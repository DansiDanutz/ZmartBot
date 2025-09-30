from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from src.services.daily_price_updater import get_daily_updater

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/update-all", response_model=Dict[str, Any])
async def update_all_symbols(background_tasks: BackgroundTasks):
    """Update all symbols with latest price data"""
    try:
        updater = await get_daily_updater()
        
        # Run update in background
        background_tasks.add_task(updater.run_daily_update)
        
        logger.info("🔄 Daily price update started in background")
        return {
            "message": "Daily price update started in background",
            "status": "running",
            "timestamp": "2025-08-10T12:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start daily update: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start daily update: {str(e)}")

@router.post("/update/{symbol}", response_model=Dict[str, Any])
async def update_single_symbol(symbol: str):
    """Update a single symbol with latest price data"""
    try:
        updater = await get_daily_updater()
        success = await updater.update_single_symbol(symbol)
        
        if success:
            logger.info(f"✅ Successfully updated {symbol}")
            return {
                "symbol": symbol,
                "status": "success",
                "message": f"Successfully updated price data for {symbol}"
            }
        else:
            logger.error(f"❌ Failed to update {symbol}")
            raise HTTPException(status_code=400, detail=f"Failed to update {symbol}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update {symbol}: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_update_status():
    """Get status of daily updates"""
    try:
        updater = await get_daily_updater()
        
        # Get existing files
        existing_files = updater.get_existing_files()
        
        # Get symbols from database
        symbols = await updater.get_my_symbols()
        
        # Check which symbols have files
        symbols_with_files = []
        symbols_without_files = []
        
        for symbol in symbols:
            if symbol in existing_files:
                symbols_with_files.append(symbol)
            else:
                symbols_without_files.append(symbol)
        
        return {
            "total_symbols": len(symbols),
            "symbols_with_files": symbols_with_files,
            "symbols_without_files": symbols_without_files,
            "total_with_files": len(symbols_with_files),
            "total_without_files": len(symbols_without_files),
            "last_update": "2025-08-10T12:30:00Z",  # You can implement actual last update tracking
            "next_scheduled": "2025-08-11T00:05:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get update status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get update status: {str(e)}")

@router.get("/logs", response_model=List[Dict[str, Any]])
async def get_update_logs(limit: int = 10):
    """Get recent update logs"""
    try:
        updater = await get_daily_updater()
        logs_path = updater.logs_path
        
        logs = []
        if logs_path.exists():
            # Get recent log files
            log_files = sorted(logs_path.glob("daily_update_*.log"), reverse=True)[:limit]
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                    
                    logs.append({
                        "filename": log_file.name,
                        "date": log_file.stem.replace("daily_update_", ""),
                        "content": content,
                        "size": len(content)
                    })
                except Exception as e:
                    logger.error(f"❌ Error reading log file {log_file}: {e}")
        
        return logs
        
    except Exception as e:
        logger.error(f"❌ Failed to get update logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get update logs: {str(e)}")

@router.get("/symbols", response_model=List[str])
async def get_symbols_to_update():
    """Get list of symbols that need to be updated"""
    try:
        updater = await get_daily_updater()
        symbols = await updater.get_my_symbols()
        
        logger.info(f"📊 Retrieved {len(symbols)} symbols for update")
        return symbols
        
    except Exception as e:
        logger.error(f"❌ Failed to get symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")

@router.post("/force-update", response_model=Dict[str, Any])
async def force_update_all():
    """Force update all symbols immediately (not in background)"""
    try:
        updater = await get_daily_updater()
        results = await updater.update_all_symbols()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info(f"✅ Force update complete: {success_count}/{total_count} symbols updated")
        
        return {
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "message": f"Force update complete: {success_count}/{total_count} symbols updated"
        }
        
    except Exception as e:
        logger.error(f"❌ Force update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Force update failed: {str(e)}")
