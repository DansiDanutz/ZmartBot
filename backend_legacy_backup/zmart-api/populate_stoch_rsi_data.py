#!/usr/bin/env python3
"""
Populate Stochastic RSI Data
Calculates and stores Stochastic RSI indicators for all symbols in My Symbols list
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

def calculate_stochastic(rsi_values, k_period=14, d_period=3):
    """Calculate Stochastic oscillator from RSI values"""
    if len(rsi_values) < k_period:
        return None, None
    
    # Calculate %K (stochastic K)
    rsi_window = rsi_values[-k_period:]
    highest_high = max(rsi_window)
    lowest_low = min(rsi_window)
    
    if highest_high == lowest_low:
        stoch_k = 50.0  # Neutral when no range
    else:
        stoch_k = ((rsi_values[-1] - lowest_low) / (highest_high - lowest_low)) * 100
    
    # Calculate %D (stochastic D) - SMA of %K
    if len(rsi_values) >= k_period + d_period - 1:
        k_values = []
        for i in range(d_period):
            start_idx = -(k_period + i)
            end_idx = -(i + 1) if i > 0 else None
            rsi_window = rsi_values[start_idx:end_idx]
            if len(rsi_window) >= k_period:
                highest_high = max(rsi_window)
                lowest_low = min(rsi_window)
                if highest_high == lowest_low:
                    k_val = 50.0
                else:
                    k_val = ((rsi_window[-1] - lowest_low) / (highest_high - lowest_low)) * 100
                k_values.append(k_val)
        
        if k_values:
            stoch_d = np.mean(k_values)
        else:
            stoch_d = stoch_k
    else:
        stoch_d = stoch_k
    
    return stoch_k, stoch_d

def determine_signal_status(stoch_k, stoch_d, overbought_level=80, oversold_level=20):
    """Determine signal status based on Stochastic RSI values"""
    if stoch_k is None or stoch_d is None:
        return "neutral"
    
    # Check for overbought conditions
    if stoch_k > overbought_level and stoch_d > overbought_level:
        return "overbought"
    elif stoch_k < oversold_level and stoch_d < oversold_level:
        return "oversold"
    elif stoch_k > stoch_d and stoch_k > 50:
        return "bullish"
    elif stoch_k < stoch_d and stoch_k < 50:
        return "bearish"
    else:
        return "neutral"

def calculate_signal_strength(stoch_k, stoch_d, signal_status):
    """Calculate signal strength based on Stochastic RSI values"""
    if stoch_k is None or stoch_d is None:
        return 0.0
    
    if signal_status == "overbought":
        # Strength based on how far above overbought level
        strength = min((stoch_k - 80) / 20 * 100, 100)
        return max(strength, 0)
    elif signal_status == "oversold":
        # Strength based on how far below oversold level
        strength = min((20 - stoch_k) / 20 * 100, 100)
        return max(strength, 0)
    elif signal_status == "bullish":
        # Strength based on distance from neutral (50)
        strength = (stoch_k - 50) / 50 * 100
        return max(strength, 0)
    elif signal_status == "bearish":
        # Strength based on distance from neutral (50)
        strength = (50 - stoch_k) / 50 * 100
        return max(strength, 0)
    else:
        return 0.0

def detect_divergence(rsi_values, prices, stoch_k_values, lookback=14):
    """Detect divergence between price and Stochastic RSI"""
    if len(rsi_values) < lookback or len(prices) < lookback or len(stoch_k_values) < lookback:
        return "none", 0.0
    
    # Get recent data
    recent_prices = prices[-lookback:]
    recent_stoch = stoch_k_values[-lookback:]
    
    # Calculate price trend
    price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
    
    # Calculate Stochastic RSI trend
    stoch_trend = "up" if recent_stoch[-1] > recent_stoch[0] else "down"
    
    # Detect divergence
    if price_trend == "up" and stoch_trend == "down":
        # Bearish divergence: price up, indicator down
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bearish", divergence_strength
    elif price_trend == "down" and stoch_trend == "up":
        # Bullish divergence: price down, indicator up
        divergence_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        return "bullish", divergence_strength
    else:
        return "none", 0.0

def determine_momentum_trend(stoch_k_values, period=5):
    """Determine momentum trend based on Stochastic RSI values"""
    if len(stoch_k_values) < period:
        return "neutral", 0.0
    
    recent_stoch = stoch_k_values[-period:]
    
    # Calculate momentum
    momentum_change = recent_stoch[-1] - recent_stoch[0]
    momentum_strength = abs(momentum_change) / 100 * 100  # Normalize to 0-100
    
    if momentum_change > 0:
        return "increasing", momentum_strength
    elif momentum_change < 0:
        return "decreasing", momentum_strength
    else:
        return "neutral", 0.0

def calculate_stoch_rsi_for_symbol(symbol, symbol_id):
    """Calculate Stochastic RSI for all timeframes for a symbol"""
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
                prices = [float(kline[4]) for kline in klines_data]  # Close prices
                
                if len(prices) >= 50:  # Need enough data for RSI and Stochastic
                    # Calculate RSI values for the entire period
                    rsi_values = []
                    for i in range(14, len(prices)):
                        rsi = calculate_rsi(prices[:i+1], 14)
                        if rsi is not None:
                            rsi_values.append(rsi)
                    
                    if len(rsi_values) >= 20:  # Need enough RSI values for Stochastic
                        # Calculate current RSI
                        current_rsi = rsi_values[-1]
                        
                        # Calculate Stochastic RSI
                        stoch_k, stoch_d = calculate_stochastic(rsi_values, 14, 3)
                        
                        if stoch_k is not None and stoch_d is not None:
                            # Calculate Stochastic RSI value (average of K and D)
                            stoch_rsi_value = (stoch_k + stoch_d) / 2
                            
                            # Determine signal status
                            signal_status = determine_signal_status(stoch_k, stoch_d)
                            
                            # Calculate signal strength
                            signal_strength = calculate_signal_strength(stoch_k, stoch_d, signal_status)
                            
                            # Detect divergence
                            divergence_type, divergence_strength = detect_divergence(rsi_values, prices, [stoch_k] * len(rsi_values))
                            
                            # Determine momentum trend
                            momentum_trend, momentum_strength = determine_momentum_trend([stoch_k] * 5)  # Use current value for trend
                            
                            results[tf] = {
                                "rsi_value": current_rsi,
                                "stoch_k": stoch_k,
                                "stoch_d": stoch_d,
                                "stoch_rsi_value": stoch_rsi_value,
                                "overbought_level": 80.0,
                                "oversold_level": 20.0,
                                "signal_status": signal_status,
                                "signal_strength": signal_strength,
                                "divergence_type": divergence_type,
                                "divergence_strength": divergence_strength,
                                "momentum_trend": momentum_trend,
                                "momentum_strength": momentum_strength,
                                "current_price": current_price
                            }
                        else:
                            print(f"⚠️ Could not calculate Stochastic RSI for {symbol} {tf}")
                    else:
                        print(f"⚠️ Insufficient RSI data for {symbol} {tf}")
                else:
                    print(f"⚠️ Insufficient price data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating Stochastic RSI for {symbol}: {e}")
        return {}

def store_stoch_rsi_data(symbol_id, symbol, stoch_rsi_data):
    """Store Stochastic RSI data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in stoch_rsi_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO stoch_rsi_data 
                (symbol_id, symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value,
                overbought_level, oversold_level, signal_status, signal_strength,
                divergence_type, divergence_strength, momentum_trend, momentum_strength,
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['rsi_value'], data['stoch_k'],
                data['stoch_d'], data['stoch_rsi_value'], data['overbought_level'],
                data['oversold_level'], data['signal_status'], data['signal_strength'],
                data['divergence_type'], data['divergence_strength'], data['momentum_trend'],
                data['momentum_strength'], data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing Stochastic RSI data for {symbol}: {e}")
        return False

def generate_stoch_rsi_report():
    """Generate a comprehensive report of all Stochastic RSI data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value,
                   signal_status, signal_strength, divergence_type, divergence_strength,
                   momentum_trend, momentum_strength, current_price, last_updated
            FROM stoch_rsi_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No Stochastic RSI data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 STOCHASTIC RSI COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, current_price, last_updated = row
            
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
            
            print(f"  {timeframe:>4} | RSI: {rsi_value:>6.1f} | K: {stoch_k:>6.1f} | D: {stoch_d:>6.1f} | {signal_emoji} {signal_status:>10} | {divergence_emoji} {divergence_type:>8} | {momentum_emoji} {momentum_trend:>10}")
        
        print("\n" + "="*80)
        print("📈 STOCHASTIC RSI SUMMARY:")
        print("="*80)
        
        # Count by signal status
        overbought_count = sum(1 for row in data if row[6] == "overbought")
        oversold_count = sum(1 for row in data if row[6] == "oversold")
        bullish_count = sum(1 for row in data if row[6] == "bullish")
        bearish_count = sum(1 for row in data if row[6] == "bearish")
        neutral_count = sum(1 for row in data if row[6] == "neutral")
        
        # Count by divergence type
        bullish_divergence_count = sum(1 for row in data if row[8] == "bullish")
        bearish_divergence_count = sum(1 for row in data if row[8] == "bearish")
        no_divergence_count = sum(1 for row in data if row[8] == "none")
        
        # Count by momentum trend
        increasing_momentum_count = sum(1 for row in data if row[10] == "increasing")
        decreasing_momentum_count = sum(1 for row in data if row[10] == "decreasing")
        neutral_momentum_count = sum(1 for row in data if row[10] == "neutral")
        
        # Count strong signals
        strong_signals = sum(1 for row in data if row[7] > 50)
        moderate_signals = sum(1 for row in data if 20 < row[7] <= 50)
        weak_signals = sum(1 for row in data if row[7] <= 20)
        
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
        print(f"   💪 Strong Signals (>50%): {strong_signals}")
        print(f"   📊 Moderate Signals (20-50%): {moderate_signals}")
        print(f"   🔸 Weak Signals (<20%): {weak_signals}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find overbought conditions
        overbought_signals = [row for row in data if row[6] == "overbought" and row[7] > 30]
        if overbought_signals:
            print("   🔴 Overbought Conditions (Potential Sell Opportunities):")
            for signal in overbought_signals:
                symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - RSI: {rsi_value:.1f}, K: {stoch_k:.1f}, D: {stoch_d:.1f}")
        else:
            print("   ✅ No strong overbought conditions detected")
        
        # Find oversold conditions
        oversold_signals = [row for row in data if row[6] == "oversold" and row[7] > 30]
        if oversold_signals:
            print("   🟢 Oversold Conditions (Potential Buy Opportunities):")
            for signal in oversold_signals:
                symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, current_price, last_updated = signal
                print(f"      • {symbol} {timeframe}: Signal strength {signal_strength:.1f}% - RSI: {rsi_value:.1f}, K: {stoch_k:.1f}, D: {stoch_d:.1f}")
        else:
            print("   ✅ No strong oversold conditions detected")
        
        # Find bullish divergences
        bullish_divergences = [row for row in data if row[8] == "bullish" and row[9] > 2.0]
        if bullish_divergences:
            print("   🟢 Bullish Divergences (Potential Buy Signals):")
            for divergence in bullish_divergences:
                symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price down, Stochastic RSI up")
        else:
            print("   ✅ No bullish divergences detected")
        
        # Find bearish divergences
        bearish_divergences = [row for row in data if row[8] == "bearish" and row[9] > 2.0]
        if bearish_divergences:
            print("   🔴 Bearish Divergences (Potential Sell Signals):")
            for divergence in bearish_divergences:
                symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Divergence strength {divergence_strength:.1f}% - Price up, Stochastic RSI down")
        else:
            print("   ✅ No bearish divergences detected")
        
        # Find strong momentum trends
        strong_momentum = [row for row in data if row[11] > 30]
        if strong_momentum:
            print("   📈 Strong Momentum Trends:")
            for momentum in strong_momentum:
                symbol, timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, current_price, last_updated = momentum
                print(f"      • {symbol} {timeframe}: {momentum_trend} momentum ({momentum_strength:.1f}% strength)")
        else:
            print("   ✅ No strong momentum trends detected")
        
        print("\n" + "="*80)
        print("✅ Stochastic RSI report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating Stochastic RSI report: {e}")

def main():
    """Main function to populate Stochastic RSI data"""
    print("🚀 Starting Stochastic RSI data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store Stochastic RSI for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        stoch_rsi_data = calculate_stoch_rsi_for_symbol(symbol, symbol_id)
        if stoch_rsi_data:
            if store_stoch_rsi_data(symbol_id, symbol, stoch_rsi_data):
                print(f"✅ Stored {len(stoch_rsi_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No Stochastic RSI data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_stoch_rsi_report()

if __name__ == "__main__":
    main()
