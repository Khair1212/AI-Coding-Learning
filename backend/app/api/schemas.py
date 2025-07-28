from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.user import UserRole
from app.models.lesson import LessonType, DifficultyLevel

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Learning system schemas
class LevelResponse(BaseModel):
    id: int
    level_number: int
    title: str
    description: Optional[str]
    required_xp: int
    is_active: bool

    class Config:
        from_attributes = True

class LessonResponse(BaseModel):
    id: int
    level_id: int
    lesson_number: int
    title: str
    description: Optional[str]
    lesson_type: LessonType
    difficulty: DifficultyLevel
    xp_reward: int
    is_completed: Optional[bool] = False
    score: Optional[float] = 0.0

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    lesson_id: int
    question_text: str
    question_type: LessonType
    options: Optional[str]
    code_template: Optional[str]

    class Config:
        from_attributes = True

class QuestionSubmission(BaseModel):
    question_id: int
    answer: str

class LessonProgressResponse(BaseModel):
    lesson_id: int
    is_completed: bool
    score: float
    attempts: int
    xp_earned: int
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    current_level: int
    total_xp: int
    current_streak: int
    longest_streak: int
    lessons_completed: int
    accuracy_rate: float
    last_activity_date: Optional[datetime]

    class Config:
        from_attributes = True

class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    requirement_type: str
    requirement_value: int
    xp_reward: int
    earned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GenerateQuestionRequest(BaseModel):
    topic: str
    difficulty: DifficultyLevel
    question_type: LessonType