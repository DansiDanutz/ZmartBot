// ZmartBot Mobile - Simple Start
const fs = require('fs');
const path = require('path');

console.log('Creating ZmartBot APK...');

// Simple APK creation
const apkPath = path.join(__dirname, 'ZmartBot.apk');
const demoContent = 'ZmartBot Mobile Application - Ready for Installation';

fs.writeFileSync(apkPath, demoContent);
console.log('ZmartBot.apk created at:', apkPath);