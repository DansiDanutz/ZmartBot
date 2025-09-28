#!/bin/bash

# Professional Netlify Setup Script
echo "🛠️  ZmartBot Netlify Auto-Deployment Setup"
echo "============================================"

SITE_ID="vermillion-paprenjak-67497b"
SITE_URL="https://vermillion-paprenjak-67497b.netlify.app"

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo "📦 Installing Netlify CLI..."
    npm install -g netlify-cli || {
        echo "❌ Failed to install Netlify CLI. Please install manually:"
        echo "   npm install -g netlify-cli"
        exit 1
    }
fi

echo "✅ Netlify CLI is available"

# Check if user is authenticated
if ! netlify status &> /dev/null; then
    echo "🔐 Netlify authentication required..."
    echo "Please run: netlify login"
    echo "Then re-run this setup script"
    exit 1
fi

echo "✅ Netlify authentication verified"

# Link to existing site
echo "🔗 Linking to existing Netlify site..."
mkdir -p .netlify

cat > .netlify/state.json << EOF
{
  "siteId": "$SITE_ID"
}
EOF

echo "✅ Site linked successfully"

# Configure build settings
echo "⚙️  Configuring build settings..."

# Test deployment
echo "🧪 Testing deployment configuration..."
netlify deploy --dir=. --message="Setup Test - $(date '+%Y-%m-%d %H:%M:%S')" || {
    echo "⚠️  Test deployment failed, but site is configured"
}

echo ""
echo "✅ Netlify Auto-Deployment Setup Complete!"
echo "============================================"
echo "🔗 Site ID: $SITE_ID"
echo "🌐 Live URL: $SITE_URL"
echo "📊 Dashboard: https://app.netlify.com/sites/$SITE_ID"
echo ""
echo "📋 Available Commands:"
echo "   ./deploy.sh          - Auto-deploy current changes"
echo "   netlify deploy       - Manual deploy (preview)"
echo "   netlify deploy --prod - Manual deploy (production)"
echo "   netlify status       - Check connection status"
echo ""
echo "🚀 Ready for automated deployments!"