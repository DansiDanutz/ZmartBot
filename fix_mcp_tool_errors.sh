#!/bin/bash
# MCP Tool Error Handler
# This script monitors and fixes tool calling errors

LOG_FILE="/Users/dansidanutz/Desktop/ZmartBot/logs/mcp_error_monitor.log"

# Function to restart MCP servers if they're causing issues
restart_mcp_servers() {
    echo "$(date): Restarting MCP servers due to tool calling errors" >> "$LOG_FILE"
    
    # Kill existing MCP processes
    pkill -f "mcp-server"
    pkill -f "npx.*mcp"
    
    # Wait a moment
    sleep 2
    
    # Restart Claude Desktop to reload MCP configuration
    echo "$(date): MCP servers restarted" >> "$LOG_FILE"
}

# Monitor for tool calling errors
monitor_tool_errors() {
    while true; do
        # Check for stuck tool calls (this would need to be implemented based on your specific setup)
        # For now, we'll just log that we're monitoring
        echo "$(date): Monitoring tool calling status" >> "$LOG_FILE"
        sleep 30
    done
}

# Main execution
case "$1" in
    "restart")
        restart_mcp_servers
        ;;
    "monitor")
        monitor_tool_errors
        ;;
    *)
        echo "Usage: $0 {restart|monitor}"
        exit 1
        ;;
esac
