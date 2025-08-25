#!/usr/bin/env python3
"""
Populate MACD Data
Calculates and stores MACD data for all symbols in My Symbols list
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

def calculate_macd_for_symbol(symbol, symbol_id):
    """Calculate MACD for all timeframes for a symbol"""
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
                
                if len(prices) >= 26:
                    macd_line, signal_line, histogram = ta_service.calculate_macd(prices)
                    if macd_line and signal_line and histogram:
                        # Get latest values
                        macd_value = macd_line[-1]
                        signal_value = signal_line[-1]
                        hist_value = histogram[-1]
                        
                        # Determine signal status
                        if len(macd_line) >= 2 and len(signal_line) >= 2:
                            prev_macd = macd_line[-2]
                            prev_signal = signal_line[-2]
                            
                            if prev_macd <= prev_signal and macd_value > signal_value:
                                signal_status = "Bullish Crossover"
                            elif prev_macd >= prev_signal and macd_value < signal_value:
                                signal_status = "Bearish Crossover"
                            elif macd_value > signal_value:
                                signal_status = "Bullish"
                            else:
                                signal_status = "Bearish"
                        else:
                            signal_status = "Neutral"
                        
                        results[tf] = {
                            "macd_line": macd_value,
                            "signal_line": signal_value,
                            "histogram": hist_value,
                            "signal_status": signal_status,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate MACD for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating MACD for {symbol}: {e}")
        return {}

def store_macd_data(symbol_id, symbol, macd_data):
    """Store MACD data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in macd_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO macd_data 
                (symbol_id, symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['macd_line'], data['signal_line'], 
                data['histogram'], data['signal_status'], data['current_price'], 
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing MACD data for {symbol}: {e}")
        return False

def generate_macd_report():
    """Generate a comprehensive report of all MACD data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated
            FROM macd_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No MACD data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 MACD COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine status emoji
            status_emoji = {
                "Bullish": "🟢",
                "Bearish": "🔴", 
                "Bullish Crossover": "🟢⚡",
                "Bearish Crossover": "🔴⚡",
                "Neutral": "⚪"
            }.get(signal_status, "⚪")
            
            print(f"  {timeframe:>4} | MACD: {macd_line:>10.4f} | Signal: {signal_line:>10.4f} | Histogram: {histogram:>10.4f} | {status_emoji} {signal_status}")
        
        print("\n" + "="*80)
        print("📈 SIGNAL SUMMARY:")
        print("="*80)
        
        # Count signals by status
        bullish_count = sum(1 for row in data if "Bullish" in row[5] and "Crossover" not in row[5])
        bearish_count = sum(1 for row in data if "Bearish" in row[5] and "Crossover" not in row[5])
        bullish_cross_count = sum(1 for row in data if "Bullish Crossover" in row[5])
        bearish_cross_count = sum(1 for row in data if "Bearish Crossover" in row[5])
        neutral_count = sum(1 for row in data if "Neutral" in row[5])
        
        print(f"   🟢 Bullish: {bullish_count}")
        print(f"   🔴 Bearish: {bearish_count}")
        print(f"   🟢⚡ Bullish Crossovers: {bullish_cross_count}")
        print(f"   🔴⚡ Bearish Crossovers: {bearish_cross_count}")
        print(f"   ⚪ Neutral: {neutral_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find crossover opportunities
        crossovers = [row for row in data if "Crossover" in row[5]]
        if crossovers:
            print("   ⚡ Recent Crossovers:")
            for crossover in crossovers:
                symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated = crossover
                emoji = "🟢" if "Bullish" in signal_status else "🔴"
                print(f"      • {emoji} {symbol} {timeframe}: {signal_status}")
        else:
            print("   ✅ No recent crossovers detected")
        
        # Find strong signals
        strong_bullish = [row for row in data if row[5] == "Bullish" and row[4] > 0 and row[4] > abs(row[2]) * 0.1]
        strong_bearish = [row for row in data if row[5] == "Bearish" and row[4] < 0 and abs(row[4]) > abs(row[2]) * 0.1]
        
        if strong_bullish:
            print(f"\n   🟢 Strong Bullish Signals:")
            for signal in strong_bullish:
                symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Histogram {histogram:.4f}")
        
        if strong_bearish:
            print(f"\n   🔴 Strong Bearish Signals:")
            for signal in strong_bearish:
                symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Histogram {histogram:.4f}")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✅ MACD report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating MACD report: {e}")

def main():
    """Main function to populate MACD data"""
    print("🚀 Starting MACD data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store MACD for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        macd_data = calculate_macd_for_symbol(symbol, symbol_id)
        if macd_data:
            if store_macd_data(symbol_id, symbol, macd_data):
                print(f"✅ Stored {len(macd_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No MACD data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_macd_report()

if __name__ == "__main__":
    main()
