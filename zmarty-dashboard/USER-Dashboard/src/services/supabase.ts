import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://asjtxrmftmutcsnqgidy.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database Types
export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  credit_balance: number
  avatar_url?: string
  is_verified: boolean
  two_factor_enabled: boolean
  created_at: string
  updated_at: string
}

export interface TradingSignal {
  id: string
  symbol: string
  signal_type: 'BUY' | 'SELL'
  confidence: number
  current_price: number
  target_price: number
  stop_loss: number
  timeframe: string
  status: 'active' | 'completed' | 'cancelled'
  analysis?: string
  pnl?: number
  user_id: string
  created_at: string
  updated_at: string
}

export interface MarketData {
  id: string
  symbol: string
  price: number
  change_24h?: number
  volume_24h?: number
  market_cap?: number
  timestamp: string
}

export interface UserPosition {
  id: string
  user_id: string
  signal_id?: string
  symbol: string
  position_type: 'LONG' | 'SHORT'
  entry_price: number
  current_price?: number
  quantity: number
  pnl: number
  status: 'open' | 'closed'
  opened_at: string
  closed_at?: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  user_id: string
  message_type: 'user' | 'assistant' | 'system'
  content: string
  metadata?: Record<string, any>
  created_at: string
}

export interface UserSettings {
  id: string
  user_id: string
  auto_trading_enabled: boolean
  risk_tolerance: 'low' | 'medium' | 'high'
  notification_preferences: Record<string, boolean>
  trading_preferences: Record<string, any>
  created_at: string
  updated_at: string
}

// Trading Signals Service
export const tradingSignalsService = {
  async getActiveSignals(userId: string): Promise<TradingSignal[]> {
    const { data, error } = await supabase
      .from('trading_signals')
      .select('*')
      .eq('user_id', userId)
      .eq('status', 'active')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  async getAllSignals(userId: string): Promise<TradingSignal[]> {
    const { data, error } = await supabase
      .from('trading_signals')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  async createSignal(signal: Omit<TradingSignal, 'id' | 'created_at' | 'updated_at'>): Promise<TradingSignal> {
    const { data, error } = await supabase
      .from('trading_signals')
      .insert([signal])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async updateSignal(id: string, updates: Partial<TradingSignal>): Promise<TradingSignal> {
    const { data, error } = await supabase
      .from('trading_signals')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  // Real-time subscription for trading signals
  subscribeToSignals(userId: string, callback: (payload: any) => void) {
    return supabase
      .channel('trading_signals')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'trading_signals',
          filter: `user_id=eq.${userId}`
        },
        callback
      )
      .subscribe()
  }
}

// Market Data Service
export const marketDataService = {
  async getLatestMarketData(): Promise<MarketData[]> {
    const { data, error } = await supabase
      .from('market_data')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(20)

    if (error) throw error
    return data || []
  },

  async getMarketDataBySymbol(symbol: string): Promise<MarketData[]> {
    const { data, error } = await supabase
      .from('market_data')
      .select('*')
      .eq('symbol', symbol)
      .order('timestamp', { ascending: false })
      .limit(100)

    if (error) throw error
    return data || []
  },

  async insertMarketData(marketData: Omit<MarketData, 'id'>): Promise<MarketData> {
    const { data, error } = await supabase
      .from('market_data')
      .insert([marketData])
      .select()
      .single()

    if (error) throw error
    return data
  },

  // Real-time subscription for market data
  subscribeToMarketData(callback: (payload: any) => void) {
    return supabase
      .channel('market_data')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'market_data'
        },
        callback
      )
      .subscribe()
  }
}

// User Positions Service
export const userPositionsService = {
  async getUserPositions(userId: string): Promise<UserPosition[]> {
    const { data, error } = await supabase
      .from('user_positions')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  async getOpenPositions(userId: string): Promise<UserPosition[]> {
    const { data, error } = await supabase
      .from('user_positions')
      .select('*')
      .eq('user_id', userId)
      .eq('status', 'open')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  async createPosition(position: Omit<UserPosition, 'id' | 'created_at' | 'updated_at'>): Promise<UserPosition> {
    const { data, error } = await supabase
      .from('user_positions')
      .insert([position])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async updatePosition(id: string, updates: Partial<UserPosition>): Promise<UserPosition> {
    const { data, error } = await supabase
      .from('user_positions')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  async closePosition(id: string, closedPrice: number): Promise<UserPosition> {
    const { data, error } = await supabase
      .from('user_positions')
      .update({
        status: 'closed',
        current_price: closedPrice,
        closed_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  }
}

// Chat Messages Service
export const chatService = {
  async getChatHistory(userId: string, limit: number = 50): Promise<ChatMessage[]> {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: true })
      .limit(limit)

    if (error) throw error
    return data || []
  },

  async sendMessage(message: Omit<ChatMessage, 'id' | 'created_at'>): Promise<ChatMessage> {
    const { data, error } = await supabase
      .from('chat_messages')
      .insert([message])
      .select()
      .single()

    if (error) throw error
    return data
  },

  // Real-time subscription for chat messages
  subscribeToChatMessages(userId: string, callback: (payload: any) => void) {
    return supabase
      .channel('chat_messages')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'chat_messages',
          filter: `user_id=eq.${userId}`
        },
        callback
      )
      .subscribe()
  }
}

// User Settings Service
export const userSettingsService = {
  async getUserSettings(userId: string): Promise<UserSettings | null> {
    const { data, error } = await supabase
      .from('user_settings')
      .select('*')
      .eq('user_id', userId)
      .single()

    if (error && error.code !== 'PGRST116') throw error
    return data
  },

  async updateUserSettings(userId: string, settings: Partial<UserSettings>): Promise<UserSettings> {
    const { data, error } = await supabase
      .from('user_settings')
      .upsert({
        user_id: userId,
        ...settings,
        updated_at: new Date().toISOString()
      })
      .select()
      .single()

    if (error) throw error
    return data
  }
}

// Service Registry Service (for monitoring ZmartBot services)
export const serviceRegistryService = {
  async getActiveServices() {
    const { data, error } = await supabase
      .from('service_registry')
      .select('*')
      .eq('status', 'ACTIVE')
      .order('service_name')

    if (error) throw error
    return data || []
  },

  async getServiceByName(serviceName: string) {
    const { data, error } = await supabase
      .from('service_registry')
      .select('*')
      .eq('service_name', serviceName)
      .single()

    if (error && error.code !== 'PGRST116') throw error
    return data
  }
}

export default supabase