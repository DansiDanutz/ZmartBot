"""Data Manager for handling multiple data sources and real-time feeds."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable
import websockets
import ccxt.async_support as ccxt
import aiohttp
from .models import MarketData, TechnicalIndicators, TimeFrame

logger = logging.getLogger(__name__)


class DataManager:
    """Manages real-time market data from multiple sources."""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.market_data: Dict[str, MarketData] = {}
        self.technical_data: Dict[str, Dict[TimeFrame, TechnicalIndicators]] = {}
        self.exchanges = {}
        self.websocket_connections = {}
        self.is_running = False
        
    async def initialize(self):
        """Initialize data sources and connections."""
        try:
            # Initialize Binance exchange
            self.exchanges['binance'] = ccxt.binance({
                'apiKey': '',  # Add your API key
                'secret': '',  # Add your secret
                'sandbox': False,
                'enableRateLimit': True,
            })
            
            logger.info("Data Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Data Manager: {e}")
            raise
    
    async def start(self):
        """Start data collection from all sources."""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting Data Manager...")
        
        # Start WebSocket connections
        asyncio.create_task(self._start_binance_websocket())
        
        # Start periodic technical analysis updates
        asyncio.create_task(self._update_technical_indicators())
        
    async def stop(self):
        """Stop all data collection."""
        self.is_running = False
        logger.info("Stopping Data Manager...")
        
        # Close WebSocket connections
        for ws in self.websocket_connections.values():
            if ws and not ws.closed:
                await ws.close()
        
        # Close exchange connections
        for exchange in self.exchanges.values():
            await exchange.close()
    
    def subscribe_symbol(self, symbol: str, callback: Callable):
        """Subscribe to real-time data for a symbol."""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = set()
        self.subscribers[symbol].add(callback)
        logger.info(f"Subscribed to {symbol}, total subscribers: {len(self.subscribers[symbol])}")
    
    def unsubscribe_symbol(self, symbol: str, callback: Callable):
        """Unsubscribe from symbol data."""
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)
            if not self.subscribers[symbol]:
                del self.subscribers[symbol]
            logger.info(f"Unsubscribed from {symbol}")
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get latest market data for a symbol."""
        return self.market_data.get(symbol)
    
    async def get_technical_data(self, symbol: str, timeframe: TimeFrame) -> Optional[TechnicalIndicators]:
        """Get technical indicators for a symbol and timeframe."""
        if symbol in self.technical_data:
            return self.technical_data[symbol].get(timeframe)
        return None
    
    async def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Get historical OHLCV data."""
        try:
            exchange = self.exchanges.get('binance')
            if not exchange:
                raise Exception("Exchange not initialized")
            
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return [
                {
                    'timestamp': datetime.fromtimestamp(candle[0] / 1000),
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
                for candle in ohlcv
            ]
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return []
    
    async def _start_binance_websocket(self):
        """Start Binance WebSocket connection for real-time data."""
        while self.is_running:
            try:
                # Get all subscribed symbols
                symbols = list(self.subscribers.keys())
                if not symbols:
                    await asyncio.sleep(5)
                    continue
                
                # Create stream names for ticker data
                streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
                stream_url = f"wss://stream.binance.com:9443/ws/{'/'.join(streams)}"
                
                async with websockets.connect(stream_url) as websocket:
                    self.websocket_connections['binance'] = websocket
                    logger.info(f"Connected to Binance WebSocket for {len(symbols)} symbols")
                    
                    async for message in websocket:
                        if not self.is_running:
                            break
                        
                        try:
                            data = json.loads(message)
                            await self._process_binance_ticker(data)
                        except Exception as e:
                            logger.error(f"Error processing WebSocket message: {e}")
                            
            except Exception as e:
                logger.error(f"Binance WebSocket error: {e}")
                await asyncio.sleep(5)  # Reconnect after 5 seconds
    
    async def _process_binance_ticker(self, data: Dict):
        """Process Binance ticker data."""
        try:
            symbol = data['s']
            
            market_data = MarketData(
                symbol=symbol,
                price=float(data['c']),
                volume=float(data['v']),
                timestamp=datetime.fromtimestamp(int(data['E']) / 1000),
                bid=float(data['b']),
                ask=float(data['a']),
                high_24h=float(data['h']),
                low_24h=float(data['l']),
                change_24h=float(data['P']),
                change_percent_24h=float(data['p'])
            )
            
            # Store market data
            self.market_data[symbol] = market_data
            
            # Notify subscribers
            if symbol in self.subscribers:
                for callback in self.subscribers[symbol]:
                    try:
                        await callback(market_data)
                    except Exception as e:
                        logger.error(f"Error in subscriber callback for {symbol}: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing ticker data: {e}")
    
    async def _update_technical_indicators(self):
        """Periodically update technical indicators."""
        while self.is_running:
            try:
                symbols = list(self.subscribers.keys())
                
                for symbol in symbols:
                    for timeframe in TimeFrame:
                        try:
                            indicators = await self._calculate_technical_indicators(symbol, timeframe)
                            if indicators:
                                if symbol not in self.technical_data:
                                    self.technical_data[symbol] = {}
                                self.technical_data[symbol][timeframe] = indicators
                        except Exception as e:
                            logger.error(f"Error calculating indicators for {symbol} {timeframe}: {e}")
                
                # Update every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in technical indicators update: {e}")
                await asyncio.sleep(30)
    
    async def _calculate_technical_indicators(self, symbol: str, timeframe: TimeFrame) -> Optional[TechnicalIndicators]:
        """Calculate technical indicators for a symbol and timeframe."""
        try:
            # Get historical data
            historical = await self.get_historical_data(symbol, timeframe.value, 100)
            if len(historical) < 50:  # Need enough data for indicators
                return None
            
            import pandas as pd
            import talib
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(historical)
            
            # Calculate indicators
            rsi = talib.RSI(df['close'].values, timeperiod=14)[-1]
            macd, macd_signal, macd_hist = talib.MACD(df['close'].values)
            bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'].values)
            sma_20 = talib.SMA(df['close'].values, timeperiod=20)[-1]
            sma_50 = talib.SMA(df['close'].values, timeperiod=50)[-1]
            ema_12 = talib.EMA(df['close'].values, timeperiod=12)[-1]
            ema_26 = talib.EMA(df['close'].values, timeperiod=26)[-1]
            volume_sma = talib.SMA(df['volume'].values, timeperiod=20)[-1]
            
            return TechnicalIndicators(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now(),
                rsi=float(rsi) if not pd.isna(rsi) else None,
                macd=float(macd[-1]) if not pd.isna(macd[-1]) else None,
                macd_signal=float(macd_signal[-1]) if not pd.isna(macd_signal[-1]) else None,
                macd_histogram=float(macd_hist[-1]) if not pd.isna(macd_hist[-1]) else None,
                bb_upper=float(bb_upper[-1]) if not pd.isna(bb_upper[-1]) else None,
                bb_middle=float(bb_middle[-1]) if not pd.isna(bb_middle[-1]) else None,
                bb_lower=float(bb_lower[-1]) if not pd.isna(bb_lower[-1]) else None,
                sma_20=float(sma_20) if not pd.isna(sma_20) else None,
                sma_50=float(sma_50) if not pd.isna(sma_50) else None,
                ema_12=float(ema_12) if not pd.isna(ema_12) else None,
                ema_26=float(ema_26) if not pd.isna(ema_26) else None,
                volume_sma=float(volume_sma) if not pd.isna(volume_sma) else None
            )
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return None

