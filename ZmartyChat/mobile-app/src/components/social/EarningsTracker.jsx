/**
 * EarningsTracker - Commission and referral earnings tracker
 * Shows earnings, referrals, and viral growth metrics
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './EarningsTracker.css';

const EarningsTracker = ({ user, onBack }) => {
  const [earnings, setEarnings] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  // Mock earnings data - would be fetched from backend
  const mockEarnings = {
    totalEarned: 127.50,
    todayEarnings: 12.50,
    monthlyEarnings: 89.75,
    commissionRate: 0.05,
    tier: 'Bronze',
    nextTier: 'Silver',
    progressToNext: 65,
    referrals: {
      total: 23,
      active: 18,
      thisMonth: 5
    },
    recentEarnings: [
      {
        id: 1,
        timestamp: Date.now() - 120000,
        amount: 2.50,
        type: 'subscription',
        referralName: 'John D.',
        plan: 'Premium'
      },
      {
        id: 2,
        timestamp: Date.now() - 360000,
        amount: 5.00,
        type: 'subscription',
        referralName: 'Sarah M.',
        plan: 'Pro'
      },
      {
        id: 3,
        timestamp: Date.now() - 720000,
        amount: 1.25,
        type: 'usage',
        referralName: 'Mike R.',
        plan: 'Basic'
      }
    ],
    topReferrals: [
      {
        id: 1,
        name: 'Sarah M.',
        earnings: 25.50,
        signupDate: Date.now() - 2592000000, // 30 days ago
        plan: 'Pro',
        status: 'active'
      },
      {
        id: 2,
        name: 'John D.',
        earnings: 15.75,
        signupDate: Date.now() - 1728000000, // 20 days ago
        plan: 'Premium',
        status: 'active'
      },
      {
        id: 3,
        name: 'Mike R.',
        earnings: 8.25,
        signupDate: Date.now() - 864000000, // 10 days ago
        plan: 'Basic',
        status: 'active'
      }
    ],
    tiers: [
      { name: 'Bronze', rate: 0.05, requirement: 0, color: '#cd7f32' },
      { name: 'Silver', rate: 0.08, requirement: 10, color: '#c0c0c0' },
      { name: 'Gold', rate: 0.12, requirement: 25, color: '#ffd700' },
      { name: 'Platinum', rate: 0.15, requirement: 50, color: '#e5e4e2' }
    ]
  };

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setEarnings(mockEarnings);
      setLoading(false);
    }, 1000);
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatTime = (timestamp) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  const getCurrentTier = () => {
    return earnings?.tiers.find(tier => tier.name === earnings.tier) || earnings?.tiers[0];
  };

  const getNextTier = () => {
    const currentIndex = earnings?.tiers.findIndex(tier => tier.name === earnings.tier) || 0;
    return earnings?.tiers[currentIndex + 1] || null;
  };

  if (loading) {
    return (
      <div className="earnings-tracker loading">
        <div className="earnings-header">
          <button className="back-btn" onClick={onBack}>
            ←
          </button>
          <h1>Earnings</h1>
        </div>
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading earnings...</p>
        </div>
      </div>
    );
  }

  const currentTier = getCurrentTier();
  const nextTier = getNextTier();

  return (
    <div className="earnings-tracker">
      {/* Header */}
      <div className="earnings-header">
        <button className="back-btn" onClick={onBack}>
          ←
        </button>
        <h1>💰 Earnings</h1>
        <button className="share-btn">
          📱
        </button>
      </div>

      {/* Total Earnings Card */}
      <motion.div
        className="total-earnings-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="earnings-amount">
          <h2>{formatCurrency(earnings.totalEarned)}</h2>
          <p className="earnings-subtitle">Total Earned</p>
        </div>
        <div className="earnings-stats">
          <div className="stat">
            <span className="stat-value">{formatCurrency(earnings.todayEarnings)}</span>
            <span className="stat-label">Today</span>
          </div>
          <div className="stat">
            <span className="stat-value">{formatCurrency(earnings.monthlyEarnings)}</span>
            <span className="stat-label">This Month</span>
          </div>
        </div>
      </motion.div>

      {/* Tier Progress */}
      <motion.div
        className="tier-progress-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="tier-header">
          <div className="current-tier">
            <span className="tier-badge" style={{ backgroundColor: currentTier.color }}>
              {currentTier.name}
            </span>
            <span className="tier-rate">{(currentTier.rate * 100).toFixed(0)}% Commission</span>
          </div>
          {nextTier && (
            <div className="next-tier">
              <span className="next-tier-text">Next: {nextTier.name}</span>
              <span className="next-tier-rate">{(nextTier.rate * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
        {nextTier && (
          <div className="progress-container">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${earnings.progressToNext}%` }}
              />
            </div>
            <span className="progress-text">
              {earnings.referrals.total}/{nextTier.requirement} referrals ({earnings.progressToNext}%)
            </span>
          </div>
        )}
      </motion.div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {['overview', 'referrals', 'history'].map((tab) => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <motion.div
            className="overview-tab"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            {/* Referral Stats */}
            <div className="referral-stats-grid">
              <div className="referral-stat">
                <span className="stat-number">{earnings.referrals.total}</span>
                <span className="stat-description">Total Referrals</span>
              </div>
              <div className="referral-stat">
                <span className="stat-number">{earnings.referrals.active}</span>
                <span className="stat-description">Active Users</span>
              </div>
              <div className="referral-stat">
                <span className="stat-number">{earnings.referrals.thisMonth}</span>
                <span className="stat-description">This Month</span>
              </div>
            </div>

            {/* Share Actions */}
            <div className="share-section">
              <h3>📢 Share & Earn</h3>
              <div className="share-actions">
                <button className="share-action-btn">
                  📱 Copy Referral Link
                </button>
                <button className="share-action-btn">
                  📧 Email Invitation
                </button>
                <button className="share-action-btn">
                  💬 Share on Social
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'referrals' && (
          <motion.div
            className="referrals-tab"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="referrals-list">
              <h3>👥 Your Referrals</h3>
              {earnings.topReferrals.map((referral) => (
                <div key={referral.id} className="referral-item">
                  <div className="referral-avatar">
                    {referral.name.charAt(0)}
                  </div>
                  <div className="referral-info">
                    <h4>{referral.name}</h4>
                    <p className="referral-plan">{referral.plan} Plan</p>
                    <p className="referral-date">Joined {formatTime(referral.signupDate)}</p>
                  </div>
                  <div className="referral-earnings">
                    <span className="earnings-amount">{formatCurrency(referral.earnings)}</span>
                    <span className={`status ${referral.status}`}>
                      {referral.status === 'active' ? '🟢' : '🔴'} {referral.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'history' && (
          <motion.div
            className="history-tab"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="earnings-history">
              <h3>💸 Recent Earnings</h3>
              {earnings.recentEarnings.map((earning) => (
                <div key={earning.id} className="earning-item">
                  <div className="earning-icon">
                    {earning.type === 'subscription' ? '💳' : '⚡'}
                  </div>
                  <div className="earning-details">
                    <h4>{earning.type === 'subscription' ? 'Subscription' : 'Usage Fee'}</h4>
                    <p className="earning-source">{earning.referralName} - {earning.plan}</p>
                    <p className="earning-time">{formatTime(earning.timestamp)}</p>
                  </div>
                  <div className="earning-amount">
                    +{formatCurrency(earning.amount)}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="earnings-quick-actions">
        <motion.button
          className="quick-action-btn primary"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🚀 Boost Referrals
        </motion.button>
        <motion.button
          className="quick-action-btn secondary"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          📊 Analytics
        </motion.button>
        <motion.button
          className="quick-action-btn secondary"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          💳 Withdraw
        </motion.button>
      </div>
    </div>
  );
};

export default EarningsTracker;