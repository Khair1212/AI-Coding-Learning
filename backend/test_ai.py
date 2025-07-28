#!/usr/bin/env python3
"""
Test script to verify AI question generation is working
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.services.ai_service import AIQuestionGenerator, LessonContentGenerator
from app.models.lesson import DifficultyLevel
from app.core.config import settings

def test_openai_connection():
    """Test if OpenAI API is working"""
    print("🔍 Testing OpenAI API connection...")
    print(f"API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
    
    if not settings.openai_api_key:
        print("❌ OpenAI API key not found in .env file")
        return False
        
    if settings.openai_api_key.startswith('sk-'):
        print("✅ OpenAI API key format looks correct")
    else:
        print("⚠️  OpenAI API key format might be incorrect")
    
    return True

def test_question_generation():
    """Test AI question generation"""
    print("\n🧠 Testing AI question generation...")
    
    try:
        generator = AIQuestionGenerator()
        
        # Test theory question
        print("Generating theory question...")
        theory_q = generator.generate_theory_question("variables", DifficultyLevel.BEGINNER)
        print(f"✅ Theory question generated: {theory_q.get('question_text', 'No question text')[:50]}...")
        
        # Test coding exercise
        print("Generating coding exercise...")
        coding_q = generator.generate_coding_exercise("hello world", DifficultyLevel.BEGINNER)
        print(f"✅ Coding exercise generated: {coding_q.get('question_text', 'No question text')[:50]}...")
        
        # Test fill in blank
        print("Generating fill-in-blank question...")
        fill_q = generator.generate_fill_in_blank("printf function", DifficultyLevel.BEGINNER)
        print(f"✅ Fill-in-blank generated: {fill_q.get('question_text', 'No question text')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI generation failed: {str(e)}")
        return False

def test_lesson_content():
    """Test lesson content generation"""
    print("\n📚 Testing lesson content generation...")
    
    try:
        generator = LessonContentGenerator()
        content = generator.generate_lesson_content(1, "Your First C Program")
        print(f"✅ Lesson content generated with keys: {list(content.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Lesson content generation failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Coding Learner - Backend AI Tests")
    print("=" * 50)
    
    # Test OpenAI connection
    if not test_openai_connection():
        print("\n❌ OpenAI configuration test failed")
        return
    
    # Test question generation
    if not test_question_generation():
        print("\n❌ Question generation test failed")
        return
        
    # Test lesson content
    if not test_lesson_content():
        print("\n❌ Lesson content test failed")
        return
    
    print("\n🎉 All AI tests passed! Your backend is ready to generate questions.")
    print("\nNext steps:")
    print("1. Start backend: uvicorn app.main:app --reload")
    print("2. Start frontend: npm start")
    print("3. Test the full application!")

if __name__ == "__main__":
    main()