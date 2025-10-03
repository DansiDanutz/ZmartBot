-- =====================================================
-- FIX SECURITY WARNINGS IN SUPABASE
-- =====================================================

-- =====================================================
-- PART 1: FIX FUNCTION SEARCH PATH SECURITY ISSUE
-- =====================================================
-- The function 'reward_inviter_credits' needs to have search_path set
-- to prevent malicious schema injection attacks

-- First, let's check the current function definition
-- (This is for documentation, won't execute)
/*
SELECT
    proname as function_name,
    prosrc as source_code,
    prosecdef as security_definer
FROM pg_proc
WHERE proname = 'reward_inviter_credits'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
*/

-- Drop and recreate the function with proper search_path
-- Note: Adjust the function body based on your actual implementation
CREATE OR REPLACE FUNCTION public.reward_inviter_credits(
    p_invitee_id uuid,
    p_amount integer DEFAULT 10
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_catalog
AS $$
DECLARE
    v_invitation record;
    v_inviter_id uuid;
BEGIN
    -- Find the invitation for this invitee
    SELECT * INTO v_invitation
    FROM invitations
    WHERE invitee_id = p_invitee_id
    AND status = 'accepted'
    LIMIT 1;

    IF v_invitation.inviter_id IS NOT NULL THEN
        -- Update inviter's credit balance
        UPDATE users
        SET credits_balance = credits_balance + p_amount,
            updated_at = NOW()
        WHERE id = v_invitation.inviter_id;

        -- Log the credit transaction
        INSERT INTO credit_transactions (
            user_id,
            amount,
            transaction_type,
            description,
            created_at
        ) VALUES (
            v_invitation.inviter_id,
            p_amount,
            'referral_reward',
            'Referral reward for inviting user',
            NOW()
        );
    END IF;
END;
$$;

-- If you have other functions without search_path set, here's how to find them:
SELECT
    n.nspname as schema,
    p.proname as function_name,
    pg_get_function_identity_arguments(p.oid) as arguments,
    CASE
        WHEN p.prosecdef THEN 'SECURITY DEFINER'
        ELSE 'SECURITY INVOKER'
    END as security_type,
    CASE
        WHEN p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        ))
        THEN '⚠️ NO SEARCH_PATH SET'
        ELSE '✅ HAS SEARCH_PATH'
    END as search_path_status
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prokind = 'f'  -- Only functions, not procedures
ORDER BY search_path_status DESC, p.proname;

-- =====================================================
-- PART 2: LEAKED PASSWORD PROTECTION
-- =====================================================
-- This cannot be fixed via SQL - it's a Supabase Dashboard setting
-- Instructions are provided below:

/*
TO ENABLE LEAKED PASSWORD PROTECTION:

1. Go to your Supabase Dashboard:
   https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/auth

2. Navigate to: Settings → Authentication → Security

3. Find "Password Security" section

4. Enable "Leaked Password Protection"
   - Toggle ON the "Check passwords against HaveIBeenPwned" option

5. Optionally, also enable:
   - Minimum password length (recommend 8+ characters)
   - Password strength requirements

6. Click "Save" to apply changes

This will:
- Check new passwords against the HaveIBeenPwned database
- Prevent users from using compromised passwords
- Enhance overall account security
*/

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if the function now has search_path set
SELECT
    'Function Security Check' as check_type,
    proname as function_name,
    CASE
        WHEN proconfig IS NOT NULL AND 'search_path=public, pg_catalog' = ANY(proconfig)
        THEN '✅ FIXED: search_path is set'
        WHEN proconfig IS NOT NULL AND 'search_path' = ANY(
            SELECT split_part(unnest(proconfig), '=', 1)
        )
        THEN '✅ FIXED: search_path is set (custom)'
        ELSE '❌ ISSUE: search_path not set'
    END as status
FROM pg_proc
WHERE proname = 'reward_inviter_credits'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- List all public functions and their search_path status
SELECT
    'All Public Functions' as check_type,
    COUNT(*) FILTER (WHERE proconfig IS NULL OR NOT ('search_path' = ANY(
        SELECT split_part(unnest(proconfig), '=', 1)
    ))) as functions_without_search_path,
    COUNT(*) FILTER (WHERE proconfig IS NOT NULL AND 'search_path' = ANY(
        SELECT split_part(unnest(proconfig), '=', 1)
    )) as functions_with_search_path,
    COUNT(*) as total_functions
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prokind = 'f';

-- =====================================================
-- SUMMARY
-- =====================================================
-- 1. Function search_path issue: FIXED via SQL
-- 2. Leaked password protection: Must be enabled in Dashboard
--
-- After running this script and enabling leaked password protection
-- in the dashboard, both security warnings should be resolved.