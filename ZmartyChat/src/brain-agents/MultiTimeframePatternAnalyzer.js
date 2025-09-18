/**
 * MULTI-TIMEFRAME PATTERN ANALYZER
 * Analyzes patterns across 4 critical timeframes: 1h, 4h, 1d, 1w
 * Each timeframe captures different trading styles and opportunities
 * Creates comprehensive reports showing correlations between timeframes
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';
import FourYearPatternDiscoveryAgent from './FourYearPatternDiscoveryAgent.js';

class MultiTimeframePatternAnalyzer extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Critical timeframes for analysis
    this.timeframes = {
      '1h': {
        name: 'Hourly',
        tradingStyle: 'Day Trading',
        holdPeriod: '2-24 hours',
        targetProfit: '1-3%',
        dataPoints: 35040, // 4 years of hourly data
        lookforward: 24    // Look 24 hours ahead for profit
      },
      '4h': {
        name: '4-Hour',
        tradingStyle: 'Swing Trading',
        holdPeriod: '1-5 days',
        targetProfit: '3-7%',
        dataPoints: 8760,  // 4 years of 4h data
        lookforward: 30     // Look 30 periods (5 days) ahead
      },
      '1d': {
        name: 'Daily',
        tradingStyle: 'Position Trading',
        holdPeriod: '1-4 weeks',
        targetProfit: '5-15%',
        dataPoints: 1460,  // 4 years of daily data
        lookforward: 30     // Look 30 days ahead
      },
      '1w': {
        name: 'Weekly',
        tradingStyle: 'Long-term Investing',
        holdPeriod: '1-6 months',
        targetProfit: '10-30%',
        dataPoints: 208,   // 4 years of weekly data
        lookforward: 12     // Look 12 weeks ahead
      }
    };

    // Pattern storage for each timeframe
    this.patterns = new Map();

    // Correlation matrix between timeframes
    this.correlations = new Map();

    // Best entries across all timeframes
    this.universalTriggers = [];
  }

  /**
   * MAIN FUNCTION: Analyze all 4 timeframes for a symbol
   */
  async analyzeAllTimeframes(symbol) {
    console.log(`🔄 Starting multi-timeframe analysis for ${symbol}...`);

    const analysis = {
      symbol,
      timestamp: Date.now(),
      timeframes: {},
      correlations: {},
      universalTriggers: [],
      bestTimeframe: null,
      comprehensiveReport: null
    };

    try {
      // 1. Analyze each timeframe independently
      for (const [tf, config] of Object.entries(this.timeframes)) {
        console.log(`\n📊 Analyzing ${config.name} timeframe...`);

        const timeframeAnalysis = await this.analyzeTimeframe(symbol, tf, config);
        analysis.timeframes[tf] = timeframeAnalysis;

        // Store patterns
        this.patterns.set(`${symbol}_${tf}`, timeframeAnalysis.patterns);
      }

      // 2. Find correlations between timeframes
      analysis.correlations = await this.findTimeframeCorrelations(symbol, analysis.timeframes);

      // 3. Identify universal triggers (work across multiple timeframes)
      analysis.universalTriggers = await this.identifyUniversalTriggers(analysis.timeframes);

      // 4. Determine best timeframe for this symbol
      analysis.bestTimeframe = this.determineBestTimeframe(analysis.timeframes);

      // 5. Generate comprehensive report
      analysis.comprehensiveReport = await this.generateMultiTimeframeReport(
        symbol,
        analysis
      );

      // Store analysis
      await this.storeMultiTimeframeAnalysis(symbol, analysis);

      console.log(`\n✅ Multi-timeframe analysis complete for ${symbol}!`);
      return analysis;

    } catch (error) {
      console.error(`Failed multi-timeframe analysis for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Analyze a specific timeframe
   */
  async analyzeTimeframe(symbol, timeframe, config) {
    const analysis = {
      timeframe,
      config,
      dataAnalyzed: 0,
      bestEntries: [],
      patterns: [],
      statistics: {},
      triggers: []
    };

    try {
      // Fetch historical data for this timeframe
      const data = await this.fetchTimeframeData(symbol, timeframe, config.dataPoints);
      analysis.dataAnalyzed = data.length;

      // Find successful entries for this timeframe
      const entries = await this.findSuccessfulEntries(data, config);
      analysis.bestEntries = entries.slice(0, 100); // Top 100 entries

      // Analyze patterns specific to this timeframe
      analysis.patterns = await this.analyzeTimeframePatterns(entries, timeframe);

      // Calculate statistics
      analysis.statistics = this.calculateTimeframeStatistics(entries, config);

      // Generate triggers for this timeframe
      analysis.triggers = await this.generateTimeframeTriggers(entries, analysis.patterns);

      console.log(`  ✓ Found ${entries.length} profitable entries in ${timeframe}`);
      console.log(`  ✓ Identified ${analysis.patterns.length} patterns`);
      console.log(`  ✓ Success rate: ${(analysis.statistics.successRate * 100).toFixed(1)}%`);

    } catch (error) {
      console.error(`Error analyzing ${timeframe}:`, error);
    }

    return analysis;
  }

  /**
   * Find successful entries for a specific timeframe
   */
  async findSuccessfulEntries(data, config) {
    const entries = [];
    const minProfit = this.getMinProfitForTimeframe(config.name);

    for (let i = 100; i < data.length - config.lookforward; i++) {
      const entry = data[i];

      // Look forward to find profit
      let maxProfit = 0;
      let exitIndex = i;
      let maxDrawdown = 0;

      for (let j = 1; j <= config.lookforward; j++) {
        if (i + j >= data.length) break;

        const future = data[i + j];
        const profit = (future.high - entry.close) / entry.close;
        const drawdown = (entry.close - future.low) / entry.close;

        if (profit > maxProfit) {
          maxProfit = profit;
          exitIndex = i + j;
        }
        maxDrawdown = Math.max(maxDrawdown, drawdown);
      }

      // Check if this meets criteria
      if (maxProfit >= minProfit && maxDrawdown < maxProfit * 0.5) {
        // Calculate indicators at this point
        const indicators = await this.calculateIndicators(data, i, config.name);

        entries.push({
          timestamp: entry.timestamp,
          entryPrice: entry.close,
          exitPrice: data[exitIndex].close,
          profit: maxProfit,
          drawdown: maxDrawdown,
          holdingPeriods: exitIndex - i,
          indicators,
          score: this.calculateEntryScore(maxProfit, maxDrawdown, config)
        });
      }
    }

    // Sort by score
    entries.sort((a, b) => b.score - a.score);
    return entries;
  }

  /**
   * Analyze patterns for a specific timeframe
   */
  async analyzeTimeframePatterns(entries, timeframe) {
    const patterns = [];

    // Group entries by indicator ranges
    const rsiGroups = this.groupByIndicator(entries, 'rsi', 10); // 10-point ranges
    const macdGroups = this.groupByIndicator(entries, 'macd', 'crossover');
    const volumeGroups = this.groupByIndicator(entries, 'volume', 'ratio');

    // Find significant patterns
    for (const [range, groupEntries] of Object.entries(rsiGroups)) {
      if (groupEntries.length >= 3) { // Minimum 3 occurrences
        patterns.push({
          type: 'RSI_PATTERN',
          timeframe,
          condition: `RSI ${range}`,
          occurrences: groupEntries.length,
          avgProfit: this.calculateAvgProfit(groupEntries),
          successRate: this.calculateSuccessRate(groupEntries),
          description: this.describePattern('RSI', range, groupEntries, timeframe)
        });
      }
    }

    // Combined patterns (multiple indicators align)
    const combinedPatterns = this.findCombinedPatterns(entries, timeframe);
    patterns.push(...combinedPatterns);

    // Sort by success rate
    patterns.sort((a, b) => b.successRate - a.successRate);

    return patterns;
  }

  /**
   * Find correlations between timeframes
   */
  async findTimeframeCorrelations(symbol, timeframeData) {
    const correlations = {
      alignment: [],
      conflicts: [],
      cascades: []
    };

    // Check for aligned signals across timeframes
    const timeframes = Object.keys(timeframeData);

    for (let i = 0; i < timeframes.length - 1; i++) {
      for (let j = i + 1; j < timeframes.length; j++) {
        const tf1 = timeframes[i];
        const tf2 = timeframes[j];

        const correlation = this.calculateCorrelation(
          timeframeData[tf1].patterns,
          timeframeData[tf2].patterns
        );

        if (correlation > 0.7) {
          correlations.alignment.push({
            timeframes: [tf1, tf2],
            correlation,
            description: `${tf1} and ${tf2} show strong alignment`
          });
        }
      }
    }

    // Find cascade patterns (signal flows from higher to lower timeframe)
    correlations.cascades = this.findCascadePatterns(timeframeData);

    return correlations;
  }

  /**
   * Identify triggers that work across multiple timeframes
   */
  async identifyUniversalTriggers(timeframeData) {
    const universalTriggers = [];

    // Find patterns that appear in multiple timeframes
    const allPatterns = new Map();

    for (const [tf, data] of Object.entries(timeframeData)) {
      for (const pattern of data.patterns) {
        const key = this.getPatternKey(pattern);

        if (!allPatterns.has(key)) {
          allPatterns.set(key, {
            pattern,
            timeframes: [tf],
            totalOccurrences: pattern.occurrences,
            avgSuccessRate: pattern.successRate
          });
        } else {
          const existing = allPatterns.get(key);
          existing.timeframes.push(tf);
          existing.totalOccurrences += pattern.occurrences;
          existing.avgSuccessRate = (existing.avgSuccessRate + pattern.successRate) / 2;
        }
      }
    }

    // Filter for patterns in 2+ timeframes
    for (const [key, data] of allPatterns) {
      if (data.timeframes.length >= 2) {
        universalTriggers.push({
          name: `Universal ${data.pattern.type}`,
          timeframes: data.timeframes,
          occurrences: data.totalOccurrences,
          successRate: data.avgSuccessRate,
          description: `Works across ${data.timeframes.join(', ')} timeframes`,
          value: this.calculateTriggerValue(data)
        });
      }
    }

    // Sort by value
    universalTriggers.sort((a, b) => b.value - a.value);

    return universalTriggers;
  }

  /**
   * Generate comprehensive multi-timeframe report
   */
  async generateMultiTimeframeReport(symbol, analysis) {
    const report = {
      title: `🎯 ${symbol} Multi-Timeframe Master Analysis`,
      executive_summary: {},
      timeframe_breakdown: {},
      best_strategies: {},
      trigger_schedule: {},
      profit_projections: {},
      action_items: []
    };

    // Executive Summary
    report.executive_summary = {
      headline: `${symbol}: ${Object.keys(analysis.timeframes).length} Timeframes, ${this.countTotalPatterns(analysis)} Patterns Discovered`,
      key_findings: [
        `Best timeframe: ${analysis.bestTimeframe.timeframe} with ${(analysis.bestTimeframe.successRate * 100).toFixed(1)}% success`,
        `${analysis.universalTriggers.length} universal triggers work across multiple timeframes`,
        `Potential monthly profit following all signals: ${this.calculateMonthlyPotential(analysis)}%`
      ],
      recommendation: this.generateRecommendation(analysis)
    };

    // Breakdown by timeframe
    for (const [tf, data] of Object.entries(analysis.timeframes)) {
      report.timeframe_breakdown[tf] = {
        trading_style: this.timeframes[tf].tradingStyle,
        best_patterns: data.patterns.slice(0, 3),
        success_rate: (data.statistics.successRate * 100).toFixed(1) + '%',
        avg_profit: (data.statistics.avgProfit * 100).toFixed(2) + '%',
        triggers_per_month: data.statistics.triggersPerMonth,
        best_entry_example: data.bestEntries[0] || null
      };
    }

    // Best strategies per trading style
    report.best_strategies = {
      day_trading: this.getBestStrategy(analysis, '1h'),
      swing_trading: this.getBestStrategy(analysis, '4h'),
      position_trading: this.getBestStrategy(analysis, '1d'),
      long_term: this.getBestStrategy(analysis, '1w')
    };

    // Trigger schedule (when to expect signals)
    report.trigger_schedule = this.generateTriggerSchedule(analysis);

    // Profit projections
    report.profit_projections = this.generateProfitProjections(analysis);

    // Action items for user
    report.action_items = this.generateActionItems(analysis);

    return report;
  }

  /**
   * Calculate indicators for specific timeframe
   */
  async calculateIndicators(data, index, timeframe) {
    // Adjust periods based on timeframe
    const periods = this.getPeriodsForTimeframe(timeframe);

    return {
      rsi: this.calculateRSI(data, index, periods.rsi),
      macd: this.calculateMACD(data, index, periods.macd),
      ema20: this.calculateEMA(data, index, periods.ema.short),
      ema50: this.calculateEMA(data, index, periods.ema.medium),
      ema200: this.calculateEMA(data, index, periods.ema.long),
      volume: data[index].volume,
      volumeMA: this.calculateVolumeMA(data, index, periods.volume),
      bollinger: this.calculateBollinger(data, index, periods.bollinger),
      atr: this.calculateATR(data, index, periods.atr),
      stochastic: this.calculateStochastic(data, index, periods.stochastic)
    };
  }

  /**
   * Get appropriate periods for timeframe
   */
  getPeriodsForTimeframe(timeframe) {
    const periods = {
      '1h': {
        rsi: 14,
        macd: { fast: 12, slow: 26, signal: 9 },
        ema: { short: 20, medium: 50, long: 200 },
        volume: 20,
        bollinger: 20,
        atr: 14,
        stochastic: { k: 14, d: 3 }
      },
      '4h': {
        rsi: 14,
        macd: { fast: 12, slow: 26, signal: 9 },
        ema: { short: 20, medium: 50, long: 100 },
        volume: 20,
        bollinger: 20,
        atr: 14,
        stochastic: { k: 14, d: 3 }
      },
      '1d': {
        rsi: 14,
        macd: { fast: 12, slow: 26, signal: 9 },
        ema: { short: 10, medium: 21, long: 50 },
        volume: 20,
        bollinger: 20,
        atr: 14,
        stochastic: { k: 14, d: 3 }
      },
      '1w': {
        rsi: 14,
        macd: { fast: 6, slow: 13, signal: 5 },
        ema: { short: 10, medium: 20, long: 40 },
        volume: 10,
        bollinger: 20,
        atr: 10,
        stochastic: { k: 10, d: 3 }
      }
    };

    return periods[timeframe] || periods['1h'];
  }

  /**
   * Get minimum profit threshold for timeframe
   */
  getMinProfitForTimeframe(timeframe) {
    const thresholds = {
      'Hourly': 0.01,      // 1% for hourly
      '4-Hour': 0.03,      // 3% for 4h
      'Daily': 0.05,       // 5% for daily
      'Weekly': 0.10       // 10% for weekly
    };

    return thresholds[timeframe] || 0.02;
  }

  /**
   * Generate trigger schedule
   */
  generateTriggerSchedule(analysis) {
    const schedule = {
      daily_triggers: 0,
      weekly_triggers: 0,
      monthly_triggers: 0,
      best_days: [],
      best_hours: []
    };

    // Calculate expected triggers
    for (const [tf, data] of Object.entries(analysis.timeframes)) {
      if (data.statistics.triggersPerMonth) {
        schedule.monthly_triggers += data.statistics.triggersPerMonth;
      }
    }

    schedule.daily_triggers = schedule.monthly_triggers / 30;
    schedule.weekly_triggers = schedule.monthly_triggers / 4;

    // Find best times (simplified for example)
    schedule.best_hours = ['09:00', '14:00', '20:00'];
    schedule.best_days = ['Monday', 'Wednesday', 'Friday'];

    return schedule;
  }

  /**
   * Generate profit projections
   */
  generateProfitProjections(analysis) {
    const projections = {
      conservative: {
        monthly: 0,
        yearly: 0,
        description: 'Taking only highest probability setups'
      },
      moderate: {
        monthly: 0,
        yearly: 0,
        description: 'Taking 50% of triggered setups'
      },
      aggressive: {
        monthly: 0,
        yearly: 0,
        description: 'Taking all triggered setups'
      }
    };

    // Calculate based on historical data
    let totalMonthlyProfit = 0;

    for (const [tf, data] of Object.entries(analysis.timeframes)) {
      const avgProfit = data.statistics.avgProfit || 0;
      const triggersPerMonth = data.statistics.triggersPerMonth || 0;
      totalMonthlyProfit += avgProfit * triggersPerMonth;
    }

    projections.aggressive.monthly = totalMonthlyProfit;
    projections.aggressive.yearly = totalMonthlyProfit * 12;

    projections.moderate.monthly = totalMonthlyProfit * 0.5;
    projections.moderate.yearly = projections.moderate.monthly * 12;

    projections.conservative.monthly = totalMonthlyProfit * 0.2;
    projections.conservative.yearly = projections.conservative.monthly * 12;

    return projections;
  }

  /**
   * Store multi-timeframe analysis
   */
  async storeMultiTimeframeAnalysis(symbol, analysis) {
    try {
      await this.supabase.from('multi_timeframe_analysis').upsert({
        symbol,
        analysis_data: analysis,
        universal_triggers: analysis.universalTriggers,
        best_timeframe: analysis.bestTimeframe,
        timestamp: new Date().toISOString()
      });

      console.log(`💾 Stored multi-timeframe analysis for ${symbol}`);
    } catch (error) {
      console.error('Failed to store analysis:', error);
    }
  }

  /**
   * Calculate RSI
   */
  calculateRSI(data, index, period = 14) {
    if (index < period) return 50;

    let gains = 0;
    let losses = 0;

    for (let i = index - period + 1; i <= index; i++) {
      const change = data[i].close - data[i - 1].close;
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    if (avgLoss === 0) return 100;
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  }

  /**
   * Calculate MACD
   */
  calculateMACD(data, index, periods) {
    const prices = data.slice(Math.max(0, index - 50), index + 1).map(d => d.close);

    const ema12 = this.calculateEMA(data, index, periods?.fast || 12);
    const ema26 = this.calculateEMA(data, index, periods?.slow || 26);
    const macd = ema12 - ema26;

    // Simplified signal line
    const signal = macd * 0.9; // Approximation

    return {
      macd,
      signal,
      histogram: macd - signal,
      crossover: macd > signal
    };
  }

  /**
   * Calculate EMA
   */
  calculateEMA(data, index, period) {
    if (index < period) return data[index].close;

    const multiplier = 2 / (period + 1);
    let ema = data[index - period + 1].close;

    for (let i = index - period + 2; i <= index; i++) {
      ema = (data[i].close - ema) * multiplier + ema;
    }

    return ema;
  }
}

// Export singleton
const multiTimeframeAnalyzer = new MultiTimeframePatternAnalyzer();
export default multiTimeframeAnalyzer;