import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import SymbolsManager from './components/SymbolsManager'
import SymbolChart from './components/SymbolChart'
import Scoring from './components/Scoring'
import EnhancedAlertsCard from './components/EnhancedAlertsCard'
import EnhancedAlertsSystem from './components/EnhancedAlertsSystem'
import Overview from './components/Overview'
import './App.css'

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
            <Route path="/enhanced-alerts" element={<EnhancedAlertsCard />} />
            <Route path="/alerts" element={<EnhancedAlertsSystem />} />
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

