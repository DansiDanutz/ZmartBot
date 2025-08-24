import React, { useState, useEffect, useCallback } from 'react';

const EnhancedAlertsDashboard = () => {
  const [symbols, setSymbols] = useState([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alertsData, setAlertsData] = useState({});

  const timeframes = [
    { id: '15m', label: '15 Minutes', icon: '⏱️' },
    { id: '1h', label: '1 Hour', icon: '🕐' },
    { id: '4h', label: '4 Hours', icon: '🕓' },
    { id: '1d', label: '1 Day', icon: '📅' }
  ];

  // Fetch symbols from the backend
  const fetchSymbols = useCallback(async () => {
    try {
      console.log('🔄 Fetching symbols for Enhanced Alerts...');
      const response = await fetch('/api/futures-symbols/my-symbols/current');
      
      if (response.ok) {
        const data = await response.json();
        const symbolsList = data.portfolio?.symbols || [];
        console.log('🎯 Enhanced Alerts - Symbols loaded:', symbolsList);
        setSymbols(symbolsList);
      } else {
        console.error('❌ Failed to load symbols for Enhanced Alerts:', response.status);
        // Fallback to default symbols
        const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];
        setSymbols(fallbackSymbols);
      }
    } catch (error) {
      console.error('❌ Error loading symbols for Enhanced Alerts:', error);
      const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];
      setSymbols(fallbackSymbols);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch enhanced alerts data for a symbol
  const fetchEnhancedAlerts = useCallback(async (symbol) => {
    try {
      const response = await fetch(`/api/v1/alerts/enhanced/state/${symbol}?timeframe=${selectedTimeframe}`);
      if (response.ok) {
        const data = await response.json();
        setAlertsData(prev => ({
          ...prev,
          [symbol]: data.data || {}
        }));
      } else {
        console.error(`❌ Failed to load enhanced alerts for ${symbol}:`, response.status);
      }
    } catch (error) {
      console.error(`❌ Error loading enhanced alerts for ${symbol}:`, error);
    }
  }, [selectedTimeframe]);

  // Load data on component mount
  useEffect(() => {
    fetchSymbols();
  }, [fetchSymbols]);

  // Fetch alerts data for all symbols when timeframe changes
  useEffect(() => {
    if (symbols.length > 0) {
      symbols.forEach(symbol => {
        fetchEnhancedAlerts(symbol);
      });
    }
  }, [symbols, selectedTimeframe, fetchEnhancedAlerts]);

  const getSentimentColor = (sentiment) => {
    if (sentiment.bullish > 60) return '#10b981';
    if (sentiment.bearish > 60) return '#ef4444';
    return '#f59e0b';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'bullish': return '#10b981';
      case 'bearish': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="enhanced-alerts-dashboard">
        <div className="dashboard-header">
          <h2>🚀 Enhanced Alerts System</h2>
          <p>Advanced cross-signals and real-time pattern detection</p>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading Enhanced Alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="enhanced-alerts-dashboard">
      <div className="dashboard-header">
        <h2>🚀 Enhanced Alerts System</h2>
        <p>Advanced cross-signals and real-time pattern detection</p>
        
        <div className="timeframe-selector">
          <label>Timeframe:</label>
          <select 
            value={selectedTimeframe} 
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="timeframe-select"
          >
            {timeframes.map(tf => (
              <option key={tf.id} value={tf.id}>
                {tf.icon} {tf.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      <div className="alerts-grid">
        {symbols.map(symbol => {
          const symbolData = alertsData[symbol] || {};
          const sentiment = symbolData.sentiment || { bullish: 0, neutral: 0, bearish: 0 };
          const indicators = symbolData.indicators || {};

          return (
            <div key={symbol} className="alert-card">
              <div className="card-header">
                <h3>{symbol}</h3>
                <span className="timeframe-badge">{selectedTimeframe.toUpperCase()}</span>
              </div>

              <div className="sentiment-section">
                <h4>Market Sentiment</h4>
                <div className="sentiment-bars">
                  <div className="sentiment-bar">
                    <span>Bullish</span>
                    <div className="bar-container">
                      <div 
                        className="bar bullish" 
                        style={{ width: `${sentiment.bullish}%` }}
                      ></div>
                    </div>
                    <span>{sentiment.bullish}%</span>
                  </div>
                  <div className="sentiment-bar">
                    <span>Neutral</span>
                    <div className="bar-container">
                      <div 
                        className="bar neutral" 
                        style={{ width: `${sentiment.neutral}%` }}
                      ></div>
                    </div>
                    <span>{sentiment.neutral}%</span>
                  </div>
                  <div className="sentiment-bar">
                    <span>Bearish</span>
                    <div className="bar-container">
                      <div 
                        className="bar bearish" 
                        style={{ width: `${sentiment.bearish}%` }}
                      ></div>
                    </div>
                    <span>{sentiment.bearish}%</span>
                  </div>
                </div>
              </div>

              <div className="indicators-section">
                <h4>Technical Indicators</h4>
                <div className="indicators-grid">
                  {Object.entries(indicators).slice(0, 6).map(([key, indicator]) => (
                    <div key={key} className="indicator-item">
                      <span className="indicator-name">{key.toUpperCase()}</span>
                      <span 
                        className="indicator-status"
                        style={{ color: getStatusColor(indicator.status) }}
                      >
                        {indicator.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card-footer">
                <span className="last-update">
                  Last update: {symbolData.updated_at ? 
                    new Date(symbolData.updated_at).toLocaleTimeString() : 
                    'N/A'
                  }
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="system-stats">
        <div className="stats-card">
          <h4>📊 System Status</h4>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Active Symbols</span>
              <span className="stat-value">{symbols.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Timeframe</span>
              <span className="stat-value">{selectedTimeframe.toUpperCase()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Real-time Updates</span>
              <span className="stat-value">Active</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Cross Signals</span>
              <span className="stat-value">Monitoring</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAlertsDashboard;
