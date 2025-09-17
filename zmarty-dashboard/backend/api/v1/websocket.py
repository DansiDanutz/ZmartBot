from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List, Set
import json
import asyncio
import uuid
from datetime import datetime

from services.auth_service import AuthService
from services.zmarty_service import ZmartyService
from core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Store active connections per user
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and add to user's connection pool"""
        await websocket.accept()
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        
        self.user_connections[user_id].add(websocket)
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to Zmarty Chat",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]["user_id"]
            
            # Remove from user's connections
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove metadata
            del self.connection_metadata[websocket]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
            # Update last activity
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["last_activity"] = datetime.utcnow()
        except Exception as e:
            print(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, message: dict, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            disconnected = []
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected WebSockets
            for ws in disconnected:
                self.disconnect(ws)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.user_connections.keys()):
            await self.send_to_user(message, user_id)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user"""
        return len(self.user_connections.get(user_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.user_connections.values())
    
    async def heartbeat(self):
        """Send heartbeat to all connections"""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_all(heartbeat_message)

# Global connection manager instance
manager = ConnectionManager()

async def verify_websocket_token(websocket: WebSocket, token: str) -> str:
    """Verify WebSocket authentication token and return user ID"""
    try:
        # Create a temporary database session for authentication
        from core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            auth_service = AuthService(db)
            payload = auth_service.verify_token(token)
            
            if not payload:
                await websocket.close(code=4001, reason="Invalid token")
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user = await auth_service.get_user_by_id(payload.get("sub"))
            if not user:
                await websocket.close(code=4001, reason="User not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            return str(user.id)
    
    except Exception as e:
        await websocket.close(code=4000, reason="Authentication failed")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.websocket("/chat/{token}")
async def websocket_chat_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time chat with Zmarty"""
    try:
        # Verify authentication
        user_id = await verify_websocket_token(websocket, token)
        
        # Connect user
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process different message types
                await process_websocket_message(websocket, user_id, message_data)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            print(f"User {user_id} disconnected from WebSocket")
        
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Server error")
        except:
            pass

async def process_websocket_message(websocket: WebSocket, user_id: str, message_data: dict):
    """Process incoming WebSocket messages"""
    message_type = message_data.get("type")
    
    if message_type == "zmarty_query":
        await handle_zmarty_query(websocket, user_id, message_data)
    
    elif message_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    elif message_type == "typing":
        # Handle typing indicators (could broadcast to other user sessions)
        await manager.send_personal_message({
            "type": "typing_received",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

async def handle_zmarty_query(websocket: WebSocket, user_id: str, message_data: dict):
    """Handle Zmarty AI query through WebSocket"""
    try:
        query = message_data.get("query", "")
        request_type = message_data.get("request_type", "basic_query")
        parameters = message_data.get("parameters", {})
        
        if not query.strip():
            await manager.send_personal_message({
                "type": "error",
                "message": "Query cannot be empty",
                "timestamp": datetime.utcnow().isoformat()
            }, websocket)
            return
        
        # Send processing status
        await manager.send_personal_message({
            "type": "processing_started",
            "message": "Processing your request...",
            "query": query,
            "request_type": request_type,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        # Process request using Zmarty service
        from core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            zmarty_service = ZmartyService(db)
            
            result = await zmarty_service.process_request(
                user_id=uuid.UUID(user_id),
                query=query,
                request_type=request_type,
                parameters=parameters
            )
            
            if result["success"]:
                # Send successful response
                await manager.send_personal_message({
                    "type": "zmarty_response",
                    "request_id": str(result["request_id"]),
                    "query": query,
                    "response": result["response"],
                    "credits_used": result["credits_used"],
                    "processing_time": result["processing_time"],
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
            else:
                # Send error response
                await manager.send_personal_message({
                    "type": "error",
                    "error_code": result.get("error", "unknown_error"),
                    "message": result.get("message", "Request failed"),
                    "credits_refunded": result.get("credits_refunded", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
    
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Failed to process request: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

@router.get("/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_total_connections(),
        "active_users": len(manager.user_connections),
        "connections_per_user": {
            user_id: len(connections) 
            for user_id, connections in manager.user_connections.items()
        }
    }

# Background task for heartbeat
async def heartbeat_task():
    """Background task to send heartbeat messages"""
    while True:
        await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        try:
            await manager.heartbeat()
        except Exception as e:
            print(f"Heartbeat error: {e}")

# Start heartbeat task when module loads
asyncio.create_task(heartbeat_task())