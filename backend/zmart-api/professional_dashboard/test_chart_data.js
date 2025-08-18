// Test script to verify chart data processing
async function testChartData() {
  console.log('🧪 Testing Chart Data Processing...')
  
  try {
    // Test BTCUSDT data
    const response = await fetch('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=24')
    const data = await response.json()
    
    console.log('📊 Raw Binance Data (first 3 candles):', data.slice(0, 3))
    
    // Process data like the frontend does
    const chartData = data.map((candle, index) => {
      const [timestamp, open, high, low, close, volume] = candle
      const date = new Date(parseInt(timestamp))
      
      return {
        timestamp: parseInt(timestamp),
        date,
        open: parseFloat(open),
        high: parseFloat(high),
        low: parseFloat(low),
        close: parseFloat(close),
        volume: parseFloat(volume),
        hour: index
      }
    })
    
    console.log('🔧 Processed Chart Data (first 3 points):', chartData.slice(0, 3))
    
    // Check for price variation
    const prices = chartData.map(d => d.close)
    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const priceRange = maxPrice - minPrice
    
    console.log('💰 Price Analysis:')
    console.log('  - Min Price:', minPrice)
    console.log('  - Max Price:', maxPrice)
    console.log('  - Price Range:', priceRange)
    console.log('  - Has Variation:', priceRange > 0)
    
    // Test FusionChart data format
    const fusionChartData = chartData.map((point, index) => {
      if (!point || typeof point.close !== 'number') {
        console.warn(`Invalid data point:`, point)
        return null
      }
      
      return {
        x: point.timestamp,
        y: point.close,
        label: new Date(point.timestamp).toLocaleTimeString()
      }
    }).filter(item => item !== null)
    
    console.log('🎯 FusionChart Data (first 3 points):', fusionChartData.slice(0, 3))
    
    return {
      success: true,
      dataPoints: chartData.length,
      priceRange,
      hasVariation: priceRange > 0
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

// Run the test
testChartData()
