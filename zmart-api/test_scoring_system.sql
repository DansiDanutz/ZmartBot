-- TEST RISKMETRIC SCORING SYSTEM
-- ================================
-- Comprehensive tests to verify scoring implementation

-- 1. TEST BASE SCORE CALCULATION
SELECT '🧪 BASE SCORE CALCULATION TEST' as test_section;
WITH test_risks AS (
    SELECT * FROM (VALUES
        (0.05, 100, 'Extreme oversold'),
        (0.10, 100, 'Extreme oversold'),
        (0.15, 100, 'Extreme oversold edge'),
        (0.20, 80, 'Strong accumulation'),
        (0.25, 80, 'Strong accumulation edge'),
        (0.30, 60, 'Moderate accumulation'),
        (0.35, 60, 'Moderate accumulation edge'),
        (0.50, 50, 'Neutral zone'),
        (0.65, 60, 'Moderate distribution edge'),
        (0.70, 60, 'Moderate distribution'),
        (0.75, 80, 'Strong distribution edge'),
        (0.80, 80, 'Strong distribution'),
        (0.85, 100, 'Extreme overbought edge'),
        (0.90, 100, 'Extreme overbought'),
        (0.95, 100, 'Extreme overbought')
    ) AS t(risk, expected_score, description)
)
SELECT
    risk,
    expected_score,
    calculate_base_score(risk) as calculated_score,
    description,
    CASE
        WHEN calculate_base_score(risk) = expected_score THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM test_risks
ORDER BY risk;

-- 2. TEST SIGNAL TYPE DETERMINATION
SELECT '🧪 SIGNAL TYPE TEST' as test_section;
WITH test_signals AS (
    SELECT * FROM (VALUES
        (0.10, 'LONG', 'Deep accumulation'),
        (0.25, 'LONG', 'Accumulation'),
        (0.35, 'LONG', 'Late accumulation'),
        (0.50, 'NEUTRAL', 'Middle neutral'),
        (0.65, 'SHORT', 'Early distribution'),
        (0.75, 'SHORT', 'Distribution'),
        (0.90, 'SHORT', 'Deep distribution')
    ) AS t(risk, expected_signal, description)
)
SELECT
    risk,
    expected_signal,
    determine_signal_type(risk) as calculated_signal,
    description,
    CASE
        WHEN determine_signal_type(risk) = expected_signal THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM test_signals
ORDER BY risk;

-- 3. TEST COMPLETE SCORING WITH REAL DATA
SELECT '📊 LIVE SCORING TEST - TOP SYMBOLS' as test_section;
SELECT
    symbol,
    ROUND(current_risk, 3) as risk,
    current_risk_band as band,
    base_score,
    ROUND(coefficient, 3) as coef,
    ROUND(total_score, 1) as score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE symbol IN ('BTC', 'ETH', 'SOL', 'ADA', 'AVAX')
ORDER BY total_score DESC;

-- 4. CHECK COEFFICIENT APPLICATION
SELECT '🔢 COEFFICIENT VERIFICATION' as test_section;
WITH sol_check AS (
    SELECT
        symbol,
        current_risk,
        current_risk_band,
        base_score,
        CASE current_risk_band
            WHEN '0.0-0.1' THEN coef_0_10
            WHEN '0.1-0.2' THEN coef_10_20
            WHEN '0.2-0.3' THEN coef_20_30
            WHEN '0.3-0.4' THEN coef_30_40
            WHEN '0.4-0.5' THEN coef_40_50
            WHEN '0.5-0.6' THEN coef_50_60
            WHEN '0.6-0.7' THEN coef_60_70
            WHEN '0.7-0.8' THEN coef_70_80
            WHEN '0.8-0.9' THEN coef_80_90
            WHEN '0.9-1.0' THEN coef_90_100
        END as coefficient,
        total_score,
        band_70_80 as days_in_current_band
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = 'SOL'
)
SELECT
    symbol,
    ROUND(current_risk, 3) as risk,
    current_risk_band as band,
    days_in_current_band as days,
    base_score,
    ROUND(coefficient, 3) as coef,
    base_score || ' × ' || ROUND(coefficient, 3) as formula,
    ROUND(total_score, 1) as calculated,
    ROUND(base_score * coefficient, 1) as expected,
    CASE
        WHEN ABS(total_score - (base_score * coefficient)) < 0.1 THEN '✅ MATCH'
        ELSE '❌ MISMATCH'
    END as verification
FROM sol_check;

-- 5. FIND STRONGEST SIGNALS
SELECT '🎯 STRONGEST TRADING SIGNALS' as test_section;
SELECT
    symbol,
    ROUND(current_risk, 3) as risk,
    base_score as base,
    ROUND(coefficient, 2) as coef,
    ROUND(total_score, 0) as score,
    signal_strength as strength,
    action
FROM v_riskmetric_scores
WHERE signal_strength IN ('STRONGEST', 'STRONG')
ORDER BY total_score DESC
LIMIT 10;

-- 6. DISTRIBUTION OF SIGNAL STRENGTHS
SELECT '📈 SIGNAL STRENGTH DISTRIBUTION' as test_section;
SELECT
    signal_strength,
    COUNT(*) as count,
    ROUND(AVG(total_score), 1) as avg_score,
    MIN(total_score) as min_score,
    MAX(total_score) as max_score
FROM v_riskmetric_scores
WHERE signal_type != 'NEUTRAL'
GROUP BY signal_strength
ORDER BY
    CASE signal_strength
        WHEN 'STRONGEST' THEN 1
        WHEN 'STRONG' THEN 2
        WHEN 'MODERATE' THEN 3
        WHEN 'WEAK' THEN 4
    END;

-- 7. EXTREME ZONE ANALYSIS
SELECT '⚡ EXTREME ZONES (100 POINTS BASE)' as test_section;
SELECT
    symbol,
    ROUND(current_risk, 3) as risk,
    CASE
        WHEN current_risk <= 0.15 THEN 'EXTREME OVERSOLD'
        WHEN current_risk >= 0.85 THEN 'EXTREME OVERBOUGHT'
    END as zone,
    base_score,
    ROUND(coefficient, 3) as coef,
    ROUND(total_score, 0) as total,
    signal_type,
    action
FROM v_riskmetric_scores
WHERE current_risk <= 0.15 OR current_risk >= 0.85
ORDER BY total_score DESC;

-- 8. CHECK SCORING UPDATES
SELECT '🔄 LAST SCORING UPDATE' as test_section;
SELECT
    COUNT(*) as total_symbols,
    COUNT(last_score_update) as symbols_with_scores,
    MIN(last_score_update) as oldest_update,
    MAX(last_score_update) as newest_update,
    CASE
        WHEN COUNT(*) = COUNT(last_score_update) THEN '✅ ALL SCORED'
        ELSE '⚠️ ' || (COUNT(*) - COUNT(last_score_update)) || ' MISSING'
    END as status
FROM cryptoverse_risk_time_bands_v2;

-- 9. TOP OPPORTUNITIES VIEW TEST
SELECT '💎 TOP TRADING OPPORTUNITIES' as test_section;
SELECT * FROM v_top_trading_opportunities;

-- 10. MANUAL SCORE CALCULATION TEST
SELECT '🔧 MANUAL CALCULATION FOR SOL' as test_section;
SELECT
    'SOL @ $245' as context,
    'Risk: 0.715' as step1,
    'Band: 0.7-0.8' as step2,
    'Days in band: 140' as step3,
    'Coefficient: 1.450' as step4,
    'Base score: 60 (0.65-0.75 range)' as step5,
    'Total: 60 × 1.450 = 87' as step6,
    'Signal: SHORT (risk > 0.65)' as step7,
    'Strength: WEAK (< 90)' as step8,
    '👀 MONITOR' as action;