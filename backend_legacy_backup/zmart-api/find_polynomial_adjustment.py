#!/usr/bin/env python3
"""
Find the polynomial adjustment to match exact risk values
"""

import numpy as np
from scipy.optimize import curve_fit
import math

def exponential_risk(price, min_price, max_price):
    """Basic exponential risk formula"""
    if price <= min_price:
        return 0.0
    elif price >= max_price:
        return 1.0
    return math.log(price / min_price) / math.log(max_price / min_price)

def polynomial_adjustment(risk, a, b, c, d):
    """4th degree polynomial adjustment"""
    return a + b * risk + c * risk**2 + d * risk**3

def find_adjustment():
    """Find the adjustment needed"""
    
    print("🔍 FINDING THE ADJUSTMENT FACTOR")
    print("=" * 80)
    
    # AAVE known values
    aave_min = 63.35
    aave_max = 1446.00
    aave_price = 275.39
    
    # Calculate base exponential risk
    base_risk = exponential_risk(aave_price, aave_min, aave_max)
    target_risk = 0.566
    
    print(f"\nAAVE at ${aave_price}:")
    print(f"  Base exponential risk: {base_risk:.4f}")
    print(f"  Target risk: {target_risk:.4f}")
    print(f"  Difference: {target_risk - base_risk:.4f}")
    print(f"  Adjustment factor: {target_risk / base_risk:.4f}")
    
    # The adjustment is approximately 1.2x
    adjustment = target_risk / base_risk
    
    print(f"\n💡 Required adjustment: {adjustment:.4f}x")
    
    # Test if this is consistent across symbols
    print("\n📊 Testing adjustment on other symbols:")
    print("-" * 60)
    
    # We need more data points to verify
    # But the pattern suggests a non-linear adjustment
    
    # Hypothesis: The adjustment might be based on growth multiple
    growth_multiple = aave_max / aave_min
    print(f"\nAAVE growth multiple: {growth_multiple:.1f}x")
    
    # Symbols with higher growth multiples might have different adjustments
    test_symbols = {
        'ETH': {'min': 445.60, 'max': 10780.24},
        'SOL': {'min': 18.75, 'max': 907.09},
        'ADA': {'min': 0.10, 'max': 6.56},
    }
    
    print("\nGrowth multiples:")
    for symbol, bounds in test_symbols.items():
        multiple = bounds['max'] / bounds['min']
        print(f"  {symbol}: {multiple:.1f}x")
    
    # Hypothesis: Adjustment = 1 + 0.2 * log(growth_multiple) / log(50)
    print("\n🎯 HYPOTHESIS: Logarithmic adjustment based on growth multiple")
    
    for symbol, bounds in {'AAVE': {'min': aave_min, 'max': aave_max}, **test_symbols}.items():
        multiple = bounds['max'] / bounds['min']
        # Adjustment formula hypothesis
        adj = 1 + 0.2 * math.log(multiple) / math.log(50)
        print(f"  {symbol} (growth {multiple:.1f}x): adjustment = {adj:.4f}")
    
    # For AAVE, this gives approximately the right adjustment
    aave_growth = aave_max / aave_min
    aave_adj = 1 + 0.2 * math.log(aave_growth) / math.log(50)
    adjusted_risk = base_risk * aave_adj
    
    print(f"\nAAVE verification:")
    print(f"  Base risk: {base_risk:.4f}")
    print(f"  Adjustment: {aave_adj:.4f}")
    print(f"  Adjusted risk: {adjusted_risk:.4f}")
    print(f"  Target: {target_risk:.4f}")
    print(f"  Match: {'✅' if abs(adjusted_risk - target_risk) < 0.01 else '❌'}")

if __name__ == "__main__":
    find_adjustment()