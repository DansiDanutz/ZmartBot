import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Zap,
  TrendingUp,
  Grid3X3,
  Target,
  Vault,
  Users,
  History,
  Globe,
  FileText,
  Code,
  BookOpen,
  FileCode,
  ChevronRight,
  ChevronDown,
  Bell,
  BarChart3,
  Eye
} from 'lucide-react'

const Sidebar = ({ currentPage, setCurrentPage }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [isScoringOpen, setScoringOpen] = useState(false)

  const navigationGroups = [
    {
      items: [
        { icon: Eye, label: 'Overview', active: currentPage === 'overview', page: 'overview' },
        { icon: Zap, label: 'Quick Trade', active: currentPage === 'quicktrade', page: 'quicktrade' },
        { icon: TrendingUp, label: 'Analytics', active: currentPage === 'analytics', page: 'analytics' },
        { icon: Grid3X3, label: 'Symbols', active: currentPage === 'symbols', page: 'symbols' },
        { icon: BarChart3, label: 'Chart', active: currentPage === 'chart', page: 'chart' },
        { icon: Bell, label: 'Enhanced Alerts', active: currentPage === 'enhanced-alerts', page: 'enhanced-alerts' },
        { icon: Bell, label: 'Alerts', active: currentPage === 'alerts', page: 'alerts' }
      ]
    },
    {
      items: [
        {
          icon: Target,
          label: 'Scoring',
          active: currentPage === 'scoring',
          page: 'scoring',
          hasSubmenu: true,
          submenu: [
            { label: 'Cryptometer', page: 'cryptometer' },
            { label: 'KingFisher', page: 'kingfisher' },
            { label: 'RiskMetric', page: 'riskmetric' }
          ]
        }
      ]
    },
    {
      items: [
        { icon: Vault, label: 'Vaults', active: currentPage === 'vaults', page: 'vaults' },
        { icon: Users, label: 'Investors', active: currentPage === 'investors', page: 'investors' },
        { icon: History, label: 'History', active: currentPage === 'history', page: 'history' }
      ]
    },
    {
      items: [
        { icon: Globe, label: 'Website', active: currentPage === 'website', page: 'website' },
        { icon: FileText, label: 'Blog', active: currentPage === 'blog', page: 'blog' }
      ]
    },
    {
      items: [
        { icon: BookOpen, label: 'Documentation', active: currentPage === 'documentation', page: 'documentation' },
        { icon: FileCode, label: 'Examples', active: currentPage === 'examples', page: 'examples' }
      ]
    }
  ]

  const handleNavClick = (page) => {
    setCurrentPage(page)
    if (page === 'symbols') {
      navigate('/')
    } else if (page === 'overview') {
      navigate('/overview')
    } else if (page === 'scoring') {
      navigate('/scoring')
    } else if (page === 'cryptometer') {
      navigate('/cryptometer')
    } else if (page === 'kingfisher') {
      navigate('/kingfisher')
    } else if (page === 'riskmetric') {
      navigate('/riskmetric')
    } else if (page === 'chart') {
      navigate('/chart')
    } else if (page === 'enhanced-alerts') {
      navigate('/enhanced-alerts')
    } else if (page === 'alerts') {
      navigate('/alerts')
    } else {
      navigate(`/${page}`)
    }
  }

  return (
    <aside className="sidebar">
      {navigationGroups.map((group, gi) => (
        <div className="sidebar-group" key={gi}>
          {group.items.map((item, ii) => {
            const Icon = item.icon
            if (item.hasSubmenu) {
              return (
                <div className="sidebar-item" key={`${gi}-${ii}`}>
                  <button
                    className={`sidebar-link ${item.active ? 'active' : ''}`}
                    onClick={() => {
                      handleNavClick(item.page)
                      if (item.page === 'scoring') {
                        setScoringOpen((v) => !v)
                      }
                    }}
                  >
                    <Icon className="sidebar-icon" />
                    <span>{item.label}</span>
                    {item.page === 'scoring' && isScoringOpen ? (
                      <ChevronDown className="sidebar-chevron" />
                    ) : (
                      <ChevronRight className="sidebar-chevron" />
                    )}
                  </button>
                  {(item.page === 'scoring' && isScoringOpen) && (
                    <div className="sidebar-submenu">
                      {item.submenu.map((sub) => (
                        <button
                          key={sub.page}
                          className={`sidebar-sublink ${currentPage === sub.page ? 'active' : ''}`}
                          onClick={() => handleNavClick(sub.page)}
                        >
                          {sub.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )
            }

            return (
              <button
                key={`${gi}-${ii}`}
                className={`sidebar-link ${item.active ? 'active' : ''}`}
                onClick={() => handleNavClick(item.page)}
              >
                <Icon className="sidebar-icon" />
                <span>{item.label}</span>
              </button>
            )
          })}
        </div>
      ))}
    </aside>
  )
}

export default Sidebar


