import React, { useState } from 'react';
import Chatbot from './components/Chatbot';
import RoleSelector from './components/RoleSelector';
import { FaHospital, FaHeartbeat, FaShieldAlt } from 'react-icons/fa';
import './components/App.css';

function App() {
  const [userRole, setUserRole] = useState('general');
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [documentCount, setDocumentCount] = useState(0);

  // Check backend health on mount
  React.useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      setConnectionStatus(data.vector_db_status === 'healthy' ? 'connected' : 'empty');
      setDocumentCount(data.document_count);
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Backend connection failed:', error);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <FaHospital className="main-logo" />
            <div className="title-section">
              <h1>Healthcare Knowledge Assistant</h1>
              <p className="subtitle">AI-Powered Medical Information System</p>
            </div>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <FaHeartbeat className="stat-icon" />
              <div className="stat-info">
                <span className="stat-value">{documentCount}</span>
                <span className="stat-label">Documents</span>
              </div>
            </div>
            <div className="stat-item">
              <FaShieldAlt className="stat-icon" />
              <div className="stat-info">
                <span className={`stat-value status-${connectionStatus}`}>
                  {connectionStatus === 'connected' ? 'Online' : 
                   connectionStatus === 'empty' ? 'No Docs' : 'Offline'}
                </span>
                <span className="stat-label">Status</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="chatbot-container">
          <RoleSelector userRole={userRole} setUserRole={setUserRole} />
          <Chatbot userRole={userRole} />
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>⚠️ For medical emergencies, call 911 or visit Emergency Department</p>
        <p className="footer-note">This is an AI assistant for hospital policy information only</p>
      </footer>
    </div>
  );
}

export default App;
