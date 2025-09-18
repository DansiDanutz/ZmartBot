# 🚀 ZmartyChat Complete Setup Guide

## ✅ Current Status

Your Supabase URL is configured: `https://asjtxrmftmutcsnqgidy.supabase.co`

## 📋 Setup Steps

### 1. Get Your Supabase Keys

1. Go to your Supabase project: https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy
2. Click on **Settings** → **API**
3. Copy these keys and add them to your `.env` file:
   - **anon public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_KEY` (keep this secret!)

### 2. Run Database Migration

1. Go to your Supabase SQL Editor:
   https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql

2. Click **New query**

3. Copy and paste the entire contents of:
   ```
   database/zmartychat_complete_schema.sql
   ```

4. Click **Run** to create all tables

### 3. Enable Row Level Security (RLS)

After creating tables, run this query to enable RLS:

```sql
-- Enable RLS on all ZmartyChat tables
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

-- Create basic RLS policies
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
```

### 4. Insert Initial Data

Run this to add subscription plans:

```sql
INSERT INTO zmartychat_subscription_plans (plan_name, tier, price_monthly, price_yearly, monthly_credits, features) VALUES
('Free', 'free', 0, 0, 100, ARRAY['Basic chat', 'Market data', 'Limited analysis']),
('Basic', 'basic', 9.99, 99.99, 1000, ARRAY['Everything in Free', 'Technical analysis', 'Basic AI predictions', 'Email support']),
('Pro', 'pro', 29.99, 299.99, 5000, ARRAY['Everything in Basic', 'Advanced AI features', 'Priority data', 'Custom alerts', 'API access']),
('Premium', 'premium', 99.99, 999.99, 20000, ARRAY['Everything in Pro', 'Unlimited AI queries', 'All agents', 'White-glove support', 'Custom models']);
```

### 5. Create Database Functions

Run this to create the credit deduction function:

```sql
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
```

### 6. Test Your Setup

Run the setup test:
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat
node test-setup.js
```

### 7. Start the Application

```bash
# Terminal 1: Main server
npm run dev

# Terminal 2: Serve frontend
npm run serve
```

Then open: http://localhost:8080

## 🔍 Verify Everything Works

### Check Tables Were Created

In Supabase Table Editor, you should see:
- zmartychat_users
- zmartychat_credit_transactions
- zmartychat_user_categories
- zmartychat_user_transcripts
- zmartychat_conversation_messages
- zmartychat_user_insights
- zmartychat_addiction_metrics
- zmartychat_subscription_plans
- zmartychat_user_subscriptions
- zmartychat_achievements
- zmartychat_user_achievements
- zmartychat_user_streaks
- zmartychat_referrals

### Test API Connection

```bash
curl http://localhost:3001/health
```

## 📱 Using Supabase MCP

The Supabase MCP tools available:
- `mcp__supabase__execute_sql` - Run queries
- `mcp__supabase__list_tables` - List tables
- `mcp__supabase__get_logs` - Get service logs

## 🎉 You're Ready!

Your ZmartyChat system is now:
✅ Connected to Supabase
✅ Database schema created
✅ Environment configured
✅ Ready to accept users

Next steps:
1. Register a test user
2. Start chatting with Zmarty
3. Watch the credits flow!

## 🆘 Need Help?

- Supabase Dashboard: https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy
- Check logs: `npm run logs`
- Database issues: Check SQL Editor in Supabase