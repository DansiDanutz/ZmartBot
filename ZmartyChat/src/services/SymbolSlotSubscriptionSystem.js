/**
 * SYMBOL SLOT SUBSCRIPTION SYSTEM
 * The core monetization engine - Query once, sell infinitely!
 * Users get 1 free slot, pay daily credits for additional slots
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import symbolMasterBrain from '../brain-agents/SymbolMasterBrain.js';
import alertEngine from '../brain-agents/UserProfileAlertEngine.js';

class SymbolSlotSubscriptionSystem extends EventEmitter {
  constructor() {
    super();

    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Symbol data cache - Query ONCE, sell MANY times!
    this.symbolDataCache = new Map();

    // User slot subscriptions
    this.userSlots = new Map();

    // Pricing model
    this.pricing = {
      freeSlots: 1,                    // Everyone gets 1 free
      dailyCostPerSlot: 10,            // 10 credits per day per slot
      premiumSlotCost: 20,             // Premium slots with more features
      bulkDiscount: {
        5: 0.9,   // 10% off for 5+ slots
        10: 0.8,  // 20% off for 10+ slots
        20: 0.7   // 30% off for 20+ slots
      }
    };

    // Data refresh intervals
    this.refreshIntervals = {
      realtime: 5000,        // 5 seconds for price
      fast: 60000,          // 1 minute for indicators
      medium: 300000,       // 5 minutes for analysis
      slow: 900000,         // 15 minutes for on-chain
      daily: 86400000       // Daily for intelligence
    };

    // What users get for their slot subscription
    this.slotFeatures = {
      basic: [
        'realtime_price',
        'basic_indicators',
        'support_resistance',
        'daily_summary'
      ],
      standard: [
        ...this.slotFeatures.basic,
        'advanced_indicators',
        'pattern_recognition',
        'risk_analysis',
        'hourly_updates'
      ],
      premium: [
        ...this.slotFeatures.standard,
        'whale_tracking',
        'liquidation_heatmap',
        'ai_predictions',
        'custom_alerts',
        'minute_updates'
      ]
    };

    this.initialize();
  }

  /**
   * Initialize the subscription system
   */
  async initialize() {
    console.log('💎 Initializing Symbol Slot Subscription System...');

    // Load user subscriptions
    await this.loadUserSubscriptions();

    // Start data collection cycles
    this.startDataCollection();

    // Start billing cycle
    this.startBillingCycle();

    // Start delivery cycle
    this.startDeliverySystem();

    console.log('✅ Subscription System Active - Query Once, Sell Infinitely!');
  }

  /**
   * USER SUBSCRIBES TO A SYMBOL SLOT
   */
  async subscribeToSymbol(userId, symbol, slotType = 'standard') {
    // Get user's current slots
    let userSlotData = this.userSlots.get(userId) || {
      userId,
      slots: [],
      totalDailyCost: 0,
      lastBilled: Date.now(),
      creditsBalance: 100
    };

    // Check if first slot (free)
    const isFreeSlot = userSlotData.slots.length < this.pricing.freeSlots;

    // Calculate cost
    const dailyCost = isFreeSlot ? 0 : this.getSlotCost(slotType, userSlotData.slots.length);

    // Check if user has enough credits for today
    if (!isFreeSlot && userSlotData.creditsBalance < dailyCost) {
      throw new Error(`Insufficient credits. Need ${dailyCost} credits per day for this slot.`);
    }

    // Create slot subscription
    const slot = {
      id: `${userId}_${symbol}_${Date.now()}`,
      symbol: symbol.toUpperCase(),
      slotType,
      subscribedAt: Date.now(),
      dailyCost,
      isFree: isFreeSlot,
      features: this.slotFeatures[slotType],
      lastDelivery: null,
      engagementScore: 0,
      profitableAlerts: 0,
      totalAlerts: 0
    };

    // Add to user's slots
    userSlotData.slots.push(slot);
    userSlotData.totalDailyCost = this.calculateTotalDailyCost(userSlotData.slots);

    // Save to cache
    this.userSlots.set(userId, userSlotData);

    // Save to database
    await this.saveUserSubscription(userId, userSlotData);

    // Immediately deliver first data package
    await this.deliverSymbolData(userId, slot);

    // Log the money maker!
    console.log(`💰 User ${userId} subscribed to ${symbol} (${isFreeSlot ? 'FREE' : dailyCost + ' credits/day'})`);

    return {
      slot,
      message: isFreeSlot ?
        `You're now tracking ${symbol} with your free slot!` :
        `You're now tracking ${symbol} for ${dailyCost} credits/day`,
      totalDailyCost: userSlotData.totalDailyCost,
      creditsBalance: userSlotData.creditsBalance
    };
  }

  /**
   * THE MAGIC: Query symbol data ONCE for ALL users!
   */
  async querySymbolDataOnce(symbol) {
    console.log(`🔄 Querying ${symbol} data ONCE for all users...`);

    // Get comprehensive data from Symbol Master Brain
    const masterData = await symbolMasterBrain.getSymbolMasterData(symbol);

    // Process into deliverable format
    const processedData = {
      symbol,
      queriedAt: Date.now(),
      expiresAt: Date.now() + this.refreshIntervals.fast,

      // REAL-TIME DATA
      realtime: {
        price: masterData.market.price,
        change24h: masterData.market.change24h,
        volume24h: masterData.market.volume24h,
        lastUpdate: Date.now()
      },

      // TRADING INTELLIGENCE
      trading: {
        signal: this.generateTradingSignal(masterData),
        entryZone: this.calculateEntryZone(masterData),
        targets: this.calculateTargets(masterData),
        stopLoss: this.calculateStopLoss(masterData),
        riskReward: this.calculateRiskReward(masterData),
        winRate: this.calculateWinRate(masterData)
      },

      // INDICATORS DASHBOARD
      indicators: {
        summary: this.generateIndicatorSummary(masterData),
        rsi: { value: masterData.indicators.rsi.value, signal: this.getRSISignal(masterData.indicators.rsi.value) },
        macd: { signal: masterData.indicators.macd.crossover ? 'BUY' : 'NEUTRAL' },
        bollinger: this.getBollingerSignal(masterData),
        ema: this.getEMASignal(masterData),
        volume: this.getVolumeSignal(masterData)
      },

      // PATTERNS & TRIGGERS
      patterns: {
        active: this.identifyActivePatterns(masterData),
        forming: this.identifyFormingPatterns(masterData),
        completed: this.getCompletedPatterns(masterData),
        triggers: this.generateTriggers(masterData)
      },

      // RISK ANALYSIS
      risk: {
        currentLevel: this.calculateRiskLevel(masterData),
        volatility: this.calculateVolatility(masterData),
        liquidationZones: this.identifyLiquidationZones(masterData),
        safetyScore: this.calculateSafetyScore(masterData)
      },

      // WHALE & ON-CHAIN
      whales: {
        recentActivity: this.processWhaleActivity(masterData),
        accumulation: masterData.whales.accumulation,
        alerts: this.generateWhaleAlerts(masterData)
      },

      // AI INSIGHTS (The addiction maker!)
      insights: {
        prediction: this.generatePrediction(masterData),
        recommendation: this.generateRecommendation(masterData),
        opportunities: this.findOpportunities(masterData),
        warnings: this.generateWarnings(masterData)
      },

      // ENGAGEMENT CONTENT
      engagement: {
        quickStats: this.generateQuickStats(masterData),
        didYouKnow: this.generateDidYouKnow(masterData),
        compareToYesterday: this.compareToYesterday(masterData),
        profitIfFollowed: this.calculateProfitIfFollowed(masterData)
      }
    };

    // Cache it - THIS IS THE GOLD!
    this.symbolDataCache.set(symbol, processedData);

    // Track query cost vs revenue
    console.log(`✅ ${symbol} data cached - Will be sold to ${this.countSymbolSubscribers(symbol)} users!`);

    return processedData;
  }

  /**
   * DELIVER data to user (the addiction delivery!)
   */
  async deliverSymbolData(userId, slot) {
    // Get cached data or query if needed
    let symbolData = this.symbolDataCache.get(slot.symbol);

    if (!symbolData || symbolData.expiresAt < Date.now()) {
      symbolData = await this.querySymbolDataOnce(slot.symbol);
    }

    // Prepare personalized delivery based on slot type
    const delivery = this.preparePersonalizedDelivery(symbolData, slot);

    // Create beautiful formatted message
    const message = this.formatDeliveryMessage(delivery, slot);

    // Store delivery
    await this.storeDelivery(userId, slot, delivery);

    // Send to user
    await this.sendToUser(userId, message, slot);

    // Update engagement
    slot.lastDelivery = Date.now();
    slot.totalAlerts++;

    return delivery;
  }

  /**
   * Prepare personalized delivery based on slot type
   */
  preparePersonalizedDelivery(data, slot) {
    const delivery = {
      timestamp: Date.now(),
      symbol: data.symbol,
      slotType: slot.slotType
    };

    // Basic features (free slot)
    if (slot.features.includes('realtime_price')) {
      delivery.price = data.realtime;
    }

    if (slot.features.includes('basic_indicators')) {
      delivery.indicators = {
        rsi: data.indicators.rsi,
        summary: data.indicators.summary
      };
    }

    // Standard features
    if (slot.features.includes('advanced_indicators')) {
      delivery.indicators = data.indicators;
    }

    if (slot.features.includes('pattern_recognition')) {
      delivery.patterns = data.patterns;
    }

    if (slot.features.includes('risk_analysis')) {
      delivery.risk = data.risk;
    }

    // Premium features
    if (slot.features.includes('whale_tracking')) {
      delivery.whales = data.whales;
    }

    if (slot.features.includes('ai_predictions')) {
      delivery.insights = data.insights;
    }

    if (slot.features.includes('liquidation_heatmap')) {
      delivery.liquidations = data.risk.liquidationZones;
    }

    // Always include engagement content (addiction!)
    delivery.engagement = data.engagement;

    // Add trading setup if good opportunity
    if (data.trading.signal !== 'NEUTRAL') {
      delivery.tradingSetup = {
        signal: data.trading.signal,
        entry: data.trading.entryZone,
        targets: data.trading.targets,
        stopLoss: data.trading.stopLoss,
        riskReward: data.trading.riskReward,
        winRate: data.trading.winRate
      };
    }

    return delivery;
  }

  /**
   * Format delivery message (the addiction content!)
   */
  formatDeliveryMessage(delivery, slot) {
    let message = `📊 **${delivery.symbol} Update** (${slot.slotType.toUpperCase()} SLOT)\n\n`;

    // Price section
    if (delivery.price) {
      const emoji = delivery.price.change24h > 0 ? '📈' : '📉';
      message += `${emoji} **Price**: $${delivery.price.price.toLocaleString()} (${delivery.price.change24h > 0 ? '+' : ''}${delivery.price.change24h}%)\n`;
      message += `📊 **Volume**: $${(delivery.price.volume24h / 1e9).toFixed(2)}B\n\n`;
    }

    // Trading setup (THE MONEY MAKER!)
    if (delivery.tradingSetup) {
      message += `🎯 **TRADING OPPORTUNITY**\n`;
      message += `Signal: **${delivery.tradingSetup.signal}**\n`;
      message += `Entry: $${delivery.tradingSetup.entry}\n`;
      message += `Targets: ${delivery.tradingSetup.targets.map(t => `$${t}`).join(', ')}\n`;
      message += `Stop Loss: $${delivery.tradingSetup.stopLoss}\n`;
      message += `Risk/Reward: ${delivery.tradingSetup.riskReward}\n`;
      message += `Win Rate: ${delivery.tradingSetup.winRate}%\n\n`;
    }

    // Indicators
    if (delivery.indicators) {
      message += `📊 **Indicators**\n`;
      if (delivery.indicators.rsi) {
        message += `RSI: ${delivery.indicators.rsi.value} (${delivery.indicators.rsi.signal})\n`;
      }
      if (delivery.indicators.summary) {
        message += `Summary: ${delivery.indicators.summary}\n`;
      }
      message += '\n';
    }

    // Patterns & Triggers
    if (delivery.patterns) {
      if (delivery.patterns.active.length > 0) {
        message += `🎯 **Active Patterns**: ${delivery.patterns.active.join(', ')}\n`;
      }
      if (delivery.patterns.triggers.length > 0) {
        message += `⚡ **Triggers Set**: ${delivery.patterns.triggers.length} alerts waiting\n`;
      }
      message += '\n';
    }

    // Risk Analysis
    if (delivery.risk) {
      message += `⚠️ **Risk Level**: ${delivery.risk.currentLevel}/10\n`;
      message += `Safety Score: ${delivery.risk.safetyScore}%\n\n`;
    }

    // Whale Activity (FOMO TRIGGER!)
    if (delivery.whales && delivery.whales.recentActivity.length > 0) {
      message += `🐋 **WHALE ALERT**: ${delivery.whales.recentActivity[0]}\n\n`;
    }

    // AI Insights (ADDICTION CONTENT!)
    if (delivery.insights) {
      message += `🤖 **AI Insights**\n`;
      message += `Prediction: ${delivery.insights.prediction}\n`;
      message += `Recommendation: ${delivery.insights.recommendation}\n\n`;
    }

    // Engagement (KEEP THEM HOOKED!)
    if (delivery.engagement) {
      message += `💡 **Did You Know?**\n${delivery.engagement.didYouKnow}\n\n`;

      if (delivery.engagement.profitIfFollowed) {
        message += `💰 **If you followed our signals**: +${delivery.engagement.profitIfFollowed}%\n`;
      }
    }

    // Footer with slot info
    message += `---\n`;
    message += `Slot Type: ${slot.slotType} | Daily Cost: ${slot.dailyCost} credits\n`;

    if (slot.slotType === 'basic' || slot.slotType === 'standard') {
      message += `💎 Upgrade for more features!`;
    }

    return message;
  }

  /**
   * Generate trading signal
   */
  generateTradingSignal(masterData) {
    let bullishScore = 0;
    let bearishScore = 0;

    // Price action
    if (masterData.market.change24h > 3) bullishScore += 2;
    if (masterData.market.change24h < -3) bearishScore += 2;

    // RSI
    if (masterData.indicators.rsi.value < 30) bullishScore += 3;
    if (masterData.indicators.rsi.value > 70) bearishScore += 3;

    // MACD
    if (masterData.indicators.macd.crossover) bullishScore += 2;

    // Volume
    if (masterData.market.volume24h > masterData.indicators.volume.average * 1.5) {
      if (masterData.market.change24h > 0) bullishScore += 2;
      else bearishScore += 2;
    }

    // Determine signal
    if (bullishScore > bearishScore + 2) return 'STRONG BUY';
    if (bullishScore > bearishScore) return 'BUY';
    if (bearishScore > bullishScore + 2) return 'STRONG SELL';
    if (bearishScore > bullishScore) return 'SELL';

    return 'NEUTRAL';
  }

  /**
   * Calculate win rate based on historical patterns
   */
  calculateWinRate(masterData) {
    // Simulate based on pattern success rates
    const patterns = masterData.patterns.current || [];
    if (patterns.length === 0) return 65; // Default

    const avgSuccessRate = patterns.reduce((sum, p) => sum + (p.successRate || 0.65), 0) / patterns.length;
    return Math.round(avgSuccessRate * 100);
  }

  /**
   * Calculate risk/reward ratio
   */
  calculateRiskReward(masterData) {
    const entry = masterData.market.price;
    const target = entry * 1.05; // 5% target
    const stop = entry * 0.97;   // 3% stop

    const reward = target - entry;
    const risk = entry - stop;

    return `1:${(reward / risk).toFixed(1)}`;
  }

  /**
   * Daily billing cycle - COLLECT THE MONEY!
   */
  async startBillingCycle() {
    // Run every day at midnight
    setInterval(async () => {
      console.log('💰 Running daily billing cycle...');

      let totalCreditsCollected = 0;

      for (const [userId, userData] of this.userSlots) {
        // Calculate daily cost
        const dailyCost = userData.totalDailyCost;

        if (dailyCost > 0) {
          // Check if user has credits
          if (userData.creditsBalance >= dailyCost) {
            // Deduct credits
            userData.creditsBalance -= dailyCost;
            totalCreditsCollected += dailyCost;

            // Update last billed
            userData.lastBilled = Date.now();

            // Save
            await this.saveUserSubscription(userId, userData);

            console.log(`💳 Billed ${userId}: ${dailyCost} credits`);
          } else {
            // Insufficient credits - suspend paid slots
            await this.suspendPaidSlots(userId);

            // Send notification
            await this.notifyInsufficientCredits(userId, dailyCost, userData.creditsBalance);
          }
        }
      }

      console.log(`💰 Total credits collected: ${totalCreditsCollected}`);

      // Store metrics
      await this.storeBillingMetrics(totalCreditsCollected);

    }, 86400000); // 24 hours
  }

  /**
   * Delivery system - Keep them engaged!
   */
  startDeliverySystem() {
    // Real-time updates for premium users
    setInterval(async () => {
      await this.deliverToSlotType('premium');
    }, this.refreshIntervals.realtime);

    // Fast updates for standard users
    setInterval(async () => {
      await this.deliverToSlotType('standard');
    }, this.refreshIntervals.fast);

    // Regular updates for basic users
    setInterval(async () => {
      await this.deliverToSlotType('basic');
    }, this.refreshIntervals.medium);
  }

  /**
   * Deliver updates to specific slot type users
   */
  async deliverToSlotType(slotType) {
    for (const [userId, userData] of this.userSlots) {
      const slots = userData.slots.filter(s => s.slotType === slotType);

      for (const slot of slots) {
        // Check if enough time passed since last delivery
        const timeSinceLastDelivery = Date.now() - (slot.lastDelivery || 0);
        const minInterval = this.getMinDeliveryInterval(slotType);

        if (timeSinceLastDelivery >= minInterval) {
          await this.deliverSymbolData(userId, slot);
        }
      }
    }
  }

  /**
   * Get minimum delivery interval based on slot type
   */
  getMinDeliveryInterval(slotType) {
    switch (slotType) {
      case 'premium': return 60000;      // 1 minute
      case 'standard': return 300000;    // 5 minutes
      case 'basic': return 900000;       // 15 minutes
      default: return 900000;
    }
  }

  /**
   * Count how many users subscribe to a symbol
   */
  countSymbolSubscribers(symbol) {
    let count = 0;
    for (const [userId, userData] of this.userSlots) {
      count += userData.slots.filter(s => s.symbol === symbol).length;
    }
    return count;
  }

  /**
   * Get slot cost with bulk discounts
   */
  getSlotCost(slotType, currentSlotCount) {
    let baseCost = slotType === 'premium' ?
      this.pricing.premiumSlotCost :
      this.pricing.dailyCostPerSlot;

    // Apply bulk discount
    for (const [threshold, discount] of Object.entries(this.pricing.bulkDiscount)) {
      if (currentSlotCount >= threshold) {
        baseCost *= discount;
      }
    }

    return Math.round(baseCost);
  }

  /**
   * Calculate total daily cost for all slots
   */
  calculateTotalDailyCost(slots) {
    return slots.reduce((total, slot) => total + (slot.dailyCost || 0), 0);
  }

  /**
   * Get user's subscription summary
   */
  async getUserSubscriptionSummary(userId) {
    const userData = this.userSlots.get(userId);
    if (!userData) return null;

    return {
      userId,
      totalSlots: userData.slots.length,
      freeSlots: userData.slots.filter(s => s.isFree).length,
      paidSlots: userData.slots.filter(s => !s.isFree).length,
      symbols: userData.slots.map(s => s.symbol),
      dailyCost: userData.totalDailyCost,
      creditsBalance: userData.creditsBalance,
      slotsDetail: userData.slots.map(slot => ({
        symbol: slot.symbol,
        type: slot.slotType,
        dailyCost: slot.dailyCost,
        features: slot.features,
        engagementScore: slot.engagementScore
      }))
    };
  }

  /**
   * Load user subscriptions from database
   */
  async loadUserSubscriptions() {
    const { data: subscriptions } = await this.supabase
      .from('user_symbol_subscriptions')
      .select('*');

    if (subscriptions) {
      for (const sub of subscriptions) {
        this.userSlots.set(sub.user_id, sub.data);
      }
    }

    console.log(`📊 Loaded ${this.userSlots.size} user subscriptions`);
  }

  /**
   * Save user subscription
   */
  async saveUserSubscription(userId, userData) {
    await this.supabase.from('user_symbol_subscriptions').upsert({
      user_id: userId,
      data: userData,
      updated_at: new Date().toISOString()
    });
  }
}

// Export singleton instance
const subscriptionSystem = new SymbolSlotSubscriptionSystem();
export default subscriptionSystem;