# 🚀 IntoTheCryptoverse Automated Risk Data System

## 🎯 Overview

Complete automated system for scraping risk grid data from IntoTheCryptoverse every 72 hours and syncing to Supabase. This system ensures the RISKMETRIC Agent always has the latest risk values for accurate trading signals.

## ✅ Features

- **🤖 MCP Browser Integration**: Uses MCP Browser for reliable web scraping
- **⏰ 72-Hour Automation**: Runs automatically every 3 days
- **📊 25 Symbols Coverage**: All major cryptocurrencies
- **🔄 Supabase Sync**: Automatic database updates
- **✅ Data Validation**: Ensures 41 risk points per symbol
- **📈 Success Monitoring**: Detailed reports and logs
- **🛡️ Error Handling**: Retry logic and graceful failures
- **💯 100% Autonomous**: Once configured, runs indefinitely

## 📦 System Components

### 1. **cryptoverse_mcp_scraper.py**
- Main scraper using MCP Browser
- Extracts risk tables from IntoTheCryptoverse
- Validates all 41 risk points (0.000 to 1.000)
- Saves to JSON files in `extracted_risk_grids/`

### 2. **mcp_browser_integration.py**
- MCP Browser client implementation
- Handles navigation, snapshots, and data extraction
- Parses risk tables from page content

### 3. **risk_grid_sync_to_supabase.py**
- Syncs extracted risk grids to Supabase
- Updates `cryptoverse_risk_grid` table
- Verifies data integrity after sync
- Generates sync reports

### 4. **cryptoverse_72h_scheduler.py**
- Automated 72-hour scheduler
- Manages complete update cycles
- Tracks last run and next scheduled run
- Can run as daemon or foreground

## 🔧 Installation & Setup

### Prerequisites

1. **Python 3.8+**
```bash
python3 --version
```

2. **Required Packages**
```bash
pip install supabase python-dotenv schedule psutil
```

3. **Environment Variables**
Create `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. **MCP Browser Setup**
- Ensure MCP Browser is installed and configured
- Browser must be logged in to IntoTheCryptoverse

## 🚀 Quick Start

### Manual Test Run

1. **Test Single Symbol**:
```bash
python3 cryptoverse_mcp_scraper.py --test
```

2. **Scrape All Symbols**:
```bash
python3 cryptoverse_mcp_scraper.py --all
```

3. **Sync to Supabase**:
```bash
python3 risk_grid_sync_to_supabase.py --all
```

4. **Complete Cycle**:
```bash
python3 cryptoverse_mcp_scraper.py --complete
```

### Start Automated Scheduler

1. **Start in Foreground** (for testing):
```bash
python3 cryptoverse_72h_scheduler.py --start
```

2. **Start as Daemon** (production):
```bash
python3 cryptoverse_72h_scheduler.py --start --daemon
```

3. **Check Status**:
```bash
python3 cryptoverse_72h_scheduler.py --status
```

4. **Stop Scheduler**:
```bash
python3 cryptoverse_72h_scheduler.py --stop
```

## 📊 Symbol Mapping

| URL Name | Trading Symbol | Status |
|----------|---------------|---------|
| bitcoin | BTC | ✅ Active |
| ethereum | ETH | ✅ Active |
| binancecoin | BNB | ✅ Active |
| cardano | ADA | ✅ Active |
| ripple | XRP | ✅ Active |
| solana | SOL | ✅ Active |
| avalanche-2 | AVAX | ✅ Active |
| polkadot | DOT | ✅ Active |
| matic-network | MATIC | ✅ Active |
| dogecoin | DOGE | ✅ Active |
| chainlink | LINK | ✅ Active |
| litecoin | LTC | ✅ Active |
| cosmos | ATOM | ✅ Active |
| stellar | XLM | ✅ Active |
| hedera-hashgraph | HBAR | ✅ Active |
| tron | TRX | ✅ Active |
| vechain | VET | ✅ Active |
| monero | XMR | ✅ Active |
| maker | MKR | ✅ Active |
| tezos | XTZ | ✅ Active |
| aave | AAVE | ✅ Active |
| render-token | RNDR | ✅ Active |
| sui | SUI | ✅ Active |
| blockstack | STX | ✅ Active |
| sei-network | SEI | ✅ Active |

## 🔄 Update Workflow

### Every 72 Hours:

1. **Hour 0**: Scheduler wakes up
2. **Phase 1**: Scrape IntoTheCryptoverse
   - Navigate to each symbol's risk page
   - Extract 41 risk points
   - Validate data completeness
   - Save to JSON files

3. **Phase 2**: Sync to Supabase
   - Load validated JSON files
   - Clear existing data for each symbol
   - Insert new 41-point grids
   - Verify data integrity

4. **Phase 3**: Report Generation
   - Success rate calculation
   - Failed symbols logging
   - Next run scheduling
   - State persistence

## 📁 Directory Structure

```
zmart-api/
├── cryptoverse_mcp_scraper.py      # Main scraper
├── mcp_browser_integration.py       # MCP Browser client
├── risk_grid_sync_to_supabase.py   # Supabase sync
├── cryptoverse_72h_scheduler.py     # 72-hour scheduler
├── extracted_risk_grids/            # JSON risk data
│   ├── BTC_risk_grid.json
│   ├── ETH_risk_grid.json
│   └── ... (25 files total)
├── risk_grid_validation/            # Validation reports
│   └── mcp_scrape_report_*.json
├── sync_logs/                       # Sync reports
│   └── sync_report_*.json
├── scheduler_state.json             # Scheduler state
└── cryptoverse_scheduler.log        # Scheduler logs
```

## 📈 Monitoring & Logs

### Log Files

1. **cryptoverse_mcp_scraper.log**: Scraping activities
2. **cryptoverse_scheduler.log**: Scheduler operations
3. **scheduler_state.json**: Current state and last run

### Reports

1. **Scrape Reports**: `risk_grid_validation/mcp_scrape_report_*.json`
   - Success rate
   - Failed symbols
   - Extraction timestamps

2. **Sync Reports**: `sync_logs/sync_report_*.json`
   - Symbols synced
   - Verification results
   - Error details

## 🛠️ Troubleshooting

### Common Issues

1. **MCP Browser Not Connected**
   - Ensure browser is open
   - Check MCP server is running
   - Verify logged in to IntoTheCryptoverse

2. **Low Success Rate**
   - Check website structure hasn't changed
   - Verify login status
   - Review failed symbols in reports

3. **Supabase Sync Failures**
   - Check environment variables
   - Verify table structure
   - Review Supabase logs

4. **Scheduler Not Running**
   - Check PID file: `scheduler.pid`
   - Review logs: `cryptoverse_scheduler.log`
   - Verify no other instance running

### Manual Recovery

Force immediate update:
```bash
python3 cryptoverse_72h_scheduler.py --force
```

Reset scheduler state:
```bash
rm scheduler_state.json
python3 cryptoverse_72h_scheduler.py --start
```

## 🚀 Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/cryptoverse-scheduler.service`:

```ini
[Unit]
Description=IntoTheCryptoverse Risk Data Scheduler
After=network.target

[Service]
Type=simple
User=zmartbot
WorkingDirectory=/path/to/zmart-api
ExecStart=/usr/bin/python3 /path/to/cryptoverse_72h_scheduler.py --run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cryptoverse-scheduler
sudo systemctl start cryptoverse-scheduler
sudo systemctl status cryptoverse-scheduler
```

### Docker Container

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .
COPY .env .

CMD ["python3", "cryptoverse_72h_scheduler.py", "--run"]
```

## 🎯 Success Criteria

### System is 100% Autonomous When:

✅ **Scheduler Running**: Status shows active
✅ **Last Run Success**: Within last 72 hours
✅ **Success Rate > 90%**: Most symbols updating
✅ **Supabase Verified**: 41 points per symbol
✅ **No Manual Intervention**: 30+ days uptime

## 📊 Monitoring Dashboard

Check system health:
```bash
python3 check_system_health.py
```

Output:
```
🎯 CRYPTOVERSE AUTOMATION STATUS
================================
Scheduler: ✅ Running (PID: 12345)
Last Run: 2025-09-15 14:30:00
Next Run: 2025-09-18 14:30:00
Success Rate: 96% (24/25 symbols)
Supabase: ✅ Synced
Uptime: 15 days
```

## 🔐 Security Notes

1. **API Keys**: Store in `.env`, never commit
2. **Login Session**: Keep browser logged in
3. **Rate Limiting**: 2-second delay between symbols
4. **Error Logs**: Review regularly for issues

## 📞 Support

For issues or questions:
1. Check logs in `cryptoverse_scheduler.log`
2. Review reports in `risk_grid_validation/`
3. Verify MCP Browser connection
4. Ensure Supabase credentials are valid

---

## ✅ Final Checklist

Before considering the system autonomous:

- [ ] MCP Browser installed and configured
- [ ] Logged in to IntoTheCryptoverse
- [ ] Environment variables set (.env file)
- [ ] Test scrape successful
- [ ] Test sync successful
- [ ] Scheduler started as daemon
- [ ] First automated run completed
- [ ] Monitoring shows 100% success

Once all items are checked, the system will run autonomously every 72 hours! 🚀

---

**Version**: 1.0.0
**Last Updated**: 2025-09-17
**Status**: PRODUCTION READY