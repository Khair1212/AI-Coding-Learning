#!/usr/bin/env python3
"""
Debug script to understand assessment calculation issues
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import User, UserAssessment, AssessmentResponse, AssessmentQuestion
from app.services.adaptive_service import AdaptiveLearningService
from sqlalchemy import desc

def debug_latest_assessment():
    """Debug the latest assessment calculation"""
    print("🔍 Debugging latest assessment calculation...")
    
    db = SessionLocal()
    try:
        # Get the most recent completed assessment
        latest_assessment = db.query(UserAssessment).filter(
            UserAssessment.is_completed == True
        ).order_by(desc(UserAssessment.completed_at)).first()
        
        if not latest_assessment:
            print("❌ No completed assessments found")
            return
        
        print(f"📋 Assessment Details:")
        print(f"   ID: {latest_assessment.id}")
        print(f"   User ID: {latest_assessment.user_id}")
        print(f"   Accuracy: {latest_assessment.accuracy_percentage}%")
        print(f"   Calculated Level: {latest_assessment.calculated_level}")
        print(f"   Skill Level: {latest_assessment.skill_level}")
        
        # Get assessment responses
        responses = db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == latest_assessment.id
        ).all()
        
        print(f"\n📊 Response Analysis ({len(responses)} total):")
        topic_breakdown = {}
        correct_count = 0
        
        for response in responses:
            question = response.question
            if question:
                topic = question.topic_area
                level = question.expected_level
                
                if topic not in topic_breakdown:
                    topic_breakdown[topic] = {'correct': 0, 'total': 0}
                
                topic_breakdown[topic]['total'] += 1
                if response.is_correct:
                    topic_breakdown[topic]['correct'] += 1
                    correct_count += 1
                
                print(f"   Q{response.id}: {topic} (L{level}) - {'✅' if response.is_correct else '❌'}")
        
        print(f"\n📈 Topic Breakdown:")
        for topic, data in topic_breakdown.items():
            accuracy = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
            print(f"   {topic}: {data['correct']}/{data['total']} ({accuracy:.0f}%)")
        
        calculated_accuracy = (correct_count / len(responses)) * 100 if responses else 0
        print(f"\n🧮 Calculated Accuracy: {correct_count}/{len(responses)} = {calculated_accuracy:.1f}%")
        print(f"🗂️ Stored Accuracy: {latest_assessment.accuracy_percentage}%")
        
        # Now run the adaptive service calculation
        print(f"\n🤖 Running Adaptive Service Calculation...")
        service = AdaptiveLearningService(db)
        calculated_level, skill_level = service.calculate_skill_level(latest_assessment)
        
        print(f"\n🎯 Results:")
        print(f"   Calculated Level: {calculated_level}")
        print(f"   Skill Level: {skill_level}")
        
        # Check if the calculation matches what's stored
        if calculated_level != latest_assessment.calculated_level:
            print(f"⚠️ MISMATCH: Stored level ({latest_assessment.calculated_level}) differs from calculated ({calculated_level})")
        
        if skill_level != latest_assessment.skill_level:
            print(f"⚠️ MISMATCH: Stored skill level ({latest_assessment.skill_level}) differs from calculated ({skill_level})")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_latest_assessment()