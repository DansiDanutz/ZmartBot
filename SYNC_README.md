# 🔄 ZmartBot Auto-Sync System

## ✅ Setup Complete

Your ZmartBot system now has **automatic folder synchronization** between:

- Main ZmartBot: `/Users/dansidanutz/Desktop/ZmartBot/.claude` & `.cursor/rules`
- Zmart-API: `/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.claude` & `.cursor/rules`

## 🚀 How It Works

### Automatic Startup
- **Every time you run `./START_ZMARTBOT.sh`**, sync starts automatically
- **Always-on monitoring** watches for file changes and syncs instantly
- **Integrated shutdown** stops sync when you run `./STOP_ZMARTBOT.sh`

### Current Status

✅ **Sync Service**: Running (PID: 98763)
✅ **Folders**: Synchronized
✅ **File Monitoring**: Active (fswatch installed)
✅ **Auto-start**: Integrated into START script

## 📋 Quick Commands

### Status & Management

```bash
./manage_sync.sh status    # Show sync status
./manage_sync.sh start     # Start sync service
./manage_sync.sh stop      # Stop sync service
./manage_sync.sh restart   # Restart sync service
./manage_sync.sh test      # Test functionality
```

### Manual Operations

```bash
./sync.sh                  # One-time sync
./sync.sh diff             # Show differences
./sync.sh watch            # Watch for changes
```

### Logs & Monitoring

```bash
./manage_sync.sh logs      # Show recent activity
cat /tmp/zmartbot-sync-always.log  # Full logs
```

## 🔧 Technical Details

### Files Created
- `sync_claude_folders.sh` - Main sync script with full features
- `sync_always.sh` - Always-on background service
- `sync.sh` - Quick launcher
- `manage_sync.sh` - Management interface
- `start_sync.sh` - Startup helper

### Integration Points
- **START_ZMARTBOT.sh**: Auto-starts sync on system startup
- **STOP_ZMARTBOT.sh**: Cleanly stops sync on system shutdown
- **File Monitoring**: Real-time sync using fswatch
- **Backup System**: Automatic backups before each sync

### Sync Direction
**Main → zmart-api** (one-way sync)

- Changes in main ZmartBot folder automatically sync to zmart-api
- Preserves main folder as the authoritative source
- Prevents conflicts and ensures consistency

## 🎯 Benefits

✅ **Always in Sync**: Folders stay synchronized automatically
✅ **Zero Manual Work**: No need to remember to sync
✅ **Real-time Updates**: Changes sync instantly
✅ **Safe Operations**: Automatic backups before sync
✅ **Integrated Startup**: Works seamlessly with ZmartBot system
✅ **Error Recovery**: Robust error handling and fallbacks

## 🚨 Important Notes

- **Sync Direction**: Main → zmart-api (changes in zmart-api will be overwritten)
- **Backup Location**: `/tmp/zmartbot_sync_backup_*` (automatic backups)
- **Log Files**: `/tmp/zmartbot-sync-always.log` (sync activity)
- **PID File**: `/tmp/zmartbot-sync-always.pid` (service management)

---

**🎉 Your ZmartBot system now has automatic folder synchronization!**
**The sync will start every time you run `./START_ZMARTBOT.sh`**
