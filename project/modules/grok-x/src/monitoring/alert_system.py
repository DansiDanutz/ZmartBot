"""
Advanced Alert and Notification System
Comprehensive alerting for trading signals and market events
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

from ..signals.signal_generator import EnhancedTradingSignal, SignalStrength, RiskLevel
from ..analysis.sentiment_analyzer import SentimentAnalysis
from ...config.settings.config import get_config


class AlertType(Enum):
    """Types of alerts"""
    SIGNAL_GENERATED = "signal_generated"
    SENTIMENT_EXTREME = "sentiment_extreme"
    RISK_WARNING = "risk_warning"
    SYSTEM_ERROR = "system_error"
    PERFORMANCE_ALERT = "performance_alert"


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels"""
    WEBHOOK = "webhook"
    EMAIL = "email"
    CONSOLE = "console"
    FILE = "file"
    DATABASE = "database"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    channels: List[AlertChannel]
    delivered: bool = False
    delivery_attempts: int = 0
    max_attempts: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'channels': [ch.value for ch in self.channels],
            'delivered': self.delivered,
            'delivery_attempts': self.delivery_attempts
        }


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: Callable[[Any], bool]
    alert_type: AlertType
    priority: AlertPriority
    channels: List[AlertChannel]
    cooldown_minutes: int = 30
    enabled: bool = True
    last_triggered: Optional[datetime] = None


class WebhookNotifier:
    """Webhook notification handler"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via webhook"""
        
        try:
            payload = {
                'alert': alert.to_dict(),
                'timestamp': datetime.now().isoformat(),
                'source': 'grok-x-module'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Webhook alert sent successfully: {alert.id}")
                        return True
                    else:
                        self.logger.error(f"Webhook failed with status {response.status}: {alert.id}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Webhook delivery failed: {e}")
            return False


class EmailNotifier:
    """Email notification handler"""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.logger = logging.getLogger(__name__)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via email"""
        
        try:
            # Create email message
            msg = MimeMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = self.smtp_config['to_email']
            msg['Subject'] = f"[{alert.priority.value.upper()}] {alert.title}"
            
            # Email body
            body = f"""
Grok-X-Module Alert

Priority: {alert.priority.value.upper()}
Type: {alert.type.value}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Message:
{alert.message}

Additional Data:
{json.dumps(alert.data, indent=2)}

Alert ID: {alert.id}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.smtp_config['from_email'], self.smtp_config['to_email'], text)
            server.quit()
            
            self.logger.info(f"Email alert sent successfully: {alert.id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Email delivery failed: {e}")
            return False


class ConsoleNotifier:
    """Console notification handler"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to console"""
        
        try:
            # Color coding based on priority
            colors = {
                AlertPriority.LOW: '\033[92m',      # Green
                AlertPriority.MEDIUM: '\033[93m',   # Yellow
                AlertPriority.HIGH: '\033[91m',     # Red
                AlertPriority.CRITICAL: '\033[95m'  # Magenta
            }
            
            reset_color = '\033[0m'
            color = colors.get(alert.priority, '')
            
            print(f"\n{color}🚨 ALERT [{alert.priority.value.upper()}]{reset_color}")
            print(f"Type: {alert.type.value}")
            print(f"Time: {alert.timestamp.strftime('%H:%M:%S')}")
            print(f"Title: {alert.title}")
            print(f"Message: {alert.message}")
            
            if alert.data:
                print("Data:")
                for key, value in alert.data.items():
                    print(f"  {key}: {value}")
            
            print(f"Alert ID: {alert.id}")
            print("-" * 50)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Console alert failed: {e}")
            return False


class FileNotifier:
    """File notification handler"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to file"""
        
        try:
            alert_data = alert.to_dict()
            alert_line = json.dumps(alert_data) + '\n'
            
            with open(self.log_file, 'a') as f:
                f.write(alert_line)
            
            self.logger.debug(f"Alert logged to file: {alert.id}")
            return True
        
        except Exception as e:
            self.logger.error(f"File alert failed: {e}")
            return False


class AlertManager:
    """Central alert management system"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Alert storage
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        
        # Notification handlers
        self.notifiers = {}
        self._setup_notifiers()
        
        # Alert statistics
        self.stats = {
            'total_alerts': 0,
            'delivered_alerts': 0,
            'failed_alerts': 0,
            'alerts_by_type': {},
            'alerts_by_priority': {}
        }
        
        # Setup default alert rules
        self._setup_default_rules()
    
    def _setup_notifiers(self):
        """Setup notification handlers"""
        
        # Console notifier (always available)
        self.notifiers[AlertChannel.CONSOLE] = ConsoleNotifier()
        
        # File notifier
        self.notifiers[AlertChannel.FILE] = FileNotifier('logs/alerts.log')
        
        # Webhook notifier
        webhook_url = getattr(self.config.monitoring, 'webhook_url', None)
        if webhook_url:
            self.notifiers[AlertChannel.WEBHOOK] = WebhookNotifier(webhook_url)
        
        # Email notifier (would need SMTP configuration)
        # self.notifiers[AlertChannel.EMAIL] = EmailNotifier(smtp_config)
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        
        # High confidence trading signals
        self.add_rule(AlertRule(
            name="high_confidence_signals",
            condition=lambda signal: (
                isinstance(signal, EnhancedTradingSignal) and
                signal.confidence >= 0.8 and
                signal.strength in [SignalStrength.STRONG, SignalStrength.VERY_STRONG]
            ),
            alert_type=AlertType.SIGNAL_GENERATED,
            priority=AlertPriority.HIGH,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.WEBHOOK],
            cooldown_minutes=15
        ))
        
        # Critical risk signals
        self.add_rule(AlertRule(
            name="critical_risk_signals",
            condition=lambda signal: (
                isinstance(signal, EnhancedTradingSignal) and
                signal.risk_level == RiskLevel.CRITICAL
            ),
            alert_type=AlertType.RISK_WARNING,
            priority=AlertPriority.CRITICAL,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.WEBHOOK],
            cooldown_minutes=5
        ))
        
        # Extreme sentiment
        self.add_rule(AlertRule(
            name="extreme_sentiment",
            condition=lambda sentiment: (
                isinstance(sentiment, SentimentAnalysis) and
                abs(sentiment.overall_sentiment) > 0.8 and
                sentiment.confidence > 0.7
            ),
            alert_type=AlertType.SENTIMENT_EXTREME,
            priority=AlertPriority.MEDIUM,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE],
            cooldown_minutes=30
        ))
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove alert rule"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
        self.logger.info(f"Removed alert rule: {rule_name}")
    
    async def process_event(self, event: Any):
        """Process event and check alert rules"""
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            if rule.last_triggered:
                time_since_last = datetime.now() - rule.last_triggered
                if time_since_last.total_seconds() < rule.cooldown_minutes * 60:
                    continue
            
            # Check condition
            try:
                if rule.condition(event):
                    await self._trigger_alert(rule, event)
                    rule.last_triggered = datetime.now()
            
            except Exception as e:
                self.logger.error(f"Error checking rule {rule.name}: {e}")
    
    async def _trigger_alert(self, rule: AlertRule, event: Any):
        """Trigger alert based on rule"""
        
        # Generate alert ID
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alerts)}"
        
        # Create alert message
        title, message, data = self._create_alert_content(rule, event)
        
        # Create alert
        alert = Alert(
            id=alert_id,
            type=rule.alert_type,
            priority=rule.priority,
            title=title,
            message=message,
            data=data,
            timestamp=datetime.now(),
            channels=rule.channels
        )
        
        # Store alert
        self.alerts.append(alert)
        
        # Update statistics
        self.stats['total_alerts'] += 1
        self.stats['alerts_by_type'][rule.alert_type.value] = (
            self.stats['alerts_by_type'].get(rule.alert_type.value, 0) + 1
        )
        self.stats['alerts_by_priority'][rule.priority.value] = (
            self.stats['alerts_by_priority'].get(rule.priority.value, 0) + 1
        )
        
        # Deliver alert
        await self._deliver_alert(alert)
        
        self.logger.info(f"Alert triggered: {alert.id} ({rule.name})")
    
    def _create_alert_content(self, rule: AlertRule, event: Any) -> tuple[str, str, Dict[str, Any]]:
        """Create alert content based on rule and event"""
        
        if rule.alert_type == AlertType.SIGNAL_GENERATED:
            signal = event
            title = f"Trading Signal: {signal.symbol} {signal.signal_type.value}"
            message = f"Generated {signal.signal_type.value} signal for {signal.symbol} with {signal.confidence:.1%} confidence"
            data = {
                'symbol': signal.symbol,
                'signal_type': signal.signal_type.value,
                'strength': signal.strength.value,
                'confidence': signal.confidence,
                'risk_level': signal.risk_level.value,
                'reasoning': signal.reasoning
            }
        
        elif rule.alert_type == AlertType.SENTIMENT_EXTREME:
            sentiment = event
            sentiment_type = "BULLISH" if sentiment.overall_sentiment > 0 else "BEARISH"
            title = f"Extreme {sentiment_type} Sentiment Detected"
            message = f"Market sentiment is extremely {sentiment_type.lower()} ({sentiment.overall_sentiment:.2f}) with {sentiment.confidence:.1%} confidence"
            data = {
                'sentiment_score': sentiment.overall_sentiment,
                'sentiment_label': sentiment.sentiment_label,
                'confidence': sentiment.confidence,
                'key_insights': sentiment.key_insights
            }
        
        elif rule.alert_type == AlertType.RISK_WARNING:
            signal = event
            title = f"High Risk Warning: {signal.symbol}"
            message = f"Critical risk level detected for {signal.symbol} signal"
            data = {
                'symbol': signal.symbol,
                'risk_level': signal.risk_level.value,
                'risk_factors': signal.risk_factors,
                'signal_type': signal.signal_type.value
            }
        
        else:
            title = f"Alert: {rule.alert_type.value}"
            message = f"Alert triggered by rule: {rule.name}"
            data = {'event_type': type(event).__name__}
        
        return title, message, data
    
    async def _deliver_alert(self, alert: Alert):
        """Deliver alert through configured channels"""
        
        delivery_success = False
        
        for channel in alert.channels:
            if channel in self.notifiers:
                try:
                    success = await self.notifiers[channel].send_alert(alert)
                    if success:
                        delivery_success = True
                except Exception as e:
                    self.logger.error(f"Alert delivery failed for channel {channel.value}: {e}")
        
        # Update alert status
        alert.delivered = delivery_success
        alert.delivery_attempts += 1
        
        # Update statistics
        if delivery_success:
            self.stats['delivered_alerts'] += 1
        else:
            self.stats['failed_alerts'] += 1
    
    async def send_custom_alert(
        self,
        title: str,
        message: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
        alert_type: AlertType = AlertType.SYSTEM_ERROR,
        channels: Optional[List[AlertChannel]] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send custom alert"""
        
        if channels is None:
            channels = [AlertChannel.CONSOLE, AlertChannel.FILE]
        
        alert_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alerts)}"
        
        alert = Alert(
            id=alert_id,
            type=alert_type,
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            timestamp=datetime.now(),
            channels=channels
        )
        
        self.alerts.append(alert)
        await self._deliver_alert(alert)
        
        self.logger.info(f"Custom alert sent: {alert_id}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp > cutoff_time]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        
        recent_alerts = self.get_recent_alerts(24)
        
        return {
            **self.stats,
            'recent_alerts_24h': len(recent_alerts),
            'active_rules': len([rule for rule in self.alert_rules if rule.enabled]),
            'total_rules': len(self.alert_rules),
            'available_channels': list(self.notifiers.keys())
        }
    
    def clear_old_alerts(self, days: int = 7):
        """Clear old alerts"""
        
        cutoff_time = datetime.now() - timedelta(days=days)
        old_count = len(self.alerts)
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]
        cleared_count = old_count - len(self.alerts)
        
        self.logger.info(f"Cleared {cleared_count} old alerts")
        return cleared_count


# Global alert manager instance
alert_manager = AlertManager()


# Convenience functions
async def send_signal_alert(signal: EnhancedTradingSignal):
    """Send alert for trading signal"""
    await alert_manager.process_event(signal)


async def send_sentiment_alert(sentiment: SentimentAnalysis):
    """Send alert for sentiment analysis"""
    await alert_manager.process_event(sentiment)


async def send_custom_alert(title: str, message: str, priority: AlertPriority = AlertPriority.MEDIUM):
    """Send custom alert"""
    await alert_manager.send_custom_alert(title, message, priority)


def get_alert_stats() -> Dict[str, Any]:
    """Get alert statistics"""
    return alert_manager.get_alert_statistics()

