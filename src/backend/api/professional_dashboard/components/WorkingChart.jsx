// WorkingChart - Bulletproof chart component that always works
// Uses simple HTML/CSS for guaranteed rendering
// ---------------------------------------------------------------------------------

import React, { useState, useEffect } from 'react';

const WorkingChart = ({ symbol, height = 100, marketData = null }) => {
  const [priceData, setPriceData] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch price data from Binance
  useEffect(() => {
    const fetchPriceData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch 24 hours of hourly data - NO CUSTOM HEADERS to avoid CORS issues
        const response = await fetch(
          `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1h&limit=24`
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const prices = data.map(candle => parseFloat(candle[4])); // Close prices
        const latestPrice = prices[prices.length - 1];
        
        setPriceData(prices);
        setCurrentPrice(latestPrice);
        setLoading(false);
        
        console.log(`✅ Chart data loaded for ${symbol}: ${prices.length} points, latest: $${latestPrice}`);
      } catch (err) {
        console.error(`❌ Error fetching data for ${symbol}:`, err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchPriceData();
  }, [symbol]);

  // Generate chart bars
  const generateChartBars = () => {
    if (priceData.length === 0) return [];

    const minPrice = Math.min(...priceData);
    const maxPrice = Math.max(...priceData);
    const priceRange = maxPrice - minPrice;

    return priceData.map((price, index) => {
      const heightPercent = priceRange > 0 ? ((price - minPrice) / priceRange) * 100 : 50;
      const isLatest = index === priceData.length - 1;
      
      return {
        height: `${heightPercent}%`,
        price,
        isLatest,
        color: isLatest ? '#22c55e' : '#3b82f6'
      };
    });
  };

  if (loading) {
    return (
      <div style={{
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(26, 26, 26, 0.3)',
        borderRadius: '8px',
        border: '1px solid rgba(139, 92, 246, 0.2)'
      }}>
        <div style={{ textAlign: 'center', color: '#8b5cf6' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>⏳</div>
          <div style={{ fontSize: '0.8rem' }}>Loading {symbol}...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(239, 68, 68, 0.1)',
        borderRadius: '8px',
        border: '1px solid rgba(239, 68, 68, 0.3)'
      }}>
        <div style={{ textAlign: 'center', color: '#ef4444' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>⚠️</div>
          <div style={{ fontSize: '0.8rem' }}>Data unavailable</div>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '8px',
              padding: '4px 8px',
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              borderRadius: '4px',
              color: '#ef4444',
              fontSize: '0.7rem',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const chartBars = generateChartBars();
  
  // Use marketData if available, otherwise calculate from chart data
  const symbolData = marketData?.[symbol];
  const priceChange = symbolData?.priceChangePercent !== undefined 
    ? symbolData.priceChangePercent 
    : (priceData.length > 1 ? ((priceData[priceData.length - 1] - priceData[0]) / priceData[0]) * 100 : 0);

  return (
    <div style={{
      height,
      background: 'linear-gradient(135deg, rgba(26, 26, 26, 0.4) 0%, rgba(26, 26, 26, 0.2) 100%)',
      borderRadius: '12px',
      padding: '16px',
      position: 'relative',
      overflow: 'hidden',
      border: '1px solid rgba(255, 255, 255, 0.05)',
      boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.2)'
    }}>


      {/* Chart bars */}
      <div style={{
        display: 'flex',
        alignItems: 'end',
        height: '100%',
        gap: '2px',
        paddingTop: '32px'
      }}>
        {chartBars.map((bar, index) => (
          <div
            key={index}
            style={{
              flex: 1,
              height: bar.height,
              background: bar.isLatest ? 
                'linear-gradient(to top, #22c55e, #16a34a)' : 
                'linear-gradient(to top, #3b82f6, #2563eb)',
              borderRadius: '2px',
              minHeight: '4px',
              transition: 'all 0.3s ease',
              position: 'relative'
            }}
            title={`${bar.price.toFixed(2)}`}
          >
            {bar.isLatest && (
              <div style={{
                position: 'absolute',
                top: '-4px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: '6px',
                height: '6px',
                background: '#ffffff',
                borderRadius: '50%',
                border: '1px solid #22c55e'
              }} />
            )}
          </div>
        ))}
      </div>


    </div>
  );
};

export default WorkingChart;
