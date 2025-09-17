#!/usr/bin/env python3
"""
Script to help extract remaining risk grid data from IntoTheCryptoverse
"""

# List of symbols we still need to extract
remaining_symbols = [
    ("AVAX", "avalanche-2"),
    ("LINK", "chainlink"),
    ("DOGE", "dogecoin"),
    ("TRX", "tron"),
    ("SHIB", "shiba-inu"),
    ("TON", "the-open-network"),
    ("MATIC", "matic-network"),
    ("POL", "polygon-ecosystem-token"),
    ("VET", "vechain"),
    ("ALGO", "algorand"),
    ("MKR", "maker"),
    ("XRP", "ripple"),
    ("ATOM", "cosmos"),
    ("XTZ", "tezos"),
    ("AAVE", "aave"),
    ("LTC", "litecoin"),
    ("XMR", "monero"),
    ("XLM", "stellar"),
    ("SUI", "sui"),
    ("HBAR", "hedera-hashgraph"),
    ("RENDER", "render-token")
]

# Symbols we've already extracted
completed_symbols = ["BTC", "ETH", "SOL", "ADA", "BNB", "DOT"]

print("Symbols already extracted:")
for symbol in completed_symbols:
    print(f"  ✓ {symbol}")

print(f"\nRemaining symbols to extract ({len(remaining_symbols)}):")
for symbol, slug in remaining_symbols:
    url = f"https://app.intothecryptoverse.com/assets/{slug}/risk"
    print(f"  • {symbol}: {url}")

print("\nNext symbol to extract:")
if remaining_symbols:
    next_symbol, next_slug = remaining_symbols[0]
    next_url = f"https://app.intothecryptoverse.com/assets/{next_slug}/risk"
    print(f"  {next_symbol}: {next_url}")