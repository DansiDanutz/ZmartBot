# 🚨 CRITICAL DEVELOPMENT RULES - NEVER BREAK THESE

## 🔍 **ALWAYS CHECK EXISTING FILES FIRST**

### **BEFORE ANY IMPLEMENTATION:**
1. **SEARCH FOR EXISTING FILES** using `file_search` or `grep_search`
2. **CHECK CURRENT IMPLEMENTATIONS** before creating new ones
3. **VERIFY FILE LOCATIONS** and paths before making changes
4. **READ EXISTING CODE** to understand current structure

### **SPECIFIC RULES:**

#### **Logo Files:**
- ✅ **CORRECT**: `Zmart-Logo-New.jpg` (in dashboard directory)
- ❌ **WRONG**: `Zmart-Logo-New.jpeg` (wrong extension)
- **ALWAYS CHECK**: `list_dir` to see what files actually exist

#### **File Locations:**
- **Dashboard Assets**: `Documentation/complete-trading-platform-package/dashboard/`
- **Source Code**: `Documentation/complete-trading-platform-package/dashboard-source/`
- **Backend**: `backend/zmart-api/`
- **Historical Data**: `Symbol_Price_history_data/`

#### **Before Making Changes:**
1. **Search for existing implementations**
2. **Check file extensions and paths**
3. **Verify current working state**
4. **Read existing documentation**

## 🚫 **NEVER DO THESE:**

- ❌ Start from scratch without checking existing code
- ❌ Assume file names or extensions
- ❌ Create duplicate implementations
- ❌ Ignore existing working features
- ❌ Make changes without understanding current state

## ✅ **ALWAYS DO THESE:**

- ✅ Search for existing files first
- ✅ Check current implementations
- ✅ Verify file paths and extensions
- ✅ Read existing documentation
- ✅ Test before making changes
- ✅ Update system status after fixes

## 📋 **CURRENT WORKING FILES:**

### **Logo Files:**
- `Documentation/complete-trading-platform-package/dashboard/Zmart-Logo-New.jpg` ✅
- `Documentation/complete-trading-platform-package/dashboard/z-logo.png` ✅

### **Critical Components:**
- **App.jsx**: `Documentation/complete-trading-platform-package/dashboard-source/App.jsx`
- **SymbolsManager**: `Documentation/complete-trading-platform-package/dashboard-source/components/SymbolsManager.jsx`
- **Backend API**: `backend/zmart-api/src/main.py`
- **Database**: `backend/zmart-api/my_symbols_v2.db`

## 🔧 **QUICK CHECK COMMANDS:**

```bash
# Check dashboard files
ls -la Documentation/complete-trading-platform-package/dashboard/

# Check source files
ls -la Documentation/complete-trading-platform-package/dashboard-source/

# Check backend files
ls -la backend/zmart-api/src/
```

---

**ENFORCE THESE RULES OR RISK BREAKING WORKING SYSTEMS**
