#!/bin/bash

# ZmartBot Complete Autonomous System Installer
# This script makes the entire system completely autonomous - no manual intervention ever needed

cd "$(dirname "$0")"

echo "🚀 ZmartBot Complete Autonomous System Installation"
echo "=================================================="
echo ""

# 1. Enable all auto-start configurations
echo "📝 Step 1: Enabling auto-start configurations..."
python3 -c "
import json

# Background optimization config
config_path = 'background_optimization_config.json'
with open(config_path, 'r') as f:
    config = json.load(f)
config['auto_start'] = True
config['system_integration']['create_launchd_plist'] = True
config['system_integration']['auto_start_on_boot'] = True
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print('✅ Background optimization auto-start enabled')

# System optimization config
config_path = 'system_optimization_config.json'
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['system_optimization']['auto_start'] = True
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print('✅ System optimization auto-start enabled')
"

# 2. Install LaunchAgent service
echo ""
echo "🔧 Step 2: Installing LaunchAgent service..."
python3 background_optimization_agent.py --install-launchd

# 3. Start Master Autonomous Controller
echo ""
echo "🎯 Step 3: Starting Master Autonomous Controller..."
nohup python3 master_autonomous_controller.py --daemon > logs/master_autonomous_controller.log 2>&1 &
MASTER_PID=$!
echo "Master Controller PID: $MASTER_PID"
echo "$MASTER_PID" > logs/master_autonomous_controller.pid

# 4. Start Autonomous Health Monitor
echo ""
echo "🏥 Step 4: Starting Autonomous Health Monitor..."
nohup python3 autonomous_health_monitor.py --daemon > logs/autonomous_health_monitor.log 2>&1 &
HEALTH_PID=$!
echo "Health Monitor PID: $HEALTH_PID"
echo "$HEALTH_PID" > logs/autonomous_health_monitor.pid

# 5. Start Background Optimization Agent
echo ""
echo "⚡ Step 5: Starting Background Optimization Agent..."
nohup python3 background_optimization_agent.py --daemon > logs/background_optimization_agent.log 2>&1 &
OPTIMIZATION_PID=$!
echo "Optimization Agent PID: $OPTIMIZATION_PID"
echo "$OPTIMIZATION_PID" > logs/background_optimization_agent.pid

# 6. Start Log Rotation Manager
echo ""
echo "📋 Step 6: Starting Log Rotation Manager..."
nohup python3 log_rotation_manager.py --daemon > logs/log_rotation_manager.log 2>&1 &
LOG_PID=$!
echo "Log Rotation Manager PID: $LOG_PID"
echo "$LOG_PID" > logs/log_rotation_manager.pid

# 7. Verify all services are running
echo ""
echo "🔍 Step 7: Verifying all services..."
sleep 5

echo "Checking Master Autonomous Controller..."
if ps -p $MASTER_PID > /dev/null; then
    echo "✅ Master Autonomous Controller running (PID: $MASTER_PID)"
else
    echo "❌ Master Autonomous Controller failed to start"
fi

echo "Checking Autonomous Health Monitor..."
if ps -p $HEALTH_PID > /dev/null; then
    echo "✅ Autonomous Health Monitor running (PID: $HEALTH_PID)"
else
    echo "❌ Autonomous Health Monitor failed to start"
fi

echo "Checking Background Optimization Agent..."
if ps -p $OPTIMIZATION_PID > /dev/null; then
    echo "✅ Background Optimization Agent running (PID: $OPTIMIZATION_PID)"
else
    echo "❌ Background Optimization Agent failed to start"
fi

echo "Checking Log Rotation Manager..."
if ps -p $LOG_PID > /dev/null; then
    echo "✅ Log Rotation Manager running (PID: $LOG_PID)"
else
    echo "❌ Log Rotation Manager failed to start"
fi

# 8. Create system status script
echo ""
echo "📊 Step 8: Creating system status script..."
cat > check_autonomous_status.sh << 'EOF'
#!/bin/bash
echo "🤖 ZmartBot Autonomous System Status"
echo "===================================="
echo ""

# Check Master Autonomous Controller
if [ -f "logs/master_autonomous_controller.pid" ]; then
    MASTER_PID=$(cat logs/master_autonomous_controller.pid)
    if ps -p $MASTER_PID > /dev/null; then
        echo "✅ Master Autonomous Controller: RUNNING (PID: $MASTER_PID)"
    else
        echo "❌ Master Autonomous Controller: STOPPED"
    fi
else
    echo "❌ Master Autonomous Controller: NOT INSTALLED"
fi

# Check Autonomous Health Monitor
if [ -f "logs/autonomous_health_monitor.pid" ]; then
    HEALTH_PID=$(cat logs/autonomous_health_monitor.pid)
    if ps -p $HEALTH_PID > /dev/null; then
        echo "✅ Autonomous Health Monitor: RUNNING (PID: $HEALTH_PID)"
    else
        echo "❌ Autonomous Health Monitor: STOPPED"
    fi
else
    echo "❌ Autonomous Health Monitor: NOT INSTALLED"
fi

# Check Background Optimization Agent
if [ -f "logs/background_optimization_agent.pid" ]; then
    OPTIMIZATION_PID=$(cat logs/background_optimization_agent.pid)
    if ps -p $OPTIMIZATION_PID > /dev/null; then
        echo "✅ Background Optimization Agent: RUNNING (PID: $OPTIMIZATION_PID)"
    else
        echo "❌ Background Optimization Agent: STOPPED"
    fi
else
    echo "❌ Background Optimization Agent: NOT INSTALLED"
fi

# Check Log Rotation Manager
if [ -f "logs/log_rotation_manager.pid" ]; then
    LOG_PID=$(cat logs/log_rotation_manager.pid)
    if ps -p $LOG_PID > /dev/null; then
        echo "✅ Log Rotation Manager: RUNNING (PID: $LOG_PID)"
    else
        echo "❌ Log Rotation Manager: STOPPED"
    fi
else
    echo "❌ Log Rotation Manager: NOT INSTALLED"
fi

echo ""
echo "📋 System Logs:"
echo "Master Controller: logs/master_autonomous_controller.log"
echo "Health Monitor: logs/autonomous_health_monitor.log"
echo "Optimization Agent: logs/background_optimization_agent.log"
echo "Log Rotation: logs/log_rotation_manager.log"
EOF

chmod +x check_autonomous_status.sh

# 9. Create emergency stop script
echo ""
echo "🛑 Step 9: Creating emergency stop script..."
cat > stop_all_autonomous.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping all ZmartBot autonomous services..."

# Stop Master Autonomous Controller
if [ -f "logs/master_autonomous_controller.pid" ]; then
    MASTER_PID=$(cat logs/master_autonomous_controller.pid)
    if ps -p $MASTER_PID > /dev/null; then
        echo "Stopping Master Autonomous Controller (PID: $MASTER_PID)..."
        kill $MASTER_PID
        rm logs/master_autonomous_controller.pid
    fi
fi

# Stop Autonomous Health Monitor
if [ -f "logs/autonomous_health_monitor.pid" ]; then
    HEALTH_PID=$(cat logs/autonomous_health_monitor.pid)
    if ps -p $HEALTH_PID > /dev/null; then
        echo "Stopping Autonomous Health Monitor (PID: $HEALTH_PID)..."
        kill $HEALTH_PID
        rm logs/autonomous_health_monitor.pid
    fi
fi

# Stop Background Optimization Agent
if [ -f "logs/background_optimization_agent.pid" ]; then
    OPTIMIZATION_PID=$(cat logs/background_optimization_agent.pid)
    if ps -p $OPTIMIZATION_PID > /dev/null; then
        echo "Stopping Background Optimization Agent (PID: $OPTIMIZATION_PID)..."
        kill $OPTIMIZATION_PID
        rm logs/background_optimization_agent.pid
    fi
fi

# Stop Log Rotation Manager
if [ -f "logs/log_rotation_manager.pid" ]; then
    LOG_PID=$(cat logs/log_rotation_manager.pid)
    if ps -p $LOG_PID > /dev/null; then
        echo "Stopping Log Rotation Manager (PID: $LOG_PID)..."
        kill $LOG_PID
        rm logs/log_rotation_manager.pid
    fi
fi

echo "✅ All autonomous services stopped"
EOF

chmod +x stop_all_autonomous.sh

# 10. Final status check
echo ""
echo "🎉 Step 10: Final system status..."
./check_autonomous_status.sh

echo ""
echo "🚀 INSTALLATION COMPLETE!"
echo "========================="
echo ""
echo "✅ Your ZmartBot system is now COMPLETELY AUTONOMOUS!"
echo ""
echo "📋 What's been installed:"
echo "  • Master Autonomous Controller - Orchestrates everything"
echo "  • Autonomous Health Monitor - Monitors and fixes issues"
echo "  • Background Optimization Agent - Runs optimizations"
echo "  • Log Rotation Manager - Manages log files"
echo "  • LaunchAgent Service - Auto-starts on system boot"
echo ""
echo "🔧 Management Commands:"
echo "  • Check status: ./check_autonomous_status.sh"
echo "  • Emergency stop: ./stop_all_autonomous.sh"
echo "  • View logs: tail -f logs/*.log"
echo ""
echo "🎯 The system will now:"
echo "  • Start automatically on system boot"
echo "  • Monitor itself continuously"
echo "  • Fix issues automatically"
echo "  • Optimize performance continuously"
echo "  • Manage logs automatically"
echo "  • Restart failed services"
echo ""
echo "💡 You never need to manually start anything again!"
echo "   The system is completely self-managing and autonomous."
