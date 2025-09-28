-- ============================================
-- CHECK AUTH CONFIGURATION IN DATABASE
-- Run this in ZmartyBrain SQL Editor
-- ============================================

-- 1. Check if there are any auth configuration settings
SELECT
    'Auth Configuration Check' as check_type,
    NOW() as checked_at;

-- 2. Check recent signups for leaked password errors
SELECT
    created_at,
    ip_address,
    CASE
        WHEN payload->>'event_message' ILIKE '%leak%' THEN '✅ HIBP Active'
        WHEN payload->>'event_message' ILIKE '%compromised%' THEN '✅ HIBP Active'
        WHEN payload->>'event_message' ILIKE '%pwned%' THEN '✅ HIBP Active'
        WHEN payload->>'event_message' ILIKE '%breach%' THEN '✅ HIBP Active'
        WHEN payload->>'event_message' ILIKE '%weak%' THEN '⚠️ Weak password check'
        ELSE 'Other'
    END as protection_status,
    payload->>'event_message' as message
FROM auth.audit_log_entries
WHERE
    created_at > NOW() - INTERVAL '1 hour'
    AND payload->>'action' IN ('signup', 'user_signedup')
ORDER BY created_at DESC
LIMIT 10;

-- 3. Check if any users were blocked recently
SELECT
    'Recent Auth Activity' as report,
    COUNT(*) FILTER (WHERE payload->>'event_message' ILIKE '%leak%' OR
                           payload->>'event_message' ILIKE '%compromised%' OR
                           payload->>'event_message' ILIKE '%pwned%') as blocked_by_hibp,
    COUNT(*) FILTER (WHERE payload->>'action' = 'signup') as total_signups,
    COUNT(*) FILTER (WHERE payload->>'event_message' ILIKE '%fail%') as failed_attempts
FROM auth.audit_log_entries
WHERE created_at > NOW() - INTERVAL '24 hours';

-- 4. Check auth.users for any test accounts
SELECT
    email,
    created_at,
    last_sign_in_at,
    CASE
        WHEN email LIKE '%test-hibp%' THEN 'Test account for HIBP'
        ELSE 'Regular user'
    END as account_type
FROM auth.users
WHERE email LIKE '%test%'
ORDER BY created_at DESC
LIMIT 5;

-- 5. Summary
SELECT
    '📊 AUTH STATUS SUMMARY' as status,
    CASE
        WHEN EXISTS (
            SELECT 1 FROM auth.audit_log_entries
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND (payload->>'event_message' ILIKE '%leak%' OR
                 payload->>'event_message' ILIKE '%compromised%')
        ) THEN '✅ HIBP appears to be ACTIVE'
        ELSE '⚠️ No recent HIBP blocks detected - may need more testing'
    END as hibp_status;