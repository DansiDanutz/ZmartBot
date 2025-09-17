-- ==================== FIXED RISK DATA IMPORT ====================
-- Remove existing constraints that prevent our data import
-- Then import all 25 symbols with their complete risk data

-- STEP 1: Remove the restrictive price_point constraint
ALTER TABLE risk_metric_grid DROP CONSTRAINT IF EXISTS risk_metric_grid_price_point_check;

-- STEP 2: Add risk_type column if it doesn't exist
ALTER TABLE risk_metric_grid
ADD COLUMN IF NOT EXISTS risk_type VARCHAR(20) DEFAULT 'KEY_RISK';

-- STEP 3: Update unique constraint to include risk_type
ALTER TABLE risk_metric_grid
DROP CONSTRAINT IF EXISTS risk_metric_grid_unique_key;

ALTER TABLE risk_metric_grid
ADD CONSTRAINT risk_metric_grid_unique_key
UNIQUE (symbol, price_point, risk_type);

-- STEP 4: Add a more reasonable price_point constraint (1 to 200 to allow all risk types)
ALTER TABLE risk_metric_grid
ADD CONSTRAINT risk_metric_grid_price_point_check
CHECK (price_point >= 1 AND price_point <= 200);

-- Now the data can be imported safely!