import axios from 'axios';
export const API = axios.create({
  baseURL: process.env.EXPO_PUBLIC_FOUNDATION_API_URL || 'http://127.0.0.1:8000',
  timeout: 10000,
});
