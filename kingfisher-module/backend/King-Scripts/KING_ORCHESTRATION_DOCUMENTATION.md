# 👑 KING ORCHESTRATION AGENT - COMPLETE DOCUMENTATION

## Overview
The King Orchestration Agent is an intelligent automation system that orchestrates all 6 KingFisher processing steps based on trigger conditions, ensuring data is always up-to-date and providing easy API access to all processed information.

## Architecture

### Core Components
1. **Trigger Monitor** - Continuously monitors for step execution triggers
2. **Step Executor** - Manages sequential execution of processing steps
3. **File Watcher** - Monitors downloads folder for new images
4. **API Server** - Provides RESTful endpoints for data access
5. **Status Tracker** - Maintains execution history and step status

### Step Dependencies & Triggers

| Step | Description | Dependencies | Trigger Conditions |
|------|-------------|--------------|-------------------|
| **Step 1** | Monitor & Download Images | None | - Downloads folder empty<br>- 5 minutes since last run<br>- Manual trigger |
| **Step 2** | Sort Images with AI | Step 1 | - Unsorted images exist in downloads<br>- New images detected |
| **Step 3** | Remove Duplicates | Step 2 | - Multiple images in sorted folders<br>- Potential duplicates detected |
| **Step 4** | Analyze & Create Reports | Step 3 | - Unanalyzed images exist<br>- Images not in analyzed folder |
| **Step 5** | Extract Liquidation Clusters | Step 4 | - New MD files created<br>- Unprocessed reports exist |
| **Step 6** | Generate Professional Reports | Step 5 | - Airtable data updated<br>- 30 minutes since last generation |

## Installation & Setup

### Prerequisites
```bash
# Python 3.8+ required
python3 --version

# Install required packages
pip install flask flask-cors python-dotenv aiohttp watchdog
```

### Environment Variables
Ensure `.env` file contains:
```env
# Telegram API
TELEGRAM_API_ID=26706005
TELEGRAM_API_HASH=bab8e720fd3b045785a5ec44d5e399fe

# Airtable
AIRTABLE_API_KEY=patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835
AIRTABLE_BASE_ID=appAs9sZH7OmtYaTJ
AIRTABLE_TABLE_NAME=KingFisher

# OpenAI
OPENAI_API_KEY=your_key_here
```

## Starting the Orchestrator

### Method 1: Using Start Script
```bash
cd kingfisher-module/backend/King-Scripts
./start_orchestrator.sh
```

### Method 2: Direct Python Execution
```bash
cd kingfisher-module/backend/King-Scripts
python3 KING_ORCHESTRATION_AGENT.py
```

### Method 3: As a System Service
```bash
# Create systemd service (Linux)
sudo nano /etc/systemd/system/king-orchestrator.service

[Unit]
Description=King Orchestration Agent
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/King-Scripts
ExecStart=/usr/bin/python3 /path/to/KING_ORCHESTRATION_AGENT.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable king-orchestrator
sudo systemctl start king-orchestrator
```

## API Endpoints

### Base URL
```
http://localhost:5555
```

### Available Endpoints

#### 1. Health Check
```http
GET /health
```
Response:
```json
{
  "status": "healthy",
  "service": "King Orchestration Agent",
  "timestamp": "2025-08-09T10:30:00"
}
```

#### 2. System Status
```http
GET /status
```
Response:
```json
{
  "steps": {
    "step_1": {
      "status": "completed",
      "last_execution": "2025-08-09T10:25:00",
      "script": "STEP1-Monitoring-Images-And-download.py"
    },
    ...
  },
  "is_running": true,
  "history_count": 42
}
```

#### 3. Manual Trigger
```http
POST /trigger/{step_number}
```
Example:
```bash
curl -X POST http://localhost:5555/trigger/1
```

#### 4. Get Symbol Data
```http
GET /data/{symbol}
```
Example:
```bash
curl http://localhost:5555/data/BTC
```
Response:
```json
{
  "Symbol": "BTC",
  "CurrentPrice": 114222.00,
  "Score": 86,
  "WinRate_24h": "86% Long/14% Short",
  "WinRate_7d": "65% Long/35% Short",
  "WinRate_1m": "54% Long/46% Short",
  "Liqcluster-2": 110000,
  "Liqcluster-1": 112000,
  "Liqcluster+1": 116000,
  "Liqcluster+2": 118000
}
```

#### 5. Get Symbol Report
```http
GET /reports/{symbol}
```
Returns the latest professional report for the symbol.

#### 6. Execution History
```http
GET /history
```
Returns last 100 execution records.

#### 7. Restart System
```http
POST /restart
```
Resets all steps to IDLE state.

## Monitoring Dashboard

### Access the Dashboard
Open `orchestrator_dashboard.html` in a web browser or serve it:
```bash
python3 -m http.server 8000
# Then open: http://localhost:8000/orchestrator_dashboard.html
```

### Dashboard Features
- **Real-time Status** - Updates every 5 seconds
- **Manual Triggers** - Execute any step on demand
- **Symbol Data Viewer** - Query data for any symbol
- **Report Viewer** - Display professional reports
- **System Controls** - Restart orchestration system

## Workflow Automation Logic

### Trigger Detection Flow
```
1. Initial State Check
   ├── Downloads folder empty?
   │   └── Yes → Wait for first image
   └── No → Process existing images

2. Continuous Monitoring (every 10 seconds)
   ├── Check Step 1: New Telegram images?
   ├── Check Step 2: Unsorted images exist?
   ├── Check Step 3: Duplicates to remove?
   ├── Check Step 4: Images to analyze?
   ├── Check Step 5: MD files to process?
   └── Check Step 6: Time to generate reports?

3. Execution Chain
   Step triggered → Check dependencies → Execute → Trigger next step
```

### Smart Features
1. **Dependency Management** - Steps only run when dependencies are met
2. **Auto-Recovery** - Failed steps can be retried
3. **Rate Limiting** - Prevents API overload
4. **State Persistence** - Tracks execution history
5. **Parallel Safety** - Prevents concurrent execution of same step

## Troubleshooting

### Common Issues

#### 1. Orchestrator Won't Start
```bash
# Check if port 5555 is in use
lsof -i :5555

# Kill existing process if needed
kill -9 <PID>
```

#### 2. Steps Not Triggering
```bash
# Check step status via API
curl http://localhost:5555/status

# Manually trigger step
curl -X POST http://localhost:5555/trigger/1
```

#### 3. File Monitoring Not Working
```bash
# Check downloads folder permissions
ls -la downloads/

# Verify watchdog is installed
pip install watchdog
```

#### 4. API Connection Failed
```bash
# Check if orchestrator is running
ps aux | grep KING_ORCHESTRATION

# Check logs
tail -f king_orchestrator.log
```

## Performance Optimization

### Recommended Settings
- **Monitor Interval**: 10 seconds (configurable)
- **Step Timeout**: 5 minutes per step
- **API Rate Limit**: 100 requests/minute
- **File Watch Buffer**: 1000 events

### Scaling Considerations
- Use Redis for queue management in production
- Implement distributed locking for multi-instance setup
- Consider message queue (RabbitMQ/Kafka) for high volume

## Security Considerations

1. **API Authentication** - Add JWT tokens for production
2. **HTTPS** - Use SSL certificates for API endpoints
3. **Rate Limiting** - Implement per-IP rate limiting
4. **Input Validation** - Sanitize all user inputs
5. **Secrets Management** - Use environment variables or vault

## Integration Examples

### Python Client
```python
import requests

class KingOrchestratorClient:
    def __init__(self, base_url="http://localhost:5555"):
        self.base_url = base_url
    
    def get_status(self):
        return requests.get(f"{self.base_url}/status").json()
    
    def trigger_step(self, step_num):
        return requests.post(f"{self.base_url}/trigger/{step_num}").json()
    
    def get_symbol_data(self, symbol):
        return requests.get(f"{self.base_url}/data/{symbol}").json()

# Usage
client = KingOrchestratorClient()
status = client.get_status()
data = client.get_symbol_data("BTC")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

class KingOrchestrator {
    constructor(baseUrl = 'http://localhost:5555') {
        this.baseUrl = baseUrl;
    }
    
    async getSymbolData(symbol) {
        const response = await axios.get(`${this.baseUrl}/data/${symbol}`);
        return response.data;
    }
    
    async triggerStep(stepNum) {
        const response = await axios.post(`${this.baseUrl}/trigger/${stepNum}`);
        return response.data;
    }
}
```

## Maintenance

### Daily Tasks
- Check execution history for failures
- Verify all steps completed successfully
- Monitor disk space for image storage

### Weekly Tasks
- Clean up old images in HistoryData
- Review error logs
- Update Airtable field mappings if needed

### Monthly Tasks
- Backup configuration and scripts
- Update dependencies
- Performance optimization review

## Support & Updates

### Log Files
```bash
# View orchestrator logs
tail -f ~/.king_orchestrator/orchestrator.log

# Check step execution logs
ls -la King-Scripts/logs/
```

### Version History
- **v1.0** - Initial release with 6-step automation
- **v1.1** - Added API endpoints and dashboard
- **v1.2** - Improved trigger detection logic

### Future Enhancements
- [ ] WebSocket support for real-time updates
- [ ] Multi-symbol parallel processing
- [ ] Machine learning for trigger prediction
- [ ] Cloud deployment support
- [ ] Mobile app integration

---

**Created by**: King Orchestration System  
**Version**: 1.0  
**Last Updated**: August 9, 2025