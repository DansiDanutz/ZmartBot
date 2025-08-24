#!/usr/bin/env python3
"""
Verify 17 Symbols in RiskMetric Database
Quick verification that all 17 symbols are properly loaded and accessible
Fixed to avoid complex import dependencies
"""

import sqlite3
import os
from datetime import datetime

def main():
    print("🔍 VERIFYING RISKMETRIC DATABASE - 17 SYMBOLS")
    print("=" * 60)
    
    # Expected 17 symbols from Benjamin Cowen's methodology
    expected_symbols = [
        'BTC', 'ETH', 'BNB', 'LINK', 'SOL',
        'ADA', 'DOT', 'AVAX', 'TON', 'POL', 
        'DOGE', 'TRX', 'SHIB', 'VET', 'ALGO',
        'LTC', 'XRP'
    ]
    
    # Database paths to check
    db_paths = [
        'backend/zmart-api/data/comprehensive_riskmetric.db',
        'backend/zmart-api/test_comprehensive_riskmetric.db',
        'backend/zmart-api/comprehensive_riskmetric.db'
    ]
    
    found_db = None
    for db_path in db_paths:
        if os.path.exists(db_path):
            found_db = db_path
            break
    
    if not found_db:
        print("❌ No RiskMetric database found!")
        print("   Searched paths:")
        for path in db_paths:
            print(f"   - {path}")
        return False
    
    print(f"📂 Using database: {found_db}")
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(found_db)
        cursor = conn.cursor()
        
        # Check if symbols table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='symbols'
        """)
        
        if not cursor.fetchone():
            print("❌ Symbols table not found in database!")
            return False
        
        print("✅ Symbols table found")
        
        # Get all symbols from database
        cursor.execute("SELECT symbol FROM symbols ORDER BY symbol")
        db_symbols = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Database contains {len(db_symbols)} symbols")
        print(f"🎯 Expected: {len(expected_symbols)} symbols")
        print()
        
        # Check each expected symbol
        missing_symbols = []
        found_symbols = []
        
        for symbol in expected_symbols:
            if symbol in db_symbols:
                found_symbols.append(symbol)
                print(f"   ✅ {symbol}")
            else:
                missing_symbols.append(symbol)
                print(f"   ❌ {symbol} - MISSING")
        
        print()
        print("=" * 60)
        print("📋 VERIFICATION RESULTS:")
        print(f"   Found symbols: {len(found_symbols)}/{len(expected_symbols)}")
        print(f"   Missing symbols: {len(missing_symbols)}")
        
        if missing_symbols:
            print(f"   Missing: {', '.join(missing_symbols)}")
        
        # Additional database info
        cursor.execute("SELECT COUNT(*) FROM symbols")
        total_symbols = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM risk_levels")
        total_risk_levels = cursor.fetchone()[0]
        
        print(f"   Total symbols in DB: {total_symbols}")
        print(f"   Total risk levels: {total_risk_levels}")
        
        # Check for extra symbols
        extra_symbols = [s for s in db_symbols if s not in expected_symbols]
        if extra_symbols:
            print(f"   Extra symbols: {', '.join(extra_symbols)}")
        
        print("=" * 60)
        
        # Final status
        if len(found_symbols) == len(expected_symbols):
            print("🎉 SUCCESS: All 17 symbols verified!")
            return True
        else:
            print(f"⚠️  INCOMPLETE: {len(missing_symbols)} symbols missing")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)