# 🎯 OFFICIAL ZMARTBOT STRUCTURE

## THE SINGLE SOURCE OF TRUTH

### 🚀 **OFFICIAL BACKEND** (THE ONLY ONE)
```
/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/
├── src/main.py                    ← Main API Server (Port 8000)
├── professional_dashboard_server.py ← Dashboard Server (Port 3400)
├── src/
│   ├── routes/                    ← All API routes
│   ├── services/                  ← Business logic
│   ├── agents/                    ← Multi-agent system
│   └── config/                    ← Configuration
├── venv/                          ← Python environment
└── requirements.txt               ← Dependencies
```

### 🎨 **OFFICIAL FRONTEND** (THE ONLY ONE)
```
/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/
├── App.jsx                        ← Main React app
├── components/
│   ├── RealTimeLiveAlerts.jsx     ← Live Alerts system
│   ├── RealTimeLiveAlerts.css     ← Live Alerts styling
│   ├── SymbolsManager.jsx         ← Symbol management
│   └── Sidebar.jsx                ← Navigation
├── dist/                          ← Built files (served by dashboard server)
├── package.json                   ← React dependencies
└── vite.config.js                 ← Build configuration
```

## 🔧 **HOW TO START THE SYSTEM**

### Start Backend API (Port 8000)
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
source venv/bin/activate
python src/main.py
```

### Start Dashboard Server (Port 3400)
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
python professional_dashboard_server.py
```

### Build Frontend (when needed)
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard
npm run build
```

## 📍 **ACCESS POINTS**
- **Professional Dashboard**: http://localhost:3400/
- **Live Alerts**: http://localhost:3400/enhanced-alerts
- **Backend API**: http://localhost:8000/api/
- **API Documentation**: http://localhost:8000/docs

## 🚫 **WHAT TO IGNORE**

### Legacy/Module Locations (DO NOT USE FOR MAIN DEVELOPMENT)
- `backend_legacy_backup/` - Old backup files
- `zmart-platform/` - Old platform structure
- `backend/zmart-api/` - Legacy backend location
- Any other dashboard implementations

### Specialized Modules (Have their own backend/frontend)
- `Alerts/` - Alerts module
- `kingfisher-module/` - KingFisher module
- `modules/` - Various specialized modules

## ✅ **DEVELOPMENT RULES**

### For Backend Development:
1. **ALWAYS** work in `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/`
2. Add routes in `src/routes/`
3. Add services in `src/services/`
4. Add agents in `src/agents/`

### For Frontend Development:
1. **ALWAYS** work in `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/`
2. Add components in `components/`
3. Update routing in `App.jsx`
4. Build with `npm run build`
5. Restart dashboard server after building

### For Live Alerts:
1. **Component**: `project/frontend/dashboard/components/RealTimeLiveAlerts.jsx`
2. **Styling**: `project/frontend/dashboard/components/RealTimeLiveAlerts.css`
3. **Access**: http://localhost:3400/enhanced-alerts

## 🎯 **THIS IS THE OFFICIAL STRUCTURE - USE ONLY THIS!**