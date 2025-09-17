-- Cryptometer Database Migration
-- Creates comprehensive tables for Cryptometer autonomous system data storage
-- Run this migration to implement Cryptometer in Supabase

-- ========================================
-- CRYPTOMETER MULTI-TIMEFRAME ANALYSIS TABLES
-- ========================================

-- 1. Cryptometer Symbol Analysis - Main table for symbol analysis data
CREATE TABLE IF NOT EXISTS cryptometer_symbol_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Multi-timeframe scores
    short_term_score NUMERIC(5,2) CHECK (short_term_score >= 0 AND short_term_score <= 100),
    medium_term_score NUMERIC(5,2) CHECK (medium_term_score >= 0 AND medium_term_score <= 100),
    long_term_score NUMERIC(5,2) CHECK (long_term_score >= 0 AND long_term_score <= 100),

    -- AI recommendations
    ai_recommendation JSONB,
    primary_timeframe VARCHAR(10), -- SHORT, MEDIUM, LONG
    primary_action VARCHAR(20), -- ALL_IN, AGGRESSIVE, MODERATE, CONSERVATIVE, AVOID
    position_size VARCHAR(20), -- MAXIMUM, LARGE, MEDIUM, SMALL, NONE
    reasoning TEXT,

    -- Analysis metadata
    data_points_collected INTEGER DEFAULT 0,
    endpoints_called INTEGER DEFAULT 0,
    analysis_source VARCHAR(50) DEFAULT 'autonomous_cryptometer',

    -- Risk assessment
    risk_level VARCHAR(10), -- LOW, MEDIUM, HIGH
    confidence_score NUMERIC(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Raw analysis data
    raw_analysis_data JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Cryptometer Win Rate Predictions
CREATE TABLE IF NOT EXISTS cryptometer_win_rates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Timeframe-specific win rates
    short_term_24h_win_rate NUMERIC(3,2) CHECK (short_term_24h_win_rate >= 0 AND short_term_24h_win_rate <= 1),
    short_term_24h_confidence NUMERIC(3,2) CHECK (short_term_24h_confidence >= 0 AND short_term_24h_confidence <= 1),
    short_term_direction VARCHAR(10) DEFAULT 'neutral',

    medium_term_7d_win_rate NUMERIC(3,2) CHECK (medium_term_7d_win_rate >= 0 AND medium_term_7d_win_rate <= 1),
    medium_term_7d_confidence NUMERIC(3,2) CHECK (medium_term_7d_confidence >= 0 AND medium_term_7d_confidence <= 1),
    medium_term_direction VARCHAR(10) DEFAULT 'neutral',

    long_term_1m_win_rate NUMERIC(3,2) CHECK (long_term_1m_win_rate >= 0 AND long_term_1m_win_rate <= 1),
    long_term_1m_confidence NUMERIC(3,2) CHECK (long_term_1m_confidence >= 0 AND long_term_1m_confidence <= 1),
    long_term_direction VARCHAR(10) DEFAULT 'neutral',

    -- Overall metrics
    overall_confidence NUMERIC(3,2) CHECK (overall_confidence >= 0 AND overall_confidence <= 1),
    best_opportunity_timeframe VARCHAR(10),
    best_opportunity_win_rate NUMERIC(3,2),
    best_opportunity_direction VARCHAR(10),

    -- Prediction metadata
    model_type VARCHAR(50) DEFAULT 'cryptometer_multi_timeframe',
    prediction_source VARCHAR(50) DEFAULT 'ai_powered_analysis',
    reasoning TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Cryptometer API Endpoint Data - Store data from individual endpoints
CREATE TABLE IF NOT EXISTS cryptometer_endpoint_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    endpoint_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Endpoint response
    success BOOLEAN NOT NULL DEFAULT FALSE,
    response_data JSONB,
    error_message TEXT,

    -- Performance metrics
    response_time_ms INTEGER,
    data_points_extracted INTEGER DEFAULT 0,
    cached BOOLEAN DEFAULT FALSE,

    -- Endpoint metadata
    endpoint_url TEXT,
    endpoint_description TEXT,
    endpoint_weight INTEGER DEFAULT 1,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Cryptometer Autonomous System Status
CREATE TABLE IF NOT EXISTS cryptometer_system_status (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- System status
    agent_running BOOLEAN DEFAULT FALSE,
    last_successful_update TIMESTAMPTZ,
    next_update_due TIMESTAMPTZ,
    update_interval_hours INTEGER DEFAULT 24,

    -- Session statistics
    symbols_attempted INTEGER DEFAULT 0,
    symbols_successful INTEGER DEFAULT 0,
    symbols_failed INTEGER DEFAULT 0,
    total_endpoints_called INTEGER DEFAULT 0,
    total_data_points INTEGER DEFAULT 0,

    -- Session errors
    session_errors JSONB,
    failed_symbols TEXT[],

    -- System configuration
    api_configured BOOLEAN DEFAULT FALSE,
    autonomous_features JSONB,
    system_health VARCHAR(20) DEFAULT 'unknown',

    -- Session metadata
    session_duration_minutes NUMERIC(10,2),
    session_started_at TIMESTAMPTZ,
    session_completed_at TIMESTAMPTZ,
    session_id VARCHAR(50),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Cryptometer Pattern Analysis - Store trading patterns and confluences
CREATE TABLE IF NOT EXISTS cryptometer_patterns (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- SHORT, MEDIUM, LONG
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Pattern details
    pattern_type VARCHAR(50) NOT NULL,
    pattern_confidence NUMERIC(3,2) CHECK (pattern_confidence >= 0 AND pattern_confidence <= 1),
    pattern_description TEXT,

    -- Signal information
    signal VARCHAR(10), -- LONG, SHORT, NEUTRAL
    confluence_count INTEGER DEFAULT 1,
    confluence_multiplier NUMERIC(4,2) DEFAULT 1.0,
    final_score NUMERIC(5,2),
    base_scores JSONB,

    -- Pattern metadata
    base_success_rate NUMERIC(3,2),
    market_conditions JSONB,
    trade_type VARCHAR(20), -- SCALP_TRADE, SWING_TRADE, POSITION_TRADE

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Cryptometer Multi-Timeframe Summary - Daily summary view
CREATE TABLE IF NOT EXISTS cryptometer_daily_summary (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Best opportunities
    best_timeframe VARCHAR(10),
    best_score NUMERIC(5,2),
    best_action VARCHAR(20),
    best_win_rate NUMERIC(3,2),

    -- Timeframe breakdown
    short_patterns_count INTEGER DEFAULT 0,
    medium_patterns_count INTEGER DEFAULT 0,
    long_patterns_count INTEGER DEFAULT 0,

    -- System performance
    total_endpoints_called INTEGER DEFAULT 0,
    total_data_points INTEGER DEFAULT 0,
    analysis_success BOOLEAN DEFAULT TRUE,

    -- Summary data
    summary_data JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Primary indexes for symbol and timestamp queries
CREATE INDEX IF NOT EXISTS idx_cryptometer_symbol_analysis_symbol_timestamp ON cryptometer_symbol_analysis(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_win_rates_symbol_timestamp ON cryptometer_win_rates(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_endpoint_data_symbol_endpoint ON cryptometer_endpoint_data(symbol, endpoint_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_system_status_timestamp ON cryptometer_system_status(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_patterns_symbol_timeframe ON cryptometer_patterns(symbol, timeframe, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_daily_summary_symbol_date ON cryptometer_daily_summary(symbol, analysis_date DESC);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_cryptometer_symbol_analysis_score ON cryptometer_symbol_analysis(symbol, short_term_score DESC, medium_term_score DESC, long_term_score DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_win_rates_best_opportunity ON cryptometer_win_rates(symbol, best_opportunity_timeframe, best_opportunity_win_rate DESC);
CREATE INDEX IF NOT EXISTS idx_cryptometer_patterns_signal ON cryptometer_patterns(symbol, timeframe, signal, final_score DESC);

-- ========================================
-- UNIQUE CONSTRAINTS
-- ========================================

-- Note: Daily uniqueness will be handled at application level
-- PostgreSQL doesn't allow date functions in unique indexes
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_cryptometer_daily_summary_unique ON cryptometer_daily_summary(symbol, analysis_date);

-- ========================================
-- TABLE COMMENTS
-- ========================================

COMMENT ON TABLE cryptometer_symbol_analysis IS 'Main table storing multi-timeframe analysis results from Cryptometer autonomous system';
COMMENT ON TABLE cryptometer_win_rates IS 'AI-powered win rate predictions across different timeframes (24h, 7d, 1m)';
COMMENT ON TABLE cryptometer_endpoint_data IS 'Raw data from individual Cryptometer API endpoints (17 endpoints total)';
COMMENT ON TABLE cryptometer_system_status IS 'Autonomous system status and session statistics for monitoring';
COMMENT ON TABLE cryptometer_patterns IS 'Trading patterns and confluence analysis for each timeframe';
COMMENT ON TABLE cryptometer_daily_summary IS 'Daily summary of best opportunities and system performance';

-- Column comments
COMMENT ON COLUMN cryptometer_symbol_analysis.short_term_score IS 'SHORT term (24-48h) analysis score 0-100';
COMMENT ON COLUMN cryptometer_symbol_analysis.medium_term_score IS 'MEDIUM term (1 week) analysis score 0-100';
COMMENT ON COLUMN cryptometer_symbol_analysis.long_term_score IS 'LONG term (1 month+) analysis score 0-100';
COMMENT ON COLUMN cryptometer_win_rates.short_term_24h_win_rate IS 'Win rate prediction for 24h timeframe (0.0-1.0)';
COMMENT ON COLUMN cryptometer_win_rates.medium_term_7d_win_rate IS 'Win rate prediction for 7d timeframe (0.0-1.0)';
COMMENT ON COLUMN cryptometer_win_rates.long_term_1m_win_rate IS 'Win rate prediction for 1m timeframe (0.0-1.0)';

-- ========================================
-- ROW LEVEL SECURITY
-- ========================================

-- Enable RLS for data protection
ALTER TABLE cryptometer_symbol_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptometer_win_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptometer_endpoint_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptometer_system_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptometer_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptometer_daily_summary ENABLE ROW LEVEL SECURITY;

-- ========================================
-- SAMPLE VIEWS FOR EASY ACCESS
-- ========================================

-- Latest analysis view
CREATE OR REPLACE VIEW cryptometer_latest_analysis AS
SELECT
    symbol,
    short_term_score,
    medium_term_score,
    long_term_score,
    primary_timeframe,
    primary_action,
    confidence_score,
    timestamp,
    CASE
        WHEN short_term_score >= medium_term_score AND short_term_score >= long_term_score THEN 'SHORT'
        WHEN medium_term_score >= long_term_score THEN 'MEDIUM'
        ELSE 'LONG'
    END AS highest_scoring_timeframe
FROM cryptometer_symbol_analysis csa1
WHERE timestamp = (
    SELECT MAX(timestamp)
    FROM cryptometer_symbol_analysis csa2
    WHERE csa2.symbol = csa1.symbol
);

-- Best opportunities view
CREATE OR REPLACE VIEW cryptometer_best_opportunities AS
SELECT
    wr.symbol,
    wr.best_opportunity_timeframe,
    wr.best_opportunity_win_rate,
    wr.best_opportunity_direction,
    sa.primary_action,
    sa.confidence_score,
    sa.reasoning,
    wr.timestamp
FROM cryptometer_win_rates wr
JOIN cryptometer_symbol_analysis sa ON wr.symbol = sa.symbol
    AND wr.timestamp::date = sa.timestamp::date
WHERE wr.best_opportunity_win_rate > 0.7  -- Only show high probability opportunities
ORDER BY wr.best_opportunity_win_rate DESC;

-- System health view
CREATE OR REPLACE VIEW cryptometer_system_health AS
SELECT
    agent_running,
    last_successful_update,
    next_update_due,
    symbols_successful,
    symbols_failed,
    ROUND((symbols_successful::NUMERIC / NULLIF(symbols_attempted, 0)) * 100, 2) as success_rate_pct,
    total_data_points,
    system_health,
    timestamp
FROM cryptometer_system_status
ORDER BY timestamp DESC
LIMIT 1;

-- ========================================
-- COMPLETION MESSAGE
-- ========================================

DO $$
BEGIN
    RAISE NOTICE 'Cryptometer database schema created successfully!';
    RAISE NOTICE 'Tables created: 6 main tables + 3 views';
    RAISE NOTICE 'Features: Multi-timeframe analysis, Win rate predictions, Pattern analysis, System monitoring';
    RAISE NOTICE 'Ready for autonomous Cryptometer system integration';
END $$;