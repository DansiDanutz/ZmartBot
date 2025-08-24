"""
Scoring Engine - Advanced scoring algorithms and calculations
"""

import logging
import json
import hashlib
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import uuid
import random
import math

from sqlalchemy import desc, asc
from src.models.user import db
from src.models.symbol_models import (
    Symbol, SymbolScore, ScoringAlgorithm
)

logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Advanced scoring engine for symbol evaluation and ranking.
    Implements multiple scoring algorithms and composite scoring.
    """
    
    def __init__(self):
        self.algorithms = {}
        self._load_algorithms()
    
    def _load_algorithms(self):
        """Load active scoring algorithms from database"""
        try:
            from flask import current_app
            if current_app:
                algorithms = ScoringAlgorithm.query.filter_by(is_active=True).all()
                for algorithm in algorithms:
                    self.algorithms[algorithm.algorithm_name] = algorithm
        except Exception as e:
            logger.error(f"Error loading algorithms: {e}")
    
    def calculate_all_scores(self, symbol_id: str = None) -> Dict[str, Any]:
        """
        Calculate scores for all symbols or a specific symbol using all active algorithms.
        
        Args:
            symbol_id: Optional UUID of specific symbol to score
            
        Returns:
            Dictionary with calculation results
        """
        try:
            # Get symbols to score
            if symbol_id:
                symbols = Symbol.query.filter_by(
                    id=uuid.UUID(symbol_id),
                    is_eligible_for_management=True,
                    status='Active'
                ).all()
            else:
                symbols = Symbol.query.filter_by(
                    is_eligible_for_management=True,
                    status='Active'
                ).all()
            
            if not symbols:
                return {'error': 'No eligible symbols found'}
            
            results = {
                'symbols_processed': len(symbols),
                'algorithms_used': list(self.algorithms.keys()),
                'scores_calculated': 0,
                'errors': [],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            for symbol in symbols:
                try:
                    symbol_results = self._calculate_symbol_scores(symbol)
                    results['scores_calculated'] += len(symbol_results)
                except Exception as e:
                    error_msg = f"Error scoring symbol {symbol.symbol}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Calculate composite scores
            self._calculate_composite_scores(symbols)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in calculate_all_scores: {e}")
            return {'error': str(e)}
    
    def _calculate_symbol_scores(self, symbol: Symbol) -> List[Dict[str, Any]]:
        """Calculate scores for a single symbol using all algorithms"""
        results = []
        
        for algorithm_name, algorithm in self.algorithms.items():
            try:
                if algorithm.algorithm_type == 'COMPOSITE':
                    continue  # Composite scores calculated separately
                
                score_data = self._execute_algorithm(symbol, algorithm)
                
                if score_data:
                    # Save score to database
                    score_record = SymbolScore(
                        symbol_id=symbol.id,
                        algorithm_id=algorithm.id,
                        score_value=score_data['score_value'],
                        confidence_level=score_data['confidence_level'],
                        technical_component=score_data.get('technical_component'),
                        fundamental_component=score_data.get('fundamental_component'),
                        market_structure_component=score_data.get('market_structure_component'),
                        risk_component=score_data.get('risk_component'),
                        data_freshness_score=score_data.get('data_freshness_score'),
                        calculation_duration_ms=score_data.get('calculation_duration_ms'),
                        input_data_hash=score_data.get('input_data_hash'),
                        supporting_data=json.dumps(score_data.get('supporting_data', {}))
                    )
                    
                    db.session.add(score_record)
                    results.append(score_data)
            
            except Exception as e:
                logger.error(f"Error calculating {algorithm_name} score for {symbol.symbol}: {e}")
        
        db.session.commit()
        return results
    
    def _execute_algorithm(self, symbol: Symbol, algorithm: ScoringAlgorithm) -> Optional[Dict[str, Any]]:
        """Execute a specific scoring algorithm for a symbol"""
        start_time = datetime.now()
        
        try:
            if algorithm.algorithm_type == 'TECHNICAL':
                score_data = self._calculate_technical_score(symbol, algorithm)
            elif algorithm.algorithm_type == 'FUNDAMENTAL':
                score_data = self._calculate_fundamental_score(symbol, algorithm)
            elif algorithm.algorithm_type == 'MARKET_STRUCTURE':
                score_data = self._calculate_market_structure_score(symbol, algorithm)
            elif algorithm.algorithm_type == 'RISK':
                score_data = self._calculate_risk_score(symbol, algorithm)
            else:
                logger.warning(f"Unknown algorithm type: {algorithm.algorithm_type}")
                return None
            
            # Add calculation metadata
            calculation_time = (datetime.now() - start_time).total_seconds() * 1000
            score_data['calculation_duration_ms'] = int(calculation_time)
            score_data['algorithm_name'] = algorithm.algorithm_name
            score_data['algorithm_version'] = algorithm.algorithm_version
            
            return score_data
            
        except Exception as e:
            logger.error(f"Error executing algorithm {algorithm.algorithm_name}: {e}")
            return None
    
    def _calculate_technical_score(self, symbol: Symbol, algorithm: ScoringAlgorithm) -> Dict[str, Any]:
        """Calculate technical analysis score"""
        # Simulated technical analysis - in production, this would use real market data
        
        # Mock technical indicators
        rsi = random.uniform(20, 80)
        macd_signal = random.choice(['bullish', 'bearish', 'neutral'])
        bollinger_position = random.uniform(0, 1)  # 0 = lower band, 1 = upper band
        volume_trend = random.uniform(0.5, 2.0)  # Volume multiplier
        
        # Calculate component scores
        rsi_score = self._normalize_rsi_score(rsi)
        macd_score = {'bullish': 0.8, 'bearish': 0.2, 'neutral': 0.5}[macd_signal]
        bollinger_score = abs(0.5 - bollinger_position) * 2  # Distance from middle
        volume_score = min(volume_trend, 2.0) / 2.0
        
        # Weighted composite
        weights = algorithm.parameters_dict.get('weights', {
            'rsi': 0.3, 'macd': 0.3, 'bollinger': 0.2, 'volume': 0.2
        })
        
        technical_score = (
            rsi_score * weights.get('rsi', 0.3) +
            macd_score * weights.get('macd', 0.3) +
            bollinger_score * weights.get('bollinger', 0.2) +
            volume_score * weights.get('volume', 0.2)
        )
        
        # Add some randomness for confidence
        confidence = random.uniform(0.6, 0.9)
        
        return {
            'score_value': Decimal(str(round(technical_score, 4))),
            'confidence_level': Decimal(str(round(confidence, 4))),
            'technical_component': Decimal(str(round(technical_score, 4))),
            'data_freshness_score': Decimal('0.9'),
            'supporting_data': {
                'rsi': rsi,
                'macd_signal': macd_signal,
                'bollinger_position': bollinger_position,
                'volume_trend': volume_trend,
                'component_scores': {
                    'rsi_score': rsi_score,
                    'macd_score': macd_score,
                    'bollinger_score': bollinger_score,
                    'volume_score': volume_score
                }
            },
            'input_data_hash': self._generate_data_hash(symbol.symbol, 'technical')
        }
    
    def _calculate_fundamental_score(self, symbol: Symbol, algorithm: ScoringAlgorithm) -> Dict[str, Any]:
        """Calculate fundamental analysis score"""
        # Simulated fundamental analysis
        
        # Mock fundamental metrics
        volume_growth = random.uniform(-0.3, 0.5)  # -30% to +50%
        open_interest_change = random.uniform(-0.2, 0.3)
        funding_rate_stability = random.uniform(0.3, 1.0)
        market_cap_tier = random.choice(['large', 'medium', 'small'])
        
        # Calculate component scores
        volume_score = max(0, min(1, (volume_growth + 0.3) / 0.8))
        oi_score = max(0, min(1, (open_interest_change + 0.2) / 0.5))
        funding_score = funding_rate_stability
        
        # Market cap tier scoring
        cap_scores = {'large': 0.8, 'medium': 0.6, 'small': 0.4}
        cap_score = cap_scores[market_cap_tier]
        
        # Weighted composite
        weights = algorithm.parameters_dict.get('weights', {
            'volume': 0.4, 'open_interest': 0.3, 'funding': 0.2, 'market_cap': 0.1
        })
        
        fundamental_score = (
            volume_score * weights.get('volume', 0.4) +
            oi_score * weights.get('open_interest', 0.3) +
            funding_score * weights.get('funding', 0.2) +
            cap_score * weights.get('market_cap', 0.1)
        )
        
        confidence = random.uniform(0.5, 0.8)
        
        return {
            'score_value': Decimal(str(round(fundamental_score, 4))),
            'confidence_level': Decimal(str(round(confidence, 4))),
            'fundamental_component': Decimal(str(round(fundamental_score, 4))),
            'data_freshness_score': Decimal('0.8'),
            'supporting_data': {
                'volume_growth': volume_growth,
                'open_interest_change': open_interest_change,
                'funding_rate_stability': funding_rate_stability,
                'market_cap_tier': market_cap_tier,
                'component_scores': {
                    'volume_score': volume_score,
                    'oi_score': oi_score,
                    'funding_score': funding_score,
                    'cap_score': cap_score
                }
            },
            'input_data_hash': self._generate_data_hash(symbol.symbol, 'fundamental')
        }
    
    def _calculate_market_structure_score(self, symbol: Symbol, algorithm: ScoringAlgorithm) -> Dict[str, Any]:
        """Calculate market structure score"""
        # Simulated market structure analysis
        
        # Mock market structure metrics
        spread_bps = random.uniform(1, 20)  # 1-20 basis points
        depth_usd = random.uniform(50000, 500000)  # $50k - $500k depth
        market_impact = random.uniform(0.001, 0.01)  # 0.1% - 1% impact
        efficiency_score = random.uniform(0.6, 0.95)
        
        # Calculate component scores (lower spread/impact = higher score)
        spread_score = max(0, min(1, (20 - spread_bps) / 19))
        depth_score = min(1, depth_usd / 200000)  # Normalize to $200k
        impact_score = max(0, min(1, (0.01 - market_impact) / 0.009))
        
        # Weighted composite
        weights = algorithm.parameters_dict.get('weights', {
            'spread': 0.3, 'depth': 0.3, 'impact': 0.2, 'efficiency': 0.2
        })
        
        market_structure_score = (
            spread_score * weights.get('spread', 0.3) +
            depth_score * weights.get('depth', 0.3) +
            impact_score * weights.get('impact', 0.2) +
            efficiency_score * weights.get('efficiency', 0.2)
        )
        
        confidence = random.uniform(0.7, 0.9)
        
        return {
            'score_value': Decimal(str(round(market_structure_score, 4))),
            'confidence_level': Decimal(str(round(confidence, 4))),
            'market_structure_component': Decimal(str(round(market_structure_score, 4))),
            'data_freshness_score': Decimal('0.95'),
            'supporting_data': {
                'spread_bps': spread_bps,
                'depth_usd': depth_usd,
                'market_impact': market_impact,
                'efficiency_score': efficiency_score,
                'component_scores': {
                    'spread_score': spread_score,
                    'depth_score': depth_score,
                    'impact_score': impact_score
                }
            },
            'input_data_hash': self._generate_data_hash(symbol.symbol, 'market_structure')
        }
    
    def _calculate_risk_score(self, symbol: Symbol, algorithm: ScoringAlgorithm) -> Dict[str, Any]:
        """Calculate risk assessment score"""
        # Simulated risk analysis
        
        # Mock risk metrics
        volatility = random.uniform(0.2, 1.5)  # 20% - 150% annualized
        max_drawdown = random.uniform(0.1, 0.6)  # 10% - 60%
        correlation_risk = random.uniform(0.2, 0.8)  # Portfolio correlation
        liquidity_risk = random.uniform(0.1, 0.5)  # Liquidity risk score
        
        # Calculate component scores (lower risk = higher score)
        vol_score = max(0, min(1, (1.5 - volatility) / 1.3))
        drawdown_score = max(0, min(1, (0.6 - max_drawdown) / 0.5))
        correlation_score = max(0, min(1, (0.8 - correlation_risk) / 0.6))
        liquidity_score = max(0, min(1, (0.5 - liquidity_risk) / 0.4))
        
        # Weighted composite
        weights = algorithm.parameters_dict.get('weights', {
            'volatility': 0.3, 'drawdown': 0.3, 'correlation': 0.2, 'liquidity': 0.2
        })
        
        risk_score = (
            vol_score * weights.get('volatility', 0.3) +
            drawdown_score * weights.get('drawdown', 0.3) +
            correlation_score * weights.get('correlation', 0.2) +
            liquidity_score * weights.get('liquidity', 0.2)
        )
        
        confidence = random.uniform(0.6, 0.85)
        
        return {
            'score_value': Decimal(str(round(risk_score, 4))),
            'confidence_level': Decimal(str(round(confidence, 4))),
            'risk_component': Decimal(str(round(risk_score, 4))),
            'data_freshness_score': Decimal('0.85'),
            'supporting_data': {
                'volatility': volatility,
                'max_drawdown': max_drawdown,
                'correlation_risk': correlation_risk,
                'liquidity_risk': liquidity_risk,
                'component_scores': {
                    'vol_score': vol_score,
                    'drawdown_score': drawdown_score,
                    'correlation_score': correlation_score,
                    'liquidity_score': liquidity_score
                }
            },
            'input_data_hash': self._generate_data_hash(symbol.symbol, 'risk')
        }
    
    def _calculate_composite_scores(self, symbols: List[Symbol]):
        """Calculate composite scores from component scores"""
        try:
            composite_algorithm = ScoringAlgorithm.query.filter_by(
                algorithm_type='COMPOSITE',
                is_active=True
            ).first()
            
            if not composite_algorithm:
                logger.warning("No active composite algorithm found")
                return
            
            for symbol in symbols:
                # Get latest component scores
                component_scores = self._get_latest_component_scores(symbol.id)
                
                if not component_scores:
                    continue
                
                # Calculate weighted composite
                composite_score = self._calculate_weighted_composite(
                    component_scores, 
                    composite_algorithm.parameters_dict
                )
                
                if composite_score:
                    # Save composite score
                    score_record = SymbolScore(
                        symbol_id=symbol.id,
                        algorithm_id=composite_algorithm.id,
                        score_value=composite_score['score_value'],
                        confidence_level=composite_score['confidence_level'],
                        technical_component=composite_score.get('technical_component'),
                        fundamental_component=composite_score.get('fundamental_component'),
                        market_structure_component=composite_score.get('market_structure_component'),
                        risk_component=composite_score.get('risk_component'),
                        data_freshness_score=composite_score.get('data_freshness_score'),
                        supporting_data=json.dumps(composite_score.get('supporting_data', {}))
                    )
                    
                    db.session.add(score_record)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error calculating composite scores: {e}")
            db.session.rollback()
    
    def _get_latest_component_scores(self, symbol_id: uuid.UUID) -> Dict[str, Any]:
        """Get latest component scores for a symbol"""
        try:
            # Get scores from last hour
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            scores = (
                SymbolScore.query
                .join(ScoringAlgorithm)
                .filter(
                    SymbolScore.symbol_id == symbol_id,
                    SymbolScore.calculation_timestamp >= cutoff_time,
                    ScoringAlgorithm.algorithm_type != 'COMPOSITE'
                )
                .order_by(desc(SymbolScore.calculation_timestamp))
                .all()
            )
            
            # Group by algorithm type and get latest
            component_scores = {}
            for score in scores:
                algo_type = score.algorithm.algorithm_type
                if algo_type not in component_scores:
                    component_scores[algo_type] = {
                        'score_value': score.score_value,
                        'confidence_level': score.confidence_level,
                        'algorithm_name': score.algorithm.algorithm_name,
                        'weight': score.algorithm.weight_in_composite
                    }
            
            return component_scores
            
        except Exception as e:
            logger.error(f"Error getting component scores: {e}")
            return {}
    
    def _calculate_weighted_composite(self, component_scores: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate weighted composite score from components"""
        try:
            if not component_scores:
                return None
            
            # Default weights
            default_weights = {
                'TECHNICAL': 0.25,
                'FUNDAMENTAL': 0.25,
                'MARKET_STRUCTURE': 0.25,
                'RISK': 0.25
            }
            
            weights = parameters.get('weights', default_weights)
            
            total_score = Decimal('0')
            total_weight = Decimal('0')
            total_confidence = Decimal('0')
            
            components = {}
            
            for algo_type, score_data in component_scores.items():
                weight = Decimal(str(weights.get(algo_type, 0)))
                score = score_data['score_value']
                confidence = score_data['confidence_level']
                
                if weight > 0:
                    weighted_score = score * weight
                    total_score += weighted_score
                    total_weight += weight
                    total_confidence += confidence * weight
                    
                    components[f"{algo_type.lower()}_component"] = score
            
            if total_weight == 0:
                return None
            
            # Normalize
            final_score = total_score / total_weight
            final_confidence = total_confidence / total_weight
            
            return {
                'score_value': final_score,
                'confidence_level': final_confidence,
                'data_freshness_score': Decimal('0.9'),
                'supporting_data': {
                    'component_scores': component_scores,
                    'weights_used': weights,
                    'total_weight': float(total_weight)
                },
                **components
            }
            
        except Exception as e:
            logger.error(f"Error calculating weighted composite: {e}")
            return None
    
    def _normalize_rsi_score(self, rsi: float) -> float:
        """Normalize RSI to 0-1 score (50 = neutral, extremes are better)"""
        if rsi <= 30:
            return 0.8 + (30 - rsi) / 30 * 0.2  # Oversold is good
        elif rsi >= 70:
            return 0.8 + (rsi - 70) / 30 * 0.2  # Overbought is good
        else:
            return 0.3 + (1 - abs(rsi - 50) / 20) * 0.5  # Closer to 50 is neutral
    
    def _generate_data_hash(self, symbol: str, algorithm_type: str) -> str:
        """Generate hash for input data tracking"""
        data_string = f"{symbol}_{algorithm_type}_{datetime.now().strftime('%Y%m%d%H')}"
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def get_symbol_rankings(self, algorithm_type: str = 'COMPOSITE', limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get symbol rankings based on specified algorithm.
        
        Args:
            algorithm_type: Type of algorithm to rank by
            limit: Maximum number of symbols to return
            
        Returns:
            List of symbols ranked by score
        """
        try:
            algorithm = ScoringAlgorithm.query.filter_by(
                algorithm_type=algorithm_type,
                is_active=True
            ).first()
            
            if not algorithm:
                return []
            
            # Get latest scores
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=2)
            
            scores = (
                db.session.query(SymbolScore, Symbol)
                .join(Symbol)
                .filter(
                    SymbolScore.algorithm_id == algorithm.id,
                    SymbolScore.calculation_timestamp >= cutoff_time,
                    Symbol.is_eligible_for_management == True,
                    Symbol.status == 'Active'
                )
                .order_by(desc(SymbolScore.score_value))
                .limit(limit)
                .all()
            )
            
            rankings = []
            for i, (score, symbol) in enumerate(scores):
                rankings.append({
                    'rank': i + 1,
                    'symbol_id': str(symbol.id),
                    'symbol': symbol.symbol,
                    'score': float(score.score_value),
                    'confidence': float(score.confidence_level),
                    'algorithm': algorithm.algorithm_name,
                    'calculation_time': score.calculation_timestamp.isoformat(),
                    'symbol_details': symbol.to_dict()
                })
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error getting symbol rankings: {e}")
            return []

