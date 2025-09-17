#!/usr/bin/env python3
"""
YAML-Database Synchronization Fix System
Fixes the critical synchronization issue between YAML Governance System and Service Registry Database
"""

import sqlite3
import json
import os
import shutil
import requests
from pathlib import Path
from datetime import datetime
import yaml

class YAMLDatabaseSyncFix:
    def __init__(self):
        self.db_path = "src/data/service_registry.db"
        self.yaml_governance_url = "http://127.0.0.1:8897"
        self.backup_dir = Path("sync_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def get_database_services(self):
        """Get all services from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, certification_level, port, passport_id, status, 
                   kind, description, python_file_path, mdc_file_path
            FROM service_registry 
            ORDER BY service_name
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_name': row[0],
                'certification_level': row[1],
                'port': row[2],
                'passport_id': row[3],
                'status': row[4],
                'kind': row[5],
                'description': row[6],
                'python_file_path': row[7],
                'mdc_file_path': row[8]
            })
        
        conn.close()
        return services
        
    def get_yaml_services(self):
        """Get all services from YAML Governance System"""
        try:
            response = requests.get(f"{self.yaml_governance_url}/api/scan", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('files', [])
            else:
                print(f"YAML Governance Service not responding: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to YAML Governance Service: {e}")
            return []
    
    def create_backup(self):
        """Create backup of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"sync_backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup database
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, backup_path / "service_registry.db")
        
        # Backup YAML files
        yaml_backup_path = backup_path / "yaml_files"
        yaml_backup_path.mkdir(exist_ok=True)
        
        for yaml_file in Path(".").rglob("service.yaml"):
            # Skip backup directories to avoid recursion
            if "sync_backups" in yaml_file.parts or "orphaned_yaml_files" in yaml_file.parts:
                continue
            relative_path = yaml_file.relative_to(".")
            backup_file_path = yaml_backup_path / relative_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(yaml_file, backup_file_path)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def analyze_discrepancies(self):
        """Analyze discrepancies between systems"""
        db_services = self.get_database_services()
        yaml_services = self.get_yaml_services()
        
        db_names = {s['service_name'] for s in db_services}
        yaml_names = {s['service_name'] for s in yaml_services}
        
        # Find discrepancies
        only_in_db = db_names - yaml_names
        only_in_yaml = yaml_names - db_names
        synchronized = db_names & yaml_names
        
        print("\n📊 SYNCHRONIZATION ANALYSIS")
        print("=" * 50)
        print(f"Database services: {len(db_services)}")
        print(f"YAML services: {len(yaml_services)}")
        print(f"Synchronized: {len(synchronized)}")
        print(f"Only in database: {len(only_in_db)}")
        print(f"Only in YAML: {len(only_in_yaml)}")
        
        return {
            'db_services': db_services,
            'yaml_services': yaml_services,
            'only_in_db': only_in_db,
            'only_in_yaml': only_in_yaml,
            'synchronized': synchronized
        }
    
    def generate_service_yaml(self, service):
        """Generate service.yaml content for a database service"""
        yaml_content = {
            'service': {
                'name': service['service_name'],
                'type': service['kind'] or 'backend',
                'port': service['port'],
                'status': service['status'],
                'level': service['certification_level'],
                'passport': service['passport_id']
            },
            'metadata': {
                'description': service['description'] or f"Service {service['service_name']}",
                'version': '1.0.0',
                'owner': 'zmartbot'
            },
            'endpoints': {
                'health': f"http://127.0.0.1:{service['port']}/health" if service['port'] else None,
                'ready': f"http://127.0.0.1:{service['port']}/ready" if service['port'] else None,
                'metrics': f"http://127.0.0.1:{service['port']}/metrics" if service['port'] else None
            },
            'lifecycle': {
                'start_command': f"python3 {service['python_file_path']}" if service['python_file_path'] else None,
                'stop_command': f"pkill -f {service['service_name']}",
                'health_check': f"curl -f http://127.0.0.1:{service['port']}/health" if service['port'] else None
            }
        }
        return yaml_content
    
    def create_missing_yaml_files(self, analysis):
        """Create YAML files for services that only exist in database"""
        created_count = 0
        
        for service_name in analysis['only_in_db']:
            # Find the service details
            service = next(s for s in analysis['db_services'] if s['service_name'] == service_name)
            
            # Determine directory name (convert from database naming)
            dir_name = service_name.replace('-', '_').replace(' ', '_').lower()
            
            # Create service directory if it doesn't exist
            service_dir = Path(dir_name)
            if not service_dir.exists():
                service_dir.mkdir(exist_ok=True)
                print(f"📁 Created directory: {service_dir}")
            
            # Create service.yaml
            yaml_path = service_dir / "service.yaml"
            yaml_content = self.generate_service_yaml(service)
            
            with open(yaml_path, 'w') as f:
                yaml.dump(yaml_content, f, default_flow_style=False, indent=2)
            
            created_count += 1
            print(f"✅ Created YAML: {yaml_path}")
        
        print(f"\n📦 Created {created_count} missing YAML files")
        return created_count
    
    def cleanup_orphaned_yaml_files(self, analysis):
        """Clean up YAML files for services not in database"""
        cleaned_count = 0
        orphaned_dir = Path("orphaned_yaml_files")
        orphaned_dir.mkdir(exist_ok=True)
        
        for yaml_service in analysis['yaml_services']:
            if yaml_service['service_name'] in analysis['only_in_yaml']:
                yaml_path = Path(yaml_service['path'])
                if yaml_path.exists():
                    # Move to orphaned directory instead of deleting
                    orphaned_path = orphaned_dir / yaml_path.name.replace('.yaml', f'_{yaml_service["service_name"]}.yaml')
                    shutil.move(yaml_path, orphaned_path)
                    cleaned_count += 1
                    print(f"🗑️  Moved orphaned YAML: {yaml_path} -> {orphaned_path}")
        
        print(f"\n🧹 Moved {cleaned_count} orphaned YAML files to {orphaned_dir}")
        return cleaned_count
    
    def update_database_from_yaml(self, analysis):
        """Update database with services that only exist in YAML (if they're valid)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added_count = 0
        
        for yaml_service in analysis['yaml_services']:
            if yaml_service['service_name'] in analysis['only_in_yaml']:
                # Load YAML content to get service details
                yaml_path = Path(yaml_service['path'])
                if yaml_path.exists():
                    try:
                        with open(yaml_path, 'r') as f:
                            yaml_content = yaml.safe_load(f)
                        
                        service_config = yaml_content.get('service', {})
                        
                        # Insert into database with discovery status
                        cursor.execute("""
                            INSERT OR IGNORE INTO service_registry 
                            (service_name, kind, port, status, certification_level, description, passport_id)
                            VALUES (?, ?, ?, 'DISCOVERED', 1, ?, NULL)
                        """, (
                            yaml_service['service_name'],
                            service_config.get('type', 'backend'),
                            service_config.get('port'),
                            f"Service discovered from YAML file: {yaml_service['path']}"
                        ))
                        
                        if cursor.rowcount > 0:
                            added_count += 1
                            print(f"➕ Added to database: {yaml_service['service_name']}")
                    
                    except Exception as e:
                        print(f"❌ Error processing {yaml_path}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 Added {added_count} services to database from YAML files")
        return added_count
    
    def validate_synchronization(self):
        """Validate final synchronization"""
        analysis = self.analyze_discrepancies()
        
        if len(analysis['only_in_db']) == 0 and len(analysis['only_in_yaml']) == 0:
            print("\n✅ SYNCHRONIZATION SUCCESSFUL!")
            print(f"All {len(analysis['synchronized'])} services are now synchronized")
            return True
        else:
            print(f"\n⚠️  Synchronization incomplete:")
            print(f"Still {len(analysis['only_in_db'])} services only in database")
            print(f"Still {len(analysis['only_in_yaml'])} services only in YAML")
            return False
    
    def run_full_sync(self):
        """Run complete synchronization process"""
        print("🔄 YAML-Database Synchronization Fix")
        print("=" * 50)
        
        # Create backup
        backup_path = self.create_backup()
        
        # Analyze current state
        analysis = self.analyze_discrepancies()
        
        if len(analysis['only_in_db']) == 0 and len(analysis['only_in_yaml']) == 0:
            print("\n✅ Systems already synchronized!")
            return
        
        print(f"\n🔧 Starting synchronization...")
        
        # Step 1: Create missing YAML files
        created = self.create_missing_yaml_files(analysis)
        
        # Step 2: Add valid YAML-only services to database
        added = self.update_database_from_yaml(analysis)
        
        # Step 3: Clean up remaining orphaned YAML files
        cleaned = self.cleanup_orphaned_yaml_files(analysis)
        
        # Step 4: Validate final state
        success = self.validate_synchronization()
        
        print(f"\n📋 SYNCHRONIZATION SUMMARY")
        print("=" * 30)
        print(f"YAML files created: {created}")
        print(f"Database entries added: {added}")
        print(f"Orphaned files cleaned: {cleaned}")
        print(f"Backup location: {backup_path}")
        print(f"Status: {'✅ SUCCESS' if success else '⚠️ PARTIAL'}")
        
        return success

if __name__ == "__main__":
    sync_fix = YAMLDatabaseSyncFix()
    sync_fix.run_full_sync()