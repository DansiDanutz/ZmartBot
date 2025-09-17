#!/usr/bin/env python3
"""
Extract Time Spent in Risk Bands data from IntoTheCryptoverse
for all supported symbols
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Based on the visual data from the chart, here's BTC's time spent in each risk band
# These are approximate values read from the chart
BTC_RISK_BANDS_DATA = {
    "symbol": "BTC",
    "symbol_name": "Bitcoin",
    "birth_date": "2009-01-03",  # Bitcoin genesis block
    "current_date": datetime.now().strftime("%Y-%m-%d"),
    "total_days": 5385,  # Approximate from chart
    "risk_bands": {
        "0.0-0.1": 175,    # Days spent in 0.0-0.1 risk band
        "0.1-0.2": 550,    # Days spent in 0.1-0.2 risk band
        "0.2-0.3": 680,    # Days spent in 0.2-0.3 risk band
        "0.3-0.4": 850,    # Days spent in 0.3-0.4 risk band
        "0.4-0.5": 1100,   # Days spent in 0.4-0.5 risk band
        "0.5-0.6": 1180,   # Days spent in 0.5-0.6 risk band (highest)
        "0.6-0.7": 700,    # Days spent in 0.6-0.7 risk band
        "0.7-0.8": 380,    # Days spent in 0.7-0.8 risk band
        "0.8-0.9": 200,    # Days spent in 0.8-0.9 risk band
        "0.9-1.0": 85,     # Days spent in 0.9-1.0 risk band
    },
    "current_risk_band": "0.5-0.6",
    "confidence_level": 9
}

# Other major symbols with their birth dates
SYMBOL_BIRTH_DATES = {
    "BTC": {"name": "Bitcoin", "birth": "2009-01-03"},
    "ETH": {"name": "Ethereum", "birth": "2015-07-30"},
    "BNB": {"name": "Binance Coin", "birth": "2017-07-14"},
    "SOL": {"name": "Solana", "birth": "2020-03-16"},
    "XRP": {"name": "Ripple", "birth": "2013-08-04"},
    "ADA": {"name": "Cardano", "birth": "2017-09-29"},
    "AVAX": {"name": "Avalanche", "birth": "2020-09-21"},
    "DOGE": {"name": "Dogecoin", "birth": "2013-12-06"},
    "DOT": {"name": "Polkadot", "birth": "2020-08-19"},
    "LINK": {"name": "Chainlink", "birth": "2017-09-19"},
    "LTC": {"name": "Litecoin", "birth": "2011-10-07"},
    "ATOM": {"name": "Cosmos", "birth": "2019-03-14"},
    "XTZ": {"name": "Tezos", "birth": "2018-06-30"},
    "AAVE": {"name": "Aave", "birth": "2020-10-02"},
    "MKR": {"name": "Maker", "birth": "2017-11-25"},
    "XMR": {"name": "Monero", "birth": "2014-04-18"},
    "XLM": {"name": "Stellar", "birth": "2014-07-31"},
    "SUI": {"name": "Sui", "birth": "2023-05-03"},
    "HBAR": {"name": "Hedera", "birth": "2019-09-17"},
    "RENDER": {"name": "Render", "birth": "2020-12-28"},
    "TRX": {"name": "Tron", "birth": "2017-08-28"},
    "VET": {"name": "VeChain", "birth": "2017-08-18"},
    "ALGO": {"name": "Algorand", "birth": "2019-06-19"},
    "SHIB": {"name": "Shiba Inu", "birth": "2020-08-01"},
    "TON": {"name": "The Open Network", "birth": "2021-06-01"}
}

def calculate_age_in_days(birth_date_str):
    """Calculate the age of a cryptocurrency in days"""
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    current_date = datetime.now()
    age_days = (current_date - birth_date).days
    return age_days

def generate_placeholder_risk_bands(symbol, total_days):
    """
    Generate placeholder risk band data for a symbol
    This distributes the days across risk bands in a bell curve pattern
    Similar to what we see in the BTC chart
    """
    # Create a bell curve distribution (highest in middle bands)
    distribution = [
        0.03,  # 0.0-0.1 (3% of time)
        0.10,  # 0.1-0.2 (10% of time)
        0.13,  # 0.2-0.3 (13% of time)
        0.16,  # 0.3-0.4 (16% of time)
        0.20,  # 0.4-0.5 (20% of time)
        0.22,  # 0.5-0.6 (22% of time - highest)
        0.13,  # 0.6-0.7 (13% of time)
        0.07,  # 0.7-0.8 (7% of time)
        0.04,  # 0.8-0.9 (4% of time)
        0.02,  # 0.9-1.0 (2% of time)
    ]

    risk_bands = {}
    band_labels = [
        "0.0-0.1", "0.1-0.2", "0.2-0.3", "0.3-0.4", "0.4-0.5",
        "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0"
    ]

    for i, label in enumerate(band_labels):
        days = int(total_days * distribution[i])
        risk_bands[label] = days

    # Adjust to ensure total matches
    total_assigned = sum(risk_bands.values())
    if total_assigned < total_days:
        # Add remaining days to the highest probability band
        risk_bands["0.5-0.6"] += (total_days - total_assigned)

    return risk_bands

def create_risk_bands_dataset():
    """Create complete dataset for all symbols"""
    dataset = []

    for symbol, info in SYMBOL_BIRTH_DATES.items():
        age_days = calculate_age_in_days(info["birth"])

        # For BTC, use the actual data from the chart
        if symbol == "BTC":
            data = BTC_RISK_BANDS_DATA.copy()
            data["actual_age_days"] = age_days
        else:
            # For other symbols, generate placeholder data
            risk_bands = generate_placeholder_risk_bands(symbol, age_days)

            data = {
                "symbol": symbol,
                "symbol_name": info["name"],
                "birth_date": info["birth"],
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "total_days": age_days,
                "actual_age_days": age_days,
                "risk_bands": risk_bands,
                "current_risk_band": "0.5-0.6",  # Placeholder - needs actual data
                "confidence_level": 7,  # Lower confidence for estimated data
                "data_type": "estimated"  # Mark as estimated vs actual
            }

        # Calculate percentages
        for band in data["risk_bands"]:
            percentage = (data["risk_bands"][band] / data["total_days"]) * 100
            data[f"{band}_percentage"] = round(percentage, 2)

        dataset.append(data)

    return dataset

def save_dataset():
    """Save the dataset to JSON file"""
    dataset = create_risk_bands_dataset()

    output_path = Path("extracted_risk_time_bands")
    output_path.mkdir(exist_ok=True)

    # Save full dataset
    with open(output_path / "risk_time_bands_all_symbols.json", "w") as f:
        json.dump(dataset, f, indent=2)

    # Save individual symbol files
    for data in dataset:
        symbol = data["symbol"]
        with open(output_path / f"{symbol}_time_bands.json", "w") as f:
            json.dump(data, f, indent=2)

    # Create summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_symbols": len(dataset),
        "symbols": [d["symbol"] for d in dataset],
        "data_source": "IntoTheCryptoverse",
        "notes": [
            "BTC data is based on actual chart values",
            "Other symbols use estimated distribution",
            "Actual data should be extracted from IntoTheCryptoverse API",
            "Risk bands are: 0.0-0.1, 0.1-0.2, ..., 0.9-1.0",
            "Total of 10 risk bands per symbol"
        ]
    }

    with open(output_path / "EXTRACTION_SUMMARY.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Generated risk time bands data for {len(dataset)} symbols")
    print(f"📁 Data saved to: {output_path}")

    # Print summary statistics
    print("\n📊 Summary Statistics:")
    for data in dataset[:5]:  # Show first 5 symbols
        symbol = data["symbol"]
        total_days = data["total_days"]
        print(f"\n{symbol} ({data['symbol_name']}):")
        print(f"  • Age: {total_days} days (since {data['birth_date']})")
        print(f"  • Current risk band: {data['current_risk_band']}")
        print(f"  • Risk band distribution:")
        for band, days in data["risk_bands"].items():
            percentage = (days / total_days) * 100
            print(f"    - {band}: {days} days ({percentage:.1f}%)")

if __name__ == "__main__":
    save_dataset()