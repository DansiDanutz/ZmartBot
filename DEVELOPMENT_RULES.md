# 🎯 ZMARTBOT DEVELOPMENT RULES

## 🚨 **CRITICAL: SINGLE OFFICIAL STRUCTURE**

### **THE ONLY BACKEND AND FRONTEND TO USE**

```
OFFICIAL BACKEND (ONLY ONE):
/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/

OFFICIAL FRONTEND (ONLY ONE):
/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/
```

## 🚫 **WHAT TO NEVER USE**

### ❌ DEPRECATED/LEGACY LOCATIONS (DO NOT TOUCH)
- `backend_legacy_backup/` - Old backup files
- `backend/zmart-api/` - Legacy backend location  
- `zmart-platform/` - Old platform structure
- Any other dashboard implementations outside the official path

### ❌ WRONG PATHS (DO NOT USE)
- Any backend not in `project/backend/api/`
- Any frontend not in `project/frontend/dashboard/`
- Multiple dashboard servers
- Old configuration files

## ✅ **DEVELOPMENT WORKFLOW**

### For Backend Development:
1. **ALWAYS** navigate to: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/`
2. Activate environment: `source venv/bin/activate`
3. Add routes in: `src/routes/`
4. Add services in: `src/services/`
5. Add agents in: `src/agents/`
6. Start API: `python src/main.py` (Port 8000)
7. Start Dashboard: `python professional_dashboard_server.py` (Port 3400)

### For Frontend Development:
1. **ALWAYS** navigate to: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/`
2. Add components in: `components/`
3. Update routing in: `App.jsx`
4. Build with: `npm run build`
5. Restart dashboard server after building

### For Live Alerts Development:
1. **Component**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/components/RealTimeLiveAlerts.jsx`
2. **Styling**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/components/RealTimeLiveAlerts.css`
3. **Access URL**: http://localhost:3400/enhanced-alerts

## 🔍 **VERIFICATION COMMANDS**

### Check You're in the Right Place:
```bash
# For Backend Development:
pwd
# Should show: /Users/dansidanutz/Desktop/ZmartBot/project/backend/api

# For Frontend Development:
pwd  
# Should show: /Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard
```

### Test Official System:
```bash
# Backend API
curl http://localhost:8000/health

# Dashboard
curl http://localhost:3400/health

# Live Alerts
curl http://localhost:3400/enhanced-alerts
```

## 📦 **MODULE DEVELOPMENT**

### For Specialized Modules:
- Modules can have their own backend/frontend in `project/modules/`
- Each module is self-contained
- Modules don't interfere with official backend/frontend
- Examples: `project/modules/alerts/`, `project/modules/kingfisher/`

## 🚨 **ENFORCEMENT RULES**

### Before Any Development:
1. ✅ Verify you're in the official backend: `project/backend/api/`
2. ✅ Verify you're in the official frontend: `project/frontend/dashboard/`
3. ✅ Never create new backend/frontend directories
4. ✅ Never modify files outside official paths

### Code Review Checklist:
- [ ] All backend changes in `project/backend/api/`
- [ ] All frontend changes in `project/frontend/dashboard/`
- [ ] No new backend/frontend directories created
- [ ] No modifications to legacy/deprecated paths
- [ ] System tested on http://localhost:3400/

## 🎯 **THIS STRUCTURE IS FINAL - NO EXCEPTIONS!**