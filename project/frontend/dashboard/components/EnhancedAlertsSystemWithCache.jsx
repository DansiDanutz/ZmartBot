import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { AlertCacheProvider, useAlertCache, createCachedApi, CacheManager } from './AlertCacheManager';
import './EnhancedAlertsSystem.css';
import './AlertCacheManager.css';

const EnhancedAlertsSystemWithCache = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [symbols, setSymbols] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [expandedSymbol, setExpandedSymbol] = useState(null);
  const [technicalData, setTechnicalData] = useState({});
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [systemStatus, setSystemStatus] = useState({
    engineRunning: true,
    activeAlerts: 0,
    recentTriggers: 0,
    uptime: '24h'
  });
  const [cacheStats, setCacheStats] = useState({});
  const [showCacheManager, setShowCacheManager] = useState(false);
  const [error, setError] = useState(null);

  const cacheFunctions = useAlertCache();
  const { getCacheStats } = cacheFunctions;
  
  // Create cachedApi only once using useMemo
  const cachedApi = useMemo(() => {
    try {
      console.log('🔧 Creating cached API with functions:', Object.keys(cacheFunctions));
      return createCachedApi(cacheFunctions);
    } catch (error) {
      console.error('❌ Error creating cached API:', error);
      return null;
    }
  }, [cacheFunctions]);

  const timeframes = [
    { id: '15m', label: '15 Minutes', icon: '⏱️' },
    { id: '1h', label: '1 Hour', icon: '🕐' },
    { id: '4h', label: '4 Hours', icon: '🕓' },
    { id: '1d', label: '1 Day', icon: '📅' }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'alerts', label: 'Active Alerts', icon: '🔔' },
    { id: 'telegram', label: 'Telegram', icon: '📱' },
    { id: 'templates', label: 'Templates', icon: '📋' },
    { id: 'history', label: 'History', icon: '📈' },
    { id: 'reports', label: 'Reports', icon: '📄' }
  ];

  // Fallback function for direct API calls
  const fallbackFetch = async (url) => {
    try {
      console.log(`🔄 Fallback fetch: ${url}`);
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Fallback success: ${url}`, data);
        return data;
      } else {
        console.error(`❌ Fallback failed: ${url} - ${response.status}`);
        return null;
      }
    } catch (error) {
      console.error(`❌ Fallback error: ${url}`, error);
      return null;
    }
  };

  // Load all data using cached API or fallback
  const loadAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🔄 Loading all data with caching...');
      
      let symbolsData, alertsData, statusData;
      
      if (cachedApi) {
        console.log('📦 Using cached API...');
        // Use cached API functions
        [symbolsData, alertsData, statusData] = await Promise.all([
          cachedApi.fetchSymbols(),
          cachedApi.fetchAlerts(),
          cachedApi.fetchAlertsStatus()
        ]);
      } else {
        console.log('🔄 Using fallback API calls...');
        // Use fallback direct API calls
        [symbolsData, alertsData, statusData] = await Promise.all([
          fallbackFetch('/api/futures-symbols/my-symbols/current').then(data => data?.portfolio?.symbols || []),
          fallbackFetch('/api/v1/alerts/list').then(data => data?.data || []),
          fallbackFetch('/api/v1/alerts/status')
        ]);
      }

      console.log('📊 Symbols data received:', symbolsData);
      console.log('🔔 Alerts data received:', alertsData);
      console.log('📈 Status data received:', statusData);

      setSymbols(symbolsData || []);
      setAlerts(alertsData || []);
      
      if (statusData) {
        setSystemStatus({
          engineRunning: statusData.engine_running || true,
          activeAlerts: (alertsData || []).length,
          recentTriggers: statusData.recent_triggers || 0,
          uptime: statusData.uptime || '24h'
        });
      }

      setLastRefresh(new Date());
      console.log('✅ All data loaded successfully');
    } catch (error) {
      console.error('❌ Error loading data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [cachedApi]);

  // Auto-refresh every 15 minutes
  useEffect(() => {
    loadAllData();
    
    const interval = setInterval(() => {
      loadAllData();
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [loadAllData]);

  // Update cache stats every 30 seconds
  useEffect(() => {
    const updateCacheStats = () => {
      try {
        const stats = getCacheStats();
        setCacheStats(stats);
      } catch (error) {
        console.error('❌ Error updating cache stats:', error);
        setCacheStats({});
      }
    };

    updateCacheStats();
    const interval = setInterval(updateCacheStats, 30 * 1000);
    return () => clearInterval(interval);
  }, [getCacheStats]);

  // Handle symbol expansion with caching
  const handleExpandSymbol = async (symbol) => {
    if (expandedSymbol === symbol) {
      setExpandedSymbol(null);
    } else {
      setExpandedSymbol(symbol);
      try {
        let symbolData;
        
        if (cachedApi) {
          symbolData = await cachedApi.fetchSymbolData(symbol);
        } else {
          // Fallback: fetch price and technical data separately
          const [priceData, technicalData] = await Promise.all([
            fallbackFetch(`/api/v1/binance/ticker/24hr?symbol=${symbol}`),
            fallbackFetch(`http://localhost:8000/api/v1/alerts/analysis/${symbol}`)
          ]);
          
          symbolData = {
            price: priceData,
            technical: technicalData,
            symbol
          };
        }
        
        if (symbolData) {
          setTechnicalData(prev => ({
            ...prev,
            [symbol]: symbolData
          }));
        }
      } catch (error) {
        console.error('❌ Error loading symbol data:', error);
      }
    }
  };

  // Render cache status indicator
  const renderCacheStatus = () => (
    <div className={`cache-status ${cachedApi ? 'hit' : 'miss'}`}>
      <span>📦</span>
      <span>Cache: {cachedApi ? 'Active' : 'Fallback'} ({cacheStats.validEntries || 0} entries)</span>
      <span>•</span>
      <span>{(cacheStats.memoryUsage / 1024).toFixed(1)} KB</span>
    </div>
  );

  // Render symbol card
  const renderSymbolCard = (symbol) => {
    const isExpanded = expandedSymbol === symbol;
    const symbolTechnicalData = technicalData[symbol];
    
    return (
      <div key={symbol} className="symbol-card">
        <div className="symbol-header" onClick={() => handleExpandSymbol(symbol)}>
          <div className="symbol-info">
            <span className="symbol-name">{symbol}</span>
            <span className="symbol-status active">Active</span>
          </div>
          <div className="symbol-actions">
            <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
          </div>
        </div>
        
        {isExpanded && symbolTechnicalData && (
          <div className="symbol-details">
            <div className="technical-indicators">
              <h4>Technical Analysis</h4>
              <div className="indicators-grid">
                {symbolTechnicalData.technical && Object.entries(symbolTechnicalData.technical).map(([key, value]) => (
                  <div key={key} className="indicator">
                    <span className="indicator-name">{key}</span>
                    <span className="indicator-value">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                  </div>
                ))}
              </div>
            </div>
            
            {symbolTechnicalData.price && (
              <div className="price-info">
                <h4>Price Data</h4>
                <div className="price-grid">
                  <div className="price-item">
                    <span>Current Price:</span>
                    <span>${symbolTechnicalData.price.lastPrice}</span>
                  </div>
                  <div className="price-item">
                    <span>24h Change:</span>
                    <span className={parseFloat(symbolTechnicalData.price.priceChangePercent) >= 0 ? 'positive' : 'negative'}>
                      {symbolTechnicalData.price.priceChangePercent}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // Render content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="overview-content">
            {error && (
              <div className="error-message">
                <h3>⚠️ Error Loading Data</h3>
                <p>{error}</p>
                <button onClick={loadAllData} className="retry-btn">
                  🔄 Retry Loading
                </button>
              </div>
            )}
            
            <div className="system-status">
              <h3>System Status</h3>
              <div className="status-grid">
                <div className="status-item">
                  <span className="status-label">Engine Status:</span>
                  <span className={`status-value ${systemStatus.engineRunning ? 'running' : 'stopped'}`}>
                    {systemStatus.engineRunning ? '🟢 Running' : '🔴 Stopped'}
                  </span>
                </div>
                <div className="status-item">
                  <span className="status-label">Active Alerts:</span>
                  <span className="status-value">{systemStatus.activeAlerts}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Recent Triggers:</span>
                  <span className="status-value">{systemStatus.recentTriggers}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Uptime:</span>
                  <span className="status-value">{systemStatus.uptime}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Cache System:</span>
                  <span className={`status-value ${cachedApi ? 'running' : 'stopped'}`}>
                    {cachedApi ? '🟢 Active' : '🟡 Fallback Mode'}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="symbols-overview">
              <h3>Portfolio Symbols ({symbols.length})</h3>
              {symbols.length === 0 ? (
                <div className="no-symbols">
                  <p>No symbols loaded. Please check the console for errors.</p>
                  <button onClick={loadAllData} className="retry-btn">
                    🔄 Retry Loading
                  </button>
                </div>
              ) : (
                <div className="symbols-grid">
                  {symbols.map(symbol => renderSymbolCard(symbol))}
                </div>
              )}
            </div>
            
            {showCacheManager && <CacheManager />}
          </div>
        );
        
      case 'alerts':
        return (
          <div className="alerts-content">
            <h3>Active Alerts ({alerts.length})</h3>
            {alerts.length === 0 ? (
              <div className="no-alerts">
                <p>No active alerts at the moment.</p>
              </div>
            ) : (
              <div className="alerts-list">
                {alerts.map((alert, index) => (
                  <div key={index} className="alert-item">
                    <div className="alert-header">
                      <span className="alert-symbol">{alert.symbol}</span>
                      <span className={`alert-type ${alert.type}`}>{alert.type}</span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-timestamp">{alert.timestamp}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
        
      default:
        return (
          <div className="tab-content">
            <h3>{tabs.find(tab => tab.id === activeTab)?.label}</h3>
            <p>Content for {activeTab} tab coming soon...</p>
          </div>
        );
    }
  };

  return (
    <div className="enhanced-alerts-system">
      <div className="alerts-header">
        <div className="header-content">
          <div className="header-left">
            <h2>🔔 Enhanced Alerts System</h2>
            <p>Advanced trading alerts and notifications</p>
          </div>
          <div className="header-right">
            {renderCacheStatus()}
            <div className="refresh-info">
              <span>Last refresh: {lastRefresh.toLocaleTimeString()}</span>
              <button 
                className="refresh-btn"
                onClick={loadAllData}
                disabled={loading}
              >
                {loading ? '🔄' : '🔄'} Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="alerts-tabs">
        <div className="tab-buttons">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>
        
        <div className="tab-actions">
          <button
            className="cache-toggle-btn"
            onClick={() => setShowCacheManager(!showCacheManager)}
          >
            {showCacheManager ? '📦 Hide Cache' : '📦 Show Cache'}
          </button>
        </div>
      </div>

      <div className="alerts-content">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading data...</p>
          </div>
        ) : (
          renderTabContent()
        )}
      </div>
    </div>
  );
};

// Wrapper component that provides the cache context
const EnhancedAlertsSystemWithCacheWrapper = () => {
  return (
    <AlertCacheProvider>
      <EnhancedAlertsSystemWithCache />
    </AlertCacheProvider>
  );
};

export default EnhancedAlertsSystemWithCacheWrapper;
