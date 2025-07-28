from openai import OpenAI
import json
from typing import Dict, List, Any
from app.core.config import settings
from app.models.lesson import LessonType, DifficultyLevel

class AIQuestionGenerator:
    def __init__(self):
        if not settings.openai_api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_theory_question(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate a theory-based multiple choice question about C programming"""
        if not self.client:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
            
        prompt = f"""
        Create a multiple choice question about {topic} in C programming at {difficulty.value} level.
        
        Return a JSON object with:
        - question_text: The question
        - options: Array of 4 options (A, B, C, D)
        - correct_answer: The correct option letter
        - explanation: Brief explanation of the correct answer
        
        Make it educational and engaging like Duolingo.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"Failed to generate question: {str(e)}")
    
    def generate_coding_exercise(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate a coding exercise for C programming"""
        if not self.client:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
            
        prompt = f"""
        Create a coding exercise about {topic} in C programming at {difficulty.value} level.
        
        Return a JSON object with:
        - question_text: Description of what to code
        - code_template: Basic C code structure with // TODO comments
        - correct_answer: Complete working solution
        - test_cases: Array of test cases with input/expected_output
        - explanation: Brief explanation of the solution approach
        
        Keep it simple and educational like Duolingo coding exercises.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"Failed to generate coding exercise: {str(e)}")
    
    def generate_fill_in_blank(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate a fill-in-the-blank question for C programming"""
        if not self.client:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
            
        prompt = f"""
        Create a fill-in-the-blank question about {topic} in C programming at {difficulty.value} level.
        
        Return a JSON object with:
        - question_text: C code with blanks marked as ___
        - correct_answer: The missing word/phrase
        - explanation: Brief explanation
        
        Make it engaging and educational.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"Failed to generate fill-in-blank question: {str(e)}")

class LessonContentGenerator:
    def __init__(self):
        if not settings.openai_api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_lesson_content(self, level: int, lesson_title: str) -> Dict[str, Any]:
        """Generate lesson content for C programming"""
        if not self.client:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
            
        prompt = f"""
        Create educational content for Level {level} lesson: "{lesson_title}" in C programming.
        
        Return a JSON object with:
        - theory: Detailed explanation of the concept
        - examples: Array of 2-3 code examples with comments
        - key_points: Array of important points to remember
        - common_mistakes: Array of common errors to avoid
        
        Make it beginner-friendly and progressive like Duolingo lessons.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"Failed to generate lesson content: {str(e)}")

# C Programming curriculum structure
C_PROGRAMMING_LEVELS = {
    1: {
        "title": "Hello, C World!",
        "description": "Introduction to C programming and your first program",
        "lessons": [
            "What is C Programming?",
            "Your First C Program",
            "Understanding main() function",
            "Comments in C"
        ]
    },
    2: {
        "title": "Variables and Data Types",
        "description": "Learn about storing and using data in C",
        "lessons": [
            "Introduction to Variables",
            "Basic Data Types (int, char, float)",
            "Variable Declaration and Initialization",
            "Constants in C"
        ]
    },
    3: {
        "title": "Input and Output",
        "description": "Communicate with users through input and output",
        "lessons": [
            "printf() Function",
            "scanf() Function", 
            "Format Specifiers",
            "Reading and Writing Characters"
        ]
    },
    4: {
        "title": "Operators and Expressions",
        "description": "Perform calculations and operations",
        "lessons": [
            "Arithmetic Operators",
            "Assignment Operators",
            "Comparison Operators",
            "Logical Operators"
        ]
    },
    5: {
        "title": "Control Flow - Conditions",
        "description": "Make decisions in your programs",
        "lessons": [
            "if Statement",
            "if-else Statement",
            "else-if Ladder",
            "switch Statement"
        ]
    },
    6: {
        "title": "Control Flow - Loops",
        "description": "Repeat actions efficiently",
        "lessons": [
            "while Loop",
            "for Loop",
            "do-while Loop",
            "Loop Control (break, continue)"
        ]
    },
    7: {
        "title": "Functions",
        "description": "Organize code with reusable functions",
        "lessons": [
            "Function Declaration and Definition",
            "Function Parameters and Arguments",
            "Return Values",
            "Scope and Local Variables"
        ]
    },
    8: {
        "title": "Arrays",
        "description": "Store and manipulate collections of data",
        "lessons": [
            "Introduction to Arrays",
            "Array Declaration and Initialization",
            "Accessing Array Elements",
            "Multidimensional Arrays"
        ]
    },
    9: {
        "title": "Strings",
        "description": "Work with text and string manipulation",
        "lessons": [
            "Character Arrays and Strings",
            "String Input and Output",
            "String Functions (strlen, strcpy, strcmp)",
            "String Manipulation"
        ]
    },
    10: {
        "title": "Pointers and Memory",
        "description": "Advanced concepts - pointers and memory management",
        "lessons": [
            "Introduction to Pointers",
            "Pointer Declaration and Initialization",
            "Pointer Arithmetic",
            "Dynamic Memory Allocation"
        ]
    }
}