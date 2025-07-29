import React from 'react';
import { useLocation } from 'react-router-dom';

const DebugInfo: React.FC = () => {
  const location = useLocation();
  
  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '5px',
      fontSize: '12px',
      zIndex: 9999
    }}>
      <div>Current Route: {location.pathname}</div>
      <div>Assessment Available: {window.location.origin}/assessment</div>
      <div>Backend Health: <span id="backend-status">Checking...</span></div>
    </div>
  );
};

export default DebugInfo;