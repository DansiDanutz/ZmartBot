// React import not needed in React 18 with JSX transform
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'
import { ErrorBoundary } from 'react-error-boundary'

import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import ErrorFallback from './components/ErrorFallback'
import Dashboard from './pages/Dashboard'
import Trading from './pages/Trading'
import Signals from './pages/Signals'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import Login from './pages/Login'
import NotFound from './pages/NotFound'

// Create a client
const queryClient = new QueryClient()

function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <QueryClientProvider client={queryClient}>
        <HelmetProvider>
          <Router>
            <div className="min-h-screen bg-slate-900">
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#1e293b',
                    color: '#f8fafc',
                    border: '1px solid #475569',
                  },
                }}
              />
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<Login />} />
                
                {/* Protected routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }>
                  <Route index element={<Dashboard />} />
                  <Route path="trading" element={<Trading />} />
                  <Route path="signals" element={<Signals />} />
                  <Route path="analytics" element={<Analytics />} />
                  <Route path="settings" element={<Settings />} />
                </Route>
                
                {/* Admin routes */}
                <Route path="/admin" element={
                  <ProtectedRoute requiredRole="admin">
                    <Layout />
                  </ProtectedRoute>
                }>
                  <Route index element={<div className="p-6"><h1 className="text-2xl font-bold text-white">Admin Panel</h1><p className="text-slate-400 mt-2">Admin features coming soon...</p></div>} />
                </Route>
                
                {/* 404 route */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </Router>
        </HelmetProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App 