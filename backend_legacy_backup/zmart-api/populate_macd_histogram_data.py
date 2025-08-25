#!/usr/bin/env python3
"""
Populate MACD Histogram Data
Calculates and stores MACD Histogram analysis for all symbols in My Symbols list
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

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    alpha = 2 / (period + 1)
    ema = [prices[0]]
    
    for i in range(1, len(prices)):
        ema.append(alpha * prices[i] + (1 - alpha) * ema[i-1])
    
    return ema

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """Calculate MACD, Signal Line, and Histogram"""
    if len(prices) < slow_period + signal_period:
        return None, None, None
    
    # Calculate fast and slow EMAs
    fast_ema = calculate_ema(prices, fast_period)
    slow_ema = calculate_ema(prices, slow_period)
    
    if fast_ema is None or slow_ema is None:
        return None, None, None
    
    # Calculate MACD line
    macd_line = []
    for i in range(len(prices)):
        if i >= slow_period - 1:
            macd_line.append(fast_ema[i] - slow_ema[i])
        else:
            macd_line.append(0)
    
    # Calculate Signal line (EMA of MACD)
    signal_line = calculate_ema(macd_line, signal_period)
    
    if signal_line is None:
        return None, None, None
    
    # Calculate Histogram
    histogram = []
    for i in range(len(macd_line)):
        if i >= signal_period - 1:
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(0)
    
    return macd_line, signal_line, histogram

def calculate_histogram_change(histogram):
    """Calculate histogram change from previous period"""
    if len(histogram) < 2:
        return 0.0
    
    current = histogram[-1]
    previous = histogram[-2]
    
    if previous == 0:
        return 0.0
    
    return ((current - previous) / abs(previous)) * 100

def determine_histogram_trend(histogram, periods=3):
    """Determine histogram trend direction"""
    if len(histogram) < periods:
        return "neutral"
    
    recent_histogram = histogram[-periods:]
    
    # Check if all recent values are positive and increasing
    if all(h > 0 for h in recent_histogram) and all(recent_histogram[i] >= recent_histogram[i-1] for i in range(1, len(recent_histogram))):
        return "strong_bullish"
    # Check if all recent values are negative and decreasing
    elif all(h < 0 for h in recent_histogram) and all(recent_histogram[i] <= recent_histogram[i-1] for i in range(1, len(recent_histogram))):
        return "strong_bearish"
    # Check if recent values are positive
    elif all(h > 0 for h in recent_histogram):
        return "bullish"
    # Check if recent values are negative
    elif all(h < 0 for h in recent_histogram):
        return "bearish"
    else:
        return "neutral"

def calculate_histogram_strength(histogram, periods=5):
    """Calculate histogram strength based on recent values"""
    if len(histogram) < periods:
        return 0.0
    
    recent_histogram = histogram[-periods:]
    
    # Calculate average absolute value
    avg_abs = np.mean([abs(h) for h in recent_histogram])
    
    # Calculate trend consistency
    positive_count = sum(1 for h in recent_histogram if h > 0)
    negative_count = sum(1 for h in recent_histogram if h < 0)
    
    # Determine dominant direction
    if positive_count > negative_count:
        dominant_direction = 1
    elif negative_count > positive_count:
        dominant_direction = -1
    else:
        dominant_direction = 0
    
    # Calculate strength based on consistency and magnitude
    consistency = max(positive_count, negative_count) / periods
    strength = consistency * avg_abs * 100
    
    return min(strength, 100.0)

def detect_zero_line_cross(histogram):
    """Detect zero line crossovers"""
    if len(histogram) < 2:
        return "none", 0.0
    
    current = histogram[-1]
    previous = histogram[-2]
    
    # Bullish crossover (negative to positive)
    if previous < 0 and current > 0:
        strength = abs(current) * 100
        return "bullish", strength
    # Bearish crossover (positive to negative)
    elif previous > 0 and current < 0:
        strength = abs(current) * 100
        return "bearish", strength
    else:
        return "none", 0.0

def detect_signal_cross(macd_line, signal_line):
    """Detect MACD line and signal line crossovers"""
    if len(macd_line) < 2 or len(signal_line) < 2:
        return "none", 0.0
    
    current_macd = macd_line[-1]
    previous_macd = macd_line[-2]
    current_signal = signal_line[-1]
    previous_signal = signal_line[-2]
    
    # Bullish crossover (MACD crosses above signal)
    if previous_macd <= previous_signal and current_macd > current_signal:
        strength = abs(current_macd - current_signal) * 100
        return "bullish", strength
    # Bearish crossover (MACD crosses below signal)
    elif previous_macd >= previous_signal and current_macd < current_signal:
        strength = abs(current_macd - current_signal) * 100
        return "bearish", strength
    else:
        return "none", 0.0

def detect_divergence(prices, histogram, periods=10):
    """Detect price vs histogram divergence"""
    if len(prices) < periods or len(histogram) < periods:
        return "none", 0.0
    
    # Get recent data
    recent_prices = prices[-periods:]
    recent_histogram = histogram[-periods:]
    
    # Calculate price trend
    price_trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
    
    # Calculate histogram trend
    histogram_trend = (recent_histogram[-1] - recent_histogram[0])
    
    # Detect divergence
    if price_trend > 0.02 and histogram_trend < -0.001:  # Price up, histogram down
        strength = abs(price_trend) * 100
        return "bearish", strength
    elif price_trend < -0.02 and histogram_trend > 0.001:  # Price down, histogram up
        strength = abs(price_trend) * 100
        return "bullish", strength
    else:
        return "none", 0.0

def detect_momentum_shift(histogram, periods=5):
    """Detect momentum shift in histogram"""
    if len(histogram) < periods:
        return "none", 0.0
    
    recent_histogram = histogram[-periods:]
    
    # Calculate momentum change
    first_half = recent_histogram[:periods//2]
    second_half = recent_histogram[periods//2:]
    
    first_momentum = np.mean(first_half)
    second_momentum = np.mean(second_half)
    
    momentum_change = second_momentum - first_momentum
    
    if momentum_change > 0.001:
        strength = abs(momentum_change) * 100
        return "bullish", strength
    elif momentum_change < -0.001:
        strength = abs(momentum_change) * 100
        return "bearish", strength
    else:
        return "none", 0.0

def detect_histogram_pattern(histogram, periods=5):
    """Detect histogram patterns"""
    if len(histogram) < periods:
        return "none", 0.0
    
    recent_histogram = histogram[-periods:]
    
    # Double bottom pattern (two consecutive lows)
    if len(recent_histogram) >= 4:
        if (recent_histogram[-4] > recent_histogram[-3] and 
            recent_histogram[-3] < recent_histogram[-2] and 
            recent_histogram[-2] > recent_histogram[-1] and
            recent_histogram[-1] < recent_histogram[-2]):
            strength = abs(recent_histogram[-1]) * 100
            return "double_bottom", strength
    
    # Double top pattern (two consecutive highs)
    if len(recent_histogram) >= 4:
        if (recent_histogram[-4] < recent_histogram[-3] and 
            recent_histogram[-3] > recent_histogram[-2] and 
            recent_histogram[-2] < recent_histogram[-1] and
            recent_histogram[-1] > recent_histogram[-2]):
            strength = abs(recent_histogram[-1]) * 100
            return "double_top", strength
    
    # Bullish divergence (lower lows in histogram while price makes higher lows)
    if len(recent_histogram) >= 3:
        if (recent_histogram[-3] > recent_histogram[-2] and 
            recent_histogram[-2] < recent_histogram[-1] and
            recent_histogram[-1] > recent_histogram[-2]):
            strength = abs(recent_histogram[-1]) * 100
            return "bullish_divergence", strength
    
    # Bearish divergence (higher highs in histogram while price makes lower highs)
    if len(recent_histogram) >= 3:
        if (recent_histogram[-3] < recent_histogram[-2] and 
            recent_histogram[-2] > recent_histogram[-1] and
            recent_histogram[-1] < recent_histogram[-2]):
            strength = abs(recent_histogram[-1]) * 100
            return "bearish_divergence", strength
    
    return "none", 0.0

def determine_volume_confirmation(volumes, histogram_trend, periods=5):
    """Determine volume confirmation for histogram trend"""
    if len(volumes) < periods:
        return "none", 0.0
    
    recent_volumes = volumes[-periods:]
    avg_volume = np.mean(recent_volumes[:-1])  # Exclude current volume
    current_volume = recent_volumes[-1]
    
    if avg_volume == 0:
        return "none", 0.0
    
    volume_ratio = current_volume / avg_volume
    
    # Determine confirmation based on trend and volume
    if histogram_trend in ["strong_bullish", "bullish"]:
        if volume_ratio > 1.5:
            return "strong_bullish", volume_ratio * 100
        elif volume_ratio > 1.2:
            return "moderate_bullish", volume_ratio * 100
        elif volume_ratio > 1.0:
            return "weak_bullish", volume_ratio * 100
        else:
            return "none", volume_ratio * 100
    elif histogram_trend in ["strong_bearish", "bearish"]:
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

def calculate_macd_histogram_for_symbol(symbol, symbol_id):
    """Calculate MACD Histogram for all timeframes for a symbol"""
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
                    "15m": 100,
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
                
                # Extract OHLCV data
                closes = [float(kline[4]) for kline in klines_data]
                volumes = [float(kline[5]) for kline in klines_data]
                
                if len(closes) >= 50:  # Need enough data for MACD calculation
                    # Calculate MACD components
                    macd_line, signal_line, histogram = calculate_macd(closes, 12, 26, 9)
                    
                    if macd_line is not None and signal_line is not None and histogram is not None:
                        # Calculate histogram metrics
                        histogram_change = calculate_histogram_change(histogram)
                        histogram_trend = determine_histogram_trend(histogram)
                        histogram_strength = calculate_histogram_strength(histogram)
                        
                        # Detect crossovers
                        zero_line_cross, zero_line_cross_strength = detect_zero_line_cross(histogram)
                        signal_cross, signal_cross_strength = detect_signal_cross(macd_line, signal_line)
                        
                        # Detect divergences and patterns
                        divergence_type, divergence_strength = detect_divergence(closes, histogram)
                        momentum_shift, momentum_strength = detect_momentum_shift(histogram)
                        histogram_pattern, pattern_strength = detect_histogram_pattern(histogram)
                        
                        # Determine volume confirmation
                        volume_confirmation, volume_strength = determine_volume_confirmation(volumes, histogram_trend)
                        
                        results[tf] = {
                            "macd_line": macd_line[-1],
                            "signal_line": signal_line[-1],
                            "histogram_value": histogram[-1],
                            "histogram_change": histogram_change,
                            "histogram_trend": histogram_trend,
                            "histogram_strength": histogram_strength,
                            "zero_line_cross": zero_line_cross,
                            "zero_line_cross_strength": zero_line_cross_strength,
                            "signal_cross": signal_cross,
                            "signal_cross_strength": signal_cross_strength,
                            "divergence_type": divergence_type,
                            "divergence_strength": divergence_strength,
                            "momentum_shift": momentum_shift,
                            "momentum_strength": momentum_strength,
                            "histogram_pattern": histogram_pattern,
                            "pattern_strength": pattern_strength,
                            "volume_confirmation": volume_confirmation,
                            "volume_strength": volume_strength,
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
        print(f"❌ Error calculating MACD Histogram for {symbol}: {e}")
        return {}

def store_macd_histogram_data(symbol_id, symbol, macd_histogram_data):
    """Store MACD Histogram data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in macd_histogram_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO macd_histogram_data 
                (symbol_id, symbol, timeframe, macd_line, signal_line, histogram_value,
                histogram_change, histogram_trend, histogram_strength, zero_line_cross,
                zero_line_cross_strength, signal_cross, signal_cross_strength,
                divergence_type, divergence_strength, momentum_shift, momentum_strength,
                histogram_pattern, pattern_strength, volume_confirmation, volume_strength,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['macd_line'], data['signal_line'],
                data['histogram_value'], data['histogram_change'], data['histogram_trend'],
                data['histogram_strength'], data['zero_line_cross'], data['zero_line_cross_strength'],
                data['signal_cross'], data['signal_cross_strength'], data['divergence_type'],
                data['divergence_strength'], data['momentum_shift'], data['momentum_strength'],
                data['histogram_pattern'], data['pattern_strength'], data['volume_confirmation'],
                data['volume_strength'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing MACD Histogram data for {symbol}: {e}")
        return False

def generate_macd_histogram_report():
    """Generate a comprehensive report of all MACD Histogram data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross,
                   signal_cross, divergence_type, momentum_shift, histogram_pattern,
                   volume_confirmation, current_price, last_updated
            FROM macd_histogram_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No MACD Histogram data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 MACD HISTOGRAM COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine trend emoji
            trend_emoji = {
                "strong_bullish": "🚀",
                "bullish": "📈",
                "neutral": "➡️",
                "bearish": "📉",
                "strong_bearish": "💥"
            }.get(histogram_trend, "➡️")
            
            # Determine zero line cross emoji
            zero_cross_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(zero_line_cross, "⚪")
            
            # Determine signal cross emoji
            signal_cross_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(signal_cross, "⚪")
            
            # Determine divergence emoji
            divergence_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(divergence_type, "⚪")
            
            # Determine momentum emoji
            momentum_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(momentum_shift, "⚪")
            
            # Determine pattern emoji
            pattern_emoji = {
                "double_bottom": "📊",
                "double_top": "📊",
                "bullish_divergence": "🟢",
                "bearish_divergence": "🔴",
                "none": "⚪"
            }.get(histogram_pattern, "⚪")
            
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
            
            print(f"  {timeframe:>4} | {trend_emoji} {histogram_trend:>15} | {zero_cross_emoji} {zero_line_cross:>8} | {signal_cross_emoji} {signal_cross:>8} | {divergence_emoji} {divergence_type:>8} | {momentum_emoji} {momentum_shift:>8} | {pattern_emoji} {histogram_pattern:>15} | {volume_emoji} {volume_confirmation:>15} | Strength: {histogram_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 MACD HISTOGRAM SUMMARY:")
        print("="*80)
        
        # Count by histogram trend
        strong_bullish_count = sum(1 for row in data if row[2] == "strong_bullish")
        bullish_count = sum(1 for row in data if row[2] == "bullish")
        neutral_count = sum(1 for row in data if row[2] == "neutral")
        bearish_count = sum(1 for row in data if row[2] == "bearish")
        strong_bearish_count = sum(1 for row in data if row[2] == "strong_bearish")
        
        print(f"   🚀 Strong Bullish: {strong_bullish_count}")
        print(f"   📈 Bullish: {bullish_count}")
        print(f"   ➡️ Neutral: {neutral_count}")
        print(f"   📉 Bearish: {bearish_count}")
        print(f"   💥 Strong Bearish: {strong_bearish_count}")
        
        # Count by zero line cross
        bullish_zero_cross_count = sum(1 for row in data if row[4] == "bullish")
        bearish_zero_cross_count = sum(1 for row in data if row[4] == "bearish")
        no_zero_cross_count = sum(1 for row in data if row[4] == "none")
        
        print(f"   🟢 Bullish Zero Cross: {bullish_zero_cross_count}")
        print(f"   🔴 Bearish Zero Cross: {bearish_zero_cross_count}")
        print(f"   ⚪ No Zero Cross: {no_zero_cross_count}")
        
        # Count by signal cross
        bullish_signal_cross_count = sum(1 for row in data if row[5] == "bullish")
        bearish_signal_cross_count = sum(1 for row in data if row[5] == "bearish")
        no_signal_cross_count = sum(1 for row in data if row[5] == "none")
        
        print(f"   🟢 Bullish Signal Cross: {bullish_signal_cross_count}")
        print(f"   🔴 Bearish Signal Cross: {bearish_signal_cross_count}")
        print(f"   ⚪ No Signal Cross: {no_signal_cross_count}")
        
        # Count by divergence
        bullish_divergence_count = sum(1 for row in data if row[6] == "bullish")
        bearish_divergence_count = sum(1 for row in data if row[6] == "bearish")
        no_divergence_count = sum(1 for row in data if row[6] == "none")
        
        print(f"   🟢 Bullish Divergence: {bullish_divergence_count}")
        print(f"   🔴 Bearish Divergence: {bearish_divergence_count}")
        print(f"   ⚪ No Divergence: {no_divergence_count}")
        
        # Count by momentum shift
        bullish_momentum_count = sum(1 for row in data if row[7] == "bullish")
        bearish_momentum_count = sum(1 for row in data if row[7] == "bearish")
        no_momentum_count = sum(1 for row in data if row[7] == "none")
        
        print(f"   🟢 Bullish Momentum: {bullish_momentum_count}")
        print(f"   🔴 Bearish Momentum: {bearish_momentum_count}")
        print(f"   ⚪ No Momentum: {no_momentum_count}")
        
        # Count by histogram pattern
        double_bottom_count = sum(1 for row in data if row[8] == "double_bottom")
        double_top_count = sum(1 for row in data if row[8] == "double_top")
        bullish_pattern_divergence_count = sum(1 for row in data if row[8] == "bullish_divergence")
        bearish_pattern_divergence_count = sum(1 for row in data if row[8] == "bearish_divergence")
        no_pattern_count = sum(1 for row in data if row[8] == "none")
        
        print(f"   📊 Double Bottom: {double_bottom_count}")
        print(f"   📊 Double Top: {double_top_count}")
        print(f"   🟢 Bullish Pattern Divergence: {bullish_pattern_divergence_count}")
        print(f"   🔴 Bearish Pattern Divergence: {bearish_pattern_divergence_count}")
        print(f"   ⚪ No Pattern: {no_pattern_count}")
        
        # Count by volume confirmation
        strong_bullish_volume_count = sum(1 for row in data if row[9] == "strong_bullish")
        moderate_bullish_volume_count = sum(1 for row in data if row[9] == "moderate_bullish")
        weak_bullish_volume_count = sum(1 for row in data if row[9] == "weak_bullish")
        strong_bearish_volume_count = sum(1 for row in data if row[9] == "strong_bearish")
        moderate_bearish_volume_count = sum(1 for row in data if row[9] == "moderate_bearish")
        weak_bearish_volume_count = sum(1 for row in data if row[9] == "weak_bearish")
        no_volume_count = sum(1 for row in data if row[9] == "none")
        
        print(f"   📊 Strong Bullish Volume: {strong_bullish_volume_count}")
        print(f"   📈 Moderate Bullish Volume: {moderate_bullish_volume_count}")
        print(f"   📈 Weak Bullish Volume: {weak_bullish_volume_count}")
        print(f"   📊 Strong Bearish Volume: {strong_bearish_volume_count}")
        print(f"   📉 Moderate Bearish Volume: {moderate_bearish_volume_count}")
        print(f"   📉 Weak Bearish Volume: {weak_bearish_volume_count}")
        print(f"   ➡️ No Volume: {no_volume_count}")
        
        # Count strong histograms
        strong_histograms = sum(1 for row in data if row[3] > 70)
        moderate_histograms = sum(1 for row in data if 40 < row[3] <= 70)
        weak_histograms = sum(1 for row in data if row[3] <= 40)
        
        print(f"   💪 Strong Histograms (>70%): {strong_histograms}")
        print(f"   📊 Moderate Histograms (40-70%): {moderate_histograms}")
        print(f"   🔸 Weak Histograms (<40%): {weak_histograms}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong bullish signals
        strong_bullish = [row for row in data if row[2] in ["strong_bullish", "bullish"] and row[3] > 60]
        if strong_bullish:
            print("   🚀 Strong Bullish Signals (Buy Opportunities):")
            for signal in strong_bullish:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: {histogram_trend} - Strength {histogram_strength:.1f}%, Zero Cross {zero_line_cross}")
        else:
            print("   ✅ No strong bullish signals detected")
        
        # Find strong bearish signals
        strong_bearish = [row for row in data if row[2] in ["strong_bearish", "bearish"] and row[3] > 60]
        if strong_bearish:
            print("   💥 Strong Bearish Signals (Sell Opportunities):")
            for signal in strong_bearish:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: {histogram_trend} - Strength {histogram_strength:.1f}%, Zero Cross {zero_line_cross}")
        else:
            print("   ✅ No strong bearish signals detected")
        
        # Find zero line crossovers
        zero_crosses = [row for row in data if row[4] != "none" and row[3] > 30]
        if zero_crosses:
            print("   📊 Zero Line Crossovers (Trend Changes):")
            for cross in zero_crosses:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = cross
                print(f"      • {symbol} {timeframe}: {zero_line_cross} crossover - Strength {histogram_strength:.1f}%")
        else:
            print("   ✅ No zero line crossovers detected")
        
        # Find signal line crossovers
        signal_crosses = [row for row in data if row[5] != "none" and row[3] > 30]
        if signal_crosses:
            print("   📈 Signal Line Crossovers (MACD vs Signal):")
            for cross in signal_crosses:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = cross
                print(f"      • {symbol} {timeframe}: {signal_cross} crossover - Strength {histogram_strength:.1f}%")
        else:
            print("   ✅ No signal line crossovers detected")
        
        # Find divergences
        divergences = [row for row in data if row[6] != "none" and row[3] > 20]
        if divergences:
            print("   🔄 Divergences (Price vs Histogram):")
            for divergence in divergences:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: {divergence_type} divergence - Strength {histogram_strength:.1f}%")
        else:
            print("   ✅ No divergences detected")
        
        # Find momentum shifts
        momentum_shifts = [row for row in data if row[7] != "none" and row[3] > 20]
        if momentum_shifts:
            print("   🔄 Momentum Shifts (Histogram Momentum):")
            for shift in momentum_shifts:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = shift
                print(f"      • {symbol} {timeframe}: {momentum_shift} momentum shift - Strength {histogram_strength:.1f}%")
        else:
            print("   ✅ No momentum shifts detected")
        
        # Find histogram patterns
        patterns = [row for row in data if row[8] != "none" and row[3] > 20]
        if patterns:
            print("   📊 Histogram Patterns (Technical Patterns):")
            for pattern in patterns:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = pattern
                print(f"      • {symbol} {timeframe}: {histogram_pattern} pattern - Strength {histogram_strength:.1f}%")
        else:
            print("   ✅ No histogram patterns detected")
        
        # Find strong volume confirmations
        strong_volume = [row for row in data if "strong" in row[9] and row[3] > 30]
        if strong_volume:
            print("   📊 Strong Volume Confirmations:")
            for volume in strong_volume:
                symbol, timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, current_price, last_updated = volume
                print(f"      • {symbol} {timeframe}: {volume_confirmation} volume - Trend {histogram_trend}, Strength {histogram_strength:.1f}%")
        else:
            print("   ✅ No strong volume confirmations detected")
        
        print("\n" + "="*80)
        print("✅ MACD Histogram report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating MACD Histogram report: {e}")

def main():
    """Main function to populate MACD Histogram data"""
    print("🚀 Starting MACD Histogram data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store MACD Histogram for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        macd_histogram_data = calculate_macd_histogram_for_symbol(symbol, symbol_id)
        if macd_histogram_data:
            if store_macd_histogram_data(symbol_id, symbol, macd_histogram_data):
                print(f"✅ Stored {len(macd_histogram_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No MACD Histogram data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_macd_histogram_report()

if __name__ == "__main__":
    main()
