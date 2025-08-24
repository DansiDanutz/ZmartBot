#!/usr/bin/env python3
"""
Create Bollinger Bands Table
Adds the bollinger_bands table to the database for storing multi-timeframe Bollinger Bands data
"""

import sqlite3
import os
from datetime import datetime

def create_bollinger_bands_table():
    """Create the bollinger_bands table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create bollinger_bands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bollinger_bands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                sma REAL NOT NULL,
                upper_band REAL NOT NULL,
                lower_band REAL NOT NULL,
                bandwidth REAL NOT NULL,
                position REAL NOT NULL,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_bands_symbol 
            ON bollinger_bands(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_bands_timeframe 
            ON bollinger_bands(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_bands_updated 
            ON bollinger_bands(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Bollinger Bands table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Bollinger Bands table: {e}")
        return False

if __name__ == "__main__":
    create_bollinger_bands_table()
