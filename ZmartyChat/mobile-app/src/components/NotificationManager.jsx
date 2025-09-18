/**
 * NotificationManager - Real-time notification system for mobile
 * Handles in-app notifications with proper security and user experience
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './NotificationManager.css';

const NotificationManager = ({
  notifications = [],
  onNotificationClick,
  onNotificationDismiss,
  maxVisible = 3,
  autoHideDuration = 5000
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const timeoutsRef = useRef(new Map());

  useEffect(() => {
    // Process new notifications
    const newNotifications = notifications
      .filter(notification => !visibleNotifications.find(v => v.id === notification.id))
      .slice(0, maxVisible);

    if (newNotifications.length > 0) {
      setVisibleNotifications(prev => {
        const updated = [...newNotifications, ...prev].slice(0, maxVisible);

        // Set auto-hide timers for new notifications
        newNotifications.forEach(notification => {
          if (notification.priority !== 'urgent' && !notification.persistent) {
            scheduleAutoHide(notification);
          }
        });

        return updated;
      });
    }
  }, [notifications, maxVisible]);

  useEffect(() => {
    // Cleanup timers on unmount
    return () => {
      timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
      timeoutsRef.current.clear();
    };
  }, []);

  const scheduleAutoHide = (notification) => {
    if (timeoutsRef.current.has(notification.id)) {
      clearTimeout(timeoutsRef.current.get(notification.id));
    }

    const timeout = setTimeout(() => {
      if (!isPaused) {
        hideNotification(notification.id);
      }
    }, autoHideDuration);

    timeoutsRef.current.set(notification.id, timeout);
  };

  const hideNotification = (notificationId) => {
    setVisibleNotifications(prev =>
      prev.filter(n => n.id !== notificationId)
    );

    // Clear timeout
    if (timeoutsRef.current.has(notificationId)) {
      clearTimeout(timeoutsRef.current.get(notificationId));
      timeoutsRef.current.delete(notificationId);
    }

    // Call dismiss callback
    if (onNotificationDismiss) {
      onNotificationDismiss(notificationId);
    }
  };

  const handleNotificationClick = (notification) => {
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
    hideNotification(notification.id);
  };

  const handleMouseEnter = () => {
    setIsPaused(true);
    // Pause all auto-hide timers
    timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
  };

  const handleMouseLeave = () => {
    setIsPaused(false);
    // Resume auto-hide timers for non-urgent notifications
    visibleNotifications.forEach(notification => {
      if (notification.priority !== 'urgent' && !notification.persistent) {
        scheduleAutoHide(notification);
      }
    });
  };

  const getNotificationIcon = (type, priority) => {
    const iconMap = {
      whale_alert: '🐋',
      pattern_trigger: '⚡',
      market_alert: '📊',
      ai_response: '🤖',
      system: '⚙️',
      security: '🔒',
      error: '❌',
      warning: '⚠️',
      success: '✅',
      info: 'ℹ️'
    };

    const priorityIcons = {
      urgent: '🚨',
      high: '🔥',
      medium: '📢',
      low: '💬'
    };

    return iconMap[type] || priorityIcons[priority] || '📱';
  };

  const getPriorityClass = (priority) => {
    const priorityClasses = {
      urgent: 'urgent',
      high: 'high',
      medium: 'medium',
      low: 'low'
    };
    return priorityClasses[priority] || 'medium';
  };

  const sanitizeContent = (content) => {
    // Basic XSS protection for notification content
    if (typeof content !== 'string') return '';
    return content
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .substring(0, 200); // Limit length
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';

    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'now';
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
  };

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div
      className="notification-manager"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <AnimatePresence mode="popLayout">
        {visibleNotifications.map((notification, index) => (
          <motion.div
            key={notification.id}
            className={`notification ${getPriorityClass(notification.priority)}`}
            initial={{ opacity: 0, y: -50, scale: 0.9 }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
              zIndex: visibleNotifications.length - index
            }}
            exit={{
              opacity: 0,
              x: 300,
              scale: 0.9,
              transition: { duration: 0.2 }
            }}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 30
            }}
            layout
            onClick={() => handleNotificationClick(notification)}
            style={{
              '--notification-index': index
            }}
          >
            {/* Notification Header */}
            <div className="notification-header">
              <div className="notification-icon">
                {getNotificationIcon(notification.type, notification.priority)}
              </div>

              <div className="notification-info">
                <h4 className="notification-title">
                  {sanitizeContent(notification.title || 'Notification')}
                </h4>
                {notification.timestamp && (
                  <span className="notification-time">
                    {formatTimestamp(notification.timestamp)}
                  </span>
                )}
              </div>

              <button
                className="notification-close"
                onClick={(e) => {
                  e.stopPropagation();
                  hideNotification(notification.id);
                }}
                aria-label="Dismiss notification"
              >
                ✕
              </button>
            </div>

            {/* Notification Body */}
            {notification.body && (
              <div className="notification-body">
                <p>{sanitizeContent(notification.body)}</p>
              </div>
            )}

            {/* Notification Actions */}
            {notification.actions && notification.actions.length > 0 && (
              <div className="notification-actions">
                {notification.actions.slice(0, 2).map((action, actionIndex) => (
                  <button
                    key={actionIndex}
                    className="notification-action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (action.callback) {
                        action.callback();
                      }
                      hideNotification(notification.id);
                    }}
                  >
                    {sanitizeContent(action.label || 'Action')}
                  </button>
                ))}
              </div>
            )}

            {/* Progress Bar for Auto-hide */}
            {notification.priority !== 'urgent' && !notification.persistent && (
              <div className="notification-progress">
                <motion.div
                  className="progress-bar"
                  initial={{ width: '100%' }}
                  animate={{ width: isPaused ? '100%' : '0%' }}
                  transition={{
                    duration: isPaused ? 0 : autoHideDuration / 1000,
                    ease: 'linear'
                  }}
                />
              </div>
            )}

            {/* Priority Indicator */}
            {notification.priority === 'urgent' && (
              <div className="urgent-indicator">
                <motion.div
                  className="urgent-pulse"
                  animate={{
                    opacity: [1, 0.5, 1],
                    scale: [1, 1.05, 1]
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    ease: 'easeInOut'
                  }}
                />
              </div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Notification Counter */}
      {notifications.length > maxVisible && (
        <motion.div
          className="notification-counter"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
        >
          <span>+{notifications.length - maxVisible} more</span>
        </motion.div>
      )}
    </div>
  );
};

// Hook for managing notifications globally
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (notification) => {
    const id = notification.id || `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = notification.timestamp || Date.now();

    setNotifications(prev => [{
      ...notification,
      id,
      timestamp
    }, ...prev.slice(0, 49)]); // Keep last 50 notifications
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const showSuccess = (title, body, options = {}) => {
    addNotification({
      type: 'success',
      priority: 'medium',
      title,
      body,
      ...options
    });
  };

  const showError = (title, body, options = {}) => {
    addNotification({
      type: 'error',
      priority: 'high',
      title,
      body,
      persistent: true,
      ...options
    });
  };

  const showWarning = (title, body, options = {}) => {
    addNotification({
      type: 'warning',
      priority: 'medium',
      title,
      body,
      ...options
    });
  };

  const showInfo = (title, body, options = {}) => {
    addNotification({
      type: 'info',
      priority: 'low',
      title,
      body,
      ...options
    });
  };

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};

export default NotificationManager;