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
