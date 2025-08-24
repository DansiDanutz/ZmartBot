#!/usr/bin/env python3
"""
Create Support/Resistance Levels Table
Adds the support_resistance_data table to the database for storing Support/Resistance Levels analysis
"""

import sqlite3
import os
from datetime import datetime

def create_support_resistance_table():
    """Create the support_resistance_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create support_resistance_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_resistance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                support_level_1 REAL NOT NULL,
                support_level_2 REAL NOT NULL,
                support_level_3 REAL NOT NULL,
                resistance_level_1 REAL NOT NULL,
                resistance_level_2 REAL NOT NULL,
                resistance_level_3 REAL NOT NULL,
                current_price REAL NOT NULL,
                price_position TEXT NOT NULL,
                nearest_support REAL NOT NULL,
                nearest_resistance REAL NOT NULL,
                support_distance REAL NOT NULL,
                resistance_distance REAL NOT NULL,
                support_strength REAL DEFAULT 0.0,
                resistance_strength REAL DEFAULT 0.0,
                breakout_potential TEXT DEFAULT 'none',
                breakout_direction TEXT DEFAULT 'neutral',
                breakout_strength REAL DEFAULT 0.0,
                volume_confirmation TEXT DEFAULT 'none',
                volume_strength REAL DEFAULT 0.0,
                trend_alignment TEXT DEFAULT 'neutral',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_resistance_data_symbol 
            ON support_resistance_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_resistance_data_timeframe 
            ON support_resistance_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_resistance_data_breakout 
            ON support_resistance_data(breakout_potential)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_resistance_data_position 
            ON support_resistance_data(price_position)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_resistance_data_updated 
            ON support_resistance_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Support/Resistance Levels data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Support/Resistance Levels table: {e}")
        return False

if __name__ == "__main__":
    create_support_resistance_table()
