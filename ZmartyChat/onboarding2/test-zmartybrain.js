const { createClient } = require('@supabase/supabase-js');

// ZmartyBrain configuration (where auth happens)
const ZMARTYBRAIN_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const ZMARTYBRAIN_SERVICE_KEY = process.env.ZMARTYBRAIN_SERVICE_KEY;

if (!ZMARTYBRAIN_SERVICE_KEY) {
    console.error('❌ Please set ZMARTYBRAIN_SERVICE_KEY environment variable');
    console.log('You can find it at: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/api');
    process.exit(1);
}

const supabase = createClient(ZMARTYBRAIN_URL, ZMARTYBRAIN_SERVICE_KEY, {
    auth: {
        autoRefreshToken: false,
        persistSession: false
    }
});

async function checkDatabase() {
    console.log('🔍 Checking ZmartyBrain database...\n');

    try {
        // Check if auth.users table is accessible
        const { data: authCheck, error: authError } = await supabase
            .from('auth.users')
            .select('count')
            .limit(1);

        if (authError) {
            console.log('❌ Cannot access auth.users directly (expected):', authError.message);
        } else {
            console.log('✅ auth.users table exists');
        }

        // Check for user_profiles table
        const { data: profilesCheck, error: profilesError } = await supabase
            .from('user_profiles')
            .select('count')
            .limit(1);

        if (profilesError) {
            console.log('❌ user_profiles table error:', profilesError.message);
            console.log('\n⚠️  This table might be missing or have RLS issues');
        } else {
            console.log('✅ user_profiles table exists');
        }

        // Check for any existing users
        const { data: users, error: usersError } = await supabase.auth.admin.listUsers({
            page: 1,
            perPage: 5
        });

        if (usersError) {
            console.log('❌ Cannot list users:', usersError.message);
        } else {
            console.log(`\n📊 Total users in ZmartyBrain: ${users.users.length}`);

            // Check for seme@kryptostack.com
            const semeUser = users.users.find(u => u.email === 'seme@kryptostack.com');
            if (semeUser) {
                console.log('\n⚠️  User seme@kryptostack.com already exists!');
                console.log(`   ID: ${semeUser.id}`);
                console.log(`   Created: ${semeUser.created_at}`);
                console.log(`   Confirmed: ${semeUser.email_confirmed_at ? 'Yes' : 'No'}`);

                // Try to delete the user
                console.log('\n🗑️  Attempting to delete user...');
                const { error: deleteError } = await supabase.auth.admin.deleteUser(semeUser.id);
                if (deleteError) {
                    console.log('❌ Delete failed:', deleteError.message);
                } else {
                    console.log('✅ User deleted successfully');
                }
            } else {
                console.log('✅ User seme@kryptostack.com does not exist');
            }
        }

        // Check database functions
        console.log('\n🔧 Checking database functions...');
        const { data: functions, error: funcError } = await supabase.rpc('get_functions', {});
        if (funcError) {
            // Try alternative query
            const { data: triggers, error: triggerError } = await supabase
                .from('information_schema.triggers')
                .select('trigger_name')
                .eq('trigger_schema', 'public')
                .limit(5);

            if (triggerError) {
                console.log('⚠️  Cannot query triggers (might need different permissions)');
            } else {
                console.log(`✅ Found ${triggers?.length || 0} triggers in public schema`);
            }
        }

        // Test creating a user programmatically
        console.log('\n🧪 Testing user creation...');
        const testEmail = `test_${Date.now()}@example.com`;
        const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
            email: testEmail,
            password: 'TestPassword123!',
            email_confirm: true
        });

        if (createError) {
            console.log('❌ User creation failed:', createError.message);
            console.log('\n⚠️  This is likely the root cause of the registration issue!');
            console.log('   The database might be missing required triggers or functions.');
        } else {
            console.log('✅ Test user created successfully');
            console.log(`   ID: ${newUser.user.id}`);

            // Clean up test user
            await supabase.auth.admin.deleteUser(newUser.user.id);
            console.log('🗑️  Test user cleaned up');
        }

    } catch (error) {
        console.error('\n❌ Unexpected error:', error);
    }
}

checkDatabase().then(() => {
    console.log('\n✨ Database check complete');
    process.exit(0);
}).catch(err => {
    console.error('\n❌ Fatal error:', err);
    process.exit(1);
});