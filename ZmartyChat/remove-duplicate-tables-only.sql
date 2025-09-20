-- ============================================
-- REMOVE ONLY DUPLICATE TABLES FROM SMART TRADING
-- These tables should be in ZmartyBrain, not here
-- Run this in Smart Trading (asjtxrmftmutcsnqgidy)
-- ============================================

-- Drop zmartychat tables (they belong in ZmartyBrain)
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

-- Drop user management tables (they belong in ZmartyBrain)
DROP TABLE IF EXISTS user_api_keys CASCADE;
DROP TABLE IF EXISTS user_portfolios CASCADE;
DROP TABLE IF EXISTS user_strategies CASCADE;
DROP TABLE IF EXISTS user_trading_profiles CASCADE;

-- KEEP user_trades (it can stay here for trading history)
-- KEEP all cryptometer_* tables
-- KEEP all cryptoverse_* tables
-- KEEP all other trading tables

SELECT 'Removed duplicate user tables. Trading tables remain.' as status;