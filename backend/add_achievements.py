#!/usr/bin/env python3
"""
Script to add sample achievements to the database
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import Achievement

def create_achievements(db):
    """Create sample achievements"""
    print("Creating sample achievements...")
    
    achievements_data = [
        {
            "name": "First Steps",
            "description": "Complete your first lesson",
            "requirement_type": "lessons_completed",
            "requirement_value": 1,
            "xp_reward": 50
        },
        {
            "name": "Getting Started",
            "description": "Complete 5 lessons",
            "requirement_type": "lessons_completed", 
            "requirement_value": 5,
            "xp_reward": 100
        },
        {
            "name": "Dedicated Learner",
            "description": "Complete 10 lessons",
            "requirement_type": "lessons_completed",
            "requirement_value": 10,
            "xp_reward": 200
        },
        {
            "name": "Assessment Master",
            "description": "Complete your first assessment",
            "requirement_type": "assessments_completed",
            "requirement_value": 1,
            "xp_reward": 75
        },
        {
            "name": "High Achiever",
            "description": "Score 90% or higher on an assessment", 
            "requirement_type": "assessment_accuracy",
            "requirement_value": 90,
            "xp_reward": 150
        },
        {
            "name": "Streak Starter",
            "description": "Maintain a 3-day learning streak",
            "requirement_type": "streak_days",
            "requirement_value": 3,
            "xp_reward": 100
        },
        {
            "name": "Consistency Champion",
            "description": "Maintain a 7-day learning streak",
            "requirement_type": "streak_days", 
            "requirement_value": 7,
            "xp_reward": 250
        },
        {
            "name": "XP Collector",
            "description": "Earn 500 XP",
            "requirement_type": "total_xp",
            "requirement_value": 500,
            "xp_reward": 100
        },
        {
            "name": "Knowledge Seeker",
            "description": "Earn 1000 XP",
            "requirement_type": "total_xp",
            "requirement_value": 1000,
            "xp_reward": 200
        },
        {
            "name": "Perfect Score",
            "description": "Get 100% accuracy on an assessment",
            "requirement_type": "perfect_assessment",
            "requirement_value": 1,
            "xp_reward": 300
        }
    ]
    
    achievements_created = 0
    
    for ach_data in achievements_data:
        # Check if achievement already exists
        existing = db.query(Achievement).filter(
            Achievement.name == ach_data["name"]
        ).first()
        
        if existing:
            print(f"Achievement '{ach_data['name']}' already exists")
            continue
        
        achievement = Achievement(**ach_data, is_active=True)
        db.add(achievement)
        achievements_created += 1
        print(f"✅ Created: {ach_data['name']}")
    
    db.commit()
    return achievements_created

def main():
    """Main function"""
    print("🏆 Adding sample achievements...")
    
    db = SessionLocal()
    
    try:
        achievements_created = create_achievements(db)
        
        # Show summary
        total_achievements = db.query(Achievement).count()
        
        print("\n" + "="*50)
        print("🏆 ACHIEVEMENTS SUMMARY")
        print("="*50)
        print(f"✅ New achievements created: {achievements_created}")
        print(f"📊 Total achievements: {total_achievements}")
        print("="*50)
        print("✅ Achievement setup completed!")
        
    except Exception as e:
        print(f"❌ Error creating achievements: {e}")
        db.rollback()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    exit(main())