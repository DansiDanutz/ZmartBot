// Check if zmarty.me DNS is configured correctly for Resend
import dns from 'dns/promises';
import nodemailer from 'nodemailer';

async function checkDNS() {
    console.log('🔍 Checking DNS records for zmarty.me...\n');
    console.log('═'.repeat(50));

    const domain = 'zmarty.me';
    let recordsFound = 0;

    try {
        // Check TXT records (for SPF)
        console.log('\n📋 SPF Record (TXT):');
        console.log('─'.repeat(40));
        try {
            const txtRecords = await dns.resolveTxt(domain);
            txtRecords.forEach(record => {
                const txt = record.join('');
                if (txt.includes('include:amazonses.com')) {
                    console.log('✅ SPF record found:', txt);
                    recordsFound++;
                } else if (txt.includes('spf1')) {
                    console.log('⚠️  SPF record exists but missing Resend:', txt);
                } else {
                    console.log('   Other TXT:', txt);
                }
            });
        } catch (e) {
            console.log('❌ No TXT records found');
            console.log('   REQUIRED: "v=spf1 include:amazonses.com ~all"');
        }

        // Check DKIM CNAME record
        console.log('\n📋 DKIM Record (CNAME):');
        console.log('─'.repeat(40));
        const dkimSelector = 'resend._domainkey';

        try {
            const cname = await dns.resolveCname(`${dkimSelector}.${domain}`);
            console.log(`✅ ${dkimSelector} →`, cname[0]);
            recordsFound++;
        } catch (e) {
            console.log('❌ DKIM record not found');
            console.log('   REQUIRED: CNAME from resend._domainkey');
            console.log('   (You\'ll get this value from Resend dashboard)');
        }

        // Summary
        console.log('\n' + '═'.repeat(50));
        console.log(`📊 DNS Status: ${recordsFound}/2 records configured`);
        console.log('═'.repeat(50));

        if (recordsFound === 0) {
            console.log('\n🚨 ACTION REQUIRED:');
            console.log('────────────────────');
            console.log('\n1️⃣  Go to: https://resend.com/domains');
            console.log('2️⃣  Click "Add Domain"');
            console.log('3️⃣  Enter: zmarty.me');
            console.log('4️⃣  You\'ll see 2 DNS records to add:');
            console.log('    • SPF (TXT record)');
            console.log('    • DKIM (CNAME record)');
            console.log('\n5️⃣  In GoDaddy (https://dcc.godaddy.com/domains/):');
            console.log('    • Click on zmarty.me');
            console.log('    • Go to "DNS" or "Manage DNS"');
            console.log('    • Add the records from Resend');
            console.log('\n6️⃣  Wait 5-30 minutes for DNS propagation');
            console.log('7️⃣  Click "Verify Domain" in Resend dashboard');
        } else if (recordsFound < 2) {
            console.log('\n⚠️  Partial configuration detected');
            console.log('   Complete the missing records in GoDaddy');
        } else {
            console.log('\n✅ All DNS records configured!');
            console.log('   Verify domain in Resend dashboard if not done');
        }

    } catch (error) {
        console.error('Error checking DNS:', error.message);
    }
}

// Test if we can send email
async function testEmailCapability() {
    console.log('\n\n🚀 Testing email sending capability...');
    console.log('═'.repeat(50));

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
        // Verify SMTP connection
        await transporter.verify();
        console.log('✅ SMTP connection successful');

        // Try sending from zmarty.me
        await transporter.sendMail({
            from: '"Zmarty" <noreply@zmarty.me>',
            to: 'test@resend.com', // Resend test address
            subject: 'Domain Verification Test',
            text: 'Testing zmarty.me domain'
        });

        console.log('\n🎉 SUCCESS! Your zmarty.me domain is ready!');
        console.log('═'.repeat(50));
        console.log('\n✨ You can now:');
        console.log('   • Send emails from any @zmarty.me address');
        console.log('   • Configure Supabase to use noreply@zmarty.me');

        console.log('\n📝 SUPABASE CONFIGURATION:');
        console.log('────────────────────────');
        console.log('In Supabase Dashboard → Settings → Auth:');
        console.log('');
        console.log('SMTP Settings:');
        console.log('  Host: smtp.resend.com');
        console.log('  Port: 587');
        console.log('  Username: resend');
        console.log('  Password: re_FbA39H6g_L2uZQktnoGQgMQZMcDc3xgWg');
        console.log('  Sender email: noreply@zmarty.me');
        console.log('  Sender name: Zmarty');

    } catch (error) {
        if (error.message.includes('verify a domain') || error.message.includes('not verified')) {
            console.log('\n⏳ Domain not verified in Resend yet');
            console.log('   Complete DNS setup and verify in Resend dashboard');
            console.log('\n   Error details:', error.response || error.message);
        } else {
            console.log('\n❌ Error:', error.response || error.message);
        }
    }
}

// Run both checks
console.log('🌐 ZMARTY.ME DOMAIN SETUP CHECKER');
console.log('═'.repeat(50));

checkDNS().then(() => testEmailCapability());