#!/usr/bin/env python3
"""
Load all 25 symbols' risk grids into Supabase cryptoverse_risk_grid table
Each symbol has 41 points from risk 0.000 to 1.000
Total: 1,025 records (25 symbols × 41 points)
"""

import json
import os
from pathlib import Path

def generate_sql():
    """Generate SQL to insert all risk grid data"""

    grid_dir = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_risk_grids")

    # Collect all insert statements
    all_inserts = []
    symbol_count = 0
    total_points = 0

    # Process each JSON file
    for json_file in sorted(grid_dir.glob("*_risk_grid.json")):
        with open(json_file, 'r') as f:
            data = json.load(f)

        symbol = data['symbol']
        symbol_count += 1

        # Process fiat risk grid (41 points)
        # Get the expected risk values (0.000 to 1.000 in 0.025 increments)
        expected_risks = [round(i * 0.025, 3) for i in range(41)]

        # Create a mapping of risk values to prices
        risk_to_price = {round(p['risk'], 3): p['price'] for p in data['fiat_risk_grid']}

        # Process each expected risk value
        for risk in expected_risks:
            if risk in risk_to_price:
                price = risk_to_price[risk]
                # Generate INSERT statement
                insert = f"    ('{symbol}', {price:.2f}, {risk:.3f})"
                all_inserts.append(insert)
                total_points += 1

    # Create the complete SQL
    inserts_joined = ',\n'.join(all_inserts)
    sql = f"""-- Load complete risk grids for all 25 symbols
-- Total symbols: {symbol_count}
-- Total data points: {total_points} (should be 1,025 = 25 × 41)
-- Generated: 2025-09-16

-- Clear existing data (optional - remove if you want to keep existing data)
TRUNCATE TABLE cryptoverse_risk_grid;

-- Insert all risk grid points
INSERT INTO cryptoverse_risk_grid (symbol, price_usd, fiat_risk) VALUES
{inserts_joined};

-- Verify the load
SELECT
    symbol,
    COUNT(*) as points,
    MIN(fiat_risk) as min_risk,
    MAX(fiat_risk) as max_risk,
    MIN(price_usd) as min_price,
    MAX(price_usd) as max_price
FROM cryptoverse_risk_grid
GROUP BY symbol
ORDER BY symbol;

-- Summary statistics
SELECT
    COUNT(DISTINCT symbol) as total_symbols,
    COUNT(*) as total_points,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT symbol), 1) as avg_points_per_symbol
FROM cryptoverse_risk_grid;
"""

    return sql, symbol_count, total_points

def main():
    """Generate and save SQL file"""

    print("Generating SQL for risk grid data...")
    sql, symbol_count, total_points = generate_sql()

    # Save to file
    output_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/insert_full_risk_grids.sql"
    with open(output_file, 'w') as f:
        f.write(sql)

    print(f"\n✅ SQL file generated successfully!")
    print(f"📊 Statistics:")
    print(f"  - Symbols processed: {symbol_count}")
    print(f"  - Total data points: {total_points}")
    print(f"  - Expected: 1,025 (25 × 41)")
    print(f"\n📁 Output file: {output_file}")
    print(f"\n🚀 Next steps:")
    print(f"  1. Open Supabase SQL Editor")
    print(f"  2. Copy and paste the SQL from {output_file}")
    print(f"  3. Run the query to load all data")

    # Also create a summary JSON
    summary = {
        "symbols_processed": symbol_count,
        "total_data_points": total_points,
        "expected_points": 1025,
        "complete": total_points == 1025
    }

    summary_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/risk_grid_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📋 Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()