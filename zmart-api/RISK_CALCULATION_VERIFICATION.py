#!/usr/bin/env python3
"""
EXACT Risk Calculation Verification for ADA
To ensure we NEVER guess and ALWAYS have precise math
"""

# Grid data from ADA_risk_grid.json
grid_points = [
    {"risk": 0.550, "price": 0.829},
    {"risk": 0.575, "price": 0.893}
]

# EXACT Binance price
ada_price = 0.8824

# Linear interpolation
price_lower = 0.829
price_upper = 0.893
risk_lower = 0.550
risk_upper = 0.575

# Calculate position
price_range = price_upper - price_lower
price_position = ada_price - price_lower
position_ratio = price_position / price_range

print("=== RISK CALCULATION VERIFICATION ===")
print(f"ADA Price: ${ada_price}")
print(f"\nGrid Points:")
print(f"  Lower: ${price_lower} → Risk {risk_lower}")
print(f"  Upper: ${price_upper} → Risk {risk_upper}")
print(f"\nCalculation:")
print(f"  Price Range: {price_upper} - {price_lower} = {price_range:.4f}")
print(f"  Price Position: {ada_price} - {price_lower} = {price_position:.4f}")
print(f"  Position Ratio: {price_position:.4f} / {price_range:.4f} = {position_ratio:.6f}")

# Calculate risk
risk_range = risk_upper - risk_lower
risk_increment = position_ratio * risk_range
final_risk = risk_lower + risk_increment

print(f"\n  Risk Range: {risk_upper} - {risk_lower} = {risk_range}")
print(f"  Risk Increment: {position_ratio:.6f} × {risk_range} = {risk_increment:.6f}")
print(f"  Final Risk: {risk_lower} + {risk_increment:.6f} = {final_risk:.6f}")

print(f"\n=== RESULT ===")
print(f"Risk Value: {final_risk:.3f}")
print(f"Risk Band: {int(final_risk * 10) / 10:.1f}-{(int(final_risk * 10) + 1) / 10:.1f}")

# Double check
verification = 0.550 + ((0.8824 - 0.829) / (0.893 - 0.829)) * 0.025
print(f"\nVerification: {verification:.6f}")

# Where did 0.582 come from?
print("\n=== ERROR ANALYSIS ===")
wrong_calc = 0.550 + ((0.893 - 0.829) / (0.893 - 0.829)) * 0.025 + 0.007
print(f"The 0.582 was WRONG - possibly from:")
print(f"1. Using wrong price point")
print(f"2. Calculation error")
print(f"3. Not using linear interpolation")

print(f"\n✅ CORRECT RISK: {final_risk:.3f}")
print(f"❌ WRONG RISK: 0.582 (ERROR!)")