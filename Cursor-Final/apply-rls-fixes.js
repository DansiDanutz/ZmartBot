const { createClient } = require('@supabase/supabase-js');

// ZmartyBrain Supabase credentials
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY || 'YOUR_SERVICE_KEY_HERE';

async function applyRLSFixes() {
    console.log('🔧 Applying RLS Performance Fixes to ZmartyBrain...\n');

    // Note: For RLS policy changes, you need to use the service role key
    // or apply these via the Supabase dashboard SQL editor

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

    const sqlStatements = [
        // Drop existing policies
        `DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;`,
        `DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;`,
        `DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;`,
        `DROP POLICY IF EXISTS "Users can view own credits" ON public.user_credits;`,

        // Recreate optimized policies for profiles
        `CREATE POLICY "Users can view own profile" ON public.profiles
            FOR SELECT
            USING (id = (SELECT auth.uid()));`,

        `CREATE POLICY "Users can insert own profile" ON public.profiles
            FOR INSERT
            WITH CHECK (id = (SELECT auth.uid()));`,

        `CREATE POLICY "Users can update own profile" ON public.profiles
            FOR UPDATE
            USING (id = (SELECT auth.uid()))
            WITH CHECK (id = (SELECT auth.uid()));`,

        // Recreate optimized policy for user_credits
        `CREATE POLICY "Users can view own credits" ON public.user_credits
            FOR SELECT
            USING (user_id = (SELECT auth.uid()));`
    ];

    console.log('⚠️  IMPORTANT: RLS policy changes require service role access.');
    console.log('📋 Please apply the following fixes via Supabase Dashboard:\n');
    console.log('1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql/new');
    console.log('2. Copy and paste the contents of fix-rls-performance.sql');
    console.log('3. Click "Run" to apply the changes\n');

    console.log('The fix changes:');
    console.log('❌ OLD: auth.uid() - re-evaluates for each row');
    console.log('✅ NEW: (SELECT auth.uid()) - evaluates once per query\n');

    console.log('This optimization prevents the auth function from being called');
    console.log('for every row in the result set, significantly improving performance.\n');

    // Test current connection
    try {
        const { data, error } = await supabase
            .from('profiles')
            .select('id')
            .limit(1);

        if (error) {
            console.log('❌ Connection test failed:', error.message);
        } else {
            console.log('✅ Connected to ZmartyBrain database successfully');
            console.log('📝 Please apply the RLS fixes via the dashboard as shown above.');
        }
    } catch (err) {
        console.error('Error:', err.message);
    }
}

applyRLSFixes().catch(console.error);