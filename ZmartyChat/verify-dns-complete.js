// Complete DNS verification for zmarty.me
import dns from 'dns/promises';
import nodemailer from 'nodemailer';

async function verifyDNSComplete() {
    console.log('🔍 COMPLETE DNS VERIFICATION FOR ZMARTY.ME');
    console.log('═'.repeat(60));
    console.log('\nChecking all required DNS records...\n');

    const domain = 'zmarty.me';
    let allRecordsValid = true;

    // 1. Check SPF on root domain
    console.log('1️⃣  SPF Record (root domain):');
    try {
        const txtRecords = await dns.resolveTxt(domain);
        const spfRecord = txtRecords.find(r => r.join('').includes('spf1'));
        if (spfRecord) {
            console.log('   ✅ Found:', spfRecord.join(''));
        } else {
            console.log('   ⚠️  Not found at root');
        }
    } catch (e) {
        console.log('   ❌ Error checking root SPF');
    }

    // 2. Check SPF on send subdomain
    console.log('\n2️⃣  SPF Record (send subdomain):');
    try {
        const txtRecords = await dns.resolveTxt(`send.${domain}`);
        const spfRecord = txtRecords.find(r => r.join('').includes('spf1'));
        if (spfRecord) {
            console.log('   ✅ Found:', spfRecord.join(''));
        } else {
            console.log('   ❌ Not found at send subdomain');
            allRecordsValid = false;
        }
    } catch (e) {
        console.log('   ❌ Not found at send subdomain');
        allRecordsValid = false;
    }

    // 3. Check DKIM
    console.log('\n3️⃣  DKIM Record (resend._domainkey):');
    try {
        const dkimRecords = await dns.resolveTxt(`resend._domainkey.${domain}`);
        if (dkimRecords && dkimRecords.length > 0) {
            const dkimValue = dkimRecords[0].join('');
            console.log('   ✅ Found: p=', dkimValue.substring(2, 50) + '...');
        } else {
            console.log('   ❌ Not found');
            allRecordsValid = false;
        }
    } catch (e) {
        console.log('   ❌ Not found');
        allRecordsValid = false;
    }

    // 4. Check MX record
    console.log('\n4️⃣  MX Record (optional but recommended):');
    try {
        const mxRecords = await dns.resolveMx(`send.${domain}`);
        if (mxRecords && mxRecords.length > 0) {
            console.log('   ✅ Found:', mxRecords[0].exchange);
        } else {
            console.log('   ⚠️  Not found (optional)');
        }
    } catch (e) {
        console.log('   ⚠️  Not found (optional)');
    }

    // 5. Check DMARC
    console.log('\n5️⃣  DMARC Record (optional):');
    try {
        const dmarcRecords = await dns.resolveTxt(`_dmarc.${domain}`);
        if (dmarcRecords && dmarcRecords.length > 0) {
            console.log('   ✅ Found:', dmarcRecords[0].join(''));
        } else {
            console.log('   ⚠️  Not found (optional)');
        }
    } catch (e) {
        console.log('   ⚠️  Not found (optional)');
    }

    // Summary
    console.log('\n' + '═'.repeat(60));
    if (allRecordsValid) {
        console.log('✅ ALL REQUIRED DNS RECORDS ARE CONFIGURED!');
    } else {
        console.log('⚠️  SOME REQUIRED RECORDS ARE MISSING');
    }
    console.log('═'.repeat(60));

    // Test email sending
    console.log('\n\n🚀 TESTING EMAIL CAPABILITY...');
    console.log('─'.repeat(60));

    const transporter = nodemailer.createTransport({
        host: 'smtp.resend.com',
        port: 587,
        secure: false,
        auth: {
            user: 'resend',
            pass: 're_FbA39H6g_L2uZQktnoGQgMQZMcDc3xgWg'
        }
    });

    try {
        await transporter.verify();
        console.log('✅ SMTP connection successful');

        // Try sending test email
        const result = await transporter.sendMail({
            from: '"Zmarty" <noreply@zmarty.me>',
            to: 'test@resend.com', // Test address
            subject: 'Domain Test',
            text: 'Testing zmarty.me domain'
        });

        console.log('✅ DOMAIN IS VERIFIED AND WORKING!');
        console.log('📧 You can now send emails from @zmarty.me');

        // Final test to user's email
        await transporter.sendMail({
            from: '"Zmarty" <noreply@zmarty.me>',
            to: 'dansidanutz@yahoo.com',
            subject: '🎉 Zmarty.me Email System Active!',
            html: `
                <div style="font-family: system-ui; padding: 20px;">
                    <h2>✅ Success! Your email domain is working!</h2>
                    <p>This email was sent from <strong>noreply@zmarty.me</strong></p>
                    <p>Your Supabase authentication emails will now use this domain.</p>
                </div>
            `
        });

        console.log('\n📬 Check your inbox at dansidanutz@yahoo.com');
        console.log('🎉 EMAIL SYSTEM FULLY OPERATIONAL!');

    } catch (error) {
        if (error.message.includes('not verified')) {
            console.log('\n⚠️  Domain not verified in Resend yet');
            console.log('\n📋 NEXT STEPS:');
            console.log('1. Go to https://resend.com/domains');
            console.log('2. Click "Verify DNS Records" for zmarty.me');
            console.log('3. If records don\'t verify:');
            console.log('   - Remove the domain from Resend');
            console.log('   - Re-add zmarty.me');
            console.log('   - It will show new DNS records to add');
            console.log('4. Make sure ALL records show green checkmarks');
        } else {
            console.log('❌ Error:', error.message);
        }
    }
}

verifyDNSComplete();