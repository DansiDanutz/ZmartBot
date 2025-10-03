# 📦 Large Files Cleanup Report

**Generated**: 2025-10-01
**Total Project Size**: 1.5GB
**Cleanup Potential**: ~200-300MB

---

## 🔍 Large Files Identified

### Critical - Files > 10MB

| Size | File | Recommendation |
|------|------|----------------|
| 74MB | `./background_mdc_agent.log` | 🔴 Delete or rotate |
| 51MB | `./predictions.db` | 🟡 Archive if old |
| 16MB | `./trading_orchestration.db` | 🟢 Keep (active DB) |
| 16MB | `./data/riskmetric_qa.db` | 🟡 Review/Archive |
| 13MB | `./immediate_protection.log` | 🔴 Delete or rotate |
| 12MB | `./port_conflict_detector.log` | 🔴 Delete or rotate |

**Total from large files**: ~182MB

---

## 📝 Log Files Identified

Large log files (> 1MB):

1. `./snapshot_service/snapshot-service.log`
2. `./mdc_orchestration_agent.log`
3. `./backtesting/zmart_backtesting.log`
4. `./port_conflict_detector.log`
5. `./failover_startup.log`
6. `./background_mdc_agent.log`
7. `./binance_worker/binance-worker-service.log`
8. `./mysymbols/mysymbols.log`
9. `./dashboard/MDC-Dashboard/service-discovery/service_discovery.log`
10. `./technical_analysis/zmart_technical_analysis.log`

---

## 🎯 Cleanup Recommendations

### Immediate Actions (High Priority)

#### 1. Rotate/Archive Large Log Files

```bash
# Create logs archive directory
mkdir -p archive/logs_$(date +%Y%m%d)

# Move large log files to archive
mv background_mdc_agent.log archive/logs_$(date +%Y%m%d)/
mv immediate_protection.log archive/logs_$(date +%Y%m%d)/
mv port_conflict_detector.log archive/logs_$(date +%Y%m%d)/

# Or delete if not needed
# rm -f background_mdc_agent.log immediate_protection.log port_conflict_detector.log
```

**Expected Savings**: ~99MB

#### 2. Implement Log Rotation

```bash
# Create logrotate config
cat > /tmp/zmartbot_logrotate.conf << 'EOF'
/Users/dansidanutz/Desktop/ZmartBot/**/*.log {
    size 10M
    rotate 5
    compress
    delaycompress
    missingok
    notifempty
    create 0644 dansidanutz staff
}
EOF

# Test configuration
logrotate -d /tmp/zmartbot_logrotate.conf

# Apply (run daily via cron)
logrotate /tmp/zmartbot_logrotate.conf
```

#### 3. Clean Up Database Files

```bash
# Review old prediction data
sqlite3 predictions.db "SELECT COUNT(*) FROM predictions;"

# Archive if historical
mkdir -p archive/databases_$(date +%Y%m%d)
cp predictions.db archive/databases_$(date +%Y%m%d)/
# Then decide if you can remove the original

# Same for QA database
cp data/riskmetric_qa.db archive/databases_$(date +%Y%m%d)/
```

**Expected Savings**: ~67MB (if archived)

---

## 📊 Disk Usage Analysis

### Current Distribution

```bash
Total Project: 1.5GB
├── Virtual Environments: ~1.2GB (estimated)
├── Git Repository: ~50MB
├── Log Files: ~100MB
├── Database Files: ~80MB
├── Source Code: ~20MB
└── Documentation (MDC): ~4MB
```

### After Cleanup (Estimated)

```bash
Total Project: 1.2-1.3GB
├── Virtual Environments: ~1.2GB
├── Git Repository: ~50MB
├── Log Files: ~10MB (rotated)
├── Database Files: ~16MB (archived old)
├── Source Code: ~20MB
└── Documentation (MDC): ~4MB
```

---

## 🛠️ Automated Cleanup Script

Create this script to automate cleanup:

```bash
#!/bin/bash
# cleanup_zmartbot.sh - Automated cleanup script

set -e

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
ARCHIVE_DIR="$PROJECT_ROOT/archive/$(date +%Y%m%d_%H%M%S)"

echo "🧹 ZmartBot Cleanup Script"
echo "========================="

# Create archive directory
mkdir -p "$ARCHIVE_DIR/logs"
mkdir -p "$ARCHIVE_DIR/databases"

# Archive large log files (>10MB)
echo "📦 Archiving large log files..."
find "$PROJECT_ROOT" -name "*.log" -type f -size +10M -exec sh -c '
    for file; do
        echo "  Archiving: $file"
        mv "$file" "'"$ARCHIVE_DIR/logs/"'"
    done
' sh {} +

# Compress archived logs
echo "🗜️  Compressing archived logs..."
cd "$ARCHIVE_DIR/logs"
for log in *.log; do
    if [ -f "$log" ]; then
        gzip "$log"
    fi
done

# Clean Python cache (if any)
echo "🐍 Cleaning Python cache..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true

# Clean Node.js cache (if any)
echo "📦 Cleaning Node.js cache..."
find "$PROJECT_ROOT" -type d -name "node_modules/.cache" -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
echo "🗑️  Removing temporary files..."
find "$PROJECT_ROOT" -type f -name "*.tmp" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name ".DS_Store" -delete 2>/dev/null || true

# Summary
echo ""
echo "✅ Cleanup Complete!"
echo "Archive location: $ARCHIVE_DIR"
echo ""
echo "📊 Disk usage:"
du -sh "$PROJECT_ROOT"

echo ""
echo "🔍 Archived files:"
ls -lh "$ARCHIVE_DIR/logs/" 2>/dev/null || echo "  No large logs archived"

exit 0
```

**Make it executable:**

```bash
chmod +x cleanup_zmartbot.sh
```

---

## 🔄 Maintenance Schedule

### Daily
- Check log file sizes
- Rotate logs if needed

### Weekly

```bash
# Check project size
du -sh /Users/dansidanutz/Desktop/ZmartBot

# List largest directories
du -sh /Users/dansidanutz/Desktop/ZmartBot/* | sort -hr | head -10

# List largest files
find /Users/dansidanutz/Desktop/ZmartBot -type f -size +5M -exec ls -lh {} \; | sort -k5 -hr | head -10
```

### Monthly
- Archive old database files
- Clean up old virtual environments
- Review and compress archived logs

---

## 📋 Manual Cleanup Commands

### Quick Cleanup (Safe)

```bash
# Remove log files older than 30 days
find . -name "*.log" -type f -mtime +30 -delete

# Remove empty directories
find . -type d -empty -delete

# Clean macOS metadata
find . -name ".DS_Store" -delete
```

### Deep Cleanup (Review First!)

```bash
# Find and remove large files (review list first!)
find . -type f -size +50M -not -path "*/venv/*" -not -path "*/node_modules/*"

# Remove unused virtual environments (verify first!)
# find . -name "venv" -type d -mtime +60

# Archive old test data
# find ./tests -name "*.db" -mtime +90
```

---

## 🚨 .gitignore Optimization

Add these to `.gitignore` to prevent future bloat:

```gitignore
# Logs
*.log
*.log.*
logs/

# Databases (development)
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# System
.DS_Store
Thumbs.db
*.tmp
*.temp

# Archives
archive/
backups/
```

---

## 📈 Expected Benefits

### Storage Savings
- **Immediate**: 100-200MB from log cleanup
- **Long-term**: 200-300MB with proper rotation

### Performance
- Faster file searches
- Quicker git operations
- Better backup efficiency

### Maintenance
- Easier to navigate project
- Cleaner git status
- Reduced confusion

---

## ✅ Cleanup Checklist

- [ ] Review large files identified
- [ ] Archive important logs
- [ ] Delete unnecessary logs
- [ ] Archive old database files
- [ ] Set up log rotation
- [ ] Update .gitignore
- [ ] Schedule weekly cleanup
- [ ] Document retention policy
- [ ] Create cleanup script
- [ ] Test backup/restore

---

## 🔧 Tools for Monitoring

### Disk Usage Tools

```bash
# Interactive disk usage
ncdu /Users/dansidanutz/Desktop/ZmartBot

# Visual tree
tree -L 2 -h --du

# Largest directories
du -h -d 2 | sort -hr | head -20
```

### Log Monitoring

```bash
# Watch log growth
watch -n 5 'du -sh *.log'

# Find rapidly growing files
find . -name "*.log" -mmin -60 -ls
```

---

**Report Generated**: 2025-10-01
**Next Review**: Weekly maintenance
**Estimated Cleanup Time**: 30 minutes
