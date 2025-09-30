#!/usr/bin/env python3
"""
WebSocket Routes for Real-time Data Streaming
"""

import json
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.services.websocket_service import get_websocket_service, WebSocketMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.price_subscribers: List[WebSocket] = []
        self.trade_subscribers: List[WebSocket] = []
        self.score_subscribers: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"📡 New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.price_subscribers:
            self.price_subscribers.remove(websocket)
        if websocket in self.trade_subscribers:
            self.trade_subscribers.remove(websocket)
        if websocket in self.score_subscribers:
            self.score_subscribers.remove(websocket)
        logger.info(f"📡 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_price_subscribers(self, message: str):
        """Send price updates to price subscribers"""
        disconnected = []
        for connection in self.price_subscribers:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Error sending price update: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_trade_subscribers(self, message: str):
        """Send trade signals to trade subscribers"""
        disconnected = []
        for connection in self.trade_subscribers:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Error sending trade signal: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_score_subscribers(self, message: str):
        """Send scoring updates to score subscribers"""
        disconnected = []
        for connection in self.score_subscribers:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Error sending score update: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

# Global connection manager
manager = ConnectionManager()

@router.get("/")
async def get_websocket_info():
    """Get WebSocket connection information"""
    return {
        "active_connections": len(manager.active_connections),
        "price_subscribers": len(manager.price_subscribers),
        "trade_subscribers": len(manager.trade_subscribers),
        "score_subscribers": len(manager.score_subscribers)
    }

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle subscription requests
            if message.get("type") == "subscribe":
                subscription_type = message.get("channel", "all")
                
                if subscription_type == "price":
                    manager.price_subscribers.append(websocket)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscription", "channel": "price", "status": "subscribed"}),
                        websocket
                    )
                
                elif subscription_type == "trade":
                    manager.trade_subscribers.append(websocket)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscription", "channel": "trade", "status": "subscribed"}),
                        websocket
                    )
                
                elif subscription_type == "score":
                    manager.score_subscribers.append(websocket)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscription", "channel": "score", "status": "subscribed"}),
                        websocket
                    )
                
                elif subscription_type == "all":
                    manager.price_subscribers.append(websocket)
                    manager.trade_subscribers.append(websocket)
                    manager.score_subscribers.append(websocket)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscription", "channel": "all", "status": "subscribed"}),
                        websocket
                    )
            
            # Handle unsubscribe requests
            elif message.get("type") == "unsubscribe":
                subscription_type = message.get("channel", "all")
                
                if subscription_type == "price" and websocket in manager.price_subscribers:
                    manager.price_subscribers.remove(websocket)
                elif subscription_type == "trade" and websocket in manager.trade_subscribers:
                    manager.trade_subscribers.remove(websocket)
                elif subscription_type == "score" and websocket in manager.score_subscribers:
                    manager.score_subscribers.remove(websocket)
                elif subscription_type == "all":
                    if websocket in manager.price_subscribers:
                        manager.price_subscribers.remove(websocket)
                    if websocket in manager.trade_subscribers:
                        manager.trade_subscribers.remove(websocket)
                    if websocket in manager.score_subscribers:
                        manager.score_subscribers.remove(websocket)
                
                await manager.send_personal_message(
                    json.dumps({"type": "unsubscription", "channel": subscription_type, "status": "unsubscribed"}),
                    websocket
                )
            
            # Handle ping/pong
            elif message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

# WebSocket message handlers
async def handle_price_message(message: WebSocketMessage):
    """Handle price update messages"""
    try:
        price_data = {
            "type": "price_update",
            "source": message.source,
            "symbol": message.symbol,
            "data": message.data,
            "timestamp": message.timestamp
        }
        
        await manager.send_to_price_subscribers(json.dumps(price_data))
        
    except Exception as e:
        logger.error(f"❌ Error handling price message: {e}")

async def handle_trade_message(message: WebSocketMessage):
    """Handle trade signal messages"""
    try:
        trade_data = {
            "type": "trade_signal",
            "source": message.source,
            "symbol": message.symbol,
            "data": message.data,
            "confidence": message.confidence,
            "timestamp": message.timestamp
        }
        
        await manager.send_to_trade_subscribers(json.dumps(trade_data))
        
    except Exception as e:
        logger.error(f"❌ Error handling trade message: {e}")

async def handle_score_message(message: WebSocketMessage):
    """Handle scoring update messages"""
    try:
        score_data = {
            "type": "score_update",
            "source": message.source,
            "symbol": message.symbol,
            "data": message.data,
            "confidence": message.confidence,
            "timestamp": message.timestamp
        }
        
        await manager.send_to_score_subscribers(json.dumps(score_data))
        
    except Exception as e:
        logger.error(f"❌ Error handling score message: {e}")

# Initialize WebSocket service handlers
async def initialize_websocket_handlers():
    """Initialize WebSocket message handlers"""
    try:
        websocket_service = await get_websocket_service()
        
        # Subscribe to different message types
        websocket_service.subscribe_to_price_updates(handle_price_message)
        websocket_service.subscribe_to_trade_signals(handle_trade_message)
        websocket_service.subscribe_to_scoring_updates(handle_score_message)
        
        logger.info("✅ WebSocket handlers initialized")
        
    except Exception as e:
        logger.error(f"❌ Error initializing WebSocket handlers: {e}")

# HTML test page for WebSocket
@router.get("/test", response_class=HTMLResponse)
async def get_websocket_test_page():
    """Get WebSocket test page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZmartBot WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .connected { background: #2d5a2d; }
            .disconnected { background: #5a2d2d; }
            .messages { background: #2a2a2a; padding: 10px; border-radius: 5px; height: 400px; overflow-y: auto; }
            .message { margin: 5px 0; padding: 5px; background: #3a3a3a; border-radius: 3px; }
            button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            .subscribe { background: #4CAF50; color: white; }
            .unsubscribe { background: #f44336; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ZmartBot WebSocket Test</h1>
            
            <div id="status" class="status disconnected">
                Status: Disconnected
            </div>
            
            <div>
                <button class="subscribe" onclick="subscribe('price')">Subscribe to Price Updates</button>
                <button class="subscribe" onclick="subscribe('trade')">Subscribe to Trade Signals</button>
                <button class="subscribe" onclick="subscribe('score')">Subscribe to Score Updates</button>
                <button class="subscribe" onclick="subscribe('all')">Subscribe to All</button>
                <button class="unsubscribe" onclick="unsubscribe('all')">Unsubscribe All</button>
            </div>
            
            <div class="messages" id="messages">
                <div class="message">Waiting for connection...</div>
            </div>
        </div>

        <script>
            let ws = null;
            let connected = false;

            function connect() {
                ws = new WebSocket('ws://localhost:5000/ws/stream');
                
                ws.onopen = function() {
                    connected = true;
                    document.getElementById('status').className = 'status connected';
                    document.getElementById('status').textContent = 'Status: Connected';
                    addMessage('Connected to WebSocket server');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage('Received: ' + JSON.stringify(data, null, 2));
                };
                
                ws.onclose = function() {
                    connected = false;
                    document.getElementById('status').className = 'status disconnected';
                    document.getElementById('status').textContent = 'Status: Disconnected';
                    addMessage('Disconnected from WebSocket server');
                    
                    // Reconnect after 5 seconds
                    setTimeout(connect, 5000);
                };
                
                ws.onerror = function(error) {
                    addMessage('WebSocket error: ' + error);
                };
            }
            
            function subscribe(channel) {
                if (ws && connected) {
                    ws.send(JSON.stringify({
                        type: 'subscribe',
                        channel: channel
                    }));
                    addMessage('Subscribed to ' + channel);
                }
            }
            
            function unsubscribe(channel) {
                if (ws && connected) {
                    ws.send(JSON.stringify({
                        type: 'unsubscribe',
                        channel: channel
                    }));
                    addMessage('Unsubscribed from ' + channel);
                }
            }
            
            function addMessage(message) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                messageDiv.textContent = new Date().toLocaleTimeString() + ': ' + message;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // Connect on page load
            connect();
        </script>
    </body>
    </html>
    """ 