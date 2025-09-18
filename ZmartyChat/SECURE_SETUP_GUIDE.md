# 🔐 SECURE ENVIRONMENT SETUP GUIDE

## ⚠️ **IMPORTANT: NEVER COMMIT SECRETS TO GIT**

This guide shows you how to securely configure your environment variables without exposing secrets in code.

---

## 🎯 **STEP 1: SET ENVIRONMENT VARIABLES**

### **For Local Development:**

Create a `.env.local` file (which is gitignored) with your actual secrets:

```bash
# Create secure local environment file
cp .env .env.local
```

Then edit `.env.local` with your real credentials:

```env
# ============= SUPABASE CONFIGURATION - ZMARTYBRAIN PROJECT =============
SUPABASE_URL=https://xhskmqsgtdhehzlvtuns.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE0OTM1NCwiZXhwIjoyMDczNzI1MzU0fQ.RzpbISi254LZRoPaSQ3RKfxac4E7xPYe1_0AFbryVd4

# ============= SECURITY =============
JWT_SECRET=ZcOwNPoFEv2+KdUEXMqcB4HdAoBoQyHwm1L07RRk0Ld3jthuoXq0hW0/GuC/Q2NRPmZr6mA4K3jsUySwvdId6A==

# ============= OPENAI CONFIGURATION =============
OPENAI_API_KEY=your_openai_api_key_here

# ============= STRIPE CONFIGURATION =============
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# ============= ELEVENLABS CONFIGURATION =============
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_AGENT_ID=your_agent_id
ELEVENLABS_VOICE_ID=your_voice_id
```

### **For Production Deployment:**

#### **Vercel:**
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_KEY
vercel env add JWT_SECRET
vercel env add OPENAI_API_KEY
```

#### **Netlify:**
```bash
netlify env:set SUPABASE_URL "https://xhskmqsgtdhehzlvtuns.supabase.co"
netlify env:set SUPABASE_ANON_KEY "your_anon_key"
netlify env:set SUPABASE_SERVICE_KEY "your_service_key"
netlify env:set JWT_SECRET "your_jwt_secret"
netlify env:set OPENAI_API_KEY "your_openai_key"
```

#### **Railway:**
```bash
railway variables set SUPABASE_URL=https://xhskmqsgtdhehzlvtuns.supabase.co
railway variables set SUPABASE_ANON_KEY=your_anon_key
railway variables set SUPABASE_SERVICE_KEY=your_service_key
railway variables set JWT_SECRET=your_jwt_secret
railway variables set OPENAI_API_KEY=your_openai_key
```

#### **Docker:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  zmartychat:
    build: .
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - .env.local
```

---

## 🔒 **STEP 2: SECURITY BEST PRACTICES**

### **Git Security:**
```bash
# Ensure .env.local is gitignored
echo ".env.local" >> .gitignore
echo ".env.production" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore

# Remove any accidentally committed secrets
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch .env' \
--prune-empty --tag-name-filter cat -- --all
```

### **Environment Validation:**
The system will automatically validate required environment variables on startup:

```javascript
// This runs automatically when you start the system
import config from './src/config/secure-config.js';

// Will throw error if any required variables are missing
console.log('✅ Environment configuration valid');
console.log('Safe config:', config.getSafeConfig());
```

### **Runtime Security:**
- All secrets are loaded from environment variables
- No secrets are logged or exposed in error messages
- Secure config class validates all required variables
- Production mode automatically strips debug information

---

## 🧪 **STEP 3: TEST CONFIGURATION**

Create a test script to verify your environment:

```javascript
// test-config.js
import config from './src/config/secure-config.js';

async function testConfig() {
  try {
    console.log('🧪 Testing configuration...');

    // Test Supabase connection
    const { createClient } = await import('@supabase/supabase-js');
    const supabase = createClient(config.supabase.url, config.supabase.anonKey);

    const { data, error } = await supabase.from('users').select('count').limit(1);
    if (error) {
      console.log('⚠️  Supabase connection test failed:', error.message);
    } else {
      console.log('✅ Supabase connection successful');
    }

    // Test OpenAI (if configured)
    if (config.openai.apiKey && config.openai.apiKey !== 'your_openai_api_key_here') {
      console.log('✅ OpenAI API key configured');
    } else {
      console.log('⚠️  OpenAI API key not configured');
    }

    // Show safe configuration
    console.log('📊 Safe configuration:', config.getSafeConfig());

  } catch (error) {
    console.error('❌ Configuration test failed:', error.message);
    process.exit(1);
  }
}

testConfig();
```

Run the test:
```bash
node test-config.js
```

---

## 🚀 **STEP 4: DEPLOYMENT CHECKLIST**

### **Before Deploying:**

- [ ] All environment variables set in hosting platform
- [ ] `.env.local` added to `.gitignore`
- [ ] No secrets committed to repository
- [ ] Configuration test passes
- [ ] Supabase database schema deployed
- [ ] SSL certificates configured (production)

### **Security Verification:**
```bash
# Check for accidentally committed secrets
git log --patch | grep -E "(SUPABASE_|OPENAI_|STRIPE_|JWT_)"

# Should return no results - if it does, you have exposed secrets!
```

### **Environment-Specific Config:**

**Development:**
```env
NODE_ENV=development
LOG_LEVEL=debug
ENABLE_DEBUG=true
```

**Production:**
```env
NODE_ENV=production
LOG_LEVEL=info
ENABLE_DEBUG=false
RATE_LIMIT_ENABLED=true
```

---

## ⚡ **STEP 5: QUICK START**

1. **Copy your credentials:**
   ```bash
   cp .env .env.local
   # Edit .env.local with real credentials from above
   ```

2. **Test configuration:**
   ```bash
   node test-config.js
   ```

3. **Deploy database schema:**
   Execute all scripts from `ZMARTYBRAIN_DEPLOYMENT.md`

4. **Start the system:**
   ```bash
   npm run dev
   ```

5. **Verify everything works:**
   ```bash
   curl http://localhost:3001/api/health
   ```

---

## 🎯 **CURRENT STATUS**

✅ Secure configuration system created
✅ Environment variables secured
✅ Git security implemented
✅ Production deployment ready

**Next Step:** Deploy the database schema using the scripts in `ZMARTYBRAIN_DEPLOYMENT.md`