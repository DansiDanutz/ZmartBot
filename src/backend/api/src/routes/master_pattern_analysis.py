#!/usr/bin/env python3
"""
Master Pattern Analysis Routes
API endpoints for comprehensive pattern analysis
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
import asyncio

from ..agents.pattern_analysis.master_pattern_agent import master_pattern_agent
from ..services.market_data_service import market_data_service
# Services will be initialized as needed
cryptometer_service = None  # Will be initialized when needed
kingfisher_service = None  # Will be initialized when needed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pattern-analysis", tags=["Pattern Analysis"])

@router.get("/analyze/{symbol}")
async def analyze_patterns(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe for analysis (1m, 5m, 15m, 1h, 4h, 1d)"),
    lookback_periods: int = Query(100, description="Number of periods to analyze"),
    include_volume: bool = Query(True, description="Include volume profile analysis"),
    include_liquidation: bool = Query(True, description="Include liquidation data"),
    include_indicators: bool = Query(True, description="Include technical indicators")
) -> Dict[str, Any]:
    """
    Perform comprehensive pattern analysis for a symbol
    
    Returns detailed pattern detection results including:
    - Complex patterns (harmonic, Elliott waves, Wyckoff, etc.)
    - Pattern clusters and confluence
    - Trading signals and confidence levels
    - Risk assessment and position sizing
    - Historical pattern performance
    """
    try:
        logger.info(f"🔍 Starting pattern analysis for {symbol}")
        
        # Fetch price data
        # Note: get_ohlcv method needs to be implemented or use get_historical_data
        if market_data_service and hasattr(market_data_service, 'get_historical_data'):
            historical_data = await market_data_service.get_historical_data(
                symbol=symbol,
                days=lookback_periods
            )
            price_data = historical_data
        else:
            price_data = []  # Fallback
        
        # Original call (commented for reference):
        # price_data = await market_data_service.get_ohlcv(
        #     symbol=symbol,
        #     timeframe=timeframe,
        #     limit=lookback_periods
        # )
        
        if not price_data or len(price_data) < 20:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient price data for {symbol}"
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(price_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Fetch additional data if requested
        volume_data = None
        liquidation_data = None
        technical_indicators = None
        
        if include_volume:
            try:
                volume_data = df[['volume']].copy()
            except:
                logger.warning("Volume data not available")
        
        if include_liquidation:
            try:
                # Fetch liquidation data from KingFisher
                liquidation_response = {}
                if kingfisher_service and hasattr(kingfisher_service, 'analyze_liquidations'):
                    liquidation_response = await kingfisher_service.analyze_liquidations(symbol)  # type: ignore
                if liquidation_response.get('success'):
                    liquidation_data = liquidation_response.get('data', {})
            except Exception as e:
                logger.warning(f"Could not fetch liquidation data: {e}")
        
        if include_indicators:
            try:
                # Calculate technical indicators
                technical_indicators = await _calculate_technical_indicators(df)
            except Exception as e:
                logger.warning(f"Could not calculate indicators: {e}")
        
        # Perform pattern analysis
        analysis = await master_pattern_agent.analyze(
            symbol=symbol,
            price_data=df,
            volume_data=volume_data,
            liquidation_data=liquidation_data,
            technical_indicators=technical_indicators,
            risk_metrics=None  # Can be added if needed
        )
        
        # Format response
        response = {
            "success": True,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "pattern_score": analysis.pattern_score,
                "trade_signal": analysis.trade_signal,
                "confidence_level": analysis.confidence_level,
                "detected_patterns": [
                    {
                        "name": p.pattern_name,
                        "category": p.category.value,
                        "strength": p.strength.value,
                        "confidence": p.confidence,
                        "direction": p.direction,
                        "time_horizon": p.time_horizon.value,
                        "entry_price": p.entry_price,
                        "stop_loss": p.stop_loss,
                        "take_profit_targets": p.take_profit_targets,
                        "risk_reward_ratio": p.risk_reward_ratio,
                        "historical_win_rate": p.historical_win_rate,
                        "notes": p.notes
                    }
                    for p in analysis.detected_patterns
                ],
                "pattern_clusters": [
                    {
                        "cluster_id": c.cluster_id,
                        "pattern_count": len(c.patterns),
                        "cluster_strength": c.cluster_strength,
                        "cluster_direction": c.cluster_direction,
                        "synergy_score": c.synergy_score
                    }
                    for c in analysis.pattern_clusters
                ],
                "risk_assessment": {
                    "risk_score": analysis.pattern_risk_score,
                    "conflicting_patterns": analysis.conflicting_patterns,
                    "uncertainty_level": analysis.uncertainty_level
                },
                "position_management": {
                    "suggested_size": analysis.suggested_position_size,
                    "max_risk": analysis.max_risk_per_trade,
                    "scaling_strategy": analysis.scaling_strategy
                },
                "timing": {
                    "entry_window_start": analysis.optimal_entry_window[0].isoformat(),
                    "entry_window_end": analysis.optimal_entry_window[1].isoformat(),
                    "pattern_validity_hours": analysis.pattern_validity_period.total_seconds() / 3600
                },
                "reports": {
                    "technical_analysis": analysis.technical_analysis,
                    "pattern_narrative": analysis.pattern_narrative,
                    "risk_assessment": analysis.risk_assessment
                },
                "historical_performance": analysis.historical_performance
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in pattern analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pattern analysis failed: {str(e)}"
        )

@router.get("/patterns/realtime/{symbol}")
async def get_realtime_patterns(
    symbol: str,
    sensitivity: str = Query("medium", description="Pattern detection sensitivity (low, medium, high)")
) -> Dict[str, Any]:
    """
    Get real-time pattern alerts for a symbol
    
    Monitors for immediate pattern formations and breakouts
    """
    try:
        logger.info(f"⚡ Getting real-time patterns for {symbol}")
        
        # Adjust sensitivity thresholds
        confidence_threshold = {
            "low": 0.75,
            "medium": 0.65,
            "high": 0.55
        }.get(sensitivity, 0.65)
        
        # Get recent price data
        if market_data_service and hasattr(market_data_service, 'get_historical_data'):
            price_data = await market_data_service.get_historical_data(
                symbol=symbol,
                days=1  # 1 day for 5m data
            )
        else:
            price_data = []
        
        if not price_data:
            raise HTTPException(
                status_code=400,
                detail=f"No price data available for {symbol}"
            )
        
        df = pd.DataFrame(price_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Quick pattern scan
        analysis = await master_pattern_agent.analyze(
            symbol=symbol,
            price_data=df,
            volume_data=df[['volume']].copy() if 'volume' in df else None
        )
        
        # Filter for immediate patterns only
        immediate_patterns = [
            p for p in analysis.detected_patterns
            if p.confidence >= confidence_threshold and p.time_horizon.value == "immediate"
        ]
        
        alerts = []
        for pattern in immediate_patterns:
            alerts.append({
                "pattern": pattern.pattern_name,
                "direction": pattern.direction.upper(),
                "confidence": f"{pattern.confidence:.1%}",
                "entry": pattern.entry_price,
                "stop_loss": pattern.stop_loss,
                "targets": pattern.take_profit_targets,
                "urgency": "HIGH" if pattern.confidence > 0.8 else "MEDIUM",
                "message": f"🚨 {pattern.pattern_name} detected! {pattern.direction.upper()} signal with {pattern.confidence:.1%} confidence"
            })
        
        return {
            "success": True,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "summary": {
                "total_patterns": len(immediate_patterns),
                "strongest_signal": alerts[0] if alerts else None,
                "overall_bias": _determine_bias(immediate_patterns)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting realtime patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Realtime pattern detection failed: {str(e)}"
        )

@router.get("/patterns/backtest/{symbol}")
async def backtest_patterns(
    symbol: str,
    pattern_type: Optional[str] = Query(None, description="Specific pattern to backtest"),
    lookback_days: int = Query(30, description="Days to look back for backtesting"),
    min_confidence: float = Query(0.6, description="Minimum pattern confidence")
) -> Dict[str, Any]:
    """
    Backtest pattern performance for a symbol
    
    Analyzes historical pattern accuracy and profitability
    """
    try:
        logger.info(f"📊 Backtesting patterns for {symbol}")
        
        # Fetch historical data
        if market_data_service and hasattr(market_data_service, 'get_historical_data'):
            price_data = await market_data_service.get_historical_data(
                symbol=symbol,
                days=lookback_days
            )
        else:
            price_data = []
        
        if not price_data or len(price_data) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient historical data for backtesting"
            )
        
        df = pd.DataFrame(price_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Run pattern detection on historical data
        backtest_results = []
        window_size = 50  # Analyze in 50-period windows
        
        for i in range(window_size, len(df), 12):  # Step by 12 hours
            window_df = df.iloc[i-window_size:i].copy()
            
            analysis = await master_pattern_agent.analyze(
                symbol=symbol,
                price_data=window_df
            )
            
            # Filter patterns by confidence
            valid_patterns = [
                p for p in analysis.detected_patterns
                if p.confidence >= min_confidence
            ]
            
            if pattern_type:
                valid_patterns = [
                    p for p in valid_patterns
                    if pattern_type.lower() in p.pattern_name.lower()
                ]
            
            for pattern in valid_patterns:
                # Check outcome
                future_prices = df.iloc[i:i+24]  # Next 24 hours
                if len(future_prices) > 0:
                    entry = pattern.entry_price
                    exit_price = future_prices['close'].iloc[-1]
                    
                    if pattern.direction == "long":
                        profit = (exit_price - entry) / entry * 100
                        hit_stop = future_prices['low'].min() <= pattern.stop_loss
                        hit_target = any(future_prices['high'].max() >= tp for tp in pattern.take_profit_targets)
                    else:
                        profit = (entry - exit_price) / entry * 100
                        hit_stop = future_prices['high'].max() >= pattern.stop_loss
                        hit_target = any(future_prices['low'].min() <= tp for tp in pattern.take_profit_targets)
                    
                    backtest_results.append({
                        "timestamp": df.index[i].isoformat(),
                        "pattern": pattern.pattern_name,
                        "direction": pattern.direction,
                        "confidence": pattern.confidence,
                        "profit_pct": profit,
                        "hit_stop": hit_stop,
                        "hit_target": hit_target,
                        "successful": profit > 0 and not hit_stop
                    })
        
        # Calculate statistics
        if backtest_results:
            successful_trades = [r for r in backtest_results if r['successful']]
            win_rate = len(successful_trades) / len(backtest_results) * 100
            avg_profit = sum(r['profit_pct'] for r in backtest_results) / len(backtest_results)
            
            # Group by pattern
            pattern_stats = {}
            for result in backtest_results:
                pattern_name = result['pattern']
                if pattern_name not in pattern_stats:
                    pattern_stats[pattern_name] = {
                        'count': 0,
                        'wins': 0,
                        'total_profit': 0
                    }
                pattern_stats[pattern_name]['count'] += 1
                if result['successful']:
                    pattern_stats[pattern_name]['wins'] += 1
                pattern_stats[pattern_name]['total_profit'] += result['profit_pct']
            
            # Calculate per-pattern statistics
            for pattern_name, stats in pattern_stats.items():
                stats['win_rate'] = stats['wins'] / stats['count'] * 100 if stats['count'] > 0 else 0
                stats['avg_profit'] = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
        else:
            win_rate = 0
            avg_profit = 0
            pattern_stats = {}
        
        return {
            "success": True,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "backtest_period": {
                "days": lookback_days,
                "total_patterns_detected": len(backtest_results)
            },
            "overall_statistics": {
                "win_rate": f"{win_rate:.1f}%",
                "average_profit": f"{avg_profit:.2f}%",
                "total_trades": len(backtest_results),
                "successful_trades": len([r for r in backtest_results if r['successful']])
            },
            "pattern_statistics": pattern_stats,
            "recent_results": backtest_results[-10:] if backtest_results else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error backtesting patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pattern backtesting failed: {str(e)}"
        )

@router.get("/patterns/statistics")
async def get_pattern_statistics() -> Dict[str, Any]:
    """
    Get global pattern detection statistics
    
    Returns performance metrics for all pattern types
    """
    try:
        stats = master_pattern_agent.pattern_trigger_system.get_pattern_statistics()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting pattern statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pattern statistics: {str(e)}"
        )

async def _calculate_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate technical indicators for pattern detection"""
    
    indicators = {}
    
    try:
        # Moving averages
        indicators['sma_20'] = df['close'].rolling(window=20).mean().iloc[-1]
        indicators['sma_50'] = df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
        indicators['ema_9'] = df['close'].ewm(span=9, adjust=False).mean().iloc[-1]
        indicators['ema_21'] = df['close'].ewm(span=21, adjust=False).mean().iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()  # type: ignore
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()  # type: ignore
        rs = gain / loss
        indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
        
        # Bollinger Bands
        sma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        indicators['bb_upper'] = (sma + (std * 2)).iloc[-1]
        indicators['bb_lower'] = (sma - (std * 2)).iloc[-1]
        indicators['bb_middle'] = sma.iloc[-1]
        
        # MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        indicators['macd'] = (ema_12 - ema_26).iloc[-1]
        indicators['macd_signal'] = (ema_12 - ema_26).ewm(span=9, adjust=False).mean().iloc[-1]
        
        # Volume indicators
        if 'volume' in df.columns:
            indicators['volume_sma'] = df['volume'].rolling(window=20).mean().iloc[-1]
            indicators['volume_ratio'] = df['volume'].iloc[-1] / indicators['volume_sma']
        
        # Detect specific conditions
        indicators['golden_cross_detected'] = (
            indicators['ema_9'] > indicators['ema_21'] and
            df['close'].ewm(span=9, adjust=False).mean().iloc[-2] <= df['close'].ewm(span=21, adjust=False).mean().iloc[-2]
        ) if len(df) > 1 else False
        
        indicators['death_cross_detected'] = (
            indicators['ema_9'] < indicators['ema_21'] and
            df['close'].ewm(span=9, adjust=False).mean().iloc[-2] >= df['close'].ewm(span=21, adjust=False).mean().iloc[-2]
        ) if len(df) > 1 else False
        
        # Support and resistance
        recent_high = df['high'].iloc[-20:].max()
        recent_low = df['low'].iloc[-20:].min()
        current_price = df['close'].iloc[-1]
        
        indicators['resistance_break'] = current_price > recent_high * 0.995
        indicators['support_break'] = current_price < recent_low * 1.005
        
        # Divergence detection (simplified)
        if len(df) >= 14:
            price_trend = 1 if df['close'].iloc[-1] > df['close'].iloc[-14] else -1
            rsi_trend = 1 if indicators['rsi'] > 50 else -1
            indicators['divergence_detected'] = price_trend != rsi_trend
            indicators['divergence_type'] = 'bullish' if price_trend < 0 and rsi_trend > 0 else 'bearish'
        
    except Exception as e:
        logger.warning(f"Error calculating some indicators: {e}")
    
    return indicators

def _determine_bias(patterns: List) -> str:
    """Determine overall market bias from patterns"""
    
    if not patterns:
        return "NEUTRAL"
    
    long_score = sum(p.confidence for p in patterns if p.direction == "long")
    short_score = sum(p.confidence for p in patterns if p.direction == "short")
    
    if long_score > short_score * 1.5:
        return "BULLISH"
    elif short_score > long_score * 1.5:
        return "BEARISH"
    else:
        return "NEUTRAL"