import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPageSimple from './pages/auth/LoginPageSimple'
import ChatPageSimple from './pages/chat/ChatPageSimple'
// Removed dependency on DashboardLayout - using standalone design
// Removed dependency on DashboardCards - using inline professional design
import './index.css'

const DashboardPage: React.FC = () => (
  <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
    {/* Header */}
    <div className="mb-8">
      <h1 className="text-4xl font-bold text-white mb-2">⚡ ZmartBot Professional Dashboard</h1>
      <p className="text-slate-300">Advanced Trading Intelligence Platform</p>
    </div>

    {/* Stats Cards Row */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Portfolio Card */}
      <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 p-6 rounded-2xl shadow-xl text-white">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-emerald-100 text-sm font-medium mb-1">Portfolio Value</p>
            <p className="text-3xl font-bold mb-1">$12,847.32</p>
            <p className="text-emerald-100 text-sm">+3.2% today</p>
          </div>
          <div className="bg-white/20 p-3 rounded-xl">
            <span className="text-2xl">💰</span>
          </div>
        </div>
      </div>

      {/* Active Trades */}
      <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-2xl shadow-xl text-white">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-blue-100 text-sm font-medium mb-1">Active Trades</p>
            <p className="text-3xl font-bold mb-1">7</p>
            <p className="text-blue-100 text-sm">5 profitable</p>
          </div>
          <div className="bg-white/20 p-3 rounded-xl">
            <span className="text-2xl">📈</span>
          </div>
        </div>
      </div>

      {/* Win Rate */}
      <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-2xl shadow-xl text-white">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-purple-100 text-sm font-medium mb-1">Win Rate</p>
            <p className="text-3xl font-bold mb-1">78.4%</p>
            <p className="text-purple-100 text-sm">Last 30 days</p>
          </div>
          <div className="bg-white/20 p-3 rounded-xl">
            <span className="text-2xl">🎯</span>
          </div>
        </div>
      </div>

      {/* AI Insights */}
      <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-2xl shadow-xl text-white">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-orange-100 text-sm font-medium mb-1">AI Insights</p>
            <p className="text-3xl font-bold mb-1">23</p>
            <p className="text-orange-100 text-sm">This week</p>
          </div>
          <div className="bg-white/20 p-3 rounded-xl">
            <span className="text-2xl">🤖</span>
          </div>
        </div>
      </div>
    </div>

    {/* Main Content */}
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* System Status */}
      <div className="lg:col-span-2 bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">🚀 System Status</h2>
          <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
            All Systems Operational
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800/50 p-4 rounded-xl border border-green-500/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-400 font-medium">KuCoin API</p>
                <p className="text-white text-lg">Connected</p>
              </div>
              <span className="text-green-500 text-2xl">✅</span>
            </div>
          </div>
          
          <div className="bg-slate-800/50 p-4 rounded-xl border border-green-500/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-400 font-medium">Binance API</p>
                <p className="text-white text-lg">Connected</p>
              </div>
              <span className="text-green-500 text-2xl">✅</span>
            </div>
          </div>
          
          <div className="bg-slate-800/50 p-4 rounded-xl border border-blue-500/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-400 font-medium">Trading AI</p>
                <p className="text-white text-lg">Active</p>
              </div>
              <span className="text-blue-500 text-2xl">⚡</span>
            </div>
          </div>
          
          <div className="bg-slate-800/50 p-4 rounded-xl border border-purple-500/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-400 font-medium">Zmarty AI</p>
                <p className="text-white text-lg">Ready</p>
              </div>
              <span className="text-purple-500 text-2xl">🤖</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
        <h3 className="text-xl font-bold text-white mb-6">⚡ Quick Actions</h3>
        <div className="space-y-4">
          <button 
            onClick={() => window.location.href = '/chat'}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-4 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <span className="text-lg mr-3">💬</span>
            Open Zmarty Chat
          </button>
          
          <button 
            onClick={() => window.location.href = '/analytics'}
            className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white py-4 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <span className="text-lg mr-3">📊</span>
            View Analytics
          </button>
          
          <button 
            onClick={() => window.location.href = '/trading'}
            className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white py-4 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <span className="text-lg mr-3">🔧</span>
            Trading Settings
          </button>
        </div>

        {/* Recent Activity */}
        <div className="mt-8">
          <h4 className="text-lg font-semibold text-white mb-4">📈 Recent Activity</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-white text-sm font-medium">BTC/USDT Buy Signal</p>
                  <p className="text-slate-400 text-xs">2 minutes ago</p>
                </div>
              </div>
              <span className="text-green-500 font-bold">+$127.50</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-white text-sm font-medium">ETH Analysis Complete</p>
                  <p className="text-slate-400 text-xs">15 minutes ago</p>
                </div>
              </div>
              <span className="text-blue-500">📊</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-white text-sm font-medium">AI Model Updated</p>
                  <p className="text-slate-400 text-xs">1 hour ago</p>
                </div>
              </div>
              <span className="text-purple-500">🤖</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* Welcome Banner */}
    <div className="mt-8 bg-gradient-to-r from-slate-800/50 to-blue-800/50 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <div className="flex items-center">
        <div className="text-5xl mr-6">🎯</div>
        <div>
          <h3 className="text-2xl font-bold text-white mb-2">Welcome to ZmartBot Professional!</h3>
          <p className="text-slate-300 text-lg">
            Your advanced trading platform is fully operational. Navigate to{' '}
            <span className="text-blue-400 font-semibold cursor-pointer hover:text-blue-300" onClick={() => window.location.href = '/chat'}>
              Zmarty Chat
            </span>{' '}
            to interact with your AI trading assistant and access real-time market intelligence.
          </p>
        </div>
      </div>
    </div>
  </div>
)

const TradingPage: React.FC = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold text-white mb-6">📈 Trading Hub</h1>
    <div className="bg-slate-800 p-6 rounded-lg">
      <p className="text-white">Trading interface coming soon...</p>
    </div>
  </div>
)

const AnalyticsPage: React.FC = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold text-white mb-6">📊 Analytics</h1>
    <div className="bg-slate-800 p-6 rounded-lg">
      <p className="text-white">Analytics dashboard coming soon...</p>
    </div>
  </div>
)

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // For demo, always authenticated
  const isAuthenticated = true
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900">
      <Routes>
        <Route path="/login" element={<LoginPageSimple />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPageSimple />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trading"
          element={
            <ProtectedRoute>
              <TradingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  )
}

export default App