#!/usr/bin/env python3
"""
Cryptometer Background Agent
24-hour autonomous data collection system similar to RISKMETRIC background agent
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import time
import subprocess

# Add current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptometerBackgroundAgent:
    """
    Background agent for autonomous cryptometer data collection
    Runs forever with 24-hour update cycles
    """

    def __init__(self):
        self.running = False
        self.pid_file = Path('/tmp/cryptometer_background_agent.pid')
        self.status_file = Path('cryptometer_agent_status.json')
        self.last_update = None
        self.next_update = None
        self.update_interval_hours = 24  # 24-hour cycles
        self.session_count = 0

        # Signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def _create_pid_file(self):
        """Create PID file"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"PID file created: {self.pid_file}")
        except Exception as e:
            logger.warning(f"Could not create PID file: {e}")

    def _remove_pid_file(self):
        """Remove PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.info("PID file removed")
        except Exception as e:
            logger.warning(f"Could not remove PID file: {e}")

    async def _perform_cryptometer_update(self) -> bool:
        """Perform cryptometer update using autonomous system"""
        try:
            logger.info("🚀 Starting cryptometer autonomous update...")

            # Import and run autonomous system
            from cryptometer_autonomous_system import AutonomousCryptometerScraper, CryptometerConfig

            # Create config
            config = CryptometerConfig.from_env()

            # Create scraper
            scraper = AutonomousCryptometerScraper(config)

            # Run complete cycle
            success = await scraper.run_complete_autonomous_cycle()

            if success:
                logger.info("✅ Cryptometer autonomous update completed successfully")
                self._update_status('completed', scraper.session_stats)
                return True
            else:
                logger.error("❌ Cryptometer autonomous update failed")
                self._update_status('failed', scraper.session_stats)
                return False

        except Exception as e:
            logger.error(f"💥 Error in cryptometer update: {e}")
            self._update_status('error', {'error': str(e)})
            return False

    def _update_status(self, status: str, session_data: Dict[str, Any]):
        """Update agent status file"""
        try:
            status_data = {
                'agent': 'cryptometer_background',
                'status': status,
                'last_update': datetime.now().isoformat(),
                'next_update': (datetime.now() + timedelta(hours=self.update_interval_hours)).isoformat(),
                'session_count': self.session_count,
                'update_interval_hours': self.update_interval_hours,
                'running': self.running,
                'pid': os.getpid(),
                'session_data': session_data
            }

            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)

        except Exception as e:
            logger.warning(f"Could not update status file: {e}")

    async def run_forever(self):
        """Run background agent forever"""
        try:
            self._create_pid_file()
            self.running = True

            logger.info(f"🤖 Cryptometer background agent started (PID: {os.getpid()})")
            logger.info(f"⏰ Update interval: {self.update_interval_hours} hours")

            while self.running:
                try:
                    self.session_count += 1
                    logger.info(f"📊 Starting update session #{self.session_count}")

                    # Perform update
                    success = await self._perform_cryptometer_update()

                    self.last_update = datetime.now()
                    self.next_update = self.last_update + timedelta(hours=self.update_interval_hours)

                    if success:
                        logger.info(f"✅ Session #{self.session_count} completed. Next update: {self.next_update}")
                    else:
                        logger.error(f"❌ Session #{self.session_count} failed. Will retry at next interval.")

                    # Sleep until next update
                    sleep_seconds = self.update_interval_hours * 3600
                    logger.info(f"😴 Sleeping for {self.update_interval_hours} hours until next update...")

                    # Sleep with periodic status updates
                    for i in range(0, sleep_seconds, 60):  # Check every minute
                        if not self.running:
                            break
                        await asyncio.sleep(60)

                        # Update status every 10 minutes
                        if i % 600 == 0:
                            remaining_hours = (sleep_seconds - i) / 3600
                            logger.debug(f"💤 Sleeping... {remaining_hours:.1f} hours remaining")

                except Exception as e:
                    logger.error(f"💥 Error in update cycle: {e}")
                    # Sleep for 5 minutes before retrying
                    await asyncio.sleep(300)

        except Exception as e:
            logger.error(f"💥 Fatal error in background agent: {e}")
        finally:
            self.running = False
            self._update_status('stopped', {'stopped_at': datetime.now().isoformat()})
            self._remove_pid_file()
            logger.info("👋 Cryptometer background agent stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                return status
            else:
                return {
                    'agent': 'cryptometer_background',
                    'status': 'not_running',
                    'running': False
                }
        except Exception as e:
            return {
                'agent': 'cryptometer_background',
                'status': 'error',
                'error': str(e),
                'running': False
            }

    @staticmethod
    def is_running() -> bool:
        """Check if agent is already running"""
        pid_file = Path('/tmp/cryptometer_background_agent.pid')
        if not pid_file.exists():
            return False

        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # Process doesn't exist, remove stale PID file
                pid_file.unlink()
                return False
        except Exception:
            return False

    @staticmethod
    def stop_agent():
        """Stop running agent"""
        pid_file = Path('/tmp/cryptometer_background_agent.pid')
        if not pid_file.exists():
            logger.info("No PID file found - agent not running")
            return False

        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            logger.info(f"Stopping cryptometer agent (PID: {pid})")
            os.kill(pid, signal.SIGTERM)

            # Wait for graceful shutdown
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    logger.info("✅ Agent stopped successfully")
                    return True

            # Force kill if still running
            logger.warning("Force killing agent...")
            os.kill(pid, signal.SIGKILL)
            return True

        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
            return False

async def main():
    """Main function"""
    try:
        if len(sys.argv) < 2:
            print("Usage: python cryptometer_background_agent.py [start|stop|status|restart]")
            sys.exit(1)

        command = sys.argv[1].lower()

        if command == 'start':
            if CryptometerBackgroundAgent.is_running():
                logger.error("Cryptometer agent is already running")
                sys.exit(1)

            logger.info("Starting cryptometer background agent...")
            agent = CryptometerBackgroundAgent()
            await agent.run_forever()

        elif command == 'stop':
            success = CryptometerBackgroundAgent.stop_agent()
            sys.exit(0 if success else 1)

        elif command == 'status':
            agent = CryptometerBackgroundAgent()
            status = agent.get_status()
            print(json.dumps(status, indent=2))

        elif command == 'restart':
            logger.info("Restarting cryptometer agent...")
            CryptometerBackgroundAgent.stop_agent()
            time.sleep(2)

            if CryptometerBackgroundAgent.is_running():
                logger.error("Failed to stop agent for restart")
                sys.exit(1)

            agent = CryptometerBackgroundAgent()
            await agent.run_forever()

        else:
            print(f"Unknown command: {command}")
            print("Usage: python cryptometer_background_agent.py [start|stop|status|restart]")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("👋 Cryptometer agent interrupted by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())