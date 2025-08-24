# KINGFISHER AUTOMATION SYSTEM - COMPLETE DOCUMENTATION

## Overview
Complete 6-step automation pipeline for processing KingFisher trading images from Telegram, updating Airtable with liquidation clusters, and generating professional trading reports with win rate analysis.

## Completed Steps

### STEP 1: Monitor & Download Telegram Images
**Script:** `STEP1-Monitoring-Images-And-download.py`
- Monitors @thekingfisher_liqmap_bot Telegram channel
- Downloads ALL images automatically
- Numbers images sequentially (1.jpg, 2.jpg, etc.)
- Saves to `downloads/` folder

### STEP 2: Sort Images with AI
**Script:** `STEP2-Sort-Images-With-AI.py`
- Uses OCR and ChatGPT to categorize images
- Sorts into 4 folders:
  - LiquidationMap
  - LiquidationHeatmap  
  - ShortTermRatio (OPTICAL_OPTI)
  - LongTermRatio (ALL_LEVERAGE)

### STEP 3: Remove Duplicates
**Script:** `STEP3-Remove-Duplicates.py`
- Uses MD5 hashing to detect duplicates
- Removes duplicate images from all folders
- Keeps only unique images for analysis

### STEP 4: Analyze & Create Professional Reports
**Script:** `STEP4-Analyze-And-Create-Reports.py`
- Uses ChatGPT Vision (GPT-4o) for analysis
- Creates institutional-grade MD reports
- 4000-token comprehensive analysis
- Moves analyzed images to `imagesanalysed/`
- Saves reports to `mdfiles/`

### STEP 5: Extract Liquidation Clusters & Update Airtable
**Script:** `STEP5-Extract-Liquidation-Clusters.py`
- Processes latest MD file from Step 4
- Extracts liquidation cluster prices
- Enforces 2% minimum distance from current price
- Updates Airtable with 4 clusters (2 below, 2 above)
- Moves processed files to `HistoryData/`

**Enhanced Version:** `STEP5-Extract-Liquidation-Clusters-Enhanced.py`
- Direct image analysis with ChatGPT for maximum accuracy
- Same functionality but analyzes original image

### STEP 6: Generate Professional Trading Reports
**Script:** `STEP6-Generate-Professional-Reports.py` / `STEP6-Enhanced-Professional-Reports.py`
- Fetches all data from Airtable (LiquidationMap, Heatmap, Ratios)
- Generates comprehensive Manus-style professional reports
- Extracts win rates for 24h, 7d, and 1m timeframes
- Calculates SCORE as max(24h_long%, 24h_short%) 
- Updates Airtable fields:
  - WinRate_24h: "82% Long/18% Short"
  - WinRate_7d: "65% Long/35% Short" 
  - WinRate_1m: "54% Long/46% Short"
  - Score: 82 (the max value from 24h rates)
- Saves reports in organized date-based folder structure
- Creates MD Reports folder with daily subfolders
- Moves reports to HistoryData for archival

## Running the System

### One-Time Execution
```bash
# Run individual steps
python STEP1-Monitoring-Images-And-download.py
python STEP2-Sort-Images-With-AI.py
python STEP3-Remove-Duplicates.py
python STEP4-Analyze-And-Create-Reports.py
python STEP5-Extract-Liquidation-Clusters.py --once
python STEP6-Enhanced-Professional-Reports.py
```

### Continuous Monitoring (Every 5 Minutes)
```bash
# Option 1: Shell script
./START_CONTINUOUS_MONITORING.sh

# Option 2: Python orchestrator
python RUN_ALL_STEPS_CONTINUOUS.py

# Option 3: Just STEP5 continuous
python STEP5-Extract-Liquidation-Clusters.py
```

## Environment Variables Required (.env)
```
# Telegram API
TELEGRAM_API_ID=26706005
TELEGRAM_API_HASH=bab8e720fd3b045785a5ec44d5e399fe

# Airtable
AIRTABLE_API_KEY=patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835
AIRTABLE_BASE_ID=appAs9sZH7OmtYaTJ
AIRTABLE_TABLE_NAME=KingFisher

# OpenAI (for ChatGPT analysis)
OPENAI_API_KEY=your_key_here
```

## Airtable Fields Updated
- **Symbol**: Cryptocurrency symbol (BTC, ETH, etc.)
- **CurrentPrice**: Current market price
- **Liqcluster-2**: 2nd liquidation level below price (>2% away)
- **Liqcluster-1**: 1st liquidation level below price (>2% away)
- **Liqcluster+1**: 1st liquidation level above price (>2% away)
- **Liqcluster+2**: 2nd liquidation level above price (>2% away)
- **LiquidationMap**: Full analysis of liquidation map image
- **LiquidationHeatmap**: Full analysis of liquidation heatmap image
- **ShortTermRatio**: OPTICAL/OPTI ratio analysis
- **LongTermRatio**: ALL_LEVERAGE ratio analysis
- **WinRate_24h**: 24-hour win rate (e.g., "82% Long/18% Short")
- **WinRate_7d**: 7-day win rate projection (e.g., "65% Long/35% Short")
- **WinRate_1m**: 1-month win rate projection (e.g., "54% Long/46% Short")
- **Score**: Max value between long and short 24h rates (e.g., 82)
- **ReportGenerated**: Timestamp of report generation
- **LastUpdated**: Timestamp of last update

## Key Features
- ✅ Fully automated Telegram monitoring
- ✅ AI-powered image categorization
- ✅ Professional report generation with Manus-style analysis
- ✅ Win rate extraction and calculation for multiple timeframes
- ✅ Automated Airtable updates with formatted win rates
- ✅ Organized report storage with date-based folders
- ✅ Duplicate detection and removal
- ✅ Professional institutional-grade analysis
- ✅ Accurate liquidation cluster extraction
- ✅ 2% minimum distance rule enforcement
- ✅ Automatic Airtable updates
- ✅ 5-minute update intervals
- ✅ Historical data archiving

## Next Steps (STEP 6 - To Be Implemented)
Potential enhancements for Step 6:
- Real-time alerting when critical clusters are approached
- Multi-symbol tracking dashboard
- Risk metrics calculation based on clusters
- Integration with trading systems
- Historical cluster analysis and patterns

## Status
**✅ STEPS 1-5 COMPLETE AND OPERATIONAL**
- All scripts tested and working
- Airtable integration confirmed
- Continuous monitoring available
- Ready for production use

---
*Last Updated: August 8, 2025*
*System ready for 24/7 automated operation*