#!/usr/bin/env python3
"""
Calculate correct ETH bounds to match Benjamin Cowen's current risk value
ETH at $3500 should have risk = 0.715 (high risk zone)
"""

import math

def calculate_risk(price, min_price, max_price):
    """Calculate logarithmic risk value (Benjamin Cowen formula)"""
    if price <= min_price:
        return 0.0
    elif price >= max_price:
        return 1.0
    else:
        log_price = math.log(price)
        log_min = math.log(min_price)
        log_max = math.log(max_price)
        risk = (log_price - log_min) / (log_max - log_min)
        return max(0.0, min(1.0, risk))

def find_bounds_for_risk(current_price, target_risk, min_price_guess=80):
    """
    Find min and max bounds that give target risk at current price
    Using Benjamin Cowen's typical range patterns
    """
    # For ETH, typical cycle is about 100x from bottom to top
    # If risk = 0.715 at $3500, we're in high risk zone

    # Work backwards from the logarithmic formula
    # risk = (log(price) - log(min)) / (log(max) - log(min))
    # 0.715 = (log(3500) - log(min)) / (log(max) - log(min))

    # Try different min values to find reasonable bounds
    best_min = None
    best_max = None

    for min_price in range(80, 500, 10):  # Try min from $80 to $500
        # Calculate what max would need to be
        # Rearranging: log(max) = log(min) + (log(price) - log(min)) / risk
        log_price = math.log(current_price)
        log_min = math.log(min_price)

        # log(max) = log(min) + (log(price) - log(min)) / 0.715
        log_max = log_min + (log_price - log_min) / target_risk
        max_price = math.exp(log_max)

        # Check if this gives reasonable cycle multiplier
        multiplier = max_price / min_price

        # ETH typically has 30-100x cycles
        if 30 <= multiplier <= 100:
            # Verify the calculation
            calculated_risk = calculate_risk(current_price, min_price, max_price)
            if abs(calculated_risk - target_risk) < 0.001:
                print(f"Min: ${min_price:,.0f}, Max: ${max_price:,.0f}")
                print(f"Multiplier: {multiplier:.1f}x")
                print(f"Risk at ${current_price}: {calculated_risk:.4f}")

                # Check some key levels
                print(f"\nKey price levels:")
                print(f"  Risk 0.1: ${math.exp(log_min + 0.1 * (log_max - log_min)):,.0f}")
                print(f"  Risk 0.3: ${math.exp(log_min + 0.3 * (log_max - log_min)):,.0f}")
                print(f"  Risk 0.5: ${math.exp(log_min + 0.5 * (log_max - log_min)):,.0f}")
                print(f"  Risk 0.7: ${math.exp(log_min + 0.7 * (log_max - log_min)):,.0f}")
                print(f"  Risk 0.9: ${math.exp(log_min + 0.9 * (log_max - log_min)):,.0f}")
                print("-" * 50)

                if best_min is None:
                    best_min = min_price
                    best_max = max_price

    return best_min, best_max

# Current situation
print("="*60)
print("FIXING ETH RISK CALCULATION")
print("="*60)

current_eth_price = 3500
target_risk = 0.715

print(f"\nTarget: ETH at ${current_eth_price} should have risk = {target_risk}")
print(f"Current bounds: $300 - $25,000")

# Calculate with current bounds
current_risk = calculate_risk(3500, 300, 25000)
print(f"Current calculation: risk = {current_risk:.4f} ❌ WRONG!")

print(f"\n{'='*60}")
print("FINDING CORRECT BOUNDS")
print("="*60)

# Find correct bounds
best_min, best_max = find_bounds_for_risk(current_eth_price, target_risk)

if best_min and best_max:
    print(f"\n{'='*60}")
    print("RECOMMENDED FIX")
    print("="*60)
    print(f"Update ETH bounds to:")
    print(f"  'min': {best_min}")
    print(f"  'max': {best_max}")

    # Verify
    print(f"\nVerification:")
    verify_risk = calculate_risk(current_eth_price, best_min, best_max)
    print(f"  Risk at ${current_eth_price}: {verify_risk:.4f} {'✅ CORRECT!' if abs(verify_risk - target_risk) < 0.001 else '❌'}")

    # Benjamin Cowen's typical risk zones
    print(f"\nRisk Zones with new bounds:")
    print(f"  🟢 Low Risk (0-0.3): ${best_min:,.0f} - ${math.exp(math.log(best_min) + 0.3 * (math.log(best_max) - math.log(best_min))):,.0f}")
    print(f"  🟡 Medium Risk (0.3-0.7): ${math.exp(math.log(best_min) + 0.3 * (math.log(best_max) - math.log(best_min))):,.0f} - ${math.exp(math.log(best_min) + 0.7 * (math.log(best_max) - math.log(best_min))):,.0f}")
    print(f"  🔴 High Risk (0.7-1.0): ${math.exp(math.log(best_min) + 0.7 * (math.log(best_max) - math.log(best_min))):,.0f} - ${best_max:,.0f}")