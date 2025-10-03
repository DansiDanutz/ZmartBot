#!/bin/bash

echo "=========================================="
echo "🎯 Targeted Memory Cleanup"
echo "=========================================="

# Function to safely kill a process
kill_process() {
    local pid=$1
    local name=$2
    local force=$3
    
    if ps -p $pid > /dev/null; then
        echo "🔪 Killing $name (PID: $pid)..."
        if [ "$force" = "true" ]; then
            kill -9 $pid
        else
            kill -TERM $pid
            sleep 2
            if ps -p $pid > /dev/null; then
                echo "   Force killing $name..."
                kill -9 $pid
            fi
        fi
        
        if [ $? -eq 0 ]; then
            echo "   ✅ Successfully killed $name"
        else
            echo "   ❌ Failed to kill $name"
        fi
    else
        echo "   Process $name (PID: $pid) not found"
    fi
}

echo ""
echo "🔍 Current High Memory Processes:"
echo "------------------------------------------"
ps aux | awk '{print $2, $4, $11}' | sort -k2 -nr | head -8

echo ""
echo "🎯 Targeting High Memory Consumers..."

# 1. Kill Virtualization Framework (6.6% memory - 1GB+)
echo ""
echo "1. 🖥️  Virtualization Framework (1GB+ memory)..."
VIRT_PID=$(ps aux | grep "com.apple.Virtualization.VirtualMachine" | grep -v grep | awk '{print $2}')
if [ -n "$VIRT_PID" ]; then
    kill_process $VIRT_PID "Virtualization Framework" "true"
else
    echo "   No Virtualization Framework process found"
fi

# 2. Kill high-memory Cursor Helper processes
echo ""
echo "2. 🖥️  High-memory Cursor Helper processes..."
CURSOR_HELPER_PIDS=$(ps aux | grep "Cursor Helper (Renderer)" | grep -v grep | awk '{print $2}')
if [ -n "$CURSOR_HELPER_PIDS" ]; then
    for pid in $CURSOR_HELPER_PIDS; do
        kill_process $pid "Cursor Helper (Renderer)" "false"
    done
else
    echo "   No high-memory Cursor Helper processes found"
fi

# 3. Kill TypeScript Server (if using too much memory)
echo ""
echo "3. 📝 TypeScript Server processes..."
TSSERVER_PIDS=$(ps aux | grep "tsserver" | grep -v grep | awk '{print $2}')
if [ -n "$TSSERVER_PIDS" ]; then
    for pid in $TSSERVER_PIDS; do
        kill_process $pid "TypeScript Server" "false"
    done
else
    echo "   No TypeScript Server processes found"
fi

# 4. Kill npm processes that might be hanging
echo ""
echo "4. 📦 Hanging npm processes..."
NPM_PIDS=$(ps aux | grep "npm exec" | grep -v grep | awk '{print $2}')
if [ -n "$NPM_PIDS" ]; then
    for pid in $NPM_PIDS; do
        kill_process $pid "npm exec" "false"
    done
else
    echo "   No hanging npm processes found"
fi

# 5. Kill node processes that might be hanging
echo ""
echo "5. 🟢 Hanging node processes..."
NODE_PIDS=$(ps aux | grep "node /Users/dansidanutz/.npm-cache-temp" | grep -v grep | awk '{print $2}')
if [ -n "$NODE_PIDS" ]; then
    for pid in $NODE_PIDS; do
        kill_process $pid "node npm-cache-temp" "false"
    done
else
    echo "   No hanging node processes found"
fi

echo ""
echo "🧹 Cleaning up temporary files..."
# Clean npm cache
npm cache clean --force > /dev/null 2>&1
echo "   ✅ npm cache cleaned"

# Clean temporary files
rm -rf /tmp/* > /dev/null 2>&1
echo "   ✅ temporary files cleaned"

echo ""
echo "📊 Memory Usage After Cleanup:"
echo "------------------------------------------"
ps aux | awk '{print $2, $4, $11}' | sort -k2 -nr | head -8

echo ""
echo "=========================================="
echo "✅ Targeted Memory Cleanup Complete!"
echo "=========================================="
echo ""
echo "💡 Recommendations:"
echo "   • Restart Cursor if it feels sluggish"
echo "   • Close unused browser tabs"
echo "   • Consider stopping Docker if not needed"
echo "   • Monitor memory usage with: ps aux | sort -k4 -nr | head -10"
echo ""
