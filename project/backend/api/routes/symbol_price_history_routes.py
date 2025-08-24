from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from src.services.symbol_price_history_manager import get_historical_data_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_symbol_price_history_status():
    """Get status of symbol price history data for all symbols"""
    try:
        manager = await get_historical_data_manager()
        status = await manager.get_data_status()
        
        logger.info(f"📊 Symbol price history status: {status['total_symbols']} symbols, {len(status['existing_data'])} with data, {len(status['missing_data'])} missing")
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get symbol price history status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbol price history status: {str(e)}")

@router.post("/sync", response_model=Dict[str, Any])
async def sync_symbol_price_history(background_tasks: BackgroundTasks):
    """Sync all missing symbol price history data"""
    try:
        manager = await get_historical_data_manager()
        
        # Run sync in background
        background_tasks.add_task(manager.auto_sync)
        
        logger.info("🔄 Symbol price history sync started in background")
        return {
            "message": "Symbol price history sync started in background",
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start symbol price history sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start symbol price history sync: {str(e)}")

@router.post("/download/{symbol}", response_model=Dict[str, Any])
async def download_symbol_price_data(symbol: str):
    """Download symbol price history data for a specific symbol"""
    try:
        manager = await get_historical_data_manager()
        success = await manager.ensure_data_for_symbol(symbol)
        
        if success:
            logger.info(f"✅ Successfully downloaded price data for {symbol}")
            return {
                "symbol": symbol,
                "status": "success",
                "message": f"Symbol price history data downloaded for {symbol}"
            }
        else:
            logger.error(f"❌ Failed to download price data for {symbol}")
            raise HTTPException(status_code=400, detail=f"Failed to download price data for {symbol}")
        
    except Exception as e:
        logger.error(f"❌ Failed to download price data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download price data for {symbol}: {str(e)}")

@router.get("/check-missing", response_model=Dict[str, Any])
async def check_missing_price_data():
    """Check which symbols are missing price history data"""
    try:
        manager = await get_historical_data_manager()
        existing, missing = await manager.check_missing_data()
        
        return {
            "existing_symbols": existing,
            "missing_symbols": missing,
            "total_existing": len(existing),
            "total_missing": len(missing)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to check missing price data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check missing price data: {str(e)}")

@router.post("/download-missing", response_model=Dict[str, Any])
async def download_missing_price_data(symbols: Optional[List[str]] = None):
    """Download missing price history data for specific symbols or all missing"""
    try:
        manager = await get_historical_data_manager()
        results = await manager.download_missing_data(symbols)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info(f"📥 Downloaded price data for {success_count}/{total_count} symbols")
        
        return {
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "message": f"Downloaded price data for {success_count}/{total_count} symbols"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to download missing price data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download missing price data: {str(e)}")

@router.get("/symbols", response_model=List[str])
async def get_my_symbols():
    """Get all symbols from My Symbols database"""
    try:
        manager = await get_historical_data_manager()
        symbols = await manager.get_my_symbols()
        
        logger.info(f"📊 Retrieved {len(symbols)} symbols from database")
        return symbols
        
    except Exception as e:
        logger.error(f"❌ Failed to get symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")
