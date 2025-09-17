-- STEP 1: Add risk_type column to risk_metric_grid table (run this first)
ALTER TABLE risk_metric_grid
ADD COLUMN IF NOT EXISTS risk_type VARCHAR(20) DEFAULT 'KEY_RISK';

-- STEP 2: Create unique constraint for upsert operations (run this second)
DROP CONSTRAINT IF EXISTS risk_metric_grid_unique_key;
ALTER TABLE risk_metric_grid
ADD CONSTRAINT risk_metric_grid_unique_key
UNIQUE (symbol, price_point, risk_type);

-- STEP 3: Clear existing data (optional - run if you want to start fresh)
-- DELETE FROM risk_metric_grid;

-- STEP 4: Now you can copy and paste the INSERT statements from individual files
-- Start with smaller files like hbar_risk_data.sql, sui_risk_data.sql, etc.
-- Each file has INSERT statements with ON CONFLICT clauses for safe upserts