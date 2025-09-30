"""
WebSocket Manager for Real-time Updates
Provides real-time price updates and alert notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by user_id
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
        # Active connections by subscription type
        self.price_subscribers: Dict[str, Set[WebSocket]] = {}  # symbol -> connections
        self.alert_subscribers: Set[WebSocket] = set()
        self.system_subscribers: Set[WebSocket] = set()
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.now(),
            "subscriptions": set(),
            "last_ping": datetime.now()
        }
        
        logger.info(f"✅ WebSocket connected for user {user_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket connection established",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket not in self.connection_metadata:
            return
            
        metadata = self.connection_metadata[websocket]
        user_id = metadata["user_id"]
        
        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from subscription lists
        for symbol_subscribers in self.price_subscribers.values():
            symbol_subscribers.discard(websocket)
        self.alert_subscribers.discard(websocket)
        self.system_subscribers.discard(websocket)
        
        # Clean up empty subscription lists
        empty_symbols = [symbol for symbol, subs in self.price_subscribers.items() if not subs]
        for symbol in empty_symbols:
            del self.price_subscribers[symbol]
        
        # Remove metadata
        del self.connection_metadata[websocket]
        
        logger.info(f"❌ WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to all connections for a specific user"""
        if user_id not in self.user_connections:
            return
            
        disconnected = set()
        for websocket in self.user_connections[user_id].copy():
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], subscriber_set: Set[WebSocket]):
        """Broadcast message to a set of subscribers"""
        if not subscriber_set:
            return
            
        disconnected = set()
        for websocket in subscriber_set.copy():
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def subscribe_to_price_updates(self, websocket: WebSocket, symbol: str):
        """Subscribe connection to price updates for a symbol"""
        if symbol not in self.price_subscribers:
            self.price_subscribers[symbol] = set()
        
        self.price_subscribers[symbol].add(websocket)
        
        # Update connection metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscriptions"].add(f"price:{symbol}")
        
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "subscription": f"price:{symbol}",
            "message": f"Subscribed to price updates for {symbol}"
        }, websocket)
        
        logger.info(f"📈 Subscribed to price updates: {symbol}")
    
    async def subscribe_to_alert_updates(self, websocket: WebSocket):
        """Subscribe connection to alert updates"""
        self.alert_subscribers.add(websocket)
        
        # Update connection metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscriptions"].add("alerts")
        
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "subscription": "alerts",
            "message": "Subscribed to alert updates"
        }, websocket)
        
        logger.info("🔔 Subscribed to alert updates")
    
    async def subscribe_to_system_updates(self, websocket: WebSocket):
        """Subscribe connection to system status updates"""
        self.system_subscribers.add(websocket)
        
        # Update connection metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscriptions"].add("system")
        
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "subscription": "system",
            "message": "Subscribed to system updates"
        }, websocket)
        
        logger.info("⚙️ Subscribed to system updates")
    
    async def broadcast_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """Broadcast price update to symbol subscribers"""
        if symbol not in self.price_subscribers:
            return
        
        message = {
            "type": "price_update",
            "symbol": symbol,
            "data": price_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_subscribers(message, self.price_subscribers[symbol])
    
    async def broadcast_alert_notification(self, alert_data: Dict[str, Any]):
        """Broadcast alert notification to alert subscribers"""
        message = {
            "type": "alert_triggered",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_subscribers(message, self.alert_subscribers)
    
    async def broadcast_system_update(self, system_data: Dict[str, Any]):
        """Broadcast system update to system subscribers"""
        message = {
            "type": "system_update",
            "data": system_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_subscribers(message, self.system_subscribers)
    
    async def handle_websocket_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            if not isinstance(message, dict):
                raise ValueError("Message must be a dictionary")
            
            message_type = message.get("type")
            
            if not message_type:
                await self.send_personal_message({
                    "type": "error",
                    "message": "Message type is required"
                }, websocket)
                return
            
            if message_type == "ping":
                # Update last ping time
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_ping"] = datetime.now()
                
                await self.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            elif message_type == "subscribe":
                subscription = message.get("subscription")
                
                if subscription and subscription.startswith("price:"):
                    symbol = subscription.split(":", 1)[1]
                    await self.subscribe_to_price_updates(websocket, symbol)
                
                elif subscription == "alerts":
                    await self.subscribe_to_alert_updates(websocket)
                
                elif subscription == "system":
                    await self.subscribe_to_system_updates(websocket)
            
            elif message_type == "unsubscribe":
                subscription = message.get("subscription")
                
                if subscription and subscription.startswith("price:"):
                    symbol = subscription.split(":", 1)[1]
                    if symbol in self.price_subscribers:
                        self.price_subscribers[symbol].discard(websocket)
                        if not self.price_subscribers[symbol]:
                            del self.price_subscribers[symbol]
                
                elif subscription == "alerts":
                    self.alert_subscribers.discard(websocket)
                
                elif subscription == "system":
                    self.system_subscribers.discard(websocket)
                
                # Update connection metadata
                if websocket in self.connection_metadata and subscription:
                    self.connection_metadata[websocket]["subscriptions"].discard(subscription)
                
                await self.send_personal_message({
                    "type": "unsubscription_confirmed",
                    "subscription": subscription or "unknown",
                    "message": f"Unsubscribed from {subscription or 'unknown'}"
                }, websocket)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message({
                "type": "error",
                "message": "Error processing message",
                "error": str(e)
            }, websocket)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": sum(len(connections) for connections in self.user_connections.values()),
            "total_users": len(self.user_connections),
            "price_subscriptions": {
                symbol: len(subscribers) for symbol, subscribers in self.price_subscribers.items()
            },
            "alert_subscribers": len(self.alert_subscribers),
            "system_subscribers": len(self.system_subscribers),
            "active_symbols": list(self.price_subscribers.keys())
        }

# Global connection manager instance
connection_manager = ConnectionManager()

# Utility functions for integration with alerts system
async def notify_price_update(symbol: str, price_data: Dict[str, Any]):
    """Utility to notify price update through WebSocket"""
    await connection_manager.broadcast_price_update(symbol, price_data)

async def notify_alert_triggered(alert_data: Dict[str, Any]):
    """Utility to notify alert triggered through WebSocket"""
    await connection_manager.broadcast_alert_notification(alert_data)

async def notify_system_status(status_data: Dict[str, Any]):
    """Utility to notify system status change through WebSocket"""
    await connection_manager.broadcast_system_update(status_data)

# Background task for periodic health checks
async def periodic_health_check():
    """Periodic health check for WebSocket connections"""
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            current_time = datetime.now()
            stale_connections = []
            
            # Find stale connections (no ping in last 2 minutes)
            for websocket, metadata in connection_manager.connection_metadata.items():
                last_ping = metadata.get("last_ping", metadata["connected_at"])
                if (current_time - last_ping).total_seconds() > 120:
                    stale_connections.append(websocket)
            
            # Disconnect stale connections
            for websocket in stale_connections:
                try:
                    await websocket.close()
                except:
                    pass
                connection_manager.disconnect(websocket)
            
            if stale_connections:
                logger.info(f"🧹 Cleaned up {len(stale_connections)} stale WebSocket connections")
                
        except Exception as e:
            logger.error(f"Error in periodic health check: {e}")

# Start health check task
def start_websocket_health_check():
    """Start the WebSocket health check background task"""
    task = asyncio.create_task(periodic_health_check())
    connection_manager.background_tasks.add(task)
    task.add_done_callback(connection_manager.background_tasks.discard)