import { supabaseService } from './supabaseEnhanced'

interface MemoryEntry {
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
  }
  timestamp: string
  expires_at?: string
  embeddings?: number[]
  relevance_score?: number
}

interface ConversationMemory {
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

interface TradingMemory {
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

interface MarketMemory {
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

class MemoryAdapter {
  private memoryCache: Map<string, MemoryEntry[]> = new Map()
  private conversationCache: Map<string, ConversationMemory> = new Map()
  private tradingMemoryCache: Map<string, TradingMemory> = new Map()
  private marketMemoryCache: Map<string, MarketMemory> = new Map()
  
  private readonly MEMORY_RETENTION_DAYS = 90
  private readonly MAX_CACHE_SIZE = 10000
  private readonly SIMILARITY_THRESHOLD = 0.75

  constructor() {
    this.initializeMemorySystem()
  }

  // 🧠 Initialize Memory System
  private async initializeMemorySystem(): Promise<void> {
    console.log('🧠 Initializing Advanced Memory Adapter...')
    
    try {
      // Load recent memories from Supabase
      await this.loadRecentMemories()
      
      // Initialize memory cleanup
      this.startMemoryCleanup()
      
      // Start memory optimization
      this.startMemoryOptimization()
      
      console.log('✅ Memory Adapter initialized successfully')
    } catch (error) {
      console.error('❌ Memory Adapter initialization failed:', error)
    }
  }

  // 💾 Store Memory Entry
  async storeMemory(entry: Omit<MemoryEntry, 'id' | 'timestamp'>): Promise<string> {
    const memoryEntry: MemoryEntry = {
      id: `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      ...entry
    }

    // Store in cache for fast access
    const cacheKey = `${entry.type}_${entry.symbol || 'global'}`
    if (!this.memoryCache.has(cacheKey)) {
      this.memoryCache.set(cacheKey, [])
    }
    this.memoryCache.get(cacheKey)!.push(memoryEntry)

    // Store in Supabase for persistence
    try {
      await supabaseService.createMemoryEntry(memoryEntry)
      console.log(`💾 Memory stored: ${memoryEntry.type} - ${memoryEntry.id}`)
    } catch (error) {
      // Silently handle Supabase connection issues - memory still works locally
    }

    // Maintain cache size
    this.pruneCache()

    return memoryEntry.id
  }

  // 🔍 Retrieve Relevant Memories
  async getRelevantMemories(
    query: string, 
    type?: MemoryEntry['type'], 
    symbol?: string,
    limit: number = 10
  ): Promise<MemoryEntry[]> {
    
    // Search in cache first
    let relevantMemories: MemoryEntry[] = []
    
    this.memoryCache.forEach((memories, key) => {
      memories.forEach(memory => {
        if (type && memory.type !== type) return
        if (symbol && memory.symbol !== symbol) return
        
        // Calculate relevance score based on content similarity
        const relevanceScore = this.calculateRelevance(query, memory.content, memory.metadata.context_tags)
        
        if (relevanceScore > this.SIMILARITY_THRESHOLD) {
          memory.relevance_score = relevanceScore
          relevantMemories.push(memory)
        }
      })
    })

    // Sort by relevance and recency
    relevantMemories.sort((a, b) => {
      const relevanceDiff = (b.relevance_score || 0) - (a.relevance_score || 0)
      if (relevanceDiff !== 0) return relevanceDiff
      
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    })

    // If cache doesn't have enough results, query Supabase
    if (relevantMemories.length < limit) {
      try {
        const dbMemories = await supabaseService.searchMemories(query, type, symbol, limit)
        
        // Merge and deduplicate
        const existingIds = new Set(relevantMemories.map(m => m.id))
        const newMemories = dbMemories.filter((m: MemoryEntry) => !existingIds.has(m.id))
        
        relevantMemories = [...relevantMemories, ...newMemories].slice(0, limit)
      } catch (error) {
        console.error('Failed to search memories in database:', error)
      }
    }

    return relevantMemories.slice(0, limit)
  }

  // 💬 Conversation Memory Management
  async storeConversation(
    userId: string, 
    sessionId: string, 
    message: { role: 'user' | 'assistant', content: string, metadata?: any }
  ): Promise<void> {
    
    const cacheKey = `${userId}_${sessionId}`
    let conversation = this.conversationCache.get(cacheKey)
    
    if (!conversation) {
      conversation = {
        user_id: userId,
        session_id: sessionId,
        messages: [],
        context_summary: '',
        trading_preferences: {},
        last_updated: new Date().toISOString()
      }
    }

    // Add new message
    conversation.messages.push({
      ...message,
      timestamp: new Date().toISOString()
    })

    // Update context summary every 10 messages
    if (conversation.messages.length % 10 === 0) {
      conversation.context_summary = await this.generateContextSummary(conversation.messages)
    }

    // Extract trading preferences from conversation
    if (message.role === 'user') {
      const preferences = this.extractTradingPreferences(message.content)
      conversation.trading_preferences = { ...conversation.trading_preferences, ...preferences }
    }

    conversation.last_updated = new Date().toISOString()
    this.conversationCache.set(cacheKey, conversation)

    // Store conversation memory
    await this.storeMemory({
      type: 'conversation',
      content: message.content,
      metadata: {
        user_id: userId,
        session_id: sessionId,
        confidence: 1.0,
        source: 'chat',
        automated: false,
        context_tags: ['conversation', `role_${message.role}`, sessionId]
      }
    })

    // Persist to database
    try {
      await supabaseService.updateConversationMemory(conversation)
    } catch (error) {
      console.error('Failed to persist conversation memory:', error)
    }
  }

  // 📈 Trading Decision Memory
  async storeTradingDecision(
    symbol: string,
    decision: 'buy' | 'sell' | 'hold',
    reasoning: string,
    confidence: number,
    userId?: string
  ): Promise<void> {
    
    let tradingMemory = this.tradingMemoryCache.get(symbol)
    
    if (!tradingMemory) {
      tradingMemory = {
        symbol,
        historical_decisions: [],
        learned_patterns: [],
        success_rate: 0,
        risk_tolerance: 0.5,
        preferred_strategies: []
      }
    }

    // Add new decision
    tradingMemory.historical_decisions.push({
      decision,
      reasoning,
      confidence,
      timestamp: new Date().toISOString()
    })

    // Update learned patterns
    const patterns = this.extractPatterns(reasoning)
    tradingMemory.learned_patterns = [...new Set([...tradingMemory.learned_patterns, ...patterns])]

    // Calculate success rate (will be updated when outcomes are known)
    const completedDecisions = tradingMemory.historical_decisions.filter(d => d.outcome)
    const successfulDecisions = completedDecisions.filter(d => d.outcome === 'profitable')
    tradingMemory.success_rate = completedDecisions.length > 0 
      ? successfulDecisions.length / completedDecisions.length 
      : 0

    this.tradingMemoryCache.set(symbol, tradingMemory)

    // Store as memory entry
    await this.storeMemory({
      type: 'trading_decision',
      symbol,
      content: `Decision: ${decision.toUpperCase()} ${symbol} - ${reasoning}`,
      metadata: {
        user_id: userId,
        session_id: `trading_${Date.now()}`,
        confidence,
        source: 'trading_engine',
        automated: true,
        context_tags: ['trading', symbol, decision, `confidence_${Math.round(confidence * 10)}`]
      }
    })

    // Persist to database
    try {
      await supabaseService.updateTradingMemory(tradingMemory)
    } catch (error) {
      console.error('Failed to persist trading memory:', error)
    }
  }

  // 📊 Market Analysis Memory
  async storeMarketAnalysis(
    symbol: string,
    analysis: string,
    patterns: any[],
    confidence: number,
    source: string = 'market_analyzer'
  ): Promise<void> {
    
    let marketMemory = this.marketMemoryCache.get(symbol)
    
    if (!marketMemory) {
      marketMemory = {
        symbol,
        price_patterns: [],
        volatility_patterns: [],
        liquidation_patterns: [],
        sentiment_patterns: [],
        correlation_data: {}
      }
    }

    // Process and categorize patterns
    patterns.forEach(pattern => {
      if (pattern.type === 'price') {
        marketMemory!.price_patterns.push({
          pattern_type: pattern.pattern_type,
          description: pattern.description,
          success_rate: pattern.success_rate || 0,
          conditions: pattern.conditions || [],
          timestamp: new Date().toISOString()
        })
      } else if (pattern.type === 'volatility') {
        marketMemory!.volatility_patterns.push(pattern)
      } else if (pattern.type === 'liquidation') {
        marketMemory!.liquidation_patterns.push(pattern)
      } else if (pattern.type === 'sentiment') {
        marketMemory!.sentiment_patterns.push(pattern)
      }
    })

    this.marketMemoryCache.set(symbol, marketMemory)

    // Store as memory entry
    await this.storeMemory({
      type: 'market_analysis',
      symbol,
      content: analysis,
      metadata: {
        session_id: `market_${Date.now()}`,
        confidence,
        source,
        automated: true,
        context_tags: ['market_analysis', symbol, source, ...patterns.map(p => p.type)]
      }
    })

    // Persist to database
    try {
      await supabaseService.updateMarketMemory(marketMemory)
    } catch (error) {
      console.error('Failed to persist market memory:', error)
    }
  }

  // 🤖 AI Learning Memory
  async storeAILearning(
    content: string,
    learning_type: string,
    confidence: number,
    source: string,
    metadata: any = {}
  ): Promise<void> {
    
    await this.storeMemory({
      type: 'ai_learning',
      content,
      metadata: {
        session_id: `ai_learning_${Date.now()}`,
        confidence,
        source,
        automated: true,
        context_tags: ['ai_learning', learning_type, source, ...Object.keys(metadata)]
      }
    })
  }

  // 🔄 Update Memory Outcome
  async updateMemoryOutcome(memoryId: string, outcome: any): Promise<void> {
    try {
      await supabaseService.updateMemoryOutcome(memoryId, outcome)
      
      // Update cache if present
      this.memoryCache.forEach(memories => {
        const memory = memories.find(m => m.id === memoryId)
        if (memory) {
          memory.metadata = { ...memory.metadata, outcome }
        }
      })
      
      console.log(`📊 Memory outcome updated: ${memoryId}`)
    } catch (error) {
      console.error('Failed to update memory outcome:', error)
    }
  }

  // 🧹 Memory Cleanup and Optimization
  private startMemoryCleanup(): void {
    // Clean up expired memories every hour
    setInterval(async () => {
      await this.cleanupExpiredMemories()
    }, 60 * 60 * 1000)

    console.log('🧹 Memory cleanup started')
  }

  private startMemoryOptimization(): void {
    // Optimize memory every 30 minutes
    setInterval(async () => {
      await this.optimizeMemory()
    }, 30 * 60 * 1000)

    console.log('⚡ Memory optimization started')
  }

  private async cleanupExpiredMemories(): Promise<void> {
    const now = new Date()
    const retentionDate = new Date(now.getTime() - (this.MEMORY_RETENTION_DAYS * 24 * 60 * 60 * 1000))

    // Clean cache
    this.memoryCache.forEach((memories, key) => {
      const filteredMemories = memories.filter(memory => {
        if (memory.expires_at && new Date(memory.expires_at) < now) {
          return false
        }
        if (new Date(memory.timestamp) < retentionDate) {
          return false
        }
        return true
      })
      
      if (filteredMemories.length !== memories.length) {
        this.memoryCache.set(key, filteredMemories)
      }
    })

    // Clean database
    try {
      await supabaseService.cleanupExpiredMemories(retentionDate.toISOString())
      console.log('🧹 Expired memories cleaned up')
    } catch (error) {
      console.error('Memory cleanup failed:', error)
    }
  }

  private async optimizeMemory(): Promise<void> {
    // Consolidate similar memories
    // Update relevance scores
    // Compress old memories
    console.log('⚡ Memory optimization completed')
  }

  private pruneCache(): void {
    let totalEntries = 0
    this.memoryCache.forEach(memories => {
      totalEntries += memories.length
    })

    if (totalEntries > this.MAX_CACHE_SIZE) {
      // Remove oldest entries
      this.memoryCache.forEach((memories, key) => {
        if (memories.length > 100) {
          const sorted = memories.sort((a, b) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          )
          this.memoryCache.set(key, sorted.slice(0, 100))
        }
      })
    }
  }

  // 🧮 Utility Methods
  private calculateRelevance(query: string, content: string, tags: string[]): number {
    const queryWords = query.toLowerCase().split(/\s+/)
    const contentWords = content.toLowerCase().split(/\s+/)
    
    let relevanceScore = 0
    
    // Word matching
    queryWords.forEach(word => {
      if (contentWords.includes(word)) {
        relevanceScore += 0.1
      }
    })
    
    // Tag matching
    tags.forEach(tag => {
      if (queryWords.some(word => tag.toLowerCase().includes(word))) {
        relevanceScore += 0.2
      }
    })
    
    // Content similarity (simplified)
    const commonWords = queryWords.filter(word => contentWords.includes(word))
    relevanceScore += (commonWords.length / queryWords.length) * 0.5
    
    return Math.min(relevanceScore, 1.0)
  }

  private async generateContextSummary(messages: Array<{role: string, content: string}>): Promise<string> {
    // Generate a summary of the conversation context
    const recentMessages = messages.slice(-20) // Last 20 messages
    const userMessages = recentMessages.filter(m => m.role === 'user')
    const topics = this.extractTopics(userMessages.map(m => m.content).join(' '))
    
    return `Recent conversation topics: ${topics.join(', ')}`
  }

  private extractTradingPreferences(content: string): any {
    const preferences: any = {}
    
    // Extract risk tolerance
    if (/conservative|safe|low.risk/i.test(content)) {
      preferences.risk_tolerance = 'low'
    } else if (/aggressive|high.risk|risky/i.test(content)) {
      preferences.risk_tolerance = 'high'
    }
    
    // Extract preferred assets
    const symbols = content.match(/[A-Z]{3,6}(?:USDT|USD|BTC|ETH)/g)
    if (symbols) {
      preferences.preferred_symbols = symbols
    }
    
    // Extract strategies
    if (/scalp/i.test(content)) preferences.strategies = ['scalping']
    if (/swing/i.test(content)) preferences.strategies = ['swing_trading']
    if (/hold|hodl/i.test(content)) preferences.strategies = ['holding']
    
    return preferences
  }

  private extractPatterns(reasoning: string): string[] {
    const patterns: string[] = []
    
    // Extract common trading patterns from reasoning
    if (/support|resistance/i.test(reasoning)) patterns.push('support_resistance')
    if (/breakout/i.test(reasoning)) patterns.push('breakout')
    if (/reversal/i.test(reasoning)) patterns.push('reversal')
    if (/trend/i.test(reasoning)) patterns.push('trend_following')
    if (/liquidation/i.test(reasoning)) patterns.push('liquidation_based')
    if (/volume/i.test(reasoning)) patterns.push('volume_analysis')
    
    return patterns
  }

  private extractTopics(text: string): string[] {
    // Simple topic extraction
    const topics: string[] = []
    const words = text.toLowerCase().split(/\s+/)
    
    // Trading related topics
    if (words.some(w => ['bitcoin', 'btc'].includes(w))) topics.push('Bitcoin')
    if (words.some(w => ['ethereum', 'eth'].includes(w))) topics.push('Ethereum')
    if (words.some(w => ['trading', 'trade'].includes(w))) topics.push('Trading')
    if (words.some(w => ['analysis', 'analyze'].includes(w))) topics.push('Analysis')
    if (words.some(w => ['price', 'chart'].includes(w))) topics.push('Price Analysis')
    
    return topics
  }

  private async loadRecentMemories(): Promise<void> {
    try {
      // Load recent memories from Supabase into cache
      const recentMemories = await supabaseService.getRecentMemories(1000) // Last 1000 memories
      
      recentMemories.forEach((memory: MemoryEntry) => {
        const cacheKey = `${memory.type}_${memory.symbol || 'global'}`
        if (!this.memoryCache.has(cacheKey)) {
          this.memoryCache.set(cacheKey, [])
        }
        this.memoryCache.get(cacheKey)!.push(memory)
      })
      
      console.log(`📚 Loaded ${recentMemories.length} recent memories into cache`)
    } catch (error) {
      // Silently handle Supabase connection issues - continue with local cache
    }
  }

  // 📊 Get Memory Statistics
  getMemoryStatistics(): any {
    let totalMemories = 0
    const typeDistribution: { [key: string]: number } = {}
    
    this.memoryCache.forEach(memories => {
      totalMemories += memories.length
      
      memories.forEach(memory => {
        typeDistribution[memory.type] = (typeDistribution[memory.type] || 0) + 1
      })
    })
    
    return {
      total_cached_memories: totalMemories,
      type_distribution: typeDistribution,
      conversation_sessions: this.conversationCache.size,
      trading_symbols: this.tradingMemoryCache.size,
      market_symbols: this.marketMemoryCache.size,
      cache_utilization: `${Math.round((totalMemories / this.MAX_CACHE_SIZE) * 100)}%`
    }
  }

  // 🔍 Search Memories with Advanced Filtering
  async searchMemories(
    query: string,
    filters: {
      type?: MemoryEntry['type']
      symbol?: string
      dateRange?: { start: string, end: string }
      minConfidence?: number
      source?: string
      tags?: string[]
    } = {},
    limit: number = 50
  ): Promise<MemoryEntry[]> {
    
    let results = await this.getRelevantMemories(query, filters.type, filters.symbol, limit * 2)
    
    // Apply additional filters
    results = results.filter(memory => {
      if (filters.dateRange) {
        const memoryDate = new Date(memory.timestamp)
        const startDate = new Date(filters.dateRange.start)
        const endDate = new Date(filters.dateRange.end)
        if (memoryDate < startDate || memoryDate > endDate) return false
      }
      
      if (filters.minConfidence && memory.metadata.confidence < filters.minConfidence) {
        return false
      }
      
      if (filters.source && memory.metadata.source !== filters.source) {
        return false
      }
      
      if (filters.tags && !filters.tags.some(tag => 
        memory.metadata.context_tags.includes(tag)
      )) {
        return false
      }
      
      return true
    })
    
    return results.slice(0, limit)
  }

  // 🎯 Get User Context
  async getUserContext(userId: string, symbol?: string): Promise<any> {
    const conversations = await this.searchMemories('', {
      type: 'conversation',
      source: 'chat'
    }, 100)
    
    const userConversations = conversations.filter(m => m.metadata.user_id === userId)
    
    const tradingDecisions = await this.searchMemories('', {
      type: 'trading_decision',
      symbol
    }, 50)
    
    return {
      user_id: userId,
      recent_conversations: userConversations.slice(0, 10),
      trading_history: tradingDecisions.slice(0, 20),
      preferences: this.extractUserPreferences(userConversations),
      statistics: {
        total_conversations: userConversations.length,
        total_trading_decisions: tradingDecisions.length,
        active_symbols: [...new Set(tradingDecisions.map(d => d.symbol).filter(Boolean))]
      }
    }
  }

  private extractUserPreferences(conversations: MemoryEntry[]): any {
    // Analyze conversation history to extract user preferences
    const allContent = conversations.map(c => c.content).join(' ')
    return this.extractTradingPreferences(allContent)
  }
}

// Export singleton instance
export const memoryAdapter = new MemoryAdapter()
export default memoryAdapter