#!/usr/bin/env python3
"""
Position Lifecycle Orchestration Agent
Monitors open positions and manages their complete lifecycle with real liquidation clusters
"""

import asyncio
import logging
from typing import List, Optional
from decimal import Decimal
import aiohttp
import os
from datetime import datetime

from ..services.vault_position_manager import VaultPositionManager, VaultPosition, LiquidationCluster

logger = logging.getLogger(__name__)

class PositionLifecycleOrchestrator:
    """
    Orchestrates the complete lifecycle of open positions:
    1. Monitors real liquidation clusters from KingFisher
    2. Tracks position liquidation levels
    3. Executes doubling decisions based on real data
    4. Manages TP/trailing stops
    5. Ensures positions are managed 24/7
    """
    
    def __init__(self):
        self.vault_manager = VaultPositionManager()
        
        # API endpoints and keys
        self.kucoin_api_key = os.getenv("KUCOIN_API_KEY")
        self.kucoin_secret = os.getenv("KUCOIN_SECRET")
        self.kucoin_passphrase = os.getenv("KUCOIN_PASSPHRASE")
        self.kingfisher_url = os.getenv("KINGFISHER_API_URL", "http://localhost:8001")
        
        self.monitoring_interval = 5  # Check every 5 seconds
        self.cluster_update_interval = 30  # Update clusters every 30 seconds
        self._running = False
        self._tasks = {}
        self._session = None
        
        logger.info("Position Lifecycle Orchestrator initialized")
    
    async def start_monitoring(self):
        """Start monitoring all open positions"""
        self._running = True
        logger.info("Starting position lifecycle monitoring...")
        
        # Create aiohttp session
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        # Start monitoring tasks
        self._tasks['position_monitor'] = asyncio.create_task(self._monitor_positions())
        self._tasks['cluster_updater'] = asyncio.create_task(self._update_clusters_continuously())
        self._tasks['health_check'] = asyncio.create_task(self._health_check())
        
        logger.info("Position monitoring started with 3 parallel tasks")
    
    async def _monitor_positions(self):
        """Main monitoring loop for all open positions"""
        while self._running:
            try:
                # Get all active positions
                if not self.vault_manager:
                    logger.error("Vault manager not available")
                    await asyncio.sleep(self.monitoring_interval)
                    continue
                    
                active_positions = self.vault_manager.active_positions
                
                if not active_positions:
                    await asyncio.sleep(self.monitoring_interval)
                    continue
                
                # Monitor each position
                for position_id, position in active_positions.items():
                    await self._check_position_lifecycle(position)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in position monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _check_position_lifecycle(self, position: VaultPosition):
        """
        Check complete lifecycle of a single position:
        1. Get current price
        2. Check liquidation proximity
        3. Check cluster positions
        4. Execute doubling if needed
        5. Check TP/trailing stops
        """
        try:
            # Get current market price
            current_price = await self._get_current_price(position.symbol)
            if not current_price:
                return
            
            # Get real liquidation clusters from KingFisher
            clusters_above, clusters_below = await self._get_real_clusters(position.symbol)
            
            # Update position with real clusters
            if self.vault_manager:
                position.clusters_above = clusters_above
                position.clusters_below = clusters_below
            
            # Log critical information
            logger.info(f"Position {position.position_id} Lifecycle Check:")
            logger.info(f"  Symbol: {position.symbol}")
            logger.info(f"  Current Price: ${current_price:.4f}")
            logger.info(f"  Avg Entry: ${position.current_entry_price:.4f}")
            logger.info(f"  Position Liquidation: ${position.liquidation_price:.4f}")
            
            if clusters_below and len(clusters_below) >= 2:
                logger.info(f"  First Cluster: ${clusters_below[0].price_level:.4f}")
                logger.info(f"  Second Cluster: ${clusters_below[1].price_level:.4f}")
                
                # Determine liquidation position relative to clusters
                liq_position = self._analyze_liquidation_position(
                    position.liquidation_price,
                    clusters_below[0].price_level,
                    clusters_below[1].price_level
                )
                logger.info(f"  Liquidation Position: {liq_position}")
            
            # Calculate current P&L
            pnl = self._calculate_pnl(position, current_price)
            margin_loss_pct = Decimal(str(abs(pnl) / position.total_margin_invested)) if pnl < 0 else Decimal("0")
            
            logger.info(f"  Current P&L: ${pnl:.2f}")
            logger.info(f"  Margin Loss: {margin_loss_pct*100:.1f}%")
            
            # Check for critical actions
            actions_taken = []
            
            # 1. Check if approaching liquidation (emergency)
            if self._is_near_liquidation(current_price, position.liquidation_price):
                actions_taken.append("EMERGENCY: Near liquidation!")
                await self._handle_near_liquidation(position, current_price)
            
            # 2. Check doubling triggers
            should_double, reason = self._check_doubling_triggers(
                position, current_price, margin_loss_pct, clusters_below
            )
            
            if should_double:
                logger.info(f"  DOUBLING TRIGGERED: {reason}")
                if self.vault_manager:
                    await self.vault_manager.update_position(position.position_id, current_price)
                actions_taken.append(f"Doubled: {reason}")
            
            # 3. Check TP hit
            if current_price >= position.current_tp_price and not position.first_tp_triggered:
                logger.info(f"  TP HIT at ${current_price:.4f}")
                if self.vault_manager:
                    await self.vault_manager.update_position(position.position_id, current_price)
                actions_taken.append("TP hit - 50% closed")
            
            # 4. Check trailing stop
            if position.trailing_stop_price and current_price <= position.trailing_stop_price:
                logger.info(f"  TRAILING STOP HIT at ${current_price:.4f}")
                if self.vault_manager:
                    await self.vault_manager.update_position(position.position_id, current_price)
                actions_taken.append("Trailing stop triggered")
            
            if actions_taken:
                await self._send_alert(position, actions_taken, current_price)
            
        except Exception as e:
            logger.error(f"Error checking position {position.position_id}: {e}")
    
    async def _get_real_clusters(self, symbol: str) -> tuple:
        """Get real liquidation clusters from KingFisher"""
        try:
            # Check if session exists
            if not self._session:
                logger.warning("No session available for KingFisher API")
                return await self._calculate_estimated_clusters(symbol)
            
            # Convert symbol format for KingFisher (SUI/USDT:USDT -> SUI)
            base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
            
            # Call KingFisher API
            url = f"{self.kingfisher_url}/api/liquidation-clusters/{base_symbol}"
            async with self._session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"KingFisher API returned {response.status}")
                    return await self._calculate_estimated_clusters(symbol)
                
                cluster_data = await response.json()
            
            if not cluster_data:
                return await self._calculate_estimated_clusters(symbol)
            
            clusters_above = []
            clusters_below = []
            current_price = await self._get_current_price(symbol)
            
            if not current_price:
                return [], []
            
            # Process liquidation levels from KingFisher
            liquidation_levels = cluster_data.get('liquidation_levels', []) if cluster_data and isinstance(cluster_data, dict) else []
            for level in liquidation_levels:
                if not isinstance(level, dict):
                    continue
                price = Decimal(str(level.get('price', 0)))
                volume = Decimal(str(level.get('volume', 0)))
                
                if price > current_price:
                    clusters_above.append(LiquidationCluster(
                        price_level=price,
                        cluster_type="above",
                        strength=float(volume / 1000000),  # Normalize
                        volume=float(volume),
                        distance_from_entry=(price - current_price) / current_price,
                        last_updated=datetime.now()
                    ))
                else:
                    clusters_below.append(LiquidationCluster(
                        price_level=price,
                        cluster_type="below",
                        strength=float(volume / 1000000),  # Normalize
                        volume=float(volume),
                        distance_from_entry=(price - current_price) / current_price,
                        last_updated=datetime.now()
                    ))
            
            # Sort and limit to 2 clusters each side
            clusters_above.sort(key=lambda x: x.price_level)
            clusters_below.sort(key=lambda x: x.price_level, reverse=True)
            
            return clusters_above[:2], clusters_below[:2]
            
        except Exception as e:
            logger.error(f"Error getting real clusters: {e}")
            return await self._calculate_estimated_clusters(symbol)
    
    async def _calculate_estimated_clusters(self, symbol: str) -> tuple:
        """Calculate estimated clusters based on common liquidation levels"""
        current_price = await self._get_current_price(symbol)
        if not current_price:
            return [], []
        
        # Common liquidation levels for different leverages
        clusters_above = [
            LiquidationCluster(
                price_level=current_price * Decimal("1.05"),
                cluster_type="above",
                strength=0.8,
                volume=1000000,
                distance_from_entry=Decimal("0.05"),
                last_updated=datetime.now()
            ),
            LiquidationCluster(
                price_level=current_price * Decimal("1.10"),
                cluster_type="above",
                strength=0.6,
                volume=500000,
                distance_from_entry=Decimal("0.10"),
                last_updated=datetime.now()
            )
        ]
        
        clusters_below = [
            LiquidationCluster(
                price_level=current_price * Decimal("0.95"),
                cluster_type="below",
                strength=0.8,
                volume=1000000,
                distance_from_entry=Decimal("-0.05"),
                last_updated=datetime.now()
            ),
            LiquidationCluster(
                price_level=current_price * Decimal("0.90"),
                cluster_type="below",
                strength=0.6,
                volume=500000,
                distance_from_entry=Decimal("-0.10"),
                last_updated=datetime.now()
            )
        ]
        
        return clusters_above, clusters_below
    
    async def _get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price from KuCoin"""
        try:
            # Check if session exists
            if not self._session:
                logger.warning("No session available for price fetching")
                return None
            
            # Use KuCoin public API (no auth needed for ticker)
            # Convert symbol format: SUI/USDT:USDT -> SUI-USDT
            kucoin_symbol = symbol.replace('/', '-').replace(':USDT', '')
            
            url = f"https://api-futures.kucoin.com/api/v1/ticker?symbol={kucoin_symbol}"
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and 'price' in data['data']:
                        return Decimal(str(data['data']['price']))
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
        return None
    
    def _analyze_liquidation_position(self, liq_price: Decimal, 
                                     first_cluster: Decimal, 
                                     second_cluster: Decimal) -> str:
        """Analyze where liquidation sits relative to clusters"""
        if liq_price > first_cluster:
            return "BEFORE clusters (critical)"
        elif liq_price <= first_cluster and liq_price > second_cluster:
            return "BETWEEN clusters (optimal)"
        else:
            return "AFTER clusters (safe)"
    
    def _calculate_pnl(self, position: VaultPosition, current_price: Decimal) -> Decimal:
        """Calculate current P&L"""
        price_change_pct = (current_price - position.current_entry_price) / position.current_entry_price
        return price_change_pct * position.total_position_size
    
    def _is_near_liquidation(self, current_price: Decimal, liq_price: Decimal) -> bool:
        """Check if position is dangerously close to liquidation"""
        distance = abs(current_price - liq_price) / current_price
        return distance < Decimal("0.02")  # Within 2% of liquidation
    
    def _check_doubling_triggers(self, position: VaultPosition, 
                                current_price: Decimal,
                                margin_loss_pct: Decimal,
                                clusters_below: list) -> tuple:
        """Check if we should double the position"""
        # Trigger 1: 80% margin loss
        if margin_loss_pct >= Decimal("0.80"):
            return True, "80% margin loss reached"
        
        # Trigger 2: Hit liquidation cluster
        if clusters_below and len(clusters_below) >= 2:
            first_cluster = clusters_below[0].price_level
            second_cluster = clusters_below[1].price_level
            
            # Check if we hit first cluster
            if abs(current_price - first_cluster) / current_price < Decimal("0.002"):
                # Check liquidation position
                if position.liquidation_price > first_cluster:
                    return True, "Hit cluster - liquidation BEFORE clusters"
                elif position.liquidation_price <= first_cluster and position.liquidation_price > second_cluster:
                    return True, "Hit cluster - liquidation BETWEEN clusters"
        
        return False, ""
    
    async def _handle_near_liquidation(self, position: VaultPosition, current_price: Decimal):
        """Handle emergency situation when near liquidation"""
        logger.critical(f"EMERGENCY: Position {position.position_id} near liquidation!")
        logger.critical(f"  Current: ${current_price:.4f}")
        logger.critical(f"  Liquidation: ${position.liquidation_price:.4f}")
        
        # Check if we can add margin or need to double
        if not self.vault_manager:
            logger.error("Vault manager not available")
            return
            
        vault = self.vault_manager.vaults.get(position.vault_id)
        if vault and not position.margin_added:
            # Try margin injection
            margin_to_add = vault.total_balance * Decimal("0.15")
            if margin_to_add <= vault.available_balance:
                logger.info(f"  Adding emergency margin: ${margin_to_add}")
                await self.vault_manager.update_position(position.position_id, current_price)
    
    async def _update_clusters_continuously(self):
        """Continuously update liquidation clusters for all positions"""
        while self._running:
            try:
                if not self.vault_manager:
                    logger.error("Vault manager not available")
                    await asyncio.sleep(self.cluster_update_interval)
                    continue
                    
                for position_id, position in self.vault_manager.active_positions.items():
                    clusters_above, clusters_below = await self._get_real_clusters(position.symbol)
                    position.clusters_above = clusters_above
                    position.clusters_below = clusters_below
                    
                await asyncio.sleep(self.cluster_update_interval)
                
            except Exception as e:
                logger.error(f"Error updating clusters: {e}")
                await asyncio.sleep(self.cluster_update_interval)
    
    async def _health_check(self):
        """Regular health check of the system"""
        while self._running:
            try:
                if not self.vault_manager:
                    logger.error("Vault manager not available")
                    await asyncio.sleep(60)
                    continue
                    
                active_count = len(self.vault_manager.active_positions)
                logger.info(f"Health Check: Monitoring {active_count} active positions")
                
                # Check KuCoin connection
                kucoin_status = await self._check_kucoin_connection()
                
                # Check KingFisher connection
                kingfisher_status = await self._check_kingfisher_connection()
                
                if not kucoin_status:
                    logger.error("KuCoin connection lost!")
                if not kingfisher_status:
                    logger.warning("KingFisher connection lost - using estimated clusters")
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    async def _check_kucoin_connection(self) -> bool:
        """Check KuCoin API connection"""
        try:
            if not self._session:
                return False
            url = "https://api-futures.kucoin.com/api/v1/timestamp"
            timeout = aiohttp.ClientTimeout(total=5)
            async with self._session.get(url, timeout=timeout) as response:
                return response.status == 200
        except:
            return False
    
    async def _check_kingfisher_connection(self) -> bool:
        """Check KingFisher API connection"""
        try:
            if not self._session:
                return False
            url = f"{self.kingfisher_url}/health"
            timeout = aiohttp.ClientTimeout(total=5)
            async with self._session.get(url, timeout=timeout) as response:
                return response.status == 200
        except:
            return False
    
    async def _send_alert(self, position: VaultPosition, actions: List[str], price: Decimal):
        """Send alerts for critical events"""
        alert_msg = f"Position {position.position_id} Alert:\n"
        alert_msg += f"Symbol: {position.symbol}\n"
        alert_msg += f"Price: ${price:.4f}\n"
        alert_msg += f"Actions: {', '.join(actions)}\n"
        
        logger.info(f"ALERT: {alert_msg}")
        # TODO: Send to Telegram, Discord, etc.
    
    async def stop_monitoring(self):
        """Stop all monitoring tasks"""
        self._running = False
        
        # Cancel all tasks
        for task_name, task in self._tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled task: {task_name}")
        
        # Close aiohttp session
        if self._session:
            await self._session.close()
        
        logger.info("Position Lifecycle Orchestrator stopped")

# Global instance
position_orchestrator = PositionLifecycleOrchestrator()