#!/bin/bash

# Quick Memory Fix Script
# Immediate actions to reduce memory usage

echo "=========================================="
echo "⚡ Quick Memory Fix - Immediate Actions"
echo "=========================================="

echo ""
echo "🎯 Current High Memory Processes:"
echo "------------------------------------------"
echo "• Cursor IDE: ~1.1GB (564MB + 435MB + 147MB)"
echo "• WebKit Process: 562MB (browser tab/app)"
echo "• Virtualization: 378MB"
echo "• TypeScript Server: 215MB"
echo "• Another WebKit: 190MB"
echo ""

echo "💡 Immediate Actions You Can Take:"
echo "------------------------------------------"
echo ""
echo "1. 🌐 BROWSER MEMORY (562MB + 190MB = 752MB):"
echo "   • Close unused browser tabs"
echo "   • Restart your browser"
echo "   • Kill WebKit processes: pkill -f WebKit"
echo ""
echo "2. 🔧 CURSOR IDE (1.1GB):"
echo "   • Close unused files/tabs in Cursor"
echo "   • Disable unused extensions"
echo "   • Restart Cursor IDE"
echo "   • Kill Cursor: killall 'Cursor Helper'"
echo ""
echo "3. 🖥️  VIRTUALIZATION (378MB):"
echo "   • Close any running VMs or containers"
echo "   • Kill virtualization: pkill -f Virtualization"
echo ""
echo "4. 📝 TYPESCRIPT SERVER (215MB):"
echo "   • Restart Cursor IDE (this will restart TypeScript server)"
echo ""

echo "🚀 Quick Commands to Run:"
echo "------------------------------------------"
echo ""
echo "# Kill high-memory WebKit processes (browser tabs)"
echo "pkill -f WebKit"
echo ""
echo "# Restart Cursor IDE"
echo "killall 'Cursor Helper'"
echo ""
echo "# Kill virtualization processes"
echo "pkill -f Virtualization"
echo ""
echo "# Check memory after cleanup"
echo "./monitor_memory.sh"
echo ""

echo "⚠️  WARNING: These commands will:"
echo "• Close browser tabs and web apps"
echo "• Close Cursor IDE (you'll need to restart it)"
echo "• Stop any running VMs/containers"
echo ""

read -p "Do you want to run these commands now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔧 Executing memory cleanup..."
    echo "------------------------------------------"
    
    echo "1. Killing WebKit processes..."
    pkill -f WebKit
    sleep 2
    
    echo "2. Killing Cursor IDE..."
    killall 'Cursor Helper' 2>/dev/null
    sleep 2
    
    echo "3. Killing virtualization processes..."
    pkill -f Virtualization
    sleep 2
    
    echo ""
    echo "✅ Memory cleanup complete!"
    echo ""
    echo "📊 Checking memory usage..."
    echo "------------------------------------------"
    sleep 3
    ./monitor_memory.sh
    
    echo ""
    echo "💡 Next Steps:"
    echo "• Restart Cursor IDE from Applications"
    echo "• Close unused browser tabs when you reopen your browser"
    echo "• Run './monitor_memory.sh' regularly to check memory usage"
    
else
    echo ""
    echo "❌ Memory cleanup cancelled."
    echo ""
    echo "💡 You can run these commands manually when ready:"
    echo "• pkill -f WebKit"
    echo "• killall 'Cursor Helper'"
    echo "• pkill -f Virtualization"
fi

echo ""
echo "=========================================="
echo "✅ Quick Memory Fix Complete!"
echo "=========================================="













