#!/usr/bin/env python3
"""
Create Williams %R Table
Adds the williams_r_data table to the database for storing Williams %R indicators
"""

import sqlite3
import os
from datetime import datetime

def create_williams_r_table():
    """Create the williams_r_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create williams_r_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS williams_r_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                williams_r_value REAL NOT NULL,
                overbought_level REAL DEFAULT -20.0,
                oversold_level REAL DEFAULT -80.0,
                signal_status TEXT NOT NULL,
                signal_strength REAL DEFAULT 0.0,
                divergence_type TEXT DEFAULT 'none',
                divergence_strength REAL DEFAULT 0.0,
                momentum_trend TEXT DEFAULT 'neutral',
                momentum_strength REAL DEFAULT 0.0,
                extreme_level REAL DEFAULT 0.0,
                extreme_type TEXT DEFAULT 'none',
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_williams_r_data_symbol 
            ON williams_r_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_williams_r_data_timeframe 
            ON williams_r_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_williams_r_data_signal 
            ON williams_r_data(signal_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_williams_r_data_updated 
            ON williams_r_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Williams %R data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Williams %R table: {e}")
        return False

if __name__ == "__main__":
    create_williams_r_table()
