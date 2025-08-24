# Score Tracking System - Complete Implementation

## 📊 Overview

The Score Tracking System is a comprehensive database solution for tracking **Base Score** and **Total Score** (with coefficient applied) for all cryptocurrency symbols on a daily basis. This system provides powerful analytics and insights into how the RiskMetric scoring methodology performs over time.

## 🎯 Key Features

### **Two Distinct Score Types Tracked:**

1. **Base Score**: Raw score before coefficient application (40-100 points)
   - Based on risk value and rarity analysis
   - Dynamic adjustments for band proximity
   - Historical rarity factor calculations

2. **Total Score**: Final score after coefficient application (0-100 points)
   - Base Score × Coefficient (1.0-1.6 range)
   - Represents the final trading signal strength
   - Used for position sizing and risk management

## 🏗️ System Architecture

### **Database Models:**

#### **ScoreTracking Table**
```sql
CREATE TABLE score_tracking (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    tracking_date TIMESTAMP NOT NULL,
    current_price FLOAT NOT NULL,
    risk_value FLOAT NOT NULL,
    risk_band VARCHAR(20) NOT NULL,
    base_score FLOAT NOT NULL,
    base_score_components TEXT,
    coefficient_value FLOAT NOT NULL,
    coefficient_calculation TEXT,
    total_score FLOAT NOT NULL,
    risk_bands_data TEXT,
    current_band_rank INTEGER,
    rarity_factor FLOAT,
    proximity_bonus FLOAT,
    life_age_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **ScoreAnalytics Table**
```sql
CREATE TABLE score_analytics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    period_type VARCHAR(20) NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    avg_base_score FLOAT NOT NULL,
    avg_total_score FLOAT NOT NULL,
    min_base_score FLOAT NOT NULL,
    max_base_score FLOAT NOT NULL,
    min_total_score FLOAT NOT NULL,
    max_total_score FLOAT NOT NULL,
    avg_coefficient FLOAT NOT NULL,
    min_coefficient FLOAT NOT NULL,
    max_coefficient FLOAT NOT NULL,
    risk_band_distribution TEXT,
    base_total_correlation FLOAT,
    coefficient_impact FLOAT,
    data_points_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Implementation Components

### **1. Score Tracking Service** (`src/services/score_tracking_service.py`)

**Core Functions:**
- `record_daily_score()`: Records daily score data
- `get_score_history()`: Retrieves historical data
- `get_score_analytics()`: Calculates comprehensive analytics
- `get_comparative_analysis()`: Compares multiple symbols

**Analytics Features:**
- Statistical analysis (mean, median, min, max, std)
- Correlation analysis between Base and Total scores
- Trend analysis over time
- Volatility calculations
- Risk band distribution analysis

### **2. API Routes** (`src/routes/score_tracking_routes.py`)

**Available Endpoints:**
- `POST /api/v1/score-tracking/record`: Record daily score
- `GET /api/v1/score-tracking/history/{symbol}`: Get score history
- `GET /api/v1/score-tracking/analytics/{symbol}`: Get analytics
- `GET /api/v1/score-tracking/comparative`: Compare symbols
- `GET /api/v1/score-tracking/summary`: Get system summary

### **3. Daily Score Tracker** (`daily_score_tracker.py`)

**Automated Features:**
- Fetches current prices from Binance API
- Calculates risk values using polynomial formula
- Determines risk bands and rarity factors
- Calculates Base Score with dynamic adjustments
- Applies coefficient calculations
- Records all data to database

## 📈 Base Score Calculation Methodology

### **Score Ranges by Risk Zone:**

```python
# Risk 0.0-0.25: 70-100 points (Premium zones)
# Risk 0.25-0.40: 60-70 points (Transition zones)  
# Risk 0.40-0.60: 40-60 points (Neutral zone)
# Risk 0.60-0.75: 60-70 points (Transition zones)
# Risk 0.75-1.0: 70-100 points (Premium zones)
```

### **Dynamic Adjustments:**

1. **Rarity Factor**: 0-20 points based on band rarity
2. **Proximity Bonus**: 0-15 points based on neighboring bands
3. **Total Bonus**: Up to 35 additional points

### **Calculation Example:**
```python
# For BTC in 0.5-0.6 band (943 days, 17.23%):
# Base Range: 40-60 points (neutral zone)
# Rarity Factor: Based on rank among all bands
# Proximity Analysis: Check neighboring bands
# Final Score: Base + Rarity + Proximity bonuses
```

## 🔄 Daily Tracking Process

### **Automated Workflow:**

1. **Price Fetching**: Get current prices from Binance API
2. **Risk Calculation**: Apply polynomial formula
3. **Band Analysis**: Determine current risk band
4. **Rarity Analysis**: Calculate band rank and rarity factor
5. **Proximity Analysis**: Check neighboring bands
6. **Base Score**: Calculate with all adjustments
7. **Coefficient**: Apply ChatGPT-based coefficient
8. **Total Score**: Final calculation
9. **Database Storage**: Record all data

### **Cron Job Setup:**
```bash
# Add to crontab to run daily at 2 AM
0 2 * * * /path/to/zmart-api/run_daily_score_tracker.sh
```

## 📊 Analytics Capabilities

### **Individual Symbol Analysis:**
- Score trends over time
- Volatility analysis
- Risk band distribution
- Coefficient impact analysis
- Correlation between metrics

### **Comparative Analysis:**
- Cross-symbol performance comparison
- Ranking by score performance
- Stability analysis
- Market condition impact

### **System-Wide Insights:**
- Overall score distribution
- Coefficient effectiveness
- Market condition correlation
- Performance tracking

## 🎯 Use Cases

### **1. Performance Monitoring:**
- Track how Base Score vs Total Score perform
- Monitor coefficient effectiveness
- Identify optimal trading conditions

### **2. Strategy Validation:**
- Validate RiskMetric methodology
- Test coefficient calculations
- Measure trading signal accuracy

### **3. Risk Management:**
- Analyze score volatility
- Monitor risk band transitions
- Track position sizing effectiveness

### **4. Research & Development:**
- Test new scoring algorithms
- Validate coefficient methodologies
- Analyze market condition impacts

## 🚀 Getting Started

### **1. Database Setup:**
```bash
# Run database migrations
python -m alembic upgrade head
```

### **2. Manual Testing:**
```bash
# Run daily tracker manually
python daily_score_tracker.py
```

### **3. API Testing:**
```bash
# Test API endpoints
curl -X GET "http://localhost:3400/api/v1/score-tracking/history/BTC"
```

### **4. Automated Setup:**
```bash
# Make script executable
chmod +x run_daily_score_tracker.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /path/to/run_daily_score_tracker.sh
```

## 📈 Expected Data Growth

### **Daily Records:**
- 22 symbols × 1 record/day = 22 records/day
- 22 records/day × 365 days = 8,030 records/year

### **Storage Requirements:**
- ~2KB per record
- 8,030 records/year × 2KB = ~16MB/year
- 10 years = ~160MB total

## 🔍 Monitoring & Alerts

### **Log Files:**
- `daily_score_tracker.log`: Detailed execution logs
- Database logs: Query performance and errors
- API logs: Endpoint usage and errors

### **Key Metrics to Monitor:**
- Daily tracking success rate
- API response times
- Database performance
- Score calculation accuracy

## 🛠️ Future Enhancements

### **Planned Features:**
1. **Real-time Tracking**: Hourly score updates
2. **Advanced Analytics**: Machine learning insights
3. **Alert System**: Score threshold notifications
4. **Dashboard Integration**: Real-time score visualization
5. **Backtesting**: Historical strategy validation

### **Integration Points:**
- Trading bot integration
- Risk management system
- Portfolio management
- Performance reporting

## 📋 Maintenance

### **Regular Tasks:**
- Monitor daily tracking execution
- Review analytics accuracy
- Clean old data (if needed)
- Update coefficient calculations
- Validate score calculations

### **Troubleshooting:**
- Check log files for errors
- Verify API connectivity
- Validate database connections
- Test score calculations
- Monitor system resources

---

**This system provides the foundation for comprehensive score tracking and analysis, enabling data-driven insights into the RiskMetric methodology's performance over time.**
