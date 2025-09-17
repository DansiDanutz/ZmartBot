import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface TradingState {
  selectedSymbol: string
  position: {
    side: 'long' | 'short' | null
    size: number
    entryPrice: number
    currentPrice: number
    pnl: number
  } | null
  orders: Array<{
    id: string
    symbol: string
    side: 'buy' | 'sell'
    type: 'market' | 'limit' | 'stop'
    quantity: number
    price?: number
    status: 'pending' | 'filled' | 'cancelled'
    timestamp: number
  }>
  isTradingEnabled: boolean
  riskLevel: 'low' | 'medium' | 'high'
}

const initialState: TradingState = {
  selectedSymbol: 'BTCUSDT',
  position: null,
  orders: [],
  isTradingEnabled: false,
  riskLevel: 'medium'
}

const tradingSlice = createSlice({
  name: 'trading',
  initialState,
  reducers: {
    setSelectedSymbol: (state, action: PayloadAction<string>) => {
      state.selectedSymbol = action.payload
    },
    setPosition: (state, action: PayloadAction<TradingState['position']>) => {
      state.position = action.payload
    },
    addOrder: (state, action: PayloadAction<TradingState['orders'][0]>) => {
      state.orders.push(action.payload)
    },
    updateOrder: (state, action: PayloadAction<{ id: string; updates: Partial<TradingState['orders'][0]> }>) => {
      const order = state.orders.find(o => o.id === action.payload.id)
      if (order) {
        Object.assign(order, action.payload.updates)
      }
    },
    removeOrder: (state, action: PayloadAction<string>) => {
      state.orders = state.orders.filter(o => o.id !== action.payload)
    },
    setTradingEnabled: (state, action: PayloadAction<boolean>) => {
      state.isTradingEnabled = action.payload
    },
    setRiskLevel: (state, action: PayloadAction<TradingState['riskLevel']>) => {
      state.riskLevel = action.payload
    },
    clearTradingData: (state) => {
      state.position = null
      state.orders = []
    }
  }
})

export const {
  setSelectedSymbol,
  setPosition,
  addOrder,
  updateOrder,
  removeOrder,
  setTradingEnabled,
  setRiskLevel,
  clearTradingData
} = tradingSlice.actions

export default tradingSlice.reducer
