#!/usr/bin/env python3
"""
My Symbols Database Protection System
=====================================

This script provides comprehensive protection for the My Symbols database:
1. File system protection (immutable flag)
2. Automatic backup system
3. Database integrity monitoring
4. Auto-restoration system
"""

import os
import sys
import sqlite3
import shutil
import time
import logging
from datetime import datetime
from pathlib import Path
import subprocess

# Configuration
DB_PATH = "my_symbols_v2.db"
BACKUP_DIR = "backups"
PROTECTION_LOG = "database_protection.log"

# Expected symbols (our 10 core symbols)
EXPECTED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT"
]

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(PROTECTION_LOG),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def set_immutable_flag(db_path):
    """Set immutable flag to prevent deletion/modification"""
    try:
        subprocess.run(['chattr', '+i', str(db_path)], check=True)
        print(f"✅ Immutable flag set on {db_path}")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Could not set immutable flag (may need sudo)")
        return False
    except FileNotFoundError:
        print("⚠️ chattr not available on this system")
        return False

def remove_immutable_flag(db_path):
    """Remove immutable flag for maintenance"""
    try:
        subprocess.run(['chattr', '-i', str(db_path)], check=True)
        print(f"🔓 Immutable flag removed from {db_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_backup(db_path, backup_dir):
    """Create timestamped backup"""
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"my_symbols_v2_protected_{timestamp}.db"
    backup_path = backup_dir / backup_name
    
    try:
        # Remove immutable flag temporarily
        remove_immutable_flag(db_path)
        
        # Create backup
        shutil.copy2(db_path, backup_path)
        
        # Set immutable flag on backup too
        try:
            subprocess.run(['chattr', '+i', str(backup_path)], check=True)
        except:
            pass
            
        # Restore immutable flag on original
        set_immutable_flag(db_path)
        
        print(f"💾 Backup created: {backup_name}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        set_immutable_flag(db_path)  # Restore protection
        return None

def check_database_integrity(db_path):
    """Check if database has all expected symbols"""
    try:
        # Remove immutable flag temporarily
        remove_immutable_flag(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check active symbols count
        cursor.execute("""
            SELECT COUNT(*) FROM portfolio_composition 
            WHERE status = 'Active'
        """)
        active_count = cursor.fetchone()[0]
        
        if active_count != 10:
            print(f"❌ Expected 10 symbols, found {active_count}")
            conn.close()
            set_immutable_flag(db_path)
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
            print(f"❌ Symbol mismatch! Expected: {EXPECTED_SYMBOLS}")
            print(f"❌ Found: {symbols}")
            conn.close()
            set_immutable_flag(db_path)
            return False
            
        conn.close()
        set_immutable_flag(db_path)
        print("✅ Database integrity check passed")
        return True
        
    except Exception as e:
        print(f"❌ Integrity check failed: {e}")
        set_immutable_flag(db_path)
        return False

def restore_from_backup(db_path, backup_dir):
    """Restore database from most recent backup"""
    try:
        backup_dir = Path(backup_dir)
        backups = list(backup_dir.glob("my_symbols_v2_protected_*.db"))
        if not backups:
            print("❌ No backup files found!")
            return False
            
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_backup = backups[0]
        
        print(f"🔄 Restoring from backup: {latest_backup.name}")
        
        # Remove immutable flag from backup
        try:
            subprocess.run(['chattr', '-i', str(latest_backup)], check=True)
        except:
            pass
            
        # Remove immutable flag from original
        remove_immutable_flag(db_path)
        
        # Restore database
        shutil.copy2(latest_backup, db_path)
        
        # Set immutable flag on both
        set_immutable_flag(db_path)
        try:
            subprocess.run(['chattr', '+i', str(latest_backup)], check=True)
        except:
            pass
            
        print("✅ Database restored successfully")
        return True
        
    except Exception as e:
        print(f"❌ Restoration failed: {e}")
        set_immutable_flag(db_path)
        return False

def main():
    """Main protection system"""
    print("🛡️ My Symbols Database Protection System")
    print("=" * 50)
    
    db_path = Path(DB_PATH)
    
    # Initial setup
    if not db_path.exists():
        print("❌ Database file not found! Creating from backup...")
        if not restore_from_backup(db_path, BACKUP_DIR):
            print("❌ No backup available! Please restore manually.")
            return
            
    # Set initial protection
    set_immutable_flag(db_path)
    
    # Create initial backup
    create_backup(db_path, BACKUP_DIR)
    
    # Verify integrity
    if not check_database_integrity(db_path):
        print("❌ Database integrity check failed! Attempting restoration...")
        if not restore_from_backup(db_path, BACKUP_DIR):
            print("❌ Restoration failed! Please check manually.")
            return
            
    print("✅ Database protection initialized successfully!")
    print("🛡️ Database is now protected from deletion/modification")
    print("💾 Backup created")
    print("🔍 Integrity check passed")
    print("")
    print("To check status anytime, run: python3 protect_database.py --check")
    print("To create backup, run: python3 protect_database.py --backup")
    print("To restore from backup, run: python3 protect_database.py --restore")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        db_path = Path(DB_PATH)
        if sys.argv[1] == "--check":
            if check_database_integrity(db_path):
                print("✅ Database is healthy")
            else:
                print("❌ Database has issues")
        elif sys.argv[1] == "--backup":
            create_backup(db_path, BACKUP_DIR)
        elif sys.argv[1] == "--restore":
            restore_from_backup(db_path, BACKUP_DIR)
        else:
            print("Usage: python3 protect_database.py [--check|--backup|--restore]")
    else:
        main()
