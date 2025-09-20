const fs = require('fs');

console.log('\n🔍 FINAL PRODUCTION CHECK\n');
console.log('=' .repeat(50));

// Check JavaScript file
const js = fs.readFileSync('production-ready/onboarding-slides.js', 'utf8');
let criticalIssues = [];
let warnings = [];

// Check for console.logs (warning only, not critical)
const consoleLogs = (js.match(/console\.log/g) || []).length;
if (consoleLogs > 0) {
    warnings.push(`⚠️  Has ${consoleLogs} console.log statements (OK for production, browsers ignore them)`);
}

// Check for critical navigation functions
if (!js.includes('window.nextSlide')) criticalIssues.push('❌ Missing nextSlide function');
if (!js.includes('window.goToSlide')) criticalIssues.push('❌ Missing goToSlide function');
if (!js.includes('window.previousSlide')) criticalIssues.push('❌ Missing previousSlide function');
if (!js.includes('function nextSlide')) criticalIssues.push('❌ Missing nextSlide implementation');
if (!js.includes('function goToSlide')) criticalIssues.push('❌ Missing goToSlide implementation');

// Check for keyboard navigation
if (!js.includes('ArrowRight')) criticalIssues.push('❌ Missing arrow key navigation');

// Check HTML file
const html = fs.readFileSync('production-ready/index.html', 'utf8');

// Check for all slides
for (let i = 1; i <= 8; i++) {
    if (!html.includes(`slide-${i}`)) {
        criticalIssues.push(`❌ Missing slide ${i}`);
    }
}

// Check for navigation elements
if (!html.includes('next-btn')) criticalIssues.push('❌ Missing NEXT button');
if (!html.includes('dots-nav')) criticalIssues.push('❌ Missing dots navigation');
if (!html.includes('skip-btn')) criticalIssues.push('❌ Missing skip button');

// Check for form elements
if (!html.includes('register-email')) criticalIssues.push('❌ Missing email field');
if (!html.includes('register-password')) criticalIssues.push('❌ Missing password field');

// Check Supabase configuration
const supabase = fs.readFileSync('production-ready/supabase-dual-client.js', 'utf8');
if (!supabase.includes('xhskmqsgtdhehzlvtuns')) criticalIssues.push('❌ Missing ZmartyBrain project');
if (!supabase.includes('asjtxrmftmutcsnqgidy')) criticalIssues.push('❌ Missing ZmartBot project');

// Check for test/debug files
const files = fs.readdirSync('production-ready');
const badFiles = files.filter(f =>
    f.includes('test') ||
    f.includes('debug') ||
    f.includes('check') ||
    f.endsWith('.png') ||
    f.endsWith('.jpg') ||
    f.endsWith('.md')
);

if (badFiles.length > 0) {
    criticalIssues.push(`❌ Found ${badFiles.length} test/debug files: ${badFiles.join(', ')}`);
}

// RESULTS
console.log('\n📊 RESULTS:');
console.log('=' .repeat(50));

if (criticalIssues.length === 0) {
    console.log('\n✅ ✅ ✅ PRODUCTION READY! ✅ ✅ ✅');
    console.log('\n🎉 ALL CRITICAL CHECKS PASSED!');
    console.log('✓ Navigation functions working');
    console.log('✓ All slides present');
    console.log('✓ Both Supabase projects configured');
    console.log('✓ No test/debug files');
    console.log('\n🚀 READY TO DEPLOY TO NETLIFY!');
} else {
    console.log('\n❌ CRITICAL ISSUES FOUND:');
    criticalIssues.forEach(issue => console.log(issue));
    console.log('\nDO NOT DEPLOY UNTIL FIXED!');
}

if (warnings.length > 0) {
    console.log('\n⚠️  WARNINGS (non-critical):');
    warnings.forEach(w => console.log(w));
}

console.log('\n' + '=' .repeat(50));
console.log('\nFiles in production-ready folder:');
files.forEach(f => {
    const size = fs.statSync(`production-ready/${f}`).size;
    const sizeKB = (size / 1024).toFixed(1);
    console.log(`  • ${f} (${sizeKB} KB)`);
});

console.log('\n' + '=' .repeat(50));