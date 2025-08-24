#!/usr/bin/env python3
"""
Populate Moving Average Convergence Data
Calculates and stores Moving Average Convergence analysis for all symbols in My Symbols list
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

def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return None
    
    sma = np.mean(prices[-period:])
    return sma

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    alpha = 2 / (period + 1)
    ema = [prices[0]]
    
    for i in range(1, len(prices)):
        ema.append(alpha * prices[i] + (1 - alpha) * ema[i-1])
    
    return ema[-1]

def calculate_convergence_status(sma_10, sma_20, sma_50, sma_200, ema_12, ema_26):
    """Determine convergence status of moving averages"""
    # Calculate percentage differences between MAs
    ma_values = [sma_10, sma_20, sma_50, sma_200, ema_12, ema_26]
    ma_values = [v for v in ma_values if v is not None and v > 0]
    
    if len(ma_values) < 2:
        return "unknown", 0.0
    
    # Calculate average value
    avg_value = np.mean(ma_values)
    
    # Calculate maximum deviation from average
    max_deviation = max(abs(v - avg_value) for v in ma_values)
    
    # Calculate convergence percentage
    convergence_percentage = (1 - (max_deviation / avg_value)) * 100
    
    # Determine convergence status
    if convergence_percentage >= 95:
        return "strong_convergence", convergence_percentage
    elif convergence_percentage >= 90:
        return "moderate_convergence", convergence_percentage
    elif convergence_percentage >= 80:
        return "weak_convergence", convergence_percentage
    elif convergence_percentage >= 60:
        return "diverging", convergence_percentage
    else:
        return "strong_divergence", convergence_percentage

def determine_ma_alignment(sma_10, sma_20, sma_50, sma_200, ema_12, ema_26):
    """Determine moving average alignment"""
    ma_values = []
    ma_names = []
    
    if sma_10 is not None:
        ma_values.append(sma_10)
        ma_names.append("SMA10")
    if sma_20 is not None:
        ma_values.append(sma_20)
        ma_names.append("SMA20")
    if sma_50 is not None:
        ma_values.append(sma_50)
        ma_names.append("SMA50")
    if sma_200 is not None:
        ma_values.append(sma_200)
        ma_names.append("SMA200")
    if ema_12 is not None:
        ma_values.append(ema_12)
        ma_names.append("EMA12")
    if ema_26 is not None:
        ma_values.append(ema_26)
        ma_names.append("EMA26")
    
    if len(ma_values) < 2:
        return "unknown", 0.0
    
    # Check if all MAs are aligned (increasing or decreasing)
    is_increasing = all(ma_values[i] <= ma_values[i+1] for i in range(len(ma_values)-1))
    is_decreasing = all(ma_values[i] >= ma_values[i+1] for i in range(len(ma_values)-1))
    
    # Calculate alignment strength
    if is_increasing:
        # Calculate how well they're aligned in increasing order
        alignment_score = 0
        for i in range(len(ma_values)-1):
            if ma_values[i] <= ma_values[i+1]:
                alignment_score += 1
        alignment_strength = (alignment_score / (len(ma_values)-1)) * 100
        return "bullish_alignment", alignment_strength
    elif is_decreasing:
        # Calculate how well they're aligned in decreasing order
        alignment_score = 0
        for i in range(len(ma_values)-1):
            if ma_values[i] >= ma_values[i+1]:
                alignment_score += 1
        alignment_strength = (alignment_score / (len(ma_values)-1)) * 100
        return "bearish_alignment", alignment_strength
    else:
        # Mixed alignment
        return "mixed_alignment", 50.0

def detect_golden_cross(sma_50, sma_200, ema_12, ema_26):
    """Detect Golden Cross patterns"""
    golden_crosses = []
    
    # SMA 50 crossing above SMA 200
    if sma_50 is not None and sma_200 is not None:
        if sma_50 > sma_200:
            strength = ((sma_50 - sma_200) / sma_200) * 100
            golden_crosses.append(("sma_golden_cross", strength))
    
    # EMA 12 crossing above EMA 26
    if ema_12 is not None and ema_26 is not None:
        if ema_12 > ema_26:
            strength = ((ema_12 - ema_26) / ema_26) * 100
            golden_crosses.append(("ema_golden_cross", strength))
    
    if golden_crosses:
        # Return the strongest golden cross
        strongest = max(golden_crosses, key=lambda x: x[1])
        return strongest[0], strongest[1]
    else:
        return "none", 0.0

def detect_death_cross(sma_50, sma_200, ema_12, ema_26):
    """Detect Death Cross patterns"""
    death_crosses = []
    
    # SMA 50 crossing below SMA 200
    if sma_50 is not None and sma_200 is not None:
        if sma_50 < sma_200:
            strength = ((sma_200 - sma_50) / sma_50) * 100
            death_crosses.append(("sma_death_cross", strength))
    
    # EMA 12 crossing below EMA 26
    if ema_12 is not None and ema_26 is not None:
        if ema_12 < ema_26:
            strength = ((ema_26 - ema_12) / ema_12) * 100
            death_crosses.append(("ema_death_cross", strength))
    
    if death_crosses:
        # Return the strongest death cross
        strongest = max(death_crosses, key=lambda x: x[1])
        return strongest[0], strongest[1]
    else:
        return "none", 0.0

def determine_trend_direction(sma_10, sma_20, sma_50, sma_200, ema_12, ema_26, current_price):
    """Determine overall trend direction"""
    ma_values = []
    
    if sma_10 is not None:
        ma_values.append(sma_10)
    if sma_20 is not None:
        ma_values.append(sma_20)
    if sma_50 is not None:
        ma_values.append(sma_50)
    if sma_200 is not None:
        ma_values.append(sma_200)
    if ema_12 is not None:
        ma_values.append(ema_12)
    if ema_26 is not None:
        ma_values.append(ema_26)
    
    if not ma_values:
        return "unknown", 0.0
    
    # Calculate average MA value
    avg_ma = np.mean(ma_values)
    
    # Determine trend based on current price vs average MA
    if current_price > avg_ma * 1.05:
        trend_strength = ((current_price - avg_ma) / avg_ma) * 100
        return "strong_bullish", trend_strength
    elif current_price > avg_ma * 1.02:
        trend_strength = ((current_price - avg_ma) / avg_ma) * 100
        return "bullish", trend_strength
    elif current_price < avg_ma * 0.95:
        trend_strength = ((avg_ma - current_price) / avg_ma) * 100
        return "strong_bearish", trend_strength
    elif current_price < avg_ma * 0.98:
        trend_strength = ((avg_ma - current_price) / avg_ma) * 100
        return "bearish", trend_strength
    else:
        return "neutral", 0.0

def calculate_support_resistance_levels(sma_10, sma_20, sma_50, sma_200, ema_12, ema_26):
    """Calculate support and resistance levels from MAs"""
    ma_values = []
    
    if sma_10 is not None:
        ma_values.append(sma_10)
    if sma_20 is not None:
        ma_values.append(sma_20)
    if sma_50 is not None:
        ma_values.append(sma_50)
    if sma_200 is not None:
        ma_values.append(sma_200)
    if ema_12 is not None:
        ma_values.append(ema_12)
    if ema_26 is not None:
        ma_values.append(ema_26)
    
    if not ma_values:
        return "No levels available"
    
    # Sort MAs to find support and resistance
    ma_values.sort()
    
    # Support levels (lower MAs)
    support_levels = ma_values[:3]  # Take 3 lowest MAs
    
    # Resistance levels (higher MAs)
    resistance_levels = ma_values[-3:]  # Take 3 highest MAs
    
    support_str = ", ".join([f"${level:.4f}" for level in support_levels])
    resistance_str = ", ".join([f"${level:.4f}" for level in resistance_levels])
    
    return f"Support: {support_str} | Resistance: {resistance_str}"

def determine_breakout_potential(current_price, sma_10, sma_20, sma_50, sma_200, ema_12, ema_26):
    """Determine breakout potential based on price position relative to MAs"""
    ma_values = []
    
    if sma_10 is not None:
        ma_values.append(sma_10)
    if sma_20 is not None:
        ma_values.append(sma_20)
    if sma_50 is not None:
        ma_values.append(sma_50)
    if sma_200 is not None:
        ma_values.append(sma_200)
    if ema_12 is not None:
        ma_values.append(ema_12)
    if ema_26 is not None:
        ma_values.append(ema_26)
    
    if not ma_values:
        return "none", 0.0
    
    # Calculate how many MAs price is above/below
    above_count = sum(1 for ma in ma_values if current_price > ma)
    below_count = sum(1 for ma in ma_values if current_price < ma)
    total_mas = len(ma_values)
    
    # Calculate breakout strength
    if above_count == total_mas:
        # Price above all MAs - strong bullish breakout
        strength = (above_count / total_mas) * 100
        return "strong_bullish_breakout", strength
    elif above_count >= total_mas * 0.8:
        # Price above most MAs - moderate bullish breakout
        strength = (above_count / total_mas) * 100
        return "moderate_bullish_breakout", strength
    elif below_count == total_mas:
        # Price below all MAs - strong bearish breakout
        strength = (below_count / total_mas) * 100
        return "strong_bearish_breakout", strength
    elif below_count >= total_mas * 0.8:
        # Price below most MAs - moderate bearish breakout
        strength = (below_count / total_mas) * 100
        return "moderate_bearish_breakout", strength
    else:
        # Price mixed relative to MAs - no clear breakout
        return "none", 0.0

def determine_volume_confirmation(volumes, trend_direction, periods=5):
    """Determine volume confirmation for trend"""
    if len(volumes) < periods:
        return "none", 0.0
    
    recent_volumes = volumes[-periods:]
    avg_volume = np.mean(recent_volumes[:-1])  # Exclude current volume
    current_volume = recent_volumes[-1]
    
    if avg_volume == 0:
        return "none", 0.0
    
    volume_ratio = current_volume / avg_volume
    
    # Determine confirmation based on trend and volume
    if trend_direction in ["strong_bullish", "bullish"]:
        if volume_ratio > 1.5:
            return "strong_bullish", volume_ratio * 100
        elif volume_ratio > 1.2:
            return "moderate_bullish", volume_ratio * 100
        elif volume_ratio > 1.0:
            return "weak_bullish", volume_ratio * 100
        else:
            return "none", volume_ratio * 100
    elif trend_direction in ["strong_bearish", "bearish"]:
        if volume_ratio > 1.5:
            return "strong_bearish", volume_ratio * 100
        elif volume_ratio > 1.2:
            return "moderate_bearish", volume_ratio * 100
        elif volume_ratio > 1.0:
            return "weak_bearish", volume_ratio * 100
        else:
            return "none", volume_ratio * 100
    else:
        return "none", volume_ratio * 100

def calculate_ma_convergence_for_symbol(symbol, symbol_id):
    """Calculate Moving Average Convergence for all timeframes for a symbol"""
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
                
                # Extract OHLCV data
                closes = [float(kline[4]) for kline in klines_data]
                volumes = [float(kline[5]) for kline in klines_data]
                
                if len(closes) >= 200:  # Need enough data for all MAs
                    # Calculate all moving averages
                    sma_10 = calculate_sma(closes, 10)
                    sma_20 = calculate_sma(closes, 20)
                    sma_50 = calculate_sma(closes, 50)
                    sma_200 = calculate_sma(closes, 200)
                    ema_12 = calculate_ema(closes, 12)
                    ema_26 = calculate_ema(closes, 26)
                    
                    if all(ma is not None for ma in [sma_10, sma_20, sma_50, sma_200, ema_12, ema_26]):
                        # Calculate convergence metrics
                        convergence_status, convergence_strength = calculate_convergence_status(
                            sma_10, sma_20, sma_50, sma_200, ema_12, ema_26
                        )
                        
                        ma_alignment, alignment_strength = determine_ma_alignment(
                            sma_10, sma_20, sma_50, sma_200, ema_12, ema_26
                        )
                        
                        # Detect crossovers
                        golden_cross_detected, golden_cross_strength = detect_golden_cross(
                            sma_50, sma_200, ema_12, ema_26
                        )
                        
                        death_cross_detected, death_cross_strength = detect_death_cross(
                            sma_50, sma_200, ema_12, ema_26
                        )
                        
                        # Determine trend
                        trend_direction, trend_strength = determine_trend_direction(
                            sma_10, sma_20, sma_50, sma_200, ema_12, ema_26, current_price
                        )
                        
                        # Calculate support/resistance levels
                        support_resistance_levels = calculate_support_resistance_levels(
                            sma_10, sma_20, sma_50, sma_200, ema_12, ema_26
                        )
                        
                        # Determine breakout potential
                        breakout_potential, breakout_strength = determine_breakout_potential(
                            current_price, sma_10, sma_20, sma_50, sma_200, ema_12, ema_26
                        )
                        
                        # Determine volume confirmation
                        volume_confirmation, volume_strength = determine_volume_confirmation(
                            volumes, trend_direction
                        )
                        
                        results[tf] = {
                            "sma_10": sma_10,
                            "sma_20": sma_20,
                            "sma_50": sma_50,
                            "sma_200": sma_200,
                            "ema_12": ema_12,
                            "ema_26": ema_26,
                            "convergence_status": convergence_status,
                            "convergence_strength": convergence_strength,
                            "ma_alignment": ma_alignment,
                            "alignment_strength": alignment_strength,
                            "golden_cross_detected": golden_cross_detected,
                            "golden_cross_strength": golden_cross_strength,
                            "death_cross_detected": death_cross_detected,
                            "death_cross_strength": death_cross_strength,
                            "trend_direction": trend_direction,
                            "trend_strength": trend_strength,
                            "support_resistance_levels": support_resistance_levels,
                            "breakout_potential": breakout_potential,
                            "breakout_strength": breakout_strength,
                            "volume_confirmation": volume_confirmation,
                            "volume_strength": volume_strength,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate all MAs for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Moving Average Convergence for {symbol}: {e}")
        return {}

def store_ma_convergence_data(symbol_id, symbol, ma_convergence_data):
    """Store Moving Average Convergence data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in ma_convergence_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO ma_convergence_data 
                (symbol_id, symbol, timeframe, sma_10, sma_20, sma_50, sma_200,
                ema_12, ema_26, convergence_status, convergence_strength, ma_alignment,
                alignment_strength, golden_cross_detected, golden_cross_strength,
                death_cross_detected, death_cross_strength, trend_direction, trend_strength,
                support_resistance_levels, breakout_potential, breakout_strength,
                volume_confirmation, volume_strength, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['sma_10'], data['sma_20'],
                data['sma_50'], data['sma_200'], data['ema_12'], data['ema_26'],
                data['convergence_status'], data['convergence_strength'], data['ma_alignment'],
                data['alignment_strength'], data['golden_cross_detected'], data['golden_cross_strength'],
                data['death_cross_detected'], data['death_cross_strength'], data['trend_direction'],
                data['trend_strength'], data['support_resistance_levels'], data['breakout_potential'],
                data['breakout_strength'], data['volume_confirmation'], data['volume_strength'],
                data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Moving Average Convergence data for {symbol}: {e}")
        return False

def generate_ma_convergence_report():
    """Generate a comprehensive report of all Moving Average Convergence data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, convergence_status, convergence_strength, ma_alignment,
                   alignment_strength, golden_cross_detected, death_cross_detected,
                   trend_direction, trend_strength, breakout_potential, volume_confirmation,
                   current_price, last_updated
            FROM ma_convergence_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Moving Average Convergence data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 MOVING AVERAGE CONVERGENCE COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine convergence emoji
            convergence_emoji = {
                "strong_convergence": "🔒",
                "moderate_convergence": "📏",
                "weak_convergence": "📊",
                "diverging": "📈",
                "strong_divergence": "💥",
                "unknown": "❓"
            }.get(convergence_status, "❓")
            
            # Determine alignment emoji
            alignment_emoji = {
                "bullish_alignment": "📈",
                "bearish_alignment": "📉",
                "mixed_alignment": "➡️",
                "unknown": "❓"
            }.get(ma_alignment, "❓")
            
            # Determine golden cross emoji
            golden_cross_emoji = {
                "sma_golden_cross": "🟢",
                "ema_golden_cross": "🟢",
                "none": "⚪"
            }.get(golden_cross_detected, "⚪")
            
            # Determine death cross emoji
            death_cross_emoji = {
                "sma_death_cross": "🔴",
                "ema_death_cross": "🔴",
                "none": "⚪"
            }.get(death_cross_detected, "⚪")
            
            # Determine trend emoji
            trend_emoji = {
                "strong_bullish": "🚀",
                "bullish": "📈",
                "neutral": "➡️",
                "bearish": "📉",
                "strong_bearish": "💥",
                "unknown": "❓"
            }.get(trend_direction, "❓")
            
            # Determine breakout emoji
            breakout_emoji = {
                "strong_bullish_breakout": "🚀",
                "moderate_bullish_breakout": "📈",
                "strong_bearish_breakout": "💥",
                "moderate_bearish_breakout": "📉",
                "none": "⚪"
            }.get(breakout_potential, "⚪")
            
            # Determine volume emoji
            volume_emoji = {
                "strong_bullish": "📊",
                "moderate_bullish": "📈",
                "weak_bullish": "📈",
                "strong_bearish": "📊",
                "moderate_bearish": "📉",
                "weak_bearish": "📉",
                "none": "➡️"
            }.get(volume_confirmation, "➡️")
            
            print(f"  {timeframe:>4} | {convergence_emoji} {convergence_status:>20} | {alignment_emoji} {ma_alignment:>15} | {golden_cross_emoji} {golden_cross_detected:>15} | {death_cross_emoji} {death_cross_detected:>15} | {trend_emoji} {trend_direction:>15} | {breakout_emoji} {breakout_potential:>20} | {volume_emoji} {volume_confirmation:>15} | Conv: {convergence_strength:>5.1f}% | Align: {alignment_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 MOVING AVERAGE CONVERGENCE SUMMARY:")
        print("="*80)
        
        # Count by convergence status
        strong_convergence_count = sum(1 for row in data if row[2] == "strong_convergence")
        moderate_convergence_count = sum(1 for row in data if row[2] == "moderate_convergence")
        weak_convergence_count = sum(1 for row in data if row[2] == "weak_convergence")
        diverging_count = sum(1 for row in data if row[2] == "diverging")
        strong_divergence_count = sum(1 for row in data if row[2] == "strong_divergence")
        unknown_count = sum(1 for row in data if row[2] == "unknown")
        
        print(f"   🔒 Strong Convergence: {strong_convergence_count}")
        print(f"   📏 Moderate Convergence: {moderate_convergence_count}")
        print(f"   📊 Weak Convergence: {weak_convergence_count}")
        print(f"   📈 Diverging: {diverging_count}")
        print(f"   💥 Strong Divergence: {strong_divergence_count}")
        print(f"   ❓ Unknown: {unknown_count}")
        
        # Count by MA alignment
        bullish_alignment_count = sum(1 for row in data if row[4] == "bullish_alignment")
        bearish_alignment_count = sum(1 for row in data if row[4] == "bearish_alignment")
        mixed_alignment_count = sum(1 for row in data if row[4] == "mixed_alignment")
        unknown_alignment_count = sum(1 for row in data if row[4] == "unknown")
        
        print(f"   📈 Bullish Alignment: {bullish_alignment_count}")
        print(f"   📉 Bearish Alignment: {bearish_alignment_count}")
        print(f"   ➡️ Mixed Alignment: {mixed_alignment_count}")
        print(f"   ❓ Unknown Alignment: {unknown_alignment_count}")
        
        # Count golden crosses
        sma_golden_cross_count = sum(1 for row in data if row[6] == "sma_golden_cross")
        ema_golden_cross_count = sum(1 for row in data if row[6] == "ema_golden_cross")
        no_golden_cross_count = sum(1 for row in data if row[6] == "none")
        
        print(f"   🟢 SMA Golden Cross: {sma_golden_cross_count}")
        print(f"   🟢 EMA Golden Cross: {ema_golden_cross_count}")
        print(f"   ⚪ No Golden Cross: {no_golden_cross_count}")
        
        # Count death crosses
        sma_death_cross_count = sum(1 for row in data if row[7] == "sma_death_cross")
        ema_death_cross_count = sum(1 for row in data if row[7] == "ema_death_cross")
        no_death_cross_count = sum(1 for row in data if row[7] == "none")
        
        print(f"   🔴 SMA Death Cross: {sma_death_cross_count}")
        print(f"   🔴 EMA Death Cross: {ema_death_cross_count}")
        print(f"   ⚪ No Death Cross: {no_death_cross_count}")
        
        # Count trend directions
        strong_bullish_trend_count = sum(1 for row in data if row[8] == "strong_bullish")
        bullish_trend_count = sum(1 for row in data if row[8] == "bullish")
        neutral_trend_count = sum(1 for row in data if row[8] == "neutral")
        bearish_trend_count = sum(1 for row in data if row[8] == "bearish")
        strong_bearish_trend_count = sum(1 for row in data if row[8] == "strong_bearish")
        unknown_trend_count = sum(1 for row in data if row[8] == "unknown")
        
        print(f"   🚀 Strong Bullish Trend: {strong_bullish_trend_count}")
        print(f"   📈 Bullish Trend: {bullish_trend_count}")
        print(f"   ➡️ Neutral Trend: {neutral_trend_count}")
        print(f"   📉 Bearish Trend: {bearish_trend_count}")
        print(f"   💥 Strong Bearish Trend: {strong_bearish_trend_count}")
        print(f"   ❓ Unknown Trend: {unknown_trend_count}")
        
        # Count breakout potentials
        strong_bullish_breakout_count = sum(1 for row in data if row[10] == "strong_bullish_breakout")
        moderate_bullish_breakout_count = sum(1 for row in data if row[10] == "moderate_bullish_breakout")
        strong_bearish_breakout_count = sum(1 for row in data if row[10] == "strong_bearish_breakout")
        moderate_bearish_breakout_count = sum(1 for row in data if row[10] == "moderate_bearish_breakout")
        no_breakout_count = sum(1 for row in data if row[10] == "none")
        
        print(f"   🚀 Strong Bullish Breakout: {strong_bullish_breakout_count}")
        print(f"   📈 Moderate Bullish Breakout: {moderate_bullish_breakout_count}")
        print(f"   💥 Strong Bearish Breakout: {strong_bearish_breakout_count}")
        print(f"   📉 Moderate Bearish Breakout: {moderate_bearish_breakout_count}")
        print(f"   ⚪ No Breakout: {no_breakout_count}")
        
        # Count volume confirmations
        strong_bullish_volume_count = sum(1 for row in data if row[11] == "strong_bullish")
        moderate_bullish_volume_count = sum(1 for row in data if row[11] == "moderate_bullish")
        weak_bullish_volume_count = sum(1 for row in data if row[11] == "weak_bullish")
        strong_bearish_volume_count = sum(1 for row in data if row[11] == "strong_bearish")
        moderate_bearish_volume_count = sum(1 for row in data if row[11] == "moderate_bearish")
        weak_bearish_volume_count = sum(1 for row in data if row[11] == "weak_bearish")
        no_volume_count = sum(1 for row in data if row[11] == "none")
        
        print(f"   📊 Strong Bullish Volume: {strong_bullish_volume_count}")
        print(f"   📈 Moderate Bullish Volume: {moderate_bullish_volume_count}")
        print(f"   📈 Weak Bullish Volume: {weak_bullish_volume_count}")
        print(f"   📊 Strong Bearish Volume: {strong_bearish_volume_count}")
        print(f"   📉 Moderate Bearish Volume: {moderate_bearish_volume_count}")
        print(f"   📉 Weak Bearish Volume: {weak_bearish_volume_count}")
        print(f"   ➡️ No Volume: {no_volume_count}")
        
        # Count strong convergences
        strong_convergences = sum(1 for row in data if row[3] > 70)
        moderate_convergences = sum(1 for row in data if 40 < row[3] <= 70)
        weak_convergences = sum(1 for row in data if row[3] <= 40)
        
        print(f"   💪 Strong Convergences (>70%): {strong_convergences}")
        print(f"   📊 Moderate Convergences (40-70%): {moderate_convergences}")
        print(f"   🔸 Weak Convergences (<40%): {weak_convergences}")
        
        # Count strong alignments
        strong_alignments = sum(1 for row in data if row[5] > 70)
        moderate_alignments = sum(1 for row in data if 40 < row[5] <= 70)
        weak_alignments = sum(1 for row in data if row[5] <= 40)
        
        print(f"   💪 Strong Alignments (>70%): {strong_alignments}")
        print(f"   📊 Moderate Alignments (40-70%): {moderate_alignments}")
        print(f"   🔸 Weak Alignments (<40%): {weak_alignments}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong convergences
        strong_convergence = [row for row in data if row[2] in ["strong_convergence", "moderate_convergence"] and row[3] > 60]
        if strong_convergence:
            print("   🔒 Strong Convergence Signals (Trend Continuation):")
            for conv in strong_convergence:
                symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = conv
                print(f"      • {symbol} {timeframe}: {convergence_status} - Strength {convergence_strength:.1f}%, Alignment {ma_alignment}")
        else:
            print("   ✅ No strong convergence signals detected")
        
        # Find golden crosses
        golden_crosses = [row for row in data if row[6] != "none" and row[3] > 30]
        if golden_crosses:
            print("   🟢 Golden Cross Signals (Bullish Trend Change):")
            for cross in golden_crosses:
                symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = cross
                print(f"      • {symbol} {timeframe}: {golden_cross_detected} - Strength {convergence_strength:.1f}%")
        else:
            print("   ✅ No golden cross signals detected")
        
        # Find death crosses
        death_crosses = [row for row in data if row[7] != "none" and row[3] > 30]
        if death_crosses:
            print("   🔴 Death Cross Signals (Bearish Trend Change):")
            for cross in death_crosses:
                symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = cross
                print(f"      • {symbol} {timeframe}: {death_cross_detected} - Strength {convergence_strength:.1f}%")
        else:
            print("   ✅ No death cross signals detected")
        
        # Find strong breakouts
        strong_breakouts = [row for row in data if "strong" in row[10] and row[3] > 50]
        if strong_breakouts:
            print("   🚀 Strong Breakout Signals (Price vs MAs):")
            for breakout in strong_breakouts:
                symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = breakout
                print(f"      • {symbol} {timeframe}: {breakout_potential} - Strength {convergence_strength:.1f}%")
        else:
            print("   ✅ No strong breakout signals detected")
        
        # Find strong alignments
        strong_alignments = [row for row in data if row[4] in ["bullish_alignment", "bearish_alignment"] and row[5] > 70]
        if strong_alignments:
            print("   📊 Strong Alignment Signals (MA Direction):")
            for align in strong_alignments:
                symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = align
                print(f"      • {symbol} {timeframe}: {ma_alignment} - Strength {alignment_strength:.1f}%")
        else:
            print("   ✅ No strong alignment signals detected")
        
        # Find strong volume confirmations
        strong_volume = [row for row in data if "strong" in row[11] and row[3] > 30]
        if strong_volume:
            print("   📊 Strong Volume Confirmations:")
            for volume in strong_volume:
                symbol, timeframe, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation, current_price, last_updated = volume
                print(f"      • {symbol} {timeframe}: {volume_confirmation} volume - Trend {trend_direction}, Convergence {convergence_strength:.1f}%")
        else:
            print("   ✅ No strong volume confirmations detected")
        
        print("\n" + "="*80)
        print("✅ Moving Average Convergence report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Moving Average Convergence report: {e}")

def main():
    """Main function to populate Moving Average Convergence data"""
    print("🚀 Starting Moving Average Convergence data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Moving Average Convergence for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        ma_convergence_data = calculate_ma_convergence_for_symbol(symbol, symbol_id)
        if ma_convergence_data:
            if store_ma_convergence_data(symbol_id, symbol, ma_convergence_data):
                print(f"✅ Stored {len(ma_convergence_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Moving Average Convergence data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_ma_convergence_report()

if __name__ == "__main__":
    main()
