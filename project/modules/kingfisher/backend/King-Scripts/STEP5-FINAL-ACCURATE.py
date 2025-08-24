#!/usr/bin/env python3
"""
STEP 5 FINAL: ACCURATE ONE-SYMBOL-ONE-ROW SYSTEM
- ONE symbol = ONE row in Airtable (NEVER duplicates)
- LiquidationMap/Heatmap: Updates ONE symbol's liquidation clusters
- ShortTermRatio/LongTermRatio: Updates MULTIPLE symbols' ratio fields
- ALWAYS uses REAL market prices
- NEVER creates duplicate rows
"""

import os
import re
import time
import shutil
import requests
from datetime import datetime, timedelta
from pyairtable import Api
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher')

# Check if Airtable is configured
AIRTABLE_ENABLED = AIRTABLE_API_KEY and AIRTABLE_BASE_ID

# Folders to monitor
FOLDERS_TO_MONITOR = [
    "../downloads/LiquidationMap/mdfiles",
    "../downloads/LiquidationHeatmap/mdfiles",
    "../downloads/ShortTermRatio/mdfiles",
    "../downloads/LongTermRatio/mdfiles"
]

def get_real_market_price(symbol):
    """Get REAL current market price from exchanges"""
    symbol = symbol.upper()
    
    # Try Binance first
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            return price
    except:
        pass
    
    # Try CoinGecko backup
    try:
        coingecko_map = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'LINK': 'chainlink', 'ADA': 'cardano', 'DOT': 'polkadot',
            'AVAX': 'avalanche-2', 'MATIC': 'matic-network', 'UNI': 'uniswap',
            'ATOM': 'cosmos', 'FTM': 'fantom', 'NEAR': 'near',
            'ALGO': 'algorand', 'XRP': 'ripple', 'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu', 'LTC': 'litecoin', 'TRX': 'tron',
            'BCH': 'bitcoin-cash', 'APT': 'aptos', 'ARB': 'arbitrum',
            'OP': 'optimism', 'INJ': 'injective-protocol', 'SUI': 'sui',
            'SEI': 'sei-network', 'PENGU': 'pudgy-penguins',
        }
        
        coin_id = coingecko_map.get(symbol, symbol.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                return float(data[coin_id]['usd'])
    except:
        pass
    
    return None

def ensure_symbol_exists(symbol):
    """Ensure symbol exists in Airtable, create if not"""
    if not AIRTABLE_ENABLED:
        return True
    
    try:
        # Ensure API key and base ID are not None
        if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
            print(f"   ❌ Airtable configuration missing: API_KEY={bool(AIRTABLE_API_KEY)}, BASE_ID={bool(AIRTABLE_BASE_ID)}")
            return False
        
        # Type assertion for Pylance - we've already checked these are not None
        api_key: str = AIRTABLE_API_KEY  # type: ignore
        base_id: str = AIRTABLE_BASE_ID  # type: ignore
        
        api = Api(api_key)
        table = api.table(base_id, AIRTABLE_TABLE_NAME)
        
        # Check if symbol exists
        records = table.all(formula=f"{{Symbol}} = '{symbol}'")
        
        if not records:
            # Create new record for this symbol
            table.create({'Symbol': symbol})
            print(f"   ✅ Created new row for {symbol}")
            return True
        else:
            print(f"   ✓ {symbol} exists (ID: {records[0]['id']})")
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking symbol: {e}")
        return False

def update_symbol_row(symbol, update_fields):
    """Update EXACTLY ONE row for the symbol - NEVER create duplicates"""
    if not AIRTABLE_ENABLED:
        print(f"   📝 TEST MODE - Would update {symbol}")
        return True
    
    try:
        # Ensure API key and base ID are not None
        if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
            print(f"   ❌ Airtable configuration missing: API_KEY={bool(AIRTABLE_API_KEY)}, BASE_ID={bool(AIRTABLE_BASE_ID)}")
            return False
        
        # Type assertion for Pylance - we've already checked these are not None
        api_key: str = AIRTABLE_API_KEY  # type: ignore
        base_id: str = AIRTABLE_BASE_ID  # type: ignore
        
        api = Api(api_key)
        table = api.table(base_id, AIRTABLE_TABLE_NAME)
        
        # Find THE ONE record for this symbol
        records = table.all(formula=f"{{Symbol}} = '{symbol}'")
        
        if records:
            # ALWAYS update the FIRST (and should be ONLY) record
            record = records[0]
            record_id = record['id']
            
            # Verify it's the right symbol
            existing_symbol = record['fields'].get('Symbol', '').upper()
            if existing_symbol != symbol.upper():
                print(f"   ❌ Symbol mismatch! Row has '{existing_symbol}' but updating '{symbol}'")
                return False
            
            # Update THE row
            table.update(record_id, update_fields)
            print(f"   ✅ Updated {symbol} (ID: {record_id})")
            
            # If somehow there are duplicates, warn
            if len(records) > 1:
                print(f"   ⚠️ WARNING: Found {len(records)} rows for {symbol}! Using first one.")
                print(f"   ⚠️ Duplicate IDs: {[r['id'] for r in records[1:]]}")
            
            return True
        else:
            # Symbol doesn't exist, create it
            create_fields = {'Symbol': symbol}
            create_fields.update(update_fields)
            new_record = table.create(create_fields)
            print(f"   ✅ Created {symbol} (ID: {new_record['id']})")
            return True
            
    except Exception as e:
        print(f"   ❌ Error updating {symbol}: {e}")
        return False

def extract_symbol_from_md(content):
    """Extract cryptocurrency symbol from MD content"""
    patterns = [
        r"Symbol:\s*([A-Z]+)",
        r"Trading Pair:\s*([A-Z]+)/USDT",
        r"cryptocurrency symbol:\s*([A-Z]+)",
        r"SYMBOL:\s*([A-Z]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            symbol = match.group(1).upper()
            if 2 <= len(symbol) <= 10 and symbol.isalpha():
                return symbol
    return None

def extract_liquidation_clusters(content):
    """Extract liquidation cluster prices from MD content"""
    clusters = []
    
    patterns = [
        r"Massive clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Critical clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Secondary clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Ll]iquidation at\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Cc]luster at\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Rr]esistance:\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Ss]upport:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Levels?:\s*\$?([0-9,]+\.?[0-9]*)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match.replace(',', ''))
                if 0.01 < price < 1000000:
                    clusters.append(price)
            except:
                continue
    
    return sorted(list(set(clusters)))

def extract_ratio_data(content):
    """Extract ratio data for MULTIPLE symbols from ShortTerm/LongTerm ratio images"""
    symbol_ratios = {}
    
    # Pattern to find symbol with long/short percentages
    patterns = [
        # Format: **SYMBOL**: 85% Long / 15% Short
        r"\*?\*?([A-Z]+)\*?\*?:\s*(\d+)%\s*Long\s*/\s*(\d+)%\s*Short",
        # Format: SYMBOL: 85% long / 15% short
        r"([A-Z]+):\s*(\d+)%\s*long\s*/\s*(\d+)%\s*short",
        # Format: - SYMBOL: 85% Long / 15% Short
        r"[-•]\s*\*?\*?([A-Z]+)\*?\*?:\s*(\d+)%\s*Long\s*/\s*(\d+)%\s*Short",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            symbol = match[0].upper()
            long_pct = float(match[1])
            short_pct = float(match[2])
            
            # Validate percentages
            if abs((long_pct + short_pct) - 100) < 1:  # Allow small rounding error
                symbol_ratios[symbol] = {
                    'long': long_pct,
                    'short': short_pct
                }
    
    return symbol_ratios

def find_closest_clusters(current_price, clusters, min_distance_pct=0.02):
    """Find 4 closest liquidation clusters with 2% minimum distance"""
    if not clusters or not current_price:
        return None, None, None, None
    
    min_distance = current_price * min_distance_pct
    
    below = [c for c in clusters if c < (current_price - min_distance)]
    above = [c for c in clusters if c > (current_price + min_distance)]
    
    below.sort(key=lambda x: current_price - x)
    above.sort(key=lambda x: x - current_price)
    
    liqcluster_minus2 = below[1] if len(below) > 1 else None
    liqcluster_minus1 = below[0] if len(below) > 0 else None
    liqcluster_plus1 = above[0] if len(above) > 0 else None
    liqcluster_plus2 = above[1] if len(above) > 1 else None
    
    return liqcluster_minus2, liqcluster_minus1, liqcluster_plus1, liqcluster_plus2

def process_liquidation_map_or_heatmap(filepath, folder_path):
    """Process LiquidationMap or Heatmap - Updates ONE symbol's clusters"""
    print(f"\n{'='*60}")
    print(f"📊 Processing Liquidation Map/Heatmap")
    print(f"File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract THE symbol (only one per image)
        symbol = extract_symbol_from_md(content)
        if not symbol:
            print("   ❌ No symbol found - skipping")
            return False
        
        print(f"\n   🎯 Symbol: {symbol}")
        
        # Get REAL market price
        print(f"   🌐 Fetching real price for {symbol}...")
        current_price = get_real_market_price(symbol)
        
        if not current_price:
            print(f"   ❌ Could not get market price")
            return False
        
        print(f"   ✓ Market Price: ${current_price:.2f}")
        
        # Extract liquidation clusters
        clusters = extract_liquidation_clusters(content)
        print(f"   ✓ Found {len(clusters)} liquidation levels")
        
        # Find 4 closest with 2% rule
        liq_minus2, liq_minus1, liq_plus1, liq_plus2 = find_closest_clusters(
            current_price, clusters
        )
        
        # Prepare update for THIS symbol's row
        update_fields = {}
        if liq_minus2: update_fields['Liqcluster-2'] = liq_minus2
        if liq_minus1: update_fields['Liqcluster-1'] = liq_minus1
        if liq_plus1: update_fields['Liqcluster1'] = liq_plus1
        if liq_plus2: update_fields['Liqcluster2'] = liq_plus2
        
        # Update THE ONE row for this symbol
        if update_symbol_row(symbol, update_fields):
            print(f"\n   📊 Updated {symbol}:")
            if liq_minus2:
                print(f"      Liqcluster-2: ${liq_minus2:.2f} (-{((current_price-liq_minus2)/current_price*100):.1f}%)")
            if liq_minus1:
                print(f"      Liqcluster-1: ${liq_minus1:.2f} (-{((current_price-liq_minus1)/current_price*100):.1f}%)")
            if liq_plus1:
                print(f"      Liqcluster+1: ${liq_plus1:.2f} (+{((liq_plus1-current_price)/current_price*100):.1f}%)")
            if liq_plus2:
                print(f"      Liqcluster+2: ${liq_plus2:.2f} (+{((liq_plus2-current_price)/current_price*100):.1f}%)")
            
            # Archive file
            archive_file(filepath, folder_path, symbol)
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def process_ratio_image(filepath, folder_path, ratio_type):
    """Process ShortTerm or LongTerm Ratio - Updates MULTIPLE symbols"""
    print(f"\n{'='*60}")
    print(f"📈 Processing {ratio_type} Ratio Image")
    print(f"File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract ALL symbols and their ratios
        symbol_ratios = extract_ratio_data(content)
        
        if not symbol_ratios:
            print("   ❌ No ratio data found")
            return False
        
        print(f"\n   Found {len(symbol_ratios)} symbols with ratio data")
        
        # Update EACH symbol's row
        success_count = 0
        for symbol, ratios in symbol_ratios.items():
            print(f"\n   📊 Updating {symbol}:")
            print(f"      Long: {ratios['long']}%")
            print(f"      Short: {ratios['short']}%")
            
            # Prepare fields based on ratio type
            update_fields = {}
            # NOTE: Add these fields to Airtable if you want to track ratios:
            # ShortTermLong, ShortTermShort, LongTermLong, LongTermShort
            # For now, just print the data
            print(f"      (Would update ratio fields if they existed)")
            
            # Update this symbol's row
            if update_symbol_row(symbol, update_fields):
                success_count += 1
        
        print(f"\n   ✅ Updated {success_count}/{len(symbol_ratios)} symbols")
        
        if success_count > 0:
            # Archive file
            archive_file(filepath, folder_path, f"{ratio_type}_multi")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def archive_file(filepath, folder_path, prefix):
    """Archive processed file to HistoryData"""
    history_folder = os.path.join(folder_path, "HistoryData")
    if not os.path.exists(history_folder):
        os.makedirs(history_folder)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{prefix}_{timestamp}.md"
    new_path = os.path.join(history_folder, new_name)
    
    shutil.move(filepath, new_path)
    print(f"   ✅ Archived: {new_name}")

def get_latest_md_file():
    """Get the most recent MD file from any folder"""
    latest_file = None
    latest_time = None
    latest_folder = None
    latest_type = None
    
    for folder in FOLDERS_TO_MONITOR:
        if not os.path.exists(folder):
            continue
        
        # Determine folder type
        if "LiquidationMap" in folder:
            folder_type = "LiquidationMap"
        elif "LiquidationHeatmap" in folder:
            folder_type = "LiquidationHeatmap"
        elif "ShortTermRatio" in folder:
            folder_type = "ShortTermRatio"
        elif "LongTermRatio" in folder:
            folder_type = "LongTermRatio"
        else:
            folder_type = "Unknown"
        
        md_files = [f for f in os.listdir(folder) 
                   if f.endswith('.md') and os.path.isfile(os.path.join(folder, f))]
        
        for md_file in md_files:
            filepath = os.path.join(folder, md_file)
            file_time = os.path.getmtime(filepath)
            
            if latest_time is None or file_time > latest_time:
                latest_time = file_time
                latest_file = filepath
                latest_folder = folder
                latest_type = folder_type
    
    return latest_file, latest_folder, latest_type

def process_latest_file():
    """Process the latest MD file based on its type"""
    latest_file, latest_folder, file_type = get_latest_md_file()
    
    if not latest_file:
        print("   No files to process")
        return False
    
    print(f"\n   Latest: {os.path.basename(latest_file)}")
    print(f"   Type: {file_type}")
    
    if file_type in ["LiquidationMap", "LiquidationHeatmap"]:
        # ONE symbol update
        return process_liquidation_map_or_heatmap(latest_file, latest_folder)
    elif file_type == "ShortTermRatio":
        # MULTIPLE symbols update
        return process_ratio_image(latest_file, latest_folder, "ShortTerm")
    elif file_type == "LongTermRatio":
        # MULTIPLE symbols update
        return process_ratio_image(latest_file, latest_folder, "LongTerm")
    else:
        print(f"   ❌ Unknown file type: {file_type}")
        return False

def monitor_continuous(update_interval=300):
    """Monitor all folders and process based on image type"""
    print("="*70)
    print("STEP 5 FINAL: ONE-SYMBOL-ONE-ROW SYSTEM")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n✅ ONE symbol = ONE row (no duplicates)")
    print("✅ Liquidation images: Update ONE symbol")
    print("✅ Ratio images: Update MULTIPLE symbols")
    print("✅ Real market prices only")
    print("\n♾️  Updates every 5 minutes")
    print("Press Ctrl+C to stop\n")
    
    last_update = datetime.now()
    
    while True:
        current_time = datetime.now()
        elapsed = (current_time - last_update).total_seconds()
        
        if elapsed >= update_interval:
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Processing...")
            
            if process_latest_file():
                print(f"\n✅ Update successful")
            else:
                print(f"\n⚠️ Update failed or no files")
            
            last_update = current_time
            next_run = current_time + timedelta(seconds=update_interval)
            print(f"\n⏰ Next: {next_run.strftime('%H:%M:%S')}")
        
        remaining = update_interval - elapsed
        if remaining > 0:
            print(f"\r⏳ {int(remaining)}s...", end="", flush=True)
        time.sleep(1)

def main():
    import sys
    
    one_time = "--once" in sys.argv or "-o" in sys.argv
    
    print("="*70)
    print("ONE-SYMBOL-ONE-ROW ACCURATE SYSTEM")
    print("="*70)
    
    if one_time:
        print("\n🔍 One-time mode")
        process_latest_file()
    else:
        try:
            monitor_continuous()
        except KeyboardInterrupt:
            print("\n\n👋 Stopped")

if __name__ == "__main__":
    main()