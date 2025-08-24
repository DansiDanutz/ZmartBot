"""REST API Server for managing alerts and system configuration."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

from ..core.engine import AlertEngine
from ..core.models import (
    AlertConfig, AlertCondition, AlertType, TimeFrame, 
    SystemMetrics, UserConfig
)
from .trading_bot_connector import TradingBotConnector, WebhookTradingBot, ZmartTradingBot

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class CreateAlertRequest(BaseModel):
    user_id: str
    symbol: str
    alert_type: AlertType
    conditions: List[AlertCondition]
    message: Optional[str] = None
    webhook_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    max_triggers: Optional[int] = None
    cooldown_minutes: Optional[int] = 5

class UpdateAlertRequest(BaseModel):
    is_active: Optional[bool] = None
    message: Optional[str] = None
    webhook_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    max_triggers: Optional[int] = None
    cooldown_minutes: Optional[int] = None

class AddBotRequest(BaseModel):
    bot_id: str
    bot_type: str  # 'webhook' or 'zmart'
    config: Dict[str, Any]

class TestWebhookRequest(BaseModel):
    webhook_url: str

class AlertResponse(BaseModel):
    id: str
    user_id: str
    symbol: str
    alert_type: AlertType
    conditions: List[AlertCondition]
    message: Optional[str]
    webhook_url: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    max_triggers: Optional[int]
    cooldown_minutes: Optional[int]

class SystemStatusResponse(BaseModel):
    status: str
    timestamp: str
    metrics: SystemMetrics
    components: Dict[str, str]


class AlertAPIServer:
    """REST API server for the Symbol Alerts System."""
    
    def __init__(self, alert_engine: AlertEngine, trading_connector: TradingBotConnector):
        self.alert_engine = alert_engine
        self.trading_connector = trading_connector
        self.app = FastAPI(
            title="Symbol Alerts API",
            description="REST API for managing symbol alerts and trading bot integration",
            version="1.0.0"
        )
        self.security = HTTPBearer(auto_error=False)
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/health")
        async def health_check():
            """System health check."""
            return await self.alert_engine.health_check()
        
        @self.app.get("/status", response_model=SystemStatusResponse)
        async def get_system_status():
            """Get comprehensive system status."""
            health = await self.alert_engine.health_check()
            metrics = await self.alert_engine.get_system_metrics()
            
            return SystemStatusResponse(
                status=health['status'],
                timestamp=health['timestamp'],
                metrics=metrics,
                components=health['components']
            )
        
        @self.app.post("/alerts", response_model=AlertResponse)
        async def create_alert(request: CreateAlertRequest):
            """Create a new alert."""
            try:
                alert_config = AlertConfig(
                    user_id=request.user_id,
                    symbol=request.symbol,
                    alert_type=request.alert_type,
                    conditions=request.conditions,
                    message=request.message,
                    webhook_url=request.webhook_url,
                    expires_at=request.expires_at,
                    max_triggers=request.max_triggers,
                    cooldown_minutes=request.cooldown_minutes
                )
                
                alert_id = await self.alert_engine.add_alert(alert_config)
                alert_config.id = alert_id
                
                return AlertResponse(**alert_config.dict())
                
            except Exception as e:
                logger.error(f"Error creating alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/alerts", response_model=List[AlertResponse])
        async def list_alerts(user_id: Optional[str] = None):
            """List all alerts, optionally filtered by user."""
            try:
                alerts = await self.alert_engine.list_alerts(user_id)
                return [AlertResponse(**alert.dict()) for alert in alerts]
            except Exception as e:
                logger.error(f"Error listing alerts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/alerts/{alert_id}", response_model=AlertResponse)
        async def get_alert(alert_id: str):
            """Get specific alert by ID."""
            try:
                alert = await self.alert_engine.get_alert(alert_id)
                if not alert:
                    raise HTTPException(status_code=404, detail="Alert not found")
                return AlertResponse(**alert.dict())
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/alerts/{alert_id}", response_model=AlertResponse)
        async def update_alert(alert_id: str, request: UpdateAlertRequest):
            """Update an existing alert."""
            try:
                alert = await self.alert_engine.get_alert(alert_id)
                if not alert:
                    raise HTTPException(status_code=404, detail="Alert not found")
                
                # Update fields
                if request.is_active is not None:
                    if request.is_active:
                        await self.alert_engine.resume_alert(alert_id)
                    else:
                        await self.alert_engine.pause_alert(alert_id)
                
                # Note: For simplicity, other fields would require removing and recreating the alert
                # In a production system, you'd implement proper update functionality
                
                updated_alert = await self.alert_engine.get_alert(alert_id)
                return AlertResponse(**updated_alert.dict())
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error updating alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/alerts/{alert_id}")
        async def delete_alert(alert_id: str):
            """Delete an alert."""
            try:
                success = await self.alert_engine.remove_alert(alert_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Alert not found")
                return {"message": "Alert deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/alerts/{alert_id}/pause")
        async def pause_alert(alert_id: str):
            """Pause an alert."""
            try:
                success = await self.alert_engine.pause_alert(alert_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Alert not found")
                return {"message": "Alert paused successfully"}
            except Exception as e:
                logger.error(f"Error pausing alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/alerts/{alert_id}/resume")
        async def resume_alert(alert_id: str):
            """Resume a paused alert."""
            try:
                success = await self.alert_engine.resume_alert(alert_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Alert not found")
                return {"message": "Alert resumed successfully"}
            except Exception as e:
                logger.error(f"Error resuming alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/alerts/{alert_id}/history")
        async def get_alert_history(alert_id: str):
            """Get trigger history for an alert."""
            try:
                history = await self.alert_engine.get_trigger_history(alert_id)
                return {"alert_id": alert_id, "triggers": history}
            except Exception as e:
                logger.error(f"Error getting alert history: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/market/{symbol}")
        async def get_market_data(symbol: str):
            """Get latest market data for a symbol."""
            try:
                data = await self.alert_engine.get_market_data(symbol)
                if not data:
                    raise HTTPException(status_code=404, detail="Market data not found")
                return data.dict()
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting market data: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/technical/{symbol}/{timeframe}")
        async def get_technical_data(symbol: str, timeframe: TimeFrame):
            """Get technical indicators for a symbol and timeframe."""
            try:
                data = await self.alert_engine.get_technical_data(symbol, timeframe)
                if not data:
                    raise HTTPException(status_code=404, detail="Technical data not found")
                return data.dict()
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting technical data: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/webhook/test")
        async def test_webhook(request: TestWebhookRequest):
            """Test webhook connectivity."""
            try:
                result = await self.alert_engine.test_webhook(request.webhook_url)
                return result
            except Exception as e:
                logger.error(f"Error testing webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/bots")
        async def add_trading_bot(request: AddBotRequest):
            """Add a trading bot to the system."""
            try:
                if request.bot_type == 'webhook':
                    bot = WebhookTradingBot(
                        webhook_url=request.config['webhook_url'],
                        api_key=request.config.get('api_key')
                    )
                elif request.bot_type == 'zmart':
                    bot = ZmartTradingBot(
                        api_key=request.config['api_key'],
                        api_secret=request.config['api_secret'],
                        passphrase=request.config['passphrase'],
                        sandbox=request.config.get('sandbox', False),
                        sub_account=request.config.get('sub_account', 'ZmartBot')
                    )
                else:
                    raise HTTPException(status_code=400, detail="Invalid bot type")
                
                await self.trading_connector.add_bot(request.bot_id, bot)
                return {"message": f"Bot {request.bot_id} added successfully"}
                
            except Exception as e:
                logger.error(f"Error adding bot: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/bots/{bot_id}")
        async def remove_trading_bot(bot_id: str):
            """Remove a trading bot from the system."""
            try:
                await self.trading_connector.remove_bot(bot_id)
                return {"message": f"Bot {bot_id} removed successfully"}
            except Exception as e:
                logger.error(f"Error removing bot: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/bots/positions")
        async def get_all_positions():
            """Get positions from all connected bots."""
            try:
                positions = await self.trading_connector.get_all_positions()
                return positions
            except Exception as e:
                logger.error(f"Error getting positions: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/bots/balances")
        async def get_all_balances():
            """Get balances from all connected bots."""
            try:
                balances = await self.trading_connector.get_all_balances()
                return balances
            except Exception as e:
                logger.error(f"Error getting balances: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/bots/health")
        async def check_bots_health():
            """Check health of all connected bots."""
            try:
                health = await self.trading_connector.health_check_all()
                return health
            except Exception as e:
                logger.error(f"Error checking bot health: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/stats/delivery")
        async def get_delivery_stats():
            """Get notification delivery statistics."""
            try:
                stats = await self.alert_engine.get_delivery_stats()
                return stats
            except Exception as e:
                logger.error(f"Error getting delivery stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/stats/failed-deliveries")
        async def get_failed_deliveries():
            """Get failed delivery attempts."""
            try:
                failed = await self.alert_engine.get_failed_deliveries()
                return failed
            except Exception as e:
                logger.error(f"Error getting failed deliveries: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the API server."""
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

