import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { theme } from '../styles/theme';
import Button from './common/Button';
import Input from './common/Input';
import axios from 'axios';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [step, setStep] = useState<'email' | 'reset'>('email');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await axios.post(`${API_BASE_URL}/api/auth/forgot-password`, { email });
      setStep('reset');
      setSuccess('User found! Please enter your new password.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'User not found');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await axios.post(`${API_BASE_URL}/api/auth/reset-password`, {
        email,
        new_password: newPassword
      });
      setSuccess('Password has been reset successfully! You can now login with your new password.');
      setStep('email');
      setEmail('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  const containerStyle = {
    minHeight: '100vh',
    background: theme.colors.gradient,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px'
  };

  const cardStyle = {
    background: theme.colors.surface,
    padding: '40px',
    borderRadius: theme.borderRadius.xl,
    boxShadow: theme.shadows.xl,
    width: '100%',
    maxWidth: '400px'
  };

  const titleStyle = {
    fontSize: '28px',
    fontWeight: '700',
    color: theme.colors.text,
    textAlign: 'center' as const,
    marginBottom: '8px'
  };

  const subtitleStyle = {
    fontSize: '16px',
    color: theme.colors.textSecondary,
    textAlign: 'center' as const,
    marginBottom: '32px'
  };

  const errorStyle = {
    background: '#fef2f2',
    color: theme.colors.error,
    padding: '12px',
    borderRadius: theme.borderRadius.md,
    marginBottom: '16px',
    fontSize: '14px',
    textAlign: 'center' as const
  };

  const successStyle = {
    background: '#f0f9ff',
    color: theme.colors.primary,
    padding: '12px',
    borderRadius: theme.borderRadius.md,
    marginBottom: '16px',
    fontSize: '14px',
    textAlign: 'center' as const
  };

  const linkStyle = {
    textAlign: 'center' as const,
    marginTop: '24px',
    fontSize: '14px',
    color: theme.colors.textSecondary
  };

  const linkTextStyle = {
    color: theme.colors.primary,
    textDecoration: 'none',
    fontWeight: '500'
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h1 style={titleStyle}>
          {step === 'email' ? 'Forgot Password' : 'Reset Password'}
        </h1>
        <p style={subtitleStyle}>
          {step === 'email' 
            ? 'Enter your email to reset your password'
            : 'Enter your new password'
          }
        </p>
        
        {step === 'email' ? (
          <form onSubmit={handleEmailSubmit}>
            <Input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              label="Email"
              required
            />
            
            {error && <div style={errorStyle}>{error}</div>}
            {success && <div style={successStyle}>{success}</div>}
            
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              disabled={loading}
            >
              {loading ? 'Checking...' : 'Continue'}
            </Button>
          </form>
        ) : (
          <form onSubmit={handlePasswordReset}>
            <Input
              type="password"
              placeholder="Enter new password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              label="New Password"
              required
            />
            
            <Input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              label="Confirm Password"
              required
            />
            
            {error && <div style={errorStyle}>{error}</div>}
            {success && <div style={successStyle}>{success}</div>}
            
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              disabled={loading}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </form>
        )}
        
        <div style={linkStyle}>
          <Link to="/login" style={linkTextStyle}>
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;