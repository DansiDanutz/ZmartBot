-- RISK MONITORING DASHBOARD
-- =========================
-- Complete view of your autonomous risk tracking system

-- 1. CURRENT STATUS OVERVIEW
SELECT '📊 SYSTEM STATUS' as dashboard;
SELECT
    COUNT(DISTINCT symbol) as total_symbols,
    MAX(last_risk_update) as last_update,
    MIN(total_days) as min_life_days,
    MAX(total_days) as max_life_days,
    AVG(total_days)::INTEGER as avg_life_days
FROM cryptoverse_risk_time_bands_v2;

-- 2. TOP TRADING SIGNALS RIGHT NOW
SELECT '🎯 TOP TRADING OPPORTUNITIES' as signals;
SELECT
    rtb.symbol,
    rtb.current_risk as risk,
    rtb.current_risk_band as band,
    CASE rtb.current_risk_band
        WHEN '0.0-0.1' THEN rtb.coef_0_10
        WHEN '0.1-0.2' THEN rtb.coef_10_20
        WHEN '0.2-0.3' THEN rtb.coef_20_30
        WHEN '0.3-0.4' THEN rtb.coef_30_40
        WHEN '0.4-0.5' THEN rtb.coef_40_50
        WHEN '0.5-0.6' THEN rtb.coef_50_60
        WHEN '0.6-0.7' THEN rtb.coef_60_70
        WHEN '0.7-0.8' THEN rtb.coef_70_80
        WHEN '0.8-0.9' THEN rtb.coef_80_90
        WHEN '0.9-1.0' THEN rtb.coef_90_100
    END as coefficient,
    CASE
        -- Strong signals for rare bands
        WHEN rtb.current_risk < 0.2 AND CASE rtb.current_risk_band
            WHEN '0.0-0.1' THEN rtb.coef_0_10
            WHEN '0.1-0.2' THEN rtb.coef_10_20
            ELSE 1.0
        END >= 1.5 THEN '🔥🔥 STRONG BUY - RARE LOW!'

        WHEN rtb.current_risk > 0.8 AND CASE rtb.current_risk_band
            WHEN '0.8-0.9' THEN rtb.coef_80_90
            WHEN '0.9-1.0' THEN rtb.coef_90_100
            ELSE 1.0
        END >= 1.5 THEN '⚠️⚠️ STRONG SELL - RARE HIGH!'

        WHEN rtb.current_risk < 0.3 AND CASE rtb.current_risk_band
            WHEN '0.0-0.1' THEN rtb.coef_0_10
            WHEN '0.1-0.2' THEN rtb.coef_10_20
            WHEN '0.2-0.3' THEN rtb.coef_20_30
            ELSE 1.0
        END >= 1.3 THEN '✅ BUY - Accumulation'

        WHEN rtb.current_risk > 0.7 AND CASE rtb.current_risk_band
            WHEN '0.7-0.8' THEN rtb.coef_70_80
            WHEN '0.8-0.9' THEN rtb.coef_80_90
            WHEN '0.9-1.0' THEN rtb.coef_90_100
            ELSE 1.0
        END >= 1.3 THEN '📉 SELL - Distribution'

        WHEN rtb.current_risk < 0.3 THEN '💰 ACCUMULATE'
        WHEN rtb.current_risk > 0.7 THEN '💸 TAKE PROFIT'
        ELSE '⏸️ HOLD'
    END as signal
FROM cryptoverse_risk_time_bands_v2 rtb
WHERE rtb.current_risk IS NOT NULL
ORDER BY
    CASE
        WHEN rtb.current_risk < 0.2 THEN CASE rtb.current_risk_band
            WHEN '0.0-0.1' THEN rtb.coef_0_10
            WHEN '0.1-0.2' THEN rtb.coef_10_20
            ELSE 1.0
        END
        WHEN rtb.current_risk > 0.8 THEN CASE rtb.current_risk_band
            WHEN '0.8-0.9' THEN rtb.coef_80_90
            WHEN '0.9-1.0' THEN rtb.coef_90_100
            ELSE 1.0
        END
        ELSE 0
    END DESC
LIMIT 10;

-- 3. RAREST CURRENT POSITIONS (HIGH COEFFICIENT = HIGH OPPORTUNITY)
SELECT '🦄 RAREST POSITIONS' as rarity;
SELECT
    rtb.symbol,
    rtb.current_risk_band,
    CASE rtb.current_risk_band
        WHEN '0.0-0.1' THEN rtb.band_0_10
        WHEN '0.1-0.2' THEN rtb.band_10_20
        WHEN '0.2-0.3' THEN rtb.band_20_30
        WHEN '0.3-0.4' THEN rtb.band_30_40
        WHEN '0.4-0.5' THEN rtb.band_40_50
        WHEN '0.5-0.6' THEN rtb.band_50_60
        WHEN '0.6-0.7' THEN rtb.band_60_70
        WHEN '0.7-0.8' THEN rtb.band_70_80
        WHEN '0.8-0.9' THEN rtb.band_80_90
        WHEN '0.9-1.0' THEN rtb.band_90_100
    END as days_in_band,
    rtb.total_days,
    ROUND(100.0 * CASE rtb.current_risk_band
        WHEN '0.0-0.1' THEN rtb.band_0_10
        WHEN '0.1-0.2' THEN rtb.band_10_20
        WHEN '0.2-0.3' THEN rtb.band_20_30
        WHEN '0.3-0.4' THEN rtb.band_30_40
        WHEN '0.4-0.5' THEN rtb.band_40_50
        WHEN '0.5-0.6' THEN rtb.band_50_60
        WHEN '0.6-0.7' THEN rtb.band_60_70
        WHEN '0.7-0.8' THEN rtb.band_70_80
        WHEN '0.8-0.9' THEN rtb.band_80_90
        WHEN '0.9-1.0' THEN rtb.band_90_100
    END / NULLIF(rtb.total_days, 0), 2) as "% time here",
    CASE rtb.current_risk_band
        WHEN '0.0-0.1' THEN rtb.coef_0_10
        WHEN '0.1-0.2' THEN rtb.coef_10_20
        WHEN '0.2-0.3' THEN rtb.coef_20_30
        WHEN '0.3-0.4' THEN rtb.coef_30_40
        WHEN '0.4-0.5' THEN rtb.coef_40_50
        WHEN '0.5-0.6' THEN rtb.coef_50_60
        WHEN '0.6-0.7' THEN rtb.coef_60_70
        WHEN '0.7-0.8' THEN rtb.coef_70_80
        WHEN '0.8-0.9' THEN rtb.coef_80_90
        WHEN '0.9-1.0' THEN rtb.coef_90_100
    END as coefficient
FROM cryptoverse_risk_time_bands_v2 rtb
WHERE rtb.current_risk IS NOT NULL
ORDER BY coefficient DESC
LIMIT 10;

-- 4. TODAY'S UPDATES
SELECT '📅 TODAY''S ACTIVITY' as today;
SELECT
    h.symbol,
    h.risk_value,
    h.risk_band,
    h.price_usd,
    h.created_at
FROM risk_band_daily_history h
WHERE h.date = CURRENT_DATE
ORDER BY h.created_at DESC;

-- 5. COEFFICIENT CHANGES (Shows how patterns evolve)
SELECT '📈 COEFFICIENT EVOLUTION' as evolution;
SELECT
    rtb.symbol,
    rtb.coef_0_10 as "0-10%",
    rtb.coef_10_20 as "10-20%",
    rtb.coef_20_30 as "20-30%",
    rtb.coef_30_40 as "30-40%",
    rtb.coef_40_50 as "40-50%",
    rtb.coef_50_60 as "50-60%",
    rtb.coef_60_70 as "60-70%",
    rtb.coef_70_80 as "70-80%",
    rtb.coef_80_90 as "80-90%",
    rtb.coef_90_100 as "90-100%"
FROM cryptoverse_risk_time_bands_v2 rtb
WHERE rtb.symbol IN ('BTC', 'ETH', 'SOL')
ORDER BY rtb.symbol;

-- 6. NEXT CRON JOB RUN
SELECT '⏰ NEXT SCHEDULED UPDATE' as schedule;
SELECT
    jobname,
    schedule,
    command,
    CASE
        WHEN schedule = '0 0 * * *' THEN 'Daily at midnight UTC'
        ELSE schedule
    END as frequency
FROM cron.job
WHERE jobname = 'daily-risk-band-update';

-- 7. QUICK HEALTH CHECK
SELECT '✅ SYSTEM HEALTH' as health;
SELECT
    CASE
        WHEN COUNT(*) > 0 THEN '✅ Risk Data: OK'
        ELSE '❌ Risk Data: MISSING'
    END as risk_data_status,
    CASE
        WHEN MAX(last_risk_update) >= CURRENT_DATE - INTERVAL '1 day' THEN '✅ Updates: CURRENT'
        ELSE '⚠️ Updates: STALE'
    END as update_status,
    CASE
        WHEN COUNT(DISTINCT symbol) >= 25 THEN '✅ Symbols: COMPLETE'
        ELSE '⚠️ Symbols: ' || COUNT(DISTINCT symbol) || '/25'
    END as symbol_status
FROM cryptoverse_risk_time_bands_v2;