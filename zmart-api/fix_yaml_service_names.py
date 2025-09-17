#!/usr/bin/env python3
"""
Fix YAML Service Names to Match Database Exactly
Updates the service names inside YAML files to match database entries precisely
"""

import yaml
import sqlite3
from pathlib import Path

def get_database_services():
    """Get all service names from database"""
    conn = sqlite3.connect('src/data/service_registry.db')
    cursor = conn.cursor()
    cursor.execute('SELECT service_name FROM service_registry ORDER BY service_name')
    services = {row[0] for row in cursor.fetchall()}
    conn.close()
    return services

def find_yaml_files():
    """Find all service.yaml files"""
    yaml_files = []
    for yaml_file in Path(".").rglob("service.yaml"):
        # Skip backup directories
        if "sync_backups" in yaml_file.parts or "orphaned_yaml_files" in yaml_file.parts:
            continue
        yaml_files.append(yaml_file)
    return yaml_files

def fix_yaml_service_names():
    """Fix service names in YAML files to match database exactly"""
    db_services = get_database_services()
    yaml_files = find_yaml_files()
    
    # Create mapping from directory names to database service names
    # This follows Cursor's pattern: directory_name -> database-service-name
    directory_to_service_map = {
        'orchestrationstart': 'OrchestrationStart',
        'registryconsolidator': 'RegistryConsolidator', 
        'tradingstrategy': 'TradingStrategy',
        'yamlgovernanceservice': 'YAMLGovernanceService',
        'yamlmonitoringdaemon': 'YAMLMonitoringDaemon',
        'achievements': 'achievements',
        'binance_worker': 'binance-worker',
        'certification': 'certification',
        'enhanced_mdc_monitor': 'enhanced-mdc-monitor',
        'kingfisher_ai': 'kingfisher-ai',
        'live_alerts': 'live-alerts',
        'maradona_alerts': 'maradona-alerts',
        'messi_alerts': 'messi-alerts',
        'pele_alerts': 'pele-alerts',
        'registration_service': 'registration-service',
        'whale_alerts': 'whale-alerts',
        'ziva_agent': 'ziva-agent',
        'zmart_alert_system': 'zmart_alert_system',
        'zmart_analytics': 'zmart_analytics', 
        'zmart_backtesting': 'zmart_backtesting',
        'zmart_data_warehouse': 'zmart_data_warehouse',
        'zmart_machine_learning': 'zmart_machine_learning',
        'zmart_risk_management': 'zmart_risk_management',
        'zmart_technical_analysis': 'zmart_technical_analysis'
    }
    
    fixed_count = 0
    
    for yaml_file in yaml_files:
        try:
            # Get directory name
            dir_name = yaml_file.parent.name
            
            # Check if we need to fix this directory
            if dir_name in directory_to_service_map:
                correct_service_name = directory_to_service_map[dir_name]
                
                # Load YAML content
                with open(yaml_file, 'r') as f:
                    content = yaml.safe_load(f)
                
                # Check current service name
                current_name = content.get('service', {}).get('name', '')
                
                if current_name != correct_service_name:
                    # Fix the service name
                    if 'service' not in content:
                        content['service'] = {}
                    content['service']['name'] = correct_service_name
                    
                    # Write back the fixed YAML
                    with open(yaml_file, 'w') as f:
                        yaml.dump(content, f, default_flow_style=False, indent=2)
                    
                    fixed_count += 1
                    print(f"✅ Fixed service name in {yaml_file}: '{current_name}' -> '{correct_service_name}'")
                else:
                    print(f"⏭️  Already correct: {yaml_file} -> {correct_service_name}")
            
        except Exception as e:
            print(f"❌ Error processing {yaml_file}: {e}")
    
    print(f"\n🔧 Fixed {fixed_count} YAML service names")
    return fixed_count

if __name__ == "__main__":
    print("🔧 FIXING YAML SERVICE NAMES TO MATCH DATABASE")
    print("=" * 50)
    fix_yaml_service_names()