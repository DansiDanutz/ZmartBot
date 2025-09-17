#!/usr/bin/env python3
"""
Calculate Risk Coefficients based on Time Spent in Risk Bands
Uses the IntoTheCryptoverse methodology where coefficients are derived from
the percentage of time spent in each risk band
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Supabase client
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def calculate_risk_coefficient(days_in_band: float, total_days: float, band_center: float) -> float:
    """
    Calculate risk coefficient for a specific band based on time spent

    Methodology:
    - Base coefficient is the center point of the risk band (e.g., 0.05 for 0.0-0.1)
    - Weight by percentage of time spent in that band
    - Apply confidence factor based on data quality
    """
    if total_days == 0:
        return 0.0

    # Calculate percentage of time in this band
    time_percentage = (days_in_band / total_days) * 100

    # The coefficient is weighted by time spent
    # More time in a band = stronger influence on overall risk
    coefficient = band_center * (time_percentage / 100)

    return round(coefficient, 6)

def calculate_weighted_risk_score(risk_bands: Dict[str, float], total_days: float) -> float:
    """
    Calculate overall weighted risk score based on all bands
    """
    weighted_score = 0.0

    for band_label, days in risk_bands.items():
        # Parse band label to get center point
        lower, upper = band_label.split('-')
        lower = float(lower)
        upper = float(upper)
        band_center = (lower + upper) / 2

        # Weight by time spent
        if total_days > 0:
            weight = days / total_days
            weighted_score += band_center * weight

    return round(weighted_score, 4)

def generate_coefficients_for_symbol(symbol_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate all risk coefficients for a symbol
    """
    symbol = symbol_data['symbol']
    symbol_name = symbol_data['symbol_name']
    total_days = symbol_data['total_days']
    risk_bands = symbol_data['risk_bands']

    # Calculate coefficients for each band
    band_coefficients = {}

    for band_label, days in risk_bands.items():
        # Parse band label
        lower, upper = band_label.split('-')
        lower = float(lower)
        upper = float(upper)
        band_center = (lower + upper) / 2

        # Calculate coefficient
        coefficient = calculate_risk_coefficient(days, total_days, band_center)

        band_coefficients[band_label] = {
            'days_in_band': days,
            'percentage': round((days / total_days * 100) if total_days > 0 else 0, 2),
            'coefficient': coefficient,
            'band_center': band_center,
            'lower': lower,
            'upper': upper
        }

    # Calculate overall weighted risk score
    weighted_risk_score = calculate_weighted_risk_score(risk_bands, total_days)

    # Determine current risk level based on current band
    current_band = symbol_data.get('current_risk_band', '0.5-0.6')
    current_lower, current_upper = current_band.split('-')
    current_risk_level = (float(current_lower) + float(current_upper)) / 2

    return {
        'symbol': symbol,
        'symbol_name': symbol_name,
        'birth_date': symbol_data['birth_date'],
        'total_days': total_days,
        'band_coefficients': band_coefficients,
        'weighted_risk_score': weighted_risk_score,
        'current_risk_level': current_risk_level,
        'current_risk_band': current_band,
        'confidence_level': symbol_data.get('confidence_level', 7),
        'data_type': symbol_data.get('data_type', 'estimated'),
        'calculated_at': datetime.now().isoformat()
    }

async def store_coefficients_in_database(supabase: Client, coefficients_data: Dict[str, Any]):
    """
    Store calculated coefficients in Supabase database
    """
    symbol = coefficients_data['symbol']

    # Store each band's data
    for band_label, band_data in coefficients_data['band_coefficients'].items():
        try:
            # Prepare data for database
            db_data = {
                'symbol': symbol,
                'symbol_name': coefficients_data['symbol_name'],
                'risk_band_lower': band_data['lower'],
                'risk_band_upper': band_data['upper'],
                'days_in_band': band_data['days_in_band'],
                'percentage_in_band': band_data['percentage'],
                'market_cycle': 'all',  # Default to all cycles
                'currently_in_band': band_label == coefficients_data['current_risk_band'],
                'confidence_level': coefficients_data['confidence_level'],
                'data_source': 'intothecryptoverse'
            }

            # Use the upsert function
            result = await supabase.rpc('upsert_risk_band_data', {
                'p_symbol': db_data['symbol'],
                'p_symbol_name': db_data['symbol_name'],
                'p_risk_lower': db_data['risk_band_lower'],
                'p_risk_upper': db_data['risk_band_upper'],
                'p_days': db_data['days_in_band'],
                'p_percentage': db_data['percentage_in_band'],
                'p_market_cycle': db_data['market_cycle'],
                'p_currently_in': db_data['currently_in_band'],
                'p_confidence': db_data['confidence_level']
            }).execute()

            print(f"✅ Stored {symbol} band {band_label} in database")

        except Exception as e:
            print(f"❌ Error storing {symbol} band {band_label}: {e}")

async def main():
    """
    Main function to calculate and store risk coefficients
    """
    print("🔄 Starting Risk Coefficient Calculation...")

    # Load time bands data
    input_path = Path("extracted_risk_time_bands")
    output_path = Path("calculated_risk_coefficients")
    output_path.mkdir(exist_ok=True)

    # Read all symbols data
    all_symbols_file = input_path / "risk_time_bands_all_symbols.json"

    if not all_symbols_file.exists():
        print("❌ Time bands data not found. Please run extract_time_risk_bands.py first.")
        return

    with open(all_symbols_file, 'r') as f:
        symbols_data = json.load(f)

    print(f"📊 Processing {len(symbols_data)} symbols...")

    # Initialize Supabase client if credentials are available
    supabase = None
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Connected to Supabase")
        except Exception as e:
            print(f"⚠️ Could not connect to Supabase: {e}")
            print("   Coefficients will be saved to files only")

    # Calculate coefficients for each symbol
    all_coefficients = []

    for symbol_data in symbols_data:
        symbol = symbol_data['symbol']
        print(f"\n📈 Processing {symbol}...")

        # Generate coefficients
        coefficients = generate_coefficients_for_symbol(symbol_data)
        all_coefficients.append(coefficients)

        # Save to individual file
        with open(output_path / f"{symbol}_coefficients.json", 'w') as f:
            json.dump(coefficients, f, indent=2)

        # Store in database if connected
        if supabase:
            await store_coefficients_in_database(supabase, coefficients)

        # Print summary
        print(f"  • Weighted Risk Score: {coefficients['weighted_risk_score']}")
        print(f"  • Current Risk Level: {coefficients['current_risk_level']}")
        print(f"  • Current Band: {coefficients['current_risk_band']}")
        print(f"  • Total Days Tracked: {coefficients['total_days']}")

    # Save consolidated coefficients
    with open(output_path / "all_risk_coefficients.json", 'w') as f:
        json.dump(all_coefficients, f, indent=2)

    # Create summary report
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_symbols': len(all_coefficients),
        'methodology': {
            'description': 'Risk coefficients calculated based on time spent in each risk band',
            'formula': 'coefficient = band_center * (time_percentage / 100)',
            'weighted_score': 'Sum of (band_center * time_weight) for all bands'
        },
        'symbols_processed': [c['symbol'] for c in all_coefficients],
        'risk_scores': {
            c['symbol']: {
                'weighted_score': c['weighted_risk_score'],
                'current_level': c['current_risk_level'],
                'confidence': c['confidence_level']
            }
            for c in all_coefficients
        }
    }

    with open(output_path / "COEFFICIENTS_SUMMARY.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*50)
    print("✅ Risk Coefficient Calculation Complete!")
    print(f"📁 Coefficients saved to: {output_path}")

    if supabase:
        print("✅ Data stored in Supabase database")
    else:
        print("⚠️ Database storage skipped (no connection)")

    # Print top 5 by risk score
    sorted_symbols = sorted(all_coefficients, key=lambda x: x['weighted_risk_score'], reverse=True)

    print("\n📊 Top 5 Symbols by Risk Score:")
    for i, coef in enumerate(sorted_symbols[:5], 1):
        print(f"{i}. {coef['symbol']:6} - Score: {coef['weighted_risk_score']:.4f} (Current: {coef['current_risk_level']:.2f})")

if __name__ == "__main__":
    asyncio.run(main())