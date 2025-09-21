from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import (
    User, AssessmentQuestion, UserAssessment, AssessmentResponse,
    UserSkillProfile, SkillLevel, AdaptiveDifficultyLog
)
from app.services.adaptive_service import AdaptiveLearningService
from app.services.ai_quiz_assignment_service import AIQuizAssignmentService
from pydantic import BaseModel

router = APIRouter()

# Pydantic schemas for assessment
class AssessmentQuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[str]
    topic_area: str
    expected_level: int

    class Config:
        from_attributes = True

class AssessmentAnswer(BaseModel):
    question_id: int
    answer: str
    confidence_level: Optional[int] = 3  # 1-5 scale
    time_taken_seconds: Optional[float] = None

class AssessmentSubmission(BaseModel):
    answers: List[AssessmentAnswer]

class AssessmentResult(BaseModel):
    assessment_id: int
    total_questions: int
    correct_answers: int
    accuracy_percentage: float
    calculated_level: int
    skill_level: str
    time_taken_minutes: Optional[float]
    topic_breakdown: dict
    recommendations: List[str]

class UserSkillProfileResponse(BaseModel):
    user_id: int
    overall_skill_level: str
    adaptive_level: int
    basics_mastery: float
    control_flow_mastery: float
    functions_mastery: float
    arrays_mastery: float
    pointers_mastery: float
    learning_velocity: float
    prefers_challenge: bool
    needs_more_practice: bool

    class Config:
        from_attributes = True

@router.get("/start", response_model=List[AssessmentQuestionResponse])
def start_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new intelligent skill assessment for the user"""
    
    # Check if user already has a completed assessment
    existing_assessment = db.query(UserAssessment).filter(
        UserAssessment.user_id == current_user.id,
        UserAssessment.is_completed == True
    ).first()
    
    if existing_assessment:
        # Allow retaking assessment but mark it as progress check
        assessment_type = "progress_check"
    else:
        assessment_type = "initial"
    
    # Create new assessment
    assessment = UserAssessment(
        user_id=current_user.id,
        assessment_type=assessment_type
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # Intelligent question selection for assessment
    all_questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.is_active == True
    ).all()
    
    # Select questions intelligently based on assessment type and user history
    selected_questions = _select_intelligent_assessment_questions(
        all_questions, assessment_type, existing_assessment, db
    )
    
    print(f"🎯 Starting {'retake' if existing_assessment else 'initial'} assessment for user {current_user.id}")
    print(f"   Selected {len(selected_questions)} questions from {len(all_questions)} available")
    
    return selected_questions

@router.post("/submit", response_model=AssessmentResult)
def submit_assessment(
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit assessment answers and get results"""
    
    # Get the latest incomplete assessment for this user
    assessment = db.query(UserAssessment).filter(
        UserAssessment.user_id == current_user.id,
        UserAssessment.is_completed == False
    ).order_by(UserAssessment.started_at.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No active assessment found")
    
    # Process answers
    correct_count = 0
    total_time = 0
    topic_performance = {}
    
    for answer in submission.answers:
        question = db.query(AssessmentQuestion).filter(
            AssessmentQuestion.id == answer.question_id
        ).first()
        
        if not question:
            continue
        
        # Handle multiple choice answers that may include letter prefixes
        user_answer = answer.answer.strip()
        correct_answer = question.correct_answer.strip()
        
        # If user sent full option text like "A. Some text", extract the text part
        if '. ' in user_answer and len(user_answer) > 2:
            # Extract the text from "A. Some text" format
            user_text = '. '.join(user_answer.split('. ')[1:]).strip()
        else:
            # User sent just the text
            user_text = user_answer
        
        is_correct = user_text.lower() == correct_answer.lower()
        if is_correct:
            correct_count += 1
        
        # Track topic performance
        topic = question.topic_area
        if topic not in topic_performance:
            topic_performance[topic] = {"correct": 0, "total": 0}
        topic_performance[topic]["total"] += 1
        if is_correct:
            topic_performance[topic]["correct"] += 1
        
        # Store response
        response = AssessmentResponse(
            assessment_id=assessment.id,
            question_id=question.id,
            user_answer=answer.answer,
            is_correct=is_correct,
            time_taken_seconds=answer.time_taken_seconds,
            confidence_level=answer.confidence_level
        )
        db.add(response)
        
        if answer.time_taken_seconds:
            total_time += answer.time_taken_seconds
    
    # Update assessment
    assessment.total_questions = len(submission.answers)
    assessment.correct_answers = correct_count
    assessment.accuracy_percentage = (correct_count / len(submission.answers)) * 100
    assessment.time_taken_minutes = total_time / 60 if total_time > 0 else None
    assessment.is_completed = True
    assessment.completed_at = datetime.now()
    
    # Calculate skill level using adaptive service
    adaptive_service = AdaptiveLearningService(db)
    calculated_level, skill_level = adaptive_service.calculate_skill_level(assessment)
    
    # Debug logging
    print(f"Assessment completed:")
    print(f"  User ID: {assessment.user_id}")
    print(f"  Correct: {correct_count}/{len(submission.answers)} ({assessment.accuracy_percentage:.1f}%)")
    print(f"  Calculated Level: {calculated_level}")
    print(f"  Skill Level: {skill_level.value}")
    print(f"  Topic Performance: {topic_performance}")
    
    assessment.calculated_level = calculated_level
    assessment.skill_level = skill_level
    
    db.commit()
    
    # Trigger AI-powered quiz assignment based on assessment results
    print(f"🤖 Starting comprehensive AI quiz assignment process...")
    ai_quiz_service = AIQuizAssignmentService(db)
    
    # Use async method in a synchronous context
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        quiz_assignment_result = loop.run_until_complete(
            ai_quiz_service.create_comprehensive_quiz_assignments(
                user_id=assessment.user_id,
                assessment_id=assessment.id
            )
        )
        print(f"✅ AI quiz assignment completed: {quiz_assignment_result.get('total_assignments_created', 0)} assignments")
    except Exception as e:
        print(f"⚠️ AI quiz assignment failed: {e}")
        # Fallback: continue without AI assignment
    finally:
        loop.close()
    
    # Generate recommendations
    recommendations = _generate_recommendations(topic_performance, skill_level, calculated_level)
    
    # Format topic breakdown for response
    topic_breakdown = {
        topic: {
            "accuracy": data["correct"] / data["total"] if data["total"] > 0 else 0,
            "questions_answered": data["total"]
        }
        for topic, data in topic_performance.items()
    }
    
    return AssessmentResult(
        assessment_id=assessment.id,
        total_questions=assessment.total_questions,
        correct_answers=assessment.correct_answers,
        accuracy_percentage=assessment.accuracy_percentage,
        calculated_level=calculated_level,
        skill_level=skill_level.value,
        time_taken_minutes=assessment.time_taken_minutes,
        topic_breakdown=topic_breakdown,
        recommendations=recommendations
    )

@router.get("/profile", response_model=UserSkillProfileResponse)
def get_skill_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current skill profile"""
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create default profile if none exists
        profile = UserSkillProfile(
            user_id=current_user.id,
            overall_skill_level=SkillLevel.COMPLETE_BEGINNER,
            adaptive_level=1
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile

@router.get("/history")
def get_assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's assessment history"""
    assessments = db.query(UserAssessment).filter(
        UserAssessment.user_id == current_user.id,
        UserAssessment.is_completed == True
    ).order_by(UserAssessment.completed_at.desc()).all()
    
    return [{
        "id": assessment.id,
        "type": assessment.assessment_type,
        "accuracy": assessment.accuracy_percentage,
        "level": assessment.calculated_level,
        "completed_at": assessment.completed_at,
        "time_taken": assessment.time_taken_minutes
    } for assessment in assessments]

@router.post("/retake")
def allow_retake_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allow user to retake the assessment (mark as progress check)"""
    # Just return success - the start endpoint will handle creating a new assessment
    return {"message": "You can now retake the assessment", "type": "progress_check"}

def _generate_recommendations(topic_performance: dict, skill_level: SkillLevel, 
                            calculated_level: int) -> List[str]:
    """Generate personalized learning recommendations"""
    recommendations = []
    
    # Analyze weak areas
    weak_topics = []
    for topic, data in topic_performance.items():
        accuracy = data["correct"] / data["total"] if data["total"] > 0 else 0
        if accuracy < 0.6:
            weak_topics.append(topic)
    
    # Generate recommendations based on skill level
    if skill_level == SkillLevel.COMPLETE_BEGINNER:
        recommendations.extend([
            "Start with the basics: Learn about variables and data types",
            "Practice writing simple programs with printf and scanf",
            "Focus on understanding program structure and syntax"
        ])
    elif skill_level == SkillLevel.BEGINNER:
        recommendations.extend([
            "Work on control flow: if-else statements and loops",
            "Practice solving problems that require decisions and repetition",
            "Learn about operators and expressions"
        ])
    elif skill_level == SkillLevel.INTERMEDIATE:
        recommendations.extend([
            "Master functions: parameter passing and return values",
            "Learn about arrays and string manipulation",
            "Practice modular programming concepts"
        ])
    elif skill_level == SkillLevel.ADVANCED:
        recommendations.extend([
            "Deep dive into pointers and memory management",
            "Practice advanced data structures",
            "Work on complex programming projects"
        ])
    else:  # EXPERT
        recommendations.extend([
            "Explore advanced C concepts and system programming",
            "Practice optimization techniques",
            "Consider learning about C libraries and frameworks"
        ])
    
    # Add topic-specific recommendations
    for topic in weak_topics:
        if topic == "basics":
            recommendations.append("Spend extra time on fundamental concepts like variables and I/O")
        elif topic == "loops":
            recommendations.append("Practice more loop-based problems and iterations")
        elif topic == "functions":
            recommendations.append("Focus on function design and modular programming")
        elif topic == "arrays":
            recommendations.append("Work on array manipulation and string handling")
        elif topic == "pointers":
            recommendations.append("Study pointer concepts and memory management carefully")
    
    # Level-specific recommendations
    if calculated_level <= 3:
        recommendations.append(f"You're ready to start at Level {calculated_level}. Take your time with fundamentals!")
    elif calculated_level <= 6:
        recommendations.append(f"Great progress! Starting at Level {calculated_level} will challenge you appropriately.")
    else:
        recommendations.append(f"Excellent! You can skip ahead to Level {calculated_level} and tackle advanced topics.")
    
    return recommendations[:5]  # Return top 5 recommendations

def _select_intelligent_assessment_questions(
    all_questions: list, 
    assessment_type: str, 
    existing_assessment, 
    db: Session
) -> list:
    """
    Intelligently select assessment questions based on:
    - Assessment type (initial vs progress_check)
    - Previous assessment results (if any)
    - Balanced coverage of topics and difficulty levels
    """
    import random
    
    # Target question count
    target_count = 15
    
    if assessment_type == "initial":
        # For initial assessment, ensure balanced coverage
        return _select_balanced_initial_questions(all_questions, target_count)
    else:
        # For progress check, focus on areas that need re-evaluation
        return _select_progress_focused_questions(
            all_questions, existing_assessment, target_count, db
        )

def _select_balanced_initial_questions(all_questions: list, target_count: int) -> list:
    """Select questions for initial assessment with balanced coverage"""
    
    # Group questions by topic and expected level
    topic_groups = {}
    level_groups = {}
    
    for q in all_questions:
        # Group by topic
        topic = q.topic_area
        if topic not in topic_groups:
            topic_groups[topic] = []
        topic_groups[topic].append(q)
        
        # Group by level
        level = q.expected_level
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(q)
    
    selected = []
    
    # Ensure we have questions from each difficulty level (1-10)
    level_targets = {
        1: 2,  # Basics - 2 questions
        2: 2,  # Variables - 2 questions
        3: 2,  # I/O - 2 questions
        4: 2,  # Operators - 2 questions
        5: 2,  # Control Flow - 2 questions
        6: 1,  # Loops - 1 question
        7: 1,  # Functions - 1 question
        8: 1,  # Arrays - 1 question
        9: 1,  # Strings - 1 question
        10: 1  # Pointers - 1 question
    }
    
    import random
    
    for level, target in level_targets.items():
        if level in level_groups:
            available = level_groups[level]
            count = min(target, len(available))
            selected.extend(random.sample(available, count))
    
    # If we don't have enough questions, fill randomly
    if len(selected) < target_count:
        remaining = [q for q in all_questions if q not in selected]
        additional = min(target_count - len(selected), len(remaining))
        selected.extend(random.sample(remaining, additional))
    
    return selected[:target_count]

def _select_progress_focused_questions(
    all_questions: list, 
    existing_assessment, 
    target_count: int, 
    db: Session
) -> list:
    """Select questions for progress check focused on previous weak areas"""
    
    if not existing_assessment:
        return _select_balanced_initial_questions(all_questions, target_count)
    
    # Get previous responses to identify weak areas
    previous_responses = db.query(AssessmentResponse).filter(
        AssessmentResponse.assessment_id == existing_assessment.id
    ).all()
    
    # Analyze weak topic areas
    topic_performance = {}
    for response in previous_responses:
        if response.question:
            topic = response.question.topic_area
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(response.is_correct)
    
    # Identify weak areas (< 60% accuracy)
    weak_topics = []
    for topic, results in topic_performance.items():
        accuracy = sum(results) / len(results) if results else 0
        if accuracy < 0.6:
            weak_topics.append(topic)
    
    print(f"🔍 Progress check: Weak areas identified: {weak_topics}")
    
    # Select questions with bias toward weak areas
    selected = []
    
    # 60% from weak areas, 40% balanced coverage
    weak_target = int(target_count * 0.6)
    balanced_target = target_count - weak_target
    
    # Select from weak areas
    weak_questions = [q for q in all_questions if q.topic_area in weak_topics]
    if weak_questions:
        import random
        weak_selected = random.sample(weak_questions, min(weak_target, len(weak_questions)))
        selected.extend(weak_selected)
    
    # Fill remaining with balanced selection
    remaining_questions = [q for q in all_questions if q not in selected]
    if remaining_questions:
        import random
        additional = min(target_count - len(selected), len(remaining_questions))
        selected.extend(random.sample(remaining_questions, additional))
    
    return selected[:target_count]