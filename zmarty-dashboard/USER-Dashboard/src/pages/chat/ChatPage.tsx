import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Mic, 
  MicOff, 
  Paperclip, 
  Smile, 
  MoreVertical,
  Bot,
  User,
  Zap,
  TrendingUp,
  Download,
  Copy,
  Volume2,
  VolumeX,
  RefreshCcw,
  Brain,
  Shield,
  AlertCircle,
  CheckCircle2,
  Activity,
  Settings
} from 'lucide-react'
import { useAppSelector } from '@store/hooks'
import { zmartyAI } from '@/services/zmartyAI'
import { automationOrchestrator } from '@/services/automationOrchestrator'
import { memoryAdapter } from '@/services/memoryAdapter'
import { supabaseService } from '@/services/supabaseEnhanced'

interface ChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  status: 'sending' | 'sent' | 'error'
  metadata?: {
    tradingSignals?: any[]
    marketData?: any
    analysis?: string
    kingfisher_powered?: boolean
    memory_enhanced?: boolean
    mcp_enhanced?: boolean
    automated?: boolean
    confidence?: number
    sources?: string[]
  }
}

interface SystemStatus {
  zmarty_ai: boolean
  kingfisher_ai: boolean
  automation: boolean
  memory: boolean
  mcp_services: boolean
}

const ChatPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    zmarty_ai: false,
    kingfisher_ai: false,
    automation: false,
    memory: false,
    mcp_services: false
  })
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  
  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  // Initialize Enhanced AI Services
  useEffect(() => {
    const initializeServices = async () => {
      console.log('🚀 Initializing Enhanced Zmarty AI with MCP Integration...')
      
      try {
        // Initialize system status checks
        const statusChecks = {
          zmarty_ai: true, // Always available
          kingfisher_ai: false,
          automation: false,
          memory: false,
          mcp_services: false
        }

        // Check KingFisher AI
        try {
          const healthCheck = await fetch('http://localhost:8098/health')
          statusChecks.kingfisher_ai = healthCheck.ok
        } catch (error) {
          console.warn('KingFisher AI not available:', error)
        }

        // Check automation orchestrator
        try {
          const automationStatus = automationOrchestrator.getAutomationStatus()
          statusChecks.automation = automationStatus.isRunning
        } catch (error) {
          console.warn('Automation orchestrator error:', error)
        }

        // Check memory adapter
        try {
          const memoryStats = memoryAdapter.getMemoryStatistics()
          statusChecks.memory = memoryStats.total_cached_memories >= 0
        } catch (error) {
          console.warn('Memory adapter error:', error)
        }

        // Check MCP services (Supabase)
        try {
          const supabaseHealth = await supabaseService.getSystemHealth()
          statusChecks.mcp_services = supabaseHealth.database_connected
        } catch (error) {
          console.warn('MCP services error:', error)
        }

        setSystemStatus(statusChecks)
        setIsConnected(Object.values(statusChecks).some(status => status))

        // Initialize welcome message
        if (messages.length === 0) {
          const welcomeMessage: ChatMessage = {
            id: 'welcome_msg',
            type: 'assistant',
            content: `🤖 Hello ${user?.fullName || user?.username}! I'm Zmarty, your enhanced AI trading assistant.\n\n🔥 **Now Powered By:**\n${statusChecks.kingfisher_ai ? '👑 KingFisher AI - Advanced liquidation analysis\n' : ''}${statusChecks.automation ? '🤖 Full Automation - Real-time market monitoring\n' : ''}${statusChecks.memory ? '🧠 Memory Adapter - Personalized learning\n' : ''}${statusChecks.mcp_services ? '🔗 MCP Services - Enhanced capabilities\n' : ''}\nI can provide comprehensive market analysis, intelligent trading tips, automated insights, and personalized advice based on your trading history. What can I help you with today?`,
            timestamp: new Date(),
            status: 'sent',
            metadata: {
              kingfisher_powered: statusChecks.kingfisher_ai,
              memory_enhanced: statusChecks.memory,
              mcp_enhanced: statusChecks.mcp_services,
              automated: statusChecks.automation,
              confidence: 95,
              sources: ['zmarty_ai', 'system_initialization']
            }
          }

          setMessages([welcomeMessage])
        }

        // Start automation if available
        if (statusChecks.automation) {
          try {
            await automationOrchestrator.startFullAutomation()
            console.log('✅ Automation orchestrator started')
          } catch (error) {
            console.warn('Failed to start automation:', error)
          }
        }

        console.log('✅ Enhanced Zmarty AI initialized successfully')
      } catch (error) {
        console.error('❌ Failed to initialize services:', error)
      }
    }

    initializeServices()
  }, [])
  
  const sendMessage = async () => {
    if (!inputMessage.trim() || !isConnected) return
    
    const messageId = Date.now().toString()
    const userMessage: ChatMessage = {
      id: messageId,
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
      status: 'sending'
    }
    
    setMessages(prev => [...prev, userMessage])
    const messageContent = inputMessage.trim()
    setInputMessage('')
    setIsTyping(true)
    
    try {
      // Extract symbol from message if present
      const symbolMatch = messageContent.match(/([A-Z]{3,6}(?:USDT|USD|BTC|ETH))/i)
      const symbol = symbolMatch ? symbolMatch[1].toUpperCase() : undefined
      
      // Use enhanced Zmarty AI
      const response = await zmartyAI.chat(
        user?.id || 'anonymous',
        sessionId,
        messageContent,
        symbol
      )
      
      // Update user message status
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, status: 'sent' as const }
            : msg
        )
      )
      
      // Add AI response
      const aiMessage: ChatMessage = {
        id: response.id,
        type: 'assistant',
        content: response.message,
        timestamp: new Date(response.timestamp),
        status: 'sent',
        metadata: {
          kingfisher_powered: response.kingfisher_powered,
          memory_enhanced: response.memory_enhanced,
          mcp_enhanced: response.mcp_enhanced,
          automated: response.automated,
          confidence: response.confidence,
          sources: response.sources,
          analysis: response.metadata?.analysis
        }
      }
      
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
      
    } catch (error) {
      console.error('Failed to get AI response:', error)
      
      // Update user message status to error
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, status: 'error' as const }
            : msg
        )
      )
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your message. Please try again or check if all services are running properly.',
        timestamp: new Date(),
        status: 'sent',
        metadata: {
          kingfisher_powered: false,
          memory_enhanced: false,
          mcp_enhanced: false,
          automated: false,
          confidence: 0,
          sources: ['error_handler']
        }
      }
      
      setMessages(prev => [...prev, errorMessage])
      setIsTyping(false)
    }
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }
  
  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // TODO: Implement voice recording functionality
  }
  
  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    // TODO: Add toast notification
  }
  
  const quickPrompts = [
    { text: 'Analyze BTCUSDT with KingFisher AI', icon: TrendingUp },
    { text: 'Current market overview', icon: Bot },
    { text: 'Show automated insights', icon: Brain },
    { text: 'My trading history', icon: Activity },
    { text: 'Risk assessment for ETHUSDT', icon: Shield },
    { text: 'Latest trading signals', icon: Send }
  ]
  
  return (
    <div className="flex flex-col h-full bg-secondary-900">
      {/* Chat Header */}
      <div className="bg-secondary-800 border-b border-secondary-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-secondary-800 ${
                isConnected ? 'bg-success-500' : 'bg-danger-500'
              }`} />
            </div>
            
            <div>
              <h1 className="text-lg font-semibold text-white flex items-center gap-2">
                Zmarty AI
                {systemStatus.kingfisher_ai && <span className="text-xs bg-primary-600 px-2 py-1 rounded">KF</span>}
                {systemStatus.automation && <span className="text-xs bg-success-600 px-2 py-1 rounded">AUTO</span>}
                {systemStatus.memory && <span className="text-xs bg-blue-600 px-2 py-1 rounded">MEM</span>}
              </h1>
              <div className="text-sm text-secondary-400 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success-500' : 'bg-danger-500'}`} />
                {isConnected ? (
                  <span>Enhanced AI • {Object.values(systemStatus).filter(Boolean).length}/5 services active</span>
                ) : (
                  <span>Initializing services...</span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-2 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-700 transition-colors"
            >
              {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>
            
            <button className="p-2 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-700 transition-colors">
              <MoreVertical className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3xl flex ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'user' ? 'bg-primary-600 ml-3' : 'bg-secondary-700 mr-3'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                
                {/* Message Bubble */}
                <div className={`group relative ${
                  message.type === 'user' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-secondary-800 border border-secondary-700 text-white'
                } rounded-2xl px-4 py-3 max-w-full`}>
                  
                  {/* AI Enhancement Badges */}
                  {message.type === 'assistant' && message.metadata && (
                    <div className="flex items-center gap-1 mb-2 flex-wrap">
                      {message.metadata.kingfisher_powered && (
                        <span className="inline-flex items-center gap-1 text-xs bg-primary-600/20 text-primary-300 px-2 py-1 rounded-full">
                          <Brain className="w-3 h-3" />
                          KingFisher AI
                        </span>
                      )}
                      {message.metadata.automated && (
                        <span className="inline-flex items-center gap-1 text-xs bg-success-600/20 text-success-300 px-2 py-1 rounded-full">
                          <Zap className="w-3 h-3" />
                          Automated
                        </span>
                      )}
                      {message.metadata.memory_enhanced && (
                        <span className="inline-flex items-center gap-1 text-xs bg-blue-600/20 text-blue-300 px-2 py-1 rounded-full">
                          <Activity className="w-3 h-3" />
                          Memory
                        </span>
                      )}
                      {message.metadata.mcp_enhanced && (
                        <span className="inline-flex items-center gap-1 text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded-full">
                          <Settings className="w-3 h-3" />
                          MCP
                        </span>
                      )}
                      {message.metadata.confidence && (
                        <span className="text-xs bg-secondary-700 text-secondary-300 px-2 py-1 rounded-full">
                          {message.metadata.confidence}% confidence
                        </span>
                      )}
                    </div>
                  )}
                  
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                  
                  {/* Sources Footer */}
                  {message.type === 'assistant' && message.metadata?.sources && (
                    <div className="mt-2 pt-2 border-t border-secondary-700">
                      <div className="text-xs text-secondary-400">
                        Sources: {message.metadata.sources.join(', ')}
                      </div>
                    </div>
                  )}
                  
                  {/* Message Status */}
                  {message.type === 'user' && (
                    <div className={`text-xs mt-1 ${
                      message.status === 'sending' ? 'text-primary-200' :
                      message.status === 'sent' ? 'text-primary-200' :
                      'text-danger-300'
                    }`}>
                      {message.status === 'sending' ? 'Sending...' :
                       message.status === 'sent' ? 'Sent' :
                       'Failed to send'}
                    </div>
                  )}
                  
                  {/* Message Actions */}
                  <div className="absolute top-full left-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-2">
                    <button
                      onClick={() => copyMessage(message.content)}
                      className="p-1 text-secondary-400 hover:text-white rounded bg-secondary-800 shadow-lg"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                    
                    {message.type === 'assistant' && (
                      <>
                        <button className="p-1 text-secondary-400 hover:text-white rounded bg-secondary-800 shadow-lg">
                          <Volume2 className="w-3 h-3" />
                        </button>
                        <button className="p-1 text-secondary-400 hover:text-white rounded bg-secondary-800 shadow-lg">
                          <Download className="w-3 h-3" />
                        </button>
                      </>
                    )}
                  </div>
                  
                  {/* Trading Data */}
                  {message.metadata?.tradingSignals && (
                    <div className="mt-3 p-3 bg-secondary-700 rounded-lg">
                      <h4 className="text-sm font-medium text-white mb-2">Trading Signals</h4>
                      {/* TODO: Render trading signals */}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex items-start space-x-3"
            >
              <div className="w-8 h-8 bg-secondary-700 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              
              <div className="bg-secondary-800 border border-secondary-700 rounded-2xl px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Quick Prompts */}
      <div className="p-4 border-t border-secondary-700 bg-secondary-800">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {quickPrompts.map((prompt, index) => {
            const Icon = prompt.icon
            return (
              <motion.button
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => setInputMessage(prompt.text)}
                className="flex items-center space-x-2 px-3 py-2 bg-secondary-700 hover:bg-secondary-600 text-secondary-300 hover:text-white rounded-lg transition-colors whitespace-nowrap"
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{prompt.text}</span>
              </motion.button>
            )
          })}
        </div>
      </div>
      
      {/* Message Input */}
      <div className="p-4 bg-secondary-800 border-t border-secondary-700">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Zmarty about trading, market analysis, or anything else..."
              disabled={!isConnected}
              className="w-full bg-secondary-700 border border-secondary-600 rounded-xl px-4 py-3 text-white placeholder-secondary-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none max-h-32"
              rows={1}
              style={{ minHeight: '48px' }}
            />
            
            <div className="absolute right-2 bottom-2 flex items-center space-x-1">
              <button
                onClick={() => {/* TODO: Attach file */}}
                className="p-1.5 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-600 transition-colors"
              >
                <Paperclip className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => {/* TODO: Add emoji */}}
                className="p-1.5 text-secondary-400 hover:text-white rounded-lg hover:bg-secondary-600 transition-colors"
              >
                <Smile className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-full transition-all ${
                isRecording 
                  ? 'bg-danger-600 text-white animate-pulse' 
                  : 'bg-secondary-700 text-secondary-300 hover:text-white hover:bg-secondary-600'
              }`}
            >
              {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
            
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || !isConnected}
              className="p-3 bg-primary-600 hover:bg-primary-700 disabled:bg-secondary-700 disabled:text-secondary-400 text-white rounded-full transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center space-x-2 text-xs text-secondary-400">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success-500' : 'bg-danger-500'}`} />
            <span>{isConnected ? 'Connected' : 'Reconnecting...'}</span>
          </div>
          
          <div className="text-xs text-secondary-400">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPage