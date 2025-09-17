# Zmarty Interactive Dashboard

A comprehensive cryptocurrency trading dashboard with AI-powered Zmarty assistant and credit-based interaction system.

## 🏗️ Architecture

### Backend (FastAPI)
- **Database Models**: PostgreSQL with SQLAlchemy ORM
- **Credit System**: Flexible credit-based pricing for AI interactions  
- **Authentication**: JWT-based auth with refresh tokens
- **WebSocket**: Real-time chat communication
- **AI Integration**: OpenAI GPT-4 powered Zmarty assistant

### Frontend (React + TypeScript)
- **Components**: Modern UI with Radix UI and Tailwind CSS
- **State Management**: Zustand for global state
- **Real-time**: Socket.IO client for WebSocket communication
- **MCP Integration**: Figma design tokens and assets via MCP server
- **Charts**: Trading visualizations with Recharts

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- PostgreSQL 14+
- Redis (for WebSocket sessions)

### Backend Setup

1. **Create virtual environment**:
```bash
cd zmarty-dashboard/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install fastapi[all] sqlalchemy[asyncio] asyncpg alembic
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install openai redis stripe
```

3. **Environment configuration**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Database setup**:
```bash
# Create database
createdb zmarty_dashboard

# Run migrations
alembic upgrade head
```

5. **Start backend**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd zmarty-dashboard/frontend
npm install
```

2. **Environment configuration**:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. **Start development server**:
```bash
npm run dev
```

### MCP Server Setup (Optional)

For Figma integration, set up MCP server:

1. **Install MCP dependencies**:
```bash
npm install -g @figma/mcp-server
```

2. **Configure MCP server**:
```bash
# Add to ~/.cursor/mcp.json
{
  "servers": {
    "figma": {
      "command": "figma-mcp-server",
      "args": ["--token", "YOUR_FIGMA_TOKEN"]
    }
  }
}
```

## 📁 Project Structure

```
zmarty-dashboard/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── core/
│   │   ├── config.py          # Settings & environment
│   │   └── database.py        # Database connection
│   ├── models/
│   │   └── database.py        # SQLAlchemy models
│   ├── services/
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── credit_service.py  # Credit management
│   │   └── zmarty_service.py  # AI interaction logic
│   ├── api/v1/
│   │   ├── auth.py           # Auth endpoints
│   │   ├── credits.py        # Credit endpoints
│   │   ├── zmarty.py         # AI endpoints
│   │   └── websocket.py      # WebSocket handlers
│   └── schemas/
│       ├── auth.py           # Pydantic models
│       └── credits.py        # Credit schemas
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/     # Main dashboard components
│   │   │   ├── ui/           # Reusable UI components
│   │   │   └── Auth/         # Authentication components
│   │   ├── hooks/
│   │   │   ├── useMCP.ts     # MCP integration hooks
│   │   │   └── useAuth.ts    # Authentication hooks
│   │   ├── services/
│   │   │   ├── api.ts        # API client
│   │   │   ├── mcp.ts        # MCP service
│   │   │   └── websocket.ts  # WebSocket client
│   │   ├── stores/
│   │   │   └── authStore.ts  # Zustand auth store
│   │   └── types/
│   │       └── index.ts      # TypeScript definitions
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🔑 Key Features

### Credit System
- **Flexible Pricing**: Different credit costs per request type
- **Package System**: Starter, Professional, Enterprise tiers
- **Usage Analytics**: Detailed credit usage tracking
- **Refund Protection**: Automatic refunds on system failures

### AI Assistant (Zmarty)
- **Multiple Query Types**: 
  - Basic queries (1 credit)
  - Market analysis (3 credits) 
  - Trading strategies (5 credits)
  - AI predictions (8 credits)
  - Live signals (10 credits)
  - Custom research (25 credits)
- **Context Awareness**: Tailored responses based on user tier and history
- **Quality Ratings**: User feedback system for continuous improvement

### Real-time Features
- **WebSocket Chat**: Instant messaging with Zmarty
- **Live Updates**: Real-time credit balance and system status
- **Typing Indicators**: Enhanced chat experience
- **Connection Management**: Automatic reconnection and heartbeat

### MCP Integration
- **Design Tokens**: Automatic Figma design system sync
- **Asset Management**: Direct asset serving from Figma
- **Brand Consistency**: Single source of truth for UI elements
- **Performance**: Cached asset delivery with fallbacks

## 📊 API Endpoints

### Authentication
```
POST   /api/v1/auth/register    # User registration
POST   /api/v1/auth/login       # User login
POST   /api/v1/auth/refresh     # Token refresh
GET    /api/v1/auth/me          # Current user info
```

### Credits
```
GET    /api/v1/credits/balance           # Get credit balance
GET    /api/v1/credits/packages          # Available packages
POST   /api/v1/credits/purchase          # Purchase credits
GET    /api/v1/credits/transactions      # Transaction history
GET    /api/v1/credits/usage-stats       # Usage analytics
```

### Zmarty AI
```
POST   /api/v1/zmarty/query              # Main AI interaction
GET    /api/v1/zmarty/requests           # Request history
GET    /api/v1/zmarty/requests/{id}      # Specific request
POST   /api/v1/zmarty/rate/{id}          # Rate response
GET    /api/v1/zmarty/trending           # Trending queries
```

### WebSocket
```
WS     /ws/chat/{token}                  # Real-time chat
GET    /ws/stats                         # Connection stats
```

## 🎨 Component Library

### Dashboard Components
- `<ZmartyChat />` - Main AI chat interface
- `<CreditBalance />` - Credit display and management
- `<TradingPanel />` - Market data and charts  
- `<PerformanceMetrics />` - User analytics
- `<RequestHistory />` - Query history table

### UI Components (Radix UI)
- Fully accessible component library
- Consistent design system
- Dark/light theme support
- Mobile responsive

## 🔧 Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/zmarty_dashboard

# JWT Authentication  
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
ZMARTY_API_KEY=your-openai-api-key
ZMARTY_MODEL=gpt-4-turbo

# Stripe (Payment Processing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Redis
REDIS_URL=redis://localhost:6379

# MCP
MCP_FIGMA_SERVER_URL=http://localhost:3001
```

### Frontend (.env.local)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_MCP_ENABLED=true
```

## 🚦 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 . && black . && isort .

# Frontend linting
cd frontend
npm run lint && npm run type-check
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📈 Monitoring

### Health Checks
- `GET /health` - API health status
- `GET /ws/stats` - WebSocket statistics
- Built-in Prometheus metrics

### Logging
- Structured JSON logging
- Error tracking with Sentry integration
- Performance monitoring

## 🔒 Security

### Authentication
- JWT tokens with refresh mechanism
- Password hashing with bcrypt
- Rate limiting on endpoints

### Data Protection
- SQL injection prevention
- XSS protection
- CORS configuration
- Environment-based secrets

## 🎯 Credit System Details

### Pricing Tiers
| Request Type | Credits | Description |
|-------------|---------|-------------|
| Basic Query | 1 | Simple market questions |
| Market Analysis | 3 | Technical analysis |
| Trading Strategy | 5 | Strategy recommendations |
| AI Predictions | 8 | Price predictions |
| Live Signals | 10 | Real-time alerts |
| Custom Research | 25 | Deep analysis |

### Purchase Packages
| Package | Credits | Price | Bonus |
|---------|---------|-------|--------|
| Starter | 100 | $9.99 | 0% |
| Professional | 500 | $39.99 | 25% |
| Enterprise | 2000 | $149.99 | 50% |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)  
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [docs.zmarty.com](https://docs.zmarty.com)
- Email: support@zmarty.com
- Discord: [discord.gg/zmarty](https://discord.gg/zmarty)
- Issues: [GitHub Issues](https://github.com/zmarty/dashboard/issues)

---

**Built with ❤️ by the Zmarty Team**