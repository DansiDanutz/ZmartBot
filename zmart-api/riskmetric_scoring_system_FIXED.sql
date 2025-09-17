-- RISKMETRIC SCORING SYSTEM - CORRECTED VERSION
-- ==============================================
-- Fixed signal logic based on actual scoring zones
-- Base Score × Coefficient = Total Score

-- STEP 1: Add scoring columns to risk_time_bands table
ALTER TABLE cryptoverse_risk_time_bands_v2
ADD COLUMN IF NOT EXISTS base_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_score DECIMAL(6, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS signal_type VARCHAR(10), -- 'LONG', 'SHORT', or 'NEUTRAL'
ADD COLUMN IF NOT EXISTS signal_strength VARCHAR(20), -- 'STRONGEST', 'STRONG', 'MODERATE', 'WEAK'
ADD COLUMN IF NOT EXISTS last_score_update TIMESTAMP;

-- STEP 2: Function to calculate base score from risk value
-- CORRECT SCORING BASED ON YOUR REQUIREMENTS
CREATE OR REPLACE FUNCTION calculate_base_score(p_risk DECIMAL)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE
        -- HIGHEST SCORES (100 points) - Extreme zones ONLY
        WHEN p_risk >= 0.00 AND p_risk <= 0.15 THEN 100  -- Extreme oversold (BUY zone)
        WHEN p_risk >= 0.85 AND p_risk <= 1.00 THEN 100  -- Extreme overbought (SELL zone)

        -- HIGH SCORES (80 points) - Strong zones
        WHEN p_risk > 0.15 AND p_risk <= 0.25 THEN 80   -- Strong oversold
        WHEN p_risk >= 0.75 AND p_risk < 0.85 THEN 80   -- Strong overbought

        -- MODERATE SCORES (60 points) - Moderate zones
        WHEN p_risk > 0.25 AND p_risk <= 0.35 THEN 60   -- Moderate oversold
        WHEN p_risk >= 0.65 AND p_risk < 0.75 THEN 60   -- Moderate overbought

        -- LOW SCORES (50 points) - Neutral zone
        WHEN p_risk > 0.35 AND p_risk < 0.65 THEN 50    -- Middle neutral zone

        ELSE 50 -- Default
    END;
END;
$$ LANGUAGE plpgsql;

-- STEP 3: Function to determine signal type - CORRECTED LOGIC
CREATE OR REPLACE FUNCTION determine_signal_type(p_risk DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE
        -- LONG signals in LOW risk zones (oversold = buy opportunity)
        WHEN p_risk <= 0.15 THEN 'LONG'     -- Extreme oversold - STRONGEST BUY
        WHEN p_risk <= 0.25 THEN 'LONG'     -- Strong oversold - STRONG BUY
        WHEN p_risk <= 0.35 THEN 'LONG'     -- Moderate oversold - BUY

        -- SHORT signals in HIGH risk zones (overbought = sell opportunity)
        WHEN p_risk >= 0.85 THEN 'SHORT'    -- Extreme overbought - STRONGEST SELL
        WHEN p_risk >= 0.75 THEN 'SHORT'    -- Strong overbought - STRONG SELL
        WHEN p_risk >= 0.65 THEN 'SHORT'    -- Moderate overbought - SELL

        -- NEUTRAL in middle zone
        ELSE 'NEUTRAL'                      -- Middle zone - HOLD
    END;
END;
$$ LANGUAGE plpgsql;

-- STEP 4: Master scoring function with correct signal logic
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

    -- Determine signal strength based on total score AND zone
    v_signal_strength := CASE
        WHEN v_total_score >= 150 THEN 'STRONGEST'  -- 100 × 1.50+
        WHEN v_total_score >= 120 THEN 'STRONG'     -- 80 × 1.50 or 100 × 1.20
        WHEN v_total_score >= 90 THEN 'MODERATE'    -- 60 × 1.50
        ELSE 'WEAK'                                 -- Lower scores
    END;

    -- Generate action recommendation with CORRECT logic
    v_action := CASE
        -- LONG SIGNALS (Low risk = Oversold = Buy opportunity)
        WHEN p_risk <= 0.15 AND v_signal_strength = 'STRONGEST' THEN
            '🔥🔥🔥 STRONGEST BUY SIGNAL - Extreme oversold (0-15%) + Very rare condition!'
        WHEN p_risk <= 0.15 AND v_signal_strength = 'STRONG' THEN
            '🔥🔥 STRONG BUY - Extreme oversold (0-15%) + Rare condition'
        WHEN p_risk <= 0.25 AND v_signal_strength = 'STRONG' THEN
            '🔥 STRONG BUY - Strong oversold (15-25%) + Rare condition'
        WHEN p_risk <= 0.35 AND v_signal_strength = 'MODERATE' THEN
            '✅ BUY - Moderate oversold (25-35%) opportunity'

        -- SHORT SIGNALS (High risk = Overbought = Sell opportunity)
        WHEN p_risk >= 0.85 AND v_signal_strength = 'STRONGEST' THEN
            '⚠️⚠️⚠️ STRONGEST SELL SIGNAL - Extreme overbought (85-100%) + Very rare condition!'
        WHEN p_risk >= 0.85 AND v_signal_strength = 'STRONG' THEN
            '⚠️⚠️ STRONG SELL - Extreme overbought (85-100%) + Rare condition'
        WHEN p_risk >= 0.75 AND v_signal_strength = 'STRONG' THEN
            '⚠️ STRONG SELL - Strong overbought (75-85%) + Rare condition'
        WHEN p_risk >= 0.65 AND v_signal_strength = 'MODERATE' THEN
            '📉 SELL - Moderate overbought (65-75%) opportunity'

        -- NEUTRAL ZONE
        WHEN v_signal_type = 'NEUTRAL' THEN
            '⏸️ HOLD - Neutral zone (35-65%) - Wait for better entry/exit'

        -- WEAK SIGNALS
        ELSE
            '👀 MONITOR - Weak signal, continue watching'
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

-- STEP 8: Create comprehensive scoring view with CORRECTED logic
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
        -- CORRECTED ACTION LOGIC
        WHEN rtb.current_risk <= 0.15 AND rtb.signal_strength = 'STRONGEST' THEN
            '🔥🔥🔥 STRONGEST BUY (0-15%)'
        WHEN rtb.current_risk <= 0.15 AND rtb.signal_strength = 'STRONG' THEN
            '🔥🔥 STRONG BUY (0-15%)'
        WHEN rtb.current_risk <= 0.25 AND rtb.signal_strength = 'STRONG' THEN
            '🔥 STRONG BUY (15-25%)'
        WHEN rtb.current_risk <= 0.35 AND rtb.signal_type = 'LONG' THEN
            '✅ BUY (25-35%)'

        WHEN rtb.current_risk >= 0.85 AND rtb.signal_strength = 'STRONGEST' THEN
            '⚠️⚠️⚠️ STRONGEST SELL (85-100%)'
        WHEN rtb.current_risk >= 0.85 AND rtb.signal_strength = 'STRONG' THEN
            '⚠️⚠️ STRONG SELL (85-100%)'
        WHEN rtb.current_risk >= 0.75 AND rtb.signal_strength = 'STRONG' THEN
            '⚠️ STRONG SELL (75-85%)'
        WHEN rtb.current_risk >= 0.65 AND rtb.signal_type = 'SHORT' THEN
            '📉 SELL (65-75%)'

        WHEN rtb.signal_type = 'NEUTRAL' THEN
            '⏸️ HOLD (35-65%)'
        ELSE
            '👀 MONITOR'
    END as action,
    crd.price_usd as current_price,
    rtb.last_score_update
FROM cryptoverse_risk_time_bands_v2 rtb
LEFT JOIN cryptoverse_risk_data crd ON rtb.symbol = crd.symbol
ORDER BY rtb.total_score DESC;

-- STEP 9: Top opportunities view - focus on EXTREME zones
CREATE OR REPLACE VIEW v_top_trading_opportunities AS
SELECT
    symbol,
    current_price,
    current_risk,
    CASE
        WHEN current_risk <= 0.15 THEN 'EXTREME OVERSOLD (0-15%)'
        WHEN current_risk <= 0.25 THEN 'STRONG OVERSOLD (15-25%)'
        WHEN current_risk <= 0.35 THEN 'MODERATE OVERSOLD (25-35%)'
        WHEN current_risk >= 0.85 THEN 'EXTREME OVERBOUGHT (85-100%)'
        WHEN current_risk >= 0.75 THEN 'STRONG OVERBOUGHT (75-85%)'
        WHEN current_risk >= 0.65 THEN 'MODERATE OVERBOUGHT (65-75%)'
        ELSE 'NEUTRAL (35-65%)'
    END as zone,
    base_score,
    coefficient,
    total_score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE (current_risk <= 0.35 OR current_risk >= 0.65)  -- Only show actionable zones
AND signal_strength IN ('STRONGEST', 'STRONG', 'MODERATE')
ORDER BY total_score DESC
LIMIT 10;

-- STEP 10: Initialize scores for all symbols
SELECT update_all_riskmetric_scores();

-- VERIFICATION with CORRECT expectations
SELECT
    '📊 SCORING VERIFICATION' as check_type,
    symbol,
    ROUND(current_risk, 3) as risk,
    CASE
        WHEN current_risk <= 0.15 THEN 'Extreme Low (0-15%)'
        WHEN current_risk >= 0.85 THEN 'Extreme High (85-100%)'
        WHEN current_risk BETWEEN 0.35 AND 0.65 THEN 'Neutral (35-65%)'
        ELSE 'Other'
    END as risk_zone,
    base_score,
    coefficient,
    total_score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE symbol IN ('BTC', 'ETH', 'SOL')
ORDER BY total_score DESC;