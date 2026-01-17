import axios from 'axios';
import { useEffect, useRef, useState } from 'react';
import { FaPaperPlane, FaRobot, FaSpinner } from 'react-icons/fa';
import Message from './Message';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Chatbot({ userRole, pendingQuestion, onQuestionSent }) {
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

  // Handle pending question from suggestions - just fill input, don't auto-send
  useEffect(() => {
    if (pendingQuestion) {
      setInput(pendingQuestion);
      onQuestionSent && onQuestionSent();
    }
  }, [pendingQuestion]);

  const sendMessageWithText = async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      sender: 'user',
      text: text,
      timestamp: new Date()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    // Build chat history for context (exclude initial bot greeting, limit to recent messages)
    const chatHistory = updatedMessages
      .slice(1) // Skip the initial greeting
      .slice(-10) // Last 10 messages max
      .map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

    try {
      const response = await axios.post(`${API_URL}/query`, {
        question: text,
        user_role: userRole,
        include_sources: true,
        chat_history: chatHistory.length > 0 ? chatHistory : null
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

  const sendMessage = async () => {
    await sendMessageWithText(input);
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
          {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
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
          Press Enter to send
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
