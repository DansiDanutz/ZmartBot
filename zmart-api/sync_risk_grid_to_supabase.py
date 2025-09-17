#!/usr/bin/env python3
"""
Sync Complete Risk Grid to Supabase
41 price points per symbol (0.000 to 1.000 in 0.025 increments)
Both Fiat and BTC risk grids
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def create_sample_grid_data():
    """
    Create sample grid data structure
    41 points from risk 0.000 to 1.000 (0.025 increments)
    """

    # Example structure for complete risk grid
    sample_data = {
        "symbols": {
            "SOL": {
                "fiat_risk_grid": [
                    # 41 price points for Fiat Risk
                    {"price": 10.00, "risk_value": 0.000},
                    {"price": 15.00, "risk_value": 0.025},
                    {"price": 20.00, "risk_value": 0.050},
                    {"price": 25.00, "risk_value": 0.075},
                    {"price": 30.00, "risk_value": 0.100},
                    {"price": 35.00, "risk_value": 0.125},
                    {"price": 40.00, "risk_value": 0.150},
                    {"price": 50.00, "risk_value": 0.175},
                    {"price": 60.00, "risk_value": 0.200},
                    {"price": 70.00, "risk_value": 0.225},
                    {"price": 80.00, "risk_value": 0.250},
                    {"price": 90.00, "risk_value": 0.275},
                    {"price": 100.00, "risk_value": 0.300},
                    {"price": 115.00, "risk_value": 0.325},
                    {"price": 130.00, "risk_value": 0.350},
                    {"price": 145.00, "risk_value": 0.375},
                    {"price": 160.00, "risk_value": 0.400},
                    {"price": 180.00, "risk_value": 0.425},
                    {"price": 200.00, "risk_value": 0.450},
                    {"price": 220.00, "risk_value": 0.475},
                    {"price": 240.00, "risk_value": 0.500},
                    {"price": 260.00, "risk_value": 0.525},
                    {"price": 280.00, "risk_value": 0.550},
                    {"price": 300.00, "risk_value": 0.575},
                    {"price": 330.00, "risk_value": 0.600},
                    {"price": 360.00, "risk_value": 0.625},
                    {"price": 400.00, "risk_value": 0.650},
                    {"price": 450.00, "risk_value": 0.675},
                    {"price": 500.00, "risk_value": 0.700},
                    {"price": 550.00, "risk_value": 0.725},
                    {"price": 600.00, "risk_value": 0.750},
                    {"price": 700.00, "risk_value": 0.775},
                    {"price": 800.00, "risk_value": 0.800},
                    {"price": 900.00, "risk_value": 0.825},
                    {"price": 1000.00, "risk_value": 0.850},
                    {"price": 1200.00, "risk_value": 0.875},
                    {"price": 1400.00, "risk_value": 0.900},
                    {"price": 1600.00, "risk_value": 0.925},
                    {"price": 1800.00, "risk_value": 0.950},
                    {"price": 2000.00, "risk_value": 0.975},
                    {"price": 2500.00, "risk_value": 1.000}
                ],
                "btc_risk_grid": [
                    # 41 price points for BTC Risk (prices in BTC)
                    {"price": 0.0001, "risk_value": 0.000},
                    {"price": 0.0002, "risk_value": 0.025},
                    {"price": 0.0003, "risk_value": 0.050},
                    # ... continue for all 41 points
                ]
            }
        }
    }

    return sample_data

def generate_sql_inserts(grid_data: Dict) -> List[str]:
    """
    Generate SQL INSERT statements for the complete risk grid
    """
    sql_statements = []

    # Create the main insert statement
    sql_statements.append("-- Complete Risk Grid Data")
    sql_statements.append("-- 41 price points per risk type per symbol")
    sql_statements.append("-- Total: 82 points per symbol (41 Fiat + 41 BTC)")
    sql_statements.append("")

    # For Fiat Risk Grid
    sql_statements.append("-- Fiat Risk Grid")
    sql_statements.append("INSERT INTO public.cryptoverse_fiat_risk_grid (symbol, price, risk_value, risk_type) VALUES")

    fiat_values = []
    for symbol, data in grid_data.get("symbols", {}).items():
        for point in data.get("fiat_risk_grid", []):
            fiat_values.append(
                f"    ('{symbol}', {point['price']}, {point['risk_value']}, 'FIAT')"
            )

    sql_statements.append(",\n".join(fiat_values))
    sql_statements.append("ON CONFLICT (symbol, price, risk_type) DO UPDATE SET")
    sql_statements.append("    risk_value = EXCLUDED.risk_value,")
    sql_statements.append("    updated_at = NOW();")
    sql_statements.append("")

    # For BTC Risk Grid
    sql_statements.append("-- BTC Risk Grid")
    sql_statements.append("INSERT INTO public.cryptoverse_btc_risk_grid (symbol, price_btc, risk_value, risk_type) VALUES")

    btc_values = []
    for symbol, data in grid_data.get("symbols", {}).items():
        for point in data.get("btc_risk_grid", []):
            btc_values.append(
                f"    ('{symbol}', {point['price']}, {point['risk_value']}, 'BTC')"
            )

    sql_statements.append(",\n".join(btc_values))
    sql_statements.append("ON CONFLICT (symbol, price_btc, risk_type) DO UPDATE SET")
    sql_statements.append("    risk_value = EXCLUDED.risk_value,")
    sql_statements.append("    updated_at = NOW();")

    return sql_statements

def calculate_statistics(grid_data: Dict) -> Dict:
    """
    Calculate statistics for the risk grid data
    """
    stats = {
        "total_symbols": len(grid_data.get("symbols", {})),
        "points_per_symbol": 0,
        "total_data_points": 0,
        "risk_levels": 41,  # 0.000 to 1.000 in 0.025 increments
        "symbols": []
    }

    for symbol, data in grid_data.get("symbols", {}).items():
        fiat_points = len(data.get("fiat_risk_grid", []))
        btc_points = len(data.get("btc_risk_grid", []))
        total_points = fiat_points + btc_points

        stats["symbols"].append({
            "symbol": symbol,
            "fiat_points": fiat_points,
            "btc_points": btc_points,
            "total_points": total_points
        })

        stats["total_data_points"] += total_points

    if stats["symbols"]:
        stats["points_per_symbol"] = stats["total_data_points"] // stats["total_symbols"]

    return stats

def main():
    """
    Main function to process risk grid data
    """
    print("="*60)
    print("COMPLETE RISK GRID PROCESSOR")
    print("="*60)
    print()
    print("📊 Risk Grid Structure:")
    print("  - 41 risk levels (0.000 to 1.000 in 0.025 increments)")
    print("  - Each level maps to a specific price")
    print("  - Both Fiat and BTC risk grids")
    print("  - Total: 82 data points per symbol")
    print()

    # Check if we have the complete grid file
    grid_file = Path("cryptoverse_complete_risk_database.json")

    if grid_file.exists():
        print(f"✅ Found grid file: {grid_file}")
        with open(grid_file, 'r') as f:
            grid_data = json.load(f)
    else:
        print("⚠️ Grid file not found, using sample structure")
        grid_data = create_sample_grid_data()

    # Calculate statistics
    stats = calculate_statistics(grid_data)

    print("\n📈 Grid Statistics:")
    print(f"  - Total Symbols: {stats['total_symbols']}")
    print(f"  - Points per Symbol: {stats['points_per_symbol']}")
    print(f"  - Total Data Points: {stats['total_data_points']}")
    print()

    # Expected totals
    expected_symbols = 20
    expected_points_per_symbol = 82  # 41 Fiat + 41 BTC
    expected_total = expected_symbols * expected_points_per_symbol

    print("📋 Expected Data Volume:")
    print(f"  - Symbols: {expected_symbols}")
    print(f"  - Points per Symbol: {expected_points_per_symbol}")
    print(f"  - Total Expected: {expected_total:,} data points")
    print()

    # Generate SQL
    sql_statements = generate_sql_inserts(grid_data)

    # Save SQL to file
    sql_file = Path("risk_grid_insert.sql")
    with open(sql_file, 'w') as f:
        f.write("\n".join(sql_statements))

    print(f"✅ SQL statements saved to: {sql_file}")
    print()
    print("📊 Risk Level Mapping (0.025 increments):")
    print("  Risk 0.000 = Bottom (lowest price)")
    print("  Risk 0.250 = 25% (accumulation zone)")
    print("  Risk 0.500 = 50% (mid-cycle)")
    print("  Risk 0.750 = 75% (distribution zone)")
    print("  Risk 1.000 = Top (highest price)")
    print()
    print("🎯 With this data, you can query exact risk at ANY price!")
    print("  Example: SOL at $250 → Look up in grid → Get exact risk")

    # Create a lookup example
    print("\n📝 SQL Query Examples:")
    print("```sql")
    print("-- Get exact risk for SOL at specific price")
    print("SELECT * FROM cryptoverse_fiat_risk_grid")
    print("WHERE symbol = 'SOL' AND price = 250;")
    print()
    print("-- Get risk for all symbols at 0.500 level")
    print("SELECT * FROM cryptoverse_fiat_risk_grid")
    print("WHERE risk_value = 0.500;")
    print()
    print("-- Find what price SOL needs for 0.300 risk")
    print("SELECT price FROM cryptoverse_fiat_risk_grid")
    print("WHERE symbol = 'SOL' AND risk_value = 0.300;")
    print("```")

if __name__ == "__main__":
    main()