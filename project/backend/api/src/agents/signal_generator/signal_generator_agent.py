#!/usr/bin/env python3
"""
Signal Generator Agent
Multi-source signal generation and aggregation system for trading decisions
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from src.services.signal_center import SignalCenterService, SignalDirection, SignalStrength

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Types of trading signals"""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    VOLUME = "volume"
    MOMENTUM = "momentum"

@dataclass
class SignalData:
    """Signal data structure"""
    symbol: str
    signal_type: SignalType
    direction: SignalDirection
    strength: SignalStrength
    confidence: float
    price: float
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]

class SignalGeneratorAgent:
    """
    Signal Generator Agent for multi-source signal generation and aggregation
    
    This agent coordinates signal generation from multiple sources and provides
    aggregated trading signals for the ZmartBot platform.
    """
    
    def __init__(self):
        """Initialize the Signal Generator Agent"""
        self.signal_center = SignalCenterService()
        self.active_signals: Dict[str, List[SignalData]] = {}
        self.signal_history: List[SignalData] = []
        self.is_running = False
        
        logger.info("Signal Generator Agent initialized")
    
    async def start(self):
        """Start the signal generation agent"""
        try:
            self.is_running = True
            logger.info("Signal Generator Agent started")
        except Exception as e:
            logger.error(f"Failed to start Signal Generator Agent: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the signal generation agent"""
        try:
            self.is_running = False
            logger.info("Signal Generator Agent stopped")
        except Exception as e:
            logger.error(f"Failed to stop Signal Generator Agent: {str(e)}")
    
    async def generate_signal(self, symbol: str, signal_type: SignalType) -> Optional[SignalData]:
        """
        Generate a trading signal for a specific symbol and type
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            signal_type: Type of signal to generate
        
        Returns:
            SignalData object or None if no signal generated
        """
        try:
            # Use the signal center to generate signals
            signal_info = await self.signal_center.get_signal_aggregation(symbol, "1h")
            
            if not signal_info:
                return None
            
            # Create signal data
            signal_data = SignalData(
                symbol=symbol,
                signal_type=signal_type,
                direction=SignalDirection.BUY if signal_info.get('direction') == 'BUY' else SignalDirection.SELL,
                strength=SignalStrength.STRONG if signal_info.get('strength', 0) > 0.7 else SignalStrength.MODERATE,
                confidence=signal_info.get('confidence', 0.5),
                price=signal_info.get('price', 0.0),
                timestamp=datetime.now(),
                source="signal_center",
                metadata=signal_info
            )
            
            # Store signal
            if symbol not in self.active_signals:
                self.active_signals[symbol] = []
            
            self.active_signals[symbol].append(signal_data)
            self.signal_history.append(signal_data)
            
            # Keep only last 100 signals per symbol
            if len(self.active_signals[symbol]) > 100:
                self.active_signals[symbol] = self.active_signals[symbol][-100:]
            
            # Keep only last 1000 signals in history
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-1000:]
            
            logger.info(f"Generated {signal_type.value} signal for {symbol}: {signal_data.direction.value} ({signal_data.strength.value})")
            
            return signal_data
            
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return None
    
    async def generate_multi_signals(self, symbols: List[str]) -> Dict[str, List[SignalData]]:
        """
        Generate signals for multiple symbols
        
        Args:
            symbols: List of trading symbols
        
        Returns:
            Dictionary mapping symbols to their signals
        """
        results = {}
        
        for symbol in symbols:
            symbol_signals = []
            
            # Generate different types of signals
            for signal_type in SignalType:
                signal = await self.generate_signal(symbol, signal_type)
                if signal:
                    symbol_signals.append(signal)
            
            if symbol_signals:
                results[symbol] = symbol_signals
        
        return results
    
    def get_active_signals(self, symbol: Optional[str] = None) -> Dict[str, List[SignalData]]:
        """
        Get active signals for a symbol or all symbols
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            Dictionary of active signals
        """
        if symbol:
            return {symbol: self.active_signals.get(symbol, [])}
        
        return self.active_signals.copy()
    
    def get_signal_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[SignalData]:
        """
        Get signal history
        
        Args:
            symbol: Optional symbol filter
            limit: Maximum number of signals to return
        
        Returns:
            List of historical signals
        """
        if symbol:
            history = [s for s in self.signal_history if s.symbol == symbol]
        else:
            history = self.signal_history
        
        return history[-limit:] if history else []
    
    async def get_aggregated_signal(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get aggregated signal for a symbol based on all active signals
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Aggregated signal data or None
        """
        try:
            signals = self.active_signals.get(symbol, [])
            
            if not signals:
                return None
            
            # Calculate aggregated metrics
            total_confidence = sum(s.confidence for s in signals)
            avg_confidence = total_confidence / len(signals)
            
            # Count directions
            buy_signals = sum(1 for s in signals if s.direction == SignalDirection.BUY)
            sell_signals = sum(1 for s in signals if s.direction == SignalDirection.SELL)
            
            # Determine overall direction
            if buy_signals > sell_signals:
                overall_direction = SignalDirection.BUY
                direction_strength = buy_signals / len(signals)
            elif sell_signals > buy_signals:
                overall_direction = SignalDirection.SELL
                direction_strength = sell_signals / len(signals)
            else:
                overall_direction = SignalDirection.HOLD
                direction_strength = 0.5
            
            # Calculate strength
            strong_signals = sum(1 for s in signals if s.strength == SignalStrength.STRONG)
            strength_ratio = strong_signals / len(signals)
            
            if strength_ratio > 0.6:
                overall_strength = SignalStrength.STRONG
            elif strength_ratio > 0.3:
                overall_strength = SignalStrength.MODERATE
            else:
                overall_strength = SignalStrength.WEAK
            
            return {
                'symbol': symbol,
                'direction': overall_direction.value,
                'strength': overall_strength.value,
                'confidence': avg_confidence,
                'direction_strength': direction_strength,
                'signal_count': len(signals),
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'timestamp': datetime.now().isoformat(),
                'latest_price': signals[-1].price if signals else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get aggregated signal for {symbol}: {str(e)}")
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the signal generator
        
        Returns:
            Health status information
        """
        return {
            'status': 'healthy' if self.is_running else 'stopped',
            'active_symbols': len(self.active_signals),
            'total_active_signals': sum(len(signals) for signals in self.active_signals.values()),
            'history_size': len(self.signal_history),
            'is_running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }