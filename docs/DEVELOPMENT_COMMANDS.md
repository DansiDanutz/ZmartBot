# Zmart Trading Bot Platform - Development Commands

## 🚀 Quick Start

### Frontend Development
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/zmart-platform/frontend/zmart-dashboard
npm run dev
```
**URL**: http://localhost:5173

### Backend Development
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api
source venv/bin/activate
python run_dev.py
```
**URL**: http://localhost:8000

## 📋 Alternative Commands

### Using the Startup Script
```bash
./start_dev.sh both      # Start both frontend and backend
./start_dev.sh frontend  # Start frontend only
./start_dev.sh backend   # Start backend only
```

### Using Aliases (if loaded)
```bash
source .zshrc_zmart     # Load aliases (run once)
zmart-frontend          # Start frontend
zmart-backend           # Start backend
zmart-start             # Start both
```

## 🔧 VS Code Configuration

### To Fix Import Errors:
1. **Reload VS Code**: `Cmd+R`
2. **Restart Python Language Server**: `Cmd+Shift+P` → "Python: Restart Language Server"
3. **Select Interpreter**: `Cmd+Shift+P` → "Python: Select Interpreter" → Choose the venv path

### Expected Python Interpreter Path:
```
/Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api/venv/bin/python
```

## 📊 Development URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ⚠️ Common Issues

### Frontend: "Could not read package.json"
**Solution**: Make sure you're in the correct directory:
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/zmart-platform/frontend/zmart-dashboard
```

### Backend: Import errors in VS Code
**Solution**: Reload VS Code and restart Python language server

### Backend: Database connection errors
**Solution**: These are expected in development - the server will start without databases

## 🎯 Current Status

- ✅ **Backend**: Running on port 8000 (with database warnings - normal for development)
- ✅ **Frontend**: Ready to run on port 5173
- ✅ **All Python imports**: Working correctly
- ✅ **VS Code configuration**: Properly set up 