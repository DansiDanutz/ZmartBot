"""
WebSocket Routes for Real-time Communication
Provides WebSocket endpoints for Enhanced Alerts System
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Any
import json
import logging
from datetime import datetime

from ..auth.auth_middleware import auth_manager
from .websocket_manager import connection_manager, start_websocket_health_check

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_user_from_websocket_token(websocket: WebSocket) -> Dict[str, Any]:
    """Extract and validate user from WebSocket token"""
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            raise ValueError("No token provided")
        
        # Verify token
        payload = auth_manager.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            raise ValueError("Invalid token payload")
        
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email"),
            "permissions": payload.get("permissions", {})
        }
        
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        try:
            await websocket.close(code=4001, reason="Authentication failed")
        except:
            pass
        raise

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for alerts system"""
    
    try:
        # Authenticate user
        user = await get_user_from_websocket_token(websocket)
        user_id = user["user_id"]
        
        # Connect to manager
        await connection_manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    await connection_manager.handle_websocket_message(websocket, message)
                    
                except json.JSONDecodeError:
                    await connection_manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }, websocket)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        # Ensure cleanup
        connection_manager.disconnect(websocket)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    try:
        stats = connection_manager.get_connection_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Initialize WebSocket health monitoring
start_websocket_health_check()