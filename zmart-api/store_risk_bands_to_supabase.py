#!/usr/bin/env python3
"""
Store Risk Bands Data to Supabase Database
Uses direct SQL inserts to populate the risk_time_bands table
"""

import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def main():
    """
    Main function to store risk bands data in Supabase
    """
    print("🔄 Storing Risk Bands Data to Supabase...")

    # Check for Supabase credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment variables")
        print("   Please add them to your .env file")
        return

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Could not connect to Supabase: {e}")
        return

    # Load calculated coefficients
    coefficients_path = Path("calculated_risk_coefficients/all_risk_coefficients.json")

    if not coefficients_path.exists():
        print("❌ Coefficients file not found. Please run calculate_risk_coefficients.py first.")
        return

    with open(coefficients_path, 'r') as f:
        all_coefficients = json.load(f)

    print(f"📊 Processing {len(all_coefficients)} symbols...")

    success_count = 0
    error_count = 0

    for coef_data in all_coefficients:
        symbol = coef_data['symbol']
        symbol_name = coef_data['symbol_name']

        print(f"\n📈 Storing {symbol} ({symbol_name})...")

        # Process each risk band
        for band_label, band_data in coef_data['band_coefficients'].items():
            try:
                # Prepare data for insertion
                insert_data = {
                    'symbol': symbol,
                    'symbol_name': symbol_name,
                    'risk_band_lower': band_data['lower'],
                    'risk_band_upper': band_data['upper'],
                    'days_in_band': band_data['days_in_band'],
                    'percentage_in_band': band_data['percentage'],
                    'market_cycle': 'all',
                    'currently_in_band': band_label == coef_data['current_risk_band'],
                    'confidence_level': coef_data['confidence_level'],
                    'data_source': 'intothecryptoverse',
                    'last_updated': datetime.now().isoformat()
                }

                # Insert or update the data
                response = supabase.table('risk_time_bands').upsert(
                    insert_data,
                    on_conflict='symbol,risk_band_lower,risk_band_upper,market_cycle'
                ).execute()

                if response.data:
                    print(f"  ✅ Band {band_label}: {band_data['days_in_band']} days ({band_data['percentage']}%)")
                    success_count += 1

            except Exception as e:
                print(f"  ❌ Error storing band {band_label}: {e}")
                error_count += 1

        # Also store the weighted risk score as metadata
        try:
            # Store overall risk score in a summary band (optional approach)
            summary_data = {
                'symbol': symbol,
                'symbol_name': symbol_name,
                'risk_band_lower': 0.0,
                'risk_band_upper': 1.0,
                'days_in_band': coef_data['total_days'],
                'percentage_in_band': 100.0,
                'market_cycle': 'summary',  # Special cycle for summary data
                'currently_in_band': False,
                'confidence_level': coef_data['confidence_level'],
                'data_source': 'intothecryptoverse',
                'last_updated': datetime.now().isoformat()
            }

            response = supabase.table('risk_time_bands').upsert(
                summary_data,
                on_conflict='symbol,risk_band_lower,risk_band_upper,market_cycle'
            ).execute()

            print(f"  📊 Weighted Risk Score: {coef_data['weighted_risk_score']}")
            print(f"  📍 Current Band: {coef_data['current_risk_band']}")

        except Exception as e:
            print(f"  ⚠️ Could not store summary: {e}")

    print("\n" + "="*50)
    print(f"✅ Database Update Complete!")
    print(f"   • Success: {success_count} bands")
    print(f"   • Errors: {error_count} bands")

    # Query to verify data was stored
    try:
        print("\n🔍 Verifying stored data...")

        # Get count of stored records
        result = supabase.table('risk_time_bands').select('symbol', count='exact').execute()

        if result.count:
            print(f"✅ Total records in database: {result.count}")

        # Get current risk bands
        current_bands = supabase.table('risk_time_bands').select(
            'symbol', 'risk_band_label', 'days_in_band', 'percentage_in_band'
        ).eq('currently_in_band', True).limit(5).execute()

        if current_bands.data:
            print("\n📊 Sample Current Risk Bands:")
            for band in current_bands.data:
                print(f"   • {band['symbol']}: Band {band.get('risk_band_label', 'N/A')}")

    except Exception as e:
        print(f"⚠️ Could not verify data: {e}")

if __name__ == "__main__":
    main()