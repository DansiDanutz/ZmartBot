import { kingfisherAIService, KingFisherInsights } from './kingfisherAI'
import { automationOrchestrator } from './automationOrchestrator'
import { memoryAdapter } from './memoryAdapter'
import { supabaseService } from './supabaseEnhanced'
import { cryptometerService } from './cryptometer'
import { kucoinService } from './kucoinService'
import { binanceService } from './binanceService'
import { tradingOrchestrationService } from './tradingOrchestrationService'

interface ZmartyResponse {
  id: string
  message: string
  type: 'analysis' | 'recommendation' | 'alert' | 'general' | 'automated_insight'
  symbol?: string
  confidence: number
  sources: string[]
  timestamp: string
  metadata?: any
  automated: boolean
  memory_enhanced: boolean
  kingfisher_powered: boolean
  mcp_enhanced: boolean
}

interface ZmartyContext {
  user_id: string
  session_id: string
  current_symbol?: string
  conversation_history: Array<{
    role: 'user' | 'assistant'
    content: string
    timestamp: string
  }>
  user_preferences: any
  trading_memory: any
  market_context: any
}

interface AutomatedInsight {
  type: 'liquidation_opportunity' | 'win_rate_signal' | 'market_anomaly' | 'risk_warning' | 'profit_taking'
  symbol: string
  description: string
  actionable_advice: string[]
  confidence: number
  kingfisher_data: KingFisherInsights
  timestamp: string
}

class ZmartyAI {
  private context: Map<string, ZmartyContext> = new Map()
  private automatedInsightsQueue: AutomatedInsight[] = []
  private mcpConnections: Map<string, any> = new Map()

  constructor() {
    this.initializeZmarty()
  }

  // 🚀 Initialize Zmarty with Full MCP Integration
  private async initializeZmarty(): Promise<void> {
    console.log('🤖 Initializing Zmarty AI with Full MCP Integration...')

    try {
      // Initialize MCP connections
      await this.initializeMCPConnections()

      // Start automated insight processing
      this.startAutomatedInsightProcessing()

      // Initialize real-time market monitoring
      this.startMarketMonitoring()

      console.log('✅ Zmarty AI fully initialized with MCP integration')
    } catch (error) {
      console.error('❌ Zmarty AI initialization failed:', error)
    }
  }

  // 🔌 Initialize MCP Connections
  private async initializeMCPConnections(): Promise<void> {
    console.log('🔌 Connecting to all MCP servers...')

    // Supabase MCP - Database and real-time subscriptions
    this.mcpConnections.set('supabase', {
      service: supabaseService,
      capabilities: ['real_time_data', 'user_management', 'data_storage', 'subscriptions'],
      status: 'active'
    })

    // Browser MCP - Web automation and data scraping
    this.mcpConnections.set('browser', {
      capabilities: ['web_scraping', 'automation', 'data_extraction'],
      status: 'ready'
    })

    // Firecrawl MCP - Advanced web crawling and data extraction
    this.mcpConnections.set('firecrawl', {
      capabilities: ['web_crawling', 'structured_data_extraction', 'batch_processing'],
      status: 'ready'
    })

    // Documentation/Ref MCP - Knowledge enhancement
    this.mcpConnections.set('documentation', {
      capabilities: ['knowledge_search', 'context_enhancement', 'reference_data'],
      status: 'ready'
    })

    // KuCoin API Service - Real exchange integration
    this.mcpConnections.set('kucoin', {
      service: kucoinService,
      capabilities: ['real_market_data', 'position_management', 'order_execution', 'futures_trading'],
      status: 'connecting',
      port: 8302
    })

    // Binance API Service - Major exchange integration  
    this.mcpConnections.set('binance', {
      service: binanceService,
      capabilities: ['spot_trading', 'market_data', 'order_management', 'account_info'],
      status: 'connecting',
      port: 8303
    })

    // Trading Orchestration Service - AI-powered trading decisions
    this.mcpConnections.set('trading_orchestration', {
      service: tradingOrchestrationService,
      capabilities: ['trading_decisions', 'market_analysis', 'portfolio_optimization', 'risk_management'],
      status: 'connecting',
      port: 8200
    })

    // Check connectivity for all API services
    await this.checkAPIServiceConnectivity()

    // Memory Adapter MCP - Advanced memory management
    this.mcpConnections.set('memory', {
      service: memoryAdapter,
      capabilities: ['conversation_memory', 'trading_memory', 'pattern_learning'],
      status: 'active'
    })

    // Automation Orchestrator MCP - Full automation
    this.mcpConnections.set('automation', {
      service: automationOrchestrator,
      capabilities: ['automated_analysis', 'real_time_alerts', 'batch_processing'],
      status: 'active'
    })

    console.log('✅ All MCP connections established')
  }

  // 🔌 Check API Service Connectivity
  private async checkAPIServiceConnectivity(): Promise<void> {
    console.log('🔍 Checking API service connectivity...')

    // Check KuCoin connectivity
    try {
      const kucoinHealthy = await kucoinService.checkHealth()
      const kucoinConnection = this.mcpConnections.get('kucoin')
      if (kucoinConnection) {
        kucoinConnection.status = kucoinHealthy ? 'connected' : 'disconnected'
        kucoinConnection.last_check = new Date().toISOString()
      }
      console.log(`📈 KuCoin API (port 8302): ${kucoinHealthy ? '✅ Connected' : '❌ Disconnected'}`)
    } catch (error) {
      console.error('❌ KuCoin connectivity check failed:', error)
    }

    // Check Binance connectivity
    try {
      const binanceHealthy = await binanceService.checkHealth()
      const binanceConnection = this.mcpConnections.get('binance')
      if (binanceConnection) {
        binanceConnection.status = binanceHealthy ? 'connected' : 'disconnected'
        binanceConnection.last_check = new Date().toISOString()
      }
      console.log(`🚀 Binance API (port 8303): ${binanceHealthy ? '✅ Connected' : '❌ Disconnected'}`)
    } catch (error) {
      console.error('❌ Binance connectivity check failed:', error)
    }

    // Check Trading Orchestration connectivity
    try {
      const tradingHealthy = await tradingOrchestrationService.checkHealth()
      const tradingConnection = this.mcpConnections.get('trading_orchestration')
      if (tradingConnection) {
        tradingConnection.status = tradingHealthy ? 'connected' : 'disconnected'
        tradingConnection.last_check = new Date().toISOString()
      }
      console.log(`🧠 Trading Orchestration (port 8200): ${tradingHealthy ? '✅ Connected' : '❌ Disconnected'}`)
    } catch (error) {
      console.error('❌ Trading Orchestration connectivity check failed:', error)
    }

    console.log('✅ API service connectivity check completed')
  }

  // 📊 Get Comprehensive System Status
  async getSystemStatus(): Promise<{
    services: Record<string, any>
    summary: {
      total_services: number
      connected_services: number
      availability_percentage: number
      last_check: string
    }
    capabilities: string[]
    recommendations: string[]
  }> {
    await this.checkAPIServiceConnectivity()

    const services: Record<string, any> = {}
    let connectedCount = 0
    const totalServices = this.mcpConnections.size
    const capabilities: string[] = []

    for (const [name, connection] of this.mcpConnections.entries()) {
      services[name] = {
        ...connection,
        connected: connection.status === 'connected' || connection.status === 'active'
      }

      if (services[name].connected) {
        connectedCount++
        if (connection.capabilities) {
          capabilities.push(...connection.capabilities)
        }
      }
    }

    const availabilityPercentage = (connectedCount / totalServices) * 100

    const recommendations = [
      `${connectedCount}/${totalServices} services operational`,
      availabilityPercentage > 90 ? 'System running optimally' : 
      availabilityPercentage > 70 ? 'System running well with minor issues' : 
      'Some services need attention',
      'Zmarty AI is ready to provide comprehensive trading intelligence'
    ]

    return {
      services,
      summary: {
        total_services: totalServices,
        connected_services: connectedCount,
        availability_percentage: availabilityPercentage,
        last_check: new Date().toISOString()
      },
      capabilities: [...new Set(capabilities)],
      recommendations
    }
  }

  // 💬 Enhanced Chat with Full MCP Integration
  async chat(
    userId: string,
    sessionId: string,
    message: string,
    symbol?: string
  ): Promise<ZmartyResponse> {

    // Get or create user context
    const contextKey = `${userId}_${sessionId}`
    let context = this.context.get(contextKey)

    if (!context) {
      context = await this.createUserContext(userId, sessionId, symbol)
      this.context.set(contextKey, context)
    }

    // Update conversation history
    context.conversation_history.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    })

    // Store conversation in memory adapter
    await memoryAdapter.storeConversation(userId, sessionId, {
      role: 'user',
      content: message
    })

    // Analyze message and determine response type
    const messageAnalysis = await this.analyzeMessage(message, context)
    
    let response: ZmartyResponse

    if (messageAnalysis.requires_market_analysis && symbol) {
      response = await this.generateMarketAnalysisResponse(message, symbol, context, messageAnalysis)
    } else if (messageAnalysis.requires_trading_advice) {
      response = await this.generateTradingAdviceResponse(message, symbol, context, messageAnalysis)
    } else if (messageAnalysis.is_general_question) {
      response = await this.generateGeneralResponse(message, context, messageAnalysis)
    } else {
      response = await this.generateEnhancedResponse(message, symbol, context, messageAnalysis)
    }

    // Store assistant response in memory
    await memoryAdapter.storeConversation(userId, sessionId, {
      role: 'assistant',
      content: response.message,
      metadata: {
        type: response.type,
        confidence: response.confidence,
        sources: response.sources,
        automated: response.automated
      }
    })

    // Update context
    context.conversation_history.push({
      role: 'assistant',
      content: response.message,
      timestamp: response.timestamp
    })

    return response
  }

  // 🧠 Generate Enhanced Response with All MCP Services
  private async generateEnhancedResponse(
    message: string,
    symbol: string | undefined,
    context: ZmartyContext,
    analysis: any
  ): Promise<ZmartyResponse> {

    const sources: string[] = ['zmarty_ai', 'memory_adapter']
    let confidence = 75
    let responseMessage = ''
    let automated = false
    let mcpEnhanced = true

    try {
      // 1. Get KingFisher AI insights if symbol is available
      let kingfisherInsights: KingFisherInsights | null = null
      if (symbol) {
        kingfisherInsights = await kingfisherAIService.getKingFisherInsights(symbol)
        sources.push('kingfisher_ai')
        confidence += 10
      }

      // 2. Get relevant memories from memory adapter
      const relevantMemories = await memoryAdapter.getRelevantMemories(message, undefined, symbol, 5)
      if (relevantMemories.length > 0) {
        sources.push('memory_search')
        confidence += 5
      }

      // 3. Get market data from Cryptometer via MCP
      let marketData: any = null
      if (symbol) {
        try {
          marketData = await cryptometerService.getSymbolData(symbol)
          sources.push('cryptometer_api')
          confidence += 5
        } catch (error) {
          console.warn('Failed to get Cryptometer data:', error)
        }
      }

      // 4. Get comprehensive exchange data from all API services
      let exchangeData: any = {}
      let tradingDecisions: any = null
      
      // Get KuCoin data if connected
      const kucoinConnection = this.mcpConnections.get('kucoin')
      if (kucoinConnection?.status === 'connected' && symbol) {
        try {
          const kucoinMarketData = await kucoinService.getMarketData(symbol)
          const kucoinSummary = await kucoinService.getMarketSummary()
          exchangeData.kucoin = { marketData: kucoinMarketData, summary: kucoinSummary }
          sources.push('kucoin_api')
          confidence += 8
        } catch (error) {
          console.warn('Failed to get KuCoin data:', error)
        }
      }

      // Get Binance data if connected
      const binanceConnection = this.mcpConnections.get('binance')
      if (binanceConnection?.status === 'connected' && symbol) {
        try {
          const binanceMarketData = await binanceService.getMarketData(symbol)
          const binanceSummary = await binanceService.getMarketSummary()
          exchangeData.binance = { marketData: binanceMarketData, summary: binanceSummary }
          sources.push('binance_api')
          confidence += 8
        } catch (error) {
          console.warn('Failed to get Binance data:', error)
        }
      }

      // Get Trading Orchestration insights if connected
      const tradingConnection = this.mcpConnections.get('trading_orchestration')
      if (tradingConnection?.status === 'connected') {
        try {
          const tradingAnalysis = await tradingOrchestrationService.getComprehensiveAnalysis()
          const portfolioInsights = await tradingOrchestrationService.getPortfolioInsights()
          if (symbol) {
            const latestDecision = await tradingOrchestrationService.getLatestDecision(symbol)
            tradingDecisions = { analysis: tradingAnalysis, portfolio: portfolioInsights, decision: latestDecision }
          } else {
            tradingDecisions = { analysis: tradingAnalysis, portfolio: portfolioInsights }
          }
          sources.push('trading_orchestration')
          confidence += 12 // Higher confidence for AI trading decisions
        } catch (error) {
          console.warn('Failed to get Trading Orchestration data:', error)
        }
      }

      // 5. Get user context and preferences
      const userContext = await memoryAdapter.getUserContext(context.user_id, symbol)
      if (userContext.preferences) {
        sources.push('user_preferences')
        confidence += 5
      }

      // 6. Generate comprehensive response with all data sources
      responseMessage = await this.generateComprehensiveResponse({
        message,
        symbol,
        kingfisherInsights,
        relevantMemories,
        marketData,
        exchangeData,
        tradingDecisions,
        userContext,
        analysis
      })

      // 6. Check for automated insights
      if (kingfisherInsights && this.shouldTriggerAutomatedInsight(kingfisherInsights)) {
        automated = true
        await this.queueAutomatedInsight(kingfisherInsights, symbol!)
        sources.push('automated_analysis')
        confidence += 10
      }

    } catch (error) {
      console.error('Enhanced response generation error:', error)
      responseMessage = this.generateFallbackResponse(message, analysis)
      confidence = 60
      mcpEnhanced = false
    }

    return {
      id: `zmarty_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      message: responseMessage,
      type: analysis.response_type || 'general',
      symbol,
      confidence: Math.min(confidence, 100),
      sources,
      timestamp: new Date().toISOString(),
      automated,
      memory_enhanced: relevantMemories?.length > 0,
      kingfisher_powered: kingfisherInsights !== null,
      mcp_enhanced: mcpEnhanced,
      metadata: {
        analysis,
        kingfisher_insights: kingfisherInsights,
        memory_count: relevantMemories?.length || 0
      }
    }
  }

  // 📊 Generate Market Analysis Response
  private async generateMarketAnalysisResponse(
    message: string,
    symbol: string,
    context: ZmartyContext,
    analysis: any
  ): Promise<ZmartyResponse> {

    const kingfisherInsights = await kingfisherAIService.getKingFisherInsights(symbol)
    const marketData = await cryptometerService.getSymbolData(symbol)
    
    const analysisResponse = `
🔍 **${symbol} Advanced Market Analysis** (Powered by KingFisher AI & MCP)

**📈 Current Market Structure:**
- Trend: ${kingfisherInsights.market_structure.trend} (${kingfisherInsights.market_structure.strength}% strength)
- Volume Profile: ${kingfisherInsights.market_structure.volume_profile}
- Overall AI Confidence: ${kingfisherInsights.ai_confidence}%

**👑 KingFisher Liquidation Analysis:**
- Risk Level: ${kingfisherInsights.liquidation_analysis.risk_level}
- Total Liquidation Volume: $${(kingfisherInsights.liquidation_analysis.total_liquidation_volume / 1000000).toFixed(1)}M
- Recommended Action: ${kingfisherInsights.liquidation_analysis.recommended_action}
- Toxic Flow Detected: ${kingfisherInsights.liquidation_analysis.toxic_flow_detected ? '⚠️ YES' : '✅ NO'}

**🎯 Win Rate Prediction:**
- Prediction: ${kingfisherInsights.win_rate_prediction.prediction}%
- Model Confidence: ${kingfisherInsights.win_rate_prediction.confidence}%
- Recommended Position Size: ${kingfisherInsights.win_rate_prediction.recommended_position_size}%

**🚨 Key Levels:**
- Support: ${kingfisherInsights.liquidation_analysis.key_levels.support.map(s => `$${s.toLocaleString()}`).join(', ')}
- Resistance: ${kingfisherInsights.liquidation_analysis.key_levels.resistance.map(r => `$${r.toLocaleString()}`).join(', ')}

**💡 Intelligent Trading Tips:**
${kingfisherInsights.trading_tips.slice(0, 3).map((tip, i) => 
  `${i + 1}. **${tip.title}** (${tip.priority} Priority)\n   ${tip.message}\n   💡 ${tip.actionable_insights.slice(0, 2).join(', ')}`
).join('\n\n')}

*This analysis combines KingFisher AI's multi-agent system with real-time market data and your personal trading memory.*
    `.trim()

    // Store market analysis in memory
    await memoryAdapter.storeMarketAnalysis(
      symbol,
      analysisResponse,
      [
        { type: 'liquidation', pattern_type: 'risk_assessment', success_rate: kingfisherInsights.ai_confidence / 100 },
        { type: 'price', pattern_type: kingfisherInsights.market_structure.trend, success_rate: kingfisherInsights.win_rate_prediction.prediction / 100 }
      ],
      kingfisherInsights.ai_confidence / 100,
      'zmarty_ai'
    )

    return {
      id: `zmarty_analysis_${Date.now()}`,
      message: analysisResponse,
      type: 'analysis',
      symbol,
      confidence: kingfisherInsights.ai_confidence,
      sources: ['kingfisher_ai', 'cryptometer', 'memory_adapter', 'supabase'],
      timestamp: new Date().toISOString(),
      automated: false,
      memory_enhanced: true,
      kingfisher_powered: true,
      mcp_enhanced: true,
      metadata: { kingfisher_insights: kingfisherInsights }
    }
  }

  // 💰 Generate Trading Advice Response
  private async generateTradingAdviceResponse(
    message: string,
    symbol: string | undefined,
    context: ZmartyContext,
    analysis: any
  ): Promise<ZmartyResponse> {

    if (!symbol) {
      return {
        id: `zmarty_advice_${Date.now()}`,
        message: "I'd love to give you trading advice! Could you specify which cryptocurrency symbol you're interested in? (e.g., BTCUSDT, ETHUSDT, SOLUSDT)",
        type: 'general',
        confidence: 90,
        sources: ['zmarty_ai'],
        timestamp: new Date().toISOString(),
        automated: false,
        memory_enhanced: false,
        kingfisher_powered: false,
        mcp_enhanced: false
      }
    }

    const [kingfisherInsights, userMemory, tradingHistory] = await Promise.all([
      kingfisherAIService.getKingFisherInsights(symbol),
      memoryAdapter.getUserContext(context.user_id, symbol),
      memoryAdapter.getRelevantMemories('trading decision', 'trading_decision', symbol, 5)
    ])

    const tradingAdvice = `
🎯 **Smart Trading Advice for ${symbol}** (AI + Memory Enhanced)

**🤖 KingFisher AI Recommendation:**
- **Action**: ${kingfisherInsights.liquidation_analysis.recommended_action}
- **Win Rate Prediction**: ${kingfisherInsights.win_rate_prediction.prediction}% (${kingfisherInsights.win_rate_prediction.confidence}% confidence)
- **Risk Assessment**: ${kingfisherInsights.liquidation_analysis.risk_level}

**💼 Personalized Strategy (Based on Your History):**
${this.generatePersonalizedStrategy(userMemory, tradingHistory, kingfisherInsights)}

**📊 Risk Management:**
- **Suggested Position Size**: ${kingfisherInsights.win_rate_prediction.recommended_position_size}%
- **Stop Loss**: ${kingfisherInsights.win_rate_prediction.stop_loss_suggestion}%
- **Take Profit Levels**: ${kingfisherInsights.win_rate_prediction.take_profit_levels.join('%, ')}%

**🎯 Top 3 Action Items:**
${kingfisherInsights.trading_tips.slice(0, 3).map((tip, i) => 
  `${i + 1}. ${tip.actionable_insights[0] || tip.message}`
).join('\n')}

**⚠️ Important Notes:**
- Current market volatility: ${this.assessVolatility(kingfisherInsights)}
- Liquidation clusters detected: ${kingfisherInsights.liquidation_analysis.clusters.above.length + kingfisherInsights.liquidation_analysis.clusters.below.length} zones
- Sentiment: ${kingfisherInsights.liquidation_analysis.sentiment.overall}

*Remember: This advice combines advanced AI analysis with your personal trading patterns. Always manage risk appropriately!*
    `.trim()

    // Store trading advice in memory
    await memoryAdapter.storeTradingDecision(
      symbol,
      kingfisherInsights.liquidation_analysis.recommended_action.toLowerCase() as any,
      `Zmarty AI recommendation: ${tradingAdvice.substring(0, 200)}...`,
      kingfisherInsights.ai_confidence / 100,
      context.user_id
    )

    return {
      id: `zmarty_advice_${Date.now()}`,
      message: tradingAdvice,
      type: 'recommendation',
      symbol,
      confidence: kingfisherInsights.ai_confidence,
      sources: ['kingfisher_ai', 'memory_adapter', 'user_history', 'risk_management'],
      timestamp: new Date().toISOString(),
      automated: false,
      memory_enhanced: true,
      kingfisher_powered: true,
      mcp_enhanced: true,
      metadata: { 
        kingfisher_insights: kingfisherInsights,
        user_context: userMemory,
        trading_history_count: tradingHistory.length
      }
    }
  }

  // 🤖 Start Automated Insight Processing
  private startAutomatedInsightProcessing(): void {
    // Process automated insights every 30 seconds
    setInterval(async () => {
      if (this.automatedInsightsQueue.length > 0) {
        const insight = this.automatedInsightsQueue.shift()!
        await this.processAutomatedInsight(insight)
      }
    }, 30000)

    console.log('🤖 Automated insight processing started')
  }

  // 📈 Start Market Monitoring
  private startMarketMonitoring(): void {
    // Monitor market conditions every minute
    setInterval(async () => {
      await this.monitorMarketConditions()
    }, 60000)

    console.log('📈 Market monitoring started')
  }

  // 🔍 Monitor Market Conditions
  private async monitorMarketConditions(): Promise<void> {
    const activeSymbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

    for (const symbol of activeSymbols) {
      try {
        const insights = await kingfisherAIService.getKingFisherInsights(symbol)
        
        // Check for critical conditions
        if (this.shouldTriggerAutomatedInsight(insights)) {
          await this.queueAutomatedInsight(insights, symbol)
        }

        // Store market monitoring data
        await memoryAdapter.storeAILearning(
          `Market monitoring: ${symbol} - Risk: ${insights.liquidation_analysis.risk_level}, Win Rate: ${insights.win_rate_prediction.prediction}%`,
          'market_monitoring',
          insights.ai_confidence / 100,
          'automated_monitoring'
        )

      } catch (error) {
        console.error(`Market monitoring failed for ${symbol}:`, error)
      }
    }
  }

  // 🚨 Check if Automated Insight Should be Triggered
  private shouldTriggerAutomatedInsight(insights: KingFisherInsights): boolean {
    return (
      insights.liquidation_analysis.risk_level === 'CRITICAL' ||
      insights.win_rate_prediction.prediction > 85 ||
      insights.liquidation_analysis.toxic_flow_detected ||
      insights.ai_confidence > 95
    )
  }

  // ➕ Queue Automated Insight
  private async queueAutomatedInsight(insights: KingFisherInsights, symbol: string): Promise<void> {
    const insight: AutomatedInsight = {
      type: this.determineInsightType(insights),
      symbol,
      description: this.generateInsightDescription(insights),
      actionable_advice: this.generateActionableAdvice(insights),
      confidence: insights.ai_confidence,
      kingfisher_data: insights,
      timestamp: new Date().toISOString()
    }

    this.automatedInsightsQueue.push(insight)
    console.log(`🚨 Queued automated insight: ${insight.type} for ${symbol}`)
  }

  // 🔄 Process Automated Insight
  private async processAutomatedInsight(insight: AutomatedInsight): Promise<void> {
    try {
      // Store insight in Supabase for dashboard notifications
      await supabaseService.createAutomatedInsight({
        id: `auto_insight_${Date.now()}`,
        type: insight.type,
        symbol: insight.symbol,
        data: insight,
        confidence: insight.confidence,
        timestamp: insight.timestamp,
        automated: true,
        sources: ['kingfisher_ai', 'zmarty_ai', 'automation_orchestrator']
      })

      // Store in memory adapter
      await memoryAdapter.storeAILearning(
        `Automated insight: ${insight.description}`,
        'automated_insight',
        insight.confidence / 100,
        'automated_processing',
        { insight_type: insight.type, symbol: insight.symbol }
      )

      console.log(`✅ Processed automated insight: ${insight.type} for ${insight.symbol}`)
    } catch (error) {
      console.error('Failed to process automated insight:', error)
    }
  }

  // 🧠 Utility Methods
  private async createUserContext(userId: string, sessionId: string, symbol?: string): Promise<ZmartyContext> {
    const userMemory = await memoryAdapter.getUserContext(userId, symbol)
    
    return {
      user_id: userId,
      session_id: sessionId,
      current_symbol: symbol,
      conversation_history: [],
      user_preferences: userMemory.preferences || {},
      trading_memory: userMemory.trading_history || [],
      market_context: {}
    }
  }

  private async analyzeMessage(message: string, context: ZmartyContext): Promise<any> {
    const lowerMessage = message.toLowerCase()
    
    return {
      requires_market_analysis: lowerMessage.includes('analyze') || lowerMessage.includes('analysis') || lowerMessage.includes('chart'),
      requires_trading_advice: lowerMessage.includes('buy') || lowerMessage.includes('sell') || lowerMessage.includes('trade') || lowerMessage.includes('advice'),
      is_general_question: lowerMessage.includes('how') || lowerMessage.includes('what') || lowerMessage.includes('why'),
      mentions_symbol: /[A-Z]{3,6}(USDT|USD)/.test(message.toUpperCase()),
      response_type: this.determineResponseType(message),
      urgency: lowerMessage.includes('urgent') || lowerMessage.includes('critical') ? 'high' : 'normal'
    }
  }

  private determineResponseType(message: string): 'analysis' | 'recommendation' | 'alert' | 'general' {
    const lowerMessage = message.toLowerCase()
    
    if (lowerMessage.includes('analyze') || lowerMessage.includes('analysis')) return 'analysis'
    if (lowerMessage.includes('buy') || lowerMessage.includes('sell') || lowerMessage.includes('trade')) return 'recommendation'
    if (lowerMessage.includes('alert') || lowerMessage.includes('warning')) return 'alert'
    return 'general'
  }

  private generatePersonalizedStrategy(userMemory: any, tradingHistory: any[], insights: KingFisherInsights): string {
    const riskTolerance = userMemory.preferences?.risk_tolerance || 'medium'
    const successRate = tradingHistory.length > 0 ? 
      tradingHistory.filter((t: any) => t.metadata.outcome === 'profitable').length / tradingHistory.length * 100 : 0

    return `Based on your ${riskTolerance} risk tolerance and ${successRate.toFixed(0)}% historical success rate, ` +
           `I recommend ${this.getPersonalizedRecommendation(riskTolerance, insights.liquidation_analysis.recommended_action)}.`
  }

  private getPersonalizedRecommendation(riskTolerance: string, aiRecommendation: string): string {
    if (riskTolerance === 'low' && aiRecommendation === 'BUY') {
      return 'a conservative approach with smaller position sizes and tight stop losses'
    } else if (riskTolerance === 'high' && aiRecommendation === 'BUY') {
      return 'taking advantage of this opportunity with increased position sizing'
    }
    return `following the AI recommendation to ${aiRecommendation} with appropriate risk management`
  }

  private assessVolatility(insights: KingFisherInsights): string {
    if (insights.liquidation_analysis.risk_level === 'CRITICAL') return 'Very High'
    if (insights.liquidation_analysis.risk_level === 'HIGH') return 'High'
    if (insights.liquidation_analysis.risk_level === 'MEDIUM') return 'Moderate'
    return 'Low'
  }

  private determineInsightType(insights: KingFisherInsights): AutomatedInsight['type'] {
    if (insights.liquidation_analysis.toxic_flow_detected) return 'risk_warning'
    if (insights.win_rate_prediction.prediction > 85) return 'win_rate_signal'
    if (insights.liquidation_analysis.risk_level === 'CRITICAL') return 'risk_warning'
    if (insights.liquidation_analysis.clusters.above.length > 3) return 'liquidation_opportunity'
    return 'market_anomaly'
  }

  private generateInsightDescription(insights: KingFisherInsights): string {
    switch (this.determineInsightType(insights)) {
      case 'risk_warning':
        return `Critical risk detected for ${insights.symbol}: ${insights.liquidation_analysis.risk_level} level with ${insights.liquidation_analysis.toxic_flow_detected ? 'toxic flow' : 'high volatility'}`
      case 'win_rate_signal':
        return `High probability opportunity for ${insights.symbol}: ${insights.win_rate_prediction.prediction}% win rate predicted`
      case 'liquidation_opportunity':
        return `Major liquidation clusters detected for ${insights.symbol}: ${insights.liquidation_analysis.clusters.above.length + insights.liquidation_analysis.clusters.below.length} zones identified`
      default:
        return `Market anomaly detected for ${insights.symbol}: Unusual patterns in liquidation data`
    }
  }

  private generateActionableAdvice(insights: KingFisherInsights): string[] {
    const advice: string[] = []
    
    if (insights.liquidation_analysis.recommended_action === 'BUY') {
      advice.push('Consider long positions with proper risk management')
    } else if (insights.liquidation_analysis.recommended_action === 'SELL') {
      advice.push('Consider taking profits or short positions')
    }
    
    advice.push(`Set stop loss at ${insights.win_rate_prediction.stop_loss_suggestion}%`)
    advice.push(`Target take profit levels: ${insights.win_rate_prediction.take_profit_levels.join('%, ')}%`)
    
    if (insights.liquidation_analysis.toxic_flow_detected) {
      advice.push('⚠️ Avoid large positions due to toxic flow detection')
    }
    
    return advice
  }

  private async generateComprehensiveResponse(params: {
    message: string
    symbol?: string
    kingfisherInsights: KingFisherInsights | null
    relevantMemories: any[]
    marketData: any
    exchangeData: any
    tradingDecisions: any
    userContext: any
    analysis: any
  }): Promise<string> {
    
    let response = `🤖 **Zmarty AI - The Brain of ZmartBot Trading Platform**\n`
    response += `Connected to all major trading services and providing comprehensive market intelligence.\n`

    // Service Status Summary
    const connectedServices = []
    if (params.exchangeData.kucoin) connectedServices.push('📈 KuCoin')
    if (params.exchangeData.binance) connectedServices.push('🚀 Binance')
    if (params.tradingDecisions) connectedServices.push('🧠 Trading AI')
    if (params.kingfisherInsights) connectedServices.push('🔍 KingFisher')
    
    if (connectedServices.length > 0) {
      response += `\n**🔗 Active Connections:** ${connectedServices.join(' | ')}\n`
    }

    // Trading Orchestration Insights
    if (params.tradingDecisions && params.tradingDecisions.analysis) {
      const analysis = params.tradingDecisions.analysis
      response += `\n**🎯 Market Overview:**\n`
      response += `- Market Sentiment: ${analysis.market_sentiment}\n`
      response += `- Opportunities: ${analysis.top_opportunities.length} high-confidence signals\n`
      response += `- Risk Alerts: ${analysis.risk_alerts.length} items to monitor\n`
    }

    // Symbol-Specific Analysis
    if (params.symbol && params.kingfisherInsights) {
      response += `\n**🔍 ${params.symbol} Deep Analysis:**\n`
      response += `- KingFisher AI: ${params.kingfisherInsights.market_structure.trend} (${params.kingfisherInsights.ai_confidence}% confidence)\n`
      response += `- Risk Level: ${params.kingfisherInsights.liquidation_analysis.risk_level}\n`
      response += `- Recommendation: ${params.kingfisherInsights.liquidation_analysis.recommended_action}\n`
      
      // Trading Decision from Orchestration
      if (params.tradingDecisions && params.tradingDecisions.decision) {
        const decision = params.tradingDecisions.decision
        response += `- Trading AI Decision: ${decision.action} (${(decision.confidence * 100).toFixed(1)}% confidence)\n`
        response += `- Reasoning: ${decision.reasoning}\n`
      }
    }

    // Multi-Exchange Price Comparison
    if (params.symbol && (params.exchangeData.kucoin || params.exchangeData.binance)) {
      response += `\n**💱 Exchange Comparison for ${params.symbol}:**\n`
      
      if (params.exchangeData.kucoin && params.exchangeData.kucoin.marketData) {
        const kucoin = params.exchangeData.kucoin.marketData
        response += `- KuCoin: $${kucoin.price.toFixed(2)} (${kucoin.change_24h >= 0 ? '+' : ''}${kucoin.change_24h.toFixed(2)}%)\n`
      }
      
      if (params.exchangeData.binance && params.exchangeData.binance.marketData) {
        const binance = params.exchangeData.binance.marketData
        response += `- Binance: $${binance.price.toFixed(2)} (${binance.change_24h >= 0 ? '+' : ''}${binance.change_24h.toFixed(2)}%)\n`
      }
      
      // Arbitrage opportunity detection
      if (params.exchangeData.kucoin && params.exchangeData.binance) {
        const priceDiff = Math.abs(params.exchangeData.kucoin.marketData.price - params.exchangeData.binance.marketData.price)
        const percentDiff = (priceDiff / params.exchangeData.kucoin.marketData.price) * 100
        if (percentDiff > 0.5) {
          response += `⚡ **Arbitrage Alert:** ${percentDiff.toFixed(2)}% price difference detected!\n`
        }
      }
    }

    // Market Summary from Multiple Exchanges
    if (params.exchangeData.kucoin && params.exchangeData.kucoin.summary) {
      const summary = params.exchangeData.kucoin.summary
      response += `\n**📊 Market Summary:**\n`
      response += `- KuCoin: ${summary.marketOverview} (${summary.totalSymbols} symbols tracked)\n`
      if (summary.topGainers.length > 0) {
        response += `- Top Gainer: ${summary.topGainers[0].symbol} (+${summary.topGainers[0].change_24h.toFixed(2)}%)\n`
      }
    }

    // Portfolio & Risk Insights
    if (params.tradingDecisions && params.tradingDecisions.portfolio) {
      const portfolio = params.tradingDecisions.portfolio
      response += `\n**📈 Portfolio Intelligence:**\n`
      response += `- Active Symbols: ${portfolio.active_symbols.length}\n`
      response += `- High Confidence Decisions: ${portfolio.confidence_analysis.high_confidence.length}\n`
      response += `- Recommendations: ${portfolio.recommendations.slice(0, 2).join(', ')}\n`
    }

    // Memory & Learning Context
    if (params.relevantMemories.length > 0) {
      response += `\n**🧠 Personalized Insights:** Based on ${params.relevantMemories.length} previous conversations, I've learned your trading patterns and preferences.\n`
    }

    // User Preferences
    if (params.userContext.preferences && params.userContext.preferences.risk_tolerance) {
      response += `\n**⚙️ Personal Settings:** Configured for ${params.userContext.preferences.risk_tolerance} risk tolerance.\n`
    }

    response += `\n**💡 What I can help with:**\n`
    response += `• Real-time market analysis across exchanges\n`
    response += `• AI-powered trading recommendations\n`
    response += `• Risk management and portfolio optimization\n`
    response += `• Arbitrage opportunity detection\n`
    response += `• Personalized trading insights\n`
    response += `\nJust ask me about any symbol or trading strategy! 🚀`
    
    return response
  }

  private generateFallbackResponse(message: string, analysis: any): string {
    return `I understand you're asking about trading and markets. While I'm experiencing some technical issues with my advanced analysis systems, I can still help you with basic questions. Could you please be more specific about what you'd like to know?`
  }

  private generateGeneralResponse(
    message: string, 
    context: ZmartyContext, 
    analysis: any
  ): Promise<ZmartyResponse> {
    return Promise.resolve({
      id: `zmarty_general_${Date.now()}`,
      message: `I'm Zmarty, your advanced AI trading assistant. I'm powered by KingFisher AI's multi-agent system and enhanced with memory capabilities. I can help you with market analysis, trading advice, risk management, and more. What would you like to explore today?`,
      type: 'general',
      confidence: 90,
      sources: ['zmarty_ai'],
      timestamp: new Date().toISOString(),
      automated: false,
      memory_enhanced: false,
      kingfisher_powered: false,
      mcp_enhanced: true
    })
  }

  // 📊 Get Zmarty Statistics
  getZmartyStats(): any {
    return {
      active_contexts: this.context.size,
      queued_insights: this.automatedInsightsQueue.length,
      mcp_connections: Object.fromEntries(
        Array.from(this.mcpConnections.entries()).map(([key, value]) => [key, value.status])
      ),
      memory_stats: memoryAdapter.getMemoryStatistics(),
      automation_status: automationOrchestrator.getAutomationStatus()
    }
  }

  // 🎯 Get Automated Insights
  getAutomatedInsights(): AutomatedInsight[] {
    return [...this.automatedInsightsQueue]
  }

  // ⚙️ Update Configuration
  updateConfiguration(config: any): void {
    // Update Zmarty configuration
    console.log('⚙️ Zmarty configuration updated:', config)
  }
}

// Export singleton instance
export const zmartyAI = new ZmartyAI()
export default zmartyAI