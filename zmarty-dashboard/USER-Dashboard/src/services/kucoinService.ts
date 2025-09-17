import axios, { AxiosInstance } from 'axios';

export interface KuCoinMarketData {
  symbol: string;
  price: number;
  volume_24h: number;
  change_24h: number;
  high_24h: number;
  low_24h: number;
  timestamp: number;
}

export interface KuCoinPosition {
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  realized_pnl: number;
  margin_type: string;
  leverage: number;
  liquidation_price: number;
  timestamp: number;
}

export interface KuCoinOrder {
  id: string;
  symbol: string;
  side: string;
  type: string;
  size: number;
  price: number;
  status: string;
  timestamp: number;
}

export interface KuCoinAccount {
  account_id: string;
  currency: string;
  balance: number;
  available: number;
  holds: number;
  timestamp: number;
}

export interface KuCoinServiceResponse<T = any> {
  success: boolean;
  data: T;
  source: 'kucoin-api' | 'mock-data';
}

class KuCoinServiceClient {
  private api: AxiosInstance;
  private baseURL: string;
  private isConnected: boolean = false;

  constructor() {
    this.baseURL = 'http://localhost:8302';
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.api.interceptors.response.use(
      (response) => {
        this.isConnected = true;
        return response;
      },
      (error) => {
        console.error('KuCoin API Error:', error.message);
        this.isConnected = false;
        throw error;
      }
    );
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      this.isConnected = response.status === 200;
      return this.isConnected;
    } catch (error) {
      console.error('KuCoin health check failed:', error);
      this.isConnected = false;
      return false;
    }
  }

  async getMarketData(symbol: string, timeframe: string = '1m'): Promise<KuCoinMarketData> {
    try {
      const response = await this.api.get<KuCoinServiceResponse<KuCoinMarketData>>(
        `/api/v1/market-data/${symbol}?timeframe=${timeframe}`
      );
      
      if (!response.data.success) {
        throw new Error('Failed to get market data from KuCoin API');
      }

      return response.data.data;
    } catch (error) {
      console.error(`Error getting KuCoin market data for ${symbol}:`, error);
      throw error;
    }
  }

  async getAllMarketData(): Promise<Record<string, KuCoinMarketData>> {
    try {
      const symbols = await this.getAvailableSymbols();
      const marketData: Record<string, KuCoinMarketData> = {};

      for (const symbol of symbols.slice(0, 10)) { // Limit to first 10 symbols to avoid overload
        try {
          const data = await this.getMarketData(symbol);
          marketData[symbol] = data;
        } catch (error) {
          console.warn(`Failed to get market data for ${symbol}:`, error);
        }
      }

      return marketData;
    } catch (error) {
      console.error('Error getting all KuCoin market data:', error);
      throw error;
    }
  }

  async getPositions(): Promise<KuCoinPosition[]> {
    try {
      const response = await this.api.get<KuCoinServiceResponse<KuCoinPosition[]>>('/api/v1/positions');
      
      if (!response.data.success) {
        throw new Error('Failed to get positions from KuCoin API');
      }

      return response.data.data;
    } catch (error) {
      console.error('Error getting KuCoin positions:', error);
      throw error;
    }
  }

  async createOrder(orderData: {
    symbol: string;
    side: string;
    order_type: string;
    size: number;
    price?: number;
  }): Promise<KuCoinOrder> {
    try {
      const response = await this.api.post<KuCoinServiceResponse<KuCoinOrder>>(
        '/api/v1/orders',
        orderData
      );
      
      if (!response.data.success) {
        throw new Error('Failed to create order on KuCoin API');
      }

      return response.data.data;
    } catch (error) {
      console.error('Error creating KuCoin order:', error);
      throw error;
    }
  }

  async getAccountInfo(): Promise<KuCoinAccount> {
    try {
      const response = await this.api.get<KuCoinServiceResponse<KuCoinAccount>>('/api/v1/account');
      
      if (!response.data.success) {
        throw new Error('Failed to get account info from KuCoin API');
      }

      return response.data.data;
    } catch (error) {
      console.error('Error getting KuCoin account info:', error);
      throw error;
    }
  }

  async getAvailableSymbols(): Promise<string[]> {
    try {
      const response = await this.api.get<KuCoinServiceResponse<string[]>>('/api/v1/symbols');
      
      if (!response.data.success) {
        throw new Error('Failed to get symbols from KuCoin API');
      }

      return response.data.data;
    } catch (error) {
      console.error('Error getting KuCoin symbols:', error);
      throw error;
    }
  }

  async getMetrics(): Promise<any> {
    try {
      const response = await this.api.get('/metrics');
      return response.data;
    } catch (error) {
      console.error('Error getting KuCoin metrics:', error);
      throw error;
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getServiceInfo(): { name: string; port: number; baseURL: string; connected: boolean } {
    return {
      name: 'KuCoin Service',
      port: 8302,
      baseURL: this.baseURL,
      connected: this.isConnected
    };
  }

  // High-level analysis methods for Zmarty AI
  async getMarketSummary(): Promise<{
    totalSymbols: number;
    topGainers: KuCoinMarketData[];
    topLosers: KuCoinMarketData[];
    highVolume: KuCoinMarketData[];
    marketOverview: string;
  }> {
    try {
      const marketData = await this.getAllMarketData();
      const dataArray = Object.values(marketData);

      const topGainers = dataArray
        .filter(data => data.change_24h > 0)
        .sort((a, b) => b.change_24h - a.change_24h)
        .slice(0, 5);

      const topLosers = dataArray
        .filter(data => data.change_24h < 0)
        .sort((a, b) => a.change_24h - b.change_24h)
        .slice(0, 5);

      const highVolume = dataArray
        .sort((a, b) => b.volume_24h - a.volume_24h)
        .slice(0, 5);

      const avgChange = dataArray.reduce((sum, data) => sum + data.change_24h, 0) / dataArray.length;
      const marketOverview = avgChange > 0 ? 'Bullish Market' : 
                           avgChange < -2 ? 'Bearish Market' : 'Neutral Market';

      return {
        totalSymbols: dataArray.length,
        topGainers,
        topLosers,
        highVolume,
        marketOverview
      };
    } catch (error) {
      console.error('Error getting KuCoin market summary:', error);
      throw error;
    }
  }

  async getTradingOpportunities(): Promise<{
    volatileSymbols: KuCoinMarketData[];
    breakoutCandidates: KuCoinMarketData[];
    recommendations: string[];
  }> {
    try {
      const marketData = await this.getAllMarketData();
      const dataArray = Object.values(marketData);

      // Find volatile symbols (high price movement)
      const volatileSymbols = dataArray
        .filter(data => Math.abs(data.change_24h) > 5)
        .sort((a, b) => Math.abs(b.change_24h) - Math.abs(a.change_24h))
        .slice(0, 5);

      // Find potential breakout candidates (near 24h high with good volume)
      const breakoutCandidates = dataArray
        .filter(data => {
          const priceNearHigh = (data.price / data.high_24h) > 0.95;
          const goodVolume = data.volume_24h > 1000000; // Arbitrary threshold
          return priceNearHigh && goodVolume;
        })
        .slice(0, 5);

      const recommendations = [
        `${volatileSymbols.length} highly volatile symbols detected`,
        `${breakoutCandidates.length} potential breakout candidates found`,
        'Monitor these symbols for trading opportunities'
      ];

      return {
        volatileSymbols,
        breakoutCandidates,
        recommendations
      };
    } catch (error) {
      console.error('Error getting KuCoin trading opportunities:', error);
      throw error;
    }
  }

  async getRiskAnalysis(): Promise<{
    positions: KuCoinPosition[];
    totalExposure: number;
    riskLevel: 'Low' | 'Medium' | 'High';
    recommendations: string[];
  }> {
    try {
      const positions = await this.getPositions();
      const totalExposure = positions.reduce((sum, pos) => sum + Math.abs(pos.unrealized_pnl), 0);
      
      let riskLevel: 'Low' | 'Medium' | 'High' = 'Low';
      if (totalExposure > 10000) riskLevel = 'High';
      else if (totalExposure > 5000) riskLevel = 'Medium';

      const recommendations = [
        `Total unrealized P&L exposure: $${totalExposure.toFixed(2)}`,
        `Risk level: ${riskLevel}`,
        positions.length > 0 ? 'Monitor position leverage and liquidation prices' : 'No active positions'
      ];

      return {
        positions,
        totalExposure,
        riskLevel,
        recommendations
      };
    } catch (error) {
      console.error('Error getting KuCoin risk analysis:', error);
      throw error;
    }
  }
}

export const kucoinService = new KuCoinServiceClient();
export default kucoinService;