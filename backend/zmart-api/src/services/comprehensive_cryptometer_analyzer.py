#!/usr/bin/env python3
"""
Comprehensive Cryptometer Analyzer
Advanced implementation based on the comprehensive analysis package
Includes 18-endpoint analysis, symbol-specific scoring, and advanced win rate calculations
"""

import asyncio
import aiohttp
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

from src.config.settings import settings
from src.services.enhanced_cache_manager import cache_manager

logger = logging.getLogger(__name__)

@dataclass
class SymbolSpecificConfig:
    """Symbol-specific configuration for analysis"""
    symbol: str
    predictability_factor: float  # How predictable the asset is (0.8-1.2)
    volatility_adjustment: float  # Volatility impact on win rates (0.8-1.2)
    long_term_bias: float  # Long-term directional bias (0.8-1.2)
    liquidity_factor: float  # Liquidity impact (0.9-1.1)
    fundamental_strength: float  # Fundamental analysis weight (0.8-1.2)
    technical_reliability: float  # Technical analysis reliability (0.8-1.2)

@dataclass
class EndpointConfiguration:
    """Enhanced endpoint configuration"""
    name: str
    endpoint: str
    params: Dict[str, Any]
    description: str
    weight: float
    analysis_type: str
    win_rate_impact: str
    reliability_threshold: float

@dataclass
class ComprehensiveAnalysisResult:
    """Comprehensive analysis result structure"""
    symbol: str
    timestamp: datetime
    analysis_metadata: Dict[str, Any]
    raw_endpoint_data: Dict[str, Any]
    processed_metrics: Dict[str, Any]
    composite_scores: Dict[str, Any]
    win_rates: Dict[str, Any]
    market_analysis: Dict[str, Any]
    recommendations: Dict[str, Any]
    confidence_assessment: Dict[str, Any]
    cache_info: Dict[str, Any]

class ComprehensiveCryptometerAnalyzer:
    """
    Advanced Cryptometer analyzer implementing the comprehensive package features
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Comprehensive Cryptometer Analyzer"""
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        self.base_url = "https://api.cryptometer.io"
        self.session = None
        
        # Enhanced 18-endpoint configuration
        self.endpoints = self._initialize_enhanced_endpoints()
        
        # Symbol-specific configurations
        self.symbol_configs = self._initialize_symbol_configs()
        
        logger.info("Comprehensive Cryptometer Analyzer initialized with 18 endpoints")
    
    def _initialize_enhanced_endpoints(self) -> Dict[str, EndpointConfiguration]:
        """Initialize all 18 Cryptometer endpoints with enhanced configuration"""
        return {
            "market_list": EndpointConfiguration(
                name="market_list",
                endpoint="/coinlist/",
                params={"e": "binance"},
                description="Market List - Available trading pairs",
                weight=5.0,
                analysis_type="fundamental",
                win_rate_impact="low",
                reliability_threshold=0.9
            ),
            "crypto_info": EndpointConfiguration(
                name="crypto_info",
                endpoint="/cryptocurrency-info/",
                params={"e": "binance", "filter": "defi"},
                description="Cryptocurrency Info - Market data and metrics",
                weight=15.0,
                analysis_type="fundamental",
                win_rate_impact="high",
                reliability_threshold=0.8
            ),
            "coin_info": EndpointConfiguration(
                name="coin_info",
                endpoint="/coininfo/",
                params={},
                description="Coin Info - Fundamental data",
                weight=10.0,
                analysis_type="fundamental",
                win_rate_impact="medium",
                reliability_threshold=0.8
            ),
            "forex_rates": EndpointConfiguration(
                name="forex_rates",
                endpoint="/forex-rates/",
                params={"source": "USD"},
                description="Forex Rates - Currency conversion rates",
                weight=5.0,
                analysis_type="macro",
                win_rate_impact="low",
                reliability_threshold=0.9
            ),
            "volume_flow": EndpointConfiguration(
                name="volume_flow",
                endpoint="/volume-flow/",
                params={"timeframe": "1h"},
                description="Volume Flow - Money flow analysis",
                weight=20.0,
                analysis_type="volume",
                win_rate_impact="very_high",
                reliability_threshold=0.7
            ),
            "liquidity_lens": EndpointConfiguration(
                name="liquidity_lens",
                endpoint="/liquidity-lens/",
                params={"timeframe": "1h"},
                description="Liquidity Lens - Liquidity analysis",
                weight=18.0,
                analysis_type="volume",
                win_rate_impact="high",
                reliability_threshold=0.7
            ),
            "volatility_index": EndpointConfiguration(
                name="volatility_index",
                endpoint="/volatility-index/",
                params={"e": "binance", "timeframe": "1h"},
                description="Volatility Index - Market volatility metrics",
                weight=12.0,
                analysis_type="technical",
                win_rate_impact="medium",
                reliability_threshold=0.8
            ),
            "ohlcv": EndpointConfiguration(
                name="ohlcv",
                endpoint="/ohlcv/",
                params={"e": "binance", "timeframe": "1h"},
                description="OHLCV Candles - Price and volume data",
                weight=25.0,
                analysis_type="technical",
                win_rate_impact="very_high",
                reliability_threshold=0.9
            ),
            "ls_ratio": EndpointConfiguration(
                name="ls_ratio",
                endpoint="/ls-v1/",
                params={},
                description="Long/Short Ratio - Sentiment indicator",
                weight=15.0,
                analysis_type="sentiment",
                win_rate_impact="high",
                reliability_threshold=0.8
            ),
            "tickerlist_pro": EndpointConfiguration(
                name="tickerlist_pro",
                endpoint="/tickerlist-pro/",
                params={"e": "binance"},
                description="Tickerlist Pro - Advanced ticker data",
                weight=12.0,
                analysis_type="technical",
                win_rate_impact="medium",
                reliability_threshold=0.8
            ),
            "merged_volume": EndpointConfiguration(
                name="merged_volume",
                endpoint="/merged-volume/",
                params={"timeframe": "1h"},
                description="Merged Buy/Sell Volume - Order flow analysis",
                weight=22.0,
                analysis_type="volume",
                win_rate_impact="very_high",
                reliability_threshold=0.7
            ),
            "liquidation_data": EndpointConfiguration(
                name="liquidation_data",
                endpoint="/liquidation-v2/",
                params={},
                description="Total Liquidation Data - Risk assessment",
                weight=18.0,
                analysis_type="risk",
                win_rate_impact="high",
                reliability_threshold=0.7
            ),
            "trend_indicator": EndpointConfiguration(
                name="trend_indicator",
                endpoint="/trend-v3/",
                params={},
                description="Trend Indicator V3 - Advanced trend analysis",
                weight=25.0,
                analysis_type="trend",
                win_rate_impact="very_high",
                reliability_threshold=0.8
            ),
            "rapid_movements": EndpointConfiguration(
                name="rapid_movements",
                endpoint="/rapid-v1/",
                params={},
                description="Rapid Movements - Momentum detection",
                weight=20.0,
                analysis_type="momentum",
                win_rate_impact="high",
                reliability_threshold=0.7
            ),
            "whale_trades": EndpointConfiguration(
                name="whale_trades",
                endpoint="/xtrades/",
                params={},
                description="Whale Trades (xTrade) - Large transaction analysis",
                weight=15.0,
                analysis_type="whale",
                win_rate_impact="high",
                reliability_threshold=0.6
            ),
            "large_trades": EndpointConfiguration(
                name="large_trades",
                endpoint="/whale-v2/",
                params={},
                description="Large Trades Activity - Institutional flow",
                weight=18.0,
                analysis_type="whale",
                win_rate_impact="high",
                reliability_threshold=0.7
            ),
            "ai_screener": EndpointConfiguration(
                name="ai_screener",
                endpoint="/ai-screener/",
                params={},
                description="AI Screener - Machine learning insights",
                weight=15.0,
                analysis_type="ai",
                win_rate_impact="medium",
                reliability_threshold=0.6
            ),
            "ai_screener_analysis": EndpointConfiguration(
                name="ai_screener_analysis",
                endpoint="/ai-screener-analysis/",
                params={},
                description="AI Screener Analysis - Advanced AI insights",
                weight=12.0,
                analysis_type="ai",
                win_rate_impact="medium",
                reliability_threshold=0.6
            )
        }
    
    def _initialize_symbol_configs(self) -> Dict[str, SymbolSpecificConfig]:
        """Initialize symbol-specific configurations"""
        return {
            "BTC/USDT": SymbolSpecificConfig(
                symbol="BTC/USDT",
                predictability_factor=1.1,  # BTC is relatively predictable
                volatility_adjustment=1.0,  # Standard volatility
                long_term_bias=1.15,  # Strong long-term uptrend
                liquidity_factor=1.1,  # Excellent liquidity
                fundamental_strength=1.2,  # Strong fundamentals
                technical_reliability=1.1  # Reliable technical patterns
            ),
            "ETH/USDT": SymbolSpecificConfig(
                symbol="ETH/USDT",
                predictability_factor=1.05,  # ETH is fairly predictable
                volatility_adjustment=1.1,  # Slightly more volatile than BTC
                long_term_bias=1.1,  # Good long-term prospects
                liquidity_factor=1.05,  # Good liquidity
                fundamental_strength=1.15,  # Strong fundamentals (DeFi, staking)
                technical_reliability=1.0  # Standard technical reliability
            ),
            "AVAX/USDT": SymbolSpecificConfig(
                symbol="AVAX/USDT",
                predictability_factor=0.9,  # More volatile, less predictable
                volatility_adjustment=1.2,  # Higher volatility
                long_term_bias=1.0,  # Neutral long-term bias
                liquidity_factor=0.95,  # Lower liquidity than BTC/ETH
                fundamental_strength=1.0,  # Moderate fundamentals
                technical_reliability=0.9  # Less reliable patterns
            ),
            "SOL/USDT": SymbolSpecificConfig(
                symbol="SOL/USDT",
                predictability_factor=0.85,  # High volatility, less predictable
                volatility_adjustment=1.25,  # High volatility
                long_term_bias=1.05,  # Moderate long-term potential
                liquidity_factor=0.9,  # Moderate liquidity
                fundamental_strength=1.05,  # Growing ecosystem
                technical_reliability=0.85  # Less reliable due to volatility
            )
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze_symbol_comprehensive(self, symbol: str, force_refresh: bool = False) -> ComprehensiveAnalysisResult:
        """
        Comprehensive analysis using all 18 endpoints with caching
        """
        logger.info(f"Starting comprehensive analysis for {symbol}")
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = cache_manager.get(symbol, "comprehensive")
            if cached_result:
                logger.info(f"Returning cached analysis for {symbol}")
                # Convert cached dict back to ComprehensiveAnalysisResult
                return ComprehensiveAnalysisResult(**cached_result)
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            start_time = datetime.now()
            
            # Phase 1: Collect all endpoint data
            raw_data = await self._collect_all_endpoint_data(symbol)
            
            # Phase 2: Process and analyze data
            processed_metrics = self._process_comprehensive_metrics(symbol, raw_data)
            
            # Phase 3: Calculate composite scores
            composite_scores = self._calculate_advanced_composite_scores(symbol, processed_metrics)
            
            # Phase 4: Calculate enhanced win rates
            win_rates = self._calculate_enhanced_win_rates(symbol, composite_scores, processed_metrics)
            
            # Phase 5: Generate market analysis
            market_analysis = self._generate_comprehensive_market_analysis(symbol, processed_metrics, composite_scores)
            
            # Phase 6: Generate recommendations
            recommendations = self._generate_advanced_recommendations(symbol, composite_scores, win_rates, market_analysis)
            
            # Phase 7: Assess confidence
            confidence_assessment = self._assess_analysis_confidence(processed_metrics, composite_scores)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create comprehensive result
            result = ComprehensiveAnalysisResult(
                symbol=symbol,
                timestamp=datetime.now(),
                analysis_metadata={
                    "analysis_type": "Comprehensive Multi-Source Professional Analysis",
                    "endpoints_used": len([ep for ep in raw_data.values() if ep.get("success")]),
                    "total_endpoints": len(self.endpoints),
                    "processing_time": processing_time,
                    "api_key_used": self.api_key[:10] + "...",
                    "cache_enabled": True
                },
                raw_endpoint_data=raw_data,
                processed_metrics=processed_metrics,
                composite_scores=composite_scores,
                win_rates=win_rates,
                market_analysis=market_analysis,
                recommendations=recommendations,
                confidence_assessment=confidence_assessment,
                cache_info=cache_manager.get_cache_info(symbol)
            )
            
            # Cache the result
            result_dict = asdict(result)
            cache_manager.set(
                symbol, 
                result_dict, 
                "comprehensive", 
                confidence_assessment.get("overall_confidence", 0.5)
            )
            
            logger.info(f"Comprehensive analysis completed for {symbol} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            return self._create_fallback_comprehensive_result(symbol, str(e))
    
    async def _collect_all_endpoint_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data from all 18 endpoints"""
        raw_data = {}
        
        for endpoint_name, config in self.endpoints.items():
            try:
                logger.debug(f"Collecting data from {endpoint_name}")
                
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
                    error_msg = data.get('error', 'No data') if data else 'No data'
                    logger.warning(f"⚠️ {endpoint_name}: {error_msg}")
                    
            except Exception as e:
                logger.error(f"❌ Error collecting {endpoint_name}: {e}")
                raw_data[endpoint_name] = {
                    "config": asdict(config),
                    "data": {"success": "false", "error": str(e)},
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
        
        return raw_data
    
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
            
            # Process based on endpoint type
            self._process_endpoint_specific_metrics(endpoint_name, data, metrics, symbol)
        
        metrics["summary"] = {
            "successful_endpoints": successful_endpoints,
            "total_endpoints": len(self.endpoints),
            "data_coverage": successful_endpoints / len(self.endpoints),
            "primary_analysis_types": list(set([
                source["analysis_type"] for source in metrics["data_sources"]
            ]))
        }
        
        return metrics
    
    def _process_endpoint_specific_metrics(self, endpoint_name: str, data: Dict[str, Any], metrics: Dict[str, Any], symbol: str):
        """Process metrics for specific endpoints"""
        
        if endpoint_name == "trend_indicator":
            trend_data = data.get("data", [])
            if trend_data and isinstance(trend_data, list):
                # Find data for our symbol
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
        
        # Add more endpoint processing as needed...
    
    def _calculate_advanced_composite_scores(self, symbol: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced composite scores with symbol-specific adjustments"""
        
        # Get symbol-specific configuration
        symbol_config = self.symbol_configs.get(symbol, self.symbol_configs["BTC/USDT"])  # Default to BTC config
        
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
    
    def _calculate_enhanced_win_rates(self, symbol: str, composite_scores: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate enhanced win rates using advanced methodology"""
        
        symbol_config = self.symbol_configs.get(symbol, self.symbol_configs["BTC/USDT"])
        
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
            "methodology": f"Enhanced Multi-Factor Win Rate Calculation for {symbol}",
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
    
    def _generate_comprehensive_market_analysis(self, symbol: str, metrics: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive market analysis"""
        
        analysis = {
            "current_market_condition": {},
            "key_insights": [],
            "risk_factors": [],
            "opportunity_indicators": [],
            "market_structure": {},
            "institutional_activity": {}
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
                analysis["risk_factors"].append("Heavy long liquidations indicate potential oversold conditions")
            else:
                analysis["risk_factors"].append("Heavy short liquidations indicate potential overbought conditions")
        
        return analysis
    
    def _generate_advanced_recommendations(self, symbol: str, scores: Dict[str, Any], win_rates: Dict[str, Any], market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced trading recommendations"""
        
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
    
    def _assess_analysis_confidence(self, metrics: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall analysis confidence"""
        
        confidence_factors = []
        
        # Data coverage
        data_coverage = len(metrics["data_sources"]) / 18
        confidence_factors.append(data_coverage * 100)
        
        # Signal consistency
        component_scores = [comp["score"] for comp in scores["components"].values()]
        score_std = np.std(component_scores)
        consistency_score = max(0, 100 - score_std * 2)  # Lower std = higher consistency
        confidence_factors.append(consistency_score)
        
        # Data freshness (all data is current, so high score)
        confidence_factors.append(95)
        
        overall_confidence = np.mean(confidence_factors) / 100
        
        return {
            "overall_confidence": overall_confidence,
            "data_coverage_score": data_coverage,
            "signal_consistency_score": consistency_score / 100,
            "data_freshness_score": 0.95,
            "confidence_level": "High" if overall_confidence > 0.8 else "Medium" if overall_confidence > 0.6 else "Low"
        }
    
    async def _make_api_call(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API call to Cryptometer endpoint"""
        try:
            if self.session is None:
                logger.error("Session not initialized. Use 'async with analyzer:' context manager.")
                return None
                
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
    
    def _create_fallback_comprehensive_result(self, symbol: str, error: str) -> ComprehensiveAnalysisResult:
        """Create fallback result when analysis fails"""
        
        return ComprehensiveAnalysisResult(
            symbol=symbol,
            timestamp=datetime.now(),
            analysis_metadata={
                "analysis_type": "Fallback Analysis",
                "endpoints_used": 0,
                "total_endpoints": len(self.endpoints),
                "processing_time": 0.0,
                "error": error
            },
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
            confidence_assessment={
                "overall_confidence": 0.3,
                "confidence_level": "Low"
            },
            cache_info={"cached": False}
        )

# Global instance for easy access
comprehensive_cryptometer_analyzer = ComprehensiveCryptometerAnalyzer()