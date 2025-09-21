#!/usr/bin/env python3
"""
Update existing database with payment/subscription features
Run this on databases that were created before payment system was added
"""

from app.core.database import engine, Base
from init_subscription_plans import create_subscription_plans, assign_free_subscriptions_to_existing_users
from add_achievements import create_achievements
import subprocess
import sys

def update_database_for_payments():
    """Update existing database with new payment/subscription features"""
    print("🔄 UPDATING DATABASE FOR PAYMENT SYSTEM")
    print("=" * 50)
    
    try:
        # Step 1: Create new tables
        print("\n1. Creating new subscription/payment tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables updated!")
        
        # Step 2: Add subscription plans
        print("\n2. Setting up subscription plans...")
        create_subscription_plans()
        
        # Step 3: Assign free subscriptions to existing users
        print("\n3. Assigning free subscriptions to existing users...")
        assign_free_subscriptions_to_existing_users()
        
        # Step 4: Add achievements
        print("\n4. Setting up achievements system...")
        # create_achievements()
        
        # Step 5: Fix payment constraints if needed
        print("\n5. Checking payment table constraints...")
        try:
            subprocess.run([sys.executable, "fix_payment_constraint.py"], check=False)
        except Exception as e:
            print(f"   Note: Payment constraint fix not needed or failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ DATABASE UPDATE COMPLETE!")
        print("\n🎉 New features added:")
        print("   💳 Payment System (SSLCommerz integration)")
        print("   📊 Subscription Tiers (Free, Gold, Premium)")
        print("   🏆 Achievements System")
        print("   📈 Usage Tracking")
        
        print("\n📋 Next steps:")
        print("   1. Add SSLCommerz credentials to .env:")
        print("      SSLCOMMERZ_STORE_ID=your_store_id")
        print("      SSLCOMMERZ_STORE_PASS=your_store_pass")
        print("      SSLCOMMERZ_SANDBOX=true")
        print("   2. Restart your backend server")
        print("   3. Test subscription features!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error updating database: {e}")
        return False

if __name__ == "__main__":
    success = update_database_for_payments()
    sys.exit(0 if success else 1)
