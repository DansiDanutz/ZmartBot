#!/usr/bin/env python3
"""
Orchestration-Signal Center Integration Service
Bridges the Unified Signal Center with the Orchestration Agent
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from src.services.unified_signal_center import unified_signal_center
from src.agents.orchestration.orchestration_agent import OrchestrationAgent
from src.utils.event_bus import EventBus, EventType, Event

logger = logging.getLogger(__name__)

class SignalIntegrationService:
    """
    Service that integrates Unified Signal Center with Orchestration Agent
    Polls Signal Center and feeds signals to Orchestration Agent via Event Bus
    """
    
    def __init__(self, orchestration_agent: Optional[OrchestrationAgent] = None):
        """
        Initialize the integration service
        
        Args:
            orchestration_agent: Optional orchestration agent instance
        """
        self.signal_center = unified_signal_center
        self.orchestration_agent = orchestration_agent
        self.event_bus = EventBus()
        
        # Configuration
        self.polling_interval = 30  # seconds
        self.min_score_threshold = 65  # Minimum score to generate signal
        self.min_confidence_threshold = 60  # Minimum confidence
        
        # Tracking
        self.processed_signals = set()
        self.active = False
        self._polling_task = None
        
        # Symbols to monitor
        self.monitored_symbols = ["BTC", "ETH", "SOL", "BNB", "XRP"]
        
        logger.info("Signal Integration Service initialized")
    
    async def start(self):
        """Start the signal integration service"""
        if self.active:
            logger.warning("Signal Integration Service already running")
            return
        
        self.active = True
        
        # Start event bus if not already started
        if not self.event_bus.is_running:
            await self.event_bus.start()
        
        # Start polling task
        self._polling_task = asyncio.create_task(self._signal_polling_loop())
        
        logger.info("Signal Integration Service started")
    
    async def stop(self):
        """Stop the signal integration service"""
        self.active = False
        
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Signal Integration Service stopped")
    
    async def _signal_polling_loop(self):
        """Main polling loop that checks for new signals"""
        while self.active:
            try:
                # Check signals for all monitored symbols
                for symbol in self.monitored_symbols:
                    await self._check_and_process_symbol(symbol)
                
                # Wait before next poll
                await asyncio.sleep(self.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in signal polling loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_and_process_symbol(self, symbol: str):
        """
        Check signals for a symbol and process if conditions met
        
        Args:
            symbol: Trading symbol
        """
        try:
            # Get unified signals from Signal Center
            signal = await self.signal_center.get_all_signals(symbol)
            
            # Check if signal meets thresholds
            if signal.total_score < self.min_score_threshold:
                return
            
            if signal.confidence < self.min_confidence_threshold:
                return
            
            # Create unique signal ID
            signal_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if already processed
            if signal_id in self.processed_signals:
                return
            
            # Convert to orchestration signal format
            orchestration_signal = self._convert_to_orchestration_format(signal)
            
            # Send via Event Bus
            await self._emit_signal_event(orchestration_signal)
            
            # If orchestration agent is directly available, also process directly
            if self.orchestration_agent:
                await self.orchestration_agent.process_signal(orchestration_signal)
            
            # Mark as processed
            self.processed_signals.add(signal_id)
            
            # Keep only recent signals (last 100)
            if len(self.processed_signals) > 100:
                self.processed_signals = set(list(self.processed_signals)[-100:])
            
            logger.info(f"Signal processed for {symbol}: Score={signal.total_score:.2f}, "
                       f"Direction={signal.direction}, Confidence={signal.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Error processing symbol {symbol}: {e}")
    
    def _convert_to_orchestration_format(self, signal) -> Dict[str, Any]:
        """
        Convert Unified Signal to Orchestration Agent format
        
        Args:
            signal: Unified signal from Signal Center
            
        Returns:
            Signal in orchestration format
        """
        # Determine action
        if signal.direction.upper() in ["BUY", "STRONG_BUY"]:
            action = "BUY"
            side = "long"
        elif signal.direction.upper() in ["SELL", "STRONG_SELL"]:
            action = "SELL"
            side = "short"
        else:
            action = "HOLD"
            side = "neutral"
        
        return {
            "signal_id": f"USC_{signal.symbol}_{int(datetime.now().timestamp())}",
            "symbol": signal.symbol,
            "action": action,
            "side": side,
            "score": signal.total_score,
            "confidence": signal.confidence,
            "risk_level": signal.risk_level,
            "recommendation": signal.recommendation,
            "source": "unified_signal_center",
            "components": signal.components,
            "timestamp": signal.timestamp.isoformat(),
            "metadata": {
                "direction": signal.direction,
                "signals_count": len(signal.signals),
                "component_scores": signal.components
            }
        }
    
    async def _emit_signal_event(self, signal_data: Dict[str, Any]):
        """
        Emit signal event via Event Bus
        
        Args:
            signal_data: Signal data to emit
        """
        event = Event(
            type=EventType.SIGNAL_GENERATED,
            data=signal_data
        )
        
        await self.event_bus.emit(event)
        
        logger.debug(f"Signal event emitted: {signal_data['signal_id']}")
    
    async def force_check(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Force immediate check and processing of a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Signal data if generated, None otherwise
        """
        try:
            # Get signals
            signal = await self.signal_center.get_all_signals(symbol.upper())
            
            # Convert to orchestration format
            orchestration_signal = self._convert_to_orchestration_format(signal)
            
            # Always return the signal for force check (ignore thresholds)
            return {
                "original_signal": signal.to_dict(),
                "orchestration_signal": orchestration_signal,
                "would_trigger": (
                    signal.total_score >= self.min_score_threshold and
                    signal.confidence >= self.min_confidence_threshold
                )
            }
            
        except Exception as e:
            logger.error(f"Error in force check for {symbol}: {e}")
            return None
    
    def update_thresholds(self, score_threshold: Optional[float] = None, 
                         confidence_threshold: Optional[float] = None):
        """
        Update triggering thresholds
        
        Args:
            score_threshold: New minimum score threshold
            confidence_threshold: New minimum confidence threshold
        """
        if score_threshold is not None:
            self.min_score_threshold = score_threshold
            logger.info(f"Score threshold updated to {score_threshold}")
        
        if confidence_threshold is not None:
            self.min_confidence_threshold = confidence_threshold
            logger.info(f"Confidence threshold updated to {confidence_threshold}")
    
    def add_monitored_symbol(self, symbol: str):
        """Add a symbol to monitoring list"""
        if symbol.upper() not in self.monitored_symbols:
            self.monitored_symbols.append(symbol.upper())
            logger.info(f"Added {symbol} to monitored symbols")
    
    def remove_monitored_symbol(self, symbol: str):
        """Remove a symbol from monitoring list"""
        if symbol.upper() in self.monitored_symbols:
            self.monitored_symbols.remove(symbol.upper())
            logger.info(f"Removed {symbol} from monitored symbols")
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration service status"""
        return {
            "active": self.active,
            "polling_interval": self.polling_interval,
            "min_score_threshold": self.min_score_threshold,
            "min_confidence_threshold": self.min_confidence_threshold,
            "monitored_symbols": self.monitored_symbols,
            "processed_signals_count": len(self.processed_signals),
            "orchestration_connected": self.orchestration_agent is not None
        }

# Global instance
signal_integration_service = SignalIntegrationService()