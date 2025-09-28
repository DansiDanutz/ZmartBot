# ZmartBot Professional Service Dashboard

A modern, dark-themed professional dashboard for managing and monitoring all ZmartBot services across three levels of service classification.

## 🎯 Features

### **Professional Dark Theme**
- Modern, sleek dark interface with gradient backgrounds
- Smooth animations and hover effects
- Professional color scheme with accent colors
- Responsive design for all screen sizes

### **Three-Level Service Management**
- **Level 1 - Discovery**: 237 basic services with MDC and/or Python files
- **Level 2 - Active/Passport**: 21 services with MDC + Python + Port + Passport
- **Level 3 - Certified**: 43 fully certified services with all requirements

### **Interactive Card System**
- Click on any level card to expand and see all services
- Filter services by Passport and Certified status
- Real-time status indicators (green for online, red for offline)
- Service details modal with comprehensive information

### **Service Management Actions**
- **Restart Service**: Restart any service with one click
- **Fix Bug**: Send service to bug fixing system
- **Send to Doctor**: Route service to Doctor Service for analysis
- Real-time notifications for all actions

### **System Overview**
- Total services count
- Online/offline service statistics
- Real-time system health monitoring
- Auto-refresh every 30 seconds

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- FastAPI, Uvicorn, httpx

### Installation
```bash
# Navigate to dashboard directory
cd zmart-api/dashboard/Service-Dashboard

# Install dependencies (if needed)
pip3 install fastapi uvicorn httpx

# Start the dashboard
./start_dashboard.sh
```

### Access Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:3000
```

## 📁 File Structure

```
Service-Dashboard/
├── index.html          # Main dashboard HTML
├── dashboard.css       # Professional dark theme styles
├── dashboard.js        # Interactive functionality
├── api_server.py       # FastAPI backend server
├── start_dashboard.sh  # Startup script
├── README.md          # This file
└── styles.css         # Legacy styles (backup)
```

## 🎨 Design Features

### **Color Scheme**
- Primary Background: `#0a0e17` (Deep dark blue)
- Secondary Background: `#1a1f2e` (Dark blue-gray)
- Card Background: `#252b3d` (Medium dark blue)
- Accent Color: `#4fd1c7` (Teal)
- Success: `#48bb78` (Green)
- Error: `#f56565` (Red)
- Warning: `#ed8936` (Orange)

### **Animations**
- Smooth hover effects on cards
- Fade-in animations for service grids
- Pulsing status indicators
- Smooth transitions for all interactions

### **Responsive Design**
- Mobile-friendly layout
- Adaptive grid system
- Touch-friendly buttons
- Optimized for all screen sizes

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Main dashboard
- `GET /health` - Health check
- `GET /api/services/status` - Get all services status
- `GET /api/system/overview` - System overview data

### Service Management
- `POST /api/services/{name}/restart` - Restart service
- `POST /api/services/{name}/stop` - Stop service
- `POST /api/services/{name}/start` - Start service
- `POST /api/services/{name}/fix` - Fix service bugs
- `POST /api/services/{name}/doctor` - Send to Doctor Service
- `GET /api/services/{name}/logs` - Get service logs

### Service Levels
- `GET /api/services/levels` - Get services organized by level

## 🎯 Service Classification

### Level 1 - Discovery (237 services)
- Basic services with MDC and/or Python files
- No port assignment required
- No passport required
- Examples: `21indicators`, `API-Manager`, `Backend`

### Level 2 - Active/Passport (21 services)
- Services with MDC + Python + Port + Passport
- Active passport status
- Network port assigned
- Examples: `OrchestrationStart`, `TradingStrategy`, `YAMLGovernanceService`

### Level 3 - Certified (43 services)
- Fully certified services with all requirements
- Complete compliance with all standards
- Highest level of service maturity
- Examples: `achievements`, `database-service`, `zmart-api`

## 🔍 Service Status Indicators

### Visual Indicators
- **Green Light**: Service is online and healthy
- **Red Light**: Service is offline or has issues
- **Pulsing Animation**: Real-time status updates

### Status Types
- **Online**: Service is running and responding
- **Offline**: Service is not responding or stopped
- **Loading**: Service is starting up
- **Error**: Service has encountered an error

## 🛠️ Customization

### Adding New Services
1. Update the `servicesData` object in `dashboard.js`
2. Add service information with proper level classification
3. Ensure correct port numbers and status

### Modifying Styles
1. Edit `dashboard.css` for visual changes
2. CSS variables are defined in `:root` for easy theming
3. All colors and spacing can be customized

### Adding New Actions
1. Add new API endpoints in `api_server.py`
2. Update JavaScript functions in `dashboard.js`
3. Add corresponding UI elements in `index.html`

## 🔒 Security Features

- Input validation on all API endpoints
- Error handling for all service operations
- Secure service management actions
- Health check monitoring

## 📊 Performance

- Optimized for fast loading
- Efficient service data management
- Minimal API calls with caching
- Smooth animations without performance impact

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check if port 3000 is available
lsof -i :3000

# Kill existing process if needed
pkill -f "api_server.py"
```

**Services not showing:**
- Check if database service is running on port 8900
- Verify API endpoints are responding
- Check browser console for errors

**Styling issues:**
- Clear browser cache
- Check if CSS file is loading properly
- Verify Font Awesome CDN is accessible

## 📈 Future Enhancements

- Real-time WebSocket connections for live updates
- Advanced filtering and search capabilities
- Service performance metrics and charts
- User authentication and role-based access
- Service dependency mapping
- Automated health checks and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This dashboard is part of the ZmartBot project and follows the same licensing terms.

---

**Built with ❤️ for ZmartBot Service Management**
















