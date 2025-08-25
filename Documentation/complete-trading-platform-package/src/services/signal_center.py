"""
Trade Strategy Module - Signal Center Service
=============================================

Advanced signal processing and aggregation service for the Trade Strategy module.
Handles signal ingestion, validation, scoring, and aggregation from multiple sources.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
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
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from redis import Redis
from celery import Celery
from pydantic import BaseModel, Field, validator

from ..core.config import settings, config_manager
from ..models.base import BaseRepository
from ..models.signals import (
    SignalSource, RawSignal, ProcessedSignal, SignalAggregation,
    SignalSourceCreate, RawSignalCreate, ProcessedSignalCreate,
    SignalAggregationCreate
)


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
    processed_signal: Optional[ProcessedSignal]
    error_message: Optional[str]
    processing_time_ms: float
    quality_score: Decimal
    confidence_score: Decimal


class SignalValidator:
    """Advanced signal validation and quality assessment."""
    
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Validation thresholds
        self.min_confidence = settings.signal_processing.min_signal_confidence
        self.min_quality = settings.signal_processing.min_signal_quality
        self.max_price_deviation = Decimal('0.10')  # 10% max price deviation
        
    def validate_raw_signal(self, signal: RawSignal) -> Tuple[bool, List[str]]:
        """Validate raw signal data and return validation result."""
        errors = []
        
        # Basic data validation
        if not signal.symbol or len(signal.symbol) < 2:
            errors.append("Invalid symbol format")
        
        if signal.strength < 0 or signal.strength > 1:
            errors.append("Signal strength must be between 0 and 1")
        
        if signal.confidence < 0 or signal.confidence > 1:
            errors.append("Signal confidence must be between 0 and 1")
        
        if signal.price and signal.price <= 0:
            errors.append("Price must be positive")
        
        # Timeframe validation
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        if signal.timeframe not in valid_timeframes:
            errors.append(f"Invalid timeframe: {signal.timeframe}")
        
        # Signal type validation
        valid_types = [e.value for e in SignalDirection]
        if signal.signal_type not in valid_types:
            errors.append(f"Invalid signal type: {signal.signal_type}")
        
        # Price consistency checks
        if signal.price and signal.target_price:
            if signal.signal_type in ['buy', 'strong_buy']:
                if signal.target_price <= signal.price:
                    errors.append("Target price should be higher than entry price for buy signals")
            elif signal.signal_type in ['sell', 'strong_sell']:
                if signal.target_price >= signal.price:
                    errors.append("Target price should be lower than entry price for sell signals")
        
        # Stop loss validation
        if signal.price and signal.stop_loss:
            if signal.signal_type in ['buy', 'strong_buy']:
                if signal.stop_loss >= signal.price:
                    errors.append("Stop loss should be lower than entry price for buy signals")
            elif signal.signal_type in ['sell', 'strong_sell']:
                if signal.stop_loss <= signal.price:
                    errors.append("Stop loss should be higher than entry price for sell signals")
        
        # Market data consistency check
        if signal.price:
            market_price = self._get_current_market_price(signal.symbol)
            if market_price:
                price_deviation = abs(signal.price - market_price) / market_price
                if price_deviation > self.max_price_deviation:
                    errors.append(f"Signal price deviates too much from market price: {price_deviation:.2%}")
        
        return len(errors) == 0, errors
    
    def calculate_quality_score(self, signal: RawSignal, source: SignalSource) -> Decimal:
        """Calculate quality score for a signal based on multiple factors."""
        quality_factors = []
        
        # Source reliability factor (30%)
        source_factor = source.reliability_score * Decimal('0.30')
        quality_factors.append(source_factor)
        
        # Signal confidence factor (25%)
        confidence_factor = signal.confidence * Decimal('0.25')
        quality_factors.append(confidence_factor)
        
        # Signal strength factor (20%)
        strength_factor = signal.strength * Decimal('0.20')
        quality_factors.append(strength_factor)
        
        # Data completeness factor (15%)
        completeness_score = self._calculate_completeness_score(signal)
        completeness_factor = completeness_score * Decimal('0.15')
        quality_factors.append(completeness_factor)
        
        # Historical performance factor (10%)
        historical_factor = self._get_historical_performance_factor(signal, source) * Decimal('0.10')
        quality_factors.append(historical_factor)
        
        # Calculate weighted average
        total_quality = sum(quality_factors)
        
        # Apply market condition adjustment
        market_condition = self._assess_market_condition(signal.symbol)
        condition_multiplier = self._get_condition_multiplier(market_condition, signal.signal_type)
        
        final_quality = total_quality * condition_multiplier
        
        # Ensure quality score is within bounds
        return max(Decimal('0'), min(Decimal('1'), final_quality))
    
    def _calculate_completeness_score(self, signal: RawSignal) -> Decimal:
        """Calculate data completeness score."""
        total_fields = 8  # Total number of optional fields
        present_fields = 0
        
        optional_fields = [
            signal.price, signal.target_price, signal.stop_loss,
            signal.metadata, signal.raw_data
        ]
        
        for field in optional_fields:
            if field is not None:
                present_fields += 1
        
        # Additional points for rich metadata
        if signal.metadata:
            metadata_keys = len(signal.metadata) if isinstance(signal.metadata, dict) else 0
            present_fields += min(metadata_keys / 5, 3)  # Up to 3 bonus points
        
        return Decimal(str(present_fields / total_fields))
    
    def _get_historical_performance_factor(self, signal: RawSignal, source: SignalSource) -> Decimal:
        """Get historical performance factor for signal type from this source."""
        cache_key = f"signal_performance:{source.id}:{signal.signal_type}:{signal.timeframe}"
        
        cached_performance = self.redis_client.get(cache_key)
        if cached_performance:
            try:
                return Decimal(cached_performance)
            except:
                pass
        
        # Default performance factor if no historical data
        return Decimal('0.5')
    
    def _get_current_market_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for symbol."""
        cache_key = f"market_price:{symbol}"
        
        cached_price = self.redis_client.get(cache_key)
        if cached_price:
            try:
                return Decimal(cached_price)
            except:
                pass
        
        return None
    
    def _assess_market_condition(self, symbol: str) -> MarketCondition:
        """Assess current market condition for symbol."""
        cache_key = f"market_condition:{symbol}"
        
        cached_condition = self.redis_client.get(cache_key)
        if cached_condition:
            try:
                return MarketCondition(cached_condition)
            except:
                pass
        
        # Default to uncertain if no data available
        return MarketCondition.UNCERTAIN
    
    def _get_condition_multiplier(self, condition: MarketCondition, signal_type: str) -> Decimal:
        """Get quality multiplier based on market condition and signal type."""
        multipliers = {
            MarketCondition.BULLISH: {
                'buy': Decimal('1.2'),
                'strong_buy': Decimal('1.3'),
                'sell': Decimal('0.8'),
                'strong_sell': Decimal('0.7'),
                'hold': Decimal('0.9')
            },
            MarketCondition.BEARISH: {
                'buy': Decimal('0.7'),
                'strong_buy': Decimal('0.6'),
                'sell': Decimal('1.2'),
                'strong_sell': Decimal('1.3'),
                'hold': Decimal('0.9')
            },
            MarketCondition.SIDEWAYS: {
                'buy': Decimal('0.9'),
                'strong_buy': Decimal('0.8'),
                'sell': Decimal('0.9'),
                'strong_sell': Decimal('0.8'),
                'hold': Decimal('1.1')
            },
            MarketCondition.VOLATILE: {
                'buy': Decimal('0.8'),
                'strong_buy': Decimal('0.7'),
                'sell': Decimal('0.8'),
                'strong_sell': Decimal('0.7'),
                'hold': Decimal('1.2')
            },
            MarketCondition.UNCERTAIN: {
                'buy': Decimal('0.9'),
                'strong_buy': Decimal('0.8'),
                'sell': Decimal('0.9'),
                'strong_sell': Decimal('0.8'),
                'hold': Decimal('1.0')
            }
        }
        
        return multipliers.get(condition, {}).get(signal_type, Decimal('1.0'))


class SignalProcessor:
    """Advanced signal processing engine."""
    
    def __init__(self, session: Session, redis_client: Redis):
        self.session = session
        self.redis_client = redis_client
        self.validator = SignalValidator(redis_client)
        self.logger = logging.getLogger(__name__)
        
        # Initialize repositories
        self.raw_signal_repo = BaseRepository(RawSignal, session)
        self.processed_signal_repo = BaseRepository(ProcessedSignal, session)
        self.signal_source_repo = BaseRepository(SignalSource, session)
    
    async def process_raw_signal(self, raw_signal: RawSignal) -> ProcessingResult:
        """Process a raw signal into a processed signal."""
        start_time = datetime.now()
        
        try:
            # Get signal source
            source = self.signal_source_repo.get(raw_signal.source_id)
            if not source:
                return ProcessingResult(
                    success=False,
                    processed_signal=None,
                    error_message="Signal source not found",
                    processing_time_ms=0,
                    quality_score=Decimal('0'),
                    confidence_score=Decimal('0')
                )
            
            # Validate raw signal
            is_valid, errors = self.validator.validate_raw_signal(raw_signal)
            if not is_valid:
                return ProcessingResult(
                    success=False,
                    processed_signal=None,
                    error_message=f"Validation failed: {'; '.join(errors)}",
                    processing_time_ms=0,
                    quality_score=Decimal('0'),
                    confidence_score=Decimal('0')
                )
            
            # Calculate quality score
            quality_score = self.validator.calculate_quality_score(raw_signal, source)
            
            # Check minimum quality threshold
            if quality_score < self.validator.min_quality:
                return ProcessingResult(
                    success=False,
                    processed_signal=None,
                    error_message=f"Quality score {quality_score} below minimum threshold {self.validator.min_quality}",
                    processing_time_ms=0,
                    quality_score=quality_score,
                    confidence_score=raw_signal.confidence
                )
            
            # Calculate adjusted strength and confidence
            adjusted_strength = self._calculate_adjusted_strength(raw_signal, source, quality_score)
            adjusted_confidence = self._calculate_adjusted_confidence(raw_signal, source, quality_score)
            
            # Calculate risk metrics
            risk_score = self._calculate_risk_score(raw_signal, source)
            expected_return = self._calculate_expected_return(raw_signal, source)
            max_drawdown = self._calculate_max_drawdown(raw_signal, source)
            
            # Assess market condition
            market_condition = self.validator._assess_market_condition(raw_signal.symbol)
            
            # Calculate correlation with other signals
            correlation_score = await self._calculate_correlation_score(raw_signal)
            
            # Create processed signal
            processed_signal_data = ProcessedSignalCreate(
                raw_signal_id=raw_signal.id,
                source_id=raw_signal.source_id,
                symbol=raw_signal.symbol,
                signal_type=raw_signal.signal_type,
                original_strength=raw_signal.strength,
                adjusted_strength=adjusted_strength,
                confidence=adjusted_confidence,
                quality_score=quality_score,
                risk_score=risk_score,
                timeframe=raw_signal.timeframe,
                price=raw_signal.price,
                target_price=raw_signal.target_price,
                stop_loss=raw_signal.stop_loss,
                expected_return=expected_return,
                max_drawdown=max_drawdown,
                correlation_score=correlation_score,
                market_condition=market_condition.value,
                validation_flags={
                    "validated": True,
                    "quality_check": True,
                    "risk_assessed": True,
                    "correlation_analyzed": True
                },
                processing_metadata={
                    "processing_version": "1.0",
                    "validator_version": "1.0",
                    "market_condition_at_processing": market_condition.value,
                    "source_reliability_at_processing": float(source.reliability_score)
                },
                expires_at=datetime.now(timezone.utc) + timedelta(
                    minutes=settings.signal_processing.signal_expiry_minutes
                )
            )
            
            # Save processed signal
            processed_signal = self.processed_signal_repo.create(processed_signal_data)
            
            # Update raw signal status
            raw_signal.processed_at = datetime.now(timezone.utc)
            raw_signal.is_processed = True
            raw_signal.processing_status = "completed"
            self.session.commit()
            
            # Cache processed signal for quick access
            await self._cache_processed_signal(processed_signal)
            
            # Update source performance metrics
            await self._update_source_metrics(source, processed_signal)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                f"Successfully processed signal {raw_signal.id} "
                f"with quality score {quality_score} in {processing_time:.2f}ms"
            )
            
            return ProcessingResult(
                success=True,
                processed_signal=processed_signal,
                error_message=None,
                processing_time_ms=processing_time,
                quality_score=quality_score,
                confidence_score=adjusted_confidence
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Error processing signal {raw_signal.id}: {str(e)}")
            
            # Update raw signal with error status
            raw_signal.processing_status = "failed"
            self.session.commit()
            
            return ProcessingResult(
                success=False,
                processed_signal=None,
                error_message=str(e),
                processing_time_ms=processing_time,
                quality_score=Decimal('0'),
                confidence_score=Decimal('0')
            )
    
    def _calculate_adjusted_strength(
        self, 
        signal: RawSignal, 
        source: SignalSource, 
        quality_score: Decimal
    ) -> Decimal:
        """Calculate adjusted signal strength based on source reliability and quality."""
        base_strength = signal.strength
        
        # Apply source reliability adjustment
        reliability_adjustment = source.reliability_score * Decimal('0.3')
        
        # Apply quality score adjustment
        quality_adjustment = quality_score * Decimal('0.2')
        
        # Calculate adjusted strength
        adjusted_strength = base_strength + reliability_adjustment + quality_adjustment
        
        # Ensure within bounds [0, 1]
        return max(Decimal('0'), min(Decimal('1'), adjusted_strength))
    
    def _calculate_adjusted_confidence(
        self, 
        signal: RawSignal, 
        source: SignalSource, 
        quality_score: Decimal
    ) -> Decimal:
        """Calculate adjusted confidence based on various factors."""
        base_confidence = signal.confidence
        
        # Apply source reliability factor
        reliability_factor = Decimal('1') + (source.reliability_score - Decimal('0.5')) * Decimal('0.2')
        
        # Apply quality factor
        quality_factor = Decimal('1') + (quality_score - Decimal('0.5')) * Decimal('0.15')
        
        # Calculate adjusted confidence
        adjusted_confidence = base_confidence * reliability_factor * quality_factor
        
        # Ensure within bounds [0, 1]
        return max(Decimal('0'), min(Decimal('1'), adjusted_confidence))
    
    def _calculate_risk_score(self, signal: RawSignal, source: SignalSource) -> Decimal:
        """Calculate risk score for the signal."""
        risk_factors = []
        
        # Base risk from signal strength (higher strength = lower risk)
        strength_risk = Decimal('1') - signal.strength
        risk_factors.append(strength_risk * Decimal('0.3'))
        
        # Source reliability risk (lower reliability = higher risk)
        reliability_risk = Decimal('1') - source.reliability_score
        risk_factors.append(reliability_risk * Decimal('0.25'))
        
        # Confidence risk (lower confidence = higher risk)
        confidence_risk = Decimal('1') - signal.confidence
        risk_factors.append(confidence_risk * Decimal('0.2'))
        
        # Timeframe risk (shorter timeframes = higher risk)
        timeframe_risk = self._get_timeframe_risk(signal.timeframe)
        risk_factors.append(timeframe_risk * Decimal('0.15'))
        
        # Market volatility risk
        volatility_risk = self._get_volatility_risk(signal.symbol)
        risk_factors.append(volatility_risk * Decimal('0.1'))
        
        # Calculate total risk score
        total_risk = sum(risk_factors)
        
        # Ensure within bounds [0, 1]
        return max(Decimal('0'), min(Decimal('1'), total_risk))
    
    def _calculate_expected_return(self, signal: RawSignal, source: SignalSource) -> Optional[Decimal]:
        """Calculate expected return for the signal."""
        if not signal.price or not signal.target_price:
            return None
        
        # Calculate basic return
        if signal.signal_type in ['buy', 'strong_buy']:
            basic_return = (signal.target_price - signal.price) / signal.price
        elif signal.signal_type in ['sell', 'strong_sell']:
            basic_return = (signal.price - signal.target_price) / signal.price
        else:
            return Decimal('0')
        
        # Adjust for signal strength and confidence
        strength_factor = signal.strength
        confidence_factor = signal.confidence
        reliability_factor = source.reliability_score
        
        # Calculate expected return with adjustments
        expected_return = basic_return * strength_factor * confidence_factor * reliability_factor
        
        return expected_return
    
    def _calculate_max_drawdown(self, signal: RawSignal, source: SignalSource) -> Optional[Decimal]:
        """Calculate maximum expected drawdown for the signal."""
        if not signal.price or not signal.stop_loss:
            # Use default drawdown based on signal type and timeframe
            return self._get_default_drawdown(signal.signal_type, signal.timeframe)
        
        # Calculate drawdown from stop loss
        if signal.signal_type in ['buy', 'strong_buy']:
            drawdown = (signal.price - signal.stop_loss) / signal.price
        elif signal.signal_type in ['sell', 'strong_sell']:
            drawdown = (signal.stop_loss - signal.price) / signal.price
        else:
            return Decimal('0')
        
        # Adjust for source reliability (less reliable sources may have higher actual drawdown)
        reliability_adjustment = Decimal('2') - source.reliability_score
        adjusted_drawdown = drawdown * reliability_adjustment
        
        return max(Decimal('0'), adjusted_drawdown)
    
    async def _calculate_correlation_score(self, signal: RawSignal) -> Decimal:
        """Calculate correlation score with other recent signals."""
        # Get recent signals for the same symbol
        recent_signals = self.session.query(ProcessedSignal).filter(
            and_(
                ProcessedSignal.symbol == signal.symbol,
                ProcessedSignal.created_at >= datetime.now(timezone.utc) - timedelta(hours=24),
                ProcessedSignal.is_active == True
            )
        ).limit(10).all()
        
        if not recent_signals:
            return Decimal('0.5')  # Neutral correlation if no recent signals
        
        # Calculate correlation based on signal agreement
        same_direction_count = 0
        total_signals = len(recent_signals)
        
        for recent_signal in recent_signals:
            if self._signals_agree(signal.signal_type, recent_signal.signal_type):
                same_direction_count += 1
        
        correlation_score = Decimal(str(same_direction_count / total_signals))
        
        return correlation_score
    
    def _signals_agree(self, signal1_type: str, signal2_type: str) -> bool:
        """Check if two signals agree in direction."""
        buy_signals = ['buy', 'strong_buy']
        sell_signals = ['sell', 'strong_sell']
        
        return (
            (signal1_type in buy_signals and signal2_type in buy_signals) or
            (signal1_type in sell_signals and signal2_type in sell_signals) or
            (signal1_type == 'hold' and signal2_type == 'hold')
        )
    
    def _get_timeframe_risk(self, timeframe: str) -> Decimal:
        """Get risk factor based on timeframe."""
        risk_map = {
            '1m': Decimal('0.9'),
            '5m': Decimal('0.8'),
            '15m': Decimal('0.7'),
            '30m': Decimal('0.6'),
            '1h': Decimal('0.5'),
            '4h': Decimal('0.4'),
            '1d': Decimal('0.3'),
            '1w': Decimal('0.2')
        }
        return risk_map.get(timeframe, Decimal('0.5'))
    
    def _get_volatility_risk(self, symbol: str) -> Decimal:
        """Get volatility risk for symbol."""
        # This would typically fetch from market data
        # For now, return default moderate risk
        return Decimal('0.5')
    
    def _get_default_drawdown(self, signal_type: str, timeframe: str) -> Decimal:
        """Get default expected drawdown based on signal type and timeframe."""
        base_drawdowns = {
            'buy': Decimal('0.05'),
            'strong_buy': Decimal('0.08'),
            'sell': Decimal('0.05'),
            'strong_sell': Decimal('0.08'),
            'hold': Decimal('0.02')
        }
        
        timeframe_multipliers = {
            '1m': Decimal('2.0'),
            '5m': Decimal('1.8'),
            '15m': Decimal('1.5'),
            '30m': Decimal('1.3'),
            '1h': Decimal('1.0'),
            '4h': Decimal('0.8'),
            '1d': Decimal('0.6'),
            '1w': Decimal('0.4')
        }
        
        base_drawdown = base_drawdowns.get(signal_type, Decimal('0.05'))
        timeframe_multiplier = timeframe_multipliers.get(timeframe, Decimal('1.0'))
        
        return base_drawdown * timeframe_multiplier
    
    async def _cache_processed_signal(self, signal: ProcessedSignal) -> None:
        """Cache processed signal for quick access."""
        cache_key = f"{settings.redis_namespace}:processed_signal:{signal.id}"
        
        signal_data = {
            "id": str(signal.id),
            "symbol": signal.symbol,
            "signal_type": signal.signal_type,
            "adjusted_strength": float(signal.adjusted_strength),
            "confidence": float(signal.confidence),
            "quality_score": float(signal.quality_score),
            "risk_score": float(signal.risk_score),
            "timeframe": signal.timeframe,
            "created_at": signal.created_at.isoformat(),
            "expires_at": signal.expires_at.isoformat() if signal.expires_at else None
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.redis_client.setex(
                cache_key,
                settings.redis_ttl_seconds,
                json.dumps(signal_data)
            )
        )
    
    async def _update_source_metrics(self, source: SignalSource, signal: ProcessedSignal) -> None:
        """Update source performance metrics."""
        # This would typically update comprehensive metrics
        # For now, just log the processing
        self.logger.debug(
            f"Updated metrics for source {source.name} "
            f"with signal quality {signal.quality_score}"
        )


class SignalAggregator:
    """Advanced signal aggregation engine."""
    
    def __init__(self, session: Session, redis_client: Redis):
        self.session = session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize repositories
        self.processed_signal_repo = BaseRepository(ProcessedSignal, session)
        self.aggregation_repo = BaseRepository(SignalAggregation, session)
        
        # Aggregation parameters
        self.min_signals = settings.signal_processing.min_signals_for_consensus
        self.consensus_threshold = settings.signal_processing.consensus_threshold
    
    async def create_signal_aggregation(
        self, 
        symbol: str, 
        timeframe: str,
        max_age_hours: int = 1
    ) -> Optional[SignalAggregation]:
        """Create signal aggregation for symbol and timeframe."""
        try:
            # Get recent high-quality signals
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            
            signals = self.session.query(ProcessedSignal).filter(
                and_(
                    ProcessedSignal.symbol == symbol,
                    ProcessedSignal.timeframe == timeframe,
                    ProcessedSignal.created_at >= cutoff_time,
                    ProcessedSignal.is_active == True,
                    ProcessedSignal.quality_score >= settings.signal_processing.min_signal_quality
                )
            ).order_by(desc(ProcessedSignal.quality_score)).all()
            
            if len(signals) < self.min_signals:
                self.logger.info(
                    f"Insufficient signals for aggregation: {len(signals)} < {self.min_signals}"
                )
                return None
            
            # Perform aggregation
            aggregation_result = self._aggregate_signals(signals)
            
            if not aggregation_result:
                return None
            
            # Create aggregation record
            aggregation_data = SignalAggregationCreate(
                symbol=symbol,
                timeframe=timeframe,
                aggregation_type="weighted_consensus",
                signal_count=len(signals),
                buy_signals=aggregation_result["buy_signals"],
                sell_signals=aggregation_result["sell_signals"],
                hold_signals=aggregation_result["hold_signals"],
                consensus_signal=aggregation_result["consensus_signal"],
                consensus_strength=aggregation_result["consensus_strength"],
                consensus_confidence=aggregation_result["consensus_confidence"],
                risk_reward_ratio=aggregation_result["risk_reward_ratio"],
                expected_return=aggregation_result["expected_return"],
                max_risk=aggregation_result["max_risk"],
                signal_ids=[signal.id for signal in signals],
                weights=aggregation_result["weights"],
                aggregation_metadata={
                    "aggregation_version": "1.0",
                    "min_quality_threshold": float(settings.signal_processing.min_signal_quality),
                    "consensus_threshold": float(self.consensus_threshold),
                    "signals_considered": len(signals),
                    "aggregation_timestamp": datetime.now(timezone.utc).isoformat()
                },
                expires_at=datetime.now(timezone.utc) + timedelta(
                    minutes=settings.signal_processing.signal_expiry_minutes
                )
            )
            
            aggregation = self.aggregation_repo.create(aggregation_data)
            
            # Cache aggregation
            await self._cache_aggregation(aggregation)
            
            self.logger.info(
                f"Created signal aggregation for {symbol} {timeframe} "
                f"with {len(signals)} signals, consensus: {aggregation_result['consensus_signal']}"
            )
            
            return aggregation
            
        except Exception as e:
            self.logger.error(f"Error creating signal aggregation: {str(e)}")
            return None
    
    def _aggregate_signals(self, signals: List[ProcessedSignal]) -> Optional[Dict[str, Any]]:
        """Aggregate multiple signals into consensus."""
        if not signals:
            return None
        
        # Calculate weights based on quality score and confidence
        weights = []
        for signal in signals:
            weight = signal.quality_score * signal.confidence
            weights.append(float(weight))
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return None
        
        normalized_weights = [w / total_weight for w in weights]
        
        # Count signal types
        signal_counts = {"buy": 0, "sell": 0, "hold": 0}
        weighted_strengths = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        
        for i, signal in enumerate(signals):
            weight = normalized_weights[i]
            
            if signal.signal_type in ['buy', 'strong_buy']:
                signal_counts["buy"] += 1
                weighted_strengths["buy"] += float(signal.adjusted_strength) * weight
            elif signal.signal_type in ['sell', 'strong_sell']:
                signal_counts["sell"] += 1
                weighted_strengths["sell"] += float(signal.adjusted_strength) * weight
            else:
                signal_counts["hold"] += 1
                weighted_strengths["hold"] += float(signal.adjusted_strength) * weight
        
        # Determine consensus
        max_count = max(signal_counts.values())
        consensus_types = [k for k, v in signal_counts.items() if v == max_count]
        
        # If tie, use weighted strength to break it
        if len(consensus_types) > 1:
            consensus_signal = max(consensus_types, key=lambda x: weighted_strengths[x])
        else:
            consensus_signal = consensus_types[0]
        
        # Calculate consensus strength and confidence
        consensus_strength = Decimal(str(weighted_strengths[consensus_signal]))
        
        # Calculate weighted average confidence
        weighted_confidence = sum(
            float(signal.confidence) * normalized_weights[i]
            for i, signal in enumerate(signals)
        )
        consensus_confidence = Decimal(str(weighted_confidence))
        
        # Calculate risk metrics
        expected_returns = [
            float(signal.expected_return) * normalized_weights[i]
            for i, signal in enumerate(signals)
            if signal.expected_return is not None
        ]
        expected_return = Decimal(str(sum(expected_returns))) if expected_returns else None
        
        max_risks = [
            float(signal.max_drawdown) * normalized_weights[i]
            for i, signal in enumerate(signals)
            if signal.max_drawdown is not None
        ]
        max_risk = Decimal(str(sum(max_risks))) if max_risks else None
        
        # Calculate risk-reward ratio
        risk_reward_ratio = None
        if expected_return and max_risk and max_risk > 0:
            risk_reward_ratio = expected_return / max_risk
        
        return {
            "buy_signals": signal_counts["buy"],
            "sell_signals": signal_counts["sell"],
            "hold_signals": signal_counts["hold"],
            "consensus_signal": consensus_signal,
            "consensus_strength": consensus_strength,
            "consensus_confidence": consensus_confidence,
            "risk_reward_ratio": risk_reward_ratio,
            "expected_return": expected_return,
            "max_risk": max_risk,
            "weights": [Decimal(str(w)) for w in normalized_weights]
        }
    
    async def _cache_aggregation(self, aggregation: SignalAggregation) -> None:
        """Cache signal aggregation for quick access."""
        cache_key = f"{settings.redis_namespace}:aggregation:{aggregation.symbol}:{aggregation.timeframe}"
        
        aggregation_data = {
            "id": str(aggregation.id),
            "symbol": aggregation.symbol,
            "timeframe": aggregation.timeframe,
            "consensus_signal": aggregation.consensus_signal,
            "consensus_strength": float(aggregation.consensus_strength),
            "consensus_confidence": float(aggregation.consensus_confidence),
            "signal_count": aggregation.signal_count,
            "created_at": aggregation.created_at.isoformat(),
            "expires_at": aggregation.expires_at.isoformat() if aggregation.expires_at else None
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.redis_client.setex(
                cache_key,
                settings.redis_ttl_seconds,
                json.dumps(aggregation_data)
            )
        )


class SignalCenterService:
    """Main Signal Center service orchestrating all signal operations."""
    
    def __init__(self, session: Session, redis_client: Redis):
        self.session = session
        self.redis_client = redis_client
        self.processor = SignalProcessor(session, redis_client)
        self.aggregator = SignalAggregator(session, redis_client)
        self.logger = logging.getLogger(__name__)
        
        # Initialize repositories
        self.raw_signal_repo = BaseRepository(RawSignal, session)
        self.processed_signal_repo = BaseRepository(ProcessedSignal, session)
        self.aggregation_repo = BaseRepository(SignalAggregation, session)
    
    async def ingest_signal(self, signal_data: RawSignalCreate) -> Tuple[bool, str, Optional[uuid.UUID]]:
        """Ingest a new raw signal."""
        try:
            # Create raw signal
            raw_signal = self.raw_signal_repo.create(signal_data)
            
            # Process signal asynchronously
            processing_result = await self.processor.process_raw_signal(raw_signal)
            
            if processing_result.success:
                self.logger.info(f"Successfully ingested and processed signal {raw_signal.id}")
                return True, "Signal processed successfully", raw_signal.id
            else:
                self.logger.warning(
                    f"Signal {raw_signal.id} ingested but processing failed: "
                    f"{processing_result.error_message}"
                )
                return False, processing_result.error_message, raw_signal.id
                
        except Exception as e:
            self.logger.error(f"Error ingesting signal: {str(e)}")
            return False, str(e), None
    
    async def get_signal_aggregation(
        self, 
        symbol: str, 
        timeframe: str,
        force_refresh: bool = False
    ) -> Optional[SignalAggregation]:
        """Get or create signal aggregation for symbol and timeframe."""
        if not force_refresh:
            # Try to get cached aggregation first
            cached_aggregation = await self._get_cached_aggregation(symbol, timeframe)
            if cached_aggregation:
                return cached_aggregation
        
        # Create new aggregation
        return await self.aggregator.create_signal_aggregation(symbol, timeframe)
    
    async def get_top_signals(
        self, 
        limit: int = 10,
        min_quality: Optional[Decimal] = None,
        symbols: Optional[List[str]] = None,
        timeframes: Optional[List[str]] = None
    ) -> List[ProcessedSignal]:
        """Get top quality signals with optional filtering."""
        query = self.session.query(ProcessedSignal).filter(
            ProcessedSignal.is_active == True
        )
        
        # Apply filters
        if min_quality:
            query = query.filter(ProcessedSignal.quality_score >= min_quality)
        
        if symbols:
            query = query.filter(ProcessedSignal.symbol.in_(symbols))
        
        if timeframes:
            query = query.filter(ProcessedSignal.timeframe.in_(timeframes))
        
        # Order by quality score and limit
        signals = query.order_by(
            desc(ProcessedSignal.quality_score),
            desc(ProcessedSignal.confidence)
        ).limit(limit).all()
        
        return signals
    
    async def cleanup_expired_signals(self) -> int:
        """Clean up expired signals and aggregations."""
        now = datetime.now(timezone.utc)
        
        # Clean up expired processed signals
        expired_signals = self.session.query(ProcessedSignal).filter(
            and_(
                ProcessedSignal.expires_at < now,
                ProcessedSignal.is_active == True
            )
        ).all()
        
        for signal in expired_signals:
            signal.is_active = False
        
        # Clean up expired aggregations
        expired_aggregations = self.session.query(SignalAggregation).filter(
            and_(
                SignalAggregation.expires_at < now,
                SignalAggregation.is_active == True
            )
        ).all()
        
        for aggregation in expired_aggregations:
            aggregation.is_active = False
        
        self.session.commit()
        
        total_cleaned = len(expired_signals) + len(expired_aggregations)
        self.logger.info(f"Cleaned up {total_cleaned} expired signals and aggregations")
        
        return total_cleaned
    
    async def _get_cached_aggregation(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Optional[SignalAggregation]:
        """Get cached signal aggregation."""
        cache_key = f"{settings.redis_namespace}:aggregation:{symbol}:{timeframe}"
        
        try:
            cached_data = await asyncio.get_event_loop().run_in_executor(
                None,
                self.redis_client.get,
                cache_key
            )
            
            if cached_data:
                data = json.loads(cached_data)
                aggregation_id = uuid.UUID(data["id"])
                return self.aggregation_repo.get(aggregation_id)
                
        except Exception as e:
            self.logger.warning(f"Error getting cached aggregation: {str(e)}")
        
        return None


# Export main service class
__all__ = [
    'SignalCenterService',
    'SignalProcessor',
    'SignalAggregator',
    'SignalValidator',
    'SignalStrength',
    'SignalDirection',
    'MarketCondition',
    'ProcessingResult'
]

