"""
Real-time Cross-Project Notifications Service
Provides real-time synchronization and notifications between ZmartyBrain and ZmartBot
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from supabase import create_client, Client
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import websockets
from threading import Thread
import time

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    USER_UPDATE = "user_update"
    TRADING_SIGNAL = "trading_signal"
    PORTFOLIO_CHANGE = "portfolio_change"
    ALERT_TRIGGERED = "alert_triggered"
    ENGAGEMENT_UPDATE = "engagement_update"
    PERFORMANCE_UPDATE = "performance_update"
    SYSTEM_EVENT = "system_event"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Notification:
    id: str
    type: NotificationType
    priority: NotificationPriority
    user_id: str
    title: str
    message: str
    data: Dict[str, Any]
    source_project: str
    target_project: str
    created_at: datetime
    delivered: bool = False
    delivered_at: Optional[datetime] = None

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.connection_users: Dict[str, str] = {}  # connection_id -> user_id
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        self.connection_users[connection_id] = user_id
        
        logger.info(f"🔌 WebSocket connected: {connection_id} for user {user_id}")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            user_id = self.connection_users.get(connection_id)
            
            del self.active_connections[connection_id]
            del self.connection_users[connection_id]
            
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            logger.info(f"🔌 WebSocket disconnected: {connection_id}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections for a user"""
        if user_id not in self.user_connections:
            return False
        
        connections_to_remove = []
        for connection_id in self.user_connections[user_id]:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Failed to send to connection {connection_id}: {e}")
                connections_to_remove.append(connection_id)
        
        # Remove failed connections
        for connection_id in connections_to_remove:
            self.disconnect(connection_id)
        
        return len(connections_to_remove) == 0
    
    async def send_to_all(self, message: dict):
        """Send message to all active connections"""
        connections_to_remove = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Failed to send to connection {connection_id}: {e}")
                connections_to_remove.append(connection_id)
        
        # Remove failed connections
        for connection_id in connections_to_remove:
            self.disconnect(connection_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of connections for a specific user"""
        return len(self.user_connections.get(user_id, set()))

class RealtimeCrossProjectNotifications:
    """
    Real-time notification service for cross-project synchronization
    """
    
    def __init__(self):
        # ZmartyBrain configuration
        self.brain_url = "https://xhskmqsgtdhehzlvtuns.supabase.co"
        self.brain_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw"
        
        # ZmartBot configuration
        self.bot_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.bot_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"
        
        # Initialize clients
        self.brain_client: Optional[Client] = None
        self.bot_client: Optional[Client] = None
        
        # Connection management
        self.connection_manager = ConnectionManager()
        
        # Notification management
        self.notification_queue: List[Notification] = []
        self.notification_history: List[Notification] = []
        self.subscribers: Dict[NotificationType, List[Callable]] = {}
        
        # Real-time subscriptions
        self.brain_subscription = None
        self.bot_subscription = None
        self.is_running = False
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        self._initialize_clients()
        self._setup_notification_tables()
    
    def _initialize_clients(self):
        """Initialize Supabase clients for both projects"""
        try:
            self.brain_client = create_client(self.brain_url, self.brain_key)
            self.bot_client = create_client(self.bot_url, self.bot_key)
            logger.info("✅ Real-time Cross-Project Notifications initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase clients: {e}")
            raise
    
    async def _setup_notification_tables(self):
        """Set up notification tables in both projects"""
        try:
            # Create notifications table in ZmartBot
            notification_table_sql = """
            CREATE TABLE IF NOT EXISTS cross_project_notifications (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                notification_type VARCHAR(50) NOT NULL,
                priority VARCHAR(20) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                data JSONB DEFAULT '{}',
                source_project VARCHAR(50) NOT NULL,
                target_project VARCHAR(50) NOT NULL,
                delivered BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON cross_project_notifications(user_id);
            CREATE INDEX IF NOT EXISTS idx_notifications_type ON cross_project_notifications(notification_type);
            CREATE INDEX IF NOT EXISTS idx_notifications_priority ON cross_project_notifications(priority);
            CREATE INDEX IF NOT EXISTS idx_notifications_delivered ON cross_project_notifications(delivered);
            """
            
            # Execute in ZmartBot
            response = self.bot_client.rpc('exec_sql', {'sql': notification_table_sql}).execute()
            logger.info("✅ Notification tables created")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create notification tables: {e}")
    
    async def start_service(self):
        """Start the real-time notification service"""
        if self.is_running:
            logger.warning("⚠️ Real-time service already running")
            return
        
        self.is_running = True
        
        # Start background tasks
        self.background_tasks.add(asyncio.create_task(self._process_notification_queue()))
        self.background_tasks.add(asyncio.create_task(self._setup_realtime_subscriptions()))
        self.background_tasks.add(asyncio.create_task(self._cleanup_old_notifications()))
        
        logger.info("🚀 Real-time Cross-Project Notifications service started")
    
    async def stop_service(self):
        """Stop the real-time notification service"""
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        # Close subscriptions
        if self.brain_subscription:
            await self.brain_subscription.close()
        if self.bot_subscription:
            await self.bot_subscription.close()
        
        logger.info("🛑 Real-time Cross-Project Notifications service stopped")
    
    async def _process_notification_queue(self):
        """Process pending notifications"""
        while self.is_running:
            try:
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    await self._deliver_notification(notification)
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"❌ Error processing notification queue: {e}")
                await asyncio.sleep(5)
    
    async def _deliver_notification(self, notification: Notification):
        """Deliver a notification to the target user"""
        try:
            # Send via WebSocket
            message = {
                "type": "notification",
                "notification": {
                    "id": notification.id,
                    "type": notification.type.value,
                    "priority": notification.priority.value,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "source_project": notification.source_project,
                    "created_at": notification.created_at.isoformat()
                }
            }
            
            success = await self.connection_manager.send_to_user(notification.user_id, message)
            
            if success:
                notification.delivered = True
                notification.delivered_at = datetime.now()
                logger.info(f"📤 Notification delivered: {notification.id}")
            else:
                logger.warning(f"⚠️ No active connections for user {notification.user_id}")
            
            # Store in database
            await self._store_notification(notification)
            
            # Add to history
            self.notification_history.append(notification)
            
        except Exception as e:
            logger.error(f"❌ Failed to deliver notification {notification.id}: {e}")
    
    async def _store_notification(self, notification: Notification):
        """Store notification in database"""
        try:
            notification_data = {
                "id": notification.id,
                "notification_type": notification.type.value,
                "priority": notification.priority.value,
                "user_id": notification.user_id,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "source_project": notification.source_project,
                "target_project": notification.target_project,
                "delivered": notification.delivered,
                "created_at": notification.created_at.isoformat(),
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None
            }
            
            response = self.bot_client.table("cross_project_notifications").insert(notification_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Failed to store notification: {e}")
    
    async def _setup_realtime_subscriptions(self):
        """Set up real-time subscriptions for both projects"""
        try:
            # Subscribe to ZmartyBrain changes
            self.brain_subscription = self.brain_client.channel("brain_changes")
            
            # Listen for user updates
            self.brain_subscription.on(
                "postgres_changes",
                {
                    "event": "*",
                    "schema": "public",
                    "table": "users"
                },
                self._handle_brain_user_change
            ).subscribe()
            
            # Subscribe to ZmartBot changes
            self.bot_subscription = self.bot_client.channel("bot_changes")
            
            # Listen for trading data changes
            self.bot_subscription.on(
                "postgres_changes",
                {
                    "event": "*",
                    "schema": "public",
                    "table": "trades"
                },
                self._handle_bot_trade_change
            ).subscribe()
            
            # Listen for portfolio changes
            self.bot_subscription.on(
                "postgres_changes",
                {
                    "event": "*",
                    "schema": "public",
                    "table": "portfolios"
                },
                self._handle_bot_portfolio_change
            ).subscribe()
            
            # Listen for alert changes
            self.bot_subscription.on(
                "postgres_changes",
                {
                    "event": "*",
                    "schema": "public",
                    "table": "smart_alerts"
                },
                self._handle_bot_alert_change
            ).subscribe()
            
            logger.info("✅ Real-time subscriptions established")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup real-time subscriptions: {e}")
    
    async def _handle_brain_user_change(self, payload):
        """Handle user changes from ZmartyBrain"""
        try:
            event_type = payload.get("eventType")
            record = payload.get("new", payload.get("old", {}))
            user_id = record.get("id")
            
            if not user_id:
                return
            
            # Create notification based on change type
            if event_type == "UPDATE":
                # Check if engagement score changed significantly
                old_record = payload.get("old", {})
                old_engagement = old_record.get("engagement_score", 0.5)
                new_engagement = record.get("engagement_score", 0.5)
                
                if abs(new_engagement - old_engagement) > 0.1:
                    await self._create_notification(
                        NotificationType.ENGAGEMENT_UPDATE,
                        NotificationPriority.MEDIUM,
                        user_id,
                        "Engagement Update",
                        f"Your engagement score has changed to {new_engagement:.2f}",
                        {"old_score": old_engagement, "new_score": new_engagement},
                        "zmartybrain",
                        "zmartbot"
                    )
            
            logger.info(f"📊 Brain user change processed: {event_type} for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling brain user change: {e}")
    
    async def _handle_bot_trade_change(self, payload):
        """Handle trade changes from ZmartBot"""
        try:
            event_type = payload.get("eventType")
            record = payload.get("new", payload.get("old", {}))
            user_id = record.get("user_id")
            
            if not user_id:
                return
            
            # Create notification for new trades
            if event_type == "INSERT":
                symbol = record.get("symbol", "Unknown")
                pnl = record.get("pnl", 0)
                
                priority = NotificationPriority.HIGH if abs(pnl) > 100 else NotificationPriority.MEDIUM
                title = "New Trade Executed"
                message = f"Trade executed for {symbol} with P&L: ${pnl:.2f}"
                
                await self._create_notification(
                    NotificationType.TRADING_SIGNAL,
                    priority,
                    user_id,
                    title,
                    message,
                    {"symbol": symbol, "pnl": pnl, "trade_id": record.get("id")},
                    "zmartbot",
                    "zmartybrain"
                )
            
            logger.info(f"📈 Bot trade change processed: {event_type} for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling bot trade change: {e}")
    
    async def _handle_bot_portfolio_change(self, payload):
        """Handle portfolio changes from ZmartBot"""
        try:
            event_type = payload.get("eventType")
            record = payload.get("new", payload.get("old", {}))
            user_id = record.get("user_id")
            
            if not user_id:
                return
            
            # Create notification for portfolio updates
            if event_type in ["INSERT", "UPDATE"]:
                total_value = record.get("total_value", 0)
                
                await self._create_notification(
                    NotificationType.PORTFOLIO_CHANGE,
                    NotificationPriority.MEDIUM,
                    user_id,
                    "Portfolio Updated",
                    f"Your portfolio value is now ${total_value:.2f}",
                    {"total_value": total_value, "portfolio_id": record.get("id")},
                    "zmartbot",
                    "zmartybrain"
                )
            
            logger.info(f"💼 Bot portfolio change processed: {event_type} for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling bot portfolio change: {e}")
    
    async def _handle_bot_alert_change(self, payload):
        """Handle alert changes from ZmartBot"""
        try:
            event_type = payload.get("eventType")
            record = payload.get("new", payload.get("old", {}))
            user_id = record.get("user_id")
            
            if not user_id:
                return
            
            # Create notification for triggered alerts
            if event_type == "UPDATE" and record.get("status") == "TRIGGERED":
                symbol = record.get("symbol", "Unknown")
                alert_type = record.get("alert_type", "Unknown")
                
                await self._create_notification(
                    NotificationType.ALERT_TRIGGERED,
                    NotificationPriority.HIGH,
                    user_id,
                    "Alert Triggered",
                    f"{alert_type} alert triggered for {symbol}",
                    {"symbol": symbol, "alert_type": alert_type, "alert_id": record.get("id")},
                    "zmartbot",
                    "zmartybrain"
                )
            
            logger.info(f"🚨 Bot alert change processed: {event_type} for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling bot alert change: {e}")
    
    async def _create_notification(self, notification_type: NotificationType, priority: NotificationPriority, 
                                 user_id: str, title: str, message: str, data: Dict[str, Any], 
                                 source_project: str, target_project: str):
        """Create and queue a new notification"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=notification_type,
            priority=priority,
            user_id=user_id,
            title=title,
            message=message,
            data=data,
            source_project=source_project,
            target_project=target_project,
            created_at=datetime.now()
        )
        
        self.notification_queue.append(notification)
        logger.info(f"📝 Notification queued: {notification.id}")
    
    async def _cleanup_old_notifications(self):
        """Clean up old notifications from memory"""
        while self.is_running:
            try:
                # Keep only last 1000 notifications in history
                if len(self.notification_history) > 1000:
                    self.notification_history = self.notification_history[-1000:]
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up notifications: {e}")
                await asyncio.sleep(3600)
    
    async def send_manual_notification(self, user_id: str, title: str, message: str, 
                                     notification_type: str = "system_event", priority: str = "medium"):
        """Send a manual notification to a user"""
        try:
            notification_type_enum = NotificationType(notification_type)
            priority_enum = NotificationPriority(priority)
            
            await self._create_notification(
                notification_type_enum,
                priority_enum,
                user_id,
                title,
                message,
                {"manual": True},
                "system",
                "both"
            )
            
            return {"success": True, "message": "Notification queued"}
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid notification type or priority: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_notification_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notification history for a user"""
        try:
            user_notifications = [n for n in self.notification_history if n.user_id == user_id]
            user_notifications.sort(key=lambda x: x.created_at, reverse=True)
            
            return [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "priority": n.priority.value,
                    "title": n.title,
                    "message": n.message,
                    "data": n.data,
                    "source_project": n.source_project,
                    "delivered": n.delivered,
                    "created_at": n.created_at.isoformat(),
                    "delivered_at": n.delivered_at.isoformat() if n.delivered_at else None
                }
                for n in user_notifications[:limit]
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification history: {e}")
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            "is_running": self.is_running,
            "active_connections": self.connection_manager.get_connection_count(),
            "notification_queue_size": len(self.notification_queue),
            "notification_history_size": len(self.notification_history),
            "background_tasks": len(self.background_tasks)
        }

# FastAPI integration
app = FastAPI(title="Real-time Cross-Project Notifications", version="1.0.0")
notification_service = RealtimeCrossProjectNotifications()

@app.on_event("startup")
async def startup_event():
    """Start notification service on startup"""
    await notification_service.start_service()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop notification service on shutdown"""
    await notification_service.stop_service()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    connection_id = await notification_service.connection_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle ping/pong for connection health
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
    except WebSocketDisconnect:
        notification_service.connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        notification_service.connection_manager.disconnect(connection_id)

@app.post("/notifications/send")
async def send_notification(user_id: str, title: str, message: str, 
                          notification_type: str = "system_event", priority: str = "medium"):
    """Send a manual notification"""
    return await notification_service.send_manual_notification(
        user_id, title, message, notification_type, priority
    )

@app.get("/notifications/history/{user_id}")
async def get_notification_history(user_id: str, limit: int = 50):
    """Get notification history for a user"""
    history = await notification_service.get_notification_history(user_id, limit)
    return {"user_id": user_id, "notifications": history}

@app.get("/notifications/status")
async def get_service_status():
    """Get notification service status"""
    return notification_service.get_service_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8903)

