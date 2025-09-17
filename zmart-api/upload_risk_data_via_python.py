#!/usr/bin/env python3
"""
Upload complete risk data to Supabase via Python client
"""
import os
import re
import sys
from dotenv import load_dotenv

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase...")
    os.system("pip install supabase")
    from supabase import create_client

load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing Supabase credentials")
    exit(1)

print("🔗 Connecting to Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_sql_inserts(sql_file):
    """Parse INSERT statements from SQL file"""
    print(f"📄 Reading {sql_file}...")

    with open(sql_file, 'r') as f:
        content = f.read()

    # Find all INSERT statements
    insert_pattern = r"INSERT INTO risk_metric_grid.*?VALUES\s*(.*?)(?=ON CONFLICT|INSERT|$)"
    matches = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)

    all_records = []

    for match in matches:
        # Parse individual value rows
        value_pattern = r"\('([^']+)',\s*(\d+),\s*([\d.]+),\s*([\d.]+),\s*'([^']+)',\s*'([^']+)'\)"
        values = re.findall(value_pattern, match)

        for value in values:
            symbol, price_point, risk_value, price_usd, risk_band, risk_type = value

            record = {
                'symbol': symbol,
                'price_point': int(price_point),
                'risk_value': float(risk_value),
                'price_usd': float(price_usd),
                'risk_band': risk_band,
                'risk_type': risk_type
            }
            all_records.append(record)

    return all_records

def upload_in_batches(records, batch_size=100):
    """Upload records in batches"""
    total_batches = (len(records) + batch_size - 1) // batch_size

    print(f"📊 Uploading {len(records)} records in {total_batches} batches...")

    # Clear existing data first
    try:
        print("🧹 Clearing existing risk data...")
        result = supabase.table('risk_metric_grid').delete().neq('id', 0).execute()
        print(f"   Cleared existing records")
    except Exception as e:
        print(f"   Note: {e}")

    successful_uploads = 0
    failed_uploads = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        batch_num = i // batch_size + 1

        try:
            result = supabase.table('risk_metric_grid').insert(batch).execute()
            successful_uploads += len(batch)
            print(f"   ✅ Batch {batch_num}/{total_batches}: {len(batch)} records uploaded")
        except Exception as e:
            failed_uploads += len(batch)
            print(f"   ❌ Batch {batch_num}/{total_batches} failed: {e}")

            # Try individual records if batch fails
            for record in batch:
                try:
                    supabase.table('risk_metric_grid').insert([record]).execute()
                    successful_uploads += 1
                    failed_uploads -= 1
                except Exception as e2:
                    print(f"      ❌ Failed record {record['symbol']}: {e2}")

    return successful_uploads, failed_uploads

def verify_upload():
    """Verify the upload was successful"""
    print("\n🔍 Verifying upload...")

    try:
        # Get counts
        count_result = supabase.table('risk_metric_grid').select('*', count='exact').execute()
        total_records = count_result.count

        # Get symbols
        symbols_result = supabase.table('risk_metric_grid').select('symbol').execute()
        unique_symbols = set(row['symbol'] for row in symbols_result.data)

        # Get risk types
        risk_types_result = supabase.table('risk_metric_grid').select('risk_type').execute()
        unique_risk_types = set(row['risk_type'] for row in risk_types_result.data)

        print(f"✅ Total records: {total_records}")
        print(f"✅ Unique symbols: {len(unique_symbols)}")
        print(f"   Symbols: {', '.join(sorted(unique_symbols))}")
        print(f"✅ Risk types: {', '.join(sorted(unique_risk_types))}")

        # Check BTC range
        btc_result = supabase.table('risk_metric_grid').select('price_usd').eq('symbol', 'BTC').execute()
        if btc_result.data:
            btc_prices = [row['price_usd'] for row in btc_result.data]
            print(f"✅ BTC price range: ${min(btc_prices):,.0f} - ${max(btc_prices):,.0f}")

        return total_records, len(unique_symbols)

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return 0, 0

def main():
    sql_file = "complete_risk_import.sql"

    if not os.path.exists(sql_file):
        print(f"❌ Error: {sql_file} not found!")
        return

    # Parse the SQL file
    records = parse_sql_inserts(sql_file)

    if not records:
        print("❌ No records found in SQL file!")
        return

    print(f"📋 Parsed {len(records)} records from SQL file")

    # Upload records
    successful, failed = upload_in_batches(records)

    print(f"\n📊 Upload Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")

    # Verify upload
    total_records, total_symbols = verify_upload()

    if total_records > 2000 and total_symbols >= 20:
        print("\n🎉 Upload completed successfully!")
    else:
        print("\n⚠️  Upload may be incomplete. Please check the data.")

if __name__ == "__main__":
    main()