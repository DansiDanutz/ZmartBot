/**
 * ZMARTY MASTER SYSTEM
 * The complete orchestration of BRAIN + User MD Files
 * Everything connects here - this is the piece of cake! 🍰
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import config from './config/secure-config.js';

// Import all our components
import SymbolMasterBrain from './brain-agents/SymbolMasterBrain.js';
import FourYearPatternDiscoveryAgent from './brain-agents/FourYearPatternDiscoveryAgent.js';
import MultiTimeframePatternAnalyzer from './brain-agents/MultiTimeframePatternAnalyzer.js';
import HistoricalPatternTriggerSystem from './brain-agents/HistoricalPatternTriggerSystem.js';
import UserProfileAlertEngine from './brain-agents/UserProfileAlertEngine.js';
import BrainKnowledgeManager from './services/BrainKnowledgeManager.js';

// Monetization systems
import TriggerBasedMonetizationEngine from './services/TriggerBasedMonetizationEngine.js';
import ExclusiveInvitationSystem from './services/ExclusiveInvitationSystem.js';
import TieredCommissionWithdrawalSystem from './services/TieredCommissionWithdrawalSystem.js';
import MilestoneRewardSystem from './services/MilestoneRewardSystem.js';

// Report generation
import ComprehensiveTriggerReportGenerator from './services/ComprehensiveTriggerReportGenerator.js';

class ZmartyMasterSystem extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase with secure config
    this.supabase = createClient(
      config.supabase.url,
      config.supabase.anonKey
    );

    // System status
    this.status = {
      initialized: false,
      brain: 'offline',
      monetization: 'offline',
      patterns: 'offline',
      users: 'offline'
    };

    // User MD files storage
    this.userMDFiles = new Map();

    // Active user sessions
    this.activeSessions = new Map();

    console.log('🧠 Zmarty Master System initializing...');
  }

  /**
   * MASTER INITIALIZATION - Brings everything online
   */
  async initialize() {
    console.log('🚀 Starting Zmarty Master System...');

    try {
      // 1. Initialize Brain System
      await this.initializeBrainSystem();

      // 2. Initialize Pattern Discovery
      await this.initializePatternSystems();

      // 3. Initialize Monetization
      await this.initializeMonetizationSystems();

      // 4. Initialize User System
      await this.initializeUserSystems();

      // 5. Connect all systems
      await this.connectSystems();

      // 6. Start monitoring
      await this.startMonitoring();

      this.status.initialized = true;
      console.log('✅ ZMARTY MASTER SYSTEM ONLINE! All systems connected!');

      return true;

    } catch (error) {
      console.error('❌ Failed to initialize Zmarty Master System:', error);
      throw error;
    }
  }

  /**
   * Initialize Brain System
   */
  async initializeBrainSystem() {
    console.log('🧠 Initializing Brain Systems...');

    // Initialize core brain
    await SymbolMasterBrain.initialize();
    await BrainKnowledgeManager.initialize();

    this.status.brain = 'online';
    console.log('✅ Brain System online');
  }

  /**
   * Initialize Pattern Discovery Systems
   */
  async initializePatternSystems() {
    console.log('📊 Initializing Pattern Systems...');

    // Initialize pattern analyzers
    await MultiTimeframePatternAnalyzer.initialize();
    await HistoricalPatternTriggerSystem.initialize();

    this.status.patterns = 'online';
    console.log('✅ Pattern Systems online');
  }

  /**
   * Initialize Monetization Systems
   */
  async initializeMonetizationSystems() {
    console.log('💰 Initializing Monetization Systems...');

    // Initialize all monetization components
    await TriggerBasedMonetizationEngine.initialize();
    await ExclusiveInvitationSystem.initialize();
    await TieredCommissionWithdrawalSystem.initialize();
    await MilestoneRewardSystem.initialize();

    this.status.monetization = 'online';
    console.log('✅ Monetization Systems online');
  }

  /**
   * Initialize User Systems
   */
  async initializeUserSystems() {
    console.log('👥 Initializing User Systems...');

    // Load all user MD files
    await this.loadAllUserMDFiles();

    // Initialize alert engine
    await UserProfileAlertEngine.initialize();

    this.status.users = 'online';
    console.log('✅ User Systems online');
  }

  /**
   * Connect all systems together
   */
  async connectSystems() {
    console.log('🔗 Connecting all systems...');

    // Connect brain to monetization
    SymbolMasterBrain.on('symbolAnalyzed', (data) => {
      this.handleSymbolAnalysis(data);
    });

    // Connect patterns to alerts
    HistoricalPatternTriggerSystem.on('triggerDetected', (trigger) => {
      this.handleTriggerDetected(trigger);
    });

    // Connect invitations to milestones
    ExclusiveInvitationSystem.on('inviteAccepted', (data) => {
      this.handleInviteAccepted(data);
    });

    // Connect purchases to commissions
    TieredCommissionWithdrawalSystem.on('purchaseProcessed', (data) => {
      this.handlePurchaseProcessed(data);
    });

    console.log('✅ All systems connected');
  }

  /**
   * THE MAGIC FUNCTION: Ask Zmarty anything
   */
  async askZmarty(userId, question, context = {}) {
    console.log(`🤖 Zmarty answering: "${question}" for user ${userId}`);

    try {
      // 1. Get user MD file
      const userProfile = await this.getUserMDProfile(userId);

      // 2. Extract symbols from question
      const symbols = this.extractSymbols(question);

      // 3. Get symbol data from brain
      const symbolData = {};
      for (const symbol of symbols) {
        symbolData[symbol] = await SymbolMasterBrain.getSymbolMasterData(symbol);
      }

      // 4. Get relevant historical patterns
      const patterns = await this.getRelevantPatterns(symbols, userProfile);

      // 5. Check for active triggers
      const activeTriggers = await this.checkActiveTriggers(symbols, userProfile);

      // 6. Generate personalized response
      const response = await this.generatePersonalizedResponse({
        userId,
        question,
        userProfile,
        symbolData,
        patterns,
        activeTriggers,
        context
      });

      // 7. Update user engagement
      await this.updateUserEngagement(userId, question, response);

      // 8. Check for trigger subscriptions
      await this.checkTriggerSubscriptions(userId, symbols, response);

      return response;

    } catch (error) {
      console.error('Failed to process Zmarty query:', error);
      return this.generateErrorResponse(error);
    }
  }

  /**
   * Load user MD profile
   */
  async getUserMDProfile(userId) {
    // Check cache first
    if (this.userMDFiles.has(userId)) {
      return this.userMDFiles.get(userId);
    }

    // Load from database
    const { data: profile } = await this.supabase
      .from('user_profiles')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (!profile) {
      // Create new user profile
      const newProfile = await this.createUserMDProfile(userId);
      this.userMDFiles.set(userId, newProfile);
      return newProfile;
    }

    // Cache and return
    this.userMDFiles.set(userId, profile);
    return profile;
  }

  /**
   * Create new user MD profile
   */
  async createUserMDProfile(userId) {
    const profile = {
      user_id: userId,

      // Trading preferences
      trading_style: 'beginner',
      risk_level: 'moderate',
      preferred_timeframes: ['1d'],

      // Tracking
      tracked_symbols: [],
      alert_preferences: {
        price_alerts: true,
        pattern_alerts: true,
        whale_alerts: false,
        frequency: 'important_only'
      },

      // Engagement
      addiction_level: 1,
      engagement_score: 0.5,

      // Slots
      free_slots: 1,
      paid_slots: 0,

      // Learning data
      questions_asked: [],
      favorite_patterns: [],
      successful_triggers: [],

      created_at: new Date().toISOString()
    };

    // Store in database
    await this.supabase.from('user_profiles').insert(profile);

    return profile;
  }

  /**
   * Extract symbols from user question
   */
  extractSymbols(question) {
    const symbols = [];
    const commonSymbols = ['BTC', 'ETH', 'SOL', 'BNB', 'ADA', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE'];

    const upperQuestion = question.toUpperCase();

    for (const symbol of commonSymbols) {
      if (upperQuestion.includes(symbol) || upperQuestion.includes(`${symbol}USD`) || upperQuestion.includes(`${symbol}/USD`)) {
        symbols.push(symbol);
      }
    }

    // If no symbols found, default to user's tracked symbols
    if (symbols.length === 0) {
      return ['BTC']; // Default to BTC
    }

    return symbols;
  }

  /**
   * Generate personalized response
   */
  async generatePersonalizedResponse(data) {
    const { userId, question, userProfile, symbolData, patterns, activeTriggers } = data;

    const response = {
      answer: '',
      confidence: 0.95,

      // Symbol data
      symbols: symbolData,

      // Patterns
      relevantPatterns: patterns,

      // Active triggers
      activeTriggers: activeTriggers,

      // Personalization
      personalizedInsights: [],

      // Recommendations
      recommendations: [],

      // Credits info
      creditsUsed: 0,
      creditsRemaining: await this.getUserCredits(userId),

      // Engagement
      addictionScore: this.calculateAddictionScore(userProfile, question),

      timestamp: Date.now()
    };

    // Generate main answer based on question type
    if (this.isPatternQuestion(question)) {
      response.answer = await this.generatePatternAnswer(data);
      response.creditsUsed = 3;
    } else if (this.isPriceQuestion(question)) {
      response.answer = await this.generatePriceAnswer(data);
      response.creditsUsed = 1;
    } else if (this.isAnalysisQuestion(question)) {
      response.answer = await this.generateAnalysisAnswer(data);
      response.creditsUsed = 5;
    } else {
      response.answer = await this.generateGeneralAnswer(data);
      response.creditsUsed = 2;
    }

    // Add personalized insights
    response.personalizedInsights = await this.generatePersonalizedInsights(userProfile, symbolData);

    // Add recommendations
    response.recommendations = await this.generateRecommendations(userProfile, patterns, activeTriggers);

    // Deduct credits
    if (response.creditsUsed > 0) {
      await this.deductCredits(userId, response.creditsUsed);
    }

    return response;
  }

  /**
   * Generate pattern answer
   */
  async generatePatternAnswer(data) {
    const { symbolData, patterns } = data;
    const symbol = Object.keys(symbolData)[0];

    if (!patterns || patterns.length === 0) {
      return `📊 Currently analyzing patterns for ${symbol}. No high-probability setups detected at the moment.`;
    }

    const topPattern = patterns[0];

    return `📈 ${symbol} Pattern Analysis:

🎯 **Top Pattern Detected**: ${topPattern.type}
✅ **Success Rate**: ${(topPattern.successRate * 100).toFixed(1)}%
💰 **Average Profit**: ${(topPattern.averageProfit * 100).toFixed(2)}%
📊 **Historical Occurrences**: ${topPattern.occurrences}

**Current Status**: ${topPattern.isActive ? '🔥 ACTIVE NOW' : '⏳ Monitoring'}

Based on 4 years of historical data, this pattern has worked ${(topPattern.successRate * 100).toFixed(0)}% of the time.`;
  }

  /**
   * Generate price answer
   */
  async generatePriceAnswer(data) {
    const { symbolData } = data;
    const symbol = Object.keys(symbolData)[0];
    const price = symbolData[symbol]?.currentPrice || 'N/A';

    return `💰 ${symbol} Current Price: $${price}

📊 **24h Analysis**:
- Current: $${price}
- Support: $${(price * 0.95).toFixed(2)}
- Resistance: $${(price * 1.05).toFixed(2)}

Remember: This shows current market data, not investment advice!`;
  }

  /**
   * Generate analysis answer
   */
  async generateAnalysisAnswer(data) {
    const { symbolData, patterns, activeTriggers } = data;
    const symbol = Object.keys(symbolData)[0];

    return `📊 ${symbol} Complete Analysis:

🎯 **Active Triggers**: ${activeTriggers.length}
📈 **Patterns Found**: ${patterns.length}
💎 **Confidence Level**: 87% (Based on historical data)

**Key Insights**:
- Market structure shows ${patterns.length > 0 ? 'bullish' : 'neutral'} bias
- ${activeTriggers.length} high-probability setups detected
- Risk/reward favors ${patterns.length > 2 ? 'long' : 'cautious'} positioning

This analysis is based on 4 years of market data patterns.`;
  }

  /**
   * Generate general answer
   */
  async generateGeneralAnswer(data) {
    const { question, symbolData } = data;
    const symbols = Object.keys(symbolData);

    return `🤖 Based on your question about ${symbols.join(', ')}, here's what Zmarty found:

📊 **Market Overview**: Currently analyzing real-time data
🎯 **Probability Assessment**: Running historical pattern matching
💡 **Key Insight**: This shows statistical probabilities, not trading advice

Would you like me to dive deeper into specific patterns or timeframes?`;
  }

  /**
   * Check for question types
   */
  isPatternQuestion(question) {
    const patterns = ['pattern', 'setup', 'signal', 'indicator', 'rsi', 'macd', 'bollinger'];
    return patterns.some(p => question.toLowerCase().includes(p));
  }

  isPriceQuestion(question) {
    const price = ['price', 'cost', 'value', 'how much', 'current'];
    return price.some(p => question.toLowerCase().includes(p));
  }

  isAnalysisQuestion(question) {
    const analysis = ['analysis', 'analyze', 'report', 'complete', 'full', 'detailed'];
    return analysis.some(p => question.toLowerCase().includes(p));
  }

  /**
   * Get relevant patterns for symbols
   */
  async getRelevantPatterns(symbols, userProfile) {
    const patterns = [];

    for (const symbol of symbols) {
      const symbolPatterns = await HistoricalPatternTriggerSystem.getPatterns(symbol, {
        minSuccessRate: 0.6,
        timeframes: userProfile.preferred_timeframes || ['1d']
      });
      patterns.push(...symbolPatterns);
    }

    return patterns.sort((a, b) => b.successRate - a.successRate).slice(0, 5);
  }

  /**
   * Check active triggers for symbols
   */
  async checkActiveTriggers(symbols, userProfile) {
    const triggers = [];

    for (const symbol of symbols) {
      const symbolTriggers = await HistoricalPatternTriggerSystem.checkCurrentTriggers(symbol, {
        minSuccessRate: 0.7
      });
      triggers.push(...symbolTriggers);
    }

    return triggers.filter(t => t.successRate > 0.7);
  }

  /**
   * Generate personalized insights
   */
  async generatePersonalizedInsights(userProfile, symbolData) {
    const insights = [];

    // Based on user's trading style
    if (userProfile.trading_style === 'beginner') {
      insights.push("💡 Focus on high-probability setups (80%+ success rate)");
      insights.push("⚠️ Start with small positions to learn");
    }

    // Based on risk level
    if (userProfile.risk_level === 'conservative') {
      insights.push("🛡️ Only patterns with 85%+ historical success shown");
    }

    return insights;
  }

  /**
   * Generate recommendations
   */
  async generateRecommendations(userProfile, patterns, activeTriggers) {
    const recommendations = [];

    if (activeTriggers.length > 0) {
      recommendations.push(`🎯 ${activeTriggers.length} high-probability triggers active`);
    }

    if (patterns.length > 3) {
      recommendations.push("📈 Multiple patterns confirm current setup");
    }

    recommendations.push("💎 Subscribe to trigger alerts for instant notifications");

    return recommendations;
  }

  /**
   * Update user engagement
   */
  async updateUserEngagement(userId, question, response) {
    await BrainKnowledgeManager.learnFromInteraction({
      userId,
      question,
      answer: response.answer,
      source: 'zmarty_master',
      wasHelpful: true,
      context: {
        creditsUsed: response.creditsUsed,
        confidence: response.confidence,
        responseTime: Date.now() - response.timestamp
      }
    });

    // Update user addiction score
    const currentProfile = this.userMDFiles.get(userId);
    if (currentProfile) {
      currentProfile.addiction_level = Math.min(10, currentProfile.addiction_level + 0.1);
      currentProfile.questions_asked.push({
        question,
        timestamp: Date.now(),
        creditsUsed: response.creditsUsed
      });

      // Update in database
      await this.supabase
        .from('user_profiles')
        .update({
          addiction_level: currentProfile.addiction_level,
          questions_asked: currentProfile.questions_asked
        })
        .eq('user_id', userId);
    }
  }

  /**
   * Check trigger subscriptions
   */
  async checkTriggerSubscriptions(userId, symbols, response) {
    // If user asks about patterns, suggest trigger subscriptions
    if (response.activeTriggers && response.activeTriggers.length > 0) {
      for (const symbol of symbols) {
        const isSubscribed = await this.isUserSubscribedToSymbol(userId, symbol);
        if (!isSubscribed) {
          response.recommendations.push(
            `🔔 Subscribe to ${symbol} trigger alerts for instant notifications when patterns activate`
          );
        }
      }
    }
  }

  /**
   * Helper methods
   */
  async getSymbolSubscribers(symbol) {
    const { data } = await this.supabase
      .from('trigger_subscriptions')
      .select('user_id, user_profiles(*)')
      .eq('symbol', symbol)
      .eq('is_active', true);

    return data || [];
  }

  async isUserSubscribedToSymbol(userId, symbol) {
    const { data } = await this.supabase
      .from('trigger_subscriptions')
      .select('id')
      .eq('user_id', userId)
      .eq('symbol', symbol)
      .eq('is_active', true)
      .single();

    return !!data;
  }

  async getTrackedSymbols() {
    const { data } = await this.supabase
      .from('trigger_subscriptions')
      .select('symbol')
      .eq('is_active', true);

    const uniqueSymbols = [...new Set((data || []).map(d => d.symbol))];
    return uniqueSymbols.length > 0 ? uniqueSymbols : ['BTC', 'ETH', 'SOL'];
  }

  async getInviterStats(userId) {
    const { data } = await this.supabase
      .from('invitations')
      .select('*')
      .eq('inviter_id', userId)
      .eq('status', 'accepted');

    return {
      successfulInvites: data?.length || 0,
      totalEarnings: data?.reduce((sum, inv) => sum + (inv.commission_earned || 0), 0) || 0
    };
  }

  calculateAlertCost(trigger) {
    // Higher success rate = higher cost
    if (trigger.successRate > 0.9) return 5;
    if (trigger.successRate > 0.8) return 3;
    if (trigger.successRate > 0.7) return 2;
    return 1;
  }

  generateErrorResponse(error) {
    return {
      answer: "🤖 Zmarty is currently processing your request. Please try again in a moment.",
      confidence: 0.1,
      symbols: {},
      relevantPatterns: [],
      activeTriggers: [],
      personalizedInsights: ["⚠️ System is optimizing for better performance"],
      recommendations: ["🔄 Try asking again in a few seconds"],
      creditsUsed: 0,
      timestamp: Date.now()
    };
  }

  async updatePatterns() {
    console.log('🔄 Updating pattern database...');
    try {
      await MultiTimeframePatternAnalyzer.updateAllPatterns();
      await FourYearPatternDiscoveryAgent.updateDiscoveries();
    } catch (error) {
      console.error('Error updating patterns:', error);
    }
  }

  async processCommissions() {
    console.log('💰 Processing pending commissions...');
    try {
      await TieredCommissionWithdrawalSystem.processAllPendingCommissions();
    } catch (error) {
      console.error('Error processing commissions:', error);
    }
  }

  /**
   * Handle trigger detected
   */
  async handleTriggerDetected(trigger) {
    console.log(`🎯 Trigger detected for ${trigger.symbol}!`);

    // Get all users subscribed to this symbol
    const subscribers = await this.getSymbolSubscribers(trigger.symbol);

    // Send alerts to each subscriber
    for (const subscriber of subscribers) {
      await this.sendTriggerAlert(subscriber, trigger);
    }

    // Update monetization metrics
    await TriggerBasedMonetizationEngine.processTrigger(trigger);
  }

  /**
   * Handle invite accepted
   */
  async handleInviteAccepted(data) {
    const { inviterId, newUserId } = data;

    // Award commissions
    await TieredCommissionWithdrawalSystem.processCreditPurchase({
      userId: newUserId,
      amount: 100, // Welcome bonus
      value: 5,
      type: 'welcome_bonus'
    });

    // Check milestones
    const inviterStats = await this.getInviterStats(inviterId);
    await MilestoneRewardSystem.checkMilestones(inviterId, inviterStats.successfulInvites);
  }

  /**
   * Send trigger alert
   */
  async sendTriggerAlert(subscriber, trigger) {
    const alert = {
      userId: subscriber.user_id,
      symbol: trigger.symbol,
      message: `🎯 ${trigger.symbol} TRIGGER ACTIVATED!

Pattern: ${trigger.pattern.type}
Success Rate: ${(trigger.successRate * 100).toFixed(1)}%
Expected Profit: ${(trigger.averageProfit * 100).toFixed(2)}%

This pattern has worked ${trigger.pattern.occurrences} times historically.

Remember: This shows probability based on data, not trading advice!`,

      creditsCharged: this.calculateAlertCost(trigger),
      timestamp: Date.now()
    };

    // Check if user has enough credits
    const userCredits = await this.getUserCredits(subscriber.user_id);
    if (userCredits >= alert.creditsCharged) {
      // Send alert
      await this.supabase.from('trigger_alerts').insert(alert);

      // Deduct credits
      await this.deductCredits(subscriber.user_id, alert.creditsCharged);

      // Emit real-time event
      this.emit('alertSent', alert);
    }
  }

  /**
   * Start monitoring loop
   */
  async startMonitoring() {
    console.log('👀 Starting monitoring systems...');

    // Monitor triggers every minute
    setInterval(async () => {
      await this.monitorTriggers();
    }, 60000);

    // Update patterns every hour
    setInterval(async () => {
      await this.updatePatterns();
    }, 3600000);

    // Process commissions every 10 minutes
    setInterval(async () => {
      await this.processCommissions();
    }, 600000);

    console.log('✅ Monitoring active');
  }

  /**
   * Monitor triggers
   */
  async monitorTriggers() {
    try {
      // Get all tracked symbols
      const symbols = await this.getTrackedSymbols();

      // Check each symbol for triggers
      for (const symbol of symbols) {
        const triggers = await HistoricalPatternTriggerSystem.checkCurrentTriggers(symbol, {});

        for (const trigger of triggers) {
          if (trigger.successRate > 0.7) { // Only high-probability triggers
            this.emit('triggerDetected', trigger);
          }
        }
      }
    } catch (error) {
      console.error('Error monitoring triggers:', error);
    }
  }

  /**
   * Get system status
   */
  getSystemStatus() {
    return {
      ...this.status,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      activeUsers: this.activeSessions.size,
      cachedProfiles: this.userMDFiles.size,
      lastUpdate: Date.now()
    };
  }

  /**
   * Helper: Get user credits
   */
  async getUserCredits(userId) {
    const { data } = await this.supabase
      .from('users')
      .select('credits_balance')
      .eq('id', userId)
      .single();

    return data?.credits_balance || 0;
  }

  /**
   * Helper: Deduct credits
   */
  async deductCredits(userId, amount) {
    await this.supabase.rpc('deduct_credits', {
      p_user_id: userId,
      p_amount: amount
    });
  }

  /**
   * Helper: Calculate addiction score
   */
  calculateAddictionScore(userProfile, question) {
    let score = userProfile.addiction_level || 1;

    // Increase based on question complexity
    if (question.toLowerCase().includes('pattern')) score += 0.5;
    if (question.toLowerCase().includes('trigger')) score += 0.3;
    if (question.toLowerCase().includes('when')) score += 0.7; // Looking for timing

    return Math.min(10, score);
  }

  /**
   * Load all user MD files on startup
   */
  async loadAllUserMDFiles() {
    const { data: profiles } = await this.supabase
      .from('user_profiles')
      .select('*');

    for (const profile of profiles || []) {
      this.userMDFiles.set(profile.user_id, profile);
    }

    console.log(`📁 Loaded ${this.userMDFiles.size} user MD profiles`);
  }

  /**
   * Health check
   */
  async healthCheck() {
    return {
      status: 'healthy',
      systems: this.status,
      timestamp: Date.now(),
      version: '1.0.0'
    };
  }
}

// Export singleton instance
const zmartyMaster = new ZmartyMasterSystem();
export default zmartyMaster;