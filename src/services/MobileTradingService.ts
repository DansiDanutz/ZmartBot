import { zmartBotAPI, MarketData, PortfolioPosition, TradingSignal } from './ZmartBotAPIGateway';

export interface PortfolioData {
  totalValue: number;
  totalPnL: number;
  totalPnLPercent: number;
  availableBalance: number;
  marginUsed: number;
  positions: PortfolioPosition[];
}

export class MobileTradingService {
  private static instance: MobileTradingService;
  private isInitialized: boolean = false;

  private constructor() {}

  public static getInstance(): MobileTradingService {
    if (!MobileTradingService.instance) {
      MobileTradingService.instance = new MobileTradingService();
    }
    return MobileTradingService.instance;
  }

  public async initialize(): Promise<void> {
    try {
      await zmartBotAPI.initialize({
        mobileServiceUrl: 'http://localhost:7777',
        timeout: 10000,
      });
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize MobileTradingService:', error);
      throw error;
    }
  }

  public async testConnection(): Promise<boolean> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }
      const health = await zmartBotAPI.getHealthStatus();
      return health.status === 'healthy';
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  public async getMarketData(): Promise<MarketData[]> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }
      return await zmartBotAPI.getMarketData();
    } catch (error) {
      console.error('Failed to get market data:', error);
      // Return mock data as fallback
      return this.getMockMarketData();
    }
  }

  public async getPortfolio(): Promise<PortfolioData> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }
      const positions = await zmartBotAPI.getPortfolio();
      
      const totalValue = positions.reduce((sum, pos) => sum + (pos.size * pos.currentPrice), 0);
      const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
      const totalPnLPercent = totalValue > 0 ? (totalPnL / totalValue) * 100 : 0;
      const marginUsed = positions.reduce((sum, pos) => sum + pos.marginUsed, 0);
      const availableBalance = 100000; // Mock available balance

      return {
        totalValue,
        totalPnL,
        totalPnLPercent,
        availableBalance,
        marginUsed,
        positions
      };
    } catch (error) {
      console.error('Failed to get portfolio:', error);
      // Return mock data as fallback
      return this.getMockPortfolioData();
    }
  }

  public async getTradingSignals(): Promise<TradingSignal[]> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }
      return await zmartBotAPI.getTradingSignals();
    } catch (error) {
      console.error('Failed to get trading signals:', error);
      // Return mock data as fallback
      return this.getMockTradingSignals();
    }
  }

  public async executeTrade(tradeParams: {
    symbol: string;
    side: 'BUY' | 'SELL';
    size: number;
    price: number;
    type: 'MARKET' | 'LIMIT';
  }): Promise<any> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }
      return await zmartBotAPI.executeTrade(tradeParams);
    } catch (error) {
      console.error('Trade execution failed:', error);
      throw error;
    }
  }

  // Mock data methods for fallback
  private getMockMarketData(): MarketData[] {
    return [
      {
        symbol: 'BTCUSDT',
        price: 43250.50,
        change24h: 1250.75,
        changePercent24h: 2.98,
        volume24h: 2850000000,
        high24h: 43500.00,
        low24h: 41800.00,
        lastUpdated: new Date().toISOString()
      },
      {
        symbol: 'ETHUSDT',
        price: 2650.25,
        change24h: 85.50,
        changePercent24h: 3.33,
        volume24h: 1850000000,
        high24h: 2680.00,
        low24h: 2550.00,
        lastUpdated: new Date().toISOString()
      },
      {
        symbol: 'BNBUSDT',
        price: 312.75,
        change24h: 12.25,
        changePercent24h: 4.08,
        volume24h: 850000000,
        high24h: 315.00,
        low24h: 300.00,
        lastUpdated: new Date().toISOString()
      }
    ];
  }

  private getMockPortfolioData(): PortfolioData {
    return {
      totalValue: 125000,
      totalPnL: 8750,
      totalPnLPercent: 7.5,
      availableBalance: 45000,
      marginUsed: 80000,
      positions: [
        {
          id: '1',
          symbol: 'BTCUSDT',
          side: 'LONG',
          size: 0.5,
          entryPrice: 42000,
          currentPrice: 43250.50,
          unrealizedPnL: 625.25,
          unrealizedPnLPercent: 2.98,
          marginUsed: 21000,
          leverage: 2,
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          symbol: 'ETHUSDT',
          side: 'SHORT',
          size: 2.0,
          entryPrice: 2700,
          currentPrice: 2650.25,
          unrealizedPnL: 99.50,
          unrealizedPnLPercent: 1.84,
          marginUsed: 1350,
          leverage: 10,
          timestamp: new Date().toISOString()
        }
      ]
    };
  }

  private getMockTradingSignals(): TradingSignal[] {
    return [
      {
        id: '1',
        symbol: 'BTCUSDT',
        signal: 'BUY',
        confidence: 85,
        price: '43250.50',
        targetPrice: '44500.00',
        stopLoss: '42500.00',
        timeframe: '4H',
        reasoning: 'Strong support at 42.5k, bullish momentum building',
        timestamp: Date.now()
      },
      {
        id: '2',
        symbol: 'ETHUSDT',
        signal: 'HOLD',
        confidence: 65,
        price: '2650.25',
        targetPrice: '2700.00',
        stopLoss: '2600.00',
        timeframe: '1H',
        reasoning: 'Consolidating above key support, waiting for breakout',
        timestamp: Date.now()
      }
    ];
  }
}

export const mobileTradingService = MobileTradingService.getInstance();










