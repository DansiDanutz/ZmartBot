#!/usr/bin/env python3
"""
Generate SQL to load all time bands data into Supabase
"""

import json
from pathlib import Path

def generate_time_bands_sql():
    """Generate SQL INSERT statements for all symbols' time bands"""

    # Path to time bands data
    time_bands_dir = Path("extracted_risk_time_bands")

    if not time_bands_dir.exists():
        print("❌ Time bands directory not found!")
        return

    all_inserts = []

    # Get all time band files
    for json_file in sorted(time_bands_dir.glob("*_time_bands.json")):
        with open(json_file, 'r') as f:
            data = json.load(f)

        symbol = data['symbol']

        # Extract risk band days
        risk_bands = data['risk_bands']

        insert = f"""INSERT INTO cryptoverse_risk_time_bands (
    symbol, symbol_name, birth_date, total_days,
    band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
    band_50_60, band_60_70, band_70_80, band_80_90, band_90_100,
    band_0_10_pct, band_10_20_pct, band_20_30_pct, band_30_40_pct, band_40_50_pct,
    band_50_60_pct, band_60_70_pct, band_70_80_pct, band_80_90_pct, band_90_100_pct,
    current_risk_band, confidence_level, data_type
) VALUES (
    '{symbol}', '{data.get('symbol_name', symbol)}', '{data.get('birth_date', 'NULL')}', {data.get('total_days', data.get('actual_age_days', 0))},
    {risk_bands.get('0.0-0.1', 0)}, {risk_bands.get('0.1-0.2', 0)}, {risk_bands.get('0.2-0.3', 0)}, {risk_bands.get('0.3-0.4', 0)}, {risk_bands.get('0.4-0.5', 0)},
    {risk_bands.get('0.5-0.6', 0)}, {risk_bands.get('0.6-0.7', 0)}, {risk_bands.get('0.7-0.8', 0)}, {risk_bands.get('0.8-0.9', 0)}, {risk_bands.get('0.9-1.0', 0)},
    {data.get('0.0-0.1_percentage', 0)}, {data.get('0.1-0.2_percentage', 0)}, {data.get('0.2-0.3_percentage', 0)}, {data.get('0.3-0.4_percentage', 0)}, {data.get('0.4-0.5_percentage', 0)},
    {data.get('0.5-0.6_percentage', 0)}, {data.get('0.6-0.7_percentage', 0)}, {data.get('0.7-0.8_percentage', 0)}, {data.get('0.8-0.9_percentage', 0)}, {data.get('0.9-1.0_percentage', 0)},
    '{data.get('current_risk_band', 'Unknown')}', {data.get('confidence_level', 5)}, '{data.get('data_type', 'estimated')}'
) ON CONFLICT (symbol) DO UPDATE SET
    band_0_10 = EXCLUDED.band_0_10,
    band_10_20 = EXCLUDED.band_10_20,
    band_20_30 = EXCLUDED.band_20_30,
    band_30_40 = EXCLUDED.band_30_40,
    band_40_50 = EXCLUDED.band_40_50,
    band_50_60 = EXCLUDED.band_50_60,
    band_60_70 = EXCLUDED.band_60_70,
    band_70_80 = EXCLUDED.band_70_80,
    band_80_90 = EXCLUDED.band_80_90,
    band_90_100 = EXCLUDED.band_90_100,
    band_0_10_pct = EXCLUDED.band_0_10_pct,
    band_10_20_pct = EXCLUDED.band_10_20_pct,
    band_20_30_pct = EXCLUDED.band_20_30_pct,
    band_30_40_pct = EXCLUDED.band_30_40_pct,
    band_40_50_pct = EXCLUDED.band_40_50_pct,
    band_50_60_pct = EXCLUDED.band_50_60_pct,
    band_60_70_pct = EXCLUDED.band_60_70_pct,
    band_70_80_pct = EXCLUDED.band_70_80_pct,
    band_80_90_pct = EXCLUDED.band_80_90_pct,
    band_90_100_pct = EXCLUDED.band_90_100_pct,
    current_risk_band = EXCLUDED.current_risk_band,
    confidence_level = EXCLUDED.confidence_level,
    data_type = EXCLUDED.data_type,
    last_updated = NOW();"""

        all_inserts.append(insert)

    # Write to SQL file
    output_file = "insert_all_time_bands.sql"
    with open(output_file, 'w') as f:
        f.write("-- INSERT ALL TIME BANDS DATA INTO SUPABASE\n")
        f.write("-- Generated from extracted_risk_time_bands/*.json\n")
        f.write("-- =============================================\n\n")

        f.write("\n\n".join(all_inserts))

        f.write("\n\n-- VERIFY DATA LOADED\n")
        f.write("""SELECT
    'Time Bands Loaded' as status,
    COUNT(*) as symbols_count,
    string_agg(symbol, ', ' ORDER BY symbol) as symbols
FROM cryptoverse_risk_time_bands;

-- SHOW DISTRIBUTION SUMMARY
SELECT
    symbol,
    current_risk_band,
    ROUND(accumulation_pct, 1) as "Accumulation %",
    ROUND(transition_pct, 1) as "Transition %",
    ROUND(distribution_pct, 1) as "Distribution %"
FROM v_risk_time_distribution
ORDER BY symbol
LIMIT 10;""")

    print(f"✅ Generated {output_file} with {len(all_inserts)} symbols")
    print(f"📁 File size: {Path(output_file).stat().st_size:,} bytes")

if __name__ == "__main__":
    generate_time_bands_sql()