// SimpleChart - A lightweight, working chart component
// Uses basic HTML5 Canvas for reliable rendering
// ---------------------------------------------------------------------------------

import React, { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const SimpleChart = ({ 
  data, 
  symbol, 
  width = '100%', 
  height = '650',
  indicators = {},
  timeframe = '24H'
}) => {
  const [chartData, setChartData] = useState(null)
  const [volumeData, setVolumeData] = useState(null)
  const [activeIndicators, setActiveIndicators] = useState({
    sma: true,
    ema: false,
    rsi: false,
    macd: false,
    bollinger: false
  })
  const [chartType, setChartType] = useState('line')
  const [notifications, setNotifications] = useState([])
  const [lastEmaCross, setLastEmaCross] = useState(null)
  const [showHistory, setShowHistory] = useState(false)
  const [notificationHistory, setNotificationHistory] = useState([])

  // EMA Crossover Detection and Notification System
  const checkEmaCrossovers = (prices) => {
    if (prices.length < 2) return
    
    // Define calculateEMA locally to avoid scope issues
    const calculateEMA = (data, period) => {
      const k = 2 / (period + 1)
      const ema = []
      ema[0] = data[0]
      for (let i = 1; i < data.length; i++) {
        ema[i] = data[i] * k + ema[i - 1] * (1 - k)
      }
      return ema
    }
    
    const ema12 = calculateEMA(prices, 12)
    const ema26 = calculateEMA(prices, 26)
    
    const current = prices.length - 1
    const previous = prices.length - 2
    
    if (ema12[current] && ema26[current] && ema12[previous] && ema26[previous]) {
      const currentDiff = ema12[current] - ema26[current]
      const previousDiff = ema12[previous] - ema26[previous]
      
      // Check for actual crossover
      if ((currentDiff > 0 && previousDiff <= 0) || (currentDiff < 0 && previousDiff >= 0)) {
        const crossType = currentDiff > 0 ? 'Golden Cross' : 'Death Cross'
        const notification = {
          id: Date.now(),
          type: 'crossover',
          symbol: symbol,
          message: `🔄 ${crossType} detected! EMA12 ${currentDiff > 0 ? 'crossed above' : 'crossed below'} EMA26 (${timeframe})`,
          price: prices[current],
          timestamp: new Date().toLocaleTimeString(),
          severity: 'high'
        }
        
        setNotifications(prev => [notification, ...prev.slice(0, 4)]) // Keep last 5 notifications
        setNotificationHistory(prev => [notification, ...prev]) // Store in history
        setLastEmaCross(crossType)
        
        // Show browser notification if supported
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification(`${symbol} ${crossType}`, {
            body: notification.message,
            icon: '/favicon.ico'
          })
        }
      }
      
      // Check for near crossover (within 0.5% of each other)
      const emaDiff = Math.abs(currentDiff)
      const avgPrice = (ema12[current] + ema26[current]) / 2
      const diffPercentage = (emaDiff / avgPrice) * 100
      
      if (diffPercentage <= 0.5 && diffPercentage > 0.1) {
        const notification = {
          id: Date.now(),
          type: 'near-cross',
          symbol: symbol,
          message: `⚠️ Near EMA crossover! EMA12 and EMA26 are ${diffPercentage.toFixed(2)}% apart (${timeframe})`,
          price: prices[current],
          timestamp: new Date().toLocaleTimeString(),
          severity: 'medium'
        }
        
                          // Only add if we don't already have a recent near-cross notification
                  setNotifications(prev => {
                    const hasRecentNearCross = prev.some(n => 
                      n.type === 'near-cross' && 
                      n.symbol === symbol && 
                      Date.now() - n.id < 30000 // 30 seconds
                    )
                    if (!hasRecentNearCross) {
                      setNotificationHistory(prevHistory => [notification, ...prevHistory]) // Store in history
                      return [notification, ...prev.slice(0, 4)]
                    }
                    return prev
                  })
      }
    }
  }

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const requestNotificationPermission = () => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }

  useEffect(() => {
    if (!data || data.length === 0) return

    console.log(`🎯 SimpleChart processing ${data.length} data points for ${symbol}`)
    console.log(`📊 Chart type: ${chartType}`)
    if (chartType === 'candlestick') {
      console.log(`🕯️ Candlestick data sample:`, data.slice(0, 3))
    }
    
    // Check for EMA crossovers
    const pricesForCrossover = data.map(candle => parseFloat(candle.close))
    checkEmaCrossovers(pricesForCrossover)

    // Process data for Chart.js
    const labels = data.map((candle, index) => {
      const timestamp = candle.time ? candle.time * 1000 : candle.timestamp
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
    })

    const prices = data.map(candle => parseFloat(candle.close))
    const volumes = data.map(candle => parseFloat(candle.volume))

    // Calculate technical indicators
    const calculateSMA = (data, period) => {
      const sma = []
      for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
          sma.push(null)
        } else {
          const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
          sma.push(sum / period)
        }
      }
      return sma
    }

    const calculateEMA = (data, period) => {
      const ema = []
      const multiplier = 2 / (period + 1)
      
      for (let i = 0; i < data.length; i++) {
        if (i === 0) {
          ema.push(data[i])
        } else {
          ema.push((data[i] * multiplier) + (ema[i - 1] * (1 - multiplier)))
        }
      }
      return ema
    }

    const calculateRSI = (data, period = 14) => {
      const rsi = []
      const gains = []
      const losses = []
      
      // Calculate gains and losses
      for (let i = 1; i < data.length; i++) {
        const change = data[i] - data[i - 1]
        gains.push(change > 0 ? change : 0)
        losses.push(change < 0 ? Math.abs(change) : 0)
      }
      
      // Calculate RSI
      for (let i = 0; i < data.length; i++) {
        if (i < period) {
          rsi.push(null)
        } else {
          const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b, 0) / period
          const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b, 0) / period
          const rs = avgGain / avgLoss
          const rsiValue = 100 - (100 / (1 + rs))
          rsi.push(rsiValue)
        }
      }
      
      return rsi
    }

    const calculateMACD = (data, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) => {
      const ema12 = calculateEMA(data, fastPeriod)
      const ema26 = calculateEMA(data, slowPeriod)
      const macdLine = ema12.map((fast, i) => fast - ema26[i])
      const signalLine = calculateEMA(macdLine.filter(x => x !== null), signalPeriod)
      
      // Pad signal line with nulls to match length
      const paddedSignalLine = []
      for (let i = 0; i < macdLine.length; i++) {
        if (i < signalLine.length) {
          paddedSignalLine.push(signalLine[i])
        } else {
          paddedSignalLine.push(null)
        }
      }
      
      const histogram = macdLine.map((macd, i) => 
        macd !== null && paddedSignalLine[i] !== null ? macd - paddedSignalLine[i] : null
      )
      
      return { macdLine, signalLine: paddedSignalLine, histogram }
    }

    const calculateBollingerBands = (data, period = 20, stdDev = 2) => {
      const upper = []
      const middle = []
      const lower = []
      
      for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
          upper.push(null)
          middle.push(null)
          lower.push(null)
        } else {
          const slice = data.slice(i - period + 1, i + 1)
          const sma = slice.reduce((a, b) => a + b, 0) / period
          const variance = slice.reduce((sum, val) => sum + Math.pow(val - sma, 2), 0) / period
          const standardDeviation = Math.sqrt(variance)
          
          middle.push(sma)
          upper.push(sma + (standardDeviation * stdDev))
          lower.push(sma - (standardDeviation * stdDev))
        }
      }
      
      return { upper, middle, lower }
    }

    const calculateHeikinAshi = (data) => {
      if (!data || data.length === 0) return []
      
      const heikinAshi = []
      
      for (let i = 0; i < data.length; i++) {
        const candle = data[i]
        
        // Ensure we have valid data
        const open = parseFloat(candle.open) || 0
        const high = parseFloat(candle.high) || 0
        const low = parseFloat(candle.low) || 0
        const close = parseFloat(candle.close) || 0
        
        let haOpen, haHigh, haLow, haClose
        
        if (i === 0) {
          // First candle: use regular OHLC
          haOpen = open
          haHigh = high
          haLow = low
          haClose = close
        } else {
          // Heikin Ashi calculations
          const prevCandle = heikinAshi[i - 1]
          haClose = (open + high + low + close) / 4
          haOpen = (prevCandle.haOpen + prevCandle.haClose) / 2
          haHigh = Math.max(high, haOpen, haClose)
          haLow = Math.min(low, haOpen, haClose)
        }
        
        heikinAshi.push({
          haOpen,
          haHigh,
          haLow,
          haClose,
          isBullish: haClose > haOpen
        })
      }
      
      return heikinAshi
    }

    const sma20 = calculateSMA(prices, 20)
    const ema12 = calculateEMA(prices, 12)
    const ema26 = calculateEMA(prices, 26)
    const rsi = calculateRSI(prices, 14)
    const macd = calculateMACD(prices, 12, 26, 9)
    const bollinger = calculateBollingerBands(prices, 20, 2)
    const heikinAshi = calculateHeikinAshi(data)

    // Create datasets array
    const datasets = []

    // Add main price dataset
    datasets.push({
      label: `${symbol} Price`,
      data: prices,
      borderColor: '#3b82f6', // Blue
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      fill: false,
      tension: 0.1,
      pointRadius: 0,
      pointHoverRadius: 6,
      pointHoverBackgroundColor: '#3b82f6',
      pointHoverBorderColor: '#ffffff',
      pointHoverBorderWidth: 2
    })

    // Add SMA if active
    if (activeIndicators.sma) {
      datasets.push({
        label: 'SMA 20',
        data: sma20,
        borderColor: '#10b981', // Green
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 1.5,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#10b981',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1
      })
    }

    // Add EMA if active
    if (activeIndicators.ema) {
      datasets.push({
        label: 'EMA 12',
        data: ema12,
        borderColor: '#f59e0b', // Orange
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        borderWidth: 1.5,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#f59e0b',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1
      })
      datasets.push({
        label: 'EMA 26',
        data: ema26,
        borderColor: '#ef4444', // Red
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 1.5,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#ef4444',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1
      })
    }

    // Add RSI if active
    if (activeIndicators.rsi) {
      datasets.push({
        label: 'RSI',
        data: rsi,
        borderColor: '#8b5cf6', // Purple
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#8b5cf6',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1,
        yAxisID: 'rsi'
      })
    }

    // Add MACD if active
    if (activeIndicators.macd) {
      datasets.push({
        label: 'MACD Line',
        data: macd.macdLine,
        borderColor: '#06b6d4', // Cyan
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#06b6d4',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1,
        yAxisID: 'macd'
      })
      datasets.push({
        label: 'Signal Line',
        data: macd.signalLine,
        borderColor: '#ec4899', // Pink
        backgroundColor: 'rgba(236, 72, 153, 0.1)',
        borderWidth: 1.5,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#ec4899',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1,
        yAxisID: 'macd'
      })
      datasets.push({
        label: 'MACD Histogram',
        data: macd.histogram,
        backgroundColor: macd.histogram.map(val => val > 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
        borderColor: macd.histogram.map(val => val > 0 ? '#10b981' : '#ef4444'),
        borderWidth: 1,
        type: 'bar',
        yAxisID: 'macd'
      })
    }

    // Add Bollinger Bands if active
    if (activeIndicators.bollinger) {
      datasets.push({
        label: 'Bollinger Upper',
        data: bollinger.upper,
        borderColor: '#10b981', // Green
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 1,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3,
        pointHoverBackgroundColor: '#10b981',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1
      })
      datasets.push({
        label: 'Bollinger Middle',
        data: bollinger.middle,
        borderColor: '#6366f1', // Indigo
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        borderWidth: 1,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3,
        pointHoverBackgroundColor: '#6366f1',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1
      })
      datasets.push({
        label: 'Bollinger Lower',
        data: bollinger.lower,
        borderColor: '#ef4444', // Red
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 1,
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3,
        pointHoverBackgroundColor: '#ef4444',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 1
      })
    }

    // Create price chart data
    const priceChartData = {
      labels,
      datasets
    }

    // Create volume chart data
    const volumeChartData = {
      labels,
      datasets: [
        {
          label: 'Volume',
          data: volumes,
          backgroundColor: 'rgba(6, 182, 212, 0.6)',
          borderColor: '#06b6d4',
          borderWidth: 1,
          borderRadius: 2
        }
      ]
    }

    setChartData(priceChartData)
    setVolumeData(volumeChartData)

  }, [data, symbol, activeIndicators, chartType])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#ffffff',
          font: {
            size: 12,
            family: 'Arial'
          }
        }
      },
      title: {
        display: true,
        text: `${symbol} Professional Trading Chart`,
        color: '#ffffff',
        font: {
          size: 18,
          family: 'Arial',
          weight: 'bold'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: '#8b5cf6',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          title: (context) => {
            return `${symbol} - ${context[0].label}`
          },
          label: (context) => {
            const index = context.dataIndex
            const candle = data[index]
            return [
              `Price: $${parseFloat(candle.close).toFixed(4)}`,
              `Open: $${parseFloat(candle.open).toFixed(4)}`,
              `High: $${parseFloat(candle.high).toFixed(4)}`,
              `Low: $${parseFloat(candle.low).toFixed(4)}`,
              `Volume: ${formatVolume(parseFloat(candle.volume))}`
            ]
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Time',
          color: '#9ca3af',
          font: {
            size: 12,
            family: 'Arial'
          }
        },
        ticks: {
          color: '#9ca3af',
          maxTicksLimit: 8,
          font: {
            size: 10,
            family: 'Arial'
          }
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)',
          drawBorder: false
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Price (USD)',
          color: '#9ca3af',
          font: {
            size: 12,
            family: 'Arial'
          }
        },
        ticks: {
          color: '#9ca3af',
          font: {
            size: 10,
            family: 'Arial'
          },
          callback: (value) => `$${value.toFixed(2)}`
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)',
          drawBorder: false
        }
      },
      rsi: {
        type: 'linear',
        display: activeIndicators.rsi,
        position: 'right',
        title: {
          display: true,
          text: 'RSI',
          color: '#8b5cf6',
          font: {
            size: 10,
            family: 'Arial'
          }
        },
        ticks: {
          color: '#8b5cf6',
          font: {
            size: 8,
            family: 'Arial'
          },
          max: 100,
          min: 0,
          callback: (value) => `${value.toFixed(0)}`
        },
        grid: {
          display: false
        }
      },
      macd: {
        type: 'linear',
        display: activeIndicators.macd,
        position: 'right',
        title: {
          display: true,
          text: 'MACD',
          color: '#06b6d4',
          font: {
            size: 10,
            family: 'Arial'
          }
        },
        ticks: {
          color: '#06b6d4',
          font: {
            size: 8,
            family: 'Arial'
          },
          callback: (value) => `${value.toFixed(4)}`
        },
        grid: {
          display: false
        }
      }
    }
  }

  const volumeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: '#06b6d4',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          title: (context) => {
            return `${symbol} Volume - ${context[0].label}`
          },
          label: (context) => {
            return `Volume: ${formatVolume(context.parsed.y)}`
          }
        }
      }
    },
    scales: {
      x: {
        display: false
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Volume',
          color: '#9ca3af',
          font: {
            size: 10,
            family: 'Arial'
          }
        },
        ticks: {
          color: '#9ca3af',
          font: {
            size: 8,
            family: 'Arial'
          },
          callback: (value) => formatVolume(value)
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.2)',
          drawBorder: false
        }
      }
    }
  }

  const formatVolume = (volume) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`
    return volume.toFixed(0)
  }

  const toggleIndicator = (indicator) => {
    setActiveIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }))
  }

  const changeChartType = (type) => {
    setChartType(type)
  }

  if (!data || data.length === 0) {
    return (
      <div className="chart-loading">
        <div className="loading-spinner"></div>
        <span>Loading chart data...</span>
      </div>
    )
  }

  return (
    <div className="simple-chart-container">


      {/* EMA Crossover Alerts */}
      {notifications.length > 0 && (
        <div className="ema-notifications">
          <div className="notifications-header">
            <h4>🔔 EMA Crossover Alerts</h4>
            <button 
              onClick={() => setNotifications([])}
              className="clear-notifications-btn"
            >
              Clear All
            </button>
          </div>
          <div className="notifications-list">
            {notifications.map(notification => (
              <div 
                key={notification.id} 
                className={`notification-item ${notification.severity} ${notification.type}`}
              >
                <div className="notification-content">
                  <div className="notification-message">{notification.message}</div>
                  <div className="notification-details">
                    <span className="notification-price">${notification.price?.toFixed(4)}</span>
                    <span className="notification-time">{notification.timestamp}</span>
                  </div>
                </div>
                <button 
                  onClick={() => removeNotification(notification.id)}
                  className="notification-close"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notification Permission Request */}
      {('Notification' in window && Notification.permission === 'default') && (
        <div className="notification-permission">
          <div className="permission-content">
            <span>🔔 Enable notifications for EMA crossover alerts</span>
            <button onClick={requestNotificationPermission} className="permission-btn">
              Enable
            </button>
          </div>
        </div>
      )}

      {/* Last EMA Cross Display */}
      {lastEmaCross && (
        <div className="last-ema-cross">
          <span className="cross-indicator">
            {lastEmaCross === 'Golden Cross' ? '🟢' : '🔴'} Last: {lastEmaCross}
          </span>
        </div>
      )}

      {/* Chart Controls */}
      <div className="chart-controls">
        <div className="chart-info">
          <span className="chart-type">
            PROFESSIONAL CHART
          </span>
          <span className="data-points">
            {data ? `${data.length} data points` : 'Loading...'}
          </span>
        </div>
        
        {/* Professional Technical Indicators & Chart Type Row */}
        <div className="controls-row">
          {/* Professional Technical Indicators */}
          <div className="indicators-controls">
            <h4>Professional Technical Indicators</h4>
            <div className="indicators-grid">
              <button 
                className={`indicator-btn ${activeIndicators.sma ? 'active' : ''}`}
                onClick={() => toggleIndicator('sma')}
              >
                SMA
              </button>
              <button 
                className={`indicator-btn ${activeIndicators.ema ? 'active' : ''}`}
                onClick={() => toggleIndicator('ema')}
              >
                EMA
              </button>
              <button 
                className={`indicator-btn ${activeIndicators.rsi ? 'active' : ''}`}
                onClick={() => toggleIndicator('rsi')}
              >
                RSI
              </button>
              <button 
                className={`indicator-btn ${activeIndicators.macd ? 'active' : ''}`}
                onClick={() => toggleIndicator('macd')}
              >
                MACD
              </button>
              <button 
                className={`indicator-btn ${activeIndicators.bollinger ? 'active' : ''}`}
                onClick={() => toggleIndicator('bollinger')}
              >
                Bollinger
              </button>
            </div>
          </div>

          {/* Chart Type Selector */}
          <div className="chart-type-selector">
            <h4>Chart Type</h4>
            <div className="chart-type-buttons">
              <button 
                className={`chart-type-btn ${chartType === 'candlestick' ? 'active' : ''}`}
                onClick={() => changeChartType('candlestick')}
              >
                Candlestick
              </button>
              <button 
                className={`chart-type-btn ${chartType === 'line' ? 'active' : ''}`}
                onClick={() => changeChartType('line')}
              >
                Line
              </button>
              <button 
                className={`chart-type-btn ${chartType === 'area' ? 'active' : ''}`}
                onClick={() => changeChartType('area')}
              >
                Area
              </button>
              <button 
                className={`chart-type-btn ${chartType === 'bar' ? 'active' : ''}`}
                onClick={() => changeChartType('bar')}
              >
                Bar
              </button>
              <button 
                className={`chart-type-btn ${chartType === 'heikin-ashi' ? 'active' : ''}`}
                onClick={() => changeChartType('heikin-ashi')}
              >
                Heikin Ashi
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Price Chart */}
      <div className="chart-wrapper" style={{ height: '88%', marginBottom: '1rem' }}>
        {chartData && (
          <>
            {chartType === 'candlestick' && (
              <div>
                {(() => {
                  try {
                    const candlestickData = {
                      labels: chartData.labels,
                      datasets: [{
                        label: `${symbol} Candlestick`,
                        data: data.map(candle => {
                          const close = parseFloat(candle.close || 0)
                          const open = parseFloat(candle.open || 0)
                          return close
                        }),
                        backgroundColor: data.map(candle => {
                          const close = parseFloat(candle.close || 0)
                          const open = parseFloat(candle.open || 0)
                          return close >= open 
                            ? 'rgba(16, 185, 129, 0.8)' // Green for bullish
                            : 'rgba(239, 68, 68, 0.8)'  // Red for bearish
                        }),
                        borderColor: data.map(candle => {
                          const close = parseFloat(candle.close || 0)
                          const open = parseFloat(candle.open || 0)
                          return close >= open 
                            ? '#10b981' // Green border
                            : '#ef4444'  // Red border
                        }),
                        borderWidth: 1,
                        borderRadius: 2,
                        borderSkipped: false
                      }]
                    }
                    
                    return (
                      <Bar 
                        data={candlestickData}
                        options={{
                          ...chartOptions,
                          plugins: {
                            ...chartOptions.plugins,
                            title: {
                              ...chartOptions.plugins.title,
                              text: `${symbol} Candlestick Chart`
                            },
                            tooltip: {
                              ...chartOptions.plugins.tooltip,
                              callbacks: {
                                title: (context) => {
                                  if (!context || context.length === 0 || !context[0].label) {
                                    return `${symbol} Candlestick`
                                  }
                                  return `${symbol} Candlestick - ${context[0].label}`
                                },
                                label: (context) => {
                                  if (!context || context.length === 0 || context[0].dataIndex === undefined) {
                                    return ['No data available']
                                  }
                                  const index = context[0].dataIndex
                                  if (index < 0 || index >= data.length) {
                                    return ['Data index out of range']
                                  }
                                  const candle = data[index]
                                  if (!candle) {
                                    return ['Candle data not available']
                                  }
                                  return [
                                    `Close: $${parseFloat(candle.close || 0).toFixed(4)}`,
                                    `Open: $${parseFloat(candle.open || 0).toFixed(4)}`,
                                    `High: $${parseFloat(candle.high || 0).toFixed(4)}`,
                                    `Low: $${parseFloat(candle.low || 0).toFixed(4)}`,
                                    `Type: ${parseFloat(candle.close || 0) >= parseFloat(candle.open || 0) ? 'Bullish 🟢' : 'Bearish 🔴'}`
                                  ]
                                }
                              }
                            }
                          },
                          scales: {
                            ...chartOptions.scales,
                            y: {
                              ...chartOptions.scales.y,
                              beginAtZero: false
                            }
                          }
                        }}
                        style={{ background: 'rgba(17, 24, 39, 0.8)' }}
                      />
                    )
                  } catch (error) {
                    console.error('Candlestick chart error:', error)
                    return (
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        height: '400px',
                        color: '#ffffff',
                        fontSize: '16px'
                      }}>
                        <div>
                          <div>🕯️ Candlestick Chart Error</div>
                          <div style={{ fontSize: '14px', color: '#9ca3af', marginTop: '8px' }}>
                            Falling back to Line chart...
                          </div>
                        </div>
                      </div>
                    )
                  }
                })()}
              </div>
            )}
            {chartType === 'line' && (
              <Line 
                data={chartData} 
                options={chartOptions}
                style={{ background: 'rgba(17, 24, 39, 0.8)' }}
              />
            )}
            {chartType === 'area' && (
              <Line 
                data={{
                  ...chartData,
                  datasets: chartData.datasets.map(dataset => {
                    // Only fill the main price dataset, not indicators
                    if (dataset.label.includes('Price') || dataset.label.includes('SMA') || dataset.label.includes('EMA')) {
                      return {
                        ...dataset,
                        fill: true,
                        backgroundColor: dataset.backgroundColor.replace('0.1', '0.4')
                      }
                    }
                    return dataset
                  })
                }}
                options={chartOptions}
                style={{ background: 'rgba(17, 24, 39, 0.8)' }}
              />
            )}
            {chartType === 'bar' && (
              <Bar 
                data={chartData}
                options={{
                  ...chartOptions,
                  scales: {
                    ...chartOptions.scales,
                    y: {
                      ...chartOptions.scales.y,
                      beginAtZero: false
                    }
                  }
                }}
                style={{ background: 'rgba(17, 24, 39, 0.8)' }}
              />
            )}
            {chartType === 'heikin-ashi' && (
              <Line 
                data={{
                  labels: chartData.labels,
                  datasets: [{
                    label: 'Heikin Ashi Close',
                    data: chartData.datasets[0].data, // Use the main price dataset
                    borderColor: '#8b5cf6', // Purple
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    pointHoverBackgroundColor: '#8b5cf6',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 1
                  }]
                }}
                options={{
                  ...chartOptions,
                  plugins: {
                    ...chartOptions.plugins,
                    title: {
                      ...chartOptions.plugins.title,
                      text: `${symbol} Heikin Ashi Chart (Simplified)`
                    },
                    tooltip: {
                      ...chartOptions.plugins.tooltip,
                      callbacks: {
                        title: (context) => {
                          return `${symbol} Heikin Ashi - ${context[0].label}`
                        },
                        label: (context) => {
                          const index = context[0].dataIndex
                          const candle = data[index]
                          return [
                            `Close: $${parseFloat(candle.close).toFixed(4)}`,
                            `Open: $${parseFloat(candle.open).toFixed(4)}`,
                            `High: $${parseFloat(candle.high).toFixed(4)}`,
                            `Low: $${parseFloat(candle.low).toFixed(4)}`,
                            `Type: ${parseFloat(candle.close) > parseFloat(candle.open) ? 'Bullish 🟢' : 'Bearish 🔴'}`
                          ]
                        }
                      }
                    }
                  }
                }}
                style={{ background: 'rgba(17, 24, 39, 0.8)' }}
              />
            )}
          </>
        )}
      </div>

                    {/* Volume Chart */}
              <div className="chart-wrapper" style={{ height: '10%' }}>
        {volumeData && (
          <Bar 
            data={volumeData} 
            options={volumeOptions}
            style={{ background: 'rgba(17, 24, 39, 0.6)' }}
          />
        )}
      </div>

      {/* Chart Status */}
      <div className="chart-status">
        <span className="status-success">✅ Chart.js Professional Chart loaded successfully</span>
        <span className="data-range">
          {data.length > 0 && (
            <>
              Range: ${parseFloat(data[0]?.close || 0).toFixed(4)} - ${parseFloat(data[data.length - 1]?.close || 0).toFixed(4)}
            </>
          )}
        </span>
      </div>

      {/* History Button */}
      <div className="history-section">
        <button 
          className="history-btn"
          onClick={() => setShowHistory(!showHistory)}
        >
          📋 {showHistory ? 'Hide' : 'Show'} Notification History ({notificationHistory.length})
        </button>
      </div>

      {/* Notification History Display */}
      {showHistory && (
        <div className="notification-history-card">
          <div className="history-header">
            <h4>📋 Notification History</h4>
            <button 
              onClick={() => setNotificationHistory([])}
              className="clear-history-btn"
            >
              Clear History
            </button>
          </div>
          <div className="history-content">
            {notificationHistory.length === 0 ? (
              <div className="no-history">
                <span>No notification history yet.</span>
              </div>
            ) : (
              <div className="history-list">
                {notificationHistory.map(notification => (
                  <div 
                    key={notification.id} 
                    className={`history-item ${notification.severity} ${notification.type}`}
                  >
                    <div className="history-content">
                      <div className="history-message">{notification.message}</div>
                      <div className="history-details">
                        <span className="history-price">${notification.price?.toFixed(4)}</span>
                        <span className="history-time">{notification.timestamp}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SimpleChart
