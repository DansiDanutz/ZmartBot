#!/usr/bin/env python3
"""
STEP 5: ACCURATE SYMBOL-SPECIFIC LIQUIDATION CLUSTER UPDATES
- MANDATORY: Updates ONLY the correct symbol row in Airtable
- Extracts symbol, current price, and liquidation clusters from MD files
- Verifies symbol match before updating
- Updates current price along with clusters
- Ensures 2% minimum distance from current price
"""

import os
import re
import time
import shutil
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

if not AIRTABLE_ENABLED:
    print("\n⚠️  AIRTABLE NOT FULLY CONFIGURED!")
    print("Running in TEST MODE - will extract data but not update Airtable\n")

# Folders to monitor
FOLDERS_TO_MONITOR = [
    "../downloads/LiquidationMap/mdfiles",
    "../downloads/LiquidationHeatmap/mdfiles"
]

def create_history_folder(mdfiles_folder):
    """Create HistoryData folder inside mdfiles folder if it doesn't exist"""
    history_folder = os.path.join(mdfiles_folder, "HistoryData")
    if not os.path.exists(history_folder):
        os.makedirs(history_folder)
        print(f"✅ Created history folder: {history_folder}")
    return history_folder

def extract_symbol_from_md(content):
    """Extract cryptocurrency symbol from MD content - ENHANCED FOR ACCURACY"""
    # Multiple patterns to ensure we get the correct symbol
    patterns = [
        # Most specific patterns first
        r"Exact cryptocurrency symbol:\s*([A-Z]+)",
        r"Symbol:\s*([A-Z]+)\s*\n",  # Symbol at start of line
        r"Trading Pair:\s*([A-Z]+)/USDT",
        r"cryptocurrency symbol:\s*([A-Z]+)",
        r"SYMBOL:\s*([A-Z]+)",
        r"Coin:\s*([A-Z]+)",
        r"Asset:\s*([A-Z]+)",
        # Look in technical data section
        r"Symbol:\s*([A-Z]+)\s*Price:",
        r"```[^`]*Symbol:\s*([A-Z]+)[^`]*```",  # Inside code blocks
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            symbol = match.group(1).upper()
            # Validate symbol (should be 2-10 characters, only letters)
            if 2 <= len(symbol) <= 10 and symbol.isalpha():
                print(f"   ✓ Extracted Symbol: {symbol}")
                return symbol
    
    print("   ⚠️ WARNING: Could not extract valid symbol from MD file")
    return None

def extract_current_price(content):
    """Extract current price from MD content - ENHANCED FOR ACCURACY"""
    patterns = [
        # Most specific patterns first
        r"Current [Pp]rice:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Current Price:\s*\$?([0-9,]+\.?[0-9]*)\s*USDT",
        r"Price:\s*\$?([0-9,]+\.?[0-9]*)",
        r"CURRENT_PRICE:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Market Price:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Spot Price:\s*\$?([0-9,]+\.?[0-9]*)",
        # In technical data section
        r"Price:\s*\$([0-9,]+\.?[0-9]*)\s*\n",
        r"```[^`]*Price:\s*\$([0-9,]+\.?[0-9]*)[^`]*```",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                price = float(price_str)
                if 0.001 < price < 1000000:  # Sanity check
                    print(f"   ✓ Extracted Current Price: ${price:.2f}")
                    return price
            except:
                continue
    
    print("   ⚠️ WARNING: Could not extract valid current price from MD file")
    return None

def extract_liquidation_clusters(content):
    """Extract all liquidation cluster prices from MD content"""
    clusters = []
    
    # Enhanced patterns for better extraction
    patterns = [
        # Specific cluster mentions
        r"Massive clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Critical clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Secondary clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Minor clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
        # Liquidation levels
        r"[Ll]iquidation [Ll]evel[s]?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Ll]iquidation at\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Cc]luster at\s*\$?([0-9,]+\.?[0-9]*)",
        # Support/Resistance (often liquidation zones)
        r"[Rr]esistance:\s*\$?([0-9,]+\.?[0-9]*)",
        r"[Ss]upport:\s*\$?([0-9,]+\.?[0-9]*)",
        # Range patterns
        r"\$?([0-9,]+\.?[0-9]*)\s*[-–]\s*\$?([0-9,]+\.?[0-9]*)",
        # In lists
        r"[-•]\s*\$?([0-9,]+\.?[0-9]*)",
        # Technical data section
        r"Levels?:\s*\$?([0-9,]+\.?[0-9]*)",
        r"Clusters?:\s*\$?([0-9,]+\.?[0-9]*)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                # For range patterns, add both values
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
    
    # Remove duplicates and sort
    clusters = sorted(list(set(clusters)))
    
    print(f"   ✓ Found {len(clusters)} unique liquidation levels")
    return clusters

def find_closest_clusters(current_price, clusters, min_distance_pct=0.02):
    """Find the 4 closest liquidation clusters with minimum 2% distance"""
    if not clusters or not current_price:
        return None, None, None, None
    
    # Calculate minimum distance
    min_distance = current_price * min_distance_pct
    
    # Separate below and above clusters with minimum distance requirement
    below = [c for c in clusters if c < (current_price - min_distance)]
    above = [c for c in clusters if c > (current_price + min_distance)]
    
    # Sort by distance from current price
    below.sort(key=lambda x: current_price - x)  # Closest first
    above.sort(key=lambda x: x - current_price)   # Closest first
    
    # Get the required clusters
    liqcluster_minus2 = below[1] if len(below) > 1 else None
    liqcluster_minus1 = below[0] if len(below) > 0 else None
    liqcluster_plus1 = above[0] if len(above) > 0 else None
    liqcluster_plus2 = above[1] if len(above) > 1 else None
    
    return liqcluster_minus2, liqcluster_minus1, liqcluster_plus1, liqcluster_plus2

def verify_and_update_airtable(symbol, current_price, clusters_data):
    """Update Airtable with VERIFICATION of correct symbol row"""
    if not AIRTABLE_ENABLED:
        print(f"\n   📝 TEST MODE - Would update Airtable for {symbol}")
        print(f"      Current Price: ${current_price:.2f}")
        print(f"      Clusters: {clusters_data}")
        return True
    
    if not symbol:
        print("   ❌ ERROR: Cannot update Airtable without valid symbol")
        return False
    
    try:
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Prepare update data
        update_fields = {}
        
        # ALWAYS update current price
        if current_price is not None:
            update_fields['CurrentPrice'] = current_price
        
        # Add liquidation clusters
        if clusters_data[0] is not None:
            update_fields['Liqcluster-2'] = clusters_data[0]
        if clusters_data[1] is not None:
            update_fields['Liqcluster-1'] = clusters_data[1]
        if clusters_data[2] is not None:
            update_fields['Liqcluster1'] = clusters_data[2]
        if clusters_data[3] is not None:
            update_fields['Liqcluster2'] = clusters_data[3]
        
        # Add timestamp
        update_fields['LastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # CRITICAL: Find the EXACT record by symbol
        print(f"\n   🔍 Searching for symbol '{symbol}' in Airtable...")
        records = table.all(formula=f"{{Symbol}} = '{symbol}'")
        
        if records:
            # VERIFY we have the correct record
            record = records[0]
            existing_symbol = record['fields'].get('Symbol', '').upper()
            
            if existing_symbol != symbol.upper():
                print(f"   ❌ ERROR: Symbol mismatch! Found '{existing_symbol}' but need '{symbol}'")
                return False
            
            # Update the VERIFIED correct record
            record_id = record['id']
            table.update(record_id, update_fields)
            print(f"\n   ✅ VERIFIED UPDATE for {symbol} (Record ID: {record_id})")
        else:
            # Create new record ONLY if symbol doesn't exist
            print(f"   📝 Creating NEW record for {symbol}")
            create_fields = {'Symbol': symbol}
            create_fields.update(update_fields)
            new_record = table.create(create_fields)
            print(f"   ✅ Created new record for {symbol} (ID: {new_record['id']})")
        
        # Show what was updated
        print(f"\n   📊 Updated Data for {symbol}:")
        print(f"      Current Price: ${current_price:.2f}" if current_price else "      Current Price: Not updated")
        print(f"      Liqcluster-2: ${clusters_data[0]:.2f} (-{((current_price-clusters_data[0])/current_price*100):.1f}%)" if clusters_data[0] and current_price else "      Liqcluster-2: None")
        print(f"      Liqcluster-1: ${clusters_data[1]:.2f} (-{((current_price-clusters_data[1])/current_price*100):.1f}%)" if clusters_data[1] and current_price else "      Liqcluster-1: None")
        print(f"      Liqcluster+1: ${clusters_data[2]:.2f} (+{((clusters_data[2]-current_price)/current_price*100):.1f}%)" if clusters_data[2] and current_price else "      Liqcluster+1: None")
        print(f"      Liqcluster+2: ${clusters_data[3]:.2f} (+{((clusters_data[3]-current_price)/current_price*100):.1f}%)" if clusters_data[3] and current_price else "      Liqcluster+2: None")
        print(f"      Updated at: {datetime.now().strftime('%H:%M:%S')}")
        
        return True
            
    except Exception as e:
        print(f"\n   ❌ ERROR updating Airtable: {e}")
        return False

def process_md_file(filepath, folder_path):
    """Process a single MD file with enhanced accuracy"""
    print(f"\n{'='*60}")
    print(f"📄 Processing: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        # Read MD file
        with open(filepath, 'r') as f:
            content = f.read()
        
        # STEP 1: Extract symbol (MANDATORY)
        symbol = extract_symbol_from_md(content)
        if not symbol:
            print("\n   ❌ CRITICAL: Cannot process without valid symbol")
            print("   ⚠️  File will be skipped to prevent wrong updates")
            return False
        
        # STEP 2: Extract current price (MANDATORY)
        current_price = extract_current_price(content)
        if not current_price:
            print("\n   ⚠️ WARNING: No current price found")
            # Continue but won't calculate percentages
        
        # STEP 3: Extract all liquidation clusters
        clusters = extract_liquidation_clusters(content)
        if not clusters:
            print("   ⚠️ WARNING: No liquidation clusters found")
            # Still update with current price if available
        
        # STEP 4: Find the 4 closest clusters with 2% rule
        liq_minus2, liq_minus1, liq_plus1, liq_plus2 = None, None, None, None
        if clusters and current_price:
            liq_minus2, liq_minus1, liq_plus1, liq_plus2 = find_closest_clusters(
                current_price, clusters
            )
            
            print(f"\n   🎯 Selected Clusters (min 2% from ${current_price:.2f}):")
            print(f"      Below: {f'${liq_minus2:.2f}' if liq_minus2 else 'None'}, {f'${liq_minus1:.2f}' if liq_minus1 else 'None'}")
            print(f"      Above: {f'${liq_plus1:.2f}' if liq_plus1 else 'None'}, {f'${liq_plus2:.2f}' if liq_plus2 else 'None'}")
        
        # STEP 5: Update Airtable with VERIFICATION
        if verify_and_update_airtable(symbol, current_price, (liq_minus2, liq_minus1, liq_plus1, liq_plus2)):
            # Move file to HistoryData after successful update
            history_folder = create_history_folder(folder_path)
            new_path = os.path.join(history_folder, os.path.basename(filepath))
            
            # Add timestamp if file already exists
            if os.path.exists(new_path):
                base, ext = os.path.splitext(os.path.basename(filepath))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_path = os.path.join(history_folder, f"{base}_{timestamp}{ext}")
            
            shutil.move(filepath, new_path)
            print(f"\n   ✅ Archived to: HistoryData/{os.path.basename(new_path)}")
            return True
        else:
            print("\n   ⚠️ Update failed - file not moved")
            return False
        
    except Exception as e:
        print(f"\n   ❌ ERROR processing file: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_latest_md_file():
    """Get the most recently modified MD file from all monitored folders"""
    latest_file = None
    latest_time = None
    latest_folder = None
    
    for folder in FOLDERS_TO_MONITOR:
        if not os.path.exists(folder):
            continue
        
        # Get all MD files in folder (not in HistoryData)
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
    """Monitor and update every 5 minutes with ACCURATE symbol matching"""
    print("="*70)
    print("STEP 5: ACCURATE SYMBOL-SPECIFIC LIQUIDATION UPDATES")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n♾️  Continuous monitoring mode - Updates every 5 minutes")
    print("✓ Symbol verification enabled")
    print("✓ Current price updates enabled")
    print("✓ 2% minimum distance rule active")
    print("\nPress Ctrl+C to stop\n")
    
    last_update_time = datetime.now()
    
    while True:
        current_time = datetime.now()
        time_since_update = (current_time - last_update_time).total_seconds()
        
        if time_since_update >= update_interval:
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Checking for latest MD file...")
            
            # Get the most recent MD file
            latest_file, latest_folder = get_latest_md_file()
            
            if latest_file and latest_folder:
                file_age = (current_time - datetime.fromtimestamp(os.path.getmtime(latest_file))).total_seconds()
                print(f"   Found: {os.path.basename(latest_file)}")
                print(f"   Age: {int(file_age/60)} minutes old")
                
                # Process with enhanced accuracy
                if process_md_file(latest_file, latest_folder):
                    print(f"\n✅ Successfully updated Airtable with verified symbol match")
                else:
                    print(f"\n⚠️ Update skipped - accuracy requirements not met")
            else:
                print(f"   No MD files found to process")
            
            last_update_time = current_time
            
            # Show countdown to next update
            print(f"\n⏰ Next update at {(current_time + timedelta(seconds=update_interval)).strftime('%H:%M:%S')}")
        
        # Show progress
        remaining = update_interval - time_since_update
        if remaining > 0:
            print(f"\r⏳ Next update in {int(remaining)} seconds...", end="", flush=True)
        time.sleep(1)

def main():
    """Main function"""
    import sys
    
    # Check if running in one-time mode
    one_time = "--once" in sys.argv or "-o" in sys.argv
    
    if one_time:
        print("="*70)
        print("STEP 5: ACCURATE SYMBOL-SPECIFIC LIQUIDATION UPDATES")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print("\n🔍 Running in one-time mode with symbol verification")
        
        # Get the latest MD file
        latest_file, latest_folder = get_latest_md_file()
        
        if latest_file and latest_folder:
            print(f"\n   Latest file: {os.path.basename(latest_file)}")
            process_md_file(latest_file, latest_folder)
        else:
            print("\n   No MD files found to process")
    else:
        try:
            monitor_continuous()
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()