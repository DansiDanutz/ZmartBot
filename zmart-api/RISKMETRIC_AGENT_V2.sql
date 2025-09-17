-- ============================================================
-- RISKMETRIC AGENT V2 - WITH TARGET PRICE CALCULATION
-- ============================================================
-- Enhanced version with target price for better entry points
-- Version: 2.0.0 | Status: PRODUCTION READY

-- DROP EXISTING FUNCTIONS
DROP FUNCTION IF EXISTS riskmetric_agent_v2(VARCHAR, DECIMAL);
DROP FUNCTION IF EXISTS find_better_entry_target(VARCHAR, DECIMAL, VARCHAR);

-- ============================================================
-- HELPER FUNCTION: FIND BETTER ENTRY TARGET
-- ============================================================
CREATE OR REPLACE FUNCTION find_better_entry_target(
    p_symbol VARCHAR,
    p_current_risk DECIMAL,
    p_current_band VARCHAR
)
RETURNS TABLE(
    target_band VARCHAR,
    target_risk_center DECIMAL,
    target_price DECIMAL,
    target_days INTEGER,
    target_coefficient DECIMAL,
    target_score INTEGER,
    distance_to_target DECIMAL
) AS $$
DECLARE
    v_band_data RECORD;
    v_current_days INTEGER;
    v_best_long_band VARCHAR;
    v_best_short_band VARCHAR;
    v_best_long_days INTEGER := 999999;
    v_best_short_days INTEGER := 999999;
BEGIN
    -- Get band data
    SELECT * INTO v_band_data
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    -- Get current band days
    v_current_days := CASE p_current_band
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

    -- Find best LONG entry (look for rare oversold bands)
    IF p_current_risk > 0.35 THEN  -- Currently not in oversold
        -- Check 0.2-0.3 band
        IF v_band_data.band_20_30 < v_current_days AND v_band_data.band_20_30 > 0 THEN
            v_best_long_band := '0.2-0.3';
            v_best_long_days := v_band_data.band_20_30;
        END IF;

        -- Check 0.1-0.2 band (rarer)
        IF v_band_data.band_10_20 < v_best_long_days AND v_band_data.band_10_20 > 0 THEN
            v_best_long_band := '0.1-0.2';
            v_best_long_days := v_band_data.band_10_20;
        END IF;

        -- Check 0.0-0.1 band (rarest)
        IF v_band_data.band_0_10 < v_best_long_days AND v_band_data.band_0_10 > 0 THEN
            v_best_long_band := '0.0-0.1';
            v_best_long_days := v_band_data.band_0_10;
        END IF;

        -- Return LONG target if found
        IF v_best_long_band IS NOT NULL THEN
            RETURN QUERY
            SELECT
                v_best_long_band::VARCHAR as target_band,
                CASE v_best_long_band
                    WHEN '0.0-0.1' THEN 0.05
                    WHEN '0.1-0.2' THEN 0.15
                    WHEN '0.2-0.3' THEN 0.25
                END::DECIMAL as target_risk_center,
                get_price_at_risk(p_symbol, CASE v_best_long_band
                    WHEN '0.0-0.1' THEN 0.05
                    WHEN '0.1-0.2' THEN 0.15
                    WHEN '0.2-0.3' THEN 0.25
                END, 'fiat')::DECIMAL as target_price,
                v_best_long_days::INTEGER as target_days,
                CASE v_best_long_band
                    WHEN '0.0-0.1' THEN v_band_data.coef_0_10
                    WHEN '0.1-0.2' THEN v_band_data.coef_10_20
                    WHEN '0.2-0.3' THEN v_band_data.coef_20_30
                END::DECIMAL as target_coefficient,
                CASE
                    WHEN v_best_long_band IN ('0.0-0.1', '0.1-0.2') THEN 100
                    WHEN v_best_long_band = '0.2-0.3' THEN 80
                END::INTEGER as target_score,
                ABS(p_current_risk - CASE v_best_long_band
                    WHEN '0.0-0.1' THEN 0.05
                    WHEN '0.1-0.2' THEN 0.15
                    WHEN '0.2-0.3' THEN 0.25
                END)::DECIMAL as distance_to_target;
            RETURN;
        END IF;
    END IF;

    -- Find best SHORT entry (look for rare overbought bands)
    IF p_current_risk < 0.65 THEN  -- Currently not in overbought
        -- Check 0.7-0.8 band
        IF v_band_data.band_70_80 < v_current_days AND v_band_data.band_70_80 > 0 THEN
            v_best_short_band := '0.7-0.8';
            v_best_short_days := v_band_data.band_70_80;
        END IF;

        -- Check 0.8-0.9 band (rarer)
        IF v_band_data.band_80_90 < v_best_short_days AND v_band_data.band_80_90 > 0 THEN
            v_best_short_band := '0.8-0.9';
            v_best_short_days := v_band_data.band_80_90;
        END IF;

        -- Check 0.9-1.0 band (rarest)
        IF v_band_data.band_90_100 < v_best_short_days AND v_band_data.band_90_100 > 0 THEN
            v_best_short_band := '0.9-1.0';
            v_best_short_days := v_band_data.band_90_100;
        END IF;

        -- Return SHORT target if found
        IF v_best_short_band IS NOT NULL THEN
            RETURN QUERY
            SELECT
                v_best_short_band::VARCHAR as target_band,
                CASE v_best_short_band
                    WHEN '0.7-0.8' THEN 0.75
                    WHEN '0.8-0.9' THEN 0.85
                    WHEN '0.9-1.0' THEN 0.95
                END::DECIMAL as target_risk_center,
                get_price_at_risk(p_symbol, CASE v_best_short_band
                    WHEN '0.7-0.8' THEN 0.75
                    WHEN '0.8-0.9' THEN 0.85
                    WHEN '0.9-1.0' THEN 0.95
                END, 'fiat')::DECIMAL as target_price,
                v_best_short_days::INTEGER as target_days,
                CASE v_best_short_band
                    WHEN '0.7-0.8' THEN v_band_data.coef_70_80
                    WHEN '0.8-0.9' THEN v_band_data.coef_80_90
                    WHEN '0.9-1.0' THEN v_band_data.coef_90_100
                END::DECIMAL as target_coefficient,
                CASE
                    WHEN v_best_short_band IN ('0.8-0.9', '0.9-1.0') THEN 100
                    WHEN v_best_short_band = '0.7-0.8' THEN 80
                END::INTEGER as target_score,
                ABS(p_current_risk - CASE v_best_short_band
                    WHEN '0.7-0.8' THEN 0.75
                    WHEN '0.8-0.9' THEN 0.85
                    WHEN '0.9-1.0' THEN 0.95
                END)::DECIMAL as distance_to_target;
            RETURN;
        END IF;
    END IF;

    -- If no better target found, return NULL
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- MAIN RISKMETRIC AGENT V2 FUNCTION
-- ============================================================
CREATE OR REPLACE FUNCTION riskmetric_agent_v2(
    p_symbol VARCHAR,
    p_price DECIMAL DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    -- Current analysis variables
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

    -- Target entry variables
    v_target RECORD;
    v_target_text TEXT := '';

    -- Output
    v_output TEXT;
BEGIN
    -- 1. GET CURRENT PRICE
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

    -- 8. CALCULATE SCORES
    v_base_score := calculate_base_score(v_risk);
    v_total_score := v_base_score * v_coefficient;
    v_signal := determine_signal_type(v_risk);

    -- 9. SIGNAL STRENGTH
    v_signal_strength := CASE
        WHEN v_total_score >= 150 THEN 'STRONGEST'
        WHEN v_total_score >= 120 THEN 'STRONG'
        WHEN v_total_score >= 90 THEN 'MODERATE'
        ELSE 'WEAK'
    END;

    -- 10. CALCULATE WIN RATE
    v_most_common_days := GREATEST(
        v_band_data.band_0_10, v_band_data.band_10_20, v_band_data.band_20_30,
        v_band_data.band_30_40, v_band_data.band_40_50, v_band_data.band_50_60,
        v_band_data.band_60_70, v_band_data.band_70_80, v_band_data.band_80_90,
        v_band_data.band_90_100
    );

    IF v_signal = 'LONG' AND v_risk <= 0.35 THEN
        v_target_days := v_band_data.band_40_50 + v_band_data.band_50_60;
        v_win_rate := LEAST((v_target_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100, 95);
    ELSIF v_signal = 'SHORT' AND v_risk >= 0.65 THEN
        v_target_days := v_band_data.band_40_50 + v_band_data.band_50_60;
        v_win_rate := LEAST((v_target_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100, 95);
    ELSE
        v_win_rate := (v_most_common_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100;
    END IF;

    v_win_rate := GREATEST(0, LEAST(COALESCE(v_win_rate, 0), 95));

    -- 11. FIND BETTER ENTRY TARGET
    SELECT * INTO v_target
    FROM find_better_entry_target(p_symbol, v_risk, v_risk_band)
    LIMIT 1;

    -- Build target text if found
    IF v_target IS NOT NULL THEN
        v_target_text := E'\n\nThe Target for a better score is: $' ||
                        ROUND(v_target.target_price, 2) ||
                        ' (Risk: ' || ROUND(v_target.target_risk_center, 2) ||
                        ', Band: ' || v_target.target_band ||
                        ', ' || v_target.target_days || ' days, ' ||
                        'Coefficient: ' || ROUND(v_target.target_coefficient, 2) ||
                        ', Score: ' || (v_target.target_score * v_target.target_coefficient)::INTEGER || ')';
    ELSE
        -- Check if already in good position
        IF v_signal_strength IN ('STRONGEST', 'STRONG') THEN
            v_target_text := E'\n\nThe Target for a better score is: Already in optimal position!';
        ELSE
            v_target_text := E'\n\nThe Target for a better score is: Wait for extremes (< $' ||
                            ROUND(get_price_at_risk(p_symbol, 0.25, 'fiat'), 2) ||
                            ' for LONG or > $' ||
                            ROUND(get_price_at_risk(p_symbol, 0.75, 'fiat'), 2) ||
                            ' for SHORT)';
        END IF;
    END IF;

    -- 12. FORMAT OUTPUT WITH TARGET
    v_output := 'Risk value is: ' || ROUND(v_risk, 3) || E'\n\n' ||
                'BTC value at this price IS: ' || ROUND(v_btc_value, 6) || ' BTC' || E'\n\n' ||
                p_symbol || ' is in the ' || v_risk_band || ' risk band for ' ||
                v_current_band_days || ' days from his life age of ' || v_total_days || ' days.' || E'\n\n' ||
                'Based on all this data the base score is: ' || v_base_score ||
                ' points, and the coefficient based on our methodology is: ' || ROUND(v_coefficient, 3) || E'\n\n' ||
                'Total score is: ' || ROUND(v_total_score, 2) || ' that means a ' || v_signal || ' signal' || E'\n\n' ||
                'Based on our history patterns we have a WIN ratio for ' || v_signal || ' of: ' ||
                ROUND(v_win_rate, 1) || '%' || v_target_text;

    RETURN v_output;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- HELPER: GET ALL PRICE TARGETS
-- ============================================================
CREATE OR REPLACE FUNCTION get_all_price_targets(p_symbol VARCHAR)
RETURNS TABLE(
    risk_band VARCHAR,
    risk_center DECIMAL,
    price_usd DECIMAL,
    days_in_band INTEGER,
    coefficient DECIMAL,
    base_score INTEGER,
    total_score DECIMAL,
    rarity_rank TEXT
) AS $$
DECLARE
    v_band_data RECORD;
BEGIN
    SELECT * INTO v_band_data
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    RETURN QUERY
    WITH bands AS (
        SELECT * FROM (VALUES
            ('0.0-0.1', 0.05, v_band_data.band_0_10, v_band_data.coef_0_10, 100),
            ('0.1-0.2', 0.15, v_band_data.band_10_20, v_band_data.coef_10_20, 100),
            ('0.2-0.3', 0.25, v_band_data.band_20_30, v_band_data.coef_20_30, 80),
            ('0.3-0.4', 0.35, v_band_data.band_30_40, v_band_data.coef_30_40, 60),
            ('0.4-0.5', 0.45, v_band_data.band_40_50, v_band_data.coef_40_50, 50),
            ('0.5-0.6', 0.55, v_band_data.band_50_60, v_band_data.coef_50_60, 50),
            ('0.6-0.7', 0.65, v_band_data.band_60_70, v_band_data.coef_60_70, 60),
            ('0.7-0.8', 0.75, v_band_data.band_70_80, v_band_data.coef_70_80, 80),
            ('0.8-0.9', 0.85, v_band_data.band_80_90, v_band_data.coef_80_90, 100),
            ('0.9-1.0', 0.95, v_band_data.band_90_100, v_band_data.coef_90_100, 100)
        ) AS t(band, center, days, coef, score)
    )
    SELECT
        band::VARCHAR,
        center::DECIMAL,
        get_price_at_risk(p_symbol, center, 'fiat')::DECIMAL as price_usd,
        days::INTEGER,
        coef::DECIMAL,
        score::INTEGER,
        (score * coef)::DECIMAL as total_score,
        CASE
            WHEN days <= 50 THEN '🌟 RAREST'
            WHEN days <= 100 THEN '⭐ VERY RARE'
            WHEN days <= 200 THEN '✨ RARE'
            WHEN days <= 300 THEN '📊 COMMON'
            ELSE '📈 MOST COMMON'
        END::TEXT as rarity_rank
    FROM bands
    ORDER BY days ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- USAGE EXAMPLES
-- ============================================================

-- Example 1: Full analysis with target price
SELECT riskmetric_agent_v2('AVAX', 30.47);

-- Example 2: Get all price targets for a symbol
SELECT * FROM get_all_price_targets('AVAX')
ORDER BY total_score DESC;

-- Example 3: Find nearest better entry
SELECT * FROM find_better_entry_target(
    'AVAX',
    0.482,  -- current risk
    '0.4-0.5'  -- current band
);

-- ============================================================
-- TEST WITH AVAX
-- ============================================================
SELECT '📊 RISKMETRIC AGENT V2 - AVAX at $30.47' as test;
SELECT riskmetric_agent_v2('AVAX', 30.47);

SELECT '=' as separator;
SELECT '🎯 ALL PRICE TARGETS FOR AVAX' as test;
SELECT * FROM get_all_price_targets('AVAX')
ORDER BY total_score DESC;