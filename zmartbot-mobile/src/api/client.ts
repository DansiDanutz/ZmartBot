import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Connect to ZmartBot backend API
const API_BASE_URL = 'http://192.168.1.166:8000/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
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

export const generateRequestId = () => {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};