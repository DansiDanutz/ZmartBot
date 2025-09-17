import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  Zap,
  Target,
  BarChart3,
  RefreshCw,
  Filter,
  Search,
  Settings,
  Play,
  Pause,
  Square,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { useAppSelector } from '@store/hooks'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { cn, formatCurrency, formatPercentage, getTimeAgo } from '@/lib/utils'

interface TradingSignal {
  id: string
  symbol: string
  type: 'BUY' | 'SELL'
  confidence: number
  currentPrice: number
  targetPrice: number
  stopLoss: number
  timeframe: string
  status: 'active' | 'completed' | 'cancelled'
  timestamp: Date
  pnl?: number
  analysis: string
}

interface MarketData {
  symbol: string
  price: number
  change24h: number
  volume24h: number
  marketCap: number
}

const TradingPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth)
  const [activeTab, setActiveTab] = useState<'signals' | 'positions' | 'history'>('signals')
  const [isAutoTrading, setIsAutoTrading] = useState(false)
  const [selectedSignal, setSelectedSignal] = useState<TradingSignal | null>(null)
  
  // Mock data - in real app this would come from API
  const [signals] = useState<TradingSignal[]>([
    {
      id: '1',
      symbol: 'BTC/USDT',
      type: 'BUY',
      confidence: 89,
      currentPrice: 43250.00,
      targetPrice: 45200.00,
      stopLoss: 41800.00,
      timeframe: '4h',
      status: 'active',
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      analysis: 'Strong bullish momentum with RSI oversold condition. Volume increasing on breakout above resistance.'
    },
    {
      id: '2',
      symbol: 'ETH/USDT',
      type: 'SELL',
      confidence: 76,
      currentPrice: 2640.00,
      targetPrice: 2520.00,
      stopLoss: 2720.00,
      timeframe: '1h',
      status: 'active',
      timestamp: new Date(Date.now() - 32 * 60 * 1000),
      analysis: 'Bearish divergence on RSI with declining volume. Price facing resistance at key level.'
    },
    {
      id: '3',
      symbol: 'SOL/USDT',
      type: 'BUY',
      confidence: 95,
      currentPrice: 98.50,
      targetPrice: 105.00,
      stopLoss: 95.00,
      timeframe: '15m',
      status: 'completed',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      pnl: 452.30,
      analysis: 'Perfect bounce from support level with strong volume confirmation. Quick scalp opportunity.'
    }
  ])
  
  const [marketData] = useState<MarketData[]>([
    { symbol: 'BTC/USDT', price: 43250.00, change24h: 2.4, volume24h: 1.2e9, marketCap: 8.5e11 },
    { symbol: 'ETH/USDT', price: 2640.00, change24h: -0.8, volume24h: 8.7e8, marketCap: 3.2e11 },
    { symbol: 'BNB/USDT', price: 310.50, change24h: 1.2, volume24h: 1.5e8, marketCap: 4.8e10 },
    { symbol: 'SOL/USDT', price: 98.50, change24h: 4.1, volume24h: 2.1e8, marketCap: 4.2e10 },
  ])
  
  const stats = [
    {
      name: 'Active Signals',
      value: signals.filter(s => s.status === 'active').length,
      change: '+3',
      changeType: 'positive' as const,
      icon: Zap,
    },
    {
      name: 'Win Rate',
      value: '74.2%',
      change: '+2.1%',
      changeType: 'positive' as const,
      icon: Target,
    },
    {
      name: 'Today\'s P&L',
      value: '$1,247.80',
      change: '+8.3%',
      changeType: 'positive' as const,
      icon: DollarSign,
    },
    {
      name: 'Total Trades',
      value: '156',
      change: '+12',
      changeType: 'positive' as const,
      icon: Activity,
    },
  ]
  
  const formatLargeNumber = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`
    return `$${value.toFixed(2)}`
  }
  
  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'completed': return 'success'
      case 'cancelled': return 'destructive'
      default: return 'secondary'
    }
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
          <h1 className="text-3xl font-bold text-white">Trading Dashboard</h1>
          <p className="text-secondary-400 mt-1">
            AI-powered trading signals and portfolio management
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Button
              onClick={() => setIsAutoTrading(!isAutoTrading)}
              variant={isAutoTrading ? "default" : "secondary"}
              className="flex items-center space-x-2"
            >
              {isAutoTrading ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              <span>{isAutoTrading ? 'Auto Trading ON' : 'Auto Trading OFF'}</span>
            </Button>
          </div>
          
          <Button variant="outline" size="icon">
            <Settings className="w-5 h-5" />
          </Button>
          
          <Button variant="outline" size="icon">
            <RefreshCw className="w-5 h-5" />
          </Button>
        </div>
      </motion.div>
      
      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon
          const isPositive = stat.changeType === 'positive'
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
            >
              <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-muted-foreground">
                        {stat.name}
                      </p>
                      <p className="text-2xl font-bold tracking-tight">
                        {stat.value}
                      </p>
                      <div className="flex items-center space-x-2">
                        {isPositive ? (
                          <ArrowUpRight className="w-4 h-4 text-green-500" />
                        ) : (
                          <ArrowDownRight className="w-4 h-4 text-red-500" />
                        )}
                        <span className={cn(
                          "text-sm font-medium",
                          isPositive ? "text-green-500" : "text-red-500"
                        )}>
                          {stat.change}
                        </span>
                        <span className="text-xs text-muted-foreground">vs yesterday</span>
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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Trading Signals */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <div className="bg-secondary-800 border border-secondary-700 rounded-lg">
            {/* Tabs */}
            <div className="border-b border-secondary-700 p-6">
              <div className="flex items-center justify-between">
                <div className="flex space-x-1">
                  {(['signals', 'positions', 'history'] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        activeTab === tab
                          ? 'bg-primary-600 text-white'
                          : 'text-secondary-400 hover:text-white hover:bg-secondary-700'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>
                
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-700 transition-colors">
                    <Search className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-700 transition-colors">
                    <Filter className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Content */}
            <div className="p-6">
              {activeTab === 'signals' && (
                <div className="space-y-4">
                  {signals.map((signal, index) => (
                    <motion.div
                      key={signal.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setSelectedSignal(signal)}
                      className="bg-secondary-700 rounded-lg p-4 hover:bg-secondary-600 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                            signal.type === 'BUY' ? 'bg-success-400/20 text-success-400' : 'bg-danger-400/20 text-danger-400'
                          }`}>
                            {signal.type}
                          </div>
                          <div>
                            <h3 className="font-medium text-white">{signal.symbol}</h3>
                            <p className="text-sm text-secondary-400">{signal.timeframe} • {signal.confidence}% confidence</p>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <p className="text-white font-medium">{formatCurrency(signal.currentPrice)}</p>
                          <div className={`text-xs px-2 py-1 rounded ${getStatusColor(signal.status)}`}>
                            {signal.status}
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-secondary-400">Target</p>
                          <p className="text-white font-medium">{formatCurrency(signal.targetPrice)}</p>
                        </div>
                        <div>
                          <p className="text-secondary-400">Stop Loss</p>
                          <p className="text-white font-medium">{formatCurrency(signal.stopLoss)}</p>
                        </div>
                        <div>
                          <p className="text-secondary-400">P&L</p>
                          <p className={`font-medium ${signal.pnl ? 'text-success-400' : 'text-secondary-400'}`}>
                            {signal.pnl ? `+${formatCurrency(signal.pnl)}` : '-'}
                          </p>
                        </div>
                      </div>
                      
                      <p className="text-sm text-secondary-400 mt-3 line-clamp-2">
                        {signal.analysis}
                      </p>
                    </motion.div>
                  ))}
                </div>
              )}
              
              {activeTab === 'positions' && (
                <div className="text-center py-12">
                  <BarChart3 className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">No Active Positions</h3>
                  <p className="text-secondary-400">Your active trading positions will appear here</p>
                </div>
              )}
              
              {activeTab === 'history' && (
                <div className="text-center py-12">
                  <Clock className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">Trading History</h3>
                  <p className="text-secondary-400">Your completed trades will appear here</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
        
        {/* Market Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          <div className="bg-secondary-800 border border-secondary-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Market Overview</h3>
            <div className="space-y-4">
              {marketData.map((market, index) => (
                <motion.div
                  key={market.symbol}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-secondary-700 rounded-lg hover:bg-secondary-600 transition-colors cursor-pointer"
                >
                  <div>
                    <p className="font-medium text-white">{market.symbol}</p>
                    <p className="text-sm text-secondary-400">{formatLargeNumber(market.volume24h)} 24h Vol</p>
                  </div>
                  
                  <div className="text-right">
                    <p className="font-medium text-white">{formatCurrency(market.price)}</p>
                    <div className={`text-sm ${market.change24h > 0 ? 'text-success-400' : 'text-danger-400'}`}>
                      {market.change24h > 0 ? '+' : ''}{market.change24h}%
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
          
          {/* Quick Actions */}
          <div className="bg-secondary-800 border border-secondary-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full flex items-center justify-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-medium transition-colors">
                <Zap className="w-4 h-4" />
                <span>Generate New Signals</span>
              </button>
              
              <button className="w-full flex items-center justify-center space-x-2 bg-secondary-700 hover:bg-secondary-600 text-white py-3 rounded-lg font-medium transition-colors">
                <Target className="w-4 h-4" />
                <span>Portfolio Analysis</span>
              </button>
              
              <button className="w-full flex items-center justify-center space-x-2 bg-secondary-700 hover:bg-secondary-600 text-white py-3 rounded-lg font-medium transition-colors">
                <Settings className="w-4 h-4" />
                <span>Trading Settings</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default TradingPage