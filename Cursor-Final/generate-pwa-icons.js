const fs = require('fs');
const { createCanvas } = require('canvas');

function generateIcon(size) {
    const canvas = createCanvas(size, size);
    const ctx = canvas.getContext('2d');

    // Background gradient (purple theme)
    const gradient = ctx.createLinearGradient(0, 0, size, size);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);

    // White text "ZB"
    ctx.fillStyle = 'white';
    ctx.font = `bold ${size * 0.35}px Arial, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('ZB', size / 2, size / 2 + size * 0.05);

    return canvas.toBuffer('image/png');
}

// Generate and save icons
try {
    // Generate 192x192 icon
    const icon192 = generateIcon(192);
    fs.writeFileSync('icon-192.png', icon192);
    console.log('✅ Created icon-192.png');

    // Generate 512x512 icon
    const icon512 = generateIcon(512);
    fs.writeFileSync('icon-512.png', icon512);
    console.log('✅ Created icon-512.png');

    // Also copy to MANUAL-DEPLOY folder
    fs.writeFileSync('../MANUAL-DEPLOY-100-PERCENT/icon-192.png', icon192);
    fs.writeFileSync('../MANUAL-DEPLOY-100-PERCENT/icon-512.png', icon512);
    console.log('✅ Copied icons to MANUAL-DEPLOY-100-PERCENT folder');

    console.log('\n🎉 PWA icons generated successfully!');
} catch (error) {
    console.error('Error generating icons:', error);
}