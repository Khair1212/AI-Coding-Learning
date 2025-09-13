from sslcommerz_lib import SSLCOMMERZ
from sqlalchemy.orm import Session
from app.models.subscription import Payment, PaymentStatus, Subscription, SubscriptionTier
from app.models.user import User
from app.core.database import SessionLocal
from datetime import datetime, timedelta
import uuid
import logging
import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PaymentRequest(BaseModel):
    user_id: int
    subscription_tier: SubscriptionTier
    success_url: str
    fail_url: str
    cancel_url: str

class SSLCommerzConfig:
    def __init__(self, store_id: str, store_pass: str, is_sandbox: bool = True):
        self.store_id = store_id
        self.store_pass = store_pass
        self.is_sandbox = is_sandbox
        
        self.settings = {
            'store_id': store_id,
            'store_pass': store_pass,
            'issandbox': is_sandbox
        }

class PaymentService:
    def __init__(self, config: SSLCommerzConfig):
        self.config = config
        self.sslcommerz = SSLCOMMERZ(config.settings)
        
    def get_subscription_price(self, tier: SubscriptionTier) -> float:
        prices = {
            SubscriptionTier.FREE: 0.0,
            SubscriptionTier.GOLD: 500.0,
            SubscriptionTier.PREMIUM: 1000.0
        }
        return prices.get(tier, 0.0)
    
    def create_payment_session(self, payment_request: PaymentRequest, db: Session) -> Dict[str, Any]:
        try:
            # Get user details
            user = db.query(User).filter(User.id == payment_request.user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Generate unique transaction ID
            transaction_id = f"TXN_{user.id}_{int(datetime.utcnow().timestamp())}"
            
            # Get subscription price
            amount = self.get_subscription_price(payment_request.subscription_tier)
            
            if amount == 0:
                # Free tier - no payment needed
                return self._create_free_subscription(user.id, db)
            
            # Create payment record
            payment = Payment(
                user_id=user.id,
                subscription_id=None,  # Will be set after subscription creation
                transaction_id=transaction_id,
                amount=amount,
                currency="BDT",
                status=PaymentStatus.PENDING
            )
            db.add(payment)
            db.commit()
            
            # Prepare SSLCommerz payment data
            post_body = {
                'total_amount': amount,
                'currency': "BDT",
                'tran_id': transaction_id,
                'success_url': payment_request.success_url,
                'fail_url': payment_request.fail_url,
                'cancel_url': payment_request.cancel_url,
                'emi_option': 0,
                'cus_name': user.username,
                'cus_email': user.email,
                'cus_phone': "01700000000",  # Default phone - should be collected from user
                'cus_add1': "Dhaka, Bangladesh",
                'cus_city': "Dhaka",
                'cus_country': "Bangladesh",
                'shipping_method': "NO",
                'multi_card_name': "",
                'num_of_item': 1,
                'product_name': f"{payment_request.subscription_tier.value.title()} Subscription",
                'product_category': "Subscription",
                'product_profile': "general"
            }
            
            # Create SSLCommerz session
            response = self.sslcommerz.createSession(post_body)
            
            if response['status'] == 'SUCCESS':
                # Update payment with session key
                payment.session_key = response['sessionkey']
                db.commit()
                
                return {
                    'status': 'success',
                    'payment_url': response['GatewayPageURL'],
                    'session_key': response['sessionkey'],
                    'transaction_id': transaction_id
                }
            else:
                logger.error(f"SSLCommerz session creation failed: {response}")
                payment.status = PaymentStatus.FAILED
                db.commit()
                return {
                    'status': 'error',
                    'message': 'Payment session creation failed'
                }
                
        except Exception as e:
            logger.error(f"Payment session creation error: {str(e)}")
            db.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _create_free_subscription(self, user_id: int, db: Session) -> Dict[str, Any]:
        try:
            # Check if user already has active subscription
            existing_sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).first()
            
            if existing_sub:
                return {
                    'status': 'success',
                    'message': 'User already has active subscription'
                }
            
            # Create free subscription
            subscription = Subscription(
                user_id=user_id,
                tier=SubscriptionTier.FREE,
                start_date=datetime.utcnow(),
                end_date=None,  # Free tier doesn't expire
                is_active=True,
                auto_renew=False
            )
            db.add(subscription)
            db.commit()
            
            return {
                'status': 'success',
                'message': 'Free subscription activated'
            }
            
        except Exception as e:
            logger.error(f"Free subscription creation error: {str(e)}")
            db.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def handle_payment_success(self, transaction_id: str, val_id: str, db: Session) -> Dict[str, Any]:
        try:
            # Verify payment with SSLCommerz
            verification_response = self.verify_payment(val_id, transaction_id)
            
            if not verification_response.get('verified', False):
                logger.error(f"Payment verification failed for transaction: {transaction_id}")
                return {'status': 'error', 'message': 'Payment verification failed'}
            
            # Get payment record
            payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
            if not payment:
                logger.error(f"Payment record not found for transaction: {transaction_id}")
                return {'status': 'error', 'message': 'Payment record not found'}
            
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            payment.val_id = val_id
            payment.payment_date = datetime.utcnow()
            
            # Update payment with SSLCommerz response data
            ssl_data = verification_response.get('data', {})
            payment.bank_transaction_id = ssl_data.get('bank_tran_id')
            payment.card_type = ssl_data.get('card_type')
            payment.card_no = ssl_data.get('card_no')
            payment.card_issuer = ssl_data.get('card_issuer')
            payment.card_brand = ssl_data.get('card_brand')
            payment.store_amount = ssl_data.get('store_amount')
            payment.risk_level = ssl_data.get('risk_level')
            payment.risk_title = ssl_data.get('risk_title')
            
            # Create or update subscription
            self._create_paid_subscription(payment, db)
            
            db.commit()
            
            return {
                'status': 'success',
                'message': 'Payment processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Payment success handling error: {str(e)}")
            db.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _create_paid_subscription(self, payment: Payment, db: Session):
        try:
            # Determine subscription tier based on amount
            tier = SubscriptionTier.GOLD if payment.amount == 500 else SubscriptionTier.PREMIUM
            
            # Deactivate existing subscriptions
            existing_subs = db.query(Subscription).filter(
                Subscription.user_id == payment.user_id,
                Subscription.is_active == True
            ).all()
            
            for sub in existing_subs:
                sub.is_active = False
                sub.end_date = datetime.utcnow()
            
            # Create new subscription
            subscription = Subscription(
                user_id=payment.user_id,
                tier=tier,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),  # 30 days subscription
                is_active=True,
                auto_renew=True
            )
            db.add(subscription)
            db.flush()
            
            # Update payment with subscription ID
            payment.subscription_id = subscription.id
            
        except Exception as e:
            logger.error(f"Subscription creation error: {str(e)}")
            raise e
    
    def handle_payment_failure(self, transaction_id: str, db: Session) -> Dict[str, Any]:
        try:
            payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
            if payment:
                payment.status = PaymentStatus.FAILED
                db.commit()
            
            return {
                'status': 'success',
                'message': 'Payment failure recorded'
            }
            
        except Exception as e:
            logger.error(f"Payment failure handling error: {str(e)}")
            db.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def handle_payment_cancellation(self, transaction_id: str, db: Session) -> Dict[str, Any]:
        try:
            payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
            if payment:
                payment.status = PaymentStatus.CANCELLED
                db.commit()
            
            return {
                'status': 'success',
                'message': 'Payment cancellation recorded'
            }
            
        except Exception as e:
            logger.error(f"Payment cancellation handling error: {str(e)}")
            db.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def verify_payment(self, val_id: str, transaction_id: str) -> Dict[str, Any]:
        try:
            # SSLCommerz validation endpoint
            validation_url = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php" if self.config.is_sandbox else "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
            
            payload = {
                'val_id': val_id,
                'store_id': self.config.store_id,
                'store_passwd': self.config.store_pass,
                'format': 'json'
            }
            
            response = requests.get(validation_url, params=payload)
            data = response.json()
            
            if data.get('status') == 'VALID' and data.get('tran_id') == transaction_id:
                return {
                    'verified': True,
                    'data': data
                }
            else:
                return {
                    'verified': False,
                    'error': 'Invalid payment'
                }
                
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    def get_user_subscription(self, user_id: int, db: Session) -> Optional[Subscription]:
        return db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()
    
    def check_subscription_validity(self, subscription: Subscription) -> bool:
        if not subscription or not subscription.is_active:
            return False
            
        if subscription.tier == SubscriptionTier.FREE:
            return True
            
        if subscription.end_date and subscription.end_date.replace(tzinfo=None) < datetime.utcnow():
            return False
            
        return True