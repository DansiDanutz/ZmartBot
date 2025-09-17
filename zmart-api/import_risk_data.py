#!/usr/bin/env python3
"""
Import risk metric data into Supabase database
"""

import os
import glob
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_ANON_KEY not found in environment variables")
    exit(1)

supabase: Client = create_client(url, key)

def parse_sql_file(filepath):
    """Parse SQL file and extract data for insertion"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract symbol from filename
    symbol = os.path.basename(filepath).replace('_risk_data.sql', '').upper()

    # Find all INSERT statements
    import re
    pattern = r"\('([^']+)',\s*(\d+),\s*([\d.]+),\s*([\d.]+),\s*'([^']+)',\s*'([^']+)'\)"
    matches = re.findall(pattern, content)

    data = []
    for match in matches:
        data.append({
            'symbol': match[0],
            'price_point': int(match[1]),
            'risk_value': float(match[2]),
            'price_usd': float(match[3]),
            'risk_band': match[4],
            'risk_type': match[5]
        })

    return data

def main():
    # Get all SQL files
    sql_files = glob.glob('*_risk_data.sql')
    print(f"Found {len(sql_files)} SQL files to import")

    total_records = 0

    for sql_file in sql_files:
        print(f"\nProcessing {sql_file}...")

        try:
            # Parse the SQL file
            data = parse_sql_file(sql_file)

            if not data:
                print(f"  No data found in {sql_file}")
                continue

            # Insert data in batches
            batch_size = 100
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]

                # Use upsert to handle duplicates
                response = supabase.table('risk_metric_grid').upsert(
                    batch,
                    on_conflict='symbol,price_point,risk_type'
                ).execute()

                print(f"  Inserted batch {i//batch_size + 1} ({len(batch)} records)")

            total_records += len(data)
            print(f"  ✅ Successfully imported {len(data)} records from {sql_file}")

        except Exception as e:
            print(f"  ❌ Error processing {sql_file}: {str(e)}")

    print(f"\n{'='*50}")
    print(f"Total records imported: {total_records}")
    print(f"Import complete!")

if __name__ == "__main__":
    main()