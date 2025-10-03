-- =====================================================
-- CHECK CURRENT AUTH CONFIGURATION
-- =====================================================
-- This query checks the current auth configuration in your database

-- Check if auth config table exists and its settings
SELECT
    key,
    value,
    CASE
        WHEN key LIKE '%password%' THEN 'Password Setting'
        WHEN key LIKE '%hibp%' THEN 'HaveIBeenPwned Setting'
        WHEN key LIKE '%leak%' THEN 'Leak Protection'
        ELSE 'Other Setting'
    END as setting_type
FROM auth.config
WHERE key ILIKE '%password%'
   OR key ILIKE '%hibp%'
   OR key ILIKE '%leak%'
   OR key ILIKE '%pwned%'
ORDER BY setting_type, key;

-- Alternative: Check raw auth settings
SELECT *
FROM auth.config
WHERE key = 'password_min_length'
   OR key = 'hibp_enabled'
   OR key = 'leaked_password_protection'
   OR key = 'security_hibp_enabled';

-- If the above queries don't work, this might show available settings
SELECT
    'Available Auth Settings' as info,
    COUNT(*) as total_settings
FROM auth.config;