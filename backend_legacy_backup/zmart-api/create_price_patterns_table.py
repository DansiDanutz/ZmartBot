#!/usr/bin/env python3
"""
Create Price Action Patterns Table
Adds the price_patterns_data table to the database for storing Price Action Patterns analysis
"""

import sqlite3
import os
from datetime import datetime

def create_price_patterns_table():
    """Create the price_patterns_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create price_patterns_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_patterns_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_name TEXT NOT NULL,
                pattern_strength REAL DEFAULT 0.0,
                pattern_reliability REAL DEFAULT 0.0,
                pattern_direction TEXT NOT NULL,
                pattern_completion REAL DEFAULT 0.0,
                breakout_level REAL,
                stop_loss_level REAL,
                take_profit_level REAL,
                risk_reward_ratio REAL DEFAULT 0.0,
                volume_confirmation TEXT DEFAULT 'none',
                volume_strength REAL DEFAULT 0.0,
                trend_alignment TEXT DEFAULT 'neutral',
                support_resistance_levels TEXT,
                pattern_duration INTEGER DEFAULT 0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_patterns_data_symbol 
            ON price_patterns_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_patterns_data_timeframe 
            ON price_patterns_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_patterns_data_pattern 
            ON price_patterns_data(pattern_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_patterns_data_direction 
            ON price_patterns_data(pattern_direction)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_patterns_data_updated 
            ON price_patterns_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Price Action Patterns data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Price Action Patterns table: {e}")
        return False

if __name__ == "__main__":
    create_price_patterns_table()
