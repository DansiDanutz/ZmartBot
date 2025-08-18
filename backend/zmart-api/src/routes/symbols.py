#!/usr/bin/env python3
"""
Symbols API Routes - Single Source of Truth for All Symbol Data
Manages min/max prices, risk formulas, coefficients, time spent data
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/symbols", tags=["Symbols"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'symbols.db'

# Pydantic models
class SymbolData(BaseModel):
    symbol: str
    name: str
    min_price: float
    max_price: float
    risk_formula: str
    life_age_days: int
    last_updated: str

class SymbolRequest(BaseModel):
    symbol: str
    name: str
    min_price: float
    max_price: float
    risk_formula: str
    life_age_days: int

class RiskBandData(BaseModel):
    symbol: str
    band_key: str
    days_spent: int
    percentage: float
    coefficient: float
    last_updated: str

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

@router.get("/all", response_model=List[SymbolData])
async def get_all_symbols():
    """Get all symbols with their data"""
    try:
        create_symbols_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, name, min_price, max_price, risk_formula, life_age_days, last_updated
            FROM symbols ORDER BY symbol
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            SymbolData(
                symbol=row[0],
                name=row[1],
                min_price=row[2],
                max_price=row[3],
                risk_formula=row[4],
                life_age_days=row[5],
                last_updated=row[6]
            )
            for row in results
        ]
        
    except Exception as e:
        logger.error(f"Error getting all symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to get symbols")

@router.get("/{symbol}", response_model=SymbolData)
async def get_symbol(symbol: str):
    """Get specific symbol data"""
    try:
        create_symbols_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, name, min_price, max_price, risk_formula, life_age_days, last_updated
            FROM symbols WHERE symbol = ?
        ''', (symbol.upper(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return SymbolData(
                symbol=result[0],
                name=result[1],
                min_price=result[2],
                max_price=result[3],
                risk_formula=result[4],
                life_age_days=result[5],
                last_updated=result[6]
            )
        else:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get symbol")

@router.post("/{symbol}")
async def create_or_update_symbol(symbol: str, request: SymbolRequest):
    """Create or update symbol data"""
    try:
        create_symbols_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO symbols 
            (symbol, name, min_price, max_price, risk_formula, life_age_days, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            symbol.upper(),
            request.name,
            request.min_price,
            request.max_price,
            request.risk_formula,
            request.life_age_days
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Symbol {symbol} created/updated successfully")
        
        return {
            "success": True,
            "message": f"Symbol {symbol} created/updated successfully",
            "symbol": symbol.upper(),
            "data": request.dict()
        }
        
    except Exception as e:
        logger.error(f"Error creating/updating symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create/update symbol")

@router.put("/{symbol}/bounds")
async def update_symbol_bounds(
    symbol: str,
    min_price: float = Query(..., description="New min price"),
    max_price: float = Query(..., description="New max price")
):
    """Update symbol min/max prices"""
    try:
        create_symbols_database()
        
        if min_price >= max_price:
            raise HTTPException(status_code=400, detail="min_price must be less than max_price")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE symbols 
            SET min_price = ?, max_price = ?, last_updated = CURRENT_TIMESTAMP
            WHERE symbol = ?
        ''', (min_price, max_price, symbol.upper()))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Updated {symbol} bounds: min=${min_price}, max=${max_price}")
        
        return {
            "success": True,
            "message": f"Symbol {symbol} bounds updated successfully",
            "symbol": symbol.upper(),
            "min_price": min_price,
            "max_price": max_price,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bounds for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bounds")

@router.get("/{symbol}/risk-bands", response_model=List[RiskBandData])
async def get_symbol_risk_bands(symbol: str):
    """Get risk bands data for a symbol"""
    try:
        create_symbols_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Define all 10 risk bands
        all_bands = [
            '0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
            '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'
        ]
        
        # Check which bands exist for this symbol
        cursor.execute('''
            SELECT band_key FROM risk_bands 
            WHERE symbol = ?
        ''', (symbol.upper(),))
        
        existing_bands = [row[0] for row in cursor.fetchall()]
        
        # Insert missing bands with default values
        for band_key in all_bands:
            if band_key not in existing_bands:
                cursor.execute('''
                    INSERT INTO risk_bands (symbol, band_key, days_spent, percentage, coefficient, last_updated)
                    VALUES (?, ?, 0, 0.0, 1.0, CURRENT_TIMESTAMP)
                ''', (symbol.upper(), band_key))
        
        conn.commit()
        
        # Get all bands with data
        cursor.execute('''
            SELECT symbol, band_key, days_spent, percentage, coefficient, last_updated
            FROM risk_bands WHERE symbol = ? ORDER BY band_key
        ''', (symbol.upper(),))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            RiskBandData(
                symbol=row[0],
                band_key=row[1],
                days_spent=row[2],
                percentage=row[3],
                coefficient=row[4],
                last_updated=row[5]
            )
            for row in results
        ]
        
    except Exception as e:
        logger.error(f"Error getting risk bands for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk bands")

@router.put("/{symbol}/risk-bands/{band_key}")
async def update_risk_band(
    symbol: str,
    band_key: str,
    days_spent: int = Query(..., description="Days spent in this band"),
    percentage: float = Query(..., description="Percentage of total time"),
    coefficient: float = Query(..., description="Coefficient for this band")
):
    """Update risk band data"""
    try:
        create_symbols_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO risk_bands 
            (symbol, band_key, days_spent, percentage, coefficient, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (symbol.upper(), band_key, days_spent, percentage, coefficient))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Updated {symbol} band {band_key}: {days_spent} days, {percentage}%, coefficient {coefficient}")
        
        return {
            "success": True,
            "message": f"Risk band {band_key} updated for {symbol}",
            "symbol": symbol.upper(),
            "band_key": band_key,
            "days_spent": days_spent,
            "percentage": percentage,
            "coefficient": coefficient,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating risk band for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update risk band")

# Initialize with BTC data
@router.post("/initialize/btc")
async def initialize_btc():
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
        
        return {
            "success": True,
            "message": "BTC initialized successfully",
            "symbol": "BTC",
            "min_price": 30001.00,
            "max_price": 299720.00,
            "life_age_days": 5474,
            "risk_bands_count": 10
        }
        
    except Exception as e:
        logger.error(f"Error initializing BTC: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize BTC")

logger.info("✅ Symbols API routes created - Single source of truth for all symbol data")




