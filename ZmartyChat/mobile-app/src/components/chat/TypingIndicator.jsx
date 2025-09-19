import React from 'react';

const TypingIndicator = ({ isTyping }) => {
  if (!isTyping) return null;

  return (
    <div className="typing-indicator">
      <div className="typing-dots">
        <span className="dot"></span>
        <span className="dot"></span>
        <span className="dot"></span>
      </div>
      <span className="typing-text">Zmarty is typing...</span>
    </div>
  );
};

export default TypingIndicator;