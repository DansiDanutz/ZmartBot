import React, { useState, useEffect, useCallback } from 'react';
import './RealTimeLiveAlerts.css';
import { useAlertVolumeManager } from './AlertVolumeManager';
import IndicatorManager, { INDICATOR_RANKINGS, RANK_COLORS } from './IndicatorRankingSystem';

const RealTimeLiveAlerts = () => {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [alerts, setAlerts] = useState({});
  const [indicatorStates, setIndicatorStates] = useState({});
  const [marketSentiment, setMarketSentiment] = useState({ bullish: 0, neutral: 0, bearish: 0 });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [symbolPrices, setSymbolPrices] = useState({});
  
  // 🚀 Alert Volume Management System
  const { addRequest, addToBatch, healthStatus, reset } = useAlertVolumeManager();

  const timeframes = [
    { id: '15m', label: '15m', name: '15 Minutes' },
    { id: '1h', label: '1h', name: '1 Hour' },
    { id: '4h', label: '4h', name: '4 Hours' },
    { id: '1d', label: '1d', name: '1 Day' }
  ];

  // 🏆 RANKED: 21 Technical Indicators with Professional Ranking System
  const indicators = IndicatorManager.getAllIndicators();
  
  // 🚀 Smart Loading Strategy based on system health
  const [loadingStrategy, setLoadingStrategy] = useState('balanced');
  
  useEffect(() => {
    const strategy = IndicatorManager.getLoadingStrategy(healthStatus);
    setLoadingStrategy(strategy.strategy);
    console.log(`📊 [STRATEGY] ${strategy.description} (${strategy.strategy})`);
  }, [healthStatus]);
  
  // Helper functions using the ranking system
  const getIndicatorsByRank = (rank) => IndicatorManager.getIndicatorsByRank(rank);
  const getIndicatorsByTier = (tier) => IndicatorManager.getIndicatorsByTier(tier);
  const getCriticalIndicators = () => IndicatorManager.getCriticalIndicators();
  
  // Get indicators to load based on current strategy
  const getIndicatorsToLoad = () => {
    const strategy = IndicatorManager.getLoadingStrategy(healthStatus);
    return strategy.ranks.flatMap(rank => getIndicatorsByRank(rank));
  };

  // Fetch symbols from backend (optimized)
  const fetchSymbols = useCallback(async () => {
    try {
      console.log('🔄 Fetching symbols for Live Alerts...');
      // Use correct API endpoint without my-symbols prefix
      const response = await fetch('/api/v1/portfolio', {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache'
        }
      });
      if (response.ok) {
        const data = await response.json();
        // Handle both object with symbols property and direct array
        const symbolsList = Array.isArray(data) ? data.map(item => item.symbol) : (data.symbols || []);
        setSymbols(symbolsList);
        if (symbolsList.length > 0 && !selectedSymbol) {
          setSelectedSymbol(symbolsList[0]);
        }
        console.log('📊 Loaded symbols for Live Alerts:', symbolsList.length);
      } else {
        // Use fallback symbols to prevent loading issues
        const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT'];
        setSymbols(fallbackSymbols);
        setSelectedSymbol(fallbackSymbols[0]);
        console.log('📊 Using fallback symbols:', fallbackSymbols.length);
      }
    } catch (error) {
      console.error('❌ Error loading symbols:', error);
      const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];
      setSymbols(fallbackSymbols);
      setSelectedSymbol(fallbackSymbols[0]);
    }
  }, [selectedSymbol]);

  // 🚀 MANAGED: Fetch real-time prices with volume management
  const fetchRealTimePrices = useCallback(async (symbols) => {
    try {
      console.log(`📊 [MANAGED] Fetching prices for ${symbols.length} symbols via Volume Manager`);
      
      const pricesData = {};
      const pricePromises = [];
      
      // Use Volume Manager for each symbol to prevent API overload
      for (const symbol of symbols.slice(0, 8)) { // Limit to 8 symbols max to prevent overload
        const binanceSymbol = symbol.replace('/USDT:USDT', 'USDT').replace('/', '');
        
        const pricePromise = addRequest({
          symbol: symbol,
          timeframe: 'price', // Special timeframe for price data
          type: 'binance_ticker',
          apiEndpoint: `/api/v1/binance/ticker/24hr?symbol=${binanceSymbol}`,
          priority: 1, // High priority for price data
          callback: (data) => {
            if (data && data.lastPrice) {
              pricesData[symbol] = {
                symbol: symbol,
                price: parseFloat(data.lastPrice),
                change_24h: parseFloat(data.priceChange || 0),
                change_percent_24h: parseFloat(data.priceChangePercent || 0),
                volume_24h: parseFloat(data.volume || 0),
                high_24h: parseFloat(data.highPrice || 0),
                low_24h: parseFloat(data.lowPrice || 0),
                timestamp: new Date().toISOString(),
                source: 'binance_managed'
              };
              console.log(`✅ [PRICE] ${symbol}: $${parseFloat(data.lastPrice).toFixed(2)} (${data.priceChangePercent}%)`);
            } else {
              console.log(`❌ [PRICE ERROR] No data for ${symbol}:`, data);
            }
          },
          fallback: () => {
            // Fallback: Try direct fetch if volume manager fails
            fetch(`/api/v1/binance/ticker/24hr?symbol=${binanceSymbol}`)
              .then(res => res.json())
              .then(data => {
                if (data && data.lastPrice) {
                  pricesData[symbol] = {
                    symbol: symbol,
                    price: parseFloat(data.lastPrice),
                    change_24h: parseFloat(data.priceChange || 0),
                    change_percent_24h: parseFloat(data.priceChangePercent || 0),
                    volume_24h: parseFloat(data.volume || 0),
                    high_24h: parseFloat(data.highPrice || 0),
                    low_24h: parseFloat(data.lowPrice || 0),
                    timestamp: new Date().toISOString(),
                    source: 'binance_fallback'
                  };
                  console.log(`🔄 [FALLBACK] Got price for ${symbol}: $${parseFloat(data.lastPrice).toFixed(2)}`);
                }
              })
              .catch(err => console.log(`❌ [FALLBACK FAILED] ${symbol}:`, err.message));
          }
        });
        
        pricePromises.push(pricePromise);
      }
      
      // Wait for all managed requests to complete (with timeout)
      await Promise.allSettled(pricePromises);
      
      // Give a moment for fallbacks to complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const loadedCount = Object.keys(pricesData).length;
      const failedSymbols = symbols.filter(s => !pricesData[s]);
      
      console.log(`✅ [MANAGED] Price fetch completed: ${loadedCount}/${symbols.length} symbols`);
      if (failedSymbols.length > 0) {
        console.log(`⚠️ [MISSING PRICES] Failed symbols:`, failedSymbols);
      }
      console.log(`📊 [HEALTH] Queue: ${healthStatus.queue_length}, Cache: ${healthStatus.cache_hit_rate}%`);
      
      return pricesData;
      
    } catch (error) {
      console.error('❌ [MANAGED] Error in fetchRealTimePrices:', error);
      return {};
    }
  }, [addRequest, healthStatus]);

  // 🚀 OPTIMIZED: Managed technical data with intelligent batching
  const fetchTechnicalData = useCallback(async (symbol, timeframe = '1h') => {
    try {
      console.log(`📈 [MANAGED] Fetching technical data for ${symbol} ${timeframe}...`);
      
      // Use batch processing for multiple timeframes of same symbol
      return new Promise((resolve) => {
        addToBatch(symbol, timeframe, (data) => {
          if (data) {
            console.log(`✅ [BATCH] Got technical data for ${symbol} ${timeframe}`);
            resolve(data);
          } else {
            // Fallback to individual request with low priority
            addRequest({
              symbol: symbol,
              timeframe: timeframe,
              type: 'technical',
              apiEndpoint: `/api/real-time/technical/${symbol}`,
              priority: 4, // Lower priority than prices
              callback: (apiData) => {
                if (apiData && apiData.success && apiData.data) {
                  const realData = {
                    rsi: apiData.data.rsi,
                    rsi_14: apiData.data.rsi_14,
                    macd: apiData.data.macd,
                    macd_signal: apiData.data.macd_signal,
                    macd_histogram: apiData.data.macd_histogram,
                    price: apiData.data.price || symbolPrices[symbol]?.price,
                    trend_direction: apiData.data.trend,
                    signal_strength: apiData.data.strength
                  };
                  console.log(`✅ [MANAGED] Individual technical data for ${symbol}`);
                  resolve(realData);
                } else {
                  console.log(`❌ [MANAGED] No technical data for ${symbol}`);
                  resolve(null);
                }
              },
              fallback: null
            });
          }
        });
      });
      
    } catch (error) {
      console.error(`❌ [MANAGED] Error in technical data for ${symbol}:`, error);
      return null;
    }
  }, [addRequest, addToBatch, symbolPrices]);

  // 🏆 RANKED: Progressive alerts loading by indicator ranking
  const fetchAlertsByRank = useCallback(async (symbol, timeframe, rank = 'S') => {
    if (!symbol || !timeframe) return;
    
    const rankIndicators = getIndicatorsByRank(rank);
    const rankData = INDICATOR_RANKINGS[`RANK_${rank}`];
    
    console.log(`🏆 [RANK ${rank}] Loading ${rankIndicators.length} ${rankData.description.toLowerCase()} indicators for ${symbol} ${timeframe}`);
    
    try {
      const techData = await fetchTechnicalData(symbol, timeframe);
      if (techData) {
        const key = `${symbol}_${timeframe}`;
        
        // Process indicators in batches to prevent overload
        const batchSize = rankData.max_queue_load;
        for (let i = 0; i < rankIndicators.length; i += batchSize) {
          const batch = rankIndicators.slice(i, i + batchSize);
          
          batch.forEach((indicator, index) => {
            // Stagger requests within the batch to prevent queue flooding
            setTimeout(() => {
              addRequest({
                symbol: symbol,
                timeframe: timeframe,
                type: `indicator_${indicator.id}`,
                apiEndpoint: `/api/v1/alerts/analysis/${symbol}?timeframe=${timeframe}&indicator=${indicator.id}`,
                priority: indicator.priority,
                callback: (data) => {
                  const indicatorState = processIndicatorData(indicator.id, techData, data);
                  
                  setIndicatorStates(prev => ({
                    ...prev,
                    [key]: {
                      ...prev[key],
                      [indicator.id]: {
                        ...indicatorState,
                        rank: indicator.rank,
                        weight: indicator.weight,
                        color: rankData.color
                      }
                    }
                  }));
                  
                  console.log(`✅ [${indicator.rank}] Loaded ${indicator.name} for ${symbol}`);
                },
                fallback: null
              });
            }, index * 200); // 200ms stagger between requests in same batch
          });
          
          // Wait between batches if there are more
          if (i + batchSize < rankIndicators.length) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
        
        console.log(`✅ [RANK ${rank}] Queued ${rankIndicators.length} ${rank}-rank indicator requests`);
      }
    } catch (error) {
      console.error(`❌ [RANK ${rank}] Error fetching alerts for ${symbol}:`, error);
    }
  }, [fetchTechnicalData, addRequest, getIndicatorsByRank]);
  
  // Helper function to process individual indicator data
  const processIndicatorData = (indicatorId, techData, specificData = null) => {
    const data = specificData || techData;
    if (!data) return { status: 'neutral', value: 0 };
    
    switch (indicatorId) {
      case 'rsi':
        return { 
          status: data.rsi > 70 ? 'bearish' : data.rsi < 30 ? 'bullish' : 'neutral', 
          value: Math.round((data.rsi || 50) * 100) / 100 
        };
      case 'macd':
        return { 
          status: (data.macd_histogram || 0) > 0 ? 'bullish' : 'bearish', 
          value: Math.round((data.macd || 0) * 100) / 100 
        };
      case 'ema_cross':
        return { 
          status: (data.ema_9 || 0) > (data.ema_21 || 0) ? 'bullish' : 'bearish', 
          value: Math.round(((data.ema_9 - data.ema_21) / (data.ema_21 || 1)) * 10000) / 100 
        };
      case 'support_resistance':
        const price = data.price || 100;
        return { 
          status: price > (data.resistance_level || price) ? 'above_resistance' : 'below_resistance', 
          value: Math.round((data.support_level || price) * 100) / 100 
        };
      case 'bollinger':
        return { 
          status: (data.bollinger_upper || 0) > (data.bollinger_lower || 0) * 1.04 ? 'volatile' : 'squeeze', 
          value: Math.round(((data.bollinger_upper - data.bollinger_lower) / (data.bollinger_middle || 1)) * 10000) / 100 
        };
      default:
        return { status: 'neutral', value: 0 };
    }
  };
  
  // 🚀 INTELLIGENT: Smart progressive loading based on system health and indicator rankings
  const fetchAlertsIntelligently = useCallback(async (symbol, timeframe) => {
    if (!symbol || !timeframe) return;
    
    const strategy = IndicatorManager.getLoadingStrategy(healthStatus);
    const timings = IndicatorManager.getUpdateTimings(strategy.strategy);
    
    console.log(`🚀 [INTELLIGENT] Using '${strategy.strategy}' strategy for ${symbol} ${timeframe}`);
    console.log(`📋 [STRATEGY] ${strategy.description}`);
    
    // Load indicators by rank with intelligent timing
    let loadPromises = [];
    
    for (const rank of strategy.ranks) {
      const delay = timings[rank] || 0;
      
      const loadPromise = new Promise(async (resolve) => {
        setTimeout(async () => {
          // Double-check system health before loading
          if (healthStatus.queue_length < 15) {
            console.log(`⏰ [TIMING] Loading Rank ${rank} after ${delay}ms delay`);
            await fetchAlertsByRank(symbol, timeframe, rank);
            resolve(rank);
          } else {
            console.log(`⚠️ [SKIP] Skipping Rank ${rank} - system overloaded (queue: ${healthStatus.queue_length})`);
            resolve(`${rank}_skipped`);
          }
        }, delay);
      });
      
      loadPromises.push(loadPromise);
    }
    
    // Wait for all allowed ranks to complete
    const results = await Promise.allSettled(loadPromises);
    const completed = results.filter(r => r.status === 'fulfilled' && !r.value.includes('_skipped')).length;
    const skipped = results.length - completed;
    
    console.log(`✅ [INTELLIGENT] Completed loading for ${symbol} ${timeframe}`);
    console.log(`📊 [RESULTS] Loaded: ${completed} ranks, Skipped: ${skipped} ranks, Strategy: ${strategy.strategy}`);
    
  }, [fetchAlertsByRank, healthStatus]);
  
  // Main alerts fetching function - now uses intelligent loading
  const fetchAlerts = useCallback(async (symbol, timeframe) => {
    return fetchAlertsIntelligently(symbol, timeframe);
  }, [fetchAlertsIntelligently]);

  // 📊 Market Sentiment fetching function
  const fetchMarketSentiment = useCallback(async (symbol, timeframe) => {
    if (!symbol || !timeframe) return;
    
    try {
      console.log(`📊 [SENTIMENT] Fetching market sentiment for ${symbol} ${timeframe}...`);
      
      const response = await fetch(`/api/v1/alerts/market-sentiment/${symbol}?timeframe=${timeframe}`);
      const data = await response.json();
      
      if (data.success && data.data) {
        const sentiment = {
          bullish: data.data.bullish || 0,
          neutral: data.data.neutral || 0,
          bearish: data.data.bearish || 0
        };
        
        setMarketSentiment(sentiment);
        console.log(`✅ [SENTIMENT] ${symbol} ${timeframe}: Bullish ${sentiment.bullish}%, Neutral ${sentiment.neutral}%, Bearish ${sentiment.bearish}%`);
      } else {
        console.log(`❌ [SENTIMENT] Failed to fetch sentiment for ${symbol}: ${data.error}`);
        // Set default sentiment
        setMarketSentiment({ bullish: 33, neutral: 34, bearish: 33 });
      }
    } catch (error) {
      console.error(`❌ [SENTIMENT] Error fetching sentiment for ${symbol}:`, error);
      // Set default sentiment on error
      setMarketSentiment({ bullish: 33, neutral: 34, bearish: 33 });
    }
  }, []);

  // Fetch and update real-time prices for all symbols
  const updateSymbolPrices = useCallback(async () => {
    if (symbols.length === 0) return;
    
    try {
      console.log('💰 Updating real-time prices for all symbols...');
      const pricesData = await fetchRealTimePrices(symbols);
      setSymbolPrices(pricesData);
      console.log('✅ Updated prices for', Object.keys(pricesData).length, 'symbols');
    } catch (error) {
      console.error('❌ Error updating symbol prices:', error);
    }
  }, [symbols, fetchRealTimePrices]);

  // Initialize data
  useEffect(() => {
    const initializeData = async () => {
      await fetchSymbols();
      setLoading(false);
    };
    initializeData();
  }, [fetchSymbols]);

  // Update prices when symbols are loaded
  useEffect(() => {
    if (symbols.length > 0) {
      updateSymbolPrices();
    }
  }, [symbols, updateSymbolPrices]);

  // Fetch alerts and sentiment when symbol or timeframe changes
  useEffect(() => {
    if (selectedSymbol && selectedTimeframe) {
      fetchAlerts(selectedSymbol, selectedTimeframe);
      fetchMarketSentiment(selectedSymbol, selectedTimeframe);
    }
  }, [selectedSymbol, selectedTimeframe, fetchAlerts, fetchMarketSentiment]);

  // 🔥 OPTIMIZED: Conservative refresh strategy - 3 minutes for system stability
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('🔄 [CONSERVATIVE] Starting system-friendly update cycle...');
      
      // Only update if we have symbols and the queue isn't overloaded
      if (symbols.length > 0 && healthStatus.queue_length < 5) {
        console.log(`📊 [HEALTH CHECK] Queue: ${healthStatus.queue_length}, Cache Rate: ${healthStatus.cache_hit_rate}%`);
        
        // Update prices with delay between symbols
        setTimeout(() => updateSymbolPrices(), 2000);
        
        // Update alerts and sentiment for selected symbol only (not all combinations)
        if (selectedSymbol && selectedTimeframe) {
          setTimeout(() => {
            fetchAlerts(selectedSymbol, selectedTimeframe);
            fetchMarketSentiment(selectedSymbol, selectedTimeframe);
            setLastUpdate(new Date());
          }, 5000); // 5 second delay after prices
        }
      } else {
        console.log('⚠️ [THROTTLED] Skipping update - system overloaded or no symbols');
      }
    }, 180000); // 3 minutes instead of 1 minute - much more conservative

    return () => clearInterval(interval);
  }, [symbols, selectedSymbol, selectedTimeframe, fetchAlerts, fetchMarketSentiment, updateSymbolPrices, healthStatus]);

  const getAlertSeverityClass = (severity) => {
    switch (severity) {
      case 'strong': return 'alert-strong';
      case 'warning': return 'alert-warning';
      case 'info': return 'alert-info';
      default: return 'alert-info';
    }
  };

  const getIndicatorColor = (status) => {
    switch (status) {
      case 'bullish': return '#22c55e';
      case 'bearish': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getCurrentAlerts = () => {
    if (!selectedSymbol || !selectedTimeframe) return [];
    const key = `${selectedSymbol}_${selectedTimeframe}`;
    return alerts[key] || [];
  };

  const getIndicatorState = (indicatorId) => {
    if (!selectedSymbol || !selectedTimeframe) return 'neutral';
    const key = `${selectedSymbol}_${selectedTimeframe}`;
    const states = indicatorStates[key] || {};
    return states[indicatorId]?.status || 'neutral';
  };

  if (loading) {
    return (
      <div className="live-alerts-loading">
        <div className="loading-spinner"></div>
        <p>Loading Live Alerts System...</p>
      </div>
    );
  }

  return (
    <div className="live-alerts-container">
      <div className="live-alerts-header">
        <div className="header-title">
          <h1>🔴 Live Alerts Dashboard</h1>
          <p className="header-subtitle">
            Real-time alerts from 21 technical indicators across all timeframes
          </p>
        </div>
        <div className="system-health">
          <div className="health-stats">
            <span className={`health-indicator ${healthStatus.status}`}>
              {healthStatus.status === 'good' ? '🟢' : healthStatus.status === 'warning' ? '🟡' : '🔴'} System: {healthStatus.status}
            </span>
            <span className="queue-info">Queue: {healthStatus.queue_length}</span>
            <span className="cache-info">Cache: {healthStatus.cache_hit_rate}%</span>
            <span className={`strategy-info ${loadingStrategy}`}>
              Strategy: {loadingStrategy.toUpperCase()}
            </span>
            <span className="last-update">Updated: {lastUpdate.toLocaleTimeString()}</span>
          </div>
          <div className="update-frequency">
            <small>🏆 Intelligent Loading: Adapts indicator priorities based on system health (Updates every 3 minutes)</small>
          </div>
          <div className="indicator-stats">
            <small>
              📊 Total: {indicators.length} indicators | 
              🔥 Critical: {getCriticalIndicators().length} | 
              📈 Current: {getIndicatorsToLoad().length} will load
            </small>
          </div>
        </div>
      </div>

      {/* Horizontal Symbol Cards - 5 per row */}
      <div className="symbols-section">
        <h2>📊 Symbols ({symbols.length})</h2>
        <div className="symbols-grid-5-per-row">
          {symbols.map(symbol => (
            <div
              key={symbol}
              className={`symbol-card ${selectedSymbol === symbol ? 'selected' : ''}`}
              onClick={() => setSelectedSymbol(symbol)}
            >
              <div className="symbol-header">
                <h3>{symbol}</h3>
                <div className="symbol-status">
                  <span className={`status-dot ${getIndicatorState('overall') || 'neutral'}`}></span>
                </div>
              </div>
              
              {/* Real-time price display */}
              <div className="symbol-price-info">
                {symbolPrices[symbol] ? (
                  <>
                    <div className="current-price">
                      ${symbolPrices[symbol].price?.toFixed(2) || 'N/A'}
                    </div>
                    <div className={`price-change ${symbolPrices[symbol].change_percent_24h >= 0 ? 'positive' : 'negative'}`}>
                      {symbolPrices[symbol].change_percent_24h >= 0 ? '+' : ''}
                      {symbolPrices[symbol].change_percent_24h?.toFixed(2) || '0.00'}%
                    </div>
                  </>
                ) : (
                  <div className="price-loading">Loading...</div>
                )}
              </div>
              
              <div className="timeframes-row">
                {timeframes.map(tf => {
                  const key = `${symbol}_${tf.id}`;
                  const alertCount = (alerts[key] || []).length;
                  const hasStrongAlert = (alerts[key] || []).some(alert => alert.severity === 'strong');
                  
                  return (
                    <div
                      key={tf.id}
                      className={`timeframe-chip ${selectedSymbol === symbol && selectedTimeframe === tf.id ? 'active' : ''} ${hasStrongAlert ? 'has-strong-alert' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedSymbol(symbol);
                        setSelectedTimeframe(tf.id);
                      }}
                    >
                      <span className="tf-label">{tf.label}</span>
                      {alertCount > 0 && (
                        <span className="alert-count">{alertCount}</span>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className="sentiment-bar">
                <div className="sentiment-fill" style={{
                  background: `linear-gradient(90deg, 
                    #22c55e ${marketSentiment.bullish}%, 
                    #6b7280 ${marketSentiment.bullish}% ${marketSentiment.bullish + marketSentiment.neutral}%, 
                    #ef4444 ${marketSentiment.bullish + marketSentiment.neutral}%)`
                }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Symbol Details */}
      {selectedSymbol && (
        <div className="symbol-details">
          <div className="details-header">
            <h2>🎯 {selectedSymbol} - {timeframes.find(tf => tf.id === selectedTimeframe)?.name}</h2>
            <div className="market-sentiment">
              <h4>Market Sentiment</h4>
              <div className="sentiment-stats">
                <span className="bullish">🟢 Bullish: {marketSentiment.bullish || 0}%</span>
                <span className="neutral">⚪ Neutral: {marketSentiment.neutral || 0}%</span>
                <span className="bearish">🔴 Bearish: {marketSentiment.bearish || 0}%</span>
              </div>
            </div>
          </div>

          <div className="content-grid">
            {/* Technical Indicators Grid */}
            <div className="indicators-section">
              <h3>📈 Technical Indicators ({indicators.length})</h3>
              <div className="indicators-grid">
                {indicators.map(indicator => {
                  const status = getIndicatorState(indicator.id);
                  const statusColor = getIndicatorColor(status);
                  const indicatorInfo = IndicatorManager.getIndicatorInfo(indicator.id);
                  const isLoaded = selectedSymbol && selectedTimeframe && 
                                   indicatorStates[`${selectedSymbol}_${selectedTimeframe}`]?.[indicator.id];
                  
                  return (
                    <div
                      key={indicator.id}
                      className={`indicator-card rank-${indicator.rank} ${isLoaded ? 'loaded' : 'loading'}`}
                      style={{ 
                        borderColor: statusColor,
                        borderLeftColor: RANK_COLORS[indicator.rank]
                      }}
                    >
                      <div className="indicator-header">
                        <div className="indicator-title">
                          <span className={`rank-badge rank-${indicator.rank}`}>
                            {indicator.rank}
                          </span>
                          <span className="indicator-name">{indicator.name}</span>
                        </div>
                        <span 
                          className="indicator-status"
                          style={{ color: statusColor }}
                        >
                          {status}
                        </span>
                      </div>
                      <div className="indicator-meta">
                        <span className="indicator-weight">
                          Weight: {Math.round(indicator.weight * 100)}%
                        </span>
                        <span className="indicator-priority">
                          P{indicator.priority}
                        </span>
                      </div>
                      <div className="indicator-category">
                        {indicator.category?.replace('_', ' ') || 'N/A'}
                      </div>
                      {!isLoaded && (
                        <div className="loading-indicator">
                          <div className="loading-dot"></div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Live Alerts Feed */}
            <div className="alerts-section">
              <h3>🔔 Live Alerts ({getCurrentAlerts().length})</h3>
              <div className="alerts-feed">
                {getCurrentAlerts().length === 0 ? (
                  <div className="no-alerts">
                    <p>No alerts for {selectedSymbol} on {selectedTimeframe} timeframe</p>
                  </div>
                ) : (
                  getCurrentAlerts().map(alert => (
                    <div
                      key={alert.id}
                      className={`alert-item ${getAlertSeverityClass(alert.severity)}`}
                    >
                      <div className="alert-header">
                        <div className="alert-indicator">
                          <span className="indicator-tag">{alert.indicator.toUpperCase()}</span>
                          <span className="alert-type">{alert.type.replace('_', ' ')}</span>
                        </div>
                        <div className="alert-time">
                          {alert.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                      <div className="alert-message">
                        {alert.message}
                      </div>
                      <div className="alert-footer">
                        <span className={`alert-severity ${alert.severity}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className={`alert-status ${alert.status}`}>
                          {alert.status}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeLiveAlerts;