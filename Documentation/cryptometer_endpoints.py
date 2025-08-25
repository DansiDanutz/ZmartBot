#!/usr/bin/env python3
"""
Cryptometer API Data Collection Script for ETH USDT Analysis
Collects data from all 17 endpoints and analyzes win rates based on historical patterns
"""

import requests
import json
import time
from datetime import datetime
import pandas as pd

# API Configuration
API_KEY = "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"
BASE_URL = "https://api.cryptometer.io"

# ETH USDT Configuration
EXCHANGE = "binance"
MARKET_PAIR = "ETH-USDT"
SYMBOL = "ETH"

def make_api_request(endpoint, params=None):
    """Make API request with rate limiting"""
    if params is None:
        params = {}
    
    params['api_key'] = API_KEY
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        time.sleep(1.0)  # Rate limiting: 1 request per second
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} for {endpoint}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception for {endpoint}: {str(e)}")
        return None

def collect_all_endpoint_data():
    """Collect data from all 17 Cryptometer endpoints for ETH USDT"""
    
    endpoints_data = {}
    
    # 1. Market List
    print("1. Collecting Market List...")
    endpoints_data['market_list'] = make_api_request("/coinlist/", {"e": EXCHANGE})
    
    # 2. Cryptocurrency Info
    print("2. Collecting Cryptocurrency Info...")
    endpoints_data['crypto_info'] = make_api_request("/cryptocurrency-info/", {
        "e": EXCHANGE, 
        "filter": "defi"
    })
    
    # 3. Coin Info
    print("3. Collecting Coin Info...")
    endpoints_data['coin_info'] = make_api_request("/coininfo/")
    
    # 4. Forex Rates
    print("4. Collecting Forex Rates...")
    endpoints_data['forex_rates'] = make_api_request("/forex-rates/", {"source": "USD"})
    
    # 5. Volume Flow
    print("5. Collecting Volume Flow...")
    endpoints_data['volume_flow'] = make_api_request("/volume-flow/", {"timeframe": "1h"})
    
    # 6. Liquidity Lens
    print("6. Collecting Liquidity Lens...")
    endpoints_data['liquidity_lens'] = make_api_request("/liquidity-lens/", {"timeframe": "1h"})
    
    # 7. Volatility Index
    print("7. Collecting Volatility Index...")
    endpoints_data['volatility_index'] = make_api_request("/volatility-index/", {
        "e": EXCHANGE, 
        "timeframe": "1h"
    })
    
    # 8. OHLCV Candles
    print("8. Collecting OHLCV...")
    endpoints_data['ohlcv'] = make_api_request("/ohlcv/", {
        "e": EXCHANGE,
        "pair": MARKET_PAIR,
        "timeframe": "1h"
    })
    
    # 9. LS Ratio
    print("9. Collecting LS Ratio...")
    endpoints_data['ls_ratio'] = make_api_request("/ls-ratio/", {
        "e": "binance_futures",
        "pair": MARKET_PAIR,
        "timeframe": "1h"
    })
    
    # 10. Tickerlist Pro
    print("10. Collecting Tickerlist Pro...")
    endpoints_data['tickerlist_pro'] = make_api_request("/tickerlist-pro/", {"e": EXCHANGE})
    
    # 11. Merged Buy/Sell Volume
    print("11. Collecting Merged Trade Volume...")
    endpoints_data['merged_volume'] = make_api_request("/merged-trade-volume/", {
        "symbol": SYMBOL,
        "timeframe": "1h",
        "exchange_type": "spot"
    })
    
    # 12. Total Liquidation Data
    print("12. Collecting Liquidation Data...")
    endpoints_data['liquidation_data'] = make_api_request("/liquidation-data-v2/", {"symbol": "btc"})
    
    # 13. Trend Indicator V3
    print("13. Collecting Trend Indicator V3...")
    endpoints_data['trend_indicator'] = make_api_request("/trend-indicator-v3/")
    
    # 14. Rapid Movements
    print("14. Collecting Rapid Movements...")
    endpoints_data['rapid_movements'] = make_api_request("/rapid-movements/")
    
    # 15. xTrade (Whale Trades)
    print("15. Collecting Whale Trades...")
    endpoints_data['whale_trades'] = make_api_request("/xtrades/", {
        "e": EXCHANGE,
        "symbol": "btc"
    })
    
    # 16. Large Trades Activity
    print("16. Collecting Large Trades Activity...")
    endpoints_data['large_trades'] = make_api_request("/large-trades-activity/", {
        "e": EXCHANGE,
        "pair": MARKET_PAIR
    })
    
    # 17. AI Screener
    print("17. Collecting AI Screener...")
    endpoints_data['ai_screener'] = make_api_request("/ai-screener/", {"type": "full"})
    
    # 18. AI Screener Analysis (Bonus endpoint)
    print("18. Collecting AI Screener Analysis...")
    endpoints_data['ai_screener_analysis'] = make_api_request("/ai-screener-analysis/", {"symbol": "FUN"})
    
    return endpoints_data

def save_data_to_files(data):
    """Save collected data to JSON files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save individual endpoint data
    for endpoint_name, endpoint_data in data.items():
        if endpoint_data:
            filename = f"/home/ubuntu/cryptometer_{endpoint_name}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(endpoint_data, f, indent=2)
            print(f"Saved {endpoint_name} data to {filename}")
    
    # Save combined data
    combined_filename = f"/home/ubuntu/cryptometer_all_data_{timestamp}.json"
    with open(combined_filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved combined data to {combined_filename}")
    
    return combined_filename

def main():
    """Main execution function"""
    print("Starting Cryptometer API data collection for ETH USDT analysis...")
    print(f"Timestamp: {datetime.now()}")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Target: {MARKET_PAIR} on {EXCHANGE}")
    print("-" * 50)
    
    # Collect data from all endpoints
    all_data = collect_all_endpoint_data()
    
    # Save data to files
    combined_file = save_data_to_files(all_data)
    
    print("-" * 50)
    print("Data collection completed!")
    print(f"Combined data saved to: {combined_file}")
    
    # Basic summary
    successful_endpoints = sum(1 for data in all_data.values() if data is not None)
    total_endpoints = len(all_data)
    
    print(f"Successfully collected data from {successful_endpoints}/{total_endpoints} endpoints")
    
    return all_data, combined_file

if __name__ == "__main__":
    collected_data, data_file = main()

