#!/usr/bin/env python3
"""
Sync Complete IntoTheCryptoverse Risk Data to Supabase
Syncs both Fiat Risk and BTC Risk values
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CryptoverseCompleteSync:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.data_file = Path(__file__).parent / 'cryptoverse_complete_risk_data.json'

    def load_risk_data(self) -> Dict[str, Any]:
        """Load risk data from JSON file"""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Risk data file not found: {self.data_file}")

        with open(self.data_file, 'r') as f:
            return json.load(f)

    def sync_fiat_risks(self, risk_data: Dict[str, Any]) -> None:
        """Sync Fiat Risk values to Supabase"""
        print("\n📊 Syncing Fiat Risk values...")

        symbols_data = risk_data.get('risk_data', {})

        # Prepare data for insertion
        fiat_risks = []
        for symbol, data in symbols_data.items():
            fiat_risks.append({
                'symbol': symbol,
                'current_price': data.get('price_usd'),
                'risk_value': data.get('fiat_risk'),
                'market_cap_rank': None  # Will be updated based on order
            })

        # Sort by fiat_risk to assign market cap ranks
        fiat_risks.sort(key=lambda x: x['risk_value'])
        for i, item in enumerate(fiat_risks, 1):
            item['market_cap_rank'] = i

        # Upsert to Supabase
        try:
            response = self.supabase.table('cryptoverse_fiat_risks').upsert(
                fiat_risks,
                on_conflict='symbol'
            ).execute()
            print(f"✅ Synced {len(fiat_risks)} Fiat Risk values")
        except Exception as e:
            print(f"❌ Error syncing Fiat Risks: {e}")

    def sync_btc_risks(self, risk_data: Dict[str, Any]) -> None:
        """Sync BTC Risk values to Supabase"""
        print("\n📊 Syncing BTC Risk values...")

        symbols_data = risk_data.get('risk_data', {})

        # Prepare data for insertion
        btc_risks = []
        for symbol, data in symbols_data.items():
            btc_risks.append({
                'symbol': symbol,
                'current_price_btc': data.get('price_btc'),
                'risk_value': data.get('btc_risk'),
                'btc_price': risk_data.get('metadata', {}).get('btc_price', 115844.88)
            })

        # Upsert to Supabase
        try:
            response = self.supabase.table('cryptoverse_btc_risks').upsert(
                btc_risks,
                on_conflict='symbol'
            ).execute()
            print(f"✅ Synced {len(btc_risks)} BTC Risk values")
        except Exception as e:
            print(f"❌ Error syncing BTC Risks: {e}")

    def sync_combined_risks(self, risk_data: Dict[str, Any]) -> None:
        """Sync combined risk data to unified table"""
        print("\n📊 Syncing combined risk data...")

        symbols_data = risk_data.get('risk_data', {})
        btc_price = risk_data.get('metadata', {}).get('btc_price', 115844.88)

        # Prepare combined data
        combined_risks = []
        for symbol, data in symbols_data.items():
            combined_risks.append({
                'symbol': symbol,
                'price_usd': data.get('price_usd'),
                'price_btc': data.get('price_btc'),
                'fiat_risk': data.get('fiat_risk'),
                'btc_risk': data.get('btc_risk'),
                'btc_reference_price': btc_price,
                'data_source': 'IntoTheCryptoverse',
                'last_updated': datetime.utcnow().isoformat()
            })

        # Upsert to Supabase
        try:
            response = self.supabase.table('cryptoverse_risk_data').upsert(
                combined_risks,
                on_conflict='symbol'
            ).execute()
            print(f"✅ Synced {len(combined_risks)} combined risk records")
        except Exception as e:
            print(f"❌ Error syncing combined risks: {e}")

    def create_tables_if_needed(self) -> None:
        """Create tables if they don't exist (run migrations)"""
        print("\n🔧 Checking tables...")

        # Check if tables exist
        try:
            # Try to query each table
            self.supabase.table('cryptoverse_fiat_risks').select('symbol').limit(1).execute()
            print("✅ cryptoverse_fiat_risks table exists")
        except:
            print("⚠️ cryptoverse_fiat_risks table doesn't exist - please run migration")

        try:
            self.supabase.table('cryptoverse_btc_risks').select('symbol').limit(1).execute()
            print("✅ cryptoverse_btc_risks table exists")
        except:
            print("⚠️ cryptoverse_btc_risks table doesn't exist - please run migration")

        try:
            self.supabase.table('cryptoverse_risk_data').select('symbol').limit(1).execute()
            print("✅ cryptoverse_risk_data table exists")
        except:
            print("⚠️ cryptoverse_risk_data table doesn't exist - please run migration")

    def display_summary(self, risk_data: Dict[str, Any]) -> None:
        """Display summary of risk data"""
        print("\n" + "="*60)
        print("📊 RISK DATA SUMMARY")
        print("="*60)

        symbols_data = risk_data.get('risk_data', {})

        # Group by risk zones
        accumulation = []  # < 0.3
        transition = []    # 0.3 - 0.7
        distribution = []  # > 0.7

        for symbol, data in symbols_data.items():
            fiat_risk = data.get('fiat_risk', 0)
            entry = f"{symbol}: {fiat_risk:.3f}"

            if fiat_risk < 0.3:
                accumulation.append(entry)
            elif fiat_risk < 0.7:
                transition.append(entry)
            else:
                distribution.append(entry)

        print("\n🟢 ACCUMULATION ZONE (< 0.3):")
        if accumulation:
            for item in sorted(accumulation):
                print(f"  {item}")
        else:
            print("  No symbols in accumulation zone")

        print("\n🟡 TRANSITION ZONE (0.3 - 0.7):")
        if transition:
            for item in sorted(transition):
                print(f"  {item}")
        else:
            print("  No symbols in transition zone")

        print("\n🔴 DISTRIBUTION ZONE (> 0.7):")
        if distribution:
            for item in sorted(distribution):
                print(f"  {item}")
        else:
            print("  No symbols in distribution zone")

        # Show BTC risk correlation
        print("\n📈 BTC RISK CORRELATION:")
        btc_correlated = [(s, d['btc_risk']) for s, d in symbols_data.items() if s != 'BTC']
        btc_correlated.sort(key=lambda x: x[1], reverse=True)

        print("  Highest BTC correlation:")
        for symbol, btc_risk in btc_correlated[:3]:
            print(f"    {symbol}: {btc_risk:.3f}")

        print("  Lowest BTC correlation:")
        for symbol, btc_risk in btc_correlated[-3:]:
            print(f"    {symbol}: {btc_risk:.3f}")

    def run(self):
        """Main sync process"""
        print("🚀 Starting IntoTheCryptoverse Complete Risk Data Sync")
        print(f"📁 Loading data from: {self.data_file}")

        try:
            # Load risk data
            risk_data = self.load_risk_data()

            # Check tables
            self.create_tables_if_needed()

            # Display summary
            self.display_summary(risk_data)

            # Sync to Supabase
            self.sync_fiat_risks(risk_data)
            self.sync_btc_risks(risk_data)
            self.sync_combined_risks(risk_data)

            print("\n✅ Sync complete!")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1

        return 0

if __name__ == "__main__":
    syncer = CryptoverseCompleteSync()
    exit(syncer.run())