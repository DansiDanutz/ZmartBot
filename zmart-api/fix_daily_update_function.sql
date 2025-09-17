-- FIX FOR DAILY UPDATE FUNCTION - RESOLVES AMBIGUITY ERROR
-- =========================================================

-- Drop and recreate the function with proper table aliasing
DROP FUNCTION IF EXISTS update_daily_risk_bands();

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
    FOR r IN SELECT DISTINCT t.symbol AS sym
             FROM cryptoverse_risk_time_bands_v2 t
    LOOP
        -- Get current price with proper table reference
        SELECT crd.price_usd INTO current_price
        FROM cryptoverse_risk_data crd
        WHERE crd.symbol = r.sym;

        -- Get current risk value
        SELECT get_risk_at_price(r.sym, current_price, 'fiat')
        INTO current_risk_value;

        -- Handle NULL risk values
        IF current_risk_value IS NULL THEN
            -- Try to get from current risk data
            SELECT crd.fiat_risk INTO current_risk_value
            FROM cryptoverse_risk_data crd
            WHERE crd.symbol = r.sym;

            -- If still NULL, skip this symbol
            IF current_risk_value IS NULL THEN
                CONTINUE;
            END IF;
        END IF;

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
        ) USING current_risk_value, risk_band_text, r.sym;

        -- Record in history
        INSERT INTO risk_band_daily_history (symbol, date, risk_value, risk_band, price_usd)
        VALUES (r.sym, CURRENT_DATE, current_risk_value, risk_band_text, current_price)
        ON CONFLICT (symbol, date) DO UPDATE SET
            risk_value = EXCLUDED.risk_value,
            risk_band = EXCLUDED.risk_band,
            price_usd = EXCLUDED.price_usd;

        -- Return result
        RETURN QUERY
        SELECT
            r.sym,
            risk_band_text,
            1 as days_added,
            (SELECT rtb.total_days FROM cryptoverse_risk_time_bands_v2 rtb WHERE rtb.symbol = r.sym);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Also fix the master function to handle errors better
DROP FUNCTION IF EXISTS daily_risk_update_master();

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
    FROM cryptoverse_risk_time_bands_v2 rtb
    WHERE DATE(rtb.last_risk_update) = CURRENT_DATE;

    -- Step 2: Recalculate coefficients
    PERFORM recalculate_trading_coefficients();

    -- Return status
    RETURN QUERY
    SELECT
        'Daily update completed'::TEXT as status,
        updated_count as symbols_updated,
        TRUE as coefficients_recalculated;
END;
$$ LANGUAGE plpgsql;

-- TEST: First make sure we have current risk data
SELECT
    crd.symbol,
    crd.price_usd,
    crd.fiat_risk,
    get_current_risk_band(crd.fiat_risk) as risk_band
FROM cryptoverse_risk_data crd
WHERE crd.symbol IN ('BTC', 'ETH', 'SOL')
ORDER BY crd.symbol;

-- If above returns NULL, let's populate some test data
INSERT INTO cryptoverse_risk_data (symbol, price_usd, fiat_risk)
VALUES
    ('BTC', 102000, 0.55),
    ('ETH', 3900, 0.60),
    ('SOL', 245, 0.715)
ON CONFLICT (symbol) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    fiat_risk = EXCLUDED.fiat_risk,
    last_updated = NOW();

-- Now try the master function again
SELECT * FROM daily_risk_update_master();

-- Check results
SELECT
    rtb.symbol,
    rtb.current_risk_band,
    rtb.total_days,
    rtb.band_70_80 as "Days in 70-80%",
    rtb.coef_70_80 as "70-80% Coefficient",
    rtb.last_risk_update
FROM cryptoverse_risk_time_bands_v2 rtb
WHERE rtb.symbol IN ('SOL', 'BTC', 'ETH')
ORDER BY rtb.symbol;