#!/usr/bin/env python3
"""
ZmartBot WebSocket Service
Real-time data streaming and communication service
"""

import os
import sys
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZmartBot WebSocket Service",
    description="Real-time data streaming and communication service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.rooms: Dict[str, List[WebSocket]] = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_stats["total_connections"] += 1
        self.connection_stats["active_connections"] += 1
        logger.info(f"WebSocket connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_stats["active_connections"] -= 1
            logger.info(f"WebSocket disconnected. Total active: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            self.connection_stats["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                self.connection_stats["messages_sent"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def join_room(self, websocket: WebSocket, room: str):
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(websocket)
        logger.info(f"WebSocket joined room: {room}")

    async def leave_room(self, websocket: WebSocket, room: str):
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
            logger.info(f"WebSocket left room: {room}")

    async def broadcast_to_room(self, message: str, room: str):
        if room in self.rooms:
            disconnected = []
            for connection in self.rooms[room]:
                try:
                    await connection.send_text(message)
                    self.connection_stats["messages_sent"] += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to room {room}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
                if room in self.rooms:
                    self.rooms[room].remove(connection)

manager = ConnectionManager()

# Health check endpoints
@app.get("/health")
async def health_check():
    """Liveness probe endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zmart-websocket",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zmart-websocket",
        "active_connections": len(manager.active_connections)
    }

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for observability"""
    return {
        "service": "zmart-websocket",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "active_connections": len(manager.active_connections),
            "total_connections": manager.connection_stats["total_connections"],
            "messages_sent": manager.connection_stats["messages_sent"],
            "messages_received": manager.connection_stats["messages_received"],
            "rooms_count": len(manager.rooms)
        }
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            manager.connection_stats["messages_received"] += 1
            
            try:
                message = json.loads(data)
                logger.info(f"Received message: {message}")
                
                # Handle different message types
                if message.get("type") == "join_room":
                    await manager.join_room(websocket, message.get("room", "default"))
                    await manager.send_personal_message(
                        json.dumps({"type": "room_joined", "room": message.get("room", "default")}),
                        websocket
                    )
                elif message.get("type") == "leave_room":
                    await manager.leave_room(websocket, message.get("room", "default"))
                    await manager.send_personal_message(
                        json.dumps({"type": "room_left", "room": message.get("room", "default")}),
                        websocket
                    )
                else:
                    # Echo message back
                    await manager.send_personal_message(data, websocket)
                    
            except json.JSONDecodeError:
                # Send raw message back
                await manager.send_personal_message(data, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API endpoints
@app.get("/api/v1/websocket/status")
async def get_websocket_status():
    """Get WebSocket service status"""
    return {
        "status": "active",
        "active_connections": len(manager.active_connections),
        "total_connections": manager.connection_stats["total_connections"],
        "messages_sent": manager.connection_stats["messages_sent"],
        "messages_received": manager.connection_stats["messages_received"],
        "rooms": list(manager.rooms.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/websocket/connections")
async def get_connections_count():
    """Get active connections count"""
    return {
        "active_connections": len(manager.active_connections),
        "total_connections": manager.connection_stats["total_connections"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/websocket/broadcast")
async def broadcast_message(message: dict):
    """Broadcast message to all connected clients"""
    try:
        message_text = json.dumps(message)
        await manager.broadcast(message_text)
        return {
            "success": True,
            "message": "Message broadcasted successfully",
            "recipients": len(manager.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/websocket/rooms")
async def get_rooms():
    """Get available rooms"""
    return {
        "rooms": list(manager.rooms.keys()),
        "room_details": {
            room: len(connections) for room, connections in manager.rooms.items()
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/websocket/join")
async def join_room(room: str, websocket: WebSocket):
    """Join WebSocket room"""
    await manager.join_room(websocket, room)
    return {
        "success": True,
        "message": f"Joined room: {room}",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/connections/list")
async def list_connections():
    """List active connections"""
    return {
        "connections": [
            {
                "id": i,
                "connected_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            for i in range(len(manager.active_connections))
        ],
        "total": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/connections/stats")
async def get_connection_stats():
    """Get connection statistics"""
    return {
        "stats": manager.connection_stats,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/messages/send")
async def send_message(message: dict):
    """Send message to specific client (placeholder)"""
    return {
        "success": True,
        "message": "Message sent successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/messages/history")
async def get_message_history():
    """Get message history (placeholder)"""
    return {
        "messages": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/messages/broadcast")
async def broadcast_message_endpoint(message: dict):
    """Broadcast message endpoint"""
    try:
        message_text = json.dumps(message)
        await manager.broadcast(message_text)
        return {
            "success": True,
            "message": "Message broadcasted successfully",
            "recipients": len(manager.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/messages/stats")
async def get_message_stats():
    """Get message statistics"""
    return {
        "stats": {
            "messages_sent": manager.connection_stats["messages_sent"],
            "messages_received": manager.connection_stats["messages_received"],
            "active_connections": len(manager.active_connections)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ZmartBot WebSocket Service")
    parser.add_argument("--port", type=int, default=8009, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()
    
    logger.info(f"Starting ZmartBot WebSocket Service on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
