-- ================================================================
-- ZMARTYCHAT COMPLETE DATABASE SCHEMA
-- Credit-based AI Trading Companion
-- ================================================================
-- Run this entire script in Supabase SQL Editor
-- ================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============= USERS TABLE =============
CREATE TABLE IF NOT EXISTS zmartychat_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE,
    contact_type VARCHAR(50) CHECK (contact_type IN ('email', 'phone', 'both')),
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro', 'premium', 'enterprise')),
    credits_balance INTEGER DEFAULT 100 CHECK (credits_balance >= 0),
    credits_used_total INTEGER DEFAULT 0,
    monthly_credit_limit INTEGER DEFAULT NULL,
    preferences JSONB DEFAULT '{}',
    stripe_customer_id VARCHAR(255),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= CREDIT TRANSACTIONS =============
CREATE TABLE IF NOT EXISTS zmartychat_credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) CHECK (transaction_type IN ('usage', 'purchase', 'bonus', 'referral', 'milestone', 'subscription')),
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    service VARCHAR(100),
    description TEXT,
    payment_method VARCHAR(50),
    payment_id VARCHAR(255),
    currency VARCHAR(10) DEFAULT 'USD',
    amount_paid DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= USER CATEGORIES =============
CREATE TABLE IF NOT EXISTS zmartychat_user_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    category_name VARCHAR(100) NOT NULL,
    category_type VARCHAR(50) CHECK (category_type IN ('trading_style', 'risk_profile', 'knowledge_level', 'interest', 'behavior')),
    weight DECIMAL(3,2) DEFAULT 1.0 CHECK (weight >= 0 AND weight <= 10),
    confidence_score DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    evidence_count INTEGER DEFAULT 1,
    last_mentioned TIMESTAMPTZ DEFAULT NOW(),
    example_messages TEXT[],
    extracted_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category_name, category_type)
);

-- ============= USER TRANSCRIPTS =============
CREATE TABLE IF NOT EXISTS zmartychat_user_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    transcript_date DATE NOT NULL,
    transcript_md TEXT NOT NULL,
    message_count INTEGER DEFAULT 0,
    session_duration INTEGER DEFAULT 0,
    topics_discussed TEXT[],
    symbols_mentioned TEXT[],
    actions_taken TEXT[],
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    engagement_score INTEGER DEFAULT 0 CHECK (engagement_score >= 0 AND engagement_score <= 100),
    credits_consumed INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, transcript_date)
);

-- ============= CONVERSATION MESSAGES =============
CREATE TABLE IF NOT EXISTS zmartychat_conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    transcript_id UUID REFERENCES zmartychat_user_transcripts(id) ON DELETE CASCADE,
    sender VARCHAR(50) CHECK (sender IN ('user', 'assistant', 'system')),
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text' CHECK (message_type IN ('text', 'voice', 'image', 'command')),
    intent VARCHAR(100),
    entities JSONB,
    sentiment DECIMAL(3,2),
    importance_score DECIMAL(3,2) DEFAULT 0.5,
    credits_used INTEGER DEFAULT 0,
    api_endpoints_called TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= USER INSIGHTS =============
CREATE TABLE IF NOT EXISTS zmartychat_user_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    insight_type VARCHAR(100) CHECK (insight_type IN ('trading_pattern', 'engagement_spike', 'learning_opportunity', 'market_opportunity', 'risk_alert', 'achievement')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    recommendations TEXT[],
    action_items JSONB,
    confidence_score DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    relevance_score DECIMAL(3,2) DEFAULT 0.5 CHECK (relevance_score >= 0 AND relevance_score <= 1),
    shown_to_user BOOLEAN DEFAULT FALSE,
    user_feedback VARCHAR(50),
    valid_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= ADDICTION METRICS =============
CREATE TABLE IF NOT EXISTS zmartychat_addiction_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sessions_count INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_received INTEGER DEFAULT 0,
    peak_activity_hour INTEGER CHECK (peak_activity_hour >= 0 AND peak_activity_hour <= 23),
    features_used TEXT[],
    credits_consumed INTEGER DEFAULT 0,
    curiosity_score INTEGER DEFAULT 0 CHECK (curiosity_score >= 0 AND curiosity_score <= 100),
    consistency_score INTEGER DEFAULT 0 CHECK (consistency_score >= 0 AND consistency_score <= 100),
    depth_score INTEGER DEFAULT 0 CHECK (depth_score >= 0 AND depth_score <= 100),
    dependency_score INTEGER DEFAULT 0 CHECK (dependency_score >= 0 AND dependency_score <= 100),
    streak_days INTEGER DEFAULT 0,
    return_probability DECIMAL(3,2) CHECK (return_probability >= 0 AND return_probability <= 100),
    churn_risk INTEGER DEFAULT 0 CHECK (churn_risk >= 0 AND churn_risk <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- ============= SUBSCRIPTION PLANS =============
CREATE TABLE IF NOT EXISTS zmartychat_subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_name VARCHAR(100) UNIQUE NOT NULL,
    tier VARCHAR(50) NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2),
    monthly_credits INTEGER NOT NULL,
    daily_credit_limit INTEGER,
    features TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= USER SUBSCRIPTIONS =============
CREATE TABLE IF NOT EXISTS zmartychat_user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES zmartychat_subscription_plans(id),
    status VARCHAR(50) CHECK (status IN ('active', 'cancelled', 'expired', 'paused')),
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly')),
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(50),
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= ACHIEVEMENT DEFINITIONS =============
CREATE TABLE IF NOT EXISTS zmartychat_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    achievement_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    reward_credits INTEGER DEFAULT 0,
    requirement_type VARCHAR(50),
    requirement_value INTEGER,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= USER ACHIEVEMENTS =============
CREATE TABLE IF NOT EXISTS zmartychat_user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES zmartychat_achievements(id),
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),
    credits_awarded INTEGER DEFAULT 0,
    UNIQUE(user_id, achievement_id)
);

-- ============= STREAK RECORDS =============
CREATE TABLE IF NOT EXISTS zmartychat_user_streaks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_checkin DATE,
    streak_bonus_claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ============= REFERRAL SYSTEM =============
CREATE TABLE IF NOT EXISTS zmartychat_referrals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    referrer_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    referred_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    referral_code VARCHAR(50) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'expired')),
    referrer_credits_awarded INTEGER DEFAULT 0,
    referred_credits_awarded INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    UNIQUE(referrer_id, referred_id)
);

-- ============= INDEXES FOR PERFORMANCE =============
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON zmartychat_credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON zmartychat_credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_categories_user_id ON zmartychat_user_categories(user_id);
CREATE INDEX IF NOT EXISTS idx_user_transcripts_user_id ON zmartychat_user_transcripts(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_user_id ON zmartychat_conversation_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_user_insights_user_id ON zmartychat_user_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_addiction_metrics_user_id ON zmartychat_addiction_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON zmartychat_user_subscriptions(user_id);

-- ============= VIEWS FOR ANALYTICS =============

-- User engagement overview
CREATE OR REPLACE VIEW zmartychat_user_engagement_overview AS
SELECT
    u.id,
    u.name,
    u.subscription_tier,
    u.credits_balance,
    u.credits_used_total,
    COUNT(DISTINCT ut.id) as total_sessions,
    COUNT(DISTINCT cm.id) as total_messages,
    AVG(am.dependency_score) as avg_dependency_score,
    MAX(us.current_streak) as current_streak
FROM zmartychat_users u
LEFT JOIN zmartychat_user_transcripts ut ON u.id = ut.user_id
LEFT JOIN zmartychat_conversation_messages cm ON u.id = cm.user_id
LEFT JOIN zmartychat_addiction_metrics am ON u.id = am.user_id
LEFT JOIN zmartychat_user_streaks us ON u.id = us.user_id
GROUP BY u.id;

-- Top user interests
CREATE OR REPLACE VIEW zmartychat_top_user_interests AS
SELECT
    user_id,
    category_name,
    weight,
    confidence_score
FROM zmartychat_user_categories
WHERE category_type = 'interest'
ORDER BY weight DESC, confidence_score DESC;

-- ============= STORED FUNCTIONS =============

-- Credit deduction function
CREATE OR REPLACE FUNCTION deduct_credits(
    p_user_id UUID,
    p_amount INTEGER,
    p_service TEXT,
    p_description TEXT
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_balance INTEGER;
    v_new_balance INTEGER;
BEGIN
    -- Get current balance with lock
    SELECT credits_balance INTO v_current_balance
    FROM zmartychat_users
    WHERE id = p_user_id
    FOR UPDATE;

    -- Check sufficient balance
    IF v_current_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient credits';
    END IF;

    -- Calculate new balance
    v_new_balance := v_current_balance - p_amount;

    -- Update user balance
    UPDATE zmartychat_users
    SET credits_balance = v_new_balance,
        credits_used_total = credits_used_total + p_amount,
        updated_at = NOW()
    WHERE id = p_user_id;

    -- Record transaction
    INSERT INTO zmartychat_credit_transactions (
        user_id,
        transaction_type,
        amount,
        balance_after,
        service,
        description
    ) VALUES (
        p_user_id,
        'usage',
        -p_amount,
        v_new_balance,
        p_service,
        p_description
    );

    RETURN v_new_balance;
END;
$$;

-- Calculate addiction score
CREATE OR REPLACE FUNCTION calculate_addiction_score(user_id UUID)
RETURNS TABLE(
    dependency_score INTEGER,
    curiosity_score INTEGER,
    consistency_score INTEGER,
    depth_score INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.dependency_score,
        am.curiosity_score,
        am.consistency_score,
        am.depth_score
    FROM zmartychat_addiction_metrics am
    WHERE am.user_id = $1
    ORDER BY am.date DESC
    LIMIT 1;
END;
$$;

-- Get dashboard statistics
CREATE OR REPLACE FUNCTION get_dashboard_stats()
RETURNS TABLE(
    total_users BIGINT,
    active_users_today BIGINT,
    total_revenue NUMERIC,
    credits_consumed_today BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT CASE WHEN u.last_active::date = CURRENT_DATE THEN u.id END) as active_users_today,
        COALESCE(SUM(ct.amount_paid), 0) as total_revenue,
        COALESCE(SUM(CASE WHEN ct.created_at::date = CURRENT_DATE AND ct.transaction_type = 'usage' THEN ABS(ct.amount) ELSE 0 END), 0) as credits_consumed_today
    FROM zmartychat_users u
    LEFT JOIN zmartychat_credit_transactions ct ON u.id = ct.user_id;
END;
$$;

-- ============= INITIAL DATA =============

-- Insert subscription plans
INSERT INTO zmartychat_subscription_plans (plan_name, tier, price_monthly, price_yearly, monthly_credits, features) VALUES
('Free', 'free', 0, 0, 100, ARRAY['Basic chat', 'Market data (limited)', 'Daily credit limit: 10', '20 messages per day']),
('Basic', 'basic', 9.99, 99.99, 1000, ARRAY['Everything in Free', 'Technical analysis', 'Basic AI predictions', 'Email support', '100 messages per day']),
('Pro', 'pro', 29.99, 299.99, 5000, ARRAY['Everything in Basic', 'Advanced AI features', 'Priority data access', 'Custom alerts', 'API access', 'Unlimited messages']),
('Premium', 'premium', 99.99, 999.99, 20000, ARRAY['Everything in Pro', 'Unlimited AI queries', 'All agent consensus', 'White-glove support', 'Custom models', 'Dedicated account manager'])
ON CONFLICT (plan_name) DO NOTHING;

-- Insert achievements
INSERT INTO zmartychat_achievements (achievement_key, name, description, icon, reward_credits, requirement_type, requirement_value, category) VALUES
('first_trade', 'First Trade', 'Complete your first trade analysis', '🎯', 50, 'action', 1, 'trading'),
('night_owl', 'Night Owl', 'Trade between midnight and 4 AM', '🦉', 30, 'time', 1, 'activity'),
('early_bird', 'Early Bird', 'Start trading before 6 AM', '🐦', 30, 'time', 1, 'activity'),
('power_user', 'Power User', 'Send 100 messages in one day', '⚡', 100, 'messages', 100, 'engagement'),
('crypto_explorer', 'Crypto Explorer', 'Analyze 10 different cryptocurrencies', '🗺️', 75, 'symbols', 10, 'exploration'),
('profit_master', 'Profit Master', 'Achieve 5 profitable trades in a row', '💰', 200, 'wins', 5, 'performance'),
('knowledge_seeker', 'Knowledge Seeker', 'Ask 50 educational questions', '📚', 60, 'questions', 50, 'learning'),
('social_butterfly', 'Social Butterfly', 'Refer 3 friends', '🦋', 300, 'referrals', 3, 'social'),
('week_warrior', 'Week Warrior', '7 day login streak', '🔥', 70, 'streak', 7, 'consistency'),
('monthly_master', 'Monthly Master', '30 day login streak', '👑', 500, 'streak', 30, 'consistency')
ON CONFLICT (achievement_key) DO NOTHING;

-- ============= ROW LEVEL SECURITY =============

-- Enable RLS on all tables
ALTER TABLE zmartychat_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_addiction_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_referrals ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own data" ON zmartychat_users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON zmartychat_users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own transactions" ON zmartychat_credit_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own categories" ON zmartychat_user_categories
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own transcripts" ON zmartychat_user_transcripts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own messages" ON zmartychat_conversation_messages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own insights" ON zmartychat_user_insights
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own metrics" ON zmartychat_addiction_metrics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view subscription plans" ON zmartychat_subscription_plans
    FOR SELECT USING (true);

CREATE POLICY "Users can view own subscriptions" ON zmartychat_user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view achievements" ON zmartychat_achievements
    FOR SELECT USING (true);

CREATE POLICY "Users can view own achievements" ON zmartychat_user_achievements
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own streaks" ON zmartychat_user_streaks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own referrals" ON zmartychat_referrals
    FOR SELECT USING (auth.uid() = referrer_id OR auth.uid() = referred_id);

-- ============= SUCCESS MESSAGE =============
-- If you see this, your ZmartyChat database is ready!
-- Tables created: 13
-- Views created: 2
-- Functions created: 3
-- Subscription plans added: 4
-- Achievements added: 10
-- ================================================================