export interface EvidenceItem {
  source: 'Cryptometer' | 'Binance' | 'KuCoin' | 'KingFisher' | 'RiskMetric' | 'Demo';
  text: string;
}

export interface SnapshotResponse {
  symbol: string;
  long_prob: number;
  short_prob: number;
  stance: 'long' | 'short' | 'wait';
  evidence: EvidenceItem[];
  disclaimer: string;
}

export interface BestEntryResponse {
  symbol: string;
  best_entry: number;
  est_prob: number;
  evidence: EvidenceItem[];
  disclaimer: string;
}

export interface TargetsResponse {
  symbol: string;
  tp: number[];
  sr: number[];
  trail_rule: string;
}

export interface PlanBResponse {
  symbol: string;
  invalidation: number;
  notes: string[];
}

export interface LadderStep {
  level_name: string;
  price: number;
  bankroll_pct: number;
  leverage_cap: number;
}

export interface LadderResponse {
  symbol: string;
  steps: LadderStep[];
  caps: Record<string, any>;
  alerts: string[];
}

export interface CreditsBalance {
  user_id: string;
  balance: number;
}

export interface LedgerItem {
  delta: number;
  reason: string;
  meta: Record<string, any>;
}

export interface PoolCreate {
  topic: string;
  goal_credits?: number;
  contribute?: number;
}

export interface PoolStatus {
  pool_id: number;
  topic: string;
  progress: number;
  goal: number;
}

export interface ContributeRequest {
  credits: number;
}

export interface AlertSubscribeRequest {
  symbols: string[];
  rules: string[];
  channel: string;
  plan: string;
}