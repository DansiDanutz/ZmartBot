#!/bin/bash

# Update All Paths Script
# Converts all absolute paths to relative paths for zmart-api

echo "🔧 Updating all paths to work within zmart-api only..."

# List of files to update
files_to_update=(
    "test_certification.py"
    "test_qu2cu.py" 
    "test_kucoin.py"
    "test_achievements.py"
    "test_zmart_risk_management.py"
    "test_all_validations_fixed.py"
    "test_zmart_backtesting.py"
    "test_system_protection.py"
    "test_zmart_analytics.py"
    "test_all_validations.py"
    "test_zmart_data_warehouse.py"
    "test_zmart_machine_learning.py"
    "test_zmart_notification.py"
    "test_zmart_technical_analysis.py"
    "test_zmart_websocket.py"
    "api_keys_manager_server.py"
)

# Update each file
for file in "${files_to_update[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ Updating $file"
        # Replace absolute path with relative path
        sed -i '' 's|/Users/dansidanutz/Desktop/ZmartBot/zmart-api|.|g' "$file"
        sed -i '' 's|Path("/Users/dansidanutz/Desktop/ZmartBot")|Path("../.")|g' "$file"
    else
        echo "  ⏭️  $file not found, skipping"
    fi
done

echo "✅ Path updates complete!"
echo ""
echo "🎯 All services now work within zmart-api folder only"
echo "   No more dependencies on root ZmartBot folder"