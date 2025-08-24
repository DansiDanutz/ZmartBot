# 🚀 ZMARTBOT FINAL TRADING STRATEGY - DO NOT CHANGE

## ⚠️ CRITICAL: This is our ONLY strategy. Never deviate from this.

---

## 📋 STRATEGY OVERVIEW

### Core Principles
- **NO STOP LOSS** - We NEVER use stop loss
- **175% Take Profit** - Always target 175% of TOTAL margin invested
- **50% Partial Close** - Close 50% at TP, trail the rest
- **Maximum 45% Risk** - Never risk more than 45% of vault balance
- **Liquidation Clusters** - Use clusters for doubling decisions

---

## 💰 POSITION SIZING

### Stage Structure
| Stage | Vault % | Leverage | Position Size | Cumulative Margin |
|-------|---------|----------|---------------|-------------------|
| 1     | 2%      | 20X      | 40% of margin | $200 (on $10k)   |
| 2     | 4%      | 10X      | 40% of margin | $600             |
| 3     | 8%      | 5X       | 40% of margin | $1,400           |
| 4     | 16%     | 2X       | 32% of margin | $3,000           |
| 5     | 15%     | 0X       | Margin only   | $4,500 (MAX)     |

---

## 🎯 DOUBLING TRIGGERS

### Two Triggers ONLY:
1. **80% of TOTAL MARGIN lost** - When unrealized loss = 80% of total margin invested
2. **Hit Liquidation Cluster** - When price hits cluster AND liquidation is between/before clusters

### Liquidation Position Analysis:
```
BEFORE Clusters → Double at first cluster (critical)
BETWEEN Clusters → Double at first cluster (optimal)
AFTER Clusters → Wait for 80% margin loss
```

---

## 📊 PROFIT CALCULATIONS

### How Profit Scales:

| Scenario | Total Margin | TP Target (175%) | Profit | Vault ROI |
|----------|--------------|------------------|--------|-----------|
| No Double | $200 | $350 | $108 | 1.08% |
| 1 Double | $600 | $1,050 | $366 | 3.66% |
| 2 Doubles | $1,400 | $2,450 | $920 | 9.20% |
| 3 Doubles | $3,000 | $5,250 | $1,125 | 11.25% |
| Maximum | $4,500 | $7,875 | $1,687 | 16.88% |

### Profit Formula:
```
TP Target = Total Margin × 1.75
Profit Needed = TP Target - Total Margin
TP Price = Avg Entry × (1 + Profit Needed / Total Position Size)
Secured Profit = Profit Needed × 0.5 (50% close)
```

---

## 🔄 POSITION MANAGEMENT FLOW

### 1. Open Position
```python
margin = vault_balance * 0.02  # 2%
leverage = 20
position = margin * leverage
tp_target = margin * 1.75  # $350 on $200
```

### 2. Monitor & Double
```python
# Check doubling triggers
if margin_loss_pct >= 0.80:
    double_position()
elif price_hits_cluster and liquidation_between_clusters:
    double_position()
```

### 3. After Doubling
```python
# Recalculate everything
total_margin = sum(all_margins)
new_tp_target = total_margin * 1.75  # ALWAYS 175% of TOTAL
new_tp_price = calculate_based_on_new_target()
# Reset ALL previous targets
```

### 4. Take Profit
```python
if price >= tp_price:
    close_50_percent()
    activate_trailing_stop(2%)
    let_remaining_run()
```

---

## ⚠️ CRITICAL RULES

### NEVER:
- ❌ Use stop loss
- ❌ Close at loss
- ❌ Change the 175% rule
- ❌ Risk more than 45% of vault
- ❌ Ignore liquidation clusters

### ALWAYS:
- ✅ Target 175% of TOTAL margin
- ✅ Reset targets after doubling
- ✅ Close 50% at TP
- ✅ Use liquidation clusters for timing
- ✅ Wait for profit (no time limit)

---

## 📈 LIQUIDATION MANAGEMENT

### EFFECTIVE Leverage After Doubling:
The liquidation price is based on the WEIGHTED AVERAGE leverage, not individual stages.

#### Examples with $10,000 vault:

**After Stage 1 Only:**
- Margin: $200
- Position: $4,000
- Effective Leverage: 20X
- Liquidation: ~4.75% drop from entry

**After Stage 1 + 2:**
- Total Margin: $600
- Total Position: $8,000
- Effective Leverage: 13.3X
- Liquidation: ~7.1% drop from avg entry

**After Stages 1 + 2 + 3:**
- Total Margin: $1,400
- Total Position: $12,000
- Effective Leverage: 8.6X
- Liquidation: ~11% drop from avg entry

**After All 4 Stages:**
- Total Margin: $3,000
- Total Position: $15,200
- Effective Leverage: 5.1X
- Liquidation: ~18.6% drop from avg entry

**With Margin Injection (Stage 5):**
- Total Margin: $4,500
- Total Position: $15,200
- Effective Leverage: 3.4X
- Liquidation: ~28% drop from avg entry

### Protection Mechanism:
```
Effective Leverage = Total Position Size / Total Margin
Liquidation Distance = 0.95 / Effective Leverage
```

As we double, effective leverage DECREASES → liquidation moves FURTHER away

---

## 💡 WHY THIS WORKS

1. **No Stop Loss** = No realized losses, ever
2. **Doubling at Clusters** = We buy when others get liquidated
3. **Decreasing Leverage** = Protection as position grows
4. **175% Rule** = Consistent profit target that scales
5. **Time Independence** = We wait as long as needed

---

## 📁 IMPLEMENTATION

### Primary File:
```
backend/zmart-api/src/services/vault_position_manager.py
```

### Key Functions:
- `open_position()` - Opens with 2% at 20X
- `_check_and_execute_doubling()` - Monitors doubling triggers
- `_double_position()` - Executes doubling with TP reset
- `_execute_first_take_profit()` - Closes 50% at TP

### Liquidation Calculation:
```python
# Always calculate based on TOTAL position and TOTAL margin
effective_leverage = total_position_size / total_margin_invested
liquidation_distance = Decimal("0.95") / effective_leverage
liquidation_price = avg_entry_price * (1 - liquidation_distance)
```

---

## 🎯 SUMMARY

**This strategy is FINAL and UNCHANGEABLE.**

Every position follows the same rules:
1. Start with 2% at 20X
2. Double at clusters or 80% loss
3. Always target 175% of total margin
4. Close 50% at TP, trail the rest
5. Never close at loss

**Result**: Consistent profits that scale with market volatility.

---

*Last Updated: Strategy is FINAL - Do not change*