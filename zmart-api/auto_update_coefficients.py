#!/usr/bin/env python3
"""
Automatically Update Risk Band Coefficients
This should run whenever risk_time_bands table is updated
Uses our methodology: Rarest = 1.6, Most Common = 1.0
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def calculate_band_coefficients(risk_bands_dict):
    """
    Calculate coefficients for risk bands using our methodology
    """
    bands = []
    for band_name, days in risk_bands_dict.items():
        bands.append({
            'band': band_name,
            'days': float(days),
            'center': sum(float(x) for x in band_name.replace('band_', '').replace('_', '.').split('-')) / 2 if '-' in band_name else 0
        })

    # Find rarest and most common
    rarest = min(bands, key=lambda x: x['days'])
    most_common = max(bands, key=lambda x: x['days'])

    # Calculate coefficient step
    day_difference = most_common['days'] - rarest['days']
    coefficient_step = 0.6 / day_difference if day_difference > 0 else 0

    # Calculate coefficients
    coefficients = {}
    for band in bands:
        days_from_rarest = band['days'] - rarest['days']
        coefficient = 1.6 - (days_from_rarest * coefficient_step)
        coefficient = max(1.0, min(1.6, coefficient))
        coefficients[band['band']] = round(coefficient, 4)

    return coefficients, rarest['band'], most_common['band']

def update_all_coefficients():
    """
    Update coefficients for all symbols in risk_time_bands
    """
    # Fetch all symbols
    result = supabase.table('risk_time_bands').select('*').execute()

    if not result.data:
        print("No data found in risk_time_bands")
        return

    updates = []

    for row in result.data:
        symbol = row['symbol']

        # Construct risk bands dictionary
        risk_bands = {}
        for i in range(10):
            band_key = f"band_{i}_{i+1}" if i < 9 else "band_9_10"
            band_name = f"{i/10:.1f}-{(i+1)/10:.1f}"

            # Get the value from the correct column name
            if band_key.replace('_', '') in ['band001', 'band0102']:
                col_name = f"band_0_0{i+1}" if i == 0 else f"band_0{i}_0{i+1}"
            else:
                col_name = f"band_{i//10}{i%10}_{(i+1)//10}{(i+1)%10}"

            # Use the actual column names from the table
            if i == 0:
                col_name = "band_0_01"
            elif i == 1:
                col_name = "band_01_02"
            elif i == 2:
                col_name = "band_02_03"
            elif i == 3:
                col_name = "band_03_04"
            elif i == 4:
                col_name = "band_04_05"
            elif i == 5:
                col_name = "band_05_06"
            elif i == 6:
                col_name = "band_06_07"
            elif i == 7:
                col_name = "band_07_08"
            elif i == 8:
                col_name = "band_08_09"
            elif i == 9:
                col_name = "band_09_10"

            risk_bands[band_name] = float(row.get(col_name, 0))

        # Calculate coefficients
        coefficients, rarest, most_common = calculate_band_coefficients(risk_bands)

        print(f"\n{symbol}:")
        print(f"  Rarest: {rarest} ({risk_bands[rarest]} days) → 1.6")
        print(f"  Most Common: {most_common} ({risk_bands[most_common]} days) → 1.0")
        print(f"  Coefficients: {coefficients}")

        # Store update
        updates.append({
            'symbol': symbol,
            'coefficients': coefficients,
            'rarest_band': rarest,
            'most_common_band': most_common
        })

    return updates

if __name__ == "__main__":
    print("=" * 80)
    print("UPDATING RISK BAND COEFFICIENTS")
    print("=" * 80)

    updates = update_all_coefficients()

    if updates:
        print(f"\n✅ Calculated coefficients for {len(updates)} symbols")

        # Save to JSON for reference
        import json
        with open('risk_band_coefficients.json', 'w') as f:
            json.dump(updates, f, indent=2)
        print("📁 Saved to risk_band_coefficients.json")
    else:
        print("❌ No updates calculated")