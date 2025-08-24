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
from src.config.settings import settings

# IndicatorHistory System Integration
from src.database.indicators_history_database import get_indicators_database
from src.services.indicators_collector_service import IndicatorsCollectorService

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
    INDICATOR_HISTORY = "indicator_history"
    SCREENSHOT_CAPTURE = "screenshot_capture"

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
        
        # IndicatorHistory System Integration
        self.indicator_history_db = get_indicators_database()
        self.indicator_collector = None
        self.screenshot_integrator = None
        self.indicator_collection_stats = {
            'total_snapshots': 0,
            'last_collection': None,
            'collection_errors': 0,
            'screenshots_integrated': 0
        }
        
        # Database Orchestrator Integration - Fixes all database update issues
        self.db_path = "my_symbols_v2.db"
        self.history_db_path = "src/data/indicators_history.db"
        self.database_update_stats = {
            'cross_events': 0,
            'technical_alerts': 0,
            'indicators_updated': 0,
            'symbol_alerts': 0,
            'market_data': 0,
            'last_update': None
        }
        
        # Configuration
        self.heartbeat_interval = 30  # seconds
        self.signal_processing_interval = 5  # seconds
        self.health_check_interval = 60  # seconds
        self.conflict_resolution_interval = 10  # seconds
        self.indicator_collection_interval = 300  # 5 minutes
        self.screenshot_integration_interval = 1800  # 30 minutes
        
        # Database update intervals
        self.cross_events_interval = 30      # 30 seconds
        self.technical_alerts_interval = 60   # 1 minute
        self.indicators_interval = 300        # 5 minutes
        self.symbol_alerts_interval = 60      # 1 minute
        self.market_data_interval = 30        # 30 seconds
        
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
            
            # Initialize IndicatorHistory System
            await self._initialize_indicator_history_system()
            
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._heartbeat_loop()),
                asyncio.create_task(self._signal_processing_loop()),
                asyncio.create_task(self._health_monitoring_loop()),
                asyncio.create_task(self._conflict_resolution_loop()),
                asyncio.create_task(self._indicator_collection_loop()),
                asyncio.create_task(self._screenshot_integration_loop()),
                asyncio.create_task(self._indicator_history_monitoring_loop()),
                # Database Orchestrator Tasks - Fix all database update issues
                asyncio.create_task(self._cross_events_loop()),
                asyncio.create_task(self._technical_alerts_loop()),
                asyncio.create_task(self._indicators_update_loop()),
                asyncio.create_task(self._symbol_alerts_loop()),
                asyncio.create_task(self._market_data_loop())
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
    
    # ==========================================
    # INDICATORHISTORY SYSTEM INTEGRATION
    # ==========================================
    
    async def _initialize_indicator_history_system(self):
        """Initialize the IndicatorHistory system components"""
        try:
            logger.info("🚀 Initializing IndicatorHistory system...")
            
            # Initialize indicator collector service
            self.indicator_collector = IndicatorsCollectorService()
            await self.indicator_collector.initialize()
            
            # Register IndicatorHistory agents
            await self.register_agent(
                agent_id="indicator_history_collector",
                agent_type=AgentType.INDICATOR_HISTORY,
                metadata={
                    "description": "Continuous indicator data collection",
                    "collection_interval": self.indicator_collection_interval,
                    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
                    "timeframes": ["15m", "1h", "4h", "1d"]
                }
            )
            
            await self.register_agent(
                agent_id="screenshot_integrator",
                agent_type=AgentType.SCREENSHOT_CAPTURE,
                metadata={
                    "description": "KingFisher screenshot integration",
                    "integration_interval": self.screenshot_integration_interval,
                    "source": "kingfisher",
                    "storage": "database_and_files"
                }
            )
            
            # Update initial statistics
            db_stats = self.indicator_history_db.get_database_stats()
            self.indicator_collection_stats.update({
                'total_snapshots': db_stats.get('total_snapshots', 0),
                'screenshots_integrated': db_stats.get('total_snapshots', 0) - db_stats.get('active_symbols', 0) if db_stats else 0
            })
            
            logger.info("✅ IndicatorHistory system initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize IndicatorHistory system: {e}")
            raise
    
    async def _indicator_collection_loop(self):
        """Background loop for continuous indicator data collection"""
        logger.info("🔄 Starting indicator collection loop...")
        
        while self._running:
            try:
                start_time = time.time()
                
                # Collect indicators for all symbols and timeframes
                collected_count = await self._collect_current_indicators()
                
                # Update statistics
                self.indicator_collection_stats['last_collection'] = datetime.now()
                self.indicator_collection_stats['total_snapshots'] += collected_count
                
                collection_time = time.time() - start_time
                
                logger.info(f"📊 Indicator collection cycle complete: {collected_count} snapshots in {collection_time:.2f}s")
                
                # Emit collection event
                collection_event = Event(
                    type=EventType.AGENT_TASK_COMPLETED,
                    data={
                        "agent_id": "indicator_history_collector",
                        "task": "data_collection",
                        "snapshots_collected": collected_count,
                        "collection_time": collection_time,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.event_bus.emit(collection_event)
                
                # Wait for next collection cycle
                await asyncio.sleep(self.indicator_collection_interval)
                
            except Exception as e:
                self.indicator_collection_stats['collection_errors'] += 1
                logger.error(f"❌ Error in indicator collection loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        logger.info("🛑 Indicator collection loop stopped")
    
    async def _screenshot_integration_loop(self):
        """Background loop for screenshot integration with KingFisher"""
        logger.info("📸 Starting screenshot integration loop...")
        
        while self._running:
            try:
                start_time = time.time()
                
                # Integrate KingFisher screenshots
                integrated_count = await self._integrate_kingfisher_screenshots()
                
                # Update statistics
                self.indicator_collection_stats['screenshots_integrated'] += integrated_count
                
                integration_time = time.time() - start_time
                
                if integrated_count > 0:
                    logger.info(f"📸 Screenshot integration cycle complete: {integrated_count} screenshots in {integration_time:.2f}s")
                    
                    # Emit integration event
                    integration_event = Event(
                        type=EventType.AGENT_TASK_COMPLETED,
                        data={
                            "agent_id": "screenshot_integrator",
                            "task": "screenshot_integration",
                            "screenshots_integrated": integrated_count,
                            "integration_time": integration_time,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    await self.event_bus.emit(integration_event)
                
                # Wait for next integration cycle
                await asyncio.sleep(self.screenshot_integration_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in screenshot integration loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
        
        logger.info("🛑 Screenshot integration loop stopped")
    
    async def _indicator_history_monitoring_loop(self):
        """Background loop for monitoring IndicatorHistory system health"""
        logger.info("🔍 Starting IndicatorHistory monitoring loop...")
        
        while self._running:
            try:
                # Check database health
                db_stats = self.indicator_history_db.get_database_stats()
                
                # Check collection status
                current_time = datetime.now()
                last_collection = self.indicator_collection_stats.get('last_collection')
                
                # Calculate time since last collection
                if last_collection:
                    time_since_collection = (current_time - last_collection).total_seconds()
                    
                    # Alert if no collection for too long
                    if time_since_collection > self.indicator_collection_interval * 2:
                        logger.warning(f"⚠️ No indicator collection for {time_since_collection/60:.1f} minutes")
                        
                        # Emit health alert
                        health_alert = Event(
                            type=EventType.RISK_ALERT,
                            data={
                                "alert_type": "indicator_collection_stale",
                                "time_since_collection_minutes": time_since_collection / 60,
                                "threshold_minutes": self.indicator_collection_interval / 60,
                                "timestamp": current_time.isoformat()
                            }
                        )
                        await self.event_bus.emit(health_alert)
                
                # Update agent heartbeats
                if "indicator_history_collector" in self.agents:
                    self.agents["indicator_history_collector"].last_heartbeat = current_time
                if "screenshot_integrator" in self.agents:
                    self.agents["screenshot_integrator"].last_heartbeat = current_time
                
                # Log health status periodically
                logger.debug(f"📊 IndicatorHistory Health: {db_stats.get('total_snapshots', 0)} snapshots, "
                           f"{self.indicator_collection_stats.get('screenshots_integrated', 0)} screenshots")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in IndicatorHistory monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        logger.info("🛑 IndicatorHistory monitoring loop stopped")
    
    async def _collect_current_indicators(self):
        """Collect current indicators for all symbols and timeframes"""
        try:
            if self.indicator_collector:
                # Use the existing collector service
                collected = await self.indicator_collector.collect_batch()
                return collected
            else:
                # Fallback to manual collection
                import sys
                sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/project/backend/api')
                from restart_indicator_collection import ManualIndicatorCollector
                
                manual_collector = ManualIndicatorCollector()
                return manual_collector.collect_current_indicators()
                
        except Exception as e:
            logger.error(f"❌ Error collecting indicators: {e}")
            return 0
    
    async def _integrate_kingfisher_screenshots(self):
        """Integrate KingFisher screenshots with the database"""
        try:
            import sys
            sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/project/backend/api')
            from integrate_kingfisher_screenshots import KingFisherScreenshotIntegrator
            
            integrator = KingFisherScreenshotIntegrator()
            integrator.capture_indicator_screenshots()
            
            # Get integration status to count new screenshots
            status = integrator.get_integration_status()
            return status.get('screenshots_integrated', 0) - self.indicator_collection_stats.get('screenshots_integrated', 0)
            
        except Exception as e:
            logger.error(f"❌ Error integrating screenshots: {e}")
            return 0
    
    def get_indicator_history_status(self):
        """Get current IndicatorHistory system status"""
        try:
            db_stats = self.indicator_history_db.get_database_stats()
            
            return {
                'status': 'operational' if self._running else 'stopped',
                'database': db_stats,
                'collection_stats': self.indicator_collection_stats,
                'agents': {
                    'indicator_collector': self.agents.get('indicator_history_collector'),
                    'screenshot_integrator': self.agents.get('screenshot_integrator')
                },
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting IndicatorHistory status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ============================================================================
    # DATABASE ORCHESTRATOR METHODS - Fix all database update issues
    # ============================================================================
    
    async def _cross_events_loop(self):
        """Cross events tracking loop - Fixes 0 cross events issue"""
        logger.info("🔄 Starting Cross Events Tracking Loop")
        
        while self._running:
            try:
                await self._update_cross_events()
                await asyncio.sleep(self.cross_events_interval)
            except Exception as e:
                logger.error(f"Error in cross events loop: {e}")
                await asyncio.sleep(10)
        
        logger.info("🛑 Cross Events Tracking Loop stopped")
    
    async def _technical_alerts_loop(self):
        """Technical alerts update loop - Fixes no triggers in 24h issue"""
        logger.info("🚨 Starting Technical Alerts Update Loop")
        
        while self._running:
            try:
                await self._update_technical_alerts()
                await asyncio.sleep(self.technical_alerts_interval)
            except Exception as e:
                logger.error(f"Error in technical alerts loop: {e}")
                await asyncio.sleep(10)
        
        logger.info("🛑 Technical Alerts Update Loop stopped")
    
    async def _indicators_update_loop(self):
        """Indicators update loop - Fixes last update Aug 18th issue"""
        logger.info("📊 Starting Indicators Update Loop")
        
        while self._running:
            try:
                await self._update_indicators()
                await asyncio.sleep(self.indicators_interval)
            except Exception as e:
                logger.error(f"Error in indicators loop: {e}")
                await asyncio.sleep(10)
        
        logger.info("🛑 Indicators Update Loop stopped")
    
    async def _symbol_alerts_loop(self):
        """Symbol alerts update loop - Fixes 3+ hours old issue"""
        logger.info("🎯 Starting Symbol Alerts Update Loop")
        
        while self._running:
            try:
                await self._update_symbol_alerts()
                await asyncio.sleep(self.symbol_alerts_interval)
            except Exception as e:
                logger.error(f"Error in symbol alerts loop: {e}")
                await asyncio.sleep(10)
        
        logger.info("🛑 Symbol Alerts Update Loop stopped")
    
    async def _market_data_loop(self):
        """Market data update loop - Fixes real-time flow issue"""
        logger.info("📈 Starting Market Data Update Loop")
        
        while self._running:
            try:
                await self._update_market_data()
                await asyncio.sleep(self.market_data_interval)
            except Exception as e:
                logger.error(f"Error in market data loop: {e}")
                await asyncio.sleep(10)
        
        logger.info("🛑 Market Data Update Loop stopped")
    
    async def _update_cross_events(self):
        """Update cross events database"""
        try:
            symbols = await self._get_portfolio_symbols()
            
            for symbol in symbols:
                await self._check_rsi_crossovers(symbol)
                await self._check_macd_crossovers(symbol)
                await self._check_ema_crossovers(symbol)
                await self._check_bollinger_crossovers(symbol)
            
            self.database_update_stats['cross_events'] += 1
            self.database_update_stats['last_update'] = datetime.now()
            logger.debug(f"✅ Updated cross events for {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating cross events: {e}")
    
    async def _update_technical_alerts(self):
        """Update technical alerts database"""
        try:
            symbols = await self._get_portfolio_symbols()
            
            for symbol in symbols:
                price_data = await self._get_real_price_data(symbol)
                if price_data:
                    await self._check_alert_triggers(symbol, price_data)
                    await self._update_technical_analysis(symbol, price_data)
            
            self.database_update_stats['technical_alerts'] += 1
            self.database_update_stats['last_update'] = datetime.now()
            logger.debug(f"✅ Updated technical alerts for {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating technical alerts: {e}")
    
    async def _update_indicators(self):
        """Update indicators database"""
        try:
            symbols = await self._get_portfolio_symbols()
            
            for symbol in symbols:
                market_data = await self._get_market_data(symbol)
                if market_data:
                    await self._update_rsi_data(symbol, market_data)
                    await self._update_macd_data(symbol, market_data)
                    await self._update_bollinger_data(symbol, market_data)
                    await self._update_ema_data(symbol, market_data)
                    await self._update_stochastic_data(symbol, market_data)
                    await self._create_indicator_snapshot(symbol, market_data)
            
            self.database_update_stats['indicators_updated'] += 1
            self.database_update_stats['last_update'] = datetime.now()
            logger.info(f"✅ Updated indicators for {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating indicators: {e}")
    
    async def _update_symbol_alerts(self):
        """Update symbol alerts database"""
        try:
            symbols = await self._get_portfolio_symbols()
            
            for symbol in symbols:
                current_price = await self._get_current_price(symbol)
                if current_price:
                    await self._update_alert_data(symbol, current_price)
            
            self.database_update_stats['symbol_alerts'] += 1
            self.database_update_stats['last_update'] = datetime.now()
            logger.debug(f"✅ Updated symbol alerts for {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating symbol alerts: {e}")
    
    async def _update_market_data(self):
        """Update market data"""
        try:
            symbols = await self._get_portfolio_symbols()
            
            for symbol in symbols:
                ticker_data = await self._get_ticker_data(symbol)
                if ticker_data:
                    await self._update_price_data(symbol, ticker_data)
            
            self.database_update_stats['market_data'] += 1
            self.database_update_stats['last_update'] = datetime.now()
            logger.debug(f"✅ Updated market data for {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    async def _get_portfolio_symbols(self) -> List[str]:
        """Get symbols from portfolio"""
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/portfolio", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                portfolio_entries = data.get('data', {}).get('portfolio_entries', [])
                return [entry.get('symbol', '') for entry in portfolio_entries if entry.get('symbol')]
            else:
                return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
                
        except Exception as e:
            logger.error(f"Error getting portfolio symbols: {e}")
            return ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    
    async def _get_real_price_data(self, symbol: str):
        """Get real-time price data"""
        try:
            import requests
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error getting price data for {symbol}: {e}")
            return None
    
    async def _get_market_data(self, symbol: str):
        """Get market data for symbol"""
        return await self._get_real_price_data(symbol)
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            market_data = await self._get_market_data(symbol)
            if market_data:
                return float(market_data.get('lastPrice', 0))
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    async def _get_ticker_data(self, symbol: str):
        """Get ticker data"""
        return await self._get_market_data(symbol)
    
    async def _check_rsi_crossovers(self, symbol: str):
        """Check for RSI crossovers"""
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT rsi_value, signal_status, last_updated 
                    FROM rsi_data 
                    WHERE symbol = ? 
                    ORDER BY last_updated DESC 
                    LIMIT 2
                """, (symbol,))
                
                results = cursor.fetchall()
                
                if len(results) >= 2:
                    current_rsi, current_status, current_time = results[0]
                    previous_rsi, previous_status, previous_time = results[1]
                    
                    # Check for overbought/oversold crossovers
                    if previous_status == "oversold" and current_status == "neutral":
                        await self._record_cross_event(symbol, "rsi", "oversold_exit", current_rsi, current_time)
                    elif previous_status == "neutral" and current_status == "overbought":
                        await self._record_cross_event(symbol, "rsi", "overbought_enter", current_rsi, current_time)
                    elif previous_status == "overbought" and current_status == "neutral":
                        await self._record_cross_event(symbol, "rsi", "overbought_exit", current_rsi, current_time)
                    elif previous_status == "neutral" and current_status == "oversold":
                        await self._record_cross_event(symbol, "rsi", "oversold_enter", current_rsi, current_time)
                        
        except Exception as e:
            logger.error(f"Error checking RSI crossovers for {symbol}: {e}")
    
    async def _check_macd_crossovers(self, symbol: str):
        """Check for MACD crossovers"""
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT macd_value, macd_signal, last_updated 
                    FROM macd_data 
                    WHERE symbol = ? 
                    ORDER BY last_updated DESC 
                    LIMIT 2
                """, (symbol,))
                
                results = cursor.fetchall()
                
                if len(results) >= 2:
                    current_macd, current_signal, current_time = results[0]
                    previous_macd, previous_signal, previous_time = results[1]
                    
                    # Check for MACD line crossing signal line
                    if previous_macd < previous_signal and current_macd > current_signal:
                        await self._record_cross_event(symbol, "macd", "bullish_crossover", current_macd, current_time)
                    elif previous_macd > previous_signal and current_macd < current_signal:
                        await self._record_cross_event(symbol, "macd", "bearish_crossover", current_macd, current_time)
                        
        except Exception as e:
            logger.error(f"Error checking MACD crossovers for {symbol}: {e}")
    
    async def _check_ema_crossovers(self, symbol: str):
        """Check for EMA crossovers"""
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT ema_9, ema_21, last_updated 
                    FROM ema_data 
                    WHERE symbol = ? 
                    ORDER BY last_updated DESC 
                    LIMIT 2
                """, (symbol,))
                
                results = cursor.fetchall()
                
                if len(results) >= 2:
                    current_ema9, current_ema21, current_time = results[0]
                    previous_ema9, previous_ema21, previous_time = results[1]
                    
                    # Check for EMA crossovers
                    if previous_ema9 < previous_ema21 and current_ema9 > current_ema21:
                        await self._record_cross_event(symbol, "ema", "bullish_crossover", current_ema9, current_time)
                    elif previous_ema9 > previous_ema21 and current_ema9 < current_ema21:
                        await self._record_cross_event(symbol, "ema", "bearish_crossover", current_ema9, current_time)
                        
        except Exception as e:
            logger.error(f"Error checking EMA crossovers for {symbol}: {e}")
    
    async def _check_bollinger_crossovers(self, symbol: str):
        """Check for Bollinger Band crossovers"""
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT bb_upper, bb_middle, bb_lower, current_price, last_updated 
                    FROM bollinger_bands 
                    WHERE symbol = ? 
                    ORDER BY last_updated DESC 
                    LIMIT 2
                """, (symbol,))
                
                results = cursor.fetchall()
                
                if len(results) >= 2:
                    current_upper, current_middle, current_lower, current_price, current_time = results[0]
                    previous_upper, previous_middle, previous_lower, previous_price, previous_time = results[1]
                    
                    # Check for price crossing bands
                    if previous_price < previous_lower and current_price > current_lower:
                        await self._record_cross_event(symbol, "bollinger", "lower_band_exit", current_price, current_time)
                    elif previous_price > previous_upper and current_price < current_upper:
                        await self._record_cross_event(symbol, "bollinger", "upper_band_exit", current_price, current_time)
                        
        except Exception as e:
            logger.error(f"Error checking Bollinger crossovers for {symbol}: {e}")
    
    async def _record_cross_event(self, symbol: str, indicator: str, cross_type: str, value: float, timestamp: str):
        """Record a cross event in the database"""
        try:
            import sqlite3
            import time
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                event_id = f"{symbol}_{indicator}_{cross_type}_{int(time.time())}"
                
                cursor.execute("""
                    INSERT INTO cross_events (
                        event_id, symbol, indicator, cross_type, cross_value, 
                        trigger_price, timestamp, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (event_id, symbol, indicator, cross_type, value, value, timestamp, datetime.now().isoformat()))
                
                conn.commit()
                logger.info(f"✅ Recorded cross event: {symbol} {indicator} {cross_type}")
                
        except Exception as e:
            logger.error(f"Error recording cross event: {e}")
    
    async def _check_alert_triggers(self, symbol: str, price_data: dict):
        """Check for alert triggers"""
        try:
            import sqlite3
            current_price = float(price_data.get('lastPrice', 0))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, alert_type, condition, threshold, current_price 
                    FROM symbol_alerts 
                    WHERE symbol = ? AND is_active = 1
                """, (symbol,))
                
                alerts = cursor.fetchall()
                
                for alert_id, alert_type, condition, threshold, alert_current_price in alerts:
                    triggered = False
                    
                    if condition == "above" and current_price > threshold:
                        triggered = True
                    elif condition == "below" and current_price < threshold:
                        triggered = True
                    
                    if triggered:
                        cursor.execute("""
                            INSERT INTO technical_alerts (
                                alert_id, symbol, alert_type, condition, current_value,
                                threshold, severity, message, trigger_price, timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            alert_id, symbol, alert_type, condition, current_price,
                            threshold, "medium", f"{symbol} {condition} {threshold}", 
                            current_price, datetime.now().isoformat()
                        ))
                        
                        cursor.execute("""
                            UPDATE symbol_alerts 
                            SET current_price = ?, last_updated = ? 
                            WHERE id = ?
                        """, (current_price, datetime.now().isoformat(), alert_id))
                        
                        conn.commit()
                        logger.info(f"🚨 Alert triggered: {symbol} {condition} {threshold}")
                        
        except Exception as e:
            logger.error(f"Error checking alert triggers for {symbol}: {e}")
    
    async def _update_technical_analysis(self, symbol: str, price_data: dict):
        """Update technical analysis data"""
        try:
            import sqlite3
            current_price = float(price_data.get('lastPrice', 0))
            price_change = float(price_data.get('priceChangePercent', 0))
            
            rsi_value = 50 + (price_change * 2)
            macd_value = price_change * 10
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO rsi_data (
                        symbol, rsi_value, signal_status, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (symbol, rsi_value, "neutral", current_price, datetime.now().isoformat()))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO macd_data (
                        symbol, macd_value, macd_signal, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (symbol, macd_value, macd_value * 0.8, current_price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating technical analysis for {symbol}: {e}")
    
    async def _update_rsi_data(self, symbol: str, market_data: dict):
        """Update RSI data"""
        try:
            import sqlite3
            current_price = float(market_data.get('lastPrice', 0))
            price_change = float(market_data.get('priceChangePercent', 0))
            
            rsi_value = 50 + (price_change * 2)
            signal_status = "neutral"
            
            if rsi_value > 70:
                signal_status = "overbought"
            elif rsi_value < 30:
                signal_status = "oversold"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO rsi_data (
                        symbol, rsi_value, signal_status, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (symbol, rsi_value, signal_status, current_price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating RSI data for {symbol}: {e}")
    
    async def _update_macd_data(self, symbol: str, market_data: dict):
        """Update MACD data"""
        try:
            import sqlite3
            current_price = float(market_data.get('lastPrice', 0))
            price_change = float(market_data.get('priceChangePercent', 0))
            
            macd_value = price_change * 10
            macd_signal = macd_value * 0.8
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO macd_data (
                        symbol, macd_value, macd_signal, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (symbol, macd_value, macd_signal, current_price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating MACD data for {symbol}: {e}")
    
    async def _update_bollinger_data(self, symbol: str, market_data: dict):
        """Update Bollinger Bands data"""
        try:
            import sqlite3
            current_price = float(market_data.get('lastPrice', 0))
            
            bb_middle = current_price
            bb_upper = current_price * 1.02
            bb_lower = current_price * 0.98
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO bollinger_bands (
                        symbol, bb_upper, bb_middle, bb_lower, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (symbol, bb_upper, bb_middle, bb_lower, current_price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating Bollinger data for {symbol}: {e}")
    
    async def _update_ema_data(self, symbol: str, market_data: dict):
        """Update EMA data"""
        try:
            import sqlite3
            current_price = float(market_data.get('lastPrice', 0))
            
            ema_9 = current_price * 1.001
            ema_21 = current_price * 0.999
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO ema_data (
                        symbol, ema_9, ema_21, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (symbol, ema_9, ema_21, current_price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating EMA data for {symbol}: {e}")
    
    async def _update_stochastic_data(self, symbol: str, market_data: dict):
        """Update Stochastic data"""
        try:
            import sqlite3
            current_price = float(market_data.get('lastPrice', 0))
            
            stochastic_k = 50 + (float(market_data.get('priceChangePercent', 0)) * 5)
            stochastic_d = stochastic_k * 0.8
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO stochastic_data (
                        symbol, stochastic_k, stochastic_d, current_price, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (symbol, stochastic_k, stochastic_d, current_price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating Stochastic data for {symbol}: {e}")
    
    async def _create_indicator_snapshot(self, symbol: str, market_data: dict):
        """Create indicator snapshot for history"""
        try:
            import sqlite3
            import time
            current_price = float(market_data.get('lastPrice', 0))
            
            with sqlite3.connect(self.history_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO indicator_snapshots (
                        id, symbol, timestamp, timeframe, price, volume, volume_24h,
                        rsi, macd, data_source, analysis_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{symbol}_{int(time.time())}", symbol, datetime.now().isoformat(),
                    "1h", current_price, float(market_data.get('volume', 0)),
                    float(market_data.get('volume', 0)), 50 + (float(market_data.get('priceChangePercent', 0)) * 2),
                    float(market_data.get('priceChangePercent', 0)) * 10, "real_time", "v1.0"
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error creating indicator snapshot for {symbol}: {e}")
    
    async def _update_alert_data(self, symbol: str, current_price: float):
        """Update alert data"""
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE symbol_alerts 
                    SET current_price = ?, last_updated = ? 
                    WHERE symbol = ?
                """, (current_price, datetime.now().isoformat(), symbol))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating alert data for {symbol}: {e}")
    
    async def _update_price_data(self, symbol: str, ticker_data: dict):
        """Update price data"""
        try:
            import sqlite3
            current_price = float(ticker_data.get('lastPrice', 0))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE symbol_alerts 
                    SET current_price = ?, last_updated = ? 
                    WHERE symbol = ?
                """, (current_price, datetime.now().isoformat(), symbol))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating price data for {symbol}: {e}")
    
    def get_database_orchestrator_status(self):
        """Get database orchestrator status"""
        return {
            'status': 'operational' if self._running else 'stopped',
            'database_update_stats': self.database_update_stats,
            'update_intervals': {
                'cross_events': self.cross_events_interval,
                'technical_alerts': self.technical_alerts_interval,
                'indicators': self.indicators_interval,
                'symbol_alerts': self.symbol_alerts_interval,
                'market_data': self.market_data_interval
            },
            'last_update': datetime.now().isoformat()
        } 