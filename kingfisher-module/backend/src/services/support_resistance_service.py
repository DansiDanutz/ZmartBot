#!/usr/bin/env python3
"""
Support and Resistance Service
Manages support/resistance levels extracted from liquidation clusters
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
import numpy as np

from src.models.support_resistance import (
    Base, SupportResistanceLevel, LiquidationCluster, TradingTargets
)

logger = logging.getLogger(__name__)

class SupportResistanceService:
    """Service for managing support and resistance levels"""
    
    def __init__(self, database_url: str = "sqlite:///kingfisher_levels.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("Support/Resistance Service initialized")
    
    async def store_support_resistance_levels(
        self, 
        symbol: str, 
        timeframe: str,
        levels: List[Dict[str, Any]],
        source_agent: str
    ) -> List[int]:
        """Store support and resistance levels in database"""
        session = self.SessionLocal()
        stored_ids = []
        
        try:
            for level in levels:
                # Check if similar level already exists
                existing = session.query(SupportResistanceLevel).filter(
                    and_(
                        SupportResistanceLevel.symbol == symbol,
                        SupportResistanceLevel.timeframe == timeframe,
                        SupportResistanceLevel.level_type == level['type'],
                        SupportResistanceLevel.price_level.between(
                            level['price'] * 0.995,  # 0.5% tolerance
                            level['price'] * 1.005
                        ),
                        SupportResistanceLevel.is_active == True
                    )
                ).first()
                
                if existing:
                    # Update existing level
                    existing.strength = max(existing.strength, level.get('strength', 0.5))
                    existing.volume_concentration += level.get('volume', 0)
                    existing.confidence = max(existing.confidence, level.get('confidence', 0.5))
                    existing.last_validated = datetime.utcnow()
                    existing.hit_count += 1
                    stored_ids.append(existing.id)
                else:
                    # Create new level
                    new_level = SupportResistanceLevel(
                        symbol=symbol,
                        timeframe=timeframe,
                        level_type=level['type'],
                        price_level=level['price'],
                        strength=level.get('strength', 0.5),
                        volume_concentration=level.get('volume', 0),
                        source_agent=source_agent,
                        source_image_type=level.get('image_type'),
                        confidence=level.get('confidence', 0.5),
                        cluster_data=level.get('cluster_data', {}),
                        expires_at=datetime.utcnow() + self._get_expiry_delta(timeframe)
                    )
                    session.add(new_level)
                    session.flush()
                    stored_ids.append(new_level.id)
            
            session.commit()
            logger.info(f"Stored {len(stored_ids)} support/resistance levels for {symbol} {timeframe}")
            return stored_ids
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing support/resistance levels: {e}")
            raise
        finally:
            session.close()
    
    async def store_liquidation_clusters(
        self,
        symbol: str,
        timeframe: str,
        clusters: List[Dict[str, Any]],
        source_agent: str
    ) -> List[int]:
        """Store liquidation cluster data"""
        session = self.SessionLocal()
        stored_ids = []
        
        try:
            for cluster in clusters:
                new_cluster = LiquidationCluster(
                    symbol=symbol,
                    timeframe=timeframe,
                    center_price=cluster['center_price'],
                    price_range_start=cluster['range_start'],
                    price_range_end=cluster['range_end'],
                    long_liquidation_volume=cluster.get('long_volume', 0),
                    short_liquidation_volume=cluster.get('short_volume', 0),
                    total_volume=cluster.get('total_volume', 0),
                    derived_support=cluster.get('support_level'),
                    derived_resistance=cluster.get('resistance_level'),
                    intensity=cluster.get('intensity', 0.5),
                    density=cluster.get('density', 0.5),
                    significance=cluster.get('significance', 0.5),
                    source_agent=source_agent,
                    source_analysis_id=cluster.get('analysis_id')
                )
                session.add(new_cluster)
                session.flush()
                stored_ids.append(new_cluster.id)
            
            session.commit()
            logger.info(f"Stored {len(stored_ids)} liquidation clusters for {symbol} {timeframe}")
            return stored_ids
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing liquidation clusters: {e}")
            raise
        finally:
            session.close()
    
    async def get_active_levels(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
        level_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get active support/resistance levels for a symbol"""
        session = self.SessionLocal()
        
        try:
            query = session.query(SupportResistanceLevel).filter(
                and_(
                    SupportResistanceLevel.symbol == symbol,
                    SupportResistanceLevel.is_active == True
                )
            )
            
            if timeframe:
                query = query.filter(SupportResistanceLevel.timeframe == timeframe)
            
            if level_type:
                query = query.filter(SupportResistanceLevel.level_type == level_type)
            
            # Order by strength and confidence
            query = query.order_by(
                SupportResistanceLevel.strength.desc(),
                SupportResistanceLevel.confidence.desc()
            )
            
            levels = query.all()
            return [level.to_dict() for level in levels]
            
        finally:
            session.close()
    
    async def get_trading_targets(
        self,
        symbol: str,
        timeframe: str,
        current_price: float
    ) -> Dict[str, Any]:
        """Generate trading targets based on support/resistance levels"""
        session = self.SessionLocal()
        
        try:
            # Get active levels
            support_levels = session.query(SupportResistanceLevel).filter(
                and_(
                    SupportResistanceLevel.symbol == symbol,
                    SupportResistanceLevel.timeframe == timeframe,
                    SupportResistanceLevel.level_type == 'support',
                    SupportResistanceLevel.is_active == True,
                    SupportResistanceLevel.price_level < current_price
                )
            ).order_by(SupportResistanceLevel.price_level.desc()).limit(3).all()
            
            resistance_levels = session.query(SupportResistanceLevel).filter(
                and_(
                    SupportResistanceLevel.symbol == symbol,
                    SupportResistanceLevel.timeframe == timeframe,
                    SupportResistanceLevel.level_type == 'resistance',
                    SupportResistanceLevel.is_active == True,
                    SupportResistanceLevel.price_level > current_price
                )
            ).order_by(SupportResistanceLevel.price_level.asc()).limit(3).all()
            
            # Generate long targets
            long_targets = self._generate_long_targets(
                current_price, support_levels, resistance_levels
            )
            
            # Generate short targets
            short_targets = self._generate_short_targets(
                current_price, support_levels, resistance_levels
            )
            
            # Store targets in database
            if long_targets['confidence'] > 0.6:
                self._store_trading_targets(session, symbol, timeframe, 'long', long_targets)
            
            if short_targets['confidence'] > 0.6:
                self._store_trading_targets(session, symbol, timeframe, 'short', short_targets)
            
            session.commit()
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'long_setup': long_targets,
                'short_setup': short_targets,
                'support_levels': [s.price_level for s in support_levels],
                'resistance_levels': [r.price_level for r in resistance_levels]
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error generating trading targets: {e}")
            raise
        finally:
            session.close()
    
    def _generate_long_targets(
        self,
        current_price: float,
        support_levels: List[SupportResistanceLevel],
        resistance_levels: List[SupportResistanceLevel]
    ) -> Dict[str, Any]:
        """Generate long position targets"""
        if not support_levels or not resistance_levels:
            return {
                'entry': current_price,
                'targets': [],
                'stop_loss': current_price * 0.97,
                'confidence': 0.3
            }
        
        # Entry near current price or first support
        entry = current_price
        
        # Stop loss below nearest support
        stop_loss = support_levels[0].price_level * 0.995  # Just below support
        
        # Targets at resistance levels
        targets = []
        for i, resistance in enumerate(resistance_levels[:3]):
            targets.append(resistance.price_level * (1 - 0.002 * i))  # Slightly below resistance
        
        # Calculate risk/reward
        risk = entry - stop_loss
        reward = targets[0] - entry if targets else 0
        risk_reward = reward / risk if risk > 0 else 0
        
        # Calculate confidence based on level strength
        avg_support_strength = np.mean([s.strength for s in support_levels])
        avg_resistance_strength = np.mean([r.strength for r in resistance_levels])
        confidence = (avg_support_strength + avg_resistance_strength) / 2
        
        return {
            'entry': entry,
            'targets': targets,
            'stop_loss': stop_loss,
            'risk_reward_ratio': risk_reward,
            'confidence': confidence,
            'support_used': [s.id for s in support_levels],
            'resistance_used': [r.id for r in resistance_levels]
        }
    
    def _generate_short_targets(
        self,
        current_price: float,
        support_levels: List[SupportResistanceLevel],
        resistance_levels: List[SupportResistanceLevel]
    ) -> Dict[str, Any]:
        """Generate short position targets"""
        if not support_levels or not resistance_levels:
            return {
                'entry': current_price,
                'targets': [],
                'stop_loss': current_price * 1.03,
                'confidence': 0.3
            }
        
        # Entry near current price or first resistance
        entry = current_price
        
        # Stop loss above nearest resistance
        stop_loss = resistance_levels[0].price_level * 1.005  # Just above resistance
        
        # Targets at support levels
        targets = []
        for i, support in enumerate(support_levels[:3]):
            targets.append(support.price_level * (1 + 0.002 * i))  # Slightly above support
        
        # Calculate risk/reward
        risk = stop_loss - entry
        reward = entry - targets[0] if targets else 0
        risk_reward = reward / risk if risk > 0 else 0
        
        # Calculate confidence
        avg_support_strength = np.mean([s.strength for s in support_levels])
        avg_resistance_strength = np.mean([r.strength for r in resistance_levels])
        confidence = (avg_support_strength + avg_resistance_strength) / 2
        
        return {
            'entry': entry,
            'targets': targets,
            'stop_loss': stop_loss,
            'risk_reward_ratio': risk_reward,
            'confidence': confidence,
            'support_used': [s.id for s in support_levels],
            'resistance_used': [r.id for r in resistance_levels]
        }
    
    def _store_trading_targets(
        self,
        session: Session,
        symbol: str,
        timeframe: str,
        position_type: str,
        targets_data: Dict[str, Any]
    ):
        """Store trading targets in database"""
        targets = targets_data['targets']
        
        new_target = TradingTargets(
            symbol=symbol,
            timeframe=timeframe,
            position_type=position_type,
            entry_price=targets_data['entry'],
            target_1=targets[0] if len(targets) > 0 else None,
            target_2=targets[1] if len(targets) > 1 else None,
            target_3=targets[2] if len(targets) > 2 else None,
            stop_loss=targets_data['stop_loss'],
            risk_reward_ratio=targets_data['risk_reward_ratio'],
            confidence=targets_data['confidence'],
            strength=targets_data['confidence'],  # Can be refined
            support_levels=targets_data.get('support_used', []),
            resistance_levels=targets_data.get('resistance_used', [])
        )
        session.add(new_target)
    
    def _get_expiry_delta(self, timeframe: str) -> timedelta:
        """Get expiry time delta based on timeframe"""
        if timeframe == '24h':
            return timedelta(hours=24)
        elif timeframe == '7d':
            return timedelta(days=7)
        elif timeframe == '1m':
            return timedelta(days=30)
        else:
            return timedelta(days=1)
    
    async def invalidate_broken_levels(
        self,
        symbol: str,
        current_price: float,
        tolerance: float = 0.02
    ):
        """Invalidate support/resistance levels that have been broken"""
        session = self.SessionLocal()
        
        try:
            # Find broken support levels (price went below)
            broken_supports = session.query(SupportResistanceLevel).filter(
                and_(
                    SupportResistanceLevel.symbol == symbol,
                    SupportResistanceLevel.level_type == 'support',
                    SupportResistanceLevel.is_active == True,
                    SupportResistanceLevel.price_level > current_price * (1 + tolerance)
                )
            ).all()
            
            for support in broken_supports:
                support.is_active = False
                support.break_count += 1
                logger.info(f"Invalidated broken support at {support.price_level} for {symbol}")
            
            # Find broken resistance levels (price went above)
            broken_resistances = session.query(SupportResistanceLevel).filter(
                and_(
                    SupportResistanceLevel.symbol == symbol,
                    SupportResistanceLevel.level_type == 'resistance',
                    SupportResistanceLevel.is_active == True,
                    SupportResistanceLevel.price_level < current_price * (1 - tolerance)
                )
            ).all()
            
            for resistance in broken_resistances:
                resistance.is_active = False
                resistance.break_count += 1
                logger.info(f"Invalidated broken resistance at {resistance.price_level} for {symbol}")
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error invalidating broken levels: {e}")
        finally:
            session.close()
    
    async def get_nearest_levels(
        self,
        symbol: str,
        current_price: float,
        timeframe: Optional[str] = None,
        count: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get nearest support and resistance levels to current price"""
        session = self.SessionLocal()
        
        try:
            base_query = session.query(SupportResistanceLevel).filter(
                and_(
                    SupportResistanceLevel.symbol == symbol,
                    SupportResistanceLevel.is_active == True
                )
            )
            
            if timeframe:
                base_query = base_query.filter(SupportResistanceLevel.timeframe == timeframe)
            
            # Get nearest supports below current price
            supports = base_query.filter(
                and_(
                    SupportResistanceLevel.level_type == 'support',
                    SupportResistanceLevel.price_level < current_price
                )
            ).order_by(SupportResistanceLevel.price_level.desc()).limit(count).all()
            
            # Get nearest resistances above current price
            resistances = base_query.filter(
                and_(
                    SupportResistanceLevel.level_type == 'resistance',
                    SupportResistanceLevel.price_level > current_price
                )
            ).order_by(SupportResistanceLevel.price_level.asc()).limit(count).all()
            
            return {
                'current_price': current_price,
                'nearest_supports': [s.to_dict() for s in supports],
                'nearest_resistances': [r.to_dict() for r in resistances]
            }
            
        finally:
            session.close()