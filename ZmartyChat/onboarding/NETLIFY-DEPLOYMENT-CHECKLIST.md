# ✅ Netlify Deployment Checklist for Zmarty Onboarding

## Files Ready for Deployment ✅

Your `/Onboarding/` folder is now **READY FOR NETLIFY**!

### Current Structure:
```
/Onboarding/
├── index.html           ✅ Main onboarding page
├── test-setup.html      ✅ Test page for verification
├── _redirects           ✅ Netlify routing configuration
├── js/
│   ├── supabase-client.js   ✅ Database connections
│   ├── onboarding.js        ✅ Main logic
│   └── analytics.js         ✅ Analytics tracking
└── (original files preserved as backup)
```

## Deploy to Netlify - 3 Methods:

### 🎯 Method 1: Drag and Drop (EASIEST - 30 seconds!)
1. Open https://app.netlify.com/drop
2. Drag your **Onboarding** folder onto the page
3. Wait ~30 seconds for deployment
4. Get your URL instantly!

### 🚀 Method 2: Netlify CLI
```bash
# If not installed:
npm install -g netlify-cli

# From Onboarding folder:
cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/Onboarding
netlify deploy

# For production:
netlify deploy --prod
```

### 🔗 Method 3: GitHub Integration
1. Push to GitHub
2. Connect Netlify to repo
3. Settings:
   - Base directory: `ZmartyChat/Onboarding`
   - Build command: (leave empty)
   - Publish directory: `.`

## ⚙️ After Deployment - IMPORTANT Settings:

### 1. Netlify Environment Variables
Go to: Site settings → Environment variables

Add these:
```
VITE_SUPABASE_AUTH_URL=https://xhskmqsgtdhehzlvtuns.supabase.co
VITE_SUPABASE_DATA_URL=https://asjtxrmftmutcsnqgidy.supabase.co
```

### 2. Update Supabase (ZmartyBrain Project)
Go to: Authentication → URL Configuration

Add your Netlify URL to **Redirect URLs**:
```
https://your-site.netlify.app/verify
https://your-site.netlify.app/auth/callback
https://your-site.netlify.app/dashboard
```

### 3. Update JavaScript Files
After getting your Netlify URL, update in `js/supabase-client.js`:
```javascript
emailRedirectTo: 'https://your-site.netlify.app/verify'
```

## 🧪 Test Your Deployment:

1. **Main Page**: `https://your-site.netlify.app/`
2. **Test Page**: `https://your-site.netlify.app/test-setup.html`

### Test Checklist:
- [ ] Main page loads
- [ ] Can enter email
- [ ] Registration flow works
- [ ] Email verification sent
- [ ] Login flow works
- [ ] Redirects work properly

## 📝 Files Included:

| File | Purpose | Status |
|------|---------|--------|
| `index.html` | Main onboarding slides | ✅ Ready |
| `test-setup.html` | System test page | ✅ Ready |
| `_redirects` | Netlify SPA routing | ✅ Ready |
| `js/supabase-client.js` | Database connections | ✅ Ready |
| `js/onboarding.js` | Onboarding logic | ✅ Ready |
| `js/analytics.js` | User tracking | ✅ Ready |

## 🎉 You're Ready to Deploy!

Just drag the **Onboarding** folder to https://app.netlify.com/drop and you'll have a live URL in 30 seconds!

---

**Path to folder**: `/Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/Onboarding/`

**Support**: If any issues, check:
- Browser console for errors
- Netlify deploy logs
- Supabase logs (Authentication section)