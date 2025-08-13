#!/usr/bin/env python3
"""
Script to create sample data for the admin dashboard
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import User, UserProfile, UserLessonProgress, UserAssessment, Level, Lesson, UserRole, SkillLevel
from app.core.security import get_password_hash

def create_sample_users(db, count=20):
    """Create sample users"""
    print(f"Creating {count} sample users...")
    
    users_created = 0
    for i in range(count):
        # Create users with varied registration dates (last 30 days)
        created_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        user = User(
            email=f"user{i+1}@example.com",
            username=f"user{i+1}",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_active=random.choice([True, True, True, False]),  # 75% active
            created_at=created_date
        )
        
        # Check if user already exists
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            continue
            
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            current_level=random.randint(1, 5),
            total_xp=random.randint(0, 1000),
            current_streak=random.randint(0, 10),
            longest_streak=random.randint(0, 15),
            lessons_completed=random.randint(0, 20),
            accuracy_rate=random.uniform(40, 95)
        )
        db.add(profile)
        users_created += 1
    
    db.commit()
    print(f"✅ Created {users_created} sample users")

def create_sample_lesson_progress(db):
    """Create sample lesson progress data"""
    print("Creating sample lesson progress...")
    
    # Get all users and lessons
    users = db.query(User).filter(User.role == UserRole.USER).all()
    lessons = db.query(Lesson).all()
    
    progress_created = 0
    
    for user in users:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            continue
            
        # Each user completes some random lessons
        num_lessons_to_complete = random.randint(0, min(15, len(lessons)))
        completed_lessons = random.sample(lessons, num_lessons_to_complete)
        
        for lesson in completed_lessons:
            # Check if progress already exists
            existing = db.query(UserLessonProgress).filter(
                UserLessonProgress.user_profile_id == profile.id,
                UserLessonProgress.lesson_id == lesson.id
            ).first()
            
            if existing:
                continue
            
            progress = UserLessonProgress(
                user_profile_id=profile.id,
                lesson_id=lesson.id,
                is_completed=random.choice([True, True, False]),  # 67% completion rate
                score=random.uniform(60, 100),
                attempts=random.randint(1, 3),
                xp_earned=random.randint(10, 50),
                completed_at=datetime.now() - timedelta(days=random.randint(0, 20))
            )
            db.add(progress)
            progress_created += 1
    
    db.commit()
    print(f"✅ Created {progress_created} lesson progress records")

def create_sample_assessments(db):
    """Create sample assessment data"""
    print("Creating sample assessments...")
    
    users = db.query(User).filter(User.role == UserRole.USER).all()
    assessments_created = 0
    
    for user in users:
        # 70% of users have taken assessments
        if random.random() < 0.7:
            num_assessments = random.randint(1, 3)
            
            for i in range(num_assessments):
                # Check if assessment already exists
                existing = db.query(UserAssessment).filter(
                    UserAssessment.user_id == user.id
                ).first()
                
                if existing:
                    continue
                
                assessment = UserAssessment(
                    user_id=user.id,
                    assessment_type="initial" if i == 0 else "progress_check",
                    total_questions=15,
                    correct_answers=random.randint(5, 15),
                    accuracy_percentage=random.uniform(30, 95),
                    calculated_level=random.randint(1, 8),
                    skill_level=random.choice([
                        SkillLevel.COMPLETE_BEGINNER,
                        SkillLevel.BEGINNER, 
                        SkillLevel.INTERMEDIATE,
                        SkillLevel.ADVANCED,
                        SkillLevel.EXPERT
                    ]),
                    time_taken_minutes=random.uniform(10, 30),
                    is_completed=True,
                    completed_at=datetime.now() - timedelta(days=random.randint(0, 20)),
                    started_at=datetime.now() - timedelta(days=random.randint(0, 20))
                )
                db.add(assessment)
                assessments_created += 1
    
    db.commit()
    print(f"✅ Created {assessments_created} assessment records")

def create_admin_user(db):
    """Ensure an admin user exists"""
    print("Checking for admin user...")
    
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if not admin:
        print("Creating admin user...")
        admin = User(
            email="admin@ailearner.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created (email: admin@ailearner.com, password: admin123)")
    else:
        print(f"✅ Admin user exists: {admin.email}")

def main():
    """Main function"""
    print("🚀 Creating sample data for admin dashboard...")
    
    db = SessionLocal()
    
    try:
        # Create admin user first
        create_admin_user(db)
        
        # Create sample data
        create_sample_users(db, count=25)
        create_sample_lesson_progress(db)
        create_sample_assessments(db)
        
        # Show summary
        total_users = db.query(User).filter(User.role == UserRole.USER).count()
        total_progress = db.query(UserLessonProgress).count()
        total_assessments = db.query(UserAssessment).count()
        
        print("\n" + "="*50)
        print("📊 SAMPLE DATA SUMMARY")
        print("="*50)
        print(f"👥 Total Users: {total_users}")
        print(f"📚 Lesson Progress Records: {total_progress}")
        print(f"📝 Assessment Records: {total_assessments}")
        print(f"🔑 Admin User: admin@ailearner.com (password: admin123)")
        print("="*50)
        print("✅ Sample data creation completed!")
        print("🌐 You can now view the admin dashboard with populated data")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    exit(main())