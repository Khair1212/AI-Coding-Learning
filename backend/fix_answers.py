#!/usr/bin/env python3

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lesson import Question

def fix_answers():
    db = SessionLocal()
    try:
        print('=== FIXING PROBLEMATIC ANSWERS ===')
        
        # Fix Lesson 3, Q3 - standardize printf quotes  
        q3_lesson3 = db.query(Question).join(Question.lesson).filter(
            Question.lesson.has(lesson_number=3),
            Question.question_text.contains('Hello, World!')
        ).first()
        
        if q3_lesson3:
            print('Fixing Lesson 3, Q3 printf quotes...')
            q3_lesson3.correct_answer = '''#include <stdio.h>

int main() {
    printf("Hello, World!");
    return 0;
}'''
            print(f'Updated: {q3_lesson3.correct_answer[:50]}...')
        
        # Fix Lesson 4, Q2 - remove markdown code blocks
        q2_lesson4 = db.query(Question).join(Question.lesson).filter(
            Question.lesson.has(lesson_number=4),
            Question.correct_answer.contains('```c')
        ).first()
        
        if q2_lesson4:
            print('Fixing Lesson 4, Q2 markdown blocks...')
            # Remove markdown and clean up the answer
            fixed_answer = '''#include <stdio.h>

int main() {
    // Declare variables to store the two numbers
    int num1, num2, sum;
    // Prompt user to enter the first number
    printf("Enter the first number: ");
    // Read the first number from user input
    scanf("%d", &num1);
    // Prompt user to enter the second number
    printf("Enter the second number: ");
    // Read the second number from user input
    scanf("%d", &num2);
    // Add the two numbers and store the result in a variable
    sum = num1 + num2;
    // Display the result
    printf("The sum of %d and %d is %d\\n", num1, num2, sum);
    return 0;
}'''
            q2_lesson4.correct_answer = fixed_answer
            print(f'Updated: {fixed_answer[:100]}...')
        
        db.commit()
        print('✅ Fixed problematic answers')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_answers()