import React, { useEffect, useRef, useState } from 'react'
import FusionCharts from 'fusioncharts/core'
import Candlestick from 'fusioncharts/viz/candlestick'
import Line from 'fusioncharts/viz/line'
import FusionTheme from 'fusioncharts/themes/es/fusioncharts.theme.fusion'

// Add chart dependencies
FusionCharts.addDep(Candlestick)
FusionCharts.addDep(Line)
FusionCharts.addDep(FusionTheme)

const ProfessionalChart = ({ 
  type = 'candlestick', 
  data, 
  symbol, 
  width = '100%', 
  height = '600',
  indicators = {},
  onChartReady = null 
}) => {
  const chartRef = useRef(null)
  const chartInstance = useRef(null)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [chartData, setChartData] = useState(null)

  useEffect(() => {
    if (!data || !chartRef.current) return

    console.log(`🎯 ProfessionalChart rendering for ${symbol}:`, {
      type,
      dataPoints: data.length,
      firstPrice: data[0]?.close,
      lastPrice: data[data.length - 1]?.close,
      zoomLevel
    })

    // Process data for chart
    const processedData = processChartData(data, type, indicators)
    setChartData(processedData)

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.dispose()
    }

    // Create chart configuration
    const config = {
      type: getChartType(type),
      renderAt: chartRef.current,
      width,
      height,
      dataFormat: 'json',
      dataSource: processedData
    }

    // Create and render chart
    chartInstance.current = new FusionCharts(config)
    chartInstance.current.render()

    // Call onChartReady callback
    if (onChartReady && typeof onChartReady === 'function') {
      onChartReady(chartInstance.current)
    }

    // Cleanup on unmount
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose()
      }
    }
  }, [data, type, symbol, width, height, indicators, zoomLevel, onChartReady])

  const processChartData = (data, chartType, indicators) => {
    if (!data || data.length === 0) {
      return createEmptyChartData(symbol, chartType)
    }

    switch (chartType) {
      case 'candlestick':
        return createCandlestickChartData(data, symbol, indicators)
      case 'line':
        return createLineChartData(data, symbol, indicators)
      default:
        return createCandlestickChartData(data, symbol, indicators)
    }
  }

  const getChartType = (type) => {
    switch (type) {
      case 'candlestick':
        return 'candlestick'
      case 'line':
        return 'line'
      default:
        return 'candlestick'
    }
  }

  const createEmptyChartData = (symbol, type) => ({
    chart: {
      caption: `${symbol} Price Chart`,
      subcaption: 'Loading data...',
      xAxisName: 'Time',
      yAxisName: 'Price (USD)',
      theme: 'fusion',
      bgColor: 'rgba(17, 24, 39, 0.95)',
      canvasBgColor: 'rgba(17, 24, 39, 0.8)',
      captionFontColor: '#ffffff',
      subcaptionFontColor: '#9ca3af',
      xAxisNameFontColor: '#9ca3af',
      yAxisNameFontColor: '#9ca3af',
      xAxisLineColor: '#374151',
      yAxisLineColor: '#374151',
      xAxisTickColor: '#374151',
      yAxisTickColor: '#374151',
      xAxisLabelFontColor: '#9ca3af',
      yAxisLabelFontColor: '#9ca3af',
      showChartMessage: '0',
      showChartMessageOnLoad: '0'
    },
    dataset: [{
      data: []
    }]
  })

  const createCandlestickChartData = (data, symbol, indicators) => {
    // Process candlestick data
    const chartData = data.map((candle, index) => {
      const open = parseFloat(candle.open) || 0
      const high = parseFloat(candle.high) || 0
      const low = parseFloat(candle.low) || 0
      const close = parseFloat(candle.close) || 0
      const volume = parseFloat(candle.volume) || 0
      
      const tooltext = `
        <div style="background: rgba(0,0,0,0.9); padding: 12px; border-radius: 8px; color: white; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #8b5cf6;">${symbol}</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px;">
            <span style="color: #10b981;">Open: $${open.toFixed(4)}</span>
            <span style="color: #ef4444;">High: $${high.toFixed(4)}</span>
            <span style="color: #f59e0b;">Low: $${low.toFixed(4)}</span>
            <span style="color: #3b82f6;">Close: $${close.toFixed(4)}</span>
          </div>
          <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2);">
            <span style="color: #8b5cf6;">Volume: ${formatVolume(volume)}</span>
          </div>
          ${indicators.ema && candle.ema12 ? `<div style="color: #06b6d4;">EMA12: $${candle.ema12.toFixed(4)}</div>` : ''}
          ${indicators.ema2 && candle.ema26 ? `<div style="color: #f59e0b;">EMA26: $${candle.ema26.toFixed(4)}</div>` : ''}
          ${indicators.sma && candle.sma20 ? `<div style="color: #10b981;">SMA20: $${candle.sma20.toFixed(4)}</div>` : ''}
        </div>
      `
      
      return {
        value: `${open},${high},${low},${close}`,
        tooltext: tooltext,
        volume: volume
      }
    })

    // Create categories for x-axis
    const categories = []
    const step = Math.max(1, Math.floor(data.length / 8))
    for (let i = 0; i < data.length; i += step) {
      const timestamp = data[i].time ? data[i].time * 1000 : data[i].timestamp
      categories.push({
        label: new Date(timestamp).toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        })
      })
    }

    // Add technical indicators
    const datasets = [{
      seriesname: 'Price',
      data: chartData
    }]

    if (indicators.ema && data.some(d => d.ema12)) {
      datasets.push({
        seriesname: 'EMA12',
        renderas: 'line',
        data: data.map((candle, index) => ({
          value: candle.ema12 || null,
          tooltext: `EMA12: $${candle.ema12?.toFixed(4) || 'N/A'}`
        }))
      })
    }

    if (indicators.ema2 && data.some(d => d.ema26)) {
      datasets.push({
        seriesname: 'EMA26',
        renderas: 'line',
        data: data.map((candle, index) => ({
          value: candle.ema26 || null,
          tooltext: `EMA26: $${candle.ema26?.toFixed(4) || 'N/A'}`
        }))
      })
    }

    if (indicators.sma && data.some(d => d.sma20)) {
      datasets.push({
        seriesname: 'SMA20',
        renderas: 'line',
        data: data.map((candle, index) => ({
          value: candle.sma20 || null,
          tooltext: `SMA20: $${candle.sma20?.toFixed(4) || 'N/A'}`
        }))
      })
    }

    return {
      chart: {
        caption: `${symbol} Professional Price Chart`,
        subcaption: `${data.length} data points | Real-time from Binance`,
        xAxisName: 'Time',
        yAxisName: 'Price (USD)',
        theme: 'fusion',
        bgColor: 'rgba(17, 24, 39, 0.95)',
        canvasBgColor: 'rgba(17, 24, 39, 0.8)',
        captionFontColor: '#ffffff',
        subcaptionFontColor: '#9ca3af',
        xAxisNameFontColor: '#9ca3af',
        yAxisNameFontColor: '#9ca3af',
        xAxisLineColor: '#374151',
        yAxisLineColor: '#374151',
        xAxisTickColor: '#374151',
        yAxisTickColor: '#374151',
        xAxisLabelFontColor: '#9ca3af',
        yAxisLabelFontColor: '#9ca3af',
        showChartMessage: '0',
        showChartMessageOnLoad: '0',
        showToolTip: '1',
        animation: '1',
        showLegend: '1',
        legendBgColor: 'rgba(17, 24, 39, 0.9)',
        legendBorderColor: '#374151',
        legendFontColor: '#ffffff',
        showValues: '0',
        showLabels: '1',
        labelDisplay: 'ROTATE',
        slantLabels: '1',
        rotateLabels: '1',
        labelStep: step,
        showPlotBorder: '0',
        showCanvasBorder: '0',
        showBorder: '0',
        enableZoom: '1',
        zoomMode: 'x',
        showZoomResetBtn: '1',
        zoomResetBtnText: 'Reset Zoom',
        zoomResetBtnColor: '#8b5cf6',
        zoomResetBtnBgColor: 'rgba(139, 92, 246, 0.1)',
        zoomResetBtnBorderColor: '#8b5cf6',
        paletteColors: '#8b5cf6,#06b6d4,#10b981,#f59e0b,#ef4444'
      },
      dataset: datasets,
      categories: [{
        category: categories
      }]
    }
  }

  const createLineChartData = (data, symbol, indicators) => {
    const chartData = data.map((point, index) => {
      const close = parseFloat(point.close) || 0
      const timestamp = point.time ? point.time * 1000 : point.timestamp
      
      const tooltext = `
        <div style="background: rgba(0,0,0,0.9); padding: 12px; border-radius: 8px; color: white; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #8b5cf6;">${symbol}</div>
          <div style="font-size: 16px; color: #3b82f6; margin-bottom: 6px;">$${close.toFixed(4)}</div>
          <div style="font-size: 12px; color: #9ca3af;">
            ${new Date(timestamp).toLocaleString()}
          </div>
        </div>
      `
      
      return {
        label: new Date(timestamp).toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        }),
        value: close,
        tooltext: tooltext
      }
    })

    return {
      chart: {
        caption: `${symbol} Price Trend`,
        subcaption: `${data.length} data points | Real-time from Binance`,
        xAxisName: 'Time',
        yAxisName: 'Price (USD)',
        theme: 'fusion',
        bgColor: 'rgba(17, 24, 39, 0.95)',
        canvasBgColor: 'rgba(17, 24, 39, 0.8)',
        captionFontColor: '#ffffff',
        subcaptionFontColor: '#9ca3af',
        xAxisNameFontColor: '#9ca3af',
        yAxisNameFontColor: '#9ca3af',
        xAxisLineColor: '#374151',
        yAxisLineColor: '#374151',
        xAxisTickColor: '#374151',
        yAxisTickColor: '#374151',
        xAxisLabelFontColor: '#9ca3af',
        yAxisLabelFontColor: '#9ca3af',
        lineColor: '#8b5cf6',
        lineThickness: '3',
        showChartMessage: '0',
        showChartMessageOnLoad: '0',
        showToolTip: '1',
        animation: '1',
        enableZoom: '1',
        zoomMode: 'x',
        showZoomResetBtn: '1',
        zoomResetBtnText: 'Reset Zoom',
        zoomResetBtnColor: '#8b5cf6',
        zoomResetBtnBgColor: 'rgba(139, 92, 246, 0.1)',
        zoomResetBtnBorderColor: '#8b5cf6'
      },
      data: chartData
    }
  }



  const formatVolume = (volume) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`
    return volume.toFixed(0)
  }

  const handleZoomIn = () => {
    if (chartInstance.current) {
      setZoomLevel(prev => Math.min(prev * 1.5, 5))
    }
  }

  const handleZoomOut = () => {
    if (chartInstance.current) {
      setZoomLevel(prev => Math.max(prev / 1.5, 0.1))
    }
  }

  const handleResetZoom = () => {
    if (chartInstance.current) {
      setZoomLevel(1)
    }
  }

  return (
    <div className="professional-chart-container">
      {/* Chart Controls */}
      <div className="chart-controls">
        <div className="zoom-controls">
          <button 
            className="zoom-btn"
            onClick={handleZoomOut}
            title="Zoom Out"
          >
            🔍-
          </button>
          <span className="zoom-level">{Math.round(zoomLevel * 100)}%</span>
          <button 
            className="zoom-btn"
            onClick={handleZoomIn}
            title="Zoom In"
          >
            🔍+
          </button>
          <button 
            className="reset-btn"
            onClick={handleResetZoom}
            title="Reset Zoom"
          >
            🔄 Reset
          </button>
        </div>
        
        <div className="chart-info">
          <span className="data-points">
            {data ? `${data.length} data points` : 'Loading...'}
          </span>
          <span className="chart-type">
            {type.toUpperCase()} Chart
          </span>
        </div>
      </div>

      {/* Chart Container */}
      <div className="chart-wrapper">
        <div ref={chartRef} className="chart-container" />
      </div>

      {/* Chart Status */}
      {!data || data.length === 0 ? (
        <div className="chart-status">
          <div className="loading-spinner"></div>
          <span>Loading professional chart data...</span>
        </div>
      ) : (
        <div className="chart-status">
          <span className="status-success">✅ Chart loaded successfully</span>
          <span className="data-range">
            {data.length > 0 && (
              <>
                Range: ${parseFloat(data[0]?.close || 0).toFixed(4)} - ${parseFloat(data[data.length - 1]?.close || 0).toFixed(4)}
              </>
            )}
          </span>
        </div>
      )}
    </div>
  )
}

export default ProfessionalChart
