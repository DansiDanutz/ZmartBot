#!/usr/bin/env python3
"""
72-Hour Automated Scheduler for IntoTheCryptoverse Risk Data
Runs scraping and sync every 72 hours automatically
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import schedule
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cryptoverse_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoverseScheduler:
    """72-hour scheduler for risk data updates"""

    def __init__(self):
        self.state_file = Path("scheduler_state.json")
        self.running = True
        self.current_task = None

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
        self.running = False

        if self.current_task:
            logger.info("Waiting for current task to complete...")

        self.save_state({"status": "stopped", "timestamp": datetime.now().isoformat()})
        sys.exit(0)

    def load_state(self) -> Dict:
        """Load scheduler state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return {}

    def save_state(self, state: Dict):
        """Save scheduler state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def get_last_run(self) -> Optional[datetime]:
        """Get timestamp of last successful run"""
        state = self.load_state()
        last_run = state.get("last_successful_run")

        if last_run:
            return datetime.fromisoformat(last_run)
        return None

    def should_run_now(self) -> bool:
        """Check if we should run based on 72-hour schedule"""
        last_run = self.get_last_run()

        if not last_run:
            logger.info("No previous run found. Will run immediately.")
            return True

        time_since_last = datetime.now() - last_run
        hours_since_last = time_since_last.total_seconds() / 3600

        if hours_since_last >= 72:
            logger.info(f"Last run was {hours_since_last:.1f} hours ago. Time to run!")
            return True
        else:
            hours_until_next = 72 - hours_since_last
            logger.info(f"Last run was {hours_since_last:.1f} hours ago.")
            logger.info(f"Next run in {hours_until_next:.1f} hours")
            return False

    async def run_update_cycle(self) -> bool:
        """Run the complete update cycle"""
        try:
            self.current_task = "update_cycle"

            logger.info("\n" + "🚀"*20)
            logger.info("AUTOMATED UPDATE CYCLE STARTING")
            logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("🚀"*20)

            # Update state
            self.save_state({
                "status": "running",
                "current_task": "scraping",
                "started_at": datetime.now().isoformat()
            })

            # Import and run the scraper
            from cryptoverse_mcp_scraper import IntoTheCryptoverseMCPScraper

            scraper = IntoTheCryptoverseMCPScraper()

            # Step 1: Scrape all symbols
            logger.info("\n📊 Phase 1: Scraping risk data from IntoTheCryptoverse...")
            scrape_results = await scraper.scrape_all_symbols()

            # Check success rate
            success_count = sum(1 for v in scrape_results.values() if v)
            success_rate = success_count / len(scrape_results) if scrape_results else 0

            if success_rate < 0.9:
                logger.error(f"⚠️ Low scraping success rate: {success_rate*100:.1f}%")
                self.save_state({
                    "status": "failed",
                    "error": "Low scraping success rate",
                    "timestamp": datetime.now().isoformat()
                })
                return False

            # Update state
            self.save_state({
                "status": "running",
                "current_task": "syncing",
                "scraping_complete": datetime.now().isoformat()
            })

            # Step 2: Sync to Supabase
            logger.info("\n🔄 Phase 2: Syncing to Supabase...")

            from risk_grid_sync_to_supabase import sync_all_risk_grids

            sync_success, sync_report = await sync_all_risk_grids()

            if sync_success:
                logger.info("✅ COMPLETE UPDATE CYCLE SUCCESSFUL")

                # Update state with success
                next_run = datetime.now() + timedelta(hours=72)
                self.save_state({
                    "status": "success",
                    "last_successful_run": datetime.now().isoformat(),
                    "next_scheduled_run": next_run.isoformat(),
                    "scrape_success_rate": f"{success_rate*100:.1f}%",
                    "symbols_updated": success_count
                })

                self.current_task = None
                return True
            else:
                logger.error("❌ Supabase sync failed")
                self.save_state({
                    "status": "failed",
                    "error": "Supabase sync failed",
                    "timestamp": datetime.now().isoformat()
                })
                self.current_task = None
                return False

        except Exception as e:
            logger.error(f"Error in update cycle: {e}")
            self.save_state({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.current_task = None
            return False

    def scheduled_job(self):
        """Job to run on schedule"""
        try:
            if self.should_run_now():
                logger.info("Starting scheduled update...")
                asyncio.run(self.run_update_cycle())
            else:
                logger.info("Not time for update yet.")

        except Exception as e:
            logger.error(f"Error in scheduled job: {e}")

    def start(self):
        """Start the scheduler"""
        logger.info("\n" + "="*60)
        logger.info("🎯 INTOTHECRYPTOVERSE 72-HOUR SCHEDULER")
        logger.info("="*60)
        logger.info("Schedule: Every 72 hours")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*60)

        # Load state and show last run info
        state = self.load_state()
        last_run = state.get("last_successful_run")

        if last_run:
            last_run_dt = datetime.fromisoformat(last_run)
            logger.info(f"Last successful run: {last_run_dt.strftime('%Y-%m-%d %H:%M:%S')}")

            next_run = last_run_dt + timedelta(hours=72)
            logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        # Check if should run immediately
        if self.should_run_now():
            logger.info("\n📌 Running update immediately...")
            asyncio.run(self.run_update_cycle())

        # Schedule the job to run every hour (will check if 72 hours passed)
        schedule.every().hour.do(self.scheduled_job)

        # Main loop
        logger.info("\n⏰ Scheduler is now running...")
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                logger.info("\n🛑 Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)

        logger.info("Scheduler has stopped.")

class SchedulerManager:
    """Manager for the scheduler process"""

    def __init__(self):
        self.pid_file = Path("scheduler.pid")
        self.log_file = Path("cryptoverse_scheduler.log")

    def is_running(self) -> bool:
        """Check if scheduler is already running"""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            import psutil
            return psutil.pid_exists(pid)

        except Exception:
            return False

    def start_scheduler(self, daemon: bool = False):
        """Start the scheduler"""
        if self.is_running():
            logger.warning("Scheduler is already running!")
            return

        if daemon:
            # Run as daemon
            import subprocess
            cmd = [sys.executable, __file__, "--run"]
            process = subprocess.Popen(
                cmd,
                stdout=open(self.log_file, 'a'),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            logger.info(f"Scheduler started as daemon (PID: {process.pid})")
            logger.info(f"Logs: {self.log_file}")

        else:
            # Run in foreground
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))

            scheduler = CryptoverseScheduler()
            scheduler.start()

    def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.is_running():
            logger.info("Scheduler is not running")
            return

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent stop signal to scheduler (PID: {pid})")

            # Clean up PID file
            self.pid_file.unlink()

        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def status(self):
        """Show scheduler status"""
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            logger.info(f"✅ Scheduler is running (PID: {pid})")

            # Show state
            state_file = Path("scheduler_state.json")
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)

                logger.info(f"Status: {state.get('status', 'unknown')}")

                if state.get('last_successful_run'):
                    last_run = datetime.fromisoformat(state['last_successful_run'])
                    logger.info(f"Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")

                    next_run = last_run + timedelta(hours=72)
                    time_until = next_run - datetime.now()
                    hours = time_until.total_seconds() / 3600

                    logger.info(f"Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"Time until next: {hours:.1f} hours")

        else:
            logger.info("❌ Scheduler is not running")

def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="72-Hour Automated Scheduler")
    parser.add_argument("--start", action="store_true", help="Start scheduler")
    parser.add_argument("--stop", action="store_true", help="Stop scheduler")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--run", action="store_true", help="Internal: run scheduler")
    parser.add_argument("--force", action="store_true", help="Force immediate run")

    args = parser.parse_args()

    manager = SchedulerManager()

    if args.start:
        logger.info("Starting 72-hour scheduler...")
        manager.start_scheduler(daemon=args.daemon)

    elif args.stop:
        logger.info("Stopping scheduler...")
        manager.stop_scheduler()

    elif args.status:
        manager.status()

    elif args.run:
        # Internal use: run the scheduler
        scheduler = CryptoverseScheduler()
        scheduler.start()

    elif args.force:
        # Force immediate run
        logger.info("Forcing immediate update cycle...")
        scheduler = CryptoverseScheduler()
        asyncio.run(scheduler.run_update_cycle())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()