import React, { useState } from 'react';
import './EnhancedAlertsSystem.css';

const LiveAlertsGuide = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = [
    { id: 'overview', title: 'Architecture Overview', icon: '🏗️' },
    { id: 'datamodel', title: 'Data Model', icon: '🗃️' },
    { id: 'backend', title: 'Backend Logic', icon: '⚙️' },
    { id: 'api', title: 'API Endpoints', icon: '🔌' },
    { id: 'frontend', title: 'Frontend Components', icon: '🎨' },
    { id: 'implementation', title: 'Implementation Steps', icon: '📋' }
  ];

  return (
    <div className="enhanced-alerts-container">
      <div className="alerts-header">
        <div className="header-title">
          <h1>🚀 ZmartBot Alerts System Implementation Guide</h1>
          <p className="header-subtitle">
            Comprehensive guide for implementing a robust, resource-efficient Alerts pipeline
          </p>
        </div>
      </div>

      <div className="alerts-content">
        <div className="alerts-sidebar">
          <nav className="alerts-nav">
            {sections.map(section => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
              >
                <span className="nav-icon">{section.icon}</span>
                <span className="nav-label">{section.title}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="alerts-main">
          {activeSection === 'overview' && (
            <div className="section-content">
              <h2>🏗️ Architecture at a Glance</h2>
              <div className="architecture-diagram">
                <div className="flow-box">
                  <h3>📅 Scheduler</h3>
                  <p>Bar-close schedulers<br/>15m · 1h · 4h · 1d</p>
                </div>
                <div className="flow-arrow">→</div>
                <div className="flow-box">
                  <h3>⚙️ Backend</h3>
                  <ul>
                    <li>Fetch OHLC once</li>
                    <li>Compute 21 Indicators</li>
                    <li>normalizeTA()</li>
                    <li>applyDiffs() + deriveSentiment</li>
                    <li>evaluateCrossSignals()</li>
                  </ul>
                </div>
                <div className="flow-arrow">→</div>
                <div className="flow-box">
                  <h3>🎨 Frontend</h3>
                  <p>SymbolAlertCard<br/>Subscribe SSE</p>
                </div>
              </div>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>⏱️ Real-time Processing</h4>
                  <p>Bar-close computations with diff-based updates for all 21 indicators</p>
                </div>
                <div className="feature-card">
                  <h4>🎯 Cross-Signals</h4>
                  <p>Composite signals with cooldown & hysteresis to avoid noise</p>
                </div>
                <div className="feature-card">
                  <h4>📸 Smart Screenshots</h4>
                  <p>Screenshot throttling for severe events only</p>
                </div>
                <div className="feature-card">
                  <h4>📡 Live Updates</h4>
                  <p>Snappy UI that updates cards instantly via SSE</p>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'datamodel' && (
            <div className="section-content">
              <h2>🗃️ Data Model</h2>
              <div className="code-section">
                <h3>SymbolState</h3>
                <pre className="code-block">
{`type SymbolState = {
  symbol: string;
  timeframe: '15m'|'1h'|'4h'|'1d';
  last_bar_ts: number; // closed bar timestamp (ms)
  indicators: Record<string, { 
    status:'bullish'|'neutral'|'bearish', 
    fields: any 
  }>;
  sentiment: { 
    bullish:number; 
    neutral:number; 
    bearish:number 
  };
  updated_at: number;
};`}
                </pre>
              </div>
              <div className="code-section">
                <h3>AlertEvent</h3>
                <pre className="code-block">
{`type AlertEvent = {
  id: string;
  symbol: string;
  timeframe: '15m'|'1h'|'4h'|'1d';
  bar_ts: number;
  type: 'indicator_status_change' | 'rule';
  indicator_key?: string; 
  from?: string; 
  to?: string;
  rule_id?: string; 
  label?: string;
  severity: 'info'|'warning'|'strong';
  score: number;
  screenshot_url?: string;
  created_at: number;
};`}
                </pre>
              </div>
              <div className="db-info">
                <h3>Database Indexes</h3>
                <ul>
                  <li>SymbolState (symbol, timeframe) UNIQUE</li>
                  <li>AlertEvent (symbol, timeframe, created_at DESC)</li>
                </ul>
              </div>
            </div>
          )}

          {activeSection === 'backend' && (
            <div className="section-content">
              <h2>⚙️ Backend Core Logic</h2>
              <div className="logic-grid">
                <div className="logic-card">
                  <h3>🔄 normalizeTa.ts</h3>
                  <p>Normalizes your 21 indicators into a consistent UI/logic shape</p>
                  <div className="code-snippet">
                    <code>normalizeTA(ta: any): NormalizedIndicator[]</code>
                  </div>
                </div>
                <div className="logic-card">
                  <h3>📊 applyDiff.ts</h3>
                  <p>Computes indicator diffs and emits events only for changed statuses</p>
                  <div className="code-snippet">
                    <code>applyIndicatorDiffs(prev, curr): IndicatorEvent[]</code>
                  </div>
                </div>
                <div className="logic-card">
                  <h3>🎯 engine.ts</h3>
                  <p>Implements Cross-Signals rules with cooldown & hysteresis hooks</p>
                  <div className="code-snippet">
                    <code>evaluateCrossSignals(prev, curr, ctx): CrossAlert[]</code>
                  </div>
                </div>
                <div className="logic-card">
                  <h3>⏰ cooldown.ts</h3>
                  <p>Bare-bones cooldown management (swap for Redis in prod)</p>
                  <div className="code-snippet">
                    <code>recentlyFiredFactory(symbol, timeframe)</code>
                  </div>
                </div>
              </div>
              <div className="rules-section">
                <h3>Cross-Signal Rules</h3>
                <div className="rules-grid">
                  <div className="rule-card">
                    <h4>EMA Bullish Cross</h4>
                    <p>EMA 9/21 crosses bullish with 30min cooldown</p>
                  </div>
                  <div className="rule-card">
                    <h4>MACD Bullish Flip</h4>
                    <p>MACD flips to bullish with 30min cooldown</p>
                  </div>
                  <div className="rule-card">
                    <h4>RSI Recovery</h4>
                    <p>RSI oversold → recover with hysteresis</p>
                  </div>
                  <div className="rule-card">
                    <h4>Squeeze Breakout</h4>
                    <p>BB Squeeze breakout with momentum (strong alert)</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'api' && (
            <div className="section-content">
              <h2>🔌 API Endpoints</h2>
              <div className="api-grid">
                <div className="api-card">
                  <h3>GET /api/state/{symbol}</h3>
                  <p>Get current state for a symbol</p>
                  <div className="api-params">
                    <strong>Query:</strong> tf (timeframe: 15m|1h|4h|1d)
                  </div>
                  <div className="api-response">
                    <strong>Response:</strong> SymbolState object
                  </div>
                </div>
                <div className="api-card">
                  <h3>GET /api/events/{symbol}</h3>
                  <p>List alert events for a symbol</p>
                  <div className="api-params">
                    <strong>Query:</strong> tf, limit
                  </div>
                  <div className="api-response">
                    <strong>Response:</strong> AlertEvent[] array
                  </div>
                </div>
                <div className="api-card">
                  <h3>GET /api/alerts/stream</h3>
                  <p>Server-Sent Events stream for real-time updates</p>
                  <div className="api-params">
                    <strong>Type:</strong> text/event-stream
                  </div>
                  <div className="api-response">
                    <strong>Events:</strong> Real-time alert updates
                  </div>
                </div>
              </div>
              <div className="integration-info">
                <h3>Integration with Your Backend</h3>
                <p>Your ZmartBot already has comprehensive alerts infrastructure:</p>
                <ul>
                  <li>✅ Enhanced Alerts API Routes (/api/v1/alerts/)</li>
                  <li>✅ Cross-Signals Engine (src/lib/alerts/engine.py)</li>
                  <li>✅ Technical Indicators Services</li>
                  <li>✅ WebSocket Support for Real-time Updates</li>
                </ul>
              </div>
            </div>
          )}

          {activeSection === 'frontend' && (
            <div className="section-content">
              <h2>🎨 Frontend Components</h2>
              <div className="component-grid">
                <div className="component-card">
                  <h3>SymbolAlertCard</h3>
                  <p>Main component displaying symbol alerts with real-time updates</p>
                  <div className="features-list">
                    <ul>
                      <li>Market Sentiment Analysis</li>
                      <li>Cross Signals Display</li>
                      <li>21 Technical Indicators</li>
                      <li>SSE Real-time Updates</li>
                    </ul>
                  </div>
                </div>
                <div className="component-card">
                  <h3>AlertsPage</h3>
                  <p>Main alerts dashboard page</p>
                  <div className="features-list">
                    <ul>
                      <li>Multiple Symbol Cards</li>
                      <li>Timeframe Selection</li>
                      <li>Expandable Details</li>
                      <li>Status Monitoring</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="ui-features">
                <h3>UI Features</h3>
                <div className="ui-grid">
                  <div className="ui-feature">
                    <h4>📊 Sentiment Bars</h4>
                    <p>Visual representation of bullish/neutral/bearish sentiment</p>
                  </div>
                  <div className="ui-feature">
                    <h4>🎯 Status Chips</h4>
                    <p>Color-coded indicator status (bullish, neutral, bearish)</p>
                  </div>
                  <div className="ui-feature">
                    <h4>🔔 Alert Badges</h4>
                    <p>Severity-based badges for cross signals</p>
                  </div>
                  <div className="ui-feature">
                    <h4>📡 Live Updates</h4>
                    <p>Real-time card updates without page refresh</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'implementation' && (
            <div className="section-content">
              <h2>📋 Implementation Steps</h2>
              <div className="steps-container">
                <div className="step-section">
                  <h3>Phase 1: Core Logic (Backend)</h3>
                  <div className="step-list">
                    <div className="step-item">
                      <span className="step-number">1</span>
                      <div className="step-content">
                        <h4>Create lib/alerts/normalizeTa.ts</h4>
                        <p>Normalize your 21 indicators into consistent format</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">2</span>
                      <div className="step-content">
                        <h4>Create lib/alerts/applyDiff.ts</h4>
                        <p>Implement diff-based updates and sentiment derivation</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">3</span>
                      <div className="step-content">
                        <h4>Create lib/alerts/engine.ts</h4>
                        <p>Cross-signals rules with cooldown & hysteresis</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">4</span>
                      <div className="step-content">
                        <h4>Create lib/alerts/cooldown.ts</h4>
                        <p>Cooldown management system</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="step-section">
                  <h3>Phase 2: Services & API</h3>
                  <div className="step-list">
                    <div className="step-item">
                      <span className="step-number">5</span>
                      <div className="step-content">
                        <h4>Create lib/services/index.ts</h4>
                        <p>Service contracts for DB, screenshots, SSE</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">6</span>
                      <div className="step-content">
                        <h4>Create API routes</h4>
                        <p>State, events, and SSE stream endpoints</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">7</span>
                      <div className="step-content">
                        <h4>Create runAlertsWorker.mjs</h4>
                        <p>Worker script for processing alerts</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="step-section">
                  <h3>Phase 3: Frontend & Scheduling</h3>
                  <div className="step-list">
                    <div className="step-item">
                      <span className="step-number">8</span>
                      <div className="step-content">
                        <h4>Create SymbolAlertCard.tsx</h4>
                        <p>Main component with SSE integration</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">9</span>
                      <div className="step-content">
                        <h4>Create AlertsPage</h4>
                        <p>Dashboard page with multiple symbol cards</p>
                      </div>
                    </div>
                    <div className="step-item">
                      <span className="step-number">10</span>
                      <div className="step-content">
                        <h4>Set up Cron Jobs</h4>
                        <p>Bar-close scheduling for 15m, 1h, 4h, 1d</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="current-status">
                <h3>✅ Current ZmartBot Status</h3>
                <p>Your ZmartBot already has extensive alerts infrastructure implemented:</p>
                <div className="status-grid">
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <span>Enhanced Alerts API Routes</span>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <span>Cross-Signals Engine</span>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <span>Technical Indicators Services</span>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <span>WebSocket Support</span>
                  </div>
                  <div className="status-item completed">
                    <span className="status-icon">✅</span>
                    <span>Enhanced Alerts Dashboard</span>
                  </div>
                  <div className="status-item in-progress">
                    <span className="status-icon">🔄</span>
                    <span>Cron Scheduling (Ready to implement)</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveAlertsGuide;