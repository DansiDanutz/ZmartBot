#!/usr/bin/env python3
"""
IntoTheCryptoverse Symbols Configuration
ONLY symbols that have risk metrics from Benjamin Cowen's model
"""

# These are the ONLY symbols with risk metrics on IntoTheCryptoverse
CRYPTOVERSE_SYMBOLS = {
    'BTC': {
        'name': 'Bitcoin',
        'has_risk_metric': True,
        'current_risk': 0.558,  # As of 2025-09-14
        'current_price': 115876.88
    },
    'ETH': {
        'name': 'Ethereum',
        'has_risk_metric': True,
        'current_risk': 0.452,  # As of 2025-09-14
        'current_price': 4637
    },
    'SOL': {
        'name': 'Solana',
        'has_risk_metric': True,
        'current_risk': 0.511,
        'current_price': 238.88
    },
    'ADA': {
        'name': 'Cardano',
        'has_risk_metric': True,
        'current_risk': 0.482,
        'current_price': 1.18
    },
    'AVAX': {
        'name': 'Avalanche',
        'has_risk_metric': True,
        'current_risk': 0.511,
        'current_price': 56.88
    },
    'DOT': {
        'name': 'Polkadot',
        'has_risk_metric': True,
        'current_risk': 0.452,
        'current_price': 10.88
    },
    'MATIC': {
        'name': 'Polygon',
        'has_risk_metric': True,
        'current_risk': 0.547,
        'current_price': 0.887
    },
    'LINK': {
        'name': 'Chainlink',
        'has_risk_metric': True,
        'current_risk': 0.565,
        'current_price': 25.88
    },
    'UNI': {
        'name': 'Uniswap',
        'has_risk_metric': True,
        'current_risk': 0.508,
        'current_price': 15.88
    },
    'ATOM': {
        'name': 'Cosmos',
        'has_risk_metric': True,
        'current_risk': 0.43,
        'current_price': 10.88
    },
    'FTM': {
        'name': 'Fantom',
        'has_risk_metric': True,
        'current_risk': 0.612,
        'current_price': 1.388
    },
    'ALGO': {
        'name': 'Algorand',
        'has_risk_metric': True,
        'current_risk': 0.627,
        'current_price': 0.498
    }
}

# List of symbol codes only
SUPPORTED_SYMBOLS = list(CRYPTOVERSE_SYMBOLS.keys())

# Total count
TOTAL_SYMBOLS = len(SUPPORTED_SYMBOLS)

def is_supported(symbol: str) -> bool:
    """Check if a symbol has Cryptoverse risk metrics"""
    return symbol.upper() in CRYPTOVERSE_SYMBOLS

def get_current_risk(symbol: str) -> float:
    """Get current risk value for a symbol"""
    symbol = symbol.upper()
    if symbol in CRYPTOVERSE_SYMBOLS:
        return CRYPTOVERSE_SYMBOLS[symbol]['current_risk']
    return None

def get_all_supported_symbols():
    """Get list of all symbols with risk metrics"""
    return SUPPORTED_SYMBOLS

if __name__ == "__main__":
    print(f"✅ IntoTheCryptoverse Supported Symbols: {TOTAL_SYMBOLS}")
    print("=" * 50)
    for symbol, data in CRYPTOVERSE_SYMBOLS.items():
        print(f"{symbol:6} - {data['name']:15} Risk: {data['current_risk']:.3f}")
    print("=" * 50)
    print(f"Total: {TOTAL_SYMBOLS} symbols with risk metrics")