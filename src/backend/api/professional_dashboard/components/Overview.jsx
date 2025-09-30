import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Overview = () => {
  const [symbolsData, setSymbolsData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // All 10 active symbols
  const symbols = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
    'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT'
  ];

  const fetchSymbolData = async (symbol) => {
    try {
      const response = await axios.get(`/api/v1/binance/ticker/24hr?symbol=${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching data for ${symbol}:`, error);
      return null;
    }
  };

  const fetchAllSymbolsData = async () => {
    setLoading(true);
    const newData = {};
    
    // Fetch data for all symbols concurrently
    const promises = symbols.map(async (symbol) => {
      const data = await fetchSymbolData(symbol);
      if (data) {
        newData[symbol] = data;
      }
    });
    
    await Promise.all(promises);
    setSymbolsData(newData);
    setLoading(false);
  };

  useEffect(() => {
    fetchAllSymbolsData();
    
    // Update every 15 seconds
    const interval = setInterval(fetchAllSymbolsData, 15000);
    return () => clearInterval(interval);
  }, []);

  const formatNumber = (num) => {
    if (!num) return 'N/A';
    return parseFloat(num).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const formatVolume = (volume) => {
    if (!volume) return 'N/A';
    const vol = parseFloat(volume);
    if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`;
    if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`;
    if (vol >= 1e3) return `${(vol / 1e3).toFixed(2)}K`;
    return vol.toFixed(2);
  };

  const getPriceChangeColor = (change) => {
    if (!change) return 'text-gray-400';
    const changeNum = parseFloat(change);
    return changeNum >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getPriceChangeIcon = (change) => {
    if (!change) return '➡️';
    const changeNum = parseFloat(change);
    return changeNum >= 0 ? '📈' : '📉';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading real-time market data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-red-400 font-medium mb-2">Connection Error</p>
          <p className="text-gray-400 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Market Overview</h1>
        <div className="flex items-center gap-2">
          <span className="text-green-400 text-sm">Live Data</span>
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Price Data Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {symbols.map((symbol) => {
          const data = symbolsData[symbol];
          if (!data) return null;

          return (
            <div key={symbol} className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300">
              {/* Symbol Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm font-bold">
                      {symbol.replace('USDT', '').slice(0, 3)}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{symbol}</h3>
                    <p className="text-gray-400 text-xs">Real-time data</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-400">Last Updated</div>
                  <div className="text-xs text-white">
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
              </div>

              {/* Current Price */}
              <div className="mb-4">
                <div className="text-2xl font-bold text-white mb-1">
                  ${formatNumber(data.lastPrice)}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getPriceChangeIcon(data.priceChangePercent)}</span>
                  <span className={`text-sm font-medium ${getPriceChangeColor(data.priceChangePercent)}`}>
                    {parseFloat(data.priceChangePercent || 0).toFixed(2)}%
                  </span>
                  <span className={`text-sm ${getPriceChangeColor(data.priceChangePercent)}`}>
                    ${formatNumber(Math.abs(parseFloat(data.priceChange || 0)))}
                  </span>
                </div>
              </div>

              {/* Market Data */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">24h High</span>
                  <span className="text-green-400 font-medium">${formatNumber(data.highPrice)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">24h Low</span>
                  <span className="text-red-400 font-medium">${formatNumber(data.lowPrice)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">24h Change</span>
                  <span className={`font-medium ${getPriceChangeColor(data.priceChangePercent)}`}>
                    {parseFloat(data.priceChangePercent || 0).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Volume (24h)</span>
                  <span className="text-white font-medium">{formatVolume(data.volume)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Quote Volume</span>
                  <span className="text-white font-medium">{formatVolume(data.quoteVolume)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Count</span>
                  <span className="text-white font-medium">{parseInt(data.count || 0).toLocaleString()}</span>
                </div>
              </div>

              {/* Status Indicator */}
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Status</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-green-400">Live</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Market Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Symbols</span>
              <span className="text-white font-medium">{symbols.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Gainers</span>
              <span className="text-green-400 font-medium">
                {symbols.filter(symbol => {
                  const data = symbolsData[symbol];
                  return data && parseFloat(data.priceChangePercent || 0) > 0;
                }).length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Losers</span>
              <span className="text-red-400 font-medium">
                {symbols.filter(symbol => {
                  const data = symbolsData[symbol];
                  return data && parseFloat(data.priceChangePercent || 0) < 0;
                }).length}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Top Gainers</h3>
          <div className="space-y-2">
            {symbols
              .filter(symbol => {
                const data = symbolsData[symbol];
                return data && parseFloat(data.priceChangePercent || 0) > 0;
              })
              .sort((a, b) => {
                const dataA = symbolsData[a];
                const dataB = symbolsData[b];
                return parseFloat(dataB?.priceChangePercent || 0) - parseFloat(dataA?.priceChangePercent || 0);
              })
              .slice(0, 3)
              .map((symbol) => {
                const data = symbolsData[symbol];
                return (
                  <div key={symbol} className="flex justify-between items-center">
                    <span className="text-white text-sm">{symbol}</span>
                    <span className="text-green-400 text-sm font-medium">
                      +{parseFloat(data?.priceChangePercent || 0).toFixed(2)}%
                    </span>
                  </div>
                );
              })}
          </div>
        </div>

        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Top Losers</h3>
          <div className="space-y-2">
            {symbols
              .filter(symbol => {
                const data = symbolsData[symbol];
                return data && parseFloat(data.priceChangePercent || 0) < 0;
              })
              .sort((a, b) => {
                const dataA = symbolsData[a];
                const dataB = symbolsData[b];
                return parseFloat(dataA?.priceChangePercent || 0) - parseFloat(dataB?.priceChangePercent || 0);
              })
              .slice(0, 3)
              .map((symbol) => {
                const data = symbolsData[symbol];
                return (
                  <div key={symbol} className="flex justify-between items-center">
                    <span className="text-white text-sm">{symbol}</span>
                    <span className="text-red-400 text-sm font-medium">
                      {parseFloat(data?.priceChangePercent || 0).toFixed(2)}%
                    </span>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overview;
