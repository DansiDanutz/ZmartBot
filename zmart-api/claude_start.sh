#!/bin/bash

# Claude Code Startup Script for zmart-api
# Ensures Claude always works in the zmart-api directory

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ZMART_API_DIR="/Users/dansidanutz/Desktop/ZmartBot/zmart-api"

echo -e "${BLUE}🎯 Claude Code zmart-api Workspace Setup${NC}"
echo "======================================="

# Function to check if we're in the right directory
check_directory() {
    current_dir=$(pwd)
    if [[ "$current_dir" == "$ZMART_API_DIR" ]]; then
        echo -e "${GREEN}✅ Already in zmart-api directory${NC}"
        return 0
    else
        echo -e "${YELLOW}📁 Current directory: $current_dir${NC}"
        echo -e "${YELLOW}🎯 Target directory: $ZMART_API_DIR${NC}"
        return 1
    fi
}

# Function to set up environment
setup_environment() {
    echo -e "${BLUE}🔧 Setting up Claude workspace environment...${NC}"
    
    # Set environment variables
    export WORKING_DIR="$ZMART_API_DIR"
    export PROJECT_ROOT="$ZMART_API_DIR"
    export CLAUDE_WORKSPACE="zmart-api"
    
    # Change to zmart-api directory
    cd "$ZMART_API_DIR" || {
        echo -e "${RED}❌ Failed to change to zmart-api directory${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ Environment configured for zmart-api${NC}"
}

# Function to verify setup
verify_setup() {
    echo -e "${BLUE}🔍 Verifying workspace setup...${NC}"
    
    # Check current directory
    if ! check_directory; then
        echo -e "${RED}❌ Not in zmart-api directory${NC}"
        return 1
    fi
    
    # Check key files exist
    if [ -f "CLAUDE.md" ]; then
        echo -e "${GREEN}✅ CLAUDE.md found${NC}"
    else
        echo -e "${RED}❌ CLAUDE.md missing${NC}"
        return 1
    fi
    
    if [ -d "dashboard" ]; then
        echo -e "${GREEN}✅ Dashboard directory found${NC}"
    else
        echo -e "${RED}❌ Dashboard directory missing${NC}"
        return 1
    fi
    
    if [ -f "service_health_check.py" ]; then
        echo -e "${GREEN}✅ Service tools available${NC}"
    else
        echo -e "${YELLOW}⚠️ Service tools not found${NC}"
    fi
    
    return 0
}

# Function to show workspace info
show_workspace_info() {
    echo -e "${BLUE}📊 ZmartBot zmart-api Workspace${NC}"
    echo "Working Directory: $(pwd)"
    echo "Available Commands:"
    echo "  • ./service_health_check.py - Check all 25 services"
    echo "  • ./fix_services.sh - Fix service issues"  
    echo "  • ./start_service_dashboard.sh - Start dashboard"
    echo "  • ./verify_zmart_api_only.sh - Verify setup"
    echo ""
    echo "Dashboard URLs:"
    echo "  • Main: http://localhost:3401"
    echo "  • Health: http://localhost:3401/health"
    echo "  • Services: http://localhost:3401/api/services/status"
    echo ""
    echo -e "${GREEN}🎉 Ready to work in zmart-api!${NC}"
}

# Function to create reminder message
create_reminder() {
    cat > .claude_workspace_reminder.txt << EOF
🎯 CLAUDE WORKSPACE REMINDER
===========================

You are working in the zmart-api folder only.
Working Directory: /Users/dansidanutz/Desktop/ZmartBot/zmart-api

RULES:
✅ Use relative paths only (./dashboard/, src/, etc.)
❌ Never use /Users/dansidanutz/Desktop/ZmartBot/anything-outside-zmart-api/
❌ Never reference parent directories with ../

QUICK COMMANDS:
• ./service_health_check.py
• ./fix_services.sh
• ./start_service_dashboard.sh

DASHBOARD: http://localhost:3401

Generated: $(date)
EOF
    
    echo -e "${GREEN}✅ Workspace reminder created${NC}"
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup")
            setup_environment
            verify_setup && show_workspace_info
            create_reminder
            ;;
        "check")
            check_directory && verify_setup
            ;;
        "info")
            show_workspace_info
            ;;
        "cd")
            echo "cd $ZMART_API_DIR"
            ;;
        *)
            echo "Usage: $0 [setup|check|info|cd]"
            echo ""
            echo "Commands:"
            echo "  setup - Set up Claude workspace (default)"
            echo "  check - Check if in correct directory"
            echo "  info  - Show workspace information"
            echo "  cd    - Print change directory command"
            ;;
    esac
}

# Run main function
main "$@"