# Fix Supabase RLS Performance Issues

## Problem
Your Supabase RLS policies are calling `auth.uid()` for every row, causing performance issues.

## Solution
Replace `auth.uid()` with `(SELECT auth.uid())` to evaluate once per query instead of per row.

## Steps to Apply the Fix:

1. **Go to Supabase SQL Editor:**
   https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql/new

2. **Copy and paste this SQL:**

```sql
-- Fix RLS Performance Issues for ZmartyBrain

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view own credits" ON public.user_credits;

-- Recreate optimized policies for profiles table
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT
    USING (id = (SELECT auth.uid()));

CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT
    WITH CHECK (id = (SELECT auth.uid()));

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE
    USING (id = (SELECT auth.uid()))
    WITH CHECK (id = (SELECT auth.uid()));

-- Recreate optimized policy for user_credits table
CREATE POLICY "Users can view own credits" ON public.user_credits
    FOR SELECT
    USING (user_id = (SELECT auth.uid()));
```

3. **Click "Run"** to execute the SQL

## What This Fixes:

### Before (Slow):
- `auth.uid()` - Function called for EVERY row in result set
- Performance degrades as table grows

### After (Fast):
- `(SELECT auth.uid())` - Function called ONCE per query
- Consistent performance regardless of table size

## Verification:
After running the SQL, the linter warnings should disappear and queries will be faster.

## Files Created:
- `fix-rls-performance.sql` - The complete SQL fix
- `rls-fix-instructions.md` - This instruction file