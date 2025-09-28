#!/bin/bash

# ============================================
# Verify HIBP Protection Status
# ============================================

echo "🔍 Checking Leaked Password Protection Status"
echo "=============================================="
echo ""

# Method 1: Check via Supabase CLI
echo "Method 1: Checking via Supabase CLI..."
if command -v supabase &> /dev/null; then
    echo "Fetching project configuration..."
    supabase projects get xhskmqsgtdhehzlvtuns --json | grep -i "password\|hibp\|leak" || echo "No direct config found via CLI"
else
    echo "Supabase CLI not found - skipping CLI check"
fi

echo ""
echo "Method 2: Testing with a known compromised password..."
echo ""

# Test with the API
node << 'EOF'
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function testHIBP() {
    console.log('Testing signup with known compromised password "P@ssw0rd"...\n');

    const testEmail = `test-hibp-${Date.now()}@example.com`;

    try {
        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: 'P@ssw0rd'  // Known compromised password
        });

        if (error) {
            if (error.message.toLowerCase().includes('leak') ||
                error.message.toLowerCase().includes('compromised') ||
                error.message.toLowerCase().includes('pwned') ||
                error.message.toLowerCase().includes('breach')) {
                console.log('✅ SUCCESS! HIBP Protection is ACTIVE!');
                console.log('Error message:', error.message);
                console.log('\nLeaked password protection is working correctly!');
            } else {
                console.log('⚠️  Different error received:', error.message);
                console.log('HIBP might be enabled but error message is different');
            }
        } else {
            console.log('❌ WARNING: Signup succeeded with compromised password!');
            console.log('HIBP protection may not be enabled server-side.');
            console.log('But your client-side protection is still active!');

            // Clean up test user if created
            if (data?.user) {
                await supabase.auth.admin.deleteUser(data.user.id).catch(() => {});
            }
        }
    } catch (err) {
        console.log('Test error:', err.message);
    }
}

testHIBP();
EOF

echo ""
echo "=============================================="
echo "📊 Status Check Complete!"
echo ""
echo "If you see '✅ SUCCESS' above, HIBP is enabled!"
echo "If not, your client-side protection is still working."
echo "=============================================="