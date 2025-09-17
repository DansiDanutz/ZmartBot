import { create } from 'zustand';
import { apiClient } from '../services/api';
import { useAuthStore } from './authStore';

interface CreditTransaction {
  id: string;
  transaction_type: string;
  amount: number;
  description: string;
  balance_before: number;
  balance_after: number;
  created_at: string;
}

interface CreditUsageStats {
  total_credits_used: number;
  usage_by_type: Record<string, number>;
  average_daily_usage: number;
  current_balance: number;
}

interface CreditPackage {
  id: string;
  name: string;
  description: string;
  credits: number;
  price: number;
  currency: string;
  discount_percentage: number;
  is_active: boolean;
}

interface CreditState {
  creditBalance: number;
  transactions: CreditTransaction[];
  usageStats: CreditUsageStats | null;
  packages: CreditPackage[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchCreditBalance: () => Promise<void>;
  fetchTransactions: (limit?: number, offset?: number) => Promise<void>;
  fetchUsageStats: (days?: number) => Promise<void>;
  fetchPackages: () => Promise<void>;
  purchaseCredits: (packageId: string) => Promise<void>;
  refreshData: () => Promise<void>;
}

export const useCreditStore = create<CreditState>((set, get) => ({
  creditBalance: 0,
  transactions: [],
  usageStats: null,
  packages: [],
  isLoading: false,
  error: null,

  fetchCreditBalance: async () => {
    try {
      const response = await apiClient.get('/credits/balance');
      const balance = response.data.balance;
      
      set({ creditBalance: balance });
      
      // Update auth store as well
      useAuthStore.getState().updateCreditBalance(balance);
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to fetch credit balance' });
    }
  },

  fetchTransactions: async (limit = 50, offset = 0) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get('/credits/transactions', {
        params: { limit, offset }
      });
      
      set({ 
        transactions: response.data.transactions,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to fetch transactions',
        isLoading: false 
      });
    }
  },

  fetchUsageStats: async (days = 30) => {
    try {
      const response = await apiClient.get('/credits/usage-stats', {
        params: { days }
      });
      
      set({ usageStats: response.data });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to fetch usage stats' });
    }
  },

  fetchPackages: async () => {
    try {
      const response = await apiClient.get('/credits/packages');
      set({ packages: response.data.packages });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to fetch packages' });
    }
  },

  purchaseCredits: async (packageId: string) => {
    set({ isLoading: true, error: null });
    try {
      // Create payment intent
      const response = await apiClient.post('/credits/purchase', {
        package_id: packageId
      });
      
      const { payment_intent_id, client_secret } = response.data;
      
      // Handle Stripe payment (simplified - would use Stripe Elements in real implementation)
      // For now, we'll simulate successful payment
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Confirm payment
      await apiClient.post('/credits/confirm-purchase', {
        payment_intent_id,
        package_id: packageId
      });
      
      // Refresh data
      await get().refreshData();
      
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Purchase failed',
        isLoading: false 
      });
      throw error;
    }
  },

  refreshData: async () => {
    const { fetchCreditBalance, fetchTransactions, fetchUsageStats, fetchPackages } = get();
    
    await Promise.allSettled([
      fetchCreditBalance(),
      fetchTransactions(),
      fetchUsageStats(),
      fetchPackages()
    ]);
  }
}));

// Initialize data when store is created
useCreditStore.getState().refreshData();