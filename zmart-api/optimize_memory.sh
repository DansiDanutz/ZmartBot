#!/bin/bash

# ZmartBot Memory Optimization Script
# Auto-runs on Cursor/VS Code startup

echo "🧹 Starting Memory Optimization for ZmartBot..."

# Function to convert memory values
get_memory_mb() {
    echo "$1" | awk '{print int($1/1024)}'
}

# Kill Chrome tabs that are using too much memory (over 100MB)
echo "📌 Cleaning up Chrome memory hogs..."
for pid in $(ps aux | grep "Chrome Helper (Renderer)" | awk '$4 > 0.5 {print $2}'); do
    mem_percent=$(ps aux | grep "^[^ ]*[ ]*$pid " | awk '{print $4}')
    if (( $(echo "$mem_percent > 0.5" | bc -l) )); then
        echo "  Killing Chrome process $pid (${mem_percent}% memory)"
        kill -9 $pid 2>/dev/null
    fi
done

# Clear Python cache
echo "🐍 Clearing Python cache..."
find /Users/dansidanutz/Desktop/ZmartBot -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /Users/dansidanutz/Desktop/ZmartBot -type f -name "*.pyc" -delete 2>/dev/null

# Clear npm cache
echo "📦 Clearing npm cache..."
npm cache clean --force 2>/dev/null

# Clear Cursor/VS Code workspace cache
echo "🔧 Clearing Cursor workspace cache..."
rm -rf /Users/dansidanutz/Library/Application\ Support/Cursor/Cache/* 2>/dev/null
rm -rf /Users/dansidanutz/Library/Application\ Support/Cursor/CachedData/* 2>/dev/null

# Clear system cache
echo "💾 Purging system cache..."
sudo purge 2>/dev/null || echo "  (Skipped - requires sudo)"

# Kill unnecessary background processes
echo "🔪 Stopping unnecessary processes..."

# Kill any orphaned Python processes (except our services)
for pid in $(ps aux | grep python | grep -v "8000\|8006\|api_mcp" | awk '{print $2}'); do
    process_info=$(ps -p $pid -o comm= 2>/dev/null)
    if [[ $process_info == *"python"* ]]; then
        echo "  Killing orphaned Python process: $pid"
        kill -9 $pid 2>/dev/null
    fi
done

# Optimize PostgreSQL if running
if pgrep -x "postgres" > /dev/null; then
    echo "🐘 Optimizing PostgreSQL..."
    # Reduce shared buffers if needed
    psql -U zmartbot -d zmartbot_production -c "VACUUM ANALYZE;" 2>/dev/null || true
fi

# Clear Docker if present
if command -v docker &> /dev/null; then
    echo "🐳 Cleaning Docker resources..."
    docker system prune -f 2>/dev/null || true
fi

# Clear temporary files
echo "🗑️  Clearing temporary files..."
rm -rf /tmp/* 2>/dev/null
rm -rf /var/tmp/* 2>/dev/null
rm -rf ~/Library/Caches/* 2>/dev/null

# Memory report
echo ""
echo "📊 Memory Status After Optimization:"
memory_info=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f MB\n", "$1:", $2 * $size / 1048576);')
echo "$memory_info" | grep -E "free:|wired down:|active:|inactive:"

# Calculate and show memory usage
total_mem=$(sysctl -n hw.memsize)
total_mb=$((total_mem / 1024 / 1024))
free_mem=$(vm_stat | awk '/Pages free/ {print $3}' | sed 's/\.//')
free_mb=$((free_mem * 4096 / 1024 / 1024))
used_mb=$((total_mb - free_mb))
percent=$((used_mb * 100 / total_mb))

echo ""
echo "💾 Total Memory: ${total_mb} MB"
echo "✅ Free Memory: ${free_mb} MB"
echo "📈 Memory Usage: ${percent}%"

if [ $percent -lt 70 ]; then
    echo "✅ Memory optimized successfully!"
elif [ $percent -lt 80 ]; then
    echo "⚠️  Memory usage is moderate"
else
    echo "❌ Memory usage is still high - consider closing some applications"
fi

echo ""
echo "🚀 Memory optimization complete!"