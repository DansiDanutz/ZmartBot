/**
 * FOUR-YEAR PATTERN DISCOVERY AGENT
 * Specialized agent that analyzes 4 years of historical data
 * Finds the best entry points in history and their indicator patterns
 * Creates comprehensive reports that create user addiction
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

class FourYearPatternDiscoveryAgent extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Configuration
    this.config = {
      yearsToAnalyze: 4,
      minProfitThreshold: 0.05,  // 5% minimum profit to consider "best entry"
      maxDrawdown: 0.02,         // 2% maximum drawdown allowed
      dataResolution: '1h',      // Hourly data for detailed analysis
      topEntriesCount: 100       // Track top 100 best entries per symbol
    };

    // Store discovered patterns
    this.bestEntries = new Map();
    this.specialEvents = new Map();
    this.comprehensiveReports = new Map();

    // Addiction metrics
    this.addictionMetrics = {
      reportViews: 0,
      averageTimeSpent: 0,
      repeatViewRate: 0,
      shareRate: 0
    };
  }

  /**
   * MAIN FUNCTION: Analyze 4 years of data for a symbol
   */
  async analyzeFourYearCycle(symbol) {
    console.log(`📊 Starting 4-year deep analysis for ${symbol}...`);

    const startTime = Date.now();
    const report = {
      symbol,
      analysisDate: new Date().toISOString(),
      timeframe: '4 years',
      dataPoints: 0,
      bestEntries: [],
      patterns: [],
      specialEvents: [],
      statistics: {},
      addictionScore: 0
    };

    try {
      // 1. Fetch 4 years of historical data
      const historicalData = await this.fetchFourYearsData(symbol);
      report.dataPoints = historicalData.length;

      // 2. Find ALL successful entry points
      const allEntries = await this.findAllSuccessfulEntries(historicalData, symbol);

      // 3. Analyze indicator patterns at each entry
      const patternsAnalysis = await this.analyzeIndicatorPatterns(allEntries, historicalData);

      // 4. Identify special events (rare but highly profitable)
      const specialEvents = await this.identifySpecialEvents(allEntries, historicalData);

      // 5. Calculate statistics and probabilities
      const statistics = await this.calculateComprehensiveStatistics(allEntries, patternsAnalysis);

      // 6. Generate addiction-inducing insights
      const addictiveInsights = await this.generateAddictiveInsights(
        symbol,
        allEntries,
        specialEvents,
        statistics
      );

      // Build comprehensive report
      report.bestEntries = allEntries.slice(0, this.config.topEntriesCount);
      report.patterns = patternsAnalysis;
      report.specialEvents = specialEvents;
      report.statistics = statistics;
      report.insights = addictiveInsights;
      report.processingTime = Date.now() - startTime;

      // Calculate addiction score
      report.addictionScore = this.calculateAddictionScore(report);

      // Store report
      await this.storeComprehensiveReport(symbol, report);

      console.log(`✅ 4-year analysis complete for ${symbol}. Found ${allEntries.length} profitable entries!`);

      return report;

    } catch (error) {
      console.error(`Failed to analyze 4-year cycle for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Fetch 4 years of historical data
   */
  async fetchFourYearsData(symbol) {
    console.log(`📥 Fetching 4 years of data for ${symbol}...`);

    const fourYearsAgo = Date.now() - (4 * 365 * 24 * 60 * 60 * 1000);
    const allData = [];

    try {
      // Fetch from multiple sources for complete data
      const binanceData = await this.fetchBinanceHistorical(symbol, fourYearsAgo);
      allData.push(...binanceData);

      // If we need more historical data, fetch from other sources
      if (allData.length < 35000) { // ~4 years of hourly data
        const additionalData = await this.fetchAdditionalHistoricalData(symbol, fourYearsAgo);
        allData.push(...additionalData);
      }

      // Sort by timestamp
      allData.sort((a, b) => a.timestamp - b.timestamp);

      console.log(`📊 Fetched ${allData.length} data points for ${symbol}`);
      return allData;

    } catch (error) {
      console.error('Error fetching 4-year data:', error);
      throw error;
    }
  }

  /**
   * Find ALL successful entry points in 4 years
   */
  async findAllSuccessfulEntries(historicalData, symbol) {
    console.log(`🔍 Finding all successful entries in ${historicalData.length} data points...`);

    const entries = [];
    const lookforward = 240; // Look 10 days ahead (240 hours)

    for (let i = 100; i < historicalData.length - lookforward; i++) {
      const entry = historicalData[i];

      // Calculate potential profit from this entry point
      let maxProfit = 0;
      let maxLoss = 0;
      let exitIndex = i;

      for (let j = 1; j <= lookforward; j++) {
        const future = historicalData[i + j];
        const priceChange = (future.high - entry.close) / entry.close;
        const drawdown = (entry.close - future.low) / entry.close;

        if (priceChange > maxProfit) {
          maxProfit = priceChange;
          exitIndex = i + j;
        }
        maxLoss = Math.max(maxLoss, drawdown);
      }

      // Check if this was a successful entry
      if (maxProfit >= this.config.minProfitThreshold &&
          maxLoss <= this.config.maxDrawdown) {

        // Calculate all indicators at this point
        const indicators = await this.calculateAllIndicators(historicalData, i);

        entries.push({
          timestamp: entry.timestamp,
          date: new Date(entry.timestamp).toISOString(),
          entryPrice: entry.close,
          exitPrice: historicalData[exitIndex].close,
          profit: maxProfit,
          drawdown: maxLoss,
          holdingPeriod: exitIndex - i,
          indicators: indicators,
          marketContext: this.getMarketContext(historicalData, i),
          score: this.calculateEntryScore(maxProfit, maxLoss, exitIndex - i)
        });
      }
    }

    // Sort by score (best entries first)
    entries.sort((a, b) => b.score - a.score);

    console.log(`✅ Found ${entries.length} successful entries!`);
    return entries;
  }

  /**
   * Calculate ALL indicators at a specific point
   */
  async calculateAllIndicators(data, index) {
    const indicators = {
      // Price action
      price: data[index].close,
      priceChange1h: (data[index].close - data[index - 1].close) / data[index - 1].close,
      priceChange24h: (data[index].close - data[index - 24].close) / data[index - 24].close,
      priceChange7d: (data[index].close - data[Math.max(0, index - 168)].close) / data[Math.max(0, index - 168)].close,

      // RSI
      rsi14: this.calculateRSI(data, index, 14),
      rsi7: this.calculateRSI(data, index, 7),
      rsi21: this.calculateRSI(data, index, 21),

      // MACD
      macd: this.calculateMACD(data, index),

      // Moving Averages
      ma7: this.calculateMA(data, index, 7),
      ma25: this.calculateMA(data, index, 25),
      ma50: this.calculateMA(data, index, 50),
      ma100: this.calculateMA(data, index, 100),
      ma200: this.calculateMA(data, index, 200),

      // Volume
      volume: data[index].volume,
      volumeMA: this.calculateVolumeMA(data, index, 20),
      volumeRatio: data[index].volume / this.calculateVolumeMA(data, index, 20),

      // Bollinger Bands
      bollinger: this.calculateBollingerBands(data, index),

      // Stochastic
      stochastic: this.calculateStochastic(data, index),

      // ATR (volatility)
      atr: this.calculateATR(data, index),

      // Support/Resistance
      nearSupport: this.findNearestSupport(data, index),
      nearResistance: this.findNearestResistance(data, index),

      // Market Structure
      trend: this.determineTrend(data, index),
      marketPhase: this.determineMarketPhase(data, index)
    };

    return indicators;
  }

  /**
   * Analyze patterns in successful entries
   */
  async analyzeIndicatorPatterns(entries, historicalData) {
    console.log(`🔬 Analyzing patterns in ${entries.length} successful entries...`);

    const patterns = {
      rsiPatterns: [],
      macdPatterns: [],
      volumePatterns: [],
      priceActionPatterns: [],
      combinedPatterns: []
    };

    // Group entries by similar indicator values
    const rsiGroups = this.groupByRSI(entries);
    const macdGroups = this.groupByMACD(entries);
    const volumeGroups = this.groupByVolume(entries);

    // Find most common successful patterns
    for (const [range, groupEntries] of Object.entries(rsiGroups)) {
      if (groupEntries.length >= 5) { // At least 5 occurrences
        patterns.rsiPatterns.push({
          range: range,
          occurrences: groupEntries.length,
          averageProfit: this.calculateAverageProfit(groupEntries),
          successRate: groupEntries.length / entries.length,
          description: this.describeRSIPattern(range, groupEntries)
        });
      }
    }

    // Find combined patterns (multiple indicators align)
    const combinedPatterns = this.findCombinedPatterns(entries);
    patterns.combinedPatterns = combinedPatterns;

    // Sort patterns by success rate
    Object.keys(patterns).forEach(key => {
      if (Array.isArray(patterns[key])) {
        patterns[key].sort((a, b) => b.successRate - a.successRate);
      }
    });

    return patterns;
  }

  /**
   * Identify special events (rare but highly profitable)
   */
  async identifySpecialEvents(entries, historicalData) {
    console.log(`🌟 Identifying special events...`);

    const specialEvents = [];

    // Find entries with exceptional profits (>10%)
    const exceptionalEntries = entries.filter(e => e.profit > 0.1);

    for (const entry of exceptionalEntries) {
      const event = {
        date: entry.date,
        type: this.categorizeSpecialEvent(entry),
        profit: entry.profit,
        indicators: entry.indicators,
        description: await this.describeSpecialEvent(entry, historicalData),
        rarity: this.calculateRarity(entry, entries),
        historicalContext: await this.getHistoricalContext(entry.timestamp)
      };

      specialEvents.push(event);
    }

    // Sort by profit
    specialEvents.sort((a, b) => b.profit - a.profit);

    console.log(`✨ Found ${specialEvents.length} special events!`);
    return specialEvents;
  }

  /**
   * Generate addiction-inducing insights
   */
  async generateAddictiveInsights(symbol, entries, specialEvents, statistics) {
    const insights = {
      headline: '',
      keyFindings: [],
      shockingStats: [],
      motivationalData: [],
      fomo: [],
      successStories: []
    };

    // Generate headline
    insights.headline = `🔥 ${symbol} 4-Year Analysis: ${entries.length} Profitable Setups Discovered!`;

    // Key findings that create excitement
    insights.keyFindings = [
      `📊 Best entry yielded ${(Math.max(...entries.map(e => e.profit)) * 100).toFixed(1)}% profit`,
      `⚡ Average profitable setup occurs every ${Math.floor(1460 / entries.length)} days`,
      `🎯 Top pattern has ${(statistics.topPatternSuccessRate * 100).toFixed(1)}% success rate`,
      `💰 Following all triggers would yield ${(statistics.totalPotentialProfit * 100).toFixed(1)}% over 4 years`
    ];

    // Shocking statistics that grab attention
    insights.shockingStats = [
      {
        stat: `${specialEvents.length} "Golden Setups"`,
        detail: `Rare patterns that yielded over 10% profit`,
        impact: 'Life-changing opportunities'
      },
      {
        stat: `${entries.filter(e => e.profit > 0.07).length} High-Profit Entries`,
        detail: `Setups that made over 7% profit`,
        impact: 'Beating 99% of traders'
      },
      {
        stat: `${Math.floor(statistics.bestMonth.profit * 100)}% Best Month`,
        detail: `${statistics.bestMonth.name} historically best for ${symbol}`,
        impact: 'Perfect timing revealed'
      }
    ];

    // Motivational data
    insights.motivationalData = [
      `If you had caught just 10% of these setups, you'd have made ${(statistics.tenPercentProfit * 100).toFixed(1)}%`,
      `The next setup could happen in ${statistics.averageDaysBetweenSetups} days`,
      `Users following these patterns report ${statistics.userSatisfaction}% satisfaction`
    ];

    // FOMO generators
    insights.fomo = [
      `⏰ Only ${statistics.setupsPerYear} perfect setups per year - can't afford to miss one!`,
      `🚨 Last similar pattern was ${statistics.daysSinceLastSetup} days ago`,
      `💎 Next special event estimated in ${statistics.estimatedDaysToNextSpecial} days`
    ];

    // Success stories from the data
    insights.successStories = specialEvents.slice(0, 3).map(event => ({
      date: event.date,
      setup: event.description,
      profit: `+${(event.profit * 100).toFixed(1)}%`,
      message: `This exact pattern has appeared ${event.rarity.occurrences} times with ${(event.rarity.successRate * 100).toFixed(0)}% success`
    }));

    return insights;
  }

  /**
   * Generate comprehensive report for distribution
   */
  async generateComprehensiveReport(symbol, userId) {
    const report = await this.comprehensiveReports.get(symbol);

    if (!report) {
      // Generate new report if not cached
      const newReport = await this.analyzeFourYearCycle(symbol);
      this.comprehensiveReports.set(symbol, newReport);
      return newReport;
    }

    // Personalize report for user
    const personalizedReport = {
      ...report,
      personalization: {
        userId,
        relevantPatterns: await this.getRelevantPatternsForUser(userId, report),
        customAlerts: await this.generateCustomAlerts(userId, report),
        motivationalMessage: await this.generatePersonalMotivation(userId, report)
      }
    };

    // Track engagement for addiction metrics
    await this.trackReportEngagement(userId, symbol);

    return personalizedReport;
  }

  /**
   * Calculate addiction score for report
   */
  calculateAddictionScore(report) {
    let score = 0;

    // Factors that increase addiction
    score += report.bestEntries.length * 0.1;        // More opportunities = more addiction
    score += report.specialEvents.length * 5;         // Rare events = high addiction
    score += (report.statistics.topPatternSuccessRate || 0) * 20;  // High success = addiction
    score += report.insights.shockingStats.length * 2;  // Shocking stats = engagement

    // Cap at 100
    return Math.min(100, score);
  }

  /**
   * Store comprehensive report in database
   */
  async storeComprehensiveReport(symbol, report) {
    try {
      await this.supabase.from('pattern_discovery_reports').upsert({
        symbol: symbol,
        report_data: report,
        analysis_date: report.analysisDate,
        addiction_score: report.addictionScore,
        best_entries_count: report.bestEntries.length,
        special_events_count: report.specialEvents.length,
        updated_at: new Date().toISOString()
      });

      console.log(`💾 Stored comprehensive report for ${symbol}`);
    } catch (error) {
      console.error('Failed to store report:', error);
    }
  }

  /**
   * Distribute report to interested users
   */
  async distributeReport(symbol) {
    console.log(`📨 Distributing ${symbol} report to interested users...`);

    try {
      // Get all users subscribed to this symbol
      const { data: subscribers } = await this.supabase
        .from('user_symbol_subscriptions')
        .select('user_id, preferences')
        .eq('symbol', symbol);

      if (!subscribers || subscribers.length === 0) {
        console.log('No subscribers for', symbol);
        return;
      }

      // Generate report once
      const report = await this.generateComprehensiveReport(symbol);

      // Send to each subscriber
      for (const subscriber of subscribers) {
        const personalizedReport = await this.personalizeReportForUser(
          report,
          subscriber.user_id,
          subscriber.preferences
        );

        await this.sendReportToUser(subscriber.user_id, personalizedReport);

        // Track delivery
        await this.trackReportDelivery(subscriber.user_id, symbol);
      }

      console.log(`✅ Distributed report to ${subscribers.length} users`);

    } catch (error) {
      console.error('Failed to distribute report:', error);
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
  calculateMACD(data, index) {
    if (index < 26) return { macd: 0, signal: 0, histogram: 0 };

    const ema12 = this.calculateEMA(data, index, 12);
    const ema26 = this.calculateEMA(data, index, 26);
    const macd = ema12 - ema26;
    const signal = this.calculateEMA([{ close: macd }], 0, 9);
    const histogram = macd - signal;

    return {
      macd: macd,
      signal: signal,
      histogram: histogram,
      crossover: macd > signal && this.calculateMACD(data, index - 1).macd <= this.calculateMACD(data, index - 1).signal
    };
  }

  /**
   * Calculate entry score
   */
  calculateEntryScore(profit, drawdown, holdingPeriod) {
    // Higher profit = higher score
    let score = profit * 100;

    // Lower drawdown = higher score
    score += (1 - drawdown) * 50;

    // Shorter holding period = higher score (faster profit)
    score += Math.max(0, 50 - holdingPeriod);

    return score;
  }

  /**
   * Track report engagement for addiction metrics
   */
  async trackReportEngagement(userId, symbol) {
    try {
      await this.supabase.from('report_engagement').insert({
        user_id: userId,
        symbol: symbol,
        view_time: new Date().toISOString(),
        engagement_type: 'view'
      });

      this.addictionMetrics.reportViews++;
    } catch (error) {
      console.error('Failed to track engagement:', error);
    }
  }
}

// Export singleton
const fourYearAgent = new FourYearPatternDiscoveryAgent();
export default fourYearAgent;