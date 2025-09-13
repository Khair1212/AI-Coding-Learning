import React, { useState } from 'react';
import { subscriptionAPI, PaymentSession } from '../api/subscription';
import './PaymentModal.css';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  tier: 'gold' | 'premium';
  planName: string;
  price: number;
  onSuccess: () => void;
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  tier,
  planName,
  price,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(3);

  const handlePayment = async () => {
    try {
      setLoading(true);
      setError(null);

      const paymentRequest = {
        subscription_tier: tier,
        success_url: `http://localhost:8000/api/subscription/payment-success`,
        fail_url: `http://localhost:8000/api/subscription/payment-failure`,
        cancel_url: `http://localhost:8000/api/subscription/payment-cancel`,
      };

      const paymentSession: PaymentSession = await subscriptionAPI.createPaymentSession(paymentRequest);

      if (paymentSession.status === 'success' && paymentSession.payment_url) {
        setPaymentUrl(paymentSession.payment_url);
      } else {
        throw new Error(paymentSession.message || 'Failed to create payment session');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Payment initiation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleIframeLoad = () => {
    // Listen for messages from the iframe success page
    const handleMessage = (event: MessageEvent) => {
      // Only accept messages from our backend
      if (event.origin !== 'http://localhost:8000') return;
      
      if (event.data.type === 'payment_success') {
        console.log('Payment successful:', event.data.transaction_id);
        onSuccess();
        onClose();
      } else if (event.data.type === 'payment_failed' || event.data.type === 'payment_cancelled') {
        setPaymentUrl(null);
        setError('Payment was not completed. Please try again.');
      }
    };

    window.addEventListener('message', handleMessage);
    
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  };

  // Auto-redirect when payment URL is set
  React.useEffect(() => {
    if (paymentUrl) {
      setCountdown(3);
      
      // Countdown timer
      const countdownInterval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(countdownInterval);
            window.open(paymentUrl, '_blank');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      // Listen for when user returns (window gets focus)
      const handleFocus = () => {
        // User might have returned from payment, refresh data and redirect to dashboard
        setTimeout(async () => {
          try {
            await onSuccess(); // This will refresh subscription data
            onClose(); // Close modal
            // Force redirect to dashboard after successful payment
            window.location.href = '/dashboard?payment_success=true';
          } catch (error) {
            console.error('Error handling payment return:', error);
          }
        }, 3000); // Wait 3 seconds to ensure payment processing is complete
      };

      window.addEventListener('focus', handleFocus);

      return () => {
        clearInterval(countdownInterval);
        window.removeEventListener('focus', handleFocus);
      };
    }
  }, [paymentUrl, onSuccess, onClose]);

  if (!isOpen) return null;

  return (
    <div className="payment-modal-overlay">
      <div className="payment-modal">
        <div className="modal-header">
          <h2>Complete Your Upgrade</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {!paymentUrl && (
            <>
              <div className="payment-summary">
                <div className="plan-info">
                  <h3>{planName} Plan</h3>
                  <div className="price">৳{price}/month</div>
                </div>

                <div className="payment-details">
                  <div className="detail-row">
                    <span>Plan:</span>
                    <span>{planName}</span>
                  </div>
                  <div className="detail-row">
                    <span>Billing:</span>
                    <span>Monthly</span>
                  </div>
                  <div className="detail-row total">
                    <span>Total:</span>
                    <span>৳{price}</span>
                  </div>
                </div>

                <div className="payment-methods">
                  <h4>🔒 Secure Payment Methods</h4>
                  <div className="methods-grid">
                    <div className="method">💳 Credit/Debit Cards</div>
                    <div className="method">📱 Mobile Banking</div>
                    <div className="method">🏦 Net Banking</div>
                  </div>
                </div>

                {error && (
                  <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    {error}
                  </div>
                )}

                <div className="modal-actions">
                  <button 
                    className="btn-cancel" 
                    onClick={onClose}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button 
                    className="btn-pay" 
                    onClick={handlePayment}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner"></span>
                        Processing...
                      </>
                    ) : (
                      `Pay ৳${price}`
                    )}
                  </button>
                </div>
              </div>
            </>
          )}

          {paymentUrl && (
            <div className="payment-redirect-container">
              <div className="redirect-message">
                <div className="message-content">
                  <div className="countdown-display">{countdown}</div>
                  <h3>🔒 Redirecting to Secure Payment</h3>
                  <p>SSLCommerz requires external window for security. Opening payment page in {countdown} seconds...</p>
                  <p><strong>After payment, you'll be redirected back here automatically.</strong></p>
                </div>
                
                <div className="redirect-actions">
                  <button 
                    className="btn-redirect-now" 
                    onClick={() => window.open(paymentUrl, '_blank')}
                  >
                    🚀 Complete Payment Now
                  </button>
                  <button 
                    className="btn-cancel" 
                    onClick={() => setPaymentUrl(null)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
              
              <div className="security-badges">
                <div className="badge">🛡️ SSL Secured</div>
                <div className="badge">🏦 Bank Grade Security</div>
                <div className="badge">↩️ Auto Return</div>
              </div>
            </div>
          )}

          {!paymentUrl && (
            <div className="security-badges">
              <div className="badge">🛡️ SSL Secured</div>
              <div className="badge">🏦 Bank Grade Security</div>
              <div className="badge">💯 30-Day Money Back</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentModal;