import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { theme } from '../styles/theme';
import Button from './common/Button';
import Input from './common/Input';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await register(email, username, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
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
    background: '#f0fdf4',
    color: theme.colors.success,
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

  if (success) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <h1 style={titleStyle}>Account Created!</h1>
          <div style={successStyle}>
            Registration successful! Redirecting to login...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h1 style={titleStyle}>Create Account</h1>
        <p style={subtitleStyle}>Join AI Learning platform today</p>
        
        <form onSubmit={handleSubmit}>
          <Input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            label="Email"
            required
          />
          
          <Input
            type="text"
            placeholder="Choose a username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            label="Username"
            required
          />
          
          <Input
            type="password"
            placeholder="Create a password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            label="Password"
            required
          />
          
          {error && <div style={errorStyle}>{error}</div>}
          
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </form>
        
        <div style={linkStyle}>
          Already have an account?{' '}
          <Link to="/login" style={linkTextStyle}>
            Sign in here
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;