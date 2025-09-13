from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime

class SubscriptionTier(enum.Enum):
    FREE = "free"
    GOLD = "gold" 
    PREMIUM = "premium"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier = Column(Enum(SubscriptionTier), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # SSLCommerz specific fields
    transaction_id = Column(String, unique=True, nullable=False)
    session_key = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="BDT")
    
    # Payment status and details
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String, nullable=True)
    bank_transaction_id = Column(String, nullable=True)
    card_type = Column(String, nullable=True)
    card_no = Column(String, nullable=True)
    card_issuer = Column(String, nullable=True)
    card_brand = Column(String, nullable=True)
    card_issuer_country = Column(String, nullable=True)
    card_issuer_country_code = Column(String, nullable=True)
    
    # SSLCommerz response data
    val_id = Column(String, nullable=True)  # Validation ID from SSLCommerz
    store_amount = Column(Numeric(10, 2), nullable=True)
    risk_level = Column(String, nullable=True)
    risk_title = Column(String, nullable=True)
    
    # Timestamps
    payment_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    subscription = relationship("Subscription", back_populates="payments")
    user = relationship("User", back_populates="payments")

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    tier = Column(Enum(SubscriptionTier), unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="BDT")
    duration_days = Column(Integer, nullable=False)  # 30 for monthly
    
    # Feature limits
    daily_question_limit = Column(Integer, nullable=True)  # null means unlimited
    max_level_access = Column(Integer, nullable=True)  # null means all levels
    ai_questions_enabled = Column(Boolean, default=False)
    detailed_analytics = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    unlimited_retakes = Column(Boolean, default=False)
    personalized_tutor = Column(Boolean, default=False)
    custom_learning_paths = Column(Boolean, default=False)
    
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserUsage(Base):
    __tablename__ = "user_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    questions_attempted = Column(Integer, default=0)
    ai_questions_used = Column(Integer, default=0)
    assessments_taken = Column(Integer, default=0)
    
    user = relationship("User", back_populates="usage_records")
    
