-- FINAL COMPLETE DATABASE FIX FOR ZMARTYBRAIN
-- Run this entire script in Supabase SQL Editor
-- This consolidates ALL fixes in the correct order

-- ========================================
-- 1. DROP OLD/PROBLEMATIC OBJECTS FIRST
-- ========================================

-- Drop problematic views and functions
DROP TABLE IF EXISTS public.user_profiles CASCADE;
DROP VIEW IF EXISTS public.user_profiles CASCADE;
DROP VIEW IF EXISTS public.user_details CASCADE;
DROP FUNCTION IF EXISTS public.get_user_profile(uuid) CASCADE;
DROP FUNCTION IF EXISTS public.update_user_tier CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user CASCADE;
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- ========================================
-- 2. CREATE SECURE VIEW
-- ========================================

CREATE VIEW public.user_profiles AS
SELECT
    p.id,
    p.full_name,
    p.updated_at
FROM public.profiles p
WHERE p.id = auth.uid();

-- Set permissions
GRANT SELECT ON public.user_profiles TO authenticated;
REVOKE ALL ON public.user_profiles FROM anon;

-- ========================================
-- 3. CREATE SECURE FUNCTIONS
-- ========================================

-- Create secure get_user_profile function
CREATE FUNCTION public.get_user_profile(user_id uuid)
RETURNS TABLE (
    id uuid,
    full_name text
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public
AS $$
BEGIN
    IF user_id = auth.uid() OR auth.jwt()->>'role' = 'service_role' THEN
        RETURN QUERY
        SELECT p.id, p.full_name
        FROM public.profiles p
        WHERE p.id = user_id;
    ELSE
        RETURN;
    END IF;
END;
$$;

-- Create handle_new_user function with fixed search_path
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
SET search_path = public
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, created_at, updated_at)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        NEW.email,
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

-- Create update_user_tier function with fixed search_path
CREATE OR REPLACE FUNCTION public.update_user_tier()
RETURNS trigger
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    -- Add your tier update logic here
    RETURN NEW;
END;
$$;

-- Recreate trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.get_user_profile(uuid) TO authenticated;
REVOKE EXECUTE ON FUNCTION public.get_user_profile(uuid) FROM anon;

-- ========================================
-- 4. ENABLE RLS
-- ========================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_credits ENABLE ROW LEVEL SECURITY;

-- ========================================
-- 5. FIX RLS POLICIES (OPTIMIZED)
-- ========================================

-- Drop old policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view own credits" ON public.user_credits;

-- Create optimized policies with single auth.uid() call
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT
    USING (id = (SELECT auth.uid()));

CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT
    WITH CHECK (id = (SELECT auth.uid()));

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE
    USING (id = (SELECT auth.uid()))
    WITH CHECK (id = (SELECT auth.uid()));

CREATE POLICY "Users can view own credits" ON public.user_credits
    FOR SELECT
    USING (user_id = (SELECT auth.uid()));

-- ========================================
-- 6. ADD ALL MISSING INDEXES
-- ========================================

-- Core table indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_brain_categories_parent_id ON public.brain_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_brain_knowledge_category_id ON public.brain_knowledge(category_id);
CREATE INDEX IF NOT EXISTS idx_brain_user_interactions_user_id ON public.brain_user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_brain_user_memory_user_id ON public.brain_user_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_commission_transactions_invitation_id ON public.commission_transactions(invitation_id);
CREATE INDEX IF NOT EXISTS idx_commission_transactions_invitee_id ON public.commission_transactions(invitee_id);
CREATE INDEX IF NOT EXISTS idx_commission_transactions_inviter_id ON public.commission_transactions(inviter_id);
CREATE INDEX IF NOT EXISTS idx_credit_purchases_referrer_id ON public.credit_purchases(referrer_id);
CREATE INDEX IF NOT EXISTS idx_credit_purchases_user_id ON public.credit_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee_id ON public.invitations(invitee_id);
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_id ON public.invitations(inviter_id);
CREATE INDEX IF NOT EXISTS idx_milestone_achievements_user_id ON public.milestone_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_slot_subscriptions_user_id ON public.slot_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_signals_user_id ON public.trading_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_trigger_alerts_trigger_event_id ON public.trigger_alerts(trigger_event_id);
CREATE INDEX IF NOT EXISTS idx_trigger_alerts_user_id ON public.trigger_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_trigger_events_pattern_id ON public.trigger_events(pattern_id);
CREATE INDEX IF NOT EXISTS idx_trigger_subscriptions_user_id ON public.trigger_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON public.user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON public.user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_user_credits_user_id ON public.user_credits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id ON public.user_portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_strategies_user_id ON public.user_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON public.user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_user_id ON public.withdrawal_requests(user_id);

-- ZmartyChat specific indexes
CREATE INDEX IF NOT EXISTS idx_zmartychat_referrals_referred_id ON public.zmartychat_referrals(referred_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_referrals_referrer_id ON public.zmartychat_referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_achievements_achievement_id ON public.zmartychat_user_achievements(achievement_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_achievements_user_id ON public.zmartychat_user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_streaks_user_id ON public.zmartychat_user_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_subscriptions_plan_id ON public.zmartychat_user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_subscriptions_user_id ON public.zmartychat_user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_transcripts_user_id ON public.zmartychat_user_transcripts(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_conversation_messages_user_id ON public.zmartychat_conversation_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_credit_transactions_user_id ON public.zmartychat_credit_transactions(user_id);

-- ========================================
-- 7. DROP UNUSED INDEXES
-- ========================================

DROP INDEX IF EXISTS public.idx_users_username;
DROP INDEX IF EXISTS public.idx_users_email;
DROP INDEX IF EXISTS public.idx_users_commission_tier;
DROP INDEX IF EXISTS public.idx_zmartychat_users_email;
DROP INDEX IF EXISTS public.idx_conversation_messages_user_id;
DROP INDEX IF EXISTS public.idx_subscriptions_status;
DROP INDEX IF EXISTS public.idx_notifications_read_at;
DROP INDEX IF EXISTS public.idx_zmartychat_users_country;
DROP INDEX IF EXISTS public.idx_zmartychat_users_tier;
DROP INDEX IF EXISTS public.idx_conversation_messages_conversation_id;
DROP INDEX IF EXISTS public.idx_user_subscriptions_status;
DROP INDEX IF EXISTS public.idx_referrals_referral_code;
DROP INDEX IF EXISTS public.idx_user_engagement_metrics_date;
DROP INDEX IF EXISTS public.idx_audit_log_created_at;
DROP INDEX IF EXISTS public.idx_credit_transactions_created_at;

-- ========================================
-- COMPLETE! All fixes applied.
-- ========================================