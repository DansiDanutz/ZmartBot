#!/usr/bin/env python3
"""
Get REAL-TIME cryptocurrency prices
"""

import requests
import json

def get_real_prices():
    """
    Get real-time prices from CoinGecko API (free tier)
    """
    print("📊 Fetching REAL-TIME prices...")
    
    # CoinGecko API (free, no key needed)
    url = "https://api.coingecko.com/api/v3/simple/price"
    
    # Symbols to fetch
    symbols = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'solana': 'SOL',
        'ripple': 'XRP',
        'dogecoin': 'DOGE',
        'cardano': 'ADA',
        'polkadot': 'DOT',
        'avalanche-2': 'AVAX',
        'chainlink': 'LINK',
        'cosmos': 'ATOM',
        'litecoin': 'LTC',
        'binancecoin': 'BNB',
        'matic-network': 'MATIC',
        'uniswap': 'UNI'
    }
    
    params = {
        'ids': ','.join(symbols.keys()),
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_24hr_vol': 'true'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            prices = {}
            print("\n✅ REAL-TIME PRICES:")
            print("-"*50)
            
            for coin_id, symbol in symbols.items():
                if coin_id in data:
                    price = data[coin_id]['usd']
                    change = data[coin_id].get('usd_24h_change', 0)
                    volume = data[coin_id].get('usd_24h_vol', 0)
                    
                    prices[symbol] = {
                        'price': price,
                        'change_24h': change,
                        'volume_24h': volume
                    }
                    
                    # Format display
                    if price > 1:
                        price_str = f"${price:,.2f}"
                    else:
                        price_str = f"${price:.8f}"
                    
                    print(f"{symbol:6s}: {price_str:20s} ({change:+.2f}%)")
            
            print("-"*50)
            return prices
            
    except Exception as e:
        print(f"❌ Error fetching prices: {e}")
        
        # Fallback to more recent estimates
        print("\n⚠️ Using fallback prices (estimated):")
        fallback = {
            'BTC': {'price': 116500, 'change_24h': 2.0, 'volume_24h': 60000000000},
            'ETH': {'price': 4250, 'change_24h': 1.5, 'volume_24h': 20000000000},
            'SOL': {'price': 210, 'change_24h': 3.2, 'volume_24h': 4000000000},
            'XRP': {'price': 2.85, 'change_24h': 0.8, 'volume_24h': 3000000000},
            'DOGE': {'price': 0.095, 'change_24h': -0.5, 'volume_24h': 1500000000}
        }
        
        for symbol, data in fallback.items():
            print(f"{symbol}: ${data['price']:,.2f}")
        
        return fallback
    
    return {}

def get_cryptometer_prices():
    """
    Alternative: Get prices from Cryptometer API if available
    """
    # This would use your Cryptometer API key
    # But for now, using CoinGecko as it's free
    pass

if __name__ == "__main__":
    print("="*60)
    print("🔍 CHECKING REAL CRYPTOCURRENCY PRICES")
    print("="*60)
    
    prices = get_real_prices()
    
    if prices:
        print(f"\n📌 Bitcoin actual price: ${prices.get('BTC', {}).get('price', 'N/A'):,.2f}")
        print(f"📌 Your code was using: $96,547.82")
        print(f"📌 Difference: ${prices.get('BTC', {}).get('price', 116500) - 96547.82:,.2f}")
        
        print("\n💡 SOLUTION:")
        print("Update the KingFisher monitor to fetch real prices")
        print("instead of using hardcoded values!")
    
    print("="*60)