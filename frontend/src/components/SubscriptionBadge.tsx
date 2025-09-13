import React from 'react';

interface SubscriptionBadgeProps {
  tier: string;
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  showText?: boolean;
}

const SubscriptionBadge: React.FC<SubscriptionBadgeProps> = ({ 
  tier, 
  size = 'medium', 
  onClick,
  showText = true 
}) => {
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

  const getSizeConfig = (size: string) => {
    const configs = {
      small: {
        padding: '2px 8px',
        fontSize: '10px',
        iconSize: '12px',
        borderRadius: '12px'
      },
      medium: {
        padding: '4px 12px',
        fontSize: '12px',
        iconSize: '14px',
        borderRadius: '16px'
      },
      large: {
        padding: '6px 16px',
        fontSize: '14px',
        iconSize: '16px',
        borderRadius: '20px'
      }
    };
    return configs[size as keyof typeof configs] || configs.medium;
  };

  const tierConfig = getTierConfig(tier);
  const sizeConfig = getSizeConfig(size);

  const badgeStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: showText ? '6px' : '0',
    padding: sizeConfig.padding,
    background: tierConfig.gradient,
    color: tierConfig.color,
    border: `2px solid ${tierConfig.border}`,
    borderRadius: sizeConfig.borderRadius,
    fontSize: sizeConfig.fontSize,
    fontWeight: '700' as const,
    textTransform: 'uppercase' as const,
    cursor: onClick ? 'pointer' : 'default',
    transition: 'all 0.2s ease',
    userSelect: 'none' as const,
    ...(onClick && {
      ':hover': {
        transform: 'translateY(-1px)',
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
      }
    })
  };

  return (
    <div style={badgeStyle} onClick={onClick}>
      <span style={{ fontSize: sizeConfig.iconSize }}>{tierConfig.icon}</span>
      {showText && tierConfig.name}
    </div>
  );
};

export default SubscriptionBadge;