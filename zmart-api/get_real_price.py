#!/usr/bin/env python3
"""
Get REAL market price for ETH from live APIs
"""

import requests
import json

def get_eth_price():
    """Get real ETH price from multiple sources"""

    # Try Binance first
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT', timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            print(f"✅ Binance ETH Price: ${price:,.2f}")
            return price
    except Exception as e:
        print(f"Binance error: {e}")

    # Try CoinGecko as backup
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['ethereum']['usd'])
            print(f"✅ CoinGecko ETH Price: ${price:,.2f}")
            return price
    except Exception as e:
        print(f"CoinGecko error: {e}")

    # Try Coinbase
    try:
        response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=ETH', timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['rates']['USD'])
            print(f"✅ Coinbase ETH Price: ${price:,.2f}")
            return price
    except Exception as e:
        print(f"Coinbase error: {e}")

    return None

if __name__ == "__main__":
    print("="*60)
    print("🔍 FETCHING REAL ETH MARKET PRICE")
    print("="*60)

    price = get_eth_price()

    if price:
        print(f"\n💰 Current ETH Price: ${price:,.2f}")

        # Calculate risk with real price
        import math

        # Updated ETH bounds (corrected for 0.715 risk at $3500)
        min_price = 140
        max_price = 12627

        # Calculate logarithmic risk
        if price <= min_price:
            risk = 0.0
        elif price >= max_price:
            risk = 1.0
        else:
            log_price = math.log(price)
            log_min = math.log(min_price)
            log_max = math.log(max_price)
            risk = (log_price - log_min) / (log_max - log_min)

        print(f"\n📊 Risk Calculation:")
        print(f"  Min: ${min_price}")
        print(f"  Max: ${max_price:,}")
        print(f"  Current: ${price:,.2f}")
        print(f"  Risk Value: {risk:.4f}")

        # Determine risk zone
        if risk < 0.3:
            zone = "🟢 LOW RISK - Accumulation Zone"
            bias = "LONG"
        elif risk < 0.7:
            zone = "🟡 MEDIUM RISK - Neutral Zone"
            bias = "NEUTRAL"
        else:
            zone = "🔴 HIGH RISK - Distribution Zone"
            bias = "SHORT"

        print(f"  Risk Zone: {zone}")
        print(f"  Market Bias: {bias}")

        # Save to file for orchestration
        result = {
            "symbol": "ETH",
            "price": price,
            "risk_value": risk,
            "risk_zone": zone,
            "market_bias": bias,
            "source": "Binance/CoinGecko/Coinbase"
        }

        with open('real_eth_price.json', 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n✅ Saved to real_eth_price.json")
    else:
        print("❌ Could not fetch ETH price from any source")