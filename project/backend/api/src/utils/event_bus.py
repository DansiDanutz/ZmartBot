"""
Zmart Trading Bot Platform - Event Bus
Event-driven communication system for inter-component messaging
"""
import asyncio
import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types for the trading platform"""
    # Trading events
    TRADE_EXECUTED = "trade.executed"
    TRADE_CANCELLED = "trade.cancelled"
    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"
    POSITION_UPDATED = "position.updated"
    
    # Signal events
    SIGNAL_GENERATED = "signal.generated"
    SIGNAL_PROCESSED = "signal.processed"
    SIGNAL_REJECTED = "signal.rejected"
    
    # Risk events
    RISK_THRESHOLD_EXCEEDED = "risk.threshold_exceeded"
    RISK_SCORE_UPDATED = "risk.score_updated"
    CIRCUIT_BREAKER_TRIGGERED = "risk.circuit_breaker_triggered"
    
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
    
    # Market events
    MARKET_DATA_UPDATED = "market.data_updated"
    MARKET_VOLATILITY_CHANGED = "market.volatility_changed"
    
    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_ACTION = "user.action"

@dataclass
class Event:
    """Event data structure"""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    correlation_id: Optional[str] = None
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
            "priority": self.priority
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())

class EventBus:
    """Event bus for inter-component communication"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        self.is_running = False
        self.event_queue = asyncio.Queue()
        
        logger.info("Event bus initialized")
    
    async def start(self):
        """Start the event bus"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting event bus")
        
        # Start event processing loop
        asyncio.create_task(self._process_events())
    
    async def stop(self):
        """Stop the event bus"""
        self.is_running = False
        logger.info("Stopping event bus")
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event type: {event_type.value}")
    
    async def emit(self, event: Event):
        """Emit an event"""
        if not self.is_running:
            logger.warning("Event bus not running, cannot emit event")
            return
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Add to processing queue
        await self.event_queue.put(event)
        
        logger.debug(f"Emitted event: {event.type.value}")
    
    async def emit_sync(self, event: Event):
        """Emit an event synchronously (immediate processing)"""
        if not self.is_running:
            logger.warning("Event bus not running, cannot emit event")
            return
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Process immediately
        await self._process_event(event)
    
    async def _process_events(self):
        """Process events from the queue"""
        while self.is_running:
            try:
                event = await self.event_queue.get()
                await self._process_event(event)
                self.event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _process_event(self, event: Event):
        """Process a single event"""
        try:
            if event.type in self.subscribers:
                # Create tasks for all subscribers
                tasks = []
                for callback in self.subscribers[event.type]:
                    task = asyncio.create_task(self._call_subscriber(callback, event))
                    tasks.append(task)
                
                # Wait for all subscribers to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.debug(f"Processed event: {event.type.value}")
            
        except Exception as e:
            logger.error(f"Error processing event {event.type.value}: {e}")
    
    async def _call_subscriber(self, callback: Callable, event: Event):
        """Call a subscriber with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            logger.error(f"Error in event subscriber: {e}")
    
    def get_subscribers(self, event_type: EventType) -> List[Callable]:
        """Get all subscribers for an event type"""
        return self.subscribers.get(event_type, [])
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type"""
        history = self.event_history
        
        if event_type:
            history = [event for event in history if event.type == event_type]
        
        return history[-limit:] if limit else history
    
    def clear_history(self):
        """Clear event history"""
        self.event_history.clear()
        logger.info("Event history cleared")

# Global event bus instance
event_bus = EventBus()

# Convenience functions for common events
async def emit_trade_event(symbol: str, side: str, volume: float, price: float, status: str = "executed"):
    """Emit a trade event"""
    event = Event(
        type=EventType.TRADE_EXECUTED,
        data={
            "symbol": symbol,
            "side": side,
            "volume": volume,
            "price": price,
            "status": status
        },
        source="trading_engine"
    )
    await event_bus.emit(event)

async def emit_signal_event(source: str, symbol: str, confidence: float, data: Dict[str, Any]):
    """Emit a signal event"""
    event = Event(
        type=EventType.SIGNAL_GENERATED,
        data={
            "source": source,
            "symbol": symbol,
            "confidence": confidence,
            "data": data
        },
        source=source
    )
    await event_bus.emit(event)

async def emit_risk_event(risk_type: str, symbol: str, score: float, threshold: float):
    """Emit a risk event"""
    event = Event(
        type=EventType.RISK_THRESHOLD_EXCEEDED,
        data={
            "risk_type": risk_type,
            "symbol": symbol,
            "score": score,
            "threshold": threshold
        },
        source="risk_manager",
        priority=3  # High priority for risk events
    )
    await event_bus.emit(event)

async def emit_agent_event(agent_type: str, event_type: EventType, data: Dict[str, Any]):
    """Emit an agent event"""
    event = Event(
        type=event_type,
        data={
            "agent_type": agent_type,
            **data
        },
        source=f"agent.{agent_type}"
    )
    await event_bus.emit(event)

# Event decorators for easy subscription
def subscribe_to_event(event_type: EventType):
    """Decorator to subscribe a function to an event type"""
    def decorator(func: Callable):
        event_bus.subscribe(event_type, func)
        return func
    return decorator

def subscribe_to_trade_events(func: Callable):
    """Decorator to subscribe to trade events"""
    event_bus.subscribe(EventType.TRADE_EXECUTED, func)
    event_bus.subscribe(EventType.TRADE_CANCELLED, func)
    return func

def subscribe_to_signal_events(func: Callable):
    """Decorator to subscribe to signal events"""
    event_bus.subscribe(EventType.SIGNAL_GENERATED, func)
    event_bus.subscribe(EventType.SIGNAL_PROCESSED, func)
    event_bus.subscribe(EventType.SIGNAL_REJECTED, func)
    return func

def subscribe_to_risk_events(func: Callable):
    """Decorator to subscribe to risk events"""
    event_bus.subscribe(EventType.RISK_THRESHOLD_EXCEEDED, func)
    event_bus.subscribe(EventType.CIRCUIT_BREAKER_TRIGGERED, func)
    return func 