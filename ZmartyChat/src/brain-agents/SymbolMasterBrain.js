/**
 * SYMBOL MASTER BRAIN
 * Comprehensive symbol-centric knowledge system
 * When user asks about any symbol, EVERYTHING is instantly available
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

// Import specialized agents
import SymbolDataAggregator from './symbol-agents/SymbolDataAggregator.js';
import MarketDataCollector from './symbol-agents/MarketDataCollector.js';
import OnChainDataAgent from './symbol-agents/OnChainDataAgent.js';
import LiquidationClusterTracker from './symbol-agents/LiquidationClusterTracker.js';
import WhaleAlertMonitor from './symbol-agents/WhaleAlertMonitor.js';
import NewsIntelligenceAgent from './symbol-agents/NewsIntelligenceAgent.js';
import ExternalIntelligenceScraper from './symbol-agents/ExternalIntelligenceScraper.js';
import PatternRecognitionEngine from './symbol-agents/PatternRecognitionEngine.js';
import IndicatorAnalysisEngine from './symbol-agents/IndicatorAnalysisEngine.js';
import TriggerAlertSystem from './symbol-agents/TriggerAlertSystem.js';

class SymbolMasterBrain extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Symbol knowledge cache - EVERYTHING about each symbol
    this.symbolKnowledge = new Map();

    // Active tracking symbols
    this.activeSymbols = new Set(['BTC', 'ETH', 'SOL', 'BNB', 'MATIC']);

    // Data sources configuration
    this.dataSources = {
      // Internal APIs
      kingfisher: {
        url: process.env.KINGFISHER_API || 'http://localhost:8001',
        priority: 10
      },
      riskmetric: {
        url: process.env.RISKMETRIC_API || 'http://localhost:8002',
        priority: 10
      },

      // Exchange APIs
      binance: {
        url: 'https://api.binance.com/api/v3',
        priority: 9
      },
      kucoin: {
        url: 'https://api.kucoin.com/api/v1',
        priority: 8
      },

      // On-chain sources
      glassnode: {
        url: 'https://api.glassnode.com/v1',
        apiKey: process.env.GLASSNODE_API_KEY,
        priority: 8
      },
      santiment: {
        url: 'https://api.santiment.net/graphql',
        apiKey: process.env.SANTIMENT_API_KEY,
        priority: 7
      },

      // Intelligence sources
      cryptopanic: {
        url: 'https://cryptopanic.com/api/v1',
        apiKey: process.env.CRYPTOPANIC_API_KEY,
        priority: 6
      },
      messari: {
        url: 'https://data.messari.io/api/v1',
        apiKey: process.env.MESSARI_API_KEY,
        priority: 7
      },
      coinglass: {
        url: 'https://api.coinglass.com/api',
        priority: 9 // For liquidation data
      },

      // Social & Sentiment
      lunarcrush: {
        url: 'https://api.lunarcrush.com/v2',
        apiKey: process.env.LUNARCRUSH_API_KEY,
        priority: 6
      },

      // External intelligence sites to scrape
      externalSites: [
        'tradingview.com',
        'cryptoquant.com',
        'intotheblock.com',
        'dune.com',
        'nansen.ai',
        'arkham.intelligence',
        'debank.com',
        'defillama.com',
        'tokenterminal.com'
      ]
    };

    // Initialize sub-agents
    this.initializeAgents();

    // Update cycles
    this.updateIntervals = {
      realtime: 1000,      // 1 second for prices
      fast: 60000,         // 1 minute for indicators
      medium: 300000,      // 5 minutes for patterns
      slow: 900000,        // 15 minutes for on-chain
      daily: 86400000      // Daily for intelligence
    };

    // Start the brain
    this.initialize();
  }

  /**
   * Initialize all symbol agents
   */
  initializeAgents() {
    this.agents = {
      aggregator: new SymbolDataAggregator(),
      marketCollector: new MarketDataCollector(),
      onChainAgent: new OnChainDataAgent(),
      liquidationTracker: new LiquidationClusterTracker(),
      whaleMonitor: new WhaleAlertMonitor(),
      newsAgent: new NewsIntelligenceAgent(),
      intelligenceScraper: new ExternalIntelligenceScraper(),
      patternEngine: new PatternRecognitionEngine(),
      indicatorEngine: new IndicatorAnalysisEngine(),
      triggerSystem: new TriggerAlertSystem()
    };
  }

  /**
   * Initialize the symbol brain
   */
  async initialize() {
    console.log('🧠 Initializing Symbol Master Brain...');

    // Load existing symbol knowledge
    await this.loadSymbolKnowledge();

    // Start all update cycles
    this.startUpdateCycles();

    // Initialize agents
    for (const agent of Object.values(this.agents)) {
      await agent.initialize();
    }

    console.log('✅ Symbol Master Brain initialized');
  }

  /**
   * Load existing symbol knowledge from database
   */
  async loadSymbolKnowledge() {
    try {
      console.log('📚 Loading existing symbol knowledge...');

      const { data: symbols, error } = await this.supabase
        .from('symbol_knowledge')
        .select('symbol, data, updated_at')
        .order('updated_at', { ascending: false })
        .limit(100);

      if (error) {
        console.warn('⚠️  Could not load symbol knowledge:', error.message);
        return;
      }

      symbols?.forEach(symbolData => {
        if (symbolData.data) {
          this.symbolKnowledge.set(symbolData.symbol, {
            ...symbolData.data,
            lastUpdated: new Date(symbolData.updated_at).getTime()
          });
        }
      });

      console.log(`✅ Loaded ${symbols?.length || 0} symbol knowledge entries`);
    } catch (error) {
      console.warn('⚠️  Error loading symbol knowledge:', error.message);
    }
  }

  /**
   * GET EVERYTHING ABOUT A SYMBOL - THE MAIN FUNCTION
   */
  async getSymbolMasterData(symbol) {
    symbol = symbol.toUpperCase();

    // Check cache first
    if (this.symbolKnowledge.has(symbol)) {
      const cached = this.symbolKnowledge.get(symbol);

      // Return cached if fresh enough
      if (Date.now() - cached.lastUpdated < 60000) {
        return cached;
      }
    }

    // Build comprehensive symbol data
    const masterData = await this.buildSymbolMasterData(symbol);

    // Cache it
    this.symbolKnowledge.set(symbol, masterData);

    // Store in database
    await this.storeSymbolKnowledge(symbol, masterData);

    return masterData;
  }

  /**
   * Build complete symbol knowledge
   */
  async buildSymbolMasterData(symbol) {
    console.log(`🔄 Building master data for ${symbol}`);

    const masterData = {
      symbol,
      timestamp: Date.now(),
      lastUpdated: Date.now(),

      // CURRENT MARKET DATA
      market: {
        price: null,
        change24h: null,
        volume24h: null,
        marketCap: null,
        dominance: null,
        exchanges: {}
      },

      // HISTORICAL DATA (RiskMetric)
      history: {
        priceHistory: [],
        volatility: [],
        correlations: {},
        seasonalPatterns: [],
        historicalSupport: [],
        historicalResistance: []
      },

      // PROBABILITY ANALYSIS (Based on Real Data - Not Trading Advice)
      probabilities: {
        // Price movement probabilities
        upward_1h: null,     // Probability of upward move in 1 hour
        upward_4h: null,     // Probability of upward move in 4 hours
        upward_24h: null,    // Probability of upward move in 24 hours
        downward_1h: null,   // Probability of downward move in 1 hour
        downward_4h: null,   // Probability of downward move in 4 hours
        downward_24h: null,  // Probability of downward move in 24 hours

        // Key levels probabilities
        breakResistance: null,  // Probability of breaking resistance
        holdSupport: null,      // Probability of holding support
        volatilitySpike: null,  // Probability of volatility increase

        // Statistical odds (like poker)
        oddsInFavor: null,      // Overall odds in user's favor (>0.6 is good)
        riskRewardRatio: null,  // Risk/Reward ratio
        winRate: null,          // Historical win rate for similar setups

        // Confidence metrics
        dataPoints: null,       // Number of data points analyzed
        confidence: null,       // Confidence in probability calculations
        accuracy: null          // Historical accuracy of predictions
      },

      // LIQUIDATION DATA
      liquidations: {
        clusters: [],
        heatmap: {},
        largestLiquidations: [],
        totalLongs: null,
        totalShorts: null,
        fundingRate: null
      },

      // PATTERNS
      patterns: {
        current: [],
        forming: [],
        historical: [],
        successRates: {}
      },

      // INDICATORS (Each with history)
      indicators: {
        rsi: { value: null, history: [], triggers: [] },
        macd: { value: null, signal: null, histogram: null, history: [], triggers: [] },
        bollinger: { upper: null, middle: null, lower: null, history: [], triggers: [] },
        ema: { ema9: null, ema21: null, ema50: null, ema200: null, history: [] },
        volume: { current: null, average: null, profile: {}, history: [] },
        atr: { value: null, history: [] },
        stochastic: { k: null, d: null, history: [], triggers: [] },
        fibonacci: { levels: {}, history: [] }
      },

      // TRIGGERS (Based on history)
      triggers: {
        active: [],
        pending: [],
        historical: [],
        alerts: []
      },

      // ON-CHAIN DATA
      onChain: {
        activeAddresses: null,
        transactionVolume: null,
        exchangeFlows: {
          inflow: null,
          outflow: null,
          netflow: null
        },
        holderDistribution: {},
        supplyDynamics: {},
        networkHealth: {}
      },

      // WHALE MOVEMENTS
      whales: {
        recentTransactions: [],
        accumulation: [],
        distribution: [],
        alerts: [],
        walletTracking: []
      },

      // NEWS & SENTIMENT
      news: {
        latest: [],
        sentiment: {
          score: null,
          trend: null,
          sources: {}
        },
        events: [],
        social: {
          twitter: null,
          reddit: null,
          telegram: null
        }
      },

      // SMART IQ (External Intelligence)
      smartIQ: {
        tradingViewAnalysis: null,
        cryptoQuantMetrics: null,
        intoTheBlockData: null,
        duneAnalytics: null,
        nansenSignals: null,
        arkhamIntelligence: null,
        defiMetrics: null,
        dailySummary: null
      },

      // AI INSIGHTS
      aiInsights: {
        prediction: null,
        recommendation: null,
        riskAssessment: null,
        opportunities: [],
        warnings: []
      },

      // ADDICTION METRICS (Keep users engaged)
      engagement: {
        interestingFacts: [],
        didYouKnow: [],
        comparisons: [],
        milestones: [],
        achievements: []
      }
    };

    // Fetch all data in parallel for speed
    const fetchPromises = [
      this.fetchMarketData(symbol, masterData),
      this.fetchHistoricalData(symbol, masterData),
      this.calculateProbabilities(symbol, masterData), // Changed from fetchTradingIntelligence
      this.fetchLiquidationData(symbol, masterData),
      this.fetchPatterns(symbol, masterData),
      this.fetchIndicators(symbol, masterData),
      this.fetchOnChainData(symbol, masterData),
      this.fetchWhaleData(symbol, masterData),
      this.fetchNews(symbol, masterData),
      this.fetchExternalIntelligence(symbol, masterData)
    ];

    await Promise.allSettled(fetchPromises);

    // Generate AI insights based on all data
    masterData.aiInsights = await this.generateAIInsights(masterData);

    // Generate engagement content
    masterData.engagement = await this.generateEngagementContent(masterData);

    // Set up triggers based on history
    masterData.triggers = await this.setupTriggers(symbol, masterData);

    return masterData;
  }

  /**
   * Fetch current market data
   */
  async fetchMarketData(symbol, masterData) {
    try {
      // Binance data
      const binanceData = await axios.get(
        `${this.dataSources.binance.url}/ticker/24hr`,
        { params: { symbol: `${symbol}USDT` } }
      );

      if (binanceData.data) {
        masterData.market.price = parseFloat(binanceData.data.lastPrice);
        masterData.market.change24h = parseFloat(binanceData.data.priceChangePercent);
        masterData.market.volume24h = parseFloat(binanceData.data.volume);
        masterData.market.exchanges.binance = {
          price: parseFloat(binanceData.data.lastPrice),
          bid: parseFloat(binanceData.data.bidPrice),
          ask: parseFloat(binanceData.data.askPrice)
        };
      }

      // KuCoin data
      try {
        const kucoinData = await axios.get(
          `${this.dataSources.kucoin.url}/market/stats`,
          { params: { symbol: `${symbol}-USDT` } }
        );

        if (kucoinData.data) {
          masterData.market.exchanges.kucoin = {
            price: parseFloat(kucoinData.data.data.last),
            bid: parseFloat(kucoinData.data.data.buy),
            ask: parseFloat(kucoinData.data.data.sell)
          };
        }
      } catch (e) {
        // KuCoin might not have all symbols
      }

    } catch (error) {
      console.error(`Failed to fetch market data for ${symbol}:`, error.message);
    }
  }

  /**
   * Fetch historical data from RiskMetric
   */
  async fetchHistoricalData(symbol, masterData) {
    try {
      const response = await axios.get(
        `${this.dataSources.riskmetric.url}/api/history/${symbol}`
      );

      if (response.data) {
        masterData.history = {
          ...masterData.history,
          ...response.data
        };
      }
    } catch (error) {
      console.error(`Failed to fetch historical data for ${symbol}:`, error.message);
    }
  }

  /**
   * Calculate probabilities based on real data (NOT trading advice)
   */
  async calculateProbabilities(symbol, masterData) {
    try {
      // Gather all real data sources
      const marketData = masterData.market;
      const indicators = masterData.indicators;
      const patterns = masterData.patterns;
      const volume = masterData.market.volume24h;
      const sentiment = masterData.news.sentiment;
      const onChain = masterData.onChain;
      const whales = masterData.whales;

      // Calculate movement probabilities based on statistical analysis
      masterData.probabilities = {
        // Short-term probabilities (like poker hand odds)
        upward_1h: this.calculateMovementOdds(indicators, patterns, '1h', 'up'),
        upward_4h: this.calculateMovementOdds(indicators, patterns, '4h', 'up'),
        upward_24h: this.calculateMovementOdds(indicators, patterns, '24h', 'up'),
        downward_1h: this.calculateMovementOdds(indicators, patterns, '1h', 'down'),
        downward_4h: this.calculateMovementOdds(indicators, patterns, '4h', 'down'),
        downward_24h: this.calculateMovementOdds(indicators, patterns, '24h', 'down'),

        // Key level probabilities
        breakResistance: this.calculateBreakoutOdds(marketData, volume, 'resistance'),
        holdSupport: this.calculateSupportOdds(marketData, volume, 'support'),
        volatilitySpike: this.calculateVolatilityOdds(indicators, patterns),

        // Overall odds assessment (like poker - "pot odds")
        oddsInFavor: this.calculateOverallOdds(indicators, patterns, sentiment, onChain),
        riskRewardRatio: this.calculateRiskReward(marketData, masterData.history),
        winRate: await this.getHistoricalWinRate(symbol, indicators),

        // Meta information
        dataPoints: this.countDataPoints(masterData),
        confidence: this.calculateConfidence(masterData),
        accuracy: await this.getHistoricalAccuracy(symbol)
      };

      // Add interpretation (like poker advice: "Odds favor calling")
      masterData.probabilities.interpretation = this.interpretProbabilities(masterData.probabilities);

    } catch (error) {
      console.error(`Failed to calculate probabilities for ${symbol}:`, error.message);
    }
  }

  /**
   * Calculate movement odds based on indicators and patterns
   */
  calculateMovementOdds(indicators, patterns, timeframe, direction) {
    // Start with neutral probability (50/50)
    let probability = 0.5;
    let factors = 0;

    // RSI influence (oversold/overbought conditions)
    if (indicators.rsi?.value) {
      if (direction === 'up') {
        if (indicators.rsi.value < 30) probability += 0.15; // Oversold bounce odds
        if (indicators.rsi.value > 70) probability -= 0.10; // Overbought resistance
      } else {
        if (indicators.rsi.value > 70) probability += 0.15; // Overbought pullback odds
        if (indicators.rsi.value < 30) probability -= 0.10; // Oversold support
      }
      factors++;
    }

    // MACD influence
    if (indicators.macd) {
      const bullishCrossover = indicators.macd.value > indicators.macd.signal;
      if ((direction === 'up' && bullishCrossover) || (direction === 'down' && !bullishCrossover)) {
        probability += 0.08;
      } else {
        probability -= 0.05;
      }
      factors++;
    }

    // Moving average influence
    if (indicators.ema) {
      const priceAboveMA = this.market?.price > indicators.ema.ema50;
      if ((direction === 'up' && priceAboveMA) || (direction === 'down' && !priceAboveMA)) {
        probability += 0.07;
      }
      factors++;
    }

    // Pattern influence
    if (patterns.current?.length > 0) {
      const bullishPatterns = patterns.current.filter(p => p.type === 'bullish').length;
      const bearishPatterns = patterns.current.filter(p => p.type === 'bearish').length;

      if (direction === 'up') {
        probability += (bullishPatterns * 0.05);
        probability -= (bearishPatterns * 0.03);
      } else {
        probability += (bearishPatterns * 0.05);
        probability -= (bullishPatterns * 0.03);
      }
      factors++;
    }

    // Adjust for timeframe (shorter timeframes are less predictable)
    const timeframeMultiplier = {
      '1h': 0.85,   // Less certain
      '4h': 0.92,   // More certain
      '24h': 0.95   // Most certain for trends
    };

    probability = probability * (timeframeMultiplier[timeframe] || 1);

    // Cap between 5% and 95% (never absolute certainty)
    return Math.max(0.05, Math.min(0.95, probability));
  }

  /**
   * Calculate overall odds (like pot odds in poker)
   */
  calculateOverallOdds(indicators, patterns, sentiment, onChain) {
    const factors = [];
    const weights = [];

    // Technical analysis odds
    if (indicators) {
      let technicalScore = 0.5;
      if (indicators.rsi?.value < 30) technicalScore += 0.15;
      if (indicators.rsi?.value > 70) technicalScore -= 0.10;
      if (indicators.macd?.value > indicators.macd?.signal) technicalScore += 0.10;
      factors.push(technicalScore);
      weights.push(0.35); // 35% weight
    }

    // Pattern recognition odds
    if (patterns?.current) {
      const bullishPatterns = patterns.current.filter(p => p.type === 'bullish').length;
      const totalPatterns = patterns.current.length || 1;
      factors.push(bullishPatterns / totalPatterns);
      weights.push(0.25); // 25% weight
    }

    // Sentiment odds
    if (sentiment?.score) {
      factors.push((sentiment.score + 1) / 2); // Convert from -1 to 1 range to 0 to 1
      weights.push(0.20); // 20% weight
    }

    // On-chain odds
    if (onChain?.exchangeFlows) {
      // Negative netflow (leaving exchanges) is bullish
      const flowScore = onChain.exchangeFlows.netflow < 0 ? 0.65 : 0.35;
      factors.push(flowScore);
      weights.push(0.20); // 20% weight
    }

    // Calculate weighted average
    let weightedSum = 0;
    let totalWeight = 0;

    for (let i = 0; i < factors.length; i++) {
      weightedSum += factors[i] * weights[i];
      totalWeight += weights[i];
    }

    return totalWeight > 0 ? weightedSum / totalWeight : 0.5;
  }

  /**
   * Interpret probabilities for user (like poker advice)
   */
  interpretProbabilities(probabilities) {
    const interpretation = {
      action: '',
      reasoning: '',
      pokerAnalogy: ''
    };

    // Overall odds assessment
    if (probabilities.oddsInFavor > 0.65) {
      interpretation.action = 'ODDS STRONGLY IN FAVOR';
      interpretation.reasoning = 'Multiple indicators align positively';
      interpretation.pokerAnalogy = 'Like having pocket Aces - odds are in your favor';
    } else if (probabilities.oddsInFavor > 0.55) {
      interpretation.action = 'ODDS SLIGHTLY IN FAVOR';
      interpretation.reasoning = 'Some positive signals present';
      interpretation.pokerAnalogy = 'Like having AK suited - good odds but not guaranteed';
    } else if (probabilities.oddsInFavor < 0.35) {
      interpretation.action = 'ODDS AGAINST';
      interpretation.reasoning = 'Multiple negative indicators';
      interpretation.pokerAnalogy = 'Like having 2-7 offsuit - odds not in your favor';
    } else {
      interpretation.action = 'NEUTRAL ODDS';
      interpretation.reasoning = 'Mixed signals, no clear edge';
      interpretation.pokerAnalogy = 'Like having middle pair - could go either way';
    }

    // Risk/Reward assessment
    if (probabilities.riskRewardRatio > 3) {
      interpretation.reasoning += '. Excellent risk/reward ratio';
    } else if (probabilities.riskRewardRatio < 1) {
      interpretation.reasoning += '. Poor risk/reward ratio';
    }

    return interpretation;
  }

  /**
   * Fetch liquidation data
   */
  async fetchLiquidationData(symbol, masterData) {
    try {
      // Use CoinGlass or similar API for liquidation data
      const response = await axios.get(
        `${this.dataSources.coinglass.url}/liquidation/${symbol}`
      );

      if (response.data) {
        masterData.liquidations = {
          ...masterData.liquidations,
          clusters: response.data.clusters || [],
          heatmap: response.data.heatmap || {},
          totalLongs: response.data.totalLongs,
          totalShorts: response.data.totalShorts,
          fundingRate: response.data.fundingRate
        };
      }
    } catch (error) {
      // Store mock data for now
      masterData.liquidations.clusters = this.generateLiquidationClusters(masterData.market.price);
    }
  }

  /**
   * Fetch all indicators with history
   */
  async fetchIndicators(symbol, masterData) {
    try {
      // Get indicator data from multiple timeframes
      const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];

      for (const tf of timeframes) {
        const indicators = await this.agents.indicatorEngine.calculateAll(symbol, tf);

        // Store current values (use 15m as default display)
        if (tf === '15m') {
          masterData.indicators = {
            ...masterData.indicators,
            ...indicators.current
          };
        }

        // Store history for each indicator
        if (indicators.history) {
          Object.keys(indicators.history).forEach(indicator => {
            if (masterData.indicators[indicator]) {
              masterData.indicators[indicator].history.push({
                timeframe: tf,
                data: indicators.history[indicator]
              });
            }
          });
        }

        // Set up triggers based on historical levels
        const triggers = await this.agents.triggerSystem.generateTriggers(
          symbol,
          indicators,
          tf
        );

        masterData.triggers.pending.push(...triggers);
      }
    } catch (error) {
      console.error(`Failed to fetch indicators for ${symbol}:`, error.message);
    }
  }

  /**
   * Fetch on-chain data
   */
  async fetchOnChainData(symbol, masterData) {
    try {
      const onChainData = await this.agents.onChainAgent.fetchComprehensive(symbol);

      masterData.onChain = {
        ...masterData.onChain,
        ...onChainData
      };

      // Add Glassnode data if available
      if (this.dataSources.glassnode.apiKey) {
        const glassnodeData = await this.fetchGlassnodeMetrics(symbol);
        masterData.onChain = {
          ...masterData.onChain,
          ...glassnodeData
        };
      }
    } catch (error) {
      console.error(`Failed to fetch on-chain data for ${symbol}:`, error.message);
    }
  }

  /**
   * Fetch whale movements
   */
  async fetchWhaleData(symbol, masterData) {
    try {
      const whaleData = await this.agents.whaleMonitor.getWhaleActivity(symbol);

      masterData.whales = {
        ...masterData.whales,
        ...whaleData
      };

      // Check for whale alerts
      const alerts = await this.detectWhaleAlerts(whaleData);
      masterData.whales.alerts = alerts;

    } catch (error) {
      console.error(`Failed to fetch whale data for ${symbol}:`, error.message);
    }
  }

  /**
   * Fetch news and sentiment
   */
  async fetchNews(symbol, masterData) {
    try {
      const newsData = await this.agents.newsAgent.fetchLatest(symbol);

      masterData.news = {
        ...masterData.news,
        ...newsData
      };

      // Get sentiment from LunarCrush if available
      if (this.dataSources.lunarcrush.apiKey) {
        const sentiment = await this.fetchLunarCrushSentiment(symbol);
        masterData.news.sentiment = {
          ...masterData.news.sentiment,
          ...sentiment
        };
      }

    } catch (error) {
      console.error(`Failed to fetch news for ${symbol}:`, error.message);
    }
  }

  /**
   * Fetch external intelligence (Smart IQ)
   */
  async fetchExternalIntelligence(symbol, masterData) {
    try {
      // Scrape each external source
      const intelligencePromises = this.dataSources.externalSites.map(async (site) => {
        return await this.agents.intelligenceScraper.scrape(site, symbol);
      });

      const results = await Promise.allSettled(intelligencePromises);

      // Aggregate results
      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          const siteName = this.dataSources.externalSites[index].replace('.com', '').replace('.ai', '');
          masterData.smartIQ[siteName] = result.value;
        }
      });

      // Generate daily summary from all intelligence
      masterData.smartIQ.dailySummary = await this.generateDailySummary(masterData.smartIQ);

    } catch (error) {
      console.error(`Failed to fetch external intelligence for ${symbol}:`, error.message);
    }
  }

  /**
   * Generate AI insights from all data (Probabilities, not advice)
   */
  async generateAIInsights(masterData) {
    const insights = {
      probabilityAnalysis: null,
      dataInterpretation: null,
      riskAssessment: null,
      opportunities: [],
      warnings: []
    };

    try {
      // Probability-based analysis (NOT prediction)
      insights.probabilityAnalysis = this.analyzeProbabilities(masterData);

      // Data interpretation (explaining what the data shows)
      insights.dataInterpretation = this.interpretData(masterData);

      // Risk assessment based on statistical analysis
      insights.riskAssessment = this.assessStatisticalRisk(masterData);

      // Find statistical opportunities (high probability setups)
      insights.opportunities = this.findStatisticalOpportunities(masterData);

      // Generate data-based warnings
      insights.warnings = this.generateDataWarnings(masterData);

    } catch (error) {
      console.error('Failed to generate AI insights:', error);
    }

    return insights;
  }

  /**
   * Analyze probabilities (like analyzing poker odds)
   */
  analyzeProbabilities(masterData) {
    const probs = masterData.probabilities;

    return {
      summary: `Based on ${probs.dataPoints} data points analyzed`,
      shortTerm: `1H: ${(probs.upward_1h * 100).toFixed(1)}% up probability`,
      mediumTerm: `4H: ${(probs.upward_4h * 100).toFixed(1)}% up probability`,
      dayTrend: `24H: ${(probs.upward_24h * 100).toFixed(1)}% up probability`,
      keyLevels: `${(probs.breakResistance * 100).toFixed(1)}% chance to break resistance`,
      overall: probs.interpretation,
      confidence: `${(probs.confidence * 100).toFixed(0)}% confidence in analysis`
    };
  }

  /**
   * Interpret data objectively
   */
  interpretData(masterData) {
    const interpretations = [];

    // RSI interpretation
    if (masterData.indicators.rsi?.value) {
      const rsi = masterData.indicators.rsi.value;
      if (rsi > 70) {
        interpretations.push(`RSI at ${rsi.toFixed(1)} - Statistically overbought territory`);
      } else if (rsi < 30) {
        interpretations.push(`RSI at ${rsi.toFixed(1)} - Statistically oversold territory`);
      }
    }

    // Volume interpretation
    if (masterData.market.volume24h) {
      const avgVolume = masterData.indicators.volume?.average || masterData.market.volume24h;
      const volumeRatio = masterData.market.volume24h / avgVolume;
      if (volumeRatio > 1.5) {
        interpretations.push(`Volume ${(volumeRatio * 100 - 100).toFixed(0)}% above average - High activity`);
      }
    }

    // Whale activity
    if (masterData.whales?.recentTransactions?.length > 5) {
      interpretations.push(`${masterData.whales.recentTransactions.length} whale transactions detected`);
    }

    return interpretations;
  }

  /**
   * Assess statistical risk
   */
  assessStatisticalRisk(masterData) {
    let riskScore = 50; // Start neutral

    // Volatility risk
    if (masterData.history?.volatility?.length > 0) {
      const currentVol = masterData.history.volatility[0];
      if (currentVol > 50) riskScore += 20;
      if (currentVol > 75) riskScore += 20;
    }

    // Liquidation risk
    if (masterData.liquidations?.clusters?.length > 0) {
      const nearbyLiquidations = masterData.liquidations.clusters.filter(
        c => Math.abs(c.price - masterData.market.price) / masterData.market.price < 0.05
      );
      if (nearbyLiquidations.length > 0) riskScore += 15;
    }

    // Probability-based risk
    if (masterData.probabilities?.oddsInFavor < 0.4) {
      riskScore += 20;
    }

    const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low';

    return {
      score: riskScore,
      level: riskLevel,
      factors: `Volatility: ${masterData.history?.volatility?.[0]?.toFixed(1) || 'N/A'}%, Odds: ${(masterData.probabilities?.oddsInFavor * 100)?.toFixed(1) || 'N/A'}%`
    };
  }

  /**
   * Generate engagement content (addiction mechanics)
   */
  async generateEngagementContent(masterData) {
    const engagement = {
      interestingFacts: [],
      didYouKnow: [],
      comparisons: [],
      milestones: [],
      achievements: []
    };

    // Interesting facts
    engagement.interestingFacts.push(
      `${masterData.symbol} has moved ${Math.abs(masterData.market.change24h)}% in 24h`,
      `Current RSI: ${masterData.indicators.rsi.value} - ${this.getRSIInterpretation(masterData.indicators.rsi.value)}`,
      `${masterData.whales.recentTransactions.length} whale transactions in last hour`
    );

    // Did you know
    if (masterData.history.seasonalPatterns.length > 0) {
      engagement.didYouKnow.push(
        `${masterData.symbol} historically performs best in ${masterData.history.seasonalPatterns[0].month}`
      );
    }

    // Comparisons
    engagement.comparisons.push(
      `${masterData.symbol} volume is ${masterData.market.volume24h > 1000000000 ? 'above' : 'below'} $1B`,
      `Funding rate: ${masterData.liquidations.fundingRate}% - ${masterData.liquidations.fundingRate > 0 ? 'Longs paying shorts' : 'Shorts paying longs'}`
    );

    // Milestones
    if (masterData.market.price > masterData.history.historicalResistance[0]) {
      engagement.milestones.push(`Breaking above key resistance at $${masterData.history.historicalResistance[0]}`);
    }

    // Achievements for user
    engagement.achievements.push(
      `You're tracking ${masterData.symbol} - Top 10 crypto!`,
      `Smart trader: Checking all indicators before decision`
    );

    return engagement;
  }

  /**
   * Setup triggers based on historical data
   */
  async setupTriggers(symbol, masterData) {
    const triggers = {
      active: [],
      pending: [],
      historical: [],
      alerts: []
    };

    // Price triggers from support/resistance
    masterData.history.historicalSupport.forEach(level => {
      triggers.pending.push({
        type: 'price_support',
        level,
        condition: 'cross_below',
        message: `${symbol} approaching support at $${level}`
      });
    });

    masterData.history.historicalResistance.forEach(level => {
      triggers.pending.push({
        type: 'price_resistance',
        level,
        condition: 'cross_above',
        message: `${symbol} approaching resistance at $${level}`
      });
    });

    // Indicator triggers
    if (masterData.indicators.rsi.value > 70) {
      triggers.active.push({
        type: 'rsi_overbought',
        value: masterData.indicators.rsi.value,
        message: `${symbol} RSI overbought at ${masterData.indicators.rsi.value}`
      });
    }

    // Whale triggers
    if (masterData.whales.alerts.length > 0) {
      triggers.alerts.push(...masterData.whales.alerts);
    }

    return triggers;
  }

  /**
   * Generate liquidation clusters
   */
  generateLiquidationClusters(currentPrice) {
    const clusters = [];
    const levels = [0.95, 0.93, 0.90, 1.05, 1.07, 1.10];

    levels.forEach(multiplier => {
      clusters.push({
        price: currentPrice * multiplier,
        volume: Math.random() * 10000000,
        side: multiplier < 1 ? 'long' : 'short'
      });
    });

    return clusters.sort((a, b) => b.volume - a.volume);
  }

  /**
   * Get RSI interpretation
   */
  getRSIInterpretation(rsi) {
    if (rsi > 70) return 'Overbought - Potential pullback';
    if (rsi < 30) return 'Oversold - Potential bounce';
    if (rsi > 60) return 'Bullish momentum';
    if (rsi < 40) return 'Bearish momentum';
    return 'Neutral';
  }

  /**
   * Start update cycles
   */
  startUpdateCycles() {
    // Real-time updates (prices)
    setInterval(() => this.updateRealtimeData(), this.updateIntervals.realtime);

    // Fast updates (indicators)
    setInterval(() => this.updateFastData(), this.updateIntervals.fast);

    // Medium updates (patterns)
    setInterval(() => this.updateMediumData(), this.updateIntervals.medium);

    // Slow updates (on-chain)
    setInterval(() => this.updateSlowData(), this.updateIntervals.slow);

    // Daily updates (intelligence)
    setInterval(() => this.updateDailyData(), this.updateIntervals.daily);
  }

  /**
   * Store symbol knowledge in database
   */
  async storeSymbolKnowledge(symbol, masterData) {
    try {
      // Store main data
      await this.supabase.from('symbol_knowledge').upsert({
        symbol,
        data: masterData,
        updated_at: new Date().toISOString()
      });

      // Store as knowledge item for brain
      await this.supabase.from('brain_knowledge').insert({
        title: `${symbol} Master Data`,
        content: JSON.stringify(masterData, null, 2),
        category_id: await this.getSymbolCategoryId(),
        knowledge_type: 'symbol_data',
        source_type: 'aggregation',
        confidence_score: 1.0,
        keywords: [symbol, 'market', 'trading', 'analysis'],
        tags: ['symbol', symbol.toLowerCase()]
      });

    } catch (error) {
      console.error('Failed to store symbol knowledge:', error);
    }
  }

  /**
   * Get symbol data for response
   */
  async getSymbolResponse(symbol, focus = 'all') {
    const masterData = await this.getSymbolMasterData(symbol);

    // Format response based on focus
    if (focus === 'price') {
      return this.formatPriceResponse(masterData);
    } else if (focus === 'trading') {
      return this.formatTradingResponse(masterData);
    } else if (focus === 'risk') {
      return this.formatRiskResponse(masterData);
    } else if (focus === 'whales') {
      return this.formatWhaleResponse(masterData);
    } else {
      return this.formatCompleteResponse(masterData);
    }
  }

  /**
   * Format complete response for Zmarty
   */
  formatCompleteResponse(data) {
    return {
      quick: {
        price: data.market.price,
        change: data.market.change24h,
        odds: data.probabilities?.oddsInFavor,
        risk: data.aiInsights.riskAssessment
      },
      detailed: data,
      summary: `${data.symbol} is at $${data.market.price} (${data.market.change24h > 0 ? '+' : ''}${data.market.change24h}%). Odds: ${data.probabilities?.interpretation?.action || 'Calculating'}. Risk: ${data.aiInsights?.riskAssessment?.level || 'Assessing'}.`,
      engagement: data.engagement
    };
  }
}

// Export singleton instance
const symbolMasterBrain = new SymbolMasterBrain();
export default symbolMasterBrain;