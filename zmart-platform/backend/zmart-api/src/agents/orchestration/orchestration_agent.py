"""
Zmart Trading Bot Platform - Orchestration Agent
Central coordinator for all trading activities and agent interactions
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

from src.config.settings import settings
from src.utils.event_bus import EventBus, Event
from src.utils.locking import LockManager
from src.utils.metrics import MetricsCollector

class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Represents a task to be executed by an agent"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    agent_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class AgentInfo:
    """Information about a registered agent"""
    name: str
    type: str
    status: AgentStatus
    capabilities: List[str]
    last_heartbeat: datetime
    current_task: Optional[str] = None
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_execution_time: float = 0.0

class OrchestrationAgent:
    """
    Central orchestration agent that coordinates all trading activities
    and manages communication between different agents in the system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_bus = EventBus()
        self.lock_manager = LockManager()
        self.metrics = MetricsCollector()
        
        # Agent management
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_callbacks: Dict[str, Callable] = {}
        
        # Task management
        self.pending_tasks: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.task_timeout_default = 300
        self.heartbeat_timeout = 60
        
        # State
        self.is_running = False
        self.shutdown_requested = False
        
        # Initialize event handlers
        self._setup_event_handlers()
        
        self.logger.info("Orchestration Agent initialized")
    
    def _setup_event_handlers(self):
        """Setup event handlers for different types of events"""
        self.event_bus.subscribe("agent.heartbeat", self._handle_agent_heartbeat)
        self.event_bus.subscribe("agent.task_completed", self._handle_task_completed)
        self.event_bus.subscribe("agent.task_failed", self._handle_task_failed)
        self.event_bus.subscribe("signal.generated", self._handle_signal_generated)
        self.event_bus.subscribe("trade.executed", self._handle_trade_executed)
        self.event_bus.subscribe("risk.threshold_exceeded", self._handle_risk_threshold_exceeded)
    
    async def start(self):
        """Start the orchestration agent"""
        if self.is_running:
            self.logger.warning("Orchestration agent is already running")
            return
        
        self.is_running = True
        self.shutdown_requested = False
        
        self.logger.info("Starting orchestration agent")
        
        # Start background tasks
        await asyncio.gather(
            self._task_scheduler(),
            self._agent_monitor(),
            self._metrics_collector(),
            self._cleanup_tasks()
        )
    
    async def stop(self):
        """Stop the orchestration agent gracefully"""
        self.logger.info("Stopping orchestration agent")
        self.shutdown_requested = True
        
        # Wait for active tasks to complete or timeout
        timeout = 30  # seconds
        start_time = datetime.utcnow()
        
        while self.active_tasks and (datetime.utcnow() - start_time).seconds < timeout:
            await asyncio.sleep(1)
        
        # Force stop remaining tasks
        for task_id in list(self.active_tasks.keys()):
            await self._cancel_task(task_id)
        
        self.is_running = False
        self.logger.info("Orchestration agent stopped")
    
    def register_agent(self, name: str, agent_type: str, capabilities: List[str], callback: Callable):
        """Register a new agent with the orchestration system"""
        agent_info = AgentInfo(
            name=name,
            type=agent_type,
            status=AgentStatus.IDLE,
            capabilities=capabilities,
            last_heartbeat=datetime.utcnow()
        )
        
        self.agents[name] = agent_info
        self.agent_callbacks[name] = callback
        
        self.logger.info(f"Registered agent: {name} ({agent_type}) with capabilities: {capabilities}")
        
        # Emit registration event
        self.event_bus.emit(Event(
            type="agent.registered",
            data={"name": name, "type": agent_type, "capabilities": capabilities}
        ))
    
    def unregister_agent(self, name: str):
        """Unregister an agent from the orchestration system"""
        if name in self.agents:
            # Cancel any active tasks for this agent
            for task in self.active_tasks.values():
                if task.agent_type == self.agents[name].type:
                    asyncio.create_task(self._cancel_task(task.id))
            
            del self.agents[name]
            del self.agent_callbacks[name]
            
            self.logger.info(f"Unregistered agent: {name}")
            
            # Emit unregistration event
            self.event_bus.emit(Event(
                type="agent.unregistered",
                data={"name": name}
            ))
    
    async def submit_task(self, task_type: str, agent_type: str, payload: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.NORMAL, 
                         scheduled_at: Optional[datetime] = None) -> str:
        """Submit a new task for execution"""
        task = Task(
            type=task_type,
            priority=priority,
            agent_type=agent_type,
            payload=payload,
            scheduled_at=scheduled_at or datetime.utcnow()
        )
        
        # Check for conflicts
        if await self._check_task_conflicts(task):
            raise ValueError(f"Task conflicts with existing operations: {task.type}")
        
        self.pending_tasks.append(task)
        self.pending_tasks.sort(key=lambda t: (t.priority.value, t.scheduled_at), reverse=True)
        
        self.logger.info(f"Submitted task: {task.id} ({task.type}) for agent type: {agent_type}")
        
        # Emit task submission event
        self.event_bus.emit(Event(
            type="task.submitted",
            data={"task_id": task.id, "type": task.type, "agent_type": agent_type}
        ))
        
        return task.id
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or active task"""
        # Check pending tasks
        for i, task in enumerate(self.pending_tasks):
            if task.id == task_id:
                self.pending_tasks.pop(i)
                self.logger.info(f"Cancelled pending task: {task_id}")
                return True
        
        # Check active tasks
        if task_id in self.active_tasks:
            await self._cancel_task(task_id)
            return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "agent_type": task.agent_type
            }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "agent_type": task.agent_type,
                "result": task.result,
                "error": task.error
            }
        
        # Check pending tasks
        for task in self.pending_tasks:
            if task.id == task_id:
                return {
                    "id": task.id,
                    "type": task.type,
                    "status": "pending",
                    "created_at": task.created_at.isoformat(),
                    "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
                    "agent_type": task.agent_type
                }
        
        return None
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the status of an agent"""
        if agent_name not in self.agents:
            return None
        
        agent = self.agents[agent_name]
        return {
            "name": agent.name,
            "type": agent.type,
            "status": agent.status.value,
            "capabilities": agent.capabilities,
            "last_heartbeat": agent.last_heartbeat.isoformat(),
            "current_task": agent.current_task,
            "total_tasks_completed": agent.total_tasks_completed,
            "total_tasks_failed": agent.total_tasks_failed,
            "average_execution_time": agent.average_execution_time
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "is_running": self.is_running,
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.ACTIVE]),
            "pending_tasks": len(self.pending_tasks),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agents": {name: self.get_agent_status(name) for name in self.agents.keys()}
        }
    
    async def _task_scheduler(self):
        """Background task scheduler"""
        while not self.shutdown_requested:
            try:
                await self._process_pending_tasks()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                self.logger.error(f"Error in task scheduler: {e}")
                await asyncio.sleep(5)
    
    async def _process_pending_tasks(self):
        """Process pending tasks and assign them to available agents"""
        if not self.pending_tasks:
            return
        
        # Limit concurrent tasks
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return
        
        current_time = datetime.utcnow()
        
        for i, task in enumerate(self.pending_tasks):
            # Check if task is scheduled for future execution
            if task.scheduled_at and task.scheduled_at > current_time:
                continue
            
            # Find available agent
            available_agent = self._find_available_agent(task.agent_type)
            if not available_agent:
                continue
            
            # Remove from pending and add to active
            self.pending_tasks.pop(i)
            self.active_tasks[task.id] = task
            
            # Update agent status
            self.agents[available_agent].status = AgentStatus.BUSY
            self.agents[available_agent].current_task = task.id
            
            # Execute task
            asyncio.create_task(self._execute_task(task, available_agent))
            
            break  # Process one task at a time
    
    def _find_available_agent(self, agent_type: str) -> Optional[str]:
        """Find an available agent of the specified type"""
        for name, agent in self.agents.items():
            if (agent.type == agent_type and 
                agent.status in [AgentStatus.IDLE, AgentStatus.ACTIVE] and
                agent.current_task is None):
                return name
        return None
    
    async def _execute_task(self, task: Task, agent_name: str):
        """Execute a task using the specified agent"""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Executing task {task.id} with agent {agent_name}")
            
            # Get agent callback
            callback = self.agent_callbacks[agent_name]
            
            # Execute task with timeout
            result = await asyncio.wait_for(
                callback(task.type, task.payload),
                timeout=task.timeout_seconds
            )
            
            # Task completed successfully
            task.status = "completed"
            task.result = result
            
            # Update agent statistics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            agent = self.agents[agent_name]
            agent.total_tasks_completed += 1
            agent.average_execution_time = (
                (agent.average_execution_time * (agent.total_tasks_completed - 1) + execution_time) /
                agent.total_tasks_completed
            )
            
            self.logger.info(f"Task {task.id} completed successfully in {execution_time:.2f}s")
            
            # Emit completion event
            self.event_bus.emit(Event(
                type="task.completed",
                data={"task_id": task.id, "agent_name": agent_name, "result": result}
            ))
            
        except asyncio.TimeoutError:
            self.logger.error(f"Task {task.id} timed out after {task.timeout_seconds}s")
            task.status = "timeout"
            task.error = f"Task timed out after {task.timeout_seconds} seconds"
            self.agents[agent_name].total_tasks_failed += 1
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            task.status = "failed"
            task.error = str(e)
            self.agents[agent_name].total_tasks_failed += 1
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = "pending"
                task.error = None
                self.pending_tasks.append(task)
                self.logger.info(f"Retrying task {task.id} (attempt {task.retry_count}/{task.max_retries})")
        
        finally:
            # Clean up
            if task.id in self.active_tasks:
                self.completed_tasks[task.id] = self.active_tasks.pop(task.id)
            
            # Update agent status
            agent = self.agents[agent_name]
            agent.status = AgentStatus.IDLE
            agent.current_task = None
    
    async def _cancel_task(self, task_id: str):
        """Cancel an active task"""
        if task_id not in self.active_tasks:
            return
        
        task = self.active_tasks[task_id]
        task.status = "cancelled"
        
        # Find and update agent
        for agent in self.agents.values():
            if agent.current_task == task_id:
                agent.status = AgentStatus.IDLE
                agent.current_task = None
                break
        
        self.completed_tasks[task_id] = self.active_tasks.pop(task_id)
        
        self.logger.info(f"Cancelled task: {task_id}")
    
    async def _check_task_conflicts(self, task: Task) -> bool:
        """Check if a task conflicts with existing operations"""
        # Implement conflict detection logic based on task type and payload
        # This is a simplified version - expand based on specific requirements
        
        conflict_types = {
            "trade_execution": ["trade_execution", "position_modification"],
            "position_modification": ["trade_execution", "position_modification"],
            "risk_assessment": [],  # Risk assessment can run concurrently
            "signal_generation": []  # Signal generation can run concurrently
        }
        
        if task.type not in conflict_types:
            return False
        
        conflicting_types = conflict_types[task.type]
        
        for active_task in self.active_tasks.values():
            if active_task.type in conflicting_types:
                # Check if they operate on the same symbol/resource
                if self._tasks_conflict(task, active_task):
                    return True
        
        return False
    
    def _tasks_conflict(self, task1: Task, task2: Task) -> bool:
        """Check if two tasks conflict with each other"""
        # Extract symbol/resource information from task payloads
        symbol1 = task1.payload.get("symbol")
        symbol2 = task2.payload.get("symbol")
        
        user_id1 = task1.payload.get("user_id")
        user_id2 = task2.payload.get("user_id")
        
        # Tasks conflict if they operate on the same symbol for the same user
        return symbol1 == symbol2 and user_id1 == user_id2
    
    async def _agent_monitor(self):
        """Monitor agent health and availability"""
        while not self.shutdown_requested:
            try:
                current_time = datetime.utcnow()
                
                for name, agent in self.agents.items():
                    # Check for stale heartbeats
                    if (current_time - agent.last_heartbeat).seconds > self.heartbeat_timeout:
                        if agent.status != AgentStatus.ERROR:
                            self.logger.warning(f"Agent {name} heartbeat timeout")
                            agent.status = AgentStatus.ERROR
                            
                            # Cancel current task if any
                            if agent.current_task:
                                await self._cancel_task(agent.current_task)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in agent monitor: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_collector(self):
        """Collect and emit system metrics"""
        while not self.shutdown_requested:
            try:
                metrics = {
                    "orchestration.agents.total": len(self.agents),
                    "orchestration.agents.active": len([a for a in self.agents.values() if a.status == AgentStatus.ACTIVE]),
                    "orchestration.tasks.pending": len(self.pending_tasks),
                    "orchestration.tasks.active": len(self.active_tasks),
                    "orchestration.tasks.completed": len(self.completed_tasks)
                }
                
                for metric_name, value in metrics.items():
                    self.metrics.gauge(metric_name, value)
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                self.logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_tasks(self):
        """Clean up old completed tasks"""
        while not self.shutdown_requested:
            try:
                current_time = datetime.utcnow()
                cleanup_threshold = current_time - timedelta(hours=24)
                
                # Remove old completed tasks
                old_tasks = [
                    task_id for task_id, task in self.completed_tasks.items()
                    if task.created_at < cleanup_threshold
                ]
                
                for task_id in old_tasks:
                    del self.completed_tasks[task_id]
                
                if old_tasks:
                    self.logger.info(f"Cleaned up {len(old_tasks)} old completed tasks")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error in task cleanup: {e}")
                await asyncio.sleep(3600)
    
    # Event handlers
    async def _handle_agent_heartbeat(self, event: Event):
        """Handle agent heartbeat events"""
        agent_name = event.data.get("agent_name")
        if agent_name in self.agents:
            self.agents[agent_name].last_heartbeat = datetime.utcnow()
            if self.agents[agent_name].status == AgentStatus.ERROR:
                self.agents[agent_name].status = AgentStatus.IDLE
    
    async def _handle_task_completed(self, event: Event):
        """Handle task completion events"""
        task_id = event.data.get("task_id")
        self.logger.info(f"Received task completion event for task: {task_id}")
    
    async def _handle_task_failed(self, event: Event):
        """Handle task failure events"""
        task_id = event.data.get("task_id")
        error = event.data.get("error")
        self.logger.error(f"Received task failure event for task: {task_id}, error: {error}")
    
    async def _handle_signal_generated(self, event: Event):
        """Handle signal generation events"""
        signal_data = event.data
        self.logger.info(f"Received signal: {signal_data.get('symbol')} - {signal_data.get('action')}")
        
        # Submit trade execution task if signal meets criteria
        if signal_data.get("confidence", 0) >= settings.trading.signal_confidence_threshold:
            await self.submit_task(
                task_type="trade_execution",
                agent_type="trading",
                payload=signal_data,
                priority=TaskPriority.HIGH
            )
    
    async def _handle_trade_executed(self, event: Event):
        """Handle trade execution events"""
        trade_data = event.data
        self.logger.info(f"Trade executed: {trade_data.get('symbol')} - {trade_data.get('side')} - {trade_data.get('amount')}")
    
    async def _handle_risk_threshold_exceeded(self, event: Event):
        """Handle risk threshold exceeded events"""
        risk_data = event.data
        self.logger.warning(f"Risk threshold exceeded: {risk_data.get('type')} - {risk_data.get('value')}")
        
        # Submit emergency risk management task
        await self.submit_task(
            task_type="emergency_risk_management",
            agent_type="risk_guard",
            payload=risk_data,
            priority=TaskPriority.CRITICAL
        )

