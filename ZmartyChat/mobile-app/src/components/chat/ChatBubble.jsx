import React from 'react';

const ChatBubble = ({ message }) => {
  return (
    <div className={`chat-bubble ${message.sender}`}>
      <div className='bubble-content'>
        {message.content}
      </div>
      <div className='bubble-time'>
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
};

export default ChatBubble;
