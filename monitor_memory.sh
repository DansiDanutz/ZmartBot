#!/bin/bash

# Memory Monitoring Script
# Quick overview of memory usage

echo "=========================================="
echo "📊 Memory Usage Monitor"
echo "=========================================="

# Current timestamp
echo "Time: $(date)"
echo ""

# System memory overview
echo "🖥️  System Memory Overview:"
echo "------------------------------------------"
vm_stat | grep -E "(Pages free|Pages active|Pages inactive|Pages speculative|Pages wired down)" | while read line; do
    echo "  $line"
done

echo ""
echo "📈 Memory Pressure:"
echo "------------------------------------------"
memory_pressure | head -3

echo ""
echo "🔝 Top 10 Memory Consumers:"
echo "------------------------------------------"
ps aux | sort -k6 -nr | head -10 | awk '{printf "  %-8s %-8s %-30s\n", $2, int($6/1024)"MB", $11}'

echo ""
echo "🌐 WebKit Processes:"
echo "------------------------------------------"
webkit_processes=$(ps aux | grep -i webkit | grep -v grep)
if [ -n "$webkit_processes" ]; then
    echo "$webkit_processes" | awk '{printf "  %-8s %-8s %-30s\n", $2, int($6/1024)"MB", $11}'
else
    echo "  ✅ No WebKit processes found"
fi

echo ""
echo "🔧 Cursor/VS Code Processes:"
echo "------------------------------------------"
cursor_processes=$(ps aux | grep -i cursor | grep -v grep)
if [ -n "$cursor_processes" ]; then
    echo "$cursor_processes" | awk '{printf "  %-8s %-8s %-30s\n", $2, int($6/1024)"MB", $11}'
else
    echo "  ✅ No Cursor processes found"
fi

echo ""
echo "🐍 Python Processes:"
echo "------------------------------------------"
python_processes=$(ps aux | grep python | grep -v grep)
if [ -n "$python_processes" ]; then
    echo "$python_processes" | awk '{printf "  %-8s %-8s %-30s\n", $2, int($6/1024)"MB", $11}'
else
    echo "  ✅ No Python processes found"
fi

echo ""
echo "📦 Node.js Processes:"
echo "------------------------------------------"
node_processes=$(ps aux | grep node | grep -v grep)
if [ -n "$node_processes" ]; then
    echo "$node_processes" | awk '{printf "  %-8s %-8s %-30s\n", $2, int($6/1024)"MB", $11}'
else
    echo "  ✅ No Node.js processes found"
fi

echo ""
echo "=========================================="
echo "💡 Quick Actions:"
echo "  • Run memory optimization: ./optimize_memory.sh"
echo "  • Kill high-memory processes: ./kill_high_memory_processes.sh"
echo "  • Monitor continuously: watch -n 5 ./monitor_memory.sh"
echo "=========================================="













