from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models import (
    User, UserProfile, Level, Lesson, Question, UserLessonProgress,
    UserAssessment, Achievement, UserAchievement, AssessmentQuestion, LessonType
)
from app.api.schemas import UserResponse
from app.services.ai_service import AIQuestionGenerator
from pydantic import BaseModel

router = APIRouter()
ai_generator = AIQuestionGenerator()

class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_lessons_completed: int
    total_assessments: int
    average_accuracy: float
    popular_levels: List[Dict[str, Any]]
    recent_registrations: List[Dict[str, Any]]

class CreateQuestionRequest(BaseModel):
    lesson_id: int
    question_text: str
    question_type: str
    correct_answer: str
    options: str = None
    explanation: str = None
    code_template: str = None

class UpdateUserRequest(BaseModel):
    is_active: bool
    role: str = None

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive platform statistics"""
    
    # Basic counts
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_lessons_completed = db.query(UserLessonProgress).filter(
        UserLessonProgress.is_completed == True
    ).count()
    total_assessments = db.query(UserAssessment).filter(
        UserAssessment.is_completed == True
    ).count()
    
    # Average accuracy
    avg_accuracy = db.query(func.avg(UserAssessment.accuracy_percentage)).filter(
        UserAssessment.is_completed == True
    ).scalar() or 0.0
    
    # Popular levels (by lesson completions)
    popular_levels = db.query(
        Level.level_number,
        Level.title,
        func.count(UserLessonProgress.id).label('completions')
    ).join(
        Lesson, Level.id == Lesson.level_id
    ).join(
        UserLessonProgress, Lesson.id == UserLessonProgress.lesson_id
    ).filter(
        UserLessonProgress.is_completed == True
    ).group_by(Level.id).order_by(desc('completions')).limit(5).all()
    
    # Recent registrations (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_users = db.query(User).filter(
        User.created_at >= week_ago
    ).order_by(desc(User.created_at)).limit(10).all()
    
    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_lessons_completed=total_lessons_completed,
        total_assessments=total_assessments,
        average_accuracy=round(avg_accuracy, 1),
        popular_levels=[
            {
                "level": level.level_number,
                "title": level.title,
                "completions": completions
            } for level, completions in popular_levels
        ],
        recent_registrations=[
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None
            } for user in recent_users
        ]
    )

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users for admin management"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user status or role"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = update_data.is_active
    if update_data.role:
        user.role = update_data.role
    
    db.commit()
    return {"message": "User updated successfully"}

@router.get("/user-progress/{user_id}")
def get_user_progress_detail(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_profile_id == profile.id if profile else None
    ).all()
    assessments = db.query(UserAssessment).filter(
        UserAssessment.user_id == user_id,
        UserAssessment.is_completed == True
    ).order_by(desc(UserAssessment.completed_at)).all()
    
    return {
        "user": user,
        "profile": profile,
        "lesson_progress": progress,
        "assessments": [{
            "id": a.id,
            "accuracy": a.accuracy_percentage,
            "level": a.calculated_level,
            "skill_level": a.skill_level.value if a.skill_level else None,
            "completed_at": a.completed_at
        } for a in assessments]
    }

@router.get("/questions")
def get_all_questions(
    lesson_id: int = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all questions, optionally filtered by lesson"""
    query = db.query(Question)
    if lesson_id:
        query = query.filter(Question.lesson_id == lesson_id)
    
    questions = query.all()
    return questions

@router.post("/questions")
def create_question(
    question_data: CreateQuestionRequest,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new question for a lesson"""
    lesson = db.query(Lesson).filter(Lesson.id == question_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Convert question_type string to enum
    try:
        question_type_enum = LessonType(question_data.question_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid question type: {question_data.question_type}")
    
    question = Question(
        lesson_id=question_data.lesson_id,
        question_text=question_data.question_text,
        question_type=question_type_enum,
        correct_answer=question_data.correct_answer,
        options=question_data.options,
        explanation=question_data.explanation,
        code_template=question_data.code_template
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return {"message": "Question created successfully", "question": question}

@router.put("/questions/{question_id}")
def update_question(
    question_id: int,
    question_data: CreateQuestionRequest,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update an existing question"""
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Update question fields
        question.lesson_id = question_data.lesson_id
        question.question_text = question_data.question_text
        question.question_type = question_data.question_type
        question.correct_answer = question_data.correct_answer
        question.options = question_data.options
        question.explanation = question_data.explanation
        question.code_template = question_data.code_template
        
        db.commit()
        db.refresh(question)
        
        return {"message": "Question updated successfully", "question": question}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update question: {str(e)}")

@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}

@router.post("/questions/generate-ai")
def generate_ai_question(
    lesson_id: int,
    topic: str,
    difficulty: str,
    question_type: str,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Generate an AI question and optionally save it"""
    try:
        from app.models.lesson import DifficultyLevel, LessonType
        
        # Map strings to enums
        difficulty_map = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED
        }
        
        type_map = {
            "multiple_choice": LessonType.MULTIPLE_CHOICE,
            "coding_exercise": LessonType.CODING_EXERCISE,
            "fill_in_blank": LessonType.FILL_IN_BLANK
        }
        
        difficulty_level = difficulty_map.get(difficulty, DifficultyLevel.BEGINNER)
        lesson_type = type_map.get(question_type, LessonType.MULTIPLE_CHOICE)
        
        # Generate question using AI
        if question_type == "multiple_choice":
            question_data = ai_generator.generate_theory_question(topic, difficulty_level)
        elif question_type == "coding_exercise":
            question_data = ai_generator.generate_coding_exercise(topic, difficulty_level)
        else:
            question_data = ai_generator.generate_fill_in_blank(topic, difficulty_level)
        
        return {
            "generated_question": question_data,
            "lesson_id": lesson_id,
            "message": "Question generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

@router.get("/assessment-questions")
def get_assessment_questions(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all assessment questions"""
    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.is_active == True
    ).all()
    return questions

@router.get("/levels-lessons")
def get_levels_with_lessons(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all levels with their lessons for admin management"""
    levels = db.query(Level).filter(Level.is_active == True).order_by(Level.level_number).all()
    
    result = []
    for level in levels:
        lessons = db.query(Lesson).filter(
            Lesson.level_id == level.id,
            Lesson.is_active == True
        ).order_by(Lesson.lesson_number).all()
        
        result.append({
            "id": level.id,
            "level_number": level.level_number,
            "title": level.title,
            "description": level.description,
            "lessons": [{
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "lesson_type": lesson.lesson_type.value,
                "difficulty": lesson.difficulty.value,
                "question_count": db.query(Question).filter(Question.lesson_id == lesson.id).count()
            } for lesson in lessons]
        })
    
    return result

@router.get("/achievements")
def get_achievements_with_stats(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all achievements with earned statistics"""
    achievements = db.query(Achievement).filter(Achievement.is_active == True).all()
    
    result = []
    for achievement in achievements:
        earned_count = db.query(UserAchievement).filter(
            UserAchievement.achievement_id == achievement.id
        ).count()
        
        result.append({
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "requirement_type": achievement.requirement_type,
            "requirement_value": achievement.requirement_value,
            "xp_reward": achievement.xp_reward,
            "times_earned": earned_count
        })
    
    return result