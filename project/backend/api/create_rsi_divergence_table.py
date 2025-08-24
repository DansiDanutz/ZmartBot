#!/usr/bin/env python3
"""
Create RSI Divergence Table
Adds the rsi_divergence_data table to the database for storing RSI Divergence analysis
"""

import sqlite3
import os
from datetime import datetime

def create_rsi_divergence_table():
    """Create the rsi_divergence_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create rsi_divergence_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rsi_divergence_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                divergence_type TEXT NOT NULL,
                divergence_strength REAL DEFAULT 0.0,
                price_high_1 REAL NOT NULL,
                price_high_2 REAL NOT NULL,
                price_low_1 REAL NOT NULL,
                price_low_2 REAL NOT NULL,
                rsi_high_1 REAL NOT NULL,
                rsi_high_2 REAL NOT NULL,
                rsi_low_1 REAL NOT NULL,
                rsi_low_2 REAL NOT NULL,
                divergence_period INTEGER NOT NULL,
                confirmation_level TEXT DEFAULT 'pending',
                signal_strength REAL DEFAULT 0.0,
                trend_direction TEXT DEFAULT 'neutral',
                momentum_shift TEXT DEFAULT 'none',
                breakout_potential TEXT DEFAULT 'none',
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_divergence_data_symbol 
            ON rsi_divergence_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_divergence_data_timeframe 
            ON rsi_divergence_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_divergence_data_type 
            ON rsi_divergence_data(divergence_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_divergence_data_updated 
            ON rsi_divergence_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ RSI Divergence data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating RSI Divergence table: {e}")
        return False

if __name__ == "__main__":
    create_rsi_divergence_table()
