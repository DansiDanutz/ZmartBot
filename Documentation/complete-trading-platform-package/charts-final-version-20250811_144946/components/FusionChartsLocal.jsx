import React, { useEffect, useRef, useState } from 'react'

const FusionChartsLocal = ({ 
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
  const [isLoaded, setIsLoaded] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)

  useEffect(() => {
    // Check if FusionCharts is already loaded
    const checkFusionCharts = () => {
      if (window.FusionCharts) {
        setIsLoaded(true)
        console.log('✅ FusionCharts loaded successfully')
        return true
      }
      return false
    }

    // Check immediately
    if (!checkFusionCharts()) {
      // Wait for scripts to load
      const interval = setInterval(() => {
        if (checkFusionCharts()) {
          clearInterval(interval)
        }
      }, 100)

      // Timeout after 5 seconds
      setTimeout(() => {
        clearInterval(interval)
        if (!window.FusionCharts) {
          console.error('❌ FusionCharts failed to load after 5 seconds')
        }
      }, 5000)
    }
  }, [])

  const loadScript = (src) => {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = src
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }

  useEffect(() => {
    if (!isLoaded || !data || !chartRef.current || !window.FusionCharts) {
      console.log(`⏳ Waiting for chart to be ready:`, {
        isLoaded,
        hasData: !!data,
        dataLength: data?.length,
        hasChartRef: !!chartRef.current,
        hasFusionCharts: !!window.FusionCharts
      })
      return
    }

    console.log(`🎯 FusionChartsLocal rendering for ${symbol}:`, {
      type,
      dataPoints: data.length,
      firstPrice: data[0]?.close,
      lastPrice: data[data.length - 1]?.close,
      zoomLevel,
      sampleData: data.slice(0, 2)
    })

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.dispose()
    }

    // Process data for chart
    const processedData = processChartData(data, type, indicators)
    console.log(`📊 Processed chart data:`, {
      chartType: processedData.chart?.caption,
      dataPoints: processedData.dataset?.[0]?.data?.length,
      categories: processedData.categories?.[0]?.category?.length,
      sampleProcessedData: processedData.dataset?.[0]?.data?.slice(0, 2)
    })

    // Create chart configuration
    const config = {
      type: getChartType(type),
      renderAt: chartRef.current,
      width,
      height,
      dataFormat: 'json',
      dataSource: processedData
    }

    console.log(`🔧 Chart config:`, {
      type: config.type,
      width: config.width,
      height: config.height,
      dataFormat: config.dataFormat
    })

    try {
      // Create and render chart
      chartInstance.current = new window.FusionCharts(config)
      chartInstance.current.render()
      console.log(`✅ Chart rendered successfully for ${symbol}`)

      // Call onChartReady callback
      if (onChartReady && typeof onChartReady === 'function') {
        onChartReady(chartInstance.current)
      }
    } catch (error) {
      console.error(`❌ Error rendering chart for ${symbol}:`, error)
    }

    // Cleanup on unmount
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose()
      }
    }
  }, [isLoaded, data, type, symbol, width, height, indicators, zoomLevel, onChartReady])

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

  const createEmptyChartData = (symbol, type) => {
    console.log(`📊 Creating empty chart data for ${symbol}`)
    
    // Create some test data to ensure chart renders
    const testData = [
      { open: '50000', high: '51000', low: '49000', close: '50500', x: '1', volume: '1000000' },
      { open: '50500', high: '52000', low: '50000', close: '51500', x: '2', volume: '1200000' },
      { open: '51500', high: '53000', low: '51000', close: '52500', x: '3', volume: '1100000' },
      { open: '52500', high: '54000', low: '52000', close: '53500', x: '4', volume: '1300000' },
      { open: '53500', high: '55000', low: '53000', close: '54500', x: '5', volume: '1400000' }
    ]
    
    return {
      chart: {
        caption: `${symbol} Price Chart`,
        subCaption: 'Loading real-time data...',
        numberprefix: '$',
        vNumberPrefix: ' ',
        pyaxisname: 'Price (USD)',
        vyaxisname: 'Volume (Millions)',
        theme: 'fusion',
        bgColor: 'rgba(17, 24, 39, 0.95)',
        canvasBgColor: 'rgba(17, 24, 39, 0.8)',
        captionFontColor: '#ffffff',
        subCaptionFontColor: '#9ca3af',
        showChartMessage: '0',
        showChartMessageOnLoad: '0',
        showToolTip: '1',
        animation: '1',
        showVolumeChart: '1',
        volumeHeightPercent: '30',
        enableZoom: '1',
        zoomMode: 'x',
        showZoomResetBtn: '1'
      },
      categories: [{
        category: [
          { label: 'Test 1', x: '1' },
          { label: 'Test 2', x: '2' },
          { label: 'Test 3', x: '3' },
          { label: 'Test 4', x: '4' },
          { label: 'Test 5', x: '5' }
        ]
      }],
      dataset: [{
        data: testData
      }]
    }
  }

  const createCandlestickChartData = (data, symbol, indicators) => {
    console.log(`🎯 Processing ${data.length} candlestick data points for ${symbol}`)
    console.log('Sample data:', data.slice(0, 3))
    
    // Process candlestick data in the correct FusionCharts format
    const chartData = data.map((candle, index) => {
      const open = parseFloat(candle.open) || 0
      const high = parseFloat(candle.high) || 0
      const low = parseFloat(candle.low) || 0
      const close = parseFloat(candle.close) || 0
      const volume = parseFloat(candle.volume) || 0
      
      // Ensure all values are valid numbers
      if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close) || isNaN(volume)) {
        console.warn(`⚠️ Invalid data at index ${index}:`, candle)
        return null
      }
      
      return {
        open: open.toFixed(4),
        high: high.toFixed(4),
        low: low.toFixed(4),
        close: close.toFixed(4),
        x: (index + 1).toString(),
        volume: volume.toString()
      }
    }).filter(item => item !== null) // Remove invalid data points

    console.log(`✅ Processed ${chartData.length} valid candlestick data points`)
    console.log('Sample processed data:', chartData.slice(0, 3))

    // Create categories for x-axis
    const categories = []
    const step = Math.max(1, Math.floor(data.length / 8))
    for (let i = 0; i < data.length; i += step) {
      const timestamp = data[i].time ? data[i].time * 1000 : data[i].timestamp
      const date = new Date(timestamp)
      categories.push({
        label: date.toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        }),
        x: (i + 1).toString()
      })
    }

    return {
      chart: {
        // Chart Titles and Caption
        caption: `${symbol} Professional Trading Chart`,
        subCaption: `${data.length} data points | Real-time from Binance`,
        captionFont: 'Arial',
        captionFontSize: '18',
        captionFontColor: '#ffffff',
        captionFontBold: '1',
        subCaptionFont: 'Arial',
        subCaptionFontSize: '14',
        subCaptionFontColor: '#9ca3af',
        captionAlignment: 'center',
        captionOnTop: '1',
        alignCaptionWithCanvas: '1',
        captionHorizontalPadding: '10',
        
        // Axis Configuration
        pyaxisname: 'Price (USD)',
        vyaxisname: 'Volume (Millions)',
        pYAxisNameFont: 'Arial',
        pYAxisNameFontSize: '12',
        pYAxisNameFontColor: '#9ca3af',
        pYAxisNameFontBold: '1',
        vYAxisNameFont: 'Arial',
        vYAxisNameFontSize: '12',
        vYAxisNameFontColor: '#9ca3af',
        vYAxisNameFontBold: '1',
        showYAxisValues: '1',
        yAxisValuesStep: '1',
        yAxisValueDecimals: '4',
        vYAxisValueDecimals: '0',
        forceYAxisValueDecimals: '1',
        forceVYAxisValueDecimals: '1',
        
        // Number Formatting
        numberprefix: '$',
        vNumberPrefix: ' ',
        formatNumber: '1',
        formatNumberScale: '1',
        defaultNumberScale: 'K,M,B',
        numberScaleUnit: 'K,M,B',
        numberScaleValue: '1000,1000000,1000000000',
        scaleRecursively: '1',
        maxScaleRecursion: '3',
        scaleSeparator: ',',
        decimalSeparator: '.',
        thousandSeparator: ',',
        decimals: '4',
        forceDecimals: '1',
        vFormatNumber: '1',
        vFormatNumberScale: '1',
        vDefaultNumberScale: 'K,M,B',
        vNumberScaleUnit: 'K,M,B',
        vNumberScaleValue: '1000,1000000,1000000000',
        vDecimals: '0',
        forceVDecimals: '1',
        
        // Chart Cosmetics
        theme: 'fusion',
        bgColor: 'rgba(17, 24, 39, 0.95)',
        bgAlpha: '95',
        canvasBgColor: 'rgba(17, 24, 39, 0.8)',
        canvasBgAlpha: '80',
        showBorder: '0',
        showCanvasBorder: '0',
        canvasBorderColor: '#374151',
        canvasBorderThickness: '1',
        canvasBorderAlpha: '50',
        
        // Data Plot Cosmetics (Candlestick Colors)
        bearBorderColor: '#ef4444',
        bearFillColor: '#ef4444',
        bullBorderColor: '#10b981',
        bullFillColor: '#10b981',
        showShadow: '1',
        showVPlotBorder: '1',
        vPlotBorderColor: '#374151',
        vPlotBorderThickness: '1',
        vPlotBorderAlpha: '50',
        
        // Volume Chart
        showVolumeChart: '1',
        volumeHeightPercent: '30',
        
        // Divisional Lines & Grids
        numDivLines: '5',
        divLineColor: '#374151',
        divLineThickness: '1',
        divLineAlpha: '30',
        divLineDashed: '1',
        divLineDashLen: '5',
        divLineDashGap: '5',
        showAlternateHGridColor: '1',
        alternateHGridColor: 'rgba(55, 65, 81, 0.1)',
        alternateHGridAlpha: '10',
        
        // Tooltip Configuration
        showToolTip: '1',
        toolTipBgColor: 'rgba(0, 0, 0, 0.9)',
        toolTipColor: '#ffffff',
        toolTipBorderColor: '#374151',
        tooltipBorderAlpha: '80',
        toolTipSepChar: ' | ',
        showToolTipShadow: '1',
        tooltipbgalpha: '90',
        tooltipborderradius: '8',
        tooltipborderthickness: '1',
        toolTipPadding: '10',
        plottooltext: `<div style="background: rgba(0,0,0,0.9); padding: 12px; border-radius: 8px; color: white; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #8b5cf6;">${symbol}</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px;">
            <span style="color: #10b981;">Open: $open</span>
            <span style="color: #ef4444;">High: $high</span>
            <span style="color: #f59e0b;">Low: $low</span>
            <span style="color: #3b82f6;">Close: $close</span>
          </div>
          <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2);">
            <span style="color: #8b5cf6;">Volume: $volume</span>
          </div>
        </div>`,
        
        // Animation and Effects
        animation: '1',
        animationDuration: '2',
        showHoverEffect: '1',
        plotHoverEffect: '1',
        plotFillHoverColor: '#8b5cf6',
        plotFillHoverAlpha: '20',
        
        // Zoom and Navigation
        enableZoom: '1',
        zoomMode: 'x',
        showZoomResetBtn: '1',
        zoomResetBtnText: 'Reset Zoom',
        zoomResetBtnColor: '#8b5cf6',
        zoomResetBtnBgColor: 'rgba(139, 92, 246, 0.1)',
        zoomResetBtnBorderColor: '#8b5cf6',
        
        // Legend Configuration
        showLegend: '1',
        legendItemFont: 'Arial',
        legendItemFontSize: '12',
        legendItemFontColor: '#ffffff',
        legendItemHoverFontColor: '#8b5cf6',
        legendPosition: 'bottom',
        legendBgColor: 'rgba(17, 24, 39, 0.9)',
        legendBgAlpha: '90',
        legendBorderColor: '#374151',
        legendBorderThickness: '1',
        legendBorderAlpha: '50',
        legendShadow: '1',
        legendAllowDrag: '1',
        
        // Chart Padding & Margins
        captionPadding: '15',
        yAxisNamePadding: '10',
        yAxisValuesPadding: '5',
        labelPadding: '5',
        chartLeftMargin: '10',
        chartRightMargin: '10',
        chartTopMargin: '10',
        chartBottomMargin: '10',
        valuePadding: '5',
        legendPadding: '10',
        canvasPadding: '10',
        plotSpacePercent: '80',
        
        // Font Properties
        baseFont: 'Arial',
        baseFontSize: '12',
        baseFontColor: '#9ca3af',
        outCnvBaseFont: 'Arial',
        outCnvBaseFontSize: '12',
        outCnvBaseFontColor: '#9ca3af',
        
        // Export Features
        exportEnabled: '1',
        exportAction: 'download',
        exportFormats: 'PNG,JPG,PDF,SVG',
        exportShowMenuItem: '1',
        exportFileName: `${symbol}_chart`,
        
        // Chart Messages
        showChartMessage: '0',
        showChartMessageOnLoad: '0',
        loadMessage: 'Loading professional chart data...',
        loadMessageFont: 'Arial',
        loadMessageFontSize: '14',
        loadMessageColor: '#8b5cf6',
        dataEmptyMessage: 'No data available for this symbol',
        dataEmptyMessageFont: 'Arial',
        dataEmptyMessageFontSize: '14',
        dataEmptyMessageColor: '#9ca3af'
      },
      categories: [{
        font: 'Arial',
        fontColor: '#9ca3af',
        fontSize: '11',
        verticalLineAlpha: '30',
        verticalLineColor: '#374151',
        verticalLineDashed: '1',
        verticalLineDashLen: '3',
        verticalLineDashGap: '3',
        verticalLineThickness: '1',
        category: categories
      }],
      dataset: [{
        data: chartData
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

  if (!isLoaded) {
    return (
      <div className="chart-loading">
        <div className="loading-spinner"></div>
        <span>Loading FusionCharts Suite XT...</span>
      </div>
    )
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
          <span className="status-success">✅ FusionCharts Suite XT loaded successfully</span>
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

export default FusionChartsLocal
