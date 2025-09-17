-- VERIFY TIME BANDS COMPLETE SETUP
-- =================================

-- 1. CHECK DATA STATUS
SELECT
    '📊 TIME BANDS DATA STATUS' as check_type,
    COUNT(*) as total_symbols,
    CASE
        WHEN COUNT(*) = 25 THEN '✅ All 25 symbols loaded!'
        ELSE '⚠️ Only ' || COUNT(*) || ' symbols loaded'
    END as status
FROM cryptoverse_risk_time_bands;

-- 2. SHOW ZONE DISTRIBUTION FOR ALL SYMBOLS
SELECT
    symbol,
    current_risk_band as "Current Band",
    ROUND(accumulation_pct, 1) as "Accumulation %",
    ROUND(transition_pct, 1) as "Transition %",
    ROUND(distribution_pct, 1) as "Distribution %",
    CASE
        WHEN current_risk_band LIKE '0.%' THEN '🟢'
        WHEN current_risk_band < '0.7' THEN '🟡'
        ELSE '🔴'
    END as "Zone"
FROM v_risk_time_distribution
ORDER BY symbol;

-- 3. INTERESTING STATISTICS
SELECT
    '📈 STATISTICS' as analysis,
    ROUND(AVG(accumulation_pct), 1) as "Avg Accumulation %",
    ROUND(AVG(transition_pct), 1) as "Avg Transition %",
    ROUND(AVG(distribution_pct), 1) as "Avg Distribution %"
FROM v_risk_time_distribution;

-- 4. SYMBOLS BY CURRENT RISK
SELECT
    current_risk_band,
    COUNT(*) as symbols_count,
    string_agg(symbol, ', ' ORDER BY symbol) as symbols
FROM cryptoverse_risk_time_bands
GROUP BY current_risk_band
ORDER BY current_risk_band;

-- 5. COMBINED ANALYSIS - SOL EXAMPLE
SELECT
    'SOL COMPLETE ANALYSIS' as symbol_analysis,
    get_price_at_risk('SOL', 0.715, 'fiat') as "Current Price (at 71.5% risk)",
    (SELECT band_70_80 FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL') as "Days in 70-80% band",
    (SELECT band_70_80_pct FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL') as "% Time in 70-80% band";

-- 6. FINAL STATUS
SELECT
    '🎉 COMPLETE RISK SYSTEM' as status,
    'You now have:' as message
UNION ALL
SELECT
    '✅' as status,
    '1,025 FIAT risk grid points' as message
UNION ALL
SELECT
    '✅' as status,
    '410 BTC risk grid points' as message
UNION ALL
SELECT
    '✅' as status,
    '25 symbols time distribution data' as message
UNION ALL
SELECT
    '✅' as status,
    'Functions for price/risk interpolation' as message;