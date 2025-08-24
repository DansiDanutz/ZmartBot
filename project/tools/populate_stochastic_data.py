#!/usr/bin/env python3
"""
Populate Stochastic Oscillator Data
Calculates and stores Stochastic Oscillator indicators for all symbols in My Symbols list
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

def calculate_stochastic(highs, lows, closes, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator (%K and %D)"""
    if len(highs) < k_period or len(lows) < k_period or len(closes) < k_period:
        return None, None
    
    # Calculate %K values
    k_values = []
    for i in range(k_period - 1, len(closes)):
        # Get the highest high and lowest low in the k_period
        period_high = max(highs[i-k_period+1:i+1])
        period_low = min(lows[i-k_period+1:i+1])
        
        # Calculate %K
        if period_high == period_low:
            k_percent = 50.0  # Neutral when no range
        else:
            k_percent = ((closes[i] - period_low) / (period_high - period_low)) * 100
        
        k_values.append(k_percent)
    
    if len(k_values) < d_period:
        return None, None
    
    # Calculate %D (SMA of %K)
    d_values = []
    for i in range(d_period - 1, len(k_values)):
        d_percent = np.mean(k_values[i-d_period+1:i+1])
        d_values.append(d_percent)
    
    # Return current %K and %D values
    if k_values and d_values:
        return k_values[-1], d_values[-1]
    else:
        return None, None

def determine_signal_status(k_percent, d_percent, overbought_level=80, oversold_level=20):
    """Determine signal status based on Stochastic values"""
    if k_percent > overbought_level and d_percent > overbought_level:
        return "overbought"
    elif k_percent < oversold_level and d_percent < oversold_level:
        return "oversold"
    elif k_percent > d_percent and k_percent > 50:
        return "bullish"
    elif k_percent < d_percent and k_percent < 50:
        return "bearish"
    else:
        return "neutral"

def calculate_signal_strength(k_percent, d_percent, signal_status, overbought_level=80, oversold_level=20):
    """Calculate signal strength based on Stochastic values"""
    if signal_status == "overbought":
        # Strength based on how far above overbought level
        strength = min((k_percent - overbought_level) / (100 - overbought_level) * 100, 100)
        return max(strength, 0)
    elif signal_status == "oversold":
        # Strength based on how far below oversold level
        strength = min((oversold_level - k_percent) / oversold_level * 100, 100)
        return max(strength, 0)
    elif signal_status == "bullish":
        # Strength based on distance from neutral (50)
        strength = (k_percent - 50) / 50 * 100
        return max(strength, 0)
    elif signal_status == "bearish":
        # Strength based on distance from neutral (50)
        strength = (50 - k_percent) / 50 * 100
        return max(strength, 0)
    else:
        return 0.0

def detect_k_d_crossover(k_values, d_values, period=5):
    """Detect K/D crossover signals"""
    if len(k_values) < period or len(d_values) < period:
        return "none", 0.0
    
    # Get recent values
    recent_k = k_values[-period:]
    recent_d = d_values[-period:]
    
    # Check for crossover
    if recent_k[-1] > recent_d[-1] and recent_k[-2] <= recent_d[-2]:
        # Bullish crossover: K crosses above D
        crossover_strength = abs(recent_k[-1] - recent_d[-1]) / 100 * 100
        return "bullish", crossover_strength
    elif recent_k[-1] < recent_d[-1] and recent_k[-2] >= recent_d[-2]:
        # Bearish crossover: K crosses below D
        crossover_strength = abs(recent_k[-1] - recent_d[-1]) / 100 * 100
        return "bearish", crossover_strength
    else:
        return "none", 0.0

def detect_divergence(k_values, prices, lookback=14):
    """Detect divergence between price and Stochastic %K"""
    if len(k_values) < lookback or len(prices) < lookback:
        return "none", 0.0
    
    # Get recent data
    recent_prices = prices[-lookback:]
    recent_k = k_values[-lookback:]
    
    # Calculate price trend
    price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
    
    # Calculate Stochastic trend
    k_trend = "up" if recent_k[-1] > recent_k[0] else "down"
    
    # Detect divergence
    if price_trend == "up" and k_trend == "down":
        # Bearish divergence: price up, indicator down
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bearish", divergence_strength
    elif price_trend == "down" and k_trend == "up":
        # Bullish divergence: price down, indicator up
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bullish", divergence_strength
    else:
        return "none", 0.0

def determine_momentum_trend(k_values, period=5):
    """Determine momentum trend based on Stochastic %K values"""
    if len(k_values) < period:
        return "neutral", 0.0
    
    recent_k = k_values[-period:]
    
    # Calculate momentum
    momentum_change = recent_k[-1] - recent_k[0]
    momentum_strength = abs(momentum_change) / 100 * 100  # Normalize to 0-100
    
    if momentum_change > 0:
        return "increasing", momentum_strength
    elif momentum_change < 0:
        return "decreasing", momentum_strength
    else:
        return "neutral", 0.0

def detect_extreme_levels(k_percent, extreme_threshold=10):
    """Detect extreme overbought/oversold levels"""
    if k_percent > (100 - extreme_threshold):
        extreme_level = k_percent - (100 - extreme_threshold)
        extreme_type = "extreme_overbought"
    elif k_percent < extreme_threshold:
        extreme_level = extreme_threshold - k_percent
        extreme_type = "extreme_oversold"
    else:
        extreme_level = 0.0
        extreme_type = "none"
    
    return extreme_level, extreme_type

def calculate_stochastic_for_symbol(symbol, symbol_id):
    """Calculate Stochastic Oscillator for all timeframes for a symbol"""
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
                    "15m": 200,
                    "1h": 200,
                    "4h": 200,
                    "1d": 200
                }
                
                klines_response = requests.get(
                    f"https://api.binance.com/api/v3/klines",
                    params={"symbol": symbol, "interval": interval_map[tf], "limit": limit_map[tf]},
                    timeout=10
                )
                klines_response.raise_for_status()
                klines_data = klines_response.json()
                
                # Extract high, low, and close prices
                highs = [float(kline[2]) for kline in klines_data]
                lows = [float(kline[3]) for kline in klines_data]
                closes = [float(kline[4]) for kline in klines_data]
                
                if len(closes) >= 30:  # Need enough data for Stochastic
                    # Calculate Stochastic values for the entire period
                    k_values = []
                    d_values = []
                    
                    for i in range(13, len(closes)):  # Start from 14th element
                        k_percent, d_percent = calculate_stochastic(highs[:i+1], lows[:i+1], closes[:i+1], 14, 3)
                        if k_percent is not None and d_percent is not None:
                            k_values.append(k_percent)
                            d_values.append(d_percent)
                    
                    if len(k_values) >= 10:  # Need enough Stochastic values
                        # Calculate current Stochastic
                        current_k, current_d = calculate_stochastic(highs, lows, closes, 14, 3)
                        
                        if current_k is not None and current_d is not None:
                            # Determine signal status
                            signal_status = determine_signal_status(current_k, current_d)
                            
                            # Calculate signal strength
                            signal_strength = calculate_signal_strength(current_k, current_d, signal_status)
                            
                            # Detect K/D crossover
                            k_d_crossover, k_d_crossover_strength = detect_k_d_crossover(k_values, d_values)
                            
                            # Detect divergence
                            divergence_type, divergence_strength = detect_divergence(k_values, closes)
                            
                            # Determine momentum trend
                            momentum_trend, momentum_strength = determine_momentum_trend(k_values)
                            
                            # Detect extreme levels
                            extreme_level, extreme_type = detect_extreme_levels(current_k)
                            
                            results[tf] = {
                                "k_percent": current_k,
                                "d_percent": current_d,
                                "overbought_level": 80.0,
                                "oversold_level": 20.0,
                                "signal_status": signal_status,
                                "signal_strength": signal_strength,
                                "k_d_crossover": k_d_crossover,
                                "k_d_crossover_strength": k_d_crossover_strength,
                                "divergence_type": divergence_type,
                                "divergence_strength": divergence_strength,
                                "momentum_trend": momentum_trend,
                                "momentum_strength": momentum_strength,
                                "extreme_level": extreme_level,
                                "extreme_type": extreme_type,
                                "current_price": current_price
                            }
                        else:
                            print(f"⚠️ Could not calculate Stochastic for {symbol} {tf}")
                    else:
                        print(f"⚠️ Insufficient Stochastic data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Stochastic for {symbol}: {e}")
        return {}

def store_stochastic_data(symbol_id, symbol, stochastic_data):
    """Store Stochastic Oscillator data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in stochastic_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO stochastic_data 
                (symbol_id, symbol, timeframe, k_percent, d_percent, overbought_level, oversold_level,
                signal_status, signal_strength, k_d_crossover, k_d_crossover_strength,
                divergence_type, divergence_strength, momentum_trend, momentum_strength,
                extreme_level, extreme_type, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['k_percent'], data['d_percent'],
                data['overbought_level'], data['oversold_level'], data['signal_status'],
                data['signal_strength'], data['k_d_crossover'], data['k_d_crossover_strength'],
                data['divergence_type'], data['divergence_strength'], data['momentum_trend'],
                data['momentum_strength'], data['extreme_level'], data['extreme_type'],
                data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Stochastic data for {symbol}: {e}")
        return False

def generate_stochastic_report():
    """Generate a comprehensive report of all Stochastic Oscillator data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, k_percent, d_percent, signal_status, signal_strength,
                   k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength,
                   momentum_trend, momentum_strength, extreme_level, extreme_type,
                   current_price, last_updated
            FROM stochastic_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Stochastic Oscillator data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 STOCHASTIC OSCILLATOR COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine signal emoji
            signal_emoji = {
                "overbought": "🔴",
                "oversold": "🟢",
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "⚪"
            }.get(signal_status, "⚪")
            
            # Determine crossover emoji
            crossover_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(k_d_crossover, "⚪")
            
            # Determine divergence emoji
            divergence_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(divergence_type, "⚪")
            
            # Determine momentum emoji
            momentum_emoji = {
                "increasing": "📈",
                "decreasing": "📉",
                "neutral": "➡️"
            }.get(momentum_trend, "➡️")
            
            # Determine extreme emoji
            extreme_emoji = {
                "extreme_overbought": "🚀",
                "extreme_oversold": "💥",
                "none": "⚪"
            }.get(extreme_type, "⚪")
            
            print(f"  {timeframe:>4} | %K: {k_percent:>5.1f} | %D: {d_percent:>5.1f} | {signal_emoji} {signal_status:>10} | {crossover_emoji} {k_d_crossover:>8} | {divergence_emoji} {divergence_type:>8} | {momentum_emoji} {momentum_trend:>10} | {extreme_emoji} {extreme_type:>18}")
        
        print("\n" + "="*80)
        print("📈 STOCHASTIC OSCILLATOR SUMMARY:")
        print("="*80)
        
        # Count by signal status
        overbought_count = sum(1 for row in data if row[4] == "overbought")
        oversold_count = sum(1 for row in data if row[4] == "oversold")
        bullish_count = sum(1 for row in data if row[4] == "bullish")
        bearish_count = sum(1 for row in data if row[4] == "bearish")
        neutral_count = sum(1 for row in data if row[4] == "neutral")
        
        # Count by crossover type
        bullish_crossover_count = sum(1 for row in data if row[6] == "bullish")
        bearish_crossover_count = sum(1 for row in data if row[6] == "bearish")
        no_crossover_count = sum(1 for row in data if row[6] == "none")
        
        # Count by divergence type
        bullish_divergence_count = sum(1 for row in data if row[8] == "bullish")
        bearish_divergence_count = sum(1 for row in data if row[8] == "bearish")
        no_divergence_count = sum(1 for row in data if row[8] == "none")
        
        # Count by momentum trend
        increasing_momentum_count = sum(1 for row in data if row[10] == "increasing")
        decreasing_momentum_count = sum(1 for row in data if row[10] == "decreasing")
        neutral_momentum_count = sum(1 for row in data if row[10] == "neutral")
        
        # Count extreme levels
        extreme_overbought_count = sum(1 for row in data if row[13] == "extreme_overbought")
        extreme_oversold_count = sum(1 for row in data if row[13] == "extreme_oversold")
        no_extreme_count = sum(1 for row in data if row[13] == "none")
        
        # Count strong signals
        strong_signals = sum(1 for row in data if row[5] > 50)
        moderate_signals = sum(1 for row in data if 20 < row[5] <= 50)
        weak_signals = sum(1 for row in data if row[5] <= 20)
        
        print(f"   🔴 Overbought Signals: {overbought_count}")
        print(f"   🟢 Oversold Signals: {oversold_count}")
        print(f"   🟢 Bullish Signals: {bullish_count}")
        print(f"   🔴 Bearish Signals: {bearish_count}")
        print(f"   ⚪ Neutral Signals: {neutral_count}")
        print(f"   🟢 Bullish Crossovers: {bullish_crossover_count}")
        print(f"   🔴 Bearish Crossovers: {bearish_crossover_count}")
        print(f"   ⚪ No Crossovers: {no_crossover_count}")
        print(f"   🟢 Bullish Divergences: {bullish_divergence_count}")
        print(f"   🔴 Bearish Divergences: {bearish_divergence_count}")
        print(f"   ⚪ No Divergences: {no_divergence_count}")
        print(f"   📈 Increasing Momentum: {increasing_momentum_count}")
        print(f"   📉 Decreasing Momentum: {decreasing_momentum_count}")
        print(f"   ➡️ Neutral Momentum: {neutral_momentum_count}")
        print(f"   🚀 Extreme Overbought: {extreme_overbought_count}")
        print(f"   💥 Extreme Oversold: {extreme_oversold_count}")
        print(f"   ⚪ No Extreme Levels: {no_extreme_count}")
        print(f"   💪 Strong Signals (>50%): {strong_signals}")
        print(f"   📊 Moderate Signals (20-50%): {moderate_signals}")
        print(f"   🔸 Weak Signals (<20%): {weak_signals}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find overbought conditions
        overbought_signals = [row for row in data if row[4] == "overbought" and row[5] > 30]
        if overbought_signals:
            print("   🔴 Overbought Conditions (Potential Sell Opportunities):")
            for signal in overbought_signals:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - %K: {k_percent:.1f}, %D: {d_percent:.1f}")
        else:
            print("   ✅ No strong overbought conditions detected")
        
        # Find oversold conditions
        oversold_signals = [row for row in data if row[4] == "oversold" and row[5] > 30]
        if oversold_signals:
            print("   🟢 Oversold Conditions (Potential Buy Opportunities):")
            for signal in oversold_signals:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - %K: {k_percent:.1f}, %D: {d_percent:.1f}")
        else:
            print("   ✅ No strong oversold conditions detected")
        
        # Find bullish crossovers
        bullish_crossovers = [row for row in data if row[6] == "bullish" and row[7] > 5.0]
        if bullish_crossovers:
            print("   🟢 Bullish Crossovers (Potential Buy Signals):")
            for crossover in bullish_crossovers:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = crossover
                print(f"      • {symbol} {timeframe}: Crossover strength {k_d_crossover_strength:.1f}% - %K crosses above %D")
        else:
            print("   ✅ No bullish crossovers detected")
        
        # Find bearish crossovers
        bearish_crossovers = [row for row in data if row[6] == "bearish" and row[7] > 5.0]
        if bearish_crossovers:
            print("   🔴 Bearish Crossovers (Potential Sell Signals):")
            for crossover in bearish_crossovers:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = crossover
                print(f"      • {symbol} {timeframe}: Crossover strength {k_d_crossover_strength:.1f}% - %K crosses below %D")
        else:
            print("   ✅ No bearish crossovers detected")
        
        # Find bullish divergences
        bullish_divergences = [row for row in data if row[8] == "bullish" and row[9] > 2.0]
        if bullish_divergences:
            print("   🟢 Bullish Divergences (Potential Buy Signals):")
            for divergence in bullish_divergences:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price down, %K up")
        else:
            print("   ✅ No bullish divergences detected")
        
        # Find bearish divergences
        bearish_divergences = [row for row in data if row[8] == "bearish" and row[9] > 2.0]
        if bearish_divergences:
            print("   🔴 Bearish Divergences (Potential Sell Signals):")
            for divergence in bearish_divergences:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price up, %K down")
        else:
            print("   ✅ No bearish divergences detected")
        
        # Find extreme levels
        extreme_overbought = [row for row in data if row[13] == "extreme_overbought"]
        if extreme_overbought:
            print("   🚀 Extreme Overbought Levels (Potential Reversal):")
            for extreme in extreme_overbought:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = extreme
                print(f"      • {symbol} {timeframe}: %K: {k_percent:.1f} (extreme level: {extreme_level:.1f})")
        else:
            print("   ✅ No extreme overbought levels detected")
        
        extreme_oversold = [row for row in data if row[13] == "extreme_oversold"]
        if extreme_oversold:
            print("   💥 Extreme Oversold Levels (Potential Reversal):")
            for extreme in extreme_oversold:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = extreme
                print(f"      • {symbol} {timeframe}: %K: {k_percent:.1f} (extreme level: {extreme_level:.1f})")
        else:
            print("   ✅ No extreme oversold levels detected")
        
        # Find strong momentum trends
        strong_momentum = [row for row in data if row[11] > 30]
        if strong_momentum:
            print("   📈 Strong Momentum Trends:")
            for momentum in strong_momentum:
                symbol, timeframe, k_percent, d_percent, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = momentum
                print(f"      • {symbol} {timeframe}: {momentum_trend} momentum ({momentum_strength:.1f}% strength)")
        else:
            print("   ✅ No strong momentum trends detected")
        
        print("\n" + "="*80)
        print("✅ Stochastic Oscillator report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Stochastic Oscillator report: {e}")

def main():
    """Main function to populate Stochastic Oscillator data"""
    print("🚀 Starting Stochastic Oscillator data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Stochastic Oscillator for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        stochastic_data = calculate_stochastic_for_symbol(symbol, symbol_id)
        if stochastic_data:
            if store_stochastic_data(symbol_id, symbol, stochastic_data):
                print(f"✅ Stored {len(stochastic_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Stochastic Oscillator data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_stochastic_report()

if __name__ == "__main__":
    main()
