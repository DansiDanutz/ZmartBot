/**
 * ZmartyChat Mobile App - Main App Component
 * WhatsApp-style crypto trading companion with multi-provider AI
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ChatList from './components/chat/ChatList';
import ChatInterface from './components/chat/ChatInterface';
import PortfolioView from './components/trading/PortfolioView';
import WhaleAlerts from './components/trading/WhaleAlerts';
import EarningsTracker from './components/social/EarningsTracker';
import Settings from './components/Settings';
import NotificationManager from './components/NotificationManager';
import zmartyAI from './services/ZmartyAIService';
import './App.css';

const App = () => {
  const [currentView, setCurrentView] = useState('chat-list');
  const [activeChat, setActiveChat] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [user, setUser] = useState(null);

  useEffect(() => {
    initializeApp();

    // Set up global event listeners
    zmartyAI.on('connection', handleConnection);
    zmartyAI.on('market_alert', handleMarketAlert);
    zmartyAI.on('whale_alert', handleWhaleAlert);
    zmartyAI.on('pattern_trigger', handlePatternTrigger);
    zmartyAI.on('show_notification', handleNotification);

    return () => {
      zmartyAI.off('connection', handleConnection);
      zmartyAI.off('market_alert', handleMarketAlert);
      zmartyAI.off('whale_alert', handleWhaleAlert);
      zmartyAI.off('pattern_trigger', handlePatternTrigger);
      zmartyAI.off('show_notification', handleNotification);
    };
  }, []);

  const initializeApp = async () => {
    // Load user data from localStorage
    const userData = localStorage.getItem('zmartychat_user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Initialize demo user
      const demoUser = {
        id: 'demo_user',
        name: 'Demo User',
        avatar: '👤',
        credits: 100,
        streak: 5,
        commissionRate: 0.05,
        totalEarned: 127.50
      };
      setUser(demoUser);
      localStorage.setItem('zmartychat_user', JSON.stringify(demoUser));
    }

    // Request notification permissions
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  };

  const handleConnection = (data) => {
    setIsConnected(data.status === 'connected');
  };

  const handleMarketAlert = (alert) => {
    addNotification({
      ...alert,
      type: 'market_alert',
      timestamp: Date.now()
    });
  };

  const handleWhaleAlert = (alert) => {
    addNotification({
      ...alert,
      type: 'whale_alert',
      timestamp: Date.now()
    });
  };

  const handlePatternTrigger = (alert) => {
    addNotification({
      ...alert,
      type: 'pattern_trigger',
      timestamp: Date.now()
    });
  };

  const handleNotification = (notification) => {
    addNotification({
      ...notification,
      timestamp: Date.now()
    });
  };

  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep last 50

    // Auto-remove after 5 seconds for non-urgent notifications
    if (notification.priority !== 'urgent') {
      setTimeout(() => {
        removeNotification(notification.id || notification.timestamp);
      }, 5000);
    }
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => (n.id || n.timestamp) !== id));
  };

  const openChat = (chatType, chatId) => {
    setActiveChat({ type: chatType, id: chatId });
    setCurrentView('chat');
  };

  const goBack = () => {
    if (currentView === 'chat') {
      setCurrentView('chat-list');
      setActiveChat(null);
    }
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'chat':
        return (
          <ChatInterface
            chatType={activeChat?.type || 'ai'}
            chatId={activeChat?.id || 'zmarty-ai'}
            onBack={goBack}
          />
        );

      case 'portfolio':
        return <PortfolioView user={user} onBack={() => setCurrentView('chat-list')} />;

      case 'whale-alerts':
        return <WhaleAlerts onBack={() => setCurrentView('chat-list')} />;

      case 'earnings':
        return <EarningsTracker user={user} onBack={() => setCurrentView('chat-list')} />;

      case 'settings':
        return <Settings user={user} onBack={() => setCurrentView('chat-list')} />;

      default:
        return (
          <ChatList
            onChatSelect={openChat}
            onNavigate={setCurrentView}
            user={user}
            notifications={notifications}
            isConnected={isConnected}
          />
        );
    }
  };

  return (
    <div className="app">
      <div className="app-container">
        {renderCurrentView()}
      </div>

      {/* Notification Manager */}
      <NotificationManager
        notifications={notifications}
        onNotificationClick={(notification) => {
          // Handle notification click based on type
          if (notification.type === 'whale_alert') {
            setCurrentView('whale-alerts');
          } else if (notification.type === 'pattern_trigger') {
            openChat('pattern', 'pattern-alerts');
          } else if (notification.type === 'market_alert') {
            openChat('ai', 'zmarty-ai');
          }
          removeNotification(notification.id || notification.timestamp);
        }}
        onNotificationDismiss={removeNotification}
      />

      {/* Connection Status */}
      {!isConnected && (
        <div className="connection-status offline">
          🔄 Connecting to ZmartyAI...
        </div>
      )}

      {/* PWA Install Prompt */}
      <div className="pwa-install-prompt" id="pwa-install-prompt">
        <div className="pwa-prompt-content">
          <h3>📱 Install ZmartyChat</h3>
          <p>Get the best experience with our mobile app!</p>
          <div className="pwa-prompt-actions">
            <button className="pwa-install-btn" id="pwa-install-btn">
              Install App
            </button>
            <button className="pwa-dismiss-btn" id="pwa-dismiss-btn">
              Not Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;