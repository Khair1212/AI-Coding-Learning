import React from 'react';
import { theme } from '../../styles/theme';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  fullWidth?: boolean;
  style?: React.CSSProperties;
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  fullWidth = false,
  style
}) => {
  const baseStyles = {
    border: 'none',
    borderRadius: theme.borderRadius.md,
    fontWeight: '500',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease-in-out',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: fullWidth ? '100%' : 'auto',
    opacity: disabled ? 0.6 : 1
  };

  const variants = {
    primary: {
      background: theme.colors.primary,
      color: 'white',
      boxShadow: theme.shadows.sm,
      ':hover': {
        background: theme.colors.primaryHover,
        boxShadow: theme.shadows.md
      }
    },
    secondary: {
      background: theme.colors.secondary,
      color: 'white',
      boxShadow: theme.shadows.sm
    },
    outline: {
      background: 'transparent',
      color: theme.colors.primary,
      border: `1px solid ${theme.colors.border}`
    }
  };

  const sizes = {
    sm: { padding: '8px 12px', fontSize: '14px' },
    md: { padding: '10px 16px', fontSize: '16px' },
    lg: { padding: '12px 20px', fontSize: '18px' }
  };

  const buttonStyle = {
    ...baseStyles,
    ...variants[variant],
    ...sizes[size],
    ...style
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={buttonStyle}
      onMouseEnter={(e) => {
        if (!disabled && variant === 'primary') {
          e.currentTarget.style.background = theme.colors.primaryHover;
          e.currentTarget.style.boxShadow = theme.shadows.md;
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled && variant === 'primary') {
          e.currentTarget.style.background = theme.colors.primary;
          e.currentTarget.style.boxShadow = theme.shadows.sm;
        }
      }}
    >
      {children}
    </button>
  );
};

export default Button;