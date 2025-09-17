-- ================================================
-- COMPLETE RISKMETRIC SYSTEM - MERGED & CORRECTED
-- ================================================
-- Comprehensive risk metric system with scoring, automation, and monitoring
-- Version: 3.0.0 | Status: PRODUCTION READY

-- =====================================
-- PART 1: DATABASE TABLES & STRUCTURE
-- =====================================

-- 1.1 FIAT Risk Grid Table (25 symbols × 41 points = 1,025 rows)
CREATE TABLE IF NOT EXISTS cryptoverse_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_usd DECIMAL(20, 2) NOT NULL,
    fiat_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, fiat_risk)
);

CREATE INDEX IF NOT EXISTS idx_risk_grid_symbol ON cryptoverse_risk_grid(symbol);
CREATE INDEX IF NOT EXISTS idx_risk_grid_risk ON cryptoverse_risk_grid(fiat_risk);

-- 1.2 BTC Risk Grid Table (10 symbols × 41 points = 410 rows)
CREATE TABLE IF NOT EXISTS cryptoverse_btc_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_btc DECIMAL(20, 8) NOT NULL,
    btc_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, btc_risk)
);

CREATE INDEX IF NOT EXISTS idx_btc_risk_grid_symbol ON cryptoverse_btc_risk_grid(symbol);
CREATE INDEX IF NOT EXISTS idx_btc_risk_grid_risk ON cryptoverse_btc_risk_grid(btc_risk);

-- 1.3 Current Risk Data Table
CREATE TABLE IF NOT EXISTS cryptoverse_risk_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    price_usd DECIMAL(20, 2),
    fiat_risk DECIMAL(5, 3),
    btc_risk DECIMAL(5, 3),
    eth_risk DECIMAL(5, 3),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_data_symbol ON cryptoverse_risk_data(symbol);

-- 1.4 Time Bands Table with Scoring Columns
CREATE TABLE IF NOT EXISTS cryptoverse_risk_time_bands_v2 (
    symbol VARCHAR(10) PRIMARY KEY,
    total_days INTEGER DEFAULT 0,

    -- Days in each band
    band_0_10 INTEGER DEFAULT 0,
    band_10_20 INTEGER DEFAULT 0,
    band_20_30 INTEGER DEFAULT 0,
    band_30_40 INTEGER DEFAULT 0,
    band_40_50 INTEGER DEFAULT 0,
    band_50_60 INTEGER DEFAULT 0,
    band_60_70 INTEGER DEFAULT 0,
    band_70_80 INTEGER DEFAULT 0,
    band_80_90 INTEGER DEFAULT 0,
    band_90_100 INTEGER DEFAULT 0,

    -- Coefficients for each band
    coef_0_10 DECIMAL(4, 3) DEFAULT 1.000,
    coef_10_20 DECIMAL(4, 3) DEFAULT 1.000,
    coef_20_30 DECIMAL(4, 3) DEFAULT 1.000,
    coef_30_40 DECIMAL(4, 3) DEFAULT 1.000,
    coef_40_50 DECIMAL(4, 3) DEFAULT 1.000,
    coef_50_60 DECIMAL(4, 3) DEFAULT 1.000,
    coef_60_70 DECIMAL(4, 3) DEFAULT 1.000,
    coef_70_80 DECIMAL(4, 3) DEFAULT 1.000,
    coef_80_90 DECIMAL(4, 3) DEFAULT 1.000,
    coef_90_100 DECIMAL(4, 3) DEFAULT 1.000,

    -- Current status
    current_risk DECIMAL(5, 3),
    current_risk_band VARCHAR(10),
    last_risk_update TIMESTAMP DEFAULT NOW(),

    -- Scoring columns
    base_score INTEGER DEFAULT 0,
    total_score DECIMAL(6, 2) DEFAULT 0,
    signal_type VARCHAR(10),
    signal_strength VARCHAR(20),
    last_score_update TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_time_bands_symbol ON cryptoverse_risk_time_bands_v2(symbol);
CREATE INDEX IF NOT EXISTS idx_time_bands_risk ON cryptoverse_risk_time_bands_v2(current_risk);

-- 1.5 Daily History Table
CREATE TABLE IF NOT EXISTS risk_band_daily_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    risk_value DECIMAL(5, 3),
    risk_band VARCHAR(10),
    price_usd DECIMAL(20, 2),
    coefficient_applied DECIMAL(4, 3),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_history_symbol_date ON risk_band_daily_history(symbol, date);
CREATE INDEX IF NOT EXISTS idx_history_date ON risk_band_daily_history(date);

-- =====================================
-- PART 2: CORE CALCULATION FUNCTIONS
-- =====================================

-- 2.1 Get Risk from Price
CREATE OR REPLACE FUNCTION get_risk_at_price(
    p_symbol VARCHAR,
    p_price DECIMAL,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS DECIMAL AS $$
DECLARE
    v_lower_risk DECIMAL;
    v_upper_risk DECIMAL;
    v_lower_price DECIMAL;
    v_upper_price DECIMAL;
    v_interpolated_risk DECIMAL;
BEGIN
    IF p_type = 'fiat' THEN
        -- Get surrounding risk points
        SELECT fiat_risk, price_usd INTO v_lower_risk, v_lower_price
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol AND price_usd <= p_price
        ORDER BY price_usd DESC
        LIMIT 1;

        SELECT fiat_risk, price_usd INTO v_upper_risk, v_upper_price
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol AND price_usd >= p_price
        ORDER BY price_usd ASC
        LIMIT 1;
    ELSE -- btc
        SELECT btc_risk, price_btc INTO v_lower_risk, v_lower_price
        FROM cryptoverse_btc_risk_grid
        WHERE symbol = p_symbol AND price_btc <= p_price
        ORDER BY price_btc DESC
        LIMIT 1;

        SELECT btc_risk, price_btc INTO v_upper_risk, v_upper_price
        FROM cryptoverse_btc_risk_grid
        WHERE symbol = p_symbol AND price_btc >= p_price
        ORDER BY price_btc ASC
        LIMIT 1;
    END IF;

    -- Handle edge cases
    IF v_lower_risk IS NULL THEN RETURN 0.000; END IF;
    IF v_upper_risk IS NULL THEN RETURN 1.000; END IF;
    IF v_lower_price = v_upper_price THEN RETURN v_lower_risk; END IF;

    -- Linear interpolation
    v_interpolated_risk := v_lower_risk +
        (v_upper_risk - v_lower_risk) *
        ((p_price - v_lower_price) / (v_upper_price - v_lower_price));

    RETURN ROUND(v_interpolated_risk, 3);
END;
$$ LANGUAGE plpgsql;

-- 2.2 Get Price from Risk
CREATE OR REPLACE FUNCTION get_price_at_risk(
    p_symbol VARCHAR,
    p_risk DECIMAL,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS DECIMAL AS $$
DECLARE
    v_lower_risk DECIMAL;
    v_upper_risk DECIMAL;
    v_lower_price DECIMAL;
    v_upper_price DECIMAL;
    v_interpolated_price DECIMAL;
BEGIN
    IF p_type = 'fiat' THEN
        SELECT fiat_risk, price_usd INTO v_lower_risk, v_lower_price
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol AND fiat_risk <= p_risk
        ORDER BY fiat_risk DESC
        LIMIT 1;

        SELECT fiat_risk, price_usd INTO v_upper_risk, v_upper_price
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol AND fiat_risk >= p_risk
        ORDER BY fiat_risk ASC
        LIMIT 1;
    ELSE
        SELECT btc_risk, price_btc INTO v_lower_risk, v_lower_price
        FROM cryptoverse_btc_risk_grid
        WHERE symbol = p_symbol AND btc_risk <= p_risk
        ORDER BY btc_risk DESC
        LIMIT 1;

        SELECT btc_risk, price_btc INTO v_upper_risk, v_upper_price
        FROM cryptoverse_btc_risk_grid
        WHERE symbol = p_symbol AND btc_risk >= p_risk
        ORDER BY btc_risk ASC
        LIMIT 1;
    END IF;

    IF v_lower_risk = v_upper_risk THEN
        RETURN v_lower_price;
    END IF;

    v_interpolated_price := v_lower_price +
        (v_upper_price - v_lower_price) *
        ((p_risk - v_lower_risk) / (v_upper_risk - v_lower_risk));

    RETURN ROUND(v_interpolated_price, 2);
END;
$$ LANGUAGE plpgsql;

-- 2.3 Get Current Risk Band
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

-- =====================================
-- PART 3: COEFFICIENT CALCULATIONS
-- =====================================

-- 3.1 Recalculate Trading Coefficients
CREATE OR REPLACE FUNCTION recalculate_trading_coefficients()
RETURNS VOID AS $$
DECLARE
    r RECORD;
    min_days INTEGER;
    max_days INTEGER;
    days_array INTEGER[];
    coef DECIMAL;
BEGIN
    FOR r IN SELECT * FROM cryptoverse_risk_time_bands_v2
    LOOP
        days_array := ARRAY[
            CASE WHEN r.band_0_10 > 0 THEN r.band_0_10 ELSE NULL END,
            CASE WHEN r.band_10_20 > 0 THEN r.band_10_20 ELSE NULL END,
            CASE WHEN r.band_20_30 > 0 THEN r.band_20_30 ELSE NULL END,
            CASE WHEN r.band_30_40 > 0 THEN r.band_30_40 ELSE NULL END,
            CASE WHEN r.band_40_50 > 0 THEN r.band_40_50 ELSE NULL END,
            CASE WHEN r.band_50_60 > 0 THEN r.band_50_60 ELSE NULL END,
            CASE WHEN r.band_60_70 > 0 THEN r.band_60_70 ELSE NULL END,
            CASE WHEN r.band_70_80 > 0 THEN r.band_70_80 ELSE NULL END,
            CASE WHEN r.band_80_90 > 0 THEN r.band_80_90 ELSE NULL END,
            CASE WHEN r.band_90_100 > 0 THEN r.band_90_100 ELSE NULL END
        ];

        days_array := array_remove(days_array, NULL);

        IF array_length(days_array, 1) > 0 THEN
            min_days := (SELECT MIN(d) FROM unnest(days_array) AS d);
            max_days := (SELECT MAX(d) FROM unnest(days_array) AS d);

            IF max_days = min_days THEN
                UPDATE cryptoverse_risk_time_bands_v2
                SET coef_0_10 = 1.000, coef_10_20 = 1.000, coef_20_30 = 1.000,
                    coef_30_40 = 1.000, coef_40_50 = 1.000, coef_50_60 = 1.000,
                    coef_60_70 = 1.000, coef_70_80 = 1.000, coef_80_90 = 1.000,
                    coef_90_100 = 1.000
                WHERE symbol = r.symbol;
            ELSE
                -- Calculate coefficients for each band
                UPDATE cryptoverse_risk_time_bands_v2
                SET
                    coef_0_10 = CASE
                        WHEN band_0_10 > 0 THEN
                            ROUND(1.600 - ((band_0_10 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_10_20 = CASE
                        WHEN band_10_20 > 0 THEN
                            ROUND(1.600 - ((band_10_20 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_20_30 = CASE
                        WHEN band_20_30 > 0 THEN
                            ROUND(1.600 - ((band_20_30 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_30_40 = CASE
                        WHEN band_30_40 > 0 THEN
                            ROUND(1.600 - ((band_30_40 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_40_50 = CASE
                        WHEN band_40_50 > 0 THEN
                            ROUND(1.600 - ((band_40_50 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_50_60 = CASE
                        WHEN band_50_60 > 0 THEN
                            ROUND(1.600 - ((band_50_60 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_60_70 = CASE
                        WHEN band_60_70 > 0 THEN
                            ROUND(1.600 - ((band_60_70 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_70_80 = CASE
                        WHEN band_70_80 > 0 THEN
                            ROUND(1.600 - ((band_70_80 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_80_90 = CASE
                        WHEN band_80_90 > 0 THEN
                            ROUND(1.600 - ((band_80_90 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END,
                    coef_90_100 = CASE
                        WHEN band_90_100 > 0 THEN
                            ROUND(1.600 - ((band_90_100 - min_days)::DECIMAL * 0.600 / (max_days - min_days)), 3)
                        ELSE 1.000
                    END
                WHERE symbol = r.symbol;
            END IF;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- PART 4: SCORING SYSTEM (CORRECTED)
-- =====================================

-- 4.1 Calculate Base Score
CREATE OR REPLACE FUNCTION calculate_base_score(p_risk DECIMAL)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE
        -- HIGHEST SCORES (100 points) - Extreme zones
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

-- 4.2 Determine Signal Type (CORRECTED)
CREATE OR REPLACE FUNCTION determine_signal_type(p_risk DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE
        -- LONG signals in LOW risk zones (oversold = buy opportunity)
        WHEN p_risk <= 0.15 THEN 'LONG'     -- Extreme oversold
        WHEN p_risk <= 0.25 THEN 'LONG'     -- Strong oversold
        WHEN p_risk <= 0.35 THEN 'LONG'     -- Moderate oversold

        -- SHORT signals in HIGH risk zones (overbought = sell opportunity)
        WHEN p_risk >= 0.85 THEN 'SHORT'    -- Extreme overbought
        WHEN p_risk >= 0.75 THEN 'SHORT'    -- Strong overbought
        WHEN p_risk >= 0.65 THEN 'SHORT'    -- Moderate overbought

        -- NEUTRAL in middle zone
        ELSE 'NEUTRAL'                      -- Middle zone
    END;
END;
$$ LANGUAGE plpgsql;

-- 4.3 Master Scoring Function
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
    v_base_score := calculate_base_score(p_risk);
    v_total_score := v_base_score * p_coefficient;
    v_signal_type := determine_signal_type(p_risk);

    v_signal_strength := CASE
        WHEN v_total_score >= 150 THEN 'STRONGEST'
        WHEN v_total_score >= 120 THEN 'STRONG'
        WHEN v_total_score >= 90 THEN 'MODERATE'
        ELSE 'WEAK'
    END;

    v_action := CASE
        -- LONG SIGNALS (Low risk = Oversold = Buy)
        WHEN p_risk <= 0.15 AND v_signal_strength = 'STRONGEST' THEN
            '🔥🔥🔥 STRONGEST BUY - Extreme oversold (0-15%) + Very rare!'
        WHEN p_risk <= 0.15 AND v_signal_strength = 'STRONG' THEN
            '🔥🔥 STRONG BUY - Extreme oversold (0-15%) + Rare'
        WHEN p_risk <= 0.25 AND v_signal_strength = 'STRONG' THEN
            '🔥 STRONG BUY - Strong oversold (15-25%) + Rare'
        WHEN p_risk <= 0.35 AND v_signal_strength = 'MODERATE' THEN
            '✅ BUY - Moderate oversold (25-35%)'

        -- SHORT SIGNALS (High risk = Overbought = Sell)
        WHEN p_risk >= 0.85 AND v_signal_strength = 'STRONGEST' THEN
            '⚠️⚠️⚠️ STRONGEST SELL - Extreme overbought (85-100%) + Very rare!'
        WHEN p_risk >= 0.85 AND v_signal_strength = 'STRONG' THEN
            '⚠️⚠️ STRONG SELL - Extreme overbought (85-100%) + Rare'
        WHEN p_risk >= 0.75 AND v_signal_strength = 'STRONG' THEN
            '⚠️ STRONG SELL - Strong overbought (75-85%) + Rare'
        WHEN p_risk >= 0.65 AND v_signal_strength = 'MODERATE' THEN
            '📉 SELL - Moderate overbought (65-75%)'

        -- NEUTRAL
        WHEN v_signal_type = 'NEUTRAL' THEN
            '⏸️ HOLD - Neutral zone (35-65%)'
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

-- 4.4 Update All Scores
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
        IF r.current_risk IS NULL THEN
            CONTINUE;
        END IF;

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

        v_base_score := calculate_base_score(r.current_risk);
        v_total_score := v_base_score * v_coefficient;
        v_signal_type := determine_signal_type(r.current_risk);

        v_signal_strength := CASE
            WHEN v_total_score >= 150 THEN 'STRONGEST'
            WHEN v_total_score >= 120 THEN 'STRONG'
            WHEN v_total_score >= 90 THEN 'MODERATE'
            ELSE 'WEAK'
        END;

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

-- =====================================
-- PART 5: AUTOMATION FUNCTIONS
-- =====================================

-- 5.1 Update Daily Risk Bands
CREATE OR REPLACE FUNCTION update_daily_risk_bands()
RETURNS VOID AS $$
DECLARE
    r RECORD;
    v_band VARCHAR;
BEGIN
    FOR r IN SELECT * FROM cryptoverse_risk_time_bands_v2
    WHERE current_risk IS NOT NULL
    LOOP
        v_band := get_current_risk_band(r.current_risk);

        -- Log to history
        INSERT INTO risk_band_daily_history (symbol, date, risk_value, risk_band, price_usd)
        VALUES (r.symbol, CURRENT_DATE, r.current_risk, v_band,
               (SELECT price_usd FROM cryptoverse_risk_data WHERE symbol = r.symbol))
        ON CONFLICT (symbol, date) DO UPDATE
        SET risk_value = EXCLUDED.risk_value,
            risk_band = EXCLUDED.risk_band,
            price_usd = EXCLUDED.price_usd;

        -- Update band days
        UPDATE cryptoverse_risk_time_bands_v2
        SET
            total_days = total_days + 1,
            band_0_10 = CASE WHEN v_band = '0.0-0.1' THEN band_0_10 + 1 ELSE band_0_10 END,
            band_10_20 = CASE WHEN v_band = '0.1-0.2' THEN band_10_20 + 1 ELSE band_10_20 END,
            band_20_30 = CASE WHEN v_band = '0.2-0.3' THEN band_20_30 + 1 ELSE band_20_30 END,
            band_30_40 = CASE WHEN v_band = '0.3-0.4' THEN band_30_40 + 1 ELSE band_30_40 END,
            band_40_50 = CASE WHEN v_band = '0.4-0.5' THEN band_40_50 + 1 ELSE band_40_50 END,
            band_50_60 = CASE WHEN v_band = '0.5-0.6' THEN band_50_60 + 1 ELSE band_50_60 END,
            band_60_70 = CASE WHEN v_band = '0.6-0.7' THEN band_60_70 + 1 ELSE band_60_70 END,
            band_70_80 = CASE WHEN v_band = '0.7-0.8' THEN band_70_80 + 1 ELSE band_70_80 END,
            band_80_90 = CASE WHEN v_band = '0.8-0.9' THEN band_80_90 + 1 ELSE band_80_90 END,
            band_90_100 = CASE WHEN v_band = '0.9-1.0' THEN band_90_100 + 1 ELSE band_90_100 END,
            last_risk_update = NOW()
        WHERE symbol = r.symbol;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 5.2 Master Daily Update
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
    -- Update daily risk bands
    PERFORM update_daily_risk_bands();

    -- Count updated symbols
    SELECT COUNT(*) INTO updated_count
    FROM cryptoverse_risk_time_bands_v2
    WHERE DATE(last_risk_update) = CURRENT_DATE;

    -- Recalculate coefficients
    PERFORM recalculate_trading_coefficients();

    -- Update all scores
    PERFORM update_all_riskmetric_scores();

    RETURN QUERY
    SELECT
        'Daily update completed'::TEXT,
        updated_count,
        TRUE,
        TRUE;
END;
$$ LANGUAGE plpgsql;

-- 5.3 Update from Binance Prices
CREATE OR REPLACE FUNCTION update_risk_from_binance()
RETURNS TABLE(
    symbol VARCHAR,
    price DECIMAL,
    risk DECIMAL,
    status TEXT
) AS $$
DECLARE
    r RECORD;
    v_price DECIMAL;
    v_risk DECIMAL;
    v_band VARCHAR;
BEGIN
    FOR r IN
        SELECT DISTINCT symbol FROM cryptoverse_risk_grid
    LOOP
        -- This would call Binance API - simplified for SQL
        -- In production, use external script or pg_cron with http extension

        -- Get current price from risk_data table
        SELECT price_usd INTO v_price
        FROM cryptoverse_risk_data
        WHERE symbol = r.symbol;

        IF v_price IS NOT NULL THEN
            v_risk := get_risk_at_price(r.symbol, v_price, 'fiat');
            v_band := get_current_risk_band(v_risk);

            -- Update current risk
            UPDATE cryptoverse_risk_time_bands_v2
            SET current_risk = v_risk,
                current_risk_band = v_band
            WHERE symbol = r.symbol;

            -- Update risk data
            UPDATE cryptoverse_risk_data
            SET fiat_risk = v_risk,
                last_updated = NOW()
            WHERE symbol = r.symbol;

            RETURN QUERY
            SELECT r.symbol, v_price, v_risk, 'Updated'::TEXT;
        END IF;
    END LOOP;

    -- Trigger score updates
    PERFORM update_all_riskmetric_scores();
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- PART 6: VIEWS & MONITORING
-- =====================================

-- 6.1 Main Scoring View
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

-- 6.2 Top Trading Opportunities
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
WHERE (current_risk <= 0.35 OR current_risk >= 0.65)
AND signal_strength IN ('STRONGEST', 'STRONG', 'MODERATE')
ORDER BY total_score DESC
LIMIT 10;

-- 6.3 Trading Alerts
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

-- =====================================
-- PART 7: AUTOMATION SETUP
-- =====================================

-- 7.1 Triggers
DROP TRIGGER IF EXISTS auto_update_scores ON cryptoverse_risk_time_bands_v2;
CREATE TRIGGER auto_update_scores
AFTER UPDATE OF current_risk, current_risk_band ON cryptoverse_risk_time_bands_v2
FOR EACH ROW
EXECUTE FUNCTION trigger_score_update();

CREATE OR REPLACE FUNCTION trigger_score_update()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_risk IS DISTINCT FROM OLD.current_risk OR
       NEW.current_risk_band IS DISTINCT FROM OLD.current_risk_band THEN
        PERFORM update_all_riskmetric_scores();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7.2 Cron Jobs (Enable pg_cron first)
-- Daily update at midnight UTC
SELECT cron.schedule('daily-risk-band-update', '0 0 * * *',
    $$SELECT daily_risk_update_master();$$);

-- Hourly price update
SELECT cron.schedule('hourly-binance-risk-update', '0 * * * *',
    $$SELECT update_risk_from_binance();$$);

-- =====================================
-- PART 8: INITIALIZATION
-- =====================================

-- Initialize all scores
SELECT update_all_riskmetric_scores();

-- Verify system
SELECT
    '✅ RISKMETRIC SYSTEM READY' as status,
    COUNT(*) as total_symbols,
    COUNT(CASE WHEN current_risk IS NOT NULL THEN 1 END) as symbols_with_risk,
    COUNT(CASE WHEN total_score > 0 THEN 1 END) as symbols_with_scores
FROM cryptoverse_risk_time_bands_v2;

-- =====================================
-- END OF COMPLETE RISKMETRIC SYSTEM
-- ====================================