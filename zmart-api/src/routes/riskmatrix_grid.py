#!/usr/bin/env python3
"""
RiskMatrixGrid API Routes
Serves complete risk matrix data for frontend display
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Create Router
router = APIRouter(prefix="/api/v1/riskmatrix-grid", tags=["riskmatrix-grid"])

class RiskMatrixGridAPI:
    """API for RiskMatrixGrid database operations"""
    
    def __init__(self, db_path="data/RiskMatrixGrid.db"):
        # Make path absolute
        if not os.path.isabs(db_path):
            # Get the directory of this file
            current_dir = Path(__file__).parent.parent.parent
            self.db_path = current_dir / db_path
        else:
            self.db_path = db_path

    def get_all_risk_matrix_data(self):
        """Get complete risk matrix data for frontend display"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all data ordered by risk value
            cursor.execute('''
                SELECT risk_value, btc_price, eth_price, xrp_price, bnb_price, sol_price,
                       doge_price, ada_price, link_price, avax_price, xlm_price, sui_price,
                       dot_price, ltc_price, xmr_price, aave_price, vet_price, atom_price,
                       render_price, hbar_price, xtz_price, ton_price, trx_price
                FROM risk_matrix_grid 
                ORDER BY risk_value
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to structured format for frontend
            symbols = ['BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'ADA', 'LINK', 'AVAX', 
                      'XLM', 'SUI', 'DOT', 'LTC', 'XMR', 'AAVE', 'VET', 'ATOM', 'RENDER', 
                      'HBAR', 'XTZ', 'TON', 'TRX']
            
            data = []
            for row in rows:
                risk_value = row[0]
                prices = row[1:]  # All price columns
                
                row_data = {
                    'risk_value': risk_value,
                    'risk_percentage': round(risk_value * 100, 2),
                    'prices': {}
                }
                
                # Add prices for each symbol
                for i, symbol in enumerate(symbols):
                    if i < len(prices):
                        row_data['prices'][symbol] = prices[i]
                
                data.append(row_data)
            
            return {
                'success': True,
                'data': data,
                'symbols': symbols,
                'total_rows': len(data),
                'total_symbols': len(symbols),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting risk matrix data: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def get_symbol_data(self, symbol):
        """Get risk matrix data for a specific symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get column name for symbol
            symbol_column = f"{symbol.lower()}_price"
            
            cursor.execute(f'''
                SELECT risk_value, {symbol_column}
                FROM risk_matrix_grid 
                WHERE {symbol_column} IS NOT NULL
                ORDER BY risk_value
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'risk_value': row[0],
                    'risk_percentage': round(row[0] * 100, 2),
                    'price': row[1]
                })
            
            return {
                'success': True,
                'symbol': symbol,
                'data': data,
                'total_points': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting {symbol} data: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

# Initialize API
risk_matrix_api = RiskMatrixGridAPI()

@router.get('/all')
async def get_all_risk_matrix():
    """Get complete risk matrix data"""
    try:
        result = risk_matrix_api.get_all_risk_matrix_data()
        return result
    except Exception as e:
        logger.error(f"Error in get_all_risk_matrix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/symbol/{symbol}')
async def get_symbol_risk_matrix(symbol: str):
    """Get risk matrix data for specific symbol"""
    try:
        result = risk_matrix_api.get_symbol_data(symbol.upper())
        return result
    except Exception as e:
        logger.error(f"Error in get_symbol_risk_matrix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/symbols')
async def get_available_symbols():
    """Get list of available symbols"""
    try:
        symbols = ['BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'ADA', 'LINK', 'AVAX', 
                  'XLM', 'SUI', 'DOT', 'LTC', 'XMR', 'AAVE', 'VET', 'ATOM', 'RENDER', 
                  'HBAR', 'XTZ', 'TON', 'TRX']
        
        return {
            'success': True,
            'symbols': symbols,
            'total_symbols': len(symbols)
        }
    except Exception as e:
        logger.error(f"Error in get_available_symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/stats')
async def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(risk_matrix_api.db_path)
        cursor = conn.cursor()
        
        # Get total rows
        cursor.execute('SELECT COUNT(*) FROM risk_matrix_grid')
        total_rows = cursor.fetchone()[0]
        
        # Get risk value range
        cursor.execute('SELECT MIN(risk_value), MAX(risk_value) FROM risk_matrix_grid')
        min_risk, max_risk = cursor.fetchone()
        
        conn.close()
        
        return {
            'success': True,
            'stats': {
                'total_rows': total_rows,
                'risk_range': {
                    'min': min_risk,
                    'max': max_risk
                },
                'symbols_count': 22,
                'database_path': risk_matrix_api.db_path
            }
        }
    except Exception as e:
        logger.error(f"Error in get_database_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
