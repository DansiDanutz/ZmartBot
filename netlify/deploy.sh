#!/bin/bash

echo "🚀 DEPLOYING ZMARTYBRAIN TO NETLIFY"
echo "===================================="
echo ""

# Check if we have the Netlify CLI
if command -v netlify &> /dev/null; then
    echo "✅ Netlify CLI detected"
    echo ""
    echo "Deploying to production..."

    netlify deploy --prod --dir=.

    echo ""
    echo "✅ Deployment complete!"
else
    echo "⚠️  Netlify CLI not installed"
    echo ""
    echo "Option 1: Install Netlify CLI"
    echo "  npm install -g netlify-cli"
    echo "  Then run: ./deploy.sh"
    echo ""
    echo "Option 2: Manual deployment"
    echo "  1. Go to https://app.netlify.com/drop"
    echo "  2. Drag the 'netlify' folder to the browser"
    echo "  3. Your site will be live immediately!"
fi

echo ""
echo "📱 Features included:"
echo "  ✅ 9-step onboarding flow"
echo "  ✅ Working navigation (arrows, keyboard, swipe)"
echo "  ✅ All forms and validation"
echo "  ✅ Authentication UI"
echo "  ✅ Plan selection"
echo "  ✅ Responsive design"
echo ""
echo "🌐 Your site will be available at:"
echo "   https://[your-site-name].netlify.app"