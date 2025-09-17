export interface User {
  id: string
  email: string
  username: string
  fullName?: string
  creditBalance: number
  tier: 'basic' | 'premium' | 'enterprise'
  isActive: boolean
  avatar?: string
  preferences?: UserPreferences
  stats?: UserStats
  createdAt: string
  updatedAt?: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: string
  timezone: string
  notifications: NotificationPreferences
  trading: TradingPreferences
  dashboard: DashboardPreferences
}

export interface NotificationPreferences {
  email: boolean
  browser: boolean
  mobile: boolean
  priceAlerts: boolean
  marketNews: boolean
  systemUpdates: boolean
  tradingSignals: boolean
}

export interface TradingPreferences {
  defaultExchange: string
  favoriteSymbols: string[]
  riskLevel: 'conservative' | 'moderate' | 'aggressive'
  autoTrading: boolean
  stopLoss: boolean
  takeProfit: boolean
}

export interface DashboardPreferences {
  layout: 'compact' | 'comfortable' | 'spacious'
  widgets: string[]
  defaultPage: string
  sidebarCollapsed: boolean
}

export interface UserStats {
  totalTrades: number
  successfulTrades: number
  totalProfitLoss: number
  winRate: number
  avgHoldTime: number
  creditsUsed: number
  lastActivity: string
  joinDate: string
}

export interface CreditTransaction {
  id: string
  userId: string
  transactionType: 'purchase' | 'usage' | 'refund' | 'bonus'
  amount: number
  description: string
  balanceBefore: number
  balanceAfter: number
  createdAt: string
}

export interface CreditPackage {
  id: string
  name: string
  description: string
  credits: number
  price: number
  currency: string
  discountPercentage: number
  isActive: boolean
  popular?: boolean
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginCredentials {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterData {
  email: string
  password: string
  username: string
  fullName?: string
}

export interface ForgotPasswordData {
  email: string
}

export interface ResetPasswordData {
  token: string
  password: string
  confirmPassword: string
}

export interface UpdateProfileData {
  fullName?: string
  email?: string
  username?: string
  preferences?: Partial<UserPreferences>
}

export interface ChangePasswordData {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}