// ChartCard - Responsive chart card component for mobile and desktop
// Handles chart loading, errors, and responsive design
// ---------------------------------------------------------------------------------

import React, { useState, useEffect } from "react";
import WorkingChart from "./WorkingChart";

const ChartCard = ({ 
  symbol, 
  marketData, 
  onViewDetail,
  chartType = "candlestick",
  autoRefresh = false
}) => {
  console.log(`🔍 ChartCard component created for symbol: ${symbol}`);
  console.log(`🔍 onViewDetail prop type: ${typeof onViewDetail}`);
  console.log(`🔍 marketData for ${symbol}:`, marketData ? marketData[symbol] : 'undefined');
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
                const [chartHeight, setChartHeight] = useState(100);

  const data = marketData[symbol];

  // Responsive chart height
  useEffect(() => {
    const updateChartHeight = () => {
      const isMobile = window.innerWidth < 768;
      const isTablet = window.innerWidth < 1024;
      
                      if (isMobile) {
                  setChartHeight(80);
                } else if (isTablet) {
                  setChartHeight(90);
                } else {
                  setChartHeight(100);
                }
    };

    updateChartHeight();
    window.addEventListener('resize', updateChartHeight);
    return () => window.removeEventListener('resize', updateChartHeight);
  }, []);

  // Simple loading state
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  const formatNumber = (num, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  };

  const formatVolume = (num) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toFixed(2);
  };

  return (
    <div className="chart-card">
      <div className="chart-card-header">
        <h4 className="symbol-name">{symbol}</h4>
        <div className="price-info">
          <span className="current-price">
            ${data ? formatNumber(data.price) : '0.00'}
          </span>
          <span className={`price-change ${data?.priceChangePercent > 0 ? 'positive' : data?.priceChangePercent < 0 ? 'negative' : 'neutral'}`}>
            {data ? (data.priceChangePercent > 0 ? '+' : '') + formatNumber(data.priceChangePercent, 2) + '%' : '0.00%'}
          </span>
        </div>
      </div>
      
      <div className="chart-card-body">
        <div className="market-metrics">
          <div className="metric">
            <span className="metric-label">24h High:</span>
            <span className="metric-value">
              ${data ? formatNumber(data.high24h) : '0.00'}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">24h Low:</span>
            <span className="metric-value">
              ${data ? formatNumber(data.low24h) : '0.00'}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Volume:</span>
            <span className="metric-value">
              ${data ? formatVolume(data.quoteVolume) : '0'}M
            </span>
          </div>
        </div>
        
        {/* Chart Container */}
        <div className="chart-container">
                              <div className="zmart-chart-wrapper">
                      <WorkingChart
                        symbol={symbol}
                        height={chartHeight}
                        marketData={marketData}
                      />
                    </div>
        </div>
      </div>
      
                <div className="chart-card-footer">
            <button 
              style={{
                width: '100%',
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                color: '#8b5cf6',
                padding: '0.25rem',
                borderRadius: '8px',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                letterSpacing: '0.25px',
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                textAlign: 'center'
              }}
              onClick={() => {
                console.log(`🔘 View Detailed Chart clicked for symbol: ${symbol}`);
                if (onViewDetail) {
                  console.log(`🔘 Calling onViewDetail with symbol: ${symbol}`);
                  onViewDetail(symbol);
                } else {
                  console.error(`❌ onViewDetail function is not available`);
                }
              }}
            >
              📊 View Detailed Chart
            </button>
          </div>

      <style jsx>{`
        .chart-card {
          background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(26, 26, 26, 0.7) 100%);
          border: 1px solid rgba(139, 92, 246, 0.15);
          border-radius: 16px;
          padding: 0.5rem;
          backdrop-filter: blur(20px);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          min-height: 180px;
          display: flex;
          flex-direction: column;
          position: relative;
          overflow: hidden;
        }

        .chart-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, #8b5cf6, #06b6d4, #10b981);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .chart-card:hover {
          transform: translateY(-4px) scale(1.02);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(139, 92, 246, 0.2);
          border-color: rgba(139, 92, 246, 0.4);
        }

        .chart-card:hover::before {
          opacity: 1;
        }

        .chart-card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.375rem;
          gap: 0.375rem;
          position: relative;
        }

        .symbol-name {
          font-size: 1.1rem;
          font-weight: 700;
          color: #ffffff;
          margin: 0;
          flex: 1;
          letter-spacing: 0.5px;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }

        .price-info {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 0.25rem;
        }

        .current-price {
          font-size: 1.2rem;
          font-weight: 800;
          color: #ffffff;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
          letter-spacing: 0.5px;
        }

        .price-change {
          font-size: 0.9rem;
          font-weight: 600;
          padding: 0.25rem 0.75rem;
          border-radius: 6px;
          letter-spacing: 0.25px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .price-change.positive {
          color: #10b981;
          background: rgba(16, 185, 129, 0.1);
        }

        .price-change.negative {
          color: #ef4444;
          background: rgba(239, 68, 68, 0.1);
        }

        .price-change.neutral {
          color: #9ca3af;
          background: rgba(156, 163, 175, 0.1);
        }

        .chart-card-body {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .market-metrics {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.25rem;
          font-size: 0.65rem;
          margin-bottom: 0.375rem;
          padding: 0.25rem;
          background: rgba(255, 255, 255, 0.03);
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .metric {
          display: flex;
          flex-direction: column;
          gap: 0.375rem;
          text-align: center;
        }

        .metric-label {
          color: rgba(255, 255, 255, 0.6);
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .metric-value {
          color: #ffffff;
          font-weight: 600;
          font-size: 0.85rem;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }

        .chart-container {
          flex: 1;
          min-height: 100px;
          position: relative;
          border-radius: 12px;
          overflow: hidden;
          background: linear-gradient(135deg, rgba(26, 26, 26, 0.4) 0%, rgba(26, 26, 26, 0.2) 100%);
          border: 1px solid rgba(255, 255, 255, 0.05);
          box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
          z-index: 1;
          pointer-events: none;
        }

        .chart-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 0.5rem;
          color: var(--text-muted);
          font-size: 0.875rem;
        }

        .loading-spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(139, 92, 246, 0.3);
          border-top: 2px solid #8b5cf6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .chart-error {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 0.5rem;
          color: #ef4444;
          font-size: 0.875rem;
          text-align: center;
          padding: 1rem;
        }

        .error-icon {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }

        .retry-button {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          color: #ef4444;
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          font-size: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .retry-button:hover {
          background: rgba(239, 68, 68, 0.2);
        }

        .zmart-chart-wrapper {
          height: 100%;
          width: 100%;
        }

        .chart-card-footer {
          margin-top: 0.375rem;
        }

        .view-chart-btn {
          width: 100%;
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%);
          border: 1px solid rgba(139, 92, 246, 0.3);
          color: #8b5cf6;
          padding: 0.25rem;
          border-radius: 8px;
          font-size: 0.75rem;
          font-weight: 600;
          cursor: pointer !important;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          letter-spacing: 0.25px;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
          position: relative;
          z-index: 999 !important;
          pointer-events: auto !important;
          user-select: none;
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
        }

        .view-chart-btn:hover {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(6, 182, 212, 0.25) 100%);
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
          border-color: rgba(139, 92, 246, 0.5);
        }

        .view-chart-btn:active {
          transform: translateY(0);
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.4) 0%, rgba(6, 182, 212, 0.4) 100%);
          box-shadow: 0 4px 10px rgba(139, 92, 246, 0.4);
        }

                            /* Mobile Responsive */
                    @media (max-width: 768px) {
                      .chart-card {
                        padding: 0.5rem;
                        min-height: 160px;
                      }

                      .chart-card-header {
                        margin-bottom: 0.25rem;
                      }

                      .symbol-name {
                        font-size: 1rem;
                      }

                      .current-price {
                        font-size: 1.1rem;
                      }

                      .market-metrics {
                        font-size: 0.65rem;
                        gap: 0.25rem;
                      }

                      .chart-container {
                        min-height: 80px;
                      }

                      .chart-card-body {
                        gap: 0.25rem;
                      }
                    }

                            /* Tablet Responsive */
                    @media (min-width: 769px) and (max-width: 1024px) {
                      .chart-card {
                        padding: 0.625rem;
                        min-height: 170px;
                      }

                      .chart-container {
                        min-height: 90px;
                      }
                    }

                            /* Desktop Large */
                    @media (min-width: 1025px) {
                      .chart-card {
                        padding: 0.75rem;
                        min-height: 180px;
                      }

                      .chart-container {
                        min-height: 100px;
                      }
                    }
      `}</style>
    </div>
  );
};

export default ChartCard;
