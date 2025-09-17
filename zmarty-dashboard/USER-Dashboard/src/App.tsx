import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { motion, AnimatePresence } from 'framer-motion'

// Store and auth
import { RootState, AppDispatch } from '@store/index'
import { checkAuthStatus, clearError } from '@store/slices/authSlice'

// Layout components
import AuthLayout from '@components/layouts/AuthLayout'
import DashboardLayout from '@components/layouts/DashboardLayout'

// Pages
import LoginPage from '@pages/auth/LoginPage'
import RegisterPage from '@pages/auth/RegisterPage'
import ForgotPasswordPage from '@pages/auth/ForgotPasswordPage'
import DashboardPage from '@pages/dashboard/DashboardPage'
import ChatPage from '@pages/chat/ChatPage'
import TradingPage from '@pages/trading/TradingPage'
import AnalyticsPage from '@pages/analytics/AnalyticsPage'
import SettingsPage from '@pages/settings/SettingsPage'
import ProfilePage from '@pages/profile/ProfilePage'

// Components
import LoadingSpinner from '@components/ui/LoadingSpinner'
import ErrorBoundary from '@components/ui/ErrorBoundary'
import ToastNotification from '@components/ui/ToastNotification'

// Hooks
import { useWebSocket } from '@hooks/useWebSocket'
import { useTheme } from '@hooks/useTheme'

// Utils
import { cn } from '@utils/cn'

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth)
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-900">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth)
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-900">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <>{children}</>
}

const App: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { isAuthenticated, loading, error } = useSelector((state: RootState) => state.auth)
  const { theme } = useTheme()
  
  // Initialize WebSocket connection for authenticated users
  useWebSocket({
    enabled: isAuthenticated,
    url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  })
  
  // Check authentication status on app load
  useEffect(() => {
    dispatch(checkAuthStatus())
  }, [dispatch])
  
  // Clear errors after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch(clearError())
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [error, dispatch])
  
  // Handle theme changes
  useEffect(() => {
    document.documentElement.className = theme
  }, [theme])
  
  // Show loading screen during initial auth check
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-900">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-4"
          >
            <h2 className="text-xl font-semibold text-primary-400 mb-2">
              Initializing Zmarty Dashboard
            </h2>
            <p className="text-secondary-400">
              Preparing your trading environment...
            </p>
          </motion.div>
        </div>
      </div>
    )
  }
  
  return (
    <ErrorBoundary>
      <div className={cn('min-h-screen bg-secondary-900', theme)}>
        <AnimatePresence mode="wait">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <AuthLayout>
                    <LoginPage />
                  </AuthLayout>
                </PublicRoute>
              }
            />
            <Route
              path="/register"
              element={
                <PublicRoute>
                  <AuthLayout>
                    <RegisterPage />
                  </AuthLayout>
                </PublicRoute>
              }
            />
            <Route
              path="/forgot-password"
              element={
                <PublicRoute>
                  <AuthLayout>
                    <ForgotPasswordPage />
                  </AuthLayout>
                </PublicRoute>
              }
            />
            
            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <DashboardPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ChatPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/trading"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <TradingPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <AnalyticsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <SettingsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ProfilePage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            
            {/* Default redirects */}
            <Route
              path="/"
              element={
                isAuthenticated ? 
                <Navigate to="/dashboard" replace /> : 
                <Navigate to="/login" replace />
              }
            />
            
            {/* 404 Page */}
            <Route
              path="*"
              element={
                <div className="min-h-screen flex items-center justify-center bg-secondary-900">
                  <div className="text-center">
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="text-8xl mb-4"
                    >
                      🔍
                    </motion.div>
                    <h1 className="text-4xl font-bold text-white mb-4">
                      Page Not Found
                    </h1>
                    <p className="text-secondary-400 mb-8 max-w-md">
                      The page you're looking for doesn't exist or has been moved.
                    </p>
                    <div className="space-x-4">
                      <button
                        onClick={() => window.history.back()}
                        className="btn-secondary"
                      >
                        Go Back
                      </button>
                      <button
                        onClick={() => window.location.href = isAuthenticated ? '/dashboard' : '/login'}
                        className="btn-primary"
                      >
                        {isAuthenticated ? 'Go to Dashboard' : 'Go to Login'}
                      </button>
                    </div>
                  </div>
                </div>
              }
            />
          </Routes>
        </AnimatePresence>
        
        {/* Global notifications */}
        <ToastNotification />
        
        {/* Global error display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 z-50 bg-danger-600 text-white px-4 py-3 rounded-lg shadow-lg max-w-sm"
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Error</h4>
                <p className="text-sm opacity-90">{error}</p>
              </div>
              <button
                onClick={() => dispatch(clearError())}
                className="ml-4 text-white hover:text-gray-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
        
        {/* Development tools */}
        {process.env.NODE_ENV === 'development' && (
          <div className="fixed bottom-4 left-4 z-50">
            <details className="bg-secondary-800 border border-secondary-700 rounded-lg p-3 text-xs">
              <summary className="cursor-pointer text-secondary-400 hover:text-secondary-300">
                Dev Tools
              </summary>
              <div className="mt-2 space-y-1 text-secondary-300">
                <div>Theme: {theme}</div>
                <div>Auth: {isAuthenticated ? '✅' : '❌'}</div>
                <div>Route: {window.location.pathname}</div>
                <div>Version: 1.0.0</div>
              </div>
            </details>
          </div>
        )}
      </div>
    </ErrorBoundary>
  )
}

export default App