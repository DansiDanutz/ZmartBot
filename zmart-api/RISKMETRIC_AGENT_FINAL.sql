-- ============================================================
-- ENHANCED RISKMETRIC AGENT - SQL VERSION WITH TARGET PRICE
-- Complete Autonomous Risk Analysis System with Optimal Entry Points
-- ============================================================
-- Version: 2.0.0 | Status: PRODUCTION READY
-- Includes target price calculation for finding rare bands

-- DROP EXISTING FUNCTIONS IF EXIST (INCLUDING CASCADE FOR DEPENDENCIES)
DROP FUNCTION IF EXISTS calculate_base_score(DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS determine_signal_type(DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS get_current_risk_band(DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(VARCHAR, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(VARCHAR, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS find_better_entry_target(VARCHAR, DECIMAL, VARCHAR, VARCHAR) CASCADE;

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Calculate base score from risk value
CREATE OR REPLACE FUNCTION calculate_base_score(p_risk DECIMAL)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE
        WHEN p_risk >= 0.00 AND p_risk <= 0.15 THEN 100  -- Extreme oversold (BUY zone)
        WHEN p_risk >= 0.85 AND p_risk <= 1.00 THEN 100  -- Extreme overbought (SELL zone)
        WHEN p_risk > 0.15 AND p_risk <= 0.25 THEN 80    -- Strong oversold
        WHEN p_risk >= 0.75 AND p_risk < 0.85 THEN 80    -- Strong overbought
        WHEN p_risk > 0.25 AND p_risk <= 0.35 THEN 60    -- Moderate oversold
        WHEN p_risk >= 0.65 AND p_risk < 0.75 THEN 60    -- Moderate overbought
        WHEN p_risk > 0.35 AND p_risk < 0.65 THEN 50     -- Neutral zone
    END;
END;
$$ LANGUAGE plpgsql;

-- Determine signal type from risk value
CREATE OR REPLACE FUNCTION determine_signal_type(p_risk DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    IF p_risk <= 0.35 THEN
        RETURN 'LONG';
    ELSIF p_risk >= 0.65 THEN
        RETURN 'SHORT';
    ELSE
        RETURN 'NEUTRAL';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Get current risk band from risk value
CREATE OR REPLACE FUNCTION get_current_risk_band(p_risk DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE
        WHEN p_risk >= 0.0 AND p_risk < 0.1 THEN '0.0-0.1'
        WHEN p_risk >= 0.1 AND p_risk < 0.2 THEN '0.1-0.2'
        WHEN p_risk >= 0.2 AND p_risk < 0.3 THEN '0.2-0.3'
        WHEN p_risk >= 0.3 AND p_risk < 0.4 THEN '0.3-0.4'
        WHEN p_risk >= 0.4 AND p_risk < 0.5 THEN '0.4-0.5'
        WHEN p_risk >= 0.5 AND p_risk < 0.6 THEN '0.5-0.6'
        WHEN p_risk >= 0.6 AND p_risk < 0.7 THEN '0.6-0.7'
        WHEN p_risk >= 0.7 AND p_risk < 0.8 THEN '0.7-0.8'
        WHEN p_risk >= 0.8 AND p_risk < 0.9 THEN '0.8-0.9'
        WHEN p_risk >= 0.9 AND p_risk <= 1.0 THEN '0.9-1.0'
        ELSE 'UNKNOWN'
    END;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- HELPER FUNCTION: Find Better Entry Target (NEIGHBOR BANDS)
-- ============================================================
CREATE OR REPLACE FUNCTION find_better_entry_target(
    p_symbol VARCHAR,
    p_current_risk DECIMAL,
    p_current_band VARCHAR,
    p_signal VARCHAR
)
RETURNS TABLE(
    target_price DECIMAL,
    target_risk DECIMAL,
    target_band VARCHAR,
    target_days INTEGER,
    target_coefficient DECIMAL,
    target_score DECIMAL,
    improvement DECIMAL
) AS $$
DECLARE
    v_band_data RECORD;
    v_current_days INTEGER;
    v_current_score DECIMAL;
    v_target_risk DECIMAL;
    v_target_band VARCHAR;
    v_target_days INTEGER;
    v_target_coef DECIMAL;
    v_target_base_score INTEGER;
    v_neighbor_days INTEGER;
    v_neighbor_coef DECIMAL;
BEGIN
    -- Get band data
    SELECT * INTO v_band_data
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    -- Get current days
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

    -- Calculate current score
    v_current_score := calculate_base_score(p_current_risk) * CASE p_current_band
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

    -- Find NEIGHBOR band based on signal (step by step approach)
    IF p_signal = 'LONG' THEN
        -- For LONG, move ONE BAND DOWN (towards lower risk)
        IF p_current_band = '0.4-0.5' THEN
            v_target_band := '0.3-0.4';
            v_target_risk := 0.35;
            v_neighbor_days := v_band_data.band_30_40;
            v_neighbor_coef := v_band_data.coef_30_40;
        ELSIF p_current_band = '0.3-0.4' THEN
            v_target_band := '0.2-0.3';
            v_target_risk := 0.25;
            v_neighbor_days := v_band_data.band_20_30;
            v_neighbor_coef := v_band_data.coef_20_30;
        ELSIF p_current_band = '0.2-0.3' THEN
            v_target_band := '0.1-0.2';
            v_target_risk := 0.15;
            v_neighbor_days := v_band_data.band_10_20;
            v_neighbor_coef := v_band_data.coef_10_20;
        ELSIF p_current_band = '0.1-0.2' THEN
            v_target_band := '0.0-0.1';
            v_target_risk := 0.05;
            v_neighbor_days := v_band_data.band_0_10;
            v_neighbor_coef := v_band_data.coef_0_10;
        ELSIF p_current_band = '0.5-0.6' THEN
            v_target_band := '0.4-0.5';
            v_target_risk := 0.45;
            v_neighbor_days := v_band_data.band_40_50;
            v_neighbor_coef := v_band_data.coef_40_50;
        ELSIF p_current_band = '0.6-0.7' THEN
            v_target_band := '0.5-0.6';
            v_target_risk := 0.55;
            v_neighbor_days := v_band_data.band_50_60;
            v_neighbor_coef := v_band_data.coef_50_60;
        ELSE
            -- Already at extreme or can't go lower
            RETURN;
        END IF;

        -- Check if neighbor has fewer days (better opportunity)
        IF v_neighbor_days >= v_current_days THEN
            -- Neighbor is not better, don't suggest it
            RETURN;
        END IF;

        v_target_days := v_neighbor_days;
        v_target_coef := v_neighbor_coef;

    ELSIF p_signal = 'SHORT' THEN
        -- For SHORT, move ONE BAND UP (towards higher risk)
        IF p_current_band = '0.5-0.6' THEN
            v_target_band := '0.6-0.7';
            v_target_risk := 0.65;
            v_neighbor_days := v_band_data.band_60_70;
            v_neighbor_coef := v_band_data.coef_60_70;
        ELSIF p_current_band = '0.6-0.7' THEN
            v_target_band := '0.7-0.8';
            v_target_risk := 0.75;
            v_neighbor_days := v_band_data.band_70_80;
            v_neighbor_coef := v_band_data.coef_70_80;
        ELSIF p_current_band = '0.7-0.8' THEN
            v_target_band := '0.8-0.9';
            v_target_risk := 0.85;
            v_neighbor_days := v_band_data.band_80_90;
            v_neighbor_coef := v_band_data.coef_80_90;
        ELSIF p_current_band = '0.8-0.9' THEN
            v_target_band := '0.9-1.0';
            v_target_risk := 0.95;
            v_neighbor_days := v_band_data.band_90_100;
            v_neighbor_coef := v_band_data.coef_90_100;
        ELSIF p_current_band = '0.4-0.5' THEN
            v_target_band := '0.5-0.6';
            v_target_risk := 0.55;
            v_neighbor_days := v_band_data.band_50_60;
            v_neighbor_coef := v_band_data.coef_50_60;
        ELSIF p_current_band = '0.3-0.4' THEN
            v_target_band := '0.4-0.5';
            v_target_risk := 0.45;
            v_neighbor_days := v_band_data.band_40_50;
            v_neighbor_coef := v_band_data.coef_40_50;
        ELSE
            -- Already at extreme or can't go higher
            RETURN;
        END IF;

        -- Check if neighbor has fewer days (better opportunity)
        IF v_neighbor_days >= v_current_days THEN
            -- Neighbor is not better, don't suggest it
            RETURN;
        END IF;

        v_target_days := v_neighbor_days;
        v_target_coef := v_neighbor_coef;

    ELSE  -- NEUTRAL
        -- For NEUTRAL, check both neighbors and pick the one with fewer days
        DECLARE
            v_lower_band VARCHAR;
            v_upper_band VARCHAR;
            v_lower_days INTEGER;
            v_upper_days INTEGER;
            v_lower_coef DECIMAL;
            v_upper_coef DECIMAL;
        BEGIN
            -- Get both neighbors
            CASE p_current_band
                WHEN '0.4-0.5' THEN
                    v_lower_band := '0.3-0.4';
                    v_lower_days := v_band_data.band_30_40;
                    v_lower_coef := v_band_data.coef_30_40;
                    v_upper_band := '0.5-0.6';
                    v_upper_days := v_band_data.band_50_60;
                    v_upper_coef := v_band_data.coef_50_60;
                WHEN '0.5-0.6' THEN
                    v_lower_band := '0.4-0.5';
                    v_lower_days := v_band_data.band_40_50;
                    v_lower_coef := v_band_data.coef_40_50;
                    v_upper_band := '0.6-0.7';
                    v_upper_days := v_band_data.band_60_70;
                    v_upper_coef := v_band_data.coef_60_70;
                ELSE
                    RETURN;
            END CASE;

            -- Pick the neighbor with fewer days
            IF v_lower_days < v_upper_days AND v_lower_days < v_current_days THEN
                v_target_band := v_lower_band;
                v_target_risk := CASE v_lower_band
                    WHEN '0.3-0.4' THEN 0.35
                    WHEN '0.4-0.5' THEN 0.45
                END;
                v_target_days := v_lower_days;
                v_target_coef := v_lower_coef;
            ELSIF v_upper_days < v_lower_days AND v_upper_days < v_current_days THEN
                v_target_band := v_upper_band;
                v_target_risk := CASE v_upper_band
                    WHEN '0.5-0.6' THEN 0.55
                    WHEN '0.6-0.7' THEN 0.65
                END;
                v_target_days := v_upper_days;
                v_target_coef := v_upper_coef;
            ELSE
                -- No better neighbor
                RETURN;
            END IF;
        END;
    END IF;

    -- If no target found, return NULL
    IF v_target_risk IS NULL THEN
        RETURN;
    END IF;

    -- Calculate target base score
    v_target_base_score := calculate_base_score(v_target_risk);

    -- Get price at target risk
    target_price := get_price_at_risk(p_symbol, v_target_risk, 'fiat');
    target_risk := v_target_risk;
    target_band := v_target_band;
    target_days := v_target_days;
    target_coefficient := v_target_coef;
    target_score := v_target_base_score * v_target_coef;
    improvement := (v_target_base_score * v_target_coef) - v_current_score;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- MAIN ENHANCED RISKMETRIC AGENT FUNCTION WITH ALTCOIN SEASON
-- ============================================================
CREATE OR REPLACE FUNCTION riskmetric_agent_enhanced(
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

    -- Target variables
    v_target RECORD;
    v_has_target BOOLEAN := FALSE;

    -- BTC pair analysis variables
    v_btc_risk DECIMAL;
    v_btc_risk_band VARCHAR;
    v_market_phase VARCHAR;
    v_season_strength VARCHAR;

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

    -- 2. CALCULATE RISK VALUE (Using linear interpolation)
    -- CRITICAL: Always use exact interpolation, never approximate!
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

    -- Simple formula: (Most Common Days / Current Days) × 100
    v_win_rate := LEAST((v_most_common_days::DECIMAL / NULLIF(v_current_band_days, 0)) * 100, 95);
    v_win_rate := GREATEST(0, COALESCE(v_win_rate, 0));

    -- 13. FIND BETTER ENTRY TARGET (NEW!)
    SELECT * INTO v_target
    FROM find_better_entry_target(p_symbol, v_risk, v_risk_band, v_signal);

    IF v_target.target_price IS NOT NULL THEN
        v_has_target := TRUE;
    END IF;

    -- 14. FORMAT OUTPUT ACCORDING TO TEMPLATE
    v_output := 'Risk value is: ' || ROUND(v_risk, 3) || E'\n\n' ||
                'BTC value at this price IS: ' || ROUND(v_btc_value, 6) || ' BTC' || E'\n\n' ||
                p_symbol || ' is in the ' || v_risk_band || ' risk band for ' ||
                v_current_band_days || ' days from his life age of ' || v_total_days || ' days.' || E'\n\n' ||
                'Based on all this data the base score is: ' || v_base_score ||
                ' points, and the coefficient based on our methodology is: ' || ROUND(v_coefficient, 3) || E'\n\n' ||
                'Total score is: ' || ROUND(v_total_score, 2) || ' that means a ' || v_signal || ' signal' || E'\n\n' ||
                'Based on our history patterns we have a WIN ratio for ' || v_signal || ' of: ' ||
                ROUND(v_win_rate, 1) || '%';

    -- Add target information if available
    IF v_has_target THEN
        v_output := v_output || E'\n\n' ||
                   'The Target for a better score is: $' || ROUND(v_target.target_price, 2) ||
                   ' (Risk: ' || ROUND(v_target.target_risk, 2) ||
                   ', Band: ' || v_target.target_band ||
                   ', ' || v_target.target_days || ' days' ||
                   ', Coefficient: ' || ROUND(v_target.target_coefficient, 2) ||
                   ', Score: ' || ROUND(v_target.target_score, 0) || ')';

        IF v_target.improvement > 0 THEN
            v_output := v_output || E'\n' ||
                       'This would improve your score by ' || ROUND(v_target.improvement, 1) || ' points!';
        END IF;
    END IF;

    -- 15. ANALYZE BTC PAIR FOR ALTCOIN SEASON (NEW!)
    -- Only for non-BTC symbols
    IF p_symbol != 'BTC' THEN
        -- Calculate BTC pair risk (symbol/BTC)
        -- We use the BTC value (e.g., 0.000305 BTC) directly as the "price" in BTC terms
        v_btc_risk := get_risk_at_price(p_symbol, v_btc_value, 'btc');
        v_btc_risk_band := get_current_risk_band(v_btc_risk);

        -- Determine market phase based on BTC pair risk
        -- Low risk (0-0.35) = Symbol weak vs BTC = Bitcoin season
        -- Mid risk (0.35-0.65) = Neutral phase
        -- High risk (0.65-1.0) = Symbol strong vs BTC = Altcoin season

        IF v_btc_risk <= 0.25 THEN
            v_market_phase := 'STRONG BITCOIN SEASON';
            v_season_strength := p_symbol || ' is very weak against BTC';
        ELSIF v_btc_risk > 0.25 AND v_btc_risk <= 0.35 THEN
            v_market_phase := 'BITCOIN SEASON';
            v_season_strength := p_symbol || ' is weak against BTC';
        ELSIF v_btc_risk > 0.35 AND v_btc_risk <= 0.50 THEN
            v_market_phase := 'EARLY TRANSITION';
            v_season_strength := p_symbol || ' starting to show strength vs BTC';
        ELSIF v_btc_risk > 0.50 AND v_btc_risk <= 0.65 THEN
            v_market_phase := 'LATE TRANSITION';
            v_season_strength := p_symbol || ' gaining momentum against BTC';
        ELSIF v_btc_risk > 0.65 AND v_btc_risk <= 0.75 THEN
            v_market_phase := 'ALTCOIN SEASON';
            v_season_strength := p_symbol || ' is strong against BTC';
        ELSIF v_btc_risk > 0.75 AND v_btc_risk <= 0.85 THEN
            v_market_phase := 'STRONG ALTCOIN SEASON';
            v_season_strength := p_symbol || ' is very strong against BTC';
        ELSE -- v_btc_risk > 0.85
            v_market_phase := 'PEAK ALTCOIN SEASON';
            v_season_strength := p_symbol || ' at extreme strength vs BTC (caution!)';
        END IF;

        -- Add market phase analysis to output
        v_output := v_output || E'\n\n' ||
                   '📊 MARKET PHASE ANALYSIS:' || E'\n' ||
                   p_symbol || '/BTC Risk: ' || ROUND(v_btc_risk, 3) || ' (Band: ' || v_btc_risk_band || ')' || E'\n' ||
                   'Market Phase: ' || v_market_phase || E'\n' ||
                   v_season_strength;

        -- Add strategic insight based on both USD and BTC risks
        v_output := v_output || E'\n\n' ||
                   '💡 STRATEGIC INSIGHT:' || E'\n';

        -- Combined analysis
        IF v_risk <= 0.35 AND v_btc_risk <= 0.35 THEN
            v_output := v_output || 'OVERSOLD in both USD and BTC - Strong accumulation zone during Bitcoin dominance';
        ELSIF v_risk <= 0.35 AND v_btc_risk >= 0.65 THEN
            v_output := v_output || 'OVERSOLD in USD but STRONG vs BTC - Altcoin showing relative strength';
        ELSIF v_risk >= 0.65 AND v_btc_risk <= 0.35 THEN
            v_output := v_output || 'OVERBOUGHT in USD but WEAK vs BTC - Rising with market but underperforming Bitcoin';
        ELSIF v_risk >= 0.65 AND v_btc_risk >= 0.65 THEN
            v_output := v_output || 'OVERBOUGHT in both USD and BTC - Peak altcoin euphoria, consider taking profits';
        ELSIF v_btc_risk <= 0.25 THEN
            v_output := v_output || 'Bitcoin strongly outperforming - Wait for altcoin season to begin';
        ELSIF v_btc_risk >= 0.75 THEN
            v_output := v_output || 'Peak altcoin outperformance - Monitor for rotation back to Bitcoin';
        ELSE
            v_output := v_output || 'Balanced market conditions - Follow standard risk signals';
        END IF;
    END IF;

    RETURN v_output;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- ENHANCED VERSION WITH DETAILED TABLE OUTPUT
-- ============================================================
CREATE OR REPLACE FUNCTION riskmetric_agent_enhanced_detailed(
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
    target_price DECIMAL,
    target_risk DECIMAL,
    target_band VARCHAR,
    target_days INTEGER,
    target_coefficient DECIMAL,
    target_score DECIMAL,
    score_improvement DECIMAL,
    btc_pair_risk DECIMAL,
    btc_pair_band VARCHAR,
    market_phase VARCHAR,
    season_analysis TEXT,
    action_recommendation TEXT
) AS $$
DECLARE
    v_price DECIMAL;
    v_risk DECIMAL;
    v_btc_price DECIMAL;
    v_band_data RECORD;
    v_most_common_days INTEGER;
    v_output TEXT;
    v_action TEXT;
    v_target RECORD;
    v_has_target BOOLEAN := FALSE;
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
    risk_value := v_risk;

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

    win_rate := LEAST((v_most_common_days::DECIMAL / NULLIF(current_band_days, 0)) * 100, 95);
    win_rate := GREATEST(0, COALESCE(win_rate, 0));

    -- Find better entry target
    SELECT * INTO v_target
    FROM find_better_entry_target(p_symbol, v_risk, risk_band, signal_type);

    IF v_target.target_price IS NOT NULL THEN
        v_has_target := TRUE;
        target_price := v_target.target_price;
        target_risk := v_target.target_risk;
        target_band := v_target.target_band;
        target_days := v_target.target_days;
        target_coefficient := v_target.target_coefficient;
        target_score := v_target.target_score;
        score_improvement := v_target.improvement;
    END IF;

    -- Generate action recommendation with target
    IF v_has_target THEN
        v_action := CASE
            WHEN signal_type = 'LONG' THEN
                '🎯 WAIT FOR TARGET: $' || ROUND(v_target.target_price, 2) || ' for better LONG entry (Score: ' || ROUND(v_target.target_score, 0) || ')'
            WHEN signal_type = 'SHORT' THEN
                '🎯 WAIT FOR TARGET: $' || ROUND(v_target.target_price, 2) || ' for better SHORT entry (Score: ' || ROUND(v_target.target_score, 0) || ')'
            ELSE
                '⏸️ MONITOR - Target: $' || ROUND(v_target.target_price, 2) || ' for opportunity'
        END;
    ELSE
        v_action := CASE
            WHEN signal_type = 'LONG' AND signal_strength IN ('STRONGEST', 'STRONG') THEN
                '🔥🔥🔥 STRONGEST BUY - Already at optimal entry with ' || ROUND(win_rate, 0) || '% win rate'
            WHEN signal_type = 'SHORT' AND signal_strength IN ('STRONGEST', 'STRONG') THEN
                '⚠️⚠️⚠️ STRONGEST SELL - Already at optimal exit with ' || ROUND(win_rate, 0) || '% win rate'
            WHEN signal_type = 'LONG' AND signal_strength = 'MODERATE' THEN
                '✅ BUY - Good entry with ' || ROUND(win_rate, 0) || '% win rate'
            WHEN signal_type = 'SHORT' AND signal_strength = 'MODERATE' THEN
                '📉 SELL - Good exit with ' || ROUND(win_rate, 0) || '% win rate'
            WHEN signal_type = 'NEUTRAL' THEN
                '⏸️ HOLD - Wait for risk < 0.35 (LONG) or > 0.65 (SHORT)'
            ELSE
                '👀 MONITOR - Weak signal'
        END;
    END IF;

    action_recommendation := v_action;

    -- Add BTC pair analysis if not BTC
    IF p_symbol != 'BTC' THEN
        btc_pair_risk := get_risk_at_price(p_symbol, btc_value, 'btc');
        btc_pair_band := get_current_risk_band(btc_pair_risk);

        -- Determine market phase
        IF btc_pair_risk <= 0.25 THEN
            market_phase := 'STRONG BITCOIN SEASON';
        ELSIF btc_pair_risk <= 0.35 THEN
            market_phase := 'BITCOIN SEASON';
        ELSIF btc_pair_risk <= 0.50 THEN
            market_phase := 'EARLY TRANSITION';
        ELSIF btc_pair_risk <= 0.65 THEN
            market_phase := 'LATE TRANSITION';
        ELSIF btc_pair_risk <= 0.75 THEN
            market_phase := 'ALTCOIN SEASON';
        ELSIF btc_pair_risk <= 0.85 THEN
            market_phase := 'STRONG ALTCOIN SEASON';
        ELSE
            market_phase := 'PEAK ALTCOIN SEASON';
        END IF;

        -- Create season analysis
        IF risk_value <= 0.35 AND btc_pair_risk <= 0.35 THEN
            season_analysis := 'OVERSOLD both USD/BTC - Accumulation during BTC dominance';
        ELSIF risk_value <= 0.35 AND btc_pair_risk >= 0.65 THEN
            season_analysis := 'OVERSOLD USD, STRONG vs BTC - Altcoin relative strength';
        ELSIF risk_value >= 0.65 AND btc_pair_risk <= 0.35 THEN
            season_analysis := 'OVERBOUGHT USD, WEAK vs BTC - Underperforming Bitcoin';
        ELSIF risk_value >= 0.65 AND btc_pair_risk >= 0.65 THEN
            season_analysis := 'OVERBOUGHT both USD/BTC - Peak euphoria, take profits';
        ELSE
            season_analysis := 'Balanced conditions - Follow standard signals';
        END IF;
    END IF;

    -- Generate formatted output
    analysis_text := riskmetric_agent_enhanced(p_symbol, p_price);

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
        target_price,
        target_risk,
        target_band,
        target_days,
        target_coefficient,
        target_score,
        score_improvement,
        btc_pair_risk,
        btc_pair_band,
        market_phase,
        season_analysis,
        action_recommendation;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- USAGE EXAMPLES
-- ============================================================

-- Example 1: Simple enhanced analysis with current database price
-- SELECT riskmetric_agent_enhanced('AVAX');

-- Example 2: Enhanced analysis with specific price
-- SELECT riskmetric_agent_enhanced('AVAX', 30.47);

-- Example 3: Detailed analysis with all fields including target
-- SELECT * FROM riskmetric_agent_enhanced_detailed('AVAX', 30.47);

-- Example 4: Multiple symbols with targets
-- SELECT
--     symbol,
--     riskmetric_agent_enhanced(symbol) as analysis
-- FROM (VALUES ('BTC'), ('ETH'), ('SOL'), ('AVAX')) AS t(symbol);

-- ============================================================
-- TEST THE ENHANCED AGENT
-- ============================================================

SELECT '📊 ENHANCED RISKMETRIC AGENT TEST - AVAX at $30.47' as test;
SELECT riskmetric_agent_enhanced('AVAX', 30.47);

SELECT '=' as separator;
SELECT '📊 DETAILED ANALYSIS WITH TARGET' as test;
SELECT * FROM riskmetric_agent_enhanced_detailed('AVAX', 30.47);