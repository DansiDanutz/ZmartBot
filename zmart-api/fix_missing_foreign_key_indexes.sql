-- ============================================================================
-- ZMARTBOT DATABASE OPTIMIZATION - MISSING FOREIGN KEY INDEXES
-- ============================================================================
-- Purpose: Add indexes to foreign keys to improve query performance
-- Date: 2025-10-01
-- Issue: 7 foreign keys without covering indexes causing suboptimal performance
-- ============================================================================

-- Before running this script:
-- 1. Backup your database
-- 2. Run during low-traffic period if possible
-- 3. Monitor query performance before/after

BEGIN;

-- ============================================================================
-- 1. manus_extraordinary_reports.alert_id
-- ============================================================================
-- Table: public.manus_extraordinary_reports
-- FK: manus_extraordinary_reports_alert_id_fkey
-- Impact: Improves joins and lookups on alert_id

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_manus_reports_alert_id
ON public.manus_extraordinary_reports(alert_id);

COMMENT ON INDEX idx_manus_reports_alert_id IS
'Index on alert_id foreign key for better join performance';

-- ============================================================================
-- 2. trade_history.account_id
-- ============================================================================
-- Table: public.trade_history
-- FK: trade_history_account_id_fkey
-- Impact: Improves queries filtering/joining by account_id

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trade_history_account_id
ON public.trade_history(account_id);

COMMENT ON INDEX idx_trade_history_account_id IS
'Index on account_id foreign key for trade history queries';

-- ============================================================================
-- 3. trade_history.portfolio_id
-- ============================================================================
-- Table: public.trade_history
-- FK: trade_history_portfolio_id_fkey
-- Impact: Improves portfolio-based trade queries

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trade_history_portfolio_id
ON public.trade_history(portfolio_id);

COMMENT ON INDEX idx_trade_history_portfolio_id IS
'Index on portfolio_id foreign key for portfolio trade lookups';

-- ============================================================================
-- 4. trade_history.strategy_id
-- ============================================================================
-- Table: public.trade_history
-- FK: trade_history_strategy_id_fkey
-- Impact: Improves strategy performance analysis queries

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trade_history_strategy_id
ON public.trade_history(strategy_id);

COMMENT ON INDEX idx_trade_history_strategy_id IS
'Index on strategy_id foreign key for strategy-based queries';

-- ============================================================================
-- 5. zmartychat_conversation_messages.transcript_id
-- ============================================================================
-- Table: public.zmartychat_conversation_messages
-- FK: zmartychat_conversation_messages_transcript_id_fkey
-- Impact: Improves conversation message retrieval

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversation_messages_transcript_id
ON public.zmartychat_conversation_messages(transcript_id);

COMMENT ON INDEX idx_conversation_messages_transcript_id IS
'Index on transcript_id foreign key for message retrieval';

-- ============================================================================
-- 6. zmartychat_referrals.referred_id
-- ============================================================================
-- Table: public.zmartychat_referrals
-- FK: zmartychat_referrals_referred_id_fkey
-- Impact: Improves referral tracking queries

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referrals_referred_id
ON public.zmartychat_referrals(referred_id);

COMMENT ON INDEX idx_referrals_referred_id IS
'Index on referred_id foreign key for referral tracking';

-- ============================================================================
-- 7. zmartychat_user_subscriptions.plan_id
-- ============================================================================
-- Table: public.zmartychat_user_subscriptions
-- FK: zmartychat_user_subscriptions_plan_id_fkey
-- Impact: Improves subscription plan queries

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_subscriptions_plan_id
ON public.zmartychat_user_subscriptions(plan_id);

COMMENT ON INDEX idx_user_subscriptions_plan_id IS
'Index on plan_id foreign key for subscription queries';

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify indexes were created successfully:

-- Check all new indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname IN (
    'idx_manus_reports_alert_id',
    'idx_trade_history_account_id',
    'idx_trade_history_portfolio_id',
    'idx_trade_history_strategy_id',
    'idx_conversation_messages_transcript_id',
    'idx_referrals_referred_id',
    'idx_user_subscriptions_plan_id'
)
ORDER BY tablename, indexname;

-- Check index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexrelname IN (
    'idx_manus_reports_alert_id',
    'idx_trade_history_account_id',
    'idx_trade_history_portfolio_id',
    'idx_trade_history_strategy_id',
    'idx_conversation_messages_transcript_id',
    'idx_referrals_referred_id',
    'idx_user_subscriptions_plan_id'
)
ORDER BY tablename;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- - CONCURRENTLY option allows index creation without locking the table
-- - If CONCURRENTLY fails, remove it and run during maintenance window
-- - Monitor query performance improvements using pg_stat_statements
-- - Expected impact: 20-80% improvement on FK join queries
-- ============================================================================
