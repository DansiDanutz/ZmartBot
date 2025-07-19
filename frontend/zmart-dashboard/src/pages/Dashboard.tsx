import React from 'react'
import { Helmet } from 'react-helmet-async'
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

const Dashboard: React.FC = () => {
  // Mock data - in real app this would come from API
  const portfolioData = {
    totalValue: 125000,
    change24h: 2500,
    changePercent: 2.04,
    isPositive: true,
  }

  const activeTrades = [
    {
      id: '1',
      symbol: 'BTCUSDT',
      type: 'LONG',
      size: 0.5,
      entryPrice: 50000,
      currentPrice: 51200,
      pnl: 600,
      pnlPercent: 2.4,
    },
    {
      id: '2',
      symbol: 'ETHUSDT',
      type: 'SHORT',
      size: 2.0,
      entryPrice: 3200,
      currentPrice: 3150,
      pnl: 100,
      pnlPercent: 1.56,
    },
  ]

  const recentSignals = [
    {
      id: '1',
      symbol: 'BTCUSDT',
      type: 'STRONG_BUY',
      confidence: 0.85,
      timestamp: '2024-01-15T10:30:00Z',
    },
    {
      id: '2',
      symbol: 'ETHUSDT',
      type: 'BUY',
      confidence: 0.72,
      timestamp: '2024-01-15T09:15:00Z',
    },
  ]

  return (
    <>
      <Helmet>
        <title>Dashboard - Zmart Trading Bot</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400">Welcome to your Zmart Trading Bot dashboard</p>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-800 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Portfolio Value</p>
                <p className="text-2xl font-bold text-white">
                  ${portfolioData.totalValue.toLocaleString()}
                </p>
              </div>
            </div>
            <div className="mt-4 flex items-center">
              {portfolioData.isPositive ? (
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
              )}
              <span
                className={`ml-2 text-sm font-medium ${
                  portfolioData.isPositive ? 'text-green-500' : 'text-red-500'
                }`}
              >
                {portfolioData.isPositive ? '+' : ''}${portfolioData.change24h.toLocaleString()} (
                {portfolioData.changePercent}%)
              </span>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Active Trades</p>
                <p className="text-2xl font-bold text-white">{activeTrades.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-purple-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Total P&L</p>
                <p className="text-2xl font-bold text-white">$700</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-yellow-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-400">Win Rate</p>
                <p className="text-2xl font-bold text-white">68%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Active Trades */}
        <div className="bg-slate-800 rounded-lg">
          <div className="px-6 py-4 border-b border-slate-700">
            <h2 className="text-lg font-semibold text-white">Active Trades</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {activeTrades.map((trade) => (
                <div
                  key={trade.id}
                  className="flex items-center justify-between p-4 bg-slate-700 rounded-lg"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-white font-medium">{trade.symbol}</span>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          trade.type === 'LONG'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {trade.type}
                      </span>
                    </div>
                    <div className="text-slate-400 text-sm">
                      {trade.size} @ ${trade.entryPrice.toLocaleString()}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-medium">
                      ${trade.currentPrice.toLocaleString()}
                    </div>
                    <div
                      className={`text-sm font-medium ${
                        trade.pnl >= 0 ? 'text-green-500' : 'text-red-500'
                      }`}
                    >
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl} ({trade.pnlPercent}%)
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Signals */}
        <div className="bg-slate-800 rounded-lg">
          <div className="px-6 py-4 border-b border-slate-700">
            <h2 className="text-lg font-semibold text-white">Recent Signals</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentSignals.map((signal) => (
                <div
                  key={signal.id}
                  className="flex items-center justify-between p-4 bg-slate-700 rounded-lg"
                >
                  <div className="flex items-center space-x-4">
                    <span className="text-white font-medium">{signal.symbol}</span>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        signal.type === 'STRONG_BUY' || signal.type === 'BUY'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {signal.type}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-medium">
                      {(signal.confidence * 100).toFixed(0)}% confidence
                    </div>
                    <div className="text-slate-400 text-sm">
                      {new Date(signal.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Signal Confidence Heatmap */}
        <div className="bg-slate-800 rounded-lg">
          <div className="px-6 py-4 border-b border-slate-700">
            <h2 className="text-lg font-semibold text-white">Signal Confidence Heatmap</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-6 gap-2">
              {Array.from({ length: 30 }, (_, i) => (
                <div
                  key={i}
                  className="aspect-square rounded bg-gradient-to-br from-green-500 to-red-500 opacity-75"
                  style={{
                    opacity: 0.3 + Math.random() * 0.7,
                  }}
                />
              ))}
            </div>
            <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
              <span>Low Confidence</span>
              <span>High Confidence</span>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Dashboard 