#!/usr/bin/env python3
"""
Populate Bollinger Bands Data
Calculates and stores Bollinger Bands data for all symbols in My Symbols list
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

def calculate_bollinger_bands_for_symbol(symbol, symbol_id):
    """Calculate Bollinger Bands for all timeframes for a symbol"""
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
                
                if len(prices) >= 20:
                    sma, upper_band, lower_band = ta_service.calculate_bollinger_bands(prices)
                    if sma and upper_band and lower_band:
                        bandwidth = ((upper_band[-1] - lower_band[-1]) / sma[-1] * 100)
                        position = ((current_price - lower_band[-1]) / (upper_band[-1] - lower_band[-1]) * 100)
                        
                        results[tf] = {
                            "sma": sma[-1],
                            "upper_band": upper_band[-1],
                            "lower_band": lower_band[-1],
                            "bandwidth": bandwidth,
                            "position": position,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate Bollinger Bands for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Bollinger Bands for {symbol}: {e}")
        return {}

def store_bollinger_bands_data(symbol_id, symbol, bollinger_data):
    """Store Bollinger Bands data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in bollinger_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO bollinger_bands 
                (symbol_id, symbol, timeframe, sma, upper_band, lower_band, bandwidth, position, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['sma'], data['upper_band'], 
                data['lower_band'], data['bandwidth'], data['position'], 
                data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Bollinger Bands data for {symbol}: {e}")
        return False

def generate_bollinger_bands_report():
    """Generate a comprehensive report of all Bollinger Bands data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, sma, upper_band, lower_band, bandwidth, position, current_price, last_updated
            FROM bollinger_bands
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Bollinger Bands data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 BOLLINGER BANDS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, sma, upper_band, lower_band, bandwidth, position, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine position status
            if position <= 20:
                position_status = "🟢 Near Lower Band (Support)"
                position_color = "GREEN"
            elif position >= 80:
                position_status = "🔴 Near Upper Band (Resistance)"
                position_color = "RED"
            else:
                position_status = "⚪ Middle Range"
                position_color = "WHITE"
            
            # Determine bandwidth status
            if bandwidth > 5:
                bandwidth_status = "🟠 High Volatility"
            elif bandwidth < 1:
                bandwidth_status = "🔵 Low Volatility"
            else:
                bandwidth_status = "⚪ Normal Volatility"
            
            print(f"  {timeframe:>4} | SMA: ${sma:>10,.2f} | Upper: ${upper_band:>10,.2f} | Lower: ${lower_band:>10,.2f}")
            print(f"       | Position: {position:>6.1f}% ({position_status})")
            print(f"       | Bandwidth: {bandwidth:>6.2f}% ({bandwidth_status})")
            print(f"       | Updated: {last_updated}")
        
        print("\n" + "="*80)
        print("📈 TRADING INSIGHTS:")
        print("="*80)
        
        # Group by symbol for insights
        symbols_data = {}
        for row in data:
            symbol, timeframe, sma, upper_band, lower_band, bandwidth, position, current_price, last_updated = row
            if symbol not in symbols_data:
                symbols_data[symbol] = []
            symbols_data[symbol].append({
                'timeframe': timeframe,
                'position': position,
                'bandwidth': bandwidth,
                'current_price': current_price
            })
        
        for symbol, timeframes in symbols_data.items():
            print(f"\n🔸 {symbol} Analysis:")
            
            # Find most volatile timeframe
            most_volatile = max(timeframes, key=lambda x: x['bandwidth'])
            least_volatile = min(timeframes, key=lambda x: x['bandwidth'])
            
            print(f"   📊 Most Volatile: {most_volatile['timeframe']} ({most_volatile['bandwidth']:.2f}%)")
            print(f"   📊 Least Volatile: {least_volatile['timeframe']} ({least_volatile['bandwidth']:.2f}%)")
            
            # Check for potential breakout signals
            breakout_signals = []
            for tf in timeframes:
                if tf['position'] <= 15:
                    breakout_signals.append(f"{tf['timeframe']} - Near Support (Buy Signal)")
                elif tf['position'] >= 85:
                    breakout_signals.append(f"{tf['timeframe']} - Near Resistance (Sell Signal)")
            
            if breakout_signals:
                print(f"   🚨 Potential Breakout Signals:")
                for signal in breakout_signals:
                    print(f"      • {signal}")
            else:
                print(f"   ✅ No immediate breakout signals")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def main():
    """Main function to populate Bollinger Bands data"""
    print("🚀 Starting Bollinger Bands data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Bollinger Bands for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        bollinger_data = calculate_bollinger_bands_for_symbol(symbol, symbol_id)
        if bollinger_data:
            if store_bollinger_bands_data(symbol_id, symbol, bollinger_data):
                print(f"✅ Stored {len(bollinger_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Bollinger Bands data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_bollinger_bands_report()

if __name__ == "__main__":
    main()
