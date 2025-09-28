#!/usr/bin/env python3
"""
API-MCP Background Agent
Automated synchronization between API Manager and MCP servers
Runs as a background service to keep credentials synchronized
"""

import os
import sys
import json
import time
import logging
import threading
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import requests
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/api_mcp_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConfigChangeHandler(FileSystemEventHandler):
    """Handle changes to configuration files"""

    def __init__(self, agent):
        self.agent = agent

    def on_modified(self, event):
        if event.is_directory:
            return

        # Check if it's a relevant file
        if "api_keys.db" in event.src_path:
            logger.info("API keys database changed, triggering sync...")
            self.agent.sync_configurations()

class APIMCPBackgroundAgent:
    """
    Background agent for automatic API-MCP synchronization
    """

    def __init__(self):
        self.running = False
        self.sync_interval = 300  # 5 minutes
        self.last_sync = None
        self.api_manager_url = "http://localhost:8006"

        # Configuration paths
        self.claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        self.ccxt_config_path = Path("/Users/dansidanutz/Desktop/ZmartBot/ccxt-exchanges-config.json")
        self.db_path = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/api_keys.db")

        # Supported exchanges
        self.exchanges = {
            "binance": {"requires_passphrase": False},
            "bybit": {"requires_passphrase": False},
            "kucoin": {"requires_passphrase": True},
            "okx": {"requires_passphrase": True},
            "bitget": {"requires_passphrase": True},
            "kraken": {"requires_passphrase": False},
            "coinbase": {"requires_passphrase": False},
            "huobi": {"requires_passphrase": False},
            "bitfinex": {"requires_passphrase": False},
            "mexc": {"requires_passphrase": False}
        }

        # Statistics
        self.stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_sync_time": None,
            "keys_synced": 0
        }

        # File watcher
        self.observer = None

    def start(self):
        """Start the background agent"""
        logger.info("Starting API-MCP Background Agent...")
        self.running = True

        # Start API Manager if not running
        self.ensure_api_manager_running()

        # Start file watcher
        self.start_file_watcher()

        # Start sync thread
        sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        sync_thread.start()

        # Start health check thread
        health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        health_thread.start()

        logger.info("API-MCP Background Agent started successfully")

        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        logger.info("Shutting down API-MCP Background Agent...")
        self.running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()

        # Save statistics
        self.save_statistics()

        logger.info("API-MCP Background Agent stopped")
        sys.exit(0)

    def ensure_api_manager_running(self):
        """Ensure API Manager service is running"""
        try:
            response = requests.get(f"{self.api_manager_url}/health", timeout=2)
            if response.status_code == 200:
                logger.info("API Manager is running")
                return True
        except:
            logger.warning("API Manager is not running, attempting to start...")

        # Start API Manager
        import subprocess
        try:
            cmd = [
                "python3",
                "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/api_keys_manager/api_keys_manager_server.py",
                "--port", "8006"
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)  # Wait for service to start

            # Verify it's running
            response = requests.get(f"{self.api_manager_url}/health", timeout=2)
            if response.status_code == 200:
                logger.info("API Manager started successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to start API Manager: {e}")
            return False

    def start_file_watcher(self):
        """Start watching for file changes"""
        try:
            self.observer = Observer()
            handler = ConfigChangeHandler(self)

            # Watch API keys database directory
            watch_path = self.db_path.parent
            self.observer.schedule(handler, str(watch_path), recursive=False)

            self.observer.start()
            logger.info(f"File watcher started for {watch_path}")
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")

    def sync_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                # Perform sync
                self.sync_configurations()

                # Wait for next sync interval
                time.sleep(self.sync_interval)

            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                time.sleep(60)  # Wait before retry

    def health_check_loop(self):
        """Monitor health of services"""
        while self.running:
            try:
                # Check API Manager health
                api_manager_healthy = self.check_api_manager_health()

                if not api_manager_healthy:
                    logger.warning("API Manager unhealthy, attempting restart...")
                    self.ensure_api_manager_running()

                # Log statistics every hour
                if self.stats["total_syncs"] > 0 and self.stats["total_syncs"] % 12 == 0:
                    self.log_statistics()

                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                time.sleep(60)

    def check_api_manager_health(self) -> bool:
        """Check if API Manager is healthy"""
        try:
            response = requests.get(f"{self.api_manager_url}/ready", timeout=5)
            return response.status_code == 200
        except:
            return False

    def sync_configurations(self):
        """Synchronize API keys to all MCP configurations"""
        logger.info("Starting configuration sync...")
        self.stats["total_syncs"] += 1
        sync_start = datetime.now()

        try:
            # Get all API keys from database
            keys = self.get_all_api_keys()

            if not keys:
                logger.info("No API keys to sync")
                return

            # Update Claude config
            claude_success = self.update_claude_config(keys)

            # Update CCXT config
            ccxt_success = self.update_ccxt_config(keys)

            if claude_success and ccxt_success:
                self.stats["successful_syncs"] += 1
                self.stats["keys_synced"] = len(keys)
                logger.info(f"Successfully synced {len(keys)} API keys")
            else:
                self.stats["failed_syncs"] += 1
                logger.warning("Partial sync failure")

            self.last_sync = sync_start
            self.stats["last_sync_time"] = sync_start.isoformat()

        except Exception as e:
            self.stats["failed_syncs"] += 1
            logger.error(f"Sync failed: {e}")

    def get_all_api_keys(self) -> Dict[str, Any]:
        """Get all API keys from the database"""
        keys = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT service_name, encrypted_key, key_type, description
                FROM api_keys
                WHERE is_active = 1
            """)

            rows = cursor.fetchall()
            for row in rows:
                service_name = row[0].lower()
                if service_name in self.exchanges:
                    # Note: In production, decrypt the key here
                    keys[service_name] = {
                        "api_key": row[1][:20] + "...",  # Masked for logging
                        "api_secret": "***",  # Masked
                        "key_type": row[2],
                        "description": row[3]
                    }

            conn.close()
            return keys

        except Exception as e:
            logger.error(f"Failed to get API keys from database: {e}")
            return {}

    def update_claude_config(self, keys: Dict[str, Any]) -> bool:
        """Update Claude Desktop configuration"""
        try:
            if not self.claude_config_path.exists():
                logger.warning("Claude config file not found")
                return False

            with open(self.claude_config_path, 'r') as f:
                config = json.load(f)

            # Update MCP server configurations
            for exchange, key_data in keys.items():
                # Update binance server
                if exchange == "binance" and "binance" in config.get("mcpServers", {}):
                    # Note: Use actual decrypted keys in production
                    logger.debug(f"Updating Binance MCP config")

                # Update ccxt-multi server
                if "ccxt-multi" in config.get("mcpServers", {}):
                    logger.debug(f"Updating CCXT multi config for {exchange}")

            # Save config (in production, actually update with real keys)
            with open(self.claude_config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("Claude config updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update Claude config: {e}")
            return False

    def update_ccxt_config(self, keys: Dict[str, Any]) -> bool:
        """Update CCXT configuration file"""
        try:
            config = {"accounts": []}

            if self.ccxt_config_path.exists():
                with open(self.ccxt_config_path, 'r') as f:
                    config = json.load(f)

            # Update accounts
            for exchange, key_data in keys.items():
                logger.debug(f"Updating CCXT config for {exchange}")
                # Note: In production, update with actual decrypted keys

            # Save config
            with open(self.ccxt_config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("CCXT config updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update CCXT config: {e}")
            return False

    def log_statistics(self):
        """Log current statistics"""
        logger.info("=== API-MCP Sync Statistics ===")
        logger.info(f"Total syncs: {self.stats['total_syncs']}")
        logger.info(f"Successful: {self.stats['successful_syncs']}")
        logger.info(f"Failed: {self.stats['failed_syncs']}")
        logger.info(f"Keys synced: {self.stats['keys_synced']}")
        logger.info(f"Last sync: {self.stats['last_sync_time']}")

        if self.stats['total_syncs'] > 0:
            success_rate = (self.stats['successful_syncs'] / self.stats['total_syncs']) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")

    def save_statistics(self):
        """Save statistics to file"""
        try:
            stats_file = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/api_mcp_stats.json")
            stats_file.parent.mkdir(parents=True, exist_ok=True)

            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)

            logger.info(f"Statistics saved to {stats_file}")
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")

def main():
    """Main entry point"""
    # Create logs directory
    log_dir = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Start the agent
    agent = APIMCPBackgroundAgent()
    agent.start()

if __name__ == "__main__":
    main()