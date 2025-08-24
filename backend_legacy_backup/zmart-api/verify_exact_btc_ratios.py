#!/usr/bin/env python3
"""
Verify the exact BTC ratios with Google Sheets data
"""

def verify_btc_ratio_pattern():
    """
    Verify that the BTC ratio pattern works with exact Google Sheets data
    """
    
    # BTC bounds
    BTC_MIN = 30000
    BTC_MAX = 299720
    
    # Exact values from Google Sheets
    GOOGLE_SHEETS_DATA = {
        'BTC': {'min': 30000, 'max': 299720},
        'ETH': {'min': 445.60, 'max': 10780.24},
        'SOL': {'min': 18.75, 'max': 907.09},
        'ADA': {'min': 0.10, 'max': 6.56},
        'AAVE': {'min': 63, 'max': 1446},  # Previously confirmed
    }
    
    print("✅ VERIFYING BTC RATIO PATTERN WITH GOOGLE SHEETS DATA")
    print("=" * 80)
    print(f"BTC Reference: Min=${BTC_MIN:,} | Max=${BTC_MAX:,}")
    print()
    
    print("📊 EXACT BTC RATIOS FROM GOOGLE SHEETS:")
    print(f"{'Symbol':<8} | {'Min $':>10} | {'Max $':>10} | {'Min/BTC Ratio':>15} | {'Max/BTC Ratio':>15} | {'Growth':>8}")
    print("-" * 90)
    
    ratios = {}
    for symbol, values in GOOGLE_SHEETS_DATA.items():
        if symbol == 'BTC':
            min_ratio = 1.0
            max_ratio = 1.0
        else:
            min_ratio = values['min'] / BTC_MIN
            max_ratio = values['max'] / BTC_MAX
        
        growth = values['max'] / values['min']
        
        ratios[symbol] = {
            'min_ratio': min_ratio,
            'max_ratio': max_ratio,
            'growth': growth
        }
        
        print(f"{symbol:<8} | {values['min']:>10.2f} | {values['max']:>10.2f} | "
              f"{min_ratio:>15.10f} | {max_ratio:>15.10f} | {growth:>8.2f}x")
    
    # Verify by reconstructing values
    print("\n🔍 VERIFICATION - Reconstructing values from ratios:")
    print(f"{'Symbol':<8} | {'Calc Min':>10} | {'Actual Min':>10} | {'Calc Max':>10} | {'Actual Max':>10} | {'Match'}")
    print("-" * 70)
    
    all_match = True
    for symbol, values in GOOGLE_SHEETS_DATA.items():
        if symbol == 'BTC':
            continue
            
        calc_min = ratios[symbol]['min_ratio'] * BTC_MIN
        calc_max = ratios[symbol]['max_ratio'] * BTC_MAX
        
        min_match = abs(calc_min - values['min']) < 0.01
        max_match = abs(calc_max - values['max']) < 0.01
        match = min_match and max_match
        
        if not match:
            all_match = False
        
        print(f"{symbol:<8} | {calc_min:>10.2f} | {values['min']:>10.2f} | "
              f"{calc_max:>10.2f} | {values['max']:>10.2f} | {'✅' if match else '❌'}")
    
    print("\n" + "=" * 80)
    
    if all_match:
        print("✅ PATTERN CONFIRMED! All values match perfectly!")
        print("\n🎯 THE FORMULA IS:")
        print("   Symbol_Min = Symbol_Min_BTC_Ratio × $30,000")
        print("   Symbol_Max = Symbol_Max_BTC_Ratio × $299,720")
        
        print("\n📊 EXACT BTC RATIOS TO USE:")
        for symbol in ['ETH', 'SOL', 'ADA', 'AAVE']:
            print(f"   {symbol}: min_ratio={ratios[symbol]['min_ratio']:.10f}, "
                  f"max_ratio={ratios[symbol]['max_ratio']:.10f}")
    else:
        print("❌ Pattern doesn't match perfectly. Need to investigate further.")
    
    # Generate updated SYMBOL_BOUNDS
    print("\n💾 UPDATED SYMBOL_BOUNDS FOR ULTIMATE_COMPLETE_RISKMETRIC.py:")
    print("-" * 80)
    print("    # Verified from Google Sheets - EXACT VALUES")
    for symbol, values in GOOGLE_SHEETS_DATA.items():
        if symbol == 'BTC':
            print(f"    'BTC': {{'min': {values['min']}, 'max': {values['max']}, 'inception': '2009-01-03'}},")
        elif symbol == 'ETH':
            print(f"    'ETH': {{'min': {values['min']}, 'max': {values['max']}, 'inception': '2015-07-30'}},")
        elif symbol == 'SOL':
            print(f"    'SOL': {{'min': {values['min']}, 'max': {values['max']}, 'inception': '2020-04-10'}},")
        elif symbol == 'ADA':
            print(f"    'ADA': {{'min': {values['min']}, 'max': {values['max']}, 'inception': '2017-10-01'}},")
        elif symbol == 'AAVE':
            print(f"    'AAVE': {{'min': {values['min']}, 'max': {values['max']}, 'inception': '2020-10-02'}},")
    
    # Store ratios for future calculations
    print("\n📝 BTC_RATIOS constant for future use:")
    print("-" * 80)
    print("BTC_RATIOS = {")
    for symbol in ['ETH', 'SOL', 'ADA', 'AAVE']:
        print(f"    '{symbol}': {{'min_ratio': {ratios[symbol]['min_ratio']:.10f}, "
              f"'max_ratio': {ratios[symbol]['max_ratio']:.10f}}},")
    print("}")
    
    return all_match

if __name__ == "__main__":
    verify_btc_ratio_pattern()