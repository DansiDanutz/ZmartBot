import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    }
  }

  static getDerivedStateFromError(error) {
    // Update state to show error UI
    return {
      hasError: true,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('Error Boundary caught an error:', error, errorInfo)
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    })

    // Send error to monitoring service
    this.logErrorToService(error, errorInfo)
  }

  logErrorToService = async (error, errorInfo) => {
    try {
      const errorReport = {
        error: {
          message: error.message,
          stack: error.stack,
          name: error.name
        },
        errorInfo: {
          componentStack: errorInfo.componentStack
        },
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: this.props.userId || 'anonymous',
        errorId: this.state.errorId
      }

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.group('🚨 Error Boundary Report')
        console.error('Error:', error)
        console.error('Error Info:', errorInfo)
        console.error('Full Report:', errorReport)
        console.groupEnd()
      }

      // Send to backend error logging endpoint
      await fetch('/api/v1/system/error-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorReport)
      }).catch(() => {
        // Fail silently if error logging fails
        console.warn('Failed to send error report to server')
      })

    } catch (logError) {
      console.error('Failed to log error:', logError)
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    })
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      const { error, errorInfo } = this.state
      const { fallback: CustomFallback, level = 'component' } = this.props

      // Use custom fallback if provided
      if (CustomFallback) {
        return (
          <CustomFallback
            error={error}
            errorInfo={errorInfo}
            onRetry={this.handleRetry}
            onReload={this.handleReload}
          />
        )
      }

      // Application-level error (more severe)
      if (level === 'application') {
        return (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, #1a1a1a 0%, #2d1b69 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            color: '#ffffff'
          }}>
            <div style={{
              background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
              border: '2px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '20px',
              padding: '40px',
              maxWidth: '600px',
              width: '90%',
              textAlign: 'center',
              boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
              backdropFilter: 'blur(20px)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>💥</div>
              <h1 style={{ 
                margin: '0 0 20px 0', 
                fontSize: '2rem', 
                color: '#ef4444',
                fontWeight: '600'
              }}>
                Application Error
              </h1>
              <p style={{ 
                margin: '0 0 30px 0', 
                fontSize: '1.1rem', 
                color: 'rgba(255,255,255,0.8)',
                lineHeight: '1.6'
              }}>
                The Enhanced Alerts System has encountered a critical error and needs to be restarted.
                Our team has been automatically notified.
              </p>
              
              {process.env.NODE_ENV === 'development' && (
                <div style={{
                  background: 'rgba(0,0,0,0.3)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  padding: '20px',
                  marginBottom: '30px',
                  textAlign: 'left',
                  fontSize: '0.9rem',
                  fontFamily: 'monospace',
                  color: '#ff6b6b'
                }}>
                  <div style={{ marginBottom: '10px', fontWeight: 'bold' }}>
                    Error: {error?.message}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>
                    Error ID: {this.state.errorId}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
                <button
                  onClick={this.handleRetry}
                  style={{
                    padding: '12px 24px',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    border: 'none',
                    borderRadius: '10px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: '600',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)'
                    e.target.style.boxShadow = '0 8px 25px rgba(16, 185, 129, 0.4)'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)'
                    e.target.style.boxShadow = 'none'
                  }}
                >
                  🔄 Try Again
                </button>
                <button
                  onClick={this.handleReload}
                  style={{
                    padding: '12px 24px',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    border: 'none',
                    borderRadius: '10px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: '600',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)'
                    e.target.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.4)'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)'
                    e.target.style.boxShadow = 'none'
                  }}
                >
                  🔄 Reload Page
                </button>
              </div>
            </div>
          </div>
        )
      }

      // Component-level error (less severe)
      return (
        <div style={{
          background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%)',
          border: '2px solid rgba(239, 68, 68, 0.2)',
          borderRadius: '16px',
          padding: '30px',
          margin: '20px 0',
          textAlign: 'center',
          color: '#ffffff',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>⚠️</div>
          <h3 style={{ 
            margin: '0 0 15px 0', 
            fontSize: '1.3rem', 
            color: '#ef4444',
            fontWeight: '600'
          }}>
            Component Error
          </h3>
          <p style={{ 
            margin: '0 0 20px 0', 
            color: 'rgba(255,255,255,0.8)',
            fontSize: '0.95rem',
            lineHeight: '1.5'
          }}>
            This section of the Enhanced Alerts System encountered an error.
            You can try refreshing this component or reload the entire page.
          </p>

          {process.env.NODE_ENV === 'development' && (
            <div style={{
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '15px',
              marginBottom: '20px',
              textAlign: 'left',
              fontSize: '0.85rem',
              fontFamily: 'monospace',
              color: '#ff9999'
            }}>
              <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>
                Error: {error?.message}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>
                Component: {errorInfo?.componentStack?.split('\n')[1]?.trim()}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>
                Error ID: {this.state.errorId}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              onClick={this.handleRetry}
              style={{
                padding: '10px 20px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '600'
              }}
            >
              🔄 Retry Component
            </button>
            <button
              onClick={this.handleReload}
              style={{
                padding: '10px 20px',
                background: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '600'
              }}
            >
              🔄 Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Higher-order component for easy wrapping
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  return function WrappedComponent(props) {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </ErrorBoundary>
    )
  }
}

// Hook for functional components to handle errors
export const useErrorHandler = () => {
  const [error, setError] = React.useState(null)

  const throwError = React.useCallback((error) => {
    setError(() => {
      throw error
    })
  }, [])

  const resetError = React.useCallback(() => {
    setError(null)
  }, [])

  React.useEffect(() => {
    if (error) {
      throw error
    }
  }, [error])

  return { throwError, resetError }
}

export default ErrorBoundary