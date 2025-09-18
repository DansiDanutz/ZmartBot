/**
 * ErrorBoundary - Comprehensive error handling for React components
 * Catches JavaScript errors anywhere in the component tree and provides fallback UI
 */

import React from 'react';
import './ErrorBoundary.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      errorId: Date.now().toString(36) + Math.random().toString(36).substr(2, 9)
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('🚨 Error Boundary caught an error:', {
      error: error.toString(),
      errorInfo: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });

    this.setState({
      error: error.toString(),
      errorInfo: errorInfo.componentStack
    });

    // Report error to external service (if available)
    this.reportError(error, errorInfo);
  }

  reportError = (error, errorInfo) => {
    // Send error to analytics/monitoring service
    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: error.toString(),
        fatal: false,
        custom_parameter_component: errorInfo.componentStack.split('\n')[1]
      });
    }

    // Send to error tracking service (implement based on your service)
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      });
    }
  };

  handleRetry = () => {
    // Reset error state to retry rendering
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    });

    // Optional: refresh the page for critical errors
    if (this.props.refreshOnRetry) {
      window.location.reload();
    }
  };

  handleReportBug = () => {
    const errorReport = {
      error: this.state.error,
      errorInfo: this.state.errorInfo,
      errorId: this.state.errorId,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    // Copy error report to clipboard
    if (navigator.clipboard) {
      navigator.clipboard.writeText(JSON.stringify(errorReport, null, 2));
      alert('Error details copied to clipboard. Please share with support.');
    } else {
      // Fallback for older browsers
      console.log('Error Report:', errorReport);
      alert('Error details logged to console. Please check browser console and share with support.');
    }
  };

  render() {
    if (this.state.hasError) {
      // Render different fallback UI based on error boundary level
      if (this.props.level === 'app') {
        return this.renderAppLevelError();
      } else if (this.props.level === 'page') {
        return this.renderPageLevelError();
      } else {
        return this.renderComponentLevelError();
      }
    }

    return this.props.children;
  }

  renderAppLevelError() {
    return (
      <div className="error-boundary app-level">
        <div className="error-container">
          <div className="error-icon">💥</div>
          <h1>Oops! Something went wrong</h1>
          <p className="error-message">
            ZmartyChat encountered an unexpected error and needs to restart.
          </p>

          <div className="error-actions">
            <button
              className="error-btn primary"
              onClick={() => window.location.reload()}
            >
              🔄 Restart App
            </button>
            <button
              className="error-btn secondary"
              onClick={this.handleReportBug}
            >
              📋 Report Bug
            </button>
          </div>

          <div className="error-details">
            <details>
              <summary>Technical Details</summary>
              <div className="error-info">
                <p><strong>Error ID:</strong> {this.state.errorId}</p>
                <p><strong>Error:</strong> {this.state.error}</p>
                <pre className="error-stack">
                  {this.state.errorInfo}
                </pre>
              </div>
            </details>
          </div>

          <div className="support-info">
            <p>If this problem persists, please contact support with Error ID: <code>{this.state.errorId}</code></p>
          </div>
        </div>
      </div>
    );
  }

  renderPageLevelError() {
    return (
      <div className="error-boundary page-level">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h2>Page Error</h2>
          <p className="error-message">
            This page encountered an error, but the rest of the app should work normally.
          </p>

          <div className="error-actions">
            <button
              className="error-btn primary"
              onClick={this.handleRetry}
            >
              🔄 Retry
            </button>
            <button
              className="error-btn secondary"
              onClick={() => window.history.back()}
            >
              ← Go Back
            </button>
            <button
              className="error-btn tertiary"
              onClick={this.handleReportBug}
            >
              📋 Report
            </button>
          </div>

          {this.props.showDetails && (
            <div className="error-details">
              <p><strong>Error:</strong> {this.state.error}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  renderComponentLevelError() {
    return (
      <div className="error-boundary component-level">
        <div className="error-container">
          <div className="error-icon">🔧</div>
          <h3>Component Error</h3>
          <p className="error-message">
            {this.props.fallbackMessage || 'This component is temporarily unavailable.'}
          </p>

          <div className="error-actions">
            <button
              className="error-btn primary small"
              onClick={this.handleRetry}
            >
              🔄 Retry
            </button>
            {this.props.showReportButton && (
              <button
                className="error-btn secondary small"
                onClick={this.handleReportBug}
              >
                📋 Report
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }
}

// Higher-order component for wrapping components with error boundaries
export const withErrorBoundary = (Component, options = {}) => {
  const WrappedComponent = (props) => (
    <ErrorBoundary
      level={options.level || 'component'}
      fallbackMessage={options.fallbackMessage}
      showDetails={options.showDetails}
      showReportButton={options.showReportButton}
      refreshOnRetry={options.refreshOnRetry}
    >
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
};

// Functional component wrapper for modern React
export const ErrorBoundaryProvider = ({ children, ...props }) => (
  <ErrorBoundary {...props}>
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;