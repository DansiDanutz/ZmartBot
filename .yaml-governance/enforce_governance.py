#!/usr/bin/env python3
"""
Governance Enforcement Tool - Final System Setup
"""

import os
import sys
import yaml

def fix_unknown_services():
    """Fix YAML files that have 'unknown' service names"""
    
    fixes = [
        ("zmart-api/database/service.yaml", "database-service"),
        ("zmart-api/data_warehouse/service.yaml", "zmart-data-warehouse"), 
        ("zmart-api/backtesting/service.yaml", "zmart-backtesting"),
        ("zmart-api/gpt-mds-agent/service.yaml", "gpt-mds-agent"),
        ("zmart-api/machine_learning/service.yaml", "zmart-machine-learning"),
        ("zmart-api/risk_management/service.yaml", "zmart-risk-management"),
        ("zmart-api/alert_system/service.yaml", "zmart-alert-system"),
        ("zmart-api/technical_analysis/service.yaml", "zmart-technical-analysis")
    ]
    
    for yaml_path, correct_name in fixes:
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                if content:
                    content['service_name'] = correct_name
                    
                    with open(yaml_path, 'w') as f:
                        yaml.dump(content, f, default_flow_style=False, sort_keys=False)
                    
                    print(f"✅ Fixed service name in {yaml_path} → {correct_name}")
            except Exception as e:
                print(f"❌ Error fixing {yaml_path}: {e}")

def fix_port_conflicts():
    """Fix remaining port conflicts"""
    
    port_fixes = [
        ("zmart-api/machine_learning/service.yaml", 8170),  # Change from 8014
        ("zmart-api/alerts/messi--server/service.yaml", 8022),  # Use existing MessiAlerts port
        ("zmart-api/alerts/pele--server/service.yaml", 8023),   # Use existing PeleAlerts port  
        ("zmart-api/service_discovery_server/service.yaml", 8781),  # Change from 8780
    ]
    
    for yaml_path, new_port in port_fixes:
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                if content:
                    old_port = content.get('port')
                    content['port'] = new_port
                    content['health_url'] = f"http://localhost:{new_port}/health"
                    
                    with open(yaml_path, 'w') as f:
                        yaml.dump(content, f, default_flow_style=False, sort_keys=False)
                    
                    print(f"✅ Fixed port conflict in {yaml_path}: {old_port} → {new_port}")
            except Exception as e:
                print(f"❌ Error fixing {yaml_path}: {e}")

def create_startup_script():
    """Create a startup script for the governance system"""
    
    startup_script = """#!/bin/bash
#
# YAML Governance System Startup Script
# Run this to ensure the governance system is active
#

echo "🛡️  Initializing YAML Governance System..."

# Create templates
echo "📋 Creating YAML templates..."
python3 .yaml-governance/yaml_manager.py create-templates

# Run initial validation
echo "🔍 Running initial validation..."
python3 .yaml-governance/yaml_validator.py

# Check if validation passed
if [ $? -eq 0 ]; then
    echo "✅ YAML Governance System is ready!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Use: python3 .yaml-governance/yaml_manager.py create-service [name] [type] [port]"
    echo "2. All commits will be automatically validated"
    echo "3. Monitor: python3 .yaml-governance/monitoring_daemon.py"
    echo ""
else
    echo "❌ Validation failed - please fix issues before proceeding"
    echo "💡 Run: python3 .yaml-governance/yaml_validator.py"
    exit 1
fi
"""
    
    with open('.yaml-governance/start_governance.sh', 'w') as f:
        f.write(startup_script)
    
    os.chmod('.yaml-governance/start_governance.sh', 0o755)
    print("✅ Created governance startup script")

def main():
    """Main enforcement function"""
    print("🔧 Running final governance enforcement...")
    
    fix_unknown_services()
    fix_port_conflicts()
    create_startup_script()
    
    print("\n🎯 Governance enforcement complete!")
    print("🚀 Run: ./.yaml-governance/start_governance.sh to activate the system")

if __name__ == "__main__":
    main()