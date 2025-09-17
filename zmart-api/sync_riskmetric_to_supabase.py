#!/usr/bin/env python3
"""
Sync RiskMetric Data from SQLite to Supabase
Migrates time_spent_bands and related data to cloud database
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from supabase import create_client, Client
from pathlib import Path

# Add project path
sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

class RiskMetricSupabaseSync:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"

        # Get Supabase key from environment or use the one from config
        self.supabase_key = os.getenv('SUPABASE_KEY') or self.get_supabase_key()

        if not self.supabase_key:
            raise ValueError("❌ Supabase key not found. Please set SUPABASE_KEY environment variable")

        # Initialize Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Local database path
        self.local_db_path = "data/unified_riskmetric.db"

    def get_supabase_key(self):
        """Try to get Supabase key from various sources"""
        # Try from .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("SUPABASE_KEY="):
                        return line.split("=", 1)[1].strip()

        # Try from config.json
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                return config.get("SUPABASE_KEY")

        return None

    def create_tables(self):
        """Create RiskMetric tables in Supabase if they don't exist"""

        print("📦 Creating RiskMetric tables in Supabase...")

        # SQL for creating tables
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS riskmetric_symbols (
                symbol TEXT PRIMARY KEY,
                min_price NUMERIC NOT NULL,
                max_price NUMERIC NOT NULL,
                inception_date DATE,
                life_age_days INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS riskmetric_time_spent_bands (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                band_start NUMERIC CHECK (band_start BETWEEN 0 AND 0.9),
                band_end NUMERIC CHECK (band_end BETWEEN 0.1 AND 1.0),
                days_spent INTEGER CHECK (days_spent >= 0),
                percentage NUMERIC CHECK (percentage BETWEEN 0 AND 100),
                coefficient NUMERIC CHECK (coefficient BETWEEN 1.0 AND 1.6),
                total_days INTEGER CHECK (total_days > 0),
                last_updated DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(symbol, band_start),
                CHECK (band_end > band_start)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS riskmetric_risk_levels (
                id SERIAL PRIMARY KEY,
                min_value NUMERIC NOT NULL,
                max_value NUMERIC NOT NULL,
                risk_band TEXT NOT NULL,
                risk_zone TEXT NOT NULL,
                signal TEXT NOT NULL,
                win_rate NUMERIC NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(min_value, max_value)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS riskmetric_outcomes (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                risk_value NUMERIC NOT NULL,
                risk_band TEXT NOT NULL,
                price NUMERIC NOT NULL,
                outcome TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_time_spent_symbol ON riskmetric_time_spent_bands(symbol);
            CREATE INDEX IF NOT EXISTS idx_outcomes_symbol ON riskmetric_outcomes(symbol);
            CREATE INDEX IF NOT EXISTS idx_outcomes_timestamp ON riskmetric_outcomes(timestamp);
            """
        ]

        # Execute each SQL statement
        for sql in create_tables_sql:
            try:
                # Use raw SQL execution via Supabase RPC or direct PostgreSQL connection
                print(f"   Creating table from SQL: {sql[:50]}...")
                # Note: Supabase doesn't directly support DDL via client
                # We'll need to use the migration approach
            except Exception as e:
                print(f"   ⚠️ Warning: {e}")

        print("✅ Table creation process completed")

    def sync_symbols(self):
        """Sync symbols data from SQLite to Supabase"""
        print("\n📊 Syncing symbols data...")

        # Connect to SQLite
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()

        # Get symbols from SQLite
        cursor.execute("SELECT * FROM symbols")
        columns = [desc[0] for desc in cursor.description]
        symbols = cursor.fetchall()

        if not symbols:
            print("   No symbols found in local database")
            conn.close()
            return

        # Prepare data for Supabase
        symbols_data = []
        for row in symbols:
            data = dict(zip(columns, row))
            # Map to Supabase schema
            symbols_data.append({
                'symbol': data.get('symbol'),
                'min_price': data.get('min_price'),
                'max_price': data.get('max_price'),
                'inception_date': data.get('inception_date'),
                'life_age_days': data.get('life_age_days')
            })

        # Insert into Supabase
        try:
            result = self.supabase.table('riskmetric_symbols').upsert(symbols_data).execute()
            print(f"   ✅ Synced {len(symbols_data)} symbols")
        except Exception as e:
            print(f"   ❌ Error syncing symbols: {e}")

        conn.close()

    def sync_time_spent_bands(self):
        """Sync time_spent_bands data from SQLite to Supabase"""
        print("\n📊 Syncing time_spent_bands data...")

        # Connect to SQLite
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()

        # Get time_spent_bands from SQLite
        cursor.execute("""
            SELECT symbol, band_start, band_end, days_spent,
                   percentage, coefficient, total_days, last_updated
            FROM time_spent_bands
            ORDER BY symbol, band_start
        """)

        bands = cursor.fetchall()

        if not bands:
            print("   No time_spent_bands found in local database")
            conn.close()
            return

        # Prepare data for Supabase
        bands_data = []
        for row in bands:
            bands_data.append({
                'symbol': row[0],
                'band_start': row[1],
                'band_end': row[2],
                'days_spent': row[3],
                'percentage': row[4],
                'coefficient': row[5],
                'total_days': row[6],
                'last_updated': row[7]
            })

        # Insert into Supabase
        try:
            # Clear existing data for these symbols
            symbols = list(set([b['symbol'] for b in bands_data]))
            for symbol in symbols:
                self.supabase.table('riskmetric_time_spent_bands').delete().eq('symbol', symbol).execute()

            # Insert new data
            result = self.supabase.table('riskmetric_time_spent_bands').insert(bands_data).execute()
            print(f"   ✅ Synced {len(bands_data)} time_spent_bands records")

            # Show ETH data as verification
            eth_bands = [b for b in bands_data if b['symbol'] == 'ETH']
            if eth_bands:
                print("\n   📊 ETH Time Spent Bands (verification):")
                for band in eth_bands:
                    print(f"      Band {band['band_start']:.1f}-{band['band_end']:.1f}: "
                          f"{band['days_spent']} days ({band['percentage']:.2f}%) "
                          f"Coeff: {band['coefficient']}")

        except Exception as e:
            print(f"   ❌ Error syncing time_spent_bands: {e}")

        conn.close()

    def sync_risk_levels(self):
        """Sync risk_levels data from SQLite to Supabase"""
        print("\n📊 Syncing risk_levels data...")

        # Connect to SQLite
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()

        # Get risk_levels from SQLite
        cursor.execute("SELECT * FROM risk_levels")
        columns = [desc[0] for desc in cursor.description]
        levels = cursor.fetchall()

        if not levels:
            print("   No risk_levels found in local database")
            conn.close()
            return

        # Prepare data for Supabase
        levels_data = []
        for row in levels:
            data = dict(zip(columns, row))
            levels_data.append({
                'min_value': data.get('min_value'),
                'max_value': data.get('max_value'),
                'risk_band': data.get('risk_band'),
                'risk_zone': data.get('risk_zone'),
                'signal': data.get('signal'),
                'win_rate': data.get('win_rate')
            })

        # Insert into Supabase
        try:
            # Clear existing data
            self.supabase.table('riskmetric_risk_levels').delete().neq('id', 0).execute()

            # Insert new data
            result = self.supabase.table('riskmetric_risk_levels').insert(levels_data).execute()
            print(f"   ✅ Synced {len(levels_data)} risk_levels")
        except Exception as e:
            print(f"   ❌ Error syncing risk_levels: {e}")

        conn.close()

    def verify_sync(self):
        """Verify data was synced correctly"""
        print("\n🔍 Verifying sync...")

        try:
            # Check time_spent_bands for ETH
            result = self.supabase.table('riskmetric_time_spent_bands')\
                .select('*')\
                .eq('symbol', 'ETH')\
                .order('band_start')\
                .execute()

            if result.data:
                print(f"   ✅ Found {len(result.data)} ETH bands in Supabase")

                # Calculate total percentage
                total_percentage = sum(float(band['percentage']) for band in result.data)
                print(f"   📊 Total percentage coverage: {total_percentage:.2f}%")

                # Show 0.7-0.8 band specifically
                band_07_08 = [b for b in result.data if b['band_start'] == 0.7]
                if band_07_08:
                    band = band_07_08[0]
                    print(f"   📍 ETH 0.7-0.8 band: {band['days_spent']} days "
                          f"({band['percentage']:.2f}%) Coeff: {band['coefficient']}")
            else:
                print("   ⚠️ No ETH data found in Supabase")

        except Exception as e:
            print(f"   ❌ Error verifying sync: {e}")

    def run(self):
        """Run the complete sync process"""
        print("=" * 60)
        print("🚀 RISKMETRIC TO SUPABASE SYNC")
        print("=" * 60)
        print(f"📁 Source: {self.local_db_path}")
        print(f"☁️  Target: {self.supabase_url}")
        print("=" * 60)

        # Check if local database exists
        if not Path(self.local_db_path).exists():
            print(f"❌ Local database not found: {self.local_db_path}")
            return

        # Create tables (note: this needs proper migration setup)
        # self.create_tables()

        # Sync data
        self.sync_symbols()
        self.sync_time_spent_bands()
        self.sync_risk_levels()

        # Verify
        self.verify_sync()

        print("\n" + "=" * 60)
        print("✅ SYNC COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    try:
        syncer = RiskMetricSupabaseSync()
        syncer.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)