#!/usr/bin/env python3
"""
Position Manager with Liquidation Cluster Integration
Implements the correct take profit and trailing stop strategy with KingFisher liquidation clusters
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

@dataclass
class LiquidationClusterTarget:
    """Liquidation cluster target from KingFisher"""
    price_level: Decimal
    cluster_strength: float
    cluster_type: str  # support/resistance
    last_updated: datetime
    volume_concentration: float

@dataclass
class ManagedPosition:
    """Enhanced position with cluster tracking"""
    position_id: str
    symbol: str
    entry_price: Decimal
    position_size: Decimal
    margin_used: Decimal  # X - the actual margin invested
    leverage: int
    current_stage: int
    
    # Profit taking
    first_take_profit_triggered: bool = False
    partial_close_percentage: float = 0.0  # How much has been closed
    
    # Trailing stop
    max_price_reached: Decimal = field(default_factory=Decimal)
    trailing_stop_price: Optional[Decimal] = None
    trailing_stop_percentage: Decimal = Decimal("0.02")  # 2% trailing stop
    
    # Liquidation clusters
    liquidation_clusters: List[LiquidationClusterTarget] = field(default_factory=list)
    last_cluster_update: Optional[datetime] = None
    cluster_update_interval: int = 600  # 10 minutes in seconds
    
    # Status
    status: PositionStatus = PositionStatus.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class PositionManagerWithClusters:
    """
    Position manager implementing the correct strategy:
    - First take profit at 175% of margin (close 50%)
    - Trailing stop of 2% from max price
    - Exit at liquidation clusters
    - Update clusters every 10 minutes
    """
    
    def __init__(self):
        self.active_positions: Dict[str, ManagedPosition] = {}
        self.kingfisher_service = None  # Will be injected
        self.cluster_update_task = None
        self._running = False
        
        # Strategy parameters
        self.first_tp_percentage = 1.75  # 175% of margin
        self.partial_close_ratio = 0.5   # Close 50% at first TP
        self.trailing_stop_percentage = 0.02  # 2% trailing stop
        
        logger.info("Position Manager with Clusters initialized")
    
    async def start(self, kingfisher_service):
        """Start the position manager with KingFisher service"""
        self.kingfisher_service = kingfisher_service
        self._running = True
        
        # Start cluster update task
        self.cluster_update_task = asyncio.create_task(self._cluster_update_loop())
        
        logger.info("Position manager started with cluster monitoring")
    
    async def stop(self):
        """Stop the position manager"""
        self._running = False
        if self.cluster_update_task:
            self.cluster_update_task.cancel()
            try:
                await self.cluster_update_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Position manager stopped")
    
    async def open_position(self, symbol: str, entry_price: Decimal, 
                           position_size: Decimal, margin_used: Decimal, 
                           leverage: int = 20) -> ManagedPosition:
        """
        Open a new position with proper tracking
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            position_size: Total position size (margin * leverage)
            margin_used: Actual margin invested (X in the strategy)
            leverage: Leverage used (default 20X)
        """
        position_id = f"POS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"
        
        position = ManagedPosition(
            position_id=position_id,
            symbol=symbol,
            entry_price=entry_price,
            position_size=position_size,
            margin_used=margin_used,
            leverage=leverage,
            current_stage=1,
            max_price_reached=entry_price
        )
        
        # Get initial liquidation clusters
        clusters = await self._fetch_liquidation_clusters(symbol)
        position.liquidation_clusters = clusters
        position.last_cluster_update = datetime.now()
        
        self.active_positions[position_id] = position
        
        logger.info(f"Opened position {position_id}: {symbol} @ {entry_price}, "
                   f"Margin: {margin_used}, Size: {position_size}, Leverage: {leverage}X")
        
        return position
    
    async def update_position(self, position_id: str, current_price: Decimal) -> Dict[str, Any]:
        """
        Update position with current price and check for exits
        
        Returns:
            Dict with actions taken
        """
        if position_id not in self.active_positions:
            return {"error": "Position not found"}
        
        position = self.active_positions[position_id]
        actions_taken = []
        
        # Update max price for trailing stop
        if current_price > position.max_price_reached:
            position.max_price_reached = current_price
            position.trailing_stop_price = current_price * (Decimal("1") - position.trailing_stop_percentage)
            actions_taken.append(f"Updated max price to {current_price}, trailing stop at {position.trailing_stop_price}")
        
        # Calculate current profit
        price_change = current_price - position.entry_price
        profit_percentage = (price_change / position.entry_price) * position.leverage
        current_pnl = price_change * position.position_size / position.entry_price
        
        # Check first take profit (175% of margin)
        profit_target = position.margin_used * Decimal(str(self.first_tp_percentage))
        
        if not position.first_take_profit_triggered and current_pnl >= profit_target:
            # Trigger first take profit - close 50% of position
            await self._execute_partial_close(position, self.partial_close_ratio)
            position.first_take_profit_triggered = True
            actions_taken.append(f"First TP triggered at {current_price}, closed 50% of position")
            
            # After partial close, activate trailing stop
            position.trailing_stop_price = current_price * (Decimal("1") - position.trailing_stop_percentage)
            actions_taken.append(f"Trailing stop activated at {position.trailing_stop_price}")
        
        # Check liquidation cluster exit
        if position.first_take_profit_triggered:
            cluster_exit = await self._check_cluster_exit(position, current_price)
            if cluster_exit:
                await self._close_position(position, current_price, "Liquidation cluster exit")
                actions_taken.append(f"Closed at liquidation cluster: {current_price}")
        
        # Check trailing stop
        if position.trailing_stop_price and current_price <= position.trailing_stop_price:
            await self._close_position(position, current_price, "Trailing stop triggered")
            actions_taken.append(f"Trailing stop triggered at {current_price}")
        
        # Update position timestamp
        position.updated_at = datetime.now()
        
        return {
            "position_id": position_id,
            "current_price": float(current_price),
            "profit_percentage": float(profit_percentage * 100),
            "current_pnl": float(current_pnl),
            "max_price": float(position.max_price_reached),
            "trailing_stop": float(position.trailing_stop_price) if position.trailing_stop_price else None,
            "actions": actions_taken,
            "status": position.status.value
        }
    
    async def _execute_partial_close(self, position: ManagedPosition, close_ratio: float):
        """Execute partial position close"""
        close_amount = position.position_size * Decimal(str(close_ratio))
        position.position_size -= close_amount
        position.partial_close_percentage += close_ratio
        position.status = PositionStatus.PARTIAL_CLOSED
        
        logger.info(f"Partial close executed for {position.position_id}: "
                   f"Closed {close_ratio*100}% ({close_amount}), "
                   f"Remaining: {position.position_size}")
    
    async def _close_position(self, position: ManagedPosition, exit_price: Decimal, reason: str):
        """Close entire position"""
        position.status = PositionStatus.CLOSED
        final_pnl = (exit_price - position.entry_price) * position.position_size / position.entry_price
        
        logger.info(f"Position {position.position_id} closed: {reason}, "
                   f"Exit: {exit_price}, PnL: {final_pnl}")
        
        # Remove from active positions
        del self.active_positions[position.position_id]
    
    async def _check_cluster_exit(self, position: ManagedPosition, current_price: Decimal) -> bool:
        """
        Check if price has reached a liquidation cluster target
        
        Returns:
            True if should exit at cluster
        """
        if not position.liquidation_clusters:
            return False
        
        for cluster in position.liquidation_clusters:
            # Check if price is within 0.1% of cluster level
            distance = abs(current_price - cluster.price_level) / current_price
            if distance < Decimal("0.001"):  # Within 0.1%
                logger.info(f"Price {current_price} reached liquidation cluster at {cluster.price_level}")
                return True
        
        return False
    
    async def _fetch_liquidation_clusters(self, symbol: str) -> List[LiquidationClusterTarget]:
        """Fetch liquidation clusters from KingFisher"""
        try:
            if not self.kingfisher_service:
                return []
            
            # Get support/resistance levels from KingFisher
            # This would integrate with actual KingFisher service
            # For now, return mock clusters based on typical levels
            
            # Mock implementation - replace with actual KingFisher integration
            clusters = []
            
            # Example: Create mock clusters around current price
            # In production, this would call KingFisher's support_resistance_service
            base_price = 50000  # Example base price
            cluster_levels = [
                (base_price * Decimal("0.95"), "support", 0.8),   # Strong support
                (base_price * Decimal("0.97"), "support", 0.6),   # Medium support
                (base_price * Decimal("1.03"), "resistance", 0.6), # Medium resistance
                (base_price * Decimal("1.05"), "resistance", 0.8), # Strong resistance
            ]
            
            for price, cluster_type, strength in cluster_levels:
                cluster = LiquidationClusterTarget(
                    price_level=price,
                    cluster_strength=strength,
                    cluster_type=cluster_type,
                    last_updated=datetime.now(),
                    volume_concentration=strength * 1000000  # Mock volume
                )
                clusters.append(cluster)
            
            # Sort by distance from current price
            clusters.sort(key=lambda x: x.cluster_strength, reverse=True)
            
            return clusters[:5]  # Return top 5 strongest clusters
            
        except Exception as e:
            logger.error(f"Error fetching liquidation clusters for {symbol}: {e}")
            return []
    
    async def _cluster_update_loop(self):
        """Background task to update liquidation clusters every 10 minutes"""
        while self._running:
            try:
                for position in list(self.active_positions.values()):
                    # Check if update needed (10 minutes passed)
                    if position.last_cluster_update:
                        time_since_update = (datetime.now() - position.last_cluster_update).total_seconds()
                        if time_since_update >= position.cluster_update_interval:
                            # Update clusters
                            new_clusters = await self._fetch_liquidation_clusters(position.symbol)
                            position.liquidation_clusters = new_clusters
                            position.last_cluster_update = datetime.now()
                            
                            logger.info(f"Updated liquidation clusters for {position.symbol}: "
                                      f"{len(new_clusters)} clusters found")
                
                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cluster update loop: {e}")
                await asyncio.sleep(30)
    
    def get_position_status(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get current position status"""
        if position_id not in self.active_positions:
            return None
        
        position = self.active_positions[position_id]
        
        return {
            "position_id": position.position_id,
            "symbol": position.symbol,
            "entry_price": float(position.entry_price),
            "current_size": float(position.position_size),
            "margin_used": float(position.margin_used),
            "leverage": position.leverage,
            "stage": position.current_stage,
            "first_tp_triggered": position.first_take_profit_triggered,
            "partial_close_percentage": position.partial_close_percentage,
            "max_price": float(position.max_price_reached),
            "trailing_stop": float(position.trailing_stop_price) if position.trailing_stop_price else None,
            "liquidation_clusters": [
                {
                    "price": float(c.price_level),
                    "strength": c.cluster_strength,
                    "type": c.cluster_type
                } for c in position.liquidation_clusters[:3]  # Top 3 clusters
            ],
            "last_cluster_update": position.last_cluster_update.isoformat() if position.last_cluster_update else None,
            "status": position.status.value
        }

# Global instance
position_manager = PositionManagerWithClusters()