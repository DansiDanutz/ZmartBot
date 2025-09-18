/**
 * TRIGGER ALERT SYSTEM
 * Manages trading triggers and alert generation
 */

class TriggerAlertSystem {
  constructor() {
    this.name = 'TriggerAlertSystem';
    this.triggerTypes = {
      price: ['support_break', 'resistance_break', 'price_target', 'stop_loss'],
      technical: ['rsi_oversold', 'rsi_overbought', 'macd_crossover', 'bollinger_breakout'],
      volume: ['volume_spike', 'volume_drought', 'unusual_activity'],
      pattern: ['pattern_completion', 'pattern_breakout', 'pattern_failure'],
      whale: ['large_transaction', 'whale_accumulation', 'whale_distribution'],
      news: ['sentiment_shift', 'major_news', 'social_spike']
    };
    this.activeTriggers = new Map();
    this.triggerHistory = [];
    this.alertQueue = [];
  }

  /**
   * Initialize the trigger alert system
   */
  async initialize() {
    console.log('=¨ Initializing Trigger Alert System...');

    // Setup trigger monitoring
    this.setupTriggerMonitoring();

    // Initialize alert delivery
    this.initializeAlertDelivery();

    // Setup trigger evaluation
    this.setupTriggerEvaluation();

    console.log(' Trigger Alert System initialized');
  }

  /**
   * Generate triggers for a symbol
   * Called by SymbolMasterBrain.fetchIndicators() and setupTriggers()
   */
  async generateTriggers(symbol, indicators, timeframe) {
    try {
      console.log(`=¨ Generating triggers for ${symbol} on ${timeframe}...`);

      const triggers = [];

      // Generate price-based triggers
      triggers.push(...await this.generatePriceTriggers(symbol, indicators, timeframe));

      // Generate technical triggers
      triggers.push(...await this.generateTechnicalTriggers(symbol, indicators, timeframe));

      // Generate volume triggers
      triggers.push(...await this.generateVolumeTriggers(symbol, indicators, timeframe));

      // Generate pattern triggers
      triggers.push(...await this.generatePatternTriggers(symbol, indicators, timeframe));

      return triggers;

    } catch (error) {
      console.error(`Failed to generate triggers for ${symbol}:`, error.message);
      return [];
    }
  }

  /**
   * Setup trigger monitoring infrastructure
   */
  setupTriggerMonitoring() {
    // Trigger evaluation intervals
    this.evaluationIntervals = {
      realtime: 1000,    // 1 second for price triggers
      fast: 60000,       // 1 minute for technical triggers
      medium: 300000,    // 5 minutes for pattern triggers
      slow: 900000       // 15 minutes for whale/news triggers
    };

    // Trigger priority levels
    this.priorityLevels = {
      critical: 1,
      high: 2,
      medium: 3,
      low: 4,
      info: 5
    };
  }

  /**
   * Initialize alert delivery system
   */
  initializeAlertDelivery() {
    // Alert delivery channels
    this.deliveryChannels = {
      websocket: true,
      webhook: false,
      email: false,
      sms: false,
      push: false
    };

    // Alert rate limiting
    this.rateLimits = {
      maxAlertsPerMinute: 10,
      maxAlertsPerHour: 50,
      maxAlertsPerDay: 200
    };

    this.alertCounters = {
      minute: { count: 0, resetTime: Date.now() + 60000 },
      hour: { count: 0, resetTime: Date.now() + 3600000 },
      day: { count: 0, resetTime: Date.now() + 86400000 }
    };
  }

  /**
   * Setup trigger evaluation methods
   */
  setupTriggerEvaluation() {
    this.evaluationMethods = {
      price_above: (current, target) => current > target,
      price_below: (current, target) => current < target,
      price_crosses_above: (current, previous, target) => previous <= target && current > target,
      price_crosses_below: (current, previous, target) => previous >= target && current < target,
      indicator_above: (value, threshold) => value > threshold,
      indicator_below: (value, threshold) => value < threshold,
      percentage_change: (current, reference, percent) => Math.abs((current - reference) / reference) >= percent,
      volume_spike: (current, average, multiplier) => current > (average * multiplier)
    };
  }

  /**
   * Generate price-based triggers
   */
  async generatePriceTriggers(symbol, indicators, timeframe) {
    const triggers = [];
    const currentPrice = indicators.current?.price || 50000 + Math.random() * 20000;

    // Support and resistance triggers
    const supportLevels = this.calculateSupportLevels(currentPrice);
    const resistanceLevels = this.calculateResistanceLevels(currentPrice);

    supportLevels.forEach((level, index) => {
      triggers.push({
        id: `support_${symbol}_${timeframe}_${index}`,
        type: 'support_break',
        symbol,
        timeframe,
        condition: 'price_crosses_below',
        target: level,
        currentValue: currentPrice,
        priority: currentPrice > level * 1.05 ? 'medium' : 'high',
        message: `${symbol} approaching support at $${level.toFixed(2)}`,
        action: 'watch_for_bounce_or_breakdown',
        createdAt: Date.now(),
        isActive: true
      });
    });

    resistanceLevels.forEach((level, index) => {
      triggers.push({
        id: `resistance_${symbol}_${timeframe}_${index}`,
        type: 'resistance_break',
        symbol,
        timeframe,
        condition: 'price_crosses_above',
        target: level,
        currentValue: currentPrice,
        priority: currentPrice < level * 0.95 ? 'medium' : 'high',
        message: `${symbol} approaching resistance at $${level.toFixed(2)}`,
        action: 'watch_for_breakout_or_rejection',
        createdAt: Date.now(),
        isActive: true
      });
    });

    // Percentage move triggers
    const percentageTriggers = [0.05, 0.10, 0.15, 0.20]; // 5%, 10%, 15%, 20%
    percentageTriggers.forEach(percent => {
      triggers.push({
        id: `price_move_up_${percent * 100}_${symbol}_${timeframe}`,
        type: 'price_target',
        symbol,
        timeframe,
        condition: 'percentage_change',
        target: currentPrice * (1 + percent),
        currentValue: currentPrice,
        priority: percent >= 0.15 ? 'high' : 'medium',
        message: `${symbol} moved ${(percent * 100).toFixed(0)}% up`,
        action: 'profit_taking_consideration',
        createdAt: Date.now(),
        isActive: true
      });

      triggers.push({
        id: `price_move_down_${percent * 100}_${symbol}_${timeframe}`,
        type: 'stop_loss',
        symbol,
        timeframe,
        condition: 'percentage_change',
        target: currentPrice * (1 - percent),
        currentValue: currentPrice,
        priority: percent >= 0.10 ? 'critical' : 'high',
        message: `${symbol} dropped ${(percent * 100).toFixed(0)}% down`,
        action: 'risk_management_review',
        createdAt: Date.now(),
        isActive: true
      });
    });

    return triggers;
  }

  /**
   * Generate technical indicator triggers
   */
  async generateTechnicalTriggers(symbol, indicators, timeframe) {
    const triggers = [];

    // RSI triggers
    if (indicators.current?.rsi) {
      const rsi = indicators.current.rsi;

      if (rsi > 50 && rsi < 70) {
        triggers.push({
          id: `rsi_overbought_approach_${symbol}_${timeframe}`,
          type: 'rsi_overbought',
          symbol,
          timeframe,
          condition: 'indicator_above',
          target: 70,
          currentValue: rsi,
          priority: 'medium',
          message: `${symbol} RSI approaching overbought (${rsi.toFixed(1)})`,
          action: 'watch_for_reversal_signals',
          createdAt: Date.now(),
          isActive: true
        });
      }

      if (rsi < 50 && rsi > 30) {
        triggers.push({
          id: `rsi_oversold_approach_${symbol}_${timeframe}`,
          type: 'rsi_oversold',
          symbol,
          timeframe,
          condition: 'indicator_below',
          target: 30,
          currentValue: rsi,
          priority: 'medium',
          message: `${symbol} RSI approaching oversold (${rsi.toFixed(1)})`,
          action: 'watch_for_bounce_signals',
          createdAt: Date.now(),
          isActive: true
        });
      }
    }

    // MACD triggers
    if (indicators.current?.macd) {
      const macd = indicators.current.macd;

      triggers.push({
        id: `macd_crossover_${symbol}_${timeframe}`,
        type: 'macd_crossover',
        symbol,
        timeframe,
        condition: 'macd_signal_cross',
        target: 0,
        currentValue: macd.histogram,
        priority: 'high',
        message: `${symbol} MACD showing ${macd.histogram > 0 ? 'bullish' : 'bearish'} momentum`,
        action: 'trend_confirmation',
        createdAt: Date.now(),
        isActive: true
      });
    }

    // Bollinger Bands triggers
    if (indicators.current?.bollinger) {
      const bb = indicators.current.bollinger;
      const currentPrice = indicators.current?.price || 50000 + Math.random() * 20000;

      if (currentPrice > bb.middle && currentPrice < bb.upper) {
        triggers.push({
          id: `bollinger_upper_approach_${symbol}_${timeframe}`,
          type: 'bollinger_breakout',
          symbol,
          timeframe,
          condition: 'price_crosses_above',
          target: bb.upper,
          currentValue: currentPrice,
          priority: 'medium',
          message: `${symbol} approaching upper Bollinger Band`,
          action: 'watch_for_breakout',
          createdAt: Date.now(),
          isActive: true
        });
      }

      if (currentPrice < bb.middle && currentPrice > bb.lower) {
        triggers.push({
          id: `bollinger_lower_approach_${symbol}_${timeframe}`,
          type: 'bollinger_breakout',
          symbol,
          timeframe,
          condition: 'price_crosses_below',
          target: bb.lower,
          currentValue: currentPrice,
          priority: 'medium',
          message: `${symbol} approaching lower Bollinger Band`,
          action: 'watch_for_bounce',
          createdAt: Date.now(),
          isActive: true
        });
      }
    }

    return triggers;
  }

  /**
   * Generate volume-based triggers
   */
  async generateVolumeTriggers(symbol, indicators, timeframe) {
    const triggers = [];
    const currentVolume = indicators.current?.volume || Math.random() * 1000000;
    const averageVolume = indicators.current?.volume_sma || currentVolume * 0.8;

    // Volume spike triggers
    const volumeMultipliers = [1.5, 2.0, 3.0, 5.0];
    volumeMultipliers.forEach(multiplier => {
      triggers.push({
        id: `volume_spike_${multiplier}x_${symbol}_${timeframe}`,
        type: 'volume_spike',
        symbol,
        timeframe,
        condition: 'volume_spike',
        target: averageVolume * multiplier,
        currentValue: currentVolume,
        priority: multiplier >= 3.0 ? 'high' : 'medium',
        message: `${symbol} volume spike ${multiplier}x average detected`,
        action: 'investigate_price_catalyst',
        createdAt: Date.now(),
        isActive: true
      });
    });

    // Volume drought trigger
    triggers.push({
      id: `volume_drought_${symbol}_${timeframe}`,
      type: 'volume_drought',
      symbol,
      timeframe,
      condition: 'indicator_below',
      target: averageVolume * 0.3,
      currentValue: currentVolume,
      priority: 'low',
      message: `${symbol} unusually low volume detected`,
      action: 'consolidation_pattern_watch',
      createdAt: Date.now(),
      isActive: true
    });

    return triggers;
  }

  /**
   * Generate pattern-based triggers
   */
  async generatePatternTriggers(symbol, indicators, timeframe) {
    const triggers = [];

    // Mock pattern triggers (would integrate with PatternRecognitionEngine)
    const patternTypes = ['head_and_shoulders', 'double_bottom', 'bull_flag', 'ascending_triangle'];
    const randomPattern = patternTypes[Math.floor(Math.random() * patternTypes.length)];

    triggers.push({
      id: `pattern_completion_${randomPattern}_${symbol}_${timeframe}`,
      type: 'pattern_completion',
      symbol,
      timeframe,
      condition: 'pattern_threshold',
      target: 85, // 85% completion
      currentValue: Math.random() * 30 + 60, // 60-90% completion
      priority: 'high',
      message: `${symbol} ${randomPattern} pattern nearing completion`,
      action: 'prepare_for_breakout',
      createdAt: Date.now(),
      isActive: true,
      metadata: {
        patternType: randomPattern,
        reliability: Math.random() * 0.3 + 0.6 // 60-90%
      }
    });

    return triggers;
  }

  /**
   * Calculate support levels
   */
  calculateSupportLevels(currentPrice) {
    const levels = [];
    const baseSupport = currentPrice * 0.95; // 5% below current

    // Generate 3-5 support levels
    for (let i = 0; i < 4; i++) {
      const level = baseSupport * (1 - (i * 0.03)); // 3% intervals
      levels.push(level);
    }

    return levels;
  }

  /**
   * Calculate resistance levels
   */
  calculateResistanceLevels(currentPrice) {
    const levels = [];
    const baseResistance = currentPrice * 1.05; // 5% above current

    // Generate 3-5 resistance levels
    for (let i = 0; i < 4; i++) {
      const level = baseResistance * (1 + (i * 0.03)); // 3% intervals
      levels.push(level);
    }

    return levels;
  }

  /**
   * Evaluate trigger conditions
   */
  async evaluateTrigger(trigger, currentData) {
    const method = this.evaluationMethods[trigger.condition];
    if (!method) return false;

    try {
      switch (trigger.condition) {
        case 'price_above':
        case 'price_below':
        case 'indicator_above':
        case 'indicator_below':
          return method(currentData.value, trigger.target);

        case 'price_crosses_above':
        case 'price_crosses_below':
          return method(currentData.current, currentData.previous, trigger.target);

        case 'percentage_change':
          return method(currentData.current, trigger.target, 0.01); // 1% threshold

        case 'volume_spike':
          return method(currentData.volume, currentData.averageVolume, trigger.multiplier || 2);

        default:
          return false;
      }
    } catch (error) {
      console.error(`Error evaluating trigger ${trigger.id}:`, error);
      return false;
    }
  }

  /**
   * Process triggered alert
   */
  async processTriggerAlert(trigger, currentData) {
    // Check rate limits
    if (!this.checkRateLimit()) {
      console.log('Rate limit exceeded, queuing alert');
      this.alertQueue.push({ trigger, currentData, timestamp: Date.now() });
      return;
    }

    // Create alert
    const alert = {
      id: `alert_${trigger.id}_${Date.now()}`,
      triggerId: trigger.id,
      symbol: trigger.symbol,
      type: trigger.type,
      priority: trigger.priority,
      message: trigger.message,
      action: trigger.action,
      currentValue: currentData.value,
      targetValue: trigger.target,
      timestamp: Date.now(),
      timeframe: trigger.timeframe
    };

    // Send alert
    await this.sendAlert(alert);

    // Update counters
    this.updateAlertCounters();

    // Add to history
    this.triggerHistory.push({
      ...trigger,
      firedAt: Date.now(),
      currentValue: currentData.value
    });

    // Deactivate one-time triggers
    if (trigger.type === 'price_target' || trigger.type === 'stop_loss') {
      trigger.isActive = false;
    }
  }

  /**
   * Check rate limits
   */
  checkRateLimit() {
    const now = Date.now();

    // Reset counters if needed
    Object.keys(this.alertCounters).forEach(period => {
      const counter = this.alertCounters[period];
      if (now > counter.resetTime) {
        counter.count = 0;
        const resetInterval = period === 'minute' ? 60000 : period === 'hour' ? 3600000 : 86400000;
        counter.resetTime = now + resetInterval;
      }
    });

    // Check limits
    if (this.alertCounters.minute.count >= this.rateLimits.maxAlertsPerMinute) return false;
    if (this.alertCounters.hour.count >= this.rateLimits.maxAlertsPerHour) return false;
    if (this.alertCounters.day.count >= this.rateLimits.maxAlertsPerDay) return false;

    return true;
  }

  /**
   * Update alert counters
   */
  updateAlertCounters() {
    this.alertCounters.minute.count++;
    this.alertCounters.hour.count++;
    this.alertCounters.day.count++;
  }

  /**
   * Send alert through configured channels
   */
  async sendAlert(alert) {
    console.log(`=¨ ALERT: ${alert.message}`);

    // WebSocket notification (mock)
    if (this.deliveryChannels.websocket) {
      this.broadcastWebSocket(alert);
    }

    // Additional delivery channels would be implemented here
    // Email, SMS, Push notifications, etc.
  }

  /**
   * Broadcast alert via WebSocket (mock)
   */
  broadcastWebSocket(alert) {
    // In real implementation, this would send to WebSocket clients
    console.log(`=á WebSocket broadcast: ${JSON.stringify(alert, null, 2)}`);
  }

  /**
   * Get active triggers for a symbol
   */
  getActiveTriggers(symbol) {
    const symbolTriggers = [];
    this.activeTriggers.forEach((triggers, key) => {
      if (key.includes(symbol)) {
        symbolTriggers.push(...triggers.filter(t => t.isActive));
      }
    });
    return symbolTriggers;
  }

  /**
   * Add custom trigger
   */
  addCustomTrigger(trigger) {
    const key = `${trigger.symbol}_${trigger.timeframe}`;
    if (!this.activeTriggers.has(key)) {
      this.activeTriggers.set(key, []);
    }
    this.activeTriggers.get(key).push({
      ...trigger,
      id: `custom_${Date.now()}`,
      createdAt: Date.now(),
      isActive: true
    });
  }

  /**
   * Remove trigger
   */
  removeTrigger(triggerId) {
    this.activeTriggers.forEach((triggers, key) => {
      const index = triggers.findIndex(t => t.id === triggerId);
      if (index !== -1) {
        triggers.splice(index, 1);
      }
    });
  }

  /**
   * Get trigger statistics
   */
  getTriggerStatistics() {
    let totalTriggers = 0;
    let activeTriggers = 0;
    const typeCount = {};

    this.activeTriggers.forEach(triggers => {
      triggers.forEach(trigger => {
        totalTriggers++;
        if (trigger.isActive) activeTriggers++;

        typeCount[trigger.type] = (typeCount[trigger.type] || 0) + 1;
      });
    });

    return {
      totalTriggers,
      activeTriggers,
      triggersInHistory: this.triggerHistory.length,
      queuedAlerts: this.alertQueue.length,
      typeDistribution: typeCount,
      rateLimitStatus: this.alertCounters
    };
  }

  /**
   * Process queued alerts
   */
  async processQueuedAlerts() {
    while (this.alertQueue.length > 0 && this.checkRateLimit()) {
      const queuedAlert = this.alertQueue.shift();
      await this.processTriggerAlert(queuedAlert.trigger, queuedAlert.currentData);
    }
  }

  /**
   * Clear trigger history
   */
  clearHistory(olderThan = null) {
    if (olderThan) {
      this.triggerHistory = this.triggerHistory.filter(
        trigger => trigger.firedAt > olderThan
      );
    } else {
      this.triggerHistory = [];
    }
  }

  /**
   * Export triggers configuration
   */
  exportTriggers() {
    const exportData = {
      activeTriggers: Array.from(this.activeTriggers.entries()),
      triggerHistory: this.triggerHistory.slice(-100), // Last 100 triggers
      configuration: {
        evaluationIntervals: this.evaluationIntervals,
        priorityLevels: this.priorityLevels,
        rateLimits: this.rateLimits
      },
      exportedAt: Date.now()
    };

    return exportData;
  }

  /**
   * Import triggers configuration
   */
  importTriggers(importData) {
    try {
      if (importData.activeTriggers) {
        this.activeTriggers = new Map(importData.activeTriggers);
      }

      if (importData.triggerHistory) {
        this.triggerHistory = importData.triggerHistory;
      }

      if (importData.configuration) {
        this.evaluationIntervals = { ...this.evaluationIntervals, ...importData.configuration.evaluationIntervals };
        this.priorityLevels = { ...this.priorityLevels, ...importData.configuration.priorityLevels };
        this.rateLimits = { ...this.rateLimits, ...importData.configuration.rateLimits };
      }

      return { success: true, message: 'Triggers imported successfully' };
    } catch (error) {
      return { success: false, message: `Import failed: ${error.message}` };
    }
  }
}

export default TriggerAlertSystem;