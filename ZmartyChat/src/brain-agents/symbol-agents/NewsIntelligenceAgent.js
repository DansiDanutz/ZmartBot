/**
 * NEWS INTELLIGENCE AGENT
 * Fetches and analyzes crypto news from multiple sources
 */

class NewsIntelligenceAgent {
  constructor() {
    this.name = 'NewsIntelligenceAgent';
    this.sources = {
      cryptopanic: 'https://cryptopanic.com/api/v1',
      coindesk: 'https://www.coindesk.com/api',
      cointelegraph: 'https://cointelegraph.com/api',
      decrypt: 'https://decrypt.co/api',
      theblock: 'https://api.theblock.co'
    };
    this.sentimentKeywords = {
      bullish: ['bullish', 'moon', 'pump', 'rally', 'surge', 'breakthrough', 'adoption', 'partnership'],
      bearish: ['bearish', 'crash', 'dump', 'decline', 'fear', 'regulation', 'ban', 'hack'],
      neutral: ['analysis', 'report', 'update', 'announcement', 'launch', 'development']
    };
    this.newsCache = new Map();
  }

  /**
   * Initialize the news intelligence agent
   */
  async initialize() {
    console.log('=ð Initializing News Intelligence Agent...');

    // Setup news monitoring
    this.setupNewsMonitoring();

    // Initialize sentiment analysis
    this.initializeSentimentAnalysis();

    console.log(' News Intelligence Agent initialized');
  }

  /**
   * Fetch latest news for a symbol
   * Called by SymbolMasterBrain.fetchNews()
   */
  async fetchLatest(symbol) {
    try {
      console.log(`=ð Fetching latest news for ${symbol}...`);

      // Check cache first
      const cacheKey = `news_${symbol}`;
      if (this.newsCache.has(cacheKey)) {
        const cached = this.newsCache.get(cacheKey);
        if (Date.now() - cached.timestamp < 300000) { // 5 minutes
          return cached.data;
        }
      }

      const newsData = {
        latest: await this.fetchNewsArticles(symbol),
        sentiment: await this.analyzeSentiment(symbol),
        events: await this.fetchUpcomingEvents(symbol),
        social: await this.fetchSocialMetrics(symbol)
      };

      // Cache the results
      this.newsCache.set(cacheKey, {
        data: newsData,
        timestamp: Date.now()
      });

      return newsData;

    } catch (error) {
      console.error(`Failed to fetch news for ${symbol}:`, error.message);
      return this.getEmptyNewsData();
    }
  }

  /**
   * Setup news monitoring infrastructure
   */
  setupNewsMonitoring() {
    // Setup source monitoring
    this.setupSourceMonitoring();

    // Setup keyword tracking
    this.setupKeywordTracking();

    // Setup sentiment tracking
    this.setupSentimentTracking();
  }

  /**
   * Setup source monitoring for different news outlets
   */
  setupSourceMonitoring() {
    this.sourceWeights = {
      cryptopanic: 0.8,    // Aggregator
      coindesk: 0.9,       // High credibility
      cointelegraph: 0.7,  // Popular but sometimes clickbait
      decrypt: 0.8,        // Good analysis
      theblock: 0.9        // Professional
    };
  }

  /**
   * Setup keyword tracking for different symbols
   */
  setupKeywordTracking() {
    this.symbolKeywords = {
      'BTC': ['bitcoin', 'btc', 'satoshi', 'digital gold'],
      'ETH': ['ethereum', 'eth', 'vitalik', 'smart contracts', 'defi'],
      'SOL': ['solana', 'sol', 'anatoly', 'proof of stake'],
      'BNB': ['binance', 'bnb', 'cz', 'bsc'],
      'MATIC': ['polygon', 'matic', 'scaling', 'layer 2']
    };
  }

  /**
   * Setup sentiment tracking
   */
  setupSentimentTracking() {
    this.sentimentWeights = {
      title: 0.4,      // Title sentiment is important
      content: 0.5,    // Content sentiment
      source: 0.1      // Source bias
    };
  }

  /**
   * Initialize sentiment analysis
   */
  initializeSentimentAnalysis() {
    // Simple keyword-based sentiment analysis
    this.sentimentAnalyzer = {
      analyze: (text) => this.analyzeSentimentText(text),
      getScore: (text) => this.getSentimentScore(text)
    };
  }

  /**
   * Fetch news articles for a symbol
   */
  async fetchNewsArticles(symbol) {
    const articles = [];

    // Generate mock news articles
    const mockArticles = this.generateMockArticles(symbol);
    articles.push(...mockArticles);

    // Sort by publication date
    return articles.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  }

  /**
   * Generate mock news articles
   */
  generateMockArticles(symbol) {
    const articles = [];
    const articleCount = 8 + Math.floor(Math.random() * 12); // 8-20 articles

    const headlines = this.generateHeadlines(symbol);
    const sources = Object.keys(this.sources);

    for (let i = 0; i < articleCount; i++) {
      const source = sources[Math.floor(Math.random() * sources.length)];
      const headline = headlines[Math.floor(Math.random() * headlines.length)];
      const sentiment = this.analyzeSentimentText(headline);

      articles.push({
        id: `article_${symbol}_${Date.now()}_${i}`,
        title: headline,
        summary: this.generateArticleSummary(headline, symbol),
        url: `https://${source}.com/article-${i}`,
        source: source,
        author: this.generateAuthorName(),
        publishedAt: new Date(Date.now() - (i * 3600000)).toISOString(), // Every hour
        sentiment: sentiment,
        relevanceScore: 0.7 + (Math.random() * 0.3), // 70-100%
        impactScore: Math.random(),
        keywords: this.extractKeywords(headline, symbol),
        category: this.categorizeArticle(headline)
      });
    }

    return articles;
  }

  /**
   * Generate headlines for a symbol
   */
  generateHeadlines(symbol) {
    const symbolName = this.getSymbolFullName(symbol);

    return [
      `${symbolName} Breaks Key Resistance Level in Strong Rally`,
      `Institutional Adoption Drives ${symbolName} to New Highs`,
      `${symbolName} Shows Bullish Momentum Amid Market Uncertainty`,
      `Analysts Predict Strong Performance for ${symbolName}`,
      `${symbolName} Technical Analysis: What's Next?`,
      `Major Partnership Announcement Boosts ${symbolName}`,
      `${symbolName} Trading Volume Surges 300% in 24 Hours`,
      `Whale Activity Detected in ${symbolName} Markets`,
      `${symbolName} Developer Activity Reaches All-Time High`,
      `Market Update: ${symbolName} Leads Crypto Recovery`,
      `${symbolName} Price Analysis: Support and Resistance Levels`,
      `Breaking: Major Exchange Lists ${symbolName} Derivatives`,
      `${symbolName} Network Upgrade Scheduled for Next Month`,
      `Regulatory Clarity Brings Optimism to ${symbolName}`,
      `${symbolName} DeFi Integration Expands Use Cases`
    ];
  }

  /**
   * Get full name for symbol
   */
  getSymbolFullName(symbol) {
    const names = {
      'BTC': 'Bitcoin',
      'ETH': 'Ethereum',
      'SOL': 'Solana',
      'BNB': 'Binance Coin',
      'MATIC': 'Polygon'
    };
    return names[symbol] || symbol;
  }

  /**
   * Generate article summary
   */
  generateArticleSummary(headline, symbol) {
    const summaries = [
      `Market analysis reveals strong momentum for ${symbol} as institutional interest continues to grow.`,
      `Technical indicators suggest ${symbol} is positioning for a significant move in the coming days.`,
      `Recent developments in the ${symbol} ecosystem are driving increased adoption and trading volume.`,
      `Experts weigh in on ${symbol}'s recent price action and what it means for long-term investors.`,
      `On-chain metrics show growing activity in the ${symbol} network, signaling healthy ecosystem development.`
    ];

    return summaries[Math.floor(Math.random() * summaries.length)];
  }

  /**
   * Generate author name
   */
  generateAuthorName() {
    const firstNames = ['Alex', 'Sarah', 'Michael', 'Jessica', 'David', 'Emily', 'James', 'Lisa'];
    const lastNames = ['Chen', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 'Garcia'];

    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];

    return `${firstName} ${lastName}`;
  }

  /**
   * Extract keywords from headline
   */
  extractKeywords(headline, symbol) {
    const keywords = [symbol.toLowerCase()];
    const symbolKeywords = this.symbolKeywords[symbol] || [];

    // Add symbol-specific keywords
    symbolKeywords.forEach(keyword => {
      if (headline.toLowerCase().includes(keyword)) {
        keywords.push(keyword);
      }
    });

    // Add general keywords
    const generalKeywords = ['trading', 'price', 'market', 'analysis', 'bullish', 'bearish'];
    generalKeywords.forEach(keyword => {
      if (headline.toLowerCase().includes(keyword)) {
        keywords.push(keyword);
      }
    });

    return [...new Set(keywords)]; // Remove duplicates
  }

  /**
   * Categorize article based on headline
   */
  categorizeArticle(headline) {
    const categories = {
      'price_analysis': ['analysis', 'technical', 'price', 'support', 'resistance'],
      'market_news': ['market', 'trading', 'volume', 'rally', 'crash'],
      'development': ['development', 'upgrade', 'network', 'protocol'],
      'adoption': ['adoption', 'partnership', 'institutional', 'integration'],
      'regulation': ['regulation', 'regulatory', 'legal', 'compliance']
    };

    const lowerHeadline = headline.toLowerCase();

    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => lowerHeadline.includes(keyword))) {
        return category;
      }
    }

    return 'general';
  }

  /**
   * Analyze sentiment for a symbol
   */
  async analyzeSentiment(symbol) {
    // Get recent articles for sentiment analysis
    const articles = await this.fetchNewsArticles(symbol);

    let totalSentiment = 0;
    let sentimentCount = 0;
    const sentimentSources = {};

    articles.forEach(article => {
      const sentiment = this.analyzeSentimentText(article.title + ' ' + article.summary);
      totalSentiment += sentiment.score;
      sentimentCount++;

      // Track sentiment by source
      if (!sentimentSources[article.source]) {
        sentimentSources[article.source] = { score: 0, count: 0 };
      }
      sentimentSources[article.source].score += sentiment.score;
      sentimentSources[article.source].count++;
    });

    // Calculate average sentiment
    const averageSentiment = sentimentCount > 0 ? totalSentiment / sentimentCount : 0;

    // Calculate trend (compare with previous sentiment)
    const trend = this.calculateSentimentTrend(symbol, averageSentiment);

    return {
      score: averageSentiment,
      trend: trend,
      sources: sentimentSources,
      confidence: this.calculateSentimentConfidence(sentimentCount),
      distribution: this.calculateSentimentDistribution(articles)
    };
  }

  /**
   * Analyze sentiment of text
   */
  analyzeSentimentText(text) {
    const lowerText = text.toLowerCase();
    let score = 0;
    let positiveCount = 0;
    let negativeCount = 0;

    // Count bullish keywords
    this.sentimentKeywords.bullish.forEach(keyword => {
      if (lowerText.includes(keyword)) {
        score += 0.1;
        positiveCount++;
      }
    });

    // Count bearish keywords
    this.sentimentKeywords.bearish.forEach(keyword => {
      if (lowerText.includes(keyword)) {
        score -= 0.1;
        negativeCount++;
      }
    });

    // Normalize score between -1 and 1
    score = Math.max(-1, Math.min(1, score));

    return {
      score: score,
      label: this.getSentimentLabel(score),
      positiveSignals: positiveCount,
      negativeSignals: negativeCount
    };
  }

  /**
   * Get sentiment score (simplified version)
   */
  getSentimentScore(text) {
    return this.analyzeSentimentText(text).score;
  }

  /**
   * Get sentiment label
   */
  getSentimentLabel(score) {
    if (score > 0.2) return 'bullish';
    if (score < -0.2) return 'bearish';
    return 'neutral';
  }

  /**
   * Calculate sentiment trend
   */
  calculateSentimentTrend(symbol, currentSentiment) {
    // Mock trend calculation (in real implementation, compare with historical data)
    const previousSentiment = Math.random() * 2 - 1; // -1 to 1
    const change = currentSentiment - previousSentiment;

    if (change > 0.1) return 'improving';
    if (change < -0.1) return 'declining';
    return 'stable';
  }

  /**
   * Calculate sentiment confidence
   */
  calculateSentimentConfidence(articleCount) {
    // More articles = higher confidence
    if (articleCount >= 20) return 0.95;
    if (articleCount >= 10) return 0.85;
    if (articleCount >= 5) return 0.75;
    return 0.60;
  }

  /**
   * Calculate sentiment distribution
   */
  calculateSentimentDistribution(articles) {
    let bullish = 0;
    let bearish = 0;
    let neutral = 0;

    articles.forEach(article => {
      const sentiment = article.sentiment;
      if (sentiment.score > 0.2) bullish++;
      else if (sentiment.score < -0.2) bearish++;
      else neutral++;
    });

    const total = articles.length || 1;

    return {
      bullish: bullish / total,
      bearish: bearish / total,
      neutral: neutral / total
    };
  }

  /**
   * Fetch upcoming events
   */
  async fetchUpcomingEvents(symbol) {
    // Generate mock events
    return this.generateMockEvents(symbol);
  }

  /**
   * Generate mock events
   */
  generateMockEvents(symbol) {
    const events = [];
    const eventTypes = ['conference', 'upgrade', 'partnership', 'listing', 'earnings'];
    const eventCount = Math.floor(Math.random() * 5) + 1; // 1-5 events

    for (let i = 0; i < eventCount; i++) {
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const futureDate = new Date(Date.now() + (i + 1) * 86400000 * 7); // Weekly events

      events.push({
        id: `event_${symbol}_${i}`,
        title: this.generateEventTitle(symbol, eventType),
        type: eventType,
        date: futureDate.toISOString(),
        description: this.generateEventDescription(symbol, eventType),
        importance: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
        confirmed: Math.random() > 0.3 // 70% confirmed
      });
    }

    return events;
  }

  /**
   * Generate event title
   */
  generateEventTitle(symbol, type) {
    const symbolName = this.getSymbolFullName(symbol);

    const titles = {
      conference: `${symbolName} Developer Conference 2024`,
      upgrade: `${symbolName} Network Upgrade v2.0`,
      partnership: `${symbolName} Strategic Partnership Announcement`,
      listing: `${symbolName} Listing on Major Exchange`,
      earnings: `${symbolName} Foundation Quarterly Report`
    };

    return titles[type] || `${symbolName} Event`;
  }

  /**
   * Generate event description
   */
  generateEventDescription(symbol, type) {
    const descriptions = {
      conference: 'Annual developer conference featuring the latest updates and roadmap.',
      upgrade: 'Major network upgrade introducing new features and improvements.',
      partnership: 'Strategic partnership announcement with industry leader.',
      listing: 'New exchange listing expanding trading accessibility.',
      earnings: 'Quarterly financial and development progress report.'
    };

    return descriptions[type] || 'Important event for the ecosystem.';
  }

  /**
   * Fetch social metrics
   */
  async fetchSocialMetrics(symbol) {
    return {
      twitter: this.generateTwitterMetrics(symbol),
      reddit: this.generateRedditMetrics(symbol),
      telegram: this.generateTelegramMetrics(symbol)
    };
  }

  /**
   * Generate Twitter metrics
   */
  generateTwitterMetrics(symbol) {
    return {
      mentions: 1000 + Math.floor(Math.random() * 5000),
      sentiment: Math.random() * 2 - 1, // -1 to 1
      trending: Math.random() > 0.8, // 20% chance of trending
      influencerMentions: Math.floor(Math.random() * 10),
      reach: 100000 + Math.floor(Math.random() * 900000)
    };
  }

  /**
   * Generate Reddit metrics
   */
  generateRedditMetrics(symbol) {
    return {
      posts: 50 + Math.floor(Math.random() * 200),
      comments: 500 + Math.floor(Math.random() * 2000),
      upvotes: 1000 + Math.floor(Math.random() * 5000),
      sentiment: Math.random() * 2 - 1,
      hotTopics: this.generateHotTopics(symbol)
    };
  }

  /**
   * Generate Telegram metrics
   */
  generateTelegramMetrics(symbol) {
    return {
      messages: 200 + Math.floor(Math.random() * 800),
      activeUsers: 1000 + Math.floor(Math.random() * 5000),
      sentiment: Math.random() * 2 - 1,
      channels: 5 + Math.floor(Math.random() * 15)
    };
  }

  /**
   * Generate hot topics for Reddit
   */
  generateHotTopics(symbol) {
    const topics = [
      `${symbol} price prediction`,
      `${symbol} technical analysis`,
      `${symbol} news discussion`,
      `${symbol} trading strategies`,
      `${symbol} holder meetup`
    ];

    return topics.slice(0, 2 + Math.floor(Math.random() * 3)); // 2-4 topics
  }

  /**
   * Get empty news data structure
   */
  getEmptyNewsData() {
    return {
      latest: [],
      sentiment: {
        score: 0,
        trend: 'stable',
        sources: {},
        confidence: 0,
        distribution: { bullish: 0, bearish: 0, neutral: 1 }
      },
      events: [],
      social: {
        twitter: null,
        reddit: null,
        telegram: null
      }
    };
  }

  /**
   * Get news summary for a symbol
   */
  getNewsSummary(newsData) {
    return {
      articlesCount: newsData.latest.length,
      sentimentScore: newsData.sentiment.score,
      sentimentLabel: this.getSentimentLabel(newsData.sentiment.score),
      upcomingEvents: newsData.events.length,
      socialActivity: {
        twitter: newsData.social.twitter?.mentions || 0,
        reddit: newsData.social.reddit?.posts || 0,
        telegram: newsData.social.telegram?.messages || 0
      }
    };
  }
}

export default NewsIntelligenceAgent;