-- ============================================
-- FIRST: Check if table exists and its structure
-- ============================================

-- Check if user_profiles table exists
SELECT
    EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
    ) as table_exists;

-- If it exists, show its columns
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Check constraints
SELECT
    conname as constraint_name,
    contype as constraint_type
FROM pg_constraint
WHERE conrelid = 'public.user_profiles'::regclass;

-- Check if auth.users has email column
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'auth'
AND table_name = 'users'
AND column_name IN ('id', 'email', 'raw_user_meta_data')
ORDER BY ordinal_position;