#!/usr/bin/env python3
"""
Populate Parabolic SAR Data
Calculates and stores Parabolic SAR indicators for all symbols in My Symbols list
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

def calculate_parabolic_sar(highs, lows, closes, acceleration=0.02, maximum=0.2):
    """Calculate Parabolic SAR"""
    if len(highs) < 3 or len(lows) < 3 or len(closes) < 3:
        return None, None, None, None, None, None
    
    # Initialize SAR values
    sar_values = []
    trend_directions = []
    acceleration_factors = []
    extreme_points = []
    
    # Start with first SAR value
    if closes[1] > closes[0]:
        # Bullish trend
        sar = lows[0]
        trend = "bullish"
        af = acceleration
        ep = highs[0]
    else:
        # Bearish trend
        sar = highs[0]
        trend = "bearish"
        af = acceleration
        ep = lows[0]
    
    sar_values.append(sar)
    trend_directions.append(trend)
    acceleration_factors.append(af)
    extreme_points.append(ep)
    
    # Calculate SAR for each period
    for i in range(1, len(highs)):
        high = highs[i]
        low = lows[i]
        close = closes[i]
        
        if trend == "bullish":
            # Update extreme point if new high
            if high > ep:
                ep = high
                af = min(af + acceleration, maximum)
            
            # Calculate SAR
            sar = sar + af * (ep - sar)
            
            # SAR should not be above previous low
            if i > 0:
                sar = min(sar, lows[i-1])
            
            # Check for trend reversal
            if close < sar:
                # Trend reversal to bearish
                trend = "bearish"
                sar = ep
                af = acceleration
                ep = low
            else:
                # Continue bullish trend
                sar = min(sar, low)
                
        else:  # bearish
            # Update extreme point if new low
            if low < ep:
                ep = low
                af = min(af + acceleration, maximum)
            
            # Calculate SAR
            sar = sar - af * (sar - ep)
            
            # SAR should not be below previous high
            if i > 0:
                sar = max(sar, highs[i-1])
            
            # Check for trend reversal
            if close > sar:
                # Trend reversal to bullish
                trend = "bullish"
                sar = ep
                af = acceleration
                ep = high
            else:
                # Continue bearish trend
                sar = max(sar, high)
        
        sar_values.append(sar)
        trend_directions.append(trend)
        acceleration_factors.append(af)
        extreme_points.append(ep)
    
    # Get current values
    current_sar = sar_values[-1]
    current_trend = trend_directions[-1]
    current_af = acceleration_factors[-1]
    current_ep = extreme_points[-1]
    
    return current_sar, current_trend, current_af, current_ep, sar_values, trend_directions

def calculate_trend_strength(sar_values, trend_directions, period=10):
    """Calculate trend strength based on SAR consistency"""
    if len(sar_values) < period:
        return 0.0
    
    recent_trends = trend_directions[-period:]
    current_trend = recent_trends[-1]
    
    # Count consecutive trend periods
    consecutive_count = 0
    for trend in reversed(recent_trends):
        if trend == current_trend:
            consecutive_count += 1
        else:
            break
    
    # Calculate strength as percentage of period
    strength = (consecutive_count / period) * 100
    return min(strength, 100.0)

def calculate_stop_loss_take_profit(sar_value, current_price, trend_direction):
    """Calculate stop loss and take profit levels"""
    if trend_direction == "bullish":
        stop_loss = sar_value
        # Take profit at 2:1 risk-reward ratio
        risk = current_price - stop_loss
        take_profit = current_price + (risk * 2)
    else:  # bearish
        stop_loss = sar_value
        # Take profit at 2:1 risk-reward ratio
        risk = stop_loss - current_price
        take_profit = current_price - (risk * 2)
    
    return stop_loss, take_profit

def calculate_risk_reward_ratio(current_price, stop_loss, take_profit, trend_direction):
    """Calculate risk-reward ratio"""
    if trend_direction == "bullish":
        risk = current_price - stop_loss
        reward = take_profit - current_price
    else:  # bearish
        risk = stop_loss - current_price
        reward = current_price - take_profit
    
    if risk == 0:
        return 0.0
    
    return reward / risk

def determine_trend_quality(sar_values, trend_directions, period=10):
    """Determine trend quality based on SAR consistency"""
    if len(sar_values) < period:
        return "neutral"
    
    recent_trends = trend_directions[-period:]
    current_trend = recent_trends[-1]
    
    # Count trend consistency
    trend_count = sum(1 for trend in recent_trends if trend == current_trend)
    consistency_ratio = trend_count / period
    
    if consistency_ratio >= 0.8:
        return "excellent"
    elif consistency_ratio >= 0.6:
        return "good"
    elif consistency_ratio >= 0.4:
        return "fair"
    else:
        return "poor"

def detect_reversal_signal(sar_values, trend_directions, current_price, period=5):
    """Detect potential trend reversal signals"""
    if len(sar_values) < period:
        return "none", 0.0
    
    current_trend = trend_directions[-1]
    current_sar = sar_values[-1]
    
    # Check for SAR crossover
    if current_trend == "bullish" and current_price < current_sar:
        # Potential bearish reversal
        reversal_strength = abs(current_price - current_sar) / current_price * 100
        return "bearish", min(reversal_strength, 100)
    elif current_trend == "bearish" and current_price > current_sar:
        # Potential bullish reversal
        reversal_strength = abs(current_price - current_sar) / current_price * 100
        return "bullish", min(reversal_strength, 100)
    else:
        return "none", 0.0

def calculate_trend_duration(trend_directions):
    """Calculate current trend duration"""
    if not trend_directions:
        return 0
    
    current_trend = trend_directions[-1]
    duration = 0
    
    for trend in reversed(trend_directions):
        if trend == current_trend:
            duration += 1
        else:
            break
    
    return duration

def calculate_parabolic_sar_for_symbol(symbol, symbol_id):
    """Calculate Parabolic SAR for all timeframes for a symbol"""
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
                
                if len(closes) >= 20:  # Need enough data for Parabolic SAR
                    # Calculate Parabolic SAR
                    current_sar, current_trend, current_af, current_ep, sar_values, trend_directions = calculate_parabolic_sar(highs, lows, closes)
                    
                    if current_sar is not None:
                        # Calculate trend strength
                        trend_strength = calculate_trend_strength(sar_values, trend_directions)
                        
                        # Calculate stop loss and take profit
                        stop_loss, take_profit = calculate_stop_loss_take_profit(current_sar, current_price, current_trend)
                        
                        # Calculate risk-reward ratio
                        risk_reward_ratio = calculate_risk_reward_ratio(current_price, stop_loss, take_profit, current_trend)
                        
                        # Determine trend quality
                        trend_quality = determine_trend_quality(sar_values, trend_directions)
                        
                        # Detect reversal signal
                        reversal_signal, reversal_strength = detect_reversal_signal(sar_values, trend_directions, current_price)
                        
                        # Calculate trend duration
                        trend_duration = calculate_trend_duration(trend_directions)
                        
                        results[tf] = {
                            "sar_value": current_sar,
                            "trend_direction": current_trend,
                            "trend_strength": trend_strength,
                            "acceleration_factor": current_af,
                            "extreme_point": current_ep,
                            "stop_loss_level": stop_loss,
                            "take_profit_level": take_profit,
                            "risk_reward_ratio": risk_reward_ratio,
                            "trend_duration": trend_duration,
                            "trend_quality": trend_quality,
                            "reversal_signal": reversal_signal,
                            "reversal_strength": reversal_strength,
                            "current_price": current_price
                        }
                    else:
                        print(f"⚠️ Could not calculate Parabolic SAR for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Parabolic SAR for {symbol}: {e}")
        return {}

def store_parabolic_sar_data(symbol_id, symbol, parabolic_sar_data):
    """Store Parabolic SAR data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in parabolic_sar_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO parabolic_sar_data 
                (symbol_id, symbol, timeframe, sar_value, trend_direction, trend_strength,
                acceleration_factor, extreme_point, stop_loss_level, take_profit_level,
                risk_reward_ratio, trend_duration, trend_quality, reversal_signal,
                reversal_strength, current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['sar_value'], data['trend_direction'],
                data['trend_strength'], data['acceleration_factor'], data['extreme_point'],
                data['stop_loss_level'], data['take_profit_level'], data['risk_reward_ratio'],
                data['trend_duration'], data['trend_quality'], data['reversal_signal'],
                data['reversal_strength'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Parabolic SAR data for {symbol}: {e}")
        return False

def generate_parabolic_sar_report():
    """Generate a comprehensive report of all Parabolic SAR data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, sar_value, trend_direction, trend_strength,
                   acceleration_factor, stop_loss_level, take_profit_level,
                   risk_reward_ratio, trend_duration, trend_quality, reversal_signal,
                   reversal_strength, current_price, last_updated
            FROM parabolic_sar_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Parabolic SAR data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 PARABOLIC SAR COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, sar_value, trend_direction, trend_strength, acceleration_factor, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine trend emoji
            trend_emoji = {
                "bullish": "🟢",
                "bearish": "🔴"
            }.get(trend_direction, "⚪")
            
            # Determine quality emoji
            quality_emoji = {
                "excellent": "⭐",
                "good": "👍",
                "fair": "➡️",
                "poor": "⚠️",
                "neutral": "⚪"
            }.get(trend_quality, "⚪")
            
            # Determine reversal emoji
            reversal_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "none": "⚪"
            }.get(reversal_signal, "⚪")
            
            print(f"  {timeframe:>4} | SAR: {sar_value:>8.4f} | {trend_emoji} {trend_direction:>8} | {quality_emoji} {trend_quality:>9} | {reversal_emoji} {reversal_signal:>8} | R/R: {risk_reward_ratio:>4.1f}")
        
        print("\n" + "="*80)
        print("📈 PARABOLIC SAR SUMMARY:")
        print("="*80)
        
        # Count by trend direction
        bullish_count = sum(1 for row in data if row[3] == "bullish")
        bearish_count = sum(1 for row in data if row[3] == "bearish")
        
        # Count by trend quality
        excellent_quality_count = sum(1 for row in data if row[10] == "excellent")
        good_quality_count = sum(1 for row in data if row[10] == "good")
        fair_quality_count = sum(1 for row in data if row[10] == "fair")
        poor_quality_count = sum(1 for row in data if row[10] == "poor")
        neutral_quality_count = sum(1 for row in data if row[10] == "neutral")
        
        # Count by reversal signal
        bullish_reversal_count = sum(1 for row in data if row[11] == "bullish")
        bearish_reversal_count = sum(1 for row in data if row[11] == "bearish")
        no_reversal_count = sum(1 for row in data if row[11] == "none")
        
        # Count strong trends
        strong_trends = sum(1 for row in data if row[4] > 50)
        moderate_trends = sum(1 for row in data if 20 < row[4] <= 50)
        weak_trends = sum(1 for row in data if row[4] <= 20)
        
        # Count good risk-reward ratios
        good_rr_ratios = sum(1 for row in data if row[8] > 2.0)
        moderate_rr_ratios = sum(1 for row in data if 1.0 < row[8] <= 2.0)
        poor_rr_ratios = sum(1 for row in data if row[8] <= 1.0)
        
        print(f"   🟢 Bullish Trends: {bullish_count}")
        print(f"   🔴 Bearish Trends: {bearish_count}")
        print(f"   ⭐ Excellent Quality: {excellent_quality_count}")
        print(f"   👍 Good Quality: {good_quality_count}")
        print(f"   ➡️ Fair Quality: {fair_quality_count}")
        print(f"   ⚠️ Poor Quality: {poor_quality_count}")
        print(f"   ⚪ Neutral Quality: {neutral_quality_count}")
        print(f"   🟢 Bullish Reversals: {bullish_reversal_count}")
        print(f"   🔴 Bearish Reversals: {bearish_reversal_count}")
        print(f"   ⚪ No Reversals: {no_reversal_count}")
        print(f"   💪 Strong Trends (>50%): {strong_trends}")
        print(f"   📊 Moderate Trends (20-50%): {moderate_trends}")
        print(f"   🔸 Weak Trends (<20%): {weak_trends}")
        print(f"   🎯 Good R/R Ratios (>2.0): {good_rr_ratios}")
        print(f"   📊 Moderate R/R Ratios (1.0-2.0): {moderate_rr_ratios}")
        print(f"   ⚠️ Poor R/R Ratios (<1.0): {poor_rr_ratios}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find strong bullish trends
        strong_bullish = [row for row in data if row[3] == "bullish" and row[4] > 50 and row[10] in ["excellent", "good"]]
        if strong_bullish:
            print("   🟢 Strong Bullish Trends (Potential Buy Opportunities):")
            for trend in strong_bullish:
                symbol, timeframe, sar_value, trend_direction, trend_strength, acceleration_factor, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: Trend strength {trend_strength:.1f}% - Quality: {trend_quality} - R/R: {risk_reward_ratio:.1f}")
        else:
            print("   ✅ No strong bullish trends detected")
        
        # Find strong bearish trends
        strong_bearish = [row for row in data if row[3] == "bearish" and row[4] > 50 and row[10] in ["excellent", "good"]]
        if strong_bearish:
            print("   🔴 Strong Bearish Trends (Potential Sell Opportunities):")
            for trend in strong_bearish:
                symbol, timeframe, sar_value, trend_direction, trend_strength, acceleration_factor, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength, current_price, last_updated = trend
                print(f"      • {symbol} {timeframe}: Trend strength {trend_strength:.1f}% - Quality: {trend_quality} - R/R: {risk_reward_ratio:.1f}")
        else:
            print("   ✅ No strong bearish trends detected")
        
        # Find bullish reversal signals
        bullish_reversals = [row for row in data if row[11] == "bullish" and row[12] > 30]
        if bullish_reversals:
            print("   🟢 Bullish Reversal Signals (Potential Buy Opportunities):")
            for reversal in bullish_reversals:
                symbol, timeframe, sar_value, trend_direction, trend_strength, acceleration_factor, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength, current_price, last_updated = reversal
                print(f"      • {symbol} {timeframe}: Reversal strength {reversal_strength:.1f}% - SAR: {sar_value:.4f}")
        else:
            print("   ✅ No bullish reversal signals detected")
        
        # Find bearish reversal signals
        bearish_reversals = [row for row in data if row[11] == "bearish" and row[12] > 30]
        if bearish_reversals:
            print("   🔴 Bearish Reversal Signals (Potential Sell Opportunities):")
            for reversal in bearish_reversals:
                symbol, timeframe, sar_value, trend_direction, trend_strength, acceleration_factor, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength, current_price, last_updated = reversal
                print(f"      • {symbol} {timeframe}: Reversal strength {reversal_strength:.1f}% - SAR: {sar_value:.4f}")
        else:
            print("   ✅ No bearish reversal signals detected")
        
        # Find excellent risk-reward opportunities
        excellent_rr = [row for row in data if row[8] > 3.0 and row[10] in ["excellent", "good"]]
        if excellent_rr:
            print("   🎯 Excellent Risk-Reward Opportunities:")
            for rr in excellent_rr:
                symbol, timeframe, sar_value, trend_direction, trend_strength, acceleration_factor, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength, current_price, last_updated = rr
                print(f"      • {symbol} {timeframe}: R/R ratio {risk_reward_ratio:.1f} - Quality: {trend_quality} - Trend: {trend_direction}")
        else:
            print("   ✅ No excellent risk-reward opportunities detected")
        
        print("\n" + "="*80)
        print("✅ Parabolic SAR report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Parabolic SAR report: {e}")

def main():
    """Main function to populate Parabolic SAR data"""
    print("🚀 Starting Parabolic SAR data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Parabolic SAR for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        parabolic_sar_data = calculate_parabolic_sar_for_symbol(symbol, symbol_id)
        if parabolic_sar_data:
            if store_parabolic_sar_data(symbol_id, symbol, parabolic_sar_data):
                print(f"✅ Stored {len(parabolic_sar_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Parabolic SAR data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_parabolic_sar_report()

if __name__ == "__main__":
    main()
