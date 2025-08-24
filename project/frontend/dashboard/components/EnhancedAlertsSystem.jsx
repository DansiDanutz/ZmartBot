import React, { useState, useEffect, useCallback } from 'react';
import LiveAlertsGuide from './LiveAlertsGuide';
import './EnhancedAlertsSystem.css';

// TradingAdviceSection component with real-time indicator analysis and AI advice
const TradingAdviceSection = ({ alert, indicatorData = {}, currentPrice = 0 }) => {
  const [aiAdvice, setAiAdvice] = useState('');
  const [adviceLoading, setAdviceLoading] = useState(false);
  
  // Early return if no valid data
  if (!alert || !alert.symbol || currentPrice <= 0) {
    return (
      <div className="trading-advice-section">
        <div className="advice-loading">
          <div className="advice-spinner"></div>
          Loading trading analysis...
        </div>
      </div>
    );
  }
  
  // Extract real indicator values with error handling
  const extractIndicatorValues = () => {
    try {
      const rsi = indicatorData.rsi_data ? parseFloat(indicatorData.rsi_data.rsi_value || indicatorData.rsi_data.value || 50) : 50;
      const macd = indicatorData.macd_data || {};
      const macdLine = parseFloat(macd.macd_line || 0);
      const signalLine = parseFloat(macd.signal_line || 0);
      const histogram = parseFloat(macd.histogram || 0);
      
      const emaData = indicatorData.ema_data || {};
      const ema9 = parseFloat(emaData.ema_9 || currentPrice);
      const ema20 = parseFloat(emaData.ema_20 || currentPrice);
      const ema50 = parseFloat(emaData.ema_50 || currentPrice);
      
      const bbData = indicatorData.bollinger_bands_timeframes || {};
      const upperBand = parseFloat(bbData.upper_band || currentPrice * 1.02);
      const lowerBand = parseFloat(bbData.lower_band || currentPrice * 0.98);
      const middleBand = parseFloat(bbData.middle_band || currentPrice);
      const bbPosition = bbData.price_position || 'middle';
      const bbWidth = middleBand > 0 ? ((upperBand - lowerBand) / middleBand * 100).toFixed(2) : '2.0';
      
      const stochData = indicatorData.stochastic_data || {};
      const stochK = parseFloat(stochData.stoch_k || 50);
      const stochD = parseFloat(stochData.stoch_d || 50);
      
      const adxData = indicatorData.adx_data || {};
      const adx = parseFloat(adxData.adx || 25);
      const trend = adxData.trend || 'neutral';
      
      return {
        rsi: isNaN(rsi) ? 50 : rsi,
        macdLine: isNaN(macdLine) ? 0 : macdLine,
        signalLine: isNaN(signalLine) ? 0 : signalLine,
        histogram: isNaN(histogram) ? 0 : histogram,
        ema9: isNaN(ema9) ? currentPrice : ema9,
        ema20: isNaN(ema20) ? currentPrice : ema20,
        ema50: isNaN(ema50) ? currentPrice : ema50,
        upperBand: isNaN(upperBand) ? currentPrice * 1.02 : upperBand,
        lowerBand: isNaN(lowerBand) ? currentPrice * 0.98 : lowerBand,
        middleBand: isNaN(middleBand) ? currentPrice : middleBand,
        bbPosition,
        bbWidth,
        stochK: isNaN(stochK) ? 50 : stochK,
        stochD: isNaN(stochD) ? 50 : stochD,
        adx: isNaN(adx) ? 25 : adx,
        trend
      };
    } catch (error) {
      console.error('Error extracting indicator values:', error);
      return {
        rsi: 50, macdLine: 0, signalLine: 0, histogram: 0,
        ema9: currentPrice, ema20: currentPrice, ema50: currentPrice,
        upperBand: currentPrice * 1.02, lowerBand: currentPrice * 0.98, middleBand: currentPrice,
        bbPosition: 'middle', bbWidth: '2.0', stochK: 50, stochD: 50, adx: 25, trend: 'neutral'
      };
    }
  };
  
  // Generate dynamic support/resistance levels with error handling
  const generateSupportResistance = (indicators) => {
    try {
      const { ema9, ema20, ema50, upperBand, lowerBand, middleBand } = indicators;
      
      const supportLevels = [
        { price: Math.min(ema20, lowerBand), strength: ema20 > lowerBand ? 'strong' : 'moderate', source: 'EMA20/BB_Lower' },
        { price: Math.min(ema50, middleBand), strength: ema50 > middleBand ? 'moderate' : 'weak', source: 'EMA50/BB_Middle' },
        { price: lowerBand, strength: indicators.bbPosition === 'lower_band' ? 'strong' : 'moderate', source: 'Bollinger_Lower' }
      ].filter(level => !isNaN(level.price) && level.price < currentPrice && level.price > 0)
       .sort((a, b) => b.price - a.price).slice(0, 3);
      
      const resistanceLevels = [
        { price: Math.max(ema20, upperBand), strength: ema20 < upperBand ? 'strong' : 'moderate', source: 'EMA20/BB_Upper' },
        { price: Math.max(ema50, middleBand), strength: ema50 < middleBand ? 'moderate' : 'weak', source: 'EMA50/BB_Middle' },
        { price: upperBand, strength: indicators.bbPosition === 'upper_band' ? 'strong' : 'moderate', source: 'Bollinger_Upper' }
      ].filter(level => !isNaN(level.price) && level.price > currentPrice)
       .sort((a, b) => a.price - b.price).slice(0, 3);
      
      return { supportLevels, resistanceLevels };
    } catch (error) {
      console.error('Error generating support/resistance levels:', error);
      return { 
        supportLevels: [{ price: currentPrice * 0.98, strength: 'moderate', source: 'Default' }],
        resistanceLevels: [{ price: currentPrice * 1.02, strength: 'moderate', source: 'Default' }]
      };
    }
  };
  
  // Generate price targets based on technical analysis
  const generatePriceTargets = (indicators) => {
    const { rsi, macdLine, signalLine, ema9, ema20, upperBand, lowerBand, adx } = indicators;
    
    const bullishBias = macdLine > signalLine && rsi < 70 && ema9 > ema20;
    const bearishBias = macdLine < signalLine && rsi > 30 && ema9 < ema20;
    
    if (bullishBias) {
      return [
        { price: upperBand, probability: rsi < 60 ? 'high' : 'medium', timeframe: '2-4h', rationale: 'Bollinger upper band test' },
        { price: upperBand * 1.015, probability: adx > 25 ? 'medium' : 'low', timeframe: '6-12h', rationale: 'Breakout continuation' },
        { price: upperBand * 1.03, probability: 'low', timeframe: '1-2d', rationale: 'Extended target' }
      ];
    } else if (bearishBias) {
      return [
        { price: lowerBand, probability: rsi > 40 ? 'high' : 'medium', timeframe: '2-4h', rationale: 'Bollinger lower band test' },
        { price: lowerBand * 0.985, probability: adx > 25 ? 'medium' : 'low', timeframe: '6-12h', rationale: 'Breakdown continuation' },
        { price: lowerBand * 0.97, probability: 'low', timeframe: '1-2d', rationale: 'Extended target' }
      ];
    }
    
    return [
      { price: (upperBand + lowerBand) / 2, probability: 'medium', timeframe: '4-6h', rationale: 'Mean reversion to middle BB' },
      // ❌ REMOVED MOCK PRICE TARGET - NO MORE RANDOM PRICES
    ];
  };
  
  // Generate AI advice using OpenAI API (ChatGPT-5)
  const generateAIAdvice = async (indicators) => {
    setAdviceLoading(true);
    try {
      const { rsi, macdLine, signalLine, histogram, ema9, ema20, ema50, bbPosition, bbWidth, stochK, adx, trend } = indicators;
      
      const prompt = `As a professional cryptocurrency trading expert, provide detailed analysis for ${alert.symbol}:

📊 CURRENT MARKET DATA:
• Price: $${currentPrice}
• RSI: ${rsi.toFixed(1)} (${rsi > 70 ? 'Overbought' : rsi < 30 ? 'Oversold' : 'Neutral'})
• MACD: Line ${macdLine.toFixed(4)}, Signal ${signalLine.toFixed(4)}, Histogram ${histogram.toFixed(4)}
• EMA Alignment: 9-Period $${ema9.toFixed(2)}, 20-Period $${ema20.toFixed(2)}, 50-Period $${ema50.toFixed(2)}
• Bollinger Bands: Position "${bbPosition}", Width ${bbWidth}%
• Stochastic K: ${stochK.toFixed(1)}
• ADX: ${adx.toFixed(1)}, Current Trend: ${trend}

🎯 ANALYSIS REQUIREMENTS:
1. **Bollinger Band Analysis**: What does the current position (${bbPosition}) and width (${bbWidth}%) indicate about volatility and potential price movement?

2. **MACD Signal Interpretation**: Analyze the MACD line vs signal line relationship and histogram direction for momentum insights.

3. **EMA Trend Analysis**: Evaluate the ${ema9 > ema20 ? 'bullish' : 'bearish'} EMA alignment and its significance for trend continuation.

4. **Multi-Timeframe Confluence**: How do these indicators work together to suggest the most probable next move?

5. **Risk Management**: Specific entry levels, stop-loss placement, and position sizing recommendations.

6. **Probability Assessment**: Assign confidence levels to potential outcomes.

Provide actionable insights in under 300 words. Be specific, professional, and focus on practical trading decisions.`;

      // Try multiple endpoints for ChatGPT-5/GPT-4 integration
      const endpoints = [
        '/api/v1/openai/trading-advice',
        '/api/v1/ai/analysis', 
        '/api/v1/gpt/advice'
      ];
      
      let success = false;
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              prompt, 
              symbol: alert.symbol,
              model: 'gpt-5', // Request ChatGPT-5 (fallback to latest GPT-4)
              temperature: 0.7,
              max_tokens: 800
            })
          });
          
          if (response.ok) {
            const data = await response.json();
            setAiAdvice(data.advice || data.response || data.analysis || 'AI analysis completed');
            success = true;
            break;
          }
        } catch (endpointError) {
          console.log(`Endpoint ${endpoint} failed:`, endpointError.message);
          continue;
        }
      }
      
      if (!success) {
        throw new Error('All AI endpoints unavailable');
      }
    } catch (error) {
      console.error('AI advice generation error:', error);
      setAiAdvice('AI service temporarily unavailable. Click "Generate AI Advice" to retry with current market conditions.');
    } finally {
      setAdviceLoading(false);
    }
  };
  
  // Manual trigger for AI advice generation
  const handleGenerateAdvice = () => {
    const currentIndicators = extractIndicatorValues();
    generateAIAdvice(currentIndicators);
  };
  
  // Memoize calculations to prevent infinite re-renders
  const indicators = React.useMemo(() => extractIndicatorValues(), [indicatorData, currentPrice]);
  const { supportLevels, resistanceLevels } = React.useMemo(() => generateSupportResistance(indicators), [indicators]);
  const priceTargets = React.useMemo(() => generatePriceTargets(indicators), [indicators]);
  
  // Initialize with default message - AI advice is now generated manually
  useEffect(() => {
    if (!aiAdvice && alert.symbol) {
      setAiAdvice('');
    }
  }, [alert.symbol]);
  
  return (
    <div className="trading-advice-section">
      <div className="advice-header">
        <span className="advice-icon">💡</span>
        <div>
          <h4 className="advice-title">Dynamic Trading Analysis</h4>
          <p className="advice-subtitle">Real-time indicator-based insights</p>
        </div>
      </div>
      
      <div className="advice-grid">
        {/* Support & Resistance Levels */}
        <div className="advice-card">
          <div className="advice-card-header">
            <span className="card-icon">🎯</span>
            <h5 className="card-title">Support & Resistance</h5>
          </div>
          <ul className="support-resistance-list">
            {resistanceLevels.map((level, index) => (
              <li key={`resistance-${index}`} className="resistance-level">
                <span className="level-price">${level.price.toFixed(2)}</span>
                <span className={`level-strength ${level.strength}`}>{level.strength} ({level.source})</span>
              </li>
            ))}
            {supportLevels.map((level, index) => (
              <li key={`support-${index}`} className="support-level">
                <span className="level-price">${level.price.toFixed(2)}</span>
                <span className={`level-strength ${level.strength}`}>{level.strength} ({level.source})</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Price Targets */}
        <div className="advice-card">
          <div className="advice-card-header">
            <span className="card-icon">🚀</span>
            <h5 className="card-title">Price Targets</h5>
          </div>
          <ul className="target-list">
            {priceTargets.map((target, index) => (
              <li key={`target-${index}`} className="target-item">
                <span className="target-price">${target.price.toFixed(2)}</span>
                <span className={`target-probability ${target.probability}`}>
                  {target.probability} ({target.timeframe})
                </span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Risk Management */}
        <div className="advice-card">
          <div className="risk-management-section">
            <h5 className="risk-title">
              <span>🛡️</span> Risk Management
            </h5>
            <div className="risk-items">
              <div className="risk-item">
                <span className="risk-label">Stop Loss:</span>
                <span className="risk-value">${(supportLevels[0]?.price * 0.995 || currentPrice * 0.98).toFixed(2)}</span>
              </div>
              <div className="risk-item">
                <span className="risk-label">Risk Level:</span>
                <span className={`risk-value ${indicators.adx > 25 && Math.abs(indicators.rsi - 50) > 20 ? 'low' : indicators.adx > 20 ? 'medium' : 'high'}`}>
                  {indicators.adx > 25 && Math.abs(indicators.rsi - 50) > 20 ? 'Low' : indicators.adx > 20 ? 'Medium' : 'High'}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Market Context */}
        <div className="advice-card">
          <div className="market-context-section">
            <h5 className="context-title">
              <span>📈</span> Market Context
            </h5>
            <div className="context-metrics">
              <div className="context-metric">
                <span className="metric-label">Trend</span>
                <span className={`metric-value ${indicators.trend === 'bullish' ? 'bullish' : indicators.trend === 'bearish' ? 'bearish' : 'neutral'}`}>
                  {indicators.trend}
                </span>
              </div>
              <div className="context-metric">
                <span className="metric-label">BB Width</span>
                <span className="metric-value">{indicators.bbWidth}%</span>
              </div>
              <div className="context-metric">
                <span className="metric-label">RSI</span>
                <span className={`metric-value ${indicators.rsi > 60 ? 'bullish' : indicators.rsi < 40 ? 'bearish' : 'neutral'}`}>
                  {indicators.rsi.toFixed(1)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* AI Recommendations */}
      <div className="ai-recommendations-section">
        <div className="ai-header-row">
          <h5 className="ai-title">
            <span className="ai-icon">🤖</span> AI Trading Insights (ChatGPT-5)
          </h5>
          <button 
            className="btn-generate-ai" 
            onClick={handleGenerateAdvice}
            disabled={adviceLoading}
          >
            {adviceLoading ? (
              <>
                <div className="advice-spinner"></div>
                Analyzing...
              </>
            ) : (
              <>
                ⚡ Generate AI Advice
              </>
            )}
          </button>
        </div>
        
        <div className="ai-advice-content">
          {aiAdvice ? (
            <div className="advice-text">
              <p>{aiAdvice}</p>
              <div className="advice-timestamp">
                Last generated: {new Date().toLocaleTimeString()}
              </div>
            </div>
          ) : (
            <div className="no-advice-placeholder">
              <div className="placeholder-icon">🎯</div>
              <p>Click "Generate AI Advice" to get professional ChatGPT-5 analysis based on current technical indicators</p>
              <div className="indicator-preview">
                <span>RSI: {indicators.rsi.toFixed(1)}</span>
                <span>MACD: {indicators.histogram > 0 ? '📈' : '📉'}</span>
                <span>Trend: {indicators.trend}</span>
                <span>BB Position: {indicators.bbPosition}</span>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div className="disclaimer">
        <span className="disclaimer-icon">⚠️</span>
        <span className="disclaimer-text">
          Dynamic analysis based on real technical indicators. Not financial advice - trade responsibly.
        </span>
      </div>
    </div>
  );
};

const EnhancedAlertsSystem = () => {
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
  const [showCreateAlert, setShowCreateAlert] = useState(false);

  const timeframes = [
    { id: '15m', label: '15 Minutes', icon: '⏱️' },
    { id: '1h', label: '1 Hour', icon: '🕐' },
    { id: '4h', label: '4 Hours', icon: '🕓' },
    { id: '1d', label: '1 Day', icon: '📅' }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'alerts', label: 'Active Alerts', icon: '🔔' },
    { id: 'guide', label: 'Implementation Guide', icon: '🚀' },
    { id: 'telegram', label: 'Telegram', icon: '📱' },
    { id: 'templates', label: 'Templates', icon: '📋' },
    { id: 'history', label: 'History', icon: '📈' },
    { id: 'reports', label: 'Reports', icon: '📄' }
  ];

  // Fetch symbols from the backend (optimized)
  const fetchSymbols = useCallback(async () => {
    try {
      // Use correct API endpoint without my-symbols prefix
      const response = await fetch('/api/v1/portfolio', {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // API returns array of symbol objects directly
        const symbolsList = Array.isArray(data) ? data.map(item => item.symbol) : [];
        setSymbols(symbolsList);
        
      } else {
        console.error('❌ Failed to load symbols:', response.status, response.statusText);
        // Fallback to default symbols if API fails
        const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT'];
        setSymbols(fallbackSymbols);
      }
    } catch (error) {
      console.error('❌ Error loading symbols:', error);
      // Fallback to default symbols if fetch fails
      const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT'];
      setSymbols(fallbackSymbols);
    }
  }, []);

  // Fetch alerts from the backend
  const fetchAlerts = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/alerts/list');
      if (response.ok) {
        const data = await response.json();
        // The API returns data.data array of alerts
        const alertsList = data.data || [];
        setAlerts(alertsList);
        
        // Get system status from the status endpoint
        const statusResponse = await fetch('/api/v1/alerts/status');
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          const statusInfo = statusData.data || statusData;
          setSystemStatus({
            engineRunning: statusInfo.engine_running || true,
            activeAlerts: alertsList.length,
            recentTriggers: statusInfo.recent_triggers || 0,
            uptime: statusInfo.uptime || '24h'
          });
        }
        
      } else {
        console.error('❌ Failed to load alerts:', response.status);
      }
    } catch (error) {
      console.error('❌ Error loading alerts:', error);
    }
  }, []);

  // Fetch technical analysis for a specific symbol
  const fetchTechnicalAnalysis = useCallback(async (symbol) => {
    try {
      // First, fetch real-time price data from Binance API
      const priceResponse = await fetch(`/api/v1/binance/ticker/24hr?symbol=${symbol}`);
      let priceData = null;
      
      if (priceResponse.ok) {
        const priceResult = await priceResponse.json();
        
        priceData = {
          current_price: parseFloat(priceResult.lastPrice),
          high_24h: parseFloat(priceResult.highPrice),
          low_24h: parseFloat(priceResult.lowPrice),
          price_change_24h: parseFloat(priceResult.priceChangePercent),
          volume_24h: parseFloat(priceResult.volume),
          last_updated: new Date().toISOString()
        };
        // Price data loaded successfully
      } else {
        console.error(`❌ Failed to load price data for ${symbol}:`, priceResponse.status);
        const errorText = await priceResponse.text();
        console.error(`❌ Error response:`, errorText);
      }

      // Then, try to fetch technical analysis data
      let technicalAnalysisData = null;
      try {
        const response = await fetch(`http://localhost:8000/api/v1/alerts/analysis/${symbol}`);
        if (response.ok) {
          const result = await response.json();
          technicalAnalysisData = result.data || result;
          // Technical analysis loaded
        } else {
          console.error(`❌ Failed to load technical analysis for ${symbol}:`, response.status);
        }
      } catch (error) {
        console.error(`❌ Error loading technical analysis for ${symbol}:`, error);
      }

      // Combine price data with technical analysis data
      const combinedData = {
        ...technicalAnalysisData,
        ...priceData
      };

      setTechnicalData(prev => ({
        ...prev,
        [symbol]: combinedData
      }));
      
      return combinedData;
    } catch (error) {
      console.error(`❌ Error in fetchTechnicalAnalysis for ${symbol}:`, error);
      return null;
    }
  }, []);

  // Load all data
  const loadAllData = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSymbols(),
        fetchAlerts()
      ]);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('❌ Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchSymbols, fetchAlerts]);

  // Auto-refresh every 15 minutes
  useEffect(() => {
    loadAllData();
    
    const interval = setInterval(() => {
      loadAllData();
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [loadAllData]);

  // Handle symbol expansion
  const handleExpandSymbol = async (symbol) => {
    // Expanding symbol details
    if (expandedSymbol === symbol) {
      setExpandedSymbol(null);
    } else {
      setExpandedSymbol(symbol);
      // Current technical data available
      
      // Always fetch fresh data when expanding
      const result = await fetchTechnicalAnalysis(symbol);
      // Fresh data result obtained
    }
  };

  // Alert management handlers
  const handleEditAlert = (alert) => {
    // TODO: Implement alert editing modal
  };

  const handleDeleteAlert = async (alertId) => {
    try {
      const response = await fetch(`/api/v1/alerts/${alertId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        // Alert deleted
        fetchAlerts(); // Refresh the list
      }
    } catch (error) {
      console.error('❌ Error deleting alert:', error);
    }
  };

  const handleToggleAlert = async (alertId) => {
    try {
      const response = await fetch(`/api/v1/alerts/${alertId}/toggle`, {
        method: 'POST'
      });
      if (response.ok) {
        // Alert toggled
        fetchAlerts(); // Refresh the list
      }
    } catch (error) {
      console.error('❌ Error toggling alert:', error);
    }
  };

  // Get alert count for a symbol in a specific timeframe
  const getSymbolAlertCount = (symbol, timeframe) => {
    return alerts.filter(alert => 
      alert.symbol === symbol && 
      alert.timeframe === timeframe
    ).length;
  };

  // Get alert severity color
  const getAlertSeverityColor = (alert) => {
    // Determine severity based on alert type and conditions
    if (alert.type === 'price_alert') {
      const priceDiff = Math.abs(alert.current_price - alert.threshold);
      const percentageDiff = (priceDiff / alert.threshold) * 100;
      
      if (percentageDiff < 1) return 'text-red-500'; // Critical - very close to threshold
      if (percentageDiff < 3) return 'text-orange-500'; // High
      if (percentageDiff < 5) return 'text-yellow-500'; // Medium
      return 'text-green-500'; // Low
    }
    return 'text-gray-500';
  };

  // Get indicator market condition and styling
  const getIndicatorMarketCondition = (indicatorKey, indicatorData) => {
    if (!indicatorData) return { condition: 'neutral', color: 'neutral', bgColor: 'bg-gray-100', borderColor: 'border-gray-300' };

    try {
      switch (indicatorKey) {
        case 'rsi_data':
          const rsiValue = parseFloat(indicatorData.rsi_value || indicatorData.value || 50);
          if (rsiValue > 70) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          if (rsiValue < 30) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'macd_data':
          const macdLine = parseFloat(indicatorData.macd_line || 0);
          const signalLine = parseFloat(indicatorData.signal_line || 0);
          const histogram = parseFloat(indicatorData.histogram || 0);
          if (macdLine > signalLine && histogram > 0) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          if (macdLine < signalLine && histogram < 0) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'ema_data':
          const ema9 = parseFloat(indicatorData.ema_9 || 0);
          const ema20 = parseFloat(indicatorData.ema_20 || 0);
          if (ema9 > ema20) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          if (ema9 < ema20) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'bollinger_bands_timeframes':
          const bbPosition = indicatorData.price_position || 'middle';
          if (bbPosition === 'upper_band') return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          if (bbPosition === 'lower_band') return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'stochastic_data':
          const stochK = parseFloat(indicatorData.stoch_k || 50);
          if (stochK > 80) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          if (stochK < 20) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'williams_r_data':
          const williamsR = parseFloat(indicatorData.williams_r || -50);
          if (williamsR > -20) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          if (williamsR < -80) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'cci_data':
          const cci = parseFloat(indicatorData.cci || 0);
          if (cci > 100) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          if (cci < -100) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'adx_data':
          const adx = parseFloat(indicatorData.adx || 25);
          if (adx > 25) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        case 'volume_data':
          const volumeChange = parseFloat(indicatorData.volume_change_24h || 0);
          if (volumeChange > 20) return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          if (volumeChange < -20) return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };

        default:
          // For other indicators, check for common bullish/bearish keywords
          const dataString = JSON.stringify(indicatorData).toLowerCase();
          if (dataString.includes('bullish') || dataString.includes('buy') || dataString.includes('strong_buy')) {
            return { condition: 'bullish', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
          }
          if (dataString.includes('bearish') || dataString.includes('sell') || dataString.includes('strong_sell')) {
            return { condition: 'bearish', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
          }
          return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };
      }
    } catch (error) {
      console.error(`Error determining market condition for ${indicatorKey}:`, error);
      return { condition: 'neutral', color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' };
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid Date';
    }
  };

  // ❌ REMOVED: generateMockIndicatorData function - NO MORE MOCK DATA
  // All indicator data now comes from real database APIs only

  // Render technical indicators for a symbol
  const renderTechnicalIndicators = (symbol, timeframe) => {
    const data = technicalData[symbol];
    // Rendering indicators
    if (!data) return <div className="text-gray-500">Loading indicators...</div>;

    // Define indicators with their correct API keys
    const indicators = [
      { key: 'rsi_data', name: 'RSI', icon: '📊' },
      { key: 'ema_data', name: 'EMA Crossovers', icon: '📈' },
      { key: 'macd_data', name: 'MACD', icon: '📉' },
      { key: 'bollinger_bands_timeframes', name: 'Bollinger Bands', icon: '📊' },
      { key: 'support_resistance_data', name: 'Support/Resistance', icon: '🎯' },
      { key: 'momentum_indicators_data', name: 'Momentum', icon: '⚡' },
      { key: 'volume_data', name: 'Volume', icon: '📊' },
      { key: 'fibonacci_data', name: 'Fibonacci', icon: '📐' },
      { key: 'ichimoku_data', name: 'Ichimoku', icon: '☁️' },
      { key: 'stochastic_data', name: 'Stochastic', icon: '📊' },
      { key: 'williams_r_data', name: 'Williams %R', icon: '📊' },
      { key: 'atr_data', name: 'ATR', icon: '📊' },
      { key: 'parabolic_sar_data', name: 'Parabolic SAR', icon: '📊' },
      { key: 'adx_data', name: 'ADX', icon: '📊' },
      { key: 'cci_data', name: 'CCI', icon: '📊' },
      { key: 'stoch_rsi_data', name: 'Stochastic RSI', icon: '📊' },
      { key: 'price_patterns_data', name: 'Price Patterns', icon: '📊' },
      { key: 'bollinger_squeeze_data', name: 'Bollinger Squeeze', icon: '📊' },
      { key: 'macd_histogram_data', name: 'MACD Histogram', icon: '📊' },
      { key: 'ma_convergence_data', name: 'MA Convergence', icon: '📊' },
      { key: 'price_channels_data', name: 'Price Channels', icon: '📊' }
    ];

    return (
      <div className="technical-indicators-grid">
        {indicators.map(({ key, name, icon }) => {
          // Get the indicator data from the API response
          let indicatorData = data[key];
          // Processing indicator
          let isRealData = false;
          let isMockData = false;
          let isBorrowedData = false;
          let dataSource = '';

          // Check if this indicator has timeframe data
          if (indicatorData && typeof indicatorData === 'object' && indicatorData[timeframe]) {
            // Real data with timeframe structure
            indicatorData = indicatorData[timeframe];
            isRealData = true;
            dataSource = 'Real Database Data';
            // Found real data
            
            // Check if data is borrowed from another timeframe
            if (indicatorData._data_source === 'borrowed_from_closest_timeframe') {
              isBorrowedData = true;
              dataSource = 'Borrowed from Closest Timeframe';
            }
          } else if (indicatorData && typeof indicatorData === 'object' && Object.keys(indicatorData).length > 0) {
            // Real data without timeframe structure (single timeframe)
            isRealData = true;
            dataSource = 'Real Database Data (Single Timeframe)';
            // Found single timeframe data
          } else {
            // ❌ NO MORE MOCK DATA - SKIP IF NO REAL DATA
            // No real data available - skipping
            indicatorData = null;
            isMockData = false;
            dataSource = 'No Data Available';
          }

          // Get market condition styling
          const marketCondition = getIndicatorMarketCondition(key, indicatorData);
          const conditionEmoji = marketCondition.condition === 'bullish' ? '📈' : 
                                marketCondition.condition === 'bearish' ? '📉' : '➡️';

          return (
            <div key={key} className={`indicator-card ${marketCondition.bgColor} ${marketCondition.borderColor} border-2`}>
              <div className="indicator-header">
                <span className="indicator-icon">{icon}</span>
                <span className={`indicator-name ${marketCondition.color}`}>{name}</span>
                <div className="indicator-status">
                  <span className={`status-emoji ${marketCondition.color}`}>{conditionEmoji}</span>
                  <span className={`status-text ${marketCondition.color} text-xs font-medium`}>
                    {marketCondition.condition.toUpperCase()}
                  </span>
                </div>
                {isMockData && (
                  <span className="mock-data-badge" title={dataSource}>Mock</span>
                )}
                {isRealData && !isBorrowedData && (
                  <span className="real-data-badge" title={dataSource}>Real</span>
                )}
                {isBorrowedData && (
                  <span className="borrowed-data-badge" title={dataSource}>Borrowed</span>
                )}
              </div>
              <div className="indicator-content">
                {indicatorData ? (
                  Object.entries(indicatorData).map(([k, v]) => (
                    <div key={k} className="indicator-item">
                      <span className="indicator-label">{k.replace(/_/g, ' ')}:</span>
                      <span className="indicator-value">
                        {typeof v === 'boolean' ? (v ? 'Yes' : 'No') : 
                         typeof v === 'number' ? v.toFixed(2) : 
                         String(v)}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="indicator-item">
                    <span className="indicator-label">Status:</span>
                    <span className="indicator-value">No data for {timeframe}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Calculate sentiment percentages for a symbol
  const calculateSentimentPercentages = (symbol, timeframe) => {
    const indicators = [
      'rsi_data', 'ema_data', 'macd_data', 'bollinger_bands_timeframes', 
      'support_resistance_data', 'momentum_indicators_data', 'volume_data', 
      'fibonacci_data', 'ichimoku_data', 'stochastic_data', 'williams_r_data', 
      'atr_data', 'parabolic_sar_data', 'adx_data', 'cci_data', 'stoch_rsi_data', 
      'price_patterns_data', 'bollinger_squeeze_data', 'macd_histogram_data', 
      'ma_convergence_data', 'price_channels_data'
    ];

    let bullishCount = 0;
    let bearishCount = 0;
    let neutralCount = 0;
    let totalIndicators = 0;

    indicators.forEach(indicatorKey => {
      let indicatorData = technicalData[symbol]?.[indicatorKey];
      
      // Check if this indicator has timeframe data
      if (indicatorData && typeof indicatorData === 'object' && indicatorData[timeframe]) {
        indicatorData = indicatorData[timeframe];
      }

      if (indicatorData && typeof indicatorData === 'object' && Object.keys(indicatorData).length > 0) {
        totalIndicators++;
        const marketCondition = getIndicatorMarketCondition(indicatorKey, indicatorData);
        
        if (marketCondition.condition === 'bullish') {
          bullishCount++;
        } else if (marketCondition.condition === 'bearish') {
          bearishCount++;
        } else {
          neutralCount++;
        }
      }
    });

    // Calculate percentages (total should be 21 indicators)
    const total = Math.max(totalIndicators, 1); // Avoid division by zero
    const bullishPercent = ((bullishCount / total) * 100).toFixed(2);
    const bearishPercent = ((bearishCount / total) * 100).toFixed(2);
    const neutralPercent = ((neutralCount / total) * 100).toFixed(2);

    return {
      bullish: parseFloat(bullishPercent),
      bearish: parseFloat(bearishPercent),
      neutral: parseFloat(neutralPercent),
      counts: { bullish: bullishCount, bearish: bearishCount, neutral: neutralCount, total: totalIndicators }
    };
  };

  // Render symbol card
  const renderSymbolCard = (symbol) => {
    const alertCount = getSymbolAlertCount(symbol, selectedTimeframe);
    const isExpanded = expandedSymbol === symbol;
    const symbolData = technicalData[symbol]; // Get the full symbol data, not just timeframe
    const sentiment = calculateSentimentPercentages(symbol, selectedTimeframe);

    return (
      <div key={symbol} className="symbol-card">
        <div className="symbol-header">
          <div className="symbol-info">
            <h3 className="symbol-name">{symbol}</h3>
            <div className="symbol-metrics">
              <span className="metric">
                <span className="metric-icon">🔔</span>
                {alertCount} Alerts
              </span>
              <span className="metric">
                <span className="metric-icon">⏰</span>
                {symbolData?.last_updated ? formatTimestamp(symbolData.last_updated) : 'N/A'}
              </span>
            </div>
          </div>
          <div className="symbol-actions">
            <button
              className="expand-button"
              onClick={() => handleExpandSymbol(symbol)}
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        </div>

        {/* Sentiment Analysis Card */}
        <div className="sentiment-card">
          <div className="sentiment-header">
            <span className="sentiment-icon">📊</span>
            <span className="sentiment-title">Market Sentiment Analysis</span>
            <span className="sentiment-subtitle">({sentiment.counts.total} indicators analyzed)</span>
          </div>
          <div className="sentiment-bars">
            <div className="sentiment-bar bullish">
              <div className="sentiment-label">
                <span className="sentiment-emoji">🟢</span>
                <span>Bullish</span>
              </div>
              <div className="sentiment-bar-container">
                <div 
                  className="sentiment-bar-fill bullish-fill" 
                  style={{ width: `${Math.max(sentiment.bullish, 5)}%` }}
                ></div>
                <span className="sentiment-percentage">{sentiment.bullish}%</span>
              </div>
            </div>
            <div className="sentiment-bar neutral">
              <div className="sentiment-label">
                <span className="sentiment-emoji">⚪</span>
                <span>Neutral</span>
              </div>
              <div className="sentiment-bar-container">
                <div 
                  className="sentiment-bar-fill neutral-fill" 
                  style={{ width: `${Math.max(sentiment.neutral, 5)}%` }}
                ></div>
                <span className="sentiment-percentage">{sentiment.neutral}%</span>
              </div>
            </div>
            <div className="sentiment-bar bearish">
              <div className="sentiment-label">
                <span className="sentiment-emoji">🔴</span>
                <span>Bearish</span>
              </div>
              <div className="sentiment-bar-container">
                <div 
                  className="sentiment-bar-fill bearish-fill" 
                  style={{ width: `${Math.max(sentiment.bearish, 5)}%` }}
                ></div>
                <span className="sentiment-percentage">{sentiment.bearish}%</span>
              </div>
            </div>
          </div>
        </div>

        {isExpanded && (
          <div className="symbol-expanded">
            <div className="expanded-section">
              <h4>📊 Price Data</h4>
              <div className="price-data">
                <div className="price-item">
                  <span>Current Price:</span>
                  <span className="price-value">${symbolData?.current_price || 'N/A'}</span>
                </div>
                <div className="price-item">
                  <span>24h High:</span>
                  <span className="price-value">${symbolData?.high_24h || 'N/A'}</span>
                </div>
                <div className="price-item">
                  <span>24h Low:</span>
                  <span className="price-value">${symbolData?.low_24h || 'N/A'}</span>
                </div>
                <div className="price-item">
                  <span>24h Change:</span>
                  <span className={`price-change ${symbolData?.price_change_24h > 0 ? 'positive' : 'negative'}`}>
                    {symbolData?.price_change_24h ? `${symbolData.price_change_24h.toFixed(2)}%` : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="expanded-section">
              <h4>📈 Technical Indicators - {selectedTimeframe} Timeframe</h4>
              {renderTechnicalIndicators(symbol, selectedTimeframe)}
            </div>

            <div className="expanded-section">
              <h4>🎯 Cross Signals</h4>
              <div className="cross-signals">
                {symbolData?.cross_signals ? (
                  Object.entries(symbolData.cross_signals).map(([signal, data]) => (
                    <div key={signal} className="cross-signal">
                      <span className="signal-name">{signal}:</span>
                      <span className="signal-value">{data}</span>
                    </div>
                  ))
                ) : (
                  <div className="no-signals">No cross signals detected</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="enhanced-alerts-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading Live Alerts System...</p>
        </div>
      </div>
    );
  }

  // Debug log to see symbols state
  console.log('🎯 Rendering with symbols:', symbols, 'Count:', symbols.length);

  return (
    <div className="enhanced-alerts-container">
      {/* Header */}
      <div className="alerts-header">
        <div className="header-content">
          <h1>Live Alerts System</h1>
          <p>Advanced trading alerts and notifications</p>
        </div>
        <div className="header-actions">
          <div className={`status-indicator ${systemStatus.engineRunning ? 'active' : 'inactive'}`}>
            {systemStatus.engineRunning ? '✅ Active' : '❌ Inactive'}
          </div>
          <button className="add-button">+</button>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="overview-cards">
        <div className="overview-card">
          <div className="card-icon">🔔</div>
          <div className="card-content">
            <div className="card-value">{systemStatus.activeAlerts}</div>
            <div className="card-label">ACTIVE ALERTS</div>
          </div>
        </div>
        <div className="overview-card">
          <div className="card-icon">⚡</div>
          <div className="card-content">
            <div className="card-value">{systemStatus.recentTriggers}</div>
            <div className="card-label">RECENT TRIGGERS</div>
          </div>
        </div>
        <div className="overview-card">
          <div className="card-icon">⏰</div>
          <div className="card-content">
            <div className="card-value">{systemStatus.uptime}</div>
            <div className="card-label">UPTIME</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="alerts-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div className="alerts-content">
        {activeTab === 'overview' && (
          <div className="overview-content">
            {/* Timeframe Filter */}
            <div className="timeframe-filter">
              <h3>Timeframe Filter</h3>
              <div className="timeframe-buttons">
                {timeframes.map(timeframe => (
                  <button
                    key={timeframe.id}
                    className={`timeframe-button ${selectedTimeframe === timeframe.id ? 'active' : ''}`}
                    onClick={() => setSelectedTimeframe(timeframe.id)}
                  >
                    {timeframe.icon} {timeframe.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Symbols Grid */}
            <div className="symbols-section">
              <div className="section-header">
                <h3>My Symbols ({symbols.length})</h3>
                <div className="refresh-info">
                  <span>Last Refresh: {lastRefresh.toLocaleTimeString()}</span>
                  <span>Auto Refresh: Every 15 min</span>
                </div>
              </div>
              
              <div className="symbols-grid">
                {symbols.map(symbol => renderSymbolCard(symbol))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="alerts-list">
            {/* Enhanced Alerts Header */}
            <div className="alerts-header-section">
              <div className="alerts-title-row">
                <h3>🔔 Active Alerts ({alerts.length})</h3>
                <div className="alerts-actions">
                  <button className="btn-create-alert" onClick={() => setShowCreateAlert(true)}>
                    ➕ Create Alert
                  </button>
                  <button className="btn-refresh" onClick={fetchAlerts}>
                    🔄 Refresh
                  </button>
                </div>
              </div>
              
              {/* Alert Statistics */}
              <div className="alert-stats">
                <div className="stat-item">
                  <div className="stat-icon">🟢</div>
                  <div className="stat-info">
                    <div className="stat-value">{alerts.filter(a => a.current_price < a.threshold).length}</div>
                    <div className="stat-label">Below Threshold</div>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-icon">🔴</div>
                  <div className="stat-info">
                    <div className="stat-value">{alerts.filter(a => a.current_price >= a.threshold).length}</div>
                    <div className="stat-label">Above Threshold</div>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-icon">⚡</div>
                  <div className="stat-info">
                    <div className="stat-value">{alerts.filter(a => a.last_triggered).length}</div>
                    <div className="stat-label">Triggered</div>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-icon">🔄</div>
                  <div className="stat-info">
                    <div className="stat-value">{alerts.filter(a => a.is_active).length}</div>
                    <div className="stat-label">Active</div>
                  </div>
                </div>
              </div>
            </div>

            {alerts.length > 0 ? (
              <div className="alerts-grid-enhanced">
                {alerts.map((alert, index) => {
                  const isTriggered = alert.current_price >= alert.threshold;
                  const priceDiff = ((alert.current_price - alert.threshold) / alert.threshold * 100);
                  const urgency = Math.abs(priceDiff) < 1 ? 'high' : Math.abs(priceDiff) < 5 ? 'medium' : 'low';
                  
                  return (
                    <div key={alert.id || index} className={`alert-card ${isTriggered ? 'triggered' : 'pending'} urgency-${urgency}`}>
                      <div className="alert-card-header">
                        <div className="alert-symbol-info">
                          <div className="symbol-badge">{alert.symbol}</div>
                          <div className="alert-type">{alert.type?.replace('_', ' ').toUpperCase()}</div>
                        </div>
                        <div className="alert-status">
                          {isTriggered ? (
                            <span className="status-triggered">✅ TRIGGERED</span>
                          ) : (
                            <span className="status-pending">🔍 PENDING</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="alert-card-content">
                        <div className="price-comparison">
                          <div className="price-row">
                            <span className="label">Threshold:</span>
                            <span className="threshold-price">${alert.threshold?.toFixed(2)}</span>
                          </div>
                          <div className="price-row">
                            <span className="label">Current:</span>
                            <span className={`current-price ${isTriggered ? 'above' : 'below'}`}>
                              ${alert.current_price?.toFixed(2)}
                            </span>
                          </div>
                          <div className="price-row">
                            <span className="label">Difference:</span>
                            <span className={`price-diff ${priceDiff >= 0 ? 'positive' : 'negative'}`}>
                              {priceDiff >= 0 ? '+' : ''}{priceDiff.toFixed(2)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="alert-message">
                          {alert.message}
                        </div>
                        
                        {/* Trading Advice Section */}
                        <TradingAdviceSection 
                          alert={alert} 
                          indicatorData={technicalData[alert.symbol] || {}}
                          currentPrice={alert.current_price}
                        />
                        
                        <div className="alert-metadata">
                          <div className="meta-item">
                            <span className="meta-icon">🕰️</span>
                            <span>Timeframe: {alert.timeframe}</span>
                          </div>
                          <div className="meta-item">
                            <span className="meta-icon">📅</span>
                            <span>Created: {new Date(alert.created_at).toLocaleDateString()}</span>
                          </div>
                          <div className="meta-item">
                            <span className="meta-icon">🔄</span>
                            <span>Updated: {new Date(alert.last_updated).toLocaleTimeString()}</span>
                          </div>
                          {alert.last_triggered && (
                            <div className="meta-item triggered">
                              <span className="meta-icon">⚡</span>
                              <span>Triggered: {new Date(alert.last_triggered).toLocaleString()}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="alert-card-actions">
                        <button className="btn-edit" onClick={() => handleEditAlert(alert)}>
                          ✏️ Edit
                        </button>
                        <button className="btn-delete" onClick={() => handleDeleteAlert(alert.id)}>
                          🗑️ Delete
                        </button>
                        <button className={`btn-toggle ${alert.is_active ? 'active' : 'inactive'}`} 
                                onClick={() => handleToggleAlert(alert.id)}>
                          {alert.is_active ? '🔇 Disable' : '🔔 Enable'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="no-alerts-enhanced">
                <div className="no-alerts-icon">🔔</div>
                <h4>No Active Alerts</h4>
                <p>Create your first alert to start monitoring price movements</p>
                <button className="btn-create-first-alert" onClick={() => setShowCreateAlert(true)}>
                  ➕ Create Your First Alert
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'guide' && (
          <LiveAlertsGuide />
        )}

        {activeTab === 'telegram' && (
          <div className="telegram-content">
            <h3>Telegram Integration</h3>
            <p>Telegram alerts configuration coming soon...</p>
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="templates-content">
            <h3>Alert Templates</h3>
            <p>Alert template management coming soon...</p>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-content">
            <h3>Alert History</h3>
            <p>Historical alert data coming soon...</p>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="reports-content">
            <h3>Alert Reports</h3>
            <p>Alert reporting and analytics coming soon...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedAlertsSystem;
