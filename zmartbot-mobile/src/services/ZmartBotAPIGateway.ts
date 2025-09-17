import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { buildMobileServiceUrl, validateConfig, PORTS } from '../config/ZmartBotConfig';

export interface ZmartBotConfig {
  mobileServiceUrl: string;
  apiKey?: string;
  timeout: number;
}

export interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
}

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  lastUpdated: string;
}

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  marketValue: number;
}

export interface TradingSignal {
  id: string;
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  price: number;
  targetPrice: number;
  stopLoss: number;
  reasoning: string;
  timestamp: string;
}

export interface IoTDevice {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'error';
  lastSeen: string;
  data: any;
}

export interface IoTData {
  deviceId: string;
  timestamp: string;
  data: any;
  type: string;
}

export class ZmartBotAPI {
  private static instance: ZmartBotAPI;
  private config: ZmartBotConfig;
  private mobileServiceClient: any;

  private constructor() {
    // Validate configuration - ensure mobile service uses port 7777
    const config = require('../config/ZmartBotConfig').getZmartBotConfig();
    if (!validateConfig(config)) {
      throw new Error('Invalid configuration: Mobile service MUST use port 7777');
    }

    this.config = {
      mobileServiceUrl: buildMobileServiceUrl(''),
      timeout: 10000,
    };

    // Create mobile service client (port 7777)
    this.mobileServiceClient = axios.create({
      baseURL: this.config.mobileServiceUrl,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'ZmartBot-Mobile/1.0.0',
      },
    });

    // Add request interceptor for authentication
    this.mobileServiceClient.interceptors.request.use(
      async (config: any) => {
        const apiKey = await AsyncStorage.getItem('zmartbot_api_key');
        if (apiKey) {
          config.headers.Authorization = `Bearer ${apiKey}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.mobileServiceClient.interceptors.response.use(
      (response: any) => response,
      (error: any) => {
        console.error('ZmartBot API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  public static getInstance(): ZmartBotAPI {
    if (!ZmartBotAPI.instance) {
      ZmartBotAPI.instance = new ZmartBotAPI();
    }
    return ZmartBotAPI.instance;
  }

  public async initialize(config: Partial<ZmartBotConfig>): Promise<void> {
    this.config = { ...this.config, ...config };
    
    // Validate port assignment
    if (!validateConfig(require('../config/ZmartBotConfig').getZmartBotConfig())) {
      throw new Error('Port validation failed: Mobile service MUST use port 7777');
    }
    
    console.log(`🚀 ZmartBot API Gateway initialized`);
    console.log(`📱 Mobile Service URL: ${this.config.mobileServiceUrl}`);
    console.log(`🔗 Port 7777: Mobile App Service (RESERVED)`);
    console.log(`🔗 Port 8000: ZmartBot Main API`);
  }

  public async getHealthStatus(): Promise<any> {
    try {
      const response = await this.mobileServiceClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  public async getMarketData(): Promise<MarketData[]> {
    try {
      const response = await this.mobileServiceClient.get('/api/market-data');
      return response.data.data || [];
    } catch (error) {
      console.error('Failed to fetch market data:', error);
      throw error;
    }
  }

  public async getPortfolio(): Promise<PortfolioPosition[]> {
    try {
      const response = await this.mobileServiceClient.get('/api/portfolio');
      return response.data.data || [];
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
      throw error;
    }
  }

  public async executeTrade(trade: any): Promise<any> {
    try {
      // Note: Trading execution goes through the mobile service on port 7777
      // which then forwards to zmart-api on port 8000
      const response = await this.mobileServiceClient.post('/api/trading/execute', trade);
      return response.data;
    } catch (error) {
      console.error('Trade execution failed:', error);
      throw error;
    }
  }

  public async getTradingSignals(): Promise<TradingSignal[]> {
    try {
      const response = await this.mobileServiceClient.get('/api/trading-signals');
      return response.data.data || [];
    } catch (error) {
      console.error('Failed to fetch trading signals:', error);
      throw error;
    }
  }

  public async getIoTDevices(): Promise<IoTDevice[]> {
    try {
      const response = await this.mobileServiceClient.get('/api/iot-devices');
      return response.data.data || [];
    } catch (error) {
      console.error('Failed to fetch IoT devices:', error);
      throw error;
    }
  }

  public async getIoTData(deviceId: string): Promise<IoTData[]> {
    try {
      const response = await this.mobileServiceClient.get(`/api/iot-devices/${deviceId}/data`);
      return response.data.data || [];
    } catch (error) {
      console.error('Failed to fetch IoT data:', error);
      throw error;
    }
  }

  public async getZmartIntegrationStatus(): Promise<any> {
    try {
      const response = await this.mobileServiceClient.get('/api/zmart-integration');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch integration status:', error);
      throw error;
    }
  }

  // Helper method to check if mobile service is running on port 7777
  public async checkMobileServiceStatus(): Promise<boolean> {
    try {
      const response = await this.mobileServiceClient.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('Mobile service on port 7777 is not accessible:', error);
      return false;
    }
  }

  // Helper method to get service configuration
  public getConfig(): ZmartBotConfig {
    return { ...this.config };
  }
}

export const zmartBotAPI = ZmartBotAPI.getInstance();
