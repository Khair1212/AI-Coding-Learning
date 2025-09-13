from sqlalchemy.orm import Session
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionPlan, UserUsage
from app.models.lesson import Level
from datetime import datetime, date
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    
    @staticmethod
    def can_access_level(user_id: int, level_number: int, db: Session) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            # No subscription - only allow first 3 levels for free
            return level_number <= 3
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription.tier
        ).first()
        
        if not plan:
            return level_number <= 3
        
        if plan.max_level_access is None:
            return True  # Unlimited access
        
        return level_number <= plan.max_level_access
    
    @staticmethod
    def can_attempt_question(user_id: int, db: Session) -> Dict[str, Any]:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            subscription_tier = SubscriptionTier.FREE
        else:
            subscription_tier = subscription.tier
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription_tier
        ).first()
        
        if not plan or plan.daily_question_limit is None:
            return {'allowed': True, 'remaining': None}
        
        # Get today's usage
        today = date.today()
        usage = db.query(UserUsage).filter(
            UserUsage.user_id == user_id,
            UserUsage.date >= datetime.combine(today, datetime.min.time()),
            UserUsage.date < datetime.combine(today, datetime.max.time())
        ).first()
        
        questions_used = usage.questions_attempted if usage else 0
        remaining = max(0, plan.daily_question_limit - questions_used)
        
        return {
            'allowed': remaining > 0,
            'remaining': remaining,
            'limit': plan.daily_question_limit,
            'used': questions_used
        }
    
    @staticmethod
    def can_use_ai_questions(user_id: int, db: Session) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            return False  # Free tier doesn't have AI questions
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription.tier
        ).first()
        
        return plan.ai_questions_enabled if plan else False
    
    @staticmethod
    def can_retake_assessment(user_id: int, db: Session) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            return False  # Free tier has limited retakes
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription.tier
        ).first()
        
        return plan.unlimited_retakes if plan else False
    
    @staticmethod
    def has_detailed_analytics(user_id: int, db: Session) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            return False
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription.tier
        ).first()
        
        return plan.detailed_analytics if plan else False
    
    @staticmethod
    def has_priority_support(user_id: int, db: Session) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            return False
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription.tier
        ).first()
        
        return plan.priority_support if plan else False
    
    @staticmethod
    def has_personalized_tutor(user_id: int, db: Session) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            return False
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription.tier
        ).first()
        
        return plan.personalized_tutor if plan else False
    
    @staticmethod
    def record_usage(user_id: int, activity_type: str, db: Session):
        """Record user activity for daily limits tracking"""
        today = date.today()
        
        # Get or create today's usage record
        usage = db.query(UserUsage).filter(
            UserUsage.user_id == user_id,
            UserUsage.date >= datetime.combine(today, datetime.min.time()),
            UserUsage.date < datetime.combine(today, datetime.max.time())
        ).first()
        
        if not usage:
            usage = UserUsage(
                user_id=user_id,
                date=datetime.combine(today, datetime.min.time()),
                questions_attempted=0,
                ai_questions_used=0,
                assessments_taken=0
            )
            db.add(usage)
        
        # Update based on activity type
        if activity_type == 'question':
            usage.questions_attempted += 1
        elif activity_type == 'ai_question':
            usage.ai_questions_used += 1
        elif activity_type == 'assessment':
            usage.assessments_taken += 1
        
        db.commit()
    
    @staticmethod
    def get_subscription_features(user_id: int, db: Session) -> Dict[str, Any]:
        """Get all subscription features for a user"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.tier
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()
        
        if not plan:
            # Default free tier features
            return {
                'tier': 'free',
                'daily_question_limit': 5,
                'max_level_access': 3,
                'ai_questions_enabled': False,
                'detailed_analytics': False,
                'priority_support': False,
                'unlimited_retakes': False,
                'personalized_tutor': False,
                'custom_learning_paths': False
            }
        
        return {
            'tier': tier.value,
            'daily_question_limit': plan.daily_question_limit,
            'max_level_access': plan.max_level_access,
            'ai_questions_enabled': plan.ai_questions_enabled,
            'detailed_analytics': plan.detailed_analytics,
            'priority_support': plan.priority_support,
            'unlimited_retakes': plan.unlimited_retakes,
            'personalized_tutor': plan.personalized_tutor,
            'custom_learning_paths': plan.custom_learning_paths
        }
    
    @staticmethod
    def get_upgrade_suggestions(user_id: int, db: Session) -> Dict[str, Any]:
        """Get upgrade suggestions based on user usage patterns"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
        
        current_tier = subscription.tier if subscription else SubscriptionTier.FREE
        
        # Get recent usage patterns
        recent_usage = db.query(UserUsage).filter(
            UserUsage.user_id == user_id
        ).order_by(UserUsage.date.desc()).limit(7).all()
        
        suggestions = []
        
        if current_tier == SubscriptionTier.FREE:
            avg_questions = sum(u.questions_attempted for u in recent_usage) / max(len(recent_usage), 1)
            
            if avg_questions > 3:
                suggestions.append({
                    'tier': 'gold',
                    'reason': 'You\'re approaching the daily question limit. Upgrade to Gold for 25 questions per day.',
                    'benefit': '5x more questions daily'
                })
            
            # Check level access
            user_progress = db.query(Level).join(
                # This would need proper progress tracking
            ).filter().count()
            
            suggestions.append({
                'tier': 'gold',
                'reason': 'Unlock all 10 C programming levels and AI-generated questions.',
                'benefit': 'Complete curriculum access + AI tutor'
            })
        
        elif current_tier == SubscriptionTier.GOLD:
            avg_questions = sum(u.questions_attempted for u in recent_usage) / max(len(recent_usage), 1)
            
            if avg_questions > 15:
                suggestions.append({
                    'tier': 'premium',
                    'reason': 'You\'re a power learner! Get unlimited questions and personalized AI tutor.',
                    'benefit': 'Unlimited access + Advanced AI features'
                })
        
        return {
            'current_tier': current_tier.value,
            'suggestions': suggestions
        }