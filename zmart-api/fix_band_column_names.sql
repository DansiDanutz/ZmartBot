-- FIX BAND COLUMN NAME MAPPING
-- =============================

-- Drop and recreate the function with correct column name mapping
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
    band_column_name VARCHAR;
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

        -- Convert risk band to column name
        -- 0.0-0.1 -> band_0_10
        -- 0.1-0.2 -> band_10_20
        -- etc.
        band_column_name := CASE risk_band_text
            WHEN '0.0-0.1' THEN 'band_0_10'
            WHEN '0.1-0.2' THEN 'band_10_20'
            WHEN '0.2-0.3' THEN 'band_20_30'
            WHEN '0.3-0.4' THEN 'band_30_40'
            WHEN '0.4-0.5' THEN 'band_40_50'
            WHEN '0.5-0.6' THEN 'band_50_60'
            WHEN '0.6-0.7' THEN 'band_60_70'
            WHEN '0.7-0.8' THEN 'band_70_80'
            WHEN '0.8-0.9' THEN 'band_80_90'
            WHEN '0.9-1.0' THEN 'band_90_100'
        END;

        -- Update the corresponding band counter
        EXECUTE format('
            UPDATE cryptoverse_risk_time_bands_v2
            SET
                %I = %I + 1,
                total_days = total_days + 1,
                current_risk = $1,
                current_risk_band = $2,
                last_risk_update = NOW(),
                updated_at = NOW()
            WHERE symbol = $3',
            band_column_name, band_column_name
        ) USING current_risk_value, risk_band_text, r.sym;

        -- Also update the coefficient for this band
        EXECUTE format('
            UPDATE cryptoverse_risk_time_bands_v2
            SET
                %I = %I + 1
            WHERE symbol = $1',
            REPLACE('coef_' || band_column_name, 'band_', ''),
            REPLACE('coef_' || band_column_name, 'band_', '')
        ) USING r.sym;

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

-- Test the column names exist
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'cryptoverse_risk_time_bands_v2'
AND column_name LIKE 'band_%'
ORDER BY column_name;

-- Now test the function
SELECT * FROM daily_risk_update_master();

-- Verify it worked
SELECT
    rtb.symbol,
    rtb.current_risk,
    rtb.current_risk_band,
    rtb.total_days,
    CASE rtb.current_risk_band
        WHEN '0.0-0.1' THEN rtb.band_0_10
        WHEN '0.1-0.2' THEN rtb.band_10_20
        WHEN '0.2-0.3' THEN rtb.band_20_30
        WHEN '0.3-0.4' THEN rtb.band_30_40
        WHEN '0.4-0.5' THEN rtb.band_40_50
        WHEN '0.5-0.6' THEN rtb.band_50_60
        WHEN '0.6-0.7' THEN rtb.band_60_70
        WHEN '0.7-0.8' THEN rtb.band_70_80
        WHEN '0.8-0.9' THEN rtb.band_80_90
        WHEN '0.9-1.0' THEN rtb.band_90_100
    END as "Days in Current Band",
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
    END as "Current Coefficient",
    rtb.last_risk_update
FROM cryptoverse_risk_time_bands_v2 rtb
WHERE rtb.symbol IN ('SOL', 'BTC', 'ETH')
ORDER BY rtb.symbol;