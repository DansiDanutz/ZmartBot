#!/usr/bin/env python3
"""
IntoTheCryptoverse Risk Data Automated Scraper
Scrapes risk grid data from IntoTheCryptoverse every 72 hours
Uses MCP Browser for automation
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import schedule
import time
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cryptoverse_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoverseRiskScraper:
    """Automated scraper for IntoTheCryptoverse risk data"""

    def __init__(self):
        self.base_url = "https://intothecryptoverse.com"
        self.symbols = [
            'BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'AVAX', 'DOT', 'MATIC', 'DOGE',
            'LINK', 'LTC', 'ATOM', 'XLM', 'HBAR', 'TRX', 'VET', 'XMR', 'MKR', 'XTZ',
            'AAVE', 'RNDR', 'SUI', 'STX', 'SEI'
        ]
        self.output_dir = Path("extracted_risk_grids")
        self.output_dir.mkdir(exist_ok=True)
        self.validation_dir = Path("risk_grid_validation")
        self.validation_dir.mkdir(exist_ok=True)

    async def navigate_to_symbol(self, symbol: str) -> bool:
        """Navigate to symbol's risk page using MCP browser"""
        try:
            logger.info(f"Navigating to {symbol} risk page...")

            # Navigate to the risk metric page for the symbol
            url = f"{self.base_url}/risk/{symbol.lower()}"

            # Use MCP browser to navigate
            result = await self.mcp_browser_navigate(url)

            # Wait for page to load
            await asyncio.sleep(3)

            # Take snapshot to verify we're on the right page
            snapshot = await self.mcp_browser_snapshot()

            if symbol.upper() in snapshot or symbol.lower() in snapshot:
                logger.info(f"Successfully navigated to {symbol} page")
                return True
            else:
                logger.warning(f"May not be on correct page for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error navigating to {symbol}: {e}")
            return False

    async def mcp_browser_navigate(self, url: str) -> Dict:
        """Navigate using MCP browser"""
        # This will be replaced with actual MCP browser call
        logger.info(f"MCP Browser: Navigating to {url}")
        # Simulated response for now
        return {"status": "success", "url": url}

    async def mcp_browser_snapshot(self) -> str:
        """Take snapshot using MCP browser"""
        # This will be replaced with actual MCP browser call
        logger.info("MCP Browser: Taking snapshot")
        # Simulated response for now
        return "Page content snapshot"

    async def extract_risk_table(self, symbol: str) -> Optional[Dict]:
        """Extract risk table data from the current page"""
        try:
            logger.info(f"Extracting risk table for {symbol}...")

            # Take snapshot of the page
            snapshot = await self.mcp_browser_snapshot()

            # Look for the risk table
            # The table typically has headers like "Risk", "Price USD", "Price BTC"

            risk_data = {
                "symbol": symbol,
                "current_price": 0,
                "current_risk": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "fiat_risk_grid": [],
                "btc_risk_grid": [],
                "eth_risk_grid": []
            }

            # Parse the risk grid (41 points from 0.000 to 1.000)
            for i in range(41):
                risk_value = i * 0.025  # 0.000, 0.025, 0.050, ..., 1.000

                # Extract corresponding prices from the table
                # This would use actual MCP browser element selection
                fiat_price = await self.extract_price_at_risk(symbol, risk_value, "USD")
                btc_price = await self.extract_price_at_risk(symbol, risk_value, "BTC")
                eth_price = await self.extract_price_at_risk(symbol, risk_value, "ETH")

                if fiat_price:
                    risk_data["fiat_risk_grid"].append({
                        "risk": round(risk_value, 3),
                        "price": fiat_price
                    })

                if btc_price:
                    risk_data["btc_risk_grid"].append({
                        "risk": round(risk_value, 3),
                        "price_btc": btc_price
                    })

                if eth_price:
                    risk_data["eth_risk_grid"].append({
                        "risk": round(risk_value, 3),
                        "price_eth": eth_price
                    })

            # Validate we got all 41 points
            if len(risk_data["fiat_risk_grid"]) == 41:
                logger.info(f"Successfully extracted {len(risk_data['fiat_risk_grid'])} risk points for {symbol}")
                return risk_data
            else:
                logger.warning(f"Incomplete data for {symbol}: only {len(risk_data['fiat_risk_grid'])} points")
                return None

        except Exception as e:
            logger.error(f"Error extracting risk table for {symbol}: {e}")
            return None

    async def extract_price_at_risk(self, symbol: str, risk: float, price_type: str) -> Optional[float]:
        """Extract price at specific risk level"""
        try:
            # This would use actual MCP browser to find the specific cell
            # For now, returning simulated data

            # Simulated extraction based on risk level
            if price_type == "USD":
                # Simulate USD price calculation
                base_price = {"BTC": 100000, "ETH": 3000, "BNB": 500}.get(symbol, 100)
                price = base_price * (0.3 + risk * 1.7)  # Simulated formula
                return round(price, 2)
            elif price_type == "BTC":
                # Simulate BTC price
                return round(0.001 + risk * 0.05, 6)
            elif price_type == "ETH":
                # Simulate ETH price
                return round(0.01 + risk * 0.5, 6)

            return None

        except Exception as e:
            logger.error(f"Error extracting price at risk {risk} for {symbol}: {e}")
            return None

    def validate_risk_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate extracted risk data"""
        errors = []

        # Check symbol
        if not data.get("symbol"):
            errors.append("Missing symbol")

        # Check fiat risk grid
        fiat_grid = data.get("fiat_risk_grid", [])
        if len(fiat_grid) != 41:
            errors.append(f"Fiat grid has {len(fiat_grid)} points, expected 41")

        # Check risk values are correct (0.000 to 1.000 in 0.025 increments)
        expected_risks = [round(i * 0.025, 3) for i in range(41)]
        actual_risks = [point.get("risk") for point in fiat_grid]

        if actual_risks != expected_risks:
            errors.append("Risk values don't match expected sequence")

        # Check prices are positive
        for point in fiat_grid:
            if point.get("price", 0) <= 0:
                errors.append(f"Invalid price at risk {point.get('risk')}")

        # Check BTC grid if present
        btc_grid = data.get("btc_risk_grid", [])
        if btc_grid and len(btc_grid) != 41:
            errors.append(f"BTC grid has {len(btc_grid)} points, expected 41")

        is_valid = len(errors) == 0
        return is_valid, errors

    def save_risk_data(self, symbol: str, data: Dict) -> bool:
        """Save risk data to JSON file"""
        try:
            filename = self.output_dir / f"{symbol}_risk_grid.json"

            # Add metadata
            data["extraction_timestamp"] = datetime.now().isoformat()
            data["extraction_method"] = "MCP_BROWSER"
            data["validated"] = True

            # Calculate checksum for integrity
            content = json.dumps(data, sort_keys=True)
            data["checksum"] = hashlib.md5(content.encode()).hexdigest()

            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved risk data for {symbol} to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error saving risk data for {symbol}: {e}")
            return False

    def load_existing_data(self, symbol: str) -> Optional[Dict]:
        """Load existing risk data for comparison"""
        try:
            filename = self.output_dir / f"{symbol}_risk_grid.json"
            if filename.exists():
                with open(filename, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading existing data for {symbol}: {e}")
            return None

    def has_data_changed(self, old_data: Dict, new_data: Dict) -> bool:
        """Check if risk data has changed"""
        if not old_data:
            return True

        # Compare fiat risk grids
        old_grid = old_data.get("fiat_risk_grid", [])
        new_grid = new_data.get("fiat_risk_grid", [])

        if len(old_grid) != len(new_grid):
            return True

        for old, new in zip(old_grid, new_grid):
            if abs(old.get("price", 0) - new.get("price", 0)) > 0.01:
                return True

        return False

    async def scrape_all_symbols(self) -> Dict[str, bool]:
        """Scrape risk data for all symbols"""
        results = {}
        successful = []
        failed = []
        updated = []
        unchanged = []

        logger.info(f"Starting scrape for {len(self.symbols)} symbols...")

        for symbol in self.symbols:
            try:
                logger.info(f"\n{'='*50}")
                logger.info(f"Processing {symbol}...")

                # Navigate to symbol page
                if not await self.navigate_to_symbol(symbol):
                    logger.error(f"Failed to navigate to {symbol}")
                    failed.append(symbol)
                    results[symbol] = False
                    continue

                # Extract risk table
                risk_data = await self.extract_risk_table(symbol)

                if not risk_data:
                    logger.error(f"Failed to extract data for {symbol}")
                    failed.append(symbol)
                    results[symbol] = False
                    continue

                # Validate data
                is_valid, errors = self.validate_risk_data(risk_data)

                if not is_valid:
                    logger.error(f"Invalid data for {symbol}: {errors}")
                    failed.append(symbol)
                    results[symbol] = False
                    continue

                # Check if data has changed
                old_data = self.load_existing_data(symbol)
                if self.has_data_changed(old_data, risk_data):
                    updated.append(symbol)
                    logger.info(f"Data updated for {symbol}")
                else:
                    unchanged.append(symbol)
                    logger.info(f"No changes for {symbol}")

                # Save data
                if self.save_risk_data(symbol, risk_data):
                    successful.append(symbol)
                    results[symbol] = True
                else:
                    failed.append(symbol)
                    results[symbol] = False

                # Small delay between symbols
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Unexpected error processing {symbol}: {e}")
                failed.append(symbol)
                results[symbol] = False

        # Generate summary report
        logger.info(f"\n{'='*50}")
        logger.info("SCRAPING COMPLETE")
        logger.info(f"Successful: {len(successful)}/{len(self.symbols)}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Updated: {updated}")
        logger.info(f"Unchanged: {unchanged}")

        # Save summary report
        self.save_scrape_report(results, successful, failed, updated, unchanged)

        return results

    def save_scrape_report(self, results: Dict, successful: List, failed: List,
                          updated: List, unchanged: List):
        """Save scraping report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_symbols": len(self.symbols),
            "successful": len(successful),
            "failed": len(failed),
            "updated": len(updated),
            "unchanged": len(unchanged),
            "success_rate": f"{(len(successful)/len(self.symbols)*100):.1f}%",
            "symbols": {
                "successful": successful,
                "failed": failed,
                "updated": updated,
                "unchanged": unchanged
            },
            "details": results
        }

        report_file = self.validation_dir / f"scrape_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {report_file}")

    async def sync_to_supabase(self) -> bool:
        """Sync all risk data to Supabase"""
        try:
            logger.info("Starting Supabase sync...")

            # Import Supabase sync module
            from sync_risk_grids_to_supabase import sync_all_risk_grids

            # Run sync
            success, report = await sync_all_risk_grids()

            if success:
                logger.info("Successfully synced to Supabase")
                logger.info(f"Sync report: {report}")
                return True
            else:
                logger.error("Failed to sync to Supabase")
                return False

        except Exception as e:
            logger.error(f"Error syncing to Supabase: {e}")
            return False

    async def run_complete_update(self) -> bool:
        """Run complete update cycle: scrape + validate + sync"""
        try:
            logger.info("\n" + "="*60)
            logger.info("STARTING COMPLETE UPDATE CYCLE")
            logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*60)

            # Step 1: Scrape all symbols
            results = await self.scrape_all_symbols()

            # Check if we got at least 90% success rate
            success_rate = sum(1 for v in results.values() if v) / len(results)

            if success_rate < 0.9:
                logger.error(f"Low success rate: {success_rate*100:.1f}%")
                logger.error("Aborting Supabase sync due to incomplete data")
                return False

            # Step 2: Sync to Supabase
            logger.info("\nStarting Supabase synchronization...")
            if await self.sync_to_supabase():
                logger.info("✅ COMPLETE UPDATE SUCCESSFUL")
                return True
            else:
                logger.error("❌ Supabase sync failed")
                return False

        except Exception as e:
            logger.error(f"Error in complete update cycle: {e}")
            return False

class ScheduledScraper:
    """Scheduler for running scraper every 72 hours"""

    def __init__(self):
        self.scraper = CryptoverseRiskScraper()
        self.last_run_file = Path("last_scrape_run.json")

    def load_last_run(self) -> Optional[datetime]:
        """Load last run timestamp"""
        try:
            if self.last_run_file.exists():
                with open(self.last_run_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data["last_run"])
            return None
        except Exception as e:
            logger.error(f"Error loading last run: {e}")
            return None

    def save_last_run(self):
        """Save last run timestamp"""
        try:
            data = {
                "last_run": datetime.now().isoformat(),
                "next_run": (datetime.now() + timedelta(hours=72)).isoformat()
            }
            with open(self.last_run_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving last run: {e}")

    async def run_scheduled_scrape(self):
        """Run scheduled scrape"""
        logger.info("\n" + "🚀"*20)
        logger.info("SCHEDULED SCRAPE STARTING")
        logger.info("🚀"*20)

        success = await self.scraper.run_complete_update()

        if success:
            self.save_last_run()
            logger.info("✅ Scheduled scrape completed successfully")
        else:
            logger.error("❌ Scheduled scrape failed")

        # Calculate next run
        next_run = datetime.now() + timedelta(hours=72)
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    def check_and_run(self):
        """Check if it's time to run and execute if needed"""
        last_run = self.load_last_run()

        if last_run:
            time_since_last = datetime.now() - last_run
            if time_since_last < timedelta(hours=71):
                hours_until_next = 72 - (time_since_last.total_seconds() / 3600)
                logger.info(f"Not time yet. Next run in {hours_until_next:.1f} hours")
                return

        # Run the scrape
        asyncio.run(self.run_scheduled_scrape())

    def start_scheduler(self):
        """Start the scheduler"""
        logger.info("Starting IntoTheCryptoverse Risk Data Scheduler")
        logger.info("Schedule: Every 72 hours")

        # Schedule the job
        schedule.every(72).hours.do(self.check_and_run)

        # Also check immediately on start
        self.check_and_run()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="IntoTheCryptoverse Risk Data Scraper")
    parser.add_argument("--run-once", action="store_true", help="Run once immediately")
    parser.add_argument("--schedule", action="store_true", help="Run on 72-hour schedule")
    parser.add_argument("--symbol", help="Scrape single symbol")
    parser.add_argument("--sync-only", action="store_true", help="Only sync to Supabase")

    args = parser.parse_args()

    if args.run_once:
        # Run once immediately
        scraper = CryptoverseRiskScraper()
        asyncio.run(scraper.run_complete_update())

    elif args.symbol:
        # Scrape single symbol
        scraper = CryptoverseRiskScraper()
        scraper.symbols = [args.symbol.upper()]
        asyncio.run(scraper.scrape_all_symbols())

    elif args.sync_only:
        # Only sync to Supabase
        scraper = CryptoverseRiskScraper()
        asyncio.run(scraper.sync_to_supabase())

    elif args.schedule:
        # Run on schedule
        scheduler = ScheduledScraper()
        scheduler.start_scheduler()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()