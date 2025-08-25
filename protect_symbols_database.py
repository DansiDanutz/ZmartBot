#!/usr/bin/env python3
"""
My Symbols Database Protection System
=====================================

This script provides comprehensive protection for the My Symbols database:
1. File system protection (immutable flag)
2. Automatic backup system
3. Database integrity monitoring
4. Auto-restoration system
5. Write protection during critical operations
"""

import os
import sys
import sqlite3
import shutil
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import threading
import signal

# Configuration
DB_PATH = "my_symbols_v2.db"
BACKUP_DIR = "backups"
PROTECTION_LOG = "database_protection.log"
INTEGRITY_CHECK_INTERVAL = 300  # 5 minutes
BACKUP_INTERVAL = 3600  # 1 hour
MAX_BACKUPS = 10

# Expected symbols (our 10 core symbols)
EXPECTED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT"
]

class DatabaseProtector:
    def __init__(self):
        self.db_path = Path(DB_PATH)
        self.backup_dir = Path(BACKUP_DIR)
        self.backup_dir.mkdir(exist_ok=True)
        self.setup_logging()
        self.protection_active = False
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(PROTECTION_LOG),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def set_immutable_flag(self):
        """Set immutable flag to prevent deletion/modification"""
        try:
            # Set immutable flag (chattr +i)
            subprocess.run(['chattr', '+i', str(self.db_path)], check=True)
            self.logger.info(f"✅ Immutable flag set on {self.db_path}")
            return True
        except subprocess.CalledProcessError:
            self.logger.warning("⚠️ Could not set immutable flag (may need sudo)")
            return False
        except FileNotFoundError:
            self.logger.warning("⚠️ chattr not available on this system")
            return False
            
    def remove_immutable_flag(self):
        """Remove immutable flag for maintenance"""
        try:
            subprocess.run(['chattr', '-i', str(self.db_path)], check=True)
            self.logger.info(f"🔓 Immutable flag removed from {self.db_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def create_backup(self, suffix=""):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"my_symbols_v2_protected_{timestamp}{suffix}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Remove immutable flag temporarily for backup
            self.remove_immutable_flag()
            
            # Create backup
            shutil.copy2(self.db_path, backup_path)
            
            # Set immutable flag on backup too
            try:
                subprocess.run(['chattr', '+i', str(backup_path)], check=True)
            except:
                pass
                
            # Restore immutable flag on original
            self.set_immutable_flag()
            
            self.logger.info(f"💾 Backup created: {backup_name}")
            return backup_path
        except Exception as e:
            self.logger.error(f"❌ Backup failed: {e}")
            self.set_immutable_flag()  # Restore protection
            return None
            
    def check_database_integrity(self):
        """Check if database has all expected symbols"""
        try:
            # Remove immutable flag temporarily
            self.remove_immutable_flag()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if portfolio_composition table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='portfolio_composition'
            """)
            if not cursor.fetchone():
                self.logger.error("❌ portfolio_composition table missing!")
                conn.close()
                self.set_immutable_flag()
                return False
                
            # Check active symbols count
            cursor.execute("""
                SELECT COUNT(*) FROM portfolio_composition 
                WHERE status = 'Active'
            """)
            active_count = cursor.fetchone()[0]
            
            if active_count != 10:
                self.logger.error(f"❌ Expected 10 symbols, found {active_count}")
                conn.close()
                self.set_immutable_flag()
                return False
                
            # Check specific symbols
            cursor.execute("""
                SELECT s.symbol FROM portfolio_composition pc 
                JOIN symbols s ON pc.symbol_id = s.id 
                WHERE pc.status = 'Active' 
                ORDER BY pc.position_rank
            """)
            symbols = [row[0] for row in cursor.fetchall()]
            
            if symbols != EXPECTED_SYMBOLS:
                self.logger.error(f"❌ Symbol mismatch! Expected: {EXPECTED_SYMBOLS}")
                self.logger.error(f"❌ Found: {symbols}")
                conn.close()
                self.set_immutable_flag()
                return False
                
            conn.close()
            self.set_immutable_flag()
            self.logger.info("✅ Database integrity check passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Integrity check failed: {e}")
            self.set_immutable_flag()
            return False
            
    def restore_from_backup(self):
        """Restore database from most recent backup"""
        try:
            # Find most recent backup
            backups = list(self.backup_dir.glob("my_symbols_v2_protected_*.db"))
            if not backups:
                self.logger.error("❌ No backup files found!")
                return False
                
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            latest_backup = backups[0]
            
            self.logger.info(f"🔄 Restoring from backup: {latest_backup.name}")
            
            # Remove immutable flag from backup
            try:
                subprocess.run(['chattr', '-i', str(latest_backup)], check=True)
            except:
                pass
                
            # Remove immutable flag from original
            self.remove_immutable_flag()
            
            # Restore database
            shutil.copy2(latest_backup, self.db_path)
            
            # Set immutable flag on both
            self.set_immutable_flag()
            try:
                subprocess.run(['chattr', '+i', str(latest_backup)], check=True)
            except:
                pass
                
            self.logger.info("✅ Database restored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Restoration failed: {e}")
            self.set_immutable_flag()
            return False
            
    def cleanup_old_backups(self):
        """Keep only the most recent backups"""
        try:
            backups = list(self.backup_dir.glob("my_symbols_v2_protected_*.db"))
            if len(backups) <= MAX_BACKUPS:
                return
                
            # Sort by modification time
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for backup in backups[MAX_BACKUPS:]:
                try:
                    subprocess.run(['chattr', '-i', str(backup)], check=True)
                except:
                    pass
                backup.unlink()
                self.logger.info(f"🗑️ Removed old backup: {backup.name}")
                
        except Exception as e:
            self.logger.error(f"❌ Backup cleanup failed: {e}")
            
    def start_protection_monitor(self):
        """Start continuous protection monitoring"""
        self.protection_active = True
        self.logger.info("🛡️ Starting database protection monitor...")
        
        def monitor_loop():
            while self.protection_active:
                try:
                    # Check if database exists
                    if not self.db_path.exists():
                        self.logger.error("❌ Database file missing! Attempting restoration...")
                        if self.restore_from_backup():
                            self.logger.info("✅ Database restored from backup")
                        else:
                            self.logger.error("❌ Restoration failed!")
                            
                    # Check integrity
                    if not self.check_database_integrity():
                        self.logger.error("❌ Database integrity check failed! Attempting restoration...")
                        if self.restore_from_backup():
                            self.logger.info("✅ Database restored from backup")
                        else:
                            self.logger.error("❌ Restoration failed!")
                            
                    # Create periodic backup
                    if time.time() % BACKUP_INTERVAL < 60:  # Within 1 minute of interval
                        self.create_backup()
                        self.cleanup_old_backups()
                        
                    time.sleep(INTEGRITY_CHECK_INTERVAL)
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Protection monitor stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Monitor error: {e}")
                    time.sleep(60)  # Wait before retrying
                    
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
    def stop_protection(self):
        """Stop protection monitoring"""
        self.protection_active = False
        self.logger.info("🛑 Database protection stopped")
        
    def emergency_restore(self):
        """Emergency restoration procedure"""
        self.logger.info("🚨 EMERGENCY RESTORATION INITIATED")
        
        # Create emergency backup of current state
        if self.db_path.exists():
            self.create_backup("_emergency")
            
        # Attempt restoration
        if self.restore_from_backup():
            self.logger.info("✅ Emergency restoration successful")
            return True
        else:
            self.logger.error("❌ Emergency restoration failed")
            return False
            
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
            self.stop_protection()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main protection system"""
    protector = DatabaseProtector()
    protector.setup_signal_handlers()
    
    print("🛡️ My Symbols Database Protection System")
    print("=" * 50)
    
    # Initial setup
    if not protector.db_path.exists():
        print("❌ Database file not found! Creating from backup...")
        if not protector.restore_from_backup():
            print("❌ No backup available! Please restore manually.")
            return
            
    # Set initial protection
    protector.set_immutable_flag()
    
    # Create initial backup
    protector.create_backup("_initial")
    
    # Verify integrity
    if not protector.check_database_integrity():
        print("❌ Database integrity check failed! Attempting restoration...")
        if not protector.restore_from_backup():
            print("❌ Restoration failed! Please check manually.")
            return
            
    print("✅ Database protection initialized successfully!")
    print("🛡️ Database is now protected from deletion/modification")
    print("💾 Automatic backups will be created every hour")
    print("🔍 Integrity checks will run every 5 minutes")
    print("🔄 Auto-restoration will occur if issues are detected")
    print("\nPress Ctrl+C to stop protection...")
    
    # Start continuous protection
    protector.start_protection_monitor()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        protector.stop_protection()

if __name__ == "__main__":
    main()
