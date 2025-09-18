# 🚀 ZmartyChat Quick Start Guide

## 📦 Prerequisites Check

Before starting, ensure you have:
- ✅ Node.js 18+ installed
- ✅ npm 9+ installed
- ✅ Supabase account (free tier works)
- ✅ Stripe account (test mode is fine)
- ✅ Git installed

## 🎯 5-Minute Setup

### Step 1: Run Automated Setup
```bash
# Navigate to ZmartyChat directory
cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat

# Run the setup script
./setup.sh
```

The script will:
- Check Node.js version
- Install dependencies
- Create .env from template
- Guide you through configuration
- Set up directories
- Generate security keys

### Step 2: Configure Supabase

1. **Create a Supabase Project:**
   - Go to [https://supabase.com](https://supabase.com)
   - Click "New project"
   - Name it "zmartychat"
   - Wait for provisioning (~2 minutes)

2. **Get your credentials:**
   - Go to Settings → API
   - Copy:
     - Project URL → `SUPABASE_URL` in .env
     - anon/public key → `SUPABASE_ANON_KEY` in .env
     - service_role key → `SUPABASE_SERVICE_KEY` in .env

3. **Run the database migration:**

   **Option A: Using SQL Editor (Recommended)**
   - Go to SQL Editor in Supabase dashboard
   - Click "New query"
   - Copy entire contents of `database/supabase_schema.sql`
   - Click "Run"

   **Option B: Using migration script**
   ```bash
   npm run db:migrate
   ```

4. **Verify tables were created:**
   - Go to Table Editor in Supabase
   - You should see 15+ tables including:
     - users
     - credit_transactions
     - user_categories
     - addiction_metrics

### Step 3: Configure Stripe (Optional for Testing)

For testing, you can skip Stripe and use mock mode. For real payments:

1. **Get test API keys:**
   - Go to [https://dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)
   - Copy:
     - Publishable key → `STRIPE_PUBLISHABLE_KEY`
     - Secret key → `STRIPE_SECRET_KEY`

2. **Create products (optional):**
   ```bash
   # Products will be created automatically
   # Or create manually in Stripe Dashboard
   ```

3. **Set up webhook (for production):**
   - Go to Webhooks in Stripe
   - Add endpoint: `https://your-domain.com/api/stripe/webhook`
   - Select events:
     - payment_intent.succeeded
     - customer.subscription.created
     - customer.subscription.deleted

### Step 4: Start the Application

Open 3 terminal windows:

**Terminal 1: Main Server**
```bash
npm run dev
# Server starts on http://localhost:3001
```

**Terminal 2: Background Processor**
```bash
npm run background
# Processes user messages and generates insights
```

**Terminal 3: Frontend**
```bash
npm run serve
# UI available at http://localhost:8080
```

### Step 5: Test the System

1. **Open the app:**
   - Navigate to [http://localhost:8080](http://localhost:8080)

2. **Register a user:**
   - Click "Get Started"
   - Enter name, email/phone
   - You'll receive 100 free credits

3. **Test Zmarty:**
   - Type: "Hey Zmarty, what's Bitcoin at?"
   - Zmarty should respond with market data
   - Check credits were deducted (2 credits)

4. **Test credit system:**
   - Type: "Check my credits"
   - Should show 98 credits remaining

## 🔧 Configuration Options

### Environment Variables

**Minimal Setup (for testing):**
```env
# Just these 3 are required to start
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
JWT_SECRET=any_random_string
```

**Full Setup:**
See `.env.example` for all options

### Feature Flags

Enable/disable features in `.env`:
```env
ENABLE_VOICE_CHAT=false  # Disable ElevenLabs
ENABLE_MULTI_AGENT=false # Disable Manus agents
ENABLE_ADDICTION_HOOKS=true # Keep engagement features
```

## 🚨 Common Issues & Solutions

### Issue: "Cannot connect to Supabase"
**Solution:** Check your SUPABASE_URL doesn't have trailing slash

### Issue: "Credits not deducting"
**Solution:** Ensure RLS policies are enabled in Supabase

### Issue: "Manus agents not responding"
**Solution:** Manus is optional. Set `ENABLE_MULTI_AGENT=false`

### Issue: "Port 3001 already in use"
**Solution:** Change PORT in .env to 3002 or another free port

### Issue: "npm install fails"
**Solution:** Clear npm cache: `npm cache clean --force`

## 📊 Verify Everything Works

Run the health check:
```bash
curl http://localhost:3001/health
```

Should return:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "ai": "ready",
    "payment": "configured",
    "mcp": "running"
  }
}
```

## 🎮 Quick Test Commands

Test credit deduction:
```bash
curl -X POST http://localhost:3001/api/credits/deduct \
  -H "Content-Type: application/json" \
  -d '{"userId": "test", "amount": 5, "action": "test"}'
```

Test market data:
```bash
curl http://localhost:3001/api/market/BTC
```

## 🚀 Next Steps

1. **Set up production:**
   - Use PM2 for process management
   - Set up SSL with Let's Encrypt
   - Configure domain name
   - Set `NODE_ENV=production`

2. **Configure ElevenLabs (optional):**
   - Follow `elevenlabs-config/ELEVENLABS_SETUP.md`
   - Add voice capabilities

3. **Connect Manus agents:**
   - Ensure Manus webhook is running
   - Update `MANUS_WEBHOOK_URL` in .env

4. **Monitor the system:**
   - Check logs in `logs/` directory
   - Monitor Supabase dashboard
   - Track Stripe transactions

## 💡 Tips

- Start with free tiers for all services
- Test thoroughly before enabling payments
- Monitor credit usage to prevent abuse
- Use addiction hooks ethically
- Keep user data secure

## 📞 Support

- Check README.md for detailed docs
- Review logs for debugging
- Supabase Discord for database help
- Stripe Discord for payment issues

---

**You're ready to go! 🎉**

Your ZmartyChat system is now operational. Start chatting with Zmarty and watch the credits flow!