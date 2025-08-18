#!/usr/bin/env python3
"""
🎯 ZmartBot Trading Center
Receives signals from Signal Center and executes trades when win rate > 80%
Manages vault allocation and position limits
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

from src.services.unified_signal_center import UnifiedSignalCenter, AggregatedSignal
from src.services.vault_management_system import VaultManagementSystem, VaultType
from src.services.vault_position_manager import VaultPositionManager
# AI Win Rate Predictor temporarily disabled - using unified scoring system
# from src.agents.scoring.ai_win_rate_predictor import AIWinRatePredictor
from src.agents.trading.unified_trading_agent import UnifiedTradingAgent, TradingDecision, TradeAction, PositionType
from src.agents.pattern_analysis.master_pattern_agent import MasterPatternAgent
from src.services.my_symbols_service_v2 import MySymbolsServiceV2
from src.services.my_symbols_orchestrator import MySymbolsOrchestrator
from src.utils.event_bus import EventBus, Event, EventType

logger = logging.getLogger(__name__)

# Configuration
WIN_RATE_THRESHOLD = 80.0  # 80% win rate required to execute trade
MAX_TRADES_PER_VAULT = 2   # Maximum concurrent trades per vault

class SignalStatus(Enum):
    """Signal processing status"""
    PENDING = "pending"
    QUALIFIED = "qualified"      # Meets win rate threshold
    REJECTED = "rejected"        # Below threshold
    EXECUTED = "executed"        # Trade placed
    FAILED = "failed"           # Execution failed

@dataclass
class QualifiedSignal:
    """Signal that meets win rate criteria"""
    signal: AggregatedSignal
    win_rate_long: float
    win_rate_short: float
    selected_direction: str  # 'long' or 'short'
    selected_win_rate: float
    confidence: float
    has_pattern: bool = False  # Pattern validation flag
    pattern_win_rate: Optional[float] = None  # Pattern-based win rate
    pattern_confidence: Optional[float] = None  # Pattern confidence
    pattern_type: Optional[str] = None  # Type of pattern detected
    is_rare_event: bool = False  # Flag for rare/unusual events
    vault_id: Optional[str] = None
    status: SignalStatus = SignalStatus.PENDING
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class TradingCenter:
    """
    Central trading coordination system
    - Receives signals from Signal Center
    - Filters by 80% win rate threshold
    - Allocates to available vaults
    - Manages position limits per vault
    """
    
    def __init__(self):
        """Initialize Trading Center"""
        # Core components
        self.signal_center = UnifiedSignalCenter()
        self.vault_manager = VaultManagementSystem()
        self.position_manager = VaultPositionManager()
        # self.win_rate_predictor = AIWinRatePredictor()  # Temporarily disabled - will be re-enabled when fixed
        self.master_pattern_agent = MasterPatternAgent()  # Pattern validation
        self.my_symbols_service = MySymbolsServiceV2()  # My Symbol service
        self.my_symbols_orchestrator = MySymbolsOrchestrator()  # Complete My Symbol integration
        self.trading_agent = UnifiedTradingAgent()
        self.event_bus = EventBus()
        
        # Signal tracking
        self.qualified_signals: List[QualifiedSignal] = []
        self.signal_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.total_signals_received = 0
        self.signals_qualified = 0
        self.trades_executed = 0
        self.trades_rejected = 0
        
        # Configuration
        self.win_rate_threshold = WIN_RATE_THRESHOLD
        self.max_trades_per_vault = MAX_TRADES_PER_VAULT
        
        logger.info(f"🎯 Trading Center initialized - Win Rate Threshold: {self.win_rate_threshold}%")
    
    async def process_signal(self, symbol: str) -> Optional[QualifiedSignal]:
        """
        Process signal from Signal Center through win rate filter
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            QualifiedSignal if meets threshold, None otherwise
        """
        try:
            self.total_signals_received += 1
            
            # Step 0: Get comprehensive My Symbols data package
            my_symbol_package = await self.my_symbols_orchestrator.get_my_symbol_package(symbol)
            is_my_symbol = my_symbol_package is not None
            symbol_score = my_symbol_package.composite_score if my_symbol_package else None
            
            # Step 1: Get aggregated signal from Signal Center (enhanced with My Symbols data)
            signal = await self.signal_center.get_all_signals(symbol)
            logger.info(f"📡 Received signal for {symbol}: Score={signal.total_score:.2f}, Direction={signal.direction}")
            
            # My Symbols get priority logging with comprehensive insights
            if is_my_symbol:
                logger.info(f"🎯 HIGH PRIORITY My Symbol: {symbol}")
                logger.info(f"   • Composite Score: {symbol_score:.2f} (Rank #{my_symbol_package.rank})")
                logger.info(f"   • Priority Level: {my_symbol_package.priority.value}")
                logger.info(f"   • Rare Events: {len(my_symbol_package.rare_events_detected)}")
                logger.info(f"   • High-Value Opportunities: {len(my_symbol_package.high_value_opportunities)}")
                
                # Log cross-module insights
                if my_symbol_package.high_value_opportunities:
                    logger.info(f"   💎 Opportunities: {', '.join(my_symbol_package.high_value_opportunities)}")
            
            # Step 2: Get AI win rate predictions
            win_rate_data = await self._get_win_rate_predictions(symbol, signal)
            
            # Step 3: Check if meets threshold (adjusted for My Symbols)
            qualified = self._check_win_rate_threshold(signal, win_rate_data, is_my_symbol)
            
            # Step 4: Validate with Master Pattern Agent if qualified
            if qualified:
                pattern_validation = await self._validate_with_patterns(symbol, signal, qualified, is_my_symbol, symbol_score)
                
                # Update qualified signal with pattern data
                qualified.has_pattern = pattern_validation['has_pattern']
                qualified.pattern_win_rate = pattern_validation.get('pattern_win_rate')
                qualified.pattern_confidence = pattern_validation.get('pattern_confidence')
                qualified.pattern_type = pattern_validation.get('pattern_type')
                qualified.is_rare_event = pattern_validation.get('is_rare_event', False)
                
                # Log pattern validation results
                if qualified.has_pattern:
                    logger.info(f"✅ Pattern CONFIRMED for {symbol}: {qualified.pattern_type} with {qualified.pattern_win_rate:.2f}% win rate")
                    # Boost confidence if pattern confirms signal
                    qualified.confidence = min(qualified.confidence * 1.2, 1.0)
                    
                    # Extra boost for rare events with patterns - these are high-value opportunities!
                    if qualified.is_rare_event:
                        logger.info(f"🎯 RARE EVENT with PATTERN for {symbol} - Premium trading opportunity!")
                        # Rare events with patterns are the best opportunities - boost confidence significantly
                        qualified.confidence = min(qualified.confidence * 1.3, 1.0)
                        
                elif qualified.is_rare_event:
                    logger.info(f"🎯 RARE EVENT detected for {symbol} - High-value trading opportunity!")
                    # Rare events are valuable - they have few data points but higher win rates
                    # Boost confidence for rare events as they represent unique opportunities
                    qualified.confidence = min(qualified.confidence * 1.15, 1.0)
                else:
                    logger.info(f"📊 Standard signal for {symbol} - Common market pattern")
            
            if qualified:
                self.signals_qualified += 1
                logger.info(f"✅ {symbol} QUALIFIED - Win Rate: {qualified.selected_win_rate:.2f}% > {self.win_rate_threshold}%")
                
                # Step 4: Find available vault
                vault = await self._find_available_vault()
                
                if vault:
                    qualified.vault_id = vault['id']
                    qualified.status = SignalStatus.QUALIFIED
                    
                    # Step 5: Execute trade
                    success = await self._execute_trade(qualified, vault)
                    
                    if success:
                        qualified.status = SignalStatus.EXECUTED
                        self.trades_executed += 1
                        logger.info(f"🚀 Trade EXECUTED for {symbol} in Vault {vault['id']}")
                    else:
                        qualified.status = SignalStatus.FAILED
                        logger.error(f"❌ Trade execution failed for {symbol}")
                else:
                    logger.warning(f"⚠️ No available vault for {symbol} - all vaults at max capacity")
                    self.trades_rejected += 1
                
                # Store qualified signal
                self.qualified_signals.append(qualified)
                
                # Emit event
                await self.event_bus.emit(Event(
                    type=EventType.SIGNAL_PROCESSED,
                    data={
                        'symbol': symbol,
                        'win_rate': qualified.selected_win_rate,
                        'direction': qualified.selected_direction,
                        'vault_id': qualified.vault_id
                    }
                ))
                
                return qualified
            else:
                logger.info(f"❌ {symbol} REJECTED - Win rates below {self.win_rate_threshold}% threshold")
                self.trades_rejected += 1
                
                # Emit rejection event
                await self.event_bus.emit(Event(
                    type=EventType.SIGNAL_REJECTED,
                    data={
                        'symbol': symbol,
                        'win_rate_long': win_rate_data.get('long', 0),
                        'win_rate_short': win_rate_data.get('short', 0),
                        'threshold': self.win_rate_threshold
                    }
                ))
                
                return None
                
        except Exception as e:
            logger.error(f"Error processing signal for {symbol}: {e}")
            return None
    
    async def _get_win_rate_predictions(self, symbol: str, signal: AggregatedSignal) -> Dict[str, float]:
        """
        Get AI win rate predictions for both long and short positions
        
        Args:
            symbol: Trading symbol
            signal: Aggregated signal data
            
        Returns:
            Dict with 'long' and 'short' win rate predictions
        """
        try:
            # Temporarily use mock win rate predictions since AIWinRatePredictor is disabled
            # TODO: Re-enable when AIWinRatePredictor is fixed
            mock_win_rates = {
                'long': 75.0,  # Mock 75% win rate for long
                'short': 70.0,  # Mock 70% win rate for short
                'confidence': 0.8  # Mock 80% confidence
            }
            
            logger.debug(f"Mock win rate predictions for {symbol}: Long={mock_win_rates['long']:.2f}%, Short={mock_win_rates['short']:.2f}%")
            
            return mock_win_rates
            
        except Exception as e:
            logger.error(f"Error getting win rate predictions: {e}")
            return {'long': 0, 'short': 0, 'confidence': 0}
    
    def _check_win_rate_threshold(self, signal: AggregatedSignal, win_rate_data: Dict[str, float], is_my_symbol: bool = False) -> Optional[QualifiedSignal]:
        """
        Check if signal meets win rate threshold
        
        Args:
            signal: Aggregated signal
            win_rate_data: Win rate predictions
            is_my_symbol: Whether symbol is in My Symbols database
            
        Returns:
            QualifiedSignal if meets threshold, None otherwise
        """
        long_win_rate = win_rate_data.get('long', 0)
        short_win_rate = win_rate_data.get('short', 0)
        confidence = win_rate_data.get('confidence', 0)
        
        # My Symbols get lower threshold (more opportunities)
        effective_threshold = self.win_rate_threshold
        if is_my_symbol:
            effective_threshold *= 0.8  # 20% lower threshold for My Symbols
            logger.info(f"🎯 My Symbol {signal.symbol}: Using reduced threshold {effective_threshold:.1f}% vs {self.win_rate_threshold:.1f}%")
        
        # Check if either direction meets threshold
        if long_win_rate >= effective_threshold:
            return QualifiedSignal(
                signal=signal,
                win_rate_long=long_win_rate,
                win_rate_short=short_win_rate,
                selected_direction='long',
                selected_win_rate=long_win_rate,
                confidence=confidence
            )
        elif short_win_rate >= effective_threshold:
            return QualifiedSignal(
                signal=signal,
                win_rate_long=long_win_rate,
                win_rate_short=short_win_rate,
                selected_direction='short',
                selected_win_rate=short_win_rate,
                confidence=confidence
            )
        
        return None
    
    async def _is_my_symbol(self, symbol: str) -> bool:
        """Check if symbol is in My Symbols database"""
        try:
            tradeable_symbols = await self.my_symbols_service.get_tradeable_symbols()
            return symbol in tradeable_symbols
        except Exception as e:
            logger.error(f"Error checking if {symbol} is My Symbol: {e}")
            return False
    
    async def _get_my_symbol_score(self, symbol: str) -> float:
        """Get My Symbol composite score"""
        try:
            should_trade, reason = await self.my_symbols_service.should_trade_symbol(symbol)
            if should_trade:
                # Try to get the actual score from symbol_scores
                symbol_scores = await self.my_symbols_service.get_symbol_scores(100)
                for score_data in symbol_scores:
                    if score_data.symbol == symbol:
                        return score_data.composite_score
                return 0.8  # Default high score if in tradeable list
            return 0.0
        except Exception as e:
            logger.error(f"Error getting My Symbol score for {symbol}: {e}")
            return 0.0
    
    async def _validate_with_patterns(
        self, 
        symbol: str, 
        signal: AggregatedSignal,
        qualified_signal: QualifiedSignal,
        is_my_symbol: bool = False,
        my_symbol_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validate signal with Master Pattern Agent to check for real patterns
        
        Args:
            symbol: Trading symbol
            signal: Aggregated signal data
            qualified_signal: Initially qualified signal
            is_my_symbol: Whether symbol is in My Symbols database
            my_symbol_score: My Symbol composite score if available
            
        Returns:
            Pattern validation results
        """
        try:
            # Prepare data for pattern analysis
            # In production, fetch real price and volume data
            import pandas as pd
            
            # Mock price data for development (replace with real data fetch)
            price_data = pd.DataFrame({
                'open': [100, 102, 101, 103, 104],
                'high': [103, 104, 103, 105, 106],
                'low': [99, 101, 100, 102, 103],
                'close': [102, 101, 103, 104, 105],
                'volume': [1000, 1200, 900, 1500, 1100]
            })
            
            # Add My Symbols context for pattern analysis
            analysis_metadata = {
                'is_my_symbol': is_my_symbol,
                'my_symbol_score': my_symbol_score,
                'symbol_priority': 'high' if is_my_symbol else 'normal'
            }
            
            # Get pattern analysis from Master Pattern Agent
            # Handle missing metadata attribute safely
            metadata = getattr(signal, 'metadata', {})
            
            # Enhance metadata with My Symbols context
            enhanced_metadata = {
                **metadata.get('technical', {}),
                **analysis_metadata  # Add My Symbols context
            }
            
            pattern_analysis = await self.master_pattern_agent.analyze(
                symbol=symbol,
                price_data=price_data,
                technical_indicators=enhanced_metadata,
                risk_metrics=metadata.get('risk', {})
            )
            
            # Extract pattern validation results
            has_pattern = len(pattern_analysis.detected_patterns) > 0
            is_rare_event = False
            pattern_win_rate = None
            pattern_confidence = None
            pattern_type = None
            
            if has_pattern:
                # Get the strongest pattern
                strongest_pattern = max(
                    pattern_analysis.detected_patterns,
                    key=lambda p: p.confidence * p.historical_win_rate
                )
                
                pattern_win_rate = strongest_pattern.historical_win_rate
                pattern_confidence = strongest_pattern.confidence
                pattern_type = strongest_pattern.pattern_name
                
                # Check if it's a rare event (low occurrence frequency)
                if strongest_pattern.occurrence_frequency < 0.05:  # Less than 5% occurrence
                    is_rare_event = True
                    logger.info(f"🎯 Rare pattern detected: {pattern_type} with {strongest_pattern.occurrence_frequency:.2%} frequency - High-value opportunity!")
                
                # Additional validation: Check if pattern aligns with signal direction
                pattern_direction = strongest_pattern.direction
                signal_direction = qualified_signal.selected_direction
                
                if pattern_direction != signal_direction:
                    logger.warning(f"Pattern direction ({pattern_direction}) conflicts with signal direction ({signal_direction})")
                    # Reduce confidence for conflicting signals
                    pattern_confidence *= 0.5
            else:
                # No strong pattern detected
                logger.info(f"No significant pattern detected for {symbol}")
                
                # Check if signal score is unusually high without patterns (potential rare event)
                # Lower threshold for My Symbols (more sensitive to rare events)
                rare_event_threshold = 75 if is_my_symbol else 85
                if signal.total_score > rare_event_threshold and not has_pattern:
                    is_rare_event = True
                    priority_msg = "HIGH PRIORITY My Symbol" if is_my_symbol else "market event"
                    logger.info(f"🎯 High score ({signal.total_score}) without pattern support - potential rare {priority_msg}!")
                
                # Additional rare event detection for My Symbols with high scores
                if is_my_symbol and my_symbol_score and my_symbol_score > 0.9 and signal.total_score > 70:
                    is_rare_event = True
                    logger.info(f"🎯 My Symbol {symbol} with exceptional score ({my_symbol_score:.2f}) - rare opportunity!")
            
            return {
                'has_pattern': has_pattern,
                'pattern_win_rate': pattern_win_rate,
                'pattern_confidence': pattern_confidence,
                'pattern_type': pattern_type,
                'is_rare_event': is_rare_event,
                'pattern_count': len(pattern_analysis.detected_patterns) if pattern_analysis else 0,
                'pattern_clusters': len(pattern_analysis.pattern_clusters) if pattern_analysis else 0,
                'trade_signal': pattern_analysis.trade_signal if pattern_analysis else 'HOLD'
            }
            
        except Exception as e:
            logger.error(f"Error validating patterns for {symbol}: {e}")
            # Return default values on error
            return {
                'has_pattern': False,
                'pattern_win_rate': None,
                'pattern_confidence': None,
                'pattern_type': None,
                'is_rare_event': False,
                'pattern_count': 0,
                'pattern_clusters': 0,
                'recommendation': 'hold'
            }
    
    async def _find_available_vault(self) -> Optional[Dict[str, Any]]:
        """
        Find a vault with available capacity (< 2 concurrent trades)
        
        Returns:
            Vault info if available, None otherwise
        """
        try:
            # Get all active vaults
            active_vaults = await self.vault_manager.get_active_vaults()
            
            for vault in active_vaults:
                vault_id = vault['id']
                
                # Get current positions for this vault
                positions = await self.position_manager.get_vault_positions(vault_id)
                active_positions = [p for p in positions if p.get('status') == 'open']
                
                # Check if vault has capacity
                if len(active_positions) < self.max_trades_per_vault:
                    logger.debug(f"Found available vault {vault_id}: {len(active_positions)}/{self.max_trades_per_vault} positions")
                    return vault
            
            # No vault with capacity found
            return None
            
        except Exception as e:
            logger.error(f"Error finding available vault: {e}")
            return None
    
    async def _execute_trade(self, qualified_signal: QualifiedSignal, vault: Dict[str, Any]) -> bool:
        """
        Execute trade for qualified signal
        
        Args:
            qualified_signal: Signal that passed win rate threshold
            vault: Vault to execute trade in
            
        Returns:
            True if trade executed successfully
        """
        try:
            # Create trading decision
            decision = TradingDecision(
                symbol=qualified_signal.signal.symbol,
                action=TradeAction.BUY if qualified_signal.selected_direction == 'long' else TradeAction.SELL,
                position_type=PositionType.FUTURES_LONG if qualified_signal.selected_direction == 'long' else PositionType.FUTURES_SHORT,
                size=vault.get('position_size', 1000),  # Use vault's position size
                entry_price=0,  # Will be set by market
                stop_loss=0,    # Will be calculated by risk management
                take_profit=0,  # Will be calculated by risk management
                confidence=qualified_signal.confidence,
                score=qualified_signal.signal.total_score,
                risk_reward_ratio=2.0,  # Default 1:2 risk/reward
                metadata={
                    'vault_id': vault['id'],
                    'win_rate': qualified_signal.selected_win_rate,
                    'signal_source': 'trading_center',
                    'has_pattern': qualified_signal.has_pattern,
                    'pattern_type': qualified_signal.pattern_type,
                    'pattern_win_rate': qualified_signal.pattern_win_rate,
                    'pattern_confidence': qualified_signal.pattern_confidence,
                    'is_rare_event': qualified_signal.is_rare_event
                }
            )
            
            # Execute through trading agent
            result = await self.trading_agent.execute_trade(decision)
            
            if result and result.get('success'):
                # Emit trade execution event
                await self.event_bus.emit(Event(
                    type=EventType.TRADE_EXECUTED,
                    data={
                        'symbol': qualified_signal.signal.symbol,
                        'vault_id': vault['id'],
                        'direction': qualified_signal.selected_direction,
                        'win_rate': qualified_signal.selected_win_rate,
                        'position_id': result.get('position_id')
                    }
                ))
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    async def process_my_symbols_batch(self) -> List[QualifiedSignal]:
        """
        Process all My Symbols in batch with priority-based processing
        
        Returns:
            List of qualified signals from My Symbols
        """
        try:
            logger.info("🎯 Processing My Symbols batch with orchestrator integration")
            
            # Get all My Symbols with their packages
            tradeable_symbols = await self.my_symbols_service.get_tradeable_symbols()
            logger.info(f"📊 Processing {len(tradeable_symbols)} tradeable My Symbols")
            
            # Process symbols with priority-based parallel execution
            tasks = []
            for symbol in tradeable_symbols:
                tasks.append(self.process_signal(symbol))
            
            # Execute all in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful qualifications
            qualified_signals = []
            for result in results:
                if isinstance(result, QualifiedSignal):
                    qualified_signals.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in batch processing: {result}")
            
            logger.info(f"✅ My Symbols batch complete: {len(qualified_signals)}/{len(tradeable_symbols)} qualified")
            
            # Get high-value opportunities from orchestrator
            opportunities = await self.my_symbols_orchestrator.get_high_value_opportunities()
            rare_events = await self.my_symbols_orchestrator.get_rare_events()
            
            if opportunities:
                logger.info(f"💎 High-value opportunities detected: {len(opportunities)} symbols")
            if rare_events:
                logger.info(f"⚡ Rare events detected: {len(rare_events)} symbols")
            
            return qualified_signals
            
        except Exception as e:
            logger.error(f"❌ Error in My Symbols batch processing: {e}")
            return []
    
    async def monitor_signals(self, symbols: List[str], interval: int = 60):
        """
        Continuously monitor signals for multiple symbols
        
        Args:
            symbols: List of symbols to monitor
            interval: Check interval in seconds
        """
        logger.info(f"🔍 Starting signal monitoring for {len(symbols)} symbols")
        
        while True:
            try:
                # Process each symbol
                tasks = []
                for symbol in symbols:
                    tasks.append(self.process_signal(symbol))
                
                # Process all symbols in parallel
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log results
                qualified_count = sum(1 for r in results if r and isinstance(r, QualifiedSignal))
                logger.info(f"📊 Signal scan complete: {qualified_count}/{len(symbols)} qualified")
                
                # Wait before next scan
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in signal monitoring: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def monitor_my_symbols_continuous(self, interval: int = 60):
        """
        Continuously monitor My Symbols with orchestrator integration
        
        Args:
            interval: Base check interval in seconds (priority symbols checked more frequently)
        """
        logger.info("🚀 Starting continuous My Symbols monitoring with orchestrator")
        
        # Initialize the orchestrator
        await self.my_symbols_orchestrator.initialize_my_symbols_integration()
        
        while True:
            try:
                # Process My Symbols batch
                qualified_signals = await self.process_my_symbols_batch()
                
                # Log statistics
                stats = self.my_symbols_orchestrator.get_statistics()
                logger.info(f"📈 My Symbols Status: {stats['symbols_with_opportunities']}/{stats['total_symbols']} with opportunities")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in continuous My Symbols monitoring: {e}")
                await asyncio.sleep(30)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Trading Center statistics with pattern analysis"""
        qualified_rate = (self.signals_qualified / self.total_signals_received * 100) if self.total_signals_received > 0 else 0
        execution_rate = (self.trades_executed / self.signals_qualified * 100) if self.signals_qualified > 0 else 0
        
        # Calculate pattern statistics
        pattern_confirmed_signals = [s for s in self.qualified_signals if s.has_pattern]
        rare_event_signals = [s for s in self.qualified_signals if s.is_rare_event]
        pattern_confirmation_rate = (len(pattern_confirmed_signals) / len(self.qualified_signals) * 100) if self.qualified_signals else 0
        
        # Calculate average pattern win rate for confirmed patterns
        avg_pattern_win_rate = 0
        if pattern_confirmed_signals:
            pattern_win_rates = [s.pattern_win_rate for s in pattern_confirmed_signals if s.pattern_win_rate]
            avg_pattern_win_rate = sum(pattern_win_rates) / len(pattern_win_rates) if pattern_win_rates else 0
        
        return {
            'total_signals_received': self.total_signals_received,
            'signals_qualified': self.signals_qualified,
            'trades_executed': self.trades_executed,
            'trades_rejected': self.trades_rejected,
            'qualification_rate': round(qualified_rate, 2),
            'execution_rate': round(execution_rate, 2),
            'win_rate_threshold': self.win_rate_threshold,
            'max_trades_per_vault': self.max_trades_per_vault,
            'active_qualified_signals': len([s for s in self.qualified_signals if s.status == SignalStatus.QUALIFIED]),
            'total_qualified_signals': len(self.qualified_signals),
            # Pattern statistics
            'pattern_confirmed_count': len(pattern_confirmed_signals),
            'pattern_confirmation_rate': round(pattern_confirmation_rate, 2),
            'average_pattern_win_rate': round(avg_pattern_win_rate, 2),
            'rare_event_count': len(rare_event_signals),
            'pattern_types_detected': list(set([s.pattern_type for s in pattern_confirmed_signals if s.pattern_type]))
        }

# Global instance
trading_center = TradingCenter()

# Export for use in other modules
__all__ = ['TradingCenter', 'trading_center', 'QualifiedSignal', 'SignalStatus']