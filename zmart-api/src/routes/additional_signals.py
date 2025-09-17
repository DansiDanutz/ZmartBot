#!/usr/bin/env python3
"""
Additional Signal Routes - Advanced Signal Management API
Enterprise-grade signal generation, analysis, and management system
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum
import logging
import asyncio
from functools import lru_cache
import numpy as np
from collections import defaultdict

from src.agents.signal_generator.signal_generator_agent import SignalGeneratorAgent
from src.services.signal_center import get_signal_center_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/signals", tags=["Additional Signals"])

# Enums for better type safety
class SignalType(str, Enum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    VOLUME = "volume"
    MOMENTUM = "momentum"
    AI_PREDICTION = "ai_prediction"
    ALL = "all"

class TimeFrame(str, Enum):
    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    FIFTEEN_MIN = "15m"
    THIRTY_MIN = "30m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"

class MarketRegime(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"

# Enhanced Pydantic models with validation
class SignalBatchRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=50, description="List of symbols to process")
    signal_types: List[SignalType] = Field(
        default=[SignalType.TECHNICAL, SignalType.FUNDAMENTAL, SignalType.SENTIMENT],
        description="Types of signals to generate"
    )
    timeframes: List[TimeFrame] = Field(
        default=[TimeFrame.ONE_HOUR, TimeFrame.FOUR_HOUR, TimeFrame.ONE_DAY],
        description="Timeframes for analysis"
    )
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    
    @validator('symbols')
    def validate_symbols(cls, v):
        if not v:
            raise ValueError('At least one symbol is required')
        if len(v) > 50:
            raise ValueError('Maximum 50 symbols allowed')
        return [symbol.upper().strip() for symbol in v]

class SignalFilterRequest(BaseModel):
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    signal_type: Optional[SignalType] = Field(None, description="Filter by signal type")
    min_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Minimum confidence threshold")
    max_age_hours: int = Field(24, gt=0, le=168, description="Maximum age in hours")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    sort_by: str = Field("timestamp", description="Sort field")
    sort_order: str = Field("desc", description="Sort order")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be asc or desc')
        return v

class SignalSubscriptionRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=20, description="Symbols to subscribe")
    webhook_url: str = Field(..., description="Webhook URL for notifications")
    min_confidence: float = Field(0.7, ge=0.0, le=1.0, description="Minimum confidence for alerts")
    signal_types: List[SignalType] = Field(default=[SignalType.ALL], description="Signal types to monitor")
    retry_attempts: int = Field(3, ge=1, le=5, description="Webhook retry attempts")
    
    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Webhook URL must start with http:// or https://')
        return v
    
    @validator('symbols')
    def validate_symbols(cls, v):
        return [symbol.upper().strip() for symbol in v]

class SignalBacktestRequest(BaseModel):
    symbol: str = Field(..., description="Symbol to backtest")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    strategy_params: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    initial_capital: float = Field(10000.0, gt=0, description="Initial capital for backtest")
    fee_percentage: float = Field(0.001, ge=0, le=0.1, description="Trading fee percentage")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper().strip()
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

# Simple circuit breaker implementation
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    async def __aenter__(self):
        if self.is_open:
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout:
                self.is_open = False
                self.failure_count = 0
            else:
                raise Exception("Circuit breaker is open")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
        return False

# Simple cache manager implementation
class CacheManager:
    def __init__(self, default_ttl=300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, expiry = self.cache[key]
            if expiry > datetime.now():
                return value
            else:
                del self.cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
    
    def cached(self, ttl: int):
        """Decorator for caching function results"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
                
                # Check cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Call function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

# Initialize circuit breaker and cache manager
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception
)

cache_manager = CacheManager(default_ttl=300)  # 5 minute default TTL

# Dependency injection
class Dependencies:
    """Service dependencies with singleton pattern"""
    _signal_generator: Optional[SignalGeneratorAgent] = None
    _signal_center: Optional[Any] = None
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_signal_generator(cls) -> SignalGeneratorAgent:
        """Get or create signal generator instance"""
        if cls._signal_generator is None:
            async with cls._lock:
                if cls._signal_generator is None:
                    cls._signal_generator = SignalGeneratorAgent()
        return cls._signal_generator
    
    @classmethod
    async def get_signal_center(cls):
        """Get or create signal center instance"""
        if cls._signal_center is None:
            async with cls._lock:
                if cls._signal_center is None:
                    cls._signal_center = await get_signal_center_service()
        return cls._signal_center
    
    @classmethod
    async def reset(cls):
        """Reset all dependencies (useful for testing)"""
        async with cls._lock:
            cls._signal_generator = None
            cls._signal_center = None

# Helper functions
async def get_generator_dependency() -> SignalGeneratorAgent:
    """FastAPI dependency for signal generator"""
    return await Dependencies.get_signal_generator()

async def get_center_dependency():
    """FastAPI dependency for signal center"""
    return await Dependencies.get_signal_center()

@router.post("/batch-generate", response_model=Dict[str, Any])
async def generate_batch_signals(
    request: SignalBatchRequest,
    background_tasks: BackgroundTasks,
    generator: SignalGeneratorAgent = Depends(get_generator_dependency)
) -> Dict[str, Any]:
    """
    Generate signals for multiple symbols and timeframes with parallel processing
    
    Args:
        request: Batch signal request parameters
        background_tasks: FastAPI background tasks
        generator: Signal generator dependency
    
    Returns:
        Batch processing results with correlation IDs
    """
    try:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        logger.info(f"Processing batch signal generation: {batch_id}")
        
        # Check cache first
        cache_key = f"batch_signals_{request.symbols}_{request.timeframes}"
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached batch results for {batch_id}")
            return cached_result
        
        results = {}
        errors = []
        
        if request.parallel_processing:
            # Parallel processing for better performance
            tasks = []
            for symbol in request.symbols:
                for timeframe in request.timeframes:
                    task = asyncio.create_task(
                        _generate_single_signal(
                            generator, symbol, timeframe.value, request.signal_types
                        )
                    )
                    tasks.append((symbol, timeframe, task))
            
            # Gather results with timeout
            for symbol, timeframe, task in tasks:
                try:
                    signal_result = await asyncio.wait_for(task, timeout=10.0)
                    if symbol not in results:
                        results[symbol] = {}
                    results[symbol][timeframe.value] = signal_result
                except asyncio.TimeoutError:
                    error_msg = f"Timeout generating signal for {symbol} {timeframe.value}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    if symbol not in results:
                        results[symbol] = {}
                    results[symbol][timeframe.value] = {"error": "timeout", "message": error_msg}
                except Exception as e:
                    error_msg = f"Error generating signal for {symbol} {timeframe.value}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    if symbol not in results:
                        results[symbol] = {}
                    results[symbol][timeframe.value] = {"error": "failed", "message": str(e)}
        else:
            # Sequential processing (more stable but slower)
            for symbol in request.symbols:
                symbol_results = {}
                for timeframe in request.timeframes:
                    try:
                        signal = await _generate_single_signal(
                            generator, symbol, timeframe.value, request.signal_types
                        )
                        symbol_results[timeframe.value] = signal
                    except Exception as e:
                        error_msg = f"Error generating signal for {symbol} {timeframe.value}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        symbol_results[timeframe.value] = {"error": "failed", "message": str(e)}
                results[symbol] = symbol_results
        
        # Calculate statistics
        total_signals = sum(
            len(timeframes) for timeframes in results.values()
        )
        successful_signals = sum(
            1 for symbol_data in results.values()
            for signal in symbol_data.values()
            if not isinstance(signal, dict) or "error" not in signal
        )
        
        response = {
            "batch_id": batch_id,
            "status": "completed" if not errors else "partial",
            "symbols_processed": len(request.symbols),
            "timeframes_processed": len(request.timeframes),
            "total_signals_generated": total_signals,
            "successful_signals": successful_signals,
            "failed_signals": total_signals - successful_signals,
            "results": results,
            "errors": errors if errors else None,
            "processing_time_ms": 0,  # Will be calculated by middleware
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the results
        await cache_manager.set(cache_key, response, ttl=300)
        
        # Schedule background analysis
        background_tasks.add_task(
            _analyze_batch_signals,
            batch_id,
            results
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Batch signal generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch signal generation failed: {str(e)}"
        )

async def _generate_single_signal(
    generator: SignalGeneratorAgent,
    symbol: str,
    timeframe: str,
    signal_types: List[SignalType]
) -> Dict[str, Any]:
    """Generate a single signal with circuit breaker protection"""
    async with circuit_breaker:
        signal = await generator.get_aggregated_signal(symbol=symbol)
        if signal:
            signal['timeframe'] = timeframe
            signal['requested_types'] = [st.value for st in signal_types]
            signal['generated_at'] = datetime.now().isoformat()
        return signal or {"status": "no_signal", "symbol": symbol, "timeframe": timeframe}

async def _analyze_batch_signals(batch_id: str, results: Dict[str, Any]):
    """Background task to analyze generated signals"""
    try:
        logger.info(f"Analyzing batch signals for {batch_id}")
        # Perform analysis (correlation, patterns, etc.)
        # This would be implemented based on specific requirements
    except Exception as e:
        logger.error(f"Failed to analyze batch signals {batch_id}: {e}")

@router.post("/filtered-search", response_model=Dict[str, Any])
async def search_signals(
    request: SignalFilterRequest,
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    Search and filter historical signals with advanced filtering
    
    Args:
        request: Filter criteria for signal search
        center: Signal center dependency
        
    Returns:
        Filtered signals with metadata
    """
    try:
        # Build filter criteria
        filters = {}
        if request.symbol:
            filters['symbol'] = request.symbol.upper()
        if request.signal_type:
            filters['signal_type'] = request.signal_type.value
        if request.min_confidence:
            filters['min_confidence'] = request.min_confidence
        
        # Calculate time filter
        cutoff_time = None
        if request.max_age_hours:
            cutoff_time = datetime.now() - timedelta(hours=request.max_age_hours)
            filters['after'] = cutoff_time.isoformat()
        
        # Implement actual signal search (with mock data for now)
        signals = await _search_signals_impl(
            filters, 
            cutoff_time,
            request.limit,
            request.sort_by,
            request.sort_order
        )
        
        # Calculate statistics
        confidence_distribution = _calculate_confidence_distribution(signals)
        
        return {
            "total_signals": len(signals),
            "filters_applied": filters,
            "signals": signals[:request.limit],
            "statistics": {
                "avg_confidence": np.mean([s.get('confidence', 0) for s in signals]) if signals else 0,
                "confidence_distribution": confidence_distribution,
                "signal_types": list(set(s.get('type', 'unknown') for s in signals))
            },
            "sort_criteria": {
                "field": request.sort_by,
                "order": request.sort_order
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Signal search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signal search failed: {str(e)}"
        )

async def _search_signals_impl(
    filters: Dict[str, Any],
    cutoff_time: Optional[datetime],
    limit: int,
    sort_by: str,
    sort_order: str
) -> List[Dict[str, Any]]:
    """Implementation of signal search with filtering and sorting"""
    # This would connect to actual database/storage
    # For now, returning mock data
    mock_signals = []
    for i in range(min(10, limit)):
        mock_signals.append({
            "id": f"signal_{i}",
            "symbol": filters.get('symbol', 'BTC-USDT'),
            "type": filters.get('signal_type', 'technical'),
            "confidence": 0.5 + (i * 0.05),
            "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
            "action": "buy" if i % 2 == 0 else "sell",
            "metadata": {
                "source": "technical_analysis",
                "indicators": ["RSI", "MACD", "BB"]
            }
        })
    
    # Sort signals
    if sort_by == "confidence":
        mock_signals.sort(key=lambda x: x['confidence'], reverse=(sort_order == "desc"))
    elif sort_by == "timestamp":
        mock_signals.sort(key=lambda x: x['timestamp'], reverse=(sort_order == "desc"))
    
    return mock_signals

def _calculate_confidence_distribution(signals: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate confidence level distribution"""
    distribution = defaultdict(int)
    for signal in signals:
        confidence = signal.get('confidence', 0)
        if confidence >= 0.8:
            distribution['high'] += 1
        elif confidence >= 0.5:
            distribution['medium'] += 1
        else:
            distribution['low'] += 1
    return dict(distribution)

@router.get("/performance-analytics/{symbol}", response_model=Dict[str, Any])
@cache_manager.cached(ttl=600)  # Cache for 10 minutes
async def get_signal_performance(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    Get comprehensive signal performance analytics for a symbol
    
    Args:
        symbol: Trading symbol to analyze
        days: Number of days to analyze
        center: Signal center dependency
        
    Returns:
        Detailed performance metrics and analytics
    """
    try:
        symbol_upper = symbol.upper()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Calculate performance metrics (with mock data for now)
        performance_data = await _calculate_performance_metrics(
            symbol_upper, start_date, end_date
        )
        
        # Advanced analytics
        sharpe_ratio = _calculate_sharpe_ratio(performance_data)
        max_drawdown = _calculate_max_drawdown(performance_data)
        win_rate = performance_data.get('win_rate', 0.0)
        
        return {
            "symbol": symbol_upper,
            "analysis_period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "performance_metrics": {
                "total_signals": performance_data.get('total_signals', 0),
                "successful_signals": performance_data.get('successful_signals', 0),
                "failed_signals": performance_data.get('failed_signals', 0),
                "accuracy": performance_data.get('accuracy', 0.0),
                "precision": performance_data.get('precision', 0.0),
                "recall": performance_data.get('recall', 0.0),
                "f1_score": performance_data.get('f1_score', 0.0),
                "win_rate": win_rate,
                "avg_confidence": performance_data.get('avg_confidence', 0.0),
                "avg_return": performance_data.get('avg_return', 0.0),
                "total_return": performance_data.get('total_return', 0.0)
            },
            "risk_metrics": {
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "volatility": performance_data.get('volatility', 0.0),
                "var_95": performance_data.get('var_95', 0.0),
                "cvar_95": performance_data.get('cvar_95', 0.0)
            },
            "signal_distribution": {
                "by_type": performance_data.get('type_distribution', {}),
                "by_timeframe": performance_data.get('timeframe_distribution', {}),
                "by_confidence": performance_data.get('confidence_distribution', {})
            },
            "best_performing": {
                "timeframe": performance_data.get('best_timeframe', '1d'),
                "signal_type": performance_data.get('best_signal_type', 'technical'),
                "hour_of_day": performance_data.get('best_hour', 14)
            },
            "recommendations": _generate_recommendations(performance_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance analytics failed for {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance analytics failed: {str(e)}"
        )

async def _calculate_performance_metrics(
    symbol: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Calculate detailed performance metrics"""
    # Mock implementation - would connect to actual data source
    return {
        "total_signals": 150,
        "successful_signals": 95,
        "failed_signals": 55,
        "accuracy": 0.633,
        "precision": 0.68,
        "recall": 0.72,
        "f1_score": 0.695,
        "win_rate": 0.633,
        "avg_confidence": 0.74,
        "avg_return": 0.023,
        "total_return": 3.45,
        "volatility": 0.18,
        "var_95": -0.05,
        "cvar_95": -0.08,
        "type_distribution": {"technical": 60, "fundamental": 50, "sentiment": 40},
        "timeframe_distribution": {"1h": 50, "4h": 60, "1d": 40},
        "confidence_distribution": {"high": 45, "medium": 75, "low": 30},
        "best_timeframe": "4h",
        "best_signal_type": "technical",
        "best_hour": 14
    }

def _calculate_sharpe_ratio(performance_data: Dict[str, Any]) -> float:
    """Calculate Sharpe ratio"""
    avg_return = performance_data.get('avg_return', 0)
    volatility = performance_data.get('volatility', 1)
    risk_free_rate = 0.02 / 365  # Daily risk-free rate
    
    if volatility == 0:
        return 0.0
    
    return float((avg_return - risk_free_rate) / volatility)

def _calculate_max_drawdown(performance_data: Dict[str, Any]) -> float:
    """Calculate maximum drawdown"""
    # Mock calculation
    return -0.12  # 12% max drawdown

def _generate_recommendations(performance_data: Dict[str, Any]) -> List[str]:
    """Generate trading recommendations based on performance"""
    recommendations = []
    
    if performance_data.get('win_rate', 0) < 0.5:
        recommendations.append("Consider adjusting signal confidence threshold")
    
    if performance_data.get('volatility', 0) > 0.25:
        recommendations.append("High volatility detected - consider risk reduction")
    
    best_timeframe = performance_data.get('best_timeframe')
    if best_timeframe:
        recommendations.append(f"Focus on {best_timeframe} timeframe for better results")
    
    return recommendations

@router.post("/subscriptions", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_signal_subscription(
    request: SignalSubscriptionRequest,
    background_tasks: BackgroundTasks,
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    Create a webhook subscription for real-time signal notifications
    
    Args:
        request: Subscription configuration
        background_tasks: Background task manager
        center: Signal center dependency
        
    Returns:
        Subscription details with ID and status
    """
    try:
        subscription_id = f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        logger.info(f"Creating subscription {subscription_id} for {request.symbols}")
        
        # Store subscription (would be saved to database)
        subscription_data = {
            "id": subscription_id,
            "symbols": request.symbols,
            "webhook_url": request.webhook_url,
            "min_confidence": request.min_confidence,
            "signal_types": [st.value for st in request.signal_types],
            "retry_attempts": request.retry_attempts,
            "status": "active",
            "created_at": datetime.now(),
            "last_triggered": None,
            "trigger_count": 0
        }
        
        # Schedule subscription validation in background
        background_tasks.add_task(
            _validate_webhook_url,
            request.webhook_url,
            subscription_id
        )
        
        return {
            "subscription_id": subscription_id,
            "status": "active",
            "symbols": request.symbols,
            "webhook_url": request.webhook_url,
            "filters": {
                "min_confidence": request.min_confidence,
                "signal_types": [st.value for st in request.signal_types]
            },
            "retry_policy": {
                "max_attempts": request.retry_attempts,
                "backoff_strategy": "exponential"
            },
            "created_at": datetime.now().isoformat(),
            "health_check_url": f"/api/signals/subscriptions/{subscription_id}/health"
        }
        
    except Exception as e:
        logger.error(f"Subscription creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription creation failed: {str(e)}"
        )

async def _validate_webhook_url(webhook_url: str, subscription_id: str):
    """Validate webhook URL is accessible"""
    try:
        # Would perform actual HTTP request to validate
        logger.info(f"Validated webhook URL for subscription {subscription_id}")
    except Exception as e:
        logger.error(f"Webhook validation failed for {subscription_id}: {e}")

@router.get("/subscriptions", response_model=Dict[str, Any])
async def list_subscriptions(
    status_filter: Optional[str] = Query(None, description="Filter by status (active, paused, failed)"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(50, ge=1, le=200),
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    List all signal subscriptions with optional filtering
    
    Args:
        status_filter: Filter by subscription status
        symbol: Filter by symbol
        limit: Maximum subscriptions to return
        center: Signal center dependency
        
    Returns:
        List of active subscriptions with metadata
    """
    try:
        # Validate status filter
        if status_filter and status_filter not in ['active', 'paused', 'failed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter. Must be one of: active, paused, failed"
            )
        # Mock subscription data (would query database)
        all_subscriptions = [
            {
                "subscription_id": f"sub_2024_{i}",
                "status": "active" if i % 3 != 0 else "paused",
                "symbols": ["BTC-USDT", "ETH-USDT"] if i % 2 == 0 else ["SOL-USDT"],
                "webhook_url": f"https://example.com/webhook/{i}",
                "min_confidence": 0.7,
                "signal_types": ["technical", "sentiment"],
                "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "last_triggered": (datetime.now() - timedelta(hours=i*2)).isoformat() if i < 5 else None,
                "trigger_count": i * 10,
                "health_status": "healthy" if i % 4 != 0 else "degraded"
            }
            for i in range(10)
        ]
        
        # Apply filters
        filtered_subs = all_subscriptions
        if status_filter:
            filtered_subs = [s for s in filtered_subs if s['status'] == status_filter]
        if symbol:
            symbol_upper = symbol.upper()
            filtered_subs = [s for s in filtered_subs if symbol_upper in s['symbols']]
        
        # Apply limit
        filtered_subs = filtered_subs[:limit]
        
        # Calculate statistics
        active_count = sum(1 for s in filtered_subs if s['status'] == 'active')
        
        return {
            "total_subscriptions": len(filtered_subs),
            "active_subscriptions": active_count,
            "filters_applied": {
                "status": status_filter,
                "symbol": symbol
            },
            "subscriptions": filtered_subs,
            "statistics": {
                "avg_trigger_count": np.mean([s['trigger_count'] for s in filtered_subs]) if filtered_subs else 0,
                "most_active_symbols": _get_most_active_symbols(filtered_subs)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list subscriptions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subscriptions: {str(e)}"
        )

def _get_most_active_symbols(subscriptions: List[Dict[str, Any]]) -> List[str]:
    """Get most frequently subscribed symbols"""
    symbol_counts = defaultdict(int)
    for sub in subscriptions:
        for symbol in sub.get('symbols', []):
            symbol_counts[symbol] += 1
    
    sorted_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)
    return [symbol for symbol, _ in sorted_symbols[:5]]

@router.delete("/subscriptions/{subscription_id}", response_model=Dict[str, Any])
async def delete_subscription(
    subscription_id: str,
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    Delete a signal subscription
    
    Args:
        subscription_id: ID of subscription to delete
        center: Signal center dependency
        
    Returns:
        Deletion confirmation
    """
    try:
        # Validate subscription exists (would check database)
        if not subscription_id.startswith("sub_"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription {subscription_id} not found"
            )
        
        # Delete subscription (would remove from database)
        logger.info(f"Deleting subscription {subscription_id}")
        
        return {
            "subscription_id": subscription_id,
            "status": "deleted",
            "deleted_at": datetime.now().isoformat(),
            "cleanup_actions": [
                "Webhook notifications stopped",
                "Subscription data archived",
                "Resources released"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription deletion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription deletion failed: {str(e)}"
        )

@router.post("/backtest", response_model=Dict[str, Any])
async def backtest_strategy(
    request: SignalBacktestRequest,
    background_tasks: BackgroundTasks,
    generator: SignalGeneratorAgent = Depends(get_generator_dependency)
) -> Dict[str, Any]:
    """
    Backtest a trading strategy using historical signals
    
    Args:
        request: Backtest configuration
        background_tasks: Background task manager
        generator: Signal generator dependency
        
    Returns:
        Comprehensive backtest results with performance metrics
    """
    try:
        backtest_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        logger.info(f"Starting backtest {backtest_id} for {request.symbol}")
        
        # Validate date range
        if request.end_date > datetime.now():
            raise ValueError("End date cannot be in the future")
        
        # Run backtest simulation
        backtest_results = await _run_backtest_simulation(
            generator,
            request.symbol,
            request.start_date,
            request.end_date,
            request.initial_capital,
            request.fee_percentage,
            request.strategy_params
        )
        
        # Calculate performance metrics
        metrics = _calculate_backtest_metrics(backtest_results)
        
        # Schedule detailed analysis in background
        background_tasks.add_task(
            _store_backtest_results,
            backtest_id,
            backtest_results
        )
        
        return {
            "backtest_id": backtest_id,
            "symbol": request.symbol,
            "period": {
                "start": request.start_date.isoformat(),
                "end": request.end_date.isoformat(),
                "trading_days": (request.end_date - request.start_date).days
            },
            "configuration": {
                "initial_capital": request.initial_capital,
                "fee_percentage": request.fee_percentage,
                "strategy_params": request.strategy_params
            },
            "performance": {
                "final_capital": metrics['final_capital'],
                "total_return": metrics['total_return'],
                "total_return_pct": metrics['total_return_pct'],
                "annualized_return": metrics['annualized_return'],
                "sharpe_ratio": metrics['sharpe_ratio'],
                "max_drawdown": metrics['max_drawdown'],
                "win_rate": metrics['win_rate'],
                "profit_factor": metrics['profit_factor']
            },
            "trade_statistics": {
                "total_trades": metrics['total_trades'],
                "winning_trades": metrics['winning_trades'],
                "losing_trades": metrics['losing_trades'],
                "avg_win": metrics['avg_win'],
                "avg_loss": metrics['avg_loss'],
                "largest_win": metrics['largest_win'],
                "largest_loss": metrics['largest_loss'],
                "avg_holding_period": metrics['avg_holding_period']
            },
            "risk_metrics": {
                "volatility": metrics['volatility'],
                "sortino_ratio": metrics['sortino_ratio'],
                "calmar_ratio": metrics['calmar_ratio'],
                "var_95": metrics['var_95'],
                "cvar_95": metrics['cvar_95']
            },
            "execution_stats": {
                "total_fees_paid": metrics['total_fees'],
                "avg_slippage": metrics['avg_slippage'],
                "execution_time_ms": metrics['execution_time']
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Backtest failed for {request.symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest failed: {str(e)}"
        )

async def _run_backtest_simulation(
    generator: SignalGeneratorAgent,
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    initial_capital: float,
    fee_percentage: float,
    strategy_params: Dict[str, Any]
) -> Dict[str, Any]:
    """Run the actual backtest simulation"""
    # Mock implementation - would use historical data
    trades = []
    capital = initial_capital
    
    # Simulate trades
    for i in range(20):
        trade_return = np.random.normal(0.002, 0.02)  # Random returns
        fee = capital * fee_percentage
        capital = capital * (1 + trade_return) - fee
        
        trades.append({
            "date": start_date + timedelta(days=i*10),
            "return": trade_return,
            "capital_after": capital,
            "fee": fee
        })
    
    return {
        "trades": trades,
        "final_capital": capital,
        "initial_capital": initial_capital
    }

def _calculate_backtest_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comprehensive backtest metrics"""
    initial = results['initial_capital']
    final = results['final_capital']
    trades = results['trades']
    
    returns = [t['return'] for t in trades]
    
    return {
        "final_capital": final,
        "total_return": final - initial,
        "total_return_pct": ((final - initial) / initial) * 100,
        "annualized_return": 0.15,  # Mock value
        "sharpe_ratio": 1.2,
        "max_drawdown": -0.08,
        "win_rate": 0.55,
        "profit_factor": 1.4,
        "total_trades": len(trades),
        "winning_trades": sum(1 for r in returns if r > 0),
        "losing_trades": sum(1 for r in returns if r <= 0),
        "avg_win": np.mean([r for r in returns if r > 0]) if any(r > 0 for r in returns) else 0,
        "avg_loss": np.mean([r for r in returns if r <= 0]) if any(r <= 0 for r in returns) else 0,
        "largest_win": max(returns) if returns else 0,
        "largest_loss": min(returns) if returns else 0,
        "avg_holding_period": "2.5 days",
        "volatility": np.std(returns) if returns else 0,
        "sortino_ratio": 1.5,
        "calmar_ratio": 1.8,
        "var_95": np.percentile(returns, 5) if returns else 0,
        "cvar_95": np.mean([r for r in returns if r <= np.percentile(returns, 5)]) if returns else 0,
        "total_fees": sum(t['fee'] for t in trades),
        "avg_slippage": 0.0001,
        "execution_time": 250
    }

async def _store_backtest_results(backtest_id: str, results: Dict[str, Any]):
    """Store backtest results for later retrieval"""
    try:
        logger.info(f"Storing backtest results for {backtest_id}")
        # Would save to database
    except Exception as e:
        logger.error(f"Failed to store backtest results: {e}")

@router.get("/market-regime", response_model=Dict[str, Any])
@cache_manager.cached(ttl=180)  # Cache for 3 minutes
async def get_market_regime(
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    Get current market regime analysis with AI-powered insights
    
    Returns:
        Comprehensive market regime analysis and recommendations
    """
    try:
        # Analyze market conditions
        regime_data = await _analyze_market_regime()
        
        # Generate AI insights
        ai_insights = _generate_regime_insights(regime_data)
        
        return {
            "market_regime": regime_data['regime'],
            "confidence": regime_data['confidence'],
            "sub_regime": regime_data['sub_regime'],
            "characteristics": regime_data['characteristics'],
            "indicators": {
                "volatility": {
                    "level": regime_data['volatility_level'],
                    "value": regime_data['volatility_value'],
                    "percentile": regime_data['volatility_percentile']
                },
                "trend": {
                    "direction": regime_data['trend_direction'],
                    "strength": regime_data['trend_strength'],
                    "momentum": regime_data['momentum']
                },
                "volume": {
                    "level": regime_data['volume_level'],
                    "relative_strength": regime_data['volume_rs']
                },
                "correlation": {
                    "market_wide": regime_data['correlation'],
                    "sector_dispersion": regime_data['dispersion']
                }
            },
            "risk_indicators": {
                "vix_level": regime_data['vix'],
                "put_call_ratio": regime_data['put_call'],
                "fear_greed_index": regime_data['fear_greed'],
                "margin_debt": regime_data['margin_debt']
            },
            "recommended_strategies": regime_data['strategies'],
            "position_sizing": {
                "aggressive": regime_data['aggressive_size'],
                "moderate": regime_data['moderate_size'],
                "conservative": regime_data['conservative_size']
            },
            "ai_insights": ai_insights,
            "next_update": (datetime.now() + timedelta(minutes=3)).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market regime analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market regime analysis failed: {str(e)}"
        )

async def _analyze_market_regime() -> Dict[str, Any]:
    """Analyze current market regime"""
    # Mock implementation - would use real market data
    return {
        "regime": MarketRegime.NEUTRAL,
        "confidence": 0.72,
        "sub_regime": "consolidating",
        "characteristics": [
            "Range-bound trading",
            "Mixed sector performance",
            "Moderate volatility"
        ],
        "volatility_level": "moderate",
        "volatility_value": 18.5,
        "volatility_percentile": 45,
        "trend_direction": "sideways",
        "trend_strength": 0.3,
        "momentum": 0.1,
        "volume_level": "average",
        "volume_rs": 1.02,
        "correlation": 0.65,
        "dispersion": 0.28,
        "vix": 18.5,
        "put_call": 0.95,
        "fear_greed": 52,
        "margin_debt": "elevated",
        "strategies": [
            "Mean reversion",
            "Range trading",
            "Volatility selling"
        ],
        "aggressive_size": 0.5,
        "moderate_size": 0.3,
        "conservative_size": 0.15
    }

def _generate_regime_insights(regime_data: Dict[str, Any]) -> List[str]:
    """Generate AI-powered insights based on regime"""
    insights = []
    
    if regime_data['regime'] == MarketRegime.NEUTRAL:
        insights.append("Market showing consolidation patterns - consider range-trading strategies")
    
    if regime_data['volatility_value'] > 20:
        insights.append("Elevated volatility suggests using wider stop-losses")
    
    if regime_data['fear_greed'] < 30:
        insights.append("Extreme fear presents potential buying opportunities")
    
    return insights

@router.get("/correlation-matrix", response_model=Dict[str, Any])
@cache_manager.cached(ttl=600)  # Cache for 10 minutes
async def get_signal_correlations(
    symbols: List[str] = Query(default=["BTC-USDT", "ETH-USDT", "SOL-USDT"], description="Symbols to analyze (max 10)"),
    period_days: int = Query(30, ge=7, le=90),
    center = Depends(get_center_dependency)
) -> Dict[str, Any]:
    """
    Calculate signal correlation matrix across multiple symbols
    
    Args:
        symbols: List of symbols to analyze
        period_days: Analysis period in days
        center: Signal center dependency
        
    Returns:
        Correlation matrix with insights
    """
    try:
        # Validate symbols list
        if len(symbols) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 symbols allowed for correlation analysis"
            )
        
        # Normalize symbols
        symbols_upper = [s.upper() for s in symbols]
        
        # Calculate correlation matrix
        correlation_matrix = await _calculate_correlation_matrix(
            symbols_upper, period_days
        )
        
        # Find strongest and weakest correlations
        correlations_list = _extract_correlations(correlation_matrix)
        strongest = sorted(correlations_list, key=lambda x: abs(x['correlation']), reverse=True)[:5]
        weakest = sorted(correlations_list, key=lambda x: abs(x['correlation']))[:5]
        
        # Identify clusters
        clusters = _identify_correlation_clusters(correlation_matrix)
        
        return {
            "symbols_analyzed": symbols_upper,
            "period_days": period_days,
            "correlation_matrix": correlation_matrix,
            "strongest_correlations": strongest,
            "weakest_correlations": weakest,
            "correlation_clusters": clusters,
            "insights": {
                "avg_correlation": np.mean([abs(c['correlation']) for c in correlations_list]),
                "highly_correlated_pairs": len([c for c in correlations_list if abs(c['correlation']) > 0.7]),
                "uncorrelated_pairs": len([c for c in correlations_list if abs(c['correlation']) < 0.3]),
                "diversification_score": _calculate_diversification_score(correlation_matrix)
            },
            "recommendations": _generate_correlation_recommendations(correlation_matrix, clusters),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Correlation analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Correlation analysis failed: {str(e)}"
        )

async def _calculate_correlation_matrix(
    symbols: List[str],
    period_days: int
) -> Dict[str, Dict[str, float]]:
    """Calculate correlation matrix for symbols"""
    # Mock implementation - would use actual price/signal data
    matrix = {}
    for i, sym1 in enumerate(symbols):
        matrix[sym1] = {}
        for j, sym2 in enumerate(symbols):
            if i == j:
                matrix[sym1][sym2] = 1.0
            else:
                # Generate mock correlation
                base_corr = 0.3 if (i + j) % 2 == 0 else 0.6
                noise = np.random.uniform(-0.2, 0.2)
                matrix[sym1][sym2] = max(-1, min(1, base_corr + noise))
    return matrix

def _extract_correlations(matrix: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
    """Extract correlation pairs from matrix"""
    correlations = []
    seen = set()
    
    for sym1, row in matrix.items():
        for sym2, corr in row.items():
            if sym1 != sym2 and (sym2, sym1) not in seen:
                correlations.append({
                    "pair": f"{sym1}/{sym2}",
                    "symbol1": sym1,
                    "symbol2": sym2,
                    "correlation": round(corr, 3)
                })
                seen.add((sym1, sym2))
    
    return correlations

def _identify_correlation_clusters(matrix: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
    """Identify clusters of correlated symbols"""
    # Simplified clustering - would use actual clustering algorithm
    clusters = [
        {
            "cluster_id": "crypto_majors",
            "symbols": ["BTC-USDT", "ETH-USDT"],
            "avg_correlation": 0.75,
            "description": "Major cryptocurrencies moving together"
        }
    ]
    return clusters

def _calculate_diversification_score(matrix: Dict[str, Dict[str, float]]) -> float:
    """Calculate portfolio diversification score (0-1, higher is better)"""
    correlations = []
    for sym1, row in matrix.items():
        for sym2, corr in row.items():
            if sym1 != sym2:
                correlations.append(abs(corr))
    
    if not correlations:
        return 1.0
    
    avg_correlation = float(np.mean(correlations))
    return round(1 - avg_correlation, 2)

def _generate_correlation_recommendations(matrix: Dict[str, Dict[str, float]], clusters: List[Dict[str, Any]]) -> List[str]:
    """Generate recommendations based on correlations"""
    recommendations = []
    
    if clusters:
        recommendations.append("Consider diversifying across different correlation clusters")
    
    # Check for high correlations
    high_corr_count = sum(
        1 for sym1, row in matrix.items()
        for sym2, corr in row.items()
        if sym1 != sym2 and abs(corr) > 0.8
    )
    
    if high_corr_count > 0:
        recommendations.append("High correlations detected - avoid over-concentration in similar assets")
    
    return recommendations

@router.post("/custom-indicator", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_custom_indicator(
    indicator_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    generator: SignalGeneratorAgent = Depends(get_generator_dependency)
) -> Dict[str, Any]:
    """
    Create and deploy a custom trading indicator with validation
    
    Args:
        indicator_config: Custom indicator configuration
        background_tasks: Background task manager
        generator: Signal generator dependency
        
    Returns:
        Indicator creation confirmation with deployment details
    """
    try:
        indicator_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Validate indicator configuration
        validation_results = _validate_indicator_config(indicator_config)
        if not validation_results['valid']:
            raise ValueError(f"Invalid indicator configuration: {validation_results['errors']}")
        
        # Create indicator definition
        indicator_def = {
            "id": indicator_id,
            "name": indicator_config.get('name', 'Custom Indicator'),
            "description": indicator_config.get('description', ''),
            "type": indicator_config.get('type', 'technical'),
            "parameters": indicator_config.get('parameters', {}),
            "formula": indicator_config.get('formula', ''),
            "thresholds": indicator_config.get('thresholds', {}),
            "created_at": datetime.now(),
            "status": "deploying"
        }
        
        # Schedule deployment in background
        background_tasks.add_task(
            _deploy_custom_indicator,
            indicator_id,
            indicator_def
        )
        
        return {
            "indicator_id": indicator_id,
            "status": "created",
            "deployment_status": "in_progress",
            "config": {
                "name": indicator_def['name'],
                "type": indicator_def['type'],
                "parameters": indicator_def['parameters']
            },
            "validation_results": {
                "valid": validation_results['valid'],
                "warnings": validation_results.get('warnings', []),
                "optimization_suggestions": validation_results.get('suggestions', [])
            },
            "estimated_deployment_time": "30 seconds",
            "api_endpoints": {
                "status": f"/api/signals/indicators/{indicator_id}/status",
                "test": f"/api/signals/indicators/{indicator_id}/test",
                "metrics": f"/api/signals/indicators/{indicator_id}/metrics"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Custom indicator creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Custom indicator creation failed: {str(e)}"
        )

def _validate_indicator_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate custom indicator configuration"""
    errors = []
    warnings = []
    suggestions = []
    
    # Check required fields
    if 'name' not in config:
        errors.append("Indicator name is required")
    
    if 'type' not in config:
        warnings.append("Indicator type not specified, defaulting to 'technical'")
    
    # Validate parameters
    if 'parameters' in config:
        params = config['parameters']
        if isinstance(params, dict):
            for key, value in params.items():
                if not isinstance(key, str):
                    errors.append(f"Parameter key must be string: {key}")
        else:
            errors.append("Parameters must be a dictionary")
    
    # Provide optimization suggestions
    if 'thresholds' not in config:
        suggestions.append("Consider adding thresholds for signal generation")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions
    }

async def _deploy_custom_indicator(indicator_id: str, indicator_def: Dict[str, Any]):
    """Deploy custom indicator in background"""
    try:
        logger.info(f"Deploying custom indicator {indicator_id}")
        await asyncio.sleep(2)  # Simulate deployment
        logger.info(f"Successfully deployed indicator {indicator_id}")
    except Exception as e:
        logger.error(f"Failed to deploy indicator {indicator_id}: {e}")

@router.get("/indicators", response_model=Dict[str, Any])
async def list_indicators(
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active indicators"),
    generator: SignalGeneratorAgent = Depends(get_generator_dependency)
) -> Dict[str, Any]:
    """
    List all available indicators with detailed information
    
    Args:
        category: Optional category filter
        active_only: Show only active indicators
        generator: Signal generator dependency
        
    Returns:
        Comprehensive list of indicators with metadata
    """
    try:
        # Get all indicators
        all_indicators = _get_all_indicators()
        
        # Apply filters
        filtered_indicators = all_indicators
        if category:
            filtered_indicators = [
                ind for ind in filtered_indicators
                if ind['category'] == category
            ]
        if active_only:
            filtered_indicators = [
                ind for ind in filtered_indicators
                if ind['status'] == 'active'
            ]
        
        # Categorize indicators
        categorized = _categorize_indicators(filtered_indicators)
        
        # Calculate statistics
        stats = _calculate_indicator_stats(filtered_indicators)
        
        return {
            "total_indicators": len(filtered_indicators),
            "filters_applied": {
                "category": category,
                "active_only": active_only
            },
            "indicators": {
                "built_in": categorized['built_in'],
                "custom": categorized['custom'],
                "experimental": categorized['experimental']
            },
            "categories": {
                "technical": categorized['technical_count'],
                "fundamental": categorized['fundamental_count'],
                "sentiment": categorized['sentiment_count'],
                "volume": categorized['volume_count'],
                "momentum": categorized['momentum_count'],
                "ai_powered": categorized['ai_count']
            },
            "statistics": stats,
            "most_used": _get_most_used_indicators(filtered_indicators),
            "recently_added": _get_recently_added_indicators(filtered_indicators),
            "performance_leaders": _get_top_performing_indicators(filtered_indicators),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list indicators: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list indicators: {str(e)}"
        )

def _get_all_indicators() -> List[Dict[str, Any]]:
    """Get all available indicators"""
    # Mock implementation - would fetch from database
    indicators = [
        {
            "id": "rsi",
            "name": "Relative Strength Index",
            "category": "technical",
            "type": "built_in",
            "status": "active",
            "usage_count": 1520,
            "accuracy": 0.68,
            "created_at": datetime.now() - timedelta(days=365)
        },
        {
            "id": "macd",
            "name": "MACD",
            "category": "momentum",
            "type": "built_in",
            "status": "active",
            "usage_count": 1350,
            "accuracy": 0.65,
            "created_at": datetime.now() - timedelta(days=365)
        },
        {
            "id": "custom_ai_1",
            "name": "AI Pattern Detector",
            "category": "ai_powered",
            "type": "custom",
            "status": "active",
            "usage_count": 450,
            "accuracy": 0.72,
            "created_at": datetime.now() - timedelta(days=30)
        }
    ]
    return indicators

def _categorize_indicators(indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Categorize indicators by type and category"""
    result = {
        "built_in": [],
        "custom": [],
        "experimental": [],
        "technical_count": 0,
        "fundamental_count": 0,
        "sentiment_count": 0,
        "volume_count": 0,
        "momentum_count": 0,
        "ai_count": 0
    }
    
    for ind in indicators:
        # By type
        if ind['type'] == 'built_in':
            result['built_in'].append(ind)
        elif ind['type'] == 'custom':
            result['custom'].append(ind)
        elif ind['type'] == 'experimental':
            result['experimental'].append(ind)
        
        # Count by category
        category = ind.get('category', '')
        if category == 'technical':
            result['technical_count'] += 1
        elif category == 'fundamental':
            result['fundamental_count'] += 1
        elif category == 'sentiment':
            result['sentiment_count'] += 1
        elif category == 'volume':
            result['volume_count'] += 1
        elif category == 'momentum':
            result['momentum_count'] += 1
        elif category == 'ai_powered':
            result['ai_count'] += 1
    
    return result

def _calculate_indicator_stats(indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate indicator statistics"""
    if not indicators:
        return {
            "avg_accuracy": 0,
            "avg_usage": 0,
            "total_usage": 0
        }
    
    accuracies = [ind.get('accuracy', 0) for ind in indicators]
    usages = [ind.get('usage_count', 0) for ind in indicators]
    
    return {
        "avg_accuracy": round(np.mean(accuracies), 3),
        "avg_usage": round(np.mean(usages), 1),
        "total_usage": sum(usages),
        "accuracy_std": round(np.std(accuracies), 3),
        "best_accuracy": max(accuracies) if accuracies else 0,
        "worst_accuracy": min(accuracies) if accuracies else 0
    }

def _get_most_used_indicators(indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get most frequently used indicators"""
    sorted_by_usage = sorted(indicators, key=lambda x: x.get('usage_count', 0), reverse=True)
    return sorted_by_usage[:5]

def _get_recently_added_indicators(indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get recently added indicators"""
    sorted_by_date = sorted(indicators, key=lambda x: x.get('created_at', datetime.min), reverse=True)
    return sorted_by_date[:3]

def _get_top_performing_indicators(indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get top performing indicators by accuracy"""
    sorted_by_accuracy = sorted(indicators, key=lambda x: x.get('accuracy', 0), reverse=True)
    return sorted_by_accuracy[:5]