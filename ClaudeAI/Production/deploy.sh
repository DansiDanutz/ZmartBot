#!/bin/bash

# Auto-deployment script for Netlify
echo "🚀 Starting auto-deployment to Netlify..."

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Run this script from ClaudeAI/Production directory"
    exit 1
fi

# Add and commit changes
echo "📦 Adding changes to git..."
git add .
git add ../index.html

# Get current bug number from notification system
BUG_NUMBER=$(grep -o 'bugNumber: [0-9]*' index.html | tail -1 | grep -o '[0-9]*')
if [ -z "$BUG_NUMBER" ]; then
    BUG_NUMBER="unknown"
fi

# Commit with auto-generated message
echo "💾 Committing Bug #$BUG_NUMBER deployment..."
git commit -m "🚀 Auto-Deploy Bug #$BUG_NUMBER - $(date '+%Y-%m-%d %H:%M:%S')

Auto-deployment triggered for Bug #$BUG_NUMBER fix

Files updated:
- ClaudeAI/index.html
- ClaudeAI/Production/index.html

🤖 Auto-deployed with deployment script

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to trigger Netlify deployment
echo "🌐 Pushing to GitHub to trigger Netlify deployment..."
git push origin simple-setup

# Check if Netlify CLI is available for direct deployment
if command -v netlify &> /dev/null; then
    echo "🚀 Triggering direct Netlify deployment..."
    netlify deploy --prod --dir=. --message="Auto-Deploy Bug #$BUG_NUMBER"
else
    echo "💡 Netlify CLI not found. Using GitHub trigger method."
    echo "📋 Deployment will be triggered automatically via GitHub integration."
fi

echo "✅ Auto-deployment process completed!"
echo "🔗 Check deployment status at: https://app.netlify.com/sites/vermillion-paprenjak-67497b/deploys"
echo "🌐 Live site: https://vermillion-paprenjak-67497b.netlify.app"