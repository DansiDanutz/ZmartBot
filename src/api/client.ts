import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Real API configuration
const API_BASE_URL = 'https://api.binance.com'; // Primary data source
const KUCOIN_API_URL = 'https://api.kucoin.com'; // Secondary data source

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// KuCoin API client
export const kucoinClient = axios.create({
  baseURL: KUCOIN_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  async (config) => {
    const userId = await AsyncStorage.getItem('user_id');
    if (userId && config.params) {
      config.params.user_id = userId;
    } else if (userId) {
      config.params = { user_id: userId };
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('user_id');
    }
    return Promise.reject(error);
  }
);

// Real-time market data functions
export const getRealTimePrice = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/api/v3/ticker/price`, {
      params: { symbol: symbol.toUpperCase() }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching real-time price for ${symbol}:`, error);
    throw error;
  }
};

export const get24hrTicker = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/api/v3/ticker/24hr`, {
      params: { symbol: symbol.toUpperCase() }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching 24hr ticker for ${symbol}:`, error);
    throw error;
  }
};

export const getKlines = async (symbol: string, interval: string = '1d', limit: number = 100) => {
  try {
    const response = await apiClient.get(`/api/v3/klines`, {
      params: {
        symbol: symbol.toUpperCase(),
        interval,
        limit
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching klines for ${symbol}:`, error);
    throw error;
  }
};

export const generateRequestId = () => {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
