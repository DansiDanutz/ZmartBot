-- RISKMETRIC SCORING SYSTEM
-- ==========================
-- Complete automated scoring system for trading signals
-- Base Score × Coefficient = Total Score

-- STEP 1: Add scoring columns to risk_time_bands table
ALTER TABLE cryptoverse_risk_time_bands_v2
ADD COLUMN IF NOT EXISTS base_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_score DECIMAL(6, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS signal_type VARCHAR(10), -- 'LONG' or 'SHORT'
ADD COLUMN IF NOT EXISTS signal_strength VARCHAR(20), -- 'STRONGEST', 'STRONG', 'MODERATE', 'WEAK'
ADD COLUMN IF NOT EXISTS last_score_update TIMESTAMP;

-- STEP 2: Function to calculate base score from risk value
CREATE OR REPLACE FUNCTION calculate_base_score(p_risk DECIMAL)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE
        -- HIGHEST SCORES (100 points) - Extreme zones
        WHEN p_risk >= 0.00 AND p_risk <= 0.15 THEN 100  -- Extreme oversold
        WHEN p_risk >= 0.85 AND p_risk <= 1.00 THEN 100  -- Extreme overbought

        -- HIGH SCORES (80 points) - Strong zones
        WHEN p_risk > 0.15 AND p_risk <= 0.25 THEN 80   -- Strong accumulation
        WHEN p_risk >= 0.75 AND p_risk < 0.85 THEN 80   -- Strong distribution

        -- MODERATE SCORES (60 points) - Normal zones
        WHEN p_risk > 0.25 AND p_risk <= 0.35 THEN 60   -- Moderate accumulation
        WHEN p_risk >= 0.65 AND p_risk < 0.75 THEN 60   -- Moderate distribution

        -- LOW SCORES (50 points) - Neutral zone
        WHEN p_risk > 0.35 AND p_risk < 0.65 THEN 50    -- Transition/neutral

        ELSE 50 -- Default
    END;
END;
$$ LANGUAGE plpgsql;

-- STEP 3: Function to determine signal type
CREATE OR REPLACE FUNCTION determine_signal_type(p_risk DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE
        WHEN p_risk <= 0.35 THEN 'LONG'   -- Accumulation zones
        WHEN p_risk >= 0.65 THEN 'SHORT'  -- Distribution zones
        ELSE 'NEUTRAL'                    -- Transition zone
    END;
END;
$$ LANGUAGE plpgsql;

-- STEP 4: Master scoring function
CREATE OR REPLACE FUNCTION calculate_riskmetric_score(
    p_symbol VARCHAR,
    p_risk DECIMAL,
    p_coefficient DECIMAL
)
RETURNS TABLE(
    base_score INTEGER,
    coefficient DECIMAL,
    total_score DECIMAL,
    signal_type VARCHAR,
    signal_strength VARCHAR,
    action_recommendation TEXT
) AS $$
DECLARE
    v_base_score INTEGER;
    v_total_score DECIMAL;
    v_signal_type VARCHAR;
    v_signal_strength VARCHAR;
    v_action TEXT;
BEGIN
    -- Calculate base score
    v_base_score := calculate_base_score(p_risk);

    -- Calculate total score
    v_total_score := v_base_score * p_coefficient;

    -- Determine signal type
    v_signal_type := determine_signal_type(p_risk);

    -- Determine signal strength based on total score
    v_signal_strength := CASE
        WHEN v_total_score >= 150 THEN 'STRONGEST'  -- 100 × 1.50+
        WHEN v_total_score >= 120 THEN 'STRONG'     -- 80 × 1.50 or 100 × 1.20
        WHEN v_total_score >= 90 THEN 'MODERATE'    -- 60 × 1.50
        ELSE 'WEAK'                                 -- Lower scores
    END;

    -- Generate action recommendation
    v_action := CASE
        WHEN v_signal_type = 'LONG' AND v_signal_strength = 'STRONGEST' THEN
            '🔥🔥🔥 STRONGEST BUY SIGNAL - Extreme oversold + Very rare condition!'
        WHEN v_signal_type = 'SHORT' AND v_signal_strength = 'STRONGEST' THEN
            '⚠️⚠️⚠️ STRONGEST SELL SIGNAL - Extreme overbought + Very rare condition!'
        WHEN v_signal_type = 'LONG' AND v_signal_strength = 'STRONG' THEN
            '🔥🔥 STRONG BUY - Oversold + Rare condition'
        WHEN v_signal_type = 'SHORT' AND v_signal_strength = 'STRONG' THEN
            '⚠️⚠️ STRONG SELL - Overbought + Rare condition'
        WHEN v_signal_type = 'LONG' AND v_signal_strength = 'MODERATE' THEN
            '✅ BUY - Good accumulation opportunity'
        WHEN v_signal_type = 'SHORT' AND v_signal_strength = 'MODERATE' THEN
            '📉 SELL - Good distribution opportunity'
        WHEN v_signal_type = 'NEUTRAL' THEN
            '⏸️ HOLD - Wait for better entry/exit'
        ELSE
            '👀 MONITOR - Weak signal'
    END;

    RETURN QUERY
    SELECT
        v_base_score,
        p_coefficient,
        v_total_score,
        v_signal_type,
        v_signal_strength,
        v_action;
END;
$$ LANGUAGE plpgsql;

-- STEP 5: Update all scores automatically
CREATE OR REPLACE FUNCTION update_all_riskmetric_scores()
RETURNS VOID AS $$
DECLARE
    r RECORD;
    v_coefficient DECIMAL;
    v_base_score INTEGER;
    v_total_score DECIMAL;
    v_signal_type VARCHAR;
    v_signal_strength VARCHAR;
BEGIN
    FOR r IN SELECT * FROM cryptoverse_risk_time_bands_v2
    LOOP
        -- Skip if no current risk
        IF r.current_risk IS NULL THEN
            CONTINUE;
        END IF;

        -- Get the appropriate coefficient based on current risk band
        v_coefficient := CASE r.current_risk_band
            WHEN '0.0-0.1' THEN r.coef_0_10
            WHEN '0.1-0.2' THEN r.coef_10_20
            WHEN '0.2-0.3' THEN r.coef_20_30
            WHEN '0.3-0.4' THEN r.coef_30_40
            WHEN '0.4-0.5' THEN r.coef_40_50
            WHEN '0.5-0.6' THEN r.coef_50_60
            WHEN '0.6-0.7' THEN r.coef_60_70
            WHEN '0.7-0.8' THEN r.coef_70_80
            WHEN '0.8-0.9' THEN r.coef_80_90
            WHEN '0.9-1.0' THEN r.coef_90_100
            ELSE 1.0
        END;

        -- Calculate scores
        v_base_score := calculate_base_score(r.current_risk);
        v_total_score := v_base_score * v_coefficient;
        v_signal_type := determine_signal_type(r.current_risk);

        -- Determine signal strength
        v_signal_strength := CASE
            WHEN v_total_score >= 150 THEN 'STRONGEST'
            WHEN v_total_score >= 120 THEN 'STRONG'
            WHEN v_total_score >= 90 THEN 'MODERATE'
            ELSE 'WEAK'
        END;

        -- Update the record
        UPDATE cryptoverse_risk_time_bands_v2
        SET
            base_score = v_base_score,
            total_score = v_total_score,
            signal_type = v_signal_type,
            signal_strength = v_signal_strength,
            last_score_update = NOW()
        WHERE symbol = r.symbol;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- STEP 6: Trigger to auto-update scores when risk changes
CREATE OR REPLACE FUNCTION trigger_score_update()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_risk IS DISTINCT FROM OLD.current_risk OR
       NEW.current_risk_band IS DISTINCT FROM OLD.current_risk_band THEN

        -- Recalculate scores for this symbol
        PERFORM update_all_riskmetric_scores();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_update_scores ON cryptoverse_risk_time_bands_v2;
CREATE TRIGGER auto_update_scores
AFTER UPDATE OF current_risk, current_risk_band ON cryptoverse_risk_time_bands_v2
FOR EACH ROW
EXECUTE FUNCTION trigger_score_update();

-- STEP 7: Enhanced daily update to include scoring
DROP FUNCTION IF EXISTS daily_risk_update_master();
CREATE OR REPLACE FUNCTION daily_risk_update_master()
RETURNS TABLE(
    status TEXT,
    symbols_updated INTEGER,
    coefficients_recalculated BOOLEAN,
    scores_updated BOOLEAN
) AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    -- Step 1: Update daily risk bands
    PERFORM update_daily_risk_bands();

    -- Count updated symbols
    SELECT COUNT(*) INTO updated_count
    FROM cryptoverse_risk_time_bands_v2 rtb
    WHERE DATE(rtb.last_risk_update) = CURRENT_DATE;

    -- Step 2: Recalculate coefficients
    PERFORM recalculate_trading_coefficients();

    -- Step 3: Update all scores
    PERFORM update_all_riskmetric_scores();

    -- Return status
    RETURN QUERY
    SELECT
        'Daily update completed'::TEXT as status,
        updated_count as symbols_updated,
        TRUE as coefficients_recalculated,
        TRUE as scores_updated;
END;
$$ LANGUAGE plpgsql;

-- STEP 8: Create comprehensive scoring view
CREATE OR REPLACE VIEW v_riskmetric_scores AS
SELECT
    rtb.symbol,
    rtb.current_risk,
    rtb.current_risk_band,
    rtb.base_score,
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
    rtb.total_score,
    rtb.signal_type,
    rtb.signal_strength,
    CASE
        WHEN rtb.signal_type = 'LONG' AND rtb.signal_strength = 'STRONGEST' THEN
            '🔥🔥🔥 STRONGEST BUY'
        WHEN rtb.signal_type = 'SHORT' AND rtb.signal_strength = 'STRONGEST' THEN
            '⚠️⚠️⚠️ STRONGEST SELL'
        WHEN rtb.signal_type = 'LONG' AND rtb.signal_strength = 'STRONG' THEN
            '🔥🔥 STRONG BUY'
        WHEN rtb.signal_type = 'SHORT' AND rtb.signal_strength = 'STRONG' THEN
            '⚠️⚠️ STRONG SELL'
        WHEN rtb.signal_type = 'LONG' AND rtb.signal_strength = 'MODERATE' THEN
            '✅ BUY'
        WHEN rtb.signal_type = 'SHORT' AND rtb.signal_strength = 'MODERATE' THEN
            '📉 SELL'
        WHEN rtb.signal_type = 'NEUTRAL' THEN
            '⏸️ HOLD'
        ELSE
            '👀 MONITOR'
    END as action,
    crd.price_usd as current_price,
    rtb.last_score_update
FROM cryptoverse_risk_time_bands_v2 rtb
LEFT JOIN cryptoverse_risk_data crd ON rtb.symbol = crd.symbol
ORDER BY rtb.total_score DESC;

-- STEP 9: Top opportunities view
CREATE OR REPLACE VIEW v_top_trading_opportunities AS
SELECT
    symbol,
    current_price,
    current_risk,
    base_score,
    coefficient,
    total_score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE signal_strength IN ('STRONGEST', 'STRONG')
AND signal_type != 'NEUTRAL'
ORDER BY total_score DESC
LIMIT 10;

-- STEP 10: Initialize scores for all symbols
SELECT update_all_riskmetric_scores();

-- VERIFICATION
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