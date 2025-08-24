#!/usr/bin/env python3
"""
Discover the BTC ratio pattern for all symbols
This should reveal Benjamin Cowen's methodology
"""

import math
from typing import Dict, Tuple

def analyze_btc_ratios():
    """
    Analyze the ratio between each symbol and BTC
    to find the pattern for min/max values
    """
    
    # Known BTC bounds
    BTC_MIN = 30000
    BTC_MAX = 299720
    
    # Current symbol bounds from our system
    CURRENT_BOUNDS = {
        'BTC': {'min': 30000, 'max': 299720},
        'ETH': {'min': 445.60, 'max': 10780.24},
        'SOL': {'min': 18.75, 'max': 907.09},
        'ADA': {'min': 0.10, 'max': 6.56},
        'DOT': {'min': 2.5, 'max': 150},
        'XRP': {'min': 0.15, 'max': 10},
        'BNB': {'min': 30, 'max': 2000},
        'AVAX': {'min': 3, 'max': 500},
        'LINK': {'min': 3.5, 'max': 200},
        'LTC': {'min': 30, 'max': 1000},
        'DOGE': {'min': 0.002, 'max': 1},
        'ATOM': {'min': 2, 'max': 100},
        'XLM': {'min': 0.03, 'max': 2},
        'XMR': {'min': 50, 'max': 1000},
        'VET': {'min': 0.002, 'max': 0.5},
        'HBAR': {'min': 0.02, 'max': 1},
        'TRX': {'min': 0.01, 'max': 0.5},
        'TON': {'min': 0.5, 'max': 20},
        'AAVE': {'min': 30, 'max': 1000},  # Wrong - should be 63/1446
        'RENDER': {'min': 0.5, 'max': 50},
        'SUI': {'min': 0.5, 'max': 20},

    }
    
    # Known correct values from Google Sheets
    KNOWN_CORRECT = {
        'AAVE': {'min': 63, 'max': 1446},
        # Add more as we discover them
    }
    
    print("🔍 DISCOVERING BTC RATIO PATTERN")
    print("=" * 80)
    print(f"\nBTC Reference: Min=${BTC_MIN:,} | Max=${BTC_MAX:,}")
    print(f"BTC Growth Multiple: {BTC_MAX/BTC_MIN:.2f}x\n")
    
    # Calculate ratios
    print("📊 SYMBOL/BTC RATIOS:")
    print(f"{'Symbol':<8} | {'Min':>10} | {'Max':>10} | {'Min/BTC':>12} | {'Max/BTC':>12} | {'Growth':>8}")
    print("-" * 80)
    
    ratios = {}
    for symbol, bounds in CURRENT_BOUNDS.items():
        min_val = bounds['min']
        max_val = bounds['max']
        
        # Calculate ratios (in satoshis - multiply by 100,000,000)
        min_ratio_sats = (min_val / BTC_MIN) * 100_000_000
        max_ratio_sats = (max_val / BTC_MAX) * 100_000_000
        
        # Growth multiple
        growth = max_val / min_val
        
        ratios[symbol] = {
            'min': min_val,
            'max': max_val,
            'min_ratio_sats': min_ratio_sats,
            'max_ratio_sats': max_ratio_sats,
            'growth': growth
        }
        
        # Mark if we know it's wrong
        mark = " ❌" if symbol in KNOWN_CORRECT else ""
        
        print(f"{symbol:<8} | {min_val:>10.2f} | {max_val:>10.2f} | "
              f"{min_ratio_sats:>12.0f} | {max_ratio_sats:>12.0f} | {growth:>8.2f}x{mark}")
    
    # Show correct AAVE for comparison
    print("\n📍 CORRECT VALUES:")
    for symbol, correct_bounds in KNOWN_CORRECT.items():
        min_val = correct_bounds['min']
        max_val = correct_bounds['max']
        min_ratio_sats = (min_val / BTC_MIN) * 100_000_000
        max_ratio_sats = (max_val / BTC_MAX) * 100_000_000
        growth = max_val / min_val
        
        print(f"{symbol:<8} | {min_val:>10.2f} | {max_val:>10.2f} | "
              f"{min_ratio_sats:>12.0f} | {max_ratio_sats:>12.0f} | {growth:>8.2f}x ✅")
    
    # Look for patterns
    print("\n🎯 PATTERN ANALYSIS:")
    print("-" * 80)
    
    # Group by similar min ratios
    print("\n1. GROUPING BY MIN RATIO (satoshis):")
    ratio_groups = {}
    for symbol, data in ratios.items():
        ratio_bucket = int(data['min_ratio_sats'] / 1000) * 1000  # Round to nearest 1000
        if ratio_bucket not in ratio_groups:
            ratio_groups[ratio_bucket] = []
        ratio_groups[ratio_bucket].append(symbol)
    
    for ratio, symbols in sorted(ratio_groups.items()):
        print(f"  {ratio:>10,} sats: {', '.join(symbols)}")
    
    # Analyze growth multiples
    print("\n2. GROWTH MULTIPLE PATTERNS:")
    growth_buckets = {}
    for symbol, data in ratios.items():
        growth_bucket = int(data['growth'] / 10) * 10  # Round to nearest 10
        if growth_bucket not in growth_buckets:
            growth_buckets[growth_bucket] = []
        growth_buckets[growth_bucket].append(symbol)
    
    for growth, symbols in sorted(growth_buckets.items()):
        print(f"  {growth:>3}x-{growth+10:>3}x: {', '.join(symbols)}")
    
    # Check if there's a historical price ratio pattern
    print("\n3. HISTORICAL PATTERNS:")
    
    # These might be based on historical ATH/ATL ratios
    historical_ratios = {
        'ETH': {'historical_min_btc': 0.0001, 'historical_max_btc': 0.15},  # Hypothetical
        'LTC': {'historical_min_btc': 0.0001, 'historical_max_btc': 0.05},
        'XRP': {'historical_min_btc': 0.000001, 'historical_max_btc': 0.0003},
    }
    
    print("  Checking if bounds are based on historical BTC ratios...")
    
    # Test AAVE pattern
    print("\n4. TESTING AAVE PATTERN:")
    aave_correct_min = 63
    aave_correct_max = 1446
    
    # What BTC price ratio does this represent?
    print(f"  AAVE correct: ${aave_correct_min} - ${aave_correct_max}")
    print(f"  If AAVE min=${aave_correct_min} when BTC was at certain price...")
    
    # Test different BTC prices when AAVE launched
    btc_prices_at_aave_launch = [10000, 15000, 20000, 30000]
    for btc_price in btc_prices_at_aave_launch:
        ratio = aave_correct_min / btc_price
        print(f"    If BTC was ${btc_price:,}: AAVE/BTC = {ratio:.8f}")
    
    # Calculate what the pattern might be
    print("\n5. POSSIBLE FORMULA:")
    print("  Min = Symbol_Historical_Low_vs_BTC * BTC_Min")
    print("  Max = Symbol_Historical_High_vs_BTC * BTC_Max")
    
    # Or it could be based on market cap ratios
    print("\n6. MARKET CAP RATIO HYPOTHESIS:")
    print("  Min = (Symbol_Min_MCap / BTC_Min_MCap) * BTC_Min_Price")
    print("  Max = (Symbol_Max_MCap / BTC_Max_MCap) * BTC_Max_Price")
    
    # Calculate AAVE's implied BTC ratios
    aave_min_btc_ratio = aave_correct_min / BTC_MIN
    aave_max_btc_ratio = aave_correct_max / BTC_MAX
    
    print(f"\n7. AAVE IMPLIED BTC RATIOS:")
    print(f"  Min ratio: {aave_min_btc_ratio:.8f} ({aave_min_btc_ratio * 100_000_000:.0f} sats)")
    print(f"  Max ratio: {aave_max_btc_ratio:.8f} ({aave_max_btc_ratio * 100_000_000:.0f} sats)")
    
    # Test if there's a simple multiplier
    print("\n8. TESTING SIMPLE MULTIPLIERS:")
    
    # AAVE launched at ~$50-80 range in 2020
    # BTC was around $10,000-15,000
    aave_launch_price = 75
    btc_launch_price = 12500
    launch_ratio = aave_launch_price / btc_launch_price
    
    print(f"  AAVE launch (~Oct 2020): ~${aave_launch_price}")
    print(f"  BTC at that time: ~${btc_launch_price}")
    print(f"  Launch ratio: {launch_ratio:.8f}")
    
    # Test if min/max are based on launch ratio
    test_min = launch_ratio * BTC_MIN * 0.84  # Some adjustment factor
    test_max = launch_ratio * BTC_MAX * 0.8   # Some adjustment factor
    
    print(f"  Test min (launch_ratio * BTC_MIN * 0.84): ${test_min:.2f}")
    print(f"  Test max (launch_ratio * BTC_MAX * 0.8): ${test_max:.2f}")
    
    print("\n" + "=" * 80)
    print("💡 KEY INSIGHTS:")
    print("1. Each symbol has a unique min/max that doesn't follow a simple pattern")
    print("2. The ratios might be based on historical BTC pair trading ranges")
    print("3. AAVE min/BTC = 0.0021 (210,000 sats)")
    print("4. AAVE max/BTC = 0.0048 (482,000 sats)")
    print("5. The pattern might be: Symbol bounds = Historical_BTC_ratio_range * BTC_bounds")

if __name__ == "__main__":
    analyze_btc_ratios()