import { useState, useEffect, useCallback } from 'react'
import { useAppSelector } from '@store/hooks'
import { 
  tradingSignalsService, 
  marketDataService, 
  userPositionsService,
  type TradingSignal,
  type MarketData,
  type UserPosition 
} from '@/services/supabase'

interface TradingStats {
  activeSignals: number
  winRate: string
  totalPnL: string
  totalTrades: number
}

interface UseTradingReturn {
  signals: TradingSignal[]
  marketData: MarketData[]
  positions: UserPosition[]
  stats: TradingStats
  loading: boolean
  error: string | null
  refreshSignals: () => Promise<void>
  refreshMarketData: () => Promise<void>
  refreshPositions: () => Promise<void>
  createSignal: (signal: Omit<TradingSignal, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => Promise<void>
  updateSignal: (id: string, updates: Partial<TradingSignal>) => Promise<void>
}

export const useTrading = (): UseTradingReturn => {
  const { user } = useAppSelector(state => state.auth)
  
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [positions, setPositions] = useState<UserPosition[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Calculate trading statistics
  const calculateStats = useCallback((signals: TradingSignal[], positions: UserPosition[]): TradingStats => {
    const activeSignals = signals.filter(s => s.status === 'active').length
    const completedSignals = signals.filter(s => s.status === 'completed')
    const totalTrades = completedSignals.length
    
    const profitableSignals = completedSignals.filter(s => s.pnl && s.pnl > 0).length
    const winRate = totalTrades > 0 ? ((profitableSignals / totalTrades) * 100).toFixed(1) : '0.0'
    
    const totalPnL = completedSignals.reduce((sum, signal) => sum + (signal.pnl || 0), 0)
    
    return {
      activeSignals,
      winRate: `${winRate}%`,
      totalPnL: `$${totalPnL.toLocaleString()}`,
      totalTrades
    }
  }, [])

  const [stats, setStats] = useState<TradingStats>({
    activeSignals: 0,
    winRate: '0.0%',
    totalPnL: '$0',
    totalTrades: 0
  })

  // Fetch trading signals
  const refreshSignals = useCallback(async () => {
    if (!user?.id) return
    
    try {
      setError(null)
      const data = await tradingSignalsService.getAllSignals(user.id)
      setSignals(data)
    } catch (err) {
      console.error('Error fetching signals:', err)
      setError('Failed to load trading signals')
    }
  }, [user?.id])

  // Fetch market data
  const refreshMarketData = useCallback(async () => {
    try {
      setError(null)
      const data = await marketDataService.getLatestMarketData()
      setMarketData(data)
    } catch (err) {
      console.error('Error fetching market data:', err)
      setError('Failed to load market data')
    }
  }, [])

  // Fetch user positions
  const refreshPositions = useCallback(async () => {
    if (!user?.id) return
    
    try {
      setError(null)
      const data = await userPositionsService.getUserPositions(user.id)
      setPositions(data)
    } catch (err) {
      console.error('Error fetching positions:', err)
      setError('Failed to load positions')
    }
  }, [user?.id])

  // Create new trading signal
  const createSignal = useCallback(async (
    signalData: Omit<TradingSignal, 'id' | 'user_id' | 'created_at' | 'updated_at'>
  ) => {
    if (!user?.id) return

    try {
      setError(null)
      const newSignal = await tradingSignalsService.createSignal({
        ...signalData,
        user_id: user.id
      })
      setSignals(prev => [newSignal, ...prev])
    } catch (err) {
      console.error('Error creating signal:', err)
      setError('Failed to create trading signal')
      throw err
    }
  }, [user?.id])

  // Update existing trading signal
  const updateSignal = useCallback(async (id: string, updates: Partial<TradingSignal>) => {
    try {
      setError(null)
      const updatedSignal = await tradingSignalsService.updateSignal(id, updates)
      setSignals(prev => prev.map(signal => 
        signal.id === id ? updatedSignal : signal
      ))
    } catch (err) {
      console.error('Error updating signal:', err)
      setError('Failed to update trading signal')
      throw err
    }
  }, [])

  // Load all data on component mount
  const loadAllData = useCallback(async () => {
    if (!user?.id) return
    
    setLoading(true)
    
    try {
      await Promise.all([
        refreshSignals(),
        refreshMarketData(),
        refreshPositions()
      ])
    } catch (err) {
      console.error('Error loading trading data:', err)
    } finally {
      setLoading(false)
    }
  }, [refreshSignals, refreshMarketData, refreshPositions, user?.id])

  // Update stats when signals or positions change
  useEffect(() => {
    const newStats = calculateStats(signals, positions)
    setStats(newStats)
  }, [signals, positions, calculateStats])

  // Load data on user change
  useEffect(() => {
    loadAllData()
  }, [loadAllData])

  // Set up real-time subscriptions
  useEffect(() => {
    if (!user?.id) return

    const signalsSubscription = tradingSignalsService.subscribeToSignals(
      user.id,
      (payload) => {
        console.log('Real-time signal update:', payload)
        
        switch (payload.eventType) {
          case 'INSERT':
            setSignals(prev => [payload.new, ...prev])
            break
          case 'UPDATE':
            setSignals(prev => prev.map(signal => 
              signal.id === payload.new.id ? payload.new : signal
            ))
            break
          case 'DELETE':
            setSignals(prev => prev.filter(signal => signal.id !== payload.old.id))
            break
        }
      }
    )

    const marketDataSubscription = marketDataService.subscribeToMarketData(
      (payload) => {
        console.log('Real-time market data update:', payload)
        
        if (payload.eventType === 'INSERT') {
          setMarketData(prev => {
            // Keep only the latest data per symbol
            const filtered = prev.filter(data => data.symbol !== payload.new.symbol)
            return [payload.new, ...filtered]
          })
        }
      }
    )

    return () => {
      signalsSubscription.unsubscribe()
      marketDataSubscription.unsubscribe()
    }
  }, [user?.id])

  return {
    signals,
    marketData,
    positions,
    stats,
    loading,
    error,
    refreshSignals,
    refreshMarketData,
    refreshPositions,
    createSignal,
    updateSignal
  }
}

export default useTrading