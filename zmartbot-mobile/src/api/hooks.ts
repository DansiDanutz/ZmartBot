import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, generateRequestId } from './client';
import type {
  SnapshotResponse,
  BestEntryResponse,
  TargetsResponse,
  PlanBResponse,
  LadderResponse,
  CreditsBalance,
  LedgerItem,
  PoolCreate,
  PoolStatus,
  ContributeRequest,
  AlertSubscribeRequest,
} from '../types/api';

// Signals API
export const useSnapshot = (symbol: string) => {
  return useQuery({
    queryKey: ['snapshot', symbol],
    queryFn: async (): Promise<SnapshotResponse> => {
      // Mock data to prevent freeze
      return {
        symbol,
        long_prob: 0.65,
        short_prob: 0.35,
        stance: 'long',
        evidence: [
          { source: 'Demo', text: 'Sample trading signal data' }
        ],
        disclaimer: 'Demo mode - not real trading advice'
      };
    },
    enabled: !!symbol,
    staleTime: 5 * 60 * 1000,
  });
};

export const useBestEntry = (symbol: string) => {
  return useQuery({
    queryKey: ['best-entry', symbol],
    queryFn: async (): Promise<BestEntryResponse> => {
      return {
        symbol,
        best_entry: 45000,
        est_prob: 0.75,
        evidence: [{ source: 'Demo', text: 'Sample entry point' }],
        disclaimer: 'Demo mode'
      };
    },
    enabled: !!symbol,
    staleTime: 5 * 60 * 1000,
  });
};

export const useTargets = (symbol: string) => {
  return useQuery({
    queryKey: ['targets', symbol],
    queryFn: async (): Promise<TargetsResponse> => {
      const { data } = await apiClient.post(`/signals/targets`, { symbol });
      return data;
    },
    enabled: !!symbol,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const usePlanB = (symbol: string) => {
  return useQuery({
    queryKey: ['plan-b', symbol],
    queryFn: async (): Promise<PlanBResponse> => {
      const { data } = await apiClient.post(`/signals/plan-b`, { symbol });
      return data;
    },
    enabled: !!symbol,
    staleTime: 10 * 60 * 1000,
  });
};

export const useLadder = (symbol: string, bankroll: number = 10000) => {
  return useQuery({
    queryKey: ['ladder', symbol, bankroll],
    queryFn: async (): Promise<LadderResponse> => {
      const { data } = await apiClient.post(`/signals/ladder`, { symbol, bankroll });
      return data;
    },
    enabled: !!symbol,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

// Credits API
export const useCreditsBalance = () => {
  return useQuery({
    queryKey: ['credits-balance'],
    queryFn: async (): Promise<CreditsBalance> => {
      return { user_id: 'demo_user', balance: 10000 };
    },
    staleTime: 30 * 1000,
  });
};

export const useCreditsLedger = () => {
  return useQuery({
    queryKey: ['credits-ledger'],
    queryFn: async (): Promise<LedgerItem[]> => {
      const { data } = await apiClient.get('/credits/ledger');
      return data;
    },
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useSpendCredits = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (credits: number) => {
      const requestId = generateRequestId();
      const { data } = await apiClient.post('/credits/spend', 
        {},
        { 
          params: { 
            amount: credits, 
            reason: `Signal request for ${credits} credits` 
          },
          headers: { 'X-Request-ID': requestId } 
        }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credits-balance'] });
      queryClient.invalidateQueries({ queryKey: ['credits-ledger'] });
    },
  });
};

// Pools API
export const usePools = () => {
  return useQuery({
    queryKey: ['pools'],
    queryFn: async (): Promise<PoolStatus[]> => {
      const { data } = await apiClient.get('/pools');
      return data;
    },
    staleTime: 60 * 1000, // 1 minute
  });
};

export const usePool = (poolId: number) => {
  return useQuery({
    queryKey: ['pool', poolId],
    queryFn: async (): Promise<PoolStatus> => {
      const { data } = await apiClient.get(`/pools/${poolId}`);
      return data;
    },
    enabled: !!poolId,
    staleTime: 30 * 1000,
  });
};

export const useCreatePool = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (pool: PoolCreate) => {
      const { data } = await apiClient.post('/pools', pool);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pools'] });
      queryClient.invalidateQueries({ queryKey: ['credits-balance'] });
    },
  });
};

export const useContributeToPool = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ poolId, credits }: { poolId: number; credits: number }) => {
      const { data } = await apiClient.post(`/pools/${poolId}/contribute`, { credits });
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['pools'] });
      queryClient.invalidateQueries({ queryKey: ['pool', variables.poolId] });
      queryClient.invalidateQueries({ queryKey: ['credits-balance'] });
    },
  });
};

// Alerts API
export const useSubscribeAlerts = () => {
  return useMutation({
    mutationFn: async (request: AlertSubscribeRequest) => {
      const { data } = await apiClient.post('/alerts/subscribe', request);
      return data;
    },
  });
};