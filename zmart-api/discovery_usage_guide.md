# Discovery Database - Trigger-Based System Usage Guide

## 🚀 **ULTRA-EFFICIENT DISCOVERY SYSTEM**

This system replaces the slow folder scanning with instant trigger-based detection. Much faster and more efficient!

## 📁 **Available Tools**

### 1. **discovery_trigger.py** - Primary Tool (RECOMMENDED)
**Use this when you create a new Python file or MDC file**

```bash
# When you create a new Python file
python3 discovery_trigger.py /path/to/new_service.py

# When you create a new MDC file  
python3 discovery_trigger.py /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/new_service.mdc

# Example usage
python3 discovery_trigger.py /Users/dansidanutz/Desktop/ZmartBot/zmart-api/my_new_service.py
```

### 2. **discovery_file_watcher.py** - Background Monitor (OPTIONAL)
**Run this in background to automatically detect new files**

```bash
# Start background file watcher
python3 discovery_file_watcher.py

# It will monitor:
# - /Users/dansidanutz/Desktop/ZmartBot/ (for Python files)
# - /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/ (for MDC files)
```

## 🔍 **How It Works**

### Discovery Rules:
1. ✅ **Both files required**: Python file AND MDC file must exist
2. ✅ **No duplicates**: Checks service name and Python file path
3. ✅ **No passport services**: Services with passports are excluded
4. ✅ **Unique names**: Same Python file can't have different names

### Example Workflow:
```bash
# Step 1: Create your Python file
touch /Users/dansidanutz/Desktop/ZmartBot/zmart-api/amazing_service.py

# Step 2: Create corresponding MDC file
touch /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/amazing_service.mdc

# Step 3: Trigger discovery (EITHER file will work)
python3 discovery_trigger.py /Users/dansidanutz/Desktop/ZmartBot/zmart-api/amazing_service.py
# OR
python3 discovery_trigger.py /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/amazing_service.mdc

# Result: ✅ amazing_service - Added to discovery database
```

## 📊 **Check Discovery Database**

```bash
# See all discovered services
sqlite3 discovery_registry.db "SELECT * FROM discovery_services;"

# Count discovered services
sqlite3 discovery_registry.db "SELECT COUNT(*) FROM discovery_services WHERE status = 'DISCOVERED';"

# Check specific service
sqlite3 discovery_registry.db "SELECT * FROM discovery_services WHERE service_name = 'your_service';"
```

## 🚨 **Critical Features**

### Duplicate Prevention:
- ❌ **Service name exists**: `my_service` already in database
- ❌ **Same Python file**: `/path/file.py` already tracked with different name
- ❌ **Has passport**: Service already has passport (Level 2+)

### Success Messages:
```
✅ my_service - Added to discovery database
   Python: /Users/dansidanutz/Desktop/ZmartBot/zmart-api/my_service.py
   MDC: /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/my_service.mdc
```

### Skip Messages:
```
❌ my_service - Python file exists but no MDC file
❌ my_service - MDC file exists but no Python file  
⏭️  my_service - Has passport, not adding to discovery database
⏭️  my_service - Duplicate detected, not adding
```

## 🎯 **Best Practices**

### When creating new services:
1. Create both `.py` and `.mdc` files
2. Use consistent naming (same name for both files)
3. Run trigger after creating both files
4. Check database to confirm addition

### Integration with ZmartBot:
- Discovery services are Level 1 (pre-passport)
- ServiceDiscovery monitors discovery database for promotion
- Port assignment triggers Level 2 (passport) promotion
- Full registration triggers Level 3 (certification) promotion

## 💡 **Why This Is Better**

### Old System (Hourly Scanning):
- ❌ Scanned entire ZmartBot folder every hour
- ❌ Processed thousands of files (including venv)
- ❌ Slow and resource intensive
- ❌ Delays in detection

### New System (Trigger-Based):
- ✅ Only processes files when created
- ✅ Instant detection and processing
- ✅ No unnecessary scanning
- ✅ Efficient and fast
- ✅ No resource waste

## 🔧 **Troubleshooting**

### If trigger doesn't work:
1. Check file exists: `ls -la /path/to/file`
2. Check permissions: `chmod +x discovery_trigger.py`
3. Check database: `ls -la discovery_registry.db`
4. Run with debug: `python3 discovery_trigger.py /path/file`

### If duplicate errors:
1. Check existing entries: `sqlite3 discovery_registry.db "SELECT * FROM discovery_services;"`
2. Remove duplicate if needed: `sqlite3 discovery_registry.db "DELETE FROM discovery_services WHERE service_name = 'name';"`
3. Re-run trigger

---

**This trigger-based system is the foundation of the 3-database ZmartBot service lifecycle!** 🚀