#!/usr/bin/env python3
"""
Sync all extracted risk grid data to Supabase
"""
import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing Supabase credentials in .env file")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_risk_grids():
    """Sync all risk grid JSON files to Supabase"""

    # Get all JSON files
    risk_grid_dir = "extracted_risk_grids"
    json_files = [f for f in os.listdir(risk_grid_dir) if f.endswith('.json')]

    print(f"Found {len(json_files)} risk grid files to sync")

    for json_file in json_files:
        file_path = os.path.join(risk_grid_dir, json_file)
        print(f"\nProcessing {json_file}...")

        with open(file_path, 'r') as f:
            data = json.load(f)

        symbol = data['symbol']
        current_price = data['current_price']
        current_risk = data['current_risk']
        last_updated = data['last_updated']

        # Prepare records for cryptoverse_risk_grid table
        records = []

        # Add fiat risk grid
        for point in data.get('fiat_risk_grid', []):
            records.append({
                'symbol': symbol,
                'price_usd': point['price'],
                'fiat_risk': point['risk'],
                'btc_risk': None,
                'eth_risk': None,
                'last_updated': last_updated
            })

        # Update with BTC risk where available
        btc_grid = {p['risk']: p['price_btc'] for p in data.get('btc_risk_grid', [])}
        for record in records:
            risk_val = record['fiat_risk']
            if risk_val in btc_grid:
                record['btc_risk'] = btc_grid[risk_val]

        # Update with ETH risk where available
        eth_grid = {p['risk']: p['price_eth'] for p in data.get('eth_risk_grid', [])}
        for record in records:
            risk_val = record['fiat_risk']
            if risk_val in eth_grid:
                record['eth_risk'] = eth_grid[risk_val]

        # Delete existing records for this symbol
        try:
            result = supabase.table('cryptoverse_risk_grid').delete().eq('symbol', symbol).execute()
            print(f"  Deleted {len(result.data) if result.data else 0} existing records for {symbol}")
        except Exception as e:
            print(f"  Note: No existing records to delete for {symbol}")

        # Insert new records in batches
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                result = supabase.table('cryptoverse_risk_grid').insert(batch).execute()
                print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} records")
            except Exception as e:
                print(f"  Error inserting batch for {symbol}: {e}")

        # Update current values in cryptoverse_risk_current table
        current_data = {
            'symbol': symbol,
            'current_price': current_price,
            'current_risk': current_risk,
            'last_updated': last_updated
        }

        try:
            # Try to update first
            result = supabase.table('cryptoverse_risk_current').update(current_data).eq('symbol', symbol).execute()
            if not result.data:
                # If no record exists, insert
                result = supabase.table('cryptoverse_risk_current').insert(current_data).execute()
                print(f"  Inserted current values for {symbol}")
            else:
                print(f"  Updated current values for {symbol}")
        except Exception as e:
            print(f"  Error updating current values for {symbol}: {e}")

    print("\n✅ Sync complete!")

    # Show summary
    try:
        count_result = supabase.table('cryptoverse_risk_grid').select('symbol', count='exact').execute()
        current_count = supabase.table('cryptoverse_risk_current').select('symbol', count='exact').execute()
        print(f"\nTotal records in cryptoverse_risk_grid: {count_result.count}")
        print(f"Total symbols in cryptoverse_risk_current: {current_count.count}")
    except Exception as e:
        print(f"Could not get counts: {e}")

if __name__ == "__main__":
    sync_risk_grids()