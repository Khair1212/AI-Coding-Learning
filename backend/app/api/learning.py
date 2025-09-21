from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import (
    User, Level, Lesson, Question, UserProfile, UserLessonProgress, Achievement, UserAchievement,
    Quiz, PersonalizedQuizAssignment, UserQuizAttempt, UserQuizResponse, UserLessonAnswer
)
from app.api.schemas import (
    LevelResponse, LessonResponse, QuestionResponse, QuestionSubmission,
    UserProfileResponse, LessonProgressResponse, AchievementResponse,
    GenerateQuestionRequest
)
from app.services.ai_service import AIQuestionGenerator, LessonContentGenerator
from app.services.ai_quiz_assignment_service import AIQuizAssignmentService
from app.services.intelligent_question_service import IntelligentQuestionSelectionService
from app.services.subscription_service import SubscriptionService
from app.services.code_execution_service import CodeExecutionService
import re

router = APIRouter()
ai_generator = AIQuestionGenerator()
content_generator = LessonContentGenerator()
code_execution_service = CodeExecutionService()

def normalize_code(code_str):
    """Normalize code by removing extra whitespace and standardizing quotes"""
    if not code_str:
        return ""
    
    # Remove markdown code blocks
    code_str = re.sub(r'```[a-zA-Z]*\n?', '', code_str)
    code_str = re.sub(r'```', '', code_str)
    
    # Normalize whitespace
    code_str = re.sub(r'\s+', ' ', code_str.strip())
    
    # Standardize quotes - convert single quotes to double quotes in printf statements
    code_str = re.sub(r'printf\s*\(\s*\'([^\']*)\'\s*\)', r'printf("\1")', code_str)
    
    return code_str.lower()

def evaluate_answer(user_answer, correct_answer, question_type, test_cases=None):
    """Evaluate user answer with improved logic for different question types"""
    
    if question_type.value == 'multiple_choice':
        # For multiple choice, match the full text of the selected option
        user_clean = user_answer.strip()
        correct_clean = correct_answer.strip()
        
        # If user sent full option text like "A. Some text", extract the text part
        if '. ' in user_clean and len(user_clean) > 2:
            # Extract the text from "A. Some text" format
            user_text = '. '.join(user_clean.split('. ')[1:]).strip()
        else:
            # User sent just the text
            user_text = user_clean
        
        # Compare the actual text content (case-insensitive)
        return user_text.lower() == correct_clean.lower()
    
    elif question_type.value == 'fill_in_blank':
        # For fill in blank, remove quotes and do exact match
        user_clean = user_answer.strip().lower().strip('"').strip("'")
        correct_clean = correct_answer.strip().lower().strip('"').strip("'")
        return user_clean == correct_clean
    
    elif question_type.value == 'coding_exercise':
        # NEW: Use output-based evaluation for coding exercises
        if test_cases:
            try:
                is_correct, results = code_execution_service.evaluate_code_exercise(user_answer, test_cases)
                print(f"Code execution result: {is_correct}, details: {results}")
                return is_correct
            except Exception as e:
                print(f"Code execution failed, falling back to pattern matching: {e}")
                # Fall back to the old method if execution fails
                pass
        
        # FALLBACK: For coding exercises without test cases, use enhanced pattern matching
        user_normalized = normalize_code(user_answer)
        correct_normalized = normalize_code(correct_answer)
        
        # Check if the normalized code matches
        if user_normalized == correct_normalized:
            return True
        
        # Additional checks for common variations
        # Check if user code contains essential elements
        essential_checks = [
            'printf' in user_normalized,
            'return 0' in user_normalized or 'return0' in user_normalized,
            'main()' in user_normalized or 'main(' in user_normalized,
            '#include' in user_normalized
        ]
        
        # If it's a simple program, check for key elements
        if 'hello' in correct_normalized and 'world' in correct_normalized:
            return ('hello' in user_normalized and 'world' in user_normalized and 
                    'printf' in user_normalized and ('return 0' in user_normalized or 'return0' in user_normalized))
        
        # For addition programs
        if 'scanf' in correct_normalized and 'sum' in correct_normalized:
            return ('scanf' in user_normalized and 'printf' in user_normalized and 
                    ('sum' in user_normalized or '+' in user_normalized))
        
        return False
    
    else:
        # Default to exact match for other types
        return user_answer.strip().lower() == correct_answer.strip().lower()

@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's learning profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = UserProfile(
            user_id=current_user.id,
            current_level=1,
            total_xp=0,
            current_streak=0,
            longest_streak=0,
            lessons_completed=0,
            accuracy_rate=0.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile

@router.get("/levels", response_model=List[LevelResponse])
def get_levels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all levels with lock status based on user's subscription"""
    all_levels = db.query(Level).filter(Level.is_active == True).order_by(Level.level_number).all()
    
    # Add lock status to each level based on subscription access
    levels_with_lock_status = []
    for level in all_levels:
        # Create a dict from the level object and add is_locked field
        level_dict = {
            "id": level.id,
            "level_number": level.level_number,
            "title": level.title,
            "description": level.description,
            "required_xp": level.required_xp,
            "is_active": level.is_active,
            "is_locked": not SubscriptionService.can_access_level(int(current_user.id), level.level_number, db)
        }
        levels_with_lock_status.append(level_dict)
    
    return levels_with_lock_status

@router.get("/levels/{level_id}/lessons", response_model=List[LessonResponse])
def get_level_lessons(
    level_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lessons for a specific level with user progress"""
    # Check subscription access
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    if not SubscriptionService.can_access_level(int(current_user.id), level.level_number, db):
        raise HTTPException(
            status_code=403, 
            detail=f"Upgrade your subscription to access Level {level.level_number}. Free users can access levels 1-3 only."
        )
    
    lessons = db.query(Lesson).filter(
        Lesson.level_id == level_id,
        Lesson.is_active == True
    ).order_by(Lesson.lesson_number).all()
    
    # Get user's progress for these lessons
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        progress_map = {
            p.lesson_id: p for p in db.query(UserLessonProgress).filter(
                UserLessonProgress.user_profile_id == profile.id,
                UserLessonProgress.lesson_id.in_([l.id for l in lessons])
            ).all()
        }
        
        # Add progress info to lessons
        for lesson in lessons:
            progress = progress_map.get(lesson.id)
            if progress and progress.attempts > 0:  # Only show progress if actually attempted
                lesson.is_completed = progress.is_completed
                lesson.score = progress.score
    
    return lessons

@router.get("/lessons/{lesson_id}/questions", response_model=List[QuestionResponse])
def get_lesson_questions(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized questions for a specific lesson based on user's skill assessment"""
    # First, check if the lesson exists and get its level
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    level = db.query(Level).filter(Level.id == lesson.level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # Check subscription access to the level
    if not SubscriptionService.can_access_level(int(current_user.id), level.level_number, db):
        raise HTTPException(
            status_code=403, 
            detail=f"Upgrade your subscription to access Level {level.level_number}. Free users can access levels 1-3 only."
        )
    
    # Check daily question limit
    question_check = SubscriptionService.can_attempt_question(current_user.id, db)
    if not question_check['allowed']:
        raise HTTPException(
            status_code=429,
            detail=f"Daily question limit reached ({question_check['used']}/{question_check['limit']}). Upgrade your subscription for more questions."
        )
    
    # Use intelligent question selection
    intelligent_service = IntelligentQuestionSelectionService(db)
    
    try:
        # Get personalized question selection (3-4 questions per lesson)
        selected_questions = intelligent_service.select_personalized_questions_for_lesson(
            user_id=current_user.id,
            lesson_id=lesson_id,
            target_count=4  # Show 4 questions instead of all available
        )
        
        # Convert to QuestionResponse format
        questions = []
        for q_data in selected_questions:
            questions.append({
                'id': q_data['id'],
                'lesson_id': lesson_id,
                'question_text': q_data['question_text'],
                'question_type': q_data['question_type'],
                'correct_answer': q_data['correct_answer'],
                'options': q_data['options'],
                'explanation': q_data['explanation'],
                'code_template': q_data['code_template'],
                # Additional AI context (for frontend to show reasoning)
                'ai_context': {
                    'selection_reasoning': q_data.get('selection_reasoning'),
                    'personalized': q_data.get('personalized', True),
                    'difficulty_for_user': q_data.get('difficulty_for_user'),
                    'estimated_time_minutes': q_data.get('recommended_time_minutes')
                }
            })
        
        print(f"🎯 Serving {len(questions)} personalized questions for lesson {lesson_id} to user {current_user.id}")
        return questions
        
    except Exception as e:
        print(f"❌ Error in intelligent question selection: {e}")
        # Fallback to random selection if AI service fails
        all_questions = db.query(Question).filter(Question.lesson_id == lesson_id).all()
        # Return random 4 questions as fallback
        import random
        selected = random.sample(all_questions, min(4, len(all_questions)))
        return selected

@router.post("/questions/submit")
def submit_answer(
    submission: QuestionSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answer for a question"""
    question = db.query(Question).filter(Question.id == submission.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Record usage for subscription limits
    SubscriptionService.record_usage(current_user.id, 'question', db)
    
    # Check if answer is correct with better evaluation logic
    is_correct = evaluate_answer(submission.answer, question.correct_answer, question.question_type, question.test_cases)
    
    # Get or create user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Update lesson progress
    lesson_progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_profile_id == profile.id,
        UserLessonProgress.lesson_id == question.lesson_id
    ).first()
    
    if not lesson_progress:
        lesson_progress = UserLessonProgress(
            user_profile_id=profile.id,
            lesson_id=question.lesson_id,
            score=0.0,
            attempts=0,
            xp_earned=0
        )
        db.add(lesson_progress)
    
    lesson_progress.attempts += 1

    # Track per-question results
    answer_record = db.query(UserLessonAnswer).filter(
        UserLessonAnswer.user_profile_id == profile.id,
        UserLessonAnswer.lesson_id == question.lesson_id,
        UserLessonAnswer.question_id == question.id
    ).first()

    if not answer_record:
        answer_record = UserLessonAnswer(
            user_profile_id=profile.id,
            lesson_id=question.lesson_id,
            question_id=question.id,
            is_correct=is_correct,
            attempts=1
        )
        db.add(answer_record)
    else:
        answer_record.is_correct = is_correct or answer_record.is_correct
        answer_record.attempts = (answer_record.attempts or 0) + 1

    # Completion threshold logic
    # Require at least 70% correct across lesson questions AND all coding_exercise questions correct
    lesson_questions = db.query(Question).filter(Question.lesson_id == question.lesson_id).all()
    records = db.query(UserLessonAnswer).filter(
        UserLessonAnswer.user_profile_id == profile.id,
        UserLessonAnswer.lesson_id == question.lesson_id
    ).all()

    total_q = len(lesson_questions)
    correct_count = len([r for r in records if r.is_correct])
    percent_correct = (correct_count / total_q) if total_q > 0 else 0.0

    # Ensure all coding questions are correct before completion
    coding_q_ids = {q.id for q in lesson_questions if q.question_type.value == 'coding_exercise'}
    coding_correct_ids = {r.question_id for r in records if r.is_correct}
    all_coding_correct = coding_q_ids.issubset(coding_correct_ids)

    # Pass threshold
    passed_threshold = percent_correct >= 0.7 and all_coding_correct

    if is_correct:
        # Award XP on first time completion only
        lesson = db.query(Lesson).filter(Lesson.id == question.lesson_id).first()
        xp_reward = lesson.xp_reward if lesson else 10
        
        # Update user profile XP incrementally on correct answers
        profile.total_xp += xp_reward
        profile.last_activity_date = datetime.now()
        
        # Update streak
        if profile.last_activity_date and profile.last_activity_date.date() == date.today() - timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
        
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak

    # Update lesson_progress aggregate fields
    lesson_progress.score = round(percent_correct * 100.0, 1)
    if passed_threshold:
        if not lesson_progress.is_completed:
            profile.lessons_completed += 1
        lesson_progress.is_completed = True
        lesson_progress.completed_at = datetime.now()
    
    db.commit()
    
    return {
        "correct": is_correct,
        "explanation": question.explanation,
        "xp_earned": 0,
        "lesson_progress": {
            "score": lesson_progress.score,
            "is_completed": lesson_progress.is_completed,
            "correct_count": correct_count,
            "total_questions": total_q,
            "coding_required_passed": all_coding_correct
        }
    }

@router.get("/achievements", response_model=List[AchievementResponse])
def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's achievements"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        return []
    
    # Get all achievements with user's earned status
    achievements = db.query(Achievement).filter(Achievement.is_active == True).all()
    user_achievements = {
        ua.achievement_id: ua.earned_at for ua in 
        db.query(UserAchievement).filter(UserAchievement.user_profile_id == profile.id).all()
    }
    
    result = []
    for achievement in achievements:
        achievement_data = AchievementResponse.from_orm(achievement)
        achievement_data.earned_at = user_achievements.get(achievement.id)
        result.append(achievement_data)
    
    return result

@router.post("/questions/generate")
def generate_question(
    request: GenerateQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI question"""
    # Check if user has access to AI questions
    if not SubscriptionService.can_use_ai_questions(current_user.id, db):
        raise HTTPException(
            status_code=403,
            detail="AI-generated questions are available for Gold and Premium subscribers only. Upgrade your subscription to access this feature."
        )
    
    # Record AI question usage
    SubscriptionService.record_usage(current_user.id, 'ai_question', db)
    
    try:
        if request.question_type == "multiple_choice":
            return ai_generator.generate_theory_question(request.topic, request.difficulty)
        elif request.question_type == "coding_exercise":
            return ai_generator.generate_coding_exercise(request.topic, request.difficulty)
        elif request.question_type == "fill_in_blank":
            return ai_generator.generate_fill_in_blank(request.topic, request.difficulty)
        else:
            raise HTTPException(status_code=400, detail="Invalid question type")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress/stats")
def get_progress_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress statistics"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        return {"error": "Profile not found"}
    
    # Get lesson progress by level
    lesson_progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_profile_id == profile.id
    ).all()
    
    # Calculate accuracy
    total_attempts = sum(p.attempts for p in lesson_progress)
    correct_answers = len([p for p in lesson_progress if p.is_completed])
    accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        "profile": profile,
        "total_lessons_available": db.query(Lesson).filter(Lesson.is_active == True).count(),
        "accuracy_rate": round(accuracy, 1),
        "lessons_by_level": {
            level.level_number: {
                "total": len(level.lessons),
                "completed": len([p for p in lesson_progress if p.lesson_id in [l.id for l in level.lessons] and p.is_completed])
            }
            for level in db.query(Level).filter(Level.is_active == True).all()
        }
    }

@router.get("/personalized-quizzes")
def get_personalized_quizzes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized quizzes assigned to the current user"""
    # Check if user has AI-powered assignments
    ai_assignments = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.user_id == current_user.id,
        PersonalizedQuizAssignment.assignment_type == 'ai_generated',
        PersonalizedQuizAssignment.is_active == True
    ).all()
    
    if ai_assignments:
        # Return AI-generated assignments with enhanced info
        assignments = []
        for assignment in ai_assignments:
            assignments.append({
                'id': assignment.id,
                'lesson_id': assignment.lesson_id,
                'lesson_title': assignment.lesson.title if assignment.lesson else 'Unknown',
                'level_number': assignment.lesson.level.level_number if assignment.lesson and assignment.lesson.level else 1,
                'priority_level': assignment.priority_level,
                'difficulty_adjustment': assignment.difficulty_adjustment,
                'target_question_count': assignment.target_question_count,
                'estimated_completion_time': assignment.estimated_completion_time,
                'ai_reasoning': assignment.ai_reasoning,
                'assignment_type': 'AI-Generated',
                'created_at': assignment.created_at
            })
        
        return {
            "assignments": assignments,
            "message": "AI-powered personalized quizzes based on your comprehensive skill assessment",
            "total_assignments": len(assignments),
            "ai_enhanced": True
        }
    
    else:
        return {
            "assignments": [],
            "message": "No personalized quizzes available. Please complete your skill assessment first.",
            "total_assignments": 0,
            "ai_enhanced": False
        }

@router.post("/refresh-quiz-assignments")
def refresh_quiz_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh personalized quiz assignments using AI analysis"""
    # Get the user's latest assessment
    latest_assessment = db.query(UserAssessment).filter(
        UserAssessment.user_id == current_user.id,
        UserAssessment.is_completed == True
    ).order_by(UserAssessment.completed_at.desc()).first()
    
    if not latest_assessment:
        return {
            "error": "No completed assessment found. Please complete your skill assessment first.",
            "new_assignments": 0
        }
    
    # Deactivate existing AI assignments
    existing_assignments = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.user_id == current_user.id,
        PersonalizedQuizAssignment.assignment_type == 'ai_generated'
    ).all()
    
    for assignment in existing_assignments:
        assignment.is_active = False
    db.commit()
    
    # Create new AI-powered assignments
    ai_service = AIQuizAssignmentService(db)
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            ai_service.create_comprehensive_quiz_assignments(
                user_id=current_user.id,
                assessment_id=latest_assessment.id
            )
        )
        
        return {
            "message": "AI-powered quiz assignments refreshed successfully",
            "new_assignments": result.get('total_assignments_created', 0),
            "ai_enhanced": True,
            "assessment_analyzed": latest_assessment.id
        }
    except Exception as e:
        return {
            "error": f"Failed to refresh assignments: {str(e)}",
            "new_assignments": 0
        }
    finally:
        loop.close()

@router.get("/quiz/{quiz_id}/questions")
def get_personalized_quiz_questions(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get questions for a specific personalized quiz"""
    
    # Verify user has access to this quiz
    assignment = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.user_id == current_user.id,
        PersonalizedQuizAssignment.quiz_id == quiz_id,
        PersonalizedQuizAssignment.is_active == True
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=403, detail="Quiz not assigned to user")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get quiz questions (randomized if enabled)
    questions = quiz.questions
    if quiz.randomize_questions:
        import random
        questions = random.sample(questions, min(len(questions), quiz.question_count))
    else:
        questions = questions[:quiz.question_count]
    
    # Check if user has already started this quiz
    existing_attempt = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.user_id == current_user.id,
        UserQuizAttempt.quiz_id == quiz_id,
        UserQuizAttempt.is_completed == False
    ).first()
    
    if existing_attempt:
        attempt_id = existing_attempt.id
    else:
        # Create new quiz attempt
        new_attempt = UserQuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            assignment_id=assignment.id,
            total_questions=len(questions)
        )
        db.add(new_attempt)
        db.commit()
        db.refresh(new_attempt)
        attempt_id = new_attempt.id
    
    return {
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "estimated_time_minutes": quiz.estimated_time_minutes,
            "time_limit_minutes": quiz.time_limit_minutes,
            "question_count": len(questions)
        },
        "attempt_id": attempt_id,
        "questions": [{
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type.value,
            "options": q.options,
            "code_template": q.code_template
        } for q in questions]
    }

@router.post("/quiz/submit-response")
def submit_quiz_response(
    quiz_attempt_id: int,
    question_id: int,
    answer: str,
    confidence_level: int = 3,
    time_taken_seconds: float = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a response to a quiz question"""
    
    # Verify quiz attempt belongs to user
    attempt = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.id == quiz_attempt_id,
        UserQuizAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer is correct using the evaluate_answer function
    is_correct = evaluate_answer(answer, question.correct_answer, question.question_type, question.test_cases)
    
    # Store response
    response = UserQuizResponse(
        quiz_attempt_id=quiz_attempt_id,
        question_id=question_id,
        user_answer=answer,
        is_correct=is_correct,
        time_taken_seconds=time_taken_seconds,
        confidence_level=confidence_level,
        skill_area=question.lesson.title  # Simplified skill area mapping
    )
    
    db.add(response)
    db.commit()
    
    return {
        "correct": is_correct,
        "explanation": question.explanation,
        "response_id": response.id
    }

@router.get("/ai-assignments")
def get_ai_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about AI-generated quiz assignments"""
    # Get all AI assignments for the user
    assignments = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.user_id == current_user.id,
        PersonalizedQuizAssignment.assignment_type == 'ai_generated',
        PersonalizedQuizAssignment.is_active == True
    ).order_by(PersonalizedQuizAssignment.created_at.desc()).all()
    
    if not assignments:
        return {
            "assignments": [],
            "message": "No AI assignments found. Please complete your skill assessment to generate personalized quizzes.",
            "total": 0
        }
    
    # Format detailed assignment information
    detailed_assignments = []
    for assignment in assignments:
        lesson = assignment.lesson
        level = lesson.level if lesson else None
        
        # Parse learning objectives
        learning_objectives = []
        try:
            if assignment.learning_objectives:
                import json
                learning_objectives = json.loads(assignment.learning_objectives)
        except:
            learning_objectives = ["Complete lesson with understanding"]
        
        assignment_data = {
            'id': assignment.id,
            'lesson_id': assignment.lesson_id,
            'lesson_title': lesson.title if lesson else 'Unknown Lesson',
            'level_number': level.level_number if level else 1,
            'level_title': level.title if level else 'Unknown Level',
            'priority_level': assignment.priority_level,
            'difficulty_adjustment': assignment.difficulty_adjustment,
            'target_question_count': assignment.target_question_count,
            'estimated_completion_time': assignment.estimated_completion_time,
            'learning_objectives': learning_objectives,
            'ai_reasoning': assignment.ai_reasoning,
            'assignment_type': assignment.assignment_type,
            'created_at': assignment.created_at,
            'status': 'active' if assignment.is_active else 'inactive'
        }
        detailed_assignments.append(assignment_data)
    
    # Group by priority for better organization
    priority_groups = {'high': [], 'medium': [], 'low': []}
    for assignment in detailed_assignments:
        priority = assignment['priority_level']
        if priority in priority_groups:
            priority_groups[priority].append(assignment)
    
    return {
        "assignments": detailed_assignments,
        "assignments_by_priority": priority_groups,
        "total_assignments": len(detailed_assignments),
        "message": f"Found {len(detailed_assignments)} AI-generated quiz assignments",
        "ai_enhanced": True,
        "summary": {
            'high_priority': len(priority_groups['high']),
            'medium_priority': len(priority_groups['medium']),
            'low_priority': len(priority_groups['low']),
            'total_estimated_time': sum(a['estimated_completion_time'] for a in detailed_assignments if a['estimated_completion_time']),
            'levels_covered': list(set(a['level_number'] for a in detailed_assignments))
        }
    }

@router.get("/ai-assignment/{assignment_id}")
def get_ai_assignment_detail(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific AI assignment"""
    assignment = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.id == assignment_id,
        PersonalizedQuizAssignment.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    lesson = assignment.lesson
    level = lesson.level if lesson else None
    
    # Get available questions for this lesson
    questions = db.query(Question).filter(Question.lesson_id == assignment.lesson_id).all()
    
    # Parse learning objectives
    learning_objectives = []
    try:
        if assignment.learning_objectives:
            import json
            learning_objectives = json.loads(assignment.learning_objectives)
    except:
        learning_objectives = ["Complete lesson with understanding"]
    
    return {
        'assignment': {
            'id': assignment.id,
            'lesson_id': assignment.lesson_id,
            'lesson_title': lesson.title if lesson else 'Unknown',
            'lesson_description': lesson.description if lesson else '',
            'level_number': level.level_number if level else 1,
            'level_title': level.title if level else 'Unknown',
            'priority_level': assignment.priority_level,
            'difficulty_adjustment': assignment.difficulty_adjustment,
            'target_question_count': assignment.target_question_count,
            'available_questions': len(questions),
            'estimated_completion_time': assignment.estimated_completion_time,
            'learning_objectives': learning_objectives,
            'ai_reasoning': assignment.ai_reasoning,
            'created_at': assignment.created_at,
            'is_active': assignment.is_active
        },
        'questions_preview': [
            {
                'id': q.id,
                'question_text': q.question_text[:100] + '...' if len(q.question_text) > 100 else q.question_text,
                'question_type': q.question_type.value,
                'difficulty': getattr(q, 'difficulty_level', 'unknown')
            } for q in questions[:5]  # Show first 5 questions as preview
        ],
        'level_info': {
            'number': level.level_number if level else 1,
            'title': level.title if level else 'Unknown',
            'description': level.description if level else '',
            'total_lessons': len(level.lessons) if level else 0
        } if level else None
    }

@router.post("/quiz/complete/{attempt_id}")
def complete_quiz_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a quiz attempt and calculate results"""
    
    attempt = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.id == attempt_id,
        UserQuizAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    # Get all responses for this attempt
    responses = db.query(UserQuizResponse).filter(
        UserQuizResponse.quiz_attempt_id == attempt_id
    ).all()
    
    if not responses:
        raise HTTPException(status_code=400, detail="No responses found for this attempt")
    
    # Calculate results
    correct_count = sum(1 for r in responses if r.is_correct)
    accuracy = (correct_count / len(responses)) * 100
    
    # Calculate total time
    total_time = sum(r.time_taken_seconds for r in responses if r.time_taken_seconds) / 60
    
    # Update attempt
    attempt.completed_at = datetime.now()
    attempt.correct_answers = correct_count
    attempt.accuracy_percentage = accuracy
    attempt.time_taken_minutes = total_time
    attempt.is_completed = True
    attempt.is_passed = accuracy >= 70  # Pass threshold
    
    # Update user profile and progress
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        # Award XP for completion
        xp_reward = min(50, int(accuracy))  # Up to 50 XP based on accuracy
        profile.total_xp += xp_reward
        profile.last_activity_date = datetime.now()
        
        # Update accuracy rate
        all_attempts = db.query(UserQuizAttempt).filter(
            UserQuizAttempt.user_id == current_user.id,
            UserQuizAttempt.is_completed == True
        ).all()
        
        if all_attempts:
            avg_accuracy = sum(a.accuracy_percentage for a in all_attempts) / len(all_attempts)
            profile.accuracy_rate = avg_accuracy
    
    db.commit()
    
    # Trigger reassignment if user performance suggests they're ready for new challenges
    if accuracy >= 85:  # High performance
        # Get latest assessment for AI reassignment
        latest_assessment = db.query(UserAssessment).filter(
            UserAssessment.user_id == current_user.id,
            UserAssessment.is_completed == True
        ).order_by(UserAssessment.completed_at.desc()).first()
        
        if latest_assessment:
            ai_service = AIQuizAssignmentService(db)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    ai_service.create_comprehensive_quiz_assignments(
                        user_id=current_user.id,
                        assessment_id=latest_assessment.id
                    )
                )
                print(f"🎯 High performance triggered AI reassignment for user {current_user.id}")
            except Exception as e:
                print(f"⚠️ AI reassignment failed: {e}")
            finally:
                loop.close()
    
    return {
        "attempt_id": attempt_id,
        "total_questions": attempt.total_questions,
        "correct_answers": correct_count,
        "accuracy_percentage": accuracy,
        "time_taken_minutes": total_time,
        "is_passed": attempt.is_passed,
        "xp_earned": xp_reward if profile else 0,
        "message": "Great job!" if accuracy >= 70 else "Keep practicing!"
    }