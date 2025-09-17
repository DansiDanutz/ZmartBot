-- SETUP RISK TIME BANDS TABLE IN SUPABASE
-- =========================================
-- This table stores how much time each symbol has spent in different risk bands

-- STEP 1: Create the table
CREATE TABLE IF NOT EXISTS cryptoverse_risk_time_bands (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    symbol_name VARCHAR(100),
    birth_date DATE,
    total_days INTEGER,

    -- Risk band days (0.0-0.1, 0.1-0.2, etc.)
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

    -- Risk band percentages
    band_0_10_pct DECIMAL(5, 2),
    band_10_20_pct DECIMAL(5, 2),
    band_20_30_pct DECIMAL(5, 2),
    band_30_40_pct DECIMAL(5, 2),
    band_40_50_pct DECIMAL(5, 2),
    band_50_60_pct DECIMAL(5, 2),
    band_60_70_pct DECIMAL(5, 2),
    band_70_80_pct DECIMAL(5, 2),
    band_80_90_pct DECIMAL(5, 2),
    band_90_100_pct DECIMAL(5, 2),

    current_risk_band VARCHAR(10),
    confidence_level INTEGER,
    data_type VARCHAR(20),
    last_updated TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_symbol_time_bands UNIQUE(symbol)
);

-- STEP 2: Create indexes
CREATE INDEX IF NOT EXISTS idx_time_bands_symbol ON cryptoverse_risk_time_bands(symbol);
CREATE INDEX IF NOT EXISTS idx_time_bands_current ON cryptoverse_risk_time_bands(current_risk_band);

-- STEP 3: Create view for easy querying
CREATE OR REPLACE VIEW v_risk_time_distribution AS
SELECT
    symbol,
    symbol_name,
    birth_date,
    total_days,
    current_risk_band,

    -- Accumulation Zone (0-30%)
    band_0_10 + band_10_20 + band_20_30 as accumulation_days,
    band_0_10_pct + band_10_20_pct + band_20_30_pct as accumulation_pct,

    -- Transition Zone (30-70%)
    band_30_40 + band_40_50 + band_50_60 + band_60_70 as transition_days,
    band_30_40_pct + band_40_50_pct + band_50_60_pct + band_60_70_pct as transition_pct,

    -- Distribution Zone (70-100%)
    band_70_80 + band_80_90 + band_90_100 as distribution_days,
    band_70_80_pct + band_80_90_pct + band_90_100_pct as distribution_pct,

    confidence_level,
    data_type,
    last_updated
FROM cryptoverse_risk_time_bands;

-- STEP 4: Function to get time spent at specific risk level
CREATE OR REPLACE FUNCTION get_time_at_risk_level(
    p_symbol VARCHAR,
    p_risk_level DECIMAL
)
RETURNS TABLE(
    days_in_band INTEGER,
    percentage_in_band DECIMAL,
    risk_band VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        CASE
            WHEN p_risk_level < 0.1 THEN band_0_10
            WHEN p_risk_level < 0.2 THEN band_10_20
            WHEN p_risk_level < 0.3 THEN band_20_30
            WHEN p_risk_level < 0.4 THEN band_30_40
            WHEN p_risk_level < 0.5 THEN band_40_50
            WHEN p_risk_level < 0.6 THEN band_50_60
            WHEN p_risk_level < 0.7 THEN band_60_70
            WHEN p_risk_level < 0.8 THEN band_70_80
            WHEN p_risk_level < 0.9 THEN band_80_90
            ELSE band_90_100
        END as days_in_band,
        CASE
            WHEN p_risk_level < 0.1 THEN band_0_10_pct
            WHEN p_risk_level < 0.2 THEN band_10_20_pct
            WHEN p_risk_level < 0.3 THEN band_20_30_pct
            WHEN p_risk_level < 0.4 THEN band_30_40_pct
            WHEN p_risk_level < 0.5 THEN band_40_50_pct
            WHEN p_risk_level < 0.6 THEN band_50_60_pct
            WHEN p_risk_level < 0.7 THEN band_60_70_pct
            WHEN p_risk_level < 0.8 THEN band_70_80_pct
            WHEN p_risk_level < 0.9 THEN band_80_90_pct
            ELSE band_90_100_pct
        END as percentage_in_band,
        CASE
            WHEN p_risk_level < 0.1 THEN '0.0-0.1'
            WHEN p_risk_level < 0.2 THEN '0.1-0.2'
            WHEN p_risk_level < 0.3 THEN '0.2-0.3'
            WHEN p_risk_level < 0.4 THEN '0.3-0.4'
            WHEN p_risk_level < 0.5 THEN '0.4-0.5'
            WHEN p_risk_level < 0.6 THEN '0.5-0.6'
            WHEN p_risk_level < 0.7 THEN '0.6-0.7'
            WHEN p_risk_level < 0.8 THEN '0.7-0.8'
            WHEN p_risk_level < 0.9 THEN '0.8-0.9'
            ELSE '0.9-1.0'
        END as risk_band
    FROM cryptoverse_risk_time_bands
    WHERE symbol = p_symbol;
END;
$$ LANGUAGE plpgsql;

-- STEP 5: Test insert with SOL data
INSERT INTO cryptoverse_risk_time_bands (
    symbol, symbol_name, birth_date, total_days,
    band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
    band_50_60, band_60_70, band_70_80, band_80_90, band_90_100,
    band_0_10_pct, band_10_20_pct, band_20_30_pct, band_30_40_pct, band_40_50_pct,
    band_50_60_pct, band_60_70_pct, band_70_80_pct, band_80_90_pct, band_90_100_pct,
    current_risk_band, confidence_level, data_type
) VALUES (
    'SOL', 'Solana', '2020-03-16', 2008,
    60, 200, 261, 321, 401,
    441, 261, 140, 80, 40,
    2.99, 9.96, 13.0, 15.99, 19.97,
    21.96, 13.0, 6.97, 3.98, 1.99,
    '0.7-0.8', 7, 'estimated'
) ON CONFLICT (symbol) DO UPDATE SET
    band_0_10 = EXCLUDED.band_0_10,
    band_10_20 = EXCLUDED.band_10_20,
    band_20_30 = EXCLUDED.band_20_30,
    band_30_40 = EXCLUDED.band_30_40,
    band_40_50 = EXCLUDED.band_40_50,
    band_50_60 = EXCLUDED.band_50_60,
    band_60_70 = EXCLUDED.band_60_70,
    band_70_80 = EXCLUDED.band_70_80,
    band_80_90 = EXCLUDED.band_80_90,
    band_90_100 = EXCLUDED.band_90_100,
    band_0_10_pct = EXCLUDED.band_0_10_pct,
    band_10_20_pct = EXCLUDED.band_10_20_pct,
    band_20_30_pct = EXCLUDED.band_20_30_pct,
    band_30_40_pct = EXCLUDED.band_30_40_pct,
    band_40_50_pct = EXCLUDED.band_40_50_pct,
    band_50_60_pct = EXCLUDED.band_50_60_pct,
    band_60_70_pct = EXCLUDED.band_60_70_pct,
    band_70_80_pct = EXCLUDED.band_70_80_pct,
    band_80_90_pct = EXCLUDED.band_80_90_pct,
    band_90_100_pct = EXCLUDED.band_90_100_pct,
    current_risk_band = EXCLUDED.current_risk_band,
    last_updated = NOW();

-- STEP 6: Test queries
SELECT
    symbol,
    symbol_name,
    current_risk_band,
    accumulation_days,
    ROUND(accumulation_pct, 1) as "Accumulation %",
    transition_days,
    ROUND(transition_pct, 1) as "Transition %",
    distribution_days,
    ROUND(distribution_pct, 1) as "Distribution %"
FROM v_risk_time_distribution
WHERE symbol = 'SOL';

-- STEP 7: Check status
SELECT
    '✅ TIME BANDS SETUP COMPLETE' as status,
    'Now run load_all_time_bands.sql to load all 25 symbols' as next_step;