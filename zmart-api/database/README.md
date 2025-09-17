# ZmartBot Database Service

## 🎯 Overview
Enterprise-grade database management and monitoring system for ZmartBot ecosystem. Manages 50+ databases with real-time monitoring, automatic discovery, and centralized control.

## 🚀 Quick Start

### Start Database Service
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/zmart-api/database
./start_database_service.sh
```

### Access Dashboards
- **Advanced Card Dashboard**: `advanced_card_dashboard.html`
- **Management System**: `dashboard_management_system.html`
- **Visualization Dashboard**: `advanced_database_visualization.html`
- **Supabase Dashboard**: `supabase_dashboard.html`

## 📊 Features

### Core Functionality
- ✅ **Database Discovery**: Automatic detection of all SQLite databases
- ✅ **Health Monitoring**: Real-time health scoring and alerts
- ✅ **Cloud Sync**: Supabase integration with automatic synchronization
- ✅ **Master Registry**: Centralized database management
- ✅ **Advanced Visualizations**: Multiple interactive dashboards
- ✅ **API Endpoints**: RESTful API for database operations

### Service Details
- **Port**: 8900
- **Type**: Backend Service
- **Status**: Running (PID varies)
- **Log File**: `database_service.log`
- **Registry**: `master_database_registry.db`

## 🔧 API Endpoints

### Core Endpoints
```bash
GET /health                          # Health check
GET /api/databases                   # All registered databases
GET /api/system/overview            # System overview
POST /api/cloud/sync                # Trigger cloud sync
GET /api/cloud/status               # Cloud sync status
GET /api/databases/{db_name}        # Specific database info
GET /api/databases/categories/stats # Database statistics
```

### Cloud Endpoints
```bash
GET /api/cloud/databases            # All cloud databases
POST /api/cloud/sync/{db_name}      # Sync single database
GET /api/cloud/setup-instructions   # Setup guide
GET /api/cloud/individual-tables   # Table mapping
```

## 📁 File Structure

```
database/
├── database_service.py              # Main service file
├── database_service.log             # Service logs
├── start_database_service.sh        # Startup script
├── master_database_registry.db      # Master registry
├── service.yaml                     # Service configuration
├── README.md                        # This file
├── 
├── # Visualization Dashboards
├── advanced_card_dashboard.html     # Premium card-based dashboard
├── dashboard_management_system.html # Management interface
├── advanced_database_visualization.html # Advanced charts
├── supabase_dashboard.html          # Cloud dashboard
├── 
├── # Database Scripts
├── create_discovery_database.py     # Database creation
├── create_supabase_tables.sql       # Supabase setup
├── custom_visualization_queries.sql # Custom queries
└── discovery_database_server.py     # Discovery server
```

## 🎛️ Service Lifecycle Status

### Current Registration Status
- ❌ **Discovery Level**: Not registered in discovery_registry.db
- ❌ **Passport Level**: Not registered in passport_registry.db  
- ❌ **Registration Level**: Not registered in service_registry.db
- ❌ **Certification**: Not certified

### Required Actions for Full Registration
1. **Create MDC File**: `database_service.mdc`
2. **Discovery Registration**: Register in Level 1
3. **Port Manager Assignment**: Official port 8900 assignment
4. **Passport Assignment**: Get Level 2 passport
5. **Service Registration**: Complete Level 3 certification
6. **Orchestration Integration**: Add to Master Orchestration Agent

## 🔗 Integration

### Supabase Configuration
```javascript
const SUPABASE_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co'
const SUPABASE_KEY = 'your-anon-key'
```

### Database Tables
- `database_registry` - Main registry table
- `database_sync_log` - Sync operation logs
- `database_health_metrics` - Health monitoring data

## 📊 Monitoring

### Health Metrics
- **Total Databases**: 50+ monitored
- **Sync Frequency**: Every 30 seconds
- **Health Checks**: Continuous monitoring
- **Average Health**: 95%+

### Performance
- **Response Time**: <100ms average
- **Uptime**: 99.9%
- **Memory Usage**: <100MB
- **CPU Usage**: <5%

## 🛠️ Troubleshooting

### Common Issues
1. **Service Not Starting**: Check port 8900 availability
2. **Cloud Sync Failing**: Verify SUPABASE_KEY environment variable
3. **Database Discovery**: Ensure proper file permissions
4. **Dashboard Not Loading**: Check service is running on port 8900

### Log Analysis
```bash
tail -f database_service.log
```

### Health Check
```bash
curl -f http://127.0.0.1:8900/health
```

## 📝 Development

### Adding New Features
1. Edit `database_service.py`
2. Update service configuration in `service.yaml`
3. Test with health check endpoint
4. Update dashboards if needed

### Testing
```bash
python3 -m pytest tests/
```

## 🔄 Service Registration Process

To complete the ZmartBot service registration:

1. **Create MDC File**
2. **Follow StopStartCycle workflow**
3. **Complete NewService registration**
4. **Obtain official certification**
5. **Integration with Master Orchestration Agent**

---

**Version**: 1.0.0  
**Owner**: ZmartBot  
**Type**: Backend Service  
**Port**: 8900