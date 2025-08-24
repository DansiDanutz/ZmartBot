#!/usr/bin/env python3
"""
Populate Ichimoku Data
Calculates and stores Ichimoku Cloud indicators for all symbols in My Symbols list
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

def calculate_tenkan_sen(highs, lows, period=9):
    """Calculate Tenkan-sen (Conversion Line)"""
    if len(highs) < period or len(lows) < period:
        return None
    
    highest_high = max(highs[-period:])
    lowest_low = min(lows[-period:])
    
    return (highest_high + lowest_low) / 2

def calculate_kijun_sen(highs, lows, period=26):
    """Calculate Kijun-sen (Base Line)"""
    if len(highs) < period or len(lows) < period:
        return None
    
    highest_high = max(highs[-period:])
    lowest_low = min(lows[-period:])
    
    return (highest_high + lowest_low) / 2

def calculate_senkou_span_a(tenkan_sen, kijun_sen):
    """Calculate Senkou Span A (Leading Span A)"""
    if tenkan_sen is None or kijun_sen is None:
        return None
    
    return (tenkan_sen + kijun_sen) / 2

def calculate_senkou_span_b(highs, lows, period=52):
    """Calculate Senkou Span B (Leading Span B)"""
    if len(highs) < period or len(lows) < period:
        return None
    
    highest_high = max(highs[-period:])
    lowest_low = min(lows[-period:])
    
    return (highest_high + lowest_low) / 2

def calculate_chikou_span(prices, period=26):
    """Calculate Chikou Span (Lagging Span)"""
    if len(prices) < period:
        return None
    
    return prices[-period]

def determine_cloud_color(senkou_span_a, senkou_span_b):
    """Determine cloud color based on Senkou Span A and B"""
    if senkou_span_a is None or senkou_span_b is None:
        return "neutral"
    
    if senkou_span_a > senkou_span_b:
        return "green"  # Bullish cloud
    elif senkou_span_a < senkou_span_b:
        return "red"    # Bearish cloud
    else:
        return "neutral"

def determine_cloud_trend(cloud_color, current_price, senkou_span_a, senkou_span_b):
    """Determine cloud trend based on price position relative to cloud"""
    if senkou_span_a is None or senkou_span_b is None:
        return "neutral"
    
    cloud_top = max(senkou_span_a, senkou_span_b)
    cloud_bottom = min(senkou_span_a, senkou_span_b)
    
    if current_price > cloud_top:
        return "bullish_above_cloud"
    elif current_price < cloud_bottom:
        return "bearish_below_cloud"
    elif cloud_color == "green":
        return "bullish_in_green_cloud"
    elif cloud_color == "red":
        return "bearish_in_red_cloud"
    else:
        return "neutral_in_cloud"

def determine_price_position(current_price, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b):
    """Determine price position relative to Ichimoku components"""
    if tenkan_sen is None or kijun_sen is None:
        return "unknown"
    
    # Check Tenkan-sen vs Kijun-sen
    if current_price > tenkan_sen and tenkan_sen > kijun_sen:
        return "above_tenkan_above_kijun"
    elif current_price > tenkan_sen and tenkan_sen < kijun_sen:
        return "above_tenkan_below_kijun"
    elif current_price < tenkan_sen and tenkan_sen > kijun_sen:
        return "below_tenkan_above_kijun"
    else:
        return "below_tenkan_below_kijun"

def determine_tenkan_kijun_signal(tenkan_sen, kijun_sen, prev_tenkan_sen, prev_kijun_sen):
    """Determine Tenkan-sen vs Kijun-sen signal"""
    if tenkan_sen is None or kijun_sen is None:
        return "neutral"
    
    if prev_tenkan_sen is None or prev_kijun_sen is None:
        return "neutral"
    
    # Check for crossover
    if tenkan_sen > kijun_sen and prev_tenkan_sen <= prev_kijun_sen:
        return "bullish_crossover"
    elif tenkan_sen < kijun_sen and prev_tenkan_sen >= prev_kijun_sen:
        return "bearish_crossover"
    elif tenkan_sen > kijun_sen:
        return "bullish_aligned"
    elif tenkan_sen < kijun_sen:
        return "bearish_aligned"
    else:
        return "neutral"

def calculate_tenkan_kijun_strength(tenkan_sen, kijun_sen):
    """Calculate the strength of Tenkan-sen vs Kijun-sen alignment"""
    if tenkan_sen is None or kijun_sen is None:
        return 0.0
    
    if kijun_sen == 0:
        return 0.0
    
    return abs(tenkan_sen - kijun_sen) / kijun_sen * 100

def find_cloud_support_resistance(senkou_span_a, senkou_span_b, current_price):
    """Find cloud support and resistance levels"""
    if senkou_span_a is None or senkou_span_b is None:
        return None, None, float('inf'), float('inf')
    
    cloud_top = max(senkou_span_a, senkou_span_b)
    cloud_bottom = min(senkou_span_a, senkou_span_b)
    
    # Find nearest support and resistance
    if current_price > cloud_top:
        # Price above cloud - cloud top is support
        support = cloud_top
        resistance = None
        support_distance = current_price - cloud_top
        resistance_distance = float('inf')
    elif current_price < cloud_bottom:
        # Price below cloud - cloud bottom is resistance
        support = None
        resistance = cloud_bottom
        support_distance = float('inf')
        resistance_distance = cloud_bottom - current_price
    else:
        # Price inside cloud
        support = cloud_bottom
        resistance = cloud_top
        support_distance = current_price - cloud_bottom
        resistance_distance = cloud_top - current_price
    
    return support, resistance, support_distance, resistance_distance

def determine_momentum_signal(chikou_span, current_price, period=26):
    """Determine momentum signal based on Chikou Span"""
    if chikou_span is None:
        return "neutral"
    
    # Compare Chikou Span with current price (26 periods ago)
    if chikou_span > current_price:
        return "bullish_momentum"
    elif chikou_span < current_price:
        return "bearish_momentum"
    else:
        return "neutral_momentum"

def calculate_trend_strength(tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, current_price):
    """Calculate overall trend strength"""
    if tenkan_sen is None or kijun_sen is None or senkou_span_a is None or senkou_span_b is None:
        return 0.0
    
    # Calculate alignment score
    alignment_score = 0.0
    
    # Tenkan-sen vs Kijun-sen alignment
    if tenkan_sen > kijun_sen:
        alignment_score += 25
    elif tenkan_sen < kijun_sen:
        alignment_score -= 25
    
    # Price vs Tenkan-sen alignment
    if current_price > tenkan_sen:
        alignment_score += 25
    elif current_price < tenkan_sen:
        alignment_score -= 25
    
    # Price vs Kijun-sen alignment
    if current_price > kijun_sen:
        alignment_score += 25
    elif current_price < kijun_sen:
        alignment_score -= 25
    
    # Cloud alignment
    cloud_top = max(senkou_span_a, senkou_span_b)
    cloud_bottom = min(senkou_span_a, senkou_span_b)
    
    if current_price > cloud_top:
        alignment_score += 25
    elif current_price < cloud_bottom:
        alignment_score -= 25
    
    return alignment_score

def calculate_ichimoku_for_symbol(symbol, symbol_id):
    """Calculate Ichimoku Cloud for all timeframes for a symbol"""
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
                
                # Get appropriate limit for each timeframe (need more data for Ichimoku)
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
                prices = [float(kline[4]) for kline in klines_data]  # Close prices
                
                if len(prices) >= 52:  # Need at least 52 periods for Senkou Span B
                    # Calculate Ichimoku components
                    tenkan_sen = calculate_tenkan_sen(highs, lows, 9)
                    kijun_sen = calculate_kijun_sen(highs, lows, 26)
                    senkou_span_a = calculate_senkou_span_a(tenkan_sen, kijun_sen)
                    senkou_span_b = calculate_senkou_span_b(highs, lows, 52)
                    chikou_span = calculate_chikou_span(prices, 26)
                    
                    if all(x is not None for x in [tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span]):
                        # Determine cloud characteristics
                        cloud_color = determine_cloud_color(senkou_span_a, senkou_span_b)
                        cloud_trend = determine_cloud_trend(cloud_color, current_price, senkou_span_a, senkou_span_b)
                        price_position = determine_price_position(current_price, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b)
                        
                        # Calculate previous values for signal detection
                        if len(prices) >= 53:
                            prev_tenkan_sen = calculate_tenkan_sen(highs[:-1], lows[:-1], 9)
                            prev_kijun_sen = calculate_kijun_sen(highs[:-1], lows[:-1], 26)
                        else:
                            prev_tenkan_sen = prev_kijun_sen = None
                        
                        tenkan_kijun_signal = determine_tenkan_kijun_signal(tenkan_sen, kijun_sen, prev_tenkan_sen, prev_kijun_sen)
                        tenkan_kijun_strength = calculate_tenkan_kijun_strength(tenkan_sen, kijun_sen)
                        
                        # Find cloud support and resistance
                        cloud_support, cloud_resistance, support_distance, resistance_distance = find_cloud_support_resistance(senkou_span_a, senkou_span_b, current_price)
                        
                        # Determine momentum signal
                        momentum_signal = determine_momentum_signal(chikou_span, current_price, 26)
                        
                        # Calculate trend strength
                        trend_strength = calculate_trend_strength(tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, current_price)
                        
                        results[tf] = {
                            "tenkan_sen": tenkan_sen,
                            "kijun_sen": kijun_sen,
                            "senkou_span_a": senkou_span_a,
                            "senkou_span_b": senkou_span_b,
                            "chikou_span": chikou_span,
                            "current_price": current_price,
                            "cloud_color": cloud_color,
                            "cloud_trend": cloud_trend,
                            "price_position": price_position,
                            "tenkan_kijun_signal": tenkan_kijun_signal,
                            "tenkan_kijun_strength": tenkan_kijun_strength,
                            "cloud_support": cloud_support,
                            "cloud_resistance": cloud_resistance,
                            "support_distance": support_distance,
                            "resistance_distance": resistance_distance,
                            "momentum_signal": momentum_signal,
                            "trend_strength": trend_strength
                        }
                    else:
                        print(f"⚠️ Could not calculate all Ichimoku components for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf} (need at least 52 periods)")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Ichimoku for {symbol}: {e}")
        return {}

def store_ichimoku_data(symbol_id, symbol, ichimoku_data):
    """Store Ichimoku data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in ichimoku_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO ichimoku_data 
                (symbol_id, symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b,
                chikou_span, current_price, cloud_color, cloud_trend, price_position,
                tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance,
                support_distance, resistance_distance, momentum_signal, trend_strength, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['tenkan_sen'], data['kijun_sen'],
                data['senkou_span_a'], data['senkou_span_b'], data['chikou_span'],
                data['current_price'], data['cloud_color'], data['cloud_trend'],
                data['price_position'], data['tenkan_kijun_signal'], data['tenkan_kijun_strength'],
                data['cloud_support'], data['cloud_resistance'], data['support_distance'],
                data['resistance_distance'], data['momentum_signal'], data['trend_strength'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Ichimoku data for {symbol}: {e}")
        return False

def generate_ichimoku_report():
    """Generate a comprehensive report of all Ichimoku data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b,
                   chikou_span, current_price, cloud_color, cloud_trend, price_position,
                   tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance,
                   support_distance, resistance_distance, momentum_signal, trend_strength, last_updated
            FROM ichimoku_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Ichimoku data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 ICHIMOKU CLOUD COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine cloud emoji
            cloud_emoji = {
                "green": "🟢",
                "red": "🔴",
                "neutral": "⚪"
            }.get(cloud_color, "⚪")
            
            # Determine signal emoji
            signal_emoji = {
                "bullish_crossover": "🟢",
                "bearish_crossover": "🔴",
                "bullish_aligned": "🟢",
                "bearish_aligned": "🔴",
                "neutral": "⚪"
            }.get(tenkan_kijun_signal, "⚪")
            
            # Determine trend emoji
            trend_emoji = "📈" if trend_strength > 0 else "📉" if trend_strength < 0 else "➡️"
            
            print(f"  {timeframe:>4} | Tenkan: ${tenkan_sen:>10,.2f} | Kijun: ${kijun_sen:>10,.2f} | {cloud_emoji} {cloud_color:>6} | {signal_emoji} {tenkan_kijun_signal:>15} | {trend_emoji} {trend_strength:>5.0f}")
        
        print("\n" + "="*80)
        print("📈 ICHIMOKU SUMMARY:")
        print("="*80)
        
        # Count by cloud color
        green_cloud_count = sum(1 for row in data if row[8] == "green")
        red_cloud_count = sum(1 for row in data if row[8] == "red")
        neutral_cloud_count = sum(1 for row in data if row[8] == "neutral")
        
        # Count by signal
        bullish_crossover_count = sum(1 for row in data if row[11] == "bullish_crossover")
        bearish_crossover_count = sum(1 for row in data if row[11] == "bearish_crossover")
        bullish_aligned_count = sum(1 for row in data if row[11] == "bullish_aligned")
        bearish_aligned_count = sum(1 for row in data if row[11] == "bearish_aligned")
        neutral_signal_count = sum(1 for row in data if row[11] == "neutral")
        
        # Count by trend strength
        strong_bullish_count = sum(1 for row in data if row[18] > 50)
        moderate_bullish_count = sum(1 for row in data if 0 < row[18] <= 50)
        strong_bearish_count = sum(1 for row in data if row[18] < -50)
        moderate_bearish_count = sum(1 for row in data if -50 <= row[18] < 0)
        neutral_trend_count = sum(1 for row in data if row[18] == 0)
        
        print(f"   🟢 Green Clouds: {green_cloud_count}")
        print(f"   🔴 Red Clouds: {red_cloud_count}")
        print(f"   ⚪ Neutral Clouds: {neutral_cloud_count}")
        print(f"   🟢 Bullish Crossovers: {bullish_crossover_count}")
        print(f"   🔴 Bearish Crossovers: {bearish_crossover_count}")
        print(f"   🟢 Bullish Aligned: {bullish_aligned_count}")
        print(f"   🔴 Bearish Aligned: {bearish_aligned_count}")
        print(f"   ⚪ Neutral Signals: {neutral_signal_count}")
        print(f"   📈 Strong Bullish Trends: {strong_bullish_count}")
        print(f"   📈 Moderate Bullish Trends: {moderate_bullish_count}")
        print(f"   📉 Strong Bearish Trends: {strong_bearish_count}")
        print(f"   📉 Moderate Bearish Trends: {moderate_bearish_count}")
        print(f"   ➡️ Neutral Trends: {neutral_trend_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong bullish trends
        strong_bullish = [row for row in data if row[18] > 50]
        if strong_bullish:
            print("   🟢 Strong Bullish Trends (Potential Buy Opportunities):")
            for trend in strong_bullish:
                symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = trend
                print(f"      • {symbol} {timeframe}: Trend strength {trend_strength:.0f} - {tenkan_kijun_signal} - {cloud_trend}")
        else:
            print("   ✅ No strong bullish trends detected")
        
        # Find strong bearish trends
        strong_bearish = [row for row in data if row[18] < -50]
        if strong_bearish:
            print("   🔴 Strong Bearish Trends (Potential Sell Opportunities):")
            for trend in strong_bearish:
                symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = trend
                print(f"      • {symbol} {timeframe}: Trend strength {trend_strength:.0f} - {tenkan_kijun_signal} - {cloud_trend}")
        else:
            print("   ✅ No strong bearish trends detected")
        
        # Find bullish crossovers
        bullish_crossovers = [row for row in data if row[11] == "bullish_crossover"]
        if bullish_crossovers:
            print("   🟢 Bullish Crossovers (Potential Buy Signals):")
            for crossover in bullish_crossovers:
                symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = crossover
                print(f"      • {symbol} {timeframe}: Tenkan-sen crossed above Kijun-sen - {cloud_trend}")
        else:
            print("   ✅ No bullish crossovers detected")
        
        # Find bearish crossovers
        bearish_crossovers = [row for row in data if row[11] == "bearish_crossover"]
        if bearish_crossovers:
            print("   🔴 Bearish Crossovers (Potential Sell Signals):")
            for crossover in bearish_crossovers:
                symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = crossover
                print(f"      • {symbol} {timeframe}: Tenkan-sen crossed below Kijun-sen - {cloud_trend}")
        else:
            print("   ✅ No bearish crossovers detected")
        
        # Find near cloud support
        near_support = [row for row in data if row[15] is not None and row[16] < (row[7] * 0.02)]  # Within 2% of support
        if near_support:
            print("   🛡️ Near Cloud Support (Potential Bounce):")
            for support in near_support:
                symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = support
                distance_pct = (support_distance / current_price) * 100
                print(f"      • {symbol} {timeframe}: {distance_pct:.2f}% from cloud support at ${cloud_support:.2f}")
        else:
            print("   ✅ No near cloud support levels detected")
        
        # Find near cloud resistance
        near_resistance = [row for row in data if row[16] is not None and row[17] < (row[7] * 0.02)]  # Within 2% of resistance
        if near_resistance:
            print("   🚧 Near Cloud Resistance (Potential Rejection):")
            for resistance in near_resistance:
                symbol, timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength, last_updated = resistance
                distance_pct = (resistance_distance / current_price) * 100
                print(f"      • {symbol} {timeframe}: {distance_pct:.2f}% from cloud resistance at ${cloud_resistance:.2f}")
        else:
            print("   ✅ No near cloud resistance levels detected")
        
        print("\n" + "="*80)
        print("✅ Ichimoku report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Ichimoku report: {e}")

def main():
    """Main function to populate Ichimoku data"""
    print("🚀 Starting Ichimoku data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Ichimoku for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        ichimoku_data = calculate_ichimoku_for_symbol(symbol, symbol_id)
        if ichimoku_data:
            if store_ichimoku_data(symbol_id, symbol, ichimoku_data):
                print(f"✅ Stored {len(ichimoku_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Ichimoku data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_ichimoku_report()

if __name__ == "__main__":
    main()
