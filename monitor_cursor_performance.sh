#!/bin/bash

echo "=========================================="
echo "📊 Cursor Performance Monitor"
echo "=========================================="
echo "Time: $(date)"
echo ""

echo "🖥️  Cursor Processes:"
echo "------------------------------------------"
ps aux | grep -i cursor | grep -v grep | awk '{print "  " $2 "    " $3 "%    " $4 "%    " $11}'
echo ""

echo "💾 Memory Usage:"
echo "------------------------------------------"
ps aux | grep -i cursor | grep -v grep | awk '{sum+=$6} END {print "  Total Memory: " sum/1024 " MB"}'
echo ""

echo "🔌 MCP Servers Status:"
echo "------------------------------------------"
if [ -f "$HOME/.cursor/mcp.json" ]; then
    echo "  MCP Configuration: ✅ Found"
    grep -o '"command":\|"url":' "$HOME/.cursor/mcp.json" | wc -l | awk '{print "  Active Servers: " $1}'
else
    echo "  MCP Configuration: ❌ Not found"
fi
echo ""

echo "📁 Cache Status:"
echo "------------------------------------------"
CACHE_DIR="$HOME/Library/Application Support/Cursor/CachedData"
if [ -d "$CACHE_DIR" ]; then
    CACHE_SIZE=$(du -sh "$CACHE_DIR" 2>/dev/null | awk '{print $1}')
    echo "  Cache Size: $CACHE_SIZE"
else
    echo "  Cache: Not found"
fi
echo ""

echo "=========================================="
echo "💡 Performance Tips:"
echo "  • Restart Cursor if memory usage > 1GB"
echo "  • Clear cache if size > 500MB"
echo "  • Check MCP server status regularly"
echo "=========================================="
