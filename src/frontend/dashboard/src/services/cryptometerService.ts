/**
 * Cryptometer API Service for Frontend
 * Handles all Cryptometer API interactions from the frontend
 */

export interface CryptometerResponse {
  success: boolean;
  data?: any;
  error?: string;
  timestamp: string;
  endpoint: string;
}

export interface TradingSignalsResponse {
  symbol: string;
  price_data?: any;
  technical_indicators?: any;
  sentiment?: any;
  social_metrics?: any;
  confidence_score: number;
  timestamp: string;
}

export interface MarketAnalysisResponse {
  market_overview?: any;
  top_gainers?: any;
  top_losers?: any;
  fear_greed_index?: any;
  global_market_data?: any;
  timestamp: string;
}

export interface CacheStats {
  cache_size: number;
  rate_limit_calls: number;
  rate_limit_window: number;
  max_calls_per_window: number;
}

class CryptometerService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:5000';
  }

  private async makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}/api/v1/cryptometer${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error making request to ${endpoint}:`, error);
      throw error;
    }
  }

  // Market Data Endpoints
  async getMarketOverview(): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>('/market/overview');
  }

  async getTopGainers(limit: number = 50): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>(`/market/top-gainers?limit=${limit}`);
  }

  async getTopLosers(limit: number = 50): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>(`/market/top-losers?limit=${limit}`);
  }

  async getFearGreedIndex(): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>('/market/fear-greed-index');
  }

  // Crypto Data Endpoints
  async getCryptoData(symbol: string): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>(`/crypto/${symbol.toUpperCase()}`);
  }

  async getPriceData(symbol: string, timeframe: string = '24h'): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>(`/crypto/${symbol.toUpperCase()}/price?timeframe=${timeframe}`);
  }

  async getTechnicalIndicators(symbol: string): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>(`/crypto/${symbol.toUpperCase()}/indicators`);
  }

  async getSentimentData(symbol: string): Promise<CryptometerResponse> {
    return this.makeRequest<CryptometerResponse>(`/crypto/${symbol.toUpperCase()}/sentiment`);
  }

  // Trading Signals
  async getTradingSignals(symbol: string): Promise<TradingSignalsResponse> {
    return this.makeRequest<TradingSignalsResponse>(`/trading/signals/${symbol.toUpperCase()}`);
  }

  // Market Analysis
  async getMarketAnalysis(): Promise<MarketAnalysisResponse> {
    return this.makeRequest<MarketAnalysisResponse>('/market/analysis');
  }

  // Portfolio Analysis
  async getPortfolioAnalysis(symbols: string[]): Promise<any> {
    const symbolsParam = symbols.join(',');
    return this.makeRequest(`/portfolio/analysis?symbols=${symbolsParam}`);
  }

  // Cache Management
  async getCacheStats(): Promise<CacheStats> {
    return this.makeRequest<CacheStats>('/cache/stats');
  }

  async clearCache(): Promise<{ message: string; timestamp: string }> {
    return this.makeRequest<{ message: string; timestamp: string }>('/cache/clear', {
      method: 'POST',
    });
  }

  // Utility Methods for Dashboard
  async getDashboardData() {
    try {
      const [marketOverview, topGainers, topLosers, fearGreed] = await Promise.all([
        this.getMarketOverview(),
        this.getTopGainers(10),
        this.getTopLosers(10),
        this.getFearGreedIndex(),
      ]);

      return {
        marketOverview: marketOverview.data,
        topGainers: topGainers.data,
        topLosers: topLosers.data,
        fearGreedIndex: fearGreed.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  async getSymbolAnalysis(symbol: string) {
    try {
      const [cryptoData, priceData, indicators, sentiment] = await Promise.all([
        this.getCryptoData(symbol),
        this.getPriceData(symbol),
        this.getTechnicalIndicators(symbol),
        this.getSentimentData(symbol),
      ]);

      return {
        symbol: symbol.toUpperCase(),
        cryptoData: cryptoData.data,
        priceData: priceData.data,
        indicators: indicators.data,
        sentiment: sentiment.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error(`Error fetching analysis for ${symbol}:`, error);
      throw error;
    }
  }

  async getTradingSignalsForSymbols(symbols: string[]) {
    try {
      const signals = await Promise.all(
        symbols.map(symbol => this.getTradingSignals(symbol))
      );

      return {
        signals,
        timestamp: new Date().toISOString(),
        symbolCount: symbols.length,
      };
    } catch (error) {
      console.error('Error fetching trading signals:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const cryptometerService = new CryptometerService();
export default cryptometerService; 