#!/usr/bin/env python3

"""
Initialize subscription plans in the database
Run this script to set up the Free, Gold, and Premium subscription tiers
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.subscription import SubscriptionPlan, SubscriptionTier

def create_subscription_plans():
    """Create default subscription plans"""
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing_plans = db.query(SubscriptionPlan).count()
        if existing_plans > 0:
            print("Subscription plans already exist. Skipping creation.")
            return
        
        # Free Plan
        free_plan = SubscriptionPlan(
            tier=SubscriptionTier.FREE,
            name="Free",
            price=0.0,
            currency="BDT",
            duration_days=365,  # Free forever (1 year cycles)
            daily_question_limit=5,
            max_level_access=3,
            ai_questions_enabled=False,
            detailed_analytics=False,
            priority_support=False,
            unlimited_retakes=False,
            personalized_tutor=False,
            custom_learning_paths=False,
            description="Perfect for getting started with C programming. Access to first 3 levels with basic features."
        )
        
        # Gold Plan  
        gold_plan = SubscriptionPlan(
            tier=SubscriptionTier.GOLD,
            name="Gold",
            price=500.0,
            currency="BDT", 
            duration_days=30,  # Monthly subscription
            daily_question_limit=25,
            max_level_access=None,  # Unlimited levels
            ai_questions_enabled=False,  # Not implemented yet
            detailed_analytics=False,    # Not implemented yet
            priority_support=False,      # Not implemented yet
            unlimited_retakes=False,     # Not implemented yet
            personalized_tutor=False,    # Not implemented yet
            custom_learning_paths=False, # Not implemented yet
            description="For serious learners. Access to all 10 levels and more practice questions daily."
        )
        
        # Premium Plan
        premium_plan = SubscriptionPlan(
            tier=SubscriptionTier.PREMIUM,
            name="Premium",
            price=1000.0,
            currency="BDT",
            duration_days=30,  # Monthly subscription
            daily_question_limit=None,  # Unlimited questions
            max_level_access=None,  # Unlimited levels
            ai_questions_enabled=False,  # Not implemented yet
            detailed_analytics=False,    # Not implemented yet
            priority_support=False,      # Not implemented yet
            unlimited_retakes=False,     # Not implemented yet
            personalized_tutor=False,    # Not implemented yet
            custom_learning_paths=False, # Not implemented yet
            description="Complete access to all levels with unlimited daily practice questions."
        )
        
        # Add all plans to database
        db.add(free_plan)
        db.add(gold_plan)
        db.add(premium_plan)
        db.commit()
        
        print("✅ Successfully created subscription plans:")
        print(f"   - Free: ৳0 (5 questions/day, levels 1-3)")
        print(f"   - Gold: ৳500/month (25 questions/day, all levels)")
        print(f"   - Premium: ৳1000/month (unlimited questions, all levels)")
        
    except Exception as e:
        print(f"❌ Error creating subscription plans: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def assign_free_subscriptions_to_existing_users():
    """Assign free subscriptions to all existing users who don't have one"""
    from app.models.user import User
    from app.models.subscription import Subscription
    from datetime import datetime
    
    db = SessionLocal()
    
    try:
        # Get all users without active subscriptions
        users_without_subscription = db.query(User).outerjoin(Subscription).filter(
            Subscription.id.is_(None)
        ).all()
        
        print(f"Found {len(users_without_subscription)} users without subscriptions")
        
        for user in users_without_subscription:
            subscription = Subscription(
                user_id=user.id,
                tier=SubscriptionTier.FREE,
                start_date=datetime.utcnow(),
                end_date=None,  # Free tier doesn't expire
                is_active=True,
                auto_renew=False
            )
            db.add(subscription)
            
        db.commit()
        print(f"✅ Assigned free subscriptions to {len(users_without_subscription)} existing users")
        
    except Exception as e:
        print(f"❌ Error assigning free subscriptions: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing subscription plans...")
    
    # Create subscription plans
    create_subscription_plans()
    
    # Assign free subscriptions to existing users
    assign_free_subscriptions_to_existing_users()
    
    print("✅ Subscription system setup complete!")
    print("\nNext steps:")
    print("1. Update your .env file with SSLCommerz credentials:")
    print("   SSLCOMMERZ_STORE_ID=your_store_id")
    print("   SSLCOMMERZ_STORE_PASS=your_store_pass")  
    print("   SSLCOMMERZ_SANDBOX=true  # Set to false for production")
    print("\n2. Install required packages:")
    print("   pip install -r requirements.txt")
    print("\n3. Run database migrations if using Alembic:")
    print("   alembic upgrade head")
    print("\n4. Test the payment integration in sandbox mode first")