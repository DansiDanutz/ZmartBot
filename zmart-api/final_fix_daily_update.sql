-- FINAL FIX FOR DAILY UPDATE FUNCTION - ALL AMBIGUITIES RESOLVED
-- ================================================================

-- Drop and recreate with all ambiguities fixed
DROP FUNCTION IF EXISTS update_daily_risk_bands();

CREATE OR REPLACE FUNCTION update_daily_risk_bands()
RETURNS TABLE(
    out_symbol VARCHAR,
    out_risk_band VARCHAR,
    out_days_added INTEGER,
    out_new_total_days INTEGER
) AS $$
DECLARE
    r RECORD;
    current_price DECIMAL;
    current_risk_value DECIMAL;
    risk_band_text VARCHAR;
    band_column_name VARCHAR;
    coef_column_name VARCHAR;
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

        -- Also get coefficient column name
        coef_column_name := CASE risk_band_text
            WHEN '0.0-0.1' THEN 'coef_0_10'
            WHEN '0.1-0.2' THEN 'coef_10_20'
            WHEN '0.2-0.3' THEN 'coef_20_30'
            WHEN '0.3-0.4' THEN 'coef_30_40'
            WHEN '0.4-0.5' THEN 'coef_40_50'
            WHEN '0.5-0.6' THEN 'coef_50_60'
            WHEN '0.6-0.7' THEN 'coef_60_70'
            WHEN '0.7-0.8' THEN 'coef_70_80'
            WHEN '0.8-0.9' THEN 'coef_80_90'
            WHEN '0.9-1.0' THEN 'coef_90_100'
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
            WHERE cryptoverse_risk_time_bands_v2.symbol = $3',
            band_column_name, band_column_name
        ) USING current_risk_value, risk_band_text, r.sym;

        -- Record in history (fixed ambiguity)
        INSERT INTO risk_band_daily_history (symbol, date, risk_value, risk_band, price_usd)
        SELECT r.sym, CURRENT_DATE, current_risk_value, risk_band_text, current_price
        ON CONFLICT (symbol, date) DO UPDATE SET
            risk_value = EXCLUDED.risk_value,
            risk_band = EXCLUDED.risk_band,
            price_usd = EXCLUDED.price_usd;

        -- Return result
        out_symbol := r.sym;
        out_risk_band := risk_band_text;
        out_days_added := 1;

        SELECT rtb.total_days INTO out_new_total_days
        FROM cryptoverse_risk_time_bands_v2 rtb
        WHERE rtb.symbol = r.sym;

        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Test it now
SELECT * FROM daily_risk_update_master();

-- Check the results
SELECT
    rtb.symbol,
    rtb.current_risk,
    rtb.current_risk_band,
    rtb.total_days,
    rtb.band_70_80 as "Days in 70-80%",
    rtb.coef_70_80 as "70-80% Coef",
    rtb.last_risk_update
FROM cryptoverse_risk_time_bands_v2 rtb
WHERE rtb.symbol IN ('SOL', 'BTC', 'ETH')
ORDER BY rtb.symbol;

-- Also check history was recorded
SELECT * FROM risk_band_daily_history
WHERE date = CURRENT_DATE
ORDER BY symbol;