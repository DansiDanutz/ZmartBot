#!/bin/bash

# ZmartBot Security Scanning Script
# This script performs comprehensive secret detection using gitleaks and detect-secrets
# It fails on any matches to prevent secrets from being committed

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
GITLEAKS_CONFIG="$PROJECT_ROOT/.gitleaks.toml"
DETECT_SECRETS_BASELINE="$PROJECT_ROOT/.secrets.baseline"
GITLEAKS_REPORT="$PROJECT_ROOT/gitleaks-report.json"
DETECT_SECRETS_REPORT="$PROJECT_ROOT/detect-secrets-report.json"
SCAN_LOG="$PROJECT_ROOT/security-scan.log"

# Initialize log file
echo "=== ZmartBot Security Scan - $(date) ===" > "$SCAN_LOG"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$SCAN_LOG"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "${RED}❌ Error: Not in a git repository${NC}"
        exit 1
    fi
}

# Function to check for staged changes
check_staged_changes() {
    if git diff --cached --quiet; then
        log "${YELLOW}⚠️  Warning: No staged changes to scan${NC}"
        return 1
    fi
    return 0
}

# Function to run gitleaks scan
run_gitleaks() {
    log "${BLUE}🔍 Running Gitleaks scan...${NC}"
    
    if ! command_exists gitleaks; then
        log "${RED}❌ Error: gitleaks not found. Please install it first.${NC}"
        return 1
    fi
    
    # Run gitleaks on staged files
    if gitleaks detect \
        --config "$GITLEAKS_CONFIG" \
        --source . \
        --report-format json \
        --report-path "$GITLEAKS_REPORT" \
        --verbose \
        --no-git; then
        
        # Check if any secrets were found
        if [ -f "$GITLEAKS_REPORT" ] && [ -s "$GITLEAKS_REPORT" ]; then
            log "${RED}❌ Gitleaks found potential secrets!${NC}"
            log "${YELLOW}📋 Gitleaks Report:${NC}"
            cat "$GITLEAKS_REPORT" | jq '.' 2>/dev/null || cat "$GITLEAKS_REPORT"
            return 1
        else
            log "${GREEN}✅ Gitleaks scan completed - no secrets found${NC}"
            return 0
        fi
    else
        log "${RED}❌ Gitleaks scan failed${NC}"
        return 1
    fi
}

# Function to run detect-secrets scan
run_detect_secrets() {
    log "${BLUE}🔍 Running Detect-Secrets scan...${NC}"
    
    # Get detect-secrets path
    DETECT_SECRETS_PATH=""
    if command_exists detect-secrets; then
        DETECT_SECRETS_PATH="detect-secrets"
    elif [ -f "/Users/dansidanutz/Library/Python/3.9/bin/detect-secrets" ]; then
        DETECT_SECRETS_PATH="/Users/dansidanutz/Library/Python/3.9/bin/detect-secrets"
    else
        log "${RED}❌ Error: detect-secrets not found. Please install it first.${NC}"
        return 1
    fi
    
    # Run detect-secrets scan
    if $DETECT_SECRETS_PATH scan \
        --baseline "$DETECT_SECRETS_BASELINE" \
        --update \
        --exclude-files "$DETECT_SECRETS_BASELINE" \
        . > "$DETECT_SECRETS_REPORT" 2>&1; then
        
        # Check if any new secrets were found
        if $DETECT_SECRETS_PATH audit \
            --baseline "$DETECT_SECRETS_BASELINE" \
            --report | grep -q "UNVERIFIED"; then
            
            log "${RED}❌ Detect-Secrets found potential secrets!${NC}"
            log "${YELLOW}📋 Detect-Secrets Report:${NC}"
            $DETECT_SECRETS_PATH audit --baseline "$DETECT_SECRETS_BASELINE" --report
            return 1
        else
            log "${GREEN}✅ Detect-Secrets scan completed - no new secrets found${NC}"
            return 0
        fi
    else
        log "${RED}❌ Detect-Secrets scan failed${NC}"
        return 1
    fi
}

# Function to run custom ZmartBot specific checks
run_custom_checks() {
    log "${BLUE}🔍 Running custom ZmartBot security checks...${NC}"
    
    local found_secrets=false
    
    # Check for hardcoded API keys in staged files
    while IFS= read -r -d '' file; do
        if git diff --cached --name-only | grep -q "$file"; then
            # Check for common API key patterns
            if git diff --cached "$file" | grep -iE "(api[_-]?key|apikey|api_key)[\s]*[=:][\s]*[\"']?[a-zA-Z0-9]{32,}[\"']?"; then
                log "${RED}❌ Potential API key found in: $file${NC}"
                found_secrets=true
            fi
            
            # Check for database URLs
            if git diff --cached "$file" | grep -iE "(database_url|db_url|connection_string)[\s]*[=:][\s]*[\"']?[a-zA-Z]+://[^\s\"']+[\"']?"; then
                log "${RED}❌ Potential database URL found in: $file${NC}"
                found_secrets=true
            fi
            
            # Check for private keys
            if git diff --cached "$file" | grep -iE "(-----BEGIN.*PRIVATE KEY-----|-----BEGIN.*RSA PRIVATE KEY-----)"; then
                log "${RED}❌ Potential private key found in: $file${NC}"
                found_secrets=true
            fi
        fi
    done < <(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.sh" -o -name "*.env" -o -name "*.yml" -o -name "*.yaml" \) -print0)
    
    if [ "$found_secrets" = true ]; then
        return 1
    else
        log "${GREEN}✅ Custom checks completed - no secrets found${NC}"
        return 0
    fi
}

# Function to clean up temporary files
cleanup() {
    log "${BLUE}🧹 Cleaning up temporary files...${NC}"
    rm -f "$GITLEAKS_REPORT" "$DETECT_SECRETS_REPORT" 2>/dev/null || true
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

ZmartBot Security Scanning Script

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    --gitleaks-only     Run only gitleaks scan
    --detect-secrets-only Run only detect-secrets scan
    --custom-only       Run only custom checks
    --no-cleanup        Don't clean up temporary files
    --pre-commit        Run in pre-commit mode (scan staged files only)

EXAMPLES:
    $0                    # Run all scans
    $0 --pre-commit      # Run pre-commit scan
    $0 --gitleaks-only   # Run only gitleaks
    $0 --verbose         # Run with verbose output

EOF
}

# Parse command line arguments
VERBOSE=false
GITLEAKS_ONLY=false
DETECT_SECRETS_ONLY=false
CUSTOM_ONLY=false
NO_CLEANUP=false
PRE_COMMIT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --gitleaks-only)
            GITLEAKS_ONLY=true
            shift
            ;;
        --detect-secrets-only)
            DETECT_SECRETS_ONLY=true
            shift
            ;;
        --custom-only)
            CUSTOM_ONLY=true
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        --pre-commit)
            PRE_COMMIT=true
            shift
            ;;
        *)
            log "${RED}❌ Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log "${BLUE}🚀 Starting ZmartBot Security Scan${NC}"
    
    # Check if we're in a git repository
    check_git_repo
    
    # Check for staged changes in pre-commit mode
    if [ "$PRE_COMMIT" = true ]; then
        if ! check_staged_changes; then
            log "${YELLOW}⚠️  No staged changes to scan in pre-commit mode${NC}"
            exit 0
        fi
    fi
    
    # Set up trap for cleanup
    if [ "$NO_CLEANUP" = false ]; then
        trap cleanup EXIT
    fi
    
    local exit_code=0
    
    # Run scans based on options
    if [ "$GITLEAKS_ONLY" = true ]; then
        if ! run_gitleaks; then
            exit_code=1
        fi
    elif [ "$DETECT_SECRETS_ONLY" = true ]; then
        if ! run_detect_secrets; then
            exit_code=1
        fi
    elif [ "$CUSTOM_ONLY" = true ]; then
        if ! run_custom_checks; then
            exit_code=1
        fi
    else
        # Run all scans
        if ! run_gitleaks; then
            exit_code=1
        fi
        
        if ! run_detect_secrets; then
            exit_code=1
        fi
        
        if ! run_custom_checks; then
            exit_code=1
        fi
    fi
    
    # Final result
    if [ $exit_code -eq 0 ]; then
        log "${GREEN}🎉 All security scans passed!${NC}"
        log "${GREEN}✅ No secrets detected in the codebase${NC}"
    else
        log "${RED}💥 Security scan failed!${NC}"
        log "${RED}❌ Potential secrets were detected. Please review and fix before committing.${NC}"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
