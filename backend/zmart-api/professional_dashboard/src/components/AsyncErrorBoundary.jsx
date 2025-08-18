import React, { useState, useEffect } from 'react'
import ErrorBoundary from './ErrorBoundary'

const AsyncErrorBoundary = ({ children, onError, fallback }) => {
  const [asyncError, setAsyncError] = useState(null)

  // Handle async errors that don't bubble up to React Error Boundaries
  useEffect(() => {
    const handleUnhandledRejection = (event) => {
      console.error('Unhandled Promise Rejection:', event.reason)
      
      // Create a synthetic error for the error boundary
      const error = new Error(`Async Error: ${event.reason?.message || event.reason}`)
      error.stack = event.reason?.stack || error.stack
      
      setAsyncError(error)
      
      if (onError) {
        onError(error, { type: 'unhandledrejection', originalEvent: event })
      }
    }

    const handleError = (event) => {
      console.error('Global Error:', event.error)
      
      const error = event.error || new Error(event.message)
      setAsyncError(error)
      
      if (onError) {
        onError(error, { type: 'error', originalEvent: event })
      }
    }

    // Listen for unhandled promise rejections and global errors
    window.addEventListener('unhandledrejection', handleUnhandledRejection)
    window.addEventListener('error', handleError)

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
      window.removeEventListener('error', handleError)
    }
  }, [onError])

  // If we caught an async error, throw it to trigger the Error Boundary
  if (asyncError) {
    throw asyncError
  }

  return (
    <ErrorBoundary fallback={fallback}>
      {children}
    </ErrorBoundary>
  )
}

// Custom hook for handling async errors in components
export const useAsyncError = () => {
  const [error, setError] = useState(null)

  const throwAsyncError = (asyncError) => {
    setError(asyncError)
  }

  const resetAsyncError = () => {
    setError(null)
  }

  useEffect(() => {
    if (error) {
      // Re-throw error to be caught by Error Boundary
      throw error
    }
  }, [error])

  return { throwAsyncError, resetAsyncError }
}

// HOC for wrapping components with async error handling
export const withAsyncErrorBoundary = (Component, errorBoundaryProps = {}) => {
  return function WrappedComponent(props) {
    return (
      <AsyncErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </AsyncErrorBoundary>
    )
  }
}

export default AsyncErrorBoundary