import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { subscriptionAPI, UserSubscription, UserLimits } from '../api/subscription';
import './SubscriptionManage.css';

const SubscriptionManage: React.FC = () => {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<UserSubscription | null>(null);
  const [limits, setLimits] = useState<UserLimits | null>(null);
  const [paymentHistory, setPaymentHistory] = useState<any[]>([]);
  const [usage, setUsage] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [subscriptionData, limitsData, historyData, usageData] = await Promise.all([
        subscriptionAPI.getMySubscription(),
        subscriptionAPI.checkLimits(),
        subscriptionAPI.getPaymentHistory().catch(() => []),
        subscriptionAPI.getUsage(7).catch(() => []), // Last 7 days
      ]);

      setSubscription(subscriptionData);
      setLimits(limitsData);
      setPaymentHistory(historyData);
      setUsage(usageData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel auto-renewal? Your subscription will remain active until the end of the current billing period.')) {
      return;
    }

    try {
      setCancelling(true);
      await subscriptionAPI.cancelSubscription();
      await loadData(); // Refresh data
      alert('Auto-renewal has been cancelled successfully.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel subscription');
    } finally {
      setCancelling(false);
    }
  };

  const handleUpgrade = () => {
    navigate('/subscription/plans');
  };

  const getTierBadge = (tier: string) => {
    const configs = {
      free: { icon: '🆓', color: 'tier-free' },
      gold: { icon: '🥇', color: 'tier-gold' },
      premium: { icon: '💎', color: 'tier-premium' }
    };
    const config = configs[tier as keyof typeof configs] || configs.free;
    return { icon: config.icon, color: config.color };
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount: number) => {
    return `৳${amount.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="subscription-manage loading">
        <div className="loading-spinner large"></div>
        <p>Loading your subscription details...</p>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="subscription-manage no-subscription">
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h2>No Active Subscription</h2>
          <p>You don't have an active subscription yet. Choose a plan to get started!</p>
          <button className="btn-primary" onClick={handleUpgrade}>
            View Subscription Plans
          </button>
        </div>
      </div>
    );
  }

  const tierBadge = getTierBadge(subscription.tier);

  return (
    <div className="subscription-manage">
      <div className="page-header">
        <h1>Manage Subscription</h1>
        <button className="btn-back" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
          <button className="btn-retry" onClick={loadData}>Retry</button>
        </div>
      )}

      {/* Current Subscription */}
      <div className="subscription-card">
        <div className="card-header">
          <h2>Current Subscription</h2>
          <div className={`tier-badge ${tierBadge.color}`}>
            <span className="tier-icon">{tierBadge.icon}</span>
            <span className="tier-name">{subscription.tier.toUpperCase()}</span>
          </div>
        </div>

        <div className="subscription-details">
          <div className="detail-grid">
            <div className="detail-item">
              <strong>Status:</strong>
              <span className={`status ${subscription.is_active ? 'active' : 'inactive'}`}>
                {subscription.is_active ? '✅ Active' : '❌ Inactive'}
              </span>
            </div>
            
            <div className="detail-item">
              <strong>Started:</strong>
              <span>{formatDate(subscription.start_date)}</span>
            </div>

            {subscription.end_date && (
              <div className="detail-item">
                <strong>Expires:</strong>
                <span>{formatDate(subscription.end_date)}</span>
              </div>
            )}

            <div className="detail-item">
              <strong>Auto-Renew:</strong>
              <span className={subscription.auto_renew ? 'enabled' : 'disabled'}>
                {subscription.auto_renew ? '✅ Enabled' : '❌ Disabled'}
              </span>
            </div>
          </div>

          <div className="subscription-actions">
            {subscription.tier !== 'premium' && (
              <button className="btn-upgrade" onClick={handleUpgrade}>
                🚀 Upgrade Plan
              </button>
            )}
            
            {subscription.tier !== 'free' && subscription.auto_renew && (
              <button 
                className="btn-cancel" 
                onClick={handleCancelSubscription}
                disabled={cancelling}
              >
                {cancelling ? 'Cancelling...' : '🚫 Cancel Auto-Renewal'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Usage Overview */}
      {limits && (
        <div className="usage-card">
          <div className="card-header">
            <h2>Current Usage</h2>
            <span className="usage-period">Today</span>
          </div>

          <div className="usage-stats">
            <div className="usage-item">
              <div className="usage-icon">❓</div>
              <div className="usage-details">
                <div className="usage-title">Questions</div>
                <div className="usage-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{
                        width: limits.limits.daily_question_limit 
                          ? `${Math.min(100, (limits.current_usage.questions_attempted / limits.limits.daily_question_limit) * 100)}%`
                          : '0%'
                      }}
                    ></div>
                  </div>
                  <div className="usage-text">
                    {limits.current_usage.questions_attempted} / {limits.limits.daily_question_limit || '∞'}
                  </div>
                </div>
              </div>
            </div>

            {limits.limits.ai_questions_enabled && (
              <div className="usage-item">
                <div className="usage-icon">🤖</div>
                <div className="usage-details">
                  <div className="usage-title">AI Questions</div>
                  <div className="usage-text">
                    {limits.current_usage.ai_questions_used} used today
                  </div>
                </div>
              </div>
            )}

            <div className="usage-item">
              <div className="usage-icon">📊</div>
              <div className="usage-details">
                <div className="usage-title">Assessments</div>
                <div className="usage-text">
                  {limits.current_usage.assessments_taken} completed today
                </div>
              </div>
            </div>
          </div>

          <div className="feature-status">
            <h3>Features Available</h3>
            <div className="features-grid">
              <div className={`feature ${limits.limits.ai_questions_enabled ? 'enabled' : 'disabled'}`}>
                <span className="feature-icon">{limits.limits.ai_questions_enabled ? '🤖' : '🚫'}</span>
                <span>AI Questions</span>
              </div>
              <div className={`feature ${limits.limits.detailed_analytics ? 'enabled' : 'disabled'}`}>
                <span className="feature-icon">{limits.limits.detailed_analytics ? '📊' : '🚫'}</span>
                <span>Detailed Analytics</span>
              </div>
              <div className={`feature ${limits.limits.priority_support ? 'enabled' : 'disabled'}`}>
                <span className="feature-icon">{limits.limits.priority_support ? '⭐' : '🚫'}</span>
                <span>Priority Support</span>
              </div>
              <div className={`feature ${limits.limits.unlimited_retakes ? 'enabled' : 'disabled'}`}>
                <span className="feature-icon">{limits.limits.unlimited_retakes ? '🔄' : '🚫'}</span>
                <span>Unlimited Retakes</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment History */}
      {paymentHistory.length > 0 && (
        <div className="payment-history-card">
          <div className="card-header">
            <h2>Payment History</h2>
            <span className="history-count">{paymentHistory.length} transactions</span>
          </div>

          <div className="payment-list">
            {paymentHistory.slice(0, 5).map((payment) => (
              <div key={payment.id} className="payment-item">
                <div className="payment-info">
                  <div className="payment-id">#{payment.transaction_id}</div>
                  <div className="payment-date">{formatDate(payment.created_at)}</div>
                </div>
                <div className="payment-amount">{formatCurrency(payment.amount)}</div>
                <div className={`payment-status ${payment.status}`}>
                  {payment.status === 'completed' ? '✅' : payment.status === 'failed' ? '❌' : '⏳'} 
                  {payment.status.toUpperCase()}
                </div>
              </div>
            ))}
          </div>

          {paymentHistory.length > 5 && (
            <div className="show-more">
              <button className="btn-link">Show All Transactions</button>
            </div>
          )}
        </div>
      )}

      {/* Usage History */}
      {usage.length > 0 && (
        <div className="usage-history-card">
          <div className="card-header">
            <h2>Weekly Activity</h2>
            <span className="activity-period">Last 7 days</span>
          </div>

          <div className="activity-chart">
            {usage.map((day, index) => (
              <div key={index} className="activity-day">
                <div className="day-label">
                  {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
                <div className="day-stats">
                  <div className="stat-item">
                    <span className="stat-icon">❓</span>
                    <span className="stat-value">{day.questions_attempted}</span>
                  </div>
                  {day.ai_questions_used > 0 && (
                    <div className="stat-item">
                      <span className="stat-icon">🤖</span>
                      <span className="stat-value">{day.ai_questions_used}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Support */}
      <div className="support-card">
        <h2>Need Help?</h2>
        <div className="support-options">
          <div className="support-item">
            <span className="support-icon">📧</span>
            <div>
              <strong>Email Support</strong>
              <p>Get help within 24 hours</p>
              <a href="mailto:support@ailearner.com">support@ailearner.com</a>
            </div>
          </div>
          
          {limits?.limits.priority_support && (
            <div className="support-item priority">
              <span className="support-icon">⭐</span>
              <div>
                <strong>Priority Support</strong>
                <p>Get help within 2 hours</p>
                <a href="mailto:priority@ailearner.com">priority@ailearner.com</a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubscriptionManage;