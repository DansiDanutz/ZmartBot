#!/usr/bin/env python3
"""
AI Explainability Service
Provides insights into trading decisions, signal confidence, and risk assessments
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class RiskLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class SignalExplanation:
    """Explanation for a trading signal"""
    signal_id: str
    symbol: str
    direction: str  # 'BUY' or 'SELL'
    confidence: float
    confidence_level: ConfidenceLevel
    factors: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    recommendation: str
    timestamp: datetime
    explanation_text: str

@dataclass
class RiskExplanation:
    """Explanation for risk assessment"""
    symbol: str
    risk_score: float
    risk_level: RiskLevel
    factors: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    timestamp: datetime
    explanation_text: str

@dataclass
class PortfolioExplanation:
    """Explanation for portfolio decisions"""
    portfolio_id: str
    total_value: float
    risk_score: float
    diversification_score: float
    recommendations: List[Dict[str, Any]]
    timestamp: datetime
    explanation_text: str

class ExplainabilityService:
    """AI-powered explainability service for trading decisions"""
    
    def __init__(self):
        self.confidence_thresholds = {
            ConfidenceLevel.VERY_LOW: 0.0,
            ConfidenceLevel.LOW: 0.2,
            ConfidenceLevel.MEDIUM: 0.4,
            ConfidenceLevel.HIGH: 0.7,
            ConfidenceLevel.VERY_HIGH: 0.9
        }
        
        self.risk_thresholds = {
            RiskLevel.VERY_LOW: 0.0,
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.4,
            RiskLevel.HIGH: 0.7,
            RiskLevel.VERY_HIGH: 0.9
        }
    
    def explain_signal(self, signal_data: Dict[str, Any]) -> SignalExplanation:
        """Generate explanation for a trading signal"""
        try:
            symbol = signal_data.get('symbol', 'UNKNOWN')
            direction = signal_data.get('direction', 'HOLD')
            confidence = signal_data.get('confidence', 0.0)
            
            # Determine confidence level
            confidence_level = self._get_confidence_level(confidence)
            
            # Analyze contributing factors
            factors = self._analyze_signal_factors(signal_data)
            
            # Assess risk
            risk_assessment = self._assess_signal_risk(signal_data)
            
            # Generate recommendation
            recommendation = self._generate_signal_recommendation(
                direction, confidence, risk_assessment
            )
            
            # Create explanation text
            explanation_text = self._generate_signal_explanation(
                symbol, direction, confidence, factors, risk_assessment
            )
            
            return SignalExplanation(
                signal_id=signal_data.get('id', 'unknown'),
                symbol=symbol,
                direction=direction,
                confidence=confidence,
                confidence_level=confidence_level,
                factors=factors,
                risk_assessment=risk_assessment,
                recommendation=recommendation,
                timestamp=datetime.utcnow(),
                explanation_text=explanation_text
            )
            
        except Exception as e:
            logger.error(f"Error explaining signal: {e}")
            return self._create_default_signal_explanation(signal_data)
    
    def explain_risk(self, risk_data: Dict[str, Any]) -> RiskExplanation:
        """Generate explanation for risk assessment"""
        try:
            symbol = risk_data.get('symbol', 'UNKNOWN')
            risk_score = risk_data.get('risk_score', 0.0)
            
            # Determine risk level
            risk_level = self._get_risk_level(risk_score)
            
            # Analyze risk factors
            factors = self._analyze_risk_factors(risk_data)
            
            # Generate mitigation strategies
            mitigation_strategies = self._generate_mitigation_strategies(
                risk_level, factors
            )
            
            # Create explanation text
            explanation_text = self._generate_risk_explanation(
                symbol, risk_score, factors, mitigation_strategies
            )
            
            return RiskExplanation(
                symbol=symbol,
                risk_score=risk_score,
                risk_level=risk_level,
                factors=factors,
                mitigation_strategies=mitigation_strategies,
                timestamp=datetime.utcnow(),
                explanation_text=explanation_text
            )
            
        except Exception as e:
            logger.error(f"Error explaining risk: {e}")
            return self._create_default_risk_explanation(risk_data)
    
    def explain_portfolio(self, portfolio_data: Dict[str, Any]) -> PortfolioExplanation:
        """Generate explanation for portfolio decisions"""
        try:
            portfolio_id = portfolio_data.get('id', 'unknown')
            total_value = portfolio_data.get('total_value', 0.0)
            risk_score = portfolio_data.get('risk_score', 0.0)
            diversification_score = portfolio_data.get('diversification_score', 0.0)
            
            # Generate recommendations
            recommendations = self._generate_portfolio_recommendations(
                portfolio_data
            )
            
            # Create explanation text
            explanation_text = self._generate_portfolio_explanation(
                total_value, risk_score, diversification_score, recommendations
            )
            
            return PortfolioExplanation(
                portfolio_id=portfolio_id,
                total_value=total_value,
                risk_score=risk_score,
                diversification_score=diversification_score,
                recommendations=recommendations,
                timestamp=datetime.utcnow(),
                explanation_text=explanation_text
            )
            
        except Exception as e:
            logger.error(f"Error explaining portfolio: {e}")
            return self._create_default_portfolio_explanation(portfolio_data)
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level based on score"""
        for level, threshold in self.confidence_thresholds.items():
            if confidence >= threshold:
                continue
            else:
                return level
        return ConfidenceLevel.VERY_HIGH
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        for level, threshold in self.risk_thresholds.items():
            if risk_score >= threshold:
                continue
            else:
                return level
        return RiskLevel.VERY_HIGH
    
    def _analyze_signal_factors(self, signal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze factors contributing to the signal"""
        factors = []
        
        # KingFisher analysis
        if 'kingfisher_score' in signal_data:
            score = signal_data['kingfisher_score']
            factors.append({
                'name': 'KingFisher Liquidation Analysis',
                'value': score,
                'weight': 0.30,
                'contribution': score * 0.30,
                'description': f'Liquidation cluster analysis indicates {"strong" if score > 0.7 else "moderate" if score > 0.4 else "weak"} signal strength'
            })
        
        # RiskMetric analysis
        if 'riskmetric_score' in signal_data:
            score = signal_data['riskmetric_score']
            factors.append({
                'name': 'RiskMetric Scoring',
                'value': score,
                'weight': 0.20,
                'contribution': score * 0.20,
                'description': f'Risk assessment shows {"favorable" if score > 0.6 else "moderate" if score > 0.4 else "unfavorable"} conditions'
            })
        
        # Cryptometer analysis
        if 'cryptometer_score' in signal_data:
            score = signal_data['cryptometer_score']
            factors.append({
                'name': 'Cryptometer API Data',
                'value': score,
                'weight': 0.50,
                'contribution': score * 0.50,
                'description': f'Market data analysis indicates {"strong" if score > 0.8 else "moderate" if score > 0.5 else "weak"} market sentiment'
            })
        
        return factors
    
    def _assess_signal_risk(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for a trading signal"""
        risk_factors = []
        total_risk = 0.0
        
        # Volatility risk
        volatility = signal_data.get('volatility', 0.0)
        if volatility > 0.8:
            risk_factors.append('High volatility detected')
            total_risk += 0.3
        elif volatility > 0.5:
            risk_factors.append('Moderate volatility')
            total_risk += 0.15
        
        # Liquidity risk
        liquidity = signal_data.get('liquidity', 0.0)
        if liquidity < 0.3:
            risk_factors.append('Low liquidity')
            total_risk += 0.25
        elif liquidity < 0.6:
            risk_factors.append('Moderate liquidity')
            total_risk += 0.1
        
        # Market correlation risk
        correlation = signal_data.get('market_correlation', 0.0)
        if abs(correlation) > 0.8:
            risk_factors.append('High market correlation')
            total_risk += 0.2
        
        # Position size risk
        position_size = signal_data.get('position_size', 0.0)
        if position_size > 0.1:  # More than 10% of portfolio
            risk_factors.append('Large position size')
            total_risk += 0.25
        
        return {
            'total_risk': min(total_risk, 1.0),
            'risk_factors': risk_factors,
            'risk_level': self._get_risk_level(total_risk).value
        }
    
    def _generate_signal_recommendation(self, direction: str, confidence: float, 
                                      risk_assessment: Dict[str, Any]) -> str:
        """Generate trading recommendation"""
        risk_level = risk_assessment.get('risk_level', 'medium')
        total_risk = risk_assessment.get('total_risk', 0.5)
        
        if confidence < 0.4:
            return "HOLD - Low confidence signal"
        elif total_risk > 0.7:
            return f"HOLD - High risk ({risk_level})"
        elif confidence > 0.7 and total_risk < 0.5:
            return f"{direction} - Strong signal with manageable risk"
        elif confidence > 0.5:
            return f"{direction} - Moderate confidence, consider position sizing"
        else:
            return "HOLD - Insufficient signal strength"
    
    def _generate_signal_explanation(self, symbol: str, direction: str, confidence: float,
                                   factors: List[Dict[str, Any]], risk_assessment: Dict[str, Any]) -> str:
        """Generate human-readable explanation for signal"""
        confidence_text = "very strong" if confidence > 0.8 else "strong" if confidence > 0.6 else "moderate" if confidence > 0.4 else "weak"
        risk_text = "high" if risk_assessment['total_risk'] > 0.7 else "moderate" if risk_assessment['total_risk'] > 0.4 else "low"
        
        explanation = f"Signal Analysis for {symbol}:\n\n"
        explanation += f"Direction: {direction}\n"
        explanation += f"Confidence: {confidence_text} ({confidence:.1%})\n"
        explanation += f"Risk Level: {risk_text}\n\n"
        
        explanation += "Contributing Factors:\n"
        for factor in factors:
            explanation += f"• {factor['name']}: {factor['description']}\n"
        
        if risk_assessment['risk_factors']:
            explanation += f"\nRisk Factors:\n"
            for risk in risk_assessment['risk_factors']:
                explanation += f"• {risk}\n"
        
        return explanation
    
    def _analyze_risk_factors(self, risk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze risk factors"""
        factors = []
        
        # Volatility analysis
        volatility = risk_data.get('volatility', 0.0)
        factors.append({
            'name': 'Price Volatility',
            'value': volatility,
            'impact': 'high' if volatility > 0.8 else 'moderate' if volatility > 0.5 else 'low',
            'description': f'{"High" if volatility > 0.8 else "Moderate" if volatility > 0.5 else "Low"} price volatility detected'
        })
        
        # Liquidity analysis
        liquidity = risk_data.get('liquidity', 0.0)
        factors.append({
            'name': 'Market Liquidity',
            'value': liquidity,
            'impact': 'low' if liquidity < 0.3 else 'moderate' if liquidity < 0.6 else 'high',
            'description': f'{"Low" if liquidity < 0.3 else "Moderate" if liquidity < 0.6 else "High"} market liquidity'
        })
        
        # Correlation analysis
        correlation = risk_data.get('market_correlation', 0.0)
        factors.append({
            'name': 'Market Correlation',
            'value': abs(correlation),
            'impact': 'high' if abs(correlation) > 0.8 else 'moderate' if abs(correlation) > 0.5 else 'low',
            'description': f'{"High" if abs(correlation) > 0.8 else "Moderate" if abs(correlation) > 0.5 else "Low"} correlation with market'
        })
        
        return factors
    
    def _generate_mitigation_strategies(self, risk_level: RiskLevel, 
                                      factors: List[Dict[str, Any]]) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            strategies.append("Reduce position size to minimize exposure")
            strategies.append("Set tighter stop-loss orders")
            strategies.append("Consider hedging strategies")
        
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            strategies.append("Diversify across multiple assets")
            strategies.append("Monitor position closely")
        
        # Add specific strategies based on factors
        for factor in factors:
            if factor['name'] == 'Price Volatility' and factor['impact'] == 'high':
                strategies.append("Use options for volatility protection")
            elif factor['name'] == 'Market Liquidity' and factor['impact'] == 'low':
                strategies.append("Trade in smaller increments")
            elif factor['name'] == 'Market Correlation' and factor['impact'] == 'high':
                strategies.append("Consider uncorrelated assets")
        
        return strategies
    
    def _generate_risk_explanation(self, symbol: str, risk_score: float,
                                  factors: List[Dict[str, Any]], 
                                  mitigation_strategies: List[str]) -> str:
        """Generate human-readable risk explanation"""
        risk_text = "very high" if risk_score > 0.8 else "high" if risk_score > 0.6 else "moderate" if risk_score > 0.4 else "low"
        
        explanation = f"Risk Assessment for {symbol}:\n\n"
        explanation += f"Overall Risk: {risk_text} ({risk_score:.1%})\n\n"
        
        explanation += "Risk Factors:\n"
        for factor in factors:
            explanation += f"• {factor['name']}: {factor['description']}\n"
        
        if mitigation_strategies:
            explanation += f"\nMitigation Strategies:\n"
            for strategy in mitigation_strategies:
                explanation += f"• {strategy}\n"
        
        return explanation
    
    def _generate_portfolio_recommendations(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Diversification recommendations
        diversification = portfolio_data.get('diversification_score', 0.0)
        if diversification < 0.5:
            recommendations.append({
                'type': 'diversification',
                'priority': 'high',
                'description': 'Add more diverse assets to reduce concentration risk',
                'action': 'Consider adding uncorrelated assets'
            })
        
        # Risk management recommendations
        risk_score = portfolio_data.get('risk_score', 0.0)
        if risk_score > 0.7:
            recommendations.append({
                'type': 'risk_management',
                'priority': 'high',
                'description': 'Portfolio risk is elevated',
                'action': 'Consider reducing position sizes or adding hedges'
            })
        
        # Rebalancing recommendations
        rebalance_needed = portfolio_data.get('rebalance_needed', False)
        if rebalance_needed:
            recommendations.append({
                'type': 'rebalancing',
                'priority': 'medium',
                'description': 'Portfolio allocation has drifted from targets',
                'action': 'Rebalance to target allocations'
            })
        
        return recommendations
    
    def _generate_portfolio_explanation(self, total_value: float, risk_score: float,
                                      diversification_score: float,
                                      recommendations: List[Dict[str, Any]]) -> str:
        """Generate human-readable portfolio explanation"""
        explanation = f"Portfolio Analysis:\n\n"
        explanation += f"Total Value: ${total_value:,.2f}\n"
        explanation += f"Risk Score: {risk_score:.1%}\n"
        explanation += f"Diversification Score: {diversification_score:.1%}\n\n"
        
        if recommendations:
            explanation += "Recommendations:\n"
            for rec in recommendations:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                explanation += f"{priority_icon} {rec['description']}\n"
                explanation += f"   Action: {rec['action']}\n\n"
        
        return explanation
    
    def _create_default_signal_explanation(self, signal_data: Dict[str, Any]) -> SignalExplanation:
        """Create default signal explanation on error"""
        return SignalExplanation(
            signal_id=signal_data.get('id', 'unknown'),
            symbol=signal_data.get('symbol', 'UNKNOWN'),
            direction='HOLD',
            confidence=0.0,
            confidence_level=ConfidenceLevel.VERY_LOW,
            factors=[],
            risk_assessment={'total_risk': 1.0, 'risk_factors': ['Unable to analyze'], 'risk_level': 'very_high'},
            recommendation='HOLD - Unable to analyze signal',
            timestamp=datetime.utcnow(),
            explanation_text='Unable to generate signal explanation due to insufficient data.'
        )
    
    def _create_default_risk_explanation(self, risk_data: Dict[str, Any]) -> RiskExplanation:
        """Create default risk explanation on error"""
        return RiskExplanation(
            symbol=risk_data.get('symbol', 'UNKNOWN'),
            risk_score=1.0,
            risk_level=RiskLevel.VERY_HIGH,
            factors=[],
            mitigation_strategies=['Unable to analyze risk'],
            timestamp=datetime.utcnow(),
            explanation_text='Unable to generate risk explanation due to insufficient data.'
        )
    
    def _create_default_portfolio_explanation(self, portfolio_data: Dict[str, Any]) -> PortfolioExplanation:
        """Create default portfolio explanation on error"""
        return PortfolioExplanation(
            portfolio_id=portfolio_data.get('id', 'unknown'),
            total_value=0.0,
            risk_score=1.0,
            diversification_score=0.0,
            recommendations=[],
            timestamp=datetime.utcnow(),
            explanation_text='Unable to generate portfolio explanation due to insufficient data.'
        )

# Global service instance
_explainability_service: Optional[ExplainabilityService] = None

def get_explainability_service() -> ExplainabilityService:
    """Get or create explainability service instance"""
    global _explainability_service
    if _explainability_service is None:
        _explainability_service = ExplainabilityService()
    return _explainability_service 