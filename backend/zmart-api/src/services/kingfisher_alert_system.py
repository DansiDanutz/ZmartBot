#!/usr/bin/env python3
"""
KingFisher Alert System
Real-time alerts for critical liquidation events
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertPriority(Enum):
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"         # Important, check soon
    MEDIUM = "medium"     # Notable event
    LOW = "low"          # Informational

class AlertType(Enum):
    CASCADE_IMMINENT = "cascade_imminent"
    LARGE_LIQUIDATION = "large_liquidation"
    TREND_REVERSAL = "trend_reversal"
    ENTRY_OPPORTUNITY = "entry_opportunity"
    EXIT_SIGNAL = "exit_signal"
    RISK_THRESHOLD = "risk_threshold"
    PATTERN_DETECTED = "pattern_detected"
    ANOMALY = "anomaly"

class KingFisherAlertSystem:
    """
    Sophisticated alert system for KingFisher liquidation events
    """
    
    def __init__(self):
        self.active_alerts: Dict[str, List[Dict]] = {}  # symbol -> list of alerts
        self.alert_history: List[Dict] = []
        self.subscribers: Set[str] = set()
        self.alert_thresholds = self._initialize_thresholds()
        self.cooldown_periods = {}  # Prevent alert spam
        
        # Alert channels
        self.channels = {
            'telegram': True,
            'webhook': False,
            'email': False,
            'dashboard': True
        }
        
        logger.info("KingFisher Alert System initialized")
    
    def _initialize_thresholds(self) -> Dict:
        """Initialize alert thresholds for different events"""
        return {
            'liquidation_size': {
                'BTC': {'critical': 10000000, 'high': 5000000, 'medium': 1000000},
                'ETH': {'critical': 5000000, 'high': 2000000, 'medium': 500000},
                'default': {'critical': 1000000, 'high': 500000, 'medium': 100000}
            },
            'cascade_risk_score': {
                'critical': 80,
                'high': 60,
                'medium': 40
            },
            'price_movement': {
                'critical': 5.0,  # 5% move
                'high': 3.0,      # 3% move
                'medium': 1.5     # 1.5% move
            },
            'win_rate_change': {
                'critical': 20,   # 20% change in win rate
                'high': 15,
                'medium': 10
            }
        }
    
    async def check_for_alerts(self, symbol: str, 
                              current_data: Dict,
                              historical_data: Optional[List] = None) -> List[Dict]:
        """
        Check current data for alert conditions
        
        Returns list of triggered alerts
        """
        alerts = []
        
        try:
            # Check liquidation size alerts
            size_alert = self._check_liquidation_size(symbol, current_data)
            if size_alert:
                alerts.append(size_alert)
            
            # Check cascade risk alerts
            cascade_alert = self._check_cascade_risk(symbol, current_data)
            if cascade_alert:
                alerts.append(cascade_alert)
            
            # Check for trend reversal
            if historical_data and len(historical_data) > 5:
                reversal_alert = self._check_trend_reversal(symbol, current_data, historical_data)
                if reversal_alert:
                    alerts.append(reversal_alert)
            
            # Check for entry opportunities
            entry_alert = self._check_entry_opportunity(symbol, current_data)
            if entry_alert:
                alerts.append(entry_alert)
            
            # Check for anomalies
            anomaly_alert = self._check_anomalies(symbol, current_data)
            if anomaly_alert:
                alerts.append(anomaly_alert)
            
            # Process and send alerts
            if alerts:
                await self._process_alerts(symbol, alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts for {symbol}: {e}")
            return []
    
    def _check_liquidation_size(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Check for large liquidation events"""
        total_liquidations = (
            data.get('liquidation_analysis', {}).get('long_liquidations', 0) +
            data.get('liquidation_analysis', {}).get('short_liquidations', 0)
        )
        
        thresholds = self.alert_thresholds['liquidation_size'].get(
            symbol, self.alert_thresholds['liquidation_size']['default']
        )
        
        if total_liquidations >= thresholds['critical']:
            return self._create_alert(
                AlertType.LARGE_LIQUIDATION,
                AlertPriority.CRITICAL,
                f"MASSIVE LIQUIDATION: ${total_liquidations:,.0f} liquidated on {symbol}",
                {
                    'symbol': symbol,
                    'total_liquidations': total_liquidations,
                    'long_liquidations': data.get('liquidation_analysis', {}).get('long_liquidations', 0),
                    'short_liquidations': data.get('liquidation_analysis', {}).get('short_liquidations', 0)
                }
            )
        elif total_liquidations >= thresholds['high']:
            return self._create_alert(
                AlertType.LARGE_LIQUIDATION,
                AlertPriority.HIGH,
                f"Large liquidation event: ${total_liquidations:,.0f} on {symbol}",
                {'symbol': symbol, 'total_liquidations': total_liquidations}
            )
        elif total_liquidations >= thresholds['medium']:
            return self._create_alert(
                AlertType.LARGE_LIQUIDATION,
                AlertPriority.MEDIUM,
                f"Notable liquidation: ${total_liquidations:,.0f} on {symbol}",
                {'symbol': symbol, 'total_liquidations': total_liquidations}
            )
        
        return None
    
    def _check_cascade_risk(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Check for liquidation cascade risk"""
        cascade_risk = data.get('cascade_analysis', {})
        risk_score = cascade_risk.get('risk_score', 0)
        
        thresholds = self.alert_thresholds['cascade_risk_score']
        
        if risk_score >= thresholds['critical']:
            danger_zones = cascade_risk.get('danger_zones', [])
            nearest = danger_zones[0] if danger_zones else {}
            
            return self._create_alert(
                AlertType.CASCADE_IMMINENT,
                AlertPriority.CRITICAL,
                f"🚨 CASCADE IMMINENT on {symbol}! Risk score: {risk_score:.0f}/100",
                {
                    'symbol': symbol,
                    'risk_score': risk_score,
                    'nearest_danger': nearest.get('price', 0),
                    'distance': nearest.get('distance_pct', 0),
                    'action': 'EXIT POSITIONS or USE TIGHT STOPS'
                }
            )
        elif risk_score >= thresholds['high']:
            return self._create_alert(
                AlertType.CASCADE_IMMINENT,
                AlertPriority.HIGH,
                f"High cascade risk on {symbol}: {risk_score:.0f}/100",
                {'symbol': symbol, 'risk_score': risk_score}
            )
        
        return None
    
    def _check_trend_reversal(self, symbol: str, current: Dict, historical: List) -> Optional[Dict]:
        """Check for potential trend reversal based on liquidation patterns"""
        try:
            # Get recent liquidation trend
            recent_long_liqs = [h.get('long_liquidations', 0) for h in historical[-5:]]
            recent_short_liqs = [h.get('short_liquidations', 0) for h in historical[-5:]]
            
            current_long = current.get('liquidation_analysis', {}).get('long_liquidations', 0)
            current_short = current.get('liquidation_analysis', {}).get('short_liquidations', 0)
            
            # Check for reversal patterns
            avg_long = sum(recent_long_liqs) / len(recent_long_liqs) if recent_long_liqs else 0
            avg_short = sum(recent_short_liqs) / len(recent_short_liqs) if recent_short_liqs else 0
            
            # Bullish reversal: Heavy long liquidations followed by short liquidations
            if avg_long > avg_short * 2 and current_short > current_long * 1.5:
                return self._create_alert(
                    AlertType.TREND_REVERSAL,
                    AlertPriority.HIGH,
                    f"📈 BULLISH REVERSAL on {symbol} - Shorts getting squeezed",
                    {
                        'symbol': symbol,
                        'pattern': 'bullish_reversal',
                        'confidence': 75,
                        'action': 'Consider LONG positions'
                    }
                )
            
            # Bearish reversal: Heavy short liquidations followed by long liquidations
            elif avg_short > avg_long * 2 and current_long > current_short * 1.5:
                return self._create_alert(
                    AlertType.TREND_REVERSAL,
                    AlertPriority.HIGH,
                    f"📉 BEARISH REVERSAL on {symbol} - Longs getting squeezed",
                    {
                        'symbol': symbol,
                        'pattern': 'bearish_reversal',
                        'confidence': 75,
                        'action': 'Consider SHORT positions'
                    }
                )
            
        except Exception as e:
            logger.error(f"Error checking trend reversal: {e}")
        
        return None
    
    def _check_entry_opportunity(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Check for high-probability entry opportunities"""
        entry_zones = data.get('entry_zones', {})
        best_entry = entry_zones.get('best_entry')
        
        if best_entry and best_entry.get('strength', 0) > 80:
            win_rate = data.get('ai_win_rate_prediction', {}).get('win_rate_prediction', 50)
            
            if win_rate > 70:
                return self._create_alert(
                    AlertType.ENTRY_OPPORTUNITY,
                    AlertPriority.HIGH,
                    f"🎯 HIGH PROBABILITY ENTRY on {symbol}",
                    {
                        'symbol': symbol,
                        'entry_price': best_entry['price'],
                        'entry_type': best_entry['type'],
                        'win_rate': win_rate,
                        'strength': best_entry['strength'],
                        'action': f"Enter {best_entry['type'].upper()} near ${best_entry['price']:,.2f}"
                    }
                )
        
        return None
    
    def _check_anomalies(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Check for unusual patterns or anomalies"""
        liquidation_data = data.get('liquidation_analysis', {})
        
        # Check for unusual liquidation ratio
        ratio = liquidation_data.get('liquidation_ratio', 0)
        if ratio > 0.9 or ratio < 0.1:  # Extremely one-sided
            return self._create_alert(
                AlertType.ANOMALY,
                AlertPriority.MEDIUM,
                f"⚡ UNUSUAL PATTERN on {symbol}",
                {
                    'symbol': symbol,
                    'type': 'extreme_ratio',
                    'ratio': ratio,
                    'description': 'Extremely one-sided liquidations detected'
                }
            )
        
        # Check for toxic order flow
        if liquidation_data.get('toxic_order_flow'):
            return self._create_alert(
                AlertType.ANOMALY,
                AlertPriority.HIGH,
                f"☠️ TOXIC ORDER FLOW on {symbol}",
                {
                    'symbol': symbol,
                    'type': 'toxic_flow',
                    'action': 'AVOID TRADING - Market manipulation likely'
                }
            )
        
        return None
    
    def _create_alert(self, alert_type: AlertType, 
                     priority: AlertPriority,
                     message: str,
                     data: Dict) -> Dict:
        """Create a structured alert"""
        return {
            'id': f"{alert_type.value}_{datetime.now().timestamp()}",
            'type': alert_type.value,
            'priority': priority.value,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'channels': list(self.channels.keys())
        }
    
    async def _process_alerts(self, symbol: str, alerts: List[Dict]):
        """Process and distribute alerts to various channels"""
        # Check cooldown to prevent spam
        for alert in alerts:
            alert_key = f"{symbol}_{alert['type']}"
            
            if alert_key in self.cooldown_periods:
                last_sent = self.cooldown_periods[alert_key]
                cooldown = timedelta(minutes=5 if alert['priority'] != 'critical' else 1)
                
                if datetime.now() - last_sent < cooldown:
                    continue  # Skip this alert
            
            # Send to enabled channels
            if self.channels['telegram']:
                await self._send_telegram_alert(alert)
            
            if self.channels['dashboard']:
                await self._send_dashboard_alert(symbol, alert)
            
            if self.channels['webhook']:
                await self._send_webhook_alert(alert)
            
            # Update cooldown
            self.cooldown_periods[alert_key] = datetime.now()
            
            # Store in history
            self.alert_history.append(alert)
            
            # Keep only last 100 alerts in history
            if len(self.alert_history) > 100:
                self.alert_history = self.alert_history[-100:]
            
            # Store active alerts
            if symbol not in self.active_alerts:
                self.active_alerts[symbol] = []
            self.active_alerts[symbol].append(alert)
            
            # Keep only last 10 active alerts per symbol
            if len(self.active_alerts[symbol]) > 10:
                self.active_alerts[symbol] = self.active_alerts[symbol][-10:]
    
    async def _send_telegram_alert(self, alert: Dict):
        """Send alert to Telegram"""
        try:
            # Format message with priority emoji
            priority_emojis = {
                'critical': '🚨🚨🚨',
                'high': '⚠️',
                'medium': '📊',
                'low': 'ℹ️'
            }
            
            emoji = priority_emojis.get(alert['priority'], '')
            message = f"{emoji} {alert['message']}\n\n"
            
            # Add action if available
            if 'action' in alert['data']:
                message += f"👉 ACTION: {alert['data']['action']}\n"
            
            # Add timestamp
            message += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            
            # Send via telegram service (if available)
            logger.info(f"Telegram alert: {message}")
            
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
    
    async def _send_dashboard_alert(self, symbol: str, alert: Dict):
        """Send alert to dashboard via WebSocket"""
        try:
            # This would integrate with the WebSocket manager
            logger.info(f"Dashboard alert for {symbol}: {alert['message']}")
        except Exception as e:
            logger.error(f"Error sending dashboard alert: {e}")
    
    async def _send_webhook_alert(self, alert: Dict):
        """Send alert to configured webhook"""
        try:
            # Implement webhook sending logic
            logger.info(f"Webhook alert: {alert['message']}")
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
    
    def get_active_alerts(self, symbol: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Get active alerts for symbol or all symbols"""
        if symbol:
            return {symbol: self.active_alerts.get(symbol, [])}
        return self.active_alerts
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        stats = {
            'total_alerts': len(self.alert_history),
            'active_symbols': len(self.active_alerts),
            'alerts_by_type': {},
            'alerts_by_priority': {},
            'recent_alerts': self.alert_history[-10:] if self.alert_history else []
        }
        
        # Count by type and priority
        for alert in self.alert_history:
            alert_type = alert['type']
            priority = alert['priority']
            
            stats['alerts_by_type'][alert_type] = stats['alerts_by_type'].get(alert_type, 0) + 1
            stats['alerts_by_priority'][priority] = stats['alerts_by_priority'].get(priority, 0) + 1
        
        return stats
    
    def configure_channel(self, channel: str, enabled: bool):
        """Enable or disable alert channel"""
        if channel in self.channels:
            self.channels[channel] = enabled
            logger.info(f"Alert channel {channel} {'enabled' if enabled else 'disabled'}")
    
    def update_threshold(self, threshold_type: str, values: Dict):
        """Update alert thresholds"""
        if threshold_type in self.alert_thresholds:
            self.alert_thresholds[threshold_type].update(values)
            logger.info(f"Updated thresholds for {threshold_type}")

# Create global instance
kingfisher_alerts = KingFisherAlertSystem()