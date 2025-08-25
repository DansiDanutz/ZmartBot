#!/usr/bin/env python3
"""
Populate Support/Resistance Levels Data
Calculates and stores Support/Resistance Levels analysis for all symbols in My Symbols list
"""

import sqlite3
import requests
import os
import sys
import numpy as np
from datetime import datetime

# Add the src directory to the path to import the technical analysis service
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from services.technical_analysis_service import TechnicalAnalysisService

def get_active_symbols():
    """Get all active symbols from the portfolio"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.id, s.symbol 
            FROM symbols s
            JOIN portfolio_composition pc ON s.id = pc.symbol_id
            WHERE pc.status = 'Active'
            ORDER BY s.symbol
        """)
        
        symbols = cursor.fetchall()
        conn.close()
        return symbols
        
    except Exception as e:
        print(f"❌ Error getting active symbols: {e}")
        return []

def find_swing_points(highs, lows, window=5):
    """Find swing highs and lows"""
    if len(highs) < window * 2 + 1:
        return [], []
    
    swing_highs = []
    swing_lows = []
    
    for i in range(window, len(highs) - window):
        # Check if current high is a swing high
        if all(highs[i] >= highs[j] for j in range(i - window, i + window + 1)):
            swing_highs.append((i, highs[i]))
        
        # Check if current low is a swing low
        if all(lows[i] <= lows[j] for j in range(i - window, i + window + 1)):
            swing_lows.append((i, lows[i]))
    
    return swing_highs, swing_lows

def find_pivot_points(highs, lows, closes, window=5):
    """Find pivot points (support and resistance levels)"""
    if len(highs) < window * 2 + 1:
        return [], []
    
    pivot_highs = []
    pivot_lows = []
    
    for i in range(window, len(highs) - window):
        # Pivot high (resistance)
        if (all(highs[i] >= highs[j] for j in range(i - window, i)) and 
            all(highs[i] >= highs[j] for j in range(i + 1, i + window + 1))):
            pivot_highs.append(highs[i])
        
        # Pivot low (support)
        if (all(lows[i] <= lows[j] for j in range(i - window, i)) and 
            all(lows[i] <= lows[j] for j in range(i + 1, i + window + 1))):
            pivot_lows.append(lows[i])
    
    return pivot_highs, pivot_lows

def find_psychological_levels(current_price):
    """Find psychological support and resistance levels"""
    # Round to nearest psychological level
    if current_price >= 1000:
        # For high-priced assets, round to nearest 100, 500, 1000
        base = 1000
        levels = []
        for i in range(-5, 6):
            level = current_price + (i * base)
            if level > 0:
                levels.append(level)
    elif current_price >= 100:
        # For medium-priced assets, round to nearest 10, 50, 100
        base = 10
        levels = []
        for i in range(-10, 11):
            level = current_price + (i * base)
            if level > 0:
                levels.append(level)
    else:
        # For low-priced assets, round to nearest 0.1, 0.5, 1.0
        base = 0.1
        levels = []
        for i in range(-10, 11):
            level = current_price + (i * base)
            if level > 0:
                levels.append(level)
    
    return levels

def calculate_support_levels(lows, pivot_lows, current_price, psychological_levels):
    """Calculate support levels"""
    support_levels = []
    
    # Add recent lows
    if len(lows) >= 20:
        recent_lows = sorted(lows[-20:])
        support_levels.extend(recent_lows[-3:])  # Take 3 highest recent lows
    
    # Add pivot lows
    if pivot_lows:
        pivot_lows_sorted = sorted(pivot_lows)
        support_levels.extend(pivot_lows_sorted[-3:])  # Take 3 highest pivot lows
    
    # Add psychological levels below current price
    below_price = [level for level in psychological_levels if level < current_price]
    if below_price:
        below_price_sorted = sorted(below_price, reverse=True)
        support_levels.extend(below_price_sorted[:3])  # Take 3 closest below current price
    
    # Remove duplicates and sort
    support_levels = sorted(list(set(support_levels)), reverse=True)
    
    # Take top 3 support levels
    return support_levels[:3] if len(support_levels) >= 3 else support_levels + [current_price * 0.95] * (3 - len(support_levels))

def calculate_resistance_levels(highs, pivot_highs, current_price, psychological_levels):
    """Calculate resistance levels"""
    resistance_levels = []
    
    # Add recent highs
    if len(highs) >= 20:
        recent_highs = sorted(highs[-20:])
        resistance_levels.extend(recent_highs[-3:])  # Take 3 highest recent highs
    
    # Add pivot highs
    if pivot_highs:
        pivot_highs_sorted = sorted(pivot_highs)
        resistance_levels.extend(pivot_highs_sorted[-3:])  # Take 3 highest pivot highs
    
    # Add psychological levels above current price
    above_price = [level for level in psychological_levels if level > current_price]
    if above_price:
        above_price_sorted = sorted(above_price)
        resistance_levels.extend(above_price_sorted[:3])  # Take 3 closest above current price
    
    # Remove duplicates and sort
    resistance_levels = sorted(list(set(resistance_levels)))
    
    # Take top 3 resistance levels
    return resistance_levels[:3] if len(resistance_levels) >= 3 else resistance_levels + [current_price * 1.05] * (3 - len(resistance_levels))

def determine_price_position(current_price, support_levels, resistance_levels):
    """Determine price position relative to support and resistance"""
    if not support_levels or not resistance_levels:
        return "neutral"
    
    nearest_support = max([s for s in support_levels if s <= current_price], default=0)
    nearest_resistance = min([r for r in resistance_levels if r >= current_price], default=float('inf'))
    
    if nearest_support == 0 and nearest_resistance == float('inf'):
        return "neutral"
    
    if nearest_support == 0:
        # Price below all support levels
        return "below_support"
    elif nearest_resistance == float('inf'):
        # Price above all resistance levels
        return "above_resistance"
    else:
        # Price between support and resistance
        range_size = nearest_resistance - nearest_support
        if range_size == 0:
            return "neutral"
        
        position = (current_price - nearest_support) / range_size
        
        if position < 0.2:
            return "near_support"
        elif position > 0.8:
            return "near_resistance"
        else:
            return "middle_range"

def calculate_support_strength(support_levels, lows, volumes, window=20):
    """Calculate support level strength"""
    if not support_levels:
        return 0.0
    
    # Find the strongest support level
    strongest_support = max(support_levels)
    
    # Count how many times this level has been tested
    test_count = sum(1 for low in lows[-window:] if abs(low - strongest_support) / strongest_support < 0.01)
    
    # Calculate volume confirmation
    if len(volumes) >= window:
        avg_volume = np.mean(volumes[-window:])
        recent_volume = volumes[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
    else:
        volume_ratio = 1.0
    
    # Calculate strength based on test count and volume
    strength = min((test_count * 10) + (volume_ratio * 20), 100.0)
    return strength

def calculate_resistance_strength(resistance_levels, highs, volumes, window=20):
    """Calculate resistance level strength"""
    if not resistance_levels:
        return 0.0
    
    # Find the strongest resistance level
    strongest_resistance = min(resistance_levels)
    
    # Count how many times this level has been tested
    test_count = sum(1 for high in highs[-window:] if abs(high - strongest_resistance) / strongest_resistance < 0.01)
    
    # Calculate volume confirmation
    if len(volumes) >= window:
        avg_volume = np.mean(volumes[-window:])
        recent_volume = volumes[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
    else:
        volume_ratio = 1.0
    
    # Calculate strength based on test count and volume
    strength = min((test_count * 10) + (volume_ratio * 20), 100.0)
    return strength

def determine_breakout_potential(current_price, support_levels, resistance_levels, support_strength, resistance_strength):
    """Determine breakout potential"""
    if not support_levels or not resistance_levels:
        return "none", "neutral", 0.0
    
    nearest_support = max([s for s in support_levels if s <= current_price], default=0)
    nearest_resistance = min([r for r in resistance_levels if r >= current_price], default=float('inf'))
    
    if nearest_support == 0 and nearest_resistance == float('inf'):
        return "none", "neutral", 0.0
    
    # Calculate distances
    support_distance = current_price - nearest_support if nearest_support > 0 else float('inf')
    resistance_distance = nearest_resistance - current_price if nearest_resistance < float('inf') else float('inf')
    
    # Determine which level is closer
    if support_distance < resistance_distance:
        # Closer to support
        if support_distance / current_price < 0.01:  # Within 1%
            if support_strength < 50:  # Weak support
                return "high_bearish", "bearish", 80.0
            else:
                return "moderate_bearish", "bearish", 60.0
        else:
            return "low_bearish", "bearish", 30.0
    else:
        # Closer to resistance
        if resistance_distance / current_price < 0.01:  # Within 1%
            if resistance_strength < 50:  # Weak resistance
                return "high_bullish", "bullish", 80.0
            else:
                return "moderate_bullish", "bullish", 60.0
        else:
            return "low_bullish", "bullish", 30.0

def determine_volume_confirmation(volumes, breakout_direction, periods=5):
    """Determine volume confirmation for breakout"""
    if len(volumes) < periods:
        return "none", 0.0
    
    recent_volumes = volumes[-periods:]
    avg_volume = np.mean(recent_volumes[:-1])  # Exclude current volume
    current_volume = recent_volumes[-1]
    
    if avg_volume == 0:
        return "none", 0.0
    
    volume_ratio = current_volume / avg_volume
    
    # Determine confirmation based on breakout direction and volume
    if breakout_direction == "bullish":
        if volume_ratio > 1.5:
            return "strong_bullish", volume_ratio * 100
        elif volume_ratio > 1.2:
            return "moderate_bullish", volume_ratio * 100
        elif volume_ratio > 1.0:
            return "weak_bullish", volume_ratio * 100
        else:
            return "none", volume_ratio * 100
    elif breakout_direction == "bearish":
        if volume_ratio > 1.5:
            return "strong_bearish", volume_ratio * 100
        elif volume_ratio > 1.2:
            return "moderate_bearish", volume_ratio * 100
        elif volume_ratio > 1.0:
            return "weak_bearish", volume_ratio * 100
        else:
            return "none", volume_ratio * 100
    else:
        return "none", volume_ratio * 100

def determine_trend_alignment(closes, breakout_direction, periods=10):
    """Determine if breakout aligns with overall trend"""
    if len(closes) < periods:
        return "neutral"
    
    # Calculate short-term trend
    short_trend = "up" if closes[-1] > closes[-periods//2] else "down"
    
    # Calculate medium-term trend
    medium_trend = "up" if closes[-1] > closes[-periods] else "down"
    
    # Determine alignment
    if breakout_direction == "bullish":
        if short_trend == "up" and medium_trend == "up":
            return "strong_bullish"
        elif short_trend == "up" or medium_trend == "up":
            return "weak_bullish"
        else:
            return "counter_trend"
    elif breakout_direction == "bearish":
        if short_trend == "down" and medium_trend == "down":
            return "strong_bearish"
        elif short_trend == "down" or medium_trend == "down":
            return "weak_bearish"
        else:
            return "counter_trend"
    else:
        return "neutral"

def calculate_support_resistance_for_symbol(symbol, symbol_id):
    """Calculate Support/Resistance Levels for all timeframes for a symbol"""
    try:
        ta_service = TechnicalAnalysisService()
        timeframes = ["15m", "1h", "4h", "1d"]
        results = {}
        
        # Get current price
        response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        response.raise_for_status()
        ticker_data = response.json()
        current_price = float(ticker_data['lastPrice'])
        
        for tf in timeframes:
            try:
                # Map timeframe to Binance interval
                interval_map = {
                    "15m": "15m",
                    "1h": "1h", 
                    "4h": "4h",
                    "1d": "1d"
                }
                
                # Get appropriate limit for each timeframe
                limit_map = {
                    "15m": 100,
                    "1h": 100,
                    "4h": 100,
                    "1d": 100
                }
                
                klines_response = requests.get(
                    f"https://api.binance.com/api/v3/klines",
                    params={"symbol": symbol, "interval": interval_map[tf], "limit": limit_map[tf]},
                    timeout=10
                )
                klines_response.raise_for_status()
                klines_data = klines_response.json()
                
                # Extract OHLCV data
                highs = [float(kline[2]) for kline in klines_data]
                lows = [float(kline[3]) for kline in klines_data]
                closes = [float(kline[4]) for kline in klines_data]
                volumes = [float(kline[5]) for kline in klines_data]
                
                if len(closes) >= 50:  # Need enough data for analysis
                    # Find swing points and pivot points
                    swing_highs, swing_lows = find_swing_points(highs, lows, 5)
                    pivot_highs, pivot_lows = find_pivot_points(highs, lows, closes, 5)
                    
                    # Find psychological levels
                    psychological_levels = find_psychological_levels(current_price)
                    
                    # Calculate support and resistance levels
                    support_levels = calculate_support_levels(lows, pivot_lows, current_price, psychological_levels)
                    resistance_levels = calculate_resistance_levels(highs, pivot_highs, current_price, psychological_levels)
                    
                    # Ensure we have exactly 3 levels each
                    while len(support_levels) < 3:
                        support_levels.append(current_price * 0.95)
                    while len(resistance_levels) < 3:
                        resistance_levels.append(current_price * 1.05)
                    
                    support_levels = support_levels[:3]
                    resistance_levels = resistance_levels[:3]
                    
                    # Determine price position
                    price_position = determine_price_position(current_price, support_levels, resistance_levels)
                    
                    # Find nearest support and resistance
                    nearest_support = max([s for s in support_levels if s <= current_price], default=support_levels[0])
                    nearest_resistance = min([r for r in resistance_levels if r >= current_price], default=resistance_levels[0])
                    
                    # Calculate distances
                    support_distance = current_price - nearest_support
                    resistance_distance = nearest_resistance - current_price
                    
                    # Calculate strength
                    support_strength = calculate_support_strength(support_levels, lows, volumes)
                    resistance_strength = calculate_resistance_strength(resistance_levels, highs, volumes)
                    
                    # Determine breakout potential
                    breakout_potential, breakout_direction, breakout_strength = determine_breakout_potential(
                        current_price, support_levels, resistance_levels, support_strength, resistance_strength
                    )
                    
                    # Determine volume confirmation
                    volume_confirmation, volume_strength = determine_volume_confirmation(volumes, breakout_direction)
                    
                    # Determine trend alignment
                    trend_alignment = determine_trend_alignment(closes, breakout_direction)
                    
                    results[tf] = {
                        "support_level_1": support_levels[0],
                        "support_level_2": support_levels[1],
                        "support_level_3": support_levels[2],
                        "resistance_level_1": resistance_levels[0],
                        "resistance_level_2": resistance_levels[1],
                        "resistance_level_3": resistance_levels[2],
                        "current_price": current_price,
                        "price_position": price_position,
                        "nearest_support": nearest_support,
                        "nearest_resistance": nearest_resistance,
                        "support_distance": support_distance,
                        "resistance_distance": resistance_distance,
                        "support_strength": support_strength,
                        "resistance_strength": resistance_strength,
                        "breakout_potential": breakout_potential,
                        "breakout_direction": breakout_direction,
                        "breakout_strength": breakout_strength,
                        "volume_confirmation": volume_confirmation,
                        "volume_strength": volume_strength,
                        "trend_alignment": trend_alignment
                    }
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Support/Resistance Levels for {symbol}: {e}")
        return {}

def store_support_resistance_data(symbol_id, symbol, support_resistance_data):
    """Store Support/Resistance Levels data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in support_resistance_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO support_resistance_data 
                (symbol_id, symbol, timeframe, support_level_1, support_level_2, support_level_3,
                resistance_level_1, resistance_level_2, resistance_level_3, current_price,
                price_position, nearest_support, nearest_resistance, support_distance,
                resistance_distance, support_strength, resistance_strength, breakout_potential,
                breakout_direction, breakout_strength, volume_confirmation, volume_strength,
                trend_alignment, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['support_level_1'], data['support_level_2'],
                data['support_level_3'], data['resistance_level_1'], data['resistance_level_2'],
                data['resistance_level_3'], data['current_price'], data['price_position'],
                data['nearest_support'], data['nearest_resistance'], data['support_distance'],
                data['resistance_distance'], data['support_strength'], data['resistance_strength'],
                data['breakout_potential'], data['breakout_direction'], data['breakout_strength'],
                data['volume_confirmation'], data['volume_strength'], data['trend_alignment'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Support/Resistance Levels data for {symbol}: {e}")
        return False

def generate_support_resistance_report():
    """Generate a comprehensive report of all Support/Resistance Levels data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, price_position, nearest_support, nearest_resistance,
                   support_distance, resistance_distance, support_strength, resistance_strength,
                   breakout_potential, breakout_direction, breakout_strength, volume_confirmation,
                   trend_alignment, current_price, last_updated
            FROM support_resistance_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Support/Resistance Levels data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 SUPPORT/RESISTANCE LEVELS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine position emoji
            position_emoji = {
                "near_support": "📈",
                "near_resistance": "📉",
                "middle_range": "➡️",
                "below_support": "💥",
                "above_resistance": "🚀",
                "neutral": "⚪"
            }.get(price_position, "⚪")
            
            # Determine breakout emoji
            breakout_emoji = {
                "high_bullish": "🚀",
                "moderate_bullish": "📈",
                "low_bullish": "📈",
                "high_bearish": "💥",
                "moderate_bearish": "📉",
                "low_bearish": "📉",
                "none": "⚪"
            }.get(breakout_potential, "⚪")
            
            # Determine direction emoji
            direction_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "⚪"
            }.get(breakout_direction, "⚪")
            
            # Determine volume emoji
            volume_emoji = {
                "strong_bullish": "📊",
                "moderate_bullish": "📈",
                "weak_bullish": "📈",
                "strong_bearish": "📊",
                "moderate_bearish": "📉",
                "weak_bearish": "📉",
                "none": "➡️"
            }.get(volume_confirmation, "➡️")
            
            # Determine trend emoji
            trend_emoji = {
                "strong_bullish": "🚀",
                "weak_bullish": "📈",
                "strong_bearish": "💥",
                "weak_bearish": "📉",
                "counter_trend": "🔄",
                "neutral": "➡️"
            }.get(trend_alignment, "➡️")
            
            print(f"  {timeframe:>4} | {position_emoji} {price_position:>15} | {breakout_emoji} {breakout_potential:>15} | {direction_emoji} {breakout_direction:>8} | {volume_emoji} {volume_confirmation:>15} | {trend_emoji} {trend_alignment:>15} | Support: ${nearest_support:>8.2f} | Resistance: ${nearest_resistance:>8.2f} | Strength: {support_strength:>5.1f}%/{resistance_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 SUPPORT/RESISTANCE LEVELS SUMMARY:")
        print("="*80)
        
        # Count by price position
        near_support_count = sum(1 for row in data if row[2] == "near_support")
        near_resistance_count = sum(1 for row in data if row[2] == "near_resistance")
        middle_range_count = sum(1 for row in data if row[2] == "middle_range")
        below_support_count = sum(1 for row in data if row[2] == "below_support")
        above_resistance_count = sum(1 for row in data if row[2] == "above_resistance")
        neutral_count = sum(1 for row in data if row[2] == "neutral")
        
        print(f"   📈 Near Support: {near_support_count}")
        print(f"   📉 Near Resistance: {near_resistance_count}")
        print(f"   ➡️ Middle Range: {middle_range_count}")
        print(f"   💥 Below Support: {below_support_count}")
        print(f"   🚀 Above Resistance: {above_resistance_count}")
        print(f"   ⚪ Neutral: {neutral_count}")
        
        # Count by breakout potential
        high_bullish_count = sum(1 for row in data if row[9] == "high_bullish")
        moderate_bullish_count = sum(1 for row in data if row[9] == "moderate_bullish")
        low_bullish_count = sum(1 for row in data if row[9] == "low_bullish")
        high_bearish_count = sum(1 for row in data if row[9] == "high_bearish")
        moderate_bearish_count = sum(1 for row in data if row[9] == "moderate_bearish")
        low_bearish_count = sum(1 for row in data if row[9] == "low_bearish")
        none_count = sum(1 for row in data if row[9] == "none")
        
        print(f"   🚀 High Bullish: {high_bullish_count}")
        print(f"   📈 Moderate Bullish: {moderate_bullish_count}")
        print(f"   📈 Low Bullish: {low_bullish_count}")
        print(f"   💥 High Bearish: {high_bearish_count}")
        print(f"   📉 Moderate Bearish: {moderate_bearish_count}")
        print(f"   📉 Low Bearish: {low_bearish_count}")
        print(f"   ⚪ None: {none_count}")
        
        # Count by breakout direction
        bullish_direction_count = sum(1 for row in data if row[10] == "bullish")
        bearish_direction_count = sum(1 for row in data if row[10] == "bearish")
        neutral_direction_count = sum(1 for row in data if row[10] == "neutral")
        
        print(f"   🟢 Bullish Direction: {bullish_direction_count}")
        print(f"   🔴 Bearish Direction: {bearish_direction_count}")
        print(f"   ⚪ Neutral Direction: {neutral_direction_count}")
        
        # Count by volume confirmation
        strong_bullish_volume_count = sum(1 for row in data if row[12] == "strong_bullish")
        moderate_bullish_volume_count = sum(1 for row in data if row[12] == "moderate_bullish")
        weak_bullish_volume_count = sum(1 for row in data if row[12] == "weak_bullish")
        strong_bearish_volume_count = sum(1 for row in data if row[12] == "strong_bearish")
        moderate_bearish_volume_count = sum(1 for row in data if row[12] == "moderate_bearish")
        weak_bearish_volume_count = sum(1 for row in data if row[12] == "weak_bearish")
        no_volume_count = sum(1 for row in data if row[12] == "none")
        
        print(f"   📊 Strong Bullish Volume: {strong_bullish_volume_count}")
        print(f"   📈 Moderate Bullish Volume: {moderate_bullish_volume_count}")
        print(f"   📈 Weak Bullish Volume: {weak_bullish_volume_count}")
        print(f"   📊 Strong Bearish Volume: {strong_bearish_volume_count}")
        print(f"   📉 Moderate Bearish Volume: {moderate_bearish_volume_count}")
        print(f"   📉 Weak Bearish Volume: {weak_bearish_volume_count}")
        print(f"   ➡️ No Volume: {no_volume_count}")
        
        # Count by trend alignment
        strong_bullish_trend_count = sum(1 for row in data if row[13] == "strong_bullish")
        weak_bullish_trend_count = sum(1 for row in data if row[13] == "weak_bullish")
        strong_bearish_trend_count = sum(1 for row in data if row[13] == "strong_bearish")
        weak_bearish_trend_count = sum(1 for row in data if row[13] == "weak_bearish")
        counter_trend_count = sum(1 for row in data if row[13] == "counter_trend")
        neutral_trend_count = sum(1 for row in data if row[13] == "neutral")
        
        print(f"   🚀 Strong Bullish Trend: {strong_bullish_trend_count}")
        print(f"   📈 Weak Bullish Trend: {weak_bullish_trend_count}")
        print(f"   💥 Strong Bearish Trend: {strong_bearish_trend_count}")
        print(f"   📉 Weak Bearish Trend: {weak_bearish_trend_count}")
        print(f"   🔄 Counter Trend: {counter_trend_count}")
        print(f"   ➡️ Neutral Trend: {neutral_trend_count}")
        
        # Count strong supports and resistances
        strong_supports = sum(1 for row in data if row[7] > 70)
        moderate_supports = sum(1 for row in data if 40 < row[7] <= 70)
        weak_supports = sum(1 for row in data if row[7] <= 40)
        
        print(f"   💪 Strong Supports (>70%): {strong_supports}")
        print(f"   📊 Moderate Supports (40-70%): {moderate_supports}")
        print(f"   🔸 Weak Supports (<40%): {weak_supports}")
        
        strong_resistances = sum(1 for row in data if row[8] > 70)
        moderate_resistances = sum(1 for row in data if 40 < row[8] <= 70)
        weak_resistances = sum(1 for row in data if row[8] <= 40)
        
        print(f"   💪 Strong Resistances (>70%): {strong_resistances}")
        print(f"   📊 Moderate Resistances (40-70%): {moderate_resistances}")
        print(f"   🔸 Weak Resistances (<40%): {weak_resistances}")
        
        # Count strong breakouts
        strong_breakouts = sum(1 for row in data if row[11] > 70)
        moderate_breakouts = sum(1 for row in data if 40 < row[11] <= 70)
        weak_breakouts = sum(1 for row in data if row[11] <= 40)
        
        print(f"   💪 Strong Breakouts (>70%): {strong_breakouts}")
        print(f"   📊 Moderate Breakouts (40-70%): {moderate_breakouts}")
        print(f"   🔸 Weak Breakouts (<40%): {weak_breakouts}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find high breakout potential
        high_breakout = [row for row in data if "high" in row[9] and row[11] > 50]
        if high_breakout:
            print("   🚀 High Breakout Potential (Strong Signals):")
            for breakout in high_breakout:
                symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_potential} - Direction {breakout_direction}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No high breakout potential detected")
        
        # Find moderate breakout potential
        moderate_breakout = [row for row in data if "moderate" in row[9] and row[11] > 30]
        if moderate_breakout:
            print("   📊 Moderate Breakout Potential (Watch for Confirmation):")
            for breakout in moderate_breakout:
                symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_potential} - Direction {breakout_direction}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No moderate breakout potential detected")
        
        # Find price near support
        near_support = [row for row in data if row[2] == "near_support" and row[7] > 50]
        if near_support:
            print("   📈 Price Near Strong Support (Bounce Potential):")
            for support in near_support:
                symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = support
                print(f"      • {symbol} {timeframe}: Support ${nearest_support:.2f}, Strength {support_strength:.1f}%")
        else:
            print("   ✅ No price near strong support detected")
        
        # Find price near resistance
        near_resistance = [row for row in data if row[2] == "near_resistance" and row[8] > 50]
        if near_resistance:
            print("   📉 Price Near Strong Resistance (Rejection Potential):")
            for resistance in near_resistance:
                symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = resistance
                print(f"      • {symbol} {timeframe}: Resistance ${nearest_resistance:.2f}, Strength {resistance_strength:.1f}%")
        else:
            print("   ✅ No price near strong resistance detected")
        
        # Find strong volume confirmations
        strong_volume = [row for row in data if "strong" in row[12] and row[11] > 30]
        if strong_volume:
            print("   📊 Strong Volume Confirmations:")
            for volume in strong_volume:
                symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = volume
                print(f"      • {symbol} {timeframe}: {volume_confirmation} volume - Breakout {breakout_potential}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No strong volume confirmations detected")
        
        # Find trend alignments
        strong_trend_alignments = [row for row in data if "strong" in row[13] and row[11] > 20]
        if strong_trend_alignments:
            print("   📊 Strong Trend Alignments:")
            for trend in strong_trend_alignments:
                symbol, timeframe, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation, trend_alignment, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: {trend_alignment} alignment - Breakout {breakout_potential}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No strong trend alignments detected")
        
        print("\n" + "="*80)
        print("✅ Support/Resistance Levels report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Support/Resistance Levels report: {e}")

def main():
    """Main function to populate Support/Resistance Levels data"""
    print("🚀 Starting Support/Resistance Levels data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Support/Resistance Levels for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        support_resistance_data = calculate_support_resistance_for_symbol(symbol, symbol_id)
        if support_resistance_data:
            if store_support_resistance_data(symbol_id, symbol, support_resistance_data):
                print(f"✅ Stored {len(support_resistance_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Support/Resistance Levels data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_support_resistance_report()

if __name__ == "__main__":
    main()
