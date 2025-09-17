import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
  activeTab: string
  modals: {
    settings: boolean
    trading: boolean
    notifications: boolean
  }
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    timestamp: number
    read: boolean
  }>
  loading: {
    marketData: boolean
    trading: boolean
    auth: boolean
  }
  viewport: {
    width: number
    height: number
    isMobile: boolean
  }
}

const initialState: UIState = {
  theme: 'dark',
  sidebarCollapsed: false,
  activeTab: 'dashboard',
  modals: {
    settings: false,
    trading: false,
    notifications: false
  },
  notifications: [],
  loading: {
    marketData: false,
    trading: false,
    auth: false
  },
  viewport: {
    width: window.innerWidth,
    height: window.innerHeight,
    isMobile: window.innerWidth < 768
  }
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<UIState['theme']>) => {
      state.theme = action.payload
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload
    },
    openModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = true
    },
    closeModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = false
    },
    closeAllModals: (state) => {
      Object.keys(state.modals).forEach(key => {
        state.modals[key as keyof UIState['modals']] = false
      })
    },
    addNotification: (state, action: PayloadAction<Omit<UIState['notifications'][0], 'id' | 'timestamp' | 'read'>>) => {
      const notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: Date.now(),
        read: false
      }
      state.notifications.unshift(notification)
    },
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload)
      if (notification) {
        notification.read = true
      }
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload)
    },
    clearAllNotifications: (state) => {
      state.notifications = []
    },
    setLoading: (state, action: PayloadAction<{ key: keyof UIState['loading']; value: boolean }>) => {
      state.loading[action.payload.key] = action.payload.value
    },
    updateViewport: (state, action: PayloadAction<{ width: number; height: number }>) => {
      state.viewport.width = action.payload.width
      state.viewport.height = action.payload.height
      state.viewport.isMobile = action.payload.width < 768
    }
  }
})

export const {
  setTheme,
  toggleSidebar,
  setActiveTab,
  openModal,
  closeModal,
  closeAllModals,
  addNotification,
  markNotificationAsRead,
  removeNotification,
  clearAllNotifications,
  setLoading,
  updateViewport
} = uiSlice.actions

export default uiSlice.reducer
