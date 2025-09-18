/**
 * WhaleAlerts - Real-time whale transaction monitoring
 * Shows large crypto transactions and market impact analysis
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './WhaleAlerts.css';

const WhaleAlerts = ({ onBack }) => {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  // Mock whale alerts data
  const mockAlerts = [
    {
      id: 1,
      timestamp: Date.now() - 120000,
      type: 'transfer',
      amount: 50000000,
      symbol: 'USDT',
      from: 'Binance',
      to: 'Unknown Wallet',
      txHash: '0x1234...5678',
      impact: 'high',
      price: 1.00,
      value: 50000000,
      direction: 'outflow'
    },
    {
      id: 2,
      timestamp: Date.now() - 300000,
      type: 'trade',
      amount: 1500,
      symbol: 'BTC',
      from: 'Coinbase Pro',
      to: 'Market',
      txHash: '0x2345...6789',
      impact: 'medium',
      price: 43500,
      value: 65250000,
      direction: 'buy'
    },
    {
      id: 3,
      timestamp: Date.now() - 480000,
      type: 'transfer',
      amount: 25000,
      symbol: 'ETH',
      from: 'Unknown Wallet',
      to: 'Kraken',
      txHash: '0x3456...7890',
      impact: 'high',
      price: 1685,
      value: 42125000,
      direction: 'inflow'
    },
    {
      id: 4,
      timestamp: Date.now() - 720000,
      type: 'trade',
      amount: 500000,
      symbol: 'SOL',
      from: 'FTX',
      to: 'Market',
      txHash: '0x4567...8901',
      impact: 'medium',
      price: 101.5,
      value: 50750000,
      direction: 'sell'
    }
  ];

  useEffect(() => {
    // Simulate loading and real-time updates
    setTimeout(() => {
      setAlerts(mockAlerts);
      setLoading(false);
    }, 1000);

    // Simulate new alerts coming in
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        const newAlert = {
          id: Date.now(),
          timestamp: Date.now(),
          type: Math.random() > 0.5 ? 'transfer' : 'trade',
          amount: Math.random() * 100000000,
          symbol: ['BTC', 'ETH', 'USDT', 'SOL'][Math.floor(Math.random() * 4)],
          from: ['Binance', 'Coinbase', 'Unknown Wallet'][Math.floor(Math.random() * 3)],
          to: ['Unknown Wallet', 'Kraken', 'Market'][Math.floor(Math.random() * 3)],
          txHash: `0x${Math.random().toString(16).substr(2, 8)}...${Math.random().toString(16).substr(2, 4)}`,
          impact: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
          price: Math.random() * 50000,
          value: Math.random() * 100000000,
          direction: ['inflow', 'outflow', 'buy', 'sell'][Math.floor(Math.random() * 4)]
        };
        setAlerts(prev => [newAlert, ...prev.slice(0, 19)]);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    }
    if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(1)}K`;
    }
    return `$${amount.toFixed(2)}`;
  };

  const formatCrypto = (amount, symbol) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M ${symbol}`;
    }
    if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K ${symbol}`;
    }
    return `${amount.toFixed(2)} ${symbol}`;
  };

  const formatTime = (timestamp) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getDirectionIcon = (direction) => {
    switch (direction) {
      case 'inflow': return '📈';
      case 'outflow': return '📉';
      case 'buy': return '💚';
      case 'sell': return '❤️';
      default: return '🔄';
    }
  };

  const filteredAlerts = filter === 'all'
    ? alerts
    : alerts.filter(alert => alert.impact === filter);

  if (loading) {
    return (
      <div className="whale-alerts loading">
        <div className="whale-header">
          <button className="back-btn" onClick={onBack}>
            ←
          </button>
          <h1>Whale Alerts</h1>
        </div>
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading whale activity...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="whale-alerts">
      {/* Header */}
      <div className="whale-header">
        <button className="back-btn" onClick={onBack}>
          ←
        </button>
        <h1>🐋 Whale Alerts</h1>
        <div className="live-indicator">
          <span className="live-dot"></span>
          LIVE
        </div>
      </div>

      {/* Stats Summary */}
      <div className="whale-stats">
        <div className="stat-item">
          <span className="stat-value">{alerts.length}</span>
          <span className="stat-label">Alerts Today</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">
            {formatCurrency(alerts.reduce((sum, alert) => sum + alert.value, 0))}
          </span>
          <span className="stat-label">Total Volume</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">
            {alerts.filter(a => a.impact === 'high').length}
          </span>
          <span className="stat-label">High Impact</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        {['all', 'high', 'medium', 'low'].map((filterType) => (
          <button
            key={filterType}
            className={`filter-tab ${filter === filterType ? 'active' : ''}`}
            onClick={() => setFilter(filterType)}
          >
            {filterType === 'all' ? 'All' : `${filterType.charAt(0).toUpperCase() + filterType.slice(1)} Impact`}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="alerts-container">
        <AnimatePresence>
          {filteredAlerts.map((alert) => (
            <motion.div
              key={alert.id}
              className="whale-alert-item"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="alert-header">
                <div className="alert-icon">
                  🐋
                </div>
                <div className="alert-title">
                  <h4>{alert.type === 'transfer' ? 'Large Transfer' : 'Whale Trade'}</h4>
                  <span className="alert-time">{formatTime(alert.timestamp)}</span>
                </div>
                <div className="alert-impact">
                  <span
                    className="impact-badge"
                    style={{ backgroundColor: getImpactColor(alert.impact) }}
                  >
                    {alert.impact.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="alert-content">
                <div className="alert-amount">
                  <span className="crypto-amount">
                    {formatCrypto(alert.amount, alert.symbol)}
                  </span>
                  <span className="usd-amount">
                    {formatCurrency(alert.value)}
                  </span>
                </div>

                <div className="alert-flow">
                  <div className="flow-item">
                    <span className="flow-label">From</span>
                    <span className="flow-value">{alert.from}</span>
                  </div>
                  <div className="flow-arrow">
                    {getDirectionIcon(alert.direction)}
                  </div>
                  <div className="flow-item">
                    <span className="flow-label">To</span>
                    <span className="flow-value">{alert.to}</span>
                  </div>
                </div>

                <div className="alert-details">
                  <div className="detail-item">
                    <span className="detail-label">Price</span>
                    <span className="detail-value">{formatCurrency(alert.price)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Hash</span>
                    <span className="detail-value hash">{alert.txHash}</span>
                  </div>
                </div>
              </div>

              <div className="alert-actions">
                <button className="action-btn primary">
                  📊 Analyze Impact
                </button>
                <button className="action-btn secondary">
                  🔗 View Transaction
                </button>
                <button className="action-btn secondary">
                  📱 Share Alert
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {filteredAlerts.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🐋</div>
          <h3>No whale alerts</h3>
          <p>No {filter !== 'all' ? `${filter} impact` : ''} whale activity detected right now</p>
        </div>
      )}

      {/* Quick Actions */}
      <div className="whale-quick-actions">
        <motion.button
          className="quick-action-btn"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          ⚙️ Alert Settings
        </motion.button>
        <motion.button
          className="quick-action-btn"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          📈 Market Impact
        </motion.button>
        <motion.button
          className="quick-action-btn"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🔔 Set Threshold
        </motion.button>
      </div>
    </div>
  );
};

export default WhaleAlerts;