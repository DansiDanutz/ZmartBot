#!/usr/bin/env python3
"""
Notification Service
Handles sending alerts through multiple channels
"""

import logging
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """Notification configuration"""
    webhook_url: Optional[str] = None
    email_enabled: bool = False
    email_recipients: Optional[List[str]] = None
    discord_webhook: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    sms_enabled: bool = False
    sms_recipients: Optional[List[str]] = None

@dataclass
class AlertNotification:
    """Alert notification data"""
    alert_id: str
    symbol: str
    alert_type: str
    trigger_price: float
    conditions_met: Dict[str, Any]
    timestamp: datetime
    priority: str = "medium"  # low, medium, high, critical

class NotificationService:
    """Multi-channel notification service"""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config if config is not None else NotificationConfig()
        self.notification_history: List[AlertNotification] = []
        self.max_history = 1000
        
    async def send_alert_notification(self, notification: AlertNotification) -> Dict[str, bool]:
        """Send alert notification through all configured channels"""
        results = {
            'webhook': False,
            'email': False,
            'discord': False,
            'telegram': False,
            'sms': False
        }
        
        # Add to history
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
            
        # Send through all channels
        tasks = []
        
        if self.config.webhook_url:
            tasks.append(self._send_webhook_notification(notification))
            
        if self.config.email_enabled and self.config.email_recipients:
            tasks.append(self._send_email_notification(notification))
            
        if self.config.discord_webhook:
            tasks.append(self._send_discord_notification(notification))
            
        if self.config.telegram_bot_token and self.config.telegram_chat_id:
            tasks.append(self._send_telegram_notification(notification))
            
        if self.config.sms_enabled and self.config.sms_recipients:
            tasks.append(self._send_sms_notification(notification))
            
        # Execute all notifications concurrently
        if tasks:
            notification_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(notification_results):
                if isinstance(result, dict):
                    for channel, success in result.items():
                        results[channel] = success
                        
        logger.info(f"📢 Notification sent for {notification.symbol}: {results}")
        return results
        
    async def _send_webhook_notification(self, notification: AlertNotification) -> Dict[str, bool]:
        """Send webhook notification"""
        try:
            payload = {
                'alert_id': notification.alert_id,
                'symbol': notification.symbol,
                'type': notification.alert_type,
                'price': notification.trigger_price,
                'conditions': notification.conditions_met,
                'timestamp': notification.timestamp.isoformat(),
                'priority': notification.priority
            }
            
            if not self.config.webhook_url:
                return {'webhook': False}
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.config.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                success = response.status_code in [200, 201, 202]
                logger.info(f"Webhook notification {'sent' if success else 'failed'}: {response.status_code}")
                return {'webhook': success}
                
        except Exception as e:
            logger.error(f"Webhook notification error: {e}")
            return {'webhook': False}
            
    async def _send_email_notification(self, notification: AlertNotification) -> Dict[str, bool]:
        """Send email notification"""
        try:
            # This would integrate with your email service (SendGrid, AWS SES, etc.)
            subject = f"🚨 Alert: {notification.symbol} {notification.alert_type}"
            body = f"""
            Alert Triggered!
            
            Symbol: {notification.symbol}
            Type: {notification.alert_type}
            Price: ${notification.trigger_price:,.2f}
            Time: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
            Priority: {notification.priority.upper()}
            
            Conditions Met:
            {json.dumps(notification.conditions_met, indent=2)}
            """
            
            # For now, just log the email
            logger.info(f"📧 Email notification prepared: {subject}")
            return {'email': True}
            
        except Exception as e:
            logger.error(f"Email notification error: {e}")
            return {'email': False}
            
    async def _send_discord_notification(self, notification: AlertNotification) -> Dict[str, bool]:
        """Send Discord notification"""
        try:
            # Check if Discord webhook is configured
            if not self.config.discord_webhook:
                logger.debug("Discord webhook not configured")
                return {'discord': False}
            
            # Create Discord embed
            embed = {
                "title": f"🚨 {notification.symbol} Alert",
                "description": f"**{notification.alert_type}** alert triggered",
                "color": self._get_priority_color(notification.priority),
                "fields": [
                    {
                        "name": "Price",
                        "value": f"${notification.trigger_price:,.2f}",
                        "inline": True
                    },
                    {
                        "name": "Priority",
                        "value": notification.priority.upper(),
                        "inline": True
                    },
                    {
                        "name": "Time",
                        "value": notification.timestamp.strftime('%H:%M:%S UTC'),
                        "inline": True
                    }
                ],
                "timestamp": notification.timestamp.isoformat()
            }
            
            payload = {
                "embeds": [embed]
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.config.discord_webhook,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                success = response.status_code == 204
                logger.info(f"Discord notification {'sent' if success else 'failed'}: {response.status_code}")
                return {'discord': success}
                
        except Exception as e:
            logger.error(f"Discord notification error: {e}")
            return {'discord': False}
            
    async def _send_telegram_notification(self, notification: AlertNotification) -> Dict[str, bool]:
        """Send Telegram notification"""
        try:
            message = f"""
🚨 *{notification.symbol} Alert*

*Type:* {notification.alert_type}
*Price:* ${notification.trigger_price:,.2f}
*Priority:* {notification.priority.upper()}
*Time:* {notification.timestamp.strftime('%H:%M:%S UTC')}

*Conditions Met:*
{json.dumps(notification.conditions_met, indent=2)}
            """.strip()
            
            if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
                return {'telegram': False}
                
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.config.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                
                success = response.status_code == 200
                logger.info(f"Telegram notification {'sent' if success else 'failed'}: {response.status_code}")
                return {'telegram': success}
                
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")
            return {'telegram': False}
            
    async def _send_sms_notification(self, notification: AlertNotification) -> Dict[str, bool]:
        """Send SMS notification"""
        try:
            # This would integrate with SMS service (Twilio, AWS SNS, etc.)
            message = f"Alert: {notification.symbol} {notification.alert_type} at ${notification.trigger_price:,.2f}"
            
            logger.info(f"📱 SMS notification prepared: {message}")
            return {'sms': True}
            
        except Exception as e:
            logger.error(f"SMS notification error: {e}")
            return {'sms': False}
            
    def _get_priority_color(self, priority: str) -> int:
        """Get Discord embed color based on priority"""
        colors = {
            'low': 0x00ff00,      # Green
            'medium': 0xffff00,   # Yellow
            'high': 0xff8800,     # Orange
            'critical': 0xff0000   # Red
        }
        return colors.get(priority, 0x808080)  # Default gray
        
    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        recent = self.notification_history[-limit:]
        return [
            {
                'alert_id': n.alert_id,
                'symbol': n.symbol,
                'type': n.alert_type,
                'price': n.trigger_price,
                'timestamp': n.timestamp.isoformat(),
                'priority': n.priority
            }
            for n in recent
        ]
        
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        total = len(self.notification_history)
        if total == 0:
            return {'total': 0, 'by_priority': {}, 'by_symbol': {}}
            
        by_priority = {}
        by_symbol = {}
        
        for notification in self.notification_history:
            # Count by priority
            by_priority[notification.priority] = by_priority.get(notification.priority, 0) + 1
            
            # Count by symbol
            by_symbol[notification.symbol] = by_symbol.get(notification.symbol, 0) + 1
            
        return {
            'total': total,
            'by_priority': by_priority,
            'by_symbol': by_symbol
        }

# Global instance
notification_service = NotificationService()
