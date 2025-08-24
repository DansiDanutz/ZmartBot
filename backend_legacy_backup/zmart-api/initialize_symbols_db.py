#!/usr/bin/env python3
"""
Initialize Symbols Database with BTC Data
"""

import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / 'data' / 'symbols.db'

def create_symbols_database():
    """Create the symbols database with all necessary tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Main symbols table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                min_price REAL NOT NULL,
                max_price REAL NOT NULL,
                risk_formula TEXT NOT NULL,
                life_age_days INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Risk bands table for time spent data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_bands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                band_key TEXT NOT NULL,
                days_spent INTEGER DEFAULT 0,
                percentage REAL DEFAULT 0.0,
                coefficient REAL DEFAULT 1.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, band_key),
                FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
            )
        ''')
        
        # Coefficients table for dynamic coefficient calculation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coefficients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                risk_value REAL NOT NULL,
                coefficient REAL NOT NULL,
                calculated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, risk_value),
                FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
            )
        ''')
        
        # Price history for tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                risk_value REAL NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Symbols database created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating symbols database: {e}")

def initialize_btc():
    """Initialize BTC with correct data"""
    try:
        create_symbols_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert BTC with correct data
        cursor.execute('''
            INSERT OR REPLACE INTO symbols 
            (symbol, name, min_price, max_price, risk_formula, life_age_days, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            'BTC',
            'Bitcoin',
            30001.00,  # Your correct min price
            299720.00, # Your correct max price
            'Risk=−0.380790057100+1.718335491963×10⁻⁵⋅P−1.213364209168×10⁻¹⁰⋅P²+4.390647720677×10⁻¹⁶⋅P³−5.830886880671×10⁻²²⋅P⁴',
            5474  # From life_age.db
        ))
        
        # Insert BTC risk bands data
        btc_bands = [
            ('0.0-0.1', 134, 2.45),
            ('0.1-0.2', 721, 13.17),
            ('0.2-0.3', 840, 15.35),
            ('0.3-0.4', 1131, 20.67),
            ('0.4-0.5', 1102, 20.14),
            ('0.5-0.6', 943, 17.23),
            ('0.6-0.7', 369, 6.74),
            ('0.7-0.8', 135, 2.47),
            ('0.8-0.9', 79, 1.44),
            ('0.9-1.0', 19, 0.35)
        ]
        
        for band_key, days_spent, percentage in btc_bands:
            # Calculate coefficient based on rarity (1.0 for common, 1.6 for rare)
            if percentage < 1:
                coefficient = 1.6
            elif percentage < 2.5:
                coefficient = 1.55
            elif percentage < 5:
                coefficient = 1.5
            elif percentage < 10:
                coefficient = 1.4
            elif percentage < 15:
                coefficient = 1.3
            elif percentage < 20:
                coefficient = 1.2
            elif percentage < 30:
                coefficient = 1.1
            else:
                coefficient = 1.0
            
            cursor.execute('''
                INSERT OR REPLACE INTO risk_bands 
                (symbol, band_key, days_spent, percentage, coefficient, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', ('BTC', band_key, days_spent, percentage, coefficient))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ BTC initialized with correct data in symbols database")
        
        # Verify the data
        verify_btc_data()
        
    except Exception as e:
        logger.error(f"Error initializing BTC: {e}")

def verify_btc_data():
    """Verify BTC data was stored correctly"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check symbols table
        cursor.execute('SELECT * FROM symbols WHERE symbol = ?', ('BTC',))
        symbol_data = cursor.fetchone()
        
        if symbol_data:
            logger.info(f"✅ BTC Symbol Data: {symbol_data}")
        else:
            logger.error("❌ BTC symbol data not found")
        
        # Check risk bands
        cursor.execute('SELECT * FROM risk_bands WHERE symbol = ? ORDER BY band_key', ('BTC',))
        risk_bands = cursor.fetchall()
        
        if risk_bands:
            logger.info(f"✅ BTC Risk Bands: {len(risk_bands)} bands found")
            for band in risk_bands:
                logger.info(f"  {band[2]}: {band[3]} days, {band[4]}%, coefficient {band[5]}")
        else:
            logger.error("❌ BTC risk bands not found")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error verifying BTC data: {e}")

if __name__ == "__main__":
    logger.info("🚀 Initializing Symbols Database with BTC Data")
    initialize_btc()
    logger.info("✅ Symbols Database initialization complete!")




