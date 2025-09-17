import BinanceService, { BinanceTicker } from './BinanceService';
import KuCoinService, { KuCoinTicker } from './KuCoinService';

export interface UnifiedMarketData {
  symbol: string;
  exchange: 'binance' | 'kucoin' | 'both';
  price: string;
  change24h: string;
  changePercent24h: string;
  volume24h: string;
  high24h: string;
  low24h: string;
  lastUpdated: number;
  binanceData?: BinanceTicker;
  kucoinData?: KuCoinTicker;
}

export interface MarketInsight {
  symbol: string;
  currentPrice: string;
  aiPrediction: string;
  confidence: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  recommendation: 'Buy' | 'Hold' | 'Sell';
  marketSentiment: 'Bullish' | 'Bearish' | 'Neutral';
  keyFactors: string[];
  priceChange24h: string;
  volume24h: string;
  high24h: string;
  low24h: string;
}

export class MarketDataService {
  private static instance: MarketDataService;
  private cache: Map<string, UnifiedMarketData> = new Map();
  private cacheTimeout = 30000; // 30 seconds

  private constructor() {}

  public static getInstance(): MarketDataService {
    if (!MarketDataService.instance) {
      MarketDataService.instance = new MarketDataService();
    }
    return MarketDataService.instance;
  }

  // Get market data for specific symbols
  async getMarketData(symbols: string[]): Promise<UnifiedMarketData[]> {
    const results: UnifiedMarketData[] = [];
    
    for (const symbol of symbols) {
      try {
        const data = await this.getSymbolData(symbol);
        results.push(data);
      } catch (error) {
        console.error(`Error fetching data for ${symbol}:`, error);
        // Add fallback data
        results.push({
          symbol,
          exchange: 'binance',
          price: '0.00',
          change24h: '0.00',
          changePercent24h: '0.00',
          volume24h: '0.00',
          high24h: '0.00',
          low24h: '0.00',
          lastUpdated: Date.now()
        });
      }
    }
    
    return results;
  }

  // Get data for a single symbol
  private async getSymbolData(symbol: string): Promise<UnifiedMarketData> {
    const cacheKey = symbol.toUpperCase();
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.lastUpdated < this.cacheTimeout) {
      return cached;
    }

    try {
      // Try Binance first (more reliable)
      const binanceData = await BinanceService.getTicker(symbol);
      
      const marketData: UnifiedMarketData = {
        symbol: symbol.toUpperCase(),
        exchange: 'binance',
        price: binanceData.lastPrice,
        change24h: binanceData.priceChange,
        changePercent24h: binanceData.priceChangePercent,
        volume24h: binanceData.volume,
        high24h: binanceData.highPrice,
        low24h: binanceData.lowPrice,
        lastUpdated: Date.now(),
        binanceData
      };

      // Try to get KuCoin data as well
      try {
        const kucoinData = await KuCoinService.getTicker(symbol);
        marketData.exchange = 'both';
        marketData.kucoinData = kucoinData;
        
        // Use average price if both exchanges have data
        if (kucoinData.last && binanceData.lastPrice) {
          const binancePrice = parseFloat(binanceData.lastPrice);
          const kucoinPrice = parseFloat(kucoinData.last);
          marketData.price = ((binancePrice + kucoinPrice) / 2).toFixed(8);
        }
      } catch (kucoinError) {
        // KuCoin data not available, keep Binance only
        console.log(`KuCoin data not available for ${symbol}`);
      }

      this.cache.set(cacheKey, marketData);
      return marketData;
      
    } catch (binanceError) {
      // Try KuCoin as fallback
      try {
        const kucoinData = await KuCoinService.getTicker(symbol);
        
        const marketData: UnifiedMarketData = {
          symbol: symbol.toUpperCase(),
          exchange: 'kucoin',
          price: kucoinData.last,
          change24h: kucoinData.changePrice,
          changePercent24h: kucoinData.changeRate,
          volume24h: kucoinData.vol,
          high24h: kucoinData.high,
          low24h: kucoinData.low,
          lastUpdated: Date.now(),
          kucoinData
        };

        this.cache.set(cacheKey, marketData);
        return marketData;
        
      } catch (kucoinError) {
        throw new Error(`Both Binance and KuCoin failed for ${symbol}`);
      }
    }
  }

  // Get AI market insights based on real data
  async getMarketInsights(symbols: string[]): Promise<MarketInsight[]> {
    const marketData = await this.getMarketData(symbols);
    
    return marketData.map(data => {
      const changePercent = parseFloat(data.changePercent24h);
      const volume = parseFloat(data.volume24h);
      
      // AI prediction logic based on real data
      let aiPrediction = '';
      let confidence = 0;
      let recommendation: 'Buy' | 'Hold' | 'Sell' = 'Hold';
      let marketSentiment: 'Bullish' | 'Bearish' | 'Neutral' = 'Neutral';
      let keyFactors: string[] = [];

      if (changePercent > 5) {
        aiPrediction = `$${(parseFloat(data.price) * 1.1).toFixed(2)} by EOW`;
        confidence = 75;
        recommendation = 'Buy';
        marketSentiment = 'Bullish';
        keyFactors = ['Strong momentum', 'High volume', 'Positive price action'];
      } else if (changePercent > 2) {
        aiPrediction = `$${(parseFloat(data.price) * 1.05).toFixed(2)} by EOW`;
        confidence = 65;
        recommendation = 'Buy';
        marketSentiment = 'Bullish';
        keyFactors = ['Moderate momentum', 'Stable volume', 'Positive trend'];
      } else if (changePercent < -5) {
        aiPrediction = `$${(parseFloat(data.price) * 0.9).toFixed(2)} by EOW`;
        confidence = 70;
        recommendation = 'Sell';
        marketSentiment = 'Bearish';
        keyFactors = ['Strong decline', 'High volume', 'Negative momentum'];
      } else if (changePercent < -2) {
        aiPrediction = `$${(parseFloat(data.price) * 0.95).toFixed(2)} by EOW`;
        confidence = 60;
        recommendation = 'Sell';
        marketSentiment = 'Bearish';
        keyFactors = ['Moderate decline', 'Stable volume', 'Negative trend'];
      } else {
        aiPrediction = `$${data.price} stable`;
        confidence = 80;
        recommendation = 'Hold';
        marketSentiment = 'Neutral';
        keyFactors = ['Low volatility', 'Stable price', 'Consolidation'];
      }

      // Risk level based on volatility
      let riskLevel: 'Low' | 'Medium' | 'High' = 'Medium';
      if (Math.abs(changePercent) < 2) riskLevel = 'Low';
      else if (Math.abs(changePercent) > 8) riskLevel = 'High';

      return {
        symbol: data.symbol,
        currentPrice: `$${parseFloat(data.price).toFixed(2)}`,
        aiPrediction,
        confidence,
        riskLevel,
        recommendation,
        marketSentiment,
        keyFactors,
        priceChange24h: data.change24h,
        volume24h: data.volume24h,
        high24h: data.high24h,
        low24h: data.low24h
      };
    });
  }

  // Get top gainers and losers
  async getTopMovers(limit: number = 10): Promise<UnifiedMarketData[]> {
    try {
      const allTickers = await BinanceService.getAllTickers();
      
      // Filter USDT pairs and sort by change percentage
      const usdtPairs = allTickers
        .filter(ticker => ticker.symbol.endsWith('USDT'))
        .sort((a, b) => Math.abs(parseFloat(b.priceChangePercent)) - Math.abs(parseFloat(a.priceChangePercent)))
        .slice(0, limit);

      return usdtPairs.map(ticker => ({
        symbol: ticker.symbol,
        exchange: 'binance',
        price: ticker.lastPrice,
        change24h: ticker.priceChange,
        changePercent24h: ticker.priceChangePercent,
        volume24h: ticker.volume,
        high24h: ticker.highPrice,
        low24h: ticker.lowPrice,
        lastUpdated: Date.now(),
        binanceData: ticker
      }));
    } catch (error) {
      console.error('Error fetching top movers:', error);
      return [];
    }
  }

  // Clear cache
  clearCache(): void {
    this.cache.clear();
  }

  // Set cache timeout
  setCacheTimeout(timeout: number): void {
    this.cacheTimeout = timeout;
  }
}

export default MarketDataService.getInstance();
