# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

ZmartBot is an enterprise-grade cryptocurrency trading platform with multi-agent architecture, combining multiple data sources for automated trading decisions.

## Architecture & Key Components

### Multi-Agent System
- **Orchestration Agent**: Central coordinator (`src/agents/orchestration/`)
- **Scoring Agent**: Signal aggregation with dynamic weighting (`src/agents/scoring/`)
- **Risk Guard Agent**: Position management and circuit breakers (`src/agents/risk_guard/`)
- **Signal Generator Agent**: Technical analysis (`src/agents/signal_generator/`)
- **Database Agent**: RiskMetric calculations (`src/agents/database/`)

### Data Sources & Integrations
- **Cryptometer API**: 17 endpoints for market data (70% weight)
- **KingFisher Module**: Liquidation analysis via image processing (30% weight)
- **Google Sheets API**: Historical risk band data
- **KuCoin Futures API**: Trading execution
- **OpenAI API**: AI-powered analysis and predictions

### Technology Stack
- **Backend**: FastAPI 0.104.1, Python 3.11+, PostgreSQL, Redis, InfluxDB
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Processing**: Pandas, NumPy, OpenCV, Pillow
- **Monitoring**: Prometheus metrics, structured logging

## Essential Commands

### Backend Development
```bash
cd backend/zmart-api
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Development server with hot reload
python run_dev.py

# Testing
pytest tests/                    # Run all tests
pytest tests/test_specific.py   # Run specific test file
pytest -k "test_function_name"  # Run specific test

# Code Quality
black .                          # Format code
ruff check .                     # Lint code (configured in pyproject.toml)
```

### Frontend Development
```bash
cd zmart-platform/frontend/zmart-dashboard
npm install --legacy-peer-deps

# Development
npm run dev                      # Start development server (port 5173)

# Build & Lint
npm run build                    # Production build
npm run lint                     # ESLint check
```

### ACTUAL SYSTEM ARCHITECTURE - MEMORIZED

**Project Structure (THE REAL SETUP):**
```
backend/zmart-api/
├── professional_dashboard_server.py  ← Serves dashboard (Port 3400)
├── src/main.py                      ← Backend API (Port 8000)
├── professional_dashboard/          ← React app source
│   ├── src/                        ← React components
│   ├── dist/                       ← Compiled React app
│   └── package.json                ← React dependencies
└── venv/                          ← Python virtual environment
```

**How The System Works:**
1. **Python Backend (Port 8000)**
   - File: `backend/zmart-api/src/main.py`
   - FastAPI server for API operations
   - Handles trading logic, RiskMetric, KuCoin/Binance APIs
   - Provides `/api/v1/` endpoints

2. **Python Dashboard Server (Port 3400)**
   - File: `backend/zmart-api/professional_dashboard_server.py`
   - Serves compiled React from `professional_dashboard/dist/`
   - Acts as proxy between frontend and backend
   - Handles static files (CSS, JS, images)

3. **React Frontend**
   - Location: `backend/zmart-api/professional_dashboard/`
   - Dark "Zmart Trading" dashboard UI
   - Makes API calls to Python backend
   - Built with Vite into `dist/` folder

**Starting the Platform:**
```bash
# Start API Backend (Port 8000)
cd backend/zmart-api
python src/main.py

# Start Dashboard Server (Port 3400)
cd backend/zmart-api
python professional_dashboard_server.py

# Build React if needed
cd backend/zmart-api/professional_dashboard
npm run build  # Creates/updates dist/ folder
```

**Access Points:**
- **Professional Dashboard**: http://localhost:3400
- **Backend API**: http://localhost:8000/api/
- **API Docs**: http://localhost:8000/docs

**CRITICAL RULES - THIS IS THE STRUCTURE**: 
- Dashboard lives in `backend/zmart-api/professional_dashboard/`
- NOT in `frontend/zmart-dashboard/` (that's something else)
- Python serves the dashboard from port 3400
- Always work within this structure
- When adding features, add to THIS structure

## Project Structure

```
ZmartBot/
├── backend/zmart-api/
│   ├── src/
│   │   ├── agents/              # Multi-agent trading system
│   │   ├── routes/              # API endpoints (20+ modules)
│   │   ├── services/            # Business logic and integrations
│   │   ├── utils/               # Shared utilities
│   │   └── config/              # Settings and configuration
│   ├── tests/                   # Test suite
│   └── requirements.txt         # Python dependencies
├── zmart-platform/
│   └── frontend/zmart-dashboard/  # React frontend
├── kingfisher-module/           # Liquidation analysis module
└── Documentation/               # Project documentation
```

## Critical Implementation Details

### API Response Format
All API endpoints return standardized responses:
```python
{
    "success": bool,
    "data": Any,
    "error": Optional[str],
    "timestamp": str
}
```

### Scoring System (100-point scale)
- **KingFisher**: 30 points (liquidation analysis)
- **Cryptometer**: 50 points (market metrics, 3-tier system)
- **RiskMetric**: 20 points (historical patterns)

### Environment Variables
Required in `.env`:
```
CRYPTOMETER_API_KEY=
KUCOIN_API_KEY=
KUCOIN_SECRET=
KUCOIN_PASSPHRASE=
OPENAI_API_KEY=
DATABASE_URL=postgresql://user:password@localhost/zmart_bot
REDIS_URL=redis://localhost:6379
```

### Critical RiskMetric Rules
**IMPORTANT**: These rules must be followed for RiskMetric calculations:

1. **DBI Workflow Only**: When calculating coefficients for RiskMetric, ONLY use the DBI (Database Integration) workflow. Do not use alternative calculation methods.

2. **Daily Updates Only**: Update the following ONCE per day only:
   - Life age of each symbol
   - Corresponding risk bands for each symbol
   - These updates should be scheduled, not triggered on every request

### Database Schema
- **PostgreSQL**: Trading data, positions, analytics
- **Redis**: Caching, rate limiting, session management
- **InfluxDB**: Time-series market data
- **SQLite**: Local learning system

### Testing Strategy
- Unit tests for individual components
- Integration tests for agent interactions
- Mock external APIs for consistent testing
- Use pytest fixtures for database state

## Common Tasks

### Adding a New Trading Signal
1. Create service in `src/services/`
2. Add route in `src/routes/`
3. Register in scoring agent `src/agents/scoring/`
4. Update scoring weights if needed
5. Add tests in `tests/`

### Debugging API Issues
1. Check logs in console output
2. Use FastAPI docs at `http://localhost:8000/docs`
3. Verify environment variables are set
4. Check database connections
5. Review rate limiting (429 errors expected for external APIs)

### Modifying Scoring Weights
Edit `src/agents/scoring/scoring_agent.py`:
- Adjust `WEIGHT_DISTRIBUTION` constants
- Update `calculate_composite_score()` method
- Test with `pytest tests/test_scoring_agent.py`

## Important Notes

- **Rate Limiting**: External APIs have rate limits; fallback mechanisms are in place
- **Mock Mode**: Development can run without external APIs using mock data
- **Correlation IDs**: All events use correlation IDs for tracking
- **Circuit Breakers**: Risk management includes automatic position closure triggers
- **AI Integration**: OpenAI calls have retry logic and error handling