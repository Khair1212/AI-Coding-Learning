from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class QuizDifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ADAPTIVE = "adaptive"  # Difficulty adjusts based on user performance

class QuizType(enum.Enum):
    LESSON_PRACTICE = "lesson_practice"    # Practice questions for a lesson
    LEVEL_ASSESSMENT = "level_assessment"  # End-of-level assessment
    SKILL_REINFORCEMENT = "skill_reinforcement"  # Targeted practice for weak areas
    CHALLENGE = "challenge"  # Advanced questions for high performers

# Association table for many-to-many relationship between Quiz and Question
quiz_questions = Table(
    'quiz_questions',
    Base.metadata,
    Column('quiz_id', Integer, ForeignKey('quizzes.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('question_order', Integer, default=1),  # Order of questions in quiz
    Column('weight', Float, default=1.0)  # Weight/importance of this question
)

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Quiz characteristics
    quiz_type = Column(Enum(QuizType), default=QuizType.LESSON_PRACTICE)
    difficulty_level = Column(Enum(QuizDifficultyLevel), default=QuizDifficultyLevel.BEGINNER)
    estimated_time_minutes = Column(Integer, default=10)
    
    # Skill targeting (for personalized assignment)
    target_skill_areas = Column(Text)  # JSON: ["variables", "loops", "functions"]
    prerequisite_skills = Column(Text)  # JSON: Required skills before taking this quiz
    
    # Assignment criteria
    min_skill_level = Column(Float, default=0.0)  # Minimum mastery level (0.0-1.0)
    max_skill_level = Column(Float, default=1.0)  # Maximum mastery level (0.0-1.0)
    min_accuracy_threshold = Column(Float, default=0.5)  # Min accuracy to unlock
    
    # Quiz settings
    question_count = Column(Integer, default=5)  # How many questions to show
    randomize_questions = Column(Boolean, default=True)
    time_limit_minutes = Column(Integer)  # Optional time limit
    max_attempts = Column(Integer, default=3)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("Question", secondary=quiz_questions, back_populates="quizzes")
    user_quiz_attempts = relationship("UserQuizAttempt", back_populates="quiz")
    assignments = relationship("PersonalizedQuizAssignment", back_populates="quiz")
    creator = relationship("User")

class PersonalizedQuizAssignment(Base):
    """Tracks which quizzes are assigned to which users based on their skill assessment"""
    __tablename__ = "personalized_quiz_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Assignment metadata
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assignment_reason = Column(String)  # "skill_gap", "reinforcement", "advancement", etc.
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    
    # User skill context at assignment time
    user_skill_level_snapshot = Column(Float)  # User's skill level when assigned
    target_improvement_areas = Column(Text)  # JSON: Areas this quiz targets
    
    # Assignment status
    is_active = Column(Boolean, default=True)
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    quiz = relationship("Quiz", back_populates="assignments")
    lesson = relationship("Lesson")

class UserQuizAttempt(Base):
    """Records of user attempts at specific quizzes"""
    __tablename__ = "user_quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("personalized_quiz_assignments.id"))
    
    # Attempt details
    attempt_number = Column(Integer, default=1)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    time_taken_minutes = Column(Float)
    
    # Results
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    score = Column(Integer, default=0)  # Weighted score based on question difficulty
    
    # Performance analysis
    skill_areas_performance = Column(Text)  # JSON: Performance by skill area
    question_response_times = Column(Text)  # JSON: Time taken for each question
    confidence_levels = Column(Text)  # JSON: User confidence for each answer
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_passed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")
    quiz = relationship("Quiz", back_populates="user_quiz_attempts")
    assignment = relationship("PersonalizedQuizAssignment")
    responses = relationship("UserQuizResponse", back_populates="quiz_attempt")

class UserQuizResponse(Base):
    """Individual question responses within a quiz attempt"""
    __tablename__ = "user_quiz_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("user_quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Response details
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Float)
    confidence_level = Column(Integer, default=3)  # 1-5 scale
    question_order = Column(Integer)  # Order in which question was presented
    
    # Analysis
    difficulty_perceived = Column(Integer)  # 1-5 scale, how hard user found it
    skill_area = Column(String)  # Primary skill this question tested
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz_attempt = relationship("UserQuizAttempt", back_populates="responses")
    question = relationship("Question")

class QuizRecommendation(Base):
    """AI-generated quiz recommendations for users"""
    __tablename__ = "quiz_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommended_quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Recommendation metadata
    recommendation_score = Column(Float)  # 0.0-1.0, how strongly recommended
    recommendation_reason = Column(Text)  # AI explanation of why recommended
    skill_gaps_addressed = Column(Text)  # JSON: Skills this quiz will help with
    
    # Context
    based_on_assessment_id = Column(Integer, ForeignKey("user_assessments.id"))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # User response
    user_feedback = Column(Integer)  # 1-5 rating if user provides feedback
    was_taken = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")
    quiz = relationship("Quiz")
    assessment = relationship("UserAssessment")