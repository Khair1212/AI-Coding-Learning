#!/usr/bin/env python3
"""
Direct test of admin stats endpoint
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.admin import get_admin_stats
from app.api.deps import get_current_admin_user
from app.core.database import SessionLocal, get_db
from app.models import User, UserRole

def test_stats_directly():
    """Test the stats function directly"""
    print("🧪 Testing stats endpoint directly...")
    
    db = SessionLocal()
    
    try:
        # Get admin user
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            print("❌ No admin user found")
            return False
        
        print(f"✅ Found admin: {admin.email}")
        
        # Call the stats function directly
        print("📊 Calling get_admin_stats...")
        stats = get_admin_stats(admin=admin, db=db)
        
        print("✅ Stats retrieved successfully:")
        print(f"   Total Users: {stats.total_users}")
        print(f"   Active Users: {stats.active_users}")
        print(f"   Lessons Completed: {stats.total_lessons_completed}")
        print(f"   Assessments: {stats.total_assessments}")
        print(f"   Average Accuracy: {stats.average_accuracy}%")
        print(f"   Popular Levels: {len(stats.popular_levels)}")
        print(f"   Recent Registrations: {len(stats.recent_registrations)}")
        
        if len(stats.popular_levels) > 0:
            print("   Top levels:")
            for level in stats.popular_levels:
                print(f"     - Level {level['level']}: {level['title']} ({level['completions']} completions)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing stats: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_stats_directly()