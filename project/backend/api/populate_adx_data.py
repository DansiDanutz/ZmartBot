#!/usr/bin/env python3
"""
Populate ADX Data
Calculates and stores ADX (Average Directional Index) indicators for all symbols in My Symbols list
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

def calculate_directional_movement(high, low, prev_high, prev_low):
    """Calculate Directional Movement"""
    up_move = high - prev_high
    down_move = prev_low - low
    
    if up_move > down_move and up_move > 0:
        return up_move, 0  # +DM, -DM
    elif down_move > up_move and down_move > 0:
        return 0, down_move  # +DM, -DM
    else:
        return 0, 0  # +DM, -DM

def calculate_adx(highs, lows, closes, period=14):
    """Calculate ADX (Average Directional Index)"""
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None, None, None, None, None, None
    
    # Calculate True Range and Directional Movement
    tr_values = []
    plus_dm_values = []
    minus_dm_values = []
    
    for i in range(1, len(highs)):
        tr = calculate_true_range(highs[i], lows[i], closes[i-1])
        plus_dm, minus_dm = calculate_directional_movement(highs[i], lows[i], highs[i-1], lows[i-1])
        
        tr_values.append(tr)
        plus_dm_values.append(plus_dm)
        minus_dm_values.append(minus_dm)
    
    if len(tr_values) < period:
        return None, None, None, None, None, None
    
    # Calculate smoothed values using Wilder's smoothing
    # Initial values
    atr = sum(tr_values[:period])
    plus_di_smooth = sum(plus_dm_values[:period])
    minus_di_smooth = sum(minus_dm_values[:period])
    
    # Calculate initial DI values
    if atr > 0:
        plus_di = (plus_di_smooth / atr) * 100
        minus_di = (minus_di_smooth / atr) * 100
    else:
        plus_di = 0
        minus_di = 0
    
    # Calculate DX
    di_sum = plus_di + minus_di
    if di_sum > 0:
        dx = abs(plus_di - minus_di) / di_sum * 100
    else:
        dx = 0
    
    # Smooth DX to get ADX
    adx = dx
    
    # Apply smoothing for remaining periods
    for i in range(period, len(tr_values)):
        # Smooth ATR
        atr = (atr * (period - 1) + tr_values[i]) / period
        
        # Smooth DI values
        plus_di_smooth = (plus_di_smooth * (period - 1) + plus_dm_values[i]) / period
        minus_di_smooth = (minus_di_smooth * (period - 1) + minus_dm_values[i]) / period
        
        # Calculate DI values
        if atr > 0:
            plus_di = (plus_di_smooth / atr) * 100
            minus_di = (minus_di_smooth / atr) * 100
        else:
            plus_di = 0
            minus_di = 0
        
        # Calculate DX
        di_sum = plus_di + minus_di
        if di_sum > 0:
            dx = abs(plus_di - minus_di) / di_sum * 100
        else:
            dx = 0
        
        # Smooth ADX
        adx = (adx * (period - 1) + dx) / period
    
    return adx, plus_di, minus_di, tr_values, plus_dm_values, minus_dm_values

def determine_trend_strength(adx_value):
    """Determine trend strength based on ADX value"""
    if adx_value >= 50:
        return "very_strong", adx_value
    elif adx_value >= 40:
        return "strong", adx_value
    elif adx_value >= 25:
        return "moderate", adx_value
    elif adx_value >= 20:
        return "weak", adx_value
    else:
        return "very_weak", adx_value

def determine_trend_direction(plus_di, minus_di):
    """Determine trend direction based on DI values"""
    if plus_di > minus_di:
        return "bullish"
    elif minus_di > plus_di:
        return "bearish"
    else:
        return "neutral"

def detect_di_crossover(plus_di_values, minus_di_values, period=5):
    """Detect DI crossover signals"""
    if len(plus_di_values) < period or len(minus_di_values) < period:
        return "none", 0.0
    
    current_plus_di = plus_di_values[-1]
    current_minus_di = minus_di_values[-1]
    prev_plus_di = plus_di_values[-2]
    prev_minus_di = minus_di_values[-2]
    
    # Check for bullish crossover (+DI crosses above -DI)
    if prev_plus_di <= prev_minus_di and current_plus_di > current_minus_di:
        crossover_strength = abs(current_plus_di - current_minus_di)
        return "bullish", min(crossover_strength, 100)
    
    # Check for bearish crossover (-DI crosses above +DI)
    elif prev_minus_di <= prev_plus_di and current_minus_di > current_plus_di:
        crossover_strength = abs(current_minus_di - current_plus_di)
        return "bearish", min(crossover_strength, 100)
    
    else:
        return "none", 0.0

def determine_momentum_signal(adx_values, plus_di_values, minus_di_values, period=5):
    """Determine momentum signal based on ADX and DI trends"""
    if len(adx_values) < period or len(plus_di_values) < period or len(minus_di_values) < period:
        return "neutral", 0.0
    
    # Calculate momentum changes
    adx_change = adx_values[-1] - adx_values[-period]
    plus_di_change = plus_di_values[-1] - plus_di_values[-period]
    minus_di_change = minus_di_values[-1] - minus_di_values[-period]
    
    # Determine momentum signal
    if adx_change > 0 and plus_di_change > 0 and plus_di_values[-1] > minus_di_values[-1]:
        # Strong bullish momentum
        momentum_strength = min((adx_change + plus_di_change) / 2, 100)
        return "strong_bullish", momentum_strength
    elif adx_change > 0 and minus_di_change > 0 and minus_di_values[-1] > plus_di_values[-1]:
        # Strong bearish momentum
        momentum_strength = min((adx_change + minus_di_change) / 2, 100)
        return "strong_bearish", momentum_strength
    elif plus_di_change > 0 and plus_di_values[-1] > minus_di_values[-1]:
        # Weak bullish momentum
        momentum_strength = min(plus_di_change, 100)
        return "weak_bullish", momentum_strength
    elif minus_di_change > 0 and minus_di_values[-1] > plus_di_values[-1]:
        # Weak bearish momentum
        momentum_strength = min(minus_di_change, 100)
        return "weak_bearish", momentum_strength
    else:
        return "neutral", 0.0

def detect_breakout_potential(adx_value, plus_di, minus_di, current_price, period=5):
    """Detect potential breakout based on ADX and DI values"""
    if adx_value >= 40:
        # Strong trend suggests potential breakout
        if adx_value >= 50:
            return "high", min((adx_value - 50) / 10 * 100, 100)
        else:
            return "moderate", min((adx_value - 40) / 10 * 100, 100)
    elif adx_value <= 20:
        # Very weak trend suggests potential breakout from consolidation
        return "consolidation", min((20 - adx_value) / 20 * 100, 100)
    else:
        return "none", 0.0

def calculate_adx_for_symbol(symbol, symbol_id):
    """Calculate ADX for all timeframes for a symbol"""
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
                
                if len(closes) >= 30:  # Need enough data for ADX
                    # Calculate ADX values for the entire period
                    adx_values = []
                    plus_di_values = []
                    minus_di_values = []
                    
                    for i in range(14, len(closes)):
                        adx, plus_di, minus_di, tr, plus_dm, minus_dm = calculate_adx(highs[:i+1], lows[:i+1], closes[:i+1], 14)
                        if adx is not None:
                            adx_values.append(adx)
                            plus_di_values.append(plus_di)
                            minus_di_values.append(minus_di)
                    
                    if len(adx_values) >= 10:  # Need enough ADX values
                        # Calculate current ADX
                        current_adx, current_plus_di, current_minus_di, tr_values, plus_dm_values, minus_dm_values = calculate_adx(highs, lows, closes, 14)
                        
                        if current_adx is not None:
                            # Determine trend strength
                            trend_strength, trend_strength_value = determine_trend_strength(current_adx)
                            
                            # Determine trend direction
                            trend_direction = determine_trend_direction(current_plus_di, current_minus_di)
                            
                            # Detect DI crossover
                            di_crossover, di_crossover_strength = detect_di_crossover(plus_di_values, minus_di_values)
                            
                            # Determine momentum signal
                            momentum_signal, momentum_strength = determine_momentum_signal(adx_values, plus_di_values, minus_di_values)
                            
                            # Detect breakout potential
                            breakout_potential, breakout_strength = detect_breakout_potential(current_adx, current_plus_di, current_minus_di, current_price)
                            
                            results[tf] = {
                                "adx_value": current_adx,
                                "plus_di": current_plus_di,
                                "minus_di": current_minus_di,
                                "trend_strength": trend_strength,
                                "trend_strength_value": trend_strength_value,
                                "trend_direction": trend_direction,
                                "di_crossover": di_crossover,
                                "di_crossover_strength": di_crossover_strength,
                                "momentum_signal": momentum_signal,
                                "momentum_strength": momentum_strength,
                                "breakout_potential": breakout_potential,
                                "breakout_strength": breakout_strength,
                                "current_price": current_price
                            }
                        else:
                            print(f"⚠️ Could not calculate ADX for {symbol} {tf}")
                    else:
                        print(f"⚠️ Insufficient ADX data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating ADX for {symbol}: {e}")
        return {}

def store_adx_data(symbol_id, symbol, adx_data):
    """Store ADX data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in adx_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO adx_data 
                (symbol_id, symbol, timeframe, adx_value, plus_di, minus_di,
                trend_strength, trend_strength_value, trend_direction, di_crossover,
                di_crossover_strength, momentum_signal, momentum_strength,
                breakout_potential, breakout_strength, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['adx_value'], data['plus_di'],
                data['minus_di'], data['trend_strength'], data['trend_strength_value'],
                data['trend_direction'], data['di_crossover'], data['di_crossover_strength'],
                data['momentum_signal'], data['momentum_strength'], data['breakout_potential'],
                data['breakout_strength'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing ADX data for {symbol}: {e}")
        return False

def generate_adx_report():
    """Generate a comprehensive report of all ADX data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, adx_value, plus_di, minus_di, trend_strength,
                   trend_strength_value, trend_direction, di_crossover, di_crossover_strength,
                   momentum_signal, momentum_strength, breakout_potential, breakout_strength,
                   current_price, last_updated
            FROM adx_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No ADX data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 ADX (AVERAGE DIRECTIONAL INDEX) COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine trend strength emoji
            strength_emoji = {
                "very_strong": "💪",
                "strong": "🔥",
                "moderate": "⚡",
                "weak": "🌊",
                "very_weak": "💧"
            }.get(trend_strength, "⚪")
            
            # Determine trend direction emoji
            direction_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "⚪"
            }.get(trend_direction, "⚪")
            
            # Determine crossover emoji
            crossover_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(di_crossover, "⚪")
            
            # Determine momentum emoji
            momentum_emoji = {
                "strong_bullish": "🚀",
                "strong_bearish": "💥",
                "weak_bullish": "🟢",
                "weak_bearish": "🔴",
                "neutral": "⚪"
            }.get(momentum_signal, "⚪")
            
            # Determine breakout emoji
            breakout_emoji = {
                "high": "🎯",
                "moderate": "📊",
                "consolidation": "🎲",
                "none": "⚪"
            }.get(breakout_potential, "⚪")
            
            print(f"  {timeframe:>4} | ADX: {adx_value:>5.1f} | +DI: {plus_di:>5.1f} | -DI: {minus_di:>5.1f} | {strength_emoji} {trend_strength:>12} | {direction_emoji} {trend_direction:>8} | {crossover_emoji} {di_crossover:>8} | {momentum_emoji} {momentum_signal:>15} | {breakout_emoji} {breakout_potential:>12}")
        
        print("\n" + "="*80)
        print("📈 ADX SUMMARY:")
        print("="*80)
        
        # Count by trend strength
        very_strong_count = sum(1 for row in data if row[5] == "very_strong")
        strong_count = sum(1 for row in data if row[5] == "strong")
        moderate_count = sum(1 for row in data if row[5] == "moderate")
        weak_count = sum(1 for row in data if row[5] == "weak")
        very_weak_count = sum(1 for row in data if row[5] == "very_weak")
        
        # Count by trend direction
        bullish_count = sum(1 for row in data if row[7] == "bullish")
        bearish_count = sum(1 for row in data if row[7] == "bearish")
        neutral_count = sum(1 for row in data if row[7] == "neutral")
        
        # Count by DI crossover
        bullish_crossover_count = sum(1 for row in data if row[8] == "bullish")
        bearish_crossover_count = sum(1 for row in data if row[8] == "bearish")
        no_crossover_count = sum(1 for row in data if row[8] == "none")
        
        # Count by momentum signal
        strong_bullish_momentum_count = sum(1 for row in data if row[10] == "strong_bullish")
        strong_bearish_momentum_count = sum(1 for row in data if row[10] == "strong_bearish")
        weak_bullish_momentum_count = sum(1 for row in data if row[10] == "weak_bullish")
        weak_bearish_momentum_count = sum(1 for row in data if row[10] == "weak_bearish")
        neutral_momentum_count = sum(1 for row in data if row[10] == "neutral")
        
        # Count by breakout potential
        high_breakout_count = sum(1 for row in data if row[12] == "high")
        moderate_breakout_count = sum(1 for row in data if row[12] == "moderate")
        consolidation_breakout_count = sum(1 for row in data if row[12] == "consolidation")
        no_breakout_count = sum(1 for row in data if row[12] == "none")
        
        # Count strong trends
        strong_trends = sum(1 for row in data if row[6] > 40)
        moderate_trends = sum(1 for row in data if 25 < row[6] <= 40)
        weak_trends = sum(1 for row in data if row[6] <= 25)
        
        print(f"   💪 Very Strong Trends (≥50): {very_strong_count}")
        print(f"   🔥 Strong Trends (40-49): {strong_count}")
        print(f"   ⚡ Moderate Trends (25-39): {moderate_count}")
        print(f"   🌊 Weak Trends (20-24): {weak_count}")
        print(f"   💧 Very Weak Trends (<20): {very_weak_count}")
        print(f"   🟢 Bullish Trends: {bullish_count}")
        print(f"   🔴 Bearish Trends: {bearish_count}")
        print(f"   ⚪ Neutral Trends: {neutral_count}")
        print(f"   🟢 Bullish Crossovers: {bullish_crossover_count}")
        print(f"   🔴 Bearish Crossovers: {bearish_crossover_count}")
        print(f"   ⚪ No Crossovers: {no_crossover_count}")
        print(f"   🚀 Strong Bullish Momentum: {strong_bullish_momentum_count}")
        print(f"   💥 Strong Bearish Momentum: {strong_bearish_momentum_count}")
        print(f"   🟢 Weak Bullish Momentum: {weak_bullish_momentum_count}")
        print(f"   🔴 Weak Bearish Momentum: {weak_bearish_momentum_count}")
        print(f"   ⚪ Neutral Momentum: {neutral_momentum_count}")
        print(f"   🎯 High Breakout Potential: {high_breakout_count}")
        print(f"   📊 Moderate Breakout Potential: {moderate_breakout_count}")
        print(f"   🎲 Consolidation Breakout: {consolidation_breakout_count}")
        print(f"   ⚪ No Breakout Potential: {no_breakout_count}")
        print(f"   💪 Strong Trends (>40): {strong_trends}")
        print(f"   📊 Moderate Trends (25-40): {moderate_trends}")
        print(f"   🔸 Weak Trends (<25): {weak_trends}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find very strong trends
        very_strong_trends = [row for row in data if row[5] == "very_strong" and row[6] > 50]
        if very_strong_trends:
            print("   💪 Very Strong Trends (High Confidence Trades):")
            for trend in very_strong_trends:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: ADX {adx_value:.1f} - {trend_direction} trend - +DI: {plus_di:.1f}, -DI: {minus_di:.1f}")
        else:
            print("   ✅ No very strong trends detected")
        
        # Find strong trends
        strong_trends = [row for row in data if row[5] == "strong" and 40 <= row[6] <= 49]
        if strong_trends:
            print("   🔥 Strong Trends (Good Trading Opportunities):")
            for trend in strong_trends:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: ADX {adx_value:.1f} - {trend_direction} trend - +DI: {plus_di:.1f}, -DI: {minus_di:.1f}")
        else:
            print("   ✅ No strong trends detected")
        
        # Find bullish crossovers
        bullish_crossovers = [row for row in data if row[8] == "bullish" and row[9] > 5]
        if bullish_crossovers:
            print("   🟢 Bullish DI Crossovers (Potential Buy Signals):")
            for crossover in bullish_crossovers:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = crossover
                print(f"      • {symbol} {timeframe}: Crossover strength {di_crossover_strength:.1f} - +DI: {plus_di:.1f}, -DI: {minus_di:.1f}")
        else:
            print("   ✅ No bullish crossovers detected")
        
        # Find bearish crossovers
        bearish_crossovers = [row for row in data if row[8] == "bearish" and row[9] > 5]
        if bearish_crossovers:
            print("   🔴 Bearish DI Crossovers (Potential Sell Signals):")
            for crossover in bearish_crossovers:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = crossover
                print(f"      • {symbol} {timeframe}: Crossover strength {di_crossover_strength:.1f} - +DI: {plus_di:.1f}, -DI: {minus_di:.1f}")
        else:
            print("   ✅ No bearish crossovers detected")
        
        # Find strong momentum signals
        strong_momentum = [row for row in data if row[10] in ["strong_bullish", "strong_bearish"] and row[11] > 20]
        if strong_momentum:
            print("   🚀 Strong Momentum Signals:")
            for momentum in strong_momentum:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = momentum
                print(f"      • {symbol} {timeframe}: {momentum_signal} momentum ({momentum_strength:.1f}% strength)")
        else:
            print("   ✅ No strong momentum signals detected")
        
        # Find high breakout potential
        high_breakout = [row for row in data if row[12] == "high" and row[13] > 30]
        if high_breakout:
            print("   🎯 High Breakout Potential (Strong Trend Continuation):")
            for breakout in high_breakout:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: Breakout strength {breakout_strength:.1f}% - ADX: {adx_value:.1f}")
        else:
            print("   ✅ No high breakout potential detected")
        
        # Find consolidation breakout potential
        consolidation_breakout = [row for row in data if row[12] == "consolidation" and row[13] > 30]
        if consolidation_breakout:
            print("   🎲 Consolidation Breakout Potential (Low ADX Reversal):")
            for breakout in consolidation_breakout:
                symbol, timeframe, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: Breakout strength {breakout_strength:.1f}% - ADX: {adx_value:.1f}")
        else:
            print("   ✅ No consolidation breakout potential detected")
        
        print("\n" + "="*80)
        print("✅ ADX report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating ADX report: {e}")

def main():
    """Main function to populate ADX data"""
    print("🚀 Starting ADX data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store ADX for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        adx_data = calculate_adx_for_symbol(symbol, symbol_id)
        if adx_data:
            if store_adx_data(symbol_id, symbol, adx_data):
                print(f"✅ Stored {len(adx_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No ADX data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_adx_report()

if __name__ == "__main__":
    main()
