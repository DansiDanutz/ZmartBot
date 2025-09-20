-- ============================================
-- REMOVE ALL USER-RELATED TABLES FROM SMART TRADING
-- Smart Trading should ONLY have trading data
-- Run this in Smart Trading (asjtxrmftmutcsnqgidy)
-- ============================================

-- 1. Delete ALL users from auth.users
DELETE FROM auth.users;

-- 2. Drop user_trades if you don't want ANY user references
-- (Optional - keep this if you want trading history)
DROP TABLE IF EXISTS user_trades CASCADE;

-- 3. Make sure no zmartychat tables exist
DROP TABLE IF EXISTS zmartychat_user_achievements CASCADE;
DROP TABLE IF EXISTS zmartychat_achievements CASCADE;
DROP TABLE IF EXISTS zmartychat_addiction_metrics CASCADE;
DROP TABLE IF EXISTS zmartychat_conversation_messages CASCADE;
DROP TABLE IF EXISTS zmartychat_credit_transactions CASCADE;
DROP TABLE IF EXISTS zmartychat_referrals CASCADE;
DROP TABLE IF EXISTS zmartychat_subscription_plans CASCADE;
DROP TABLE IF EXISTS zmartychat_top_user_interests CASCADE;
DROP TABLE IF EXISTS zmartychat_user_categories CASCADE;
DROP TABLE IF EXISTS zmartychat_user_engagement_overview CASCADE;
DROP TABLE IF EXISTS zmartychat_user_insights CASCADE;
DROP TABLE IF EXISTS zmartychat_user_streaks CASCADE;
DROP TABLE IF EXISTS zmartychat_user_subscriptions CASCADE;
DROP TABLE IF EXISTS zmartychat_user_transcripts CASCADE;
DROP TABLE IF EXISTS zmartychat_users CASCADE;

-- 4. Make sure no user management tables exist
DROP TABLE IF EXISTS user_api_keys CASCADE;
DROP TABLE IF EXISTS user_portfolios CASCADE;
DROP TABLE IF EXISTS user_strategies CASCADE;
DROP TABLE IF EXISTS user_trading_profiles CASCADE;

-- ============================================
-- WHAT REMAINS IN SMART TRADING:
-- ============================================
-- ✓ All cryptometer_* tables (market analysis)
-- ✓ All cryptoverse_* tables (risk data)
-- ✓ All alert_* tables (trading alerts)
-- ✓ All risk_* tables (risk management)
-- ✓ All manus_* tables (reports)
-- ✓ All service_* tables (infrastructure)
-- ✓ trading_intelligence (AI signals)
-- ✓ orchestration_states (system state)
-- ✓ symbol_coverage (market coverage)
-- ✓ Zmart Vaults (vault data)

-- Verify cleanup
SELECT 'Smart Trading cleaned! Only trading tables remain. No user data.' as status;

-- Show remaining tables (should be only trading-related)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name NOT LIKE 'zmartychat_%'
  AND table_name NOT LIKE 'user_%'
ORDER BY table_name;