/**
 * HISTORICAL PATTERN TRIGGER SYSTEM
 * Analyzes historical charts to find successful entry points
 * Records indicator values at those points as triggers
 * Calculates probabilities based on real historical success rates
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

class HistoricalPatternTriggerSystem extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Timeframes to analyze
    this.timeframes = {
      short: ['1m', '5m', '15m'],
      medium: ['1h', '4h'],
      long: ['1d', '1w']
    };

    // Store discovered triggers
    this.triggers = new Map();

    // Store success rates for each trigger
    this.successRates = new Map();
  }

  /**
   * Analyze historical data to find successful entry points
   * This is the CORE function - finding what worked in the past
   */
  async analyzeHistoricalEntryPoints(symbol, timeframe = '15m') {
    console.log(`📊 Analyzing historical entry points for ${symbol} on ${timeframe}`);

    try {
      // Fetch historical candlestick data
      const historicalData = await this.fetchHistoricalData(symbol, timeframe);

      // Find successful entry points (where price moved favorably)
      const successfulEntries = this.findSuccessfulEntries(historicalData);

      // Analyze indicator values at those successful points
      const triggerPatterns = await this.analyzeIndicatorValues(
        symbol,
        successfulEntries,
        historicalData,
        timeframe
      );

      // Calculate success rates for each trigger pattern
      const successRates = this.calculateSuccessRates(triggerPatterns, historicalData);

      // Store triggers in database
      await this.storeTriggers(symbol, timeframe, triggerPatterns, successRates);

      return {
        symbol,
        timeframe,
        entriesAnalyzed: successfulEntries.length,
        triggersFound: triggerPatterns.length,
        averageSuccessRate: this.calculateAverageSuccessRate(successRates)
      };

    } catch (error) {
      console.error(`Failed to analyze historical entries for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Find successful entry points in historical data
   * Looking for points where entering would have been profitable
   */
  findSuccessfulEntries(historicalData) {
    const successfulEntries = [];

    // Analyze each candle
    for (let i = 10; i < historicalData.length - 10; i++) {
      const currentCandle = historicalData[i];

      // Check next 10 candles for profit
      let maxProfit = 0;
      let maxLoss = 0;

      for (let j = 1; j <= 10; j++) {
        const futureCandle = historicalData[i + j];
        const priceChange = (futureCandle.close - currentCandle.close) / currentCandle.close;

        maxProfit = Math.max(maxProfit, priceChange);
        maxLoss = Math.min(maxLoss, priceChange);
      }

      // If this point led to >2% profit with <1% drawdown, it's a successful entry
      if (maxProfit > 0.02 && Math.abs(maxLoss) < 0.01) {
        successfulEntries.push({
          timestamp: currentCandle.timestamp,
          price: currentCandle.close,
          profit: maxProfit,
          index: i,
          type: 'long'
        });
      }

      // Check for successful short entries too
      if (maxLoss < -0.02 && maxProfit < 0.01) {
        successfulEntries.push({
          timestamp: currentCandle.timestamp,
          price: currentCandle.close,
          profit: Math.abs(maxLoss),
          index: i,
          type: 'short'
        });
      }
    }

    console.log(`✅ Found ${successfulEntries.length} successful entry points`);
    return successfulEntries;
  }

  /**
   * Analyze indicator values at successful entry points
   * This finds the common patterns - what indicators showed at winning trades
   */
  async analyzeIndicatorValues(symbol, successfulEntries, historicalData, timeframe) {
    const patterns = [];

    for (const entry of successfulEntries) {
      // Calculate all indicators at this point
      const indicators = await this.calculateIndicatorsAtPoint(
        historicalData,
        entry.index
      );

      // Create a trigger pattern from these values
      const pattern = {
        type: entry.type,
        conditions: {
          // RSI conditions
          rsi: {
            value: indicators.rsi,
            condition: this.determineRSICondition(indicators.rsi, entry.type)
          },

          // MACD conditions
          macd: {
            crossover: indicators.macdCrossover,
            histogram: indicators.macdHistogram,
            condition: indicators.macdCrossover ? 'bullish_cross' : 'bearish_cross'
          },

          // Moving Average conditions
          ma: {
            priceVsMA50: indicators.priceVsMA50,
            priceVsMA200: indicators.priceVsMA200,
            condition: this.determineMACondition(indicators)
          },

          // Volume conditions
          volume: {
            vsAverage: indicators.volumeRatio,
            condition: indicators.volumeRatio > 1.5 ? 'high_volume' : 'normal_volume'
          },

          // Bollinger Bands
          bollinger: {
            position: indicators.bollingerPosition,
            condition: this.determineBollingerCondition(indicators.bollingerPosition)
          },

          // Support/Resistance
          levels: {
            nearSupport: indicators.nearSupport,
            nearResistance: indicators.nearResistance,
            condition: this.determineLevelCondition(indicators)
          }
        },

        // Store the profit this pattern led to
        historicalProfit: entry.profit,
        timestamp: entry.timestamp
      };

      patterns.push(pattern);
    }

    // Group similar patterns and find the most common ones
    const groupedPatterns = this.groupSimilarPatterns(patterns);

    console.log(`📈 Identified ${groupedPatterns.length} unique trigger patterns`);
    return groupedPatterns;
  }

  /**
   * Calculate indicators at a specific point in history
   */
  async calculateIndicatorsAtPoint(historicalData, index) {
    // Get price data around this point
    const lookback = 50; // Look back 50 periods for indicator calculation
    const startIdx = Math.max(0, index - lookback);
    const priceData = historicalData.slice(startIdx, index + 1);

    // Calculate RSI
    const rsi = this.calculateRSI(priceData, 14);

    // Calculate MACD
    const macd = this.calculateMACD(priceData);

    // Calculate Moving Averages
    const ma50 = this.calculateSMA(priceData, 50);
    const ma200 = this.calculateSMA(historicalData.slice(0, index + 1), 200);

    // Current price
    const currentPrice = priceData[priceData.length - 1].close;

    // Volume analysis
    const currentVolume = priceData[priceData.length - 1].volume;
    const avgVolume = priceData.reduce((sum, d) => sum + d.volume, 0) / priceData.length;

    // Bollinger Bands
    const bollinger = this.calculateBollingerBands(priceData, 20);

    // Support/Resistance (simplified - find recent highs/lows)
    const recentHigh = Math.max(...priceData.slice(-20).map(d => d.high));
    const recentLow = Math.min(...priceData.slice(-20).map(d => d.low));

    return {
      rsi,
      macdCrossover: macd.macd > macd.signal,
      macdHistogram: macd.histogram,
      priceVsMA50: (currentPrice - ma50) / ma50,
      priceVsMA200: (currentPrice - ma200) / ma200,
      volumeRatio: currentVolume / avgVolume,
      bollingerPosition: (currentPrice - bollinger.middle) / (bollinger.upper - bollinger.middle),
      nearSupport: Math.abs(currentPrice - recentLow) / currentPrice < 0.02,
      nearResistance: Math.abs(currentPrice - recentHigh) / currentPrice < 0.02
    };
  }

  /**
   * Calculate RSI
   */
  calculateRSI(priceData, period = 14) {
    if (priceData.length < period + 1) return 50;

    let gains = 0;
    let losses = 0;

    for (let i = 1; i <= period; i++) {
      const change = priceData[i].close - priceData[i - 1].close;
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    if (avgLoss === 0) return 100;

    const rs = avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));

    return rsi;
  }

  /**
   * Calculate MACD
   */
  calculateMACD(priceData) {
    const prices = priceData.map(d => d.close);

    // Calculate EMAs
    const ema12 = this.calculateEMA(prices, 12);
    const ema26 = this.calculateEMA(prices, 26);

    const macd = ema12 - ema26;
    const signal = this.calculateEMA([macd], 9);
    const histogram = macd - signal;

    return { macd, signal, histogram };
  }

  /**
   * Calculate EMA
   */
  calculateEMA(data, period) {
    if (data.length < period) return data[data.length - 1];

    const multiplier = 2 / (period + 1);
    let ema = data.slice(0, period).reduce((a, b) => a + b) / period;

    for (let i = period; i < data.length; i++) {
      ema = (data[i] - ema) * multiplier + ema;
    }

    return ema;
  }

  /**
   * Calculate SMA
   */
  calculateSMA(data, period) {
    if (data.length < period) return data[data.length - 1].close;

    const prices = data.slice(-period).map(d => d.close);
    return prices.reduce((a, b) => a + b) / prices.length;
  }

  /**
   * Calculate Bollinger Bands
   */
  calculateBollingerBands(priceData, period = 20) {
    const prices = priceData.slice(-period).map(d => d.close);
    const sma = prices.reduce((a, b) => a + b) / prices.length;

    const variance = prices.reduce((sum, price) => {
      return sum + Math.pow(price - sma, 2);
    }, 0) / prices.length;

    const stdDev = Math.sqrt(variance);

    return {
      upper: sma + (stdDev * 2),
      middle: sma,
      lower: sma - (stdDev * 2)
    };
  }

  /**
   * Group similar patterns together
   */
  groupSimilarPatterns(patterns) {
    const grouped = [];

    for (const pattern of patterns) {
      // Find if similar pattern already exists
      const similar = grouped.find(g => this.arePatternsSimlar(g.conditions, pattern.conditions));

      if (similar) {
        similar.occurrences++;
        similar.totalProfit += pattern.historicalProfit;
        similar.instances.push({
          timestamp: pattern.timestamp,
          profit: pattern.historicalProfit
        });
      } else {
        grouped.push({
          ...pattern,
          occurrences: 1,
          totalProfit: pattern.historicalProfit,
          instances: [{
            timestamp: pattern.timestamp,
            profit: pattern.historicalProfit
          }]
        });
      }
    }

    // Sort by occurrence frequency
    return grouped.sort((a, b) => b.occurrences - a.occurrences);
  }

  /**
   * Check if two patterns are similar
   */
  arePatternsSimlar(pattern1, pattern2) {
    // RSI similarity (within 5 points)
    if (Math.abs(pattern1.rsi.value - pattern2.rsi.value) > 5) return false;

    // MACD crossover must match
    if (pattern1.macd.crossover !== pattern2.macd.crossover) return false;

    // Volume condition must match
    if (pattern1.volume.condition !== pattern2.volume.condition) return false;

    // Bollinger position must be similar
    if (pattern1.bollinger.condition !== pattern2.bollinger.condition) return false;

    return true;
  }

  /**
   * Calculate success rates for triggers
   */
  calculateSuccessRates(triggerPatterns, historicalData) {
    const successRates = [];

    for (const pattern of triggerPatterns) {
      // Find all times this pattern occurred in history
      const allOccurrences = this.findPatternOccurrences(pattern, historicalData);

      // Calculate how many times it led to profit
      let successfulCount = 0;
      let totalCount = allOccurrences.length;

      for (const occurrence of allOccurrences) {
        if (occurrence.profit > 0.01) { // >1% profit considered success
          successfulCount++;
        }
      }

      const successRate = totalCount > 0 ? successfulCount / totalCount : 0;

      successRates.push({
        pattern: pattern,
        successRate: successRate,
        totalOccurrences: totalCount,
        successfulOccurrences: successfulCount,
        averageProfit: pattern.totalProfit / pattern.occurrences
      });
    }

    return successRates;
  }

  /**
   * Find all occurrences of a pattern in historical data
   */
  findPatternOccurrences(pattern, historicalData) {
    const occurrences = [];

    for (let i = 50; i < historicalData.length - 10; i++) {
      const indicators = this.calculateIndicatorsAtPoint(historicalData, i);

      // Check if current indicators match the pattern
      if (this.doesIndicatorMatchPattern(indicators, pattern.conditions)) {
        // Calculate profit from this point
        const entryPrice = historicalData[i].close;
        const exitPrice = historicalData[Math.min(i + 10, historicalData.length - 1)].close;
        const profit = (exitPrice - entryPrice) / entryPrice;

        occurrences.push({
          index: i,
          timestamp: historicalData[i].timestamp,
          profit: profit
        });
      }
    }

    return occurrences;
  }

  /**
   * Check if current indicators match a pattern
   */
  doesIndicatorMatchPattern(indicators, patternConditions) {
    // Check RSI
    if (Math.abs(indicators.rsi - patternConditions.rsi.value) > 5) return false;

    // Check MACD
    if (indicators.macdCrossover !== (patternConditions.macd.condition === 'bullish_cross')) return false;

    // Check volume
    const highVolume = indicators.volumeRatio > 1.5;
    if (highVolume !== (patternConditions.volume.condition === 'high_volume')) return false;

    return true;
  }

  /**
   * Get real-time trigger alerts based on current market conditions
   */
  async checkCurrentTriggers(symbol, currentData) {
    const triggers = await this.getTriggers(symbol);
    const activeAlerts = [];

    // Calculate current indicators
    const currentIndicators = await this.calculateCurrentIndicators(symbol, currentData);

    // Check each trigger pattern
    for (const trigger of triggers) {
      if (this.doesIndicatorMatchPattern(currentIndicators, trigger.conditions)) {
        activeAlerts.push({
          symbol: symbol,
          triggerPattern: trigger,
          successRate: trigger.successRate,
          averageProfit: trigger.averageProfit,
          probability: trigger.successRate,
          message: this.generateTriggerMessage(symbol, trigger),
          timestamp: Date.now()
        });
      }
    }

    return activeAlerts;
  }

  /**
   * Generate human-readable trigger message
   */
  generateTriggerMessage(symbol, trigger) {
    const successPercent = (trigger.successRate * 100).toFixed(1);
    const profitPercent = (trigger.averageProfit * 100).toFixed(2);

    return `📊 ${symbol} TRIGGER ACTIVATED: Historical pattern detected with ${successPercent}% success rate. Average profit when this occurred: ${profitPercent}%. Based on ${trigger.totalOccurrences} historical occurrences.`;
  }

  /**
   * Store triggers in database
   */
  async storeTriggers(symbol, timeframe, patterns, successRates) {
    try {
      for (const rate of successRates) {
        await this.supabase.from('historical_triggers').upsert({
          symbol: symbol,
          timeframe: timeframe,
          pattern_conditions: rate.pattern.conditions,
          success_rate: rate.successRate,
          total_occurrences: rate.totalOccurrences,
          successful_occurrences: rate.successfulOccurrences,
          average_profit: rate.averageProfit,
          last_updated: new Date().toISOString()
        });
      }

      console.log(`💾 Stored ${successRates.length} triggers for ${symbol} ${timeframe}`);
    } catch (error) {
      console.error('Failed to store triggers:', error);
    }
  }

  /**
   * Fetch historical data from exchange
   */
  async fetchHistoricalData(symbol, timeframe) {
    try {
      // Binance API for historical klines
      const interval = this.convertTimeframe(timeframe);
      const limit = 1000; // Get last 1000 candles

      const response = await axios.get(
        `https://api.binance.com/api/v3/klines`,
        {
          params: {
            symbol: `${symbol}USDT`,
            interval: interval,
            limit: limit
          }
        }
      );

      // Format the data
      return response.data.map(candle => ({
        timestamp: candle[0],
        open: parseFloat(candle[1]),
        high: parseFloat(candle[2]),
        low: parseFloat(candle[3]),
        close: parseFloat(candle[4]),
        volume: parseFloat(candle[5])
      }));

    } catch (error) {
      console.error(`Failed to fetch historical data for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Convert timeframe to Binance interval
   */
  convertTimeframe(timeframe) {
    const map = {
      '1m': '1m',
      '5m': '5m',
      '15m': '15m',
      '30m': '30m',
      '1h': '1h',
      '4h': '4h',
      '1d': '1d',
      '1w': '1w'
    };
    return map[timeframe] || '15m';
  }

  /**
   * Analyze all timeframes for a symbol
   */
  async analyzeAllTimeframes(symbol) {
    const results = {
      symbol: symbol,
      timeframes: {}
    };

    // Analyze short timeframes
    for (const tf of this.timeframes.short) {
      results.timeframes[tf] = await this.analyzeHistoricalEntryPoints(symbol, tf);
    }

    // Analyze medium timeframes
    for (const tf of this.timeframes.medium) {
      results.timeframes[tf] = await this.analyzeHistoricalEntryPoints(symbol, tf);
    }

    // Analyze long timeframes
    for (const tf of this.timeframes.long) {
      results.timeframes[tf] = await this.analyzeHistoricalEntryPoints(symbol, tf);
    }

    return results;
  }
}

// Export singleton
const historicalPatternTriggerSystem = new HistoricalPatternTriggerSystem();
export default historicalPatternTriggerSystem;