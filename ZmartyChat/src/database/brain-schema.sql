-- ==========================================
-- ZMARTY BRAIN MANAGEMENT SYSTEM - SUPABASE SCHEMA
-- ==========================================
-- Complete database schema for Zmarty's knowledge management
-- Designed for scalability, fast retrieval, and intelligent categorization

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector"; -- For embeddings and semantic search
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- ==========================================
-- CORE TABLES
-- ==========================================

-- Knowledge Categories (hierarchical)
CREATE TABLE IF NOT EXISTS brain_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    parent_id UUID REFERENCES brain_categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    level INTEGER DEFAULT 0,
    path TEXT, -- Materialized path for fast hierarchy queries
    icon VARCHAR(50),
    color VARCHAR(7),
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create indexes for categories
CREATE INDEX idx_brain_categories_parent ON brain_categories(parent_id);
CREATE INDEX idx_brain_categories_slug ON brain_categories(slug);
CREATE INDEX idx_brain_categories_path ON brain_categories USING gin(path gin_trgm_ops);
CREATE INDEX idx_brain_categories_active ON brain_categories(is_active) WHERE is_active = true;

-- Main Knowledge Base
CREATE TABLE IF NOT EXISTS brain_knowledge (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    category_id UUID REFERENCES brain_categories(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_md TEXT, -- Markdown version
    content_html TEXT, -- HTML version for display
    summary TEXT, -- AI-generated summary

    -- Knowledge Type Classification
    knowledge_type VARCHAR(50) CHECK (knowledge_type IN (
        'indicator', 'strategy', 'pattern', 'rule', 'concept',
        'market_insight', 'user_learning', 'api_cache', 'discovery',
        'alert', 'signal', 'risk', 'tutorial', 'faq'
    )),

    -- Source Information
    source_type VARCHAR(50) CHECK (source_type IN (
        'manual', 'api', 'user_interaction', 'discovery_agent',
        'market_analysis', 'backtest', 'simulation', 'external'
    )),
    source_reference VARCHAR(500),
    source_timestamp TIMESTAMP WITH TIME ZONE,

    -- Confidence and Validation
    confidence_score DECIMAL(3,2) DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (validation_status IN (
        'pending', 'validated', 'rejected', 'outdated', 'archived'
    )),
    validation_date TIMESTAMP WITH TIME ZONE,
    validated_by UUID,

    -- Usage Metrics
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    avg_response_time INTEGER, -- milliseconds

    -- Relationships
    parent_knowledge_id UUID REFERENCES brain_knowledge(id) ON DELETE SET NULL,
    related_knowledge_ids UUID[] DEFAULT '{}',
    prerequisite_ids UUID[] DEFAULT '{}',

    -- Search and Discovery
    keywords TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    embedding vector(1536), -- OpenAI embeddings for semantic search

    -- Metadata
    metadata JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    -- Unique constraint on slug within category
    UNIQUE(category_id, slug)
);

-- Comprehensive indexes for brain_knowledge
CREATE INDEX idx_brain_knowledge_category ON brain_knowledge(category_id);
CREATE INDEX idx_brain_knowledge_type ON brain_knowledge(knowledge_type);
CREATE INDEX idx_brain_knowledge_source ON brain_knowledge(source_type);
CREATE INDEX idx_brain_knowledge_confidence ON brain_knowledge(confidence_score DESC);
CREATE INDEX idx_brain_knowledge_usage ON brain_knowledge(usage_count DESC);
CREATE INDEX idx_brain_knowledge_accessed ON brain_knowledge(last_accessed DESC NULLS LAST);
CREATE INDEX idx_brain_knowledge_keywords ON brain_knowledge USING gin(keywords);
CREATE INDEX idx_brain_knowledge_tags ON brain_knowledge USING gin(tags);
CREATE INDEX idx_brain_knowledge_title_search ON brain_knowledge USING gin(title gin_trgm_ops);
CREATE INDEX idx_brain_knowledge_content_search ON brain_knowledge USING gin(content gin_trgm_ops);
CREATE INDEX idx_brain_knowledge_embedding ON brain_knowledge USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_brain_knowledge_active ON brain_knowledge(is_active) WHERE is_active = true;
CREATE INDEX idx_brain_knowledge_expires ON brain_knowledge(expires_at) WHERE expires_at IS NOT NULL;

-- Knowledge Revisions (version control)
CREATE TABLE IF NOT EXISTS brain_knowledge_revisions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    knowledge_id UUID REFERENCES brain_knowledge(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    title VARCHAR(500),
    content TEXT,
    changed_by UUID,
    change_reason TEXT,
    diff_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_knowledge_revisions_knowledge ON brain_knowledge_revisions(knowledge_id);
CREATE INDEX idx_knowledge_revisions_version ON brain_knowledge_revisions(knowledge_id, version DESC);

-- ==========================================
-- USER LEARNING TABLES
-- ==========================================

-- User Memory Profiles
CREATE TABLE IF NOT EXISTS brain_user_memory (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,

    -- User Profiling
    experience_level VARCHAR(20) CHECK (experience_level IN (
        'beginner', 'intermediate', 'advanced', 'expert'
    )),
    trading_style VARCHAR(50),
    risk_profile VARCHAR(20) CHECK (risk_profile IN (
        'conservative', 'moderate', 'aggressive'
    )),

    -- Preferences
    preferred_explanations VARCHAR(20) CHECK (preferred_explanations IN (
        'technical', 'simple', 'analogies'
    )),
    language_style VARCHAR(20) CHECK (language_style IN (
        'formal', 'casual', 'educational'
    )),
    detail_level VARCHAR(20) CHECK (detail_level IN (
        'brief', 'standard', 'comprehensive'
    )),

    -- Trading Preferences
    favorite_pairs TEXT[] DEFAULT '{}',
    preferred_strategies TEXT[] DEFAULT '{}',
    typical_position_size DECIMAL(10,2),
    risk_tolerance INTEGER CHECK (risk_tolerance >= 1 AND risk_tolerance <= 10),

    -- Performance Metrics
    total_interactions INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    failed_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    avg_return DECIMAL(5,2),

    -- Learning Progress
    knowledge_score INTEGER DEFAULT 0 CHECK (knowledge_score >= 0 AND knowledge_score <= 100),
    skill_progression JSONB DEFAULT '{}',
    milestones_achieved TEXT[] DEFAULT '{}',

    -- Behavioral Patterns
    common_questions JSONB DEFAULT '{}',
    trading_patterns JSONB DEFAULT '{}',
    success_patterns JSONB DEFAULT '{}',
    failure_patterns JSONB DEFAULT '{}',

    -- Metadata
    metadata JSONB DEFAULT '{}',
    last_active TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    UNIQUE(user_id)
);

CREATE INDEX idx_brain_user_memory_user ON brain_user_memory(user_id);
CREATE INDEX idx_brain_user_memory_level ON brain_user_memory(experience_level);
CREATE INDEX idx_brain_user_memory_active ON brain_user_memory(last_active DESC);

-- User Interactions History
CREATE TABLE IF NOT EXISTS brain_user_interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    knowledge_id UUID REFERENCES brain_knowledge(id) ON DELETE SET NULL,

    -- Interaction Details
    interaction_type VARCHAR(50) CHECK (interaction_type IN (
        'query', 'learn', 'apply', 'feedback', 'correction'
    )),
    question TEXT,
    answer TEXT,
    answer_source VARCHAR(50),

    -- Quality Metrics
    was_helpful BOOLEAN,
    confidence_score DECIMAL(3,2),
    response_time INTEGER, -- milliseconds

    -- Learning Outcome
    knowledge_gained TEXT[],
    patterns_identified TEXT[],

    -- Metadata
    context JSONB DEFAULT '{}',
    session_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_user_interactions_user ON brain_user_interactions(user_id);
CREATE INDEX idx_user_interactions_knowledge ON brain_user_interactions(knowledge_id);
CREATE INDEX idx_user_interactions_session ON brain_user_interactions(session_id);
CREATE INDEX idx_user_interactions_created ON brain_user_interactions(created_at DESC);

-- ==========================================
-- PATTERN & DISCOVERY TABLES
-- ==========================================

-- Discovered Patterns
CREATE TABLE IF NOT EXISTS brain_patterns (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    pattern_name VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(50) CHECK (pattern_type IN (
        'price', 'volume', 'user_behavior', 'market_correlation',
        'trading_setup', 'risk_pattern', 'success_pattern'
    )),

    -- Pattern Details
    description TEXT,
    conditions JSONB NOT NULL,
    expected_outcome JSONB,

    -- Statistical Validation
    occurrences INTEGER DEFAULT 1,
    success_rate DECIMAL(5,2),
    confidence_level DECIMAL(3,2),
    avg_return DECIMAL(5,2),

    -- Discovery Information
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    discovered_by VARCHAR(50), -- 'user', 'discovery_agent', 'analysis'

    -- Validation
    is_validated BOOLEAN DEFAULT false,
    validation_count INTEGER DEFAULT 0,
    failed_validations INTEGER DEFAULT 0,

    -- Usage
    times_used INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,

    -- Relationships
    related_patterns UUID[] DEFAULT '{}',
    required_indicators TEXT[] DEFAULT '{}',

    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN (
        'active', 'testing', 'retired', 'failed'
    )),

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_brain_patterns_type ON brain_patterns(pattern_type);
CREATE INDEX idx_brain_patterns_confidence ON brain_patterns(confidence_level DESC);
CREATE INDEX idx_brain_patterns_success ON brain_patterns(success_rate DESC);
CREATE INDEX idx_brain_patterns_status ON brain_patterns(status);
CREATE INDEX idx_brain_patterns_last_seen ON brain_patterns(last_seen DESC);

-- ==========================================
-- CACHING & PERFORMANCE TABLES
-- ==========================================

-- API Response Cache
CREATE TABLE IF NOT EXISTS brain_api_cache (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    cache_key VARCHAR(500) NOT NULL UNIQUE,
    query_hash VARCHAR(64) NOT NULL,

    -- Cache Content
    request_data JSONB,
    response_data JSONB NOT NULL,
    response_text TEXT,

    -- Source Information
    api_source VARCHAR(100),
    endpoint VARCHAR(255),

    -- Cache Management
    hit_count INTEGER DEFAULT 0,
    last_hit TIMESTAMP WITH TIME ZONE,
    ttl_seconds INTEGER,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Performance
    original_response_time INTEGER, -- milliseconds
    avg_saved_time INTEGER,

    -- Metadata
    tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_api_cache_key ON brain_api_cache(cache_key);
CREATE INDEX idx_api_cache_hash ON brain_api_cache(query_hash);
CREATE INDEX idx_api_cache_source ON brain_api_cache(api_source);
CREATE INDEX idx_api_cache_expires ON brain_api_cache(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_api_cache_hits ON brain_api_cache(hit_count DESC);

-- Query Performance Tracking
CREATE TABLE IF NOT EXISTS brain_query_performance (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    query_type VARCHAR(50),
    query_text TEXT,
    query_hash VARCHAR(64),

    -- Performance Metrics
    execution_time INTEGER, -- milliseconds
    rows_returned INTEGER,
    cache_hit BOOLEAN DEFAULT false,

    -- Source
    source_type VARCHAR(50),
    knowledge_ids UUID[] DEFAULT '{}',

    -- User Context
    user_id UUID,
    session_id UUID,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_query_performance_type ON brain_query_performance(query_type);
CREATE INDEX idx_query_performance_hash ON brain_query_performance(query_hash);
CREATE INDEX idx_query_performance_time ON brain_query_performance(execution_time);
CREATE INDEX idx_query_performance_created ON brain_query_performance(created_at DESC);

-- ==========================================
-- RELATIONSHIP TABLES
-- ==========================================

-- Knowledge Relationships
CREATE TABLE IF NOT EXISTS brain_knowledge_relationships (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source_id UUID REFERENCES brain_knowledge(id) ON DELETE CASCADE,
    target_id UUID REFERENCES brain_knowledge(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) CHECK (relationship_type IN (
        'requires', 'suggests', 'contradicts', 'enhances',
        'replaces', 'extends', 'examples', 'implements'
    )),
    strength DECIMAL(3,2) DEFAULT 0.5 CHECK (strength >= 0 AND strength <= 1),
    bidirectional BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    UNIQUE(source_id, target_id, relationship_type)
);

CREATE INDEX idx_knowledge_rel_source ON brain_knowledge_relationships(source_id);
CREATE INDEX idx_knowledge_rel_target ON brain_knowledge_relationships(target_id);
CREATE INDEX idx_knowledge_rel_type ON brain_knowledge_relationships(relationship_type);

-- ==========================================
-- LEARNING & EVOLUTION TABLES
-- ==========================================

-- Learning Queue
CREATE TABLE IF NOT EXISTS brain_learning_queue (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    learning_type VARCHAR(50) CHECK (learning_type IN (
        'new_pattern', 'user_feedback', 'market_event',
        'api_response', 'discovery', 'correction'
    )),

    -- Content to Learn
    content JSONB NOT NULL,
    source VARCHAR(100),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),

    -- Processing Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'skipped'
    )),
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Results
    knowledge_created UUID[],
    patterns_identified UUID[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_learning_queue_status ON brain_learning_queue(status);
CREATE INDEX idx_learning_queue_priority ON brain_learning_queue(priority DESC, created_at);
CREATE INDEX idx_learning_queue_type ON brain_learning_queue(learning_type);

-- Evolution Tracking
CREATE TABLE IF NOT EXISTS brain_evolution_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    evolution_type VARCHAR(50),
    description TEXT,

    -- Metrics Before/After
    metrics_before JSONB,
    metrics_after JSONB,
    improvement_percentage DECIMAL(5,2),

    -- Changes Made
    knowledge_added INTEGER DEFAULT 0,
    knowledge_updated INTEGER DEFAULT 0,
    patterns_discovered INTEGER DEFAULT 0,

    -- Impact
    affected_users INTEGER DEFAULT 0,
    queries_improved INTEGER DEFAULT 0,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

CREATE INDEX idx_evolution_log_type ON brain_evolution_log(evolution_type);
CREATE INDEX idx_evolution_log_created ON brain_evolution_log(created_at DESC);

-- ==========================================
-- FUNCTIONS AND TRIGGERS
-- ==========================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all relevant tables
CREATE TRIGGER update_brain_categories_updated_at BEFORE UPDATE ON brain_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_brain_knowledge_updated_at BEFORE UPDATE ON brain_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_brain_user_memory_updated_at BEFORE UPDATE ON brain_user_memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_brain_patterns_updated_at BEFORE UPDATE ON brain_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_brain_api_cache_updated_at BEFORE UPDATE ON brain_api_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function to increment usage count
CREATE OR REPLACE FUNCTION increment_knowledge_usage(knowledge_uuid UUID)
RETURNS void AS $$
BEGIN
    UPDATE brain_knowledge
    SET usage_count = usage_count + 1,
        last_accessed = TIMEZONE('utc', NOW())
    WHERE id = knowledge_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate knowledge confidence
CREATE OR REPLACE FUNCTION calculate_knowledge_confidence(
    p_usage_count INTEGER,
    p_success_count INTEGER,
    p_failure_count INTEGER,
    p_days_old INTEGER
) RETURNS DECIMAL AS $$
DECLARE
    base_confidence DECIMAL;
    age_factor DECIMAL;
    success_rate DECIMAL;
BEGIN
    -- Calculate success rate
    IF p_success_count + p_failure_count > 0 THEN
        success_rate := p_success_count::DECIMAL / (p_success_count + p_failure_count);
    ELSE
        success_rate := 0.5; -- Neutral if no data
    END IF;

    -- Calculate base confidence from usage and success
    base_confidence := (
        (LEAST(p_usage_count, 100) / 100.0 * 0.3) + -- Usage factor (30%)
        (success_rate * 0.7) -- Success factor (70%)
    );

    -- Apply age decay
    age_factor := GREATEST(0.5, 1.0 - (p_days_old / 365.0));

    RETURN LEAST(1.0, base_confidence * age_factor);
END;
$$ LANGUAGE plpgsql;

-- Function to find similar knowledge
CREATE OR REPLACE FUNCTION find_similar_knowledge(
    search_embedding vector(1536),
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE(
    id UUID,
    title VARCHAR(500),
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        k.id,
        k.title,
        1 - (k.embedding <=> search_embedding) as similarity
    FROM brain_knowledge k
    WHERE k.embedding IS NOT NULL
        AND k.is_active = true
    ORDER BY k.embedding <=> search_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- VIEWS FOR COMMON QUERIES
-- ==========================================

-- Active Knowledge View
CREATE OR REPLACE VIEW v_active_knowledge AS
SELECT
    k.*,
    c.name as category_name,
    c.path as category_path,
    (k.success_count::FLOAT / NULLIF(k.success_count + k.failure_count, 0)) as success_rate,
    EXTRACT(DAY FROM NOW() - k.created_at) as days_old
FROM brain_knowledge k
LEFT JOIN brain_categories c ON k.category_id = c.id
WHERE k.is_active = true
    AND k.validation_status = 'validated'
    AND (k.expires_at IS NULL OR k.expires_at > NOW());

-- User Learning Progress View
CREATE OR REPLACE VIEW v_user_learning_progress AS
SELECT
    um.*,
    COUNT(DISTINCT ui.id) as total_interactions,
    COUNT(DISTINCT DATE(ui.created_at)) as active_days,
    MAX(ui.created_at) as last_interaction
FROM brain_user_memory um
LEFT JOIN brain_user_interactions ui ON um.user_id = ui.user_id
GROUP BY um.id;

-- Pattern Performance View
CREATE OR REPLACE VIEW v_pattern_performance AS
SELECT
    p.*,
    EXTRACT(DAY FROM NOW() - p.first_seen) as days_active,
    CASE
        WHEN p.occurrences > 100 AND p.success_rate > 70 THEN 'proven'
        WHEN p.occurrences > 20 AND p.success_rate > 60 THEN 'promising'
        WHEN p.occurrences > 5 THEN 'testing'
        ELSE 'new'
    END as reliability_status
FROM brain_patterns p
WHERE p.status = 'active';

-- ==========================================
-- INITIAL DATA CATEGORIES
-- ==========================================

INSERT INTO brain_categories (name, slug, description, level, path, icon, color, priority) VALUES
-- Level 0 - Root Categories
('Core Knowledge', 'core-knowledge', 'Fundamental trading knowledge', 0, 'core-knowledge', '📚', '#4A90E2', 100),
('Market Analysis', 'market-analysis', 'Market data and analysis', 0, 'market-analysis', '📊', '#7ED321', 90),
('Trading Strategies', 'trading-strategies', 'Trading strategies and methods', 0, 'trading-strategies', '🎯', '#F5A623', 80),
('Risk Management', 'risk-management', 'Risk assessment and management', 0, 'risk-management', '🛡️', '#D0021B', 95),
('User Learning', 'user-learning', 'User-specific knowledge', 0, 'user-learning', '👤', '#9013FE', 70),
('Discoveries', 'discoveries', 'AI-discovered patterns', 0, 'discoveries', '🔍', '#50E3C2', 60),

-- Level 1 - Indicators (under Core Knowledge)
('Technical Indicators', 'technical-indicators', 'All technical indicators', 1, 'core-knowledge/technical-indicators', '📈', '#4A90E2', 100),
('Chart Patterns', 'chart-patterns', 'Chart pattern recognition', 1, 'core-knowledge/chart-patterns', '📉', '#4A90E2', 90),
('Market Concepts', 'market-concepts', 'Basic market concepts', 1, 'core-knowledge/market-concepts', '💡', '#4A90E2', 80),

-- Level 2 - Indicator Types (under Technical Indicators)
('Momentum Indicators', 'momentum-indicators', 'RSI, MACD, Stochastic', 2, 'core-knowledge/technical-indicators/momentum', '⚡', '#4A90E2', 100),
('Trend Indicators', 'trend-indicators', 'MA, EMA, Ichimoku', 2, 'core-knowledge/technical-indicators/trend', '📊', '#4A90E2', 90),
('Volatility Indicators', 'volatility-indicators', 'Bollinger, ATR, Keltner', 2, 'core-knowledge/technical-indicators/volatility', '🌊', '#4A90E2', 80),
('Volume Indicators', 'volume-indicators', 'OBV, Volume Profile, VWAP', 2, 'core-knowledge/technical-indicators/volume', '📊', '#4A90E2', 70)
ON CONFLICT (slug) DO NOTHING;

-- ==========================================
-- ROW LEVEL SECURITY
-- ==========================================

-- Enable RLS on sensitive tables
ALTER TABLE brain_user_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE brain_user_interactions ENABLE ROW LEVEL SECURITY;

-- Create policies for user data
CREATE POLICY "Users can view own memory" ON brain_user_memory
    FOR SELECT USING (auth.uid()::uuid = user_id);

CREATE POLICY "Users can update own memory" ON brain_user_memory
    FOR UPDATE USING (auth.uid()::uuid = user_id);

CREATE POLICY "Users can view own interactions" ON brain_user_interactions
    FOR SELECT USING (auth.uid()::uuid = user_id);

-- Public read access for knowledge (controlled by is_active)
CREATE POLICY "Public can view active knowledge" ON brain_knowledge
    FOR SELECT USING (is_active = true);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Composite indexes for common queries
CREATE INDEX idx_knowledge_category_type ON brain_knowledge(category_id, knowledge_type);
CREATE INDEX idx_knowledge_search_composite ON brain_knowledge(is_active, validation_status, confidence_score DESC);
CREATE INDEX idx_patterns_active_confidence ON brain_patterns(status, confidence_level DESC) WHERE status = 'active';
CREATE INDEX idx_cache_active_expires ON brain_api_cache(is_active, expires_at) WHERE is_active = true;

-- Partial indexes for filtering
CREATE INDEX idx_knowledge_validated ON brain_knowledge(category_id, usage_count DESC)
    WHERE validation_status = 'validated' AND is_active = true;
CREATE INDEX idx_patterns_validated ON brain_patterns(pattern_type, success_rate DESC)
    WHERE is_validated = true AND status = 'active';

-- ==========================================
-- MAINTENANCE FUNCTIONS
-- ==========================================

-- Function to clean expired cache
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM brain_api_cache
    WHERE expires_at < NOW()
        OR (ttl_seconds IS NOT NULL AND created_at + (ttl_seconds || ' seconds')::INTERVAL < NOW());

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old knowledge
CREATE OR REPLACE FUNCTION archive_old_knowledge()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE brain_knowledge
    SET validation_status = 'archived',
        is_active = false
    WHERE last_accessed < NOW() - INTERVAL '90 days'
        AND usage_count < 5
        AND validation_status != 'archived';

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;