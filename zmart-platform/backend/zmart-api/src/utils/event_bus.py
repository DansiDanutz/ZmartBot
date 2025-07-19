"""
Zmart Trading Bot Platform - Event Bus
Handles async event-driven communication between system components
"""
import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types for the trading platform"""
    # Trading events
    TRADE_EXECUTED = "trade.executed"
    TRADE_CANCELLED = "trade.cancelled"
    TRADE_FAILED = "trade.failed"
    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"
    POSITION_UPDATED = "position.updated"
    
    # Signal events
    SIGNAL_GENERATED = "signal.generated"
    SIGNAL_PROCESSED = "signal.processed"
    SIGNAL_REJECTED = "signal.rejected"
    SIGNAL_EXPIRED = "signal.expired"
    
    # Risk events
    RISK_THRESHOLD_EXCEEDED = "risk.threshold_exceeded"
    RISK_ALERT_TRIGGERED = "risk.alert_triggered"
    CIRCUIT_BREAKER_ACTIVATED = "circuit_breaker.activated"
    CIRCUIT_BREAKER_DEACTIVATED = "circuit_breaker.deactivated"
    
    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_TASK_COMPLETED = "agent.task_completed"
    AGENT_TASK_FAILED = "agent.task_failed"
    AGENT_HEARTBEAT = "agent.heartbeat"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    
    # Market events
    MARKET_DATA_UPDATED = "market.data_updated"
    MARKET_VOLATILITY_HIGH = "market.volatility_high"
    MARKET_TREND_CHANGED = "market.trend_changed"
    
    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_ACTION = "user.action"

@dataclass
class Event:
    """Event data structure"""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=critical
    id: str = ""
    
    def __post_init__(self):
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())

class EventBus:
    """Event bus for async event-driven communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        self.is_running = False
        
        logger.info("Event bus initialized")
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event type: {event_type}")
            except ValueError:
                logger.warning(f"Callback not found for event type: {event_type}")
    
    async def emit(self, event: Event):
        """Emit an event to all subscribers"""
        if not self.is_running:
            logger.warning("Event bus is not running, event not emitted")
            return
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Get subscribers for this event type
        subscribers = self.subscribers.get(event.type, [])
        
        if not subscribers:
            logger.debug(f"No subscribers for event type: {event.type}")
            return
        
        # Emit to all subscribers concurrently
        tasks = []
        for callback in subscribers:
            try:
                task = asyncio.create_task(self._call_subscriber(callback, event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Failed to create task for event {event.type}: {e}")
        
        if tasks:
            # Wait for all subscribers to process the event
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Subscriber {i} failed for event {event.type}: {result}")
        
        logger.debug(f"Emitted event: {event.type} to {len(subscribers)} subscribers")
    
    async def _call_subscriber(self, callback: Callable, event: Event):
        """Call a subscriber with the event"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            logger.error(f"Subscriber callback failed for event {event.type}: {e}")
            raise
    
    def emit_sync(self, event: Event):
        """Emit an event synchronously (for non-async callbacks)"""
        if not self.is_running:
            logger.warning("Event bus is not running, event not emitted")
            return
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Get subscribers for this event type
        subscribers = self.subscribers.get(event.type, [])
        
        if not subscribers:
            logger.debug(f"No subscribers for event type: {event.type}")
            return
        
        # Emit to all subscribers
        for callback in subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Schedule async callback
                    asyncio.create_task(callback(event))
                else:
                    # Call sync callback directly
                    callback(event)
            except Exception as e:
                logger.error(f"Subscriber callback failed for event {event.type}: {e}")
        
        logger.debug(f"Emitted event: {event.type} to {len(subscribers)} subscribers")
    
    def start(self):
        """Start the event bus"""
        self.is_running = True
        logger.info("Event bus started")
    
    def stop(self):
        """Stop the event bus"""
        self.is_running = False
        logger.info("Event bus stopped")
    
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type"""
        history = self.event_history
        
        if event_type:
            history = [event for event in history if event.type == event_type]
        
        return history[-limit:] if limit else history
    
    def get_subscriber_count(self, event_type: Optional[str] = None) -> int:
        """Get the number of subscribers for an event type or total"""
        if event_type:
            return len(self.subscribers.get(event_type, []))
        else:
            return sum(len(subscribers) for subscribers in self.subscribers.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        event_counts = {}
        for event in self.event_history:
            event_counts[event.type] = event_counts.get(event.type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "subscriber_count": self.get_subscriber_count(),
            "event_types": len(self.subscribers),
            "event_type_counts": event_counts,
            "is_running": self.is_running
        }

# Global event bus instance
event_bus = EventBus()

def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    return event_bus

# Convenience functions for common events
async def emit_trade_event(symbol: str, side: str, amount: float, price: float, status: str = "executed"):
    """Emit a trade event"""
    event = Event(
        type=EventType.TRADE_EXECUTED.value,
        data={
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price,
            "status": status
        },
        source="trading_engine"
    )
    await event_bus.emit(event)

async def emit_signal_event(signal_type: str, symbol: str, confidence: float, data: Dict[str, Any]):
    """Emit a signal event"""
    event = Event(
        type=EventType.SIGNAL_GENERATED.value,
        data={
            "signal_type": signal_type,
            "symbol": symbol,
            "confidence": confidence,
            **data
        },
        source="signal_generator"
    )
    await event_bus.emit(event)

async def emit_risk_event(risk_type: str, severity: str, details: Dict[str, Any]):
    """Emit a risk event"""
    event = Event(
        type=EventType.RISK_THRESHOLD_EXCEEDED.value,
        data={
            "risk_type": risk_type,
            "severity": severity,
            **details
        },
        source="risk_manager",
        priority=4  # High priority for risk events
    )
    await event_bus.emit(event)

async def emit_agent_event(agent_type: str, action: str, data: Dict[str, Any]):
    """Emit an agent event"""
    event = Event(
        type=EventType.AGENT_TASK_COMPLETED.value,
        data={
            "agent_type": agent_type,
            "action": action,
            **data
        },
        source=f"agent_{agent_type}"
    )
    await event_bus.emit(event) 