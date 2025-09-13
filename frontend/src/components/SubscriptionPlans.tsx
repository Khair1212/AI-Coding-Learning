import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { subscriptionAPI, SubscriptionPlan, UserSubscription, PaymentSession } from '../api/subscription';
import PaymentModal from './PaymentModal';
import { theme } from '../styles/theme';
import './SubscriptionPlans.css';

const SubscriptionPlans: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<UserSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentModal, setPaymentModal] = useState<{
    isOpen: boolean;
    tier: 'gold' | 'premium';
    planName: string;
    price: number;
  }>({
    isOpen: false,
    tier: 'gold',
    planName: '',
    price: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [plansData, subscriptionData] = await Promise.all([
        subscriptionAPI.getPlans(),
        subscriptionAPI.getMySubscription(),
      ]);
      setPlans(plansData);
      setCurrentSubscription(subscriptionData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = (tier: 'gold' | 'premium') => {
    const plan = plans.find(p => p.tier === tier);
    if (!plan) return;

    setPaymentModal({
      isOpen: true,
      tier,
      planName: plan.name,
      price: plan.price
    });
  };

  const handlePaymentSuccess = async () => {
    // Show success message
    const successMessage = `🎉 Congratulations! You're now a ${paymentModal.planName} user!`;
    
    // Refresh subscription data after successful payment
    await loadData();
    setPaymentModal(prev => ({ ...prev, isOpen: false }));
    
    // Show success notification
    alert(successMessage);
  };

  const getPlanIcon = (tier: string) => {
    switch (tier) {
      case 'free': return '🆓';
      case 'gold': return '🥇';
      case 'premium': return '💎';
      default: return '📦';
    }
  };

  const getPlanColor = (tier: string) => {
    switch (tier) {
      case 'free': return 'plan-free';
      case 'gold': return 'plan-gold';
      case 'premium': return 'plan-premium';
      default: return 'plan-free';
    }
  };

  const isCurrentPlan = (tier: string) => {
    return currentSubscription?.tier === tier && currentSubscription?.is_active;
  };

  const canUpgrade = (tier: string) => {
    if (!currentSubscription) return tier !== 'free';
    if (tier === 'free') return false;
    if (currentSubscription.tier === 'premium') return false;
    if (currentSubscription.tier === 'gold' && tier === 'premium') return true;
    return currentSubscription.tier === 'free';
  };

  // Navigation styles
  const containerStyle = {
    minHeight: '100vh',
    background: theme.colors.background
  };

  const headerStyle = {
    background: theme.colors.surface,
    boxShadow: theme.shadows.sm,
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const logoStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    color: theme.colors.primary
  };

  const navStyle = {
    display: 'flex',
    gap: '24px',
    alignItems: 'center'
  };

  const tabButtonStyle = (isActive: boolean) => ({
    padding: '8px 16px',
    border: 'none',
    background: isActive ? theme.colors.primary : 'transparent',
    color: isActive ? 'white' : theme.colors.text,
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.3s ease'
  });

  const userInfoStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  };

  const logoutButtonStyle = {
    padding: '8px 16px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500'
  };

  if (loading) {
    return (
      <div style={containerStyle}>
        <header style={headerStyle}>
          <div style={logoStyle}>
            AI Coding Learner Version 2
          </div>
          
          <nav style={navStyle}>
            <button
              style={tabButtonStyle(false)}
              onClick={() => navigate('/dashboard')}
            >
              Learn
            </button>
            <button
              style={tabButtonStyle(false)}
              onClick={() => navigate('/dashboard?tab=profile')}
            >
              Profile
            </button>
            <button
              style={tabButtonStyle(true)}
            >
              Subscription Plans
            </button>
            <button
              style={{
                padding: '8px 16px',
                border: `2px solid ${theme.colors.primary}`,
                background: 'transparent',
                color: theme.colors.primary,
                borderRadius: theme.borderRadius.md,
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600',
                transition: 'all 0.3s ease'
              }}
              onClick={() => navigate('/assessment')}
            >
              🎯 Take Assessment
            </button>
          </nav>

          <div style={userInfoStyle}>
            <span style={{ color: theme.colors.text }}>
              Welcome, {user?.username}!
            </span>
            <button onClick={logout} style={logoutButtonStyle}>
              Logout
            </button>
          </div>
        </header>

        <main style={{ padding: '20px' }}>
          <div className="subscription-loading">
            <div className="loading-spinner"></div>
            <p>Loading subscription plans...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <div style={logoStyle}>
          AI Coding Learner Version 2
        </div>
        
        <nav style={navStyle}>
          <button
            style={tabButtonStyle(false)}
            onClick={() => navigate('/dashboard')}
          >
            Learn
          </button>
          <button
            style={tabButtonStyle(false)}
            onClick={() => navigate('/dashboard?tab=profile')}
          >
            Profile
          </button>
          <button
            style={tabButtonStyle(true)}
          >
            Subscription Plans
          </button>
          <button
            style={{
              padding: '8px 16px',
              border: `2px solid ${theme.colors.primary}`,
              background: 'transparent',
              color: theme.colors.primary,
              borderRadius: theme.borderRadius.md,
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              transition: 'all 0.3s ease'
            }}
            onClick={() => navigate('/assessment')}
          >
            🎯 Take Assessment
          </button>
        </nav>

        <div style={userInfoStyle}>
          <span style={{ color: theme.colors.text }}>
            Welcome, {user?.username}!
          </span>
          <button onClick={logout} style={logoutButtonStyle}>
            Logout
          </button>
        </div>
      </header>

      <main style={{ padding: '20px' }}>
        <div className="subscription-plans">
      <div className="subscription-header">
        <h1>Choose Your Learning Plan</h1>
        <p>Unlock your potential with our comprehensive C programming courses</p>
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
      </div>

      <div className="plans-container">
        {plans.map((plan) => (
          <div 
            key={plan.id} 
            className={`plan-card ${getPlanColor(plan.tier)} ${isCurrentPlan(plan.tier) ? 'current-plan' : ''}`}
          >
            <div className="plan-header">
              <div className="plan-icon">{getPlanIcon(plan.tier)}</div>
              <h3>{plan.name}</h3>
              {isCurrentPlan(plan.tier) && (
                <div className="current-badge">Current Plan</div>
              )}
            </div>

            <div className="plan-price">
              <span className="currency">৳</span>
              <span className="amount">{plan.price}</span>
              {plan.price > 0 && <span className="period">/month</span>}
            </div>

            <div className="plan-description">
              {plan.description}
            </div>

            <div className="plan-features">
              <div className="feature">
                <span className="feature-icon">❓</span>
                <span>
                  {plan.daily_question_limit ? `${plan.daily_question_limit} questions/day` : 'Unlimited questions'}
                </span>
              </div>

              <div className="feature">
                <span className="feature-icon">📚</span>
                <span>
                  {plan.max_level_access ? `Access to ${plan.max_level_access} levels` : 'All 10 levels'}
                </span>
              </div>

              <div className="feature">
                <span className="feature-icon">🎯</span>
                <span>Assessment tests</span>
              </div>

              <div className="feature">
                <span className="feature-icon">📊</span>
                <span>Progress tracking</span>
              </div>
            </div>

            <div className="plan-action">
              {isCurrentPlan(plan.tier) ? (
                <button className="btn-current" disabled>
                  ✅ Current Plan
                </button>
              ) : canUpgrade(plan.tier) ? (
                <button 
                  className="btn-upgrade"
                  onClick={() => handleUpgrade(plan.tier as 'gold' | 'premium')}
                >
                  {`Upgrade to ${plan.name}`}
                </button>
              ) : (
                <button className="btn-disabled" disabled>
                  {plan.tier === 'free' ? 'Basic Plan' : 'Already Premium'}
                </button>
              )}
            </div>

            {plan.tier === 'premium' && (
              <div className="plan-badge">
                <span>🏆 Most Popular</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="subscription-info">
        <div className="payment-info">
          <h3>🔒 Secure Payment</h3>
          <p>Powered by SSLCommerz - Bangladesh's leading payment gateway</p>
          <div className="payment-methods">
            <span>💳 Credit/Debit Cards</span>
            <span>📱 Mobile Banking</span>
            <span>🏦 Net Banking</span>
          </div>
        </div>

        <div className="money-back">
          <h3>💯 30-Day Money Back Guarantee</h3>
          <p>Not satisfied? Get your money back within 30 days of purchase.</p>
        </div>
      </div>

      <PaymentModal
        isOpen={paymentModal.isOpen}
        onClose={() => setPaymentModal(prev => ({ ...prev, isOpen: false }))}
        tier={paymentModal.tier}
        planName={paymentModal.planName}
        price={paymentModal.price}
        onSuccess={handlePaymentSuccess}
      />
        </div>
      </main>
    </div>
  );
};

export default SubscriptionPlans;