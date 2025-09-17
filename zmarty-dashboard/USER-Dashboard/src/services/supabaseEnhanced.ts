import { supabase } from './supabase'
import { 
  tradingSignalsService,
  marketDataService,
  userPositionsService,
  chatService,
  userSettingsService,
  serviceRegistryService
} from './supabase'
import type { 
  TradingSignal, 
  MarketData, 
  UserPosition, 
  ChatMessage, 
  UserSettings, 
  User 
} from './supabase'

// Extended interfaces for MCP integration
export interface MemoryEntry {
  id: string
  type: 'conversation' | 'trading_decision' | 'market_analysis' | 'user_preference' | 'ai_learning'
  symbol?: string
  content: string
  metadata: {
    user_id?: string
    session_id: string
    confidence: number
    source: string
    automated: boolean
    context_tags: string[]
    outcome?: string
  }
  timestamp: string
  expires_at?: string
  embeddings?: number[]
  relevance_score?: number
}

export interface ConversationMemory {
  id: string
  user_id: string
  session_id: string
  messages: Array<{
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: string
    metadata?: any
  }>
  context_summary: string
  trading_preferences: any
  last_updated: string
}

export interface TradingMemory {
  id: string
  symbol: string
  historical_decisions: Array<{
    decision: 'buy' | 'sell' | 'hold'
    reasoning: string
    confidence: number
    outcome?: 'profitable' | 'loss' | 'neutral'
    timestamp: string
  }>
  learned_patterns: string[]
  success_rate: number
  risk_tolerance: number
  preferred_strategies: string[]
}

export interface MarketMemory {
  id: string
  symbol: string
  price_patterns: Array<{
    pattern_type: string
    description: string
    success_rate: number
    conditions: string[]
    timestamp: string
  }>
  volatility_patterns: any[]
  liquidation_patterns: any[]
  sentiment_patterns: any[]
  correlation_data: any
}

export interface AutomatedInsight {
  id: string
  type: 'liquidation_alert' | 'win_rate_prediction' | 'market_sentiment' | 'risk_warning'
  symbol: string
  data: any
  confidence: number
  timestamp: string
  automated: boolean
  sources: string[]
}

export interface TradingTip {
  id: string
  symbol: string
  type: 'liquidation' | 'technical' | 'sentiment' | 'risk_management'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'
  title: string
  message: string
  analysis: string
  actionable_insights: string[]
  automated: boolean
  confidence: number
  zmarty_context?: string
  expires_at?: string
  timestamp: string
}

export interface CriticalAlert {
  id: string
  symbol: string
  type: string
  data: any
  confidence: number
  automated: boolean
  timestamp: string
}

export interface AutomatedReport {
  id: string
  symbol: string
  timestamp: string
  automated: boolean
  kingfisher_insights: any
  market_data: any
  cryptometer_data?: any
  executive_summary: string
  risk_assessment: any
  trading_recommendations: any[]
  confidence_score: number
}

// Enhanced Supabase Service with MCP Integration
export const supabaseService = {
  // Re-export existing services
  tradingSignals: tradingSignalsService,
  marketData: marketDataService,
  userPositions: userPositionsService,
  chat: chatService,
  userSettings: userSettingsService,
  serviceRegistry: serviceRegistryService,

  // Enhanced initialization with real-time subscriptions
  async initializeRealTimeSubscriptions(tables: string[]): Promise<void> {
    console.log('🔄 Initializing real-time subscriptions for:', tables.join(', '))

    for (const table of tables) {
      try {
        supabase
          .channel(`realtime_${table}`)
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: table
            },
            (payload) => {
              console.log(`📡 Real-time update for ${table}:`, payload)
              // Dispatch custom events for components to listen
              window.dispatchEvent(new CustomEvent(`supabase_${table}_update`, {
                detail: payload
              }))
            }
          )
          .subscribe()
      } catch (error) {
        console.warn(`Failed to subscribe to ${table}:`, error)
      }
    }
  },

  // Memory Adapter Support
  async createMemoryEntry(entry: MemoryEntry): Promise<MemoryEntry> {
    try {
      const { data, error } = await supabase
        .from('memory_entries')
        .insert([entry])
        .select()
        .single()
      
      if (error) {
        // Return the original entry if database save fails
        return entry
      }
      
      return data
    } catch (error) {
      // Silently handle database issues and return original entry
      return entry
    }
  },

  async searchMemories(query: string, type?: string, symbol?: string, limit: number = 10): Promise<MemoryEntry[]> {
    try {
      let queryBuilder = supabase
        .from('memory_entries')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(limit)

      if (type) {
        queryBuilder = queryBuilder.eq('type', type)
      }
      
      if (symbol) {
        queryBuilder = queryBuilder.eq('symbol', symbol)
      }

      // Simple text search in content
      if (query) {
        queryBuilder = queryBuilder.ilike('content', `%${query}%`)
      }

      const { data, error } = await queryBuilder

      if (error) {
        // Return empty array if table doesn't exist or other errors
        return []
      }

      return data || []
    } catch (error) {
      // Silently handle any database connection issues
      return []
    }
  },

  async getRecentMemories(limit: number = 1000): Promise<MemoryEntry[]> {
    try {
      const { data, error } = await supabase
        .from('memory_entries')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(limit)

      if (error) {
        // Return empty array if table doesn't exist or other errors
        return []
      }

      return data || []
    } catch (error) {
      // Silently handle any database connection issues
      return []
    }
  },

  async updateMemoryOutcome(memoryId: string, outcome: any): Promise<void> {
    const { error } = await supabase
      .from('memory_entries')
      .update({ 
        metadata: supabase.rpc('jsonb_set', {
          target: supabase.raw('metadata'),
          path: '{outcome}',
          new_value: JSON.stringify(outcome)
        })
      })
      .eq('id', memoryId)

    if (error) {
      console.error('Error updating memory outcome:', error)
      throw error
    }
  },

  async cleanupExpiredMemories(retentionDate: string): Promise<void> {
    const now = new Date().toISOString()
    
    const { error } = await supabase
      .from('memory_entries')
      .delete()
      .or(`expires_at.lt.${now},timestamp.lt.${retentionDate}`)

    if (error) {
      console.error('Error cleaning up expired memories:', error)
      throw error
    }
  },

  // Conversation Memory Support
  async updateConversationMemory(conversation: ConversationMemory): Promise<void> {
    const { error } = await supabase
      .from('conversation_memory')
      .upsert([conversation])

    if (error) {
      console.error('Error updating conversation memory:', error)
      throw error
    }
  },

  async getConversationMemory(userId: string, sessionId: string): Promise<ConversationMemory | null> {
    const { data, error } = await supabase
      .from('conversation_memory')
      .select('*')
      .eq('user_id', userId)
      .eq('session_id', sessionId)
      .single()

    if (error && error.code !== 'PGRST116') {
      console.error('Error getting conversation memory:', error)
      throw error
    }

    return data
  },

  // Trading Memory Support
  async updateTradingMemory(tradingMemory: TradingMemory): Promise<void> {
    const { error } = await supabase
      .from('trading_memory')
      .upsert([tradingMemory])

    if (error) {
      console.error('Error updating trading memory:', error)
      throw error
    }
  },

  async getTradingMemory(symbol: string): Promise<TradingMemory | null> {
    const { data, error } = await supabase
      .from('trading_memory')
      .select('*')
      .eq('symbol', symbol)
      .single()

    if (error && error.code !== 'PGRST116') {
      console.error('Error getting trading memory:', error)
      throw error
    }

    return data
  },

  // Market Memory Support
  async updateMarketMemory(marketMemory: MarketMemory): Promise<void> {
    const { error } = await supabase
      .from('market_memory')
      .upsert([marketMemory])

    if (error) {
      console.error('Error updating market memory:', error)
      throw error
    }
  },

  async getMarketMemory(symbol: string): Promise<MarketMemory | null> {
    const { data, error } = await supabase
      .from('market_memory')
      .select('*')
      .eq('symbol', symbol)
      .single()

    if (error && error.code !== 'PGRST116') {
      console.error('Error getting market memory:', error)
      throw error
    }

    return data
  },

  // Automated Insights Support
  async createAutomatedInsight(insight: AutomatedInsight): Promise<AutomatedInsight> {
    const { data, error } = await supabase
      .from('automated_insights')
      .insert([insight])
      .select()
      .single()
    
    if (error) {
      console.error('Error creating automated insight:', error)
      throw error
    }
    
    return data
  },

  async getAutomatedInsights(limit: number = 50): Promise<AutomatedInsight[]> {
    const { data, error } = await supabase
      .from('automated_insights')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (error) {
      console.error('Error getting automated insights:', error)
      throw error
    }

    return data || []
  },

  async getAutomatedInsightsBySymbol(symbol: string, limit: number = 20): Promise<AutomatedInsight[]> {
    const { data, error } = await supabase
      .from('automated_insights')
      .select('*')
      .eq('symbol', symbol)
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (error) {
      console.error('Error getting automated insights by symbol:', error)
      throw error
    }

    return data || []
  },

  // Trading Tips Support
  async createTradingTip(tip: TradingTip): Promise<TradingTip> {
    const { data, error } = await supabase
      .from('trading_tips')
      .insert([tip])
      .select()
      .single()
    
    if (error) {
      console.error('Error creating trading tip:', error)
      throw error
    }
    
    return data
  },

  async getTradingTips(symbol?: string, limit: number = 20): Promise<TradingTip[]> {
    let queryBuilder = supabase
      .from('trading_tips')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (symbol) {
      queryBuilder = queryBuilder.eq('symbol', symbol)
    }

    const { data, error } = await queryBuilder

    if (error) {
      console.error('Error getting trading tips:', error)
      throw error
    }

    return data || []
  },

  async getActiveTradingTips(symbol?: string, limit: number = 10): Promise<TradingTip[]> {
    const now = new Date().toISOString()
    
    let queryBuilder = supabase
      .from('trading_tips')
      .select('*')
      .or(`expires_at.is.null,expires_at.gt.${now}`)
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (symbol) {
      queryBuilder = queryBuilder.eq('symbol', symbol)
    }

    const { data, error } = await queryBuilder

    if (error) {
      console.error('Error getting active trading tips:', error)
      throw error
    }

    return data || []
  },

  // Critical Alerts Support
  async createCriticalAlert(alert: CriticalAlert): Promise<CriticalAlert> {
    const { data, error } = await supabase
      .from('critical_alerts')
      .insert([alert])
      .select()
      .single()
    
    if (error) {
      console.error('Error creating critical alert:', error)
      throw error
    }
    
    return data
  },

  async getCriticalAlerts(limit: number = 20): Promise<CriticalAlert[]> {
    const { data, error } = await supabase
      .from('critical_alerts')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (error) {
      console.error('Error getting critical alerts:', error)
      throw error
    }

    return data || []
  },

  async getActiveCriticalAlerts(): Promise<CriticalAlert[]> {
    // Get alerts from the last 24 hours
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
    
    const { data, error } = await supabase
      .from('critical_alerts')
      .select('*')
      .gte('timestamp', yesterday)
      .order('timestamp', { ascending: false })

    if (error) {
      console.error('Error getting active critical alerts:', error)
      throw error
    }

    return data || []
  },

  // Automated Reports Support
  async createAutomatedReport(report: AutomatedReport): Promise<AutomatedReport> {
    const { data, error } = await supabase
      .from('automated_reports')
      .insert([report])
      .select()
      .single()
    
    if (error) {
      console.error('Error creating automated report:', error)
      throw error
    }
    
    return data
  },

  async getAutomatedReports(symbol?: string, limit: number = 10): Promise<AutomatedReport[]> {
    let queryBuilder = supabase
      .from('automated_reports')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (symbol) {
      queryBuilder = queryBuilder.eq('symbol', symbol)
    }

    const { data, error } = await queryBuilder

    if (error) {
      console.error('Error getting automated reports:', error)
      throw error
    }

    return data || []
  },

  async getLatestAutomatedReport(symbol: string): Promise<AutomatedReport | null> {
    const { data, error } = await supabase
      .from('automated_reports')
      .select('*')
      .eq('symbol', symbol)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single()

    if (error && error.code !== 'PGRST116') {
      console.error('Error getting latest automated report:', error)
      throw error
    }

    return data
  },

  // Enhanced Market Data Support
  async updateMarketData(marketData: Partial<MarketData> & { symbol: string }): Promise<void> {
    const { error } = await supabase
      .from('market_data')
      .upsert([{
        id: `${marketData.symbol}_${Date.now()}`,
        timestamp: new Date().toISOString(),
        ...marketData
      }])

    if (error) {
      console.error('Error updating market data:', error)
      throw error
    }
  },

  async getLatestMarketData(symbol: string): Promise<MarketData | null> {
    const { data, error } = await supabase
      .from('market_data')
      .select('*')
      .eq('symbol', symbol)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single()

    if (error && error.code !== 'PGRST116') {
      console.error('Error getting latest market data:', error)
      return null
    }

    return data
  },

  async getMarketDataHistory(symbol: string, limit: number = 100): Promise<MarketData[]> {
    const { data, error } = await supabase
      .from('market_data')
      .select('*')
      .eq('symbol', symbol)
      .order('timestamp', { ascending: false })
      .limit(limit)

    if (error) {
      console.error('Error getting market data history:', error)
      throw error
    }

    return data || []
  },

  // Enhanced Chat Support with MCP Integration
  async createChatMessage(message: ChatMessage): Promise<ChatMessage> {
    const { data, error } = await supabase
      .from('chat_messages')
      .insert([{
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        created_at: new Date().toISOString(),
        ...message
      }])
      .select()
      .single()
    
    if (error) {
      console.error('Error creating chat message:', error)
      throw error
    }
    
    return data
  },

  async getChatHistory(userId: string, sessionId?: string, limit: number = 100): Promise<ChatMessage[]> {
    let queryBuilder = supabase
      .from('chat_messages')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: true })
      .limit(limit)

    if (sessionId) {
      queryBuilder = queryBuilder.eq('metadata->>session_id', sessionId)
    }

    const { data, error } = await queryBuilder

    if (error) {
      console.error('Error getting chat history:', error)
      throw error
    }

    return data || []
  },

  // Real-time Subscriptions with Enhanced Event Handling
  subscribeToRealTimeUpdates(table: string, filter?: string, callback?: (payload: any) => void) {
    const channelName = `realtime_${table}_${Date.now()}`
    
    let subscription = supabase
      .channel(channelName)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: table,
          ...(filter ? { filter } : {})
        },
        (payload) => {
          console.log(`📡 Real-time ${table} update:`, payload)
          
          // Custom callback
          if (callback) {
            callback(payload)
          }
          
          // Global event dispatch
          window.dispatchEvent(new CustomEvent(`supabase_${table}_update`, {
            detail: payload
          }))
        }
      )

    subscription.subscribe((status) => {
      console.log(`📡 Subscription status for ${table}:`, status)
    })

    return subscription
  },

  // Analytics and Statistics
  async getDashboardStats(userId: string): Promise<any> {
    // Parallel queries for dashboard statistics
    const [
      tradingSignals,
      userPositions,
      automatedInsights,
      tradingTips,
      criticalAlerts
    ] = await Promise.all([
      supabase.from('trading_signals').select('*', { count: 'exact' }).eq('user_id', userId),
      supabase.from('user_positions').select('*', { count: 'exact' }).eq('user_id', userId),
      supabase.from('automated_insights').select('*', { count: 'exact' }),
      supabase.from('trading_tips').select('*', { count: 'exact' }),
      supabase.from('critical_alerts').select('*', { count: 'exact' })
        .gte('timestamp', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
    ])

    return {
      user_id: userId,
      trading_signals_count: tradingSignals.count || 0,
      user_positions_count: userPositions.count || 0,
      automated_insights_count: automatedInsights.count || 0,
      trading_tips_count: tradingTips.count || 0,
      critical_alerts_24h: criticalAlerts.count || 0,
      timestamp: new Date().toISOString()
    }
  },

  async getSystemHealth(): Promise<any> {
    try {
      // Test database connectivity
      const { data, error } = await supabase
        .from('service_registry')
        .select('count')
        .limit(1)

      return {
        database_connected: !error,
        timestamp: new Date().toISOString(),
        error: error?.message || null
      }
    } catch (error: any) {
      return {
        database_connected: false,
        timestamp: new Date().toISOString(),
        error: error.message
      }
    }
  },

  // Batch Operations for Performance
  async batchInsert(table: string, records: any[]): Promise<any[]> {
    const { data, error } = await supabase
      .from(table)
      .insert(records)
      .select()

    if (error) {
      console.error(`Error batch inserting to ${table}:`, error)
      throw error
    }

    return data || []
  },

  async batchUpdate(table: string, updates: Array<{ id: string, data: any }>): Promise<any[]> {
    const results = []
    
    // Process in chunks of 100
    for (let i = 0; i < updates.length; i += 100) {
      const chunk = updates.slice(i, i + 100)
      
      const promises = chunk.map(update =>
        supabase
          .from(table)
          .update(update.data)
          .eq('id', update.id)
          .select()
          .single()
      )
      
      const chunkResults = await Promise.all(promises)
      results.push(...chunkResults.map(r => r.data).filter(Boolean))
    }
    
    return results
  }
}

export default supabaseService