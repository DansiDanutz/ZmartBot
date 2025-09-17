#!/bin/bash

# File Protection Guard - Prevents accidental mass deletions
PROTECTED_FILES=".protected_files_list"
LOG_FILE="deletion_protection.log"

# Function to check if file should be protected
is_protected() {
    local file="$1"
    
    # Read protected patterns
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        # Skip comments and empty lines
        [[ "$pattern" =~ ^#.*$ ]] && continue
        [[ -z "$pattern" ]] && continue
        
        # Check if file matches pattern
        if [[ "$file" == $pattern ]]; then
            return 0  # Protected
        fi
    done < "$PROTECTED_FILES"
    
    return 1  # Not protected
}

# Function to log protection events
log_protection() {
    echo "[$(date)] PROTECTION: $1" >> "$LOG_FILE"
}

# Check if this is a mass deletion attempt
if [[ "$1" == "rm" ]] && [[ "$#" -gt 10 ]]; then
    echo "🚨 MASS DELETION DETECTED - BLOCKING"
    log_protection "Mass deletion blocked: $*"
    exit 1
fi

# Check individual files
for file in "$@"; do
    if is_protected "$file"; then
        echo "🛡️  PROTECTED FILE: $file - Operation blocked"
        log_protection "Protected file access blocked: $file"
        exit 1
    fi
done

echo "✅ File protection check passed"
