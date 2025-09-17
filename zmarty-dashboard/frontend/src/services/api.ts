import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log response time in development
    if (import.meta.env.DEV && response.config.metadata) {
      const endTime = new Date();
      const duration = endTime.getTime() - response.config.metadata.startTime.getTime();
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    
    return response;
  },
  (error) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data);
    }
    
    // Handle common HTTP errors
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          error.message = data.detail || 'Invalid request';
          break;
        case 401:
          error.message = 'Authentication required';
          break;
        case 403:
          error.message = 'Access denied';
          break;
        case 404:
          error.message = 'Resource not found';
          break;
        case 422:
          error.message = data.detail || 'Validation error';
          break;
        case 429:
          error.message = 'Too many requests. Please try again later.';
          break;
        case 500:
          error.message = 'Server error. Please try again later.';
          break;
        default:
          error.message = data.detail || 'An unexpected error occurred';
      }
    } else if (error.request) {
      error.message = 'Network error. Please check your connection.';
    } else {
      error.message = 'An unexpected error occurred';
    }
    
    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Auth endpoints
  auth: {
    login: (email: string, password: string) => 
      apiClient.post('/auth/login', { email, password }),
    
    register: (userData: {
      email: string;
      username: string;
      password: string;
      full_name?: string;
    }) => apiClient.post('/auth/register', userData),
    
    refresh: (refreshToken: string) => 
      apiClient.post('/auth/refresh', {}, {
        headers: { Authorization: `Bearer ${refreshToken}` }
      }),
    
    me: () => apiClient.get('/auth/me'),
    
    logout: () => apiClient.post('/auth/logout')
  },

  // User endpoints
  users: {
    updateProfile: (data: any) => apiClient.put('/users/profile', data),
    
    changePassword: (currentPassword: string, newPassword: string) =>
      apiClient.put('/users/password', { current_password: currentPassword, new_password: newPassword }),
    
    deactivate: () => apiClient.delete('/users/profile')
  },

  // Credit endpoints
  credits: {
    getBalance: () => apiClient.get('/credits/balance'),
    
    getPackages: () => apiClient.get('/credits/packages'),
    
    getTransactions: (limit = 50, offset = 0) => 
      apiClient.get('/credits/transactions', { params: { limit, offset } }),
    
    getUsageStats: (days = 30) => 
      apiClient.get('/credits/usage-stats', { params: { days } }),
    
    purchase: (packageId: string) => 
      apiClient.post('/credits/purchase', { package_id: packageId }),
    
    confirmPurchase: (paymentIntentId: string, packageId: string) =>
      apiClient.post('/credits/confirm-purchase', { 
        payment_intent_id: paymentIntentId, 
        package_id: packageId 
      })
  },

  // Zmarty AI endpoints
  zmarty: {
    query: (data: {
      query: string;
      request_type: string;
      parameters?: Record<string, any>;
    }) => apiClient.post('/zmarty/query', data),
    
    getRequests: (limit = 50, offset = 0, status?: string) => 
      apiClient.get('/zmarty/requests', { params: { limit, offset, status } }),
    
    getRequest: (requestId: string) => 
      apiClient.get(`/zmarty/requests/${requestId}`),
    
    rateResponse: (requestId: string, qualityScore: number) =>
      apiClient.post(`/zmarty/rate/${requestId}`, { quality_score: qualityScore }),
    
    getTrendingQueries: (limit = 10) => 
      apiClient.get('/zmarty/trending', { params: { limit } }),
    
    tradingAnalysis: (data: any) => 
      apiClient.post('/zmarty/trading-analysis', data),
    
    marketSignals: (data: any) => 
      apiClient.post('/zmarty/market-signals', data),
    
    aiPredictions: (data: any) => 
      apiClient.post('/zmarty/ai-predictions', data)
  },

  // Dashboard endpoints
  dashboard: {
    getOverview: () => apiClient.get('/dashboard/overview'),
    
    getRecentActivity: (limit = 20) => 
      apiClient.get('/dashboard/recent-activity', { params: { limit } }),
    
    getPerformanceMetrics: (timeframe = '30d') => 
      apiClient.get('/dashboard/performance', { params: { timeframe } })
  },

  // WebSocket stats
  websocket: {
    getStats: () => apiClient.get('/ws/stats')
  }
};

// Helper function to set auth token
export const setAuthToken = (token: string | null) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
};

// Helper function to handle file uploads
export const uploadFile = async (
  endpoint: string, 
  file: File, 
  onProgress?: (progress: number) => void
) => {
  const formData = new FormData();
  formData.append('file', file);

  return apiClient.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
};

// Helper function for paginated requests
export const paginatedRequest = async <T>(
  requestFn: (limit: number, offset: number) => Promise<{ data: T[] }>,
  limit = 50
): Promise<T[]> => {
  let allData: T[] = [];
  let offset = 0;
  let hasMore = true;

  while (hasMore) {
    const response = await requestFn(limit, offset);
    const newData = response.data;
    
    allData = [...allData, ...newData];
    hasMore = newData.length === limit;
    offset += limit;
  }

  return allData;
};

export default apiClient;