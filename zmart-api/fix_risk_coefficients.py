#!/usr/bin/env python3
"""
Fix Risk Band Coefficients using our CORRECT methodology
Rarest band = 1.6, Most common = 1.0
"""

def calculate_correct_coefficients(symbol_data):
    """
    Calculate coefficients based on our methodology:
    1. Rarest band gets 1.6
    2. Most common band gets 1.0
    3. Others scaled based on days difference
    """

    # Extract days from bands
    bands = []
    for band_name, days in symbol_data['risk_bands'].items():
        bands.append({
            'band': band_name,
            'days': days,
            'center': sum(float(x) for x in band_name.split('-')) / 2
        })

    # Find rarest and most common
    rarest = min(bands, key=lambda x: x['days'])
    most_common = max(bands, key=lambda x: x['days'])

    print(f"Rarest band: {rarest['band']} with {rarest['days']} days → Coefficient 1.6")
    print(f"Most common: {most_common['band']} with {most_common['days']} days → Coefficient 1.0")

    # Calculate coefficient step
    day_difference = most_common['days'] - rarest['days']
    coefficient_step = 0.6 / day_difference if day_difference > 0 else 0

    print(f"Day difference: {day_difference}")
    print(f"Coefficient step: {coefficient_step:.6f} per day")

    # Calculate coefficient for each band
    coefficients = {}
    for band in bands:
        days_from_rarest = band['days'] - rarest['days']
        coefficient = 1.6 - (days_from_rarest * coefficient_step)
        coefficient = max(1.0, min(1.6, coefficient))  # Ensure between 1.0 and 1.6
        coefficients[band['band']] = {
            'days': band['days'],
            'coefficient': round(coefficient, 4),
            'band_center': band['center']
        }

    return coefficients

# SOL data from our database
SOL_DATA = {
    "symbol": "SOL",
    "life_age_days": 1890,
    "risk_bands": {
        "0.0-0.1": 61,
        "0.1-0.2": 193,
        "0.2-0.3": 316,
        "0.3-0.4": 307,
        "0.4-0.5": 219,
        "0.5-0.6": 158,
        "0.6-0.7": 149,
        "0.7-0.8": 210,
        "0.8-0.9": 149,
        "0.9-1.0": 126
    }
}

print("=" * 80)
print("CORRECTED SOL RISK BAND COEFFICIENTS")
print("=" * 80)
print()

coefficients = calculate_correct_coefficients(SOL_DATA)

print("\n" + "=" * 80)
print("FINAL COEFFICIENT TABLE:")
print("=" * 80)
print(f"{'Band':<12} {'Days':<10} {'Coefficient':<12} {'Band Center':<12}")
print("-" * 80)

# Sort by days (rarest to most common)
sorted_bands = sorted(coefficients.items(), key=lambda x: x[1]['days'])
for band, data in sorted_bands:
    print(f"{band:<12} {data['days']:<10} {data['coefficient']:<12.4f} {data['band_center']:<12.2f}")

print("-" * 80)

# Now let's test SOL at $300
print("\n" + "=" * 80)
print("SOL at $300 TEST:")
print("=" * 80)

# From our earlier analysis, SOL at $300 would be in 0.6-0.7 band
target_band = "0.6-0.7"
band_data = coefficients[target_band]

print(f"\nSOL at $300:")
print(f"  • Risk Band: {target_band}")
print(f"  • Days in Band: {band_data['days']} days")
print(f"  • Coefficient: {band_data['coefficient']}")
print(f"  • Calculation: 1.6 - ({band_data['days']} - 61) × {coefficient_step:.6f} = {band_data['coefficient']}")

print("\n" + "=" * 80)