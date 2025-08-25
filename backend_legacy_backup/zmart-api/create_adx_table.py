#!/usr/bin/env python3
"""
Create ADX Table
Adds the adx_data table to the database for storing ADX (Average Directional Index) indicators
"""

import sqlite3
import os
from datetime import datetime

def create_adx_table():
    """Create the adx_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create adx_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adx_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                adx_value REAL NOT NULL,
                plus_di REAL NOT NULL,
                minus_di REAL NOT NULL,
                trend_strength TEXT NOT NULL,
                trend_strength_value REAL DEFAULT 0.0,
                trend_direction TEXT NOT NULL,
                di_crossover TEXT DEFAULT 'none',
                di_crossover_strength REAL DEFAULT 0.0,
                momentum_signal TEXT DEFAULT 'neutral',
                momentum_strength REAL DEFAULT 0.0,
                breakout_potential TEXT DEFAULT 'none',
                breakout_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_adx_data_symbol 
            ON adx_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_adx_data_timeframe 
            ON adx_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_adx_data_trend_strength 
            ON adx_data(trend_strength)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_adx_data_updated 
            ON adx_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ ADX data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating ADX table: {e}")
        return False

if __name__ == "__main__":
    create_adx_table()
