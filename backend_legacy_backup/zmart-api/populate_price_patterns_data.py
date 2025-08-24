#!/usr/bin/env python3
"""
Populate Price Action Patterns Data
Calculates and stores Price Action Patterns analysis for all symbols in My Symbols list
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

def detect_doji(opens, highs, lows, closes, threshold=0.1):
    """Detect Doji patterns"""
    if len(opens) < 1:
        return None, 0.0, 0.0
    
    # Check the most recent candle
    open_price = opens[-1]
    high_price = highs[-1]
    low_price = lows[-1]
    close_price = closes[-1]
    
    # Calculate body size and total range
    body_size = abs(close_price - open_price)
    total_range = high_price - low_price
    
    if total_range == 0:
        return None, 0.0, 0.0
    
    # Calculate body to range ratio
    body_ratio = body_size / total_range
    
    # Doji: body is very small compared to range
    if body_ratio <= threshold:
        # Determine direction based on previous trend
        if len(opens) > 1:
            prev_close = closes[-2]
            if close_price > prev_close:
                direction = "bullish"
            elif close_price < prev_close:
                direction = "bearish"
            else:
                direction = "neutral"
        else:
            direction = "neutral"
        
        # Calculate strength based on how small the body is
        strength = (1 - body_ratio) * 100
        reliability = 70.0  # Doji reliability
        
        return "doji", strength, reliability, direction
    
    return None, 0.0, 0.0

def detect_hammer(opens, highs, lows, closes, threshold=0.3):
    """Detect Hammer patterns"""
    if len(opens) < 1:
        return None, 0.0, 0.0
    
    # Check the most recent candle
    open_price = opens[-1]
    high_price = highs[-1]
    low_price = lows[-1]
    close_price = closes[-1]
    
    # Calculate body and shadow sizes
    body_size = abs(close_price - open_price)
    total_range = high_price - low_price
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    
    if total_range == 0:
        return None, 0.0, 0.0
    
    # Hammer criteria: small body, long lower shadow, small upper shadow
    body_ratio = body_size / total_range
    lower_shadow_ratio = lower_shadow / total_range
    upper_shadow_ratio = upper_shadow / total_range
    
    if (body_ratio <= threshold and 
        lower_shadow_ratio >= 0.6 and 
        upper_shadow_ratio <= 0.1):
        
        # Determine if it's bullish (close near high) or bearish (close near low)
        if close_price > open_price:
            direction = "bullish"
        else:
            direction = "bullish"  # Hammer is typically bullish regardless of body color
        
        # Calculate strength based on shadow ratios
        strength = (lower_shadow_ratio * 100) * (1 - body_ratio)
        reliability = 75.0  # Hammer reliability
        
        return "hammer", strength, reliability, direction
    
    return None, 0.0, 0.0

def detect_shooting_star(opens, highs, lows, closes, threshold=0.3):
    """Detect Shooting Star patterns"""
    if len(opens) < 1:
        return None, 0.0, 0.0
    
    # Check the most recent candle
    open_price = opens[-1]
    high_price = highs[-1]
    low_price = lows[-1]
    close_price = closes[-1]
    
    # Calculate body and shadow sizes
    body_size = abs(close_price - open_price)
    total_range = high_price - low_price
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    
    if total_range == 0:
        return None, 0.0, 0.0
    
    # Shooting Star criteria: small body, long upper shadow, small lower shadow
    body_ratio = body_size / total_range
    upper_shadow_ratio = upper_shadow / total_range
    lower_shadow_ratio = lower_shadow / total_range
    
    if (body_ratio <= threshold and 
        upper_shadow_ratio >= 0.6 and 
        lower_shadow_ratio <= 0.1):
        
        # Shooting Star is typically bearish
        direction = "bearish"
        
        # Calculate strength based on shadow ratios
        strength = (upper_shadow_ratio * 100) * (1 - body_ratio)
        reliability = 70.0  # Shooting Star reliability
        
        return "shooting_star", strength, reliability, direction
    
    return None, 0.0, 0.0

def detect_engulfing(opens, highs, lows, closes):
    """Detect Engulfing patterns"""
    if len(opens) < 2:
        return None, 0.0, 0.0
    
    # Check the last two candles
    prev_open = opens[-2]
    prev_close = closes[-2]
    curr_open = opens[-1]
    curr_close = closes[-1]
    
    # Calculate body sizes
    prev_body_size = abs(prev_close - prev_open)
    curr_body_size = abs(curr_close - curr_open)
    
    # Bullish Engulfing: current green candle completely engulfs previous red candle
    if (curr_close > curr_open and  # Current candle is green
        prev_close < prev_open and  # Previous candle is red
        curr_open < prev_close and  # Current open below previous close
        curr_close > prev_open):    # Current close above previous open
        
        direction = "bullish"
        strength = (curr_body_size / prev_body_size) * 100 if prev_body_size > 0 else 100
        reliability = 80.0  # Bullish Engulfing reliability
        
        return "bullish_engulfing", strength, reliability, direction
    
    # Bearish Engulfing: current red candle completely engulfs previous green candle
    elif (curr_close < curr_open and  # Current candle is red
          prev_close > prev_open and  # Previous candle is green
          curr_open > prev_close and  # Current open above previous close
          curr_close < prev_open):    # Current close below previous open
        
        direction = "bearish"
        strength = (curr_body_size / prev_body_size) * 100 if prev_body_size > 0 else 100
        reliability = 80.0  # Bearish Engulfing reliability
        
        return "bearish_engulfing", strength, reliability, direction
    
    return None, 0.0, 0.0

def detect_morning_star(opens, highs, lows, closes):
    """Detect Morning Star patterns"""
    if len(opens) < 3:
        return None, 0.0, 0.0
    
    # Check the last three candles
    first_open = opens[-3]
    first_close = closes[-3]
    second_open = opens[-2]
    second_close = closes[-2]
    third_open = opens[-1]
    third_close = closes[-1]
    
    # Morning Star criteria:
    # 1. First candle: long red (bearish)
    # 2. Second candle: small body (doji-like)
    # 3. Third candle: long green (bullish)
    first_body = abs(first_close - first_open)
    second_body = abs(second_close - second_open)
    third_body = abs(third_close - third_open)
    
    if (first_close < first_open and  # First candle is red
        second_body < first_body * 0.3 and  # Second candle has small body
        third_close > third_open and  # Third candle is green
        third_body > first_body * 0.5):  # Third candle has substantial body
        
        direction = "bullish"
        strength = (third_body / first_body) * 100
        reliability = 85.0  # Morning Star reliability
        
        return "morning_star", strength, reliability, direction
    
    return None, 0.0, 0.0

def detect_evening_star(opens, highs, lows, closes):
    """Detect Evening Star patterns"""
    if len(opens) < 3:
        return None, 0.0, 0.0
    
    # Check the last three candles
    first_open = opens[-3]
    first_close = closes[-3]
    second_open = opens[-2]
    second_close = closes[-2]
    third_open = opens[-1]
    third_close = closes[-1]
    
    # Evening Star criteria:
    # 1. First candle: long green (bullish)
    # 2. Second candle: small body (doji-like)
    # 3. Third candle: long red (bearish)
    first_body = abs(first_close - first_open)
    second_body = abs(second_close - second_open)
    third_body = abs(third_close - third_open)
    
    if (first_close > first_open and  # First candle is green
        second_body < first_body * 0.3 and  # Second candle has small body
        third_close < third_open and  # Third candle is red
        third_body > first_body * 0.5):  # Third candle has substantial body
        
        direction = "bearish"
        strength = (third_body / first_body) * 100
        reliability = 85.0  # Evening Star reliability
        
        return "evening_star", strength, reliability, direction
    
    return None, 0.0, 0.0

def detect_triangle_pattern(highs, lows, closes, min_periods=5):
    """Detect Triangle patterns (Ascending, Descending, Symmetrical)"""
    if len(highs) < min_periods:
        return None, 0.0, 0.0
    
    # Get recent data
    recent_highs = highs[-min_periods:]
    recent_lows = lows[-min_periods:]
    
    # Calculate trend lines
    high_slope = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
    low_slope = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
    
    # Calculate R-squared for trend line fit
    high_r_squared = np.corrcoef(range(len(recent_highs)), recent_highs)[0, 1] ** 2
    low_r_squared = np.corrcoef(range(len(recent_lows)), recent_lows)[0, 1] ** 2
    
    # Check if trend lines are well-fitted (R-squared > 0.7)
    if high_r_squared < 0.7 or low_r_squared < 0.7:
        return None, 0.0, 0.0
    
    # Determine triangle type
    if high_slope < -0.001 and low_slope > 0.001:
        # Descending highs, ascending lows = Ascending Triangle
        direction = "bullish"
        pattern_name = "ascending_triangle"
        strength = (abs(high_slope) + abs(low_slope)) * 1000
        reliability = 75.0
    elif high_slope < -0.001 and low_slope < -0.001:
        # Both descending = Descending Triangle
        direction = "bearish"
        pattern_name = "descending_triangle"
        strength = (abs(high_slope) + abs(low_slope)) * 1000
        reliability = 75.0
    elif abs(high_slope) < 0.001 and abs(low_slope) < 0.001:
        # Both horizontal = Rectangle
        direction = "neutral"
        pattern_name = "rectangle"
        strength = 50.0
        reliability = 60.0
    else:
        # Symmetrical Triangle
        direction = "neutral"
        pattern_name = "symmetrical_triangle"
        strength = (abs(high_slope) + abs(low_slope)) * 1000
        reliability = 65.0
    
    return pattern_name, strength, reliability, direction

def calculate_pattern_completion(pattern_type, opens, highs, lows, closes):
    """Calculate pattern completion percentage"""
    if pattern_type in ["doji", "hammer", "shooting_star"]:
        # Single candle patterns are complete
        return 100.0
    elif pattern_type in ["bullish_engulfing", "bearish_engulfing"]:
        # Two candle patterns are complete
        return 100.0
    elif pattern_type in ["morning_star", "evening_star"]:
        # Three candle patterns are complete
        return 100.0
    elif "triangle" in pattern_type or pattern_type == "rectangle":
        # Multi-period patterns - calculate based on convergence
        if len(highs) >= 5:
            recent_highs = highs[-5:]
            recent_lows = lows[-5:]
            
            # Calculate if highs and lows are converging
            high_range = max(recent_highs) - min(recent_highs)
            low_range = max(recent_lows) - min(recent_lows)
            total_range = max(recent_highs) - min(recent_lows)
            
            if total_range > 0:
                convergence = ((high_range + low_range) / total_range) * 100
                return min(convergence, 100.0)
    
    return 0.0

def calculate_breakout_levels(pattern_type, opens, highs, lows, closes, current_price):
    """Calculate breakout, stop loss, and take profit levels"""
    breakout_level = None
    stop_loss_level = None
    take_profit_level = None
    
    if pattern_type == "doji":
        # Doji breakout levels
        if len(highs) > 0:
            breakout_level = highs[-1]  # High of doji
            stop_loss_level = lows[-1]  # Low of doji
            take_profit_level = breakout_level + (breakout_level - stop_loss_level)
    
    elif pattern_type == "hammer":
        # Hammer breakout levels
        if len(highs) > 0:
            breakout_level = highs[-1]  # High of hammer
            stop_loss_level = lows[-1]  # Low of hammer
            take_profit_level = breakout_level + (breakout_level - stop_loss_level)
    
    elif pattern_type == "shooting_star":
        # Shooting Star breakout levels
        if len(lows) > 0:
            breakout_level = lows[-1]  # Low of shooting star
            stop_loss_level = highs[-1]  # High of shooting star
            take_profit_level = breakout_level - (stop_loss_level - breakout_level)
    
    elif pattern_type in ["bullish_engulfing", "morning_star"]:
        # Bullish pattern breakout levels
        if len(highs) > 0:
            breakout_level = max(highs[-2:])  # High of pattern
            stop_loss_level = min(lows[-2:])  # Low of pattern
            take_profit_level = breakout_level + (breakout_level - stop_loss_level)
    
    elif pattern_type in ["bearish_engulfing", "evening_star"]:
        # Bearish pattern breakout levels
        if len(lows) > 0:
            breakout_level = min(lows[-2:])  # Low of pattern
            stop_loss_level = max(highs[-2:])  # High of pattern
            take_profit_level = breakout_level - (stop_loss_level - breakout_level)
    
    elif "triangle" in pattern_type or pattern_type == "rectangle":
        # Triangle/Rectangle breakout levels
        if len(highs) >= 5:
            recent_highs = highs[-5:]
            recent_lows = lows[-5:]
            
            if pattern_type in ["ascending_triangle", "rectangle"]:
                breakout_level = max(recent_highs)  # Resistance level
                stop_loss_level = min(recent_lows)  # Support level
                take_profit_level = breakout_level + (breakout_level - stop_loss_level)
            elif pattern_type == "descending_triangle":
                breakout_level = min(recent_lows)  # Support level
                stop_loss_level = max(recent_highs)  # Resistance level
                take_profit_level = breakout_level - (stop_loss_level - breakout_level)
            else:  # symmetrical_triangle
                # Use current price as reference
                breakout_level = current_price * 1.02  # 2% above current
                stop_loss_level = current_price * 0.98  # 2% below current
                take_profit_level = current_price * 1.06  # 6% above current
    
    return breakout_level, stop_loss_level, take_profit_level

def calculate_risk_reward_ratio(current_price, stop_loss, take_profit):
    """Calculate risk-reward ratio"""
    if stop_loss is None or take_profit is None:
        return 0.0
    
    risk = abs(current_price - stop_loss)
    reward = abs(take_profit - current_price)
    
    if risk == 0:
        return 0.0
    
    return reward / risk

def determine_volume_confirmation(volumes, pattern_type):
    """Determine volume confirmation for pattern"""
    if len(volumes) < 2:
        return "none", 0.0
    
    # Get recent volume data
    if pattern_type in ["doji", "hammer", "shooting_star"]:
        recent_volumes = volumes[-1:]
    elif pattern_type in ["bullish_engulfing", "bearish_engulfing"]:
        recent_volumes = volumes[-2:]
    elif pattern_type in ["morning_star", "evening_star"]:
        recent_volumes = volumes[-3:]
    else:
        recent_volumes = volumes[-5:]
    
    if len(recent_volumes) == 0:
        return "none", 0.0
    
    # Calculate average volume
    avg_volume = np.mean(recent_volumes)
    
    # Check if current volume is above average
    current_volume = recent_volumes[-1]
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    if volume_ratio > 1.5:
        return "strong", volume_ratio * 100
    elif volume_ratio > 1.2:
        return "moderate", volume_ratio * 100
    elif volume_ratio > 1.0:
        return "weak", volume_ratio * 100
    else:
        return "none", volume_ratio * 100

def determine_trend_alignment(opens, highs, lows, closes, pattern_direction):
    """Determine if pattern aligns with overall trend"""
    if len(closes) < 10:
        return "neutral"
    
    # Calculate short-term trend (last 5 candles)
    short_trend = "up" if closes[-1] > closes[-5] else "down"
    
    # Calculate medium-term trend (last 10 candles)
    medium_trend = "up" if closes[-1] > closes[-10] else "down"
    
    # Determine alignment
    if pattern_direction == "bullish":
        if short_trend == "up" and medium_trend == "up":
            return "strong_bullish"
        elif short_trend == "up" or medium_trend == "up":
            return "weak_bullish"
        else:
            return "counter_trend"
    elif pattern_direction == "bearish":
        if short_trend == "down" and medium_trend == "down":
            return "strong_bearish"
        elif short_trend == "down" or medium_trend == "down":
            return "weak_bearish"
        else:
            return "counter_trend"
    else:
        return "neutral"

def calculate_price_patterns_for_symbol(symbol, symbol_id):
    """Calculate Price Action Patterns for all timeframes for a symbol"""
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
                opens = [float(kline[1]) for kline in klines_data]
                highs = [float(kline[2]) for kline in klines_data]
                lows = [float(kline[3]) for kline in klines_data]
                closes = [float(kline[4]) for kline in klines_data]
                volumes = [float(kline[5]) for kline in klines_data]
                
                if len(closes) >= 10:  # Need enough data for pattern analysis
                    # Detect various patterns
                    patterns = []
                    
                    # Single candle patterns
                    doji_result = detect_doji(opens, highs, lows, closes)
                    if doji_result[0]:
                        patterns.append(doji_result)
                    
                    hammer_result = detect_hammer(opens, highs, lows, closes)
                    if hammer_result[0]:
                        patterns.append(hammer_result)
                    
                    shooting_star_result = detect_shooting_star(opens, highs, lows, closes)
                    if shooting_star_result[0]:
                        patterns.append(shooting_star_result)
                    
                    # Multi-candle patterns
                    engulfing_result = detect_engulfing(opens, highs, lows, closes)
                    if engulfing_result[0]:
                        patterns.append(engulfing_result)
                    
                    morning_star_result = detect_morning_star(opens, highs, lows, closes)
                    if morning_star_result[0]:
                        patterns.append(morning_star_result)
                    
                    evening_star_result = detect_evening_star(opens, highs, lows, closes)
                    if evening_star_result[0]:
                        patterns.append(evening_star_result)
                    
                    # Multi-period patterns
                    triangle_result = detect_triangle_pattern(highs, lows, closes)
                    if triangle_result[0]:
                        patterns.append(triangle_result)
                    
                    # Select the strongest pattern
                    if patterns:
                        # Sort by strength and reliability
                        patterns.sort(key=lambda x: (x[1] * x[2]), reverse=True)
                        pattern_type, pattern_strength, pattern_reliability, pattern_direction = patterns[0]
                        
                        # Calculate additional metrics
                        pattern_completion = calculate_pattern_completion(pattern_type, opens, highs, lows, closes)
                        breakout_level, stop_loss_level, take_profit_level = calculate_breakout_levels(
                            pattern_type, opens, highs, lows, closes, current_price
                        )
                        risk_reward_ratio = calculate_risk_reward_ratio(current_price, stop_loss_level, take_profit_level)
                        volume_confirmation, volume_strength = determine_volume_confirmation(volumes, pattern_type)
                        trend_alignment = determine_trend_alignment(opens, highs, lows, closes, pattern_direction)
                        
                        # Support/Resistance levels
                        support_resistance_levels = f"Support: {min(lows[-5:]):.4f}, Resistance: {max(highs[-5:]):.4f}"
                        
                        # Pattern duration
                        if pattern_type in ["doji", "hammer", "shooting_star"]:
                            pattern_duration = 1
                        elif pattern_type in ["bullish_engulfing", "bearish_engulfing"]:
                            pattern_duration = 2
                        elif pattern_type in ["morning_star", "evening_star"]:
                            pattern_duration = 3
                        else:
                            pattern_duration = 5
                        
                        results[tf] = {
                            "pattern_type": pattern_type,
                            "pattern_name": pattern_type.replace("_", " ").title(),
                            "pattern_strength": pattern_strength,
                            "pattern_reliability": pattern_reliability,
                            "pattern_direction": pattern_direction,
                            "pattern_completion": pattern_completion,
                            "breakout_level": breakout_level,
                            "stop_loss_level": stop_loss_level,
                            "take_profit_level": take_profit_level,
                            "risk_reward_ratio": risk_reward_ratio,
                            "volume_confirmation": volume_confirmation,
                            "volume_strength": volume_strength,
                            "trend_alignment": trend_alignment,
                            "support_resistance_levels": support_resistance_levels,
                            "pattern_duration": pattern_duration,
                            "current_price": current_price
                        }
                    else:
                        # No patterns detected
                        results[tf] = {
                            "pattern_type": "none",
                            "pattern_name": "No Pattern",
                            "pattern_strength": 0.0,
                            "pattern_reliability": 0.0,
                            "pattern_direction": "neutral",
                            "pattern_completion": 0.0,
                            "breakout_level": None,
                            "stop_loss_level": None,
                            "take_profit_level": None,
                            "risk_reward_ratio": 0.0,
                            "volume_confirmation": "none",
                            "volume_strength": 0.0,
                            "trend_alignment": "neutral",
                            "support_resistance_levels": "No levels",
                            "pattern_duration": 0,
                            "current_price": current_price
                        }
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Price Action Patterns for {symbol}: {e}")
        return {}

def store_price_patterns_data(symbol_id, symbol, price_patterns_data):
    """Store Price Action Patterns data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in price_patterns_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO price_patterns_data 
                (symbol_id, symbol, timeframe, pattern_type, pattern_name, pattern_strength,
                pattern_reliability, pattern_direction, pattern_completion, breakout_level,
                stop_loss_level, take_profit_level, risk_reward_ratio, volume_confirmation,
                volume_strength, trend_alignment, support_resistance_levels, pattern_duration,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['pattern_type'], data['pattern_name'],
                data['pattern_strength'], data['pattern_reliability'], data['pattern_direction'],
                data['pattern_completion'], data['breakout_level'], data['stop_loss_level'],
                data['take_profit_level'], data['risk_reward_ratio'], data['volume_confirmation'],
                data['volume_strength'], data['trend_alignment'], data['support_resistance_levels'],
                data['pattern_duration'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Price Action Patterns data for {symbol}: {e}")
        return False

def generate_price_patterns_report():
    """Generate a comprehensive report of all Price Action Patterns data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, pattern_type, pattern_name, pattern_strength,
                   pattern_reliability, pattern_direction, pattern_completion,
                   volume_confirmation, volume_strength, trend_alignment,
                   risk_reward_ratio, current_price, last_updated
            FROM price_patterns_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Price Action Patterns data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 PRICE ACTION PATTERNS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine pattern emoji
            pattern_emoji = {
                "doji": "⚪",
                "hammer": "🔨",
                "shooting_star": "⭐",
                "bullish_engulfing": "🟢",
                "bearish_engulfing": "🔴",
                "morning_star": "🌅",
                "evening_star": "🌆",
                "ascending_triangle": "📈",
                "descending_triangle": "📉",
                "symmetrical_triangle": "⚖️",
                "rectangle": "📦",
                "none": "⚪"
            }.get(pattern_type, "⚪")
            
            # Determine direction emoji
            direction_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "⚪"
            }.get(pattern_direction, "⚪")
            
            # Determine volume emoji
            volume_emoji = {
                "strong": "📊",
                "moderate": "📈",
                "weak": "📉",
                "none": "➡️"
            }.get(volume_confirmation, "➡️")
            
            # Determine trend alignment emoji
            trend_emoji = {
                "strong_bullish": "🚀",
                "weak_bullish": "📈",
                "strong_bearish": "💥",
                "weak_bearish": "📉",
                "counter_trend": "🔄",
                "neutral": "➡️"
            }.get(trend_alignment, "➡️")
            
            print(f"  {timeframe:>4} | {pattern_emoji} {pattern_name:>20} | {direction_emoji} {pattern_direction:>8} | {volume_emoji} {volume_confirmation:>8} | {trend_emoji} {trend_alignment:>15} | Strength: {pattern_strength:>5.1f}% | R/R: {risk_reward_ratio:>4.1f}")
        
        print("\n" + "="*80)
        print("📈 PRICE ACTION PATTERNS SUMMARY:")
        print("="*80)
        
        # Count by pattern type
        pattern_counts = {}
        for row in data:
            pattern_type = row[2]
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        for pattern_type, count in sorted(pattern_counts.items()):
            pattern_name = pattern_type.replace("_", " ").title() if pattern_type != "none" else "No Pattern"
            print(f"   {pattern_name}: {count}")
        
        # Count by direction
        bullish_count = sum(1 for row in data if row[6] == "bullish")
        bearish_count = sum(1 for row in data if row[6] == "bearish")
        neutral_count = sum(1 for row in data if row[6] == "neutral")
        
        print(f"   🟢 Bullish Patterns: {bullish_count}")
        print(f"   🔴 Bearish Patterns: {bearish_count}")
        print(f"   ⚪ Neutral Patterns: {neutral_count}")
        
        # Count by volume confirmation
        strong_volume_count = sum(1 for row in data if row[8] == "strong")
        moderate_volume_count = sum(1 for row in data if row[8] == "moderate")
        weak_volume_count = sum(1 for row in data if row[8] == "weak")
        no_volume_count = sum(1 for row in data if row[8] == "none")
        
        print(f"   📊 Strong Volume: {strong_volume_count}")
        print(f"   📈 Moderate Volume: {moderate_volume_count}")
        print(f"   📉 Weak Volume: {weak_volume_count}")
        print(f"   ➡️ No Volume: {no_volume_count}")
        
        # Count by trend alignment
        strong_bullish_trend_count = sum(1 for row in data if row[10] == "strong_bullish")
        weak_bullish_trend_count = sum(1 for row in data if row[10] == "weak_bullish")
        strong_bearish_trend_count = sum(1 for row in data if row[10] == "strong_bearish")
        weak_bearish_trend_count = sum(1 for row in data if row[10] == "weak_bearish")
        counter_trend_count = sum(1 for row in data if row[10] == "counter_trend")
        neutral_trend_count = sum(1 for row in data if row[10] == "neutral")
        
        print(f"   🚀 Strong Bullish Trend: {strong_bullish_trend_count}")
        print(f"   📈 Weak Bullish Trend: {weak_bullish_trend_count}")
        print(f"   💥 Strong Bearish Trend: {strong_bearish_trend_count}")
        print(f"   📉 Weak Bearish Trend: {weak_bearish_trend_count}")
        print(f"   🔄 Counter Trend: {counter_trend_count}")
        print(f"   ➡️ Neutral Trend: {neutral_trend_count}")
        
        # Count strong patterns
        strong_patterns = sum(1 for row in data if row[4] > 70)
        moderate_patterns = sum(1 for row in data if 40 < row[4] <= 70)
        weak_patterns = sum(1 for row in data if row[4] <= 40)
        
        print(f"   💪 Strong Patterns (>70%): {strong_patterns}")
        print(f"   📊 Moderate Patterns (40-70%): {moderate_patterns}")
        print(f"   🔸 Weak Patterns (<40%): {weak_patterns}")
        
        # Count good risk/reward ratios
        good_rr_count = sum(1 for row in data if row[11] > 2.0)
        moderate_rr_count = sum(1 for row in data if 1.5 < row[11] <= 2.0)
        poor_rr_count = sum(1 for row in data if row[11] <= 1.5)
        
        print(f"   🎯 Good R/R (>2.0): {good_rr_count}")
        print(f"   📊 Moderate R/R (1.5-2.0): {moderate_rr_count}")
        print(f"   🔸 Poor R/R (<1.5): {poor_rr_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong bullish patterns with good volume
        strong_bullish = [row for row in data if row[6] == "bullish" and row[4] > 60 and row[8] in ["strong", "moderate"]]
        if strong_bullish:
            print("   🟢 Strong Bullish Patterns (Buy Opportunities):")
            for pattern in strong_bullish:
                symbol, timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio, current_price, last_updated = pattern
                print(f"      • {symbol} {timeframe}: {pattern_name} - Strength {pattern_strength:.1f}%, Volume {volume_confirmation}, R/R {risk_reward_ratio:.1f}")
        else:
            print("   ✅ No strong bullish patterns detected")
        
        # Find strong bearish patterns with good volume
        strong_bearish = [row for row in data if row[6] == "bearish" and row[4] > 60 and row[8] in ["strong", "moderate"]]
        if strong_bearish:
            print("   🔴 Strong Bearish Patterns (Sell Opportunities):")
            for pattern in strong_bearish:
                symbol, timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio, current_price, last_updated = pattern
                print(f"      • {symbol} {timeframe}: {pattern_name} - Strength {pattern_strength:.1f}%, Volume {volume_confirmation}, R/R {risk_reward_ratio:.1f}")
        else:
            print("   ✅ No strong bearish patterns detected")
        
        # Find patterns with good risk/reward ratios
        good_rr_patterns = [row for row in data if row[11] > 2.0 and row[2] != "none"]
        if good_rr_patterns:
            print("   🎯 Patterns with Good Risk/Reward (>2.0):")
            for pattern in good_rr_patterns:
                symbol, timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio, current_price, last_updated = pattern
                print(f"      • {symbol} {timeframe}: {pattern_name} - R/R {risk_reward_ratio:.1f}, Direction {pattern_direction}")
        else:
            print("   ✅ No patterns with good risk/reward ratios detected")
        
        # Find counter-trend patterns
        counter_trend = [row for row in data if row[10] == "counter_trend" and row[2] != "none"]
        if counter_trend:
            print("   🔄 Counter-Trend Patterns (Potential Reversals):")
            for pattern in counter_trend:
                symbol, timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio, current_price, last_updated = pattern
                print(f"      • {symbol} {timeframe}: {pattern_name} - Direction {pattern_direction}, Strength {pattern_strength:.1f}%")
        else:
            print("   ✅ No counter-trend patterns detected")
        
        # Find triangle patterns
        triangle_patterns = [row for row in data if "triangle" in row[2] or row[2] == "rectangle"]
        if triangle_patterns:
            print("   📐 Triangle/Rectangle Patterns (Breakout Opportunities):")
            for pattern in triangle_patterns:
                symbol, timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio, current_price, last_updated = pattern
                print(f"      • {symbol} {timeframe}: {pattern_name} - Direction {pattern_direction}, Completion {pattern_completion:.1f}%")
        else:
            print("   ✅ No triangle/rectangle patterns detected")
        
        print("\n" + "="*80)
        print("✅ Price Action Patterns report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Price Action Patterns report: {e}")

def main():
    """Main function to populate Price Action Patterns data"""
    print("🚀 Starting Price Action Patterns data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Price Action Patterns for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        price_patterns_data = calculate_price_patterns_for_symbol(symbol, symbol_id)
        if price_patterns_data:
            if store_price_patterns_data(symbol_id, symbol, price_patterns_data):
                print(f"✅ Stored {len(price_patterns_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Price Action Patterns data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_price_patterns_report()

if __name__ == "__main__":
    main()
