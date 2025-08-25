# 👑 KINGFISHER LIBRARY - MASTER GUIDE

## Overview
The Kingfisher Library is a complete, self-learning trading automation system with a 6-step pipeline for processing trading signals from Telegram images to professional reports with win rate analysis.

## ✅ Clean Library Structure

```
ZmartBot/
├── King-Scripts/                          # Main Production Scripts
│   ├── KING_ORCHESTRATION_AGENT_SELF_LEARNING.py  # Self-learning orchestrator
│   ├── STEP1-Monitoring-Images-And-download.py    # Telegram monitor
│   ├── STEP2-Sort-Images-With-AI.py              # AI image sorting
│   ├── STEP3-Remove-Duplicates.py                # Duplicate removal
│   ├── STEP4-Analyze-And-Create-Reports.py       # Image analysis
│   ├── STEP5-Extract-Liquidation-Clusters.py     # Cluster extraction
│   ├── STEP6-Enhanced-Professional-Reports.py    # Report generation
│   ├── ml_orchestrator_dashboard.html            # ML Dashboard
│   └── start_ml_orchestrator.sh                  # Start script
│
├── KingfisherLibrary/                    # Clean Library Package
│   ├── __init__.py                       # Package initialization
│   ├── main.py                           # Main entry point
│   ├── config/                           # Configuration
│   │   ├── __init__.py
│   │   └── settings.py                   # Centralized settings
│   ├── orchestration/                    # Orchestration engine
│   │   └── self_learning_orchestrator.py
│   ├── learning/                         # ML components
│   │   └── learning_module.py
│   └── api/                             # API endpoints
│       └── kingfisher_api.py
│
└── backend/
    └── archive_old_versions/             # Archived conflicting files

```

## 🚀 Quick Start

### Method 1: Using Self-Learning Orchestrator (Recommended)
```bash
# Navigate to King-Scripts
cd King-Scripts

# Start the self-learning orchestrator
./start_ml_orchestrator.sh

# Or directly with Python
python KING_ORCHESTRATION_AGENT_SELF_LEARNING.py
```

### Method 2: Using KingfisherLibrary Package
```bash
# Navigate to library
cd KingfisherLibrary

# Run with default settings
python main.py

# Run without ML
python main.py --no-ml

# Run with custom config
python main.py --config custom_config.json
```

## 📊 System Components

### 1. **Self-Learning Orchestration Engine**
- **Pattern Recognition**: Learns optimal execution times
- **Adaptive Scheduling**: Adjusts timing based on performance
- **Anomaly Detection**: Identifies unusual conditions
- **Performance Optimization**: Improves with each execution

### 2. **6-Step Processing Pipeline**

| Step | Component | Description | Trigger |
|------|-----------|-------------|---------|
| 1 | Image Monitor | Downloads Telegram images | Empty folder or 5 min timer |
| 2 | AI Sorter | Sorts images by type | New unsorted images |
| 3 | Duplicate Remover | Removes duplicate images | Multiple images in folders |
| 4 | Analyzer | Creates analysis reports | Unanalyzed images exist |
| 5 | Cluster Extractor | Extracts liquidation levels | New MD files created |
| 6 | Report Generator | Professional reports with win rates | Data updated or 30 min timer |

### 3. **Machine Learning Features**
- **Success Rate Tracking**: Monitors performance per step
- **Execution Time Prediction**: Estimates duration
- **Confidence Scoring**: ML-based execution confidence
- **Pattern Identification**: Time and sequence patterns
- **Continuous Learning**: Updates models every 10 executions

## 🌐 API Endpoints

**Base URL**: `http://localhost:5555`

### Core Endpoints
- `GET /health` - System health check
- `GET /status` - Current status of all steps
- `POST /trigger/<step>` - Manually trigger a step
- `GET /data/<symbol>` - Get symbol data from Airtable
- `GET /reports/<symbol>` - Get latest report

### ML Endpoints
- `GET /ml/patterns` - View learned patterns
- `GET /ml/suggestions/<step>` - Get ML suggestions
- `GET /ml/metrics` - View learning metrics
- `POST /ml/toggle` - Enable/disable ML optimization

## 📈 Dashboard Access

### ML Dashboard
Open `King-Scripts/ml_orchestrator_dashboard.html` in browser

Features:
- Real-time status monitoring
- ML metrics and performance charts
- Pattern visualization
- Prediction timeline
- Manual controls

## 🔧 Configuration

### Environment Variables (.env)
```env
# Telegram
TELEGRAM_API_ID=26706005
TELEGRAM_API_HASH=your_hash

# Airtable
AIRTABLE_API_KEY=your_key
AIRTABLE_BASE_ID=appAs9sZH7OmtYaTJ
AIRTABLE_TABLE_NAME=KingFisher

# OpenAI
OPENAI_API_KEY=your_key
```

### Custom Configuration (optional)
Create `config.json`:
```json
{
  "ML_ENABLED": true,
  "LEARNING_RATE": 0.1,
  "EXPLORATION_RATE": 0.2,
  "CONFIDENCE_THRESHOLD": 0.75,
  "MONITOR_INTERVAL": 10,
  "API_PORT": 5555
}
```

## 📊 Data Flow

```
Telegram Images → Download → Sort → Remove Duplicates → Analyze 
    ↓
Airtable ← Win Rates ← Professional Reports ← Extract Clusters
```

## 🎯 Key Features

### Automated Processing
- ✅ Trigger-based execution
- ✅ Dependency management
- ✅ Error recovery
- ✅ Rate limiting

### Self-Learning
- ✅ Pattern recognition
- ✅ Performance optimization
- ✅ Adaptive scheduling
- ✅ Predictive triggering

### Professional Output
- ✅ Manus-style reports
- ✅ Win rate analysis (24h/7d/1m)
- ✅ Score calculation
- ✅ Organized storage

## 🛠️ Troubleshooting

### Common Issues

1. **Orchestrator won't start**
```bash
# Check if port 5555 is in use
lsof -i :5555
# Kill if needed
kill -9 <PID>
```

2. **ML models not updating**
```bash
# Check learning data
ls learning_data/models/
# Force model update (requires 10+ executions)
```

3. **Steps not triggering**
```bash
# Check status via API
curl http://localhost:5555/status
# Manually trigger
curl -X POST http://localhost:5555/trigger/1
```

## 📈 Performance Metrics

The system tracks:
- **Success Rates**: Per step success percentage
- **Execution Times**: Average duration per step
- **Confidence Scores**: ML confidence for triggers
- **Pattern Frequency**: Common execution patterns
- **Improvement Rate**: Performance over time

## 🔒 Security Notes

- API keys stored in environment variables
- No hardcoded credentials in code
- Rate limiting on external APIs
- Secure Airtable integration
- Input validation on all endpoints

## 📚 Advanced Usage

### Custom Step Scripts
Place custom scripts in King-Scripts/ and update configuration:
```python
STEP_SCRIPTS[7] = "STEP7-CustomProcess.py"
```

### Extending ML Features
Add custom patterns in learning module:
```python
self.learning_module.add_pattern_detector(custom_detector)
```

### API Integration
```python
import requests

# Get status
response = requests.get("http://localhost:5555/status")
data = response.json()

# Trigger step
requests.post("http://localhost:5555/trigger/1")
```

## 🔄 System Maintenance

### Daily
- Check execution history for failures
- Review ML suggestions
- Monitor success rates

### Weekly
- Clean old images in HistoryData/
- Review learned patterns
- Optimize based on ML insights

### Monthly
- Backup learning_data/
- Update dependencies
- Review and tune ML parameters

## 📞 Support

- **Logs**: Check `kingfisher.log`
- **ML Database**: `learning_data/metrics.db`
- **Dashboard**: Real-time monitoring
- **API Docs**: http://localhost:5555/docs

## 🎉 Conclusion

The Kingfisher Library provides a complete, self-learning trading automation system that:
- **Learns** from every execution
- **Improves** performance over time
- **Adapts** to changing patterns
- **Automates** the entire pipeline
- **Provides** professional analysis

The system is now clean, conflict-free, and ready for production use!

---
**Version**: 2.0.0  
**Last Updated**: August 2025  
**Status**: Production Ready