#!/usr/bin/env python3
"""
STEP 5: EXTRACT LIQUIDATION CLUSTERS AND UPDATE AIRTABLE
- Monitors mdfiles folders for new MD reports
- Extracts liquidation cluster prices from analysis
- Updates Airtable with 4 closest clusters (2 below, 2 above current price)
- Moves processed files to HistoryData folder
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
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'CursorTable')

# Check if Airtable is configured
AIRTABLE_ENABLED = AIRTABLE_API_KEY and AIRTABLE_BASE_ID

if not AIRTABLE_ENABLED:
    print("\n⚠️  AIRTABLE NOT FULLY CONFIGURED!")
    if not AIRTABLE_API_KEY:
        print("❌ Missing AIRTABLE_API_KEY in .env file")
    if not AIRTABLE_BASE_ID:
        print("❌ Missing AIRTABLE_BASE_ID in .env file")
    elif not AIRTABLE_BASE_ID.startswith('app'):
        print(f"⚠️  AIRTABLE_BASE_ID should start with 'app'")
        print(f"   Current value: {AIRTABLE_BASE_ID}")
        print(f"   Expected format: appXXXXXXXXXXXXXX")
        print(f"   Find it in your Airtable URL: airtable.com/appXXXXXXXXXXXXXX/...")
    print(f"\nTable Name: {AIRTABLE_TABLE_NAME}")
    print("\nRunning in TEST MODE - will extract data but not update Airtable\n")

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
    """Extract cryptocurrency symbol from MD content"""
    # Look for patterns like "Trading Pair: SOL/USDT" or "symbol: LINK"
    patterns = [
        r"Trading Pair:\s*([A-Z]+)/USDT",
        r"cryptocurrency symbol:\s*([A-Z]+)",
        r"Symbol:\s*([A-Z]+)",
        r"symbol:\s*([A-Z]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    return None

def extract_current_price(content):
    """Extract current price from MD content"""
    patterns = [
        r"Current [Pp]rice:\s*\$?([\d,]+\.?\d*)",
        r"Current Price:\s*\$?([\d,]+\.?\d*)\s*USDT",
        r"price:\s*\$?([\d,]+\.?\d*)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                return float(price_str)
            except:
                continue
    
    return None

def extract_liquidation_clusters(content):
    """Extract all liquidation cluster prices from MD content"""
    clusters = []
    
    # Multiple patterns to catch different formats
    patterns = [
        # Format: $160-165 or $160-$165
        r"\$?([\d,]+\.?\d*)\s*[-–]\s*\$?([\d,]+\.?\d*)",
        # Format: Cluster at $160
        r"[Cc]luster.*?\$?([\d,]+\.?\d*)",
        # Format: Levels: $xxx, $xxx
        r"Levels?:\s*\$?([\d,]+\.?\d*)",
        # Format: liquidation at $xxx
        r"liquidation.*?\$?([\d,]+\.?\d*)",
        # Format: Location: $[exact range] (e.g., $160-165)
        r"Location:\s*\$?\[?([\d,]+\.?\d*)",
        # Format: price range: $[start]-[end]
        r"price range:\s*\$?([\d,]+\.?\d*)",
        # Format: Massive clusters: $16.05
        r"Massive clusters?:\s*\$?([\d,]+\.?\d*)",
        # Format: Critical clusters: $13.65
        r"Critical clusters?:\s*\$?([\d,]+\.?\d*)",
        # Format: Secondary clusters: $18.47
        r"Secondary clusters?:\s*\$?([\d,]+\.?\d*)",
        # Format: resistance: $16.00
        r"resistance:\s*\$?([\d,]+\.?\d*)",
        # Format: support: $11.00
        r"support:\s*\$?([\d,]+\.?\d*)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                # For range patterns, take the midpoint
                try:
                    val1 = float(match[0].replace(',', ''))
                    if len(match) > 1 and match[1]:
                        val2 = float(match[1].replace(',', ''))
                        clusters.append((val1 + val2) / 2)
                    else:
                        clusters.append(val1)
                except:
                    continue
            else:
                try:
                    clusters.append(float(match.replace(',', '')))
                except:
                    continue
    
    # Remove duplicates and sort
    clusters = sorted(list(set(clusters)))
    
    # Filter out unrealistic values (too small or too large)
    clusters = [c for c in clusters if 0.01 < c < 100000]
    
    return clusters

def find_closest_clusters(current_price, clusters, num_below=2, num_above=2):
    """Find the closest liquidation clusters relative to current price with minimum 2% distance"""
    if not clusters or not current_price:
        return None, None, None, None
    
    # Filter clusters with minimum 2% distance from current price
    min_distance_pct = 0.02  # 2% minimum distance
    min_distance = current_price * min_distance_pct
    
    # Separate below and above clusters with minimum distance requirement
    below = [c for c in clusters if c < (current_price - min_distance)]
    above = [c for c in clusters if c > (current_price + min_distance)]
    
    # Sort by distance from current price
    below.sort(key=lambda x: current_price - x)  # Closest first
    above.sort(key=lambda x: x - current_price)   # Closest first
    
    # Get the required number of clusters (2 below, 2 above)
    selected_below = []
    selected_above = []
    
    # Select below clusters (need exactly 2)
    for cluster in below:
        if len(selected_below) < 2:
            selected_below.append(cluster)
    
    # Select above clusters (need exactly 2)
    for cluster in above:
        if len(selected_above) < 2:
            selected_above.append(cluster)
    
    # Ensure we have exactly 2 below and 2 above
    liqcluster_minus2 = selected_below[1] if len(selected_below) > 1 else None
    liqcluster_minus1 = selected_below[0] if len(selected_below) > 0 else None
    liqcluster_plus1 = selected_above[0] if len(selected_above) > 0 else None
    liqcluster_plus2 = selected_above[1] if len(selected_above) > 1 else None
    
    return liqcluster_minus2, liqcluster_minus1, liqcluster_plus1, liqcluster_plus2

def update_airtable(symbol, clusters_data):
    """Update Airtable with liquidation cluster data"""
    if not AIRTABLE_ENABLED:
        print(f"   📝 TEST MODE - Would update Airtable for {symbol}")
        return True
    
    try:
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Prepare update data
        update_fields = {}
        
        if clusters_data[0] is not None:
            update_fields['Liqcluster-2'] = clusters_data[0]
        if clusters_data[1] is not None:
            update_fields['Liqcluster-1'] = clusters_data[1]
        if clusters_data[2] is not None:
            update_fields['Liqcluster1'] = clusters_data[2]
        if clusters_data[3] is not None:
            update_fields['Liqcluster2'] = clusters_data[3]
        
        # Find record by symbol
        records = table.all(formula=f"{{Symbol}} = '{symbol}'")
        
        if records:
            # Update existing record (always update with latest data)
            record_id = records[0]['id']
            table.update(record_id, update_fields)
            print(f"✅ Updated Airtable record for {symbol}:")
        else:
            # Create new record
            create_fields = {'Symbol': symbol}
            create_fields.update(update_fields)
            table.create(create_fields)
            print(f"✅ Created new Airtable record for {symbol}:")
        
        # Show what was updated
        print(f"   Liqcluster-2: ${clusters_data[0]:.2f}" if clusters_data[0] else "   Liqcluster-2: None")
        print(f"   Liqcluster-1: ${clusters_data[1]:.2f}" if clusters_data[1] else "   Liqcluster-1: None")
        print(f"   Liqcluster+1: ${clusters_data[2]:.2f}" if clusters_data[2] else "   Liqcluster+1: None")
        print(f"   Liqcluster+2: ${clusters_data[3]:.2f}" if clusters_data[3] else "   Liqcluster+2: None")
        print(f"   Updated at: {datetime.now().strftime('%H:%M:%S')}")
        return True
            
    except Exception as e:
        print(f"❌ Error updating Airtable: {e}")
        return False

def process_md_file(filepath, folder_path):
    """Process a single MD file to extract and update liquidation clusters"""
    print(f"\n📄 Processing: {os.path.basename(filepath)}")
    print("="*60)
    
    try:
        # Read MD file
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract symbol
        symbol = extract_symbol_from_md(content)
        if not symbol:
            print("   ⚠️ Could not extract symbol from MD file")
            return False
        
        print(f"   Symbol: {symbol}")
        
        # Extract current price
        current_price = extract_current_price(content)
        if not current_price:
            print("   ⚠️ Could not extract current price from MD file")
            return False
        
        print(f"   Current Price: ${current_price:.2f}")
        
        # Extract all liquidation clusters
        clusters = extract_liquidation_clusters(content)
        if not clusters:
            print("   ⚠️ Could not extract liquidation clusters from MD file")
            return False
        
        print(f"   Found {len(clusters)} liquidation levels")
        print(f"   Clusters: {[f'${c:.2f}' for c in clusters[:10]]}")  # Show first 10
        
        # Find the 4 closest clusters
        liq_minus2, liq_minus1, liq_plus1, liq_plus2 = find_closest_clusters(
            current_price, clusters
        )
        
        print(f"\n   Selected Clusters (min 2% distance from ${current_price:.2f}):")
        print(f"   Below current price:")
        if liq_minus2:
            pct_diff = ((current_price - liq_minus2) / current_price) * 100
            print(f"     Liqcluster-2: ${liq_minus2:.2f} (-{pct_diff:.1f}%)")
        else:
            print(f"     Liqcluster-2: None")
        if liq_minus1:
            pct_diff = ((current_price - liq_minus1) / current_price) * 100
            print(f"     Liqcluster-1: ${liq_minus1:.2f} (-{pct_diff:.1f}%)")
        else:
            print(f"     Liqcluster-1: None")
        print(f"   Above current price:")
        if liq_plus1:
            pct_diff = ((liq_plus1 - current_price) / current_price) * 100
            print(f"     Liqcluster+1: ${liq_plus1:.2f} (+{pct_diff:.1f}%)")
        else:
            print(f"     Liqcluster+1: None")
        if liq_plus2:
            pct_diff = ((liq_plus2 - current_price) / current_price) * 100
            print(f"     Liqcluster+2: ${liq_plus2:.2f} (+{pct_diff:.1f}%)")
        else:
            print(f"     Liqcluster+2: None")
        
        # Update Airtable
        if update_airtable(symbol, (liq_minus2, liq_minus1, liq_plus1, liq_plus2)):
            # Move file to HistoryData
            history_folder = create_history_folder(folder_path)
            new_path = os.path.join(history_folder, os.path.basename(filepath))
            
            # Add timestamp if file already exists
            if os.path.exists(new_path):
                base, ext = os.path.splitext(os.path.basename(filepath))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_path = os.path.join(history_folder, f"{base}_{timestamp}{ext}")
            
            shutil.move(filepath, new_path)
            print(f"   ✅ Moved to: HistoryData/{os.path.basename(new_path)}")
            return True
        
    except Exception as e:
        print(f"   ❌ Error processing file: {e}")
        return False
    
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

def monitor_folders(one_time=False):
    """Monitor folders and update Airtable based on latest MD file every 5 minutes"""
    print("="*60)
    print("STEP 5: LIQUIDATION CLUSTER EXTRACTION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if not one_time:
        print("\n♾️  Continuous monitoring mode - Updates every 5 minutes")
        print("Based on the LATEST MD file in LiquidationMap or LiquidationHeatmap")
        print("Press Ctrl+C to stop\n")
    else:
        print("\nLooking for the latest MD file...")
    
    last_update_time = datetime.now()
    update_interval = 300  # 5 minutes in seconds
    
    while True:
        current_time = datetime.now()
        time_since_update = (current_time - last_update_time).total_seconds()
        
        # Process files every 5 minutes or immediately in one-time mode
        if one_time or time_since_update >= update_interval:
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Checking for latest MD file...")
            
            # Get the most recent MD file
            latest_file, latest_folder = get_latest_md_file()
            
            if latest_file and latest_folder:
                file_age = (current_time - datetime.fromtimestamp(os.path.getmtime(latest_file))).total_seconds()
                print(f"   Found: {os.path.basename(latest_file)}")
                print(f"   Age: {int(file_age/60)} minutes old")
                print(f"   Folder: {os.path.basename(latest_folder)}")
                
                # Process the latest file
                if process_md_file(latest_file, latest_folder):
                    print(f"\n✅ Successfully updated Airtable from latest image analysis")
                else:
                    print(f"\n⚠️ Could not process the latest file")
            else:
                print(f"   No MD files found to process")
            
            last_update_time = current_time
            
            if one_time:
                break
            
            # Show countdown to next update
            print(f"\n⏰ Next update in 5 minutes at {(current_time + timedelta(seconds=update_interval)).strftime('%H:%M:%S')}")
        
        if not one_time:
            # Show progress dots while waiting
            remaining = update_interval - time_since_update
            if remaining > 0:
                print(f"\r⏳ Next update in {int(remaining)} seconds...", end="", flush=True)
            time.sleep(1)  # Check every second for smoother countdown

def main():
    """Main function"""
    import sys
    
    # Check if running in one-time mode
    one_time = "--once" in sys.argv or "-o" in sys.argv
    
    if one_time:
        print("\n🔍 Running in one-time mode (process existing files)")
    else:
        print("\n♾️  Running in continuous monitoring mode")
        print("Press Ctrl+C to stop\n")
    
    try:
        monitor_folders(one_time=one_time)
        
        if one_time:
            print("\n✅ Processed all existing MD files")
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()