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
from app.services.quiz_assignment_service import IntelligentQuizAssignmentService
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
    """Start a new skill assessment for the user"""
    
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
    
    # Get assessment questions (15 questions covering all levels)
    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.is_active == True
    ).all()
    
    # Store assessment ID in session (you might want to use a different approach)
    # For now, we'll rely on getting the latest assessment for this user
    
    return questions

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
        
        is_correct = answer.answer.strip().lower() == question.correct_answer.strip().lower()
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
    
    # Trigger personalized quiz assignment based on assessment results
    quiz_service = IntelligentQuizAssignmentService(db)
    quiz_assignments = quiz_service.reassign_quizzes_after_assessment(assessment.user_id, assessment.id)
    
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