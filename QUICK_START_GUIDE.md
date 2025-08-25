# 🚀 ZmartBot Trading Platform - Quick Start Guide

## ⚡ **ONE-COMMAND START**

```bash
# Start everything
./start_zmartbot.sh start

# Check status
./start_zmartbot.sh status

# Stop everything
./start_zmartbot.sh stop
```

## 🌐 **ACCESS YOUR DASHBOARD**

**Main Dashboard**: http://localhost:3400  
**API Documentation**: http://localhost:8000/docs  
**Health Check**: http://localhost:8000/health

## 📊 **CURRENT STATUS**

✅ **Backend API**: Running on port 8000  
✅ **Dashboard**: Running on port 3400  
✅ **Symbols**: 10 symbols in portfolio  
✅ **Header**: Zmart logo and branding restored  
✅ **Interactive Charts**: Fully functional  
✅ **Analytics**: Portfolio analysis working  

## 🎯 **FEATURES READY**

- **Symbols Management**: Add/remove from KuCoin/Binance
- **Interactive Charts**: Candlestick charts with indicators
- **Analytics Dashboard**: Portfolio performance analysis
- **Performance Tracking**: Historical data visualization
- **Daily Updates**: Automated price data sync

## 📁 **CRITICAL FILES**

- **System Status**: `ZmartBot_System_Status.md`
- **Quick Start**: `start_zmartbot.sh`
- **Backend**: `backend/zmart-api/`
- **Frontend**: `Documentation/complete-trading-platform-package/dashboard-source/`

## 🔧 **TROUBLESHOOTING**

### If Dashboard Shows Black Screen:
1. Check if backend is running: `curl http://localhost:8000/health`
2. Check if dashboard is running: `curl http://localhost:3400`
3. Restart system: `./start_zmartbot.sh restart`

### If Symbols Don't Load:
1. Check API: `curl http://localhost:8000/api/futures-symbols/my-symbols/current`
2. Check browser console for errors
3. Restart backend: `./start_zmartbot.sh restart`

## 📞 **SUPPORT**

- **Backend Logs**: Check terminal running uvicorn
- **Frontend Errors**: Browser developer tools
- **System Status**: `./start_zmartbot.sh status`

---

**Last Updated**: 2025-08-10 13:02  
**Status**: ✅ FULLY OPERATIONAL
