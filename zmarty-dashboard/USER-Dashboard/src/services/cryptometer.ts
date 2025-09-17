import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const CRYPTOMETER_API_URL = 'https://api.cryptometer.io/v2' // Placeholder URL

// Cryptometer API client
const cryptometerClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Technical Indicator Types
export interface TechnicalIndicators {
  sma: { [period: string]: number }
  ema: { [period: string]: number }
  rsi: { [period: string]: number }
  macd: {
    macd: number
    signal: number
    histogram: number
  }
  bollinger: {
    upper: number
    middle: number
    lower: number
    bandwidth: number
  }
  stochastic: {
    k: number
    d: number
  }
  williams_r: number
  cci: number
  momentum: { [period: string]: number }
  roc: { [period: string]: number }
  adx: {
    adx: number
    di_positive: number
    di_negative: number
  }
  aroon: {
    up: number
    down: number
    oscillator: number
  }
  obv: number
  mfi: number
  atr: number
  parabolic_sar: number
  ichimoku: {
    tenkan_sen: number
    kijun_sen: number
    senkou_span_a: number
    senkou_span_b: number
    chikou_span: number
  }
}

export interface CryptometerData {
  symbol: string
  timestamp: string
  ohlcv: {
    open: number
    high: number
    low: number
    close: number
    volume: number
  }
  indicators: TechnicalIndicators
  signals: {
    overall: 'BUY' | 'SELL' | 'HOLD'
    strength: number // 0-100
    trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    momentum: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
    volatility: 'HIGH' | 'MEDIUM' | 'LOW'
  }
  risk_metrics: {
    drawdown: number
    sharpe_ratio: number
    volatility: number
    beta: number
  }
}

export interface CryptoSymbol {
  symbol: string
  name: string
  exchange: string
  category: string
  market_cap?: number
  volume_24h?: number
  price?: number
  change_24h?: number
}

// Mock data generator for demonstration
const generateMockTechnicalIndicators = (price: number): TechnicalIndicators => {
  const randomVariation = (base: number, variance: number) => 
    base + (Math.random() - 0.5) * variance

  return {
    sma: {
      '5': randomVariation(price, price * 0.02),
      '10': randomVariation(price, price * 0.03),
      '20': randomVariation(price, price * 0.05),
      '50': randomVariation(price, price * 0.08),
      '100': randomVariation(price, price * 0.12),
      '200': randomVariation(price, price * 0.15)
    },
    ema: {
      '5': randomVariation(price, price * 0.015),
      '12': randomVariation(price, price * 0.025),
      '21': randomVariation(price, price * 0.04),
      '26': randomVariation(price, price * 0.045),
      '50': randomVariation(price, price * 0.07),
      '100': randomVariation(price, price * 0.1)
    },
    rsi: {
      '14': randomVariation(50, 30),
      '21': randomVariation(50, 25)
    },
    macd: {
      macd: randomVariation(0, price * 0.01),
      signal: randomVariation(0, price * 0.008),
      histogram: randomVariation(0, price * 0.005)
    },
    bollinger: {
      upper: price * randomVariation(1.02, 0.01),
      middle: price,
      lower: price * randomVariation(0.98, 0.01),
      bandwidth: randomVariation(0.04, 0.02)
    },
    stochastic: {
      k: randomVariation(50, 40),
      d: randomVariation(50, 35)
    },
    williams_r: randomVariation(-50, 40),
    cci: randomVariation(0, 100),
    momentum: {
      '10': randomVariation(0, price * 0.05),
      '14': randomVariation(0, price * 0.06)
    },
    roc: {
      '10': randomVariation(0, 10),
      '21': randomVariation(0, 15)
    },
    adx: {
      adx: randomVariation(25, 20),
      di_positive: randomVariation(20, 15),
      di_negative: randomVariation(20, 15)
    },
    aroon: {
      up: randomVariation(50, 40),
      down: randomVariation(50, 40),
      oscillator: randomVariation(0, 80)
    },
    obv: randomVariation(1000000, 500000),
    mfi: randomVariation(50, 30),
    atr: randomVariation(price * 0.02, price * 0.01),
    parabolic_sar: randomVariation(price * 0.98, price * 0.02),
    ichimoku: {
      tenkan_sen: randomVariation(price * 1.01, price * 0.02),
      kijun_sen: randomVariation(price * 0.99, price * 0.02),
      senkou_span_a: randomVariation(price * 1.005, price * 0.015),
      senkou_span_b: randomVariation(price * 0.995, price * 0.015),
      chikou_span: randomVariation(price * 1.002, price * 0.01)
    }
  }
}

const generateMockSignals = (indicators: TechnicalIndicators): CryptometerData['signals'] => {
  const rsi14 = indicators.rsi['14']
  const macdHistogram = indicators.macd.histogram
  const stochK = indicators.stochastic.k
  
  let bullishSignals = 0
  let bearishSignals = 0
  
  // RSI Analysis
  if (rsi14 < 30) bullishSignals++
  if (rsi14 > 70) bearishSignals++
  
  // MACD Analysis
  if (macdHistogram > 0) bullishSignals++
  else bearishSignals++
  
  // Stochastic Analysis
  if (stochK < 20) bullishSignals++
  if (stochK > 80) bearishSignals++
  
  const totalSignals = bullishSignals + bearishSignals
  const bullishPercent = totalSignals > 0 ? bullishSignals / totalSignals : 0.5
  
  let overall: 'BUY' | 'SELL' | 'HOLD'
  let trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  let momentum: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
  
  if (bullishPercent > 0.6) {
    overall = 'BUY'
    trend = 'BULLISH'
    momentum = 'POSITIVE'
  } else if (bullishPercent < 0.4) {
    overall = 'SELL'
    trend = 'BEARISH'
    momentum = 'NEGATIVE'
  } else {
    overall = 'HOLD'
    trend = 'NEUTRAL'
    momentum = 'NEUTRAL'
  }
  
  const strength = Math.round(Math.abs(bullishPercent - 0.5) * 200)
  
  return {
    overall,
    strength,
    trend,
    momentum,
    volatility: indicators.atr > indicators.sma['20'] * 0.03 ? 'HIGH' : 
               indicators.atr > indicators.sma['20'] * 0.015 ? 'MEDIUM' : 'LOW'
  }
}

// Cryptometer Service
export const cryptometerService = {
  // Get supported cryptocurrency symbols
  async getSupportedSymbols(): Promise<CryptoSymbol[]> {
    try {
      const response = await cryptometerClient.get('/cryptometer/symbols')
      return response.data
    } catch (error) {
      console.error('Error fetching symbols:', error)
      // Return mock data
      return [
        { symbol: 'BTCUSDT', name: 'Bitcoin', exchange: 'Binance', category: 'Cryptocurrency' },
        { symbol: 'ETHUSDT', name: 'Ethereum', exchange: 'Binance', category: 'Cryptocurrency' },
        { symbol: 'ADAUSDT', name: 'Cardano', exchange: 'Binance', category: 'Cryptocurrency' },
        { symbol: 'SOLUSDT', name: 'Solana', exchange: 'Binance', category: 'Cryptocurrency' },
        { symbol: 'DOTUSDT', name: 'Polkadot', exchange: 'Binance', category: 'Cryptocurrency' },
        { symbol: 'AVAXUSDT', name: 'Avalanche', exchange: 'Binance', category: 'Cryptocurrency' }
      ]
    }
  },

  // Get comprehensive analysis for a symbol
  async getCryptoAnalysis(symbol: string, timeframe: string = '1h'): Promise<CryptometerData> {
    try {
      const response = await cryptometerClient.get(`/cryptometer/analysis/${symbol}`, {
        params: { timeframe }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching analysis:', error)
      
      // Generate mock data
      const basePrice = this.getMockPrice(symbol)
      const indicators = generateMockTechnicalIndicators(basePrice)
      const signals = generateMockSignals(indicators)
      
      return {
        symbol,
        timestamp: new Date().toISOString(),
        ohlcv: {
          open: basePrice * 0.999,
          high: basePrice * 1.005,
          low: basePrice * 0.995,
          close: basePrice,
          volume: Math.random() * 1000000 + 100000
        },
        indicators,
        signals,
        risk_metrics: {
          drawdown: Math.random() * 15,
          sharpe_ratio: Math.random() * 3,
          volatility: Math.random() * 50 + 10,
          beta: Math.random() * 2
        }
      }
    }
  },

  // Get historical data with indicators
  async getHistoricalData(
    symbol: string, 
    timeframe: string = '1h', 
    limit: number = 100
  ): Promise<CryptometerData[]> {
    try {
      const response = await cryptometerClient.get(`/cryptometer/history/${symbol}`, {
        params: { timeframe, limit }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching historical data:', error)
      
      // Generate mock historical data
      const basePrice = this.getMockPrice(symbol)
      const data: CryptometerData[] = []
      
      for (let i = limit; i > 0; i--) {
        const timestamp = new Date(Date.now() - i * 60 * 60 * 1000).toISOString()
        const price = basePrice * (0.95 + Math.random() * 0.1)
        const indicators = generateMockTechnicalIndicators(price)
        const signals = generateMockSignals(indicators)
        
        data.push({
          symbol,
          timestamp,
          ohlcv: {
            open: price * (0.998 + Math.random() * 0.004),
            high: price * (1.002 + Math.random() * 0.008),
            low: price * (0.998 - Math.random() * 0.008),
            close: price,
            volume: Math.random() * 1000000 + 100000
          },
          indicators,
          signals,
          risk_metrics: {
            drawdown: Math.random() * 15,
            sharpe_ratio: Math.random() * 3,
            volatility: Math.random() * 50 + 10,
            beta: Math.random() * 2
          }
        })
      }
      
      return data
    }
  },

  // Get specific technical indicator
  async getTechnicalIndicator(
    symbol: string, 
    indicator: string, 
    period?: number
  ): Promise<{ time: string; value: number }[]> {
    try {
      const response = await cryptometerClient.get(`/cryptometer/indicator/${symbol}/${indicator}`, {
        params: { period }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching indicator:', error)
      
      // Generate mock indicator data
      const data: { time: string; value: number }[] = []
      const baseValue = indicator === 'rsi' ? 50 : this.getMockPrice(symbol)
      
      for (let i = 100; i > 0; i--) {
        const time = new Date(Date.now() - i * 60 * 60 * 1000).toISOString()
        const variation = indicator === 'rsi' ? 30 : baseValue * 0.05
        const value = baseValue + (Math.random() - 0.5) * variation
        
        data.push({ time, value })
      }
      
      return data
    }
  },

  // Get real-time price updates
  async getRealTimePrice(symbol: string): Promise<{ price: number; change: number; volume: number }> {
    try {
      const response = await cryptometerClient.get(`/cryptometer/price/${symbol}`)
      return response.data
    } catch (error) {
      console.error('Error fetching real-time price:', error)
      
      const basePrice = this.getMockPrice(symbol)
      return {
        price: basePrice,
        change: (Math.random() - 0.5) * 10,
        volume: Math.random() * 1000000 + 100000
      }
    }
  },

  // Utility function to get mock prices
  getMockPrice(symbol: string): number {
    const prices: { [key: string]: number } = {
      'BTCUSDT': 43250,
      'ETHUSDT': 2640,
      'ADAUSDT': 0.45,
      'SOLUSDT': 98.5,
      'DOTUSDT': 7.2,
      'AVAXUSDT': 36.8,
      'BNBUSDT': 310.5,
      'LINKUSDT': 14.5,
      'MATICUSDT': 0.85,
      'UNIUSDT': 6.2
    }
    
    return prices[symbol] || Math.random() * 1000 + 10
  },

  // Get market sentiment analysis
  async getMarketSentiment(): Promise<{
    overall: string
    fear_greed_index: number
    social_sentiment: number
    news_sentiment: number
  }> {
    try {
      const response = await cryptometerClient.get('/cryptometer/sentiment')
      return response.data
    } catch (error) {
      console.error('Error fetching sentiment:', error)
      
      return {
        overall: ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'][Math.floor(Math.random() * 5)],
        fear_greed_index: Math.random() * 100,
        social_sentiment: Math.random() * 100,
        news_sentiment: Math.random() * 100
      }
    }
  }
}

export default cryptometerService