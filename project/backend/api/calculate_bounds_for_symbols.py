#!/usr/bin/env python3
"""
Calculate min and max bounds for DOGE, AVAX, DOT, LTC, and XMR
Using the discovered pattern: 75% of sustainable BTC ratios
"""

def calculate_symbol_bounds():
    """
    Calculate bounds for requested symbols using historical BTC ratios
    """
    
    # BTC reference bounds (Benjamin Cowen's values)
    BTC_MIN = 30000
    BTC_MAX = 299720
    
    print("🎯 CALCULATING BOUNDS FOR: DOGE, AVAX, DOT, LTC, XMR")
    print("=" * 100)
    print(f"Using BTC bounds: ${BTC_MIN:,} - ${BTC_MAX:,}")
    print(f"Formula: Min/Max = Historical_Sustainable_BTC_Ratio × 0.75 × BTC_Bounds")
    print()
    
    # Historical BTC trading ranges (from market data research)
    # These are sustainable levels, not absolute extremes
    HISTORICAL_BTC_RATIOS = {
        'DOGE': {
            'name': 'Dogecoin',
            'sustainable_low_btc': 0.0000020,   # DOGE typically bottoms around 20-30 sats
            'sustainable_high_btc': 0.0000200,  # DOGE peaks around 150-200 sats sustainably
            'notes': 'Meme coin with high volatility, 2021 peak was ~1200 sats but unsustainable'
        },
        'AVAX': {
            'name': 'Avalanche',
            'sustainable_low_btc': 0.0002000,   # AVAX bear market around 0.0002 BTC
            'sustainable_high_btc': 0.0025000,  # AVAX bull market sustains around 0.002-0.0025 BTC
            'notes': 'Layer 1 competitor, launched 2020, peaked at 0.003+ BTC'
        },
        'DOT': {
            'name': 'Polkadot',
            'sustainable_low_btc': 0.0001000,   # DOT bear market around 0.0001 BTC
            'sustainable_high_btc': 0.0008000,  # DOT sustains around 0.0006-0.0008 BTC in bull
            'notes': 'Parachain platform, launched 2020'
        },
        'LTC': {
            'name': 'Litecoin',
            'sustainable_low_btc': 0.0015000,   # LTC historically bottoms around 0.001-0.002 BTC
            'sustainable_high_btc': 0.0050000,  # LTC sustains around 0.004-0.005 BTC
            'notes': 'Silver to Bitcoin\'s gold, one of oldest alts'
        },
        'XMR': {
            'name': 'Monero',
            'sustainable_low_btc': 0.0020000,   # XMR bottoms around 0.002 BTC
            'sustainable_high_btc': 0.0060000,  # XMR sustains around 0.005-0.006 BTC
            'notes': 'Privacy coin, relatively stable BTC ratio'
        }
    }
    
    print("📊 HISTORICAL BTC RATIOS (Sustainable Levels):")
    print("-" * 100)
    
    for symbol, data in HISTORICAL_BTC_RATIOS.items():
        print(f"\n{symbol} ({data['name']}):")
        print(f"  Sustainable Low:  {data['sustainable_low_btc']:.8f} BTC")
        print(f"  Sustainable High: {data['sustainable_high_btc']:.8f} BTC")
        print(f"  Notes: {data['notes']}")
    
    print("\n" + "=" * 100)
    print("💰 CALCULATED BOUNDS (Using 75% of Sustainable Levels):")
    print("-" * 100)
    
    results = {}
    
    print(f"\n{'Symbol':<8} {'Min Ratio':>12} {'Max Ratio':>12} | {'Min Price':>12} {'Max Price':>12} | {'Growth':>8}")
    print("-" * 100)
    
    for symbol, data in HISTORICAL_BTC_RATIOS.items():
        # Apply the discovered formula: 75% of sustainable levels
        min_ratio = data['sustainable_low_btc'] * 0.75
        max_ratio = data['sustainable_high_btc'] * 0.75
        
        # Convert to USD prices
        min_price = min_ratio * BTC_MIN
        max_price = max_ratio * BTC_MAX
        
        # Calculate growth multiple
        growth = max_price / min_price if min_price > 0 else 0
        
        results[symbol] = {
            'min': min_price,
            'max': max_price,
            'min_ratio': min_ratio,
            'max_ratio': max_ratio,
            'growth': growth
        }
        
        print(f"{symbol:<8} {min_ratio:>12.8f} {max_ratio:>12.8f} | "
              f"${min_price:>11.2f} ${max_price:>11.2f} | {growth:>7.1f}x")
    
    # Generate Python dict for ULTIMATE_COMPLETE_RISKMETRIC
    print("\n" + "=" * 100)
    print("📝 PYTHON DICT FOR ULTIMATE_COMPLETE_RISKMETRIC.py:")
    print("-" * 100)
    
    inception_dates = {
        'DOGE': '2013-12-15',
        'AVAX': '2020-09-22',
        'DOT': '2020-08-19',
        'LTC': '2011-10-07',
        'XMR': '2014-04-18'
    }
    
    for symbol in ['DOGE', 'AVAX', 'DOT', 'LTC', 'XMR']:
        r = results[symbol]
        inception = inception_dates[symbol]
        print(f"        '{symbol}': {{'min': {r['min']:.2f}, 'max': {r['max']:.2f}, 'inception': '{inception}'}},")
    
    # Verify calculations
    print("\n" + "=" * 100)
    print("✅ VERIFICATION:")
    print("-" * 100)
    
    for symbol, r in results.items():
        print(f"\n{symbol}:")
        print(f"  Min: {r['min_ratio']:.8f} × ${BTC_MIN:,} = ${r['min']:.2f}")
        print(f"  Max: {r['max_ratio']:.8f} × ${BTC_MAX:,} = ${r['max']:.2f}")
        print(f"  Risk Range: {r['growth']:.1f}x growth potential")
    
    # Compare with any known values
    print("\n" + "=" * 100)
    print("📊 REASONABLENESS CHECK:")
    print("-" * 100)
    
    current_prices = {
        'DOGE': 0.35,    # Approximate current price
        'AVAX': 40,      # Approximate current price
        'DOT': 7,        # Approximate current price
        'LTC': 100,      # Approximate current price
        'XMR': 160,      # Approximate current price
    }
    
    for symbol, current in current_prices.items():
        r = results[symbol]
        if r['min'] <= current <= r['max']:
            position = (current - r['min']) / (r['max'] - r['min'])
            print(f"{symbol} at ${current}: Within range ✅ (Risk ~{position:.2f})")
        else:
            print(f"{symbol} at ${current}: Outside range ❌")
    
    return results

if __name__ == "__main__":
    results = calculate_symbol_bounds()