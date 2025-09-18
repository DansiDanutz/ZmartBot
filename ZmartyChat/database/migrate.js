// Database Migration Script for ZmartyChat
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Supabase client with service key for admin operations
const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY,
    {
        auth: {
            persistSession: false
        }
    }
);

console.log('🚀 ZmartyChat Database Migration Tool');
console.log('=====================================\n');

async function runMigration() {
    try {
        // Check connection
        console.log('📡 Checking Supabase connection...');
        const { data: test, error: testError } = await supabase
            .from('users')
            .select('count');

        if (testError && !testError.message.includes('relation "public.users" does not exist')) {
            console.error('❌ Connection failed:', testError.message);
            console.log('\nPlease check your SUPABASE_URL and SUPABASE_ANON_KEY in .env');
            process.exit(1);
        }

        console.log('✅ Connected to Supabase\n');

        // Read SQL schema file
        console.log('📄 Reading schema file...');
        const schemaPath = path.join(__dirname, 'supabase_schema.sql');

        if (!fs.existsSync(schemaPath)) {
            console.error('❌ Schema file not found:', schemaPath);
            process.exit(1);
        }

        const schema = fs.readFileSync(schemaPath, 'utf8');
        console.log('✅ Schema file loaded\n');

        // Split SQL into individual statements
        const statements = schema
            .split(';')
            .map(s => s.trim())
            .filter(s => s.length > 0 && !s.startsWith('--'));

        console.log(`📝 Found ${statements.length} SQL statements to execute\n`);

        // Execute each statement
        console.log('🔨 Running migration...\n');

        let successCount = 0;
        let errorCount = 0;
        const errors = [];

        for (let i = 0; i < statements.length; i++) {
            const statement = statements[i] + ';';

            // Extract table/function name for logging
            let objectName = 'Statement ' + (i + 1);
            if (statement.includes('CREATE TABLE')) {
                const match = statement.match(/CREATE TABLE (?:IF NOT EXISTS )?([\w.]+)/i);
                if (match) objectName = `Table: ${match[1]}`;
            } else if (statement.includes('CREATE FUNCTION')) {
                const match = statement.match(/CREATE (?:OR REPLACE )?FUNCTION ([\w.]+)/i);
                if (match) objectName = `Function: ${match[1]}`;
            } else if (statement.includes('CREATE POLICY')) {
                const match = statement.match(/CREATE POLICY "?([^"]+)"?/i);
                if (match) objectName = `Policy: ${match[1]}`;
            } else if (statement.includes('ALTER TABLE')) {
                const match = statement.match(/ALTER TABLE ([\w.]+)/i);
                if (match) objectName = `Alter: ${match[1]}`;
            }

            process.stdout.write(`  ${objectName}... `);

            try {
                // Use raw SQL execution through Supabase
                const { data, error } = await supabase.rpc('exec_sql', {
                    sql_query: statement
                }).catch(async (err) => {
                    // If exec_sql doesn't exist, we need to run the migration differently
                    // This is a fallback - you'll need to run the SQL directly in Supabase SQL editor
                    return { data: null, error: err };
                });

                if (error) {
                    throw error;
                }

                console.log('✅');
                successCount++;
            } catch (error) {
                console.log('❌');
                errorCount++;
                errors.push({
                    object: objectName,
                    error: error.message
                });

                // Continue with other statements even if one fails
                // (some might already exist)
            }
        }

        console.log('\n=====================================');
        console.log(`Migration Results:`);
        console.log(`  ✅ Success: ${successCount} statements`);
        console.log(`  ❌ Errors: ${errorCount} statements`);

        if (errors.length > 0) {
            console.log('\n⚠️  Errors encountered:');
            errors.forEach(e => {
                console.log(`  - ${e.object}: ${e.error}`);
            });

            console.log('\n💡 Note: Some errors are expected if tables/functions already exist.');
            console.log('   If these are "already exists" errors, your database is likely set up correctly.');
        }

        // Test core tables
        console.log('\n🔍 Verifying core tables...\n');
        const coreTables = [
            'users',
            'credit_transactions',
            'user_categories',
            'user_transcripts',
            'conversation_messages',
            'user_insights',
            'addiction_metrics',
            'subscription_plans',
            'user_subscriptions'
        ];

        let tablesOk = true;
        for (const table of coreTables) {
            process.stdout.write(`  Checking ${table}... `);
            const { error } = await supabase
                .from(table)
                .select('count')
                .limit(1);

            if (error) {
                console.log('❌ Not found');
                tablesOk = false;
            } else {
                console.log('✅ OK');
            }
        }

        if (!tablesOk) {
            console.log('\n⚠️  Some tables are missing.');
            console.log('Please run the migration SQL directly in Supabase SQL Editor:');
            console.log('1. Go to your Supabase project');
            console.log('2. Navigate to SQL Editor');
            console.log('3. Copy and paste the contents of database/supabase_schema.sql');
            console.log('4. Click "Run"');
        } else {
            console.log('\n✅ All core tables verified!');

            // Insert initial data
            console.log('\n📦 Setting up initial data...\n');

            // Check if subscription plans exist
            const { data: plans } = await supabase
                .from('subscription_plans')
                .select('id');

            if (!plans || plans.length === 0) {
                console.log('  Creating subscription plans...');
                const { error: planError } = await supabase
                    .from('subscription_plans')
                    .insert([
                        {
                            plan_name: 'Free',
                            tier: 'free',
                            price_monthly: 0,
                            price_yearly: 0,
                            monthly_credits: 100,
                            features: ['Basic chat', 'Market data', 'Limited analysis']
                        },
                        {
                            plan_name: 'Basic',
                            tier: 'basic',
                            price_monthly: 9.99,
                            price_yearly: 99.99,
                            monthly_credits: 1000,
                            features: ['Everything in Free', 'Technical analysis', 'Basic AI predictions', 'Email support']
                        },
                        {
                            plan_name: 'Pro',
                            tier: 'pro',
                            price_monthly: 29.99,
                            price_yearly: 299.99,
                            monthly_credits: 5000,
                            features: ['Everything in Basic', 'Advanced AI features', 'Priority data', 'Custom alerts', 'API access']
                        },
                        {
                            plan_name: 'Premium',
                            tier: 'premium',
                            price_monthly: 99.99,
                            price_yearly: 999.99,
                            monthly_credits: 20000,
                            features: ['Everything in Pro', 'Unlimited AI queries', 'All agents', 'White-glove support', 'Custom models']
                        }
                    ]);

                if (planError) {
                    console.log('  ❌ Error creating plans:', planError.message);
                } else {
                    console.log('  ✅ Subscription plans created');
                }
            } else {
                console.log('  ✅ Subscription plans already exist');
            }

            console.log('\n🎉 Database migration completed successfully!');
            console.log('\n✨ Your ZmartyChat database is ready to use.');
        }

    } catch (error) {
        console.error('\n❌ Migration failed:', error.message);
        console.log('\n💡 Troubleshooting tips:');
        console.log('1. Check your SUPABASE_URL and keys in .env');
        console.log('2. Ensure your Supabase project is active');
        console.log('3. Try running the SQL directly in Supabase SQL Editor');
        process.exit(1);
    }
}

// Add helper function if exec_sql doesn't exist
async function createExecSqlFunction() {
    const createFunction = `
        CREATE OR REPLACE FUNCTION exec_sql(sql_query text)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
            EXECUTE sql_query;
        END;
        $$;
    `;

    console.log('\n📌 Note: For security reasons, you may need to run the migration SQL directly in Supabase.');
    console.log('   The exec_sql function is not recommended for production use.\n');
}

// Run the migration
runMigration().then(() => {
    process.exit(0);
}).catch((error) => {
    console.error('Unexpected error:', error);
    process.exit(1);
});