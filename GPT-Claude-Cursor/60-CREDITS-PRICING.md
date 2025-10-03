# Credits Pricing Model

## Overview

This document defines the **credits pricing structure** for LLM usage in the Zmarty platform. Credits are the internal currency users spend to interact with AI models.

---

## Pricing Table

| Provider | Input (per 1K tokens) | Output (per 1K tokens) | Min Call Cost | Use Case |
|----------|----------------------|------------------------|---------------|----------|
| **Grok** (XAI) | 1 credit | 4 credits | 1 credit | Default, general chat |
| **GPT** (OpenAI) | 3 credits | 10 credits | 2 credits | Tool use, complex queries |
| **Claude** (Anthropic) | 3 credits | 10 credits | 2 credits | Deep reasoning, analysis |
| **Data** (Ingestion) | 1 credit | 0 credits | 1 credit | Symbol data fetching |

---

## Pricing Formula

For each LLM call, calculate total credits charged:

```bash
total_credits = ceil(
  (input_tokens / 1000) * input_per_1k +
  (output_tokens / 1000) * output_per_1k +
  min_call
)
```

### Examples

**Example 1: Grok Call**

- Input: 500 tokens
- Output: 1000 tokens
- Calculation: `ceil((500/1000)*1 + (1000/1000)*4 + 1) = ceil(0.5 + 4 + 1) = 6 credits`

**Example 2: GPT Call**

- Input: 1500 tokens
- Output: 2000 tokens
- Calculation: `ceil((1500/1000)*3 + (2000/1000)*10 + 2) = ceil(4.5 + 20 + 2) = 27 credits`

**Example 3: Claude Call**

- Input: 2000 tokens
- Output: 3000 tokens
- Calculation: `ceil((2000/1000)*3 + (3000/1000)*10 + 2) = ceil(6 + 30 + 2) = 38 credits`

**Example 4: Data Ingestion**

- Per symbol fetch: 1 credit (flat rate)

---

## User Tiers

### Free Tier
- **Starting Credits**: 100 credits (one-time bonus on signup)
- **Top-Up**: Not available (upgrade required)
- **Max Tokens/Request**: 1024
- **Max Requests/Minute**: 10
- **Features**:
  - ✅ Basic chat
  - ✅ 1 watched symbol
  - ❌ Voice mode
  - ❌ Multi-symbol analysis
  - ❌ Backtesting

**Typical Usage**: ~20 chat requests with Grok before credits run out

---

### Pro Tier ($19/month)
- **Monthly Credits**: 1000 credits
- **Top-Up**: Available ($10 for 500 credits)
- **Max Tokens/Request**: 4096
- **Max Requests/Minute**: 100
- **Features**:
  - ✅ All Free features
  - ✅ Voice mode
  - ✅ Up to 10 watched symbols
  - ✅ Multi-symbol analysis
  - ❌ Backtesting

**Typical Usage**: ~150-200 chat requests per month with Grok

---

### Enterprise Tier (Contact Sales)
- **Monthly Credits**: 5000+ credits (custom)
- **Top-Up**: Unlimited
- **Max Tokens/Request**: 8192
- **Max Requests/Minute**: 1000
- **Features**:
  - ✅ All Pro features
  - ✅ Unlimited watched symbols
  - ✅ Backtesting
  - ✅ Custom strategies
  - ✅ API access
  - ✅ Priority support

---

## Credit Operations

### Earning Credits

| Action | Credits Awarded | Description |
|--------|----------------|-------------|
| **Signup Bonus** | +100 | One-time on account creation |
| **Email Verification** | +50 | Verify email address |
| **Referral** | +200 | Refer a friend who signs up |
| **Monthly Subscription** | +1000 (Pro) | Recurring monthly |
| **Top-Up Purchase** | Variable | Buy credits as needed |
| **Promotion** | Variable | Special promotions/events |

### Spending Credits

| Action | Credits Cost | Description |
|--------|-------------|-------------|
| **Chat (Grok)** | 5-10 | Typical chat message |
| **Chat (GPT)** | 15-30 | Complex query with GPT |
| **Chat (Claude)** | 20-40 | Deep analysis with Claude |
| **Symbol Data Fetch** | 1 | Fetch indicators for 1 symbol |
| **Voice Response** | +5 | Add voice synthesis (if mode=voice) |

---

## Implementation

### Database Function (Supabase A)

This function is already implemented in `20-SCHEMA-SUPABASE-A.sql`:

```sql
CREATE OR REPLACE FUNCTION public.charge_user_credits(
  p_user_id UUID,
  p_amount INTEGER,
  p_provider TEXT,
  p_units JSONB DEFAULT '{}'::JSONB,
  p_reason TEXT DEFAULT 'chat_request',
  p_metadata JSONB DEFAULT '{}'::JSONB
)
RETURNS JSONB AS $$
DECLARE
  v_current_balance INTEGER;
  v_new_balance INTEGER;
BEGIN
  -- Get current balance
  v_current_balance := public.get_user_credits(p_user_id);

  -- Check if user has sufficient credits
  IF v_current_balance < p_amount THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'insufficient_credits',
      'current_balance', v_current_balance,
      'required', p_amount
    );
  END IF;

  -- Insert charge transaction
  INSERT INTO public.credits_ledger (user_id, delta, provider, units, reason, metadata)
  VALUES (p_user_id, -p_amount, p_provider, p_units, p_reason, p_metadata);

  -- Calculate new balance
  v_new_balance := v_current_balance - p_amount;

  RETURN jsonb_build_object(
    'success', true,
    'previous_balance', v_current_balance,
    'new_balance', v_new_balance,
    'charged', p_amount
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Usage in Orchestrator API

```typescript
// After LLM call completes
const pricing = {
  grok: { input_per_1k: 1, output_per_1k: 4, min_call: 1 },
  gpt: { input_per_1k: 3, output_per_1k: 10, min_call: 2 },
  claude: { input_per_1k: 3, output_per_1k: 10, min_call: 2 },
};

const price = pricing[provider];

const creditsToCharge = Math.ceil(
  (usage.input_tokens / 1000) * price.input_per_1k +
  (usage.output_tokens / 1000) * price.output_per_1k +
  price.min_call
);

// Charge user
const { data, error } = await supabaseA.rpc('charge_user_credits', {
  p_user_id: userId,
  p_amount: creditsToCharge,
  p_provider: provider,
  p_units: {
    input_tokens: usage.input_tokens,
    output_tokens: usage.output_tokens,
  },
  p_reason: 'chat_request',
  p_metadata: {
    message: message.substring(0, 100),  // First 100 chars
    model: provider,
  },
});

if (error || !data.success) {
  throw new Error('Failed to charge credits');
}

console.log(`💳 Charged ${creditsToCharge} credits to user ${userId}`);
```

---

## Price Optimization Strategies

### 1. Use Grok by Default
- **Cheapest**: 5-10 credits per typical chat
- **Fastest**: Lower latency
- **Good Enough**: Handles 80% of queries well

### 2. Smart Routing
- Detect when GPT/Claude needed:
  - Keywords: "analyze deeply", "explain why", "calculate", "tools"
  - Previous message context: If Grok couldn't answer well
- Only use expensive models when necessary

### 3. Response Caching
- Cache common queries:
  - "What is BTC signal?" → Cache for 5 minutes
  - "Explain RSI" → Cache indefinitely (educational)
- Save ~30% on repeat queries

### 4. Token Optimization
- **Prompt Engineering**: Keep prompts concise
- **Context Pruning**: Only include relevant signals (not all user symbols)
- **Response Limits**: Set max_tokens appropriately per tier

---

## Business Model

### Revenue Streams

1. **Subscriptions**:
   - Pro: $19/month → 1000 credits/month
   - Enterprise: Custom pricing
2. **Top-Ups**:
   - $10 → 500 credits (0.02 per credit)
   - $50 → 3000 credits (0.0167 per credit) - 15% discount
   - $100 → 7000 credits (0.0143 per credit) - 30% discount
3. **Referrals**:
   - Referrer gets 200 credits
   - Referee gets 50 bonus credits

### Cost Structure (Example)

Assuming:

- **Grok**: $0.0001 per 1K tokens (input/output average)
- **GPT**: $0.001 per 1K tokens
- **Claude**: $0.0015 per 1K tokens

**Our Credit Costs**:

- **Grok**: ~0.0002 per credit
- **GPT**: ~0.0005 per credit
- **Claude**: ~0.0007 per credit

**Profit Margin**:

- Selling at $0.02 per credit (top-up)
- Cost: $0.0002-0.0007 per credit (depending on model)
- **Margin**: 97-99% (high margin due to bundling and routing to cheap model)

---

## Monitoring Credits

### User Dashboard

Show in frontend:

```typescript
Current Balance: 450 credits
Last 5 Transactions:

- Chat with Grok: -5 credits (2 minutes ago)
- Chat with GPT: -15 credits (1 hour ago)
- Symbol data fetch: -1 credit (3 hours ago)
- Referral bonus: +200 credits (1 day ago)

```

### Admin Dashboard

Show aggregate stats:

- Total credits in circulation
- Credits charged per provider (today, this week, this month)
- Top users by credits spent
- Average credits per chat request
- Provider distribution (% using Grok vs GPT vs Claude)

---

## Alerts & Thresholds

### User Alerts

- **Low balance**: Alert when < 20 credits remaining
- **Out of credits**: Show top-up modal
- **Large charge**: Alert if single request > 50 credits

### System Alerts

- **High burn rate**: Alert if credits/hour > threshold
- **Provider cost spike**: Alert if provider costs increase > 20%
- **Fraud detection**: Alert if user uses > 1000 credits in 1 hour

---

## Adjusting Prices

To change pricing:

1. Update this file (`60-CREDITS-PRICING.md`)
2. Update env vars in Render (API service)
3. Restart orchestrator-api service
4. Update frontend pricing display
5. Notify users of changes (if increasing)

**Grandfathering**: Consider honoring old prices for existing subscribers for 30 days

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Pricing Model Complete



