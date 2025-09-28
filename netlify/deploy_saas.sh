#!/bin/bash

echo "🚀 DEPLOYING COMPLETE SAAS ONBOARDING TO NETLIFY"
echo "================================================"
echo ""
echo "This deployment includes:"
echo "✅ 6-step onboarding flow"
echo "✅ Supabase authentication integration"
echo "✅ Google OAuth configuration"
echo "✅ Stripe payment integration"
echo "✅ Team/organization management"
echo "✅ Complete user profile setup"
echo ""

# Check which file to deploy
echo "Select which version to deploy:"
echo "1) index.html - Original fixed version"
echo "2) enhanced_onboarding.html - Enhanced with team setup"
echo "3) saas_onboarding_complete.html - Full SaaS features"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        DEPLOY_FILE="index.html"
        echo "Deploying original fixed version..."
        ;;
    2)
        DEPLOY_FILE="enhanced_onboarding.html"
        echo "Deploying enhanced version..."
        ;;
    3)
        DEPLOY_FILE="saas_onboarding_complete.html"
        echo "Deploying complete SaaS version..."
        ;;
    *)
        echo "Invalid choice. Deploying complete SaaS version by default..."
        DEPLOY_FILE="saas_onboarding_complete.html"
        ;;
esac

# Create a deployment directory
echo "Preparing deployment..."
mkdir -p deploy_temp
cp $DEPLOY_FILE deploy_temp/index.html
cp -r favicon.ico deploy_temp/ 2>/dev/null || true
cp netlify.toml deploy_temp/ 2>/dev/null || true
cp _headers deploy_temp/ 2>/dev/null || true
cp _redirects deploy_temp/ 2>/dev/null || true

# Deploy to Netlify
if command -v netlify &> /dev/null; then
    echo "Deploying to Netlify..."
    cd deploy_temp
    netlify deploy --prod --dir=.
    cd ..
    rm -rf deploy_temp
    echo ""
    echo "✅ Deployment complete!"
else
    echo "⚠️  Netlify CLI not installed"
    echo ""
    echo "To deploy manually:"
    echo "1. Go to https://app.netlify.com/drop"
    echo "2. Drag the 'deploy_temp' folder to the browser"
    echo ""
    echo "Or install Netlify CLI:"
    echo "npm install -g netlify-cli"
fi

echo ""
echo "📱 Complete SaaS Features:"
echo "  ✅ Multi-step onboarding wizard"
echo "  ✅ Google/GitHub OAuth authentication"
echo "  ✅ Team workspace configuration"
echo "  ✅ User profile & preferences"
echo "  ✅ Subscription plan selection"
echo "  ✅ Stripe payment integration"
echo "  ✅ 14-day free trial"
echo "  ✅ Success dashboard redirect"
echo ""
echo "🔐 Authentication configured with:"
echo "  - Supabase backend"
echo "  - Your existing credentials"
echo "  - OAuth providers ready"
echo ""
echo "💳 Payment processing via:"
echo "  - Stripe (test mode configured)"
echo "  - Cryptocurrency option available"
echo ""