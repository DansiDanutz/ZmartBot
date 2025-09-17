#!/usr/bin/env python3
"""
Direct sync of IntoTheCryptoverse data to Supabase
Uses the complete risk data (both Fiat and BTC risks)
"""

import json
from pathlib import Path
from datetime import datetime

# Load the complete risk data
data_file = Path(__file__).parent / 'cryptoverse_complete_risk_data.json'

print("🚀 Loading IntoTheCryptoverse Complete Risk Data")
print(f"📁 Data file: {data_file}")

with open(data_file, 'r') as f:
    risk_data = json.load(f)

# Display summary
print("\n" + "="*60)
print("📊 RISK DATA SUMMARY")
print("="*60)

symbols_data = risk_data.get('risk_data', {})
btc_price = risk_data.get('metadata', {}).get('btc_price', 115844.88)

print(f"\n💰 BTC Reference Price: ${btc_price:,.2f}")
print(f"📋 Total Symbols: {len(symbols_data)}")

# Group by risk zones
accumulation_fiat = []  # < 0.3
transition_fiat = []    # 0.3 - 0.7
distribution_fiat = []  # > 0.7

accumulation_btc = []  # < 0.3
transition_btc = []    # 0.3 - 0.7
distribution_btc = []  # > 0.7

for symbol, data in symbols_data.items():
    fiat_risk = data.get('fiat_risk', 0)
    btc_risk = data.get('btc_risk', 0)

    # Fiat Risk zones
    if fiat_risk < 0.3:
        accumulation_fiat.append(f"{symbol}: {fiat_risk:.3f}")
    elif fiat_risk < 0.7:
        transition_fiat.append(f"{symbol}: {fiat_risk:.3f}")
    else:
        distribution_fiat.append(f"{symbol}: {fiat_risk:.3f}")

    # BTC Risk zones
    if btc_risk < 0.3:
        accumulation_btc.append(f"{symbol}: {btc_risk:.3f}")
    elif btc_risk < 0.7:
        transition_btc.append(f"{symbol}: {btc_risk:.3f}")
    else:
        distribution_btc.append(f"{symbol}: {btc_risk:.3f}")

print("\n📊 FIAT RISK DISTRIBUTION:")
print("🟢 ACCUMULATION ZONE (< 0.3):")
if accumulation_fiat:
    for item in sorted(accumulation_fiat):
        print(f"  {item}")
else:
    print("  No symbols")

print("\n🟡 TRANSITION ZONE (0.3 - 0.7):")
if transition_fiat:
    for item in sorted(transition_fiat):
        print(f"  {item}")
else:
    print("  No symbols")

print("\n🔴 DISTRIBUTION ZONE (> 0.7):")
if distribution_fiat:
    for item in sorted(distribution_fiat):
        print(f"  {item}")
else:
    print("  No symbols")

print("\n📊 BTC RISK DISTRIBUTION:")
print("🟢 ACCUMULATION ZONE (< 0.3):")
if accumulation_btc:
    for item in sorted(accumulation_btc):
        print(f"  {item}")
else:
    print("  No symbols")

print("\n🟡 TRANSITION ZONE (0.3 - 0.7):")
if transition_btc:
    for item in sorted(transition_btc):
        print(f"  {item}")
else:
    print("  No symbols")

print("\n🔴 DISTRIBUTION ZONE (> 0.7):")
if distribution_btc:
    for item in sorted(distribution_btc):
        print(f"  {item}")
else:
    print("  No symbols")

# Show divergence analysis
print("\n📈 RISK DIVERGENCE ANALYSIS:")
divergences = []
for symbol, data in symbols_data.items():
    fiat_risk = data.get('fiat_risk', 0)
    btc_risk = data.get('btc_risk', 0)
    divergence = abs(fiat_risk - btc_risk)
    divergences.append((symbol, divergence, fiat_risk, btc_risk))

divergences.sort(key=lambda x: x[1], reverse=True)

print("\n  Highest Divergence (Fiat vs BTC):")
for symbol, div, fiat, btc in divergences[:5]:
    print(f"    {symbol}: {div:.3f} (Fiat: {fiat:.3f}, BTC: {btc:.3f})")

print("\n  Lowest Divergence (Most Aligned):")
for symbol, div, fiat, btc in divergences[-5:]:
    print(f"    {symbol}: {div:.3f} (Fiat: {fiat:.3f}, BTC: {btc:.3f})")

# Create SQL insert statements for manual execution
print("\n" + "="*60)
print("📝 SQL INSERT STATEMENTS")
print("="*60)

print("\n-- Fiat Risk Data")
print("INSERT INTO public.cryptoverse_fiat_risks (symbol, current_price, risk_value, market_cap_rank) VALUES")
fiat_values = []
for i, (symbol, data) in enumerate(symbols_data.items(), 1):
    price = data.get('price_usd', 0)
    fiat_risk = data.get('fiat_risk', 0)
    fiat_values.append(f"    ('{symbol}', {price}, {fiat_risk}, {i})")
print(",\n".join(fiat_values))
print("ON CONFLICT (symbol) DO UPDATE SET")
print("    current_price = EXCLUDED.current_price,")
print("    risk_value = EXCLUDED.risk_value,")
print("    market_cap_rank = EXCLUDED.market_cap_rank,")
print("    last_updated = NOW();")

print("\n-- BTC Risk Data")
print("INSERT INTO public.cryptoverse_btc_risks (symbol, current_price_btc, risk_value, btc_price) VALUES")
btc_values = []
for symbol, data in symbols_data.items():
    price_btc = data.get('price_btc', 0)
    btc_risk = data.get('btc_risk', 0)
    btc_values.append(f"    ('{symbol}', {price_btc}, {btc_risk}, {btc_price})")
print(",\n".join(btc_values))
print("ON CONFLICT (symbol) DO UPDATE SET")
print("    current_price_btc = EXCLUDED.current_price_btc,")
print("    risk_value = EXCLUDED.risk_value,")
print("    btc_price = EXCLUDED.btc_price,")
print("    last_updated = NOW();")

print("\n-- Combined Risk Data")
print("INSERT INTO public.cryptoverse_risk_data (symbol, price_usd, price_btc, fiat_risk, btc_risk, btc_reference_price) VALUES")
combined_values = []
for symbol, data in symbols_data.items():
    price_usd = data.get('price_usd', 0)
    price_btc = data.get('price_btc', 0)
    fiat_risk = data.get('fiat_risk', 0)
    btc_risk = data.get('btc_risk', 0)
    combined_values.append(f"    ('{symbol}', {price_usd}, {price_btc}, {fiat_risk}, {btc_risk}, {btc_price})")
print(",\n".join(combined_values))
print("ON CONFLICT (symbol) DO UPDATE SET")
print("    price_usd = EXCLUDED.price_usd,")
print("    price_btc = EXCLUDED.price_btc,")
print("    fiat_risk = EXCLUDED.fiat_risk,")
print("    btc_risk = EXCLUDED.btc_risk,")
print("    btc_reference_price = EXCLUDED.btc_reference_price,")
print("    last_updated = NOW();")

print("\n✅ Analysis complete!")
print("📌 Copy the SQL statements above and run them in Supabase SQL Editor")
print("🔗 Or use the migration files in supabase/migrations/")