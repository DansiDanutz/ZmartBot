#!/bin/bash

# Claude Code Diagnostics Script
# Comprehensive health check for Claude Code and MCP servers

echo "🏥 Claude Code Diagnostics"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
ISSUES=0
WARNINGS=0
SUCCESS=0

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1 is installed"
        ((SUCCESS++))
        return 0
    else
        echo -e "${RED}❌${NC} $1 is not installed"
        ((ISSUES++))
        return 1
    fi
}

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2 exists"
        ((SUCCESS++))
        return 0
    else
        echo -e "${RED}❌${NC} $2 missing: $1"
        ((ISSUES++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2 exists"
        ((SUCCESS++))
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $2 missing: $1"
        ((WARNINGS++))
        return 1
    fi
}

# Function to check service running
check_service() {
    if lsof -Pi :$2 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✅${NC} $1 is running on port $2"
        ((SUCCESS++))
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $1 is not running on port $2"
        ((WARNINGS++))
        return 1
    fi
}

echo -e "${BLUE}1. System Requirements${NC}"
echo "------------------------"

# Check Node.js
if check_command node; then
    NODE_VERSION=$(node --version)
    echo "   Node version: $NODE_VERSION"
fi

# Check npm
if check_command npm; then
    NPM_VERSION=$(npm --version)
    echo "   NPM version: $NPM_VERSION"
fi

# Check Python
if check_command python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "   Python version: $PYTHON_VERSION"
fi

# Check Git
if check_command git; then
    GIT_VERSION=$(git --version)
    echo "   Git version: $GIT_VERSION"
fi

echo ""
echo -e "${BLUE}2. Claude Code Installation${NC}"
echo "----------------------------"

# Check Claude Code CLI
if check_command claude; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "version check failed")
    echo "   Claude version: $CLAUDE_VERSION"
fi

# Check Claude configuration
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if check_file "$CLAUDE_CONFIG" "Claude config"; then
    # Count MCP servers
    if command -v jq &> /dev/null; then
        MCP_COUNT=$(jq '.mcpServers | length' "$CLAUDE_CONFIG" 2>/dev/null || echo 0)
        echo "   MCP servers configured: $MCP_COUNT"
    else
        echo "   Install jq to analyze config: brew install jq"
    fi
fi

echo ""
echo -e "${BLUE}3. MCP Servers Status${NC}"
echo "---------------------"

# Check if Claude config exists and parse MCP servers
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "Checking MCP server configurations..."

    # List configured MCP servers (without jq fallback)
    if command -v jq &> /dev/null; then
        SERVERS=$(jq -r '.mcpServers | keys[]' "$CLAUDE_CONFIG" 2>/dev/null)
        for server in $SERVERS; do
            echo -e "${BLUE}   • $server${NC}"
        done
    else
        # Basic grep approach
        grep -o '"[^"]*":\s*{' "$CLAUDE_CONFIG" | grep -o '"[^"]*"' | while read server; do
            server_clean=${server//\"/}
            echo -e "${BLUE}   • $server_clean${NC}"
        done
    fi
else
    echo -e "${RED}❌${NC} Claude config not found"
    ((ISSUES++))
fi

echo ""
echo -e "${BLUE}4. Project Services${NC}"
echo "-------------------"

# Check API Manager
check_service "API Manager" 8006

# Check Main API Server
check_service "Main API Server" 8000

# Check MDC Dashboard
check_service "MDC Dashboard" 3001

echo ""
echo -e "${BLUE}5. Project Structure${NC}"
echo "--------------------"

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"

check_dir "$PROJECT_ROOT" "Project root"
check_dir "$PROJECT_ROOT/zmart-api" "API directory"
check_dir "$PROJECT_ROOT/ZmartyChat" "Chat directory"
check_dir "$PROJECT_ROOT/.cursor/rules" "MDC rules"

echo ""
echo -e "${BLUE}6. Exchange Configurations${NC}"
echo "--------------------------"

CCXT_CONFIG="$PROJECT_ROOT/ccxt-exchanges-config.json"
if check_file "$CCXT_CONFIG" "CCXT config"; then
    if command -v jq &> /dev/null; then
        EXCHANGE_COUNT=$(jq '.accounts | length' "$CCXT_CONFIG" 2>/dev/null || echo 0)
        echo "   Configured exchanges: $EXCHANGE_COUNT"
    fi
fi

echo ""
echo -e "${BLUE}7. Background Services${NC}"
echo "----------------------"

# Check if background agent is installed
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.zmartbot.api-mcp-agent.plist"
if [ -f "$LAUNCH_AGENT" ]; then
    echo -e "${GREEN}✅${NC} Background agent installed"
    ((SUCCESS++))

    # Check if running
    if launchctl list | grep -q "com.zmartbot.api-mcp-agent"; then
        echo -e "${GREEN}✅${NC} Background agent running"
        ((SUCCESS++))
    else
        echo -e "${YELLOW}⚠️${NC} Background agent not running"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️${NC} Background agent not installed"
    ((WARNINGS++))
fi

echo ""
echo -e "${BLUE}8. NPM Package Check${NC}"
echo "--------------------"

# Check key npm packages
PACKAGES=(
    "@anthropic-ai/claude-code"
    "@supabase/mcp-server-supabase"
    "firecrawl-mcp"
    "@agent-infra/mcp-server-browser"
    "@lazydino/ccxt-mcp"
)

for pkg in "${PACKAGES[@]}"; do
    if npm list -g "$pkg" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $pkg"
        ((SUCCESS++))
    else
        echo -e "${YELLOW}⚠️${NC} $pkg not globally installed"
        ((WARNINGS++))
    fi
done

echo ""
echo "================================"
echo -e "${BLUE}📊 Diagnostics Summary${NC}"
echo "================================"
echo -e "${GREEN}Success:${NC} $SUCCESS checks passed"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS potential issues"
echo -e "${RED}Issues:${NC} $ISSUES critical problems"

echo ""
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 System is healthy!${NC}"
else
    echo -e "${RED}⚠️ Critical issues detected${NC}"
    echo ""
    echo "Recommended fixes:"
    echo "1. Update Claude Code: npm update -g @anthropic-ai/claude-code"
    echo "2. Install missing packages"
    echo "3. Start required services"
fi

if [ $WARNINGS -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}📝 Recommendations:${NC}"
    echo "• Install background agent: ./install-background-agent.sh"
    echo "• Start API Manager: ./start-api-mcp-integration.sh"
    echo "• Install jq for better diagnostics: brew install jq"
fi

echo ""
echo -e "${BLUE}📋 Quick Actions:${NC}"
echo "1. Start all services: ./start-all-services.sh"
echo "2. Check MCP servers: Restart Claude Desktop and check Developer tab"
echo "3. View logs: tail -f zmart-api/logs/*.log"
echo "4. Test connections: curl http://localhost:8006/health"

exit $ISSUES