-- Create Price-to-Risk Lookup Table for SOL
-- Direct lookup: Give price → Get risk value
-- Based on actual IntoTheCryptoverse data

-- Drop existing table if exists
DROP TABLE IF EXISTS public.price_risk_lookup CASCADE;

-- Create the lookup table
CREATE TABLE public.price_risk_lookup (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_usd DECIMAL(20,8) NOT NULL,
    risk_value DECIMAL(5,4) NOT NULL,
    risk_band VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, price_usd)
);

-- Create indexes for fast lookups
CREATE INDEX idx_price_risk_lookup_symbol_price ON price_risk_lookup(symbol, price_usd);
CREATE INDEX idx_price_risk_lookup_symbol_risk ON price_risk_lookup(symbol, risk_value);

-- Insert SOL data from IntoTheCryptoverse (42 exact points)
INSERT INTO price_risk_lookup (symbol, price_usd, risk_value, risk_band) VALUES
('SOL', 20.61, 0.000, '0.0-0.1'),
('SOL', 22.89, 0.024, '0.0-0.1'),
('SOL', 25.42, 0.048, '0.0-0.1'),
('SOL', 28.24, 0.071, '0.0-0.1'),
('SOL', 31.36, 0.095, '0.0-0.1'),
('SOL', 34.83, 0.119, '0.1-0.2'),
('SOL', 38.69, 0.143, '0.1-0.2'),
('SOL', 42.97, 0.167, '0.1-0.2'),
('SOL', 47.72, 0.190, '0.1-0.2'),
('SOL', 53.00, 0.214, '0.2-0.3'),
('SOL', 58.86, 0.238, '0.2-0.3'),
('SOL', 65.38, 0.262, '0.2-0.3'),
('SOL', 72.62, 0.286, '0.2-0.3'),
('SOL', 80.67, 0.310, '0.3-0.4'),
('SOL', 89.60, 0.333, '0.3-0.4'),
('SOL', 99.52, 0.357, '0.3-0.4'),
('SOL', 110.54, 0.381, '0.3-0.4'),
('SOL', 122.78, 0.405, '0.4-0.5'),
('SOL', 136.37, 0.429, '0.4-0.5'),
('SOL', 151.46, 0.452, '0.4-0.5'),
('SOL', 168.23, 0.476, '0.4-0.5'),
('SOL', 186.85, 0.500, '0.5-0.6'),
('SOL', 207.53, 0.524, '0.5-0.6'),
('SOL', 230.52, 0.548, '0.5-0.6'),
('SOL', 256.08, 0.571, '0.5-0.6'),
('SOL', 284.49, 0.595, '0.5-0.6'),
('SOL', 316.07, 0.619, '0.6-0.7'),
('SOL', 351.16, 0.643, '0.6-0.7'),
('SOL', 390.15, 0.667, '0.6-0.7'),
('SOL', 433.45, 0.690, '0.6-0.7'),
('SOL', 244.11, 0.714, '0.7-0.8'),  -- Close to current price
('SOL', 534.37, 0.738, '0.7-0.8'),
('SOL', 593.61, 0.762, '0.7-0.8'),
('SOL', 659.41, 0.786, '0.7-0.8'),
('SOL', 732.49, 0.810, '0.8-0.9'),
('SOL', 813.71, 0.833, '0.8-0.9'),
('SOL', 903.95, 0.857, '0.8-0.9'),
('SOL', 1004.25, 0.881, '0.8-0.9'),
('SOL', 1115.70, 0.905, '0.9-1.0'),
('SOL', 1239.52, 0.929, '0.9-1.0'),
('SOL', 1377.02, 0.952, '0.9-1.0'),
('SOL', 933.79, 1.000, '0.9-1.0')
ON CONFLICT (symbol, price_usd) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    risk_band = EXCLUDED.risk_band,
    updated_at = CURRENT_TIMESTAMP;

-- Function to find closest price and return risk value
CREATE OR REPLACE FUNCTION get_risk_for_price(
    p_symbol VARCHAR,
    p_price DECIMAL
) RETURNS TABLE (
    exact_match BOOLEAN,
    price_usd DECIMAL,
    risk_value DECIMAL,
    risk_band VARCHAR,
    price_diff DECIMAL
) AS $$
BEGIN
    -- First try exact match
    RETURN QUERY
    SELECT
        TRUE as exact_match,
        l.price_usd,
        l.risk_value,
        l.risk_band,
        0::DECIMAL as price_diff
    FROM price_risk_lookup l
    WHERE l.symbol = p_symbol AND l.price_usd = p_price
    LIMIT 1;

    -- If no exact match, find closest
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT
            FALSE as exact_match,
            l.price_usd,
            l.risk_value,
            l.risk_band,
            ABS(l.price_usd - p_price) as price_diff
        FROM price_risk_lookup l
        WHERE l.symbol = p_symbol
        ORDER BY ABS(l.price_usd - p_price)
        LIMIT 1;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to interpolate risk value for any price
CREATE OR REPLACE FUNCTION interpolate_risk_for_price(
    p_symbol VARCHAR,
    p_price DECIMAL
) RETURNS TABLE (
    interpolated_risk DECIMAL,
    lower_price DECIMAL,
    lower_risk DECIMAL,
    upper_price DECIMAL,
    upper_risk DECIMAL,
    risk_band VARCHAR
) AS $$
DECLARE
    v_lower RECORD;
    v_upper RECORD;
    v_interpolated DECIMAL;
    v_band VARCHAR;
BEGIN
    -- Get lower bound
    SELECT price_usd, risk_value, risk_band
    INTO v_lower
    FROM price_risk_lookup
    WHERE symbol = p_symbol AND price_usd <= p_price
    ORDER BY price_usd DESC
    LIMIT 1;

    -- Get upper bound
    SELECT price_usd, risk_value, risk_band
    INTO v_upper
    FROM price_risk_lookup
    WHERE symbol = p_symbol AND price_usd >= p_price
    ORDER BY price_usd ASC
    LIMIT 1;

    -- Calculate interpolated risk
    IF v_lower.price_usd IS NOT NULL AND v_upper.price_usd IS NOT NULL THEN
        IF v_lower.price_usd = v_upper.price_usd THEN
            -- Exact match
            v_interpolated := v_lower.risk_value;
            v_band := v_lower.risk_band;
        ELSE
            -- Linear interpolation
            v_interpolated := v_lower.risk_value +
                (v_upper.risk_value - v_lower.risk_value) *
                ((p_price - v_lower.price_usd) / (v_upper.price_usd - v_lower.price_usd));

            -- Determine risk band
            v_band := CASE
                WHEN v_interpolated < 0.1 THEN '0.0-0.1'
                WHEN v_interpolated < 0.2 THEN '0.1-0.2'
                WHEN v_interpolated < 0.3 THEN '0.2-0.3'
                WHEN v_interpolated < 0.4 THEN '0.3-0.4'
                WHEN v_interpolated < 0.5 THEN '0.4-0.5'
                WHEN v_interpolated < 0.6 THEN '0.5-0.6'
                WHEN v_interpolated < 0.7 THEN '0.6-0.7'
                WHEN v_interpolated < 0.8 THEN '0.7-0.8'
                WHEN v_interpolated < 0.9 THEN '0.8-0.9'
                ELSE '0.9-1.0'
            END;
        END IF;

        RETURN QUERY SELECT
            v_interpolated,
            v_lower.price_usd,
            v_lower.risk_value,
            v_upper.price_usd,
            v_upper.risk_value,
            v_band;
    ELSIF v_lower.price_usd IS NOT NULL THEN
        -- Price is above highest point
        RETURN QUERY SELECT
            v_lower.risk_value,
            v_lower.price_usd,
            v_lower.risk_value,
            v_lower.price_usd,
            v_lower.risk_value,
            v_lower.risk_band;
    ELSIF v_upper.price_usd IS NOT NULL THEN
        -- Price is below lowest point
        RETURN QUERY SELECT
            v_upper.risk_value,
            v_upper.price_usd,
            v_upper.risk_value,
            v_upper.price_usd,
            v_upper.risk_value,
            v_upper.risk_band;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test queries
SELECT '=== EXACT LOOKUPS ===' as test_section;

-- Find risk for exact price $244.11
SELECT * FROM price_risk_lookup
WHERE symbol = 'SOL' AND price_usd = 244.11;

-- Find risk for current market price (closest match)
SELECT * FROM get_risk_for_price('SOL', 238.88);

-- Find risk for $300 (interpolation needed)
SELECT * FROM interpolate_risk_for_price('SOL', 300);

-- Find risk for $500 (interpolation needed)
SELECT * FROM interpolate_risk_for_price('SOL', 500);

SELECT '=== CURRENT MARKET ANALYSIS ===' as test_section;

-- Get risk for current SOL price $238.88
SELECT
    'SOL' as symbol,
    238.88 as current_price,
    interpolated_risk,
    risk_band,
    lower_price,
    upper_price
FROM interpolate_risk_for_price('SOL', 238.88);

SELECT '=== TARGET PRICE ANALYSIS ===' as test_section;

-- Get risk for target price $300
SELECT
    'SOL' as symbol,
    300 as target_price,
    interpolated_risk,
    risk_band,
    lower_price,
    upper_price
FROM interpolate_risk_for_price('SOL', 300);

-- Show all SOL prices sorted by risk
SELECT '=== COMPLETE SOL RISK TABLE ===' as test_section;
SELECT
    symbol,
    price_usd,
    risk_value,
    risk_band,
    CASE
        WHEN price_usd BETWEEN 230 AND 250 THEN '← CURRENT RANGE'
        WHEN price_usd = 300 THEN '← TARGET'
        ELSE ''
    END as note
FROM price_risk_lookup
WHERE symbol = 'SOL'
ORDER BY risk_value;