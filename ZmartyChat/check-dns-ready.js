// Check if zmarty.team DNS is configured correctly
import dns from 'dns/promises';

async function checkDNS() {
    console.log('🔍 Checking DNS records for zmarty.team...\n');

    const domain = 'zmarty.team';

    try {
        // Check TXT records (for SPF)
        console.log('📋 TXT Records (checking for SPF):');
        try {
            const txtRecords = await dns.resolveTxt(domain);
            txtRecords.forEach(record => {
                const txt = record.join('');
                if (txt.includes('spf1')) {
                    console.log('✅ SPF record found:', txt);
                } else {
                    console.log('   TXT:', txt);
                }
            });
        } catch (e) {
            console.log('❌ No TXT records found');
        }

        // Check DKIM CNAME records
        console.log('\n📋 DKIM Records (CNAME):');
        const dkimSelectors = [
            'resend._domainkey',
            'resend1._domainkey',
            'resend2._domainkey'
        ];

        for (const selector of dkimSelectors) {
            try {
                const cname = await dns.resolveCname(`${selector}.${domain}`);
                console.log(`✅ ${selector} →`, cname[0]);
            } catch (e) {
                // This is normal if the selector doesn't exist yet
            }
        }

        console.log('\n📊 DNS Status:');
        console.log('1. After adding records in GoDaddy, wait 5-30 minutes');
        console.log('2. Then verify in Resend dashboard');
        console.log('3. Once verified, you can send to any email address!');

    } catch (error) {
        console.error('Error checking DNS:', error.message);
    }
}

// Also test if we can send email
async function testEmail() {
    console.log('\n\n🚀 Testing email sending capability...\n');

    const nodemailer = await import('nodemailer');

    const transporter = nodemailer.default.createTransport({
        host: 'smtp.resend.com',
        port: 587,
        secure: false,
        auth: {
            user: 'resend',
            pass: 're_FbA39H6g_L2uZQktnoGQgMQZMcDc3xgWg'
        }
    });

    try {
        // Try sending from zmarty.team
        await transporter.sendMail({
            from: '"Zmarty Team" <noreply@zmarty.team>',
            to: 'test@example.com', // Just testing, won't actually send
            subject: 'Test',
            text: 'Test'
        });

        console.log('✅ zmarty.team is READY! You can send emails from your domain!');

    } catch (error) {
        if (error.message.includes('verify a domain')) {
            console.log('⏳ Domain not verified in Resend yet');
            console.log('   Add DNS records in GoDaddy first, then verify in Resend');
        } else {
            console.log('❌ Not ready:', error.response || error.message);
        }
    }
}

// Run checks
checkDNS().then(() => testEmail());