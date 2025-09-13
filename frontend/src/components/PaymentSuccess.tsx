import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { subscriptionAPI } from '../api/subscription';
import './PaymentResult.css';

const PaymentSuccess: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [subscriptionData, setSubscriptionData] = useState<any>(null);

  useEffect(() => {
    // Refresh subscription data after successful payment
    const refreshSubscription = async () => {
      try {
        const subscription = await subscriptionAPI.getMySubscription();
        setSubscriptionData(subscription);
      } catch (error) {
        console.error('Failed to refresh subscription data:', error);
      } finally {
        setLoading(false);
      }
    };

    // Delay to ensure backend has processed the payment
    setTimeout(refreshSubscription, 2000);
  }, []);

  const handleContinue = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className="payment-result loading">
        <div className="payment-card">
          <div className="loading-spinner large"></div>
          <h2>Processing your payment...</h2>
          <p>Please wait while we confirm your subscription.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-result success">
      <div className="payment-card">
        <div className="success-icon">
          <span className="checkmark">✅</span>
        </div>
        
        <h1>Payment Successful!</h1>
        <p className="success-message">
          🎉 Congratulations! Your subscription has been activated successfully.
        </p>

        {subscriptionData && (
          <div className="subscription-details">
            <h3>Your New Subscription</h3>
            <div className="detail-item">
              <strong>Plan:</strong> 
              <span className={`tier-badge ${subscriptionData.tier}`}>
                {subscriptionData.tier.charAt(0).toUpperCase() + subscriptionData.tier.slice(1)}
              </span>
            </div>
            <div className="detail-item">
              <strong>Status:</strong> 
              <span className="status-active">Active</span>
            </div>
            {subscriptionData.end_date && (
              <div className="detail-item">
                <strong>Valid Until:</strong> 
                <span>{new Date(subscriptionData.end_date).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        )}

        <div className="benefits-list">
          <h3>🚀 What's Now Available:</h3>
          <ul>
            <li>✅ Increased daily question limits</li>
            <li>✅ Access to all programming levels</li>
            <li>✅ AI-generated practice questions</li>
            <li>✅ Detailed progress analytics</li>
            <li>✅ Priority support access</li>
          </ul>
        </div>

        <div className="action-buttons">
          <button className="btn-primary" onClick={handleContinue}>
            Start Learning Now!
          </button>
          <button 
            className="btn-secondary" 
            onClick={() => navigate('/subscription/manage')}
          >
            Manage Subscription
          </button>
        </div>

        <div className="support-info">
          <p>
            📧 Need help? Contact our support team at{' '}
            <a href="mailto:support@ailearner.com">support@ailearner.com</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccess;