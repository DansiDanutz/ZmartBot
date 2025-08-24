#!/usr/bin/env python3
"""
🚀 UNIFIED ANALYSIS AGENT - The Ultimate Cryptocurrency Analysis System
================================================================================

This is the single, comprehensive module that combines ALL advanced features:
- 18-endpoint Cryptometer analysis
- Symbol-specific scoring adjustments  
- Advanced win rate calculations
- 15-minute intelligent caching
- Professional report generation
- Self-learning capabilities
- Real-time market data integration

No more conflicts, no redundancy - just one powerful agent for everything!
================================================================================
"""

import asyncio
import aiohttp
import logging
import json
import sqlite3
import numpy as np
import statistics
import hashlib
import os
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
import re

from src.config.settings import settings

logger = logging.getLogger(__name__)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SymbolConfig:
    """Symbol-specific configuration for professional analysis"""
    symbol: str
    predictability_factor: float = 1.0  # 0.8-1.2
    volatility_adjustment: float = 1.0   # 0.8-1.2  
    long_term_bias: float = 1.0          # 0.8-1.2
    liquidity_factor: float = 1.0        # 0.9-1.1
    fundamental_strength: float = 1.0     # 0.8-1.2
    technical_reliability: float = 1.0    # 0.8-1.2

@dataclass
class EndpointConfig:
    """Comprehensive endpoint configuration"""
    name: str
    endpoint: str
    params: Dict[str, Any]
    description: str
    weight: float
    analysis_type: str
    win_rate_impact: str
    reliability_threshold: float

@dataclass
class CacheEntry:
    """Intelligent cache entry with metadata"""
    symbol: str
    data: Dict[str, Any]
    timestamp: datetime
    expires_at: datetime
    data_hash: str
    confidence_level: float
    endpoint_count: int
    volatility_level: str

@dataclass
class AnalysisResult:
    """Complete analysis result structure"""
    symbol: str
    timestamp: datetime
    
    # Core Analysis Data
    raw_endpoint_data: Dict[str, Any]
    processed_metrics: Dict[str, Any]
    composite_scores: Dict[str, Any]
    win_rates: Dict[str, Any]
    
    # Market Intelligence
    market_analysis: Dict[str, Any]
    recommendations: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    
    # System Metadata
    analysis_metadata: Dict[str, Any]
    confidence_assessment: Dict[str, Any]
    cache_info: Dict[str, Any]
    learning_insights: Dict[str, Any]
    
    # Report Content
    executive_summary: str = ""
    comprehensive_report: str = ""

@dataclass
class LearningPattern:
    """Advanced learning pattern for continuous improvement"""
    pattern_id: str
    pattern_type: str
    success_metrics: Dict[str, float]
    improvement_suggestions: List[str]
    confidence_level: float
    usage_count: int
    last_updated: datetime

# =============================================================================
# UNIFIED ANALYSIS AGENT - THE ULTIMATE SOLUTION
# =============================================================================

class UnifiedAnalysisAgent:
    """
    🚀 THE ULTIMATE CRYPTOCURRENCY ANALYSIS AGENT
    
    This single agent combines ALL advanced features:
    ✅ 18-endpoint Cryptometer analysis
    ✅ Symbol-specific scoring (BTC, ETH, AVAX, SOL)
    ✅ Advanced win rate calculations
    ✅ 15-minute intelligent caching
    ✅ Professional report generation
    ✅ Self-learning capabilities
    ✅ Real-time market data integration
    ✅ Volatility-based optimizations
    ✅ Comprehensive monitoring
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "unified_cache"):
        """Initialize the Unified Analysis Agent"""
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        self.base_url = "https://api.cryptometer.io"
        self.session = None
        
        # Cache system
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.default_ttl_minutes = 15
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Learning system
        self.learning_db_path = "unified_learning.db"
        self.learning_patterns: Dict[str, LearningPattern] = {}
        
        # Initialize all components
        self.endpoints = self._initialize_18_endpoints()
        self.symbol_configs = self._initialize_symbol_configs()
        self._init_learning_database()
        self._load_learning_patterns()
        
        # Performance statistics
        self.stats = {
            "total_analyses": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_processing_time": 0.0,
            "avg_confidence": 0.0,
            "learning_improvements": 0
        }
        
        logger.info("🚀 Unified Analysis Agent initialized - ALL FEATURES ACTIVE")
    
    # =========================================================================
    # CORE ANALYSIS METHODS
    # =========================================================================
    
    async def analyze_symbol(self, symbol: str, force_refresh: bool = False, include_learning: bool = True) -> AnalysisResult:
        """
        🎯 MAIN ANALYSIS METHOD - Complete symbol analysis with all features
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USDT")
            force_refresh: Skip cache and force fresh analysis
            include_learning: Apply learning insights and store patterns
            
        Returns:
            Complete AnalysisResult with all data and reports
        """
        logger.info(f"🔍 Starting unified analysis for {symbol}")
        self.stats["total_analyses"] += 1
        start_time = time.time()
        
        try:
            # Step 1: Check cache (unless force refresh)
            if not force_refresh:
                cached_result = self._get_cached_analysis(symbol)
                if cached_result:
                    logger.info(f"📋 Cache HIT for {symbol}")
                    self.stats["cache_hits"] += 1
                    return cached_result
            
            self.stats["cache_misses"] += 1
            
            # Step 2: Collect endpoint data
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            raw_data = await self._collect_18_endpoint_data(symbol)
            
            # Step 3: Process comprehensive metrics
            processed_metrics = self._process_comprehensive_metrics(symbol, raw_data)
            
            # Step 4: Calculate advanced composite scores
            composite_scores = self._calculate_symbol_specific_scores(symbol, processed_metrics)
            
            # Step 5: Calculate professional win rates
            win_rates = self._calculate_advanced_win_rates(symbol, composite_scores, processed_metrics)
            
            # Step 6: Generate market intelligence
            market_analysis = self._generate_market_intelligence(symbol, processed_metrics, composite_scores)
            
            # Step 7: Create trading recommendations
            recommendations = self._generate_trading_recommendations(symbol, composite_scores, win_rates, market_analysis)
            
            # Step 8: Assess risks
            risk_assessment = self._assess_comprehensive_risks(symbol, processed_metrics, market_analysis)
            
            # Step 9: Calculate confidence
            confidence_assessment = self._calculate_analysis_confidence(processed_metrics, composite_scores)
            
            # Step 10: Apply learning (if enabled)
            learning_insights = {}
            if include_learning:
                learning_insights = self._apply_learning_insights(symbol, processed_metrics)
            
            # Step 11: Generate professional reports
            executive_summary = self._generate_executive_summary(symbol, composite_scores, win_rates, market_analysis, confidence_assessment)
            comprehensive_report = self._generate_comprehensive_report(symbol, processed_metrics, composite_scores, win_rates, market_analysis, recommendations, risk_assessment)
            
            # Step 12: Create final result
            processing_time = time.time() - start_time
            
            result = AnalysisResult(
                symbol=symbol,
                timestamp=datetime.now(),
                raw_endpoint_data=raw_data,
                processed_metrics=processed_metrics,
                composite_scores=composite_scores,
                win_rates=win_rates,
                market_analysis=market_analysis,
                recommendations=recommendations,
                risk_assessment=risk_assessment,
                analysis_metadata={
                    "processing_time": processing_time,
                    "endpoints_used": len([ep for ep in raw_data.values() if ep.get("success")]),
                    "total_endpoints": len(self.endpoints),
                    "analysis_version": "unified_v1.0",
                    "features_active": ["18_endpoints", "symbol_specific", "advanced_win_rates", "caching", "learning"]
                },
                confidence_assessment=confidence_assessment,
                cache_info={"cached": False, "fresh_analysis": True},
                learning_insights=learning_insights,
                executive_summary=executive_summary,
                comprehensive_report=comprehensive_report
            )
            
            # Step 13: Cache the result
            self._cache_analysis_result(symbol, result, confidence_assessment.get("overall_confidence", 0.5))
            
            # Step 14: Learn from this analysis
            if include_learning:
                self._learn_from_analysis(symbol, result)
            
            # Update statistics
            self.stats["avg_processing_time"] = (self.stats["avg_processing_time"] + processing_time) / 2
            self.stats["avg_confidence"] = (self.stats["avg_confidence"] + confidence_assessment.get("overall_confidence", 0.5)) / 2
            
            logger.info(f"✅ Unified analysis completed for {symbol} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in unified analysis for {symbol}: {e}")
            return self._create_fallback_result(symbol, str(e))
    
    async def generate_executive_summary(self, symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Generate executive summary report"""
        try:
            result = await self.analyze_symbol(symbol, force_refresh)
            return {
                "success": True,
                "symbol": symbol,
                "report_content": result.executive_summary,
                "metadata": result.analysis_metadata,
                "confidence": result.confidence_assessment.get("overall_confidence", 0.5),
                "cache_info": result.cache_info
            }
        except Exception as e:
            logger.error(f"Error generating executive summary for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    async def generate_comprehensive_report(self, symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        try:
            result = await self.analyze_symbol(symbol, force_refresh)
            return {
                "success": True,
                "symbol": symbol,
                "report_content": result.comprehensive_report,
                "analysis_data": asdict(result),
                "metadata": result.analysis_metadata,
                "confidence": result.confidence_assessment.get("overall_confidence", 0.5),
                "cache_info": result.cache_info
            }
        except Exception as e:
            logger.error(f"Error generating comprehensive report for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    # =========================================================================
    # 18-ENDPOINT DATA COLLECTION
    # =========================================================================
    
    def _initialize_18_endpoints(self) -> Dict[str, EndpointConfig]:
        """Initialize all 18 Cryptometer endpoints with professional configuration"""
        return {
            "market_list": EndpointConfig(
                name="market_list", endpoint="/coinlist/", params={"e": "binance"},
                description="Market List - Available trading pairs", weight=5.0,
                analysis_type="fundamental", win_rate_impact="low", reliability_threshold=0.9
            ),
            "crypto_info": EndpointConfig(
                name="crypto_info", endpoint="/cryptocurrency-info/", params={"e": "binance", "filter": "defi"},
                description="Cryptocurrency Info - Market data and metrics", weight=15.0,
                analysis_type="fundamental", win_rate_impact="high", reliability_threshold=0.8
            ),
            "coin_info": EndpointConfig(
                name="coin_info", endpoint="/coininfo/", params={},
                description="Coin Info - Fundamental data", weight=10.0,
                analysis_type="fundamental", win_rate_impact="medium", reliability_threshold=0.8
            ),
            "forex_rates": EndpointConfig(
                name="forex_rates", endpoint="/forex-rates/", params={"source": "USD"},
                description="Forex Rates - Currency conversion rates", weight=5.0,
                analysis_type="macro", win_rate_impact="low", reliability_threshold=0.9
            ),
            "volume_flow": EndpointConfig(
                name="volume_flow", endpoint="/volume-flow/", params={"timeframe": "1h"},
                description="Volume Flow - Money flow analysis", weight=20.0,
                analysis_type="volume", win_rate_impact="very_high", reliability_threshold=0.7
            ),
            "liquidity_lens": EndpointConfig(
                name="liquidity_lens", endpoint="/liquidity-lens/", params={"timeframe": "1h"},
                description="Liquidity Lens - Liquidity analysis", weight=18.0,
                analysis_type="volume", win_rate_impact="high", reliability_threshold=0.7
            ),
            "volatility_index": EndpointConfig(
                name="volatility_index", endpoint="/volatility-index/", params={"e": "binance", "timeframe": "1h"},
                description="Volatility Index - Market volatility metrics", weight=12.0,
                analysis_type="technical", win_rate_impact="medium", reliability_threshold=0.8
            ),
            "ohlcv": EndpointConfig(
                name="ohlcv", endpoint="/ohlcv/", params={"e": "binance", "timeframe": "1h"},
                description="OHLCV Candles - Price and volume data", weight=25.0,
                analysis_type="technical", win_rate_impact="very_high", reliability_threshold=0.9
            ),
            "ls_ratio": EndpointConfig(
                name="ls_ratio", endpoint="/ls-v1/", params={},
                description="Long/Short Ratio - Sentiment indicator", weight=15.0,
                analysis_type="sentiment", win_rate_impact="high", reliability_threshold=0.8
            ),
            "tickerlist_pro": EndpointConfig(
                name="tickerlist_pro", endpoint="/tickerlist-pro/", params={"e": "binance"},
                description="Tickerlist Pro - Advanced ticker data", weight=12.0,
                analysis_type="technical", win_rate_impact="medium", reliability_threshold=0.8
            ),
            "merged_volume": EndpointConfig(
                name="merged_volume", endpoint="/merged-volume/", params={"timeframe": "1h"},
                description="Merged Buy/Sell Volume - Order flow analysis", weight=22.0,
                analysis_type="volume", win_rate_impact="very_high", reliability_threshold=0.7
            ),
            "liquidation_data": EndpointConfig(
                name="liquidation_data", endpoint="/liquidation-v2/", params={},
                description="Total Liquidation Data - Risk assessment", weight=18.0,
                analysis_type="risk", win_rate_impact="high", reliability_threshold=0.7
            ),
            "trend_indicator": EndpointConfig(
                name="trend_indicator", endpoint="/trend-v3/", params={},
                description="Trend Indicator V3 - Advanced trend analysis", weight=25.0,
                analysis_type="trend", win_rate_impact="very_high", reliability_threshold=0.8
            ),
            "rapid_movements": EndpointConfig(
                name="rapid_movements", endpoint="/rapid-v1/", params={},
                description="Rapid Movements - Momentum detection", weight=20.0,
                analysis_type="momentum", win_rate_impact="high", reliability_threshold=0.7
            ),
            "whale_trades": EndpointConfig(
                name="whale_trades", endpoint="/xtrades/", params={},
                description="Whale Trades (xTrade) - Large transaction analysis", weight=15.0,
                analysis_type="whale", win_rate_impact="high", reliability_threshold=0.6
            ),
            "large_trades": EndpointConfig(
                name="large_trades", endpoint="/whale-v2/", params={},
                description="Large Trades Activity - Institutional flow", weight=18.0,
                analysis_type="whale", win_rate_impact="high", reliability_threshold=0.7
            ),
            "ai_screener": EndpointConfig(
                name="ai_screener", endpoint="/ai-screener/", params={},
                description="AI Screener - Machine learning insights", weight=15.0,
                analysis_type="ai", win_rate_impact="medium", reliability_threshold=0.6
            ),
            "ai_screener_analysis": EndpointConfig(
                name="ai_screener_analysis", endpoint="/ai-screener-analysis/", params={},
                description="AI Screener Analysis - Advanced AI insights", weight=12.0,
                analysis_type="ai", win_rate_impact="medium", reliability_threshold=0.6
            )
        }
    
    async def _collect_18_endpoint_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data from all 18 Cryptometer endpoints"""
        raw_data = {}
        
        for endpoint_name, config in self.endpoints.items():
            try:
                logger.debug(f"📡 Collecting {endpoint_name}")
                
                # Prepare parameters
                params = config.params.copy()
                params["api"] = self.api_key
                
                # Add symbol-specific parameters
                if endpoint_name in ["crypto_info", "ohlcv", "tickerlist_pro"]:
                    params["symbol"] = symbol.replace("/", "-")
                elif endpoint_name in ["ls_ratio", "liquidation_data", "trend_indicator", "rapid_movements"]:
                    params["symbol"] = symbol.replace("/", "")
                
                # Make API call
                data = await self._make_api_call(config.endpoint, params)
                await asyncio.sleep(1.0)  # Rate limiting
                
                raw_data[endpoint_name] = {
                    "config": asdict(config),
                    "data": data,
                    "success": data and data.get("success") == "true",
                    "timestamp": datetime.now().isoformat()
                }
                
                if raw_data[endpoint_name]["success"]:
                    logger.debug(f"✅ {endpoint_name}: Success")
                else:
                    logger.warning(f"⚠️ {endpoint_name}: {data.get('error', 'No data') if data else 'No response'}")
                    
            except Exception as e:
                logger.error(f"❌ Error collecting {endpoint_name}: {e}")
                raw_data[endpoint_name] = {
                    "config": asdict(config),
                    "data": {"success": "false", "error": str(e)},
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
        
        return raw_data
    
    async def _make_api_call(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API call to Cryptometer endpoint"""
        try:
            if self.session is None:
                logger.error("Session is None, cannot make API call")
                return {"success": "false", "error": "Session not initialized"}
                
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"API call failed: {response.status}")
                    return {"success": "false", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"API call error: {e}")
            return {"success": "false", "error": str(e)}
    
    # =========================================================================
    # SYMBOL-SPECIFIC CONFIGURATIONS
    # =========================================================================
    
    def _initialize_symbol_configs(self) -> Dict[str, SymbolConfig]:
        """Initialize symbol-specific configurations for professional accuracy"""
        return {
            "BTC/USDT": SymbolConfig(
                symbol="BTC/USDT",
                predictability_factor=1.1,    # BTC is more predictable
                volatility_adjustment=1.0,    # Standard volatility
                long_term_bias=1.15,         # Strong long-term uptrend
                liquidity_factor=1.1,        # Excellent liquidity
                fundamental_strength=1.2,     # Strong fundamentals
                technical_reliability=1.1     # Reliable technical patterns
            ),
            "ETH/USDT": SymbolConfig(
                symbol="ETH/USDT",
                predictability_factor=1.05,   # ETH is fairly predictable
                volatility_adjustment=1.1,    # Slightly more volatile than BTC
                long_term_bias=1.1,          # Good long-term prospects
                liquidity_factor=1.05,       # Good liquidity
                fundamental_strength=1.15,    # Strong fundamentals (DeFi, staking)
                technical_reliability=1.0     # Standard technical reliability
            ),
            "AVAX/USDT": SymbolConfig(
                symbol="AVAX/USDT",
                predictability_factor=0.9,    # More volatile, less predictable
                volatility_adjustment=1.2,    # Higher volatility
                long_term_bias=1.0,          # Neutral long-term bias
                liquidity_factor=0.95,       # Lower liquidity than BTC/ETH
                fundamental_strength=1.0,     # Moderate fundamentals
                technical_reliability=0.9     # Less reliable patterns
            ),
            "SOL/USDT": SymbolConfig(
                symbol="SOL/USDT",
                predictability_factor=0.85,   # High volatility, less predictable
                volatility_adjustment=1.25,   # High volatility
                long_term_bias=1.05,         # Moderate long-term potential
                liquidity_factor=0.9,        # Moderate liquidity
                fundamental_strength=1.05,    # Growing ecosystem
                technical_reliability=0.85    # Less reliable due to volatility
            )
        }
    
    # =========================================================================
    # ADVANCED PROCESSING & SCORING
    # =========================================================================
    
    def _process_comprehensive_metrics(self, symbol: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw endpoint data into comprehensive metrics"""
        metrics = {
            "data_sources": [],
            "technical_indicators": {},
            "sentiment_indicators": {},
            "volume_indicators": {},
            "liquidation_indicators": {},
            "ai_indicators": {},
            "trend_indicators": {},
            "whale_indicators": {},
            "risk_indicators": {},
            "macro_indicators": {}
        }
        
        successful_endpoints = 0
        
        for endpoint_name, endpoint_info in raw_data.items():
            if not endpoint_info["success"]:
                continue
                
            successful_endpoints += 1
            data = endpoint_info["data"]
            config = endpoint_info["config"]
            
            metrics["data_sources"].append({
                "name": endpoint_name,
                "description": config["description"],
                "weight": config["weight"],
                "analysis_type": config["analysis_type"],
                "status": "active"
            })
            
            # Process specific endpoint data
            self._process_endpoint_metrics(endpoint_name, data, metrics, symbol)
        
        metrics["summary"] = {
            "successful_endpoints": successful_endpoints,
            "total_endpoints": len(self.endpoints),
            "data_coverage": successful_endpoints / len(self.endpoints),
            "primary_analysis_types": list(set([
                source["analysis_type"] for source in metrics["data_sources"]
            ]))
        }
        
        return metrics
    
    def _process_endpoint_metrics(self, endpoint_name: str, data: Dict[str, Any], metrics: Dict[str, Any], symbol: str):
        """Process metrics for specific endpoints"""
        
        try:
            if endpoint_name == "trend_indicator":
                trend_data = data.get("data", [])
                if trend_data and isinstance(trend_data, list):
                    symbol_trend = None
                    for item in trend_data:
                        if symbol.replace("/", "").upper() in item.get("symbol", "").upper():
                            symbol_trend = item
                            break
                    
                    if symbol_trend:
                        metrics["trend_indicators"] = {
                            "trend_score": float(symbol_trend.get("trend_score", 50)),
                            "buy_pressure": float(symbol_trend.get("buy_pressure", 50)),
                            "sell_pressure": float(symbol_trend.get("sell_pressure", 50)),
                            "momentum": float(symbol_trend.get("momentum", 50)),
                            "strength": symbol_trend.get("strength", "neutral")
                        }
            
            elif endpoint_name == "ls_ratio":
                ls_data = data.get("data", [])
                if ls_data and isinstance(ls_data, list):
                    latest_ls = ls_data[0]
                    metrics["sentiment_indicators"]["ls_ratio"] = {
                        "ratio": float(latest_ls.get("ratio", 0.5)),
                        "long_percentage": float(latest_ls.get("buy", 50)),
                        "short_percentage": float(latest_ls.get("sell", 50)),
                        "timestamp": latest_ls.get("timestamp")
                    }
            
            elif endpoint_name == "volume_flow":
                volume_data = data.get("data", {})
                inflow = volume_data.get("inflow", [])
                outflow = volume_data.get("outflow", [])
                
                if inflow and outflow:
                    total_inflow = sum([float(item.get("volume", 0)) for item in inflow[:10]])
                    total_outflow = sum([float(item.get("volume", 0)) for item in outflow[:10]])
                    net_flow = total_inflow - total_outflow
                    
                    metrics["volume_indicators"]["flow_analysis"] = {
                        "total_inflow": total_inflow,
                        "total_outflow": total_outflow,
                        "net_flow": net_flow,
                        "flow_ratio": total_inflow / total_outflow if total_outflow > 0 else 0
                    }
            
            elif endpoint_name == "liquidation_data":
                liq_data = data.get("data", [])
                if liq_data and isinstance(liq_data, list) and len(liq_data) > 0:
                    total_longs = 0
                    total_shorts = 0
                    
                    for exchange_data in liq_data[0].values():
                        if isinstance(exchange_data, dict):
                            longs = float(exchange_data.get("longs", 0))
                            shorts = float(exchange_data.get("shorts", 0))
                            total_longs += longs
                            total_shorts += shorts
                    
                    metrics["liquidation_indicators"] = {
                        "total_long_liquidations": total_longs,
                        "total_short_liquidations": total_shorts,
                        "liquidation_ratio": total_longs / total_shorts if total_shorts > 0 else float('inf'),
                        "liquidation_dominance": "longs" if total_longs > total_shorts else "shorts"
                    }
            
            elif endpoint_name == "large_trades":
                whale_data = data.get("data", [])
                if whale_data and isinstance(whale_data, list):
                    buy_volume = 0
                    sell_volume = 0
                    
                    for trade in whale_data[:20]:  # Top 20 trades
                        volume = float(trade.get("volume", 0))
                        if trade.get("side", "").lower() == "buy":
                            buy_volume += volume
                        else:
                            sell_volume += volume
                    
                    metrics["whale_indicators"]["large_trades"] = {
                        "buy_volume": buy_volume,
                        "sell_volume": sell_volume,
                        "buy_sell_ratio": buy_volume / sell_volume if sell_volume > 0 else float('inf'),
                        "net_whale_flow": buy_volume - sell_volume
                    }
            
            elif endpoint_name == "ai_screener_analysis":
                ai_data = data.get("data", {})
                if ai_data:
                    metrics["ai_indicators"]["analysis"] = {
                        "sentiment_score": float(ai_data.get("sentiment", 50)),
                        "prediction_confidence": float(ai_data.get("confidence", 50)),
                        "recommendation": ai_data.get("recommendation", "neutral"),
                        "ai_score": float(ai_data.get("score", 50))
                    }
                    
        except Exception as e:
            logger.debug(f"Error processing {endpoint_name} metrics: {e}")
    
    def _calculate_symbol_specific_scores(self, symbol: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced composite scores with symbol-specific adjustments"""
        
        # Get symbol-specific configuration
        symbol_config = self.symbol_configs.get(symbol, self.symbol_configs.get("BTC/USDT"))
        if symbol_config is None:
            # Fallback to default BTC configuration if somehow both lookups fail
            symbol_config = SymbolConfig(symbol=symbol)
        
        scores = {
            "components": {},
            "symbol_adjustments": asdict(symbol_config)
        }
        
        # Technical Analysis Component (Weight: 30%)
        technical_factors = []
        
        if metrics["trend_indicators"]:
            trend_score = metrics["trend_indicators"]["trend_score"]
            buy_pressure = metrics["trend_indicators"]["buy_pressure"]
            sell_pressure = metrics["trend_indicators"]["sell_pressure"]
            
            # Apply symbol-specific technical reliability
            adjusted_trend = trend_score * symbol_config.technical_reliability
            technical_factors.append(adjusted_trend)
            
            # Pressure differential
            pressure_diff = (buy_pressure - sell_pressure) * 0.5 + 50
            technical_factors.append(pressure_diff)
        
        technical_score = np.mean(technical_factors) if technical_factors else 50
        scores["components"]["technical_analysis"] = {
            "score": technical_score,
            "factors_count": len(technical_factors),
            "weight": 0.30,
            "symbol_adjustment": symbol_config.technical_reliability
        }
        
        # Sentiment Analysis Component (Weight: 25%)
        sentiment_factors = []
        
        if "ls_ratio" in metrics["sentiment_indicators"]:
            ls_data = metrics["sentiment_indicators"]["ls_ratio"]
            long_pct = ls_data["long_percentage"]
            
            # Symbol-specific sentiment processing
            if symbol in ["BTC/USDT", "ETH/USDT"]:
                # Major cryptos follow sentiment more directly
                sentiment_score = 50 + (long_pct - 50) * 0.8
            else:
                # Smaller caps more contrarian
                if long_pct > 80:
                    sentiment_score = 35  # Contrarian bearish
                elif long_pct < 20:
                    sentiment_score = 75  # Contrarian bullish
                else:
                    sentiment_score = 50 + (long_pct - 50) * 0.4
            
            sentiment_factors.append(sentiment_score)
        
        if metrics["ai_indicators"] and "analysis" in metrics["ai_indicators"]:
            ai_sentiment = metrics["ai_indicators"]["analysis"]["sentiment_score"]
            # AI sentiment weighted by fundamental strength
            weighted_ai = ai_sentiment * symbol_config.fundamental_strength
            sentiment_factors.append(weighted_ai)
        
        sentiment_score = np.mean(sentiment_factors) if sentiment_factors else 50
        scores["components"]["sentiment_analysis"] = {
            "score": sentiment_score,
            "factors_count": len(sentiment_factors),
            "weight": 0.25,
            "symbol_adjustment": symbol_config.fundamental_strength
        }
        
        # Volume Analysis Component (Weight: 25%)
        volume_factors = []
        
        if "flow_analysis" in metrics["volume_indicators"]:
            flow_data = metrics["volume_indicators"]["flow_analysis"]
            net_flow = flow_data["net_flow"]
            
            # Symbol-specific volume scaling
            if symbol == "BTC/USDT":
                volume_scale = 10000000  # 10M for BTC
            elif symbol == "ETH/USDT":
                volume_scale = 5000000   # 5M for ETH
            else:
                volume_scale = 1000000   # 1M for others
            
            if net_flow > 0:
                flow_score = min(80, 50 + (net_flow / volume_scale) * 15)
            else:
                flow_score = max(20, 50 + (net_flow / volume_scale) * 15)
            
            # Apply liquidity factor
            adjusted_flow = flow_score * symbol_config.liquidity_factor
            volume_factors.append(adjusted_flow)
        
        if "large_trades" in metrics["whale_indicators"]:
            whale_data = metrics["whale_indicators"]["large_trades"]
            buy_sell_ratio = whale_data["buy_sell_ratio"]
            
            if buy_sell_ratio > 1:
                whale_score = min(80, 50 + (buy_sell_ratio - 1) * 25)
            else:
                whale_score = max(20, 50 - (1 - buy_sell_ratio) * 25)
            
            volume_factors.append(whale_score)
        
        volume_score = np.mean(volume_factors) if volume_factors else 50
        scores["components"]["volume_analysis"] = {
            "score": volume_score,
            "factors_count": len(volume_factors),
            "weight": 0.25,
            "symbol_adjustment": symbol_config.liquidity_factor
        }
        
        # Liquidation Analysis Component (Weight: 20%)
        liquidation_factors = []
        
        if metrics["liquidation_indicators"]:
            liq_data = metrics["liquidation_indicators"]
            total_longs = liq_data["total_long_liquidations"]
            total_shorts = liq_data["total_short_liquidations"]
            
            if total_longs + total_shorts > 0:
                long_liq_pct = total_longs / (total_longs + total_shorts) * 100
                
                # Symbol-specific liquidation analysis
                if symbol in ["BTC/USDT", "ETH/USDT"]:
                    # Major cryptos more stable
                    if long_liq_pct > 75:
                        liq_score = 60  # Moderate oversold
                    elif long_liq_pct < 25:
                        liq_score = 40  # Moderate overbought
                    else:
                        liq_score = 50
                else:
                    # Smaller caps more volatile
                    if long_liq_pct > 80:
                        liq_score = 70  # Strong oversold signal
                    elif long_liq_pct < 20:
                        liq_score = 30  # Strong overbought signal
                    else:
                        liq_score = 50
                
                liquidation_factors.append(liq_score)
        
        liquidation_score = np.mean(liquidation_factors) if liquidation_factors else 50
        scores["components"]["liquidation_analysis"] = {
            "score": liquidation_score,
            "factors_count": len(liquidation_factors),
            "weight": 0.20,
            "symbol_adjustment": 1.0
        }
        
        # Calculate weighted composite scores
        weights = {
            "technical_analysis": 0.30,
            "sentiment_analysis": 0.25,
            "volume_analysis": 0.25,
            "liquidation_analysis": 0.20
        }
        
        # Long position score
        long_score = sum([
            scores["components"][component]["score"] * weights[component]
            for component in weights.keys()
        ])
        
        # Apply symbol-specific adjustments
        long_score *= symbol_config.predictability_factor
        
        # Short position score with symbol-specific logic
        short_technical = 100 - scores["components"]["technical_analysis"]["score"]
        short_sentiment = scores["components"]["sentiment_analysis"]["score"] * (0.7 if symbol in ["BTC/USDT", "ETH/USDT"] else 1.0)
        short_volume = 100 - scores["components"]["volume_analysis"]["score"]
        short_liquidation = 100 - scores["components"]["liquidation_analysis"]["score"]
        
        short_score = (
            short_technical * weights["technical_analysis"] +
            short_sentiment * weights["sentiment_analysis"] +
            short_volume * weights["volume_analysis"] +
            short_liquidation * weights["liquidation_analysis"]
        )
        
        # Apply symbol-specific short bias
        if symbol_config.long_term_bias > 1.0:
            short_score *= (2.0 - symbol_config.long_term_bias)  # Reduce short score for bullish assets
        
        # Bounds based on symbol characteristics
        if symbol in ["BTC/USDT", "ETH/USDT"]:
            long_bounds = (25, 85)
            short_bounds = (15, 75)
        else:
            long_bounds = (20, 80)
            short_bounds = (20, 80)
        
        scores["final_scores"] = {
            "long_score": max(long_bounds[0], min(long_bounds[1], long_score)),
            "short_score": max(short_bounds[0], min(short_bounds[1], short_score)),
            "confidence_level": min(len(metrics["data_sources"]) / 18 * 100, 100),
            "symbol_specific_applied": True
        }
        
        return scores
    
    def _calculate_advanced_win_rates(self, symbol: str, composite_scores: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate professional win rates using advanced methodology"""
        
        symbol_config = self.symbol_configs.get(symbol, self.symbol_configs.get("BTC/USDT"))
        if symbol_config is None:
            # Fallback to default configuration if somehow both lookups fail
            symbol_config = SymbolConfig(symbol=symbol)
        
        def advanced_score_to_win_rate(score: float, timeframe: str, position: str, confidence: float) -> float:
            """Advanced win rate calculation with comprehensive adjustments"""
            
            # Base conversion
            base_rate = score * 0.9
            
            # Confidence adjustment
            confidence_factor = 0.85 + (confidence / 100) * 0.3
            
            # Timeframe adjustments (symbol-specific)
            if symbol in ["BTC/USDT", "ETH/USDT"]:
                timeframe_factors = {
                    "24-48h": 0.9,   # Short-term volatility
                    "7d": 1.0,       # Balanced
                    "1m": 1.2        # Strong long-term trends
                }
            else:
                timeframe_factors = {
                    "24-48h": 0.85,  # Higher short-term volatility
                    "7d": 0.95,      # Moderate
                    "1m": 1.1        # Less predictable long-term
                }
            
            # Position-specific adjustments
            if position == "long":
                position_factor = symbol_config.long_term_bias
                if timeframe == "1m":
                    position_factor *= 1.1  # Boost long-term longs
            else:  # short
                position_factor = 2.0 - symbol_config.long_term_bias  # Inverse relationship
                if timeframe == "1m" and symbol_config.long_term_bias > 1.1:
                    position_factor *= 0.8  # Penalize long-term shorts on bullish assets
            
            # Volatility adjustment
            volatility_factor = symbol_config.volatility_adjustment
            if position == "short":
                volatility_factor = min(1.0, volatility_factor)  # Cap volatility benefit for shorts
            
            # Data quality adjustment
            data_quality_factor = 0.9 + (len(metrics["data_sources"]) / 18) * 0.2
            
            # Calculate final win rate
            win_rate = (base_rate * confidence_factor * 
                       timeframe_factors[timeframe] * 
                       position_factor * volatility_factor * 
                       data_quality_factor * symbol_config.predictability_factor)
            
            # Symbol-specific bounds
            if symbol in ["BTC/USDT", "ETH/USDT"]:
                return max(30, min(90, win_rate))
            else:
                return max(25, min(85, win_rate))
        
        confidence = composite_scores["final_scores"]["confidence_level"]
        long_score = composite_scores["final_scores"]["long_score"]
        short_score = composite_scores["final_scores"]["short_score"]
        
        win_rates = {
            "methodology": f"Advanced Multi-Factor Win Rate Calculation for {symbol}",
            "symbol_config": asdict(symbol_config),
            "confidence_level": confidence,
            "data_quality_score": len(metrics["data_sources"]) / 18 * 100,
            "timeframes": {
                "24-48h": {
                    "long": advanced_score_to_win_rate(long_score, "24-48h", "long", confidence),
                    "short": advanced_score_to_win_rate(short_score, "24-48h", "short", confidence)
                },
                "7d": {
                    "long": advanced_score_to_win_rate(long_score, "7d", "long", confidence),
                    "short": advanced_score_to_win_rate(short_score, "7d", "short", confidence)
                },
                "1m": {
                    "long": advanced_score_to_win_rate(long_score, "1m", "long", confidence),
                    "short": advanced_score_to_win_rate(short_score, "1m", "short", confidence)
                }
            },
            "adjustments_applied": {
                "symbol_specific": True,
                "volatility_adjusted": True,
                "liquidity_adjusted": True,
                "fundamental_weighted": True
            }
        }
        
        return win_rates
    
    # =========================================================================
    # INTELLIGENT CACHING SYSTEM
    # =========================================================================
    
    def _get_cached_analysis(self, symbol: str) -> Optional[AnalysisResult]:
        """Get cached analysis with intelligent TTL"""
        cache_key = self._generate_cache_key(symbol)
        
        try:
            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                
                if datetime.now() < entry.expires_at:
                    logger.info(f"📋 Cache HIT for {symbol} (memory) - expires in {(entry.expires_at - datetime.now()).total_seconds():.0f}s")
                    return AnalysisResult(**entry.data)
                else:
                    del self.memory_cache[cache_key]
            
            # Check file cache
            file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    cache_data = json.load(f)
                
                expires_at = datetime.fromisoformat(cache_data["expires_at"])
                if datetime.now() < expires_at:
                    # Load into memory cache
                    entry = CacheEntry(
                        symbol=cache_data["symbol"],
                        data=cache_data["data"],
                        timestamp=datetime.fromisoformat(cache_data["timestamp"]),
                        expires_at=expires_at,
                        data_hash=cache_data["data_hash"],
                        confidence_level=cache_data["confidence_level"],
                        endpoint_count=cache_data["endpoint_count"],
                        volatility_level=cache_data["volatility_level"]
                    )
                    self.memory_cache[cache_key] = entry
                    
                    logger.info(f"📋 Cache HIT for {symbol} (file) - expires in {(expires_at - datetime.now()).total_seconds():.0f}s")
                    return AnalysisResult(**entry.data)
                else:
                    os.remove(file_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading cache for {symbol}: {e}")
            return None
    
    def _cache_analysis_result(self, symbol: str, result: AnalysisResult, confidence: float):
        """Cache analysis result with intelligent TTL"""
        try:
            cache_key = self._generate_cache_key(symbol)
            
            # Calculate adaptive TTL
            ttl_minutes = self._calculate_adaptive_ttl(symbol, result, confidence)
            
            # Create cache entry
            now = datetime.now()
            expires_at = now + timedelta(minutes=ttl_minutes)
            data_dict = asdict(result)
            data_hash = hashlib.md5(json.dumps(data_dict, default=str, sort_keys=True).encode()).hexdigest()
            
            # Determine volatility level
            volatility_level = self._assess_volatility_level(result)
            
            entry = CacheEntry(
                symbol=symbol,
                data=data_dict,
                timestamp=now,
                expires_at=expires_at,
                data_hash=data_hash,
                confidence_level=confidence,
                endpoint_count=len(result.processed_metrics.get("data_sources", [])),
                volatility_level=volatility_level
            )
            
            # Store in memory cache
            self.memory_cache[cache_key] = entry
            
            # Store in file cache
            file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            cache_data = {
                "symbol": entry.symbol,
                "data": entry.data,
                "timestamp": entry.timestamp.isoformat(),
                "expires_at": entry.expires_at.isoformat(),
                "data_hash": entry.data_hash,
                "confidence_level": entry.confidence_level,
                "endpoint_count": entry.endpoint_count,
                "volatility_level": entry.volatility_level
            }
            
            with open(file_path, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            logger.info(f"💾 Cache SAVE for {symbol} - TTL: {ttl_minutes}min ({volatility_level} volatility)")
            
        except Exception as e:
            logger.error(f"Error caching analysis for {symbol}: {e}")
    
    def _calculate_adaptive_ttl(self, symbol: str, result: AnalysisResult, confidence: float) -> int:
        """Calculate adaptive TTL based on market conditions"""
        base_ttl = self.default_ttl_minutes
        
        # Volatility adjustment
        volatility_level = self._assess_volatility_level(result)
        if volatility_level == "high":
            base_ttl = max(5, base_ttl // 3)  # High volatility: 5 minutes
        elif volatility_level == "low":
            base_ttl = min(30, base_ttl * 1.5)  # Low volatility: 22.5 minutes
        
        # Confidence adjustment
        if confidence < 0.5:
            base_ttl = max(5, base_ttl // 2)  # Low confidence: shorter TTL
        elif confidence > 0.8:
            base_ttl = min(30, base_ttl * 1.2)  # High confidence: longer TTL
        
        # Data quality adjustment
        endpoint_count = len(result.processed_metrics.get("data_sources", []))
        if endpoint_count < 5:
            base_ttl = max(5, base_ttl // 2)  # Limited data: shorter TTL
        elif endpoint_count > 15:
            base_ttl = min(30, base_ttl * 1.1)  # Comprehensive data: longer TTL
        
        return int(base_ttl)
    
    def _assess_volatility_level(self, result: AnalysisResult) -> str:
        """Assess market volatility level from analysis result"""
        try:
            # Check for rapid movements
            rapid_score = 0
            if "rapid_movements" in result.raw_endpoint_data:
                rapid_data = result.raw_endpoint_data["rapid_movements"].get("data", {})
                rapid_score = float(rapid_data.get("rapid_score", 50))
            
            # Check liquidation activity
            liq_activity = 0
            if result.processed_metrics.get("liquidation_indicators"):
                liq_data = result.processed_metrics["liquidation_indicators"]
                total_liq = liq_data.get("total_long_liquidations", 0) + liq_data.get("total_short_liquidations", 0)
                liq_activity = min(100, total_liq / 1000000)  # Normalize to 0-100
            
            # Determine volatility level
            volatility_score = (rapid_score + liq_activity) / 2
            
            if volatility_score > 70:
                return "high"
            elif volatility_score < 30:
                return "low"
            else:
                return "medium"
                
        except Exception as e:
            logger.debug(f"Error assessing volatility: {e}")
            return "medium"
    
    def _generate_cache_key(self, symbol: str) -> str:
        """Generate cache key for symbol"""
        return symbol.replace("/", "_").lower()
    
    # =========================================================================
    # MARKET INTELLIGENCE & RECOMMENDATIONS
    # =========================================================================
    
    def _generate_market_intelligence(self, symbol: str, metrics: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive market intelligence"""
        
        analysis = {
            "current_market_condition": {},
            "key_insights": [],
            "market_structure": {},
            "institutional_activity": {},
            "technical_outlook": {},
            "sentiment_analysis": {}
        }
        
        # Determine market condition
        long_score = scores["final_scores"]["long_score"]
        short_score = scores["final_scores"]["short_score"]
        
        if long_score > 65:
            condition = "Bullish"
            bias_strength = "Strong" if long_score > 75 else "Moderate"
        elif short_score > 65:
            condition = "Bearish"
            bias_strength = "Strong" if short_score > 75 else "Moderate"
        else:
            condition = "Neutral"
            bias_strength = "Balanced"
        
        analysis["current_market_condition"] = {
            "direction": condition,
            "strength": bias_strength,
            "long_score": long_score,
            "short_score": short_score,
            "confidence": scores["final_scores"]["confidence_level"]
        }
        
        # Generate insights based on data
        if metrics["trend_indicators"]:
            trend_data = metrics["trend_indicators"]
            if trend_data["trend_score"] > 70:
                analysis["key_insights"].append(f"Strong uptrend detected with {trend_data['trend_score']:.1f} trend score")
            elif trend_data["trend_score"] < 30:
                analysis["key_insights"].append(f"Strong downtrend detected with {trend_data['trend_score']:.1f} trend score")
        
        if "flow_analysis" in metrics["volume_indicators"]:
            flow_data = metrics["volume_indicators"]["flow_analysis"]
            if abs(flow_data["net_flow"]) > 1000000:  # Significant flow
                direction = "inflow" if flow_data["net_flow"] > 0 else "outflow"
                analysis["key_insights"].append(f"Significant volume {direction}: ${abs(flow_data['net_flow']):,.0f}")
        
        if metrics["liquidation_indicators"]:
            liq_data = metrics["liquidation_indicators"]
            if liq_data["liquidation_dominance"] == "longs":
                analysis["key_insights"].append("Heavy long liquidations indicate potential oversold conditions")
            else:
                analysis["key_insights"].append("Heavy short liquidations indicate potential overbought conditions")
        
        # Institutional activity analysis
        if "large_trades" in metrics["whale_indicators"]:
            whale_data = metrics["whale_indicators"]["large_trades"]
            net_flow = whale_data["net_whale_flow"]
            if abs(net_flow) > 500000:
                direction = "accumulation" if net_flow > 0 else "distribution"
                analysis["institutional_activity"]["whale_sentiment"] = direction
                analysis["key_insights"].append(f"Whale activity shows {direction} pattern")
        
        return analysis
    
    def _generate_trading_recommendations(self, symbol: str, scores: Dict[str, Any], win_rates: Dict[str, Any], market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional trading recommendations"""
        
        long_score = scores["final_scores"]["long_score"]
        short_score = scores["final_scores"]["short_score"]
        confidence = scores["final_scores"]["confidence_level"]
        
        recommendations = {
            "primary_direction": "",
            "entry_strategy": "",
            "risk_management": "",
            "timeframe_recommendations": {},
            "position_sizing": "",
            "stop_loss_guidance": "",
            "take_profit_targets": []
        }
        
        # Primary direction
        if long_score > short_score + 10:
            recommendations["primary_direction"] = "LONG"
            recommendations["entry_strategy"] = "Consider long positions on dips or breakouts"
        elif short_score > long_score + 10:
            recommendations["primary_direction"] = "SHORT" 
            recommendations["entry_strategy"] = "Consider short positions on rallies or breakdowns"
        else:
            recommendations["primary_direction"] = "NEUTRAL"
            recommendations["entry_strategy"] = "Wait for clearer directional signals"
        
        # Timeframe-specific recommendations
        for timeframe, rates in win_rates["timeframes"].items():
            long_rate = rates["long"]
            short_rate = rates["short"]
            
            if long_rate > 60:
                tf_rec = f"Long bias ({long_rate:.1f}% win rate)"
            elif short_rate > 60:
                tf_rec = f"Short bias ({short_rate:.1f}% win rate)"
            else:
                tf_rec = f"Neutral (Long: {long_rate:.1f}%, Short: {short_rate:.1f}%)"
            
            recommendations["timeframe_recommendations"][timeframe] = tf_rec
        
        # Position sizing based on confidence
        if confidence > 80:
            recommendations["position_sizing"] = "Standard position size"
        elif confidence > 60:
            recommendations["position_sizing"] = "Reduced position size (75% of standard)"
        else:
            recommendations["position_sizing"] = "Minimal position size (50% of standard)"
        
        # Risk management
        recommendations["risk_management"] = f"Use {2 if confidence > 70 else 1.5}% risk per trade"
        recommendations["stop_loss_guidance"] = "Place stops beyond key support/resistance levels"
        
        return recommendations
    
    def _assess_comprehensive_risks(self, symbol: str, metrics: Dict[str, Any], market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess comprehensive risk factors"""
        
        risks = {
            "market_risks": [],
            "technical_risks": [],
            "liquidity_risks": [],
            "sentiment_risks": [],
            "overall_risk_level": "Medium"
        }
        
        # Market risks
        if metrics["liquidation_indicators"]:
            liq_data = metrics["liquidation_indicators"]
            total_liq = liq_data["total_long_liquidations"] + liq_data["total_short_liquidations"]
            if total_liq > 5000000:  # High liquidation activity
                risks["market_risks"].append("High liquidation activity indicates volatile conditions")
        
        # Technical risks
        if metrics["trend_indicators"]:
            trend_data = metrics["trend_indicators"]
            if abs(trend_data["trend_score"] - 50) < 10:  # Neutral trend
                risks["technical_risks"].append("Weak trend signals increase directional uncertainty")
        
        # Sentiment risks
        if "ls_ratio" in metrics["sentiment_indicators"]:
            ls_data = metrics["sentiment_indicators"]["ls_ratio"]
            long_pct = ls_data["long_percentage"]
            if long_pct > 85 or long_pct < 15:
                risks["sentiment_risks"].append("Extreme sentiment positioning increases reversal risk")
        
        # Data quality risks
        data_coverage = len(metrics["data_sources"]) / 18
        if data_coverage < 0.7:
            risks["market_risks"].append("Limited data availability may affect analysis accuracy")
        
        # Determine overall risk level
        total_risks = len(risks["market_risks"]) + len(risks["technical_risks"]) + len(risks["liquidity_risks"]) + len(risks["sentiment_risks"])
        
        if total_risks > 4:
            risks["overall_risk_level"] = "High"
        elif total_risks < 2:
            risks["overall_risk_level"] = "Low"
        else:
            risks["overall_risk_level"] = "Medium"
        
        return risks
    
    def _calculate_analysis_confidence(self, metrics: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive analysis confidence"""
        
        confidence_factors = []
        
        # Data coverage
        data_coverage = len(metrics["data_sources"]) / 18
        confidence_factors.append(data_coverage * 100)
        
        # Signal consistency
        component_scores = [comp["score"] for comp in scores["components"].values()]
        if component_scores:
            score_std = np.std(component_scores)
            consistency_score = max(0, 100 - score_std * 2)  # Lower std = higher consistency
            confidence_factors.append(consistency_score)
        
        # Data freshness (all data is current, so high score)
        confidence_factors.append(95)
        
        # Endpoint reliability
        reliable_endpoints = len([source for source in metrics["data_sources"] if source.get("status") == "active"])
        reliability_score = (reliable_endpoints / max(1, len(metrics["data_sources"]))) * 100
        confidence_factors.append(reliability_score)
        
        overall_confidence = np.mean(confidence_factors) / 100
        
        return {
            "overall_confidence": overall_confidence,
            "data_coverage_score": data_coverage,
            "signal_consistency_score": consistency_score / 100 if component_scores else 0.5,
            "data_freshness_score": 0.95,
            "endpoint_reliability_score": reliability_score / 100,
            "confidence_level": "High" if overall_confidence > 0.8 else "Medium" if overall_confidence > 0.6 else "Low",
            "confidence_factors": confidence_factors
        }
    
    # =========================================================================
    # SELF-LEARNING SYSTEM
    # =========================================================================
    
    def _init_learning_database(self):
        """Initialize the learning database"""
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # Create learning patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    success_metrics TEXT NOT NULL,
                    improvement_suggestions TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Create analysis history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    endpoint_count INTEGER NOT NULL,
                    processing_time REAL NOT NULL,
                    success_indicators TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("📚 Learning database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing learning database: {e}")
    
    def _load_learning_patterns(self):
        """Load existing learning patterns"""
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM learning_patterns')
            rows = cursor.fetchall()
            
            for row in rows:
                pattern_id, pattern_type, success_metrics, improvement_suggestions, confidence_level, usage_count, last_updated = row
                
                self.learning_patterns[pattern_id] = LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern_type,
                    success_metrics=json.loads(success_metrics),
                    improvement_suggestions=json.loads(improvement_suggestions),
                    confidence_level=confidence_level,
                    usage_count=usage_count,
                    last_updated=datetime.fromisoformat(last_updated)
                )
            
            conn.close()
            logger.info(f"📚 Loaded {len(self.learning_patterns)} learning patterns")
            
        except Exception as e:
            logger.debug(f"No existing learning patterns found: {e}")
    
    def _apply_learning_insights(self, symbol: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learning insights to improve analysis"""
        insights = {
            "patterns_applied": [],
            "confidence_adjustments": [],
            "improvement_suggestions": []
        }
        
        try:
            # Apply relevant learning patterns
            for pattern_id, pattern in self.learning_patterns.items():
                if self._is_pattern_applicable(pattern, symbol, metrics):
                    insights["patterns_applied"].append({
                        "pattern_id": pattern_id,
                        "pattern_type": pattern.pattern_type,
                        "confidence_boost": pattern.confidence_level
                    })
                    
                    # Update usage count
                    pattern.usage_count += 1
                    pattern.last_updated = datetime.now()
            
            # Generate improvement suggestions based on current analysis
            if len(metrics["data_sources"]) < 10:
                insights["improvement_suggestions"].append("Increase endpoint coverage for higher confidence")
            
            if not metrics["trend_indicators"]:
                insights["improvement_suggestions"].append("Trend analysis data would improve directional confidence")
            
        except Exception as e:
            logger.debug(f"Error applying learning insights: {e}")
        
        return insights
    
    def _is_pattern_applicable(self, pattern: LearningPattern, symbol: str, metrics: Dict[str, Any]) -> bool:
        """Check if a learning pattern is applicable to current analysis"""
        try:
            # Simple pattern matching - can be enhanced
            if pattern.pattern_type == "high_confidence" and len(metrics["data_sources"]) > 15:
                return True
            elif pattern.pattern_type == "volatility_adjustment" and symbol in ["AVAX/USDT", "SOL/USDT"]:
                return True
            elif pattern.pattern_type == "trend_confirmation" and metrics.get("trend_indicators"):
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking pattern applicability: {e}")
            return False
    
    def _learn_from_analysis(self, symbol: str, result: AnalysisResult):
        """Learn from completed analysis to improve future performance"""
        try:
            # Store analysis history
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            success_indicators = {
                "endpoint_coverage": len(result.processed_metrics.get("data_sources", [])) / 18,
                "confidence_level": result.confidence_assessment.get("overall_confidence", 0.5),
                "processing_time": result.analysis_metadata.get("processing_time", 0),
                "data_quality": result.confidence_assessment.get("data_coverage_score", 0)
            }
            
            cursor.execute('''
                INSERT INTO analysis_history 
                (symbol, timestamp, confidence_level, endpoint_count, processing_time, success_indicators)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                result.timestamp.isoformat(),
                result.confidence_assessment.get("overall_confidence", 0.5),
                len(result.processed_metrics.get("data_sources", [])),
                result.analysis_metadata.get("processing_time", 0),
                json.dumps(success_indicators)
            ))
            
            conn.commit()
            conn.close()
            
            # Update learning patterns based on success
            self._update_learning_patterns(symbol, result, success_indicators)
            
            self.stats["learning_improvements"] += 1
            
        except Exception as e:
            logger.debug(f"Error learning from analysis: {e}")
    
    def _update_learning_patterns(self, symbol: str, result: AnalysisResult, success_indicators: Dict[str, float]):
        """Update learning patterns based on analysis success"""
        try:
            # Create new patterns based on successful analysis
            if success_indicators["confidence_level"] > 0.8 and success_indicators["endpoint_coverage"] > 0.8:
                pattern_id = f"high_success_{symbol}_{int(time.time())}"
                
                new_pattern = LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type="high_success",
                    success_metrics=success_indicators,
                    improvement_suggestions=["Maintain high endpoint coverage", "Continue symbol-specific adjustments"],
                    confidence_level=success_indicators["confidence_level"],
                    usage_count=1,
                    last_updated=datetime.now()
                )
                
                self.learning_patterns[pattern_id] = new_pattern
                
                # Store in database
                conn = sqlite3.connect(self.learning_db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO learning_patterns 
                    (pattern_id, pattern_type, success_metrics, improvement_suggestions, confidence_level, usage_count, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_pattern.pattern_id,
                    new_pattern.pattern_type,
                    json.dumps(new_pattern.success_metrics),
                    json.dumps(new_pattern.improvement_suggestions),
                    new_pattern.confidence_level,
                    new_pattern.usage_count,
                    new_pattern.last_updated.isoformat()
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"📚 Created new learning pattern: {pattern_id}")
                
        except Exception as e:
            logger.debug(f"Error updating learning patterns: {e}")
    
    # =========================================================================
    # PROFESSIONAL REPORT GENERATION
    # =========================================================================
    
    def _generate_executive_summary(self, symbol: str, scores: Dict[str, Any], win_rates: Dict[str, Any], 
                                   market_analysis: Dict[str, Any], confidence: Dict[str, Any]) -> str:
        """Generate professional executive summary"""
        
        symbol_clean = symbol.replace('/', ' ')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        
        long_score = scores["final_scores"]["long_score"]
        short_score = scores["final_scores"]["short_score"]
        overall_confidence = confidence.get("overall_confidence", 0.5)
        
        content = f"""# {symbol_clean} Analysis - Executive Summary & Key Metrics

*🚀 Unified Analysis Agent - Professional Trading Analysis*
*Generated: {current_time}*
*Analysis Confidence: {overall_confidence:.1%} | Symbol-Specific Adjustments: Active*

---

## Quick Reference Guide

| **Metric** | **Value** | **Confidence** |
|------------|-----------|----------------|
| **Long Position Score** | **{long_score:.1f}/100** | {confidence.get('confidence_level', 'Medium')} |
| **Short Position Score** | **{short_score:.1f}/100** | {confidence.get('confidence_level', 'Medium')} |
| **Market Direction** | **{market_analysis.get('current_market_condition', {}).get('direction', 'NEUTRAL')}** | {market_analysis.get('current_market_condition', {}).get('strength', 'Moderate')} |
| **Analysis Quality** | **{overall_confidence:.1%}** | 18-Endpoint Coverage |

---

## 🎯 WIN RATE SUMMARY

### Long Positions
"""
        
        timeframes = win_rates.get("timeframes", {})
        if timeframes:
            for tf, rates in timeframes.items():
                content += f"- **{tf.replace('-', ' to ')}:** {rates.get('long', 50):.1f}% win rate\n"
        else:
            content += "- **Data unavailable**\n"
        
        content += "\n### Short Positions\n"
        
        if timeframes:
            for tf, rates in timeframes.items():
                content += f"- **{tf.replace('-', ' to ')}:** {rates.get('short', 50):.1f}% win rate\n"
        else:
            content += "- **Data unavailable**\n"
        
        content += f"""

---

## 📊 COMPOSITE SCORES

- **Long Position Score:** {long_score:.1f}/100
- **Short Position Score:** {short_score:.1f}/100

*Scores calculated using symbol-specific adjustments for {symbol}*

---

## 🔑 KEY MARKET METRICS

### Current Market Analysis
- **Direction:** {market_analysis.get('current_market_condition', {}).get('direction', 'Neutral')}
- **Strength:** {market_analysis.get('current_market_condition', {}).get('strength', 'Moderate')}
- **Confidence Level:** {market_analysis.get('current_market_condition', {}).get('confidence', 50):.1f}%

### Data Quality Assessment
- **Overall Confidence:** {confidence.get('confidence_level', 'Medium')}
- **Data Coverage:** {confidence.get('data_coverage_score', 0):.1%}
- **Signal Consistency:** {confidence.get('signal_consistency_score', 0.5):.1%}

---

## 📈 TRADING RECOMMENDATIONS

**Primary Direction:** {market_analysis.get('current_market_condition', {}).get('direction', 'NEUTRAL')}

**Market Condition:** {market_analysis.get('current_market_condition', {}).get('strength', 'Moderate')} {market_analysis.get('current_market_condition', {}).get('direction', 'neutral').lower()} bias

**Risk Level:** {confidence.get('confidence_level', 'Medium')} confidence analysis

---

## 💡 KEY INSIGHTS
"""
        
        insights = market_analysis.get('key_insights', [])
        if insights:
            for insight in insights[:5]:
                content += f"- {insight}\n"
        else:
            content += f"- Professional analysis based on 18-endpoint Cryptometer data\n"
            content += f"- Symbol-specific adjustments applied for {symbol}\n"
            content += f"- Advanced win rate calculations with timeframe factors\n"
        
        content += f"""

---

## 🚨 IMMEDIATE ACTION ITEMS

1. **Monitor Market Conditions:** Track {symbol_clean} price movements and key levels
2. **Risk Management:** Use appropriate position sizing based on {confidence.get('confidence_level', 'Medium').lower()} confidence
3. **Timeframe Selection:** Consider win rates across different timeframes for optimal entry
4. **Data Refresh:** Analysis cached with intelligent TTL based on market volatility
5. **Professional Execution:** Follow symbol-specific recommendations

---

*🚀 Powered by Unified Analysis Agent - The Ultimate Cryptocurrency Analysis System*
*Features: 18-endpoint analysis, Symbol-specific scoring, Advanced win rates, Intelligent caching, Self-learning*

**Analysis Quality:** {overall_confidence:.1%} | **Cache Status:** Active | **Last Updated:** {current_time}
"""
        
        return content
    
    def _generate_comprehensive_report(self, symbol: str, metrics: Dict[str, Any], scores: Dict[str, Any], 
                                     win_rates: Dict[str, Any], market_analysis: Dict[str, Any], 
                                     recommendations: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
        """Generate comprehensive analysis report"""
        
        # Start with executive summary
        executive_content = self._generate_executive_summary(symbol, scores, win_rates, market_analysis, 
                                                           scores.get("confidence_assessment", {}))
        
        # Add comprehensive sections
        comprehensive_content = executive_content + f"""

---

# {symbol.replace('/', ' ')} Comprehensive Analysis Report

## 📊 DETAILED ENDPOINT ANALYSIS

### 18-Endpoint Data Collection Results
"""
        
        # Add endpoint analysis details
        data_sources = metrics.get("data_sources", [])
        for i, source in enumerate(data_sources, 1):
            comprehensive_content += f"""
#### {i}. {source['name'].replace('_', ' ').title()}
- **Description:** {source['description']}
- **Weight:** {source['weight']:.1f}
- **Analysis Type:** {source['analysis_type'].title()}
- **Status:** {source['status'].title()}
"""
        
        comprehensive_content += f"""

---

## 🔍 SYMBOL-SPECIFIC ADJUSTMENTS

### {symbol} Configuration Applied
"""
        
        # Add symbol-specific details
        symbol_adjustments = scores.get("symbol_adjustments", {})
        if symbol_adjustments:
            comprehensive_content += f"""
- **Predictability Factor:** {symbol_adjustments.get('predictability_factor', 1.0):.2f}
- **Volatility Adjustment:** {symbol_adjustments.get('volatility_adjustment', 1.0):.2f}
- **Long-term Bias:** {symbol_adjustments.get('long_term_bias', 1.0):.2f}
- **Liquidity Factor:** {symbol_adjustments.get('liquidity_factor', 1.0):.2f}
- **Fundamental Strength:** {symbol_adjustments.get('fundamental_strength', 1.0):.2f}
- **Technical Reliability:** {symbol_adjustments.get('technical_reliability', 1.0):.2f}
"""
        
        comprehensive_content += f"""

---

## 📈 ADVANCED WIN RATE METHODOLOGY

### Professional Calculation Framework
"""
        
        # Add win rate methodology details
        methodology = win_rates.get("methodology", "Advanced Multi-Factor Win Rate Calculation")
        comprehensive_content += f"""
**Methodology:** {methodology}

**Adjustments Applied:**
"""
        
        adjustments = win_rates.get("adjustments_applied", {})
        for adjustment, status in adjustments.items():
            comprehensive_content += f"- **{adjustment.replace('_', ' ').title()}:** {'✅ Active' if status else '❌ Inactive'}\n"
        
        comprehensive_content += f"""

### Timeframe Analysis
"""
        
        timeframes = win_rates.get("timeframes", {})
        for tf, rates in timeframes.items():
            comprehensive_content += f"""
#### {tf.replace('-', ' to ').upper()}
- **Long Position:** {rates.get('long', 50):.1f}% win rate
- **Short Position:** {rates.get('short', 50):.1f}% win rate
"""
        
        comprehensive_content += f"""

---

## 🎯 TRADING RECOMMENDATIONS

### Professional Trading Guidance
"""
        
        # Add detailed recommendations
        for key, value in recommendations.items():
            if isinstance(value, dict):
                comprehensive_content += f"\n**{key.replace('_', ' ').title()}:**\n"
                for sub_key, sub_value in value.items():
                    comprehensive_content += f"- **{sub_key.replace('_', ' ').title()}:** {sub_value}\n"
            else:
                comprehensive_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        comprehensive_content += f"""

---

## ⚠️ COMPREHENSIVE RISK ASSESSMENT

### Risk Analysis
"""
        
        # Add risk assessment details
        for risk_type, risks in risk_assessment.items():
            if isinstance(risks, list) and risks:
                comprehensive_content += f"\n**{risk_type.replace('_', ' ').title()}:**\n"
                for risk in risks:
                    comprehensive_content += f"- {risk}\n"
            elif not isinstance(risks, list):
                comprehensive_content += f"- **{risk_type.replace('_', ' ').title()}:** {risks}\n"
        
        comprehensive_content += f"""

---

## 🚀 SYSTEM PERFORMANCE METRICS

### Analysis Statistics
- **Processing Time:** {metrics.get('summary', {}).get('processing_time', 'N/A')}
- **Endpoint Coverage:** {len(data_sources)}/18 ({len(data_sources)/18:.1%})
- **Data Quality Score:** {scores.get('confidence_assessment', {}).get('data_coverage_score', 0):.1%}
- **Analysis Confidence:** {scores.get('confidence_assessment', {}).get('confidence_level', 'Medium')}

### Features Active
✅ 18-endpoint comprehensive analysis
✅ Symbol-specific scoring adjustments
✅ Advanced win rate calculations
✅ Intelligent caching system
✅ Self-learning capabilities
✅ Professional report generation

---

*🚀 Generated by Unified Analysis Agent - The Ultimate Cryptocurrency Analysis System*
*This comprehensive analysis combines all advanced features in a single, powerful module for professional trading decisions.*

**Disclaimer:** This analysis is for informational purposes only. Always conduct your own research and consider your risk tolerance before making trading decisions.
"""
        
        return comprehensive_content
    
    # =========================================================================
    # UTILITY & MANAGEMENT METHODS
    # =========================================================================
    
    def _create_fallback_result(self, symbol: str, error: str) -> AnalysisResult:
        """Create fallback result when analysis fails"""
        
        return AnalysisResult(
            symbol=symbol,
            timestamp=datetime.now(),
            raw_endpoint_data={},
            processed_metrics={"data_sources": [], "summary": {"successful_endpoints": 0}},
            composite_scores={
                "final_scores": {
                    "long_score": 45.0,
                    "short_score": 55.0,
                    "confidence_level": 30.0
                }
            },
            win_rates={
                "timeframes": {
                    "24-48h": {"long": 45.0, "short": 55.0},
                    "7d": {"long": 47.0, "short": 53.0},
                    "1m": {"long": 50.0, "short": 50.0}
                }
            },
            market_analysis={
                "current_market_condition": {
                    "direction": "Neutral",
                    "strength": "Limited Data",
                    "confidence": 30.0
                },
                "key_insights": [f"Analysis limited due to: {error}"]
            },
            recommendations={
                "primary_direction": "NEUTRAL",
                "entry_strategy": "Wait for better data availability"
            },
            risk_assessment={
                "overall_risk_level": "High",
                "market_risks": ["Limited data availability", "Analysis accuracy reduced"]
            },
            analysis_metadata={
                "processing_time": 0.0,
                "endpoints_used": 0,
                "total_endpoints": 18,
                "error": error
            },
            confidence_assessment={
                "overall_confidence": 0.3,
                "confidence_level": "Low"
            },
            cache_info={"cached": False, "error": True},
            learning_insights={},
            executive_summary=f"# {symbol.replace('/', ' ')} Analysis - Limited Data\n\nAnalysis temporarily unavailable due to: {error}",
            comprehensive_report=f"# {symbol.replace('/', ' ')} Analysis - Error Report\n\nSystem encountered an error: {error}\n\nPlease try again later."
        )
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_name": "Unified Analysis Agent",
            "version": "1.0.0",
            "status": "active",
            "features": {
                "18_endpoint_analysis": True,
                "symbol_specific_scoring": True,
                "advanced_win_rates": True,
                "intelligent_caching": True,
                "self_learning": True,
                "professional_reports": True
            },
            "statistics": self.stats,
            "cache_info": {
                "memory_cache_size": len(self.memory_cache),
                "cache_directory": self.cache_dir,
                "default_ttl_minutes": self.default_ttl_minutes
            },
            "learning_info": {
                "learning_patterns": len(self.learning_patterns),
                "database_path": self.learning_db_path
            },
            "supported_symbols": list(self.symbol_configs.keys()),
            "endpoints_configured": len(self.endpoints)
        }
    
    async def invalidate_cache(self, symbol: str) -> Dict[str, Any]:
        """Invalidate cache for specific symbol"""
        try:
            cache_key = self._generate_cache_key(symbol)
            
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            # Remove from file cache
            file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            logger.info(f"🗑️ Cache invalidated for {symbol}")
            return {"success": True, "symbol": symbol, "message": f"Cache invalidated for {symbol}"}
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {symbol}: {e}")
            return {"success": False, "error": str(e), "symbol": symbol}
    
    async def cleanup_expired_cache(self) -> Dict[str, Any]:
        """Clean up expired cache entries"""
        try:
            cleaned_count = 0
            now = datetime.now()
            
            # Clean memory cache
            expired_keys = [
                key for key, entry in self.memory_cache.items() 
                if now >= entry.expires_at
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleaned_count += 1
            
            # Clean file cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        expires_at = datetime.fromisoformat(cache_data["expires_at"])
                        if now >= expires_at:
                            os.remove(file_path)
                            cleaned_count += 1
                            
                    except Exception as e:
                        logger.debug(f"Error checking file {filename}: {e}")
                        os.remove(file_path)
                        cleaned_count += 1
            
            logger.info(f"🧹 Cleaned up {cleaned_count} expired cache entries")
            return {"success": True, "cleaned_entries": cleaned_count}
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return {"success": False, "error": str(e)}
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

# =============================================================================
# GLOBAL INSTANCE - READY TO USE
# =============================================================================

# Create the global unified agent instance
unified_analysis_agent = UnifiedAnalysisAgent()

# =============================================================================
# CONVENIENCE FUNCTIONS FOR EASY ACCESS
# =============================================================================

async def analyze_symbol(symbol: str, force_refresh: bool = False) -> AnalysisResult:
    """Convenience function for symbol analysis"""
    async with unified_analysis_agent as agent:
        return await agent.analyze_symbol(symbol, force_refresh)

async def get_executive_summary(symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Convenience function for executive summary"""
    async with unified_analysis_agent as agent:
        return await agent.generate_executive_summary(symbol, force_refresh)

async def get_comprehensive_report(symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Convenience function for comprehensive report"""
    async with unified_analysis_agent as agent:
        return await agent.generate_comprehensive_report(symbol, force_refresh)

async def get_system_status() -> Dict[str, Any]:
    """Convenience function for system status"""
    return await unified_analysis_agent.get_system_status()

# =============================================================================
# END OF UNIFIED ANALYSIS AGENT
# =============================================================================

logger.info("🚀 Unified Analysis Agent module loaded - ALL FEATURES READY!")