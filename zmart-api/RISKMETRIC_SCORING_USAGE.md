# RiskMetric Scoring System - Usage Guide

## 🎯 Quick Start

### Step 1: Run the Scoring System Setup
```sql
-- Run in Supabase SQL Editor
-- File: riskmetric_scoring_system.sql
```

### Step 2: Initialize All Scores
```sql
SELECT update_all_riskmetric_scores();
```

### Step 3: View Top Opportunities
```sql
SELECT * FROM v_top_trading_opportunities;
```

## 📊 Understanding the Scores

### Base Score Ranges
- **100 points**: Extreme zones (Risk 0-0.15 or 0.85-1.0)
- **80 points**: Strong zones (Risk 0.15-0.25 or 0.75-0.85)
- **60 points**: Moderate zones (Risk 0.25-0.35 or 0.65-0.75)
- **50 points**: Neutral zone (Risk 0.35-0.65)

### Total Score Calculation
```
Total Score = Base Score × Coefficient
```
- Coefficient ranges from 1.00 (most common) to 1.60 (rarest)
- Higher coefficients = Rarer market conditions = Higher confidence

### Signal Strength Thresholds
- **STRONGEST**: Total Score ≥ 150
- **STRONG**: Total Score ≥ 120
- **MODERATE**: Total Score ≥ 90
- **WEAK**: Total Score < 90

## 🚨 Trading Signals

### BUY Signals (Risk < 0.35)
- 🔥🔥🔥 **STRONGEST BUY**: Extreme oversold + Very rare (Score ≥ 150)
- 🔥🔥 **STRONG BUY**: Oversold + Rare (Score ≥ 120)
- ✅ **BUY**: Good accumulation (Score ≥ 90)
- 💰 **ACCUMULATE**: Standard buy zone

### SELL Signals (Risk > 0.65)
- ⚠️⚠️⚠️ **STRONGEST SELL**: Extreme overbought + Very rare (Score ≥ 150)
- ⚠️⚠️ **STRONG SELL**: Overbought + Rare (Score ≥ 120)
- 📉 **SELL**: Good distribution (Score ≥ 90)
- 💸 **TAKE PROFIT**: Standard sell zone

### NEUTRAL Signals (Risk 0.35-0.65)
- ⏸️ **HOLD**: Wait for better entry/exit
- 👀 **MONITOR**: Weak signal, observe

## 💻 Common Queries

### 1. Get Current Scores for Specific Symbols
```sql
SELECT
    symbol,
    current_risk,
    base_score,
    coefficient,
    total_score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE symbol IN ('BTC', 'ETH', 'SOL')
ORDER BY total_score DESC;
```

### 2. Find Strongest Buy Opportunities
```sql
SELECT * FROM v_strongest_buy_signals;
```

### 3. Find Strongest Sell Opportunities
```sql
SELECT * FROM v_strongest_sell_signals;
```

### 4. Check Rare Market Conditions
```sql
SELECT * FROM v_rare_market_conditions;
```

### 5. Get Trading Alerts
```sql
SELECT * FROM v_trading_alerts;
```

### 6. Calculate Score for Custom Risk
```sql
-- Example: What would be the score for SOL at risk 0.2?
SELECT * FROM calculate_riskmetric_score('SOL', 0.2, 1.45);
```

### 7. Get Price Targets
```sql
SELECT * FROM v_price_targets
WHERE symbol = 'SOL';
```

## 🔄 Automation

### Daily Updates (Midnight UTC)
The system automatically:
1. Updates risk bands (+1 day to current band)
2. Recalculates all coefficients
3. Updates all scores
4. Generates new signals

### Hourly Updates
The system fetches Binance prices and:
1. Calculates current risk values
2. Updates scores if risk changes
3. Triggers alerts for significant changes

### Manual Update
```sql
-- Force update all scores
SELECT update_all_riskmetric_scores();

-- Update specific symbol
SELECT calculate_riskmetric_score('BTC',
    (SELECT current_risk FROM cryptoverse_risk_time_bands_v2 WHERE symbol = 'BTC'),
    (SELECT coef_70_80 FROM cryptoverse_risk_time_bands_v2 WHERE symbol = 'BTC')
);
```

## 📈 Monitoring

### Quick Dashboard
```sql
SELECT * FROM get_trading_summary();
```

### Full Dashboard
```sql
-- Market Overview
SELECT * FROM v_riskmetric_dashboard;

-- Top Opportunities
SELECT * FROM v_top_trading_opportunities;

-- Active Alerts
SELECT * FROM v_trading_alerts;
```

### Performance Check
```sql
-- Run validation tests
SELECT * FROM validate_risk_calculations();

-- Check scoring accuracy
SELECT * FROM test_scoring_system.sql;
```

## 🎯 Trading Strategy Examples

### Conservative Strategy
Only trade on STRONGEST signals (Score ≥ 150):
```sql
SELECT * FROM v_riskmetric_scores
WHERE signal_strength = 'STRONGEST'
ORDER BY total_score DESC;
```

### Moderate Strategy
Trade on STRONG and STRONGEST signals (Score ≥ 120):
```sql
SELECT * FROM v_riskmetric_scores
WHERE signal_strength IN ('STRONGEST', 'STRONG')
ORDER BY total_score DESC;
```

### Active Strategy
Include MODERATE signals (Score ≥ 90):
```sql
SELECT * FROM v_riskmetric_scores
WHERE signal_strength IN ('STRONGEST', 'STRONG', 'MODERATE')
AND signal_type != 'NEUTRAL'
ORDER BY total_score DESC;
```

### Rare Conditions Strategy
Focus on rare market conditions (Coefficient ≥ 1.45):
```sql
SELECT * FROM v_rare_market_conditions
WHERE coefficient >= 1.45
ORDER BY total_score DESC;
```

## 🔍 Troubleshooting

### Check If Scores Are Updating
```sql
SELECT
    symbol,
    last_score_update,
    CASE
        WHEN last_score_update > NOW() - INTERVAL '1 hour' THEN '✅ Recent'
        WHEN last_score_update > NOW() - INTERVAL '1 day' THEN '⚠️ Stale'
        ELSE '❌ Old'
    END as status
FROM cryptoverse_risk_time_bands_v2
LIMIT 10;
```

### Verify Coefficient Calculations
```sql
SELECT
    symbol,
    band_50_60 as most_common_days,
    coef_50_60 as should_be_1,
    band_90_100 as rarest_days,
    coef_90_100 as should_be_near_160
FROM cryptoverse_risk_time_bands_v2
WHERE symbol = 'SOL';
```

### Force Recalculation
```sql
-- Recalculate all coefficients
SELECT recalculate_trading_coefficients();

-- Update all scores
SELECT update_all_riskmetric_scores();
```

## 📊 Example Output

### Top Trading Opportunity
```
Symbol: SOL
Risk: 0.715
Band: 0.7-0.8
Base Score: 60
Coefficient: 1.450
Total Score: 87.0
Signal: SHORT
Strength: WEAK
Action: 👀 MONITOR
```

### Strongest Signal Example
```
Symbol: RENDER
Risk: 0.900
Band: 0.9-1.0
Base Score: 100
Coefficient: 1.580
Total Score: 158.0
Signal: SHORT
Strength: STRONGEST
Action: ⚠️⚠️⚠️ STRONGEST SELL
```

## 🚀 Best Practices

1. **Check coefficient values** - Higher coefficients indicate rarer conditions
2. **Monitor score changes** - Significant jumps may indicate trend changes
3. **Combine with other indicators** - Use scores as one input in your strategy
4. **Set alerts** - Monitor for scores crossing key thresholds (90, 120, 150)
5. **Review daily** - Check morning dashboard for overnight changes
6. **Validate weekly** - Run validation tests to ensure accuracy

## 📝 Notes

- Scores update automatically but can be manually refreshed
- Historical data improves coefficient accuracy over time
- Extreme scores (>150) are rare and should be acted upon quickly
- System is self-healing and continues if API failures occur
- All times are in UTC

---

**Last Updated**: 2025-09-16
**Version**: 2.0.0
**Status**: PRODUCTION READY