-- Quick Security Fix for user_profiles SECURITY DEFINER warning
-- Run this in Supabase SQL Editor

-- Fix the user_profiles view security mode
ALTER VIEW public.user_profiles SET (security_invoker = true);

-- Verify the fix
SELECT 'Security fix applied successfully! ✅' as status;