import React, { useState, useEffect, useCallback } from 'react'

const AlertsModule = ({ symbol, onAlertTriggered }) => {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [selectedTab, setSelectedTab] = useState(0)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)
  
  // Form states for creating/editing alerts
  const [formData, setFormData] = useState({
    symbol: symbol || '',
    alert_type: 'PRICE',
    conditions: {
      threshold: '',
      operator: 'above',
      timeframe: '1m'
    },
    notification_channels: ['webhook', 'database'],
    metadata: {}
  })

  // WebSocket connection for real-time updates
  const [ws, setWs] = useState(null)

  // Fetch alerts
  const fetchAlerts = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (symbol) params.append('symbol', symbol)
      
      const response = await fetch(`http://localhost:3400/api/v1/alerts/list?${params}`)
      const data = await response.json()
      
      if (data.success) {
        setAlerts(data.data)
      } else {
        throw new Error(data.error || 'Failed to fetch alerts')
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch alerts')
    } finally {
      setLoading(false)
    }
  }, [symbol])

  // Fetch system status
  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:3400/api/v1/alerts/status')
      const data = await response.json()
      if (data.success) {
        setSystemStatus(data.data)
      }
    } catch (err) {
      console.error('Failed to fetch system status:', err)
    }
  }

  // Initialize WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8001')
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
      // Subscribe to alerts
      if (symbol) {
        websocket.send(JSON.stringify({
          type: 'subscribe_symbols',
          symbols: [symbol]
        }))
      }
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'alert_triggered') {
        // Refresh alerts and notify parent
        fetchAlerts()
        if (onAlertTriggered) {
          onAlertTriggered(data.alert)
        }
        setSuccess(`Alert triggered: ${data.alert.symbol} - ${data.alert.type}`)
      }
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected')
    }
    
    setWs(websocket)
    
    return () => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.close()
      }
    }
  }, [symbol, fetchAlerts, onAlertTriggered])

  // Initial data fetch
  useEffect(() => {
    fetchAlerts()
    fetchSystemStatus()
    const interval = setInterval(fetchSystemStatus, 30000) // Update status every 30 seconds
    return () => clearInterval(interval)
  }, [fetchAlerts])

  // Create new alert
  const handleCreateAlert = async () => {
    try {
      const response = await fetch('http://localhost:3400/api/v1/alerts/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      const data = await response.json()
      if (data.success) {
        setSuccess('Alert created successfully')
        setCreateDialogOpen(false)
        fetchAlerts()
        // Reset form
        setFormData({
          symbol: symbol || '',
          alert_type: 'PRICE',
          conditions: {
            threshold: '',
            operator: 'above',
            timeframe: '1m'
          },
          notification_channels: ['webhook', 'database'],
          metadata: {}
        })
      } else {
        throw new Error(data.error || 'Failed to create alert')
      }
    } catch (err) {
      setError(err.message || 'Failed to create alert')
    }
  }

  // Update alert
  const handleUpdateAlert = async () => {
    if (!selectedAlert) return
    
    try {
      const response = await fetch(`http://localhost:3400/api/v1/alerts/${selectedAlert.alert_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conditions: formData.conditions,
          notification_channels: formData.notification_channels,
          metadata: formData.metadata
        })
      })
      
      const data = await response.json()
      if (data.success) {
        setSuccess('Alert updated successfully')
        setEditDialogOpen(false)
        fetchAlerts()
      } else {
        throw new Error(data.error || 'Failed to update alert')
      }
    } catch (err) {
      setError(err.message || 'Failed to update alert')
    }
  }

  // Delete alert
  const handleDeleteAlert = async (alertId) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/alerts/${alertId}`, {
        method: 'DELETE'
      })
      
      const data = await response.json()
      if (data.success) {
        setSuccess('Alert deleted successfully')
        fetchAlerts()
      } else {
        throw new Error(data.error || 'Failed to delete alert')
      }
    } catch (err) {
      setError(err.message || 'Failed to delete alert')
    }
  }

  // Pause/Resume alert
  const handleToggleAlert = async (alert) => {
    const endpoint = alert.status === 'ACTIVE' ? 'pause' : 'resume'
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/alerts/${alert.alert_id}/${endpoint}`, {
        method: 'POST'
      })
      
      const data = await response.json()
      if (data.success) {
        setSuccess(`Alert ${endpoint}d successfully`)
        fetchAlerts()
      } else {
        throw new Error(data.error || `Failed to ${endpoint} alert`)
      }
    } catch (err) {
      setError(err.message || `Failed to ${endpoint} alert`)
    }
  }

  // Get alert type icon
  const getAlertTypeIcon = (type) => {
    switch (type) {
      case 'PRICE':
        return '📈'
      case 'VOLUME':
        return '📊'
      case 'TECHNICAL':
        return '📉'
      case 'PATTERN':
        return '📐'
      default:
        return '🔔'
    }
  }

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE':
        return '#10b981'
      case 'PAUSED':
        return '#f59e0b'
      case 'TRIGGERED':
        return '#3b82f6'
      case 'EXPIRED':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  return (
    <div style={{ width: '100%' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h3 style={{ margin: 0, color: '#00bcd4', fontSize: '1.5rem' }}>
            Professional Trading Alerts
            {symbol && (
              <span style={{ 
                marginLeft: '10px',
                padding: '4px 12px',
                background: 'rgba(0, 188, 212, 0.2)',
                borderRadius: '20px',
                fontSize: '0.9rem',
                fontWeight: 'normal'
              }}>
                {symbol}
              </span>
            )}
          </h3>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={fetchAlerts}
            disabled={loading}
            style={{
              padding: '8px 16px',
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '0.9rem'
            }}
          >
            🔄 Refresh
          </button>
          <button
            onClick={() => setCreateDialogOpen(true)}
            style={{
              padding: '8px 16px',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: '600'
            }}
          >
            ➕ Create Alert
          </button>
        </div>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div style={{
          marginBottom: '20px',
          padding: '15px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '10px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>System Status</div>
              <div style={{ fontSize: '1.1rem', color: systemStatus.engine_running ? '#10b981' : '#ef4444' }}>
                {systemStatus.engine_running ? '✅ Active' : '❌ Inactive'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>Active Alerts</div>
              <div style={{ fontSize: '1.1rem' }}>{systemStatus.active_alerts || 0}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>Monitored Symbols</div>
              <div style={{ fontSize: '1.1rem' }}>{systemStatus.monitored_symbols || 0}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>Last Check</div>
              <div style={{ fontSize: '1.1rem' }}>
                {systemStatus.last_check ? new Date(systemStatus.last_check).toLocaleTimeString() : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ 
        display: 'flex', 
        gap: '10px',
        marginBottom: '20px',
        borderBottom: '2px solid rgba(255,255,255,0.1)',
        paddingBottom: '10px'
      }}>
        <button
          onClick={() => setSelectedTab(0)}
          style={{
            padding: '8px 16px',
            background: selectedTab === 0 ? 'rgba(0, 188, 212, 0.2)' : 'transparent',
            border: 'none',
            borderBottom: selectedTab === 0 ? '2px solid #00bcd4' : 'none',
            color: selectedTab === 0 ? '#00bcd4' : 'rgba(255,255,255,0.6)',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: selectedTab === 0 ? '600' : 'normal'
          }}
        >
          Active Alerts ({alerts.filter(a => a.status === 'ACTIVE').length})
        </button>
        <button
          onClick={() => setSelectedTab(1)}
          style={{
            padding: '8px 16px',
            background: selectedTab === 1 ? 'rgba(0, 188, 212, 0.2)' : 'transparent',
            border: 'none',
            borderBottom: selectedTab === 1 ? '2px solid #00bcd4' : 'none',
            color: selectedTab === 1 ? '#00bcd4' : 'rgba(255,255,255,0.6)',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: selectedTab === 1 ? '600' : 'normal'
          }}
        >
          All Alerts ({alerts.length})
        </button>
      </div>

      {/* Loading indicator */}
      {loading && (
        <div style={{ 
          width: '100%', 
          height: '4px', 
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '2px',
          overflow: 'hidden',
          marginBottom: '20px'
        }}>
          <div style={{
            width: '30%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, #00bcd4, transparent)',
            animation: 'loading 1.5s infinite'
          }} />
        </div>
      )}

      {/* Alerts Table */}
      {selectedTab <= 1 && (
        <div style={{
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '10px',
          border: '1px solid rgba(255,255,255,0.1)',
          overflow: 'hidden'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.05)' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Type</th>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Symbol</th>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Conditions</th>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Triggers</th>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Last Triggered</th>
                <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts
                .filter(alert => selectedTab === 0 ? alert.status === 'ACTIVE' : true)
                .map((alert) => (
                  <tr key={alert.alert_id} style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '1.2rem' }}>{getAlertTypeIcon(alert.type)}</span>
                        <span style={{ fontSize: '0.9rem' }}>{alert.type}</span>
                      </div>
                    </td>
                    <td style={{ padding: '12px', fontSize: '0.9rem' }}>{alert.symbol}</td>
                    <td style={{ padding: '12px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)' }}>
                      {JSON.stringify(alert.conditions).substring(0, 50)}...
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        padding: '4px 8px',
                        background: `${getStatusColor(alert.status)}20`,
                        color: getStatusColor(alert.status),
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        fontWeight: '600'
                      }}>
                        {alert.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '0.9rem' }}>🔔</span>
                        <span style={{ 
                          background: 'rgba(59, 130, 246, 0.2)',
                          color: '#3b82f6',
                          padding: '2px 6px',
                          borderRadius: '10px',
                          fontSize: '0.8rem',
                          fontWeight: '600'
                        }}>
                          {alert.trigger_count}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '12px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)' }}>
                      {alert.last_triggered 
                        ? new Date(alert.last_triggered).toLocaleString()
                        : 'Never'
                      }
                    </td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => handleToggleAlert(alert)}
                          style={{
                            padding: '4px 8px',
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            borderRadius: '4px',
                            color: '#ffffff',
                            cursor: 'pointer',
                            fontSize: '0.8rem'
                          }}
                        >
                          {alert.status === 'ACTIVE' ? '⏸️' : '▶️'}
                        </button>
                        <button
                          onClick={() => {
                            setSelectedAlert(alert)
                            setFormData({
                              symbol: alert.symbol,
                              alert_type: alert.type,
                              conditions: alert.conditions,
                              notification_channels: alert.notification_channels,
                              metadata: alert.metadata || {}
                            })
                            setEditDialogOpen(true)
                          }}
                          style={{
                            padding: '4px 8px',
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            borderRadius: '4px',
                            color: '#ffffff',
                            cursor: 'pointer',
                            fontSize: '0.8rem'
                          }}
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDeleteAlert(alert.alert_id)}
                          style={{
                            padding: '4px 8px',
                            background: 'rgba(239, 68, 68, 0.2)',
                            border: 'none',
                            borderRadius: '4px',
                            color: '#ef4444',
                            cursor: 'pointer',
                            fontSize: '0.8rem'
                          }}
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create/Edit Dialog */}
      {(createDialogOpen || editDialogOpen) && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#1a1a1a',
            borderRadius: '12px',
            padding: '24px',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '80vh',
            overflow: 'auto',
            border: '2px solid rgba(255,255,255,0.1)'
          }}>
            <h3 style={{ margin: '0 0 20px 0', color: '#00bcd4' }}>
              {createDialogOpen ? 'Create New Alert' : 'Edit Alert'}
            </h3>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                Symbol
              </label>
              <input
                type="text"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                disabled={editDialogOpen}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '6px',
                  color: '#ffffff',
                  fontSize: '0.9rem'
                }}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                Alert Type
              </label>
              <select
                value={formData.alert_type}
                onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                disabled={editDialogOpen}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '6px',
                  color: '#ffffff',
                  fontSize: '0.9rem'
                }}
              >
                <option value="PRICE">Price Alert</option>
                <option value="VOLUME">Volume Alert</option>
                <option value="TECHNICAL">Technical Indicator</option>
                <option value="PATTERN">Pattern Recognition</option>
              </select>
            </div>
            
            {formData.alert_type === 'PRICE' && (
              <>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                    Operator
                  </label>
                  <select
                    value={formData.conditions.operator}
                    onChange={(e) => setFormData({
                      ...formData,
                      conditions: { ...formData.conditions, operator: e.target.value }
                    })}
                    style={{
                      width: '100%',
                      padding: '10px',
                      background: 'rgba(255,255,255,0.1)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '6px',
                      color: '#ffffff',
                      fontSize: '0.9rem'
                    }}
                  >
                    <option value="above">Above</option>
                    <option value="below">Below</option>
                    <option value="crosses">Crosses</option>
                  </select>
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                    Threshold
                  </label>
                  <input
                    type="number"
                    value={formData.conditions.threshold}
                    onChange={(e) => setFormData({
                      ...formData,
                      conditions: { ...formData.conditions, threshold: e.target.value }
                    })}
                    style={{
                      width: '100%',
                      padding: '10px',
                      background: 'rgba(255,255,255,0.1)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '6px',
                      color: '#ffffff',
                      fontSize: '0.9rem'
                    }}
                  />
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                    Timeframe
                  </label>
                  <select
                    value={formData.conditions.timeframe}
                    onChange={(e) => setFormData({
                      ...formData,
                      conditions: { ...formData.conditions, timeframe: e.target.value }
                    })}
                    style={{
                      width: '100%',
                      padding: '10px',
                      background: 'rgba(255,255,255,0.1)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '6px',
                      color: '#ffffff',
                      fontSize: '0.9rem'
                    }}
                  >
                    <option value="1m">1 Minute</option>
                    <option value="5m">5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="1h">1 Hour</option>
                    <option value="4h">4 Hours</option>
                    <option value="1d">1 Day</option>
                  </select>
                </div>
              </>
            )}
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                Notification Channels
              </label>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {['webhook', 'database', 'email', 'telegram'].map((channel) => (
                  <button
                    key={channel}
                    onClick={() => {
                      const channels = formData.notification_channels.includes(channel)
                        ? formData.notification_channels.filter(c => c !== channel)
                        : [...formData.notification_channels, channel]
                      setFormData({ ...formData, notification_channels: channels })
                    }}
                    style={{
                      padding: '6px 12px',
                      background: formData.notification_channels.includes(channel) 
                        ? 'rgba(0, 188, 212, 0.2)' 
                        : 'rgba(255,255,255,0.1)',
                      border: formData.notification_channels.includes(channel)
                        ? '1px solid #00bcd4'
                        : '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '20px',
                      color: formData.notification_channels.includes(channel)
                        ? '#00bcd4'
                        : 'rgba(255,255,255,0.7)',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}
                  >
                    {channel}
                  </button>
                ))}
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                onClick={() => {
                  setCreateDialogOpen(false)
                  setEditDialogOpen(false)
                }}
                style={{
                  padding: '10px 20px',
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '6px',
                  color: '#ffffff',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
              >
                Cancel
              </button>
              <button
                onClick={createDialogOpen ? handleCreateAlert : handleUpdateAlert}
                style={{
                  padding: '10px 20px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#ffffff',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '600'
                }}
              >
                {createDialogOpen ? 'Create' : 'Update'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success/Error Messages */}
      {success && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          padding: '12px 20px',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '8px',
          color: '#ffffff',
          fontSize: '0.9rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 1001,
          animation: 'slideIn 0.3s ease'
        }}>
          ✅ {success}
        </div>
      )}
      
      {error && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          padding: '12px 20px',
          background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
          borderRadius: '8px',
          color: '#ffffff',
          fontSize: '0.9rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 1001,
          animation: 'slideIn 0.3s ease'
        }}>
          ❌ {error}
        </div>
      )}

      <style jsx>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
        
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

export default AlertsModule