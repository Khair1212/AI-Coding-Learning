from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class LessonType(enum.Enum):
    THEORY = "theory"
    CODING_EXERCISE = "coding_exercise"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"

class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Level(Base):
    __tablename__ = "levels"
    
    id = Column(Integer, primary_key=True, index=True)
    level_number = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    required_xp = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    lessons = relationship("Lesson", back_populates="level")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    lesson_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    lesson_type = Column(Enum(LessonType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    xp_reward = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    level = relationship("Level", back_populates="lessons")
    questions = relationship("Question", back_populates="lesson")
    user_progress = relationship("UserLessonProgress", back_populates="lesson")
    quizzes = relationship("Quiz", back_populates="lesson")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(LessonType), nullable=False)
    correct_answer = Column(Text, nullable=False)
    options = Column(Text)  # JSON string for multiple choice options
    explanation = Column(Text)
    code_template = Column(Text)  # For coding exercises
    test_cases = Column(Text)  # JSON string for test cases
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    lesson = relationship("Lesson", back_populates="questions")
    quizzes = relationship("Quiz", secondary="quiz_questions", back_populates="questions")