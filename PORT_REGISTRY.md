# 📋 PORT REGISTRY - ZmartBot Services

## 🚦 RESERVED PORTS - DO NOT CHANGE

| Port | Service | Project | Status | Command |
|------|---------|---------|---------|---------|
| **3000** | ZmartyChat Main | /ZmartyChat/index.html | Reserved | `npm start` |
| **3001** | ZmartyChat Mobile | /ZmartyChat/mobile-app | Reserved | `npm start` |
| **3002** | ZmartBot Mobile | /zmartbot-mobile | Reserved | `npm start` |
| **8000** | ZmartBot API | /zmart-api | Reserved | Python API |
| **8080** | Web Dashboard | /ZmartyChat/web-app | Reserved | `python3 -m http.server 8080` |
| **8081** | Admin Dashboard | /ZmartyChat/admin | Reserved | `python3 -m http.server 8081` |
| **9000** | ZmartyChat UserApp | /ZmartyChat/ZmartyUserApp | Reserved | `node server-port-9000.js` |
| **5173** | Vite Dev Server | Various | Reserved | `npm run dev` |
| **7777** | Mobile Service | /src/services | Reserved | Mobile backend |

## 🛑 BEFORE STARTING ANY SERVICE

1. Check what's running:
```bash
lsof -i :3000  # Check if port 3000 is in use
lsof -i :8080  # Check if port 8080 is in use
```

2. Kill existing service if needed:
```bash
kill -9 $(lsof -t -i:3000)  # Kill whatever is on port 3000
kill -9 $(lsof -t -i:8080)  # Kill whatever is on port 8080
```

3. Start with the ASSIGNED port:
```bash
cd /path/to/project
npm start  # Will use the configured port
```

## 📁 PROJECT LOCATIONS

- **ZmartyChat Main**: `/Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/`
- **ZmartyChat Mobile**: `/Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/mobile-app/`
- **ZmartBot Mobile**: `/Users/dansidanutz/Desktop/ZmartBot/zmartbot-mobile/`
- **ZmartBot API**: `/Users/dansidanutz/Desktop/ZmartBot/zmart-api/`

## 🔧 SERVICE MANAGEMENT COMMANDS

### Start All Services (Organized)
```bash
# 1. Kill all existing services
pkill -f "node"
pkill -f "python3 -m http.server"

# 2. Start each service on its dedicated port
cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/web-app
python3 -m http.server 8080 &

cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/mobile-app
npm start &  # Will use port 3001
```

### Check All Running Services
```bash
# See all services and their ports
lsof -i -P | grep LISTEN | grep -E '3000|3001|3002|8000|8080|8081'
```

### Stop All Services
```bash
# Stop everything cleanly
pkill -f "node"
pkill -f "python3 -m http.server"
pkill -f "webpack"
```

## ⚠️ RULES

1. **NEVER** start a service without checking the port first
2. **ALWAYS** use the assigned port from this registry
3. **ALWAYS** stop services when done working
4. **NEVER** leave services running overnight
5. **UPDATE** this file when adding new services

## 📊 Current Status (Update Daily)

Last Updated: 2024-09-18
- [ ] Port 3000: FREE
- [ ] Port 3001: FREE
- [x] Port 3002: RUNNING - ZmartyChat Mobile
- [ ] Port 8000: FREE
- [ ] Port 8080: FREE
- [x] Port 8081: RUNNING - Web Dashboard
- [ ] Port 5173: FREE
- [ ] Port 7777: FREE

---

**Remember**: One project = One port = One service at a time!