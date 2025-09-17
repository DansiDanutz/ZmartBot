#!/bin/bash

# ZmartBot Sync Management Script
# Easy management of all sync operations

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}🔄 ZmartBot Sync Management${NC}"
    echo "=========================="
    echo ""
    echo "Commands:"
    echo "  status    - Show sync status"
    echo "  start     - Start auto-sync service"
    echo "  stop      - Stop auto-sync service"
    echo "  restart   - Restart auto-sync service"
    echo "  sync      - Manual sync once"
    echo "  diff      - Show folder differences"
    echo "  logs      - Show sync logs"
    echo "  test      - Test sync functionality"
    echo "  help      - Show this help"
    echo ""
    echo "Quick commands:"
    echo "  ./sync.sh         - Quick manual sync"
    echo "  ./manage_sync.sh  - Show this help"
    echo ""
}

show_status() {
    echo -e "${BLUE}🔍 ZmartBot Sync Status${NC}"
    echo "======================"
    echo ""
    
    # Check always-sync status
    ./sync_always.sh status
    
    # Check folder sync status
    echo ""
    echo -e "${BLUE}📊 Folder Status:${NC}"
    ./sync_claude_folders.sh diff | grep -E "(✅|⚠️|❌)"
    
    # Check logs
    if [ -f "/tmp/zmartbot-sync-always.log" ]; then
        echo ""
        echo -e "${BLUE}📝 Recent Activity:${NC}"
        tail -5 /tmp/zmartbot-sync-always.log
    fi
}

show_logs() {
    echo -e "${BLUE}📝 ZmartBot Sync Logs${NC}"
    echo "===================="
    echo ""
    
    if [ -f "/tmp/zmartbot-sync-always.log" ]; then
        echo -e "${YELLOW}Main sync log:${NC}"
        tail -20 /tmp/zmartbot-sync-always.log
    else
        echo "No logs found"
    fi
}

test_sync() {
    echo -e "${BLUE}🧪 Testing Sync Functionality${NC}"
    echo "============================="
    echo ""
    
    # Test basic sync
    echo "1. Testing basic sync..."
    if ./sync_claude_folders.sh sync; then
        echo -e "${GREEN}✅ Basic sync works${NC}"
    else
        echo -e "${RED}❌ Basic sync failed${NC}"
        return 1
    fi
    
    # Test file monitoring
    echo ""
    echo "2. Testing file monitoring..."
    if command -v fswatch &> /dev/null; then
        echo -e "${GREEN}✅ File monitoring available (fswatch installed)${NC}"
    else
        echo -e "${YELLOW}⚠️ File monitoring not available (fswatch not installed)${NC}"
    fi
    
    # Test folder differences
    echo ""
    echo "3. Testing difference detection..."
    ./sync_claude_folders.sh diff
    
    echo ""
    echo -e "${GREEN}🎉 Sync test complete!${NC}"
}

# Main command handling
case "${1:-help}" in
    "status"|"s")
        show_status
        ;;
    "start")
        ./sync_always.sh start
        ;;
    "stop")
        ./sync_always.sh stop
        ;;
    "restart")
        ./sync_always.sh restart
        ;;
    "sync")
        ./sync_claude_folders.sh sync
        ;;
    "diff")
        ./sync_claude_folders.sh diff
        ;;
    "logs"|"log")
        show_logs
        ;;
    "test")
        test_sync
        ;;
    "help"|"h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac