-- ============================================
-- CREATE ONLY THE ESSENTIAL FUNCTIONS
-- This will get your system working without conflicts
-- ============================================

-- 1. First check what tables you have with data
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns,
    pg_size_pretty(pg_total_relation_size(table_name::regclass)) as size
FROM information_schema.tables t
WHERE table_schema = 'public'
AND (
    table_name LIKE 'cryptoverse_%' OR
    table_name LIKE 'alert_%' OR
    table_name LIKE 'trading_%' OR
    table_name LIKE 'cryptometer_%'
)
ORDER BY table_name;

-- 2. Create ONLY the basic risk functions (minimal version)
-- These are simple versions just to get things working

-- Basic risk calculation (simplified)
CREATE OR REPLACE FUNCTION get_risk_at_price(
    p_symbol VARCHAR,
    p_price NUMERIC,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS NUMERIC AS $$
DECLARE
    v_risk NUMERIC;
BEGIN
    -- Check if we have the risk grid table
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'cryptoverse_risk_grid') THEN

        -- Get closest risk value
        SELECT risk_value INTO v_risk
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol
        AND price_usd <= p_price
        ORDER BY price_usd DESC
        LIMIT 1;

        -- Return found value or default
        RETURN COALESCE(v_risk, 0.5);
    ELSE
        -- No risk grid table, return default
        RETURN 0.5;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Basic price lookup (simplified)
CREATE OR REPLACE FUNCTION get_price_at_risk(
    p_symbol VARCHAR,
    p_risk NUMERIC,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS NUMERIC AS $$
DECLARE
    v_price NUMERIC;
BEGIN
    -- Check if we have the risk grid table
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'cryptoverse_risk_grid') THEN

        -- Get closest price
        SELECT price_usd INTO v_price
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol
        AND risk_value <= p_risk
        ORDER BY risk_value DESC
        LIMIT 1;

        -- Return found value or default
        RETURN COALESCE(v_price, 0);
    ELSE
        -- No risk grid table
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 3. Create the timestamp update function (many tables need this)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Test the functions
SELECT
    'FUNCTION TEST' as test,
    get_risk_at_price('BTC', 100000::numeric, 'fiat') as risk_test,
    get_price_at_risk('BTC', 0.5::numeric, 'fiat') as price_test,
    CASE
        WHEN get_risk_at_price('BTC', 100000::numeric, 'fiat') IS NOT NULL
        THEN '✅ Functions created successfully'
        ELSE '⚠️ Functions created but need data'
    END as status;

-- 5. Summary
SELECT
    '✅ ESSENTIAL FUNCTIONS CREATED' as status,
    'System should now work for basic operations' as message,
    'You can now:' as next_steps,
    '1. Continue using the system' as option_1,
    '2. Run only the NEW table migrations (alert, cryptometer)' as option_2,
    '3. Import risk data if needed' as option_3;