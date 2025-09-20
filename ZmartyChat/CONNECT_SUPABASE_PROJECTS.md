# 🔗 CONNECTING TWO SUPABASE PROJECTS

## Your Architecture:
- **ZmartyBrain** (Users & Auth) - The brain that knows users
- **ZmartBot** (Crypto & Trading) - The knowledge of crypto markets

## ✅ SOLUTION 1: Direct Database Connection (BEST)

### Use Postgres Foreign Data Wrapper (FDW)
This allows one database to query another directly!

1. In ZmartyBrain project, create connection to ZmartBot:
```sql
-- Run in ZmartyBrain SQL Editor
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER zmartbot_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
  host 'db.asjtxrmftmutcsnqgidy.supabase.co',
  port '5432',
  dbname 'postgres'
);

CREATE USER MAPPING FOR postgres
SERVER zmartbot_server
OPTIONS (
  user 'postgres',
  password 'YOUR_ZMARTBOT_DB_PASSWORD'
);

-- Import ZmartBot tables you need
IMPORT FOREIGN SCHEMA public
LIMIT TO (trading_strategies, market_data, bot_configs)
FROM SERVER zmartbot_server
INTO zmartbot;
```

Now you can JOIN across projects:
```sql
SELECT u.email, u.tier, t.strategy_name
FROM users u
JOIN zmartbot.trading_strategies t ON t.user_id = u.id;
```

## ✅ SOLUTION 2: Service-to-Service API Calls

### In your app, use both Supabase clients:
```javascript
// supabase-multi-client.js
const ZMARTYBRAIN_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const ZMARTYBRAIN_KEY = 'your_key';

const ZMARTBOT_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co';
const ZMARTBOT_KEY = 'your_key';

// Create two clients
const brainClient = supabase.createClient(ZMARTYBRAIN_URL, ZMARTYBRAIN_KEY);
const botClient = supabase.createClient(ZMARTBOT_URL, ZMARTBOT_KEY);

// Example: Get user from Brain, trading data from Bot
async function getUserWithTrading(userId) {
    // Get user from ZmartyBrain
    const { data: user } = await brainClient
        .from('users')
        .select('*')
        .eq('id', userId)
        .single();

    // Get trading data from ZmartBot
    const { data: trades } = await botClient
        .from('trades')
        .select('*')
        .eq('user_id', userId);

    return { user, trades };
}
```

## ✅ SOLUTION 3: Shared Service Token

Create a service role that can access both projects:

1. Generate service role keys for both projects
2. Use backend API to coordinate between them
3. Frontend calls your API, API talks to both Supabase projects

```javascript
// backend-api.js
app.get('/api/user-dashboard/:userId', async (req, res) => {
    // Get user from ZmartyBrain (with service key)
    const user = await brainClient.auth.admin.getUserById(userId);

    // Get crypto data from ZmartBot (with service key)
    const cryptoData = await botClient
        .from('portfolio')
        .select('*')
        .eq('user_id', userId);

    res.json({ user, cryptoData });
});
```

## ✅ SOLUTION 4: Real-time Sync with Webhooks

Set up webhooks to sync data between projects:

1. When user registers in ZmartyBrain → webhook creates profile in ZmartBot
2. When trade happens in ZmartBot → webhook updates stats in ZmartyBrain

```javascript
// Webhook endpoint
app.post('/webhook/user-created', async (req, res) => {
    const { user } = req.body;

    // Create corresponding record in ZmartBot
    await botClient.from('traders').insert({
        user_id: user.id,
        email: user.email,
        tier: user.tier
    });
});
```

## 🎯 RECOMMENDED APPROACH:

**For your use case, I recommend Solution 2:**
- Keep user auth in ZmartyBrain
- Keep crypto/trading in ZmartBot
- Use both clients in your app
- Simple, clean separation of concerns

## Implementation Example:

```javascript
// In your app
const UserService = {
    client: brainClient,  // ZmartyBrain for users

    async register(email, password) {
        return await this.client.auth.signUp({ email, password });
    }
};

const TradingService = {
    client: botClient,  // ZmartBot for trading

    async getTradingData(userId) {
        return await this.client.from('trades').select('*').eq('user_id', userId);
    }
};

// Use both together
async function loadDashboard() {
    const user = await UserService.getCurrentUser();
    const trades = await TradingService.getTradingData(user.id);
    return { user, trades };
}
```

## Which solution do you prefer?
1. **FDW** - Direct database connection (most powerful)
2. **Dual Clients** - Two Supabase clients (simplest)
3. **Backend API** - Central API manages both (most secure)
4. **Webhooks** - Real-time sync (best for events)