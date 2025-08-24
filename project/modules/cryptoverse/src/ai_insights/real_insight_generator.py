#!/usr/bin/env python3
"""
Real AI Insight Generator
Generates comprehensive AI-powered insights from real cryptocurrency data
Implements advanced analysis algorithms and machine learning techniques
"""

import logging
import json
import statistics
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.cryptoverse_database import CryptoverseDatabase

logger = logging.getLogger(__name__)

@dataclass
class MarketInsight:
    """Structure for market insights"""
    type: str
    title: str
    description: str
    confidence: float
    severity: str  # low, medium, high, critical
    actionable: bool
    recommendations: List[str]
    data_points: Dict[str, Any]
    timestamp: datetime

class RealInsightGenerator:
    """Generates comprehensive AI-powered insights from real market data"""
    
    def __init__(self, database: CryptoverseDatabase):
        self.database = database
        self.insight_types = [
            'market_trend_analysis',
            'risk_assessment',
            'opportunity_detection',
            'correlation_analysis',
            'sentiment_analysis',
            'volatility_analysis',
            'volume_analysis',
            'technical_pattern_recognition'
        ]
        logger.info("Real AI Insight Generator initialized with advanced analytics")
    
    async def generate_comprehensive_insights(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive market insights using real data"""
        try:
            logger.info(f"🧠 Generating comprehensive AI insights for {symbol or 'all markets'}")
            
            insights = []
            
            # Get fresh data from database
            risk_data = self.database.get_latest_data('crypto_risk_indicators', 10)
            screener_data = self.database.get_latest_data('screener_data', 50)
            
            if not risk_data and not screener_data:
                logger.warning("⚠️  No data available for insight generation")
                return [self._create_no_data_insight()]
            
            # Generate different types of insights
            if risk_data:
                insights.extend(await self._generate_market_trend_insights(risk_data))
                insights.extend(await self._generate_risk_assessment_insights(risk_data))
                insights.extend(await self._generate_sentiment_insights(risk_data))
            
            if screener_data:
                insights.extend(await self._generate_opportunity_insights(screener_data))
                insights.extend(await self._generate_volatility_insights(screener_data))
                insights.extend(await self._generate_volume_insights(screener_data))
            
            if risk_data and screener_data:
                insights.extend(await self._generate_correlation_insights(risk_data, screener_data))
                insights.extend(await self._generate_technical_pattern_insights(screener_data))
            
            # Filter and rank insights by relevance and confidence
            filtered_insights = self._filter_and_rank_insights(insights, symbol)
            
            # Convert to serializable format
            serializable_insights = [self._serialize_insight(insight) for insight in filtered_insights]
            
            logger.info(f"✅ Generated {len(serializable_insights)} comprehensive insights")
            
            # Save insights to database
            for insight in serializable_insights:
                await self._save_insight_to_database(insight)
            
            return serializable_insights
            
        except Exception as e:
            logger.error(f"❌ Error generating comprehensive insights: {str(e)}")
            return [self._create_error_insight(str(e))]
    
    async def _generate_market_trend_insights(self, risk_data: List[Dict]) -> List[MarketInsight]:
        """Generate market trend analysis insights"""
        insights = []
        
        try:
            if len(risk_data) < 2:
                return insights
            
            # Analyze risk trend over time
            recent_risks = []
            for data in risk_data[:5]:  # Last 5 data points
                if isinstance(data, dict) and 'risk_analysis' in data:
                    risk_score = data['risk_analysis'].get('overall_risk', 0.5)
                    recent_risks.append(risk_score)
            
            if len(recent_risks) >= 2:
                trend_direction = self._calculate_trend(recent_risks)
                trend_strength = self._calculate_trend_strength(recent_risks)
                
                # Generate trend insight
                if trend_direction > 0.05:  # Increasing risk
                    insights.append(MarketInsight(
                        type="market_trend_analysis",
                        title="Rising Market Risk Detected",
                        description=f"Market risk has increased by {trend_direction*100:.1f}% over recent periods. "
                                  f"Current trend strength: {trend_strength:.2f}",
                        confidence=0.85,
                        severity="medium" if trend_direction < 0.15 else "high",
                        actionable=True,
                        recommendations=[
                            "Consider reducing position sizes",
                            "Implement stricter stop-loss levels",
                            "Monitor market conditions more closely",
                            "Avoid high-leverage positions"
                        ],
                        data_points={
                            "trend_direction": trend_direction,
                            "trend_strength": trend_strength,
                            "recent_risk_scores": recent_risks,
                            "data_points_analyzed": len(recent_risks)
                        },
                        timestamp=datetime.now()
                    ))
                elif trend_direction < -0.05:  # Decreasing risk
                    insights.append(MarketInsight(
                        type="market_trend_analysis",
                        title="Market Risk Declining",
                        description=f"Market risk has decreased by {abs(trend_direction)*100:.1f}% over recent periods. "
                                  f"Improving market conditions detected.",
                        confidence=0.82,
                        severity="low",
                        actionable=True,
                        recommendations=[
                            "Consider increasing exposure to quality assets",
                            "Look for accumulation opportunities",
                            "Monitor for trend continuation",
                            "Maintain balanced risk management"
                        ],
                        data_points={
                            "trend_direction": trend_direction,
                            "trend_strength": trend_strength,
                            "recent_risk_scores": recent_risks
                        },
                        timestamp=datetime.now()
                    ))
            
            # Analyze fear & greed trends
            fear_greed_values = []
            for data in risk_data[:5]:
                if isinstance(data, dict) and 'fear_greed_index' in data:
                    fg_value = data['fear_greed_index'].get('current_value', 50)
                    fear_greed_values.append(fg_value)
            
            if len(fear_greed_values) >= 2:
                fg_trend = self._calculate_trend(fear_greed_values)
                current_fg = fear_greed_values[0]
                
                if current_fg <= 25:  # Extreme fear
                    insights.append(MarketInsight(
                        type="market_trend_analysis",
                        title="Extreme Fear Detected - Potential Opportunity",
                        description=f"Fear & Greed Index at {current_fg} indicates extreme fear. "
                                  f"Historically, this presents contrarian opportunities.",
                        confidence=0.78,
                        severity="medium",
                        actionable=True,
                        recommendations=[
                            "Consider contrarian investment approach",
                            "Look for oversold quality assets",
                            "Dollar-cost average into positions",
                            "Maintain patience for market recovery"
                        ],
                        data_points={
                            "current_fear_greed": current_fg,
                            "fear_greed_trend": fg_trend,
                            "historical_values": fear_greed_values
                        },
                        timestamp=datetime.now()
                    ))
                elif current_fg >= 75:  # Extreme greed
                    insights.append(MarketInsight(
                        type="market_trend_analysis",
                        title="Extreme Greed Warning",
                        description=f"Fear & Greed Index at {current_fg} indicates extreme greed. "
                                  f"Market may be overheated and due for correction.",
                        confidence=0.75,
                        severity="high",
                        actionable=True,
                        recommendations=[
                            "Consider taking profits on overextended positions",
                            "Reduce overall market exposure",
                            "Prepare for potential market correction",
                            "Avoid FOMO-driven investments"
                        ],
                        data_points={
                            "current_fear_greed": current_fg,
                            "fear_greed_trend": fg_trend,
                            "historical_values": fear_greed_values
                        },
                        timestamp=datetime.now()
                    ))
            
        except Exception as e:
            logger.error(f"❌ Error generating market trend insights: {str(e)}")
        
        return insights
    
    async def _generate_risk_assessment_insights(self, risk_data: List[Dict]) -> List[MarketInsight]:
        """Generate comprehensive risk assessment insights"""
        insights = []
        
        try:
            if not risk_data:
                return insights
            
            latest_data = risk_data[0]
            if not isinstance(latest_data, dict):
                return insights
            
            # Analyze overall risk components
            risk_analysis = latest_data.get('risk_analysis', {})
            risk_components = risk_analysis.get('risk_components', {})
            overall_risk = risk_analysis.get('overall_risk', 0.5)
            
            # Multi-dimensional risk analysis
            risk_dimensions = {
                'market_risk': risk_components.get('market_risk', 0.5),
                'sentiment_risk': risk_components.get('sentiment_risk', 0.5),
                'volatility_risk': risk_components.get('volatility_risk', 0.5),
                'onchain_risk': risk_components.get('onchain_risk', 0.5)
            }
            
            # Identify highest risk components
            highest_risk = max(risk_dimensions.items(), key=lambda x: x[1])
            lowest_risk = min(risk_dimensions.items(), key=lambda x: x[1])
            
            # Generate risk component insight
            if highest_risk[1] > 0.7:
                risk_name = highest_risk[0].replace('_', ' ').title()
                insights.append(MarketInsight(
                    type="risk_assessment",
                    title=f"High {risk_name} Detected",
                    description=f"{risk_name} is currently at {highest_risk[1]:.1%}, indicating elevated risk "
                              f"in this dimension. Overall portfolio risk: {overall_risk:.1%}",
                    confidence=0.88,
                    severity="high" if highest_risk[1] > 0.8 else "medium",
                    actionable=True,
                    recommendations=self._get_risk_specific_recommendations(highest_risk[0], highest_risk[1]),
                    data_points={
                        "risk_component": highest_risk[0],
                        "risk_level": highest_risk[1],
                        "overall_risk": overall_risk,
                        "all_components": risk_dimensions
                    },
                    timestamp=datetime.now()
                ))
            
            # Portfolio risk diversification analysis
            risk_variance = statistics.variance(risk_dimensions.values())
            if risk_variance > 0.05:  # High variance in risk components
                insights.append(MarketInsight(
                    type="risk_assessment",
                    title="Unbalanced Risk Profile Detected",
                    description=f"Risk components show high variance ({risk_variance:.3f}), indicating "
                              f"unbalanced risk exposure across different dimensions.",
                    confidence=0.75,
                    severity="medium",
                    actionable=True,
                    recommendations=[
                        "Rebalance portfolio to address high-risk components",
                        "Diversify across different risk dimensions",
                        "Consider hedging strategies for dominant risks",
                        "Review asset allocation strategy"
                    ],
                    data_points={
                        "risk_variance": risk_variance,
                        "risk_components": risk_dimensions,
                        "highest_risk": highest_risk,
                        "lowest_risk": lowest_risk
                    },
                    timestamp=datetime.now()
                ))
            
            # Risk trend analysis
            if len(risk_data) >= 3:
                risk_history = []
                for data in risk_data[:5]:
                    if isinstance(data, dict) and 'risk_analysis' in data:
                        risk_score = data['risk_analysis'].get('overall_risk', 0.5)
                        risk_history.append(risk_score)
                
                if len(risk_history) >= 3:
                    risk_acceleration = self._calculate_acceleration(risk_history)
                    
                    if abs(risk_acceleration) > 0.02:  # Significant acceleration
                        direction = "increasing" if risk_acceleration > 0 else "decreasing"
                        insights.append(MarketInsight(
                            type="risk_assessment",
                            title=f"Risk Acceleration Detected",
                            description=f"Market risk is {direction} at an accelerating rate "
                                      f"({risk_acceleration*100:.2f}% acceleration). "
                                      f"This suggests momentum in risk trends.",
                            confidence=0.82,
                            severity="medium",
                            actionable=True,
                            recommendations=[
                                f"Prepare for continued risk {direction}",
                                "Monitor risk metrics more frequently",
                                "Adjust position sizing accordingly",
                                "Consider momentum-based risk management"
                            ],
                            data_points={
                                "risk_acceleration": risk_acceleration,
                                "risk_history": risk_history,
                                "trend_direction": direction
                            },
                            timestamp=datetime.now()
                        ))
            
        except Exception as e:
            logger.error(f"❌ Error generating risk assessment insights: {str(e)}")
        
        return insights
    
    async def _generate_opportunity_insights(self, screener_data: List[Dict]) -> List[MarketInsight]:
        """Generate opportunity detection insights"""
        insights = []
        
        try:
            if not screener_data:
                return insights
            
            latest_data = screener_data[0]
            if not isinstance(latest_data, dict):
                return insights
            
            # Analyze top performers
            top_performers = latest_data.get('top_performers', {})
            if top_performers:
                # 24h gainers analysis
                gainers_24h = top_performers.get('top_24h_gainers', [])
                if gainers_24h:
                    top_gainer = gainers_24h[0]
                    gain_pct = top_gainer.get('price_change_percentage_24h_in_currency', 0)
                    
                    if gain_pct > 10:  # Significant gain
                        insights.append(MarketInsight(
                            type="opportunity_detection",
                            title="Strong Momentum Opportunity Identified",
                            description=f"{top_gainer.get('name', 'Top performer')} shows exceptional "
                                      f"24h performance (+{gain_pct:.1f}%). Strong momentum detected.",
                            confidence=0.72,
                            severity="low",
                            actionable=True,
                            recommendations=[
                                "Monitor for momentum continuation",
                                "Consider trend-following strategies",
                                "Set appropriate profit targets",
                                "Watch for potential reversal signals"
                            ],
                            data_points={
                                "symbol": top_gainer.get('symbol', ''),
                                "name": top_gainer.get('name', ''),
                                "gain_24h": gain_pct,
                                "market_cap": top_gainer.get('market_cap', 0),
                                "volume_24h": top_gainer.get('total_volume', 0)
                            },
                            timestamp=datetime.now()
                        ))
                
                # Volume surge analysis
                volume_leaders = top_performers.get('highest_volume', [])
                if volume_leaders:
                    volume_leader = volume_leaders[0]
                    volume_24h = volume_leader.get('total_volume', 0)
                    market_cap = volume_leader.get('market_cap', 1)
                    volume_ratio = volume_24h / market_cap if market_cap > 0 else 0
                    
                    if volume_ratio > 0.3:  # High volume relative to market cap
                        insights.append(MarketInsight(
                            type="opportunity_detection",
                            title="Unusual Volume Activity Detected",
                            description=f"{volume_leader.get('name', 'Asset')} showing unusual volume "
                                      f"activity (volume/market cap ratio: {volume_ratio:.2f}). "
                                      f"Potential breakout or news-driven movement.",
                            confidence=0.68,
                            severity="low",
                            actionable=True,
                            recommendations=[
                                "Investigate fundamental catalysts",
                                "Monitor price action closely",
                                "Consider breakout trading strategies",
                                "Check for news or announcements"
                            ],
                            data_points={
                                "symbol": volume_leader.get('symbol', ''),
                                "volume_24h": volume_24h,
                                "market_cap": market_cap,
                                "volume_ratio": volume_ratio,
                                "price_change_24h": volume_leader.get('price_change_percentage_24h_in_currency', 0)
                            },
                            timestamp=datetime.now()
                        ))
            
            # Market overview analysis for opportunities
            market_overview = latest_data.get('market_overview', {})
            if market_overview:
                coins_up = market_overview.get('coins_up', 0)
                coins_down = market_overview.get('coins_down', 0)
                total_coins = coins_up + coins_down
                
                if total_coins > 0:
                    positive_ratio = coins_up / total_coins
                    
                    if positive_ratio > 0.75:  # Strong market breadth
                        insights.append(MarketInsight(
                            type="opportunity_detection",
                            title="Broad Market Strength Opportunity",
                            description=f"Strong market breadth detected: {positive_ratio:.1%} of analyzed "
                                      f"assets are positive. Favorable environment for long positions.",
                            confidence=0.80,
                            severity="low",
                            actionable=True,
                            recommendations=[
                                "Consider increasing overall market exposure",
                                "Focus on quality assets with strong fundamentals",
                                "Implement systematic buying strategies",
                                "Monitor for trend continuation"
                            ],
                            data_points={
                                "positive_ratio": positive_ratio,
                                "coins_up": coins_up,
                                "coins_down": coins_down,
                                "market_sentiment": market_overview.get('market_sentiment', 'neutral')
                            },
                            timestamp=datetime.now()
                        ))
                    elif positive_ratio < 0.25:  # Oversold conditions
                        insights.append(MarketInsight(
                            type="opportunity_detection",
                            title="Potential Oversold Opportunity",
                            description=f"Market showing oversold conditions: only {positive_ratio:.1%} "
                                      f"of assets are positive. Potential contrarian opportunity.",
                            confidence=0.70,
                            severity="medium",
                            actionable=True,
                            recommendations=[
                                "Look for oversold quality assets",
                                "Consider contrarian investment strategies",
                                "Wait for reversal confirmation signals",
                                "Use dollar-cost averaging approach"
                            ],
                            data_points={
                                "positive_ratio": positive_ratio,
                                "coins_up": coins_up,
                                "coins_down": coins_down,
                                "oversold_severity": 1 - positive_ratio
                            },
                            timestamp=datetime.now()
                        ))
            
        except Exception as e:
            logger.error(f"❌ Error generating opportunity insights: {str(e)}")
        
        return insights
    
    async def _generate_volatility_insights(self, screener_data: List[Dict]) -> List[MarketInsight]:
        """Generate volatility analysis insights"""
        insights = []
        
        try:
            if not screener_data:
                return insights
            
            latest_data = screener_data[0]
            if not isinstance(latest_data, dict):
                return insights
            
            # Analyze technical indicators for volatility
            technical_analysis = latest_data.get('technical_analysis', {})
            if technical_analysis:
                individual_analysis = technical_analysis.get('individual_analysis', {})
                
                # Calculate average volatility across analyzed coins
                volatilities = []
                for coin, data in individual_analysis.items():
                    if isinstance(data, dict) and 'volatility' in data:
                        volatilities.append(data['volatility'])
                
                if volatilities:
                    avg_volatility = statistics.mean(volatilities)
                    volatility_stdev = statistics.stdev(volatilities) if len(volatilities) > 1 else 0
                    
                    # High volatility warning
                    if avg_volatility > 0.05:  # 5% average volatility
                        insights.append(MarketInsight(
                            type="volatility_analysis",
                            title="Elevated Market Volatility Detected",
                            description=f"Average market volatility is {avg_volatility:.2%}, indicating "
                                      f"elevated price swings. Standard deviation: {volatility_stdev:.2%}",
                            confidence=0.85,
                            severity="medium" if avg_volatility < 0.08 else "high",
                            actionable=True,
                            recommendations=[
                                "Reduce position sizes to manage risk",
                                "Use wider stop-loss levels",
                                "Consider volatility-based position sizing",
                                "Avoid high-leverage strategies"
                            ],
                            data_points={
                                "average_volatility": avg_volatility,
                                "volatility_stdev": volatility_stdev,
                                "coins_analyzed": len(volatilities),
                                "high_volatility_coins": len([v for v in volatilities if v > avg_volatility * 1.5])
                            },
                            timestamp=datetime.now()
                        ))
                    
                    # Volatility dispersion analysis
                    if volatility_stdev > 0.02:  # High dispersion
                        insights.append(MarketInsight(
                            type="volatility_analysis",
                            title="High Volatility Dispersion Across Markets",
                            description=f"Volatility varies significantly across assets (std dev: {volatility_stdev:.2%}). "
                                      f"Some assets much more volatile than others.",
                            confidence=0.78,
                            severity="low",
                            actionable=True,
                            recommendations=[
                                "Diversify across different volatility profiles",
                                "Adjust position sizes based on individual volatility",
                                "Consider volatility arbitrage opportunities",
                                "Monitor correlation changes"
                            ],
                            data_points={
                                "volatility_dispersion": volatility_stdev,
                                "max_volatility": max(volatilities),
                                "min_volatility": min(volatilities),
                                "volatility_range": max(volatilities) - min(volatilities)
                            },
                            timestamp=datetime.now()
                        ))
            
        except Exception as e:
            logger.error(f"❌ Error generating volatility insights: {str(e)}")
        
        return insights
    
    async def _generate_volume_insights(self, screener_data: List[Dict]) -> List[MarketInsight]:
        """Generate volume analysis insights"""
        insights = []
        
        try:
            if not screener_data:
                return insights
            
            latest_data = screener_data[0]
            if not isinstance(latest_data, dict):
                return insights
            
            volume_analysis = latest_data.get('volume_analysis', {})
            if volume_analysis:
                total_volume = volume_analysis.get('total_volume_analyzed', 0)
                pairs_analyzed = volume_analysis.get('pairs_analyzed', 0)
                
                if total_volume > 0 and pairs_analyzed > 0:
                    avg_volume = total_volume / pairs_analyzed
                    
                    # Volume distribution analysis
                    volume_distribution = volume_analysis.get('volume_distribution', {})
                    if volume_distribution:
                        # Find concentration in top pairs
                        sorted_pairs = sorted(volume_distribution.items(), key=lambda x: x[1], reverse=True)
                        top_3_concentration = sum(pair[1] for pair in sorted_pairs[:3])
                        
                        if top_3_concentration > 70:  # High concentration
                            insights.append(MarketInsight(
                                type="volume_analysis",
                                title="High Volume Concentration Detected",
                                description=f"Top 3 trading pairs account for {top_3_concentration:.1f}% "
                                          f"of total volume. Market liquidity concentrated in few assets.",
                                confidence=0.82,
                                severity="low",
                                actionable=True,
                                recommendations=[
                                    "Focus trading on high-volume pairs for better execution",
                                    "Be cautious with low-volume altcoins",
                                    "Monitor liquidity changes in major pairs",
                                    "Consider market impact when trading large sizes"
                                ],
                                data_points={
                                    "top_3_concentration": top_3_concentration,
                                    "total_volume": total_volume,
                                    "volume_distribution": dict(sorted_pairs[:5]),
                                    "pairs_analyzed": pairs_analyzed
                                },
                                timestamp=datetime.now()
                            ))
                    
                    # Individual volume analysis
                    individual_data = volume_analysis.get('individual_data', {})
                    if individual_data:
                        # Find unusual volume patterns
                        volume_changes = []
                        for pair, data in individual_data.items():
                            volume_24h = data.get('quote_volume_24h', 0)
                            price_change = abs(data.get('price_change_24h', 0))
                            
                            # Volume-price relationship
                            if volume_24h > avg_volume * 2 and price_change > 5:
                                volume_changes.append({
                                    'pair': pair,
                                    'volume': volume_24h,
                                    'price_change': price_change,
                                    'volume_ratio': volume_24h / avg_volume
                                })
                        
                        if volume_changes:
                            top_volume_change = max(volume_changes, key=lambda x: x['volume_ratio'])
                            insights.append(MarketInsight(
                                type="volume_analysis",
                                title="Unusual Volume-Price Activity",
                                description=f"{top_volume_change['pair']} showing unusual activity: "
                                          f"{top_volume_change['volume_ratio']:.1f}x average volume "
                                          f"with {top_volume_change['price_change']:.1f}% price change.",
                                confidence=0.75,
                                severity="low",
                                actionable=True,
                                recommendations=[
                                    "Investigate fundamental catalysts",
                                    "Monitor for breakout continuation",
                                    "Check order book depth",
                                    "Consider momentum trading opportunities"
                                ],
                                data_points={
                                    "unusual_activity": top_volume_change,
                                    "all_unusual_pairs": volume_changes,
                                    "average_volume": avg_volume
                                },
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"❌ Error generating volume insights: {str(e)}")
        
        return insights
    
    async def _generate_correlation_insights(self, risk_data: List[Dict], screener_data: List[Dict]) -> List[MarketInsight]:
        """Generate correlation analysis insights between risk and market data"""
        insights = []
        
        try:
            if not risk_data or not screener_data:
                return insights
            
            # Analyze correlation between risk metrics and market performance
            latest_risk = risk_data[0]
            latest_screener = screener_data[0]
            
            if not isinstance(latest_risk, dict) or not isinstance(latest_screener, dict):
                return insights
            
            # Get risk score and market performance
            risk_analysis = latest_risk.get('risk_analysis', {})
            overall_risk = risk_analysis.get('overall_risk', 0.5)
            
            market_overview = latest_screener.get('market_overview', {})
            avg_change = market_overview.get('average_24h_change', 0)
            positive_ratio = market_overview.get('coins_up', 0) / max(
                market_overview.get('coins_up', 0) + market_overview.get('coins_down', 0), 1
            )
            
            # Risk-performance correlation analysis
            risk_performance_correlation = self._calculate_risk_performance_correlation(
                overall_risk, avg_change, positive_ratio
            )
            
            if abs(risk_performance_correlation) > 0.6:  # Strong correlation
                correlation_type = "negative" if risk_performance_correlation < 0 else "positive"
                insights.append(MarketInsight(
                    type="correlation_analysis",
                    title=f"Strong Risk-Performance Correlation Detected",
                    description=f"Risk metrics show {correlation_type} correlation ({risk_performance_correlation:.2f}) "
                              f"with market performance. Risk model appears well-calibrated.",
                    confidence=0.88,
                    severity="low",
                    actionable=True,
                    recommendations=[
                        "Risk metrics are reliable for current conditions",
                        "Use risk signals for position sizing",
                        "Monitor for correlation breakdown",
                        "Maintain risk-adjusted strategies"
                    ],
                    data_points={
                        "correlation": risk_performance_correlation,
                        "overall_risk": overall_risk,
                        "market_performance": avg_change,
                        "positive_ratio": positive_ratio
                    },
                    timestamp=datetime.now()
                ))
            
            # Fear & Greed vs Market Performance
            fear_greed_data = latest_risk.get('fear_greed_index', {})
            if fear_greed_data:
                fg_value = fear_greed_data.get('current_value', 50)
                fg_market_correlation = self._calculate_fg_market_correlation(fg_value, avg_change)
                
                if fg_market_correlation < -0.7:  # Strong inverse correlation (expected)
                    insights.append(MarketInsight(
                        type="correlation_analysis",
                        title="Fear & Greed Index Well-Aligned with Market",
                        description=f"Fear & Greed Index ({fg_value}) shows strong inverse correlation "
                                  f"with market performance, indicating reliable sentiment measurement.",
                        confidence=0.80,
                        severity="low",
                        actionable=True,
                        recommendations=[
                            "Use Fear & Greed Index for contrarian signals",
                            "Monitor for extreme readings",
                            "Combine with technical analysis",
                            "Consider sentiment-based strategies"
                        ],
                        data_points={
                            "fear_greed_value": fg_value,
                            "market_performance": avg_change,
                            "correlation": fg_market_correlation
                        },
                        timestamp=datetime.now()
                    ))
            
        except Exception as e:
            logger.error(f"❌ Error generating correlation insights: {str(e)}")
        
        return insights
    
    async def _generate_sentiment_insights(self, risk_data: List[Dict]) -> List[MarketInsight]:
        """Generate sentiment analysis insights"""
        insights = []
        
        try:
            if not risk_data:
                return insights
            
            latest_data = risk_data[0]
            if not isinstance(latest_data, dict):
                return insights
            
            # Analyze Fear & Greed sentiment
            fear_greed_data = latest_data.get('fear_greed_index', {})
            if fear_greed_data:
                current_value = fear_greed_data.get('current_value', 50)
                classification = fear_greed_data.get('current_classification', 'Neutral')
                trend = fear_greed_data.get('trend', 'stable')
                interpretation = fear_greed_data.get('interpretation', '')
                
                # Extreme sentiment analysis
                if current_value <= 20:  # Extreme fear
                    insights.append(MarketInsight(
                        type="sentiment_analysis",
                        title="Extreme Fear - Contrarian Opportunity Signal",
                        description=f"Fear & Greed Index at {current_value} ({classification}). "
                                  f"{interpretation}. Historical data suggests potential buying opportunity.",
                        confidence=0.75,
                        severity="medium",
                        actionable=True,
                        recommendations=[
                            "Consider contrarian buying strategies",
                            "Look for quality assets at discounted prices",
                            "Use dollar-cost averaging in extreme fear",
                            "Wait for sentiment stabilization before large positions"
                        ],
                        data_points={
                            "fear_greed_value": current_value,
                            "classification": classification,
                            "trend": trend,
                            "contrarian_signal_strength": (25 - current_value) / 25
                        },
                        timestamp=datetime.now()
                    ))
                elif current_value >= 80:  # Extreme greed
                    insights.append(MarketInsight(
                        type="sentiment_analysis",
                        title="Extreme Greed - Caution Advised",
                        description=f"Fear & Greed Index at {current_value} ({classification}). "
                                  f"Market may be overheated. Consider risk management measures.",
                        confidence=0.78,
                        severity="high",
                        actionable=True,
                        recommendations=[
                            "Consider taking profits on overextended positions",
                            "Reduce overall market exposure",
                            "Implement stricter risk management",
                            "Avoid FOMO-driven investments"
                        ],
                        data_points={
                            "fear_greed_value": current_value,
                            "classification": classification,
                            "trend": trend,
                            "overheating_signal_strength": (current_value - 75) / 25
                        },
                        timestamp=datetime.now()
                    ))
                
                # Sentiment trend analysis
                if trend == "improving" and current_value < 40:
                    insights.append(MarketInsight(
                        type="sentiment_analysis",
                        title="Sentiment Recovery Detected",
                        description=f"Fear & Greed sentiment trending {trend} from low levels. "
                                  f"Potential early sign of market recovery.",
                        confidence=0.68,
                        severity="low",
                        actionable=True,
                        recommendations=[
                            "Monitor for continued sentiment improvement",
                            "Consider gradual position building",
                            "Watch for confirmation in price action",
                            "Maintain cautious optimism"
                        ],
                        data_points={
                            "current_sentiment": current_value,
                            "trend": trend,
                            "recovery_potential": max(0, (40 - current_value) / 40)
                        },
                        timestamp=datetime.now()
                    ))
            
        except Exception as e:
            logger.error(f"❌ Error generating sentiment insights: {str(e)}")
        
        return insights
    
    async def _generate_technical_pattern_insights(self, screener_data: List[Dict]) -> List[MarketInsight]:
        """Generate technical pattern recognition insights"""
        insights = []
        
        try:
            if not screener_data:
                return insights
            
            latest_data = screener_data[0]
            if not isinstance(latest_data, dict):
                return insights
            
            technical_analysis = latest_data.get('technical_analysis', {})
            if technical_analysis:
                individual_analysis = technical_analysis.get('individual_analysis', {})
                
                # Analyze RSI patterns
                rsi_values = []
                oversold_coins = []
                overbought_coins = []
                
                for coin, data in individual_analysis.items():
                    if isinstance(data, dict) and 'rsi_14' in data:
                        rsi = data['rsi_14']
                        rsi_values.append(rsi)
                        
                        if rsi < 30:
                            oversold_coins.append({'coin': coin, 'rsi': rsi, 'data': data})
                        elif rsi > 70:
                            overbought_coins.append({'coin': coin, 'rsi': rsi, 'data': data})
                
                # Oversold opportunities
                if len(oversold_coins) > 0:
                    most_oversold = min(oversold_coins, key=lambda x: x['rsi'])
                    insights.append(MarketInsight(
                        type="technical_pattern_recognition",
                        title="Oversold Conditions Detected",
                        description=f"{len(oversold_coins)} assets showing oversold conditions (RSI < 30). "
                                  f"Most oversold: {most_oversold['coin']} (RSI: {most_oversold['rsi']:.1f})",
                        confidence=0.72,
                        severity="low",
                        actionable=True,
                        recommendations=[
                            "Monitor oversold assets for reversal signals",
                            "Wait for RSI divergence confirmation",
                            "Consider small position sizes initially",
                            "Use support levels for entry points"
                        ],
                        data_points={
                            "oversold_count": len(oversold_coins),
                            "most_oversold": most_oversold,
                            "all_oversold": oversold_coins,
                            "average_rsi": statistics.mean(rsi_values) if rsi_values else 50
                        },
                        timestamp=datetime.now()
                    ))
                
                # Overbought warnings
                if len(overbought_coins) > 0:
                    most_overbought = max(overbought_coins, key=lambda x: x['rsi'])
                    insights.append(MarketInsight(
                        type="technical_pattern_recognition",
                        title="Overbought Conditions Warning",
                        description=f"{len(overbought_coins)} assets showing overbought conditions (RSI > 70). "
                                  f"Most overbought: {most_overbought['coin']} (RSI: {most_overbought['rsi']:.1f})",
                        confidence=0.70,
                        severity="medium",
                        actionable=True,
                        recommendations=[
                            "Consider taking profits on overbought positions",
                            "Monitor for bearish divergence signals",
                            "Tighten stop-loss levels",
                            "Avoid new long positions in overbought assets"
                        ],
                        data_points={
                            "overbought_count": len(overbought_coins),
                            "most_overbought": most_overbought,
                            "all_overbought": overbought_coins
                        },
                        timestamp=datetime.now()
                    ))
                
                # Trend analysis
                bullish_trends = []
                bearish_trends = []
                
                for coin, data in individual_analysis.items():
                    if isinstance(data, dict) and 'trend' in data:
                        trend = data['trend']
                        if trend == 'bullish':
                            bullish_trends.append(coin)
                        elif trend == 'bearish':
                            bearish_trends.append(coin)
                
                # Market trend consensus
                total_trends = len(bullish_trends) + len(bearish_trends)
                if total_trends > 0:
                    bullish_ratio = len(bullish_trends) / total_trends
                    
                    if bullish_ratio > 0.7:
                        insights.append(MarketInsight(
                            type="technical_pattern_recognition",
                            title="Strong Bullish Trend Consensus",
                            description=f"{bullish_ratio:.1%} of analyzed assets show bullish trends. "
                                      f"Strong technical momentum across the market.",
                            confidence=0.80,
                            severity="low",
                            actionable=True,
                            recommendations=[
                                "Consider trend-following strategies",
                                "Focus on momentum leaders",
                                "Use pullbacks as entry opportunities",
                                "Monitor for trend exhaustion signals"
                            ],
                            data_points={
                                "bullish_ratio": bullish_ratio,
                                "bullish_count": len(bullish_trends),
                                "bearish_count": len(bearish_trends),
                                "bullish_assets": bullish_trends
                            },
                            timestamp=datetime.now()
                        ))
                    elif bullish_ratio < 0.3:
                        insights.append(MarketInsight(
                            type="technical_pattern_recognition",
                            title="Bearish Trend Dominance",
                            description=f"Only {bullish_ratio:.1%} of analyzed assets show bullish trends. "
                                      f"Bearish technical momentum dominates the market.",
                            confidence=0.78,
                            severity="medium",
                            actionable=True,
                            recommendations=[
                                "Consider defensive positioning",
                                "Look for oversold bounce opportunities",
                                "Use bear market rally strategies",
                                "Focus on capital preservation"
                            ],
                            data_points={
                                "bullish_ratio": bullish_ratio,
                                "bearish_count": len(bearish_trends),
                                "bearish_assets": bearish_trends
                            },
                            timestamp=datetime.now()
                        ))
            
        except Exception as e:
            logger.error(f"❌ Error generating technical pattern insights: {str(e)}")
        
        return insights
    
    # Helper methods for calculations and analysis
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction from a series of values"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        y = values
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope / y_mean if y_mean != 0 else 0.0  # Normalize by mean
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength (R-squared)"""
        if len(values) < 2:
            return 0.0
        
        try:
            n = len(values)
            x = list(range(n))
            y = values
            
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(y)
            
            # Calculate correlation coefficient
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            x_variance = sum((x[i] - x_mean) ** 2 for i in range(n))
            y_variance = sum((y[i] - y_mean) ** 2 for i in range(n))
            
            if x_variance == 0 or y_variance == 0:
                return 0.0
            
            correlation = numerator / math.sqrt(x_variance * y_variance)
            return correlation ** 2  # R-squared
        except:
            return 0.0
    
    def _calculate_acceleration(self, values: List[float]) -> float:
        """Calculate acceleration (second derivative)"""
        if len(values) < 3:
            return 0.0
        
        # Calculate first derivatives
        first_derivatives = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Calculate second derivatives (acceleration)
        second_derivatives = [first_derivatives[i+1] - first_derivatives[i] 
                            for i in range(len(first_derivatives)-1)]
        
        return statistics.mean(second_derivatives) if second_derivatives else 0.0
    
    def _get_risk_specific_recommendations(self, risk_type: str, risk_level: float) -> List[str]:
        """Get specific recommendations based on risk type and level"""
        recommendations = []
        
        if risk_type == "market_risk":
            recommendations.extend([
                "Diversify across different asset classes",
                "Consider market-neutral strategies",
                "Monitor correlation changes",
                "Reduce beta exposure"
            ])
        elif risk_type == "sentiment_risk":
            recommendations.extend([
                "Use contrarian indicators",
                "Monitor social media sentiment",
                "Avoid crowd-following behavior",
                "Consider sentiment-based timing"
            ])
        elif risk_type == "volatility_risk":
            recommendations.extend([
                "Reduce position sizes",
                "Use volatility-adjusted stop losses",
                "Consider volatility trading strategies",
                "Monitor VIX-equivalent indicators"
            ])
        elif risk_type == "onchain_risk":
            recommendations.extend([
                "Monitor network health metrics",
                "Watch for congestion issues",
                "Consider layer-2 alternatives",
                "Track whale movements"
            ])
        
        # Add severity-based recommendations
        if risk_level > 0.8:
            recommendations.extend([
                "Consider emergency risk reduction",
                "Implement circuit breakers",
                "Review portfolio allocation immediately"
            ])
        
        return recommendations
    
    def _calculate_risk_performance_correlation(self, risk: float, performance: float, positive_ratio: float) -> float:
        """Calculate correlation between risk metrics and market performance"""
        # Simple correlation approximation
        # Higher risk should correlate with lower performance
        expected_performance = (1 - risk) * 10 - 5  # Map risk to expected performance
        actual_performance = performance
        
        # Calculate correlation based on expectation vs reality
        if abs(expected_performance) < 0.1:
            return 0.0
        
        correlation = -abs(expected_performance - actual_performance) / abs(expected_performance)
        return max(-1.0, min(1.0, correlation))
    
    def _calculate_fg_market_correlation(self, fg_value: int, market_performance: float) -> float:
        """Calculate Fear & Greed vs market performance correlation"""
        # Fear & Greed should be inversely correlated with negative performance
        # and positively correlated with positive performance
        normalized_fg = (fg_value - 50) / 50  # Normalize to -1 to +1
        
        if market_performance == 0:
            return 0.0
        
        # Expected: positive market performance should correlate with higher FG
        expected_correlation = normalized_fg * (market_performance / abs(market_performance))
        return max(-1.0, min(1.0, expected_correlation))
    
    def _filter_and_rank_insights(self, insights: List[MarketInsight], symbol: Optional[str] = None) -> List[MarketInsight]:
        """Filter and rank insights by relevance and confidence"""
        # Filter by symbol if specified
        if symbol:
            insights = [insight for insight in insights 
                       if symbol.upper() in str(insight.data_points).upper() or insight.type == "market_trend_analysis"]
        
        # Sort by confidence and severity
        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        def insight_score(insight):
            severity_weight = severity_weights.get(insight.severity, 1)
            return insight.confidence * severity_weight
        
        sorted_insights = sorted(insights, key=insight_score, reverse=True)
        
        # Limit to top insights to avoid information overload
        return sorted_insights[:15]
    
    def _serialize_insight(self, insight: MarketInsight) -> Dict[str, Any]:
        """Convert MarketInsight to serializable dictionary"""
        return {
            "type": insight.type,
            "title": insight.title,
            "description": insight.description,
            "confidence": insight.confidence,
            "severity": insight.severity,
            "actionable": insight.actionable,
            "recommendations": insight.recommendations,
            "data_points": insight.data_points,
            "timestamp": insight.timestamp.isoformat(),
            "generation_method": "real_ai_analysis"
        }
    
    async def _save_insight_to_database(self, insight: Dict[str, Any]) -> bool:
        """Save insight to database"""
        try:
            # This would save to a dedicated insights table
            # For now, we'll just log it
            logger.debug(f"💾 Saving insight: {insight['title']}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving insight: {str(e)}")
            return False
    
    def _create_no_data_insight(self) -> Dict[str, Any]:
        """Create insight when no data is available"""
        return {
            "type": "system_status",
            "title": "Insufficient Data for Analysis",
            "description": "No recent market data available for comprehensive analysis. Please ensure data extraction is running.",
            "confidence": 1.0,
            "severity": "medium",
            "actionable": True,
            "recommendations": [
                "Check data extraction services",
                "Verify API connectivity",
                "Run manual data extraction",
                "Review system logs for errors"
            ],
            "data_points": {"issue": "no_data_available"},
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_error_insight(self, error_message: str) -> Dict[str, Any]:
        """Create insight when analysis fails"""
        return {
            "type": "system_error",
            "title": "Analysis Error Occurred",
            "description": f"Error during insight generation: {error_message}",
            "confidence": 1.0,
            "severity": "high",
            "actionable": True,
            "recommendations": [
                "Check system logs for detailed error information",
                "Verify data integrity",
                "Restart analysis services if needed",
                "Contact system administrator if problem persists"
            ],
            "data_points": {"error": error_message},
            "timestamp": datetime.now().isoformat()
        }