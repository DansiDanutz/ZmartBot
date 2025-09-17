#!/usr/bin/env python3
"""
ZmartBot Achievements Scheduler
Daily scheduled execution of achievements scanning and documentation
"""

import os
import sys
import time
import schedule
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json

class AchievementsScheduler:
    """
    Scheduler for daily achievements service execution
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.service_script = self.project_root / "zmart-api" / "achievements_service.py"
        self.log_file = self.project_root / "zmart-api" / "logs" / "achievements_scheduler.log"
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(self.log_file)),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Schedule configuration
        self.daily_run_time = "00:00"  # UTC midnight
        self.is_running = False
        self.scheduler_thread = None
    
    def run_achievements_scan(self):
        """Execute the achievements service scan"""
        try:
            self.logger.info("Starting scheduled achievements scan")
            
            # Run the achievements service
            result = subprocess.run([
                sys.executable, 
                str(self.service_script), 
                "--project-root", str(self.project_root),
                "--scan"
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                # Parse and log results
                try:
                    scan_results = json.loads(result.stdout)
                    self.logger.info(
                        f"Achievements scan completed successfully: "
                        f"{scan_results.get('new_achievements_stored', 0)} new achievements stored, "
                        f"processed {scan_results.get('files_processed', 0)} files in "
                        f"{scan_results.get('duration_seconds', 0)}s"
                    )
                except json.JSONDecodeError:
                    self.logger.info("Achievements scan completed successfully (no JSON output)")
            else:
                self.logger.error(f"Achievements scan failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            self.logger.error("Achievements scan timed out after 5 minutes")
        except Exception as e:
            self.logger.error(f"Error running achievements scan: {e}")
    
    def setup_schedule(self):
        """Setup the daily schedule"""
        schedule.clear()  # Clear any existing schedules
        schedule.every().day.at(self.daily_run_time).do(self.run_achievements_scan)
        self.logger.info(f"Scheduled daily achievements scan at {self.daily_run_time} UTC")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.logger.info("Starting achievements scheduler")
        self.is_running = True
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue running despite errors
        
        self.logger.info("Achievements scheduler stopped")
    
    def start_scheduler(self, run_immediately: bool = False):
        """Start the scheduler in a background thread"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        
        # Optionally run immediately
        if run_immediately:
            self.logger.info("Running initial achievements scan")
            self.run_achievements_scan()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Achievements scheduler started in background")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Achievements scheduler stop requested")
    
    def get_next_run_time(self) -> str:
        """Get the next scheduled run time"""
        jobs = schedule.jobs
        if jobs:
            next_run = jobs[0].next_run
            return next_run.strftime('%Y-%m-%d %H:%M:%S UTC')
        return "Not scheduled"
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "daily_run_time": self.daily_run_time,
            "next_run": self.get_next_run_time(),
            "scheduler_thread_alive": self.scheduler_thread.is_alive() if self.scheduler_thread else False,
            "log_file": str(self.log_file),
            "service_script": str(self.service_script)
        }

def main():
    """Main entry point for Achievements Scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Achievements Scheduler")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--start", action="store_true", help="Start the scheduler")
    parser.add_argument("--run-now", action="store_true", help="Run achievements scan immediately")
    parser.add_argument("--schedule-time", default="00:00", help="Daily run time (HH:MM UTC)")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (keeps running)")
    
    args = parser.parse_args()
    
    scheduler = AchievementsScheduler(args.project_root)
    scheduler.daily_run_time = args.schedule_time
    
    if args.run_now:
        print("Running achievements scan immediately...")
        scheduler.run_achievements_scan()
        
    elif args.start or args.daemon:
        print(f"Starting achievements scheduler (daily run at {args.schedule_time} UTC)")
        scheduler.start_scheduler(run_immediately=args.run_now)
        
        if args.daemon:
            print("Running as daemon. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(10)
                    if not scheduler.scheduler_thread.is_alive():
                        print("Scheduler thread died, restarting...")
                        scheduler.start_scheduler()
            except KeyboardInterrupt:
                print("Stopping scheduler...")
                scheduler.stop_scheduler()
        else:
            print("Scheduler started in background.")
    
    elif args.status:
        status = scheduler.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        print("Use --help for available commands")
        print("Example: python achievements_scheduler.py --start --run-now")

if __name__ == "__main__":
    main()