#!/usr/bin/env python3
"""
Manual Risk Grid Data Entry
Since we know the structure is 41 points from 0.000 to 1.000 in 0.025 increments
We can create sample data and you can update with actual values
"""

import json
from decimal import Decimal

# Risk levels from 0.000 to 1.000 in 0.025 increments (41 points)
RISK_LEVELS = [round(i * 0.025, 3) for i in range(41)]

# Sample price points for each risk level (you'll need to update these with actual values)
# These are example prices - replace with actual data from IntoTheCryptoverse

SYMBOL_RISK_GRIDS = {
    "BTC": {
        "fiat_risk_prices": {
            0.000: 10000,
            0.025: 12000,
            0.050: 15000,
            0.075: 18000,
            0.100: 20000,
            0.125: 23000,
            0.150: 26000,
            0.175: 29000,
            0.200: 32000,
            0.225: 35000,
            0.250: 38000,
            0.275: 42000,
            0.300: 46000,
            0.325: 50000,
            0.350: 55000,
            0.375: 60000,
            0.400: 65000,
            0.425: 70000,
            0.450: 75000,
            0.475: 80000,
            0.500: 85000,
            0.525: 90000,
            0.550: 95000,  # Current level approximately
            0.575: 100000,
            0.600: 110000,
            0.625: 120000,
            0.650: 130000,
            0.675: 140000,
            0.700: 150000,
            0.725: 170000,
            0.750: 190000,
            0.775: 210000,
            0.800: 230000,
            0.825: 250000,
            0.850: 280000,
            0.875: 320000,
            0.900: 360000,
            0.925: 420000,
            0.950: 500000,
            0.975: 600000,
            1.000: 750000
        }
    },
    "ETH": {
        "fiat_risk_prices": {
            0.000: 500,
            0.025: 600,
            0.050: 700,
            0.075: 800,
            0.100: 900,
            0.125: 1000,
            0.150: 1200,
            0.175: 1400,
            0.200: 1600,
            0.225: 1800,
            0.250: 2000,
            0.275: 2300,
            0.300: 2600,
            0.325: 2900,
            0.350: 3200,
            0.375: 3500,
            0.400: 3800,
            0.425: 4200,
            0.450: 4600,  # Current level approximately
            0.475: 5000,
            0.500: 5500,
            0.525: 6000,
            0.550: 6500,
            0.575: 7000,
            0.600: 8000,
            0.625: 9000,
            0.650: 10000,
            0.675: 11000,
            0.700: 12000,
            0.725: 13500,
            0.750: 15000,
            0.775: 17000,
            0.800: 19000,
            0.825: 22000,
            0.850: 25000,
            0.875: 28000,
            0.900: 32000,
            0.925: 36000,
            0.950: 42000,
            0.975: 50000,
            1.000: 60000
        },
        "btc_risk_prices": {  # Prices in BTC
            0.000: 0.005,
            0.025: 0.007,
            0.050: 0.009,
            0.075: 0.011,
            0.100: 0.013,
            0.125: 0.015,
            0.150: 0.018,
            0.175: 0.021,
            0.200: 0.024,
            0.225: 0.027,
            0.250: 0.030,
            0.275: 0.033,
            0.300: 0.036,
            0.325: 0.038,
            0.350: 0.040,  # Current level approximately
            0.375: 0.042,
            0.400: 0.045,
            0.425: 0.048,
            0.450: 0.051,
            0.475: 0.055,
            0.500: 0.060,
            0.525: 0.065,
            0.550: 0.070,
            0.575: 0.075,
            0.600: 0.080,
            0.625: 0.085,
            0.650: 0.090,
            0.675: 0.095,
            0.700: 0.100,
            0.725: 0.110,
            0.750: 0.120,
            0.775: 0.130,
            0.800: 0.140,
            0.825: 0.150,
            0.850: 0.165,
            0.875: 0.180,
            0.900: 0.200,
            0.925: 0.220,
            0.950: 0.250,
            0.975: 0.280,
            1.000: 0.320
        }
    },
    "SOL": {
        "fiat_risk_prices": {
            0.000: 5,
            0.025: 8,
            0.050: 12,
            0.075: 16,
            0.100: 20,
            0.125: 25,
            0.150: 30,
            0.175: 35,
            0.200: 42,
            0.225: 50,
            0.250: 60,
            0.275: 75,
            0.300: 90,
            0.325: 110,
            0.350: 130,
            0.375: 150,
            0.400: 175,
            0.425: 200,
            0.450: 225,
            0.475: 235,
            0.500: 245,  # Current level approximately (238.88)
            0.525: 260,
            0.550: 280,
            0.575: 300,
            0.600: 330,
            0.625: 360,
            0.650: 400,
            0.675: 450,
            0.700: 500,
            0.725: 550,
            0.750: 600,
            0.775: 700,
            0.800: 800,
            0.825: 900,
            0.850: 1000,
            0.875: 1200,
            0.900: 1400,
            0.925: 1600,
            0.950: 1800,
            0.975: 2000,
            1.000: 2500
        },
        "btc_risk_prices": {  # Prices in BTC
            0.000: 0.0001,
            0.025: 0.0002,
            0.050: 0.0003,
            0.075: 0.0004,
            0.100: 0.0005,
            0.125: 0.0006,
            0.150: 0.0007,
            0.175: 0.0008,
            0.200: 0.0009,
            0.225: 0.0010,
            0.250: 0.0012,
            0.275: 0.0014,
            0.300: 0.0016,
            0.325: 0.0018,
            0.350: 0.0020,  # Current level approximately
            0.375: 0.0022,
            0.400: 0.0024,
            0.425: 0.0026,
            0.450: 0.0028,
            0.475: 0.0030,
            0.500: 0.0033,
            0.525: 0.0036,
            0.550: 0.0040,
            0.575: 0.0044,
            0.600: 0.0048,
            0.625: 0.0052,
            0.650: 0.0056,
            0.675: 0.0060,
            0.700: 0.0065,
            0.725: 0.0070,
            0.750: 0.0075,
            0.775: 0.0080,
            0.800: 0.0085,
            0.825: 0.0090,
            0.850: 0.0095,
            0.875: 0.0100,
            0.900: 0.0110,
            0.925: 0.0120,
            0.950: 0.0130,
            0.975: 0.0140,
            1.000: 0.0150
        }
    }
}

def generate_sql_inserts():
    """Generate SQL INSERT statements for the risk grids"""

    print("-- Complete Risk Grid Data Import")
    print("-- 41 price points per symbol per risk type")
    print()

    # Generate Fiat Risk Grid inserts
    print("-- Inserting Fiat Risk Grid Data")
    print("INSERT INTO public.cryptoverse_risk_grid (symbol, price_usd, fiat_risk) VALUES")

    fiat_values = []
    for symbol, data in SYMBOL_RISK_GRIDS.items():
        if "fiat_risk_prices" in data:
            for risk_level, price in data["fiat_risk_prices"].items():
                fiat_values.append(f"    ('{symbol}', {price}, {risk_level})")

    print(",\n".join(fiat_values))
    print("ON CONFLICT (symbol, price_usd) DO UPDATE SET")
    print("    fiat_risk = EXCLUDED.fiat_risk;")
    print()

    # Generate BTC Risk Grid inserts
    print("-- Inserting BTC Risk Grid Data")
    print("INSERT INTO public.cryptoverse_btc_risk_grid (symbol, price_btc, btc_risk) VALUES")

    btc_values = []
    for symbol, data in SYMBOL_RISK_GRIDS.items():
        if "btc_risk_prices" in data:
            for risk_level, price in data["btc_risk_prices"].items():
                btc_values.append(f"    ('{symbol}', {price}, {risk_level})")

    print(",\n".join(btc_values))
    print("ON CONFLICT (symbol, price_btc) DO UPDATE SET")
    print("    btc_risk = EXCLUDED.btc_risk;")
    print()

    # Generate summary inserts
    print("-- Updating Grid Summary")
    for symbol in SYMBOL_RISK_GRIDS.keys():
        print(f"INSERT INTO public.cryptoverse_grid_summary (symbol, total_fiat_points, total_btc_points)")
        print(f"VALUES ('{symbol}', 41, 41)")
        print(f"ON CONFLICT (symbol) DO UPDATE SET")
        print(f"    total_fiat_points = 41,")
        print(f"    total_btc_points = 41,")
        print(f"    last_grid_update = NOW();")
        print()

def create_json_file():
    """Create a JSON file with the grid data"""

    output = {
        "metadata": {
            "source": "IntoTheCryptoverse",
            "risk_levels": RISK_LEVELS,
            "total_levels": 41,
            "increment": 0.025
        },
        "symbols": {}
    }

    for symbol, data in SYMBOL_RISK_GRIDS.items():
        output["symbols"][symbol] = {
            "fiat_risk_grid": [],
            "btc_risk_grid": []
        }

        # Add Fiat risk grid
        if "fiat_risk_prices" in data:
            for risk_level, price in data["fiat_risk_prices"].items():
                output["symbols"][symbol]["fiat_risk_grid"].append({
                    "price": price,
                    "risk_value": risk_level
                })

        # Add BTC risk grid
        if "btc_risk_prices" in data:
            for risk_level, price in data["btc_risk_prices"].items():
                output["symbols"][symbol]["btc_risk_grid"].append({
                    "price": price,
                    "risk_value": risk_level
                })

    # Save to file
    with open("cryptoverse_manual_risk_grid.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ JSON file saved: cryptoverse_manual_risk_grid.json")

if __name__ == "__main__":
    print("="*60)
    print("MANUAL RISK GRID DATA GENERATOR")
    print("="*60)
    print()
    print("This creates sample risk grid data with the correct structure.")
    print("You can manually update the prices for each risk level.")
    print()

    # Generate SQL
    generate_sql_inserts()

    # Create JSON file
    create_json_file()

    print()
    print("📌 INSTRUCTIONS:")
    print("1. Copy the SQL above and run it in Supabase")
    print("2. Or update the prices in this file with actual values")
    print("3. The structure is correct: 41 levels from 0.000 to 1.000")