#!/usr/bin/env python3
"""
Test script to verify admin API endpoints work correctly
"""

import sys
import os
import requests
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.security import create_access_token
from app.models import User, UserRole
from app.core.database import SessionLocal

def get_admin_token():
    """Get a valid admin token"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            print("❌ No admin user found")
            return None
        
        print(f"✅ Found admin user: {admin.email}")
        token = create_access_token(data={"sub": admin.email})
        return token
    finally:
        db.close()

def test_admin_endpoints():
    """Test admin API endpoints"""
    print("🧪 Testing admin API endpoints...")
    
    # Get admin token
    token = get_admin_token()
    if not token:
        return False
    
    base_url = "http://localhost:8000/api/admin"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints
    endpoints = [
        "/stats",
        "/users",
        "/achievements",
        "/levels-lessons"
    ]
    
    all_success = True
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {endpoint}")
                
                if endpoint == "/stats":
                    print(f"   📊 Stats: {json.dumps(data, indent=2)}")
                elif endpoint == "/users":
                    print(f"   👥 Users count: {len(data)}")
                elif endpoint == "/achievements":
                    print(f"   🏆 Achievements count: {len(data)}")
                elif endpoint == "/levels-lessons":
                    print(f"   📚 Levels count: {len(data)}")
                    
            else:
                print(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                print(f"   Response: {response.text}")
                all_success = False
                
        except Exception as e:
            print(f"❌ Exception for {endpoint}: {e}")
            all_success = False
    
    return all_success

def main():
    """Main function"""
    print("🚀 Testing admin API connectivity...")
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server returned error:", response.status_code)
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("💡 Make sure to run: uvicorn app.main:app --reload")
        return 1
    
    # Test admin endpoints
    if test_admin_endpoints():
        print("\n🎉 All admin API endpoints working correctly!")
        return 0
    else:
        print("\n❌ Some admin API endpoints failed")
        return 1

if __name__ == "__main__":
    exit(main())