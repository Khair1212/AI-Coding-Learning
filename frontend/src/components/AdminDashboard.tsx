import React from 'react';
import { useAuth } from '../context/AuthContext';

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div style={{ padding: '20px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Admin Dashboard</h1>
        <div>
          <span style={{ marginRight: '15px' }}>Welcome, {user?.username}!</span>
          <button onClick={logout} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}>
            Logout
          </button>
        </div>
      </header>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>User Management</h3>
          <p>Manage registered users</p>
          <button style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none' }}>
            View Users
          </button>
        </div>
        
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>Question Management</h3>
          <p>Configure AI question generation</p>
          <button style={{ padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none' }}>
            Manage Questions
          </button>
        </div>
        
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>Analytics</h3>
          <p>View platform statistics</p>
          <button style={{ padding: '10px 20px', backgroundColor: '#ffc107', color: 'black', border: 'none' }}>
            View Analytics
          </button>
        </div>
        
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>System Settings</h3>
          <p>Configure platform settings</p>
          <button style={{ padding: '10px 20px', backgroundColor: '#6c757d', color: 'white', border: 'none' }}>
            Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;