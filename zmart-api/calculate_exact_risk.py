#!/usr/bin/env python3
"""
Calculate exact risk value for any price using linear interpolation
Based on official IntoTheCryptoverse data
"""

def calculate_exact_risk(target_price, risk_data):
    """
    Calculate exact risk for any price using linear interpolation
    """
    # Sort data by price
    sorted_data = sorted(risk_data, key=lambda x: x[0])

    # Find the two points that bracket our target price
    lower = None
    upper = None

    for i in range(len(sorted_data) - 1):
        if sorted_data[i][0] <= target_price <= sorted_data[i+1][0]:
            lower = sorted_data[i]
            upper = sorted_data[i+1]
            break

    if lower and upper:
        # Linear interpolation formula
        price_lower, risk_lower = lower
        price_upper, risk_upper = upper

        # Calculate the exact risk
        risk = risk_lower + (risk_upper - risk_lower) * ((target_price - price_lower) / (price_upper - price_lower))

        return {
            'target_price': target_price,
            'exact_risk': round(risk, 6),
            'lower_bound': {'price': price_lower, 'risk': risk_lower},
            'upper_bound': {'price': price_upper, 'risk': risk_upper}
        }

    return None

# SOL Risk Data from IntoTheCryptoverse
sol_risk_data = [
    (20.61, 0.000),
    (43.44, 0.158),
    (66.27, 0.247),
    (89.10, 0.329),
    (111.93, 0.425),
    (134.76, 0.503),
    (157.59, 0.568),
    (180.42, 0.624),
    (203.25, 0.673),
    (226.08, 0.697),
    (243.85, 0.713),
    (248.91, 0.718),
    (271.74, 0.737),
    (294.57, 0.754),
    (317.40, 0.770),
    (340.23, 0.785),
    (363.05, 0.799),
    (385.88, 0.812),
    (408.71, 0.824),
    (431.54, 0.835),
    (454.37, 0.846),
    (477.20, 0.857),
    (500.03, 0.867),
    (522.86, 0.876),
    (545.69, 0.886),
    (568.52, 0.894),
    (591.35, 0.903),
    (614.18, 0.911),
    (637.01, 0.919),
    (659.84, 0.926),
    (682.67, 0.933),
    (705.50, 0.940),
    (728.32, 0.947),
    (751.15, 0.954),
    (773.98, 0.960),
    (796.81, 0.966),
    (819.64, 0.972),
    (842.47, 0.978),
    (865.30, 0.984),
    (888.13, 0.989),
    (910.96, 0.995),
    (933.79, 1.000)
]

if __name__ == "__main__":
    print("=" * 60)
    print("EXACT RISK CALCULATOR FOR SOL")
    print("=" * 60)
    print()

    # Calculate for $300
    target = 300
    result = calculate_exact_risk(target, sol_risk_data)

    if result:
        print(f"🎯 Target Price: ${target}")
        print(f"📊 Exact Risk Value: {result['exact_risk']}")
        print()
        print("Calculation Details:")
        print(f"  Lower bound: ${result['lower_bound']['price']:.2f} → Risk {result['lower_bound']['risk']:.3f}")
        print(f"  Upper bound: ${result['upper_bound']['price']:.2f} → Risk {result['upper_bound']['risk']:.3f}")
        print()

        # Show the math
        price_diff = result['upper_bound']['price'] - result['lower_bound']['price']
        risk_diff = result['upper_bound']['risk'] - result['lower_bound']['risk']
        position = (target - result['lower_bound']['price']) / price_diff

        print("Linear Interpolation Formula:")
        print(f"  Price range: ${price_diff:.2f} (${result['lower_bound']['price']:.2f} to ${result['upper_bound']['price']:.2f})")
        print(f"  Risk range: {risk_diff:.3f} ({result['lower_bound']['risk']:.3f} to {result['upper_bound']['risk']:.3f})")
        print(f"  Position in range: {position:.4f} ({position*100:.2f}% of the way)")
        print(f"  Risk = {result['lower_bound']['risk']:.3f} + {risk_diff:.3f} × {position:.4f}")
        print(f"  Risk = {result['lower_bound']['risk']:.3f} + {risk_diff * position:.6f}")
        print(f"  Risk = {result['exact_risk']}")

    print()
    print("-" * 60)

    # Calculate for current price
    current = 238.88
    result = calculate_exact_risk(current, sol_risk_data)

    if result:
        print(f"💰 Current Price: ${current}")
        print(f"📊 Exact Risk Value: {result['exact_risk']}")
        print()
        print("Calculation Details:")
        print(f"  Lower bound: ${result['lower_bound']['price']:.2f} → Risk {result['lower_bound']['risk']:.3f}")
        print(f"  Upper bound: ${result['upper_bound']['price']:.2f} → Risk {result['upper_bound']['risk']:.3f}")

    print()
    print("-" * 60)

    # Test other prices
    test_prices = [100, 150, 200, 250, 350, 400, 500, 600, 700, 800, 900]

    print("\n📋 Risk Values for Various Prices:")
    print("Price    | Risk Value")
    print("---------|------------")

    for price in test_prices:
        result = calculate_exact_risk(price, sol_risk_data)
        if result:
            print(f"${price:6.2f} | {result['exact_risk']:.6f}")