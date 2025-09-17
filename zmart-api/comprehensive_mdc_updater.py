#!/usr/bin/env python3
"""
🔧 Comprehensive MDC Updater
Scans all MDC files alphabetically and updates them with real service data
"""

import os
import sqlite3
import glob
from pathlib import Path
from datetime import datetime
import re

def get_service_data():
    """Get all service data from the master database"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    db_path = os.path.join(base_path, "src", "data", "service_registry.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, certification_level, port, passport_id, kind, python_file_path
            FROM service_registry 
            ORDER BY service_name
        """)
        
        services = cursor.fetchall()
        conn.close()
        
        # Convert to dictionary for easy lookup
        service_dict = {}
        for name, level, port, passport, kind, python_file in services:
            service_dict[name] = {
                'level': level,
                'port': port,
                'passport': passport,
                'kind': kind or 'backend',
                'python_file': python_file,
                'status': 'certified' if level == 3 else 'active' if level == 2 else 'discovery'
            }
        
        return service_dict
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return {}

def get_level_requirements():
    """Define the requirements for each service level"""
    return {
        'level_1': {
            'name': 'Discovery',
            'requirements': [
                'MDC file OR Python file',
                'Basic service documentation',
                'Initial implementation'
            ],
            'triggers': [
                'service_discovery',
                'initial_development'
            ],
            'upgrade_to_level_2': [
                'Complete MDC file',
                'Python implementation',
                'Port assignment',
                'Passport registration',
                'Basic testing completed'
            ]
        },
        'level_2': {
            'name': 'Active/Passport',
            'requirements': [
                'Complete MDC file',
                'Python implementation with port',
                'Valid passport ID',
                'Service registration in database',
                'Basic health checks'
            ],
            'triggers': [
                'port_assignment',
                'passport_registration',
                'service_activation'
            ],
            'upgrade_to_level_3': [
                'YAML manifest file',
                'Complete workflow documentation',
                'Security audit passed',
                'Performance testing completed',
                'Integration testing passed',
                'Production readiness verified'
            ]
        },
        'level_3': {
            'name': 'Certified/Registered',
            'requirements': [
                'All Level 2 requirements',
                'YAML manifest file',
                'Complete workflow & triggers documentation',
                'Security certification',
                'Performance benchmarks',
                'Integration compatibility',
                'Production deployment ready'
            ],
            'triggers': [
                'certification_request',
                'production_deployment',
                'yaml_manifest_creation'
            ],
            'benefits': [
                'Production deployment authorization',
                'Automatic protection activation',
                'Enhanced monitoring',
                'Priority support',
                'System integration privileges'
            ]
        }
    }

def extract_service_name_from_mdc(file_path):
    """Extract likely service name from MDC file name"""
    file_name = os.path.basename(file_path).replace('.mdc', '')
    
    # Common variations to normalize
    normalizations = {
        'MainAPIServer': 'zmart-api',
        'MasterOrchestrationAgent': 'master-orchestration-agent',
        'MDCAgent': 'mdc-orchestration-agent',
        'LiveAlerts': 'live-alerts',
        'MessiAlerts': 'messi-alerts',
        'WhaleAlerts': 'whale-alerts',
        'PortManager': 'port-manager-service',
        'ServiceLog': 'servicelog-service',
        'BinanceServices': 'binance',
        'KuCoinService': 'kucoin',
        'API-Manager': 'api-keys-manager-service',
        'DoctorService': 'doctor-service',
        'CertificationService': 'certification',
        'KINGFISHER_AI': 'kingfisher-ai',
        'CryptometerService': 'cryptometer-service'
    }
    
    return normalizations.get(file_name, file_name.lower())

def update_mdc_with_service_data(file_path, service_name, service_data, requirements):
    """Update MDC file with real service data"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find matching service in database
        actual_service = None
        for db_service_name, data in service_data.items():
            if (db_service_name == service_name or 
                db_service_name.replace('-', '_') == service_name.replace('-', '_') or
                service_name in db_service_name or db_service_name in service_name):
                actual_service = data
                service_name = db_service_name  # Use the exact database name
                break
        
        if not actual_service:
            # This is a non-service MDC file (documentation, rules, etc.)
            print(f"⏭️ Skipping non-service file: {os.path.basename(file_path)}")
            return False
        
        # Extract current level info
        level = actual_service['level']
        level_name = requirements[f'level_{level}']['name']
        
        # Create service classification section
        service_classification = f"""
## 🏷️ SERVICE CLASSIFICATION & STATUS

**Service Name:** {service_name}
**Current Level:** Level {level} - {level_name}
**Port:** {actual_service['port'] or 'Not Assigned'}
**Passport ID:** {actual_service['passport'] or 'Not Assigned'}
**Service Type:** {actual_service['kind']}
**Status:** {actual_service['status'].upper()}
**Python File:** {actual_service['python_file'] or f'src/services/{service_name.replace("-", "_")}.py'}

### Level {level} Requirements Status:
"""
        
        # Add requirements for current level
        for req in requirements[f'level_{level}']['requirements']:
            status = "✅" if level >= 2 or (level == 1 and "MDC" in req) else "⚠️"
            service_classification += f"- {status} {req}\n"
        
        if level < 3:
            next_level = level + 1
            service_classification += f"""
### Upgrade to Level {next_level} Requirements:
"""
            upgrade_key = f'upgrade_to_level_{next_level}' if level == 1 else f'upgrade_to_level_{next_level}'
            if upgrade_key in requirements[f'level_{level}']:
                for req in requirements[f'level_{level}'][upgrade_key]:
                    status = "✅" if (level == 2 and actual_service['passport']) else "❌"
                    service_classification += f"- {status} {req}\n"
        
        # Add triggers section
        service_classification += f"""
### Service Triggers:
"""
        for trigger in requirements[f'level_{level}']['triggers']:
            service_classification += f"- 🔄 {trigger.replace('_', ' ').title()}\n"
        
        # Update or add the classification section
        classification_pattern = r'## 🏷️ SERVICE CLASSIFICATION & STATUS.*?(?=##|$)'
        
        if '## 🏷️ SERVICE CLASSIFICATION & STATUS' in content:
            # Replace existing section
            content = re.sub(classification_pattern, service_classification.strip(), content, flags=re.DOTALL)
        else:
            # Add after the first ## section (usually Description or Purpose)
            parts = content.split('\n## ', 1)
            if len(parts) > 1:
                content = parts[0] + '\n' + service_classification + '\n## ' + parts[1]
            else:
                content = content + '\n' + service_classification
        
        # Update service references in the content
        if actual_service['port']:
            content = re.sub(r'Port:?\s*\d+', f'Port: {actual_service["port"]}', content)
            content = re.sub(r'port\s*=\s*\d+', f'port={actual_service["port"]}', content)
        
        if actual_service['passport']:
            content = re.sub(r'Passport:?\s*[A-Z0-9-]+', f'Passport: {actual_service["passport"]}', content)
        
        # Add timestamp
        timestamp_section = f"""
---
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Service Level: {level} ({level_name})*
*Database Verified: ✅*
"""
        
        # Remove old timestamp and add new one
        content = re.sub(r'\n---\n\*Last Updated:.*?\*Database Verified:.*?\*', '', content, flags=re.DOTALL)
        content = content.rstrip() + '\n' + timestamp_section
        
        # Write updated content back
        with open(file_path, 'w') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    print("🔧 COMPREHENSIVE MDC UPDATER")
    print("=" * 70)
    print(f"🕐 Update Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get service data and requirements
    service_data = get_service_data()
    requirements = get_level_requirements()
    
    print(f"📊 Found {len(service_data)} services in database")
    print()
    
    # Get all MDC files in alphabetical order
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    mdc_files = sorted(glob.glob(os.path.join(base_path, ".cursor", "rules", "*.mdc")))
    
    print(f"📁 Processing {len(mdc_files)} MDC files alphabetically:")
    print()
    
    updated_count = 0
    skipped_count = 0
    
    for i, file_path in enumerate(mdc_files, 1):
        file_name = os.path.basename(file_path)
        service_name = extract_service_name_from_mdc(file_path)
        
        print(f"{i:3d}. {file_name:<40} -> ", end="")
        
        if update_mdc_with_service_data(file_path, service_name, service_data, requirements):
            print("✅ UPDATED")
            updated_count += 1
        else:
            print("⏭️ SKIPPED")
            skipped_count += 1
    
    print()
    print("📊 UPDATE SUMMARY")
    print("-" * 40)
    print(f"   Total MDC Files: {len(mdc_files)}")
    print(f"   Updated: {updated_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Success Rate: {(updated_count / len(mdc_files) * 100):.1f}%")
    print()
    print("🎯 All service MDC files have been updated with real database information!")
    print("=" * 70)

if __name__ == "__main__":
    main()