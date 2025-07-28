"""
Populate the database with assessment questions for skill evaluation
"""
import json
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models import AssessmentQuestion

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Assessment questions covering C programming from basic to advanced
ASSESSMENT_QUESTIONS = [
    # BEGINNER LEVEL (Expected level 1-2)
    {
        "question_text": "What does the following C code output?\n\n#include <stdio.h>\nint main() {\n    printf(\"Hello World\");\n    return 0;\n}",
        "question_type": "multiple_choice",
        "correct_answer": "Hello World",
        "options": json.dumps(["Hello World", "Hello", "World", "Error"]),
        "difficulty_weight": 1.0,
        "topic_area": "basics",
        "expected_level": 1,
        "explanation": "This basic C program prints 'Hello World' to the console using printf()."
    },
    {
        "question_text": "Which of the following is the correct way to declare an integer variable in C?",
        "question_type": "multiple_choice",
        "correct_answer": "int x;",
        "options": json.dumps(["integer x;", "int x;", "var x;", "x: integer"]),
        "difficulty_weight": 1.0,
        "topic_area": "variables",
        "expected_level": 1,
        "explanation": "In C, integer variables are declared using the 'int' keyword followed by the variable name."
    },
    {
        "question_text": "What is the correct syntax to include the standard input/output library in C?",
        "question_type": "multiple_choice",
        "correct_answer": "#include <stdio.h>",
        "options": json.dumps(["#include <stdio.h>", "import stdio", "using namespace std", "#include stdio.h"]),
        "difficulty_weight": 1.0,
        "topic_area": "basics",
        "expected_level": 1,
        "explanation": "C uses #include <stdio.h> to include the standard input/output library."
    },
    
    # BASIC LEVEL (Expected level 2-4)
    {
        "question_text": "What will be the value of 'result' after this code executes?\n\nint x = 5;\nint y = 3;\nint result = x % y;",
        "question_type": "multiple_choice",
        "correct_answer": "2",
        "options": json.dumps(["1", "2", "3", "5"]),
        "difficulty_weight": 1.5,
        "topic_area": "operators",
        "expected_level": 3,
        "explanation": "The modulo operator % returns the remainder of division. 5 % 3 = 2."
    },
    {
        "question_text": "Which loop is best for iterating a known number of times?",
        "question_type": "multiple_choice",
        "correct_answer": "for loop",
        "options": json.dumps(["while loop", "for loop", "do-while loop", "goto loop"]),
        "difficulty_weight": 1.5,
        "topic_area": "loops",
        "expected_level": 4,
        "explanation": "For loops are ideal when you know exactly how many iterations you need."
    },
    {
        "question_text": "What does this code print?\n\nint i;\nfor(i = 0; i < 3; i++) {\n    printf(\"%d \", i);\n}",
        "question_type": "multiple_choice",
        "correct_answer": "0 1 2",
        "options": json.dumps(["0 1 2", "1 2 3", "0 1 2 3", "1 2"]),
        "difficulty_weight": 1.5,
        "topic_area": "loops",
        "expected_level": 4,
        "explanation": "The loop starts at 0, continues while i < 3, so it prints 0, 1, 2."
    },
    
    # INTERMEDIATE LEVEL (Expected level 5-7)
    {
        "question_text": "What happens when you call a function in C?",
        "question_type": "multiple_choice",
        "correct_answer": "A new scope is created and execution jumps to the function",
        "options": json.dumps([
            "The program ends",
            "A new scope is created and execution jumps to the function", 
            "All variables are reset",
            "Nothing happens"
        ]),
        "difficulty_weight": 2.0,
        "topic_area": "functions",
        "expected_level": 6,
        "explanation": "Function calls create a new scope (stack frame) and transfer execution to the function."
    },
    {
        "question_text": "How do you access the 3rd element of an array named 'arr' in C?",
        "question_type": "multiple_choice",
        "correct_answer": "arr[2]",
        "options": json.dumps(["arr[3]", "arr[2]", "arr(2)", "arr.2"]),
        "difficulty_weight": 2.0,
        "topic_area": "arrays",
        "expected_level": 7,
        "explanation": "Arrays in C are zero-indexed, so the 3rd element is at index 2."
    },
    {
        "question_text": "What is the difference between 'char str[10]' and 'char *str'?",
        "question_type": "multiple_choice",
        "correct_answer": "First is an array, second is a pointer",
        "options": json.dumps([
            "No difference",
            "First is an array, second is a pointer",
            "First is a pointer, second is an array", 
            "Both are the same"
        ]),
        "difficulty_weight": 2.5,
        "topic_area": "strings",
        "expected_level": 8,
        "explanation": "char str[10] declares an array of 10 characters, while char *str declares a pointer to char."
    },
    
    # ADVANCED LEVEL (Expected level 8-10)
    {
        "question_text": "What does this pointer code do?\n\nint x = 10;\nint *ptr = &x;\n*ptr = 20;\nprintf(\"%d\", x);",
        "question_type": "multiple_choice",
        "correct_answer": "Prints 20",
        "options": json.dumps(["Prints 10", "Prints 20", "Error", "Prints address"]),
        "difficulty_weight": 3.0,
        "topic_area": "pointers",
        "expected_level": 9,
        "explanation": "ptr points to x's address. *ptr = 20 changes the value at that address, so x becomes 20."
    },
    {
        "question_text": "What is the output of this code?\n\nint arr[] = {1, 2, 3};\nint *p = arr;\nprintf(\"%d\", *(p + 1));",
        "question_type": "multiple_choice",
        "correct_answer": "2",
        "options": json.dumps(["1", "2", "3", "Error"]),
        "difficulty_weight": 3.0,
        "topic_area": "pointers",
        "expected_level": 9,
        "explanation": "p points to arr[0]. p+1 points to arr[1], so *(p+1) gives the value 2."
    },
    {
        "question_text": "What happens if you don't free() dynamically allocated memory?",
        "question_type": "multiple_choice",
        "correct_answer": "Memory leak occurs",
        "options": json.dumps([
            "Nothing happens",
            "Program crashes immediately",
            "Memory leak occurs",
            "Automatic cleanup"
        ]),
        "difficulty_weight": 3.5,
        "topic_area": "memory",
        "expected_level": 10,
        "explanation": "Not calling free() on malloc'd memory causes memory leaks - the memory remains allocated but inaccessible."
    },
    
    # CONCEPTUAL QUESTIONS
    {
        "question_text": "What is the main purpose of the 'return 0;' statement in main()?",
        "question_type": "multiple_choice",
        "correct_answer": "Indicates successful program execution to the operating system",
        "options": json.dumps([
            "Ends the program",
            "Returns to the beginning",
            "Indicates successful program execution to the operating system",
            "It's not necessary"
        ]),
        "difficulty_weight": 1.5,
        "topic_area": "basics",
        "expected_level": 2,
        "explanation": "return 0 in main() signals to the OS that the program executed successfully (0 = success)."
    },
    {
        "question_text": "Why do we use functions in programming?",
        "question_type": "multiple_choice",
        "correct_answer": "Code reusability, organization, and modularity",
        "options": json.dumps([
            "To make programs longer",
            "Code reusability, organization, and modularity",
            "To use more memory",
            "Because it's required"
        ]),
        "difficulty_weight": 2.0,
        "topic_area": "functions",
        "expected_level": 6,
        "explanation": "Functions promote code reuse, better organization, easier testing, and modular design."
    },
    {
        "question_text": "What is the key advantage of pointers in C?",
        "question_type": "multiple_choice",
        "correct_answer": "Direct memory access and dynamic memory allocation",
        "options": json.dumps([
            "They make code faster always",
            "Direct memory access and dynamic memory allocation",
            "They prevent errors",
            "They are easier to use"
        ]),
        "difficulty_weight": 3.0,
        "topic_area": "pointers",
        "expected_level": 9,
        "explanation": "Pointers allow direct memory manipulation, dynamic allocation, and efficient data structure implementation."
    }
]

def create_assessment_questions():
    db = SessionLocal()
    
    try:
        # Check if assessment questions already exist
        existing_questions = db.query(AssessmentQuestion).count()
        if existing_questions > 0:
            print("Assessment questions already exist. Skipping population.")
            return
        
        question_count = 0
        
        for q_data in ASSESSMENT_QUESTIONS:
            question = AssessmentQuestion(
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                correct_answer=q_data["correct_answer"],
                options=q_data.get("options"),
                difficulty_weight=q_data["difficulty_weight"],
                topic_area=q_data["topic_area"],
                expected_level=q_data["expected_level"],
                explanation=q_data["explanation"]
            )
            db.add(question)
            question_count += 1
        
        db.commit()
        print(f"Successfully created {question_count} assessment questions!")
        print("Assessment covers:")
        print("- Beginner (Levels 1-2): Basic syntax, variables, I/O")
        print("- Basic (Levels 3-4): Operators, loops, control flow")
        print("- Intermediate (Levels 5-7): Functions, arrays, strings") 
        print("- Advanced (Levels 8-10): Pointers, memory management")
        
    except Exception as e:
        print(f"Error creating assessment questions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_assessment_questions()