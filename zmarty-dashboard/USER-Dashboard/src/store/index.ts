import { configureStore } from '@reduxjs/toolkit'
import { 
  persistStore, 
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { combineReducers } from '@reduxjs/toolkit'

// Slices
import authSlice from './slices/authSlice'
import chatSlice from './slices/chatSlice'
import tradingSlice from './slices/tradingSlice'
import uiSlice from './slices/uiSlice'
import notificationSlice from './slices/notificationSlice'

// Root reducer
const rootReducer = combineReducers({
  auth: authSlice,
  chat: chatSlice,
  trading: tradingSlice,
  ui: uiSlice,
  notifications: notificationSlice,
})

// Persist configuration
const persistConfig = {
  key: 'zmarty-dashboard',
  storage,
  whitelist: ['auth', 'ui'], // Only persist auth and ui states
  blacklist: ['chat', 'trading', 'notifications'], // Don't persist real-time data
}

const persistedReducer = persistReducer(persistConfig, rootReducer)

// Store configuration
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
})

export const persistor = persistStore(store)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// Typed hooks
export { useAppDispatch, useAppSelector } from './hooks'