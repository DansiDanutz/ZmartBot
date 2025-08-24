#!/usr/bin/env python3
"""
Populate Volume Data
Calculates and stores volume analysis for all symbols in My Symbols list
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

def calculate_obv(prices, volumes):
    """Calculate On-Balance Volume (OBV)"""
    if len(prices) != len(volumes) or len(prices) < 2:
        return []
    
    obv = [volumes[0]]  # Start with first volume
    
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            obv.append(obv[i-1] + volumes[i])
        elif prices[i] < prices[i-1]:
            obv.append(obv[i-1] - volumes[i])
        else:
            obv.append(obv[i-1])
    
    return obv

def calculate_volume_analysis_for_symbol(symbol, symbol_id):
    """Calculate volume analysis for all timeframes for a symbol"""
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
                
                # Extract closing prices and volumes
                prices = [float(kline[4]) for kline in klines_data]
                volumes = [float(kline[5]) for kline in klines_data]
                
                if len(prices) >= 20 and len(volumes) >= 20:
                    current_volume = volumes[-1]
                    volume_sma_20 = sum(volumes[-20:]) / 20
                    volume_ratio = current_volume / volume_sma_20 if volume_sma_20 > 0 else 1.0
                    
                    # Calculate OBV
                    obv_values = calculate_obv(prices, volumes)
                    if obv_values:
                        obv = obv_values[-1]
                        obv_sma = sum(obv_values[-20:]) / 20 if len(obv_values) >= 20 else obv
                    else:
                        obv = current_volume
                        obv_sma = volume_sma_20
                    
                    # Detect volume spikes
                    volume_spike_detected = False
                    volume_spike_ratio = 0.0
                    if volume_ratio > 2.0:  # Volume spike threshold
                        volume_spike_detected = True
                        volume_spike_ratio = volume_ratio
                    
                    # Determine volume trend
                    volume_trend = "neutral"
                    if len(volumes) >= 10:
                        recent_volumes = volumes[-10:]
                        volume_trend_slope = np.polyfit(range(len(recent_volumes)), recent_volumes, 1)[0]
                        if volume_trend_slope > 0:
                            volume_trend = "increasing"
                        elif volume_trend_slope < 0:
                            volume_trend = "decreasing"
                    
                    # Detect volume divergence
                    volume_divergence_type = "none"
                    volume_divergence_strength = 0.0
                    
                    if len(prices) >= 10 and len(volumes) >= 10:
                        recent_prices = prices[-10:]
                        recent_volumes = volumes[-10:]
                        
                        # Calculate price and volume trends
                        price_trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
                        volume_trend_direction = "up" if recent_volumes[-1] > recent_volumes[0] else "down"
                        
                        # Detect divergence
                        if price_trend != volume_trend_direction:
                            if price_trend == "up" and volume_trend_direction == "down":
                                volume_divergence_type = "bearish"
                                volume_divergence_strength = abs(recent_volumes[-1] - recent_volumes[0]) / recent_volumes[0] if recent_volumes[0] > 0 else 0.0
                            elif price_trend == "down" and volume_trend_direction == "up":
                                volume_divergence_type = "bullish"
                                volume_divergence_strength = abs(recent_volumes[-1] - recent_volumes[0]) / recent_volumes[0] if recent_volumes[0] > 0 else 0.0
                    
                    # Calculate price-volume correlation
                    price_volume_correlation = 0.0
                    if len(prices) >= 20 and len(volumes) >= 20:
                        try:
                            correlation_matrix = np.corrcoef(prices[-20:], volumes[-20:])
                            price_volume_correlation = correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else 0.0
                        except:
                            price_volume_correlation = 0.0
                    
                    results[tf] = {
                        "current_volume": current_volume,
                        "volume_sma_20": volume_sma_20,
                        "volume_ratio": volume_ratio,
                        "obv": obv,
                        "obv_sma": obv_sma,
                        "volume_spike_detected": volume_spike_detected,
                        "volume_spike_ratio": volume_spike_ratio,
                        "volume_trend": volume_trend,
                        "volume_divergence_type": volume_divergence_type,
                        "volume_divergence_strength": volume_divergence_strength,
                        "price_volume_correlation": price_volume_correlation,
                        "current_price": current_price
                    }
                else:
                    print(f"⚠️ Insufficient data for {symbol} {tf}")
                    
            except Exception as e:
                print(f"⚠️ Error calculating {tf} for {symbol}: {e}")
                
        return results
        
    except Exception as e:
        print(f"❌ Error calculating volume for {symbol}: {e}")
        return {}

def store_volume_data(symbol_id, symbol, volume_data):
    """Store volume data in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for timeframe, data in volume_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO volume_data 
                (symbol_id, symbol, timeframe, current_volume, volume_sma_20, volume_ratio, 
                obv, obv_sma, volume_spike_detected, volume_spike_ratio, volume_trend,
                volume_divergence_type, volume_divergence_strength, price_volume_correlation, 
                current_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol_id, symbol, timeframe, data['current_volume'], data['volume_sma_20'], 
                data['volume_ratio'], data['obv'], data['obv_sma'], data['volume_spike_detected'],
                data['volume_spike_ratio'], data['volume_trend'], data['volume_divergence_type'],
                data['volume_divergence_strength'], data['price_volume_correlation'], 
                data['current_price'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing volume data for {symbol}: {e}")
        return False

def generate_volume_report():
    """Generate a comprehensive report of all volume data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, timeframe, current_volume, volume_sma_20, volume_ratio, 
                   volume_spike_detected, volume_spike_ratio, volume_trend, 
                   volume_divergence_type, volume_divergence_strength, price_volume_correlation,
                   current_price, last_updated
            FROM volume_data
            ORDER BY symbol, timeframe
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("📊 No volume data found in database")
            return
        
        print("\n" + "="*80)
        print("📊 VOLUME ANALYSIS COMPREHENSIVE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        current_symbol = None
        for row in data:
            symbol, timeframe, current_volume, volume_sma_20, volume_ratio, volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type, volume_divergence_strength, price_volume_correlation, current_price, last_updated = row
            
            if symbol != current_symbol:
                if current_symbol:
                    print("-" * 80)
                current_symbol = symbol
                print(f"\n🔸 {symbol} - Current Price: ${current_price:,.2f}")
                print("-" * 40)
            
            # Determine volume status emoji
            volume_status_emoji = "⚡" if volume_spike_detected else "📊"
            
            # Determine trend emoji
            trend_emoji = {
                "increasing": "📈",
                "decreasing": "📉",
                "neutral": "➡️"
            }.get(volume_trend, "➡️")
            
            # Determine divergence emoji
            divergence_emoji = {
                "bullish": "🟢↗️",
                "bearish": "🔴↘️",
                "none": ""
            }.get(volume_divergence_type, "")
            
            print(f"  {timeframe:>4} | Vol: {current_volume:>12,.0f} | SMA20: {volume_sma_20:>12,.0f} | Ratio: {volume_ratio:>5.2f} | {volume_status_emoji} {trend_emoji} {volume_trend:>10} | {divergence_emoji} {volume_divergence_type:>10}")
        
        print("\n" + "="*80)
        print("📈 VOLUME SUMMARY:")
        print("="*80)
        
        # Count by volume spike
        spike_count = sum(1 for row in data if row[5] == 1)
        no_spike_count = sum(1 for row in data if row[5] == 0)
        
        # Count by trend
        increasing_count = sum(1 for row in data if row[7] == "increasing")
        decreasing_count = sum(1 for row in data if row[7] == "decreasing")
        neutral_count = sum(1 for row in data if row[7] == "neutral")
        
        # Count by divergence
        bullish_divergence_count = sum(1 for row in data if row[8] == "bullish")
        bearish_divergence_count = sum(1 for row in data if row[8] == "bearish")
        no_divergence_count = sum(1 for row in data if row[8] == "none")
        
        print(f"   ⚡ Volume Spikes: {spike_count}")
        print(f"   📊 Normal Volume: {no_spike_count}")
        print(f"   📈 Increasing Trend: {increasing_count}")
        print(f"   📉 Decreasing Trend: {decreasing_count}")
        print(f"   ➡️ Neutral Trend: {neutral_count}")
        print(f"   🟢↗️ Bullish Divergences: {bullish_divergence_count}")
        print(f"   🔴↘️ Bearish Divergences: {bearish_divergence_count}")
        print(f"   ✅ No Divergences: {no_divergence_count}")
        
        print("\n" + "="*80)
        print("🎯 TRADING OPPORTUNITIES:")
        print("="*80)
        
        # Find volume spikes
        volume_spikes = [row for row in data if row[5] == 1]
        if volume_spikes:
            print("   ⚡ Volume Spike Signals:")
            for spike in volume_spikes:
                symbol, timeframe, current_volume, volume_sma_20, volume_ratio, volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type, volume_divergence_strength, price_volume_correlation, current_price, last_updated = spike
                print(f"      • {symbol} {timeframe}: {volume_ratio:.2f}x normal volume ({current_volume:,.0f} vs {volume_sma_20:,.0f} avg)")
        else:
            print("   ✅ No volume spikes detected")
        
        # Find bullish volume divergences
        bullish_divergences = [row for row in data if row[8] == "bullish"]
        if bullish_divergences:
            print("   🟢↗️ Bullish Volume Divergences (Price down, Volume up):")
            for divergence in bullish_divergences:
                symbol, timeframe, current_volume, volume_sma_20, volume_ratio, volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type, volume_divergence_strength, price_volume_correlation, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Volume divergence strength {volume_divergence_strength:.2f}")
        else:
            print("   ✅ No bullish volume divergences detected")
        
        # Find bearish volume divergences
        bearish_divergences = [row for row in data if row[8] == "bearish"]
        if bearish_divergences:
            print("   🔴↘️ Bearish Volume Divergences (Price up, Volume down):")
            for divergence in bearish_divergences:
                symbol, timeframe, current_volume, volume_sma_20, volume_ratio, volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type, volume_divergence_strength, price_volume_correlation, current_price, last_updated = divergence
                print(f"      • {symbol} {timeframe}: Volume divergence strength {volume_divergence_strength:.2f}")
        else:
            print("   ✅ No bearish volume divergences detected")
        
        # Find strong price-volume correlations
        strong_correlations = [row for row in data if abs(row[10]) > 0.7]
        if strong_correlations:
            print("   🔗 Strong Price-Volume Correlations:")
            for correlation in strong_correlations:
                symbol, timeframe, current_volume, volume_sma_20, volume_ratio, volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type, volume_divergence_strength, price_volume_correlation, current_price, last_updated = correlation
                correlation_type = "Positive" if price_volume_correlation > 0 else "Negative"
                print(f"      • {symbol} {timeframe}: {correlation_type} correlation {price_volume_correlation:.3f}")
        else:
            print("   ✅ No strong price-volume correlations detected")
        
        print("\n" + "="*80)
        print("✅ Volume report generation completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating volume report: {e}")

def main():
    """Main function to populate volume data"""
    print("🚀 Starting volume data population...")
    
    # Get active symbols
    symbols = get_active_symbols()
    if not symbols:
        print("❌ No active symbols found")
        return
    
    print(f"📊 Found {len(symbols)} active symbols")
    
    # Calculate and store volume for each symbol
    success_count = 0
    for symbol_id, symbol in symbols:
        print(f"\n🔸 Processing {symbol}...")
        
        volume_data = calculate_volume_analysis_for_symbol(symbol, symbol_id)
        if volume_data:
            if store_volume_data(symbol_id, symbol, volume_data):
                print(f"✅ Stored {len(volume_data)} timeframes for {symbol}")
                success_count += 1
            else:
                print(f"❌ Failed to store data for {symbol}")
        else:
            print(f"⚠️ No volume data calculated for {symbol}")
    
    print(f"\n🎉 Completed! Successfully processed {success_count}/{len(symbols)} symbols")
    
    # Generate comprehensive report
    generate_volume_report()

if __name__ == "__main__":
    main()
