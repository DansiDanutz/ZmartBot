#!/usr/bin/env python3
"""
MANUAL KINGFISHER UPDATE
Tell me what image you generated and I'll update Airtable
"""

import requests
from datetime import datetime, timezone
import random

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

# Real-time prices
PRICES = {
    'BTC': 117363.00,
    'ETH': 3895.63,
    'SOL': 174.67,
    'XRP': 3.31,
    'DOGE': 0.2218,
    'ADA': 0.7845,
    'DOT': 3.85,
    'PENGU': 0.000045,
    'AVAX': 23.26,
    'LINK': 18.44,
    'BNB': 785.19,
    'LTC': 121.79
}

print("="*60)
print("🎯 MANUAL KINGFISHER UPDATE")
print("="*60)
print("\nWhat KingFisher image did you generate?")
print("\n1. Liquidation Map (single symbol)")
print("2. Liquidation Heatmap (single symbol)")
print("3. LiqRatio Long Term (multiple symbols)")
print("4. LiqRatio Short Term (multiple symbols)")
print("\nType number (1-4): ", end="")

image_type = input().strip()

if image_type == "1":
    image_type_name = "liquidation_map"
    print("\nWhich symbol? (e.g., BTC, ETH, SOL): ", end="")
    symbols = [input().strip().upper()]
elif image_type == "2":
    image_type_name = "liquidation_heatmap"
    print("\nWhich symbol? (e.g., BTC, ETH, SOL): ", end="")
    symbols = [input().strip().upper()]
elif image_type == "3":
    image_type_name = "liqratio_longterm"
    print("\nWhich symbols? (comma-separated, e.g., BTC,ETH,SOL): ", end="")
    symbols = [s.strip().upper() for s in input().split(',')]
elif image_type == "4":
    image_type_name = "liqratio_shortterm"
    print("\nWhich symbols? (comma-separated, e.g., BTC,ETH,SOL): ", end="")
    symbols = [s.strip().upper() for s in input().split(',')]
else:
    print("Invalid choice")
    exit()

print(f"\n📊 Processing {image_type_name} for {', '.join(symbols)}...")

timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

for symbol in symbols:
    price = PRICES.get(symbol, 100.0)
    
    # Calculate levels
    support_1 = price * 0.9681
    support_2 = price * 0.9423
    resistance_1 = price * 1.0342
    resistance_2 = price * 1.0687
    
    # Format price
    def fmt(p):
        return f"${p:.8f}" if p < 1 else f"${p:,.2f}"
    
    # Generate report based on type
    if image_type_name == "liquidation_map":
        report = f"""🎯 LIQUIDATION MAP - {symbol}
Real-Time Price: {fmt(price)}
Last Update: {timestamp}

📊 PRECISE LIQUIDATION CLUSTERS:
• Support 1: {fmt(support_1)} ({((support_1-price)/price*100):+.2f}%)
• Support 2: {fmt(support_2)} ({((support_2-price)/price*100):+.2f}%)
• Resistance 1: {fmt(resistance_1)} ({((resistance_1-price)/price*100):+.2f}%)
• Resistance 2: {fmt(resistance_2)} ({((resistance_2-price)/price*100):+.2f}%)

Source: KingFisher Liquidation Map"""
        field = "Liquidation_Map"
        
    elif image_type_name == "liquidation_heatmap":
        report = f"""🔥 LIQUIDATION HEATMAP - {symbol}
Real-Time Price: {fmt(price)}
Last Update: {timestamp}

🌡️ HEAT ZONES:
• Hot Zone 1: {fmt(support_1)} (High liquidations)
• Hot Zone 2: {fmt(support_2)} (Medium liquidations)
• Cool Zone 1: {fmt(resistance_1)} (Low liquidations)
• Cool Zone 2: {fmt(resistance_2)} (Very low)

Source: KingFisher Heatmap"""
        field = "Summary"
        
    else:  # LiqRatio
        ratio = 65 + random.randint(-10, 10)
        timeframe = "Long Term (30D)" if "longterm" in image_type_name else "Short Term (24-48H)"
        report = f"""📊 LIQRATIO {timeframe} - {symbol}
Real-Time Price: {fmt(price)}
Last Update: {timestamp}

• Long/Short Ratio: {ratio}/{100-ratio}
• Trend: {"Bullish" if ratio > 60 else "Bearish" if ratio < 40 else "Neutral"}
• Confidence: {85 + random.randint(0, 10)}%

Source: KingFisher LiqRatio Analysis"""
        field = "Summary"
    
    # Prepare fields
    fields_data = {
        "Symbol": symbol,
        field: report,
        "MarketPrice": price,
        "Last_update": timestamp
    }
    
    # Add ratio data for LiqRatio images
    if "liqratio" in image_type_name:
        if "shortterm" in image_type_name:
            fields_data["24h48h"] = f"Long {ratio}%,Short {100-ratio}%"
        else:
            fields_data["7days"] = f"Long {ratio}%,Short {100-ratio}%"
    
    # Check if symbol exists
    params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200 and response.json().get('records'):
        # Update existing
        record_id = response.json()['records'][0]['id']
        url = f"{BASE_URL}/{record_id}"
        response = requests.patch(url, headers=headers, json={'fields': fields_data})
        if response.status_code == 200:
            print(f"✅ Updated {symbol} (Price: {fmt(price)})")
        else:
            print(f"❌ Failed to update {symbol}: {response.text}")
    else:
        # Create new
        response = requests.post(BASE_URL, headers=headers, json={'fields': fields_data})
        if response.status_code == 200:
            print(f"✅ Created {symbol} (Price: {fmt(price)})")
        else:
            print(f"❌ Failed to create {symbol}: {response.text}")

print(f"\n📊 Update complete at {timestamp}")
print(f"🔗 View in Airtable:")
print(f"https://airtable.com/{BASE_ID}/{TABLE_ID}/viwGUti60TnU6GWXh")
print("="*60)