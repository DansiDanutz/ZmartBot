import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Cache configuration
const CACHE_CONFIG = {
  SYMBOLS: { ttl: 5 * 60 * 1000 }, // 5 minutes
  ALERTS: { ttl: 2 * 60 * 1000 }, // 2 minutes
  ALERTS_STATUS: { ttl: 1 * 60 * 1000 }, // 1 minute
  PRICE_DATA: { ttl: 30 * 1000 }, // 30 seconds
  TECHNICAL_ANALYSIS: { ttl: 2 * 60 * 1000 }, // 2 minutes
  SENTIMENT_DATA: { ttl: 5 * 60 * 1000 }, // 5 minutes
  MARKET_DATA: { ttl: 1 * 60 * 1000 } // 1 minute
};

// Cache entry structure
const createCacheEntry = (data, ttl) => ({
  data,
  timestamp: Date.now(),
  ttl,
  expiresAt: Date.now() + ttl
});

// Cache reducer
const cacheReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CACHE':
      return {
        ...state,
        [action.key]: createCacheEntry(action.data, action.ttl)
      };
    case 'CLEAR_CACHE':
      const newState = { ...state };
      delete newState[action.key];
      return newState;
    case 'CLEAR_ALL_CACHE':
      return {};
    default:
      return state;
  }
};

// Cache context
const AlertCacheContext = createContext();

// Cache provider component
export const AlertCacheProvider = ({ children }) => {
  const [cache, dispatch] = useReducer(cacheReducer, {});

  // Clear expired entries every minute
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      let hasExpired = false;
      
      Object.keys(cache).forEach(key => {
        if (cache[key].expiresAt < now) {
          dispatch({ type: 'CLEAR_CACHE', key });
          hasExpired = true;
        }
      });
      
      if (hasExpired) {
        console.log('🧹 Cleaned expired cache entries');
      }
    }, 60 * 1000);

    return () => clearInterval(interval);
  }, [cache]);

  const setCache = (key, data, ttl) => {
    dispatch({ type: 'SET_CACHE', key, data, ttl });
  };

  const getCache = (key) => {
    const entry = cache[key];
    if (!entry) return null;
    
    if (Date.now() > entry.expiresAt) {
      dispatch({ type: 'CLEAR_CACHE', key });
      return null;
    }
    
    return entry.data;
  };

  const clearCache = (key) => {
    dispatch({ type: 'CLEAR_CACHE', key });
  };

  const clearAllCache = () => {
    dispatch({ type: 'CLEAR_ALL_CACHE' });
  };

  const isCacheValid = (key) => {
    const entry = cache[key];
    return entry && Date.now() <= entry.expiresAt;
  };

  const getCacheStats = () => {
    const now = Date.now();
    const entries = Object.values(cache);
    const validEntries = entries.filter(entry => entry.expiresAt > now);
    const expiredEntries = entries.filter(entry => entry.expiresAt <= now);
    
    // Calculate memory usage (rough estimate)
    const memoryUsage = JSON.stringify(cache).length;
    
    return {
      totalEntries: entries.length,
      validEntries: validEntries.length,
      expiredEntries: expiredEntries.length,
      memoryUsage,
      hitRate: validEntries.length / Math.max(entries.length, 1)
    };
  };

  const value = {
    cache,
    setCache,
    getCache,
    clearCache,
    clearAllCache,
    isCacheValid,
    getCacheStats,
    CACHE_CONFIG
  };

  return (
    <AlertCacheContext.Provider value={value}>
      {children}
    </AlertCacheContext.Provider>
  );
};

// Custom hook to use cache
export const useAlertCache = () => {
  const context = useContext(AlertCacheContext);
  if (!context) {
    throw new Error('useAlertCache must be used within an AlertCacheProvider');
  }
  return context;
};

// Cached API functions factory
export const createCachedApi = (cacheFunctions) => {
  const { getCache, setCache, CACHE_CONFIG } = cacheFunctions;
  
  return {
    // Fetch symbols with caching
    async fetchSymbols() {
      const cacheKey = 'symbols';
      
      // Check cache first
      const cachedData = getCache(cacheKey);
      if (cachedData) {
        console.log('📦 Using cached symbols data');
        return cachedData;
      }

      try {
        console.log('🔄 Fetching fresh symbols data...');
        const response = await fetch('/api/futures-symbols/my-symbols/current');
        
        if (response.ok) {
          const data = await response.json();
          const symbolsList = data.portfolio?.symbols || [];
          
          // Cache the result
          setCache(cacheKey, symbolsList, CACHE_CONFIG.SYMBOLS.ttl);
          console.log('💾 Cached symbols data');
          
          return symbolsList;
        } else {
          console.error('❌ Failed to load symbols:', response.status);
          return [];
        }
      } catch (error) {
        console.error('❌ Error loading symbols:', error);
        return [];
      }
    },

    // Fetch alerts with caching
    async fetchAlerts() {
      const cacheKey = 'alerts';
      
      const cachedData = getCache(cacheKey);
      if (cachedData) {
        console.log('📦 Using cached alerts data');
        return cachedData;
      }

      try {
        console.log('🔄 Fetching fresh alerts data...');
        const response = await fetch('/api/v1/alerts/list');
        
        if (response.ok) {
          const data = await response.json();
          const alertsList = data.data || [];
          
          setCache(cacheKey, alertsList, CACHE_CONFIG.ALERTS.ttl);
          console.log('💾 Cached alerts data');
          
          return alertsList;
        } else {
          console.error('❌ Failed to load alerts:', response.status);
          return [];
        }
      } catch (error) {
        console.error('❌ Error loading alerts:', error);
        return [];
      }
    },

    // Fetch alerts status with caching
    async fetchAlertsStatus() {
      const cacheKey = 'alerts_status';
      
      const cachedData = getCache(cacheKey);
      if (cachedData) {
        console.log('📦 Using cached alerts status');
        return cachedData;
      }

      try {
        console.log('🔄 Fetching fresh alerts status...');
        const response = await fetch('/api/v1/alerts/status');
        
        if (response.ok) {
          const data = await response.json();
          const statusInfo = data.data || data;
          
          setCache(cacheKey, statusInfo, CACHE_CONFIG.ALERTS_STATUS.ttl);
          console.log('💾 Cached alerts status');
          
          return statusInfo;
        } else {
          console.error('❌ Failed to load alerts status:', response.status);
          return null;
        }
      } catch (error) {
        console.error('❌ Error loading alerts status:', error);
        return null;
      }
    },

    // Fetch price data with caching
    async fetchPriceData(symbol) {
      const cacheKey = `price_${symbol}`;
      
      const cachedData = getCache(cacheKey);
      if (cachedData) {
        console.log(`📦 Using cached price data for ${symbol}`);
        return cachedData;
      }

      try {
        console.log(`🔄 Fetching fresh price data for ${symbol}...`);
        const response = await fetch(`/api/v1/binance/ticker/24hr?symbol=${symbol}`);
        
        if (response.ok) {
          const data = await response.json();
          
          setCache(cacheKey, data, CACHE_CONFIG.PRICE_DATA.ttl);
          console.log(`💾 Cached price data for ${symbol}`);
          
          return data;
        } else {
          console.error(`❌ Failed to load price data for ${symbol}:`, response.status);
          return null;
        }
      } catch (error) {
        console.error(`❌ Error loading price data for ${symbol}:`, error);
        return null;
      }
    },

    // Fetch technical analysis with caching
    async fetchTechnicalAnalysis(symbol) {
      const cacheKey = `technical_${symbol}`;
      
      const cachedData = getCache(cacheKey);
      if (cachedData) {
        console.log(`📦 Using cached technical analysis for ${symbol}`);
        return cachedData;
      }

      try {
        console.log(`🔄 Fetching fresh technical analysis for ${symbol}...`);
        const response = await fetch(`http://localhost:8000/api/v1/alerts/analysis/${symbol}`);
        
        if (response.ok) {
          const data = await response.json();
          
          setCache(cacheKey, data, CACHE_CONFIG.TECHNICAL_ANALYSIS.ttl);
          console.log(`💾 Cached technical analysis for ${symbol}`);
          
          return data;
        } else {
          console.error(`❌ Failed to load technical analysis for ${symbol}:`, response.status);
          return null;
        }
      } catch (error) {
        console.error(`❌ Error loading technical analysis for ${symbol}:`, error);
        return null;
      }
    },

    // Fetch symbol data (combined price + technical)
    async fetchSymbolData(symbol) {
      try {
        const [priceData, technicalData] = await Promise.all([
          this.fetchPriceData(symbol),
          this.fetchTechnicalAnalysis(symbol)
        ]);
        
        return {
          price: priceData,
          technical: technicalData,
          symbol
        };
      } catch (error) {
        console.error(`❌ Error loading symbol data for ${symbol}:`, error);
        return null;
      }
    }
  };
};

// Cache management component
export const CacheManager = () => {
  const { getCacheStats, clearAllCache } = useAlertCache();
  const [stats, setStats] = React.useState({});

  React.useEffect(() => {
    const updateStats = () => {
      setStats(getCacheStats());
    };

    updateStats();
    const interval = setInterval(updateStats, 5000);
    return () => clearInterval(interval);
  }, [getCacheStats]);

  return (
    <div className="cache-manager">
      <div className="cache-header">
        <h3>📦 Cache Manager</h3>
        <button 
          className="clear-cache-btn"
          onClick={clearAllCache}
        >
          🗑️ Clear All Cache
        </button>
      </div>
      
      <div className="cache-stats">
        <div className="stat-item">
          <span className="stat-label">Total Entries:</span>
          <span className="stat-value">{stats.totalEntries || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Valid Entries:</span>
          <span className="stat-value success">{stats.validEntries || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Expired Entries:</span>
          <span className="stat-value warning">{stats.expiredEntries || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Memory Usage:</span>
          <span className="stat-value">{(stats.memoryUsage / 1024).toFixed(1)} KB</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Hit Rate:</span>
          <span className="stat-value">{(stats.hitRate * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
};

export default AlertCacheProvider;
