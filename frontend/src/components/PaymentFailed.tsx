import React from 'react';
import { useNavigate } from 'react-router-dom';
import './PaymentResult.css';

const PaymentFailed: React.FC = () => {
  const navigate = useNavigate();

  const handleRetry = () => {
    navigate('/subscription/plans');
  };

  const handleContactSupport = () => {
    window.open('mailto:support@ailearner.com?subject=Payment Failed - Need Help', '_blank');
  };

  return (
    <div className="payment-result failed">
      <div className="payment-card">
        <div className="failed-icon">
          <span className="error-mark">❌</span>
        </div>
        
        <h1>Payment Failed</h1>
        <p className="failed-message">
          😔 Unfortunately, your payment could not be processed at this time.
        </p>

        <div className="reasons-list">
          <h3>🤔 Common reasons for payment failure:</h3>
          <ul>
            <li>Insufficient funds in your account</li>
            <li>Incorrect card details entered</li>
            <li>Card expired or blocked</li>
            <li>Bank declined the transaction</li>
            <li>Network connectivity issues</li>
          </ul>
        </div>

        <div className="troubleshooting">
          <h3>💡 What you can do:</h3>
          <div className="tips">
            <div className="tip">
              <strong>1. Check your card details</strong>
              <p>Ensure your card number, expiry date, and CVV are correct</p>
            </div>
            <div className="tip">
              <strong>2. Verify your balance</strong>
              <p>Make sure you have sufficient funds available</p>
            </div>
            <div className="tip">
              <strong>3. Contact your bank</strong>
              <p>Some banks block online transactions by default</p>
            </div>
            <div className="tip">
              <strong>4. Try a different payment method</strong>
              <p>Use mobile banking or net banking instead</p>
            </div>
          </div>
        </div>

        <div className="action-buttons">
          <button className="btn-primary" onClick={handleRetry}>
            Try Again
          </button>
          <button className="btn-secondary" onClick={handleContactSupport}>
            Contact Support
          </button>
        </div>

        <div className="alternative-payment">
          <h3>🏦 Alternative Payment Methods</h3>
          <div className="payment-options">
            <div className="payment-method">
              <span>📱</span>
              <div>
                <strong>Mobile Banking</strong>
                <p>bKash, Nagad, Rocket</p>
              </div>
            </div>
            <div className="payment-method">
              <span>🏦</span>
              <div>
                <strong>Net Banking</strong>
                <p>All major banks supported</p>
              </div>
            </div>
            <div className="payment-method">
              <span>💳</span>
              <div>
                <strong>Debit/Credit Cards</strong>
                <p>Visa, MasterCard, AMEX</p>
              </div>
            </div>
          </div>
        </div>

        <div className="support-info">
          <p>
            🆘 Still having trouble? Our support team is here to help!<br/>
            📧 Email: <a href="mailto:support@ailearner.com">support@ailearner.com</a><br/>
            📞 Phone: +88 01XXX-XXXXXX
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

export default PaymentFailed;