# Orchestrator API Service

## Overview

The **Orchestrator API** is a web service (deployed on Render) that handles chat requests, routes them to appropriate LLM providers, and charges credits.

---

## Responsibilities

1. **JWT Verification**: Validate user tokens from Supabase A
2. **Context Gathering**: Fetch user symbols and recent signals
3. **Model Routing**: Route to Grok (default), GPT, or Claude based on requirements
4. **Credit Charging**: Deduct credits after successful LLM calls
5. **Response Streaming**: Stream text responses to frontend
6. **Voice Generation**: Optional ElevenLabs voice synthesis
7. **Health Monitoring**: Provide `/healthz` endpoint for system checks

---

## API Endpoints

### POST /chat

**Purpose**: Main chat endpoint for user queries

**Headers**:

- `Authorization: Bearer <jwt_token>` - Required
- `Content-Type: application/json`

**Request Body**:

```json
{
  "message": "What's the signal for BTC?",
  "mode": "text" | "voice",
  "stream": true,
  "context": {
    "include_signals": true,
    "include_win_rates": true
  }
}
```

**Response** (streaming):

```json
data: {"type":"start","provider":"grok"}
data: {"type":"token","content":"The"}
data: {"type":"token","content":" current"}
data: {"type":"token","content":" signal"}
data: {"type":"done","usage":{"input_tokens":150,"output_tokens":300},"audio_url":"https://..."}
```

**Response** (non-streaming):

```json
{
  "provider": "grok",
  "text": "The current signal for BTC/USDT is...",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 300
  },
  "credits_charged": 5,
  "audio_url": "https://elevenlabs.io/..."  // Optional if mode=voice
}
```

---

### GET /healthz

**Purpose**: Health check endpoint

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-09-30T12:00:00Z",
  "services": {
    "supabase_a": "ok",
    "supabase_b": "ok",
    "grok": "ok",
    "gpt": "ok",
    "claude": "ok"
  },
  "queue_depth": {
    "ingest_indicators": 5,
    "compute_signals": 2,
    "compute_winrate": 0
  }
}
```

---

## Implementation Guide

### Tech Stack

- **Language**: Node.js (TypeScript) or Python
- **Framework**: Express.js / FastAPI
- **Database Client**: `@supabase/supabase-js` or `supabase-py`
- **LLM SDKs**:
  - XAI SDK (Grok)
  - OpenAI SDK (GPT)
  - Anthropic SDK (Claude)
- **Voice**: ElevenLabs SDK

### File Structure

```text
services/orchestrator-api/
├── src/
│   ├── index.ts              # Main entry point
│   ├── routes/
│   │   ├── chat.ts           # /chat endpoint
│   │   └── healthz.ts        # /healthz endpoint
│   ├── middleware/
│   │   ├── auth.ts           # JWT verification
│   │   └── rateLimit.ts      # Rate limiting
│   ├── services/
│   │   ├── modelRouter.ts    # LLM routing logic
│   │   ├── contextBuilder.ts # Build context from DB
│   │   ├── creditsManager.ts # Credit charging
│   │   └── voiceService.ts   # ElevenLabs integration
│   └── utils/
│       ├── supabase.ts       # Supabase clients
│       └── logger.ts         # Structured logging
├── package.json
├── tsconfig.json
└── README.md

```

---

## Key Implementation Details

### 1. JWT Verification Middleware

```typescript
import { createClient } from '@supabase/supabase-js';
import { Request, Response, NextFunction } from 'express';

const supabaseA = createClient(
  process.env.SUPABASE_A_URL!,
  process.env.SUPABASE_A_SERVICE_KEY!
);

export async function verifyJWT(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'missing_token' });
  }

  const token = authHeader.substring(7);

  try {
    const { data: { user }, error } = await supabaseA.auth.getUser(token);

    if (error || !user) {
      return res.status(401).json({ error: 'invalid_token' });
    }

    req.user = user;  // Attach user to request
    next();
  } catch (error) {
    return res.status(500).json({ error: 'auth_error' });
  }
}
```

### 2. Context Builder

```typescript
export async function buildContext(userId: string): Promise<string> {
  // Fetch user's watched symbols from Supabase A
  const { data: symbols } = await supabaseA
    .from('user_symbols')
    .select('symbol, timeframe')
    .eq('user_id', userId)
    .eq('active', true);

  // Fetch recent signals from Supabase B
  const signalPromises = symbols.map(({ symbol, timeframe }) =>
    supabaseB.rpc('get_latest_signal', { p_symbol: symbol, p_timeframe: timeframe })
  );

  const signals = await Promise.all(signalPromises);

  // Build context string
  let context = "User's Watched Symbols and Signals:\n\n";

  symbols.forEach((sym, idx) => {
    const signal = signals[idx];
    context += `${sym.symbol} (${sym.timeframe}): `;

    if (signal) {
      context += `${signal.direction} signal, score ${signal.score}, confidence ${signal.confidence}\n`;
    } else {
      context += `No signal yet\n`;
    }
  });

  return context;
}
```

### 3. Model Router

```typescript
export async function routeToModel(
  message: string,
  context: string,
  userTier: string
): Promise<{ provider: string; response: string; usage: any }> {
  // Determine which model to use
  let provider = 'grok';  // Default

  if (message.includes('analyze deeply') || message.includes('explain why')) {
    provider = 'claude';  // Better reasoning
  } else if (message.includes('calculate') || message.includes('tool')) {
    provider = 'gpt';  // Better tool use
  }

  const maxTokens = getTierMaxTokens(userTier);

  try {
    // Try primary provider
    return await callLLM(provider, message, context, maxTokens);
  } catch (error) {
    // Fallback logic
    console.error(`${provider} failed, falling back...`);

    const fallbackOrder = provider === 'grok'
      ? ['gpt', 'claude']
      : provider === 'gpt'
        ? ['claude', 'grok']
        : ['gpt', 'grok'];

    for (const fallbackProvider of fallbackOrder) {
      try {
        return await callLLM(fallbackProvider, message, context, maxTokens);
      } catch (e) {
        continue;
      }
    }

    throw new Error('all_providers_failed');
  }
}

async function callLLM(
  provider: string,
  message: string,
  context: string,
  maxTokens: number
): Promise<any> {
  const prompt = `${context}\n\nUser: ${message}\n\nZmarty:`;

  switch (provider) {
    case 'grok':
      return await callGrok(prompt, maxTokens);
    case 'gpt':
      return await callGPT(prompt, maxTokens);
    case 'claude':
      return await callClaude(prompt, maxTokens);
    default:
      throw new Error(`unknown_provider: ${provider}`);
  }
}
```

### 4. Credits Manager

```typescript
export async function chargeCredits(
  userId: string,
  provider: string,
  inputTokens: number,
  outputTokens: number
): Promise<{ success: boolean; charged: number }> {
  // Get pricing from 60-CREDITS-PRICING.md
  const pricing = {
    grok: { input_per_1k: 1, output_per_1k: 4, min_call: 1 },
    gpt: { input_per_1k: 3, output_per_1k: 10, min_call: 2 },
    claude: { input_per_1k: 3, output_per_1k: 10, min_call: 2 },
  };

  const price = pricing[provider];

  const charge = Math.ceil(
    (inputTokens / 1000) * price.input_per_1k +
    (outputTokens / 1000) * price.output_per_1k +
    price.min_call
  );

  // Call Supabase A function to charge
  const { data, error } = await supabaseA.rpc('charge_user_credits', {
    p_user_id: userId,
    p_amount: charge,
    p_provider: provider,
    p_units: { input_tokens: inputTokens, output_tokens: outputTokens },
    p_reason: 'chat_request',
  });

  if (error || !data.success) {
    throw new Error('insufficient_credits');
  }

  return { success: true, charged: charge };
}
```

### 5. Chat Endpoint

```typescript
app.post('/chat', verifyJWT, async (req, res) => {
  const { message, mode = 'text', stream = false } = req.body;
  const userId = req.user.id;

  try {
    // 1. Build context
    const context = await buildContext(userId);

    // 2. Get user tier
    const { data: profile } = await supabaseA
      .from('user_profiles')
      .select('tier')
      .eq('id', userId)
      .single();

    // 3. Check credits
    const balance = await supabaseA.rpc('get_user_credits', { p_user_id: userId });
    if (balance < 5) {  // Minimum 5 credits required
      return res.status(402).json({ error: 'insufficient_credits', balance });
    }

    // 4. Route to LLM
    const { provider, response, usage } = await routeToModel(
      message,
      context,
      profile.tier
    );

    // 5. Charge credits
    const { charged } = await chargeCredits(
      userId,
      provider,
      usage.input_tokens,
      usage.output_tokens
    );

    // 6. Optional voice synthesis
    let audioUrl = null;
    if (mode === 'voice') {
      audioUrl = await synthesizeVoice(response);
    }

    // 7. Return response
    res.json({
      provider,
      text: response,
      usage,
      credits_charged: charged,
      audio_url: audioUrl,
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: error.message });
  }
});
```

---

## Environment Variables

```bash
# Supabase A (Chat)
SUPABASE_A_URL=https://<project-ref>.supabase.co
SUPABASE_A_SERVICE_KEY=<service_role_key>

# Supabase B (Trading)
SUPABASE_B_URL=https://<project-ref>.supabase.co
SUPABASE_B_SERVICE_KEY=<service_role_key>

# LLM Providers
XAI_API_KEY=<xai_key>          # Grok
OPENAI_API_KEY=<openai_key>     # GPT
ANTHROPIC_API_KEY=<anthropic_key>  # Claude

# Voice
ELEVENLABS_API_KEY=<elevenlabs_key>

# Optional
JWT_SECRET=<jwt_secret>
PORT=8080
NODE_ENV=production
```

---

## Deployment (Render)

### render.yaml

```yaml
services:
  - type: web
    name: orchestrator-api
    env: node
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: SUPABASE_A_URL
        sync: false
      - key: SUPABASE_A_SERVICE_KEY
        sync: false
      - key: SUPABASE_B_URL
        sync: false
      - key: SUPABASE_B_SERVICE_KEY
        sync: false
      - key: XAI_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: ELEVENLABS_API_KEY
        sync: false
```

---

## Testing

### Manual Test

```bash
# Get JWT token from Supabase A
TOKEN="<user_jwt_token>"

# Test /chat
curl -X POST http://localhost:8080/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the signal for BTC?","mode":"text"}'

# Test /healthz
curl http://localhost:8080/healthz
```

---

## Monitoring

### Key Metrics

- Request latency (p50, p95, p99)
- Error rate per endpoint
- Provider distribution (grok/gpt/claude usage %)
- Credits charged per request
- User tier distribution

### Logging Example

```json
{
  "timestamp": "2025-09-30T12:00:00Z",
  "level": "info",
  "service": "orchestrator-api",
  "endpoint": "/chat",
  "user_id": "uuid",
  "provider": "grok",
  "latency_ms": 523,
  "tokens": { "input": 150, "output": 300 },
  "credits_charged": 5
}
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Implementation Spec Complete
