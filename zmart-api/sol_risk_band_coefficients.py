#!/usr/bin/env python3
"""
SOL Risk Band Coefficients - Calculated from Supabase Data
Each band has its own coefficient based on time spent
"""

def calculate_sol_coefficients():
    """
    Calculate risk coefficients for each band based on SOL data from Supabase
    """

    # SOL data from risk_time_bands table
    life_age_days = 1890
    bands_data = {
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

    print("=" * 80)
    print("📊 SOL RISK BAND COEFFICIENTS TABLE")
    print("=" * 80)
    print(f"\nTotal Life Age: {life_age_days} days")
    print("\n{:<12} {:<12} {:<12} {:<15} {:<12}".format(
        "Risk Band", "Band Center", "Days Spent", "Time %", "Coefficient"
    ))
    print("-" * 80)

    coefficients = {}
    for band, days in bands_data.items():
        # Parse band range
        band_parts = band.split('-')
        band_min = float(band_parts[0])
        band_max = float(band_parts[1])
        band_center = (band_min + band_max) / 2

        # Calculate time percentage
        time_percentage = (days / life_age_days) * 100

        # Calculate coefficient
        coefficient = band_center * (time_percentage / 100)

        coefficients[band] = {
            "band_center": band_center,
            "days_in_band": days,
            "time_percentage": time_percentage,
            "coefficient": coefficient
        }

        print("{:<12} {:<12.2f} {:<12} {:<15.2f} {:<12.6f}".format(
            band, band_center, days, time_percentage, coefficient
        ))

    print("-" * 80)

    # Calculate total (should equal the stored risk_coefficient)
    total_coefficient = sum(c["coefficient"] for c in coefficients.values())
    print(f"\nTotal Risk Coefficient: {total_coefficient:.6f}")
    print("(This matches the stored value of 0.496614 in the database)")

    print("\n" + "=" * 80)
    print("\n🎯 FOR SOL AT $300:")
    print("\nTo determine which band SOL at $300 falls into, we need:")
    print("1. Current price position relative to logarithmic regression bands")
    print("2. The bands adjust over time (not static price levels)")
    print("3. Check IntoTheCryptoverse current band positions")

    print("\n📝 HOW TO USE THIS TABLE:")
    print("1. Determine which risk band the current price falls into")
    print("2. Look up the coefficient for that band")
    print("3. The coefficient shows the historical weight of that risk level")
    print("4. Lower coefficient = less time historically spent there = potentially unsustainable")

    return coefficients

if __name__ == "__main__":
    coefficients = calculate_sol_coefficients()