#!/usr/bin/env node

/**
 * 🚀 Onboarding Setup Verification Script
 * 
 * This script verifies that all components are properly configured
 * for deployment to Netlify with Supabase integration.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Onboarding Setup...\n');

const checks = [
  {
    name: 'netlify.toml exists',
    check: () => fs.existsSync('netlify.toml'),
    fix: 'Create netlify.toml with proper build configuration'
  },
  {
    name: 'package.json exists',
    check: () => fs.existsSync('package.json'),
    fix: 'Create package.json with build scripts'
  },
  {
    name: 'Supabase client configured',
    check: () => fs.existsSync('src/lib/supabase.js'),
    fix: 'Create src/lib/supabase.js with Supabase client'
  },
  {
    name: 'Build directory exists',
    check: () => fs.existsSync('dist'),
    fix: 'Run npm run build to create dist directory'
  },
  {
    name: 'GitHub Actions workflow',
    check: () => fs.existsSync('.github/workflows/deploy.yml'),
    fix: 'Create .github/workflows/deploy.yml for automatic deployment'
  }
];

let allPassed = true;

checks.forEach(check => {
  const passed = check.check();
  const status = passed ? '✅' : '❌';
  console.log(`${status} ${check.name}`);
  
  if (!passed) {
    console.log(`   Fix: ${check.fix}`);
    allPassed = false;
  }
});

console.log('\n' + '='.repeat(50));

if (allPassed) {
  console.log('🎉 All checks passed! Your onboarding setup is ready for deployment.');
  console.log('\n📋 Next steps:');
  console.log('1. Configure environment variables in Netlify dashboard');
  console.log('2. Push to GitHub to trigger automatic deployment');
  console.log('3. Test your deployed application');
} else {
  console.log('⚠️  Some checks failed. Please fix the issues above before deploying.');
  process.exit(1);
}

console.log('\n🚀 Ready to deploy!');
