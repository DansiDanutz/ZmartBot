import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface ZmartBotConfig {
  mobileServiceUrl: string;
  apiKey?: string;
  timeout: number;
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
  id: string;
  symbol: string;
  side: 'LONG' | 'SHORT';
  size: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  marginUsed: number;
  leverage: number;
  timestamp: string;
}

export interface TradingSignal {
  id: string;
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  price: string;
  targetPrice: string;
  stopLoss: string;
  timeframe: string;
  reasoning: string;
  timestamp: number;
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
  value: number;
  unit: string;
  type: string;
}

export class ZmartBotAPI {
  private static instance: ZmartBotAPI;
  private config: ZmartBotConfig;
  private apiClient: AxiosInstance;

  private constructor() {
    this.config = {
      mobileServiceUrl: 'http://localhost:7777',
      timeout: 10000,
    };
    this.apiClient = axios.create({
      baseURL: this.config.mobileServiceUrl,
      timeout: this.config.timeout,
    });
    this.setupInterceptors();
  }

  public static getInstance(): ZmartBotAPI {
    if (!ZmartBotAPI.instance) {
      ZmartBotAPI.instance = new ZmartBotAPI();
    }
    return ZmartBotAPI.instance;
  }

  public async initialize(config: ZmartBotConfig): Promise<void> {
    this.config = { ...this.config, ...config };
    this.apiClient = axios.create({
      baseURL: this.config.mobileServiceUrl,
      timeout: this.config.timeout,
    });
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.apiClient.interceptors.request.use(
      async (config) => {
        const apiKey = await AsyncStorage.getItem('zmartbot_api_key');
        if (apiKey) {
          config.headers.Authorization = `Bearer ${apiKey}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await AsyncStorage.removeItem('zmartbot_api_key');
        }
        return Promise.reject(error);
      }
    );
  }

  public async getHealthStatus(): Promise<any> {
    try {
      const response = await this.apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  public async getMarketData(): Promise<MarketData[]> {
    try {
      const response = await this.apiClient.get('/market-data');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch market data:', error);
      throw error;
    }
  }

  public async getPortfolio(): Promise<PortfolioPosition[]> {
    try {
      const response = await this.apiClient.get('/portfolio');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
      throw error;
    }
  }

  public async executeTrade(trade: any): Promise<any> {
    try {
      const response = await this.apiClient.post('/trade', trade);
      return response.data;
    } catch (error) {
      console.error('Trade execution failed:', error);
      throw error;
    }
  }

  public async getTradingSignals(): Promise<TradingSignal[]> {
    try {
      const response = await this.apiClient.get('/trading-signals');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch trading signals:', error);
      throw error;
    }
  }

  public async getIoTDevices(): Promise<IoTDevice[]> {
    try {
      const response = await this.apiClient.get('/iot/devices');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch IoT devices:', error);
      throw error;
    }
  }

  public async getIoTData(deviceId: string): Promise<IoTData[]> {
    try {
      const response = await this.apiClient.get(`/iot/devices/${deviceId}/data`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch IoT data:', error);
      throw error;
    }
  }
}

export const zmartBotAPI = ZmartBotAPI.getInstance();








