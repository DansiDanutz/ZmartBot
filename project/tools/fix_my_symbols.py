#!/usr/bin/env python3
"""
Fix My Symbols Portfolio - Add default symbols to portfolio
"""

import sqlite3
import uuid
from datetime import datetime

def fix_my_symbols_portfolio():
    """Fix the My Symbols portfolio by adding default symbols"""
    
    db_path = "my_symbols_v2.db"
    
    # Default symbols to add
    default_symbols = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", 
        "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT"
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing My Symbols Portfolio...")
        
        # First, clear any existing portfolio entries
        cursor.execute("DELETE FROM portfolio_composition")
        print("✅ Cleared existing portfolio entries")
        
        # Get symbol IDs for each default symbol
        for i, symbol in enumerate(default_symbols):
            cursor.execute("SELECT id FROM symbols WHERE symbol = ?", (symbol,))
            result = cursor.fetchone()
            
            if result:
                symbol_id = result[0]
                
                # Add to portfolio composition with correct schema
                cursor.execute('''
                    INSERT INTO portfolio_composition (
                        id, symbol_id, position_rank, inclusion_date, inclusion_reason,
                        current_score, weight_percentage, status, is_replacement_candidate,
                        replacement_priority, performance_since_inclusion,
                        max_drawdown_since_inclusion, volatility_since_inclusion,
                        is_tradeable, last_validation, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()),
                    symbol_id,
                    i + 1,  # position_rank
                    datetime.now().isoformat(),  # inclusion_date
                    'Default portfolio symbol',  # inclusion_reason
                    0.75,  # current_score
                    10.0,  # weight_percentage (10% each)
                    'Active',  # status
                    False,  # is_replacement_candidate
                    None,  # replacement_priority
                    None,  # performance_since_inclusion
                    None,  # max_drawdown_since_inclusion
                    None,  # volatility_since_inclusion
                    True,  # is_tradeable
                    datetime.now().isoformat(),  # last_validation
                    datetime.now().isoformat(),  # created_at
                    datetime.now().isoformat()   # updated_at
                ))
                
                print(f"✅ Added {symbol} to portfolio (rank {i + 1})")
            else:
                print(f"❌ Symbol {symbol} not found in symbols table")
        
        conn.commit()
        conn.close()
        
        print("🎉 My Symbols Portfolio fixed successfully!")
        print(f"📊 Added {len(default_symbols)} symbols to portfolio")
        
        # Verify the fix
        verify_portfolio()
        
    except Exception as e:
        print(f"❌ Error fixing portfolio: {e}")

def verify_portfolio():
    """Verify the portfolio was fixed correctly"""
    try:
        conn = sqlite3.connect("my_symbols_v2.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.symbol, pc.position_rank, pc.status 
            FROM portfolio_composition pc 
            JOIN symbols s ON pc.symbol_id = s.id 
            WHERE pc.status = 'Active' 
            ORDER BY pc.position_rank
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        print("\n📋 Portfolio Verification:")
        print("=" * 50)
        for symbol, rank, status in results:
            print(f"  {rank:2d}. {symbol} - {status}")
        
        print(f"\n✅ Total symbols in portfolio: {len(results)}")
        
    except Exception as e:
        print(f"❌ Error verifying portfolio: {e}")

if __name__ == "__main__":
    fix_my_symbols_portfolio()
