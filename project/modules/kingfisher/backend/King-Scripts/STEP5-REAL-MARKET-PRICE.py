#!/usr/bin/env python3
"""
STEP 5: REAL MARKET PRICE & ACCURATE LIQUIDATION UPDATES
- ALWAYS uses REAL current market prices from Binance/CoinGecko
- NEVER uses mock or test data
- Updates ONLY the correct symbol row in Airtable
- Extracts liquidation clusters with 2% minimum distance rule
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
    "../downloads/LiquidationHeatmap/mdfiles"
]

def get_real_market_price(symbol):
    """Get REAL current market price from multiple sources"""
    symbol = symbol.upper()
    
    # Try Binance first (most reliable)
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            print(f"   ✓ Real Market Price from Binance: ${price:.2f}")
            return price
    except Exception as e:
        print(f"   ⚠️ Binance API error: {e}")
    
    # Try CoinGecko as backup
    try:
        # Map common symbols to CoinGecko IDs
        coingecko_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'LINK': 'chainlink',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'FTM': 'fantom',
            'NEAR': 'near',
            'ALGO': 'algorand',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu',
            'LTC': 'litecoin',
            'TRX': 'tron',
            'BCH': 'bitcoin-cash',
            'APT': 'aptos',
            'ARB': 'arbitrum',
            'OP': 'optimism',
            'INJ': 'injective-protocol',
            'SUI': 'sui',
            'SEI': 'sei-network',
        }
        
        coin_id = coingecko_map.get(symbol, symbol.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                price = float(data[coin_id]['usd'])
                print(f"   ✓ Real Market Price from CoinGecko: ${price:.2f}")
                return price
    except Exception as e:
        print(f"   ⚠️ CoinGecko API error: {e}")
    
    # Try CryptoCompare as final backup
    try:
        url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'USD' in data:
                price = float(data['USD'])
                print(f"   ✓ Real Market Price from CryptoCompare: ${price:.2f}")
                return price
    except Exception as e:
        print(f"   ⚠️ CryptoCompare API error: {e}")
    
    print(f"   ❌ Could not fetch real market price for {symbol}")
    return None

def create_history_folder(mdfiles_folder):
    """Create HistoryData folder inside mdfiles folder if it doesn't exist"""
    history_folder = os.path.join(mdfiles_folder, "HistoryData")
    if not os.path.exists(history_folder):
        os.makedirs(history_folder)
    return history_folder

def extract_symbol_from_md(content):
    """Extract cryptocurrency symbol from MD content"""
    patterns = [
        r"Exact cryptocurrency symbol:\s*([A-Z]+)",
        r"Symbol:\s*([A-Z]+)\s*\n",
        r"Trading Pair:\s*([A-Z]+)/USDT",
        r"cryptocurrency symbol:\s*([A-Z]+)",
        r"SYMBOL:\s*([A-Z]+)",
        r"Symbol:\s*([A-Z]+)\s*Price:",
        r"```[^`]*Symbol:\s*([A-Z]+)[^`]*```",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            symbol = match.group(1).upper()
            if 2 <= len(symbol) <= 10 and symbol.isalpha():
                return symbol
    
    return None

def extract_liquidation_clusters(content):
    """Extract all liquidation cluster prices from MD content"""
    clusters = []
    
    patterns = [
        # Cluster mentions
        r"Massive clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Critical clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Secondary clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Ll]iquidation at\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Cc]luster at\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Rr]esistance:\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Ss]upport:\s*\$?([0-9,]+\.?[0-9]*)",
        r"\$?([0-9,]+\.?[0-9]*)\s*[-–]\s*\$?([0-9,]+\.?[0-9]*)",
        r"Levels?:\s*\$?([0-9,]+\.?[0-9]*)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                for val in match:
                    if val:
                        try:
                            price = float(val.replace(',', ''))
                            if 0.01 < price < 1000000:
                                clusters.append(price)
                        except:
                            continue
            else:
                try:
                    price = float(match.replace(',', ''))
                    if 0.01 < price < 1000000:
                        clusters.append(price)
                except:
                    continue
    
    return sorted(list(set(clusters)))

def find_closest_clusters(current_price, clusters, min_distance_pct=0.02):
    """Find the 4 closest liquidation clusters with minimum 2% distance"""
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

def update_airtable_accurate(symbol, current_price, clusters_data):
    """Update Airtable with ACCURATE symbol matching and REAL prices"""
    if not AIRTABLE_ENABLED:
        print(f"\n   📝 TEST MODE - Would update {symbol}")
        return True
    
    if not symbol:
        print("   ❌ Cannot update without valid symbol")
        return False
    
    try:
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Prepare update data with REAL market price
        update_fields = {}
        
        # Add clusters
        if clusters_data[0] is not None:
            update_fields['Liqcluster-2'] = clusters_data[0]
        if clusters_data[1] is not None:
            update_fields['Liqcluster-1'] = clusters_data[1]
        if clusters_data[2] is not None:
            update_fields['Liqcluster1'] = clusters_data[2]
        if clusters_data[3] is not None:
            update_fields['Liqcluster2'] = clusters_data[3]
        
        
        # Find EXACT record by symbol
        print(f"\n   🔍 Finding {symbol} in Airtable...")
        records = table.all(formula=f"{{Symbol}} = '{symbol}'")
        
        if records:
            record = records[0]
            # VERIFY symbol match
            existing_symbol = record['fields'].get('Symbol', '').upper()
            if existing_symbol != symbol.upper():
                print(f"   ❌ Symbol mismatch! Found '{existing_symbol}' expected '{symbol}'")
                return False
            
            record_id = record['id']
            table.update(record_id, update_fields)
            print(f"   ✅ Updated {symbol} (ID: {record_id})")
        else:
            create_fields = {'Symbol': symbol}
            create_fields.update(update_fields)
            new_record = table.create(create_fields)
            print(f"   ✅ Created {symbol} (ID: {new_record['id']})")
        
        # Show updates with REAL prices
        print(f"\n   📊 REAL MARKET DATA for {symbol}:")
        print(f"      Market Price: ${current_price:.2f} (LIVE)")
        if clusters_data[0]:
            diff = ((current_price - clusters_data[0]) / current_price * 100)
            print(f"      Liqcluster-2: ${clusters_data[0]:.2f} (-{diff:.1f}%)")
        if clusters_data[1]:
            diff = ((current_price - clusters_data[1]) / current_price * 100)
            print(f"      Liqcluster-1: ${clusters_data[1]:.2f} (-{diff:.1f}%)")
        if clusters_data[2]:
            diff = ((clusters_data[2] - current_price) / current_price * 100)
            print(f"      Liqcluster+1: ${clusters_data[2]:.2f} (+{diff:.1f}%)")
        if clusters_data[3]:
            diff = ((clusters_data[3] - current_price) / current_price * 100)
            print(f"      Liqcluster+2: ${clusters_data[3]:.2f} (+{diff:.1f}%)")
        
        return True
            
    except Exception as e:
        print(f"\n   ❌ Airtable error: {e}")
        return False

def process_md_file(filepath, folder_path):
    """Process MD file with REAL market prices"""
    print(f"\n{'='*60}")
    print(f"📄 Processing: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract symbol
        symbol = extract_symbol_from_md(content)
        if not symbol:
            print("   ❌ No valid symbol found - skipping")
            return False
        
        print(f"   ✓ Symbol: {symbol}")
        
        # GET REAL MARKET PRICE - NEVER USE MOCK DATA
        print(f"\n   🌐 Fetching REAL market price for {symbol}...")
        current_price = get_real_market_price(symbol)
        
        if not current_price:
            print(f"   ❌ Cannot proceed without real market price")
            return False
        
        # Extract liquidation clusters
        clusters = extract_liquidation_clusters(content)
        print(f"   ✓ Found {len(clusters)} liquidation levels")
        
        # Find 4 closest with 2% rule
        liq_minus2, liq_minus1, liq_plus1, liq_plus2 = find_closest_clusters(
            current_price, clusters
        )
        
        # Update Airtable with REAL data
        if update_airtable_accurate(symbol, current_price, 
                                   (liq_minus2, liq_minus1, liq_plus1, liq_plus2)):
            # Archive processed file
            history_folder = create_history_folder(folder_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{symbol}_{timestamp}.md"
            new_path = os.path.join(history_folder, new_name)
            shutil.move(filepath, new_path)
            print(f"\n   ✅ Archived as: {new_name}")
            return True
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_latest_md_file():
    """Get the most recent MD file"""
    latest_file = None
    latest_time = None
    latest_folder = None
    
    for folder in FOLDERS_TO_MONITOR:
        if not os.path.exists(folder):
            continue
        
        md_files = [f for f in os.listdir(folder) 
                   if f.endswith('.md') and os.path.isfile(os.path.join(folder, f))]
        
        for md_file in md_files:
            filepath = os.path.join(folder, md_file)
            file_time = os.path.getmtime(filepath)
            
            if latest_time is None or file_time > latest_time:
                latest_time = file_time
                latest_file = filepath
                latest_folder = folder
    
    return latest_file, latest_folder

def monitor_continuous(update_interval=300):
    """Monitor with REAL market prices every 5 minutes"""
    print("="*70)
    print("STEP 5: REAL MARKET PRICE LIQUIDATION UPDATES")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n✅ REAL market prices from Binance/CoinGecko")
    print("✅ NEVER using mock or test data")
    print("✅ Symbol verification active")
    print("✅ 2% minimum distance rule")
    print("\n♾️  Updates every 5 minutes")
    print("Press Ctrl+C to stop\n")
    
    last_update = datetime.now()
    
    while True:
        current_time = datetime.now()
        elapsed = (current_time - last_update).total_seconds()
        
        if elapsed >= update_interval:
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Processing...")
            
            latest_file, latest_folder = get_latest_md_file()
            
            if latest_file and latest_folder:
                print(f"   Latest: {os.path.basename(latest_file)}")
                process_md_file(latest_file, latest_folder)
            else:
                print("   No files to process")
            
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
    print("REAL MARKET PRICE LIQUIDATION SYSTEM")
    print("="*70)
    print("✅ Using LIVE market data ONLY")
    print("❌ NO mock/test data allowed")
    
    if one_time:
        print("\n🔍 One-time mode")
        latest_file, latest_folder = get_latest_md_file()
        if latest_file and latest_folder:
            process_md_file(latest_file, latest_folder)
        else:
            print("No files found")
    else:
        try:
            monitor_continuous()
        except KeyboardInterrupt:
            print("\n\n👋 Stopped")

if __name__ == "__main__":
    main()