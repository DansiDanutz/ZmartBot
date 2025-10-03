-- =====================================================
-- ADD ALL FOREIGN KEY INDEXES
-- =====================================================
-- These indexes are required for foreign key performance
-- Even if marked as "unused", they prevent table scans on foreign key checks

-- =====================================================
-- COMMISSION TRANSACTIONS INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_commission_transactions_invitation_id
ON public.commission_transactions(invitation_id);

CREATE INDEX IF NOT EXISTS idx_commission_transactions_invitee_id
ON public.commission_transactions(invitee_id);

CREATE INDEX IF NOT EXISTS idx_commission_transactions_inviter_id
ON public.commission_transactions(inviter_id);

-- =====================================================
-- CREDIT RELATED INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_credit_purchases_referrer_id
ON public.credit_purchases(referrer_id);

CREATE INDEX IF NOT EXISTS idx_credit_purchases_user_id
ON public.credit_purchases(user_id);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id
ON public.credit_transactions(user_id);

-- =====================================================
-- MILESTONE AND SLOT INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_milestone_achievements_user_id
ON public.milestone_achievements(user_id);

CREATE INDEX IF NOT EXISTS idx_slot_subscriptions_user_id
ON public.slot_subscriptions(user_id);

-- =====================================================
-- TRIGGER RELATED INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_trigger_alerts_trigger_event_id
ON public.trigger_alerts(trigger_event_id);

CREATE INDEX IF NOT EXISTS idx_trigger_alerts_user_id
ON public.trigger_alerts(user_id);

CREATE INDEX IF NOT EXISTS idx_trigger_events_pattern_id
ON public.trigger_events(pattern_id);

CREATE INDEX IF NOT EXISTS idx_trigger_subscriptions_user_id
ON public.trigger_subscriptions(user_id);

-- =====================================================
-- USER RELATED INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id
ON public.user_api_keys(user_id);

CREATE INDEX IF NOT EXISTS idx_user_credits_user_id
ON public.user_credits(user_id);

CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id
ON public.user_portfolios(user_id);

CREATE INDEX IF NOT EXISTS idx_user_strategies_user_id
ON public.user_strategies(user_id);

CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_user_id
ON public.withdrawal_requests(user_id);

-- =====================================================
-- ZMARTYCHAT INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_zmartychat_conversation_messages_user_id
ON public.zmartychat_conversation_messages(user_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_credit_transactions_user_id
ON public.zmartychat_credit_transactions(user_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_referrals_referred_id
ON public.zmartychat_referrals(referred_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_referrals_referrer_id
ON public.zmartychat_referrals(referrer_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_user_achievements_achievement_id
ON public.zmartychat_user_achievements(achievement_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_user_achievements_user_id
ON public.zmartychat_user_achievements(user_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_user_streaks_user_id
ON public.zmartychat_user_streaks(user_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_user_subscriptions_plan_id
ON public.zmartychat_user_subscriptions(plan_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_user_subscriptions_user_id
ON public.zmartychat_user_subscriptions(user_id);

CREATE INDEX IF NOT EXISTS idx_zmartychat_user_transcripts_user_id
ON public.zmartychat_user_transcripts(user_id);

-- =====================================================
-- BRAIN KNOWLEDGE INDEXES (if not already created)
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_brain_categories_parent_id
ON public.brain_categories(parent_id);

CREATE INDEX IF NOT EXISTS idx_brain_knowledge_category_id
ON public.brain_knowledge(category_id);

CREATE INDEX IF NOT EXISTS idx_brain_user_interactions_user_id
ON public.brain_user_interactions(user_id);

CREATE INDEX IF NOT EXISTS idx_brain_user_memory_user_id
ON public.brain_user_memory(user_id);

-- =====================================================
-- INVITATIONS INDEXES (needed for RLS)
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_id
ON public.invitations(inviter_id);

CREATE INDEX IF NOT EXISTS idx_invitations_invitee_id
ON public.invitations(invitee_id);

-- =====================================================
-- ANALYZE TABLES FOR STATISTICS
-- =====================================================
ANALYZE public.commission_transactions;
ANALYZE public.credit_purchases;
ANALYZE public.credit_transactions;
ANALYZE public.milestone_achievements;
ANALYZE public.slot_subscriptions;
ANALYZE public.trigger_alerts;
ANALYZE public.trigger_events;
ANALYZE public.trigger_subscriptions;
ANALYZE public.user_api_keys;
ANALYZE public.user_credits;
ANALYZE public.user_portfolios;
ANALYZE public.user_strategies;
ANALYZE public.withdrawal_requests;
ANALYZE public.zmartychat_conversation_messages;
ANALYZE public.zmartychat_credit_transactions;
ANALYZE public.zmartychat_referrals;
ANALYZE public.zmartychat_user_achievements;
ANALYZE public.zmartychat_user_streaks;
ANALYZE public.zmartychat_user_subscriptions;
ANALYZE public.zmartychat_user_transcripts;
ANALYZE public.brain_categories;
ANALYZE public.brain_knowledge;
ANALYZE public.brain_user_interactions;
ANALYZE public.brain_user_memory;
ANALYZE public.invitations;

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT
    'Total indexes created' as status,
    COUNT(*) as count
FROM pg_indexes
WHERE schemaname = 'public'
AND indexname LIKE 'idx_%';

-- =====================================================
-- SUMMARY
-- =====================================================
-- This script creates 32 indexes for all foreign keys
-- These indexes are NECESSARY even if they show as "unused"
-- They prevent full table scans when checking foreign key constraints
--
-- The "unused" status in the linter just means they haven't been
-- used in queries yet, but they're still important for:
-- 1. Foreign key constraint checks
-- 2. CASCADE deletes/updates
-- 3. JOIN operations
-- 4. Future query optimization