"""
Trade Strategy Module - Vault Manager Service
============================================

Advanced vault management with CORRECTED profit calculation logic.
Manages multiple trading vaults with proper risk allocation and performance tracking.

Author: Manus AI
Version: 1.0 Professional Edition - CORRECTED PROFIT CALCULATIONS
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from redis import Redis

from ..core.config import settings, config_manager
from ..models.base import BaseRepository
from ..models.vaults import (
    Vault, VaultCreate, VaultUpdate, VaultStatus,
    VaultPerformance, VaultPerformanceCreate
)
from ..models.positions import Position, PositionScale, PositionStatus


class VaultAllocationStrategy(str, Enum):
    """Vault allocation strategies."""
    EQUAL_WEIGHT = "equal_weight"
    PERFORMANCE_BASED = "performance_based"
    RISK_ADJUSTED = "risk_adjusted"
    DYNAMIC = "dynamic"


@dataclass
class VaultMetrics:
    """Vault performance metrics with corrected profit calculations."""
    vault_id: str
    
    # Balance metrics
    initial_balance: Decimal
    current_balance: Decimal
    total_invested: Decimal  # CORRECTED: Total across all positions
    available_balance: Decimal
    
    # Position metrics
    active_positions: int
    total_positions_opened: int
    positions_closed: int
    
    # Performance metrics (CORRECTED)
    total_profit_realized: Decimal
    total_profit_targets: Decimal  # 75% of total invested across all positions
    unrealized_pnl: Decimal
    
    # Risk metrics
    max_drawdown: Decimal
    current_drawdown: Decimal
    risk_utilization: Decimal  # Percentage of vault at risk
    
    # Efficiency metrics
    win_rate: Decimal
    average_profit_per_trade: Decimal
    profit_factor: Decimal
    sharpe_ratio: Decimal
    
    # Timestamps
    last_updated: datetime
    performance_period_days: int


@dataclass
class VaultAllocation:
    """Vault allocation recommendation."""
    vault_id: str
    recommended_allocation: Decimal
    current_allocation: Decimal
    allocation_change: Decimal
    reasoning: str
    risk_score: Decimal
    expected_return: Decimal


class VaultManagerService:
    """
    Advanced vault management service with CORRECTED profit calculations.
    
    Key Correction: All profit calculations and performance metrics are based
    on TOTAL INVESTED AMOUNT across all scaling stages, not just initial investments.
    """
    
    def __init__(self, session: Session, redis_client: Redis):
        self.session = session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize repositories
        self.vault_repo = BaseRepository(Vault, session)
        self.performance_repo = BaseRepository(VaultPerformance, session)
        self.position_repo = BaseRepository(Position, session)
        self.scale_repo = BaseRepository(PositionScale, session)
        
        # Vault management configuration
        self.max_positions_per_vault = 2
        self.max_risk_per_vault = Decimal('0.20')  # 20% of vault balance
        self.min_vault_balance = Decimal('1000')   # Minimum 1000 USDT
        
        # CORRECTED: Profit calculation settings
        self.profit_threshold_pct = Decimal('0.75')  # 75% profit on total invested
        self.performance_update_interval = 3600     # Update every hour
        
        # Risk management
        self.correlation_threshold = Decimal('0.70')
        self.max_drawdown_threshold = Decimal('0.25')  # 25% max drawdown
        self.rebalance_threshold = Decimal('0.10')     # 10% allocation drift
    
    async def create_vault(
        self,
        name: str,
        initial_balance: Decimal,
        description: Optional[str] = None,
        allocation_strategy: VaultAllocationStrategy = VaultAllocationStrategy.EQUAL_WEIGHT
    ) -> Tuple[bool, str, Optional[Vault]]:
        """Create new trading vault."""
        
        try:
            if initial_balance < self.min_vault_balance:
                return False, f"Minimum vault balance is {self.min_vault_balance} USDT", None
            
            vault_data = VaultCreate(
                name=name,
                description=description or f"Trading vault: {name}",
                initial_balance=initial_balance,
                current_balance=initial_balance,
                available_balance=initial_balance,
                status=VaultStatus.ACTIVE.value,
                allocation_strategy=allocation_strategy.value,
                max_positions=self.max_positions_per_vault,
                risk_limit=self.max_risk_per_vault,
                vault_metadata={
                    "created_by": "vault_manager",
                    "profit_threshold_pct": float(self.profit_threshold_pct),
                    "max_positions_per_vault": self.max_positions_per_vault,
                    "creation_timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            new_vault = self.vault_repo.create(vault_data)
            
            # Initialize performance tracking
            await self._initialize_vault_performance(new_vault)
            
            self.logger.info(f"Created vault {name} with {initial_balance} USDT")
            
            return True, f"Vault {name} created successfully", new_vault
            
        except Exception as e:
            self.logger.error(f"Error creating vault: {str(e)}")
            return False, str(e), None
    
    async def get_vault_metrics(self, vault_id: str) -> Optional[VaultMetrics]:
        """Get comprehensive vault metrics with CORRECTED calculations."""
        
        try:
            vault = self.vault_repo.get(vault_id)
            if not vault:
                return None
            
            # Get all positions for this vault
            positions = self.session.query(Position).filter(
                Position.vault_id == vault_id
            ).all()
            
            active_positions = [p for p in positions if p.status == PositionStatus.OPEN.value]
            closed_positions = [p for p in positions if p.status == PositionStatus.CLOSED.value]
            
            # CORRECTED: Calculate total invested across all positions
            total_invested = Decimal('0')
            total_profit_targets = Decimal('0')
            unrealized_pnl = Decimal('0')
            
            for position in active_positions:
                # Get all scales for this position
                scales = self.session.query(PositionScale).filter(
                    PositionScale.position_id == position.id
                ).all()
                
                # CORRECTED: Sum all investments for this position
                position_total_invested = sum(scale.investment_amount for scale in scales)
                position_profit_target = position_total_invested * self.profit_threshold_pct
                
                total_invested += position_total_invested
                total_profit_targets += position_profit_target
                
                # Calculate unrealized PnL (simplified - would need current prices)
                if position.current_pnl:
                    unrealized_pnl += position.current_pnl
            
            # Calculate realized profits from closed positions
            total_profit_realized = sum(
                p.total_profit_realized or Decimal('0') for p in closed_positions
            )
            
            # Performance metrics
            total_trades = len(closed_positions)
            winning_trades = len([p for p in closed_positions if (p.total_profit_realized or 0) > 0])
            win_rate = Decimal(str(winning_trades / total_trades)) if total_trades > 0 else Decimal('0')
            
            average_profit_per_trade = (
                total_profit_realized / total_trades if total_trades > 0 else Decimal('0')
            )
            
            # Risk metrics
            current_balance = vault.current_balance
            available_balance = current_balance - total_invested
            risk_utilization = total_invested / vault.initial_balance if vault.initial_balance > 0 else Decimal('0')
            
            # Drawdown calculation
            peak_balance = max(vault.initial_balance, current_balance + total_profit_realized)
            current_drawdown = (peak_balance - current_balance) / peak_balance if peak_balance > 0 else Decimal('0')
            
            # Get historical max drawdown
            max_drawdown = await self._calculate_max_drawdown(vault_id)
            
            return VaultMetrics(
                vault_id=vault_id,
                initial_balance=vault.initial_balance,
                current_balance=current_balance,
                total_invested=total_invested,
                available_balance=available_balance,
                active_positions=len(active_positions),
                total_positions_opened=len(positions),
                positions_closed=len(closed_positions),
                total_profit_realized=total_profit_realized,
                total_profit_targets=total_profit_targets,
                unrealized_pnl=unrealized_pnl,
                max_drawdown=max_drawdown,
                current_drawdown=current_drawdown,
                risk_utilization=risk_utilization,
                win_rate=win_rate,
                average_profit_per_trade=average_profit_per_trade,
                profit_factor=self._calculate_profit_factor(closed_positions),
                sharpe_ratio=await self._calculate_sharpe_ratio(vault_id),
                last_updated=datetime.now(timezone.utc),
                performance_period_days=30  # Default 30-day period
            )
            
        except Exception as e:
            self.logger.error(f"Error getting vault metrics for {vault_id}: {str(e)}")
            return None
    
    async def get_available_vaults(self) -> List[Vault]:
        """Get vaults available for new positions."""
        
        try:
            vaults = self.session.query(Vault).filter(
                and_(
                    Vault.status == VaultStatus.ACTIVE.value,
                    Vault.positions_count < Vault.max_positions,
                    Vault.available_balance >= self.min_vault_balance * Decimal('0.01')  # At least 1% available
                )
            ).all()
            
            return vaults
            
        except Exception as e:
            self.logger.error(f"Error getting available vaults: {str(e)}")
            return []
    
    async def allocate_capital_to_vaults(
        self,
        total_capital: Decimal,
        strategy: VaultAllocationStrategy = VaultAllocationStrategy.PERFORMANCE_BASED
    ) -> List[VaultAllocation]:
        """Allocate capital across vaults based on strategy."""
        
        try:
            vaults = self.session.query(Vault).filter(
                Vault.status == VaultStatus.ACTIVE.value
            ).all()
            
            if not vaults:
                return []
            
            allocations = []
            
            if strategy == VaultAllocationStrategy.EQUAL_WEIGHT:
                allocations = await self._equal_weight_allocation(vaults, total_capital)
            
            elif strategy == VaultAllocationStrategy.PERFORMANCE_BASED:
                allocations = await self._performance_based_allocation(vaults, total_capital)
            
            elif strategy == VaultAllocationStrategy.RISK_ADJUSTED:
                allocations = await self._risk_adjusted_allocation(vaults, total_capital)
            
            elif strategy == VaultAllocationStrategy.DYNAMIC:
                allocations = await self._dynamic_allocation(vaults, total_capital)
            
            return allocations
            
        except Exception as e:
            self.logger.error(f"Error allocating capital: {str(e)}")
            return []
    
    async def _equal_weight_allocation(
        self,
        vaults: List[Vault],
        total_capital: Decimal
    ) -> List[VaultAllocation]:
        """Equal weight allocation across all vaults."""
        
        allocation_per_vault = total_capital / len(vaults)
        allocations = []
        
        for vault in vaults:
            current_allocation = vault.current_balance / total_capital if total_capital > 0 else Decimal('0')
            recommended_allocation = allocation_per_vault / total_capital
            allocation_change = recommended_allocation - current_allocation
            
            allocations.append(VaultAllocation(
                vault_id=str(vault.id),
                recommended_allocation=recommended_allocation,
                current_allocation=current_allocation,
                allocation_change=allocation_change,
                reasoning="Equal weight distribution",
                risk_score=Decimal('0.5'),  # Neutral risk
                expected_return=Decimal('0.75')  # Based on 75% profit target
            ))
        
        return allocations
    
    async def _performance_based_allocation(
        self,
        vaults: List[Vault],
        total_capital: Decimal
    ) -> List[VaultAllocation]:
        """Performance-based allocation favoring better performing vaults."""
        
        allocations = []
        vault_scores = []
        
        # Calculate performance scores for each vault
        for vault in vaults:
            metrics = await self.get_vault_metrics(str(vault.id))
            if not metrics:
                continue
            
            # Performance score based on multiple factors
            score = 0
            
            # Win rate factor (0-40 points)
            score += float(metrics.win_rate) * 40
            
            # Profit factor (0-30 points)
            score += min(float(metrics.profit_factor), 3.0) * 10
            
            # Risk-adjusted return (0-20 points)
            if metrics.current_drawdown < Decimal('0.10'):  # Low drawdown bonus
                score += 20
            elif metrics.current_drawdown < Decimal('0.20'):
                score += 10
            
            # Sharpe ratio factor (0-10 points)
            score += min(float(metrics.sharpe_ratio), 2.0) * 5
            
            vault_scores.append((vault, max(score, 10)))  # Minimum score of 10
        
        # Calculate allocations based on scores
        total_score = sum(score for _, score in vault_scores)
        
        for vault, score in vault_scores:
            if total_score > 0:
                recommended_allocation = Decimal(str(score / total_score))
                current_allocation = vault.current_balance / total_capital if total_capital > 0 else Decimal('0')
                allocation_change = recommended_allocation - current_allocation
                
                allocations.append(VaultAllocation(
                    vault_id=str(vault.id),
                    recommended_allocation=recommended_allocation,
                    current_allocation=current_allocation,
                    allocation_change=allocation_change,
                    reasoning=f"Performance score: {score:.1f}/{total_score:.1f}",
                    risk_score=Decimal(str(1 - score / 100)),  # Higher performance = lower risk
                    expected_return=Decimal(str(score / 100))  # Higher score = higher expected return
                ))
        
        return allocations
    
    async def _risk_adjusted_allocation(
        self,
        vaults: List[Vault],
        total_capital: Decimal
    ) -> List[VaultAllocation]:
        """Risk-adjusted allocation based on risk metrics."""
        
        allocations = []
        vault_risk_scores = []
        
        for vault in vaults:
            metrics = await self.get_vault_metrics(str(vault.id))
            if not metrics:
                continue
            
            # Risk score (lower is better)
            risk_score = 0
            
            # Drawdown risk
            risk_score += float(metrics.current_drawdown) * 50
            risk_score += float(metrics.max_drawdown) * 30
            
            # Utilization risk
            risk_score += float(metrics.risk_utilization) * 20
            
            # Volatility risk (based on profit variance)
            if metrics.total_positions_opened > 5:
                # Calculate profit variance (simplified)
                avg_profit = metrics.average_profit_per_trade
                # Risk increases with high variance
                risk_score += min(float(abs(avg_profit)) / 1000, 20)
            
            # Invert risk score for allocation (lower risk = higher allocation)
            allocation_score = max(100 - risk_score, 10)
            vault_risk_scores.append((vault, allocation_score, risk_score))
        
        # Calculate allocations
        total_allocation_score = sum(score for _, score, _ in vault_risk_scores)
        
        for vault, allocation_score, risk_score in vault_risk_scores:
            if total_allocation_score > 0:
                recommended_allocation = Decimal(str(allocation_score / total_allocation_score))
                current_allocation = vault.current_balance / total_capital if total_capital > 0 else Decimal('0')
                allocation_change = recommended_allocation - current_allocation
                
                allocations.append(VaultAllocation(
                    vault_id=str(vault.id),
                    recommended_allocation=recommended_allocation,
                    current_allocation=current_allocation,
                    allocation_change=allocation_change,
                    reasoning=f"Risk-adjusted: Risk score {risk_score:.1f}",
                    risk_score=Decimal(str(risk_score / 100)),
                    expected_return=Decimal(str((100 - risk_score) / 100 * 0.75))  # Risk-adjusted expected return
                ))
        
        return allocations
    
    async def _dynamic_allocation(
        self,
        vaults: List[Vault],
        total_capital: Decimal
    ) -> List[VaultAllocation]:
        """Dynamic allocation combining performance and risk factors."""
        
        # Get both performance and risk allocations
        performance_allocations = await self._performance_based_allocation(vaults, total_capital)
        risk_allocations = await self._risk_adjusted_allocation(vaults, total_capital)
        
        # Combine allocations (60% performance, 40% risk-adjusted)
        combined_allocations = []
        
        for perf_alloc in performance_allocations:
            # Find corresponding risk allocation
            risk_alloc = next(
                (r for r in risk_allocations if r.vault_id == perf_alloc.vault_id),
                None
            )
            
            if risk_alloc:
                # Weighted combination
                combined_recommended = (
                    perf_alloc.recommended_allocation * Decimal('0.6') +
                    risk_alloc.recommended_allocation * Decimal('0.4')
                )
                
                combined_risk = (
                    perf_alloc.risk_score * Decimal('0.4') +
                    risk_alloc.risk_score * Decimal('0.6')
                )
                
                combined_return = (
                    perf_alloc.expected_return * Decimal('0.7') +
                    risk_alloc.expected_return * Decimal('0.3')
                )
                
                allocation_change = combined_recommended - perf_alloc.current_allocation
                
                combined_allocations.append(VaultAllocation(
                    vault_id=perf_alloc.vault_id,
                    recommended_allocation=combined_recommended,
                    current_allocation=perf_alloc.current_allocation,
                    allocation_change=allocation_change,
                    reasoning="Dynamic: 60% performance + 40% risk-adjusted",
                    risk_score=combined_risk,
                    expected_return=combined_return
                ))
        
        return combined_allocations
    
    async def rebalance_vaults(
        self,
        strategy: VaultAllocationStrategy = VaultAllocationStrategy.DYNAMIC
    ) -> Tuple[bool, str, List[VaultAllocation]]:
        """Rebalance vault allocations based on strategy."""
        
        try:
            # Calculate total capital across all vaults
            vaults = self.session.query(Vault).filter(
                Vault.status == VaultStatus.ACTIVE.value
            ).all()
            
            total_capital = sum(vault.current_balance for vault in vaults)
            
            if total_capital == 0:
                return False, "No capital available for rebalancing", []
            
            # Get recommended allocations
            allocations = await self.allocate_capital_to_vaults(total_capital, strategy)
            
            # Check if rebalancing is needed
            rebalance_needed = any(
                abs(alloc.allocation_change) > self.rebalance_threshold
                for alloc in allocations
            )
            
            if not rebalance_needed:
                return True, "No rebalancing needed", allocations
            
            # Execute rebalancing (in practice, this would involve moving funds)
            rebalanced_count = 0
            for allocation in allocations:
                if abs(allocation.allocation_change) > self.rebalance_threshold:
                    # In a real implementation, this would transfer funds between vaults
                    self.logger.info(
                        f"Rebalancing vault {allocation.vault_id}: "
                        f"{allocation.allocation_change:+.2%} change"
                    )
                    rebalanced_count += 1
            
            return True, f"Rebalanced {rebalanced_count} vaults", allocations
            
        except Exception as e:
            self.logger.error(f"Error rebalancing vaults: {str(e)}")
            return False, str(e), []
    
    async def update_vault_performance(self, vault_id: str) -> bool:
        """Update vault performance metrics."""
        
        try:
            metrics = await self.get_vault_metrics(vault_id)
            if not metrics:
                return False
            
            # Create performance record
            performance_data = VaultPerformanceCreate(
                vault_id=vault_id,
                balance=metrics.current_balance,
                total_invested=metrics.total_invested,
                profit_realized=metrics.total_profit_realized,
                unrealized_pnl=metrics.unrealized_pnl,
                drawdown=metrics.current_drawdown,
                win_rate=metrics.win_rate,
                profit_factor=metrics.profit_factor,
                sharpe_ratio=metrics.sharpe_ratio,
                active_positions=metrics.active_positions,
                performance_metadata={
                    "total_profit_targets": float(metrics.total_profit_targets),
                    "risk_utilization": float(metrics.risk_utilization),
                    "average_profit_per_trade": float(metrics.average_profit_per_trade),
                    "max_drawdown": float(metrics.max_drawdown)
                }
            )
            
            self.performance_repo.create(performance_data)
            
            # Update vault with latest metrics
            vault = self.vault_repo.get(vault_id)
            vault.current_balance = metrics.current_balance
            vault.available_balance = metrics.available_balance
            vault.positions_count = metrics.active_positions
            vault.performance_score = float(metrics.profit_factor)
            vault.last_updated = datetime.now(timezone.utc)
            
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating vault performance: {str(e)}")
            return False
    
    async def _initialize_vault_performance(self, vault: Vault) -> None:
        """Initialize performance tracking for new vault."""
        
        try:
            initial_performance = VaultPerformanceCreate(
                vault_id=str(vault.id),
                balance=vault.initial_balance,
                total_invested=Decimal('0'),
                profit_realized=Decimal('0'),
                unrealized_pnl=Decimal('0'),
                drawdown=Decimal('0'),
                win_rate=Decimal('0'),
                profit_factor=Decimal('1'),
                sharpe_ratio=Decimal('0'),
                active_positions=0,
                performance_metadata={
                    "initialization": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            self.performance_repo.create(initial_performance)
            self.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error initializing vault performance: {str(e)}")
    
    async def _calculate_max_drawdown(self, vault_id: str) -> Decimal:
        """Calculate maximum drawdown for vault."""
        
        try:
            # Get historical performance data
            performances = self.session.query(VaultPerformance).filter(
                VaultPerformance.vault_id == vault_id
            ).order_by(VaultPerformance.created_at).all()
            
            if not performances:
                return Decimal('0')
            
            max_drawdown = Decimal('0')
            peak_balance = performances[0].balance
            
            for perf in performances:
                if perf.balance > peak_balance:
                    peak_balance = perf.balance
                
                current_drawdown = (peak_balance - perf.balance) / peak_balance if peak_balance > 0 else Decimal('0')
                max_drawdown = max(max_drawdown, current_drawdown)
            
            return max_drawdown
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {str(e)}")
            return Decimal('0')
    
    def _calculate_profit_factor(self, closed_positions: List[Position]) -> Decimal:
        """Calculate profit factor for closed positions."""
        
        if not closed_positions:
            return Decimal('1')
        
        total_profit = sum(
            p.total_profit_realized for p in closed_positions 
            if p.total_profit_realized and p.total_profit_realized > 0
        ) or Decimal('0')
        
        total_loss = abs(sum(
            p.total_profit_realized for p in closed_positions 
            if p.total_profit_realized and p.total_profit_realized < 0
        )) or Decimal('0')
        
        if total_loss == 0:
            return Decimal('999') if total_profit > 0 else Decimal('1')
        
        return total_profit / total_loss
    
    async def _calculate_sharpe_ratio(self, vault_id: str) -> Decimal:
        """Calculate Sharpe ratio for vault."""
        
        try:
            # Get recent performance data (last 30 days)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            performances = self.session.query(VaultPerformance).filter(
                and_(
                    VaultPerformance.vault_id == vault_id,
                    VaultPerformance.created_at >= cutoff_date
                )
            ).order_by(VaultPerformance.created_at).all()
            
            if len(performances) < 2:
                return Decimal('0')
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(performances)):
                prev_balance = performances[i-1].balance
                curr_balance = performances[i].balance
                
                if prev_balance > 0:
                    daily_return = (curr_balance - prev_balance) / prev_balance
                    returns.append(float(daily_return))
            
            if not returns:
                return Decimal('0')
            
            # Calculate Sharpe ratio (simplified)
            import statistics
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0
            
            if std_return == 0:
                return Decimal('999') if mean_return > 0 else Decimal('0')
            
            # Assume risk-free rate of 0 for simplicity
            sharpe = mean_return / std_return
            return Decimal(str(sharpe))
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return Decimal('0')
    
    async def get_vault_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all vaults."""
        
        try:
            vaults = self.session.query(Vault).filter(
                Vault.status == VaultStatus.ACTIVE.value
            ).all()
            
            total_capital = Decimal('0')
            total_invested = Decimal('0')
            total_profit_targets = Decimal('0')
            total_active_positions = 0
            
            vault_summaries = []
            
            for vault in vaults:
                metrics = await self.get_vault_metrics(str(vault.id))
                if metrics:
                    total_capital += metrics.current_balance
                    total_invested += metrics.total_invested
                    total_profit_targets += metrics.total_profit_targets
                    total_active_positions += metrics.active_positions
                    
                    vault_summaries.append({
                        "vault_id": str(vault.id),
                        "name": vault.name,
                        "balance": float(metrics.current_balance),
                        "invested": float(metrics.total_invested),
                        "profit_targets": float(metrics.total_profit_targets),
                        "active_positions": metrics.active_positions,
                        "win_rate": float(metrics.win_rate),
                        "profit_factor": float(metrics.profit_factor),
                        "drawdown": float(metrics.current_drawdown)
                    })
            
            return {
                "total_vaults": len(vaults),
                "total_capital": float(total_capital),
                "total_invested": float(total_invested),
                "total_profit_targets": float(total_profit_targets),
                "total_active_positions": total_active_positions,
                "average_profit_threshold_pct": float(self.profit_threshold_pct * 100),
                "vaults": vault_summaries,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting vault summary: {str(e)}")
            return {"error": str(e)}


# Export main class
__all__ = [
    'VaultManagerService',
    'VaultMetrics',
    'VaultAllocation',
    'VaultAllocationStrategy'
]

