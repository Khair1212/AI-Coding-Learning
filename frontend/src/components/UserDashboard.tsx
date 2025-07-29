import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LessonMap from './LessonMap';
import UserProfile from './UserProfile';
import { theme } from '../styles/theme';

const UserDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'learn' | 'profile'>('learn');
  const navigate = useNavigate();

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
      <header style={headerStyle}>
        <div style={logoStyle}>
          AI Coding Learner
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