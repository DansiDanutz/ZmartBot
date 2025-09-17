from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/risk-bands", tags=["Risk Bands"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'risk_bands.db'

class RiskBandData(BaseModel):
    symbol: str
    band_key: str
    days: int
    last_updated: str

class RiskBandRequest(BaseModel):
    symbol: str
    band_key: str
    days: int

class RiskBandResponse(BaseModel):
    symbol: str
    band_key: str
    days: int
    percentage: float
    last_updated: str

def create_risk_bands_table():
    """Create the risk_bands table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_bands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                band_key TEXT NOT NULL,
                days INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, band_key)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Risk bands table created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating risk bands table: {e}")

@router.get("/{symbol}", response_model=List[RiskBandResponse])
async def get_risk_bands(symbol: str):
    """Get risk bands for a specific symbol"""
    try:
        create_risk_bands_table()
        
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
        ''', (symbol,))
        
        existing_bands = [row[0] for row in cursor.fetchall()]
        
        # Insert missing bands with default values
        for band_key in all_bands:
            if band_key not in existing_bands:
                cursor.execute('''
                    INSERT INTO risk_bands (symbol, band_key, days, last_updated)
                    VALUES (?, ?, 0, CURRENT_TIMESTAMP)
                ''', (symbol, band_key))
                logger.info(f"✅ Initialized band {band_key} for {symbol}")
        
        conn.commit()
        
        # Get life age for percentage calculation
        life_age_db_path = Path(__file__).parent.parent.parent / 'data' / 'life_age.db'
        life_age_conn = sqlite3.connect(life_age_db_path)
        life_age_cursor = life_age_conn.cursor()
        
        life_age_cursor.execute('SELECT age_days FROM life_age WHERE symbol = ?', (symbol,))
        life_age_result = life_age_cursor.fetchone()
        life_age_conn.close()
        
        life_age_days = life_age_result[0] if life_age_result else 365  # Default to 365 if not found
        
        # Now get all bands
        cursor.execute('''
            SELECT symbol, band_key, days, last_updated 
            FROM risk_bands 
            WHERE symbol = ? 
            ORDER BY band_key
        ''', (symbol,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            RiskBandResponse(
                symbol=row[0],
                band_key=row[1],
                days=row[2],
                percentage=round((row[2] / life_age_days) * 100, 2) if life_age_days > 0 else 0.0,
                last_updated=row[3]
            )
            for row in results
        ]
        
    except Exception as e:
        logger.error(f"Error getting risk bands for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk bands")

@router.post("/{symbol}/{band_key}")
async def set_risk_band(symbol: str, band_key: str, request: RiskBandRequest):
    """Set risk band for a specific symbol and band"""
    try:
        create_risk_bands_table()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO risk_bands (symbol, band_key, days, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (symbol, band_key, request.days))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Set risk band {band_key} for {symbol}: {request.days} days")
        
        return {"success": True, "message": f"Risk band {band_key} updated for {symbol}"}
        
    except Exception as e:
        logger.error(f"Error setting risk band for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to set risk band")

@router.get("/{symbol}/total")
async def get_total_risk_band_days(symbol: str):
    """Get total days across all risk bands for a symbol"""
    try:
        create_risk_bands_table()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(days) as total_days
            FROM risk_bands 
            WHERE symbol = ?
        ''', (symbol,))
        
        result = cursor.fetchone()
        conn.close()
        
        total_days = result[0] if result[0] else 0
        
        return {
            "symbol": symbol,
            "total_days": total_days,
            "bands_count": 10
        }
        
    except Exception as e:
        logger.error(f"Error getting total risk band days for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get total days")
