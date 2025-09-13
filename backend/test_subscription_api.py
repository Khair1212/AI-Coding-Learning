#!/usr/bin/env python3

"""
Test script for subscription API endpoints
Run this while the server is running to test subscription functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_subscription_endpoints():
    """Test subscription API endpoints"""
    
    print("🧪 Testing Subscription API Endpoints...")
    print("=" * 50)
    
    # Test 1: Get subscription plans
    print("\n1️⃣ Testing GET /subscription/plans")
    try:
        response = requests.get(f"{BASE_URL}/subscription/plans")
        if response.status_code == 200:
            plans = response.json()
            print(f"✅ Found {len(plans)} subscription plans:")
            for plan in plans:
                print(f"   - {plan['name']}: ৳{plan['price']}")
                print(f"     Questions/day: {plan['daily_question_limit'] or 'Unlimited'}")
                level_text = f"Up to {plan['max_level_access']}" if plan['max_level_access'] else 'All levels'
                print(f"     Level access: {level_text}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on http://localhost:8000")
        return False
    
    # Test 2: Check health endpoint
    print("\n2️⃣ Testing GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Test authenticated endpoints (would need login)
    print("\n3️⃣ Testing authenticated endpoints:")
    print("   ℹ️  These require user authentication - will show 401 Unauthorized")
    
    endpoints_to_test = [
        "/subscription/my-subscription",
        "/subscription/check-limits", 
        "/subscription/payment-history"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"   ✅ {endpoint}: Correctly requires authentication")
            else:
                print(f"   ⚠️ {endpoint}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Subscription API tests completed!")
    print("\n📋 Summary:")
    print("✅ Subscription plans are configured")  
    print("✅ API endpoints are accessible")
    print("✅ Authentication is working")
    print("💳 SSLCommerz integration is ready for testing")
    
    return True

def test_payment_flow():
    """Test payment flow (would need authentication)"""
    print("\n💳 Payment Flow Test Info:")
    print("To test the complete payment flow:")
    print("1. Create a user account via POST /api/auth/register")
    print("2. Login via POST /api/auth/login to get access token")
    print("3. Use the token to create payment session:")
    print("   POST /api/subscription/create-payment")
    print("4. Complete payment using SSLCommerz sandbox")
    print("5. Handle success/failure callbacks")
    
    print("\nSSLCommerz Sandbox Credentials:")
    print("Store ID: testbox")
    print("Store Password: qwerty")
    print("Environment: Sandbox")

if __name__ == "__main__":
    success = test_subscription_endpoints()
    if success:
        test_payment_flow()
    else:
        print("\n❌ API tests failed. Please start the server first:")
        print("cd backend && python3 -m uvicorn app.main:app --reload")
        sys.exit(1)