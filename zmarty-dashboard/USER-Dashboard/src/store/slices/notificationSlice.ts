import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface NotificationState {
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    title: string
    message: string
    timestamp: number
    read: boolean
    persistent: boolean
    actions?: Array<{
      label: string
      action: string
      variant?: 'primary' | 'secondary' | 'danger'
    }>
  }>
  settings: {
    enabled: boolean
    sound: boolean
    desktop: boolean
    email: boolean
    push: boolean
  }
  filters: {
    types: Array<'success' | 'error' | 'warning' | 'info'>
    unreadOnly: boolean
  }
}

const initialState: NotificationState = {
  notifications: [],
  settings: {
    enabled: true,
    sound: true,
    desktop: true,
    email: false,
    push: false
  },
  filters: {
    types: ['success', 'error', 'warning', 'info'],
    unreadOnly: false
  }
}

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<Omit<NotificationState['notifications'][0], 'id' | 'timestamp' | 'read'>>) => {
      const notification = {
        ...action.payload,
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        timestamp: Date.now(),
        read: false
      }
      state.notifications.unshift(notification)
      
      // Keep only the last 100 notifications
      if (state.notifications.length > 100) {
        state.notifications = state.notifications.slice(0, 100)
      }
    },
    markAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload)
      if (notification) {
        notification.read = true
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach(notification => {
        notification.read = true
      })
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload)
    },
    clearAllNotifications: (state) => {
      state.notifications = []
    },
    clearReadNotifications: (state) => {
      state.notifications = state.notifications.filter(n => !n.read)
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<NotificationState['settings']>>) => {
      state.settings = { ...state.settings, ...action.payload }
    },
    updateFilters: (state, action: PayloadAction<Partial<NotificationState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload }
    },
    executeNotificationAction: (state, action: PayloadAction<{ notificationId: string; action: string }>) => {
      const notification = state.notifications.find(n => n.id === action.payload.notificationId)
      if (notification && notification.actions) {
        const actionItem = notification.actions.find(a => a.action === action.payload.action)
        if (actionItem) {
          // Mark as read when action is executed
          notification.read = true
        }
      }
    }
  }
})

export const {
  addNotification,
  markAsRead,
  markAllAsRead,
  removeNotification,
  clearAllNotifications,
  clearReadNotifications,
  updateNotificationSettings,
  updateFilters,
  executeNotificationAction
} = notificationSlice.actions

export default notificationSlice.reducer
