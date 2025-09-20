#!/bin/bash

# ZmartBot Autonomous System Auto-Install Script
# This script makes the system completely autonomous - no manual intervention needed

cd "$(dirname "$0")"

echo "🚀 ZmartBot Autonomous System Auto-Install"
echo "=========================================="

# 1. Enable auto-start in background optimization config
echo "📝 Enabling auto-start configuration..."
python3 -c "
import json
config_path = 'background_optimization_config.json'
with open(config_path, 'r') as f:
    config = json.load(f)
config['auto_start'] = True
config['system_integration']['create_launchd_plist'] = True
config['system_integration']['auto_start_on_boot'] = True
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print('✅ Auto-start configuration enabled')
"

# 2. Install LaunchAgent service
echo "🔧 Installing LaunchAgent service..."
python3 background_optimization_agent.py --install

# 3. Start the autonomous system
echo "🚀 Starting autonomous optimization system..."
./start_background_optimization_agent.sh

# 4. Verify installation
echo "✅ Verifying autonomous system status..."
sleep 5

# Check if LaunchAgent is loaded
if launchctl list | grep -q "com.zmartbot.background-optimization-agent"; then
    echo "✅ LaunchAgent service is loaded and will start on boot"
else
    echo "⚠️  LaunchAgent service not found in launchctl list"
fi

# Check if background agent is running
if pgrep -f "background_optimization_agent.py" > /dev/null; then
    echo "✅ Background optimization agent is running"
else
    echo "⚠️  Background optimization agent not running"
fi

# Check if optimization system is running
if pgrep -f "comprehensive_optimization_integration.py --daemon" > /dev/null; then
    echo "✅ Optimization system is running in daemon mode"
else
    echo "⚠️  Optimization system not running"
fi

echo ""
echo "🎯 AUTONOMOUS SYSTEM INSTALLATION COMPLETE!"
echo "=========================================="
echo "✅ System will auto-start on boot"
echo "✅ Auto-recovery enabled"
echo "✅ Log rotation enabled"
echo "✅ Performance monitoring enabled"
echo "✅ No manual intervention required"
echo ""
echo "📊 System Status:"
echo "   - Background Agent: $(pgrep -f background_optimization_agent.py > /dev/null && echo 'RUNNING' || echo 'STOPPED')"
echo "   - Optimization System: $(pgrep -f 'comprehensive_optimization_integration.py --daemon' > /dev/null && echo 'RUNNING' || echo 'STOPPED')"
echo "   - LaunchAgent: $(launchctl list | grep -q 'com.zmartbot.background-optimization-agent' && echo 'INSTALLED' || echo 'NOT INSTALLED')"
echo ""
echo "🔍 To monitor the system:"
echo "   tail -f logs/background_optimization_agent.log"
echo ""
echo "🛑 To stop the system:"
echo "   ./stop_background_optimization_agent.sh"
echo ""
echo "🎉 Your ZmartBot system is now fully autonomous!"
