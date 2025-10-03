#!/bin/bash

# ZmartBot Memory Optimization Script
# This script helps reduce memory usage by cleaning up processes and caches

echo "=========================================="
echo "🧹 ZmartBot Memory Optimization Starting..."
echo "=========================================="

# Function to kill high-memory WebKit processes
cleanup_webkit_processes() {
    echo ""
    echo "🔍 Step 1: Analyzing WebKit Memory Usage..."
    echo "------------------------------------------"
    
    # Get WebKit processes using more than 500MB
    webkit_processes=$(ps aux | grep -i webkit | awk '$6 > 500000 {print $2, $6/1024}' | sort -k2 -nr)
    
    if [ -n "$webkit_processes" ]; then
        echo "Found high-memory WebKit processes:"
        echo "$webkit_processes"
        echo ""
        echo "⚠️  These processes are consuming significant memory."
        echo "   Consider closing browser tabs or applications using WebKit."
        echo ""
        echo "To kill specific processes, use:"
        echo "   kill -9 <PID>"
        echo ""
    else
        echo "✅ No high-memory WebKit processes found."
    fi
}

# Function to clean up Python cache and temp files
cleanup_python_cache() {
    echo ""
    echo "🐍 Step 2: Cleaning Python Cache..."
    echo "------------------------------------------"
    
    # Find and remove Python cache files
    find /Users/dansidanutz/Desktop/ZmartBot -name "*.pyc" -delete 2>/dev/null
    find /Users/dansidanutz/Desktop/ZmartBot -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find /Users/dansidanutz/Desktop/ZmartBot -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
    
    echo "✅ Python cache files cleaned."
}

# Function to clean up Node.js cache
cleanup_node_cache() {
    echo ""
    echo "📦 Step 3: Cleaning Node.js Cache..."
    echo "------------------------------------------"
    
    # Clean npm cache
    if command -v npm >/dev/null 2>&1; then
        npm cache clean --force 2>/dev/null
        echo "✅ npm cache cleaned."
    fi
    
    # Clean node_modules if they exist in temp locations
    find /tmp -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null
    echo "✅ Temporary node_modules cleaned."
}

# Function to clean up system temp files
cleanup_temp_files() {
    echo ""
    echo "🗑️  Step 4: Cleaning Temporary Files..."
    echo "------------------------------------------"
    
    # Clean up common temp files
    find /Users/dansidanutz/Desktop/ZmartBot -name ".DS_Store" -delete 2>/dev/null
    find /Users/dansidanutz/Desktop/ZmartBot -name "*.log" -mtime +7 -delete 2>/dev/null
    find /Users/dansidanutz/Desktop/ZmartBot -name "*.tmp" -delete 2>/dev/null
    
    # Clean up system temp files
    rm -rf /tmp/zmartbot_* 2>/dev/null
    rm -rf /tmp/claude-* 2>/dev/null
    
    echo "✅ Temporary files cleaned."
}

# Function to show memory usage summary
show_memory_summary() {
    echo ""
    echo "📊 Step 5: Memory Usage Summary..."
    echo "------------------------------------------"
    
    # Show top memory consumers
    echo "Top 10 Memory Consumers:"
    ps aux | sort -k6 -nr | head -10 | awk '{printf "%-8s %-20s %8s MB\n", $2, $11, $6/1024}'
    
    echo ""
    echo "System Memory Info:"
    vm_stat | grep -E "(Pages free|Pages active|Pages inactive|Pages speculative|Pages wired down)"
    
    echo ""
    echo "Available Memory:"
    memory_pressure | head -5
}

# Function to suggest memory optimization actions
suggest_optimizations() {
    echo ""
    echo "💡 Memory Optimization Suggestions..."
    echo "------------------------------------------"
    echo ""
    echo "1. 🌐 Browser Memory:"
    echo "   - Close unused browser tabs"
    echo "   - Restart your browser if it's using >2GB"
    echo "   - Disable unnecessary browser extensions"
    echo ""
    echo "2. 🖥️  Applications:"
    echo "   - Close unused applications (especially GIMP, which uses 538MB)"
    echo "   - Quit applications you're not actively using"
    echo ""
    echo "3. 🔧 Development Tools:"
    echo "   - Restart Cursor/VS Code if it's using excessive memory"
    echo "   - Close unused terminal windows"
    echo "   - Disable unused extensions"
    echo ""
    echo "4. 🐍 Python Processes:"
    echo "   - Kill any hanging Python processes"
    echo "   - Restart Python virtual environments"
    echo ""
    echo "5. 📦 Node.js Processes:"
    echo "   - Kill any hanging Node.js processes"
    echo "   - Clear npm cache regularly"
    echo ""
}

# Function to kill specific high-memory processes (with confirmation)
kill_high_memory_processes() {
    echo ""
    echo "⚠️  High Memory Process Management..."
    echo "------------------------------------------"
    
    # Get processes using more than 1GB
    high_memory_processes=$(ps aux | awk '$6 > 1000000 && $11 !~ /^\[/ {print $2, $6/1024, $11}' | sort -k2 -nr)
    
    if [ -n "$high_memory_processes" ]; then
        echo "Processes using >1GB memory:"
        echo "PID     Memory(MB)  Command"
        echo "$high_memory_processes"
        echo ""
        echo "To kill a specific process: kill -9 <PID>"
        echo "To kill all WebKit processes: pkill -f WebKit"
        echo ""
    fi
}

# Main execution
main() {
    cleanup_webkit_processes
    cleanup_python_cache
    cleanup_node_cache
    cleanup_temp_files
    show_memory_summary
    suggest_optimizations
    kill_high_memory_processes
    
    echo ""
    echo "=========================================="
    echo "✅ Memory Optimization Complete!"
    echo "=========================================="
    echo ""
    echo "📌 Quick Commands:"
    echo "  • Kill WebKit: pkill -f WebKit"
    echo "  • Kill Python: pkill -f python"
    echo "  • Kill Node: pkill -f node"
    echo "  • Restart Cursor: killall 'Cursor Helper'"
    echo ""
    echo "📊 Monitor Memory:"
    echo "  • top -o rsize"
    echo "  • Activity Monitor"
    echo "  • memory_pressure"
    echo ""
}

# Run the main function
main













