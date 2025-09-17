import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  type?: 'analysis' | 'recommendation' | 'alert' | 'general' | 'automated_insight'
  symbol?: string
  confidence?: number
  sources?: string[]
  automated?: boolean
  memory_enhanced?: boolean
  kingfisher_powered?: boolean
  mcp_enhanced?: boolean
  metadata?: any
}

export interface ChatSession {
  id: string
  userId: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
  symbol?: string
}

interface ChatState {
  sessions: ChatSession[]
  activeSessionId: string | null
  isLoading: boolean
  isTyping: boolean
  error: string | null
  quickPrompts: string[]
  systemStatus: {
    connected_services: number
    total_services: number
    availability_percentage: number
    last_check: string
  } | null
}

const initialState: ChatState = {
  sessions: [],
  activeSessionId: null,
  isLoading: false,
  isTyping: false,
  error: null,
  quickPrompts: [
    "What's the current market sentiment?",
    "Show me BTC analysis",
    "Any arbitrage opportunities?",
    "Portfolio recommendations",
    "System status check"
  ],
  systemStatus: null
}

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    createSession: (state, action: PayloadAction<{ userId: string; symbol?: string }>) => {
      const newSession: ChatSession = {
        id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        userId: action.payload.userId,
        title: action.payload.symbol ? `${action.payload.symbol} Analysis` : 'New Chat',
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        symbol: action.payload.symbol
      }
      state.sessions.unshift(newSession)
      state.activeSessionId = newSession.id
    },

    setActiveSession: (state, action: PayloadAction<string>) => {
      state.activeSessionId = action.payload
    },

    addMessage: (state, action: PayloadAction<{ sessionId: string; message: ChatMessage }>) => {
      const session = state.sessions.find(s => s.id === action.payload.sessionId)
      if (session) {
        session.messages.push(action.payload.message)
        session.updatedAt = new Date().toISOString()
        
        // Update title based on first user message if it's still "New Chat"
        if (session.title === 'New Chat' && action.payload.message.role === 'user') {
          session.title = action.payload.message.content.slice(0, 50) + (action.payload.message.content.length > 50 ? '...' : '')
        }
      }
    },

    updateMessage: (state, action: PayloadAction<{ sessionId: string; messageId: string; updates: Partial<ChatMessage> }>) => {
      const session = state.sessions.find(s => s.id === action.payload.sessionId)
      if (session) {
        const message = session.messages.find(m => m.id === action.payload.messageId)
        if (message) {
          Object.assign(message, action.payload.updates)
          session.updatedAt = new Date().toISOString()
        }
      }
    },

    deleteSession: (state, action: PayloadAction<string>) => {
      state.sessions = state.sessions.filter(s => s.id !== action.payload)
      if (state.activeSessionId === action.payload) {
        state.activeSessionId = state.sessions.length > 0 ? state.sessions[0].id : null
      }
    },

    clearAllSessions: (state) => {
      state.sessions = []
      state.activeSessionId = null
    },

    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },

    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload
    },

    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },

    updateQuickPrompts: (state, action: PayloadAction<string[]>) => {
      state.quickPrompts = action.payload
    },

    setSystemStatus: (state, action: PayloadAction<ChatState['systemStatus']>) => {
      state.systemStatus = action.payload
    },

    // Advanced actions for Zmarty AI integration
    addAutomatedInsight: (state, action: PayloadAction<{ sessionId: string; insight: any }>) => {
      const session = state.sessions.find(s => s.id === action.payload.sessionId)
      if (session) {
        const message: ChatMessage = {
          id: `insight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: action.payload.insight.description,
          timestamp: new Date().toISOString(),
          type: 'automated_insight',
          symbol: action.payload.insight.symbol,
          confidence: action.payload.insight.confidence,
          sources: ['kingfisher_ai', 'automated_analysis'],
          automated: true,
          kingfisher_powered: true,
          mcp_enhanced: true,
          metadata: action.payload.insight
        }
        session.messages.push(message)
        session.updatedAt = new Date().toISOString()
      }
    },

    updateSessionSymbol: (state, action: PayloadAction<{ sessionId: string; symbol: string }>) => {
      const session = state.sessions.find(s => s.id === action.payload.sessionId)
      if (session) {
        session.symbol = action.payload.symbol
        session.updatedAt = new Date().toISOString()
      }
    },

    markMessagesAsRead: (state, action: PayloadAction<string>) => {
      const session = state.sessions.find(s => s.id === action.payload)
      if (session) {
        // Implementation for marking messages as read
        session.updatedAt = new Date().toISOString()
      }
    }
  }
})

export const {
  createSession,
  setActiveSession,
  addMessage,
  updateMessage,
  deleteSession,
  clearAllSessions,
  setLoading,
  setTyping,
  setError,
  updateQuickPrompts,
  setSystemStatus,
  addAutomatedInsight,
  updateSessionSymbol,
  markMessagesAsRead
} = chatSlice.actions

// Selectors
export const selectAllSessions = (state: { chat: ChatState }) => state.chat.sessions
export const selectActiveSession = (state: { chat: ChatState }) => {
  return state.chat.sessions.find(s => s.id === state.chat.activeSessionId) || null
}
export const selectActiveSessionMessages = (state: { chat: ChatState }) => {
  const activeSession = selectActiveSession(state)
  return activeSession?.messages || []
}
export const selectChatLoading = (state: { chat: ChatState }) => state.chat.isLoading
export const selectChatTyping = (state: { chat: ChatState }) => state.chat.isTyping
export const selectChatError = (state: { chat: ChatState }) => state.chat.error
export const selectQuickPrompts = (state: { chat: ChatState }) => state.chat.quickPrompts
export const selectSystemStatus = (state: { chat: ChatState }) => state.chat.systemStatus

export default chatSlice.reducer