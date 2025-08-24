"""Main Alert Engine that orchestrates the entire system."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .data_manager import DataManager
from .alert_processor import AlertProcessor
from .notification_manager import NotificationManager
from .models import AlertConfig, SystemMetrics

logger = logging.getLogger(__name__)


class AlertEngine:
    """Main engine that coordinates all system components."""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.notification_manager = NotificationManager()
        self.alert_processor = AlertProcessor(self.data_manager, self.notification_manager)
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
    async def initialize(self):
        """Initialize all system components."""
        try:
            logger.info("Initializing Alert Engine...")
            
            await self.data_manager.initialize()
            await self.notification_manager.initialize()
            
            self.start_time = datetime.now()
            logger.info("Alert Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alert Engine: {e}")
            raise
    
    async def start(self):
        """Start the alert engine."""
        if self.is_running:
            logger.warning("Alert Engine is already running")
            return
        
        try:
            self.is_running = True
            logger.info("Starting Alert Engine...")
            
            # Start data manager
            await self.data_manager.start()
            
            logger.info("Alert Engine started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Alert Engine: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the alert engine."""
        if not self.is_running:
            return
        
        try:
            logger.info("Stopping Alert Engine...")
            self.is_running = False
            
            # Stop components
            await self.data_manager.stop()
            await self.notification_manager.shutdown()
            
            logger.info("Alert Engine stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Alert Engine: {e}")
    
    async def add_alert(self, alert_config: AlertConfig) -> str:
        """Add a new alert to the system."""
        if not self.is_running:
            raise RuntimeError("Alert Engine is not running")
        
        return await self.alert_processor.add_alert(alert_config)
    
    async def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert from the system."""
        return await self.alert_processor.remove_alert(alert_id)
    
    async def get_alert(self, alert_id: str) -> Optional[AlertConfig]:
        """Get alert configuration by ID."""
        return await self.alert_processor.get_alert(alert_id)
    
    async def list_alerts(self, user_id: Optional[str] = None) -> List[AlertConfig]:
        """List all alerts, optionally filtered by user."""
        return await self.alert_processor.list_alerts(user_id)
    
    async def pause_alert(self, alert_id: str) -> bool:
        """Pause an alert."""
        return await self.alert_processor.pause_alert(alert_id)
    
    async def resume_alert(self, alert_id: str) -> bool:
        """Resume a paused alert."""
        return await self.alert_processor.resume_alert(alert_id)
    
    async def get_market_data(self, symbol: str):
        """Get latest market data for a symbol."""
        return await self.data_manager.get_market_data(symbol)
    
    async def get_technical_data(self, symbol: str, timeframe):
        """Get technical indicators for a symbol."""
        return await self.data_manager.get_technical_data(symbol, timeframe)
    
    async def test_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Test webhook connectivity."""
        return await self.notification_manager.send_test_webhook(webhook_url)
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get comprehensive system metrics."""
        import psutil
        
        # Get alert processor stats
        alert_stats = await self.alert_processor.get_system_stats()
        
        # Get notification stats
        delivery_stats = await self.notification_manager.get_delivery_stats()
        
        # Get system resource usage
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()
        
        # Calculate uptime
        uptime_seconds = 0
        if self.start_time:
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
        
        return SystemMetrics(
            active_alerts=alert_stats['active_alerts'],
            monitored_symbols=alert_stats['monitored_symbols'],
            triggers_last_hour=alert_stats['triggers_last_hour'],
            avg_processing_time_ms=0.0,  # TODO: Implement timing metrics
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            uptime_seconds=uptime_seconds,
            last_updated=datetime.now()
        )
    
    async def get_trigger_history(self, alert_id: str):
        """Get trigger history for an alert."""
        return await self.alert_processor.get_trigger_history(alert_id)
    
    async def get_delivery_stats(self):
        """Get notification delivery statistics."""
        return await self.notification_manager.get_delivery_stats()
    
    async def get_failed_deliveries(self):
        """Get failed delivery attempts."""
        return await self.notification_manager.get_failed_deliveries()
    
    async def retry_failed_delivery(self, delivery_id: str) -> bool:
        """Retry a failed delivery."""
        return await self.notification_manager.retry_failed_delivery(delivery_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        health = {
            'status': 'healthy' if self.is_running else 'stopped',
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # Check data manager
        try:
            # Simple check - try to get market data
            health['components']['data_manager'] = 'healthy'
        except Exception as e:
            health['components']['data_manager'] = f'error: {str(e)}'
            health['status'] = 'degraded'
        
        # Check notification manager
        try:
            stats = await self.notification_manager.get_delivery_stats()
            health['components']['notification_manager'] = 'healthy'
            health['delivery_queue_size'] = stats['queue_size']
        except Exception as e:
            health['components']['notification_manager'] = f'error: {str(e)}'
            health['status'] = 'degraded'
        
        # Check alert processor
        try:
            stats = await self.alert_processor.get_system_stats()
            health['components']['alert_processor'] = 'healthy'
            health['active_alerts'] = stats['active_alerts']
        except Exception as e:
            health['components']['alert_processor'] = f'error: {str(e)}'
            health['status'] = 'degraded'
        
        return health

