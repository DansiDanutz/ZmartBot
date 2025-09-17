#!/usr/bin/env python3
"""
Service Cleanup System for ZmartBot
Identifies duplicates, cleans them up, and registers unique orphaned services
"""

import os
import sqlite3
import hashlib
import shutil
import logging
from pathlib import Path
from datetime import datetime
import schedule
import time
import json

class ServiceCleanupSystem:
    def __init__(self):
        self.project_root = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.zmart_api_path = self.project_root / "zmart-api"
        self.log_file = self.project_root / "logs" / "service_cleanup.log"
        self.backup_dir = self.project_root / "system_backups" / f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Setup logging
        self.setup_logging()
        
        # Database paths
        self.service_registry_db = self.zmart_api_path / "service_registry.db"
        self.port_registry_db = self.zmart_api_path / "data" / "port_registry.db"
        self.workflow_registry_db = self.zmart_api_path / "workflow_registry.db"
        self.discovery_registry_db = self.zmart_api_path / "discovery_registry.db"
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return None
            
    def get_registered_services(self):
        """Get all registered services from all registries"""
        registered_services = set()
        
        # From service registry (Level 3)
        if self.service_registry_db.exists():
            try:
                conn = sqlite3.connect(self.service_registry_db)
                cursor = conn.cursor()
                cursor.execute("SELECT service_name FROM services WHERE status = 'REGISTERED'")
                for row in cursor.fetchall():
                    registered_services.add(row[0])
                conn.close()
            except Exception as e:
                self.logger.error(f"Error reading service registry: {e}")
                
        # From port registry
        if self.port_registry_db.exists():
            try:
                conn = sqlite3.connect(self.port_registry_db)
                cursor = conn.cursor()
                cursor.execute("SELECT service_name FROM port_assignments")
                for row in cursor.fetchall():
                    registered_services.add(row[0])
                conn.close()
            except Exception as e:
                self.logger.error(f"Error reading port registry: {e}")
                
        # From workflow registry
        if self.workflow_registry_db.exists():
            try:
                conn = sqlite3.connect(self.workflow_registry_db)
                cursor = conn.cursor()
                cursor.execute("SELECT service_name FROM service_workflows")
                for row in cursor.fetchall():
                    registered_services.add(row[0])
                conn.close()
            except Exception as e:
                self.logger.error(f"Error reading workflow registry: {e}")
                
        return registered_services
        
    def find_python_service_files(self):
        """Find all Python service files"""
        service_files = []
        exclude_patterns = [
            "__pycache__", "venv", "env", "site-packages", 
            "lib/python", "node_modules", ".git"
        ]
        
        for root, dirs, files in os.walk(self.zmart_api_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    # Check if it's a service file
                    if any(keyword in file.lower() for keyword in ['service', 'server', 'main', 'app', 'api', 'agent', 'manager', 'orchestration']):
                        service_files.append(file_path)
                        
        return service_files
        
    def identify_duplicates(self, service_files):
        """Identify duplicate files based on content hash"""
        hash_map = {}
        duplicates = []
        
        for file_path in service_files:
            file_hash = self.get_file_hash(file_path)
            if file_hash:
                if file_hash in hash_map:
                    duplicates.append({
                        'original': hash_map[file_hash],
                        'duplicate': file_path,
                        'hash': file_hash
                    })
                else:
                    hash_map[file_hash] = file_path
                    
        return duplicates, hash_map
        
    def backup_file(self, file_path):
        """Backup a file before deletion"""
        try:
            relative_path = file_path.relative_to(self.zmart_api_path)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            self.logger.error(f"Error backing up {file_path}: {e}")
            return None
            
    def clean_duplicates(self, duplicates):
        """Clean up duplicate files"""
        cleaned_count = 0
        
        for dup in duplicates:
            original = dup['original']
            duplicate = dup['duplicate']
            
            try:
                # Backup the duplicate
                backup_path = self.backup_file(duplicate)
                if backup_path:
                    # Remove the duplicate
                    duplicate.unlink()
                    cleaned_count += 1
                    self.logger.info(f"Cleaned duplicate: {duplicate} -> backed up to {backup_path}")
                else:
                    self.logger.warning(f"Failed to backup {duplicate}, skipping deletion")
                    
            except Exception as e:
                self.logger.error(f"Error cleaning duplicate {duplicate}: {e}")
                
        return cleaned_count
        
    def normalize_service_name(self, file_path):
        """Normalize service name from file path"""
        # Remove .py extension and zmart-api/ prefix
        name = file_path.relative_to(self.zmart_api_path).with_suffix('')
        
        # Convert to string and normalize separators
        name = str(name).replace('/', '-').replace('_', '-')
        
        # Remove common prefixes/suffixes
        name = name.replace('-server', '').replace('-service', '').replace('-agent', '')
        
        return name
        
    def register_to_discovery(self, service_files, registered_services):
        """Register unique orphaned services to discovery registry"""
        registered_count = 0
        
        # Ensure discovery registry exists
        if not self.discovery_registry_db.exists():
            self.create_discovery_registry()
            
        try:
            conn = sqlite3.connect(self.discovery_registry_db)
            cursor = conn.cursor()
            
            for file_path in service_files:
                service_name = self.normalize_service_name(file_path)
                
                # Skip if already registered
                if service_name in registered_services:
                    continue
                    
                # Check if already in discovery registry
                cursor.execute("SELECT id FROM discovery_services WHERE service_name = ?", (service_name,))
                if cursor.fetchone():
                    continue
                    
                # Register to discovery
                cursor.execute("""
                    INSERT INTO discovery_services 
                    (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    service_name,
                    datetime.now().isoformat(),
                    'DISCOVERED',
                    0,  # No MDC file initially
                    1,  # Has Python file
                    str(file_path.relative_to(self.zmart_api_path))
                ))
                
                registered_count += 1
                self.logger.info(f"Registered to discovery: {service_name}")
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registering to discovery: {e}")
            
        return registered_count
        
    def create_discovery_registry(self):
        """Create discovery registry if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.discovery_registry_db)
            cursor = conn.cursor()
            
            cursor.execute("""
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
            """)
            
            conn.commit()
            conn.close()
            self.logger.info("Created discovery registry")
            
        except Exception as e:
            self.logger.error(f"Error creating discovery registry: {e}")
            
    def generate_cleanup_report(self, duplicates, cleaned_count, registered_count, total_files):
        """Generate cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_service_files': total_files,
            'duplicates_found': len(duplicates),
            'duplicates_cleaned': cleaned_count,
            'services_registered_to_discovery': registered_count,
            'duplicate_details': [
                {
                    'original': str(dup['original']),
                    'duplicate': str(dup['duplicate']),
                    'hash': dup['hash']
                } for dup in duplicates
            ]
        }
        
        report_file = self.backup_dir / "cleanup_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Cleanup report saved to: {report_file}")
        return report
        
    def run_cleanup(self):
        """Run the complete cleanup process"""
        self.logger.info("Starting service cleanup process...")
        
        try:
            # Step 1: Find all Python service files
            self.logger.info("Finding Python service files...")
            service_files = self.find_python_service_files()
            self.logger.info(f"Found {len(service_files)} Python service files")
            
            # Step 2: Get registered services
            self.logger.info("Getting registered services...")
            registered_services = self.get_registered_services()
            self.logger.info(f"Found {len(registered_services)} registered services")
            
            # Step 3: Identify duplicates
            self.logger.info("Identifying duplicates...")
            duplicates, hash_map = self.identify_duplicates(service_files)
            self.logger.info(f"Found {len(duplicates)} duplicate files")
            
            # Step 4: Clean duplicates
            self.logger.info("Cleaning duplicates...")
            cleaned_count = self.clean_duplicates(duplicates)
            self.logger.info(f"Cleaned {cleaned_count} duplicate files")
            
            # Step 5: Get remaining unique files
            unique_files = [f for f in service_files if f.exists()]  # Remove cleaned duplicates
            orphaned_files = [f for f in unique_files if self.normalize_service_name(f) not in registered_services]
            
            # Step 6: Register orphaned services to discovery
            self.logger.info("Registering orphaned services to discovery...")
            registered_count = self.register_to_discovery(orphaned_files, registered_services)
            self.logger.info(f"Registered {registered_count} services to discovery")
            
            # Step 7: Generate report
            report = self.generate_cleanup_report(duplicates, cleaned_count, registered_count, len(service_files))
            
            # Step 8: Log final statistics
            self.logger.info("=== CLEANUP COMPLETE ===")
            self.logger.info(f"Total service files processed: {len(service_files)}")
            self.logger.info(f"Duplicates found and cleaned: {cleaned_count}")
            self.logger.info(f"New services registered to discovery: {registered_count}")
            self.logger.info(f"Backup location: {self.backup_dir}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return None
            
    def schedule_cleanup(self):
        """Schedule cleanup to run every hour"""
        schedule.every().hour.do(self.run_cleanup)
        
        self.logger.info("Service cleanup scheduled to run every hour")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function"""
    cleanup_system = ServiceCleanupSystem()
    
    # Run cleanup once
    report = cleanup_system.run_cleanup()
    
    if report:
        print("=== CLEANUP COMPLETE ===")
        print(f"Total service files: {report['total_service_files']}")
        print(f"Duplicates cleaned: {report['duplicates_cleaned']}")
        print(f"Services registered to discovery: {report['services_registered_to_discovery']}")
        print(f"Backup location: {cleanup_system.backup_dir}")
        
        # Ask if user wants to schedule hourly cleanup
        response = input("\nSchedule hourly cleanup? (y/n): ")
        if response.lower() == 'y':
            print("Starting scheduled cleanup (Ctrl+C to stop)...")
            cleanup_system.schedule_cleanup()

if __name__ == "__main__":
    main()
