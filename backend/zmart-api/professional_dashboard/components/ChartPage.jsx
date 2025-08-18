import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import ZmartChart from './ZmartChart'

const ChartPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const [availableSymbols, setAvailableSymbols] = useState([])
  const [loading, setLoading] = useState(false)

  // Get initial symbol from URL params if available
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const symbol = params.get('symbol')
    if (symbol) {
      setSelectedSymbol(symbol)
    }
  }, [location])

  // Load available symbols
  useEffect(() => {
    loadAvailableSymbols()
  }, [])

  const loadAvailableSymbols = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/futures-symbols/kucoin/available')
      if (response.ok) {
        const data = await response.json()
        setAvailableSymbols(data.symbols || [])
      }
    } catch (error) {
      console.error('Error loading symbols:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSymbolChange = (symbol) => {
    setSelectedSymbol(symbol)
    // Update URL without page reload
    const newUrl = `/chart?symbol=${symbol}`
    window.history.pushState({}, '', newUrl)
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '30px',
        padding: '20px',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: '20px',
        border: '2px solid rgba(255,255,255,0.2)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button
            onClick={() => navigate('/')}
            style={{
              padding: '12px 20px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
              border: 'none',
              borderRadius: '12px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '600',
              transition: 'all 0.2s ease',
              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 6px 16px rgba(59, 130, 246, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)'
            }}
          >
            ← Back to Dashboard
          </button>
          
          <div>
            <h1 style={{ 
              fontSize: '2.5rem', 
              fontWeight: '700', 
              color: '#ffffff',
              margin: '0'
            }}>
              📈 Professional Chart Analysis
            </h1>
            <p style={{ 
              fontSize: '1.1rem', 
              color: 'rgba(255,255,255,0.7)',
              margin: '10px 0 0 0'
            }}>
              Advanced technical analysis with real-time data
            </p>
          </div>
        </div>

        {/* Symbol Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#ffffff', fontWeight: '600', fontSize: '1.1rem' }}>
            Symbol:
          </span>
          <select
            value={selectedSymbol}
            onChange={(e) => handleSymbolChange(e.target.value)}
            style={{
              padding: '12px 20px',
              background: 'rgba(255,255,255,0.1)',
              border: '2px solid rgba(255,255,255,0.2)',
              borderRadius: '12px',
              color: '#ffffff',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              minWidth: '150px',
              backdropFilter: 'blur(10px)'
            }}
          >
            {loading ? (
              <option>Loading symbols...</option>
            ) : (
              availableSymbols.map(symbol => (
                <option key={symbol} value={symbol}>
                  {symbol}
                </option>
              ))
            )}
          </select>
        </div>
      </div>

      {/* Chart Display */}
      <div style={{
        padding: '30px',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: '20px',
        border: '2px solid rgba(255,255,255,0.2)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
        minHeight: '70vh'
      }}>
        <div style={{ marginBottom: '20px' }}>
          <h2 style={{ 
            fontSize: '2rem', 
            fontWeight: '600', 
            color: '#ffffff',
            margin: '0 0 10px 0'
          }}>
            {selectedSymbol} - Technical Analysis
          </h2>
          <p style={{ 
            fontSize: '1rem', 
            color: 'rgba(255,255,255,0.7)',
            margin: '0'
          }}>
            Real-time price data with EMA indicators and Golden/Death Cross detection
          </p>
        </div>

        <ZmartChart 
          symbol={selectedSymbol}
          unit="$"
          precision={4}
          initialRange="30D"
          height={600}
          showEMAs={true}
          showCrosses={true}
          showGrid={true}
          showTooltip={true}
          chartType="candlestick"
          autoRefresh={true}
          refreshInterval={30000}
        />
      </div>

      {/* Additional Analysis Section */}
      <div style={{
        marginTop: '30px',
        padding: '30px',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: '20px',
        border: '2px solid rgba(255,255,255,0.2)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
      }}>
        <h3 style={{ 
          fontSize: '1.5rem', 
          fontWeight: '600', 
          color: '#ffffff',
          margin: '0 0 20px 0'
        }}>
          📊 Chart Features
        </h3>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          <div style={{
            padding: '20px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h4 style={{ color: '#3b82f6', margin: '0 0 10px 0' }}>📈 Technical Indicators</h4>
            <ul style={{ color: 'rgba(255,255,255,0.8)', margin: '0', paddingLeft: '20px' }}>
              <li>EMA 9 (Fast trend)</li>
              <li>EMA 21 (Medium trend)</li>
              <li>EMA 50 (Long trend)</li>
              <li>EMA 200 (Major trend)</li>
            </ul>
          </div>
          
          <div style={{
            padding: '20px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h4 style={{ color: '#10b981', margin: '0 0 10px 0' }}>🔄 Cross Signals</h4>
            <ul style={{ color: 'rgba(255,255,255,0.8)', margin: '0', paddingLeft: '20px' }}>
              <li>Golden Cross (Bullish)</li>
              <li>Death Cross (Bearish)</li>
              <li>Real-time detection</li>
              <li>Visual markers</li>
            </ul>
          </div>
          
          <div style={{
            padding: '20px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h4 style={{ color: '#f59e0b', margin: '0 0 10px 0' }}>⚡ Real-time Data</h4>
            <ul style={{ color: 'rgba(255,255,255,0.8)', margin: '0', paddingLeft: '20px' }}>
              <li>Live Binance data</li>
              <li>Auto-refresh every 30s</li>
              <li>Multiple timeframes</li>
              <li>Professional accuracy</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChartPage
