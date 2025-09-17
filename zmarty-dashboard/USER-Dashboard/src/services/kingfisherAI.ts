import axios from 'axios'

const KINGFISHER_API_URL = 'http://localhost:8098'
const KINGFISHER_API_V2_URL = 'http://localhost:8108' // Alternative port mentioned in YAML

// KingFisher AI client
const kingfisherClient = axios.create({
  baseURL: KINGFISHER_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Alternative client for the second KingFisher service
const kingfisherClientV2 = axios.create({
  baseURL: KINGFISHER_API_V2_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// KingFisher AI Types
export interface LiquidationCluster {
  price: number
  size: 'small' | 'medium' | 'large' | 'whale'
  notional: number
  side: 'above' | 'below'
  confidence: number
  impact_score: number
}

export interface LiquidationAnalysis {
  symbol: string
  clusters: {
    above: LiquidationCluster[]
    below: LiquidationCluster[]
  }
  total_liquidation_volume: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  recommended_action: 'BUY' | 'SELL' | 'HOLD' | 'AVOID'
  win_rate_prediction: number
  confidence_score: number
  key_levels: {
    support: number[]
    resistance: number[]
  }
  toxic_flow_detected: boolean
  sentiment: {
    overall: string
    fear_greed: number
    liquidation_fear: number
  }
}

export interface WinRatePrediction {
  symbol: string
  prediction: number
  confidence: number
  timeframe: string
  model: string
  factors: string[]
  risk_assessment: {
    max_drawdown: number
    volatility: number
    correlation_btc: number
  }
  recommended_position_size: number
  stop_loss_suggestion: number
  take_profit_levels: number[]
}

export interface TradingTip {
  id: string
  type: 'liquidation' | 'technical' | 'sentiment' | 'risk_management'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'
  symbol: string
  title: string
  message: string
  analysis: string
  data: any
  actionable_insights: string[]
  risk_warning?: string
  timestamp: string
  expires_at?: string
}

export interface KingFisherInsights {
  symbol: string
  overall_score: number
  liquidation_analysis: LiquidationAnalysis
  win_rate_prediction: WinRatePrediction
  trading_tips: TradingTip[]
  market_structure: {
    trend: 'BULLISH' | 'BEARISH' | 'SIDEWAYS'
    strength: number
    volume_profile: 'HEALTHY' | 'WEAK' | 'EXPLOSIVE'
  }
  ai_confidence: number
  last_updated: string
}

// KingFisher AI Service
export const kingfisherAIService = {
  // Health check for both services
  async healthCheck(): Promise<{ primary: boolean; secondary: boolean }> {
    const results = { primary: false, secondary: false }
    
    try {
      const primaryResponse = await kingfisherClient.get('/health')
      results.primary = primaryResponse.status === 200
    } catch (error) {
      console.warn('Primary KingFisher service unavailable:', error)
    }
    
    try {
      const secondaryResponse = await kingfisherClientV2.get('/health')
      results.secondary = secondaryResponse.status === 200
    } catch (error) {
      console.warn('Secondary KingFisher service unavailable:', error)
    }
    
    return results
  },

  // Get liquidation analysis for a symbol
  async getLiquidationAnalysis(symbol: string): Promise<LiquidationAnalysis> {
    try {
      // Try primary service first
      const response = await kingfisherClient.get(`/api/v1/analysis/liquidation?symbol=${symbol}`)
      return this.formatLiquidationAnalysis(response.data, symbol)
    } catch (error) {
      console.warn('Primary service failed, trying alternative...', error)
      
      try {
        // Fallback to secondary service
        const response = await kingfisherClientV2.get(`/api/v1/analysis/liquidation?symbol=${symbol}`)
        return this.formatLiquidationAnalysis(response.data, symbol)
      } catch (secondaryError) {
        console.error('Both KingFisher services failed:', secondaryError)
        return this.generateMockLiquidationAnalysis(symbol)
      }
    }
  },

  // Get win rate prediction
  async getWinRatePrediction(symbol: string, timeframe: string = '24h'): Promise<WinRatePrediction> {
    try {
      const response = await kingfisherClient.post('/api/v1/prediction/win-rate', {
        symbol,
        timeframe,
        analysis_depth: 'comprehensive'
      })
      
      return this.formatWinRatePrediction(response.data, symbol, timeframe)
    } catch (error) {
      console.error('Win rate prediction failed:', error)
      return this.generateMockWinRatePrediction(symbol, timeframe)
    }
  },

  // Get comprehensive KingFisher insights for Zmarty AI
  async getKingFisherInsights(symbol: string): Promise<KingFisherInsights> {
    try {
      const [liquidationAnalysis, winRatePrediction] = await Promise.all([
        this.getLiquidationAnalysis(symbol),
        this.getWinRatePrediction(symbol)
      ])

      const tradingTips = this.generateTradingTips(liquidationAnalysis, winRatePrediction, symbol)
      
      return {
        symbol,
        overall_score: (liquidationAnalysis.confidence_score + winRatePrediction.confidence) / 2,
        liquidation_analysis: liquidationAnalysis,
        win_rate_prediction: winRatePrediction,
        trading_tips: tradingTips,
        market_structure: {
          trend: this.determineTrend(liquidationAnalysis, winRatePrediction),
          strength: Math.round((liquidationAnalysis.confidence_score + winRatePrediction.confidence) / 2),
          volume_profile: liquidationAnalysis.total_liquidation_volume > 10000000 ? 'EXPLOSIVE' : 
                          liquidationAnalysis.total_liquidation_volume > 1000000 ? 'HEALTHY' : 'WEAK'
        },
        ai_confidence: Math.round((liquidationAnalysis.confidence_score + winRatePrediction.confidence) / 2),
        last_updated: new Date().toISOString()
      }
    } catch (error) {
      console.error('Failed to get KingFisher insights:', error)
      return this.generateMockInsights(symbol)
    }
  },

  // Generate intelligent trading tips for Zmarty AI
  generateTradingTips(
    liquidationAnalysis: LiquidationAnalysis, 
    winRatePrediction: WinRatePrediction,
    symbol: string
  ): TradingTip[] {
    const tips: TradingTip[] = []

    // Liquidation-based tips
    if (liquidationAnalysis.clusters.above.length > 0) {
      const majorResistance = liquidationAnalysis.clusters.above[0]
      tips.push({
        id: `liq_resistance_${Date.now()}`,
        type: 'liquidation',
        priority: majorResistance.size === 'whale' ? 'HIGH' : 'MEDIUM',
        symbol,
        title: `Major Liquidation Cluster Detected`,
        message: `${majorResistance.size.toUpperCase()} liquidation cluster at $${majorResistance.price.toLocaleString()}`,
        analysis: `A ${majorResistance.size} liquidation cluster worth $${(majorResistance.notional / 1000000).toFixed(1)}M is positioned above current price. This could act as strong resistance or, if broken, lead to a significant squeeze.`,
        data: majorResistance,
        actionable_insights: [
          `Watch for price rejection near $${majorResistance.price.toLocaleString()}`,
          `If price breaks above with volume, expect acceleration`,
          `Consider taking profits before this level`,
          `Set stop-loss below recent support if going long`
        ],
        timestamp: new Date().toISOString(),
        expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
      })
    }

    if (liquidationAnalysis.clusters.below.length > 0) {
      const majorSupport = liquidationAnalysis.clusters.below[0]
      tips.push({
        id: `liq_support_${Date.now()}`,
        type: 'liquidation',
        priority: majorSupport.size === 'whale' ? 'HIGH' : 'MEDIUM',
        symbol,
        title: `Liquidation Support Zone Identified`,
        message: `${majorSupport.size.toUpperCase()} liquidation cluster provides support at $${majorSupport.price.toLocaleString()}`,
        analysis: `Strong liquidation support from ${majorSupport.size} positions worth $${(majorSupport.notional / 1000000).toFixed(1)}M. This level could provide significant buying pressure if tested.`,
        data: majorSupport,
        actionable_insights: [
          `Consider long entries near $${majorSupport.price.toLocaleString()}`,
          `Set tight stop-loss below this level`,
          `Watch for bounce signals at this support`,
          `High reward-to-risk ratio if support holds`
        ],
        timestamp: new Date().toISOString()
      })
    }

    // Win rate prediction tips
    if (winRatePrediction.prediction > 75) {
      tips.push({
        id: `winrate_high_${Date.now()}`,
        type: 'technical',
        priority: 'HIGH',
        symbol,
        title: `High Win Rate Probability Detected`,
        message: `AI predicts ${winRatePrediction.prediction}% win rate with ${winRatePrediction.confidence}% confidence`,
        analysis: `Advanced AI models indicate favorable conditions for ${symbol} with ${winRatePrediction.prediction}% win rate probability. Key factors: ${winRatePrediction.factors.join(', ')}.`,
        data: winRatePrediction,
        actionable_insights: [
          `Favorable risk-reward setup identified`,
          `Consider increasing position size (within risk limits)`,
          `Multiple confluence factors align`,
          `Monitor for entry opportunities`
        ],
        timestamp: new Date().toISOString()
      })
    }

    // Risk management tips
    if (liquidationAnalysis.risk_level === 'HIGH' || liquidationAnalysis.risk_level === 'CRITICAL') {
      tips.push({
        id: `risk_warning_${Date.now()}`,
        type: 'risk_management',
        priority: liquidationAnalysis.risk_level === 'CRITICAL' ? 'URGENT' : 'HIGH',
        symbol,
        title: `${liquidationAnalysis.risk_level} Risk Level Alert`,
        message: `Current market conditions present ${liquidationAnalysis.risk_level.toLowerCase()} risk for ${symbol}`,
        analysis: `Risk assessment indicates ${liquidationAnalysis.risk_level.toLowerCase()} volatility expected. ${liquidationAnalysis.toxic_flow_detected ? 'Toxic flow detected.' : ''} Exercise increased caution.`,
        data: { risk_level: liquidationAnalysis.risk_level, toxic_flow: liquidationAnalysis.toxic_flow_detected },
        actionable_insights: [
          `Reduce position sizes significantly`,
          `Use wider stop-losses to avoid whipsaws`,
          `Consider waiting for clearer signals`,
          `Avoid FOMO trades in current conditions`
        ],
        risk_warning: `High volatility expected - trade with extreme caution`,
        timestamp: new Date().toISOString()
      })
    }

    // Sentiment-based tips
    if (liquidationAnalysis.sentiment.liquidation_fear > 80) {
      tips.push({
        id: `sentiment_fear_${Date.now()}`,
        type: 'sentiment',
        priority: 'MEDIUM',
        symbol,
        title: `Extreme Liquidation Fear Detected`,
        message: `Liquidation fear index at ${liquidationAnalysis.sentiment.liquidation_fear}/100 - potential contrarian opportunity`,
        analysis: `Extreme fear in the market often presents contrarian opportunities. However, confirm with technical analysis before acting.`,
        data: liquidationAnalysis.sentiment,
        actionable_insights: [
          `Look for oversold bounce opportunities`,
          `Wait for technical confirmation`,
          `Consider dollar-cost averaging`,
          `Be prepared for continued volatility`
        ],
        timestamp: new Date().toISOString()
      })
    }

    return tips.slice(0, 5) // Return top 5 tips
  },

  // Helper functions
  formatLiquidationAnalysis(data: any, symbol: string): LiquidationAnalysis {
    return {
      symbol,
      clusters: data.clusters || { above: [], below: [] },
      total_liquidation_volume: data.total_volume || 0,
      risk_level: data.risk_level || 'MEDIUM',
      recommended_action: data.recommended_action || 'HOLD',
      win_rate_prediction: data.win_rate || 50,
      confidence_score: data.confidence || 75,
      key_levels: data.key_levels || { support: [], resistance: [] },
      toxic_flow_detected: data.toxic_flow || false,
      sentiment: data.sentiment || {
        overall: 'Neutral',
        fear_greed: 50,
        liquidation_fear: 50
      }
    }
  },

  formatWinRatePrediction(data: any, symbol: string, timeframe: string): WinRatePrediction {
    return {
      symbol,
      prediction: data.prediction || 50,
      confidence: data.confidence || 75,
      timeframe,
      model: data.model || 'kingfisher-ai',
      factors: data.factors || ['technical_analysis', 'liquidation_data', 'market_sentiment'],
      risk_assessment: data.risk_assessment || {
        max_drawdown: 15,
        volatility: 25,
        correlation_btc: 0.8
      },
      recommended_position_size: data.position_size || 2,
      stop_loss_suggestion: data.stop_loss || 5,
      take_profit_levels: data.take_profits || [10, 20, 35]
    }
  },

  determineTrend(liquidationAnalysis: LiquidationAnalysis, winRatePrediction: WinRatePrediction): 'BULLISH' | 'BEARISH' | 'SIDEWAYS' {
    if (liquidationAnalysis.recommended_action === 'BUY' && winRatePrediction.prediction > 60) {
      return 'BULLISH'
    } else if (liquidationAnalysis.recommended_action === 'SELL' && winRatePrediction.prediction < 40) {
      return 'BEARISH'
    }
    return 'SIDEWAYS'
  },

  // Mock data generators (fallbacks when service is unavailable)
  generateMockLiquidationAnalysis(symbol: string): LiquidationAnalysis {
    const mockPrice = this.getMockPrice(symbol)
    return {
      symbol,
      clusters: {
        above: [
          {
            price: mockPrice * 1.05,
            size: 'large' as const,
            notional: 5000000,
            side: 'above' as const,
            confidence: 85,
            impact_score: 8.5
          }
        ],
        below: [
          {
            price: mockPrice * 0.95,
            size: 'medium' as const,
            notional: 2000000,
            side: 'below' as const,
            confidence: 80,
            impact_score: 7.2
          }
        ]
      },
      total_liquidation_volume: 15000000,
      risk_level: 'MEDIUM',
      recommended_action: 'HOLD',
      win_rate_prediction: 67.5,
      confidence_score: 82,
      key_levels: {
        support: [mockPrice * 0.95, mockPrice * 0.90],
        resistance: [mockPrice * 1.05, mockPrice * 1.10]
      },
      toxic_flow_detected: false,
      sentiment: {
        overall: 'Cautiously Optimistic',
        fear_greed: 65,
        liquidation_fear: 35
      }
    }
  },

  generateMockWinRatePrediction(symbol: string, timeframe: string): WinRatePrediction {
    return {
      symbol,
      prediction: 72.5,
      confidence: 88,
      timeframe,
      model: 'kingfisher-ai-mock',
      factors: ['liquidation_clusters', 'volume_analysis', 'market_sentiment', 'technical_indicators'],
      risk_assessment: {
        max_drawdown: 12.5,
        volatility: 28.3,
        correlation_btc: 0.75
      },
      recommended_position_size: 3.5,
      stop_loss_suggestion: 4.2,
      take_profit_levels: [8.5, 15.2, 28.7]
    }
  },

  generateMockInsights(symbol: string): KingFisherInsights {
    const liquidationAnalysis = this.generateMockLiquidationAnalysis(symbol)
    const winRatePrediction = this.generateMockWinRatePrediction(symbol, '24h')
    
    return {
      symbol,
      overall_score: 78,
      liquidation_analysis: liquidationAnalysis,
      win_rate_prediction: winRatePrediction,
      trading_tips: this.generateTradingTips(liquidationAnalysis, winRatePrediction, symbol),
      market_structure: {
        trend: 'BULLISH',
        strength: 75,
        volume_profile: 'HEALTHY'
      },
      ai_confidence: 82,
      last_updated: new Date().toISOString()
    }
  },

  getMockPrice(symbol: string): number {
    const prices: { [key: string]: number } = {
      'BTCUSDT': 43250,
      'ETHUSDT': 2640,
      'SOLUSDT': 98.5,
      'ADAUSDT': 0.45,
      'AVAXUSDT': 36.8
    }
    return prices[symbol] || 100
  }
}

export default kingfisherAIService