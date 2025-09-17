#!/bin/bash

# ZmartBot Claude Folders Sync Script
# Automatically synchronizes .claude and .cursor/rules folders between main and zmart-api

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
MAIN_DIR="/Users/dansidanutz/Desktop/ZmartBot"
API_DIR="/Users/dansidanutz/Desktop/ZmartBot/zmart-api"

echo -e "${BLUE}🔄 ZmartBot Folder Sync Script${NC}"
echo "======================================"

# Function to sync .claude folders
sync_claude_folders() {
    echo -e "${YELLOW}📁 Syncing .claude folders...${NC}"
    
    # Create directories if they don't exist
    mkdir -p "$API_DIR/.claude/contexts"
    
    # Sync from main to zmart-api
    echo "  • Syncing main -> zmart-api"
    rsync -av --delete "$MAIN_DIR/.claude/" "$API_DIR/.claude/"
    
    # Check if sync was successful
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ .claude folders synced successfully${NC}"
    else
        echo -e "  ${RED}❌ Failed to sync .claude folders${NC}"
        return 1
    fi
}

# Function to sync .cursor/rules folders
sync_cursor_rules() {
    echo -e "${YELLOW}📁 Syncing .cursor/rules folders...${NC}"
    
    # Create directories if they don't exist
    mkdir -p "$API_DIR/.cursor/rules"
    
    # Sync from main to zmart-api
    echo "  • Syncing main -> zmart-api"
    rsync -av --delete "$MAIN_DIR/.cursor/rules/" "$API_DIR/.cursor/rules/"
    
    # Check if sync was successful
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ .cursor/rules folders synced successfully${NC}"
    else
        echo -e "  ${RED}❌ Failed to sync .cursor/rules folders${NC}"
        return 1
    fi
}

# Function to create backup
create_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="/tmp/zmartbot_sync_backup_$timestamp"
    
    echo -e "${YELLOW}📦 Creating backup...${NC}"
    mkdir -p "$backup_dir"
    
    # Backup zmart-api folders before sync
    cp -r "$API_DIR/.claude" "$backup_dir/zmart-api_claude" 2>/dev/null || true
    cp -r "$API_DIR/.cursor/rules" "$backup_dir/zmart-api_cursor_rules" 2>/dev/null || true
    
    echo -e "  ${GREEN}✅ Backup created at: $backup_dir${NC}"
    echo "$backup_dir" > /tmp/zmartbot_last_backup
}

# Function to show differences
show_differences() {
    echo -e "${BLUE}📊 Analyzing differences...${NC}"
    
    echo "  • .claude folder differences:"
    if diff -r "$MAIN_DIR/.claude" "$API_DIR/.claude" >/dev/null 2>&1; then
        echo -e "    ${GREEN}✅ .claude folders are identical${NC}"
    else
        echo -e "    ${YELLOW}⚠️ .claude folders differ${NC}"
        diff -r "$MAIN_DIR/.claude" "$API_DIR/.claude" | head -10
    fi
    
    echo "  • .cursor/rules folder differences:"
    if diff -r "$MAIN_DIR/.cursor/rules" "$API_DIR/.cursor/rules" >/dev/null 2>&1; then
        echo -e "    ${GREEN}✅ .cursor/rules folders are identical${NC}"
    else
        echo -e "    ${YELLOW}⚠️ .cursor/rules folders differ${NC}"
        diff -r "$MAIN_DIR/.cursor/rules" "$API_DIR/.cursor/rules" | head -10
    fi
}

# Function to watch for changes (daemon mode)
watch_changes() {
    echo -e "${BLUE}👁️ Starting watch mode...${NC}"
    echo "Press Ctrl+C to stop monitoring"
    
    # Check if fswatch is available
    if ! command -v fswatch &> /dev/null; then
        echo -e "${RED}❌ fswatch not found. Installing via Homebrew...${NC}"
        brew install fswatch || {
            echo -e "${RED}❌ Failed to install fswatch. Please install it manually: brew install fswatch${NC}"
            return 1
        }
    fi
    
    # Monitor both directories for changes
    fswatch -o "$MAIN_DIR/.claude" "$MAIN_DIR/.cursor/rules" | while read f; do
        echo -e "${YELLOW}🔄 Changes detected, syncing...${NC}"
        sync_claude_folders
        sync_cursor_rules
        echo -e "${GREEN}✅ Sync complete at $(date)${NC}"
    done
}

# Function to install as service
install_service() {
    local plist_file="$HOME/Library/LaunchAgents/com.zmartbot.sync.plist"
    
    echo -e "${BLUE}🔧 Installing sync service...${NC}"
    
    cat > "$plist_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zmartbot.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>$MAIN_DIR/sync_claude_folders.sh</string>
        <string>--watch</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/zmartbot-sync.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/zmartbot-sync.error</string>
</dict>
</plist>
EOF
    
    # Load the service
    launchctl load "$plist_file"
    
    echo -e "${GREEN}✅ Sync service installed and started${NC}"
    echo "  • Logs: /tmp/zmartbot-sync.log"
    echo "  • Errors: /tmp/zmartbot-sync.error"
    echo "  • Unload with: launchctl unload $plist_file"
}

# Main function
main() {
    case "${1:-sync}" in
        "sync")
            create_backup
            show_differences
            sync_claude_folders
            sync_cursor_rules
            echo -e "${GREEN}🎉 All folders synced successfully!${NC}"
            ;;
        "watch" | "--watch")
            watch_changes
            ;;
        "diff" | "--diff")
            show_differences
            ;;
        "backup" | "--backup")
            create_backup
            ;;
        "install" | "--install")
            install_service
            ;;
        "help" | "--help" | "-h")
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  sync     Synchronize folders once (default)"
            echo "  watch    Watch for changes and sync automatically"
            echo "  diff     Show differences between folders"
            echo "  backup   Create backup only"
            echo "  install  Install as system service"
            echo "  help     Show this help message"
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Check if script has execute permissions
if [ ! -x "$0" ]; then
    echo -e "${YELLOW}⚠️ Making script executable...${NC}"
    chmod +x "$0"
fi

# Run main function
main "$@"