/**
 * USER PROFILE ALERT ENGINE
 * Personalized alert system that creates addiction and drives credit consumption
 * Each alert costs credits - more symbols = more alerts = more revenue
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';
import path from 'path';
import cron from 'node-cron';

class UserProfileAlertEngine extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // User profiles cache
    this.userProfiles = new Map();

    // Active alerts tracking
    this.activeAlerts = new Map();

    // Addiction metrics
    this.addictionMetrics = {
      optimalAlertTimes: {
        morning: { start: 7, end: 9 },      // Morning check
        lunch: { start: 12, end: 13 },      // Lunch break
        evening: { start: 17, end: 19 },    // After work
        night: { start: 20, end: 22 }       // Evening trading
      },
      engagementMultipliers: {
        priceBreakout: 3.0,        // High engagement
        whaleMovement: 2.8,        // Very interesting
        patternComplete: 2.5,      // Trading opportunity
        indicatorTrigger: 2.0,     // Technical signal
        newsAlert: 1.8,            // Market news
        volumeSpike: 1.5,          // Unusual activity
        regularUpdate: 1.0         // Standard update
      }
    };

    // Credit costs for alerts
    this.creditCosts = {
      critical: 5,        // Major breakout, whale alert
      important: 3,       // Pattern complete, strong signal
      standard: 2,        // Indicator trigger, support/resistance
      info: 1,           // Price update, minor news
      summary: 1         // Daily/hourly summaries
    };

    // FOMO triggers
    this.fomoTriggers = [
      'Price breaking out NOW! 🚀',
      'Whale just bought $X worth! 🐋',
      'Pattern completing - last chance! ⏰',
      'RSI oversold - bounce imminent! 📈',
      'Volume spike detected - something\'s happening! 🔥',
      'Smart money accumulating! 💎',
      'Breakout confirmed - don\'t miss out! 🎯',
      'Liquidation cascade starting! 💥'
    ];

    this.initialize();
  }

  /**
   * Initialize the alert engine
   */
  async initialize() {
    console.log('🔔 Initializing User Profile Alert Engine...');

    // Load all user profiles
    await this.loadUserProfiles();

    // Start alert monitoring
    this.startAlertMonitoring();

    // Start addiction optimizer
    this.startAddictionOptimizer();

    console.log('✅ Alert Engine initialized');
  }

  /**
   * Create/Update user profile MD file
   */
  async createUserProfileMD(userId, data = {}) {
    const profile = {
      userId,
      createdAt: Date.now(),
      lastActive: Date.now(),

      // Alert Preferences
      alerts: {
        enabled: true,
        symbols: data.symbols || ['BTC', 'ETH'], // Symbols they track
        maxDailyAlerts: data.maxDailyAlerts || 50,
        quietHours: data.quietHours || { start: 23, end: 7 },
        preferredChannels: ['app', 'email', 'push'],
        creditBalance: data.creditBalance || 100,
        subscriptionTier: data.subscriptionTier || 'free'
      },

      // Tracking Interests (for targeted alerts)
      interests: {
        priceTargets: {},      // Symbol -> [price levels]
        indicators: {},        // Symbol -> [RSI, MACD, etc]
        patterns: [],         // Patterns they care about
        whaleTracking: [],    // Wallets they follow
        news: [],            // News topics
        strategies: []       // Trading strategies they use
      },

      // Engagement Metrics (for addiction optimization)
      engagement: {
        alertsReceived: 0,
        alertsClicked: 0,
        clickRate: 0,
        averageResponseTime: 0,
        mostActiveHours: [],
        favoriteSymbols: [],
        totalCreditsSpent: 0,
        lastAlertTime: null,
        streakDays: 0
      },

      // Addiction Scoring
      addictionScore: {
        level: 1,              // 1-10 addiction level
        triggers: [],          // What makes them engage
        optimalFrequency: 10,  // Alerts per day
        bestTimes: [],         // When they engage most
        fomoSensitivity: 5    // 1-10 how they respond to FOMO
      },

      // Trading Profile (for relevant alerts)
      trading: {
        style: data.tradingStyle || 'swing',  // scalp, day, swing, hold
        riskTolerance: data.riskTolerance || 5,
        averagePositionSize: 1000,
        winRate: 0,
        preferredTimeframes: ['15m', '1h', '4h'],
        successfulPatterns: []
      },

      // Credit Management
      credits: {
        balance: data.creditBalance || 100,
        monthlySpend: 0,
        alertCosts: {},
        lastPurchase: null,
        tier: 'free'
      },

      // Alert History
      history: {
        recent: [],      // Last 100 alerts
        clicked: [],     // Alerts they engaged with
        ignored: [],     // Alerts they ignored
        profitable: []   // Alerts that led to profit
      }
    };

    // Store in cache
    this.userProfiles.set(userId, profile);

    // Generate MD file
    await this.generateUserMDFile(userId, profile);

    // Store in database
    await this.storeUserProfile(userId, profile);

    return profile;
  }

  /**
   * Generate user MD file
   */
  async generateUserMDFile(userId, profile) {
    const mdContent = `# User Profile: ${userId}

## Alert Configuration
- **Active Symbols**: ${profile.alerts.symbols.join(', ')}
- **Daily Alert Limit**: ${profile.alerts.maxDailyAlerts}
- **Credit Balance**: ${profile.credits.balance}
- **Subscription**: ${profile.credits.tier}

## Tracking Interests
### Price Targets
${JSON.stringify(profile.interests.priceTargets, null, 2)}

### Indicators Watching
${JSON.stringify(profile.interests.indicators, null, 2)}

### Patterns Following
${profile.interests.patterns.join(', ') || 'None'}

## Engagement Metrics
- **Alerts Received**: ${profile.engagement.alertsReceived}
- **Click Rate**: ${profile.engagement.clickRate}%
- **Addiction Level**: ${profile.addictionScore.level}/10
- **FOMO Sensitivity**: ${profile.addictionScore.fomoSensitivity}/10
- **Optimal Alert Frequency**: ${profile.addictionScore.optimalFrequency} per day

## Trading Profile
- **Style**: ${profile.trading.style}
- **Risk Tolerance**: ${profile.trading.riskTolerance}/10
- **Preferred Timeframes**: ${profile.trading.preferredTimeframes.join(', ')}

## Alert History
### Recent Alerts
${profile.history.recent.slice(0, 10).map(a => `- [${a.timestamp}] ${a.message}`).join('\n')}

## Optimization Notes
- Best alert times: ${profile.addictionScore.bestTimes.join(', ')}
- Top triggers: ${profile.addictionScore.triggers.join(', ')}
- Credits spent this month: ${profile.credits.monthlySpend}

---
*Profile updated: ${new Date().toISOString()}*
`;

    const filePath = path.join(
      process.env.USER_PROFILES_PATH || './profiles',
      `user_${userId}.md`
    );

    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, mdContent);
  }

  /**
   * CHECK AND SEND PERSONALIZED ALERTS
   */
  async checkAndSendAlerts(userId) {
    const profile = this.userProfiles.get(userId);
    if (!profile || !profile.alerts.enabled) return;

    const alerts = [];

    // Check each symbol the user tracks
    for (const symbol of profile.alerts.symbols) {
      const symbolData = await this.getSymbolData(symbol);

      // Price alerts
      const priceAlerts = this.checkPriceAlerts(symbol, symbolData, profile);
      alerts.push(...priceAlerts);

      // Indicator alerts
      const indicatorAlerts = this.checkIndicatorAlerts(symbol, symbolData, profile);
      alerts.push(...indicatorAlerts);

      // Pattern alerts
      const patternAlerts = this.checkPatternAlerts(symbol, symbolData, profile);
      alerts.push(...patternAlerts);

      // Whale alerts
      const whaleAlerts = this.checkWhaleAlerts(symbol, symbolData, profile);
      alerts.push(...whaleAlerts);

      // Volume/Unusual activity
      const activityAlerts = this.checkActivityAlerts(symbol, symbolData, profile);
      alerts.push(...activityAlerts);
    }

    // Sort by priority and engagement score
    const prioritizedAlerts = this.prioritizeAlerts(alerts, profile);

    // Send alerts (costs credits!)
    for (const alert of prioritizedAlerts) {
      if (profile.credits.balance >= alert.creditCost) {
        await this.sendAlert(userId, alert);

        // Deduct credits
        profile.credits.balance -= alert.creditCost;
        profile.credits.monthlySpend += alert.creditCost;

        // Track engagement
        profile.engagement.alertsReceived++;
        profile.history.recent.unshift(alert);

        // Update addiction scoring
        await this.updateAddictionScore(userId, alert);
      }
    }

    // Update profile
    await this.updateUserProfile(userId, profile);
  }

  /**
   * Check price alerts
   */
  checkPriceAlerts(symbol, data, profile) {
    const alerts = [];
    const targets = profile.interests.priceTargets[symbol] || [];
    const currentPrice = data.market.price;

    for (const target of targets) {
      if (Math.abs(currentPrice - target) / target < 0.01) { // Within 1%
        alerts.push({
          type: 'price_target',
          priority: 'important',
          creditCost: this.creditCosts.important,
          symbol,
          message: `🎯 ${symbol} approaching your target $${target}! Currently $${currentPrice}`,
          fomo: true,
          engagementScore: this.addictionMetrics.engagementMultipliers.priceBreakout
        });
      }
    }

    // Breakout alerts
    if (data.market.change24h > 10) {
      alerts.push({
        type: 'breakout',
        priority: 'critical',
        creditCost: this.creditCosts.critical,
        symbol,
        message: `🚀 ${symbol} BREAKING OUT! Up ${data.market.change24h}% - Don't miss this move!`,
        fomo: true,
        engagementScore: this.addictionMetrics.engagementMultipliers.priceBreakout * 1.5
      });
    }

    return alerts;
  }

  /**
   * Check indicator alerts
   */
  checkIndicatorAlerts(symbol, data, profile) {
    const alerts = [];
    const watching = profile.interests.indicators[symbol] || [];

    // RSI alerts
    if (watching.includes('RSI')) {
      if (data.indicators.rsi.value < 30) {
        alerts.push({
          type: 'rsi_oversold',
          priority: 'important',
          creditCost: this.creditCosts.important,
          symbol,
          message: `📊 ${symbol} RSI at ${data.indicators.rsi.value} - OVERSOLD! Bounce opportunity?`,
          fomo: true,
          engagementScore: this.addictionMetrics.engagementMultipliers.indicatorTrigger
        });
      } else if (data.indicators.rsi.value > 70) {
        alerts.push({
          type: 'rsi_overbought',
          priority: 'standard',
          creditCost: this.creditCosts.standard,
          symbol,
          message: `⚠️ ${symbol} RSI at ${data.indicators.rsi.value} - Overbought warning`,
          engagementScore: this.addictionMetrics.engagementMultipliers.indicatorTrigger
        });
      }
    }

    // MACD cross
    if (watching.includes('MACD') && data.indicators.macd.crossover) {
      alerts.push({
        type: 'macd_cross',
        priority: 'important',
        creditCost: this.creditCosts.important,
        symbol,
        message: `📈 ${symbol} MACD ${data.indicators.macd.crossover > 0 ? 'BULLISH' : 'BEARISH'} CROSS!`,
        fomo: true,
        engagementScore: this.addictionMetrics.engagementMultipliers.indicatorTrigger * 1.2
      });
    }

    return alerts;
  }

  /**
   * Check whale alerts
   */
  checkWhaleAlerts(symbol, data, profile) {
    const alerts = [];

    if (data.whales.recentTransactions.length > 0) {
      const whale = data.whales.recentTransactions[0];
      if (whale.amount > 1000000) { // $1M+ transaction
        alerts.push({
          type: 'whale_movement',
          priority: 'critical',
          creditCost: this.creditCosts.critical,
          symbol,
          message: `🐋 WHALE ALERT! ${whale.type === 'buy' ? 'Bought' : 'Sold'} $${(whale.amount/1000000).toFixed(1)}M of ${symbol}!`,
          fomo: true,
          engagementScore: this.addictionMetrics.engagementMultipliers.whaleMovement * 1.5
        });
      }
    }

    return alerts;
  }

  /**
   * Prioritize alerts based on addiction optimization
   */
  prioritizeAlerts(alerts, profile) {
    // Calculate engagement score for each alert
    alerts.forEach(alert => {
      alert.totalScore = alert.engagementScore;

      // Boost score based on user preferences
      if (profile.trading.style === 'scalp' && alert.type.includes('breakout')) {
        alert.totalScore *= 1.5;
      }

      // Boost FOMO-sensitive users
      if (alert.fomo && profile.addictionScore.fomoSensitivity > 7) {
        alert.totalScore *= 1.3;
      }

      // Time-based optimization
      const hour = new Date().getHours();
      if (profile.addictionScore.bestTimes.includes(hour)) {
        alert.totalScore *= 1.2;
      }
    });

    // Sort by total score
    return alerts.sort((a, b) => b.totalScore - a.totalScore);
  }

  /**
   * Send alert to user
   */
  async sendAlert(userId, alert) {
    try {
      // Add FOMO language if appropriate
      if (alert.fomo) {
        const fomoPrefix = this.fomoTriggers[Math.floor(Math.random() * this.fomoTriggers.length)];
        alert.message = fomoPrefix + ' ' + alert.message;
      }

      // Store alert
      await this.supabase.from('user_alerts').insert({
        user_id: userId,
        alert_type: alert.type,
        symbol: alert.symbol,
        message: alert.message,
        priority: alert.priority,
        credit_cost: alert.creditCost,
        engagement_score: alert.totalScore,
        created_at: new Date().toISOString()
      });

      // Send via preferred channels
      const profile = this.userProfiles.get(userId);

      // In-app notification
      this.emit('alert', {
        userId,
        alert,
        timestamp: Date.now()
      });

      // Track delivery
      console.log(`💸 Alert sent to ${userId}: ${alert.message} (Cost: ${alert.creditCost} credits)`);

      // Update last alert time
      profile.engagement.lastAlertTime = Date.now();

    } catch (error) {
      console.error('Failed to send alert:', error);
    }
  }

  /**
   * Update addiction score based on engagement
   */
  async updateAddictionScore(userId, alert) {
    const profile = this.userProfiles.get(userId);

    // Track alert pattern
    if (!profile.addictionScore.triggers.includes(alert.type)) {
      profile.addictionScore.triggers.push(alert.type);
    }

    // Update best times
    const hour = new Date().getHours();
    if (!profile.addictionScore.bestTimes.includes(hour)) {
      profile.addictionScore.bestTimes.push(hour);
    }

    // Increase addiction level if engaging frequently
    if (profile.engagement.clickRate > 50) {
      profile.addictionScore.level = Math.min(10, profile.addictionScore.level + 0.1);
    }

    // Optimize frequency
    if (profile.engagement.alertsReceived > 0) {
      const optimalFrequency = Math.round(
        (profile.engagement.alertsClicked / profile.engagement.alertsReceived) * 50
      );
      profile.addictionScore.optimalFrequency = Math.max(5, Math.min(50, optimalFrequency));
    }
  }

  /**
   * Generate daily summary (costs 1 credit)
   */
  async generateDailySummary(userId) {
    const profile = this.userProfiles.get(userId);
    if (profile.credits.balance < this.creditCosts.summary) return;

    const summary = {
      type: 'daily_summary',
      priority: 'info',
      creditCost: this.creditCosts.summary,
      message: await this.buildDailySummary(profile),
      engagementScore: this.addictionMetrics.engagementMultipliers.regularUpdate
    };

    await this.sendAlert(userId, summary);
  }

  /**
   * Build daily summary message
   */
  async buildDailySummary(profile) {
    const topMovers = [];
    const alerts = profile.history.recent.slice(0, 10);

    for (const symbol of profile.alerts.symbols) {
      const data = await this.getSymbolData(symbol);
      topMovers.push(`${symbol}: $${data.market.price} (${data.market.change24h > 0 ? '+' : ''}${data.market.change24h}%)`);
    }

    return `📊 Daily Summary

Your Symbols:
${topMovers.join('\n')}

Alerts Today: ${alerts.length}
Credits Used: ${profile.credits.monthlySpend}
Credits Remaining: ${profile.credits.balance}

Top Alert: ${alerts[0]?.message || 'No alerts yet'}

💡 Tip: Add more symbols to track more opportunities!`;
  }

  /**
   * Addiction optimizer - runs periodically
   */
  startAddictionOptimizer() {
    // Every hour, optimize alert timing
    setInterval(async () => {
      for (const [userId, profile] of this.userProfiles) {
        // Check if it's optimal time for user
        const hour = new Date().getHours();
        const isOptimalTime = this.isOptimalAlertTime(hour);

        if (isOptimalTime) {
          // Increase alert frequency during optimal times
          await this.checkAndSendAlerts(userId);
        }

        // Send summary if end of day
        if (hour === 22) {
          await this.generateDailySummary(userId);
        }
      }
    }, 3600000); // Every hour

    // Every minute, check for critical alerts
    setInterval(async () => {
      for (const [userId, profile] of this.userProfiles) {
        // Only check for critical alerts
        await this.checkCriticalAlerts(userId);
      }
    }, 60000); // Every minute
  }

  /**
   * Check if it's optimal time for alerts
   */
  isOptimalAlertTime(hour) {
    for (const period of Object.values(this.addictionMetrics.optimalAlertTimes)) {
      if (hour >= period.start && hour <= period.end) {
        return true;
      }
    }
    return false;
  }

  /**
   * Track user engagement
   */
  async trackEngagement(userId, alertId, action) {
    const profile = this.userProfiles.get(userId);
    if (!profile) return;

    if (action === 'click') {
      profile.engagement.alertsClicked++;
      profile.engagement.clickRate =
        (profile.engagement.alertsClicked / profile.engagement.alertsReceived) * 100;

      // Move to clicked history
      const alert = profile.history.recent.find(a => a.id === alertId);
      if (alert) {
        profile.history.clicked.push(alert);
      }

      // Update response time
      const responseTime = Date.now() - profile.engagement.lastAlertTime;
      profile.engagement.averageResponseTime =
        (profile.engagement.averageResponseTime + responseTime) / 2;

      // Increase addiction score for quick responses
      if (responseTime < 60000) { // Under 1 minute
        profile.addictionScore.level = Math.min(10, profile.addictionScore.level + 0.2);
      }
    } else if (action === 'ignore') {
      // Track ignored alerts
      const alert = profile.history.recent.find(a => a.id === alertId);
      if (alert) {
        profile.history.ignored.push(alert);
      }
    }

    // Update profile
    await this.updateUserProfile(userId, profile);
  }

  /**
   * Get user addiction report
   */
  async getUserAddictionReport(userId) {
    const profile = this.userProfiles.get(userId);
    if (!profile) return null;

    return {
      userId,
      addictionLevel: profile.addictionScore.level,
      engagementRate: profile.engagement.clickRate,
      creditsSpent: profile.credits.monthlySpend,
      favoriteSymbols: profile.alerts.symbols,
      bestAlertTimes: profile.addictionScore.bestTimes,
      optimalFrequency: profile.addictionScore.optimalFrequency,
      fomoSensitivity: profile.addictionScore.fomoSensitivity,
      monthlyAlerts: profile.engagement.alertsReceived,
      clickedAlerts: profile.engagement.alertsClicked,
      profitableAlerts: profile.history.profitable.length,
      recommendation: this.getAddictionRecommendation(profile)
    };
  }

  /**
   * Get recommendation for increasing addiction
   */
  getAddictionRecommendation(profile) {
    const recommendations = [];

    if (profile.alerts.symbols.length < 5) {
      recommendations.push('Add more symbols to track - each symbol increases alert opportunities');
    }

    if (profile.addictionScore.fomoSensitivity < 5) {
      recommendations.push('Enable whale alerts and breakout notifications');
    }

    if (profile.engagement.clickRate < 30) {
      recommendations.push('Adjust alert sensitivity - too many alerts causing fatigue');
    }

    if (profile.credits.balance < 50) {
      recommendations.push('Low credit balance - user might churn, send special offer');
    }

    return recommendations;
  }

  /**
   * Load user profiles from database
   */
  async loadUserProfiles() {
    const { data: profiles } = await this.supabase
      .from('user_profiles')
      .select('*');

    if (profiles) {
      for (const profile of profiles) {
        this.userProfiles.set(profile.user_id, profile.data);
      }
    }

    console.log(`📊 Loaded ${this.userProfiles.size} user profiles`);
  }

  /**
   * Store user profile
   */
  async storeUserProfile(userId, profile) {
    await this.supabase.from('user_profiles').upsert({
      user_id: userId,
      data: profile,
      updated_at: new Date().toISOString()
    });
  }
}

// Export singleton instance
const alertEngine = new UserProfileAlertEngine();
export default alertEngine;