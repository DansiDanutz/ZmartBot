#!/usr/bin/env python3
"""
Populate CCI Data
Calculates and stores CCI (Commodity Channel Index) indicators for all symbols in My Symbols list
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

def calculate_cci(highs, lows, closes, period=20):
    """Calculate CCI (Commodity Channel Index)"""
    if len(highs) < period or len(lows) < period or len(closes) < period:
        return None
    
    # Calculate Typical Price
    typical_prices = []
    for i in range(len(closes)):
        tp = (highs[i] + lows[i] + closes[i]) / 3
        typical_prices.append(tp)
    
    # Calculate Simple Moving Average of Typical Price
    sma_tp = np.mean(typical_prices[-period:])
    
    # Calculate Mean Deviation
    mean_deviation = np.mean([abs(tp - sma_tp) for tp in typical_prices[-period:]])
    
    # Calculate CCI
    if mean_deviation == 0:
        return 0.0
    
    current_tp = typical_prices[-1]
    cci = (current_tp - sma_tp) / (0.015 * mean_deviation)
    
    return cci

def determine_signal_status(cci_value, overbought_level=100, oversold_level=-100):
    """Determine signal status based on CCI value"""
    if cci_value > overbought_level:
        return "overbought"
    elif cci_value < oversold_level:
        return "oversold"
    elif cci_value > 0:
        return "bullish"
    elif cci_value < 0:
        return "bearish"
    else:
        return "neutral"

def calculate_signal_strength(cci_value, signal_status, overbought_level=100, oversold_level=-100):
    """Calculate signal strength based on CCI value"""
    if signal_status == "overbought":
        # Strength based on how far above overbought level
        strength = min((cci_value - overbought_level) / overbought_level * 100, 100)
        return max(strength, 0)
    elif signal_status == "oversold":
        # Strength based on how far below oversold level
        strength = min((oversold_level - cci_value) / abs(oversold_level) * 100, 100)
        return max(strength, 0)
    elif signal_status == "bullish":
        # Strength based on distance from neutral (0)
        strength = min(cci_value / overbought_level * 100, 100)
        return max(strength, 0)
    elif signal_status == "bearish":
        # Strength based on distance from neutral (0)
        strength = min(abs(cci_value) / abs(oversold_level) * 100, 100)
        return max(strength, 0)
    else:
        return 0.0

def detect_divergence(cci_values, prices, lookback=14):
    """Detect divergence between price and CCI"""
    if len(cci_values) < lookback or len(prices) < lookback:
        return "none", 0.0
    
    # Get recent data
    recent_prices = prices[-lookback:]
    recent_cci = cci_values[-lookback:]
    
    # Calculate price trend
    price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
    
    # Calculate CCI trend
    cci_trend = "up" if recent_cci[-1] > recent_cci[0] else "down"
    
    # Detect divergence
    if price_trend == "up" and cci_trend == "down":
        # Bearish divergence: price up, indicator down
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bearish", divergence_strength
    elif price_trend == "down" and cci_trend == "up":
        # Bullish divergence: price down, indicator up
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bullish", divergence_strength
    else:
        return "none", 0.0

def determine_momentum_trend(cci_values, period=5):
    """Determine momentum trend based on CCI values"""
    if len(cci_values) < period:
        return "neutral", 0.0
    
    recent_cci = cci_values[-period:]
    
    # Calculate momentum
    momentum_change = recent_cci[-1] - recent_cci[0]
    momentum_strength = abs(momentum_change) / 200 * 100  # Normalize to 0-100 (assuming CCI range of ±200)
    
    if momentum_change > 0:
        return "increasing", momentum_strength
    elif momentum_change < 0:
        return "decreasing", momentum_strength
    else:
        return "neutral", 0.0

def detect_extreme_levels(cci_value, extreme_threshold=200):
    """Detect extreme overbought/oversold levels"""
    if cci_value > extreme_threshold:
        extreme_level = cci_value - extreme_threshold
        extreme_type = "extreme_overbought"
    elif cci_value < -extreme_threshold:
        extreme_level = abs(cci_value + extreme_threshold)
        extreme_type = "extreme_oversold"
    else:
        extreme_level = 0.0
        extreme_type = "none"
    
    return extreme_level, extreme_type

def calculate_cci_for_symbol(symbol, symbol_id):
    """Calculate CCI for all timeframes for a symbol"""
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
                
                if len(closes) >= 30:  # Need enough data for CCI
                    # Calculate CCI values for the entire period
                    cci_values = []
                    for i in range(19, len(closes)):  # Start from 20th element
                        cci = calculate_cci(highs[:i+1], lows[:i+1], closes[:i+1], 20)
                        if cci is not None:
                            cci_values.append(cci)
                    
                    if len(cci_values) >= 10:  # Need enough CCI values
                        # Calculate current CCI
                        current_cci = calculate_cci(highs, lows, closes, 20)
                        
                        if current_cci is not None:
                            # Determine signal status
                            signal_status = determine_signal_status(current_cci)
                            
                            # Calculate signal strength
                            signal_strength = calculate_signal_strength(current_cci, signal_status)
                            
                            # Detect divergence
                            divergence_type, divergence_strength = detect_divergence(cci_values, closes)
                            
                            # Determine momentum trend
                            momentum_trend, momentum_strength = determine_momentum_trend(cci_values)
                            
                            # Detect extreme levels
                            extreme_level, extreme_type = detect_extreme_levels(current_cci)
                            
                            results[tf] = {
                                "cci_value": current_cci,
                                "overbought_level": 100.0,
                                "oversold_level": -100.0,
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
                            print(f"⚠️ Could not calculate CCI for {symbol} {tf}")
                    else:
                        print(f"⚠️ Insufficient CCI data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating CCI for {symbol}: {e}")
        return {}

def store_cci_data(symbol_id, symbol, cci_data):
    """Store CCI data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in cci_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO cci_data 
                (symbol_id, symbol, timeframe, cci_value, overbought_level, oversold_level,
                signal_status, signal_strength, divergence_type, divergence_strength,
                momentum_trend, momentum_strength, extreme_level, extreme_type,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['cci_value'], data['overbought_level'],
                data['oversold_level'], data['signal_status'], data['signal_strength'],
                data['divergence_type'], data['divergence_strength'], data['momentum_trend'],
                data['momentum_strength'], data['extreme_level'], data['extreme_type'],
                data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing CCI data for {symbol}: {e}")
        return False

def generate_cci_report():
    """Generate a comprehensive report of all CCI data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, cci_value, signal_status, signal_strength,
                   divergence_type, divergence_strength, momentum_trend, momentum_strength,
                   extreme_level, extreme_type, current_price, last_updated
            FROM cci_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No CCI data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 CCI (COMMODITY CHANNEL INDEX) COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = row
            
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
                "extreme_overbought": "🚀",
                "extreme_oversold": "💥",
                "none": "⚪"
            }.get(extreme_type, "⚪")
            
            print(f"  {timeframe:>4} | CCI: {cci_value:>7.1f} | {signal_emoji} {signal_status:>10} | {divergence_emoji} {divergence_type:>8} | {momentum_emoji} {momentum_trend:>10} | {extreme_emoji} {extreme_type:>18}")
        
        print("\n" + "="*80)
        print("📈 CCI SUMMARY:")
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
        extreme_overbought_count = sum(1 for row in data if row[10] == "extreme_overbought")
        extreme_oversold_count = sum(1 for row in data if row[10] == "extreme_oversold")
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
        overbought_signals = [row for row in data if row[3] == "overbought" and row[4] > 30]
        if overbought_signals:
            print("   🔴 Overbought Conditions (Potential Sell Opportunities):")
            for signal in overbought_signals:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - CCI: {cci_value:.1f}")
        else:
            print("   ✅ No strong overbought conditions detected")
        
        # Find oversold conditions
        oversold_signals = [row for row in data if row[3] == "oversold" and row[4] > 30]
        if oversold_signals:
            print("   🟢 Oversold Conditions (Potential Buy Opportunities):")
            for signal in oversold_signals:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - CCI: {cci_value:.1f}")
        else:
            print("   ✅ No strong oversold conditions detected")
        
        # Find bullish divergences
        bullish_divergences = [row for row in data if row[5] == "bullish" and row[6] > 2.0]
        if bullish_divergences:
            print("   🟢 Bullish Divergences (Potential Buy Signals):")
            for divergence in bullish_divergences:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price down, CCI up")
        else:
            print("   ✅ No bullish divergences detected")
        
        # Find bearish divergences
        bearish_divergences = [row for row in data if row[5] == "bearish" and row[6] > 2.0]
        if bearish_divergences:
            print("   🔴 Bearish Divergences (Potential Sell Signals):")
            for divergence in bearish_divergences:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price up, CCI down")
        else:
            print("   ✅ No bearish divergences detected")
        
        # Find extreme levels
        extreme_overbought = [row for row in data if row[10] == "extreme_overbought"]
        if extreme_overbought:
            print("   🚀 Extreme Overbought Levels (Potential Reversal):")
            for extreme in extreme_overbought:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = extreme
                print(f"      • {symbol} {timeframe}: CCI: {cci_value:.1f} (extreme level: {extreme_level:.1f})")
        else:
            print("   ✅ No extreme overbought levels detected")
        
        extreme_oversold = [row for row in data if row[10] == "extreme_oversold"]
        if extreme_oversold:
            print("   💥 Extreme Oversold Levels (Potential Reversal):")
            for extreme in extreme_oversold:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = extreme
                print(f"      • {symbol} {timeframe}: CCI: {cci_value:.1f} (extreme level: {extreme_level:.1f})")
        else:
            print("   ✅ No extreme oversold levels detected")
        
        # Find strong momentum trends
        strong_momentum = [row for row in data if row[8] > 30]
        if strong_momentum:
            print("   📈 Strong Momentum Trends:")
            for momentum in strong_momentum:
                symbol, timeframe, cci_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type, current_price, last_updated = momentum
                print(f"      • {symbol} {timeframe}: {momentum_trend} momentum ({momentum_strength:.1f}% strength)")
        else:
            print("   ✅ No strong momentum trends detected")
        
        print("\n" + "="*80)
        print("✅ CCI report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating CCI report: {e}")

def main():
    """Main function to populate CCI data"""
    print("🚀 Starting CCI data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store CCI for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        cci_data = calculate_cci_for_symbol(symbol, symbol_id)
        if cci_data:
            if store_cci_data(symbol_id, symbol, cci_data):
                print(f"✅ Stored {len(cci_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No CCI data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_cci_report()

if __name__ == "__main__":
    main()
