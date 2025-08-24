#!/usr/bin/env python3
"""
Unified Cache Update Scheduler
Coordinates cache updates for both KingFisher and Cryptometer modules
Ensures API rate limits are respected across all services
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "kingfisher-module/backend"))

# Import cache managers
try:
    from src.cache.cryptometer_cache_manager import cryptometer_cache
    CRYPTOMETER_AVAILABLE = True
except ImportError:
    CRYPTOMETER_AVAILABLE = False
    cryptometer_cache = None

try:
    from src.cache.kingfisher_cache_manager import kingfisher_cache
    KINGFISHER_AVAILABLE = True
except ImportError:
    KINGFISHER_AVAILABLE = False
    kingfisher_cache = None

logger = logging.getLogger(__name__)

class UpdateStrategy(Enum):
    """Update strategies for different market conditions"""
    AGGRESSIVE = "aggressive"    # High frequency updates during volatility
    NORMAL = "normal"           # Standard update intervals
    CONSERVATIVE = "conservative" # Reduced updates to save API calls
    MINIMAL = "minimal"         # Emergency mode, minimal updates only

class UnifiedCacheScheduler:
    """
    Unified scheduler that coordinates cache updates across all modules
    Implements intelligent scheduling to maximize data freshness while respecting API limits
    """
    
    def __init__(self):
        self.cryptometer_cache = cryptometer_cache if CRYPTOMETER_AVAILABLE else None
        self.kingfisher_cache = kingfisher_cache if KINGFISHER_AVAILABLE else None
        
        # Current update strategy
        self.strategy = UpdateStrategy.NORMAL
        
        # API call budget tracking
        self.api_budget = {
            'cryptometer': {
                'total': 100,        # Per minute
                'used': 0,
                'reset_time': datetime.now() + timedelta(minutes=1)
            },
            'kingfisher': {
                'total': 30,         # Per minute
                'used': 0,
                'reset_time': datetime.now() + timedelta(minutes=1)
            },
            'airtable': {
                'total': 5,          # Per second
                'used': 0,
                'reset_time': datetime.now() + timedelta(seconds=1)
            }
        }
        
        # Update intervals by strategy (in minutes)
        self.update_intervals = {
            UpdateStrategy.AGGRESSIVE: {
                'critical': 2,
                'high': 5,
                'medium': 10,
                'low': 30
            },
            UpdateStrategy.NORMAL: {
                'critical': 5,
                'high': 10,
                'medium': 20,
                'low': 60
            },
            UpdateStrategy.CONSERVATIVE: {
                'critical': 10,
                'high': 20,
                'medium': 40,
                'low': 120
            },
            UpdateStrategy.MINIMAL: {
                'critical': 20,
                'high': 40,
                'medium': 80,
                'low': 240
            }
        }
        
        # Symbols to monitor
        self.monitored_symbols = set()
        
        # Active update tasks
        self.update_tasks = {}
        
        # Scheduler running flag
        self.running = False
        
        logger.info(f"Unified Cache Scheduler initialized (Cryptometer: {CRYPTOMETER_AVAILABLE}, KingFisher: {KINGFISHER_AVAILABLE})")
    
    def add_symbols(self, symbols: List[str]):
        """Add symbols to monitor"""
        self.monitored_symbols.update(symbols)
        logger.info(f"Added {len(symbols)} symbols to monitoring. Total: {len(self.monitored_symbols)}")
    
    def remove_symbols(self, symbols: List[str]):
        """Remove symbols from monitoring"""
        for symbol in symbols:
            self.monitored_symbols.discard(symbol)
        logger.info(f"Removed {len(symbols)} symbols from monitoring. Remaining: {len(self.monitored_symbols)}")
    
    def set_strategy(self, strategy: UpdateStrategy):
        """Change update strategy based on market conditions"""
        old_strategy = self.strategy
        self.strategy = strategy
        logger.info(f"Update strategy changed from {old_strategy.value} to {strategy.value}")
    
    async def _reset_api_budgets(self):
        """Reset API budgets when time windows expire"""
        now = datetime.now()
        
        for service, budget in self.api_budget.items():
            if now >= budget['reset_time']:
                budget['used'] = 0
                if service == 'airtable':
                    budget['reset_time'] = now + timedelta(seconds=1)
                else:
                    budget['reset_time'] = now + timedelta(minutes=1)
                logger.debug(f"Reset API budget for {service}")
    
    def _can_use_api(self, service: str, count: int = 1) -> bool:
        """Check if we have API budget available"""
        budget = self.api_budget.get(service, {})
        return budget.get('used', 0) + count <= budget.get('total', 0)
    
    def _use_api_budget(self, service: str, count: int = 1):
        """Use API budget"""
        if service in self.api_budget:
            self.api_budget[service]['used'] += count
    
    async def update_cryptometer_cache(self, symbol: str, endpoints: List[str]):
        """
        Update Cryptometer cache for specific symbol and endpoints
        
        Args:
            symbol: Trading symbol
            endpoints: List of endpoints to update
        """
        if not self.cryptometer_cache:
            return
        
        updated = 0
        for endpoint in endpoints:
            # Check API budget
            if not self._can_use_api('cryptometer'):
                logger.warning(f"Cryptometer API budget exhausted, postponing {endpoint}:{symbol}")
                break
            
            # Check if update is needed
            cached_data = await self.cryptometer_cache.get(endpoint, symbol)
            if cached_data is None:
                # Simulate API call (in production, would call actual fetch function)
                logger.info(f"Would update Cryptometer {endpoint}:{symbol}")
                self._use_api_budget('cryptometer')
                updated += 1
                
                # Small delay between calls
                await asyncio.sleep(0.5)
        
        logger.debug(f"Updated {updated} Cryptometer endpoints for {symbol}")
    
    async def update_kingfisher_cache(self, symbol: str, image_types: List[str]):
        """
        Update KingFisher cache for specific symbol and image types
        
        Args:
            symbol: Trading symbol
            image_types: List of image types to update
        """
        if not self.kingfisher_cache:
            return
        
        updated = 0
        for image_type in image_types:
            # Check API budget
            if not self._can_use_api('kingfisher'):
                logger.warning(f"KingFisher API budget exhausted, postponing {image_type}:{symbol}")
                break
            
            # Check if update is needed
            cached_data = await self.kingfisher_cache.get('image_analysis', symbol, image_type)
            if cached_data is None:
                # Simulate API call (in production, would call actual fetch function)
                logger.info(f"Would update KingFisher {image_type}:{symbol}")
                self._use_api_budget('kingfisher')
                updated += 1
                
                # Small delay between calls
                await asyncio.sleep(1)
        
        logger.debug(f"Updated {updated} KingFisher image types for {symbol}")
    
    async def run_update_cycle(self):
        """
        Run a single update cycle for all monitored symbols
        Prioritizes updates based on data age and importance
        """
        logger.debug("Starting update cycle")
        
        # Reset API budgets if needed
        await self._reset_api_budgets()
        
        # Get current intervals based on strategy
        intervals = self.update_intervals[self.strategy]
        
        # Categorize data by priority
        critical_data = {
            'cryptometer': ['ticker', 'rapid_movements', 'ls_ratio'],
            'kingfisher': ['liquidation_map', 'rapid_movements']
        }
        
        high_priority = {
            'cryptometer': ['liquidation_data_v2', 'open_interest', 'trend_indicator_v3'],
            'kingfisher': ['rsi_heatmap', 'liq_heatmap']
        }
        
        medium_priority = {
            'cryptometer': ['ai_screener', 'ai_screener_analysis', 'tickerlist_pro'],
            'kingfisher': ['liq_ratio_shortterm']
        }
        
        low_priority = {
            'cryptometer': ['coinlist', 'cryptocurrency_info', 'coin_info', 'forex_rates'],
            'kingfisher': ['liq_ratio_longterm', 'professional_report']
        }
        
        # Process updates by priority
        for symbol in list(self.monitored_symbols):
            # Critical updates
            if self._should_update('critical', intervals['critical']):
                await self.update_cryptometer_cache(symbol, critical_data['cryptometer'])
                await self.update_kingfisher_cache(symbol, critical_data['kingfisher'])
            
            # High priority updates
            if self._should_update('high', intervals['high']):
                await self.update_cryptometer_cache(symbol, high_priority['cryptometer'])
                await self.update_kingfisher_cache(symbol, high_priority['kingfisher'])
            
            # Medium priority updates
            if self._should_update('medium', intervals['medium']):
                await self.update_cryptometer_cache(symbol, medium_priority['cryptometer'])
                await self.update_kingfisher_cache(symbol, medium_priority['kingfisher'])
            
            # Low priority updates
            if self._should_update('low', intervals['low']):
                await self.update_cryptometer_cache(symbol, low_priority['cryptometer'])
                await self.update_kingfisher_cache(symbol, low_priority['kingfisher'])
        
        logger.debug("Update cycle completed")
    
    def _should_update(self, priority: str, interval_minutes: int) -> bool:
        """
        Determine if data of given priority should be updated
        This is a simplified check - in production would track last update times
        """
        # For demo, use a simple probability based on interval
        import random
        # Higher probability for shorter intervals
        probability = 1.0 / (interval_minutes / 5)
        return random.random() < probability
    
    async def start(self):
        """
        Start the unified cache scheduler
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting Unified Cache Scheduler")
        
        # Connect cache managers
        if self.cryptometer_cache:
            await self.cryptometer_cache.connect()
        if self.kingfisher_cache:
            await self.kingfisher_cache.connect()
        
        # Main scheduler loop
        while self.running:
            try:
                # Run update cycle
                await self.run_update_cycle()
                
                # Adjust strategy based on API usage
                await self._adjust_strategy()
                
                # Wait before next cycle (varies by strategy)
                wait_time = self._get_cycle_interval()
                logger.debug(f"Waiting {wait_time}s before next cycle")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def stop(self):
        """
        Stop the unified cache scheduler
        """
        logger.info("Stopping Unified Cache Scheduler")
        self.running = False
        
        # Cancel all update tasks
        for task_id, task in self.update_tasks.items():
            if not task.done():
                task.cancel()
        
        # Disconnect cache managers
        if self.cryptometer_cache:
            await self.cryptometer_cache.disconnect()
        if self.kingfisher_cache:
            await self.kingfisher_cache.disconnect()
    
    async def _adjust_strategy(self):
        """
        Automatically adjust strategy based on API usage
        """
        # Calculate API usage percentage
        cryptometer_usage = (self.api_budget['cryptometer']['used'] / 
                           self.api_budget['cryptometer']['total'] * 100)
        kingfisher_usage = (self.api_budget['kingfisher']['used'] / 
                          self.api_budget['kingfisher']['total'] * 100)
        
        avg_usage = (cryptometer_usage + kingfisher_usage) / 2
        
        # Adjust strategy based on usage
        if avg_usage > 80 and self.strategy != UpdateStrategy.MINIMAL:
            logger.warning(f"High API usage ({avg_usage:.1f}%), switching to CONSERVATIVE strategy")
            self.set_strategy(UpdateStrategy.CONSERVATIVE)
        elif avg_usage > 90:
            logger.critical(f"Very high API usage ({avg_usage:.1f}%), switching to MINIMAL strategy")
            self.set_strategy(UpdateStrategy.MINIMAL)
        elif avg_usage < 40 and self.strategy == UpdateStrategy.CONSERVATIVE:
            logger.info(f"Low API usage ({avg_usage:.1f}%), switching back to NORMAL strategy")
            self.set_strategy(UpdateStrategy.NORMAL)
    
    def _get_cycle_interval(self) -> int:
        """
        Get wait time between update cycles based on strategy
        """
        intervals = {
            UpdateStrategy.AGGRESSIVE: 30,      # 30 seconds
            UpdateStrategy.NORMAL: 60,          # 1 minute
            UpdateStrategy.CONSERVATIVE: 120,   # 2 minutes
            UpdateStrategy.MINIMAL: 300         # 5 minutes
        }
        return intervals.get(self.strategy, 60)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current scheduler status
        """
        cryptometer_stats = self.cryptometer_cache.get_statistics() if self.cryptometer_cache else {}
        kingfisher_stats = self.kingfisher_cache.get_statistics() if self.kingfisher_cache else {}
        
        return {
            'running': self.running,
            'strategy': self.strategy.value,
            'monitored_symbols': list(self.monitored_symbols),
            'symbol_count': len(self.monitored_symbols),
            'api_budget': {
                service: {
                    'used': budget['used'],
                    'total': budget['total'],
                    'percentage': f"{(budget['used'] / budget['total'] * 100):.1f}%" if budget['total'] > 0 else "0%",
                    'reset_in': str(budget['reset_time'] - datetime.now())
                }
                for service, budget in self.api_budget.items()
            },
            'cache_statistics': {
                'cryptometer': cryptometer_stats,
                'kingfisher': kingfisher_stats
            },
            'active_tasks': len(self.update_tasks),
            'next_cycle_in': self._get_cycle_interval()
        }

# Create global instance
unified_scheduler = UnifiedCacheScheduler()

# Convenience functions
async def start_unified_cache_scheduler(symbols: List[str], 
                                       strategy: UpdateStrategy = UpdateStrategy.NORMAL):
    """
    Start the unified cache scheduler with initial configuration
    
    Args:
        symbols: List of symbols to monitor
        strategy: Initial update strategy
    """
    unified_scheduler.add_symbols(symbols)
    unified_scheduler.set_strategy(strategy)
    await unified_scheduler.start()

async def stop_unified_cache_scheduler():
    """
    Stop the unified cache scheduler
    """
    await unified_scheduler.stop()