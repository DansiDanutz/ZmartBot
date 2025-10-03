# API Contracts Specification

## Overview

This document defines the **API request/response formats** for all Zmarty services. Use this as the authoritative reference when implementing or consuming APIs.

---

## Authentication

All API requests require a JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

JWT tokens are issued by Supabase A on user login and contain:

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "authenticated",
  "exp": 1234567890
}
```

---

## Orchestrator API

### POST /chat

**Description**: Send a chat message to Zmarty AI

**Request**:

```http
POST /chat HTTP/1.1
Host: orchestrator-api.onrender.com
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "What's the signal for BTC?",
  "mode": "text" | "voice",
  "stream": true | false,
  "context": {
    "include_signals": true,
    "include_win_rates": true,
    "symbols": ["BTC/USDT", "ETH/USDT"]  // Optional filter
  }
}
```

**Response** (non-streaming):

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "provider": "grok" | "gpt" | "claude",
  "text": "The current signal for BTC/USDT on 1h timeframe is LONG with a score of 0.85...",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 300,
    "total_tokens": 450
  },
  "credits_charged": 5,
  "credits_remaining": 445,
  "audio_url": "https://elevenlabs.io/audio/xyz.mp3",  // Only if mode=voice
  "metadata": {
    "latency_ms": 523,
    "model_version": "grok-2",
    "timestamp": "2025-09-30T12:00:00Z"
  }
}
```

**Response** (streaming with Server-Sent Events):

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"type":"start","provider":"grok","timestamp":"2025-09-30T12:00:00Z"}

data: {"type":"token","content":"The"}

data: {"type":"token","content":" current"}

data: {"type":"token","content":" signal"}

data: {"type":"token","content":" for"}

data: {"type":"token","content":" BTC/USDT"}

data: {"type":"done","usage":{"input_tokens":150,"output_tokens":300},"credits_charged":5,"audio_url":"https://..."}
```

**Error Responses**:

```http
HTTP/1.1 401 Unauthorized
{
  "error": "invalid_token",
  "message": "JWT token is invalid or expired"
}

HTTP/1.1 402 Payment Required
{
  "error": "insufficient_credits",
  "balance": 2,
  "required": 5,
  "message": "You need 5 credits but only have 2"
}

HTTP/1.1 429 Too Many Requests
{
  "error": "rate_limit_exceeded",
  "limit": 60,
  "retry_after": 45,
  "message": "Rate limit: 60 requests per minute"
}

HTTP/1.1 503 Service Unavailable
{
  "error": "all_providers_failed",
  "message": "All LLM providers are currently unavailable"
}
```

---

### GET /healthz

**Description**: Check service health

**Request**:

```http
GET /healthz HTTP/1.1
Host: orchestrator-api.onrender.com
```

**Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "healthy" | "degraded" | "unhealthy",
  "timestamp": "2025-09-30T12:00:00Z",
  "uptime_seconds": 86400,
  "version": "1.0.0",
  "services": {
    "supabase_a": {
      "status": "ok",
      "latency_ms": 45
    },
    "supabase_b": {
      "status": "ok",
      "latency_ms": 52
    },
    "grok": {
      "status": "ok",
      "latency_ms": 320
    },
    "gpt": {
      "status": "ok",
      "latency_ms": 450
    },
    "claude": {
      "status": "ok",
      "latency_ms": 680
    }
  },
  "queues": {
    "ingest_indicators": {
      "depth": 5,
      "processing": true
    },
    "compute_signals": {
      "depth": 2,
      "processing": true
    },
    "compute_winrate": {
      "depth": 0,
      "processing": true
    }
  }
}
```

**Degraded Response** (one or more services down):

```http
HTTP/1.1 200 OK

{
  "status": "degraded",
  "services": {
    "supabase_a": { "status": "ok" },
    "supabase_b": { "status": "ok" },
    "grok": { "status": "error", "error": "connection_timeout" },
    "gpt": { "status": "ok" },
    "claude": { "status": "ok" }
  }
}
```

**Unhealthy Response** (critical services down):

```http
HTTP/1.1 503 Service Unavailable

{
  "status": "unhealthy",
  "services": {
    "supabase_a": { "status": "error", "error": "connection_refused" },
    "supabase_b": { "status": "ok" }
  }
}
```

---

## Webhook (Supabase A → Supabase B)

### Payload Format

**Operation**: INSERT

```json
{
  "type": "INSERT",
  "table": "user_symbols",
  "schema": "public",
  "record": {
    "id": 123,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "strategy": {
      "type": "momentum",
      "params": { "period": 14 }
    },
    "active": true,
    "created_at": "2025-09-30T12:00:00Z"
  },
  "old_record": null
}
```

**Operation**: UPDATE

```json
{
  "type": "UPDATE",
  "table": "user_symbols",
  "schema": "public",
  "record": {
    "id": 123,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "strategy": {
      "type": "breakout",
      "params": { "threshold": 0.05 }
    },
    "active": true,
    "updated_at": "2025-09-30T12:05:00Z"
  },
  "old_record": {
    "id": 123,
    "strategy": {
      "type": "momentum",
      "params": { "period": 14 }
    }
  }
}
```

**Operation**: DELETE

```json
{
  "type": "DELETE",
  "table": "user_symbols",
  "schema": "public",
  "record": null,
  "old_record": {
    "id": 123,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "BTC/USDT",
    "timeframe": "1h"
  }
}
```

### Headers

```http
POST /functions/v1/watchers-upsert HTTP/1.1
Host: <supabase-b-url>
Content-Type: application/json
x-hmac-sha256: <hmac_signature>

<payload_json>
```

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "operation": "INSERT" | "UPDATE" | "DELETE",
  "symbol": "BTC/USDT",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-09-30T12:00:00Z"
}
```

---

## Frontend Integration

### Example: Fetch Chat Response

```javascript
async function sendChatMessage(message, mode = 'text') {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch('https://orchestrator-api.onrender.com/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      mode,
      stream: false,
    }),
  });

  if (!response.ok) {
    const error = await response.json();

    if (error.error === 'insufficient_credits') {
      // Show top-up modal
      showTopUpModal(error.balance, error.required);
      return null;
    }

    throw new Error(error.message);
  }

  const data = await response.json();

  // Update credits display
  updateCreditsDisplay(data.credits_remaining);

  return data;
}
```

### Example: Streaming Chat Response

```javascript
async function sendChatMessageStreaming(message) {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch('https://orchestrator-api.onrender.com/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      stream: true,
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Process complete lines
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.substring(6));

        switch (data.type) {
          case 'start':
            console.log(`Provider: ${data.provider}`);
            break;
          case 'token':
            appendToChat(data.content);
            break;
          case 'done':
            updateCreditsDisplay(data.credits_charged);
            if (data.audio_url) playAudio(data.audio_url);
            break;
        }
      }
    }
  }
}
```

---

## Versioning

API versioning strategy:

- **v1**: Current version (no prefix needed)
- **v2**: Future version (prefix with `/v2/`)

**Example**: `/v2/chat` (when we introduce breaking changes)

**Deprecation Policy**:

- Announce 90 days before deprecating an API version
- Maintain old version for 180 days after deprecation notice

---

## Rate Limiting

### Limits by Tier

| Tier | Requests/Minute | Concurrent Requests | Max Tokens/Request |
|------|----------------|---------------------|-------------------|
| Free | 10 | 2 | 1024 |
| Pro | 100 | 10 | 4096 |
| Enterprise | 1000 | 50 | 8192 |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1696075200
```

---

## Error Codes Reference

| Code | Description | Resolution |
|------|-------------|------------|
| `invalid_token` | JWT invalid/expired | Re-authenticate |
| `insufficient_credits` | Not enough credits | Top up credits |
| `rate_limit_exceeded` | Too many requests | Wait for reset time |
| `message_too_long` | Message exceeds limit | Shorten message |
| `all_providers_failed` | All LLMs unavailable | Retry later |
| `invalid_request` | Malformed request | Check request format |
| `server_error` | Internal server error | Report to support |

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: API Contracts Complete


