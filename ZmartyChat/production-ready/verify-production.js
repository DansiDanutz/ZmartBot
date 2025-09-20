// Quick verification of production-ready folder
import fs from 'fs';

console.log('🔍 VERIFYING PRODUCTION-READY FOLDER');
console.log('=====================================\n');

const requiredFiles = [
    'index.html',
    'onboarding-complete.js',
    'supabase-client.js',
    'supabase-dual-client.js',
    'onboarding-slides.css',
    'dashboard.html',
    'dashboard.js',
    'dashboard.css',
    'reset-password.html'
];

const checks = {
    filesExist: true,
    htmlUsesCorrectJS: false,
    navigationFunctions: false,
    emailFunctions: false,
    supabaseConfig: false
};

console.log('📋 Checking required files:');
requiredFiles.forEach(file => {
    const path = `./${file}`;
    if (fs.existsSync(path)) {
        const stats = fs.statSync(path);
        console.log(`✅ ${file} (${(stats.size / 1024).toFixed(1)} KB)`);
    } else {
        console.log(`❌ ${file} - MISSING!`);
        checks.filesExist = false;
    }
});

console.log('\n📋 Checking configuration:');

// Check HTML uses correct JS
const indexContent = fs.readFileSync('./index.html', 'utf-8');
if (indexContent.includes('onboarding-complete.js')) {
    console.log('✅ index.html loads onboarding-complete.js');
    checks.htmlUsesCorrectJS = true;
} else {
    console.log('❌ index.html does not load onboarding-complete.js');
}

// Check JavaScript has all functions
const jsContent = fs.readFileSync('./onboarding-complete.js', 'utf-8');

const requiredFunctions = [
    'nextSlide',
    'previousSlide',
    'goToSlide',
    'checkEmailExists',
    'continueWithEmail',
    'simpleRegister',
    'quickLogin',
    'sendPasswordReset',
    'selectTier',
    'completeProfile'
];

console.log('\n📋 Checking functions:');
let allFunctionsFound = true;
requiredFunctions.forEach(func => {
    if (jsContent.includes(`window.${func}`) || jsContent.includes(`function ${func}`)) {
        console.log(`✅ ${func} function exists`);
    } else {
        console.log(`❌ ${func} function missing`);
        allFunctionsFound = false;
    }
});
checks.navigationFunctions = allFunctionsFound;
checks.emailFunctions = allFunctionsFound; // Set emailFunctions check

// Check Supabase configuration
if (jsContent.includes('brainClient') || jsContent.includes('supabase')) {
    console.log('✅ Supabase client configuration found');
    checks.supabaseConfig = true;
}

// Final summary
console.log('\n=====================================');
console.log('📊 VERIFICATION SUMMARY');
console.log('=====================================');

const allChecks = Object.values(checks).every(v => v === true);

if (allChecks) {
    console.log('\n✅ ALL CHECKS PASSED!');
    console.log('📦 Production-ready folder is ready for deployment');
    console.log('\n🚀 Deploy with:');
    console.log('   1. Drag folder to https://app.netlify.com/drop');
    console.log('   OR');
    console.log('   2. netlify deploy --prod --dir=production-ready');
} else {
    console.log('\n⚠️ SOME CHECKS FAILED');
    console.log('Please fix the issues above before deploying');
}

console.log('\n📱 Test locally: http://localhost:8081/production-ready/');
console.log('🌐 Live site: https://memoproapp.netlify.app');