#!/bin/bash

# Install API-MCP Background Agent
# This script installs the background agent as a macOS LaunchAgent

echo "🤖 Installing API-MCP Background Agent"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
AGENT_SCRIPT="$PROJECT_ROOT/zmart-api/api_mcp_background_agent.py"
PLIST_FILE="$PROJECT_ROOT/zmart-api/api_mcp_agent.plist"
LAUNCHAGENT_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCHAGENT_DIR/com.zmartbot.api-mcp-agent.plist"

# Function to check if agent is running
check_agent_running() {
    if launchctl list | grep -q "com.zmartbot.api-mcp-agent"; then
        return 0
    else
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

    pip3 install watchdog requests cryptography flask flask-cors > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
}

# Function to create directories
create_directories() {
    echo -e "${YELLOW}📁 Creating required directories...${NC}"

    mkdir -p "$PROJECT_ROOT/zmart-api/logs"
    mkdir -p "$PROJECT_ROOT/zmart-api/api_keys_manager"

    echo -e "${GREEN}✅ Directories created${NC}"
}

# Function to install the agent
install_agent() {
    echo -e "${YELLOW}🔧 Installing background agent...${NC}"

    # Copy plist to LaunchAgents
    cp "$PLIST_FILE" "$INSTALLED_PLIST"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Agent installed to LaunchAgents${NC}"
    else
        echo -e "${RED}❌ Failed to install agent${NC}"
        exit 1
    fi
}

# Function to start the agent
start_agent() {
    echo -e "${YELLOW}🚀 Starting background agent...${NC}"

    # Load the agent
    launchctl load "$INSTALLED_PLIST" 2>/dev/null

    sleep 3

    if check_agent_running; then
        echo -e "${GREEN}✅ Background agent started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start background agent${NC}"
        echo -e "${YELLOW}Check logs at: $PROJECT_ROOT/zmart-api/logs/${NC}"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo ""
    echo -e "${BLUE}📊 Agent Status:${NC}"
    echo "================================"

    if check_agent_running; then
        echo -e "Status: ${GREEN}RUNNING${NC}"

        # Show recent log entries
        if [ -f "$PROJECT_ROOT/zmart-api/logs/api_mcp_agent.log" ]; then
            echo ""
            echo -e "${BLUE}Recent logs:${NC}"
            tail -n 5 "$PROJECT_ROOT/zmart-api/logs/api_mcp_agent.log"
        fi
    else
        echo -e "Status: ${RED}NOT RUNNING${NC}"
    fi

    echo ""
    echo -e "${BLUE}📍 Important Locations:${NC}"
    echo "• Agent Script: $AGENT_SCRIPT"
    echo "• Logs: $PROJECT_ROOT/zmart-api/logs/"
    echo "• LaunchAgent: $INSTALLED_PLIST"
}

# Function to uninstall the agent
uninstall_agent() {
    echo -e "${YELLOW}🗑️  Uninstalling background agent...${NC}"

    # Stop the agent
    launchctl unload "$INSTALLED_PLIST" 2>/dev/null

    # Remove plist
    rm -f "$INSTALLED_PLIST"

    echo -e "${GREEN}✅ Background agent uninstalled${NC}"
}

# Main menu
main() {
    echo ""
    echo "Choose an option:"
    echo "1) Install and start agent"
    echo "2) Stop agent"
    echo "3) Start agent"
    echo "4) Show status"
    echo "5) View logs"
    echo "6) Uninstall agent"
    echo "7) Exit"
    echo ""
    read -p "Option [1-7]: " choice

    case $choice in
        1)
            install_dependencies
            create_directories

            # Stop if already running
            if check_agent_running; then
                echo -e "${YELLOW}Stopping existing agent...${NC}"
                launchctl unload "$INSTALLED_PLIST" 2>/dev/null
                sleep 2
            fi

            install_agent
            start_agent
            show_status
            ;;
        2)
            if check_agent_running; then
                launchctl unload "$INSTALLED_PLIST" 2>/dev/null
                echo -e "${GREEN}✅ Agent stopped${NC}"
            else
                echo -e "${YELLOW}Agent is not running${NC}"
            fi
            ;;
        3)
            if check_agent_running; then
                echo -e "${YELLOW}Agent is already running${NC}"
            else
                start_agent
            fi
            ;;
        4)
            show_status
            ;;
        5)
            echo -e "${BLUE}📜 Showing recent logs:${NC}"
            echo "================================"
            tail -f "$PROJECT_ROOT/zmart-api/logs/api_mcp_agent.log"
            ;;
        6)
            uninstall_agent
            ;;
        7)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            main
            ;;
    esac
}

# Show header
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   API-MCP Background Agent Installer  ║${NC}"
echo -e "${BLUE}║        ZmartBot Platform v1.0         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Run main menu
main