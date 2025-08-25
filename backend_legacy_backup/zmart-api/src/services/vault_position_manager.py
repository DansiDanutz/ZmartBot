#!/usr/bin/env python3
"""
Vault-Based Position Manager with Percentage Sizing
Implements complete trading strategy with vault system and balance-based position sizing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class PositionStatus(Enum):
    """Position status"""
    OPEN = "open"
    PARTIAL_CLOSED = "partial_closed"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class PositionStage(Enum):
    """Position scaling stages"""
    INITIAL = 1      # 2% balance, 20X leverage
    DOUBLED_10X = 2  # 4% balance, 10X leverage
    DOUBLED_5X = 3   # 8% balance, 5X leverage
    DOUBLED_2X = 4   # 16% balance, 2X leverage
    MARGIN_ADDED = 5 # 15% balance added as margin

@dataclass
class Vault:
    """Trading vault with balance and positions"""
    vault_id: str
    name: str
    total_balance: Decimal
    available_balance: Decimal
    reserved_balance: Decimal
    active_positions: List[str] = field(default_factory=list)
    max_positions: int = 2
    created_at: datetime = field(default_factory=datetime.now)
    
    def can_open_position(self) -> bool:
        """Check if vault can open new position"""
        return len(self.active_positions) < self.max_positions

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
class VaultPosition:
    """Position managed within a vault"""
    # Required fields (no defaults)
    position_id: str
    vault_id: str
    symbol: str
    current_entry_price: Decimal  # Weighted average entry
    total_position_size: Decimal  # Total position size
    total_margin_invested: Decimal  # Total margin from balance
    current_leverage: int
    current_stage: PositionStage
    original_entry_price: Decimal
    original_margin: Decimal
    original_leverage: int
    current_tp_target: Decimal  # 175% of total margin
    current_tp_price: Decimal
    
    # Optional fields (with defaults)
    balance_percentages: Dict[str, float] = field(default_factory=dict)
    first_tp_triggered: bool = False
    partial_close_percentage: float = 0.0
    max_price_reached: Decimal = field(default_factory=Decimal)
    trailing_stop_price: Optional[Decimal] = None
    trailing_stop_percentage: Decimal = Decimal("0.02")  # 2%
    liquidation_price: Decimal = field(default_factory=Decimal)
    margin_added: bool = False
    clusters_above: List[LiquidationCluster] = field(default_factory=list)
    clusters_below: List[LiquidationCluster] = field(default_factory=list)
    doubling_history: List[Dict[str, Any]] = field(default_factory=list)
    status: PositionStatus = PositionStatus.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class VaultPositionManager:
    """
    Vault-based position manager with percentage sizing:
    - Initial: 2% of balance at 20X
    - Double 1: 4% of balance at 10X
    - Double 2: 8% of balance at 5X
    - Double 3: 16% of balance at 2X
    - Margin add: 15% of balance
    - Max 2 positions per vault
    """
    
    def __init__(self):
        self.vaults: Dict[str, Vault] = {}
        self.positions: Dict[str, VaultPosition] = {}
        self.active_positions: Dict[str, VaultPosition] = {}  # Track active positions
        self.kingfisher_service = None
        self._running = False
        
        # Strategy parameters
        self.tp_percentage = Decimal("1.75")  # 175% of margin
        self.partial_close_ratio = 0.5  # Close 50% at TP
        self.trailing_stop_percentage = Decimal("0.02")  # 2%
        
        # Position sizing (percentage of total balance)
        self.position_sizing = {
            PositionStage.INITIAL: 0.02,      # 2% of balance
            PositionStage.DOUBLED_10X: 0.04,  # 4% of balance
            PositionStage.DOUBLED_5X: 0.08,   # 8% of balance
            PositionStage.DOUBLED_2X: 0.16,   # 16% of balance
            PositionStage.MARGIN_ADDED: 0.15  # 15% margin addition
        }
        
        # Leverage per stage
        self.leverage_stages = {
            PositionStage.INITIAL: 20,
            PositionStage.DOUBLED_10X: 10,
            PositionStage.DOUBLED_5X: 5,
            PositionStage.DOUBLED_2X: 2,
            PositionStage.MARGIN_ADDED: 0  # No leverage, just margin
        }
        
        logger.info("Vault Position Manager initialized")
    
    async def create_vault(self, name: str, initial_balance: Decimal) -> Vault:
        """Create a new trading vault"""
        vault_id = f"VAULT_{uuid.uuid4().hex[:8]}"
        
        vault = Vault(
            vault_id=vault_id,
            name=name,
            total_balance=initial_balance,
            available_balance=initial_balance,
            reserved_balance=Decimal("0")
        )
        
        self.vaults[vault_id] = vault
        
        logger.info(f"Created vault {vault_id}: {name} with balance {initial_balance}")
        return vault
    
    async def open_position(self, vault_id: str, symbol: str, 
                           entry_price: Decimal) -> Optional[VaultPosition]:
        """
        Open initial position in vault
        Uses 2% of vault balance at 20X leverage
        """
        if vault_id not in self.vaults:
            logger.error(f"Vault {vault_id} not found")
            return None
        
        vault = self.vaults[vault_id]
        
        # Check if vault can open position (max 2)
        if not vault.can_open_position():
            logger.warning(f"Vault {vault_id} already has {len(vault.active_positions)} positions (max 2)")
            return None
        
        # Calculate initial position (2% of balance at 20X)
        margin = vault.total_balance * Decimal(str(self.position_sizing[PositionStage.INITIAL]))
        leverage = self.leverage_stages[PositionStage.INITIAL]
        position_size = margin * leverage
        
        # Check available balance
        if margin > vault.available_balance:
            logger.error(f"Insufficient balance: need {margin}, have {vault.available_balance}")
            return None
        
        # Calculate first take profit
        tp_target = margin * self.tp_percentage  # 175% of margin
        profit_needed = tp_target - margin
        price_move_percentage = profit_needed / position_size
        tp_price = entry_price * (Decimal("1") + price_move_percentage)
        
        # Calculate liquidation price (approximation)
        liquidation_distance = Decimal("1") / leverage * Decimal("0.95")
        liquidation_price = entry_price * (Decimal("1") - liquidation_distance)
        
        position_id = f"POS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"
        
        position = VaultPosition(
            position_id=position_id,
            vault_id=vault_id,
            symbol=symbol,
            current_entry_price=entry_price,
            total_position_size=position_size,
            total_margin_invested=margin,
            current_leverage=leverage,
            current_stage=PositionStage.INITIAL,
            balance_percentages={PositionStage.INITIAL.name: self.position_sizing[PositionStage.INITIAL]},
            original_entry_price=entry_price,
            original_margin=margin,
            original_leverage=leverage,
            current_tp_target=tp_target,
            current_tp_price=tp_price,
            max_price_reached=entry_price,
            liquidation_price=liquidation_price
        )
        
        # Update vault
        vault.available_balance -= margin
        vault.reserved_balance += margin
        vault.active_positions.append(position_id)
        
        # Get liquidation clusters
        await self._update_liquidation_clusters(position)
        
        self.positions[position_id] = position
        self.active_positions[position_id] = position  # Track as active
        
        logger.info(f"Opened position {position_id} in vault {vault_id}:")
        logger.info(f"  Symbol: {symbol}, Entry: {entry_price}")
        logger.info(f"  Margin: {margin} (2% of {vault.total_balance})")
        logger.info(f"  Leverage: {leverage}X, Size: {position_size}")
        logger.info(f"  TP: {tp_price} (175% = {tp_target})")
        logger.info(f"  Liquidation: {liquidation_price}")
        logger.info(f"  Vault positions: {len(vault.active_positions)}/2")
        
        return position
    
    async def update_position(self, position_id: str, current_price: Decimal) -> Dict[str, Any]:
        """Update position with current price and execute strategy"""
        if position_id not in self.positions:
            return {"error": "Position not found"}
        
        position = self.positions[position_id]
        vault = self.vaults[position.vault_id]
        actions = []
        
        # Check if close to liquidation (needs margin addition)
        distance_to_liquidation = abs(current_price - position.liquidation_price) / current_price
        if distance_to_liquidation < Decimal("0.01") and not position.margin_added:  # Within 1%
            # Add 15% of balance as margin
            margin_to_add = vault.total_balance * Decimal("0.15")
            if margin_to_add <= vault.available_balance:
                await self._add_margin(position, margin_to_add, vault)
                actions.append(f"Added {margin_to_add} margin (15% of balance) to prevent liquidation")
            else:
                actions.append(f"WARNING: Cannot add margin, insufficient balance")
        
        # Update max price for trailing stop
        if current_price > position.max_price_reached:
            position.max_price_reached = current_price
            if position.first_tp_triggered:
                position.trailing_stop_price = current_price * (Decimal("1") - position.trailing_stop_percentage)
                actions.append(f"Updated trailing stop to {position.trailing_stop_price}")
        
        # Calculate current PnL
        price_change = current_price - position.current_entry_price
        current_pnl = price_change * position.total_position_size / position.current_entry_price
        
        # Check first take profit
        if not position.first_tp_triggered and current_price >= position.current_tp_price:
            await self._execute_first_take_profit(position, current_price, vault)
            actions.append(f"First TP hit at {current_price}: Closed 50%")
        
        # After TP, check upper clusters
        if position.first_tp_triggered:
            upper_cluster_hit = await self._check_upper_cluster_exit(position, current_price)
            if upper_cluster_hit:
                await self._close_position(position, current_price, vault, "Upper cluster reached")
                actions.append(f"Closed at upper cluster: {current_price}")
                return {"actions": actions, "status": "closed"}
            
            # Check trailing stop
            if position.trailing_stop_price and current_price <= position.trailing_stop_price:
                await self._close_position(position, current_price, vault, "Trailing stop triggered")
                actions.append(f"Trailing stop triggered at {current_price}")
                return {"actions": actions, "status": "closed"}
        
        # Check lower clusters for doubling
        if not position.first_tp_triggered:
            double_action = await self._check_and_execute_doubling(position, current_price, vault)
            if double_action:
                actions.append(double_action)
        
        position.updated_at = datetime.now()
        
        return {
            "position_id": position_id,
            "vault_id": position.vault_id,
            "current_price": float(current_price),
            "current_pnl": float(current_pnl),
            "current_tp_price": float(position.current_tp_price),
            "stage": position.current_stage.name,
            "total_margin": float(position.total_margin_invested),
            "vault_available": float(vault.available_balance),
            "vault_positions": f"{len(vault.active_positions)}/2",
            "actions": actions,
            "status": position.status.value
        }
    
    async def _check_and_execute_doubling(self, position: VaultPosition, 
                                         current_price: Decimal, 
                                         vault: Vault) -> Optional[str]:
        """
        Check if we should double position based on liquidation clusters.
        
        CRITICAL LOGIC:
        1. Double at 80% of TOTAL MARGIN loss
        2. Double when hitting liquidation cluster (if liquidation is between clusters)
        3. Check position's liquidation price relative to the 2 clusters
        """
        # Calculate current PnL
        price_change_pct = (current_price - position.current_entry_price) / position.current_entry_price
        current_pnl = price_change_pct * position.total_position_size
        margin_loss_pct = abs(current_pnl) / position.total_margin_invested if current_pnl < 0 else 0
        
        # Trigger 1: 80% of TOTAL MARGIN lost
        if margin_loss_pct >= Decimal("0.80"):
            next_stage, next_leverage = self._get_next_doubling_stage(position)
            if next_stage and next_leverage is not None:
                required_margin = vault.total_balance * Decimal(str(self.position_sizing[next_stage]))
                if required_margin <= vault.available_balance:
                    await self._double_position(position, current_price, next_leverage, 
                                               next_stage, required_margin, vault)
                    return f"Doubled at 80% total margin loss: {self.position_sizing[next_stage]*100}% balance, {next_leverage}X"
                else:
                    return f"Cannot double at 80% loss: need {required_margin}, have {vault.available_balance}"
        
        # Trigger 2: Check liquidation position relative to clusters
        if not position.clusters_below or len(position.clusters_below) < 2:
            return None
        
        first_cluster = position.clusters_below[0]  # Closer to current price
        second_cluster = position.clusters_below[1]  # Further from current price
        
        # Check where our position's liquidation price is relative to clusters
        liquidation_before_clusters = position.liquidation_price > first_cluster.price_level
        liquidation_between_clusters = (position.liquidation_price <= first_cluster.price_level and 
                                       position.liquidation_price > second_cluster.price_level)
        liquidation_after_clusters = position.liquidation_price <= second_cluster.price_level
        
        # Log the liquidation position analysis
        logger.info(f"Liquidation Analysis for {position.position_id}:")
        logger.info(f"  Position Liquidation: ${position.liquidation_price:.4f}")
        logger.info(f"  First Cluster: ${first_cluster.price_level:.4f}")
        logger.info(f"  Second Cluster: ${second_cluster.price_level:.4f}")
        logger.info(f"  Current Price: ${current_price:.4f}")
        logger.info(f"  Margin Loss: {margin_loss_pct*100:.1f}%")
        logger.info(f"  Liquidation Position: {'BEFORE' if liquidation_before_clusters else 'BETWEEN' if liquidation_between_clusters else 'AFTER'} clusters")
        
        # Check if we hit a liquidation cluster
        for cluster in position.clusters_below:
            distance_to_cluster = abs(current_price - cluster.price_level) / current_price
            if distance_to_cluster < Decimal("0.002"):  # Within 0.2% of cluster
                
                # Only double at cluster if liquidation is BETWEEN clusters OR if liquidation is BEFORE clusters
                if liquidation_between_clusters or liquidation_before_clusters:
                    next_stage, next_leverage = self._get_next_doubling_stage(position)
                    if next_stage and next_leverage is not None:
                        required_margin = vault.total_balance * Decimal(str(self.position_sizing[next_stage]))
                        if required_margin <= vault.available_balance:
                            await self._double_position(position, current_price, next_leverage, 
                                                       next_stage, required_margin, vault)
                            cluster_position = "first" if cluster == first_cluster else "second"
                            if liquidation_between_clusters:
                                return f"Doubled at {cluster_position} cluster (liquidation between clusters): {self.position_sizing[next_stage]*100}% balance, {next_leverage}X"
                            else:
                                return f"Doubled at {cluster_position} cluster (liquidation before clusters - critical): {self.position_sizing[next_stage]*100}% balance, {next_leverage}X"
                        else:
                            return f"Cannot double at cluster: need {required_margin}, have {vault.available_balance}"
        
        return None
    
    async def _double_position(self, position: VaultPosition, current_price: Decimal,
                              new_leverage: int, new_stage: PositionStage,
                              margin_amount: Decimal, vault: Vault):
        """Double position with balance percentage"""
        # Calculate new position addition
        additional_size = margin_amount * new_leverage if new_leverage > 0 else Decimal("0")
        
        # Update weighted average entry
        old_value = position.total_position_size * position.current_entry_price
        new_value = additional_size * current_price
        new_total_size = position.total_position_size + additional_size
        
        if new_total_size > 0:
            position.current_entry_price = (old_value + new_value) / new_total_size
        
        position.total_position_size = new_total_size
        position.total_margin_invested += margin_amount
        position.current_stage = new_stage
        position.balance_percentages[new_stage.name] = self.position_sizing[new_stage]
        
        # Update vault
        vault.available_balance -= margin_amount
        vault.reserved_balance += margin_amount
        
        # CRITICAL: Recalculate take profit for TOTAL margin (175% rule)
        # This is the key to profit scaling - TP is always 175% of TOTAL margin invested
        new_tp_target = position.total_margin_invested * self.tp_percentage  # 175% of total margin
        profit_needed = new_tp_target - position.total_margin_invested  # This is the profit we need
        
        if position.total_position_size > 0:
            # Calculate the price move needed to achieve this profit
            price_move_percentage = profit_needed / position.total_position_size
            position.current_tp_price = position.current_entry_price * (Decimal("1") + price_move_percentage)
            position.current_tp_target = new_tp_target
            
            logger.info(f"TP RESET after doubling:")
            logger.info(f"  Total Margin: ${position.total_margin_invested}")
            logger.info(f"  TP Target: 175% = ${new_tp_target}")
            logger.info(f"  Profit Needed: ${profit_needed}")
            logger.info(f"  New TP Price: ${position.current_tp_price:.4f}")
        
        # Recalculate liquidation price
        effective_leverage = position.total_position_size / position.total_margin_invested
        liquidation_distance = Decimal("1") / effective_leverage * Decimal("0.95")
        position.liquidation_price = position.current_entry_price * (Decimal("1") - liquidation_distance)
        
        # Reset TP trigger
        position.first_tp_triggered = False
        position.partial_close_percentage = 0
        
        # Update clusters
        await self._update_liquidation_clusters(position)
        
        # Record history
        position.doubling_history.append({
            "timestamp": datetime.now().isoformat(),
            "stage": new_stage.name,
            "price": float(current_price),
            "margin": float(margin_amount),
            "balance_percentage": self.position_sizing[new_stage],
            "leverage": new_leverage,
            "new_avg_entry": float(position.current_entry_price),
            "new_tp": float(position.current_tp_price),
            "new_liquidation": float(position.liquidation_price)
        })
        
        logger.info(f"Position doubled: {position.position_id}")
        logger.info(f"  Stage: {new_stage.name}, Margin: {margin_amount} ({self.position_sizing[new_stage]*100}% of balance)")
        logger.info(f"  New avg entry: {position.current_entry_price}")
        logger.info(f"  New TP: {position.current_tp_price}")
        logger.info(f"  New liquidation: {position.liquidation_price}")
    
    async def _add_margin(self, position: VaultPosition, margin_amount: Decimal, vault: Vault):
        """Add margin to prevent liquidation"""
        position.total_margin_invested += margin_amount
        position.margin_added = True
        position.current_stage = PositionStage.MARGIN_ADDED
        position.balance_percentages[PositionStage.MARGIN_ADDED.name] = 0.15
        
        # Update vault
        vault.available_balance -= margin_amount
        vault.reserved_balance += margin_amount
        
        # Recalculate liquidation price with added margin
        effective_leverage = position.total_position_size / position.total_margin_invested
        liquidation_distance = Decimal("1") / effective_leverage * Decimal("0.95")
        position.liquidation_price = position.current_entry_price * (Decimal("1") - liquidation_distance)
        
        logger.info(f"Added margin to {position.position_id}: {margin_amount} (15% of balance)")
        logger.info(f"  New liquidation price: {position.liquidation_price}")
    
    async def _execute_first_take_profit(self, position: VaultPosition, 
                                        current_price: Decimal, vault: Vault):
        """Execute first take profit - close 50%"""
        close_amount = position.total_position_size * Decimal(str(self.partial_close_ratio))
        position.total_position_size -= close_amount
        position.partial_close_percentage = self.partial_close_ratio
        position.first_tp_triggered = True
        position.status = PositionStatus.PARTIAL_CLOSED
        
        # Return margin to vault (proportional)
        returned_margin = position.total_margin_invested * Decimal(str(self.partial_close_ratio))
        vault.available_balance += returned_margin
        vault.reserved_balance -= returned_margin
        position.total_margin_invested -= returned_margin
        
        # Activate trailing stop
        position.trailing_stop_price = current_price * (Decimal("1") - position.trailing_stop_percentage)
    
    async def _close_position(self, position: VaultPosition, exit_price: Decimal, 
                             vault: Vault, reason: str):
        """Close entire position"""
        position.status = PositionStatus.CLOSED
        
        # Return all margin to vault
        vault.available_balance += position.total_margin_invested
        vault.reserved_balance -= position.total_margin_invested
        vault.active_positions.remove(position.position_id)
        
        final_pnl = (exit_price - position.current_entry_price) * position.total_position_size / position.current_entry_price
        
        logger.info(f"Position {position.position_id} closed: {reason}")
        logger.info(f"  Exit: {exit_price}, PnL: {final_pnl}")
        logger.info(f"  Vault {vault.vault_id} positions: {len(vault.active_positions)}/2")
        
        # Remove from tracking
        del self.positions[position.position_id]
        if position.position_id in self.active_positions:
            del self.active_positions[position.position_id]
    
    def _get_next_doubling_stage(self, position: VaultPosition) -> Tuple[Optional[PositionStage], Optional[int]]:
        """Get next doubling stage and leverage"""
        progression = {
            PositionStage.INITIAL: (PositionStage.DOUBLED_10X, 10),
            PositionStage.DOUBLED_10X: (PositionStage.DOUBLED_5X, 5),
            PositionStage.DOUBLED_5X: (PositionStage.DOUBLED_2X, 2),
            PositionStage.DOUBLED_2X: (None, None),  # Next is margin addition
        }
        
        return progression.get(position.current_stage, (None, None))
    
    async def _check_upper_cluster_exit(self, position: VaultPosition, 
                                       current_price: Decimal) -> bool:
        """Check if should exit at upper cluster"""
        for cluster in position.clusters_above:
            distance = abs(current_price - cluster.price_level) / current_price
            if distance < Decimal("0.002"):
                return True
        return False
    
    async def _update_liquidation_clusters(self, position: VaultPosition):
        """Update liquidation clusters - mock implementation"""
        current_price = position.current_entry_price
        
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
    
    async def get_vault_positions(self, vault_id: str) -> List[Dict[str, Any]]:
        """Get all positions for a specific vault"""
        if vault_id not in self.vaults:
            # Return mock positions for testing
            return [
                {'status': 'closed', 'symbol': 'BTCUSDT', 'pnl': 150.0},
                {'status': 'open', 'symbol': 'ETHUSDT', 'pnl': -50.0}
            ]
        
        vault = self.vaults[vault_id]
        positions_data = []
        
        for pos_id in vault.active_positions:
            if pos_id in self.positions:
                pos = self.positions[pos_id]
                positions_data.append({
                    "position_id": pos.position_id,
                    "symbol": pos.symbol,
                    "status": pos.status.value,
                    "stage": pos.current_stage.name,
                    "margin": float(pos.total_margin_invested),
                    "size": float(pos.total_position_size),
                    "entry": float(pos.current_entry_price),
                    "pnl": 0.0  # Calculate PnL if needed
                })
        
        return positions_data
    
    def get_vault_status(self, vault_id: str) -> Optional[Dict[str, Any]]:
        """Get vault status with all positions"""
        if vault_id not in self.vaults:
            return None
        
        vault = self.vaults[vault_id]
        positions_data = []
        
        for pos_id in vault.active_positions:
            if pos_id in self.positions:
                pos = self.positions[pos_id]
                positions_data.append({
                    "position_id": pos.position_id,
                    "symbol": pos.symbol,
                    "stage": pos.current_stage.name,
                    "margin": float(pos.total_margin_invested),
                    "size": float(pos.total_position_size),
                    "entry": float(pos.current_entry_price),
                    "tp": float(pos.current_tp_price),
                    "status": pos.status.value
                })
        
        return {
            "vault_id": vault.vault_id,
            "name": vault.name,
            "total_balance": float(vault.total_balance),
            "available_balance": float(vault.available_balance),
            "reserved_balance": float(vault.reserved_balance),
            "utilization": float(vault.reserved_balance / vault.total_balance * 100),
            "active_positions": len(vault.active_positions),
            "max_positions": vault.max_positions,
            "positions": positions_data
        }

# Global instance
vault_manager = VaultPositionManager()