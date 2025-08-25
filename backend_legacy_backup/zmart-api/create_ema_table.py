#!/usr/bin/env python3
"""
Create EMA Table
Adds the ema_data table to the database for storing EMA crossovers
"""

import sqlite3
import os
from datetime import datetime

def create_ema_table():
    """Create the ema_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create ema_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ema_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                ema_9 REAL NOT NULL,
                ema_12 REAL NOT NULL,
                ema_20 REAL NOT NULL,
                ema_21 REAL NOT NULL,
                ema_26 REAL NOT NULL,
                ema_50 REAL NOT NULL,
                cross_signal TEXT NOT NULL,
                cross_strength REAL DEFAULT 0.0,
                golden_cross_detected BOOLEAN DEFAULT 0,
                death_cross_detected BOOLEAN DEFAULT 0,
                short_term_trend TEXT DEFAULT 'neutral',
                long_term_trend TEXT DEFAULT 'neutral',
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ema_data_symbol 
            ON ema_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ema_data_timeframe 
            ON ema_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ema_data_cross_signal 
            ON ema_data(cross_signal)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ema_data_updated 
            ON ema_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ EMA data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating EMA table: {e}")
        return False

if __name__ == "__main__":
    create_ema_table()
