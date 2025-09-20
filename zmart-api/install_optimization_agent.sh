#!/bin/bash

# ZmartBot Optimization Agent Installation Script
# ==============================================
# This script installs and configures the optimization background agent

set -e

# Configuration
SERVICE_NAME="zmartbot-optimization-agent"
SERVICE_FILE="zmartbot-optimization-agent.service"
SCRIPT_DIR="/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
LOG_DIR="/Users/dansidanutz/Desktop/ZmartBot/logs"
SYSTEMD_DIR="$HOME/Library/LaunchAgents"  # macOS LaunchAgents directory

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
check_os() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is designed for macOS. For Linux, use systemd instead."
        exit 1
    fi
    print_success "macOS detected"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$SYSTEMD_DIR"
    
    print_success "Directories created"
}

# Install Python dependencies
install_dependencies() {
    print_status "Checking Python dependencies..."
    
    cd "$SCRIPT_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install required packages
    print_status "Installing required packages..."
    pip install -q rich psutil requests
    
    print_success "Dependencies installed"
}

# Install LaunchAgent (macOS equivalent of systemd)
install_launchagent() {
    print_status "Installing LaunchAgent for macOS..."
    
    # Create LaunchAgent plist file
    cat > "$SYSTEMD_DIR/${SERVICE_NAME}.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${SERVICE_NAME}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${SCRIPT_DIR}/comprehensive_optimization_integration.py</string>
        <string>--background</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/optimization_agent.log</string>
    
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/optimization_agent_error.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>ProcessType</key>
    <string>Background</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>${SCRIPT_DIR}</string>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
</dict>
</plist>
EOF

    print_success "LaunchAgent installed"
}

# Load and start the service
start_service() {
    print_status "Loading and starting the optimization agent..."
    
    # Load the LaunchAgent
    launchctl load "$SYSTEMD_DIR/${SERVICE_NAME}.plist"
    
    # Start the service
    launchctl start "${SERVICE_NAME}"
    
    # Wait a moment and check status
    sleep 2
    if launchctl list | grep -q "${SERVICE_NAME}"; then
        print_success "Optimization agent started successfully"
    else
        print_error "Failed to start optimization agent"
        exit 1
    fi
}

# Create management script
create_management_script() {
    print_status "Creating management script..."
    
    cat > "$SCRIPT_DIR/manage_optimization_agent.sh" << 'EOF'
#!/bin/bash

# ZmartBot Optimization Agent Management Script
# ============================================

SERVICE_NAME="zmartbot-optimization-agent"
SYSTEMD_DIR="$HOME/Library/LaunchAgents"

case "$1" in
    start)
        echo "Starting optimization agent..."
        launchctl start "${SERVICE_NAME}"
        ;;
    stop)
        echo "Stopping optimization agent..."
        launchctl stop "${SERVICE_NAME}"
        ;;
    restart)
        echo "Restarting optimization agent..."
        launchctl stop "${SERVICE_NAME}"
        sleep 2
        launchctl start "${SERVICE_NAME}"
        ;;
    status)
        echo "Optimization agent status:"
        launchctl list | grep "${SERVICE_NAME}" || echo "Not running"
        ;;
    logs)
        echo "Showing recent logs..."
        tail -f "/Users/dansidanutz/Desktop/ZmartBot/logs/optimization_agent.log"
        ;;
    uninstall)
        echo "Uninstalling optimization agent..."
        launchctl stop "${SERVICE_NAME}" 2>/dev/null || true
        launchctl unload "$SYSTEMD_DIR/${SERVICE_NAME}.plist" 2>/dev/null || true
        rm -f "$SYSTEMD_DIR/${SERVICE_NAME}.plist"
        echo "Optimization agent uninstalled"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|uninstall}"
        exit 1
        ;;
esac
EOF

    chmod +x "$SCRIPT_DIR/manage_optimization_agent.sh"
    print_success "Management script created"
}

# Test the installation
test_installation() {
    print_status "Testing the installation..."
    
    # Check if service is running
    if launchctl list | grep -q "${SERVICE_NAME}"; then
        print_success "Service is running"
    else
        print_error "Service is not running"
        return 1
    fi
    
    # Check if log file is being created
    sleep 5
    if [ -f "${LOG_DIR}/optimization_agent.log" ]; then
        print_success "Log file is being created"
    else
        print_warning "Log file not found yet (may take a moment)"
    fi
    
    print_success "Installation test completed"
}

# Main installation function
main() {
    echo "=========================================="
    echo "ZmartBot Optimization Agent Installation"
    echo "=========================================="
    
    check_os
    create_directories
    install_dependencies
    install_launchagent
    start_service
    create_management_script
    test_installation
    
    echo ""
    echo "=========================================="
    print_success "Installation completed successfully!"
    echo "=========================================="
    echo ""
    echo "Management commands:"
    echo "  Start:   ./manage_optimization_agent.sh start"
    echo "  Stop:    ./manage_optimization_agent.sh stop"
    echo "  Status:  ./manage_optimization_agent.sh status"
    echo "  Logs:    ./manage_optimization_agent.sh logs"
    echo "  Restart: ./manage_optimization_agent.sh restart"
    echo ""
    echo "Log files:"
    echo "  Main:    ${LOG_DIR}/optimization_agent.log"
    echo "  Errors:  ${LOG_DIR}/optimization_agent_error.log"
    echo ""
    echo "The optimization agent will start automatically on system boot."
}

# Run main function
main "$@"
