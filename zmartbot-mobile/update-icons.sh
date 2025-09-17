#!/bin/bash
echo "🎨 ZmartBot Icon Update Script"
echo "=============================="

# Check if icon files exist
echo "📋 Checking current icons..."
ls -la assets/images/*.png

echo ""
echo "🎯 INSTRUCTIONS TO ADD YOUR Z LOGO:"
echo "1. Save your Z logo as 'icon.png' (1024x1024px) in assets/images/"
echo "2. Copy the same image as 'adaptive-icon.png' in assets/images/"
echo "3. Copy the same image as 'splash-icon.png' in assets/images/"
echo "4. Create a smaller version (48x48px) as 'favicon.png' in assets/images/"
echo ""

# Check if we can build
echo "🚀 Ready to build with new icons? (y/n)"
read -r response

if [[ "$response" == "y" || "$response" == "Y" ]]; then
    echo "🔧 Starting build with new Z logo icons..."
    npx eas build --platform android --profile preview
else
    echo "📝 Please replace the icon files first, then run this script again"
fi