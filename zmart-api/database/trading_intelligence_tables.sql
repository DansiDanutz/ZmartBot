-- 🔥 ZmartBot Trading Intelligence Tables for Supabase
-- Execute this SQL in Supabase SQL Editor to create all trading intelligence tables
-- Project: asjtxrmftmutcsnqgidy.supabase.co

-- ===================================================================
-- TRADING INTELLIGENCE CORE TABLES
-- ===================================================================

-- 1. Trading Analyses Table - Core analysis storage
CREATE TABLE IF NOT EXISTS trading_analyses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    ai_consensus JSONB DEFAULT '{}',
    kingfisher_data JSONB DEFAULT '{}',
    cryptometer_data JSONB DEFAULT '{}',
    binance_data JSONB DEFAULT '{}',
    kucoin_data JSONB DEFAULT '{}',
    coingecko_data JSONB DEFAULT '{}',
    patterns_detected JSONB DEFAULT '[]',
    confidence_score DECIMAL(5,2) DEFAULT 0.0,
    risk_level VARCHAR(20) DEFAULT 'unknown',
    recommendation TEXT DEFAULT '',
    trading_signals JSONB DEFAULT '{}',
    market_conditions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Pattern Library - ML pattern recognition
CREATE TABLE IF NOT EXISTS pattern_library (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    description TEXT DEFAULT '',
    historical_accuracy DECIMAL(5,2) DEFAULT 0.0,
    market_conditions VARCHAR(100) DEFAULT 'any',
    timeframe VARCHAR(20) DEFAULT '1h',
    pattern_data JSONB DEFAULT '{}',
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    last_detected TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Smart Alerts System - Advanced alerting
CREATE TABLE IF NOT EXISTS smart_alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) DEFAULT 'system',
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    trigger_condition JSONB DEFAULT '{}',
    threshold_value DECIMAL(15,8) DEFAULT 0.0,
    current_value DECIMAL(15,8) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    priority VARCHAR(10) DEFAULT 'MEDIUM',
    message TEXT DEFAULT '',
    alert_data JSONB DEFAULT '{}',
    triggered_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Portfolio Analytics - Performance tracking
CREATE TABLE IF NOT EXISTS portfolio_analytics (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(100) NOT NULL,
    total_value DECIMAL(20,8) DEFAULT 0.0,
    daily_pnl DECIMAL(20,8) DEFAULT 0.0,
    weekly_pnl DECIMAL(20,8) DEFAULT 0.0,
    monthly_pnl DECIMAL(20,8) DEFAULT 0.0,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    diversification_score DECIMAL(5,2) DEFAULT 0.0,
    sharpe_ratio DECIMAL(8,4) DEFAULT 0.0,
    max_drawdown DECIMAL(5,2) DEFAULT 0.0,
    ai_recommendations JSONB DEFAULT '[]',
    optimization_suggestions JSONB DEFAULT '[]',
    performance_metrics JSONB DEFAULT '{}',
    allocation_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Market Sentiment History - Sentiment tracking
CREATE TABLE IF NOT EXISTS market_sentiment_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    sentiment_score DECIMAL(5,2) DEFAULT 0.0,
    fear_greed_index INTEGER DEFAULT 50,
    social_sentiment JSONB DEFAULT '{}',
    news_sentiment JSONB DEFAULT '{}',
    technical_sentiment JSONB DEFAULT '{}',
    ai_sentiment JSONB DEFAULT '{}',
    overall_sentiment VARCHAR(20) DEFAULT 'NEUTRAL',
    confidence DECIMAL(5,2) DEFAULT 0.0,
    data_sources JSONB DEFAULT '[]',
    volume_24h DECIMAL(20,8) DEFAULT 0.0,
    price_change_24h DECIMAL(10,4) DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. AI Model Performance - Model tracking
CREATE TABLE IF NOT EXISTS ai_model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    prediction_accuracy DECIMAL(5,2) DEFAULT 0.0,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    avg_confidence DECIMAL(5,2) DEFAULT 0.0,
    performance_metrics JSONB DEFAULT '{}',
    last_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Risk Assessments - Risk management
CREATE TABLE IF NOT EXISTS risk_assessments (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) DEFAULT 'MEDIUM',
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    volatility DECIMAL(8,4) DEFAULT 0.0,
    liquidity_risk DECIMAL(5,2) DEFAULT 0.0,
    market_risk DECIMAL(5,2) DEFAULT 0.0,
    correlation_risk DECIMAL(5,2) DEFAULT 0.0,
    risk_factors JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    mitigation_strategies JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Intelligence Cache - Performance caching
CREATE TABLE IF NOT EXISTS intelligence_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    cache_data JSONB NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- PERFORMANCE INDEXES
-- ===================================================================

-- Trading Analyses indexes
CREATE INDEX IF NOT EXISTS idx_trading_analyses_symbol ON trading_analyses(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_analyses_created_at ON trading_analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_trading_analyses_type ON trading_analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_trading_analyses_confidence ON trading_analyses(confidence_score);

-- Pattern Library indexes
CREATE INDEX IF NOT EXISTS idx_pattern_library_type ON pattern_library(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_library_accuracy ON pattern_library(historical_accuracy);
CREATE INDEX IF NOT EXISTS idx_pattern_library_usage ON pattern_library(usage_count);

-- Smart Alerts indexes
CREATE INDEX IF NOT EXISTS idx_smart_alerts_symbol ON smart_alerts(symbol);
CREATE INDEX IF NOT EXISTS idx_smart_alerts_status ON smart_alerts(status);
CREATE INDEX IF NOT EXISTS idx_smart_alerts_priority ON smart_alerts(priority);
CREATE INDEX IF NOT EXISTS idx_smart_alerts_user ON smart_alerts(user_id);

-- Portfolio Analytics indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_portfolio_id ON portfolio_analytics(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_created_at ON portfolio_analytics(created_at);

-- Market Sentiment indexes
CREATE INDEX IF NOT EXISTS idx_market_sentiment_symbol ON market_sentiment_history(symbol);
CREATE INDEX IF NOT EXISTS idx_market_sentiment_timestamp ON market_sentiment_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_sentiment_overall ON market_sentiment_history(overall_sentiment);

-- AI Model Performance indexes
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_name ON ai_model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_type ON ai_model_performance(model_type);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_accuracy ON ai_model_performance(prediction_accuracy);

-- Risk Assessments indexes
CREATE INDEX IF NOT EXISTS idx_risk_assessments_symbol ON risk_assessments(symbol);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_type ON risk_assessments(assessment_type);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_level ON risk_assessments(risk_level);

-- Intelligence Cache indexes
CREATE INDEX IF NOT EXISTS idx_intelligence_cache_key ON intelligence_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_intelligence_cache_expires ON intelligence_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_intelligence_cache_type ON intelligence_cache(data_type);

-- ===================================================================
-- SAMPLE DATA FOR TESTING
-- ===================================================================

-- Insert sample AI model performance data
INSERT INTO ai_model_performance (model_name, model_type, prediction_accuracy, total_predictions, correct_predictions, avg_confidence, performance_metrics)
VALUES 
    ('claude_max_v1', 'language_model', 87.5, 1000, 875, 92.3, '{"precision": 0.89, "recall": 0.86, "f1_score": 0.875}'::jsonb),
    ('gpt5_pro_v1', 'language_model', 89.2, 1200, 1070, 91.8, '{"precision": 0.91, "recall": 0.87, "f1_score": 0.892}'::jsonb),
    ('gemini_1_5_pro', 'language_model', 86.8, 950, 825, 90.5, '{"precision": 0.88, "recall": 0.85, "f1_score": 0.868}'::jsonb)
ON CONFLICT (model_name) DO NOTHING;

-- Insert sample pattern library data
INSERT INTO pattern_library (pattern_name, pattern_type, description, historical_accuracy, market_conditions, timeframe, pattern_data, success_rate)
VALUES 
    ('Double Top', 'reversal', 'Bearish reversal pattern indicating potential downtrend', 78.5, 'trending', '4h', '{"confirmation_volume": true, "timeframe_specific": true}'::jsonb, 78.5),
    ('Bull Flag', 'continuation', 'Bullish continuation pattern in uptrends', 82.3, 'uptrend', '1h', '{"volume_confirmation": true, "breakout_target": true}'::jsonb, 82.3),
    ('Head and Shoulders', 'reversal', 'Classic reversal pattern at trend tops', 75.8, 'trending', '4h', '{"neckline_break": true, "volume_decline": true}'::jsonb, 75.8)
ON CONFLICT (pattern_name) DO NOTHING;

-- Insert sample market sentiment data
INSERT INTO market_sentiment_history (symbol, sentiment_score, fear_greed_index, social_sentiment, technical_sentiment, overall_sentiment, confidence)
VALUES 
    ('BTC/USDT', 65.5, 72, '{"twitter": 0.68, "reddit": 0.62, "news": 0.71}'::jsonb, '{"rsi": 58, "macd": "bullish", "sma_trend": "up"}'::jsonb, 'BULLISH', 85.2),
    ('ETH/USDT', 58.3, 68, '{"twitter": 0.61, "reddit": 0.55, "news": 0.58}'::jsonb, '{"rsi": 54, "macd": "neutral", "sma_trend": "sideways"}'::jsonb, 'NEUTRAL', 76.8),
    ('SOL/USDT', 72.1, 78, '{"twitter": 0.75, "reddit": 0.69, "news": 0.73}'::jsonb, '{"rsi": 62, "macd": "bullish", "sma_trend": "up"}'::jsonb, 'BULLISH', 88.9)
ON CONFLICT DO NOTHING;

-- ===================================================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- ===================================================================

-- Enable RLS on tables (optional, uncomment if needed)
-- ALTER TABLE trading_analyses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE pattern_library ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE smart_alerts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE portfolio_analytics ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE market_sentiment_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ai_model_performance ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE risk_assessments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE intelligence_cache ENABLE ROW LEVEL SECURITY;

-- ===================================================================
-- VERIFICATION QUERIES
-- ===================================================================

-- Verify tables were created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'trading_analyses', 'pattern_library', 'smart_alerts', 
    'portfolio_analytics', 'market_sentiment_history', 
    'ai_model_performance', 'risk_assessments', 'intelligence_cache'
)
ORDER BY tablename;

-- Verify indexes were created
SELECT 
    schemaname,
    indexname,
    tablename
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Check sample data
SELECT 'ai_model_performance' as table_name, COUNT(*) as row_count FROM ai_model_performance
UNION ALL
SELECT 'pattern_library' as table_name, COUNT(*) as row_count FROM pattern_library
UNION ALL
SELECT 'market_sentiment_history' as table_name, COUNT(*) as row_count FROM market_sentiment_history;

-- ===================================================================
-- SETUP COMPLETE
-- ===================================================================

/*
🎉 TRADING INTELLIGENCE TABLES SETUP COMPLETE!

Tables Created:
- trading_analyses (Core analysis storage)
- pattern_library (ML pattern recognition)
- smart_alerts (Advanced alerting system)
- portfolio_analytics (Performance tracking)
- market_sentiment_history (Sentiment analysis)
- ai_model_performance (Model tracking)
- risk_assessments (Risk management)
- intelligence_cache (Performance caching)

Performance Indexes: 24 indexes created
Sample Data: 3 AI models, 3 patterns, 3 market sentiment records

Next Steps:
1. Verify all tables are accessible in Supabase dashboard
2. Update unified_trading_intelligence_gateway.py to use Supabase
3. Test integration with all trading services
4. Configure RLS policies if needed

Integration Ready: ✅
*/