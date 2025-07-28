"""
Complete database setup script for AI Coding Learner
"""
from app.core.database import engine, Base
from init_levels import create_levels_and_lessons
from populate_questions import create_sample_questions

def setup_database():
    """Create all tables and populate with initial data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")
    
    print("\nInitializing levels and lessons...")
    create_levels_and_lessons()
    
    print("\nPopulating sample questions...")
    create_sample_questions()
    
    print("\n✅ Database setup complete!")
    print("\nYou can now:")
    print("1. Start the backend: uvicorn app.main:app --reload")
    print("2. Start the frontend: npm start")
    print("3. Register a new user and start learning C programming!")

if __name__ == "__main__":
    setup_database()