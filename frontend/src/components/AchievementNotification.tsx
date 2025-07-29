import React, { useState, useEffect } from 'react';
import { theme } from '../styles/theme';

interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
}

interface AchievementNotificationProps {
  achievement: Achievement;
  onClose: () => void;
}

const AchievementNotification: React.FC<AchievementNotificationProps> = ({ 
  achievement, 
  onClose 
}) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    setTimeout(() => setVisible(true), 100);
    
    // Auto close after 4 seconds
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300);
    }, 4000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const overlayStyle = {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    opacity: visible ? 1 : 0,
    transition: 'opacity 0.3s ease'
  };

  const notificationStyle = {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '40px',
    borderRadius: '20px',
    textAlign: 'center' as const,
    maxWidth: '400px',
    width: '90%',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
    transform: visible ? 'scale(1) translateY(0)' : 'scale(0.8) translateY(20px)',
    transition: 'transform 0.3s ease'
  };

  const iconStyle = {
    fontSize: '80px',
    marginBottom: '20px',
    display: 'block',
    animation: visible ? 'bounce 1s ease-in-out' : 'none'
  };

  const titleStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '12px',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
  };

  const descriptionStyle = {
    fontSize: '16px',
    marginBottom: '20px',
    opacity: 0.9
  };

  const xpStyle = {
    fontSize: '18px',
    fontWeight: 'bold',
    background: 'rgba(255, 255, 255, 0.2)',
    padding: '8px 16px',
    borderRadius: '20px',
    display: 'inline-block'
  };

  const closeButtonStyle = {
    position: 'absolute' as const,
    top: '15px',
    right: '15px',
    background: 'rgba(255, 255, 255, 0.2)',
    border: 'none',
    color: 'white',
    width: '30px',
    height: '30px',
    borderRadius: '50%',
    cursor: 'pointer',
    fontSize: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={notificationStyle} onClick={(e) => e.stopPropagation()}>
        <button style={closeButtonStyle} onClick={onClose}>
          ×
        </button>
        
        <div style={iconStyle}>
          {achievement.icon}
        </div>
        
        <h2 style={titleStyle}>
          Achievement Unlocked!
        </h2>
        
        <h3 style={{ ...titleStyle, fontSize: '20px' }}>
          {achievement.name}
        </h3>
        
        <p style={descriptionStyle}>
          {achievement.description}
        </p>
        
        <div style={xpStyle}>
          +{achievement.xp_reward} XP
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 20%, 60%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-10px);
          }
          80% {
            transform: translateY(-5px);
          }
        }
      `}</style>
    </div>
  );
};

export default AchievementNotification;