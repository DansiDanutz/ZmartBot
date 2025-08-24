#!/usr/bin/env python3
"""
Populate Fibonacci Data
Calculates and stores Fibonacci retracement levels for all symbols in My Symbols list
"""

import sqlite3
import requests
import os
import sys
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

def find_swing_points(prices, window=10):
    """Find swing high and low points in price data"""
    if len(prices) < window * 2:
        return None, None, None
    
    swing_high = max(prices[-window:])
    swing_low = min(prices[-window:])
    
    # Find the actual indices of swing points
    high_idx = len(prices) - window + prices[-window:].index(swing_high)
    low_idx = len(prices) - window + prices[-window:].index(swing_low)
    
    # Determine trend direction based on which came first
    if high_idx < low_idx:
        trend_direction = "bearish"  # High came first, then low
    else:
        trend_direction = "bullish"  # Low came first, then high
    
    return swing_high, swing_low, trend_direction

def calculate_fibonacci_levels(swing_high, swing_low):
    """Calculate Fibonacci retracement levels"""
    price_range = swing_high - swing_low
    
    fib_levels = {
        "fib_0": swing_high,
        "fib_23_6": swing_high - (price_range * 0.236),
        "fib_38_2": swing_high - (price_range * 0.382),
        "fib_50_0": swing_high - (price_range * 0.500),
        "fib_61_8": swing_high - (price_range * 0.618),
        "fib_78_6": swing_high - (price_range * 0.786),
        "fib_100": swing_low
    }
    
    return fib_levels

def determine_price_position(current_price, fib_levels):
    """Determine where current price is relative to Fibonacci levels"""
    if current_price >= fib_levels["fib_0"]:
        return "above_fib_0"
    elif current_price >= fib_levels["fib_23_6"]:
        return "between_fib_0_23_6"
    elif current_price >= fib_levels["fib_38_2"]:
        return "between_fib_23_6_38_2"
    elif current_price >= fib_levels["fib_50_0"]:
        return "between_fib_38_2_50_0"
    elif current_price >= fib_levels["fib_61_8"]:
        return "between_fib_50_0_61_8"
    elif current_price >= fib_levels["fib_78_6"]:
        return "between_fib_61_8_78_6"
    elif current_price >= fib_levels["fib_100"]:
        return "between_fib_78_6_100"
    else:
        return "below_fib_100"

def find_nearest_levels(current_price, fib_levels):
    """Find nearest support and resistance levels"""
    levels = list(fib_levels.values())
    levels.sort()
    
    nearest_support = None
    nearest_resistance = None
    support_distance = float('inf')
    resistance_distance = float('inf')
    
    for level in levels:
        if level <= current_price:
            distance = current_price - level
            if distance < support_distance:
                nearest_support = level
                support_distance = distance
        else:
            distance = level - current_price
            if distance < resistance_distance:
                nearest_resistance = level
                resistance_distance = distance
    
    return nearest_support, nearest_resistance, support_distance, resistance_distance

def calculate_fibonacci_for_symbol(symbol, symbol_id):
    """Calculate Fibonacci retracements for all timeframes for a symbol"""
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
                
                # Extract high and low prices
                highs = [float(kline[2]) for kline in klines_data]
                lows = [float(kline[3]) for kline in klines_data]
                prices = [float(kline[4]) for kline in klines_data]  # Close prices
                
                if len(prices) >= 20:
                    # Find swing points
                    swing_high, swing_low, trend_direction = find_swing_points(prices, window=10)
                    
                    if swing_high and swing_low and swing_high != swing_low:
                        # Calculate Fibonacci levels
                        fib_levels = calculate_fibonacci_levels(swing_high, swing_low)
                        
                        # Determine price position
                        price_position = determine_price_position(current_price, fib_levels)
                        
                        # Find nearest support and resistance
                        nearest_support, nearest_resistance, support_distance, resistance_distance = find_nearest_levels(current_price, fib_levels)
                        
                        # Calculate swing strength (percentage of price range)
                        swing_strength = abs(swing_high - swing_low) / swing_low * 100
                        
                        results[tf] = {
                            "swing_high": swing_high,
                            "swing_low": swing_low,
                            "fib_0": fib_levels["fib_0"],
                            "fib_23_6": fib_levels["fib_23_6"],
                            "fib_38_2": fib_levels["fib_38_2"],
                            "fib_50_0": fib_levels["fib_50_0"],
                            "fib_61_8": fib_levels["fib_61_8"],
                            "fib_78_6": fib_levels["fib_78_6"],
                            "fib_100": fib_levels["fib_100"],
                            "current_price": current_price,
                            "price_position": price_position,
                            "nearest_support": nearest_support,
                            "nearest_resistance": nearest_resistance,
                            "support_distance": support_distance,
                            "resistance_distance": resistance_distance,
                            "trend_direction": trend_direction,
                            "swing_strength": swing_strength
                        }
                    else:
                        print(f"⚠️ Could not find valid swing points for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Fibonacci for {symbol}: {e}")
        return {}

def store_fibonacci_data(symbol_id, symbol, fibonacci_data):
    """Store Fibonacci data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in fibonacci_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO fibonacci_data 
                (symbol_id, symbol, timeframe, swing_high, swing_low, fib_0, fib_23_6, fib_38_2, 
                fib_50_0, fib_61_8, fib_78_6, fib_100, current_price, price_position, 
                nearest_support, nearest_resistance, support_distance, resistance_distance,
                trend_direction, swing_strength, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['swing_high'], data['swing_low'],
                data['fib_0'], data['fib_23_6'], data['fib_38_2'], data['fib_50_0'],
                data['fib_61_8'], data['fib_78_6'], data['fib_100'], data['current_price'],
                data['price_position'], data['nearest_support'], data['nearest_resistance'],
                data['support_distance'], data['resistance_distance'], data['trend_direction'],
                data['swing_strength'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Fibonacci data for {symbol}: {e}")
        return False

def generate_fibonacci_report():
    """Generate a comprehensive report of all Fibonacci data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, swing_high, swing_low, current_price, price_position,
                   nearest_support, nearest_resistance, support_distance, resistance_distance,
                   trend_direction, swing_strength, last_updated
            FROM fibonacci_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Fibonacci data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 FIBONACCI RETRACEMENTS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, swing_high, swing_low, current_price, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, trend_direction, swing_strength, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine trend emoji
            trend_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "⚪"
            }.get(trend_direction, "⚪")
            
            # Determine position emoji
            position_emoji = "📈" if "above" in price_position else "📉" if "below" in price_position else "➡️"
            
            print(f"  {timeframe:>4} | Swing: ${swing_high:>10,.2f} - ${swing_low:>10,.2f} | {trend_emoji} {trend_direction:>8} | {position_emoji} {price_position:>20} | Strength: {swing_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 FIBONACCI SUMMARY:")
        print("="*80)
        
        # Count by trend direction
        bullish_count = sum(1 for row in data if row[10] == "bullish")
        bearish_count = sum(1 for row in data if row[10] == "bearish")
        neutral_count = sum(1 for row in data if row[10] == "neutral")
        
        # Count by price position
        above_fib_0 = sum(1 for row in data if "above_fib_0" in row[5])
        between_0_23_6 = sum(1 for row in data if "between_fib_0_23_6" in row[5])
        between_23_6_38_2 = sum(1 for row in data if "between_fib_23_6_38_2" in row[5])
        between_38_2_50_0 = sum(1 for row in data if "between_fib_38_2_50_0" in row[5])
        between_50_0_61_8 = sum(1 for row in data if "between_fib_50_0_61_8" in row[5])
        between_61_8_78_6 = sum(1 for row in data if "between_fib_61_8_78_6" in row[5])
        between_78_6_100 = sum(1 for row in data if "between_fib_78_6_100" in row[5])
        below_fib_100 = sum(1 for row in data if "below_fib_100" in row[5])
        
        print(f"   🟢 Bullish Trends: {bullish_count}")
        print(f"   🔴 Bearish Trends: {bearish_count}")
        print(f"   ⚪ Neutral Trends: {neutral_count}")
        print(f"   📈 Above Fib 0%: {above_fib_0}")
        print(f"   📊 Between 0-23.6%: {between_0_23_6}")
        print(f"   📊 Between 23.6-38.2%: {between_23_6_38_2}")
        print(f"   📊 Between 38.2-50%: {between_38_2_50_0}")
        print(f"   📊 Between 50-61.8%: {between_50_0_61_8}")
        print(f"   📊 Between 61.8-78.6%: {between_61_8_78_6}")
        print(f"   📊 Between 78.6-100%: {between_78_6_100}")
        print(f"   📉 Below Fib 100%: {below_fib_100}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong bullish trends
        strong_bullish = [row for row in data if row[10] == "bullish" and row[11] > 5.0]
        if strong_bullish:
            print("   🟢 Strong Bullish Trends (Potential Buy Opportunities):")
            for trend in strong_bullish:
                symbol, timeframe, swing_high, swing_low, current_price, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, trend_direction, swing_strength, last_updated = trend
                print(f"      • {symbol} {timeframe}: Swing strength {swing_strength:.1f}% - Price at {price_position}")
        else:
            print("   ✅ No strong bullish trends detected")
        
        # Find strong bearish trends
        strong_bearish = [row for row in data if row[10] == "bearish" and row[11] > 5.0]
        if strong_bearish:
            print("   🔴 Strong Bearish Trends (Potential Sell Opportunities):")
            for trend in strong_bearish:
                symbol, timeframe, swing_high, swing_low, current_price, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, trend_direction, swing_strength, last_updated = trend
                print(f"      • {symbol} {timeframe}: Swing strength {swing_strength:.1f}% - Price at {price_position}")
        else:
            print("   ✅ No strong bearish trends detected")
        
        # Find near support levels
        near_support = [row for row in data if row[8] is not None and row[8] < (row[4] * 0.02)]  # Within 2% of support
        if near_support:
            print("   🛡️ Near Support Levels (Potential Bounce):")
            for support in near_support:
                symbol, timeframe, swing_high, swing_low, current_price, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, trend_direction, swing_strength, last_updated = support
                distance_pct = (support_distance / current_price) * 100
                print(f"      • {symbol} {timeframe}: {distance_pct:.2f}% from support at ${nearest_support:.2f}")
        else:
            print("   ✅ No near support levels detected")
        
        # Find near resistance levels
        near_resistance = [row for row in data if row[9] is not None and row[9] < (row[4] * 0.02)]  # Within 2% of resistance
        if near_resistance:
            print("   🚧 Near Resistance Levels (Potential Rejection):")
            for resistance in near_resistance:
                symbol, timeframe, swing_high, swing_low, current_price, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, trend_direction, swing_strength, last_updated = resistance
                distance_pct = (resistance_distance / current_price) * 100
                print(f"      • {symbol} {timeframe}: {distance_pct:.2f}% from resistance at ${nearest_resistance:.2f}")
        else:
            print("   ✅ No near resistance levels detected")
        
        print("\n" + "="*80)
        print("✅ Fibonacci report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Fibonacci report: {e}")

def main():
    """Main function to populate Fibonacci data"""
    print("🚀 Starting Fibonacci data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Fibonacci for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        fibonacci_data = calculate_fibonacci_for_symbol(symbol, symbol_id)
        if fibonacci_data:
            if store_fibonacci_data(symbol_id, symbol, fibonacci_data):
                print(f"✅ Stored {len(fibonacci_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Fibonacci data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_fibonacci_report()

if __name__ == "__main__":
    main()
