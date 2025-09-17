import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '../services/api';

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  credit_balance: number;
  tier: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  updateCreditBalance: (newBalance: number) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.post('/auth/login', {
            email,
            password
          });
          
          const { access_token, refresh_token } = response.data;
          
          // Set tokens in API client
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          // Get user info
          const userResponse = await apiClient.get('/auth/me');
          const user = userResponse.data;
          
          set({
            user,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error: any) {
          set({ isLoading: false });
          throw new Error(error.response?.data?.detail || 'Login failed');
        }
      },

      register: async (data) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.post('/auth/register', data);
          const user = response.data;
          
          // Auto-login after registration
          await get().login(data.email, data.password);
        } catch (error: any) {
          set({ isLoading: false });
          throw new Error(error.response?.data?.detail || 'Registration failed');
        }
      },

      logout: () => {
        // Remove token from API client
        delete apiClient.defaults.headers.common['Authorization'];
        
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false
        });
      },

      refreshAuth: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().logout();
          return;
        }

        try {
          const response = await apiClient.post('/auth/refresh', {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`
            }
          });
          
          const { access_token } = response.data;
          
          // Set new token in API client
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          // Get updated user info
          const userResponse = await apiClient.get('/auth/me');
          const user = userResponse.data;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true
          });
        } catch (error) {
          get().logout();
          throw error;
        }
      },

      updateUser: async (data) => {
        const { user } = get();
        if (!user) return;

        try {
          const response = await apiClient.put('/users/profile', data);
          const updatedUser = response.data;
          
          set({ user: updatedUser });
        } catch (error: any) {
          throw new Error(error.response?.data?.detail || 'Failed to update profile');
        }
      },

      updateCreditBalance: (newBalance: number) => {
        const { user } = get();
        if (!user) return;

        set({
          user: {
            ...user,
            credit_balance: newBalance
          }
        });
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      }),
      onRehydrateStorage: () => (state) => {
        // Set token in API client when hydrating from storage
        if (state?.token) {
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
        }
      }
    }
  )
);

// Interceptor to handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await useAuthStore.getState().refreshAuth();
        return apiClient(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);