-- ============================================
-- FIX: Add missing columns first
-- ============================================

-- Step 1: Check what columns exist in user_profiles
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Step 2: Add missing columns one by one
DO $$
BEGIN
    -- Add email column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'email'
    ) THEN
        ALTER TABLE public.user_profiles ADD COLUMN email TEXT;
        RAISE NOTICE 'Added email column';
    END IF;

    -- Add full_name column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'full_name'
    ) THEN
        ALTER TABLE public.user_profiles ADD COLUMN full_name TEXT;
        RAISE NOTICE 'Added full_name column';
    END IF;

    -- Add country column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'country'
    ) THEN
        ALTER TABLE public.user_profiles ADD COLUMN country TEXT;
        RAISE NOTICE 'Added country column';
    END IF;

    -- Add tier column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'tier'
    ) THEN
        ALTER TABLE public.user_profiles ADD COLUMN tier TEXT DEFAULT 'free';
        RAISE NOTICE 'Added tier column';
    END IF;

    -- Add credits column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'credits'
    ) THEN
        ALTER TABLE public.user_profiles ADD COLUMN credits INTEGER DEFAULT 100;
        RAISE NOTICE 'Added credits column';
    END IF;

    -- Add created_at column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE public.user_profiles ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Added created_at column';
    END IF;
END $$;

-- Step 3: Now check columns again
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Step 4: Add constraints only after columns exist
DO $$
BEGIN
    -- Add unique constraint on email only if column exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_profiles'
        AND column_name = 'email'
    ) AND NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_profiles_email_key'
    ) THEN
        ALTER TABLE public.user_profiles
        ADD CONSTRAINT user_profiles_email_key UNIQUE (email);
        RAISE NOTICE 'Added unique constraint on email';
    END IF;
END $$;

-- Step 5: Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Step 6: Create policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Step 7: Final verification
SELECT
    'Table Structure Fixed' as status,
    COUNT(*) as column_count,
    array_agg(column_name ORDER BY ordinal_position) as columns
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'user_profiles';