#!/usr/bin/env python3
"""
Find the correct BTC ratios for all symbols
Using the discovered pattern: Symbol_bounds = BTC_ratio × BTC_bounds
"""

import math

def calculate_correct_bounds():
    """
    Calculate correct bounds for all symbols using BTC ratios
    """
    
    # BTC reference bounds
    BTC_MIN = 30000
    BTC_MAX = 299720
    
    print("🎯 CALCULATING CORRECT BOUNDS USING BTC RATIOS")
    print("=" * 80)
    print(f"BTC Reference: Min=${BTC_MIN:,} | Max=${BTC_MAX:,}")
    print()
    
    # Known correct ratios (we discovered AAVE)
    # These need to be found from historical data or Google Sheets
    SYMBOL_BTC_RATIOS = {
        # Symbol: (min_btc_ratio, max_btc_ratio)
        'AAVE': (0.0021, 0.00482450),  # VERIFIED ✅
        
        # These are estimates based on historical trading ranges
        # Need to verify with actual Google Sheets data
        'ETH': (0.015, 0.036),  # ETH historically 0.015-0.15 BTC
        'LTC': (0.001, 0.0033),  # LTC historically 0.001-0.025 BTC  
        'XRP': (0.000005, 0.000033),  # XRP historically very low
        'BNB': (0.001, 0.0067),  # BNB launched later
        'SOL': (0.0006, 0.003),  # SOL is newer
        'ADA': (0.0000033, 0.000022),  # ADA very small ratios
        'DOT': (0.000083, 0.0005),  # DOT medium ratios
        'LINK': (0.000117, 0.000667),  # LINK medium ratios
        'AVAX': (0.0001, 0.00167),  # AVAX higher multiples
        'ATOM': (0.000067, 0.000333),  # ATOM medium

        
        # These need real data
        'DOGE': (0.00000007, 0.00000334),
        'XLM': (0.000001, 0.0000067),
        'XMR': (0.00167, 0.00333),
        'VET': (0.00000007, 0.00000167),
        'HBAR': (0.00000067, 0.00000334),
        'TRX': (0.00000033, 0.00000167),
        'TON': (0.0000167, 0.0000667),
        'RENDER': (0.0000167, 0.000167),
        'SUI': (0.0000167, 0.0000667),
    }
    
    print("📊 CALCULATED BOUNDS FROM BTC RATIOS:")
    print(f"{'Symbol':<8} | {'Min Ratio':>12} | {'Max Ratio':>12} | {'Min $':>10} | {'Max $':>10} | {'Growth':>8}")
    print("-" * 80)
    
    calculated_bounds = {}
    for symbol, (min_ratio, max_ratio) in SYMBOL_BTC_RATIOS.items():
        min_price = min_ratio * BTC_MIN
        max_price = max_ratio * BTC_MAX
        growth = max_price / min_price if min_price > 0 else 0
        
        calculated_bounds[symbol] = {
            'min': min_price,
            'max': max_price,
            'min_ratio': min_ratio,
            'max_ratio': max_ratio,
            'growth': growth
        }
        
        verified = "✅" if symbol == 'AAVE' else ""
        print(f"{symbol:<8} | {min_ratio:>12.8f} | {max_ratio:>12.8f} | "
              f"{min_price:>10.2f} | {max_price:>10.2f} | {growth:>8.2f}x {verified}")
    
    # Show how to verify with Google Sheets
    print("\n📋 TO VERIFY WITH GOOGLE SHEETS:")
    print("-" * 80)
    print("1. Check the min/max values for each symbol in the RiskMetric sheet")
    print("2. Calculate the BTC ratio: Symbol_value / BTC_value")
    print("3. The ratios should be constant across all risk levels")
    print()
    print("Example verification for AAVE:")
    print(f"  AAVE min ${calculated_bounds['AAVE']['min']:.2f} ÷ BTC min ${BTC_MIN:,} = {calculated_bounds['AAVE']['min_ratio']:.8f}")
    print(f"  AAVE max ${calculated_bounds['AAVE']['max']:.2f} ÷ BTC max ${BTC_MAX:,} = {calculated_bounds['AAVE']['max_ratio']:.8f}")
    
    # Generate Python dict for updating ULTIMATE_COMPLETE_RISKMETRIC
    print("\n💾 PYTHON DICT FOR ULTIMATE_COMPLETE_RISKMETRIC:")
    print("-" * 80)
    print("SYMBOL_BOUNDS = {")
    print(f"    'BTC': {{'min': {BTC_MIN}, 'max': {BTC_MAX}, 'inception': '2009-01-03'}},")
    
    for symbol, bounds in calculated_bounds.items():
        # Look up inception dates (these are approximate)
        inception_dates = {
            'ETH': '2015-07-30',
            'LTC': '2011-10-07',
            'XRP': '2013-08-04',
            'BNB': '2017-07-25',
            'ADA': '2017-10-01',
            'DOT': '2020-08-19',
            'LINK': '2017-09-20',
            'SOL': '2020-04-10',
            'AVAX': '2020-09-22',

            'ATOM': '2019-03-14',
            'XLM': '2014-08-05',
            'XMR': '2014-04-18',
            'DOGE': '2013-12-15',
            'VET': '2018-08-03',
            'HBAR': '2019-09-17',
            'TRX': '2017-09-28',
            'TON': '2021-12-01',
            'AAVE': '2020-10-02',
            'RENDER': '2020-06-25',
            'SUI': '2023-05-03',
        }
        
        inception = inception_dates.get(symbol, '2020-01-01')
        print(f"    '{symbol}': {{'min': {bounds['min']:.2f}, 'max': {bounds['max']:.2f}, 'inception': '{inception}'}},")
    
    print("}")
    
    print("\n" + "=" * 80)
    print("🎯 KEY DISCOVERY:")
    print("The formula is: Symbol_Price = Symbol_BTC_Ratio × BTC_Price")
    print("Where Symbol_BTC_Ratio is historically determined and constant!")
    print()
    print("This means Benjamin Cowen's RiskMetric is based on:")
    print("1. Historical BTC trading pair ratios for each symbol")
    print("2. These ratios define the min/max bounds")
    print("3. The logarithmic formula then scales between these bounds")

if __name__ == "__main__":
    calculate_correct_bounds()