#!/usr/bin/env python3
"""
ZmartBot Cache Management Script
View cache status, clear cache, and manage cached data
"""

import json
import os
from datetime import datetime
import argparse

def load_cache(cache_file='symbol_data_cache.json'):
    """Load cache from file"""
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache, cache_file='symbol_data_cache.json'):
    """Save cache to file"""
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)

def view_cache_status():
    """View cache status and statistics"""
    cache = load_cache()
    
    if not cache:
        print("❌ No cache file found")
        return
    
    print("📊 Cache Status")
    print("===============")
    print(f"Total entries: {len(cache)}")
    
    # Group by symbol
    symbols = {}
    for key, value in cache.items():
        symbol = key.split('_')[0]
        timeframe = key.split('_')[1]
        if symbol not in symbols:
            symbols[symbol] = []
        symbols[symbol].append(timeframe)
    
    print(f"Symbols cached: {len(symbols)}")
    print()
    
    print("📈 Cached Data by Symbol:")
    for symbol, timeframes in symbols.items():
        print(f"  {symbol}: {', '.join(timeframes)}")
    
    print()
    
    # Check cache age
    current_time = datetime.now()
    oldest_cache = None
    newest_cache = None
    
    for key, value in cache.items():
        cache_time = datetime.fromisoformat(value['timestamp'])
        age = (current_time - cache_time).total_seconds() / 3600  # hours
        
        if oldest_cache is None or age > oldest_cache[1]:
            oldest_cache = (key, age)
        if newest_cache is None or age < newest_cache[1]:
            newest_cache = (key, age)
    
    if oldest_cache:
        print(f"⏰ Oldest cache: {oldest_cache[0]} ({oldest_cache[1]:.1f} hours ago)")
    if newest_cache:
        print(f"⏰ Newest cache: {newest_cache[0]} ({newest_cache[1]:.1f} hours ago)")
    
    print()
    
    # Check which entries are expired (older than 1 hour)
    expired_count = 0
    for key, value in cache.items():
        cache_time = datetime.fromisoformat(value['timestamp'])
        age = (current_time - cache_time).total_seconds()
        if age > 3600:  # 1 hour
            expired_count += 1
    
    print(f"🔄 Expired entries (need refresh): {expired_count}")
    print(f"✅ Valid entries: {len(cache) - expired_count}")

def clear_cache():
    """Clear all cached data"""
    cache_file = 'symbol_data_cache.json'
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("🗑️ Cache cleared successfully")
    else:
        print("❌ No cache file found to clear")

def clear_symbol_cache(symbol):
    """Clear cache for a specific symbol"""
    cache = load_cache()
    if not cache:
        print("❌ No cache file found")
        return
    
    # Remove all entries for this symbol
    keys_to_remove = [key for key in cache.keys() if key.startswith(f"{symbol}_")]
    
    if not keys_to_remove:
        print(f"❌ No cached data found for {symbol}")
        return
    
    for key in keys_to_remove:
        del cache[key]
    
    save_cache(cache)
    print(f"🗑️ Cleared cache for {symbol} ({len(keys_to_remove)} entries)")

def main():
    parser = argparse.ArgumentParser(description='ZmartBot Cache Management')
    parser.add_argument('action', choices=['status', 'clear', 'clear-symbol'], 
                       help='Action to perform')
    parser.add_argument('--symbol', help='Symbol to clear cache for (when using clear-symbol)')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        view_cache_status()
    elif args.action == 'clear':
        clear_cache()
    elif args.action == 'clear-symbol':
        if not args.symbol:
            print("❌ Please specify a symbol with --symbol")
            return
        clear_symbol_cache(args.symbol.upper())

if __name__ == "__main__":
    main()
