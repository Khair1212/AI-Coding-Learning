from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import (
    User, Level, Lesson, Question, UserProfile, UserLessonProgress, Achievement, UserAchievement,
    Quiz, PersonalizedQuizAssignment, UserQuizAttempt, UserQuizResponse
)
from app.api.schemas import (
    LevelResponse, LessonResponse, QuestionResponse, QuestionSubmission,
    UserProfileResponse, LessonProgressResponse, AchievementResponse,
    GenerateQuestionRequest
)
from app.services.ai_service import AIQuestionGenerator, LessonContentGenerator
from app.services.quiz_assignment_service import IntelligentQuizAssignmentService

router = APIRouter()
ai_generator = AIQuestionGenerator()
content_generator = LessonContentGenerator()

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
def get_levels(db: Session = Depends(get_db)):
    """Get all available levels"""
    levels = db.query(Level).filter(Level.is_active == True).order_by(Level.level_number).all()
    return levels

@router.get("/levels/{level_id}/lessons", response_model=List[LessonResponse])
def get_level_lessons(
    level_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lessons for a specific level with user progress"""
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
            if progress:
                lesson.is_completed = progress.is_completed
                lesson.score = progress.score
    
    return lessons

@router.get("/lessons/{lesson_id}/questions", response_model=List[QuestionResponse])
def get_lesson_questions(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questions for a specific lesson"""
    questions = db.query(Question).filter(Question.lesson_id == lesson_id).all()
    return questions

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
    
    # Check if answer is correct
    is_correct = submission.answer.strip().lower() == question.correct_answer.strip().lower()
    
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
    
    if is_correct:
        # Award XP and update progress
        lesson = db.query(Lesson).filter(Lesson.id == question.lesson_id).first()
        xp_reward = lesson.xp_reward if lesson else 10
        
        lesson_progress.xp_earned += xp_reward
        lesson_progress.score = 100.0  # Perfect score for correct answer
        lesson_progress.is_completed = True
        lesson_progress.completed_at = datetime.now()
        
        # Update user profile
        profile.total_xp += xp_reward
        profile.lessons_completed += 1
        profile.last_activity_date = datetime.now()
        
        # Update streak
        if profile.last_activity_date and profile.last_activity_date.date() == date.today() - timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
        
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak
    
    db.commit()
    
    return {
        "correct": is_correct,
        "explanation": question.explanation,
        "xp_earned": lesson_progress.xp_earned if is_correct else 0
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
    current_user: User = Depends(get_current_user)
):
    """Generate AI question (admin only for now)"""
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
    assignment_service = IntelligentQuizAssignmentService(db)
    assignments = assignment_service.get_user_assigned_quizzes(current_user.id)
    
    if not assignments:
        # If no assignments exist, create them based on skill assessment
        assignments = assignment_service.assign_personalized_quizzes_for_user(current_user.id)
    
    return {
        "assignments": assignments,
        "message": "Personalized quizzes based on your skill assessment and learning progress"
    }

@router.post("/refresh-quiz-assignments")
def refresh_quiz_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh personalized quiz assignments based on current skill level"""
    assignment_service = IntelligentQuizAssignmentService(db)
    assignments = assignment_service.assign_personalized_quizzes_for_user(current_user.id)
    
    return {
        "message": "Quiz assignments refreshed",
        "new_assignments": len(assignments)
    }

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
    
    # Check if answer is correct
    is_correct = answer.strip().lower() == question.correct_answer.strip().lower()
    
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
        assignment_service = IntelligentQuizAssignmentService(db)
        assignment_service.assign_personalized_quizzes_for_user(current_user.id)
    
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