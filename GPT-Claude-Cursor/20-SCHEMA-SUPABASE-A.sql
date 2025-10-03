-- ============================================================================
-- Supabase A: Zmarty Chat Database
-- Purpose: Authentication, user management, credits tracking, user symbols
-- ============================================================================

-- Extension: Ensure UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: user_symbols
-- Purpose: Tracks which trading symbols each user is watching
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_symbols (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL CHECK (LENGTH(symbol) > 0),
  timeframe TEXT NOT NULL DEFAULT '1h' CHECK (timeframe IN ('1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w')),
  strategy JSONB DEFAULT '{}'::JSONB,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, symbol, timeframe)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_symbols_user_id ON public.user_symbols(user_id);
CREATE INDEX IF NOT EXISTS idx_user_symbols_symbol ON public.user_symbols(symbol);
CREATE INDEX IF NOT EXISTS idx_user_symbols_active ON public.user_symbols(active) WHERE active = TRUE;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_symbols_updated_at
  BEFORE UPDATE ON public.user_symbols
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- Table: credits_ledger
-- Purpose: Tracks all credit transactions (charges and top-ups)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.credits_ledger (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  delta INTEGER NOT NULL,  -- Positive for top-up, negative for charge
  provider TEXT NOT NULL CHECK (provider IN ('grok', 'gpt', 'claude', 'data', 'topup', 'referral', 'bonus')),
  units JSONB DEFAULT '{}'::JSONB,  -- {input_tokens: N, output_tokens: M} for LLM calls
  reason TEXT,  -- e.g., 'chat_request', 'data_ingest', 'initial_bonus'
  metadata JSONB DEFAULT '{}'::JSONB,  -- Additional context (e.g., request_id, symbol)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_credits_ledger_user_id ON public.credits_ledger(user_id);
CREATE INDEX IF NOT EXISTS idx_credits_ledger_provider ON public.credits_ledger(provider);
CREATE INDEX IF NOT EXISTS idx_credits_ledger_created_at ON public.credits_ledger(created_at DESC);

-- ============================================================================
-- View: credit_balance
-- Purpose: Current credit balance per user (sum of all deltas)
-- ============================================================================
CREATE OR REPLACE VIEW public.credit_balance AS
SELECT 
  user_id,
  COALESCE(SUM(delta), 0) AS balance,
  COUNT(*) AS transaction_count,
  MAX(created_at) AS last_transaction_at
FROM public.credits_ledger
GROUP BY user_id;

-- ============================================================================
-- Table: user_profiles (optional, for tier management)
-- Purpose: Extended user information including tier and settings
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  full_name TEXT,
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
  max_tokens_per_request INTEGER DEFAULT 1024,
  max_requests_per_minute INTEGER DEFAULT 10,
  features JSONB DEFAULT '{}'::JSONB,  -- {voice: true, multiSymbol: false, etc}
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to update updated_at
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Function to auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email)
  VALUES (NEW.id, NEW.email);
  
  -- Give initial bonus credits
  INSERT INTO public.credits_ledger (user_id, delta, provider, reason)
  VALUES (NEW.id, 100, 'bonus', 'initial_signup_bonus');
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on user_symbols
ALTER TABLE public.user_symbols ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see/manage their own symbols
CREATE POLICY "users_manage_own_symbols"
  ON public.user_symbols
  FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Enable RLS on credits_ledger
ALTER TABLE public.credits_ledger ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own credit history
CREATE POLICY "users_read_own_credits"
  ON public.credits_ledger
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- Note: INSERT to credits_ledger is done by service_role (orchestrator-api)
-- No public INSERT policy needed

-- Enable RLS on user_profiles
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read and update their own profile
CREATE POLICY "users_manage_own_profile"
  ON public.user_profiles
  FOR ALL
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- ============================================================================
-- Utility Functions
-- ============================================================================

-- Function: Get user's current credit balance
CREATE OR REPLACE FUNCTION public.get_user_credits(p_user_id UUID)
RETURNS INTEGER AS $$
  SELECT COALESCE(balance, 0)::INTEGER
  FROM public.credit_balance
  WHERE user_id = p_user_id;
$$ LANGUAGE sql STABLE;

-- Function: Charge user credits (called by service_role)
CREATE OR REPLACE FUNCTION public.charge_user_credits(
  p_user_id UUID,
  p_amount INTEGER,
  p_provider TEXT,
  p_units JSONB DEFAULT '{}'::JSONB,
  p_reason TEXT DEFAULT 'chat_request',
  p_metadata JSONB DEFAULT '{}'::JSONB
)
RETURNS JSONB AS $$
DECLARE
  v_current_balance INTEGER;
  v_new_balance INTEGER;
BEGIN
  -- Get current balance
  v_current_balance := public.get_user_credits(p_user_id);
  
  -- Check if user has sufficient credits
  IF v_current_balance < p_amount THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'insufficient_credits',
      'current_balance', v_current_balance,
      'required', p_amount
    );
  END IF;
  
  -- Insert charge transaction
  INSERT INTO public.credits_ledger (user_id, delta, provider, units, reason, metadata)
  VALUES (p_user_id, -p_amount, p_provider, p_units, p_reason, p_metadata);
  
  -- Calculate new balance
  v_new_balance := v_current_balance - p_amount;
  
  RETURN jsonb_build_object(
    'success', true,
    'previous_balance', v_current_balance,
    'new_balance', v_new_balance,
    'charged', p_amount
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Uncomment to add sample data for development/testing
/*
-- Insert sample symbols for a test user (replace UUID with actual user_id)
INSERT INTO public.user_symbols (user_id, symbol, timeframe, strategy)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'BTC/USDT', '1h', '{"type": "momentum"}'::JSONB),
  ('00000000-0000-0000-0000-000000000001', 'ETH/USDT', '4h', '{"type": "trend_following"}'::JSONB),
  ('00000000-0000-0000-0000-000000000001', 'SOL/USDT', '1h', '{"type": "breakout"}'::JSONB)
ON CONFLICT (user_id, symbol, timeframe) DO NOTHING;

-- Add sample credit top-up
INSERT INTO public.credits_ledger (user_id, delta, provider, reason)
VALUES ('00000000-0000-0000-0000-000000000001', 500, 'topup', 'test_credit_purchase');
*/

-- ============================================================================
-- Maintenance Queries
-- ============================================================================

-- Check table sizes
-- SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables WHERE schemaname = 'public';

-- Check RLS policies
-- SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies WHERE schemaname = 'public';

-- View recent credit transactions
-- SELECT * FROM public.credits_ledger ORDER BY created_at DESC LIMIT 20;

-- View user balances
-- SELECT * FROM public.credit_balance ORDER BY balance DESC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================



