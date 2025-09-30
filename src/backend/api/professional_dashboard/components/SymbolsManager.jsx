import React, { useState, useEffect, useMemo } from 'react'
import ZmartChart from './ZmartChart'
import SimpleChart from './SimpleChart'
import EnhancedAlertsSystem from './EnhancedAlertsSystem'
import { useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:3400'

// Simple Dropdown Component
const Dropdown = ({ label, options, onAdd, disabled, mySymbols = [], canAddMore = true }) => {
  const [value, setValue] = useState('')
  const canAddSelected = value && canAddMore && !disabled && !mySymbols.includes(value)
  
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <span>🔍</span>
          {label}
        </div>
        <div className="card-badge">{options.length} Symbols</div>
      </div>
      <div className="card-content">
        <select
          className="dropdown-select"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          style={{
            width: '100%',
            padding: '15px',
            fontSize: '1.1rem',
            borderRadius: '10px',
            border: '2px solid rgba(255,255,255,0.2)',
            background: 'rgba(255,255,255,0.1)',
            color: '#ffffff',
            cursor: 'pointer',
            marginBottom: '15px'
          }}
        >
          <option value="">Select a symbol...</option>
          {options.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          className={`action-btn ${canAddSelected ? 'success' : 'secondary'}`}
          disabled={!canAddSelected}
          onClick={() => {
            if (!value) return
            onAdd(value)
            setValue('')
          }}
          style={{
            width: '100%',
            padding: '15px',
            fontSize: '1.2rem',
            fontWeight: '600',
            borderRadius: '10px',
            border: 'none',
            cursor: canAddSelected ? 'pointer' : 'not-allowed',
            background: canAddSelected ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'rgba(255,255,255,0.1)',
            color: canAddSelected ? '#ffffff' : 'rgba(255,255,255,0.5)'
          }}
        >
          ➕ ADD SYMBOL
        </button>
      </div>
    </div>
  )
}

const SymbolsManager = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [mySymbols, setMySymbols] = useState([])
  const [kucoinSymbols, setKucoinSymbols] = useState([])
  const [binanceSymbols, setBinanceSymbols] = useState([])
  const [commonSymbols, setCommonSymbols] = useState([])
  const [symbolQuery, setSymbolQuery] = useState('')
  const [myQuery, setMyQuery] = useState('')

  // Symbols Management sub-tab state
  const [symbolsTab, setSymbolsTab] = useState('my-symbols')

  // Analytics state
  const [analyticsData, setAnalyticsData] = useState(null)
  const [symbolScores, setSymbolScores] = useState([])
  const [performanceData, setPerformanceData] = useState({})

  // Charts state
  const [chartType, setChartType] = useState('candlestick')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D')
  const [symbolPrices, setSymbolPrices] = useState({})
  const [priceTimestamps, setPriceTimestamps] = useState({})
  const [symbol24hHigh, setSymbol24hHigh] = useState({})
  const [symbol24hLow, setSymbol24hLow] = useState({})
  const [isUpdating, setIsUpdating] = useState(false)
  const [isSymbolUpdating, setIsSymbolUpdating] = useState(false)
  const [symbolRanks, setSymbolRanks] = useState({})
  const [lastScoreUpdate, setLastScoreUpdate] = useState(Date.now())
  const [expandedSymbols, setExpandedSymbols] = useState(new Set())
  const [expandedPriceData, setExpandedPriceData] = useState({})
  
  // Chart functionality
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const [chartData, setChartData] = useState(null)
  const [chartLoading, setChartLoading] = useState(false)
  const [chartTimeframe, setChartTimeframe] = useState('24H')

  // ChatGPT Alerts functionality
  const [chatgptAlerts, setChatgptAlerts] = useState([])
  const [alertLoading, setAlertLoading] = useState(false)

  const maxMy = 10

  const canAddMore = useMemo(() => mySymbols.length < maxMy, [mySymbols, maxMy])

  // Load symbols on component mount
  useEffect(() => {
    loadAll()
  }, [])

  // Add manual refresh function for debugging
  const manualRefresh = async () => {
    console.log('🔄 Manual refresh triggered')
    await loadAll()
  }

  // Load analytics when analytics card is visible
  useEffect(() => {
    if (mySymbols.length > 0) {
      loadAnalyticsData()
    }
  }, [mySymbols])

  // Fetch prices when mySymbols change and set up real-time updates
  useEffect(() => {
    if (mySymbols.length > 0) {
      // Initial fetch
      fetchSymbolPrices(mySymbols)
      
      // Set up interval for real-time updates (every 5 minutes instead of 1 minute)
      const interval = setInterval(() => {
        fetchSymbolPrices(mySymbols)
      }, 300000) // Update every 5 minutes (300 seconds) to reduce API calls
      
      // Cleanup interval on unmount
      return () => clearInterval(interval)
    }
  }, [mySymbols])

  // Initialize scores and ranks once when symbols are loaded (but not during add/remove operations)
  useEffect(() => {
    if (mySymbols.length > 0 && !isSymbolUpdating) {
      // Initialize once with fixed scores
      initializeScoresAndRanks()
    }
  }, [mySymbols, isSymbolUpdating])

  // Load chart data when selectedSymbol or chartTimeframe changes (with throttling)
  useEffect(() => {
    console.log(`🔍 Chart useEffect triggered: selectedSymbol=${selectedSymbol}, mySymbols=${mySymbols}`)
    if (selectedSymbol && mySymbols.includes(selectedSymbol)) {
      console.log(`📊 Loading chart for ${selectedSymbol}`)
      // Add a small delay to prevent rapid successive calls
      const timeoutId = setTimeout(() => {
        loadChartData(selectedSymbol, chartTimeframe)
      }, 500)
      
      return () => clearTimeout(timeoutId)
    } else {
      console.log(`⚠️ Chart not loaded: selectedSymbol=${selectedSymbol}, included=${selectedSymbol ? mySymbols.includes(selectedSymbol) : 'no symbol'}`)
    }
  }, [selectedSymbol, chartTimeframe, mySymbols])

  const loadAll = async () => {
    try {
      setLoading(true)
      await Promise.all([
        loadMySymbols(),
        loadKucoinSymbols(),
        loadBinanceSymbols(),
        loadCommonSymbols()
      ])
    } catch (error) {
      console.error('Error loading symbols:', error)
    } finally {
      setLoading(false)
    }
  }

  // Format price: ≥1000 shows 1 decimal, ≥1 shows 2 decimals, <1 shows 4 decimals
  const formatPrice = (price) => {
    const num = parseFloat(price || 0)
    if (num >= 1000) {
      return num.toFixed(1) // 1 decimal: 1000.9, 12345.6
    } else if (num >= 1) {
      return num.toFixed(2) // 2 decimals: 1.95, 123.45
    } else {
      return num.toFixed(4) // 4 decimals: 0.1234
    }
  }

  // Generate random score between 70-100
  const generateScore = () => {
    return Math.floor(Math.random() * 31) + 70
  }

  // Fixed mock scores for each symbol (70-100 range)
  const getFixedScore = (symbol) => {
    const fixedScores = {
      'BTCUSDT': 95,
      'ETHUSDT': 92,
      'SOLUSDT': 88,
      'AAVEUSDT': 85,
      'ADAUSDT': 82,
      'BNBUSDT': 89,
      'LINKUSDT': 87,
      'AVAXUSDT': 84,
      'DOTUSDT': 81,
      'MATICUSDT': 83,
      'UNIUSDT': 86,
      'LTCUSDT': 80,
      'XRPUSDT': 79,
      'BCHUSDT': 78,
      'FILUSDT': 77,
      'ATOMUSDT': 90,
      'NEARUSDT': 91,
      'FTMUSDT': 93,
      'ALGOUSDT': 76,
      'VETUSDT': 75
    }
    return fixedScores[symbol] || 70 // Default score for unknown symbols
  }

  // Initialize scores and ranks once (fixed scores) - limited to once per 15 minutes
  const initializeScoresAndRanks = () => {
    if (mySymbols.length === 0) return

    // Check if we should update ranks (only once per 15 minutes)
    const now = Date.now()
    const fifteenMinutes = 15 * 60 * 1000 // 15 minutes in milliseconds
    
    if (lastScoreUpdate && (now - lastScoreUpdate) < fifteenMinutes) {
      console.log('⏰ Skipping rank update - too soon since last update (15 min limit)')
      return
    }

    console.log('🔄 Updating symbol ranks and scores...')

    const newScores = mySymbols.map((symbol) => ({
      symbol: symbol,
      technical_score: 0.6 + (Math.random() * 0.3),
      fundamental_score: 0.5 + (Math.random() * 0.4),
      market_structure_score: 0.4 + (Math.random() * 0.5),
      risk_score: 0.3 + (Math.random() * 0.6),
      composite_score: getFixedScore(symbol) / 100, // Convert to 0-1 scale
      confidence_level: 0.7 + (Math.random() * 0.2),
      rank: 1,
      calculation_timestamp: new Date().toISOString()
    }))

    setSymbolScores(newScores)
    setLastScoreUpdate(now)

    // Calculate ranks based on fixed scores (higher score = lower rank number)
    const sortedScores = [...newScores].sort((a, b) => b.composite_score - a.composite_score)
    const newRanks = {}
    sortedScores.forEach((scoreObj, index) => {
      newRanks[scoreObj.symbol] = index + 1 // Rank 1 is highest score
    })
    setSymbolRanks(newRanks)

    // Reorder mySymbols based on rank (rank 1 first)
    const sortedSymbols = [...mySymbols].sort((a, b) => {
      const rankA = newRanks[a] || 999
      const rankB = newRanks[b] || 999
      return rankA - rankB // Sort by rank ascending (rank 1 first)
    })
    
    // Update the mySymbols order in the backend
    updateSymbolsOrder(sortedSymbols)
  }

  // Update symbols order in backend
  const updateSymbolsOrder = async (sortedSymbols) => {
    try {
      const response = await fetch(`${API_BASE}/api/futures-symbols/my-symbols/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sortedSymbols)
      })

      if (response.ok) {
        setMySymbols(sortedSymbols)
        console.log('✅ Symbols reordered by rank successfully')
      } else {
        console.error('❌ Failed to reorder symbols by rank')
      }
    } catch (error) {
      console.error('Error reordering symbols:', error)
    }
  }

  // Load chart for selected symbol
  const loadChartData = async (symbol, timeframe = '24H') => {
    console.log(`🎯 loadChartData called with symbol: ${symbol}, timeframe: ${timeframe}`)
    setSelectedSymbol(symbol)
    setChartTimeframe(timeframe)
    setChartLoading(true)
    
    try {
      // Map timeframe to Binance interval
      const intervalMap = {
        '15m': '15m',
        '1h': '1h', 
        '4h': '4h',
        '1D': '1d',
        '24H': '1d'
      }
      
      const interval = intervalMap[timeframe] || '1d'
      
      // Use the correct Binance klines endpoint
      const response = await fetch(`${API_BASE}/api/v1/binance/klines?symbol=${symbol}&interval=${interval}&limit=100`)
      
      if (response.ok) {
        const klinesData = await response.json()
        
        if (klinesData && klinesData.length > 0) {
          // Transform Binance klines data to chart format
          const chartData = klinesData.map(kline => ({
            time: kline[0], // Keep as milliseconds (don't divide by 1000)
            open: parseFloat(kline[1]),
            high: parseFloat(kline[2]),
            low: parseFloat(kline[3]),
            close: parseFloat(kline[4]),
            volume: parseFloat(kline[5])
          }))
          
          console.log(`✅ Chart data loaded for ${symbol}: ${chartData.length} candles`)
          console.log('🔍 First 3 candles:', chartData.slice(0, 3))
          setChartData(chartData)
        } else {
          console.warn(`⚠️ No chart data available for ${symbol}`)
          setChartData(null)
        }
      } else {
        console.error(`❌ Failed to load chart data for ${symbol}: ${response.status}`)
        setChartData(null)
      }
    } catch (error) {
      console.error(`❌ Error loading chart data for ${symbol}:`, error)
      setChartData(null)
    } finally {
      setChartLoading(false)
    }
  }

  // Get score for a symbol (use fixed score)
  const getSymbolScore = (symbol) => {
    return getFixedScore(symbol) // Return the fixed score directly
  }

  // Get rank for a symbol
  const getSymbolRank = (symbol) => {
    return symbolRanks[symbol] || 'N/A'
  }

  // Generate ChatGPT alert
  const generateChatGPTAlert = async (alertData) => {
    try {
      setAlertLoading(true)
      
      const response = await fetch(`${API_BASE}/api/v1/chatgpt-alerts/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(alertData)
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success && result.alert) {
          // Add timestamp for display
          const alertWithTime = {
            ...result.alert,
            displayTime: new Date().toLocaleTimeString()
          }
          
          setChatgptAlerts(prev => [alertWithTime, ...prev.slice(0, 9)]) // Keep max 10 alerts
          console.log(`✅ Generated ChatGPT alert: ${result.alert.title}`)
          return result.alert
        } else {
          console.error('❌ Failed to generate ChatGPT alert:', result.error)
        }
      } else {
        console.error(`❌ ChatGPT alert generation failed: ${response.status}`)
      }
    } catch (error) {
      console.error('❌ Error generating ChatGPT alert:', error)
    } finally {
      setAlertLoading(false)
    }
  }

  // Generate sample alerts for demonstration
  const generateSampleAlerts = async () => {
    const sampleAlerts = [
      {
        symbol: 'BTCUSDT',
        alert_type: 'golden_cross',
        indicator: 'EMA12/EMA26',
        value: 0.85,
        threshold: 0.5,
        timeframe: '1h',
        price: 101234.56
      },
      {
        symbol: 'ETHUSDT',
        alert_type: 'rsi_overbought',
        indicator: 'RSI',
        value: 78.45,
        threshold: 70,
        timeframe: '1h',
        price: 3456.78
      },
      {
        symbol: 'SOLUSDT',
        alert_type: 'macd_bullish',
        indicator: 'MACD',
        value: 2345.67,
        threshold: 1234.56,
        timeframe: '1h',
        price: 123.45
      }
    ]

    for (const alertData of sampleAlerts) {
      await generateChatGPTAlert(alertData)
      // Small delay between alerts
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }

  // Throttle to prevent excessive API calls
  const [lastFetchTime, setLastFetchTime] = useState(0)
  
  const fetchSymbolPrices = async (symbols) => {
    const now = Date.now()
    const timeSinceLastFetch = now - lastFetchTime
    
    // Prevent fetching more than once every 30 seconds
    if (timeSinceLastFetch < 30000) {
      console.log('⏳ Skipping price fetch - too soon since last update')
      return
    }
    
    try {
      setIsUpdating(true)
      setLastFetchTime(now)
      const prices = {}
      const timestamps = {}
      const high24h = {}
      const low24h = {}
      const currentTime = Date.now()
      
      // Fetch all prices in parallel for better performance
      const pricePromises = symbols.map(async (symbol) => {
        try {
          // Convert symbol format for Binance API (e.g., BTC/USDT:USDT -> BTCUSDT)
          const binanceSymbol = symbol.replace('/USDT:USDT', 'USDT').replace('/', '')
          const response = await fetch(`${API_BASE}/api/v1/binance/ticker/24hr?symbol=${binanceSymbol}`, {
            method: 'GET',
            headers: {
              'Cache-Control': 'no-cache',
              'Pragma': 'no-cache'
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            
            return {
              symbol,
              price: formatPrice(data.lastPrice),
              high24h: formatPrice(data.highPrice),
              low24h: formatPrice(data.lowPrice),
              timestamp: currentTime,
              success: true
            }
          } else {
            console.warn(`Failed to fetch price for ${symbol}: ${response.status}`)
            return {
              symbol,
              price: 'N/A',
              high24h: 'N/A',
              low24h: 'N/A',
              timestamp: 0,
              success: false
            }
          }
        } catch (error) {
          console.error(`Error fetching price for ${symbol}:`, error)
          return {
            symbol,
            price: 'N/A',
            high24h: 'N/A',
            low24h: 'N/A',
            timestamp: 0,
            success: false
          }
        }
      })
      
      // Wait for all price fetches to complete
      const results = await Promise.all(pricePromises)
      
      // Process results
      results.forEach(result => {
        prices[result.symbol] = result.price
        high24h[result.symbol] = result.high24h
        low24h[result.symbol] = result.low24h
        timestamps[result.symbol] = result.timestamp
      })
      
      // Update state with new data
      setSymbolPrices(prev => ({ ...prev, ...prices }))
      setPriceTimestamps(prev => ({ ...prev, ...timestamps }))
      setSymbol24hHigh(prev => ({ ...prev, ...high24h }))
      setSymbol24hLow(prev => ({ ...prev, ...low24h }))
      
      // Reduced logging to prevent console spam
      if (process.env.NODE_ENV === 'development') {
        console.log(`✅ Updated prices for ${symbols.length} symbols at ${new Date().toLocaleTimeString()}`)
      }
    } catch (error) {
      console.error('Error fetching symbol prices:', error)
    } finally {
      setIsUpdating(false)
    }
  }

  const isPriceFresh = (symbol) => {
    const timestamp = priceTimestamps[symbol]
    if (!timestamp || timestamp === 0) return false
    const currentTime = Date.now()
    const tenMinutes = 10 * 60 * 1000 // 10 minutes in milliseconds
    return (currentTime - timestamp) < tenMinutes
  }

  const fetchExpandedPriceData = async (symbol) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/binance/ticker/24hr?symbol=${symbol}`)
      if (response.ok) {
        const data = await response.json()
        const priceData = {
          currentPrice: parseFloat(data.lastPrice),
          high24h: parseFloat(data.highPrice),
          low24h: parseFloat(data.lowPrice),
          change24h: parseFloat(data.priceChangePercent),
          volume24h: parseFloat(data.volume),
          timestamp: Date.now()
        }
        setExpandedPriceData(prev => ({
          ...prev,
          [symbol]: priceData
        }))
        return priceData
      }
    } catch (error) {
      console.error(`Error fetching expanded price data for ${symbol}:`, error)
    }
    return null
  }

  const toggleExpanded = (symbol) => {
    const newExpanded = new Set(expandedSymbols)
    if (newExpanded.has(symbol)) {
      newExpanded.delete(symbol)
    } else {
      newExpanded.add(symbol)
      // Fetch price data when expanding
      fetchExpandedPriceData(symbol)
    }
    setExpandedSymbols(newExpanded)
  }

  const loadAnalyticsData = async () => {
    try {
      // Reduced logging to prevent console spam
      if (process.env.NODE_ENV === 'development') {
        console.log('📊 Loading analytics data...')
      }

      // Create mock analytics data
      const mockAnalytics = {
        portfolio_size: mySymbols.length,
        average_score: 0.75,
        total_score: mySymbols.length * 0.75,
        average_performance: 0.12,
        max_drawdown: 0.08,
        average_volatility: 0.15,
        replacement_candidates: Math.min(2, mySymbols.length),
        top_performers: mySymbols.slice(0, 3).map((symbol, index) => ({
          symbol,
          score: 0.85 - (index * 0.05),
          performance: 0.15 - (index * 0.02)
        })),
        lowest_scorers: mySymbols.slice(-2).map((symbol, index) => ({
          symbol,
          score: 0.65 - (index * 0.05),
          performance: 0.05 - (index * 0.02)
        })),
        last_updated: new Date().toISOString()
      }

      setAnalyticsData(mockAnalytics)

      // Create mock symbol scores
      const mockScores = mySymbols.map((symbol, index) => ({
        symbol: symbol,
        technical_score: 0.6 + (Math.random() * 0.3),
        fundamental_score: 0.5 + (Math.random() * 0.4),
        market_structure_score: 0.4 + (Math.random() * 0.5),
        risk_score: 0.3 + (Math.random() * 0.6),
        composite_score: 0.7 + (Math.random() * 0.2),
        confidence_level: 0.7 + (Math.random() * 0.2),
        rank: index + 1,
        calculation_timestamp: new Date().toISOString()
      })).sort((a, b) => b.composite_score - a.composite_score)

      setSymbolScores(mockScores)

      // Create mock performance data
      const mockPerformance = {}
      mySymbols.forEach(symbol => {
        mockPerformance[symbol] = {
          totalReturn: (Math.random() * 40 - 20).toFixed(2),
          recentReturn: (Math.random() * 20 - 10).toFixed(2),
          volatility: (Math.random() * 30 + 10).toFixed(2),
          maxDrawdown: (Math.random() * 25 + 5).toFixed(2),
          sharpeRatio: (Math.random() * 2 + 0.5).toFixed(2),
          currentPrice: (Math.random() * 1000 + 100).toFixed(2),
          priceChange: (Math.random() * 10 - 5).toFixed(2)
        }
      })
      setPerformanceData(mockPerformance)

    } catch (error) {
      console.error('Error loading analytics data:', error)
    }
  }

  const loadMySymbols = async () => {
    try {
      console.log('🔄 Loading My Symbols...')
      const response = await fetch(`${API_BASE}/api/futures-symbols/my-symbols/current`)
      if (response.ok) {
        const data = await response.json()
        console.log('📊 My Symbols API Response:', data)
        const symbols = data.portfolio?.symbols || []
        console.log('🎯 Setting My Symbols:', symbols)
        setMySymbols(symbols)
      } else {
        console.error('❌ Failed to load My Symbols:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('❌ Error loading my symbols:', error)
    }
  }

  const loadKucoinSymbols = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/futures-symbols/kucoin/available`)
      if (response.ok) {
        const data = await response.json()
        setKucoinSymbols(data.symbols || [])
      }
    } catch (error) {
      console.error('Error loading KuCoin symbols:', error)
    }
  }

  const loadBinanceSymbols = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/futures-symbols/binance/available`)
      if (response.ok) {
        const data = await response.json()
        setBinanceSymbols(data.symbols || [])
      }
    } catch (error) {
      console.error('Error loading Binance symbols:', error)
    }
  }

  const loadCommonSymbols = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/futures-symbols/common`)
      if (response.ok) {
        const data = await response.json()
        setCommonSymbols(data.symbols || [])
      }
    } catch (error) {
      console.error('Error loading common symbols:', error)
    }
  }

  const addSymbol = async (symbol) => {
    try {
      console.log(`🎯 addSymbol called with: "${symbol}"`)
      console.log(`🔍 Current search query: "${symbolQuery}"`)
      console.log(`🔍 Filtered common symbols: ${filteredCommon.slice(0, 5)}`)
      
      // Prevent multiple rapid clicks
      if (isSymbolUpdating) {
        return
      }
      
      setIsSymbolUpdating(true)
      
      // Get current symbols and add the new one
      const currentSymbols = [...mySymbols]
      if (!currentSymbols.includes(symbol)) {
        currentSymbols.push(symbol)
      }

      const response = await fetch(`${API_BASE}/api/futures-symbols/my-symbols/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentSymbols)
      })

      if (response.ok) {
        const responseData = await response.json()
        console.log(`✅ Add Symbol API Response:`, responseData)
        // Reload symbols to ensure UI is in sync with backend
        await loadMySymbols()
        console.log(`✅ Added ${symbol} to portfolio`)
      } else {
        const errorData = await response.json()
        console.error(`❌ Failed to add ${symbol}:`, errorData)
      }
    } catch (error) {
      console.error('Error adding symbol:', error)
    } finally {
      // Add a small delay to prevent rapid clicks
      setTimeout(() => {
        setIsSymbolUpdating(false)
      }, 300)
    }
  }

  const removeSymbol = async (symbol) => {
    try {
      // Prevent multiple rapid clicks
      if (isSymbolUpdating) return
      
      setIsSymbolUpdating(true)
      
      // Get current symbols and remove the specified one
      const currentSymbols = mySymbols.filter(s => s !== symbol)

      const response = await fetch(`${API_BASE}/api/futures-symbols/my-symbols/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentSymbols)
      })

      if (response.ok) {
        const responseData = await response.json()
        console.log(`✅ Remove Symbol API Response:`, responseData)
        // Reload symbols to ensure UI is in sync with backend
        await loadMySymbols()
        console.log(`✅ Removed ${symbol} from portfolio`)
      } else {
        const errorData = await response.json()
        console.error(`❌ Failed to remove ${symbol}:`, errorData)
      }
    } catch (error) {
      console.error('Error removing symbol:', error)
    } finally {
      // Add a small delay to prevent rapid clicks
      setTimeout(() => {
        setIsSymbolUpdating(false)
      }, 300)
    }
  }

  const filteredKucoin = useMemo(() =>
    kucoinSymbols.filter(s => s.toLowerCase().includes(symbolQuery.toLowerCase())),
    [kucoinSymbols, symbolQuery]
  )

  const filteredBinance = useMemo(() => {
    const filtered = binanceSymbols.filter(s => s.toLowerCase().includes(symbolQuery.toLowerCase()))
    if (symbolQuery.toLowerCase() === 'xrp') {
      console.log('🔍 Binance search for XRP:')
      console.log('🔍 All Binance symbols count:', binanceSymbols.length)
      console.log('🔍 Filtered symbols:', filtered.slice(0, 5))
      console.log('🔍 First 10 Binance symbols:', binanceSymbols.slice(0, 10))
    }
    return filtered
  }, [binanceSymbols, symbolQuery])

  const filteredCommon = useMemo(() =>
    commonSymbols.filter(s => s.toLowerCase().includes(symbolQuery.toLowerCase())),
    [commonSymbols, symbolQuery]
  )

  const filteredMy = useMemo(() =>
    mySymbols.filter(s => s.toLowerCase().includes(myQuery.toLowerCase())),
    [mySymbols, myQuery]
  )

  const symbolsTabs = [
    { id: 'my-symbols', label: '🎯 My Symbols' },
    { id: 'kucoin', label: '🔵 KuCoin' },
    { id: 'binance', label: '🟡 Binance' },
    { id: 'both-exchanges', label: '🔄 Both Exchanges' },
    { id: 'charts', label: '📈 Charts' }
  ]

  return (
    <div className="tab-content">
      <div className="card" style={{ 
        padding: '30px',
        margin: '2px 20px 20px 2px',
        minHeight: '90vh',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: '20px',
        border: '2px solid rgba(255,255,255,0.2)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
      }}>
        <div className="card-header" style={{ marginBottom: '30px' }}>
          <div className="card-title" style={{ fontSize: '2rem' }}>
            <span>📊</span>
            Symbols Management
          </div>
          <div className="card-subtitle" style={{ fontSize: '1.1rem', marginTop: '10px' }}>
            Manage your tradeable symbols and browse futures lists
          </div>
          <div className="card-badge" style={{ fontSize: '1rem', padding: '8px 16px' }}>Portfolio</div>
        </div>

        <div className="card-content" style={{ padding: '20px' }}>
          {/* Three Main Cards - Horizontal Cards Stacked Vertically */}
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column',
            gap: '30px'
          }}>
            
            {/* Symbols Management Card - Horizontal */}
            <div className="card" style={{ width: '100%' }}>
              <div className="card-header">
                <div className="card-title">
                  <span>🎯</span>
                  Symbols Management
                </div>
                <div className="card-badge">Active</div>
              </div>
              <div className="card-content">
                {/* Sub-tabs for Symbols Management */}
                <div className="card-grid card-grid-4" style={{ marginBottom: '20px' }}>
                  {symbolsTabs.map((tab) => (
                    <button
                      key={tab.id}
                      className={`card ${symbolsTab === tab.id ? 'card-active' : ''}`}
                      onClick={() => setSymbolsTab(tab.id)}
                      style={{ padding: '10px', fontSize: '0.9rem' }}
                    >
                      <div className="card-title">
                        <span>{tab.label.split(' ')[0]}</span>
                        {tab.label.split(' ').slice(1).join(' ')}
                      </div>
                    </button>
                  ))}
                </div>

                {/* Symbols Management Content */}
                {symbolsTab === 'my-symbols' && (
                  <div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center', 
                      marginBottom: '15px' 
                    }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px',
                        color: 'rgba(255,255,255,0.8)',
                        fontSize: '0.9rem'
                      }}>
                        <div style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: isUpdating ? '#f59e0b' : '#10b981',
                          animation: isUpdating ? 'pulse 1s infinite' : 'none'
                        }} />
                        {isUpdating ? 'Updating prices...' : 'Real-time data active'}
                      </div>
                      <div style={{ 
                        color: 'rgba(255,255,255,0.6)', 
                        fontSize: '0.8rem' 
                      }}>
                        Updates every 1min
                      </div>
                    </div>
                    
                    {/* Score Update Status */}
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px', 
                      marginBottom: '16px',
                      padding: '8px 12px',
                      background: 'rgba(139, 92, 246, 0.1)',
                      border: '1px solid rgba(139, 92, 246, 0.3)',
                      borderRadius: '8px',
                      fontSize: '0.85rem'
                    }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: '#8b5cf6',
                        animation: 'pulse 2s infinite'
                      }} />
                      <span style={{ color: '#8b5cf6', fontWeight: '500' }}>
                        Fixed Scoring System
                      </span>
                      <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem' }}>
                        Stable scores | Last: {new Date(lastScoreUpdate).toLocaleTimeString()}
                      </span>
                    </div>
                    <input
                      type="text"
                      placeholder="Search my symbols..."
                      value={myQuery}
                      onChange={(e) => setMyQuery(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '1rem',
                        borderRadius: '8px',
                        border: '2px solid rgba(255,255,255,0.2)',
                        background: 'rgba(255,255,255,0.1)',
                        color: '#ffffff',
                        marginBottom: '15px'
                      }}
                    />
                    <div className="card-grid card-grid-3" style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(3, 1fr)', 
                      gap: '1.5rem',
                      marginBottom: '2rem'
                    }}>
                      {filteredMy.map((symbol) => (
                        <div key={symbol} className="card" style={{ 
                          position: 'relative',
                          background: 'linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(42, 42, 42, 0.95) 100%)',
                          border: '1px solid rgba(139, 92, 246, 0.2)',
                          borderRadius: '12px',
                          padding: '16px',
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
                          backdropFilter: 'blur(10px)',
                          overflow: 'hidden'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'translateY(-4px)'
                          e.currentTarget.style.boxShadow = '0 12px 40px rgba(139, 92, 246, 0.2)'
                          e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.4)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)'
                          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.3)'
                          e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.2)'
                        }}
                      >


                        {/* Remove Button */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            e.preventDefault()
                            removeSymbol(symbol)
                          }}
                          style={{
                            position: 'absolute',
                            top: '12px',
                            right: '12px',
                            width: '28px',
                            height: '28px',
                            background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '50%',
                            cursor: 'pointer',
                            fontSize: '14px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 10,
                            transition: 'all 0.2s ease',
                            boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)'
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.transform = 'scale(1.15)'
                            e.target.style.boxShadow = '0 6px 16px rgba(239, 68, 68, 0.5)'
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.transform = 'scale(1)'
                            e.target.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.3)'
                          }}
                        >
                          ✕
                        </button>

                        {/* Card Header */}
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'space-between',
                          marginBottom: '12px',
                          paddingBottom: '8px',
                          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                          paddingRight: '40px' // Make space for delete button
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                            {/* Status Dot */}
                            <div style={{
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              backgroundColor: isPriceFresh(symbol) ? '#10b981' : '#ef4444',
                              boxShadow: isPriceFresh(symbol) 
                                ? '0 0 8px rgba(16, 185, 129, 0.6)' 
                                : '0 0 8px rgba(239, 68, 68, 0.6)',
                              animation: isPriceFresh(symbol) ? 'pulse 2s infinite' : 'none'
                            }} />
                            
                            {/* Symbol Name */}
                            <div style={{
                              fontSize: '1rem',
                              fontWeight: '600',
                              color: '#ffffff',
                              letterSpacing: '0.5px'
                            }}>
                              {symbol}
                            </div>
                          </div>
                          
                          {/* Scoring Badge - Moved to left side */}
                          <div style={{
                            background: getSymbolRank(symbol) === 1 
                              ? 'linear-gradient(135deg, #ffd700 0%, #ffed4e 100%)' // Gold
                              : getSymbolRank(symbol) === 2
                              ? 'linear-gradient(135deg, #c0c0c0 0%, #e5e5e5 100%)' // Silver
                              : getSymbolRank(symbol) === 3
                              ? 'linear-gradient(135deg, #cd7f32 0%, #daa520 100%)' // Bronze
                              : 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', // Purple
                            color: getSymbolRank(symbol) <= 3 ? '#000000' : '#ffffff',
                            padding: '6px 12px',
                            borderRadius: '20px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            boxShadow: getSymbolRank(symbol) === 1 
                              ? '0 2px 8px rgba(255, 215, 0, 0.4)' // Gold shadow
                              : getSymbolRank(symbol) === 2
                              ? '0 2px 8px rgba(192, 192, 192, 0.4)' // Silver shadow
                              : getSymbolRank(symbol) === 3
                              ? '0 2px 8px rgba(205, 127, 50, 0.4)' // Bronze shadow
                              : '0 2px 8px rgba(139, 92, 246, 0.3)', // Purple shadow
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            marginLeft: 'auto',
                            marginRight: '8px', // Space from delete button
                            border: getSymbolRank(symbol) === 1 
                              ? '1px solid #ffd700' // Gold border
                              : getSymbolRank(symbol) === 2
                              ? '1px solid #c0c0c0' // Silver border
                              : getSymbolRank(symbol) === 3
                              ? '1px solid #cd7f32' // Bronze border
                              : 'none'
                          }}>
                            <span>Score:</span>
                            <span>{getSymbolScore(symbol)}</span>
                            <span style={{ marginLeft: '8px', opacity: 0.8 }}>|</span>
                            <span style={{ marginLeft: '8px' }}>Rank:</span>
                            <span style={{
                              fontWeight: '700',
                              textShadow: getSymbolRank(symbol) <= 3 ? '0 1px 2px rgba(0,0,0,0.3)' : 'none'
                            }}>
                              {getSymbolRank(symbol)}
                            </span>
                          </div>
                        </div>

                        {/* Card Content */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {/* Current Price with Chart Button */}
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                          }}>
                            <div style={{
                              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%)',
                              color: '#3b82f6',
                              border: '1px solid rgba(59, 130, 246, 0.3)',
                              borderRadius: '8px',
                              padding: '12px',
                              textAlign: 'center',
                              fontWeight: '700',
                              fontSize: '1.1rem',
                              letterSpacing: '0.5px',
                              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.2)',
                              backdropFilter: 'blur(5px)',
                              flex: 1
                            }}>
                              ${symbolPrices[symbol] || 'Loading...'}
                            </div>
                            
                            {/* Expand/Collapse Button */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                e.preventDefault()
                                toggleExpanded(symbol)
                              }}
                              style={{
                                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '8px',
                                padding: '12px 16px',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                                fontWeight: '600',
                                boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
                                transition: 'all 0.2s ease'
                              }}
                            >
                              {expandedSymbols.has(symbol) ? 'Collapse' : 'Expand'}
                            </button>
                            

                          </div>
                          
                          {/* 24h Range Badges */}
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            {/* 24h Low */}
                            <div style={{ 
                              background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%)',
                              color: '#ef4444',
                              border: '1px solid rgba(239, 68, 68, 0.3)',
                              borderRadius: '6px',
                              fontSize: '0.75rem',
                              padding: '8px 12px',
                              flex: 1,
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              fontWeight: '500',
                              boxShadow: '0 2px 8px rgba(239, 68, 68, 0.2)',
                              backdropFilter: 'blur(5px)'
                            }}>
                              <span style={{ opacity: 0.8 }}>Low:</span>
                              <span style={{ fontWeight: '600' }}>${symbol24hLow[symbol] || 'N/A'}</span>
                            </div>
                            
                            {/* 24h High */}
                            <div style={{ 
                              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)',
                              color: '#10b981',
                              border: '1px solid rgba(16, 185, 129, 0.3)',
                              borderRadius: '6px',
                              fontSize: '0.75rem',
                              padding: '8px 12px',
                              flex: 1,
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              fontWeight: '500',
                              boxShadow: '0 2px 8px rgba(16, 185, 129, 0.2)',
                              backdropFilter: 'blur(5px)'
                            }}>
                              <span style={{ opacity: 0.8 }}>High:</span>
                              <span style={{ fontWeight: '600' }}>${symbol24hHigh[symbol] || 'N/A'}</span>
                            </div>
                          </div>

                          {/* Expanded Card Content */}
                          {expandedSymbols.has(symbol) && (
                            <div style={{
                              marginTop: '12px',
                              padding: '16px',
                              background: 'rgba(255, 255, 255, 0.05)',
                              borderRadius: '12px',
                              border: '1px solid rgba(255, 255, 255, 0.1)',
                              backdropFilter: 'blur(10px)'
                            }}>
                              {/* Price Data Section */}
                              <div style={{ marginBottom: '16px' }}>
                                <div style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '8px',
                                  marginBottom: '12px',
                                  fontSize: '1rem',
                                  fontWeight: '600',
                                  color: '#ffffff'
                                }}>
                                  <span>📊</span>
                                  <span>Price Data</span>
                                </div>
                                
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                  {/* Current Price */}
                                  <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '8px 12px',
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    borderRadius: '8px',
                                    border: '1px solid rgba(59, 130, 246, 0.2)'
                                  }}>
                                    <span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Current Price:</span>
                                    <span style={{ 
                                      color: '#3b82f6', 
                                      fontWeight: '600',
                                      fontSize: '1.1rem'
                                    }}>
                                      ${expandedPriceData[symbol]?.currentPrice?.toFixed(2) || 'N/A'}
                                    </span>
                                  </div>
                                  
                                  {/* 24h High */}
                                  <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '8px 12px',
                                    background: 'rgba(16, 185, 129, 0.1)',
                                    borderRadius: '8px',
                                    border: '1px solid rgba(16, 185, 129, 0.2)'
                                  }}>
                                    <span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>24h High:</span>
                                    <span style={{ 
                                      color: '#10b981', 
                                      fontWeight: '600'
                                    }}>
                                      ${expandedPriceData[symbol]?.high24h?.toFixed(2) || 'N/A'}
                                    </span>
                                  </div>
                                  
                                  {/* 24h Low */}
                                  <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '8px 12px',
                                    background: 'rgba(239, 68, 68, 0.1)',
                                    borderRadius: '8px',
                                    border: '1px solid rgba(239, 68, 68, 0.2)'
                                  }}>
                                    <span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>24h Low:</span>
                                    <span style={{ 
                                      color: '#ef4444', 
                                      fontWeight: '600'
                                    }}>
                                      ${expandedPriceData[symbol]?.low24h?.toFixed(2) || 'N/A'}
                                    </span>
                                  </div>
                                  
                                  {/* 24h Change */}
                                  <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '8px 12px',
                                    background: expandedPriceData[symbol]?.change24h >= 0 
                                      ? 'rgba(16, 185, 129, 0.1)' 
                                      : 'rgba(239, 68, 68, 0.1)',
                                    borderRadius: '8px',
                                    border: expandedPriceData[symbol]?.change24h >= 0 
                                      ? '1px solid rgba(16, 185, 129, 0.2)' 
                                      : '1px solid rgba(239, 68, 68, 0.2)'
                                  }}>
                                    <span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>24h Change:</span>
                                    <span style={{ 
                                      color: expandedPriceData[symbol]?.change24h >= 0 ? '#10b981' : '#ef4444', 
                                      fontWeight: '600'
                                    }}>
                                      {expandedPriceData[symbol]?.change24h ? 
                                        `${expandedPriceData[symbol].change24h >= 0 ? '+' : ''}${expandedPriceData[symbol].change24h.toFixed(2)}%` : 
                                        'N/A'
                                      }
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      ))}
                    </div>
                    {filteredMy.length === 0 && (
                      <div style={{ textAlign: 'center', padding: '20px', color: 'rgba(255,255,255,0.7)' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '10px' }}>📭</div>
                        <div>No symbols in portfolio</div>
                      </div>
                    )}
                  </div>
                )}

                {symbolsTab === 'kucoin' && (
                  <div>
                    <input
                      type="text"
                      placeholder="Search KuCoin symbols..."
                      value={symbolQuery}
                      onChange={(e) => {
                        const value = e.target.value
                        console.log(`🔍 KuCoin search input changed: "${value}"`)
                        setSymbolQuery(value)
                      }}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '1rem',
                        borderRadius: '8px',
                        border: '2px solid rgba(255,255,255,0.2)',
                        background: 'rgba(255,255,255,0.1)',
                        color: '#ffffff',
                        marginBottom: '15px'
                      }}
                    />
                    <div className="card-grid card-grid-5">
                      {filteredKucoin.slice(0, 12).map((symbol) => {
                        const isInPortfolio = mySymbols.includes(symbol)
                        const canAdd = canAddMore && !isInPortfolio
                        
                        return (
                          <div key={symbol} className="card">
                            <div className="card-header">
                              <div className="card-title">
                                <span>📈</span>
                                {symbol}
                              </div>
                              <div className="card-badge">
                                {isInPortfolio ? 'Added' : 'Available'}
                              </div>
                            </div>
                            <div className="card-content">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  e.preventDefault()
                                  if (canAdd) addSymbol(symbol)
                                }}
                                disabled={!canAdd}
                                style={{
                                  width: '100%',
                                  padding: '8px',
                                  background: isInPortfolio 
                                    ? 'rgba(16, 185, 129, 0.2)' 
                                    : canAdd 
                                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                                      : 'rgba(255,255,255,0.1)',
                                  color: isInPortfolio 
                                    ? '#10b981' 
                                    : canAdd 
                                      ? '#ffffff' 
                                      : 'rgba(255,255,255,0.5)',
                                  border: isInPortfolio ? '1px solid #10b981' : 'none',
                                  borderRadius: '6px',
                                  cursor: canAdd ? 'pointer' : 'not-allowed',
                                  fontSize: '0.9rem'
                                }}
                              >
                                {isInPortfolio ? '✅ Added' : canAdd ? '➕ Add' : '❌ Full'}
                              </button>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    {filteredKucoin.length > 12 && (
                      <div style={{ textAlign: 'center', marginTop: '15px', color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>
                        Showing 12 of {filteredKucoin.length} symbols
                      </div>
                    )}
                  </div>
                )}

                {symbolsTab === 'binance' && (
                  <div>
                    <input
                      type="text"
                      placeholder="Search Binance symbols..."
                      value={symbolQuery}
                      onChange={(e) => {
                        const value = e.target.value
                        console.log(`🔍 Search input changed: "${value}"`)
                        setSymbolQuery(value)
                      }}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '1rem',
                        borderRadius: '8px',
                        border: '2px solid rgba(255,255,255,0.2)',
                        background: 'rgba(255,255,255,0.1)',
                        color: '#ffffff',
                        marginBottom: '15px'
                      }}
                    />
                    <div className="card-grid card-grid-5">
                      {filteredBinance.slice(0, 12).map((symbol) => {
                        const isInPortfolio = mySymbols.includes(symbol)
                        const canAdd = canAddMore && !isInPortfolio
                        
                        return (
                          <div key={symbol} className="card">
                            <div className="card-header">
                              <div className="card-title">
                                <span>📈</span>
                                {symbol}
                              </div>
                              <div className="card-badge">
                                {isInPortfolio ? 'Added' : 'Available'}
                              </div>
                            </div>
                            <div className="card-content">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  e.preventDefault()
                                  if (canAdd) addSymbol(symbol)
                                }}
                                disabled={!canAdd}
                                style={{
                                  width: '100%',
                                  padding: '8px',
                                  background: isInPortfolio 
                                    ? 'rgba(16, 185, 129, 0.2)' 
                                    : canAdd 
                                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                                      : 'rgba(255,255,255,0.1)',
                                  color: isInPortfolio 
                                    ? '#10b981' 
                                    : canAdd 
                                      ? '#ffffff' 
                                      : 'rgba(255,255,255,0.5)',
                                  border: isInPortfolio ? '1px solid #10b981' : 'none',
                                  borderRadius: '6px',
                                  cursor: canAdd ? 'pointer' : 'not-allowed',
                                  fontSize: '0.9rem'
                                }}
                              >
                                {isInPortfolio ? '✅ Added' : canAdd ? '➕ Add' : '❌ Full'}
                              </button>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    {filteredBinance.length > 12 && (
                      <div style={{ textAlign: 'center', marginTop: '15px', color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>
                        Showing 12 of {filteredBinance.length} symbols
                      </div>
                    )}
                  </div>
                )}

                {symbolsTab === 'both-exchanges' && (
                  <div>
                    <input
                      type="text"
                      placeholder="Search common symbols..."
                      value={symbolQuery}
                      onChange={(e) => {
                        const value = e.target.value
                        console.log(`🔍 Common symbols search input changed: "${value}"`)
                        setSymbolQuery(value)
                      }}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '1rem',
                        borderRadius: '8px',
                        border: '2px solid rgba(255,255,255,0.2)',
                        background: 'rgba(255,255,255,0.1)',
                        color: '#ffffff',
                        marginBottom: '15px'
                      }}
                    />
                    <div className="card-grid card-grid-5">
                      {filteredCommon.slice(0, 12).map((symbol) => {
                        const isInPortfolio = mySymbols.includes(symbol)
                        const canAdd = canAddMore && !isInPortfolio
                        
                        return (
                          <div key={symbol} className="card">
                            <div className="card-header">
                              <div className="card-title">
                                <span>📈</span>
                                {symbol}
                              </div>
                              <div className="card-badge">
                                {isInPortfolio ? 'Added' : 'Common'}
                              </div>
                            </div>
                            <div className="card-content">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  e.preventDefault()
                                  if (canAdd) addSymbol(symbol)
                                }}
                                disabled={!canAdd}
                                style={{
                                  width: '100%',
                                  padding: '8px',
                                  background: isInPortfolio 
                                    ? 'rgba(16, 185, 129, 0.2)' 
                                    : canAdd 
                                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                                      : 'rgba(255,255,255,0.1)',
                                  color: isInPortfolio 
                                    ? '#10b981' 
                                    : canAdd 
                                      ? '#ffffff' 
                                      : 'rgba(255,255,255,0.5)',
                                  border: isInPortfolio ? '1px solid #10b981' : 'none',
                                  borderRadius: '6px',
                                  cursor: canAdd ? 'pointer' : 'not-allowed',
                                  fontSize: '0.9rem'
                                }}
                              >
                                {isInPortfolio ? '✅ Added' : canAdd ? '➕ Add' : '❌ Full'}
                              </button>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    {filteredCommon.length > 12 && (
                      <div style={{ textAlign: 'center', marginTop: '15px', color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>
                        Showing 12 of {filteredCommon.length} symbols
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>



            {/* Analytics Card - Horizontal */}
            <div className="card" style={{ width: '100%' }}>
              <div className="card-header">
                <div className="card-title">
                  <span>📊</span>
                  Analytics
                </div>
                <div className="card-badge">Real-time</div>
              </div>
              <div className="card-content">
                {analyticsData ? (
                  <div style={{ display: 'flex', gap: '20px' }}>
                    {/* Portfolio Overview */}
                    <div style={{ flex: '1' }}>
                      <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '15px', color: 'rgba(255,255,255,0.9)' }}>
                        Portfolio Overview
                      </div>
                      <div className="card-grid card-grid-3">
                        <div className="card">
                          <div className="card-header">
                            <div className="card-title">
                              Portfolio
                            </div>
                          </div>
                          <div className="card-content">
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>
                              {analyticsData.portfolio_size}/10
                            </div>
                            <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                              Symbols
                            </div>
                          </div>
                        </div>
                        <div className="card">
                          <div className="card-header">
                            <div className="card-title">
                              Avg Score
                            </div>
                          </div>
                          <div className="card-content">
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f59e0b' }}>
                              {(analyticsData.average_score * 100).toFixed(1)}%
                            </div>
                            <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                              Performance
                            </div>
                          </div>
                        </div>
                        <div className="card">
                          <div className="card-header">
                            <div className="card-title">
                              Total Score
                            </div>
                          </div>
                          <div className="card-content">
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>
                              {analyticsData.total_score.toFixed(1)}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                              Combined
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Top Performers */}
                    <div style={{ flex: '1' }}>
                      <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '15px', color: 'rgba(255,255,255,0.9)' }}>
                        Top Performers
                      </div>
                      {analyticsData.top_performers.slice(0, 5).map((performer, index) => (
                        <div key={performer.symbol} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '12px',
                          marginBottom: '8px',
                          background: 'rgba(255,255,255,0.05)',
                          borderRadius: '8px',
                          border: '1px solid rgba(255,255,255,0.1)'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <div style={{ 
                              fontSize: '1.2rem', 
                              color: index === 0 ? '#fbbf24' : index === 1 ? '#9ca3af' : '#b45309'
                            }}>
                              {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                            </div>
                            <div style={{ fontSize: '1rem', color: 'rgba(255,255,255,0.9)', fontWeight: '600' }}>
                              {performer.symbol}
                            </div>
                          </div>
                          <div style={{ fontSize: '1rem', color: '#10b981', fontWeight: 'bold' }}>
                            +{(performer.performance * 100).toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255,255,255,0.7)' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📊</div>
                    <div style={{ fontSize: '1.2rem', marginBottom: '10px' }}>No portfolio data</div>
                    <div style={{ fontSize: '0.9rem' }}>Add symbols to see analytics</div>
                  </div>
                )}
              </div>
            </div>

            {/* Professional Alerts Card */}
            <div className="card" style={{ 
              width: '100%',
              background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)',
              border: '2px solid rgba(255,255,255,0.15)',
              boxShadow: '0 25px 50px rgba(0,0,0,0.4)'
            }}>
              <div className="card-header" style={{ 
                padding: '25px 30px 20px 30px',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div className="card-title" style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '8px' }}>
                      <span style={{ marginRight: '12px', fontSize: '2rem' }}>🔔</span>
                      Professional Trading Alerts
                    </div>
                    <div style={{ 
                      fontSize: '1rem', 
                      color: 'rgba(255,255,255,0.7)',
                      fontWeight: '400'
                    }}>
                      Real-time technical analysis alerts and notifications
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', justifyContent: 'flex-end' }}>
                    <div className="card-badge" style={{ 
                      background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                      padding: '8px 16px',
                      borderRadius: '20px',
                      fontSize: '0.9rem',
                      fontWeight: '600'
                    }}>
                      Live Alerts
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      color: 'rgba(255,255,255,0.6)',
                      fontSize: '0.9rem'
                    }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: '#ef4444',
                        animation: 'pulse 1s infinite'
                      }} />
                      Active Monitoring
                    </div>
                  </div>
                </div>
              </div>

              <div className="card-content" style={{ padding: '30px' }}>
                {/* Enhanced Alerts System Component */}
                <EnhancedAlertsSystem 
                  symbol={selectedSymbol}
                  onAlertTriggered={(alert) => {
                    console.log('Alert triggered:', alert);
                    // You can add additional handling here if needed
                  }}
                />

                {/* Alert Types Info */}
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  marginTop: '20px',
                  padding: '15px 20px',
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '10px',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '20px',
                    fontSize: '0.9rem',
                    color: 'rgba(255,255,255,0.6)'
                  }}>
                    <span>🔄 <strong>EMA Crossovers</strong></span>
                    <span>📈 <strong>RSI Alerts</strong></span>
                    <span>📊 <strong>MACD Signals</strong></span>
                    <span>⚡ <strong>Price Breakouts</strong></span>
                  </div>
                  <div style={{ 
                    fontSize: '0.85rem',
                    color: 'rgba(255,255,255,0.5)',
                    fontStyle: 'italic'
                  }}>
                    Real-time monitoring • Instant notifications
                  </div>
                </div>
              </div>
            </div>

            {/* Professional Charts Card */}
            <div className="card" style={{ 
              width: '100%',
              background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)',
              border: '2px solid rgba(255,255,255,0.15)',
              boxShadow: '0 25px 50px rgba(0,0,0,0.4)'
            }}>
              <div className="card-header" style={{ 
                padding: '25px 30px 20px 30px',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div className="card-title" style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '8px' }}>
                      <span style={{ marginRight: '12px', fontSize: '2rem' }}>📈</span>
                      Professional Trading Charts
                    </div>
                    <div style={{ 
                      fontSize: '1rem', 
                      color: 'rgba(255,255,255,0.7)',
                      fontWeight: '400'
                    }}>
                      Advanced technical analysis with real-time market data
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', justifyContent: 'flex-end' }}>
                    <div className="card-badge" style={{ 
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      padding: '8px 16px',
                      borderRadius: '20px',
                      fontSize: '0.9rem',
                      fontWeight: '600'
                    }}>
                      Real-time
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      color: 'rgba(255,255,255,0.6)',
                      fontSize: '0.9rem'
                    }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: chartLoading ? '#f59e0b' : '#10b981',
                        animation: chartLoading ? 'pulse 1s infinite' : 'none'
                      }} />
                      {chartLoading ? 'Loading...' : 'Live Data'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="card-content" style={{ padding: '30px' }}>
                {/* Chart Controls Section */}
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  marginBottom: '25px',
                  padding: '20px',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255,255,255,0.08)'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '20px' 
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ 
                        fontSize: '0.9rem', 
                        color: 'rgba(255,255,255,0.7)',
                        fontWeight: '500'
                      }}>
                        Symbol:
                      </span>
                      <select
                        value={selectedSymbol}
                        onChange={(e) => setSelectedSymbol(e.target.value)}
                        style={{
                          padding: '12px 16px',
                          fontSize: '1rem',
                          borderRadius: '8px',
                          border: '2px solid rgba(255,255,255,0.2)',
                          background: 'rgba(255,255,255,0.08)',
                          color: '#ffffff',
                          cursor: 'pointer',
                          fontWeight: '500',
                          minWidth: '120px',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseOver={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.4)'}
                        onMouseOut={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.2)'}
                      >
                        {mySymbols.map(symbol => (
                          <option key={symbol} value={symbol}>{symbol}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ 
                        fontSize: '0.9rem', 
                        color: 'rgba(255,255,255,0.7)',
                        fontWeight: '500'
                      }}>
                        Timeframe:
                      </span>
                      <select
                        value={chartTimeframe}
                        onChange={(e) => setChartTimeframe(e.target.value)}
                        style={{
                          padding: '12px 16px',
                          fontSize: '1rem',
                          borderRadius: '8px',
                          border: '2px solid rgba(255,255,255,0.2)',
                          background: 'rgba(255,255,255,0.08)',
                          color: '#ffffff',
                          cursor: 'pointer',
                          fontWeight: '500',
                          minWidth: '100px',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseOver={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.4)'}
                        onMouseOut={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.2)'}
                      >
                        <option value="15m">15m</option>
                        <option value="1h">1h</option>
                        <option value="4h">4h</option>
                        <option value="1D">1D</option>
                        <option value="24H">24H</option>
                      </select>
                    </div>
                  </div>
                  
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '15px',
                    color: 'rgba(255,255,255,0.7)', 
                    fontSize: '0.9rem',
                    fontWeight: '500'
                  }}>
                    <div style={{ 
                      padding: '8px 12px',
                      background: 'rgba(255,255,255,0.05)',
                      borderRadius: '6px',
                      border: '1px solid rgba(255,255,255,0.1)'
                    }}>
                      {chartLoading ? '⏳ Loading chart...' : chartData ? `📊 ${chartData.length} candles loaded` : '📈 Select symbol to load chart'}
                    </div>
                  </div>
                </div>

                {/* Chart Display Section */}
                <div style={{ 
                  height: '2000px', 
                  background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.9) 0%, rgba(17, 24, 39, 0.7) 100%)',
                  borderRadius: '16px',
                  border: '2px solid rgba(255,255,255,0.1)',
                  overflow: 'hidden',
                  boxShadow: 'inset 0 4px 20px rgba(0,0,0,0.3)',
                  position: 'relative'
                }}>
                  {chartData && chartData.length > 0 ? (
                    <SimpleChart
                      data={chartData}
                      symbol={selectedSymbol}
                      width="100%"
                      height="2000px"
                      timeframe={chartTimeframe}
                    />
                  ) : (
                    <div style={{ 
                      display: 'flex', 
                      flexDirection: 'column',
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      height: '100%',
                      color: 'rgba(255,255,255,0.7)',
                      fontSize: '1.1rem',
                      background: 'radial-gradient(circle at center, rgba(255,255,255,0.02) 0%, transparent 70%)',
                      gap: '20px'
                    }}>
                      <div style={{ 
                        textAlign: 'center',
                        padding: '40px',
                        background: 'rgba(255,255,255,0.03)',
                        borderRadius: '16px',
                        border: '1px solid rgba(255,255,255,0.08)',
                        backdropFilter: 'blur(10px)'
                      }}>
                        <div style={{ 
                          fontSize: '4rem', 
                          marginBottom: '20px',
                          filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.3))'
                        }}>📈</div>
                        <div style={{ 
                          fontSize: '1.3rem', 
                          fontWeight: '600',
                          marginBottom: '10px',
                          color: 'rgba(255,255,255,0.9)'
                        }}>
                          Professional Chart Ready
                        </div>
                        <div style={{ 
                          fontSize: '1rem', 
                          marginBottom: '15px',
                          color: 'rgba(255,255,255,0.7)'
                        }}>
                          Select a symbol from your portfolio to view advanced technical analysis
                        </div>
                        <div style={{ 
                          fontSize: '0.9rem',
                          color: 'rgba(255,255,255,0.5)',
                          fontStyle: 'italic'
                        }}>
                          Includes EMA, Bollinger Bands, RSI, MACD & more
                        </div>
                      </div>
                      
                      {/* Manual Load Chart Button for Testing */}
                      <button
                        onClick={() => {
                          console.log('🔧 Manual chart load triggered')
                          if (mySymbols.length > 0) {
                            const firstSymbol = mySymbols[0]
                            console.log(`🔧 Loading chart for first symbol: ${firstSymbol}`)
                            loadChartData(firstSymbol, '24H')
                          }
                        }}
                        style={{
                          padding: '12px 24px',
                          fontSize: '1rem',
                          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontWeight: '600',
                          boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
                        }}
                      >
                        🔧 Load BTCUSDT Chart (Test)
                      </button>
                    </div>
                  )}
                </div>

                {/* Chart Info Footer */}
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  marginTop: '20px',
                  padding: '15px 20px',
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '10px',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '20px',
                    fontSize: '0.9rem',
                    color: 'rgba(255,255,255,0.6)'
                  }}>
                    <span>🎯 <strong>Professional Analysis</strong></span>
                    <span>📊 <strong>Real-time Data</strong></span>
                    <span>🔔 <strong>Smart Alerts</strong></span>
                  </div>
                  <div style={{ 
                    fontSize: '0.85rem',
                    color: 'rgba(255,255,255,0.5)',
                    fontStyle: 'italic'
                  }}>
                    Powered by Binance API • Updated every minute
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>


      </div>
    </div>
  )
}

export default SymbolsManager


