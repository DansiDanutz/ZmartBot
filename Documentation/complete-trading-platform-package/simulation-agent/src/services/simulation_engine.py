"""
Simulation Agent - Core Simulation Engine
========================================

Advanced simulation engine for trading pattern analysis and win ratio calculation.
Integrates with KingFisher, Cryptometer, and RiskMetric data sources.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import ta  # Technical Analysis library
import warnings
warnings.filterwarnings('ignore')

from ..core.config import config
from ..models.base import SimulationResult, PatternMatch, WinRatioAnalysis

logger = logging.getLogger(__name__)

@dataclass
class MarketCondition:
    """Represents a specific market condition for analysis"""
    
    condition_type: str  # trending_up, trending_down, ranging, etc.
    start_time: datetime
    end_time: datetime
    volatility: float
    volume_profile: str
    dominant_pattern: Optional[str] = None
    confidence: float = 0.0
    
    def duration_hours(self) -> float:
        """Calculate duration in hours"""
        return (self.end_time - self.start_time).total_seconds() / 3600

@dataclass
class TradingSignal:
    """Represents a trading signal with context"""
    
    timestamp: datetime
    symbol: str
    direction: str  # long or short
    entry_price: Decimal
    confidence: float
    signal_source: str  # kingfisher, cryptometer, riskmetric
    market_condition: MarketCondition
    technical_indicators: Dict[str, float] = field(default_factory=dict)
    fundamental_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SimulationTrade:
    """Represents a simulated trade with complete lifecycle"""
    
    trade_id: str
    symbol: str
    direction: str
    entry_time: datetime
    entry_price: Decimal
    position_size: Decimal
    leverage: int
    
    # Exit information (filled when trade closes)
    exit_time: Optional[datetime] = None
    exit_price: Optional[Decimal] = None
    exit_reason: Optional[str] = None
    
    # Performance metrics
    pnl: Optional[Decimal] = None
    pnl_percentage: Optional[Decimal] = None
    duration_hours: Optional[float] = None
    max_favorable_excursion: Optional[Decimal] = None
    max_adverse_excursion: Optional[Decimal] = None
    
    # Risk metrics
    max_drawdown: Optional[Decimal] = None
    risk_reward_ratio: Optional[float] = None
    
    def is_winner(self) -> bool:
        """Check if trade is profitable"""
        return self.pnl is not None and self.pnl > 0
    
    def calculate_metrics(self, price_data: pd.DataFrame):
        """Calculate comprehensive trade metrics"""
        if self.exit_time is None or self.exit_price is None:
            return
        
        # Basic PnL calculation
        if self.direction == "long":
            self.pnl = (self.exit_price - self.entry_price) * self.position_size * self.leverage
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.position_size * self.leverage
        
        self.pnl_percentage = (self.pnl / (self.entry_price * self.position_size)) * 100
        self.duration_hours = (self.exit_time - self.entry_time).total_seconds() / 3600
        
        # Calculate excursions during trade
        trade_data = price_data[
            (price_data.index >= self.entry_time) & 
            (price_data.index <= self.exit_time)
        ]
        
        if not trade_data.empty:
            if self.direction == "long":
                self.max_favorable_excursion = (trade_data['high'].max() - self.entry_price) * self.position_size * self.leverage
                self.max_adverse_excursion = (self.entry_price - trade_data['low'].min()) * self.position_size * self.leverage
            else:
                self.max_favorable_excursion = (self.entry_price - trade_data['low'].min()) * self.position_size * self.leverage
                self.max_adverse_excursion = (trade_data['high'].max() - self.entry_price) * self.position_size * self.leverage

class PatternRecognitionEngine:
    """Advanced pattern recognition for trading signals"""
    
    def __init__(self):
        self.patterns = {
            'head_and_shoulders': self._detect_head_and_shoulders,
            'double_top': self._detect_double_top,
            'double_bottom': self._detect_double_bottom,
            'triangle': self._detect_triangle,
            'flag': self._detect_flag,
            'wedge': self._detect_wedge,
            'support_resistance': self._detect_support_resistance,
            'breakout': self._detect_breakout,
            'liquidation_cluster': self._detect_liquidation_cluster
        }
        
        self.confidence_thresholds = {
            'head_and_shoulders': 0.75,
            'double_top': 0.70,
            'double_bottom': 0.70,
            'triangle': 0.65,
            'flag': 0.60,
            'wedge': 0.65,
            'support_resistance': 0.80,
            'breakout': 0.70,
            'liquidation_cluster': 0.85
        }
    
    async def detect_patterns(self, price_data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect all patterns in price data"""
        
        patterns_found = []
        
        for pattern_name, detector_func in self.patterns.items():
            try:
                matches = await detector_func(price_data, kingfisher_data)
                for match in matches:
                    if match.confidence >= self.confidence_thresholds[pattern_name]:
                        patterns_found.append(match)
                        
            except Exception as e:
                logger.error(f"Error detecting {pattern_name}: {str(e)}")
        
        # Sort by confidence and timestamp
        patterns_found.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)
        
        return patterns_found
    
    async def _detect_head_and_shoulders(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect head and shoulders patterns"""
        patterns = []
        
        if len(data) < 50:
            return patterns
        
        # Use rolling windows to find potential patterns
        window_size = 20
        for i in range(window_size, len(data) - window_size):
            window = data.iloc[i-window_size:i+window_size]
            
            # Find local maxima
            highs = window['high'].rolling(5).max()
            peaks = []
            
            for j in range(4, len(highs) - 4):
                if (highs.iloc[j] > highs.iloc[j-2:j].max() and 
                    highs.iloc[j] > highs.iloc[j+1:j+3].max()):
                    peaks.append((j, highs.iloc[j]))
            
            # Check for head and shoulders pattern
            if len(peaks) >= 3:
                # Sort peaks by height
                peaks.sort(key=lambda x: x[1], reverse=True)
                
                # Head should be highest, shoulders should be similar
                head = peaks[0]
                potential_shoulders = [p for p in peaks[1:] if abs(p[1] - peaks[1][1]) / peaks[1][1] < 0.05]
                
                if len(potential_shoulders) >= 1:
                    confidence = 0.6 + (0.2 if len(potential_shoulders) >= 2 else 0)
                    
                    # Increase confidence if KingFisher shows resistance at head level
                    if kingfisher_data and 'liquidation_clusters' in kingfisher_data:
                        clusters = kingfisher_data['liquidation_clusters']
                        head_price = head[1]
                        
                        for cluster in clusters:
                            if abs(cluster.get('price', 0) - head_price) / head_price < 0.02:
                                confidence += 0.15
                                break
                    
                    pattern = PatternMatch(
                        pattern_type='head_and_shoulders',
                        timestamp=data.index[i],
                        confidence=min(confidence, 1.0),
                        price_level=head[1],
                        direction='bearish',
                        target_price=head[1] * 0.95,  # 5% target
                        stop_loss=head[1] * 1.02,     # 2% stop
                        metadata={
                            'head_price': head[1],
                            'shoulder_count': len(potential_shoulders),
                            'pattern_duration': window_size * 2
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_double_top(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect double top patterns"""
        patterns = []
        
        if len(data) < 30:
            return patterns
        
        # Find significant highs
        highs = data['high'].rolling(10, center=True).max()
        significant_highs = []
        
        for i in range(10, len(data) - 10):
            if data['high'].iloc[i] == highs.iloc[i] and data['high'].iloc[i] > data['high'].iloc[i-10:i+10].quantile(0.9):
                significant_highs.append((i, data['high'].iloc[i]))
        
        # Look for double tops
        for i in range(len(significant_highs) - 1):
            for j in range(i + 1, len(significant_highs)):
                high1_idx, high1_price = significant_highs[i]
                high2_idx, high2_price = significant_highs[j]
                
                # Check if highs are similar (within 2%)
                if abs(high1_price - high2_price) / high1_price < 0.02:
                    # Check if there's a valley between them
                    valley_data = data.iloc[high1_idx:high2_idx]
                    valley_low = valley_data['low'].min()
                    
                    if valley_low < high1_price * 0.95:  # At least 5% retracement
                        confidence = 0.65
                        
                        # Increase confidence with KingFisher resistance data
                        if kingfisher_data and 'liquidation_clusters' in kingfisher_data:
                            for cluster in kingfisher_data['liquidation_clusters']:
                                cluster_price = cluster.get('price', 0)
                                if abs(cluster_price - high1_price) / high1_price < 0.015:
                                    confidence += 0.1
                                    break
                        
                        pattern = PatternMatch(
                            pattern_type='double_top',
                            timestamp=data.index[high2_idx],
                            confidence=min(confidence, 1.0),
                            price_level=high2_price,
                            direction='bearish',
                            target_price=valley_low,
                            stop_loss=high2_price * 1.03,
                            metadata={
                                'first_top': high1_price,
                                'second_top': high2_price,
                                'valley_low': valley_low,
                                'pattern_duration': high2_idx - high1_idx
                            }
                        )
                        patterns.append(pattern)
        
        return patterns
    
    async def _detect_double_bottom(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect double bottom patterns"""
        patterns = []
        
        if len(data) < 30:
            return patterns
        
        # Find significant lows
        lows = data['low'].rolling(10, center=True).min()
        significant_lows = []
        
        for i in range(10, len(data) - 10):
            if data['low'].iloc[i] == lows.iloc[i] and data['low'].iloc[i] < data['low'].iloc[i-10:i+10].quantile(0.1):
                significant_lows.append((i, data['low'].iloc[i]))
        
        # Look for double bottoms
        for i in range(len(significant_lows) - 1):
            for j in range(i + 1, len(significant_lows)):
                low1_idx, low1_price = significant_lows[i]
                low2_idx, low2_price = significant_lows[j]
                
                # Check if lows are similar (within 2%)
                if abs(low1_price - low2_price) / low1_price < 0.02:
                    # Check if there's a peak between them
                    peak_data = data.iloc[low1_idx:low2_idx]
                    peak_high = peak_data['high'].max()
                    
                    if peak_high > low1_price * 1.05:  # At least 5% bounce
                        confidence = 0.65
                        
                        # Increase confidence with KingFisher support data
                        if kingfisher_data and 'liquidation_clusters' in kingfisher_data:
                            for cluster in kingfisher_data['liquidation_clusters']:
                                cluster_price = cluster.get('price', 0)
                                if abs(cluster_price - low1_price) / low1_price < 0.015:
                                    confidence += 0.1
                                    break
                        
                        pattern = PatternMatch(
                            pattern_type='double_bottom',
                            timestamp=data.index[low2_idx],
                            confidence=min(confidence, 1.0),
                            price_level=low2_price,
                            direction='bullish',
                            target_price=peak_high,
                            stop_loss=low2_price * 0.97,
                            metadata={
                                'first_bottom': low1_price,
                                'second_bottom': low2_price,
                                'peak_high': peak_high,
                                'pattern_duration': low2_idx - low1_idx
                            }
                        )
                        patterns.append(pattern)
        
        return patterns
    
    async def _detect_triangle(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        patterns = []
        
        if len(data) < 50:
            return patterns
        
        window_size = 30
        for i in range(window_size, len(data) - 10):
            window = data.iloc[i-window_size:i]
            
            # Find trend lines for highs and lows
            highs = []
            lows = []
            
            for j in range(5, len(window) - 5):
                if window['high'].iloc[j] == window['high'].iloc[j-5:j+5].max():
                    highs.append((j, window['high'].iloc[j]))
                if window['low'].iloc[j] == window['low'].iloc[j-5:j+5].min():
                    lows.append((j, window['low'].iloc[j]))
            
            if len(highs) >= 3 and len(lows) >= 3:
                # Calculate trend lines
                high_x = [h[0] for h in highs]
                high_y = [h[1] for h in highs]
                low_x = [l[0] for l in lows]
                low_y = [l[1] for l in lows]
                
                # Linear regression for trend lines
                high_slope, high_intercept, high_r, _, _ = stats.linregress(high_x, high_y)
                low_slope, low_intercept, low_r, _, _ = stats.linregress(low_x, low_y)
                
                # Check for triangle patterns
                triangle_type = None
                confidence = 0.5
                
                if abs(high_r) > 0.7 and abs(low_r) > 0.7:  # Strong trend lines
                    if abs(high_slope) < 0.001 and low_slope > 0.001:  # Ascending triangle
                        triangle_type = 'ascending'
                        confidence = 0.7
                        direction = 'bullish'
                    elif high_slope < -0.001 and abs(low_slope) < 0.001:  # Descending triangle
                        triangle_type = 'descending'
                        confidence = 0.7
                        direction = 'bearish'
                    elif high_slope < -0.001 and low_slope > 0.001:  # Symmetrical triangle
                        triangle_type = 'symmetrical'
                        confidence = 0.65
                        direction = 'neutral'
                    
                    if triangle_type:
                        current_price = data['close'].iloc[i]
                        
                        pattern = PatternMatch(
                            pattern_type=f'{triangle_type}_triangle',
                            timestamp=data.index[i],
                            confidence=confidence,
                            price_level=current_price,
                            direction=direction,
                            target_price=current_price * (1.05 if direction == 'bullish' else 0.95),
                            stop_loss=current_price * (0.98 if direction == 'bullish' else 1.02),
                            metadata={
                                'triangle_type': triangle_type,
                                'high_slope': high_slope,
                                'low_slope': low_slope,
                                'high_r_squared': high_r**2,
                                'low_r_squared': low_r**2,
                                'pattern_duration': window_size
                            }
                        )
                        patterns.append(pattern)
        
        return patterns
    
    async def _detect_flag(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect flag patterns (bullish and bearish)"""
        patterns = []
        
        if len(data) < 40:
            return patterns
        
        # Look for strong moves followed by consolidation
        for i in range(20, len(data) - 20):
            # Check for strong move (flagpole)
            flagpole_start = i - 20
            flagpole_end = i - 5
            flagpole_data = data.iloc[flagpole_start:flagpole_end]
            
            # Calculate move strength
            move_start = flagpole_data['close'].iloc[0]
            move_end = flagpole_data['close'].iloc[-1]
            move_percent = abs(move_end - move_start) / move_start
            
            if move_percent > 0.05:  # At least 5% move
                # Check for consolidation (flag)
                flag_data = data.iloc[flagpole_end:i+15]
                flag_volatility = flag_data['high'].max() / flag_data['low'].min() - 1
                
                if flag_volatility < 0.03:  # Low volatility consolidation
                    direction = 'bullish' if move_end > move_start else 'bearish'
                    confidence = 0.6 + (0.1 if move_percent > 0.08 else 0)
                    
                    current_price = data['close'].iloc[i]
                    
                    pattern = PatternMatch(
                        pattern_type='flag',
                        timestamp=data.index[i],
                        confidence=confidence,
                        price_level=current_price,
                        direction=direction,
                        target_price=current_price * (1 + move_percent if direction == 'bullish' else 1 - move_percent),
                        stop_loss=current_price * (0.98 if direction == 'bullish' else 1.02),
                        metadata={
                            'flagpole_move_percent': move_percent,
                            'flag_volatility': flag_volatility,
                            'flagpole_duration': flagpole_end - flagpole_start,
                            'flag_duration': 15
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_wedge(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect wedge patterns (rising and falling)"""
        patterns = []
        
        if len(data) < 40:
            return patterns
        
        window_size = 25
        for i in range(window_size, len(data) - 10):
            window = data.iloc[i-window_size:i]
            
            # Find highs and lows
            highs = []
            lows = []
            
            for j in range(3, len(window) - 3):
                if window['high'].iloc[j] == window['high'].iloc[j-3:j+3].max():
                    highs.append((j, window['high'].iloc[j]))
                if window['low'].iloc[j] == window['low'].iloc[j-3:j+3].min():
                    lows.append((j, window['low'].iloc[j]))
            
            if len(highs) >= 3 and len(lows) >= 3:
                # Calculate trend lines
                high_x = [h[0] for h in highs]
                high_y = [h[1] for h in highs]
                low_x = [l[0] for l in lows]
                low_y = [l[1] for l in lows]
                
                high_slope, _, high_r, _, _ = stats.linregress(high_x, high_y)
                low_slope, _, low_r, _, _ = stats.linregress(low_x, low_y)
                
                # Check for wedge patterns
                if abs(high_r) > 0.6 and abs(low_r) > 0.6:
                    if high_slope > 0 and low_slope > 0 and high_slope < low_slope:  # Rising wedge
                        wedge_type = 'rising'
                        direction = 'bearish'
                        confidence = 0.65
                    elif high_slope < 0 and low_slope < 0 and high_slope > low_slope:  # Falling wedge
                        wedge_type = 'falling'
                        direction = 'bullish'
                        confidence = 0.65
                    else:
                        continue
                    
                    current_price = data['close'].iloc[i]
                    
                    pattern = PatternMatch(
                        pattern_type=f'{wedge_type}_wedge',
                        timestamp=data.index[i],
                        confidence=confidence,
                        price_level=current_price,
                        direction=direction,
                        target_price=current_price * (1.04 if direction == 'bullish' else 0.96),
                        stop_loss=current_price * (0.98 if direction == 'bullish' else 1.02),
                        metadata={
                            'wedge_type': wedge_type,
                            'high_slope': high_slope,
                            'low_slope': low_slope,
                            'convergence_rate': abs(high_slope - low_slope)
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_support_resistance(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect support and resistance levels"""
        patterns = []
        
        if len(data) < 50:
            return patterns
        
        # Find significant price levels with multiple touches
        price_levels = {}
        tolerance = 0.02  # 2% tolerance for level matching
        
        # Collect all highs and lows
        for i in range(10, len(data) - 10):
            if data['high'].iloc[i] == data['high'].iloc[i-10:i+10].max():
                price = data['high'].iloc[i]
                timestamp = data.index[i]
                
                # Find matching levels
                matched = False
                for level, touches in price_levels.items():
                    if abs(price - level) / level < tolerance:
                        touches.append((timestamp, price, 'resistance'))
                        matched = True
                        break
                
                if not matched:
                    price_levels[price] = [(timestamp, price, 'resistance')]
            
            if data['low'].iloc[i] == data['low'].iloc[i-10:i+10].min():
                price = data['low'].iloc[i]
                timestamp = data.index[i]
                
                # Find matching levels
                matched = False
                for level, touches in price_levels.items():
                    if abs(price - level) / level < tolerance:
                        touches.append((timestamp, price, 'support'))
                        matched = True
                        break
                
                if not matched:
                    price_levels[price] = [(timestamp, price, 'support')]
        
        # Identify significant levels (3+ touches)
        for level, touches in price_levels.items():
            if len(touches) >= 3:
                level_type = max(set([t[2] for t in touches]), key=[t[2] for t in touches].count)
                confidence = min(0.8, 0.5 + len(touches) * 0.1)
                
                # Increase confidence if KingFisher confirms the level
                if kingfisher_data and 'liquidation_clusters' in kingfisher_data:
                    for cluster in kingfisher_data['liquidation_clusters']:
                        cluster_price = cluster.get('price', 0)
                        if abs(cluster_price - level) / level < 0.01:
                            confidence += 0.15
                            break
                
                latest_touch = max(touches, key=lambda x: x[0])
                
                pattern = PatternMatch(
                    pattern_type=f'{level_type}_level',
                    timestamp=latest_touch[0],
                    confidence=min(confidence, 1.0),
                    price_level=level,
                    direction='bullish' if level_type == 'support' else 'bearish',
                    target_price=level * (1.03 if level_type == 'support' else 0.97),
                    stop_loss=level * (0.98 if level_type == 'support' else 1.02),
                    metadata={
                        'touch_count': len(touches),
                        'level_type': level_type,
                        'first_touch': min(touches, key=lambda x: x[0])[0],
                        'latest_touch': latest_touch[0],
                        'average_price': sum([t[1] for t in touches]) / len(touches)
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_breakout(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect breakout patterns from consolidation"""
        patterns = []
        
        if len(data) < 30:
            return patterns
        
        # Look for consolidation followed by breakout
        for i in range(20, len(data) - 5):
            # Check for consolidation period
            consolidation_data = data.iloc[i-20:i]
            consolidation_range = consolidation_data['high'].max() / consolidation_data['low'].min() - 1
            
            if consolidation_range < 0.05:  # Tight consolidation (5% range)
                # Check for breakout
                breakout_data = data.iloc[i:i+5]
                consolidation_high = consolidation_data['high'].max()
                consolidation_low = consolidation_data['low'].min()
                
                breakout_high = breakout_data['high'].max()
                breakout_low = breakout_data['low'].min()
                
                # Upward breakout
                if breakout_high > consolidation_high * 1.02:  # 2% breakout
                    volume_surge = False
                    if 'volume' in data.columns:
                        avg_volume = consolidation_data['volume'].mean()
                        breakout_volume = breakout_data['volume'].max()
                        volume_surge = breakout_volume > avg_volume * 1.5
                    
                    confidence = 0.65 + (0.1 if volume_surge else 0)
                    
                    pattern = PatternMatch(
                        pattern_type='upward_breakout',
                        timestamp=data.index[i],
                        confidence=confidence,
                        price_level=consolidation_high,
                        direction='bullish',
                        target_price=consolidation_high * (1 + consolidation_range),
                        stop_loss=consolidation_high * 0.98,
                        metadata={
                            'consolidation_range': consolidation_range,
                            'breakout_strength': (breakout_high - consolidation_high) / consolidation_high,
                            'volume_surge': volume_surge,
                            'consolidation_duration': 20
                        }
                    )
                    patterns.append(pattern)
                
                # Downward breakout
                elif breakout_low < consolidation_low * 0.98:  # 2% breakdown
                    volume_surge = False
                    if 'volume' in data.columns:
                        avg_volume = consolidation_data['volume'].mean()
                        breakout_volume = breakout_data['volume'].max()
                        volume_surge = breakout_volume > avg_volume * 1.5
                    
                    confidence = 0.65 + (0.1 if volume_surge else 0)
                    
                    pattern = PatternMatch(
                        pattern_type='downward_breakout',
                        timestamp=data.index[i],
                        confidence=confidence,
                        price_level=consolidation_low,
                        direction='bearish',
                        target_price=consolidation_low * (1 - consolidation_range),
                        stop_loss=consolidation_low * 1.02,
                        metadata={
                            'consolidation_range': consolidation_range,
                            'breakout_strength': (consolidation_low - breakout_low) / consolidation_low,
                            'volume_surge': volume_surge,
                            'consolidation_duration': 20
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_liquidation_cluster(self, data: pd.DataFrame, kingfisher_data: Dict = None) -> List[PatternMatch]:
        """Detect liquidation cluster patterns using KingFisher data"""
        patterns = []
        
        if not kingfisher_data or 'liquidation_clusters' not in kingfisher_data:
            return patterns
        
        clusters = kingfisher_data['liquidation_clusters']
        current_price = data['close'].iloc[-1]
        
        for cluster in clusters:
            cluster_price = cluster.get('price', 0)
            cluster_size = cluster.get('size', 0)
            cluster_type = cluster.get('type', 'unknown')  # long_liquidations or short_liquidations
            
            if cluster_price == 0:
                continue
            
            # Calculate distance from current price
            distance_percent = abs(cluster_price - current_price) / current_price
            
            # Only consider clusters within 10% of current price
            if distance_percent < 0.10:
                # Determine direction based on cluster type and position
                if cluster_type == 'long_liquidations' and cluster_price < current_price:
                    direction = 'bearish'  # Price might fall to trigger long liquidations
                elif cluster_type == 'short_liquidations' and cluster_price > current_price:
                    direction = 'bullish'  # Price might rise to trigger short liquidations
                else:
                    continue
                
                # Calculate confidence based on cluster size and proximity
                base_confidence = 0.7
                size_bonus = min(0.2, cluster_size / 10000000)  # Bonus for large clusters
                proximity_bonus = 0.1 * (1 - distance_percent / 0.10)  # Bonus for closer clusters
                
                confidence = base_confidence + size_bonus + proximity_bonus
                
                # Set target and stop loss
                if direction == 'bullish':
                    target_price = cluster_price * 1.02  # 2% beyond cluster
                    stop_loss = current_price * 0.98
                else:
                    target_price = cluster_price * 0.98  # 2% beyond cluster
                    stop_loss = current_price * 1.02
                
                pattern = PatternMatch(
                    pattern_type='liquidation_cluster',
                    timestamp=data.index[-1],
                    confidence=min(confidence, 1.0),
                    price_level=cluster_price,
                    direction=direction,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    metadata={
                        'cluster_type': cluster_type,
                        'cluster_size': cluster_size,
                        'distance_percent': distance_percent,
                        'current_price': current_price
                    }
                )
                patterns.append(pattern)
        
        return patterns

class SimulationEngine:
    """Core simulation engine for trading pattern analysis"""
    
    def __init__(self):
        self.pattern_engine = PatternRecognitionEngine()
        self.ml_models = {}
        self.scalers = {}
        self.performance_cache = {}
        
        # Initialize ML models
        self._initialize_ml_models()
        
        logger.info("Simulation Engine initialized successfully")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for pattern prediction"""
        
        self.ml_models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            ),
            'svm': SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            )
        }
        
        # Initialize scalers for each model
        for model_name in self.ml_models.keys():
            self.scalers[model_name] = StandardScaler()
    
    async def analyze_symbol(
        self,
        symbol: str,
        lookback_days: int = 365,
        kingfisher_data: Dict = None,
        cryptometer_data: Dict = None,
        riskmetric_data: Dict = None
    ) -> SimulationResult:
        """
        Comprehensive analysis of a trading symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            lookback_days: Number of days to analyze
            kingfisher_data: KingFisher analysis data
            cryptometer_data: Cryptometer API data
            riskmetric_data: RiskMetric scoring data
        
        Returns:
            SimulationResult with comprehensive analysis
        """
        
        logger.info(f"Starting comprehensive analysis for {symbol}")
        
        try:
            # Get historical price data (this would be implemented to fetch from your data source)
            price_data = await self._fetch_price_data(symbol, lookback_days)
            
            if price_data.empty:
                raise ValueError(f"No price data available for {symbol}")
            
            # Detect patterns
            patterns = await self.pattern_engine.detect_patterns(price_data, kingfisher_data)
            
            # Generate technical indicators
            technical_features = self._calculate_technical_indicators(price_data)
            
            # Analyze market conditions
            market_conditions = self._analyze_market_conditions(price_data)
            
            # Run simulations for long and short positions
            long_analysis = await self._simulate_positions(
                price_data, patterns, 'long', kingfisher_data, cryptometer_data, riskmetric_data
            )
            
            short_analysis = await self._simulate_positions(
                price_data, patterns, 'short', kingfisher_data, cryptometer_data, riskmetric_data
            )
            
            # Calculate comprehensive metrics
            overall_metrics = self._calculate_overall_metrics(long_analysis, short_analysis)
            
            # Generate professional report data
            report_data = self._generate_report_data(
                symbol, patterns, long_analysis, short_analysis, overall_metrics,
                kingfisher_data, cryptometer_data, riskmetric_data
            )
            
            result = SimulationResult(
                symbol=symbol,
                analysis_period_days=lookback_days,
                patterns_detected=patterns,
                long_position_analysis=long_analysis,
                short_position_analysis=short_analysis,
                overall_metrics=overall_metrics,
                market_conditions=market_conditions,
                technical_indicators=technical_features,
                report_data=report_data,
                timestamp=datetime.now()
            )
            
            logger.info(f"Analysis completed for {symbol}: {len(patterns)} patterns detected")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            raise
    
    async def _fetch_price_data(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        """Fetch historical price data for the symbol"""
        
        # This is a placeholder - implement actual data fetching
        # You would integrate with your existing data sources here
        
        # For now, generate sample data for demonstration
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Generate sample OHLCV data
        dates = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        # Simulate realistic price movement
        np.random.seed(42)
        base_price = 50000  # Starting price
        price_changes = np.random.normal(0, 0.02, len(dates))  # 2% volatility
        
        prices = [base_price]
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1000))  # Minimum price floor
        
        # Create OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            volatility = np.random.uniform(0.005, 0.02)
            high = price * (1 + volatility)
            low = price * (1 - volatility)
            volume = np.random.uniform(1000000, 10000000)
            
            data.append({
                'timestamp': date,
                'open': prices[i-1] if i > 0 else price,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive technical indicators"""
        
        indicators = {}
        
        try:
            # Trend indicators
            indicators['sma_20'] = ta.trend.sma_indicator(data['close'], window=20).iloc[-1]
            indicators['sma_50'] = ta.trend.sma_indicator(data['close'], window=50).iloc[-1]
            indicators['ema_12'] = ta.trend.ema_indicator(data['close'], window=12).iloc[-1]
            indicators['ema_26'] = ta.trend.ema_indicator(data['close'], window=26).iloc[-1]
            
            # Momentum indicators
            indicators['rsi'] = ta.momentum.rsi(data['close'], window=14).iloc[-1]
            indicators['stoch_k'] = ta.momentum.stoch(data['high'], data['low'], data['close']).iloc[-1]
            indicators['williams_r'] = ta.momentum.williams_r(data['high'], data['low'], data['close']).iloc[-1]
            
            # MACD
            macd_line = ta.trend.macd(data['close'])
            macd_signal = ta.trend.macd_signal(data['close'])
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal'] = macd_signal.iloc[-1]
            indicators['macd_histogram'] = (macd_line - macd_signal).iloc[-1]
            
            # Volatility indicators
            indicators['atr'] = ta.volatility.average_true_range(data['high'], data['low'], data['close']).iloc[-1]
            bb_high = ta.volatility.bollinger_hband(data['close'])
            bb_low = ta.volatility.bollinger_lband(data['close'])
            indicators['bb_upper'] = bb_high.iloc[-1]
            indicators['bb_lower'] = bb_low.iloc[-1]
            indicators['bb_width'] = (bb_high - bb_low).iloc[-1] / data['close'].iloc[-1]
            
            # Volume indicators
            if 'volume' in data.columns:
                indicators['obv'] = ta.volume.on_balance_volume(data['close'], data['volume']).iloc[-1]
                indicators['mfi'] = ta.volume.money_flow_index(
                    data['high'], data['low'], data['close'], data['volume']
                ).iloc[-1]
            
            # Custom indicators based on current price position
            current_price = data['close'].iloc[-1]
            indicators['price_vs_sma20'] = (current_price - indicators['sma_20']) / indicators['sma_20']
            indicators['price_vs_sma50'] = (current_price - indicators['sma_50']) / indicators['sma_50']
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
        
        return indicators
    
    def _analyze_market_conditions(self, data: pd.DataFrame) -> List[MarketCondition]:
        """Analyze different market conditions in the data"""
        
        conditions = []
        
        # Calculate rolling volatility
        returns = data['close'].pct_change()
        volatility = returns.rolling(24).std() * np.sqrt(24)  # 24-hour rolling volatility
        
        # Calculate trend strength
        sma_20 = ta.trend.sma_indicator(data['close'], window=20)
        sma_50 = ta.trend.sma_indicator(data['close'], window=50)
        
        # Identify different market regimes
        for i in range(50, len(data) - 24, 24):  # Daily analysis
            start_time = data.index[i]
            end_time = data.index[i + 24]
            
            period_data = data.iloc[i:i+24]
            period_volatility = volatility.iloc[i:i+24].mean()
            
            # Determine condition type
            if sma_20.iloc[i+24] > sma_50.iloc[i+24] * 1.02:
                condition_type = "trending_up"
            elif sma_20.iloc[i+24] < sma_50.iloc[i+24] * 0.98:
                condition_type = "trending_down"
            elif period_volatility > volatility.quantile(0.8):
                condition_type = "high_volatility"
            elif period_volatility < volatility.quantile(0.2):
                condition_type = "low_volatility"
            else:
                condition_type = "ranging"
            
            # Calculate volume profile
            if 'volume' in data.columns:
                avg_volume = period_data['volume'].mean()
                overall_avg = data['volume'].mean()
                volume_profile = "high" if avg_volume > overall_avg * 1.2 else "normal"
            else:
                volume_profile = "unknown"
            
            condition = MarketCondition(
                condition_type=condition_type,
                start_time=start_time,
                end_time=end_time,
                volatility=period_volatility,
                volume_profile=volume_profile,
                confidence=0.7  # Base confidence
            )
            
            conditions.append(condition)
        
        return conditions
    
    async def _simulate_positions(
        self,
        price_data: pd.DataFrame,
        patterns: List[PatternMatch],
        direction: str,
        kingfisher_data: Dict = None,
        cryptometer_data: Dict = None,
        riskmetric_data: Dict = None
    ) -> WinRatioAnalysis:
        """Simulate trading positions based on detected patterns"""
        
        trades = []
        
        # Filter patterns by direction
        relevant_patterns = [p for p in patterns if p.direction == direction or p.direction == 'neutral']
        
        for pattern in relevant_patterns:
            # Generate trading signals based on pattern
            signals = self._generate_signals_from_pattern(pattern, price_data, direction)
            
            for signal in signals:
                # Simulate trade execution
                trade = await self._simulate_trade(signal, price_data)
                if trade:
                    trades.append(trade)
        
        # Calculate win ratio analysis
        if not trades:
            return WinRatioAnalysis(
                direction=direction,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_ratio=0.0,
                profit_factor=0.0,
                average_win=Decimal('0'),
                average_loss=Decimal('0'),
                max_consecutive_wins=0,
                max_consecutive_losses=0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                max_drawdown=Decimal('0'),
                confidence_interval=(0.0, 0.0),
                trades=trades
            )
        
        winning_trades = [t for t in trades if t.is_winner()]
        losing_trades = [t for t in trades if not t.is_winner()]
        
        total_pnl = sum([t.pnl for t in trades if t.pnl])
        total_wins = sum([t.pnl for t in winning_trades if t.pnl])
        total_losses = sum([abs(t.pnl) for t in losing_trades if t.pnl])
        
        win_ratio = len(winning_trades) / len(trades) if trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate Sharpe ratio
        returns = [float(t.pnl_percentage) for t in trades if t.pnl_percentage]
        if returns:
            sharpe_ratio = (np.mean(returns) - 2) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate Sortino ratio (downside deviation)
        negative_returns = [r for r in returns if r < 0]
        if negative_returns:
            downside_deviation = np.std(negative_returns)
            sortino_ratio = (np.mean(returns) - 2) / downside_deviation if downside_deviation > 0 else 0
        else:
            sortino_ratio = sharpe_ratio
        
        # Calculate maximum drawdown
        cumulative_pnl = []
        running_total = Decimal('0')
        for trade in trades:
            if trade.pnl:
                running_total += trade.pnl
                cumulative_pnl.append(running_total)
        
        max_drawdown = Decimal('0')
        if cumulative_pnl:
            peak = cumulative_pnl[0]
            for value in cumulative_pnl:
                if value > peak:
                    peak = value
                drawdown = peak - value
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        
        # Calculate consecutive wins/losses
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.is_winner():
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
        
        # Calculate confidence interval for win ratio
        if len(trades) > 10:
            # Wilson score interval
            n = len(trades)
            p = win_ratio
            z = 1.96  # 95% confidence
            
            denominator = 1 + z**2/n
            centre_adjusted_probability = p + z**2/(2*n)
            adjusted_standard_deviation = np.sqrt((p*(1-p) + z**2/(4*n))/n)
            
            lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
            upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
            
            confidence_interval = (max(0, lower_bound), min(1, upper_bound))
        else:
            confidence_interval = (0.0, 1.0)
        
        return WinRatioAnalysis(
            direction=direction,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_ratio=win_ratio,
            profit_factor=profit_factor,
            average_win=Decimal(str(total_wins / len(winning_trades))) if winning_trades else Decimal('0'),
            average_loss=Decimal(str(total_losses / len(losing_trades))) if losing_trades else Decimal('0'),
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            confidence_interval=confidence_interval,
            trades=trades
        )
    
    def _generate_signals_from_pattern(
        self,
        pattern: PatternMatch,
        price_data: pd.DataFrame,
        direction: str
    ) -> List[TradingSignal]:
        """Generate trading signals based on detected patterns"""
        
        signals = []
        
        # Find the pattern timestamp in price data
        pattern_idx = None
        for i, timestamp in enumerate(price_data.index):
            if timestamp >= pattern.timestamp:
                pattern_idx = i
                break
        
        if pattern_idx is None or pattern_idx >= len(price_data) - 1:
            return signals
        
        # Generate signal based on pattern
        entry_price = price_data['close'].iloc[pattern_idx]
        
        # Create market condition context
        market_condition = MarketCondition(
            condition_type="pattern_based",
            start_time=pattern.timestamp,
            end_time=pattern.timestamp + timedelta(hours=24),
            volatility=0.02,  # Default volatility
            volume_profile="normal"
        )
        
        signal = TradingSignal(
            timestamp=pattern.timestamp,
            symbol="BTCUSDT",  # This would be dynamic
            direction=direction,
            entry_price=Decimal(str(entry_price)),
            confidence=pattern.confidence,
            signal_source="pattern_recognition",
            market_condition=market_condition,
            technical_indicators={
                'pattern_type': pattern.pattern_type,
                'pattern_confidence': pattern.confidence,
                'target_price': float(pattern.target_price),
                'stop_loss': float(pattern.stop_loss)
            }
        )
        
        signals.append(signal)
        
        return signals
    
    async def _simulate_trade(self, signal: TradingSignal, price_data: pd.DataFrame) -> Optional[SimulationTrade]:
        """Simulate a complete trade lifecycle"""
        
        # Find entry point in price data
        entry_idx = None
        for i, timestamp in enumerate(price_data.index):
            if timestamp >= signal.timestamp:
                entry_idx = i
                break
        
        if entry_idx is None or entry_idx >= len(price_data) - 10:
            return None
        
        # Create trade
        trade = SimulationTrade(
            trade_id=f"{signal.symbol}_{signal.timestamp.strftime('%Y%m%d_%H%M%S')}",
            symbol=signal.symbol,
            direction=signal.direction,
            entry_time=signal.timestamp,
            entry_price=signal.entry_price,
            position_size=Decimal('1000'),  # $1000 position size
            leverage=1  # No leverage for simulation
        )
        
        # Simulate trade execution
        target_price = Decimal(str(signal.technical_indicators.get('target_price', 0)))
        stop_loss = Decimal(str(signal.technical_indicators.get('stop_loss', 0)))
        
        # Look for exit conditions in subsequent price data
        max_hold_periods = min(48, len(price_data) - entry_idx - 1)  # Max 48 periods or until data ends
        
        for i in range(1, max_hold_periods + 1):
            current_idx = entry_idx + i
            current_price = Decimal(str(price_data['close'].iloc[current_idx]))
            current_time = price_data.index[current_idx]
            
            # Check for target hit
            if signal.direction == "long":
                if current_price >= target_price:
                    trade.exit_time = current_time
                    trade.exit_price = target_price
                    trade.exit_reason = "target_hit"
                    break
                elif current_price <= stop_loss:
                    trade.exit_time = current_time
                    trade.exit_price = stop_loss
                    trade.exit_reason = "stop_loss"
                    break
            else:  # short
                if current_price <= target_price:
                    trade.exit_time = current_time
                    trade.exit_price = target_price
                    trade.exit_reason = "target_hit"
                    break
                elif current_price >= stop_loss:
                    trade.exit_time = current_time
                    trade.exit_price = stop_loss
                    trade.exit_reason = "stop_loss"
                    break
        
        # If no exit condition met, close at end of period
        if trade.exit_time is None:
            trade.exit_time = price_data.index[entry_idx + max_hold_periods]
            trade.exit_price = Decimal(str(price_data['close'].iloc[entry_idx + max_hold_periods]))
            trade.exit_reason = "time_exit"
        
        # Calculate trade metrics
        trade.calculate_metrics(price_data)
        
        return trade
    
    def _calculate_overall_metrics(
        self,
        long_analysis: WinRatioAnalysis,
        short_analysis: WinRatioAnalysis
    ) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        
        total_trades = long_analysis.total_trades + short_analysis.total_trades
        total_winning = long_analysis.winning_trades + short_analysis.winning_trades
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'overall_win_ratio': 0.0,
                'best_direction': 'none',
                'recommendation': 'insufficient_data'
            }
        
        overall_win_ratio = total_winning / total_trades
        
        # Determine best direction
        if long_analysis.win_ratio > short_analysis.win_ratio:
            best_direction = 'long'
            direction_confidence = long_analysis.win_ratio - short_analysis.win_ratio
        elif short_analysis.win_ratio > long_analysis.win_ratio:
            best_direction = 'short'
            direction_confidence = short_analysis.win_ratio - long_analysis.win_ratio
        else:
            best_direction = 'neutral'
            direction_confidence = 0.0
        
        # Generate recommendation
        if overall_win_ratio > 0.6 and total_trades > 20:
            recommendation = 'favorable'
        elif overall_win_ratio > 0.5 and total_trades > 10:
            recommendation = 'moderate'
        elif total_trades < 10:
            recommendation = 'insufficient_data'
        else:
            recommendation = 'unfavorable'
        
        return {
            'total_trades': total_trades,
            'overall_win_ratio': overall_win_ratio,
            'best_direction': best_direction,
            'direction_confidence': direction_confidence,
            'recommendation': recommendation,
            'long_profit_factor': long_analysis.profit_factor,
            'short_profit_factor': short_analysis.profit_factor,
            'combined_sharpe': (long_analysis.sharpe_ratio + short_analysis.sharpe_ratio) / 2
        }
    
    def _generate_report_data(
        self,
        symbol: str,
        patterns: List[PatternMatch],
        long_analysis: WinRatioAnalysis,
        short_analysis: WinRatioAnalysis,
        overall_metrics: Dict[str, Any],
        kingfisher_data: Dict = None,
        cryptometer_data: Dict = None,
        riskmetric_data: Dict = None
    ) -> Dict[str, Any]:
        """Generate comprehensive report data for professional presentation"""
        
        # Executive summary
        executive_summary = {
            'symbol': symbol,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_patterns_detected': len(patterns),
            'overall_win_ratio': overall_metrics['overall_win_ratio'],
            'recommended_direction': overall_metrics['best_direction'],
            'confidence_level': overall_metrics['direction_confidence'],
            'recommendation': overall_metrics['recommendation']
        }
        
        # Pattern analysis summary
        pattern_summary = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in pattern_summary:
                pattern_summary[pattern_type] = {
                    'count': 0,
                    'avg_confidence': 0.0,
                    'directions': {'bullish': 0, 'bearish': 0, 'neutral': 0}
                }
            
            pattern_summary[pattern_type]['count'] += 1
            pattern_summary[pattern_type]['avg_confidence'] += pattern.confidence
            pattern_summary[pattern_type]['directions'][pattern.direction] += 1
        
        # Calculate averages
        for pattern_type in pattern_summary:
            count = pattern_summary[pattern_type]['count']
            pattern_summary[pattern_type]['avg_confidence'] /= count
        
        # Risk assessment
        risk_assessment = {
            'long_max_drawdown': float(long_analysis.max_drawdown),
            'short_max_drawdown': float(short_analysis.max_drawdown),
            'long_max_consecutive_losses': long_analysis.max_consecutive_losses,
            'short_max_consecutive_losses': short_analysis.max_consecutive_losses,
            'volatility_risk': 'medium',  # This would be calculated based on actual data
            'liquidity_risk': 'low'  # This would be assessed based on volume data
        }
        
        # Performance attribution
        performance_attribution = {
            'pattern_contribution': {},
            'market_condition_contribution': {},
            'timeframe_contribution': {}
        }
        
        # Data source contributions
        data_source_analysis = {
            'kingfisher_patterns': len([p for p in patterns if 'liquidation' in p.pattern_type]),
            'technical_patterns': len([p for p in patterns if 'liquidation' not in p.pattern_type]),
            'cryptometer_score': cryptometer_data.get('overall_score', 0) if cryptometer_data else 0,
            'riskmetric_score': riskmetric_data.get('total_score', 0) if riskmetric_data else 0
        }
        
        return {
            'executive_summary': executive_summary,
            'pattern_summary': pattern_summary,
            'risk_assessment': risk_assessment,
            'performance_attribution': performance_attribution,
            'data_source_analysis': data_source_analysis,
            'detailed_metrics': {
                'long_analysis': long_analysis.__dict__,
                'short_analysis': short_analysis.__dict__,
                'overall_metrics': overall_metrics
            }
        }

# Export the main simulation engine
simulation_engine = SimulationEngine()

if __name__ == "__main__":
    # Test the simulation engine
    async def test_simulation():
        result = await simulation_engine.analyze_symbol("BTCUSDT", lookback_days=30)
        print(f"Analysis completed: {result.symbol}")
        print(f"Patterns detected: {len(result.patterns_detected)}")
        print(f"Long win ratio: {result.long_position_analysis.win_ratio:.2%}")
        print(f"Short win ratio: {result.short_position_analysis.win_ratio:.2%}")
    
    # Run test
    asyncio.run(test_simulation())

