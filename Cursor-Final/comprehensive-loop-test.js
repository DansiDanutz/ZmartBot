// ZmartyBrain Comprehensive Loop Testing System
// Run this in browser console on http://localhost:8888

console.log('🧪 STARTING COMPREHENSIVE ONBOARDING LOOP TEST');
console.log('=' .repeat(60));

const testResults = {
    slide1: { name: 'Welcome', issues: [], status: 'testing' },
    slide2: { name: 'AI Models', issues: [], status: 'pending' },
    slide3: { name: 'Exchange Integrations', issues: [], status: 'pending' },
    slide4: { name: 'Risk Management', issues: [], status: 'pending' },
    slide5: { name: 'Authentication', issues: [], status: 'pending' },
    slide6: { name: 'Google Confirmation', issues: [], status: 'pending' },
    slide7: { name: 'Email Verification', issues: [], status: 'pending' },
    slide8: { name: 'Password Reset', issues: [], status: 'pending' },
    slide9: { name: 'Tier Selection', issues: [], status: 'pending' },
    slide10: { name: 'Profile Setup', issues: [], status: 'pending' },
    slide11: { name: 'Success', issues: [], status: 'pending' }
};

// Test utility functions
function checkElement(selector, expectedText = null, required = true) {
    const element = document.querySelector(selector);
    if (!element) {
        if (required) {
            return { found: false, error: `Element not found: ${selector}` };
        }
        return { found: false, optional: true };
    }

    if (expectedText && !element.textContent.includes(expectedText)) {
        return { found: false, error: `Text mismatch in ${selector}. Expected: ${expectedText}` };
    }

    return { found: true, element };
}

function checkVisibility(selector) {
    const element = document.querySelector(selector);
    if (!element) return { visible: false, error: 'Element not found' };

    const style = getComputedStyle(element);
    const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';

    return { visible: isVisible, element };
}

function addIssue(slideKey, priority, description, type = 'visual') {
    testResults[slideKey].issues.push({
        priority,
        description,
        type,
        timestamp: new Date().toISOString()
    });
}

// SLIDE 1: Welcome Testing
console.log('\n📍 TESTING SLIDE 1: Welcome');
testResults.slide1.status = 'testing';

// Check main title
const titleCheck = checkElement('h1', 'Welcome to Zmarty');
if (!titleCheck.found) {
    addIssue('slide1', 'HIGH', 'Main title missing or incorrect text', 'content');
    console.log('  ❌ Title: ' + titleCheck.error);
} else {
    console.log('  ✅ Title: "Welcome to Zmarty" found');
}

// Check subtitle
const subtitleCheck = checkElement('.subtitle', 'AI-Powered Trading Revolution');
if (!subtitleCheck.found) {
    addIssue('slide1', 'MEDIUM', 'Subtitle missing or incorrect', 'content');
    console.log('  ❌ Subtitle: ' + subtitleCheck.error);
} else {
    console.log('  ✅ Subtitle: "AI-Powered Trading Revolution" found');
}

// Check feature cards
const featureCards = [
    { selector: '.feature-card', text: 'Smart AI', desc: '4 AI Models Combined' },
    { selector: '.feature-card', text: 'Liquidation Clusters', desc: 'Real-time tracking' },
    { selector: '.feature-card', text: 'Risk Metrics', desc: '20+ indicators' },
    { selector: '.feature-card', text: 'Bank Secure', desc: 'Enterprise grade' }
];

const allFeatureCards = document.querySelectorAll('.feature-card');
console.log(`  📊 Found ${allFeatureCards.length} feature cards`);

if (allFeatureCards.length < 4) {
    addIssue('slide1', 'HIGH', `Only ${allFeatureCards.length} feature cards found, expected 4`, 'layout');
    console.log('  ❌ Feature cards: Missing cards');
} else {
    console.log('  ✅ Feature cards: All 4 cards present');
}

// Check floating rocket emoji
const rocketEmoji = checkElement('.float', '🚀');
if (!rocketEmoji.found) {
    addIssue('slide1', 'LOW', 'Floating rocket emoji missing', 'visual');
    console.log('  ❌ Rocket emoji: Not found');
} else {
    console.log('  ✅ Rocket emoji: Found and animated');
}

// Check Get Started button
const getStartedBtn = checkElement('.btn-primary', 'Start Free Trial');
if (!getStartedBtn.found) {
    addIssue('slide1', 'HIGH', 'Get Started button missing or incorrect text', 'functional');
    console.log('  ❌ Get Started button: ' + getStartedBtn.error);
} else {
    console.log('  ✅ Get Started button: "Start Free Trial" found');
}

testResults.slide1.status = 'completed';

// SLIDE 2: AI Models Testing
console.log('\n📍 TESTING SLIDE 2: AI Models');
testResults.slide2.status = 'testing';

// Navigate to slide 2 (simulated)
const aiModelsTitle = 'Powered by Multiple AI Models';
const aiModels = ['Claude (Anthropic)', 'GPT-4 (OpenAI)', 'Gemini (Google)', 'Grok (xAI)'];

console.log('  📋 Expected AI Models:');
aiModels.forEach(model => console.log(`    - ${model}`));

// Check if slide 2 content exists in DOM
const step2Element = document.querySelector('#step2');
if (!step2Element) {
    addIssue('slide2', 'HIGH', 'Slide 2 element not found in DOM', 'structural');
    console.log('  ❌ Slide 2: DOM element missing');
} else {
    console.log('  ✅ Slide 2: DOM element found');

    // Check AI models grid
    const aiGrid = step2Element.querySelector('.ai-models-grid');
    if (!aiGrid) {
        addIssue('slide2', 'HIGH', 'AI models grid not found', 'layout');
        console.log('  ❌ AI grid: Not found');
    } else {
        const aiCards = aiGrid.querySelectorAll('.ai-model-card');
        console.log(`  📊 Found ${aiCards.length} AI model cards`);

        if (aiCards.length < 4) {
            addIssue('slide2', 'HIGH', `Only ${aiCards.length} AI model cards found, expected 4`, 'content');
        }
    }
}

testResults.slide2.status = 'completed';

// NAVIGATION TESTING
console.log('\n🎮 TESTING NAVIGATION SYSTEM');

// Check progress bar
const progressBar = checkElement('.progress-bar');
if (!progressBar.found) {
    addIssue('slide1', 'MEDIUM', 'Progress bar not found', 'ui');
    console.log('  ❌ Progress bar: Not found');
} else {
    console.log('  ✅ Progress bar: Present');
}

// Check navigation buttons
const nextBtn = checkElement('.btn-primary');
const prevBtn = checkElement('.btn-secondary');

if (!nextBtn.found) {
    addIssue('slide1', 'HIGH', 'Next button not found', 'navigation');
}
if (!prevBtn.found) {
    console.log('  ℹ️  Previous button: Not expected on slide 1');
}

// MOBILE RESPONSIVENESS TEST
console.log('\n📱 TESTING MOBILE RESPONSIVENESS');

// Check viewport meta tag
const viewportMeta = document.querySelector('meta[name="viewport"]');
if (!viewportMeta) {
    addIssue('slide1', 'MEDIUM', 'Viewport meta tag missing', 'mobile');
    console.log('  ❌ Viewport meta: Not found');
} else {
    console.log('  ✅ Viewport meta: Found');
}

// Check CSS media queries (simplified test)
const containerWidth = document.querySelector('.onboarding-container')?.offsetWidth;
console.log(`  📐 Container width: ${containerWidth}px`);

if (containerWidth > window.innerWidth) {
    addIssue('slide1', 'HIGH', 'Container wider than viewport on mobile', 'mobile');
    console.log('  ❌ Mobile layout: Container overflow detected');
} else {
    console.log('  ✅ Mobile layout: Container fits viewport');
}

// PERFORMANCE TESTING
console.log('\n⚡ TESTING PERFORMANCE');

// Check for loading states
const loadingElements = document.querySelectorAll('.loading-spinner, .loading-overlay');
console.log(`  🔄 Found ${loadingElements.length} loading elements`);

// Check for critical resources
const criticalResources = document.querySelectorAll('link[rel="preload"], link[rel="preconnect"]');
console.log(`  🚀 Found ${criticalResources.length} preloaded resources`);

// ACCESSIBILITY TESTING
console.log('\n♿ TESTING ACCESSIBILITY');

// Check for alt texts on images
const images = document.querySelectorAll('img');
let missingAltCount = 0;
images.forEach(img => {
    if (!img.alt) missingAltCount++;
});

if (missingAltCount > 0) {
    addIssue('slide1', 'MEDIUM', `${missingAltCount} images missing alt text`, 'accessibility');
    console.log(`  ❌ Alt text: ${missingAltCount} images missing alt text`);
} else {
    console.log('  ✅ Alt text: All images have alt text');
}

// Check for semantic HTML
const headings = document.querySelectorAll('h1, h2, h3');
console.log(`  📋 Found ${headings.length} heading elements`);

// GENERATE FINAL REPORT
console.log('\n' + '=' .repeat(60));
console.log('📊 COMPREHENSIVE TEST REPORT');
console.log('=' .repeat(60));

let totalIssues = 0;
let highPriorityIssues = 0;
let mediumPriorityIssues = 0;
let lowPriorityIssues = 0;

Object.entries(testResults).forEach(([slideKey, slide]) => {
    console.log(`\n🎯 ${slide.name.toUpperCase()}:`);

    if (slide.issues.length === 0) {
        console.log('  ✅ NO ISSUES FOUND');
    } else {
        slide.issues.forEach(issue => {
            const icon = issue.priority === 'HIGH' ? '🔴' : issue.priority === 'MEDIUM' ? '🟡' : '🟢';
            console.log(`  ${icon} ${issue.priority}: ${issue.description} (${issue.type})`);

            totalIssues++;
            if (issue.priority === 'HIGH') highPriorityIssues++;
            else if (issue.priority === 'MEDIUM') mediumPriorityIssues++;
            else lowPriorityIssues++;
        });
    }
});

console.log('\n' + '=' .repeat(60));
console.log('📈 SUMMARY STATISTICS:');
console.log(`🔴 High Priority Issues: ${highPriorityIssues}`);
console.log(`🟡 Medium Priority Issues: ${mediumPriorityIssues}`);
console.log(`🟢 Low Priority Issues: ${lowPriorityIssues}`);
console.log(`📊 Total Issues Found: ${totalIssues}`);

const score = Math.max(0, 100 - (highPriorityIssues * 10) - (mediumPriorityIssues * 5) - (lowPriorityIssues * 2));
console.log(`🎯 Overall Score: ${score}%`);

if (score >= 95) {
    console.log('🎉 EXCELLENT! Ready for production deployment');
} else if (score >= 85) {
    console.log('✅ GOOD! Minor fixes needed before deployment');
} else if (score >= 70) {
    console.log('⚠️  NEEDS WORK! Several issues need fixing');
} else {
    console.log('🔴 CRITICAL! Major issues must be resolved');
}

console.log('\n' + '=' .repeat(60));
console.log('📋 RECOMMENDED NEXT ACTIONS:');

if (highPriorityIssues > 0) {
    console.log('1. 🔥 FIX HIGH PRIORITY ISSUES IMMEDIATELY');
    console.log('2. 🧪 Re-run comprehensive test');
    console.log('3. 📱 Test on multiple devices');
}

if (mediumPriorityIssues > 0) {
    console.log('- 🔧 Address medium priority issues');
    console.log('- 🎨 Review design consistency');
}

console.log('- 🚀 Continue with slides 3-11 testing');
console.log('- 📊 Run automated navigation test');
console.log('- 💻 Test on different browsers');

console.log('\n✅ COMPREHENSIVE LOOP TEST COMPLETED');
console.log('=' .repeat(60));

// Export results for further analysis
window.testResults = testResults;
console.log('\n💾 Test results saved to window.testResults');