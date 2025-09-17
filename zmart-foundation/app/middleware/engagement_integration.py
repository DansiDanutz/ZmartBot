"""
Engagement System Integration Middleware
Automatically integrates engagement system with trading signals, pool updates, and other events
"""

import asyncio
import aiohttp
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json

logger = logging.getLogger(__name__)

ENGAGEMENT_SERVICE_URL = "http://localhost:8350"

class EngagementIntegrationMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically integrate events with engagement system"""
    
    def __init__(self, app):
        super().__init__(app)
        self.session = None
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def notify_engagement_system(self, event_type: str, data: Dict[str, Any]):
        """Send notification to engagement system"""
        try:
            session = await self.get_session()
            
            # Route different event types to appropriate engagement endpoints
            if event_type == "signal_created":
                await self.handle_signal_event(session, data)
            elif event_type == "pool_updated":
                await self.handle_pool_event(session, data)
            elif event_type == "alert_triggered":
                await self.handle_alert_event(session, data)
                
        except Exception as e:
            logger.warning(f"Failed to notify engagement system: {e}")
    
    async def handle_signal_event(self, session: aiohttp.ClientSession, data: Dict):
        """Handle trading signal events"""
        try:
            asset = data.get("symbol", "BTC").replace("USDT", "")
            signal_type = data.get("type", "unknown")
            score = data.get("score", 0)
            
            alert_data = {
                "asset": asset,
                "alert_type": f"trading_signal_{signal_type}",
                "urgency": min(10, max(1, int(score * 10))),
                "message": f"New {signal_type} signal for {asset} with score {score:.2f}"
            }
            
            async with session.post(
                f"{ENGAGEMENT_SERVICE_URL}/market-alert",
                json=alert_data,
                timeout=5
            ) as response:
                if response.status == 200:
                    logger.info(f"Signal event sent to engagement system: {asset}")
                    
        except Exception as e:
            logger.debug(f"Signal event notification failed: {e}")
    
    async def handle_pool_event(self, session: aiohttp.ClientSession, data: Dict):
        """Handle pool update events"""
        try:
            pool_id = data.get("id")
            status = data.get("status")
            symbol = data.get("symbol", "BTC")
            
            if status in ["expired", "liquidated", "closed"]:
                alert_data = {
                    "asset": symbol,
                    "alert_type": f"pool_{status}",
                    "urgency": 7 if status == "liquidated" else 5,
                    "message": f"Pool {pool_id} has been {status}"
                }
                
                async with session.post(
                    f"{ENGAGEMENT_SERVICE_URL}/market-alert",
                    json=alert_data,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        logger.info(f"Pool event sent to engagement system: {pool_id}")
                        
        except Exception as e:
            logger.debug(f"Pool event notification failed: {e}")
    
    async def handle_alert_event(self, session: aiohttp.ClientSession, data: Dict):
        """Handle general alert events"""
        try:
            alert_data = {
                "asset": data.get("asset", "BTC"),
                "alert_type": data.get("type", "general"),
                "urgency": data.get("urgency", 5),
                "message": data.get("message", "Alert triggered")
            }
            
            async with session.post(
                f"{ENGAGEMENT_SERVICE_URL}/market-alert",
                json=alert_data,
                timeout=5
            ) as response:
                if response.status == 200:
                    logger.info(f"Alert event sent to engagement system")
                    
        except Exception as e:
            logger.debug(f"Alert event notification failed: {e}")
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check for events to forward to engagement system"""
        
        # Process the request normally
        response = await call_next(request)
        
        # Check for events that should trigger engagement notifications
        if request.method == "POST" and response.status_code == 200:
            
            # Handle signal creation
            if "/signals" in str(request.url):
                try:
                    # We can't read response body here easily, so we'll extract from URL/headers
                    # This is a simplified approach - in production you'd want more sophisticated event tracking
                    asyncio.create_task(self.notify_engagement_system("signal_created", {
                        "symbol": request.query_params.get("symbol", "BTC"),
                        "type": "api_signal",
                        "score": 0.7  # Default score
                    }))
                except Exception:
                    pass
            
            # Handle pool updates  
            elif "/pools" in str(request.url):
                try:
                    asyncio.create_task(self.notify_engagement_system("pool_updated", {
                        "id": "pool_from_api",
                        "status": "updated",
                        "symbol": "BTC"
                    }))
                except Exception:
                    pass
        
        return response
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()

# Background task for periodic engagement sync
async def sync_with_engagement_system():
    """Periodic sync with engagement system"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                # Check engagement system health
                async with session.get(f"{ENGAGEMENT_SERVICE_URL}/health", timeout=5) as response:
                    if response.status == 200:
                        logger.debug("Engagement system sync: OK")
                    else:
                        logger.warning("Engagement system sync: Unhealthy")
                        
        except Exception as e:
            logger.debug(f"Engagement system sync failed: {e}")
            
        await asyncio.sleep(60)  # Sync every minute