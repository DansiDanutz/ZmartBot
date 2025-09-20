-- ============================================
-- CLEANUP SMART TRADING PROJECT
-- Run this in Smart Trading (asjtxrmftmutcsnqgidy)
-- ============================================

-- STEP 1: DELETE ALL TEST USERS
-- This removes users from auth.users table
DELETE FROM auth.users
WHERE email IN (
    'semebitcoin@gmail.com',
    'dansidanutz@yahoo.com',
    'mik4fish@yahoo.com',
    'seme@kryptostack.com'
);

-- Or delete ALL users if you want to start fresh:
-- DELETE FROM auth.users;

-- ============================================
-- STEP 2: DROP ZMARTYCHAT TABLES
-- These belong in ZmartyBrain, not here
-- ============================================

-- Drop all zmartychat tables (CASCADE removes dependencies)
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

-- ============================================
-- STEP 3: DROP USER MANAGEMENT TABLES
-- These also belong in ZmartyBrain
-- ============================================

DROP TABLE IF EXISTS user_api_keys CASCADE;
DROP TABLE IF EXISTS user_portfolios CASCADE;
DROP TABLE IF EXISTS user_strategies CASCADE;
DROP TABLE IF EXISTS user_trading_profiles CASCADE;

-- Note: Keep user_trades in Smart Trading as it's trading data

-- ============================================
-- VERIFICATION: Check what's left
-- ============================================

-- List remaining tables (should only be trading-related)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Count remaining users (should be 0)
SELECT COUNT(*) as user_count FROM auth.users;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================
SELECT 'Smart Trading cleaned! Only trading tables remain.' as status;