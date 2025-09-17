import axios, { AxiosInstance } from 'axios';

export interface BinanceMarketData {
  symbol: string;
  price: number;
  volume: number;
  change_24h: number;
  timestamp: string;
}

export interface BinanceOrder {
  order_id: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  status: string;
  timestamp: string;
}

export interface BinanceAccount {
  account_type: string;
  permissions: string[];
  maker_commission: number;
  taker_commission: number;
  buyer_commission: number;
  seller_commission: number;
  can_trade: boolean;
  can_withdraw: boolean;
  can_deposit: boolean;
  timestamp: string;
}

export interface BinanceMetrics {
  service: string;
  timestamp: string;
  metrics: {
    binance_connected: boolean;
    total_orders: number;
    successful_orders: number;
    failed_orders: number;
    total_volume: number;
    active_orders_count: number;
  };
}

class BinanceServiceClient {
  private api: AxiosInstance;
  private baseURL: string;
  private isConnected: boolean = false;

  constructor() {
    this.baseURL = 'http://localhost:8303';
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
        console.error('Binance API Error:', error.message);
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
      console.error('Binance health check failed:', error);
      this.isConnected = false;
      return false;
    }
  }

  async checkReadiness(): Promise<boolean> {
    try {
      const response = await this.api.get('/ready');
      return response.data.status === 'ready';
    } catch (error) {
      console.error('Binance readiness check failed:', error);
      return false;
    }
  }

  async connectToBinance(): Promise<boolean> {
    try {
      const response = await this.api.post('/api/v1/binance/connect');
      return response.data.success;
    } catch (error) {
      console.error('Error connecting to Binance:', error);
      return false;
    }
  }

  async getMarketData(symbol: string): Promise<BinanceMarketData> {
    try {
      const response = await this.api.get(`/api/v1/binance/market-data/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting Binance market data for ${symbol}:`, error);
      throw error;
    }
  }

  async getAllMarketData(): Promise<Record<string, BinanceMarketData>> {
    try {
      const response = await this.api.get('/api/v1/binance/market-data');
      return response.data;
    } catch (error) {
      console.error('Error getting all Binance market data:', error);
      throw error;
    }
  }

  async placeOrder(orderData: {
    symbol: string;
    side: string;
    quantity: number;
    price?: number;
  }): Promise<BinanceOrder> {
    try {
      const response = await this.api.post('/api/v1/binance/order', orderData);
      return response.data;
    } catch (error) {
      console.error('Error placing Binance order:', error);
      throw error;
    }
  }

  async getOrder(orderId: string): Promise<BinanceOrder> {
    try {
      const response = await this.api.get(`/api/v1/binance/order/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting Binance order ${orderId}:`, error);
      throw error;
    }
  }

  async cancelOrder(orderId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.api.delete(`/api/v1/binance/order/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`Error cancelling Binance order ${orderId}:`, error);
      throw error;
    }
  }

  async getAllOrders(): Promise<BinanceOrder[]> {
    try {
      const response = await this.api.get('/api/v1/binance/orders');
      return response.data.orders;
    } catch (error) {
      console.error('Error getting all Binance orders:', error);
      throw error;
    }
  }

  async getAccountInfo(): Promise<BinanceAccount> {
    try {
      const response = await this.api.get('/api/v1/binance/account');
      return response.data;
    } catch (error) {
      console.error('Error getting Binance account info:', error);
      throw error;
    }
  }

  async getMetrics(): Promise<BinanceMetrics> {
    try {
      const response = await this.api.get('/metrics');
      return response.data;
    } catch (error) {
      console.error('Error getting Binance metrics:', error);
      throw error;
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getServiceInfo(): { name: string; port: number; baseURL: string; connected: boolean } {
    return {
      name: 'Binance Service',
      port: 8303,
      baseURL: this.baseURL,
      connected: this.isConnected
    };
  }

  // High-level analysis methods for Zmarty AI
  async getMarketSummary(): Promise<{
    totalSymbols: number;
    topGainers: BinanceMarketData[];
    topLosers: BinanceMarketData[];
    highVolume: BinanceMarketData[];
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
        .sort((a, b) => b.volume - a.volume)
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
      console.error('Error getting Binance market summary:', error);
      throw error;
    }
  }

  async getTradingActivity(): Promise<{
    activeOrders: BinanceOrder[];
    recentTrades: BinanceOrder[];
    tradingStats: {
      totalOrders: number;
      successfulOrders: number;
      failedOrders: number;
      totalVolume: number;
      successRate: number;
    };
    recommendations: string[];
  }> {
    try {
      const [orders, metrics] = await Promise.all([
        this.getAllOrders(),
        this.getMetrics()
      ]);

      const activeOrders = orders.filter(order => 
        order.status === 'PENDING' || order.status === 'FILLED'
      );

      const recentTrades = orders
        .filter(order => order.status === 'FILLED')
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, 10);

      const tradingStats = {
        totalOrders: metrics.metrics.total_orders,
        successfulOrders: metrics.metrics.successful_orders,
        failedOrders: metrics.metrics.failed_orders,
        totalVolume: metrics.metrics.total_volume,
        successRate: metrics.metrics.total_orders > 0 ? 
          (metrics.metrics.successful_orders / metrics.metrics.total_orders) * 100 : 0
      };

      const recommendations = [
        `${activeOrders.length} active orders currently running`,
        `Trading success rate: ${tradingStats.successRate.toFixed(1)}%`,
        `Total volume traded: ${tradingStats.totalVolume.toFixed(4)}`,
        tradingStats.successRate > 80 ? 'Strong trading performance' : 
        tradingStats.successRate > 60 ? 'Moderate trading performance' : 'Consider reviewing trading strategy'
      ];

      return {
        activeOrders,
        recentTrades,
        tradingStats,
        recommendations
      };
    } catch (error) {
      console.error('Error getting Binance trading activity:', error);
      throw error;
    }
  }

  async getAccountAnalysis(): Promise<{
    account: BinanceAccount;
    tradingCapabilities: string[];
    securityLevel: 'High' | 'Medium' | 'Low';
    recommendations: string[];
  }> {
    try {
      const account = await this.getAccountInfo();

      const tradingCapabilities = [];
      if (account.can_trade) tradingCapabilities.push('Spot Trading');
      if (account.can_deposit) tradingCapabilities.push('Deposits');
      if (account.can_withdraw) tradingCapabilities.push('Withdrawals');

      const securityLevel: 'High' | 'Medium' | 'Low' = 
        account.permissions.length >= 2 ? 'High' : 
        account.permissions.length === 1 ? 'Medium' : 'Low';

      const recommendations = [
        `Account type: ${account.account_type}`,
        `Security level: ${securityLevel}`,
        `Trading capabilities: ${tradingCapabilities.join(', ')}`,
        `Maker commission: ${account.maker_commission}bps`,
        `Taker commission: ${account.taker_commission}bps`
      ];

      return {
        account,
        tradingCapabilities,
        securityLevel,
        recommendations
      };
    } catch (error) {
      console.error('Error getting Binance account analysis:', error);
      throw error;
    }
  }

  async getArbitrageOpportunities(referenceData: Record<string, any>): Promise<{
    opportunities: Array<{
      symbol: string;
      binancePrice: number;
      referencePrice: number;
      priceDiff: number;
      percentDiff: number;
      opportunity: 'buy_binance' | 'sell_binance' | 'neutral';
    }>;
    recommendations: string[];
  }> {
    try {
      const binanceData = await this.getAllMarketData();
      const opportunities = [];

      for (const [symbol, binanceInfo] of Object.entries(binanceData)) {
        if (referenceData[symbol]) {
          const binancePrice = binanceInfo.price;
          const referencePrice = referenceData[symbol].price;
          const priceDiff = binancePrice - referencePrice;
          const percentDiff = (priceDiff / referencePrice) * 100;

          let opportunity: 'buy_binance' | 'sell_binance' | 'neutral' = 'neutral';
          if (percentDiff < -0.5) opportunity = 'buy_binance';
          else if (percentDiff > 0.5) opportunity = 'sell_binance';

          opportunities.push({
            symbol,
            binancePrice,
            referencePrice,
            priceDiff,
            percentDiff,
            opportunity
          });
        }
      }

      const profitableOpps = opportunities.filter(opp => opp.opportunity !== 'neutral');
      const recommendations = [
        `${opportunities.length} symbols compared for arbitrage`,
        `${profitableOpps.length} potential arbitrage opportunities found`,
        profitableOpps.length > 0 ? 'Monitor spreads for profitable trades' : 'No significant arbitrage opportunities currently'
      ];

      return {
        opportunities: opportunities.sort((a, b) => Math.abs(b.percentDiff) - Math.abs(a.percentDiff)),
        recommendations
      };
    } catch (error) {
      console.error('Error getting Binance arbitrage opportunities:', error);
      throw error;
    }
  }
}

export const binanceService = new BinanceServiceClient();
export default binanceService;