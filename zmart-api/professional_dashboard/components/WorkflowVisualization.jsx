import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowRight, 
  Database, 
  Brain, 
  Target, 
  Shield, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Activity,
  BarChart3,
  Settings
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const WorkflowVisualization = () => {
  const [activeFlow, setActiveFlow] = useState('signal')
  const [animationStep, setAnimationStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  const workflows = {
    signal: {
      title: 'Signal Processing Pipeline',
      description: 'Real-time market signal analysis and validation',
      color: 'from-blue-500 to-cyan-500',
      steps: [
        {
          id: 1,
          title: 'Market Data Ingestion',
          description: 'Real-time data from multiple sources',
          icon: Database,
          status: 'active',
          duration: '~50ms'
        },
        {
          id: 2,
          title: 'Pattern Recognition',
          description: 'KingFisher & Simulation Agent analysis',
          icon: Brain,
          status: 'processing',
          duration: '~200ms'
        },
        {
          id: 3,
          title: 'Signal Validation',
          description: 'ZmartBot technical confirmation',
          icon: CheckCircle,
          status: 'pending',
          duration: '~100ms'
        },
        {
          id: 4,
          title: 'Risk Assessment',
          description: 'Trade Strategy evaluation',
          icon: Shield,
          status: 'pending',
          duration: '~150ms'
        },
        {
          id: 5,
          title: 'Position Execution',
          description: 'Automated trade placement',
          icon: Target,
          status: 'pending',
          duration: '~300ms'
        }
      ]
    },
    risk: {
      title: 'Risk Management Flow',
      description: 'Dynamic position sizing and protection',
      color: 'from-orange-500 to-red-500',
      steps: [
        {
          id: 1,
          title: 'Position Monitoring',
          description: 'Real-time position tracking',
          icon: Activity,
          status: 'active',
          duration: 'Continuous'
        },
        {
          id: 2,
          title: 'Scaling Decisions',
          description: 'Dynamic position sizing',
          icon: BarChart3,
          status: 'active',
          duration: '~100ms'
        },
        {
          id: 3,
          title: 'Liquidation Alerts',
          description: 'Early warning system',
          icon: AlertTriangle,
          status: 'monitoring',
          duration: 'Real-time'
        },
        {
          id: 4,
          title: 'Profit Taking',
          description: 'Automated profit realization',
          icon: TrendingUp,
          status: 'ready',
          duration: '~50ms'
        },
        {
          id: 5,
          title: 'Loss Mitigation',
          description: 'Stop-loss execution',
          icon: Shield,
          status: 'standby',
          duration: '~25ms'
        }
      ]
    }
  }

  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setAnimationStep(prev => {
          const maxSteps = workflows[activeFlow].steps.length
          return prev >= maxSteps - 1 ? 0 : prev + 1
        })
      }, 1500)
      return () => clearInterval(interval)
    }
  }, [isPlaying, activeFlow])

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500 shadow-green-500/50'
      case 'processing': return 'bg-blue-500 shadow-blue-500/50'
      case 'pending': return 'bg-yellow-500 shadow-yellow-500/50'
      case 'monitoring': return 'bg-purple-500 shadow-purple-500/50'
      case 'ready': return 'bg-cyan-500 shadow-cyan-500/50'
      case 'standby': return 'bg-gray-500 shadow-gray-500/50'
      default: return 'bg-gray-400'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Zap className="w-3 h-3" />
      case 'processing': return <Settings className="w-3 h-3 animate-spin" />
      case 'pending': return <Clock className="w-3 h-3" />
      default: return <Activity className="w-3 h-3" />
    }
  }

  const currentWorkflow = workflows[activeFlow]

  return (
    <div className="space-y-6">
      {/* Workflow Selector */}
      <div className="flex items-center space-x-4">
        {Object.entries(workflows).map(([key, workflow]) => (
          <Button
            key={key}
            variant={activeFlow === key ? "default" : "outline"}
            onClick={() => {
              setActiveFlow(key)
              setAnimationStep(0)
            }}
            className={`relative overflow-hidden ${
              activeFlow === key 
                ? `bg-gradient-to-r ${workflow.color} text-white` 
                : ''
            }`}
          >
            {workflow.title}
          </Button>
        ))}
        
        <Button
          variant="outline"
          onClick={() => setIsPlaying(!isPlaying)}
          className="ml-auto"
        >
          {isPlaying ? 'Pause' : 'Play'} Animation
        </Button>
      </div>

      {/* Workflow Visualization */}
      <Card className="bg-card/50 backdrop-blur-xl border border-border/50 rounded-xl p-6 shadow-2xl">
        <CardHeader>
          <CardTitle className={`text-xl font-bold bg-gradient-to-r ${currentWorkflow.color} bg-clip-text text-transparent`}>
            {currentWorkflow.title}
          </CardTitle>
          <p className="text-muted-foreground">{currentWorkflow.description}</p>
        </CardHeader>
        
        <CardContent>
          <div className="relative">
            {/* Flow Steps */}
            <div className="flex items-center justify-between space-x-4 overflow-x-auto pb-4">
              {currentWorkflow.steps.map((step, index) => (
                <div key={step.id} className="flex items-center space-x-4 min-w-0">
                  {/* Step Card */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ 
                      opacity: 1, 
                      scale: animationStep >= index ? 1.05 : 1,
                      y: animationStep === index ? -5 : 0
                    }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className={`
                      relative bg-gradient-to-br from-card/30 to-card/10 backdrop-blur-sm 
                      border border-border/30 rounded-lg p-4 min-w-[200px] transition-all duration-300
                      ${animationStep >= index ? 'border-primary/30 shadow-lg shadow-primary/10' : ''}
                    `}
                  >
                    {/* Status Indicator */}
                    <div className="flex items-center justify-between mb-3">
                      <div className={`w-3 h-3 rounded-full animate-pulse ${getStatusColor(step.status)}`} />
                      <Badge variant="secondary" className="text-xs">
                        {getStatusIcon(step.status)}
                        <span className="ml-1">{step.status.toUpperCase()}</span>
                      </Badge>
                    </div>

                    {/* Step Icon */}
                    <motion.div
                      className="flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 mb-3 mx-auto"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      animate={animationStep === index ? { 
                        scale: [1, 1.1, 1], 
                        rotate: [0, 5, 0] 
                      } : {}}
                      transition={{ duration: 0.5 }}
                    >
                      <step.icon className="w-6 h-6 text-primary" />
                    </motion.div>

                    {/* Step Info */}
                    <div className="text-center">
                      <h4 className="font-semibold text-sm mb-1">{step.title}</h4>
                      <p className="text-xs text-muted-foreground mb-2">{step.description}</p>
                      <Badge variant="outline" className="text-xs">
                        {step.duration}
                      </Badge>
                    </div>

                    {/* Active Step Glow */}
                    {animationStep === index && (
                      <motion.div
                        className="absolute inset-0 rounded-lg bg-gradient-to-r from-primary/20 to-primary/10 -z-10"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: [0, 1, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      />
                    )}
                  </motion.div>

                  {/* Arrow Connector */}
                  {index < currentWorkflow.steps.length - 1 && (
                    <motion.div
                      className="flex items-center"
                      animate={animationStep > index ? {
                        scale: [1, 1.2, 1],
                        opacity: [0.5, 1, 0.5]
                      } : {}}
                      transition={{ duration: 0.5 }}
                    >
                      <ArrowRight className={`w-6 h-6 ${
                        animationStep > index ? 'text-primary' : 'text-muted-foreground'
                      } transition-colors duration-300`} />
                    </motion.div>
                  )}
                </div>
              ))}
            </div>

            {/* Progress Bar */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Workflow Progress</span>
                <span className="text-sm font-medium">
                  {Math.round(((animationStep + 1) / currentWorkflow.steps.length) * 100)}%
                </span>
              </div>
              <div className="w-full bg-muted/20 rounded-full h-2 overflow-hidden">
                <motion.div
                  className={`h-full bg-gradient-to-r ${currentWorkflow.color} rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ 
                    width: `${((animationStep + 1) / currentWorkflow.steps.length) * 100}%` 
                  }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            {/* Real-time Stats */}
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="text-center p-3 rounded-lg bg-muted/10">
                <div className="text-lg font-bold text-primary">
                  {activeFlow === 'signal' ? '847ms' : '1.2s'}
                </div>
                <div className="text-xs text-muted-foreground">Avg Processing Time</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/10">
                <div className="text-lg font-bold text-green-500">
                  {activeFlow === 'signal' ? '98.7%' : '99.2%'}
                </div>
                <div className="text-xs text-muted-foreground">Success Rate</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/10">
                <div className="text-lg font-bold text-blue-500">
                  {activeFlow === 'signal' ? '1,247' : '892'}
                </div>
                <div className="text-xs text-muted-foreground">Daily Executions</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default WorkflowVisualization

