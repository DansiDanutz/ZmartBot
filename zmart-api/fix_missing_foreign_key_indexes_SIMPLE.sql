-- ============================================================================
-- ZMARTBOT DATABASE OPTIMIZATION - MISSING FOREIGN KEY INDEXES
-- ============================================================================
-- Purpose: Add indexes to foreign keys to improve query performance
-- Date: 2025-10-01
-- Version: SIMPLE (No CONCURRENTLY - for Supabase Dashboard)
-- ============================================================================

-- Note: This version creates indexes normally (not CONCURRENTLY)
-- This is safe for Supabase and works in the SQL Editor
-- Indexes will be created quickly since tables are not huge in production

-- ============================================================================
-- 1. manus_extraordinary_reports.alert_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_manus_reports_alert_id
ON public.manus_extraordinary_reports(alert_id);

-- ============================================================================
-- 2. trade_history.account_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_trade_history_account_id
ON public.trade_history(account_id);

-- ============================================================================
-- 3. trade_history.portfolio_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_trade_history_portfolio_id
ON public.trade_history(portfolio_id);

-- ============================================================================
-- 4. trade_history.strategy_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_trade_history_strategy_id
ON public.trade_history(strategy_id);

-- ============================================================================
-- 5. zmartychat_conversation_messages.transcript_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_conversation_messages_transcript_id
ON public.zmartychat_conversation_messages(transcript_id);

-- ============================================================================
-- 6. zmartychat_referrals.referred_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_referrals_referred_id
ON public.zmartychat_referrals(referred_id);

-- ============================================================================
-- 7. zmartychat_user_subscriptions.plan_id
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id
ON public.zmartychat_user_subscriptions(plan_id);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
-- If you see this without errors, all 7 indexes were created successfully!
-- Run the verification query below to confirm:

-- VERIFICATION QUERY (run this separately after):
/*
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
*/
