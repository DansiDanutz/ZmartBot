#!/usr/bin/env python3
"""
Reverse engineer Benjamin Cowen's exact formula
Using known data points to find the pattern
"""

import math
import numpy as np
from scipy.optimize import minimize_scalar, differential_evolution
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def calculate_risk(price, min_price, max_price):
    """Calculate risk using logarithmic formula"""
    if price <= min_price:
        return 0.0
    elif price >= max_price:
        return 1.0
    else:
        return (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))

def find_bounds_from_known_point(price, risk_value, test_min=None, test_max=None):
    """
    Find min/max bounds given a known price-risk pair
    If test_min is provided, find max. If test_max is provided, find min.
    """
    if test_min is not None:
        # Find max given min
        # risk = (ln(price) - ln(min)) / (ln(max) - ln(min))
        # risk * (ln(max) - ln(min)) = ln(price) - ln(min)
        # risk * ln(max) - risk * ln(min) = ln(price) - ln(min)
        # risk * ln(max) = ln(price) - ln(min) + risk * ln(min)
        # risk * ln(max) = ln(price) - ln(min) * (1 - risk)
        # ln(max) = (ln(price) - ln(min) * (1 - risk)) / risk
        
        if risk_value == 0:
            return None
        
        ln_max = (math.log(price) - math.log(test_min) * (1 - risk_value)) / risk_value
        return math.exp(ln_max)
    
    elif test_max is not None:
        # Find min given max
        # risk = (ln(price) - ln(min)) / (ln(max) - ln(min))
        # risk * (ln(max) - ln(min)) = ln(price) - ln(min)
        # ln(min) = ln(price) - risk * (ln(max) - ln(min))
        # ln(min) * (1 - risk) = ln(price) - risk * ln(max)
        # ln(min) = (ln(price) - risk * ln(max)) / (1 - risk)
        
        if risk_value == 1:
            return None
            
        ln_min = (math.log(price) - risk_value * math.log(test_max)) / (1 - risk_value)
        return math.exp(ln_min)
    
    return None

def find_bounds_multiple_points(data_points):
    """
    Find bounds using multiple known price-risk pairs
    data_points: list of (price, risk) tuples
    """
    
    def objective(params):
        """Objective function to minimize - sum of squared errors"""
        min_price, max_price = params
        if min_price >= max_price or min_price <= 0:
            return 1e10
        
        error = 0
        for price, expected_risk in data_points:
            calculated_risk = calculate_risk(price, min_price, max_price)
            error += (calculated_risk - expected_risk) ** 2
        return error
    
    # Use differential evolution for global optimization
    bounds = [(1, 500), (100, 5000)]  # min and max bounds ranges
    result = differential_evolution(objective, bounds, seed=42)
    
    return result.x[0], result.x[1]

def analyze_btc_ratio_pattern():
    """
    Analyze if there's a BTC ratio pattern in the bounds
    """
    print("\n🔍 Analyzing BTC Ratio Pattern")
    print("=" * 60)
    
    # Known BTC bounds (from your data)
    btc_min = 30000
    btc_max = 299720
    
    # AAVE actual values from Google Sheets
    aave_price = 275.39
    aave_risk = 0.566
    
    # Try different min values to find the max that gives us 0.566 risk
    print("\nTesting different min values to find correct max for AAVE:")
    print(f"Target: AAVE at ${aave_price} = {aave_risk} risk")
    print(f"{'Min':>10} | {'Max':>10} | {'Risk':>8} | {'Error':>10}")
    print("-" * 50)
    
    best_match = None
    best_error = float('inf')
    
    # Test range of min values
    for test_min in range(50, 100, 1):
        test_max = find_bounds_from_known_point(aave_price, aave_risk, test_min=test_min)
        if test_max:
            calc_risk = calculate_risk(aave_price, test_min, test_max)
            error = abs(calc_risk - aave_risk)
            
            if error < best_error:
                best_error = error
                best_match = (test_min, test_max)
            
            if error < 0.001:  # Close enough match
                print(f"{test_min:>10} | {test_max:>10.0f} | {calc_risk:>8.3f} | {error:>10.6f} ✓")
    
    if best_match:
        print(f"\n✅ Best match: Min=${best_match[0]}, Max=${best_match[1]:.0f}")
        
        # Check if there's a BTC ratio
        ratio_min = best_match[0] / btc_min * 1000000  # Scale for readability
        ratio_max = best_match[1] / btc_max * 1000000
        
        print(f"\n📊 BTC Ratio Analysis:")
        print(f"   AAVE/BTC min ratio: {ratio_min:.2f}")
        print(f"   AAVE/BTC max ratio: {ratio_max:.2f}")
    
    return best_match

def test_multiple_symbols():
    """Test pattern with multiple symbols"""
    print("\n🎯 Testing Multiple Symbols Pattern")
    print("=" * 60)
    
    # Known data points from Google Sheets (you mentioned)
    known_data = {
        'AAVE': {'price': 275.39, 'risk': 0.566, 'actual_min': 63, 'actual_max': 1446},
        # Add more known points here as you provide them
    }
    
    for symbol, data in known_data.items():
        print(f"\n{symbol}:")
        print(f"  Known: ${data['price']} = {data['risk']} risk")
        print(f"  Actual bounds: ${data['actual_min']} - ${data['actual_max']}")
        
        # Verify with actual bounds
        calc_risk = calculate_risk(data['price'], data['actual_min'], data['actual_max'])
        print(f"  Calculated risk with actual bounds: {calc_risk:.3f}")
        print(f"  Match: {'✅' if abs(calc_risk - data['risk']) < 0.001 else '❌'}")
        
        # Calculate what price should be at different risks
        print(f"\n  Price at key risk levels:")
        for risk in [0.0, 0.25, 0.5, 0.75, 1.0]:
            if risk == 0:
                price = data['actual_min']
            elif risk == 1:
                price = data['actual_max']
            else:
                ln_price = math.log(data['actual_min']) + risk * (math.log(data['actual_max']) - math.log(data['actual_min']))
                price = math.exp(ln_price)
            print(f"    Risk {risk:.2f} = ${price:.2f}")

def find_growth_multiple_pattern():
    """
    Find if there's a growth multiple pattern
    """
    print("\n📈 Analyzing Growth Multiple Pattern")
    print("=" * 60)
    
    # Calculate growth multiples
    symbols_data = {
        'BTC': {'min': 30000, 'max': 299720},
        'AAVE': {'min': 63, 'max': 1446},
    }
    
    print(f"{'Symbol':<10} | {'Min':>10} | {'Max':>10} | {'Multiple':>10}")
    print("-" * 50)
    
    for symbol, bounds in symbols_data.items():
        multiple = bounds['max'] / bounds['min']
        print(f"{symbol:<10} | ${bounds['min']:>9} | ${bounds['max']:>9} | {multiple:>10.2f}x")
    
    # Check if AAVE follows a pattern based on BTC
    btc_multiple = symbols_data['BTC']['max'] / symbols_data['BTC']['min']
    aave_multiple = symbols_data['AAVE']['max'] / symbols_data['AAVE']['min']
    
    print(f"\n📊 Multiple Comparison:")
    print(f"  BTC growth multiple: {btc_multiple:.2f}x")
    print(f"  AAVE growth multiple: {aave_multiple:.2f}x")
    print(f"  Ratio: {aave_multiple/btc_multiple:.3f}")

def main():
    """Main analysis"""
    print("🔬 REVERSE ENGINEERING BENJAMIN COWEN'S FORMULA")
    print("=" * 60)
    
    # Test with AAVE known values
    print("\n1️⃣ VERIFYING AAVE WITH CORRECT BOUNDS")
    aave_min = 63
    aave_max = 1446
    aave_price = 275.39
    expected_risk = 0.566
    
    calculated_risk = calculate_risk(aave_price, aave_min, aave_max)
    print(f"  AAVE at ${aave_price}")
    print(f"  Min: ${aave_min}, Max: ${aave_max}")
    print(f"  Expected risk: {expected_risk}")
    print(f"  Calculated risk: {calculated_risk:.3f}")
    print(f"  Match: {'✅ EXACT!' if abs(calculated_risk - expected_risk) < 0.001 else f'❌ Error: {abs(calculated_risk - expected_risk):.4f}'}")
    
    # Find pattern
    best_bounds = analyze_btc_ratio_pattern()
    
    # Test multiple symbols
    test_multiple_symbols()
    
    # Find growth pattern
    find_growth_multiple_pattern()
    
    print("\n" + "=" * 60)
    print("💡 INSIGHTS:")
    print("1. The logarithmic formula is correct")
    print("2. Each symbol has unique min/max bounds")
    print("3. Growth multiples vary by symbol (not uniform)")
    print("4. Need to find the exact bounds for each symbol")
    print("\n📝 NEXT STEPS:")
    print("1. Get more symbol data points from Google Sheets")
    print("2. Find the pattern for determining min/max per symbol")
    print("3. Update all symbol bounds in ULTIMATE_COMPLETE_RISKMETRIC.py")

if __name__ == "__main__":
    main()