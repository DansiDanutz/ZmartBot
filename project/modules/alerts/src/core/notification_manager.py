"""Notification Manager for delivering alerts through multiple channels."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from .models import AlertTrigger, AlertConfig, WebhookPayload

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages alert notifications through various channels."""
    
    def __init__(self):
        self.webhook_session: Optional[aiohttp.ClientSession] = None
        self.delivery_queue = asyncio.Queue()
        self.failed_deliveries: List[Dict] = []
        self.delivery_stats = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
        
    async def initialize(self):
        """Initialize notification manager."""
        self.webhook_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': 'SymbolAlerts/1.0'}
        )
        
        # Start delivery worker
        asyncio.create_task(self._delivery_worker())
        
        logger.info("Notification Manager initialized")
    
    async def shutdown(self):
        """Shutdown notification manager."""
        if self.webhook_session:
            await self.webhook_session.close()
        logger.info("Notification Manager shutdown")
    
    async def send_alert(self, trigger: AlertTrigger, alert_config: AlertConfig):
        """Send alert through configured channels."""
        try:
            # Create webhook payload
            payload = WebhookPayload(
                alert_trigger=trigger,
                metadata={
                    'user_id': alert_config.user_id,
                    'alert_id': alert_config.id,
                    'timestamp': trigger.timestamp.isoformat()
                }
            )
            
            # Queue for webhook delivery
            if alert_config.webhook_url:
                await self.delivery_queue.put({
                    'type': 'webhook',
                    'url': alert_config.webhook_url,
                    'payload': payload.dict(),
                    'alert_id': alert_config.id,
                    'retry_count': 0,
                    'created_at': datetime.now()
                })
            
            # Log the alert
            logger.info(f"Alert queued for delivery: {trigger.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def _delivery_worker(self):
        """Background worker for processing delivery queue."""
        while True:
            try:
                # Get next delivery task
                delivery_task = await self.delivery_queue.get()
                
                success = False
                if delivery_task['type'] == 'webhook':
                    success = await self._send_webhook(delivery_task)
                
                # Update stats
                self.delivery_stats['total_sent'] += 1
                if success:
                    self.delivery_stats['successful'] += 1
                else:
                    self.delivery_stats['failed'] += 1
                    
                    # Retry logic
                    if delivery_task['retry_count'] < 3:
                        delivery_task['retry_count'] += 1
                        self.delivery_stats['retries'] += 1
                        
                        # Exponential backoff
                        delay = 2 ** delivery_task['retry_count']
                        await asyncio.sleep(delay)
                        await self.delivery_queue.put(delivery_task)
                    else:
                        # Max retries reached, log failure
                        self.failed_deliveries.append(delivery_task)
                        logger.error(f"Failed to deliver alert after 3 retries: {delivery_task['alert_id']}")
                
                self.delivery_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in delivery worker: {e}")
                await asyncio.sleep(1)
    
    async def _send_webhook(self, delivery_task: Dict) -> bool:
        """Send webhook notification."""
        try:
            url = delivery_task['url']
            payload = delivery_task['payload']
            
            async with self.webhook_session.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    logger.info(f"Webhook delivered successfully to {url}")
                    return True
                else:
                    logger.warning(f"Webhook delivery failed: {response.status} - {url}")
                    return False
                    
        except asyncio.TimeoutError:
            logger.warning(f"Webhook timeout: {delivery_task['url']}")
            return False
        except Exception as e:
            logger.error(f"Webhook delivery error: {e}")
            return False
    
    async def send_test_webhook(self, webhook_url: str) -> Dict[str, any]:
        """Send a test webhook to verify connectivity."""
        test_payload = {
            'event_type': 'test',
            'message': 'Test webhook from Symbol Alerts System',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            async with self.webhook_session.post(
                webhook_url,
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                return {
                    'success': response.status == 200,
                    'status_code': response.status,
                    'response_text': await response.text()
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_delivery_stats(self) -> Dict[str, any]:
        """Get delivery statistics."""
        return {
            **self.delivery_stats,
            'queue_size': self.delivery_queue.qsize(),
            'failed_deliveries': len(self.failed_deliveries)
        }
    
    async def get_failed_deliveries(self) -> List[Dict]:
        """Get list of failed deliveries."""
        return self.failed_deliveries.copy()
    
    async def retry_failed_delivery(self, delivery_id: str) -> bool:
        """Retry a specific failed delivery."""
        for i, delivery in enumerate(self.failed_deliveries):
            if delivery.get('alert_id') == delivery_id:
                delivery['retry_count'] = 0  # Reset retry count
                await self.delivery_queue.put(delivery)
                del self.failed_deliveries[i]
                return True
        return False
    
    async def clear_failed_deliveries(self):
        """Clear all failed deliveries."""
        self.failed_deliveries.clear()
        logger.info("Cleared all failed deliveries")

