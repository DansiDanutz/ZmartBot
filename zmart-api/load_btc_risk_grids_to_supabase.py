#!/usr/bin/env python3
"""
Load BTC risk grids for 10 symbols that have BTC risk data
Each symbol has 41 points from risk 0.000 to 1.000
Total: 410 records (10 symbols × 41 points)
"""

import json
from pathlib import Path

def generate_sql():
    """Generate SQL to insert BTC risk grid data"""

    grid_dir = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_risk_grids")

    # Symbols that have BTC risk data
    symbols_with_btc = ['AAVE', 'ADA', 'AVAX', 'BNB', 'DOT', 'ETH', 'LINK', 'LTC', 'SOL', 'XRP']

    # Collect all insert statements
    all_inserts = []
    symbol_count = 0
    total_points = 0

    # Process each symbol with BTC risk data
    for symbol in symbols_with_btc:
        json_file = grid_dir / f"{symbol}_risk_grid.json"

        with open(json_file, 'r') as f:
            data = json.load(f)

        if 'btc_risk_grid' not in data or len(data['btc_risk_grid']) == 0:
            print(f"Warning: {symbol} missing BTC risk grid data")
            continue

        symbol_count += 1

        # Get the expected risk values (0.000 to 1.000 in 0.025 increments)
        expected_risks = [round(i * 0.025, 3) for i in range(41)]

        # Create a mapping of risk values to BTC prices
        # Handle both 'price_btc' and 'valuation' keys
        risk_to_btc_price = {}
        for p in data['btc_risk_grid']:
            risk = round(p['risk'], 3)
            # Check for different key names
            if 'price_btc' in p:
                risk_to_btc_price[risk] = p['price_btc']
            elif 'valuation' in p:
                risk_to_btc_price[risk] = p['valuation']
            else:
                print(f"Warning: Unknown price key in {symbol} BTC risk grid: {p.keys()}")
                continue

        # Process each expected risk value
        for risk in expected_risks:
            if risk in risk_to_btc_price:
                price_btc = risk_to_btc_price[risk]
                # Generate INSERT statement
                insert = f"    ('{symbol}', {price_btc:.8f}, {risk:.3f})"
                all_inserts.append(insert)
                total_points += 1

    # Create the complete SQL
    inserts_joined = ',\n'.join(all_inserts)

    # First, create the table if it doesn't exist
    sql = f"""-- Create BTC risk grid table and load data for 10 symbols
-- Total symbols: {symbol_count}
-- Total data points: {total_points} (should be 410 = 10 × 41)
-- Generated: 2025-09-16

-- Create table for BTC risk grids if it doesn't exist
CREATE TABLE IF NOT EXISTS cryptoverse_btc_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_btc DECIMAL(20, 10) NOT NULL,
    btc_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, btc_risk)
);

-- Clear existing BTC risk data (optional - remove if you want to keep existing data)
TRUNCATE TABLE cryptoverse_btc_risk_grid;

-- Insert all BTC risk grid points
INSERT INTO cryptoverse_btc_risk_grid (symbol, price_btc, btc_risk) VALUES
{inserts_joined}
ON CONFLICT (symbol, btc_risk) DO UPDATE
SET price_btc = EXCLUDED.price_btc;

-- Verify the load
SELECT
    symbol,
    COUNT(*) as points,
    MIN(btc_risk) as min_risk,
    MAX(btc_risk) as max_risk,
    MIN(price_btc) as min_price_btc,
    MAX(price_btc) as max_price_btc
FROM cryptoverse_btc_risk_grid
GROUP BY symbol
ORDER BY symbol;

-- Summary statistics
SELECT
    COUNT(DISTINCT symbol) as total_symbols,
    COUNT(*) as total_points,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT symbol), 1) as avg_points_per_symbol
FROM cryptoverse_btc_risk_grid;

-- Show combined view of both FIAT and BTC risk for symbols that have both
SELECT
    f.symbol,
    f.fiat_risk as risk_level,
    f.price_usd,
    b.price_btc,
    ROUND(f.price_usd / b.price_btc, 2) as implied_btc_price
FROM cryptoverse_risk_grid f
JOIN cryptoverse_btc_risk_grid b
    ON f.symbol = b.symbol
    AND f.fiat_risk = b.btc_risk
WHERE f.symbol IN ('ETH', 'SOL', 'BNB')
    AND f.fiat_risk IN (0.25, 0.50, 0.75)
ORDER BY f.symbol, f.fiat_risk;
"""

    return sql, symbol_count, total_points

def main():
    """Generate and save SQL file"""

    print("Generating SQL for BTC risk grid data...")
    sql, symbol_count, total_points = generate_sql()

    # Save to file
    output_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/insert_btc_risk_grids.sql"
    with open(output_file, 'w') as f:
        f.write(sql)

    print(f"\n✅ SQL file generated successfully!")
    print(f"📊 Statistics:")
    print(f"  - Symbols with BTC risk: {symbol_count}")
    print(f"  - Total data points: {total_points}")
    print(f"  - Expected: 410 (10 × 41)")
    print(f"\n📁 Output file: {output_file}")
    print(f"\n🚀 Next steps:")
    print(f"  1. Open Supabase SQL Editor")
    print(f"  2. Copy and paste the SQL from {output_file}")
    print(f"  3. Run the query to create table and load BTC risk data")

    # Also create a summary JSON
    summary = {
        "symbols_with_btc_risk": symbol_count,
        "total_btc_data_points": total_points,
        "expected_points": 410,
        "complete": total_points == 410,
        "symbols": ['AAVE', 'ADA', 'AVAX', 'BNB', 'DOT', 'ETH', 'LINK', 'LTC', 'SOL', 'XRP']
    }

    summary_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/btc_risk_grid_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📋 Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()