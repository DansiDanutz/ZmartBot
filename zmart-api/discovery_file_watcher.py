#!/usr/bin/env python3
"""
Discovery File Watcher - Efficient Trigger-Based System
Monitors for new .py and .mdc files and updates discovery database automatically
Much more efficient than full folder scanning
"""

import os
import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DiscoveryFileHandler(FileSystemEventHandler):
    """Handle file system events for .py and .mdc files"""
    
    def __init__(self):
        self.discovery_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
        self.mdc_rules_path = "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules"
        
    def on_created(self, event):
        """Handle new file creation"""
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith('.py') or file_path.endswith('.mdc'):
                print(f"🔍 New file detected: {file_path}")
                self.check_and_update_discovery(file_path)
    
    def on_modified(self, event):
        """Handle file modifications (for MDC files)"""
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith('.mdc'):
                print(f"🔄 MDC file updated: {file_path}")
                self.check_and_update_discovery(file_path)
    
    def check_and_update_discovery(self, file_path):
        """Check if new Python file has MDC and update discovery database"""
        try:
            if file_path.endswith('.py'):
                # New Python file - check if MDC exists
                service_name = Path(file_path).stem
                mdc_file_path = os.path.join(self.mdc_rules_path, f"{service_name}.mdc")
                
                if os.path.exists(mdc_file_path):
                    self.add_to_discovery_database(service_name, file_path, mdc_file_path)
                else:
                    print(f"  ❌ {service_name} - Python file created but no MDC file yet")
            
            elif file_path.endswith('.mdc'):
                # New MDC file - check if Python file exists
                service_name = Path(file_path).stem
                # Search for corresponding Python file in entire ZmartBot folder
                python_file_path = self.find_python_file(service_name)
                
                if python_file_path:
                    self.add_to_discovery_database(service_name, python_file_path, file_path)
                else:
                    print(f"  ❌ {service_name} - MDC file created but no Python file found")
        
        except Exception as e:
            print(f"❌ Error processing file {file_path}: {e}")
    
    def find_python_file(self, service_name):
        """Find Python file with given name in ZmartBot folder"""
        base_path = "/Users/dansidanutz/Desktop/ZmartBot"
        
        # Search for Python file with this name
        for root, dirs, files in os.walk(base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(excl in d for excl in ['venv', 'node_modules', '__pycache__', '.git'])]
            
            for file in files:
                if file == f"{service_name}.py":
                    return os.path.join(root, file)
        
        return None
    
    def add_to_discovery_database(self, service_name, python_file_path, mdc_file_path):
        """Add service to discovery database"""
        try:
            # Check if service has passport (exclude from discovery if it does)
            if self.has_passport(service_name):
                print(f"  ⏭️  {service_name} - Has passport, skipping discovery database")
                return
            
            # Add to discovery database
            conn = sqlite3.connect(self.discovery_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO discovery_services 
                (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path) 
                VALUES (?, ?, 'DISCOVERED', 1, 1, ?, ?)
            ''', (service_name, datetime.now(), python_file_path, mdc_file_path))
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ {service_name} - Added to discovery database")
            print(f"     Python: {python_file_path}")
            print(f"     MDC: {mdc_file_path}")
            
        except Exception as e:
            print(f"❌ Error adding {service_name} to discovery database: {e}")
    
    def has_passport(self, service_name):
        """Check if service has passport"""
        passport_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/passport_registry.db"
        
        if not os.path.exists(passport_db):
            return False
        
        try:
            conn = sqlite3.connect(passport_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE service_name = ? AND status = 'ACTIVE'", (service_name,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except:
            return False

def main():
    """Start the file watcher"""
    print("🚀 Starting Discovery File Watcher System")
    print("📁 Monitoring: /Users/dansidanutz/Desktop/ZmartBot/")
    print("📊 Database: discovery_registry.db")
    print("🔍 Watching for: .py and .mdc file changes")
    print("⚡ Trigger-based - NO SCANNING!")
    print("")
    
    # Create discovery database if it doesn't exist
    discovery_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
    if not os.path.exists(discovery_db):
        conn = sqlite3.connect(discovery_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discovery_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'DISCOVERED',
                has_mdc_file BOOLEAN DEFAULT 0,
                has_python_file BOOLEAN DEFAULT 1,
                python_file_path TEXT,
                mdc_file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Discovery database created")
    
    # Set up file watcher
    event_handler = DiscoveryFileHandler()
    observer = Observer()
    
    # Watch ZmartBot folder for Python files
    observer.schedule(event_handler, "/Users/dansidanutz/Desktop/ZmartBot/", recursive=True)
    
    # Watch .cursor/rules folder for MDC files
    observer.schedule(event_handler, "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/", recursive=False)
    
    observer.start()
    print("👁️  File watcher started - monitoring for new .py and .mdc files...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\\n⏹️  Discovery File Watcher stopped")
    
    observer.join()

if __name__ == "__main__":
    main()