import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import SymbolsManager from './components/SymbolsManager'
import SymbolChart from './components/SymbolChart'
import Scoring from './components/Scoring'
import EnhancedAlertsDashboard from './components/EnhancedAlertsDashboard'
import EnhancedAlertsSystem from './components/EnhancedAlertsSystem'
import LiveAlertsPage from './components/LiveAlertsPage'
import LiveAlertsGuide from './components/LiveAlertsGuide'
import RealTimeLiveAlerts from './components/RealTimeLiveAlerts'
import Overview from './components/Overview'
import SubscriptionStatus from './components/SubscriptionStatus'
import './App.css'

// Roadmap Page Component
const RoadmapPage = () => {
  return (
    <div className="roadmap-page">
      <div className="page-header">
        <h2>🗺️ Development Roadmap</h2>
        <p>Future features and development plans for ZmartBot</p>
      </div>
      
      <div className="roadmap-content">
        <div className="roadmap-phase">
          <h3>🚀 Phase 1: Live Alerts (Current)</h3>
          <p>Real-time cross-signals and pattern detection</p>
          <ul>
            <li>21 Technical Indicators</li>
            <li>Cross-Signal Detection</li>
            <li>Real-time Updates</li>
            <li>Cooldown Management</li>
          </ul>
        </div>
        
        <div className="roadmap-phase">
          <h3>📊 Phase 2: Advanced Analytics</h3>
          <p>Machine learning and predictive modeling</p>
          <ul>
            <li>AI Pattern Recognition</li>
            <li>Predictive Scoring</li>
            <li>Risk Assessment</li>
            <li>Performance Analytics</li>
          </ul>
        </div>
        
        <div className="roadmap-phase">
          <h3>🤖 Phase 3: AI Trading</h3>
          <p>Automated trading with AI agents</p>
          <ul>
            <li>Automated Trading Bots</li>
            <li>Portfolio Management</li>
            <li>Risk Management</li>
            <li>Multi-Exchange Support</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Separate component to use useNavigate hook
function DashboardContent() {
  const [currentPage, setCurrentPage] = useState('symbols')
  const [currentTime, setCurrentTime] = useState(new Date())
  const [logoLoaded, setLogoLoaded] = useState(true)
  const navigate = useNavigate()

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const handleLogoClick = () => {
    console.log('🔘 Logo clicked!')
    setCurrentPage('symbols')
    navigate('/')
  }

  const handleLogoLoad = () => {
    console.log('✅ Logo loaded successfully')
    setLogoLoaded(true)
  }

  const handleLogoError = (e) => {
    console.error('❌ Logo failed to load:', e.target.src)
          // Try alternative logos
      if (e.target.src.includes('Zmart-Logo-New.jpg')) {
        e.target.src = '/logoZmart.png'
      } else if (e.target.src.includes('logoZmart.png')) {
        e.target.src = '/z-logo.png'
      } else {
        setLogoLoaded(false) // Show fallback
      }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <div className="header-brand">
                                    <img 
                        src="/Zmart-Logo-New.jpg" 
                        alt="Zmart Logo" 
                        className="logo"
                style={{ 
                  width: '60px', 
                  height: '60px', 
                  borderRadius: '12px',
                  cursor: 'pointer',
                  transition: 'transform 0.3s ease'
                }}
                onClick={handleLogoClick}
                onMouseEnter={(e) => e.target.style.transform = 'scale(1.1)'}
                onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                onLoad={handleLogoLoad}
                onError={handleLogoError}
              />
              <div className="header-title">
                <h1>Zmart Trading</h1>
                <p className="header-subtitle">Complete Dashboard</p>
              </div>
            </div>
          </div>
          <div className="header-right">
            <SubscriptionStatus showFull={false} />
            <div className="time-display">
              <div className="current-time">{currentTime.toLocaleTimeString()}</div>
              <div className="current-date">{currentTime.toLocaleDateString()}</div>
            </div>
          </div>
        </div>
      </header>
      
      <div className="dashboard-container">
        <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
        <div className="dashboard-main">
          <Routes>
            <Route path="/" element={<SymbolsManager />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/symbol-chart/:symbol" element={<SymbolChart />} />
  
            <Route path="/scoring" element={<Scoring />} />
            <Route path="/cryptometer" element={<Scoring />} />
            <Route path="/kingfisher" element={<Scoring />} />
            <Route path="/riskmetric" element={<Scoring />} />
            <Route path="/chart" element={<SymbolChart />} />
            <Route path="/enhanced-alerts" element={<RealTimeLiveAlerts />} />
            <Route path="/alerts" element={<EnhancedAlertsSystem />} />
            <Route path="/roadmap" element={<RoadmapPage />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <DashboardContent />
    </Router>
  )
}

export default App

