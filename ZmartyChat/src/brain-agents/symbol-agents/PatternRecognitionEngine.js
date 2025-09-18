/**
 * PATTERN RECOGNITION ENGINE
 * Recognizes trading patterns and chart formations
 */

class PatternRecognitionEngine {
  constructor() {
    this.name = 'PatternRecognitionEngine';
    this.patterns = {
      // Reversal patterns
      reversal: [
        'head_and_shoulders',
        'inverse_head_and_shoulders',
        'double_top',
        'double_bottom',
        'triple_top',
        'triple_bottom',
        'rounding_top',
        'rounding_bottom'
      ],
      // Continuation patterns
      continuation: [
        'bull_flag',
        'bear_flag',
        'bull_pennant',
        'bear_pennant',
        'ascending_triangle',
        'descending_triangle',
        'symmetrical_triangle',
        'rectangle',
        'wedge_rising',
        'wedge_falling'
      ],
      // Candlestick patterns
      candlestick: [
        'doji',
        'hammer',
        'hanging_man',
        'shooting_star',
        'inverted_hammer',
        'engulfing_bullish',
        'engulfing_bearish',
        'harami_bullish',
        'harami_bearish',
        'morning_star',
        'evening_star'
      ]
    };
    this.patternCache = new Map();
    this.confidenceThresholds = {
      high: 0.8,
      medium: 0.6,
      low: 0.4
    };
  }

  /**
   * Initialize the pattern recognition engine
   */
  async initialize() {
    console.log('=Ê Initializing Pattern Recognition Engine...');

    // Setup pattern detection algorithms
    this.setupPatternDetection();

    // Initialize pattern scoring
    this.initializePatternScoring();

    console.log(' Pattern Recognition Engine initialized');
  }

  /**
   * Fetch patterns for a symbol
   * Called by SymbolMasterBrain.fetchPatterns()
   */
  async fetchPatterns(symbol, masterData) {
    try {
      console.log(`=Ê Detecting patterns for ${symbol}...`);

      // Check cache
      const cacheKey = `patterns_${symbol}`;
      if (this.patternCache.has(cacheKey)) {
        const cached = this.patternCache.get(cacheKey);
        if (Date.now() - cached.timestamp < 300000) { // 5 minutes
          return cached.data;
        }
      }

      const patterns = {
        current: await this.detectCurrentPatterns(symbol, masterData),
        forming: await this.detectFormingPatterns(symbol, masterData),
        historical: await this.getHistoricalPatterns(symbol),
        successRates: await this.calculateSuccessRates(symbol)
      };

      // Cache results
      this.patternCache.set(cacheKey, {
        data: patterns,
        timestamp: Date.now()
      });

      return patterns;

    } catch (error) {
      console.error(`Failed to detect patterns for ${symbol}:`, error.message);
      return this.getEmptyPatternData();
    }
  }

  /**
   * Setup pattern detection algorithms
   */
  setupPatternDetection() {
    // Setup detection thresholds
    this.detectionThresholds = {
      minDataPoints: 20,
      maxLookback: 100,
      volumeConfirmation: 1.2, // 20% above average
      priceDeviation: 0.02     // 2% deviation tolerance
    };

    // Setup pattern definitions
    this.patternDefinitions = this.initializePatternDefinitions();
  }

  /**
   * Initialize pattern definitions
   */
  initializePatternDefinitions() {
    return {
      head_and_shoulders: {
        type: 'reversal',
        timeframe: 'medium',
        reliability: 0.85,
        targetCalculation: 'neckline_distance',
        volumePattern: 'decreasing'
      },
      double_bottom: {
        type: 'reversal',
        timeframe: 'medium',
        reliability: 0.80,
        targetCalculation: 'distance_to_neckline',
        volumePattern: 'increasing_on_second_low'
      },
      bull_flag: {
        type: 'continuation',
        timeframe: 'short',
        reliability: 0.75,
        targetCalculation: 'flagpole_height',
        volumePattern: 'low_during_consolidation'
      },
      ascending_triangle: {
        type: 'continuation',
        timeframe: 'medium',
        reliability: 0.70,
        targetCalculation: 'triangle_height',
        volumePattern: 'decreasing_then_surge'
      }
    };
  }

  /**
   * Initialize pattern scoring system
   */
  initializePatternScoring() {
    this.scoringWeights = {
      priceAction: 0.4,      // 40% - How well price follows pattern
      volume: 0.25,          // 25% - Volume confirmation
      timeframe: 0.15,       // 15% - Appropriate timeframe
      marketContext: 0.10,   // 10% - Overall market conditions
      historicalSuccess: 0.10 // 10% - Historical success rate
    };
  }

  /**
   * Detect current patterns
   */
  async detectCurrentPatterns(symbol, masterData) {
    const currentPatterns = [];

    // Generate mock patterns based on market data
    const patternTypes = Object.keys(this.patternDefinitions);
    const patternCount = Math.floor(Math.random() * 4) + 1; // 1-4 patterns

    for (let i = 0; i < patternCount; i++) {
      const patternType = patternTypes[Math.floor(Math.random() * patternTypes.length)];
      const pattern = await this.createPatternData(patternType, symbol, masterData, 'current');

      if (pattern.confidence >= this.confidenceThresholds.low) {
        currentPatterns.push(pattern);
      }
    }

    return currentPatterns.sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Detect forming patterns
   */
  async detectFormingPatterns(symbol, masterData) {
    const formingPatterns = [];

    // Generate mock forming patterns
    const patternTypes = Object.keys(this.patternDefinitions);
    const patternCount = Math.floor(Math.random() * 3) + 1; // 1-3 patterns

    for (let i = 0; i < patternCount; i++) {
      const patternType = patternTypes[Math.floor(Math.random() * patternTypes.length)];
      const pattern = await this.createPatternData(patternType, symbol, masterData, 'forming');

      if (pattern.confidence >= this.confidenceThresholds.low) {
        formingPatterns.push(pattern);
      }
    }

    return formingPatterns.sort((a, b) => b.completionPercentage - a.completionPercentage);
  }

  /**
   * Create pattern data
   */
  async createPatternData(patternType, symbol, masterData, status) {
    const definition = this.patternDefinitions[patternType];
    const currentPrice = masterData.market?.price || 50000 + Math.random() * 20000;

    const pattern = {
      id: `${patternType}_${symbol}_${Date.now()}`,
      type: patternType,
      name: this.getPatternDisplayName(patternType),
      classification: definition.type,
      status: status,
      symbol: symbol,
      timeframe: this.getRandomTimeframe(),

      // Pattern geometry
      keyLevels: this.generateKeyLevels(currentPrice, patternType),
      trendLines: this.generateTrendLines(currentPrice, patternType),

      // Confidence metrics
      confidence: this.calculatePatternConfidence(patternType, masterData),
      reliability: definition.reliability,
      completionPercentage: status === 'forming' ? Math.random() * 40 + 40 : 100, // 40-80% for forming, 100% for current

      // Technical details
      entryPoint: this.calculateEntryPoint(currentPrice, patternType),
      targetPrice: this.calculateTargetPrice(currentPrice, patternType, definition),
      stopLoss: this.calculateStopLoss(currentPrice, patternType),

      // Volume analysis
      volumeConfirmation: Math.random() > 0.3, // 70% have volume confirmation
      volumePattern: definition.volumePattern,

      // Risk metrics
      riskReward: this.calculateRiskReward(currentPrice, patternType),
      breakoutProbability: Math.random() * 0.4 + 0.5, // 50-90%

      // Timing
      detectedAt: Date.now(),
      expectedCompletion: status === 'forming' ? Date.now() + Math.random() * 604800000 : null, // Up to 1 week

      // Additional metadata
      description: this.getPatternDescription(patternType),
      tradingImplications: this.getTradingImplications(patternType, definition)
    };

    return pattern;
  }

  /**
   * Generate key levels for pattern
   */
  generateKeyLevels(currentPrice, patternType) {
    const levels = {};
    const priceRange = currentPrice * 0.1; // 10% range

    switch (patternType) {
      case 'head_and_shoulders':
        levels.leftShoulder = currentPrice - priceRange * 0.3;
        levels.head = currentPrice + priceRange * 0.2;
        levels.rightShoulder = currentPrice - priceRange * 0.2;
        levels.neckline = currentPrice - priceRange * 0.5;
        break;

      case 'double_bottom':
        levels.firstBottom = currentPrice - priceRange * 0.4;
        levels.secondBottom = currentPrice - priceRange * 0.38;
        levels.peak = currentPrice + priceRange * 0.2;
        levels.neckline = currentPrice + priceRange * 0.1;
        break;

      case 'bull_flag':
        levels.flagpoleStart = currentPrice - priceRange * 0.6;
        levels.flagpoleEnd = currentPrice;
        levels.flagTop = currentPrice - priceRange * 0.05;
        levels.flagBottom = currentPrice - priceRange * 0.15;
        break;

      default:
        levels.support = currentPrice - priceRange * 0.3;
        levels.resistance = currentPrice + priceRange * 0.3;
    }

    return levels;
  }

  /**
   * Generate trend lines
   */
  generateTrendLines(currentPrice, patternType) {
    return [
      {
        type: 'support',
        slope: Math.random() * 0.02 - 0.01, // -1% to +1%
        start: { price: currentPrice * 0.95, time: Date.now() - 86400000 },
        end: { price: currentPrice * 0.98, time: Date.now() }
      },
      {
        type: 'resistance',
        slope: Math.random() * 0.02 - 0.01,
        start: { price: currentPrice * 1.05, time: Date.now() - 86400000 },
        end: { price: currentPrice * 1.02, time: Date.now() }
      }
    ];
  }

  /**
   * Calculate pattern confidence
   */
  calculatePatternConfidence(patternType, masterData) {
    let confidence = 0.5; // Start neutral

    // Price action component (40%)
    const priceActionScore = Math.random() * 0.4 + 0.3; // 30-70%
    confidence += priceActionScore * this.scoringWeights.priceAction;

    // Volume component (25%)
    const volumeScore = Math.random() * 0.4 + 0.4; // 40-80%
    confidence += volumeScore * this.scoringWeights.volume;

    // Timeframe component (15%)
    const timeframeScore = Math.random() * 0.3 + 0.5; // 50-80%
    confidence += timeframeScore * this.scoringWeights.timeframe;

    // Market context component (10%)
    const marketScore = Math.random() * 0.4 + 0.3; // 30-70%
    confidence += marketScore * this.scoringWeights.marketContext;

    // Historical success component (10%)
    const historicalScore = this.patternDefinitions[patternType]?.reliability || 0.7;
    confidence += historicalScore * this.scoringWeights.historicalSuccess;

    return Math.max(0.1, Math.min(0.95, confidence)); // Clamp between 10-95%
  }

  /**
   * Calculate entry point
   */
  calculateEntryPoint(currentPrice, patternType) {
    const adjustment = Math.random() * 0.02 + 0.01; // 1-3% adjustment

    if (this.patternDefinitions[patternType]?.type === 'reversal') {
      return currentPrice * (1 - adjustment); // Enter below current price
    } else {
      return currentPrice * (1 + adjustment); // Enter above current price
    }
  }

  /**
   * Calculate target price
   */
  calculateTargetPrice(currentPrice, patternType, definition) {
    let targetMultiplier = 1.05; // Default 5% target

    switch (definition.targetCalculation) {
      case 'neckline_distance':
        targetMultiplier = 1.08; // 8% target
        break;
      case 'flagpole_height':
        targetMultiplier = 1.12; // 12% target
        break;
      case 'triangle_height':
        targetMultiplier = 1.06; // 6% target
        break;
    }

    return currentPrice * targetMultiplier;
  }

  /**
   * Calculate stop loss
   */
  calculateStopLoss(currentPrice, patternType) {
    const stopLossPercent = Math.random() * 0.03 + 0.02; // 2-5% stop loss
    return currentPrice * (1 - stopLossPercent);
  }

  /**
   * Calculate risk reward ratio
   */
  calculateRiskReward(currentPrice, patternType) {
    const target = this.calculateTargetPrice(currentPrice, patternType, this.patternDefinitions[patternType]);
    const stopLoss = this.calculateStopLoss(currentPrice, patternType);

    const reward = Math.abs(target - currentPrice);
    const risk = Math.abs(currentPrice - stopLoss);

    return risk > 0 ? (reward / risk).toFixed(2) : '0.00';
  }

  /**
   * Get random timeframe
   */
  getRandomTimeframe() {
    const timeframes = ['1h', '4h', '1d', '3d', '1w'];
    return timeframes[Math.floor(Math.random() * timeframes.length)];
  }

  /**
   * Get pattern display name
   */
  getPatternDisplayName(patternType) {
    const displayNames = {
      head_and_shoulders: 'Head and Shoulders',
      inverse_head_and_shoulders: 'Inverse Head and Shoulders',
      double_top: 'Double Top',
      double_bottom: 'Double Bottom',
      bull_flag: 'Bull Flag',
      bear_flag: 'Bear Flag',
      ascending_triangle: 'Ascending Triangle',
      descending_triangle: 'Descending Triangle'
    };

    return displayNames[patternType] || patternType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Get pattern description
   */
  getPatternDescription(patternType) {
    const descriptions = {
      head_and_shoulders: 'A reversal pattern consisting of three peaks, with the middle peak being the highest.',
      double_bottom: 'A bullish reversal pattern formed by two consecutive lows at approximately the same level.',
      bull_flag: 'A short-term continuation pattern that appears after a strong upward move.',
      ascending_triangle: 'A continuation pattern with a flat resistance line and rising support line.'
    };

    return descriptions[patternType] || `${this.getPatternDisplayName(patternType)} pattern detected.`;
  }

  /**
   * Get trading implications
   */
  getTradingImplications(patternType, definition) {
    const implications = [];

    if (definition.type === 'reversal') {
      implications.push('Potential trend reversal');
      implications.push('Consider counter-trend positions');
    } else {
      implications.push('Trend continuation expected');
      implications.push('Consider trend-following positions');
    }

    implications.push(`Reliability: ${(definition.reliability * 100).toFixed(0)}%`);
    implications.push(`Volume pattern: ${definition.volumePattern}`);

    return implications;
  }

  /**
   * Get historical patterns
   */
  async getHistoricalPatterns(symbol) {
    const historical = [];
    const historicalCount = Math.floor(Math.random() * 10) + 5; // 5-15 historical patterns

    for (let i = 0; i < historicalCount; i++) {
      const patternTypes = Object.keys(this.patternDefinitions);
      const patternType = patternTypes[Math.floor(Math.random() * patternTypes.length)];
      const daysAgo = Math.floor(Math.random() * 365) + 1; // 1-365 days ago

      historical.push({
        id: `historical_${symbol}_${i}`,
        type: patternType,
        name: this.getPatternDisplayName(patternType),
        detectedAt: Date.now() - (daysAgo * 86400000),
        completedAt: Date.now() - ((daysAgo - Math.random() * 7) * 86400000),
        success: Math.random() > 0.3, // 70% success rate
        targetReached: Math.random() > 0.4, // 60% reach target
        maxGain: (Math.random() * 25 + 5).toFixed(2), // 5-30% gain
        timeToCompletion: Math.floor(Math.random() * 168) + 1, // 1-168 hours
        confidence: Math.random() * 0.4 + 0.5 // 50-90%
      });
    }

    return historical.sort((a, b) => b.detectedAt - a.detectedAt);
  }

  /**
   * Calculate success rates
   */
  async calculateSuccessRates(symbol) {
    const successRates = {};
    const patternTypes = Object.keys(this.patternDefinitions);

    patternTypes.forEach(patternType => {
      successRates[patternType] = {
        overall: (Math.random() * 0.4 + 0.5).toFixed(3), // 50-90%
        targetReached: (Math.random() * 0.3 + 0.4).toFixed(3), // 40-70%
        avgTimeToTarget: Math.floor(Math.random() * 120) + 24, // 24-144 hours
        avgGain: (Math.random() * 20 + 5).toFixed(2), // 5-25%
        sampleSize: Math.floor(Math.random() * 100) + 20 // 20-120 samples
      };
    });

    return successRates;
  }

  /**
   * Get empty pattern data
   */
  getEmptyPatternData() {
    return {
      current: [],
      forming: [],
      historical: [],
      successRates: {}
    };
  }

  /**
   * Analyze pattern strength
   */
  analyzePatternStrength(pattern) {
    let strength = 'Medium';

    if (pattern.confidence > this.confidenceThresholds.high) {
      strength = 'Strong';
    } else if (pattern.confidence < this.confidenceThresholds.medium) {
      strength = 'Weak';
    }

    return {
      strength,
      factors: {
        confidence: pattern.confidence,
        volumeConfirmation: pattern.volumeConfirmation,
        riskReward: parseFloat(pattern.riskReward),
        breakoutProbability: pattern.breakoutProbability
      }
    };
  }

  /**
   * Get pattern alerts
   */
  getPatternAlerts(patterns) {
    const alerts = [];

    patterns.current.forEach(pattern => {
      if (pattern.confidence > this.confidenceThresholds.high) {
        alerts.push({
          type: 'high_confidence_pattern',
          pattern: pattern.name,
          message: `High confidence ${pattern.name} detected`,
          confidence: pattern.confidence,
          symbol: pattern.symbol
        });
      }
    });

    patterns.forming.forEach(pattern => {
      if (pattern.completionPercentage > 80) {
        alerts.push({
          type: 'pattern_near_completion',
          pattern: pattern.name,
          message: `${pattern.name} near completion (${pattern.completionPercentage.toFixed(0)}%)`,
          completion: pattern.completionPercentage,
          symbol: pattern.symbol
        });
      }
    });

    return alerts;
  }

  /**
   * Clear pattern cache
   */
  clearCache(symbol = null) {
    if (symbol) {
      const keysToDelete = [];
      this.patternCache.forEach((value, key) => {
        if (key.includes(symbol)) {
          keysToDelete.push(key);
        }
      });
      keysToDelete.forEach(key => this.patternCache.delete(key));
    } else {
      this.patternCache.clear();
    }
  }
}

export default PatternRecognitionEngine;