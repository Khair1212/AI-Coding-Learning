from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, Payment, SubscriptionTier, SubscriptionPlan, UserUsage
from app.services.payment_service import PaymentService, PaymentRequest, SSLCommerzConfig
from app.core.config import get_settings
from pydantic import BaseModel

settings = get_settings()
router = APIRouter()

# Initialize Payment Service
ssl_config = SSLCommerzConfig(
    store_id=settings.sslcommerz_store_id,
    store_pass=settings.sslcommerz_store_pass,
    is_sandbox=settings.sslcommerz_sandbox
)
payment_service = PaymentService(ssl_config)

class SubscriptionResponse(BaseModel):
    id: int
    tier: SubscriptionTier
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    auto_renew: bool

class SubscriptionPlanResponse(BaseModel):
    id: int
    tier: SubscriptionTier
    name: str
    price: float
    currency: str
    duration_days: int
    daily_question_limit: Optional[int]
    max_level_access: Optional[int]
    ai_questions_enabled: bool
    detailed_analytics: bool
    priority_support: bool
    unlimited_retakes: bool
    personalized_tutor: bool
    custom_learning_paths: bool
    description: Optional[str]

class CreatePaymentRequest(BaseModel):
    subscription_tier: SubscriptionTier
    success_url: str
    fail_url: str
    cancel_url: str

class UserUsageResponse(BaseModel):
    date: datetime
    questions_attempted: int
    ai_questions_used: int
    assessments_taken: int

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(db: Session = Depends(get_db)):
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return plans

@router.get("/my-subscription", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = payment_service.get_user_subscription(current_user.id, db)
    return subscription

@router.post("/create-payment")
async def create_payment_session(
    payment_request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = PaymentRequest(
        user_id=current_user.id,
        subscription_tier=payment_request.subscription_tier,
        success_url=payment_request.success_url,
        fail_url=payment_request.fail_url,
        cancel_url=payment_request.cancel_url
    )
    
    result = payment_service.create_payment_session(request, db)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

@router.post("/payment-success")
async def handle_payment_success(
    request: Request,
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    transaction_id = form_data.get('tran_id')
    val_id = form_data.get('val_id')
    
    if not transaction_id or not val_id:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    result = payment_service.handle_payment_success(transaction_id, val_id, db)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['message'])
    
    # Return HTML page that will communicate with parent window (modal)
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            }
            .success { 
                color: #065f46; 
                font-size: 24px; 
                margin-bottom: 20px;
            }
            .message {
                color: #047857;
                font-size: 18px;
                margin-bottom: 30px;
            }
            .loading {
                color: #059669;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="success">🎉 Payment Successful!</div>
        <div class="message">Your subscription has been upgraded successfully.</div>
        <div class="loading">Returning to your dashboard...</div>
        <script>
            // Send message to parent window
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'payment_success',
                    transaction_id: '""" + str(transaction_id) + """'
                }, '*');
            }
            // Also redirect after a delay for fallback  
            setTimeout(() => {
                window.top.location.href = 'http://localhost:3000/dashboard?payment_success=true&transaction_id=""" + str(transaction_id) + """';
            }, 3000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/payment-success")
async def handle_payment_success_get(
    request: Request,
    db: Session = Depends(get_db)
):
    # Handle GET requests as well
    transaction_id = request.query_params.get('tran_id')
    val_id = request.query_params.get('val_id')
    
    if transaction_id and val_id:
        result = payment_service.handle_payment_success(transaction_id, val_id, db)
        
        if result['status'] == 'error':
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"http://localhost:3000/subscription/failed?error={result['message']}")
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"http://localhost:3000/subscription/success?transaction_id={transaction_id}")

@router.post("/payment-failure")
async def handle_payment_failure(
    request: Request,
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    transaction_id = form_data.get('tran_id')
    
    if not transaction_id:
        raise HTTPException(status_code=400, detail="Missing transaction ID")
    
    result = payment_service.handle_payment_failure(transaction_id, db)
    
    # Return HTML page for iframe communication
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Failed</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            }
            .error { 
                color: #c53030; 
                font-size: 24px; 
                margin-bottom: 20px;
            }
            .message {
                color: #e53e3e;
                font-size: 18px;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="error">❌ Payment Failed</div>
        <div class="message">Your payment could not be processed. Please try again.</div>
        <script>
            // Send message to parent window
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'payment_failed',
                    transaction_id: '""" + str(transaction_id) + """'
                }, '*');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/payment-failure")
async def handle_payment_failure_get(
    request: Request,
    db: Session = Depends(get_db)
):
    transaction_id = request.query_params.get('tran_id')
    
    if transaction_id:
        payment_service.handle_payment_failure(transaction_id, db)
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"http://localhost:3000/subscription/failed?transaction_id={transaction_id}")

@router.post("/payment-cancel")
async def handle_payment_cancellation(
    request: Request,
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    transaction_id = form_data.get('tran_id')
    
    if not transaction_id:
        raise HTTPException(status_code=400, detail="Missing transaction ID")
    
    result = payment_service.handle_payment_cancellation(transaction_id, db)
    
    # Return HTML page for iframe communication
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            }
            .warning { 
                color: #92400e; 
                font-size: 24px; 
                margin-bottom: 20px;
            }
            .message {
                color: #b45309;
                font-size: 18px;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="warning">⚠️ Payment Cancelled</div>
        <div class="message">You cancelled the payment. You can try again anytime.</div>
        <script>
            // Send message to parent window
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'payment_cancelled',
                    transaction_id: '""" + str(transaction_id) + """'
                }, '*');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/payment-cancel")
async def handle_payment_cancellation_get(
    request: Request,
    db: Session = Depends(get_db)
):
    transaction_id = request.query_params.get('tran_id')
    
    if transaction_id:
        payment_service.handle_payment_cancellation(transaction_id, db)
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"http://localhost:3000/subscription/cancel?transaction_id={transaction_id}")

@router.get("/usage", response_model=List[UserUsageResponse])
async def get_user_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    usage_records = db.query(UserUsage).filter(
        UserUsage.user_id == current_user.id
    ).order_by(UserUsage.date.desc()).limit(days).all()
    
    return usage_records

@router.get("/check-limits")
async def check_user_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = payment_service.get_user_subscription(current_user.id, db)
    
    # If no subscription exists, create a default free subscription
    if not subscription:
        from app.models.subscription import Subscription, SubscriptionTier
        
        # Create a free subscription for the user
        free_subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE,
            start_date=datetime.utcnow(),
            end_date=None,
            is_active=True,
            auto_renew=False
        )
        db.add(free_subscription)
        db.commit()
        db.refresh(free_subscription)
        subscription = free_subscription
    
    # Get subscription plan details
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.tier == subscription.tier
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    # Get today's usage
    today = datetime.utcnow().date()
    usage = db.query(UserUsage).filter(
        UserUsage.user_id == current_user.id,
        UserUsage.date >= today
    ).first()
    
    current_usage = {
        'questions_attempted': usage.questions_attempted if usage else 0,
        'ai_questions_used': usage.ai_questions_used if usage else 0,
        'assessments_taken': usage.assessments_taken if usage else 0
    }
    
    limits = {
        'daily_question_limit': plan.daily_question_limit,
        'max_level_access': plan.max_level_access,
        'ai_questions_enabled': plan.ai_questions_enabled,
        'detailed_analytics': plan.detailed_analytics,
        'priority_support': plan.priority_support,
        'unlimited_retakes': plan.unlimited_retakes,
        'personalized_tutor': plan.personalized_tutor,
        'custom_learning_paths': plan.custom_learning_paths
    }
    
    return {
        'subscription_tier': subscription.tier,
        'current_usage': current_usage,
        'limits': limits,
        'subscription_valid': payment_service.check_subscription_validity(subscription)
    }

@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = payment_service.get_user_subscription(current_user.id, db)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    if subscription.tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=400, detail="Cannot cancel free subscription")
    
    subscription.auto_renew = False
    db.commit()
    
    return {"message": "Subscription auto-renewal cancelled"}

@router.get("/payment-history", response_model=List[dict])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return [{
        'id': payment.id,
        'transaction_id': payment.transaction_id,
        'amount': float(payment.amount),
        'currency': payment.currency,
        'status': payment.status,
        'payment_method': payment.payment_method,
        'payment_date': payment.payment_date,
        'created_at': payment.created_at
    } for payment in payments]