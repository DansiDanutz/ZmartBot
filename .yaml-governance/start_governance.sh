#!/bin/bash
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
