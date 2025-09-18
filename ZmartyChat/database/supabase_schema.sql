-- ZmartyChat Supabase Database Schema
-- Complete user management, transcript storage, credit system, and intelligent categorization

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "vector"; -- For AI embeddings

-- =====================================================
-- USERS TABLE - Core user information
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE,
    avatar_url TEXT,
    contact_type VARCHAR(20) CHECK (contact_type IN ('email', 'phone')),

    -- Authentication
    password_hash TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,

    -- Profile
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(2),

    -- Trading Profile
    trading_experience VARCHAR(50) CHECK (trading_experience IN ('beginner', 'intermediate', 'advanced', 'expert')),
    risk_tolerance VARCHAR(20) CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    investment_goals TEXT[],
    preferred_assets TEXT[],

    -- Subscription & Credits
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro', 'premium', 'enterprise')),
    credits_balance INTEGER DEFAULT 100, -- Start with 100 free credits
    credits_used_total INTEGER DEFAULT 0,
    monthly_credit_limit INTEGER DEFAULT 1000,
    credit_reset_date TIMESTAMP,

    -- Engagement Metrics
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages_sent INTEGER DEFAULT 0,
    total_session_time INTEGER DEFAULT 0, -- in seconds
    addiction_score FLOAT DEFAULT 0.0, -- 0-100 engagement score

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- =====================================================
-- USER TRANSCRIPTS - Store all conversations as MD files
-- =====================================================
CREATE TABLE IF NOT EXISTS user_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Transcript Data
    transcript_date DATE NOT NULL DEFAULT CURRENT_DATE,
    transcript_md TEXT NOT NULL, -- Full markdown transcript
    message_count INTEGER DEFAULT 0,
    session_duration INTEGER DEFAULT 0, -- in seconds

    -- Analysis Results
    topics_discussed TEXT[],
    symbols_mentioned TEXT[],
    actions_taken TEXT[],
    sentiment_score FLOAT, -- -1 to 1
    engagement_score FLOAT, -- 0 to 100

    -- Credits Used
    credits_consumed INTEGER DEFAULT 0,
    api_calls_made JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, transcript_date)
);

-- =====================================================
-- USER CATEGORIES - AI-extracted user interests/patterns
-- =====================================================
CREATE TABLE IF NOT EXISTS user_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    category_name VARCHAR(100) NOT NULL,
    category_type VARCHAR(50) CHECK (category_type IN (
        'trading_style', 'favorite_symbols', 'risk_profile',
        'time_preference', 'strategy_type', 'interest_topic',
        'price_range', 'market_sector', 'technical_indicators'
    )),

    -- Weighted importance based on frequency
    weight FLOAT DEFAULT 1.0,
    confidence_score FLOAT DEFAULT 0.5, -- AI confidence in this categorization

    -- Evidence from conversations
    evidence_count INTEGER DEFAULT 1,
    first_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    example_messages TEXT[],

    -- Auto-extracted data
    extracted_data JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, category_name, category_type)
);

-- =====================================================
-- CONVERSATION MESSAGES - Individual messages for analysis
-- =====================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transcript_id UUID REFERENCES user_transcripts(id) ON DELETE CASCADE,

    -- Message Content
    sender VARCHAR(20) CHECK (sender IN ('user', 'zmarty')),
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',

    -- Analysis
    intent VARCHAR(100), -- buy, sell, analyze, learn, etc.
    entities JSONB DEFAULT '{}'::jsonb, -- {symbols: [], amounts: [], prices: []}
    sentiment FLOAT, -- -1 to 1
    importance_score FLOAT DEFAULT 0.5, -- 0 to 1

    -- Credits
    credits_used INTEGER DEFAULT 0,
    api_endpoints_called TEXT[],

    -- Embeddings for semantic search
    embedding vector(1536), -- OpenAI embedding dimension

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexing
    INDEX idx_messages_user_created (user_id, created_at DESC),
    INDEX idx_messages_importance (importance_score DESC)
);

-- =====================================================
-- CREDIT TRANSACTIONS - Track credit usage
-- =====================================================
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    transaction_type VARCHAR(50) CHECK (transaction_type IN (
        'purchase', 'bonus', 'referral', 'usage', 'refund', 'subscription'
    )),
    amount INTEGER NOT NULL, -- Positive for credits added, negative for used
    balance_after INTEGER NOT NULL,

    -- Usage Details
    service_used VARCHAR(100), -- 'chat', 'analysis', 'signals', etc.
    api_calls JSONB DEFAULT '{}'::jsonb,
    data_accessed TEXT[],

    -- Payment Info (if purchase)
    payment_method VARCHAR(50),
    payment_id VARCHAR(255),
    currency VARCHAR(3),
    amount_paid DECIMAL(10, 2),

    -- Metadata
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- USER INSIGHTS - AI-generated insights about users
-- =====================================================
CREATE TABLE IF NOT EXISTS user_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    insight_type VARCHAR(50) CHECK (insight_type IN (
        'trading_pattern', 'behavioral', 'preference',
        'opportunity', 'risk_alert', 'education_need'
    )),

    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Actionable data
    recommendations TEXT[],
    action_items JSONB DEFAULT '[]'::jsonb,

    -- Tracking
    confidence_score FLOAT DEFAULT 0.7,
    relevance_score FLOAT DEFAULT 0.5,
    shown_to_user BOOLEAN DEFAULT FALSE,
    user_feedback VARCHAR(20), -- 'helpful', 'not_helpful', 'ignored'

    -- Validity
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ADDICTION METRICS - Track engagement patterns
-- =====================================================
CREATE TABLE IF NOT EXISTS addiction_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Daily Metrics
    date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Engagement
    sessions_count INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_received INTEGER DEFAULT 0,

    -- Activity Patterns
    peak_activity_hour INTEGER, -- 0-23
    average_session_length INTEGER, -- seconds
    longest_session INTEGER, -- seconds

    -- Feature Usage
    features_used TEXT[],
    api_calls_count INTEGER DEFAULT 0,
    credits_consumed INTEGER DEFAULT 0,

    -- Behavioral Scores
    curiosity_score FLOAT DEFAULT 0, -- How many different topics
    consistency_score FLOAT DEFAULT 0, -- Regular usage pattern
    depth_score FLOAT DEFAULT 0, -- Deep dive into topics
    dependency_score FLOAT DEFAULT 0, -- Overall addiction metric

    -- Retention Indicators
    streak_days INTEGER DEFAULT 0,
    return_probability FLOAT DEFAULT 0.5,
    churn_risk FLOAT DEFAULT 0.0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, date)
);

-- =====================================================
-- PERSONALIZATION VECTORS - For AI matching
-- =====================================================
CREATE TABLE IF NOT EXISTS personalization_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Vector Types
    interest_vector vector(256), -- User interests
    behavior_vector vector(256), -- Usage patterns
    preference_vector vector(256), -- Trading preferences

    -- Computed Similarities
    similar_users UUID[], -- Users with similar patterns
    recommended_topics TEXT[],
    recommended_symbols TEXT[],

    -- Update tracking
    last_computed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT '1.0',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

-- =====================================================
-- CREDIT PACKAGES - Available purchase options
-- =====================================================
CREATE TABLE IF NOT EXISTS credit_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    package_name VARCHAR(100) NOT NULL,
    credits_amount INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Bonuses
    bonus_credits INTEGER DEFAULT 0,
    bonus_percentage FLOAT DEFAULT 0,

    -- Display
    description TEXT,
    popular BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,

    -- Availability
    active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SUBSCRIPTION PLANS
-- =====================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    plan_name VARCHAR(50) UNIQUE NOT NULL,
    tier VARCHAR(20) CHECK (tier IN ('free', 'basic', 'pro', 'premium', 'enterprise')),

    -- Pricing
    monthly_price DECIMAL(10, 2),
    yearly_price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Credits
    monthly_credits INTEGER NOT NULL,
    rollover_enabled BOOLEAN DEFAULT FALSE,

    -- Features
    features JSONB DEFAULT '{}'::jsonb,
    api_rate_limit INTEGER DEFAULT 60, -- requests per minute

    -- Display
    description TEXT,
    highlight_features TEXT[],

    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- USER SUBSCRIPTIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),

    -- Status
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),

    -- Billing
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly')),
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,

    -- Payment
    payment_method VARCHAR(50),
    stripe_subscription_id VARCHAR(255),

    -- Trial
    trial_end TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_credits ON users(credits_balance);
CREATE INDEX idx_users_last_active ON users(last_active DESC);

CREATE INDEX idx_transcripts_user_date ON user_transcripts(user_id, transcript_date DESC);
CREATE INDEX idx_transcripts_credits ON user_transcripts(credits_consumed);

CREATE INDEX idx_categories_user ON user_categories(user_id);
CREATE INDEX idx_categories_weight ON user_categories(weight DESC);

CREATE INDEX idx_insights_user ON user_insights(user_id, created_at DESC);
CREATE INDEX idx_insights_shown ON user_insights(shown_to_user);

CREATE INDEX idx_metrics_user_date ON addiction_metrics(user_id, date DESC);
CREATE INDEX idx_metrics_dependency ON addiction_metrics(dependency_score DESC);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_transcripts_updated_at BEFORE UPDATE ON user_transcripts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON user_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function to calculate addiction score
CREATE OR REPLACE FUNCTION calculate_addiction_score(user_id UUID)
RETURNS FLOAT AS $$
DECLARE
    score FLOAT := 0;
    metrics RECORD;
BEGIN
    SELECT * INTO metrics
    FROM addiction_metrics
    WHERE addiction_metrics.user_id = calculate_addiction_score.user_id
    ORDER BY date DESC
    LIMIT 1;

    IF metrics IS NOT NULL THEN
        score := (
            metrics.consistency_score * 0.3 +
            metrics.curiosity_score * 0.2 +
            metrics.depth_score * 0.2 +
            metrics.dependency_score * 0.3
        );
    END IF;

    RETURN LEAST(100, GREATEST(0, score));
END;
$$ LANGUAGE plpgsql;

-- Function to deduct credits
CREATE OR REPLACE FUNCTION deduct_credits(
    p_user_id UUID,
    p_amount INTEGER,
    p_service VARCHAR(100),
    p_description TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    current_balance INTEGER;
    new_balance INTEGER;
BEGIN
    -- Get current balance with lock
    SELECT credits_balance INTO current_balance
    FROM users
    WHERE id = p_user_id
    FOR UPDATE;

    -- Check if sufficient credits
    IF current_balance < p_amount THEN
        RETURN FALSE;
    END IF;

    -- Deduct credits
    new_balance := current_balance - p_amount;

    UPDATE users
    SET credits_balance = new_balance,
        credits_used_total = credits_used_total + p_amount
    WHERE id = p_user_id;

    -- Record transaction
    INSERT INTO credit_transactions (
        user_id, transaction_type, amount, balance_after,
        service_used, description
    ) VALUES (
        p_user_id, 'usage', -p_amount, new_balance,
        p_service, p_description
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE addiction_metrics ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY users_policy ON users
    FOR ALL USING (auth.uid() = id);

CREATE POLICY transcripts_policy ON user_transcripts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY categories_policy ON user_categories
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY messages_policy ON conversation_messages
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY transactions_policy ON credit_transactions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY insights_policy ON user_insights
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY metrics_policy ON addiction_metrics
    FOR ALL USING (auth.uid() = user_id);

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default credit packages
INSERT INTO credit_packages (package_name, credits_amount, price, bonus_credits, popular, description) VALUES
('Starter Pack', 500, 4.99, 50, FALSE, 'Perfect for trying out Zmarty'),
('Popular Choice', 2000, 14.99, 300, TRUE, 'Most popular - Best value!'),
('Power Trader', 5000, 29.99, 1000, FALSE, 'For serious traders'),
('Whale Package', 10000, 49.99, 2500, FALSE, 'Maximum credits, maximum insights');

-- Insert subscription plans
INSERT INTO subscription_plans (plan_name, tier, monthly_price, yearly_price, monthly_credits, features) VALUES
('Free', 'free', 0, 0, 100, '{"basic_chat": true, "market_data": true, "limits": {"messages_per_day": 20}}'),
('Basic', 'basic', 9.99, 99, 1000, '{"all_free": true, "advanced_analysis": true, "limits": {"messages_per_day": 100}}'),
('Pro', 'pro', 29.99, 299, 5000, '{"all_basic": true, "priority_support": true, "custom_alerts": true, "api_access": true}'),
('Premium', 'premium', 99.99, 999, 20000, '{"all_pro": true, "unlimited_messages": true, "dedicated_support": true, "custom_models": true}');

-- =====================================================
-- VIEWS FOR ANALYTICS
-- =====================================================

-- User engagement overview
CREATE OR REPLACE VIEW user_engagement_overview AS
SELECT
    u.id,
    u.name,
    u.email,
    u.subscription_tier,
    u.credits_balance,
    u.addiction_score,
    COUNT(DISTINCT ut.transcript_date) as days_active,
    SUM(ut.message_count) as total_messages,
    AVG(am.dependency_score) as avg_dependency,
    MAX(am.streak_days) as max_streak
FROM users u
LEFT JOIN user_transcripts ut ON u.id = ut.user_id
LEFT JOIN addiction_metrics am ON u.id = am.user_id
GROUP BY u.id;

-- Top user categories
CREATE OR REPLACE VIEW top_user_interests AS
SELECT
    user_id,
    category_type,
    category_name,
    weight,
    evidence_count
FROM user_categories
ORDER BY weight DESC, evidence_count DESC;

COMMENT ON SCHEMA public IS 'ZmartyChat - AI Trading Assistant with Credit System';