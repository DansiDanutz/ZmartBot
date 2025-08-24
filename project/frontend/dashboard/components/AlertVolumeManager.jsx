import React, { useState, useEffect, useCallback } from 'react';

/**
 * Alert Volume Manager
 * Intelligent system to manage high-volume alerts and prevent API overload
 * Handles 21 indicators × 4 timeframes × multiple symbols efficiently
 */

class AlertVolumeManager {
  constructor() {
    // Request throttling configuration
    this.requestQueue = [];
    this.activeRequests = new Set();
    this.maxConcurrentRequests = 3; // Limit concurrent API calls
    this.requestDelay = 1000; // 1 second between requests
    this.lastRequestTime = 0;
    
    // Caching system
    this.cache = new Map();
    this.cacheTimeout = 30000; // 30 seconds cache
    
    // Priority system for timeframes
    this.timeframePriority = {
      '1h': 1,   // Highest priority
      '4h': 2,   // Medium-high priority  
      '1d': 3,   // Medium priority
      '15m': 4   // Lowest priority (most frequent, less critical)
    };
    
    // Request batching
    this.batchQueue = [];
    this.batchSize = 5;
    this.batchTimeout = 2000; // 2 seconds
    this.batchTimer = null;
    
    // Rate limiting per API
    this.apiLimits = {
      'binance': { limit: 10, window: 60000, requests: [] }, // 10 req/min
      'cryptometer': { limit: 5, window: 60000, requests: [] }, // 5 req/min
      'technical': { limit: 20, window: 60000, requests: [] } // 20 req/min
    };
    
    // Alert volume tracking
    this.alertStats = {
      totalAlerts: 0,
      activeAlerts: 0,
      queuedRequests: 0,
      cachedResponses: 0,
      throttledRequests: 0,
      lastUpdate: new Date()
    };
  }
  
  /**
   * Add request to managed queue with priority
   */
  addRequest(requestConfig) {
    const {
      symbol,
      timeframe,
      type,
      apiEndpoint,
      priority = this.timeframePriority[timeframe] || 5,
      callback,
      fallback
    } = requestConfig;
    
    const requestId = `${symbol}_${timeframe}_${type}`;
    
    // Check cache first
    const cacheKey = `${symbol}_${timeframe}_${type}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      console.log(`📦 Using cached data for ${requestId}`);
      callback(cached);
      this.alertStats.cachedResponses++;
      return Promise.resolve(cached);
    }
    
    // Add to queue with priority
    const request = {
      id: requestId,
      symbol,
      timeframe,
      type,
      apiEndpoint,
      priority,
      callback,
      fallback,
      timestamp: Date.now(),
      retries: 0,
      maxRetries: 2
    };
    
    this.requestQueue.push(request);
    this.requestQueue.sort((a, b) => a.priority - b.priority); // Higher priority first
    
    this.alertStats.queuedRequests = this.requestQueue.length;
    
    console.log(`📋 Queued request ${requestId} (Priority: ${priority}, Queue: ${this.requestQueue.length})`);
    
    // Process queue
    this.processQueue();
    
    return new Promise((resolve) => {
      request.resolve = resolve;
    });
  }
  
  /**
   * Process request queue with intelligent throttling
   */
  async processQueue() {
    // Don't process if we're at max concurrent requests
    if (this.activeRequests.size >= this.maxConcurrentRequests) {
      console.log(`🚦 Max concurrent requests reached (${this.activeRequests.size})`);
      return;
    }
    
    // Don't process if we need to wait for rate limiting
    const now = Date.now();
    if (now - this.lastRequestTime < this.requestDelay) {
      setTimeout(() => this.processQueue(), this.requestDelay);
      return;
    }
    
    const request = this.requestQueue.shift();
    if (!request) return;
    
    this.alertStats.queuedRequests = this.requestQueue.length;
    
    // Check API rate limiting
    const apiType = this.getApiType(request.apiEndpoint);
    if (!this.canMakeRequest(apiType)) {
      console.log(`⏳ Rate limit exceeded for ${apiType}, re-queuing ${request.id}`);
      this.alertStats.throttledRequests++;
      // Re-queue with lower priority
      request.priority += 1;
      this.requestQueue.push(request);
      this.requestQueue.sort((a, b) => a.priority - b.priority);
      setTimeout(() => this.processQueue(), 5000); // Try again in 5 seconds
      return;
    }
    
    // Execute request
    this.executeRequest(request);
    this.lastRequestTime = now;
    
    // Continue processing queue after delay
    setTimeout(() => this.processQueue(), this.requestDelay);
  }
  
  /**
   * Execute individual request with error handling
   */
  async executeRequest(request) {
    const { id, apiEndpoint, callback, fallback } = request;
    
    this.activeRequests.add(id);
    console.log(`🚀 Executing request ${id} (Active: ${this.activeRequests.size})`);
    
    try {
      // Record API usage
      const apiType = this.getApiType(apiEndpoint);
      this.recordApiRequest(apiType);
      
      const response = await fetch(apiEndpoint, {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Cache successful response
        const cacheKey = `${request.symbol}_${request.timeframe}_${request.type}`;
        this.setCache(cacheKey, data);
        
        callback(data);
        request.resolve && request.resolve(data);
        
        console.log(`✅ Completed request ${id}`);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
      
    } catch (error) {
      console.error(`❌ Request failed ${id}:`, error.message);
      
      // Retry logic
      if (request.retries < request.maxRetries) {
        request.retries++;
        request.priority += 2; // Lower priority for retry
        this.requestQueue.push(request);
        this.requestQueue.sort((a, b) => a.priority - b.priority);
        console.log(`🔄 Retrying ${id} (${request.retries}/${request.maxRetries})`);
      } else {
        // Use fallback if available
        if (fallback) {
          console.log(`🆘 Using fallback for ${id}`);
          callback(fallback);
          request.resolve && request.resolve(fallback);
        } else {
          console.log(`💀 Request ${id} failed permanently`);
          request.resolve && request.resolve(null);
        }
      }
    } finally {
      this.activeRequests.delete(id);
      this.updateAlertStats();
    }
  }
  
  /**
   * Cache management
   */
  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
  
  getFromCache(key) {
    const cached = this.cache.get(key);
    if (cached && (Date.now() - cached.timestamp < this.cacheTimeout)) {
      return cached.data;
    }
    if (cached) {
      this.cache.delete(key); // Remove expired cache
    }
    return null;
  }
  
  /**
   * API rate limiting
   */
  getApiType(endpoint) {
    if (endpoint.includes('binance')) return 'binance';
    if (endpoint.includes('cryptometer')) return 'cryptometer';
    return 'technical';
  }
  
  canMakeRequest(apiType) {
    const limit = this.apiLimits[apiType];
    if (!limit) return true;
    
    const now = Date.now();
    // Clean old requests
    limit.requests = limit.requests.filter(time => now - time < limit.window);
    
    return limit.requests.length < limit.limit;
  }
  
  recordApiRequest(apiType) {
    const limit = this.apiLimits[apiType];
    if (limit) {
      limit.requests.push(Date.now());
    }
  }
  
  /**
   * Batch processing for similar requests
   */
  addToBatch(symbol, timeframe, callback) {
    this.batchQueue.push({ symbol, timeframe, callback });
    
    if (this.batchQueue.length >= this.batchSize) {
      this.processBatch();
    } else if (!this.batchTimer) {
      this.batchTimer = setTimeout(() => {
        this.processBatch();
      }, this.batchTimeout);
    }
  }
  
  processBatch() {
    if (this.batchQueue.length === 0) return;
    
    console.log(`📦 Processing batch of ${this.batchQueue.length} requests`);
    
    const batch = this.batchQueue.splice(0, this.batchSize);
    
    // Group by API endpoint for efficiency
    const grouped = batch.reduce((acc, item) => {
      const key = `${item.symbol}_batch`;
      if (!acc[key]) acc[key] = [];
      acc[key].push(item);
      return acc;
    }, {});
    
    // Execute batched requests
    Object.keys(grouped).forEach(key => {
      const items = grouped[key];
      this.executeBatchRequest(items);
    });
    
    clearTimeout(this.batchTimer);
    this.batchTimer = null;
  }
  
  async executeBatchRequest(items) {
    const symbol = items[0].symbol;
    console.log(`🎯 Executing batch for ${symbol} (${items.length} timeframes)`);
    
    try {
      // Single API call for all timeframes
      const response = await fetch(`/api/v1/alerts/analysis/${symbol}`, {
        method: 'GET',
        headers: { 'Cache-Control': 'no-cache' }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Distribute data to callbacks
        items.forEach(item => {
          const timeframeData = data.data?.[`${item.timeframe}_data`] || null;
          item.callback(timeframeData);
          
          // Cache individual timeframe data
          this.setCache(`${symbol}_${item.timeframe}_batch`, timeframeData);
        });
        
        console.log(`✅ Batch completed for ${symbol}`);
      }
    } catch (error) {
      console.error(`❌ Batch failed for ${symbol}:`, error);
      
      // Fallback to individual requests
      items.forEach(item => {
        this.addRequest({
          symbol: item.symbol,
          timeframe: item.timeframe,
          type: 'individual_fallback',
          apiEndpoint: `/api/v1/cryptometer/analyze/${item.symbol}?timeframe=${item.timeframe}`,
          priority: 5,
          callback: item.callback
        });
      });
    }
  }
  
  /**
   * Update statistics
   */
  updateAlertStats() {
    this.alertStats = {
      ...this.alertStats,
      queuedRequests: this.requestQueue.length,
      activeRequests: this.activeRequests.size,
      lastUpdate: new Date()
    };
  }
  
  /**
   * Get system health status
   */
  getHealthStatus() {
    const queueHealth = this.requestQueue.length < 10 ? 'good' : 
                       this.requestQueue.length < 20 ? 'warning' : 'critical';
                       
    const cacheHitRate = this.alertStats.cachedResponses / 
                        (this.alertStats.cachedResponses + this.alertStats.queuedRequests + 1) * 100;
    
    return {
      status: queueHealth,
      queue_length: this.requestQueue.length,
      active_requests: this.activeRequests.size,
      cache_hit_rate: Math.round(cacheHitRate),
      throttled_requests: this.alertStats.throttledRequests,
      cache_size: this.cache.size,
      api_limits: this.apiLimits
    };
  }
  
  /**
   * Clear cache and reset system
   */
  reset() {
    this.cache.clear();
    this.requestQueue.length = 0;
    this.activeRequests.clear();
    this.batchQueue.length = 0;
    
    Object.keys(this.apiLimits).forEach(api => {
      this.apiLimits[api].requests = [];
    });
    
    console.log('🔄 Alert Volume Manager reset');
  }
}

// Create global instance
const alertVolumeManager = new AlertVolumeManager();

// React Hook for using Alert Volume Manager
export const useAlertVolumeManager = () => {
  const [healthStatus, setHealthStatus] = useState(alertVolumeManager.getHealthStatus());
  
  useEffect(() => {
    const interval = setInterval(() => {
      setHealthStatus(alertVolumeManager.getHealthStatus());
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  return {
    addRequest: (config) => alertVolumeManager.addRequest(config),
    addToBatch: (symbol, timeframe, callback) => alertVolumeManager.addToBatch(symbol, timeframe, callback),
    healthStatus,
    reset: () => alertVolumeManager.reset()
  };
};

export default alertVolumeManager;