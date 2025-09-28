#!/bin/bash

# Deploy ZmartyBrain Onboarding to Netlify
echo "🚀 Deploying to MANUAL-DEPLOY-100-PERCENT..."

# Create deployment package
echo "📦 Preparing deployment files..."

# Create a clean deployment directory
rm -rf deploy-package
mkdir -p deploy-package

# Copy essential files
cp index.html deploy-package/
cp manifest.json deploy-package/
cp service-worker.js deploy-package/

# Create a simple favicon to avoid 404
echo '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><text x="50%" y="50%" font-size="12" text-anchor="middle" dominant-baseline="middle">ZB</text></svg>' > deploy-package/favicon.ico

# Create deployment instructions
cat > deploy-package/README.md << 'EOF'
# ZmartyBrain Onboarding - Production Ready

## Deploy to Netlify:
1. Go to https://app.netlify.com/drop
2. Drag this entire folder to deploy
3. Your site will be live at the provided URL

## Database Setup:
Run FINAL-FIX-V2.sql in Supabase SQL Editor

## Features:
- ✅ 9-step onboarding flow
- ✅ Email & OAuth authentication
- ✅ PWA support
- ✅ Fully responsive
- ✅ Accessibility compliant
EOF

echo "✅ Deployment package ready in ./deploy-package/"
echo "📍 Next steps:"
echo "   1. Open https://app.netlify.com/drop"
echo "   2. Drag the 'deploy-package' folder to deploy"
echo "   3. Run FINAL-FIX-V2.sql in Supabase"

# Open Netlify drop in browser
open https://app.netlify.com/drop 2>/dev/null || echo "   Visit: https://app.netlify.com/drop"