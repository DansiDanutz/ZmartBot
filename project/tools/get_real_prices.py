#!/usr/bin/env python3
"""
Get REAL current market prices for August 6, 2025
"""

import requests
import json
from datetime import datetime

def get_current_prices():
    """Get real-time cryptocurrency prices"""
    print("="*80)
    print(f"REAL MARKET PRICES - {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
    print("="*80)
    
    # CoinGecko API (free tier)
    symbols = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH', 
        'solana': 'SOL',
        'cardano': 'ADA'
    }
    
    try:
        # Get prices from CoinGecko
        ids = ','.join(symbols.keys())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            print("\nCurrent Market Prices:")
            print("-"*40)
            
            prices = {}
            for coin_id, symbol in symbols.items():
                if coin_id in data:
                    price = data[coin_id]['usd']
                    prices[symbol] = price
                    print(f"{symbol}: ${price:,.2f}")
            
            return prices
        else:
            print(f"Error fetching prices: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
        
    # Fallback to Binance API
    try:
        print("\nTrying Binance API...")
        binance_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT']
        prices = {}
        
        for symbol in binance_symbols:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                coin = symbol.replace('USDT', '')
                price = float(data['price'])
                prices[coin] = price
                print(f"{coin}: ${price:,.2f}")
        
        return prices
        
    except Exception as e:
        print(f"Binance API error: {e}")
    
    return None

def calculate_risk_values(prices):
    """Calculate risk values for current prices"""
    print("\n" + "="*80)
    print("RISK VALUE CALCULATIONS")
    print("="*80)
    
    # Benjamin Cowen's exact min/max values
    BOUNDS = {
        'BTC': {'min': 30000, 'max': 299720},
        'ETH': {'min': 445.60, 'max': 10780.24},
        'SOL': {'min': 18.75, 'max': 907.09},
        'ADA': {'min': 0.10, 'max': 6.56}
    }
    
    import math
    
    print(f"\n{'Symbol':<10} {'Current Price':<15} {'Risk Value':<15} {'Zone'}")
    print("-"*60)
    
    risk_values = {}
    for symbol, price in prices.items():
        if symbol in BOUNDS:
            min_price = BOUNDS[symbol]['min']
            max_price = BOUNDS[symbol]['max']
            
            if price <= min_price:
                risk = 0.0
            elif price >= max_price:
                risk = 1.0
            else:
                risk = (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))
            
            # Determine zone
            if risk < 0.25:
                zone = "BUY ZONE"
            elif risk < 0.40:
                zone = "EARLY BULL"
            elif risk < 0.60:
                zone = "NEUTRAL"
            elif risk < 0.75:
                zone = "LATE BULL"
            else:
                zone = "SELL ZONE"
            
            risk_values[symbol] = {
                'price': price,
                'risk': risk,
                'zone': zone
            }
            
            print(f"{symbol:<10} ${price:<14,.2f} {risk:<15.4f} {zone}")
    
    return risk_values

def main():
    print("\n" + "🔴"*40)
    print("GETTING REAL MARKET DATA - NO MOCK VALUES!")
    print("🔴"*40)
    
    # Get real prices
    prices = get_current_prices()
    
    if prices:
        # Calculate risk values
        risk_values = calculate_risk_values(prices)
        
        # Save to file
        output = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%B %d, %Y'),
            'prices': prices,
            'risk_values': risk_values
        }
        
        with open('real_market_data.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("\n" + "="*80)
        print("REAL DATA SAVED")
        print("="*80)
        print("✅ Real market data saved to: real_market_data.json")
        print(f"📅 Date: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
    else:
        print("\n❌ Could not fetch real market prices")
        print("Please provide the current prices manually")

if __name__ == "__main__":
    main()