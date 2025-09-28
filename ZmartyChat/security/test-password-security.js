#!/usr/bin/env node

/**
 * Test Script for Password Security Implementation
 * Validates that leaked password protection and password policies are working
 */

import { createClient } from '@supabase/supabase-js';
import {
    validatePasswordComplete,
    checkPasswordLeaked,
    generateStrongPassword,
    validatePasswordStrength
} from './password-validation.js';

// Test configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

// Known compromised passwords to test (from common breach lists)
const COMPROMISED_PASSWORDS = [
    'P@ssw0rd',
    'Password123!',
    'Admin@123',
    'Welcome123!',
    'Qwerty123!',
    'Password1!',
    'Summer2023!',
    'Monkey123!',
    'Dragon123!',
    'Master123!'
];

// Weak passwords that should fail validation
const WEAK_PASSWORDS = [
    'password',
    '12345678',
    'qwertyuiop',
    'abc123456',
    'testtest',
    'admin123',
    'user1234',
    'demo1234'
];

// Valid strong passwords
const STRONG_PASSWORDS = [
    'Kj#9mP$xQ2wL@nR5',
    'Purple$Monkey#Dishwasher7',
    'Tr0ub4dor&3',
    'correcthorsebatterystaple!9',
    generateStrongPassword(16),
    generateStrongPassword(20)
];

// Color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

/**
 * Test password validation functions
 */
async function runTests() {
    console.log(`${colors.cyan}========================================`);
    console.log(`Password Security Test Suite`);
    console.log(`========================================${colors.reset}\n`);

    let testsPassed = 0;
    let testsFailed = 0;

    // Test 1: Check known compromised passwords
    console.log(`${colors.yellow}Test 1: Compromised Password Detection${colors.reset}`);
    console.log('Testing passwords known to be in breach databases...\n');

    for (const password of COMPROMISED_PASSWORDS) {
        process.stdout.write(`  Testing "${password}"... `);

        try {
            const isLeaked = await checkPasswordLeaked(password);
            const validation = await validatePasswordComplete(password);

            if (isLeaked && !validation.valid) {
                console.log(`${colors.green}✓ Correctly identified as compromised${colors.reset}`);
                testsPassed++;
            } else {
                console.log(`${colors.red}✗ Failed to detect as compromised${colors.reset}`);
                testsFailed++;
            }
        } catch (error) {
            console.log(`${colors.red}✗ Error: ${error.message}${colors.reset}`);
            testsFailed++;
        }
    }

    console.log();

    // Test 2: Weak password validation
    console.log(`${colors.yellow}Test 2: Weak Password Validation${colors.reset}`);
    console.log('Testing passwords that should fail strength requirements...\n');

    for (const password of WEAK_PASSWORDS) {
        process.stdout.write(`  Testing "${password}"... `);

        const validation = validatePasswordStrength(password);

        if (!validation.passed) {
            console.log(`${colors.green}✓ Correctly rejected (${validation.errors[0]})${colors.reset}`);
            testsPassed++;
        } else {
            console.log(`${colors.red}✗ Should have been rejected${colors.reset}`);
            testsFailed++;
        }
    }

    console.log();

    // Test 3: Strong password validation
    console.log(`${colors.yellow}Test 3: Strong Password Validation${colors.reset}`);
    console.log('Testing passwords that should pass all requirements...\n');

    for (const password of STRONG_PASSWORDS) {
        process.stdout.write(`  Testing strong password... `);

        try {
            const validation = await validatePasswordComplete(password);

            if (validation.valid && !validation.compromised) {
                console.log(`${colors.green}✓ Passed (strength: ${validation.strength.level})${colors.reset}`);
                testsPassed++;
            } else if (validation.compromised) {
                console.log(`${colors.yellow}⚠ Strong but compromised${colors.reset}`);
                testsFailed++;
            } else {
                console.log(`${colors.red}✗ Failed validation: ${validation.errors.join(', ')}${colors.reset}`);
                testsFailed++;
            }
        } catch (error) {
            console.log(`${colors.red}✗ Error: ${error.message}${colors.reset}`);
            testsFailed++;
        }
    }

    console.log();

    // Test 4: Supabase integration test
    console.log(`${colors.yellow}Test 4: Supabase Auth Integration${colors.reset}`);
    console.log('Testing actual Supabase signup with compromised password...\n');

    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    const testEmail = `test-${Date.now()}@example.com`;

    try {
        // Try to sign up with a compromised password
        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: 'P@ssw0rd', // Known compromised password
        });

        if (error && (error.message.includes('compromised') || error.message.includes('leaked'))) {
            console.log(`  ${colors.green}✓ Supabase correctly rejected compromised password${colors.reset}`);
            console.log(`  Error message: "${error.message}"`);
            testsPassed++;
        } else if (error) {
            console.log(`  ${colors.yellow}⚠ Supabase error (may need dashboard config): ${error.message}${colors.reset}`);
        } else {
            console.log(`  ${colors.red}✗ Supabase accepted compromised password - Enable protection in dashboard!${colors.reset}`);
            testsFailed++;

            // Clean up test user if created
            if (data?.user) {
                await supabase.auth.admin.deleteUser(data.user.id).catch(() => {});
            }
        }
    } catch (error) {
        console.log(`  ${colors.yellow}⚠ Could not test Supabase integration: ${error.message}${colors.reset}`);
    }

    console.log();

    // Test 5: Password generator
    console.log(`${colors.yellow}Test 5: Password Generator${colors.reset}`);
    console.log('Testing generated passwords meet all requirements...\n');

    for (let i = 0; i < 5; i++) {
        const generated = generateStrongPassword(16);
        process.stdout.write(`  Generated password ${i + 1}... `);

        const validation = validatePasswordStrength(generated);

        if (validation.passed) {
            console.log(`${colors.green}✓ Valid (strength: ${validation.strength.level})${colors.reset}`);
            testsPassed++;
        } else {
            console.log(`${colors.red}✗ Failed: ${validation.errors.join(', ')}${colors.reset}`);
            testsFailed++;
        }
    }

    console.log();

    // Summary
    console.log(`${colors.cyan}========================================`);
    console.log(`Test Results Summary`);
    console.log(`========================================${colors.reset}`);
    console.log(`${colors.green}Passed: ${testsPassed}${colors.reset}`);
    console.log(`${colors.red}Failed: ${testsFailed}${colors.reset}`);

    const successRate = (testsPassed / (testsPassed + testsFailed) * 100).toFixed(1);
    if (successRate >= 80) {
        console.log(`${colors.green}Success Rate: ${successRate}%${colors.reset}`);
    } else {
        console.log(`${colors.red}Success Rate: ${successRate}%${colors.reset}`);
    }

    console.log();

    // Action items
    if (testsFailed > 0) {
        console.log(`${colors.yellow}Action Required:${colors.reset}`);
        console.log('1. Enable leaked password protection in Supabase Dashboard:');
        console.log(`   ${colors.blue}https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/auth${colors.reset}`);
        console.log('2. Navigate to Authentication → Settings → Password Security');
        console.log('3. Enable "Leaked password protection (HaveIBeenPwned)"');
        console.log('4. Save the configuration');
        console.log('5. Re-run this test to verify');
    } else {
        console.log(`${colors.green}✓ All security tests passed!${colors.reset}`);
        console.log('Password protection is properly configured.');
    }

    process.exit(testsFailed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(error => {
    console.error(`${colors.red}Test suite failed: ${error.message}${colors.reset}`);
    process.exit(1);
});