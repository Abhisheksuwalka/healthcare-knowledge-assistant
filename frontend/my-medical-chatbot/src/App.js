import React, { useState } from 'react';
import { FaChevronDown, FaChevronRight, FaHeartbeat, FaHospital, FaLightbulb, FaShieldAlt } from 'react-icons/fa';
import './components/App.css';
import Chatbot from './components/Chatbot';
import RoleSelector from './components/RoleSelector';

// Role-specific question suggestions based on knowledge base analysis
const ROLE_QUESTIONS = {
  general: {
    faq: [
      "What are the visiting hours for ICU?",
      "How do I schedule a dental appointment?",
      "What documents do I need for admission?",
    ],
    medium: [
      "How much does a routine dental cleaning cost?",
      "What is the parking situation at the hospital?",
      "Is there a cafeteria in the hospital?",
    ],
    rare: [
      "Do you allow service animals?",
      "Is sign language interpretation available?",
      "Can family stay overnight with pediatric patients?",
    ],
    unrelated: [
      "What's the weather like today?",
      "Can you recommend a good restaurant?",
    ]
  },
  doctor: {
    faq: [
      "What are the ICU visiting restrictions?",
      "What is the pre-admission process for elective procedures?",
      "What advanced lab tests are available?",
    ],
    medium: [
      "What cardiac diagnostic tests are available?",
      "What is the turnaround time for MRI results?",
      "What are the isolation/quarantine visitor policies?",
    ],
    rare: [
      "What are the end-of-life care visiting policies?",
      "Is genetic testing available and what's the cost?",
      "What sleep study options are available?",
    ],
    unrelated: [
      "What's the stock market doing today?",
      "Can you help me book a flight?",
    ]
  },
  receptionist: {
    faq: [
      "What are the general visiting hours?",
      "What ID is required for visitor registration?",
      "What are the Admissions Office hours?",
    ],
    medium: [
      "Are interpreter services available?",
      "What is the dental clinic cancellation policy?",
      "Where is the Diagnostic Center located?",
    ],
    rare: [
      "Can emotional support animals visit?",
      "What are the pediatric sibling visiting rules?",
      "Is wheelchair access available throughout?",
    ],
    unrelated: [
      "What's the capital of France?",
      "Can you order me a pizza?",
    ]
  },
  billing: {
    faq: [
      "What insurance plans do you accept?",
      "Do you offer payment plans?",
      "What is the self-pay discount?",
    ],
    medium: [
      "How much does an MRI cost?",
      "What financial assistance is available?",
      "How do I dispute a charge?",
    ],
    rare: [
      "What is the medical records copy fee?",
      "Is there a charity care program?",
      "Do you offer CareCredit financing?",
    ],
    unrelated: [
      "Who won the game last night?",
      "What's a good investment strategy?",
    ]
  }
};

const CATEGORY_LABELS = {
  faq: { label: "Common Questions", icon: "💬" },
  medium: { label: "Detailed Inquiries", icon: "📋" },
  rare: { label: "Special Cases", icon: "🔍" },
  unrelated: { label: "Out of Scope", icon: "⚠️" }
};

function App() {
  const [userRole, setUserRole] = useState('general');
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [documentCount, setDocumentCount] = useState(0);
  const [expandedCategories, setExpandedCategories] = useState({ faq: true });
  const [pendingQuestion, setPendingQuestion] = useState(null);

  // Check backend health on mount
  React.useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    try {
      const response = await fetch(`${apiUrl}/health`);
      const data = await response.json();
      setConnectionStatus(data.vector_db_status === 'healthy' ? 'connected' : 'empty');
      setDocumentCount(data.document_count);
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Backend connection failed:', error);
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const handleQuestionClick = (question) => {
    setPendingQuestion(question);
  };

  const currentQuestions = ROLE_QUESTIONS[userRole] || ROLE_QUESTIONS.general;
  
  // Get quick suggestions for mobile (just FAQs)
  const mobileQuickSuggestions = currentQuestions.faq.slice(0, 3);

  return (
    <div className="app-layout">
      {/* Mobile Header - only visible on mobile */}
      <div className="mobile-header">
        <div className="mobile-logo">
          <FaHospital className="mobile-logo-icon" />
          <span className="mobile-logo-text">Healthcare AI</span>
        </div>
        <select 
          className="mobile-role-select"
          value={userRole}
          onChange={(e) => setUserRole(e.target.value)}
        >
          <option value="general">General</option>
          <option value="doctor">Doctor</option>
          <option value="receptionist">Receptionist</option>
          <option value="billing">Billing</option>
        </select>
      </div>
      
      {/* Mobile Quick Suggestions - only visible on mobile */}
      <div className="mobile-suggestions">
        {mobileQuickSuggestions.map((q, i) => (
          <button
            key={i}
            className="mobile-suggestion-chip"
            onClick={() => handleQuestionClick(q)}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Left Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <FaHospital className="sidebar-logo" />
          <span className="sidebar-title">Healthcare AI</span>
        </div>
        
        <div className="sidebar-section">
          <RoleSelector userRole={userRole} setUserRole={setUserRole} />
        </div>
        
        <div className="sidebar-stats">
          <div className="sidebar-stat">
            <FaHeartbeat className="sidebar-stat-icon" />
            <div className="sidebar-stat-info">
              <span className="sidebar-stat-value">{documentCount}</span>
              <span className="sidebar-stat-label">Documents</span>
            </div>
          </div>
          <div className="sidebar-stat">
            <FaShieldAlt className="sidebar-stat-icon" />
            <div className="sidebar-stat-info">
              <span className={`sidebar-stat-value status-${connectionStatus}`}>
                {connectionStatus === 'connected' ? 'Online' : 
                 connectionStatus === 'empty' ? 'No Docs' : 'Offline'}
              </span>
              <span className="sidebar-stat-label">Status</span>
            </div>
          </div>
        </div>
        
        <div className="sidebar-footer">
          <p>⚠️ For emergencies, call 911</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Chatbot userRole={userRole} pendingQuestion={pendingQuestion} onQuestionSent={() => setPendingQuestion(null)} />
      </main>

      {/* Right Sidebar - Suggestions */}
      <aside className="right-sidebar">
        <div className="suggestions-header">
          <FaLightbulb className="suggestions-icon" />
          <span>Try Asking</span>
        </div>
        
        <div className="suggestions-list">
          {Object.entries(currentQuestions).map(([category, questions]) => (
            <div key={category} className="suggestion-category">
              <button 
                className="category-toggle"
                onClick={() => toggleCategory(category)}
              >
                {expandedCategories[category] ? <FaChevronDown className="toggle-chevron" /> : <FaChevronRight className="toggle-chevron" />}
                <span className="category-icon">{CATEGORY_LABELS[category].icon}</span>
                <span className="category-label">{CATEGORY_LABELS[category].label}</span>
              </button>
              
              {expandedCategories[category] && (
                <div className="category-questions">
                  {questions.map((question, idx) => (
                    <button
                      key={idx}
                      className={`suggestion-btn ${category === 'unrelated' ? 'unrelated' : ''}`}
                      onClick={() => handleQuestionClick(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="right-sidebar-footer">
          <p className="emergency-notice">⚠️ For medical emergencies, call 911 or visit Emergency Department</p>
          <p className="ai-notice">This is an AI assistant for hospital policy information</p>
        </div>
      </aside>
    </div>
  );
}

export default App;
