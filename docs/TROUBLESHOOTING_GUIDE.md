# KingFisher System - Troubleshooting Guide

**Date**: July 30, 2025  
**Purpose**: Quick reference for identifying and fixing common issues  
**Status**: ✅ **ACTIVE MAINTENANCE GUIDE**

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: "Symbol Not Updated in Airtable"**

#### **Symptoms:**
- Symbol appears to be processed but doesn't show in Airtable
- Airtable status shows "disconnected"
- No error messages in logs

#### **Root Causes:**
1. **Airtable Connection Issues**: Temporary disconnection from Airtable API
2. **Wrong Server Running**: Running `backend/zmart-api` instead of KingFisher
3. **Missing Images**: Symbol processed without required liquidation images
4. **Import Path Errors**: Server not starting due to import issues

#### **Solutions:**

**Step 1: Check Which Server is Running**
```bash
# Check what's running on port 8100
lsof -i :8100

# Check what's running on port 8000 (wrong server)
lsof -i :8000
```

**Step 2: Verify KingFisher Server**
```bash
# Test health endpoint
curl http://localhost:8100/health

# Expected response:
# {"status":"healthy","module":"kingfisher",...}
```

**Step 3: Test Airtable Connection**
```bash
# Test Airtable status
curl http://localhost:8100/api/v1/airtable/status

# Expected response:
# {"success":true,"status":"connected",...}
```

**Step 4: Test Symbol Processing**
```bash
# Test with mock images
curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
  -F "symbol=TESTUSDT" \
  -F "image_id=test_123" \
  -F "significance_score=0.85" \
  -F "market_sentiment=bullish" \
  -F "total_clusters=4" \
  -F "total_flow_area=2800" \
  -F "liquidation_map_image=@/dev/null" \
  -F "liquidation_heatmap_image=@/dev/null"
```

### **Issue 2: "Wrong Server Running"**

#### **Symptoms:**
- Trying to run `backend/zmart-api` server
- Import errors: `ModuleNotFoundError: No module named 'config'`
- Server errors on port 8000 instead of 8100

#### **Solutions:**

**Step 1: Kill Wrong Server**
```bash
# Find processes on port 8000
lsof -i :8000

# Kill the wrong server
kill -9 <PID>
```

**Step 2: Start Correct KingFisher Server**
```bash
# Navigate to KingFisher directory
cd kingfisher-module/backend

# Activate virtual environment
source venv/bin/activate

# Start KingFisher server
uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload
```

**Step 3: Verify Correct Server**
```bash
# Test health endpoint
curl http://localhost:8100/health

# Should return KingFisher health status
```

### **Issue 3: "Image Validation Errors"**

#### **Symptoms:**
- Error: "Missing required liquidation images for symbol: XXXUSDT"
- Symbols not being created in Airtable
- 400 Bad Request responses

#### **Solutions:**

**Step 1: Ensure Images Are Provided**
```bash
# Test WITHOUT images (should fail)
curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
  -F "symbol=TESTUSDT" \
  -F "image_id=test_no_images" \
  -F "significance_score=0.85" \
  -F "market_sentiment=bullish" \
  -F "total_clusters=4" \
  -F "total_flow_area=2800"

# Expected: {"detail":"At least one of 'liquidation_map_image' or 'liquidation_heatmap_image' must be provided."}
```

**Step 2: Test WITH Images**
```bash
# Test WITH mock images (should succeed)
curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
  -F "symbol=TESTUSDT" \
  -F "image_id=test_with_images" \
  -F "significance_score=0.85" \
  -F "market_sentiment=bullish" \
  -F "total_clusters=4" \
  -F "total_flow_area=2800" \
  -F "liquidation_map_image=@/dev/null" \
  -F "liquidation_heatmap_image=@/dev/null"

# Expected: Success response with record creation
```

### **Issue 4: "Import Path Errors"**

#### **Symptoms:**
- `ModuleNotFoundError: No module named 'config'`
- Server won't start
- Import errors in logs

#### **Solutions:**

**Step 1: Check Current Directory**
```bash
# Make sure you're in the right directory
pwd
# Should be: /Users/dansidanutz/Desktop/ZmartBot/kingfisher-module/backend
```

**Step 2: Verify Virtual Environment**
```bash
# Activate virtual environment
source venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

**Step 3: Start Server with Correct Path**
```bash
# Start with PYTHONPATH set
PYTHONPATH=src uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload
```

### **Issue 5: "Airtable Field Errors"**

#### **Symptoms:**
- `422 Unprocessable Entity` errors
- `UNKNOWN_FIELD_NAME` errors
- Airtable connection issues

#### **Solutions:**

**Step 1: Check Airtable Status**
```bash
curl http://localhost:8100/api/v1/airtable/status
```

**Step 2: Test Record Creation**
```bash
# Test with a simple symbol
curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
  -F "symbol=TESTUSDT" \
  -F "image_id=test_airtable" \
  -F "significance_score=0.85" \
  -F "market_sentiment=bullish" \
  -F "total_clusters=4" \
  -F "total_flow_area=2800" \
  -F "liquidation_map_image=@/dev/null" \
  -F "liquidation_heatmap_image=@/dev/null"
```

## 🔧 **QUICK DIAGNOSTIC COMMANDS**

### **System Health Check**
```bash
# 1. Check server status
curl http://localhost:8100/health

# 2. Check Airtable connection
curl http://localhost:8100/api/v1/airtable/status

# 3. Test image processing
curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
  -F "symbol=DIAGNOSTICUSDT" \
  -F "image_id=diagnostic_test" \
  -F "significance_score=0.85" \
  -F "market_sentiment=bullish" \
  -F "total_clusters=4" \
  -F "total_flow_area=2800" \
  -F "liquidation_map_image=@/dev/null" \
  -F "liquidation_heatmap_image=@/dev/null"
```

### **Server Restart Procedure**
```bash
# 1. Kill all Python processes
pkill -f uvicorn
pkill -f python

# 2. Check ports
lsof -i :8100
lsof -i :8000

# 3. Start KingFisher server
cd kingfisher-module/backend
source venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload
```

## 📊 **EXPECTED BEHAVIORS**

### **✅ Successful Processing**
- **Health Check**: `{"status":"healthy","module":"kingfisher",...}`
- **Airtable Status**: `{"success":true,"status":"connected",...}`
- **Symbol Processing**: Creates/updates record with professional report
- **Field Formatting**: All fields properly formatted (24h48h, 7days, 1Month, Score, Result)

### **❌ Common Error Responses**
- **No Images**: `{"detail":"At least one of 'liquidation_map_image' or 'liquidation_heatmap_image' must be provided."}`
- **Wrong Server**: Import errors or 404 responses
- **Airtable Issues**: `422 Unprocessable Entity` or connection errors

## 🎯 **PREVENTION CHECKLIST**

### **Before Testing New Symbols:**
- [ ] Verify KingFisher server running on port 8100
- [ ] Confirm Airtable connection status
- [ ] Test with mock images first
- [ ] Check health endpoint response
- [ ] Ensure virtual environment activated

### **When Issues Occur:**
- [ ] Check which server is running
- [ ] Verify Airtable connection
- [ ] Test image validation
- [ ] Restart server if needed
- [ ] Check import paths

## 📞 **EMERGENCY CONTACTS**

### **Critical Issues:**
1. **Server Won't Start**: Check import paths and virtual environment
2. **Airtable Not Working**: Verify API keys and connection
3. **Images Not Processing**: Ensure liquidation images provided
4. **Wrong Server Running**: Kill processes and start correct server

### **Quick Fix Commands:**
```bash
# Emergency restart
pkill -f uvicorn
cd kingfisher-module/backend
source venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload
```

---

**Last Updated**: July 30, 2025  
**Next Review**: After next issue resolution  
**Status**: ✅ **ACTIVE TROUBLESHOOTING GUIDE** 