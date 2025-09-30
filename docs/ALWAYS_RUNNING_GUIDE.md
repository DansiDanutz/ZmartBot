# KingFisher Always-Running Monitor Setup

**Date**: July 30, 2025  
**Purpose**: Set up monitoring to run automatically and continuously  
**Status**: ✅ **ONE-COMMAND INSTALLATION**

## 🚀 **Quick Setup (One Command)**

```bash
# Navigate to KingFisher backend
cd kingfisher-module/backend

# Install always-running monitor
./install_always_running.sh
```

That's it! The monitoring system will now:
- ✅ Start automatically when you log in
- ✅ Restart automatically if it crashes
- ✅ Run continuously in the background
- ✅ Check every 2 minutes to ensure it's running

## 📊 **What This Does**

### **Automatic Startup**
- **Systemd Service**: Starts when you log in
- **Cron Job**: Checks every 2 minutes to ensure it's running
- **Auto-Restart**: If the process crashes, it restarts automatically

### **Continuous Monitoring**
- **Every 30 seconds**: Checks for new images
- **Automatic Processing**: Processes images without manual intervention
- **Background Operation**: Runs silently in the background

### **Multiple Safety Nets**
1. **Systemd Service**: Primary startup mechanism
2. **Cron Job**: Backup to ensure it's always running
3. **Auto-Restart**: Recovers from crashes automatically
4. **Health Checks**: Monitors server and Airtable connection

## 🔧 **Management Commands**

### **System Service Commands**
```bash
# Check status
systemctl --user status kingfisher-monitor.service

# Start service
systemctl --user start kingfisher-monitor.service

# Stop service
systemctl --user stop kingfisher-monitor.service

# View logs
journalctl --user -u kingfisher-monitor.service -f
```

### **Manual Commands**
```bash
# Check status
./launch_monitoring.sh status

# Start manually
./launch_monitoring.sh start

# Stop manually
./launch_monitoring.sh stop

# View logs
tail -f monitoring.log
```

## 📱 **Usage**

Once installed, you can:

1. **Generate images on Telegram** - they'll be processed automatically
2. **Check Airtable** - results will appear automatically
3. **Monitor logs** - see real-time processing status

**No manual intervention needed!**

## 🔍 **Troubleshooting**

### **Check if it's running**
```bash
./launch_monitoring.sh status
```

### **View logs**
```bash
tail -f monitoring.log
```

### **Restart if needed**
```bash
./launch_monitoring.sh restart
```

### **Check system service**
```bash
systemctl --user status kingfisher-monitor.service
```

## 🎯 **Benefits**

### **Before (Manual)**
- ❌ Had to manually start monitoring
- ❌ Had to check if it was running
- ❌ Had to restart when it crashed
- ❌ Had to tell me when images weren't processed

### **After (Always-Running)**
- ✅ **Starts automatically** when you log in
- ✅ **Runs continuously** in the background
- ✅ **Auto-restarts** if it crashes
- ✅ **Processes images automatically** every 30 seconds
- ✅ **No manual intervention** needed

## 🚀 **Ready to Use**

After running `./install_always_running.sh`:

1. **The monitoring is now running continuously**
2. **Generate images on Telegram**
3. **Watch them be processed automatically**
4. **Check Airtable for results**

**That's it! No more manual checking or telling me when things aren't working!**

---

**🎉 Result**: Your monitoring system now runs automatically and continuously. Just generate images on Telegram and they'll be processed automatically every 30 seconds!

**Status**: ✅ **ALWAYS-RUNNING MONITOR READY** 