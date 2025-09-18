/**
 * Market Data Collector
 * Collects real-time and historical market data from multiple sources
 */

import axios from 'axios';
import config from '../../config/secure-config.js';

export default class MarketDataCollector {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 30000; // 30 seconds for real-time data
    this.isInitialized = false;

    // Exchange APIs configuration
    this.exchanges = {
      binance: {
        baseUrl: 'https://api.binance.com/api/v3',
        endpoints: {
          ticker: '/ticker/24hr',
          klines: '/klines',
          depth: '/depth'
        }
      },
      kucoin: {
        baseUrl: 'https://api.kucoin.com/api/v1',
        endpoints: {
          ticker: '/market/stats',
          klines: '/market/candles',
          depth: '/market/orderbook/level2_20'
        }
      }
    };

    this.timeframeMap = {
      '1m': '1m',
      '5m': '5m',
      '15m': '15m',
      '1h': '1h',
      '4h': '4h',
      '1d': '1d',
      '1w': '1w'
    };
  }

  /**
   * Initialize the market data collector
   */
  async initialize() {
    console.log('📊 Initializing Market Data Collector...');

    try {
      // Test connection to primary exchange
      await this.testConnection();
      this.isInitialized = true;
      console.log('✅ Market Data Collector initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Market Data Collector:', error.message);
      this.isInitialized = false;
    }
  }

  /**
   * Test connection to exchanges
   */
  async testConnection() {
    try {
      const response = await axios.get(`${this.exchanges.binance.baseUrl}/ping`, {
        timeout: 5000
      });
      return true;
    } catch (error) {
      throw new Error('Cannot connect to exchange APIs');
    }
  }

  /**
   * Get current market data for a symbol
   */
  async getCurrentMarketData(symbol) {
    const cacheKey = `market_${symbol}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    try {
      const marketData = {
        symbol,
        exchanges: {},
        aggregated: {
          price: null,
          volume24h: null,
          change24h: null,
          high24h: null,
          low24h: null,
          bid: null,
          ask: null,
          spread: null
        },
        timestamp: Date.now()
      };

      // Fetch from Binance
      try {
        const binanceData = await this.fetchBinanceData(symbol);
        if (binanceData) {
          marketData.exchanges.binance = binanceData;
          marketData.aggregated = { ...marketData.aggregated, ...binanceData };
        }
      } catch (error) {
        console.warn(`Binance data failed for ${symbol}:`, error.message);
      }

      // Fetch from KuCoin
      try {
        const kucoinData = await this.fetchKucoinData(symbol);
        if (kucoinData) {
          marketData.exchanges.kucoin = kucoinData;

          // Aggregate prices if we have multiple sources
          if (marketData.aggregated.price && kucoinData.price) {
            marketData.aggregated.price = (marketData.aggregated.price + kucoinData.price) / 2;
          } else if (kucoinData.price) {
            marketData.aggregated = { ...marketData.aggregated, ...kucoinData };
          }
        }
      } catch (error) {
        console.warn(`KuCoin data failed for ${symbol}:`, error.message);
      }

      // Calculate spread if we have bid/ask
      if (marketData.aggregated.bid && marketData.aggregated.ask) {
        marketData.aggregated.spread = (
          (marketData.aggregated.ask - marketData.aggregated.bid) /
          marketData.aggregated.price * 100
        ).toFixed(3);
      }

      this.cache.set(cacheKey, {
        data: marketData,
        timestamp: Date.now()
      });

      return marketData;

    } catch (error) {
      console.error(`Error fetching market data for ${symbol}:`, error);
      return this.getMockMarketData(symbol);
    }
  }

  /**
   * Fetch data from Binance
   */
  async fetchBinanceData(symbol) {
    const binanceSymbol = `${symbol}USDT`;

    const response = await axios.get(
      `${this.exchanges.binance.baseUrl}${this.exchanges.binance.endpoints.ticker}`,
      {
        params: { symbol: binanceSymbol },
        timeout: 5000
      }
    );

    if (response.data) {
      return {
        price: parseFloat(response.data.lastPrice),
        volume24h: parseFloat(response.data.volume),
        change24h: parseFloat(response.data.priceChangePercent),
        high24h: parseFloat(response.data.highPrice),
        low24h: parseFloat(response.data.lowPrice),
        bid: parseFloat(response.data.bidPrice),
        ask: parseFloat(response.data.askPrice)
      };
    }

    return null;
  }

  /**
   * Fetch data from KuCoin
   */
  async fetchKucoinData(symbol) {
    const kucoinSymbol = `${symbol}-USDT`;

    try {
      const response = await axios.get(
        `${this.exchanges.kucoin.baseUrl}${this.exchanges.kucoin.endpoints.ticker}`,
        {
          params: { symbol: kucoinSymbol },
          timeout: 5000
        }
      );

      if (response.data && response.data.data) {
        const data = response.data.data;
        return {
          price: parseFloat(data.last),
          volume24h: parseFloat(data.vol),
          change24h: parseFloat(data.changeRate) * 100,
          high24h: parseFloat(data.high),
          low24h: parseFloat(data.low),
          bid: parseFloat(data.buy),
          ask: parseFloat(data.sell)
        };
      }
    } catch (error) {
      // KuCoin might not have all symbols
      return null;
    }

    return null;
  }

  /**
   * Get historical candlestick data
   */
  async getHistoricalData(symbol, timeframe = '1d', limit = 100) {
    const cacheKey = `historical_${symbol}_${timeframe}_${limit}`;
    const cached = this.cache.get(cacheKey);

    // Cache historical data longer (5 minutes)
    if (cached && Date.now() - cached.timestamp < 300000) {
      return cached.data;
    }

    try {
      const historicalData = await this.fetchBinanceKlines(symbol, timeframe, limit);

      if (historicalData) {
        this.cache.set(cacheKey, {
          data: historicalData,
          timestamp: Date.now()
        });

        return historicalData;
      }

      // Fallback to mock data
      return this.getMockHistoricalData(symbol, timeframe, limit);

    } catch (error) {
      console.error(`Error fetching historical data for ${symbol}:`, error);
      return this.getMockHistoricalData(symbol, timeframe, limit);
    }
  }

  /**
   * Fetch klines data from Binance
   */
  async fetchBinanceKlines(symbol, timeframe, limit) {
    const binanceSymbol = `${symbol}USDT`;
    const interval = this.timeframeMap[timeframe] || '1d';

    const response = await axios.get(
      `${this.exchanges.binance.baseUrl}${this.exchanges.binance.endpoints.klines}`,
      {
        params: {
          symbol: binanceSymbol,
          interval: interval,
          limit: limit
        },
        timeout: 10000
      }
    );

    if (response.data) {
      return response.data.map(kline => ({
        timestamp: kline[0],
        open: parseFloat(kline[1]),
        high: parseFloat(kline[2]),
        low: parseFloat(kline[3]),
        close: parseFloat(kline[4]),
        volume: parseFloat(kline[5])
      }));
    }

    return null;
  }

  /**
   * Get order book data
   */
  async getOrderBookData(symbol, depth = 20) {
    const cacheKey = `orderbook_${symbol}_${depth}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < 10000) { // 10 second cache
      return cached.data;
    }

    try {
      const binanceSymbol = `${symbol}USDT`;

      const response = await axios.get(
        `${this.exchanges.binance.baseUrl}${this.exchanges.binance.endpoints.depth}`,
        {
          params: {
            symbol: binanceSymbol,
            limit: depth
          },
          timeout: 5000
        }
      );

      if (response.data) {
        const orderBookData = {
          symbol,
          bids: response.data.bids.map(bid => ({
            price: parseFloat(bid[0]),
            quantity: parseFloat(bid[1])
          })),
          asks: response.data.asks.map(ask => ({
            price: parseFloat(ask[0]),
            quantity: parseFloat(ask[1])
          })),
          timestamp: Date.now()
        };

        this.cache.set(cacheKey, {
          data: orderBookData,
          timestamp: Date.now()
        });

        return orderBookData;
      }

    } catch (error) {
      console.error(`Error fetching order book for ${symbol}:`, error);
    }

    return this.getMockOrderBookData(symbol);
  }

  /**
   * Get volume profile data
   */
  async getVolumeProfile(symbol, timeframe = '1d', periods = 30) {
    try {
      const historicalData = await this.getHistoricalData(symbol, timeframe, periods);

      if (!historicalData || historicalData.length === 0) {
        return null;
      }

      // Calculate volume profile
      const priceRanges = new Map();
      const minPrice = Math.min(...historicalData.map(d => d.low));
      const maxPrice = Math.max(...historicalData.map(d => d.high));
      const priceStep = (maxPrice - minPrice) / 20; // 20 price levels

      // Initialize price ranges
      for (let i = 0; i < 20; i++) {
        const price = minPrice + (i * priceStep);
        priceRanges.set(price.toFixed(2), 0);
      }

      // Distribute volume across price ranges
      historicalData.forEach(candle => {
        const avgPrice = (candle.high + candle.low + candle.close) / 3;
        const closestRange = this.findClosestPriceRange(avgPrice, priceRanges);
        if (closestRange) {
          priceRanges.set(closestRange, priceRanges.get(closestRange) + candle.volume);
        }
      });

      // Convert to array and sort by volume
      const volumeProfile = Array.from(priceRanges.entries())
        .map(([price, volume]) => ({
          price: parseFloat(price),
          volume: volume
        }))
        .sort((a, b) => b.volume - a.volume);

      return {
        symbol,
        timeframe,
        profile: volumeProfile,
        poc: volumeProfile[0], // Point of Control (highest volume)
        timestamp: Date.now()
      };

    } catch (error) {
      console.error(`Error calculating volume profile for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Find closest price range for volume distribution
   */
  findClosestPriceRange(price, priceRanges) {
    let closest = null;
    let minDiff = Infinity;

    for (const rangePrice of priceRanges.keys()) {
      const diff = Math.abs(parseFloat(rangePrice) - price);
      if (diff < minDiff) {
        minDiff = diff;
        closest = rangePrice;
      }
    }

    return closest;
  }

  /**
   * Get multiple symbols data at once
   */
  async getMultiSymbolData(symbols) {
    const promises = symbols.map(symbol => this.getCurrentMarketData(symbol));
    const results = await Promise.allSettled(promises);

    return results
      .filter(result => result.status === 'fulfilled')
      .map(result => result.value);
  }

  /**
   * Generate mock market data for testing
   */
  getMockMarketData(symbol) {
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
    const price = basePrice * (1 + (Math.random() - 0.5) * 0.02);
    const change24h = (Math.random() - 0.5) * 10;

    return {
      symbol,
      exchanges: {
        mock: {
          price,
          volume24h: Math.random() * 1000000000,
          change24h,
          high24h: price * 1.05,
          low24h: price * 0.95,
          bid: price * 0.999,
          ask: price * 1.001
        }
      },
      aggregated: {
        price,
        volume24h: Math.random() * 1000000000,
        change24h,
        high24h: price * 1.05,
        low24h: price * 0.95,
        bid: price * 0.999,
        ask: price * 1.001,
        spread: '0.002'
      },
      timestamp: Date.now()
    };
  }

  /**
   * Generate mock historical data
   */
  getMockHistoricalData(symbol, timeframe, limit) {
    const data = [];
    const basePrice = this.getMockMarketData(symbol).aggregated.price;
    let currentPrice = basePrice;
    const now = Date.now();

    // Calculate time intervals
    const intervals = {
      '1m': 60 * 1000,
      '5m': 5 * 60 * 1000,
      '15m': 15 * 60 * 1000,
      '1h': 60 * 60 * 1000,
      '4h': 4 * 60 * 60 * 1000,
      '1d': 24 * 60 * 60 * 1000,
      '1w': 7 * 24 * 60 * 60 * 1000
    };

    const interval = intervals[timeframe] || intervals['1d'];

    for (let i = limit - 1; i >= 0; i--) {
      const timestamp = now - (i * interval);
      const volatility = 0.02; // 2% volatility per period
      const change = (Math.random() - 0.5) * volatility;

      const open = currentPrice;
      const close = currentPrice * (1 + change);
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (1 - Math.random() * 0.01);
      const volume = Math.random() * 1000000;

      data.push({
        timestamp,
        open,
        high,
        low,
        close,
        volume
      });

      currentPrice = close;
    }

    return data;
  }

  /**
   * Generate mock order book data
   */
  getMockOrderBookData(symbol) {
    const marketData = this.getMockMarketData(symbol);
    const currentPrice = marketData.aggregated.price;

    const bids = [];
    const asks = [];

    // Generate 10 bid levels
    for (let i = 1; i <= 10; i++) {
      bids.push({
        price: currentPrice * (1 - (i * 0.001)),
        quantity: Math.random() * 100
      });
    }

    // Generate 10 ask levels
    for (let i = 1; i <= 10; i++) {
      asks.push({
        price: currentPrice * (1 + (i * 0.001)),
        quantity: Math.random() * 100
      });
    }

    return {
      symbol,
      bids: bids.sort((a, b) => b.price - a.price),
      asks: asks.sort((a, b) => a.price - b.price),
      timestamp: Date.now()
    };
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

  /**
   * Health check
   */
  async healthCheck() {
    if (!this.isInitialized) {
      return { status: 'unhealthy', message: 'Not initialized' };
    }

    try {
      await this.testConnection();
      return {
        status: 'healthy',
        cache: this.getCacheStats(),
        initialized: this.isInitialized
      };
    } catch (error) {
      return {
        status: 'degraded',
        message: 'Connection issues',
        error: error.message
      };
    }
  }
}