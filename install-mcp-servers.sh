#!/bin/bash

echo "MCP Server Installation Script"
echo "=============================="
echo ""

check_and_install() {
    local package_name=$1
    local display_name=$2

    echo "Checking $display_name..."

    if npm list -g "$package_name" 2>/dev/null | grep -q "$package_name"; then
        echo "✅ $display_name is already installed"
        npm list -g "$package_name" 2>/dev/null | grep "$package_name"
    else
        echo "📦 Installing $display_name..."
        npm install -g "$package_name"
        if [ $? -eq 0 ]; then
            echo "✅ $display_name installed successfully"
        else
            echo "❌ Failed to install $display_name"
            return 1
        fi
    fi
    echo ""
}

echo "Starting MCP server installations..."
echo ""

check_and_install "@supabase/mcp-server-supabase" "Supabase MCP Server"

check_and_install "mcp-server-browser" "Browser MCP Server"

check_and_install "byterover-mcp" "Byterover MCP Server"

check_and_install "firecrawl-mcp" "Firecrawl MCP Server"

check_and_install "shadcn-mcp" "Shadcn MCP Server"

echo ""
echo "Installation Summary:"
echo "===================="
npm list -g --depth=0 2>/dev/null | grep -E "(supabase/mcp|mcp-server-browser|byterover-mcp|firecrawl-mcp|shadcn-mcp)" || echo "No MCP servers found"

echo ""
echo "Checking executable paths..."
echo "============================"
which mcp-server-browser byterover-mcp shadcn-mcp 2>&1

echo ""
echo "Claude Desktop Config Location:"
echo "================================"
echo "~/Desktop/ZmartBot/claude_desktop_config.json"

echo ""
echo "To use these MCP servers:"
echo "1. Restart Claude Desktop application"
echo "2. Check the MCP status in Claude Desktop settings"
echo "3. The servers should now be available in your Claude conversations"

echo ""
echo "✅ MCP Server installation script completed!"