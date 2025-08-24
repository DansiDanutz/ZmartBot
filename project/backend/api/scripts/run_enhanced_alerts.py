#!/usr/bin/env python3
"""
Enhanced Alerts Scheduler
Runs enhanced alerts processing for symbols at specified timeframes
"""

import asyncio
import sys
import os
import logging
import requests
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_alerts.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Default symbols to process
DEFAULT_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT',
    'XRPUSDT', 'DOTUSDT', 'LINKUSDT', 'MATICUSDT', 'AVAXUSDT'
]

# Default timeframes
DEFAULT_TIMEFRAMES = ['15m', '1h', '4h', '1d']

# API base URL
API_BASE_URL = "http://localhost:5000"

async def process_symbol_alerts(symbol: str, timeframe: str) -> Dict[str, Any]:
    """Process alerts for a single symbol/timeframe via API"""
    try:
        logger.info(f"Processing alerts for {symbol} ({timeframe})")
        
        # Call the enhanced alerts API
        response = requests.post(
            f"{API_BASE_URL}/api/enhanced-alerts/process/{symbol}",
            json={"timeframe": timeframe},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok') and result.get('data'):
                data = result['data']
                logger.info(f"✅ {symbol} ({timeframe}): {data.get('changes_detected', 0)} changes, {data.get('cross_alerts', 0)} alerts")
                return data
            else:
                logger.warning(f"⚠️ {symbol} ({timeframe}): API returned error")
                return {'status': 'error', 'message': 'API error'}
        else:
            logger.error(f"❌ {symbol} ({timeframe}): HTTP {response.status_code}")
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error processing {symbol} ({timeframe}): {e}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        logger.error(f"❌ Error processing {symbol} ({timeframe}): {e}")
        return {'status': 'error', 'message': str(e)}

async def process_all_symbols(symbols: List[str], timeframes: List[str]) -> Dict[str, Any]:
    """Process alerts for all symbols and timeframes"""
    logger.info(f"Starting enhanced alerts processing for {len(symbols)} symbols across {len(timeframes)} timeframes")
    
    start_time = datetime.now()
    results = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'symbols': {}
    }
    
    for symbol in symbols:
        results['symbols'][symbol] = {}
        
        for timeframe in timeframes:
            try:
                result = await process_symbol_alerts(symbol, timeframe)
                results['symbols'][symbol][timeframe] = result
                results['total_processed'] += 1
                
                if result.get('status') == 'success':
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to process {symbol} ({timeframe}): {e}")
                results['symbols'][symbol][timeframe] = {'status': 'error', 'message': str(e)}
                results['total_processed'] += 1
                results['failed'] += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"✅ Processing complete in {duration:.2f}s")
    logger.info(f"📊 Results: {results['successful']} successful, {results['failed']} failed")
    
    return results

async def test_api_connection() -> bool:
    """Test if the enhanced alerts API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/enhanced-alerts/stats", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Enhanced alerts API is accessible")
            return True
        else:
            logger.warning(f"⚠️ Enhanced alerts API returned HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to enhanced alerts API: {e}")
        return False

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run enhanced alerts processing')
    parser.add_argument('--symbols', nargs='+', default=DEFAULT_SYMBOLS,
                       help='Symbols to process (default: BTCUSDT ETHUSDT SOLUSDT)')
    parser.add_argument('--timeframes', nargs='+', default=DEFAULT_TIMEFRAMES,
                       help='Timeframes to process (default: 15m 1h 4h 1d)')
    parser.add_argument('--single', action='store_true',
                       help='Process only the first symbol/timeframe combination')
    parser.add_argument('--test', action='store_true',
                       help='Test API connection only')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Enhanced Alerts System")
    logger.info(f"API Base URL: {API_BASE_URL}")
    logger.info(f"Symbols: {args.symbols}")
    logger.info(f"Timeframes: {args.timeframes}")
    
    try:
        # Test API connection first
        if not await test_api_connection():
            logger.error("❌ Cannot connect to enhanced alerts API. Make sure the Flask server is running.")
            logger.info("💡 To start the server: cd project/backend/api && python app.py")
            sys.exit(1)
        
        if args.test:
            logger.info("✅ API connection test passed")
            return
        
        if args.single:
            # Process only the first symbol/timeframe
            symbol = args.symbols[0]
            timeframe = args.timeframes[0]
            result = await process_symbol_alerts(symbol, timeframe)
            logger.info(f"Single processing result: {result}")
        else:
            # Process all symbols and timeframes
            results = await process_all_symbols(args.symbols, args.timeframes)
            
            # Print summary
            print("\n" + "="*50)
            print("ENHANCED ALERTS PROCESSING SUMMARY")
            print("="*50)
            print(f"Total processed: {results['total_processed']}")
            print(f"Successful: {results['successful']}")
            print(f"Failed: {results['failed']}")
            if results['total_processed'] > 0:
                success_rate = (results['successful']/results['total_processed']*100)
                print(f"Success rate: {success_rate:.1f}%")
            print("="*50)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Processing interrupted by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
