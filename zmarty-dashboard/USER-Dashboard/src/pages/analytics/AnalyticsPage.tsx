import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  DollarSign,
  Target,
  Zap,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'
import { useAppSelector } from '@store/hooks'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import TradingViewChart from '@/components/charts/TradingViewChart'
import { cryptometerService, type CryptometerData } from '@/services/cryptometer'
import { cn, formatCurrency, formatPercentage, getTimeAgo } from '@/lib/utils'

interface PortfolioMetrics {
  totalValue: number
  totalPnL: number
  totalPnLPercent: number
  bestPerformer: string
  worstPerformer: string
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
}

const AnalyticsPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth)
  
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h')
  const [chartData, setChartData] = useState<any[]>([])
  const [cryptometerData, setCryptometerData] = useState<CryptometerData | null>(null)
  const [loading, setLoading] = useState(true)
  const [symbols] = useState(['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'AVAXUSDT'])
  const [timeframes] = useState([
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '1h', value: '1h' },
    { label: '4h', value: '4h' },
    { label: '1d', value: '1d' },
    { label: '1w', value: '1w' }
  ])

  const [portfolioMetrics] = useState<PortfolioMetrics>({
    totalValue: 125430.50,
    totalPnL: 12543.20,
    totalPnLPercent: 11.2,
    bestPerformer: 'SOL/USDT (+24.5%)',
    worstPerformer: 'ADA/USDT (-8.2%)',
    sharpeRatio: 1.85,
    maxDrawdown: -5.8,
    winRate: 74.2
  })

  // Load chart data and analysis
  const loadAnalyticsData = async () => {
    setLoading(true)
    try {
      // Get historical data for the chart
      const historicalData = await cryptometerService.getHistoricalData(selectedSymbol, selectedTimeframe, 100)
      
      // Convert to chart format
      const chartDataFormatted = historicalData.map(data => ({
        time: data.timestamp,
        open: data.ohlcv.open,
        high: data.ohlcv.high,
        low: data.ohlcv.low,
        close: data.ohlcv.close,
        volume: data.ohlcv.volume
      }))
      
      setChartData(chartDataFormatted)
      
      // Get current analysis
      const currentAnalysis = await cryptometerService.getCryptoAnalysis(selectedSymbol, selectedTimeframe)
      setCryptometerData(currentAnalysis)
      
    } catch (error) {
      console.error('Error loading analytics data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnalyticsData()
  }, [selectedSymbol, selectedTimeframe])

  const metrics = [
    {
      name: 'Portfolio Value',
      value: formatCurrency(portfolioMetrics.totalValue),
      change: `${formatPercentage(portfolioMetrics.totalPnLPercent)}`,
      changeType: portfolioMetrics.totalPnL >= 0 ? 'positive' : 'negative' as const,
      icon: DollarSign,
    },
    {
      name: 'Total P&L',
      value: formatCurrency(portfolioMetrics.totalPnL),
      change: portfolioMetrics.bestPerformer,
      changeType: portfolioMetrics.totalPnL >= 0 ? 'positive' : 'negative' as const,
      icon: TrendingUp,
    },
    {
      name: 'Win Rate',
      value: `${portfolioMetrics.winRate}%`,
      change: '+2.1% vs last month',
      changeType: 'positive' as const,
      icon: Target,
    },
    {
      name: 'Sharpe Ratio',
      value: portfolioMetrics.sharpeRatio.toFixed(2),
      change: `Max DD: ${portfolioMetrics.maxDrawdown}%`,
      changeType: portfolioMetrics.sharpeRatio > 1 ? 'positive' : 'negative' as const,
      icon: BarChart3,
    },
  ]

  // Generate technical indicators data for the chart
  const generateIndicatorData = (data: CryptometerData) => {
    if (!data.indicators) return []

    const indicators = []
    
    // SMA indicators
    if (data.indicators.sma) {
      Object.entries(data.indicators.sma).forEach(([period, value]) => {
        indicators.push({
          id: `sma_${period}`,
          name: `SMA (${period})`,
          type: 'line' as const,
          color: period === '20' ? '#2962FF' : '#FF6D00',
          visible: true,
          data: [{ time: data.timestamp, value }]
        })
      })
    }
    
    // EMA indicators
    if (data.indicators.ema) {
      Object.entries(data.indicators.ema).forEach(([period, value]) => {
        indicators.push({
          id: `ema_${period}`,
          name: `EMA (${period})`,
          type: 'line' as const,
          color: period === '12' ? '#E91E63' : '#9C27B0',
          visible: true,
          data: [{ time: data.timestamp, value }]
        })
      })
    }

    // Bollinger Bands
    if (data.indicators.bollinger) {
      indicators.push(
        {
          id: 'bb_upper',
          name: 'Bollinger Upper',
          type: 'line' as const,
          color: '#FF5722',
          visible: true,
          data: [{ time: data.timestamp, value: data.indicators.bollinger.upper }]
        },
        {
          id: 'bb_lower',
          name: 'Bollinger Lower',
          type: 'line' as const,
          color: '#FF5722',
          visible: true,
          data: [{ time: data.timestamp, value: data.indicators.bollinger.lower }]
        }
      )
    }

    return indicators
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-white">Portfolio Analytics</h1>
          <p className="text-secondary-400 mt-1">
            Advanced technical analysis and portfolio insights
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Calendar className="w-4 h-4 mr-2" />
              Last 30 days
            </Button>
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>
          
          <Button variant="outline" size="sm" onClick={loadAnalyticsData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </motion.div>
      
      {/* Metrics Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {metrics.map((metric, index) => {
          const Icon = metric.icon
          const isPositive = metric.changeType === 'positive'
          return (
            <motion.div
              key={metric.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
            >
              <Card className="relative overflow-hidden">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-muted-foreground">
                        {metric.name}
                      </p>
                      <p className="text-2xl font-bold tracking-tight">
                        {metric.value}
                      </p>
                      <div className="flex items-center space-x-2">
                        {isPositive ? (
                          <TrendingUp className="w-4 h-4 text-green-500" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        )}
                        <span className={cn(
                          "text-sm font-medium",
                          isPositive ? "text-green-500" : "text-red-500"
                        )}>
                          {metric.change}
                        </span>
                      </div>
                    </div>
                    <div className={cn(
                      "h-12 w-12 rounded-lg flex items-center justify-center",
                      isPositive ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
                    )}>
                      <Icon className="h-6 w-6" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
        {/* Chart Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="xl:col-span-3 space-y-6"
        >
          {/* Symbol and Timeframe Selector */}
          <Card>
            <CardHeader className="pb-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <CardTitle className="text-lg">Technical Analysis</CardTitle>
                <div className="flex items-center space-x-2">
                  {/* Symbol Selector */}
                  <div className="flex items-center space-x-1 border border-border rounded-lg p-1">
                    {symbols.map(symbol => (
                      <Button
                        key={symbol}
                        variant={selectedSymbol === symbol ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setSelectedSymbol(symbol)}
                        className="h-8 px-3 text-xs"
                      >
                        {symbol}
                      </Button>
                    ))}
                  </div>
                  
                  {/* Timeframe Selector */}
                  <div className="flex items-center space-x-1 border border-border rounded-lg p-1">
                    {timeframes.map(tf => (
                      <Button
                        key={tf.value}
                        variant={selectedTimeframe === tf.value ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setSelectedTimeframe(tf.value)}
                        className="h-8 px-3 text-xs"
                      >
                        {tf.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* TradingView Chart */}
          {chartData.length > 0 && (
            <TradingViewChart
              symbol={selectedSymbol}
              data={chartData}
              indicators={cryptometerData ? generateIndicatorData(cryptometerData) : []}
              height={500}
              showVolume={true}
              showGrid={true}
              onCrosshairMove={(param) => {
                // Handle crosshair movement for real-time data display
                console.log('Crosshair moved:', param)
              }}
            />
          )}
        </motion.div>

        {/* Sidebar Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          {/* Trading Signals */}
          {cryptometerData && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Trading Signals</CardTitle>
                <CardDescription>AI-powered analysis for {selectedSymbol}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Overall Signal</span>
                  <Badge variant={
                    cryptometerData.signals.overall === 'BUY' ? 'success' :
                    cryptometerData.signals.overall === 'SELL' ? 'destructive' : 'secondary'
                  }>
                    {cryptometerData.signals.overall}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Signal Strength</span>
                  <span className="text-sm font-medium">{cryptometerData.signals.strength}%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Trend</span>
                  <Badge variant={
                    cryptometerData.signals.trend === 'BULLISH' ? 'success' :
                    cryptometerData.signals.trend === 'BEARISH' ? 'destructive' : 'secondary'
                  }>
                    {cryptometerData.signals.trend}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Momentum</span>
                  <Badge variant={
                    cryptometerData.signals.momentum === 'POSITIVE' ? 'success' :
                    cryptometerData.signals.momentum === 'NEGATIVE' ? 'destructive' : 'secondary'
                  }>
                    {cryptometerData.signals.momentum}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Volatility</span>
                  <Badge variant={
                    cryptometerData.signals.volatility === 'HIGH' ? 'destructive' :
                    cryptometerData.signals.volatility === 'MEDIUM' ? 'warning' : 'success'
                  }>
                    {cryptometerData.signals.volatility}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Key Indicators */}
          {cryptometerData && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Key Indicators</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">RSI (14)</span>
                  <span className="font-medium">{cryptometerData.indicators.rsi['14']?.toFixed(2)}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">MACD</span>
                  <span className="font-medium">{cryptometerData.indicators.macd.macd.toFixed(4)}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Stochastic %K</span>
                  <span className="font-medium">{cryptometerData.indicators.stochastic.k.toFixed(2)}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Williams %R</span>
                  <span className="font-medium">{cryptometerData.indicators.williams_r.toFixed(2)}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">ADX</span>
                  <span className="font-medium">{cryptometerData.indicators.adx.adx.toFixed(2)}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Risk Metrics */}
          {cryptometerData && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Max Drawdown</span>
                  <span className="font-medium text-red-500">
                    -{cryptometerData.risk_metrics.drawdown.toFixed(2)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Sharpe Ratio</span>
                  <span className="font-medium">{cryptometerData.risk_metrics.sharpe_ratio.toFixed(2)}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Volatility</span>
                  <span className="font-medium">{cryptometerData.risk_metrics.volatility.toFixed(1)}%</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Beta</span>
                  <span className="font-medium">{cryptometerData.risk_metrics.beta.toFixed(2)}</span>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default AnalyticsPage