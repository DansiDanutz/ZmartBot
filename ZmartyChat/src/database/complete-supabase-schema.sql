-- ============================================================================
-- COMPLETE SUPABASE SCHEMA FOR ZMARTY AI
-- Includes: Brain System, Triggers, Invitations, Commissions, Milestones
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,

    -- Invitation tracking
    invited_by UUID REFERENCES public.users(id),
    invitation_code VARCHAR(50),
    joined_via VARCHAR(50), -- 'invitation', 'waitlist', 'founder'

    -- Account type
    account_tier VARCHAR(50) DEFAULT 'starter', -- starter, power, influencer, legend
    commission_rate DECIMAL(4,3) DEFAULT 0.05, -- 5% default, up to 25%

    -- Credits & Balance
    credits_balance INTEGER DEFAULT 100,
    credits_spent INTEGER DEFAULT 0,
    cash_balance DECIMAL(10,2) DEFAULT 0.00,

    -- Subscription
    subscription_status VARCHAR(50) DEFAULT 'trial',
    subscription_tier VARCHAR(50) DEFAULT 'bronze',
    subscription_expires TIMESTAMP,

    -- Tracking
    last_active TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User profiles for Brain system
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Trading preferences
    trading_style VARCHAR(50), -- 'day_trading', 'swing', 'position', 'investor'
    risk_level VARCHAR(50), -- 'conservative', 'moderate', 'aggressive'
    preferred_timeframes TEXT[], -- ['1h', '4h', '1d']

    -- Tracking preferences
    tracked_symbols TEXT[],
    alert_preferences JSONB,
    best_alert_times TEXT[], -- ['08:00', '12:00', '18:00']

    -- Engagement metrics
    addiction_level INTEGER DEFAULT 1, -- 1-10 scale
    engagement_score DECIMAL(3,2) DEFAULT 0.5,
    click_rate DECIMAL(3,2),

    -- Slots (free and paid)
    free_slots INTEGER DEFAULT 1,
    paid_slots INTEGER DEFAULT 0,
    total_slots_unlocked INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- BRAIN KNOWLEDGE SYSTEM
-- ============================================================================

-- Knowledge categories
CREATE TABLE IF NOT EXISTS public.brain_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES public.brain_categories(id),
    level INTEGER DEFAULT 0,
    path TEXT,
    description TEXT,
    priority INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Main knowledge storage
CREATE TABLE IF NOT EXISTS public.brain_knowledge (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    category_id UUID REFERENCES public.brain_categories(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,

    -- Knowledge metadata
    knowledge_type VARCHAR(100), -- 'pattern', 'indicator', 'strategy', 'historical'
    source_type VARCHAR(100), -- 'api', 'user', 'analysis', 'external'
    source_url TEXT,

    -- Quality metrics
    confidence_score DECIMAL(3,2) DEFAULT 1.0,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2),

    -- Search optimization
    keywords TEXT[],
    tags TEXT[],
    embedding vector(1536), -- For semantic search

    -- Versioning
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Symbol-specific knowledge
CREATE TABLE IF NOT EXISTS public.symbol_knowledge (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    data JSONB NOT NULL, -- Complete symbol data

    -- Cache management
    last_api_call TIMESTAMP,
    cache_expires TIMESTAMP,
    update_frequency INTERVAL DEFAULT '15 minutes',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(symbol)
);

-- ============================================================================
-- HISTORICAL PATTERNS & TRIGGERS
-- ============================================================================

-- Historical patterns discovered through 4-year analysis
CREATE TABLE IF NOT EXISTS public.historical_patterns (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '1h', '4h', '1d', '1w'

    -- Pattern details
    pattern_type VARCHAR(100),
    pattern_conditions JSONB, -- All indicator values

    -- Performance metrics
    occurrences INTEGER,
    success_rate DECIMAL(3,2),
    average_profit DECIMAL(5,4),
    average_drawdown DECIMAL(5,4),
    average_holding_period INTEGER, -- in hours

    -- Historical examples
    best_entry JSONB,
    recent_triggers JSONB[],

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Active triggers monitoring
CREATE TABLE IF NOT EXISTS public.trigger_monitoring (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    pattern_id UUID REFERENCES public.historical_patterns(id),

    -- Trigger status
    status VARCHAR(50), -- 'watching', 'active', 'triggered', 'expired'
    probability DECIMAL(3,2),

    -- Conditions
    target_conditions JSONB,
    current_conditions JSONB,
    proximity_score DECIMAL(3,2), -- How close to triggering

    -- Timing
    estimated_trigger_time TIMESTAMP,
    last_checked TIMESTAMP DEFAULT NOW(),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User trigger subscriptions (waiting room)
CREATE TABLE IF NOT EXISTS public.trigger_subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,

    -- Subscription preferences
    min_success_rate DECIMAL(3,2) DEFAULT 0.70,
    pattern_types TEXT[],
    timeframes TEXT[],

    -- Status tracking
    status VARCHAR(50) DEFAULT 'waiting', -- 'waiting', 'triggered', 'paused'
    subscription_date TIMESTAMP DEFAULT NOW(),
    last_trigger_date TIMESTAMP,

    -- Metrics
    total_triggers_received INTEGER DEFAULT 0,
    total_credits_spent INTEGER DEFAULT 0,
    waiting_days INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INVITATION SYSTEM
-- ============================================================================

-- Invitations
CREATE TABLE IF NOT EXISTS public.invitations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    inviter_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Invitation details
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'used', 'expired'
    invited_user_id UUID REFERENCES public.users(id),

    -- Metadata
    inviter_level VARCHAR(50),
    inviter_invite_count INTEGER,
    exclusivity_tier VARCHAR(50),

    -- Timing
    created_at TIMESTAMP DEFAULT NOW(),
    used_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '30 days'
);

-- Invitation statistics
CREATE TABLE IF NOT EXISTS public.user_invitation_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,

    -- Invitation metrics
    total_invites_sent INTEGER DEFAULT 0,
    successful_invites INTEGER DEFAULT 0,
    pending_invites INTEGER DEFAULT 0,
    conversion_rate DECIMAL(3,2) DEFAULT 0,

    -- Rewards earned
    total_credits_earned INTEGER DEFAULT 0,
    total_slots_unlocked INTEGER DEFAULT 0,
    total_cash_earned DECIMAL(10,2) DEFAULT 0,

    -- Network metrics
    network_size INTEGER DEFAULT 0,
    active_network_users INTEGER DEFAULT 0,
    network_total_spend DECIMAL(10,2) DEFAULT 0,

    -- Status
    is_verified_influencer BOOLEAN DEFAULT false,
    last_invite_sent TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Waiting list for non-invited users
CREATE TABLE IF NOT EXISTS public.waiting_list (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    data JSONB,
    position INTEGER,
    referral_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- COMMISSION & REVENUE SHARE
-- ============================================================================

-- Credit purchases
CREATE TABLE IF NOT EXISTS public.credit_purchases (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Purchase details
    amount INTEGER NOT NULL, -- Credit amount
    value DECIMAL(10,2) NOT NULL, -- Dollar value
    package_type VARCHAR(50),
    payment_method VARCHAR(50),

    -- Stripe/payment info
    stripe_payment_id TEXT,
    stripe_invoice_id TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Commission transactions
CREATE TABLE IF NOT EXISTS public.commission_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    recipient_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    source_user_id UUID REFERENCES public.users(id),
    purchase_id UUID REFERENCES public.credit_purchases(id),

    -- Commission details
    amount INTEGER NOT NULL, -- Credits earned
    tier INTEGER, -- 1, 2, or 3
    rate DECIMAL(4,3), -- Commission rate used
    multiplier DECIMAL(3,2) DEFAULT 1.0,

    -- Type
    type VARCHAR(50), -- 'direct_commission', 'tier2', 'tier3', 'bonus'
    description TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Cash withdrawals
CREATE TABLE IF NOT EXISTS public.withdrawals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Withdrawal details
    credits INTEGER NOT NULL,
    gross_amount DECIMAL(10,2),
    fee DECIMAL(10,2),
    net_amount DECIMAL(10,2),

    -- Payment method
    method VARCHAR(50), -- 'stripe', 'paypal', 'crypto', 'bank'
    destination TEXT, -- Encrypted payment destination

    -- Status
    status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    transaction_id TEXT,

    -- Timing
    requested_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- ============================================================================
-- MILESTONE SYSTEM
-- ============================================================================

-- User milestones
CREATE TABLE IF NOT EXISTS public.user_milestones (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    milestone_key VARCHAR(50),

    -- Achievement details
    achieved_at TIMESTAMP DEFAULT NOW(),
    invites_at_achievement INTEGER,
    rewards_granted JSONB,

    UNIQUE(user_id, milestone_key)
);

-- User badges
CREATE TABLE IF NOT EXISTS public.user_badges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    badge_key VARCHAR(100),
    badge_name VARCHAR(255),
    badge_emoji VARCHAR(10),
    earned_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, badge_key)
);

-- ============================================================================
-- ALERTS & NOTIFICATIONS
-- ============================================================================

-- Trigger alerts delivered
CREATE TABLE IF NOT EXISTS public.trigger_alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR(20),
    pattern_id UUID REFERENCES public.historical_patterns(id),

    -- Alert details
    trigger_type VARCHAR(100),
    success_rate DECIMAL(3,2),
    message TEXT,

    -- Cost
    credits_charged INTEGER,

    -- Status
    delivered BOOLEAN DEFAULT true,
    clicked BOOLEAN DEFAULT false,
    profitable BOOLEAN,

    created_at TIMESTAMP DEFAULT NOW()
);

-- General notifications
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    type VARCHAR(100),
    title VARCHAR(500),
    message TEXT,
    data JSONB,

    read BOOLEAN DEFAULT false,
    clicked BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- ANALYTICS & METRICS
-- ============================================================================

-- Viral growth metrics
CREATE TABLE IF NOT EXISTS public.viral_metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,

    -- Invitation metrics
    invites_sent INTEGER DEFAULT 0,
    invites_accepted INTEGER DEFAULT 0,
    viral_coefficient DECIMAL(3,2),
    conversion_rate DECIMAL(3,2),

    -- User metrics
    total_users INTEGER,
    active_users INTEGER,
    new_users INTEGER,

    -- Revenue metrics
    total_revenue DECIMAL(10,2),
    commission_paid DECIMAL(10,2),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Report engagement tracking
CREATE TABLE IF NOT EXISTS public.report_engagement (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR(20),

    action VARCHAR(50), -- 'view', 'share', 'click', 'convert'
    engagement_type VARCHAR(50),
    time_spent INTEGER, -- seconds

    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- User indexes
CREATE INDEX idx_users_invited_by ON public.users(invited_by);
CREATE INDEX idx_users_account_tier ON public.users(account_tier);
CREATE INDEX idx_users_subscription_status ON public.users(subscription_status);

-- Knowledge indexes
CREATE INDEX idx_brain_knowledge_category ON public.brain_knowledge(category_id);
CREATE INDEX idx_brain_knowledge_type ON public.brain_knowledge(knowledge_type);
CREATE INDEX idx_brain_knowledge_keywords ON public.brain_knowledge USING GIN(keywords);
CREATE INDEX idx_brain_knowledge_tags ON public.brain_knowledge USING GIN(tags);
CREATE INDEX idx_brain_knowledge_embedding ON public.brain_knowledge USING ivfflat (embedding vector_l2_ops);

-- Pattern indexes
CREATE INDEX idx_historical_patterns_symbol ON public.historical_patterns(symbol);
CREATE INDEX idx_historical_patterns_timeframe ON public.historical_patterns(timeframe);
CREATE INDEX idx_historical_patterns_success_rate ON public.historical_patterns(success_rate DESC);

-- Trigger indexes
CREATE INDEX idx_trigger_monitoring_symbol ON public.trigger_monitoring(symbol);
CREATE INDEX idx_trigger_monitoring_status ON public.trigger_monitoring(status);
CREATE INDEX idx_trigger_subscriptions_user ON public.trigger_subscriptions(user_id);
CREATE INDEX idx_trigger_subscriptions_symbol ON public.trigger_subscriptions(symbol);

-- Invitation indexes
CREATE INDEX idx_invitations_inviter ON public.invitations(inviter_id);
CREATE INDEX idx_invitations_code ON public.invitations(code);
CREATE INDEX idx_invitations_status ON public.invitations(status);

-- Commission indexes
CREATE INDEX idx_commission_transactions_recipient ON public.commission_transactions(recipient_id);
CREATE INDEX idx_commission_transactions_source ON public.commission_transactions(source_user_id);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brain_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.commission_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.withdrawals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY users_read_own ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY users_update_own ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- User profiles
CREATE POLICY profiles_read_own ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY profiles_update_own ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Trigger subscriptions
CREATE POLICY trigger_subs_read_own ON public.trigger_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY trigger_subs_manage_own ON public.trigger_subscriptions
    FOR ALL USING (auth.uid() = user_id);

-- Commissions
CREATE POLICY commissions_read_own ON public.commission_transactions
    FOR SELECT USING (auth.uid() = recipient_id);

-- Withdrawals
CREATE POLICY withdrawals_read_own ON public.withdrawals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY withdrawals_create_own ON public.withdrawals
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Notifications
CREATE POLICY notifications_read_own ON public.notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY notifications_update_own ON public.notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update timestamp to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_brain_knowledge_updated_at BEFORE UPDATE ON public.brain_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function to deduct credits
CREATE OR REPLACE FUNCTION deduct_credits(p_user_id UUID, p_amount INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    v_balance INTEGER;
BEGIN
    SELECT credits_balance INTO v_balance FROM public.users WHERE id = p_user_id;

    IF v_balance >= p_amount THEN
        UPDATE public.users
        SET credits_balance = credits_balance - p_amount,
            credits_spent = credits_spent + p_amount
        WHERE id = p_user_id;
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate viral coefficient
CREATE OR REPLACE FUNCTION calculate_viral_coefficient()
RETURNS DECIMAL AS $$
DECLARE
    v_total_invites INTEGER;
    v_accepted_invites INTEGER;
    v_total_users INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_total_invites FROM public.invitations;
    SELECT COUNT(*) INTO v_accepted_invites FROM public.invitations WHERE status = 'used';
    SELECT COUNT(*) INTO v_total_users FROM public.users;

    IF v_total_users > 0 AND v_total_invites > 0 THEN
        RETURN (v_total_invites::DECIMAL / v_total_users) * (v_accepted_invites::DECIMAL / v_total_invites);
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's network value
CREATE OR REPLACE FUNCTION get_network_value(p_user_id UUID)
RETURNS TABLE (
    network_size INTEGER,
    active_users INTEGER,
    total_spend DECIMAL,
    monthly_revenue DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH network AS (
        SELECT u.id
        FROM public.users u
        WHERE u.invited_by = p_user_id
    ),
    network_purchases AS (
        SELECT
            COUNT(DISTINCT n.id) as network_size,
            COUNT(DISTINCT CASE WHEN cp.created_at > NOW() - INTERVAL '30 days' THEN n.id END) as active_users,
            COALESCE(SUM(cp.value), 0) as total_spend,
            COALESCE(SUM(CASE WHEN cp.created_at > NOW() - INTERVAL '30 days' THEN cp.value END), 0) as monthly_revenue
        FROM network n
        LEFT JOIN public.credit_purchases cp ON cp.user_id = n.id
    )
    SELECT * FROM network_purchases;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SEED DATA FOR MILESTONES
-- ============================================================================

INSERT INTO public.brain_categories (name, level, path, description, priority) VALUES
    ('Symbols', 0, '/symbols', 'Symbol-specific knowledge', 10),
    ('Patterns', 0, '/patterns', 'Trading patterns and setups', 9),
    ('Indicators', 0, '/indicators', 'Technical indicators', 8),
    ('Strategies', 0, '/strategies', 'Trading strategies', 7),
    ('Risk', 0, '/risk', 'Risk management', 9),
    ('Market', 0, '/market', 'Market analysis', 8)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- REALTIME SUBSCRIPTIONS
-- ============================================================================

-- Enable realtime for critical tables
ALTER PUBLICATION supabase_realtime ADD TABLE public.trigger_alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.notifications;
ALTER PUBLICATION supabase_realtime ADD TABLE public.commission_transactions;

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;