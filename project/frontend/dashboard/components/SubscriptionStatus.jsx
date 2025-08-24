import React, { useState, useEffect } from 'react';
import './SubscriptionStatus.css';

const SubscriptionStatus = ({ showFull = false }) => {
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rateLimitingEnabled, setRateLimitingEnabled] = useState(true);
  const [toggleLoading, setToggleLoading] = useState(false);

  useEffect(() => {
    const fetchSubscriptionStatus = async () => {
      try {
        const response = await fetch('/api/v1/subscription/status');
        const data = await response.json();
        
        if (data.success) {
          setSubscriptionData(data.data);
          // Set rate limiting status from quota manager
          setRateLimitingEnabled(data.data.quota_manager?.rate_limiting_enabled ?? true);
        } else {
          setError(data.error || 'Failed to fetch subscription status');
        }
      } catch (err) {
        setError('Network error fetching subscription status');
        console.error('Subscription status error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSubscriptionStatus();
    // Update every 5 minutes
    const interval = setInterval(fetchSubscriptionStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleRateLimiting = async (e) => {
    e.stopPropagation(); // Prevent triggering the Cryptometer click
    
    if (toggleLoading) return;
    
    setToggleLoading(true);
    try {
      const response = await fetch('/api/v1/subscription/toggle-rate-limiting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setRateLimitingEnabled(data.data.rate_limiting_enabled);
        
        // Show notification
        const message = data.data.rate_limiting_enabled 
          ? '🔒 Rate limiting enabled - quotas enforced'
          : '🔓 Rate limiting disabled - unlimited calls';
        
        // Simple toast notification (you can replace with your preferred notification system)
        console.log(message);
        
        // Refresh subscription data to get updated quota status
        setTimeout(() => {
          const refreshData = async () => {
            try {
              const refreshResponse = await fetch('/api/v1/subscription/status');
              const refreshData = await refreshResponse.json();
              if (refreshData.success) {
                setSubscriptionData(refreshData.data);
              }
            } catch (err) {
              console.error('Error refreshing subscription data:', err);
            }
          };
          refreshData();
        }, 500);
        
      } else {
        console.error('Failed to toggle rate limiting:', data.error);
      }
    } catch (err) {
      console.error('Error toggling rate limiting:', err);
    } finally {
      setToggleLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="subscription-status loading">
        <div className="loading-spinner"></div>
        <span>Loading subscription...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="subscription-status error">
        <span className="error-icon">⚠️</span>
        <span>{error}</span>
      </div>
    );
  }

  if (!subscriptionData?.subscription) {
    return null;
  }

  const { subscription, forecast } = subscriptionData;
  const usagePercent = subscription.usage_percent || 0;
  const daysUntilExpiry = subscription.days_until_expiry || 0;

  // Determine status color and urgency
  const getStatusColor = () => {
    if (daysUntilExpiry <= 1) return 'critical';
    if (daysUntilExpiry <= 7) return 'warning';
    if (usagePercent >= 85) return 'warning';
    if (usagePercent >= 70) return 'caution';
    return 'healthy';
  };

  const getExpiryMessage = () => {
    if (daysUntilExpiry === 0) return 'Expires TODAY!';
    if (daysUntilExpiry === 1) return 'Expires TOMORROW!';
    if (daysUntilExpiry <= 7) return `Expires in ${daysUntilExpiry} days`;
    return `${daysUntilExpiry} days remaining`;
  };

  const statusColor = getStatusColor();

  if (!showFull) {
    // Compact version for header with click handler
    const handleCryptometerClick = () => {
      window.open('https://www.cryptometer.io/services.php#api', '_blank', 'noopener,noreferrer');
    };

    return (
      <div 
        className={`subscription-status compact ${statusColor} clickable`}
        onClick={handleCryptometerClick}
        title="Click to visit Cryptometer API Services"
      >
        <div className="cryptometer-header">
          <span className="cryptometer-label">Cryptometer</span>
          <button
            className={`rate-limit-toggle ${rateLimitingEnabled ? 'enabled' : 'disabled'}`}
            onClick={handleToggleRateLimiting}
            disabled={toggleLoading}
            title={rateLimitingEnabled ? 'Rate limiting ON - Click to disable' : 'Rate limiting OFF - Click to enable'}
          >
            {toggleLoading ? '⏳' : rateLimitingEnabled ? '🔒' : '🔓'}
          </button>
        </div>
        <div className="compact-info">
          <div className="usage-display">
            <span className="usage-percent">{usagePercent.toFixed(1)}%</span>
            <span className="days-remaining">{daysUntilExpiry} days remaining</span>
          </div>
          {!rateLimitingEnabled && (
            <div className="unlimited-warning">
              <span className="unlimited-text">🔓 UNLIMITED</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Full detailed version
  return (
    <div className={`subscription-status full ${statusColor}`}>
      <div className="subscription-header">
        <h3>🔐 API Subscription Status</h3>
        <div className={`status-badge ${statusColor}`}>
          {subscription.api_plan}
        </div>
      </div>

      <div className="subscription-details">
        <div className="usage-section">
          <div className="usage-title">Monthly Usage</div>
          <div className="usage-stats">
            <div className="usage-numbers">
              <span className="current">{subscription.current_usage?.toLocaleString()}</span>
              <span className="separator">/</span>
              <span className="limit">{subscription.monthly_limit?.toLocaleString()}</span>
              <span className="unit">calls</span>
            </div>
            <div className="usage-bar">
              <div 
                className="usage-fill" 
                style={{ width: `${Math.min(usagePercent, 100)}%` }}
              ></div>
            </div>
            <div className="usage-percent">{usagePercent.toFixed(1)}%</div>
          </div>
          <div className="remaining-calls">
            {subscription.remaining_calls?.toLocaleString()} calls remaining
          </div>
        </div>

        <div className="dates-section">
          <div className="date-item">
            <span className="date-label">Expires:</span>
            <span className={`date-value ${daysUntilExpiry <= 1 ? 'urgent' : ''}`}>
              {subscription.expiry_date} ({getExpiryMessage()})
            </span>
          </div>
          <div className="date-item">
            <span className="date-label">Resets:</span>
            <span className="date-value">
              {subscription.reset_date} ({subscription.days_until_reset} days)
            </span>
          </div>
        </div>

        {forecast && (
          <div className="forecast-section">
            <div className="forecast-title">📈 Usage Forecast</div>
            <div className="forecast-stats">
              <div className="forecast-item">
                <span className="forecast-label">Daily Avg:</span>
                <span className="forecast-value">{forecast.daily_average} calls/day</span>
              </div>
              <div className="forecast-item">
                <span className="forecast-label">Projected Total:</span>
                <span className="forecast-value">
                  {forecast.forecast_total?.toLocaleString()} calls ({forecast.forecast_percent}%)
                </span>
              </div>
              {forecast.will_exceed_limit && (
                <div className="forecast-warning">
                  ⚠️ Projected to exceed monthly limit!
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {(daysUntilExpiry <= 7 || usagePercent >= 70) && (
        <div className="subscription-alert">
          <div className="alert-icon">
            {daysUntilExpiry <= 1 ? '🚨' : daysUntilExpiry <= 7 ? '⚠️' : '🟡'}
          </div>
          <div className="alert-message">
            {daysUntilExpiry <= 1 
              ? 'URGENT: Subscription expires very soon!' 
              : daysUntilExpiry <= 7 
                ? 'Please renew your subscription soon' 
                : 'Monitor API usage closely'
            }
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionStatus;