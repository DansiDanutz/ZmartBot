import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import App from './AppSimple'
import { store } from './store/simpleStore'
import './index.css'

// Configure React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes
      retry: (failureCount, error: any) => {
        if (error?.response?.status === 401) return false
        return failureCount < 3
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error boundary caught an error:', error, errorInfo)
    
    // Report to error tracking service
    if (window.location.hostname !== 'localhost') {
      // Analytics or error reporting service
      console.error('Production error:', { error, errorInfo })
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-secondary-900 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-6">
            <div className="text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-white mb-4">
              Oops! Something went wrong
            </h1>
            <p className="text-secondary-400 mb-6">
              We're sorry for the inconvenience. Please try refreshing the page or contact support if the problem persists.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Refresh Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false })}
                className="w-full bg-secondary-700 hover:bg-secondary-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Try Again
              </button>
            </div>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-secondary-400 hover:text-secondary-300">
                  Error Details
                </summary>
                <pre className="mt-2 text-xs bg-secondary-800 p-3 rounded overflow-auto text-red-400">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Performance monitoring
if (typeof window !== 'undefined') {
  // Monitor Core Web Vitals
  const observePerformance = () => {
    try {
      // Largest Contentful Paint
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          console.log('LCP:', entry.startTime)
        }
      }).observe({ entryTypes: ['largest-contentful-paint'] })

      // First Input Delay
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          console.log('FID:', (entry as any).processingStart - entry.startTime)
        }
      }).observe({ entryTypes: ['first-input'] })

      // Cumulative Layout Shift
      new PerformanceObserver((list) => {
        let clsValue = 0
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value
          }
        }
        console.log('CLS:', clsValue)
      }).observe({ entryTypes: ['layout-shift'] })
    } catch (error) {
      console.log('Performance monitoring not supported')
    }
  }

  if (document.readyState === 'complete') {
    observePerformance()
  } else {
    window.addEventListener('load', observePerformance)
  }
}

// Custom toast configuration
const toastOptions = {
  duration: 4000,
  position: 'top-right' as const,
  style: {
    background: '#334155',
    color: '#f8fafc',
    border: '1px solid #475569',
  },
  success: {
    iconTheme: {
      primary: '#22c55e',
      secondary: '#f8fafc',
    },
  },
  error: {
    iconTheme: {
      primary: '#ef4444',
      secondary: '#f8fafc',
    },
  },
  loading: {
    iconTheme: {
      primary: '#3b82f6',
      secondary: '#f8fafc',
    },
  },
}

// App wrapper with all providers
const AppWithProviders = () => (
  <ErrorBoundary>
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <App />
          <Toaster toastOptions={toastOptions} />
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  </ErrorBoundary>
)

// Mount the app
const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement)
root.render(<AppWithProviders />)

// Hot Module Replacement for development
if (import.meta.hot) {
  import.meta.hot.accept()
}

// Debugging helpers for development
if (process.env.NODE_ENV === 'development') {
  // Expose useful debugging tools
  ;(window as any).__ZMARTY_DEBUG__ = {
    store,
    queryClient,
    version: '1.0.0',
  }
  
  console.log(
    '%cZmarty Dashboard Development Mode',
    'color: #3b82f6; font-size: 16px; font-weight: bold;'
  )
  console.log('Debug tools available at window.__ZMARTY_DEBUG__')
}