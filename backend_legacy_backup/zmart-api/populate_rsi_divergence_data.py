#!/usr/bin/env python3
"""
Populate RSI Divergence Data
Calculates and stores RSI Divergence analysis for all symbols in My Symbols list
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

def calculate_rsi(prices, period=14):
    """Calculate RSI (Relative Strength Index)"""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gains = np.mean(gains[:period])
    avg_losses = np.mean(losses[:period])
    
    for i in range(period, len(gains)):
        avg_gains = (avg_gains * (period - 1) + gains[i]) / period
        avg_losses = (avg_losses * (period - 1) + losses[i]) / period
    
    if avg_losses == 0:
        return 100.0
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def find_peaks_and_troughs(prices, rsi_values, window=5):
    """Find peaks and troughs in price and RSI data"""
    if len(prices) < window * 2 or len(rsi_values) < window * 2:
        return [], [], [], []
    
    price_peaks = []
    price_troughs = []
    rsi_peaks = []
    rsi_troughs = []
    
    # Ensure we have enough data
    if len(prices) != len(rsi_values):
        return [], [], [], []
    
    for i in range(window, len(prices) - window):
        try:
            # Check for price peaks
            if all(prices[i] >= prices[j] for j in range(i - window, i + window + 1)):
                price_peaks.append((i, prices[i]))
            
            # Check for price troughs
            if all(prices[i] <= prices[j] for j in range(i - window, i + window + 1)):
                price_troughs.append((i, prices[i]))
            
            # Check for RSI peaks
            if all(rsi_values[i] >= rsi_values[j] for j in range(i - window, i + window + 1)):
                rsi_peaks.append((i, rsi_values[i]))
            
            # Check for RSI troughs
            if all(rsi_values[i] <= rsi_values[j] for j in range(i - window, i + window + 1)):
                rsi_troughs.append((i, rsi_values[i]))
        except IndexError:
            continue
    
    return price_peaks, price_troughs, rsi_peaks, rsi_troughs

def detect_bullish_divergence(price_troughs, rsi_troughs, lookback=20):
    """Detect bullish divergence (price makes lower lows, RSI makes higher lows)"""
    if len(price_troughs) < 2 or len(rsi_troughs) < 2:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Get recent troughs
    recent_price_troughs = price_troughs[-2:]
    recent_rsi_troughs = rsi_troughs[-2:]
    
    if len(recent_price_troughs) < 2 or len(recent_rsi_troughs) < 2:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Check if price is making lower lows
    price_low_1, price_low_2 = recent_price_troughs[0][1], recent_price_troughs[1][1]
    if price_low_2 >= price_low_1:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Check if RSI is making higher lows
    rsi_low_1, rsi_low_2 = recent_rsi_troughs[0][1], recent_rsi_troughs[1][1]
    if rsi_low_2 <= rsi_low_1:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Calculate divergence strength
    price_change = abs(price_low_2 - price_low_1) / price_low_1 * 100
    rsi_change = abs(rsi_low_2 - rsi_low_1)
    divergence_strength = (price_change + rsi_change) / 2
    
    # Calculate divergence period
    divergence_period = recent_price_troughs[1][0] - recent_price_troughs[0][0]
    
    return "bullish", divergence_strength, 0, 0, price_low_1, price_low_2, 0, 0, rsi_low_1, rsi_low_2, divergence_period

def detect_bearish_divergence(price_peaks, rsi_peaks, lookback=20):
    """Detect bearish divergence (price makes higher highs, RSI makes lower highs)"""
    if len(price_peaks) < 2 or len(rsi_peaks) < 2:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Get recent peaks
    recent_price_peaks = price_peaks[-2:]
    recent_rsi_peaks = rsi_peaks[-2:]
    
    if len(recent_price_peaks) < 2 or len(recent_rsi_peaks) < 2:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Check if price is making higher highs
    price_high_1, price_high_2 = recent_price_peaks[0][1], recent_price_peaks[1][1]
    if price_high_2 <= price_high_1:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Check if RSI is making lower highs
    rsi_high_1, rsi_high_2 = recent_rsi_peaks[0][1], recent_rsi_peaks[1][1]
    if rsi_high_2 >= rsi_high_1:
        return None, 0.0, 0, 0, 0, 0, 0, 0, 0
    
    # Calculate divergence strength
    price_change = abs(price_high_2 - price_high_1) / price_high_1 * 100
    rsi_change = abs(rsi_high_1 - rsi_high_2)
    divergence_strength = (price_change + rsi_change) / 2
    
    # Calculate divergence period
    divergence_period = recent_price_peaks[1][0] - recent_price_peaks[0][0]
    
    return "bearish", divergence_strength, price_high_1, price_high_2, 0, 0, rsi_high_1, rsi_high_2, divergence_period

def determine_confirmation_level(divergence_type, current_price, current_rsi, price_high_1, price_high_2, price_low_1, price_low_2):
    """Determine confirmation level of divergence"""
    if divergence_type == "bullish":
        # Check if price is breaking above the first low
        if current_price > price_low_1:
            return "confirmed"
        elif current_price > price_low_2:
            return "partial"
        else:
            return "pending"
    elif divergence_type == "bearish":
        # Check if price is breaking below the first high
        if current_price < price_high_1:
            return "confirmed"
        elif current_price < price_high_2:
            return "partial"
        else:
            return "pending"
    else:
        return "pending"

def calculate_signal_strength(divergence_strength, confirmation_level):
    """Calculate signal strength based on divergence strength and confirmation"""
    base_strength = min(divergence_strength, 100)
    
    confirmation_multiplier = {
        "confirmed": 1.0,
        "partial": 0.7,
        "pending": 0.4
    }.get(confirmation_level, 0.4)
    
    return base_strength * confirmation_multiplier

def determine_trend_direction(divergence_type, current_price, price_high_1, price_high_2, price_low_1, price_low_2):
    """Determine trend direction based on divergence and current price"""
    if divergence_type == "bullish":
        if current_price > price_low_1:
            return "bullish"
        elif current_price > price_low_2:
            return "potential_bullish"
        else:
            return "neutral"
    elif divergence_type == "bearish":
        if current_price < price_high_1:
            return "bearish"
        elif current_price < price_high_2:
            return "potential_bearish"
        else:
            return "neutral"
    else:
        return "neutral"

def determine_momentum_shift(divergence_type, current_rsi, rsi_high_1, rsi_high_2, rsi_low_1, rsi_low_2):
    """Determine momentum shift based on current RSI position"""
    if divergence_type == "bullish":
        if current_rsi > rsi_low_1:
            return "strong_bullish"
        elif current_rsi > rsi_low_2:
            return "weak_bullish"
        else:
            return "none"
    elif divergence_type == "bearish":
        if current_rsi < rsi_high_1:
            return "strong_bearish"
        elif current_rsi < rsi_high_2:
            return "weak_bearish"
        else:
            return "none"
    else:
        return "none"

def determine_breakout_potential(divergence_type, divergence_strength, confirmation_level):
    """Determine breakout potential based on divergence characteristics"""
    if divergence_strength > 50 and confirmation_level == "confirmed":
        if divergence_type == "bullish":
            return "high_bullish"
        else:
            return "high_bearish"
    elif divergence_strength > 30 and confirmation_level in ["confirmed", "partial"]:
        if divergence_type == "bullish":
            return "moderate_bullish"
        else:
            return "moderate_bearish"
    elif divergence_strength > 15:
        if divergence_type == "bullish":
            return "low_bullish"
        else:
            return "low_bearish"
    else:
        return "none"

def calculate_rsi_divergence_for_symbol(symbol, symbol_id):
    """Calculate RSI Divergence for all timeframes for a symbol"""
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
                
                # Extract close prices
                closes = [float(kline[4]) for kline in klines_data]
                
                if len(closes) >= 50:  # Need enough data for divergence analysis
                    # Calculate RSI values
                    rsi_values = []
                    for i in range(14, len(closes)):
                        rsi = calculate_rsi(closes[:i+1], 14)
                        if rsi is not None:
                            rsi_values.append(rsi)
                    
                    if len(rsi_values) >= 30:  # Need enough RSI values
                        # Find peaks and troughs
                        price_peaks, price_troughs, rsi_peaks, rsi_troughs = find_peaks_and_troughs(closes, rsi_values)
                        
                        # Detect divergences
                        bullish_div = detect_bullish_divergence(price_troughs, rsi_troughs)
                        bearish_div = detect_bearish_divergence(price_peaks, rsi_peaks)
                        
                        # Determine which divergence is stronger
                        if bullish_div[0] and bearish_div[0]:
                            if bullish_div[1] > bearish_div[1]:
                                divergence_type, divergence_strength, price_high_1, price_high_2, price_low_1, price_low_2, rsi_high_1, rsi_high_2, divergence_period = bullish_div
                            else:
                                divergence_type, divergence_strength, price_high_1, price_high_2, price_low_1, price_low_2, rsi_high_1, rsi_high_2, divergence_period = bearish_div
                        elif bullish_div[0]:
                            divergence_type, divergence_strength, price_high_1, price_high_2, price_low_1, price_low_2, rsi_high_1, rsi_high_2, divergence_period = bullish_div
                        elif bearish_div[0]:
                            divergence_type, divergence_strength, price_high_1, price_high_2, price_low_1, price_low_2, rsi_high_1, rsi_high_2, divergence_period = bearish_div
                        else:
                            # No divergence detected
                            divergence_type = "none"
                            divergence_strength = 0.0
                            price_high_1 = price_high_2 = price_low_1 = price_low_2 = 0.0
                            rsi_high_1 = rsi_high_2 = rsi_low_1 = rsi_low_2 = 0.0
                            divergence_period = 0
                        
                        # Get current RSI
                        current_rsi = calculate_rsi(closes, 14)
                        
                        if divergence_type != "none":
                            # Determine confirmation level
                            confirmation_level = determine_confirmation_level(divergence_type, current_price, current_rsi, price_high_1, price_high_2, price_low_1, price_low_2)
                            
                            # Calculate signal strength
                            signal_strength = calculate_signal_strength(divergence_strength, confirmation_level)
                            
                            # Determine trend direction
                            trend_direction = determine_trend_direction(divergence_type, current_price, price_high_1, price_high_2, price_low_1, price_low_2)
                            
                            # Determine momentum shift
                            momentum_shift = determine_momentum_shift(divergence_type, current_rsi, rsi_high_1, rsi_high_2, rsi_low_1, rsi_low_2)
                            
                            # Determine breakout potential
                            breakout_potential = determine_breakout_potential(divergence_type, divergence_strength, confirmation_level)
                        else:
                            # Set default values for "none" divergence
                            confirmation_level = "none"
                            signal_strength = 0.0
                            trend_direction = "neutral"
                            momentum_shift = "none"
                            breakout_potential = "none"
                        
                        results[tf] = {
                            "divergence_type": divergence_type,
                            "divergence_strength": divergence_strength,
                            "price_high_1": price_high_1,
                            "price_high_2": price_high_2,
                            "price_low_1": price_low_1,
                            "price_low_2": price_low_2,
                            "rsi_high_1": rsi_high_1,
                            "rsi_high_2": rsi_high_2,
                            "rsi_low_1": rsi_low_1,
                            "rsi_low_2": rsi_low_2,
                            "divergence_period": divergence_period,
                            "confirmation_level": confirmation_level,
                            "signal_strength": signal_strength,
                            "trend_direction": trend_direction,
                            "momentum_shift": momentum_shift,
                            "breakout_potential": breakout_potential,
                            "current_price": current_price
                        }
                        
                        if divergence_type == "none":
                            print(f"⚠️ No RSI divergence detected for {symbol} {tf}")
                    else:
                        print(f"⚠️ Insufficient RSI data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating RSI Divergence for {symbol}: {e}")
        return {}

def store_rsi_divergence_data(symbol_id, symbol, rsi_divergence_data):
    """Store RSI Divergence data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in rsi_divergence_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO rsi_divergence_data 
                (symbol_id, symbol, timeframe, divergence_type, divergence_strength,
                price_high_1, price_high_2, price_low_1, price_low_2,
                rsi_high_1, rsi_high_2, rsi_low_1, rsi_low_2,
                divergence_period, confirmation_level, signal_strength,
                trend_direction, momentum_shift, breakout_potential,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['divergence_type'], data['divergence_strength'],
                data['price_high_1'], data['price_high_2'], data['price_low_1'], data['price_low_2'],
                data['rsi_high_1'], data['rsi_high_2'], data['rsi_low_1'], data['rsi_low_2'],
                data['divergence_period'], data['confirmation_level'], data['signal_strength'],
                data['trend_direction'], data['momentum_shift'], data['breakout_potential'],
                data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing RSI Divergence data for {symbol}: {e}")
        return False

def generate_rsi_divergence_report():
    """Generate a comprehensive report of all RSI Divergence data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, divergence_type, divergence_strength,
                   confirmation_level, signal_strength, trend_direction,
                   momentum_shift, breakout_potential, current_price, last_updated
            FROM rsi_divergence_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No RSI Divergence data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 RSI DIVERGENCE COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine divergence emoji
            divergence_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(divergence_type, "⚪")
            
            # Determine confirmation emoji
            confirmation_emoji = {
                "confirmed": "✅",
                "partial": "⚠️",
                "pending": "⏳"
            }.get(confirmation_level, "⏳")
            
            # Determine trend emoji
            trend_emoji = {
                "bullish": "🟢",
                "potential_bullish": "🟡",
                "bearish": "🔴",
                "potential_bearish": "🟠",
                "neutral": "⚪"
            }.get(trend_direction, "⚪")
            
            # Determine momentum emoji
            momentum_emoji = {
                "strong_bullish": "🚀",
                "weak_bullish": "📈",
                "strong_bearish": "💥",
                "weak_bearish": "📉",
                "none": "➡️"
            }.get(momentum_shift, "➡️")
            
            # Determine breakout emoji
            breakout_emoji = {
                "high_bullish": "🚀",
                "moderate_bullish": "📈",
                "low_bullish": "🟢",
                "high_bearish": "💥",
                "moderate_bearish": "📉",
                "low_bearish": "🔴",
                "none": "⚪"
            }.get(breakout_potential, "⚪")
            
            print(f"  {timeframe:>4} | {divergence_emoji} {divergence_type:>8} | {confirmation_emoji} {confirmation_level:>9} | {trend_emoji} {trend_direction:>15} | {momentum_emoji} {momentum_shift:>12} | {breakout_emoji} {breakout_potential:>15} | Strength: {signal_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 RSI DIVERGENCE SUMMARY:")
        print("="*80)
        
        # Count by divergence type
        bullish_count = sum(1 for row in data if row[2] == "bullish")
        bearish_count = sum(1 for row in data if row[2] == "bearish")
        none_count = sum(1 for row in data if row[2] == "none")
        
        # Count by confirmation level
        confirmed_count = sum(1 for row in data if row[4] == "confirmed")
        partial_count = sum(1 for row in data if row[4] == "partial")
        pending_count = sum(1 for row in data if row[4] == "pending")
        
        # Count by trend direction
        bullish_trend_count = sum(1 for row in data if row[6] == "bullish")
        potential_bullish_count = sum(1 for row in data if row[6] == "potential_bullish")
        bearish_trend_count = sum(1 for row in data if row[6] == "bearish")
        potential_bearish_count = sum(1 for row in data if row[6] == "potential_bearish")
        neutral_trend_count = sum(1 for row in data if row[6] == "neutral")
        
        # Count by momentum shift
        strong_bullish_momentum_count = sum(1 for row in data if row[7] == "strong_bullish")
        weak_bullish_momentum_count = sum(1 for row in data if row[7] == "weak_bullish")
        strong_bearish_momentum_count = sum(1 for row in data if row[7] == "strong_bearish")
        weak_bearish_momentum_count = sum(1 for row in data if row[7] == "weak_bearish")
        no_momentum_count = sum(1 for row in data if row[7] == "none")
        
        # Count by breakout potential
        high_bullish_breakout_count = sum(1 for row in data if row[8] == "high_bullish")
        moderate_bullish_breakout_count = sum(1 for row in data if row[8] == "moderate_bullish")
        low_bullish_breakout_count = sum(1 for row in data if row[8] == "low_bullish")
        high_bearish_breakout_count = sum(1 for row in data if row[8] == "high_bearish")
        moderate_bearish_breakout_count = sum(1 for row in data if row[8] == "moderate_bearish")
        low_bearish_breakout_count = sum(1 for row in data if row[8] == "low_bearish")
        no_breakout_count = sum(1 for row in data if row[8] == "none")
        
        # Count strong signals
        strong_signals = sum(1 for row in data if row[5] > 50)
        moderate_signals = sum(1 for row in data if 20 < row[5] <= 50)
        weak_signals = sum(1 for row in data if row[5] <= 20)
        
        print(f"   🟢 Bullish Divergences: {bullish_count}")
        print(f"   🔴 Bearish Divergences: {bearish_count}")
        print(f"   ⚪ No Divergences: {none_count}")
        print(f"   ✅ Confirmed: {confirmed_count}")
        print(f"   ⚠️ Partial: {partial_count}")
        print(f"   ⏳ Pending: {pending_count}")
        print(f"   🟢 Bullish Trends: {bullish_trend_count}")
        print(f"   🟡 Potential Bullish: {potential_bullish_count}")
        print(f"   🔴 Bearish Trends: {bearish_trend_count}")
        print(f"   🟠 Potential Bearish: {potential_bearish_count}")
        print(f"   ⚪ Neutral Trends: {neutral_trend_count}")
        print(f"   🚀 Strong Bullish Momentum: {strong_bullish_momentum_count}")
        print(f"   📈 Weak Bullish Momentum: {weak_bullish_momentum_count}")
        print(f"   💥 Strong Bearish Momentum: {strong_bearish_momentum_count}")
        print(f"   📉 Weak Bearish Momentum: {weak_bearish_momentum_count}")
        print(f"   ➡️ No Momentum Shift: {no_momentum_count}")
        print(f"   🚀 High Bullish Breakout: {high_bullish_breakout_count}")
        print(f"   📈 Moderate Bullish Breakout: {moderate_bullish_breakout_count}")
        print(f"   🟢 Low Bullish Breakout: {low_bullish_breakout_count}")
        print(f"   💥 High Bearish Breakout: {high_bearish_breakout_count}")
        print(f"   📉 Moderate Bearish Breakout: {moderate_bearish_breakout_count}")
        print(f"   🔴 Low Bearish Breakout: {low_bearish_breakout_count}")
        print(f"   ⚪ No Breakout: {no_breakout_count}")
        print(f"   💪 Strong Signals (>50%): {strong_signals}")
        print(f"   📊 Moderate Signals (20-50%): {moderate_signals}")
        print(f"   🔸 Weak Signals (<20%): {weak_signals}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find confirmed bullish divergences
        confirmed_bullish = [row for row in data if row[2] == "bullish" and row[4] == "confirmed" and row[5] > 30]
        if confirmed_bullish:
            print("   🟢 Confirmed Bullish Divergences (Strong Buy Signals):")
            for divergence in confirmed_bullish:
                symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - {momentum_shift} momentum, {breakout_potential} breakout potential")
        else:
            print("   ✅ No confirmed bullish divergences detected")
        
        # Find confirmed bearish divergences
        confirmed_bearish = [row for row in data if row[2] == "bearish" and row[4] == "confirmed" and row[5] > 30]
        if confirmed_bearish:
            print("   🔴 Confirmed Bearish Divergences (Strong Sell Signals):")
            for divergence in confirmed_bearish:
                symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - {momentum_shift} momentum, {breakout_potential} breakout potential")
        else:
            print("   ✅ No confirmed bearish divergences detected")
        
        # Find partial bullish divergences
        partial_bullish = [row for row in data if row[2] == "bullish" and row[4] == "partial" and row[5] > 20]
        if partial_bullish:
            print("   🟡 Partial Bullish Divergences (Watch for Confirmation):")
            for divergence in partial_bullish:
                symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - {momentum_shift} momentum, {breakout_potential} breakout potential")
        else:
            print("   ✅ No partial bullish divergences detected")
        
        # Find partial bearish divergences
        partial_bearish = [row for row in data if row[2] == "bearish" and row[4] == "partial" and row[5] > 20]
        if partial_bearish:
            print("   🟠 Partial Bearish Divergences (Watch for Confirmation):")
            for divergence in partial_bearish:
                symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - {momentum_shift} momentum, {breakout_potential} breakout potential")
        else:
            print("   ✅ No partial bearish divergences detected")
        
        # Find high breakout potential
        high_breakout = [row for row in data if "high" in row[8] and row[5] > 40]
        if high_breakout:
            print("   🚀 High Breakout Potential (Strong Reversal Signals):")
            for divergence in high_breakout:
                symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: {breakout_potential} - Signal strength {signal_strength:.1f}%")
        else:
            print("   ✅ No high breakout potential detected")
        
        # Find strong momentum shifts
        strong_momentum = [row for row in data if "strong" in row[7] and row[5] > 30]
        if strong_momentum:
            print("   💪 Strong Momentum Shifts (Trend Reversal Indicators):")
            for divergence in strong_momentum:
                symbol, timeframe, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: {momentum_shift} - Signal strength {signal_strength:.1f}%")
        else:
            print("   ✅ No strong momentum shifts detected")
        
        print("\n" + "="*80)
        print("✅ RSI Divergence report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating RSI Divergence report: {e}")

def main():
    """Main function to populate RSI Divergence data"""
    print("🚀 Starting RSI Divergence data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store RSI Divergence for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        rsi_divergence_data = calculate_rsi_divergence_for_symbol(symbol, symbol_id)
        if rsi_divergence_data:
            if store_rsi_divergence_data(symbol_id, symbol, rsi_divergence_data):
                print(f"✅ Stored {len(rsi_divergence_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No RSI Divergence data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_rsi_divergence_report()

if __name__ == "__main__":
    main()
