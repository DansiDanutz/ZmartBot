# 🔥 DIRECT SQL DEPLOYMENT - COPY AND PASTE

## 🎯 **IMMEDIATE DEPLOYMENT**

**Go to your Supabase SQL Editor**: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql

**Copy and paste each script below, one at a time, then click "Run":**

---

## **Script 1: Extensions and Core Setup**
```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## **Script 2: Users Table**
```sql
-- Users table with complete profile system
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'bronze',
    credits_balance INTEGER DEFAULT 100,
    free_slots INTEGER DEFAULT 1,
    paid_slots INTEGER DEFAULT 0,
    commission_rate DECIMAL(4,3) DEFAULT 0.05,
    total_invites INTEGER DEFAULT 0,
    successful_invites INTEGER DEFAULT 0,
    commission_tier VARCHAR(20) DEFAULT 'starter',
    total_earned DECIMAL(12,2) DEFAULT 0.00,
    addiction_level INTEGER DEFAULT 1,
    engagement_score DECIMAL(3,2) DEFAULT 0.50,
    last_active TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_commission_tier ON public.users(commission_tier);
```

---

## **Script 3: Brain Knowledge System**
```sql
-- Brain categories
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

-- Brain knowledge storage
CREATE TABLE IF NOT EXISTS public.brain_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES public.brain_categories(id),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    content_md TEXT,
    content_html TEXT,
    summary TEXT,
    knowledge_type VARCHAR(50) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_reference TEXT,
    source_timestamp TIMESTAMPTZ,
    keywords TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    embedding vector(1536),
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_response_time INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    related_knowledge_ids UUID[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brain patterns
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
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User interactions
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

---

## **Script 4: Historical Patterns System**
```sql
-- Historical patterns from 4-year analysis
CREATE TABLE IF NOT EXISTS public.historical_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    entry_conditions JSONB NOT NULL,
    exit_conditions JSONB,
    indicator_values JSONB NOT NULL,
    total_occurrences INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    failed_trades INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0.0000,
    average_profit DECIMAL(8,4) DEFAULT 0.0000,
    maximum_profit DECIMAL(8,4) DEFAULT 0.0000,
    maximum_loss DECIMAL(8,4) DEFAULT 0.0000,
    discovered_date TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    is_active BOOLEAN DEFAULT true,
    is_trigger_enabled BOOLEAN DEFAULT false
);

-- Real-time trigger events
CREATE TABLE IF NOT EXISTS public.trigger_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    pattern_id UUID REFERENCES public.historical_patterns(id),
    trigger_type VARCHAR(50) NOT NULL,
    price_at_trigger DECIMAL(20,8),
    market_data JSONB,
    indicator_snapshot JSONB,
    predicted_outcome VARCHAR(20),
    confidence_level DECIMAL(3,2),
    expected_profit DECIMAL(8,4),
    risk_level VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User trigger subscriptions
CREATE TABLE IF NOT EXISTS public.trigger_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    subscription_type VARCHAR(50) DEFAULT 'basic',
    min_success_rate DECIMAL(3,2) DEFAULT 0.70,
    max_risk_level VARCHAR(20) DEFAULT 'medium',
    preferred_timeframes TEXT[] DEFAULT '{"1d"}',
    notification_enabled BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## **Script 5: Viral Growth System**
```sql
-- Invitations for viral growth
CREATE TABLE IF NOT EXISTS public.invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inviter_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    invitee_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    invitation_code VARCHAR(50) UNIQUE NOT NULL,
    invitation_link TEXT,
    message TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending',
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
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    commission_amount DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(4,3) NOT NULL,
    credit_purchase_id UUID,
    slot_subscription_id UUID,
    status VARCHAR(20) DEFAULT 'pending',
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Milestone achievements
CREATE TABLE IF NOT EXISTS public.milestone_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,
    milestone_level INTEGER NOT NULL,
    invites_required INTEGER,
    invites_achieved INTEGER,
    credits_awarded INTEGER DEFAULT 0,
    commission_rate_boost DECIMAL(4,3) DEFAULT 0.000,
    free_slots_awarded INTEGER DEFAULT 0,
    special_features TEXT[] DEFAULT '{}',
    achieved_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

---

## **Script 6: Payments and Credits System**
```sql
-- Credit purchases
CREATE TABLE IF NOT EXISTS public.credit_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    credits_amount INTEGER NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    stripe_payment_intent_id VARCHAR(255),
    stripe_charge_id VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'pending',
    referrer_id UUID REFERENCES public.users(id),
    commission_paid DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Withdrawal requests
CREATE TABLE IF NOT EXISTS public.withdrawal_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    amount_credits INTEGER NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    withdrawal_method VARCHAR(50) NOT NULL,
    bank_account_id VARCHAR(255),
    crypto_address TEXT,
    paypal_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    processed_at TIMESTAMPTZ,
    transaction_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Slot subscriptions
CREATE TABLE IF NOT EXISTS public.slot_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    slot_type VARCHAR(50) DEFAULT 'premium',
    slots_count INTEGER DEFAULT 1,
    monthly_price_credits INTEGER NOT NULL,
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## **Script 7: Alerts and User Profiles**
```sql
-- Trigger alerts
CREATE TABLE IF NOT EXISTS public.trigger_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    trigger_event_id UUID REFERENCES public.trigger_events(id),
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    success_rate DECIMAL(5,4),
    expected_profit DECIMAL(8,4),
    risk_level VARCHAR(20),
    timeframe VARCHAR(10),
    delivery_method VARCHAR(50) DEFAULT 'app',
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    credits_charged INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles for personalization
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    trading_style VARCHAR(50) DEFAULT 'beginner',
    risk_level VARCHAR(50) DEFAULT 'moderate',
    preferred_timeframes TEXT[] DEFAULT '{"1d"}',
    tracked_symbols TEXT[] DEFAULT '{}',
    alert_preferences JSONB DEFAULT '{"price_alerts": true, "pattern_alerts": true, "whale_alerts": false, "frequency": "important_only"}',
    questions_asked JSONB[] DEFAULT '{}',
    favorite_patterns TEXT[] DEFAULT '{}',
    successful_triggers TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brain API cache
CREATE TABLE IF NOT EXISTS public.brain_api_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    query_hash VARCHAR(255) NOT NULL,
    response_data JSONB NOT NULL,
    response_text TEXT,
    ttl_seconds INTEGER DEFAULT 3600,
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '1 hour'),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User memory for learning
CREATE TABLE IF NOT EXISTS public.brain_user_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    total_interactions INTEGER DEFAULT 0,
    common_questions JSONB DEFAULT '{}',
    learning_patterns JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    last_active TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brain evolution log
CREATE TABLE IF NOT EXISTS public.brain_evolution_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evolution_type VARCHAR(50) NOT NULL,
    description TEXT,
    metrics_before JSONB,
    metrics_after JSONB,
    changes_made JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## **Script 8: Helper Functions**
```sql
-- Deduct credits function
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

-- Find similar knowledge using embeddings
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

-- Increment knowledge usage
CREATE OR REPLACE FUNCTION increment_knowledge_usage(knowledge_uuid UUID)
RETURNS VOID
LANGUAGE sql
AS $$
    UPDATE public.brain_knowledge
    SET usage_count = usage_count + 1,
        last_accessed = NOW()
    WHERE id = knowledge_uuid;
$$;

-- Clean expired cache
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS INTEGER
LANGUAGE sql
AS $$
    WITH deleted AS (
        DELETE FROM public.brain_api_cache
        WHERE expires_at < NOW()
        RETURNING id
    )
    SELECT COUNT(*) FROM deleted;
$$;
```

---

## **Script 9: Row Level Security Setup**
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
CREATE POLICY "Users can view own data" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can view own profile data" ON public.user_profiles FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own subscriptions" ON public.trigger_subscriptions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own invitations" ON public.invitations FOR ALL USING (auth.uid() = inviter_id OR auth.uid() = invitee_id);
CREATE POLICY "Users can view own alerts" ON public.trigger_alerts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Anyone can view public patterns" ON public.historical_patterns FOR SELECT USING (is_active = true);
CREATE POLICY "Anyone can view active triggers" ON public.trigger_events FOR SELECT USING (is_active = true);
```

---

## **Verification Script**
```sql
-- Verify all tables are created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'users', 'brain_knowledge', 'historical_patterns',
    'invitations', 'trigger_events', 'user_profiles'
)
ORDER BY table_name;
```

---

## 🎯 **EXECUTION STEPS:**

1. **Go to**: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql
2. **Copy Script 1** → Paste → Click "Run"
3. **Copy Script 2** → Paste → Click "Run"
4. **Continue through all 9 scripts**
5. **Run verification script to confirm**

**Each script should show "Success. No rows returned" - this is GOOD!**

Let me know when you've completed this and I'll verify the deployment!