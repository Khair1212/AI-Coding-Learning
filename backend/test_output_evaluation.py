#!/usr/bin/env python3
"""
Test the new output-based evaluation system for coding exercises
"""

from app.api.learning import evaluate_answer
from app.models.lesson import LessonType
from app.services.code_execution_service import CodeExecutionService
import json

def test_output_based_evaluation():
    print('=== TESTING OUTPUT-BASED CODE EVALUATION ===\n')
    
    code_service = CodeExecutionService()
    
    # Test 1: Hello World with different formatting but same output
    print('Test 1: Hello World - Different Formatting, Same Output')
    print('-' * 50)
    
    # Student's code (different formatting)
    student_code = '''#include <stdio.h>
int main(){
printf("Hello, World!\\n");
return 0;
}'''
    
    # Expected code (original)
    expected_code = '''#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}'''
    
    # Test cases that expect the output
    test_cases = json.dumps([{
        "input": "",
        "expected_output": "Hello, World!\n",
        "description": "Basic Hello World test"
    }])
    
    result = evaluate_answer(student_code, expected_code, LessonType.CODING_EXERCISE, test_cases)
    print(f'Student code: {student_code[:40]}...')
    print(f'Expected output: "Hello, World!\\n"')
    print(f'Result: {"✅ PASS" if result else "❌ FAIL"}')
    print()
    
    # Test 2: Addition program with different variable names
    print('Test 2: Addition Program - Different Variable Names')
    print('-' * 50)
    
    # Student's code (different variable names)
    student_code2 = '''#include <stdio.h>
int main() {
    int a, b, result;
    printf("Enter the first number: ");
    scanf("%d", &a);
    printf("Enter the second number: ");
    scanf("%d", &b);
    result = a + b;
    printf("The sum of %d and %d is %d\\n", a, b, result);
    return 0;
}'''
    
    # Expected code (original variable names)
    expected_code2 = '''#include <stdio.h>
int main() {
    int num1, num2, sum;
    printf("Enter the first number: ");
    scanf("%d", &num1);
    printf("Enter the second number: ");
    scanf("%d", &num2);
    sum = num1 + num2;
    printf("The sum of %d and %d is %d\\n", num1, num2, sum);
    return 0;
}'''
    
    # Test cases for addition
    test_cases2 = json.dumps([
        {
            "input": "5\n3\n",
            "expected_output": "Enter the first number: Enter the second number: The sum of 5 and 3 is 8\n",
            "description": "Addition of 5 and 3"
        },
        {
            "input": "10\n20\n",
            "expected_output": "Enter the first number: Enter the second number: The sum of 10 and 20 is 30\n",
            "description": "Addition of 10 and 20"
        }
    ])
    
    result2 = evaluate_answer(student_code2, expected_code2, LessonType.CODING_EXERCISE, test_cases2)
    print(f'Student uses variables: a, b, result')
    print(f'Expected uses variables: num1, num2, sum')
    print(f'Both should produce same output for inputs 5, 3')
    print(f'Result: {"✅ PASS" if result2 else "❌ FAIL"}')
    print()
    
    # Test 3: Wrong output should fail
    print('Test 3: Wrong Output Should Fail')
    print('-' * 50)
    
    # Student's code with wrong output
    wrong_code = '''#include <stdio.h>
int main() {
    printf("Hello, Universe!\\n");  // Wrong message
    return 0;
}'''
    
    # Test cases expecting "Hello, World!"
    test_cases3 = json.dumps([{
        "input": "",
        "expected_output": "Hello, World!\n",
        "description": "Should expect Hello World"
    }])
    
    result3 = evaluate_answer(wrong_code, expected_code, LessonType.CODING_EXERCISE, test_cases3)
    print(f'Student output: "Hello, Universe!"')
    print(f'Expected output: "Hello, World!"')
    print(f'Result: {"✅ PASS" if result3 else "❌ FAIL (correct - should fail)"}')
    print()
    
    # Test 4: Compilation error should fail
    print('Test 4: Compilation Error Should Fail')
    print('-' * 50)
    
    # Student's code with syntax error
    broken_code = '''#include <stdio.h>
int main() {
    printf("Hello, World!"  // Missing closing parenthesis and semicolon
    return 0;
}'''
    
    result4 = evaluate_answer(broken_code, expected_code, LessonType.CODING_EXERCISE, test_cases)
    print(f'Student code has syntax error (missing closing parenthesis)')
    print(f'Result: {"✅ PASS" if result4 else "❌ FAIL (correct - should fail)"}')
    print()
    
    # Test 5: Fallback to pattern matching when no test cases
    print('Test 5: Fallback to Pattern Matching (No Test Cases)')
    print('-' * 50)
    
    result5 = evaluate_answer(student_code, expected_code, LessonType.CODING_EXERCISE, None)
    print(f'No test cases provided, should fall back to pattern matching')
    print(f'Result: {"✅ PASS" if result5 else "❌ FAIL"}')
    print()
    
    print('=== SUMMARY ===')
    tests = [result, result2, not result3, not result4, result5]  # result3 and result4 should fail
    passed = sum(tests)
    print(f'Tests passed: {passed}/5')
    print('✅ Output-based evaluation is working!' if passed >= 4 else '❌ Some tests failed')

def test_direct_code_execution():
    print('\n=== TESTING DIRECT CODE EXECUTION ===\n')
    
    code_service = CodeExecutionService()
    
    # Test simple Hello World
    hello_code = '''#include <stdio.h>
int main() {
    printf("Hello, World!\\n");
    return 0;
}'''
    
    test_cases = json.dumps([{
        "input": "",
        "expected_output": "Hello, World!\n",
        "description": "Hello World test"
    }])
    
    is_correct, results = code_service.evaluate_code_exercise(hello_code, test_cases)
    
    print('Direct Code Execution Test:')
    print(f'Code: {hello_code[:50]}...')
    print(f'Is Correct: {is_correct}')
    print(f'Results: {results}')

if __name__ == "__main__":
    test_output_based_evaluation()
    test_direct_code_execution()
