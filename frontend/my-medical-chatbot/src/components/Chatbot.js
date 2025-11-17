import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import { FaPaperPlane, FaRobot, FaSpinner } from 'react-icons/fa';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function Chatbot({ userRole }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I\'m your Healthcare Knowledge Assistant. Ask me anything about hospital policies, procedures, billing, or services. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      sender: 'user',
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/query`, {
        question: input,
        user_role: userRole,
        include_sources: true
      });

      const botMessage = {
        sender: 'bot',
        text: response.data.answer,
        sources: response.data.sources,
        disclaimer: response.data.disclaimer,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'bot',
        text: '❌ Sorry, I encountered an error. Please make sure the backend server is running on port 8000.',
        isError: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const exampleQuestions = [
    "What are the visiting hours for ICU?",
    "How do I schedule a dental appointment?",
    "What insurance plans do you accept?",
    "What documents are needed for admission?"
  ];

  const handleExampleClick = (question) => {
    setInput(question);
  };

  return (
    <div className="chatbot-card">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <FaRobot className="chat-bot-icon" />
          <div>
            <h3>Medical Assistant</h3>
            <span className="chat-status">● Online</span>
          </div>
        </div>
        <div className="chat-role-badge">
          Role: {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 1 && (
          <div className="example-questions">
            <p className="example-title">Try asking:</p>
            <div className="example-grid">
              {exampleQuestions.map((q, i) => (
                <button
                  key={i}
                  className="example-button"
                  onClick={() => handleExampleClick(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <Message key={index} message={msg} />
        ))}

        {isLoading && (
          <div className="loading-indicator">
            <FaSpinner className="spinner" />
            <span>Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-container">
        <div className="input-wrapper">
          <textarea
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about hospital policies, procedures, billing..."
            rows="1"
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
          >
            <FaPaperPlane />
          </button>
        </div>
        <div className="input-hint">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
