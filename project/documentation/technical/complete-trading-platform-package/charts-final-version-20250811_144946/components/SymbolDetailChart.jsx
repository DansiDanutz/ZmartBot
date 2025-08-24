// SymbolDetailChart - Detailed chart view for individual symbols using ZmartChart
// Based on zmart-charts-kit with enhanced features for detailed analysis
// ---------------------------------------------------------------------------------

import React, { useState, useEffect } from "react";
import ZmartChart from "./ZmartChart";

const SymbolDetailChart = ({ symbol, onBack }) => {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol}`);
        if (response.ok) {
          const data = await response.json();
          setMarketData(data);
        }
      } catch (error) {
        console.error('Error fetching market data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchMarketData();
    }
  }, [symbol]);

  const formatNumber = (num, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(num);
  };

  const formatVolume = (num) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
    return num.toFixed(2);
  };

  return (
    <div className="symbol-detail-container">
      {/* Header */}
      <div className="symbol-detail-header">
        <button onClick={onBack} className="back-button">
          ← Back to Dashboard
        </button>
        <h1 className="symbol-title">{symbol}</h1>
      </div>

      {/* Market Data Summary */}
      {marketData && (
        <div className="market-data-summary">
          <div className="market-data-grid">
            <div className="market-data-card">
              <div className="market-data-label">Current Price</div>
              <div className="market-data-value price">
                {formatCurrency(parseFloat(marketData.lastPrice))}
              </div>
              <div className={`market-data-change ${parseFloat(marketData.priceChangePercent) >= 0 ? 'positive' : 'negative'}`}>
                {parseFloat(marketData.priceChangePercent) >= 0 ? '+' : ''}{parseFloat(marketData.priceChangePercent).toFixed(2)}%
              </div>
            </div>
            
            <div className="market-data-card">
              <div className="market-data-label">24h High</div>
              <div className="market-data-value">
                {formatCurrency(parseFloat(marketData.highPrice))}
              </div>
            </div>
            
            <div className="market-data-card">
              <div className="market-data-label">24h Low</div>
              <div className="market-data-value">
                {formatCurrency(parseFloat(marketData.lowPrice))}
              </div>
            </div>
            
            <div className="market-data-card">
              <div className="market-data-label">24h Volume</div>
              <div className="market-data-value">
                {formatVolume(parseFloat(marketData.volume))}
              </div>
            </div>
            
            <div className="market-data-card">
              <div className="market-data-label">Price Change</div>
              <div className={`market-data-value ${parseFloat(marketData.priceChange) >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(Math.abs(parseFloat(marketData.priceChange)))}
              </div>
            </div>
            
            <div className="market-data-card">
              <div className="market-data-label">Weighted Avg</div>
              <div className="market-data-value">
                {formatCurrency(parseFloat(marketData.weightedAvgPrice))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chart Section */}
      <div className="chart-section">
        <div className="chart-header">
          <h2>Price Chart</h2>
          <div className="chart-controls">
            <span className="chart-info">Professional crypto chart with EMAs and Golden/Death Cross markers</span>
          </div>
        </div>
        
        <div className="chart-container">
          <ZmartChart
            symbol={symbol}
            height={400}
            chartType="candlestick"
            showEMAs={true}
            showCrosses={true}
            showGrid={true}
            showTooltip={true}
          />
        </div>
      </div>

      {/* Additional Analysis */}
      <div className="analysis-section">
        <div className="analysis-grid">
          <div className="analysis-card">
            <h3>Technical Indicators</h3>
            <div className="indicator-list">
              <div className="indicator-item">
                <span className="indicator-name">EMA 9</span>
                <span className="indicator-color" style={{ backgroundColor: '#60a5fa' }}></span>
              </div>
              <div className="indicator-item">
                <span className="indicator-name">EMA 21</span>
                <span className="indicator-color" style={{ backgroundColor: '#fbbf24' }}></span>
              </div>
              <div className="indicator-item">
                <span className="indicator-name">EMA 50</span>
                <span className="indicator-color" style={{ backgroundColor: '#a78bfa' }}></span>
              </div>
              <div className="indicator-item">
                <span className="indicator-name">EMA 200</span>
                <span className="indicator-color" style={{ backgroundColor: '#eab308' }}></span>
              </div>
            </div>
          </div>
          
          <div className="analysis-card">
            <h3>Cross Signals</h3>
            <div className="signal-list">
              <div className="signal-item">
                <span className="signal-name">Golden Cross</span>
                <span className="signal-color" style={{ backgroundColor: '#10b981' }}></span>
                <span className="signal-desc">EMA 50 crosses above EMA 200 (bullish)</span>
              </div>
              <div className="signal-item">
                <span className="signal-name">Death Cross</span>
                <span className="signal-color" style={{ backgroundColor: '#ef4444' }}></span>
                <span className="signal-desc">EMA 50 crosses below EMA 200 (bearish)</span>
              </div>
            </div>
          </div>
          
          <div className="analysis-card">
            <h3>Data Source</h3>
            <div className="source-info">
              <p>Live data from Binance API</p>
              <p>Daily candlestick data</p>
              <p>Real-time price updates</p>
              <p>Professional charting with Recharts</p>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .symbol-detail-container {
          padding: 2rem;
          max-width: 1400px;
          margin: 0 auto;
          background: var(--background);
          min-height: 100vh;
        }

        .symbol-detail-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .back-button {
          padding: 0.5rem 1rem;
          background: rgba(59, 130, 246, 0.1);
          border: 1px solid rgba(59, 130, 246, 0.3);
          border-radius: 8px;
          color: #3b82f6;
          cursor: pointer;
          transition: all 0.2s;
        }

        .back-button:hover {
          background: rgba(59, 130, 246, 0.2);
        }

        .symbol-title {
          font-size: 2rem;
          font-weight: 700;
          color: #ffffff;
          margin: 0;
        }

        .market-data-summary {
          margin-bottom: 2rem;
        }

        .market-data-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .market-data-card {
          background: rgba(26, 26, 26, 0.6);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.5rem;
          backdrop-filter: blur(10px);
        }

        .market-data-label {
          font-size: 0.875rem;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
        }

        .market-data-value {
          font-size: 1.25rem;
          font-weight: 600;
          color: #ffffff;
          margin-bottom: 0.25rem;
        }

        .market-data-value.price {
          font-size: 1.5rem;
          font-weight: 700;
        }

        .market-data-change {
          font-size: 0.875rem;
          font-weight: 500;
        }

        .market-data-change.positive {
          color: #10b981;
        }

        .market-data-change.negative {
          color: #ef4444;
        }

        .market-data-value.positive {
          color: #10b981;
        }

        .market-data-value.negative {
          color: #ef4444;
        }

        .chart-section {
          margin-bottom: 2rem;
        }

        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .chart-header h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #ffffff;
          margin: 0;
        }

        .chart-info {
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .chart-container {
          background: rgba(26, 26, 26, 0.3);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1rem;
          backdrop-filter: blur(10px);
        }

        .analysis-section {
          margin-top: 2rem;
        }

        .analysis-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .analysis-card {
          background: rgba(26, 26, 26, 0.6);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.5rem;
          backdrop-filter: blur(10px);
        }

        .analysis-card h3 {
          font-size: 1.125rem;
          font-weight: 600;
          color: #ffffff;
          margin: 0 0 1rem 0;
        }

        .indicator-list, .signal-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .indicator-item, .signal-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .indicator-name, .signal-name {
          font-size: 0.875rem;
          color: #ffffff;
          font-weight: 500;
          min-width: 80px;
        }

        .indicator-color, .signal-color {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .signal-desc {
          font-size: 0.75rem;
          color: var(--text-secondary);
          flex: 1;
        }

        .source-info p {
          font-size: 0.875rem;
          color: var(--text-secondary);
          margin: 0.5rem 0;
        }

        @media (max-width: 768px) {
          .symbol-detail-container {
            padding: 1rem;
          }

          .symbol-title {
            font-size: 1.5rem;
          }

          .market-data-grid {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          }

          .analysis-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default SymbolDetailChart;
