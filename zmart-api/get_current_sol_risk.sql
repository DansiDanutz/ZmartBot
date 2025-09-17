-- GET CURRENT SOL RISK BASED ON MARKET PRICE
-- ============================================

-- First, let's see the risk grid boundaries for SOL
WITH sol_risk_bounds AS (
    SELECT
        MIN(price_usd) as min_price,
        MAX(price_usd) as max_price,
        MIN(fiat_risk) as min_risk,
        MAX(fiat_risk) as max_risk
    FROM cryptoverse_risk_grid
    WHERE symbol = 'SOL'
)
SELECT
    'SOL RISK GRID RANGE' as info,
    ROUND(min_price::numeric, 2) as "Bottom Price (0% Risk)",
    ROUND(max_price::numeric, 2) as "Top Price (100% Risk)"
FROM sol_risk_bounds;

-- Now let's calculate risk for a specific price
-- REPLACE 240.00 with the current SOL price
DO $$
DECLARE
    current_price DECIMAL := 240.00;  -- << REPLACE WITH CURRENT SOL PRICE
    calculated_risk DECIMAL;
BEGIN
    -- Find the risk level for the current price
    WITH risk_brackets AS (
        SELECT
            symbol,
            fiat_risk,
            price_usd,
            LEAD(fiat_risk) OVER (ORDER BY fiat_risk) as next_risk,
            LEAD(price_usd) OVER (ORDER BY fiat_risk) as next_price
        FROM cryptoverse_risk_grid
        WHERE symbol = 'SOL'
    ),
    current_bracket AS (
        SELECT
            fiat_risk as lower_risk,
            next_risk as upper_risk,
            price_usd as lower_price,
            next_price as upper_price
        FROM risk_brackets
        WHERE price_usd <= current_price
        AND (next_price > current_price OR next_price IS NULL)
        LIMIT 1
    )
    SELECT
        CASE
            WHEN upper_price IS NULL THEN
                CASE
                    WHEN current_price > lower_price THEN 1.000  -- Above max
                    ELSE 0.000  -- Below min
                END
            ELSE
                lower_risk + (upper_risk - lower_risk) *
                ((current_price - lower_price) / (upper_price - lower_price))
        END INTO calculated_risk
    FROM current_bracket;

    RAISE NOTICE 'SOL at price $% has risk level: %', current_price, ROUND(calculated_risk, 3);
END $$;

-- Function to get risk at any price
CREATE OR REPLACE FUNCTION get_risk_at_price(
    p_symbol VARCHAR,
    p_price DECIMAL,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS DECIMAL AS $$
DECLARE
    v_risk DECIMAL;
BEGIN
    IF p_type = 'fiat' THEN
        WITH risk_brackets AS (
            SELECT
                fiat_risk,
                price_usd,
                LEAD(fiat_risk) OVER (ORDER BY fiat_risk) as next_risk,
                LEAD(price_usd) OVER (ORDER BY fiat_risk) as next_price
            FROM cryptoverse_risk_grid
            WHERE symbol = p_symbol
        ),
        current_bracket AS (
            SELECT
                fiat_risk as lower_risk,
                next_risk as upper_risk,
                price_usd as lower_price,
                next_price as upper_price
            FROM risk_brackets
            WHERE price_usd <= p_price
            AND (next_price > p_price OR next_price IS NULL)
            LIMIT 1
        )
        SELECT
            CASE
                WHEN upper_price IS NULL THEN
                    CASE
                        WHEN p_price > (SELECT MAX(price_usd) FROM cryptoverse_risk_grid WHERE symbol = p_symbol) THEN 1.000
                        WHEN p_price < (SELECT MIN(price_usd) FROM cryptoverse_risk_grid WHERE symbol = p_symbol) THEN 0.000
                        ELSE lower_risk
                    END
                ELSE
                    lower_risk + (upper_risk - lower_risk) *
                    ((p_price - lower_price) / (upper_price - lower_price))
            END INTO v_risk
        FROM current_bracket;
    END IF;

    RETURN v_risk;
END;
$$ LANGUAGE plpgsql;

-- Now use the function with current SOL price
-- REPLACE 240.00 with actual current price
SELECT
    'SOL CURRENT RISK' as analysis,
    240.00 as current_price,  -- << REPLACE WITH CURRENT PRICE
    ROUND(get_risk_at_price('SOL', 240.00, 'fiat'), 3) as risk_level,
    CASE
        WHEN get_risk_at_price('SOL', 240.00, 'fiat') < 0.3 THEN '🟢 ACCUMULATION ZONE'
        WHEN get_risk_at_price('SOL', 240.00, 'fiat') < 0.7 THEN '🟡 TRANSITION ZONE'
        ELSE '🔴 DISTRIBUTION ZONE'
    END as risk_zone;

-- Show nearby risk levels for context
SELECT
    'NEARBY RISK LEVELS' as context,
    fiat_risk,
    ROUND(price_usd::numeric, 2) as price,
    CASE
        WHEN fiat_risk < 0.3 THEN '🟢'
        WHEN fiat_risk < 0.7 THEN '🟡'
        ELSE '🔴'
    END as zone
FROM cryptoverse_risk_grid
WHERE symbol = 'SOL'
AND fiat_risk BETWEEN 0.45 AND 0.65  -- Adjust range based on current risk
ORDER BY fiat_risk;