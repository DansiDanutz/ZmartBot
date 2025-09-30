#!/usr/bin/env python3
"""
🎯 MASTER ORCHESTRATION AGENT - ZmartBot Central Command
The ultimate coordination layer that manages ALL modules and agents in perfect harmony
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

# Core imports
from src.utils.event_bus import EventBus, Event, EventType
from src.utils.metrics import MetricsCollector

# All integrated services
from src.services.trading_center import trading_center
from src.services.my_symbols_orchestrator import my_symbols_orchestrator
from src.services.unified_signal_center import UnifiedSignalCenter
from src.services.unified_scoring_system import unified_scoring_system
from src.agents.risk_guard.risk_guard_agent import RiskGuardAgent
from src.agents.pattern_analysis.master_pattern_agent import MasterPatternAgent
from src.agents.sentiment.grok_x_sentiment_agent import GrokXSentimentAgent
from src.services.vault_management_system import VaultManagementSystem
from src.services.telegram_notifications import get_telegram_service

# Get telegram service instance
telegram_notifier = get_telegram_service()

logger = logging.getLogger(__name__)

class SystemState(Enum):
    """System operational states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class TradingMode(Enum):
    """Trading operational modes"""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"
    SIMULATION = "simulation"

@dataclass
class SystemHealth:
    """System health metrics"""
    api_status: Dict[str, bool] = field(default_factory=dict)
    module_status: Dict[str, str] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_count: int = 0
    warning_count: int = 0
    last_check: datetime = field(default_factory=datetime.now)

@dataclass
class TradingSession:
    """Trading session tracking"""
    session_id: str
    start_time: datetime
    mode: TradingMode
    symbols_monitored: Set[str] = field(default_factory=set)
    signals_processed: int = 0
    trades_executed: int = 0
    profit_loss: float = 0.0
    win_rate: float = 0.0

class MasterOrchestrationAgent:
    """
    Master Orchestration Agent - The brain of ZmartBot
    Coordinates all modules, agents, and services for optimal trading performance
    """
    
    def __init__(self, mode: TradingMode = TradingMode.PAPER):
        """Initialize the Master Orchestration Agent"""
        
        # System configuration
        self.mode = mode
        self.state = SystemState.INITIALIZING
        self.session: Optional[TradingSession] = None
        
        # Core components
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        
        # All integrated agents and services
        self.trading_center = trading_center
        self.my_symbols_orchestrator = my_symbols_orchestrator
        self.signal_center = UnifiedSignalCenter()
        self.scoring_system = unified_scoring_system
        self.risk_guard = RiskGuardAgent()
        self.pattern_agent = MasterPatternAgent()
        self.sentiment_agent = GrokXSentimentAgent() if GrokXSentimentAgent else None
        self.vault_manager = VaultManagementSystem()
        
        # System tracking
        self.health = SystemHealth()
        self.active_modules: Dict[str, bool] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.priority_queue: asyncio.Queue = asyncio.Queue()
        
        # Configuration
        self.config = {
            'scan_interval': 30,  # seconds
            'health_check_interval': 60,  # seconds
            'my_symbols_priority': True,
            'rare_event_boost': 1.3,
            'max_concurrent_trades': 10,
            'risk_limit_daily': 0.02,  # 2% daily risk
            'emergency_stop_loss': 0.05  # 5% emergency stop
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info(f"🎯 Master Orchestration Agent initialized in {mode.value} mode")
    
    async def initialize(self) -> bool:
        """Initialize all systems and verify connections"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 MASTER ORCHESTRATION AGENT INITIALIZATION")
            logger.info("=" * 80)
            
            # Step 1: Health check
            logger.info("📋 Step 1: System Health Check...")
            await self._perform_health_check()
            
            # Step 2: Initialize My Symbols
            logger.info("📋 Step 2: Initializing My Symbols Integration...")
            if not await self.my_symbols_orchestrator.initialize_my_symbols_integration():
                logger.warning("⚠️ My Symbols initialization failed - continuing without priority symbols")
            else:
                logger.info("✅ My Symbols integration ready")
            
            # Step 3: Setup event listeners
            logger.info("📋 Step 3: Setting up event listeners...")
            self._setup_event_listeners()
            logger.info("✅ Event listeners configured")
            
            # Step 4: Initialize trading session
            logger.info("📋 Step 4: Creating trading session...")
            self.session = TradingSession(
                session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                start_time=datetime.now(),
                mode=self.mode
            )
            logger.info(f"✅ Trading session created: {self.session.session_id}")
            
            # Step 5: Notification system
            logger.info("📋 Step 5: Testing notification system...")
            if telegram_notifier.enabled:
                await telegram_notifier.send_message(
                    f"🎯 Master Orchestration Agent Started\n"
                    f"Mode: {self.mode.value}\n"
                    f"Session: {self.session.session_id}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info("✅ Telegram notifications active")
            
            # Update state
            self.state = SystemState.RUNNING
            
            logger.info("=" * 80)
            logger.info("✅ MASTER ORCHESTRATION AGENT READY")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Master Orchestration Agent: {e}")
            self.state = SystemState.ERROR
            return False
    
    async def start(self):
        """Start the orchestration system"""
        if self.state != SystemState.RUNNING:
            logger.warning(f"Cannot start - system in {self.state.value} state")
            return
        
        logger.info("🚀 Starting Master Orchestration Agent...")
        
        # Start background tasks
        self.background_tasks.append(
            asyncio.create_task(self._continuous_monitoring())
        )
        self.background_tasks.append(
            asyncio.create_task(self._process_priority_queue())
        )
        self.background_tasks.append(
            asyncio.create_task(self._health_monitor())
        )
        self.background_tasks.append(
            asyncio.create_task(self._performance_tracker())
        )
        
        logger.info("✅ All background tasks started")
    
    async def _continuous_monitoring(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting continuous monitoring...")
        
        while self.state == SystemState.RUNNING:
            try:
                scan_start = datetime.now()
                
                # Get symbols to monitor
                symbols = await self._get_monitoring_symbols()
                
                # Process in batches with priority
                await self._process_symbol_batch(symbols)
                
                # Update session stats
                if self.session:
                    self.session.symbols_monitored.update(symbols)
                
                # Calculate next scan time
                scan_duration = (datetime.now() - scan_start).total_seconds()
                wait_time = max(0, self.config['scan_interval'] - scan_duration)
                
                logger.info(f"📊 Scan complete in {scan_duration:.1f}s - Next scan in {wait_time:.0f}s")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _get_monitoring_symbols(self) -> List[str]:
        """Get list of symbols to monitor with priority ordering"""
        symbols = []
        
        # Priority 1: My Symbols (from database)
        if self.config['my_symbols_priority']:
            try:
                my_symbols = await self.my_symbols_orchestrator.my_symbols_service.get_tradeable_symbols()
                symbols.extend(my_symbols)
                logger.debug(f"Added {len(my_symbols)} My Symbols to monitoring")
            except:
                pass
        
        # Priority 2: Active vaults
        try:
            active_vaults = await self.vault_manager.get_active_vaults()
            # Get symbols from vault positions
            for vault in active_vaults:
                if 'positions' in vault:
                    position_symbols = [p['symbol'] for p in vault['positions']]
                    symbols.extend([s for s in position_symbols if s not in symbols])
        except:
            pass
        
        # Priority 3: Default symbols if no others
        if not symbols:
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT"]
        
        return symbols
    
    async def _process_symbol_batch(self, symbols: List[str]):
        """Process a batch of symbols through the full pipeline"""
        tasks = []
        
        for symbol in symbols:
            # Check if it's a My Symbol for priority processing
            is_my_symbol = await self._is_my_symbol(symbol)
            
            if is_my_symbol:
                # Priority processing
                await self.priority_queue.put({
                    'symbol': symbol,
                    'priority': 'HIGH',
                    'timestamp': datetime.now()
                })
            else:
                # Regular processing
                tasks.append(self._process_single_symbol(symbol))
        
        # Process regular symbols in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_symbol(self, symbol: str):
        """Complete processing pipeline for a single symbol"""
        try:
            # Step 1: Collect all data
            signal_data = await self._collect_comprehensive_data(symbol)
            
            # Step 2: Analyze with all agents
            analysis = await self._perform_multi_agent_analysis(symbol, signal_data)
            
            # Step 3: Make trading decision
            decision = await self._make_trading_decision(symbol, analysis)
            
            # Step 4: Execute if qualified
            if decision['should_trade']:
                await self._execute_trade(symbol, decision)
            
            # Update metrics
            if self.session:
                self.session.signals_processed += 1
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    
    async def _collect_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data from all sources"""
        data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'sources': {}
        }
        
        # Get data from all sources in parallel
        tasks = {
            'signal_center': self.signal_center.get_all_signals(symbol),
            'my_symbols': self.my_symbols_orchestrator.get_my_symbol_package(symbol),
            'pattern': self._get_pattern_analysis(symbol),
            'sentiment': self._get_sentiment_analysis(symbol)
        }
        
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        for key, result in zip(tasks.keys(), results):
            if not isinstance(result, Exception):
                data['sources'][key] = result
        
        return data
    
    async def _perform_multi_agent_analysis(self, symbol: str, data: Dict) -> Dict[str, Any]:
        """Perform analysis using all agents"""
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'recommendations': {}
        }
        
        # Get recommendations from each agent
        if data.get('sources', {}).get('signal_center'):
            signal = data['sources']['signal_center']
            
            # Scoring system analysis
            score_analysis = await self.scoring_system.get_comprehensive_score(symbol)
            analysis['recommendations']['scoring'] = score_analysis.to_dict()
            
            # Risk guard assessment
            risk_assessment = await self.risk_guard.check_trade_risk(signal)
            analysis['recommendations']['risk'] = risk_assessment
        
        # Pattern analysis
        if data.get('sources', {}).get('pattern'):
            analysis['recommendations']['pattern'] = data['sources']['pattern']
        
        # Sentiment analysis
        if data.get('sources', {}).get('sentiment'):
            analysis['recommendations']['sentiment'] = data['sources']['sentiment']
        
        return analysis
    
    async def _make_trading_decision(self, symbol: str, analysis: Dict) -> Dict[str, Any]:
        """Make final trading decision based on all analysis"""
        decision = {
            'symbol': symbol,
            'should_trade': False,
            'direction': None,
            'confidence': 0.0,
            'reasons': []
        }
        
        # Check if we have enough positive signals
        positive_signals = 0
        total_confidence = 0.0
        
        # Check scoring recommendation
        if analysis['recommendations'].get('scoring', {}).get('composite_score', 0) > 70:
            positive_signals += 1
            total_confidence += analysis['recommendations']['scoring']['composite_score'] / 100
            decision['reasons'].append('High composite score')
        
        # Check risk assessment
        if analysis['recommendations'].get('risk', {}).get('risk_level') == 'LOW':
            positive_signals += 1
            total_confidence += 0.8
            decision['reasons'].append('Low risk assessment')
        
        # Check pattern confirmation
        if analysis['recommendations'].get('pattern', {}).get('trade_signal') in ['BUY', 'STRONG_BUY', 'SELL', 'STRONG_SELL']:
            positive_signals += 1
            total_confidence += 0.9
            decision['reasons'].append('Pattern confirmation')
        
        # Decision logic
        if positive_signals >= 2:  # Need at least 2 positive signals
            decision['should_trade'] = True
            decision['confidence'] = total_confidence / max(1, positive_signals)
            
            # Determine direction
            if analysis['recommendations'].get('pattern', {}).get('trade_signal') in ['BUY', 'STRONG_BUY']:
                decision['direction'] = 'LONG'
            elif analysis['recommendations'].get('pattern', {}).get('trade_signal') in ['SELL', 'STRONG_SELL']:
                decision['direction'] = 'SHORT'
            else:
                # Use scoring agent direction
                decision['direction'] = 'LONG' if analysis['recommendations'].get('scoring', {}).get('trend') == 'bullish' else 'SHORT'
        
        return decision
    
    async def _execute_trade(self, symbol: str, decision: Dict):
        """Execute trade through Trading Center"""
        try:
            # Send to Trading Center for execution
            qualified = await self.trading_center.process_signal(symbol)
            
            if qualified:
                logger.info(f"🚀 Trade executed for {symbol}: {decision['direction']} with {decision['confidence']:.2f} confidence")
                
                if self.session:
                    self.session.trades_executed += 1
                
                # Send notification
                if telegram_notifier.enabled:
                    await telegram_notifier.send_message(
                        f"🚀 TRADE EXECUTED\n"
                        f"Symbol: {symbol}\n"
                        f"Direction: {decision['direction']}\n"
                        f"Confidence: {decision['confidence']:.2%}\n"
                        f"Reasons: {', '.join(decision['reasons'])}"
                    )
            
        except Exception as e:
            logger.error(f"Failed to execute trade for {symbol}: {e}")
    
    async def _process_priority_queue(self):
        """Process high-priority symbols from queue"""
        while self.state == SystemState.RUNNING:
            try:
                # Get priority item
                item = await self.priority_queue.get()
                
                logger.info(f"🎯 Processing priority symbol: {item['symbol']}")
                
                # Process immediately
                await self._process_single_symbol(item['symbol'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in priority queue: {e}")
                await asyncio.sleep(1)
    
    async def _health_monitor(self):
        """Monitor system health"""
        while self.state == SystemState.RUNNING:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config['health_check_interval'])
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(30)
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        self.health.last_check = datetime.now()
        
        # Check API connections
        self.health.api_status['openai'] = await self._check_openai()
        self.health.api_status['cryptometer'] = await self._check_cryptometer()
        self.health.api_status['kucoin'] = await self._check_kucoin()
        
        # Check module status
        self.health.module_status['trading_center'] = 'active' if self.trading_center else 'inactive'
        self.health.module_status['my_symbols'] = 'active' if self.my_symbols_orchestrator else 'inactive'
        self.health.module_status['signal_center'] = 'active' if self.signal_center else 'inactive'
        
        # Log health status
        healthy_apis = sum(1 for v in self.health.api_status.values() if v)
        total_apis = len(self.health.api_status)
        
        if healthy_apis == total_apis:
            logger.info(f"✅ System Health: EXCELLENT ({healthy_apis}/{total_apis} APIs)")
        elif healthy_apis > 0:
            logger.warning(f"⚠️ System Health: DEGRADED ({healthy_apis}/{total_apis} APIs)")
        else:
            logger.error(f"❌ System Health: CRITICAL (0/{total_apis} APIs)")
    
    async def _performance_tracker(self):
        """Track and report performance metrics"""
        while self.state == SystemState.RUNNING:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                if self.session:
                    runtime = (datetime.now() - self.session.start_time).total_seconds() / 60
                    
                    report = f"""
📊 PERFORMANCE REPORT
━━━━━━━━━━━━━━━━━━
Session: {self.session.session_id}
Runtime: {runtime:.1f} minutes
Symbols: {len(self.session.symbols_monitored)}
Signals: {self.session.signals_processed}
Trades: {self.session.trades_executed}
"""
                    logger.info(report)
                    
                    if telegram_notifier.enabled:
                        await telegram_notifier.send_message(report)
                
            except Exception as e:
                logger.error(f"Error in performance tracker: {e}")
    
    def _setup_event_listeners(self):
        """Setup event bus listeners"""
        
        async def on_signal_processed(event: Event):
            logger.debug(f"Signal processed: {event.data}")
        
        async def on_trade_executed(event: Event):
            logger.info(f"🎯 Trade executed: {event.data}")
            if self.session:
                self.session.trades_executed += 1
        
        async def on_risk_alert(event: Event):
            logger.warning(f"⚠️ Risk alert: {event.data}")
            self.health.warning_count += 1
        
        # Subscribe handlers
        self.event_bus.subscribe(EventType.SIGNAL_PROCESSED, on_signal_processed)
        self.event_bus.subscribe(EventType.TRADE_EXECUTED, on_trade_executed)
        # For RISK_ALERT, use appropriate event type if exists
        # self.event_bus.subscribe(EventType.RISK_ALERT, on_risk_alert)
    
    async def _is_my_symbol(self, symbol: str) -> bool:
        """Check if symbol is in My Symbols database"""
        try:
            package = await self.my_symbols_orchestrator.get_my_symbol_package(symbol)
            return package is not None
        except:
            return False
    
    async def _get_pattern_analysis(self, symbol: str):
        """Get pattern analysis for symbol"""
        try:
            # Mock implementation - replace with real data
            import pandas as pd
            price_data = pd.DataFrame({
                'close': [100, 101, 102, 101, 103]
            })
            
            return await self.pattern_agent.analyze(
                symbol=symbol,
                price_data=price_data,
                technical_indicators={},
                risk_metrics={}
            )
        except:
            return None
    
    async def _get_sentiment_analysis(self, symbol: str):
        """Get sentiment analysis for symbol"""
        try:
            if self.sentiment_agent:
                return await self.sentiment_agent.analyze_sentiment(symbol)
        except:
            return None
    
    async def _check_openai(self) -> bool:
        """Check OpenAI API status"""
        # Implementation would check actual API
        return True
    
    async def _check_cryptometer(self) -> bool:
        """Check Cryptometer API status"""
        # Implementation would check actual API
        return True
    
    async def _check_kucoin(self) -> bool:
        """Check KuCoin API status"""
        # Implementation would check actual API
        return True
    
    async def shutdown(self):
        """Gracefully shutdown the orchestration system"""
        logger.info("🛑 Shutting down Master Orchestration Agent...")
        
        self.state = SystemState.SHUTDOWN
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Final report
        if self.session:
            runtime = (datetime.now() - self.session.start_time).total_seconds() / 60
            
            final_report = f"""
🏁 SESSION COMPLETE
━━━━━━━━━━━━━━━━━
Session: {self.session.session_id}
Total Runtime: {runtime:.1f} minutes
Signals Processed: {self.session.signals_processed}
Trades Executed: {self.session.trades_executed}
Symbols Monitored: {len(self.session.symbols_monitored)}
"""
            logger.info(final_report)
            
            if telegram_notifier.enabled:
                await telegram_notifier.send_message(final_report)
        
        logger.info("✅ Master Orchestration Agent shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            'state': self.state.value,
            'mode': self.mode.value,
            'health': {
                'apis': self.health.api_status,
                'modules': self.health.module_status,
                'errors': self.health.error_count,
                'warnings': self.health.warning_count,
                'last_check': self.health.last_check.isoformat()
            }
        }
        
        if self.session:
            runtime = (datetime.now() - self.session.start_time).total_seconds() / 60
            status['session'] = {
                'id': self.session.session_id,
                'runtime_minutes': runtime,
                'signals_processed': self.session.signals_processed,
                'trades_executed': self.session.trades_executed,
                'symbols_monitored': list(self.session.symbols_monitored)
            }
        
        return status

# Global instance
master_orchestrator: Optional[MasterOrchestrationAgent] = None

async def get_master_orchestrator(mode: TradingMode = TradingMode.PAPER) -> MasterOrchestrationAgent:
    """Get or create master orchestrator instance"""
    global master_orchestrator
    if master_orchestrator is None:
        master_orchestrator = MasterOrchestrationAgent(mode)
        await master_orchestrator.initialize()
    return master_orchestrator

__all__ = ['MasterOrchestrationAgent', 'get_master_orchestrator', 'TradingMode', 'SystemState']