import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { subscriptionAPI, UserLimits } from '../api/subscription';

interface SubscriptionStatusProps {
  compact?: boolean;
}

const SubscriptionStatus: React.FC<SubscriptionStatusProps> = ({ compact = false }) => {
  const navigate = useNavigate();
  const [limits, setLimits] = useState<UserLimits | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLimits();
  }, []);

  const loadLimits = async () => {
    try {
      const limitsData = await subscriptionAPI.checkLimits();
      setLimits(limitsData);
    } catch (error) {
      console.error('Failed to load subscription limits:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTierConfig = (tier: string) => {
    const configs = {
      free: { icon: '🆓', color: '#4a5568', bgColor: '#f7fafc', name: 'Free' },
      gold: { icon: '🥇', color: '#92400e', bgColor: '#fef3c7', name: 'Gold' },
      premium: { icon: '💎', color: '#553c9a', bgColor: '#f3e8ff', name: 'Premium' }
    };
    return configs[tier as keyof typeof configs] || configs.free;
  };

  if (loading || !limits) {
    return null;
  }

  const tierConfig = getTierConfig(limits.subscription_tier);
  const questionUsagePercent = limits.limits.daily_question_limit 
    ? (limits.current_usage.questions_attempted / limits.limits.daily_question_limit) * 100
    : 0;

  const isNearLimit = questionUsagePercent > 80;
  const isAtLimit = limits.limits.daily_question_limit 
    ? limits.current_usage.questions_attempted >= limits.limits.daily_question_limit
    : false;

  if (compact) {
    return (
      <div 
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 12px',
          backgroundColor: tierConfig.bgColor,
          borderRadius: '20px',
          border: `1px solid ${tierConfig.color}20`,
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
        onClick={() => navigate('/subscription/manage')}
      >
        <span style={{ fontSize: '16px' }}>{tierConfig.icon}</span>
        <span style={{ 
          fontSize: '12px', 
          fontWeight: '600', 
          color: tierConfig.color 
        }}>
          {tierConfig.name}
        </span>
        {limits.limits.daily_question_limit && (
          <span style={{ 
            fontSize: '11px', 
            color: isAtLimit ? '#e53e3e' : '#4a5568',
            fontWeight: isAtLimit ? '600' : '400'
          }}>
            {limits.current_usage.questions_attempted}/{limits.limits.daily_question_limit}
          </span>
        )}
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '1.5rem',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
      border: '1px solid #e2e8f0',
      marginBottom: '1.5rem'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '24px' }}>{tierConfig.icon}</span>
          <h3 style={{ 
            margin: 0, 
            color: '#1a202c', 
            fontSize: '1.2rem',
            fontWeight: '700'
          }}>
            {tierConfig.name} Plan
          </h3>
        </div>
        
        <button
          style={{
            background: 'none',
            border: '1px solid #3182ce',
            color: '#3182ce',
            padding: '6px 12px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: '600'
          }}
          onClick={() => navigate('/subscription/manage')}
        >
          Manage
        </button>
      </div>

      {/* Usage Progress */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '4px'
        }}>
          <span style={{ 
            fontSize: '14px', 
            color: '#4a5568',
            fontWeight: '500'
          }}>
            Daily Questions
          </span>
          <span style={{ 
            fontSize: '13px', 
            color: isAtLimit ? '#e53e3e' : '#4a5568',
            fontWeight: isAtLimit ? '600' : '400'
          }}>
            {limits.current_usage.questions_attempted} / {limits.limits.daily_question_limit || '∞'}
          </span>
        </div>

        {limits.limits.daily_question_limit && (
          <div style={{
            width: '100%',
            height: '6px',
            backgroundColor: '#e2e8f0',
            borderRadius: '3px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${Math.min(100, questionUsagePercent)}%`,
              height: '100%',
              backgroundColor: isAtLimit ? '#e53e3e' : isNearLimit ? '#f59e0b' : '#10b981',
              borderRadius: '3px',
              transition: 'width 0.3s ease'
            }}></div>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
        gap: '1rem',
        fontSize: '12px'
      }}>
        {limits.limits.ai_questions_enabled && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: '#4a5568' }}>AI Questions</div>
            <div style={{ fontWeight: '600', color: '#1a202c' }}>
              {limits.current_usage.ai_questions_used}
            </div>
          </div>
        )}
        
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#4a5568' }}>Assessments</div>
          <div style={{ fontWeight: '600', color: '#1a202c' }}>
            {limits.current_usage.assessments_taken}
          </div>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#4a5568' }}>Level Access</div>
          <div style={{ fontWeight: '600', color: '#1a202c' }}>
            {limits.limits.max_level_access ? `1-${limits.limits.max_level_access}` : 'All'}
          </div>
        </div>
      </div>

      {/* Upgrade Prompt */}
      {(limits.subscription_tier === 'free' || isAtLimit) && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem',
          background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
          borderRadius: '8px',
          border: '1px solid #fbbf24',
          textAlign: 'center'
        }}>
          <div style={{ 
            fontSize: '13px', 
            color: '#92400e',
            marginBottom: '0.5rem'
          }}>
            {isAtLimit 
              ? '🚫 Daily limit reached!' 
              : '🚀 Unlock more features!'
            }
          </div>
          <button
            style={{
              background: 'linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%)',
              color: 'white',
              border: 'none',
              padding: '6px 16px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
            onClick={() => navigate('/subscription/plans')}
          >
            Upgrade Now
          </button>
        </div>
      )}
    </div>
  );
};

export default SubscriptionStatus;