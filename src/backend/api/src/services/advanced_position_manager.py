#!/usr/bin/env python3
"""
Advanced Position Manager with Dynamic Doubling Strategy
Implements the complete trading strategy with liquidation clusters and position doubling
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)

class PositionStatus(Enum):
    """Position status"""
    OPEN = "open"
    PARTIAL_CLOSED = "partial_closed"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class PositionStage(Enum):
    """Position scaling stages"""
    INITIAL = 1     # 20X leverage
    DOUBLED_10X = 2 # 10X leverage
    DOUBLED_5X = 3  # 5X leverage
    DOUBLED_2X = 4  # 2X leverage
    MARGIN_ADDED = 5  # Final margin addition

@dataclass
class LiquidationCluster:
    """Liquidation cluster from KingFisher"""
    price_level: Decimal
    cluster_type: str  # "above" or "below"
    strength: float
    volume: float
    distance_from_entry: Decimal
    last_updated: datetime

@dataclass
class AdvancedPosition:
    """Advanced position with complete strategy tracking"""
    position_id: str
    symbol: str
    
    # Current position state
    current_entry_price: Decimal  # Weighted average entry after doubling
    total_position_size: Decimal  # Total position size
    total_margin_invested: Decimal  # Total margin invested (X)
    current_leverage: int  # Current effective leverage
    current_stage: PositionStage
    
    # Original position (for tracking)
    original_entry_price: Decimal
    original_margin: Decimal
    original_leverage: int
    
    # Take profit tracking
    current_tp_target: Decimal  # 175% of total margin
    current_tp_price: Decimal  # Price to hit for TP
    first_tp_triggered: bool = False
    partial_close_percentage: float = 0.0
    
    # Trailing stop
    max_price_reached: Decimal = field(default_factory=Decimal)
    trailing_stop_price: Optional[Decimal] = None
    trailing_stop_percentage: Decimal = Decimal("0.02")  # 2%
    
    # Liquidation clusters (2 above, 2 below)
    clusters_above: List[LiquidationCluster] = field(default_factory=list)
    clusters_below: List[LiquidationCluster] = field(default_factory=list)
    
    # Position doubling history
    doubling_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    status: PositionStatus = PositionStatus.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_cluster_update: Optional[datetime] = None

class AdvancedPositionManager:
    """
    Advanced position manager with complete strategy:
    - Initial entry at 20X with TP at 175% of margin
    - Track 2 clusters above and 2 below
    - Double position at lower clusters with 10X, 5X, 2X
    - Recalculate TP for combined position after doubling
    - Exit at upper clusters after TP hit
    """
    
    def __init__(self):
        self.active_positions: Dict[str, AdvancedPosition] = {}
        self.kingfisher_service = None
        self._running = False
        self.cluster_update_task = None
        
        # Strategy parameters
        self.tp_percentage = Decimal("1.75")  # 175% of margin
        self.partial_close_ratio = 0.5  # Close 50% at TP
        self.trailing_stop_percentage = Decimal("0.02")  # 2%
        
        # Leverage stages for doubling
        self.leverage_stages = {
            PositionStage.INITIAL: 20,
            PositionStage.DOUBLED_10X: 10,
            PositionStage.DOUBLED_5X: 5,
            PositionStage.DOUBLED_2X: 2
        }
        
        logger.info("Advanced Position Manager initialized")
    
    async def open_position(self, symbol: str, entry_price: Decimal, 
                           margin: Decimal, leverage: int = 20) -> AdvancedPosition:
        """
        Open initial position with strategy setup
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            margin: Initial margin (X)
            leverage: Initial leverage (default 20X)
        """
        position_id = f"POS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"
        
        # Calculate initial position
        position_size = margin * leverage
        
        # Calculate first take profit
        tp_target = margin * self.tp_percentage  # 175% of margin
        profit_needed = tp_target - margin
        price_move_percentage = profit_needed / position_size
        tp_price = entry_price * (Decimal("1") + price_move_percentage)
        
        position = AdvancedPosition(
            position_id=position_id,
            symbol=symbol,
            current_entry_price=entry_price,
            total_position_size=position_size,
            total_margin_invested=margin,
            current_leverage=leverage,
            current_stage=PositionStage.INITIAL,
            original_entry_price=entry_price,
            original_margin=margin,
            original_leverage=leverage,
            current_tp_target=tp_target,
            current_tp_price=tp_price,
            max_price_reached=entry_price
        )
        
        # Get initial liquidation clusters (2 above, 2 below)
        await self._update_liquidation_clusters(position)
        
        self.active_positions[position_id] = position
        
        logger.info(f"Opened position {position_id}:")
        logger.info(f"  Entry: {entry_price}, Margin: {margin}, Leverage: {leverage}X")
        logger.info(f"  Position Size: {position_size}")
        logger.info(f"  First TP: {tp_price} (175% of margin = {tp_target})")
        logger.info(f"  Clusters: {len(position.clusters_above)} above, {len(position.clusters_below)} below")
        
        return position
    
    async def update_position(self, position_id: str, current_price: Decimal) -> Dict[str, Any]:
        """
        Update position with current price and execute strategy
        """
        if position_id not in self.active_positions:
            return {"error": "Position not found"}
        
        position = self.active_positions[position_id]
        actions = []
        
        # Update max price for trailing stop
        if current_price > position.max_price_reached:
            position.max_price_reached = current_price
            if position.first_tp_triggered:
                position.trailing_stop_price = current_price * (Decimal("1") - position.trailing_stop_percentage)
                actions.append(f"Updated trailing stop to {position.trailing_stop_price}")
        
        # Calculate current PnL
        price_change = current_price - position.current_entry_price
        current_pnl = price_change * position.total_position_size / position.current_entry_price
        
        # Check for first take profit (175% of total margin)
        if not position.first_tp_triggered and current_price >= position.current_tp_price:
            await self._execute_first_take_profit(position, current_price)
            actions.append(f"First TP hit at {current_price}: Closed 50%, looking for upper clusters")
        
        # If TP hit, check upper clusters for final exit
        if position.first_tp_triggered:
            upper_cluster_hit = await self._check_upper_cluster_exit(position, current_price)
            if upper_cluster_hit:
                await self._close_remaining_position(position, current_price, "Upper cluster reached")
                actions.append(f"Closed remaining position at upper cluster: {current_price}")
                return {"actions": actions, "status": "closed"}
            
            # Check trailing stop
            if position.trailing_stop_price and current_price <= position.trailing_stop_price:
                await self._close_remaining_position(position, current_price, "Trailing stop triggered")
                actions.append(f"Trailing stop triggered at {current_price}")
                return {"actions": actions, "status": "closed"}
        
        # If price going down, check lower clusters for doubling
        if not position.first_tp_triggered:
            double_action = await self._check_and_execute_doubling(position, current_price)
            if double_action:
                actions.append(double_action)
        
        position.updated_at = datetime.now()
        
        return {
            "position_id": position_id,
            "current_price": float(current_price),
            "current_pnl": float(current_pnl),
            "current_tp_price": float(position.current_tp_price),
            "current_tp_target": float(position.current_tp_target),
            "stage": position.current_stage.name,
            "total_margin": float(position.total_margin_invested),
            "actions": actions,
            "status": position.status.value
        }
    
    async def _execute_first_take_profit(self, position: AdvancedPosition, current_price: Decimal):
        """Execute first take profit - close 50% and activate trailing stop"""
        close_amount = position.total_position_size * Decimal(str(self.partial_close_ratio))
        position.total_position_size -= close_amount
        position.partial_close_percentage = self.partial_close_ratio
        position.first_tp_triggered = True
        position.status = PositionStatus.PARTIAL_CLOSED
        
        # Activate trailing stop
        position.trailing_stop_price = current_price * (Decimal("1") - position.trailing_stop_percentage)
        
        logger.info(f"First TP executed for {position.position_id}:")
        logger.info(f"  Closed 50% at {current_price}")
        logger.info(f"  Remaining position: {position.total_position_size}")
        logger.info(f"  Trailing stop activated at {position.trailing_stop_price}")
    
    async def _check_and_execute_doubling(self, position: AdvancedPosition, 
                                         current_price: Decimal) -> Optional[str]:
        """Check if we should double position at lower clusters"""
        if not position.clusters_below:
            return None
        
        # Check if we hit a lower cluster
        for cluster in position.clusters_below:
            distance = abs(current_price - cluster.price_level) / current_price
            if distance < Decimal("0.002"):  # Within 0.2% of cluster
                # Determine next leverage stage
                next_stage, next_leverage = self._get_next_doubling_stage(position)
                
                if next_stage and next_leverage is not None:
                    # Execute position doubling
                    await self._double_position(position, current_price, next_leverage, next_stage)
                    return f"Doubled position at {current_price} with {next_leverage}X leverage"
        
        return None
    
    async def _double_position(self, position: AdvancedPosition, 
                              current_price: Decimal, new_leverage: int, 
                              new_stage: PositionStage):
        """
        Double the position with new leverage and recalculate everything
        """
        # Calculate new position addition
        if new_stage == PositionStage.MARGIN_ADDED:
            # Just add margin, don't change position size
            additional_margin = position.original_margin
            additional_size = Decimal("0")
        else:
            # Double with new leverage
            additional_margin = position.original_margin * 2  # Double the original margin
            additional_size = additional_margin * new_leverage
        
        # Update position with new weighted average
        old_value = position.total_position_size * position.current_entry_price
        new_value = additional_size * current_price
        new_total_size = position.total_position_size + additional_size
        
        # Calculate new weighted average entry
        if new_total_size > 0:
            position.current_entry_price = (old_value + new_value) / new_total_size
        
        position.total_position_size = new_total_size
        position.total_margin_invested += additional_margin
        position.current_stage = new_stage
        
        # Recalculate take profit for the combined position
        new_tp_target = position.total_margin_invested * self.tp_percentage
        profit_needed = new_tp_target - position.total_margin_invested
        
        # Calculate new TP price
        if position.total_position_size > 0:
            price_move_percentage = profit_needed / position.total_position_size
            position.current_tp_price = position.current_entry_price * (Decimal("1") + price_move_percentage)
            position.current_tp_target = new_tp_target
        
        # Reset TP trigger since we have a new combined position
        position.first_tp_triggered = False
        position.partial_close_percentage = 0
        
        # Update clusters (2 above, 2 below from new entry)
        await self._update_liquidation_clusters(position)
        
        # Record doubling history
        position.doubling_history.append({
            "timestamp": datetime.now().isoformat(),
            "price": float(current_price),
            "additional_margin": float(additional_margin),
            "additional_size": float(additional_size),
            "new_leverage": new_leverage,
            "stage": new_stage.name,
            "new_entry_avg": float(position.current_entry_price),
            "new_tp_price": float(position.current_tp_price)
        })
        
        logger.info(f"Position doubled for {position.position_id}:")
        logger.info(f"  Stage: {new_stage.name}, Leverage: {new_leverage}X")
        logger.info(f"  Additional margin: {additional_margin}, size: {additional_size}")
        logger.info(f"  New avg entry: {position.current_entry_price}")
        logger.info(f"  New TP: {position.current_tp_price} (175% of {position.total_margin_invested})")
    
    def _get_next_doubling_stage(self, position: AdvancedPosition) -> Tuple[Optional[PositionStage], Optional[int]]:
        """Get next doubling stage and leverage"""
        stage_progression = {
            PositionStage.INITIAL: (PositionStage.DOUBLED_10X, 10),
            PositionStage.DOUBLED_10X: (PositionStage.DOUBLED_5X, 5),
            PositionStage.DOUBLED_5X: (PositionStage.DOUBLED_2X, 2),
            PositionStage.DOUBLED_2X: (PositionStage.MARGIN_ADDED, 0),  # Just add margin
        }
        
        if position.current_stage in stage_progression:
            return stage_progression[position.current_stage]
        
        return None, None
    
    async def _check_upper_cluster_exit(self, position: AdvancedPosition, 
                                       current_price: Decimal) -> bool:
        """Check if we should exit at upper cluster after TP"""
        if not position.clusters_above:
            return False
        
        for cluster in position.clusters_above:
            distance = abs(current_price - cluster.price_level) / current_price
            if distance < Decimal("0.002"):  # Within 0.2% of cluster
                return True
        
        return False
    
    async def _close_remaining_position(self, position: AdvancedPosition, 
                                       exit_price: Decimal, reason: str):
        """Close remaining position"""
        position.status = PositionStatus.CLOSED
        final_pnl = (exit_price - position.current_entry_price) * position.total_position_size / position.current_entry_price
        
        logger.info(f"Position {position.position_id} closed:")
        logger.info(f"  Reason: {reason}")
        logger.info(f"  Exit price: {exit_price}")
        logger.info(f"  Final PnL: {final_pnl}")
        
        del self.active_positions[position.position_id]
    
    async def _update_liquidation_clusters(self, position: AdvancedPosition):
        """Update liquidation clusters - 2 above and 2 below current price"""
        try:
            # This would integrate with KingFisher
            # For now, create mock clusters
            current_price = position.current_entry_price
            
            # Clusters above (resistance)
            position.clusters_above = [
                LiquidationCluster(
                    price_level=current_price * Decimal("1.03"),
                    cluster_type="above",
                    strength=0.7,
                    volume=1000000,
                    distance_from_entry=Decimal("0.03"),
                    last_updated=datetime.now()
                ),
                LiquidationCluster(
                    price_level=current_price * Decimal("1.05"),
                    cluster_type="above",
                    strength=0.8,
                    volume=1500000,
                    distance_from_entry=Decimal("0.05"),
                    last_updated=datetime.now()
                )
            ]
            
            # Clusters below (support) - for doubling
            position.clusters_below = [
                LiquidationCluster(
                    price_level=current_price * Decimal("0.97"),
                    cluster_type="below",
                    strength=0.6,
                    volume=800000,
                    distance_from_entry=Decimal("-0.03"),
                    last_updated=datetime.now()
                ),
                LiquidationCluster(
                    price_level=current_price * Decimal("0.95"),
                    cluster_type="below",
                    strength=0.8,
                    volume=1200000,
                    distance_from_entry=Decimal("-0.05"),
                    last_updated=datetime.now()
                )
            ]
            
            position.last_cluster_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating clusters: {e}")
    
    def get_position_details(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get complete position details"""
        if position_id not in self.active_positions:
            return None
        
        position = self.active_positions[position_id]
        
        return {
            "position_id": position.position_id,
            "symbol": position.symbol,
            "stage": position.current_stage.name,
            "status": position.status.value,
            "current_entry_avg": float(position.current_entry_price),
            "total_position_size": float(position.total_position_size),
            "total_margin_invested": float(position.total_margin_invested),
            "current_leverage": position.current_leverage,
            "current_tp_price": float(position.current_tp_price),
            "current_tp_target": float(position.current_tp_target),
            "first_tp_triggered": position.first_tp_triggered,
            "max_price": float(position.max_price_reached),
            "trailing_stop": float(position.trailing_stop_price) if position.trailing_stop_price else None,
            "clusters_above": [
                {"price": float(c.price_level), "strength": c.strength}
                for c in position.clusters_above
            ],
            "clusters_below": [
                {"price": float(c.price_level), "strength": c.strength}
                for c in position.clusters_below
            ],
            "doubling_history": position.doubling_history,
            "created_at": position.created_at.isoformat(),
            "updated_at": position.updated_at.isoformat()
        }

# Global instance
advanced_position_manager = AdvancedPositionManager()