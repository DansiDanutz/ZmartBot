#!/bin/bash

# Emergency System Restoration Script
echo "🚑 EMERGENCY SYSTEM RESTORATION"

# Find latest backup
LATEST_BACKUP=$(ls -td system_backups/*/2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backups found - using git restoration"
    
    # Restore from git
    git checkout ca094a6 -- .cursor/rules/ 2>/dev/null || {
        echo "🔄 Attempting individual file restoration..."
        ./restore_mdc_files.sh
    }
else
    echo "📦 Found backup: $LATEST_BACKUP"
    echo "🔄 Restoring from backup..."
    
    # Restore from backup
    cp -r "$LATEST_BACKUP"/* ./ 2>/dev/null
    echo "✅ Restoration from backup completed"
fi

# Verify restoration
mdc_count=$(find .cursor/rules -name "*.mdc" 2>/dev/null | wc -l)
echo "📊 Current MDC files: $mdc_count"

if [ "$mdc_count" -gt 50 ]; then
    echo "✅ System restoration successful"
else
    echo "⚠️  System may need manual intervention"
fi
