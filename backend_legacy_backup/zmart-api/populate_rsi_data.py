#!/usr/bin/env python3
"""
Populate RSI Data
Calculates and stores RSI data for all symbols in My Symbols list
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

def calculate_rsi_for_symbol(symbol, symbol_id):
    """Calculate RSI for all timeframes for a symbol"""
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
                
                if len(prices) >= 15:  # Need at least 15 periods for RSI
                    rsi_values = ta_service.calculate_rsi(prices, 14)
                    if rsi_values:
                        rsi_value = rsi_values[-1]
                        
                        # Determine signal status
                        if rsi_value >= 70:
                            signal_status = "Overbought"
                        elif rsi_value <= 30:
                            signal_status = "Oversold"
                        else:
                            signal_status = "Neutral"
                        
                        # Calculate divergence strength (simplified)
                        divergence_strength = 0.0
                        divergence_type = "none"
                        
                        # Check for potential divergences
                        if len(rsi_values) >= 10:
                            recent_rsi = rsi_values[-5:]
                            recent_prices = prices[-5:]
                            
                            # Simple divergence detection
                            rsi_trend = "up" if recent_rsi[-1] > recent_rsi[0] else "down"
                            price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
                            
                            if rsi_trend != price_trend:
                                if rsi_trend == "down" and price_trend == "up":
                                    divergence_type = "bearish"
                                    divergence_strength = abs(recent_rsi[-1] - recent_rsi[0]) / 100.0
                                elif rsi_trend == "up" and price_trend == "down":
                                    divergence_type = "bullish"
                                    divergence_strength = abs(recent_rsi[-1] - recent_rsi[0]) / 100.0
                        
                        results[tf] = {
                            "rsi_value": rsi_value,
                            "signal_status": signal_status,
                            "divergence_type": divergence_type,
                            "divergence_strength": divergence_strength,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate RSI for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating RSI for {symbol}: {e}")
        return {}

def store_rsi_data(symbol_id, symbol, rsi_data):
    """Store RSI data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in rsi_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO rsi_data 
                (symbol_id, symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['rsi_value'], data['signal_status'], 
                data['divergence_type'], data['divergence_strength'], data['current_price'], 
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing RSI data for {symbol}: {e}")
        return False

def generate_rsi_report():
    """Generate a comprehensive report of all RSI data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated
            FROM rsi_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No RSI data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 RSI COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine status emoji
            status_emoji = {
                "Overbought": "🔴",
                "Oversold": "🟢", 
                "Neutral": "⚪"
            }.get(signal_status, "⚪")
            
            # Determine divergence emoji
            divergence_emoji = {
                "bullish": "🟢↗️",
                "bearish": "🔴↘️",
                "none": ""
            }.get(divergence_type, "")
            
            print(f"  {timeframe:>4} | RSI: {rsi_value:>6.2f} | {status_emoji} {signal_status:>10} | {divergence_emoji} {divergence_type:>10} | Strength: {divergence_strength:>5.2f}")
        
        print("\n" + "="*80)
        print("📈 SIGNAL SUMMARY:")
        print("="*80)
        
        # Count signals by status
        overbought_count = sum(1 for row in data if row[3] == "Overbought")
        oversold_count = sum(1 for row in data if row[3] == "Oversold")
        neutral_count = sum(1 for row in data if row[3] == "Neutral")
        bullish_divergence_count = sum(1 for row in data if row[4] == "bullish")
        bearish_divergence_count = sum(1 for row in data if row[4] == "bearish")
        
        print(f"   🔴 Overbought: {overbought_count}")
        print(f"   🟢 Oversold: {oversold_count}")
        print(f"   ⚪ Neutral: {neutral_count}")
        print(f"   🟢↗️ Bullish Divergences: {bullish_divergence_count}")
        print(f"   🔴↘️ Bearish Divergences: {bearish_divergence_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find oversold opportunities (potential buy signals)
        oversold_signals = [row for row in data if row[3] == "Oversold"]
        if oversold_signals:
            print("   🟢 Oversold (Buy Opportunities):")
            for signal in oversold_signals:
                symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated = signal
                divergence_info = f" + {divergence_type} divergence" if divergence_type != "none" else ""
                print(f"      • {symbol} {timeframe}: RSI {rsi_value:.2f}{divergence_info}")
        else:
            print("   ✅ No oversold conditions detected")
        
        # Find overbought opportunities (potential sell signals)
        overbought_signals = [row for row in data if row[3] == "Overbought"]
        if overbought_signals:
            print("   🔴 Overbought (Sell Opportunities):")
            for signal in overbought_signals:
                symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated = signal
                divergence_info = f" + {divergence_type} divergence" if divergence_type != "none" else ""
                print(f"      • {symbol} {timeframe}: RSI {rsi_value:.2f}{divergence_info}")
        else:
            print("   ✅ No overbought conditions detected")
        
        # Find divergence opportunities
        divergence_signals = [row for row in data if row[4] != "none"]
        if divergence_signals:
            print("   ⚡ Divergence Signals:")
            for signal in divergence_signals:
                symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated = signal
                emoji = "🟢" if divergence_type == "bullish" else "🔴"
                print(f"      • {emoji} {symbol} {timeframe}: {divergence_type} divergence (strength: {divergence_strength:.2f})")
        else:
            print("   ✅ No divergence signals detected")
        
        print("\n" + "="*80)
        print("✅ RSI report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating RSI report: {e}")

def main():
    """Main function to populate RSI data"""
    print("🚀 Starting RSI data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store RSI for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        rsi_data = calculate_rsi_for_symbol(symbol, symbol_id)
        if rsi_data:
            if store_rsi_data(symbol_id, symbol, rsi_data):
                print(f"✅ Stored {len(rsi_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No RSI data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_rsi_report()

if __name__ == "__main__":
    main()
