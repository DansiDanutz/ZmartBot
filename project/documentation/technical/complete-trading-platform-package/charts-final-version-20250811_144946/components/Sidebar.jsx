import React, { useState } from 'react'
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
  ChevronDown
} from 'lucide-react'

const Sidebar = ({ currentPage, setCurrentPage }) => {
  const [isScoringOpen, setScoringOpen] = useState(false)
  const [isScriptsOpen, setScriptsOpen] = useState(false)

  const navigationGroups = [
    {
      items: [
        { icon: Zap, label: 'Quick Trade', active: currentPage === 'quicktrade', page: 'quicktrade' },
        { icon: TrendingUp, label: 'Analytics', active: currentPage === 'analytics', page: 'analytics' },
        { icon: Grid3X3, label: 'Symbols', active: currentPage === 'symbols', page: 'symbols' }
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
        { icon: Code, label: 'API', active: currentPage === 'api', page: 'api' },
        { icon: BookOpen, label: 'Documentation', active: currentPage === 'documentation', page: 'documentation' },
        { icon: FileCode, label: 'Examples', active: currentPage === 'examples', page: 'examples' }
      ]
    },
    {
      items: [
        {
          icon: FileCode,
          label: 'Scripts',
          active: currentPage === 'scripts',
          page: 'scripts',
          hasSubmenu: true,
          submenu: [
            { label: 'DBI', page: 'dbi' }
          ]
        }
      ]
    }
  ]

  const handleNavClick = (page) => setCurrentPage(page)

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
                      } else if (item.page === 'scripts') {
                        setScriptsOpen((v) => !v)
                      }
                    }}
                  >
                    <Icon className="sidebar-icon" />
                    <span>{item.label}</span>
                    {(item.page === 'scoring' && isScoringOpen) || (item.page === 'scripts' && isScriptsOpen) ? (
                      <ChevronDown className="sidebar-chevron" />
                    ) : (
                      <ChevronRight className="sidebar-chevron" />
                    )}
                  </button>
                  {((item.page === 'scoring' && isScoringOpen) || (item.page === 'scripts' && isScriptsOpen)) && (
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


