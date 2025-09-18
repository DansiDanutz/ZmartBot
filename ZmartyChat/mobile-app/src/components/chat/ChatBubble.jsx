/**
 * ChatBubble - WhatsApp-style message bubble component
 * Handles both user and AI messages with mobile optimization
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import './ChatBubble.css';

const ChatBubble = ({ message, onActionClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isActionsVisible, setIsActionsVisible] = useState(false);

  const {
    id,
    content,
    fullContent,
    sender,
    timestamp,
    provider,
    isExpandable,
    actions = [],
    metadata = {},
    isError = false
  } = message;

  const isAI = sender === 'ai';
  const displayContent = isExpanded ? fullContent : content;

  const handleExpand = () => {
    if (isExpandable) {
      setIsExpanded(!isExpanded);
    }
  };

  const handleActionClick = (action) => {
    onActionClick({ ...action, messageId: id });
  };

  const getProviderIcon = (provider) => {
    const icons = {
      'openai': '🧠',
      'claude': '🤖',
      'grok': '🚀',
      'gemini': '💎',
      'system': '⚙️'
    };
    return icons[provider] || '🤖';
  };

  const getProviderColor = (provider) => {
    const colors = {
      'openai': '#10a37f',
      'claude': '#d97757',
      'grok': '#1da1f2',
      'gemini': '#4285f4',
      'system': '#6b7280'
    };
    return colors[provider] || '#1f2937';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatContent = (text) => {
    // Convert crypto symbols to clickable elements
    const cryptoRegex = /\b(BTC|ETH|ADA|SOL|DOGE|XRP|DOT|LINK|UNI|MATIC|AVAX|ATOM|NEAR|FTM|ALGO|MANA|SAND|AXS|APE|CRO|LRC|IMX|GMT|STEPN|STX|ROSE|GALA|CHZ|ENJ|HBAR|VET|ONE|THETA|TFUEL|FIL|AR|STORJ|HOT|BTT|TRX|JST|SUN|USDT|USDC|BUSD|DAI|TUSD|USDP|FRAX|LUSD|SUSD|FEI|TRIBE|RAI|ALUSD|OUSD|DUSD|NUSD|PUSD|MUSD|ZUSD)\b/g;

    return text.replace(cryptoRegex, (match) => {
      return `<span class="crypto-symbol" data-symbol="${match}">${match}</span>`;
    });
  };

  return (
    <div className={`chat-bubble-container ${isAI ? 'ai-message' : 'user-message'}`}>
      <motion.div
        className={`chat-bubble ${isAI ? 'ai-bubble' : 'user-bubble'} ${isError ? 'error-bubble' : ''}`}
        layout
        transition={{ duration: 0.3 }}
        onClick={handleExpand}
      >
        {/* AI Provider Icon */}
        {isAI && provider && (
          <div
            className="provider-icon"
            style={{ backgroundColor: getProviderColor(provider) }}
          >
            {getProviderIcon(provider)}
          </div>
        )}

        {/* Message Content */}
        <div className="message-content">
          <div
            className="message-text"
            dangerouslySetInnerHTML={{ __html: formatContent(displayContent) }}
          />

          {/* Expand/Collapse Button */}
          {isExpandable && (
            <button className="expand-button" onClick={handleExpand}>
              {isExpanded ? 'Show less' : 'Read more...'}
            </button>
          )}

          {/* Message Metadata */}
          {metadata.confidence && (
            <div className="metadata">
              <span className="confidence-score">
                Confidence: {Math.round(metadata.confidence * 100)}%
              </span>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <div className="message-time">
          {formatTime(timestamp)}
          {isAI && provider && (
            <span className="provider-badge">
              {provider.toUpperCase()}
            </span>
          )}
        </div>

        {/* Read Receipts for User Messages */}
        {!isAI && (
          <div className="message-status">
            <span className="check-mark">✓✓</span>
          </div>
        )}
      </motion.div>

      {/* Action Buttons */}
      {actions.length > 0 && (
        <motion.div
          className="message-actions"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {actions.map((action, index) => (
            <button
              key={index}
              className={`action-button ${action.type}`}
              onClick={() => handleActionClick(action)}
            >
              {action.label}
            </button>
          ))}
        </motion.div>
      )}

      {/* Interactive Elements */}
      {metadata.chart && (
        <div className="embedded-chart">
          {/* Mini chart component would go here */}
          <div className="chart-placeholder">
            📊 Chart: {metadata.chart.symbol} - {metadata.chart.timeframe}
          </div>
        </div>
      )}

      {metadata.price && (
        <div className="price-ticker">
          <span className="symbol">{metadata.price.symbol}</span>
          <span className="price">${metadata.price.current}</span>
          <span className={`change ${metadata.price.change >= 0 ? 'positive' : 'negative'}`}>
            {metadata.price.change >= 0 ? '+' : ''}{metadata.price.change}%
          </span>
        </div>
      )}
    </div>
  );
};

export default ChatBubble;