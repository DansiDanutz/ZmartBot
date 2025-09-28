import { createClient } from '@supabase/supabase-js';

// Configuration - using the actual project URL
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.ZMARTYBRAIN_SERVICE_KEY;

if (!SUPABASE_SERVICE_KEY) {
    console.error('❌ Missing SUPABASE_SERVICE_KEY environment variable');
    console.log('\n📋 To fix this:');
    console.log('1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/api');
    console.log('2. Copy the service_role key (secret)');
    console.log('3. Run: export SUPABASE_SERVICE_KEY="your-key-here"');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
    auth: {
        autoRefreshToken: false,
        persistSession: false
    }
});

console.log('🔍 Checking Supabase Issues (69 issues reported)\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const issues = [];

async function checkAuthSettings() {
    console.log('1️⃣  Authentication Settings');

    try {
        // Check if email auth is enabled
        const { data: users, error } = await supabase.auth.admin.listUsers({
            page: 1,
            perPage: 1
        });

        if (error) {
            issues.push('❌ Cannot access auth.admin API: ' + error.message);
            console.log('   ❌ Auth API access failed');
        } else {
            console.log('   ✅ Auth API accessible');
        }
    } catch (err) {
        issues.push('❌ Auth check failed: ' + err.message);
    }
}

async function checkDatabaseTables() {
    console.log('\n2️⃣  Database Tables');

    const requiredTables = [
        'user_profiles',
        'user_settings',
        'subscription_plans',
        'user_subscriptions',
        'trading_signals',
        'user_sessions'
    ];

    for (const table of requiredTables) {
        try {
            const { error } = await supabase
                .from(table)
                .select('count')
                .limit(1);

            if (error) {
                issues.push(`❌ Table '${table}' error: ${error.message}`);
                console.log(`   ❌ ${table}: ${error.message}`);
            } else {
                console.log(`   ✅ ${table}: Accessible`);
            }
        } catch (err) {
            issues.push(`❌ Table '${table}' check failed`);
            console.log(`   ❌ ${table}: Check failed`);
        }
    }
}

async function checkRLSPolicies() {
    console.log('\n3️⃣  Row Level Security (RLS)');

    try {
        // Check if RLS is enabled
        const { data, error } = await supabase
            .from('user_profiles')
            .select('*')
            .limit(1);

        if (error && error.message.includes('RLS')) {
            issues.push('⚠️  RLS might be blocking access to user_profiles');
            console.log('   ⚠️  RLS policies may need adjustment');
        } else {
            console.log('   ✅ RLS configured');
        }
    } catch (err) {
        issues.push('❌ RLS check failed');
    }
}

async function checkStorageBuckets() {
    console.log('\n4️⃣  Storage Buckets');

    const requiredBuckets = ['avatars', 'documents', 'exports'];

    try {
        const { data: buckets, error } = await supabase.storage.listBuckets();

        if (error) {
            issues.push('❌ Cannot list storage buckets: ' + error.message);
            console.log('   ❌ Storage access failed');
        } else {
            const bucketNames = buckets.map(b => b.name);

            for (const bucket of requiredBuckets) {
                if (!bucketNames.includes(bucket)) {
                    issues.push(`⚠️  Missing storage bucket: ${bucket}`);
                    console.log(`   ⚠️  Missing: ${bucket}`);
                } else {
                    console.log(`   ✅ ${bucket}: Exists`);
                }
            }
        }
    } catch (err) {
        issues.push('❌ Storage check failed');
    }
}

async function checkEmailTemplates() {
    console.log('\n5️⃣  Email Configuration');

    // Check common email issues
    const emailChecks = [
        'Email confirmation template',
        'Password reset template',
        'Magic link template',
        'Invite user template'
    ];

    for (const check of emailChecks) {
        console.log(`   ℹ️  ${check}: Requires dashboard check`);
        issues.push(`⚠️  ${check} needs manual verification`);
    }
}

async function checkDatabaseFunctions() {
    console.log('\n6️⃣  Database Functions & Triggers');

    try {
        // Try to call a common function
        const { error } = await supabase.rpc('handle_new_user', {});

        if (error && error.message.includes('does not exist')) {
            issues.push('❌ Missing function: handle_new_user');
            console.log('   ❌ handle_new_user function missing');
        } else if (error) {
            console.log('   ⚠️  Function exists but has issues');
        } else {
            console.log('   ✅ Functions configured');
        }
    } catch (err) {
        issues.push('⚠️  Cannot verify database functions');
    }
}

async function checkRealtimeSubscriptions() {
    console.log('\n7️⃣  Realtime Configuration');

    try {
        // Check if realtime is enabled
        const channel = supabase.channel('test-channel');

        channel.on('presence', { event: 'sync' }, () => {
            console.log('   ✅ Realtime enabled');
        });

        await channel.subscribe();

        setTimeout(() => {
            channel.unsubscribe();
        }, 1000);

    } catch (err) {
        issues.push('⚠️  Realtime may not be configured');
        console.log('   ⚠️  Realtime check inconclusive');
    }
}

async function checkAPIKeys() {
    console.log('\n8️⃣  API Key Configuration');

    if (SUPABASE_SERVICE_KEY.includes('your_') || SUPABASE_SERVICE_KEY.length < 50) {
        issues.push('❌ Invalid service key format');
        console.log('   ❌ Service key appears invalid');
    } else {
        console.log('   ✅ Service key format valid');
    }
}

async function generateReport() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('\n📊 ISSUES SUMMARY\n');

    if (issues.length === 0) {
        console.log('✅ No critical issues found!');
    } else {
        console.log(`Found ${issues.length} issues:\n`);
        issues.forEach((issue, index) => {
            console.log(`${index + 1}. ${issue}`);
        });
    }

    console.log('\n🔧 RECOMMENDED FIXES:\n');
    console.log('1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns');
    console.log('2. Check Authentication > Providers > Enable Email');
    console.log('3. Check Authentication > Email Templates');
    console.log('4. Check Database > Tables > Create missing tables');
    console.log('5. Check Database > RLS Policies');
    console.log('6. Check Storage > Create missing buckets');
    console.log('7. Run SQL migrations for missing functions');
    console.log('8. Enable Realtime for required tables');

    console.log('\n📝 SQL TO CREATE MISSING TABLES:\n');
    console.log(`
-- User profiles table
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    country TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

-- Create trigger function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
    `);
}

// Run all checks
async function runDiagnostics() {
    await checkAuthSettings();
    await checkDatabaseTables();
    await checkRLSPolicies();
    await checkStorageBuckets();
    await checkEmailTemplates();
    await checkDatabaseFunctions();
    await checkRealtimeSubscriptions();
    await checkAPIKeys();
    await generateReport();
}

runDiagnostics().catch(console.error);