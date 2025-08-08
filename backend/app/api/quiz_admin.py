from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import json

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models import (
    User, Quiz, QuizType, QuizDifficultyLevel, Question, Lesson, Level,
    PersonalizedQuizAssignment, UserQuizAttempt, quiz_questions
)
from app.services.quiz_assignment_service import IntelligentQuizAssignmentService
from pydantic import BaseModel

router = APIRouter()

# Pydantic schemas
class CreateQuizRequest(BaseModel):
    title: str
    description: str = ""
    lesson_id: int
    quiz_type: str = "lesson_practice"
    difficulty_level: str = "beginner"
    estimated_time_minutes: int = 10
    target_skill_areas: List[str] = []
    min_skill_level: float = 0.0
    max_skill_level: float = 1.0
    question_count: int = 5
    randomize_questions: bool = True
    time_limit_minutes: int = None
    max_attempts: int = 3
    question_ids: List[int] = []

class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    lesson_id: int
    lesson_title: str
    level_number: int
    quiz_type: str
    difficulty_level: str
    estimated_time_minutes: int
    question_count: int
    max_attempts: int
    is_active: bool
    created_at: datetime
    target_skill_areas: List[str]
    total_questions: int
    
    class Config:
        from_attributes = True

class QuizAssignmentStats(BaseModel):
    total_quizzes: int
    active_assignments: int
    completed_attempts: int
    average_accuracy: float
    quiz_type_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, int]

@router.get("/quizzes", response_model=List[QuizResponse])
def get_all_quizzes(
    lesson_id: int = None,
    quiz_type: str = None,
    difficulty: str = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all quizzes with optional filtering"""
    query = db.query(Quiz).filter(Quiz.is_active == True)
    
    if lesson_id:
        query = query.filter(Quiz.lesson_id == lesson_id)
    if quiz_type:
        query = query.filter(Quiz.quiz_type == quiz_type)
    if difficulty:
        query = query.filter(Quiz.difficulty_level == difficulty)
    
    quizzes = query.all()
    
    result = []
    for quiz in quizzes:
        # Count total questions in this quiz
        total_questions = db.query(quiz_questions).filter(
            quiz_questions.c.quiz_id == quiz.id
        ).count()
        
        target_skills = json.loads(quiz.target_skill_areas) if quiz.target_skill_areas else []
        
        result.append(QuizResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            lesson_id=quiz.lesson_id,
            lesson_title=quiz.lesson.title,
            level_number=quiz.lesson.level.level_number,
            quiz_type=quiz.quiz_type.value,
            difficulty_level=quiz.difficulty_level.value,
            estimated_time_minutes=quiz.estimated_time_minutes,
            question_count=quiz.question_count,
            max_attempts=quiz.max_attempts,
            is_active=quiz.is_active,
            created_at=quiz.created_at,
            target_skill_areas=target_skills,
            total_questions=total_questions
        ))
    
    return result

@router.post("/quizzes")
def create_quiz(
    quiz_data: CreateQuizRequest,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new personalized quiz"""
    
    # Validate lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == quiz_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Validate quiz type and difficulty
    try:
        quiz_type = QuizType(quiz_data.quiz_type)
        difficulty = QuizDifficultyLevel(quiz_data.difficulty_level)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
    
    # Create quiz
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        lesson_id=quiz_data.lesson_id,
        quiz_type=quiz_type,
        difficulty_level=difficulty,
        estimated_time_minutes=quiz_data.estimated_time_minutes,
        target_skill_areas=json.dumps(quiz_data.target_skill_areas),
        min_skill_level=quiz_data.min_skill_level,
        max_skill_level=quiz_data.max_skill_level,
        question_count=quiz_data.question_count,
        randomize_questions=quiz_data.randomize_questions,
        time_limit_minutes=quiz_data.time_limit_minutes,
        max_attempts=quiz_data.max_attempts,
        created_by=admin.id
    )
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Add questions to quiz if specified
    if quiz_data.question_ids:
        for question_id in quiz_data.question_ids:
            question = db.query(Question).filter(Question.id == question_id).first()
            if question and question.lesson_id == quiz_data.lesson_id:
                quiz.questions.append(question)
    
    db.commit()
    
    return {"message": "Quiz created successfully", "quiz_id": quiz.id}

@router.get("/quizzes/{quiz_id}")
def get_quiz_details(
    quiz_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get quiz questions
    questions = quiz.questions
    
    # Get assignment stats
    total_assignments = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.quiz_id == quiz_id
    ).count()
    
    active_assignments = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.quiz_id == quiz_id,
        PersonalizedQuizAssignment.is_active == True
    ).count()
    
    completed_attempts = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.quiz_id == quiz_id,
        UserQuizAttempt.is_completed == True
    ).count()
    
    # Average accuracy
    avg_accuracy = db.query(db.func.avg(UserQuizAttempt.accuracy_percentage)).filter(
        UserQuizAttempt.quiz_id == quiz_id,
        UserQuizAttempt.is_completed == True
    ).scalar() or 0.0
    
    return {
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "lesson_title": quiz.lesson.title,
            "level_number": quiz.lesson.level.level_number,
            "quiz_type": quiz.quiz_type.value,
            "difficulty_level": quiz.difficulty_level.value,
            "estimated_time_minutes": quiz.estimated_time_minutes,
            "question_count": quiz.question_count,
            "target_skill_areas": json.loads(quiz.target_skill_areas) if quiz.target_skill_areas else [],
            "created_at": quiz.created_at
        },
        "questions": [{
            "id": q.id,
            "question_text": q.question_text[:100] + "..." if len(q.question_text) > 100 else q.question_text,
            "question_type": q.question_type.value
        } for q in questions],
        "stats": {
            "total_assignments": total_assignments,
            "active_assignments": active_assignments,
            "completed_attempts": completed_attempts,
            "average_accuracy": round(avg_accuracy, 1)
        }
    }

@router.put("/quizzes/{quiz_id}/questions")
def update_quiz_questions(
    quiz_id: int,
    question_ids: List[int],
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update the questions in a quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Clear existing questions
    quiz.questions.clear()
    
    # Add new questions
    valid_questions = db.query(Question).filter(
        Question.id.in_(question_ids),
        Question.lesson_id == quiz.lesson_id
    ).all()
    
    for question in valid_questions:
        quiz.questions.append(question)
    
    db.commit()
    
    return {
        "message": "Quiz questions updated successfully",
        "questions_added": len(valid_questions)
    }

@router.delete("/quizzes/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a quiz (soft delete by marking inactive)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz.is_active = False
    db.commit()
    
    return {"message": "Quiz deleted successfully"}

@router.get("/assignment-stats", response_model=QuizAssignmentStats)
def get_quiz_assignment_stats(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get overall quiz assignment statistics"""
    
    total_quizzes = db.query(Quiz).filter(Quiz.is_active == True).count()
    active_assignments = db.query(PersonalizedQuizAssignment).filter(
        PersonalizedQuizAssignment.is_active == True
    ).count()
    completed_attempts = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.is_completed == True
    ).count()
    
    # Average accuracy across all attempts
    avg_accuracy = db.query(db.func.avg(UserQuizAttempt.accuracy_percentage)).filter(
        UserQuizAttempt.is_completed == True
    ).scalar() or 0.0
    
    # Quiz type distribution
    quiz_types = db.query(Quiz.quiz_type, db.func.count(Quiz.id)).filter(
        Quiz.is_active == True
    ).group_by(Quiz.quiz_type).all()
    
    quiz_type_dist = {qt.value: count for qt, count in quiz_types}
    
    # Difficulty distribution
    difficulties = db.query(Quiz.difficulty_level, db.func.count(Quiz.id)).filter(
        Quiz.is_active == True
    ).group_by(Quiz.difficulty_level).all()
    
    difficulty_dist = {diff.value: count for diff, count in difficulties}
    
    return QuizAssignmentStats(
        total_quizzes=total_quizzes,
        active_assignments=active_assignments,
        completed_attempts=completed_attempts,
        average_accuracy=round(avg_accuracy, 1),
        quiz_type_distribution=quiz_type_dist,
        difficulty_distribution=difficulty_dist
    )

@router.post("/users/{user_id}/reassign-quizzes")
def reassign_user_quizzes(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Manually trigger quiz reassignment for a specific user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    assignment_service = IntelligentQuizAssignmentService(db)
    assignments = assignment_service.assign_personalized_quizzes_for_user(user_id)
    
    return {
        "message": f"Quizzes reassigned for user {user.username}",
        "assignments_created": len(assignments)
    }

@router.get("/users/{user_id}/quiz-assignments")
def get_user_quiz_assignments(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get current quiz assignments for a specific user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    assignment_service = IntelligentQuizAssignmentService(db)
    assignments = assignment_service.get_user_assigned_quizzes(user_id)
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "assignments": assignments
    }