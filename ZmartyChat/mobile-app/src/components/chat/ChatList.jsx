/**
 * ChatList - WhatsApp-style chat list component
 * Shows all available chat channels and trading features
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatList.css';

const ChatList = ({ onChatSelect, onNavigate, user, notifications, isConnected }) => {
  const [unreadCounts, setUnreadCounts] = useState({});
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Update unread counts from notifications
    const counts = {};
    notifications.forEach(notification => {
      const chatId = getChatIdFromNotification(notification);
      counts[chatId] = (counts[chatId] || 0) + 1;
    });
    setUnreadCounts(counts);
  }, [notifications]);

  const getChatIdFromNotification = (notification) => {
    switch (notification.type) {
      case 'whale_alert':
        return 'whale-alerts';
      case 'pattern_trigger':
        return 'pattern-alerts';
      case 'market_alert':
        return 'market-news';
      default:
        return 'zmarty-ai';
    }
  };

  const chatChannels = [
    {
      id: 'zmarty-ai',
      type: 'ai',
      title: '🤖 Zmarty AI',
      subtitle: isConnected ? 'Online - Ask me anything!' : 'Connecting...',
      lastMessage: 'Ready to analyze the crypto markets for you! 🚀',
      timestamp: Date.now() - 120000, // 2 min ago
      avatar: '🤖',
      badge: '🔥',
      priority: 1
    },
    {
      id: 'whale-alerts',
      type: 'whale',
      title: '🐋 Whale Alerts',
      subtitle: 'Large transaction monitoring',
      lastMessage: '50M USDT moved from Binance cold wallet',
      timestamp: Date.now() - 300000, // 5 min ago
      avatar: '🐋',
      badge: '📢',
      priority: 2
    },
    {
      id: 'pattern-alerts',
      type: 'pattern',
      title: '⚡ Pattern Alerts',
      subtitle: 'Technical analysis signals',
      lastMessage: 'Golden Cross detected on ETH/USDT',
      timestamp: Date.now() - 720000, // 12 min ago
      avatar: '⚡',
      badge: '📊',
      priority: 3
    },
    {
      id: 'market-news',
      type: 'news',
      title: '📰 Market Intelligence',
      subtitle: 'Latest crypto news & analysis',
      lastMessage: 'Fed meeting impacts crypto volatility',
      timestamp: Date.now() - 1200000, // 20 min ago
      avatar: '📰',
      badge: '📱',
      priority: 4
    },
    {
      id: 'commission-tracker',
      type: 'commission',
      title: '💰 Earnings Tracker',
      subtitle: 'Your commission updates',
      lastMessage: `You earned $${user?.todayEarnings || '12.50'} today!`,
      timestamp: Date.now() - 3600000, // 1 hour ago
      avatar: '💰',
      badge: '💎',
      priority: 5
    }
  ];

  const quickActions = [
    {
      id: 'portfolio',
      title: '📊 Portfolio',
      description: 'View your crypto holdings',
      icon: '📊',
      color: '#3b82f6',
      action: () => onNavigate('portfolio')
    },
    {
      id: 'hot-coins',
      title: '🔥 Hot Coins',
      description: 'Trending cryptocurrencies',
      icon: '🔥',
      color: '#ef4444',
      action: () => onChatSelect('ai', 'hot-coins')
    },
    {
      id: 'whale-hunt',
      title: '🐋 Whale Hunt',
      description: 'Track large movements',
      icon: '🐋',
      color: '#06b6d4',
      action: () => onNavigate('whale-alerts')
    },
    {
      id: 'earn-now',
      title: '💰 Earn Now',
      description: 'Share & earn commissions',
      icon: '💰',
      color: '#10b981',
      action: () => onNavigate('earnings')
    }
  ];

  const formatTime = (timestamp) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'now';
    if (minutes < 60) return `${minutes}m`;
    if (hours < 24) return `${hours}h`;
    return `${days}d`;
  };

  const filteredChats = chatChannels.filter(chat =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    chat.subtitle.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="chat-list">
      {/* Header */}
      <div className="chat-list-header">
        <div className="header-title">
          <h1>💰 ZmartyChat</h1>
          <span className="connection-indicator">
            {isConnected ? '🟢' : '🔴'}
          </span>
        </div>
        <div className="header-actions">
          <button className="header-btn" onClick={() => onNavigate('portfolio')}>
            📊
          </button>
          <button className="header-btn notification-btn" onClick={() => onNavigate('notifications')}>
            🔔
            {notifications.length > 0 && (
              <span className="notification-badge">{notifications.length}</span>
            )}
          </button>
          <button className="header-btn" onClick={() => onNavigate('settings')}>
            ⚙️
          </button>
        </div>
      </div>

      {/* User Stats Bar */}
      <div className="user-stats-bar">
        <div className="stat">
          <span className="stat-label">Credits</span>
          <span className="stat-value">{user?.credits || 100}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Streak</span>
          <span className="stat-value">🔥 {user?.streak || 5}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Earned Today</span>
          <span className="stat-value">${user?.todayEarnings || '12.50'}</span>
        </div>
      </div>

      {/* Search */}
      <div className="search-container">
        <input
          type="text"
          placeholder="🔍 Search chats..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-section">
        <h3 className="section-title">🚀 Quick Actions</h3>
        <div className="quick-actions-grid">
          {quickActions.map((action) => (
            <motion.button
              key={action.id}
              className="quick-action-card"
              style={{ '--action-color': action.color }}
              onClick={action.action}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="action-icon">{action.icon}</div>
              <div className="action-info">
                <div className="action-title">{action.title}</div>
                <div className="action-description">{action.description}</div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Chat Channels */}
      <div className="chats-section">
        <h3 className="section-title">💬 Chats</h3>
        <div className="chat-channels">
          <AnimatePresence>
            {filteredChats.map((chat) => (
              <motion.div
                key={chat.id}
                className="chat-item"
                onClick={() => onChatSelect(chat.type, chat.id)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
                whileTap={{ scale: 0.98 }}
              >
                {/* Avatar */}
                <div className="chat-avatar">
                  <span className="avatar-emoji">{chat.avatar}</span>
                  {chat.badge && (
                    <span className="chat-badge">{chat.badge}</span>
                  )}
                </div>

                {/* Chat Info */}
                <div className="chat-info">
                  <div className="chat-header">
                    <h4 className="chat-title">{chat.title}</h4>
                    <span className="chat-time">{formatTime(chat.timestamp)}</span>
                  </div>
                  <div className="chat-preview">
                    <p className="chat-subtitle">{chat.subtitle}</p>
                    <p className="last-message">{chat.lastMessage}</p>
                  </div>
                </div>

                {/* Unread Count */}
                {unreadCounts[chat.id] > 0 && (
                  <div className="unread-count">
                    {unreadCounts[chat.id] > 99 ? '99+' : unreadCounts[chat.id]}
                  </div>
                )}

                {/* Online Indicator */}
                {chat.id === 'zmarty-ai' && (
                  <div className={`online-indicator ${isConnected ? 'online' : 'offline'}`} />
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Viral Growth Prompt */}
      <motion.div
        className="viral-growth-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="viral-card-content">
          <div className="viral-icon">🚀</div>
          <div className="viral-info">
            <h4>Earn ${((user?.commissionRate || 0.05) * 100).toFixed(0)}% Commission!</h4>
            <p>Share ZmartyChat with friends and earn from their subscriptions</p>
          </div>
          <button
            className="viral-cta-btn"
            onClick={() => onNavigate('earnings')}
          >
            Start Earning
          </button>
        </div>
      </motion.div>

      {/* Version Info */}
      <div className="version-info">
        <p>ZmartyChat Mobile v1.0.0</p>
        <p>Powered by 4 AI Providers 🤖</p>
      </div>
    </div>
  );
};

export default ChatList;