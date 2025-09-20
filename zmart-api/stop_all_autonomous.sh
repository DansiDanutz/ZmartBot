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
