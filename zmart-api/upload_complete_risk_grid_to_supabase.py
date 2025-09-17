#!/usr/bin/env python3
"""
Upload complete risk grid data (all symbols with 41 risk values) to Supabase
"""
import os
import json
import sys
from dotenv import load_dotenv

# Add the current directory to the path to import supabase
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase...")
    os.system("pip install supabase")
    from supabase import create_client

load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing Supabase credentials in .env file")
    print("Required: SUPABASE_URL and SUPABASE_ANON_KEY")
    exit(1)

print("🔗 Connecting to Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_complete_risk_grid():
    """Upload complete risk grid with all symbols and 41 risk values to Supabase"""

    risk_grid_file = "cryptoverse_manual_risk_grid.json"

    if not os.path.exists(risk_grid_file):
        print(f"❌ Error: {risk_grid_file} not found!")
        return

    print(f"📄 Loading {risk_grid_file}...")

    with open(risk_grid_file, 'r') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    symbols_data = data.get('symbols', {})

    print(f"📊 Found data for {len(symbols_data)} symbols")
    print(f"📈 Risk levels: {metadata.get('total_levels', 41)} levels from 0.0 to 1.0")

    # Prepare records for cryptoverse_risk_grid table
    all_records = []
    summary_records = []

    for symbol, symbol_data in symbols_data.items():
        print(f"🔄 Processing {symbol}...")

        # Get fiat risk grid
        fiat_grid = symbol_data.get('fiat_risk_grid', [])
        btc_grid = symbol_data.get('btc_risk_grid', [])
        eth_grid = symbol_data.get('eth_risk_grid', [])

        # Create lookup dictionaries for BTC and ETH grids
        btc_lookup = {item['risk_value']: item['price'] for item in btc_grid} if btc_grid else {}
        eth_lookup = {item['risk_value']: item['price'] for item in eth_grid} if eth_grid else {}

        # Process each fiat risk point
        for item in fiat_grid:
            risk_value = item['risk_value']
            price_usd = item['price']

            # Get corresponding BTC and ETH prices
            price_btc = btc_lookup.get(risk_value)
            price_eth = eth_lookup.get(risk_value)

            record = {
                'symbol': symbol,
                'price_usd': price_usd,
                'fiat_risk': risk_value
            }

            # Add BTC risk if available
            if price_btc is not None:
                record['price_btc'] = price_btc
                record['btc_risk'] = risk_value

            # Add ETH risk if available
            if price_eth is not None:
                record['price_eth'] = price_eth
                record['eth_risk'] = risk_value

            all_records.append(record)

        # Create summary record
        min_price = min(item['price'] for item in fiat_grid) if fiat_grid else None
        max_price = max(item['price'] for item in fiat_grid) if fiat_grid else None

        summary_record = {
            'symbol': symbol,
            'total_fiat_points': len(fiat_grid),
            'total_btc_points': len(btc_grid),
            'total_eth_points': len(eth_grid),
            'min_price_usd': min_price,
            'max_price_usd': max_price
        }

        if btc_grid:
            summary_record['min_price_btc'] = min(item['price'] for item in btc_grid)
            summary_record['max_price_btc'] = max(item['price'] for item in btc_grid)

        if eth_grid:
            summary_record['min_price_eth'] = min(item['price'] for item in eth_grid)
            summary_record['max_price_eth'] = max(item['price'] for item in eth_grid)

        summary_records.append(summary_record)

    print(f"\n📋 Prepared {len(all_records)} total risk grid records")
    print(f"📋 Prepared {len(summary_records)} summary records")

    # Clear existing data
    try:
        print("🧹 Clearing existing risk grid data...")
        result = supabase.table('cryptoverse_risk_grid').delete().neq('id', 0).execute()
        print(f"   Cleared existing records")

        result = supabase.table('cryptoverse_grid_summary').delete().neq('id', 0).execute()
        print(f"   Cleared existing summary records")
    except Exception as e:
        print(f"   Note: {e}")

    # Upload main risk grid data in batches
    print("\n⬆️  Uploading risk grid data...")
    batch_size = 100
    total_batches = (len(all_records) + batch_size - 1) // batch_size

    for i in range(0, len(all_records), batch_size):
        batch = all_records[i:i+batch_size]
        batch_num = i // batch_size + 1

        try:
            result = supabase.table('cryptoverse_risk_grid').insert(batch).execute()
            print(f"   ✅ Batch {batch_num}/{total_batches}: {len(batch)} records uploaded")
        except Exception as e:
            print(f"   ❌ Error in batch {batch_num}: {e}")
            continue

    # Upload summary data
    print("\n⬆️  Uploading summary data...")
    try:
        result = supabase.table('cryptoverse_grid_summary').insert(summary_records).execute()
        print(f"   ✅ {len(summary_records)} summary records uploaded")
    except Exception as e:
        print(f"   ❌ Error uploading summary: {e}")

    # Verify upload
    print("\n🔍 Verifying upload...")
    try:
        count_result = supabase.table('cryptoverse_risk_grid').select('symbol', count='exact').execute()
        summary_count = supabase.table('cryptoverse_grid_summary').select('symbol', count='exact').execute()

        print(f"✅ Total records in cryptoverse_risk_grid: {count_result.count}")
        print(f"✅ Total symbols in cryptoverse_grid_summary: {summary_count.count}")

        # Show symbols breakdown
        symbols_count = supabase.table('cryptoverse_risk_grid').select('symbol').execute()
        unique_symbols = set(row['symbol'] for row in symbols_count.data)
        print(f"✅ Unique symbols uploaded: {len(unique_symbols)}")
        print(f"   Symbols: {', '.join(sorted(unique_symbols))}")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

    print("\n🎉 Upload complete!")

if __name__ == "__main__":
    upload_complete_risk_grid()