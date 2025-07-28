"""
Complete setup script for AI Coding Learner with Adaptive Assessment System
"""
from app.core.database import engine, Base
from init_levels import create_levels_and_lessons
from populate_questions import create_sample_questions
from populate_assessment import create_assessment_questions

def setup_adaptive_learning_system():
    """Create all tables and populate with initial data including assessment system"""
    print("🚀 Setting up AI Coding Learner with Adaptive Assessment System")
    print("=" * 60)
    
    print("\n1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
    
    print("\n2. Initializing C programming levels and lessons...")
    create_levels_and_lessons()
    
    print("\n3. Populating sample questions...")
    create_sample_questions()
    
    print("\n4. Creating skill assessment questions...")
    create_assessment_questions()
    
    print("\n" + "=" * 60)
    print("✅ ADAPTIVE LEARNING SYSTEM SETUP COMPLETE!")
    print("\n🎉 Your AI Coding Learner now features:")
    print("   📊 Skill Assessment (15 questions covering all C topics)")
    print("   🧠 Adaptive Difficulty (AI adjusts to user skill level)")
    print("   📈 Progress Tracking (Topic mastery & learning velocity)")
    print("   🎯 Personalized Recommendations")
    print("   🔄 Dynamic Level Unlocking")
    
    print("\n📋 What you can do now:")
    print("   1. Start the backend: uvicorn app.main:app --reload")
    print("   2. Start the frontend: npm start")
    print("   3. Register a new user")
    print("   4. Take the skill assessment (/assessment)")
    print("   5. Get personalized learning recommendations!")
    
    print("\n🌟 Assessment Features:")
    print("   • 15 carefully crafted questions")
    print("   • Covers: Basics → Variables → Loops → Functions → Pointers")
    print("   • Determines skill level: Beginner to Expert")
    print("   • Recommends starting level (1-10)")
    print("   • Tracks topic-specific mastery")
    print("   • Generates personalized study plan")
    
    print("\n🤖 AI Features:")
    print("   • Dynamic question generation based on user skill")
    print("   • Adaptive difficulty adjustment")
    print("   • Learning velocity tracking")
    print("   • Performance-based level recommendations")
    
    print("\n🎓 Learning Path:")
    print("   Level 1-2:  Hello World, Variables, I/O")
    print("   Level 3-4:  Operators, Expressions")
    print("   Level 5-6:  Control Flow, Conditions, Loops")
    print("   Level 7:    Functions, Scope")
    print("   Level 8-9:  Arrays, Strings")
    print("   Level 10:   Pointers, Memory Management")
    
    print(f"\n💾 Database: Assessment questions ready!")
    print(f"🔑 API Endpoints:")
    print(f"   • POST /api/assessment/start - Begin assessment")
    print(f"   • POST /api/assessment/submit - Submit answers")
    print(f"   • GET  /api/assessment/profile - Get skill profile")
    print(f"   • GET  /api/assessment/history - View past assessments")
    
    print("\n🚀 Ready to revolutionize C programming education!")

if __name__ == "__main__":
    setup_adaptive_learning_system()