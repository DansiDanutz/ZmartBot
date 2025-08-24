# ZmartBot - OUR ONLY TRADING STRATEGY ⚠️

## IMPORTANT: This is the ONLY strategy we use!

### ❌ NO STOP LOSS - We NEVER use stop loss

### ✅ Our Vault Position Manager Strategy

## Position Opening
- **Initial Position**: 2% of vault balance at 20X leverage
- **Maximum**: 2 positions per vault

## Position Doubling (When Price Drops)
1. **Stage 1 (Initial)**: 2% balance at 20X leverage
2. **Stage 2 (Double)**: 4% balance at 10X leverage  
3. **Stage 3 (Double)**: 8% balance at 5X leverage
4. **Stage 4 (Double)**: 16% balance at 2X leverage
5. **Stage 5 (Margin)**: 15% balance as margin (no leverage)

**Total Maximum Risk**: 45% of vault balance

## Take Profit Rules
- **TP Target**: 175% of total margin invested
- **Partial Close**: Close 50% of position when TP is hit
- **Trailing Stop**: Activated at 2% below max price (ONLY after TP)

## Risk Management
- **NO STOP LOSS** - We double positions instead
- **Maximum 2 positions** per vault
- **Leverage decreases** as position increases
- **Liquidation protection** through leverage reduction

## File Location
The ONLY correct strategy implementation is in:
```
backend/zmart-api/src/services/vault_position_manager.py
```

## Example with $100 Vault
1. Signal triggers → Open 2% ($2) at 20X = $40 position
2. If price drops → Add 4% ($4) at 10X = $40 more
3. Keep doubling with decreasing leverage
4. Take profit at 175% of total margin
5. NO STOP LOSS at any point

---

**NEVER** use any other strategy. This is our ONLY trading system.