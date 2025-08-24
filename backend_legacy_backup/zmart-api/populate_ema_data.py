#!/usr/bin/env python3
"""
Populate EMA Data
Calculates and stores EMA crossovers for all symbols in My Symbols list
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

def calculate_ema_for_symbol(symbol, symbol_id):
    """Calculate EMA crossovers for all timeframes for a symbol"""
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
                
                # Extract closing prices
                prices = [float(kline[4]) for kline in klines_data]
                
                if len(prices) >= 50:  # Need at least 50 periods for all EMAs
                    # Calculate all EMAs
                    ema_9 = ta_service.calculate_ema(prices, 9)
                    ema_12 = ta_service.calculate_ema(prices, 12)
                    ema_20 = ta_service.calculate_ema(prices, 20)
                    ema_21 = ta_service.calculate_ema(prices, 21)
                    ema_26 = ta_service.calculate_ema(prices, 26)
                    ema_50 = ta_service.calculate_ema(prices, 50)
                    
                    if all([ema_9, ema_12, ema_20, ema_21, ema_26, ema_50]):
                        # Get latest values
                        ema_9_val = ema_9[-1]
                        ema_12_val = ema_12[-1]
                        ema_20_val = ema_20[-1]
                        ema_21_val = ema_21[-1]
                        ema_26_val = ema_26[-1]
                        ema_50_val = ema_50[-1]
                        
                        # Detect crossovers
                        golden_cross_detected = False
                        death_cross_detected = False
                        cross_signal = "none"
                        cross_strength = 0.0
                        
                        # Check for Golden Cross (EMA12 > EMA26)
                        if ema_12_val > ema_26_val:
                            if len(ema_12) >= 2 and len(ema_26) >= 2:
                                if ema_12[-2] <= ema_26[-2]:  # Previous period was below
                                    golden_cross_detected = True
                                    cross_signal = "golden_cross"
                                    cross_strength = abs(ema_12_val - ema_26_val) / ema_26_val
                        
                        # Check for Death Cross (EMA12 < EMA26)
                        elif ema_12_val < ema_26_val:
                            if len(ema_12) >= 2 and len(ema_26) >= 2:
                                if ema_12[-2] >= ema_26[-2]:  # Previous period was above
                                    death_cross_detected = True
                                    cross_signal = "death_cross"
                                    cross_strength = abs(ema_12_val - ema_26_val) / ema_26_val
                        
                        # Determine trends
                        short_term_trend = "neutral"
                        if ema_9_val > ema_20_val:
                            short_term_trend = "bullish"
                        elif ema_9_val < ema_20_val:
                            short_term_trend = "bearish"
                        
                        long_term_trend = "neutral"
                        if ema_20_val > ema_50_val:
                            long_term_trend = "bullish"
                        elif ema_20_val < ema_50_val:
                            long_term_trend = "bearish"
                        
                        results[tf] = {
                            "ema_9": ema_9_val,
                            "ema_12": ema_12_val,
                            "ema_20": ema_20_val,
                            "ema_21": ema_21_val,
                            "ema_26": ema_26_val,
                            "ema_50": ema_50_val,
                            "cross_signal": cross_signal,
                            "cross_strength": cross_strength,
                            "golden_cross_detected": golden_cross_detected,
                            "death_cross_detected": death_cross_detected,
                            "short_term_trend": short_term_trend,
                            "long_term_trend": long_term_trend,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate all EMAs for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating EMA for {symbol}: {e}")
        return {}

def store_ema_data(symbol_id, symbol, ema_data):
    """Store EMA data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in ema_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO ema_data 
                (symbol_id, symbol, timeframe, ema_9, ema_12, ema_20, ema_21, ema_26, ema_50, 
                cross_signal, cross_strength, golden_cross_detected, death_cross_detected, 
                short_term_trend, long_term_trend, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['ema_9'], data['ema_12'], data['ema_20'], 
                data['ema_21'], data['ema_26'], data['ema_50'], data['cross_signal'], 
                data['cross_strength'], data['golden_cross_detected'], data['death_cross_detected'],
                data['short_term_trend'], data['long_term_trend'], data['current_price'], 
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing EMA data for {symbol}: {e}")
        return False

def generate_ema_report():
    """Generate a comprehensive report of all EMA data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, ema_12, ema_26, cross_signal, cross_strength, 
                   golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend, 
                   current_price, last_updated
            FROM ema_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No EMA data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 EMA CROSSOVERS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, ema_12, ema_26, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine signal emoji
            signal_emoji = {
                "golden_cross": "🟢⚡",
                "death_cross": "🔴⚡",
                "none": "⚪"
            }.get(cross_signal, "⚪")
            
            # Determine trend emojis
            short_trend_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(short_term_trend, "⚪")
            long_trend_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(long_term_trend, "⚪")
            
            print(f"  {timeframe:>4} | EMA12: ${ema_12:>10,.2f} | EMA26: ${ema_26:>10,.2f} | {signal_emoji} {cross_signal:>12} | {short_trend_emoji} {short_term_trend:>8} | {long_trend_emoji} {long_term_trend:>8}")
        
        print("\n" + "="*80)
        print("📈 SIGNAL SUMMARY:")
        print("="*80)
        
        # Count signals by type
        golden_cross_count = sum(1 for row in data if row[6] == 1)
        death_cross_count = sum(1 for row in data if row[7] == 1)
        no_cross_count = sum(1 for row in data if row[4] == "none")
        
        print(f"   🟢⚡ Golden Crosses: {golden_cross_count}")
        print(f"   🔴⚡ Death Crosses: {death_cross_count}")
        print(f"   ⚪ No Crosses: {no_cross_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find golden cross opportunities
        golden_crosses = [row for row in data if row[6] == 1]
        if golden_crosses:
            print("   🟢⚡ Golden Cross Signals (Buy Opportunities):")
            for cross in golden_crosses:
                symbol, timeframe, ema_12, ema_26, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend, current_price, last_updated = cross
                print(f"      • {symbol} {timeframe}: EMA12 ${ema_12:.2f} > EMA26 ${ema_26:.2f} (strength: {cross_strength:.4f})")
        else:
            print("   ✅ No golden crosses detected")
        
        # Find death cross opportunities
        death_crosses = [row for row in data if row[7] == 1]
        if death_crosses:
            print("   🔴⚡ Death Cross Signals (Sell Opportunities):")
            for cross in death_crosses:
                symbol, timeframe, ema_12, ema_26, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend, current_price, last_updated = cross
                print(f"      • {symbol} {timeframe}: EMA12 ${ema_12:.2f} < EMA26 ${ema_26:.2f} (strength: {cross_strength:.4f})")
        else:
            print("   ✅ No death crosses detected")
        
        # Find strong trend alignments
        strong_bullish = [row for row in data if row[8] == "bullish" and row[9] == "bullish"]
        strong_bearish = [row for row in data if row[8] == "bearish" and row[9] == "bearish"]
        
        if strong_bullish:
            print("   🟢 Strong Bullish Trends (Short + Long term aligned):")
            for trend in strong_bullish:
                symbol, timeframe, ema_12, ema_26, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: Both short and long term bullish")
        
        if strong_bearish:
            print("   🔴 Strong Bearish Trends (Short + Long term aligned):")
            for trend in strong_bearish:
                symbol, timeframe, ema_12, ema_26, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: Both short and long term bearish")
        
        print("\n" + "="*80)
        print("✅ EMA report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating EMA report: {e}")

def main():
    """Main function to populate EMA data"""
    print("🚀 Starting EMA data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store EMA for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        ema_data = calculate_ema_for_symbol(symbol, symbol_id)
        if ema_data:
            if store_ema_data(symbol_id, symbol, ema_data):
                print(f"✅ Stored {len(ema_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No EMA data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_ema_report()

if __name__ == "__main__":
    main()
