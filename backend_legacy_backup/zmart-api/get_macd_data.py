#!/usr/bin/env python3
"""
Get MACD Data for Multiple Symbols and Timeframes
Calculates and displays MACD values for different timeframes
"""

import requests
import sys
import os

# Add the src directory to the path to import the technical analysis service
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from services.technical_analysis_service import TechnicalAnalysisService

def get_macd_for_symbol_timeframe(symbol, timeframe):
    """Get MACD data for a specific symbol and timeframe"""
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
        
        # Get klines data
        klines_response = requests.get(
            f"https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": interval_map[timeframe], "limit": limit_map[timeframe]},
            timeout=10
        )
        klines_response.raise_for_status()
        klines_data = klines_response.json()
        
        # Extract closing prices
        prices = [float(kline[4]) for kline in klines_data]
        
        if len(prices) >= 26:
            # Calculate MACD
            ta_service = TechnicalAnalysisService()
            macd_line, signal_line, histogram = ta_service.calculate_macd(prices)
            
            if macd_line and signal_line and histogram:
                # Get latest values
                macd_value = macd_line[-1]
                signal_value = signal_line[-1]
                hist_value = histogram[-1]
                
                # Determine signal
                if len(macd_line) >= 2 and len(signal_line) >= 2:
                    prev_macd = macd_line[-2]
                    prev_signal = signal_line[-2]
                    
                    if prev_macd <= prev_signal and macd_value > signal_value:
                        signal_status = "🟢 Bullish Crossover"
                    elif prev_macd >= prev_signal and macd_value < signal_value:
                        signal_status = "🔴 Bearish Crossover"
                    elif macd_value > signal_value:
                        signal_status = "🟢 Bullish"
                    else:
                        signal_status = "🔴 Bearish"
                else:
                    signal_status = "⚪ Neutral"
                
                return {
                    "macd": macd_value,
                    "signal": signal_value,
                    "histogram": hist_value,
                    "status": signal_status
                }
        
        return None
        
    except Exception as e:
        print(f"Error getting MACD for {symbol} {timeframe}: {e}")
        return None

def main():
    """Main function to get MACD data for multiple symbols"""
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    timeframes = ["15m", "1h", "4h", "1d"]
    
    print("📊 MACD DATA FOR 3 SYMBOLS")
    print("=" * 80)
    
    for symbol in symbols:
        print(f"\n🔸 {symbol}:")
        print("-" * 60)
        print(f"{'Timeframe':<8} | {'MACD Line':<12} | {'Signal Line':<12} | {'Histogram':<12} | {'Status':<20}")
        print("-" * 80)
        
        for timeframe in timeframes:
            macd_data = get_macd_for_symbol_timeframe(symbol, timeframe)
            
            if macd_data:
                print(f"{timeframe:<8} | {macd_data['macd']:<12.4f} | {macd_data['signal']:<12.4f} | {macd_data['histogram']:<12.4f} | {macd_data['status']:<20}")
            else:
                print(f"{timeframe:<8} | {'N/A':<12} | {'N/A':<12} | {'N/A':<12} | {'Error':<20}")
        
        print()

if __name__ == "__main__":
    main()
