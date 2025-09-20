-- STEP 1: CREATE ALL ZMARTYCHAT TABLES IN ZMARTYBRAIN PROJECT
-- Run this in ZmartyBrain SQL Editor: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql

-- 1. Users table
CREATE TABLE IF NOT EXISTS zmartychat_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    country TEXT,
    selected_tier TEXT DEFAULT 'free',
    onboarding_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Subscription plans
CREATE TABLE IF NOT EXISTS zmartychat_subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    monthly_credits INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    features JSONB DEFAULT '[]',
    stripe_price_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default plans
INSERT INTO zmartychat_subscription_plans (name, display_name, monthly_credits, price, features) VALUES
('free', 'Free Plan', 100, 0, '["Basic chat access", "100 monthly credits", "Community support"]'),
('pro', 'Pro Plan', 1000, 29.99, '["Advanced features", "1,000 monthly credits", "Priority support", "API access"]'),
('premium', 'Premium Plan', 10000, 99.99, '["All features", "10,000 monthly credits", "24/7 support", "Custom integrations", "White label options"]');

-- 3. User subscriptions
CREATE TABLE IF NOT EXISTS zmartychat_user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES zmartychat_subscription_plans(id),
    status TEXT DEFAULT 'active',
    current_period_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    current_period_end TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days',
    credits_remaining INTEGER DEFAULT 100,
    stripe_subscription_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Credit transactions
CREATE TABLE IF NOT EXISTS zmartychat_credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'purchase', 'usage', 'bonus', 'refund', 'subscription'
    description TEXT,
    balance_after INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Conversation messages
CREATE TABLE IF NOT EXISTS zmartychat_conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL,
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    model TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. User insights
CREATE TABLE IF NOT EXISTS zmartychat_user_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE UNIQUE,
    total_messages_sent INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    favorite_topics JSONB DEFAULT '[]',
    usage_patterns JSONB DEFAULT '{}',
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. User streaks
CREATE TABLE IF NOT EXISTS zmartychat_user_streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_check_in DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Achievements
CREATE TABLE IF NOT EXISTS zmartychat_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    points INTEGER DEFAULT 0,
    category TEXT,
    requirements JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. User achievements
CREATE TABLE IF NOT EXISTS zmartychat_user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES zmartychat_achievements(id),
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- 10. Referrals
CREATE TABLE IF NOT EXISTS zmartychat_referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    referred_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    referral_code TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'expired'
    credits_awarded INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. Addiction metrics (gamification)
CREATE TABLE IF NOT EXISTS zmartychat_addiction_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    daily_usage_minutes INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    engagement_score DECIMAL(5,2) DEFAULT 0,
    addiction_level TEXT DEFAULT 'casual', -- 'casual', 'regular', 'power', 'addicted'
    recorded_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, recorded_date)
);

-- 12. User transcripts
CREATE TABLE IF NOT EXISTS zmartychat_user_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    conversation_id UUID,
    transcript_url TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 13. User engagement overview
CREATE TABLE IF NOT EXISTS zmartychat_user_engagement_overview (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE UNIQUE,
    total_sessions INTEGER DEFAULT 0,
    avg_session_duration INTEGER DEFAULT 0,
    last_7_days_activity JSONB DEFAULT '{}',
    last_30_days_activity JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 14. User categories
CREATE TABLE IF NOT EXISTS zmartychat_user_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    interest_score DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, category)
);

-- 15. Top user interests
CREATE TABLE IF NOT EXISTS zmartychat_top_user_interests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    interest TEXT NOT NULL,
    mention_count INTEGER DEFAULT 0,
    last_mentioned TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, interest)
);

-- 16. User API keys
CREATE TABLE IF NOT EXISTS user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    key_name TEXT NOT NULL,
    api_key_hash TEXT NOT NULL,
    last_used TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 17. User trading profiles
CREATE TABLE IF NOT EXISTS user_trading_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE UNIQUE,
    risk_tolerance TEXT DEFAULT 'medium', -- 'low', 'medium', 'high'
    preferred_exchanges JSONB DEFAULT '[]',
    trading_experience TEXT,
    investment_goals JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 18. User portfolios
CREATE TABLE IF NOT EXISTS user_portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    portfolio_name TEXT NOT NULL,
    holdings JSONB DEFAULT '{}',
    total_value DECIMAL(20,2) DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 19. User strategies
CREATE TABLE IF NOT EXISTS user_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES zmartychat_users(id) ON DELETE CASCADE,
    strategy_name TEXT NOT NULL,
    strategy_type TEXT,
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_zmartychat_users_email ON zmartychat_users(email);
CREATE INDEX idx_zmartychat_users_auth_id ON zmartychat_users(auth_id);
CREATE INDEX idx_credit_transactions_user_id ON zmartychat_credit_transactions(user_id);
CREATE INDEX idx_conversation_messages_user_id ON zmartychat_conversation_messages(user_id);
CREATE INDEX idx_user_subscriptions_user_id ON zmartychat_user_subscriptions(user_id);

-- Enable Row Level Security
ALTER TABLE zmartychat_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_subscriptions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only see their own data)
CREATE POLICY "Users can view own profile" ON zmartychat_users
    FOR ALL USING (auth.uid() = auth_id);

CREATE POLICY "Users can view own credits" ON zmartychat_credit_transactions
    FOR SELECT USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can view own messages" ON zmartychat_conversation_messages
    FOR ALL USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can view own subscription" ON zmartychat_user_subscriptions
    FOR SELECT USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

GRANT USAGE ON SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;

-- Success message
SELECT 'All ZmartyChat tables created successfully in ZmartyBrain!' as status;