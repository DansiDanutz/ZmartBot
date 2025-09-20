const fs = require('fs');
const path = require('path');

const productionDir = path.join(__dirname, 'production-ready');
const filesToClean = [
    'supabase-dual-client.js',
    'supabase-client.js',
    'onboarding-slides.js',
    'dashboard.js',
    'reset-password.html'
];

filesToClean.forEach(file => {
    const filePath = path.join(productionDir, file);

    if (fs.existsSync(filePath)) {
        let content = fs.readFileSync(filePath, 'utf8');

        // Remove console.log statements
        content = content.replace(/console\.log\([^)]+\);?\n?/g, '');

        // Remove TEST comments/modes
        content = content.replace(/\/\/\s*TEST.*\n/gi, '');
        content = content.replace(/\/\*\s*TEST[\s\S]*?\*\//gi, '');

        fs.writeFileSync(filePath, content);
        console.log(`✅ Cleaned ${file}`);
    }
});

console.log('\n🎉 All production files cleaned!');