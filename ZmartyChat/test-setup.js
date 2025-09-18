// ZmartyChat Setup Test Script
import { createClient } from '@supabase/supabase-js';
import Stripe from 'stripe';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

console.log('🧪 ZmartyChat Setup Test');
console.log('========================\n');

let testsPass = true;

// Test 1: Environment Variables
console.log('1️⃣  Testing Environment Variables...');
const requiredEnvVars = [
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY',
    'JWT_SECRET'
];

const missingVars = [];
for (const varName of requiredEnvVars) {
    if (!process.env[varName] || process.env[varName].includes('your-')) {
        missingVars.push(varName);
        console.log(`   ❌ ${varName}: Missing or using default`);
    } else {
        console.log(`   ✅ ${varName}: Configured`);
    }
}

if (missingVars.length > 0) {
    console.log('\n⚠️  Please configure missing variables in .env file');
    testsPass = false;
} else {
    console.log('   ✅ All required environment variables configured\n');
}

// Test 2: Supabase Connection
console.log('2️⃣  Testing Supabase Connection...');
if (process.env.SUPABASE_URL && !process.env.SUPABASE_URL.includes('your-project')) {
    const supabase = createClient(
        process.env.SUPABASE_URL,
        process.env.SUPABASE_ANON_KEY
    );

    try {
        // Try to query ZmartyChat users table
        const { data, error } = await supabase
            .from('zmartychat_users')
            .select('count')
            .limit(1);

        if (error) {
            if (error.message.includes('relation "public.zmartychat_users" does not exist')) {
                console.log('   ⚠️  Connected but ZmartyChat tables not created yet');
                console.log('      Run the database setup first');
            } else {
                console.log('   ❌ Connection error:', error.message);
                testsPass = false;
            }
        } else {
            console.log('   ✅ Supabase connected and ZmartyChat tables exist');
        }
    } catch (err) {
        console.log('   ❌ Failed to connect:', err.message);
        testsPass = false;
    }
} else {
    console.log('   ⏭️  Skipping - Supabase not configured');
}

console.log('');

// Test 3: Stripe Configuration (Optional)
console.log('3️⃣  Testing Stripe Configuration...');
if (process.env.STRIPE_SECRET_KEY && !process.env.STRIPE_SECRET_KEY.includes('your_secret')) {
    try {
        const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
        const account = await stripe.accounts.retrieve();
        console.log('   ✅ Stripe connected (Test mode)');
    } catch (err) {
        if (err.message.includes('No such account')) {
            // Using test key
            console.log('   ✅ Stripe test key configured');
        } else {
            console.log('   ⚠️  Stripe error (non-critical):', err.message);
        }
    }
} else {
    console.log('   ⏭️  Skipping - Stripe not configured (optional)');
}

console.log('');

// Test 4: File Structure
console.log('4️⃣  Testing File Structure...');
const requiredFiles = [
    'src/main-integration.js',
    'src/supabase-client.js',
    'src/credit-manager.js',
    'src/zmarty-ai-agent.js',
    'database/supabase_schema.sql',
    'package.json',
    'index.html'
];

const missingFiles = [];
for (const file of requiredFiles) {
    try {
        const fs = await import('fs');
        if (fs.existsSync(file)) {
            console.log(`   ✅ ${file}`);
        } else {
            console.log(`   ❌ ${file} - Missing`);
            missingFiles.push(file);
        }
    } catch (err) {
        console.log(`   ❌ ${file} - Error checking`);
        missingFiles.push(file);
    }
}

if (missingFiles.length > 0) {
    testsPass = false;
}

console.log('');

// Test 5: Port Availability
console.log('5️⃣  Testing Port Availability...');
const port = process.env.PORT || 3001;
const net = await import('net');

const server = net.createServer();
server.listen(port, '127.0.0.1');

server.on('listening', () => {
    console.log(`   ✅ Port ${port} is available`);
    server.close();
});

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.log(`   ⚠️  Port ${port} is in use (may be running already)`);
    } else {
        console.log(`   ❌ Port error:`, err.message);
    }
    testsPass = false;
});

// Wait for port test to complete
await new Promise(resolve => setTimeout(resolve, 1000));

console.log('\n========================================\n');

// Final Summary
if (testsPass) {
    console.log('✅ All tests passed! Your system is ready.');
    console.log('\n📝 Next Steps:');
    console.log('1. If Supabase tables don\'t exist, run: npm run db:migrate');
    console.log('2. Start the server: npm run dev');
    console.log('3. Open browser: http://localhost:8080');
} else {
    console.log('⚠️  Some tests failed. Please review the issues above.');
    console.log('\n📝 Required Actions:');

    if (missingVars.length > 0) {
        console.log('1. Configure missing environment variables in .env');
    }
    if (missingFiles.length > 0) {
        console.log('2. Ensure all source files are present');
    }
    console.log('\nRun this test again after fixing: node test-setup.js');
}

process.exit(testsPass ? 0 : 1);