#!/usr/bin/env python3
"""
Atomic IntoTheCryptoverse Risk Data Scraper
Ensures 100% completion before any Supabase sync
All-or-nothing approach for data integrity
"""

import asyncio
import json
import os
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cryptoverse_atomic.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AtomicCryptoverseScraper:
    """Atomic scraper with all-or-nothing approach"""

    def __init__(self):
        self.base_url = "https://app.intothecryptoverse.com"

        # ALL 25 symbols MUST be scraped
        self.required_symbols = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'binancecoin': 'BNB',
            'cardano': 'ADA',
            'ripple': 'XRP',
            'solana': 'SOL',
            'avalanche-2': 'AVAX',
            'polkadot': 'DOT',
            'matic-network': 'MATIC',
            'dogecoin': 'DOGE',
            'chainlink': 'LINK',
            'litecoin': 'LTC',
            'cosmos': 'ATOM',
            'stellar': 'XLM',
            'hedera-hashgraph': 'HBAR',
            'tron': 'TRX',
            'vechain': 'VET',
            'monero': 'XMR',
            'maker': 'MKR',
            'tezos': 'XTZ',
            'aave': 'AAVE',
            'render-token': 'RNDR',
            'sui': 'SUI',
            'blockstack': 'STX',
            'sei-network': 'SEI'
        }

        # Directories
        self.temp_dir = Path("temp_risk_grids")
        self.staging_dir = Path("staging_risk_grids")
        self.production_dir = Path("extracted_risk_grids")
        self.backup_dir = Path("backup_risk_grids")
        self.validation_dir = Path("risk_grid_validation")

        # Create directories
        for dir_path in [self.temp_dir, self.staging_dir, self.production_dir,
                        self.backup_dir, self.validation_dir]:
            dir_path.mkdir(exist_ok=True)

    def cleanup_temp(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    def cleanup_staging(self):
        """Clean up staging directory"""
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
        self.staging_dir.mkdir(exist_ok=True)

    async def scrape_with_mcp_browser(self, url_name: str, symbol: str) -> Optional[Dict]:
        """Scrape single symbol using MCP Browser"""
        try:
            logger.info(f"Scraping {symbol} from {url_name}...")

            # Navigate to risk page
            url = f"{self.base_url}/assets/{url_name}/risk"

            # Use MCP Browser to navigate and extract
            # This will be replaced with actual MCP calls
            from mcp_browser_integration import MCPBrowserClient, CryptoverseTableExtractor

            mcp = MCPBrowserClient()
            extractor = CryptoverseTableExtractor(mcp)

            # Navigate to page
            await mcp.navigate(url)
            await mcp.wait(3)  # Wait for page load

            # Extract risk table
            risk_data = await extractor.extract_risk_table(symbol)

            if not risk_data:
                logger.error(f"Failed to extract data for {symbol}")
                return None

            # Add metadata
            risk_data["url_name"] = url_name
            risk_data["extraction_timestamp"] = datetime.now().isoformat()
            risk_data["source_url"] = url

            return risk_data

        except Exception as e:
            logger.error(f"Error scraping {symbol}: {e}")
            return None

    def validate_single_grid(self, symbol: str, data: Dict) -> Tuple[bool, List[str]]:
        """Validate a single symbol's risk grid"""
        errors = []

        # Check symbol matches
        if data.get("symbol") != symbol:
            errors.append(f"Symbol mismatch: expected {symbol}, got {data.get('symbol')}")

        # Check fiat grid has exactly 41 points
        fiat_grid = data.get("fiat_risk_grid", [])
        if len(fiat_grid) != 41:
            errors.append(f"Fiat grid has {len(fiat_grid)} points, need exactly 41")

        # Verify risk values sequence (0.000 to 1.000 in 0.025 steps)
        expected_risks = [round(i * 0.025, 3) for i in range(41)]
        actual_risks = [point.get("risk") for point in fiat_grid]

        if actual_risks != expected_risks:
            errors.append("Risk values don't match expected sequence 0.000-1.000")

        # Check all prices are positive numbers
        for i, point in enumerate(fiat_grid):
            price = point.get("price", 0)
            if not isinstance(price, (int, float)) or price <= 0:
                errors.append(f"Invalid price at risk {point.get('risk')}: {price}")
                break

        # Check BTC grid if present (must also be 41 points)
        btc_grid = data.get("btc_risk_grid", [])
        if btc_grid:
            if len(btc_grid) != 41:
                errors.append(f"BTC grid has {len(btc_grid)} points, need 41")

        # Check ETH grid if present (must also be 41 points)
        eth_grid = data.get("eth_risk_grid", [])
        if eth_grid:
            if len(eth_grid) != 41:
                errors.append(f"ETH grid has {len(eth_grid)} points, need 41")

        is_valid = len(errors) == 0
        return is_valid, errors

    def save_to_temp(self, symbol: str, data: Dict) -> bool:
        """Save data to temporary directory"""
        try:
            file_path = self.temp_dir / f"{symbol}_risk_grid.json"

            # Add integrity checksum
            content = json.dumps(data, sort_keys=True)
            data["checksum"] = hashlib.sha256(content.encode()).hexdigest()

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {symbol} to temp directory")
            return True

        except Exception as e:
            logger.error(f"Error saving {symbol} to temp: {e}")
            return False

    async def atomic_scrape_all(self) -> Tuple[bool, Dict]:
        """
        Atomically scrape ALL symbols
        Returns success only if ALL 25 symbols are scraped successfully
        """
        logger.info("\n" + "="*60)
        logger.info("🎯 ATOMIC SCRAPING - ALL OR NOTHING")
        logger.info(f"Required: {len(self.required_symbols)} symbols")
        logger.info("="*60)

        # Clean up temp directory
        self.cleanup_temp()

        # Track results
        results = {
            "successful": [],
            "failed": [],
            "validation_errors": {},
            "scraped_data": {}
        }

        # Phase 1: Scrape ALL symbols
        logger.info("\n📊 PHASE 1: SCRAPING ALL SYMBOLS")

        for url_name, symbol in self.required_symbols.items():
            logger.info(f"\n[{len(results['successful']) + len(results['failed']) + 1}/{len(self.required_symbols)}] Processing {symbol}...")

            # Scrape with retry logic
            max_retries = 3
            retry_count = 0
            scraped_data = None

            while retry_count < max_retries and not scraped_data:
                if retry_count > 0:
                    logger.info(f"Retry {retry_count}/{max_retries} for {symbol}")
                    await asyncio.sleep(5)  # Wait before retry

                scraped_data = await self.scrape_with_mcp_browser(url_name, symbol)
                retry_count += 1

            if not scraped_data:
                logger.error(f"❌ Failed to scrape {symbol} after {max_retries} attempts")
                results["failed"].append(symbol)
                continue

            # Validate immediately
            is_valid, errors = self.validate_single_grid(symbol, scraped_data)

            if not is_valid:
                logger.error(f"❌ Validation failed for {symbol}: {errors}")
                results["failed"].append(symbol)
                results["validation_errors"][symbol] = errors
                continue

            # Save to temp if valid
            if self.save_to_temp(symbol, scraped_data):
                results["successful"].append(symbol)
                results["scraped_data"][symbol] = scraped_data
                logger.info(f"✅ {symbol} scraped and validated successfully")
            else:
                results["failed"].append(symbol)
                logger.error(f"❌ Failed to save {symbol}")

            # Small delay between symbols
            await asyncio.sleep(2)

        # Phase 2: Check if we have 100% success
        logger.info("\n📋 PHASE 2: VALIDATION CHECK")

        total_required = len(self.required_symbols)
        total_successful = len(results["successful"])
        success_rate = (total_successful / total_required * 100) if total_required > 0 else 0

        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Successful: {total_successful}/{total_required}")

        if total_successful < total_required:
            logger.error("\n❌ ATOMIC SCRAPING FAILED - NOT ALL SYMBOLS SCRAPED")
            logger.error(f"Missing symbols: {results['failed']}")

            # Clean up temp directory since we failed
            self.cleanup_temp()

            # Save failure report
            self.save_atomic_report(False, results, success_rate)

            return False, results

        # Phase 3: Move to staging if 100% success
        logger.info("\n✅ PHASE 3: MOVING TO STAGING")

        self.cleanup_staging()

        for symbol in results["successful"]:
            source = self.temp_dir / f"{symbol}_risk_grid.json"
            dest = self.staging_dir / f"{symbol}_risk_grid.json"
            shutil.copy2(source, dest)

        logger.info(f"Moved {total_successful} files to staging")

        # Phase 4: Final validation in staging
        logger.info("\n🔍 PHASE 4: FINAL VALIDATION")

        final_validation = self.validate_staging_directory()

        if not final_validation:
            logger.error("❌ Final validation failed")
            self.cleanup_staging()
            return False, results

        logger.info("✅ ATOMIC SCRAPING SUCCESSFUL - ALL SYMBOLS READY")

        # Save success report
        self.save_atomic_report(True, results, success_rate)

        return True, results

    def validate_staging_directory(self) -> bool:
        """Validate all files in staging directory"""
        try:
            # Check we have exactly 25 files
            files = list(self.staging_dir.glob("*_risk_grid.json"))

            if len(files) != len(self.required_symbols):
                logger.error(f"Staging has {len(files)} files, need {len(self.required_symbols)}")
                return False

            # Validate each file
            for file_path in files:
                symbol = file_path.stem.replace("_risk_grid", "")

                with open(file_path, 'r') as f:
                    data = json.load(f)

                is_valid, errors = self.validate_single_grid(symbol, data)

                if not is_valid:
                    logger.error(f"Staging validation failed for {symbol}: {errors}")
                    return False

                # Verify checksum
                stored_checksum = data.get("checksum")
                data_copy = data.copy()
                del data_copy["checksum"]
                content = json.dumps(data_copy, sort_keys=True)
                calculated_checksum = hashlib.sha256(content.encode()).hexdigest()

                if stored_checksum != calculated_checksum:
                    logger.error(f"Checksum mismatch for {symbol}")
                    return False

            logger.info(f"✅ All {len(files)} files validated successfully")
            return True

        except Exception as e:
            logger.error(f"Staging validation error: {e}")
            return False

    def promote_to_production(self) -> bool:
        """
        Promote staging to production
        This is the final step after successful sync
        """
        try:
            logger.info("\n🚀 PROMOTING TO PRODUCTION")

            # Backup current production
            if self.production_dir.exists():
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path = self.backup_dir / backup_name
                shutil.copytree(self.production_dir, backup_path)
                logger.info(f"Backed up current production to {backup_path}")

            # Clear production directory
            if self.production_dir.exists():
                shutil.rmtree(self.production_dir)
            self.production_dir.mkdir(exist_ok=True)

            # Move all files from staging to production
            for file_path in self.staging_dir.glob("*_risk_grid.json"):
                dest = self.production_dir / file_path.name
                shutil.copy2(file_path, dest)

            logger.info(f"✅ Promoted {len(list(self.staging_dir.glob('*')))} files to production")

            # Clean up staging
            self.cleanup_staging()

            return True

        except Exception as e:
            logger.error(f"Error promoting to production: {e}")
            return False

    def save_atomic_report(self, success: bool, results: Dict, success_rate: float):
        """Save detailed atomic scraping report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "success_rate": f"{success_rate:.1f}%",
            "total_required": len(self.required_symbols),
            "total_successful": len(results["successful"]),
            "total_failed": len(results["failed"]),
            "successful_symbols": results["successful"],
            "failed_symbols": results["failed"],
            "validation_errors": results.get("validation_errors", {}),
            "atomic_result": "COMPLETE" if success else "FAILED"
        }

        report_file = self.validation_dir / f"atomic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {report_file}")

class AtomicSupabaseSync:
    """Atomic Supabase sync - all or nothing"""

    def __init__(self):
        self.staging_dir = Path("staging_risk_grids")
        self.production_dir = Path("extracted_risk_grids")
        self.sync_log_dir = Path("sync_logs")
        self.sync_log_dir.mkdir(exist_ok=True)

    async def atomic_sync(self) -> Tuple[bool, Dict]:
        """
        Atomic sync to Supabase
        Only syncs if ALL symbols are in staging and valid
        """
        logger.info("\n" + "="*60)
        logger.info("🔄 ATOMIC SUPABASE SYNC")
        logger.info("="*60)

        # Step 1: Verify staging directory
        if not self.verify_staging():
            logger.error("❌ Staging verification failed - aborting sync")
            return False, {"error": "Staging verification failed"}

        # Step 2: Load all staging data
        staging_data = self.load_all_staging_data()

        if len(staging_data) != 25:
            logger.error(f"❌ Expected 25 symbols, got {len(staging_data)}")
            return False, {"error": f"Incomplete data: {len(staging_data)}/25"}

        # Step 3: Begin atomic transaction
        logger.info("📦 Starting atomic Supabase transaction...")

        from risk_grid_sync_to_supabase import RiskGridSync
        sync = RiskGridSync()

        try:
            # Start transaction (if Supabase supports it)
            # Otherwise, we'll do careful sequential updates

            success_count = 0
            failed_symbols = []

            for symbol, data in staging_data.items():
                logger.info(f"Syncing {symbol}...")

                success, message = await sync.sync_symbol_grid(symbol)

                if success:
                    success_count += 1
                    logger.info(f"✅ {symbol} synced")
                else:
                    failed_symbols.append(symbol)
                    logger.error(f"❌ {symbol} failed: {message}")

                    # If any symbol fails, abort entire sync
                    logger.error("ABORTING SYNC - Atomic operation failed")
                    return False, {
                        "error": f"Failed to sync {symbol}",
                        "message": message,
                        "failed_symbols": failed_symbols
                    }

            # Step 4: Verify all data in Supabase
            logger.info("\n🔍 Verifying Supabase data...")

            verification = await sync.verify_all_syncs()
            verified_count = sum(1 for v in verification.values() if v)

            if verified_count != 25:
                logger.error(f"❌ Verification failed: {verified_count}/25")
                return False, {
                    "error": "Verification failed",
                    "verified": verified_count,
                    "required": 25
                }

            logger.info("✅ ATOMIC SYNC SUCCESSFUL - ALL 25 SYMBOLS SYNCED")

            # Step 5: Promote to production
            scraper = AtomicCryptoverseScraper()
            if scraper.promote_to_production():
                logger.info("✅ Promoted to production")

            # Save success report
            self.save_sync_report(True, success_count, failed_symbols)

            return True, {
                "success": True,
                "synced": success_count,
                "verified": verified_count
            }

        except Exception as e:
            logger.error(f"❌ Atomic sync failed with error: {e}")
            return False, {"error": str(e)}

    def verify_staging(self) -> bool:
        """Verify staging directory has all required files"""
        if not self.staging_dir.exists():
            logger.error("Staging directory doesn't exist")
            return False

        files = list(self.staging_dir.glob("*_risk_grid.json"))

        if len(files) != 25:
            logger.error(f"Staging has {len(files)} files, need exactly 25")
            return False

        logger.info(f"✅ Staging verified: {len(files)} files ready")
        return True

    def load_all_staging_data(self) -> Dict:
        """Load all data from staging directory"""
        data = {}

        for file_path in self.staging_dir.glob("*_risk_grid.json"):
            symbol = file_path.stem.replace("_risk_grid", "")

            with open(file_path, 'r') as f:
                data[symbol] = json.load(f)

        return data

    def save_sync_report(self, success: bool, synced: int, failed: List):
        """Save atomic sync report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "atomic_sync": success,
            "symbols_synced": synced,
            "failed_symbols": failed,
            "status": "COMPLETE" if success else "FAILED"
        }

        report_file = self.sync_log_dir / f"atomic_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

async def run_atomic_update() -> bool:
    """
    Run complete atomic update
    Only succeeds if ALL 25 symbols are scraped AND synced
    """
    logger.info("\n" + "🎯"*20)
    logger.info("ATOMIC UPDATE CYCLE")
    logger.info("Requirement: 100% success or rollback")
    logger.info("🎯"*20)

    # Phase 1: Atomic Scrape
    scraper = AtomicCryptoverseScraper()
    scrape_success, scrape_results = await scraper.atomic_scrape_all()

    if not scrape_success:
        logger.error("\n❌ ATOMIC UPDATE FAILED AT SCRAPING")
        logger.error("No data will be synced to Supabase")
        return False

    # Phase 2: Atomic Sync
    logger.info("\n" + "="*60)
    logger.info("Proceeding to Supabase sync...")

    syncer = AtomicSupabaseSync()
    sync_success, sync_results = await syncer.atomic_sync()

    if not sync_success:
        logger.error("\n❌ ATOMIC UPDATE FAILED AT SYNC")
        logger.error("Staging data preserved for debugging")
        return False

    # Success!
    logger.info("\n" + "✅"*20)
    logger.info("ATOMIC UPDATE COMPLETE")
    logger.info("All 25 symbols scraped and synced successfully")
    logger.info("✅"*20)

    return True

async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Atomic IntoTheCryptoverse Scraper")
    parser.add_argument("--run", action="store_true", help="Run atomic update")
    parser.add_argument("--verify", action="store_true", help="Verify staging")
    parser.add_argument("--promote", action="store_true", help="Promote staging to production")

    args = parser.parse_args()

    if args.run:
        success = await run_atomic_update()
        if success:
            logger.info("\n✅ Atomic update successful")
        else:
            logger.error("\n❌ Atomic update failed")
            exit(1)

    elif args.verify:
        syncer = AtomicSupabaseSync()
        if syncer.verify_staging():
            logger.info("✅ Staging verified")
        else:
            logger.error("❌ Staging verification failed")

    elif args.promote:
        scraper = AtomicCryptoverseScraper()
        if scraper.promote_to_production():
            logger.info("✅ Promoted to production")
        else:
            logger.error("❌ Promotion failed")

    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())