#!/usr/bin/env python3
"""
Populate ATR Data
Calculates and stores ATR (Average True Range) indicators for all symbols in My Symbols list
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

def calculate_true_range(high, low, prev_close):
    """Calculate True Range for a single period"""
    high_low = high - low
    high_close = abs(high - prev_close)
    low_close = abs(low - prev_close)
    
    return max(high_low, high_close, low_close)

def calculate_atr(highs, lows, closes, period=14):
    """Calculate ATR (Average True Range)"""
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None, None, None, None, None
    
    # Calculate True Range for each period
    true_ranges = []
    high_low_ranges = []
    high_close_ranges = []
    low_close_ranges = []
    
    for i in range(1, len(highs)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i-1]
        
        tr = calculate_true_range(high, low, prev_close)
        true_ranges.append(tr)
        high_low_ranges.append(high - low)
        high_close_ranges.append(abs(high - prev_close))
        low_close_ranges.append(abs(low - prev_close))
    
    if len(true_ranges) < period:
        return None, None, None, None, None
    
    # Calculate ATR using exponential moving average
    atr = np.mean(true_ranges[:period])
    
    # Apply exponential smoothing for remaining periods
    for i in range(period, len(true_ranges)):
        atr = (atr * (period - 1) + true_ranges[i]) / period
    
    # Get current values
    current_tr = true_ranges[-1]
    current_high_low = high_low_ranges[-1]
    current_high_close = high_close_ranges[-1]
    current_low_close = low_close_ranges[-1]
    
    return atr, current_tr, current_high_low, current_high_close, current_low_close

def calculate_atr_percentage(atr_value, current_price):
    """Calculate ATR as a percentage of current price"""
    if current_price == 0:
        return 0.0
    return (atr_value / current_price) * 100

def determine_volatility_level(atr_percentage):
    """Determine volatility level based on ATR percentage"""
    if atr_percentage >= 5.0:
        return "extreme_high"
    elif atr_percentage >= 3.0:
        return "high"
    elif atr_percentage >= 1.5:
        return "moderate"
    elif atr_percentage >= 0.5:
        return "low"
    else:
        return "very_low"

def calculate_volatility_strength(atr_percentage, volatility_level):
    """Calculate volatility strength based on ATR percentage"""
    if volatility_level == "extreme_high":
        # Strength based on how far above 5%
        strength = min((atr_percentage - 5.0) / 5.0 * 100, 100)
        return max(strength, 0)
    elif volatility_level == "high":
        # Strength based on how far above 3%
        strength = min((atr_percentage - 3.0) / 2.0 * 100, 100)
        return max(strength, 0)
    elif volatility_level == "moderate":
        # Strength based on how far above 1.5%
        strength = min((atr_percentage - 1.5) / 1.5 * 100, 100)
        return max(strength, 0)
    elif volatility_level == "low":
        # Strength based on how far above 0.5%
        strength = min((atr_percentage - 0.5) / 1.0 * 100, 100)
        return max(strength, 0)
    else:
        return 0.0

def determine_volatility_trend(atr_values, period=5):
    """Determine volatility trend based on ATR values"""
    if len(atr_values) < period:
        return "neutral", 0.0
    
    recent_atr = atr_values[-period:]
    
    # Calculate trend
    trend_change = recent_atr[-1] - recent_atr[0]
    trend_strength = abs(trend_change) / np.mean(recent_atr) * 100  # Normalize to percentage
    
    if trend_change > 0:
        return "increasing", trend_strength
    elif trend_change < 0:
        return "decreasing", trend_strength
    else:
        return "neutral", 0.0

def detect_breakout_potential(atr_value, atr_percentage, volatility_level):
    """Detect potential breakout based on ATR"""
    if volatility_level in ["high", "extreme_high"] and atr_percentage > 2.0:
        # High volatility suggests potential breakout
        if atr_percentage > 4.0:
            return "high", min((atr_percentage - 4.0) / 2.0 * 100, 100)
        else:
            return "moderate", min((atr_percentage - 2.0) / 2.0 * 100, 100)
    elif volatility_level == "very_low" and atr_percentage < 0.3:
        # Very low volatility suggests potential breakout from consolidation
        return "consolidation", min((0.3 - atr_percentage) / 0.3 * 100, 100)
    else:
        return "none", 0.0

def calculate_atr_for_symbol(symbol, symbol_id):
    """Calculate ATR for all timeframes for a symbol"""
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
                
                if len(closes) >= 20:  # Need enough data for ATR
                    # Calculate ATR values for the entire period
                    atr_values = []
                    for i in range(14, len(closes)):
                        atr, tr, hl, hc, lc = calculate_atr(highs[:i+1], lows[:i+1], closes[:i+1], 14)
                        if atr is not None:
                            atr_values.append(atr)
                    
                    if len(atr_values) >= 10:  # Need enough ATR values
                        # Calculate current ATR
                        current_atr, current_tr, current_hl, current_hc, current_lc = calculate_atr(highs, lows, closes, 14)
                        
                        if current_atr is not None:
                            # Calculate ATR percentage
                            atr_percentage = calculate_atr_percentage(current_atr, current_price)
                            
                            # Determine volatility level
                            volatility_level = determine_volatility_level(atr_percentage)
                            
                            # Calculate volatility strength
                            volatility_strength = calculate_volatility_strength(atr_percentage, volatility_level)
                            
                            # Determine volatility trend
                            volatility_trend, volatility_change = determine_volatility_trend(atr_values)
                            
                            # Detect breakout potential
                            breakout_potential, breakout_strength = detect_breakout_potential(current_atr, atr_percentage, volatility_level)
                            
                            results[tf] = {
                                "atr_value": current_atr,
                                "atr_percentage": atr_percentage,
                                "volatility_level": volatility_level,
                                "volatility_strength": volatility_strength,
                                "true_range": current_tr,
                                "high_low_range": current_hl,
                                "high_close_range": current_hc,
                                "low_close_range": current_lc,
                                "volatility_trend": volatility_trend,
                                "volatility_change": volatility_change,
                                "breakout_potential": breakout_potential,
                                "breakout_strength": breakout_strength,
                                "current_price": current_price
                            }
                        else:
                            print(f"⚠️ Could not calculate ATR for {symbol} {tf}")
                    else:
                        print(f"⚠️ Insufficient ATR data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating ATR for {symbol}: {e}")
        return {}

def store_atr_data(symbol_id, symbol, atr_data):
    """Store ATR data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in atr_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO atr_data 
                (symbol_id, symbol, timeframe, atr_value, atr_percentage, volatility_level,
                volatility_strength, true_range, high_low_range, high_close_range, low_close_range,
                volatility_trend, volatility_change, breakout_potential, breakout_strength,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['atr_value'], data['atr_percentage'],
                data['volatility_level'], data['volatility_strength'], data['true_range'],
                data['high_low_range'], data['high_close_range'], data['low_close_range'],
                data['volatility_trend'], data['volatility_change'], data['breakout_potential'],
                data['breakout_strength'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing ATR data for {symbol}: {e}")
        return False

def generate_atr_report():
    """Generate a comprehensive report of all ATR data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, atr_value, atr_percentage, volatility_level,
                   volatility_strength, volatility_trend, volatility_change,
                   breakout_potential, breakout_strength, current_price, last_updated
            FROM atr_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No ATR data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 ATR (AVERAGE TRUE RANGE) COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine volatility emoji
            volatility_emoji = {
                "extreme_high": "💥",
                "high": "🔥",
                "moderate": "⚡",
                "low": "🌊",
                "very_low": "💧"
            }.get(volatility_level, "⚪")
            
            # Determine trend emoji
            trend_emoji = {
                "increasing": "📈",
                "decreasing": "📉",
                "neutral": "➡️"
            }.get(volatility_trend, "➡️")
            
            # Determine breakout emoji
            breakout_emoji = {
                "high": "🚀",
                "moderate": "📊",
                "consolidation": "🎯",
                "none": "⚪"
            }.get(breakout_potential, "⚪")
            
            print(f"  {timeframe:>4} | ATR: {atr_value:>8.4f} | %: {atr_percentage:>5.2f}% | {volatility_emoji} {volatility_level:>12} | {trend_emoji} {volatility_trend:>10} | {breakout_emoji} {breakout_potential:>12}")
        
        print("\n" + "="*80)
        print("📈 ATR SUMMARY:")
        print("="*80)
        
        # Count by volatility level
        extreme_high_count = sum(1 for row in data if row[4] == "extreme_high")
        high_count = sum(1 for row in data if row[4] == "high")
        moderate_count = sum(1 for row in data if row[4] == "moderate")
        low_count = sum(1 for row in data if row[4] == "low")
        very_low_count = sum(1 for row in data if row[4] == "very_low")
        
        # Count by volatility trend
        increasing_volatility_count = sum(1 for row in data if row[6] == "increasing")
        decreasing_volatility_count = sum(1 for row in data if row[6] == "decreasing")
        neutral_volatility_count = sum(1 for row in data if row[6] == "neutral")
        
        # Count by breakout potential
        high_breakout_count = sum(1 for row in data if row[8] == "high")
        moderate_breakout_count = sum(1 for row in data if row[8] == "moderate")
        consolidation_breakout_count = sum(1 for row in data if row[8] == "consolidation")
        no_breakout_count = sum(1 for row in data if row[8] == "none")
        
        # Count strong volatility
        strong_volatility = sum(1 for row in data if row[5] > 50)
        moderate_volatility = sum(1 for row in data if 20 < row[5] <= 50)
        weak_volatility = sum(1 for row in data if row[5] <= 20)
        
        print(f"   💥 Extreme High Volatility: {extreme_high_count}")
        print(f"   🔥 High Volatility: {high_count}")
        print(f"   ⚡ Moderate Volatility: {moderate_count}")
        print(f"   🌊 Low Volatility: {low_count}")
        print(f"   💧 Very Low Volatility: {very_low_count}")
        print(f"   📈 Increasing Volatility: {increasing_volatility_count}")
        print(f"   📉 Decreasing Volatility: {decreasing_volatility_count}")
        print(f"   ➡️ Neutral Volatility: {neutral_volatility_count}")
        print(f"   🚀 High Breakout Potential: {high_breakout_count}")
        print(f"   📊 Moderate Breakout Potential: {moderate_breakout_count}")
        print(f"   🎯 Consolidation Breakout: {consolidation_breakout_count}")
        print(f"   ⚪ No Breakout Potential: {no_breakout_count}")
        print(f"   💪 Strong Volatility (>50%): {strong_volatility}")
        print(f"   📊 Moderate Volatility (20-50%): {moderate_volatility}")
        print(f"   🔸 Weak Volatility (<20%): {weak_volatility}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find high volatility conditions
        high_volatility_signals = [row for row in data if row[4] in ["high", "extreme_high"] and row[5] > 30]
        if high_volatility_signals:
            print("   🔥 High Volatility Conditions (Potential Breakout Opportunities):")
            for signal in high_volatility_signals:
                symbol, timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Volatility strength {volatility_strength:.1f}% - ATR: {atr_value:.4f} ({atr_percentage:.2f}%)")
        else:
            print("   ✅ No high volatility conditions detected")
        
        # Find very low volatility conditions
        low_volatility_signals = [row for row in data if row[4] == "very_low" and row[5] > 30]
        if low_volatility_signals:
            print("   💧 Very Low Volatility Conditions (Potential Consolidation Breakout):")
            for signal in low_volatility_signals:
                symbol, timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Volatility strength {volatility_strength:.1f}% - ATR: {atr_value:.4f} ({atr_percentage:.2f}%)")
        else:
            print("   ✅ No very low volatility conditions detected")
        
        # Find increasing volatility trends
        increasing_volatility = [row for row in data if row[6] == "increasing" and row[7] > 10]
        if increasing_volatility:
            print("   📈 Increasing Volatility Trends (Potential Momentum Building):")
            for trend in increasing_volatility:
                symbol, timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: Volatility change {volatility_change:.1f}% - ATR: {atr_value:.4f}")
        else:
            print("   ✅ No significant increasing volatility trends detected")
        
        # Find high breakout potential
        high_breakout = [row for row in data if row[8] == "high" and row[9] > 30]
        if high_breakout:
            print("   🚀 High Breakout Potential (Strong Volatility Signals):")
            for breakout in high_breakout:
                symbol, timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: Breakout strength {breakout_strength:.1f}% - ATR: {atr_value:.4f} ({atr_percentage:.2f}%)")
        else:
            print("   ✅ No high breakout potential detected")
        
        # Find consolidation breakout potential
        consolidation_breakout = [row for row in data if row[8] == "consolidation" and row[9] > 30]
        if consolidation_breakout:
            print("   🎯 Consolidation Breakout Potential (Low Volatility Reversal):")
            for breakout in consolidation_breakout:
                symbol, timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: Breakout strength {breakout_strength:.1f}% - ATR: {atr_value:.4f} ({atr_percentage:.2f}%)")
        else:
            print("   ✅ No consolidation breakout potential detected")
        
        print("\n" + "="*80)
        print("✅ ATR report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating ATR report: {e}")

def main():
    """Main function to populate ATR data"""
    print("🚀 Starting ATR data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store ATR for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        atr_data = calculate_atr_for_symbol(symbol, symbol_id)
        if atr_data:
            if store_atr_data(symbol_id, symbol, atr_data):
                print(f"✅ Stored {len(atr_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No ATR data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_atr_report()

if __name__ == "__main__":
    main()
