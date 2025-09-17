-- RISKMETRIC MONITORING DASHBOARD
-- ================================
-- Real-time monitoring views and queries for trading decisions

-- 1. CREATE DASHBOARD SUMMARY VIEW
CREATE OR REPLACE VIEW v_riskmetric_dashboard AS
WITH score_stats AS (
    SELECT
        COUNT(*) as total_symbols,
        COUNT(CASE WHEN signal_strength = 'STRONGEST' THEN 1 END) as strongest_signals,
        COUNT(CASE WHEN signal_strength = 'STRONG' THEN 1 END) as strong_signals,
        COUNT(CASE WHEN signal_type = 'LONG' THEN 1 END) as long_signals,
        COUNT(CASE WHEN signal_type = 'SHORT' THEN 1 END) as short_signals,
        COUNT(CASE WHEN signal_type = 'NEUTRAL' THEN 1 END) as neutral_signals,
        AVG(total_score) as avg_score,
        MAX(total_score) as max_score,
        MIN(total_score) as min_score
    FROM v_riskmetric_scores
)
SELECT
    total_symbols,
    strongest_signals,
    strong_signals,
    long_signals,
    short_signals,
    neutral_signals,
    ROUND(avg_score, 1) as avg_score,
    ROUND(max_score, 1) as max_score,
    ROUND(min_score, 1) as min_score,
    NOW() as dashboard_update
FROM score_stats;

-- 2. STRONGEST BUY SIGNALS VIEW
CREATE OR REPLACE VIEW v_strongest_buy_signals AS
SELECT
    symbol,
    ROUND(current_risk, 3) as risk_value,
    current_risk_band,
    base_score,
    ROUND(coefficient, 3) as coefficient,
    ROUND(total_score, 1) as total_score,
    signal_strength,
    CASE
        WHEN signal_strength = 'STRONGEST' THEN '🔥🔥🔥 STRONGEST BUY'
        WHEN signal_strength = 'STRONG' THEN '🔥🔥 STRONG BUY'
        WHEN signal_strength = 'MODERATE' THEN '✅ BUY'
        ELSE '💰 ACCUMULATE'
    END as action,
    current_price,
    last_score_update
FROM v_riskmetric_scores
WHERE signal_type = 'LONG'
AND signal_strength IN ('STRONGEST', 'STRONG', 'MODERATE')
ORDER BY total_score DESC
LIMIT 10;

-- 3. STRONGEST SELL SIGNALS VIEW
CREATE OR REPLACE VIEW v_strongest_sell_signals AS
SELECT
    symbol,
    ROUND(current_risk, 3) as risk_value,
    current_risk_band,
    base_score,
    ROUND(coefficient, 3) as coefficient,
    ROUND(total_score, 1) as total_score,
    signal_strength,
    CASE
        WHEN signal_strength = 'STRONGEST' THEN '⚠️⚠️⚠️ STRONGEST SELL'
        WHEN signal_strength = 'STRONG' THEN '⚠️⚠️ STRONG SELL'
        WHEN signal_strength = 'MODERATE' THEN '📉 SELL'
        ELSE '💸 TAKE PROFIT'
    END as action,
    current_price,
    last_score_update
FROM v_riskmetric_scores
WHERE signal_type = 'SHORT'
AND signal_strength IN ('STRONGEST', 'STRONG', 'MODERATE')
ORDER BY total_score DESC
LIMIT 10;

-- 4. RARE MARKET CONDITIONS VIEW
CREATE OR REPLACE VIEW v_rare_market_conditions AS
SELECT
    symbol,
    current_risk_band,
    CASE current_risk_band
        WHEN '0.0-0.1' THEN band_0_10
        WHEN '0.1-0.2' THEN band_10_20
        WHEN '0.2-0.3' THEN band_20_30
        WHEN '0.3-0.4' THEN band_30_40
        WHEN '0.4-0.5' THEN band_40_50
        WHEN '0.5-0.6' THEN band_50_60
        WHEN '0.6-0.7' THEN band_60_70
        WHEN '0.7-0.8' THEN band_70_80
        WHEN '0.8-0.9' THEN band_80_90
        WHEN '0.9-1.0' THEN band_90_100
    END as days_in_band,
    ROUND(coefficient, 3) as rarity_coefficient,
    CASE
        WHEN coefficient >= 1.50 THEN '🌟 VERY RARE'
        WHEN coefficient >= 1.30 THEN '⭐ RARE'
        WHEN coefficient >= 1.15 THEN '📊 UNCOMMON'
        ELSE '📈 COMMON'
    END as rarity_status,
    total_score,
    signal_type,
    action
FROM v_riskmetric_scores
WHERE coefficient >= 1.30
ORDER BY coefficient DESC;

-- 5. PRICE TARGETS VIEW
CREATE OR REPLACE VIEW v_price_targets AS
SELECT
    symbol,
    current_price,
    ROUND(current_risk, 3) as current_risk,
    get_price_at_risk(symbol, 0.30, 'fiat') as accumulation_target,
    get_price_at_risk(symbol, 0.50, 'fiat') as neutral_target,
    get_price_at_risk(symbol, 0.70, 'fiat') as distribution_target,
    CASE
        WHEN current_risk < 0.30 THEN 'IN ACCUMULATION ZONE'
        WHEN current_risk > 0.70 THEN 'IN DISTRIBUTION ZONE'
        ELSE 'IN NEUTRAL ZONE'
    END as zone_status
FROM v_riskmetric_scores
WHERE symbol IN (
    SELECT symbol FROM v_riskmetric_scores
    ORDER BY total_score DESC
    LIMIT 10
);

-- 6. HISTORICAL PERFORMANCE VIEW
CREATE OR REPLACE VIEW v_score_performance AS
SELECT
    symbol,
    current_risk_band,
    COUNT(*) OVER (PARTITION BY current_risk_band) as symbols_in_band,
    base_score,
    MIN(coefficient) OVER (PARTITION BY base_score) as min_coef_for_score,
    MAX(coefficient) OVER (PARTITION BY base_score) as max_coef_for_score,
    ROUND(AVG(total_score) OVER (PARTITION BY base_score), 1) as avg_total_for_base,
    total_score,
    signal_strength
FROM v_riskmetric_scores;

-- 7. ALERT TRIGGERS VIEW
CREATE OR REPLACE VIEW v_trading_alerts AS
SELECT
    'IMMEDIATE ACTION' as priority,
    symbol,
    action,
    ROUND(total_score, 0) as score,
    ROUND(current_risk, 3) as risk,
    current_price as price,
    '🚨 Score > 150' as reason
FROM v_riskmetric_scores
WHERE total_score >= 150

UNION ALL

SELECT
    'HIGH PRIORITY' as priority,
    symbol,
    action,
    ROUND(total_score, 0) as score,
    ROUND(current_risk, 3) as risk,
    current_price as price,
    '⚡ Score 120-150' as reason
FROM v_riskmetric_scores
WHERE total_score >= 120 AND total_score < 150

UNION ALL

SELECT
    'WATCH CLOSELY' as priority,
    symbol,
    action,
    ROUND(total_score, 0) as score,
    ROUND(current_risk, 3) as risk,
    current_price as price,
    '👀 Rare condition' as reason
FROM v_riskmetric_scores
WHERE coefficient >= 1.45 AND total_score >= 90

ORDER BY
    CASE priority
        WHEN 'IMMEDIATE ACTION' THEN 1
        WHEN 'HIGH PRIORITY' THEN 2
        WHEN 'WATCH CLOSELY' THEN 3
    END,
    score DESC;

-- 8. QUICK DASHBOARD QUERY
-- Run this for instant market overview
SELECT '📊 RISKMETRIC TRADING DASHBOARD' as dashboard;
SELECT '=' as separator;

-- Summary Stats
SELECT '📈 MARKET OVERVIEW' as section;
SELECT * FROM v_riskmetric_dashboard;

-- Top Buy Signals
SELECT '🟢 TOP BUY SIGNALS' as section;
SELECT
    symbol,
    risk_value as risk,
    total_score as score,
    action
FROM v_strongest_buy_signals
LIMIT 5;

-- Top Sell Signals
SELECT '🔴 TOP SELL SIGNALS' as section;
SELECT
    symbol,
    risk_value as risk,
    total_score as score,
    action
FROM v_strongest_sell_signals
LIMIT 5;

-- Rare Conditions
SELECT '🌟 RARE MARKET CONDITIONS' as section;
SELECT
    symbol,
    rarity_coefficient as coef,
    rarity_status,
    action
FROM v_rare_market_conditions
LIMIT 5;

-- Active Alerts
SELECT '🚨 ACTIVE ALERTS' as section;
SELECT * FROM v_trading_alerts
LIMIT 10;

-- 9. MATERIALIZED VIEW FOR PERFORMANCE
-- Create this if you need faster dashboard loads
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_riskmetric_snapshot AS
SELECT
    symbol,
    current_risk,
    current_risk_band,
    base_score,
    coefficient,
    total_score,
    signal_type,
    signal_strength,
    action,
    current_price,
    last_score_update,
    NOW() as snapshot_time
FROM v_riskmetric_scores;

-- Refresh command (run periodically)
-- REFRESH MATERIALIZED VIEW mv_riskmetric_snapshot;

-- 10. MONITORING FUNCTION
CREATE OR REPLACE FUNCTION get_trading_summary()
RETURNS TABLE(
    metric TEXT,
    value TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'Total Symbols'::TEXT, COUNT(*)::TEXT FROM v_riskmetric_scores
    UNION ALL
    SELECT 'Strongest Signals', COUNT(*)::TEXT FROM v_riskmetric_scores WHERE signal_strength = 'STRONGEST'
    UNION ALL
    SELECT 'Buy Signals', COUNT(*)::TEXT FROM v_riskmetric_scores WHERE signal_type = 'LONG'
    UNION ALL
    SELECT 'Sell Signals', COUNT(*)::TEXT FROM v_riskmetric_scores WHERE signal_type = 'SHORT'
    UNION ALL
    SELECT 'Max Score', ROUND(MAX(total_score), 0)::TEXT FROM v_riskmetric_scores
    UNION ALL
    SELECT 'Avg Score', ROUND(AVG(total_score), 1)::TEXT FROM v_riskmetric_scores
    UNION ALL
    SELECT 'Last Update', MAX(last_score_update)::TEXT FROM cryptoverse_risk_time_bands_v2;
END;
$$ LANGUAGE plpgsql;

-- Usage: SELECT * FROM get_trading_summary();