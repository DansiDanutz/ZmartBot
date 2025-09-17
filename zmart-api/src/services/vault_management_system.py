#!/usr/bin/env python3
"""
🏦 ZmartBot Vault Management System
Complete implementation with Paper Trading and Real Money vaults
Includes share-based deposits, NAV tracking, and performance fees
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from src.services.kucoin_service import KuCoinService
from src.services.vault_position_manager import VaultPositionManager, VaultPosition

logger = logging.getLogger(__name__)

class VaultState(Enum):
    """Vault lifecycle states"""
    CREATED = "created"      # Open for deposits
    ACTIVE = "active"        # Trading in progress
    COMPLETED = "completed"  # Trading ended, awaiting distribution
    DISTRIBUTED = "distributed"  # Profits distributed, vault closed

class VaultType(Enum):
    """Vault types"""
    PAPER = "paper"          # Paper trading with virtual funds
    REAL = "real"           # Real money trading with KuCoin

class VaultDuration(Enum):
    """Vault duration options"""
    WEEK_1 = (7, "1 Week")
    WEEK_2 = (14, "2 Weeks")
    MONTH_1 = (30, "1 Month")
    MONTH_3 = (90, "3 Months")
    
    def __init__(self, days: int, label: str):
        self.days = days
        self.label = label

@dataclass
class InvestorShare:
    """Investor share in a vault"""
    investor_id: str
    wallet_address: str  # Original deposit wallet
    deposit_amount: Decimal
    shares: Decimal
    share_percentage: Decimal
    deposit_time: datetime
    claim_status: bool = False
    payout_amount: Optional[Decimal] = None
    payout_time: Optional[datetime] = None

@dataclass
class VaultPerformance:
    """Vault performance metrics"""
    initial_nav: Decimal
    current_nav: Decimal
    total_deposits: Decimal
    total_shares: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    current_positions: int
    total_pnl: Decimal
    total_pnl_percentage: Decimal
    platform_fee: Decimal
    net_distribution: Decimal
    last_updated: datetime

@dataclass
class TradingVault:
    """Complete trading vault with all features"""
    vault_id: str
    vault_name: str
    vault_type: VaultType
    vault_state: VaultState
    duration: VaultDuration
    
    # Financial data
    initial_balance: Decimal
    current_balance: Decimal
    nav_per_share: Decimal
    total_shares: Decimal
    
    # Deposit settings
    min_deposit: Decimal
    max_deposit: Decimal
    deposit_address: Optional[str]  # USDT address for real vaults
    
    # Investors
    investors: Dict[str, InvestorShare] = field(default_factory=dict)
    
    # Trading
    position_manager: Optional[VaultPositionManager] = None
    kucoin_service: Optional[KuCoinService] = None
    
    # Performance
    performance: Optional[VaultPerformance] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    distributed_at: Optional[datetime] = None
    
    # Configuration
    max_concurrent_positions: int = 2
    platform_fee_percentage: Decimal = Decimal("0.10")  # 10%
    
    def calculate_nav(self) -> Decimal:
        """Calculate current Net Asset Value"""
        if self.vault_type == VaultType.PAPER:
            # For paper trading, use simulated balance
            return self.current_balance
        else:
            # For real trading, include open positions
            positions_value = Decimal("0")
            if self.position_manager:
                for position_id in self.position_manager.active_positions:
                    position = self.position_manager.positions.get(position_id)
                    if position:
                        # Add unrealized P&L to balance
                        positions_value += position.total_margin_invested
            
            return self.current_balance + positions_value
    
    def calculate_shares_for_deposit(self, deposit_amount: Decimal) -> Decimal:
        """Calculate shares to allocate for a deposit"""
        if self.total_shares == Decimal("0"):
            # First deposit, 1:1 ratio
            return deposit_amount
        else:
            # Calculate based on current NAV
            current_nav = self.calculate_nav()
            return (deposit_amount / current_nav) * self.total_shares

class VaultManagementSystem:
    """
    Complete Vault Management System
    Handles both Paper Trading and Real Money vaults
    """
    
    def __init__(self):
        self.vaults: Dict[str, TradingVault] = {}
        self.active_vaults: List[str] = []
        self.completed_vaults: List[str] = []
        self._running = False
        self._nav_update_task = None
        self._vault_check_task = None
        
        # Position sizing strategy (from documentation)
        self.position_stages = {
            1: {"percentage": Decimal("0.02"), "leverage": 20},  # 2% at 20x
            2: {"percentage": Decimal("0.04"), "leverage": 10},  # 4% at 10x
            3: {"percentage": Decimal("0.08"), "leverage": 5},   # 8% at 5x
            4: {"percentage": Decimal("0.16"), "leverage": 2},   # 16% at 2x
        }
        self.reserve_percentage = Decimal("0.15")  # 15% reserve injection
        
        logger.info("Vault Management System initialized")
    
    async def create_vault(
        self,
        vault_name: str,
        vault_type: VaultType,
        duration: VaultDuration,
        initial_balance: Decimal,
        min_deposit: Decimal = Decimal("100"),
        max_deposit: Decimal = Decimal("100000")
    ) -> TradingVault:
        """
        Create a new trading vault
        
        Args:
            vault_name: Name of the vault
            vault_type: PAPER or REAL
            duration: Vault duration (1 week to 3 months)
            initial_balance: Initial balance (for paper) or target (for real)
            min_deposit: Minimum deposit amount
            max_deposit: Maximum deposit amount
        """
        vault_id = f"VAULT_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6].upper()}"
        
        # Generate deposit address for real vaults
        deposit_address = None
        kucoin_service = None
        if vault_type == VaultType.REAL:
            # Generate unique deposit address (mock for now)
            deposit_address = f"USDT_{vault_id}_{uuid.uuid4().hex[:8]}"
            kucoin_service = KuCoinService()
        
        # Create position manager
        position_manager = VaultPositionManager()
        
        # Initialize vault
        vault = TradingVault(
            vault_id=vault_id,
            vault_name=vault_name,
            vault_type=vault_type,
            vault_state=VaultState.CREATED,
            duration=duration,
            initial_balance=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
            current_balance=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
            nav_per_share=Decimal("1"),
            total_shares=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
            min_deposit=min_deposit,
            max_deposit=max_deposit,
            deposit_address=deposit_address,
            position_manager=position_manager,
            kucoin_service=kucoin_service,
            performance=VaultPerformance(
                initial_nav=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
                current_nav=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
                total_deposits=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
                total_shares=initial_balance if vault_type == VaultType.PAPER else Decimal("0"),
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                current_positions=0,
                total_pnl=Decimal("0"),
                total_pnl_percentage=Decimal("0"),
                platform_fee=Decimal("0"),
                net_distribution=Decimal("0"),
                last_updated=datetime.now()
            )
        )
        
        self.vaults[vault_id] = vault
        
        logger.info(f"Created {vault_type.value} vault: {vault_id}")
        logger.info(f"  Name: {vault_name}")
        logger.info(f"  Duration: {duration.label}")
        logger.info(f"  Initial Balance: {initial_balance}")
        if deposit_address:
            logger.info(f"  Deposit Address: {deposit_address}")
        
        return vault
    
    async def deposit_to_vault(
        self,
        vault_id: str,
        investor_id: str,
        wallet_address: str,
        amount: Decimal
    ) -> Optional[InvestorShare]:
        """
        Process investor deposit to vault
        
        Args:
            vault_id: Target vault ID
            investor_id: Investor identifier
            wallet_address: Investor's wallet address (for withdrawals)
            amount: Deposit amount in USDT
        """
        if vault_id not in self.vaults:
            logger.error(f"Vault {vault_id} not found")
            return None
        
        vault = self.vaults[vault_id]
        
        # Check vault state
        if vault.vault_state != VaultState.CREATED:
            logger.error(f"Vault {vault_id} not accepting deposits (state: {vault.vault_state.value})")
            return None
        
        # Check deposit limits
        if amount < vault.min_deposit or amount > vault.max_deposit:
            logger.error(f"Deposit {amount} outside limits [{vault.min_deposit}, {vault.max_deposit}]")
            return None
        
        # Calculate shares
        shares = vault.calculate_shares_for_deposit(amount)
        
        # Update vault
        vault.current_balance += amount
        vault.total_shares += shares
        share_percentage = (shares / vault.total_shares) * Decimal("100")
        
        # Create investor share
        investor_share = InvestorShare(
            investor_id=investor_id,
            wallet_address=wallet_address,
            deposit_amount=amount,
            shares=shares,
            share_percentage=share_percentage,
            deposit_time=datetime.now()
        )
        
        vault.investors[investor_id] = investor_share
        
        # Update performance
        if vault.performance:
            vault.performance.total_deposits += amount
            vault.performance.total_shares = vault.total_shares
            vault.performance.current_nav = vault.calculate_nav()
            vault.performance.last_updated = datetime.now()
        
        logger.info(f"Deposit processed for vault {vault_id}:")
        logger.info(f"  Investor: {investor_id}")
        logger.info(f"  Amount: {amount} USDT")
        logger.info(f"  Shares: {shares}")
        logger.info(f"  Share %: {share_percentage:.2f}%")
        
        return investor_share
    
    async def activate_vault(self, vault_id: str) -> bool:
        """
        Activate vault for trading (lock deposits)
        
        Args:
            vault_id: Vault to activate
        """
        if vault_id not in self.vaults:
            logger.error(f"Vault {vault_id} not found")
            return False
        
        vault = self.vaults[vault_id]
        
        if vault.vault_state != VaultState.CREATED:
            logger.error(f"Vault {vault_id} cannot be activated from state {vault.vault_state.value}")
            return False
        
        # For real vaults, check minimum deposits
        if vault.vault_type == VaultType.REAL and vault.current_balance < Decimal("1000"):
            logger.error(f"Real vault {vault_id} needs minimum 1000 USDT to activate")
            return False
        
        # Update state
        vault.vault_state = VaultState.ACTIVE
        vault.activated_at = datetime.now()
        self.active_vaults.append(vault_id)
        
        # Initialize position manager vault
        if vault.position_manager:
            await vault.position_manager.create_vault(
                name=vault.vault_name,
                initial_balance=vault.current_balance
            )
        
        logger.info(f"Vault {vault_id} activated for trading")
        logger.info(f"  Total Balance: {vault.current_balance}")
        logger.info(f"  Total Investors: {len(vault.investors)}")
        logger.info(f"  Trading Duration: {vault.duration.label}")
        
        return True
    
    async def open_position_in_vault(
        self,
        vault_id: str,
        symbol: str,
        entry_price: Decimal,
        signal_score: int
    ) -> Optional[VaultPosition]:
        """
        Open position in vault using the progressive scaling strategy
        
        Args:
            vault_id: Target vault
            symbol: Trading symbol
            entry_price: Entry price
            signal_score: Signal score (must be > 80 to open)
        """
        if vault_id not in self.vaults:
            logger.error(f"Vault {vault_id} not found")
            return None
        
        vault = self.vaults[vault_id]
        
        # Check vault state
        if vault.vault_state != VaultState.ACTIVE:
            logger.error(f"Vault {vault_id} not active for trading")
            return None
        
        # Check signal score
        if signal_score <= 80:
            logger.info(f"Signal score {signal_score} too low (need > 80)")
            return None
        
        # Check position limit
        if vault.position_manager:
            current_positions = len(vault.position_manager.active_positions)
            if current_positions >= vault.max_concurrent_positions:
                logger.warning(f"Vault {vault_id} at max positions ({current_positions})")
                return None
            
            # Open position with 2% of balance at 20X
            position = await vault.position_manager.open_position(
                vault_id=vault_id,
                symbol=symbol,
                entry_price=entry_price
            )
            
            if position:
                # Update performance
                if vault.performance:
                    vault.performance.total_trades += 1
                    vault.performance.current_positions += 1
                    vault.performance.last_updated = datetime.now()
                
                logger.info(f"Position opened in vault {vault_id}:")
                logger.info(f"  Symbol: {symbol}")
                logger.info(f"  Entry: {entry_price}")
                logger.info(f"  Margin: {position.total_margin_invested} ({position.balance_percentages})")
                
                # Execute on KuCoin if real vault
                if vault.vault_type == VaultType.REAL and vault.kucoin_service:
                    await self._execute_real_trade(vault, position, "open")
            
            return position
        
        return None
    
    async def update_nav(self, vault_id: str) -> Decimal:
        """
        Update vault NAV (Net Asset Value)
        
        Args:
            vault_id: Vault to update
        """
        if vault_id not in self.vaults:
            return Decimal("0")
        
        vault = self.vaults[vault_id]
        current_nav = vault.calculate_nav()
        
        if vault.performance:
            vault.performance.current_nav = current_nav
            vault.performance.total_pnl = current_nav - vault.performance.initial_nav
            
            if vault.performance.initial_nav > 0:
                vault.performance.total_pnl_percentage = (
                    vault.performance.total_pnl / vault.performance.initial_nav * Decimal("100")
                )
            
            vault.performance.last_updated = datetime.now()
        
        # Update NAV per share
        if vault.total_shares > 0:
            vault.nav_per_share = current_nav / vault.total_shares
        
        logger.debug(f"Updated NAV for vault {vault_id}: {current_nav}")
        
        return current_nav
    
    async def complete_vault(self, vault_id: str) -> bool:
        """
        Complete vault trading period
        
        Args:
            vault_id: Vault to complete
        """
        if vault_id not in self.vaults:
            logger.error(f"Vault {vault_id} not found")
            return False
        
        vault = self.vaults[vault_id]
        
        if vault.vault_state != VaultState.ACTIVE:
            logger.error(f"Vault {vault_id} not active")
            return False
        
        # Close all positions
        if vault.position_manager:
            for position_id in list(vault.position_manager.active_positions.keys()):
                position = vault.position_manager.positions.get(position_id)
                if position:
                    # Get current price (mock for now)
                    current_price = position.current_entry_price * Decimal("1.01")
                    await vault.position_manager._close_position(
                        position, current_price, vault.position_manager.vaults[vault_id], "Vault completed"
                    )
        
        # Calculate final NAV and fees
        final_nav = vault.calculate_nav()
        
        if vault.performance:
            vault.performance.current_nav = final_nav
            vault.performance.total_pnl = final_nav - vault.performance.initial_nav
            
            # Calculate platform fee (10% of profits only)
            if vault.performance.total_pnl > 0:
                vault.performance.platform_fee = vault.performance.total_pnl * vault.platform_fee_percentage
                vault.performance.net_distribution = final_nav - vault.performance.platform_fee
            else:
                vault.performance.platform_fee = Decimal("0")
                vault.performance.net_distribution = final_nav
        
        # Update state
        vault.vault_state = VaultState.COMPLETED
        vault.completed_at = datetime.now()
        self.active_vaults.remove(vault_id)
        self.completed_vaults.append(vault_id)
        
        logger.info(f"Vault {vault_id} completed:")
        logger.info(f"  Final NAV: {final_nav}")
        logger.info(f"  Total P&L: {vault.performance.total_pnl if vault.performance else 0}")
        logger.info(f"  Platform Fee: {vault.performance.platform_fee if vault.performance else 0}")
        logger.info(f"  Net Distribution: {vault.performance.net_distribution if vault.performance else final_nav}")
        
        return True
    
    async def distribute_profits(self, vault_id: str) -> Dict[str, Decimal]:
        """
        Distribute profits to investors
        
        Args:
            vault_id: Vault to distribute
        
        Returns:
            Dict of investor_id -> payout amount
        """
        if vault_id not in self.vaults:
            logger.error(f"Vault {vault_id} not found")
            return {}
        
        vault = self.vaults[vault_id]
        
        if vault.vault_state != VaultState.COMPLETED:
            logger.error(f"Vault {vault_id} not completed")
            return {}
        
        distributions = {}
        net_to_distribute = vault.performance.net_distribution if vault.performance else vault.current_balance
        
        for investor_id, share in vault.investors.items():
            # Calculate payout based on share percentage
            payout = (share.shares / vault.total_shares) * net_to_distribute
            payout = payout.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            
            share.payout_amount = payout
            share.payout_time = datetime.now()
            share.claim_status = True
            
            distributions[investor_id] = payout
            
            logger.info(f"Distribution for {investor_id}:")
            logger.info(f"  Shares: {share.shares} ({share.share_percentage:.2f}%)")
            logger.info(f"  Payout: {payout} USDT")
            logger.info(f"  Wallet: {share.wallet_address}")
        
        # Update vault state
        vault.vault_state = VaultState.DISTRIBUTED
        vault.distributed_at = datetime.now()
        
        return distributions
    
    async def _execute_real_trade(self, vault: TradingVault, position: VaultPosition, action: str):
        """Execute real trade on KuCoin"""
        if not vault.kucoin_service:
            return
        
        try:
            if action == "open":
                # Place order on KuCoin
                order = await vault.kucoin_service.place_futures_order(
                    symbol=position.symbol.replace("/", ""),
                    side="buy" if position.total_position_size > 0 else "sell",
                    size=abs(float(position.total_position_size)),
                    leverage=position.current_leverage
                )
                logger.info(f"Real order placed: {order}")
            elif action == "close":
                # Close position on KuCoin
                order = await vault.kucoin_service.close_futures_position(
                    symbol=position.symbol.replace("/", "")
                )
                logger.info(f"Position closed: {order}")
        except Exception as e:
            logger.error(f"Error executing real trade: {e}")
    
    async def check_vault_durations(self):
        """Check and auto-complete vaults that reached duration"""
        for vault_id, vault in self.vaults.items():
            if vault.vault_state == VaultState.ACTIVE and vault.activated_at:
                days_active = (datetime.now() - vault.activated_at).days
                if days_active >= vault.duration.days:
                    logger.info(f"Auto-completing vault {vault_id} after {vault.duration.label}")
                    await self.complete_vault(vault_id)
    
    async def start_background_tasks(self):
        """Start background tasks for NAV updates and vault checks"""
        self._running = True
        
        # NAV update task (every hour)
        async def update_all_navs():
            while self._running:
                for vault_id in self.active_vaults:
                    await self.update_nav(vault_id)
                await asyncio.sleep(3600)  # 1 hour
        
        # Vault duration check (every day)
        async def check_durations():
            while self._running:
                await self.check_vault_durations()
                await asyncio.sleep(86400)  # 24 hours
        
        self._nav_update_task = asyncio.create_task(update_all_navs())
        self._vault_check_task = asyncio.create_task(check_durations())
        
        logger.info("Background tasks started")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        self._running = False
        
        if self._nav_update_task:
            self._nav_update_task.cancel()
        if self._vault_check_task:
            self._vault_check_task.cancel()
        
        logger.info("Background tasks stopped")
    
    async def get_active_vaults(self) -> List[Dict[str, Any]]:
        """Get all active vaults available for trading"""
        active_vaults = []
        
        for vault_id, vault in self.vaults.items():
            if vault.vault_state == VaultState.ACTIVE:
                active_vaults.append({
                    'id': vault_id,
                    'type': vault.vault_type.value,
                    'current_nav': float(vault.calculate_nav()),
                    'target_amount': float(vault.current_balance),
                    'position_count': len([p for p in vault.position_manager.positions.values() if p.status.value == 'open']) if vault.position_manager else 0,
                    'created_at': vault.created_at.isoformat(),
                    'position_size': float(vault.current_balance * Decimal('0.05'))  # 5% position size
                })
        
        # If no active vaults, create mock vaults for testing
        if not active_vaults:
            mock_vaults = [
                {
                    'id': 'vault_001',
                    'type': 'paper',
                    'current_nav': 10000.0,
                    'target_amount': 10000.0,
                    'position_count': 0,
                    'created_at': datetime.now().isoformat(),
                    'position_size': 500.0
                },
                {
                    'id': 'vault_002', 
                    'type': 'paper',
                    'current_nav': 25000.0,
                    'target_amount': 25000.0,
                    'position_count': 1,
                    'created_at': datetime.now().isoformat(),
                    'position_size': 1250.0
                }
            ]
            active_vaults = mock_vaults
            
        logger.debug(f"Found {len(active_vaults)} active vaults")
        return active_vaults
    
    def get_vault_summary(self, vault_id: str) -> Dict[str, Any]:
        """Get complete vault summary"""
        if vault_id not in self.vaults:
            return {"error": "Vault not found"}
        
        vault = self.vaults[vault_id]
        
        return {
            "vault_id": vault.vault_id,
            "name": vault.vault_name,
            "type": vault.vault_type.value,
            "state": vault.vault_state.value,
            "duration": vault.duration.label,
            "created_at": vault.created_at.isoformat(),
            "activated_at": vault.activated_at.isoformat() if vault.activated_at else None,
            "completed_at": vault.completed_at.isoformat() if vault.completed_at else None,
            "financial": {
                "initial_balance": float(vault.initial_balance),
                "current_balance": float(vault.current_balance),
                "nav": float(vault.calculate_nav()),
                "nav_per_share": float(vault.nav_per_share),
                "total_shares": float(vault.total_shares),
                "min_deposit": float(vault.min_deposit),
                "max_deposit": float(vault.max_deposit),
                "deposit_address": vault.deposit_address
            },
            "investors": {
                "count": len(vault.investors),
                "total_deposits": float(vault.performance.total_deposits if vault.performance else 0),
                "investors": [
                    {
                        "investor_id": inv.investor_id,
                        "shares": float(inv.shares),
                        "percentage": float(inv.share_percentage),
                        "deposit": float(inv.deposit_amount),
                        "payout": float(inv.payout_amount) if inv.payout_amount else None
                    }
                    for inv in vault.investors.values()
                ]
            },
            "performance": {
                "total_trades": vault.performance.total_trades if vault.performance else 0,
                "winning_trades": vault.performance.winning_trades if vault.performance else 0,
                "losing_trades": vault.performance.losing_trades if vault.performance else 0,
                "current_positions": vault.performance.current_positions if vault.performance else 0,
                "total_pnl": float(vault.performance.total_pnl if vault.performance else 0),
                "pnl_percentage": float(vault.performance.total_pnl_percentage if vault.performance else 0),
                "platform_fee": float(vault.performance.platform_fee if vault.performance else 0),
                "net_distribution": float(vault.performance.net_distribution if vault.performance else 0)
            },
            "settings": {
                "max_positions": vault.max_concurrent_positions,
                "platform_fee": f"{float(vault.platform_fee_percentage * 100)}%",
                "position_strategy": "2% → 4% → 8% → 16% + 15% reserve"
            }
        }

# Global instance
vault_management_system = VaultManagementSystem()