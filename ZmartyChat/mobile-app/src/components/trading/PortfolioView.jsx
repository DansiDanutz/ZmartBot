/**
 * PortfolioView - Mobile cryptocurrency portfolio interface
 * Shows holdings, P&L, and trading performance metrics
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PortfolioView.css';

const PortfolioView = ({ user, onBack }) => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');

  // Mock portfolio data - would be fetched from backend
  const mockPortfolio = {
    totalValue: 42850.75,
    totalPnL: 3250.50,
    totalPnLPercent: 8.2,
    holdings: [
      {
        symbol: 'BTC',
        name: 'Bitcoin',
        amount: 0.75,
        value: 32500.00,
        pnl: 2100.50,
        pnlPercent: 6.9,
        price: 43333.33,
        change24h: 2.1,
        icon: '₿'
      },
      {
        symbol: 'ETH',
        name: 'Ethereum',
        amount: 5.2,
        value: 8750.25,
        pnl: 850.25,
        pnlPercent: 10.8,
        price: 1682.74,
        change24h: 3.5,
        icon: 'Ξ'
      },
      {
        symbol: 'SOL',
        name: 'Solana',
        amount: 15.8,
        value: 1600.50,
        pnl: 299.75,
        pnlPercent: 23.0,
        price: 101.30,
        change24h: 5.2,
        icon: '◎'
      }
    ],
    performance: {
      '24h': { value: 42850.75, change: 1250.30, percent: 3.0 },
      '7d': { value: 42850.75, change: 3250.50, percent: 8.2 },
      '30d': { value: 42850.75, change: 6750.25, percent: 18.7 },
      '90d': { value: 42850.75, change: 12850.75, percent: 42.8 }
    }
  };

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setPortfolioData(mockPortfolio);
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

  const formatPercent = (percent) => {
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent.toFixed(2)}%`;
  };

  const formatCrypto = (amount, symbol) => {
    return `${amount.toFixed(4)} ${symbol}`;
  };

  if (loading) {
    return (
      <div className="portfolio-view loading">
        <div className="portfolio-header">
          <button className="back-btn" onClick={onBack}>
            ←
          </button>
          <h1>Portfolio</h1>
        </div>
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-view">
      {/* Header */}
      <div className="portfolio-header">
        <button className="back-btn" onClick={onBack}>
          ←
        </button>
        <h1>📊 Portfolio</h1>
        <button className="refresh-btn">
          🔄
        </button>
      </div>

      {/* Total Value Card */}
      <motion.div
        className="total-value-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="total-value">
          <h2>{formatCurrency(portfolioData.totalValue)}</h2>
          <div className={`total-pnl ${portfolioData.totalPnL >= 0 ? 'positive' : 'negative'}`}>
            <span className="pnl-amount">{formatCurrency(portfolioData.totalPnL)}</span>
            <span className="pnl-percent">({formatPercent(portfolioData.totalPnLPercent)})</span>
          </div>
        </div>
        <div className="portfolio-actions">
          <button className="action-btn buy">
            💰 Buy
          </button>
          <button className="action-btn sell">
            💸 Sell
          </button>
          <button className="action-btn swap">
            🔄 Swap
          </button>
        </div>
      </motion.div>

      {/* Performance Timeframes */}
      <div className="performance-section">
        <div className="timeframe-selector">
          {Object.keys(portfolioData.performance).map((timeframe) => (
            <button
              key={timeframe}
              className={`timeframe-btn ${selectedTimeframe === timeframe ? 'active' : ''}`}
              onClick={() => setSelectedTimeframe(timeframe)}
            >
              {timeframe}
            </button>
          ))}
        </div>
        <motion.div
          className="performance-metrics"
          key={selectedTimeframe}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="metric">
            <span className="metric-label">Value</span>
            <span className="metric-value">
              {formatCurrency(portfolioData.performance[selectedTimeframe].value)}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Change</span>
            <span className={`metric-value ${portfolioData.performance[selectedTimeframe].change >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(portfolioData.performance[selectedTimeframe].change)}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Percent</span>
            <span className={`metric-value ${portfolioData.performance[selectedTimeframe].percent >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(portfolioData.performance[selectedTimeframe].percent)}
            </span>
          </div>
        </motion.div>
      </div>

      {/* Holdings List */}
      <div className="holdings-section">
        <h3>💼 Your Holdings</h3>
        <div className="holdings-list">
          <AnimatePresence>
            {portfolioData.holdings.map((holding, index) => (
              <motion.div
                key={holding.symbol}
                className="holding-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="holding-icon">
                  {holding.icon}
                </div>
                <div className="holding-info">
                  <div className="holding-primary">
                    <h4>{holding.symbol}</h4>
                    <span className="holding-amount">
                      {formatCrypto(holding.amount, holding.symbol)}
                    </span>
                  </div>
                  <div className="holding-secondary">
                    <span className="holding-name">{holding.name}</span>
                    <span className="holding-price">
                      {formatCurrency(holding.price)}
                    </span>
                  </div>
                </div>
                <div className="holding-performance">
                  <div className="holding-value">
                    {formatCurrency(holding.value)}
                  </div>
                  <div className={`holding-pnl ${holding.pnl >= 0 ? 'positive' : 'negative'}`}>
                    <span className="pnl-amount">{formatCurrency(holding.pnl)}</span>
                    <span className="pnl-percent">({formatPercent(holding.pnlPercent)})</span>
                  </div>
                  <div className={`price-change ${holding.change24h >= 0 ? 'positive' : 'negative'}`}>
                    24h: {formatPercent(holding.change24h)}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-portfolio">
        <motion.button
          className="portfolio-action-btn"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          📈 Market Analysis
        </motion.button>
        <motion.button
          className="portfolio-action-btn"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🔔 Set Alerts
        </motion.button>
        <motion.button
          className="portfolio-action-btn"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          💰 Earn Commission
        </motion.button>
      </div>
    </div>
  );
};

export default PortfolioView;