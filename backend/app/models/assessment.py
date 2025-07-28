from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class SkillLevel(enum.Enum):
    COMPLETE_BEGINNER = "complete_beginner"  # Never coded before
    BEGINNER = "beginner"                    # Basic programming concepts
    INTERMEDIATE = "intermediate"             # Some C knowledge
    ADVANCED = "advanced"                    # Strong C knowledge
    EXPERT = "expert"                       # C expert level

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # 'multiple_choice', 'code_reading', 'concept'
    correct_answer = Column(Text, nullable=False)
    options = Column(Text)  # JSON string for multiple choice
    difficulty_weight = Column(Float, default=1.0)  # How much this question affects level calculation
    topic_area = Column(String)  # 'variables', 'loops', 'functions', 'pointers', etc.
    expected_level = Column(Integer)  # What level should be able to answer this (1-10)
    explanation = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user responses
    responses = relationship("AssessmentResponse", back_populates="question")

class UserAssessment(Base):
    __tablename__ = "user_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_type = Column(String, default="initial")  # 'initial', 'progress_check', 'level_up'
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    calculated_level = Column(Integer, default=1)
    skill_level = Column(Enum(SkillLevel), default=SkillLevel.COMPLETE_BEGINNER)
    time_taken_minutes = Column(Float)
    is_completed = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    responses = relationship("AssessmentResponse", back_populates="assessment")

class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("user_assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Float)
    confidence_level = Column(Integer, default=3)  # 1-5 scale, how confident user felt
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("UserAssessment", back_populates="responses")
    question = relationship("AssessmentQuestion", back_populates="responses")

class UserSkillProfile(Base):
    __tablename__ = "user_skill_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Skill levels for different C topics (0.0 to 1.0)
    basics_mastery = Column(Float, default=0.0)      # Variables, data types, I/O
    control_flow_mastery = Column(Float, default=0.0) # If/else, loops
    functions_mastery = Column(Float, default=0.0)    # Function definition, calls, scope
    arrays_mastery = Column(Float, default=0.0)       # Arrays, strings
    pointers_mastery = Column(Float, default=0.0)     # Pointers, memory management
    
    # Overall metrics
    overall_skill_level = Column(Enum(SkillLevel), default=SkillLevel.COMPLETE_BEGINNER)
    adaptive_level = Column(Integer, default=1)        # Current recommended level (1-10)
    learning_velocity = Column(Float, default=1.0)     # How fast they learn (affects progression)
    consistency_score = Column(Float, default=1.0)     # How consistent their performance is
    
    # Adaptive settings
    prefers_challenge = Column(Boolean, default=False)  # Likes harder questions
    needs_more_practice = Column(Boolean, default=False) # Needs repetition
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

class AdaptiveDifficultyLog(Base):
    __tablename__ = "adaptive_difficulty_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    original_difficulty = Column(String)  # Original lesson difficulty
    adjusted_difficulty = Column(String)  # AI-adjusted difficulty
    performance_score = Column(Float)     # User's performance on this lesson
    adaptation_reason = Column(String)    # Why difficulty was adjusted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    lesson = relationship("Lesson")