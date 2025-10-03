import { MarketData, PortfolioPosition, TradingSignal, zmartBotAPI } from './ZmartBotAPIGateway';

// Mobile Trading Service - Integrates with ZmartBot Ecosystem
// This service provides mobile-optimized trading functionality

export interface MobileTrade {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  type: 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'TAKE_PROFIT';
  quantity: number;
  price?: number;
  status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'FAILED';
  timestamp: number;
  pnl?: number;
  fees?: number;
}

export interface MobilePortfolio {
  totalValue: number;
  totalPnL: number;
  totalPnLPercent: number;
  positions: PortfolioPosition[];
  availableBalance: number;
  marginUsed: number;
  freeMargin: number;
  lastUpdated: number;
}

export interface MobileAlert {
  id: string;
  type: 'PRICE' | 'VOLUME' | 'SIGNAL' | 'PORTFOLIO' | 'SYSTEM';
  symbol?: string;
  message: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  isRead: boolean;
  timestamp: number;
  actionRequired?: boolean;
}

export class MobileTradingService {
  private static instance: MobileTradingService;
  private isInitialized: boolean = false;
  private lastUpdate: number = 0;
  private updateInterval: number = 5000; // 5 seconds

  private constructor() {}

  public static getInstance(): MobileTradingService {
    if (!MobileTradingService.instance) {
      MobileTradingService.instance = new MobileTradingService();
    }
    return MobileTradingService.instance;
  }

  // Initialize the mobile trading service
  public async initialize(apiKey?: string): Promise<boolean> {
    try {
      // Connect to ZmartBot ecosystem
      await zmartBotAPI.initialize({ apiKey: apiKey || 'demo-key' });
      if (apiKey) {
        this.isInitialized = true;
        console.log('✅ Mobile Trading Service initialized');

        // Start real-time updates
        this.startRealTimeUpdates();

        return true;
      } else {
        console.error('❌ Failed to connect to ZmartBot ecosystem');
        return false;
      }
    } catch (error) {
      console.error('Failed to initialize Mobile Trading Service:', error);
      return false;
    }
  }

  // Get health status
  public async getHealthStatus(): Promise<any> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }
      return await zmartBotAPI.getHealthStatus();
    } catch (error) {
      console.error('Failed to fetch health status:', error);
      throw error;
    }
  }

  // Get market data (alias for mobile)
  public async getMarketData(symbols?: string[]): Promise<MarketData[]> {
    return this.getMobileMarketData(symbols);
  }

  // Get portfolio (alias for mobile)
  public async getPortfolio(): Promise<MobilePortfolio> {
    return this.getMobilePortfolio();
  }

  // Get real-time market data for mobile display
  public async getMobileMarketData(symbols: string[] = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']): Promise<MarketData[]> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }

      const marketData = await zmartBotAPI.getMarketData();
      this.lastUpdate = Date.now();
      
      return marketData;
    } catch (error) {
      console.error('Failed to fetch mobile market data:', error);
      throw error;
    }
  }

  // Get mobile-optimized portfolio data
  public async getMobilePortfolio(): Promise<MobilePortfolio> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }

      const positions = await zmartBotAPI.getPortfolio();
      
      // Calculate portfolio metrics
      const totalValue = positions.reduce((sum: number, pos: PortfolioPosition) => sum + (pos.size * pos.currentPrice), 0);
      const totalPnL = positions.reduce((sum: number, pos: PortfolioPosition) => sum + pos.pnl, 0);
      const totalPnLPercent = totalValue > 0 ? (totalPnL / totalValue) * 100 : 0;
      
      const portfolio: MobilePortfolio = {
        totalValue,
        totalPnL,
        totalPnLPercent,
        positions,
        availableBalance: 0, // Will be fetched from ZmartBot
        marginUsed: positions.reduce((sum: number, pos: PortfolioPosition) => sum + pos.margin, 0),
        freeMargin: 0, // Will be calculated
        lastUpdated: Date.now(),
      };

      return portfolio;
    } catch (error) {
      console.error('Failed to fetch mobile portfolio:', error);
      throw error;
    }
  }

  // Get trading signals optimized for mobile
  public async getMobileSignals(symbol?: string): Promise<TradingSignal[]> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }

      const signals = await zmartBotAPI.getTradingSignals();
      
      // Filter and sort signals for mobile display
      const mobileSignals = signals
        .filter(signal => signal.confidence >= 0.7) // Only high confidence signals
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 10); // Limit to top 10 signals

      return mobileSignals;
    } catch (error) {
      console.error('Failed to fetch mobile trading signals:', error);
      throw error;
    }
  }

  // Execute trade through ZmartBot ecosystem
  public async executeMobileTrade(tradeParams: {
    symbol: string;
    side: 'BUY' | 'SELL';
    type: 'MARKET' | 'LIMIT';
    quantity: number;
    price?: number;
  }): Promise<MobileTrade> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }

      // Execute trade through ZmartBot
      const result = await zmartBotAPI.executeTrade(tradeParams);
      
      // Create mobile trade object
      const mobileTrade: MobileTrade = {
        id: result.orderId || Date.now().toString(),
        symbol: tradeParams.symbol,
        side: tradeParams.side,
        type: tradeParams.type,
        quantity: tradeParams.quantity,
        price: tradeParams.price,
        status: 'EXECUTED',
        timestamp: Date.now(),
        pnl: result.pnl || 0,
        fees: result.fees || 0,
      };

      return mobileTrade;
    } catch (error) {
      console.error('Failed to execute mobile trade:', error);
      throw error;
    }
  }

  // Get IoT device status for mobile monitoring
  public async getMobileIoTStatus(): Promise<any> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }

      const iotStatus = await zmartBotAPI.getZmartIntegrationStatus();
      return iotStatus;
    } catch (error) {
      console.error('Failed to fetch mobile IoT status:', error);
      throw error;
    }
  }

  // Get mobile alerts
  public async getMobileAlerts(): Promise<MobileAlert[]> {
    try {
      if (!this.isInitialized) {
        throw new Error('Mobile Trading Service not initialized');
      }

      // Mock alerts for now - replace with actual API call when available
      const alerts: any[] = [];
      
      // Convert to mobile alert format
      const mobileAlerts: MobileAlert[] = alerts.map(alert => ({
        id: alert.id || Date.now().toString(),
        type: alert.type || 'SYSTEM',
        symbol: alert.symbol,
        message: alert.message,
        priority: alert.priority || 'MEDIUM',
        isRead: false,
        timestamp: alert.timestamp || Date.now(),
        actionRequired: alert.actionRequired || false,
      }));

      return mobileAlerts;
    } catch (error) {
      console.error('Failed to fetch mobile alerts:', error);
      throw error;
    }
  }

  // Start real-time updates for mobile
  private startRealTimeUpdates(): void {
    setInterval(async () => {
      try {
        if (this.isInitialized) {
          // Update market data every 5 seconds
          await this.getMobileMarketData();
          
          // Update portfolio every 30 seconds
          if (Date.now() - this.lastUpdate > 30000) {
            await this.getMobilePortfolio();
          }
        }
      } catch (error) {
        console.error('Real-time update failed:', error);
      }
    }, this.updateInterval);
  }

  // Check if service is initialized
  public isServiceInitialized(): boolean {
    return this.isInitialized;
  }

  // Get last update timestamp
  public getLastUpdate(): number {
    return this.lastUpdate;
  }

  // Stop real-time updates
  public stopRealTimeUpdates(): void {
    // This would be implemented with proper cleanup
    this.isInitialized = false;
  }
}

// Export singleton instance
export const mobileTradingService = MobileTradingService.getInstance();
