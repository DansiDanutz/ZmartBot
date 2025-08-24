"""Alert Processor for evaluating conditions and triggering alerts."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .models import (
    AlertConfig, AlertTrigger, AlertCondition, MarketData, 
    TechnicalIndicators, AlertStatus, AlertType
)

logger = logging.getLogger(__name__)


class AlertProcessor:
    """Processes alert conditions and triggers notifications."""
    
    def __init__(self, data_manager, notification_manager):
        self.data_manager = data_manager
        self.notification_manager = notification_manager
        self.active_alerts: Dict[str, AlertConfig] = {}
        self.alert_states: Dict[str, Dict] = {}
        self.trigger_history: Dict[str, List[datetime]] = {}
        
    async def add_alert(self, alert_config: AlertConfig) -> str:
        """Add a new alert to the system."""
        alert_id = alert_config.id or f"alert_{datetime.now().timestamp()}"
        alert_config.id = alert_id
        alert_config.created_at = datetime.now()
        
        self.active_alerts[alert_id] = alert_config
        self.alert_states[alert_id] = {
            'last_check': None,
            'trigger_count': 0,
            'last_trigger': None,
            'previous_values': {}
        }
        
        # Subscribe to symbol data
        await self.data_manager.subscribe_symbol(
            alert_config.symbol, 
            self._create_symbol_callback(alert_id)
        )
        
        logger.info(f"Added alert {alert_id} for {alert_config.symbol}")
        return alert_id
    
    async def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert from the system."""
        if alert_id not in self.active_alerts:
            return False
        
        alert_config = self.active_alerts[alert_id]
        
        # Unsubscribe from symbol data if no other alerts for this symbol
        symbol_alerts = [a for a in self.active_alerts.values() if a.symbol == alert_config.symbol]
        if len(symbol_alerts) == 1:  # Only this alert
            await self.data_manager.unsubscribe_symbol(
                alert_config.symbol,
                self._create_symbol_callback(alert_id)
            )
        
        del self.active_alerts[alert_id]
        del self.alert_states[alert_id]
        if alert_id in self.trigger_history:
            del self.trigger_history[alert_id]
        
        logger.info(f"Removed alert {alert_id}")
        return True
    
    async def get_alert(self, alert_id: str) -> Optional[AlertConfig]:
        """Get alert configuration by ID."""
        return self.active_alerts.get(alert_id)
    
    async def list_alerts(self, user_id: Optional[str] = None) -> List[AlertConfig]:
        """List all alerts, optionally filtered by user."""
        alerts = list(self.active_alerts.values())
        if user_id:
            alerts = [a for a in alerts if a.user_id == user_id]
        return alerts
    
    async def pause_alert(self, alert_id: str) -> bool:
        """Pause an alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].is_active = False
            return True
        return False
    
    async def resume_alert(self, alert_id: str) -> bool:
        """Resume a paused alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].is_active = True
            return True
        return False
    
    def _create_symbol_callback(self, alert_id: str):
        """Create a callback function for symbol data updates."""
        async def callback(market_data: MarketData):
            await self._process_alert(alert_id, market_data)
        return callback
    
    async def _process_alert(self, alert_id: str, market_data: MarketData):
        """Process an alert when new market data arrives."""
        if alert_id not in self.active_alerts:
            return
        
        alert_config = self.active_alerts[alert_id]
        alert_state = self.alert_states[alert_id]
        
        # Skip if alert is not active
        if not alert_config.is_active:
            return
        
        # Check if alert has expired
        if alert_config.expires_at and datetime.now() > alert_config.expires_at:
            await self.remove_alert(alert_id)
            return
        
        # Check cooldown period
        if self._is_in_cooldown(alert_config, alert_state):
            return
        
        # Check if max triggers reached
        if (alert_config.max_triggers and 
            alert_state['trigger_count'] >= alert_config.max_triggers):
            await self.remove_alert(alert_id)
            return
        
        try:
            # Evaluate alert conditions
            should_trigger = await self._evaluate_conditions(alert_config, market_data)
            
            if should_trigger:
                await self._trigger_alert(alert_config, market_data)
                
        except Exception as e:
            logger.error(f"Error processing alert {alert_id}: {e}")
        
        # Update last check time
        alert_state['last_check'] = datetime.now()
    
    async def _evaluate_conditions(self, alert_config: AlertConfig, market_data: MarketData) -> bool:
        """Evaluate if alert conditions are met."""
        alert_state = self.alert_states[alert_config.id]
        
        for condition in alert_config.conditions:
            if not await self._evaluate_single_condition(condition, market_data, alert_state):
                return False
        
        return True
    
    async def _evaluate_single_condition(self, condition: AlertCondition, 
                                       market_data: MarketData, alert_state: Dict) -> bool:
        """Evaluate a single alert condition."""
        try:
            # Get current value based on field
            current_value = await self._get_field_value(condition.field, market_data, condition.timeframe)
            if current_value is None:
                return False
            
            # Get previous value for cross conditions
            previous_value = alert_state['previous_values'].get(condition.field)
            alert_state['previous_values'][condition.field] = current_value
            
            # Evaluate condition based on operator
            target_value = float(condition.value)
            
            if condition.operator == '>':
                return current_value > target_value
            elif condition.operator == '<':
                return current_value < target_value
            elif condition.operator == '>=':
                return current_value >= target_value
            elif condition.operator == '<=':
                return current_value <= target_value
            elif condition.operator == '==':
                return abs(current_value - target_value) < 0.0001
            elif condition.operator == 'cross_above':
                return (previous_value is not None and 
                       previous_value <= target_value and 
                       current_value > target_value)
            elif condition.operator == 'cross_below':
                return (previous_value is not None and 
                       previous_value >= target_value and 
                       current_value < target_value)
            else:
                logger.warning(f"Unknown operator: {condition.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    async def _get_field_value(self, field: str, market_data: MarketData, timeframe) -> Optional[float]:
        """Get the value of a specific field from market or technical data."""
        # Market data fields
        if field == 'price':
            return market_data.price
        elif field == 'volume':
            return market_data.volume
        elif field == 'bid':
            return market_data.bid
        elif field == 'ask':
            return market_data.ask
        elif field == 'high_24h':
            return market_data.high_24h
        elif field == 'low_24h':
            return market_data.low_24h
        elif field == 'change_24h':
            return market_data.change_24h
        elif field == 'change_percent_24h':
            return market_data.change_percent_24h
        
        # Technical indicator fields
        technical_data = await self.data_manager.get_technical_data(market_data.symbol, timeframe)
        if not technical_data:
            return None
        
        if field == 'rsi':
            return technical_data.rsi
        elif field == 'macd':
            return technical_data.macd
        elif field == 'macd_signal':
            return technical_data.macd_signal
        elif field == 'macd_histogram':
            return technical_data.macd_histogram
        elif field == 'bb_upper':
            return technical_data.bb_upper
        elif field == 'bb_middle':
            return technical_data.bb_middle
        elif field == 'bb_lower':
            return technical_data.bb_lower
        elif field == 'sma_20':
            return technical_data.sma_20
        elif field == 'sma_50':
            return technical_data.sma_50
        elif field == 'ema_12':
            return technical_data.ema_12
        elif field == 'ema_26':
            return technical_data.ema_26
        elif field == 'volume_sma':
            return technical_data.volume_sma
        
        return None
    
    def _is_in_cooldown(self, alert_config: AlertConfig, alert_state: Dict) -> bool:
        """Check if alert is in cooldown period."""
        if not alert_config.cooldown_minutes or not alert_state['last_trigger']:
            return False
        
        cooldown_end = alert_state['last_trigger'] + timedelta(minutes=alert_config.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    async def _trigger_alert(self, alert_config: AlertConfig, market_data: MarketData):
        """Trigger an alert and send notifications."""
        alert_state = self.alert_states[alert_config.id]
        
        # Get technical data if available
        technical_data = None
        for timeframe in alert_config.conditions:
            tech_data = await self.data_manager.get_technical_data(
                market_data.symbol, timeframe.timeframe
            )
            if tech_data:
                technical_data = tech_data
                break
        
        # Create alert trigger
        trigger = AlertTrigger(
            alert_id=alert_config.id,
            symbol=alert_config.symbol,
            alert_type=alert_config.alert_type,
            trigger_price=market_data.price,
            message=alert_config.message or f"{alert_config.alert_type} triggered for {alert_config.symbol}",
            timestamp=datetime.now(),
            market_data=market_data,
            technical_data=technical_data
        )
        
        # Update alert state
        alert_state['trigger_count'] += 1
        alert_state['last_trigger'] = datetime.now()
        
        # Add to trigger history
        if alert_config.id not in self.trigger_history:
            self.trigger_history[alert_config.id] = []
        self.trigger_history[alert_config.id].append(datetime.now())
        
        # Send notification
        await self.notification_manager.send_alert(trigger, alert_config)
        
        logger.info(f"Alert {alert_config.id} triggered for {alert_config.symbol} at {market_data.price}")
    
    async def get_trigger_history(self, alert_id: str) -> List[datetime]:
        """Get trigger history for an alert."""
        return self.trigger_history.get(alert_id, [])
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        total_alerts = len(self.active_alerts)
        active_alerts = len([a for a in self.active_alerts.values() if a.is_active])
        total_triggers = sum(len(history) for history in self.trigger_history.values())
        
        # Triggers in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_triggers = 0
        for history in self.trigger_history.values():
            recent_triggers += len([t for t in history if t > one_hour_ago])
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'paused_alerts': total_alerts - active_alerts,
            'total_triggers': total_triggers,
            'triggers_last_hour': recent_triggers,
            'monitored_symbols': len(set(a.symbol for a in self.active_alerts.values()))
        }

