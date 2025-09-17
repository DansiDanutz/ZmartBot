-- Alert Collection Agent - Supabase Database Schema
-- Professional alert management system with MDC documentation and Manus integration

-- =====================================================
-- 1. ALERT COLLECTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    source_server TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    timeframe TEXT,
    signal_strength DECIMAL(5,3),
    confidence_score DECIMAL(5,3),
    technical_data JSONB,
    riskmetric_data JSONB,
    cryptometer_data JSONB,
    market_conditions JSONB,
    action_recommendation TEXT,
    priority_level TEXT CHECK (priority_level IN ('low', 'medium', 'high', 'extraordinary')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'collected', 'processed', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. ALERT REPORTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    alert_summary TEXT NOT NULL,
    technical_analysis TEXT,
    risk_assessment TEXT,
    market_context TEXT,
    action_plan TEXT,
    confidence_rating TEXT CHECK (confidence_rating IN ('Low', 'Medium', 'High', 'Extraordinary')),
    mdc_content TEXT,
    md_content TEXT,
    data_sources JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    report_version INTEGER DEFAULT 1,

    -- Ensure only one active report per symbol
    CONSTRAINT unique_active_symbol EXCLUDE (symbol WITH =) WHERE (is_active = true)
);

-- =====================================================
-- 3. SYMBOL COVERAGE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS symbol_coverage (
    symbol TEXT PRIMARY KEY,
    last_alert_time TIMESTAMPTZ,
    alert_count INTEGER DEFAULT 0,
    best_alert_confidence DECIMAL(5,3) DEFAULT 0,
    status TEXT DEFAULT 'needs_alert' CHECK (status IN ('needs_alert', 'covered', 'monitored')),
    coverage_quality_score DECIMAL(5,3) DEFAULT 0,
    last_mdc_generation TIMESTAMPTZ,
    last_manus_report TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 4. MANUS EXTRAORDINARY REPORTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS manus_extraordinary_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    alert_id TEXT REFERENCES alert_collections(alert_id),
    manus_prompt TEXT NOT NULL,
    manus_response TEXT,
    extraordinary_score DECIMAL(5,3),
    market_intelligence JSONB,
    strategic_insights JSONB,
    risk_analysis JSONB,
    execution_plan JSONB,
    prompt_tokens INTEGER,
    response_tokens INTEGER,
    processing_time_ms INTEGER,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- =====================================================
-- 5. MDC DOCUMENTATION TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS mdc_documentation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('alert_report', 'technical_analysis', 'risk_assessment', 'action_plan')),
    mdc_content TEXT NOT NULL,
    md_content TEXT,
    version TEXT DEFAULT '1.0.0',
    owner TEXT DEFAULT 'zmartbot',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deprecated')),
    metadata JSONB,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 6. ALERT AGENT STATISTICS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_agent_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alerts_collected INTEGER DEFAULT 0,
    alerts_processed INTEGER DEFAULT 0,
    reports_generated INTEGER DEFAULT 0,
    manus_reports INTEGER DEFAULT 0,
    symbols_covered INTEGER DEFAULT 0,
    mdc_documents_created INTEGER DEFAULT 0,
    average_confidence_score DECIMAL(5,3),
    processing_time_avg_ms INTEGER,
    success_rate DECIMAL(5,3),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_duration_minutes INTEGER,
    errors_count INTEGER DEFAULT 0,
    performance_metrics JSONB
);

-- =====================================================
-- 7. PROMPT TEMPLATES TABLE (for Anthropic Prompt MCP)
-- =====================================================
CREATE TABLE IF NOT EXISTS prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name TEXT UNIQUE NOT NULL,
    template_type TEXT NOT NULL CHECK (template_type IN ('mdc_generation', 'manus_analysis', 'technical_analysis', 'risk_assessment')),
    template_content TEXT NOT NULL,
    variables JSONB,
    example_usage TEXT,
    performance_rating DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    created_by TEXT DEFAULT 'alert_agent',
    version TEXT DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 8. ALERT FUSION DATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_fusion_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    fusion_timestamp TIMESTAMPTZ NOT NULL,
    whale_alerts_data JSONB,
    messi_alerts_data JSONB,
    live_alerts_data JSONB,
    maradona_alerts_data JSONB,
    pele_alerts_data JSONB,
    riskmetric_data JSONB,
    cryptometer_data JSONB,
    fusion_score DECIMAL(5,3),
    consensus_rating TEXT,
    market_regime TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Alert Collections indexes
CREATE INDEX IF NOT EXISTS idx_alert_collections_symbol ON alert_collections(symbol);
CREATE INDEX IF NOT EXISTS idx_alert_collections_timestamp ON alert_collections(timestamp);
CREATE INDEX IF NOT EXISTS idx_alert_collections_priority ON alert_collections(priority_level);
CREATE INDEX IF NOT EXISTS idx_alert_collections_status ON alert_collections(status);
CREATE INDEX IF NOT EXISTS idx_alert_collections_confidence ON alert_collections(confidence_score);

-- Alert Reports indexes
CREATE INDEX IF NOT EXISTS idx_alert_reports_symbol ON alert_reports(symbol);
CREATE INDEX IF NOT EXISTS idx_alert_reports_active ON alert_reports(is_active);
CREATE INDEX IF NOT EXISTS idx_alert_reports_confidence ON alert_reports(confidence_rating);
CREATE INDEX IF NOT EXISTS idx_alert_reports_created_at ON alert_reports(created_at);

-- Symbol Coverage indexes
CREATE INDEX IF NOT EXISTS idx_symbol_coverage_status ON symbol_coverage(status);
CREATE INDEX IF NOT EXISTS idx_symbol_coverage_last_alert ON symbol_coverage(last_alert_time);

-- Manus Reports indexes
CREATE INDEX IF NOT EXISTS idx_manus_reports_symbol ON manus_extraordinary_reports(symbol);
CREATE INDEX IF NOT EXISTS idx_manus_reports_status ON manus_extraordinary_reports(status);
CREATE INDEX IF NOT EXISTS idx_manus_reports_score ON manus_extraordinary_reports(extraordinary_score);

-- MDC Documentation indexes
CREATE INDEX IF NOT EXISTS idx_mdc_docs_symbol ON mdc_documentation(symbol);
CREATE INDEX IF NOT EXISTS idx_mdc_docs_type ON mdc_documentation(document_type);
CREATE INDEX IF NOT EXISTS idx_mdc_docs_status ON mdc_documentation(status);

-- Prompt Templates indexes
CREATE INDEX IF NOT EXISTS idx_prompt_templates_type ON prompt_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_active ON prompt_templates(is_active);

-- Alert Fusion indexes
CREATE INDEX IF NOT EXISTS idx_alert_fusion_symbol ON alert_fusion_data(symbol);
CREATE INDEX IF NOT EXISTS idx_alert_fusion_timestamp ON alert_fusion_data(fusion_timestamp);
CREATE INDEX IF NOT EXISTS idx_alert_fusion_score ON alert_fusion_data(fusion_score);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_alert_collections_updated_at
    BEFORE UPDATE ON alert_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_reports_updated_at
    BEFORE UPDATE ON alert_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_symbol_coverage_updated_at
    BEFORE UPDATE ON symbol_coverage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mdc_documentation_updated_at
    BEFORE UPDATE ON mdc_documentation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompt_templates_updated_at
    BEFORE UPDATE ON prompt_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE alert_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE symbol_coverage ENABLE ROW LEVEL SECURITY;
ALTER TABLE manus_extraordinary_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE mdc_documentation ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_agent_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_fusion_data ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for service role, read for authenticated users)
CREATE POLICY "Enable all operations for service role" ON alert_collections FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON alert_collections FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON alert_reports FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON alert_reports FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON symbol_coverage FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON symbol_coverage FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON manus_extraordinary_reports FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON manus_extraordinary_reports FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON mdc_documentation FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON mdc_documentation FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON alert_agent_statistics FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON alert_agent_statistics FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON prompt_templates FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON prompt_templates FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for service role" ON alert_fusion_data FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable read for authenticated users" ON alert_fusion_data FOR SELECT USING (auth.role() = 'authenticated');

-- =====================================================
-- INITIAL DATA - PROMPT TEMPLATES
-- =====================================================

INSERT INTO prompt_templates (template_name, template_type, template_content, variables, example_usage) VALUES
('mdc_alert_report', 'mdc_generation',
'# {{symbol}} Alert Report - ZmartBot Professional Analysis

> Type: alert-report | Version: {{version}} | Owner: {{owner}} | Generated: {{timestamp}}

## Executive Summary

{{alert_summary}}

## Technical Analysis

{{technical_analysis}}

## Risk Assessment

{{risk_assessment}}

## Market Context

{{market_context}}

## Recommended Actions

{{action_plan}}

## Data Sources

{{data_sources}}

## Confidence Rating: {{confidence_rating}}

---
*Generated by ZmartBot Alert Collection Agent*',
'{"symbol": "string", "version": "string", "owner": "string", "timestamp": "string", "alert_summary": "string", "technical_analysis": "string", "risk_assessment": "string", "market_context": "string", "action_plan": "string", "data_sources": "array", "confidence_rating": "string"}',
'Use for generating MDC documentation for alert reports'),

('manus_extraordinary_analysis', 'manus_analysis',
'You are an elite cryptocurrency trading intelligence analyst. Analyze the following extraordinary alert with institutional-grade precision:

**ALERT CONTEXT**:
Symbol: {{symbol}}
Confidence: {{confidence_score}}%
Signal Strength: {{signal_strength}}
Source: {{source_server}}
Timeframe: {{timeframe}}

**TECHNICAL DATA**:
{{technical_data}}

**RISKMETRIC ANALYSIS**:
{{riskmetric_data}}

**CRYPTOMETER INTELLIGENCE**:
{{cryptometer_data}}

**MARKET CONDITIONS**:
{{market_conditions}}

**ANALYSIS REQUIREMENTS**:
1. **Institutional Perspective**: Analyze from hedge fund/institutional viewpoint
2. **Risk-Adjusted Returns**: Calculate Sharpe ratio implications
3. **Market Microstructure**: Order flow and liquidity analysis
4. **Positioning Strategy**: Entry/exit methodology with position sizing
5. **Catalyst Analysis**: Fundamental and technical drivers
6. **Regime Assessment**: Current market cycle positioning

**OUTPUT FORMAT**:
- Executive Summary (2-3 sentences)
- Deep Market Analysis (detailed institutional insights)
- Risk-Reward Assessment (quantified metrics)
- Strategic Positioning (specific actionable recommendations)
- Market Timing (optimal execution windows)
- Portfolio Implications (correlation and diversification effects)

Provide sophisticated, actionable intelligence worthy of the extraordinary confidence rating.',
'{"symbol": "string", "confidence_score": "number", "signal_strength": "number", "source_server": "string", "timeframe": "string", "technical_data": "object", "riskmetric_data": "object", "cryptometer_data": "object", "market_conditions": "object"}',
'Use for generating Manus extraordinary analysis reports'),

('technical_analysis_comprehensive', 'technical_analysis',
'Conduct comprehensive technical analysis for {{symbol}}:

**MULTI-TIMEFRAME ANALYSIS**:
{{timeframe_data}}

**INDICATOR CONFLUENCE**:
{{technical_indicators}}

**PATTERN RECOGNITION**:
{{chart_patterns}}

**VOLUME ANALYSIS**:
{{volume_data}}

**MARKET STRUCTURE**:
{{market_structure}}

Provide:
1. Primary trend direction and strength
2. Support/resistance levels with confluence
3. Momentum analysis across timeframes
4. Volume confirmation or divergence
5. Pattern completion probabilities
6. Risk/reward calculations
7. Optimal entry and exit levels',
'{"symbol": "string", "timeframe_data": "object", "technical_indicators": "object", "chart_patterns": "object", "volume_data": "object", "market_structure": "object"}',
'Use for comprehensive technical analysis generation'),

('risk_assessment_professional', 'risk_assessment',
'Professional risk assessment for {{symbol}} position:

**VOLATILITY ANALYSIS**:
{{volatility_metrics}}

**CORRELATION MATRIX**:
{{correlations}}

**LIQUIDITY ASSESSMENT**:
{{liquidity_data}}

**DRAWDOWN SCENARIOS**:
{{risk_scenarios}}

**PORTFOLIO IMPACT**:
{{portfolio_context}}

Generate:
1. VaR calculations (1%, 5%, 10% scenarios)
2. Maximum drawdown estimates
3. Position sizing recommendations
4. Stop-loss placement strategy
5. Portfolio correlation effects
6. Liquidity risk assessment
7. Stress test scenarios',
'{"symbol": "string", "volatility_metrics": "object", "correlations": "object", "liquidity_data": "object", "risk_scenarios": "object", "portfolio_context": "object"}',
'Use for professional risk assessment generation');

-- =====================================================
-- VIEWS FOR EASY QUERYING
-- =====================================================

-- Active alerts summary view
CREATE OR REPLACE VIEW active_alerts_summary AS
SELECT
    symbol,
    COUNT(*) as alert_count,
    AVG(confidence_score) as avg_confidence,
    MAX(confidence_score) as max_confidence,
    array_agg(DISTINCT alert_type) as alert_types,
    array_agg(DISTINCT source_server) as sources,
    MAX(timestamp) as latest_alert
FROM alert_collections
WHERE status = 'processed'
    AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY symbol
ORDER BY max_confidence DESC, alert_count DESC;

-- Symbol coverage status view
CREATE OR REPLACE VIEW symbol_coverage_status AS
SELECT
    sc.symbol,
    sc.status,
    sc.last_alert_time,
    sc.alert_count,
    sc.best_alert_confidence,
    ar.confidence_rating as current_report_rating,
    ar.created_at as report_created_at,
    CASE
        WHEN sc.last_alert_time > NOW() - INTERVAL '6 hours' THEN 'fresh'
        WHEN sc.last_alert_time > NOW() - INTERVAL '24 hours' THEN 'recent'
        ELSE 'stale'
    END as freshness_status
FROM symbol_coverage sc
LEFT JOIN alert_reports ar ON sc.symbol = ar.symbol AND ar.is_active = true
ORDER BY sc.best_alert_confidence DESC;

-- Manus extraordinary reports summary
CREATE OR REPLACE VIEW manus_reports_summary AS
SELECT
    symbol,
    COUNT(*) as report_count,
    AVG(extraordinary_score) as avg_score,
    MAX(extraordinary_score) as max_score,
    AVG(prompt_tokens) as avg_prompt_tokens,
    AVG(response_tokens) as avg_response_tokens,
    AVG(processing_time_ms) as avg_processing_time,
    MAX(created_at) as latest_report
FROM manus_extraordinary_reports
WHERE status = 'completed'
GROUP BY symbol
ORDER BY max_score DESC;

-- Performance metrics view
CREATE OR REPLACE VIEW agent_performance_metrics AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(alerts_collected) as avg_alerts_collected,
    AVG(alerts_processed) as avg_alerts_processed,
    AVG(reports_generated) as avg_reports_generated,
    AVG(success_rate) as avg_success_rate,
    AVG(processing_time_avg_ms) as avg_processing_time,
    COUNT(*) as measurement_count
FROM alert_agent_statistics
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;