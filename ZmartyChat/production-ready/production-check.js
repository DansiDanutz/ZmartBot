// Production Readiness Check Script for ZmartyChat Onboarding
// This script tests all critical functionality before deployment

console.log('🚀 ZmartyChat Production Readiness Check');
console.log('=========================================');

let testsPassed = 0;
let testsFailed = 0;
const errors = [];

// Test helper function
function test(name, condition, errorMsg) {
    if (condition) {
        console.log(`✅ ${name}`);
        testsPassed++;
    } else {
        console.log(`❌ ${name}: ${errorMsg || 'Failed'}`);
        errors.push(`${name}: ${errorMsg || 'Failed'}`);
        testsFailed++;
    }
}

// Check if this is running in browser
if (typeof window === 'undefined') {
    console.log('⚠️  This script must be run in a browser environment');
    console.log('   Open index.html and run this script in the console');
    process.exit(1);
}

console.log('\n📋 Testing Critical Functions...\n');

// 1. Test Navigation Functions
test('nextSlide function exists', typeof window.nextSlide === 'function');
test('previousSlide function exists', typeof window.previousSlide === 'function');
test('goToSlide function exists', typeof window.goToSlide === 'function');

// 2. Test Email Detection Functions
test('checkEmailExists function exists', typeof window.checkEmailExists === 'function');
test('simpleRegister function exists', typeof window.simpleRegister === 'function');
test('continueWithEmail function exists', typeof window.continueWithEmail === 'function');

// 3. Test Progressive Reveal Functions
test('showPasswordField function exists', typeof window.showPasswordField === 'function');
test('showConfirmPasswordField function exists', typeof window.showConfirmPasswordField === 'function');
test('checkIfCanRegister function exists', typeof window.checkIfCanRegister === 'function');

// 4. Test Authentication Functions
test('quickLogin function exists', typeof window.quickLogin === 'function');
test('sendPasswordReset function exists', typeof window.sendPasswordReset === 'function');

// 5. Test Utility Functions
test('showError function exists', typeof window.showError === 'function');
test('selectTier function exists', typeof window.selectTier === 'function');
test('completeProfile function exists', typeof window.completeProfile === 'function');

// 6. Test Verification Functions
test('verifyCode function exists', typeof window.verifyCode === 'function');
test('resendCode function exists', typeof window.resendCode === 'function');

// 7. Test Supabase Configuration
test('Supabase client exists', typeof window.supabase !== 'undefined');
test('Supabase auth available', window.supabase && typeof window.supabase.auth !== 'undefined');

console.log('\n📋 Testing DOM Elements...\n');

// 8. Test Critical DOM Elements
test('Slide 1 exists', document.getElementById('slide-1') !== null);
test('Slide 4 (Register) exists', document.getElementById('slide-4') !== null);
test('Email input exists', document.getElementById('register-email') !== null);
test('Password field exists', document.getElementById('register-password') !== null);
test('Confirm password field exists', document.getElementById('confirm-password') !== null);
test('Register button exists', document.getElementById('email-continue-btn') !== null);
test('NEXT button exists', document.querySelector('.next-btn') !== null);
test('Navigation dots exist', document.querySelectorAll('.navigation-dots .dot').length > 0);

console.log('\n📋 Testing Interactive Features...\n');

// 9. Test Navigation Works
const initialSlide = window.currentSlide || 1;
window.nextSlide();
const afterNext = window.currentSlide;
test('Next navigation works', afterNext !== initialSlide, `Still on slide ${initialSlide}`);

window.previousSlide();
const afterPrev = window.currentSlide;
test('Previous navigation works', afterPrev === initialSlide, `Not back to slide ${initialSlide}`);

// 10. Test Slide Jump
window.goToSlide(3);
test('Direct slide navigation works', window.currentSlide === 3, `Current slide is ${window.currentSlide}`);

// Reset to slide 1
window.goToSlide(1);

console.log('\n📋 Testing Email Detection Flow...\n');

// 11. Navigate to registration slide
window.goToSlide(4);

// 12. Test email input triggers detection
const emailInput = document.getElementById('register-email');
if (emailInput) {
    // Simulate typing new email
    emailInput.value = 'newtest@example.com';
    emailInput.dispatchEvent(new Event('input'));

    setTimeout(() => {
        const passwordField = document.getElementById('register-password');
        test('Email detection triggers password field',
             passwordField && passwordField.style.display !== 'none',
             'Password field not shown');
    }, 1000);
}

console.log('\n📋 Testing Progressive Reveal...\n');

// 13. Test progressive reveal chain
const passwordField = document.getElementById('register-password');
if (passwordField) {
    passwordField.value = 'TestPassword123';
    passwordField.dispatchEvent(new Event('input'));

    setTimeout(() => {
        const confirmField = document.getElementById('confirm-password');
        test('Password input reveals confirm field',
             confirmField && confirmField.style.display !== 'none',
             'Confirm field not shown');

        if (confirmField) {
            confirmField.value = 'TestPassword123';
            confirmField.dispatchEvent(new Event('input'));

            setTimeout(() => {
                const registerBtn = document.getElementById('email-continue-btn');
                test('Matching passwords show register button',
                     registerBtn && registerBtn.style.display !== 'none',
                     'Register button not shown');
            }, 500);
        }
    }, 500);
}

// Final Summary
setTimeout(() => {
    console.log('\n=========================================');
    console.log('📊 PRODUCTION READINESS SUMMARY');
    console.log('=========================================');
    console.log(`✅ Tests Passed: ${testsPassed}`);
    console.log(`❌ Tests Failed: ${testsFailed}`);
    console.log(`📈 Success Rate: ${Math.round((testsPassed / (testsPassed + testsFailed)) * 100)}%`);

    if (testsFailed === 0) {
        console.log('\n🎉 ALL TESTS PASSED! Ready for production deployment.');
        console.log('\n📦 Next Steps:');
        console.log('1. Test on localhost:8081/test-onboarding.html');
        console.log('2. Verify email detection with real Supabase');
        console.log('3. Deploy to Netlify');
    } else {
        console.log('\n⚠️  ISSUES FOUND - Fix before deployment:');
        errors.forEach(error => console.log(`   - ${error}`));
    }

    console.log('\n🌐 Test URLs:');
    console.log('   Main: http://localhost:8081/index.html');
    console.log('   Test Suite: http://localhost:8081/test-onboarding.html');

}, 3000);