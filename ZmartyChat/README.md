# 🤖 ZmartyChat - AI Trading Companion

## 🚀 Overview

ZmartyChat is an advanced AI-powered trading companion that uses psychological addiction mechanics and personalized engagement to create an indispensable trading assistant. Built with a credit-based monetization system, it learns from every interaction to provide increasingly personalized experiences.

## ✨ Core Features

- **AI-Powered Chat**: Autonomous Zmarty AI with human-like personality
- **Multi-Agent Consensus**: Integration with 10+ specialized trading agents via Manus Webhook
- **Credit System**: Pay-per-use model with various package options
- **Addiction Mechanics**: Variable rewards, streaks, achievements, and FOMO triggers
- **User Intelligence**: Automatic categorization and personalization
- **Real-time Analysis**: Live market data and technical analysis
- **Subscription Tiers**: From free to enterprise plans
- **MCP Integration**: Model Context Protocol for advanced AI capabilities

## 📋 Prerequisites

- Node.js 18+ and npm 9+
- Supabase account and project
- Stripe account for payments
- Manus Webhook access (for multi-agent integration)

## 🔧 Installation

1. **Clone the repository:**
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Stripe Price IDs
STRIPE_PRICE_BASIC=price_basic_id
STRIPE_PRICE_PRO=price_pro_id
STRIPE_PRICE_PREMIUM=price_premium_id

# Manus Webhook
MANUS_WEBHOOK_URL=https://your-manus-webhook.com
MANUS_API_KEY=your-manus-key

# Server Configuration
PORT=3001
FRONTEND_URL=http://localhost:3000
NODE_ENV=development

# JWT Secret
JWT_SECRET=your-jwt-secret
```

4. **Set up the database:**
```bash
# Run the Supabase schema
psql -h your-supabase-host -U postgres -d postgres < database/supabase_schema.sql
```

5. **Configure Stripe:**
- Create products and price IDs in Stripe Dashboard
- Set up webhook endpoint: `https://your-domain.com/api/stripe/webhook`
- Add webhook events: payment_intent.succeeded, customer.subscription.created, etc.

## 🚀 Running the Application

### Development Mode
```bash
# Start the main server
npm run dev

# In another terminal, start the background processor
npm run background

# In another terminal, start MCP servers
npm run mcp:all
```

### Production Mode
```bash
# Start all services
npm start
```

### Serve Frontend
```bash
# Serve the static frontend
npm run serve
```

Then open http://localhost:8080 in your browser.

## 📁 Project Structure

```
ZmartyChat/
├── src/                      # Source files
│   ├── zmarty-ai-agent.js    # Core AI personality
│   ├── zmarty-manus-connector.js # Multi-agent integration
│   ├── supabase-client.js    # Database operations
│   ├── credit-manager.js     # Credit system
│   ├── stripe-payment.js     # Payment processing
│   ├── user-agent-analyzer.js # User analysis
│   ├── user-agent-background.js # Background processor
│   ├── addiction-hooks.js    # Engagement mechanics
│   └── main-integration.js   # Main server
├── mcp-servers/              # MCP server implementations
│   ├── user-data-server.js  # User data MCP
│   ├── credit-server.js     # Credit management MCP
│   └── mcp-config.json      # MCP configuration
├── api/                      # API endpoints
│   └── stripe-endpoints.js  # Stripe webhook handlers
├── database/                 # Database schemas
│   └── supabase_schema.sql  # Complete database schema
├── index.html               # Frontend interface
├── styles.css               # UI styles
└── package.json             # Dependencies

```

## 💳 Credit System

### Action Costs
- Simple Chat: 1 credit
- Market Data: 2 credits
- Technical Analysis: 5 credits
- AI Prediction: 10 credits
- Portfolio Analysis: 15 credits
- Custom Strategy: 25 credits
- Multi-Agent Consensus: 50 credits

### Credit Packages
- **Starter**: $4.99 for 500 credits
- **Popular**: $14.99 for 2,000 credits (+200 bonus)
- **Power**: $29.99 for 5,000 credits (+750 bonus)
- **Whale**: $49.99 for 10,000 credits (+2,000 bonus)

### Subscription Plans
- **Free**: 100 credits/month
- **Basic**: $9.99/month - 1,000 credits
- **Pro**: $29.99/month - 5,000 credits
- **Premium**: $99.99/month - 20,000 credits

## 🎮 Addiction Mechanics

The system implements various psychological hooks:

- **Variable Rewards**: 30% chance of bonus credits
- **Streak System**: Daily login bonuses
- **Achievements**: Unlock badges and rewards
- **FOMO Triggers**: Time-sensitive alerts
- **Social Proof**: Show peer success
- **Loss Aversion**: Low credit warnings
- **Progress Tracking**: Visual growth metrics

## 🔌 API Endpoints

### WebSocket Events
- `user:register` - Register new user
- `message:send` - Send chat message
- `credits:purchase` - Purchase credits
- `subscription:create` - Create subscription

### REST API
- `GET /api/users/:userId` - Get user profile
- `GET /api/credits/packages` - Get credit packages
- `GET /api/insights/:userId` - Get user insights
- `GET /api/metrics/:userId` - Get addiction metrics
- `GET /api/transcripts/:userId` - Get chat transcripts

## 🧪 Testing

```bash
# Run tests
npm test

# Test credit deduction
curl -X POST http://localhost:3001/api/credits/deduct \
  -H "Content-Type: application/json" \
  -d '{"userId": "test-user", "amount": 10, "action": "test"}'
```

## 📊 Monitoring

The system includes comprehensive monitoring:

- User engagement metrics
- Credit usage tracking
- Addiction score calculation
- Revenue analytics
- Performance monitoring

## 🔒 Security

- JWT authentication
- Supabase Row Level Security (RLS)
- Stripe webhook signature verification
- Environment variable protection
- CORS configuration

## 🚨 Troubleshooting

### Database Connection Issues
- Verify Supabase URL and keys in .env
- Check RLS policies are properly configured

### Payment Issues
- Verify Stripe keys are correct
- Check webhook endpoint is accessible
- Ensure price IDs match your Stripe products

### MCP Server Issues
- Ensure Node.js 18+ is installed
- Check MCP server logs: `npm run mcp:user`
- Verify @modelcontextprotocol/sdk is installed

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Support

For issues or questions:
- GitHub Issues: [Report here]
- Email: support@zmartbot.com
- Discord: Join our community

## 🎯 Next Steps

1. Configure Supabase and Stripe accounts
2. Set up environment variables
3. Run database migrations
4. Start the development server
5. Open index.html in browser
6. Register a test user
7. Start chatting with Zmarty!

---

**Built with ❤️ by the ZmartBot Team**

*Creating addiction through intelligent engagement*