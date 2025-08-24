#!/usr/bin/env python3
"""
Real-Time Market Data Connector
Connects dynamic weight adjuster to real-time market data for live optimization
"""

import asyncio
import logging
import aiohttp
import websockets
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np

from src.config.settings import settings
from src.services.dynamic_weight_adjuster import DynamicWeightAdjuster
from src.services.calibrated_scoring_service import CalibratedScoringService

logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    """Real-time market data point"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    source: str
    data_type: str  # price, volume, orderbook, etc.

@dataclass
class MarketDataStream:
    """Market data stream configuration"""
    symbol: str
    exchange: str
    data_types: List[str]
    update_frequency: float  # seconds
    is_active: bool = True

class RealTimeMarketDataConnector:
    """
    Real-time market data connector for dynamic weight adjustment
    """
    
    def __init__(self):
        """Initialize the real-time market data connector"""
        self.dynamic_weight_adjuster = DynamicWeightAdjuster()
        self.integrated_scoring_system = CalibratedScoringService()
        
        # Market data streams
        self.active_streams: Dict[str, MarketDataStream] = {}
        self.market_data_cache: Dict[str, List[MarketDataPoint]] = {}
        
        # Real-time data sources
        self.data_sources = {
            'binance': {
                'base_url': 'wss://stream.binance.com:9443/ws/',
                'rest_url': 'https://api.binance.com/api/v3/',
                'supported_symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
            },
            'kucoin': {
                'base_url': 'wss://ws-api.kucoin.com/',
                'rest_url': 'https://api.kucoin.com/api/v1/',
                'supported_symbols': ['BTC-USDT', 'ETH-USDT', 'BNB-USDT', 'ADA-USDT', 'SOL-USDT']
            }
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_data_points': 0,
            'active_streams': 0,
            'data_latency_ms': 0.0,
            'update_frequency': 0.0,
            'last_updated': datetime.now()
        }
        
        # Callbacks for real-time updates
        self.update_callbacks: List[Callable] = []
        
        # Connection state
        self._running = False
        self._websocket_connections: Dict[str, Any] = {}
        
        logger.info("Real-Time Market Data Connector initialized")
    
    async def start(self):
        """Start the real-time market data connector"""
        if self._running:
            logger.warning("Real-time market data connector already running")
            return
        
        logger.info("Starting real-time market data connector")
        self._running = True
        
        try:
            # Initialize default streams
            await self._initialize_default_streams()
            
            # Start WebSocket connections
            await self._start_websocket_connections()
            
            # Start data processing loop
            asyncio.create_task(self._data_processing_loop())
            
            logger.info("Real-time market data connector started successfully")
            
        except Exception as e:
            logger.error(f"Error starting real-time market data connector: {e}")
            self._running = False
            raise
    
    async def stop(self):
        """Stop the real-time market data connector"""
        logger.info("Stopping real-time market data connector")
        self._running = False
        
        # Close WebSocket connections
        for connection in self._websocket_connections.values():
            if hasattr(connection, 'close'):
                await connection.close()
        
        self._websocket_connections.clear()
        logger.info("Real-time market data connector stopped")
    
    async def add_market_data_stream(self, symbol: str, exchange: str = 'binance', 
                                   data_types: Optional[List[str]] = None,
                                   update_frequency: float = 1.0) -> bool:
        """Add a new market data stream"""
        try:
            if data_types is None:
                data_types = ['price', 'volume']
            
            stream = MarketDataStream(
                symbol=symbol,
                exchange=exchange,
                data_types=data_types,
                update_frequency=update_frequency
            )
            
            self.active_streams[symbol] = stream
            self.market_data_cache[symbol] = []
            
            # Start stream if connector is running
            if self._running:
                await self._start_stream(stream)
            
            logger.info(f"Added market data stream for {symbol} on {exchange}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding market data stream for {symbol}: {e}")
            return False
    
    async def remove_market_data_stream(self, symbol: str) -> bool:
        """Remove a market data stream"""
        try:
            if symbol in self.active_streams:
                stream = self.active_streams[symbol]
                stream.is_active = False
                
                # Close WebSocket connection if exists
                if symbol in self._websocket_connections:
                    connection = self._websocket_connections[symbol]
                    if hasattr(connection, 'close'):
                        await connection.close()
                    del self._websocket_connections[symbol]
                
                del self.active_streams[symbol]
                if symbol in self.market_data_cache:
                    del self.market_data_cache[symbol]
                
                logger.info(f"Removed market data stream for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing market data stream for {symbol}: {e}")
            return False
    
    async def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time market data for a symbol"""
        try:
            if symbol not in self.market_data_cache:
                return None
            
            cache = self.market_data_cache[symbol]
            if not cache:
                return None
            
            # Get latest data point
            latest_data = cache[-1]
            
            # Calculate additional metrics
            price_data = [point.price for point in cache[-100:] if point.data_type == 'price']
            volume_data = [point.volume for point in cache[-100:] if point.data_type == 'volume']
            
            # Calculate volatility
            volatility = np.std(price_data) / np.mean(price_data) if len(price_data) > 1 else 0.0
            
            # Calculate volume trend
            volume_trend = np.mean(volume_data[-10:]) / np.mean(volume_data[-50:]) if len(volume_data) >= 50 else 1.0
            
            return {
                'symbol': symbol,
                'current_price': latest_data.price,
                'current_volume': latest_data.volume,
                'timestamp': latest_data.timestamp.isoformat(),
                'volatility': volatility,
                'volume_trend': volume_trend,
                'data_points_count': len(cache),
                'source': latest_data.source
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time data for {symbol}: {e}")
            return None
    
    async def register_update_callback(self, callback: Callable):
        """Register a callback for real-time updates"""
        self.update_callbacks.append(callback)
        logger.info(f"Registered update callback: {callback.__name__}")
    
    async def _initialize_default_streams(self):
        """Initialize default market data streams"""
        default_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
        
        for symbol in default_symbols:
            await self.add_market_data_stream(
                symbol=symbol,
                exchange='binance',
                data_types=['price', 'volume'],
                update_frequency=1.0
            )
    
    async def _start_websocket_connections(self):
        """Start WebSocket connections for active streams"""
        for symbol, stream in self.active_streams.items():
            if stream.is_active:
                await self._start_stream(stream)
    
    async def _start_stream(self, stream: MarketDataStream):
        """Start a market data stream"""
        try:
            if stream.exchange == 'binance':
                await self._start_binance_stream(stream)
            elif stream.exchange == 'kucoin':
                await self._start_kucoin_stream(stream)
            else:
                logger.warning(f"Unsupported exchange: {stream.exchange}")
                
        except Exception as e:
            logger.error(f"Error starting stream for {stream.symbol}: {e}")
    
    async def _start_binance_stream(self, stream: MarketDataStream):
        """Start Binance WebSocket stream"""
        try:
            # Create WebSocket URL
            ws_url = f"{self.data_sources['binance']['base_url']}{stream.symbol.lower()}@ticker"
            
            # Connect to WebSocket
            websocket = await websockets.connect(ws_url)
            self._websocket_connections[stream.symbol] = websocket
            
            # Start message handling
            asyncio.create_task(self._handle_binance_messages(stream, websocket))
            
            logger.info(f"Started Binance WebSocket stream for {stream.symbol}")
            
        except Exception as e:
            logger.error(f"Error starting Binance stream for {stream.symbol}: {e}")
    
    async def _start_kucoin_stream(self, stream: MarketDataStream):
        """Start KuCoin WebSocket stream"""
        try:
            # KuCoin requires authentication for WebSocket
            # For now, use REST API polling
            asyncio.create_task(self._poll_kucoin_data(stream))
            
            logger.info(f"Started KuCoin data polling for {stream.symbol}")
            
        except Exception as e:
            logger.error(f"Error starting KuCoin stream for {stream.symbol}: {e}")
    
    async def _handle_binance_messages(self, stream: MarketDataStream, websocket):
        """Handle Binance WebSocket messages"""
        try:
            async for message in websocket:
                if not self._running or not stream.is_active:
                    break
                
                data = json.loads(message)
                
                # Extract price and volume data
                price = float(data.get('c', 0))  # Close price
                volume = float(data.get('v', 0))  # Volume
                
                # Create data points
                price_point = MarketDataPoint(
                    symbol=stream.symbol,
                    price=price,
                    volume=0.0,
                    timestamp=datetime.now(),
                    source='binance',
                    data_type='price'
                )
                
                volume_point = MarketDataPoint(
                    symbol=stream.symbol,
                    price=0.0,
                    volume=volume,
                    timestamp=datetime.now(),
                    source='binance',
                    data_type='volume'
                )
                
                # Add to cache
                await self._add_data_point(price_point)
                await self._add_data_point(volume_point)
                
        except Exception as e:
            logger.error(f"Error handling Binance messages for {stream.symbol}: {e}")
        finally:
            if websocket in self._websocket_connections.values():
                await websocket.close()
    
    async def _poll_kucoin_data(self, stream: MarketDataStream):
        """Poll KuCoin REST API for market data"""
        try:
            while self._running and stream.is_active:
                # Get ticker data
                ticker_data = await self._get_kucoin_ticker(stream.symbol)
                
                if ticker_data:
                    # Create data points
                    price_point = MarketDataPoint(
                        symbol=stream.symbol,
                        price=float(ticker_data.get('price', 0)),
                        volume=0.0,
                        timestamp=datetime.now(),
                        source='kucoin',
                        data_type='price'
                    )
                    
                    volume_point = MarketDataPoint(
                        symbol=stream.symbol,
                        price=0.0,
                        volume=float(ticker_data.get('size', 0)),
                        timestamp=datetime.now(),
                        source='kucoin',
                        data_type='volume'
                    )
                    
                    # Add to cache
                    await self._add_data_point(price_point)
                    await self._add_data_point(volume_point)
                
                # Wait for next update
                await asyncio.sleep(stream.update_frequency)
                
        except Exception as e:
            logger.error(f"Error polling KuCoin data for {stream.symbol}: {e}")
    
    async def _get_kucoin_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get KuCoin ticker data via REST API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.data_sources['kucoin']['rest_url']}market/orderbook/level1"
                params = {'symbol': symbol}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {})
                    else:
                        logger.warning(f"KuCoin API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting KuCoin ticker for {symbol}: {e}")
            return None
    
    async def _add_data_point(self, data_point: MarketDataPoint):
        """Add a data point to the cache"""
        try:
            symbol = data_point.symbol
            
            if symbol not in self.market_data_cache:
                self.market_data_cache[symbol] = []
            
            cache = self.market_data_cache[symbol]
            cache.append(data_point)
            
            # Keep only last 1000 data points
            if len(cache) > 1000:
                cache = cache[-1000:]
                self.market_data_cache[symbol] = cache
            
            # Update performance metrics
            self.performance_metrics['total_data_points'] += 1
            self.performance_metrics['last_updated'] = datetime.now()
            
            # Trigger callbacks
            await self._trigger_update_callbacks(data_point)
            
        except Exception as e:
            logger.error(f"Error adding data point: {e}")
    
    async def _trigger_update_callbacks(self, data_point: MarketDataPoint):
        """Trigger registered update callbacks"""
        try:
            for callback in self.update_callbacks:
                try:
                    await callback(data_point)
                except Exception as e:
                    logger.error(f"Error in update callback {callback.__name__}: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering update callbacks: {e}")
    
    async def _data_processing_loop(self):
        """Main data processing loop"""
        try:
            while self._running:
                # Process market data for dynamic weight adjustment
                await self._process_market_data_for_weights()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Wait before next processing cycle
                await asyncio.sleep(5.0)  # Process every 5 seconds
                
        except Exception as e:
            logger.error(f"Error in data processing loop: {e}")
    
    async def _process_market_data_for_weights(self):
        """Process market data for dynamic weight adjustment"""
        try:
            for symbol in self.active_streams.keys():
                real_time_data = await self.get_real_time_data(symbol)
                
                if real_time_data:
                    # Update dynamic weight adjuster with real-time data
                    await self._update_dynamic_weights(symbol, real_time_data)
                    
        except Exception as e:
            logger.error(f"Error processing market data for weights: {e}")
    
    async def _update_dynamic_weights(self, symbol: str, market_data: Dict[str, Any]):
        """Update dynamic weights based on real-time market data"""
        try:
            # Get current market regime
            market_regime = await self.dynamic_weight_adjuster.detect_market_regime(symbol)
            
            # Update endpoint performance based on real-time data
            volatility = market_data.get('volatility', 0.0)
            volume_trend = market_data.get('volume_trend', 1.0)
            
            # Update performance for relevant endpoints
            if volatility > 0.05:  # High volatility
                await self.dynamic_weight_adjuster.update_endpoint_performance(
                    'rapid_movements', True, 0.1, market_regime.regime_type, symbol
                )
            
            if volume_trend > 1.2:  # High volume trend
                await self.dynamic_weight_adjuster.update_endpoint_performance(
                    '24h_trade_volume_v2', True, 0.1, market_regime.regime_type, symbol
                )
            
            logger.debug(f"Updated dynamic weights for {symbol} based on real-time data")
            
        except Exception as e:
            logger.error(f"Error updating dynamic weights for {symbol}: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            self.performance_metrics['active_streams'] = len([
                stream for stream in self.active_streams.values() if stream.is_active
            ])
            
            # Calculate average data latency
            if self.market_data_cache:
                total_latency = 0
                count = 0
                
                for cache in self.market_data_cache.values():
                    if cache:
                        latest = cache[-1]
                        latency = (datetime.now() - latest.timestamp).total_seconds() * 1000
                        total_latency += latency
                        count += 1
                
                if count > 0:
                    self.performance_metrics['data_latency_ms'] = total_latency / count
            
            # Calculate update frequency
            if self.active_streams:
                frequencies = [stream.update_frequency for stream in self.active_streams.values()]
                self.performance_metrics['update_frequency'] = np.mean(frequencies)
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    async def get_connector_status(self) -> Dict[str, Any]:
        """Get real-time market data connector status"""
        return {
            'status': 'running' if self._running else 'stopped',
            'active_streams': len([s for s in self.active_streams.values() if s.is_active]),
            'total_streams': len(self.active_streams),
            'websocket_connections': len(self._websocket_connections),
            'performance_metrics': self.performance_metrics,
            'supported_exchanges': list(self.data_sources.keys()),
            'registered_callbacks': len(self.update_callbacks),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
real_time_market_data_connector = RealTimeMarketDataConnector() 