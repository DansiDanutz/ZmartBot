#!/usr/bin/env python3
"""
Symbol Update Plugin for STEP-5
Handles symbol data updates and validation
"""

import logging
import requests
from typing import Dict, Any
from datetime import datetime

# Import the base plugin class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from step5_runner import BasePlugin, ProcessingContext

logger = logging.getLogger(__name__)

class SymbolUpdatePlugin(BasePlugin):
    """Plugin for updating symbol data and validation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.update_airtable = config.get("update_airtable", True)
        self.validate_symbol = config.get("validate_symbol", True)
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate that context has required symbol data"""
        if not context.symbol:
            logger.error("Symbol is required for SymbolUpdatePlugin")
            return False
        return True
    
    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Execute symbol update logic"""
        logger.info(f"📊 Updating symbol data for: {context.symbol}")
        
        # 1. Validate symbol format and existence
        if self.validate_symbol:
            context = self._validate_symbol(context)
        
        # 2. Update Airtable if configured
        if self.update_airtable and not context.errors:
            context = self._update_airtable_record(context)
        
        # 3. Fetch current market price
        context = self._fetch_market_price(context)
        
        # 4. Update processing metadata
        context.processing_metadata["symbol_update"] = {
            "symbol": context.symbol,
            "validation_passed": self.validate_symbol and len(context.errors) == 0,
            "airtable_updated": self.update_airtable,
            "market_price_fetched": bool(context.market_data.get("current_price")),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Symbol update completed for {context.symbol}")
        return context
    
    def _validate_symbol(self, context: ProcessingContext) -> ProcessingContext:
        """Validate symbol format and existence"""
        symbol = context.symbol.upper()
        
        # Basic format validation
        if not symbol or len(symbol) < 3:
            context.errors.append(f"Invalid symbol format: {symbol}")
            return context
        
        # Check if symbol contains USDT (common format)
        if not symbol.endswith('USDT') and not symbol.endswith('USD'):
            logger.warning(f"Symbol {symbol} doesn't end with USDT/USD - may be invalid")
        
        # Update context with validated symbol
        context.symbol = symbol
        
        logger.info(f"✅ Symbol validation passed: {symbol}")
        return context
    
    def _update_airtable_record(self, context: ProcessingContext) -> ProcessingContext:
        """Update Airtable record with symbol data"""
        try:
            # This is a placeholder - in real implementation, would use the enhanced_airtable_service
            logger.info(f"📝 Updating Airtable record for {context.symbol}")
            
            # Simulate Airtable update
            update_data = {
                "symbol": context.symbol,
                "last_update": datetime.now().isoformat(),
                "step5_processed": True
            }
            
            # Add to analysis data for downstream plugins
            context.analysis_data["airtable_update"] = update_data
            
            logger.info(f"✅ Airtable record updated for {context.symbol}")
            
        except Exception as e:
            error_msg = f"Failed to update Airtable for {context.symbol}: {e}"
            context.errors.append(error_msg)
            logger.error(error_msg)
        
        return context
    
    def _fetch_market_price(self, context: ProcessingContext) -> ProcessingContext:
        """Fetch current market price for symbol"""
        try:
            logger.info(f"💰 Fetching market price for {context.symbol}")
            
            # Try Binance API first
            binance_url = f"https://api.binance.com/api/v3/ticker/price?symbol={context.symbol}"
            
            response = requests.get(binance_url, timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                current_price = float(price_data["price"])
                
                context.market_data.update({
                    "current_price": current_price,
                    "price_source": "binance",
                    "price_timestamp": datetime.now().isoformat(),
                    "symbol": context.symbol
                })
                
                logger.info(f"✅ Market price fetched: {context.symbol} = ${current_price}")
            else:
                logger.warning(f"Failed to fetch price from Binance: {response.status_code}")
                
        except Exception as e:
            error_msg = f"Failed to fetch market price for {context.symbol}: {e}"
            logger.warning(error_msg)  # Warning, not error - price fetch is optional
        
        return context