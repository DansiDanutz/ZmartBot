-- ============================================================
-- RISKMETRIC AGENT - SQL VERSION
-- Complete Autonomous Risk Analysis System
-- ============================================================
-- Handles all calculations and outputs formatted analysis
-- Version: 1.0.0 | Status: PRODUCTION READY

-- DROP EXISTING FUNCTION IF EXISTS
DROP FUNCTION IF EXISTS riskmetric_agent(VARCHAR, DECIMAL);

-- MAIN RISKMETRIC AGENT FUNCTION
CREATE OR REPLACE FUNCTION riskmetric_agent(
    p_symbol VARCHAR,
    p_price DECIMAL DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    -- Variables
    v_price DECIMAL;
    v_risk DECIMAL;
    v_btc_value DECIMAL;
    v_btc_price DECIMAL;
    v_risk_band VARCHAR;
    v_current_band_days INTEGER;
    v_total_days INTEGER;
    v_base_score INTEGER;
    v_coefficient DECIMAL;
    v_total_score DECIMAL;
    v_signal VARCHAR;
    v_signal_strength VARCHAR;
    v_win_rate DECIMAL;

    -- Band data variables
    v_band_data RECORD;
    v_most_common_days INTEGER;
    v_target_days INTEGER;

    -- Output
    v_output TEXT;
BEGIN
    -- 1. GET CURRENT PRICE (use provided or fetch from database)
    IF p_price IS NULL THEN
        SELECT price_usd INTO v_price
        FROM cryptoverse_risk_data
        WHERE symbol = p_symbol;
    ELSE
        v_price := p_price;
    END IF;

    IF v_price IS NULL THEN
        RETURN 'Error: No price available for ' || p_symbol;
    END IF;

    -- 2. CALCULATE RISK VALUE
    v_risk := get_risk_at_price(p_symbol, v_price, 'fiat');

    -- 3. CALCULATE BTC VALUE
    SELECT price_usd INTO v_btc_price
    FROM cryptoverse_risk_data
    WHERE symbol = 'BTC';

    v_btc_value := v_price / COALESCE(v_btc_price, 100000);

    -- 4. GET RISK BAND
    v_risk_band := get_current_risk_band(v_risk);

    -- 5. GET BAND DATA
    SELECT * INTO v_band_data
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    IF v_band_data IS NULL THEN
        RETURN 'Error: No band data available for ' || p_symbol;
    END IF;

    -- 6. GET DAYS IN CURRENT BAND
    v_current_band_days := CASE v_risk_band
        WHEN '0.0-0.1' THEN v_band_data.band_0_10
        WHEN '0.1-0.2' THEN v_band_data.band_10_20
        WHEN '0.2-0.3' THEN v_band_data.band_20_30
        WHEN '0.3-0.4' THEN v_band_data.band_30_40
        WHEN '0.4-0.5' THEN v_band_data.band_40_50
        WHEN '0.5-0.6' THEN v_band_data.band_50_60
        WHEN '0.6-0.7' THEN v_band_data.band_60_70
        WHEN '0.7-0.8' THEN v_band_data.band_70_80
        WHEN '0.8-0.9' THEN v_band_data.band_80_90
        WHEN '0.9-1.0' THEN v_band_data.band_90_100
        ELSE 0
    END;

    v_total_days := v_band_data.total_days;

    -- 7. GET COEFFICIENT
    v_coefficient := CASE v_risk_band
        WHEN '0.0-0.1' THEN v_band_data.coef_0_10
        WHEN '0.1-0.2' THEN v_band_data.coef_10_20
        WHEN '0.2-0.3' THEN v_band_data.coef_20_30
        WHEN '0.3-0.4' THEN v_band_data.coef_30_40
        WHEN '0.4-0.5' THEN v_band_data.coef_40_50
        WHEN '0.5-0.6' THEN v_band_data.coef_50_60
        WHEN '0.6-0.7' THEN v_band_data.coef_60_70
        WHEN '0.7-0.8' THEN v_band_data.coef_70_80
        WHEN '0.8-0.9' THEN v_band_data.coef_80_90
        WHEN '0.9-1.0' THEN v_band_data.coef_90_100
        ELSE 1.0
    END;

    -- 8. CALCULATE BASE SCORE
    v_base_score := calculate_base_score(v_risk);

    -- 9. CALCULATE TOTAL SCORE
    v_total_score := v_base_score * v_coefficient;

    -- 10. DETERMINE SIGNAL
    v_signal := determine_signal_type(v_risk);

    -- 11. DETERMINE SIGNAL STRENGTH
    v_signal_strength := CASE
        WHEN v_total_score >= 150 THEN 'STRONGEST'
        WHEN v_total_score >= 120 THEN 'STRONG'
        WHEN v_total_score >= 90 THEN 'MODERATE'
        ELSE 'WEAK'
    END;

    -- 12. CALCULATE WIN RATE
    -- Find most common band days
    v_most_common_days := GREATEST(
        v_band_data.band_0_10, v_band_data.band_10_20, v_band_data.band_20_30,
        v_band_data.band_30_40, v_band_data.band_40_50, v_band_data.band_50_60,
        v_band_data.band_60_70, v_band_data.band_70_80, v_band_data.band_80_90,
        v_band_data.band_90_100
    );

    -- Calculate win rate based on signal type
    IF v_signal = 'LONG' AND v_risk <= 0.35 THEN
        -- For LONG in oversold, calculate reversion to middle
        v_target_days := v_band_data.band_40_50 + v_band_data.band_50_60;
        v_win_rate := LEAST((v_target_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100, 95);
    ELSIF v_signal = 'SHORT' AND v_risk >= 0.65 THEN
        -- For SHORT in overbought, calculate reversion to middle
        v_target_days := v_band_data.band_40_50 + v_band_data.band_50_60;
        v_win_rate := LEAST((v_target_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100, 95);
    ELSE
        -- NEUTRAL or weak zones
        v_win_rate := (v_most_common_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100;
    END IF;

    -- Ensure win rate is within bounds
    v_win_rate := GREATEST(0, LEAST(COALESCE(v_win_rate, 0), 95));

    -- 13. FORMAT OUTPUT ACCORDING TO TEMPLATE
    v_output := 'Risk value is: ' || ROUND(v_risk, 3) || E'\n\n' ||
                'BTC value at this price IS: ' || ROUND(v_btc_value, 6) || ' BTC' || E'\n\n' ||
                p_symbol || ' is in the ' || v_risk_band || ' risk band for ' ||
                v_current_band_days || ' days from his life age of ' || v_total_days || ' days.' || E'\n\n' ||
                'Based on all this data the base score is: ' || v_base_score ||
                ' points, and the coefficient based on our methodology is: ' || ROUND(v_coefficient, 3) || E'\n\n' ||
                'Total score is: ' || ROUND(v_total_score, 2) || ' that means a ' || v_signal || ' signal' || E'\n\n' ||
                'Based on our history patterns we have a WIN ratio for ' || v_signal || ' of: ' ||
                ROUND(v_win_rate, 1) || '%';

    RETURN v_output;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- ENHANCED VERSION WITH ADDITIONAL INSIGHTS
-- ============================================================

CREATE OR REPLACE FUNCTION riskmetric_agent_detailed(
    p_symbol VARCHAR,
    p_price DECIMAL DEFAULT NULL
)
RETURNS TABLE(
    analysis_text TEXT,
    risk_value DECIMAL,
    btc_value DECIMAL,
    risk_band VARCHAR,
    current_band_days INTEGER,
    total_days INTEGER,
    base_score INTEGER,
    coefficient DECIMAL,
    total_score DECIMAL,
    signal_type VARCHAR,
    signal_strength VARCHAR,
    win_rate DECIMAL,
    action_recommendation TEXT
) AS $$
DECLARE
    v_price DECIMAL;
    v_risk DECIMAL;
    v_btc_price DECIMAL;
    v_band_data RECORD;
    v_most_common_days INTEGER;
    v_target_days INTEGER;
    v_output TEXT;
    v_action TEXT;
BEGIN
    -- Get price
    IF p_price IS NULL THEN
        SELECT price_usd INTO v_price
        FROM cryptoverse_risk_data
        WHERE symbol = p_symbol;
    ELSE
        v_price := p_price;
    END IF;

    -- Calculate risk
    v_risk := get_risk_at_price(p_symbol, v_price, 'fiat');

    -- Get BTC price and calculate BTC value
    SELECT price_usd INTO v_btc_price
    FROM cryptoverse_risk_data
    WHERE symbol = 'BTC';

    btc_value := v_price / COALESCE(v_btc_price, 100000);

    -- Get band
    risk_band := get_current_risk_band(v_risk);

    -- Get band data
    SELECT * INTO v_band_data
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    -- Get days in current band
    current_band_days := CASE risk_band
        WHEN '0.0-0.1' THEN v_band_data.band_0_10
        WHEN '0.1-0.2' THEN v_band_data.band_10_20
        WHEN '0.2-0.3' THEN v_band_data.band_20_30
        WHEN '0.3-0.4' THEN v_band_data.band_30_40
        WHEN '0.4-0.5' THEN v_band_data.band_40_50
        WHEN '0.5-0.6' THEN v_band_data.band_50_60
        WHEN '0.6-0.7' THEN v_band_data.band_60_70
        WHEN '0.7-0.8' THEN v_band_data.band_70_80
        WHEN '0.8-0.9' THEN v_band_data.band_80_90
        WHEN '0.9-1.0' THEN v_band_data.band_90_100
    END;

    total_days := v_band_data.total_days;

    -- Get coefficient
    coefficient := CASE risk_band
        WHEN '0.0-0.1' THEN v_band_data.coef_0_10
        WHEN '0.1-0.2' THEN v_band_data.coef_10_20
        WHEN '0.2-0.3' THEN v_band_data.coef_20_30
        WHEN '0.3-0.4' THEN v_band_data.coef_30_40
        WHEN '0.4-0.5' THEN v_band_data.coef_40_50
        WHEN '0.5-0.6' THEN v_band_data.coef_50_60
        WHEN '0.6-0.7' THEN v_band_data.coef_60_70
        WHEN '0.7-0.8' THEN v_band_data.coef_70_80
        WHEN '0.8-0.9' THEN v_band_data.coef_80_90
        WHEN '0.9-1.0' THEN v_band_data.coef_90_100
    END;

    -- Calculate scores
    base_score := calculate_base_score(v_risk);
    total_score := base_score * coefficient;
    signal_type := determine_signal_type(v_risk);

    -- Signal strength
    signal_strength := CASE
        WHEN total_score >= 150 THEN 'STRONGEST'
        WHEN total_score >= 120 THEN 'STRONG'
        WHEN total_score >= 90 THEN 'MODERATE'
        ELSE 'WEAK'
    END;

    -- Calculate win rate
    v_most_common_days := GREATEST(
        v_band_data.band_0_10, v_band_data.band_10_20, v_band_data.band_20_30,
        v_band_data.band_30_40, v_band_data.band_40_50, v_band_data.band_50_60,
        v_band_data.band_60_70, v_band_data.band_70_80, v_band_data.band_80_90,
        v_band_data.band_90_100
    );

    IF signal_type = 'LONG' AND v_risk <= 0.35 THEN
        v_target_days := v_band_data.band_40_50 + v_band_data.band_50_60;
        win_rate := LEAST((v_target_days::DECIMAL / NULLIF(current_band_days, 0)) * 100, 95);
    ELSIF signal_type = 'SHORT' AND v_risk >= 0.65 THEN
        v_target_days := v_band_data.band_40_50 + v_band_data.band_50_60;
        win_rate := LEAST((v_target_days::DECIMAL / NULLIF(current_band_days, 0)) * 100, 95);
    ELSE
        win_rate := (v_most_common_days::DECIMAL / NULLIF(current_band_days, 0)) * 100;
    END IF;

    win_rate := GREATEST(0, LEAST(COALESCE(win_rate, 0), 95));
    risk_value := v_risk;

    -- Generate action recommendation
    v_action := CASE
        WHEN signal_type = 'LONG' AND signal_strength = 'STRONGEST' THEN
            '🔥🔥🔥 STRONGEST BUY - Extreme oversold with ' || ROUND(win_rate, 0) || '% win rate'
        WHEN signal_type = 'SHORT' AND signal_strength = 'STRONGEST' THEN
            '⚠️⚠️⚠️ STRONGEST SELL - Extreme overbought with ' || ROUND(win_rate, 0) || '% win rate'
        WHEN signal_type = 'LONG' AND signal_strength = 'STRONG' THEN
            '🔥🔥 STRONG BUY - Oversold with ' || ROUND(win_rate, 0) || '% win rate'
        WHEN signal_type = 'SHORT' AND signal_strength = 'STRONG' THEN
            '⚠️⚠️ STRONG SELL - Overbought with ' || ROUND(win_rate, 0) || '% win rate'
        WHEN signal_type = 'LONG' AND signal_strength = 'MODERATE' THEN
            '✅ BUY - Good entry with ' || ROUND(win_rate, 0) || '% win rate'
        WHEN signal_type = 'SHORT' AND signal_strength = 'MODERATE' THEN
            '📉 SELL - Good exit with ' || ROUND(win_rate, 0) || '% win rate'
        WHEN signal_type = 'NEUTRAL' THEN
            '⏸️ HOLD - Wait for risk < 0.35 (LONG) or > 0.65 (SHORT)'
        ELSE
            '👀 MONITOR - Weak signal'
    END;

    action_recommendation := v_action;

    -- Generate formatted output
    analysis_text := 'Risk value is: ' || ROUND(risk_value, 3) || E'\n\n' ||
                    'BTC value at this price IS: ' || ROUND(btc_value, 6) || ' BTC' || E'\n\n' ||
                    p_symbol || ' is in the ' || risk_band || ' risk band for ' ||
                    current_band_days || ' days from his life age of ' || total_days || ' days.' || E'\n\n' ||
                    'Based on all this data the base score is: ' || base_score ||
                    ' points, and the coefficient based on our methodology is: ' || ROUND(coefficient, 3) || E'\n\n' ||
                    'Total score is: ' || ROUND(total_score, 2) || ' that means a ' || signal_type || ' signal' || E'\n\n' ||
                    'Based on our history patterns we have a WIN ratio for ' || signal_type || ' of: ' ||
                    ROUND(win_rate, 1) || '%';

    RETURN QUERY SELECT
        analysis_text,
        risk_value,
        btc_value,
        risk_band,
        current_band_days,
        total_days,
        base_score,
        coefficient,
        total_score,
        signal_type,
        signal_strength,
        win_rate,
        action_recommendation;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- USAGE EXAMPLES
-- ============================================================

-- Example 1: Simple analysis with current database price
-- SELECT riskmetric_agent('AVAX');

-- Example 2: Analysis with specific price
-- SELECT riskmetric_agent('AVAX', 30.47);

-- Example 3: Detailed analysis with all fields
-- SELECT * FROM riskmetric_agent_detailed('AVAX', 30.47);

-- Example 4: Multiple symbols at once
-- SELECT
--     symbol,
--     riskmetric_agent(symbol) as analysis
-- FROM (VALUES ('BTC'), ('ETH'), ('SOL'), ('AVAX')) AS t(symbol);

-- ============================================================
-- TEST THE AGENT
-- ============================================================

SELECT '📊 RISKMETRIC AGENT TEST - AVAX at $30.47' as test;
SELECT riskmetric_agent('AVAX', 30.47);

SELECT '=' as separator;
SELECT '📊 DETAILED ANALYSIS' as test;
SELECT * FROM riskmetric_agent_detailed('AVAX', 30.47);