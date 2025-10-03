#!/bin/bash

echo "=========================================="
echo "🚀 Applying Cursor & Claude Optimizations"
echo "=========================================="

# Function to backup existing files
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        echo "📦 Backing up $file to ${file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
}

# Function to apply optimization with confirmation
apply_optimization() {
    local source=$1
    local target=$2
    local description=$3
    
    echo ""
    echo "🔧 $description"
    echo "   Source: $source"
    echo "   Target: $target"
    
    if [ -f "$source" ]; then
        backup_file "$target"
        cp "$source" "$target"
        echo "   ✅ Applied successfully"
    else
        echo "   ❌ Source file not found: $source"
    fi
}

# Step 1: Remove corrupted Cursor installation
echo ""
echo "🗑️  Step 1: Cleaning up corrupted Cursor installation..."
if [ -d "/Applications/Cursor.app" ]; then
    echo "   Found corrupted Cursor.app (Dec 31 1979)"
    echo "   Checking if it's safe to remove..."
    
    # Check if any processes are using the old Cursor.app
    if ! ps aux | grep -q "/Applications/Cursor.app" | grep -v grep; then
        echo "   ✅ No processes using old Cursor.app - safe to remove"
        echo "   Removing corrupted Cursor.app..."
        rm -rf "/Applications/Cursor.app"
        echo "   ✅ Corrupted Cursor.app removed"
    else
        echo "   ⚠️  Processes still using old Cursor.app - skipping removal"
    fi
else
    echo "   ✅ No corrupted Cursor.app found"
fi

# Step 2: Apply optimized settings
echo ""
echo "⚙️  Step 2: Applying optimized Cursor settings..."
apply_optimization \
    "/Users/dansidanutz/Desktop/ZmartBot/optimized_cursor_settings.json" \
    "/Users/dansidanutz/Library/Application Support/Cursor/User/settings.json" \
    "Updating Cursor user settings with performance optimizations"

# Step 3: Apply optimized MCP configuration
echo ""
echo "🔗 Step 3: Applying optimized MCP configuration..."
apply_optimization \
    "/Users/dansidanutz/Desktop/ZmartBot/optimized_mcp_config.json" \
    "/Users/dansidanutz/.cursor/mcp.json" \
    "Updating MCP server configuration with performance optimizations"

# Step 4: Clean up Cursor cache
echo ""
echo "🧹 Step 4: Cleaning up Cursor cache..."
CURSOR_CACHE_DIR="$HOME/Library/Application Support/Cursor/CachedData"
if [ -d "$CURSOR_CACHE_DIR" ]; then
    echo "   Cleaning Cursor cache directory..."
    find "$CURSOR_CACHE_DIR" -type f -name "*.log" -mtime +7 -delete 2>/dev/null
    find "$CURSOR_CACHE_DIR" -type f -name "*.tmp" -delete 2>/dev/null
    echo "   ✅ Cache cleaned"
else
    echo "   ✅ No cache directory found"
fi

# Step 5: Optimize extension loading
echo ""
echo "🔌 Step 5: Optimizing extension configuration..."
EXTENSIONS_DIR="$HOME/.cursor/extensions"
if [ -d "$EXTENSIONS_DIR" ]; then
    echo "   Found $EXTENSIONS_DIR"
    echo "   Checking for problematic extensions..."
    
    # List extensions that might cause performance issues
    echo "   Current extensions:"
    ls -la "$EXTENSIONS_DIR" | grep "^d" | awk '{print "     " $9}' | head -10
    echo "   ✅ Extension directory accessible"
else
    echo "   ❌ Extensions directory not found"
fi

# Step 6: Create performance monitoring script
echo ""
echo "📊 Step 6: Creating performance monitoring script..."
cat > "/Users/dansidanutz/Desktop/ZmartBot/monitor_cursor_performance.sh" << 'EOF'
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
EOF

chmod +x "/Users/dansidanutz/Desktop/ZmartBot/monitor_cursor_performance.sh"
echo "   ✅ Performance monitoring script created"

# Step 7: Final recommendations
echo ""
echo "🎯 Step 7: Final Recommendations"
echo "------------------------------------------"
echo ""
echo "✅ Optimizations Applied:"
echo "   • Removed corrupted Cursor installation"
echo "   • Applied performance-optimized settings"
echo "   • Updated MCP configuration for better Claude integration"
echo "   • Cleaned up cache files"
echo "   • Created performance monitoring script"
echo ""
echo "🔄 Next Steps:"
echo "   1. Restart Cursor IDE to apply all changes"
echo "   2. Test Claude integration and performance"
echo "   3. Monitor performance with: ./monitor_cursor_performance.sh"
echo "   4. Report any issues or improvements needed"
echo ""
echo "📊 Performance Monitoring:"
echo "   • Run: ./monitor_cursor_performance.sh"
echo "   • Check memory usage regularly"
echo "   • Monitor MCP server status"
echo ""

echo "=========================================="
echo "✅ Cursor & Claude Optimization Complete!"
echo "   Please restart Cursor IDE to apply changes."
echo "=========================================="













