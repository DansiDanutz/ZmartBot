import React, { useState, useEffect, useCallback } from 'react';
import './EnhancedAlertsSystem.css';

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

  // Fetch symbols from the backend
  const fetchSymbols = useCallback(async () => {
    try {
      console.log('🔄 Fetching symbols from API...');
      const response = await fetch('/api/futures-symbols/my-symbols/current');
      console.log('📡 API Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Raw API data:', data);
        
        const symbolsList = data.portfolio?.symbols || [];
        console.log('🎯 Extracted symbols:', symbolsList);
        console.log('📈 Number of symbols:', symbolsList.length);
        
        setSymbols(symbolsList);
        
        // Verify the state was set
        setTimeout(() => {
          console.log('✅ Symbols state after set:', symbolsList);
        }, 100);
        
      } else {
        console.error('❌ Failed to load symbols:', response.status, response.statusText);
        // Fallback to default symbols if API fails
        const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT'];
        setSymbols(fallbackSymbols);
        console.log('🔄 Using fallback symbols:', fallbackSymbols);
      }
    } catch (error) {
      console.error('❌ Error loading symbols:', error);
      // Fallback to default symbols if fetch fails
      const fallbackSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT'];
      setSymbols(fallbackSymbols);
      console.log('🔄 Using fallback symbols due to error:', fallbackSymbols);
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
        
        console.log('🔔 Loaded alerts:', alertsList.length, 'alerts');
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
      console.log(`🔄 Fetching price data for ${symbol}...`);
      const priceResponse = await fetch(`/api/v1/binance/ticker/24hr?symbol=${symbol}`);
      let priceData = null;
      
      console.log(`📡 Price API response status:`, priceResponse.status);
      
      if (priceResponse.ok) {
        const priceResult = await priceResponse.json();
        console.log(`📊 Raw price data for ${symbol}:`, priceResult);
        
        priceData = {
          current_price: parseFloat(priceResult.lastPrice),
          high_24h: parseFloat(priceResult.highPrice),
          low_24h: parseFloat(priceResult.lowPrice),
          price_change_24h: parseFloat(priceResult.priceChangePercent),
          volume_24h: parseFloat(priceResult.volume),
          last_updated: new Date().toISOString()
        };
        console.log(`✅ Loaded price data for ${symbol}:`, priceData);
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
          console.log(`✅ Loaded technical analysis for ${symbol}:`, technicalAnalysisData);
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
    console.log(`🔍 Expanding symbol: ${symbol}`);
    if (expandedSymbol === symbol) {
      setExpandedSymbol(null);
    } else {
      setExpandedSymbol(symbol);
      console.log(`📊 Current technical data for ${symbol}:`, technicalData[symbol]);
      
      // Always fetch fresh data when expanding
      console.log(`🔄 Fetching fresh data for ${symbol}...`);
      const result = await fetchTechnicalAnalysis(symbol);
      console.log(`✅ Fetch result for ${symbol}:`, result);
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

  // Generate mock data for indicators based on actual database schema
  const generateMockIndicatorData = (indicatorKey, timeframe) => {
    // Base data that changes based on timeframe
    const timeframeData = {
      '15m': {
        basePrice: 45000.0,
        volatility: 0.8,
        trend: 'bullish',
        rsiBase: 65.4,
        macdBase: 125.5,
        volumeBase: 1450000.0
      },
      '1h': {
        basePrice: 44800.0,
        volatility: 0.6,
        trend: 'neutral',
        rsiBase: 58.2,
        macdBase: 98.2,
        volumeBase: 1250000.0
      },
      '4h': {
        basePrice: 44500.0,
        volatility: 0.4,
        trend: 'bearish',
        rsiBase: 42.8,
        macdBase: -45.3,
        volumeBase: 980000.0
      },
      '1d': {
        basePrice: 44200.0,
        volatility: 0.2,
        trend: 'strong_bearish',
        rsiBase: 35.6,
        macdBase: -125.8,
        volumeBase: 750000.0
      }
    };

    const tf = timeframeData[timeframe] || timeframeData['1h'];
    
    const mockData = {
      // RSI Data - Different for each timeframe
      rsi_data: {
        rsi_value: tf.rsiBase + (Math.random() * 10 - 5), // Vary by ±5
        signal_status: tf.rsiBase > 70 ? 'overbought' : tf.rsiBase < 30 ? 'oversold' : 'neutral',
        overbought_level: 70.0,
        oversold_level: 30.0,
        divergence_type: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none',
        divergence_strength: tf.trend === 'bullish' ? 0.7 : tf.trend === 'bearish' ? 0.6 : 0.0,
        current_price: tf.basePrice
      },
      
      // EMA Data - Different for each timeframe
      ema_data: {
        ema_9: tf.basePrice + (tf.trend === 'bullish' ? 150 : tf.trend === 'bearish' ? -150 : 50),
        ema_12: tf.basePrice + (tf.trend === 'bullish' ? 120 : tf.trend === 'bearish' ? -120 : 30),
        ema_20: tf.basePrice + (tf.trend === 'bullish' ? 80 : tf.trend === 'bearish' ? -80 : 20),
        ema_21: tf.basePrice + (tf.trend === 'bullish' ? 70 : tf.trend === 'bearish' ? -70 : 10),
        ema_26: tf.basePrice + (tf.trend === 'bullish' ? 50 : tf.trend === 'bearish' ? -50 : 0),
        ema_50: tf.basePrice + (tf.trend === 'bullish' ? -200 : tf.trend === 'bearish' ? 200 : -100),
        cross_signal: tf.trend === 'bullish' ? 'golden_cross' : tf.trend === 'bearish' ? 'death_cross' : 'none',
        cross_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.3,
        golden_cross_detected: tf.trend === 'bullish',
        death_cross_detected: tf.trend === 'bearish',
        short_term_trend: tf.trend,
        long_term_trend: tf.trend === 'strong_bearish' ? 'bearish' : tf.trend
      },
      
      // MACD Data - Different for each timeframe
      macd_data: {
        macd_line: tf.macdBase,
        signal_line: tf.macdBase + (tf.trend === 'bullish' ? -25 : tf.trend === 'bearish' ? 25 : 0),
        histogram: tf.macdBase - (tf.macdBase + (tf.trend === 'bullish' ? -25 : tf.trend === 'bearish' ? 25 : 0)),
        signal_status: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        current_price: tf.basePrice
      },
      
      // Bollinger Bands Data - Different for each timeframe
      bollinger_bands_data: {
        sma: tf.basePrice,
        upper_band: tf.basePrice + (1700 * tf.volatility),
        lower_band: tf.basePrice - (1700 * tf.volatility),
        bandwidth: 7.6 * tf.volatility,
        position: tf.trend === 'bullish' ? 65.2 : tf.trend === 'bearish' ? 35.8 : 50.0
      },
      
      // Support/Resistance Data - Different for each timeframe
      support_resistance_data: {
        support_level_1: tf.basePrice - (500 * tf.volatility),
        support_level_2: tf.basePrice - (1000 * tf.volatility),
        support_level_3: tf.basePrice - (1500 * tf.volatility),
        resistance_level_1: tf.basePrice + (500 * tf.volatility),
        resistance_level_2: tf.basePrice + (1000 * tf.volatility),
        resistance_level_3: tf.basePrice + (1500 * tf.volatility),
        price_position: tf.trend === 'bullish' ? 'above_support' : tf.trend === 'bearish' ? 'below_resistance' : 'middle_range',
        nearest_support: tf.basePrice - (500 * tf.volatility),
        nearest_resistance: tf.basePrice + (500 * tf.volatility),
        support_strength: tf.trend === 'bearish' ? 0.9 : 0.7,
        resistance_strength: tf.trend === 'bullish' ? 0.9 : 0.7,
        breakout_potential: tf.trend === 'bullish' ? 'high_bullish' : tf.trend === 'bearish' ? 'high_bearish' : 'medium',
        breakout_direction: tf.trend,
        breakout_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.5
      },
      
      // Momentum Data - Different for each timeframe
      momentum_data: {
        roc_value: tf.trend === 'bullish' ? 2.5 : tf.trend === 'bearish' ? -2.5 : 0.5,
        roc_signal: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        roc_strength: tf.trend === 'bullish' ? 0.7 : tf.trend === 'bearish' ? 0.6 : 0.3,
        roc_divergence: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none',
        mom_value: tf.trend === 'bullish' ? 850.0 : tf.trend === 'bearish' ? -850.0 : 150.0,
        mom_signal: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        mom_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.4,
        mom_divergence: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none',
        momentum_status: tf.trend === 'bullish' ? 'strong_bullish' : tf.trend === 'bearish' ? 'strong_bearish' : 'neutral',
        momentum_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.4,
        trend_alignment: tf.trend === 'bullish' ? 'aligned' : tf.trend === 'bearish' ? 'aligned' : 'mixed',
        overbought_oversold_status: tf.rsiBase > 70 ? 'overbought' : tf.rsiBase < 30 ? 'oversold' : 'neutral',
        volume_confirmation: tf.trend === 'bullish' ? 'confirmed' : tf.trend === 'bearish' ? 'confirmed' : 'weak'
      },
      
      // Volume Data - Different for each timeframe
      volume_data: {
        volume_sma: tf.volumeBase,
        current_volume: tf.volumeBase * (tf.trend === 'bullish' ? 1.16 : tf.trend === 'bearish' ? 1.08 : 1.02),
        volume_ratio: tf.trend === 'bullish' ? 1.16 : tf.trend === 'bearish' ? 1.08 : 1.02,
        volume_trend: tf.trend === 'bullish' ? 'increasing' : tf.trend === 'bearish' ? 'decreasing' : 'stable',
        volume_spike: tf.trend === 'bullish' ? true : false,
        price_volume_correlation: tf.trend === 'bullish' ? 'positive' : tf.trend === 'bearish' ? 'negative' : 'neutral',
        volume_confirmation: tf.trend === 'bullish' ? 'confirmed' : tf.trend === 'bearish' ? 'confirmed' : 'weak'
      },
      
      // Fibonacci Data - Different for each timeframe
      fibonacci_data: {
        fib_0: tf.basePrice - (2000 * tf.volatility),
        fib_236: tf.basePrice - (1500 * tf.volatility),
        fib_382: tf.basePrice - (1000 * tf.volatility),
        fib_500: tf.basePrice - (500 * tf.volatility),
        fib_618: tf.basePrice,
        fib_786: tf.basePrice + (500 * tf.volatility),
        fib_1000: tf.basePrice + (1000 * tf.volatility),
        current_position: tf.trend === 'bullish' ? 'fib_618' : tf.trend === 'bearish' ? 'fib_382' : 'fib_500',
        retracement_level: tf.trend === 'bullish' ? 61.8 : tf.trend === 'bearish' ? 38.2 : 50.0,
        extension_level: tf.trend === 'bullish' ? 161.8 : tf.trend === 'bearish' ? 138.2 : 100.0
      },
      
      // Ichimoku Data - Different for each timeframe
      ichimoku_data: {
        tenkan_sen: tf.basePrice + (tf.trend === 'bullish' ? 200 : tf.trend === 'bearish' ? -200 : 0),
        kijun_sen: tf.basePrice + (tf.trend === 'bullish' ? 100 : tf.trend === 'bearish' ? -100 : 0),
        senkou_span_a: tf.basePrice + (tf.trend === 'bullish' ? 300 : tf.trend === 'bearish' ? -300 : 0),
        senkou_span_b: tf.basePrice + (tf.trend === 'bullish' ? -200 : tf.trend === 'bearish' ? 200 : 0),
        chikou_span: tf.basePrice + (tf.trend === 'bullish' ? 400 : tf.trend === 'bearish' ? -400 : 0),
        kumo_breakout: tf.trend === 'bullish' ? 'above_cloud' : tf.trend === 'bearish' ? 'below_cloud' : 'inside_cloud',
        tk_cross: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        cloud_color: tf.trend === 'bullish' ? 'green' : tf.trend === 'bearish' ? 'red' : 'neutral',
        trend_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.4
      },
      
      // Stochastic Data - Different for each timeframe
      stochastic_data: {
        stoch_k: tf.trend === 'bullish' ? 75.2 : tf.trend === 'bearish' ? 25.8 : 50.0,
        stoch_d: tf.trend === 'bullish' ? 68.5 : tf.trend === 'bearish' ? 32.5 : 50.0,
        signal_status: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        overbought_level: 80.0,
        oversold_level: 20.0,
        cross_signal: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        divergence_type: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none'
      },
      
      // Williams %R Data - Different for each timeframe
      williams_r_data: {
        williams_r: tf.trend === 'bullish' ? -25.8 : tf.trend === 'bearish' ? -75.2 : -50.0,
        signal_status: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        overbought_level: -20.0,
        oversold_level: -80.0,
        cross_signal: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        divergence_type: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none'
      },
      
      // ATR Data - Different for each timeframe
      atr_data: {
        atr_value: 1250.0 * tf.volatility,
        atr_percentage: 2.8 * tf.volatility,
        volatility_status: tf.volatility > 0.7 ? 'high' : tf.volatility > 0.4 ? 'medium' : 'low',
        volatility_trend: tf.trend === 'bullish' ? 'increasing' : tf.trend === 'bearish' ? 'decreasing' : 'stable',
        breakout_threshold: 1500.0 * tf.volatility,
        stop_loss_distance: 2500.0 * tf.volatility
      },
      
      // Parabolic SAR Data - Different for each timeframe
      parabolic_sar_data: {
        sar_value: tf.basePrice + (tf.trend === 'bullish' ? -1200 : tf.trend === 'bearish' ? 1200 : 0),
        trend_direction: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        trend_strength: tf.trend === 'bullish' ? 0.7 : tf.trend === 'bearish' ? 0.6 : 0.3,
        acceleration_factor: tf.trend === 'bullish' ? 0.02 : tf.trend === 'bearish' ? 0.015 : 0.01,
        max_acceleration: 0.2,
        stop_loss_level: tf.basePrice + (tf.trend === 'bullish' ? -1200 : tf.trend === 'bearish' ? 1200 : 0)
      },
      
      // ADX Data - Different for each timeframe
      adx_data: {
        adx_value: tf.trend === 'bullish' ? 28.5 : tf.trend === 'bearish' ? 32.8 : 15.2,
        di_plus: tf.trend === 'bullish' ? 32.1 : tf.trend === 'bearish' ? 18.5 : 25.0,
        di_minus: tf.trend === 'bullish' ? 18.9 : tf.trend === 'bearish' ? 35.2 : 25.0,
        trend_strength: tf.trend === 'bullish' ? 'moderate' : tf.trend === 'bearish' ? 'strong' : 'weak',
        trend_direction: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        signal_strength: tf.trend === 'bullish' ? 0.7 : tf.trend === 'bearish' ? 0.8 : 0.4
      },
      
      // CCI Data - Different for each timeframe
      cci_data: {
        cci_value: tf.trend === 'bullish' ? 45.2 : tf.trend === 'bearish' ? -65.8 : 15.0,
        signal_status: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        overbought_level: 100.0,
        oversold_level: -100.0,
        cross_signal: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        divergence_type: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none'
      },
      
      // Stochastic RSI Data - Different for each timeframe
      stoch_rsi_data: {
        stoch_rsi_k: tf.trend === 'bullish' ? 72.5 : tf.trend === 'bearish' ? 28.5 : 50.0,
        stoch_rsi_d: tf.trend === 'bullish' ? 65.8 : tf.trend === 'bearish' ? 35.2 : 50.0,
        signal_status: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        overbought_level: 80.0,
        oversold_level: 20.0,
        cross_signal: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        divergence_type: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none'
      },
      
      // Price Patterns Data - Different for each timeframe
      price_patterns_data: {
        pattern_name: tf.trend === 'bullish' ? 'ascending_triangle' : tf.trend === 'bearish' ? 'descending_triangle' : 'rectangle',
        pattern_type: tf.trend === 'bullish' ? 'continuation' : tf.trend === 'bearish' ? 'continuation' : 'consolidation',
        confidence: tf.trend === 'bullish' ? 0.75 : tf.trend === 'bearish' ? 0.70 : 0.50,
        target_price: tf.basePrice + (tf.trend === 'bullish' ? 1500 : tf.trend === 'bearish' ? -1500 : 500),
        stop_loss: tf.basePrice + (tf.trend === 'bullish' ? -1000 : tf.trend === 'bearish' ? 1000 : -500),
        risk_reward_ratio: tf.trend === 'bullish' ? 2.5 : tf.trend === 'bearish' ? 2.2 : 1.5,
        completion_percentage: tf.trend === 'bullish' ? 65.0 : tf.trend === 'bearish' ? 60.0 : 45.0
      },
      
      // Bollinger Squeeze Data - Different for each timeframe
      bollinger_squeeze_data: {
        squeeze_status: tf.volatility < 0.3 ? 'squeeze' : tf.volatility < 0.6 ? 'tight' : 'normal',
        volatility_ratio: tf.volatility,
        momentum_ratio: tf.trend === 'bullish' ? 1.2 : tf.trend === 'bearish' ? 0.8 : 1.0,
        breakout_potential: tf.trend === 'bullish' ? 'high_bullish' : tf.trend === 'bearish' ? 'high_bearish' : 'medium',
        squeeze_duration: tf.volatility < 0.3 ? 5 : tf.volatility < 0.6 ? 3 : 1,
        breakout_direction: tf.trend,
        breakout_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.5
      },
      
      // MACD Histogram Data - Different for each timeframe
      macd_histogram_data: {
        histogram_trend: tf.trend === 'bullish' ? 'increasing' : tf.trend === 'bearish' ? 'decreasing' : 'stable',
        histogram_strength: tf.trend === 'bullish' ? 0.7 : tf.trend === 'bearish' ? 0.6 : 0.3,
        zero_line_cross: tf.trend === 'bullish' ? 'above' : tf.trend === 'bearish' ? 'below' : 'neutral',
        signal_cross: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        divergence_type: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none',
        momentum_shift: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'neutral',
        histogram_pattern: tf.trend === 'bullish' ? 'rising' : tf.trend === 'bearish' ? 'falling' : 'sideways'
      },
      
      // MA Convergence Data - Different for each timeframe
      ma_convergence_data: {
        convergence_status: tf.trend === 'bullish' ? 'converging' : tf.trend === 'bearish' ? 'diverging' : 'stable',
        convergence_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.4,
        ma_alignment: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'mixed',
        alignment_strength: tf.trend === 'bullish' ? 0.9 : tf.trend === 'bearish' ? 0.8 : 0.5,
        golden_cross_detected: tf.trend === 'bullish',
        death_cross_detected: tf.trend === 'bearish',
        trend_direction: tf.trend,
        trend_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.4
      },
      
      // Price Channels Data - Different for each timeframe
      price_channels_data: {
        upper_channel: tf.basePrice + (1500 * tf.volatility),
        middle_channel: tf.basePrice,
        lower_channel: tf.basePrice - (1500 * tf.volatility),
        channel_width: 3000.0 * tf.volatility,
        channel_position: tf.trend === 'bullish' ? 65.0 : tf.trend === 'bearish' ? 35.0 : 50.0,
        breakout_direction: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'none',
        breakout_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.0,
        channel_trend: tf.trend === 'bullish' ? 'bullish' : tf.trend === 'bearish' ? 'bearish' : 'sideways',
        trend_strength: tf.trend === 'bullish' ? 0.8 : tf.trend === 'bearish' ? 0.7 : 0.5
      }
    };
    
    return mockData[indicatorKey] || null;
  };

  // Render technical indicators for a symbol
  const renderTechnicalIndicators = (symbol, timeframe) => {
    const data = technicalData[symbol];
    console.log(`🎯 Rendering indicators for ${symbol} (${timeframe}):`, data);
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
          console.log(`📊 Processing indicator ${key} for ${symbol}:`, indicatorData);
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
            console.log(`✅ Found real data for ${key} (${timeframe}):`, indicatorData);
            
            // Check if data is borrowed from another timeframe
            if (indicatorData._data_source === 'borrowed_from_closest_timeframe') {
              isBorrowedData = true;
              dataSource = 'Borrowed from Closest Timeframe';
            }
          } else if (indicatorData && typeof indicatorData === 'object' && Object.keys(indicatorData).length > 0) {
            // Real data without timeframe structure (single timeframe)
            isRealData = true;
            dataSource = 'Real Database Data (Single Timeframe)';
            console.log(`✅ Found real data for ${key} (single timeframe):`, indicatorData);
          } else {
            // No real data, use mock data
            indicatorData = generateMockIndicatorData(key, timeframe);
            isMockData = true;
            dataSource = 'Mock Data (No Database Data)';
            console.log(`⚠️ Using mock data for ${key} (${timeframe}):`, indicatorData);
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
                <span className="sentiment-emoji">📈</span>
                <span>Bullish</span>
              </div>
              <div className="sentiment-bar-container">
                <div 
                  className="sentiment-bar-fill bullish-fill" 
                  style={{ width: `${sentiment.bullish}%` }}
                ></div>
                <span className="sentiment-percentage">{sentiment.bullish}%</span>
              </div>
            </div>
            <div className="sentiment-bar neutral">
              <div className="sentiment-label">
                <span className="sentiment-emoji">➡️</span>
                <span>Neutral</span>
              </div>
              <div className="sentiment-bar-container">
                <div 
                  className="sentiment-bar-fill neutral-fill" 
                  style={{ width: `${sentiment.neutral}%` }}
                ></div>
                <span className="sentiment-percentage">{sentiment.neutral}%</span>
              </div>
            </div>
            <div className="sentiment-bar bearish">
              <div className="sentiment-label">
                <span className="sentiment-emoji">📉</span>
                <span>Bearish</span>
              </div>
              <div className="sentiment-bar-container">
                <div 
                  className="sentiment-bar-fill bearish-fill" 
                  style={{ width: `${sentiment.bearish}%` }}
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
          <p>Loading Enhanced Alerts System...</p>
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
          <h1>Enhanced Alerts System</h1>
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
            <h3>Active Alerts</h3>
            {alerts.length > 0 ? (
              <div className="alerts-grid">
                {alerts.map((alert, index) => (
                  <div key={index} className="alert-item">
                    <div className="alert-header">
                      <span className={`alert-severity ${getAlertSeverityColor(alert)}`}>
                        {alert.type?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      <span className="alert-time">{formatTimestamp(alert.timestamp)}</span>
                    </div>
                    <div className="alert-content">
                      <div className="alert-symbol">{alert.symbol}</div>
                      <div className="alert-message">{alert.message}</div>
                      <div className="alert-details">
                        <span>Condition: {alert.condition}</span>
                        <span>Threshold: ${alert.threshold?.toFixed(2)}</span>
                        <span>Current: ${alert.current_price?.toFixed(2)}</span>
                        <span>Timeframe: {alert.timeframe}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-alerts">No active alerts at the moment</div>
            )}
          </div>
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
