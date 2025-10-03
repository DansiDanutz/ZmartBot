#!/bin/bash

# High Memory Process Killer Script
# Use with caution - this will terminate processes

echo "=========================================="
echo "⚠️  High Memory Process Management"
echo "=========================================="

# Function to show current high-memory processes
show_high_memory_processes() {
    echo ""
    echo "🔍 Current High Memory Processes (>500MB):"
    echo "------------------------------------------"
    ps aux | awk '$6 > 500000 && $11 !~ /^\[/ {printf "%-8s %-8s %-20s\n", $2, int($6/1024)"MB", $11}' | sort -k2 -nr
    echo ""
}

# Function to kill WebKit processes (with confirmation)
kill_webkit_processes() {
    echo ""
    echo "🌐 WebKit Process Management..."
    echo "------------------------------------------"
    
    webkit_count=$(ps aux | grep -i webkit | grep -v grep | wc -l)
    if [ $webkit_count -gt 0 ]; then
        echo "Found $webkit_count WebKit processes."
        echo "These are likely browser tabs or web applications."
        echo ""
        echo "⚠️  WARNING: This will close browser tabs and web apps!"
        echo ""
        read -p "Do you want to kill all WebKit processes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -f WebKit
            echo "✅ WebKit processes terminated."
        else
            echo "❌ WebKit processes left running."
        fi
    else
        echo "✅ No WebKit processes found."
    fi
}

# Function to restart Cursor IDE (with confirmation)
restart_cursor() {
    echo ""
    echo "🔧 Cursor IDE Management..."
    echo "------------------------------------------"
    
    cursor_count=$(ps aux | grep -i cursor | grep -v grep | wc -l)
    if [ $cursor_count -gt 0 ]; then
        echo "Found $cursor_count Cursor processes."
        echo "Cursor is using significant memory (~1GB total)."
        echo ""
        echo "⚠️  WARNING: This will close Cursor IDE!"
        echo ""
        read -p "Do you want to restart Cursor IDE? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            killall "Cursor Helper" 2>/dev/null
            killall "Cursor" 2>/dev/null
            echo "✅ Cursor IDE terminated."
            echo "💡 You can restart Cursor from Applications or Spotlight."
        else
            echo "❌ Cursor IDE left running."
        fi
    else
        echo "✅ No Cursor processes found."
    fi
}

# Function to kill specific high-memory processes
kill_specific_processes() {
    echo ""
    echo "🎯 Specific Process Management..."
    echo "------------------------------------------"
    
    # Show processes using more than 1GB
    high_memory=$(ps aux | awk '$6 > 1000000 && $11 !~ /^\[/ {print $2, int($6/1024), $11}')
    
    if [ -n "$high_memory" ]; then
        echo "Processes using >1GB memory:"
        echo "PID     Memory(MB)  Command"
        echo "$high_memory"
        echo ""
        echo "To kill a specific process, enter its PID:"
        read -p "Enter PID to kill (or press Enter to skip): " pid_to_kill
        
        if [ -n "$pid_to_kill" ] && [ "$pid_to_kill" -gt 0 ]; then
            echo "⚠️  Killing process $pid_to_kill..."
            kill -9 $pid_to_kill 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ Process $pid_to_kill terminated."
            else
                echo "❌ Failed to kill process $pid_to_kill."
            fi
        else
            echo "❌ No process killed."
        fi
    else
        echo "✅ No processes using >1GB memory found."
    fi
}

# Function to show memory improvement
show_memory_improvement() {
    echo ""
    echo "📊 Memory Usage After Cleanup..."
    echo "------------------------------------------"
    
    echo "Top 10 Memory Consumers:"
    ps aux | sort -k6 -nr | head -10 | awk '{printf "%-8s %-8s %-20s\n", $2, int($6/1024)"MB", $11}'
    
    echo ""
    echo "System Memory Pressure:"
    memory_pressure | head -3
}

# Main execution
main() {
    show_high_memory_processes
    
    echo "Choose an action:"
    echo "1) Kill WebKit processes (browser tabs)"
    echo "2) Restart Cursor IDE"
    echo "3) Kill specific high-memory process"
    echo "4) Show memory usage only"
    echo "5) Exit"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            kill_webkit_processes
            ;;
        2)
            restart_cursor
            ;;
        3)
            kill_specific_processes
            ;;
        4)
            show_memory_improvement
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting..."
            exit 1
            ;;
    esac
    
    show_memory_improvement
    
    echo ""
    echo "=========================================="
    echo "✅ Memory Management Complete!"
    echo "=========================================="
}

# Run the main function
main













