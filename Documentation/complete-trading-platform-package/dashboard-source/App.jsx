import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  BarChart3, 
  Brain, 
  Database, 
  Eye, 
  Globe, 
  Layers, 
  LineChart, 
  Server, 
  Settings, 
  Target, 
  Terminal, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Zap,
  DollarSign,
  Shield,
  Clock,
  Wifi,
  CheckCircle,
  AlertTriangle,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import './App.css'

function App() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedModule, setExpandedModule] = useState(null)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const moduleStates = {
    zmartBot: {
      status: 'online',
      cpu: 45,
      memory: 62,
      requests: 1247,
      port: 3000,
      apiPort: 8000,
      icon: Database,
      title: 'ZmartBot',
      description: 'Core Trading Platform'
    },
    kingFisher: {
      status: 'online',
      cpu: 38,
      memory: 54,
      requests: 892,
      port: 3100,
      apiPort: 8100,
      icon: Target,
      title: 'KingFisher',
      description: 'Market Analysis & Liquidation Data'
    },
    tradeStrategy: {
      status: 'online',
      cpu: 52,
      memory: 71,
      requests: 634,
      port: 3200,
      apiPort: 8200,
      icon: Shield,
      title: 'Trade Strategy',
      description: 'Position Scaling & Risk Management'
    },
    simulationAgent: {
      status: 'online',
      cpu: 29,
      memory: 43,
      requests: 456,
      port: 3300,
      apiPort: 8300,
      icon: Brain,
      title: 'Simulation Agent',
      description: 'Pattern Analysis & Win Ratio Simulation'
    }
  }

  const MetricCard = ({ title, value, change, icon: Icon, trend }) => (
    <div className="metric-card group">
      <div className="metric-header">
        <Icon className="metric-icon" />
        <span className={`metric-badge ${trend === 'up' ? 'trend-up' : trend === 'down' ? 'trend-down' : 'trend-stable'}`}>
          {change}
        </span>
      </div>
      <div className="metric-content">
        <p className="metric-value">{value}</p>
        <p className="metric-title">{title}</p>
      </div>
    </div>
  )

  const ModuleCard = ({ moduleKey, module }) => {
    const Icon = module.icon
    const isExpanded = expandedModule === moduleKey
    
    return (
      <div className={`module-card ${isExpanded ? 'expanded' : ''}`}>
        <div className="module-header">
          <div className="module-info">
            <div className="module-icon-wrapper">
              <Icon className="module-icon" />
            </div>
            <div>
              <h3 className="module-title">{module.title}</h3>
              <p className="module-description">{module.description}</p>
            </div>
          </div>
          <div className="module-status">
            <div className={`status-dot ${module.status}`}></div>
            <span className={`status-badge ${module.status}`}>
              {module.status.toUpperCase()}
            </span>
          </div>
        </div>
        
        <div className="module-ports">
          <div className="port-info">
            <div className="port-label">
              <span>Frontend</span>
              <Globe className="port-icon" />
            </div>
            <p className="port-value">:{module.port}</p>
          </div>
          <div className="port-info">
            <div className="port-label">
              <span>API</span>
              <Server className="port-icon" />
            </div>
            <p className="port-value">:{module.apiPort}</p>
          </div>
        </div>

        <div className="module-metrics">
          <div className="metric-row">
            <span className="metric-label">CPU Usage</span>
            <span className="metric-value-small">{module.cpu}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${module.cpu}%` }}></div>
          </div>
          
          <div className="metric-row">
            <span className="metric-label">Memory</span>
            <span className="metric-value-small">{module.memory}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${module.memory}%` }}></div>
          </div>
        </div>

        <div className="module-requests">
          <TrendingUp className="requests-icon" />
          <span>{module.requests} requests</span>
        </div>

        {isExpanded && (
          <div className="module-expanded">
            <div className="expanded-metrics">
              <div className="expanded-metric">
                <span>Uptime</span>
                <span>99.8%</span>
              </div>
              <div className="expanded-metric">
                <span>Response</span>
                <span>45ms</span>
              </div>
              <div className="expanded-metric">
                <span>Errors</span>
                <span className="text-green">0</span>
              </div>
            </div>
            <div className="expanded-actions">
              <button className="action-btn secondary">
                <RotateCcw className="btn-icon" />
                Restart
              </button>
              <button className="action-btn secondary">
                <Pause className="btn-icon" />
                Stop
              </button>
            </div>
          </div>
        )}

        <div className="module-actions">
          <button className="action-btn secondary">
            <Eye className="btn-icon" />
            View
          </button>
          <button 
            className="action-btn primary"
            onClick={() => setExpandedModule(isExpanded ? null : moduleKey)}
          >
            <Settings className="btn-icon" />
            {isExpanded ? 'Collapse' : 'Manage'}
          </button>
        </div>
      </div>
    )
  }

  const WorkflowStep = ({ step, index, isActive }) => (
    <div className={`workflow-step ${isActive ? 'active' : ''}`}>
      <div className="step-number">{index + 1}</div>
      <div className="step-content">
        <h4 className="step-title">{step.title}</h4>
        <p className="step-description">{step.description}</p>
        <span className="step-duration">{step.duration}</span>
      </div>
      {step.active && <div className="step-indicator"></div>}
    </div>
  )

  const signalWorkflow = [
    { title: 'Market Data Ingestion', description: 'Real-time data from multiple sources', active: true, duration: '~50ms' },
    { title: 'Pattern Recognition', description: 'KingFisher & Simulation Agent analysis', active: true, duration: '~200ms' },
    { title: 'Signal Validation', description: 'ZmartBot technical confirmation', active: false, duration: '~100ms' },
    { title: 'Risk Assessment', description: 'Trade Strategy evaluation', active: false, duration: '~150ms' },
    { title: 'Position Execution', description: 'Automated trade placement', active: false, duration: '~300ms' }
  ]

  const riskWorkflow = [
    { title: 'Position Monitoring', description: 'Real-time position tracking', active: true, duration: 'Continuous' },
    { title: 'Scaling Decisions', description: 'Dynamic position sizing', active: true, duration: '~100ms' },
    { title: 'Liquidation Alerts', description: 'Early warning system', active: false, duration: 'Real-time' },
    { title: 'Profit Taking', description: 'Automated profit realization', active: false, duration: '~50ms' },
    { title: 'Loss Mitigation', description: 'Stop-loss execution', active: false, duration: '~25ms' }
  ]

  const systemLogs = [
    { time: '14:32:15', module: 'ZmartBot', message: 'New signal generated for BTCUSDT', type: 'info' },
    { time: '14:31:42', module: 'Trade Strategy', message: 'Position scaled successfully', type: 'success' },
    { time: '14:30:18', module: 'KingFisher', message: 'Liquidation cluster detected', type: 'info' },
    { time: '14:29:55', module: 'Simulation Agent', message: 'Pattern analysis completed', type: 'info' },
    { time: '14:28:33', module: 'System', message: 'High memory usage detected', type: 'warning' },
    { time: '14:27:21', module: 'ZmartBot', message: 'Trade executed successfully', type: 'success' }
  ]

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <Activity className="logo-icon" />
            </div>
            <div className="header-info">
              <h1 className="header-title">Trading Platform Pro</h1>
              <p className="header-subtitle">Complete System Dashboard</p>
            </div>
          </div>
          
          <div className="header-right">
            <div className="time-display">
              <div className="current-time">
                {currentTime.toLocaleTimeString()}
              </div>
              <div className="current-date">
                {currentTime.toLocaleDateString()}
              </div>
            </div>
            
            <button className="header-btn danger">
              Stop All
            </button>
            
            <button className="header-btn secondary">
              <Settings className="btn-icon" />
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-tabs">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'modules', label: 'Modules', icon: Database, badge: '4' },
            { id: 'workflows', label: 'Workflows', icon: Layers, badge: '5' },
            { id: 'analytics', label: 'Analytics', icon: BarChart3, badge: '6' },
            { id: 'monitoring', label: 'Monitoring', icon: Terminal, badge: '7' }
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon className="nav-icon" />
                <span>{tab.label}</span>
                {tab.badge && <span className="nav-badge">{tab.badge}</span>}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="tab-content">
            {/* Key Metrics */}
            <div className="metrics-grid">
              <MetricCard
                title="Total Profit"
                value="$12,847"
                change="+15.3%"
                icon={DollarSign}
                trend="up"
              />
              <MetricCard
                title="Active Trades"
                value="24"
                change="+3"
                icon={TrendingUp}
                trend="up"
              />
              <MetricCard
                title="Win Rate"
                value="78.5%"
                change="+2.1%"
                icon={Target}
                trend="up"
              />
              <MetricCard
                title="System Uptime"
                value="99.8%"
                change="24h"
                icon={Clock}
                trend="stable"
              />
            </div>

            {/* System Health */}
            <div className="system-health">
              <div className="section-header">
                <Activity className="section-icon" />
                <h2>System Health</h2>
                <p>Real-time status of all trading modules</p>
              </div>
              <div className="health-grid">
                {Object.entries(moduleStates).map(([key, module]) => (
                  <div key={key} className="health-item">
                    <div className={`health-dot ${module.status}`}></div>
                    <div className="health-info">
                      <p className="health-name">{module.title}</p>
                      <p className="health-stats">CPU: {module.cpu}% | RAM: {module.memory}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance Chart Placeholder */}
            <div className="performance-chart">
              <div className="section-header">
                <LineChart className="section-icon" />
                <h2>Performance Overview</h2>
                <p>24-hour system performance metrics</p>
              </div>
              <div className="chart-placeholder">
                <div className="chart-bars">
                  {[85, 92, 78, 88, 95, 87, 91, 83, 89, 94, 86, 90].map((height, index) => (
                    <div 
                      key={index} 
                      className="chart-bar" 
                      style={{ height: `${height}%` }}
                    ></div>
                  ))}
                </div>
                <div className="chart-labels">
                  <span>00:00</span>
                  <span>04:00</span>
                  <span>08:00</span>
                  <span>12:00</span>
                  <span>16:00</span>
                  <span>20:00</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modules Tab */}
        {activeTab === 'modules' && (
          <div className="tab-content">
            <div className="modules-grid">
              {Object.entries(moduleStates).map(([key, module]) => (
                <ModuleCard key={key} moduleKey={key} module={module} />
              ))}
            </div>
          </div>
        )}

        {/* Workflows Tab */}
        {activeTab === 'workflows' && (
          <div className="tab-content">
            <div className="workflows-container">
              <div className="workflow-section">
                <div className="workflow-header">
                  <h3>Signal Processing Pipeline</h3>
                  <p>Real-time market signal analysis and validation</p>
                </div>
                <div className="workflow-steps">
                  {signalWorkflow.map((step, index) => (
                    <WorkflowStep key={index} step={step} index={index} isActive={step.active} />
                  ))}
                </div>
              </div>
              
              <div className="workflow-section">
                <div className="workflow-header">
                  <h3>Risk Management Flow</h3>
                  <p>Dynamic position sizing and protection</p>
                </div>
                <div className="workflow-steps">
                  {riskWorkflow.map((step, index) => (
                    <WorkflowStep key={index} step={step} index={index} isActive={step.active} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="tab-content">
            <div className="analytics-grid">
              <div className="analytics-card">
                <div className="section-header">
                  <h3>Trading Performance</h3>
                  <p>Profit and loss by trading pair</p>
                </div>
                <div className="trading-pairs">
                  {[
                    { symbol: 'BTCUSDT', profit: 2450, change: '+12.5%' },
                    { symbol: 'ETHUSDT', profit: 1890, change: '+8.7%' },
                    { symbol: 'ADAUSDT', profit: 1240, change: '+15.2%' },
                    { symbol: 'DOTUSDT', profit: 980, change: '+6.3%' }
                  ].map(pair => (
                    <div key={pair.symbol} className="trading-pair">
                      <span className="pair-symbol">{pair.symbol}</span>
                      <span className="pair-profit">${pair.profit}</span>
                      <span className="pair-change positive">{pair.change}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="analytics-card">
                <div className="section-header">
                  <h3>Module Distribution</h3>
                  <p>Resource usage by module</p>
                </div>
                <div className="distribution-chart">
                  {[
                    { name: 'ZmartBot', value: 35, color: '#8b5cf6' },
                    { name: 'KingFisher', value: 25, color: '#06b6d4' },
                    { name: 'Trade Strategy', value: 25, color: '#10b981' },
                    { name: 'Simulation Agent', value: 15, color: '#f59e0b' }
                  ].map(item => (
                    <div key={item.name} className="distribution-item">
                      <div 
                        className="distribution-bar" 
                        style={{ 
                          width: `${item.value}%`, 
                          backgroundColor: item.color 
                        }}
                      ></div>
                      <span className="distribution-label">{item.name}</span>
                      <span className="distribution-value">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Monitoring Tab */}
        {activeTab === 'monitoring' && (
          <div className="tab-content">
            <div className="monitoring-metrics">
              <MetricCard
                title="CPU Usage"
                value="42%"
                change="Normal"
                icon={Activity}
                trend="stable"
              />
              <MetricCard
                title="Memory Usage"
                value="68%"
                change="12.8GB"
                icon={Database}
                trend="up"
              />
              <MetricCard
                title="Network I/O"
                value="1.2GB"
                change="+5.3%"
                icon={Wifi}
                trend="up"
              />
            </div>

            <div className="system-logs">
              <div className="section-header">
                <Terminal className="section-icon" />
                <h2>System Logs</h2>
                <p>Recent system activity and alerts</p>
              </div>
              <div className="logs-container">
                {systemLogs.map((log, index) => (
                  <div key={index} className="log-entry">
                    <div className={`log-dot ${log.type}`}></div>
                    <span className="log-time">{log.time}</span>
                    <span className="log-module">{log.module}</span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

