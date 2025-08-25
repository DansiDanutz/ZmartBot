#!/usr/bin/env python3
"""
Populate Momentum Indicators Data
Calculates and stores Rate of Change (ROC) and Momentum (MOM) analysis for all symbols in My Symbols list
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

def calculate_roc(prices, period=10):
    """Calculate Rate of Change (ROC)"""
    if len(prices) < period + 1:
        return None
    
    current_price = prices[-1]
    past_price = prices[-period-1]
    
    if past_price == 0:
        return 0.0
    
    roc = ((current_price - past_price) / past_price) * 100
    return roc

def calculate_momentum(prices, period=10):
    """Calculate Momentum (MOM)"""
    if len(prices) < period + 1:
        return None
    
    current_price = prices[-1]
    past_price = prices[-period-1]
    
    momentum = current_price - past_price
    return momentum

def determine_roc_signal(roc_value, previous_roc):
    """Determine ROC signal"""
    if previous_roc is None:
        return "neutral", 0.0
    
    if roc_value > 5.0:
        return "strong_bullish", min(abs(roc_value), 100.0)
    elif roc_value > 2.0:
        return "bullish", min(abs(roc_value), 100.0)
    elif roc_value < -5.0:
        return "strong_bearish", min(abs(roc_value), 100.0)
    elif roc_value < -2.0:
        return "bearish", min(abs(roc_value), 100.0)
    else:
        return "neutral", 0.0

def determine_mom_signal(mom_value, previous_mom):
    """Determine Momentum signal"""
    if previous_mom is None:
        return "neutral", 0.0
    
    if mom_value > 0 and mom_value > previous_mom:
        return "bullish", min(abs(mom_value), 100.0)
    elif mom_value < 0 and mom_value < previous_mom:
        return "bearish", min(abs(mom_value), 100.0)
    elif mom_value > 0:
        return "weak_bullish", min(abs(mom_value), 100.0)
    elif mom_value < 0:
        return "weak_bearish", min(abs(mom_value), 100.0)
    else:
        return "neutral", 0.0

def detect_roc_divergence(prices, roc_values, period=10):
    """Detect ROC divergence"""
    if len(prices) < period * 2 or len(roc_values) < period * 2:
        return "none", 0.0
    
    # Get recent price and ROC data
    recent_prices = prices[-period:]
    recent_roc = roc_values[-period:]
    
    # Calculate price trend
    price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
    
    # Calculate ROC trend
    roc_trend = "up" if recent_roc[-1] > recent_roc[0] else "down"
    
    # Detect divergence
    if price_trend == "up" and roc_trend == "down":
        divergence_strength = abs(recent_roc[-1] - recent_roc[0])
        return "bearish", min(divergence_strength, 100.0)
    elif price_trend == "down" and roc_trend == "up":
        divergence_strength = abs(recent_roc[-1] - recent_roc[0])
        return "bullish", min(divergence_strength, 100.0)
    else:
        return "none", 0.0

def detect_mom_divergence(prices, mom_values, period=10):
    """Detect Momentum divergence"""
    if len(prices) < period * 2 or len(mom_values) < period * 2:
        return "none", 0.0
    
    # Get recent price and momentum data
    recent_prices = prices[-period:]
    recent_mom = mom_values[-period:]
    
    # Calculate price trend
    price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
    
    # Calculate momentum trend
    mom_trend = "up" if recent_mom[-1] > recent_mom[0] else "down"
    
    # Detect divergence
    if price_trend == "up" and mom_trend == "down":
        divergence_strength = abs(recent_mom[-1] - recent_mom[0])
        return "bearish", min(divergence_strength, 100.0)
    elif price_trend == "down" and mom_trend == "up":
        divergence_strength = abs(recent_mom[-1] - recent_mom[0])
        return "bullish", min(divergence_strength, 100.0)
    else:
        return "none", 0.0

def determine_momentum_status(roc_signal, mom_signal, roc_strength, mom_strength):
    """Determine overall momentum status"""
    if roc_signal in ["strong_bullish", "bullish"] and mom_signal in ["bullish", "weak_bullish"]:
        momentum_strength = (roc_strength + mom_strength) / 2
        return "strong_bullish", momentum_strength
    elif roc_signal in ["strong_bearish", "bearish"] and mom_signal in ["bearish", "weak_bearish"]:
        momentum_strength = (roc_strength + mom_strength) / 2
        return "strong_bearish", momentum_strength
    elif roc_signal in ["strong_bullish", "bullish"] or mom_signal in ["bullish", "weak_bullish"]:
        momentum_strength = (roc_strength + mom_strength) / 2
        return "weak_bullish", momentum_strength
    elif roc_signal in ["strong_bearish", "bearish"] or mom_signal in ["bearish", "weak_bearish"]:
        momentum_strength = (roc_strength + mom_strength) / 2
        return "weak_bearish", momentum_strength
    else:
        return "neutral", 0.0

def determine_trend_alignment(roc_value, mom_value, closes, period=10):
    """Determine trend alignment"""
    if len(closes) < period:
        return "neutral", 0.0
    
    # Calculate price trend
    price_trend = "up" if closes[-1] > closes[-period] else "down"
    
    # Determine ROC trend
    roc_trend = "up" if roc_value > 0 else "down"
    
    # Determine momentum trend
    mom_trend = "up" if mom_value > 0 else "down"
    
    # Calculate alignment
    alignment_score = 0
    if price_trend == roc_trend:
        alignment_score += 1
    if price_trend == mom_trend:
        alignment_score += 1
    if roc_trend == mom_trend:
        alignment_score += 1
    
    alignment_strength = (alignment_score / 3) * 100
    
    if alignment_score == 3:
        return "strong_alignment", alignment_strength
    elif alignment_score == 2:
        return "moderate_alignment", alignment_strength
    elif alignment_score == 1:
        return "weak_alignment", alignment_strength
    else:
        return "no_alignment", alignment_strength

def determine_overbought_oversold(roc_value, mom_value):
    """Determine overbought/oversold status"""
    # ROC overbought/oversold levels
    if roc_value > 10.0:
        return "overbought", min(abs(roc_value), 100.0)
    elif roc_value < -10.0:
        return "oversold", min(abs(roc_value), 100.0)
    elif roc_value > 5.0:
        return "moderate_overbought", min(abs(roc_value), 100.0)
    elif roc_value < -5.0:
        return "moderate_oversold", min(abs(roc_value), 100.0)
    else:
        return "neutral", 0.0

def determine_volume_confirmation(volumes, momentum_status, periods=5):
    """Determine volume confirmation for momentum"""
    if len(volumes) < periods:
        return "none", 0.0
    
    recent_volumes = volumes[-periods:]
    avg_volume = np.mean(recent_volumes[:-1])
    current_volume = recent_volumes[-1]
    
    if avg_volume == 0:
        return "none", 0.0
    
    volume_ratio = current_volume / avg_volume
    
    if momentum_status in ["strong_bullish", "weak_bullish"]:
        if volume_ratio > 1.5:
            return "strong_bullish", volume_ratio * 100
        elif volume_ratio > 1.2:
            return "moderate_bullish", volume_ratio * 100
        elif volume_ratio > 1.0:
            return "weak_bullish", volume_ratio * 100
        else:
            return "none", volume_ratio * 100
    elif momentum_status in ["strong_bearish", "weak_bearish"]:
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

def calculate_momentum_indicators_for_symbol(symbol, symbol_id):
    """Calculate Momentum Indicators for all timeframes for a symbol"""
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
                
                if len(closes) >= 20:  # Need enough data for momentum indicators
                    # Calculate ROC and Momentum
                    roc_value = calculate_roc(closes, 10)
                    mom_value = calculate_momentum(closes, 10)
                    
                    if roc_value is not None and mom_value is not None:
                        # Calculate previous values for signal determination
                        if len(closes) >= 21:
                            prev_roc = calculate_roc(closes[:-1], 10)
                            prev_mom = calculate_momentum(closes[:-1], 10)
                        else:
                            prev_roc = roc_value
                            prev_mom = mom_value
                        
                        # Determine signals
                        roc_signal, roc_strength = determine_roc_signal(roc_value, prev_roc)
                        mom_signal, mom_strength = determine_mom_signal(mom_value, prev_mom)
                        
                        # Calculate ROC values for divergence detection
                        roc_values = []
                        for i in range(10, len(closes)):
                            roc = calculate_roc(closes[:i+1], 10)
                            if roc is not None:
                                roc_values.append(roc)
                        
                        # Calculate momentum values for divergence detection
                        mom_values = []
                        for i in range(10, len(closes)):
                            mom = calculate_momentum(closes[:i+1], 10)
                            if mom is not None:
                                mom_values.append(mom)
                        
                        # Detect divergences
                        roc_divergence, roc_divergence_strength = detect_roc_divergence(closes, roc_values)
                        mom_divergence, mom_divergence_strength = detect_mom_divergence(closes, mom_values)
                        
                        # Determine overall momentum status
                        momentum_status, momentum_strength = determine_momentum_status(
                            roc_signal, mom_signal, roc_strength, mom_strength
                        )
                        
                        # Determine trend alignment
                        trend_alignment, trend_strength = determine_trend_alignment(
                            roc_value, mom_value, closes
                        )
                        
                        # Determine overbought/oversold status
                        overbought_oversold_status, overbought_oversold_strength = determine_overbought_oversold(
                            roc_value, mom_value
                        )
                        
                        # Determine volume confirmation
                        volume_confirmation, volume_strength = determine_volume_confirmation(
                            volumes, momentum_status
                        )
                        
                        results[tf] = {
                            "roc_value": roc_value,
                            "roc_signal": roc_signal,
                            "roc_strength": roc_strength,
                            "roc_divergence": roc_divergence,
                            "roc_divergence_strength": roc_divergence_strength,
                            "mom_value": mom_value,
                            "mom_signal": mom_signal,
                            "mom_strength": mom_strength,
                            "mom_divergence": mom_divergence,
                            "mom_divergence_strength": mom_divergence_strength,
                            "momentum_status": momentum_status,
                            "momentum_strength": momentum_strength,
                            "trend_alignment": trend_alignment,
                            "trend_strength": trend_strength,
                            "overbought_oversold_status": overbought_oversold_status,
                            "overbought_oversold_strength": overbought_oversold_strength,
                            "volume_confirmation": volume_confirmation,
                            "volume_strength": volume_strength,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate momentum indicators for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Momentum Indicators for {symbol}: {e}")
        return {}

def store_momentum_indicators_data(symbol_id, symbol, momentum_indicators_data):
    """Store Momentum Indicators data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in momentum_indicators_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO momentum_indicators_data 
                (symbol_id, symbol, timeframe, roc_value, roc_signal, roc_strength,
                roc_divergence, roc_divergence_strength, mom_value, mom_signal,
                mom_strength, mom_divergence, mom_divergence_strength,
                momentum_status, momentum_strength, trend_alignment, trend_strength,
                overbought_oversold_status, overbought_oversold_strength,
                volume_confirmation, volume_strength, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['roc_value'], data['roc_signal'],
                data['roc_strength'], data['roc_divergence'], data['roc_divergence_strength'],
                data['mom_value'], data['mom_signal'], data['mom_strength'],
                data['mom_divergence'], data['mom_divergence_strength'],
                data['momentum_status'], data['momentum_strength'], data['trend_alignment'],
                data['trend_strength'], data['overbought_oversold_status'],
                data['overbought_oversold_strength'], data['volume_confirmation'],
                data['volume_strength'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Momentum Indicators data for {symbol}: {e}")
        return False

def generate_momentum_indicators_report():
    """Generate a comprehensive report of all Momentum Indicators data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, roc_signal, roc_strength, roc_divergence,
                   mom_signal, mom_strength, mom_divergence, momentum_status,
                   momentum_strength, trend_alignment, overbought_oversold_status,
                   volume_confirmation, current_price, last_updated
            FROM momentum_indicators_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Momentum Indicators data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 MOMENTUM INDICATORS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, roc_signal, roc_strength, roc_divergence, mom_signal, mom_strength, mom_divergence, momentum_status, momentum_strength, trend_alignment, overbought_oversold_status, volume_confirmation, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine ROC emoji
            roc_emoji = {
                "strong_bullish": "🚀",
                "bullish": "📈",
                "neutral": "➡️",
                "bearish": "📉",
                "strong_bearish": "💥"
            }.get(roc_signal, "➡️")
            
            # Determine MOM emoji
            mom_emoji = {
                "bullish": "📈",
                "weak_bullish": "📈",
                "neutral": "➡️",
                "weak_bearish": "📉",
                "bearish": "📉"
            }.get(mom_signal, "➡️")
            
            # Determine momentum emoji
            momentum_emoji = {
                "strong_bullish": "🚀",
                "weak_bullish": "📈",
                "neutral": "➡️",
                "weak_bearish": "📉",
                "strong_bearish": "💥"
            }.get(momentum_status, "➡️")
            
            # Determine divergence emoji
            roc_div_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(roc_divergence, "⚪")
            
            mom_div_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(mom_divergence, "⚪")
            
            # Determine overbought/oversold emoji
            oo_emoji = {
                "overbought": "🔴",
                "moderate_overbought": "🟡",
                "neutral": "⚪",
                "moderate_oversold": "🟡",
                "oversold": "🟢"
            }.get(overbought_oversold_status, "⚪")
            
            print(f"  {timeframe:>4} | {roc_emoji} {roc_signal:>15} | {mom_emoji} {mom_signal:>12} | {momentum_emoji} {momentum_status:>15} | {roc_div_emoji} {roc_divergence:>8} | {mom_div_emoji} {mom_divergence:>8} | {oo_emoji} {overbought_oversold_status:>20} | ROC: {roc_strength:>5.1f}% | MOM: {mom_strength:>5.1f}% | Momentum: {momentum_strength:>5.1f}%")
        
        print("\n" + "="*80)
        print("📈 MOMENTUM INDICATORS SUMMARY:")
        print("="*80)
        
        # Count by ROC signal
        strong_bullish_roc_count = sum(1 for row in data if row[2] == "strong_bullish")
        bullish_roc_count = sum(1 for row in data if row[2] == "bullish")
        neutral_roc_count = sum(1 for row in data if row[2] == "neutral")
        bearish_roc_count = sum(1 for row in data if row[2] == "bearish")
        strong_bearish_roc_count = sum(1 for row in data if row[2] == "strong_bearish")
        
        print(f"   🚀 Strong Bullish ROC: {strong_bullish_roc_count}")
        print(f"   📈 Bullish ROC: {bullish_roc_count}")
        print(f"   ➡️ Neutral ROC: {neutral_roc_count}")
        print(f"   📉 Bearish ROC: {bearish_roc_count}")
        print(f"   💥 Strong Bearish ROC: {strong_bearish_roc_count}")
        
        # Count by MOM signal
        bullish_mom_count = sum(1 for row in data if row[5] == "bullish")
        weak_bullish_mom_count = sum(1 for row in data if row[5] == "weak_bullish")
        neutral_mom_count = sum(1 for row in data if row[5] == "neutral")
        weak_bearish_mom_count = sum(1 for row in data if row[5] == "weak_bearish")
        bearish_mom_count = sum(1 for row in data if row[5] == "bearish")
        
        print(f"   📈 Bullish MOM: {bullish_mom_count}")
        print(f"   📈 Weak Bullish MOM: {weak_bullish_mom_count}")
        print(f"   ➡️ Neutral MOM: {neutral_mom_count}")
        print(f"   📉 Weak Bearish MOM: {weak_bearish_mom_count}")
        print(f"   📉 Bearish MOM: {bearish_mom_count}")
        
        # Count by momentum status
        strong_bullish_momentum_count = sum(1 for row in data if row[8] == "strong_bullish")
        weak_bullish_momentum_count = sum(1 for row in data if row[8] == "weak_bullish")
        neutral_momentum_count = sum(1 for row in data if row[8] == "neutral")
        weak_bearish_momentum_count = sum(1 for row in data if row[8] == "weak_bearish")
        strong_bearish_momentum_count = sum(1 for row in data if row[8] == "strong_bearish")
        
        print(f"   🚀 Strong Bullish Momentum: {strong_bullish_momentum_count}")
        print(f"   📈 Weak Bullish Momentum: {weak_bullish_momentum_count}")
        print(f"   ➡️ Neutral Momentum: {neutral_momentum_count}")
        print(f"   📉 Weak Bearish Momentum: {weak_bearish_momentum_count}")
        print(f"   💥 Strong Bearish Momentum: {strong_bearish_momentum_count}")
        
        # Count divergences
        bullish_roc_div_count = sum(1 for row in data if row[4] == "bullish")
        bearish_roc_div_count = sum(1 for row in data if row[4] == "bearish")
        no_roc_div_count = sum(1 for row in data if row[4] == "none")
        
        print(f"   🟢 Bullish ROC Divergence: {bullish_roc_div_count}")
        print(f"   🔴 Bearish ROC Divergence: {bearish_roc_div_count}")
        print(f"   ⚪ No ROC Divergence: {no_roc_div_count}")
        
        bullish_mom_div_count = sum(1 for row in data if row[7] == "bullish")
        bearish_mom_div_count = sum(1 for row in data if row[7] == "bearish")
        no_mom_div_count = sum(1 for row in data if row[7] == "none")
        
        print(f"   🟢 Bullish MOM Divergence: {bullish_mom_div_count}")
        print(f"   🔴 Bearish MOM Divergence: {bearish_mom_div_count}")
        print(f"   ⚪ No MOM Divergence: {no_mom_div_count}")
        
        # Count overbought/oversold
        overbought_count = sum(1 for row in data if row[11] == "overbought")
        moderate_overbought_count = sum(1 for row in data if row[11] == "moderate_overbought")
        neutral_oo_count = sum(1 for row in data if row[11] == "neutral")
        moderate_oversold_count = sum(1 for row in data if row[11] == "moderate_oversold")
        oversold_count = sum(1 for row in data if row[11] == "oversold")
        
        print(f"   🔴 Overbought: {overbought_count}")
        print(f"   🟡 Moderate Overbought: {moderate_overbought_count}")
        print(f"   ⚪ Neutral: {neutral_oo_count}")
        print(f"   🟡 Moderate Oversold: {moderate_oversold_count}")
        print(f"   🟢 Oversold: {oversold_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong momentum signals
        strong_momentum = [row for row in data if "strong" in row[8] and row[9] > 50]
        if strong_momentum:
            print("   🚀 Strong Momentum Signals:")
            for momentum in strong_momentum:
                symbol, timeframe, roc_signal, roc_strength, roc_divergence, mom_signal, mom_strength, mom_divergence, momentum_status, momentum_strength, trend_alignment, overbought_oversold_status, volume_confirmation, current_price, last_updated = momentum
                print(f"      • {symbol} {timeframe}: {momentum_status} - Strength {momentum_strength:.1f}%, ROC {roc_signal}, MOM {mom_signal}")
        else:
            print("   ✅ No strong momentum signals detected")
        
        # Find divergences
        divergences = [row for row in data if row[4] != "none" or row[7] != "none"]
        if divergences:
            print("   🔄 Divergence Signals:")
            for div in divergences:
                symbol, timeframe, roc_signal, roc_strength, roc_divergence, mom_signal, mom_strength, mom_divergence, momentum_status, momentum_strength, trend_alignment, overbought_oversold_status, volume_confirmation, current_price, last_updated = div
                if roc_divergence != "none":
                    print(f"      • {symbol} {timeframe}: ROC {roc_divergence} divergence")
                if mom_divergence != "none":
                    print(f"      • {symbol} {timeframe}: MOM {mom_divergence} divergence")
        else:
            print("   ✅ No divergence signals detected")
        
        # Find overbought/oversold conditions
        extreme_oo = [row for row in data if row[11] in ["overbought", "oversold"]]
        if extreme_oo:
            print("   📊 Extreme Overbought/Oversold Conditions:")
            for oo in extreme_oo:
                symbol, timeframe, roc_signal, roc_strength, roc_divergence, mom_signal, mom_strength, mom_divergence, momentum_status, momentum_strength, trend_alignment, overbought_oversold_status, volume_confirmation, current_price, last_updated = oo
                print(f"      • {symbol} {timeframe}: {overbought_oversold_status}")
        else:
            print("   ✅ No extreme overbought/oversold conditions detected")
        
        print("\n" + "="*80)
        print("✅ Momentum Indicators report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Momentum Indicators report: {e}")

def main():
    """Main function to populate Momentum Indicators data"""
    print("🚀 Starting Momentum Indicators data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Momentum Indicators for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        momentum_indicators_data = calculate_momentum_indicators_for_symbol(symbol, symbol_id)
        if momentum_indicators_data:
            if store_momentum_indicators_data(symbol_id, symbol, momentum_indicators_data):
                print(f"✅ Stored {len(momentum_indicators_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Momentum Indicators data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_momentum_indicators_report()

if __name__ == "__main__":
    main()
