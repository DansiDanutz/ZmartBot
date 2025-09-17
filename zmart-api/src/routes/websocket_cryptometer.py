#!/usr/bin/env python3
"""
WebSocket endpoints for real-time Cryptometer updates
Provides live multi-endpoint analysis and AI insights
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Any
import asyncio
import logging
from datetime import datetime

from ..services.cryptometer_service import MultiTimeframeCryptometerSystem
from ..services.cryptometer_data_types import CryptometerEndpointAnalyzer
from ..agents.self_learning_cryptometer_agent import get_self_learning_agent

logger = logging.getLogger(__name__)

router = APIRouter()

class CryptometerConnectionManager:
    """Manages WebSocket connections for Cryptometer real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.cryptometer_system = MultiTimeframeCryptometerSystem()
        self.endpoint_analyzer = CryptometerEndpointAnalyzer()
        self.self_learning_agent = get_self_learning_agent()
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 15  # 15 seconds cache
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Cryptometer client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for symbol in list(self.symbol_subscriptions.keys()):
            if websocket in self.symbol_subscriptions[symbol]:
                self.symbol_subscriptions[symbol].remove(websocket)
                if not self.symbol_subscriptions[symbol]:
                    # No more subscribers for this symbol
                    del self.symbol_subscriptions[symbol]
                    # Cancel monitoring task
                    if symbol in self._monitoring_tasks:
                        self._monitoring_tasks[symbol].cancel()
                        del self._monitoring_tasks[symbol]
        
        logger.info(f"Cryptometer client disconnected. Total: {len(self.active_connections)}")
    
    async def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe to updates for a specific symbol"""
        symbol = symbol.upper()
        
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
            # Start monitoring task for this symbol
            self._monitoring_tasks[symbol] = asyncio.create_task(
                self._monitor_symbol(symbol)
            )
        
        self.symbol_subscriptions[symbol].add(websocket)
        logger.info(f"Client subscribed to Cryptometer updates for {symbol}")
        
        # Send initial data if available in cache
        if symbol in self._cache:
            await self.send_cryptometer_update(websocket, symbol, self._cache[symbol])
        else:
            # Fetch initial data
            await self._fetch_and_broadcast_symbol(symbol)
    
    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe from symbol updates"""
        symbol = symbol.upper()
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(websocket)
            if not self.symbol_subscriptions[symbol]:
                # No more subscribers
                del self.symbol_subscriptions[symbol]
                # Cancel monitoring task
                if symbol in self._monitoring_tasks:
                    self._monitoring_tasks[symbol].cancel()
                    del self._monitoring_tasks[symbol]
            logger.info(f"Client unsubscribed from {symbol}")
    
    async def send_cryptometer_update(self, websocket: WebSocket, symbol: str, data: Dict[str, Any]):
        """Send Cryptometer update to a specific client"""
        try:
            update = {
                "type": "cryptometer_update",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            await websocket.send_json(update)
        except Exception as e:
            logger.error(f"Error sending Cryptometer update: {e}")
    
    async def _fetch_and_broadcast_symbol(self, symbol: str):
        """Fetch latest data and broadcast to subscribers"""
        try:
            # Collect data from all endpoints
            logger.info(f"Fetching Cryptometer data for {symbol}")
            
            # Standard endpoint analysis
            endpoint_data = await self.cryptometer_system.collect_symbol_data(symbol)
            
            # Unified analysis
            unified_analysis = await self.endpoint_analyzer.analyze_symbol(symbol)
            
            # Self-learning AI analysis
            ai_analysis = None
            try:
                ai_result = await self.self_learning_agent.analyze_symbol(symbol, endpoint_data)
                ai_analysis = {
                    "total_score": ai_result.total_score,
                    "win_rate_prediction": ai_result.win_rate_prediction,
                    "signal": ai_result.signal,
                    "confidence": ai_result.confidence,
                    "best_timeframe": ai_result.best_timeframe,
                    "timeframe_scores": ai_result.timeframe_scores,
                    "ai_insights": getattr(ai_result, 'ai_insights', [])
                }
            except Exception as e:
                logger.warning(f"AI analysis failed for {symbol}: {e}")
            
            # Multi-timeframe analysis
            multi_timeframe = None
            try:
                # Access the ai_agent if it exists
                if hasattr(self.cryptometer_system, 'ai_agent'):
                    multi_timeframe = self.cryptometer_system.ai_agent.analyze_multi_timeframe(endpoint_data)
            except Exception as e:
                logger.warning(f"Multi-timeframe analysis not available: {e}")
            
            # Prepare comprehensive update
            update_data = {
                "endpoints": {
                    name: {
                        "success": data.get("success", False),
                        "data": data.get("data", {}),
                        "weight": data.get("weight", 1)
                    }
                    for name, data in endpoint_data.items()
                    if isinstance(data, dict) and name != "symbol"
                },
                "unified_analysis": {
                    "total_score": unified_analysis.total_score,
                    "signal": unified_analysis.signal,
                    "confidence": unified_analysis.confidence,
                    "endpoints_analyzed": unified_analysis.endpoints_analyzed,
                    "endpoint_scores": [
                        {
                            "endpoint": score.endpoint_name,
                            "score": score.score,
                            "weight": score.weight,
                            "confidence": score.confidence
                        }
                        for score in unified_analysis.endpoint_scores
                    ]
                },
                "ai_analysis": ai_analysis,
                "multi_timeframe": multi_timeframe,
                "summary": {
                    "recommendation": self._get_recommendation(
                        unified_analysis.total_score,
                        unified_analysis.signal,
                        ai_analysis["win_rate_prediction"] if ai_analysis else 0.5
                    ),
                    "strength": self._get_signal_strength(unified_analysis.total_score),
                    "endpoints_success": sum(
                        1 for data in endpoint_data.values()
                        if isinstance(data, dict) and data.get("success")
                    ),
                    "endpoints_total": len([
                        k for k in endpoint_data.keys() 
                        if k != "symbol"
                    ])
                }
            }
            
            # Cache the data
            self._cache[symbol] = update_data
            
            # Broadcast to all subscribers
            if symbol in self.symbol_subscriptions:
                disconnected = []
                for websocket in self.symbol_subscriptions[symbol]:
                    try:
                        await self.send_cryptometer_update(websocket, symbol, update_data)
                    except WebSocketDisconnect:
                        disconnected.append(websocket)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client: {e}")
                        disconnected.append(websocket)
                
                # Clean up disconnected clients
                for ws in disconnected:
                    self.disconnect(ws)
                    
        except Exception as e:
            logger.error(f"Error fetching Cryptometer data for {symbol}: {e}")
    
    async def _monitor_symbol(self, symbol: str):
        """Monitor a symbol and send periodic updates"""
        while symbol in self.symbol_subscriptions:
            try:
                await self._fetch_and_broadcast_symbol(symbol)
                # Wait before next update (30 seconds)
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                logger.info(f"Monitoring task cancelled for {symbol}")
                break
            except Exception as e:
                logger.error(f"Error in monitoring task for {symbol}: {e}")
                await asyncio.sleep(30)
    
    def _get_recommendation(self, score: float, signal: str, win_rate: float) -> str:
        """Generate trading recommendation"""
        if score >= 80 and win_rate >= 0.7:
            return "STRONG " + signal
        elif score >= 60 and win_rate >= 0.6:
            return signal
        elif score >= 40:
            return "WEAK " + signal
        else:
            return "NEUTRAL"
    
    def _get_signal_strength(self, score: float) -> str:
        """Get signal strength description"""
        if score >= 80:
            return "Very Strong"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Weak"
        else:
            return "Very Weak"
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        return [
            'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'AVAX', 'DOT',
            'DOGE', 'MATIC', 'SHIB', 'LTC', 'UNI', 'LINK', 'ATOM',
            'XLM', 'VET', 'ALGO', 'FTM', 'HBAR', 'MANA', 'SAND', 'AXS', 'GALA'
        ]

# Create global connection manager
manager = CryptometerConnectionManager()

@router.websocket("/ws/cryptometer")
async def websocket_cryptometer_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Cryptometer updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "subscribe":
                symbol = data.get("symbol")
                if symbol:
                    await manager.subscribe_to_symbol(websocket, symbol)
                    await websocket.send_json({
                        "type": "subscribed",
                        "symbol": symbol.upper(),
                        "status": "success"
                    })
            
            elif message_type == "unsubscribe":
                symbol = data.get("symbol")
                if symbol:
                    await manager.unsubscribe_from_symbol(websocket, symbol)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "symbol": symbol.upper(),
                        "status": "success"
                    })
            
            elif message_type == "get_symbols":
                symbols = await manager.get_available_symbols()
                await websocket.send_json({
                    "type": "symbols_list",
                    "symbols": symbols
                })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.get("/ws/cryptometer/status")
async def get_cryptometer_websocket_status():
    """Get Cryptometer WebSocket server status"""
    return {
        "active_connections": len(manager.active_connections),
        "monitored_symbols": list(manager.symbol_subscriptions.keys()),
        "cached_symbols": list(manager._cache.keys()),
        "timestamp": datetime.now().isoformat()
    }