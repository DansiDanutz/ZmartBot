# Orchestrator Worker Service

## Overview

The **Orchestrator Worker** is a background worker service (deployed on Render) that consumes message queues, ingests trading data, computes signals, and calculates win rates.

---

## Responsibilities

1. **Ingest Indicators**: Pull data from Cryptometer and KingFisher APIs
2. **Compute Signals**: Generate trading signals from 21 indicators + risk metrics
3. **Compute Win Rates**: Calculate historical signal accuracy
4. **Position Doubling Logic**: Apply guardrails for position sizing
5. **Error Handling**: Retry failed jobs with exponential backoff
6. **Observability**: Emit structured logs for monitoring

---

## Queue Consumers

### Consumer 1: ingest_indicators

**Queue**: `ingest_indicators`

**Message Format**:

```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "user_id": "uuid"
}
```

**Logic**:

1. Dequeue message from pgmq
2. Parse `{symbol, timeframe}`
3. Call **Cryptometer API** for technical indicators
4. Call **KingFisher API** for liquidation clusters
5. Write to `B.indicators` table
6. Write to `B.liq_clusters` table
7. Enqueue `compute_signals` for same symbol
8. ACK message on success
9. Retry on failure (max 3 attempts)

**Implementation**:

```typescript
async function processIngestIndicators(message: any) {
  const { symbol, timeframe } = message;

  try {
    // Fetch indicators from Cryptometer
    const indicators = await fetchCryptometerIndicators(symbol, timeframe);

    // Fetch liquidation clusters from KingFisher
    const liqClusters = await fetchKingFisherClusters(symbol);

    // Write to Supabase B
    await supabaseB.from('indicators').insert({
      symbol,
      timeframe,
      at: new Date().toISOString(),
      data: indicators,
      source: 'cryptometer',
    });

    await supabaseB.from('liq_clusters').insert({
      symbol,
      at: new Date().toISOString(),
      clusters: liqClusters,
    });

    // Enqueue signal computation
    await enqueueMessage('compute_signals', { symbol, timeframe });

    console.log(`✅ Ingested indicators for ${symbol} ${timeframe}`);
  } catch (error) {
    console.error(`❌ Failed to ingest indicators for ${symbol}:`, error);
    throw error;  // Will trigger retry
  }
}
```

---

### Consumer 2: compute_signals

**Queue**: `compute_signals`

**Message Format**:

```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h"
}
```

**Logic**:

1. Dequeue message
2. Fetch latest indicators from `B.indicators`
3. Fetch latest risk metrics from `B.risk_metric`
4. Fetch latest liquidation clusters from `B.liq_clusters`
5. **Combine 21 indicators** + risk + liq to compute:
   - Direction: `long` | `short` | `flat`
   - Score: 0-1 (confidence)
   - Entry price, stop loss, take profit levels
6. **Apply doubling guardrails** if applicable
7. Write to `B.signals` table
8. ACK message

**Implementation**:

```typescript
async function processComputeSignals(message: any) {
  const { symbol, timeframe } = message;

  try {
    // 1. Fetch latest data
    const indicators = await supabaseB.rpc('get_latest_indicators', {
      p_symbol: symbol,
      p_timeframe: timeframe
    });

    const riskMetric = await supabaseB
      .from('risk_metric')
      .select('metrics')
      .eq('symbol', symbol)
      .order('at', { ascending: false })
      .limit(1)
      .single();

    const liqClusters = await supabaseB
      .from('liq_clusters')
      .select('clusters')
      .eq('symbol', symbol)
      .order('at', { ascending: false })
      .limit(1)
      .single();

    // 2. Compute signal
    const signal = computeSignal(indicators, riskMetric, liqClusters);

    // 3. Apply doubling guardrails
    const adjustedSignal = applyDoublingGuardrails(symbol, signal);

    // 4. Write to signals table
    await supabaseB.from('signals').insert({
      symbol,
      timeframe,
      at: new Date().toISOString(),
      direction: adjustedSignal.direction,
      score: adjustedSignal.score,
      entry_price: adjustedSignal.entryPrice,
      stop_loss: adjustedSignal.stopLoss,
      take_profit: adjustedSignal.takeProfits,
      confidence: adjustedSignal.confidence,
      reasons: adjustedSignal.reasons,
    });

    console.log(`✅ Computed signal for ${symbol} ${timeframe}: ${adjustedSignal.direction}`);
  } catch (error) {
    console.error(`❌ Failed to compute signal for ${symbol}:`, error);
    throw error;
  }
}

function computeSignal(indicators: any, riskMetric: any, liqClusters: any) {
  // Example: 21 indicators logic (simplified)
  let score = 0;
  let reasons = {};

  // RSI
  if (indicators.rsi < 30) { score += 0.15; reasons.rsi_oversold = true; }
  if (indicators.rsi > 70) { score -= 0.15; reasons.rsi_overbought = true; }

  // MACD
  if (indicators.macd.value > indicators.macd.signal) { score += 0.1; reasons.macd_bullish = true; }

  // EMA Cross
  if (indicators.ema_20 > indicators.ema_50) { score += 0.1; reasons.ema_cross_bullish = true; }

  // ... (add 18 more indicators)

  // Risk adjustment
  if (riskMetric.metrics.volatility > 0.05) { score *= 0.8; reasons.high_volatility = true; }

  // Liquidation clusters
  const nearbyLiq = liqClusters.clusters.filter(c => Math.abs(c.price - indicators.price) / indicators.price < 0.02);
  if (nearbyLiq.length > 0) { score *= 0.9; reasons.liquidation_nearby = true; }

  // Determine direction
  let direction = 'flat';
  if (score > 0.6) direction = 'long';
  else if (score < -0.6) direction = 'short';

  return {
    direction,
    score: Math.abs(score),
    entryPrice: indicators.price,
    stopLoss: direction === 'long' ? indicators.price * 0.98 : indicators.price * 1.02,
    takeProfits: direction === 'long'
      ? [indicators.price * 1.02, indicators.price * 1.05, indicators.price * 1.10]
      : [indicators.price * 0.98, indicators.price * 0.95, indicators.price * 0.90],
    confidence: Math.abs(score),
    reasons,
  };
}
```

---

### Consumer 3: compute_winrate

**Queue**: `compute_winrate`

**Message Format**:

```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "lookback_days": 30
}
```

**Logic**:

1. Dequeue message
2. Fetch historical signals from `B.signals` (last N days)
3. For each signal, compare predicted direction vs actual price movement
4. Calculate: `win_rate = (winning_signals / total_signals)`
5. Write to `B.win_rate` table
6. ACK message

**Implementation**:

```typescript
async function processComputeWinrate(message: any) {
  const { symbol, timeframe, lookback_days = 30 } = message;

  try {
    // 1. Fetch historical signals
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - lookback_days);

    const { data: signals } = await supabaseB
      .from('signals')
      .select('*')
      .eq('symbol', symbol)
      .eq('timeframe', timeframe)
      .gte('at', cutoffDate.toISOString())
      .order('at', { ascending: true });

    if (!signals || signals.length === 0) {
      console.log(`⚠️ No signals found for ${symbol} in last ${lookback_days} days`);
      return;
    }

    // 2. Calculate win rate
    let wins = 0;

    for (const signal of signals) {
      // Fetch price movement after signal (e.g., 4 hours later)
      const futurePrice = await getPriceAt(symbol, signal.at, '4h');

      const priceChange = (futurePrice - signal.entry_price) / signal.entry_price;

      if (signal.direction === 'long' && priceChange > 0.01) wins++;  // 1% profit = win
      else if (signal.direction === 'short' && priceChange < -0.01) wins++;
    }

    const winRate = wins / signals.length;

    // 3. Write to win_rate table
    await supabaseB.from('win_rate').upsert({
      symbol,
      timeframe,
      lookback_days,
      win_rate: winRate,
      sample_size: signals.length,
      params: { strategy_version: 'v1' },
      computed_at: new Date().toISOString(),
    }, {
      onConflict: 'symbol,timeframe,lookback_days,coalesce((params->>\'strategy_version\'),\'v1\')'
    });

    console.log(`✅ Computed win rate for ${symbol}: ${(winRate * 100).toFixed(1)}% (n=${signals.length})`);
  } catch (error) {
    console.error(`❌ Failed to compute win rate for ${symbol}:`, error);
    throw error;
  }
}
```

---

## Position Doubling Guardrails

### Logic

When a signal improves (higher score than previous signal), consider doubling position size:

```typescript
function applyDoublingGuardrails(symbol: string, signal: any): any {
  // 1. Fetch previous signal
  const prevSignal = await supabaseB
    .from('signals')
    .select('*')
    .eq('symbol', symbol)
    .order('at', { ascending: false })
    .limit(1)
    .single();

  if (!prevSignal) return signal;  // First signal

  // 2. Check if score improved
  const SCORE_DELTA_THRESHOLD = parseFloat(process.env.SCORE_DELTA_THRESHOLD || '0.1');

  if (signal.score <= prevSignal.score + SCORE_DELTA_THRESHOLD) {
    return signal;  // No improvement
  }

  // 3. Check max position %
  const MAX_POSITION_PCT = parseFloat(process.env.MAX_POSITION_PCT || '0.1');
  const currentPosition = await getCurrentPosition(symbol);
  const portfolioValue = await getPortfolioValue();

  if (currentPosition / portfolioValue >= MAX_POSITION_PCT) {
    console.log(`⚠️ Max position reached for ${symbol} (${MAX_POSITION_PCT * 100}%)`);
    return signal;
  }

  // 4. Check cooldown
  const COOLDOWN_SECONDS = parseInt(process.env.COOLDOWN_SECONDS || '3600');
  const timeSinceLastIncrease = (new Date().getTime() - new Date(prevSignal.at).getTime()) / 1000;

  if (timeSinceLastIncrease < COOLDOWN_SECONDS) {
    console.log(`⚠️ Cooldown active for ${symbol} (${COOLDOWN_SECONDS}s)`);
    return signal;
  }

  // 5. Check volatility
  const riskMetric = await supabaseB
    .from('risk_metric')
    .select('metrics')
    .eq('symbol', symbol)
    .order('at', { ascending: false })
    .limit(1)
    .single();

  const VOLATILITY_THRESHOLD = parseFloat(process.env.VOLATILITY_THRESHOLD || '0.05');

  if (riskMetric.metrics.volatility > VOLATILITY_THRESHOLD) {
    console.log(`⚠️ Volatility too high for ${symbol} (${riskMetric.metrics.volatility})`);
    return signal;
  }

  // 6. All guardrails passed - allow doubling
  console.log(`✅ Doubling position for ${symbol} (score improved from ${prevSignal.score} to ${signal.score})`);

  return {
    ...signal,
    metadata: {
      ...signal.metadata,
      position_doubled: true,
      previous_score: prevSignal.score,
    }
  };
}
```

---

## Main Worker Loop

```typescript
async function main() {
  console.log('🚀 Orchestrator Worker started');

  // Start consumers in parallel
  await Promise.all([
    consumeQueue('ingest_indicators', processIngestIndicators),
    consumeQueue('compute_signals', processComputeSignals),
    consumeQueue('compute_winrate', processComputeWinrate),
  ]);
}

async function consumeQueue(queueName: string, handler: Function) {
  while (true) {
    try {
      // Read message from queue (with visibility timeout)
      const { data: messages } = await supabaseB.rpc('pgmq_read', {
        queue_name: queueName,
        vt: 30,  // 30 second visibility timeout
        qty: 1,
      });

      if (!messages || messages.length === 0) {
        await sleep(1000);  // No messages, wait 1 second
        continue;
      }

      const message = messages[0];

      // Process message
      await handler(message.message);

      // Delete message (ACK)
      await supabaseB.rpc('pgmq_delete', {
        queue_name: queueName,
        msg_id: message.msg_id,
      });

      // Log queue depth
      const { data: depth } = await supabaseB.rpc('pgmq_queue_depth', {
        queue_name: queueName,
      });

      console.log(`📊 Queue ${queueName}: depth=${depth}`);

    } catch (error) {
      console.error(`❌ Error in ${queueName} consumer:`, error);
      await sleep(5000);  // Backoff on error
    }
  }
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

main();
```

---

## Environment Variables

```bash
# Supabase B (Trading)
SUPABASE_B_URL=https://<project-ref>.supabase.co
SUPABASE_B_SERVICE_KEY=<service_role_key>

# External APIs
CRYPTOMETER_API_KEY=<key>
KINGFISHER_API_KEY=<key>

# Guardrails
MAX_POSITION_PCT=0.1          # 10% max position
COOLDOWN_SECONDS=3600         # 1 hour cooldown
VOLATILITY_THRESHOLD=0.05     # 5% volatility max
SCORE_DELTA_THRESHOLD=0.1     # 0.1 score improvement required
```

---

## Deployment (Render)

### render.yaml

```yaml
services:
  - type: worker
    name: orchestrator-worker
    env: node
    buildCommand: npm install && npm run build
    startCommand: npm run worker
    envVars:
      - key: SUPABASE_B_URL
        sync: false
      - key: SUPABASE_B_SERVICE_KEY
        sync: false
      - key: CRYPTOMETER_API_KEY
        sync: false
      - key: KINGFISHER_API_KEY
        sync: false
      - key: MAX_POSITION_PCT
        value: "0.1"
      - key: COOLDOWN_SECONDS
        value: "3600"
      - key: VOLATILITY_THRESHOLD
        value: "0.05"
```

---

## Monitoring

### Key Metrics

- Queue depth per queue
- Job processing time (p50, p95)
- Error rate per queue
- Retry rate
- Win rate accuracy

### Logging Example

```json
{
  "timestamp": "2025-09-30T12:00:00Z",
  "level": "info",
  "service": "orchestrator-worker",
  "queue": "compute_signals",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "job_ms": 850,
  "queue_depth": 12,
  "result": "success"
}
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Implementation Spec Complete


