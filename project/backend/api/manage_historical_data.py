#!/usr/bin/env python3
"""
Historical Data Management Script
Manage and view statistics for the HistoryMySymbols database
"""

import sys
import argparse
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append('.')

from historical_data_service import historical_data_service

def show_database_stats():
    """Show database statistics"""
    print("📊 HistoryMySymbols Database Statistics")
    print("========================================")
    
    stats = historical_data_service.get_database_stats()
    
    if not stats:
        print("❌ No data found in database")
        return
    
    print(f"📈 Total Records: {stats['total_records']}")
    print()
    
    print("📋 Table Statistics:")
    for table, count in stats['table_counts'].items():
        print(f"   {table}: {count:,} records")
    
    print()
    
    if stats['date_range'][0] and stats['date_range'][1]:
        start_date = datetime.fromisoformat(stats['date_range'][0])
        end_date = datetime.fromisoformat(stats['date_range'][1])
        print(f"📅 Date Range: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Calculate data points per hour
        hours_diff = (end_date - start_date).total_seconds() / 3600
        if hours_diff > 0:
            records_per_hour = stats['total_records'] / hours_diff
            print(f"📊 Average Records per Hour: {records_per_hour:.1f}")
    
    print()

def show_symbol_data(symbol: str, timeframe: str = '1h', hours_back: int = 24):
    """Show historical data for a specific symbol"""
    print(f"📈 Historical Data for {symbol} ({timeframe})")
    print(f"⏰ Last {hours_back} hours")
    print("=" * 50)
    
    data = historical_data_service.get_historical_data(symbol, timeframe, hours_back)
    
    if not data or all(df.empty for df in data.values()):
        print("❌ No historical data found")
        return
    
    for indicator, df in data.items():
        if not df.empty:
            print(f"\n📊 {indicator.upper()}:")
            print(f"   Records: {len(df)}")
            if len(df) > 0:
                latest = df.iloc[0]
                print(f"   Latest: {latest['snapshot_timestamp']}")
                if 'current_price' in df.columns:
                    print(f"   Price: ${latest['current_price']:.2f}")

def cleanup_old_data(days_to_keep: int = 30):
    """Clean up old historical data"""
    print(f"🗑️ Cleaning up data older than {days_to_keep} days...")
    
    # Get stats before cleanup
    stats_before = historical_data_service.get_database_stats()
    total_before = stats_before.get('total_records', 0)
    
    # Perform cleanup
    historical_data_service.cleanup_old_data(days_to_keep)
    
    # Get stats after cleanup
    stats_after = historical_data_service.get_database_stats()
    total_after = stats_after.get('total_records', 0)
    
    deleted = total_before - total_after
    print(f"✅ Cleanup completed: {deleted:,} records deleted")
    print(f"📊 Remaining records: {total_after:,}")

def show_pattern_analysis(symbol: str, timeframe: str = '1h', days_back: int = 7):
    """Show pattern analysis data"""
    print(f"🔍 Pattern Analysis for {symbol} ({timeframe})")
    print(f"📅 Last {days_back} days")
    print("=" * 50)
    
    pattern_data = historical_data_service.get_pattern_analysis_data(symbol, timeframe, days_back)
    
    if pattern_data.empty:
        print("❌ No pattern analysis data found")
        return
    
    print(f"📊 Total Patterns: {len(pattern_data)}")
    print()
    
    # Show pattern types
    if 'pattern_type' in pattern_data.columns:
        pattern_counts = pattern_data['pattern_type'].value_counts()
        print("📋 Pattern Types:")
        for pattern, count in pattern_counts.items():
            print(f"   {pattern}: {count}")
    
    print()
    
    # Show recent patterns
    if len(pattern_data) > 0:
        print("🕐 Recent Patterns:")
        recent_patterns = pattern_data.head(5)
        for _, pattern in recent_patterns.iterrows():
            timestamp = pattern['snapshot_timestamp']
            pattern_type = pattern.get('pattern_type', 'Unknown')
            strength = pattern.get('pattern_strength', 0)
            direction = pattern.get('pattern_direction', 'Unknown')
            print(f"   {timestamp}: {pattern_type} ({direction}) - Strength: {strength:.2f}")

def main():
    parser = argparse.ArgumentParser(description='Historical Data Management')
    parser.add_argument('action', choices=['stats', 'symbol', 'cleanup', 'patterns'], 
                       help='Action to perform')
    parser.add_argument('--symbol', help='Symbol to analyze')
    parser.add_argument('--timeframe', default='1h', choices=['15m', '1h', '4h', '1d'],
                       help='Timeframe to analyze')
    parser.add_argument('--hours', type=int, default=24, help='Hours back to analyze')
    parser.add_argument('--days', type=int, default=7, help='Days back to analyze')
    parser.add_argument('--keep-days', type=int, default=30, help='Days to keep when cleaning up')
    
    args = parser.parse_args()
    
    if args.action == 'stats':
        show_database_stats()
    elif args.action == 'symbol':
        if not args.symbol:
            print("❌ Please specify a symbol with --symbol")
            return
        show_symbol_data(args.symbol, args.timeframe, args.hours)
    elif args.action == 'cleanup':
        cleanup_old_data(args.keep_days)
    elif args.action == 'patterns':
        if not args.symbol:
            print("❌ Please specify a symbol with --symbol")
            return
        show_pattern_analysis(args.symbol, args.timeframe, args.days)

if __name__ == "__main__":
    main()
