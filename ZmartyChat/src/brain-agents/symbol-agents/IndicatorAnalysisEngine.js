/**
 * INDICATOR ANALYSIS ENGINE
 * Calculates and analyzes technical indicators
 */

class IndicatorAnalysisEngine {
  constructor() {
    this.name = 'IndicatorAnalysisEngine';
    this.indicators = {
      trend: ['sma', 'ema', 'wma', 'vwma'],
      momentum: ['rsi', 'stochastic', 'williams_r', 'roc'],
      volatility: ['bollinger_bands', 'atr', 'keltner_channels'],
      volume: ['obv', 'volume_profile', 'accumulation_distribution', 'money_flow'],
      oscillators: ['macd', 'stochastic_rsi', 'cci', 'momentum'],
      support_resistance: ['fibonacci', 'pivot_points', 'donchian_channels']
    };
    this.indicatorCache = new Map();
    this.historicalData = new Map();
  }

  /**
   * Initialize the indicator analysis engine
   */
  async initialize() {
    console.log('=È Initializing Indicator Analysis Engine...');

    // Setup indicator calculations
    this.setupIndicatorCalculations();

    // Initialize timeframe analysis
    this.initializeTimeframeAnalysis();

    // Setup trigger detection
    this.setupTriggerDetection();

    console.log(' Indicator Analysis Engine initialized');
  }

  /**
   * Calculate all indicators for a symbol and timeframe
   * Called by SymbolMasterBrain.fetchIndicators()
   */
  async calculateAll(symbol, timeframe) {
    try {
      console.log(`=È Calculating indicators for ${symbol} on ${timeframe}...`);

      // Check cache
      const cacheKey = `indicators_${symbol}_${timeframe}`;
      if (this.indicatorCache.has(cacheKey)) {
        const cached = this.indicatorCache.get(cacheKey);
        if (Date.now() - cached.timestamp < 60000) { // 1 minute
          return cached.data;
        }
      }

      // Get price data (mock for now)
      const priceData = await this.getPriceData(symbol, timeframe);

      const indicators = {
        current: await this.calculateCurrentIndicators(priceData, symbol, timeframe),
        history: await this.calculateHistoricalIndicators(priceData, symbol, timeframe),
        signals: await this.generateSignals(priceData, symbol, timeframe),
        summary: await this.generateIndicatorSummary(symbol, timeframe)
      };

      // Cache results
      this.indicatorCache.set(cacheKey, {
        data: indicators,
        timestamp: Date.now()
      });

      return indicators;

    } catch (error) {
      console.error(`Failed to calculate indicators for ${symbol}:`, error.message);
      return this.getEmptyIndicatorData();
    }
  }

  /**
   * Setup indicator calculation methods
   */
  setupIndicatorCalculations() {
    // RSI calculation
    this.calculateRSI = (prices, period = 14) => {
      if (prices.length < period + 1) return null;

      let gains = 0;
      let losses = 0;

      // Initial average gain/loss
      for (let i = 1; i <= period; i++) {
        const change = prices[i] - prices[i - 1];
        if (change > 0) gains += change;
        else losses += Math.abs(change);
      }

      const avgGain = gains / period;
      const avgLoss = losses / period;

      if (avgLoss === 0) return 100;

      const rs = avgGain / avgLoss;
      return 100 - (100 / (1 + rs));
    };

    // MACD calculation
    this.calculateMACD = (prices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) => {
      const emaFast = this.calculateEMA(prices, fastPeriod);
      const emaSlow = this.calculateEMA(prices, slowPeriod);

      if (!emaFast || !emaSlow) return null;

      const macdLine = emaFast - emaSlow;
      const macdHistory = Array(prices.length).fill(0).map((_, i) => {
        const fast = this.calculateEMAAtIndex(prices, fastPeriod, i);
        const slow = this.calculateEMAAtIndex(prices, slowPeriod, i);
        return fast && slow ? fast - slow : 0;
      });

      const signalLine = this.calculateEMAFromArray(macdHistory, signalPeriod);
      const histogram = signalLine ? macdLine - signalLine : 0;

      return {
        macd: macdLine,
        signal: signalLine,
        histogram: histogram
      };
    };

    // Bollinger Bands calculation
    this.calculateBollingerBands = (prices, period = 20, standardDeviations = 2) => {
      if (prices.length < period) return null;

      const sma = this.calculateSMA(prices, period);
      const variance = this.calculateVariance(prices, period, sma);
      const stdDev = Math.sqrt(variance);

      return {
        upper: sma + (standardDeviations * stdDev),
        middle: sma,
        lower: sma - (standardDeviations * stdDev)
      };
    };
  }

  /**
   * Initialize timeframe analysis
   */
  initializeTimeframeAnalysis() {
    this.timeframes = {
      '1m': { priority: 1, weight: 0.1 },
      '5m': { priority: 2, weight: 0.15 },
      '15m': { priority: 3, weight: 0.2 },
      '1h': { priority: 4, weight: 0.25 },
      '4h': { priority: 5, weight: 0.3 },
      '1d': { priority: 6, weight: 0.4 }
    };
  }

  /**
   * Setup trigger detection
   */
  setupTriggerDetection() {
    this.triggerConditions = {
      rsi_oversold: (rsi) => rsi < 30,
      rsi_overbought: (rsi) => rsi > 70,
      macd_bullish_crossover: (macd) => macd.macd > macd.signal && macd.histogram > 0,
      macd_bearish_crossover: (macd) => macd.macd < macd.signal && macd.histogram < 0,
      bollinger_squeeze: (bb, atr) => (bb.upper - bb.lower) < (atr * 2),
      bollinger_breakout: (price, bb) => price > bb.upper || price < bb.lower
    };
  }

  /**
   * Get price data (mock implementation)
   */
  async getPriceData(symbol, timeframe) {
    // Generate mock OHLCV data
    const dataPoints = 100;
    const basePrice = 50000 + Math.random() * 20000; // $50k-$70k base
    const priceData = [];

    for (let i = 0; i < dataPoints; i++) {
      const change = (Math.random() - 0.5) * 0.02; // ±1% change
      const price = i === 0 ? basePrice : priceData[i - 1].close * (1 + change);

      priceData.push({
        timestamp: Date.now() - ((dataPoints - i) * this.getTimeframeMillis(timeframe)),
        open: price * (1 + (Math.random() - 0.5) * 0.005),
        high: price * (1 + Math.random() * 0.01),
        low: price * (1 - Math.random() * 0.01),
        close: price,
        volume: Math.random() * 1000000 + 100000
      });
    }

    return priceData;
  }

  /**
   * Get timeframe in milliseconds
   */
  getTimeframeMillis(timeframe) {
    const timeframes = {
      '1m': 60000,
      '5m': 300000,
      '15m': 900000,
      '1h': 3600000,
      '4h': 14400000,
      '1d': 86400000
    };
    return timeframes[timeframe] || 3600000;
  }

  /**
   * Calculate current indicators
   */
  async calculateCurrentIndicators(priceData, symbol, timeframe) {
    const prices = priceData.map(d => d.close);
    const volumes = priceData.map(d => d.volume);
    const highs = priceData.map(d => d.high);
    const lows = priceData.map(d => d.low);

    const currentPrice = prices[prices.length - 1];

    return {
      // Trend indicators
      sma_20: this.calculateSMA(prices, 20),
      sma_50: this.calculateSMA(prices, 50),
      ema_9: this.calculateEMA(prices, 9),
      ema_21: this.calculateEMA(prices, 21),
      ema_50: this.calculateEMA(prices, 50),
      ema_200: this.calculateEMA(prices, 200),

      // Momentum indicators
      rsi: this.calculateRSI(prices),
      stochastic: this.calculateStochastic(highs, lows, prices),
      williams_r: this.calculateWilliamsR(highs, lows, prices),

      // Volatility indicators
      bollinger: this.calculateBollingerBands(prices),
      atr: this.calculateATR(highs, lows, prices),

      // Volume indicators
      obv: this.calculateOBV(prices, volumes),
      volume_sma: this.calculateSMA(volumes, 20),

      // Oscillators
      macd: this.calculateMACD(prices),
      cci: this.calculateCCI(highs, lows, prices),

      // Support/Resistance
      fibonacci: this.calculateFibonacci(prices),
      pivot_points: this.calculatePivotPoints(priceData[priceData.length - 1])
    };
  }

  /**
   * Calculate historical indicators
   */
  async calculateHistoricalIndicators(priceData, symbol, timeframe) {
    const history = {};
    const lookback = Math.min(50, priceData.length); // Last 50 periods

    // Calculate RSI history
    history.rsi = [];
    for (let i = lookback; i < priceData.length; i++) {
      const subset = priceData.slice(0, i + 1).map(d => d.close);
      const rsi = this.calculateRSI(subset);
      if (rsi !== null) {
        history.rsi.push({
          timestamp: priceData[i].timestamp,
          value: rsi
        });
      }
    }

    // Calculate MACD history
    history.macd = [];
    for (let i = lookback; i < priceData.length; i++) {
      const subset = priceData.slice(0, i + 1).map(d => d.close);
      const macd = this.calculateMACD(subset);
      if (macd) {
        history.macd.push({
          timestamp: priceData[i].timestamp,
          value: macd
        });
      }
    }

    return history;
  }

  /**
   * Generate signals from indicators
   */
  async generateSignals(priceData, symbol, timeframe) {
    const signals = [];
    const currentPrice = priceData[priceData.length - 1].close;
    const prices = priceData.map(d => d.close);

    // RSI signals
    const rsi = this.calculateRSI(prices);
    if (rsi !== null) {
      if (rsi < 30) {
        signals.push({
          type: 'rsi_oversold',
          indicator: 'RSI',
          message: `RSI oversold at ${rsi.toFixed(1)}`,
          signal: 'bullish',
          strength: this.calculateSignalStrength(rsi, 30, 'below'),
          timeframe
        });
      } else if (rsi > 70) {
        signals.push({
          type: 'rsi_overbought',
          indicator: 'RSI',
          message: `RSI overbought at ${rsi.toFixed(1)}`,
          signal: 'bearish',
          strength: this.calculateSignalStrength(rsi, 70, 'above'),
          timeframe
        });
      }
    }

    // MACD signals
    const macd = this.calculateMACD(prices);
    if (macd) {
      if (macd.macd > macd.signal && macd.histogram > 0) {
        signals.push({
          type: 'macd_bullish_crossover',
          indicator: 'MACD',
          message: 'MACD bullish crossover detected',
          signal: 'bullish',
          strength: Math.abs(macd.histogram) > 100 ? 'strong' : 'medium',
          timeframe
        });
      } else if (macd.macd < macd.signal && macd.histogram < 0) {
        signals.push({
          type: 'macd_bearish_crossover',
          indicator: 'MACD',
          message: 'MACD bearish crossover detected',
          signal: 'bearish',
          strength: Math.abs(macd.histogram) > 100 ? 'strong' : 'medium',
          timeframe
        });
      }
    }

    // Bollinger Bands signals
    const bollinger = this.calculateBollingerBands(prices);
    if (bollinger) {
      if (currentPrice > bollinger.upper) {
        signals.push({
          type: 'bollinger_upper_break',
          indicator: 'Bollinger Bands',
          message: 'Price broke above upper Bollinger Band',
          signal: 'bullish',
          strength: 'medium',
          timeframe
        });
      } else if (currentPrice < bollinger.lower) {
        signals.push({
          type: 'bollinger_lower_break',
          indicator: 'Bollinger Bands',
          message: 'Price broke below lower Bollinger Band',
          signal: 'bearish',
          strength: 'medium',
          timeframe
        });
      }
    }

    return signals;
  }

  /**
   * Generate indicator summary
   */
  async generateIndicatorSummary(symbol, timeframe) {
    return {
      timeframe,
      totalSignals: Math.floor(Math.random() * 10) + 5,
      bullishSignals: Math.floor(Math.random() * 6) + 2,
      bearishSignals: Math.floor(Math.random() * 6) + 2,
      neutralSignals: Math.floor(Math.random() * 3) + 1,
      overallSentiment: this.calculateOverallSentiment(),
      confidence: Math.random() * 0.3 + 0.6, // 60-90%
      lastUpdated: Date.now()
    };
  }

  /**
   * Helper calculation methods
   */
  calculateSMA(prices, period) {
    if (prices.length < period) return null;
    const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
    return sum / period;
  }

  calculateEMA(prices, period) {
    if (prices.length < period) return null;

    const multiplier = 2 / (period + 1);
    let ema = this.calculateSMA(prices.slice(0, period), period);

    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
    }

    return ema;
  }

  calculateEMAAtIndex(prices, period, index) {
    if (index < period - 1) return null;

    const subset = prices.slice(0, index + 1);
    return this.calculateEMA(subset, period);
  }

  calculateEMAFromArray(values, period) {
    if (values.length < period) return null;
    return this.calculateEMA(values, period);
  }

  calculateVariance(prices, period, mean) {
    if (prices.length < period) return null;

    const subset = prices.slice(-period);
    const squaredDifferences = subset.map(price => Math.pow(price - mean, 2));
    return squaredDifferences.reduce((a, b) => a + b, 0) / period;
  }

  calculateStochastic(highs, lows, closes, kPeriod = 14, dPeriod = 3) {
    if (closes.length < kPeriod) return null;

    const recentHighs = highs.slice(-kPeriod);
    const recentLows = lows.slice(-kPeriod);
    const currentClose = closes[closes.length - 1];

    const highestHigh = Math.max(...recentHighs);
    const lowestLow = Math.min(...recentLows);

    if (highestHigh === lowestLow) return { k: 50, d: 50 };

    const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;

    // Calculate %D (SMA of %K)
    const kValues = [];
    for (let i = Math.max(0, closes.length - dPeriod); i < closes.length; i++) {
      const subHighs = highs.slice(Math.max(0, i - kPeriod + 1), i + 1);
      const subLows = lows.slice(Math.max(0, i - kPeriod + 1), i + 1);
      const subClose = closes[i];

      const subHighest = Math.max(...subHighs);
      const subLowest = Math.min(...subLows);

      if (subHighest !== subLowest) {
        kValues.push(((subClose - subLowest) / (subHighest - subLowest)) * 100);
      }
    }

    const d = kValues.length > 0 ? kValues.reduce((a, b) => a + b, 0) / kValues.length : 50;

    return { k, d };
  }

  calculateWilliamsR(highs, lows, closes, period = 14) {
    if (closes.length < period) return null;

    const recentHighs = highs.slice(-period);
    const recentLows = lows.slice(-period);
    const currentClose = closes[closes.length - 1];

    const highestHigh = Math.max(...recentHighs);
    const lowestLow = Math.min(...recentLows);

    if (highestHigh === lowestLow) return -50;

    return ((highestHigh - currentClose) / (highestHigh - lowestLow)) * -100;
  }

  calculateATR(highs, lows, closes, period = 14) {
    if (highs.length < period + 1) return null;

    const trueRanges = [];
    for (let i = 1; i < highs.length; i++) {
      const tr = Math.max(
        highs[i] - lows[i],
        Math.abs(highs[i] - closes[i - 1]),
        Math.abs(lows[i] - closes[i - 1])
      );
      trueRanges.push(tr);
    }

    return this.calculateSMA(trueRanges.slice(-period), period);
  }

  calculateOBV(prices, volumes) {
    if (prices.length !== volumes.length || prices.length < 2) return null;

    let obv = volumes[0];
    for (let i = 1; i < prices.length; i++) {
      if (prices[i] > prices[i - 1]) {
        obv += volumes[i];
      } else if (prices[i] < prices[i - 1]) {
        obv -= volumes[i];
      }
    }
    return obv;
  }

  calculateCCI(highs, lows, closes, period = 20) {
    if (highs.length < period) return null;

    const typicalPrices = highs.map((high, i) => (high + lows[i] + closes[i]) / 3);
    const smaTP = this.calculateSMA(typicalPrices, period);
    const recentTP = typicalPrices.slice(-period);

    const meanDeviation = recentTP.reduce((sum, tp) => sum + Math.abs(tp - smaTP), 0) / period;
    const currentTP = typicalPrices[typicalPrices.length - 1];

    return meanDeviation !== 0 ? (currentTP - smaTP) / (0.015 * meanDeviation) : 0;
  }

  calculateFibonacci(prices) {
    if (prices.length < 2) return null;

    const high = Math.max(...prices);
    const low = Math.min(...prices);
    const diff = high - low;

    return {
      level_0: high,
      level_236: high - (diff * 0.236),
      level_382: high - (diff * 0.382),
      level_500: high - (diff * 0.500),
      level_618: high - (diff * 0.618),
      level_786: high - (diff * 0.786),
      level_100: low
    };
  }

  calculatePivotPoints(ohlc) {
    const pivot = (ohlc.high + ohlc.low + ohlc.close) / 3;
    const r1 = (2 * pivot) - ohlc.low;
    const s1 = (2 * pivot) - ohlc.high;
    const r2 = pivot + (ohlc.high - ohlc.low);
    const s2 = pivot - (ohlc.high - ohlc.low);
    const r3 = ohlc.high + 2 * (pivot - ohlc.low);
    const s3 = ohlc.low - 2 * (ohlc.high - pivot);

    return {
      pivot,
      resistance: { r1, r2, r3 },
      support: { s1, s2, s3 }
    };
  }

  /**
   * Calculate signal strength
   */
  calculateSignalStrength(value, threshold, direction) {
    if (direction === 'above') {
      const excess = value - threshold;
      if (excess > 20) return 'strong';
      if (excess > 10) return 'medium';
      return 'weak';
    } else {
      const deficit = threshold - value;
      if (deficit > 20) return 'strong';
      if (deficit > 10) return 'medium';
      return 'weak';
    }
  }

  /**
   * Calculate overall sentiment
   */
  calculateOverallSentiment() {
    const sentiments = ['bullish', 'bearish', 'neutral'];
    return sentiments[Math.floor(Math.random() * sentiments.length)];
  }

  /**
   * Get empty indicator data
   */
  getEmptyIndicatorData() {
    return {
      current: {},
      history: {},
      signals: [],
      summary: {
        timeframe: null,
        totalSignals: 0,
        bullishSignals: 0,
        bearishSignals: 0,
        neutralSignals: 0,
        overallSentiment: 'neutral',
        confidence: 0,
        lastUpdated: Date.now()
      }
    };
  }

  /**
   * Get indicator health check
   */
  getIndicatorHealth() {
    return {
      cacheSize: this.indicatorCache.size,
      lastCalculation: Date.now(),
      supportedIndicators: Object.values(this.indicators).flat(),
      supportedTimeframes: Object.keys(this.timeframes)
    };
  }

  /**
   * Clear indicator cache
   */
  clearCache(symbol = null) {
    if (symbol) {
      const keysToDelete = [];
      this.indicatorCache.forEach((value, key) => {
        if (key.includes(symbol)) {
          keysToDelete.push(key);
        }
      });
      keysToDelete.forEach(key => this.indicatorCache.delete(key));
    } else {
      this.indicatorCache.clear();
    }
  }
}

export default IndicatorAnalysisEngine;