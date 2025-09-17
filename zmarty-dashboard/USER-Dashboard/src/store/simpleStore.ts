import { configureStore } from '@reduxjs/toolkit'

// Simple store without dependencies
export const store = configureStore({
  reducer: {
    // Simple reducer to avoid dependency issues
    app: (state = { initialized: true }, action: any) => state
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch