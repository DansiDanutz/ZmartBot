-- WIN RATE CALCULATION FUNCTION
-- Based on band rarity and mean reversion probability

CREATE OR REPLACE FUNCTION calculate_win_rate(
    p_symbol VARCHAR,
    p_risk DECIMAL
)
RETURNS TABLE(
    signal_type VARCHAR,
    win_rate DECIMAL,
    explanation TEXT
) AS $$
DECLARE
    v_band VARCHAR;
    v_current_days INTEGER;
    v_target_days DECIMAL;
    v_signal VARCHAR;
    v_win_rate DECIMAL;
    v_explanation TEXT;
BEGIN
    -- Get current band
    v_band := get_current_risk_band(p_risk);

    -- Get days in current band
    SELECT CASE v_band
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
    END INTO v_current_days
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    -- Get signal type
    v_signal := determine_signal_type(p_risk);

    -- Calculate target days (average of middle bands)
    SELECT (band_40_50 + band_50_60) / 2.0 INTO v_target_days
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    -- Calculate win rate based on signal
    IF v_signal = 'LONG' AND p_risk <= 0.35 THEN
        -- For LONG positions, compare to middle bands
        v_win_rate := LEAST((v_target_days / NULLIF(v_current_days, 0)) * 30, 95);
        v_explanation := 'Based on ' || v_current_days || ' days in rare oversold zone vs ' ||
                        v_target_days::INTEGER || ' avg days in common middle zone';

    ELSIF v_signal = 'SHORT' AND p_risk >= 0.65 THEN
        -- For SHORT positions, compare to middle bands
        v_win_rate := LEAST((v_target_days / NULLIF(v_current_days, 0)) * 30, 95);
        v_explanation := 'Based on ' || v_current_days || ' days in rare overbought zone vs ' ||
                        v_target_days::INTEGER || ' avg days in common middle zone';

    ELSE
        -- NEUTRAL zone - no trade
        v_win_rate := 0;
        v_explanation := 'Neutral zone - no directional edge';
    END IF;

    -- Ensure win rate is between 0 and 95
    v_win_rate := GREATEST(0, LEAST(v_win_rate, 95));

    RETURN QUERY
    SELECT v_signal, v_win_rate, v_explanation;
END;
$$ LANGUAGE plpgsql;

-- Example usage for AVAX
SELECT * FROM calculate_win_rate('AVAX', 0.482);

-- Win rate formula for all extreme scenarios
WITH scenarios AS (
    SELECT
        symbol,
        '0.10' as test_risk,
        band_0_10 as days_in_band,
        (band_40_50 + band_50_60) / 2.0 as avg_middle_days,
        'LONG' as signal
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = 'AVAX'

    UNION ALL

    SELECT
        symbol,
        '0.90' as test_risk,
        band_90_100 as days_in_band,
        (band_40_50 + band_50_60) / 2.0 as avg_middle_days,
        'SHORT' as signal
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = 'AVAX'
)
SELECT
    signal,
    test_risk as risk,
    days_in_band,
    ROUND(avg_middle_days) as target_days,
    ROUND(LEAST((avg_middle_days / NULLIF(days_in_band, 0)) * 30, 95), 1) as win_rate_pct
FROM scenarios;