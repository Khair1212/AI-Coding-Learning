#!/usr/bin/env python3
"""
Fix all stored assessments with incorrect calculated levels and skill levels
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import UserAssessment
from app.services.adaptive_service import AdaptiveLearningService

def fix_all_assessments():
    """Recalculate and fix all completed assessments"""
    print("🔧 Fixing all stored assessments...")
    
    db = SessionLocal()
    try:
        # Get all completed assessments
        assessments = db.query(UserAssessment).filter(
            UserAssessment.is_completed == True
        ).all()
        
        if not assessments:
            print("❌ No completed assessments found")
            return
        
        print(f"📋 Found {len(assessments)} completed assessments to fix")
        
        service = AdaptiveLearningService(db)
        fixed_count = 0
        
        for assessment in assessments:
            print(f"\n🔍 Processing Assessment {assessment.id} (User {assessment.user_id})")
            print(f"   Current: Level {assessment.calculated_level}, {assessment.skill_level}")
            
            # Recalculate with new logic
            new_level, new_skill = service.calculate_skill_level(assessment)
            
            # Check if update is needed
            if assessment.calculated_level != new_level or assessment.skill_level != new_skill:
                print(f"   ✏️ Updating: Level {assessment.calculated_level} → {new_level}")
                print(f"              Skill {assessment.skill_level} → {new_skill}")
                
                # Update the assessment
                assessment.calculated_level = new_level
                assessment.skill_level = new_skill
                fixed_count += 1
            else:
                print(f"   ✅ Already correct")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Successfully fixed {fixed_count} assessments!")
        
    except Exception as e:
        print(f"❌ Error fixing assessments: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_assessments()