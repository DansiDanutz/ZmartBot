#!/bin/bash

# Simple Security Check for ZmartBot
# Focused check for staged files only

echo "🔒 ZmartBot Security Check"

# Check staged files only
staged_files=$(git diff --cached --name-only)

if [ -z "$staged_files" ]; then
    echo "✅ No staged files to check"
    exit 0
fi

echo "📋 Checking staged files:"
echo "$staged_files"

# Check for common secret patterns in staged files
found_secrets=false

for file in $staged_files; do
    if [ -f "$file" ]; then
        # Check for API keys
        if grep -qiE "(api[_-]?key|apikey)[\s]*[=:][\s]*[\"']?[a-zA-Z0-9]{20,}" "$file"; then
            echo "❌ Potential API key found in: $file"
            found_secrets=true
        fi
        
        # Check for passwords  
        if grep -qiE "(password|secret)[\s]*[=:][\s]*[\"']?[a-zA-Z0-9!@#$%^&*]{8,}" "$file"; then
            echo "❌ Potential password found in: $file"
            found_secrets=true
        fi
        
        # Check for database URLs
        if grep -qiE "(database_url|db_url)[\s]*[=:][\s]*[\"']?[a-zA-Z]+://[^\s\"']+" "$file"; then
            echo "❌ Potential database URL found in: $file"
            found_secrets=true
        fi
    fi
done

if [ "$found_secrets" = true ]; then
    echo "💥 Security scan failed! Potential secrets found."
    echo "👀 Please review the flagged files and remove any secrets."
    exit 1
else
    echo "✅ Security scan passed - no secrets detected"
    exit 0
fi