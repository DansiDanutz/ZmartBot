#!/bin/bash

# KingFisher Always-Running Monitor Installer
# One command to install and start the monitoring system

echo "🚀 Installing KingFisher Always-Running Monitor..."
echo "=================================================="

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in the right directory
if [ ! -f "$SCRIPT_DIR/auto_monitor.py" ]; then
    echo "❌ Error: auto_monitor.py not found. Please run this from the kingfisher-module/backend directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "✅ Environment check passed"

# Create the launcher script
LAUNCHER_SCRIPT="$SCRIPT_DIR/launch_monitoring.sh"

cat > "$LAUNCHER_SCRIPT" << 'EOF'
#!/bin/bash

# KingFisher Auto-Monitoring Launcher
# This script ensures the monitoring system is always running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/monitoring.log"
PID_FILE="$SCRIPT_DIR/monitoring.pid"

# Function to start monitoring
start_monitoring() {
    echo "$(date): Starting KingFisher Auto-Monitoring..." >> "$LOG_FILE"
    
    # Activate virtual environment
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # Set Python path
    export PYTHONPATH="$SCRIPT_DIR/src"
    
    # Start the monitoring script
    cd "$SCRIPT_DIR"
    python auto_monitor.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    echo "$(date): Monitoring started with PID $(cat $PID_FILE)" >> "$LOG_FILE"
}

# Function to stop monitoring
stop_monitoring() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "$(date): Stopped monitoring (PID: $PID)" >> "$LOG_FILE"
        fi
        rm -f "$PID_FILE"
    fi
}

# Function to check if monitoring is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Main logic
case "$1" in
    start)
        if is_running; then
            echo "Monitoring is already running"
        else
            start_monitoring
            echo "Monitoring started"
        fi
        ;;
    stop)
        stop_monitoring
        echo "Monitoring stopped"
        ;;
    restart)
        stop_monitoring
        sleep 2
        start_monitoring
        echo "Monitoring restarted"
        ;;
    status)
        if is_running; then
            echo "Monitoring is running (PID: $(cat $PID_FILE))"
        else
            echo "Monitoring is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF

chmod +x "$LAUNCHER_SCRIPT"
echo "✅ Created launcher script: $LAUNCHER_SCRIPT"

# Create a cron job to ensure it's always running
CRON_JOB="*/2 * * * * $LAUNCHER_SCRIPT start >/dev/null 2>&1"

echo ""
echo "📅 Setting up cron job to ensure monitoring is always running..."
echo "Current cron jobs:"
crontab -l 2>/dev/null || echo "No cron jobs found"

echo ""
echo "Adding monitoring cron job..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed. Monitoring will start automatically every 2 minutes if not running."

# Create a systemd user service for automatic startup
USER_SERVICE_DIR="$HOME/.config/systemd/user"
mkdir -p "$USER_SERVICE_DIR"

USER_SERVICE_FILE="$USER_SERVICE_DIR/kingfisher-monitor.service"

cat > "$USER_SERVICE_FILE" << EOF
[Unit]
Description=KingFisher Auto-Monitoring Service
After=network.target
Wants=network.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$SCRIPT_DIR/launch_monitoring.sh start
ExecReload=$SCRIPT_DIR/launch_monitoring.sh restart
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kingfisher-monitor

# Environment variables
Environment=PYTHONPATH=$SCRIPT_DIR/src
Environment=KINGFISHER_HOME=$SCRIPT_DIR

[Install]
WantedBy=default.target
EOF

echo "✅ Created user service file: $USER_SERVICE_FILE"

# Enable the user service
systemctl --user daemon-reload
systemctl --user enable kingfisher-monitor.service
systemctl --user start kingfisher-monitor.service

echo ""
echo "🎯 KingFisher Always-Running Monitor Installation Complete!"
echo "=================================================="
echo ""
echo "📊 Service Status:"
systemctl --user status kingfisher-monitor.service --no-pager -l

echo ""
echo "🔧 Management Commands:"
echo "  Start:   systemctl --user start kingfisher-monitor.service"
echo "  Stop:    systemctl --user stop kingfisher-monitor.service"
echo "  Status:  systemctl --user status kingfisher-monitor.service"
echo "  Logs:    journalctl --user -u kingfisher-monitor.service -f"
echo ""
echo "📝 Manual Commands:"
echo "  Start:   $LAUNCHER_SCRIPT start"
echo "  Stop:    $LAUNCHER_SCRIPT stop"
echo "  Status:  $LAUNCHER_SCRIPT status"
echo "  Logs:    tail -f $SCRIPT_DIR/monitoring.log"
echo ""
echo "🔄 The monitoring system will now:"
echo "  ✅ Start automatically when you log in"
echo "  ✅ Restart automatically if it crashes"
echo "  ✅ Run continuously in the background"
echo "  ✅ Check every 2 minutes via cron to ensure it's running"
echo ""
echo "🎉 Installation complete! The monitoring system is now running continuously."
echo ""
echo "📱 You can now generate images on Telegram and they will be processed automatically!" 