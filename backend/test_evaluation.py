#!/usr/bin/env python3

from app.api.learning import evaluate_answer, normalize_code
from app.models.lesson import LessonType

# Test cases for the improved evaluation logic
print('=== TESTING IMPROVED ANSWER EVALUATION ===')
print()

# Test 1: Fill in blank
print('Test 1: Fill in blank (printf)')
user_answer = 'printf'
correct_answer = '"printf"'
question_type = LessonType.FILL_IN_BLANK
result = evaluate_answer(user_answer, correct_answer, question_type)
print(f'User: {user_answer}')
print(f'Expected: {correct_answer}')
print(f'Result: {"✅" if result else "❌"}')
print()

# Test 2: Multiple choice
print('Test 2: Multiple choice')
user_answer = 'c'
correct_answer = 'C'
question_type = LessonType.MULTIPLE_CHOICE
result = evaluate_answer(user_answer, correct_answer, question_type)
print(f'User: {user_answer}')
print(f'Expected: {correct_answer}')
print(f'Result: {"✅" if result else "❌"}')
print()

# Test 3: Coding exercise - Hello World with different quotes
print('Test 3: Coding exercise (Hello World with double quotes)')
user_answer = '''#include <stdio.h>
int main() {
    printf("Hello, World!");
    return 0;
}'''
correct_answer = '''#include <stdio.h>

int main() {
    printf("Hello, World!");
    return 0;
}'''
question_type = LessonType.CODING_EXERCISE
result = evaluate_answer(user_answer, correct_answer, question_type)
print(f'User code: {user_answer[:50]}...')
print(f'Expected code: {correct_answer[:50]}...')
print(f'Result: {"✅" if result else "❌"}')
print()

# Test 4: Coding exercise - Hello World with single quotes (should now work)
print('Test 4: Coding exercise (Hello World with single quotes)')
user_answer = '''#include <stdio.h>
int main() {
    printf('Hello, World!');
    return 0;
}'''
result = evaluate_answer(user_answer, correct_answer, question_type)
print(f'User code (single quotes): {user_answer[40:70]}...')
print(f'Result: {"✅" if result else "❌"}')
print()

# Test 5: Code normalization
print('Test 5: Code normalization')
messy_code = '''```c
#include <stdio.h>

int   main()   {
    printf(   'Hello,     World!'   );
    return 0;
}
```'''
normalized = normalize_code(messy_code)
print(f'Original: {messy_code[:50]}...')
print(f'Normalized: {normalized}')
print()

# Test 6: Real problematic case from database
print('Test 6: Addition program with comments')
user_simple = '''#include <stdio.h>
int main() {
    int num1, num2, sum;
    printf("Enter first number: ");
    scanf("%d", &num1);
    printf("Enter second number: ");
    scanf("%d", &num2);
    sum = num1 + num2;
    printf("Sum is %d", sum);
    return 0;
}'''

correct_with_comments = '''#include <stdio.h>

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

result = evaluate_answer(user_simple, correct_with_comments, question_type)
print(f'User (no comments): {user_simple[:60]}...')
print(f'Expected (with comments): {correct_with_comments[:60]}...')
print(f'Result: {"✅" if result else "❌"}')

if __name__ == "__main__":
    pass