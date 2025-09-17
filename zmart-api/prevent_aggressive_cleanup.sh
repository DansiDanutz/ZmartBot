#!/bin/bash

# Prevent Aggressive Cleanup - Monitors for suspicious file operations

CRITICAL_DIRS=(".cursor/rules" "Dashboard/MDC-Dashboard" "Documentation")
BACKUP_DIR="./system_backups/$(date +%Y%m%d_%H%M%S)"

# Function to create emergency backup
create_emergency_backup() {
    echo "🚨 EMERGENCY: Creating protective backup"
    mkdir -p "$BACKUP_DIR"
    
    for dir in "${CRITICAL_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            cp -r "$dir" "$BACKUP_DIR/" 2>/dev/null
            echo "  📦 Backed up: $dir"
        fi
    done
    
    echo "🔒 Emergency backup created at: $BACKUP_DIR"
}

# Check for suspicious cleanup patterns
if pgrep -f "cleanup|clean|remove|delete" > /dev/null; then
    echo "🚨 CLEANUP PROCESS DETECTED"
    
    # Count critical files
    mdc_count=$(find .cursor/rules -name "*.mdc" 2>/dev/null | wc -l)
    
    if [ "$mdc_count" -lt 50 ]; then
        echo "🚨 CRITICAL: MDC file count too low ($mdc_count) - Creating emergency backup"
        create_emergency_backup
        
        # Send alert
        echo "[$(date)] CRITICAL: MDC file count dropped to $mdc_count" >> system_protection.log
    fi
fi

echo "✅ Cleanup monitoring active"
