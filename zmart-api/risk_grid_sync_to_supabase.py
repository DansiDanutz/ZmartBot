#!/usr/bin/env python3
"""
Sync Risk Grids to Supabase
Synchronizes extracted risk grid data with Supabase database
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskGridSync:
    """Sync risk grid data to Supabase"""

    def __init__(self):
        # Initialize Supabase client
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

        self.risk_grids_dir = Path("extracted_risk_grids")
        self.sync_log_dir = Path("sync_logs")
        self.sync_log_dir.mkdir(exist_ok=True)

    def load_risk_grid(self, symbol: str) -> Optional[Dict]:
        """Load risk grid data for a symbol"""
        try:
            file_path = self.risk_grids_dir / f"{symbol}_risk_grid.json"

            if not file_path.exists():
                logger.warning(f"Risk grid file not found for {symbol}")
                return None

            with open(file_path, 'r') as f:
                data = json.load(f)

            return data

        except Exception as e:
            logger.error(f"Error loading risk grid for {symbol}: {e}")
            return None

    async def sync_symbol_grid(self, symbol: str) -> Tuple[bool, str]:
        """Sync a single symbol's risk grid to Supabase"""
        try:
            logger.info(f"Syncing {symbol} to Supabase...")

            # Load risk grid data
            risk_data = self.load_risk_grid(symbol)

            if not risk_data:
                return False, f"Failed to load risk grid for {symbol}"

            # Prepare data for Supabase
            fiat_grid = risk_data.get("fiat_risk_grid", [])
            btc_grid = risk_data.get("btc_risk_grid", [])
            eth_grid = risk_data.get("eth_risk_grid", [])

            if len(fiat_grid) != 41:
                return False, f"Incomplete fiat grid for {symbol}: {len(fiat_grid)} points"

            # Step 1: Delete existing grid data for this symbol
            logger.info(f"Clearing existing data for {symbol}...")

            delete_response = self.client.table("cryptoverse_risk_grid").delete().eq("symbol", symbol).execute()

            # Step 2: Prepare new grid records
            grid_records = []

            for i in range(41):
                risk_value = round(i * 0.025, 3)

                # Get prices at this risk level
                fiat_point = next((p for p in fiat_grid if p["risk"] == risk_value), None)
                btc_point = next((p for p in btc_grid if p.get("risk") == risk_value), None) if btc_grid else None
                eth_point = next((p for p in eth_grid if p.get("risk") == risk_value), None) if eth_grid else None

                if not fiat_point:
                    logger.warning(f"Missing fiat price for {symbol} at risk {risk_value}")
                    continue

                record = {
                    "symbol": symbol,
                    "risk_value": risk_value,
                    "fiat_price": fiat_point["price"],
                    "btc_price": btc_point["price_btc"] if btc_point else None,
                    "eth_price": eth_point["price_eth"] if eth_point else None,
                    "last_updated": datetime.now().isoformat(),
                    "source": "IntoTheCryptoverse",
                    "extraction_method": "MCP_BROWSER"
                }

                grid_records.append(record)

            # Step 3: Insert new grid data
            if grid_records:
                logger.info(f"Inserting {len(grid_records)} records for {symbol}...")

                insert_response = self.client.table("cryptoverse_risk_grid").insert(grid_records).execute()

                if insert_response.data:
                    logger.info(f"✅ Successfully synced {symbol} ({len(grid_records)} points)")
                    return True, f"Synced {len(grid_records)} points"
                else:
                    logger.error(f"Failed to insert data for {symbol}")
                    return False, "Insert failed"
            else:
                return False, "No valid grid records to insert"

        except Exception as e:
            logger.error(f"Error syncing {symbol}: {e}")
            return False, str(e)

    async def update_current_values(self, symbol: str) -> bool:
        """Update current price and risk values in Supabase"""
        try:
            risk_data = self.load_risk_grid(symbol)

            if not risk_data:
                return False

            current_price = risk_data.get("current_price", 0)
            current_risk = risk_data.get("current_risk", 0)

            if current_price and current_risk:
                # Update cryptoverse_risk_data table
                update_data = {
                    "symbol": symbol,
                    "current_price": current_price,
                    "current_risk": current_risk,
                    "last_updated": datetime.now().isoformat()
                }

                response = self.client.table("cryptoverse_risk_data").upsert(
                    update_data,
                    on_conflict="symbol"
                ).execute()

                if response.data:
                    logger.info(f"Updated current values for {symbol}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error updating current values for {symbol}: {e}")
            return False

    async def sync_all_grids(self) -> bool:
        """Sync all available risk grids to Supabase"""
        try:
            logger.info("\n" + "="*60)
            logger.info("STARTING SUPABASE SYNCHRONIZATION")
            logger.info("="*60)

            # Get all available risk grid files
            grid_files = list(self.risk_grids_dir.glob("*_risk_grid.json"))

            if not grid_files:
                logger.error("No risk grid files found")
                return False

            logger.info(f"Found {len(grid_files)} risk grid files to sync")

            # Track results
            results = {
                "successful": [],
                "failed": [],
                "errors": {}
            }

            # Sync each symbol
            for grid_file in grid_files:
                symbol = grid_file.stem.replace("_risk_grid", "")

                success, message = await self.sync_symbol_grid(symbol)

                if success:
                    results["successful"].append(symbol)

                    # Also update current values
                    await self.update_current_values(symbol)
                else:
                    results["failed"].append(symbol)
                    results["errors"][symbol] = message

            # Generate summary
            total = len(grid_files)
            successful = len(results["successful"])
            failed = len(results["failed"])
            success_rate = (successful / total * 100) if total > 0 else 0

            logger.info("\n" + "="*60)
            logger.info("SYNCHRONIZATION COMPLETE")
            logger.info(f"Success Rate: {success_rate:.1f}%")
            logger.info(f"Successful: {successful}/{total}")
            logger.info(f"Failed: {results['failed']}")

            # Save sync report
            self.save_sync_report(results, success_rate)

            return success_rate >= 90  # Consider successful if 90% or more synced

        except Exception as e:
            logger.error(f"Error in sync_all_grids: {e}")
            return False

    def save_sync_report(self, results: Dict, success_rate: float):
        """Save synchronization report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "success_rate": f"{success_rate:.1f}%",
                "successful_symbols": results["successful"],
                "failed_symbols": results["failed"],
                "errors": results["errors"],
                "total_successful": len(results["successful"]),
                "total_failed": len(results["failed"])
            }

            report_file = self.sync_log_dir / f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Sync report saved to {report_file}")

        except Exception as e:
            logger.error(f"Error saving sync report: {e}")

    async def verify_sync(self, symbol: str) -> bool:
        """Verify that data was correctly synced to Supabase"""
        try:
            # Query the data back from Supabase
            response = self.client.table("cryptoverse_risk_grid").select("*").eq("symbol", symbol).execute()

            if response.data:
                count = len(response.data)
                if count == 41:
                    logger.info(f"✅ Verification passed for {symbol}: 41 points found")
                    return True
                else:
                    logger.warning(f"⚠️ Verification failed for {symbol}: {count} points found")
                    return False
            else:
                logger.error(f"❌ No data found for {symbol} in Supabase")
                return False

        except Exception as e:
            logger.error(f"Error verifying sync for {symbol}: {e}")
            return False

    async def verify_all_syncs(self) -> Dict[str, bool]:
        """Verify all synced data"""
        results = {}

        grid_files = list(self.risk_grids_dir.glob("*_risk_grid.json"))

        for grid_file in grid_files:
            symbol = grid_file.stem.replace("_risk_grid", "")
            results[symbol] = await self.verify_sync(symbol)

        # Summary
        verified = sum(1 for v in results.values() if v)
        logger.info(f"\nVerification complete: {verified}/{len(results)} symbols verified")

        return results

async def sync_all_risk_grids() -> Tuple[bool, Dict]:
    """Main function to sync all risk grids"""
    try:
        sync = RiskGridSync()
        success = await sync.sync_all_grids()

        if success:
            # Verify the sync
            verification = await sync.verify_all_syncs()
            return True, {"status": "success", "verification": verification}
        else:
            return False, {"status": "failed"}

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return False, {"status": "error", "error": str(e)}

async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Sync Risk Grids to Supabase")
    parser.add_argument("--symbol", help="Sync single symbol")
    parser.add_argument("--all", action="store_true", help="Sync all symbols")
    parser.add_argument("--verify", action="store_true", help="Verify synced data")

    args = parser.parse_args()

    sync = RiskGridSync()

    if args.symbol:
        # Sync single symbol
        success, message = await sync.sync_symbol_grid(args.symbol.upper())
        if success:
            logger.info(f"✅ {args.symbol} synced successfully")
        else:
            logger.error(f"❌ Failed to sync {args.symbol}: {message}")

    elif args.all:
        # Sync all symbols
        success = await sync.sync_all_grids()
        if success:
            logger.info("✅ All symbols synced successfully")
        else:
            logger.error("❌ Some symbols failed to sync")

    elif args.verify:
        # Verify all synced data
        results = await sync.verify_all_syncs()
        for symbol, verified in results.items():
            status = "✅" if verified else "❌"
            logger.info(f"{status} {symbol}")

    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())