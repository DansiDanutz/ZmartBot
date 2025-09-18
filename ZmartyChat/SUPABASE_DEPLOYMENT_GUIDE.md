# 🚀 SUPABASE DEPLOYMENT GUIDE - ZMARTY TRADING AI

## 📊 **STEP 1: ACCESS YOUR SUPABASE DASHBOARD**

1. **Go to**: https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy
2. **Navigate to**: SQL Editor (in the left sidebar)
3. **Execute each script below in order**

---

## 🗄️ **STEP 2: DEPLOY DATABASE SCHEMA**

### **Script 1: Core Extensions and Users Table**

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table with complete profile system
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,

    -- Subscription and credits
    subscription_tier VARCHAR(50) DEFAULT 'bronze' CHECK (subscription_tier IN ('bronze', 'silver', 'gold', 'platinum', 'diamond')),
    credits_balance INTEGER DEFAULT 100 CHECK (credits_balance >= 0),
    free_slots INTEGER DEFAULT 1 CHECK (free_slots >= 0),
    paid_slots INTEGER DEFAULT 0 CHECK (paid_slots >= 0),

    -- Commission system
    commission_rate DECIMAL(4,3) DEFAULT 0.05 CHECK (commission_rate >= 0 AND commission_rate <= 1),
    total_invites INTEGER DEFAULT 0 CHECK (total_invites >= 0),
    successful_invites INTEGER DEFAULT 0 CHECK (successful_invites >= 0),
    commission_tier VARCHAR(20) DEFAULT 'starter' CHECK (commission_tier IN ('starter', 'power', 'influencer', 'mega')),
    total_earned DECIMAL(12,2) DEFAULT 0.00 CHECK (total_earned >= 0),

    -- Engagement tracking
    addiction_level INTEGER DEFAULT 1 CHECK (addiction_level >= 1 AND addiction_level <= 10),
    engagement_score DECIMAL(3,2) DEFAULT 0.50 CHECK (engagement_score >= 0 AND engagement_score <= 1),
    last_active TIMESTAMPTZ DEFAULT NOW(),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_commission_tier ON public.users(commission_tier);
CREATE INDEX IF NOT EXISTS idx_users_total_invites ON public.users(total_invites);
```

### **Script 2: Brain Knowledge System**

```sql
-- Brain categories for organizing knowledge
CREATE TABLE IF NOT EXISTS public.brain_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES public.brain_categories(id),
    level INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    path TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Core brain knowledge storage
CREATE TABLE IF NOT EXISTS public.brain_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES public.brain_categories(id),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    content_md TEXT,
    content_html TEXT,
    summary TEXT,

    -- Knowledge metadata
    knowledge_type VARCHAR(50) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_reference TEXT,
    source_timestamp TIMESTAMPTZ,

    -- Search and classification
    keywords TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    embedding vector(1536),

    -- Quality metrics
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_response_time INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,

    -- Relationships
    related_knowledge_ids UUID[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brain patterns discovery
CREATE TABLE IF NOT EXISTS public.brain_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_name VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL,
    expected_outcome JSONB,
    confidence_level DECIMAL(3,2) DEFAULT 0.50,
    discovered_by VARCHAR(100),
    validation_count INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'testing', 'retired')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User interaction tracking for learning
CREATE TABLE IF NOT EXISTS public.brain_user_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    answer_source VARCHAR(100),
    was_helpful BOOLEAN,
    context JSONB DEFAULT '{}',
    response_time INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Script 3: Trading Pattern Analysis System**

```sql
-- Historical patterns discovered from 4-year analysis
CREATE TABLE IF NOT EXISTS public.historical_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,

    -- Pattern data
    entry_conditions JSONB NOT NULL,
    exit_conditions JSONB,
    indicator_values JSONB NOT NULL,

    -- Historical performance
    total_occurrences INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    failed_trades INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0.0000,
    average_profit DECIMAL(8,4) DEFAULT 0.0000,
    maximum_profit DECIMAL(8,4) DEFAULT 0.0000,
    maximum_loss DECIMAL(8,4) DEFAULT 0.0000,

    -- Discovery metadata
    discovered_date TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    confidence_score DECIMAL(3,2) DEFAULT 0.50,

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_trigger_enabled BOOLEAN DEFAULT false
);

-- Real-time trigger tracking
CREATE TABLE IF NOT EXISTS public.trigger_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    pattern_id UUID REFERENCES public.historical_patterns(id),
    trigger_type VARCHAR(50) NOT NULL,

    -- Market data at trigger
    price_at_trigger DECIMAL(20,8),
    market_data JSONB,
    indicator_snapshot JSONB,

    -- Prediction
    predicted_outcome VARCHAR(20),
    confidence_level DECIMAL(3,2),
    expected_profit DECIMAL(8,4),
    risk_level VARCHAR(20),

    -- Tracking
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger subscriptions for users
CREATE TABLE IF NOT EXISTS public.trigger_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    subscription_type VARCHAR(50) DEFAULT 'basic',

    -- Preferences
    min_success_rate DECIMAL(3,2) DEFAULT 0.70,
    max_risk_level VARCHAR(20) DEFAULT 'medium',
    preferred_timeframes TEXT[] DEFAULT '{"1d"}',
    notification_enabled BOOLEAN DEFAULT true,

    -- Status
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Script 4: Commission and Invitation System**

```sql
-- Invitation system for viral growth
CREATE TABLE IF NOT EXISTS public.invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inviter_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    invitee_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Invitation details
    invitation_code VARCHAR(50) UNIQUE NOT NULL,
    invitation_link TEXT,
    message TEXT,

    -- Tracking
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired', 'cancelled')),

    -- Commission tracking
    commission_rate DECIMAL(4,3),
    commission_earned DECIMAL(12,2) DEFAULT 0.00,
    total_invitee_spending DECIMAL(12,2) DEFAULT 0.00,

    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days')
);

-- Commission transactions
CREATE TABLE IF NOT EXISTS public.commission_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inviter_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    invitee_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    invitation_id UUID REFERENCES public.invitations(id),

    -- Transaction details
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    commission_amount DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(4,3) NOT NULL,

    -- References
    credit_purchase_id UUID,
    slot_subscription_id UUID,

    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'failed', 'refunded')),
    processed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Milestone achievements
CREATE TABLE IF NOT EXISTS public.milestone_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,
    milestone_level INTEGER NOT NULL,

    -- Achievement details
    invites_required INTEGER,
    invites_achieved INTEGER,

    -- Rewards
    credits_awarded INTEGER DEFAULT 0,
    commission_rate_boost DECIMAL(4,3) DEFAULT 0.000,
    free_slots_awarded INTEGER DEFAULT 0,
    special_features TEXT[] DEFAULT '{}',

    -- Status
    achieved_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

### **Script 5: Credit and Payment System**

```sql
-- Credit purchases
CREATE TABLE IF NOT EXISTS public.credit_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Purchase details
    credits_amount INTEGER NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),

    -- Payment tracking
    stripe_payment_intent_id VARCHAR(255),
    stripe_charge_id VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'pending',

    -- Commission
    referrer_id UUID REFERENCES public.users(id),
    commission_paid DECIMAL(12,2) DEFAULT 0.00,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Withdrawal requests
CREATE TABLE IF NOT EXISTS public.withdrawal_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Withdrawal details
    amount_credits INTEGER NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    withdrawal_method VARCHAR(50) NOT NULL,

    -- Destination
    bank_account_id VARCHAR(255),
    crypto_address TEXT,
    paypal_email VARCHAR(255),

    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    processed_at TIMESTAMPTZ,
    transaction_id VARCHAR(255),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Slot subscriptions
CREATE TABLE IF NOT EXISTS public.slot_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Subscription details
    slot_type VARCHAR(50) DEFAULT 'premium',
    slots_count INTEGER DEFAULT 1,
    monthly_price_credits INTEGER NOT NULL,

    -- Subscription period
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT true,

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'suspended')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Script 6: Trigger Alert System**

```sql
-- Trigger alerts sent to users
CREATE TABLE IF NOT EXISTS public.trigger_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    trigger_event_id UUID REFERENCES public.trigger_events(id),

    -- Alert content
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    -- Trigger details
    success_rate DECIMAL(5,4),
    expected_profit DECIMAL(8,4),
    risk_level VARCHAR(20),
    timeframe VARCHAR(10),

    -- Delivery
    delivery_method VARCHAR(50) DEFAULT 'app',
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,

    -- Credits
    credits_charged INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles for personalization
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Trading preferences
    trading_style VARCHAR(50) DEFAULT 'beginner',
    risk_level VARCHAR(50) DEFAULT 'moderate',
    preferred_timeframes TEXT[] DEFAULT '{"1d"}',

    -- Tracking
    tracked_symbols TEXT[] DEFAULT '{}',
    alert_preferences JSONB DEFAULT '{"price_alerts": true, "pattern_alerts": true, "whale_alerts": false, "frequency": "important_only"}',

    -- Learning data
    questions_asked JSONB[] DEFAULT '{}',
    favorite_patterns TEXT[] DEFAULT '{}',
    successful_triggers TEXT[] DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔐 **STEP 3: ENABLE ROW LEVEL SECURITY**

```sql
-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brain_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brain_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brain_user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historical_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.commission_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.milestone_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.withdrawal_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.slot_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies
CREATE POLICY "Users can view own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own profile data" ON public.user_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own subscriptions" ON public.trigger_subscriptions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own invitations" ON public.invitations
    FOR ALL USING (auth.uid() = inviter_id OR auth.uid() = invitee_id);

CREATE POLICY "Users can view own alerts" ON public.trigger_alerts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view public patterns" ON public.historical_patterns
    FOR SELECT USING (is_active = true);

CREATE POLICY "Anyone can view active triggers" ON public.trigger_events
    FOR SELECT USING (is_active = true);
```

---

## 🔧 **STEP 4: CREATE HELPER FUNCTIONS**

```sql
-- Function to deduct credits from user
CREATE OR REPLACE FUNCTION deduct_credits(p_user_id UUID, p_amount INTEGER)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.users
    SET credits_balance = credits_balance - p_amount,
        updated_at = NOW()
    WHERE id = p_user_id AND credits_balance >= p_amount;

    RETURN FOUND;
END;
$$;

-- Function to find similar knowledge using embeddings
CREATE OR REPLACE FUNCTION find_similar_knowledge(
    search_embedding vector(1536),
    limit_count INTEGER DEFAULT 5
)
RETURNS TABLE(
    id UUID,
    title VARCHAR(255),
    content TEXT,
    similarity FLOAT
)
LANGUAGE sql
AS $$
    SELECT
        bk.id,
        bk.title,
        bk.content,
        1 - (bk.embedding <=> search_embedding) AS similarity
    FROM public.brain_knowledge bk
    WHERE bk.is_active = true AND bk.embedding IS NOT NULL
    ORDER BY bk.embedding <=> search_embedding
    LIMIT limit_count;
$$;

-- Function to calculate knowledge confidence
CREATE OR REPLACE FUNCTION calculate_knowledge_confidence(
    p_usage_count INTEGER,
    p_success_count INTEGER,
    p_failure_count INTEGER,
    p_days_old INTEGER
)
RETURNS DECIMAL(3,2)
LANGUAGE plpgsql
AS $$
DECLARE
    confidence DECIMAL(3,2);
    success_rate DECIMAL(3,2);
    age_factor DECIMAL(3,2);
    usage_factor DECIMAL(3,2);
BEGIN
    -- Calculate success rate
    IF (p_success_count + p_failure_count) > 0 THEN
        success_rate := p_success_count::DECIMAL / (p_success_count + p_failure_count);
    ELSE
        success_rate := 0.5;
    END IF;

    -- Age factor (newer is better, but not too much penalty for old)
    age_factor := GREATEST(0.7, 1.0 - (p_days_old * 0.001));

    -- Usage factor (more usage = higher confidence)
    usage_factor := LEAST(1.0, 0.5 + (p_usage_count * 0.01));

    -- Combined confidence
    confidence := success_rate * age_factor * usage_factor;

    RETURN LEAST(1.0, GREATEST(0.0, confidence));
END;
$$;

-- Function to increment knowledge usage
CREATE OR REPLACE FUNCTION increment_knowledge_usage(knowledge_uuid UUID)
RETURNS VOID
LANGUAGE sql
AS $$
    UPDATE public.brain_knowledge
    SET usage_count = usage_count + 1,
        last_accessed = NOW()
    WHERE id = knowledge_uuid;
$$;
```

---

## ✅ **VERIFICATION STEPS**

After running all scripts:

1. **Check Tables Created**:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

2. **Verify RLS is Enabled**:
```sql
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

3. **Test Functions**:
```sql
SELECT deduct_credits('00000000-0000-0000-0000-000000000000'::UUID, 10);
```

---

## 🎯 **NEXT STEPS AFTER DEPLOYMENT**

1. ✅ Database schema deployed
2. 🔄 Update environment variables
3. 🧪 Test system integration
4. 🚀 Launch founder program

**Once you complete these SQL scripts, let me know and I'll help with the environment configuration and testing!**