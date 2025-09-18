/**
 * ChatInterface - Main WhatsApp-style chat component
 * Integrates with ZmartyAI backend and provides mobile-optimized experience
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import zmartyAI from '../../services/ZmartyAIService';
import ChatBubble from './ChatBubble';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import QuickActions from './QuickActions';
import './ChatInterface.css';

const ChatInterface = ({ chatType = 'ai', chatId = 'zmarty-ai' }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentProvider, setCurrentProvider] = useState('grok');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize chat with welcome message
    initializeChat();

    // Set up AI service listeners
    zmartyAI.on('ai_response', handleAIResponse);
    zmartyAI.on('connection', handleConnection);
    zmartyAI.on('typing', handleTyping);

    return () => {
      zmartyAI.off('ai_response', handleAIResponse);
      zmartyAI.off('connection', handleConnection);
      zmartyAI.off('typing', handleTyping);
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = () => {
    const welcomeMessage = {
      id: 'welcome-1',
      content: "🤖 Hey! I'm Zmarty, your AI crypto companion. Ask me about any cryptocurrency, market trends, or get real-time trading insights!",
      sender: 'ai',
      timestamp: Date.now(),
      provider: 'grok',
      actions: [
        { type: 'quick_ask', label: '📊 BTC Analysis' },
        { type: 'quick_ask', label: '🔥 Hot Coins' },
        { type: 'quick_ask', label: '🐋 Whale Activity' }
      ]
    };
    setMessages([welcomeMessage]);
  };

  const handleConnection = (data) => {
    setIsConnected(data.status === 'connected');
  };

  const handleTyping = (data) => {
    setIsTyping(data.isTyping);
  };

  const handleAIResponse = (response) => {
    setIsTyping(false);

    const aiMessage = {
      id: `ai-${Date.now()}`,
      content: response.displayContent || response.content,
      fullContent: response.fullContent,
      sender: 'ai',
      timestamp: Date.now(),
      provider: response.provider,
      isExpandable: response.isExpandable,
      actions: response.actions || [],
      metadata: response.metadata || {}
    };

    setMessages(prev => [...prev, aiMessage]);
  };

  const handleSendMessage = async (messageText, options = {}) => {
    // Add user message to chat
    const userMessage = {
      id: `user-${Date.now()}`,
      content: messageText,
      sender: 'user',
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Send to AI service
    try {
      const response = await zmartyAI.sendMessage(messageText, {
        ...options,
        chatType,
        chatId
      });

      if (response.error) {
        handleAIResponse({
          content: response.content,
          provider: 'system',
          actions: response.actions
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);

      // Show error message
      const errorMessage = {
        id: `error-${Date.now()}`,
        content: "🤖 Sorry, I'm having trouble connecting. Please try again!",
        sender: 'ai',
        timestamp: Date.now(),
        provider: 'system',
        isError: true,
        actions: [
          { type: 'retry', label: '🔄 Retry' },
          { type: 'support', label: '💬 Help' }
        ]
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleQuickAction = (action) => {
    switch (action.type) {
      case 'quick_ask':
        handleQuickAsk(action.label);
        break;
      case 'view_chart':
        openChart(action.symbol);
        break;
      case 'set_alert':
        openAlertSetup(action.symbol);
        break;
      case 'share':
        shareMessage(action.messageId);
        break;
      case 'retry':
        retryLastMessage();
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const handleQuickAsk = (query) => {
    const queries = {
      '📊 BTC Analysis': 'Give me a quick BTC analysis with current price and trend',
      '🔥 Hot Coins': 'What are the top 3 trending coins right now?',
      '🐋 Whale Activity': 'Any recent whale movements I should know about?'
    };

    const messageText = queries[query] || query;
    handleSendMessage(messageText);
  };

  const openChart = (symbol) => {
    // Open chart view
    console.log('Opening chart for:', symbol);
    // This would navigate to chart component
  };

  const openAlertSetup = (symbol) => {
    // Open alert setup
    console.log('Setting up alert for:', symbol);
    // This would open alert configuration modal
  };

  const shareMessage = (messageId) => {
    // Share functionality
    console.log('Sharing message:', messageId);
    // This would open share dialog
  };

  const retryLastMessage = () => {
    const lastUserMessage = [...messages].reverse().find(m => m.sender === 'user');
    if (lastUserMessage) {
      handleSendMessage(lastUserMessage.content);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatChatHeader = () => {
    const headers = {
      'ai': {
        title: '🤖 Zmarty AI',
        subtitle: isConnected ? `Powered by ${currentProvider.toUpperCase()}` : 'Connecting...',
        status: isConnected ? 'online' : 'offline'
      },
      'whale': {
        title: '🐋 Whale Alerts',
        subtitle: 'Large transaction monitoring',
        status: 'active'
      },
      'pattern': {
        title: '⚡ Pattern Alerts',
        subtitle: 'Technical analysis signals',
        status: 'active'
      },
      'news': {
        title: '📰 Market News',
        subtitle: 'Latest crypto intelligence',
        status: 'active'
      }
    };

    return headers[chatType] || headers.ai;
  };

  const header = formatChatHeader();

  return (
    <div className="chat-interface">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="header-info">
          <h2 className="chat-title">{header.title}</h2>
          <p className="chat-subtitle">{header.subtitle}</p>
        </div>
        <div className="header-actions">
          <button className="header-btn" onClick={() => console.log('Portfolio')}>
            📊
          </button>
          <button className="header-btn" onClick={() => console.log('Voice')}>
            📞
          </button>
          <button className="header-btn" onClick={() => console.log('Settings')}>
            ⚙️
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ChatBubble
                message={message}
                onActionClick={handleQuickAction}
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <TypingIndicator provider={currentProvider} />
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <QuickActions
        chatType={chatType}
        onActionClick={handleQuickAction}
        isVisible={messages.length <= 1} // Show for new chats
      />

      {/* Message Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        isConnected={isConnected}
        placeholder={`Message ${header.title}...`}
      />
    </div>
  );
};

export default ChatInterface;