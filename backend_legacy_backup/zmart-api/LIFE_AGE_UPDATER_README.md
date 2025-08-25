# Life Age Updater System

## Overview
The Life Age Updater automatically increments the Life Age for all cryptocurrency symbols by +1 every day at 1 AM. This system tracks how long each symbol has been in the system.

## Features
- ✅ **Automatic Daily Updates**: Runs every day at 1:00 AM
- ✅ **All 22 Symbols**: Covers all symbols in the menu (BTC, ETH, XRP, etc.)
- ✅ **Database Storage**: SQLite database for persistent storage
- ✅ **API Integration**: REST API endpoints for frontend integration
- ✅ **Logging**: Comprehensive logging for monitoring
- ✅ **Health Checks**: API health check endpoint

## Files Created

### Core Scripts
- `life_age_updater.py` - Main updater script with scheduler
- `test_life_age.py` - Test script to verify functionality
- `requirements_life_age.txt` - Python dependencies

### Management Scripts
- `start_life_age_updater.sh` - Start the updater in background
- `stop_life_age_updater.sh` - Stop the updater process

### API Integration
- `src/routes/life_age.py` - FastAPI routes for frontend integration
- Updated `professional_dashboard_server.py` - Added life age router

## Installation & Setup

### 1. Install Dependencies
```bash
cd backend/zmart-api
pip3 install -r requirements_life_age.txt
```

### 2. Test the System
```bash
python3 test_life_age.py
```

### 3. Start the Updater
```bash
./start_life_age_updater.sh
```

### 4. Stop the Updater (if needed)
```bash
./stop_life_age_updater.sh
```

## Database Schema

### Table: `life_age`
```sql
CREATE TABLE life_age (
    symbol TEXT PRIMARY KEY,
    age_days INTEGER DEFAULT 365,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Get All Life Ages
```http
GET /api/v1/life-age/all
```

### Get Specific Symbol Life Age
```http
GET /api/v1/life-age/{symbol}
```

### Set Symbol Life Age
```http
POST /api/v1/life-age/{symbol}
Content-Type: application/json

{
    "symbol": "BTC",
    "age_days": 500
}
```

### Health Check
```http
GET /api/v1/life-age/status/health
```

## Monitoring

### Log Files
- `life_age_updater.log` - Main application logs
- `life_age_updater.out` - Standard output/error logs

### Process Management
- `life_age_updater.pid` - Process ID file for management

## Symbols Covered
All 22 symbols from the menu:
- BTC, ETH, XRP, BNB, SOL, DOGE, ADA, LINK, AVAX
- XLM, SUI, DOT, LTC, XMR, AAVE, VET, ATOM, RENDER
- HBAR, XTZ, TON, TRX

## Integration with Frontend

The Life Age data is now available in the Management tab of the RiskMetric section. The frontend can:

1. **Display Current Life Age**: Shows the current age for the selected symbol
2. **Update Life Age**: Allows manual updates through the UI
3. **Real-time Updates**: Reflects changes immediately

## Cron Alternative

If you prefer to use cron instead of the Python scheduler:

```bash
# Add to crontab (crontab -e)
0 1 * * * cd /path/to/backend/zmart-api && python3 -c "from life_age_updater import run_daily_update; run_daily_update()"
```

## Troubleshooting

### Check if Updater is Running
```bash
ps aux | grep life_age_updater.py
```

### Check Logs
```bash
tail -f life_age_updater.log
```

### Restart Updater
```bash
./stop_life_age_updater.sh
./start_life_age_updater.sh
```

### Manual Update
```bash
python3 -c "from life_age_updater import run_daily_update; run_daily_update()"
```

## Security Notes
- The updater runs with the same permissions as the user who started it
- Database file is stored in `data/life_age.db`
- Logs may contain sensitive information - secure appropriately
- API endpoints should be protected in production

## Future Enhancements
- [ ] Webhook notifications for updates
- [ ] Email alerts for failures
- [ ] Dashboard monitoring interface
- [ ] Backup/restore functionality
- [ ] Historical age tracking
