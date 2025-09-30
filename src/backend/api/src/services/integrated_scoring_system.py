#!/usr/bin/env python3
"""
Integrated Scoring System - Dynamic Version
Unified scoring system with intelligent dynamic weighting
Combines KingFisher, Cryptometer, and RiskMetric 100-point scores
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .calibrated_scoring_service import CalibratedScoringService
from .unified_riskmetric import UnifiedRiskMetric as RiskMetricService

logger = logging.getLogger(__name__)

class IntegratedScoringSystem:
    """
    Integrated scoring system with dynamic weighting
    
    Features:
    - Dynamic weight calculation based on data quality
    - Market condition awareness
    - 100-point final scoring scale
    - Intelligent confidence assessment
    """
    
    def __init__(self):
        self.calibrated_scoring = CalibratedScoringService()
        self.riskmetric_service = RiskMetricService()
        # Dynamic agent import removed to avoid circular dependency
        self.dynamic_agent = None
        logger.info("Integrated Scoring System initialized")
    
    async def get_comprehensive_score(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive dynamic score using intelligent weighting
        
        Returns 100-point final score with dynamic weight analysis
        """
        try:
            # Initialize dynamic agent if needed
            if self.dynamic_agent is None:
                try:
                    from ..agents.scoring.dynamic_scoring_agent import DynamicScoringAgent
                    self.dynamic_agent = DynamicScoringAgent()
                except ImportError:
                    logger.warning("Dynamic scoring agent not available, using static weights")
            
            # Collect scores from all three systems
            kingfisher_score, kingfisher_metadata = await self._get_kingfisher_score(symbol)
            cryptometer_score, cryptometer_metadata = await self._get_cryptometer_score(symbol)
            riskmetric_score, riskmetric_metadata = await self._get_riskmetric_score(symbol)
            
            # If dynamic agent is available, use it
            if self.dynamic_agent:
                # Start the dynamic agent if not running
                if hasattr(self.dynamic_agent, 'status') and self.dynamic_agent.status != "running":
                    await self.dynamic_agent.start()
                
                # Calculate dynamic weighted score
                result = await self.dynamic_agent.calculate_dynamic_score(
                    symbol=symbol,
                    kingfisher_score=kingfisher_score,
                    cryptometer_score=cryptometer_score,
                    riskmetric_score=riskmetric_score,
                    kingfisher_metadata=kingfisher_metadata,
                    cryptometer_metadata=cryptometer_metadata,
                    riskmetric_metadata=riskmetric_metadata
                )
                
                # Format response with dynamic weights
                return {
                    'symbol': symbol,
                    'final_score': result.final_score,  # 0-100 scale
                    'signal': result.signal,
                    'confidence': result.overall_confidence,
                    'market_condition': result.market_condition.value if hasattr(result, 'market_condition') else 'normal',
                    'dynamic_weights': {
                        'kingfisher': result.dynamic_weights.kingfisher_weight,
                        'cryptometer': result.dynamic_weights.cryptometer_weight,
                        'riskmetric': result.dynamic_weights.riskmetric_weight,
                        'reasoning': result.dynamic_weights.reasoning,
                        'weight_confidence': result.dynamic_weights.confidence
                    },
                    'component_scores': {
                        'kingfisher': {
                            'score': result.kingfisher_data.score if result.kingfisher_data else None,
                            'confidence': result.kingfisher_data.confidence if result.kingfisher_data else None,
                            'data_quality': result.kingfisher_data.data_quality if result.kingfisher_data else None,
                            'data_age_minutes': result.kingfisher_data.data_age if result.kingfisher_data else None
                        },
                        'cryptometer': {
                            'score': result.cryptometer_data.score if result.cryptometer_data else None,
                            'confidence': result.cryptometer_data.confidence if result.cryptometer_data else None,
                            'data_quality': result.cryptometer_data.data_quality if result.cryptometer_data else None,
                            'data_age_minutes': result.cryptometer_data.data_age if result.cryptometer_data else None
                        },
                        'riskmetric': {
                            'score': result.riskmetric_data.score if result.riskmetric_data else None,
                            'confidence': result.riskmetric_data.confidence if result.riskmetric_data else None,
                            'data_quality': result.riskmetric_data.data_quality if result.riskmetric_data else None,
                            'data_age_minutes': result.riskmetric_data.data_age if result.riskmetric_data else None
                        }
                    },
                    'timestamp': result.timestamp.isoformat()
                }
            else:
                # Fallback to static weights
                static_weights = {
                    'kingfisher': 0.30,
                    'cryptometer': 0.50,
                    'riskmetric': 0.20
                }
                
                final_score = (
                    kingfisher_score * static_weights['kingfisher'] +
                    cryptometer_score * static_weights['cryptometer'] +
                    riskmetric_score * static_weights['riskmetric']
                )
                
                return {
                    'symbol': symbol,
                    'final_score': final_score,
                    'signal': self._get_signal_from_score(final_score),
                    'confidence': 0.7,  # Default confidence
                    'market_condition': 'normal',
                    'dynamic_weights': static_weights,
                    'component_scores': {
                        'kingfisher': {'score': kingfisher_score, 'metadata': kingfisher_metadata},
                        'cryptometer': {'score': cryptometer_score, 'metadata': cryptometer_metadata},
                        'riskmetric': {'score': riskmetric_score, 'metadata': riskmetric_metadata}
                    },
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive score for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'final_score': 50.0,
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _get_kingfisher_score(self, symbol: str) -> tuple:
        """Get KingFisher score (30% weight, 0-100 scale)"""
        try:
            # Use get_independent_scores to get KingFisher score
            if hasattr(self.calibrated_scoring, 'get_independent_scores'):
                scores = await self.calibrated_scoring.get_independent_scores(symbol)
                if scores and scores.kingfisher:
                    # The kingfisher score is in the ComponentScore object
                    return scores.kingfisher.score, {
                        'win_rate': scores.kingfisher.win_rate,
                        'direction': scores.kingfisher.direction,
                        'confidence': scores.kingfisher.confidence,
                        'patterns': scores.kingfisher.patterns,
                        'analysis_details': scores.kingfisher.analysis_details
                    }
            
            # Fallback to default score
            return 50.0, {'source': 'fallback', 'liquidation_risk': 'unknown'}
        except Exception as e:
            logger.error(f"Error getting KingFisher score: {str(e)}")
            return 50.0, {'error': str(e)}
    
    async def _get_cryptometer_score(self, symbol: str) -> tuple:
        """Get Cryptometer score (50% weight, 0-100 scale)"""
        try:
            # Use get_independent_scores which is the actual method
            if hasattr(self.calibrated_scoring, 'get_independent_scores'):
                scores = await self.calibrated_scoring.get_independent_scores(symbol)
                if scores and scores.cryptometer:
                    # The cryptometer score is in the ComponentScore object
                    return scores.cryptometer.score, {
                        'win_rate': scores.cryptometer.win_rate,
                        'direction': scores.cryptometer.direction,
                        'confidence': scores.cryptometer.confidence,
                        'patterns': scores.cryptometer.patterns,
                        'analysis_details': scores.cryptometer.analysis_details
                    }
            
            # Fallback to basic scoring
            return 50.0, {'error': 'No data available', 'source': 'fallback'}
        except Exception as e:
            logger.error(f"Error getting Cryptometer score: {str(e)}")
            return 50.0, {'error': str(e)}
    
    async def _get_riskmetric_score(self, symbol: str) -> tuple:
        """Get RiskMetric score (20% weight, 0-100 scale)"""
        try:
            # Try to get the risk data from riskmetric service
            if hasattr(self.riskmetric_service, 'assess_risk'):
                # Use assess_risk which returns RiskAssessment object
                assessment = await self.riskmetric_service.assess_risk(symbol)
                if assessment:
                    # The assessment has a score field (0-100)
                    return assessment.score, {
                        'risk_value': assessment.risk_value,
                        'risk_band': assessment.risk_band,
                        'risk_zone': assessment.risk_zone,
                        'coefficient': assessment.coefficient,
                        'signal': assessment.signal,
                        'tradeable': assessment.tradeable,
                        'win_rate': assessment.win_rate
                    }
            elif hasattr(self.riskmetric_service, 'get_scoring_component'):
                result = await self.riskmetric_service.get_scoring_component(symbol)
                if result and 'score' in result:
                    return result['score'], result
            
            # Fallback to basic scoring
            return 50.0, {'error': 'No data available', 'source': 'fallback'}
        except Exception as e:
            logger.error(f"Error getting RiskMetric score: {str(e)}")
            return 50.0, {'error': str(e)}
    
    def _get_signal_from_score(self, score: float) -> str:
        """Convert score to trading signal"""
        if score >= 80:
            return 'STRONG_BUY'
        elif score >= 65:
            return 'BUY'
        elif score >= 35:
            return 'NEUTRAL'
        elif score >= 20:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    async def get_scoring_health(self) -> Dict[str, Any]:
        """Get health status of the scoring system"""
        return {
            'status': 'healthy',
            'service': 'integrated_scoring_system',
            'components': {
                'calibrated_scoring': 'active',
                'riskmetric': 'active',
                'dynamic_agent': 'active' if self.dynamic_agent else 'inactive'
            },
            'timestamp': datetime.now().isoformat()
        }