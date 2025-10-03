-- =====================================================
-- FIX ALL SUPABASE PERFORMANCE ISSUES
-- =====================================================
-- This script addresses:
-- 1. Unindexed foreign keys
-- 2. Unused indexes (cleanup)
-- 3. General performance optimizations

-- =====================================================
-- PART 1: ADD MISSING INDEXES FOR FOREIGN KEYS
-- =====================================================
-- These foreign keys are missing indexes which impacts query performance

-- Index for brain_categories.parent_id
CREATE INDEX IF NOT EXISTS idx_brain_categories_parent_id
ON public.brain_categories(parent_id);

-- Index for brain_knowledge.category_id
CREATE INDEX IF NOT EXISTS idx_brain_knowledge_category_id
ON public.brain_knowledge(category_id);

-- Index for brain_user_interactions.user_id
CREATE INDEX IF NOT EXISTS idx_brain_user_interactions_user_id
ON public.brain_user_interactions(user_id);

-- Index for brain_user_memory.user_id
CREATE INDEX IF NOT EXISTS idx_brain_user_memory_user_id
ON public.brain_user_memory(user_id);

-- =====================================================
-- PART 2: DROP UNUSED INDEXES
-- =====================================================
-- These indexes have never been used and can be safely removed
-- Removing them will improve INSERT/UPDATE/DELETE performance

-- Drop unused indexes for trigger_alerts
DROP INDEX IF EXISTS public.idx_trigger_alerts_user_id;

-- Drop unused indexes for trigger_events
DROP INDEX IF EXISTS public.idx_trigger_events_pattern_id;

-- Drop unused indexes for trigger_subscriptions
DROP INDEX IF EXISTS public.idx_trigger_subscriptions_user_id;

-- Drop unused indexes for user_api_keys
DROP INDEX IF EXISTS public.idx_user_api_keys_user_id;

-- Drop unused indexes for user_credits
DROP INDEX IF EXISTS public.idx_user_credits_user_id;

-- Drop unused indexes for user_portfolios
DROP INDEX IF EXISTS public.idx_user_portfolios_user_id;

-- Drop unused indexes for zmartychat tables
DROP INDEX IF EXISTS public.idx_zmartychat_conversation_messages_user_id;
DROP INDEX IF EXISTS public.idx_zmartychat_credit_transactions_user_id;
DROP INDEX IF EXISTS public.idx_zmartychat_referrals_referred_id;
DROP INDEX IF EXISTS public.idx_zmartychat_referrals_referrer_id;
DROP INDEX IF EXISTS public.idx_zmartychat_user_achievements_achievement_id;
DROP INDEX IF EXISTS public.idx_zmartychat_user_streaks_user_id;
DROP INDEX IF EXISTS public.idx_zmartychat_user_subscriptions_plan_id;
DROP INDEX IF EXISTS public.idx_zmartychat_user_subscriptions_user_id;
DROP INDEX IF EXISTS public.idx_zmartychat_user_achievements_user_id;
DROP INDEX IF EXISTS public.idx_zmartychat_user_transcripts_user_id;

-- Drop unused indexes for other tables
DROP INDEX IF EXISTS public.idx_user_strategies_user_id;
DROP INDEX IF EXISTS public.idx_withdrawal_requests_user_id;
DROP INDEX IF EXISTS public.idx_credit_transactions_user_id;
DROP INDEX IF EXISTS public.idx_credit_purchases_referrer_id;
DROP INDEX IF EXISTS public.idx_credit_purchases_user_id;
DROP INDEX IF EXISTS public.idx_milestone_achievements_user_id;
DROP INDEX IF EXISTS public.idx_slot_subscriptions_user_id;
DROP INDEX IF EXISTS public.idx_trigger_alerts_trigger_event_id;

-- Drop unused indexes for invitations (these were never used)
DROP INDEX IF EXISTS public.idx_invitations_status;
DROP INDEX IF EXISTS public.idx_invitations_invitation_code;
DROP INDEX IF EXISTS public.idx_invitations_inviter_status;
DROP INDEX IF EXISTS public.idx_invitations_invitee_status;

-- Drop unused commission_transactions indexes
DROP INDEX IF EXISTS public.idx_commission_transactions_invitation_id;
DROP INDEX IF EXISTS public.idx_commission_transactions_invitee_id;
DROP INDEX IF EXISTS public.idx_commission_transactions_inviter_id;

-- Keep these invitations indexes as they support RLS policies
-- idx_invitations_inviter_id
-- idx_invitations_invitee_id

-- =====================================================
-- PART 3: CREATE OPTIMIZED INDEXES
-- =====================================================
-- Create better indexes based on actual usage patterns

-- For invitations table (supporting RLS and common queries)
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_id
ON public.invitations(inviter_id)
WHERE status = 'pending'; -- Partial index for active invitations

CREATE INDEX IF NOT EXISTS idx_invitations_invitee_id
ON public.invitations(invitee_id)
WHERE status IN ('pending', 'accepted'); -- Most common statuses

-- For user tables (common lookup patterns)
CREATE INDEX IF NOT EXISTS idx_users_email
ON public.users(email)
WHERE email IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_username
ON public.users(username)
WHERE username IS NOT NULL;

-- For brain_knowledge (text search optimization)
CREATE INDEX IF NOT EXISTS idx_brain_knowledge_embedding
ON public.brain_knowledge
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE embedding IS NOT NULL AND is_active = true;

-- =====================================================
-- PART 4: ANALYZE TABLES FOR QUERY PLANNER
-- =====================================================
-- Update statistics for better query planning

ANALYZE public.invitations;
ANALYZE public.users;
ANALYZE public.brain_categories;
ANALYZE public.brain_knowledge;
ANALYZE public.brain_user_interactions;
ANALYZE public.brain_user_memory;
ANALYZE public.trigger_alerts;
ANALYZE public.trigger_events;
ANALYZE public.commission_transactions;
ANALYZE public.credit_purchases;

-- =====================================================
-- PART 5: VERIFICATION QUERIES
-- =====================================================

-- Check that foreign key indexes were created
SELECT
    'Foreign Key Indexes Created' as status,
    COUNT(*) as count
FROM pg_indexes
WHERE schemaname = 'public'
AND indexname IN (
    'idx_brain_categories_parent_id',
    'idx_brain_knowledge_category_id',
    'idx_brain_user_interactions_user_id',
    'idx_brain_user_memory_user_id'
);

-- Verify unused indexes were dropped
SELECT
    'Remaining Indexes on invitations table' as status,
    string_agg(indexname, ', ') as indexes
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename = 'invitations';

-- Show table sizes and index usage stats
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND tablename IN ('invitations', 'users', 'brain_knowledge', 'brain_categories')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =====================================================
-- SUMMARY OF CHANGES
-- =====================================================
-- 1. Added 4 missing indexes for foreign keys
-- 2. Dropped 30+ unused indexes to improve write performance
-- 3. Created optimized partial indexes for common query patterns
-- 4. Analyzed tables to update query planner statistics
--
-- Expected improvements:
-- - Faster queries on foreign key joins
-- - Reduced storage overhead from unused indexes
-- - Better INSERT/UPDATE/DELETE performance
-- - More efficient query plans from updated statistics