#!/usr/bin/env python3
"""
Support and Resistance Level Models
Stores critical price levels extracted from liquidation clusters
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, List

Base = declarative_base()

class SupportResistanceLevel(Base):
    """Model for storing support and resistance levels"""
    __tablename__ = 'support_resistance_levels'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)  # 24h, 7d, 1m
    level_type = Column(String(20), nullable=False)  # support, resistance
    price_level = Column(Float, nullable=False)
    strength = Column(Float, default=0.5)  # 0-1 strength indicator
    volume_concentration = Column(Float, default=0)  # Liquidation volume at this level
    
    # Source information
    source_agent = Column(String(50))  # Which sub-agent detected this
    source_image_type = Column(String(50))  # Type of image analyzed
    
    # Validation and usage
    is_active = Column(Boolean, default=True)  # Whether level is still valid
    hit_count = Column(Integer, default=0)  # How many times price touched this level
    break_count = Column(Integer, default=0)  # How many times level was broken
    
    # Metadata
    cluster_data = Column(JSON)  # Original cluster information
    confidence = Column(Float, default=0.5)  # Confidence in this level
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    last_validated = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When this level should be re-evaluated
    
    # Create composite index for fast queries
    __table_args__ = (
        Index('idx_symbol_timeframe_active', 'symbol', 'timeframe', 'is_active'),
        Index('idx_symbol_level_type', 'symbol', 'level_type', 'is_active'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'level_type': self.level_type,
            'price_level': self.price_level,
            'strength': self.strength,
            'volume_concentration': self.volume_concentration,
            'confidence': self.confidence,
            'is_active': self.is_active,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class LiquidationCluster(Base):
    """Model for storing liquidation cluster data"""
    __tablename__ = 'liquidation_clusters'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    
    # Cluster properties
    center_price = Column(Float, nullable=False)
    price_range_start = Column(Float, nullable=False)
    price_range_end = Column(Float, nullable=False)
    
    # Liquidation data
    long_liquidation_volume = Column(Float, default=0)
    short_liquidation_volume = Column(Float, default=0)
    total_volume = Column(Float, default=0)
    
    # Derived levels
    derived_support = Column(Float)  # Support level derived from this cluster
    derived_resistance = Column(Float)  # Resistance level derived from this cluster
    
    # Analysis metadata
    intensity = Column(Float, default=0.5)
    density = Column(Float, default=0.5)
    significance = Column(Float, default=0.5)
    
    # Source
    source_agent = Column(String(50))
    source_analysis_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Index for queries
    __table_args__ = (
        Index('idx_cluster_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_cluster_price_range', 'symbol', 'price_range_start', 'price_range_end'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'center_price': self.center_price,
            'price_range': {
                'start': self.price_range_start,
                'end': self.price_range_end
            },
            'liquidation_volumes': {
                'long': self.long_liquidation_volume,
                'short': self.short_liquidation_volume,
                'total': self.total_volume
            },
            'derived_levels': {
                'support': self.derived_support,
                'resistance': self.derived_resistance
            },
            'metrics': {
                'intensity': self.intensity,
                'density': self.density,
                'significance': self.significance
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TradingTargets(Base):
    """Model for storing trading targets based on support/resistance"""
    __tablename__ = 'trading_targets'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    position_type = Column(String(10), nullable=False)  # long, short
    
    # Entry and exit levels
    entry_price = Column(Float, nullable=False)
    
    # Targets (can have multiple)
    target_1 = Column(Float)
    target_2 = Column(Float)
    target_3 = Column(Float)
    
    # Stop loss
    stop_loss = Column(Float, nullable=False)
    
    # Risk/Reward
    risk_reward_ratio = Column(Float)
    
    # Confidence and strength
    confidence = Column(Float, default=0.5)
    strength = Column(Float, default=0.5)
    
    # Source levels
    support_levels = Column(JSON)  # List of support level IDs used
    resistance_levels = Column(JSON)  # List of resistance level IDs used
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default='pending')  # pending, active, completed, cancelled
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Index for queries
    __table_args__ = (
        Index('idx_targets_symbol_timeframe', 'symbol', 'timeframe', 'is_active'),
        Index('idx_targets_status', 'status', 'is_active'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'position_type': self.position_type,
            'entry_price': self.entry_price,
            'targets': [t for t in [self.target_1, self.target_2, self.target_3] if t],
            'stop_loss': self.stop_loss,
            'risk_reward_ratio': self.risk_reward_ratio,
            'confidence': self.confidence,
            'strength': self.strength,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }