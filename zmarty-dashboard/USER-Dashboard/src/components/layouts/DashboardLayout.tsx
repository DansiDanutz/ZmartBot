import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Home, 
  MessageSquare, 
  TrendingUp, 
  BarChart3, 
  Settings, 
  User,
  Menu,
  X,
  Bell,
  Search,
  LogOut,
  CreditCard,
  Moon,
  Sun
} from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@store/hooks'
import { logout } from '@store/slices/authSlice'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAppSelector(state => state.auth)
  
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(true)
  
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Zmarty Chat', href: '/chat', icon: MessageSquare },
    { name: 'Trading', href: '/trading', icon: TrendingUp },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
    { name: 'Profile', href: '/profile', icon: User },
  ]
  
  const handleLogout = async () => {
    await dispatch(logout())
    navigate('/login')
  }
  
  return (
    <div className="min-h-screen bg-secondary-900 flex">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>
      
      {/* Sidebar */}
      <AnimatePresence>
        <motion.div
          initial={{ x: -280 }}
          animate={{ x: sidebarOpen ? 0 : -280 }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="fixed inset-y-0 left-0 z-50 w-64 bg-secondary-800 border-r border-secondary-700 lg:translate-x-0 lg:static lg:inset-0"
        >
          <div className="flex h-full flex-col">
            {/* Logo */}
            <div className="flex h-16 items-center justify-between px-6 border-b border-secondary-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-sm font-bold text-white">Z</span>
                </div>
                <span className="text-xl font-bold text-white">Zmarty</span>
              </div>
              
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden text-secondary-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            {/* User Info */}
            <div className="p-4 border-b border-secondary-700">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.fullName?.charAt(0) || user?.username?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    {user?.fullName || user?.username}
                  </p>
                  <p className="text-xs text-secondary-400 truncate">
                    {user?.creditBalance} credits
                  </p>
                </div>
              </div>
            </div>
            
            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                const Icon = item.icon
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`nav-item ${isActive ? 'active' : ''}`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className="nav-icon" />
                    {item.name}
                  </Link>
                )
              })}
            </nav>
            
            {/* Bottom actions */}
            <div className="p-4 border-t border-secondary-700 space-y-2">
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="w-full flex items-center px-4 py-2 text-sm text-secondary-300 hover:text-white hover:bg-secondary-700 rounded-lg transition-colors"
              >
                {isDarkMode ? <Sun className="w-4 h-4 mr-3" /> : <Moon className="w-4 h-4 mr-3" />}
                {isDarkMode ? 'Light Mode' : 'Dark Mode'}
              </button>
              
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-4 py-2 text-sm text-secondary-300 hover:text-white hover:bg-secondary-700 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4 mr-3" />
                Sign Out
              </button>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-16 bg-secondary-800 border-b border-secondary-700 flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-secondary-400 hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
            
            {/* Search */}
            <div className="hidden md:flex items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="bg-secondary-700 border border-secondary-600 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-secondary-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Credits */}
            <div className="hidden sm:flex items-center space-x-2 bg-secondary-700 rounded-lg px-3 py-1">
              <CreditCard className="w-4 h-4 text-primary-400" />
              <span className="text-sm font-medium text-white">{user?.creditBalance || 0}</span>
              <span className="text-xs text-secondary-400">credits</span>
            </div>
            
            {/* Notifications */}
            <button className="relative p-2 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-700 transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
            </button>
            
            {/* User Menu */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.fullName?.charAt(0) || user?.username?.charAt(0) || 'U'}
                </span>
              </div>
              <span className="hidden md:block text-sm font-medium text-white">
                {user?.fullName || user?.username}
              </span>
            </div>
          </div>
        </header>
        
        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout