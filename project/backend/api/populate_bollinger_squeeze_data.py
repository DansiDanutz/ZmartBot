#!/usr/bin/env python3
"""
Populate Bollinger Band Squeeze Data
Calculates and stores Bollinger Band Squeeze analysis for all symbols in My Symbols list
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

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return None, None, None
    
    # Calculate Simple Moving Average (middle band)
    sma = np.mean(prices[-period:])
    
    # Calculate Standard Deviation
    std = np.std(prices[-period:])
    
    # Calculate Upper and Lower Bands
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    
    return upper_band, sma, lower_band

def calculate_band_width(upper_band, lower_band, middle_band):
    """Calculate Bollinger Band width"""
    if middle_band == 0:
        return 0.0
    
    band_width = (upper_band - lower_band) / middle_band
    return band_width

def calculate_band_width_percentile(band_widths, current_width):
    """Calculate percentile of current band width compared to historical"""
    if len(band_widths) == 0:
        return 50.0
    
    # Calculate percentile
    percentile = (sum(1 for width in band_widths if width < current_width) / len(band_widths)) * 100
    return percentile

def determine_squeeze_status(band_width_percentile, squeeze_threshold=20):
    """Determine if Bollinger Bands are in a squeeze"""
    if band_width_percentile <= squeeze_threshold:
        return "squeeze"
    elif band_width_percentile <= 40:
        return "tight"
    else:
        return "normal"

def calculate_squeeze_strength(band_width_percentile):
    """Calculate squeeze strength based on percentile"""
    if band_width_percentile <= 10:
        return 100.0
    elif band_width_percentile <= 20:
        return 90.0
    elif band_width_percentile <= 30:
        return 70.0
    elif band_width_percentile <= 40:
        return 50.0
    else:
        return 0.0

def calculate_price_position(current_price, upper_band, lower_band):
    """Calculate price position within Bollinger Bands"""
    if upper_band == lower_band:
        return 50.0
    
    position = ((current_price - lower_band) / (upper_band - lower_band)) * 100
    return max(0.0, min(100.0, position))

def calculate_volatility_ratio(current_volatility, historical_volatility):
    """Calculate volatility ratio"""
    if historical_volatility == 0:
        return 1.0
    
    return current_volatility / historical_volatility

def calculate_historical_volatility(prices, period=20):
    """Calculate historical volatility"""
    if len(prices) < period + 1:
        return 0.0
    
    # Calculate daily returns
    returns = []
    for i in range(len(prices) - period, len(prices) - 1):
        if prices[i] != 0:
            return_val = (prices[i + 1] - prices[i]) / prices[i]
            returns.append(return_val)
    
    if len(returns) == 0:
        return 0.0
    
    # Calculate volatility (standard deviation of returns)
    volatility = np.std(returns)
    return volatility

def calculate_current_volatility(prices, period=5):
    """Calculate current volatility"""
    if len(prices) < period + 1:
        return 0.0
    
    # Calculate recent returns
    returns = []
    for i in range(len(prices) - period, len(prices) - 1):
        if prices[i] != 0:
            return_val = (prices[i + 1] - prices[i]) / prices[i]
            returns.append(return_val)
    
    if len(returns) == 0:
        return 0.0
    
    # Calculate current volatility
    volatility = np.std(returns)
    return volatility

def determine_breakout_potential(price_position, squeeze_strength, volatility_ratio):
    """Determine breakout potential"""
    if squeeze_strength < 50:
        return "none"
    
    # High squeeze strength with price near bands indicates breakout potential
    if squeeze_strength > 70:
        if price_position > 80:
            return "high_bullish"
        elif price_position < 20:
            return "high_bearish"
        else:
            return "high_neutral"
    elif squeeze_strength > 50:
        if price_position > 70:
            return "moderate_bullish"
        elif price_position < 30:
            return "moderate_bearish"
        else:
            return "moderate_neutral"
    else:
        return "none"

def determine_breakout_direction(price_position, volatility_ratio):
    """Determine likely breakout direction"""
    if price_position > 70:
        return "bullish"
    elif price_position < 30:
        return "bearish"
    else:
        return "neutral"

def calculate_breakout_strength(squeeze_strength, volatility_ratio, price_position):
    """Calculate breakout strength"""
    # Base strength from squeeze
    base_strength = squeeze_strength
    
    # Volatility multiplier
    volatility_multiplier = min(volatility_ratio, 2.0)
    
    # Position multiplier (closer to bands = stronger)
    if price_position > 80 or price_position < 20:
        position_multiplier = 1.5
    elif price_position > 70 or price_position < 30:
        position_multiplier = 1.2
    else:
        position_multiplier = 1.0
    
    strength = base_strength * volatility_multiplier * position_multiplier
    return min(strength, 100.0)

def detect_momentum_divergence(prices, volumes, period=10):
    """Detect momentum divergence"""
    if len(prices) < period or len(volumes) < period:
        return "none", 0.0
    
    # Calculate price momentum
    price_momentum = (prices[-1] - prices[-period]) / prices[-period]
    
    # Calculate volume momentum
    volume_momentum = (volumes[-1] - np.mean(volumes[-period:])) / np.mean(volumes[-period:])
    
    # Detect divergence
    if price_momentum > 0 and volume_momentum < -0.2:
        # Price up, volume down = bearish divergence
        return "bearish", abs(price_momentum) * 100
    elif price_momentum < 0 and volume_momentum > 0.2:
        # Price down, volume up = bullish divergence
        return "bullish", abs(price_momentum) * 100
    else:
        return "none", 0.0

def determine_volume_profile(volumes, period=20):
    """Determine volume profile"""
    if len(volumes) < period:
        return "normal", 0.0
    
    current_volume = volumes[-1]
    avg_volume = np.mean(volumes[-period:])
    
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    if volume_ratio > 2.0:
        return "extremely_high", volume_ratio * 100
    elif volume_ratio > 1.5:
        return "high", volume_ratio * 100
    elif volume_ratio > 1.2:
        return "above_average", volume_ratio * 100
    elif volume_ratio > 0.8:
        return "normal", volume_ratio * 100
    elif volume_ratio > 0.5:
        return "below_average", volume_ratio * 100
    else:
        return "low", volume_ratio * 100

def calculate_squeeze_duration(band_widths, squeeze_threshold=20):
    """Calculate how long the squeeze has been active"""
    duration = 0
    
    # Count consecutive periods with low band width
    for width_percentile in reversed(band_widths):
        if width_percentile <= squeeze_threshold:
            duration += 1
        else:
            break
    
    return duration

def calculate_bollinger_squeeze_for_symbol(symbol, symbol_id):
    """Calculate Bollinger Band Squeeze for all timeframes for a symbol"""
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
                closes = [float(kline[4]) for kline in klines_data]
                volumes = [float(kline[5]) for kline in klines_data]
                
                if len(closes) >= 50:  # Need enough data for analysis
                    # Calculate Bollinger Bands for current period
                    upper_band, middle_band, lower_band = calculate_bollinger_bands(closes, 20, 2)
                    
                    if upper_band is not None:
                        # Calculate current band width
                        current_band_width = calculate_band_width(upper_band, lower_band, middle_band)
                        
                        # Calculate historical band widths for percentile calculation
                        historical_band_widths = []
                        for i in range(20, len(closes) - 20):
                            hist_upper, hist_middle, hist_lower = calculate_bollinger_bands(closes[:i+1], 20, 2)
                            if hist_upper is not None:
                                hist_width = calculate_band_width(hist_upper, hist_lower, hist_middle)
                                historical_band_widths.append(hist_width)
                        
                        # Calculate band width percentile
                        band_width_percentile = calculate_band_width_percentile(historical_band_widths, current_band_width)
                        
                        # Determine squeeze status
                        squeeze_status = determine_squeeze_status(band_width_percentile)
                        squeeze_strength = calculate_squeeze_strength(band_width_percentile)
                        
                        # Calculate price position
                        price_position = calculate_price_position(current_price, upper_band, lower_band)
                        
                        # Calculate volatility metrics
                        historical_volatility = calculate_historical_volatility(closes)
                        current_volatility = calculate_current_volatility(closes)
                        volatility_ratio = calculate_volatility_ratio(current_volatility, historical_volatility)
                        
                        # Calculate squeeze duration
                        squeeze_duration = calculate_squeeze_duration([bw for bw in historical_band_widths[-20:]])
                        
                        # Determine breakout potential
                        breakout_potential = determine_breakout_potential(price_position, squeeze_strength, volatility_ratio)
                        breakout_direction = determine_breakout_direction(price_position, volatility_ratio)
                        breakout_strength = calculate_breakout_strength(squeeze_strength, volatility_ratio, price_position)
                        
                        # Detect momentum divergence
                        momentum_divergence, momentum_strength = detect_momentum_divergence(closes, volumes)
                        
                        # Determine volume profile
                        volume_profile, volume_strength = determine_volume_profile(volumes)
                        
                        results[tf] = {
                            "squeeze_status": squeeze_status,
                            "squeeze_strength": squeeze_strength,
                            "band_width": current_band_width,
                            "band_width_percentile": band_width_percentile,
                            "upper_band": upper_band,
                            "middle_band": middle_band,
                            "lower_band": lower_band,
                            "current_price": current_price,
                            "price_position": price_position,
                            "volatility_ratio": volatility_ratio,
                            "historical_volatility": historical_volatility,
                            "current_volatility": current_volatility,
                            "squeeze_duration": squeeze_duration,
                            "breakout_potential": breakout_potential,
                            "breakout_direction": breakout_direction,
                            "breakout_strength": breakout_strength,
                            "momentum_divergence": momentum_divergence,
                            "momentum_strength": momentum_strength,
                            "volume_profile": volume_profile,
                            "volume_strength": volume_strength
                        }
                    else:
                        print(f"⚠️ Could not calculate Bollinger Bands for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Bollinger Band Squeeze for {symbol}: {e}")
        return {}

def store_bollinger_squeeze_data(symbol_id, symbol, bollinger_squeeze_data):
    """Store Bollinger Band Squeeze data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in bollinger_squeeze_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO bollinger_squeeze_data 
                (symbol_id, symbol, timeframe, squeeze_status, squeeze_strength,
                band_width, band_width_percentile, upper_band, middle_band, lower_band,
                current_price, price_position, volatility_ratio, historical_volatility,
                current_volatility, squeeze_duration, breakout_potential, breakout_direction,
                breakout_strength, momentum_divergence, momentum_strength,
                volume_profile, volume_strength, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['squeeze_status'], data['squeeze_strength'],
                data['band_width'], data['band_width_percentile'], data['upper_band'],
                data['middle_band'], data['lower_band'], data['current_price'],
                data['price_position'], data['volatility_ratio'], data['historical_volatility'],
                data['current_volatility'], data['squeeze_duration'], data['breakout_potential'],
                data['breakout_direction'], data['breakout_strength'], data['momentum_divergence'],
                data['momentum_strength'], data['volume_profile'], data['volume_strength'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Bollinger Band Squeeze data for {symbol}: {e}")
        return False

def generate_bollinger_squeeze_report():
    """Generate a comprehensive report of all Bollinger Band Squeeze data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile,
                   price_position, breakout_potential, breakout_direction, breakout_strength,
                   momentum_divergence, volume_profile, current_price, last_updated
            FROM bollinger_squeeze_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Bollinger Band Squeeze data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 BOLLINGER BAND SQUEEZE COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine squeeze emoji
            squeeze_emoji = {
                "squeeze": "🔒",
                "tight": "📏",
                "normal": "📊"
            }.get(squeeze_status, "📊")
            
            # Determine breakout emoji
            breakout_emoji = {
                "high_bullish": "🚀",
                "moderate_bullish": "📈",
                "high_bearish": "💥",
                "moderate_bearish": "📉",
                "high_neutral": "⚖️",
                "moderate_neutral": "➡️",
                "none": "⚪"
            }.get(breakout_potential, "⚪")
            
            # Determine direction emoji
            direction_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "⚪"
            }.get(breakout_direction, "⚪")
            
            # Determine momentum emoji
            momentum_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(momentum_divergence, "⚪")
            
            # Determine volume emoji
            volume_emoji = {
                "extremely_high": "📊",
                "high": "📈",
                "above_average": "📊",
                "normal": "➡️",
                "below_average": "📉",
                "low": "📉"
            }.get(volume_profile, "➡️")
            
            print(f"  {timeframe:>4} | {squeeze_emoji} {squeeze_status:>8} | {breakout_emoji} {breakout_potential:>15} | {direction_emoji} {breakout_direction:>8} | {momentum_emoji} {momentum_divergence:>8} | {volume_emoji} {volume_profile:>15} | Strength: {squeeze_strength:>5.1f}% | Position: {price_position:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 BOLLINGER BAND SQUEEZE SUMMARY:")
        print("="*80)
        
        # Count by squeeze status
        squeeze_count = sum(1 for row in data if row[2] == "squeeze")
        tight_count = sum(1 for row in data if row[2] == "tight")
        normal_count = sum(1 for row in data if row[2] == "normal")
        
        print(f"   🔒 Squeeze: {squeeze_count}")
        print(f"   📏 Tight: {tight_count}")
        print(f"   📊 Normal: {normal_count}")
        
        # Count by breakout potential
        high_bullish_count = sum(1 for row in data if row[6] == "high_bullish")
        moderate_bullish_count = sum(1 for row in data if row[6] == "moderate_bullish")
        high_bearish_count = sum(1 for row in data if row[6] == "high_bearish")
        moderate_bearish_count = sum(1 for row in data if row[6] == "moderate_bearish")
        high_neutral_count = sum(1 for row in data if row[6] == "high_neutral")
        moderate_neutral_count = sum(1 for row in data if row[6] == "moderate_neutral")
        none_count = sum(1 for row in data if row[6] == "none")
        
        print(f"   🚀 High Bullish: {high_bullish_count}")
        print(f"   📈 Moderate Bullish: {moderate_bullish_count}")
        print(f"   💥 High Bearish: {high_bearish_count}")
        print(f"   📉 Moderate Bearish: {moderate_bearish_count}")
        print(f"   ⚖️ High Neutral: {high_neutral_count}")
        print(f"   ➡️ Moderate Neutral: {moderate_neutral_count}")
        print(f"   ⚪ None: {none_count}")
        
        # Count by breakout direction
        bullish_direction_count = sum(1 for row in data if row[7] == "bullish")
        bearish_direction_count = sum(1 for row in data if row[7] == "bearish")
        neutral_direction_count = sum(1 for row in data if row[7] == "neutral")
        
        print(f"   🟢 Bullish Direction: {bullish_direction_count}")
        print(f"   🔴 Bearish Direction: {bearish_direction_count}")
        print(f"   ⚪ Neutral Direction: {neutral_direction_count}")
        
        # Count by momentum divergence
        bullish_momentum_count = sum(1 for row in data if row[9] == "bullish")
        bearish_momentum_count = sum(1 for row in data if row[9] == "bearish")
        no_momentum_count = sum(1 for row in data if row[9] == "none")
        
        print(f"   🟢 Bullish Momentum: {bullish_momentum_count}")
        print(f"   🔴 Bearish Momentum: {bearish_momentum_count}")
        print(f"   ⚪ No Momentum: {no_momentum_count}")
        
        # Count by volume profile
        extremely_high_volume_count = sum(1 for row in data if row[10] == "extremely_high")
        high_volume_count = sum(1 for row in data if row[10] == "high")
        above_average_volume_count = sum(1 for row in data if row[10] == "above_average")
        normal_volume_count = sum(1 for row in data if row[10] == "normal")
        below_average_volume_count = sum(1 for row in data if row[10] == "below_average")
        low_volume_count = sum(1 for row in data if row[10] == "low")
        
        print(f"   📊 Extremely High Volume: {extremely_high_volume_count}")
        print(f"   📈 High Volume: {high_volume_count}")
        print(f"   📊 Above Average Volume: {above_average_volume_count}")
        print(f"   ➡️ Normal Volume: {normal_volume_count}")
        print(f"   📉 Below Average Volume: {below_average_volume_count}")
        print(f"   📉 Low Volume: {low_volume_count}")
        
        # Count strong squeezes
        strong_squeezes = sum(1 for row in data if row[3] > 70)
        moderate_squeezes = sum(1 for row in data if 40 < row[3] <= 70)
        weak_squeezes = sum(1 for row in data if row[3] <= 40)
        
        print(f"   💪 Strong Squeezes (>70%): {strong_squeezes}")
        print(f"   📊 Moderate Squeezes (40-70%): {moderate_squeezes}")
        print(f"   🔸 Weak Squeezes (<40%): {weak_squeezes}")
        
        # Count strong breakouts
        strong_breakouts = sum(1 for row in data if row[8] > 70)
        moderate_breakouts = sum(1 for row in data if 40 < row[8] <= 70)
        weak_breakouts = sum(1 for row in data if row[8] <= 40)
        
        print(f"   💪 Strong Breakouts (>70%): {strong_breakouts}")
        print(f"   📊 Moderate Breakouts (40-70%): {moderate_breakouts}")
        print(f"   🔸 Weak Breakouts (<40%): {weak_breakouts}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find high breakout potential
        high_breakout = [row for row in data if "high" in row[6] and row[8] > 50]
        if high_breakout:
            print("   🚀 High Breakout Potential (Strong Signals):")
            for breakout in high_breakout:
                symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_potential} - Direction {breakout_direction}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No high breakout potential detected")
        
        # Find moderate breakout potential
        moderate_breakout = [row for row in data if "moderate" in row[6] and row[8] > 30]
        if moderate_breakout:
            print("   📊 Moderate Breakout Potential (Watch for Confirmation):")
            for breakout in moderate_breakout:
                symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_potential} - Direction {breakout_direction}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No moderate breakout potential detected")
        
        # Find momentum divergences
        momentum_divergences = [row for row in data if row[9] != "none" and row[8] > 20]
        if momentum_divergences:
            print("   🔄 Momentum Divergences (Potential Reversals):")
            for divergence in momentum_divergences:
                symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: {momentum_divergence} divergence - Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No momentum divergences detected")
        
        # Find high volume squeezes
        high_volume_squeezes = [row for row in data if row[2] == "squeeze" and row[10] in ["high", "extremely_high"]]
        if high_volume_squeezes:
            print("   📊 High Volume Squeezes (Strong Confirmation):")
            for squeeze in high_volume_squeezes:
                symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, current_price, last_updated = squeeze
                print(f"      • {symbol} {timeframe}: {volume_profile} volume - Breakout {breakout_potential}, Strength {breakout_strength:.1f}%")
        else:
            print("   ✅ No high volume squeezes detected")
        
        # Find price near bands
        near_bands = [row for row in data if (row[5] > 80 or row[5] < 20) and row[3] > 50]
        if near_bands:
            print("   📍 Price Near Bands (Breakout Imminent):")
            for near in near_bands:
                symbol, timeframe, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, current_price, last_updated = near
                position_desc = "upper" if price_position > 80 else "lower"
                print(f"      • {symbol} {timeframe}: Near {position_desc} band ({price_position:.1f}%) - {breakout_potential}")
        else:
            print("   ✅ No price near bands detected")
        
        print("\n" + "="*80)
        print("✅ Bollinger Band Squeeze report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Bollinger Band Squeeze report: {e}")

def main():
    """Main function to populate Bollinger Band Squeeze data"""
    print("🚀 Starting Bollinger Band Squeeze data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Bollinger Band Squeeze for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        bollinger_squeeze_data = calculate_bollinger_squeeze_for_symbol(symbol, symbol_id)
        if bollinger_squeeze_data:
            if store_bollinger_squeeze_data(symbol_id, symbol, bollinger_squeeze_data):
                print(f"✅ Stored {len(bollinger_squeeze_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Bollinger Band Squeeze data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_bollinger_squeeze_report()

if __name__ == "__main__":
    main()
