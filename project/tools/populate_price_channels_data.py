#!/usr/bin/env python3
"""
Populate Price Channels (Donchian Channels) Data
Calculates and stores Donchian Channels analysis for all symbols in My Symbols list
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

def calculate_donchian_channels(highs, lows, period=20):
    """Calculate Donchian Channels"""
    if len(highs) < period or len(lows) < period:
        return None, None, None
    
    # Upper channel (highest high in period)
    upper_channel = max(highs[-period:])
    
    # Lower channel (lowest low in period)
    lower_channel = min(lows[-period:])
    
    # Middle channel (average of upper and lower)
    middle_channel = (upper_channel + lower_channel) / 2
    
    return upper_channel, middle_channel, lower_channel

def calculate_channel_width(upper_channel, lower_channel):
    """Calculate channel width"""
    if upper_channel is None or lower_channel is None:
        return 0.0
    
    return upper_channel - lower_channel

def calculate_channel_position(current_price, upper_channel, lower_channel):
    """Calculate position within the channel (0-100%)"""
    if upper_channel is None or lower_channel is None or upper_channel == lower_channel:
        return 50.0
    
    if current_price >= upper_channel:
        return 100.0
    elif current_price <= lower_channel:
        return 0.0
    else:
        return ((current_price - lower_channel) / (upper_channel - lower_channel)) * 100

def determine_breakout_direction(current_price, upper_channel, lower_channel, threshold=0.01):
    """Determine breakout direction"""
    if upper_channel is None or lower_channel is None:
        return "none", 0.0
    
    # Calculate breakout threshold
    upper_threshold = upper_channel * (1 + threshold)
    lower_threshold = lower_channel * (1 - threshold)
    
    # Determine breakout
    if current_price > upper_threshold:
        # Bullish breakout
        breakout_strength = ((current_price - upper_channel) / upper_channel) * 100
        return "bullish", min(breakout_strength, 100.0)
    elif current_price < lower_threshold:
        # Bearish breakout
        breakout_strength = ((lower_channel - current_price) / lower_channel) * 100
        return "bearish", min(breakout_strength, 100.0)
    else:
        return "none", 0.0

def determine_channel_trend(upper_channel, middle_channel, lower_channel, previous_upper, previous_middle, previous_lower):
    """Determine channel trend direction"""
    if any(x is None for x in [upper_channel, middle_channel, lower_channel, previous_upper, previous_middle, previous_lower]):
        return "neutral", 0.0
    
    # Calculate trend based on middle channel movement
    middle_change = ((middle_channel - previous_middle) / previous_middle) * 100
    
    # Calculate trend strength based on all three levels
    upper_change = ((upper_channel - previous_upper) / previous_upper) * 100
    lower_change = ((lower_channel - previous_lower) / previous_lower) * 100
    
    # Determine trend direction
    if middle_change > 1.0 and upper_change > 0.5 and lower_change > 0.5:
        trend_strength = min(abs(middle_change) + abs(upper_change) + abs(lower_change), 100.0)
        return "strong_bullish", trend_strength
    elif middle_change > 0.5:
        trend_strength = min(abs(middle_change), 100.0)
        return "bullish", trend_strength
    elif middle_change < -1.0 and upper_change < -0.5 and lower_change < -0.5:
        trend_strength = min(abs(middle_change) + abs(upper_change) + abs(lower_change), 100.0)
        return "strong_bearish", trend_strength
    elif middle_change < -0.5:
        trend_strength = min(abs(middle_change), 100.0)
        return "bearish", trend_strength
    else:
        return "neutral", 0.0

def determine_volatility_status(channel_width, avg_channel_width, current_price):
    """Determine volatility status"""
    if avg_channel_width == 0:
        return "unknown", 0.0
    
    volatility_ratio = channel_width / avg_channel_width
    
    if volatility_ratio > 2.0:
        return "extreme_high", volatility_ratio * 100
    elif volatility_ratio > 1.5:
        return "high", volatility_ratio * 100
    elif volatility_ratio > 1.2:
        return "moderate_high", volatility_ratio * 100
    elif volatility_ratio < 0.5:
        return "extreme_low", volatility_ratio * 100
    elif volatility_ratio < 0.8:
        return "low", volatility_ratio * 100
    elif volatility_ratio < 1.0:
        return "moderate_low", volatility_ratio * 100
    else:
        return "normal", volatility_ratio * 100

def determine_momentum_status(channel_position, previous_position, threshold=5.0):
    """Determine momentum status"""
    if previous_position is None:
        return "neutral", 0.0
    
    position_change = channel_position - previous_position
    
    if position_change > threshold:
        momentum_strength = min(abs(position_change), 100.0)
        return "bullish", momentum_strength
    elif position_change < -threshold:
        momentum_strength = min(abs(position_change), 100.0)
        return "bearish", momentum_strength
    else:
        return "neutral", 0.0

def calculate_support_resistance_levels(upper_channel, middle_channel, lower_channel):
    """Calculate support and resistance levels from channels"""
    if any(x is None for x in [upper_channel, middle_channel, lower_channel]):
        return "No levels available"
    
    # Support levels (lower channel and middle channel)
    support_levels = [lower_channel, middle_channel]
    
    # Resistance levels (upper channel and middle channel)
    resistance_levels = [upper_channel, middle_channel]
    
    support_str = ", ".join([f"${level:.4f}" for level in support_levels])
    resistance_str = ", ".join([f"${level:.4f}" for level in resistance_levels])
    
    return f"Support: {support_str} | Resistance: {resistance_str}"

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

def calculate_price_channels_for_symbol(symbol, symbol_id):
    """Calculate Price Channels (Donchian Channels) for all timeframes for a symbol"""
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
                
                if len(closes) >= 40:  # Need enough data for Donchian Channels
                    # Calculate current Donchian Channels
                    upper_channel, middle_channel, lower_channel = calculate_donchian_channels(highs, lows, 20)
                    
                    if all(x is not None for x in [upper_channel, middle_channel, lower_channel]):
                        # Calculate previous Donchian Channels for trend analysis
                        if len(closes) >= 60:
                            prev_upper, prev_middle, prev_lower = calculate_donchian_channels(highs[:-20], lows[:-20], 20)
                        else:
                            prev_upper, prev_middle, prev_lower = upper_channel, middle_channel, lower_channel
                        
                        # Calculate channel metrics
                        channel_width = calculate_channel_width(upper_channel, lower_channel)
                        channel_position = calculate_channel_position(current_price, upper_channel, lower_channel)
                        
                        # Determine breakout direction
                        breakout_direction, breakout_strength = determine_breakout_direction(
                            current_price, upper_channel, lower_channel
                        )
                        
                        # Determine channel trend
                        channel_trend, trend_strength = determine_channel_trend(
                            upper_channel, middle_channel, lower_channel,
                            prev_upper, prev_middle, prev_lower
                        )
                        
                        # Calculate average channel width for volatility
                        if len(closes) >= 60:
                            avg_channel_width = np.mean([
                                calculate_channel_width(
                                    max(highs[i:i+20]), min(lows[i:i+20])
                                ) for i in range(0, len(closes)-20, 5)
                            ])
                        else:
                            avg_channel_width = channel_width
                        
                        # Determine volatility status
                        volatility_status, volatility_strength = determine_volatility_status(
                            channel_width, avg_channel_width, current_price
                        )
                        
                        # Calculate previous channel position for momentum
                        if len(closes) >= 40:
                            prev_position = calculate_channel_position(closes[-2], upper_channel, lower_channel)
                        else:
                            prev_position = channel_position
                        
                        # Determine momentum status
                        momentum_status, momentum_strength = determine_momentum_status(
                            channel_position, prev_position
                        )
                        
                        # Calculate support and resistance levels
                        support_resistance_levels = calculate_support_resistance_levels(
                            upper_channel, middle_channel, lower_channel
                        )
                        
                        # Determine volume confirmation
                        volume_confirmation, volume_strength = determine_volume_confirmation(
                            volumes, breakout_direction
                        )
                        
                        results[tf] = {
                            "upper_channel": upper_channel,
                            "middle_channel": middle_channel,
                            "lower_channel": lower_channel,
                            "channel_width": channel_width,
                            "channel_position": channel_position,
                            "breakout_direction": breakout_direction,
                            "breakout_strength": breakout_strength,
                            "channel_trend": channel_trend,
                            "trend_strength": trend_strength,
                            "volatility_status": volatility_status,
                            "volatility_strength": volatility_strength,
                            "momentum_status": momentum_status,
                            "momentum_strength": momentum_strength,
                            "support_resistance_levels": support_resistance_levels,
                            "volume_confirmation": volume_confirmation,
                            "volume_strength": volume_strength,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate Donchian Channels for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Price Channels for {symbol}: {e}")
        return {}

def store_price_channels_data(symbol_id, symbol, price_channels_data):
    """Store Price Channels data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in price_channels_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO price_channels_data 
                (symbol_id, symbol, timeframe, upper_channel, middle_channel, lower_channel,
                channel_width, channel_position, breakout_direction, breakout_strength,
                channel_trend, trend_strength, volatility_status, volatility_strength,
                momentum_status, momentum_strength, support_resistance_levels,
                volume_confirmation, volume_strength, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['upper_channel'], data['middle_channel'],
                data['lower_channel'], data['channel_width'], data['channel_position'],
                data['breakout_direction'], data['breakout_strength'], data['channel_trend'],
                data['trend_strength'], data['volatility_status'], data['volatility_strength'],
                data['momentum_status'], data['momentum_strength'], data['support_resistance_levels'],
                data['volume_confirmation'], data['volume_strength'], data['current_price'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Price Channels data for {symbol}: {e}")
        return False

def generate_price_channels_report():
    """Generate a comprehensive report of all Price Channels data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, channel_position, breakout_direction, breakout_strength,
                   channel_trend, trend_strength, volatility_status, volatility_strength,
                   momentum_status, momentum_strength, volume_confirmation, current_price, last_updated
            FROM price_channels_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Price Channels data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 PRICE CHANNELS (DONCHIAN CHANNELS) COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine position emoji
            if channel_position > 80:
                position_emoji = "🚀"
            elif channel_position > 60:
                position_emoji = "📈"
            elif channel_position > 40:
                position_emoji = "➡️"
            elif channel_position > 20:
                position_emoji = "📉"
            else:
                position_emoji = "💥"
            
            # Determine breakout emoji
            breakout_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(breakout_direction, "⚪")
            
            # Determine trend emoji
            trend_emoji = {
                "strong_bullish": "🚀",
                "bullish": "📈",
                "neutral": "➡️",
                "bearish": "📉",
                "strong_bearish": "💥"
            }.get(channel_trend, "➡️")
            
            # Determine volatility emoji
            volatility_emoji = {
                "extreme_high": "💥",
                "high": "📊",
                "moderate_high": "📈",
                "normal": "➡️",
                "moderate_low": "📉",
                "low": "📊",
                "extreme_low": "🔒",
                "unknown": "❓"
            }.get(volatility_status, "❓")
            
            # Determine momentum emoji
            momentum_emoji = {
                "bullish": "📈",
                "bearish": "📉",
                "neutral": "➡️"
            }.get(momentum_status, "➡️")
            
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
            
            print(f"  {timeframe:>4} | {position_emoji} {channel_position:>5.1f}% | {breakout_emoji} {breakout_direction:>8} | {trend_emoji} {channel_trend:>15} | {volatility_emoji} {volatility_status:>15} | {momentum_emoji} {momentum_status:>8} | {volume_emoji} {volume_confirmation:>15} | Breakout: {breakout_strength:>5.1f}% | Trend: {trend_strength:>5.1f}% | Vol: {volatility_strength:>5.1f}% | Mom: {momentum_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 PRICE CHANNELS SUMMARY:")
        print("="*80)
        
        # Count by channel position
        upper_zone_count = sum(1 for row in data if row[2] > 80)
        upper_mid_zone_count = sum(1 for row in data if 60 < row[2] <= 80)
        middle_zone_count = sum(1 for row in data if 40 < row[2] <= 60)
        lower_mid_zone_count = sum(1 for row in data if 20 < row[2] <= 40)
        lower_zone_count = sum(1 for row in data if row[2] <= 20)
        
        print(f"   🚀 Upper Zone (>80%): {upper_zone_count}")
        print(f"   📈 Upper Mid Zone (60-80%): {upper_mid_zone_count}")
        print(f"   ➡️ Middle Zone (40-60%): {middle_zone_count}")
        print(f"   📉 Lower Mid Zone (20-40%): {lower_mid_zone_count}")
        print(f"   💥 Lower Zone (<20%): {lower_zone_count}")
        
        # Count by breakout direction
        bullish_breakout_count = sum(1 for row in data if row[3] == "bullish")
        bearish_breakout_count = sum(1 for row in data if row[3] == "bearish")
        no_breakout_count = sum(1 for row in data if row[3] == "none")
        
        print(f"   🟢 Bullish Breakout: {bullish_breakout_count}")
        print(f"   🔴 Bearish Breakout: {bearish_breakout_count}")
        print(f"   ⚪ No Breakout: {no_breakout_count}")
        
        # Count by channel trend
        strong_bullish_trend_count = sum(1 for row in data if row[5] == "strong_bullish")
        bullish_trend_count = sum(1 for row in data if row[5] == "bullish")
        neutral_trend_count = sum(1 for row in data if row[5] == "neutral")
        bearish_trend_count = sum(1 for row in data if row[5] == "bearish")
        strong_bearish_trend_count = sum(1 for row in data if row[5] == "strong_bearish")
        
        print(f"   🚀 Strong Bullish Trend: {strong_bullish_trend_count}")
        print(f"   📈 Bullish Trend: {bullish_trend_count}")
        print(f"   ➡️ Neutral Trend: {neutral_trend_count}")
        print(f"   📉 Bearish Trend: {bearish_trend_count}")
        print(f"   💥 Strong Bearish Trend: {strong_bearish_trend_count}")
        
        # Count by volatility status
        extreme_high_volatility_count = sum(1 for row in data if row[7] == "extreme_high")
        high_volatility_count = sum(1 for row in data if row[7] == "high")
        moderate_high_volatility_count = sum(1 for row in data if row[7] == "moderate_high")
        normal_volatility_count = sum(1 for row in data if row[7] == "normal")
        moderate_low_volatility_count = sum(1 for row in data if row[7] == "moderate_low")
        low_volatility_count = sum(1 for row in data if row[7] == "low")
        extreme_low_volatility_count = sum(1 for row in data if row[7] == "extreme_low")
        unknown_volatility_count = sum(1 for row in data if row[7] == "unknown")
        
        print(f"   💥 Extreme High Volatility: {extreme_high_volatility_count}")
        print(f"   📊 High Volatility: {high_volatility_count}")
        print(f"   📈 Moderate High Volatility: {moderate_high_volatility_count}")
        print(f"   ➡️ Normal Volatility: {normal_volatility_count}")
        print(f"   📉 Moderate Low Volatility: {moderate_low_volatility_count}")
        print(f"   📊 Low Volatility: {low_volatility_count}")
        print(f"   🔒 Extreme Low Volatility: {extreme_low_volatility_count}")
        print(f"   ❓ Unknown Volatility: {unknown_volatility_count}")
        
        # Count by momentum status
        bullish_momentum_count = sum(1 for row in data if row[9] == "bullish")
        bearish_momentum_count = sum(1 for row in data if row[9] == "bearish")
        neutral_momentum_count = sum(1 for row in data if row[9] == "neutral")
        
        print(f"   📈 Bullish Momentum: {bullish_momentum_count}")
        print(f"   📉 Bearish Momentum: {bearish_momentum_count}")
        print(f"   ➡️ Neutral Momentum: {neutral_momentum_count}")
        
        # Count by volume confirmation
        strong_bullish_volume_count = sum(1 for row in data if row[11] == "strong_bullish")
        moderate_bullish_volume_count = sum(1 for row in data if row[11] == "moderate_bullish")
        weak_bullish_volume_count = sum(1 for row in data if row[11] == "weak_bullish")
        strong_bearish_volume_count = sum(1 for row in data if row[11] == "strong_bearish")
        moderate_bearish_volume_count = sum(1 for row in data if row[11] == "moderate_bearish")
        weak_bearish_volume_count = sum(1 for row in data if row[11] == "weak_bearish")
        no_volume_count = sum(1 for row in data if row[11] == "none")
        
        print(f"   📊 Strong Bullish Volume: {strong_bullish_volume_count}")
        print(f"   📈 Moderate Bullish Volume: {moderate_bullish_volume_count}")
        print(f"   📈 Weak Bullish Volume: {weak_bullish_volume_count}")
        print(f"   📊 Strong Bearish Volume: {strong_bearish_volume_count}")
        print(f"   📉 Moderate Bearish Volume: {moderate_bearish_volume_count}")
        print(f"   📉 Weak Bearish Volume: {weak_bearish_volume_count}")
        print(f"   ➡️ No Volume: {no_volume_count}")
        
        # Count strong breakouts
        strong_breakouts = sum(1 for row in data if row[4] > 70)
        moderate_breakouts = sum(1 for row in data if 40 < row[4] <= 70)
        weak_breakouts = sum(1 for row in data if row[4] <= 40)
        
        print(f"   💪 Strong Breakouts (>70%): {strong_breakouts}")
        print(f"   📊 Moderate Breakouts (40-70%): {moderate_breakouts}")
        print(f"   🔸 Weak Breakouts (<40%): {weak_breakouts}")
        
        # Count strong trends
        strong_trends = sum(1 for row in data if row[6] > 70)
        moderate_trends = sum(1 for row in data if 40 < row[6] <= 70)
        weak_trends = sum(1 for row in data if row[6] <= 40)
        
        print(f"   💪 Strong Trends (>70%): {strong_trends}")
        print(f"   📊 Moderate Trends (40-70%): {moderate_trends}")
        print(f"   🔸 Weak Trends (<40%): {weak_trends}")
        
        # Count high volatility
        high_volatility = sum(1 for row in data if row[8] > 150)
        moderate_volatility = sum(1 for row in data if 100 < row[8] <= 150)
        low_volatility = sum(1 for row in data if row[8] <= 100)
        
        print(f"   💥 High Volatility (>150%): {high_volatility}")
        print(f"   📊 Moderate Volatility (100-150%): {moderate_volatility}")
        print(f"   🔒 Low Volatility (<100%): {low_volatility}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong breakouts
        strong_breakout = [row for row in data if row[4] > 70]
        if strong_breakout:
            print("   🚀 Strong Breakout Signals (Channel Breakouts):")
            for breakout in strong_breakout:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_direction} breakout - Strength {breakout_strength:.1f}%, Position {channel_position:.1f}%")
        else:
            print("   ✅ No strong breakout signals detected")
        
        # Find moderate breakouts
        moderate_breakout = [row for row in data if 40 < row[4] <= 70]
        if moderate_breakout:
            print("   📊 Moderate Breakout Signals (Watch for Confirmation):")
            for breakout in moderate_breakout:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_direction} breakout - Strength {breakout_strength:.1f}%, Position {channel_position:.1f}%")
        else:
            print("   ✅ No moderate breakout signals detected")
        
        # Find price near channel boundaries
        near_upper = [row for row in data if row[2] > 80 and row[3] == "none"]
        if near_upper:
            print("   📈 Price Near Upper Channel (Resistance Test):")
            for upper in near_upper:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = upper
                print(f"      • {symbol} {timeframe}: Position {channel_position:.1f}% - Trend {channel_trend}, Strength {trend_strength:.1f}%")
        else:
            print("   ✅ No price near upper channel detected")
        
        near_lower = [row for row in data if row[2] < 20 and row[3] == "none"]
        if near_lower:
            print("   📉 Price Near Lower Channel (Support Test):")
            for lower in near_lower:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = lower
                print(f"      • {symbol} {timeframe}: Position {channel_position:.1f}% - Trend {channel_trend}, Strength {trend_strength:.1f}%")
        else:
            print("   ✅ No price near lower channel detected")
        
        # Find strong trends
        strong_trend = [row for row in data if row[6] > 70]
        if strong_trend:
            print("   📊 Strong Channel Trends (Trend Continuation):")
            for trend in strong_trend:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: {channel_trend} trend - Strength {trend_strength:.1f}%, Position {channel_position:.1f}%")
        else:
            print("   ✅ No strong channel trends detected")
        
        # Find high volatility
        high_volatility = [row for row in data if row[8] > 150]
        if high_volatility:
            print("   💥 High Volatility Channels (Breakout Potential):")
            for vol in high_volatility:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = vol
                print(f"      • {symbol} {timeframe}: {volatility_status} volatility - Strength {volatility_strength:.1f}%, Position {channel_position:.1f}%")
        else:
            print("   ✅ No high volatility channels detected")
        
        # Find strong momentum
        strong_momentum = [row for row in data if row[10] > 50]
        if strong_momentum:
            print("   📊 Strong Momentum (Trend Acceleration):")
            for mom in strong_momentum:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = mom
                print(f"      • {symbol} {timeframe}: {momentum_status} momentum - Strength {momentum_strength:.1f}%, Position {channel_position:.1f}%")
        else:
            print("   ✅ No strong momentum detected")
        
        # Find strong volume confirmations
        strong_volume = [row for row in data if "strong" in row[11] and row[4] > 30]
        if strong_volume:
            print("   📊 Strong Volume Confirmations:")
            for volume in strong_volume:
                symbol, timeframe, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation, current_price, last_updated = volume
                print(f"      • {symbol} {timeframe}: {volume_confirmation} volume - Breakout {breakout_direction}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No strong volume confirmations detected")
        
        print("\n" + "="*80)
        print("✅ Price Channels report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Price Channels report: {e}")

def main():
    """Main function to populate Price Channels data"""
    print("🚀 Starting Price Channels (Donchian Channels) data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Price Channels for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        price_channels_data = calculate_price_channels_for_symbol(symbol, symbol_id)
        if price_channels_data:
            if store_price_channels_data(symbol_id, symbol, price_channels_data):
                print(f"✅ Stored {len(price_channels_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Price Channels data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_price_channels_report()

if __name__ == "__main__":
    main()
