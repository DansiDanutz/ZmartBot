#!/bin/bash

# 🧹 ZmartBot Automated System Cleanup Script
# This script removes duplicates, unused files, and optimizes disk space

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
INTERACTIVE=true
BACKUP_BEFORE_CLEANUP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --auto)
            INTERACTIVE=false
            shift
            ;;
        --backup)
            BACKUP_BEFORE_CLEANUP=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--auto] [--backup]"
            echo "  --dry-run: Show what would be deleted without actually deleting"
            echo "  --auto: Run without interactive prompts"
            echo "  --backup: Create backup before cleanup"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🧹 ZmartBot System Cleanup${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_section() {
    echo -e "${YELLOW}📁 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

calculate_size() {
    if [[ -d "$1" ]]; then
        du -sh "$1" 2>/dev/null | cut -f1 || echo "0B"
    else
        echo "0B"
    fi
}

safe_remove() {
    local path="$1"
    local description="$2"
    
    if [[ ! -e "$path" ]]; then
        print_warning "Path does not exist: $path"
        return
    fi
    
    local size=$(calculate_size "$path")
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [DRY RUN] Would remove: $path ($size) - $description"
        return
    fi
    
    if [[ "$INTERACTIVE" == "true" ]]; then
        echo -e "Remove ${RED}$path${NC} (${size})?"
        echo "  Description: $description"
        read -p "Continue? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Skipped: $path"
            return
        fi
    fi
    
    rm -rf "$path"
    print_success "Removed: $path ($size)"
}

create_backup() {
    if [[ "$BACKUP_BEFORE_CLEANUP" == "true" ]]; then
        local backup_name="zmartbot_cleanup_backup_$(date +%Y%m%d_%H%M%S)"
        print_section "Creating Backup"
        
        if [[ "$DRY_RUN" == "false" ]]; then
            mkdir -p "./cleanup_backups"
            cp -r . "./cleanup_backups/$backup_name" 2>/dev/null || true
            print_success "Backup created: ./cleanup_backups/$backup_name"
        else
            echo "  [DRY RUN] Would create backup: ./cleanup_backups/$backup_name"
        fi
        echo ""
    fi
}

cleanup_duplicate_backends() {
    print_section "Cleaning Duplicate Backend Implementations"
    
    # Keep: ./backend/zmart-api/ (primary)
    # Remove duplicates
    safe_remove "./zmart-platform/backend/zmart-api" "Duplicate backend implementation"
    safe_remove "./zmart-cursor-essentials/backend/zmart-api" "Duplicate backend implementation"
    
    echo ""
}

cleanup_duplicate_frontends() {
    print_section "Cleaning Duplicate Frontend Implementations"
    
    # Keep: ./frontend/zmart-dashboard/ (primary)
    # Keep: ./kingfisher-module/frontend/ (module-specific)
    # Remove duplicates
    safe_remove "./zmart-platform/frontend/zmart-dashboard" "Duplicate frontend implementation"
    
    echo ""
}

cleanup_virtual_environments() {
    print_section "Cleaning Virtual Environments"
    
    # Remove all backup venvs
    find ./backup_points -name "venv" -type d 2>/dev/null | while read venv_path; do
        safe_remove "$venv_path" "Backup virtual environment"
    done
    
    # Remove duplicate venvs
    safe_remove "./zmart-platform/backend/zmart-api/venv" "Duplicate virtual environment"
    
    # Keep active development venvs:
    # - ./backend/zmart-api/venv/
    # - ./kingfisher-module/backend/venv/
    
    echo ""
}

cleanup_node_modules() {
    print_section "Cleaning Node Modules"
    
    # Remove all backup node_modules
    find ./backup_points -name "node_modules" -type d 2>/dev/null | while read nm_path; do
        safe_remove "$nm_path" "Backup node_modules"
    done
    
    # Remove duplicate node_modules
    safe_remove "./zmart-platform/frontend/zmart-dashboard/node_modules" "Duplicate node_modules"
    
    # Keep active development node_modules:
    # - ./frontend/zmart-dashboard/node_modules/
    # - ./kingfisher-module/frontend/node_modules/
    
    echo ""
}

cleanup_backup_points() {
    print_section "Cleaning Backup Points"
    
    if [[ -d "./backup_points" ]]; then
        local backup_size=$(calculate_size "./backup_points")
        safe_remove "./backup_points" "All backup points directory ($backup_size)"
    fi
    
    echo ""
}

cleanup_obsolete_documentation() {
    print_section "Cleaning Obsolete Documentation"
    
    # Remove temporary analysis files
    find . -maxdepth 1 -name "*_STATUS*.md" -type f | while read doc_file; do
        safe_remove "$doc_file" "Temporary status documentation"
    done
    
    # Remove audit reports (keep the latest one)
    find . -maxdepth 1 -name "*AUDIT*.md" -not -name "COMPREHENSIVE_SYSTEM_AUDIT_AND_CLEANUP_REPORT.md" -type f | while read audit_file; do
        safe_remove "$audit_file" "Obsolete audit report"
    done
    
    # Remove backend fix documentation
    find . -maxdepth 1 -name "*BACKEND*FIX*.md" -type f | while read fix_file; do
        safe_remove "$fix_file" "Obsolete backend fix documentation"
    done
    
    echo ""
}

cleanup_temporary_scripts() {
    print_section "Cleaning Temporary Scripts"
    
    # Remove test scripts
    find . -maxdepth 1 -name "test_*.py" -type f | while read test_file; do
        safe_remove "$test_file" "Temporary test script"
    done
    
    # Remove cleanup scripts (except this one)
    find . -maxdepth 1 -name "*cleanup*.sh" -not -name "automated_cleanup.sh" -type f | while read cleanup_file; do
        safe_remove "$cleanup_file" "Obsolete cleanup script"
    done
    
    # Remove fix scripts
    find . -maxdepth 1 -name "fix_*.py" -type f | while read fix_file; do
        safe_remove "$fix_file" "Temporary fix script"
    done
    
    echo ""
}

cleanup_python_cache() {
    print_section "Cleaning Python Cache"
    
    # Remove __pycache__ directories
    find . -name "__pycache__" -type d | while read cache_dir; do
        safe_remove "$cache_dir" "Python cache directory"
    done
    
    # Remove .pyc files
    find . -name "*.pyc" -type f | while read pyc_file; do
        safe_remove "$pyc_file" "Python bytecode file"
    done
    
    echo ""
}

show_summary() {
    print_section "Cleanup Summary"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "DRY RUN MODE - No files were actually deleted"
    else
        print_success "Cleanup completed successfully!"
    fi
    
    echo ""
    echo "Remaining structure:"
    echo "├── backend/zmart-api/          # Primary backend"
    echo "├── frontend/zmart-dashboard/   # Primary frontend"
    echo "├── kingfisher-module/          # Specialized module"
    echo "├── Documentation/              # Consolidated docs"
    echo "└── scripts/                    # Utility scripts"
    echo ""
    
    if [[ "$DRY_RUN" == "false" ]]; then
        print_success "System is now clean and optimized!"
        echo ""
        echo "Next steps:"
        echo "1. Test backend: cd backend/zmart-api && ./FINAL_WORKING_START.sh"
        echo "2. Test frontend: cd frontend/zmart-dashboard && npm start"
        echo "3. Test KingFisher: cd kingfisher-module && npm start"
    fi
}

# Main execution
main() {
    print_header
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "Running in DRY RUN mode - no files will be deleted"
        echo ""
    fi
    
    if [[ "$INTERACTIVE" == "false" ]]; then
        print_warning "Running in AUTOMATIC mode - no prompts will be shown"
        echo ""
    fi
    
    # Show current disk usage
    echo "Current directory size: $(calculate_size .)"
    echo ""
    
    create_backup
    cleanup_duplicate_backends
    cleanup_duplicate_frontends
    cleanup_virtual_environments
    cleanup_node_modules
    cleanup_backup_points
    cleanup_obsolete_documentation
    cleanup_temporary_scripts
    cleanup_python_cache
    show_summary
}

# Run main function
main "$@"