import React, { useEffect, useRef, useState, useCallback } from 'react'
import { createChart, IChartApi, ISeriesApi, LineStyle, CrosshairMode } from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  TrendingUp,
  TrendingDown,
  Settings,
  FullScreen,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BarChart3,
  LineChart,
  CandlestickChart,
  Volume2
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface CandleData {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

interface TechnicalIndicator {
  id: string
  name: string
  type: 'line' | 'histogram' | 'baseline'
  color: string
  visible: boolean
  data: Array<{ time: string; value: number }>
}

interface TradingViewChartProps {
  symbol: string
  data: CandleData[]
  indicators?: TechnicalIndicator[]
  height?: number
  showVolume?: boolean
  showGrid?: boolean
  className?: string
  onCrosshairMove?: (param: any) => void
  onTimeRangeChanged?: (from: string, to: string) => void
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  data,
  indicators = [],
  height = 400,
  showVolume = true,
  showGrid = true,
  className,
  onCrosshairMove,
  onTimeRangeChanged
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const indicatorSeriesRefs = useRef<Map<string, ISeriesApi<any>>>(new Map())

  const [chartType, setChartType] = useState<'candlestick' | 'line' | 'bar'>('candlestick')
  const [isFullScreen, setIsFullScreen] = useState(false)
  const [activeIndicators, setActiveIndicators] = useState<string[]>([])
  const [currentPrice, setCurrentPrice] = useState<number | null>(null)
  const [priceChange, setPriceChange] = useState<number | null>(null)

  // Technical Indicators Configuration
  const availableIndicators = [
    { id: 'sma_20', name: 'SMA (20)', color: '#2962FF' },
    { id: 'sma_50', name: 'SMA (50)', color: '#FF6D00' },
    { id: 'ema_12', name: 'EMA (12)', color: '#E91E63' },
    { id: 'ema_26', name: 'EMA (26)', color: '#9C27B0' },
    { id: 'rsi', name: 'RSI (14)', color: '#00E676' },
    { id: 'macd', name: 'MACD', color: '#00BCD4' },
    { id: 'bb_upper', name: 'Bollinger Upper', color: '#FF5722' },
    { id: 'bb_lower', name: 'Bollinger Lower', color: '#FF5722' },
    { id: 'stoch_k', name: 'Stochastic %K', color: '#FFC107' },
    { id: 'stoch_d', name: 'Stochastic %D', color: '#FF9800' }
  ]

  // Initialize chart
  const initChart = useCallback(() => {
    if (!chartContainerRef.current || chartRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: showGrid ? '#2B2B43' : 'transparent' },
        horzLines: { color: showGrid ? '#2B2B43' : 'transparent' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: '#3c434c',
          style: LineStyle.Dashed,
        },
        horzLine: {
          width: 1,
          color: '#3c434c',
          style: LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: '#485c7b',
        textColor: '#d1d4dc',
      },
      timeScale: {
        borderColor: '#485c7b',
        textColor: '#d1d4dc',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    })

    chartRef.current = chart

    // Add main price series
    let mainSeries: ISeriesApi<any>
    if (chartType === 'candlestick') {
      mainSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      })
    } else if (chartType === 'line') {
      mainSeries = chart.addLineSeries({
        color: '#2196F3',
        lineWidth: 2,
      })
    } else {
      mainSeries = chart.addBarSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
      })
    }

    candleSeriesRef.current = mainSeries

    // Add volume series if enabled
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: { type: 'volume' },
        priceScaleId: '',
        scaleMargins: { top: 0.8, bottom: 0 },
      })
      volumeSeriesRef.current = volumeSeries
    }

    // Set up crosshair move handler
    chart.subscribeCrosshairMove((param) => {
      if (onCrosshairMove) {
        onCrosshairMove(param)
      }

      if (param.point && param.time) {
        const data = param.seriesData.get(mainSeries)
        if (data && 'close' in data) {
          setCurrentPrice(data.close as number)
        }
      }
    })

    // Set up time range change handler
    chart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
      if (timeRange && onTimeRangeChanged) {
        onTimeRangeChanged(timeRange.from as string, timeRange.to as string)
      }
    })

    // Handle window resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [height, showGrid, showVolume, chartType, onCrosshairMove, onTimeRangeChanged])

  // Update chart data
  useEffect(() => {
    if (!chartRef.current || !candleSeriesRef.current || !data.length) return

    try {
      if (chartType === 'candlestick') {
        candleSeriesRef.current.setData(data)
      } else if (chartType === 'line') {
        const lineData = data.map(d => ({ time: d.time, value: d.close }))
        candleSeriesRef.current.setData(lineData)
      } else {
        candleSeriesRef.current.setData(data)
      }

      // Update volume data
      if (showVolume && volumeSeriesRef.current) {
        const volumeData = data
          .filter(d => d.volume !== undefined)
          .map(d => ({
            time: d.time,
            value: d.volume!,
            color: d.close >= d.open ? '#26a69a' : '#ef5350'
          }))
        volumeSeriesRef.current.setData(volumeData)
      }

      // Calculate price change
      if (data.length >= 2) {
        const latest = data[data.length - 1]
        const previous = data[data.length - 2]
        const change = ((latest.close - previous.close) / previous.close) * 100
        setPriceChange(change)
        setCurrentPrice(latest.close)
      }
    } catch (error) {
      console.error('Error updating chart data:', error)
    }
  }, [data, chartType, showVolume])

  // Add/remove technical indicators
  useEffect(() => {
    if (!chartRef.current || !indicators.length) return

    indicators.forEach(indicator => {
      if (activeIndicators.includes(indicator.id)) {
        if (!indicatorSeriesRefs.current.has(indicator.id)) {
          let series: ISeriesApi<any>
          
          if (indicator.type === 'line') {
            series = chartRef.current!.addLineSeries({
              color: indicator.color,
              lineWidth: 1,
              title: indicator.name,
            })
          } else if (indicator.type === 'histogram') {
            series = chartRef.current!.addHistogramSeries({
              color: indicator.color,
              title: indicator.name,
            })
          } else {
            series = chartRef.current!.addBaselineSeries({
              baseValue: { type: 'price', price: 0 },
              topLineColor: indicator.color,
              bottomLineColor: indicator.color,
              title: indicator.name,
            })
          }

          series.setData(indicator.data)
          indicatorSeriesRefs.current.set(indicator.id, series)
        }
      } else {
        const series = indicatorSeriesRefs.current.get(indicator.id)
        if (series) {
          chartRef.current!.removeSeries(series)
          indicatorSeriesRefs.current.delete(indicator.id)
        }
      }
    })
  }, [indicators, activeIndicators])

  // Initialize chart on mount
  useEffect(() => {
    const cleanup = initChart()
    return cleanup
  }, [initChart])

  const toggleIndicator = (indicatorId: string) => {
    setActiveIndicators(prev => 
      prev.includes(indicatorId) 
        ? prev.filter(id => id !== indicatorId)
        : [...prev, indicatorId]
    )
  }

  const handleChartTypeChange = (type: 'candlestick' | 'line' | 'bar') => {
    setChartType(type)
    if (chartRef.current) {
      chartRef.current.remove()
      chartRef.current = null
      candleSeriesRef.current = null
      volumeSeriesRef.current = null
      indicatorSeriesRefs.current.clear()
    }
  }

  const resetChart = () => {
    if (chartRef.current) {
      chartRef.current.timeScale().resetTimeScale()
    }
  }

  const fitChart = () => {
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent()
    }
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center space-x-4">
          <CardTitle className="text-lg font-semibold">
            {symbol}
          </CardTitle>
          {currentPrice && (
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold">
                ${currentPrice.toLocaleString()}
              </span>
              {priceChange !== null && (
                <Badge variant={priceChange >= 0 ? "success" : "destructive"}>
                  {priceChange >= 0 ? (
                    <TrendingUp className="w-3 h-3 mr-1" />
                  ) : (
                    <TrendingDown className="w-3 h-3 mr-1" />
                  )}
                  {Math.abs(priceChange).toFixed(2)}%
                </Badge>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* Chart Type Controls */}
          <div className="flex items-center border border-border rounded-lg p-1">
            <Button
              variant={chartType === 'candlestick' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleChartTypeChange('candlestick')}
              className="h-8 px-2"
            >
              <CandlestickChart className="w-4 h-4" />
            </Button>
            <Button
              variant={chartType === 'line' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleChartTypeChange('line')}
              className="h-8 px-2"
            >
              <LineChart className="w-4 h-4" />
            </Button>
            <Button
              variant={chartType === 'bar' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleChartTypeChange('bar')}
              className="h-8 px-2"
            >
              <BarChart3 className="w-4 h-4" />
            </Button>
          </div>

          {/* Chart Controls */}
          <Button variant="outline" size="sm" onClick={resetChart}>
            <RotateCcw className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={fitChart}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm">
            <FullScreen className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {/* Technical Indicators Panel */}
        <div className="px-6 pb-4">
          <div className="flex flex-wrap gap-2">
            {availableIndicators.map(indicator => (
              <Button
                key={indicator.id}
                variant={activeIndicators.includes(indicator.id) ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleIndicator(indicator.id)}
                className="h-7 text-xs"
                style={activeIndicators.includes(indicator.id) ? { 
                  backgroundColor: indicator.color + '20',
                  borderColor: indicator.color,
                  color: indicator.color 
                } : {}}
              >
                {indicator.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Chart Container */}
        <div 
          ref={chartContainerRef} 
          className="w-full bg-background"
          style={{ height: height }}
        />

        {/* Chart Info Panel */}
        <div className="px-6 py-3 border-t border-border">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center space-x-4">
              <span>Data Points: {data.length}</span>
              <span>Active Indicators: {activeIndicators.length}</span>
              {showVolume && (
                <div className="flex items-center space-x-1">
                  <Volume2 className="w-3 h-3" />
                  <span>Volume</span>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <span>Real-time Updates</span>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default TradingViewChart