"""
Futures Symbols Management Routes
Manages symbol lists for futures trading on KuCoin
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.services.futures_symbol_validator import get_futures_validator
from src.services.my_symbols_service_v2 import get_my_symbols_service

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/futures-symbols", tags=["futures-symbols"])

@router.get("/kucoin/available")
async def get_kucoin_futures_symbols():
    """
    Get all available futures symbols on KuCoin
    These are the ONLY symbols you can trade
    """
    try:
        validator = await get_futures_validator()
        symbols = await validator.get_tradeable_symbols()
        
        return {
            "exchange": "kucoin",
            "type": "futures",
            "total_symbols": len(symbols),
            "symbols": sorted(symbols),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching KuCoin futures symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/binance/available")
async def get_binance_futures_symbols():
    """
    Get all available futures symbols on Binance
    For reference only - we use Binance for price data, not trading
    """
    try:
        validator = await get_futures_validator()
        
        return {
            "exchange": "binance",
            "type": "futures",
            "purpose": "price_data_only",
            "total_symbols": len(validator.binance_symbols),
            "symbols": sorted(list(validator.binance_symbols.keys())),
            "note": "Binance is used for price data only. Trading is done on KuCoin.",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching Binance futures symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/common")
async def get_common_futures_symbols():
    """
    Get symbols available on BOTH KuCoin and Binance futures
    These symbols have the best price data and liquidity
    """
    try:
        validator = await get_futures_validator()
        common = await validator.get_common_futures_symbols()
        
        return {
            "description": "Symbols available on both KuCoin and Binance futures",
            "total": len(common),
            "symbols": common,
            "advantages": [
                "Best price discovery (multiple sources)",
                "Higher liquidity",
                "More reliable data",
                "Can trade on KuCoin with Binance price validation"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching common symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommended")
async def get_recommended_symbols():
    """
    Get recommended symbols for My Symbols portfolio
    High-volume perpetual futures available on KuCoin
    """
    try:
        validator = await get_futures_validator()
        recommended = await validator.get_recommended_symbols()
        
        # Get detailed info for each symbol
        symbols_info = []
        for symbol in recommended:
            info = await validator.get_symbol_info(symbol)
            if info:
                symbols_info.append({
                    "symbol": symbol,
                    "base_asset": info.base_asset,
                    "max_leverage": info.max_leverage,
                    "min_qty": info.min_qty,
                    "available_on_binance": symbol in validator.binance_symbols
                })
        
        return {
            "description": "Recommended high-volume symbols for trading",
            "total": len(recommended),
            "max_portfolio_size": 10,
            "symbols": symbols_info,
            "criteria": [
                "Available on KuCoin futures (required for trading)",
                "High trading volume",
                "Good liquidity",
                "Preferably available on Binance too (for price data)"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching recommended symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_symbols(symbols: List[str]):
    """
    Validate if symbols can be traded on KuCoin futures
    This is CRITICAL - only validated symbols can be traded
    """
    try:
        validator = await get_futures_validator()
        results = await validator.validate_symbol_list(symbols)
        
        return {
            "request": {
                "symbols": symbols,
                "count": len(symbols)
            },
            "validation": results,
            "can_proceed": results['summary']['can_trade'],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-symbols/current")
async def get_current_my_symbols():
    """
    Get current My Symbols portfolio
    Shows which symbols are being monitored for trading
    """
    try:
        my_symbols_service = get_my_symbols_service()
        portfolio = await my_symbols_service.get_portfolio()
        
        # Convert symbols from KuCoin format to standard format
        from src.utils.symbol_converter import to_standard
        symbols = [to_standard(entry.symbol) for entry in portfolio]
        
        # Validate each symbol
        validator = await get_futures_validator()
        validation = await validator.validate_symbol_list(symbols)
        
        return {
            "portfolio": {
                "symbols": symbols,
                "count": len(symbols),
                "max_allowed": 10
            },
            "validation": validation,
            "status": "OK" if validation['summary']['can_trade'] else "ERROR",
            "message": "All symbols valid for KuCoin trading" if validation['summary']['can_trade'] 
                      else f"{len(validation['invalid_symbols'])} symbols cannot be traded on KuCoin",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching My Symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/my-symbols/update")
async def update_my_symbols(symbols: List[str]):
    """
    Update My Symbols portfolio with validated symbols
    Only symbols available on KuCoin futures will be accepted
    """
    try:
        # Limit to 10 symbols
        if len(symbols) > 10:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum 10 symbols allowed, got {len(symbols)}"
            )
        
        # Allow empty portfolio (all symbols removed)
        if len(symbols) == 0:
            validation = {
                'summary': {'can_trade': True},
                'valid_symbols': [],
                'invalid_symbols': [],
                'warnings': [],
                'recommendations': []
            }
        else:
            # Validate all symbols
            validator = await get_futures_validator()
            validation = await validator.validate_symbol_list(symbols)
            
            if not validation['summary']['can_trade']:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid symbols for KuCoin trading",
                        "invalid_symbols": validation['invalid_symbols'],
                        "warnings": validation['warnings'],
                        "recommendations": validation['recommendations']
                    }
                )
        
        # Update My Symbols portfolio
        my_symbols_service = get_my_symbols_service()
        
        # Get current portfolio to determine what changed
        current_portfolio = await my_symbols_service.get_portfolio()
        current_symbols = [entry.symbol for entry in current_portfolio]
        
        # Determine what to add and what to remove
        symbols_to_add = [s for s in validation['valid_symbols'] if s not in current_symbols]
        symbols_to_remove = [s for s in current_symbols if s not in validation['valid_symbols']]
        
        # Remove symbols that are no longer wanted
        for symbol in symbols_to_remove:
            await my_symbols_service.remove_symbol_from_portfolio(symbol)
        
        # Add new symbols
        added_symbols = []
        skipped_symbols = []
        
        for i, symbol in enumerate(symbols_to_add):
            # Find next available position
            next_position = len(current_symbols) - len(symbols_to_remove) + i + 1
            success = await my_symbols_service.add_symbol_to_portfolio(symbol, next_position)
            if success:
                added_symbols.append(symbol)
            else:
                skipped_symbols.append(symbol)
        
        # Get final portfolio to return
        portfolio = await my_symbols_service.get_portfolio()
        from src.utils.symbol_converter import to_standard
        final_symbols = [to_standard(entry.symbol) for entry in portfolio]
        
        return {
            "status": "updated",
            "message": f"Portfolio updated: {len(added_symbols)} added, {len(skipped_symbols)} skipped (duplicates)",
            "symbols": final_symbols,
            "added": added_symbols,
            "skipped": skipped_symbols,
            "count": len(final_symbols),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating My Symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbol/{symbol}")
async def get_symbol_info(symbol: str):
    """
    Get detailed information about a specific futures symbol
    Shows availability on KuCoin and Binance
    """
    try:
        validator = await get_futures_validator()
        
        # Check KuCoin
        kucoin_available = await validator.is_tradeable_on_kucoin(symbol)
        
        # Get detailed info
        info = await validator.get_symbol_info(symbol)
        
        if not info and not kucoin_available:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol {symbol} not found on KuCoin or Binance futures"
            )
        
        response = {
            "symbol": symbol,
            "kucoin": {
                "available": kucoin_available,
                "can_trade": kucoin_available
            },
            "binance": {
                "available": symbol in validator.binance_symbols,
                "purpose": "price_data_only"
            }
        }
        
        if info:
            response["details"] = {
                "exchange": info.exchange,
                "base_asset": info.base_asset,
                "quote_asset": info.quote_asset,
                "contract_type": info.contract_type,
                "max_leverage": info.max_leverage,
                "min_quantity": info.min_qty,
                "max_quantity": info.max_qty,
                "tick_size": info.tick_size
            }
        
        # Add recommendation
        if kucoin_available and symbol in validator.binance_symbols:
            response["recommendation"] = "✅ Excellent - Available on both exchanges"
        elif kucoin_available:
            response["recommendation"] = "✅ Good - Can trade on KuCoin"
        else:
            response["recommendation"] = "❌ Cannot trade - Not on KuCoin futures"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching symbol info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))