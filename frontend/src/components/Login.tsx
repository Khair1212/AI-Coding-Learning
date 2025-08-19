import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { theme } from '../styles/theme';
import Button from './common/Button';
import Input from './common/Input';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Invalid credentials');
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
        <h1 style={titleStyle}>Welcome Back</h1>
        <p style={subtitleStyle}>Sign in to your AI Learning account</p>
        
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
            type="password"
            placeholder="Enter your password"
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
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
        
        <div style={linkStyle}>
          <Link to="/forgot-password" style={linkTextStyle}>
            Forgot your password?
          </Link>
        </div>
        
        <div style={linkStyle}>
          Don't have an account?{' '}
          <Link to="/register" style={linkTextStyle}>
            Create one here
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;