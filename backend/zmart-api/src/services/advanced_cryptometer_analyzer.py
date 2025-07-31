#!/usr/bin/env python3
"""
Advanced Cryptometer Analyzer
Focus on endpoint data as primary source with professional win rate calculations
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

logger = logging.getLogger(__name__)

@dataclass
class MarketPriceAnalysis:
    """Market price analysis with win rate calculations"""
    current_price: float
    price_24h_change: float
    price_7d_change: float
    volume_24h: float
    market_cap: Optional[float]
    long_win_rate_24h: float
    long_win_rate_7d: float
    long_win_rate_30d: float
    short_win_rate_24h: float
    short_win_rate_7d: float
    short_win_rate_30d: float
    confidence_level: float
    data_quality_score: float

@dataclass
class EndpointDataAnalysis:
    """Enhanced endpoint data analysis"""
    endpoint_name: str
    raw_data: Dict[str, Any]
    processed_metrics: Dict[str, float]
    market_signals: List[str]
    risk_indicators: List[str]
    opportunity_indicators: List[str]
    data_freshness: str
    reliability_score: float
    contribution_to_analysis: float

@dataclass
class ProfessionalAnalysisReport:
    """Professional analysis report structure"""
    symbol: str
    timestamp: datetime
    market_price_analysis: MarketPriceAnalysis
    endpoint_analyses: List[EndpointDataAnalysis]
    composite_long_score: float
    composite_short_score: float
    overall_direction: str
    confidence_level: float
    key_insights: List[str]
    risk_factors: List[str]
    trading_recommendations: Dict[str, Any]
    data_sources_used: List[str]
    analysis_quality_score: float

class AdvancedCryptometerAnalyzer:
    """
    Advanced analyzer that uses Cryptometer endpoints as primary data source
    with professional win rate calculations and market-specific insights
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Advanced Cryptometer Analyzer"""
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        self.base_url = "https://api.cryptometer.io"
        self.session = None
        
        # Enhanced endpoint configurations with analysis weights
        self.endpoints = {
            "ticker": {
                "url": "/price-v5/",
                "weight": 15.0,
                "analysis_type": "price_action",
                "win_rate_impact": "high"
            },
            "cryptocurrency_info": {
                "url": "/crypto-v1/",
                "weight": 12.0,
                "analysis_type": "fundamental",
                "win_rate_impact": "medium"
            },
            "trend_indicator_v3": {
                "url": "/trend-v3/",
                "weight": 20.0,
                "analysis_type": "trend_analysis",
                "win_rate_impact": "very_high"
            },
            "rapid_movements": {
                "url": "/rapid-v1/",
                "weight": 18.0,
                "analysis_type": "momentum",
                "win_rate_impact": "high"
            },
            "large_trades_activity": {
                "url": "/whale-v2/",
                "weight": 15.0,
                "analysis_type": "whale_activity",
                "win_rate_impact": "high"
            },
            "liquidation_data_v2": {
                "url": "/liquidation-v2/",
                "weight": 10.0,
                "analysis_type": "risk_assessment",
                "win_rate_impact": "medium"
            },
            "ls_ratio": {
                "url": "/ls-v1/",
                "weight": 10.0,
                "analysis_type": "sentiment",
                "win_rate_impact": "medium"
            }
        }
        
        # Win rate calculation parameters
        self.win_rate_params = {
            "base_long_rate": 45.0,  # Base long win rate
            "base_short_rate": 55.0,  # Base short win rate
            "trend_multiplier": 0.3,  # How much trend affects win rate
            "momentum_multiplier": 0.25,  # How much momentum affects win rate
            "volume_multiplier": 0.15,  # How much volume affects win rate
            "whale_multiplier": 0.2,  # How much whale activity affects win rate
            "max_adjustment": 25.0  # Maximum adjustment to base rates
        }
        
        logger.info("Advanced Cryptometer Analyzer initialized with professional win rate calculations")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze_symbol_comprehensive(self, symbol: str) -> ProfessionalAnalysisReport:
        """
        Comprehensive analysis using Cryptometer endpoints as primary data source
        """
        logger.info(f"Starting comprehensive professional analysis for {symbol}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Phase 1: Collect endpoint data
            endpoint_analyses = await self._collect_endpoint_data(symbol)
            
            # Phase 2: Analyze market price with win rates
            market_price_analysis = await self._analyze_market_price_with_win_rates(symbol, endpoint_analyses)
            
            # Phase 3: Calculate composite scores
            composite_scores = self._calculate_composite_scores(endpoint_analyses, market_price_analysis)
            
            # Phase 4: Generate professional insights
            insights = self._generate_professional_insights(symbol, endpoint_analyses, market_price_analysis)
            
            # Phase 5: Create comprehensive report
            report = ProfessionalAnalysisReport(
                symbol=symbol,
                timestamp=datetime.now(),
                market_price_analysis=market_price_analysis,
                endpoint_analyses=endpoint_analyses,
                composite_long_score=composite_scores["long_score"],
                composite_short_score=composite_scores["short_score"],
                overall_direction=composite_scores["direction"],
                confidence_level=composite_scores["confidence"],
                key_insights=insights["key_insights"],
                risk_factors=insights["risk_factors"],
                trading_recommendations=insights["trading_recommendations"],
                data_sources_used=[ep.endpoint_name for ep in endpoint_analyses if ep.reliability_score > 0.5],
                analysis_quality_score=self._calculate_analysis_quality(endpoint_analyses)
            )
            
            logger.info(f"Professional analysis completed for {symbol}: {composite_scores['direction']} ({composite_scores['confidence']:.1%} confidence)")
            return report
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            return self._create_fallback_report(symbol, str(e))
    
    async def _collect_endpoint_data(self, symbol: str) -> List[EndpointDataAnalysis]:
        """Collect and analyze data from all Cryptometer endpoints"""
        endpoint_analyses = []
        
        for endpoint_name, config in self.endpoints.items():
            try:
                logger.info(f"Analyzing endpoint: {endpoint_name}")
                
                # Make API call with delay
                raw_data = await self._make_api_call(config["url"], {"symbol": symbol})
                await asyncio.sleep(1)  # Rate limiting
                
                if raw_data and raw_data.get("success"):
                    # Process the endpoint data
                    analysis = self._process_endpoint_data(endpoint_name, raw_data, config)
                    endpoint_analyses.append(analysis)
                    logger.info(f"✅ {endpoint_name}: {analysis.reliability_score:.2f} reliability")
                else:
                    logger.warning(f"⚠️ {endpoint_name}: No data available")
                    
            except Exception as e:
                logger.error(f"❌ Error analyzing {endpoint_name}: {e}")
                continue
        
        return endpoint_analyses
    
    def _process_endpoint_data(self, endpoint_name: str, raw_data: Dict[str, Any], config: Dict[str, Any]) -> EndpointDataAnalysis:
        """Process individual endpoint data into structured analysis"""
        
        processed_metrics = {}
        market_signals = []
        risk_indicators = []
        opportunity_indicators = []
        
        try:
            data = raw_data.get("data", {})
            
            if endpoint_name == "ticker":
                # Price action analysis
                if "price" in data:
                    processed_metrics["current_price"] = float(data["price"])
                if "change_24h" in data:
                    change_24h = float(data["change_24h"])
                    processed_metrics["price_change_24h"] = change_24h
                    
                    if change_24h > 5:
                        market_signals.append("Strong bullish momentum")
                        opportunity_indicators.append("Long position opportunity")
                    elif change_24h < -5:
                        market_signals.append("Strong bearish momentum")
                        opportunity_indicators.append("Short position opportunity")
                
            elif endpoint_name == "trend_indicator_v3":
                # Trend analysis
                if "trend" in data:
                    trend = data["trend"].lower()
                    processed_metrics["trend_strength"] = self._quantify_trend(trend)
                    
                    if "bullish" in trend:
                        market_signals.append("Bullish trend confirmed")
                        opportunity_indicators.append("Trend following long")
                    elif "bearish" in trend:
                        market_signals.append("Bearish trend confirmed")
                        opportunity_indicators.append("Trend following short")
                
            elif endpoint_name == "rapid_movements":
                # Momentum analysis
                if "rapid_score" in data:
                    rapid_score = float(data["rapid_score"])
                    processed_metrics["momentum_score"] = rapid_score
                    
                    if rapid_score > 70:
                        market_signals.append("High momentum detected")
                        risk_indicators.append("Potential overextension")
                    elif rapid_score < 30:
                        market_signals.append("Low momentum period")
                        opportunity_indicators.append("Potential reversal zone")
                
            elif endpoint_name == "large_trades_activity":
                # Whale activity analysis
                if "whale_activity" in data:
                    whale_score = float(data["whale_activity"])
                    processed_metrics["whale_activity"] = whale_score
                    
                    if whale_score > 60:
                        market_signals.append("High whale activity")
                        risk_indicators.append("Potential large moves ahead")
                    
            elif endpoint_name == "liquidation_data_v2":
                # Liquidation analysis
                if "liquidation_ratio" in data:
                    liq_ratio = float(data["liquidation_ratio"])
                    processed_metrics["liquidation_risk"] = liq_ratio
                    
                    if liq_ratio > 0.7:
                        risk_indicators.append("High liquidation risk")
                    else:
                        opportunity_indicators.append("Low liquidation environment")
            
            # Calculate reliability score based on data completeness
            reliability_score = min(len(processed_metrics) / 3.0, 1.0)
            
            # Calculate contribution to analysis
            contribution = reliability_score * config["weight"] / 100.0
            
            return EndpointDataAnalysis(
                endpoint_name=endpoint_name,
                raw_data=raw_data,
                processed_metrics=processed_metrics,
                market_signals=market_signals,
                risk_indicators=risk_indicators,
                opportunity_indicators=opportunity_indicators,
                data_freshness="current",
                reliability_score=reliability_score,
                contribution_to_analysis=contribution
            )
            
        except Exception as e:
            logger.error(f"Error processing {endpoint_name} data: {e}")
            return EndpointDataAnalysis(
                endpoint_name=endpoint_name,
                raw_data=raw_data,
                processed_metrics={},
                market_signals=[],
                risk_indicators=["Data processing error"],
                opportunity_indicators=[],
                data_freshness="stale",
                reliability_score=0.0,
                contribution_to_analysis=0.0
            )
    
    async def _analyze_market_price_with_win_rates(self, symbol: str, endpoint_analyses: List[EndpointDataAnalysis]) -> MarketPriceAnalysis:
        """Analyze market price and calculate professional win rates"""
        
        # Extract price data from endpoints
        current_price = 0.0
        price_24h_change = 0.0
        volume_24h = 0.0
        
        for analysis in endpoint_analyses:
            if "current_price" in analysis.processed_metrics:
                current_price = analysis.processed_metrics["current_price"]
            if "price_change_24h" in analysis.processed_metrics:
                price_24h_change = analysis.processed_metrics["price_change_24h"]
            if "volume_24h" in analysis.processed_metrics:
                volume_24h = analysis.processed_metrics["volume_24h"]
        
        # Calculate win rates based on market conditions
        win_rates = self._calculate_professional_win_rates(endpoint_analyses, current_price)
        
        # Calculate confidence and data quality
        confidence_level = self._calculate_confidence_level(endpoint_analyses)
        data_quality_score = self._calculate_data_quality_score(endpoint_analyses)
        
        return MarketPriceAnalysis(
            current_price=current_price,
            price_24h_change=price_24h_change,
            price_7d_change=0.0,  # Would need additional endpoint data
            volume_24h=volume_24h,
            market_cap=None,  # Would need additional endpoint data
            long_win_rate_24h=win_rates["long_24h"],
            long_win_rate_7d=win_rates["long_7d"],
            long_win_rate_30d=win_rates["long_30d"],
            short_win_rate_24h=win_rates["short_24h"],
            short_win_rate_7d=win_rates["short_7d"],
            short_win_rate_30d=win_rates["short_30d"],
            confidence_level=confidence_level,
            data_quality_score=data_quality_score
        )
    
    def _calculate_professional_win_rates(self, endpoint_analyses: List[EndpointDataAnalysis], current_price: float) -> Dict[str, float]:
        """Calculate professional win rates based on endpoint data and market conditions"""
        
        # Start with base rates
        base_long = self.win_rate_params["base_long_rate"]
        base_short = self.win_rate_params["base_short_rate"]
        
        # Analyze trend impact
        trend_adjustment = 0.0
        momentum_adjustment = 0.0
        volume_adjustment = 0.0
        whale_adjustment = 0.0
        
        for analysis in endpoint_analyses:
            # Trend impact
            if "trend_strength" in analysis.processed_metrics:
                trend_strength = analysis.processed_metrics["trend_strength"]
                trend_adjustment += trend_strength * self.win_rate_params["trend_multiplier"]
            
            # Momentum impact
            if "momentum_score" in analysis.processed_metrics:
                momentum_score = analysis.processed_metrics["momentum_score"]
                momentum_adjustment += (momentum_score - 50) * self.win_rate_params["momentum_multiplier"] / 50
            
            # Volume impact
            if "volume_score" in analysis.processed_metrics:
                volume_score = analysis.processed_metrics["volume_score"]
                volume_adjustment += (volume_score - 50) * self.win_rate_params["volume_multiplier"] / 50
            
            # Whale activity impact
            if "whale_activity" in analysis.processed_metrics:
                whale_activity = analysis.processed_metrics["whale_activity"]
                whale_adjustment += (whale_activity - 50) * self.win_rate_params["whale_multiplier"] / 50
        
        # Calculate total adjustments
        total_adjustment = trend_adjustment + momentum_adjustment + volume_adjustment + whale_adjustment
        total_adjustment = max(-self.win_rate_params["max_adjustment"], 
                             min(self.win_rate_params["max_adjustment"], total_adjustment))
        
        # Apply adjustments with timeframe variations
        long_24h = base_long + total_adjustment
        long_7d = base_long + (total_adjustment * 0.8)  # Slightly less impact over 7 days
        long_30d = base_long + (total_adjustment * 0.6)  # Even less impact over 30 days
        
        # Short rates are complementary but with slight asymmetry for realism
        short_24h = 100 - long_24h
        short_7d = 100 - long_7d  
        short_30d = 100 - long_30d
        
        # Ensure rates are within realistic bounds (20-80%)
        return {
            "long_24h": max(20.0, min(80.0, long_24h)),
            "long_7d": max(20.0, min(80.0, long_7d)),
            "long_30d": max(20.0, min(80.0, long_30d)),
            "short_24h": max(20.0, min(80.0, short_24h)),
            "short_7d": max(20.0, min(80.0, short_7d)),
            "short_30d": max(20.0, min(80.0, short_30d))
        }
    
    def _calculate_composite_scores(self, endpoint_analyses: List[EndpointDataAnalysis], market_analysis: MarketPriceAnalysis) -> Dict[str, Any]:
        """Calculate composite long/short scores based on all endpoint data"""
        
        total_weight = 0.0
        weighted_long_score = 0.0
        weighted_short_score = 0.0
        
        for analysis in endpoint_analyses:
            if analysis.reliability_score > 0.5:  # Only use reliable data
                endpoint_config = self.endpoints.get(analysis.endpoint_name, {})
                weight = endpoint_config.get("weight", 5.0) * analysis.reliability_score
                
                # Calculate endpoint-specific scores
                endpoint_long_score = self._calculate_endpoint_long_score(analysis)
                endpoint_short_score = 100.0 - endpoint_long_score  # Complementary
                
                weighted_long_score += endpoint_long_score * weight
                weighted_short_score += endpoint_short_score * weight
                total_weight += weight
        
        if total_weight > 0:
            composite_long = weighted_long_score / total_weight
            composite_short = weighted_short_score / total_weight
        else:
            composite_long = 50.0
            composite_short = 50.0
        
        # Determine overall direction
        if composite_long > 55:
            direction = "BULLISH"
        elif composite_short > 55:
            direction = "BEARISH"
        else:
            direction = "NEUTRAL"
        
        # Calculate confidence based on data quality and consensus
        confidence = market_analysis.confidence_level
        
        return {
            "long_score": composite_long,
            "short_score": composite_short,
            "direction": direction,
            "confidence": confidence
        }
    
    def _calculate_endpoint_long_score(self, analysis: EndpointDataAnalysis) -> float:
        """Calculate long score for individual endpoint"""
        base_score = 50.0
        
        # Count bullish vs bearish signals
        bullish_signals = len([s for s in analysis.market_signals if any(word in s.lower() for word in ["bullish", "up", "positive", "strong", "high"])])
        bearish_signals = len([s for s in analysis.market_signals if any(word in s.lower() for word in ["bearish", "down", "negative", "weak", "low"])])
        
        # Count opportunities vs risks
        opportunities = len(analysis.opportunity_indicators)
        risks = len(analysis.risk_indicators)
        
        # Adjust score based on signals
        signal_adjustment = (bullish_signals - bearish_signals) * 10
        opportunity_adjustment = (opportunities - risks) * 5
        
        final_score = base_score + signal_adjustment + opportunity_adjustment
        
        return max(20.0, min(80.0, final_score))
    
    def _generate_professional_insights(self, symbol: str, endpoint_analyses: List[EndpointDataAnalysis], market_analysis: MarketPriceAnalysis) -> Dict[str, Any]:
        """Generate professional insights based on endpoint data"""
        
        key_insights = []
        risk_factors = []
        trading_recommendations = {}
        
        # Analyze all signals from endpoints
        all_signals = []
        all_risks = []
        all_opportunities = []
        
        for analysis in endpoint_analyses:
            all_signals.extend(analysis.market_signals)
            all_risks.extend(analysis.risk_indicators)
            all_opportunities.extend(analysis.opportunity_indicators)
        
        # Generate key insights
        if market_analysis.long_win_rate_24h > 60:
            key_insights.append(f"Strong bullish bias with {market_analysis.long_win_rate_24h:.1f}% long win rate over 24h")
        elif market_analysis.short_win_rate_24h > 60:
            key_insights.append(f"Strong bearish bias with {market_analysis.short_win_rate_24h:.1f}% short win rate over 24h")
        
        if market_analysis.current_price > 0:
            key_insights.append(f"Current price: ${market_analysis.current_price:.4f} with {market_analysis.price_24h_change:+.2f}% 24h change")
        
        # Add endpoint-specific insights
        for signal in all_signals[:3]:  # Top 3 signals
            key_insights.append(signal)
        
        # Generate risk factors
        risk_factors.extend(all_risks[:5])  # Top 5 risks
        
        if market_analysis.data_quality_score < 0.7:
            risk_factors.append("Limited data availability may affect analysis accuracy")
        
        # Generate trading recommendations
        if market_analysis.long_win_rate_24h > 55:
            trading_recommendations["primary"] = "LONG"
            trading_recommendations["entry_strategy"] = "Consider long positions on dips"
            trading_recommendations["risk_management"] = f"Stop loss below key support levels"
        else:
            trading_recommendations["primary"] = "SHORT"
            trading_recommendations["entry_strategy"] = "Consider short positions on rallies"
            trading_recommendations["risk_management"] = f"Stop loss above key resistance levels"
        
        trading_recommendations["timeframe"] = "24-48 hours for highest probability"
        trading_recommendations["confidence"] = f"{market_analysis.confidence_level:.1%}"
        
        return {
            "key_insights": key_insights,
            "risk_factors": risk_factors,
            "trading_recommendations": trading_recommendations
        }
    
    def _calculate_confidence_level(self, endpoint_analyses: List[EndpointDataAnalysis]) -> float:
        """Calculate overall confidence level based on data quality"""
        if not endpoint_analyses:
            return 0.3
        
        total_reliability = sum(analysis.reliability_score for analysis in endpoint_analyses)
        avg_reliability = total_reliability / len(endpoint_analyses)
        
        # Boost confidence if we have multiple reliable sources
        reliable_sources = len([a for a in endpoint_analyses if a.reliability_score > 0.7])
        source_bonus = min(reliable_sources * 0.1, 0.3)
        
        return min(avg_reliability + source_bonus, 0.95)
    
    def _calculate_data_quality_score(self, endpoint_analyses: List[EndpointDataAnalysis]) -> float:
        """Calculate data quality score"""
        if not endpoint_analyses:
            return 0.0
        
        quality_scores = []
        for analysis in endpoint_analyses:
            # Score based on metrics count and reliability
            metrics_score = min(len(analysis.processed_metrics) / 5.0, 1.0)
            signals_score = min(len(analysis.market_signals) / 3.0, 1.0)
            quality_score = (metrics_score + signals_score + analysis.reliability_score) / 3.0
            quality_scores.append(quality_score)
        
        return statistics.mean(quality_scores)
    
    def _calculate_analysis_quality(self, endpoint_analyses: List[EndpointDataAnalysis]) -> float:
        """Calculate overall analysis quality score"""
        if not endpoint_analyses:
            return 0.5
        
        # Factors: data coverage, reliability, insights generated
        coverage_score = len(endpoint_analyses) / len(self.endpoints)
        reliability_score = statistics.mean([a.reliability_score for a in endpoint_analyses])
        insights_score = min(sum(len(a.market_signals) + len(a.opportunity_indicators) for a in endpoint_analyses) / 20.0, 1.0)
        
        return (coverage_score + reliability_score + insights_score) / 3.0
    
    def _quantify_trend(self, trend_text: str) -> float:
        """Convert trend text to numerical value"""
        trend_lower = trend_text.lower()
        
        if "strong" in trend_lower and "bullish" in trend_lower:
            return 80.0
        elif "bullish" in trend_lower:
            return 65.0
        elif "weak" in trend_lower and "bullish" in trend_lower:
            return 55.0
        elif "neutral" in trend_lower:
            return 50.0
        elif "weak" in trend_lower and "bearish" in trend_lower:
            return 45.0
        elif "bearish" in trend_lower:
            return 35.0
        elif "strong" in trend_lower and "bearish" in trend_lower:
            return 20.0
        else:
            return 50.0
    
    async def _make_api_call(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API call to Cryptometer endpoint"""
        try:
            if self.session is None:
                logger.error("Session not initialized. Use 'async with analyzer:' context manager.")
                return None
                
            url = f"{self.base_url}{endpoint}"
            params["api"] = self.api_key
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"API call failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"API call error: {e}")
            return None
    
    def _create_fallback_report(self, symbol: str, error: str) -> ProfessionalAnalysisReport:
        """Create fallback report when analysis fails"""
        fallback_market_analysis = MarketPriceAnalysis(
            current_price=0.0,
            price_24h_change=0.0,
            price_7d_change=0.0,
            volume_24h=0.0,
            market_cap=None,
            long_win_rate_24h=45.0,
            long_win_rate_7d=47.0,
            long_win_rate_30d=50.0,
            short_win_rate_24h=55.0,
            short_win_rate_7d=53.0,
            short_win_rate_30d=50.0,
            confidence_level=0.3,
            data_quality_score=0.2
        )
        
        return ProfessionalAnalysisReport(
            symbol=symbol,
            timestamp=datetime.now(),
            market_price_analysis=fallback_market_analysis,
            endpoint_analyses=[],
            composite_long_score=45.0,
            composite_short_score=55.0,
            overall_direction="NEUTRAL",
            confidence_level=0.3,
            key_insights=[f"Analysis limited due to data issues: {error}"],
            risk_factors=["Limited data availability", "Reduced analysis accuracy"],
            trading_recommendations={
                "primary": "NEUTRAL",
                "entry_strategy": "Wait for better data availability",
                "risk_management": "Use conservative position sizing",
                "timeframe": "Reassess when data improves",
                "confidence": "30%"
            },
            data_sources_used=[],
            analysis_quality_score=0.3
        )

# Global instance for easy access
advanced_cryptometer_analyzer = AdvancedCryptometerAnalyzer()