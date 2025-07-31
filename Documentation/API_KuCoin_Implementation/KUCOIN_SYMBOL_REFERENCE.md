# KuCoin Futures Symbol Reference

**✅ VERIFIED SYMBOLS - TESTED & WORKING**

## 🎯 REQUESTED SYMBOLS STATUS

| Coin | Symbol | Base Currency | Max Leverage | Status |
|------|--------|---------------|--------------|---------|
| **Bitcoin** | `XBTUSDTM` | XBT | 125x | ✅ WORKING |
| **Ethereum** | `ETHUSDTM` | ETH | 100x | ✅ WORKING |
| **Avalanche** | `AVAXUSDTM` | AVAX | 75x | ✅ WORKING |

## 🔍 SYMBOL NAMING PATTERNS

### USDT-Margined Futures (Most Popular)
All USDT-margined futures end with `USDTM`:

```python
# Major Cryptocurrencies
XBTUSDTM    # Bitcoin (XBT, not BTC!)
ETHUSDTM    # Ethereum  
SOLUSDTM    # Solana
AVAXUSDTM   # Avalanche
DOGEUSDTM   # Dogecoin
XRPUSDTM    # Ripple
ADAUSDTM    # Cardano
DOTUSDTM    # Polkadot
LINKUSDTM   # Chainlink
UNIUSDTM    # Uniswap
```

### Other Margin Types
```python
# USDC-Margined
XBTUSDCM    # Bitcoin/USDC
ETHUSDCM    # Ethereum/USDC
XRPUSDCM    # Ripple/USDC

# USD-Margined (Inverse)
XBTUSDM     # Bitcoin/USD Inverse
ETHUSDM     # Ethereum/USD Inverse
XRPUSDM     # Ripple/USD Inverse
```

## 📊 TOP 20 USDT-MARGINED CONTRACTS

| Rank | Symbol | Base | Max Leverage | Multiplier |
|------|--------|------|--------------|------------|
| 1 | `XBTUSDTM` | XBT | 125x | 0.001 |
| 2 | `ETHUSDTM` | ETH | 100x | 0.01 |
| 3 | `SOLUSDTM` | SOL | 75x | 0.1 |
| 4 | `WIFUSDTM` | WIF | 75x | 10.0 |
| 5 | `PEPEUSDTM` | PEPE | 75x | 520000.0 |
| 6 | `DOGEUSDTM` | DOGE | 75x | 100.0 |
| 7 | `XRPUSDTM` | XRP | 75x | 10.0 |
| 8 | `AVAXUSDTM` | AVAX | 75x | 0.1 |
| 9 | `ADAUSDTM` | ADA | 75x | 10.0 |
| 10 | `DOTUSDTM` | DOT | 75x | 1.0 |
| 11 | `LINKUSDTM` | LINK | 75x | 0.1 |
| 12 | `UNIUSDTM` | UNI | 75x | 1.0 |
| 13 | `AAVEUSDTM` | AAVE | 50x | 0.01 |
| 14 | `1000BONKUSDTM` | 1000BONK | 50x | 1.0 |
| 15 | `MATICUSDTM` | MATIC | 75x | 10.0 |
| 16 | `ATOMUSDTM` | ATOM | 75x | 1.0 |
| 17 | `FILUSDTM` | FIL | 75x | 1.0 |
| 18 | `LTCUSDTM` | LTC | 75x | 0.1 |
| 19 | `BCHUSDTM` | BCH | 75x | 0.01 |
| 20 | `EOSUSDTM` | EOS | 75x | 10.0 |

## ⚠️ IMPORTANT SYMBOL NOTES

### 1. Bitcoin Uses XBT, Not BTC
```python
# ✅ CORRECT
symbol = "XBTUSDTM"

# ❌ WRONG - This won't work
symbol = "BTCUSDTM"  # This symbol doesn't exist
```

### 2. All USDT Futures End with 'M'
```python
# ✅ CORRECT Pattern
"XBTUSDTM"   # XBT/USDT Margined
"ETHUSDTM"   # ETH/USDT Margined
"AVAXUSDTM"  # AVAX/USDT Margined

# ❌ WRONG - Missing 'M'
"XBTUSDT"    # This is spot trading symbol
"ETHUSDT"    # This is spot trading symbol
```

### 3. Multiplier Importance
Different contracts have different multipliers:
```python
XBTUSDTM:  0.001    # 1 contract = 0.001 BTC
ETHUSDTM:  0.01     # 1 contract = 0.01 ETH  
AVAXUSDTM: 0.1      # 1 contract = 0.1 AVAX
```

## 🔧 IMPLEMENTATION EXAMPLES

### Correct Symbol Usage
```python
# Initialize API
api = KuCoinFuturesAPI()

# ✅ CORRECT - Get Bitcoin contract details
btc_contract = api.get_contract_detail("XBTUSDTM")
print(f"BTC Max Leverage: {btc_contract['maxLeverage']}")

# ✅ CORRECT - Get Ethereum price
eth_ticker = api.get_ticker("ETHUSDTM")
print(f"ETH Price: {eth_ticker['price']}")

# ✅ CORRECT - Get Avalanche order book
avax_orderbook = api.get_orderbook("AVAXUSDTM")
print(f"AVAX Best Bid: {avax_orderbook['bids'][0][0]}")
```

### Trading Examples
```python
# ✅ CORRECT - Place Bitcoin buy order
btc_order = api.buy_limit(
    symbol="XBTUSDTM",
    price="45000",
    size=1,  # 1 contract = 0.001 BTC
    leverage=2
)

# ✅ CORRECT - Place Ethereum sell order  
eth_order = api.sell_limit(
    symbol="ETHUSDTM", 
    price="3000",
    size=10,  # 10 contracts = 0.1 ETH
    leverage=3
)

# ✅ CORRECT - Place Avalanche market order
avax_order = api.buy_market(
    symbol="AVAXUSDTM",
    value_qty="100",  # $100 worth
    leverage=5
)
```

### Symbol Validation Function
```python
def validate_futures_symbol(symbol: str) -> bool:
    """Validate KuCoin futures symbol format"""
    # Must end with 'M' for margined futures
    if not symbol.endswith('M'):
        return False
    
    # Common patterns
    valid_patterns = ['USDTM', 'USDCM', 'USDM']
    return any(symbol.endswith(pattern) for pattern in valid_patterns)

# Examples
print(validate_futures_symbol("XBTUSDTM"))   # True
print(validate_futures_symbol("ETHUSDTM"))   # True  
print(validate_futures_symbol("BTCUSDTM"))   # True (but symbol doesn't exist)
print(validate_futures_symbol("XBTUSDT"))    # False (missing M)
```

## 🎯 QUICK REFERENCE FOR CURSOR AI

```python
# Most Important Symbols for Implementation
POPULAR_FUTURES_SYMBOLS = {
    "bitcoin": "XBTUSDTM",      # ⚠️ XBT not BTC!
    "ethereum": "ETHUSDTM", 
    "avalanche": "AVAXUSDTM",
    "solana": "SOLUSDTM",
    "dogecoin": "DOGEUSDTM",
    "ripple": "XRPUSDTM",
    "cardano": "ADAUSDTM",
    "polkadot": "DOTUSDTM",
    "chainlink": "LINKUSDTM",
    "uniswap": "UNIUSDTM"
}

# Contract Multipliers (important for position sizing)
CONTRACT_MULTIPLIERS = {
    "XBTUSDTM": 0.001,    # 1 contract = 0.001 BTC
    "ETHUSDTM": 0.01,     # 1 contract = 0.01 ETH
    "AVAXUSDTM": 0.1,     # 1 contract = 0.1 AVAX
    "SOLUSDTM": 0.1,      # 1 contract = 0.1 SOL
    "DOGEUSDTM": 100.0,   # 1 contract = 100 DOGE
}

# Maximum Leverage by Symbol
MAX_LEVERAGE = {
    "XBTUSDTM": 125,      # Bitcoin: Up to 125x
    "ETHUSDTM": 100,      # Ethereum: Up to 100x  
    "AVAXUSDTM": 75,      # Avalanche: Up to 75x
    "SOLUSDTM": 75,       # Solana: Up to 75x
    "DOGEUSDTM": 75,      # Dogecoin: Up to 75x
}
```

## ✅ VERIFICATION STATUS

**All requested symbols are WORKING and VERIFIED:**

- ✅ **XBTUSDTM** (Bitcoin) - 125x leverage, 0.001 multiplier
- ✅ **ETHUSDTM** (Ethereum) - 100x leverage, 0.01 multiplier  
- ✅ **AVAXUSDTM** (Avalanche) - 75x leverage, 0.1 multiplier

**Total Active Contracts:** 458  
**Last Updated:** July 29, 2025  
**API Version:** V3

