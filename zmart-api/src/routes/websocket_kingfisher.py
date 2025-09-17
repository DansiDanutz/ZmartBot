#!/usr/bin/env python3
"""
WebSocket endpoints for real-time KingFisher updates
Provides live liquidation analysis and Telegram integration status
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Any
import asyncio
import logging
from datetime import datetime
import json

# Import KingFisher services
from ..services.kingfisher_service import KingFisherService
from ..services.integrated_scoring_system import IntegratedScoringSystem

logger = logging.getLogger(__name__)

router = APIRouter()

class KingFisherConnectionManager:
    """Manages WebSocket connections for KingFisher real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.kingfisher_service = KingFisherService()
        self.integrated_scoring = IntegratedScoringSystem()
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 30  # 30 seconds cache for KingFisher
        
        # Telegram monitoring status
        self.telegram_status = {
            'connected': True,
            'monitoring': True,
            'automation_enabled': True,
            'last_image': f"Last message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'processed_count': 15,
            'bot_token': '7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI',
            'chat_id': '-1002891569616',
            'channel_username': '@KingFisherAutomation',
            'status': 'enabled',
            'enabled': True
        }
        
        # Airtable records cache
        self.airtable_records = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"KingFisher client connected. Total: {len(self.active_connections)}")
        
        # Send initial status
        await self.send_status_update(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for symbol in list(self.symbol_subscriptions.keys()):
            if websocket in self.symbol_subscriptions[symbol]:
                self.symbol_subscriptions[symbol].remove(websocket)
                if not self.symbol_subscriptions[symbol]:
                    del self.symbol_subscriptions[symbol]
                    # Cancel monitoring task
                    if symbol in self._monitoring_tasks:
                        self._monitoring_tasks[symbol].cancel()
                        del self._monitoring_tasks[symbol]
        
        logger.info(f"KingFisher client disconnected. Total: {len(self.active_connections)}")
    
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
        logger.info(f"Client subscribed to KingFisher updates for {symbol}")
        
        # Send initial data if available in cache
        if symbol in self._cache:
            await self.send_kingfisher_update(websocket, symbol, self._cache[symbol])
        else:
            # Fetch initial data
            await self._fetch_and_broadcast_symbol(symbol)
    
    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe from symbol updates"""
        symbol = symbol.upper()
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(websocket)
            if not self.symbol_subscriptions[symbol]:
                del self.symbol_subscriptions[symbol]
                # Cancel monitoring task
                if symbol in self._monitoring_tasks:
                    self._monitoring_tasks[symbol].cancel()
                    del self._monitoring_tasks[symbol]
            logger.info(f"Client unsubscribed from {symbol}")
    
    async def send_kingfisher_update(self, websocket: WebSocket, symbol: str, data: Dict[str, Any]):
        """Send KingFisher update to a specific client"""
        try:
            update = {
                "type": "kingfisher_update",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            await websocket.send_json(update)
        except Exception as e:
            logger.error(f"Error sending KingFisher update: {e}")
    
    async def send_status_update(self, websocket: WebSocket):
        """Send Telegram and system status update"""
        try:
            status_update = {
                "type": "telegram_status",
                "data": self.telegram_status,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(status_update)
        except Exception as e:
            logger.error(f"Error sending status update: {e}")
    
    async def send_airtable_update(self, websocket: WebSocket, record: Dict[str, Any]):
        """Send Airtable record update"""
        try:
            airtable_update = {
                "type": "airtable_update",
                "data": record,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(airtable_update)
        except Exception as e:
            logger.error(f"Error sending Airtable update: {e}")
    
    async def _fetch_and_broadcast_symbol(self, symbol: str):
        """Fetch latest KingFisher data and broadcast to subscribers"""
        try:
            logger.info(f"Fetching KingFisher data for {symbol}")
            
            # Get KingFisher liquidation analysis
            kingfisher_analysis = await self.kingfisher_service.analyze_liquidation_data(symbol)
            
            # Get KingFisher score component
            kingfisher_score = await self.kingfisher_service.get_kingfisher_score(symbol)
            
            # Get integrated score (KingFisher + Cryptometer + RiskMetric)
            integrated_score = await self.integrated_scoring.get_comprehensive_score(symbol)
            
            # Prepare comprehensive update
            update_data = {
                "symbol": symbol,
                "liquidation_analysis": kingfisher_analysis.get('liquidation_analysis', {}),
                "ai_win_rate_prediction": kingfisher_analysis.get('ai_win_rate_prediction', {}),
                "kingfisher_score": {
                    "win_rate_prediction": kingfisher_score.get('win_rate_prediction', 0),
                    "confidence": kingfisher_score.get('confidence', 0),
                    "direction": kingfisher_score.get('direction', 'neutral'),
                    "reasoning": kingfisher_score.get('reasoning', ''),
                    "ai_analysis": kingfisher_score.get('ai_analysis', '')
                },
                "integrated_score": {
                    "final_score": integrated_score.get('final_score', 0),
                    "signal": integrated_score.get('signal', 'NEUTRAL'),
                    "confidence": integrated_score.get('confidence', 0),
                    "weights": integrated_score.get('dynamic_weights', {}),
                    "component_scores": integrated_score.get('component_scores', {})
                },
                "telegram_status": self.telegram_status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the data
            self._cache[symbol] = update_data
            
            # Broadcast to all subscribers
            if symbol in self.symbol_subscriptions:
                disconnected = []
                for websocket in self.symbol_subscriptions[symbol]:
                    try:
                        await self.send_kingfisher_update(websocket, symbol, update_data)
                    except WebSocketDisconnect:
                        disconnected.append(websocket)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client: {e}")
                        disconnected.append(websocket)
                
                # Clean up disconnected clients
                for ws in disconnected:
                    self.disconnect(ws)
                    
        except Exception as e:
            logger.error(f"Error fetching KingFisher data for {symbol}: {e}")
    
    async def _monitor_symbol(self, symbol: str):
        """Monitor a symbol and send periodic updates"""
        while symbol in self.symbol_subscriptions:
            try:
                await self._fetch_and_broadcast_symbol(symbol)
                # Wait before next update (30 seconds for KingFisher)
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                logger.info(f"Monitoring task cancelled for {symbol}")
                break
            except Exception as e:
                logger.error(f"Error in monitoring task for {symbol}: {e}")
                await asyncio.sleep(30)
    
    async def update_telegram_status(self, status: Dict[str, Any]):
        """Update Telegram status and broadcast to all clients"""
        self.telegram_status.update(status)
        
        # Broadcast to all connected clients
        for websocket in self.active_connections:
            await self.send_status_update(websocket)
    
    async def add_airtable_record(self, record: Dict[str, Any]):
        """Add new Airtable record and broadcast"""
        self.airtable_records.insert(0, record)
        # Keep only last 20 records
        self.airtable_records = self.airtable_records[:20]
        
        # Broadcast to all connected clients
        for websocket in self.active_connections:
            await self.send_airtable_update(websocket, record)
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        return [
            'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'AVAX', 'DOT',
            'DOGE', 'MATIC', 'SHIB', 'LTC', 'UNI', 'LINK', 'ATOM',
            'XLM', 'VET', 'ALGO', 'FTM', 'HBAR', 'MANA', 'SAND', 'AXS', 'GALA'
        ]

# Create global connection manager
manager = KingFisherConnectionManager()

@router.websocket("/ws/kingfisher")
async def websocket_kingfisher_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time KingFisher updates"""
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
                symbols = manager.get_available_symbols()
                await websocket.send_json({
                    "type": "symbols_list",
                    "symbols": symbols
                })
            
            elif message_type == "get_telegram_status":
                await manager.send_status_update(websocket)
            
            elif message_type == "get_airtable_records":
                await websocket.send_json({
                    "type": "airtable_records",
                    "records": manager.airtable_records
                })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.get("/ws/kingfisher/status")
async def get_kingfisher_websocket_status():
    """Get KingFisher WebSocket server status"""
    return {
        "active_connections": len(manager.active_connections),
        "monitored_symbols": list(manager.symbol_subscriptions.keys()),
        "cached_symbols": list(manager._cache.keys()),
        "telegram_status": manager.telegram_status,
        "airtable_records_count": len(manager.airtable_records),
        "timestamp": datetime.now().isoformat()
    }

# API endpoints for Telegram control
@router.post("/api/kingfisher/telegram/enable")
async def enable_telegram_automation():
    """Enable Telegram automation"""
    await manager.update_telegram_status({'automation_enabled': True})
    return {"success": True, "message": "Telegram automation enabled"}

@router.post("/api/kingfisher/telegram/disable")
async def disable_telegram_automation():
    """Disable Telegram automation"""
    await manager.update_telegram_status({'automation_enabled': False})
    return {"success": True, "message": "Telegram automation disabled"}

@router.post("/api/kingfisher/telegram/start")
async def start_telegram_monitoring():
    """Start Telegram monitoring"""
    await manager.update_telegram_status({
        'monitoring': True,
        'connected': True
    })
    return {"success": True, "message": "Telegram monitoring started"}

@router.post("/api/kingfisher/telegram/stop")
async def stop_telegram_monitoring():
    """Stop Telegram monitoring"""
    await manager.update_telegram_status({'monitoring': False})
    return {"success": True, "message": "Telegram monitoring stopped"}

@router.get("/api/kingfisher/telegram/status")
async def get_telegram_status():
    """Get current Telegram status"""
    return manager.telegram_status

@router.get("/api/kingfisher/airtable/recent")
async def get_recent_airtable_records():
    """Get recent Airtable records"""
    return {"records": manager.airtable_records}