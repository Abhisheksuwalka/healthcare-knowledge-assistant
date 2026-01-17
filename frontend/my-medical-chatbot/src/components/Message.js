import { useState } from 'react';
import { FaChevronDown, FaChevronRight, FaExclamationTriangle, FaFileAlt, FaRobot, FaUser } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

function Message({ message }) {
  const { sender, text, sources, disclaimer, isError, timestamp } = message;
  const [sourcesOpen, setSourcesOpen] = useState(false);

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`message ${sender}`}>
      <div className="message-avatar">
        {sender === 'bot' ? (
          <FaRobot className="avatar-icon bot-avatar" />
        ) : (
          <FaUser className="avatar-icon user-avatar" />
        )}
      </div>

      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">
            {sender === 'bot' ? 'Healthcare Assistant' : 'You'}
          </span>
          <span className="message-time">{formatTime(timestamp)}</span>
        </div>

        <div className={`message-text ${isError ? 'error-message' : ''}`}>
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>

        {/* Sources Section - Collapsible Dropdown */}
        {sources && sources.length > 0 && (
          <div className="message-sources">
            <button 
              className="sources-toggle"
              onClick={() => setSourcesOpen(!sourcesOpen)}
            >
              {sourcesOpen ? <FaChevronDown className="toggle-icon" /> : <FaChevronRight className="toggle-icon" />}
              <FaFileAlt className="sources-icon" />
              <span>Sources ({sources.length})</span>
            </button>
            
            {sourcesOpen && (
              <div className="sources-list">
                {sources.map((source, index) => (
                  <div key={index} className="source-item">
                    <div className="source-name">
                      📄 {source.filename}
                      <span className="source-chunk">Chunk {source.chunk_index}</span>
                    </div>
                    <div className="source-preview">{source.content_preview}</div>
                    <div className="source-score">
                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Disclaimer Section */}
        {disclaimer && (
          <div className="message-disclaimer">
            <FaExclamationTriangle className="disclaimer-icon" />
            <span>{disclaimer}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;
