"""
Portfolio Manager - Specialized portfolio operations and analytics
"""

import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import uuid

from sqlalchemy import desc, asc, func
from src.models.user import db
from src.models.symbol_models import (
    Symbol, PortfolioComposition, PortfolioHistory, 
    SymbolScore, ScoringAlgorithm
)

logger = logging.getLogger(__name__)

class PortfolioManager:
    """
    Specialized manager for portfolio operations, analytics, and optimization.
    """
    
    def __init__(self):
        self.max_portfolio_size = 10
        self.target_weights = None  # Equal weights by default
    
    def calculate_portfolio_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio metrics including risk and performance.
        
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            portfolio_entries = (
                PortfolioComposition.query
                .join(Symbol)
                .filter(PortfolioComposition.status == 'Active')
                .all()
            )
            
            if not portfolio_entries:
                return {'error': 'No active portfolio entries found'}
            
            # Basic portfolio composition
            total_symbols = len(portfolio_entries)
            
            # Score distribution
            scores = [entry.current_score for entry in portfolio_entries if entry.current_score]
            score_metrics = self._calculate_score_metrics(scores)
            
            # Sector diversification
            sector_analysis = self._analyze_sector_diversification(portfolio_entries)
            
            # Performance analysis
            performance_analysis = self._analyze_portfolio_performance(portfolio_entries)
            
            # Risk analysis
            risk_analysis = self._analyze_portfolio_risk(portfolio_entries)
            
            # Correlation analysis
            correlation_analysis = self._analyze_symbol_correlations(portfolio_entries)
            
            return {
                'portfolio_size': total_symbols,
                'max_size': self.max_portfolio_size,
                'utilization_rate': total_symbols / self.max_portfolio_size,
                'score_metrics': score_metrics,
                'sector_analysis': sector_analysis,
                'performance_analysis': performance_analysis,
                'risk_analysis': risk_analysis,
                'correlation_analysis': correlation_analysis,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {'error': str(e)}
    
    def optimize_portfolio_weights(self) -> Dict[str, Any]:
        """
        Optimize portfolio weights based on scores and risk characteristics.
        
        Returns:
            Dictionary with optimized weights and rationale
        """
        try:
            portfolio_entries = (
                PortfolioComposition.query
                .filter(PortfolioComposition.status == 'Active')
                .all()
            )
            
            if not portfolio_entries:
                return {'error': 'No active portfolio entries found'}
            
            # Simple score-based weighting for now
            # In production, this would use more sophisticated optimization
            total_score = sum(
                entry.current_score for entry in portfolio_entries 
                if entry.current_score
            )
            
            if total_score <= 0:
                # Equal weights if no valid scores
                equal_weight = Decimal('100.0') / len(portfolio_entries)
                optimized_weights = {
                    str(entry.symbol_id): equal_weight 
                    for entry in portfolio_entries
                }
            else:
                # Score-proportional weights
                optimized_weights = {}
                for entry in portfolio_entries:
                    if entry.current_score and entry.current_score > 0:
                        weight = (entry.current_score / total_score) * Decimal('100.0')
                        optimized_weights[str(entry.symbol_id)] = weight
                    else:
                        optimized_weights[str(entry.symbol_id)] = Decimal('0.0')
            
            # Apply weight constraints (min 2%, max 20%)
            min_weight = Decimal('2.0')
            max_weight = Decimal('20.0')
            
            for symbol_id in optimized_weights:
                if optimized_weights[symbol_id] < min_weight:
                    optimized_weights[symbol_id] = min_weight
                elif optimized_weights[symbol_id] > max_weight:
                    optimized_weights[symbol_id] = max_weight
            
            # Normalize to 100%
            total_weight = sum(optimized_weights.values())
            if total_weight > 0:
                for symbol_id in optimized_weights:
                    optimized_weights[symbol_id] = (
                        optimized_weights[symbol_id] / total_weight * Decimal('100.0')
                    )
            
            return {
                'optimized_weights': {k: float(v) for k, v in optimized_weights.items()},
                'optimization_method': 'score_proportional_with_constraints',
                'constraints': {
                    'min_weight': float(min_weight),
                    'max_weight': float(max_weight)
                },
                'total_weight': float(sum(optimized_weights.values())),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio weights: {e}")
            return {'error': str(e)}
    
    def rebalance_portfolio(self) -> Dict[str, Any]:
        """
        Rebalance portfolio based on optimized weights.
        
        Returns:
            Dictionary with rebalancing results
        """
        try:
            optimization_result = self.optimize_portfolio_weights()
            
            if 'error' in optimization_result:
                return optimization_result
            
            optimized_weights = optimization_result['optimized_weights']
            rebalancing_actions = []
            
            # Update portfolio weights
            for symbol_id_str, target_weight in optimized_weights.items():
                symbol_id = uuid.UUID(symbol_id_str)
                portfolio_entry = PortfolioComposition.query.filter_by(
                    symbol_id=symbol_id,
                    status='Active'
                ).first()
                
                if portfolio_entry:
                    old_weight = float(portfolio_entry.weight_percentage or 0)
                    new_weight = target_weight
                    weight_change = new_weight - old_weight
                    
                    portfolio_entry.weight_percentage = Decimal(str(target_weight))
                    
                    rebalancing_actions.append({
                        'symbol_id': symbol_id_str,
                        'symbol': portfolio_entry.symbol.symbol if portfolio_entry.symbol else None,
                        'old_weight': old_weight,
                        'new_weight': new_weight,
                        'weight_change': weight_change
                    })
            
            db.session.commit()
            
            return {
                'success': True,
                'rebalancing_actions': rebalancing_actions,
                'optimization_details': optimization_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rebalancing portfolio: {e}")
            return {'error': str(e)}
    
    def get_portfolio_performance_attribution(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze portfolio performance attribution by symbol.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with performance attribution analysis
        """
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            portfolio_entries = (
                PortfolioComposition.query
                .join(Symbol)
                .filter(PortfolioComposition.status == 'Active')
                .all()
            )
            
            attribution_data = []
            total_weighted_return = 0
            
            for entry in portfolio_entries:
                symbol_performance = entry.performance_since_inclusion or 0
                weight = float(entry.weight_percentage or 0) / 100
                contribution = symbol_performance * weight
                total_weighted_return += contribution
                
                attribution_data.append({
                    'symbol_id': str(entry.symbol_id),
                    'symbol': entry.symbol.symbol if entry.symbol else None,
                    'weight': weight,
                    'performance': symbol_performance,
                    'contribution': contribution,
                    'sector': entry.symbol.sector_category if entry.symbol else None
                })
            
            # Sort by contribution
            attribution_data.sort(key=lambda x: x['contribution'], reverse=True)
            
            # Sector attribution
            sector_attribution = {}
            for item in attribution_data:
                sector = item['sector'] or 'Unknown'
                if sector not in sector_attribution:
                    sector_attribution[sector] = {
                        'weight': 0,
                        'contribution': 0,
                        'symbols': []
                    }
                sector_attribution[sector]['weight'] += item['weight']
                sector_attribution[sector]['contribution'] += item['contribution']
                sector_attribution[sector]['symbols'].append(item['symbol'])
            
            return {
                'analysis_period_days': days,
                'total_portfolio_return': total_weighted_return,
                'symbol_attribution': attribution_data,
                'sector_attribution': sector_attribution,
                'top_contributors': attribution_data[:3],
                'bottom_contributors': attribution_data[-3:],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance attribution: {e}")
            return {'error': str(e)}
    
    def _calculate_score_metrics(self, scores: List[Decimal]) -> Dict[str, Any]:
        """Calculate statistical metrics for portfolio scores"""
        if not scores:
            return {}
        
        scores_float = [float(score) for score in scores]
        
        return {
            'count': len(scores_float),
            'mean': sum(scores_float) / len(scores_float),
            'min': min(scores_float),
            'max': max(scores_float),
            'range': max(scores_float) - min(scores_float),
            'std_dev': self._calculate_std_dev(scores_float)
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _analyze_sector_diversification(self, portfolio_entries: List[PortfolioComposition]) -> Dict[str, Any]:
        """Analyze sector diversification of the portfolio"""
        sector_counts = {}
        sector_weights = {}
        
        for entry in portfolio_entries:
            sector = entry.symbol.sector_category if entry.symbol else 'Unknown'
            weight = float(entry.weight_percentage or 0)
            
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
            sector_weights[sector] = sector_weights.get(sector, 0) + weight
        
        # Calculate concentration metrics
        total_sectors = len(sector_counts)
        max_sector_weight = max(sector_weights.values()) if sector_weights else 0
        
        # Herfindahl-Hirschman Index for concentration
        hhi = sum((weight / 100) ** 2 for weight in sector_weights.values())
        
        return {
            'sector_counts': sector_counts,
            'sector_weights': sector_weights,
            'total_sectors': total_sectors,
            'max_sector_weight': max_sector_weight,
            'concentration_hhi': hhi,
            'diversification_score': 1 - hhi  # Higher is more diversified
        }
    
    def _analyze_portfolio_performance(self, portfolio_entries: List[PortfolioComposition]) -> Dict[str, Any]:
        """Analyze portfolio performance metrics"""
        performances = [
            entry.performance_since_inclusion 
            for entry in portfolio_entries 
            if entry.performance_since_inclusion is not None
        ]
        
        if not performances:
            return {'error': 'No performance data available'}
        
        performances_float = [float(p) for p in performances]
        
        return {
            'count': len(performances_float),
            'mean_performance': sum(performances_float) / len(performances_float),
            'min_performance': min(performances_float),
            'max_performance': max(performances_float),
            'positive_performers': sum(1 for p in performances_float if p > 0),
            'negative_performers': sum(1 for p in performances_float if p < 0),
            'win_rate': sum(1 for p in performances_float if p > 0) / len(performances_float)
        }
    
    def _analyze_portfolio_risk(self, portfolio_entries: List[PortfolioComposition]) -> Dict[str, Any]:
        """Analyze portfolio risk metrics"""
        volatilities = [
            entry.volatility_since_inclusion 
            for entry in portfolio_entries 
            if entry.volatility_since_inclusion is not None
        ]
        
        drawdowns = [
            entry.max_drawdown_since_inclusion 
            for entry in portfolio_entries 
            if entry.max_drawdown_since_inclusion is not None
        ]
        
        risk_metrics = {}
        
        if volatilities:
            vol_float = [float(v) for v in volatilities]
            risk_metrics['volatility'] = {
                'mean': sum(vol_float) / len(vol_float),
                'min': min(vol_float),
                'max': max(vol_float),
                'std_dev': self._calculate_std_dev(vol_float)
            }
        
        if drawdowns:
            dd_float = [float(d) for d in drawdowns]
            risk_metrics['drawdown'] = {
                'mean': sum(dd_float) / len(dd_float),
                'min': min(dd_float),
                'max': max(dd_float),
                'worst_drawdown': min(dd_float)  # Most negative
            }
        
        return risk_metrics
    
    def _analyze_symbol_correlations(self, portfolio_entries: List[PortfolioComposition]) -> Dict[str, Any]:
        """Analyze correlations between portfolio symbols"""
        # Placeholder for correlation analysis
        # In production, this would calculate actual price correlations
        
        symbols = [entry.symbol.symbol for entry in portfolio_entries if entry.symbol]
        
        return {
            'symbols_analyzed': symbols,
            'correlation_matrix': {},  # Would contain actual correlation data
            'average_correlation': None,  # Would be calculated from price data
            'max_correlation': None,
            'min_correlation': None,
            'note': 'Correlation analysis requires historical price data implementation'
        }

