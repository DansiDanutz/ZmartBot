import React, { useState } from 'react'
import { 
  Settings, 
  Eye, 
  Play, 
  Pause, 
  RotateCcw, 
  Activity,
  Globe,
  Server,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  Zap,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

const EnhancedModuleCard = ({ 
  title, 
  description, 
  icon: Icon, 
  status, 
  port, 
  apiPort, 
  metrics,
  onAction,
  isExpanded = false,
  onToggleExpand 
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const [actionLoading, setActionLoading] = useState(null)

  const handleAction = async (action) => {
    setActionLoading(action)
    await new Promise(resolve => setTimeout(resolve, 1500)) // Simulate API call
    setActionLoading(null)
    onAction?.(action)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'text-green-500'
      case 'offline': return 'text-red-500'
      case 'warning': return 'text-yellow-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return <CheckCircle className="w-4 h-4" />
      case 'offline': return <XCircle className="w-4 h-4" />
      case 'warning': return <AlertTriangle className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  return (
    <div
      className="relative group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Card className={`
        bg-card/50 backdrop-blur-xl border border-border/50 rounded-xl shadow-2xl 
        transition-all duration-300 relative overflow-hidden
        ${isHovered ? 'bg-card/70 border-primary/30 shadow-2xl shadow-primary/10 -translate-y-1' : ''}
        ${isExpanded ? 'ring-2 ring-primary/30' : ''}
      `}>
        {/* Animated background gradient */}
        <div className={`
          absolute inset-0 opacity-0 transition-opacity duration-300
          bg-gradient-to-br from-primary/5 to-primary/10
          ${isHovered ? 'opacity-100' : ''}
        `} />
        
        {/* Pulse effect for online status */}
        {status === 'online' && (
          <div className="absolute top-4 right-4">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
            <div className="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping opacity-30" />
          </div>
        )}

        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div 
                className={`p-3 rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-all duration-300 ${
                  isHovered ? 'scale-110 rotate-3' : ''
                }`}
              >
                <Icon className="w-6 h-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold text-foreground flex items-center space-x-2">
                  <span>{title}</span>
                  <Badge variant={status === 'online' ? 'default' : 'destructive'} className="text-xs">
                    {status.toUpperCase()}
                  </Badge>
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">{description}</p>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleExpand}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <div
                className={`transition-transform duration-200 ${
                  isExpanded ? 'rotate-180' : ''
                }`}
              >
                <ChevronDown className="w-4 h-4" />
              </div>
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Port Information */}
          <div className="grid grid-cols-2 gap-3">
            <div 
              className={`bg-gradient-to-br from-card/30 to-card/10 backdrop-blur-sm border border-border/30 rounded-lg p-3 transition-all duration-200 ${
                isHovered ? 'from-card/50 to-card/20 border-primary/20 scale-102' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">Frontend</span>
                <Globe className="w-3 h-3 text-muted-foreground" />
              </div>
              <p className="text-sm font-medium">:{port}</p>
            </div>
            
            <div 
              className={`bg-gradient-to-br from-card/30 to-card/10 backdrop-blur-sm border border-border/30 rounded-lg p-3 transition-all duration-200 ${
                isHovered ? 'from-card/50 to-card/20 border-primary/20 scale-102' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">API</span>
                <Server className="w-3 h-3 text-muted-foreground" />
              </div>
              <p className="text-sm font-medium">:{apiPort}</p>
            </div>
          </div>

          {/* Resource Usage */}
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">CPU Usage</span>
                <span className="text-sm font-medium">{metrics?.cpu || 0}%</span>
              </div>
              <Progress 
                value={metrics?.cpu || 0} 
                className="h-2"
              />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Memory</span>
                <span className="text-sm font-medium">{metrics?.memory || 0}%</span>
              </div>
              <Progress 
                value={metrics?.memory || 0} 
                className="h-2"
              />
            </div>
          </div>

          {/* Expanded Content */}
          {isExpanded && (
            <div className="space-y-4 border-t border-border/30 pt-4 animate-in slide-in-from-top-2 duration-300">
              {/* Additional Metrics */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Requests</span>
                  <span className="font-medium flex items-center space-x-1">
                    <TrendingUp className="w-3 h-3 text-green-500" />
                    <span>{metrics?.requests || 0}</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Uptime</span>
                  <span className="font-medium">99.8%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Response</span>
                  <span className="font-medium">45ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Errors</span>
                  <span className="font-medium text-green-500">0</span>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAction('restart')}
                  disabled={actionLoading === 'restart'}
                  className="flex-1"
                >
                  {actionLoading === 'restart' ? (
                    <div className="animate-spin">
                      <RotateCcw className="w-3 h-3" />
                    </div>
                  ) : (
                    <RotateCcw className="w-3 h-3" />
                  )}
                  <span className="ml-1">Restart</span>
                </Button>
                
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAction(status === 'online' ? 'stop' : 'start')}
                  disabled={actionLoading === 'toggle'}
                  className="flex-1"
                >
                  {actionLoading === 'toggle' ? (
                    <Zap className="w-3 h-3 animate-pulse" />
                  ) : status === 'online' ? (
                    <Pause className="w-3 h-3" />
                  ) : (
                    <Play className="w-3 h-3" />
                  )}
                  <span className="ml-1">{status === 'online' ? 'Stop' : 'Start'}</span>
                </Button>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center space-x-2 pt-2">
            <Button 
              size="sm" 
              variant="outline" 
              className="flex-1 h-8 px-3"
              onClick={() => handleAction('view')}
              disabled={actionLoading === 'view'}
            >
              <Eye className="w-3 h-3 mr-1" />
              View
            </Button>
            
            <Button 
              size="sm" 
              className={`flex-1 h-8 px-3 relative overflow-hidden bg-gradient-to-r from-primary to-primary/80 text-primary-foreground font-semibold transition-all duration-300 ${
                isHovered ? 'shadow-lg shadow-primary/50 -translate-y-0.5' : ''
              }`}
              onClick={() => handleAction('manage')}
              disabled={actionLoading === 'manage'}
            >
              {actionLoading === 'manage' ? (
                <div className="animate-spin">
                  <Settings className="w-3 h-3 mr-1" />
                </div>
              ) : (
                <Settings className="w-3 h-3 mr-1" />
              )}
              Manage
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default EnhancedModuleCard

