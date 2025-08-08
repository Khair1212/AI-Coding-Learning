"""
Setup script to create sample personalized quizzes for testing
"""
import json
from app.core.database import SessionLocal, engine
from app.models import Base, Quiz, QuizType, QuizDifficultyLevel, Lesson, Level, Question

def create_sample_quizzes():
    """Create sample personalized quizzes for different skill levels"""
    db = SessionLocal()
    
    print("Setting up personalized quiz system...")
    
    # Create all tables first
    Base.metadata.create_all(bind=engine)
    
    # Get some lessons to create quizzes for
    lessons = db.query(Lesson).join(Level).order_by(Level.level_number, Lesson.lesson_number).limit(10).all()
    
    if not lessons:
        print("❌ No lessons found. Please run setup_database.py first.")
        return
    
    quizzes_created = 0
    
    for lesson in lessons:
        level_num = lesson.level.level_number
        
        # Create different quiz types based on level
        quiz_configs = []
        
        if level_num <= 3:  # Beginner levels
            quiz_configs = [
                {
                    'title': f'Practice Quiz: {lesson.title}',
                    'quiz_type': QuizType.LESSON_PRACTICE,
                    'difficulty': QuizDifficultyLevel.BEGINNER,
                    'skills': ['basics'],
                    'min_skill': 0.0,
                    'max_skill': 0.6
                },
                {
                    'title': f'Reinforcement: {lesson.title}',
                    'quiz_type': QuizType.SKILL_REINFORCEMENT,
                    'difficulty': QuizDifficultyLevel.BEGINNER,
                    'skills': ['basics'],
                    'min_skill': 0.0,
                    'max_skill': 0.4
                }
            ]
        elif level_num <= 6:  # Intermediate levels
            quiz_configs = [
                {
                    'title': f'Control Flow Practice: {lesson.title}',
                    'quiz_type': QuizType.LESSON_PRACTICE,
                    'difficulty': QuizDifficultyLevel.INTERMEDIATE,
                    'skills': ['control_flow'],
                    'min_skill': 0.3,
                    'max_skill': 0.8
                },
                {
                    'title': f'Challenge: {lesson.title}',
                    'quiz_type': QuizType.CHALLENGE,
                    'difficulty': QuizDifficultyLevel.ADVANCED,
                    'skills': ['control_flow'],
                    'min_skill': 0.7,
                    'max_skill': 1.0
                }
            ]
        elif level_num == 7:  # Functions
            quiz_configs = [
                {
                    'title': f'Functions Mastery: {lesson.title}',
                    'quiz_type': QuizType.LESSON_PRACTICE,
                    'difficulty': QuizDifficultyLevel.INTERMEDIATE,
                    'skills': ['functions'],
                    'min_skill': 0.4,
                    'max_skill': 0.9
                }
            ]
        elif level_num <= 9:  # Arrays and Strings
            quiz_configs = [
                {
                    'title': f'Arrays Practice: {lesson.title}',
                    'quiz_type': QuizType.LESSON_PRACTICE,
                    'difficulty': QuizDifficultyLevel.INTERMEDIATE,
                    'skills': ['arrays'],
                    'min_skill': 0.5,
                    'max_skill': 0.9
                }
            ]
        else:  # Pointers (Level 10)
            quiz_configs = [
                {
                    'title': f'Advanced Pointers: {lesson.title}',
                    'quiz_type': QuizType.CHALLENGE,
                    'difficulty': QuizDifficultyLevel.ADVANCED,
                    'skills': ['pointers'],
                    'min_skill': 0.7,
                    'max_skill': 1.0
                }
            ]
        
        # Create quizzes
        for config in quiz_configs:
            existing_quiz = db.query(Quiz).filter(
                Quiz.lesson_id == lesson.id,
                Quiz.title == config['title']
            ).first()
            
            if existing_quiz:
                continue  # Skip if already exists
            
            quiz = Quiz(
                title=config['title'],
                description=f"Personalized quiz for {lesson.title} targeting {', '.join(config['skills'])} skills",
                lesson_id=lesson.id,
                quiz_type=config['quiz_type'],
                difficulty_level=config['difficulty'],
                estimated_time_minutes=10,
                target_skill_areas=json.dumps(config['skills']),
                min_skill_level=config['min_skill'],
                max_skill_level=config['max_skill'],
                question_count=5,
                randomize_questions=True,
                max_attempts=3
            )
            
            db.add(quiz)
            quizzes_created += 1
            
            # Associate existing questions with this quiz
            lesson_questions = db.query(Question).filter(
                Question.lesson_id == lesson.id
            ).limit(5).all()
            
            for question in lesson_questions:
                if question not in quiz.questions:
                    quiz.questions.append(question)
    
    db.commit()
    
    print(f"✅ Created {quizzes_created} personalized quizzes!")
    print("📊 Quiz breakdown:")
    
    # Show statistics
    for quiz_type in QuizType:
        count = db.query(Quiz).filter(
            Quiz.quiz_type == quiz_type,
            Quiz.is_active == True
        ).count()
        print(f"   {quiz_type.value}: {count} quizzes")
    
    print("\n🎯 Quiz targeting:")
    skill_areas = ['basics', 'control_flow', 'functions', 'arrays', 'pointers']
    for skill in skill_areas:
        count = db.query(Quiz).filter(
            Quiz.target_skill_areas.contains(skill),
            Quiz.is_active == True
        ).count()
        print(f"   {skill}: {count} quizzes")
    
    print(f"\n✨ Personalized quiz system is ready!")
    print("🎓 Users will now get different quizzes based on their skill assessment results!")
    
    db.close()

if __name__ == "__main__":
    create_sample_quizzes()