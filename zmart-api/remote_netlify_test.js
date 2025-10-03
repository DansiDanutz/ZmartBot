/**
 * Remote Netlify Onboarding Testing Script
 * This script can be run from the command line to test the Netlify deployment
 *
 * Usage: node remote_netlify_test.js
 */

const https = require('https');
const { URL } = require('url');

const TEST_URL = 'https://vermillion-paprenjak-67497b.netlify.app';

function makeRequest(url) {
    return new Promise((resolve, reject) => {
        const parsedUrl = new URL(url);

        const options = {
            hostname: parsedUrl.hostname,
            port: parsedUrl.port || 443,
            path: parsedUrl.pathname + parsedUrl.search,
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    body: data
                });
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.setTimeout(10000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

function logTestResult(testName, passed, details = '') {
    const emoji = passed ? '✅' : '❌';
    const status = passed ? 'PASS' : 'FAIL';
    console.log(`${emoji} ${testName}: ${status}${details ? ' - ' + details : ''}`);
    return passed;
}

async function testNetlifyOnboarding() {
    console.log('🧪 Remote Netlify Onboarding Test\n');
    console.log(`🌐 Testing: ${TEST_URL}\n`);

    let allTestsPassed = true;

    try {
        // Test 1: Basic connectivity and response
        console.log('📡 Test 1: Basic connectivity');
        const response = await makeRequest(TEST_URL);

        const connectivityPassed = logTestResult(
            'HTTP Response',
            response.statusCode === 200,
            `Status: ${response.statusCode}`
        );
        allTestsPassed = allTestsPassed && connectivityPassed;

        if (response.statusCode !== 200) {
            console.log('❌ Cannot proceed with further tests due to connectivity issues');
            return false;
        }

        // Test 2: Content length check
        console.log('\n📄 Test 2: Content analysis');
        const contentLengthPassed = logTestResult(
            'Content Length',
            response.body.length > 5000,
            `${response.body.length} characters`
        );
        allTestsPassed = allTestsPassed && contentLengthPassed;

        // Test 3: HTML structure validation
        console.log('\n🏗️  Test 3: HTML structure validation');

        const structureTests = [
            {
                name: 'DOCTYPE Declaration',
                test: response.body.includes('<!DOCTYPE html>') || response.body.includes('<!doctype html>')
            },
            {
                name: 'HTML Tag',
                test: response.body.includes('<html')
            },
            {
                name: 'Head Section',
                test: response.body.includes('<head>') && response.body.includes('</head>')
            },
            {
                name: 'Body Section',
                test: response.body.includes('<body>') && response.body.includes('</body>')
            },
            {
                name: 'Meta Viewport',
                test: response.body.includes('viewport')
            }
        ];

        structureTests.forEach(test => {
            const passed = logTestResult('HTML ' + test.name, test.test);
            allTestsPassed = allTestsPassed && passed;
        });

        // Test 4: Critical onboarding elements
        console.log('\n🎯 Test 4: Onboarding elements detection');

        const onboardingTests = [
            {
                name: 'Slide 1 (Welcome)',
                test: response.body.includes('id="step1"') || response.body.includes('step1')
            },
            {
                name: 'Slide 2 (AI Models)',
                test: response.body.includes('id="step2"') || response.body.includes('step2')
            },
            {
                name: 'Slide 3 (Exchanges)',
                test: response.body.includes('id="step3"') || response.body.includes('step3')
            },
            {
                name: 'Slide 4 (Risk Management)',
                test: response.body.includes('id="step4"') || response.body.includes('step4')
            },
            {
                name: 'Slide 5 (Authentication)',
                test: response.body.includes('id="step5"') || response.body.includes('step5')
            },
            {
                name: 'Get Started Button',
                test: response.body.includes('Get Started') || response.body.includes('Start Free Trial')
            },
            {
                name: 'Google Tab',
                test: response.body.includes('googleTab') || response.body.includes('Google')
            },
            {
                name: 'Email Input',
                test: response.body.includes('type="email"')
            },
            {
                name: 'Password Input',
                test: response.body.includes('type="password"')
            },
            {
                name: 'Progress Bar',
                test: response.body.includes('progressFill') || response.body.includes('progress')
            }
        ];

        onboardingTests.forEach(test => {
            const passed = logTestResult('Element: ' + test.name, test.test);
            allTestsPassed = allTestsPassed && passed;
        });

        // Test 5: JavaScript and CSS inclusion
        console.log('\n📜 Test 5: Resource inclusion');

        const resourceTests = [
            {
                name: 'CSS Styling',
                test: response.body.includes('<style>') || response.body.includes('.css') || response.body.includes('style=')
            },
            {
                name: 'JavaScript Code',
                test: response.body.includes('<script>') || response.body.includes('.js') || response.body.includes('function')
            },
            {
                name: 'Navigation Functions',
                test: response.body.includes('nextStep') || response.body.includes('goToStep') || response.body.includes('navigate')
            }
        ];

        resourceTests.forEach(test => {
            const passed = logTestResult('Resource: ' + test.name, test.test);
            allTestsPassed = allTestsPassed && passed;
        });

        // Test 6: Security headers
        console.log('\n🔒 Test 6: Security headers');

        const securityTests = [
            {
                name: 'Content-Type',
                test: response.headers['content-type'] && response.headers['content-type'].includes('text/html')
            },
            {
                name: 'Content Security Policy',
                test: !!response.headers['content-security-policy']
            },
            {
                name: 'HTTPS Enforcement',
                test: !!response.headers['strict-transport-security']
            },
            {
                name: 'X-Frame-Options',
                test: !!response.headers['x-frame-options']
            }
        ];

        securityTests.forEach(test => {
            const passed = logTestResult('Security: ' + test.name, test.test);
            // Don't fail overall test for missing security headers, just warn
        });

        // Test 7: Performance indicators
        console.log('\n⚡ Test 7: Performance indicators');

        const performanceTests = [
            {
                name: 'Content Compression',
                test: response.headers['content-encoding'] === 'gzip' || response.headers['content-encoding'] === 'br'
            },
            {
                name: 'Cache Headers',
                test: !!response.headers['cache-control'] || !!response.headers['etag']
            },
            {
                name: 'Content Size',
                test: response.body.length < 1000000 // Less than 1MB
            }
        ];

        performanceTests.forEach(test => {
            const passed = logTestResult('Performance: ' + test.name, test.test);
            // Don't fail overall test for performance issues, just report
        });

        // Final summary
        console.log('\n' + '='.repeat(60));
        console.log(`🎯 REMOTE TEST SUMMARY`);
        console.log('='.repeat(60));
        console.log(`🌐 URL: ${TEST_URL}`);
        console.log(`📅 Test Date: ${new Date().toISOString()}`);
        console.log(`✅ Overall Status: ${allTestsPassed ? 'PASSED' : 'FAILED'}`);
        console.log(`📊 Content Size: ${(response.body.length / 1024).toFixed(2)} KB`);
        console.log(`⏱️  Response Time: < 10 seconds`);

        if (!allTestsPassed) {
            console.log(`\n⚠️  ISSUES FOUND: Some tests failed`);
            console.log(`💡 RECOMMENDATION: Check failed tests above`);
        } else {
            console.log(`\n🎉 ALL TESTS PASSED!`);
            console.log(`💡 NEXT STEP: Run manual browser testing for interactivity`);
        }

        console.log('\n📋 MANUAL TESTING INSTRUCTIONS:');
        console.log('   1. Open Chrome browser');
        console.log('   2. Navigate to: ' + TEST_URL);
        console.log('   3. Open Developer Tools (F12)');
        console.log('   4. Run: netlify_onboarding_test.js in Console');
        console.log('   5. Follow: NETLIFY_MANUAL_TEST_CHECKLIST.md');
        console.log('='.repeat(60));

        return allTestsPassed;

    } catch (error) {
        console.error('❌ Test execution failed:', error.message);
        return false;
    }
}

// Run the test
if (require.main === module) {
    testNetlifyOnboarding().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error('💥 Unexpected error:', error);
        process.exit(1);
    });
}

module.exports = { testNetlifyOnboarding };