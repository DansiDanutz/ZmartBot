"""
Zmart Trading Bot Platform - Orchestration Agent
Central coordinator for all trading activities and agent communication
"""
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import time

from src.utils.event_bus import EventBus, EventType, Event
from src.utils.locking import LockManager, LockType
from src.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class AgentType(Enum):
    """Agent type enumeration"""
    SCORING = "scoring"
    RISK_GUARD = "risk_guard"
    SIGNAL_GENERATOR = "signal_generator"
    TRADE_EXECUTOR = "trade_executor"

@dataclass
class AgentInfo:
    """Agent information structure"""
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    last_heartbeat: datetime
    metadata: Dict[str, Any]

class OrchestrationAgent:
    """Main orchestration agent that coordinates all other agents"""
    
    def __init__(self):
        self.agent_id = "orchestration_agent"
        self.status = AgentStatus.STOPPED
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Core components
        self.event_bus = EventBus()
        self.lock_manager = LockManager()
        self.metrics = MetricsCollector()
        
        # Agent registry
        self.agents: Dict[str, AgentInfo] = {}
        
        # Signal and trade management
        self.pending_signals: List[Dict[str, Any]] = []
        self.active_trades: Dict[str, Dict[str, Any]] = {}
        self.conflict_resolution_queue: List[Dict[str, Any]] = []
        
        # Configuration
        self.heartbeat_interval = 30  # seconds
        self.signal_processing_interval = 5  # seconds
        self.health_check_interval = 60  # seconds
        self.conflict_resolution_interval = 10  # seconds
        
        logger.info("Orchestration agent initialized")
    
    async def start(self):
        """Start the orchestration agent"""
        if self.status == AgentStatus.RUNNING:
            logger.warning("Orchestration agent already running")
            return
        
        logger.info("Starting orchestration agent")
        self.status = AgentStatus.STARTING
        
        try:
            # Start core components
            await self.event_bus.start()
            await self.lock_manager.start()
            
            # Register event handlers
            await self._register_event_handlers()
            
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._heartbeat_loop()),
                asyncio.create_task(self._signal_processing_loop()),
                asyncio.create_task(self._health_monitoring_loop()),
                asyncio.create_task(self._conflict_resolution_loop())
            ]
            
            # Update status
            self.status = AgentStatus.RUNNING
            logger.info("Orchestration agent started successfully")
            
            # Emit startup event
            startup_event = Event(
                type=EventType.AGENT_STARTED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(startup_event)
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Failed to start orchestration agent: {e}")
            raise
    
    async def stop(self):
        """Stop the orchestration agent"""
        if self.status == AgentStatus.STOPPED:
            logger.warning("Orchestration agent already stopped")
            return
        
        logger.info("Stopping orchestration agent")
        self.status = AgentStatus.STOPPING
        
        try:
            # Stop background tasks
            self._running = False
            
            # Cancel all tasks
            for task in self._tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Stop all registered agents
            await self._stop_all_agents()
            
            # Update status
            self.status = AgentStatus.STOPPED
            logger.info("Orchestration agent stopped successfully")
            
            # Emit shutdown event
            shutdown_event = Event(
                type=EventType.AGENT_STOPPED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(shutdown_event)
            
        except Exception as e:
            logger.error(f"Error stopping orchestration agent: {e}")
            raise
    
    async def register_agent(self, agent_id: str, agent_type: AgentType, metadata: Optional[Dict[str, Any]] = None):
        """Register a new agent with the orchestration system"""
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered")
            return
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            status=AgentStatus.STARTING,
            last_heartbeat=datetime.now(),
            metadata=metadata or {}
        )
        
        self.agents[agent_id] = agent_info
        
        logger.info(f"Registered agent: {agent_id} ({agent_type.value})")
        
        # Emit agent registration event
        registration_event = Event(
            type=EventType.AGENT_TASK_COMPLETED,  # Using existing event type
            data={
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.event_bus.emit(registration_event)
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from the orchestration system"""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return
        
        agent_info = self.agents.pop(agent_id)
        logger.info(f"Unregistered agent: {agent_id}")
        
        # Emit agent unregistration event
        unregistration_event = Event(
            type=EventType.AGENT_TASK_COMPLETED,  # Using existing event type
            data={
                "agent_id": agent_id,
                "agent_type": agent_info.agent_type.value,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.event_bus.emit(unregistration_event)
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update the status of a registered agent"""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return
        
        self.agents[agent_id].status = status
        logger.info(f"Updated agent {agent_id} status to {status.value}")
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trading signal through the orchestration system"""
        signal_id = signal_data.get("signal_id", f"signal_{datetime.now().timestamp()}")
        
        logger.info(f"Processing signal: {signal_id}")
        
        # Validate signal
        validation_result = await self._validate_signal(signal_data)
        if not validation_result["valid"]:
            logger.warning(f"Signal {signal_id} validation failed: {validation_result['reason']}")
            return {
                "signal_id": signal_id,
                "status": "rejected",
                "reason": validation_result["reason"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Check for conflicts
        conflict_check = await self._check_conflicts(signal_data)
        if conflict_check["has_conflict"]:
            logger.warning(f"Signal {signal_id} has conflicts: {conflict_check['conflicts']}")
            return {
                "signal_id": signal_id,
                "status": "conflict",
                "conflicts": conflict_check["conflicts"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Add to pending signals
        self.pending_signals.append({
            "signal_id": signal_id,
            "data": signal_data,
            "timestamp": datetime.now(),
            "status": "pending"
        })
        
        logger.info(f"Signal {signal_id} queued for processing")
        
        return {
            "signal_id": signal_id,
            "status": "queued",
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade through the orchestration system"""
        trade_id = trade_data.get("trade_id", f"trade_{datetime.now().timestamp()}")
        
        logger.info(f"Executing trade: {trade_id}")
        
        # Check risk limits
        risk_check = await self._check_risk_limits(trade_data)
        if not risk_check["allowed"]:
            logger.warning(f"Trade {trade_id} blocked by risk limits: {risk_check['reason']}")
            return {
                "trade_id": trade_id,
                "status": "blocked",
                "reason": risk_check["reason"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Acquire lock for the trading symbol
        symbol = trade_data.get("symbol", "unknown")
        lock_acquired = await self.lock_manager.acquire_lock(
            f"trade_{symbol}", 
            LockType.WRITE, 
            self.agent_id, 
            timeout=5.0
        )
        
        if not lock_acquired:
            logger.warning(f"Could not acquire lock for symbol {symbol}")
            return {
                "trade_id": trade_id,
                "status": "locked",
                "reason": "Symbol is currently being traded",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Execute the trade (mock implementation)
            trade_result = await self._execute_trade_internal(trade_data)
            
            # Record the trade
            self.active_trades[trade_id] = {
                **trade_data,
                "status": "executed",
                "execution_time": datetime.now(),
                "result": trade_result
            }
            
            logger.info(f"Trade {trade_id} executed successfully")
            
            return {
                "trade_id": trade_id,
                "status": "executed",
                "result": trade_result,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # Release the lock
            await self.lock_manager.release_lock(f"trade_{symbol}", self.agent_id)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status"""
        return {
            "orchestration_agent": {
                "status": self.status.value,
                "agent_id": self.agent_id,
                "running": self._running
            },
            "agents": {
                agent_id: {
                    "type": info.agent_type.value,
                    "status": info.status.value,
                    "last_heartbeat": info.last_heartbeat.isoformat(),
                    "metadata": info.metadata
                }
                for agent_id, info in self.agents.items()
            },
            "signals": {
                "pending": len(self.pending_signals),
                "active_trades": len(self.active_trades)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _register_event_handlers(self):
        """Register event handlers"""
        self.event_bus.subscribe(EventType.SIGNAL_GENERATED, self._handle_signal_generated)
        self.event_bus.subscribe(EventType.TRADE_EXECUTED, self._handle_trade_executed)
        self.event_bus.subscribe(EventType.RISK_THRESHOLD_EXCEEDED, self._handle_risk_alert)
        self.event_bus.subscribe(EventType.AGENT_HEARTBEAT, self._handle_agent_heartbeat)
    
    async def _heartbeat_loop(self):
        """Background task for sending heartbeat signals"""
        while self._running:
            try:
                heartbeat_event = Event(
                    type=EventType.AGENT_HEARTBEAT,
                    data={
                        "agent_id": self.agent_id,
                        "timestamp": datetime.now().isoformat(),
                        "status": self.status.value
                    }
                )
                await self.event_bus.emit(heartbeat_event)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(5)
    
    async def _signal_processing_loop(self):
        """Background task for processing pending signals"""
        while self._running:
            try:
                if self.pending_signals:
                    signal = self.pending_signals.pop(0)
                    await self._process_signal_internal(signal)
                
                await asyncio.sleep(self.signal_processing_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in signal processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _health_monitoring_loop(self):
        """Background task for monitoring system health"""
        while self._running:
            try:
                # Check agent health
                current_time = datetime.now()
                for agent_id, agent_info in self.agents.items():
                    if (current_time - agent_info.last_heartbeat).total_seconds() > 120:
                        logger.warning(f"Agent {agent_id} heartbeat timeout")
                        agent_info.status = AgentStatus.ERROR
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _conflict_resolution_loop(self):
        """Background task for resolving trading conflicts"""
        while self._running:
            try:
                if self.conflict_resolution_queue:
                    conflict = self.conflict_resolution_queue.pop(0)
                    await self._resolve_trading_conflicts()
                
                await asyncio.sleep(self.conflict_resolution_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in conflict resolution loop: {e}")
                await asyncio.sleep(5)
    
    async def _validate_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a trading signal"""
        # Basic validation
        required_fields = ["symbol", "side", "confidence"]
        for field in required_fields:
            if field not in signal_data:
                return {"valid": False, "reason": f"Missing required field: {field}"}
        
        # Check confidence level
        confidence = signal_data.get("confidence", 0)
        if not 0 <= confidence <= 1:
            return {"valid": False, "reason": "Confidence must be between 0 and 1"}
        
        return {"valid": True, "reason": "Signal is valid"}
    
    async def _check_conflicts(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for conflicts with existing signals/trades"""
        symbol = signal_data.get("symbol")
        side = signal_data.get("side")
        
        # Check for opposing trades
        for trade in self.active_trades.values():
            if trade.get("symbol") == symbol and trade.get("side") != side:
                return {
                    "has_conflict": True,
                    "conflicts": [f"Opposing trade for {symbol}"]
                }
        
        return {"has_conflict": False, "conflicts": []}
    
    async def _check_risk_limits(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if trade meets risk limits"""
        # Mock risk check
        return {"allowed": True, "reason": "Risk limits OK"}
    
    async def _execute_trade_internal(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal trade execution (mock implementation)"""
        return {
            "execution_price": trade_data.get("price", 0),
            "execution_time": datetime.now().isoformat(),
            "status": "executed"
        }
    
    async def _process_signal_internal(self, signal: Dict[str, Any]):
        """Process a signal internally"""
        signal_id = signal.get("signal_id")
        logger.info(f"Processing signal internally: {signal_id}")
        
        # Mock signal processing
        processed_event = Event(
            type=EventType.SIGNAL_PROCESSED,
            data={
                "signal_id": signal_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.event_bus.emit(processed_event)
    
    async def _resolve_trading_conflicts(self):
        """Resolve trading conflicts"""
        logger.info("Resolving trading conflicts")
        # Mock conflict resolution
    
    async def _stop_all_agents(self):
        """Stop all registered agents"""
        logger.info("Stopping all registered agents")
        # Mock agent stopping
    
    async def _handle_signal_generated(self, event: Event):
        """Handle signal generated event"""
        logger.info(f"Handling signal generated event: {event.data}")
    
    async def _handle_trade_executed(self, event: Event):
        """Handle trade executed event"""
        logger.info(f"Handling trade executed event: {event.data}")
    
    async def _handle_risk_alert(self, event: Event):
        """Handle risk alert event"""
        logger.info(f"Handling risk alert event: {event.data}")
    
    async def _handle_agent_heartbeat(self, event: Event):
        """Handle agent heartbeat event"""
        agent_id = event.data.get("agent_id")
        if agent_id and agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.now()
            logger.debug(f"Updated heartbeat for agent: {agent_id}") 