-- =====================================================
-- RISKMETRIC DATABASE AGENT - COMPLETE SCHEMA
-- Based on Benjamin Cowen's Methodology
-- =====================================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- =====================================================
-- TABLE: symbols
-- Stores basic information about each cryptocurrency
-- =====================================================
CREATE TABLE symbols (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    inception_date DATE,
    current_price REAL,
    current_risk REAL,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 9),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- TABLE: regression_formulas
-- Stores logarithmic regression constants for each symbol
-- Formula: y = 10^(a * ln(x) - b)
-- =====================================================
CREATE TABLE regression_formulas (
    symbol TEXT,
    formula_type TEXT CHECK (formula_type IN ('bubble', 'non_bubble')),
    constant_a REAL NOT NULL,
    constant_b REAL NOT NULL,
    r_squared REAL CHECK (r_squared BETWEEN 0 AND 1),
    last_fitted DATE,
    cycle_data TEXT, -- JSON array of cycle points used for fitting
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, formula_type),
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- =====================================================
-- TABLE: risk_levels
-- Stores complete risk-price mapping for each symbol
-- 41 levels from 0.0 to 1.0 in 0.025 increments
-- =====================================================
CREATE TABLE risk_levels (
    symbol TEXT,
    risk_value REAL CHECK (risk_value BETWEEN 0 AND 1),
    price REAL CHECK (price > 0),
    calculated_date DATE,
    calculation_method TEXT DEFAULT 'logarithmic_interpolation',
    PRIMARY KEY (symbol, risk_value),
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- =====================================================
-- TABLE: time_spent_bands
-- Stores historical time spent in each risk band
-- Used for coefficient calculation (1.0 to 1.6)
-- =====================================================
CREATE TABLE time_spent_bands (
    symbol TEXT,
    band_start REAL CHECK (band_start BETWEEN 0 AND 0.9),
    band_end REAL CHECK (band_end BETWEEN 0.1 AND 1.0),
    days_spent INTEGER CHECK (days_spent >= 0),
    percentage REAL CHECK (percentage BETWEEN 0 AND 100),
    coefficient REAL CHECK (coefficient BETWEEN 1.0 AND 1.6),
    total_days INTEGER CHECK (total_days > 0),
    last_updated DATE,
    PRIMARY KEY (symbol, band_start),
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE,
    CHECK (band_end > band_start)
);

-- =====================================================
-- TABLE: manual_overrides
-- Stores manual updates to formulas and bounds
-- Critical for when Benjamin Cowen updates his models
-- =====================================================
CREATE TABLE manual_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    override_type TEXT CHECK (override_type IN ('min_price', 'max_price', 'formula_a_bubble', 'formula_b_bubble', 'formula_a_non_bubble', 'formula_b_non_bubble')),
    override_value REAL NOT NULL,
    previous_value REAL,
    override_reason TEXT,
    created_by TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    applied_date TIMESTAMP,
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- =====================================================
-- TABLE: price_history
-- Stores daily price data for each symbol
-- Used for time-spent calculations and updates
-- =====================================================
CREATE TABLE price_history (
    symbol TEXT,
    date DATE,
    open_price REAL CHECK (open_price > 0),
    high_price REAL CHECK (high_price > 0),
    low_price REAL CHECK (low_price > 0),
    close_price REAL CHECK (close_price > 0),
    volume REAL,
    risk_value REAL CHECK (risk_value BETWEEN 0 AND 1),
    risk_band TEXT,
    data_source TEXT DEFAULT 'api',
    PRIMARY KEY (symbol, date),
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE,
    CHECK (high_price >= low_price),
    CHECK (high_price >= open_price),
    CHECK (high_price >= close_price),
    CHECK (low_price <= open_price),
    CHECK (low_price <= close_price)
);

-- =====================================================
-- TABLE: assessments
-- Stores risk assessments and signals
-- Used for tracking and auditing
-- =====================================================
CREATE TABLE assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    price REAL CHECK (price > 0),
    risk_value REAL CHECK (risk_value BETWEEN 0 AND 1),
    risk_percentage TEXT,
    coefficient REAL CHECK (coefficient BETWEEN 1.0 AND 1.6),
    score REAL,
    signal TEXT CHECK (signal IN ('Strong Buy', 'Buy', 'Neutral', 'Sell', 'Strong Sell')),
    risk_band TEXT,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_source TEXT,
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- =====================================================
-- TABLE: system_config
-- Stores system configuration and metadata
-- =====================================================
CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: audit_log
-- Stores all system changes for auditing
-- =====================================================
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    operation TEXT CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id TEXT,
    old_values TEXT, -- JSON
    new_values TEXT, -- JSON
    changed_by TEXT,
    change_reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Symbols table indexes
CREATE INDEX idx_symbols_active ON symbols(is_active);
CREATE INDEX idx_symbols_confidence ON symbols(confidence_level);

-- Risk levels table indexes
CREATE INDEX idx_risk_levels_symbol_risk ON risk_levels(symbol, risk_value);
CREATE INDEX idx_risk_levels_price ON risk_levels(symbol, price);

-- Time spent bands indexes
CREATE INDEX idx_time_spent_symbol ON time_spent_bands(symbol);
CREATE INDEX idx_time_spent_coefficient ON time_spent_bands(coefficient);

-- Manual overrides indexes
CREATE INDEX idx_overrides_symbol_active ON manual_overrides(symbol, is_active);
CREATE INDEX idx_overrides_type ON manual_overrides(override_type);
CREATE INDEX idx_overrides_date ON manual_overrides(created_date);

-- Price history indexes
CREATE INDEX idx_price_history_symbol_date ON price_history(symbol, date);
CREATE INDEX idx_price_history_risk ON price_history(risk_value);

-- Assessments indexes
CREATE INDEX idx_assessments_symbol ON assessments(symbol);
CREATE INDEX idx_assessments_date ON assessments(assessment_date);
CREATE INDEX idx_assessments_signal ON assessments(signal);

-- Audit log indexes
CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Current symbol status with latest overrides
CREATE VIEW v_current_symbol_status AS
SELECT 
    s.symbol,
    s.name,
    s.current_price,
    s.current_risk,
    s.confidence_level,
    COALESCE(mo_min.override_value, rl_min.price) as current_min_price,
    COALESCE(mo_max.override_value, rl_max.price) as current_max_price,
    s.last_updated
FROM symbols s
LEFT JOIN risk_levels rl_min ON s.symbol = rl_min.symbol AND rl_min.risk_value = 0.0
LEFT JOIN risk_levels rl_max ON s.symbol = rl_max.symbol AND rl_max.risk_value = 1.0
LEFT JOIN (
    SELECT symbol, override_value 
    FROM manual_overrides 
    WHERE override_type = 'min_price' AND is_active = 1
    GROUP BY symbol 
    HAVING created_date = MAX(created_date)
) mo_min ON s.symbol = mo_min.symbol
LEFT JOIN (
    SELECT symbol, override_value 
    FROM manual_overrides 
    WHERE override_type = 'max_price' AND is_active = 1
    GROUP BY symbol 
    HAVING created_date = MAX(created_date)
) mo_max ON s.symbol = mo_max.symbol
WHERE s.is_active = 1;

-- Symbol screener view (like Benjamin Cowen's dashboard)
CREATE VIEW v_symbol_screener AS
SELECT 
    s.symbol,
    s.name,
    s.current_price,
    s.current_risk,
    ROUND(s.current_risk * 100, 1) || '%' as risk_percentage,
    s.confidence_level,
    tsb.coefficient,
    CASE 
        WHEN s.current_risk < 0.2 THEN 'Strong Buy'
        WHEN s.current_risk < 0.4 THEN 'Buy'
        WHEN s.current_risk < 0.6 THEN 'Neutral'
        WHEN s.current_risk < 0.8 THEN 'Sell'
        ELSE 'Strong Sell'
    END as signal,
    ROUND(s.current_risk * 10) / 10 || '-' || ROUND((s.current_risk * 10 + 1)) / 10 as risk_band
FROM symbols s
LEFT JOIN time_spent_bands tsb ON s.symbol = tsb.symbol 
    AND s.current_risk >= tsb.band_start 
    AND s.current_risk < tsb.band_end
WHERE s.is_active = 1
ORDER BY s.current_risk DESC;

-- Active manual overrides view
CREATE VIEW v_active_overrides AS
SELECT 
    symbol,
    override_type,
    override_value,
    previous_value,
    override_reason,
    created_by,
    created_date
FROM manual_overrides
WHERE is_active = 1
ORDER BY symbol, override_type;

-- =====================================================
-- TRIGGERS FOR AUDIT LOGGING
-- =====================================================

-- Trigger for symbols table changes
CREATE TRIGGER tr_symbols_audit
AFTER UPDATE ON symbols
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id, old_values, new_values)
    VALUES (
        'symbols', 
        'UPDATE', 
        NEW.symbol,
        json_object('price', OLD.current_price, 'risk', OLD.current_risk),
        json_object('price', NEW.current_price, 'risk', NEW.current_risk)
    );
END;

-- Trigger for manual overrides
CREATE TRIGGER tr_overrides_audit
AFTER INSERT ON manual_overrides
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id, new_values, changed_by)
    VALUES (
        'manual_overrides',
        'INSERT',
        NEW.symbol || '_' || NEW.override_type,
        json_object('type', NEW.override_type, 'value', NEW.override_value, 'reason', NEW.override_reason),
        NEW.created_by
    );
END;

-- =====================================================
-- INITIAL SYSTEM CONFIGURATION
-- =====================================================

INSERT INTO system_config (key, value, description) VALUES
('version', '1.0.0', 'RiskMetric Database Agent Version'),
('methodology', 'Benjamin Cowen Logarithmic Regression', 'Risk calculation methodology'),
('last_formula_update', '2025-08-03', 'Last time regression formulas were updated'),
('api_rate_limit', '100', 'API requests per hour limit'),
('daily_update_time', '00:00', 'Time for daily automated updates'),
('coefficient_range_min', '1.0', 'Minimum coefficient value'),
('coefficient_range_max', '1.6', 'Maximum coefficient value'),
('risk_bands_count', '10', 'Number of risk bands (0.1 increments)'),
('supported_symbols_count', '17', 'Number of supported symbols'),
('database_schema_version', '1.0', 'Database schema version');

-- =====================================================
-- SAMPLE DATA VALIDATION QUERIES
-- =====================================================

-- Check data integrity
-- SELECT 'Symbols without risk levels' as check_type, COUNT(*) as count
-- FROM symbols s 
-- LEFT JOIN risk_levels rl ON s.symbol = rl.symbol 
-- WHERE rl.symbol IS NULL AND s.is_active = 1;

-- SELECT 'Risk levels without symbols' as check_type, COUNT(*) as count
-- FROM risk_levels rl 
-- LEFT JOIN symbols s ON rl.symbol = s.symbol 
-- WHERE s.symbol IS NULL;

-- SELECT 'Symbols without time spent data' as check_type, COUNT(*) as count
-- FROM symbols s 
-- LEFT JOIN time_spent_bands tsb ON s.symbol = tsb.symbol 
-- WHERE tsb.symbol IS NULL AND s.is_active = 1;

-- =====================================================
-- USEFUL MAINTENANCE QUERIES
-- =====================================================

-- Get symbols that need formula updates
-- SELECT symbol, name, confidence_level
-- FROM symbols 
-- WHERE symbol NOT IN (
--     SELECT DISTINCT symbol FROM regression_formulas
-- ) AND is_active = 1;

-- Get symbols with active manual overrides
-- SELECT s.symbol, s.name, COUNT(mo.id) as override_count
-- FROM symbols s
-- JOIN manual_overrides mo ON s.symbol = mo.symbol
-- WHERE mo.is_active = 1
-- GROUP BY s.symbol, s.name;

-- Get risk distribution summary
-- SELECT 
--     CASE 
--         WHEN current_risk < 0.2 THEN 'Very Low (0.0-0.2)'
--         WHEN current_risk < 0.4 THEN 'Low (0.2-0.4)'
--         WHEN current_risk < 0.6 THEN 'Medium (0.4-0.6)'
--         WHEN current_risk < 0.8 THEN 'High (0.6-0.8)'
--         ELSE 'Very High (0.8-1.0)'
--     END as risk_category,
--     COUNT(*) as symbol_count
-- FROM symbols 
-- WHERE is_active = 1
-- GROUP BY risk_category
-- ORDER BY MIN(current_risk);

-- =====================================================
-- SCHEMA VALIDATION
-- =====================================================

-- Verify all tables exist
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Verify all indexes exist
-- SELECT name FROM sqlite_master WHERE type='index' ORDER BY name;

-- Verify all views exist
-- SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;

-- Verify all triggers exist
-- SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name;

-- =====================================================
-- END OF SCHEMA
-- =====================================================

