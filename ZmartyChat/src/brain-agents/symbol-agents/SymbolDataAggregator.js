/**
 * Symbol Data Aggregator
 * Collects and aggregates market data for cryptocurrency symbols
 */

import config from '../../config/secure-config.js';

export default class SymbolDataAggregator {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute cache
    this.supportedSymbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'MATIC', 'LINK'];
  }

  /**
   * Get current price data for a symbol
   */
  async getCurrentPrice(symbol) {
    const cacheKey = `price_${symbol}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    try {
      // Mock data for testing - replace with real API call
      const mockPrice = {
        symbol: symbol,
        price: this.generateMockPrice(symbol),
        change24h: (Math.random() - 0.5) * 10,
        volume24h: Math.random() * 1000000000,
        timestamp: Date.now()
      };

      this.cache.set(cacheKey, {
        data: mockPrice,
        timestamp: Date.now()
      });

      return mockPrice;
    } catch (error) {
      console.error(`Error fetching price for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Get historical data for pattern analysis
   */
  async getHistoricalData(symbol, timeframe = '1d', limit = 100) {
    const cacheKey = `historical_${symbol}_${timeframe}_${limit}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheTimeout * 5) {
      return cached.data;
    }

    try {
      // Mock historical data for testing
      const data = this.generateMockHistoricalData(symbol, timeframe, limit);

      this.cache.set(cacheKey, {
        data: data,
        timestamp: Date.now()
      });

      return data;
    } catch (error) {
      console.error(`Error fetching historical data for ${symbol}:`, error);
      return [];
    }
  }

  /**
   * Get market data for multiple symbols
   */
  async getMarketData(symbols = this.supportedSymbols) {
    const promises = symbols.map(symbol => this.getCurrentPrice(symbol));
    const results = await Promise.allSettled(promises);

    return results
      .filter(result => result.status === 'fulfilled' && result.value)
      .map(result => result.value);
  }

  /**
   * Check if symbol is supported
   */
  isSymbolSupported(symbol) {
    return this.supportedSymbols.includes(symbol.toUpperCase());
  }

  /**
   * Add new symbol to supported list
   */
  addSymbol(symbol) {
    const upperSymbol = symbol.toUpperCase();
    if (!this.supportedSymbols.includes(upperSymbol)) {
      this.supportedSymbols.push(upperSymbol);
    }
  }

  /**
   * Generate mock price data for testing
   */
  generateMockPrice(symbol) {
    const basePrices = {
      'BTC': 45000,
      'ETH': 3000,
      'BNB': 400,
      'ADA': 0.5,
      'SOL': 100,
      'DOT': 25,
      'MATIC': 1.2,
      'LINK': 15
    };

    const basePrice = basePrices[symbol] || 100;
    const variance = 0.05; // 5% variance
    const randomFactor = 1 + (Math.random() - 0.5) * variance * 2;

    return Math.round(basePrice * randomFactor * 100) / 100;
  }

  /**
   * Generate mock historical data for testing
   */
  generateMockHistoricalData(symbol, timeframe, limit) {
    const data = [];
    const currentPrice = this.generateMockPrice(symbol);
    let timestamp = Date.now();

    // Calculate time intervals based on timeframe
    const intervals = {
      '1h': 60 * 60 * 1000,
      '4h': 4 * 60 * 60 * 1000,
      '1d': 24 * 60 * 60 * 1000,
      '1w': 7 * 24 * 60 * 60 * 1000
    };

    const interval = intervals[timeframe] || intervals['1d'];

    for (let i = limit - 1; i >= 0; i--) {
      const variance = 0.02; // 2% variance per period
      const randomFactor = 1 + (Math.random() - 0.5) * variance * 2;
      const price = Math.round(currentPrice * randomFactor * 100) / 100;

      data.push({
        timestamp: timestamp - (i * interval),
        open: price * 0.99,
        high: price * 1.02,
        low: price * 0.98,
        close: price,
        volume: Math.random() * 1000000
      });
    }

    return data;
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}