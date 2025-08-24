#!/usr/bin/env python3
"""
Master Agent for KingFisher Analysis
Collects data from all 5 specialized agents and creates comprehensive final reports
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AgentAnalysis:
    """Data structure for agent analysis results"""
    agent_type: str
    confidence: float
    analysis_data: Dict[str, Any]
    timestamp: datetime

@dataclass
class MasterReport:
    """Comprehensive final report from Master Agent"""
    symbol: str
    current_price: float
    overall_sentiment: str
    risk_level: str
    confidence_score: float
    timeframe_scores: Dict[str, int]  # 24h, 48h, 7d, 1M scores
    liquidation_clusters: Dict[str, Any]
    professional_summary: str
    detailed_analysis: str
    recommendations: str
    timestamp: datetime

class MasterAgent:
    """Master Agent that orchestrates all analysis and creates final reports"""
    
    def __init__(self):
        self.agents = {
            "image_classification": None,
            "market_data": None,
            "liquidation_analysis": None,
            "technical_analysis": None,
            "risk_assessment": None
        }
        self.analysis_history = []
    
    async def collect_agent_data(self, symbol: str, image_data: bytes, 
                                image_type: str, market_data: Dict[str, Any]) -> Dict[str, AgentAnalysis]:
        """Collect analysis from all 5 specialized agents"""
        
        logger.info(f"🔍 Master Agent: Collecting data from all agents for {symbol}")
        
        agent_results = {}
        
        # 1. Image Classification Agent
        classification_analysis = await self._run_image_classification_agent(image_data, image_type)
        agent_results["image_classification"] = classification_analysis
        
        # 2. Market Data Agent
        market_analysis = await self._run_market_data_agent(symbol, market_data)
        agent_results["market_data"] = market_analysis
        
        # 3. Liquidation Analysis Agent
        liquidation_analysis = await self._run_liquidation_analysis_agent(image_data, image_type, market_data)
        agent_results["liquidation_analysis"] = liquidation_analysis
        
        # 4. Technical Analysis Agent
        technical_analysis = await self._run_technical_analysis_agent(symbol, market_data, liquidation_analysis)
        agent_results["technical_analysis"] = technical_analysis
        
        # 5. Risk Assessment Agent
        risk_analysis = await self._run_risk_assessment_agent(symbol, market_data, liquidation_analysis, technical_analysis)
        agent_results["risk_assessment"] = risk_analysis
        
        return agent_results
    
    async def create_master_report(self, symbol: str, agent_results: Dict[str, AgentAnalysis]) -> MasterReport:
        """Create comprehensive final report from all agent data"""
        
        logger.info(f"📊 Master Agent: Creating comprehensive report for {symbol}")
        
        # Extract key data from all agents
        market_data = agent_results["market_data"].analysis_data
        liquidation_data = agent_results["liquidation_analysis"].analysis_data
        technical_data = agent_results["technical_analysis"].analysis_data
        risk_data = agent_results["risk_assessment"].analysis_data
        
        # Calculate overall sentiment
        overall_sentiment = self._calculate_overall_sentiment(agent_results)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(agent_results)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(agent_results)
        
        # Calculate timeframe scores (max of Long/Short for each timeframe)
        timeframe_scores = self._calculate_timeframe_scores(agent_results)
        
        # Extract liquidation clusters with proper field mapping
        liquidation_clusters = self._extract_liquidation_clusters(liquidation_data, market_data)
        
        # Generate professional summary
        professional_summary = self._generate_professional_summary(symbol, agent_results)
        
        # Generate detailed analysis
        detailed_analysis = self._generate_detailed_analysis(agent_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(agent_results)
        
        return MasterReport(
            symbol=symbol,
            current_price=market_data.get("current_price", 0.0),
            overall_sentiment=overall_sentiment,
            risk_level=risk_level,
            confidence_score=confidence_score,
            timeframe_scores=timeframe_scores,
            liquidation_clusters=liquidation_clusters,
            professional_summary=professional_summary,
            detailed_analysis=detailed_analysis,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def _run_image_classification_agent(self, image_data: bytes, image_type: str) -> AgentAnalysis:
        """Run Image Classification Agent"""
        try:
            # Analyze image characteristics
            analysis_data = {
                "image_type": image_type,
                "image_quality": "high",
                "detected_features": ["liquidation_zones", "price_levels", "volume_data"],
                "classification_confidence": 0.95
            }
            
            return AgentAnalysis(
                agent_type="image_classification",
                confidence=0.95,
                analysis_data=analysis_data,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in image classification agent: {e}")
            return self._get_default_agent_analysis("image_classification")
    
    async def _run_market_data_agent(self, symbol: str, market_data: Dict[str, Any]) -> AgentAnalysis:
        """Run Market Data Agent"""
        try:
            current_price = market_data.get("price", 0.0)
            
            analysis_data = {
                "current_price": current_price,
                "price_change_24h": market_data.get("change_24h", 0.0),
                "volume_24h": market_data.get("volume", 0.0),
                "market_cap": market_data.get("market_cap", 0.0),
                "volatility": market_data.get("volatility", 0.0),
                "market_sentiment": self._analyze_market_sentiment(market_data)
            }
            
            return AgentAnalysis(
                agent_type="market_data",
                confidence=0.90,
                analysis_data=analysis_data,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in market data agent: {e}")
            return self._get_default_agent_analysis("market_data")
    
    async def _run_liquidation_analysis_agent(self, image_data: bytes, image_type: str, 
                                            market_data: Dict[str, Any]) -> AgentAnalysis:
        """Run Liquidation Analysis Agent"""
        try:
            current_price = market_data.get("price", 0.0)
            
            # Analyze liquidation clusters based on image type
            if image_type == "liquidation_heatmap":
                clusters = self._analyze_heatmap_clusters(image_data, current_price)
            elif image_type == "liquidation_map":
                clusters = self._analyze_map_clusters(image_data, current_price)
            else:
                clusters = self._analyze_general_clusters(image_data, current_price)
            
            analysis_data = {
                "liquidation_clusters": clusters,
                "total_liquidation_volume": sum(cluster.get("size", 0) for cluster in clusters),
                "cluster_count": len(clusters),
                "liquidation_pressure": self._calculate_liquidation_pressure(clusters),
                "support_resistance_levels": self._extract_support_resistance(clusters, current_price)
            }
            
            return AgentAnalysis(
                agent_type="liquidation_analysis",
                confidence=0.88,
                analysis_data=analysis_data,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in liquidation analysis agent: {e}")
            return self._get_default_agent_analysis("liquidation_analysis")
    
    async def _run_technical_analysis_agent(self, symbol: str, market_data: Dict[str, Any], 
                                          liquidation_analysis: AgentAnalysis) -> AgentAnalysis:
        """Run Technical Analysis Agent"""
        try:
            current_price = market_data.get("price", 0.0)
            liquidation_data = liquidation_analysis.analysis_data
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(market_data)
            macd = self._calculate_macd(market_data)
            bollinger_bands = self._calculate_bollinger_bands(market_data)
            
            # Analyze price action
            price_action = self._analyze_price_action(market_data, liquidation_data)
            
            analysis_data = {
                "rsi": rsi,
                "macd": macd,
                "bollinger_bands": bollinger_bands,
                "price_action": price_action,
                "trend_direction": self._determine_trend_direction(market_data),
                "support_levels": liquidation_data.get("support_resistance_levels", {}).get("support", []),
                "resistance_levels": liquidation_data.get("support_resistance_levels", {}).get("resistance", [])
            }
            
            return AgentAnalysis(
                agent_type="technical_analysis",
                confidence=0.92,
                analysis_data=analysis_data,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in technical analysis agent: {e}")
            return self._get_default_agent_analysis("technical_analysis")
    
    async def _run_risk_assessment_agent(self, symbol: str, market_data: Dict[str, Any],
                                       liquidation_analysis: AgentAnalysis, 
                                       technical_analysis: AgentAnalysis) -> AgentAnalysis:
        """Run Risk Assessment Agent"""
        try:
            # Calculate risk metrics
            volatility_risk = self._calculate_volatility_risk(market_data)
            liquidity_risk = self._calculate_liquidity_risk(liquidation_analysis.analysis_data)
            technical_risk = self._calculate_technical_risk(technical_analysis.analysis_data)
            
            # Calculate timeframe win rates
            timeframe_analysis = self._calculate_timeframe_analysis(market_data, liquidation_analysis.analysis_data)
            
            analysis_data = {
                "volatility_risk": volatility_risk,
                "liquidity_risk": liquidity_risk,
                "technical_risk": technical_risk,
                "overall_risk_score": (volatility_risk + liquidity_risk + technical_risk) / 3,
                "timeframe_analysis": timeframe_analysis,
                "risk_factors": self._identify_risk_factors(market_data, liquidation_analysis.analysis_data)
            }
            
            return AgentAnalysis(
                agent_type="risk_assessment",
                confidence=0.89,
                analysis_data=analysis_data,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in risk assessment agent: {e}")
            return self._get_default_agent_analysis("risk_assessment")
    
    def _calculate_overall_sentiment(self, agent_results: Dict[str, AgentAnalysis]) -> str:
        """Calculate overall sentiment from all agents"""
        sentiments = []
        
        # Market data sentiment
        market_sentiment = agent_results["market_data"].analysis_data.get("market_sentiment", "neutral")
        sentiments.append(market_sentiment)
        
        # Technical sentiment
        technical_data = agent_results["technical_analysis"].analysis_data
        trend_direction = technical_data.get("trend_direction", "neutral")
        sentiments.append(trend_direction)
        
        # Risk sentiment
        risk_data = agent_results["risk_assessment"].analysis_data
        risk_score = risk_data.get("overall_risk_score", 0.5)
        if risk_score < 0.3:
            sentiments.append("bullish")
        elif risk_score > 0.7:
            sentiments.append("bearish")
        else:
            sentiments.append("neutral")
        
        # Determine majority sentiment
        bullish_count = sentiments.count("bullish")
        bearish_count = sentiments.count("bearish")
        
        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_risk_level(self, agent_results: Dict[str, AgentAnalysis]) -> str:
        """Calculate overall risk level"""
        risk_data = agent_results["risk_assessment"].analysis_data
        overall_risk = risk_data.get("overall_risk_score", 0.5)
        
        if overall_risk < 0.3:
            return "low"
        elif overall_risk < 0.7:
            return "medium"
        else:
            return "high"
    
    def _calculate_confidence_score(self, agent_results: Dict[str, AgentAnalysis]) -> float:
        """Calculate overall confidence score"""
        confidences = [agent.confidence for agent in agent_results.values()]
        return sum(confidences) / len(confidences)
    
    def _calculate_timeframe_scores(self, agent_results: Dict[str, AgentAnalysis]) -> Dict[str, int]:
        """Calculate timeframe scores (max of Long/Short for each timeframe)"""
        risk_data = agent_results["risk_assessment"].analysis_data
        timeframe_analysis = risk_data.get("timeframe_analysis", {})
        
        scores = {}
        for timeframe in ["24h", "48h", "7d", "1M"]:
            if timeframe in timeframe_analysis:
                long_rate = timeframe_analysis[timeframe].get("long_win_rate", 0)
                short_rate = timeframe_analysis[timeframe].get("short_win_rate", 0)
                scores[timeframe] = max(long_rate, short_rate)
            else:
                scores[timeframe] = 50  # Default score
        
        return scores
    
    def _extract_liquidation_clusters(self, liquidation_data: Dict[str, Any], 
                                    market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract liquidation clusters with proper field mapping"""
        current_price = market_data.get("current_price", 0.0)
        clusters = liquidation_data.get("liquidation_clusters", [])
        
        # Separate clusters by position relative to current price
        left_clusters = []  # Below current price (support)
        right_clusters = []  # Above current price (resistance)
        
        for cluster in clusters:
            cluster_price = cluster.get("price", 0.0)
            if cluster_price < current_price:
                left_clusters.append(cluster)
            else:
                right_clusters.append(cluster)
        
        # Sort by size (largest first) and take top 2 from each side
        left_clusters.sort(key=lambda x: x.get("size", 0), reverse=True)
        right_clusters.sort(key=lambda x: x.get("size", 0), reverse=True)
        
        return {
            "Liqcluster-1": left_clusters[0].get("price", 0.0) if len(left_clusters) > 0 else 0.0,
            "Liqcluster-2": left_clusters[1].get("price", 0.0) if len(left_clusters) > 1 else 0.0,
            "Liqcluster1": right_clusters[0].get("price", 0.0) if len(right_clusters) > 0 else 0.0,
            "Liqcluster2": right_clusters[1].get("price", 0.0) if len(right_clusters) > 1 else 0.0,
            "left_cluster_sizes": [c.get("size", 0) for c in left_clusters[:2]],
            "right_cluster_sizes": [c.get("size", 0) for c in right_clusters[:2]]
        }
    
    def _generate_professional_summary(self, symbol: str, agent_results: Dict[str, AgentAnalysis]) -> str:
        """Generate professional summary from all agent data"""
        market_data = agent_results["market_data"].analysis_data
        technical_data = agent_results["technical_analysis"].analysis_data
        risk_data = agent_results["risk_assessment"].analysis_data
        
        current_price = market_data.get("current_price", 0.0)
        sentiment = self._calculate_overall_sentiment(agent_results)
        risk_level = self._calculate_risk_level(agent_results)
        
        summary = f"""
# {symbol}/USDT Professional Trading Analysis & Win Rate Assessment

## Executive Summary

{symbol} is currently trading at ${current_price:,.2f} with a {sentiment} market sentiment and {risk_level} risk level. 
The technical analysis indicates {technical_data.get('trend_direction', 'neutral')} momentum with 
RSI at {technical_data.get('rsi', 50):.1f} and overall risk score of {risk_data.get('overall_risk_score', 0.5):.2f}.

## Key Findings

- **Market Sentiment**: {sentiment.upper()}
- **Risk Level**: {risk_level.upper()}
- **Current Price**: ${current_price:,.2f}
- **24h Change**: {market_data.get('price_change_24h', 0.0):+.2f}%
- **Volume**: ${market_data.get('volume_24h', 0):,.0f}

## Timeframe Analysis

"""
        
        # Add timeframe analysis
        timeframe_analysis = risk_data.get("timeframe_analysis", {})
        for timeframe in ["24h", "48h", "7d", "1M"]:
            if timeframe in timeframe_analysis:
                data = timeframe_analysis[timeframe]
                long_rate = data.get("long_win_rate", 0)
                short_rate = data.get("short_win_rate", 0)
                summary += f"- **{timeframe}**: Long {long_rate}%, Short {short_rate}%\n"
        
        return summary
    
    def _generate_detailed_analysis(self, agent_results: Dict[str, AgentAnalysis]) -> str:
        """Generate detailed analysis from all agent data"""
        technical_data = agent_results["technical_analysis"].analysis_data
        liquidation_data = agent_results["liquidation_analysis"].analysis_data
        risk_data = agent_results["risk_assessment"].analysis_data
        
        analysis = f"""
## Detailed Market Structure Analysis

### Technical Indicators
- **RSI**: {technical_data.get('rsi', 50):.1f} ({self._get_rsi_interpretation(technical_data.get('rsi', 50))})
- **MACD**: {technical_data.get('macd', {}).get('signal', 'neutral')}
- **Bollinger Bands**: {technical_data.get('bollinger_bands', {}).get('position', 'neutral')}

### Liquidation Analysis
- **Total Liquidation Volume**: ${liquidation_data.get('total_liquidation_volume', 0):,.0f}
- **Cluster Count**: {liquidation_data.get('cluster_count', 0)}
- **Liquidation Pressure**: {liquidation_data.get('liquidation_pressure', 0):.2f}

### Risk Assessment
- **Volatility Risk**: {risk_data.get('volatility_risk', 0):.2f}
- **Liquidity Risk**: {risk_data.get('liquidity_risk', 0):.2f}
- **Technical Risk**: {risk_data.get('technical_risk', 0):.2f}
- **Overall Risk Score**: {risk_data.get('overall_risk_score', 0):.2f}
"""
        
        return analysis
    
    def _generate_recommendations(self, agent_results: Dict[str, AgentAnalysis]) -> str:
        """Generate trading recommendations"""
        sentiment = self._calculate_overall_sentiment(agent_results)
        risk_level = self._calculate_risk_level(agent_results)
        technical_data = agent_results["technical_analysis"].analysis_data
        
        recommendations = f"""
## Trading Recommendations

### Position Sizing
Based on {risk_level} risk level and {sentiment} sentiment:
- **Conservative**: 1-2% of portfolio
- **Moderate**: 3-5% of portfolio  
- **Aggressive**: 5-10% of portfolio

### Entry/Exit Strategy
- **Entry**: {self._get_entry_strategy(sentiment, technical_data)}
- **Stop Loss**: {self._get_stop_loss_strategy(risk_level)}
- **Take Profit**: {self._get_take_profit_strategy(sentiment)}

### Key Risk Factors
{self._get_risk_factors_summary(agent_results)}
"""
        
        return recommendations
    
    # Helper methods for analysis
    def _analyze_market_sentiment(self, market_data: Dict[str, Any]) -> str:
        """Analyze market sentiment from data"""
        change_24h = market_data.get("change_24h", 0.0)
        volatility = market_data.get("volatility", 0.0)
        
        if change_24h > 5 and volatility < 0.1:
            return "bullish"
        elif change_24h < -5 and volatility > 0.2:
            return "bearish"
        else:
            return "neutral"
    
    def _analyze_heatmap_clusters(self, image_data: bytes, current_price: float) -> List[Dict[str, Any]]:
        """Analyze liquidation clusters from heatmap"""
        # Mock analysis - in real implementation, this would use computer vision
        return [
            {"price": current_price * 0.95, "size": 1000000, "intensity": "high"},
            {"price": current_price * 0.90, "size": 2000000, "intensity": "very_high"},
            {"price": current_price * 1.05, "size": 800000, "intensity": "medium"},
            {"price": current_price * 1.10, "size": 1200000, "intensity": "high"}
        ]
    
    def _analyze_map_clusters(self, image_data: bytes, current_price: float) -> List[Dict[str, Any]]:
        """Analyze liquidation clusters from map"""
        # Mock analysis - in real implementation, this would use computer vision
        return [
            {"price": current_price * 0.97, "size": 1500000, "intensity": "high"},
            {"price": current_price * 0.92, "size": 2500000, "intensity": "very_high"},
            {"price": current_price * 1.03, "size": 900000, "intensity": "medium"},
            {"price": current_price * 1.08, "size": 1100000, "intensity": "high"}
        ]
    
    def _analyze_general_clusters(self, image_data: bytes, current_price: float) -> List[Dict[str, Any]]:
        """Analyze liquidation clusters from general image"""
        return [
            {"price": current_price * 0.98, "size": 1200000, "intensity": "medium"},
            {"price": current_price * 1.02, "size": 1000000, "intensity": "medium"}
        ]
    
    def _calculate_liquidation_pressure(self, clusters: List[Dict[str, Any]]) -> float:
        """Calculate liquidation pressure from clusters"""
        if not clusters:
            return 0.0
        
        total_size = sum(cluster.get("size", 0) for cluster in clusters)
        high_intensity = sum(1 for cluster in clusters if cluster.get("intensity") in ["high", "very_high"])
        
        return min((total_size / 10000000) * (high_intensity / len(clusters)), 1.0)
    
    def _extract_support_resistance(self, clusters: List[Dict[str, Any]], current_price: float) -> Dict[str, List]:
        """Extract support and resistance levels"""
        support = [c["price"] for c in clusters if c["price"] < current_price]
        resistance = [c["price"] for c in clusters if c["price"] > current_price]
        
        return {
            "support": sorted(support, reverse=True),
            "resistance": sorted(resistance)
        }
    
    def _calculate_rsi(self, market_data: Dict[str, Any]) -> float:
        """Calculate RSI (mock implementation)"""
        return 52.5  # Mock value
    
    def _calculate_macd(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate MACD (mock implementation)"""
        return {"signal": "bullish", "value": 0.15}
    
    def _calculate_bollinger_bands(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Bollinger Bands (mock implementation)"""
        return {"position": "middle", "width": "normal"}
    
    def _analyze_price_action(self, market_data: Dict[str, Any], liquidation_data: Dict[str, Any]) -> str:
        """Analyze price action"""
        change_24h = market_data.get("change_24h", 0.0)
        if change_24h > 3:
            return "bullish_momentum"
        elif change_24h < -3:
            return "bearish_momentum"
        else:
            return "sideways"
    
    def _determine_trend_direction(self, market_data: Dict[str, Any]) -> str:
        """Determine trend direction"""
        change_24h = market_data.get("change_24h", 0.0)
        if change_24h > 2:
            return "uptrend"
        elif change_24h < -2:
            return "downtrend"
        else:
            return "sideways"
    
    def _calculate_volatility_risk(self, market_data: Dict[str, Any]) -> float:
        """Calculate volatility risk"""
        volatility = market_data.get("volatility", 0.0)
        return min(volatility * 2, 1.0)
    
    def _calculate_liquidity_risk(self, liquidation_data: Dict[str, Any]) -> float:
        """Calculate liquidity risk"""
        pressure = liquidation_data.get("liquidation_pressure", 0.0)
        return min(pressure * 1.5, 1.0)
    
    def _calculate_technical_risk(self, technical_data: Dict[str, Any]) -> float:
        """Calculate technical risk"""
        rsi = technical_data.get("rsi", 50)
        if rsi > 70 or rsi < 30:
            return 0.8
        elif rsi > 60 or rsi < 40:
            return 0.5
        else:
            return 0.2
    
    def _calculate_timeframe_analysis(self, market_data: Dict[str, Any], 
                                    liquidation_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Calculate timeframe analysis with win rates"""
        pressure = liquidation_data.get("liquidation_pressure", 0.5)
        change_24h = market_data.get("change_24h", 0.0)
        
        # Calculate win rates based on sentiment and pressure
        if change_24h > 0:
            long_base = 60
            short_base = 40
        else:
            long_base = 40
            short_base = 60
        
        # Adjust based on liquidation pressure
        pressure_adjustment = (pressure - 0.5) * 20
        
        return {
            "24h": {
                "long_win_rate": max(0, min(100, long_base + pressure_adjustment)),
                "short_win_rate": max(0, min(100, short_base - pressure_adjustment))
            },
            "48h": {
                "long_win_rate": max(0, min(100, long_base + pressure_adjustment * 0.8)),
                "short_win_rate": max(0, min(100, short_base - pressure_adjustment * 0.8))
            },
            "7d": {
                "long_win_rate": max(0, min(100, long_base + pressure_adjustment * 0.6)),
                "short_win_rate": max(0, min(100, short_base - pressure_adjustment * 0.6))
            },
            "1M": {
                "long_win_rate": max(0, min(100, long_base + pressure_adjustment * 0.4)),
                "short_win_rate": max(0, min(100, short_base - pressure_adjustment * 0.4))
            }
        }
    
    def _identify_risk_factors(self, market_data: Dict[str, Any], 
                              liquidation_data: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        risk_factors = []
        
        if market_data.get("volatility", 0) > 0.15:
            risk_factors.append("High volatility")
        
        if liquidation_data.get("liquidation_pressure", 0) > 0.7:
            risk_factors.append("High liquidation pressure")
        
        if market_data.get("change_24h", 0) > 10:
            risk_factors.append("Extreme price movement")
        
        return risk_factors
    
    def _get_rsi_interpretation(self, rsi: float) -> str:
        """Get RSI interpretation"""
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    def _get_entry_strategy(self, sentiment: str, technical_data: Dict[str, Any]) -> str:
        """Get entry strategy"""
        if sentiment == "bullish":
            return "Buy on dips near support levels"
        elif sentiment == "bearish":
            return "Sell on rallies near resistance levels"
        else:
            return "Wait for clear breakout/breakdown"
    
    def _get_stop_loss_strategy(self, risk_level: str) -> str:
        """Get stop loss strategy"""
        if risk_level == "high":
            return "Tight stops (2-3%)"
        elif risk_level == "medium":
            return "Moderate stops (3-5%)"
        else:
            return "Wide stops (5-8%)"
    
    def _get_take_profit_strategy(self, sentiment: str) -> str:
        """Get take profit strategy"""
        if sentiment == "bullish":
            return "Target resistance levels"
        elif sentiment == "bearish":
            return "Target support levels"
        else:
            return "Use risk-reward ratio of 1:2"
    
    def _get_risk_factors_summary(self, agent_results: Dict[str, AgentAnalysis]) -> str:
        """Get risk factors summary"""
        risk_data = agent_results["risk_assessment"].analysis_data
        risk_factors = risk_data.get("risk_factors", [])
        
        if not risk_factors:
            return "No significant risk factors identified"
        
        return "\n".join([f"- {factor}" for factor in risk_factors])
    
    def _get_default_agent_analysis(self, agent_type: str) -> AgentAnalysis:
        """Get default agent analysis for error cases"""
        return AgentAnalysis(
            agent_type=agent_type,
            confidence=0.3,
            analysis_data={},
            timestamp=datetime.now()
        ) 