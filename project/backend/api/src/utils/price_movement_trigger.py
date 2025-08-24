#!/usr/bin/env python3
"""
🎯 PRICE MOVEMENT TRIGGER SYSTEM
Only triggers Cryptometer API calls when there's significant price movement
Saves API calls by detecting when analysis is actually needed
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PriceSnapshot:
    """Single price snapshot"""
    timestamp: str
    price: float
    volume: float
    change_1m: float = 0.0
    change_5m: float = 0.0
    change_15m: float = 0.0

@dataclass
class MovementThresholds:
    """Movement detection thresholds - CONSERVATIVE TO SAVE API CALLS"""
    # Price change thresholds (%) - Much higher thresholds
    minor_movement: float = 3.0      # 3.0% - Only significant moves
    moderate_movement: float = 5.0   # 5.0% - Major moves only
    significant_movement: float = 8.0 # 8.0% - Very significant moves
    major_movement: float = 15.0     # 15.0% - Extreme moves only
    
    # Volume spike thresholds - Higher to reduce triggers
    volume_spike_2x: float = 5.0     # 5x average volume
    volume_spike_3x: float = 8.0     # 8x average volume
    volume_spike_5x: float = 12.0    # 12x average volume
    
    # Time windows for analysis
    fast_window: int = 15     # 15 minutes
    medium_window: int = 60   # 1 hour  
    slow_window: int = 240    # 4 hours

class PriceMovementTrigger:
    """
    🎯 Smart Price Movement Detection System
    
    Features:
    - Detects significant price movements
    - Volume spike detection
    - Multi-timeframe analysis
    - Priority-based API triggering
    - Historical price tracking
    - Movement trend analysis
    """
    
    def __init__(self, data_file: str = "config/price_movement_data.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        
        # Price history storage (symbol -> list of snapshots)
        self.price_history: Dict[str, List[PriceSnapshot]] = {}
        
        # Movement thresholds
        self.thresholds = MovementThresholds()
        
        # Last analysis timestamps to prevent spam
        self.last_analysis: Dict[str, datetime] = {}
        
        # Cooldown periods (minutes) based on priority - MUCH LONGER TO SAVE API CALLS
        self.analysis_cooldowns = {
            'critical': 30,   # 30 minute cooldown for critical movements
            'high': 60,       # 60 minute cooldown for significant movements  
            'medium': 120,    # 2 hour cooldown for moderate movements
            'low': 240        # 4 hour cooldown for minor movements
        }
        
        self._load_price_data()
        logger.info("🎯 Price Movement Trigger System initialized")
    
    def _load_price_data(self):
        """Load historical price data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                for symbol, snapshots_data in data.items():
                    self.price_history[symbol] = [
                        PriceSnapshot(**snapshot) for snapshot in snapshots_data
                    ]
                
                logger.info(f"📊 Loaded price history for {len(self.price_history)} symbols")
                
            except Exception as e:
                logger.error(f"❌ Error loading price data: {e}")
    
    def _save_price_data(self):
        """Save price data to file"""
        try:
            # Convert to serializable format
            data = {}
            for symbol, snapshots in self.price_history.items():
                data[symbol] = [asdict(snapshot) for snapshot in snapshots[-100:]]  # Keep last 100 snapshots
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving price data: {e}")
    
    def add_price_snapshot(self, symbol: str, price: float, volume: float) -> bool:
        """
        Add new price snapshot and return if analysis should be triggered
        
        Args:
            symbol: Trading symbol
            price: Current price
            volume: Current volume
            
        Returns:
            bool: True if Cryptometer analysis should be triggered
        """
        with self.lock:
            now = datetime.now()
            
            # Initialize symbol history if needed
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            history = self.price_history[symbol]
            
            # Calculate price changes
            change_1m, change_5m, change_15m = self._calculate_price_changes(history, price, now)
            
            # Create new snapshot
            snapshot = PriceSnapshot(
                timestamp=now.isoformat(),
                price=price,
                volume=volume,
                change_1m=change_1m,
                change_5m=change_5m,
                change_15m=change_15m
            )
            
            # Add to history
            history.append(snapshot)
            
            # Clean old snapshots (keep last 2 hours)
            cutoff = now - timedelta(hours=2)
            self.price_history[symbol] = [
                s for s in history 
                if datetime.fromisoformat(s.timestamp) > cutoff
            ]
            
            # Save data periodically
            if len(history) % 10 == 0:  # Save every 10 snapshots
                self._save_price_data()
            
            # Determine if analysis should be triggered
            should_trigger, priority = self._should_trigger_analysis(symbol, snapshot)
            
            if should_trigger:
                self.last_analysis[symbol] = now
                logger.info(f"🎯 TRIGGER: {symbol} analysis ({priority} priority) - Price: ${price:.4f}")
            
            return should_trigger
    
    def _calculate_price_changes(self, history: List[PriceSnapshot], current_price: float, now: datetime) -> Tuple[float, float, float]:
        """Calculate price changes over different timeframes"""
        if not history:
            return 0.0, 0.0, 0.0
        
        try:
            # Find snapshots at different time intervals
            change_1m = self._get_price_change(history, current_price, now, minutes=1)
            change_5m = self._get_price_change(history, current_price, now, minutes=5)
            change_15m = self._get_price_change(history, current_price, now, minutes=15)
            
            return change_1m, change_5m, change_15m
            
        except Exception as e:
            logger.error(f"❌ Error calculating price changes: {e}")
            return 0.0, 0.0, 0.0
    
    def _get_price_change(self, history: List[PriceSnapshot], current_price: float, now: datetime, minutes: int) -> float:
        """Get price change over specified minutes"""
        target_time = now - timedelta(minutes=minutes)
        
        # Find closest snapshot to target time
        closest_snapshot = None
        min_time_diff = float('inf')
        
        for snapshot in history:
            snapshot_time = datetime.fromisoformat(snapshot.timestamp)
            time_diff = abs((snapshot_time - target_time).total_seconds())
            
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_snapshot = snapshot
        
        if closest_snapshot and min_time_diff < 120:  # Within 2 minutes of target
            old_price = closest_snapshot.price
            if old_price > 0:
                return ((current_price - old_price) / old_price) * 100
        
        return 0.0
    
    def _should_trigger_analysis(self, symbol: str, snapshot: PriceSnapshot) -> Tuple[bool, str]:
        """Determine if analysis should be triggered and at what priority"""
        
        # 🎯 SPECIAL LOGIC: Check if price is ranging (sideways movement)
        is_ranging = self._is_price_ranging(symbol)
        if is_ranging:
            # In ranging market, be EXTREMELY conservative with API calls
            return self._handle_ranging_market(symbol, snapshot)
        
        # Check cooldown periods
        if symbol in self.last_analysis:
            last_analysis_time = self.last_analysis[symbol]
            time_since_last = (datetime.now() - last_analysis_time).total_seconds() / 60
            
            # Determine minimum cooldown based on recent movement intensity
            max_change = max(abs(snapshot.change_1m), abs(snapshot.change_5m), abs(snapshot.change_15m))
            
            if max_change >= self.thresholds.major_movement:
                min_cooldown = self.analysis_cooldowns['critical']
                priority = 'critical'
            elif max_change >= self.thresholds.significant_movement:
                min_cooldown = self.analysis_cooldowns['high']
                priority = 'high'
            elif max_change >= self.thresholds.moderate_movement:
                min_cooldown = self.analysis_cooldowns['medium']
                priority = 'medium'
            else:
                min_cooldown = self.analysis_cooldowns['low']
                priority = 'low'
            
            if time_since_last < min_cooldown:
                return False, priority  # Still in cooldown
        else:
            # First analysis for this symbol
            max_change = max(abs(snapshot.change_1m), abs(snapshot.change_5m), abs(snapshot.change_15m))
            if max_change >= self.thresholds.moderate_movement:
                priority = 'high' if max_change >= self.thresholds.significant_movement else 'medium'
            else:
                priority = 'low'
        
        # Check movement thresholds
        should_trigger = False
        
        # Major movement (always trigger)
        if (abs(snapshot.change_1m) >= self.thresholds.major_movement or
            abs(snapshot.change_5m) >= self.thresholds.major_movement or
            abs(snapshot.change_15m) >= self.thresholds.major_movement):
            should_trigger = True
            priority = 'critical'
        
        # Significant movement
        elif (abs(snapshot.change_1m) >= self.thresholds.significant_movement or
              abs(snapshot.change_5m) >= self.thresholds.significant_movement):
            should_trigger = True
            priority = 'high'
        
        # Moderate movement
        elif (abs(snapshot.change_5m) >= self.thresholds.moderate_movement or
              abs(snapshot.change_15m) >= self.thresholds.moderate_movement):
            should_trigger = True
            priority = 'medium'
        
        # Minor movement (only trigger very rarely)
        elif abs(snapshot.change_15m) >= self.thresholds.minor_movement:
            # Only trigger minor movements if no analysis in the last 6 hours
            if symbol not in self.last_analysis:
                # Only 20% chance even for first analysis of minor movements
                import random
                if random.random() < 0.2:
                    should_trigger = True
                    priority = 'low'
            else:
                last_analysis_time = self.last_analysis[symbol]
                hours_since_last = (datetime.now() - last_analysis_time).total_seconds() / 3600
                if hours_since_last > 6:  # 6 hours minimum for minor movements
                    should_trigger = True
                    priority = 'low'
        
        # Volume spike analysis
        volume_priority = self._check_volume_spike(symbol, snapshot.volume)
        if volume_priority:
            should_trigger = True
            # Use higher priority of price movement or volume spike
            if volume_priority == 'critical' or priority == 'critical':
                priority = 'critical'
            elif volume_priority == 'high' or priority == 'high':
                priority = 'high'
            elif volume_priority == 'medium':
                priority = 'medium' if priority == 'low' else priority
        
        return should_trigger, priority
    
    def _check_volume_spike(self, symbol: str, current_volume: float) -> Optional[str]:
        """Check for volume spikes"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 10:
            return None
        
        # Get recent volume history
        recent_history = self.price_history[symbol][-20:]  # Last 20 snapshots
        recent_volumes = [s.volume for s in recent_history if s.volume > 0]
        
        if len(recent_volumes) < 5:
            return None
        
        # Calculate average volume
        avg_volume = statistics.mean(recent_volumes)
        
        if avg_volume <= 0:
            return None
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio >= self.thresholds.volume_spike_5x:
            return 'critical'
        elif volume_ratio >= self.thresholds.volume_spike_3x:
            return 'high'
        elif volume_ratio >= self.thresholds.volume_spike_2x:
            return 'medium'
        
        return None
    
    def get_trigger_status(self, symbol: str) -> Dict[str, Any]:
        """Get current trigger status for a symbol"""
        if symbol not in self.price_history or not self.price_history[symbol]:
            return {'status': 'no_data', 'last_analysis': None}
        
        latest = self.price_history[symbol][-1]
        last_analysis = self.last_analysis.get(symbol)
        
        return {
            'symbol': symbol,
            'latest_price': latest.price,
            'change_1m': latest.change_1m,
            'change_5m': latest.change_5m,
            'change_15m': latest.change_15m,
            'volume': latest.volume,
            'last_analysis': last_analysis.isoformat() if last_analysis else None,
            'snapshots_count': len(self.price_history[symbol])
        }
    
    def force_trigger(self, symbol: str) -> bool:
        """Force trigger analysis for a symbol (admin function)"""
        with self.lock:
            self.last_analysis[symbol] = datetime.now()
            logger.info(f"🔧 Force triggered analysis for {symbol}")
            return True
    
    def _is_price_ranging(self, symbol: str) -> bool:
        """
        Detect if price is ranging (sideways movement) vs trending
        Returns True if price is in a range, False if trending/volatile
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 20:
            return False  # Not enough data, allow API calls
        
        recent_snapshots = self.price_history[symbol][-20:]  # Last 20 snapshots
        prices = [s.price for s in recent_snapshots]
        
        if not prices:
            return False
        
        # Calculate price range metrics
        min_price = min(prices)
        max_price = max(prices)
        current_price = prices[-1]
        
        # Calculate range percentage
        if min_price > 0:
            range_percentage = ((max_price - min_price) / min_price) * 100
        else:
            return False
        
        # If price range is less than 2% over last 20 snapshots, consider it ranging
        is_narrow_range = range_percentage < 2.0
        
        # Check if price is staying within middle 60% of the range
        range_size = max_price - min_price
        middle_zone_low = min_price + (range_size * 0.2)   # 20% from bottom
        middle_zone_high = max_price - (range_size * 0.2)  # 20% from top
        
        is_in_middle_zone = middle_zone_low <= current_price <= middle_zone_high
        
        # Additional check: low volatility over time
        recent_changes = [abs(s.change_5m) for s in recent_snapshots[-10:] if s.change_5m != 0]
        avg_change = sum(recent_changes) / len(recent_changes) if recent_changes else 0
        is_low_volatility = avg_change < 1.0  # Average 5m change less than 1%
        
        is_ranging = is_narrow_range and is_in_middle_zone and is_low_volatility
        
        if is_ranging:
            logger.debug(f"📊 {symbol} detected as RANGING - Range: {range_percentage:.2f}%, Volatility: {avg_change:.2f}%")
        
        return is_ranging
    
    def _handle_ranging_market(self, symbol: str, snapshot: PriceSnapshot) -> Tuple[bool, str]:
        """
        Handle API calls when market is ranging - VERY CONSERVATIVE
        Only trigger on major breakouts from range
        """
        # In ranging market, only trigger on MAJOR movements that might indicate breakout
        max_change = max(abs(snapshot.change_1m), abs(snapshot.change_5m), abs(snapshot.change_15m))
        
        # Even more restrictive thresholds for ranging markets
        ranging_thresholds = {
            'breakout': 5.0,      # 5% move might be range breakout
            'strong_breakout': 8.0, # 8% move likely breakout
            'major_breakout': 12.0  # 12% move definitely breakout
        }
        
        # Check cooldown - much longer in ranging markets
        if symbol in self.last_analysis:
            last_analysis_time = self.last_analysis[symbol]
            hours_since_last = (datetime.now() - last_analysis_time).total_seconds() / 3600
            
            # Minimum 4 hours between API calls in ranging market
            if hours_since_last < 4:
                return False, 'ranging_cooldown'
        
        # Only trigger on potential range breakouts
        if max_change >= ranging_thresholds['major_breakout']:
            logger.info(f"🚨 {symbol} MAJOR BREAKOUT from range: {max_change:.2f}% move")
            return True, 'critical'
        elif max_change >= ranging_thresholds['strong_breakout']:
            logger.info(f"⚡ {symbol} Strong breakout from range: {max_change:.2f}% move")
            return True, 'high'
        elif max_change >= ranging_thresholds['breakout']:
            # Only 10% chance for minor breakouts to save API calls
            import random
            if random.random() < 0.1:
                logger.info(f"📈 {symbol} Possible breakout from range: {max_change:.2f}% move")
                return True, 'medium'
        
        # Stay silent in ranging markets
        logger.debug(f"🔇 {symbol} ranging - suppressing API call (change: {max_change:.2f}%)")
        return False, 'ranging_suppressed'
    
    def get_market_state(self, symbol: str) -> Dict[str, Any]:
        """Get detailed market state information"""
        if symbol not in self.price_history or not self.price_history[symbol]:
            return {'state': 'no_data'}
        
        is_ranging = self._is_price_ranging(symbol)
        latest = self.price_history[symbol][-1]
        
        # Calculate additional metrics
        recent_prices = [s.price for s in self.price_history[symbol][-10:]]
        price_std = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0
        price_mean = statistics.mean(recent_prices)
        volatility = (price_std / price_mean * 100) if price_mean > 0 else 0
        
        return {
            'symbol': symbol,
            'state': 'ranging' if is_ranging else 'trending',
            'latest_price': latest.price,
            'volatility': volatility,
            'change_1m': latest.change_1m,
            'change_5m': latest.change_5m,
            'change_15m': latest.change_15m,
            'api_calls_suppressed': is_ranging
        }
    
    def set_thresholds(self, **kwargs):
        """Update movement thresholds"""
        for key, value in kwargs.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)
                logger.info(f"🎯 Updated threshold {key} = {value}")

# Global instance
price_movement_trigger = PriceMovementTrigger()

# Helper functions
def should_trigger_cryptometer_analysis(symbol: str, price: float, volume: float) -> bool:
    """Check if Cryptometer analysis should be triggered"""
    return price_movement_trigger.add_price_snapshot(symbol, price, volume)

def get_price_trigger_status(symbol: str) -> Dict[str, Any]:
    """Get price trigger status for symbol"""
    return price_movement_trigger.get_trigger_status(symbol)

def force_trigger_analysis(symbol: str) -> bool:
    """Force trigger analysis"""
    return price_movement_trigger.force_trigger(symbol)