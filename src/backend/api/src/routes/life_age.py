from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/life-age", tags=["Life Age"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'life_age.db'

class LifeAgeRequest(BaseModel):
    symbol: str
    age_days: int

class LifeAgeResponse(BaseModel):
    symbol: str
    age_days: int
    last_updated: str

@router.get("/all", response_model=List[LifeAgeResponse])
async def get_all_life_ages():
    """Get life ages for all symbols"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT symbol, age_days, last_updated FROM life_age ORDER BY symbol')
        results = cursor.fetchall()
        
        conn.close()
        
        return [
            LifeAgeResponse(
                symbol=row[0],
                age_days=row[1],
                last_updated=row[2]
            )
            for row in results
        ]
        
    except Exception as e:
        logger.error(f"Error getting all life ages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get life ages")

@router.get("/{symbol}", response_model=LifeAgeResponse)
async def get_life_age(symbol: str):
    """Get life age for a specific symbol"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT symbol, age_days, last_updated FROM life_age WHERE symbol = ?', (symbol,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return LifeAgeResponse(
                symbol=result[0],
                age_days=result[1],
                last_updated=result[2]
            )
        else:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting life age for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get life age")

@router.post("/{symbol}")
async def set_life_age(symbol: str, request: LifeAgeRequest):
    """Set life age for a specific symbol"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO life_age (symbol, age_days, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (symbol, request.age_days))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Set {symbol} life age to {request.age_days} days")
        
        return {"success": True, "message": f"Life age for {symbol} updated to {request.age_days} days"}
        
    except Exception as e:
        logger.error(f"Error setting life age for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to set life age")

@router.get("/status/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM life_age')
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "symbols_count": count,
            "database_path": str(DB_PATH)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
