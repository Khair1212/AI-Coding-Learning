import React from 'react';
import { useNavigate } from 'react-router-dom';
import './PaymentResult.css';

const PaymentCancelled: React.FC = () => {
  const navigate = useNavigate();

  const handleRetry = () => {
    navigate('/subscription/plans');
  };

  return (
    <div className="payment-result cancelled">
      <div className="payment-card">
        <div className="cancelled-icon">
          <span className="cancel-mark">🚫</span>
        </div>
        
        <h1>Payment Cancelled</h1>
        <p className="cancelled-message">
          You chose to cancel the payment process. No charges have been made to your account.
        </p>

        <div className="cancellation-info">
          <h3>📋 What happened?</h3>
          <ul>
            <li>✅ No money was charged from your account</li>
            <li>✅ Your current subscription remains unchanged</li>
            <li>✅ You can try the payment again anytime</li>
          </ul>
        </div>

        <div className="benefits-reminder">
          <h3>🌟 Why upgrade your subscription?</h3>
          <div className="benefits">
            <div className="benefit-item">
              <span className="benefit-icon">📚</span>
              <div>
                <strong>Complete Course Access</strong>
                <p>Unlock all 10 C programming levels</p>
              </div>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">🤖</span>
              <div>
                <strong>AI-Powered Learning</strong>
                <p>Get personalized questions and AI tutor</p>
              </div>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">📊</span>
              <div>
                <strong>Advanced Analytics</strong>
                <p>Track your progress with detailed insights</p>
              </div>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">⭐</span>
              <div>
                <strong>Priority Support</strong>
                <p>Get help faster with premium support</p>
              </div>
            </div>
          </div>
        </div>

        <div className="special-offer">
          <div className="offer-card">
            <h3>🎁 Limited Time Offer!</h3>
            <p>
              Complete your upgrade within the next 24 hours and get 
              <strong> 10% extra practice questions</strong> for free!
            </p>
            <div className="offer-timer">
              ⏰ Offer valid until tomorrow
            </div>
          </div>
        </div>

        <div className="action-buttons">
          <button className="btn-primary" onClick={handleRetry}>
            Complete Payment Now
          </button>
          <button 
            className="btn-secondary" 
            onClick={() => navigate('/dashboard')}
          >
            Continue with Current Plan
          </button>
        </div>

        <div className="payment-security">
          <h3>🔒 Your Security is Our Priority</h3>
          <div className="security-features">
            <div className="security-item">
              <span>🛡️</span>
              <span>SSL Encrypted Payments</span>
            </div>
            <div className="security-item">
              <span>🏦</span>
              <span>SSLCommerz Secured</span>
            </div>
            <div className="security-item">
              <span>💯</span>
              <span>30-Day Money Back Guarantee</span>
            </div>
          </div>
        </div>

        <div className="support-info">
          <p>
            🤝 Have questions about our plans?<br/>
            📧 Contact us at: <a href="mailto:support@ailearner.com">support@ailearner.com</a>
          </p>
        </div>

        <div className="back-link">
          <button 
            className="btn-link" 
            onClick={() => navigate('/dashboard')}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default PaymentCancelled;