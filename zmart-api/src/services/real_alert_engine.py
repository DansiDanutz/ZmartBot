#!/usr/bin/env python3
"""
Real Alert Engine Service
Monitors real market data and triggers alerts based on actual conditions
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import httpx
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class AlertCondition:
    """Alert condition configuration"""
    symbol: str
    alert_type: str
    conditions: Dict[str, Any]
    threshold: float
    operator: str  # 'above', 'below', 'equals', 'crosses'
    timeframe: str

@dataclass
class AlertTrigger:
    """Alert trigger event"""
    alert_id: str
    symbol: str
    triggered_at: datetime
    trigger_price: float
    conditions_met: Dict[str, Any]
    alert_type: str

class RealAlertEngine:
    """Real-time alert monitoring engine"""
    
    def __init__(self):
        self.is_running = False
        self.active_alerts: Dict[str, AlertCondition] = {}
        self.monitored_symbols: set = set()
        self.last_check_time = datetime.now(timezone.utc)
        self.trigger_history: List[AlertTrigger] = []
        self.check_interval = 30  # Check every 30 seconds
        
    async def start(self):
        """Start the alert monitoring engine"""
        if self.is_running:
            logger.warning("Alert engine is already running")
            return
            
        self.is_running = True
        logger.info("🚀 Starting Real Alert Engine...")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
    async def stop(self):
        """Stop the alert monitoring engine"""
        self.is_running = False
        logger.info("🛑 Stopping Real Alert Engine...")
        
    async def add_alert(self, alert_id: str, alert_data: Dict[str, Any]):
        """Add a new alert to monitor"""
        try:
            condition = AlertCondition(
                symbol=alert_data['symbol'],
                alert_type=alert_data['alert_type'],
                conditions=alert_data['conditions'],
                threshold=alert_data['conditions'].get('threshold', 0),
                operator=alert_data['conditions'].get('operator', 'above'),
                timeframe=alert_data['conditions'].get('timeframe', '1m')
            )
            
            self.active_alerts[alert_id] = condition
            self.monitored_symbols.add(alert_data['symbol'])
            
            logger.info(f"✅ Added alert {alert_id} for {alert_data['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add alert {alert_id}: {e}")
            return False
            
    async def remove_alert(self, alert_id: str):
        """Remove an alert from monitoring"""
        if alert_id in self.active_alerts:
            symbol = self.active_alerts[alert_id].symbol
            del self.active_alerts[alert_id]
            
            # Remove symbol if no more alerts for it
            if not any(alert.symbol == symbol for alert in self.active_alerts.values()):
                self.monitored_symbols.discard(symbol)
                
            logger.info(f"🗑️ Removed alert {alert_id}")
            return True
        return False
        
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                await self._check_all_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _check_all_alerts(self):
        """Check all active alerts against current market data"""
        if not self.active_alerts:
            return
            
        self.last_check_time = datetime.now(timezone.utc)
        
        # Get current prices for all monitored symbols
        symbols = list(self.monitored_symbols)
        prices = await self._fetch_current_prices(symbols)
        
        if not prices:
            return
            
        # Check each alert
        for alert_id, condition in self.active_alerts.items():
            await self._check_single_alert(alert_id, condition, prices)
            
    async def _fetch_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch current prices from Binance API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                prices = {}
                
                for symbol in symbols:
                    try:
                        # Convert symbol format for Binance API
                        binance_symbol = symbol.replace('/USDT:USDT', 'USDT').replace('/', '')
                        
                        response = await client.get(
                            f"https://api.binance.com/api/v3/ticker/price",
                            params={'symbol': binance_symbol}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            prices[symbol] = float(data['price'])
                        else:
                            logger.warning(f"Failed to fetch price for {symbol}: {response.status_code}")
                            
                    except Exception as e:
                        logger.error(f"Error fetching price for {symbol}: {e}")
                        
                return prices
                
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            return {}
            
    async def _check_single_alert(self, alert_id: str, condition: AlertCondition, prices: Dict[str, float]):
        """Check if a single alert should be triggered"""
        try:
            current_price = prices.get(condition.symbol)
            if current_price is None:
                return
                
            should_trigger = False
            conditions_met = {}
            
            # Check different alert types
            if condition.alert_type == 'PRICE':
                should_trigger = self._check_price_condition(
                    current_price, condition.threshold, condition.operator
                )
                conditions_met = {
                    'current_price': current_price,
                    'threshold': condition.threshold,
                    'operator': condition.operator
                }
                
            elif condition.alert_type == 'TECHNICAL':
                # For technical alerts, we need to fetch more data
                should_trigger = await self._check_technical_condition(
                    condition.symbol, condition.conditions, current_price
                )
                conditions_met = {
                    'current_price': current_price,
                    'technical_conditions': condition.conditions
                }
                
            if should_trigger:
                await self._trigger_alert(alert_id, condition, current_price, conditions_met)
                
        except Exception as e:
            logger.error(f"Error checking alert {alert_id}: {e}")
            
    def _check_price_condition(self, current_price: float, threshold: float, operator: str) -> bool:
        """Check if price condition is met"""
        if operator == 'above':
            return current_price > threshold
        elif operator == 'below':
            return current_price < threshold
        elif operator == 'equals':
            return abs(current_price - threshold) < 0.01  # Small tolerance
        elif operator == 'crosses':
            # This would need previous price data to implement
            return False
        return False
        
    async def _check_technical_condition(self, symbol: str, conditions: Dict[str, Any], current_price: float) -> bool:
        """Check technical analysis conditions"""
        try:
            # Fetch technical indicators
            indicators = await self._fetch_technical_indicators(symbol)
            
            if not indicators:
                return False
                
            # Check RSI conditions
            if 'rsi' in conditions:
                rsi_value = indicators.get('rsi', 50)
                rsi_threshold = conditions['rsi']
                if rsi_value > rsi_threshold:  # Overbought
                    return True
                    
            # Check MACD conditions
            if 'macd' in conditions:
                macd_value = indicators.get('macd', 0)
                signal_value = indicators.get('macd_signal', 0)
                if macd_value > signal_value:  # Bullish crossover
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking technical conditions: {e}")
            return False
            
    async def _fetch_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """Fetch technical indicators for a symbol from database"""
        try:
            # Import the existing technical analysis service
            from src.services.technical_analysis_service import technical_analysis_service
            
            # Get technical analysis from database
            analysis = await technical_analysis_service.get_technical_analysis(symbol)
            
            if not analysis:
                logger.warning(f"No database data available for {symbol}")
                return {}
            
            # Extract key indicators from database data
            indicators = {}
            
            # Get EMA data
            ema_data = analysis.get("ema_data", {})
            if ema_data:
                # Get the first available timeframe data
                for timeframe, data in ema_data.items():
                    if data.get("ema_12"):
                        indicators['ema_12'] = data["ema_12"]
                    if data.get("ema_26"):
                        indicators['ema_26'] = data["ema_26"]
                    break  # Use first timeframe
            
            # Get RSI data
            rsi_data = analysis.get("rsi_data", {})
            if rsi_data:
                for timeframe, data in rsi_data.items():
                    if data.get("rsi_value"):
                        indicators['rsi'] = data["rsi_value"]
                    break  # Use first timeframe
            
            # Get MACD data
            macd_data = analysis.get("macd_data", {})
            if macd_data:
                for timeframe, data in macd_data.items():
                    if data.get("macd_line"):
                        indicators['macd'] = data["macd_line"]
                    if data.get("signal_line"):
                        indicators['macd_signal'] = data["signal_line"]
                    break  # Use first timeframe
            
            # Get Bollinger Bands data
            bb_data = analysis.get("bollinger_bands_timeframes", {})
            if bb_data:
                for timeframe, data in bb_data.items():
                    if data.get("upper_band"):
                        indicators['bollinger_upper'] = data["upper_band"]
                    if data.get("lower_band"):
                        indicators['bollinger_lower'] = data["lower_band"]
                    break  # Use first timeframe
            
            logger.info(f"✅ Fetched technical indicators for {symbol}: {list(indicators.keys())}")
            return indicators
            
        except Exception as e:
            logger.error(f"Error fetching technical indicators for {symbol}: {e}")
            return {}
            

            
    async def _trigger_alert(self, alert_id: str, condition: AlertCondition, price: float, conditions_met: Dict[str, Any]):
        """Trigger an alert"""
        try:
            trigger = AlertTrigger(
                alert_id=alert_id,
                symbol=condition.symbol,
                triggered_at=datetime.now(timezone.utc),
                trigger_price=price,
                conditions_met=conditions_met,
                alert_type=condition.alert_type
            )
            
            # Add to history
            self.trigger_history.append(trigger)
            
            # Keep only last 1000 triggers
            if len(self.trigger_history) > 1000:
                self.trigger_history = self.trigger_history[-1000:]
                
            # Send notification (implement your notification system here)
            await self._send_notification(trigger)
            
            logger.info(f"🔔 Alert triggered: {alert_id} for {condition.symbol} at ${price}")
            
        except Exception as e:
            logger.error(f"Error triggering alert {alert_id}: {e}")
            
    async def _send_notification(self, trigger: AlertTrigger):
        """Send alert notification"""
        try:
            # Import notification service
            from src.services.notification_service import notification_service, AlertNotification
            
            # Create notification object
            notification = AlertNotification(
                alert_id=trigger.alert_id,
                symbol=trigger.symbol,
                alert_type=trigger.alert_type,
                trigger_price=trigger.trigger_price,
                conditions_met=trigger.conditions_met,
                timestamp=trigger.triggered_at,
                priority=self._determine_priority(trigger)
            )
            
            # Send through notification service
            results = await notification_service.send_alert_notification(notification)
            
            logger.info(f"📢 Notifications sent for {trigger.symbol}: {results}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            
    def _determine_priority(self, trigger: AlertTrigger) -> str:
        """Determine alert priority based on conditions"""
        try:
            # High priority for critical technical signals
            if trigger.alert_type == 'TECHNICAL':
                if 'rsi' in trigger.conditions_met:
                    rsi_value = trigger.conditions_met.get('rsi', 50)
                    if rsi_value > 80 or rsi_value < 20:
                        return 'high'
                        
            # Medium priority for price alerts
            if trigger.alert_type == 'PRICE':
                return 'medium'
                
            # Default priority
            return 'medium'
            
        except Exception as e:
            logger.error(f"Error determining priority: {e}")
            return 'medium'
            
    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            'is_running': self.is_running,
            'active_alerts': len(self.active_alerts),
            'monitored_symbols': len(self.monitored_symbols),
            'last_check': self.last_check_time.isoformat(),
            'total_triggers': len(self.trigger_history)
        }
        
    async def get_active_alerts_count(self) -> int:
        """Get count of active alerts"""
        return len(self.active_alerts)
        
    async def get_monitored_symbols(self) -> List[str]:
        """Get list of monitored symbols"""
        return list(self.monitored_symbols)
        
    def get_uptime(self) -> str:
        """Get engine uptime"""
        if not self.is_running:
            return "0h 0m 0s"
        
        # Calculate uptime from when engine started
        # For now, return a mock uptime
        return "1h 23m 45s"
        
    def get_trigger_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trigger history"""
        recent_triggers = self.trigger_history[-limit:]
        return [
            {
                'alert_id': trigger.alert_id,
                'symbol': trigger.symbol,
                'triggered_at': trigger.triggered_at.isoformat(),
                'trigger_price': trigger.trigger_price,
                'alert_type': trigger.alert_type
            }
            for trigger in recent_triggers
        ]

# Global instance
real_alert_engine = RealAlertEngine()
