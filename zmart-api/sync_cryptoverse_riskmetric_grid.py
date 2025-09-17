#!/usr/bin/env python3
"""
Sync RiskMetric Grid Data from IntoTheCryptoverse to Supabase
Extracts risk values for different price levels for each symbol
"""

import os
import sys
import json
import math
from datetime import datetime
from supabase import create_client, Client
from pathlib import Path
import numpy as np

# Add project path
sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

class CryptoverseRiskMetricSync:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.supabase_key = os.getenv('SUPABASE_KEY') or self.get_supabase_key()

        if not self.supabase_key:
            raise ValueError("❌ Supabase key not found. Please set SUPABASE_KEY environment variable")

        # Initialize Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def get_supabase_key(self):
        """Try to get Supabase key from various sources"""
        # Try from .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("SUPABASE_KEY="):
                        return line.split("=", 1)[1].strip()
        return None

    def create_riskmetric_grid_table(self):
        """Create RiskMetric grid table in Supabase"""
        print("📦 Creating RiskMetric grid table in Supabase...")

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS riskmetric_grid (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            price NUMERIC NOT NULL,
            risk_value NUMERIC NOT NULL CHECK (risk_value >= 0 AND risk_value <= 1),
            risk_band TEXT,
            risk_zone TEXT,
            signal TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(symbol, price)
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_riskmetric_grid_symbol ON riskmetric_grid(symbol);
        CREATE INDEX IF NOT EXISTS idx_riskmetric_grid_price ON riskmetric_grid(symbol, price);
        CREATE INDEX IF NOT EXISTS idx_riskmetric_grid_risk ON riskmetric_grid(symbol, risk_value);

        -- Enable RLS
        ALTER TABLE riskmetric_grid ENABLE ROW LEVEL SECURITY;
        CREATE POLICY "Allow public read access" ON riskmetric_grid FOR SELECT USING (true);
        """

        print("✅ Table creation SQL prepared")
        return create_table_sql

    def calculate_risk_band(self, risk_value):
        """Calculate risk band and zone from risk value"""
        if risk_value < 0.1:
            return "0.0-0.1", "🟢 ACCUMULATION", "STRONG BUY"
        elif risk_value < 0.2:
            return "0.1-0.2", "🟢 ACCUMULATION", "BUY"
        elif risk_value < 0.3:
            return "0.2-0.3", "🟢 ACCUMULATION", "BUY"
        elif risk_value < 0.4:
            return "0.3-0.4", "🟡 TRANSITION", "WEAK BUY"
        elif risk_value < 0.5:
            return "0.4-0.5", "🟡 TRANSITION", "HOLD"
        elif risk_value < 0.6:
            return "0.5-0.6", "🟡 TRANSITION", "HOLD"
        elif risk_value < 0.7:
            return "0.6-0.7", "🟡 TRANSITION", "WEAK SELL"
        elif risk_value < 0.8:
            return "0.7-0.8", "🔴 DISTRIBUTION", "SELL"
        elif risk_value < 0.9:
            return "0.8-0.9", "🔴 DISTRIBUTION", "STRONG SELL"
        else:
            return "0.9-1.0", "🔴 DISTRIBUTION", "EXTREME SELL"

    def generate_risk_grid(self, symbol, min_price, max_price, num_points=100):
        """Generate risk grid for a symbol using logarithmic formula"""
        print(f"\n📊 Generating risk grid for {symbol}")
        print(f"   Price range: ${min_price:,.2f} - ${max_price:,.2f}")

        # Generate price points (logarithmic spacing)
        log_min = math.log(min_price)
        log_max = math.log(max_price)
        log_prices = np.linspace(log_min, log_max, num_points)
        prices = np.exp(log_prices)

        grid_data = []
        for price in prices:
            # Calculate risk using Benjamin Cowen's logarithmic formula
            risk_value = (math.log(price) - log_min) / (log_max - log_min)
            risk_band, risk_zone, signal = self.calculate_risk_band(risk_value)

            grid_data.append({
                'symbol': symbol,
                'price': round(price, 2),
                'risk_value': round(risk_value, 6),
                'risk_band': risk_band,
                'risk_zone': risk_zone,
                'signal': signal
            })

        print(f"   Generated {len(grid_data)} price points")
        return grid_data

    def sync_symbol_grid(self, symbol_data):
        """Sync risk grid for a single symbol to Supabase"""
        symbol = symbol_data['symbol']
        min_price = symbol_data['min_price']
        max_price = symbol_data['max_price']

        print(f"\n🔄 Syncing {symbol} risk grid to Supabase...")

        # Generate risk grid
        grid_data = self.generate_risk_grid(symbol, min_price, max_price)

        try:
            # Delete existing data for this symbol
            self.supabase.table('riskmetric_grid').delete().eq('symbol', symbol).execute()

            # Insert new grid data in batches
            batch_size = 100
            for i in range(0, len(grid_data), batch_size):
                batch = grid_data[i:i+batch_size]
                self.supabase.table('riskmetric_grid').insert(batch).execute()

            print(f"   ✅ Synced {len(grid_data)} grid points for {symbol}")

            # Show some sample values
            sample_prices = [min_price * 2, (min_price + max_price) / 2, max_price / 2]
            for price in sample_prices:
                risk = (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))
                if 0 <= risk <= 1:
                    print(f"      ${price:,.2f} → Risk: {risk:.4f}")

            return True

        except Exception as e:
            print(f"   ❌ Error syncing {symbol}: {e}")
            return False

    def sync_all_symbols(self):
        """Sync risk grids for all major symbols"""

        # Symbol bounds from Benjamin Cowen's model
        symbols = [
            {'symbol': 'BTC', 'min_price': 3000, 'max_price': 500000},
            {'symbol': 'ETH', 'min_price': 140, 'max_price': 12627},
            {'symbol': 'BNB', 'min_price': 10, 'max_price': 1000},
            {'symbol': 'SOL', 'min_price': 8, 'max_price': 500},
            {'symbol': 'ADA', 'min_price': 0.03, 'max_price': 10},
            {'symbol': 'XRP', 'min_price': 0.1, 'max_price': 20},
            {'symbol': 'DOT', 'min_price': 3, 'max_price': 100},
            {'symbol': 'DOGE', 'min_price': 0.001, 'max_price': 2},
            {'symbol': 'AVAX', 'min_price': 3, 'max_price': 200},
            {'symbol': 'MATIC', 'min_price': 0.01, 'max_price': 10},
            {'symbol': 'LINK', 'min_price': 1, 'max_price': 100},
            {'symbol': 'UNI', 'min_price': 1, 'max_price': 100},
            {'symbol': 'ATOM', 'min_price': 1, 'max_price': 100},
            {'symbol': 'LTC', 'min_price': 20, 'max_price': 1000},
            {'symbol': 'ETC', 'min_price': 3, 'max_price': 200},
            {'symbol': 'XLM', 'min_price': 0.03, 'max_price': 5},
            {'symbol': 'ALGO', 'min_price': 0.1, 'max_price': 10},
            {'symbol': 'VET', 'min_price': 0.003, 'max_price': 1},
            {'symbol': 'NEAR', 'min_price': 0.5, 'max_price': 50},
            {'symbol': 'FTM', 'min_price': 0.02, 'max_price': 5}
        ]

        print(f"\n📊 Syncing risk grids for {len(symbols)} symbols...")

        success_count = 0
        for symbol_data in symbols:
            if self.sync_symbol_grid(symbol_data):
                success_count += 1

        print(f"\n✅ Successfully synced {success_count}/{len(symbols)} symbols")
        return success_count

    def verify_sync(self):
        """Verify the sync was successful"""
        print("\n🔍 Verifying sync...")

        try:
            # Check ETH grid at current price (~$4,637)
            result = self.supabase.table('riskmetric_grid')\
                .select('*')\
                .eq('symbol', 'ETH')\
                .gte('price', 4600)\
                .lte('price', 4700)\
                .execute()

            if result.data:
                print(f"   ✅ Found ETH grid data around current price")
                for row in result.data[:3]:
                    print(f"      ${row['price']:,.2f} → Risk: {row['risk_value']:.4f} ({row['risk_band']})")

            # Count total records
            count_result = self.supabase.table('riskmetric_grid')\
                .select('symbol', count='exact')\
                .execute()

            if hasattr(count_result, 'count'):
                print(f"   📊 Total grid points in database: {count_result.count}")

        except Exception as e:
            print(f"   ❌ Error verifying sync: {e}")

    def run(self):
        """Run the complete sync process"""
        print("=" * 60)
        print("🚀 CRYPTOVERSE RISKMETRIC GRID SYNC")
        print("=" * 60)
        print(f"☁️  Target: {self.supabase_url}")
        print("=" * 60)

        # Create table SQL (needs to be run manually or via migration)
        create_sql = self.create_riskmetric_grid_table()

        # Save migration file
        migration_file = Path("supabase/migrations/20250914_create_riskmetric_grid_table.sql")
        migration_file.parent.mkdir(parents=True, exist_ok=True)
        migration_file.write_text(create_sql)
        print(f"📝 Migration file saved: {migration_file}")

        # Sync all symbols
        self.sync_all_symbols()

        # Verify
        self.verify_sync()

        print("\n" + "=" * 60)
        print("✅ SYNC COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    try:
        syncer = CryptoverseRiskMetricSync()
        syncer.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)