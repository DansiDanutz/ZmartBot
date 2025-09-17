import React, { useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  BarChart3,
  MessageSquare,
  Zap,
  Target
} from 'lucide-react'
import { useAppSelector } from '@store/hooks'

const DashboardPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth)
  
  // Mock data - in real app this would come from API
  const stats = [
    {
      name: 'Total Credits',
      value: user?.creditBalance || 0,
      change: '+12.5%',
      changeType: 'positive',
      icon: DollarSign,
    },
    {
      name: 'Active Trades',
      value: 8,
      change: '+4.3%',
      changeType: 'positive',
      icon: Activity,
    },
    {
      name: 'Win Rate',
      value: '74.2%',
      change: '+2.1%',
      changeType: 'positive',
      icon: Target,
    },
    {
      name: 'Total P&L',
      value: '$12,456',
      change: '-0.8%',
      changeType: 'negative',
      icon: BarChart3,
    },
  ]
  
  const recentActivities = [
    {
      id: 1,
      type: 'trade',
      message: 'Opened BTC/USDT position',
      time: '2 minutes ago',
      status: 'success'
    },
    {
      id: 2,
      type: 'chat',
      message: 'Asked Zmarty about market analysis',
      time: '15 minutes ago',
      status: 'info'
    },
    {
      id: 3,
      type: 'alert',
      message: 'Price alert triggered for ETH',
      time: '1 hour ago',
      status: 'warning'
    },
    {
      id: 4,
      type: 'trade',
      message: 'Closed AAPL position with +5.2% profit',
      time: '3 hours ago',
      status: 'success'
    },
  ]
  
  const quickActions = [
    {
      name: 'Chat with Zmarty',
      description: 'Get AI-powered trading insights',
      icon: MessageSquare,
      href: '/chat',
      color: 'bg-primary-600'
    },
    {
      name: 'View Trading Signals',
      description: 'Latest market opportunities',
      icon: Zap,
      href: '/trading',
      color: 'bg-success-600'
    },
    {
      name: 'Portfolio Analytics',
      description: 'Deep dive into your performance',
      icon: BarChart3,
      href: '/analytics',
      color: 'bg-warning-600'
    },
  ]
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-white">
            Welcome back, {user?.fullName || user?.username}!
          </h1>
          <p className="text-secondary-400 mt-1">
            Here's what's happening with your trading portfolio today.
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
            <span className="text-sm text-secondary-400">Markets Open</span>
          </div>
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
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              className="bg-secondary-800 border border-secondary-700 rounded-lg p-6 hover:bg-secondary-750 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-secondary-400 text-sm font-medium">
                    {stat.name}
                  </p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {stat.value}
                  </p>
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  stat.changeType === 'positive' ? 'bg-success-600' : 'bg-primary-600'
                }`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
              
              <div className="flex items-center mt-4">
                {stat.changeType === 'positive' ? (
                  <TrendingUp className="w-4 h-4 text-success-400 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-danger-400 mr-1" />
                )}
                <span className={`text-sm font-medium ${
                  stat.changeType === 'positive' ? 'text-success-400' : 'text-danger-400'
                }`}>
                  {stat.change}
                </span>
                <span className="text-secondary-400 text-sm ml-2">vs last week</span>
              </div>
            </motion.div>
          )
        })}
      </motion.div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, index) => {
              const Icon = action.icon
              return (
                <motion.a
                  key={action.name}
                  href={action.href}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                  className="block bg-secondary-800 border border-secondary-700 rounded-lg p-6 hover:bg-secondary-750 hover:border-secondary-600 transition-all group"
                >
                  <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {action.name}
                  </h3>
                  <p className="text-secondary-400 text-sm">
                    {action.description}
                  </p>
                </motion.a>
              )
            })}
          </div>
        </motion.div>
        
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-start space-x-3"
              >
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                  activity.status === 'success' ? 'bg-success-500' :
                  activity.status === 'warning' ? 'bg-warning-500' :
                  'bg-primary-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium">
                    {activity.message}
                  </p>
                  <p className="text-xs text-secondary-400 mt-1">
                    {activity.time}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
          
          <button className="w-full mt-4 text-sm text-primary-400 hover:text-primary-300 font-medium transition-colors">
            View All Activity
          </button>
        </motion.div>
      </div>
      
      {/* Market Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
      >
        <h2 className="text-xl font-semibold text-white mb-6">Market Overview</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* This would typically contain real market data */}
          <div className="text-center">
            <p className="text-secondary-400 text-sm">BTC/USDT</p>
            <p className="text-2xl font-bold text-white">$43,250.00</p>
            <p className="text-success-400 text-sm flex items-center justify-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              +2.4%
            </p>
          </div>
          
          <div className="text-center">
            <p className="text-secondary-400 text-sm">ETH/USDT</p>
            <p className="text-2xl font-bold text-white">$2,640.00</p>
            <p className="text-success-400 text-sm flex items-center justify-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              +1.8%
            </p>
          </div>
          
          <div className="text-center">
            <p className="text-secondary-400 text-sm">SOL/USDT</p>
            <p className="text-2xl font-bold text-white">$98.50</p>
            <p className="text-danger-400 text-sm flex items-center justify-center">
              <TrendingDown className="w-4 h-4 mr-1" />
              -0.5%
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default DashboardPage