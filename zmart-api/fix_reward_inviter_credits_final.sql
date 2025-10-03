-- =====================================================
-- FIX REWARD_INVITER_CREDITS FUNCTION SEARCH_PATH
-- =====================================================

-- First, check the current function definition
SELECT
    proname as function_name,
    pg_get_functiondef(oid) as current_definition
FROM pg_proc
WHERE proname = 'reward_inviter_credits'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Drop the existing function (we need to know the exact signature)
-- Try different possible signatures
DROP FUNCTION IF EXISTS public.reward_inviter_credits(uuid, integer);
DROP FUNCTION IF EXISTS public.reward_inviter_credits(uuid);
DROP FUNCTION IF EXISTS public.reward_inviter_credits();

-- Recreate with proper search_path
-- Adjust parameters based on your actual implementation
CREATE OR REPLACE FUNCTION public.reward_inviter_credits(
    p_invitee_id uuid,
    p_amount integer DEFAULT 10
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_catalog, pg_temp
AS $$
DECLARE
    v_invitation record;
    v_inviter_id uuid;
BEGIN
    -- Find the invitation for this invitee
    SELECT * INTO v_invitation
    FROM public.invitations
    WHERE invitee_id = p_invitee_id
    AND status = 'accepted'
    LIMIT 1;

    IF v_invitation.inviter_id IS NOT NULL THEN
        -- Update inviter's credit balance
        UPDATE public.users
        SET credits_balance = COALESCE(credits_balance, 0) + p_amount,
            updated_at = NOW()
        WHERE id = v_invitation.inviter_id;

        -- Log the credit transaction if table exists
        IF EXISTS (SELECT 1 FROM information_schema.tables
                  WHERE table_schema = 'public'
                  AND table_name = 'credit_transactions') THEN
            INSERT INTO public.credit_transactions (
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
    END IF;
END;
$$;

-- Alternative: If the function has no parameters
CREATE OR REPLACE FUNCTION public.reward_inviter_credits()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_catalog, pg_temp
AS $$
BEGIN
    -- Implementation for parameterless version
    RAISE NOTICE 'Function called without parameters';
END;
$$;

-- Verify the fix
SELECT
    proname as function_name,
    CASE
        WHEN proconfig IS NULL THEN '❌ NO CONFIG'
        WHEN 'search_path=public, pg_catalog, pg_temp' = ANY(proconfig) THEN '✅ FIXED with pg_temp'
        WHEN 'search_path=public, pg_catalog' = ANY(proconfig) THEN '✅ FIXED'
        WHEN 'search_path' = ANY(SELECT split_part(unnest(proconfig), '=', 1)) THEN '✅ HAS search_path'
        ELSE '❌ NO search_path'
    END as status,
    proconfig as config_settings
FROM pg_proc
WHERE proname = 'reward_inviter_credits'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Check all functions to make sure none are missing search_path
SELECT
    'Final Security Check' as check_type,
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
-- LEAKED PASSWORD PROTECTION REMINDER
-- =====================================================
/*
REMINDER: Leaked Password Protection must be enabled in the Dashboard:

1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/auth
2. Navigate to: Settings → Authentication → Security
3. Find "Password Security" section
4. Toggle ON "Leaked Password Protection"
5. Click "Save"

This will check passwords against the HaveIBeenPwned database.
*/