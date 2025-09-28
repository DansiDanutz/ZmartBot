-- ============================================
-- VERIFY AUTH SETTINGS & PASSWORD PROTECTION
-- Run in ZmartyBrain: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql
-- ============================================

-- 1. Check current auth configuration (if accessible)
-- Note: Some settings may require dashboard access
SELECT
    'Current Auth Security Check' as check_type,
    NOW() as checked_at;

-- 2. Check recent failed authentication attempts
SELECT
    created_at,
    CASE
        WHEN payload->>'event_message' LIKE '%password%' THEN 'Password Issue'
        WHEN payload->>'event_message' LIKE '%leaked%' THEN 'Leaked Password'
        WHEN payload->>'event_message' LIKE '%compromised%' THEN 'Compromised Password'
        ELSE 'Other Auth Issue'
    END as issue_type,
    payload->>'event_message' as message,
    payload->>'ip' as ip_address
FROM auth.audit_log_entries
WHERE
    created_at > NOW() - INTERVAL '7 days'
    AND payload->>'event_message' IS NOT NULL
    AND (
        payload->>'event_message' LIKE '%fail%'
        OR payload->>'event_message' LIKE '%error%'
        OR payload->>'event_message' LIKE '%invalid%'
    )
ORDER BY created_at DESC
LIMIT 20;

-- 3. Check user password update patterns
SELECT
    DATE(created_at) as date,
    COUNT(*) as password_updates,
    COUNT(DISTINCT payload->>'user_id') as unique_users
FROM auth.audit_log_entries
WHERE
    payload->>'action' = 'user_modified'
    AND payload->>'event_message' LIKE '%password%'
    AND created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 4. Identify users who might need password resets
SELECT
    u.email,
    u.created_at as user_created,
    u.last_sign_in_at,
    CASE
        WHEN u.last_sign_in_at < NOW() - INTERVAL '90 days' THEN 'Inactive - Consider Reset'
        WHEN u.created_at < '2024-01-01' THEN 'Old Account - Recommend Update'
        ELSE 'Active'
    END as recommendation
FROM auth.users u
WHERE
    u.last_sign_in_at IS NOT NULL
ORDER BY u.last_sign_in_at ASC
LIMIT 10;

-- 5. Check for any existing password policies in metadata
SELECT
    id,
    email,
    raw_user_meta_data->>'password_policy' as password_policy,
    raw_user_meta_data->>'password_strength' as password_strength,
    updated_at
FROM auth.users
WHERE
    raw_user_meta_data->>'password_policy' IS NOT NULL
    OR raw_user_meta_data->>'password_strength' IS NOT NULL
LIMIT 5;

-- 6. Summary of auth security status
SELECT
    'Auth Security Summary' as report,
    (SELECT COUNT(*) FROM auth.users) as total_users,
    (SELECT COUNT(*) FROM auth.users WHERE last_sign_in_at > NOW() - INTERVAL '7 days') as active_week,
    (SELECT COUNT(*) FROM auth.users WHERE last_sign_in_at > NOW() - INTERVAL '30 days') as active_month,
    (SELECT COUNT(*) FROM auth.audit_log_entries
     WHERE payload->>'event_message' LIKE '%fail%'
     AND created_at > NOW() - INTERVAL '24 hours') as failed_logins_24h;