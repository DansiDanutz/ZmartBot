#!/usr/bin/env python3
"""
Complete YAML-Database Synchronization Fix
Achieves 100% synchronization by handling all naming convention mismatches
"""

import sqlite3
import json
import os
import shutil
import requests
from pathlib import Path
from datetime import datetime
import yaml

class CompleteSyncFix:
    def __init__(self):
        self.db_path = "src/data/service_registry.db"
        self.yaml_governance_url = "http://127.0.0.1:8897"
        
        # Naming convention mapping: database_name -> directory_name
        self.naming_map = {
            # Hyphen to underscore conversions
            'binance-worker': 'binance_worker',
            'live-alerts': 'live_alerts',
            'maradona-alerts': 'maradona_alerts', 
            'messi-alerts': 'messi_alerts',
            'pele-alerts': 'pele_alerts',
            'whale-alerts': 'whale_alerts',
            'registration-service': 'registration_service',
            'enhanced-mdc-monitor': 'enhanced_mdc_monitor',
            'kingfisher-ai': 'kingfisher_ai',
            'ziva-agent': 'ziva_agent',
            
            # PascalCase to lowercase conversions
            'OrchestrationStart': 'orchestrationstart',
            'RegistryConsolidator': 'registryconsolidator', 
            'YAMLGovernanceService': 'yamlgovernanceservice',
            'YAMLMonitoringDaemon': 'yamlmonitoringdaemon',
            'TradingStrategy': 'tradingstrategy',
            
            # Keep existing names for services already correct
            'achievements': 'achievements',
            'certification': 'certification',
            'zmart_alert_system': 'zmart_alert_system',
            'zmart_analytics': 'zmart_analytics',
            'zmart_backtesting': 'zmart_backtesting',
            'zmart_data_warehouse': 'zmart_data_warehouse', 
            'zmart_machine_learning': 'zmart_machine_learning',
            'zmart_risk_management': 'zmart_risk_management',
            'zmart_technical_analysis': 'zmart_technical_analysis'
        }
        
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
    
    def fix_missing_yaml_files(self, only_in_db):
        """Create YAML files for services only in database, using correct naming"""
        created_count = 0
        
        # Get full service details
        db_services = self.get_database_services()
        service_map = {s['service_name']: s for s in db_services}
        
        for service_name in only_in_db:
            service = service_map[service_name]
            
            # Determine correct directory name using naming map
            dir_name = self.naming_map.get(service_name, service_name.lower())
            
            # Create service directory if it doesn't exist
            service_dir = Path(dir_name)
            if not service_dir.exists():
                service_dir.mkdir(exist_ok=True)
                print(f"📁 Created directory: {service_dir}")
            
            # Create service.yaml
            yaml_path = service_dir / "service.yaml"
            if not yaml_path.exists():  # Only create if doesn't exist
                yaml_content = self.generate_service_yaml(service)
                
                with open(yaml_path, 'w') as f:
                    yaml.dump(yaml_content, f, default_flow_style=False, indent=2)
                
                created_count += 1
                print(f"✅ Created YAML: {yaml_path} for {service_name}")
            else:
                print(f"⏭️  YAML already exists: {yaml_path} for {service_name}")
        
        return created_count
    
    def fix_unknown_yaml_service(self):
        """Remove or fix the 'unknown' service in YAML"""
        yaml_services = self.get_yaml_services()
        
        for yaml_service in yaml_services:
            if yaml_service['service_name'] == 'unknown':
                yaml_path = Path(yaml_service['path'])
                if yaml_path.exists():
                    # Check if it's a malformed YAML file
                    try:
                        with open(yaml_path, 'r') as f:
                            content = f.read()
                        print(f"🔍 Found unknown service YAML: {yaml_path}")
                        print(f"Content preview: {content[:200]}...")
                        
                        # Move to orphaned files
                        orphaned_dir = Path("orphaned_yaml_files")
                        orphaned_dir.mkdir(exist_ok=True)
                        orphaned_path = orphaned_dir / f"unknown_service_{yaml_path.name}"
                        shutil.move(yaml_path, orphaned_path)
                        print(f"🗑️  Moved unknown YAML: {yaml_path} -> {orphaned_path}")
                        return 1
                        
                    except Exception as e:
                        print(f"❌ Error processing unknown YAML {yaml_path}: {e}")
        return 0
    
    def update_database_naming(self):
        """Update database service names to match YAML naming conventions if needed"""
        # This would require careful analysis - for now, we'll create YAML files
        # to match database names rather than changing database
        pass
    
    def run_complete_fix(self):
        """Run complete 100% synchronization fix"""
        print("🚀 COMPLETE YAML-DATABASE SYNCHRONIZATION (100%)")
        print("=" * 60)
        
        # Get current analysis
        db_services = self.get_database_services()
        yaml_services = self.get_yaml_services()
        
        db_names = {s['service_name'] for s in db_services}
        yaml_names = {s['service_name'] for s in yaml_services}
        
        only_in_db = db_names - yaml_names
        only_in_yaml = yaml_names - db_names
        synchronized = db_names & yaml_names
        
        print(f"📊 CURRENT STATE:")
        print(f"Database services: {len(db_services)}")
        print(f"YAML services: {len(yaml_services)}")
        print(f"Synchronized: {len(synchronized)}")
        print(f"Missing YAML: {len(only_in_db)}")
        print(f"Unknown YAML: {len(only_in_yaml)}")
        
        # Fix missing YAML files with correct naming
        created = self.fix_missing_yaml_files(only_in_db)
        print(f"\n✅ Created {created} missing YAML files")
        
        # Fix unknown YAML services
        removed = self.fix_unknown_yaml_service()
        print(f"✅ Removed {removed} unknown YAML files")
        
        # Validate final state
        print("\n🔍 VALIDATING FINAL STATE...")
        
        # Re-analyze after fixes
        yaml_services_new = self.get_yaml_services()
        yaml_names_new = {s['service_name'] for s in yaml_services_new}
        
        synchronized_new = db_names & yaml_names_new
        only_in_db_new = db_names - yaml_names_new
        only_in_yaml_new = yaml_names_new - db_names
        
        print(f"\n📈 FINAL RESULTS:")
        print(f"Database services: {len(db_services)}")
        print(f"YAML services: {len(yaml_services_new)}")
        print(f"Synchronized: {len(synchronized_new)} ({len(synchronized_new)/len(db_services)*100:.1f}%)")
        print(f"Missing YAML: {len(only_in_db_new)}")
        print(f"Unknown YAML: {len(only_in_yaml_new)}")
        
        success = len(only_in_db_new) == 0 and len(only_in_yaml_new) == 0
        
        if success:
            print(f"\n🎉 100% SYNCHRONIZATION ACHIEVED!")
            print(f"All {len(db_services)} services are now perfectly synchronized!")
        else:
            print(f"\n⚠️  Synchronization incomplete:")
            if only_in_db_new:
                print(f"Still missing YAML files for: {', '.join(list(only_in_db_new)[:5])}")
            if only_in_yaml_new:
                print(f"Still have unknown YAML files for: {', '.join(list(only_in_yaml_new)[:5])}")
        
        return success

if __name__ == "__main__":
    fix = CompleteSyncFix()
    fix.run_complete_fix()