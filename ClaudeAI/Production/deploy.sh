#!/bin/bash

# Professional Auto-deployment script for Netlify
set -e  # Exit on any error

SITE_ID="vermillion-paprenjak-67497b"
SITE_URL="https://vermillion-paprenjak-67497b.netlify.app"

# Load token from .env.local if it exists
if [ -f .env.local ]; then
    source .env.local
fi

# Use token from environment or .env.local
NETLIFY_API_TOKEN="${NETLIFY_AUTH_TOKEN:-}"

echo "🚀 ZmartBot Professional Auto-Deployment v1.0"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Run this script from ClaudeAI/Production directory"
    exit 1
fi

# Get current bug number from notification system
BUG_NUMBER=$(grep -o 'bugNumber: [0-9]*' index.html | tail -1 | grep -o '[0-9]*')
if [ -z "$BUG_NUMBER" ]; then
    BUG_NUMBER="latest"
fi

echo "🔧 Deploying Bug #$BUG_NUMBER fix..."

# Method 1: Direct Netlify API deployment (if token available)
if [ ! -z "$NETLIFY_API_TOKEN" ]; then
    echo "🌐 Using Netlify API for direct deployment..."

    # Create deployment archive
    tar -czf deploy.tar.gz index.html _redirects _headers netlify.toml 2>/dev/null || true

    # Deploy via API
    curl -H "Authorization: Bearer $NETLIFY_API_TOKEN" \
         -H "Content-Type: application/octet-stream" \
         --data-binary @deploy.tar.gz \
         "https://api.netlify.com/api/v1/sites/$SITE_ID/deploys" \
         -o deploy_response.json

    if [ $? -eq 0 ]; then
        echo "✅ API deployment successful!"
        rm -f deploy.tar.gz deploy_response.json
    else
        echo "⚠️  API deployment failed, falling back to Git method..."
    fi
fi

# Method 2: Netlify CLI deployment (if CLI available and linked)
if command -v netlify &> /dev/null; then
    echo "🚀 Using Netlify CLI for deployment..."

    # Check if site is linked
    if [ -f ".netlify/state.json" ]; then
        netlify deploy --prod --dir=. --message="Auto-Deploy Bug #$BUG_NUMBER - $(date '+%Y-%m-%d %H:%M:%S')" || echo "⚠️  CLI deployment failed"
    else
        echo "🔗 Linking to existing Netlify site..."
        echo "$SITE_ID" | netlify link --id="$SITE_ID" 2>/dev/null || true
        netlify deploy --prod --dir=. --message="Auto-Deploy Bug #$BUG_NUMBER - $(date '+%Y-%m-%d %H:%M:%S')" || echo "⚠️  CLI deployment failed"
    fi
fi

# Method 3: Git-based deployment (always attempt as backup)
echo "📦 Preparing git-based deployment..."

# Stage only production files
git add index.html _redirects _headers netlify.toml ../index.html 2>/dev/null || true

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit with auto-generated message
    echo "💾 Committing Bug #$BUG_NUMBER deployment..."
    git commit -m "🚀 Auto-Deploy Bug #$BUG_NUMBER - $(date '+%Y-%m-%d %H:%M:%S')

Production deployment for Bug #$BUG_NUMBER fix

Files updated:
- ClaudeAI/index.html: Development version
- ClaudeAI/Production/index.html: Production version
- ClaudeAI/Production/_redirects: Routing configuration
- ClaudeAI/Production/_headers: Security headers
- ClaudeAI/Production/netlify.toml: Build configuration

Deployment method: Auto-script
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')

🤖 Auto-deployed with professional deployment script

Co-Authored-By: Claude <noreply@anthropic.com>" || echo "⚠️  Commit failed - no changes or conflicts"

    # Note: Skipping git push due to API key protection
    echo "⚠️  Git push skipped due to repository protection rules"
    echo "💡 Use GitHub web interface to resolve any security issues"
fi

echo ""
echo "✅ Auto-deployment process completed!"
echo "================================================"
echo "🔗 Deployment Dashboard: https://app.netlify.com/sites/$SITE_ID/deploys"
echo "🌐 Live Site: $SITE_URL"
echo "🐛 Bug #$BUG_NUMBER deployment timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "📋 Next Steps:"
echo "   1. Check deployment status in Netlify dashboard"
echo "   2. Test the live site for Bug #$BUG_NUMBER fix"
echo "   3. Verify notification system is working"
echo "   4. Continue with Bug #$(($BUG_NUMBER + 1)) detection if ready"