#!/usr/bin/env python3
"""
WebSocket Service for Real-time Data Streaming
Handles connections to KuCoin, Binance, and Cryptometer WebSocket APIs
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable
import websockets
import aiohttp
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class WebSocketMessage:
    """Standardized WebSocket message format"""
    source: str  # 'kucoin', 'binance', 'cryptometer'
    symbol: str
    data_type: str  # 'price', 'trade', 'orderbook', 'signal', 'score'
    data: Dict[str, Any]
    timestamp: float
    confidence: Optional[float] = None

class WebSocketManager:
    """Manages multiple WebSocket connections for real-time data"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.subscribers: List[Callable] = []
        self.running = False
        self.reconnect_attempts = {}
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        
        # KuCoin WebSocket configuration
        self.kucoin_ws_url = "wss://ws-api.kucoin.com/endpoint"
        self.kucoin_token_url = "https://api.kucoin.com/api/v1/bullet-public"
        
        # Binance WebSocket configuration
        self.binance_ws_url = "wss://stream.binance.com:9443/ws/"
        
        # Message queues for each source
        self.message_queues = {
            'kucoin': asyncio.Queue(),
            'binance': asyncio.Queue(),
            'cryptometer': asyncio.Queue()
        }
    
    async def start(self):
        """Start all WebSocket connections"""
        logger.info("🚀 Starting WebSocket Manager...")
        self.running = True
        
        # Start connection tasks
        tasks = [
            asyncio.create_task(self._connect_kucoin()),
            asyncio.create_task(self._connect_binance()),
            asyncio.create_task(self._message_processor()),
            asyncio.create_task(self._health_monitor())
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop all WebSocket connections"""
        logger.info("🛑 Stopping WebSocket Manager...")
        self.running = False
        
        # Close all connections
        for source, connection in self.connections.items():
            if connection and not connection.closed:
                await connection.close()
        
        logger.info("✅ WebSocket Manager stopped")
    
    def subscribe(self, callback: Callable[[WebSocketMessage], Any]):
        """Subscribe to real-time messages"""
        self.subscribers.append(callback)
        logger.info(f"📡 New subscriber added. Total subscribers: {len(self.subscribers)}")
    
    def unsubscribe(self, callback: Callable[[WebSocketMessage], Any]):
        """Unsubscribe from real-time messages"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info(f"📡 Subscriber removed. Total subscribers: {len(self.subscribers)}")
    
    async def _get_kucoin_token(self) -> Optional[str]:
        """Get KuCoin WebSocket token"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.kucoin_token_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('code') == '200000':
                            return data['data']['token']
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get KuCoin token: {e}")
            return None
    
    async def _connect_kucoin(self):
        """Connect to KuCoin WebSocket"""
        while self.running:
            try:
                # Get token
                token = await self._get_kucoin_token()
                if not token:
                    logger.error("❌ Failed to get KuCoin WebSocket token")
                    await asyncio.sleep(self.reconnect_delay)
                    continue
                
                # Connect to WebSocket
                ws_url = f"{self.kucoin_ws_url}?token={token}"
                async with websockets.connect(ws_url) as websocket:
                    self.connections['kucoin'] = websocket
                    logger.info("✅ Connected to KuCoin WebSocket")
                    
                    # Subscribe to market data
                    subscribe_message = {
                        "type": "subscribe",
                        "topic": "/market/ticker:BTC-USDT,ETH-USDT,ADA-USDT",
                        "privateChannel": False,
                        "response": True
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    
                    # Listen for messages
                    async for message in websocket:
                        if not self.running:
                            break
                        
                        try:
                            data = json.loads(message)
                            await self._process_kucoin_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ Invalid JSON from KuCoin: {e}")
                        except Exception as e:
                            logger.error(f"❌ Error processing KuCoin message: {e}")
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ KuCoin WebSocket connection closed")
            except Exception as e:
                logger.error(f"❌ KuCoin WebSocket error: {e}")
            
            # Reconnect delay
            await asyncio.sleep(self.reconnect_delay)
    
    async def _connect_binance(self):
        """Connect to Binance WebSocket"""
        while self.running:
            try:
                # Connect to Binance WebSocket
                symbols = ['btcusdt', 'ethusdt', 'adausdt']
                streams = [f"{symbol}@ticker" for symbol in symbols]
                ws_url = f"{self.binance_ws_url}{'/'.join(streams)}"
                
                async with websockets.connect(ws_url) as websocket:
                    self.connections['binance'] = websocket
                    logger.info("✅ Connected to Binance WebSocket")
                    
                    # Listen for messages
                    async for message in websocket:
                        if not self.running:
                            break
                        
                        try:
                            data = json.loads(message)
                            await self._process_binance_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ Invalid JSON from Binance: {e}")
                        except Exception as e:
                            logger.error(f"❌ Error processing Binance message: {e}")
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ Binance WebSocket connection closed")
            except Exception as e:
                logger.error(f"❌ Binance WebSocket error: {e}")
            
            # Reconnect delay
            await asyncio.sleep(self.reconnect_delay)
    
    async def _process_kucoin_message(self, data: Dict[str, Any]):
        """Process KuCoin WebSocket message"""
        try:
            if 'data' in data:
                ticker_data = data['data']
                symbol = ticker_data.get('symbol', '').replace('-', '')
                
                message = WebSocketMessage(
                    source='kucoin',
                    symbol=symbol,
                    data_type='price',
                    data={
                        'price': float(ticker_data.get('price', 0)),
                        'volume': float(ticker_data.get('size', 0)),
                        'change': float(ticker_data.get('changeRate', 0)),
                        'high': float(ticker_data.get('high', 0)),
                        'low': float(ticker_data.get('low', 0))
                    },
                    timestamp=time.time()
                )
                
                await self.message_queues['kucoin'].put(message)
                
        except Exception as e:
            logger.error(f"❌ Error processing KuCoin message: {e}")
    
    async def _process_binance_message(self, data: Dict[str, Any]):
        """Process Binance WebSocket message"""
        try:
            if 's' in data:  # Ticker data
                symbol = data['s']
                
                message = WebSocketMessage(
                    source='binance',
                    symbol=symbol,
                    data_type='price',
                    data={
                        'price': float(data.get('c', 0)),
                        'volume': float(data.get('v', 0)),
                        'change': float(data.get('P', 0)),
                        'high': float(data.get('h', 0)),
                        'low': float(data.get('l', 0))
                    },
                    timestamp=time.time()
                )
                
                await self.message_queues['binance'].put(message)
                
        except Exception as e:
            logger.error(f"❌ Error processing Binance message: {e}")
    
    async def _message_processor(self):
        """Process and distribute messages to subscribers"""
        while self.running:
            try:
                # Check all queues for messages
                for source, queue in self.message_queues.items():
                    try:
                        # Non-blocking queue check
                        message = queue.get_nowait()
                        
                        # Notify all subscribers
                        for subscriber in self.subscribers:
                            try:
                                await asyncio.create_task(
                                    asyncio.to_thread(subscriber, message)
                                )
                            except Exception as e:
                                logger.error(f"❌ Error in subscriber callback: {e}")
                        
                        queue.task_done()
                        
                    except asyncio.QueueEmpty:
                        continue
                
                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"❌ Error in message processor: {e}")
                await asyncio.sleep(1)
    
    async def _health_monitor(self):
        """Monitor WebSocket connection health"""
        while self.running:
            try:
                for source, connection in self.connections.items():
                    if connection and connection.closed:
                        logger.warning(f"⚠️ {source} WebSocket connection is closed")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in health monitor: {e}")
                await asyncio.sleep(30)

class WebSocketService:
    """High-level WebSocket service for the application"""
    
    def __init__(self):
        self.manager = WebSocketManager()
        self.subscribers: Dict[str, List[Callable]] = {
            'price': [],
            'trade': [],
            'signal': [],
            'score': []
        }
    
    async def start(self):
        """Start the WebSocket service"""
        # Subscribe to all message types
        self.manager.subscribe(self._message_handler)
        await self.manager.start()
    
    async def stop(self):
        """Stop the WebSocket service"""
        await self.manager.stop()
    
    def subscribe_to_price_updates(self, callback: Callable[[WebSocketMessage], Any]):
        """Subscribe to price updates"""
        self.subscribers['price'].append(callback)
    
    def subscribe_to_trade_signals(self, callback: Callable[[WebSocketMessage], Any]):
        """Subscribe to trade signals"""
        self.subscribers['trade'].append(callback)
    
    def subscribe_to_scoring_updates(self, callback: Callable[[WebSocketMessage], Any]):
        """Subscribe to scoring updates"""
        self.subscribers['score'].append(callback)
    
    async def _message_handler(self, message: WebSocketMessage):
        """Handle incoming WebSocket messages"""
        try:
            # Route message to appropriate subscribers
            if message.data_type == 'price':
                for callback in self.subscribers['price']:
                    try:
                        await asyncio.create_task(
                            asyncio.to_thread(callback, message)
                        )
                    except Exception as e:
                        logger.error(f"❌ Error in price subscriber: {e}")
            
            elif message.data_type in ['signal', 'trade']:
                for callback in self.subscribers['trade']:
                    try:
                        await asyncio.create_task(
                            asyncio.to_thread(callback, message)
                        )
                    except Exception as e:
                        logger.error(f"❌ Error in trade subscriber: {e}")
            
            elif message.data_type == 'score':
                for callback in self.subscribers['score']:
                    try:
                        await asyncio.create_task(
                            asyncio.to_thread(callback, message)
                        )
                    except Exception as e:
                        logger.error(f"❌ Error in score subscriber: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error in message handler: {e}")

# Global WebSocket service instance
websocket_service: Optional[WebSocketService] = None

async def get_websocket_service() -> WebSocketService:
    """Get or create WebSocket service instance"""
    global websocket_service
    if websocket_service is None:
        websocket_service = WebSocketService()
    return websocket_service 