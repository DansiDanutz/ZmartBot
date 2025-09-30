import React, { useState, useEffect } from 'react'
import { Activity, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    imagesProcessed: 0,
    significanceScore: 0,
    marketSentiment: 'neutral',
    lastUpdate: new Date().toISOString()
  })

  useEffect(() => {
    // Fetch dashboard data
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8100/health')
        const data = await response.json()
        console.log('Dashboard data:', data)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">KingFisher Dashboard</h1>
        <p className="text-gray-400 mt-2">Telegram Image Processing & Analysis</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-blue-400" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Images Processed</p>
              <p className="text-2xl font-bold text-white">{stats.imagesProcessed}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-400" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Significance Score</p>
              <p className="text-2xl font-bold text-white">{(stats.significanceScore * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <TrendingDown className="h-8 w-8 text-red-400" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Market Sentiment</p>
              <p className="text-2xl font-bold text-white capitalize">{stats.marketSentiment}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-yellow-400" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Alerts</p>
              <p className="text-2xl font-bold text-white">0</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="text-white font-medium">Image processed</p>
              <p className="text-gray-400 text-sm">KingFisher analysis #123</p>
            </div>
            <div className="text-right">
              <p className="text-green-400 text-sm">High significance</p>
              <p className="text-gray-400 text-xs">2 minutes ago</p>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="text-white font-medium">Market sentiment changed</p>
              <p className="text-gray-400 text-sm">From neutral to bearish</p>
            </div>
            <div className="text-right">
              <p className="text-red-400 text-sm">Bearish</p>
              <p className="text-gray-400 text-xs">5 minutes ago</p>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="text-white font-medium">Liquidation clusters detected</p>
              <p className="text-gray-400 text-sm">3 clusters with high density</p>
            </div>
            <div className="text-right">
              <p className="text-yellow-400 text-sm">Medium risk</p>
              <p className="text-gray-400 text-xs">10 minutes ago</p>
            </div>
          </div>
        </div>
      </div>

      {/* Connection Status */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Connection Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center p-4 bg-gray-700 rounded-lg">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
            <div>
              <p className="text-white font-medium">Telegram</p>
              <p className="text-gray-400 text-sm">Connected</p>
            </div>
          </div>

          <div className="flex items-center p-4 bg-gray-700 rounded-lg">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
            <div>
              <p className="text-white font-medium">Image Processor</p>
              <p className="text-gray-400 text-sm">Ready</p>
            </div>
          </div>

          <div className="flex items-center p-4 bg-gray-700 rounded-lg">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
            <div>
              <p className="text-white font-medium">Analysis Engine</p>
              <p className="text-gray-400 text-sm">Active</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 