import React, { useState, useEffect } from 'react'
import { Bell, Settings, Activity, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

const EnhancedAlertsCard = () => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [systemStatus, setSystemStatus] = useState('active')
  const [alertCount, setAlertCount] = useState(0)
  const [recentTriggers, setRecentTriggers] = useState(0)

  // Mock data for demonstration - replace with real API calls
  useEffect(() => {
    // Simulate fetching system status
    setAlertCount(12)
    setRecentTriggers(3)
  }, [])

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#10B981'
      case 'warning': return '#F59E0B'
      case 'error': return '#EF4444'
      default: return '#6B7280'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle size={16} color="#10B981" />
      case 'warning': return <AlertTriangle size={16} color="#F59E0B" />
      case 'error': return <XCircle size={16} color="#EF4444" />
      default: return <Activity size={16} color="#6B7280" />
    }
  }

  return (
    <div className="enhanced-alerts-card">
      {/* Card Header */}
      <div className="card-header">
        <div className="card-header-left">
          <div className="card-icon-wrapper">
            <Bell size={24} className="card-icon" />
          </div>
          <div className="card-title-section">
            <h2 className="card-title">Enhanced Alerts System</h2>
            <p className="card-subtitle">Advanced trading alerts and notifications</p>
          </div>
        </div>
        <div className="card-header-right">
          <div className="status-indicator">
            {getStatusIcon(systemStatus)}
            <span className="status-text" style={{ color: getStatusColor(systemStatus) }}>
              {systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1)}
            </span>
          </div>
          <button
            className="expand-button"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? '−' : '+'}
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-item">
          <div className="stat-icon">
            <Bell size={16} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{alertCount}</div>
            <div className="stat-label">Active Alerts</div>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon">
            <Activity size={16} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{recentTriggers}</div>
            <div className="stat-label">Recent Triggers</div>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon">
            <Clock size={16} />
          </div>
          <div className="stat-content">
            <div className="stat-value">24h</div>
            <div className="stat-label">Uptime</div>
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="expanded-content">
          <div className="content-wrapper">
            <div style={{ 
              padding: '20px',
              textAlign: 'center',
              background: 'rgba(0, 255, 148, 0.1)',
              borderRadius: '12px',
              border: '1px solid rgba(0, 255, 148, 0.3)',
              color: '#00ff94'
            }}>
              <h3>🚨 Alerts System</h3>
              <p>Use the "Alerts" tab in the sidebar to view all technical alerts with expand functionality.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EnhancedAlertsCard
