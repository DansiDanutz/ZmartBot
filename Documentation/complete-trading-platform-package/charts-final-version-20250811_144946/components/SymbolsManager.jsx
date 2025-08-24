import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ZmartChart from './ZmartChart'
import ChartCard from './ChartCard'

const API_BASE = 'http://localhost:8000' // Fixed API base URL

async function safeJson(res) {
  try { return await res.json() } catch { return null }
}

async function fetchSymbols(path) {
  try {
    const r = await fetch(`${API_BASE}${path}`)
    if (!r.ok) return []
    const j = await safeJson(r)
    return Array.isArray(j?.symbols) ? j.symbols : []
  } catch {
    return []
  }
}

const Tabs = ({ tabs, active, onChange }) => (
  <div className="symbols-tabs">
    {tabs.map((t) => (
      <button
        key={t.id}
        className={`symbols-tab ${active === t.id ? 'active' : ''}`}
        onClick={() => onChange(t.id)}
      >
        {t.label}
      </button>
    ))}
  </div>
)

const SymbolCard = ({ symbol, marketData, onRemove }) => {
  const data = marketData[symbol]
  const isPositive = data?.priceChangePercent > 0
  const isNegative = data?.priceChangePercent < 0
  
  return (
    <div className="symbol-card-market">
      <div className="card-header">
        <h3 className="symbol-name">{symbol}</h3>
        <button className="card-remove" onClick={() => onRemove(symbol)}>×</button>
      </div>
      
      <div className="card-content">
        {data ? (
          <>
            <div className="price-section">
              <div className="current-price">${data.price.toFixed(2)}</div>
              <div className={`price-change ${isPositive ? 'positive' : isNegative ? 'negative' : 'neutral'}`}>
                {isPositive ? '+' : ''}{data.priceChangePercent.toFixed(2)}%
              </div>
            </div>
            
            <div className="price-details">
              <div className="price-row">
                <span className="label">24h High:</span>
                <span className="value">${data.high24h.toFixed(2)}</span>
              </div>
              <div className="price-row">
                <span className="label">24h Low:</span>
                <span className="value">${data.low24h.toFixed(2)}</span>
              </div>
              <div className="price-row">
                <span className="label">Volume:</span>
                <span className="value">${(data.quoteVolume / 1000000).toFixed(1)}M</span>
              </div>
            </div>
          </>
        ) : (
          <div className="loading-data">
            <div className="loading-spinner"></div>
            <span>Loading...</span>
          </div>
        )}
      </div>
    </div>
  )
}

const Dropdown = ({ label, options, onAdd, disabled, mySymbols = [], canAddMore = true }) => {
  const [value, setValue] = useState('')
  const canAddSelected = value && canAddMore && !disabled && !mySymbols.includes(value)
  return (
    <div className="dropdown">
      <label className="dropdown-label">{label}</label>
      <div className="dropdown-row">
        <select
          className="dropdown-select"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        >
          <option value="">Select a symbol</option>
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
        >
          Add
        </button>
      </div>
    </div>
  )
}

const SymbolsManager = () => {
  const navigate = useNavigate()
  const [active, setActive] = useState('my-symbols')
  const [loading, setLoading] = useState(false)
  const [mySymbols, setMySymbols] = useState([])
  const [kucoinSymbols, setKucoinSymbols] = useState([])
  const [binanceSymbols, setBinanceSymbols] = useState([])
  const [commonSymbols, setCommonSymbols] = useState([])
  const [symbolQuery, setSymbolQuery] = useState('')
  const [myQuery, setMyQuery] = useState('')
  const [analyticsData, setAnalyticsData] = useState(null)
  const [symbolScores, setSymbolScores] = useState([])
  const [replacementRecommendations, setReplacementRecommendations] = useState([])
  const [correlationData, setCorrelationData] = useState(null)
  const [portfolioAlerts, setPortfolioAlerts] = useState([])
  const [positionSizingData, setPositionSizingData] = useState(null)
  const [accountBalance, setAccountBalance] = useState(10000) // Default $10,000
  const [dataStatus, setDataStatus] = useState(null)
  const [dataLoading, setDataLoading] = useState(false)
  const [historicalData, setHistoricalData] = useState({})
  const [performanceData, setPerformanceData] = useState({})
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D')
  const [chartTimeframe, setChartTimeframe] = useState('1D')
  const [dailyUpdateStatus, setDailyUpdateStatus] = useState(null)
  const [dailyUpdateLoading, setDailyUpdateLoading] = useState(false)
  const [dailyUpdateLogs, setDailyUpdateLogs] = useState([])
  const [marketData, setMarketData] = useState({})
  const [marketDataLoading, setMarketDataLoading] = useState(false)
  const [chartData, setChartData] = useState({})
  const [chartDataLoading, setChartDataLoading] = useState(false)
  const [chartType, setChartType] = useState('candlestick')
  const maxMy = 10

  const canAddMore = useMemo(() => mySymbols.length < maxMy, [mySymbols, maxMy])

  // Load symbols on component mount
  useEffect(() => {
    loadAll()
  }, [])

  useEffect(() => {
    if (active === 'daily-updates') {
      loadDailyUpdateStatus()
      loadDailyUpdateLogs()
    }
  }, [active])

  useEffect(() => {
    if (active === 'analytics') {
      loadAnalyticsData()
    }
  }, [active])

  // Auto-refresh analytics data every 30 seconds when analytics tab is active
  useEffect(() => {
    if (active !== 'analytics') return
    
    const interval = setInterval(() => {
      console.log('🔄 Auto-refreshing analytics data...')
      loadAnalyticsData()
    }, 30000) // 30 seconds
    
    return () => clearInterval(interval)
  }, [active])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      console.log('📊 Loading analytics data...')
      const apiEndpoints = [
        `${API_BASE}/api/v1/my-symbols/portfolio`,
        `${API_BASE}/api/v1/my-symbols/scores?limit=50`,
        `${API_BASE}/api/v1/my-symbols/replacements`,
        `${API_BASE}/api/v1/my-symbols/analytics`,
        `${API_BASE}/api/v1/my-symbols/correlation`,
        `${API_BASE}/api/v1/my-symbols/alerts`,
        `${API_BASE}/api/v1/my-symbols/weights`
      ]
      try {
        const [portfolioRes, scoresRes, replacementsRes, analyticsRes, correlationRes, alertsRes, weightsRes] = await Promise.allSettled([
          fetch(apiEndpoints[0]).then(res => res.ok ? res.json() : null),
          fetch(apiEndpoints[1]).then(res => res.ok ? res.json() : null),
          fetch(apiEndpoints[2]).then(res => res.ok ? res.json() : null),
          fetch(apiEndpoints[3]).then(res => res.ok ? res.json() : null),
          fetch(apiEndpoints[4]).then(res => res.ok ? res.json() : null),
          fetch(apiEndpoints[5]).then(res => res.ok ? res.json() : null),
          fetch(apiEndpoints[6]).then(res => res.ok ? res.json() : null)
        ])
        
        // Check if we have real API data
        if (portfolioRes.status === 'fulfilled' && portfolioRes.value && portfolioRes.value.length > 0 || scoresRes.status === 'fulfilled' && scoresRes.value && scoresRes.value.length > 0) {
          console.log('✅ Using real API data')
          setAnalyticsData(analyticsRes.status === 'fulfilled' ? analyticsRes.value : createMockAnalytics(portfolioRes.value || []))
          setSymbolScores(scoresRes.status === 'fulfilled' ? scoresRes.value : createMockScores(portfolioRes.value || []))
          setReplacementRecommendations(replacementsRes.status === 'fulfilled' ? replacementsRes.value : createMockRecommendations(portfolioRes.value || []))
          setCorrelationData(correlationRes.status === 'fulfilled' ? correlationRes.value : createMockCorrelation(portfolioRes.value || []))
          setPortfolioAlerts(alertsRes.status === 'fulfilled' ? alertsRes.value : createMockAlerts(portfolioRes.value || []))
          setPositionSizingData(weightsRes.status === 'fulfilled' ? weightsRes.value : createMockPositionSizing(portfolioRes.value || [], accountBalance))
        } else {
          console.log('⚠️ Using mock data (API not available)')
          createMockAnalyticsData()
        }
      } catch (apiError) {
        console.log('⚠️ API not available, using mock data:', apiError.message)
        createMockAnalyticsData()
      }
    } catch (e) {
      console.error('Failed to load analytics data', e)
      createMockAnalyticsData()
    } finally {
      setLoading(false)
    }
  }

  const createMockAnalyticsData = () => {
    console.log('📊 Creating mock analytics data for symbols:', mySymbols)
    
    // Create mock analytics data
    setAnalyticsData(createMockAnalytics(mySymbols))
    
    // Create mock scores based on current symbols and performance data
    const mockScores = createMockScores(mySymbols)
    setSymbolScores(mockScores)
    console.log('📈 Created mock scores:', mockScores.length, 'symbols')
    
    // Create mock recommendations
    setReplacementRecommendations(createMockRecommendations(mySymbols))
    
    // Create mock correlation data
    setCorrelationData(createMockCorrelation(mySymbols))
    
    // Create mock alerts
    setPortfolioAlerts(createMockAlerts(mySymbols))
    
    // Create mock position sizing data
    setPositionSizingData(createMockPositionSizing(mySymbols, accountBalance))
  }

  const createMockAnalytics = (symbols) => ({
    portfolio_size: symbols.length,
    average_score: 0.75,
    total_score: symbols.length * 0.75,
    average_performance: 0.12,
    max_drawdown: 0.08,
    average_volatility: 0.15,
    replacement_candidates: Math.min(2, symbols.length),
    top_performers: symbols.slice(0, 3).map((symbol, index) => ({
      symbol,
      score: 0.85 - (index * 0.05),
      performance: 0.15 - (index * 0.02)
    })),
    lowest_scorers: symbols.slice(-2).map((symbol, index) => ({
      symbol,
      score: 0.65 - (index * 0.05),
      performance: 0.05 - (index * 0.02)
    })),
    last_updated: new Date().toISOString()
  })

  const createMockScores = (symbols) => {
    if (!symbols || symbols.length === 0) return []
    
    return symbols.map((symbol, index) => {
      // Generate dynamic scores based on symbol and performance data
      const performance = performanceData[symbol]
      
      // Base scores with some randomness but realistic ranges
      const baseTechnical = 0.6 + (Math.random() * 0.3) // 0.6-0.9
      const baseFundamental = 0.5 + (Math.random() * 0.4) // 0.5-0.9
      const baseMarketStructure = 0.4 + (Math.random() * 0.5) // 0.4-0.9
      const baseRisk = 0.3 + (Math.random() * 0.6) // 0.3-0.9
      
      // Adjust scores based on performance if available
      let technicalScore = baseTechnical
      let fundamentalScore = baseFundamental
      let marketStructureScore = baseMarketStructure
      let riskScore = baseRisk
      
      if (performance) {
        const returnValue = parseFloat(performance.totalReturn)
        const volatility = parseFloat(performance.volatility)
        const drawdown = parseFloat(performance.maxDrawdown)
        
        // Technical score based on returns
        if (returnValue > 10) technicalScore += 0.1
        else if (returnValue < -10) technicalScore -= 0.1
        
        // Fundamental score based on volatility (lower is better)
        if (volatility < 20) fundamentalScore += 0.1
        else if (volatility > 40) fundamentalScore -= 0.1
        
        // Market structure score based on drawdown
        if (drawdown < 15) marketStructureScore += 0.1
        else if (drawdown > 30) marketStructureScore -= 0.1
        
        // Risk score based on overall performance
        if (returnValue > 0 && volatility < 25) riskScore += 0.1
        else if (returnValue < 0 || volatility > 35) riskScore -= 0.1
      }
      
      // Ensure scores are within bounds
      technicalScore = Math.max(0.1, Math.min(1.0, technicalScore))
      fundamentalScore = Math.max(0.1, Math.min(1.0, fundamentalScore))
      marketStructureScore = Math.max(0.1, Math.min(1.0, marketStructureScore))
      riskScore = Math.max(0.1, Math.min(1.0, riskScore))
      
      // Calculate composite score (weighted average)
      const compositeScore = (
        technicalScore * 0.35 +
        fundamentalScore * 0.25 +
        marketStructureScore * 0.20 +
        riskScore * 0.20
      )
      
      return {
        symbol: symbol,
        technical_score: technicalScore,
        fundamental_score: fundamentalScore,
        market_structure_score: marketStructureScore,
        risk_score: riskScore,
        composite_score: compositeScore,
        confidence_level: 0.7 + (Math.random() * 0.2), // 0.7-0.9
        rank: index + 1,
        calculation_timestamp: new Date().toISOString(),
        supporting_data: {
          price_change: performance ? performance.priceChange : '0.00',
          volatility: performance ? performance.volatility : '0.00',
          volume_trend: Math.random() > 0.5 ? 'increasing' : 'decreasing'
        }
      }
    }).sort((a, b) => b.composite_score - a.composite_score) // Sort by composite score descending
  }

  const createMockRecommendations = (symbols) => symbols.slice(-2).map((symbol, index) => ({
    replace_symbol: symbol,
    replace_score: 0.65 - (index * 0.05),
    candidate_symbol: symbols[index] || 'BTCUSDT',
    candidate_score: 0.75 + (index * 0.05),
    score_improvement: 0.1 + (index * 0.05),
    recommendation_strength: 0.7 + (index * 0.1)
  }))

  const createMockCorrelation = (symbols) => {
    const correlations = {}
    const warnings = []
    
    // Generate mock correlations between symbols
    for (let i = 0; i < symbols.length; i++) {
      for (let j = i + 1; j < symbols.length; j++) {
        const corr = Math.random() * 0.8 - 0.4 // Random correlation between -0.4 and 0.4
        const pair = `${symbols[i]}-${symbols[j]}`
        correlations[pair] = Math.round(corr * 1000) / 1000
        
        // Add some high correlation warnings
        if (Math.abs(corr) > 0.7) {
          warnings.push(`⚠️ High correlation (${corr.toFixed(2)}) between ${symbols[i]} and ${symbols[j]}`)
        }
      }
    }
    
    return {
      correlations,
      warnings,
      average_correlation: 0.15,
      max_correlation: 0.72,
      timestamp: new Date().toISOString()
    }
  }

  const createMockAlerts = (symbols) => {
    const alerts = []
    
    // Add some mock alerts
    if (symbols.length < 10) {
      alerts.push({
        type: 'info',
        symbol: 'portfolio',
        message: `Portfolio has ${symbols.length}/10 positions`,
        action: 'consider_adding_symbols'
      })
    }
    
    // Add some symbol-specific alerts
    symbols.slice(0, 2).forEach((symbol, index) => {
      if (index === 0) {
        alerts.push({
          type: 'warning',
          symbol: symbol,
          message: `${symbol} score below threshold: 0.58`,
          action: 'consider_replacement'
        })
      } else {
        alerts.push({
          type: 'info',
          symbol: 'portfolio',
          message: `High correlation (0.72) between ${symbol} and ${symbols[0]}`,
          action: 'diversify'
        })
      }
    })
    
    return alerts
  }

  const createMockPositionSizing = (symbols, accountBalance) => {
    const positionSizing = {}
    const warnings = []

    // Simulate position sizing based on average score and risk
    symbols.forEach(symbol => {
      const score = symbolScores.find(s => s.symbol === symbol)?.composite_score || 0.5; // Use composite score for risk
      const riskFactor = score > 0.7 ? 0.05 : score > 0.5 ? 0.1 : 0.2; // Higher risk for lower scores
      const maxPosition = accountBalance * riskFactor;
      positionSizing[symbol] = {
        max_position: maxPosition.toFixed(2),
        risk_factor: riskFactor.toFixed(2),
        current_position: '0.00', // Placeholder for current position
        last_updated: new Date().toISOString()
      };

      // Add some warnings
      if (score < 0.5) {
        warnings.push(`⚠️ Low risk tolerance for ${symbol}: ${score.toFixed(2)}`);
      }
    });

    return {
      position_sizing: positionSizing,
      warnings,
      average_risk_factor: symbols.reduce((sum, symbol) => {
        const score = symbolScores.find(s => s.symbol === symbol)?.composite_score || 0.5;
        return sum + (score > 0.7 ? 0.05 : score > 0.5 ? 0.1 : 0.2);
      }, 0) / symbols.length,
      max_risk_factor: Math.max(...Object.values(positionSizing).map(p => parseFloat(p.risk_factor))),
      timestamp: new Date().toISOString()
    };
  };

  const executeReplacement = async (replaceSymbol, candidateSymbol) => {
    try {
      setLoading(true)
      console.log(`🔄 Executing replacement: ${replaceSymbol} → ${candidateSymbol}`)
      try {
        const response = await fetch(`${API_BASE}/api/v1/my-symbols/replacements/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            replace_symbol: replaceSymbol,
            candidate_symbol: candidateSymbol,
            reason: 'User initiated replacement'
          })
        })
        if (response.ok) {
          const result = await response.json()
          console.log('✅ Replacement executed via API:', result)
          await loadAnalyticsData()
          alert(`✅ Successfully replaced ${replaceSymbol} with ${candidateSymbol}`)
        } else {
          throw new Error(`API returned ${response.status}`)
        }
      } catch (apiError) {
        console.log('⚠️ API not available, simulating replacement:', apiError.message)
        const newSymbols = mySymbols.map(s => s === replaceSymbol ? candidateSymbol : s)
        setMySymbols(newSymbols)
        await saveMySymbols(newSymbols)
        await loadAnalyticsData()
        alert(`✅ Simulated replacement: ${replaceSymbol} → ${candidateSymbol}`)
      }
    } catch (e) {
      console.error('Failed to execute replacement:', e)
      alert(`❌ Failed to execute replacement: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const executeRebalancing = async () => {
    try {
      setLoading(true)
      console.log('⚖️ Executing portfolio rebalancing...')
      try {
        const response = await fetch(`${API_BASE}/api/v1/my-symbols/rebalance`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_balance: accountBalance,
            reason: 'User initiated rebalancing'
          })
        })
        if (response.ok) {
          const result = await response.json()
          console.log('✅ Rebalancing executed via API:', result)
          await loadAnalyticsData()
          alert(`✅ Portfolio rebalanced: ${result.total_changes} changes made`)
        } else {
          throw new Error(`API returned ${response.status}`)
        }
      } catch (apiError) {
        console.log('⚠️ API not available, simulating rebalancing:', apiError.message)
        // Simulate rebalancing by updating position sizing data
        const newPositionSizing = createMockPositionSizing(mySymbols, accountBalance)
        setPositionSizingData(newPositionSizing)
        alert('✅ Simulated portfolio rebalancing completed')
      }
    } catch (e) {
      console.error('Failed to execute rebalancing:', e)
      alert(`❌ Failed to execute rebalancing: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const calculatePositionSize = (symbol) => {
    if (!positionSizingData || !positionSizingData.position_sizing[symbol]) {
      return { max: 0, risk: 0 }
    }
    const data = positionSizingData.position_sizing[symbol]
    return {
      max: parseFloat(data.max_position),
      risk: parseFloat(data.risk_factor)
    }
  }

  const loadHistoricalData = async (symbols) => {
    try {
      console.log('📊 Loading historical data for symbols:', symbols)
      const data = {}
      
      // Symbol to filename mapping
      const symbolToFile = {
        'BTCUSDT': 'Bitcoin_7_1_2008-7_1_2025_historical_data_coinmarketcap.csv',
        'ETHUSDT': 'Ethereum_1_1_2010-7_1_2025_historical_data_coinmarketcap.csv',
        'SOLUSDT': 'Solana_5_10_2006-7_1_2025_historical_data_coinmarketcap.csv',
        'AVAXUSDT': 'Avalanche_5_1_2017-7_1_2025_historical_data_coinmarketcap.csv',
        'ADAUSDT': 'Cardano_1_1_2013-7_1_2025_historical_data_coinmarketcap.csv',
        'XRPUSDT': 'XRP_2_1_2006-7_1_2025_historical_data_coinmarketcap.csv',
        'DOTUSDT': 'Polkadot_1_1_2014-7_1_2025_historical_data_coinmarketcap.csv',
        'LINKUSDT': 'Chainlink_5_11_2011-7_1_2025_historical_data_coinmarketcap.csv',
        'BNBUSDT': 'BNB_1_1_2013-7_1_2025_historical_data_coinmarketcap.csv',
        'DOGEUSDT': 'Dogecoin_5_1_2011-7_1_2025_historical_data_coinmarketcap.csv',
        'AAVEUSDT': 'Aave_5_1_2010-7_1_2025_historical_data_coinmarketcap.csv',
        'ATOMUSDT': 'atom-usd-max.csv',
        'HBARUSDT': 'hbar-usd-max.csv',
        'MKRUSDT': 'mkr-usd-max.csv',
        'TRXUSDT': 'trx-usd-max.csv',
        'XTZUSDT': 'xtz-usd-max.csv'
      }
      
      for (const symbol of symbols) {
        const fileName = symbolToFile[symbol]
        
        if (!fileName) {
          console.log(`⚠️ No data file mapping for ${symbol}, using mock data`)
          data[symbol] = createMockHistoricalData(symbol)
          continue
        }
        
        try {
          const response = await fetch(`/Symbol_Price_history_data/${fileName}`)
          if (response.ok) {
            const csvText = await response.text()
            const parsedData = parseCSVData(csvText, symbol)
            data[symbol] = parsedData
            console.log(`✅ Loaded price data for ${symbol}:`, parsedData.length, 'records')
          } else {
            console.log(`⚠️ No price data file found for ${symbol} (${fileName}), using mock data`)
            data[symbol] = createMockHistoricalData(symbol)
          }
        } catch (error) {
          console.log(`⚠️ Error loading price data for ${symbol}:`, error.message)
          data[symbol] = createMockHistoricalData(symbol)
        }
      }
      
      setHistoricalData(data)
      calculatePerformanceMetrics(data)
      
      // Recalculate symbol scores based on new performance data
      const updatedScores = createMockScores(symbols)
      setSymbolScores(updatedScores)
      console.log('📈 Updated symbol scores based on performance data:', updatedScores.length, 'symbols')
      
      return data
    } catch (error) {
      console.error('❌ Failed to load historical data:', error)
      return {}
    }
  }

  const checkHistoricalDataStatus = async () => {
    try {
      setDataLoading(true)
      console.log('🔍 Checking symbol price history data status...')
      
      const response = await fetch(`${API_BASE}/api/v1/symbol-price-history/status`)
      if (response.ok) {
        const status = await response.json()
        setDataStatus(status)
        console.log('📊 Symbol price history data status:', status)
        
        // If there are missing symbols, show notification
        if (status.missing_data && status.missing_data.length > 0) {
          console.log(`⚠️ Missing price data for ${status.missing_data.length} symbols:`, status.missing_data)
          return status.missing_data
        }
      } else {
        console.log('⚠️ Could not check symbol price history data status')
      }
    } catch (error) {
      console.error('❌ Error checking symbol price history data status:', error)
    } finally {
      setDataLoading(false)
    }
    return []
  }

  const syncMissingData = async (missingSymbols = null) => {
    try {
      setDataLoading(true)
      console.log('🔄 Syncing missing symbol price history data...')
      
      const symbolsToSync = missingSymbols || await checkHistoricalDataStatus()
      
      if (symbolsToSync.length === 0) {
        console.log('✅ No missing price data to sync')
        return
      }
      
      const response = await fetch(`${API_BASE}/api/v1/symbol-price-history/download-missing`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbols: symbolsToSync })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Price data sync result:', result)
        
        // Refresh data status
        await checkHistoricalDataStatus()
        
        // Reload historical data for updated symbols
        if (result.success_count > 0) {
          await loadHistoricalData(mySymbols)
        }
      } else {
        console.log('❌ Failed to sync missing price data')
      }
    } catch (error) {
      console.error('❌ Error syncing missing price data:', error)
    } finally {
      setDataLoading(false)
    }
  }

  const generatePriceChart = (symbol, timeframe) => {
    const data = historicalData[symbol]
    if (!data || data.length === 0) return []
    
    const now = new Date()
    let daysBack = 1 // Default 1D
    
    switch (timeframe) {
      case '1D': daysBack = 1; break
      case '7D': daysBack = 7; break
      case '1M': daysBack = 30; break
      default: daysBack = 1
    }
    
    const cutoffDate = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000)
    const filteredData = data.filter(record => record.timestamp >= cutoffDate)
    
    if (filteredData.length === 0) return []
    
    // Get price range for scaling
    const prices = filteredData.map(record => record.close)
    const maxPrice = Math.max(...prices)
    const minPrice = Math.min(...prices)
    const priceRange = maxPrice - minPrice
    
    // Generate chart bars
    return filteredData.map((record, index) => {
      const height = priceRange > 0 ? ((record.close - minPrice) / priceRange) * 100 : 50
      const isUp = record.close >= record.open
      
      return {
        height: `${height}%`,
        backgroundColor: isUp ? '#10b981' : '#ef4444',
        width: `${100 / filteredData.length}%`,
        price: record.close,
        date: record.timestamp,
        index: index
      }
    })
  }

  const getPriceChange = (symbol, timeframe) => {
    const data = historicalData[symbol]
    if (!data || data.length === 0) return { change: 0, percent: 0 }
    
    const now = new Date()
    let daysBack = 1
    
    switch (timeframe) {
      case '1D': daysBack = 1; break
      case '7D': daysBack = 7; break
      case '1M': daysBack = 30; break
      default: daysBack = 1
    }
    
    const cutoffDate = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000)
    const filteredData = data.filter(record => record.timestamp >= cutoffDate)
    
    if (filteredData.length < 2) return { change: 0, percent: 0 }
    
    const startPrice = filteredData[0].close
    const endPrice = filteredData[filteredData.length - 1].close
    const change = endPrice - startPrice
    const percent = startPrice > 0 ? (change / startPrice) * 100 : 0
    
    return { change, percent }
  }

  const parseCSVData = (csvText, symbol) => {
    try {
      const lines = csvText.split('\n').filter(line => line.trim())
      const headers = lines[0].split(';')
      const data = []
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(';')
        if (values.length >= headers.length) {
          const record = {
            timestamp: new Date(values[0].replace(/"/g, '')),
            open: parseFloat(values[5]),
            high: parseFloat(values[6]),
            low: parseFloat(values[7]),
            close: parseFloat(values[8]),
            volume: parseFloat(values[9]),
            marketCap: parseFloat(values[10])
          }
          data.push(record)
        }
      }
      
      return data.sort((a, b) => a.timestamp - b.timestamp)
    } catch (error) {
      console.error('❌ Error parsing CSV data:', error)
      return createMockHistoricalData(symbol)
    }
  }

  const createMockHistoricalData = (symbol) => {
    const data = []
    const now = new Date()
    const basePrice = symbol.includes('BTC') ? 100000 : symbol.includes('ETH') ? 3000 : 100
    
    for (let i = 365; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
      const volatility = 0.02
      const trend = Math.sin(i / 30) * 0.1
      const random = (Math.random() - 0.5) * volatility
      const price = basePrice * (1 + trend + random)
      
      data.push({
        timestamp: date,
        open: price * (1 + (Math.random() - 0.5) * 0.01),
        high: price * (1 + Math.random() * 0.02),
        low: price * (1 - Math.random() * 0.02),
        close: price,
        volume: Math.random() * 1000000000,
        marketCap: price * 1000000000
      })
    }
    
    return data
  }

  const calculatePerformanceMetrics = (data) => {
    const performance = {}
    
    Object.entries(data).forEach(([symbol, historicalData]) => {
      if (historicalData.length === 0) return
      
      const recent = historicalData.slice(-30) // Last 30 days
      const oldest = historicalData[0]
      const newest = historicalData[historicalData.length - 1]
      
      const totalReturn = ((newest.close - oldest.close) / oldest.close) * 100
      const recentReturn = ((newest.close - recent[0].close) / recent[0].close) * 100
      
      // Calculate volatility
      const returns = historicalData.slice(1).map((record, i) => {
        const prev = historicalData[i]
        return ((record.close - prev.close) / prev.close) * 100
      })
      
      const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
      const volatility = Math.sqrt(variance)
      
      // Calculate max drawdown
      let maxDrawdown = 0
      let peak = historicalData[0].close
      
      historicalData.forEach(record => {
        if (record.close > peak) {
          peak = record.close
        }
        const drawdown = ((peak - record.close) / peak) * 100
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown
        }
      })
      
      performance[symbol] = {
        totalReturn: totalReturn.toFixed(2),
        recentReturn: recentReturn.toFixed(2),
        volatility: volatility.toFixed(2),
        maxDrawdown: maxDrawdown.toFixed(2),
        sharpeRatio: avgReturn > 0 ? (avgReturn / volatility).toFixed(2) : '0.00',
        currentPrice: newest.close.toFixed(2),
        priceChange: ((newest.close - newest.open) / newest.open * 100).toFixed(2)
      }
    })
    
    setPerformanceData(performance)
    console.log('📈 Calculated performance metrics:', performance)
  }

  const getFilteredData = (symbol, timeframe) => {
    const data = historicalData[symbol] || []
    if (data.length === 0) return []
    
    const now = new Date()
    let daysBack = 30 // Default 1M
    
    switch (timeframe) {
      case '1W': daysBack = 7; break
      case '1M': daysBack = 30; break
      case '3M': daysBack = 90; break
      case '6M': daysBack = 180; break
      case '1Y': daysBack = 365; break
      default: daysBack = 30
    }
    
    const cutoffDate = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000)
    return data.filter(record => record.timestamp >= cutoffDate)
  }

  const loadAll = async () => {
    try {
      setLoading(true)
      console.log('🔄 Loading all symbol data...')
      
      // Load symbols from different sources
      const [kucoinRes, binanceRes, myRes] = await Promise.allSettled([
        fetchSymbols('/api/futures-symbols/kucoin/available'),
        fetchSymbols('/api/futures-symbols/binance/available'),
        fetch(`${API_BASE}/api/futures-symbols/my-symbols/current`).then(r => r.ok ? r.json() : null)
      ])
      
      // Set KuCoin symbols
      if (kucoinRes.status === 'fulfilled') {
        setKucoinSymbols(kucoinRes.value)
        console.log('✅ Loaded KuCoin symbols:', kucoinRes.value.length)
      } else {
        console.log('⚠️ Failed to load KuCoin symbols')
        setKucoinSymbols([])
      }
      
      // Set Binance symbols
      if (binanceRes.status === 'fulfilled') {
        setBinanceSymbols(binanceRes.value)
        console.log('✅ Loaded Binance symbols:', binanceRes.value.length)
      } else {
        console.log('⚠️ Failed to load Binance symbols')
        setBinanceSymbols([])
      }
      
      // Set My Symbols
      if (myRes.status === 'fulfilled' && myRes.value && myRes.value.portfolio && myRes.value.portfolio.symbols) {
        const mySymbolsList = myRes.value.portfolio.symbols
        setMySymbols(mySymbolsList)
        console.log('✅ Loaded My Symbols:', mySymbolsList.length, mySymbolsList)
        
        // Load historical data for My Symbols
        if (mySymbolsList.length > 0) {
          await loadHistoricalData(mySymbolsList)
          // Fetch market data for My Symbols
          await fetchMarketData(mySymbolsList)
          // Fetch chart data for My Symbols
          await fetchChartData(mySymbolsList)
        }
      } else {
        console.log('⚠️ Failed to load My Symbols, using empty array')
        setMySymbols([])
      }
      
      // Calculate common symbols
      const kucoinSet = new Set(kucoinRes.status === 'fulfilled' ? kucoinRes.value : [])
      const binanceSet = new Set(binanceRes.status === 'fulfilled' ? binanceRes.value : [])
      const common = Array.from(kucoinSet).filter(s => binanceSet.has(s))
      setCommonSymbols(common)
      console.log('✅ Calculated common symbols:', common.length)
      
    } catch (error) {
      console.error('❌ Error loading symbols:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  const upperQuery = symbolQuery.trim().toUpperCase()
  const myUpper = myQuery.trim().toUpperCase()
  const filteredKucoin = useMemo(() => (
    upperQuery ? kucoinSymbols.filter((s) => s.includes(upperQuery)) : kucoinSymbols
  ), [kucoinSymbols, upperQuery])
  const filteredBinance = useMemo(() => (
    upperQuery ? binanceSymbols.filter((s) => s.includes(upperQuery)) : binanceSymbols
  ), [binanceSymbols, upperQuery])
  const filteredCommon = useMemo(() => (
    upperQuery ? commonSymbols.filter((s) => s.includes(upperQuery)) : commonSymbols
  ), [commonSymbols, upperQuery])
  const canAddMyDirect = useMemo(() => (
    !!myUpper && canAddMore && kucoinSymbols.includes(myUpper) && !mySymbols.includes(myUpper)
  ), [myUpper, canAddMore, kucoinSymbols, mySymbols])

  const pickCandidate = (list, query) => {
    const q = (query || '').trim().toUpperCase()
    if (!q) return null
    if (list.includes(q)) return q
    if (list.includes(`${q}USDT`)) return `${q}USDT`
    const found = list.find((s) => s.includes(q))
    return found || null
  }
  const kucoinCandidate = useMemo(() => pickCandidate(kucoinSymbols, upperQuery), [kucoinSymbols, upperQuery])
  const binanceCandidate = useMemo(() => pickCandidate(binanceSymbols, upperQuery), [binanceSymbols, upperQuery])
  const commonCandidate = useMemo(() => pickCandidate(commonSymbols, upperQuery), [commonSymbols, upperQuery])

  const addMySymbol = async (sym) => {
    if (!sym) return
    setMySymbols((prev) => {
      if (prev.includes(sym)) return prev
      if (prev.length >= maxMy) return prev
      const newSymbols = [...prev, sym]
      // Auto-save immediately
      saveMySymbols(newSymbols)
      return newSymbols
    })
  }

  const removeMySymbol = async (sym) => {
    setMySymbols((prev) => {
      const newSymbols = prev.filter((s) => s !== sym)
      // Auto-save immediately
      saveMySymbols(newSymbols)
      return newSymbols
    })
  }

  const addMultipleSymbols = async (symbolsToAdd) => {
    if (!symbolsToAdd || symbolsToAdd.length === 0) return
    setMySymbols((prev) => {
      const newSymbols = [...prev]
      let added = 0
      for (const sym of symbolsToAdd) {
        if (!newSymbols.includes(sym) && newSymbols.length < maxMy) {
          newSymbols.push(sym)
          added++
        }
      }
      if (added > 0) {
        // Auto-save immediately
        saveMySymbols(newSymbols)
      }
      return newSymbols
    })
  }

  const saveMySymbols = async (symbolsToSave = mySymbols) => {
    try {
      setLoading(true)
      console.log('🔄 Saving symbols to backend:', symbolsToSave)
      console.log('🌐 API URL:', `${API_BASE}/api/futures-symbols/my-symbols/update`)
      const res = await fetch(`${API_BASE}/api/futures-symbols/my-symbols/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(symbolsToSave),
      })
      console.log('📡 API Response status:', res.status)
      if (!res.ok) {
        const errorText = await res.text()
        console.error('❌ API Error:', errorText)
        console.error('❌ API URL that failed:', `${API_BASE}/api/futures-symbols/my-symbols/update`)
        throw new Error(errorText)
      }
      const responseData = await res.json()
      console.log('✅ My Symbols saved successfully:', responseData)
      // Reload symbols to ensure frontend state matches backend
      await loadAll()
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Failed to save My Symbols', e)
    } finally {
      setLoading(false)
    }
  }

  const loadDailyUpdateStatus = async () => {
    try {
      setDailyUpdateLoading(true)
      console.log('📊 Loading daily update status...')
      
      const response = await fetch(`${API_BASE}/api/v1/daily-updater/status`)
      if (response.ok) {
        const status = await response.json()
        setDailyUpdateStatus(status)
        console.log('✅ Daily update status loaded:', status)
      } else {
        console.log('⚠️ Could not load daily update status')
      }
    } catch (error) {
      console.error('❌ Error loading daily update status:', error)
    } finally {
      setDailyUpdateLoading(false)
    }
  }

  const loadDailyUpdateLogs = async () => {
    try {
      console.log('📋 Loading daily update logs...')
      
      const response = await fetch(`${API_BASE}/api/v1/daily-updater/logs?limit=5`)
      if (response.ok) {
        const logs = await response.json()
        setDailyUpdateLogs(logs)
        console.log('✅ Daily update logs loaded:', logs.length, 'files')
      } else {
        console.log('⚠️ Could not load daily update logs')
      }
    } catch (error) {
      console.error('❌ Error loading daily update logs:', error)
    }
  }

  const triggerDailyUpdate = async () => {
    try {
      setDailyUpdateLoading(true)
      console.log('🔄 Triggering daily update...')
      
      const response = await fetch(`${API_BASE}/api/v1/daily-updater/force-update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Daily update triggered:', result)
        
        // Refresh status after update
        setTimeout(() => {
          loadDailyUpdateStatus()
          loadDailyUpdateLogs()
        }, 2000)
        
        alert(`Daily update completed! ${result.success_count}/${result.total_count} symbols updated successfully.`)
      } else {
        console.log('❌ Failed to trigger daily update')
        alert('Failed to trigger daily update. Please check the console for details.')
      }
    } catch (error) {
      console.error('❌ Error triggering daily update:', error)
      alert('Error triggering daily update. Please check the console for details.')
    } finally {
      setDailyUpdateLoading(false)
    }
  }

  const fetchMarketData = async (symbols) => {
    if (!symbols || symbols.length === 0) return
    
    try {
      setMarketDataLoading(true)
      console.log('📊 Fetching market data for symbols:', symbols)
      
      const marketDataPromises = symbols.map(async (symbol) => {
        try {
          // Convert symbol format for Binance API (e.g., BTCUSDT -> BTCUSDT)
          const binanceSymbol = symbol
          const response = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${binanceSymbol}`)
          
          if (response.ok) {
            const data = await response.json()
            return {
              symbol,
              price: parseFloat(data.lastPrice),
              priceChange: parseFloat(data.priceChange),
              priceChangePercent: parseFloat(data.priceChangePercent),
              high24h: parseFloat(data.highPrice),
              low24h: parseFloat(data.lowPrice),
              volume: parseFloat(data.volume),
              quoteVolume: parseFloat(data.quoteVolume)
            }
          } else {
            console.warn(`Failed to fetch data for ${symbol}:`, response.status)
            return null
          }
        } catch (error) {
          console.error(`Error fetching market data for ${symbol}:`, error)
          return null
        }
      })

      const results = await Promise.allSettled(marketDataPromises)
      const validData = results
        .filter(result => result.status === 'fulfilled' && result.value)
        .map(result => result.value)
        .reduce((acc, data) => {
          acc[data.symbol] = data
          return acc
        }, {})

      setMarketData(validData)
      console.log('✅ Market data loaded:', Object.keys(validData).length, 'symbols')
    } catch (error) {
      console.error('❌ Failed to fetch market data:', error)
    } finally {
      setMarketDataLoading(false)
    }
  }

  const fetchChartData = async (symbols) => {
    if (!symbols || symbols.length === 0) return
    
    try {
      console.log('📈 Fetching chart data for symbols:', symbols)
      
      const chartDataPromises = symbols.map(async (symbol) => {
        try {
          // Try to get historical data first, then fallback to real-time API
          let chartData = []
          
          // Check if we have historical data for this symbol
          const historicalFileName = getHistoricalFileName(symbol)
          if (historicalFileName) {
            try {
              const historicalResponse = await fetch(`/History Data/${historicalFileName}`)
              if (historicalResponse.ok) {
                const csvText = await historicalResponse.text()
                const historicalData = parseHistoricalCSV(csvText, symbol)
                
                // Get last 24 data points for chart
                chartData = historicalData.slice(-24).map((record, index) => ({
                  timestamp: new Date(record.timestamp).getTime(),
                  date: new Date(record.timestamp),
                  open: record.open,
                  high: record.high,
                  low: record.low,
                  close: record.close,
                  volume: record.volume,
                  hour: index
                }))
                
                console.log(`📊 Using historical data for ${symbol}:`, chartData.length, 'points')
              }
            } catch (historicalError) {
              console.warn(`Historical data not available for ${symbol}, using API:`, historicalError.message)
            }
          }
          
          // If no historical data, use real-time API
          if (chartData.length === 0) {
            const binanceSymbol = symbol
            const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${binanceSymbol}&interval=1h&limit=24`)
            
            if (response.ok) {
              const data = await response.json()
              chartData = data.map((candle, index) => {
                const [timestamp, open, high, low, close, volume] = candle
                const date = new Date(parseInt(timestamp))
                
                return {
                  timestamp: parseInt(timestamp),
                  date,
                  open: parseFloat(open),
                  high: parseFloat(high),
                  low: parseFloat(low),
                  close: parseFloat(close),
                  volume: parseFloat(volume),
                  hour: index
                }
              })
              
              console.log(`📊 Using real-time API data for ${symbol}:`, chartData.length, 'points')
            } else {
              console.warn(`Failed to fetch chart data for ${symbol}:`, response.status)
              return null
            }
          }
          
          return {
            symbol,
            data: chartData
          }
        } catch (error) {
          console.error(`Error fetching chart data for ${symbol}:`, error)
          return null
        }
      })

      const results = await Promise.allSettled(chartDataPromises)
      const validChartData = results
        .filter(result => result.status === 'fulfilled' && result.value)
        .map(result => result.value)
        .reduce((acc, data) => {
          acc[data.symbol] = data.data
          return acc
        }, {})

      setChartData(validChartData)
      console.log('✅ Chart data loaded:', Object.keys(validChartData).length, 'symbols')
    } catch (error) {
      console.error('❌ Failed to fetch chart data:', error)
    }
  }
  
  // Helper function to map symbols to historical data files
  const getHistoricalFileName = (symbol) => {
    const symbolMap = {
      'BTCUSDT': 'Bitcoin_7_1_2008-7_1_2025_historical_data_coinmarketcap.csv',
      'ETHUSDT': 'Ethereum_1_1_2010-7_1_2025_historical_data_coinmarketcap.csv',
      'SOLUSDT': 'Solana_5_10_2006-7_1_2025_historical_data_coinmarketcap.csv',
      'AVAXUSDT': 'Avalanche_5_1_2017-7_1_2025_historical_data_coinmarketcap.csv',
      'ADAUSDT': 'Cardano_1_1_2013-7_1_2025_historical_data_coinmarketcap.csv',
      'XRPUSDT': 'XRP_2_1_2006-7_1_2025_historical_data_coinmarketcap.csv',
      'DOTUSDT': 'Polkadot_1_1_2014-7_1_2025_historical_data_coinmarketcap.csv',
      'LINKUSDT': 'Chainlink_5_11_2011-7_1_2025_historical_data_coinmarketcap.csv',
      'BNBUSDT': 'BNB_1_1_2013-7_1_2025_historical_data_coinmarketcap.csv',
      'DOGEUSDT': 'Dogecoin_5_1_2011-7_1_2025_historical_data_coinmarketcap.csv'
    }
    return symbolMap[symbol]
  }
  
  // Parse historical CSV data
  const parseHistoricalCSV = (csvText, symbol) => {
    try {
      const lines = csvText.split('\n')
      const headers = lines[0].split(';')
      const data = []
      
      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
          const values = lines[i].split(';')
          const record = {}
          
          headers.forEach((header, index) => {
            record[header.trim()] = values[index] ? values[index].replace(/"/g, '') : ''
          })
          
          if (record.timestamp && record.close) {
            data.push({
              timestamp: record.timestamp,
              open: parseFloat(record.open),
              high: parseFloat(record.high),
              low: parseFloat(record.low),
              close: parseFloat(record.close),
              volume: parseFloat(record.volume)
            })
          }
        }
      }
      
      return data
    } catch (error) {
      console.error(`Error parsing historical CSV for ${symbol}:`, error)
      return []
    }
  }

  const tabs = [
    { id: 'my-symbols', label: 'My Symbols' },
    { id: 'kucoin', label: 'KuCoin' },
    { id: 'binance', label: 'Binance' },
    { id: 'both-exchanges', label: 'Both Exchanges' },
    { id: 'analytics', label: '📊 Analytics' },
    { id: 'performance', label: '📈 Performance' },
    { id: 'charts', label: '📊 Charts' },
    { id: 'daily-updates', label: '🔄 Daily Updates' }
  ]

  return (
    <div className="tab-content">
      <div className="section-header">
        <h2>Symbols</h2>
        <p>Manage your tradeable symbols and browse futures lists</p>
      </div>

      <Tabs
        tabs={tabs}
        active={active}
        onChange={setActive}
      />

      {active === 'my-symbols' && (
        <div className="symbols-panel">
          <div className="search-row" style={{ marginBottom: 12 }}>
            <input
              className="search-input"
              placeholder="Type a KuCoin symbol to add (e.g., ETHUSDT)"
              value={myQuery}
              onChange={(e) => setMyQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && canAddMyDirect) {
                  addMySymbol(myUpper)
                  setMyQuery('')
                }
              }}
            />
            <button
              className={`action-btn ${canAddMyDirect ? 'success' : 'secondary'}`}
              disabled={!canAddMyDirect}
              onClick={() => {
                if (!canAddMyDirect) return
                addMySymbol(myUpper)
                setMyQuery('')
              }}
            >
              Add "{myUpper || '...'}"
            </button>
          </div>
          <div className="symbols-actions" style={{ marginBottom: 16 }}>
            <button 
              className="action-btn secondary" 
              disabled={loading || marketDataLoading} 
              onClick={loadAll}
            >
              {marketDataLoading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
          
          <div className="symbols-cards-grid">
            {mySymbols.length === 0 && (
              <div className="no-symbols-message">
                <div className="muted">No symbols yet. Add from KuCoin/Binance tabs.</div>
              </div>
            )}
            {mySymbols.map((s) => (
              <SymbolCard 
                key={s} 
                symbol={s} 
                marketData={marketData} 
                onRemove={removeMySymbol} 
              />
            ))}
          </div>
        </div>
      )}

      {active === 'kucoin' && (
        <div className="symbols-panel">
          <div className="search-row">
            <input
              className="search-input"
              placeholder="Search symbol (e.g., ETHUSDT)"
              value={symbolQuery}
              onChange={(e) => setSymbolQuery(e.target.value)}
            />
            <button
              className={`action-btn ${canAddMore && !loading && kucoinCandidate && !mySymbols.includes(kucoinCandidate) ? 'success' : 'secondary'}`}
              disabled={!canAddMore || loading || !kucoinCandidate || mySymbols.includes(kucoinCandidate)}
              onClick={() => kucoinCandidate && addMySymbol(kucoinCandidate)}
            >
              Add "{kucoinCandidate || upperQuery || '...'}"
            </button>
          </div>
          <Dropdown
            label="Add from KuCoin"
            options={filteredKucoin}
            onAdd={addMySymbol}
            disabled={!canAddMore || loading}
            mySymbols={mySymbols}
            canAddMore={canAddMore}
          />
          <div className="symbols-actions" style={{ marginBottom: 8 }}>
            <button
              className={`action-btn ${canAddMore && filteredKucoin.some((s)=>!mySymbols.includes(s)) ? 'success' : 'secondary'}`}
              disabled={!canAddMore || filteredKucoin.filter((s)=>!mySymbols.includes(s)).length === 0}
              onClick={() => {
                const remaining = maxMy - mySymbols.length
                if (remaining <= 0) return
                const toAdd = filteredKucoin.filter((s) => !mySymbols.includes(s)).slice(0, remaining)
                if (toAdd.length === 0) return
                addMultipleSymbols(toAdd)
              }}
              style={!canAddMore ? { backgroundColor: '#dc3545', color: 'white' } : {}}
            >
              {canAddMore ? `Add up to ${Math.max(0, maxMy - mySymbols.length)}` : 'Limit of 10 Symbols Reached'}
            </button>
          </div>
          <div className="symbols-grid">
            {filteredKucoin.map((s) => (
              <button key={s} className="symbol-card" onClick={() => addMySymbol(s)}>{s}</button>
            ))}
          </div>
          {!canAddMore && <div className="muted">Reached maximum of {maxMy} symbols.</div>}
        </div>
      )}

      {active === 'binance' && (
        <div className="symbols-panel">
          <div className="search-row">
            <input
              className="search-input"
              placeholder="Search symbol (e.g., ETHUSDT)"
              value={symbolQuery}
              onChange={(e) => setSymbolQuery(e.target.value)}
            />
            <button
              className={`action-btn ${canAddMore && !loading && binanceCandidate && !mySymbols.includes(binanceCandidate) ? 'success' : 'secondary'}`}
              disabled={!canAddMore || loading || !binanceCandidate || mySymbols.includes(binanceCandidate)}
              onClick={() => binanceCandidate && addMySymbol(binanceCandidate)}
            >
              Add "{binanceCandidate || upperQuery || '...'}"
            </button>
          </div>
          <Dropdown
            label="Add from Binance (price data only)"
            options={filteredBinance}
            onAdd={addMySymbol}
            disabled={!canAddMore || loading}
            mySymbols={mySymbols}
            canAddMore={canAddMore}
          />
          <div className="symbols-actions" style={{ marginBottom: 8 }}>
            <button
              className={`action-btn ${canAddMore && filteredBinance.some((s)=>!mySymbols.includes(s)) ? 'success' : 'secondary'}`}
              disabled={!canAddMore || filteredBinance.filter((s)=>!mySymbols.includes(s)).length === 0}
              onClick={() => {
                const remaining = maxMy - mySymbols.length
                if (remaining <= 0) return
                const toAdd = filteredBinance.filter((s) => !mySymbols.includes(s)).slice(0, remaining)
                if (toAdd.length === 0) return
                addMultipleSymbols(toAdd)
              }}
              style={!canAddMore ? { backgroundColor: '#dc3545', color: 'white' } : {}}
            >
              {canAddMore ? `Add up to ${Math.max(0, maxMy - mySymbols.length)}` : 'Limit of 10 Symbols Reached'}
            </button>
          </div>
          <div className="symbols-grid">
            {filteredBinance.map((s) => (
              <button key={s} className="symbol-card" onClick={() => addMySymbol(s)}>{s}</button>
            ))}
          </div>
          {!canAddMore && <div className="muted">Reached maximum of {maxMy} symbols.</div>}
        </div>
      )}

      {active === 'both-exchanges' && (
        <div className="symbols-panel">
          <div className="muted" style={{ marginBottom: 8 }}>
            Symbols available on both KuCoin and Binance futures. Add here all the symbols that are traded by both exchanges on the futures market.
          </div>
          <div className="search-row">
            <input
              className="search-input"
              placeholder="Search common symbols (e.g., BTCUSDT)"
              value={symbolQuery}
              onChange={(e) => setSymbolQuery(e.target.value)}
            />
            <button
              className={`action-btn ${canAddMore && !loading && commonCandidate && !mySymbols.includes(commonCandidate) ? 'success' : 'secondary'}`}
              disabled={!canAddMore || loading || !commonCandidate || mySymbols.includes(commonCandidate)}
              onClick={() => commonCandidate && addMySymbol(commonCandidate)}
            >
              Add "{commonCandidate || upperQuery || '...'}"
            </button>
          </div>
          <Dropdown
            label={`Add from Both Exchanges (${filteredCommon.length} symbols)`}
            options={filteredCommon}
            onAdd={addMySymbol}
            disabled={!canAddMore || loading}
            mySymbols={mySymbols}
            canAddMore={canAddMore}
          />
          <div className="symbols-actions" style={{ marginBottom: 8 }}>
            <button
              className={`action-btn ${canAddMore && filteredCommon.some((s)=>!mySymbols.includes(s)) ? 'success' : 'secondary'}`}
              disabled={!canAddMore || filteredCommon.filter((s)=>!mySymbols.includes(s)).length === 0}
              onClick={() => {
                const remaining = maxMy - mySymbols.length
                if (remaining <= 0) return
                const toAdd = filteredCommon.filter((s) => !mySymbols.includes(s)).slice(0, remaining)
                if (toAdd.length === 0) return
                addMultipleSymbols(toAdd)
              }}
              style={!canAddMore ? { backgroundColor: '#dc3545', color: 'white' } : {}}
            >
              {canAddMore ? `Add up to ${Math.max(0, maxMy - mySymbols.length)}` : 'Limit of 10 Symbols Reached'}
            </button>
          </div>
          <div className="symbols-grid">
            {filteredCommon.map((s) => (
              <button key={s} className="symbol-card" onClick={() => addMySymbol(s)}>{s}</button>
            ))}
          </div>
          {!canAddMore && <div className="muted">Reached maximum of {maxMy} symbols.</div>}
        </div>
      )}

      {active === 'analytics' && (
        <div className="symbols-panel">
          <div className="analytics-header">
            <h3>Portfolio Analytics</h3>
            <button className="action-btn secondary" disabled={loading} onClick={loadAnalyticsData}>
              {loading ? 'Loading...' : 'Refresh Analytics'}
            </button>
          </div>
          
          {analyticsData && (
            <div className="analytics-grid">
              {/* Portfolio Overview */}
              <div className="analytics-card">
                <h4>Portfolio Overview</h4>
                <div className="analytics-metrics">
                  <div className="metric">
                    <span className="metric-label">Size:</span>
                    <span className="metric-value">{analyticsData.portfolio_size}/{maxMy}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Avg Score:</span>
                    <span className="metric-value">{(analyticsData.average_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Performance:</span>
                    <span className="metric-value">{(analyticsData.average_performance * 100).toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Max Drawdown:</span>
                    <span className="metric-value">{(analyticsData.max_drawdown * 100).toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Volatility:</span>
                    <span className="metric-value">{(analyticsData.average_volatility * 100).toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Replacement Candidates:</span>
                    <span className="metric-value" style={{color: analyticsData.replacement_candidates > 0 ? '#f59e0b' : '#10b981'}}>
                      {analyticsData.replacement_candidates}
                    </span>
                  </div>
                </div>
                <div className="portfolio-status" style={{marginTop: '12px', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)'}}>
                  <span className="status-label">Portfolio Health:</span>
                  <span className="status-value" style={{
                    color: analyticsData.average_score > 0.7 ? '#10b981' : analyticsData.average_score > 0.5 ? '#f59e0b' : '#ef4444',
                    fontWeight: '600',
                    marginLeft: '8px'
                  }}>
                    {analyticsData.average_score > 0.7 ? 'Excellent' : analyticsData.average_score > 0.5 ? 'Good' : 'Needs Attention'}
                  </span>
                </div>

                {/* Replacement Recommendations - Moved inside Portfolio Overview */}
                <div style={{marginTop: '20px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                  <h5 style={{margin: '0 0 12px 0', fontSize: '1rem', fontWeight: '600', color: 'var(--text)'}}>Replacement Recommendations</h5>
                  <div className="recommendations-list">
                    {replacementRecommendations.map((rec, index) => (
                      <div key={index} className="recommendation-item">
                        <div className="recommendation-header">
                          <span className="replace-symbol">{rec.replace_symbol}</span>
                          <span className="arrow">→</span>
                          <span className="candidate-symbol">{rec.candidate_symbol}</span>
                        </div>
                        <div className="recommendation-details">
                          <span className="score-improvement">+{(rec.score_improvement * 100).toFixed(1)}% improvement</span>
                          <span className="confidence">{(rec.recommendation_strength * 100).toFixed(0)}% confidence</span>
                        </div>
                        <button className="action-btn success" style={{marginTop: '8px'}} onClick={() => executeReplacement(rec.replace_symbol, rec.candidate_symbol)}>
                          Execute Replacement
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Symbol Scores - Made larger */}
              <div className="analytics-card" style={{gridColumn: 'span 2'}}>
                <h4>Symbol Scores</h4>
                <div className="scores-table">
                  <div className="scores-header">
                    <span>Symbol</span>
                    <span>Technical</span>
                    <span>Fundamental</span>
                    <span>Market</span>
                    <span>Risk</span>
                    <span>Composite</span>
                  </div>
                  {symbolScores.map((score) => (
                    <div key={score.symbol} className="score-row">
                      <span className="symbol-name">{score.symbol}</span>
                      <span className="score-value" style={{color: score.technical_score > 0.7 ? '#10b981' : score.technical_score > 0.5 ? '#f59e0b' : '#ef4444'}}>
                        {(score.technical_score * 100).toFixed(0)}%
                      </span>
                      <span className="score-value" style={{color: score.fundamental_score > 0.7 ? '#10b981' : score.fundamental_score > 0.5 ? '#f59e0b' : '#ef4444'}}>
                        {(score.fundamental_score * 100).toFixed(0)}%
                      </span>
                      <span className="score-value" style={{color: score.market_structure_score > 0.7 ? '#10b981' : score.market_structure_score > 0.5 ? '#f59e0b' : '#ef4444'}}>
                        {(score.market_structure_score * 100).toFixed(0)}%
                      </span>
                      <span className="score-value" style={{color: score.risk_score > 0.7 ? '#10b981' : score.risk_score > 0.5 ? '#f59e0b' : '#ef4444'}}>
                        {(score.risk_score * 100).toFixed(0)}%
                      </span>
                      <span className="score-value composite" style={{color: score.composite_score > 0.7 ? '#10b981' : score.composite_score > 0.5 ? '#f59e0b' : '#ef4444'}}>
                        {(score.composite_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Performers */}
              <div className="analytics-card">
                <h4>Top Performers</h4>
                <div className="performers-list">
                  {analyticsData.top_performers.map((performer, index) => (
                    <div key={performer.symbol} className="performer-item">
                      <span className="rank">#{index + 1}</span>
                      <span className="symbol">{performer.symbol}</span>
                      <span className="performance">+{(performer.performance * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Correlation Analysis */}
              {correlationData && (
                <div className="analytics-card" style={{gridColumn: 'span 2'}}>
                  <h4>Correlation Analysis</h4>
                  <div className="correlation-metrics">
                    <div className="metric">
                      <span className="metric-label">Average Correlation:</span>
                      <span className="metric-value" style={{color: Math.abs(correlationData.average_correlation) < 0.3 ? '#10b981' : Math.abs(correlationData.average_correlation) < 0.5 ? '#f59e0b' : '#ef4444'}}>
                        {correlationData.average_correlation.toFixed(3)}
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Max Correlation:</span>
                      <span className="metric-value" style={{color: Math.abs(correlationData.max_correlation) < 0.7 ? '#10b981' : '#ef4444'}}>
                        {correlationData.max_correlation.toFixed(3)}
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Warnings:</span>
                      <span className="metric-value" style={{color: correlationData.warnings.length > 0 ? '#f59e0b' : '#10b981'}}>
                        {correlationData.warnings.length}
                      </span>
                    </div>
                  </div>
                  
                  {correlationData.warnings.length > 0 && (
                    <div className="correlation-warnings">
                      <h5 style={{margin: '16px 0 8px 0', fontSize: '0.9rem', fontWeight: '600', color: '#f59e0b'}}>⚠️ High Correlation Warnings</h5>
                      {correlationData.warnings.map((warning, index) => (
                        <div key={index} className="warning-item">
                          {warning}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="correlation-matrix">
                    <h5 style={{margin: '16px 0 8px 0', fontSize: '0.9rem', fontWeight: '600', color: 'var(--text)'}}>Correlation Matrix</h5>
                    <div className="matrix-container">
                      {Object.entries(correlationData.correlations).slice(0, 10).map(([pair, correlation]) => {
                        const [symbol1, symbol2] = pair.split('-')
                        const absCorr = Math.abs(correlation)
                        const color = absCorr < 0.3 ? '#10b981' : absCorr < 0.7 ? '#f59e0b' : '#ef4444'
                        return (
                          <div key={pair} className="correlation-pair">
                            <span className="pair-symbols">{symbol1} ↔ {symbol2}</span>
                            <span className="correlation-value" style={{color}}>{correlation.toFixed(3)}</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Portfolio Alerts */}
              {portfolioAlerts.length > 0 && (
                <div className="analytics-card">
                  <h4>Portfolio Alerts</h4>
                  <div className="alerts-list">
                    {portfolioAlerts.map((alert, index) => (
                      <div key={index} className={`alert-item ${alert.type}`}>
                        <div className="alert-header">
                          <span className="alert-type">{alert.type.toUpperCase()}</span>
                          <span className="alert-symbol">{alert.symbol}</span>
                        </div>
                        <div className="alert-message">{alert.message}</div>
                        <div className="alert-action">Action: {alert.action}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Position Sizing & Rebalancing */}
              {positionSizingData && (
                <div className="analytics-card" style={{gridColumn: 'span 2'}}>
                  <div className="position-sizing-header">
                    <h4>Position Sizing & Rebalancing</h4>
                    <div className="account-balance-input">
                      <label>Account Balance: $</label>
                      <input
                        type="number"
                        value={accountBalance}
                        onChange={(e) => setAccountBalance(parseFloat(e.target.value) || 10000)}
                        min="1000"
                        step="1000"
                        style={{
                          width: '120px',
                          padding: '4px 8px',
                          marginLeft: '8px',
                          borderRadius: '4px',
                          border: '1px solid var(--border)',
                          background: 'var(--background)',
                          color: 'var(--text)'
                        }}
                      />
                    </div>
                  </div>
                  
                  <div className="position-sizing-metrics">
                    <div className="metric">
                      <span className="metric-label">Average Risk Factor:</span>
                      <span className="metric-value" style={{color: positionSizingData.average_risk_factor < 0.1 ? '#10b981' : positionSizingData.average_risk_factor < 0.15 ? '#f59e0b' : '#ef4444'}}>
                        {(positionSizingData.average_risk_factor * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Max Risk Factor:</span>
                      <span className="metric-value" style={{color: positionSizingData.max_risk_factor < 0.15 ? '#10b981' : '#ef4444'}}>
                        {(positionSizingData.max_risk_factor * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Warnings:</span>
                      <span className="metric-value" style={{color: positionSizingData.warnings.length > 0 ? '#f59e0b' : '#10b981'}}>
                        {positionSizingData.warnings.length}
                      </span>
                    </div>
                  </div>

                  {positionSizingData.warnings.length > 0 && (
                    <div className="position-sizing-warnings">
                      <h5 style={{margin: '16px 0 8px 0', fontSize: '0.9rem', fontWeight: '600', color: '#f59e0b'}}>⚠️ Position Sizing Warnings</h5>
                      {positionSizingData.warnings.map((warning, index) => (
                        <div key={index} className="warning-item">
                          {warning}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="position-sizing-table">
                    <h5 style={{margin: '16px 0 8px 0', fontSize: '0.9rem', fontWeight: '600', color: 'var(--text)'}}>Position Sizing Recommendations</h5>
                    <div className="sizing-table">
                      <div className="sizing-header">
                        <span>Symbol</span>
                        <span>Max Position</span>
                        <span>Risk Factor</span>
                        <span>Current Position</span>
                      </div>
                      {mySymbols.map((symbol) => {
                        const sizing = calculatePositionSize(symbol)
                        return (
                          <div key={symbol} className="sizing-row">
                            <span className="symbol-name">{symbol}</span>
                            <span className="sizing-value">${sizing.max.toLocaleString()}</span>
                            <span className="sizing-value" style={{color: sizing.risk < 0.1 ? '#10b981' : sizing.risk < 0.15 ? '#f59e0b' : '#ef4444'}}>
                              {(sizing.risk * 100).toFixed(1)}%
                            </span>
                            <span className="sizing-value">$0.00</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="rebalancing-actions" style={{marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                    <button 
                      className="action-btn success" 
                      onClick={executeRebalancing}
                      disabled={loading}
                      style={{marginRight: '12px'}}
                    >
                      {loading ? 'Rebalancing...' : '⚖️ Rebalance Portfolio'}
                    </button>
                    <span className="rebalancing-info" style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>
                      Automatically adjust position weights based on current scores
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Performance Tracking Tab */}
      {active === 'performance' && (
        <div className="symbols-panel">
          <div className="performance-header">
            <h3>Performance Tracking</h3>
            <div className="timeframe-selector">
              <label>Timeframe: </label>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                style={{
                  padding: '4px 8px',
                  marginLeft: '8px',
                  borderRadius: '4px',
                  border: '1px solid var(--border)',
                  background: 'var(--background)',
                  color: 'var(--text)'
                }}
              >
                <option value="1W">1 Week</option>
                <option value="1M">1 Month</option>
                <option value="3M">3 Months</option>
                <option value="6M">6 Months</option>
                <option value="1Y">1 Year</option>
              </select>
            </div>
          </div>

          {mySymbols.length === 0 ? (
            <div className="no-data-message">
              <p>No symbols in your portfolio. Add symbols to see performance data.</p>
            </div>
          ) : (
            <div className="performance-grid">
              {/* Portfolio Overview */}
              <div className="performance-card" style={{gridColumn: 'span 2'}}>
                <h4>Portfolio Performance Summary</h4>
                <div className="portfolio-metrics">
                  <div className="metric">
                    <span className="metric-label">Total Return:</span>
                    <span className="metric-value" style={{
                      color: Object.values(performanceData).reduce((sum, p) => sum + parseFloat(p.totalReturn), 0) / Object.keys(performanceData).length > 0 ? '#10b981' : '#ef4444'
                    }}>
                      {Object.values(performanceData).reduce((sum, p) => sum + parseFloat(p.totalReturn), 0) / Object.keys(performanceData).length || 0}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Avg Volatility:</span>
                    <span className="metric-value">
                      {Object.values(performanceData).reduce((sum, p) => sum + parseFloat(p.volatility), 0) / Object.keys(performanceData).length || 0}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Max Drawdown:</span>
                    <span className="metric-value" style={{
                      color: Math.max(...Object.values(performanceData).map(p => parseFloat(p.maxDrawdown))) < 20 ? '#10b981' : '#ef4444'
                    }}>
                      {Math.max(...Object.values(performanceData).map(p => parseFloat(p.maxDrawdown))) || 0}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Sharpe Ratio:</span>
                    <span className="metric-value">
                      {Object.values(performanceData).reduce((sum, p) => sum + parseFloat(p.sharpeRatio), 0) / Object.keys(performanceData).length || 0}
                    </span>
                  </div>
                </div>
              </div>

              {/* Individual Symbol Performance */}
              {mySymbols.map((symbol) => {
                const data = getFilteredData(symbol, selectedTimeframe)
                const performance = performanceData[symbol]
                
                if (!performance) return null
                
                return (
                  <div key={symbol} className="performance-card">
                    <div className="symbol-header">
                      <h4>{symbol}</h4>
                      <span className="current-price">${performance.currentPrice}</span>
                    </div>
                    
                    <div className="symbol-metrics">
                      <div className="metric">
                        <span className="metric-label">Return:</span>
                        <span className="metric-value" style={{
                          color: parseFloat(performance.totalReturn) > 0 ? '#10b981' : '#ef4444'
                        }}>
                          {performance.totalReturn}%
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Volatility:</span>
                        <span className="metric-value">{performance.volatility}%</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Drawdown:</span>
                        <span className="metric-value" style={{
                          color: parseFloat(performance.maxDrawdown) < 20 ? '#10b981' : '#ef4444'
                        }}>
                          {performance.maxDrawdown}%
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Sharpe:</span>
                        <span className="metric-value">{performance.sharpeRatio}</span>
                      </div>
                    </div>

                    {/* Simple Price Chart */}
                    {data.length > 0 && (
                      <div className="price-chart">
                        <div className="chart-container">
                          {data.map((record, index) => {
                            const maxPrice = Math.max(...data.map(r => r.high))
                            const minPrice = Math.min(...data.map(r => r.low))
                            const priceRange = maxPrice - minPrice
                            const height = ((record.close - minPrice) / priceRange) * 100
                            
                            return (
                              <div
                                key={index}
                                className="chart-bar"
                                style={{
                                  height: `${height}%`,
                                  backgroundColor: record.close >= record.open ? '#10b981' : '#ef4444',
                                  width: `${100 / data.length}%`,
                                  minWidth: '2px'
                                }}
                                title={`${record.timestamp.toLocaleDateString()}: $${record.close.toFixed(2)}`}
                              />
                            )
                          })}
                        </div>
                        <div className="chart-labels">
                          <span>{data[0]?.timestamp.toLocaleDateString()}</span>
                          <span>{data[data.length - 1]?.timestamp.toLocaleDateString()}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Charts Tab */}
      {active === 'charts' && (
        <div className="symbols-panel">
          <div className="charts-header">
            <h3>📊 Symbol Charts</h3>
            <p className="charts-subtitle">Real-time 1-day price charts with current market data from Binance</p>
            
            <div className="charts-actions">
              <select 
                className="chart-type-selector"
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'rgba(26, 26, 26, 0.6)',
                  color: '#ffffff',
                  marginRight: '12px'
                }}
              >
                <option value="candlestick">Professional (EMAs + Crosses)</option>
                <option value="line">Simple Line</option>
                <option value="basic">Basic Chart</option>
              </select>
              
              <button 
                className="action-btn secondary" 
                disabled={marketDataLoading} 
                onClick={() => {
                  if (mySymbols.length > 0) {
                    fetchMarketData(mySymbols)
                  }
                }}
              >
                {marketDataLoading ? '🔄 Loading...' : '🔄 Refresh Data'}
              </button>
            </div>
          </div>

          {mySymbols.length === 0 ? (
            <div className="no-data-message">
              <p>No symbols in your portfolio. Add symbols to view charts.</p>
            </div>
          ) : (
            <div className="charts-grid">
              {console.log(`🔍 Rendering ${mySymbols.length} chart cards:`, mySymbols)}
              {mySymbols.map((symbol) => {
                console.log(`🔍 Rendering ChartCard for symbol: ${symbol}`);
                return (
                  <ChartCard
                    key={symbol}
                    symbol={symbol}
                    marketData={marketData}
                    chartType={chartType}
                    autoRefresh={false}
                    onViewDetail={(symbol) => {
                      // Navigate to detailed chart page
                      console.log(`🎯 Opening detailed chart for ${symbol}`);
                      console.log(`📍 Navigating to: /symbol-chart/${symbol}`);
                      try {
                        navigate(`/symbol-chart/${symbol}`);
                        console.log(`✅ Navigation successful for ${symbol}`);
                      } catch (error) {
                        console.error(`❌ Navigation failed for ${symbol}:`, error);
                      }
                    }}
                  />
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Daily Updates Tab */}
      {active === 'daily-updates' && (
        <div className="symbols-panel">
          <div className="daily-updates-header">
            <h3>🔄 Daily Price Updates</h3>
            <p className="daily-updates-subtitle">Automated daily updates of all symbol price history files</p>
            
            <div className="daily-updates-actions">
              <button 
                className={`update-btn ${dailyUpdateLoading ? 'loading' : ''}`}
                onClick={triggerDailyUpdate}
                disabled={dailyUpdateLoading}
              >
                {dailyUpdateLoading ? '🔄 Updating...' : '🔄 Update All Now'}
              </button>
              
              <button 
                className="refresh-btn"
                onClick={() => {
                  loadDailyUpdateStatus()
                  loadDailyUpdateLogs()
                }}
              >
                🔄 Refresh Status
              </button>
            </div>
          </div>

          {dailyUpdateLoading && !dailyUpdateStatus ? (
            <div className="loading-message">
              <div className="spinner"></div>
              <p>Loading daily update status...</p>
            </div>
          ) : (
            <div className="daily-updates-content">
              {/* Status Overview */}
              {dailyUpdateStatus && (
                <div className="status-overview">
                  <div className="status-card">
                    <h4>📊 Update Status</h4>
                    <div className="status-metrics">
                      <div className="metric">
                        <span className="metric-label">Total Symbols:</span>
                        <span className="metric-value">{dailyUpdateStatus.total_symbols}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">With Files:</span>
                        <span className="metric-value success">{dailyUpdateStatus.total_with_files}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Missing Files:</span>
                        <span className="metric-value warning">{dailyUpdateStatus.total_without_files}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Last Update:</span>
                        <span className="metric-value">{dailyUpdateStatus.last_update}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Next Scheduled:</span>
                        <span className="metric-value">{dailyUpdateStatus.next_scheduled}</span>
                      </div>
                    </div>
                  </div>

                  {/* Symbols Status */}
                  <div className="symbols-status">
                    <h4>📋 Symbols Status</h4>
                    
                    {dailyUpdateStatus.symbols_with_files.length > 0 && (
                      <div className="status-section">
                        <h5>✅ Symbols with Files ({dailyUpdateStatus.symbols_with_files.length})</h5>
                        <div className="symbols-list">
                          {dailyUpdateStatus.symbols_with_files.map(symbol => (
                            <span key={symbol} className="symbol-tag success">{symbol}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {dailyUpdateStatus.symbols_without_files.length > 0 && (
                      <div className="status-section">
                        <h5>⚠️ Symbols Missing Files ({dailyUpdateStatus.symbols_without_files.length})</h5>
                        <div className="symbols-list">
                          {dailyUpdateStatus.symbols_without_files.map(symbol => (
                            <span key={symbol} className="symbol-tag warning">{symbol}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Update Logs */}
              <div className="update-logs">
                <h4>📋 Recent Update Logs</h4>
                
                {dailyUpdateLogs.length > 0 ? (
                  <div className="logs-container">
                    {dailyUpdateLogs.map((log, index) => (
                      <div key={index} className="log-entry">
                        <div className="log-header">
                          <span className="log-date">{log.date}</span>
                          <span className="log-size">{log.size} bytes</span>
                        </div>
                        <div className="log-content">
                          <pre>{log.content}</pre>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-logs">
                    <p>No update logs available yet.</p>
                  </div>
                )}
              </div>

              {/* Cron Job Info */}
              <div className="cron-info">
                <h4>⏰ Automated Schedule</h4>
                <div className="cron-details">
                  <p><strong>Schedule:</strong> Daily at 00:05 (12:05 AM)</p>
                  <p><strong>Command:</strong> <code>python3 run_daily_updater.py</code></p>
                  <p><strong>Logs:</strong> <code>/Symbol_Price_history_data/logs/</code></p>
                  <p><strong>Status:</strong> <span className="status-active">Active</span></p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SymbolsManager


