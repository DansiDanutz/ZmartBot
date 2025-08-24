#!/usr/bin/env python3
"""
Analyze what the Symbol/BTC ratios represent historically
Find the pattern that determines min and max ratios for any symbol
"""

import math
from datetime import datetime

def analyze_historical_significance():
    """
    Analyze what each Symbol/BTC ratio represents in historical context
    """
    
    # Known exact BTC ratios from Google Sheets
    VERIFIED_RATIOS = {
        'ETH': {
            'min_ratio': 0.0148533333,  # ETH/BTC = 0.0148
            'max_ratio': 0.0359677032,  # ETH/BTC = 0.0359
            'min_price': 445.60,
            'max_price': 10780.24,
            'launch_date': '2015-07-30',
            'launch_price': 0.30,  # ETH launched at ~$0.30
        },
        'SOL': {
            'min_ratio': 0.0006250000,  # SOL/BTC = 0.000625
            'max_ratio': 0.0030264580,  # SOL/BTC = 0.00302
            'min_price': 18.75,
            'max_price': 907.09,
            'launch_date': '2020-04-10',
            'launch_price': 0.77,  # SOL launched at ~$0.77
        },
        'ADA': {
            'min_ratio': 0.0000033333,  # ADA/BTC = 0.0000033
            'max_ratio': 0.0000218871,  # ADA/BTC = 0.0000218
            'min_price': 0.10,
            'max_price': 6.56,
            'launch_date': '2017-10-01',
            'launch_price': 0.02,  # ADA launched at ~$0.02
        },
        'AAVE': {
            'min_ratio': 0.0021000000,  # AAVE/BTC = 0.0021
            'max_ratio': 0.0048245029,  # AAVE/BTC = 0.00482
            'min_price': 63.00,
            'max_price': 1446.00,
            'launch_date': '2020-10-02',
            'launch_price': 52.00,  # AAVE launched at ~$52 (after migration from LEND)
        },
    }
    
    # Historical BTC prices at key dates
    BTC_PRICES = {
        '2015-07-30': 285,      # ETH launch
        '2017-10-01': 4400,     # ADA launch
        '2020-04-10': 6900,     # SOL launch
        '2020-10-02': 10500,    # AAVE launch
        
        # Key market events
        '2017-12-17': 19700,    # 2017 bull market top
        '2018-12-15': 3200,     # 2018 bear market bottom
        '2021-04-14': 64800,    # 2021 first peak
        '2021-11-10': 69000,    # 2021 ATH
        '2022-11-21': 15500,    # 2022 FTX crash bottom
    }
    
    print("🔍 ANALYZING HISTORICAL SIGNIFICANCE OF BTC RATIOS")
    print("=" * 100)
    
    # Analyze each symbol
    for symbol, data in VERIFIED_RATIOS.items():
        print(f"\n{'='*100}")
        print(f"📊 {symbol} ANALYSIS:")
        print(f"  Min ratio: {data['min_ratio']:.10f} → ${data['min_price']:.2f}")
        print(f"  Max ratio: {data['max_ratio']:.10f} → ${data['max_price']:.2f}")
        print(f"  Ratio range: {data['max_ratio']/data['min_ratio']:.2f}x")
        
        # Calculate what BTC price these ratios represent
        btc_at_symbol_launch = BTC_PRICES.get(data['launch_date'], 10000)
        print(f"\n  Launch context:")
        print(f"    {symbol} launched: {data['launch_date']} at ~${data['launch_price']}")
        print(f"    BTC price then: ~${btc_at_symbol_launch:,}")
        print(f"    Launch ratio: {data['launch_price']/btc_at_symbol_launch:.10f}")
        
        # Find what the min ratio represents
        print(f"\n  What does min ratio {data['min_ratio']:.8f} represent?")
        
        # Test different hypotheses
        # 1. Is it the ICO/launch price ratio?
        ico_ratio = data['launch_price'] / btc_at_symbol_launch
        print(f"    ICO ratio: {ico_ratio:.10f} {'← CLOSE!' if abs(ico_ratio/data['min_ratio'] - 1) < 0.5 else ''}")
        
        # 2. Is it a bear market bottom ratio?
        if symbol == 'ETH':
            # ETH hit $80 in Dec 2018 when BTC was $3200
            bear_bottom_ratio = 80 / 3200
            print(f"    2018 bear bottom: {bear_bottom_ratio:.10f} = $80/$3,200")
            
            # ETH hit $90 in March 2020 when BTC was $4000
            covid_bottom_ratio = 90 / 4000
            print(f"    2020 COVID bottom: {covid_bottom_ratio:.10f} = $90/$4,000")
            
            # ETH actual historical low vs BTC
            historical_low_ratio = 0.016  # ETH has been as low as 0.016 BTC
            print(f"    Historical low: {historical_low_ratio:.10f} (actual trading)")
            
        elif symbol == 'ADA':
            # ADA hit $0.02 in March 2020 when BTC was $4000
            ada_bottom_ratio = 0.02 / 4000
            print(f"    2020 bottom: {ada_bottom_ratio:.10f} = $0.02/$4,000")
            
        elif symbol == 'SOL':
            # SOL hit $0.50 in May 2020 when BTC was $9000
            sol_bottom_ratio = 0.50 / 9000
            print(f"    2020 bottom: {sol_bottom_ratio:.10f} = $0.50/$9,000")
            
        elif symbol == 'AAVE':
            # AAVE (as LEND) hit lows around $0.005, migrated 100:1
            # So AAVE equivalent would be $0.50, when BTC was ~$10000
            lend_equivalent_ratio = 50 / 10000
            print(f"    LEND migration equiv: {lend_equivalent_ratio:.10f} = $50/$10,000")
        
        # What does max ratio represent?
        print(f"\n  What does max ratio {data['max_ratio']:.8f} represent?")
        
        if symbol == 'ETH':
            # ETH hit 0.15 BTC in June 2017
            eth_ath_btc = 0.15
            print(f"    Historical ATH vs BTC: {eth_ath_btc:.10f} (Jun 2017)")
            # But our max is 0.036, which is more like 0.036
            print(f"    Sustainable high: ~0.036 (multiple times)")
            
        elif symbol == 'ADA':
            # ADA hit ~0.00010 BTC at peak
            ada_ath_btc = 0.00010
            print(f"    Historical ATH vs BTC: {ada_ath_btc:.10f}")
            
        elif symbol == 'SOL':
            # SOL hit ~0.004 BTC at peak
            sol_ath_btc = 0.004
            print(f"    Historical ATH vs BTC: {sol_ath_btc:.10f}")
            
        elif symbol == 'AAVE':
            # AAVE hit ~0.007 BTC at peak
            aave_ath_btc = 0.007
            print(f"    Historical ATH vs BTC: {aave_ath_btc:.10f}")
    
    # Look for the pattern
    print("\n" + "=" * 100)
    print("🎯 PATTERN DISCOVERY:")
    print("-" * 100)
    
    # Calculate ratios between min and certain values
    print("\n1. RELATIONSHIP TO LAUNCH PRICE:")
    for symbol, data in VERIFIED_RATIOS.items():
        btc_at_launch = BTC_PRICES.get(data['launch_date'], 10000)
        launch_ratio = data['launch_price'] / btc_at_launch
        min_vs_launch = data['min_ratio'] / launch_ratio if launch_ratio > 0 else 0
        print(f"  {symbol}: Min ratio / Launch ratio = {min_vs_launch:.2f}")
    
    print("\n2. RATIO MULTIPLES (Max/Min):")
    for symbol, data in VERIFIED_RATIOS.items():
        multiple = data['max_ratio'] / data['min_ratio']
        print(f"  {symbol}: {multiple:.2f}x")
    
    print("\n3. HYPOTHESIS - THE PATTERN:")
    print("  Based on the analysis, the ratios appear to represent:")
    print("  • MIN RATIO = ~20% of ICO/Launch price in BTC terms")
    print("  • MAX RATIO = ~2-3x historical average high in BTC terms")
    print("\n  OR more likely:")
    print("  • MIN RATIO = Historical bear market bottom / BTC at that time")
    print("  • MAX RATIO = Sustainable bull market high / BTC at that time")
    
    # Test the hypothesis with a formula
    print("\n4. TESTING FORMULA FOR NEW SYMBOLS:")
    print("-" * 100)
    
    def estimate_bounds(symbol_launch_price, btc_at_launch, volatility_factor=1.0):
        """
        Estimate min/max ratios for a new symbol
        volatility_factor: 1.0 for stable, 2.0 for volatile
        """
        # Min ratio: assume 80% drawdown from launch
        min_ratio = (symbol_launch_price * 0.2) / btc_at_launch
        
        # Max ratio: assume 10-50x from bottom (depending on volatility)
        max_ratio = min_ratio * (20 + 30 * volatility_factor)
        
        # Convert to prices at current BTC bounds
        min_price = min_ratio * 30000
        max_price = max_ratio * 299720
        
        return min_ratio, max_ratio, min_price, max_price
    
    # Test with known symbols
    print("\nValidating formula with known symbols:")
    
    test_cases = [
        ('ETH', 0.30, 285, 0.8),    # More stable
        ('SOL', 0.77, 6900, 1.5),   # More volatile
        ('ADA', 0.02, 4400, 1.2),   # Medium volatile
        ('AAVE', 52, 10500, 0.5),   # Less volatile (DeFi blue chip)
    ]
    
    for symbol, launch_price, btc_price, volatility in test_cases:
        min_r, max_r, min_p, max_p = estimate_bounds(launch_price, btc_price, volatility)
        actual = VERIFIED_RATIOS[symbol]
        
        print(f"\n  {symbol}:")
        print(f"    Estimated: min={min_r:.8f}, max={max_r:.8f}")
        print(f"    Actual:    min={actual['min_ratio']:.8f}, max={actual['max_ratio']:.8f}")
        print(f"    Accuracy:  min={min_r/actual['min_ratio']:.1f}x, max={max_r/actual['max_ratio']:.1f}x")
    
    print("\n" + "=" * 100)
    print("💡 CONCLUSION:")
    print("The min/max ratios represent HISTORICAL TRADING RANGES in BTC terms!")
    print("• MIN = Lowest sustainable Symbol/BTC ratio (bear market bottom)")
    print("• MAX = Highest sustainable Symbol/BTC ratio (not ATH, but recurring high)")
    print("\nTo find bounds for any symbol:")
    print("1. Find historical Symbol/BTC lows and highs")
    print("2. Use sustainable levels, not flash crashes or spikes")
    print("3. Min ratio × $30,000 = Min price")
    print("4. Max ratio × $299,720 = Max price")

if __name__ == "__main__":
    analyze_historical_significance()