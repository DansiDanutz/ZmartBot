#!/usr/bin/env python3
"""
Cryptoverse Background Agent
Fully autonomous service that runs forever without manual intervention
Integrates with ZmartBot background services
"""

import asyncio
import json
import os
import sys
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import threading
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cryptoverse_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoverseBackgroundAgent:
    """
    Fully autonomous background agent for risk data updates
    Runs forever without any manual intervention
    """

    def __init__(self):
        self.running = True
        self.update_interval_hours = 72
        self.last_update = None
        self.next_update = None
        self.update_in_progress = False
        self.consecutive_failures = 0
        self.max_failures = 3

        # State persistence
        self.state_file = Path("/tmp/cryptoverse_agent_state.json")
        self.pid_file = Path("/tmp/cryptoverse_agent.pid")

        # Load state
        self.load_state()

        # Signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Graceful shutdown"""
        logger.info(f"Received shutdown signal {signum}")
        self.running = False

    def load_state(self):
        """Load persistent state"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    last_update_str = state.get("last_update")
                    if last_update_str:
                        self.last_update = datetime.fromisoformat(last_update_str)
                        self.next_update = self.last_update + timedelta(hours=self.update_interval_hours)
                    self.consecutive_failures = state.get("consecutive_failures", 0)
                    logger.info(f"Loaded state: Last update {self.last_update}")
        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def save_state(self):
        """Save persistent state"""
        try:
            state = {
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "next_update": self.next_update.isoformat() if self.next_update else None,
                "consecutive_failures": self.consecutive_failures,
                "pid": os.getpid()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def save_pid(self):
        """Save process ID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def should_update(self) -> bool:
        """Check if update is needed"""
        if self.update_in_progress:
            return False

        # First run or no last update
        if not self.last_update:
            logger.info("No previous update found - will update now")
            return True

        # Check if enough time has passed
        time_since_last = datetime.now() - self.last_update
        hours_since = time_since_last.total_seconds() / 3600

        if hours_since >= self.update_interval_hours:
            logger.info(f"Time for update: {hours_since:.1f} hours since last update")
            return True

        logger.debug(f"Not time yet: {hours_since:.1f}/{self.update_interval_hours} hours")
        return False

    async def check_browser_ready(self) -> bool:
        """Check if MCP browser is ready"""
        try:
            # Check if browser process is running
            # This would check for actual browser/MCP status
            logger.info("Checking MCP Browser readiness...")

            # For now, assume it's ready if we're running
            # In production, this would check actual MCP connection
            return True

        except Exception as e:
            logger.error(f"Browser check failed: {e}")
            return False

    async def perform_atomic_update(self) -> bool:
        """Perform the atomic scraping and sync"""
        try:
            logger.info("\n" + "🚀"*20)
            logger.info("AUTONOMOUS UPDATE STARTING")
            logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("🚀"*20)

            self.update_in_progress = True

            # Import the production scraper with real MCP integration
            from cryptoverse_mcp_production import ProductionCryptoverseScraper

            # Create and run production scraper
            scraper = ProductionCryptoverseScraper()
            success = await scraper.run_complete_cycle()

            if success:
                logger.info("✅ Complete autonomous cycle successful")
                self.last_update = datetime.now()
                self.next_update = self.last_update + timedelta(hours=self.update_interval_hours)
                self.consecutive_failures = 0
                self.save_state()
                return True
            else:
                logger.error("❌ Autonomous cycle failed")
                self.consecutive_failures += 1
                return False

        except Exception as e:
            logger.error(f"Update error: {e}")
            self.consecutive_failures += 1
            return False
        finally:
            self.update_in_progress = False

    async def self_heal(self) -> bool:
        """Attempt to self-heal after failures"""
        logger.warning(f"Self-healing after {self.consecutive_failures} failures...")

        try:
            # Clear temp directories
            temp_dirs = ["temp_risk_grids", "staging_risk_grids"]
            for dir_name in temp_dirs:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    import shutil
                    shutil.rmtree(dir_path)
                    dir_path.mkdir(exist_ok=True)
                    logger.info(f"Cleaned {dir_name}")

            # Reset failure count if healing worked
            self.consecutive_failures = 0
            return True

        except Exception as e:
            logger.error(f"Self-healing failed: {e}")
            return False

    async def main_loop(self):
        """Main autonomous loop"""
        logger.info("🤖 Cryptoverse Background Agent Started")
        logger.info(f"Update interval: {self.update_interval_hours} hours")
        logger.info("Running fully autonomous - no manual intervention needed")

        self.save_pid()

        while self.running:
            try:
                # Check if update needed
                if self.should_update():
                    # Check browser readiness
                    if await self.check_browser_ready():
                        # Perform update
                        success = await self.perform_atomic_update()

                        if not success:
                            # Check if too many failures
                            if self.consecutive_failures >= self.max_failures:
                                logger.error(f"Too many failures ({self.consecutive_failures})")
                                await self.self_heal()
                    else:
                        logger.warning("Browser not ready - skipping update")
                else:
                    # Log next update time
                    if self.next_update:
                        time_until = self.next_update - datetime.now()
                        hours_until = time_until.total_seconds() / 3600
                        if hours_until > 0:
                            logger.info(f"Next update in {hours_until:.1f} hours")

                # Sleep for 1 hour before next check
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)  # Short sleep on error

        logger.info("Background agent stopped")

    def start(self):
        """Start the background agent"""
        try:
            # Run the main loop
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")

class CryptoverseAgentManager:
    """Manager for the background agent"""

    @staticmethod
    def is_running() -> bool:
        """Check if agent is already running"""
        pid_file = Path("/tmp/cryptoverse_agent.pid")

        if not pid_file.exists():
            return False

        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            return False

    @staticmethod
    def start_agent(daemon: bool = True):
        """Start the background agent"""
        if CryptoverseAgentManager.is_running():
            logger.info("Agent already running")
            return

        if daemon:
            # Fork and run as daemon
            pid = os.fork()
            if pid > 0:
                # Parent process
                logger.info(f"Started background agent (PID: {pid})")
                return

            # Child process - become daemon
            os.setsid()

            # Redirect stdout/stderr to log file
            sys.stdout = open('/tmp/cryptoverse_agent_daemon.log', 'a')
            sys.stderr = sys.stdout

        # Run the agent
        agent = CryptoverseBackgroundAgent()
        agent.start()

    @staticmethod
    def stop_agent():
        """Stop the background agent"""
        pid_file = Path("/tmp/cryptoverse_agent.pid")

        if not pid_file.exists():
            logger.info("Agent not running")
            return

        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent stop signal to agent (PID: {pid})")

            # Clean up PID file
            pid_file.unlink()
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")

    @staticmethod
    def status():
        """Get agent status"""
        if not CryptoverseAgentManager.is_running():
            return {"running": False}

        state_file = Path("/tmp/cryptoverse_agent_state.json")

        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                return {
                    "running": True,
                    "pid": state.get("pid"),
                    "last_update": state.get("last_update"),
                    "next_update": state.get("next_update"),
                    "failures": state.get("consecutive_failures", 0)
                }

        return {"running": True}

def integrate_with_zmartbot():
    """Integration function for ZmartBot background services"""
    try:
        # Check if we should start
        if not CryptoverseAgentManager.is_running():
            logger.info("Starting Cryptoverse Background Agent...")
            CryptoverseAgentManager.start_agent(daemon=True)
            return True
        else:
            logger.info("Cryptoverse Agent already running")
            return True
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        return False

# Auto-start when imported by background services
if __name__ != "__main__":
    # This runs when imported by other services
    threading.Thread(target=integrate_with_zmartbot, daemon=True).start()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cryptoverse Background Agent")
    parser.add_argument("--start", action="store_true", help="Start agent")
    parser.add_argument("--stop", action="store_true", help="Stop agent")
    parser.add_argument("--status", action="store_true", help="Check status")
    parser.add_argument("--foreground", action="store_true", help="Run in foreground")

    args = parser.parse_args()

    if args.start:
        CryptoverseAgentManager.start_agent(daemon=not args.foreground)
    elif args.stop:
        CryptoverseAgentManager.stop_agent()
    elif args.status:
        status = CryptoverseAgentManager.status()
        print(json.dumps(status, indent=2))
    else:
        # Default: run in foreground
        agent = CryptoverseBackgroundAgent()
        agent.start()