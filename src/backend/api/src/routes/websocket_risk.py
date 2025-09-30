#!/usr/bin/env python3
"""
WebSocket endpoints for real-time RiskMetric updates
Provides live risk value changes and alerts to frontend
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import logging
from datetime import datetime

from ..services.unified_riskmetric import UnifiedRiskMetric

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.riskmetric_service = UnifiedRiskMetric()
        self._monitoring_task = None
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        # Remove from all symbol subscriptions
        for symbol in self.symbol_subscriptions:
            if websocket in self.symbol_subscriptions[symbol]:
                self.symbol_subscriptions[symbol].remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe a connection to updates for a specific symbol"""
        symbol = symbol.upper()
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
        self.symbol_subscriptions[symbol].add(websocket)
        logger.info(f"Client subscribed to {symbol}")
        
        # Send initial risk data
        await self.send_risk_update(websocket, symbol)
    
    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a connection from symbol updates"""
        symbol = symbol.upper()
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(websocket)
            logger.info(f"Client unsubscribed from {symbol}")
    
    async def send_risk_update(self, websocket: WebSocket, symbol: str):
        """Send risk update for a specific symbol to a client"""
        try:
            # Get current price
            price = await self.riskmetric_service.get_current_price(symbol)
            
            # Get risk assessment
            assessment = await self.riskmetric_service.assess_risk(symbol, price)
            
            if assessment:
                # Get risk alerts
                alerts = self.riskmetric_service.get_risk_alerts(symbol, price)
                
                # Get risk momentum
                momentum = await self.riskmetric_service.get_risk_momentum(symbol)
                
                update = {
                    "type": "risk_update",
                    "symbol": symbol,
                    "data": {
                        "risk_value": assessment.risk_value,
                        "risk_band": assessment.risk_band,
                        "score": assessment.score,
                        "tradeable": assessment.tradeable,
                        "signal": assessment.signal,
                        "price": price,
                        "alerts": alerts,
                        "momentum": momentum,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                await websocket.send_json(update)
                
        except Exception as e:
            logger.error(f"Error sending risk update for {symbol}: {e}")
    
    async def broadcast_to_symbol(self, symbol: str):
        """Broadcast risk update to all clients subscribed to a symbol"""
        if symbol in self.symbol_subscriptions:
            disconnected = []
            for websocket in self.symbol_subscriptions[symbol]:
                try:
                    await self.send_risk_update(websocket, symbol)
                except WebSocketDisconnect:
                    disconnected.append(websocket)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected clients
            for ws in disconnected:
                self.disconnect(ws)
    
    async def start_monitoring(self):
        """Start monitoring for risk changes"""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_risk_changes())
            logger.info("Started risk monitoring task")
    
    async def stop_monitoring(self):
        """Stop monitoring for risk changes"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
            logger.info("Stopped risk monitoring task")
    
    async def _monitor_risk_changes(self):
        """Monitor for risk changes and broadcast updates"""
        while True:
            try:
                # Check each subscribed symbol for updates
                for symbol in list(self.symbol_subscriptions.keys()):
                    if self.symbol_subscriptions[symbol]:  # Has subscribers
                        await self.broadcast_to_symbol(symbol)
                
                # Wait before next update cycle (5 seconds)
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring task: {e}")
                await asyncio.sleep(5)

# Create global connection manager
manager = ConnectionManager()

@router.websocket("/ws/risk")
async def websocket_risk_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time risk updates"""
    await manager.connect(websocket)
    
    # Start monitoring if not already running
    await manager.start_monitoring()
    
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
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "get_all_symbols":
                symbols = await manager.riskmetric_service.get_all_symbols()
                await websocket.send_json({
                    "type": "symbols_list",
                    "symbols": symbols
                })
            
            elif message_type == "get_screener":
                screener = await manager.riskmetric_service.get_comprehensive_screener()
                await websocket.send_json({
                    "type": "screener_data",
                    "data": screener
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.get("/ws/risk/status")
async def get_websocket_status():
    """Get WebSocket server status"""
    return {
        "active_connections": len(manager.active_connections),
        "subscribed_symbols": list(manager.symbol_subscriptions.keys()),
        "monitoring_active": manager._monitoring_task is not None,
        "timestamp": datetime.now().isoformat()
    }