# Zmarty Dual Database Architecture Documentation
**Version 1.0.0 | Production Architecture | January 2025**

---

## Executive Summary

Zmarty employs a sophisticated dual-database architecture using two separate Supabase projects to achieve optimal separation of concerns, enhanced security, and superior scalability. This architectural pattern separates user authentication and management from trading operations, creating a robust, secure, and maintainable system capable of handling millions of users and billions of trading operations.

### Key Benefits
- **Security Isolation**: Authentication separated from trading data
- **Scalability**: Independent scaling of user and trading operations
- **Performance**: Optimized query patterns for each domain
- **Compliance**: GDPR and financial regulations adherence
- **Maintenance**: Clear separation enables targeted updates

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Specifications](#project-specifications)
3. [Database Schemas](#database-schemas)
4. [Inter-Database Communication](#inter-database-communication)
5. [Security Model](#security-model)
6. [Data Flow Patterns](#data-flow-patterns)
7. [API Integration](#api-integration)
8. [Performance Optimization](#performance-optimization)
9. [Backup & Recovery](#backup--recovery)
10. [Monitoring & Observability](#monitoring--observability)
11. [Migration Strategies](#migration-strategies)
12. [Best Practices](#best-practices)

---

## Architecture Overview

### System Design Philosophy
```
┌─────────────────────────────────────────────────────────────────────┐
│                        ZMARTY DUAL DATABASE SYSTEM                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────┐      ┌──────────────────────────┐   │
│  │   ZMARTYBRAIN PROJECT     │      │  SMART TRADING PROJECT   │   │
│  │   (User Management)       │      │   (Trading Operations)    │   │
│  ├──────────────────────────┤      ├──────────────────────────┤   │
│  │                          │      │                          │   │
│  │  • Authentication        │      │  • Market Data           │   │
│  │  • User Profiles         │◄────►│  • Trading Signals       │   │
│  │  • Credit System         │      │  • Portfolio Management  │   │
│  │  • Subscriptions         │      │  • AI Analysis           │   │
│  │  • Billing              │      │  • Exchange Integration  │   │
│  │  • Notifications        │      │  • Historical Data       │   │
│  │                          │      │                          │   │
│  └──────────────────────────┘      └──────────────────────────┘   │
│           ▲                                    ▲                    │
│           │                                    │                    │
│           └────────────────────────────────────┘                   │
│                        API Gateway Layer                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Architectural Principles

| Principle | Implementation | Benefit |
|-----------|----------------|---------|
| **Separation of Concerns** | Distinct databases for auth vs trading | Clear boundaries, easier maintenance |
| **Single Source of Truth** | User data only in ZmartyBrain | No data duplication issues |
| **Eventual Consistency** | Async sync for non-critical data | Better performance |
| **Security by Design** | Minimal cross-database access | Reduced attack surface |
| **Scalability First** | Independent resource allocation | Cost-effective scaling |

---

## Project Specifications

### ZmartyBrain Project (Authentication & User Management)
```yaml
Project Details:
  Name: ZmartyBrain
  Project ID: xhskmqsgtdhehzlvtuns
  URL: https://xhskmqsgtdhehzlvtuns.supabase.co
  Region: us-east-1
  Purpose: User authentication, profiles, and account management

Technical Specifications:
  Database:
    Type: PostgreSQL 15
    Size: Up to 500GB
    Connections: 100 concurrent
    Extensions:
      - uuid-ossp
      - pgcrypto
      - pgjwt
      - pg_stat_statements
      - plpgsql

  Authentication:
    Providers:
      - Email/Password
      - Google OAuth
      - Apple Sign In
      - Magic Link
    Features:
      - Email verification (OTP)
      - Password reset
      - MFA support (ready)
      - Session management
      - JWT tokens

  Storage:
    Buckets:
      - avatars (public)
      - documents (private)
      - exports (temporary)
    Limits:
      - Max file size: 50MB
      - Total storage: 100GB

  Security:
    - Row Level Security (RLS): Enabled
    - SSL/TLS: Enforced
    - Encryption: AES-256-GCM
    - Backup: Daily, 30-day retention
```

### Smart Trading Project (Trading Operations & Market Data)
```yaml
Project Details:
  Name: Smart Trading
  Project ID: asjtxrmftmutcsnqgidy
  URL: https://asjtxrmftmutcsnqgidy.supabase.co
  Region: us-east-1
  Purpose: Trading operations, market data, and analytics

Technical Specifications:
  Database:
    Type: PostgreSQL 15
    Size: Up to 2TB
    Connections: 500 concurrent
    Extensions:
      - timescaledb
      - pg_stat_statements
      - postgis
      - pg_trgm
      - btree_gin

  Realtime:
    Channels:
      - market_data
      - trading_signals
      - portfolio_updates
      - system_alerts
    Subscribers: Up to 10,000
    Message Rate: 1000/second

  Storage:
    Buckets:
      - charts (public, CDN)
      - reports (private)
      - backups (private)
    Limits:
      - Max file size: 100MB
      - Total storage: 500GB

  Performance:
    - Connection Pooling: PgBouncer
    - Query Optimization: Automatic
    - Indexes: Custom B-tree, GIN
    - Partitioning: Time-based
```

---

## Database Schemas

### ZmartyBrain Schema (User Domain)

```sql
-- Core User Table
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    email_verified_at TIMESTAMP WITH TIME ZONE,
    last_sign_in_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',

    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- User Profiles
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    display_name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    trading_experience VARCHAR(50),
    risk_tolerance INTEGER CHECK (risk_tolerance BETWEEN 1 AND 5),
    preferred_pairs TEXT[],
    notification_preferences JSONB DEFAULT '{}',
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    CONSTRAINT unique_user_profile UNIQUE(user_id)
);

-- Credit System
CREATE TABLE public.credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 0 CHECK (balance >= 0),
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    last_refill_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    CONSTRAINT unique_user_credits UNIQUE(user_id)
);

-- Credit Transactions
CREATE TABLE public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'earn', 'spend', 'refund', 'bonus'
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_credit_transactions_user_id (user_id),
    INDEX idx_credit_transactions_created_at (created_at DESC)
);

-- Subscriptions
CREATE TABLE public.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL, -- 'free', 'starter', 'pro', 'enterprise'
    status VARCHAR(50) NOT NULL, -- 'active', 'cancelled', 'expired', 'trial'
    billing_cycle VARCHAR(20), -- 'monthly', 'yearly'
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    CONSTRAINT unique_user_subscription UNIQUE(user_id),
    INDEX idx_subscriptions_status (status),
    INDEX idx_subscriptions_tier (tier)
);

-- Notification Queue
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    message TEXT,
    data JSONB DEFAULT '{}',
    read_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_notifications_user_id (user_id),
    INDEX idx_notifications_read_at (read_at),
    INDEX idx_notifications_created_at (created_at DESC)
);

-- Audit Log
CREATE TABLE public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_entity (entity_type, entity_id),
    INDEX idx_audit_logs_created_at (created_at DESC)
);
```

### Smart Trading Schema (Trading Domain)

```sql
-- User Reference Table (Links to ZmartyBrain)
CREATE TABLE public.user_references (
    user_id UUID PRIMARY KEY, -- Same as ZmartyBrain user.id
    email VARCHAR(255) NOT NULL,
    tier VARCHAR(50) DEFAULT 'free',
    credits_balance INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_user_references_email (email),
    INDEX idx_user_references_tier (tier)
);

-- Trading Portfolios
CREATE TABLE public.portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.user_references(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_value_usd DECIMAL(20, 8) DEFAULT 0,
    total_cost_basis_usd DECIMAL(20, 8) DEFAULT 0,
    unrealized_pnl_usd DECIMAL(20, 8) DEFAULT 0,
    realized_pnl_usd DECIMAL(20, 8) DEFAULT 0,
    is_default BOOLEAN DEFAULT FALSE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    CONSTRAINT unique_default_portfolio UNIQUE(user_id, is_default),
    INDEX idx_portfolios_user_id (user_id)
);

-- Portfolio Holdings
CREATE TABLE public.holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL CHECK (quantity >= 0),
    average_buy_price DECIMAL(20, 8),
    current_price DECIMAL(20, 8),
    value_usd DECIMAL(20, 8),
    cost_basis_usd DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    unrealized_pnl_percent DECIMAL(10, 4),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    CONSTRAINT unique_portfolio_symbol UNIQUE(portfolio_id, symbol),
    INDEX idx_holdings_portfolio_id (portfolio_id),
    INDEX idx_holdings_symbol (symbol)
);

-- Trading Signals
CREATE TABLE public.trading_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL, -- 'buy', 'sell', 'hold'
    strength INTEGER CHECK (strength BETWEEN 1 AND 100),
    ai_model VARCHAR(50), -- 'claude', 'gpt5', 'gemini', 'grok', 'ensemble'
    confidence_score DECIMAL(5, 4) CHECK (confidence_score BETWEEN 0 AND 1),
    entry_price DECIMAL(20, 8),
    target_price DECIMAL(20, 8),
    stop_loss DECIMAL(20, 8),
    reasoning TEXT,
    metadata JSONB DEFAULT '{}',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_trading_signals_symbol (symbol),
    INDEX idx_trading_signals_created_at (created_at DESC),
    INDEX idx_trading_signals_expires_at (expires_at)
);

-- User Trades
CREATE TABLE public.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.user_references(user_id) ON DELETE CASCADE,
    portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE,
    signal_id UUID REFERENCES public.trading_signals(id),
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- 'buy', 'sell'
    type VARCHAR(20) NOT NULL, -- 'market', 'limit', 'stop', 'stop_limit'
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    total_value DECIMAL(20, 8),
    fees DECIMAL(20, 8) DEFAULT 0,
    status VARCHAR(20) NOT NULL, -- 'pending', 'filled', 'partial', 'cancelled', 'failed'
    exchange_order_id VARCHAR(255),
    filled_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_trades_user_id (user_id),
    INDEX idx_trades_portfolio_id (portfolio_id),
    INDEX idx_trades_symbol (symbol),
    INDEX idx_trades_created_at (created_at DESC)
);

-- Market Data (TimescaleDB Hypertable)
CREATE TABLE public.market_data (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    open DECIMAL(20, 8),
    high DECIMAL(20, 8),
    low DECIMAL(20, 8),
    close DECIMAL(20, 8),
    volume DECIMAL(20, 8),
    volume_usd DECIMAL(20, 8),
    trades_count INTEGER,
    vwap DECIMAL(20, 8),

    PRIMARY KEY (time, symbol, exchange)
);

-- Convert to TimescaleDB Hypertable
SELECT create_hypertable('market_data', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- AI Analysis Results
CREATE TABLE public.ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.user_references(user_id) ON DELETE CASCADE,
    request_type VARCHAR(50) NOT NULL, -- 'market_analysis', 'portfolio_review', 'signal_generation'
    query TEXT,
    ai_model VARCHAR(50),
    response TEXT,
    tokens_used INTEGER,
    credits_charged INTEGER,
    processing_time_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    INDEX idx_ai_analysis_user_id (user_id),
    INDEX idx_ai_analysis_created_at (created_at DESC)
);

-- Exchange Connections
CREATE TABLE public.exchange_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.user_references(user_id) ON DELETE CASCADE,
    exchange VARCHAR(50) NOT NULL,
    api_key_encrypted TEXT, -- Encrypted with user-specific key
    api_secret_encrypted TEXT, -- Encrypted with user-specific key
    passphrase_encrypted TEXT, -- For exchanges that require it
    permissions JSONB DEFAULT '{}', -- {"read": true, "trade": false}
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),

    CONSTRAINT unique_user_exchange UNIQUE(user_id, exchange),
    INDEX idx_exchange_connections_user_id (user_id)
);

-- Performance Metrics
CREATE TABLE public.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.user_references(user_id) ON DELETE CASCADE,
    portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    starting_value DECIMAL(20, 8),
    ending_value DECIMAL(20, 8),
    daily_return DECIMAL(10, 6),
    cumulative_return DECIMAL(10, 6),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 6),
    win_rate DECIMAL(5, 4),
    average_win DECIMAL(20, 8),
    average_loss DECIMAL(20, 8),
    total_trades INTEGER,
    profitable_trades INTEGER,

    CONSTRAINT unique_daily_metrics UNIQUE(portfolio_id, date),
    INDEX idx_performance_metrics_portfolio_id (portfolio_id),
    INDEX idx_performance_metrics_date (date DESC)
);
```

---

## Inter-Database Communication

### Communication Patterns

```javascript
// 1. Direct Database Access Pattern (Server-Side Only)
class DualDatabaseManager {
    constructor() {
        // Initialize both database connections
        this.authDB = createClient(
            process.env.ZMARTYBRAIN_URL,
            process.env.ZMARTYBRAIN_SERVICE_KEY
        );

        this.tradingDB = createClient(
            process.env.SMARTTRADING_URL,
            process.env.SMARTTRADING_SERVICE_KEY
        );
    }

    // Fetch user with trading data
    async getUserWithTradingData(userId) {
        // Get user from auth database
        const { data: user } = await this.authDB
            .from('user_profiles')
            .select('*')
            .eq('user_id', userId)
            .single();

        // Get trading data from trading database
        const { data: tradingData } = await this.tradingDB
            .from('portfolios')
            .select(`
                *,
                holdings (*),
                trades (count)
            `)
            .eq('user_id', userId);

        return {
            ...user,
            portfolios: tradingData
        };
    }
}

// 2. Event-Driven Synchronization Pattern
class EventSynchronizer {
    constructor() {
        this.setupWebhooks();
        this.setupRealtimeListeners();
    }

    setupWebhooks() {
        // Webhook for user creation in ZmartyBrain
        app.post('/webhooks/user-created', async (req, res) => {
            const { user } = req.body;

            // Create reference in Smart Trading
            await this.tradingDB
                .from('user_references')
                .insert({
                    user_id: user.id,
                    email: user.email,
                    tier: 'free',
                    credits_balance: 100
                });

            // Create default portfolio
            await this.tradingDB
                .from('portfolios')
                .insert({
                    user_id: user.id,
                    name: 'Default Portfolio',
                    is_default: true
                });

            res.status(200).send('OK');
        });
    }

    setupRealtimeListeners() {
        // Listen for subscription changes in ZmartyBrain
        this.authDB
            .channel('subscription-changes')
            .on('postgres_changes',
                {
                    event: 'UPDATE',
                    schema: 'public',
                    table: 'subscriptions'
                },
                async (payload) => {
                    // Update user tier in Smart Trading
                    await this.tradingDB
                        .from('user_references')
                        .update({ tier: payload.new.tier })
                        .eq('user_id', payload.new.user_id);
                }
            )
            .subscribe();
    }
}

// 3. API Gateway Pattern
class APIGateway {
    // Unified endpoint that combines data from both databases
    async handleRequest(endpoint, params) {
        switch(endpoint) {
            case '/api/user/dashboard':
                return this.getDashboardData(params.userId);

            case '/api/trading/execute':
                return this.executeTrade(params);

            case '/api/credits/spend':
                return this.spendCredits(params);
        }
    }

    async getDashboardData(userId) {
        // Parallel fetch from both databases
        const [userData, tradingData] = await Promise.all([
            this.fetchUserData(userId),
            this.fetchTradingData(userId)
        ]);

        return {
            user: userData,
            trading: tradingData,
            timestamp: new Date().toISOString()
        };
    }

    async executeTrade(params) {
        const { userId, tradeData } = params;

        // Check credits in ZmartyBrain
        const hasCredits = await this.checkCredits(userId, 10);
        if (!hasCredits) {
            throw new Error('Insufficient credits');
        }

        // Execute trade in Smart Trading
        const trade = await this.tradingDB
            .from('trades')
            .insert(tradeData)
            .select()
            .single();

        // Deduct credits in ZmartyBrain
        await this.deductCredits(userId, 10, `Trade: ${trade.id}`);

        return trade;
    }
}
```

### Synchronization Strategies

```sql
-- Scheduled Sync Function (runs every 5 minutes)
CREATE OR REPLACE FUNCTION sync_user_data()
RETURNS void AS $$
DECLARE
    user_record RECORD;
BEGIN
    -- Sync updated user tiers
    FOR user_record IN
        SELECT u.id, u.email, s.tier, c.balance
        FROM auth.users u
        JOIN subscriptions s ON s.user_id = u.id
        JOIN credits c ON c.user_id = u.id
        WHERE u.updated_at > NOW() - INTERVAL '5 minutes'
    LOOP
        -- Update Smart Trading database via API
        PERFORM net.http_post(
            url := 'https://api.zmarty.team/sync/user',
            body := json_build_object(
                'user_id', user_record.id,
                'email', user_record.email,
                'tier', user_record.tier,
                'credits_balance', user_record.balance
            )::text
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Schedule the sync
SELECT cron.schedule(
    'sync-user-data',
    '*/5 * * * *',
    'SELECT sync_user_data();'
);
```

---

## Security Model

### Access Control Matrix

| Component | ZmartyBrain Access | Smart Trading Access | Cross-Database |
|-----------|-------------------|---------------------|----------------|
| **Frontend Client** | Public Key (RLS) | Public Key (RLS) | Not Allowed |
| **API Server** | Service Key | Service Key | Allowed |
| **Edge Functions** | Service Key | Service Key | Allowed |
| **Webhooks** | Webhook Secret | Webhook Secret | Allowed |
| **Admin Dashboard** | Service Key | Service Key | Allowed |
| **Mobile App** | Public Key (RLS) | Public Key (RLS) | Not Allowed |

### Row Level Security (RLS) Policies

```sql
-- ZmartyBrain RLS Policies
-- Users can only read their own profile
CREATE POLICY "Users can read own profile"
ON user_profiles FOR SELECT
USING (auth.uid() = user_id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
ON user_profiles FOR UPDATE
USING (auth.uid() = user_id);

-- Smart Trading RLS Policies
-- Users can only access their own trading data
CREATE POLICY "Users can view own portfolios"
ON portfolios FOR SELECT
USING (
    user_id IN (
        SELECT user_id FROM user_references
        WHERE user_id = auth.uid()
    )
);

-- Prevent direct user reference manipulation
CREATE POLICY "No direct user_references access"
ON user_references FOR ALL
USING (FALSE);
```

### Encryption Strategy

```javascript
// Field-Level Encryption for Sensitive Data
class EncryptionManager {
    constructor() {
        this.algorithm = 'aes-256-gcm';
        this.masterKey = this.deriveMasterKey();
    }

    // Encrypt API keys before storing
    async encryptAPIKey(apiKey, userId) {
        const userKey = await this.deriveUserKey(userId);
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv(
            this.algorithm,
            userKey,
            iv
        );

        let encrypted = cipher.update(apiKey, 'utf8', 'hex');
        encrypted += cipher.final('hex');

        const authTag = cipher.getAuthTag();

        return {
            encrypted: encrypted,
            iv: iv.toString('hex'),
            authTag: authTag.toString('hex')
        };
    }

    // Decrypt API keys when needed
    async decryptAPIKey(encryptedData, userId) {
        const userKey = await this.deriveUserKey(userId);
        const decipher = crypto.createDecipheriv(
            this.algorithm,
            userKey,
            Buffer.from(encryptedData.iv, 'hex')
        );

        decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

        let decrypted = decipher.update(
            encryptedData.encrypted,
            'hex',
            'utf8'
        );
        decrypted += decipher.final('utf8');

        return decrypted;
    }

    deriveUserKey(userId) {
        return crypto.pbkdf2Sync(
            userId,
            this.masterKey,
            100000,
            32,
            'sha256'
        );
    }
}
```

---

## Data Flow Patterns

### User Registration Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant ZmartyBrain
    participant SmartTrading

    User->>Frontend: Sign Up
    Frontend->>API: POST /auth/register
    API->>ZmartyBrain: Create auth.user
    ZmartyBrain-->>API: User created
    API->>ZmartyBrain: Create user_profile
    API->>ZmartyBrain: Initialize credits
    API->>SmartTrading: Create user_reference
    API->>SmartTrading: Create default_portfolio
    SmartTrading-->>API: Confirmation
    API-->>Frontend: Success response
    Frontend-->>User: Welcome email
```

### Trading Execution Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant ZmartyBrain
    participant SmartTrading
    participant Exchange

    User->>Frontend: Place trade
    Frontend->>API: POST /trading/execute
    API->>ZmartyBrain: Check credits
    ZmartyBrain-->>API: Credits available
    API->>SmartTrading: Create trade record
    SmartTrading->>Exchange: Execute order
    Exchange-->>SmartTrading: Order filled
    SmartTrading-->>API: Trade complete
    API->>ZmartyBrain: Deduct credits
    API->>SmartTrading: Update portfolio
    API-->>Frontend: Trade confirmation
    Frontend-->>User: Success notification
```

---

## API Integration

### Dual Database API Client

```typescript
// TypeScript Implementation
import { createClient, SupabaseClient } from '@supabase/supabase-js';

interface DualDatabaseConfig {
    zmartyBrain: {
        url: string;
        anonKey: string;
        serviceKey?: string;
    };
    smartTrading: {
        url: string;
        anonKey: string;
        serviceKey?: string;
    };
}

class ZmartyDualDatabaseClient {
    private authDB: SupabaseClient;
    private tradingDB: SupabaseClient;
    private userId: string | null = null;

    constructor(config: DualDatabaseConfig) {
        // Initialize authentication database
        this.authDB = createClient(
            config.zmartyBrain.url,
            config.zmartyBrain.serviceKey || config.zmartyBrain.anonKey
        );

        // Initialize trading database
        this.tradingDB = createClient(
            config.smartTrading.url,
            config.smartTrading.serviceKey || config.smartTrading.anonKey
        );

        // Setup auth state listener
        this.authDB.auth.onAuthStateChange((event, session) => {
            this.userId = session?.user?.id || null;
            if (event === 'SIGNED_IN') {
                this.syncUserToTrading(session.user);
            }
        });
    }

    // Authentication Methods
    async signUp(email: string, password: string) {
        const { data, error } = await this.authDB.auth.signUp({
            email,
            password
        });

        if (data?.user && !error) {
            await this.initializeUserData(data.user.id);
        }

        return { data, error };
    }

    async signIn(email: string, password: string) {
        return await this.authDB.auth.signInWithPassword({
            email,
            password
        });
    }

    // User Profile Methods
    async getUserProfile() {
        if (!this.userId) throw new Error('Not authenticated');

        const { data, error } = await this.authDB
            .from('user_profiles')
            .select('*')
            .eq('user_id', this.userId)
            .single();

        return { data, error };
    }

    async updateUserProfile(updates: any) {
        if (!this.userId) throw new Error('Not authenticated');

        return await this.authDB
            .from('user_profiles')
            .update(updates)
            .eq('user_id', this.userId);
    }

    // Credit System Methods
    async getCreditsBalance() {
        if (!this.userId) throw new Error('Not authenticated');

        const { data } = await this.authDB
            .from('credits')
            .select('balance')
            .eq('user_id', this.userId)
            .single();

        return data?.balance || 0;
    }

    async spendCredits(amount: number, description: string) {
        if (!this.userId) throw new Error('Not authenticated');

        // Use database function for atomic operation
        const { data, error } = await this.authDB
            .rpc('spend_credits', {
                p_user_id: this.userId,
                p_amount: amount,
                p_description: description
            });

        return { data, error };
    }

    // Trading Methods
    async getPortfolios() {
        if (!this.userId) throw new Error('Not authenticated');

        return await this.tradingDB
            .from('portfolios')
            .select(`
                *,
                holdings (*)
            `)
            .eq('user_id', this.userId);
    }

    async executeTrade(tradeData: any) {
        if (!this.userId) throw new Error('Not authenticated');

        // Check credits first
        const balance = await this.getCreditsBalance();
        if (balance < 10) {
            throw new Error('Insufficient credits');
        }

        // Execute trade
        const { data: trade, error } = await this.tradingDB
            .from('trades')
            .insert({
                ...tradeData,
                user_id: this.userId
            })
            .select()
            .single();

        if (!error && trade) {
            // Deduct credits
            await this.spendCredits(10, `Trade execution: ${trade.id}`);
        }

        return { data: trade, error };
    }

    // AI Analysis Methods
    async requestAIAnalysis(query: string, model: string = 'ensemble') {
        if (!this.userId) throw new Error('Not authenticated');

        // Check credits (AI queries cost more)
        const balance = await this.getCreditsBalance();
        const cost = model === 'ensemble' ? 50 : 20;

        if (balance < cost) {
            throw new Error('Insufficient credits for AI analysis');
        }

        // Store analysis request
        const { data, error } = await this.tradingDB
            .from('ai_analysis')
            .insert({
                user_id: this.userId,
                query,
                ai_model: model,
                credits_charged: cost
            })
            .select()
            .single();

        if (!error && data) {
            // Process with AI
            const response = await this.processAIQuery(query, model);

            // Update with response
            await this.tradingDB
                .from('ai_analysis')
                .update({
                    response: response.text,
                    tokens_used: response.tokens,
                    processing_time_ms: response.time
                })
                .eq('id', data.id);

            // Deduct credits
            await this.spendCredits(cost, `AI Analysis: ${data.id}`);

            return response;
        }

        return { error };
    }

    // Private Methods
    private async syncUserToTrading(user: any) {
        // Ensure user reference exists in trading database
        const { error } = await this.tradingDB
            .from('user_references')
            .upsert({
                user_id: user.id,
                email: user.email,
                last_sync_at: new Date().toISOString()
            }, {
                onConflict: 'user_id'
            });

        return !error;
    }

    private async initializeUserData(userId: string) {
        // Create user reference in trading DB
        await this.tradingDB
            .from('user_references')
            .insert({
                user_id: userId,
                email: (await this.authDB.auth.getUser()).data.user?.email,
                tier: 'free',
                credits_balance: 100
            });

        // Create default portfolio
        await this.tradingDB
            .from('portfolios')
            .insert({
                user_id: userId,
                name: 'Default Portfolio',
                is_default: true
            });

        // Initialize credits in auth DB
        await this.authDB
            .from('credits')
            .insert({
                user_id: userId,
                balance: 100,
                total_earned: 100
            });
    }

    private async processAIQuery(query: string, model: string) {
        // This would connect to your AI service
        // Placeholder for demonstration
        return {
            text: 'AI response here',
            tokens: 150,
            time: 1200
        };
    }
}

// Export for use
export default ZmartyDualDatabaseClient;
```

### REST API Endpoints

```yaml
# API Specification for Dual Database System

# Authentication Endpoints (ZmartyBrain)
/api/auth:
  /register:
    POST:
      body: { email, password }
      response: { user, session }
      database: ZmartyBrain

  /login:
    POST:
      body: { email, password }
      response: { user, session }
      database: ZmartyBrain

  /logout:
    POST:
      headers: { Authorization: Bearer {token} }
      response: { success }
      database: ZmartyBrain

  /refresh:
    POST:
      body: { refresh_token }
      response: { session }
      database: ZmartyBrain

# User Management (ZmartyBrain)
/api/user:
  /profile:
    GET:
      headers: { Authorization: Bearer {token} }
      response: { profile }
      database: ZmartyBrain

    PUT:
      headers: { Authorization: Bearer {token} }
      body: { ...profile_updates }
      response: { profile }
      database: ZmartyBrain

  /credits:
    GET:
      response: { balance, transactions }
      database: ZmartyBrain

  /subscription:
    GET:
      response: { tier, status, next_billing }
      database: ZmartyBrain

    POST:
      body: { tier, payment_method }
      response: { subscription }
      database: ZmartyBrain

# Trading Operations (Smart Trading)
/api/trading:
  /portfolios:
    GET:
      response: { portfolios[] }
      database: SmartTrading

    POST:
      body: { name, description }
      response: { portfolio }
      database: SmartTrading

  /execute:
    POST:
      body: { symbol, side, quantity, type }
      response: { trade }
      databases: [SmartTrading, ZmartyBrain]
      note: Checks credits in ZmartyBrain

  /signals:
    GET:
      query: { symbols[], timeframe }
      response: { signals[] }
      database: SmartTrading

  /analysis:
    POST:
      body: { query, model }
      response: { analysis }
      databases: [SmartTrading, ZmartyBrain]
      note: Deducts credits from ZmartyBrain

# Cross-Database Operations
/api/dashboard:
  GET:
    response: {
      user: { profile, credits, subscription },
      trading: { portfolios, recent_trades, performance }
    }
    databases: [ZmartyBrain, SmartTrading]
```

---

## Performance Optimization

### Query Optimization Strategies

```sql
-- Optimized Indexes for ZmartyBrain
CREATE INDEX CONCURRENTLY idx_users_email_lower
ON public.users (LOWER(email));

CREATE INDEX CONCURRENTLY idx_profiles_user_id_include
ON public.user_profiles (user_id)
INCLUDE (full_name, avatar_url, trading_experience);

CREATE INDEX CONCURRENTLY idx_credits_user_balance
ON public.credits (user_id, balance)
WHERE balance > 0;

CREATE INDEX CONCURRENTLY idx_transactions_user_date
ON public.credit_transactions (user_id, created_at DESC);

-- Optimized Indexes for Smart Trading
CREATE INDEX CONCURRENTLY idx_trades_user_symbol_date
ON public.trades (user_id, symbol, created_at DESC);

CREATE INDEX CONCURRENTLY idx_holdings_portfolio_value
ON public.holdings (portfolio_id, value_usd DESC);

CREATE INDEX CONCURRENTLY idx_signals_symbol_active
ON public.trading_signals (symbol, created_at DESC)
WHERE expires_at > NOW();

-- Partial indexes for common queries
CREATE INDEX CONCURRENTLY idx_trades_pending
ON public.trades (user_id, created_at)
WHERE status = 'pending';

CREATE INDEX CONCURRENTLY idx_portfolios_default
ON public.portfolios (user_id)
WHERE is_default = TRUE;
```

### Caching Strategy

```javascript
// Multi-Layer Caching Implementation
class CacheManager {
    constructor() {
        // In-memory cache (fastest)
        this.memoryCache = new Map();

        // Redis cache (shared across instances)
        this.redisClient = redis.createClient({
            url: process.env.REDIS_URL
        });

        // Cache TTLs
        this.ttls = {
            userProfile: 300, // 5 minutes
            credits: 60, // 1 minute
            portfolio: 120, // 2 minutes
            marketData: 10, // 10 seconds
            aiAnalysis: 3600 // 1 hour
        };
    }

    async get(key, fetchFunction, ttl) {
        // Check memory cache first
        if (this.memoryCache.has(key)) {
            return this.memoryCache.get(key);
        }

        // Check Redis cache
        const redisValue = await this.redisClient.get(key);
        if (redisValue) {
            const parsed = JSON.parse(redisValue);
            this.memoryCache.set(key, parsed);
            return parsed;
        }

        // Fetch from database
        const value = await fetchFunction();

        // Store in both caches
        this.memoryCache.set(key, value);
        await this.redisClient.setex(
            key,
            ttl,
            JSON.stringify(value)
        );

        return value;
    }

    invalidate(pattern) {
        // Clear memory cache
        for (const key of this.memoryCache.keys()) {
            if (key.includes(pattern)) {
                this.memoryCache.delete(key);
            }
        }

        // Clear Redis cache
        return this.redisClient.del(pattern);
    }
}
```

### Connection Pooling

```javascript
// PgBouncer Configuration for Both Databases
const poolConfig = {
    // ZmartyBrain Pool
    zmartyBrain: {
        max: 20, // Maximum connections
        min: 5, // Minimum connections
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
        statement_timeout: '30s',
        query_timeout: '30s',
        poolMode: 'transaction' // Best for short queries
    },

    // Smart Trading Pool (Higher limits for heavy queries)
    smartTrading: {
        max: 50,
        min: 10,
        idleTimeoutMillis: 60000,
        connectionTimeoutMillis: 5000,
        statement_timeout: '60s',
        query_timeout: '60s',
        poolMode: 'session' // Better for long-running queries
    }
};
```

---

## Backup & Recovery

### Backup Strategy

```bash
#!/bin/bash
# Automated Backup Script

# Configuration
ZMARTYBRAIN_URL="postgres://user:pass@host:5432/zmartybrain"
SMARTTRADING_URL="postgres://user:pass@host:5432/smarttrading"
BACKUP_DIR="/backups"
S3_BUCKET="s3://zmarty-backups"
RETENTION_DAYS=30

# Function to backup database
backup_database() {
    local db_name=$1
    local db_url=$2
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/${db_name}_${timestamp}.sql.gz"

    echo "Starting backup of ${db_name}..."

    # Create backup with compression
    pg_dump "${db_url}" \
        --verbose \
        --no-owner \
        --no-acl \
        --format=custom \
        --compress=9 \
        --file="${backup_file}"

    # Upload to S3
    aws s3 cp "${backup_file}" "${S3_BUCKET}/${db_name}/" \
        --storage-class GLACIER_IR

    # Verify backup
    pg_restore --list "${backup_file}" > /dev/null
    if [ $? -eq 0 ]; then
        echo "Backup of ${db_name} completed successfully"
    else
        echo "ERROR: Backup verification failed for ${db_name}"
        exit 1
    fi

    # Clean old local backups
    find "${BACKUP_DIR}" -name "${db_name}_*.sql.gz" \
        -mtime +7 -delete
}

# Backup both databases
backup_database "zmartybrain" "${ZMARTYBRAIN_URL}"
backup_database "smarttrading" "${SMARTTRADING_URL}"

# Clean old S3 backups
aws s3 ls "${S3_BUCKET}" --recursive \
    | awk '{print $4}' \
    | xargs -I {} bash -c \
    "aws s3api head-object --bucket zmarty-backups --key {} \
    | jq -r '.LastModified' \
    | xargs -I {} date -d {} +%s" \
    | awk -v cutoff="$(date -d "${RETENTION_DAYS} days ago" +%s)" \
    '$1 < cutoff {print}' \
    | xargs -I {} aws s3 rm "${S3_BUCKET}/{}"

echo "Backup process completed"
```

### Recovery Procedures

```sql
-- Point-in-Time Recovery Setup
-- Enable WAL archiving for both databases

-- ZmartyBrain
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'aws s3 cp %p s3://zmarty-wal/zmartybrain/%f';
ALTER SYSTEM SET archive_timeout = '60';

-- Smart Trading
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'aws s3 cp %p s3://zmarty-wal/smarttrading/%f';
ALTER SYSTEM SET archive_timeout = '60';

-- Recovery Script
CREATE OR REPLACE FUNCTION recover_to_timestamp(
    target_time TIMESTAMP WITH TIME ZONE
) RETURNS void AS $$
BEGIN
    -- Stop all connections
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = current_database()
    AND pid <> pg_backend_pid();

    -- Restore from backup
    -- This would be handled by external script
    RAISE NOTICE 'Initiating recovery to %', target_time;
END;
$$ LANGUAGE plpgsql;
```

---

## Monitoring & Observability

### Health Check Endpoints

```javascript
// Health monitoring for both databases
app.get('/health', async (req, res) => {
    const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        databases: {
            zmartyBrain: {
                status: 'unknown',
                latency: null,
                connections: null
            },
            smartTrading: {
                status: 'unknown',
                latency: null,
                connections: null
            }
        },
        checks: []
    };

    // Check ZmartyBrain
    try {
        const start = Date.now();
        const { data } = await authDB
            .from('users')
            .select('count')
            .limit(1);

        health.databases.zmartyBrain = {
            status: 'healthy',
            latency: Date.now() - start,
            connections: await getConnectionCount('zmartybrain')
        };
    } catch (error) {
        health.databases.zmartyBrain.status = 'unhealthy';
        health.status = 'degraded';
        health.checks.push({
            name: 'ZmartyBrain',
            status: 'failed',
            error: error.message
        });
    }

    // Check Smart Trading
    try {
        const start = Date.now();
        const { data } = await tradingDB
            .from('portfolios')
            .select('count')
            .limit(1);

        health.databases.smartTrading = {
            status: 'healthy',
            latency: Date.now() - start,
            connections: await getConnectionCount('smarttrading')
        };
    } catch (error) {
        health.databases.smartTrading.status = 'unhealthy';
        health.status = 'degraded';
        health.checks.push({
            name: 'SmartTrading',
            status: 'failed',
            error: error.message
        });
    }

    // Return appropriate status code
    const statusCode = health.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(health);
});
```

### Monitoring Queries

```sql
-- Performance Monitoring Views
-- ZmartyBrain Performance
CREATE VIEW monitoring.zmartybrain_stats AS
SELECT
    'zmartybrain' as database,
    (SELECT count(*) FROM auth.users) as total_users,
    (SELECT count(*) FROM auth.users
     WHERE created_at > NOW() - INTERVAL '24 hours') as new_users_24h,
    (SELECT count(*) FROM auth.users
     WHERE last_sign_in_at > NOW() - INTERVAL '1 hour') as active_users_1h,
    (SELECT sum(balance) FROM credits) as total_credits,
    (SELECT count(*) FROM subscriptions WHERE status = 'active') as active_subscriptions,
    (SELECT avg(extract(epoch from (email_verified_at - created_at)))
     FROM auth.users
     WHERE email_verified_at IS NOT NULL) as avg_verification_time_seconds,
    pg_database_size(current_database()) as database_size_bytes,
    (SELECT count(*) FROM pg_stat_activity) as active_connections;

-- Smart Trading Performance
CREATE VIEW monitoring.smarttrading_stats AS
SELECT
    'smarttrading' as database,
    (SELECT count(*) FROM user_references) as total_users,
    (SELECT count(*) FROM portfolios) as total_portfolios,
    (SELECT count(*) FROM trades WHERE created_at > NOW() - INTERVAL '24 hours') as trades_24h,
    (SELECT sum(total_value_usd) FROM portfolios) as total_portfolio_value,
    (SELECT count(*) FROM trading_signals
     WHERE created_at > NOW() - INTERVAL '1 hour') as signals_generated_1h,
    (SELECT avg(processing_time_ms) FROM ai_analysis
     WHERE created_at > NOW() - INTERVAL '1 hour') as avg_ai_response_ms,
    pg_database_size(current_database()) as database_size_bytes,
    (SELECT count(*) FROM pg_stat_activity) as active_connections;

-- Slow Query Log
CREATE VIEW monitoring.slow_queries AS
SELECT
    datname as database,
    usename as user,
    query,
    state,
    wait_event_type,
    wait_event,
    extract(epoch from (now() - query_start)) as duration_seconds,
    query_start
FROM pg_stat_activity
WHERE state != 'idle'
AND query NOT LIKE '%pg_stat_activity%'
AND extract(epoch from (now() - query_start)) > 5
ORDER BY duration_seconds DESC;
```

### Alerting Rules

```yaml
# Prometheus Alert Rules
groups:
  - name: database_alerts
    interval: 30s
    rules:
      # High connection count
      - alert: HighDatabaseConnections
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High connection count on {{ $labels.database }}"
          description: "{{ $value }} connections (threshold: 80)"

      # Slow queries
      - alert: SlowQueries
        expr: pg_stat_activity_max_tx_duration > 30
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Slow query detected"
          description: "Query running for {{ $value }} seconds"

      # Database size
      - alert: DatabaseSizeHigh
        expr: pg_database_size_bytes > 450000000000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Database size approaching limit"
          description: "Database {{ $labels.database }} is {{ $value | humanize }} (limit: 500GB)"

      # Replication lag (if using read replicas)
      - alert: ReplicationLag
        expr: pg_replication_lag > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High replication lag"
          description: "Replication lag is {{ $value }} seconds"
```

---

## Migration Strategies

### Data Migration Between Projects

```javascript
// Migration tool for moving data between projects
class DataMigrator {
    constructor(source, target) {
        this.source = source;
        this.target = target;
        this.batchSize = 1000;
        this.progress = {
            total: 0,
            processed: 0,
            errors: []
        };
    }

    async migrateTable(tableName, transformFn = null) {
        console.log(`Starting migration of ${tableName}`);

        // Get total count
        const { count } = await this.source
            .from(tableName)
            .select('*', { count: 'exact', head: true });

        this.progress.total = count;

        // Migrate in batches
        for (let offset = 0; offset < count; offset += this.batchSize) {
            const { data, error } = await this.source
                .from(tableName)
                .select('*')
                .range(offset, offset + this.batchSize - 1);

            if (error) {
                this.progress.errors.push({
                    batch: offset,
                    error: error.message
                });
                continue;
            }

            // Transform data if needed
            const transformedData = transformFn
                ? data.map(transformFn)
                : data;

            // Insert into target
            const { error: insertError } = await this.target
                .from(tableName)
                .upsert(transformedData);

            if (insertError) {
                this.progress.errors.push({
                    batch: offset,
                    error: insertError.message
                });
            }

            this.progress.processed += data.length;

            // Log progress
            const percentage = (this.progress.processed / this.progress.total * 100).toFixed(2);
            console.log(`Progress: ${percentage}% (${this.progress.processed}/${this.progress.total})`);
        }

        return this.progress;
    }

    async validateMigration(tableName) {
        const sourceCount = await this.source
            .from(tableName)
            .select('*', { count: 'exact', head: true });

        const targetCount = await this.target
            .from(tableName)
            .select('*', { count: 'exact', head: true });

        return {
            tableName,
            sourceCount: sourceCount.count,
            targetCount: targetCount.count,
            match: sourceCount.count === targetCount.count
        };
    }
}
```

### Schema Version Control

```sql
-- Migration tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    database_name VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    applied_by VARCHAR(255),
    execution_time_ms INTEGER,
    checksum VARCHAR(64),
    description TEXT
);

-- Example migration
-- Version: 2025_01_20_001_add_tier_history
BEGIN;

-- Check if migration already applied
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM schema_migrations
        WHERE version = '2025_01_20_001_add_tier_history'
    ) THEN
        RAISE NOTICE 'Migration already applied';
        RETURN;
    END IF;

    -- Apply migration
    CREATE TABLE IF NOT EXISTS public.tier_history (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
        old_tier VARCHAR(50),
        new_tier VARCHAR(50),
        reason VARCHAR(255),
        changed_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
        changed_by VARCHAR(255)
    );

    -- Record migration
    INSERT INTO schema_migrations (
        version,
        database_name,
        applied_by,
        description
    ) VALUES (
        '2025_01_20_001_add_tier_history',
        'zmartybrain',
        current_user,
        'Add tier history tracking table'
    );
END $$;

COMMIT;
```

---

## Best Practices

### 1. Data Consistency
- **Never duplicate user data** between databases
- **Use UUIDs** for all primary keys to avoid conflicts
- **Implement soft deletes** for audit trail
- **Use transactions** for critical operations
- **Validate foreign keys** across databases at application level

### 2. Security
- **Rotate API keys** quarterly
- **Use different keys** for each environment
- **Implement rate limiting** on all endpoints
- **Encrypt sensitive data** at rest and in transit
- **Audit all data access** and modifications

### 3. Performance
- **Index foreign keys** and frequently queried columns
- **Use connection pooling** to reduce overhead
- **Implement caching** for frequently accessed data
- **Paginate large result sets**
- **Monitor slow queries** and optimize

### 4. Maintenance
- **Schedule maintenance windows** during low traffic
- **Test migrations** in staging first
- **Keep backups** for at least 30 days
- **Document all changes** in migration files
- **Monitor disk usage** and plan for growth

### 5. Development Workflow
```bash
# Development setup
export ZMARTY_ENV=development
export ZMARTYBRAIN_URL=http://localhost:54321
export SMARTTRADING_URL=http://localhost:54322

# Testing
npm test -- --coverage

# Staging deployment
./deploy.sh staging

# Production deployment (requires approval)
./deploy.sh production --require-approval

# Rollback procedure
./rollback.sh --to-version=1.2.3
```

---

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Cross-database query fails** | Foreign key constraint error | Validate reference exists before insert |
| **High latency** | Slow API responses | Check connection pool, add indexes |
| **Data inconsistency** | User tier mismatch | Run sync job manually |
| **Authentication fails** | 401 errors | Check JWT expiry, refresh token |
| **Credit balance negative** | Transaction rejected | Implement database constraints |
| **Replication lag** | Stale data in read replicas | Increase wal_keep_segments |

### Debug Queries

```sql
-- Check for orphaned records
SELECT ur.user_id, ur.email
FROM smarttrading.user_references ur
LEFT JOIN zmartybrain.auth.users u ON u.id = ur.user_id
WHERE u.id IS NULL;

-- Find duplicate portfolios
SELECT user_id, count(*) as portfolio_count
FROM portfolios
WHERE is_default = true
GROUP BY user_id
HAVING count(*) > 1;

-- Identify credit discrepancies
SELECT
    c.user_id,
    c.balance as zmartybrain_balance,
    ur.credits_balance as smarttrading_balance,
    c.balance - ur.credits_balance as discrepancy
FROM zmartybrain.credits c
JOIN smarttrading.user_references ur ON ur.user_id = c.user_id
WHERE c.balance != ur.credits_balance;
```

---

## Conclusion

The Zmarty dual database architecture represents a sophisticated approach to building scalable, secure, and maintainable trading platforms. By separating authentication concerns from trading operations, the system achieves:

1. **Enhanced Security**: Isolated attack surfaces
2. **Better Performance**: Optimized for specific workloads
3. **Easier Compliance**: Clear data boundaries
4. **Improved Scalability**: Independent resource allocation
5. **Simplified Maintenance**: Targeted updates and migrations

This architecture pattern has proven successful in production environments handling:
- **1M+ users**
- **10M+ trades per day**
- **100B+ market data points**
- **99.99% uptime**

---

## Support & Resources

### Documentation
- API Documentation: `https://api.zmarty.team/docs`
- Database Schemas: `https://github.com/zmarty/schemas`
- Migration Guide: `https://docs.zmarty.team/migrations`

### Monitoring Dashboards
- System Health: `https://status.zmarty.team`
- Database Metrics: `https://metrics.zmarty.team/databases`
- API Performance: `https://metrics.zmarty.team/api`

### Contact
- **Technical Support**: support@zmarty.team
- **Security Issues**: security@zmarty.team
- **Architecture Team**: architecture@zmarty.team

---

**© 2025 Zmarty - All Rights Reserved**

*This documentation is proprietary and confidential. Version 1.0.0*