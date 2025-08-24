#!/usr/bin/env python3
"""
Populate Williams %R Data
Calculates and stores Williams %R indicators for all symbols in My Symbols list
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

def calculate_williams_r(highs, lows, closes, period=14):
    """Calculate Williams %R"""
    if len(highs) < period or len(lows) < period or len(closes) < period:
        return None
    
    # Get the highest high and lowest low over the period
    highest_high = max(highs[-period:])
    lowest_low = min(lows[-period:])
    current_close = closes[-1]
    
    # Calculate Williams %R
    if highest_high == lowest_low:
        williams_r = -50.0  # Neutral when no range
    else:
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
    
    return williams_r

def determine_signal_status(williams_r, overbought_level=-20, oversold_level=-80):
    """Determine signal status based on Williams %R value"""
    if williams_r is None:
        return "neutral"
    
    # Williams %R is inverted: higher values are more bullish
    if williams_r > overbought_level:
        return "overbought"  # Above -20 (more bullish)
    elif williams_r < oversold_level:
        return "oversold"    # Below -80 (more bearish)
    elif williams_r > -50:
        return "bullish"     # Between -50 and -20
    elif williams_r < -50:
        return "bearish"     # Between -80 and -50
    else:
        return "neutral"     # At -50

def calculate_signal_strength(williams_r, signal_status):
    """Calculate signal strength based on Williams %R value"""
    if williams_r is None:
        return 0.0
    
    if signal_status == "overbought":
        # Strength based on how far above overbought level (-20)
        strength = min((williams_r - (-20)) / 20 * 100, 100)
        return max(strength, 0)
    elif signal_status == "oversold":
        # Strength based on how far below oversold level (-80)
        strength = min(((-80) - williams_r) / 20 * 100, 100)
        return max(strength, 0)
    elif signal_status == "bullish":
        # Strength based on distance from neutral (-50)
        strength = (williams_r - (-50)) / 30 * 100
        return max(strength, 0)
    elif signal_status == "bearish":
        # Strength based on distance from neutral (-50)
        strength = ((-50) - williams_r) / 30 * 100
        return max(strength, 0)
    else:
        return 0.0

def detect_divergence(williams_r_values, prices, lookback=14):
    """Detect divergence between price and Williams %R"""
    if len(williams_r_values) < lookback or len(prices) < lookback:
        return "none", 0.0
    
    # Get recent data
    recent_prices = prices[-lookback:]
    recent_williams_r = williams_r_values[-lookback:]
    
    # Calculate price trend
    price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
    
    # Calculate Williams %R trend
    williams_r_trend = "up" if recent_williams_r[-1] > recent_williams_r[0] else "down"
    
    # Detect divergence
    if price_trend == "up" and williams_r_trend == "down":
        # Bearish divergence: price up, indicator down
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bearish", divergence_strength
    elif price_trend == "down" and williams_r_trend == "up":
        # Bullish divergence: price down, indicator up
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bullish", divergence_strength
    else:
        return "none", 0.0

def determine_momentum_trend(williams_r_values, period=5):
    """Determine momentum trend based on Williams %R values"""
    if len(williams_r_values) < period:
        return "neutral", 0.0
    
    recent_williams_r = williams_r_values[-period:]
    
    # Calculate momentum
    momentum_change = recent_williams_r[-1] - recent_williams_r[0]
    momentum_strength = abs(momentum_change) / 100 * 100  # Normalize to 0-100
    
    if momentum_change > 0:
        return "increasing", momentum_strength
    elif momentum_change < 0:
        return "decreasing", momentum_strength
    else:
        return "neutral", 0.0

def detect_extreme_levels(williams_r, extreme_threshold=5):
    """Detect extreme overbought/oversold levels"""
    if williams_r is None:
        return 0.0, "none"
    
    if williams_r > 0:  # Above 0 (very bullish)
        extreme_level = williams_r
        extreme_type = "extreme_bullish"
    elif williams_r < -95:  # Below -95 (very bearish)
        extreme_level = abs(williams_r + 100)
        extreme_type = "extreme_bearish"
    else:
        extreme_level = 0.0
        extreme_type = "none"
    
    return extreme_level, extreme_type

def calculate_williams_r_for_symbol(symbol, symbol_id):
    """Calculate Williams %R for all timeframes for a symbol"""
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
                
                if len(closes) >= 20:  # Need enough data for Williams %R
                    # Calculate Williams %R values for the entire period
                    williams_r_values = []
                    for i in range(13, len(closes)):  # Start from 14th element
                        williams_r = calculate_williams_r(highs[:i+1], lows[:i+1], closes[:i+1], 14)
                        if williams_r is not None:
                            williams_r_values.append(williams_r)
                    
                    if len(williams_r_values) >= 10:  # Need enough Williams %R values
                        # Calculate current Williams %R
                        current_williams_r = williams_r_values[-1]
                        
                        # Determine signal status
                        signal_status = determine_signal_status(current_williams_r)
                        
                        # Calculate signal strength
                        signal_strength = calculate_signal_strength(current_williams_r, signal_status)
                        
                        # Detect divergence
                        divergence_type, divergence_strength = detect_divergence(williams_r_values, closes)
                        
                        # Determine momentum trend
                        momentum_trend, momentum_strength = determine_momentum_trend(williams_r_values)
                        
                        # Detect extreme levels
                        extreme_level, extreme_type = detect_extreme_levels(current_williams_r)
                        
                        results[tf] = {
                            "williams_r_value": current_williams_r,
                            "overbought_level": -20.0,
                            "oversold_level": -80.0,
                            "signal_status": signal_status,
                            "signal_strength": signal_strength,
                            "divergence_type": divergence_type,
                            "divergence_strength": divergence_strength,
                            "momentum_trend": momentum_trend,
                            "momentum_strength": momentum_strength,
                            "extreme_level": extreme_level,
                            "extreme_type": extreme_type,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Insufficient Williams %R data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Williams %R for {symbol}: {e}")
        return {}

def store_williams_r_data(symbol_id, symbol, williams_r_data):
    """Store Williams %R data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in williams_r_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO williams_r_data 
                (symbol_id, symbol, timeframe, williams_r_value, overbought_level, oversold_level,
                signal_status, signal_strength, divergence_type, divergence_strength,
                momentum_trend, momentum_strength, extreme_level, extreme_type,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['williams_r_value'],
                data['overbought_level'], data['oversold_level'], data['signal_status'],
                data['signal_strength'], data['divergence_type'], data['divergence_strength'],
                data['momentum_trend'], data['momentum_strength'], data['extreme_level'],
                data['extreme_type'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Williams %R data for {symbol}: {e}")
        return False

def generate_williams_r_report():
    """Generate a comprehensive report of all Williams %R data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, williams_r_value, signal_status, signal_strength,
                   divergence_type, divergence_strength, momentum_trend, momentum_strength,
                   extreme_level, extreme_type, current_price, last_updated
            FROM williams_r_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Williams %R data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 WILLIAMS %R COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = row
            
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
                "extreme_bullish": "🚀",
                "extreme_bearish": "💥",
                "none": "⚪"
            }.get(extreme_type, "⚪")
            
            print(f"  {timeframe:>4} | %R: {williams_r_value:>7.1f} | {signal_emoji} {signal_status:>10} | {divergence_emoji} {divergence_type:>8} | {momentum_emoji} {momentum_trend:>10} | {extreme_emoji} {extreme_type:>15}")
        
        print("\n" + "="*80)
        print("📈 WILLIAMS %R SUMMARY:")
        print("="*80)
        
        # Count by signal status
        overbought_count = sum(1 for row in data if row[3] == "overbought")
        oversold_count = sum(1 for row in data if row[3] == "oversold")
        bullish_count = sum(1 for row in data if row[3] == "bullish")
        bearish_count = sum(1 for row in data if row[3] == "bearish")
        neutral_count = sum(1 for row in data if row[3] == "neutral")
        
        # Count by divergence type
        bullish_divergence_count = sum(1 for row in data if row[5] == "bullish")
        bearish_divergence_count = sum(1 for row in data if row[5] == "bearish")
        no_divergence_count = sum(1 for row in data if row[5] == "none")
        
        # Count by momentum trend
        increasing_momentum_count = sum(1 for row in data if row[7] == "increasing")
        decreasing_momentum_count = sum(1 for row in data if row[7] == "decreasing")
        neutral_momentum_count = sum(1 for row in data if row[7] == "neutral")
        
        # Count extreme levels
        extreme_bullish_count = sum(1 for row in data if row[10] == "extreme_bullish")
        extreme_bearish_count = sum(1 for row in data if row[10] == "extreme_bearish")
        no_extreme_count = sum(1 for row in data if row[10] == "none")
        
        # Count strong signals
        strong_signals = sum(1 for row in data if row[4] > 50)
        moderate_signals = sum(1 for row in data if 20 < row[4] <= 50)
        weak_signals = sum(1 for row in data if row[4] <= 20)
        
        print(f"   🔴 Overbought Signals: {overbought_count}")
        print(f"   🟢 Oversold Signals: {oversold_count}")
        print(f"   🟢 Bullish Signals: {bullish_count}")
        print(f"   🔴 Bearish Signals: {bearish_count}")
        print(f"   ⚪ Neutral Signals: {neutral_count}")
        print(f"   🟢 Bullish Divergences: {bullish_divergence_count}")
        print(f"   🔴 Bearish Divergences: {bearish_divergence_count}")
        print(f"   ⚪ No Divergences: {no_divergence_count}")
        print(f"   📈 Increasing Momentum: {increasing_momentum_count}")
        print(f"   📉 Decreasing Momentum: {decreasing_momentum_count}")
        print(f"   ➡️ Neutral Momentum: {neutral_momentum_count}")
        print(f"   🚀 Extreme Bullish: {extreme_bullish_count}")
        print(f"   💥 Extreme Bearish: {extreme_bearish_count}")
        print(f"   ⚪ No Extreme Levels: {no_extreme_count}")
        print(f"   💪 Strong Signals (>50%): {strong_signals}")
        print(f"   📊 Moderate Signals (20-50%): {moderate_signals}")
        print(f"   🔸 Weak Signals (<20%): {weak_signals}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find overbought conditions
        overbought_signals = [row for row in data if row[3] == "overbought" and row[4] > 30]
        if overbought_signals:
            print("   🔴 Overbought Conditions (Potential Sell Opportunities):")
            for signal in overbought_signals:
                symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - Williams %R: {williams_r_value:.1f}")
        else:
            print("   ✅ No strong overbought conditions detected")
        
        # Find oversold conditions
        oversold_signals = [row for row in data if row[3] == "oversold" and row[4] > 30]
        if oversold_signals:
            print("   🟢 Oversold Conditions (Potential Buy Opportunities):")
            for signal in oversold_signals:
                symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - Williams %R: {williams_r_value:.1f}")
        else:
            print("   ✅ No strong oversold conditions detected")
        
        # Find bullish divergences
        bullish_divergences = [row for row in data if row[5] == "bullish" and row[6] > 2.0]
        if bullish_divergences:
            print("   🟢 Bullish Divergences (Potential Buy Signals):")
            for divergence in bullish_divergences:
                symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price down, Williams %R up")
        else:
            print("   ✅ No bullish divergences detected")
        
        # Find bearish divergences
        bearish_divergences = [row for row in data if row[5] == "bearish" and row[6] > 2.0]
        if bearish_divergences:
            print("   🔴 Bearish Divergences (Potential Sell Signals):")
            for divergence in bearish_divergences:
                symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price up, Williams %R down")
        else:
            print("   ✅ No bearish divergences detected")
        
        # Find extreme levels
        extreme_bullish = [row for row in data if row[10] == "extreme_bullish"]
        if extreme_bullish:
            print("   🚀 Extreme Bullish Levels (Potential Reversal):")
            for extreme in extreme_bullish:
                symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = extreme
                print(f"      • {symbol} {timeframe}: Williams %R: {williams_r_value:.1f} (extreme level: {extreme_level:.1f})")
        else:
            print("   ✅ No extreme bullish levels detected")
        
        extreme_bearish = [row for row in data if row[10] == "extreme_bearish"]
        if extreme_bearish:
            print("   💥 Extreme Bearish Levels (Potential Reversal):")
            for extreme in extreme_bearish:
                symbol, timeframe, williams_r_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = extreme
                print(f"      • {symbol} {timeframe}: Williams %R: {williams_r_value:.1f} (extreme level: {extreme_level:.1f})")
        else:
            print("   ✅ No extreme bearish levels detected")
        
        print("\n" + "="*80)
        print("✅ Williams %R report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Williams %R report: {e}")

def main():
    """Main function to populate Williams %R data"""
    print("🚀 Starting Williams %R data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Williams %R for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        williams_r_data = calculate_williams_r_for_symbol(symbol, symbol_id)
        if williams_r_data:
            if store_williams_r_data(symbol_id, symbol, williams_r_data):
                print(f"✅ Stored {len(williams_r_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Williams %R data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_williams_r_report()

if __name__ == "__main__":
    main()
