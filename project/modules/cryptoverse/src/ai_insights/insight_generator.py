#!/usr/bin/env python3
"""
AI Insight Generator
Generates AI-powered insights from Into The Cryptoverse data
Based on the comprehensive data pipeline system from the package
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import statistics

from ..database.cryptoverse_database import CryptoverseDatabase, DataExtractionResult

logger = logging.getLogger(__name__)

class InsightGenerator:
    """Generates AI-powered insights from extracted Cryptoverse data"""
    
    def __init__(self, database: CryptoverseDatabase):
        self.database = database
        logger.info("AI Insight Generator initialized")
    
    async def generate_insights(self, symbol: Optional[str] = None, 
                              insight_type: str = 'market_analysis') -> List[Dict[str, Any]]:
        """
        Generate AI insights based on current data
        
        Args:
            symbol: Specific symbol to analyze (optional)
            insight_type: Type of insight ('market_analysis', 'risk_assessment', 'opportunity')
        
        Returns:
            List of generated insights
        """
        try:
            insights = []
            
            if insight_type == 'market_analysis':
                insights.extend(await self._generate_market_analysis_insights(symbol))
            elif insight_type == 'risk_assessment':
                insights.extend(await self._generate_risk_assessment_insights(symbol))
            elif insight_type == 'opportunity':
                insights.extend(await self._generate_opportunity_insights(symbol))
            else:
                # Generate all types
                insights.extend(await self._generate_market_analysis_insights(symbol))
                insights.extend(await self._generate_risk_assessment_insights(symbol))
                insights.extend(await self._generate_opportunity_insights(symbol))
            
            # Save insights to database
            for insight in insights:
                await self._save_insight_to_database(insight)
            
            logger.info(f"Generated {len(insights)} insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def _generate_market_analysis_insights(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate market analysis insights"""
        insights = []
        
        try:
            # Get latest risk indicators
            risk_data = self.database.get_latest_data('crypto_risk_indicators', 5)
            screener_data = self.database.get_latest_data('screener_data', 50)
            dominance_data = self.database.get_latest_data('dominance_data', 5)
            
            # Overall market risk analysis
            if risk_data:
                latest_risk = risk_data[0]
                insights.append(await self._analyze_overall_market_risk(latest_risk))
            
            # Symbol-specific analysis
            if symbol and screener_data:
                symbol_data = [item for item in screener_data if item.get('symbol', '').upper() == symbol.upper()]
                if symbol_data:
                    insights.append(await self._analyze_symbol_performance(symbol, symbol_data))
            
            # Market dominance analysis
            if dominance_data:
                insights.append(await self._analyze_market_dominance(dominance_data))
            
            # Cross-symbol correlation analysis
            if screener_data:
                insights.append(await self._analyze_market_correlations(screener_data))
            
        except Exception as e:
            logger.error(f"Error generating market analysis insights: {str(e)}")
        
        return insights
    
    async def _generate_risk_assessment_insights(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate risk assessment insights"""
        insights = []
        
        try:
            # Get latest data
            risk_data = self.database.get_latest_data('crypto_risk_indicators', 10)
            screener_data = self.database.get_latest_data('screener_data', 50)
            
            # Risk trend analysis
            if len(risk_data) >= 2:
                insights.append(await self._analyze_risk_trends(risk_data))
            
            # Portfolio risk analysis
            if screener_data:
                insights.append(await self._analyze_portfolio_risk(screener_data))
            
            # Symbol-specific risk assessment
            if symbol and screener_data:
                symbol_data = [item for item in screener_data if item.get('symbol', '').upper() == symbol.upper()]
                if symbol_data:
                    insights.append(await self._assess_symbol_risk(symbol, symbol_data))
            
        except Exception as e:
            logger.error(f"Error generating risk assessment insights: {str(e)}")
        
        return insights
    
    async def _generate_opportunity_insights(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate opportunity insights"""
        insights = []
        
        try:
            # Get latest data
            screener_data = self.database.get_latest_data('screener_data', 50)
            risk_data = self.database.get_latest_data('crypto_risk_indicators', 5)
            
            # Low-risk opportunities
            if screener_data:
                insights.append(await self._identify_low_risk_opportunities(screener_data))
            
            # High-potential symbols
            if screener_data:
                insights.append(await self._identify_high_potential_symbols(screener_data))
            
            # Market timing opportunities
            if risk_data:
                insights.append(await self._identify_timing_opportunities(risk_data))
            
        except Exception as e:
            logger.error(f"Error generating opportunity insights: {str(e)}")
        
        return insights
    
    async def _analyze_overall_market_risk(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall market risk"""
        summary_risk = risk_data.get('summary_risk', 0)
        price_risk = risk_data.get('price_risk', 0)
        onchain_risk = risk_data.get('onchain_risk', 0)
        social_risk = risk_data.get('social_risk', 0)
        
        # Generate insight based on risk levels
        if summary_risk < 0.3:
            title = "Market Risk Remains Low - Favorable Conditions"
            description = f"Current market risk at {summary_risk:.1%} indicates favorable conditions for cryptocurrency investments. Price risk ({price_risk:.1%}) and on-chain metrics ({onchain_risk:.1%}) suggest potential upside opportunities."
            recommendation = "Consider increasing exposure to quality assets"
            risk_level = "Low"
        elif summary_risk < 0.6:
            title = "Moderate Market Risk - Balanced Approach Recommended"
            description = f"Market risk has increased to {summary_risk:.1%}, suggesting a more cautious approach. On-chain risk ({onchain_risk:.1%}) is elevated, indicating potential volatility ahead."
            recommendation = "Maintain balanced portfolio with risk management"
            risk_level = "Moderate"
        else:
            title = "High Market Risk - Defensive Positioning Advised"
            description = f"Market risk at {summary_risk:.1%} indicates challenging conditions. High price risk ({price_risk:.1%}) and elevated on-chain metrics suggest potential downside risks."
            recommendation = "Consider reducing exposure and increasing cash positions"
            risk_level = "High"
        
        return {
            "insight_type": "market_analysis",
            "symbol": None,
            "title": title,
            "description": description,
            "confidence_score": 0.85,
            "data_sources": ["crypto_risk_indicators"],
            "recommendation": recommendation,
            "risk_level": risk_level,
            "time_horizon": "short"
        }
    
    async def _analyze_symbol_performance(self, symbol: str, symbol_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual symbol performance"""
        if not symbol_data:
            return {}
        
        latest = symbol_data[0]
        risk = latest.get('fiat_risk', 0)
        price = latest.get('price', 0)
        risk_level = latest.get('risk_level', 'Unknown')
        
        # Generate symbol-specific insight
        if risk < 0.3:
            title = f"{symbol} Shows Low Risk Profile - Potential Entry Opportunity"
            description = f"{symbol} currently trades at ${price:.4f} with a low risk level of {risk:.1%}. This suggests the asset may be undervalued relative to its historical range."
            recommendation = f"Consider accumulating {symbol} at current levels"
        elif risk < 0.7:
            title = f"{symbol} in Moderate Risk Zone - Hold Current Positions"
            description = f"{symbol} at ${price:.4f} shows moderate risk ({risk:.1%}), indicating fair valuation. The asset is neither extremely cheap nor expensive."
            recommendation = f"Hold existing {symbol} positions, avoid major additions"
        else:
            title = f"{symbol} Elevated Risk - Consider Taking Profits"
            description = f"{symbol} trading at ${price:.4f} shows high risk level ({risk:.1%}), suggesting potential overvaluation. Historical data indicates elevated downside risk."
            recommendation = f"Consider reducing {symbol} exposure and taking profits"
        
        return {
            "insight_type": "market_analysis",
            "symbol": symbol,
            "title": title,
            "description": description,
            "confidence_score": 0.80,
            "data_sources": ["screener_data"],
            "recommendation": recommendation,
            "risk_level": risk_level,
            "time_horizon": "medium"
        }
    
    async def _analyze_market_dominance(self, dominance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market dominance trends"""
        if not dominance_data:
            return {}
        
        latest = dominance_data[0]
        btc_dom_with_stables = latest.get('btc_dominance_with_stables', 0)
        btc_dom_without_stables = latest.get('btc_dominance_without_stables', 0)
        trend = latest.get('trend', 'stable')
        
        if btc_dom_with_stables > 65:
            title = "Bitcoin Dominance High - Altcoin Caution Advised"
            description = f"Bitcoin dominance at {btc_dom_with_stables:.1f}% indicates strong BTC preference. This typically suggests risk-off sentiment and potential altcoin underperformance."
            recommendation = "Focus on Bitcoin over altcoins in current environment"
            risk_level = "Moderate"
        elif btc_dom_with_stables < 50:
            title = "Low Bitcoin Dominance - Altcoin Season Potential"
            description = f"Bitcoin dominance at {btc_dom_with_stables:.1f}% suggests strong altcoin interest. This environment typically favors diversified cryptocurrency exposure."
            recommendation = "Consider selective altcoin opportunities"
            risk_level = "Low"
        else:
            title = "Balanced Market Dominance - Neutral Positioning"
            description = f"Bitcoin dominance at {btc_dom_with_stables:.1f}% indicates balanced market conditions. Neither Bitcoin nor altcoins show clear dominance."
            recommendation = "Maintain balanced BTC/altcoin allocation"
            risk_level = "Moderate"
        
        return {
            "insight_type": "market_analysis",
            "symbol": None,
            "title": title,
            "description": description,
            "confidence_score": 0.75,
            "data_sources": ["dominance_data"],
            "recommendation": recommendation,
            "risk_level": risk_level,
            "time_horizon": "medium"
        }
    
    async def _identify_low_risk_opportunities(self, screener_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify low-risk investment opportunities"""
        if not screener_data:
            return {}
        
        # Find symbols with low risk (< 0.3)
        low_risk_symbols = [
            item for item in screener_data 
            if item.get('fiat_risk', 1) < 0.3 and item.get('symbol')
        ]
        
        if not low_risk_symbols:
            return {
                "insight_type": "opportunity",
                "symbol": None,
                "title": "Limited Low-Risk Opportunities Available",
                "description": "Currently, few cryptocurrencies show low-risk profiles. Market conditions suggest elevated valuations across most assets.",
                "confidence_score": 0.70,
                "data_sources": ["screener_data"],
                "recommendation": "Wait for better entry opportunities or focus on DCA strategies",
                "risk_level": "High",
                "time_horizon": "short"
            }
        
        # Sort by risk level (lowest first)
        low_risk_symbols.sort(key=lambda x: x.get('fiat_risk', 1))
        top_opportunities = low_risk_symbols[:3]
        
        symbols_list = ", ".join([item.get('symbol', '') for item in top_opportunities])
        avg_risk = statistics.mean([item.get('fiat_risk', 0) for item in top_opportunities])
        
        return {
            "insight_type": "opportunity",
            "symbol": None,
            "title": f"Low-Risk Opportunities Identified: {symbols_list}",
            "description": f"Found {len(low_risk_symbols)} symbols with low risk profiles (avg: {avg_risk:.1%}). Top opportunities include {symbols_list}, which show potential for favorable risk-adjusted returns.",
            "confidence_score": 0.80,
            "data_sources": ["screener_data"],
            "recommendation": f"Consider accumulating positions in {symbols_list}",
            "risk_level": "Low",
            "time_horizon": "medium"
        }
    
    async def _save_insight_to_database(self, insight: Dict[str, Any]):
        """Save generated insight to database"""
        try:
            result = DataExtractionResult(
                source="ai_insights_data",
                timestamp=datetime.now(),
                data=insight,
                success=True,
                confidence_score=insight.get('confidence_score', 0.5)
            )
            
            self.database.save_extraction_result(result)
            
        except Exception as e:
            logger.error(f"Error saving insight to database: {str(e)}")
    
    # Additional helper methods for comprehensive analysis
    async def _analyze_risk_trends(self, risk_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze risk trends over time"""
        if len(risk_data) < 2:
            return {}
        
        current = risk_data[0]
        previous = risk_data[1]
        
        current_risk = current.get('summary_risk', 0)
        previous_risk = previous.get('summary_risk', 0)
        
        change = current_risk - previous_risk
        change_pct = (change / previous_risk * 100) if previous_risk > 0 else 0
        
        if abs(change_pct) < 5:
            trend = "stable"
            title = "Market Risk Remains Stable"
            description = f"Market risk has remained relatively stable at {current_risk:.1%}, showing minimal change from previous reading."
        elif change_pct > 0:
            trend = "increasing"
            title = "Market Risk Trending Higher"
            description = f"Market risk has increased by {change_pct:.1f}% to {current_risk:.1%}, suggesting growing market stress."
        else:
            trend = "decreasing"
            title = "Market Risk Declining"
            description = f"Market risk has decreased by {abs(change_pct):.1f}% to {current_risk:.1%}, indicating improving market conditions."
        
        return {
            "insight_type": "risk_assessment",
            "symbol": None,
            "title": title,
            "description": description,
            "confidence_score": 0.75,
            "data_sources": ["crypto_risk_indicators"],
            "recommendation": f"Market risk trend is {trend}",
            "risk_level": "Moderate" if current_risk < 0.6 else "High",
            "time_horizon": "short"
        }
    
    async def _analyze_portfolio_risk(self, screener_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall portfolio risk"""
        if not screener_data:
            return {}
        
        risks = [item.get('fiat_risk', 0) for item in screener_data if item.get('fiat_risk') is not None]
        
        if not risks:
            return {}
        
        avg_risk = statistics.mean(risks)
        high_risk_count = sum(1 for risk in risks if risk > 0.7)
        low_risk_count = sum(1 for risk in risks if risk < 0.3)
        
        risk_distribution = f"{low_risk_count} low-risk, {len(risks) - high_risk_count - low_risk_count} moderate-risk, {high_risk_count} high-risk"
        
        if avg_risk < 0.4:
            title = "Portfolio Shows Favorable Risk Profile"
            recommendation = "Consider increasing allocation to crypto assets"
            risk_level = "Low"
        elif avg_risk < 0.6:
            title = "Portfolio Risk at Moderate Levels"
            recommendation = "Maintain current allocation with selective rebalancing"
            risk_level = "Moderate"
        else:
            title = "Portfolio Risk Elevated - Caution Advised"
            recommendation = "Consider reducing crypto exposure and increasing cash"
            risk_level = "High"
        
        return {
            "insight_type": "risk_assessment",
            "symbol": None,
            "title": title,
            "description": f"Portfolio average risk at {avg_risk:.1%} across {len(risks)} assets. Distribution: {risk_distribution}.",
            "confidence_score": 0.80,
            "data_sources": ["screener_data"],
            "recommendation": recommendation,
            "risk_level": risk_level,
            "time_horizon": "medium"
        }
    
    async def _analyze_market_correlations(self, screener_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between different assets"""
        # This is a simplified correlation analysis
        # In a real implementation, you'd use historical price data
        
        if len(screener_data) < 5:
            return {}
        
        risks = [item.get('fiat_risk', 0) for item in screener_data]
        avg_risk = statistics.mean(risks)
        risk_std = statistics.stdev(risks) if len(risks) > 1 else 0
        
        if risk_std < 0.1:
            correlation_level = "High"
            description = f"Assets show high correlation with similar risk levels (std: {risk_std:.3f}). Market is moving in sync."
            recommendation = "Diversification benefits are limited in current environment"
        elif risk_std < 0.2:
            correlation_level = "Moderate"
            description = f"Assets show moderate correlation with some dispersion (std: {risk_std:.3f}). Some diversification benefits available."
            recommendation = "Selective asset picking can add value"
        else:
            correlation_level = "Low"
            description = f"Assets show low correlation with significant dispersion (std: {risk_std:.3f}). Strong diversification opportunities."
            recommendation = "Focus on diversified portfolio construction"
        
        return {
            "insight_type": "market_analysis",
            "symbol": None,
            "title": f"{correlation_level} Asset Correlation Detected",
            "description": description,
            "confidence_score": 0.70,
            "data_sources": ["screener_data"],
            "recommendation": recommendation,
            "risk_level": "Moderate",
            "time_horizon": "medium"
        }
    
    async def _assess_symbol_risk(self, symbol: str, symbol_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risk for a specific symbol"""
        if not symbol_data:
            return {}
        
        latest = symbol_data[0]
        risk = latest.get('fiat_risk', 0)
        price = latest.get('price', 0)
        
        # Risk assessment based on Benjamin Cowen's methodology
        if risk < 0.2:
            assessment = "Very Low Risk - Strong Accumulation Zone"
            recommendation = f"Aggressively accumulate {symbol} at current levels"
            confidence = 0.90
        elif risk < 0.4:
            assessment = "Low Risk - Favorable Entry Zone"
            recommendation = f"Continue accumulating {symbol} with DCA strategy"
            confidence = 0.85
        elif risk < 0.6:
            assessment = "Moderate Risk - Fair Value Zone"
            recommendation = f"Hold {symbol} positions, avoid major additions"
            confidence = 0.75
        elif risk < 0.8:
            assessment = "High Risk - Distribution Zone"
            recommendation = f"Consider taking profits on {symbol}"
            confidence = 0.80
        else:
            assessment = "Very High Risk - Extreme Caution"
            recommendation = f"Strongly consider exiting {symbol} positions"
            confidence = 0.85
        
        return {
            "insight_type": "risk_assessment",
            "symbol": symbol,
            "title": f"{symbol} Risk Assessment: {assessment}",
            "description": f"{symbol} currently at ${price:.4f} with risk level of {risk:.1%}. Based on Benjamin Cowen's RiskMetric methodology, this indicates {assessment.lower()}.",
            "confidence_score": confidence,
            "data_sources": ["screener_data"],
            "recommendation": recommendation,
            "risk_level": latest.get('risk_level', 'Unknown'),
            "time_horizon": "medium"
        }
    
    async def _identify_high_potential_symbols(self, screener_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify symbols with high potential based on risk/reward"""
        if not screener_data:
            return {}
        
        # Look for symbols with low risk but reasonable market presence
        potential_symbols = []
        
        for item in screener_data:
            risk = item.get('fiat_risk', 1)
            price = item.get('price', 0)
            symbol = item.get('symbol', '')
            
            # Criteria: Low risk (< 0.4) and reasonable price action
            if risk < 0.4 and price > 0 and symbol:
                potential_symbols.append({
                    'symbol': symbol,
                    'risk': risk,
                    'price': price,
                    'potential_score': (0.4 - risk) * 100  # Higher score for lower risk
                })
        
        if not potential_symbols:
            return {
                "insight_type": "opportunity",
                "symbol": None,
                "title": "Limited High-Potential Opportunities",
                "description": "Current market conditions show few assets with attractive risk/reward profiles.",
                "confidence_score": 0.70,
                "data_sources": ["screener_data"],
                "recommendation": "Wait for better market conditions or focus on BTC/ETH",
                "risk_level": "High",
                "time_horizon": "short"
            }
        
        # Sort by potential score
        potential_symbols.sort(key=lambda x: x['potential_score'], reverse=True)
        top_3 = potential_symbols[:3]
        
        symbols_list = ", ".join([item['symbol'] for item in top_3])
        avg_risk = statistics.mean([item['risk'] for item in top_3])
        
        return {
            "insight_type": "opportunity",
            "symbol": None,
            "title": f"High-Potential Assets Identified: {symbols_list}",
            "description": f"Found {len(potential_symbols)} assets with attractive risk/reward profiles. Top candidates: {symbols_list} with average risk of {avg_risk:.1%}.",
            "confidence_score": 0.80,
            "data_sources": ["screener_data"],
            "recommendation": f"Consider building positions in {symbols_list}",
            "risk_level": "Low",
            "time_horizon": "long"
        }
    
    async def _identify_timing_opportunities(self, risk_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify market timing opportunities"""
        if not risk_data:
            return {}
        
        latest = risk_data[0]
        summary_risk = latest.get('summary_risk', 0)
        
        # Market timing based on overall risk levels
        if summary_risk < 0.25:
            timing = "Excellent Entry Opportunity"
            description = f"Market risk at {summary_risk:.1%} represents an excellent entry opportunity. Historical data suggests strong potential for positive returns from these levels."
            recommendation = "Increase crypto allocation significantly"
            confidence = 0.90
        elif summary_risk < 0.4:
            timing = "Good Entry Opportunity"
            description = f"Market risk at {summary_risk:.1%} suggests good entry conditions. Risk/reward is favorable for new positions."
            recommendation = "Consider increasing crypto exposure"
            confidence = 0.80
        elif summary_risk < 0.6:
            timing = "Neutral Market Conditions"
            description = f"Market risk at {summary_risk:.1%} indicates neutral conditions. Neither strong buying nor selling pressure evident."
            recommendation = "Maintain current allocation, use DCA strategies"
            confidence = 0.70
        elif summary_risk < 0.8:
            timing = "Caution - Distribution Zone"
            description = f"Market risk at {summary_risk:.1%} suggests caution. Historical patterns indicate potential for volatility and corrections."
            recommendation = "Consider reducing exposure and taking profits"
            confidence = 0.80
        else:
            timing = "High Risk - Exit Opportunity"
            description = f"Market risk at {summary_risk:.1%} indicates extreme levels. Strong potential for significant corrections based on historical patterns."
            recommendation = "Strongly consider reducing crypto exposure"
            confidence = 0.85
        
        return {
            "insight_type": "opportunity",
            "symbol": None,
            "title": f"Market Timing: {timing}",
            "description": description,
            "confidence_score": confidence,
            "data_sources": ["crypto_risk_indicators"],
            "recommendation": recommendation,
            "risk_level": "High" if summary_risk > 0.6 else "Moderate" if summary_risk > 0.4 else "Low",
            "time_horizon": "short"
        }