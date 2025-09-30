from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class ScoreTracking(Base):
    """
    Database model for tracking Base Score and Total Score daily
    Tracks both scores separately to understand coefficient impact
    """
    __tablename__ = 'score_tracking'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Symbol and date identification
    symbol = Column(String(20), nullable=False, index=True)
    tracking_date = Column(DateTime, nullable=False, index=True)
    
    # Market data
    current_price = Column(Float, nullable=False)
    risk_value = Column(Float, nullable=False)
    risk_band = Column(String(20), nullable=False)
    
    # Base Score (before coefficient)
    base_score = Column(Float, nullable=False)
    base_score_components = Column(Text, nullable=True)  # JSON string with breakdown
    
    # Coefficient data
    coefficient_value = Column(Float, nullable=False)
    coefficient_calculation = Column(Text, nullable=True)  # JSON string with calculation details
    
    # Total Score (after coefficient applied)
    total_score = Column(Float, nullable=False)
    
    # Risk bands context
    risk_bands_data = Column(Text, nullable=True)  # JSON string with all bands data
    current_band_rank = Column(Integer, nullable=True)  # Rank among all bands (1=rarest)
    rarity_factor = Column(Float, nullable=True)
    proximity_bonus = Column(Float, nullable=True)
    
    # Life age context
    life_age_days = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'tracking_date'),
        Index('idx_date_range', 'tracking_date'),
        Index('idx_score_range', 'base_score', 'total_score'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'tracking_date': self.tracking_date.isoformat(),
            'current_price': self.current_price,
            'risk_value': self.risk_value,
            'risk_band': self.risk_band,
            'base_score': self.base_score,
            'base_score_components': self.base_score_components,
            'coefficient_value': self.coefficient_value,
            'coefficient_calculation': self.coefficient_calculation,
            'total_score': self.total_score,
            'risk_bands_data': self.risk_bands_data,
            'current_band_rank': self.current_band_rank,
            'rarity_factor': self.rarity_factor,
            'proximity_bonus': self.proximity_bonus,
            'life_age_days': self.life_age_days,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScoreTracking':
        """Create model from dictionary"""
        return cls(
            symbol=data.get('symbol'),
            tracking_date=datetime.fromisoformat(data['tracking_date']) if data.get('tracking_date') else datetime.utcnow(),
            current_price=data.get('current_price'),
            risk_value=data.get('risk_value'),
            risk_band=data.get('risk_band'),
            base_score=data.get('base_score'),
            base_score_components=data.get('base_score_components'),
            coefficient_value=data.get('coefficient_value'),
            coefficient_calculation=data.get('coefficient_calculation'),
            total_score=data.get('total_score'),
            risk_bands_data=data.get('risk_bands_data'),
            current_band_rank=data.get('current_band_rank'),
            rarity_factor=data.get('rarity_factor'),
            proximity_bonus=data.get('proximity_bonus'),
            life_age_days=data.get('life_age_days')
        )

class ScoreAnalytics(Base):
    """
    Analytics table for aggregated score insights
    Pre-calculated metrics for efficient querying
    """
    __tablename__ = 'score_analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Symbol and period
    symbol = Column(String(20), nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Score statistics
    avg_base_score = Column(Float, nullable=False)
    avg_total_score = Column(Float, nullable=False)
    min_base_score = Column(Float, nullable=False)
    max_base_score = Column(Float, nullable=False)
    min_total_score = Column(Float, nullable=False)
    max_total_score = Column(Float, nullable=False)
    
    # Coefficient statistics
    avg_coefficient = Column(Float, nullable=False)
    min_coefficient = Column(Float, nullable=False)
    max_coefficient = Column(Float, nullable=False)
    
    # Risk band distribution
    risk_band_distribution = Column(Text, nullable=True)  # JSON string
    
    # Score correlation metrics
    base_total_correlation = Column(Float, nullable=True)
    coefficient_impact = Column(Float, nullable=True)  # Average impact of coefficient
    
    # Metadata
    data_points_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_symbol_period', 'symbol', 'period_type', 'period_start'),
        Index('idx_analytics_date', 'period_start', 'period_end'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'period_type': self.period_type,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'avg_base_score': self.avg_base_score,
            'avg_total_score': self.avg_total_score,
            'min_base_score': self.min_base_score,
            'max_base_score': self.max_base_score,
            'min_total_score': self.min_total_score,
            'max_total_score': self.max_total_score,
            'avg_coefficient': self.avg_coefficient,
            'min_coefficient': self.min_coefficient,
            'max_coefficient': self.max_coefficient,
            'risk_band_distribution': self.risk_band_distribution,
            'base_total_correlation': self.base_total_correlation,
            'coefficient_impact': self.coefficient_impact,
            'data_points_count': self.data_points_count,
            'created_at': self.created_at.isoformat()
        }
