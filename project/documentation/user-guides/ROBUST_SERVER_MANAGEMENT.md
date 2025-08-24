# 🚀 ZmartBot Robust Server Management System

## Overview

The ZmartBot Robust Server Management System provides enterprise-grade server management with automatic monitoring, health checks, auto-restart capabilities, and comprehensive conflict prevention. This system ensures your trading bot servers stay connected and operational 24/7.

## 🎯 Key Features

### ✅ **Automatic Conflict Prevention**
- **Port Conflict Detection**: Automatically detects and resolves port conflicts
- **Process Cleanup**: Graceful shutdown with fallback to force kill
- **Retry Logic**: Multiple attempts with exponential backoff
- **PID Management**: Proper process tracking and cleanup

### ✅ **Health Monitoring**
- **Real-time Health Checks**: Continuous monitoring of server responsiveness
- **Auto-restart**: Automatically restarts failed servers
- **Response Time Monitoring**: Tracks API and dashboard response times
- **Uptime Tracking**: Monitors server uptime and stability

### ✅ **Comprehensive Logging**
- **Structured Logging**: Timestamped logs with severity levels
- **Multiple Log Files**: Separate logs for startup, shutdown, monitoring, and servers
- **Error Tracking**: Detailed error reporting and debugging information
- **Performance Metrics**: Response times, uptime, and resource usage

### ✅ **Robust Error Handling**
- **Signal Handling**: Proper cleanup on shutdown signals
- **Timeout Management**: Configurable timeouts for all operations
- **Fallback Mechanisms**: Multiple strategies for process management
- **Resource Cleanup**: Automatic cleanup of temporary files and processes

## 📁 File Structure

```
ZmartBot/
├── start_servers_robust.sh      # Main startup script with monitoring
├── stop_servers_robust.sh       # Graceful shutdown script
├── status_servers.sh            # Real-time status monitoring
├── server_pids/                 # PID file directory
│   ├── api_server.pid
│   ├── dashboard_server.pid
│   └── monitor.pid
├── server_startup.log           # Startup process logs
├── server_shutdown.log          # Shutdown process logs
├── server_monitor.log           # Monitoring logs
├── backend/zmart-api/
│   └── api_server.log           # API server logs
└── dashboard_server.log         # Dashboard server logs
```

## 🚀 Quick Start

### 1. Start Servers with Monitoring
```bash
./start_servers_robust.sh
```

### 2. Check Server Status
```bash
./status_servers.sh
```

### 3. Stop Servers Gracefully
```bash
./stop_servers_robust.sh
```

## 📊 Status Monitoring

### Basic Status Check
```bash
./status_servers.sh
```
**Output:**
```
📊 QUICK STATUS
==============

✅ API Server: Running & Healthy
✅ Dashboard Server: Running & Healthy
✅ Monitoring: Active
```

### Detailed Status
```bash
./status_servers.sh --detailed
```
**Output:**
```
📊 DETAILED SERVER STATUS
========================

✅ API Server (Port 8000): Running
   Process: 88526 Python *:irdmi
   Uptime: 2h 15m
   Health: ✅ Healthy
   Response Time: 45ms

✅ Dashboard Server (Port 3400): Running
   Process: 83184 Python *:csms2
   Uptime: 2h 15m
   Health: ✅ Healthy
   Response Time: 23ms

🔍 Monitoring: ✅ Active
```

### All Information
```bash
./status_servers.sh --all
```
Includes:
- Detailed server status
- System resources (CPU, Memory, Disk)
- Recent logs
- Connection information

## ⚙️ Configuration

### Environment Variables
```bash
# Server Ports
API_PORT=8000
DASHBOARD_PORT=3400

# Monitoring Settings
MONITOR_INTERVAL=30          # Health check interval (seconds)
MAX_RESTART_ATTEMPTS=3       # Max restart attempts per server
HEALTH_CHECK_TIMEOUT=10      # Health check timeout (seconds)

# Paths
API_DIR="backend/zmart-api"
VENV_PATH="backend/zmart-api/venv/bin/activate"
PID_DIR="server_pids"
```

### Logging Levels
- **INFO**: Normal operations
- **WARN**: Non-critical issues
- **ERROR**: Critical failures
- **DEBUG**: Detailed debugging information

## 🔧 Advanced Usage

### Custom Monitoring Interval
```bash
# Edit start_servers_robust.sh
MONITOR_INTERVAL=60  # Check every minute instead of 30 seconds
```

### Increase Restart Attempts
```bash
# Edit start_servers_robust.sh
MAX_RESTART_ATTEMPTS=5  # Try 5 times instead of 3
```

### View Real-time Logs
```bash
# Monitor startup logs
tail -f server_startup.log

# Monitor API server logs
tail -f backend/zmart-api/api_server.log

# Monitor dashboard logs
tail -f dashboard_server.log

# Monitor health checks
tail -f server_monitor.log
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3400

# Force cleanup
./stop_servers_robust.sh
```

### Server Won't Start
```bash
# Check logs
tail -20 server_startup.log

# Check virtual environment
ls -la backend/zmart-api/venv/bin/activate

# Check Python dependencies
cd backend/zmart-api && source venv/bin/activate && pip list
```

### Monitoring Issues
```bash
# Check if monitoring is running
ps aux | grep start_servers_robust

# Restart monitoring
./stop_servers_robust.sh && ./start_servers_robust.sh
```

### Performance Issues
```bash
# Check system resources
./status_servers.sh --resources

# Check response times
./status_servers.sh --detailed
```

## 🔄 Auto-Restart Scenarios

The system automatically restarts servers in these scenarios:

1. **Health Check Failure**: Server doesn't respond to health check
2. **Process Death**: Server process terminates unexpectedly
3. **Port Conflict**: Another process takes over the port
4. **High Response Time**: Server becomes unresponsive
5. **Memory Issues**: Server runs out of memory

## 📈 Performance Monitoring

### Response Time Thresholds
- **Excellent**: < 100ms
- **Good**: 100-500ms
- **Warning**: 500ms-2s
- **Critical**: > 2s

### Uptime Tracking
- **Process Uptime**: How long each server has been running
- **System Uptime**: Overall system stability
- **Restart Frequency**: How often servers need restarting

## 🔒 Security Features

### Process Isolation
- **Separate PID Files**: Each process tracked independently
- **Graceful Shutdown**: Proper cleanup on termination
- **Resource Limits**: Prevents resource exhaustion

### Log Security
- **No Sensitive Data**: Logs don't contain API keys or passwords
- **Rotation**: Log files can be rotated to prevent disk space issues
- **Access Control**: Log files have appropriate permissions

## 🚨 Alert System

The monitoring system provides alerts for:

- **Server Down**: When a server stops responding
- **High Response Time**: When servers become slow
- **Restart Events**: When auto-restart occurs
- **Resource Issues**: When system resources are low

## 📋 Best Practices

### 1. **Regular Monitoring**
```bash
# Check status every hour
watch -n 3600 ./status_servers.sh
```

### 2. **Log Rotation**
```bash
# Rotate logs weekly
logrotate -f /etc/logrotate.d/zmartbot
```

### 3. **Backup Configuration**
```bash
# Backup server configuration
cp start_servers_robust.sh start_servers_robust.sh.backup
```

### 4. **System Integration**
```bash
# Add to system startup (macOS)
cp start_servers_robust.sh ~/Library/LaunchAgents/
```

## 🔧 Maintenance

### Weekly Tasks
1. **Review Logs**: Check for patterns or issues
2. **Update Dependencies**: Keep Python packages updated
3. **Clean Old Logs**: Remove logs older than 30 days
4. **Test Restart**: Verify auto-restart functionality

### Monthly Tasks
1. **Performance Review**: Analyze response times and uptime
2. **Configuration Review**: Update settings if needed
3. **Security Audit**: Review process permissions
4. **Backup Verification**: Test backup and restore procedures

## 🆘 Emergency Procedures

### Complete System Reset
```bash
# Stop everything
./stop_servers_robust.sh

# Clean up
rm -rf server_pids/*
rm -f *.log

# Restart
./start_servers_robust.sh
```

### Manual Server Start
```bash
# Start API server manually
cd backend/zmart-api
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Start dashboard manually
python professional_dashboard_server.py
```

## 📞 Support

### Common Issues
1. **Port Conflicts**: Use `./stop_servers_robust.sh` to clean up
2. **Permission Issues**: Ensure scripts are executable (`chmod +x *.sh`)
3. **Virtual Environment**: Verify `backend/zmart-api/venv/` exists
4. **Dependencies**: Check Python packages are installed

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
./start_servers_robust.sh
```

---

## 🎉 Benefits

✅ **Zero Downtime**: Automatic restart prevents service interruptions
✅ **Self-Healing**: System automatically recovers from failures
✅ **Comprehensive Monitoring**: Real-time visibility into system health
✅ **Easy Management**: Simple commands for all operations
✅ **Production Ready**: Enterprise-grade reliability and logging
✅ **Conflict Prevention**: No more port conflicts or process issues

This robust system ensures your ZmartBot trading platform stays operational 24/7 with minimal manual intervention!
