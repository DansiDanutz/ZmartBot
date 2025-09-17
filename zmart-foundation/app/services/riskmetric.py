import csv
import os
from loguru import logger
from typing import Optional, List, Dict
from functools import lru_cache


@lru_cache(maxsize=128)
def _load_risk_history(csv_path: str) -> Optional[List[Dict[str, str]]]:
    """Load and cache risk history CSV using built-in csv module."""
    try:
        if not os.path.exists(csv_path):
            logger.warning(f"Risk history CSV not found at {csv_path}")
            return None
            
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
        # Sort by timestamp descending (most recent first)
        data.sort(key=lambda x: x['timestamp'], reverse=True)
        logger.info(f"Loaded {len(data)} risk history records from {csv_path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load risk history CSV: {e}")
        return None


def risk_score(symbol: str) -> float:
    """Get latest risk score from CSV history with fallback."""
    csv_path = os.getenv("RISK_HISTORY_CSV")
    
    if not csv_path:
        logger.warning("RISK_HISTORY_CSV not configured, using fallback")
        return 0.35 if symbol.upper() == "ETH" else 0.42
    
    data = _load_risk_history(csv_path)
    if data is None:
        logger.warning("Risk history data not available, using fallback")
        return 0.35 if symbol.upper() == "ETH" else 0.42
    
    # Filter for symbol and get latest score
    symbol_data = [row for row in data if row['symbol'].upper() == symbol.upper()]
    
    if not symbol_data:
        logger.warning(f"No risk data found for {symbol}, using fallback")
        return 0.35 if symbol.upper() == "ETH" else 0.42
    
    latest_score = symbol_data[0]['risk_score']
    logger.debug(f"Risk score for {symbol}: {latest_score}")
    return float(latest_score)
