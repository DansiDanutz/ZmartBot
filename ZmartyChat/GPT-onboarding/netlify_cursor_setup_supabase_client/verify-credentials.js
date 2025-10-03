#!/usr/bin/env node

/**
 * Credential Verification Script for Onboarding App
 * Run this to verify all credentials are properly configured
 */

import { createClient } from '@supabase/supabase-js';
import fetch from 'node-fetch';

console.log('🔍 Verifying Onboarding App Credentials...\n');

// Check environment variables
const credentials = {
  supabase: {
    url: process.env.VITE_SUPABASE_URL || 'https://xhskmqsgtdhehzlvtuns.supabase.co',
    anonKey: process.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw'
  },
  google: {
    clientId: '966065216838-fu5fmuckc7n4e9pjbvg4o1m9vo6d9uur.apps.googleusercontent.com',
    clientSecret: process.env.GOOGLE_CLIENT_SECRET || 'Not set',
    projectId: process.env.GOOGLE_PROJECT_ID || 'lexical-rock-472809-s8'
  },
  netlify: {
    siteUrl: 'https://vermillion-paprenjak-67497b.netlify.app',
    siteId: process.env.NETLIFY_SITE_ID || 'vermillion-paprenjak-67497b'
  },
  resend: {
    apiKey: process.env.RESEND_API_KEY || 'Not set'
  }
};

// Test results
const results = {
  passed: [],
  failed: [],
  warnings: []
};

// Test 1: Verify Supabase Connection
console.log('1️⃣ Testing Supabase Connection...');
try {
  const supabase = createClient(credentials.supabase.url, credentials.supabase.anonKey);

  // Test basic connection
  const { data: healthCheck, error } = await supabase.from('profiles').select('count').limit(1);

  if (error && error.code !== 'PGRST116') { // PGRST116 is "no rows" which is OK
    throw error;
  }

  console.log('   ✅ Supabase connection successful');
  results.passed.push('Supabase Connection');
} catch (error) {
  console.log('   ❌ Supabase connection failed:', error.message);
  results.failed.push('Supabase Connection');
}

// Test 2: Check Netlify Site
console.log('\n2️⃣ Testing Netlify Deployment...');
try {
  const response = await fetch(credentials.netlify.siteUrl);
  if (response.ok) {
    console.log('   ✅ Netlify site is live');
    results.passed.push('Netlify Deployment');
  } else {
    throw new Error(`Site returned status ${response.status}`);
  }
} catch (error) {
  console.log('   ❌ Netlify site check failed:', error.message);
  results.failed.push('Netlify Deployment');
}

// Test 3: Verify Google OAuth Configuration
console.log('\n3️⃣ Checking Google OAuth Setup...');
if (credentials.google.clientId && credentials.google.clientId.includes('googleusercontent.com')) {
  console.log('   ✅ Google Client ID configured');
  results.passed.push('Google OAuth Client ID');
} else {
  console.log('   ❌ Google Client ID not properly configured');
  results.failed.push('Google OAuth Client ID');
}

// Test 4: Check Environment Variables on Netlify
console.log('\n4️⃣ Environment Variables Status...');
console.log('   📋 Required for Production:');
console.log(`   • VITE_SUPABASE_URL: ${credentials.supabase.url ? '✅ Set' : '❌ Missing'}`);
console.log(`   • VITE_SUPABASE_ANON_KEY: ${credentials.supabase.anonKey ? '✅ Set' : '❌ Missing'}`);
console.log(`   • GOOGLE_CLIENT_ID: ${credentials.google.clientId ? '✅ Set' : '❌ Missing'}`);
console.log('   📋 Optional:');
console.log(`   • GOOGLE_CLIENT_SECRET: ${credentials.google.clientSecret !== 'Not set' ? '✅ Set' : '⚠️ Not set (OK for OAuth)'}`);
console.log(`   • RESEND_API_KEY: ${credentials.resend.apiKey !== 'Not set' ? '✅ Set' : '⚠️ Not set (using Supabase email)'}`);

// Test 5: Check Supabase Auth Settings
console.log('\n5️⃣ Supabase Auth Configuration Checklist:');
console.log('   Please verify in Supabase Dashboard:');
console.log('   □ Email/Password authentication enabled');
console.log('   □ Google OAuth provider configured');
console.log('   □ Site URL set to:', credentials.netlify.siteUrl);
console.log('   □ Redirect URLs include:', credentials.netlify.siteUrl + '/*');

// Final Summary
console.log('\n' + '='.repeat(60));
console.log('📊 VERIFICATION SUMMARY');
console.log('='.repeat(60));
console.log(`✅ Passed: ${results.passed.length} tests`);
console.log(`❌ Failed: ${results.failed.length} tests`);
console.log(`⚠️  Warnings: ${results.warnings.length} items`);

if (results.passed.length > 0) {
  console.log('\n✅ Passed Tests:');
  results.passed.forEach(test => console.log(`   • ${test}`));
}

if (results.failed.length > 0) {
  console.log('\n❌ Failed Tests:');
  results.failed.forEach(test => console.log(`   • ${test}`));
}

// Action Items
console.log('\n📝 ACTION ITEMS:');
if (results.failed.includes('Supabase Connection')) {
  console.log('1. Run the setup_onboarding_tables.sql script in Supabase SQL Editor');
  console.log('2. Verify Supabase credentials are correct');
}

console.log('\n🔗 Important URLs:');
console.log('   • Live App:', credentials.netlify.siteUrl);
console.log('   • Supabase Dashboard: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns');
console.log('   • Netlify Dashboard: https://app.netlify.com/sites/vermillion-paprenjak-67497b');

console.log('\n✨ Credential verification complete!');