import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, asc
import statistics

from src.models.score_tracking import ScoreTracking, ScoreAnalytics
from src.utils.database import get_postgres_connection, postgres_transaction

logger = logging.getLogger(__name__)

class ScoreTrackingService:
    """
    Service for tracking Base Score and Total Score daily
    Provides comprehensive analytics and insights
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def record_daily_score(
        self,
        symbol: str,
        current_price: float,
        risk_value: float,
        risk_band: str,
        base_score: float,
        coefficient_value: float,
        total_score: float,
        risk_bands_data: Dict[str, Any],
        life_age_days: int,
        base_score_components: Optional[Dict[str, Any]] = None,
        coefficient_calculation: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record daily score tracking data
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            risk_value: Calculated risk value
            risk_band: Current risk band
            base_score: Base score before coefficient
            coefficient_value: Applied coefficient
            total_score: Final score after coefficient
            risk_bands_data: Complete risk bands data
            life_age_days: Symbol life age in days
            base_score_components: Breakdown of base score calculation
            coefficient_calculation: Details of coefficient calculation
            
        Returns:
            bool: Success status
        """
        try:
            # Calculate additional metrics
            current_band_rank = self._calculate_band_rank(risk_band, risk_bands_data)
            rarity_factor = self._calculate_rarity_factor(risk_band, risk_bands_data)
            proximity_bonus = self._calculate_proximity_bonus(risk_band, risk_bands_data)
            
            # Prepare tracking data
            tracking_data = {
                'symbol': symbol,
                'tracking_date': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'current_price': current_price,
                'risk_value': risk_value,
                'risk_band': risk_band,
                'base_score': base_score,
                'base_score_components': json.dumps(base_score_components) if base_score_components else None,
                'coefficient_value': coefficient_value,
                'coefficient_calculation': json.dumps(coefficient_calculation) if coefficient_calculation else None,
                'total_score': total_score,
                'risk_bands_data': json.dumps(risk_bands_data),
                'current_band_rank': current_band_rank,
                'rarity_factor': rarity_factor,
                'proximity_bonus': proximity_bonus,
                'life_age_days': life_age_days
            }
            
            # Check if record already exists for today
            existing_record = await self._get_today_record(symbol)
            
            if existing_record:
                # Update existing record
                await self._update_record(existing_record['id'], tracking_data)
                self.logger.info(f"Updated score tracking for {symbol} on {tracking_data['tracking_date']}")
            else:
                # Create new record
                await self._create_record(tracking_data)
                self.logger.info(f"Created score tracking for {symbol} on {tracking_data['tracking_date']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording daily score for {symbol}: {e}")
            return False
    
    async def get_score_history(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get score history for a symbol
        
        Args:
            symbol: Trading symbol
            start_date: Start date for query
            end_date: End date for query
            limit: Maximum number of records
            
        Returns:
            List of score tracking records
        """
        try:
            async with postgres_transaction() as conn:
                query = conn.query(ScoreTracking).filter(ScoreTracking.symbol == symbol)
                
                if start_date:
                    query = query.filter(ScoreTracking.tracking_date >= start_date)
                if end_date:
                    query = query.filter(ScoreTracking.tracking_date <= end_date)
                
                records = await conn.execute(
                    query.order_by(desc(ScoreTracking.tracking_date)).limit(limit)
                )
                
                return [record.to_dict() for record in records.scalars().all()]
                
        except Exception as e:
            self.logger.error(f"Error getting score history for {symbol}: {e}")
            return []
    
    async def get_score_analytics(
        self,
        symbol: str,
        period_type: str = 'daily',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive score analytics
        
        Args:
            symbol: Trading symbol
            period_type: 'daily', 'weekly', 'monthly'
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Analytics data
        """
        try:
            # Get raw data
            history = await self.get_score_history(symbol, start_date, end_date, limit=1000)
            
            if not history:
                return self._empty_analytics()
            
            # Calculate analytics
            analytics = {
                'symbol': symbol,
                'period_type': period_type,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'data_points': len(history),
                'score_statistics': self._calculate_score_statistics(history),
                'coefficient_statistics': self._calculate_coefficient_statistics(history),
                'risk_band_distribution': self._calculate_risk_band_distribution(history),
                'correlation_analysis': self._calculate_correlation_analysis(history),
                'trend_analysis': self._calculate_trend_analysis(history),
                'volatility_analysis': self._calculate_volatility_analysis(history)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error calculating analytics for {symbol}: {e}")
            return self._empty_analytics()
    
    async def get_comparative_analysis(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Compare score performance across multiple symbols
        
        Args:
            symbols: List of symbols to compare
            start_date: Start date for comparison
            end_date: End date for comparison
            
        Returns:
            Comparative analysis data
        """
        try:
            comparative_data = {}
            
            for symbol in symbols:
                analytics = await self.get_score_analytics(symbol, 'daily', start_date, end_date)
                comparative_data[symbol] = analytics
            
            # Calculate cross-symbol metrics
            cross_symbol_metrics = self._calculate_cross_symbol_metrics(comparative_data)
            
            return {
                'comparative_data': comparative_data,
                'cross_symbol_metrics': cross_symbol_metrics,
                'ranking': self._calculate_symbol_ranking(comparative_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating comparative analysis: {e}")
            return {}
    
    def _calculate_band_rank(self, risk_band: str, risk_bands_data: Dict[str, Any]) -> Optional[int]:
        """Calculate rank of current band among all bands"""
        try:
            bands_array = [
                {'band': band, 'days': data.get('days', 0)}
                for band, data in risk_bands_data.items()
                if data and data.get('days') is not None
            ]
            
            bands_array.sort(key=lambda x: x['days'])
            
            for i, band_info in enumerate(bands_array):
                if band_info['band'] == risk_band:
                    return i + 1  # 1-based ranking
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating band rank: {e}")
            return None
    
    def _calculate_rarity_factor(self, risk_band: str, risk_bands_data: Dict[str, Any]) -> Optional[float]:
        """Calculate rarity factor (0 = most common, 1 = rarest)"""
        try:
            band_rank = self._calculate_band_rank(risk_band, risk_bands_data)
            if band_rank is None:
                return None
            
            total_bands = len([b for b in risk_bands_data.values() if b and b.get('days') is not None])
            if total_bands <= 1:
                return 0.5
            
            return 1 - (band_rank - 1) / (total_bands - 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating rarity factor: {e}")
            return None
    
    def _calculate_proximity_bonus(self, risk_band: str, risk_bands_data: Dict[str, Any]) -> Optional[float]:
        """Calculate proximity bonus based on neighboring bands"""
        try:
            bands_array = [
                {'band': band, 'days': data.get('days', 0)}
                for band, data in risk_bands_data.items()
                if data and data.get('days') is not None
            ]
            
            bands_array.sort(key=lambda x: x['days'])
            current_index = next((i for i, b in enumerate(bands_array) if b['band'] == risk_band), None)
            
            if current_index is None:
                return None
            
            current_days = bands_array[current_index]['days']
            lower_neighbor = bands_array[current_index - 1] if current_index > 0 else None
            upper_neighbor = bands_array[current_index + 1] if current_index < len(bands_array) - 1 else None
            
            proximity_bonus = 0
            
            if lower_neighbor and upper_neighbor:
                lower_rarer = lower_neighbor['days'] < current_days
                upper_rarer = upper_neighbor['days'] < current_days
                
                if lower_rarer and upper_rarer:
                    proximity_bonus = 15  # High opportunity
                elif lower_rarer or upper_rarer:
                    rarer_neighbor = lower_neighbor if lower_rarer else upper_neighbor
                    rarity_ratio = current_days / rarer_neighbor['days']
                    proximity_bonus = min(10, rarity_ratio * 5)
            
            return proximity_bonus
            
        except Exception as e:
            self.logger.error(f"Error calculating proximity bonus: {e}")
            return None
    
    async def _get_today_record(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get today's record for a symbol"""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            async with postgres_transaction() as conn:
                result = await conn.execute(
                    conn.query(ScoreTracking).filter(
                        and_(
                            ScoreTracking.symbol == symbol,
                            ScoreTracking.tracking_date == today
                        )
                    ).first()
                )
                
                record = result.scalar()
                return record.to_dict() if record else None
                
        except Exception as e:
            self.logger.error(f"Error getting today's record for {symbol}: {e}")
            return None
    
    async def _create_record(self, tracking_data: Dict[str, Any]) -> bool:
        """Create new tracking record"""
        try:
            async with postgres_transaction() as conn:
                record = ScoreTracking.from_dict(tracking_data)
                conn.add(record)
                await conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating tracking record: {e}")
            return False
    
    async def _update_record(self, record_id: int, tracking_data: Dict[str, Any]) -> bool:
        """Update existing tracking record"""
        try:
            async with postgres_transaction() as conn:
                record = await conn.get(ScoreTracking, record_id)
                if record:
                    for key, value in tracking_data.items():
                        if hasattr(record, key):
                            setattr(record, key, value)
                    await conn.commit()
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating tracking record: {e}")
            return False
    
    def _calculate_score_statistics(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate score statistics"""
        base_scores = [h['base_score'] for h in history if h.get('base_score') is not None]
        total_scores = [h['total_score'] for h in history if h.get('total_score') is not None]
        
        return {
            'base_score': {
                'mean': statistics.mean(base_scores) if base_scores else 0,
                'median': statistics.median(base_scores) if base_scores else 0,
                'min': min(base_scores) if base_scores else 0,
                'max': max(base_scores) if base_scores else 0,
                'std': statistics.stdev(base_scores) if len(base_scores) > 1 else 0
            },
            'total_score': {
                'mean': statistics.mean(total_scores) if total_scores else 0,
                'median': statistics.median(total_scores) if total_scores else 0,
                'min': min(total_scores) if total_scores else 0,
                'max': max(total_scores) if total_scores else 0,
                'std': statistics.stdev(total_scores) if len(total_scores) > 1 else 0
            }
        }
    
    def _calculate_coefficient_statistics(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate coefficient statistics"""
        coefficients = [h['coefficient_value'] for h in history if h.get('coefficient_value') is not None]
        
        return {
            'mean': statistics.mean(coefficients) if coefficients else 0,
            'median': statistics.median(coefficients) if coefficients else 0,
            'min': min(coefficients) if coefficients else 0,
            'max': max(coefficients) if coefficients else 0,
            'std': statistics.stdev(coefficients) if len(coefficients) > 1 else 0
        }
    
    def _calculate_risk_band_distribution(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate risk band distribution"""
        distribution = {}
        for record in history:
            band = record.get('risk_band')
            if band:
                distribution[band] = distribution.get(band, 0) + 1
        return distribution
    
    def _calculate_correlation_analysis(self, history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate correlation between different metrics"""
        try:
            base_scores = [h['base_score'] for h in history if h.get('base_score') is not None]
            total_scores = [h['total_score'] for h in history if h.get('total_score') is not None]
            coefficients = [h['coefficient_value'] for h in history if h.get('coefficient_value') is not None]
            risk_values = [h['risk_value'] for h in history if h.get('risk_value') is not None]
            
            correlations = {}
            
            if len(base_scores) == len(total_scores) and len(base_scores) > 1:
                correlations['base_total_correlation'] = self._calculate_correlation(base_scores, total_scores)
            
            if len(base_scores) == len(coefficients) and len(base_scores) > 1:
                correlations['base_coefficient_correlation'] = self._calculate_correlation(base_scores, coefficients)
            
            if len(risk_values) == len(base_scores) and len(risk_values) > 1:
                correlations['risk_base_correlation'] = self._calculate_correlation(risk_values, base_scores)
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error calculating correlations: {e}")
            return {}
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        try:
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            sum_y2 = sum(y[i] ** 2 for i in range(n))
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def _calculate_trend_analysis(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend analysis"""
        if len(history) < 2:
            return {}
        
        # Sort by date
        sorted_history = sorted(history, key=lambda x: x.get('tracking_date', ''))
        
        # Calculate trends
        base_scores = [h['base_score'] for h in sorted_history if h.get('base_score') is not None]
        total_scores = [h['total_score'] for h in sorted_history if h.get('total_score') is not None]
        
        trends = {}
        
        if len(base_scores) > 1:
            base_trend = (base_scores[-1] - base_scores[0]) / len(base_scores)
            trends['base_score_trend'] = base_trend
        
        if len(total_scores) > 1:
            total_trend = (total_scores[-1] - total_scores[0]) / len(total_scores)
            trends['total_score_trend'] = total_trend
        
        return trends
    
    def _calculate_volatility_analysis(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate volatility analysis"""
        base_scores = [h['base_score'] for h in history if h.get('base_score') is not None]
        total_scores = [h['total_score'] for h in history if h.get('total_score') is not None]
        
        return {
            'base_score_volatility': statistics.stdev(base_scores) if len(base_scores) > 1 else 0,
            'total_score_volatility': statistics.stdev(total_scores) if len(total_scores) > 1 else 0,
            'coefficient_of_variation_base': (statistics.stdev(base_scores) / statistics.mean(base_scores)) if base_scores and statistics.mean(base_scores) != 0 else 0,
            'coefficient_of_variation_total': (statistics.stdev(total_scores) / statistics.mean(total_scores)) if total_scores and statistics.mean(total_scores) != 0 else 0
        }
    
    def _calculate_cross_symbol_metrics(self, comparative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cross-symbol metrics"""
        try:
            all_base_scores = []
            all_total_scores = []
            all_coefficients = []
            
            for symbol_data in comparative_data.values():
                if 'score_statistics' in symbol_data:
                    stats = symbol_data['score_statistics']
                    if 'base_score' in stats:
                        all_base_scores.append(stats['base_score']['mean'])
                    if 'total_score' in stats:
                        all_total_scores.append(stats['total_score']['mean'])
                
                if 'coefficient_statistics' in symbol_data:
                    all_coefficients.append(symbol_data['coefficient_statistics']['mean'])
            
            return {
                'average_base_score_across_symbols': statistics.mean(all_base_scores) if all_base_scores else 0,
                'average_total_score_across_symbols': statistics.mean(all_total_scores) if all_total_scores else 0,
                'average_coefficient_across_symbols': statistics.mean(all_coefficients) if all_coefficients else 0,
                'base_score_ranking': sorted(enumerate(all_base_scores), key=lambda x: x[1], reverse=True) if all_base_scores else [],
                'total_score_ranking': sorted(enumerate(all_total_scores), key=lambda x: x[1], reverse=True) if all_total_scores else []
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating cross-symbol metrics: {e}")
            return {}
    
    def _calculate_symbol_ranking(self, comparative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate symbol ranking based on performance"""
        try:
            rankings = {}
            
            for symbol, data in comparative_data.items():
                if 'score_statistics' in data:
                    stats = data['score_statistics']
                    rankings[symbol] = {
                        'base_score_avg': stats.get('base_score', {}).get('mean', 0),
                        'total_score_avg': stats.get('total_score', {}).get('mean', 0),
                        'volatility': data.get('volatility_analysis', {}).get('total_score_volatility', 0)
                    }
            
            # Sort by total score average
            sorted_rankings = sorted(rankings.items(), key=lambda x: x[1]['total_score_avg'], reverse=True)
            
            return {
                'by_total_score': sorted_rankings,
                'by_base_score': sorted(rankings.items(), key=lambda x: x[1]['base_score_avg'], reverse=True),
                'by_stability': sorted(rankings.items(), key=lambda x: x[1]['volatility'])
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating symbol ranking: {e}")
            return {}
    
    def _empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            'symbol': None,
            'period_type': 'daily',
            'start_date': None,
            'end_date': None,
            'data_points': 0,
            'score_statistics': {},
            'coefficient_statistics': {},
            'risk_band_distribution': {},
            'correlation_analysis': {},
            'trend_analysis': {},
            'volatility_analysis': {}
        }
