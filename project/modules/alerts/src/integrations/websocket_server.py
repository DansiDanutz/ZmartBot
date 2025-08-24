"""WebSocket Server for real-time alert updates and market data streaming."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, Any
import websockets
from websockets.server import WebSocketServerProtocol

from ..core.engine import AlertEngine
from ..core.models import AlertTrigger, MarketData

logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket server for real-time communication with clients."""
    
    def __init__(self, alert_engine: AlertEngine):
        self.alert_engine = alert_engine
        self.clients: Set[WebSocketServerProtocol] = set()
        self.subscriptions: Dict[WebSocketServerProtocol, Dict[str, Any]] = {}
        self.server = None
        
    async def start_server(self, host: str = "0.0.0.0", port: int = 8001):
        """Start the WebSocket server."""
        self.server = await websockets.serve(
            self.handle_client,
            host,
            port,
            ping_interval=20,
            ping_timeout=10
        )
        logger.info(f"WebSocket server started on {host}:{port}")
    
    async def stop_server(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket client connection."""
        self.clients.add(websocket)
        self.subscriptions[websocket] = {
            'alerts': set(),
            'symbols': set(),
            'user_id': None
        }
        
        logger.info(f"New WebSocket client connected: {websocket.remote_address}")
        
        try:
            # Send welcome message
            await self.send_to_client(websocket, {
                'type': 'welcome',
                'message': 'Connected to Symbol Alerts WebSocket',
                'timestamp': datetime.now().isoformat()
            })
            
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"Error handling client {websocket.remote_address}: {e}")
        finally:
            self.clients.discard(websocket)
            if websocket in self.subscriptions:
                del self.subscriptions[websocket]
    
    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe_alerts':
                await self.handle_subscribe_alerts(websocket, data)
            elif message_type == 'subscribe_symbols':
                await self.handle_subscribe_symbols(websocket, data)
            elif message_type == 'unsubscribe_alerts':
                await self.handle_unsubscribe_alerts(websocket, data)
            elif message_type == 'unsubscribe_symbols':
                await self.handle_unsubscribe_symbols(websocket, data)
            elif message_type == 'get_alerts':
                await self.handle_get_alerts(websocket, data)
            elif message_type == 'get_market_data':
                await self.handle_get_market_data(websocket, data)
            elif message_type == 'ping':
                await self.send_to_client(websocket, {'type': 'pong'})
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(websocket, "Internal server error")
    
    async def handle_subscribe_alerts(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle alert subscription request."""
        user_id = data.get('user_id')
        alert_ids = data.get('alert_ids', [])
        
        if user_id:
            self.subscriptions[websocket]['user_id'] = user_id
        
        for alert_id in alert_ids:
            self.subscriptions[websocket]['alerts'].add(alert_id)
        
        await self.send_to_client(websocket, {
            'type': 'subscription_confirmed',
            'subscription_type': 'alerts',
            'alert_ids': alert_ids,
            'user_id': user_id
        })
        
        logger.info(f"Client subscribed to alerts: {alert_ids}")
    
    async def handle_subscribe_symbols(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle symbol data subscription request."""
        symbols = data.get('symbols', [])
        
        for symbol in symbols:
            self.subscriptions[websocket]['symbols'].add(symbol)
        
        await self.send_to_client(websocket, {
            'type': 'subscription_confirmed',
            'subscription_type': 'symbols',
            'symbols': symbols
        })
        
        logger.info(f"Client subscribed to symbols: {symbols}")
    
    async def handle_unsubscribe_alerts(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle alert unsubscription request."""
        alert_ids = data.get('alert_ids', [])
        
        for alert_id in alert_ids:
            self.subscriptions[websocket]['alerts'].discard(alert_id)
        
        await self.send_to_client(websocket, {
            'type': 'unsubscription_confirmed',
            'subscription_type': 'alerts',
            'alert_ids': alert_ids
        })
    
    async def handle_unsubscribe_symbols(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle symbol unsubscription request."""
        symbols = data.get('symbols', [])
        
        for symbol in symbols:
            self.subscriptions[websocket]['symbols'].discard(symbol)
        
        await self.send_to_client(websocket, {
            'type': 'unsubscription_confirmed',
            'subscription_type': 'symbols',
            'symbols': symbols
        })
    
    async def handle_get_alerts(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle request for alert list."""
        user_id = data.get('user_id')
        
        try:
            alerts = await self.alert_engine.list_alerts(user_id)
            await self.send_to_client(websocket, {
                'type': 'alerts_list',
                'alerts': [alert.dict() for alert in alerts],
                'user_id': user_id
            })
        except Exception as e:
            await self.send_error(websocket, f"Error getting alerts: {str(e)}")
    
    async def handle_get_market_data(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle request for market data."""
        symbol = data.get('symbol')
        
        if not symbol:
            await self.send_error(websocket, "Symbol is required")
            return
        
        try:
            market_data = await self.alert_engine.get_market_data(symbol)
            if market_data:
                await self.send_to_client(websocket, {
                    'type': 'market_data',
                    'symbol': symbol,
                    'data': market_data.dict()
                })
            else:
                await self.send_error(websocket, f"No market data found for {symbol}")
        except Exception as e:
            await self.send_error(websocket, f"Error getting market data: {str(e)}")
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, data: Dict):
        """Send data to a specific client."""
        try:
            message = json.dumps(data, default=str)
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Attempted to send to closed connection")
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send error message to client."""
        await self.send_to_client(websocket, {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast_alert(self, alert_trigger: AlertTrigger):
        """Broadcast alert trigger to subscribed clients."""
        message = {
            'type': 'alert_triggered',
            'alert_trigger': alert_trigger.dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to clients subscribed to this specific alert
        for websocket, subscription in self.subscriptions.items():
            if alert_trigger.alert_id in subscription['alerts']:
                await self.send_to_client(websocket, message)
        
        # Send to clients subscribed to this user's alerts
        for websocket, subscription in self.subscriptions.items():
            if (subscription['user_id'] and 
                subscription['user_id'] == alert_trigger.alert_id.split('_')[0]):  # Assuming alert_id format
                await self.send_to_client(websocket, message)
        
        logger.info(f"Broadcasted alert trigger: {alert_trigger.alert_id}")
    
    async def broadcast_market_data(self, market_data: MarketData):
        """Broadcast market data to subscribed clients."""
        message = {
            'type': 'market_data_update',
            'symbol': market_data.symbol,
            'data': market_data.dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to clients subscribed to this symbol
        for websocket, subscription in self.subscriptions.items():
            if market_data.symbol in subscription['symbols']:
                await self.send_to_client(websocket, message)
    
    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status to all clients."""
        message = {
            'type': 'system_status',
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all connected clients
        for websocket in self.clients.copy():
            await self.send_to_client(websocket, message)
    
    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)
    
    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics."""
        total_alert_subscriptions = sum(
            len(sub['alerts']) for sub in self.subscriptions.values()
        )
        total_symbol_subscriptions = sum(
            len(sub['symbols']) for sub in self.subscriptions.values()
        )
        
        return {
            'connected_clients': len(self.clients),
            'total_alert_subscriptions': total_alert_subscriptions,
            'total_symbol_subscriptions': total_symbol_subscriptions,
            'unique_subscribed_symbols': len(set().union(
                *[sub['symbols'] for sub in self.subscriptions.values()]
            ))
        }

