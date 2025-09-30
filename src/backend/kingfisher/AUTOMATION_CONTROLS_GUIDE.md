# 🔧 KingFisher Automation Controls Guide

## 🎯 **OVERVIEW**

The KingFisher system now supports **full automation control** and **manual image processing**. You can enable/disable automatic monitoring and process images manually when needed.

---

## 🚀 **AUTOMATION CONTROLS**

### **1. Enable Automation**
```bash
curl -X POST http://localhost:8100/api/v1/telegram/enable-automation
```
**Response:**
```json
{
  "success": true,
  "message": "Automation enabled",
  "automation_status": "enabled"
}
```

### **2. Disable Automation**
```bash
curl -X POST http://localhost:8100/api/v1/telegram/disable-automation
```
**Response:**
```json
{
  "success": true,
  "message": "Automation disabled",
  "automation_status": "disabled"
}
```

### **3. Check Automation Status**
```bash
curl -X GET http://localhost:8100/api/v1/telegram/automation-status
```
**Response:**
```json
{
  "automation_enabled": true,
  "monitoring_active": true,
  "connected": true,
  "message": "Automation status retrieved"
}
```

---

## 📤 **MANUAL IMAGE PROCESSING**

### **1. Upload Manual Image**
```bash
curl -X POST http://localhost:8100/api/v1/images/upload-manual \
  -F "file=@/path/to/your/image.jpg" \
  -F "user_id=424184493" \
  -F "username=SemeCJ"
```

### **2. Process Existing File**
```bash
curl -X POST http://localhost:8100/api/v1/images/process-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/your/image.jpg",
    "user_id": 424184493,
    "username": "SemeCJ"
  }'
```

---

## 📊 **AUTOMATION STATES**

### **🟢 ENABLED (Default)**
- **Automatic monitoring** of @thekingfisher_liqmap_bot
- **Real-time processing** of posted images
- **Immediate alerts** for high significance results
- **Background operation** - no manual intervention needed

### **🔴 DISABLED**
- **No automatic monitoring** of KingFisher bot
- **Manual processing only** via upload or forwarding
- **Paused automation** - saves resources
- **Selective processing** - you choose which images to analyze

---

## 🎯 **WHEN TO USE EACH MODE**

### **🟢 ENABLE AUTOMATION WHEN:**
- ✅ You want **24/7 monitoring** of KingFisher
- ✅ You want **real-time alerts** for market opportunities
- ✅ You're **actively trading** and need immediate signals
- ✅ You have **stable internet** and system resources

### **🔴 DISABLE AUTOMATION WHEN:**
- ⏸️ You want to **pause monitoring** temporarily
- ⏸️ You're **testing specific images** manually
- ⏸️ You want to **save system resources**
- ⏸️ You're **not actively trading** and want to avoid noise

---

## 📱 **MANUAL IMAGE SOURCES**

### **1. Telegram Forwarding**
- Forward KingFisher images to your bot
- **Immediate processing** and analysis
- **Confirmation message** sent back to you

### **2. API Upload**
- Upload images via web interface or API
- **Batch processing** of multiple images
- **Detailed analysis results** returned

### **3. File System**
- Process images stored on your computer
- **Direct file path** processing
- **No upload required**

---

## 🔄 **WORKFLOW EXAMPLES**

### **Example 1: Active Trading Session**
```bash
# 1. Enable automation for real-time monitoring
curl -X POST http://localhost:8100/api/v1/telegram/enable-automation

# 2. Check status
curl -X GET http://localhost:8100/api/v1/telegram/automation-status

# 3. System automatically processes KingFisher images
# 4. Receive alerts for high significance results
```

### **Example 2: Manual Analysis Session**
```bash
# 1. Disable automation to focus on specific images
curl -X POST http://localhost:8100/api/v1/telegram/disable-automation

# 2. Upload specific image for analysis
curl -X POST http://localhost:8100/api/v1/images/upload-manual \
  -F "file=@important_kingfisher_image.jpg"

# 3. Process multiple images from folder
for file in /path/to/images/*.jpg; do
  curl -X POST http://localhost:8100/api/v1/images/process-file \
    -H "Content-Type: application/json" \
    -d "{\"file_path\": \"$file\"}"
done
```

### **Example 3: Selective Monitoring**
```bash
# 1. Disable automation
curl -X POST http://localhost:8100/api/v1/telegram/disable-automation

# 2. Manually forward only important images to your bot
# 3. System processes only the images you choose
# 4. No noise from less significant posts
```

---

## 🎛️ **ADVANCED CONTROLS**

### **Webhook Management (Production)**
```bash
# Setup webhook for production
curl -X POST http://localhost:8100/api/v1/telegram/setup-webhook \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://your-domain.com/webhook/telegram"}'

# Delete webhook (switch back to polling)
curl -X POST http://localhost:8100/api/v1/telegram/delete-webhook

# Check webhook status
curl -X GET http://localhost:8100/api/v1/telegram/webhook-info
```

### **Monitoring Controls**
```bash
# Start monitoring
curl -X POST http://localhost:8100/api/v1/telegram/start-monitoring

# Stop monitoring
curl -X POST http://localhost:8100/api/v1/telegram/stop-monitoring

# Check monitoring status
curl -X GET http://localhost:8100/api/v1/telegram/monitoring-status
```

---

## 🔧 **TROUBLESHOOTING**

### **Automation Not Working**
1. Check if automation is enabled: `GET /automation-status`
2. Enable automation: `POST /enable-automation`
3. Verify bot connection: `POST /test-connection`

### **Manual Upload Failing**
1. Ensure file is an image (jpg, png, etc.)
2. Check file size (max 10MB)
3. Verify API endpoint is accessible

### **No Alerts Received**
1. Check Telegram bot connection
2. Verify chat ID is correct
3. Ensure automation is enabled

---

## 📈 **BEST PRACTICES**

### **For Active Trading:**
- ✅ Keep automation **ENABLED**
- ✅ Monitor alerts for **high significance** (>70%)
- ✅ Use manual upload for **specific analysis**

### **For Research/Analysis:**
- ⏸️ **DISABLE** automation to avoid noise
- 📤 Use **manual upload** for specific images
- 📊 Focus on **detailed analysis** of chosen images

### **For System Maintenance:**
- ⏸️ **DISABLE** automation during updates
- 🔄 **RESTART** monitoring after maintenance
- ✅ **VERIFY** connection before re-enabling

---

## 🎯 **SUMMARY**

Your KingFisher system now provides **complete control** over automation:

- **🟢 ENABLE**: Full automatic monitoring
- **🔴 DISABLE**: Manual processing only  
- **📤 MANUAL**: Upload specific images for analysis
- **⚙️ CONTROL**: Start/stop monitoring as needed

**The system adapts to your trading style and needs!** 🚀 