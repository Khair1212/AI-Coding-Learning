import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { learningAPI, UserProfile as UserProfileType } from '../api/learning';
import { subscriptionAPI, UserLimits } from '../api/subscription';
import { theme } from '../styles/theme';

interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  earned_at?: string;
}

const UserProfile: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfileType | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [subscription, setSubscription] = useState<UserLimits | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const [profileData, achievementsData, subscriptionData] = await Promise.all([
        learningAPI.getProfile(),
        learningAPI.getAchievements(),
        subscriptionAPI.checkLimits().catch(() => null) // Don't fail if subscription data unavailable
      ]);
      setProfile(profileData);
      setAchievements(achievementsData);
      setSubscription(subscriptionData);
    } catch (error) {
      console.error('Error fetching profile data:', error);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading profile...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Profile not found</div>
      </div>
    );
  }

  const containerStyle = {
    padding: '20px',
    maxWidth: '800px',
    margin: '0 auto'
  };

  const cardStyle = {
    background: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: '24px',
    marginBottom: '20px',
    boxShadow: theme.shadows.md
  };

  const headerStyle = {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '20px',
    gap: '16px'
  };

  const avatarStyle = {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: theme.colors.primary,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '32px',
    fontWeight: 'bold'
  };

  const statsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '16px',
    marginBottom: '24px'
  };

  const statCardStyle = {
    background: '#f8f9fa',
    padding: '16px',
    borderRadius: theme.borderRadius.md,
    textAlign: 'center' as const
  };

  const statValueStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: '4px'
  };

  const statLabelStyle = {
    fontSize: '14px',
    color: theme.colors.textSecondary
  };

  const progressBarStyle = {
    width: '100%',
    height: '8px',
    background: '#e9ecef',
    borderRadius: '4px',
    overflow: 'hidden' as const,
    marginBottom: '8px'
  };

  const progressFillStyle = {
    height: '100%',
    background: `linear-gradient(90deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
    width: `${Math.min((profile.total_xp % 100) / 100 * 100, 100)}%`,
    transition: 'width 0.3s ease'
  };

  const achievementGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '12px'
  };

  const achievementCardStyle = (earned: boolean) => ({
    background: earned ? theme.colors.surface : '#f8f9fa',
    border: earned ? `2px solid ${theme.colors.primary}` : '2px solid #e9ecef',
    borderRadius: theme.borderRadius.md,
    padding: '16px',
    textAlign: 'center' as const,
    opacity: earned ? 1 : 0.6,
    transition: 'all 0.3s ease'
  });

  const earnedAchievements = achievements.filter(a => a.earned_at);
  const nextLevelXP = (profile.current_level + 1) * 100;

  return (
    <div style={containerStyle}>
      {/* Profile Header */}
      <div style={cardStyle}>
        <div style={headerStyle}>
          <div style={avatarStyle}>
            {user?.username.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
              <h2 style={{ margin: 0, color: theme.colors.text }}>
                {user?.username}
              </h2>
              {subscription && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 16px',
                  background: getTierConfig(subscription.subscription_tier).gradient,
                  color: getTierConfig(subscription.subscription_tier).color,
                  borderRadius: '24px',
                  fontSize: '14px',
                  fontWeight: '700',
                  textTransform: 'uppercase',
                  border: `2px solid ${getTierConfig(subscription.subscription_tier).border}`,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onClick={() => window.location.href = '/subscription/manage'}
                >
                  <span style={{ fontSize: '16px' }}>{getTierConfig(subscription.subscription_tier).icon}</span>
                  {getTierConfig(subscription.subscription_tier).name} USER
                </div>
              )}
            </div>
            <p style={{ margin: 0, color: theme.colors.textSecondary, fontSize: '16px' }}>
              Level {profile.current_level} C Programmer
            </p>
            {subscription && (
              <div style={{
                marginTop: '8px',
                padding: '8px 12px',
                background: getTierConfig(subscription.subscription_tier).bgColor,
                borderRadius: '8px',
                border: `1px solid ${getTierConfig(subscription.subscription_tier).border}40`,
                fontSize: '13px',
                color: getTierConfig(subscription.subscription_tier).color,
                fontWeight: '500'
              }}>
                🎯 {subscription.subscription_tier === 'premium' ? 
                  'You have full access to all premium features!' :
                  subscription.subscription_tier === 'gold' ? 
                  'Enjoying Gold benefits! Consider upgrading to Premium for more features.' :
                  'Upgrade to unlock advanced features and unlimited access!'
                }
              </div>
            )}
          </div>
        </div>

        {/* XP Progress */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ fontSize: '14px', color: theme.colors.textSecondary }}>
              Progress to Level {profile.current_level + 1}
            </span>
            <span style={{ fontSize: '14px', color: theme.colors.textSecondary }}>
              {profile.total_xp % 100}/{nextLevelXP % 100} XP
            </span>
          </div>
          <div style={progressBarStyle}>
            <div style={progressFillStyle}></div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={cardStyle}>
        <h3 style={{ marginBottom: '16px', color: theme.colors.text }}>Statistics</h3>
        <div style={statsGridStyle}>
          <div style={statCardStyle}>
            <div style={statValueStyle}>{profile.total_xp}</div>
            <div style={statLabelStyle}>Total XP</div>
          </div>
          <div style={statCardStyle}>
            <div style={statValueStyle}>{profile.lessons_completed}</div>
            <div style={statLabelStyle}>Lessons Completed</div>
          </div>
          <div style={statCardStyle}>
            <div style={statValueStyle}>{profile.current_streak}</div>
            <div style={statLabelStyle}>Current Streak</div>
          </div>
          <div style={statCardStyle}>
            <div style={statValueStyle}>{profile.longest_streak}</div>
            <div style={statLabelStyle}>Longest Streak</div>
          </div>
          <div style={statCardStyle}>
            <div style={statValueStyle}>{profile.accuracy_rate.toFixed(1)}%</div>
            <div style={statLabelStyle}>Accuracy</div>
          </div>
        </div>
      </div>

      {/* Achievements */}
      <div style={cardStyle}>
        <h3 style={{ marginBottom: '16px', color: theme.colors.text }}>
          Achievements ({earnedAchievements.length}/{achievements.length})
        </h3>
        <div style={achievementGridStyle}>
          {achievements.map((achievement) => (
            <div
              key={achievement.id}
              style={achievementCardStyle(!!achievement.earned_at)}
            >
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>
                {achievement.icon}
              </div>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '16px' }}>
                {achievement.name}
              </h4>
              <p style={{ margin: 0, fontSize: '12px', color: theme.colors.textSecondary }}>
                {achievement.description}
              </p>
              {achievement.earned_at && (
                <p style={{ margin: '8px 0 0 0', fontSize: '10px', color: theme.colors.primary }}>
                  Earned {new Date(achievement.earned_at).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;