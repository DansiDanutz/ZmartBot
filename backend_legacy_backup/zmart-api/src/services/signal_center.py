#!/usr/bin/env python3
"""
Signal Center Service - Advanced Signal Processing & Aggregation
Handles signal ingestion, validation, scoring, and aggregation from multiple sources
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class SignalStrength(str, Enum):
    """Signal strength levels."""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class SignalDirection(str, Enum):
    """Signal direction types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class MarketCondition(str, Enum):
    """Market condition types."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    UNCERTAIN = "uncertain"

@dataclass
class SignalMetrics:
    """Signal quality and performance metrics."""
    accuracy: Decimal
    precision: Decimal
    recall: Decimal
    f1_score: Decimal
    sharpe_ratio: Decimal
    max_drawdown: Decimal
    win_rate: Decimal
    avg_return: Decimal
    volatility: Decimal
    last_updated: datetime

@dataclass
class ProcessingResult:
    """Result of signal processing operation."""
    success: bool
    processed_signal: Optional[Dict[str, Any]]
    error_message: Optional[str]
    processing_time_ms: float
    quality_score: Decimal
    confidence_score: Decimal

class SignalValidator:
    """Advanced signal validation and quality assessment."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Validation thresholds
        self.min_confidence = Decimal('0.1')
        self.max_confidence = Decimal('1.0')
        self.min_strength = Decimal('0.1')
        self.max_strength = Decimal('1.0')
        self.max_age_hours = 24
        
    def validate_raw_signal(self, signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate raw signal data."""
        errors = []
        
        # Required fields
        required_fields = ['symbol', 'direction', 'confidence', 'strength', 'timestamp']
        for field in required_fields:
            if field not in signal:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate confidence
        confidence = Decimal(str(signal.get('confidence', 0)))
        if not (self.min_confidence <= confidence <= self.max_confidence):
            errors.append(f"Invalid confidence: {confidence}")
        
        # Validate strength
        strength = Decimal(str(signal.get('strength', 0)))
        if not (self.min_strength <= strength <= self.max_strength):
            errors.append(f"Invalid strength: {strength}")
        
        # Validate timestamp
        try:
            timestamp = datetime.fromisoformat(signal['timestamp'].replace('Z', '+00:00'))
            if timestamp < datetime.now(timezone.utc) - timedelta(hours=self.max_age_hours):
                errors.append(f"Signal too old: {timestamp}")
        except Exception as e:
            errors.append(f"Invalid timestamp: {e}")
        
        # Validate symbol
        symbol = signal.get('symbol', '').upper()
        if not symbol or len(symbol) < 3:
            errors.append(f"Invalid symbol: {symbol}")
        
        return len(errors) == 0, errors
    
    def calculate_quality_score(self, signal: Dict[str, Any]) -> Decimal:
        """Calculate signal quality score."""
        try:
            # Base quality factors
            completeness = self._calculate_completeness_score(signal)
            consistency = self._calculate_consistency_score(signal)
            reliability = self._calculate_reliability_score(signal)
            
            # Weighted average
            quality_score = (
                completeness * Decimal('0.4') +
                consistency * Decimal('0.3') +
                reliability * Decimal('0.3')
            )
            
            return min(max(quality_score, Decimal('0.0')), Decimal('1.0'))
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return Decimal('0.0')
    
    def _calculate_completeness_score(self, signal: Dict[str, Any]) -> Decimal:
        """Calculate completeness score based on available fields."""
        required_fields = ['symbol', 'direction', 'confidence', 'strength', 'timestamp']
        optional_fields = ['source', 'timeframe', 'price', 'volume', 'indicators']
        
        total_fields = len(required_fields) + len(optional_fields)
        present_fields = 0
        
        for field in required_fields + optional_fields:
            if field in signal and signal[field] is not None:
                present_fields += 1
        
        return Decimal(str(present_fields / total_fields))
    
    def _calculate_consistency_score(self, signal: Dict[str, Any]) -> Decimal:
        """Calculate consistency score based on signal coherence."""
        try:
            confidence = Decimal(str(signal.get('confidence', 0)))
            strength = Decimal(str(signal.get('strength', 0)))
            
            # Check if confidence and strength are consistent
            if abs(confidence - strength) > Decimal('0.3'):
                return Decimal('0.5')
            elif abs(confidence - strength) > Decimal('0.1'):
                return Decimal('0.8')
            else:
                return Decimal('1.0')
                
        except Exception:
            return Decimal('0.5')
    
    def _calculate_reliability_score(self, signal: Dict[str, Any]) -> Decimal:
        """Calculate reliability score based on source and historical performance."""
        source = signal.get('source', 'unknown').lower()
        
        # Source reliability weights
        source_weights = {
            'kucoin': Decimal('0.9'),
            'binance': Decimal('0.9'),
            'cryptometer': Decimal('0.8'),
            'kingfisher': Decimal('0.85'),
            'zmartbot': Decimal('0.9'),
            'unknown': Decimal('0.5')
        }
        
        return source_weights.get(source, Decimal('0.5'))

class SignalProcessor:
    """Advanced signal processing and enhancement."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = SignalValidator()
        
    async def process_raw_signal(self, raw_signal: Dict[str, Any]) -> ProcessingResult:
        """Process raw signal and enhance with additional metrics."""
        start_time = datetime.now()
        
        try:
            # Validate signal
            is_valid, errors = self.validator.validate_raw_signal(raw_signal)
            if not is_valid:
                return ProcessingResult(
                    success=False,
                    processed_signal=None,
                    error_message=f"Validation failed: {', '.join(errors)}",
                    processing_time_ms=0,
                    quality_score=Decimal('0.0'),
                    confidence_score=Decimal('0.0')
                )
            
            # Calculate quality score
            quality_score = self.validator.calculate_quality_score(raw_signal)
            
            # Enhance signal with additional metrics
            enhanced_signal = await self._enhance_signal(raw_signal, quality_score)
            
            # Calculate confidence score
            confidence_score = self._calculate_adjusted_confidence(raw_signal, quality_score)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ProcessingResult(
                success=True,
                processed_signal=enhanced_signal,
                error_message=None,
                processing_time_ms=processing_time,
                quality_score=quality_score,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}")
            return ProcessingResult(
                success=False,
                processed_signal=None,
                error_message=str(e),
                processing_time_ms=0,
                quality_score=Decimal('0.0'),
                confidence_score=Decimal('0.0')
            )
    
    async def _enhance_signal(self, signal: Dict[str, Any], quality_score: Decimal) -> Dict[str, Any]:
        """Enhance signal with additional metrics and analysis."""
        enhanced = signal.copy()
        
        # Add processing metadata
        enhanced['processed_at'] = datetime.now(timezone.utc).isoformat()
        enhanced['quality_score'] = float(quality_score)
        enhanced['signal_id'] = str(uuid.uuid4())
        
        # Add market context
        enhanced['market_condition'] = self._assess_market_condition(signal)
        enhanced['risk_level'] = self._calculate_risk_level(signal)
        enhanced['expected_return'] = self._calculate_expected_return(signal)
        
        # Add technical indicators if not present
        if 'indicators' not in enhanced:
            enhanced['indicators'] = self._generate_default_indicators(signal)
        
        return enhanced
    
    def _assess_market_condition(self, signal: Dict[str, Any]) -> str:
        """Assess current market condition."""
        confidence = Decimal(str(signal.get('confidence', 0)))
        strength = Decimal(str(signal.get('strength', 0)))
        
        if confidence > Decimal('0.8') and strength > Decimal('0.8'):
            return MarketCondition.BULLISH
        elif confidence < Decimal('0.2') and strength < Decimal('0.2'):
            return MarketCondition.BEARISH
        elif abs(confidence - Decimal('0.5')) < Decimal('0.1'):
            return MarketCondition.SIDEWAYS
        else:
            return MarketCondition.UNCERTAIN
    
    def _calculate_risk_level(self, signal: Dict[str, Any]) -> str:
        """Calculate risk level based on signal characteristics."""
        confidence = Decimal(str(signal.get('confidence', 0)))
        strength = Decimal(str(signal.get('strength', 0)))
        
        avg_score = (confidence + strength) / Decimal('2')
        
        if avg_score > Decimal('0.8'):
            return 'LOW'
        elif avg_score > Decimal('0.6'):
            return 'MEDIUM'
        elif avg_score > Decimal('0.4'):
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    def _calculate_expected_return(self, signal: Dict[str, Any]) -> Optional[float]:
        """Calculate expected return based on signal strength and confidence."""
        try:
            confidence = Decimal(str(signal.get('confidence', 0)))
            strength = Decimal(str(signal.get('strength', 0)))
            
            # Simple expected return calculation
            base_return = float((confidence + strength) / Decimal('2'))
            direction_multiplier = 1.0 if signal.get('direction') in ['buy', 'strong_buy'] else -1.0
            
            return base_return * direction_multiplier * 0.1  # 10% max return
            
        except Exception:
            return None
    
    def _generate_default_indicators(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default technical indicators."""
        return {
            'rsi': 50.0,
            'macd': {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0},
            'bollinger_bands': {'upper': 0.0, 'middle': 0.0, 'lower': 0.0},
            'volume': 0.0,
            'price': 0.0
        }
    
    def _calculate_adjusted_confidence(self, signal: Dict[str, Any], quality_score: Decimal) -> Decimal:
        """Calculate adjusted confidence score."""
        base_confidence = Decimal(str(signal.get('confidence', 0)))
        
        # Adjust based on quality score
        adjusted_confidence = base_confidence * quality_score
        
        # Apply market condition multiplier
        market_condition = self._assess_market_condition(signal)
        condition_multiplier = self._get_condition_multiplier(market_condition)
        
        final_confidence = adjusted_confidence * condition_multiplier
        
        return min(max(final_confidence, Decimal('0.0')), Decimal('1.0'))
    
    def _get_condition_multiplier(self, condition: str) -> Decimal:
        """Get market condition multiplier."""
        multipliers = {
            'bullish': Decimal('1.1'),
            'bearish': Decimal('0.9'),
            'sideways': Decimal('1.0'),
            'volatile': Decimal('0.8'),
            'uncertain': Decimal('0.7')
        }
        return multipliers.get(condition.lower(), Decimal('1.0'))

class SignalAggregator:
    """Signal aggregation and consensus building."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def create_signal_aggregation(
        self, 
        signals: List[Dict[str, Any]], 
        symbol: str, 
        timeframe: str,
        max_age_hours: int = 1
    ) -> Optional[Dict[str, Any]]:
        """Create signal aggregation from multiple signals."""
        try:
            # Filter signals by age
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            recent_signals = [
                s for s in signals 
                if datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
            
            if not recent_signals:
                return None
            
            # Aggregate signals
            aggregation = self._aggregate_signals(recent_signals)
            
            if not aggregation:
                return None
            
            # Add metadata
            aggregation.update({
                'symbol': symbol,
                'timeframe': timeframe,
                'aggregated_at': datetime.now(timezone.utc).isoformat(),
                'signal_count': len(recent_signals),
                'sources': list(set(s.get('source', 'unknown') for s in recent_signals))
            })
            
            return aggregation
            
        except Exception as e:
            self.logger.error(f"Error creating signal aggregation: {e}")
            return None
    
    def _aggregate_signals(self, signals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Aggregate multiple signals into consensus."""
        try:
            if not signals:
                return None
            
            # Calculate weighted averages
            total_weight = Decimal('0.0')
            weighted_confidence = Decimal('0.0')
            weighted_strength = Decimal('0.0')
            weighted_quality = Decimal('0.0')
            
            directions = []
            sources = []
            
            for signal in signals:
                quality = Decimal(str(signal.get('quality_score', 0.5)))
                weight = quality
                
                total_weight += weight
                weighted_confidence += Decimal(str(signal.get('confidence', 0))) * weight
                weighted_strength += Decimal(str(signal.get('strength', 0))) * weight
                weighted_quality += quality * weight
                
                directions.append(signal.get('direction', 'hold'))
                sources.append(signal.get('source', 'unknown'))
            
            if total_weight == Decimal('0.0'):
                return None
            
            # Calculate consensus metrics
            avg_confidence = weighted_confidence / total_weight
            avg_strength = weighted_strength / total_weight
            avg_quality = weighted_quality / total_weight
            
            # Determine consensus direction
            consensus_direction = self._determine_consensus_direction(directions)
            
            # Calculate consensus strength
            consensus_strength = self._calculate_consensus_strength(directions, avg_strength)
            
            return {
                'consensus_direction': consensus_direction,
                'consensus_confidence': float(avg_confidence),
                'consensus_strength': float(consensus_strength),
                'quality_score': float(avg_quality),
                'agreement_ratio': self._calculate_agreement_ratio(directions),
                'source_diversity': len(set(sources)),
                'signal_count': len(signals)
            }
            
        except Exception as e:
            self.logger.error(f"Error aggregating signals: {e}")
            return None
    
    def _determine_consensus_direction(self, directions: List[str]) -> str:
        """Determine consensus direction from multiple signals."""
        if not directions:
            return 'hold'
        
        # Count directions
        direction_counts = {}
        for direction in directions:
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        # Find most common direction
        most_common = max(direction_counts.items(), key=lambda x: x[1])
        
        # Check if we have strong consensus (more than 60% agreement)
        total_signals = len(directions)
        if most_common[1] / total_signals > 0.6:
            return most_common[0]
        else:
            return 'hold'  # No strong consensus
    
    def _calculate_consensus_strength(self, directions: List[str], avg_strength: Decimal) -> Decimal:
        """Calculate consensus strength based on agreement."""
        if not directions:
            return Decimal('0.0')
        
        # Calculate agreement ratio
        agreement_ratio = self._calculate_agreement_ratio(directions)
        
        # Adjust strength based on agreement
        adjusted_strength = avg_strength * Decimal(str(agreement_ratio))
        
        return min(max(adjusted_strength, Decimal('0.0')), Decimal('1.0'))
    
    def _calculate_agreement_ratio(self, directions: List[str]) -> float:
        """Calculate agreement ratio among signals."""
        if not directions:
            return 0.0
        
        # Count most common direction
        direction_counts = {}
        for direction in directions:
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        most_common_count = max(direction_counts.values())
        total_signals = len(directions)
        
        return most_common_count / total_signals

class SignalCenterService:
    """Main signal center service for managing all signal operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = SignalValidator()
        self.processor = SignalProcessor()
        self.aggregator = SignalAggregator()
        self.signal_cache: Dict[str, Dict[str, Any]] = {}
    
    async def ingest_signal(self, signal_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Ingest and process a new signal."""
        try:
            # Process the signal
            result = await self.processor.process_raw_signal(signal_data)
            
            if not result.success:
                return False, result.error_message or "Processing failed", None
            
            # Cache the processed signal
            if result.processed_signal:
                signal_id = result.processed_signal.get('signal_id')
                if signal_id:
                    self.signal_cache[signal_id] = result.processed_signal
            
            return True, "Signal processed successfully", signal_id
            
        except Exception as e:
            self.logger.error(f"Error ingesting signal: {e}")
            return False, str(e), None
    
    async def get_signal_aggregation(
        self, 
        symbol: str, 
        timeframe: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get signal aggregation for a symbol and timeframe."""
        try:
            cache_key = f"{symbol}_{timeframe}"
            
            # Check cache first
            if not force_refresh and cache_key in self.signal_cache:
                return self.signal_cache[cache_key]
            
            # Get recent signals for this symbol/timeframe
            recent_signals = [
                signal for signal in self.signal_cache.values()
                if signal.get('symbol', '').upper() == symbol.upper() and
                signal.get('timeframe') == timeframe
            ]
            
            # Create aggregation
            aggregation = await self.aggregator.create_signal_aggregation(
                recent_signals, symbol, timeframe
            )
            
            if aggregation:
                self.signal_cache[cache_key] = aggregation
            
            return aggregation
            
        except Exception as e:
            self.logger.error(f"Error getting signal aggregation: {e}")
            return None
    
    async def get_top_signals(
        self, 
        limit: int = 10,
        min_quality: Optional[float] = None,
        symbols: Optional[List[str]] = None,
        timeframes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get top signals based on quality and criteria."""
        try:
            # Filter signals
            filtered_signals = []
            
            for signal in self.signal_cache.values():
                # Apply filters
                if min_quality and signal.get('quality_score', 0) < min_quality:
                    continue
                
                if symbols and signal.get('symbol', '').upper() not in [s.upper() for s in symbols]:
                    continue
                
                if timeframes and signal.get('timeframe') not in timeframes:
                    continue
                
                filtered_signals.append(signal)
            
            # Sort by quality score and return top signals
            sorted_signals = sorted(
                filtered_signals,
                key=lambda x: x.get('quality_score', 0),
                reverse=True
            )
            
            return sorted_signals[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top signals: {e}")
            return []
    
    async def cleanup_expired_signals(self) -> int:
        """Clean up expired signals from cache."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            expired_keys = []
            
            for key, signal in self.signal_cache.items():
                try:
                    timestamp = datetime.fromisoformat(signal.get('timestamp', '').replace('Z', '+00:00'))
                    if timestamp < cutoff_time:
                        expired_keys.append(key)
                except Exception:
                    expired_keys.append(key)
            
            # Remove expired signals
            for key in expired_keys:
                del self.signal_cache[key]
            
            return len(expired_keys)
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired signals: {e}")
            return 0

# Global signal center service instance
signal_center_service: Optional[SignalCenterService] = None

async def get_signal_center_service() -> SignalCenterService:
    """Get or create signal center service instance."""
    global signal_center_service
    if signal_center_service is None:
        signal_center_service = SignalCenterService()
    return signal_center_service 