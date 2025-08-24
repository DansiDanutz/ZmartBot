import React, { useState, useEffect, useCallback } from 'react';
import LiveAlertsGuide from './LiveAlertsGuide';
import './EnhancedAlertsSystem.css';

const LiveAlertsPage = () => {
  const [activeTab, setActiveTab] = useState('guide');
  const [symbols, setSymbols] = useState([]);
  const [systemStatus, setSystemStatus] = useState({
    engineRunning: true,
    activeAlerts: 0,
    recentTriggers: 0,
    uptime: '24h'
  });

  const tabs = [
    { id: 'guide', label: 'Implementation Guide', icon: '🚀' },
    { id: 'demo', label: 'Live Demo', icon: '📊' },
    { id: 'architecture', label: 'Architecture', icon: '🏗️' },
    { id: 'integration', label: 'Integration', icon: '🔌' }
  ];

  // Fetch symbols from the backend
  const fetchSymbols = useCallback(async () => {
    try {
      const response = await fetch('/api/futures-symbols/my-symbols/current');
      if (response.ok) {
        const data = await response.json();
        const symbolsList = data.portfolio?.symbols || [];
        setSymbols(symbolsList);
      } else {
        const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];
        setSymbols(fallbackSymbols);
      }
    } catch (error) {
      console.error('Error loading symbols:', error);
      const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];
      setSymbols(fallbackSymbols);
    }
  }, []);

  // Fetch system status
  const fetchSystemStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/alerts/status');
      if (response.ok) {
        const data = await response.json();
        const statusInfo = data.data || data;
        setSystemStatus({
          engineRunning: statusInfo.engine_running || true,
          activeAlerts: statusInfo.active_alerts || 0,
          recentTriggers: statusInfo.recent_triggers || 0,
          uptime: statusInfo.uptime || '24h'
        });
      }
    } catch (error) {
      console.error('Error loading system status:', error);
    }
  }, []);

  useEffect(() => {
    fetchSymbols();
    fetchSystemStatus();
  }, [fetchSymbols, fetchSystemStatus]);

  return (
    <div className="enhanced-alerts-container">
      <div className="alerts-header">
        <div className="header-title">
          <h1>🔴 Live Alerts System</h1>
          <p className="header-subtitle">
            Real-time cross-signals and pattern detection with 21 technical indicators
          </p>
        </div>
        <div className="system-status">
          <div className="status-item">
            <span className={`status-dot ${systemStatus.engineRunning ? 'running' : 'stopped'}`}></span>
            <span className="status-label">Engine: {systemStatus.engineRunning ? 'Running' : 'Stopped'}</span>
          </div>
          <div className="status-item">
            <span className="status-value">{systemStatus.activeAlerts}</span>
            <span className="status-label">Active Alerts</span>
          </div>
          <div className="status-item">
            <span className="status-value">{systemStatus.recentTriggers}</span>
            <span className="status-label">Recent Triggers</span>
          </div>
          <div className="status-item">
            <span className="status-value">{systemStatus.uptime}</span>
            <span className="status-label">Uptime</span>
          </div>
        </div>
      </div>

      <div className="alerts-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="alerts-content">
        {activeTab === 'guide' && (
          <LiveAlertsGuide />
        )}

        {activeTab === 'demo' && (
          <div className="demo-content">
            <div className="demo-grid">
              <div className="demo-card">
                <h3>📊 Market Sentiment Analysis</h3>
                <p>Real-time sentiment derived from 21 technical indicators</p>
                <div className="sentiment-demo">
                  <div className="sentiment-bar">
                    <div className="sentiment-fill bullish" style={{width: '45%'}}></div>
                  </div>
                  <div className="sentiment-labels">
                    <span>Bullish: 45%</span>
                    <span>Neutral: 35%</span>
                    <span>Bearish: 20%</span>
                  </div>
                </div>
              </div>
              
              <div className="demo-card">
                <h3>🎯 Cross-Signal Detection</h3>
                <p>Advanced pattern recognition with cooldown management</p>
                <div className="signals-demo">
                  <div className="signal-item">
                    <span className="signal-badge warning">EMA Bullish Cross</span>
                    <span className="signal-time">2 min ago</span>
                  </div>
                  <div className="signal-item">
                    <span className="signal-badge info">RSI Recovery</span>
                    <span className="signal-time">5 min ago</span>
                  </div>
                  <div className="signal-item">
                    <span className="signal-badge strong">Squeeze Breakout</span>
                    <span className="signal-time">8 min ago</span>
                  </div>
                </div>
              </div>

              <div className="demo-card">
                <h3>📈 Symbols Coverage</h3>
                <p>Monitoring {symbols.length} active symbols</p>
                <div className="symbols-demo">
                  {symbols.slice(0, 5).map((symbol, index) => (
                    <div key={symbol} className="symbol-chip">
                      <span className="symbol-name">{symbol}</span>
                      <span className={`symbol-status ${index % 3 === 0 ? 'bullish' : index % 3 === 1 ? 'neutral' : 'bearish'}`}>
                        {index % 3 === 0 ? '📈' : index % 3 === 1 ? '➡️' : '📉'}
                      </span>
                    </div>
                  ))}
                  {symbols.length > 5 && (
                    <div className="symbol-chip more">
                      +{symbols.length - 5} more
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'architecture' && (
          <div className="architecture-content">
            <h2>🏗️ System Architecture</h2>
            <div className="architecture-flow">
              <div className="arch-step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>📅 Scheduler</h4>
                  <p>Bar-close schedulers for 15m, 1h, 4h, 1d timeframes</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="arch-step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>📊 Data Processing</h4>
                  <p>Fetch OHLC data and compute 21 technical indicators</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="arch-step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>⚙️ Signal Engine</h4>
                  <p>Normalize indicators, apply diffs, evaluate cross-signals</p>
                </div>
              </div>
              <div className="flow-arrow">↓</div>
              <div className="arch-step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h4>📡 Real-time Updates</h4>
                  <p>Push updates via SSE to frontend components</p>
                </div>
              </div>
            </div>

            <div className="components-grid">
              <div className="component-card">
                <h4>🔄 normalizeTa.ts</h4>
                <p>Normalizes 21 indicators into consistent format</p>
              </div>
              <div className="component-card">
                <h4>📊 applyDiff.ts</h4>
                <p>Computes diffs and derives sentiment</p>
              </div>
              <div className="component-card">
                <h4>🎯 engine.ts</h4>
                <p>Cross-signals with cooldown & hysteresis</p>
              </div>
              <div className="component-card">
                <h4>⏰ cooldown.ts</h4>
                <p>Prevents signal noise and flapping</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'integration' && (
          <div className="integration-content">
            <h2>🔌 Integration Status</h2>
            <div className="integration-status">
              <div className="status-section">
                <h3>✅ Backend Infrastructure</h3>
                <div className="status-grid">
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <div className="status-details">
                      <strong>Enhanced Alerts API</strong>
                      <p>Routes: /api/v1/alerts/*</p>
                    </div>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <div className="status-details">
                      <strong>Cross-Signals Engine</strong>
                      <p>File: src/lib/alerts/engine.py</p>
                    </div>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <div className="status-details">
                      <strong>Technical Indicators</strong>
                      <p>21 indicators with normalization</p>
                    </div>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <div className="status-details">
                      <strong>WebSocket Support</strong>
                      <p>Real-time updates infrastructure</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="status-section">
                <h3>🔄 Next Steps</h3>
                <div className="status-grid">
                  <div className="status-item pending">
                    <span className="status-icon">📋</span>
                    <div className="status-details">
                      <strong>Cron Scheduling</strong>
                      <p>Bar-close job automation</p>
                    </div>
                  </div>
                  <div className="status-item pending">
                    <span className="status-icon">📸</span>
                    <div className="status-details">
                      <strong>Screenshot Service</strong>
                      <p>Automated chart captures</p>
                    </div>
                  </div>
                  <div className="status-item pending">
                    <span className="status-icon">📱</span>
                    <div className="status-details">
                      <strong>Telegram Integration</strong>
                      <p>Push notifications</p>
                    </div>
                  </div>
                  <div className="status-item pending">
                    <span className="status-icon">📊</span>
                    <div className="status-details">
                      <strong>Analytics Dashboard</strong>
                      <p>Alert performance metrics</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="api-endpoints">
              <h3>🔌 Available API Endpoints</h3>
              <div className="endpoint-list">
                <div className="endpoint-item">
                  <span className="method get">GET</span>
                  <span className="path">/api/v1/alerts/status</span>
                  <span className="description">System status and health check</span>
                </div>
                <div className="endpoint-item">
                  <span className="method get">GET</span>
                  <span className="path">/api/v1/alerts/list</span>
                  <span className="description">List all active alerts</span>
                </div>
                <div className="endpoint-item">
                  <span className="method get">GET</span>
                  <span className="path">/api/enhanced-alerts/state/{symbol}</span>
                  <span className="description">Get symbol state with indicators</span>
                </div>
                <div className="endpoint-item">
                  <span className="method get">GET</span>
                  <span className="path">/api/enhanced-alerts/stream</span>
                  <span className="description">SSE stream for real-time updates</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveAlertsPage;