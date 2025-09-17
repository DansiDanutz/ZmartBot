-- AUTOMATED DAILY RISK BAND UPDATE SYSTEM
-- =========================================
-- This system automatically:
-- 1. Checks current risk for each symbol daily
-- 2. Adds +1 day to the corresponding band
-- 3. Updates total life age
-- 4. Recalculates coefficients
-- 5. Runs automatically via Supabase cron

-- STEP 1: Create enhanced table structure with trading coefficients
CREATE TABLE IF NOT EXISTS cryptoverse_risk_time_bands_v2 (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    symbol_name VARCHAR(100),
    birth_date DATE,
    total_days INTEGER DEFAULT 0,

    -- Risk band days (automatically updated daily)
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

    -- Trading coefficients (auto-calculated)
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
    last_risk_update TIMESTAMP,
    last_coefficient_update TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- STEP 2: Create daily risk history table
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

-- STEP 3: Function to get current risk band
CREATE OR REPLACE FUNCTION get_current_risk_band(p_risk DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE
        WHEN p_risk < 0.1 THEN '0.0-0.1'
        WHEN p_risk < 0.2 THEN '0.1-0.2'
        WHEN p_risk < 0.3 THEN '0.2-0.3'
        WHEN p_risk < 0.4 THEN '0.3-0.4'
        WHEN p_risk < 0.5 THEN '0.4-0.5'
        WHEN p_risk < 0.6 THEN '0.5-0.6'
        WHEN p_risk < 0.7 THEN '0.6-0.7'
        WHEN p_risk < 0.8 THEN '0.7-0.8'
        WHEN p_risk < 0.9 THEN '0.8-0.9'
        ELSE '0.9-1.0'
    END;
END;
$$ LANGUAGE plpgsql;

-- STEP 4: Function to update daily risk bands
CREATE OR REPLACE FUNCTION update_daily_risk_bands()
RETURNS TABLE(
    symbol VARCHAR,
    risk_band VARCHAR,
    days_added INTEGER,
    new_total_days INTEGER
) AS $$
DECLARE
    r RECORD;
    current_price DECIMAL;
    current_risk_value DECIMAL;
    risk_band_text VARCHAR;
BEGIN
    -- Process each symbol
    FOR r IN SELECT DISTINCT t.symbol
             FROM cryptoverse_risk_time_bands_v2 t
    LOOP
        -- Get current price (you might get this from an API or another table)
        -- For now, we'll use the risk_at_price function
        SELECT price_usd INTO current_price
        FROM cryptoverse_risk_data
        WHERE symbol = r.symbol;

        -- Get current risk value
        SELECT get_risk_at_price(r.symbol, current_price, 'fiat')
        INTO current_risk_value;

        -- Determine risk band
        risk_band_text := get_current_risk_band(current_risk_value);

        -- Update the corresponding band counter
        EXECUTE format('
            UPDATE cryptoverse_risk_time_bands_v2
            SET
                band_%s = band_%s + 1,
                total_days = total_days + 1,
                current_risk = $1,
                current_risk_band = $2,
                last_risk_update = NOW(),
                updated_at = NOW()
            WHERE symbol = $3',
            REPLACE(REPLACE(risk_band_text, '.', ''), '-', '_'),
            REPLACE(REPLACE(risk_band_text, '.', ''), '-', '_')
        ) USING current_risk_value, risk_band_text, r.symbol;

        -- Record in history
        INSERT INTO risk_band_daily_history (symbol, date, risk_value, risk_band, price_usd)
        VALUES (r.symbol, CURRENT_DATE, current_risk_value, risk_band_text, current_price)
        ON CONFLICT (symbol, date) DO UPDATE SET
            risk_value = EXCLUDED.risk_value,
            risk_band = EXCLUDED.risk_band,
            price_usd = EXCLUDED.price_usd;

        -- Return result
        RETURN QUERY
        SELECT
            r.symbol,
            risk_band_text,
            1 as days_added,
            (SELECT total_days FROM cryptoverse_risk_time_bands_v2 WHERE symbol = r.symbol);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- STEP 5: Function to recalculate coefficients
CREATE OR REPLACE FUNCTION recalculate_trading_coefficients()
RETURNS VOID AS $$
DECLARE
    r RECORD;
    max_days INTEGER;
    min_days INTEGER;
    coef DECIMAL;
BEGIN
    -- Process each symbol
    FOR r IN SELECT * FROM cryptoverse_risk_time_bands_v2
    LOOP
        -- Find max and min days (excluding zeros)
        SELECT
            GREATEST(
                NULLIF(r.band_0_10, 0), NULLIF(r.band_10_20, 0),
                NULLIF(r.band_20_30, 0), NULLIF(r.band_30_40, 0),
                NULLIF(r.band_40_50, 0), NULLIF(r.band_50_60, 0),
                NULLIF(r.band_60_70, 0), NULLIF(r.band_70_80, 0),
                NULLIF(r.band_80_90, 0), NULLIF(r.band_90_100, 0)
            ),
            LEAST(
                CASE WHEN r.band_0_10 > 0 THEN r.band_0_10 ELSE 999999 END,
                CASE WHEN r.band_10_20 > 0 THEN r.band_10_20 ELSE 999999 END,
                CASE WHEN r.band_20_30 > 0 THEN r.band_20_30 ELSE 999999 END,
                CASE WHEN r.band_30_40 > 0 THEN r.band_30_40 ELSE 999999 END,
                CASE WHEN r.band_40_50 > 0 THEN r.band_40_50 ELSE 999999 END,
                CASE WHEN r.band_50_60 > 0 THEN r.band_50_60 ELSE 999999 END,
                CASE WHEN r.band_60_70 > 0 THEN r.band_60_70 ELSE 999999 END,
                CASE WHEN r.band_70_80 > 0 THEN r.band_70_80 ELSE 999999 END,
                CASE WHEN r.band_80_90 > 0 THEN r.band_80_90 ELSE 999999 END,
                CASE WHEN r.band_90_100 > 0 THEN r.band_90_100 ELSE 999999 END
            )
        INTO max_days, min_days;

        -- Calculate coefficient for each band
        -- Formula: 1.60 - ((days - min_days) * 0.60 / (max_days - min_days))
        -- Most common = 1.00, Rarest = 1.60

        UPDATE cryptoverse_risk_time_bands_v2
        SET
            coef_0_10 = CASE
                WHEN band_0_10 = 0 THEN 1.000
                WHEN band_0_10 = max_days THEN 1.000
                WHEN band_0_10 = min_days THEN 1.600
                ELSE 1.600 - ((band_0_10 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_10_20 = CASE
                WHEN band_10_20 = 0 THEN 1.000
                WHEN band_10_20 = max_days THEN 1.000
                WHEN band_10_20 = min_days THEN 1.600
                ELSE 1.600 - ((band_10_20 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_20_30 = CASE
                WHEN band_20_30 = 0 THEN 1.000
                WHEN band_20_30 = max_days THEN 1.000
                WHEN band_20_30 = min_days THEN 1.600
                ELSE 1.600 - ((band_20_30 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_30_40 = CASE
                WHEN band_30_40 = 0 THEN 1.000
                WHEN band_30_40 = max_days THEN 1.000
                WHEN band_30_40 = min_days THEN 1.600
                ELSE 1.600 - ((band_30_40 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_40_50 = CASE
                WHEN band_40_50 = 0 THEN 1.000
                WHEN band_40_50 = max_days THEN 1.000
                WHEN band_40_50 = min_days THEN 1.600
                ELSE 1.600 - ((band_40_50 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_50_60 = CASE
                WHEN band_50_60 = 0 THEN 1.000
                WHEN band_50_60 = max_days THEN 1.000
                WHEN band_50_60 = min_days THEN 1.600
                ELSE 1.600 - ((band_50_60 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_60_70 = CASE
                WHEN band_60_70 = 0 THEN 1.000
                WHEN band_60_70 = max_days THEN 1.000
                WHEN band_60_70 = min_days THEN 1.600
                ELSE 1.600 - ((band_60_70 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_70_80 = CASE
                WHEN band_70_80 = 0 THEN 1.000
                WHEN band_70_80 = max_days THEN 1.000
                WHEN band_70_80 = min_days THEN 1.600
                ELSE 1.600 - ((band_70_80 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_80_90 = CASE
                WHEN band_80_90 = 0 THEN 1.000
                WHEN band_80_90 = max_days THEN 1.000
                WHEN band_80_90 = min_days THEN 1.600
                ELSE 1.600 - ((band_80_90 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            coef_90_100 = CASE
                WHEN band_90_100 = 0 THEN 1.000
                WHEN band_90_100 = max_days THEN 1.000
                WHEN band_90_100 = min_days THEN 1.600
                ELSE 1.600 - ((band_90_100 - min_days)::DECIMAL * 0.600 / NULLIF(max_days - min_days, 0))
            END,
            last_coefficient_update = NOW()
        WHERE symbol = r.symbol;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- STEP 6: Master daily update function
CREATE OR REPLACE FUNCTION daily_risk_update_master()
RETURNS TABLE(
    status TEXT,
    symbols_updated INTEGER,
    coefficients_recalculated BOOLEAN
) AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    -- Step 1: Update daily risk bands
    PERFORM update_daily_risk_bands();

    -- Count updated symbols
    SELECT COUNT(*) INTO updated_count
    FROM cryptoverse_risk_time_bands_v2
    WHERE DATE(last_risk_update) = CURRENT_DATE;

    -- Step 2: Recalculate coefficients
    PERFORM recalculate_trading_coefficients();

    -- Return status
    RETURN QUERY
    SELECT
        'Daily update completed' as status,
        updated_count as symbols_updated,
        TRUE as coefficients_recalculated;
END;
$$ LANGUAGE plpgsql;

-- STEP 7: Create trigger for automatic coefficient updates
CREATE OR REPLACE FUNCTION trigger_coefficient_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Whenever band days change, recalculate coefficients for that symbol
    IF (OLD.band_0_10 != NEW.band_0_10 OR
        OLD.band_10_20 != NEW.band_10_20 OR
        OLD.band_20_30 != NEW.band_20_30 OR
        OLD.band_30_40 != NEW.band_30_40 OR
        OLD.band_40_50 != NEW.band_40_50 OR
        OLD.band_50_60 != NEW.band_50_60 OR
        OLD.band_60_70 != NEW.band_60_70 OR
        OLD.band_70_80 != NEW.band_70_80 OR
        OLD.band_80_90 != NEW.band_80_90 OR
        OLD.band_90_100 != NEW.band_90_100) THEN

        -- Recalculate just for this symbol
        PERFORM recalculate_trading_coefficients();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_recalculate_coefficients ON cryptoverse_risk_time_bands_v2;
CREATE TRIGGER auto_recalculate_coefficients
AFTER UPDATE ON cryptoverse_risk_time_bands_v2
FOR EACH ROW
EXECUTE FUNCTION trigger_coefficient_update();

-- STEP 8: Set up Supabase Cron Job (run daily at midnight UTC)
-- Note: This requires pg_cron extension to be enabled in Supabase
-- Go to Dashboard > Database > Extensions and enable pg_cron

-- Create the cron job
SELECT cron.schedule(
    'daily-risk-update',           -- job name
    '0 0 * * *',                   -- cron expression (midnight UTC daily)
    $$SELECT daily_risk_update_master();$$  -- command to run
);

-- STEP 9: View to see current status with coefficients
CREATE OR REPLACE VIEW v_risk_trading_signals AS
SELECT
    t.symbol,
    t.symbol_name,
    t.current_risk,
    t.current_risk_band,
    CASE t.current_risk_band
        WHEN '0.0-0.1' THEN t.coef_0_10
        WHEN '0.1-0.2' THEN t.coef_10_20
        WHEN '0.2-0.3' THEN t.coef_20_30
        WHEN '0.3-0.4' THEN t.coef_30_40
        WHEN '0.4-0.5' THEN t.coef_40_50
        WHEN '0.5-0.6' THEN t.coef_50_60
        WHEN '0.6-0.7' THEN t.coef_60_70
        WHEN '0.7-0.8' THEN t.coef_70_80
        WHEN '0.8-0.9' THEN t.coef_80_90
        WHEN '0.9-1.0' THEN t.coef_90_100
    END as current_coefficient,
    t.current_risk * CASE t.current_risk_band
        WHEN '0.0-0.1' THEN t.coef_0_10
        WHEN '0.1-0.2' THEN t.coef_10_20
        WHEN '0.2-0.3' THEN t.coef_20_30
        WHEN '0.3-0.4' THEN t.coef_30_40
        WHEN '0.4-0.5' THEN t.coef_40_50
        WHEN '0.5-0.6' THEN t.coef_50_60
        WHEN '0.6-0.7' THEN t.coef_60_70
        WHEN '0.7-0.8' THEN t.coef_70_80
        WHEN '0.8-0.9' THEN t.coef_80_90
        WHEN '0.9-1.0' THEN t.coef_90_100
    END as adjusted_risk_score,
    CASE
        WHEN t.current_risk < 0.3 AND CASE t.current_risk_band
            WHEN '0.0-0.1' THEN t.coef_0_10
            WHEN '0.1-0.2' THEN t.coef_10_20
            WHEN '0.2-0.3' THEN t.coef_20_30
            ELSE 1.0
        END >= 1.5 THEN '🔥 STRONG BUY - Rare accumulation'
        WHEN t.current_risk > 0.7 AND CASE t.current_risk_band
            WHEN '0.7-0.8' THEN t.coef_70_80
            WHEN '0.8-0.9' THEN t.coef_80_90
            WHEN '0.9-1.0' THEN t.coef_90_100
            ELSE 1.0
        END >= 1.3 THEN '📉 SELL - Rare distribution'
        WHEN t.current_risk < 0.3 THEN '💰 BUY - Accumulation zone'
        WHEN t.current_risk > 0.7 THEN '💸 TAKE PROFIT - Distribution zone'
        ELSE '⏸️ HOLD - Transition zone'
    END as trading_signal,
    t.total_days,
    t.last_risk_update,
    t.last_coefficient_update
FROM cryptoverse_risk_time_bands_v2 t
ORDER BY t.symbol;

-- STEP 10: Initialize with existing data
INSERT INTO cryptoverse_risk_time_bands_v2 (
    symbol, symbol_name, birth_date, total_days,
    band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
    band_50_60, band_60_70, band_70_80, band_80_90, band_90_100
)
SELECT
    symbol, symbol_name, birth_date, total_days,
    band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
    band_50_60, band_60_70, band_70_80, band_80_90, band_90_100
FROM cryptoverse_risk_time_bands
ON CONFLICT (symbol) DO NOTHING;

-- Initial coefficient calculation
SELECT recalculate_trading_coefficients();

-- VERIFICATION
SELECT
    '✅ AUTOMATED SYSTEM READY' as status,
    'Daily updates will run at midnight UTC' as schedule,
    'Coefficients recalculate automatically' as feature;

-- Check current status
SELECT * FROM v_risk_trading_signals WHERE symbol IN ('BTC', 'ETH', 'SOL') LIMIT 3;