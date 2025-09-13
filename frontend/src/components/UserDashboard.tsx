import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LessonMap from './LessonMap';
import UserProfile from './UserProfile';
import SubscriptionStatus from './SubscriptionStatus';
import { subscriptionAPI, UserLimits } from '../api/subscription';
import { theme } from '../styles/theme';

const UserDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'learn' | 'profile'>('learn');
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [subscription, setSubscription] = useState<UserLimits | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Load subscription data
  useEffect(() => {
    const loadSubscription = async () => {
      // Small delay to ensure token is loaded
      await new Promise(resolve => setTimeout(resolve, 500));
      
      try {
        const subscriptionData = await subscriptionAPI.checkLimits();
        setSubscription(subscriptionData);
      } catch (error: any) {
        console.error('Failed to load subscription:', error);
        console.error('Error details:', error.response?.data || error.message);
        console.error('Error status:', error.response?.status);
        
        // Set default free tier if API fails
        setSubscription({
          subscription_tier: 'free',
          current_usage: {
            questions_attempted: 0,
            ai_questions_used: 0,
            assessments_taken: 0
          },
          limits: {
            daily_question_limit: 5, // Match the database default
            max_level_access: 3,
            ai_questions_enabled: false,
            detailed_analytics: false,
            priority_support: false,
            unlimited_retakes: false,
            personalized_tutor: false,
            custom_learning_paths: false
          },
          subscription_valid: true
        });
      }
    };
    
    // Only load subscription if user is logged in
    if (user) {
      loadSubscription();
    }
  }, [user]);

  // Check for payment success parameter
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('payment_success') === 'true') {
      setPaymentSuccess(true);
      // Clear the URL parameter
      window.history.replaceState({}, document.title, '/dashboard');
      // Hide success message after 5 seconds
      setTimeout(() => setPaymentSuccess(false), 5000);
      // Reload subscription data after payment success
      setTimeout(async () => {
        try {
          const subscriptionData = await subscriptionAPI.checkLimits();
          setSubscription(subscriptionData);
        } catch (error: any) {
          console.error('Failed to reload subscription:', error);
          // Set default free tier if API fails even after payment
          setSubscription({
            subscription_tier: 'free',
            current_usage: {
              questions_attempted: 0,
              ai_questions_used: 0,
              assessments_taken: 0
            },
            limits: {
              daily_question_limit: 10,
              max_level_access: 3,
              ai_questions_enabled: false,
              detailed_analytics: false,
              priority_support: false,
              unlimited_retakes: false,
              personalized_tutor: false,
              custom_learning_paths: false
            },
            subscription_valid: true
          });
        }
      }, 2000);
    }
  }, [location]);

  const getTierConfig = (tier: string) => {
    const configs = {
      free: { 
        icon: '🆓', 
        color: '#4a5568', 
        bgColor: '#f7fafc', 
        name: 'Free',
        border: '#e2e8f0',
        gradient: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)'
      },
      gold: { 
        icon: '🥇', 
        color: '#92400e', 
        bgColor: '#fef3c7', 
        name: 'Gold',
        border: '#fbbf24',
        gradient: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
      },
      premium: { 
        icon: '💎', 
        color: '#553c9a', 
        bgColor: '#f3e8ff', 
        name: 'Premium',
        border: '#a855f7',
        gradient: 'linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%)'
      }
    };
    return configs[tier as keyof typeof configs] || configs.free;
  };

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

  return (
    <div style={containerStyle}>
      {/* Payment Success Notification */}
      {paymentSuccess && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: subscription ? getTierConfig(subscription.subscription_tier).gradient : 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
          color: subscription ? getTierConfig(subscription.subscription_tier).color : '#065f46',
          padding: '20px 28px',
          borderRadius: '16px',
          boxShadow: '0 15px 35px rgba(0,0,0,0.2)',
          zIndex: 9999,
          maxWidth: '450px',
          animation: 'slideInRight 0.5s ease-out',
          border: subscription ? `3px solid ${getTierConfig(subscription.subscription_tier).border}` : '3px solid #10b981'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '12px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🎉</div>
            <div style={{ fontSize: '18px', fontWeight: '800', marginBottom: '4px' }}>PAYMENT SUCCESSFUL!</div>
            {subscription && (
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 16px',
                background: 'rgba(255,255,255,0.9)',
                borderRadius: '20px',
                fontSize: '14px',
                fontWeight: '700',
                textTransform: 'uppercase',
                border: `2px solid ${getTierConfig(subscription.subscription_tier).border}`,
                marginTop: '8px'
              }}>
                <span style={{ fontSize: '16px' }}>{getTierConfig(subscription.subscription_tier).icon}</span>
                NOW A {getTierConfig(subscription.subscription_tier).name} USER!
              </div>
            )}
          </div>
          <div style={{ 
            fontSize: '14px', 
            textAlign: 'center',
            lineHeight: '1.4',
            fontWeight: '600'
          }}>
            {subscription ? 
              `🚀 You now have access to all ${getTierConfig(subscription.subscription_tier).name} features!` :
              'Your subscription has been upgraded successfully!'
            }
          </div>
        </div>
      )}
      
      <header style={headerStyle}>
        <div style={logoStyle}>
          AI Coding Learner Version 2
        </div>
        
        <nav style={navStyle}>
          <button
            style={tabButtonStyle(activeTab === 'learn')}
            onClick={() => setActiveTab('learn')}
          >
            Learn
          </button>
          <button
            style={tabButtonStyle(activeTab === 'profile')}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
          
          {/* Upgrade button - only for non-premium users */}
          {(!subscription || subscription.subscription_tier !== 'premium') && (
            <button
              style={{
                padding: '8px 16px',
                border: `1px solid ${theme.colors.primary}`,
                background: subscription?.subscription_tier === 'gold' ? 
                  'linear-gradient(135deg, #c084fc 0%, #a855f7 100%)' : 
                  'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                color: subscription?.subscription_tier === 'gold' ? '#553c9a' : '#92400e',
                borderRadius: theme.borderRadius.md,
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600',
                transition: 'all 0.3s ease'
              }}
              onClick={() => navigate('/subscription/plans')}
            >
              {subscription?.subscription_tier === 'gold' ? '💎 Go Premium' : '💎 Upgrade'}
            </button>
          )}
          
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

      <main>
        {activeTab === 'learn' && <LessonMap />}
        {activeTab === 'profile' && <UserProfile />}
      </main>
    </div>
  );
};

export default UserDashboard;