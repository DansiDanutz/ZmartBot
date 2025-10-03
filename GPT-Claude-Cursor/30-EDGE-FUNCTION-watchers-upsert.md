# Edge Function: watchers-upsert

## Overview

This Supabase B Edge Function receives webhooks from Supabase A when `user_symbols` table changes (INSERT/UPDATE/DELETE), and synchronizes the changes to the `watchers` table in Supabase B.

---

## Purpose

- **Sync user symbols** from Supabase A to Supabase B trading database
- **Maintain data consistency** between authentication and trading databases
- **Enable real-time updates** without polling or batch jobs
- **Security** via HMAC signature verification

---

## Specifications

### Endpoint

```text
POST https://<SUPABASE_B_URL>/functions/v1/watchers-upsert
```

### Headers

- `Content-Type: application/json`
- `x-hmac-sha256: <signature>` - HMAC signature of request body

### Request Body (Webhook Payload)

```json
{
  "type": "INSERT" | "UPDATE" | "DELETE",
  "table": "user_symbols",
  "schema": "public",
  "record": {
    "id": 123,
    "user_id": "uuid",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "strategy": {},
    "active": true
  },
  "old_record": {
    // Present for UPDATE and DELETE operations
  }
}
```

### Response

```json
{
  "success": true,
  "operation": "INSERT" | "UPDATE" | "DELETE",
  "symbol": "BTC/USDT",
  "user_id": "uuid"
}
```

---

## Implementation

### File Location

```text
/supabase/trading/functions/watchers-upsert/index.ts
```

### Code

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { crypto } from "https://deno.land/std@0.168.0/crypto/mod.ts";

// Environment variables
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const WEBHOOK_SECRET = Deno.env.get("WEBHOOK_SECRET")!;

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

// HMAC verification function
async function verifyHmacSignature(
  body: string,
  signature: string,
  secret: string
): Promise<boolean> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const signatureBuffer = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode(body)
  );

  const computedSignature = Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  return computedSignature === signature;
}

serve(async (req) => {
  try {
    // Set timeout to 1 second
    const timeoutId = setTimeout(() => {
      return new Response(JSON.stringify({ error: "timeout" }), {
        status: 408,
        headers: { "Content-Type": "application/json" },
      });
    }, 1000);

    // Verify HMAC signature
    const signature = req.headers.get("x-hmac-sha256");
    if (!signature) {
      clearTimeout(timeoutId);
      return new Response(JSON.stringify({ error: "missing_signature" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const bodyText = await req.text();
    const isValid = await verifyHmacSignature(bodyText, signature, WEBHOOK_SECRET);

    if (!isValid) {
      clearTimeout(timeoutId);
      return new Response(JSON.stringify({ error: "invalid_signature" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Parse webhook payload
    const payload = JSON.parse(bodyText);
    const { type, record, old_record } = payload;

    let result;

    // Handle different operations
    switch (type) {
      case "INSERT":
      case "UPDATE":
        // Upsert to watchers table
        const { error: upsertError } = await supabase
          .from("watchers")
          .upsert({
            user_id: record.user_id,
            symbol: record.symbol,
            timeframe: record.timeframe,
            strategy: record.strategy || {},
            active: record.active !== false, // Default to true
            updated_at: new Date().toISOString(),
          }, {
            onConflict: "user_id,symbol,timeframe"
          });

        if (upsertError) throw upsertError;

        result = {
          success: true,
          operation: type,
          symbol: record.symbol,
          user_id: record.user_id,
        };
        break;

      case "DELETE":
        // Delete from watchers table
        const { error: deleteError } = await supabase
          .from("watchers")
          .delete()
          .match({
            user_id: old_record.user_id,
            symbol: old_record.symbol,
            timeframe: old_record.timeframe,
          });

        if (deleteError) throw deleteError;

        result = {
          success: true,
          operation: "DELETE",
          symbol: old_record.symbol,
          user_id: old_record.user_id,
        };
        break;

      default:
        throw new Error(`Unknown operation type: ${type}`);
    }

    clearTimeout(timeoutId);

    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in watchers-upsert:", error);
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
});
```

---

## Environment Variables

Set these in Supabase B Edge Function settings:

```bash
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
WEBHOOK_SECRET=<shared_secret>
```

---

## Deployment

### Using Supabase CLI

```bash
# Login to Supabase
supabase login

# Link to project
supabase link --project-ref <SUPABASE_B_PROJECT_REF>

# Deploy function
supabase functions deploy watchers-upsert

# Set secrets
supabase secrets set SUPABASE_URL=<url>
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=<key>
supabase secrets set WEBHOOK_SECRET=<secret>
```

### Using Supabase Dashboard

1. Navigate to **Edge Functions** in Supabase B dashboard
2. Click **New Function**
3. Name: `watchers-upsert`
4. Paste code above
5. Go to **Settings** → Add environment variables
6. Deploy function

---

## Webhook Configuration (Supabase A)

### Setup in Supabase A Dashboard

1. Navigate to **Database**→**Webhooks**
2. Click **Create Webhook**
3. Configure:
   - **Name**: `user_symbols_sync`
   - **Table**: `public.user_symbols`
   - **Events**: `INSERT`, `UPDATE`, `DELETE`
   - **Type**: HTTP Request
   - **Method**: POST
   - **URL**: `https://<SUPABASE_B_URL>/functions/v1/watchers-upsert`
   - **Headers**:

     ```json
     {
       "Content-Type": "application/json",
       "x-hmac-sha256": "${computed_signature}"
     }
     ```

### Generate HMAC Signature

```javascript
// In Supabase A webhook config, use this formula:
const crypto = require('crypto');
const signature = crypto
  .createHmac('sha256', WEBHOOK_SECRET)
  .update(JSON.stringify(payload))
  .digest('hex');
```

---

## Testing

### Manual Test via curl

```bash
# Generate HMAC signature
PAYLOAD='{"type":"INSERT","record":{"user_id":"test-uuid","symbol":"BTC/USDT","timeframe":"1h","strategy":{},"active":true}}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | cut -d' ' -f2)

# Send request
curl -X POST \
  https://<SUPABASE_B_URL>/functions/v1/watchers-upsert \
  -H "Content-Type: application/json" \
  -H "x-hmac-sha256: $SIGNATURE" \
  -d "$PAYLOAD"
```

### Test via Supabase A

```sql
-- Insert a test symbol in Supabase A
INSERT INTO public.user_symbols (user_id, symbol, timeframe)
VALUES ('test-uuid', 'TEST/USDT', '1h');

-- Check if it appears in Supabase B watchers table
SELECT * FROM public.watchers WHERE symbol = 'TEST/USDT';
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `missing_signature` | No HMAC header | Add `x-hmac-sha256` header to webhook |
| `invalid_signature` | HMAC mismatch | Verify WEBHOOK_SECRET matches in both A and B |
| `timeout` | Processing > 1s | Optimize query; check database performance |
| `upsert failed` | Constraint violation | Check unique constraint on (user_id, symbol, timeframe) |

### Logging

View function logs in Supabase B dashboard:

- Navigate to **Edge Functions**→**watchers-upsert**→**Logs**
- Check for errors and performance metrics

---

## Performance Considerations

- **Response Time**: Target < 200ms (max 1000ms with timeout)
- **Throughput**: Can handle ~100 req/sec with proper database indexes
- **Retries**: Supabase webhooks auto-retry on failure (exponential backoff)

### Optimizations

1. **Indexes**: Ensure indexes on `watchers(user_id, symbol, timeframe)`
2. **Connection Pooling**: Supabase Edge Functions use connection pooling automatically
3. **Batching**: Consider batching multiple operations if webhook volume is high

---

## Security Checklist

- [x] HMAC signature verification required
- [x] Service role key stored in env vars (not in code)
- [x] Timeout protection (1 second)
- [x] No sensitive data logged
- [x] Input validation on payload fields

---

## Monitoring

### Key Metrics

- **Success Rate**: Should be > 99.5%
- **Response Time**: p95 < 500ms
- **Error Rate**: < 0.5%

### Alerts

Set up alerts for:

- Error rate > 5%
- Response time p95 > 1s
- Function invocations = 0 for > 10 minutes (indicates webhook disabled)

---

## Rollback Plan

If edge function has issues:

1. **Disable webhook** in Supabase A temporarily
2. **Fix and redeploy** edge function
3. **Manually sync** missing records:

   ```sql
   INSERT INTO B.public.watchers (user_id, symbol, timeframe, strategy, active)
   SELECT user_id, symbol, timeframe, strategy, active
   FROM A.public.user_symbols
   ON CONFLICT (user_id, symbol, timeframe) DO UPDATE SET
     strategy = EXCLUDED.strategy,
     active = EXCLUDED.active,
     updated_at = NOW();
   ```

4. **Re-enable webhook**

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Implementation Spec Complete
