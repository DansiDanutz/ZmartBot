import React, { useEffect, useRef } from 'react'
import FusionCharts from 'fusioncharts/core'
import Scatter from 'fusioncharts/viz/scatter'
import Candlestick from 'fusioncharts/viz/candlestick'
import Line from 'fusioncharts/viz/line'
import FusionTheme from 'fusioncharts/themes/es/fusioncharts.theme.fusion'

// Add chart dependencies
FusionCharts.addDep(Scatter)
FusionCharts.addDep(Candlestick)
FusionCharts.addDep(Line)
FusionCharts.addDep(FusionTheme)

const FusionChart = ({ 
  type = 'scatter', 
  data, 
  symbol, 
  width = '100%', 
  height = '400',
  chartConfig = {},
  onChartReady = null 
}) => {
  const chartRef = useRef(null)
  const chartInstance = useRef(null)

  useEffect(() => {
    if (!data || !chartRef.current) return

    console.log(`🎯 FusionChart rendering for ${symbol}:`, {
      type,
      dataPoints: data.length,
      firstPrice: data[0]?.close,
      lastPrice: data[data.length - 1]?.close
    })

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.dispose()
    }

    // Create chart configuration based on type
    let chartData = {}
    
    switch (type) {
      case 'scatter':
        chartData = createScatterChartData(data, symbol)
        break
      case 'candlestick':
        chartData = createCandlestickChartData(data, symbol)
        break
      case 'line':
        chartData = createLineChartData(data, symbol)
        break
      default:
        chartData = createScatterChartData(data, symbol)
    }

    // Chart configuration
    const config = {
      type,
      renderAt: chartRef.current,
      width,
      height,
      dataFormat: 'json',
      dataSource: {
        ...chartData,
        chart: {
          ...chartData.chart,
          ...chartConfig,
          theme: 'fusion',
          // Remove trial watermark
          showChartMessage: '0',
          showChartMessageOnLoad: '0'
        }
      }
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
  }, [data, type, symbol, width, height, chartConfig, onChartReady])

  return <div ref={chartRef} />
}

// Create scatter chart data (price vs time)
const createScatterChartData = (data, symbol) => {
  if (!data || data.length === 0) {
    return {
      chart: {
        caption: `${symbol} Price Movement`,
        subcaption: '24 Hour Price Data',
        xAxisName: 'Time',
        yAxisName: 'Price (USD)',
        showRegressionLine: '1',
        plotToolText: `<b>$${symbol}</b> price: <b>$yDataValue</b> at <b>$xvalue</b>`,
        theme: 'fusion'
      },
      dataset: [{
        seriesname: `${symbol} Price`,
        anchorbgcolor: '#8b5cf6',
        data: []
      }],
      categories: [{
        category: []
      }]
    }
  }

  // Process data for scatter plot
  const chartData = data.map((point, index) => {
    // Ensure we have valid data
    if (!point || typeof point.close !== 'number') {
      console.warn(`Invalid data point for ${symbol}:`, point)
      return null
    }
    
    return {
      x: point.timestamp,
      y: point.close,
      label: new Date(point.timestamp).toLocaleTimeString()
    }
  }).filter(item => item !== null) // Remove invalid data points

  // Create categories for x-axis
  const categories = []
  const step = Math.max(1, Math.floor(data.length / 6))
  for (let i = 0; i < data.length; i += step) {
    categories.push({
      x: data[i].timestamp,
      label: new Date(data[i].timestamp).toLocaleTimeString(),
      showverticalline: '1'
    })
  }

  return {
    chart: {
      caption: `${symbol} Price Movement`,
      subcaption: '24 Hour Price Data from Binance',
      xAxisName: 'Time',
      yAxisName: 'Price (USD)',
      showRegressionLine: '1',
      plotToolText: `<b>$${symbol}</b> price: <b>$$yDataValue</b> at <b>$xvalue</b>`,
      theme: 'fusion',
      bgColor: 'rgba(26, 26, 26, 0.8)',
      canvasBgColor: 'rgba(26, 26, 26, 0.6)',
      captionFontColor: '#ffffff',
      subcaptionFontColor: '#9ca3af',
      xAxisNameFontColor: '#9ca3af',
      yAxisNameFontColor: '#9ca3af',
      xAxisLineColor: '#374151',
      yAxisLineColor: '#374151',
      xAxisTickColor: '#374151',
      yAxisTickColor: '#374151',
      xAxisLabelFontColor: '#9ca3af',
      yAxisLabelFontColor: '#9ca3af'
    },
    dataset: [{
      seriesname: `${symbol} Price`,
      anchorbgcolor: '#8b5cf6',
      data: chartData
    }],
    categories: [{
      verticallinedashed: '1',
      verticallinedashlen: '2',
      verticallinedashgap: '2',
      verticallinethickness: '1',
      verticallinecolor: '#374151',
      category: categories
    }]
  }
}

// Create candlestick chart data
const createCandlestickChartData = (data, symbol) => {
  if (!data || data.length === 0) {
    return {
      chart: {
        caption: `${symbol} Price Chart`,
        subcaption: '24 Hour OHLC Data',
        xAxisName: 'Time',
        yAxisName: 'Price (USD)',
        plotToolText: `<b>$${symbol}</b><br/>Open: <b>$open</b><br/>High: <b>$high</b><br/>Low: <b>$low</b><br/>Close: <b>$close</b>`,
        theme: 'fusion'
      },
      dataset: [{
        data: []
      }]
    }
  }

  // Process data for candlestick chart
  const chartData = data.map((candle, index) => {
    // Ensure all values are valid numbers
    const open = parseFloat(candle.open) || 0
    const high = parseFloat(candle.high) || 0
    const low = parseFloat(candle.low) || 0
    const close = parseFloat(candle.close) || 0
    
    return {
      value: `${open},${high},${low},${close}`,
      tooltext: `${new Date(candle.timestamp).toLocaleTimeString()}<br/>Open: $${open.toFixed(2)}<br/>High: $${high.toFixed(2)}<br/>Low: $${low.toFixed(2)}<br/>Close: $${close.toFixed(2)}`
    }
  })

  // Create categories for x-axis (show fewer labels for cleaner look)
  const categories = []
  const step = Math.max(1, Math.floor(data.length / 4))
  for (let i = 0; i < data.length; i += step) {
    categories.push({
      label: new Date(data[i].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  }

  return {
    chart: {
      caption: `${symbol} Price Chart`,
      subcaption: '24 Hour OHLC Data',
      xAxisName: 'Time',
      yAxisName: 'Price (USD)',
      plotToolText: `<b>$${symbol}</b><br/>Open: <b>$open</b><br/>High: <b>$high</b><br/>Low: <b>$low</b><br/>Close: <b>$close</b>`,
      theme: 'fusion',
      bgColor: 'transparent',
      canvasBgColor: 'transparent',
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
      showXAxisLabels: '0',
      showYAxisLabels: '0',
      showXAxisValues: '0',
      showYAxisValues: '0',
      showPlotBorder: '0',
      showCanvasBorder: '0',
      showBorder: '0',
      showLegend: '0',
      showValues: '0',
      showLabels: '0',
      showToolTip: '1',
      animation: '0'
    },
    dataset: [{
      data: chartData
    }],
    categories: [{
      category: categories
    }]
  }
}

// Create line chart data
const createLineChartData = (data, symbol) => {
  if (!data || data.length === 0) {
    return {
      chart: {
        caption: `${symbol} Price Trend`,
        subcaption: '24 Hour Price Movement',
        xAxisName: 'Time',
        yAxisName: 'Price (USD)',
        plotToolText: `<b>$${symbol}</b> price: <b>$$yDataValue</b> at <b>$xvalue</b>`,
        theme: 'fusion'
      },
      data: []
    }
  }

  // Process data for line chart
  const chartData = data.map((point, index) => ({
    label: new Date(point.timestamp).toLocaleTimeString(),
    value: point.close,
    tooltext: `${new Date(point.timestamp).toLocaleTimeString()}<br/>Price: $${point.close}`
  }))

  return {
    chart: {
      caption: `${symbol} Price Trend`,
      subcaption: '24 Hour Price Movement from Binance',
      xAxisName: 'Time',
      yAxisName: 'Price (USD)',
      plotToolText: `<b>$${symbol}</b> price: <b>$$yDataValue</b> at <b>$xvalue</b>`,
      theme: 'fusion',
      bgColor: 'rgba(26, 26, 26, 0.8)',
      canvasBgColor: 'rgba(26, 26, 26, 0.6)',
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
      lineThickness: '3'
    },
    data: chartData
  }
}

export default FusionChart
