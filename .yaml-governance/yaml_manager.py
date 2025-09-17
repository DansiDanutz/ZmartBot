#!/usr/bin/env python3
"""
YAML Manager - Centralized YAML Configuration Management
Created: 2025-08-31
Purpose: Manage, create, and maintain YAML configurations with governance
Level: 2 (Production Ready)
Port: N/A (Library Component)
Passport: YAML-MANAGER-LIB-L2
Owner: zmartbot-system
Status: LIBRARY
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

class YAMLManager:
    """Centralized YAML configuration management system"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.governance_dir = self.root_dir / ".yaml-governance"
        self.registry_file = self.governance_dir / "yaml_registry.json"
        self.database_file = self.root_dir / "GOODDatabase.db"
        self.templates_dir = self.governance_dir / "templates"
        
        # Ensure directories exist
        self.governance_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
    def create_service_templates(self):
        """Create YAML templates for different service types"""
        templates = {
            "backend": {
                "service_name": "[SERVICE_NAME]",
                "service_type": "backend",
                "version": "1.0.0", 
                "owner": "zmartbot",
                "description": "[SERVICE_DESCRIPTION]",
                "port": "[PORT]",
                "passport_id": "[PASSPORT_ID]",
                "status": "ACTIVE",
                "registered_at": "[DATE]",
                "health_url": "http://localhost:[PORT]/health",
                "start_cmd": "python3 [SERVICE_NAME]_server.py --port [PORT]",
                "stop_cmd": "pkill -f '[SERVICE_NAME]_server.py'",
                "dependencies": ["zmart-api"],
                "tags": ["backend", "[SERVICE_NAME]"],
                "lifecycle": {
                    "startup_grace_seconds": 30,
                    "shutdown_timeout_seconds": 15,
                    "health_check_interval": 30
                },
                "monitoring": {
                    "metrics_endpoint": "/metrics",
                    "logs_path": "logs/[SERVICE_NAME].log",
                    "dashboard_url": "http://localhost:[PORT]/dashboard"
                },
                "security": {
                    "cors_enabled": True,
                    "token_required": False,
                    "scopes": ["backend"]
                }
            },
            "alert_system": {
                "service_name": "[SERVICE_NAME]",
                "service_type": "alert_system",
                "version": "1.0.0",
                "owner": "zmartbot", 
                "description": "[SERVICE_NAME] alert system for ZmartBot platform",
                "port": "[PORT]",
                "passport_id": "[PASSPORT_ID]",
                "status": "ACTIVE",
                "registered_at": "[DATE]",
                "health_url": "http://localhost:[PORT]/health",
                "start_cmd": "python3 [SERVICE_NAME]_alerts.py --port [PORT]",
                "stop_cmd": "pkill -f '[SERVICE_NAME]_alerts.py'",
                "dependencies": ["zmart-api", "zmart-websocket"],
                "tags": ["alerts", "[SERVICE_NAME]"],
                "alert_config": {
                    "notification_channels": ["webhook", "websocket"],
                    "severity_levels": ["low", "medium", "high", "critical"],
                    "rate_limits": {
                        "max_alerts_per_minute": 60,
                        "cooldown_seconds": 5
                    }
                },
                "lifecycle": {
                    "startup_grace_seconds": 15,
                    "shutdown_timeout_seconds": 10,
                    "health_check_interval": 15
                },
                "monitoring": {
                    "metrics_endpoint": "/metrics",
                    "logs_path": "logs/[SERVICE_NAME]_alerts.log"
                }
            },
            "infrastructure": {
                "service_name": "[SERVICE_NAME]",
                "service_type": "infrastructure",
                "version": "1.0.0",
                "owner": "zmartbot",
                "description": "[SERVICE_DESCRIPTION]",
                "port": "[PORT]",
                "passport_id": "[PASSPORT_ID]",
                "status": "ACTIVE", 
                "registered_at": "[DATE]",
                "health_url": "http://localhost:[PORT]/health",
                "start_cmd": "python3 [SERVICE_NAME].py --port [PORT]",
                "stop_cmd": "pkill -f '[SERVICE_NAME].py'",
                "dependencies": ["zmart-api"],
                "tags": ["infrastructure", "[SERVICE_NAME]"],
                "infrastructure_config": {
                    "critical_service": True,
                    "auto_restart": True,
                    "monitoring_priority": "high"
                },
                "lifecycle": {
                    "startup_grace_seconds": 60,
                    "shutdown_timeout_seconds": 30,
                    "health_check_interval": 10
                }
            }
        }
        
        for service_type, template in templates.items():
            template_file = self.templates_dir / f"{service_type}_template.yaml"
            with open(template_file, 'w') as f:
                yaml.dump(template, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Created {len(templates)} YAML templates")
        
    def generate_service_yaml(self, service_name: str, service_type: str, port: int, 
                            passport_id: str, description: str = "", 
                            custom_fields: Dict = None) -> str:
        """Generate a new YAML file for a service"""
        
        # Load template
        template_file = self.templates_dir / f"{service_type}_template.yaml"
        if not template_file.exists():
            raise ValueError(f"Template for service type '{service_type}' not found")
        
        with open(template_file, 'r') as f:
            template = yaml.safe_load(f)
        
        # Replace placeholders
        yaml_content = json.dumps(template)
        yaml_content = yaml_content.replace("[SERVICE_NAME]", service_name)
        yaml_content = yaml_content.replace("[SERVICE_DESCRIPTION]", 
                                          description or f"{service_name} service for ZmartBot platform")
        yaml_content = yaml_content.replace("[PORT]", str(port))
        yaml_content = yaml_content.replace("[PASSPORT_ID]", passport_id)
        yaml_content = yaml_content.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
        
        service_config = json.loads(yaml_content)
        
        # Add custom fields if provided
        if custom_fields:
            service_config.update(custom_fields)
        
        # Determine output path based on service type
        if service_type == "alert_system":
            alert_name = service_name.lower().replace("alerts", "").replace("_", "-").strip("-")
            output_dir = self.root_dir / "zmart-api" / "alerts" / alert_name
        elif service_type in ["security", "infrastructure"]:
            output_dir = self.root_dir / "zmart-api" / service_type / service_name.lower().replace("-", "_")
        else:
            output_dir = self.root_dir / "zmart-api" / service_name.lower().replace("-", "_")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "service.yaml"
        
        with open(output_file, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Generated YAML: {output_file}")
        return str(output_file)
        
    def sync_with_database(self):
        """Sync YAML files with GOODDatabase.db"""
        if not self.database_file.exists():
            print(f"❌ Database not found: {self.database_file}")
            return
            
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        
        # Get services without YAML files
        cursor.execute("""
            SELECT service_name, passport_id, port, service_type, notes 
            FROM services 
            ORDER BY service_name
        """)
        
        services = cursor.fetchall()
        created_count = 0
        
        for service_name, passport_id, port, service_type, notes in services:
            # Check if YAML already exists
            yaml_exists = self.find_service_yaml(service_name)
            
            if not yaml_exists:
                try:
                    self.generate_service_yaml(
                        service_name=service_name,
                        service_type=service_type or "backend",
                        port=port or 8000,
                        passport_id=passport_id,
                        description=notes or ""
                    )
                    created_count += 1
                except Exception as e:
                    print(f"❌ Failed to create YAML for {service_name}: {e}")
        
        conn.close()
        print(f"📄 Database sync complete - created {created_count} new YAML files")
        
    def find_service_yaml(self, service_name: str) -> Optional[str]:
        """Find existing YAML file for a service"""
        import glob
        
        # Search patterns
        patterns = [
            f"**/zmart-api/**/{service_name.lower().replace('-', '_')}/service.yaml",
            f"**/zmart-api/**/{service_name.lower().replace('_', '-')}/service.yaml",
            f"**/zmart-api/**/{service_name.lower()}/service.yaml"
        ]
        
        for pattern in patterns:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]
        
        return None
        
    def validate_all_yamls(self):
        """Run validation on all YAML files"""
        from .yaml_validator import YAMLGovernanceValidator
        
        validator = YAMLGovernanceValidator()
        results = validator.run_validation()
        
        if results["status"] == "FAILED":
            print(f"❌ YAML Validation failed")
            return False
        else:
            print(f"✅ All YAML files passed validation")
            return True
            
    def create_new_service(self, service_name: str, service_type: str, 
                          port: int, description: str = "") -> str:
        """Create a complete new service with YAML and database entry"""
        
        # Generate passport ID
        import random
        passport_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
        passport_id = f"ZMBT-{service_type.upper()[:4]}-{datetime.now().strftime('%Y%m%d')}-{passport_suffix}"
        
        # Create YAML file
        yaml_file = self.generate_service_yaml(
            service_name=service_name,
            service_type=service_type,
            port=port,
            passport_id=passport_id,
            description=description
        )
        
        # Add to database if it exists
        if self.database_file.exists():
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO services (service_name, passport_id, port, service_type, status, notes)
                    VALUES (?, ?, ?, ?, 'active', ?)
                """, (service_name, passport_id, port, service_type, description))
                
                conn.commit()
                print(f"✅ Added service to database: {service_name}")
                
            except sqlite3.IntegrityError:
                print(f"⚠️  Service {service_name} already exists in database")
            finally:
                conn.close()
        
        print(f"🎉 Service '{service_name}' created successfully!")
        print(f"   YAML: {yaml_file}")
        print(f"   Passport ID: {passport_id}")
        print(f"   Port: {port}")
        
        return yaml_file

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="YAML Manager - Centralized YAML Configuration Management")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create templates command
    templates_cmd = subparsers.add_parser('create-templates', help='Create YAML templates')
    
    # Generate YAML command
    generate_cmd = subparsers.add_parser('generate', help='Generate YAML for a service')
    generate_cmd.add_argument('service_name', help='Service name')
    generate_cmd.add_argument('service_type', help='Service type (backend, alert_system, infrastructure)')
    generate_cmd.add_argument('port', type=int, help='Service port')
    generate_cmd.add_argument('passport_id', help='Service passport ID')
    generate_cmd.add_argument('--description', help='Service description')
    
    # Sync with database command
    sync_cmd = subparsers.add_parser('sync', help='Sync YAML files with database')
    
    # Create new service command
    create_cmd = subparsers.add_parser('create-service', help='Create new service with YAML and database entry')
    create_cmd.add_argument('service_name', help='Service name')
    create_cmd.add_argument('service_type', help='Service type')
    create_cmd.add_argument('port', type=int, help='Service port')
    create_cmd.add_argument('--description', help='Service description')
    
    # Validate command
    validate_cmd = subparsers.add_parser('validate', help='Validate all YAML files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = YAMLManager()
    
    try:
        if args.command == 'create-templates':
            manager.create_service_templates()
            
        elif args.command == 'generate':
            manager.generate_service_yaml(
                args.service_name, args.service_type, args.port,
                args.passport_id, args.description or ""
            )
            
        elif args.command == 'sync':
            manager.sync_with_database()
            
        elif args.command == 'create-service':
            manager.create_new_service(
                args.service_name, args.service_type, args.port,
                args.description or ""
            )
            
        elif args.command == 'validate':
            success = manager.validate_all_yamls()
            sys.exit(0 if success else 1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()