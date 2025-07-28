"""
Populate the database with sample questions for C programming lessons
"""
import json
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models import Lesson, Question, LessonType

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample questions for Level 1 (Hello, C World!)
SAMPLE_QUESTIONS = {
    "What is C Programming?": [
        {
            "question_text": "What does the 'C' in C programming language stand for?",
            "question_type": LessonType.MULTIPLE_CHOICE,
            "correct_answer": "It was developed after B programming language",
            "options": json.dumps([
                "Computer",
                "Code", 
                "It was developed after B programming language",
                "Creative"
            ]),
            "explanation": "C was developed by Dennis Ritchie at Bell Labs as a successor to the B programming language."
        }
    ],
    "Your First C Program": [
        {
            "question_text": "Complete the Hello World program:\n\n#include <stdio.h>\nint main() {\n    _____(\"Hello, World!\\n\");\n    return 0;\n}",
            "question_type": LessonType.FILL_IN_BLANK,
            "correct_answer": "printf",
            "explanation": "printf() is the standard function used to print text to the console in C."
        },
        {
            "question_text": "Write a complete C program that prints 'Welcome to C!' to the console.",
            "question_type": LessonType.CODING_EXERCISE,
            "correct_answer": "#include <stdio.h>\nint main() {\n    printf(\"Welcome to C!\\n\");\n    return 0;\n}",
            "code_template": "#include <stdio.h>\nint main() {\n    // TODO: Print 'Welcome to C!' here\n    return 0;\n}",
            "explanation": "A complete C program needs the stdio.h header, main function, printf statement, and return 0."
        }
    ],
    "Understanding main() function": [
        {
            "question_text": "What does the main() function return in C?",
            "question_type": LessonType.MULTIPLE_CHOICE,
            "correct_answer": "An integer value",
            "options": json.dumps([
                "A string",
                "An integer value",
                "Nothing (void)",
                "A character"
            ]),
            "explanation": "The main() function returns an integer value to the operating system. 0 typically indicates successful execution."
        }
    ],
    "Comments in C": [
        {
            "question_text": "Which of these is the correct way to write a single-line comment in C?",
            "question_type": LessonType.MULTIPLE_CHOICE,
            "correct_answer": "// This is a comment",
            "options": json.dumps([
                "# This is a comment",
                "// This is a comment",
                "<!-- This is a comment -->",
                "* This is a comment"
            ]),
            "explanation": "Single-line comments in C start with // and continue to the end of the line."
        }
    ],
    "Introduction to Variables": [
        {
            "question_text": "Declare an integer variable named 'age' and assign it the value 25.",
            "question_type": LessonType.CODING_EXERCISE,
            "correct_answer": "int age = 25;",
            "code_template": "// TODO: Declare and initialize an integer variable 'age' with value 25",
            "explanation": "Variables in C are declared with the data type followed by the variable name, and can be initialized with a value."
        }
    ],
    "Basic Data Types (int, char, float)": [
        {
            "question_text": "Which data type is used to store a single character in C?",
            "question_type": LessonType.MULTIPLE_CHOICE,
            "correct_answer": "char",
            "options": json.dumps([
                "string",
                "char",
                "character",
                "text"
            ]),
            "explanation": "The 'char' data type is used to store a single character in C, enclosed in single quotes."
        }
    ]
}

def create_sample_questions():
    db = SessionLocal()
    
    try:
        # Check if questions already exist
        existing_questions = db.query(Question).count()
        if existing_questions > 0:
            print("Questions already exist. Skipping population.")
            return
        
        # Get lessons from database
        lessons = db.query(Lesson).all()
        lesson_dict = {lesson.title: lesson for lesson in lessons}
        
        question_count = 0
        for lesson_title, questions in SAMPLE_QUESTIONS.items():
            if lesson_title in lesson_dict:
                lesson = lesson_dict[lesson_title]
                
                for q_data in questions:
                    question = Question(
                        lesson_id=lesson.id,
                        question_text=q_data["question_text"],
                        question_type=q_data["question_type"],
                        correct_answer=q_data["correct_answer"],
                        options=q_data.get("options"),
                        explanation=q_data["explanation"],
                        code_template=q_data.get("code_template"),
                        test_cases=q_data.get("test_cases")
                    )
                    db.add(question)
                    question_count += 1
                
                print(f"Added {len(questions)} questions for lesson: {lesson_title}")
        
        db.commit()
        print(f"Successfully created {question_count} sample questions!")
        
    except Exception as e:
        print(f"Error creating questions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_questions()