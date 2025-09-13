#!/usr/bin/env python3
"""
Add test cases to existing coding exercise questions for output-based evaluation
"""

import json
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models import Question, LessonType
from app.services.code_execution_service import CodeExecutionService

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_test_cases():
    db = SessionLocal()
    code_service = CodeExecutionService()
    
    try:
        print('=== ADDING TEST CASES TO CODING EXERCISES ===')
        
        # Get all coding exercise questions
        coding_questions = db.query(Question).filter(
            Question.question_type == LessonType.CODING_EXERCISE
        ).all()
        
        print(f"Found {len(coding_questions)} coding exercise questions")
        
        for question in coding_questions:
            print(f"\nProcessing question {question.id}: {question.question_text[:60]}...")
            
            # Skip if already has test cases
            if question.test_cases and question.test_cases.strip():
                print(f"  Already has test cases, skipping")
                continue
            
            # Determine test cases based on question content
            test_cases = determine_test_cases(question, code_service)
            
            if test_cases:
                question.test_cases = test_cases
                print(f"  Added test cases: {test_cases[:100]}...")
            else:
                print(f"  Could not determine appropriate test cases")
        
        db.commit()
        print('\n✅ Test cases added successfully')
        
        # Show summary
        updated_count = db.query(Question).filter(
            Question.question_type == LessonType.CODING_EXERCISE,
            Question.test_cases.isnot(None),
            Question.test_cases != ""
        ).count()
        
        print(f"📊 Summary: {updated_count}/{len(coding_questions)} coding questions now have test cases")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def determine_test_cases(question: Question, code_service: CodeExecutionService) -> str:
    """Determine appropriate test cases based on question content"""
    
    question_text = question.question_text.lower()
    correct_answer = question.correct_answer.lower() if question.correct_answer else ""
    
    # Hello World programs
    if 'hello' in question_text and 'world' in question_text:
        return code_service.create_simple_test_case("Hello, World!")
    
    # Welcome programs
    if 'welcome' in question_text:
        if 'welcome to c' in question_text:
            return code_service.create_simple_test_case("Welcome to C!")
        else:
            return code_service.create_simple_test_case("Welcome!")
    
    # Addition programs
    if ('addition' in question_text or 'add' in question_text or 'sum' in question_text) and 'scanf' in correct_answer:
        test_cases = [
            {
                "input": "5\n3\n",
                "expected_output": "Enter the first number: Enter the second number: The sum of 5 and 3 is 8",
                "description": "Addition of 5 and 3"
            },
            {
                "input": "10\n20\n",
                "expected_output": "Enter the first number: Enter the second number: The sum of 10 and 20 is 30",
                "description": "Addition of 10 and 20"
            },
            {
                "input": "0\n0\n",
                "expected_output": "Enter the first number: Enter the second number: The sum of 0 and 0 is 0",
                "description": "Addition of zeros"
            }
        ]
        return json.dumps(test_cases)
    
    # Simple calculation programs (multiplication, subtraction, etc.)
    if ('multiply' in question_text or 'product' in question_text) and 'scanf' in correct_answer:
        test_cases = [
            {
                "input": "4\n5\n",
                "expected_output": "Enter the first number: Enter the second number: The product of 4 and 5 is 20",
                "description": "Multiplication of 4 and 5"
            },
            {
                "input": "3\n7\n",
                "expected_output": "Enter the first number: Enter the second number: The product of 3 and 7 is 21",
                "description": "Multiplication of 3 and 7"
            }
        ]
        return json.dumps(test_cases)
    
    # Simple output programs (like printing name)
    if 'print' in question_text and 'name' in question_text:
        return code_service.create_simple_test_case("My name is John")
    
    # Age programs
    if 'age' in question_text and 'scanf' in correct_answer:
        test_cases = [
            {
                "input": "25\n",
                "expected_output": "Enter your age: You are 25 years old",
                "description": "Age input test"
            }
        ]
        return json.dumps(test_cases)
    
    # Temperature conversion
    if 'temperature' in question_text or 'celsius' in question_text or 'fahrenheit' in question_text:
        test_cases = [
            {
                "input": "0\n",
                "expected_output": "Enter temperature in Celsius: 0°C is 32°F",
                "description": "Freezing point conversion"
            },
            {
                "input": "100\n",
                "expected_output": "Enter temperature in Celsius: 100°C is 212°F",
                "description": "Boiling point conversion"
            }
        ]
        return json.dumps(test_cases)
    
    # Area calculations
    if 'area' in question_text:
        if 'rectangle' in question_text:
            test_cases = [
                {
                    "input": "5\n3\n",
                    "expected_output": "Enter length: Enter width: Area of rectangle is 15",
                    "description": "Rectangle area calculation"
                }
            ]
            return json.dumps(test_cases)
        elif 'circle' in question_text:
            test_cases = [
                {
                    "input": "5\n",
                    "expected_output": "Enter radius: Area of circle is 78.54",
                    "description": "Circle area calculation"
                }
            ]
            return json.dumps(test_cases)
    
    # Simple greeting programs
    if 'printf' in correct_answer and not 'scanf' in correct_answer:
        # Try to extract the expected output from the printf statement
        import re
        printf_matches = re.findall(r'printf\s*\(\s*["\']([^"\']*)["\']', correct_answer)
        if printf_matches:
            expected_output = printf_matches[0].replace('\\n', '\n')
            return code_service.create_simple_test_case(expected_output)
    
    # Default: just check if it compiles and runs without input
    return code_service.create_simple_test_case("")

def update_specific_questions():
    """Update specific problematic questions mentioned by the user"""
    db = SessionLocal()
    code_service = CodeExecutionService()
    
    try:
        print('=== UPDATING SPECIFIC PROBLEMATIC QUESTIONS ===')
        
        # Find Level 1 Q2 (the one mentioned in the terminal selection)
        # This is likely a Hello World or similar basic program
        level_1_questions = db.query(Question).join(Question.lesson).filter(
            Question.lesson.has(lesson_number=1),
            Question.question_type == LessonType.CODING_EXERCISE
        ).all()
        
        for question in level_1_questions:
            print(f"\nLevel 1 Question {question.id}: {question.question_text[:80]}...")
            
            # Check if this looks like the problematic question
            if 'hello' in question.question_text.lower() or 'print' in question.question_text.lower():
                # Create a test case that expects a newline
                test_cases = [
                    {
                        "input": "",
                        "expected_output": "Hello, World!\n",  # Note the explicit newline
                        "description": "Basic Hello World output with newline"
                    }
                ]
                question.test_cases = json.dumps(test_cases)
                print(f"  Updated with newline-aware test case")
        
        db.commit()
        print('✅ Specific questions updated')
        
    except Exception as e:
        print(f"❌ Error updating specific questions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Add test cases to all coding exercises")
    print("2. Update specific problematic questions")
    print("3. Both")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        add_test_cases()
    elif choice == "2":
        update_specific_questions()
    elif choice == "3":
        add_test_cases()
        update_specific_questions()
    else:
        print("Invalid choice")
