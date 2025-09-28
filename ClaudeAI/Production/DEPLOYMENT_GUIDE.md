# 🚀 ZmartBot Professional Auto-Deployment Guide

## Overview
This guide explains how to set up automatic deployment from GitHub to Netlify for the ZmartBot onboarding system.

## Repository Structure
```
ZmartBot/
├── ClaudeAI/
│   ├── index.html              # Development version
│   └── Production/
│       ├── index.html          # Production version
│       ├── netlify.toml        # Build configuration
│       ├── _redirects          # URL routing
│       ├── _headers           # Security headers
│       ├── deploy.sh          # Auto-deployment script
│       └── setup-netlify.sh   # Initial setup script
```

## Configuration Files

### netlify.toml
Professional Netlify configuration with:
- **Base Directory**: `ClaudeAI/Production`
- **Publish Directory**: `.` (current directory)
- **Build Command**: None (static HTML)
- **Processing**: CSS/JS minification, image compression

### _redirects
- SPA routing fallback to index.html
- All routes redirect to `/index.html` with 200 status

### _headers
- Security headers (X-Frame-Options, CSP, etc.)
- Supabase and Google OAuth domain allowlisting

## Setup Instructions

### 1. Netlify Dashboard Configuration
1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Navigate to your site: `vermillion-paprenjak-67497b`
3. Go to **Site settings > Build & deploy > Continuous Deployment**
4. Configure:
   - **Repository**: `https://github.com/DansiDanutz/ZmartBot`
   - **Branch**: `simple-setup`
   - **Base directory**: `ClaudeAI/Production`
   - **Build command**: (leave empty)
   - **Publish directory**: `.`

### 2. GitHub Integration
The auto-deployment works through GitHub integration:
- Push to `simple-setup` branch triggers deployment
- Only changes in `ClaudeAI/` directory trigger builds
- Netlify reads `netlify.toml` for configuration

### 3. Local CLI Setup (Optional)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Authenticate
netlify login

# Link to existing site
cd ClaudeAI/Production
./setup-netlify.sh
```

## Deployment Methods

### Method 1: Git Push (Recommended)
```bash
# Make changes to ClaudeAI/index.html
# Copy to Production directory
cp ../index.html .

# Commit and push
git add .
git commit -m "🚀 Deploy Bug #X fix"
git push origin simple-setup
```

### Method 2: Auto-Script
```bash
cd ClaudeAI/Production
./deploy.sh
```

### Method 3: Manual CLI
```bash
cd ClaudeAI/Production
netlify deploy --prod --message="Manual deployment"
```

## Workflow Integration

### Bug Fix Deployment Loop
1. **Develop**: Edit `ClaudeAI/index.html`
2. **Test**: Local testing and verification
3. **Deploy**: Copy to Production and commit
4. **Auto-Deploy**: Netlify detects push and deploys
5. **Verify**: Test live site for bug fixes
6. **Iterate**: Continue to next bug

### Notification System
- Each deployment shows bug fix notifications
- Notifications include bug number, description, and details
- localStorage tracks latest deployed bug number

## Configuration Details

### Build Settings
- **Framework**: None (static HTML)
- **Build Command**: Empty (no build required)
- **Node Version**: 18 (for potential tooling)
- **Processing**: Enabled for optimization

### Security
- Content Security Policy configured for Supabase
- Frame protection and XSS prevention
- HTTPS enforcement and secure headers

### Performance
- CSS/JS minification enabled
- Image compression enabled
- CDN distribution through Netlify

## Troubleshooting

### Common Issues
1. **Build fails**: Check `netlify.toml` syntax
2. **404 errors**: Verify `_redirects` configuration
3. **Security errors**: Check `_headers` CSP rules
4. **Deploy not triggered**: Verify GitHub integration

### Debug Commands
```bash
# Check site status
netlify status

# View build logs
netlify logs

# Test deploy locally
netlify dev

# Manual deploy preview
netlify deploy --dir=. --message="Debug test"
```

## Monitoring

### Deployment URLs
- **Live Site**: https://vermillion-paprenjak-67497b.netlify.app
- **Dashboard**: https://app.netlify.com/sites/vermillion-paprenjak-67497b
- **Deploy Logs**: https://app.netlify.com/sites/vermillion-paprenjak-67497b/deploys

### Success Indicators
- ✅ Green deploy status in Netlify dashboard
- ✅ Site loads without errors
- ✅ Bug notification displays correctly
- ✅ All authentication flows work

## Advanced Configuration

### Environment Variables
Set in Netlify dashboard if needed:
- API tokens for external services
- Feature flags for different environments

### Deploy Contexts
- **Production**: Live site from `simple-setup` branch
- **Deploy Previews**: PR-based deployments
- **Branch Deploys**: Other branch deployments

### Ignore Builds
Configure to only build on relevant changes:
```toml
[build]
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- . ':!*.md'"
```

## Support
- **Documentation**: [Netlify Docs](https://docs.netlify.com)
- **Status**: [Netlify Status](https://www.netlifystatus.com)
- **Support**: [Netlify Support](https://answers.netlify.com)

---
*Generated for ZmartBot Professional Deployment System*