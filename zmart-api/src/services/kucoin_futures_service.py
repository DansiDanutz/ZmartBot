#!/usr/bin/env python3
"""
KuCoin Trading Service for ZmartBot
Handles all KuCoin futures trading operations
"""

import ccxt
import os
from typing import Dict, List, Optional
import logging
import psycopg2
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KuCoinService:
    """KuCoin Futures trading service"""
    
    def __init__(self):
        self.exchange = None
        self.db_conn = None
        self.init_exchange()
        self.init_database()
    
    def init_exchange(self):
        """Initialize KuCoin exchange connection"""
        api_key = os.getenv('KUCOIN_API_KEY')
        secret = os.getenv('KUCOIN_SECRET')
        password = os.getenv('KUCOIN_PASSPHRASE')
        
        if not all([api_key, secret, password]):
            logger.warning("KuCoin API credentials not fully configured")
            self.exchange = None
            return
            
        self.exchange = ccxt.kucoinfutures({
            'apiKey': str(api_key),
            'secret': str(secret),
            'password': str(password),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
        logger.info("✅ KuCoin Futures initialized")
    
    def init_database(self):
        """Initialize database connection"""
        self.db_conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'zmartbot_production'),
            user=os.getenv('DB_USER', 'zmartbot'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def get_balance(self) -> Dict:
        """Get account balance"""
        try:
            if not self.exchange:
                logger.error("Exchange not initialized")
                return {}
                
            balance = self.exchange.fetch_balance()
            
            # Store in database
            if not self.db_conn:
                logger.error("Database connection not available")
                return balance
                
            cursor = self.db_conn.cursor()
            for currency, info in balance['info'].items():
                if isinstance(info, dict) and 'available' in info:
                    cursor.execute("""
                        INSERT INTO account_balance 
                        (exchange, currency, total, available, frozen, updated_at)
                        VALUES ('kucoin', %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (exchange, currency) 
                        DO UPDATE SET 
                            total = EXCLUDED.total,
                            available = EXCLUDED.available,
                            frozen = EXCLUDED.frozen,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        currency,
                        info.get('total', 0),
                        info.get('available', 0),
                        info.get('frozen', 0)
                    ))
            self.db_conn.commit()
            
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    def place_order(self, symbol: str, side: str, amount: float, 
                   price: Optional[float] = None, order_type: str = 'market') -> Dict:
        """Place an order on KuCoin"""
        try:
            if not self.exchange:
                logger.error("Exchange not initialized")
                return {}
                
            # Validate side parameter
            if side not in ['buy', 'sell']:
                logger.error(f"Invalid side: {side}. Must be 'buy' or 'sell'")
                return {}
                
            # Cast side to proper type for CCXT
            side_cast = 'buy' if side == 'buy' else 'sell'
                
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side_cast, amount)
            else:
                if price is None:
                    logger.error("Price required for limit orders")
                    return {}
                order = self.exchange.create_limit_order(symbol, side_cast, amount, price)
            
            # Store in database
            if not self.db_conn:
                logger.error("Database connection not available")
                return order
                
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO kucoin_orders 
                (order_id, symbol, side, type, size, price, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                order['id'],
                symbol,
                side,
                order_type,
                amount,
                price,
                order['status']
            ))
            self.db_conn.commit()
            
            logger.info(f"✅ Order placed: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        try:
            if not self.exchange:
                logger.error("Exchange not initialized")
                return []
                
            positions = self.exchange.fetch_positions()
            
            # Update database
            if not self.db_conn:
                logger.error("Database connection not available")
                return [dict(pos) for pos in positions]
                
            cursor = self.db_conn.cursor()
            for pos in positions:
                contracts = pos.get('contracts', 0)
                if contracts and float(contracts) > 0:
                    cursor.execute("""
                        INSERT INTO kucoin_positions 
                        (symbol, side, size, entry_price, mark_price, 
                         unrealized_pnl, status, opened_at)
                        VALUES (%s, %s, %s, %s, %s, %s, 'OPEN', CURRENT_TIMESTAMP)
                        ON CONFLICT (symbol, side) 
                        DO UPDATE SET 
                            size = EXCLUDED.size,
                            mark_price = EXCLUDED.mark_price,
                            unrealized_pnl = EXCLUDED.unrealized_pnl
                    """, (
                        pos['symbol'],
                        pos['side'],
                        pos['contracts'],
                        pos['entryPrice'],
                        pos['markPrice'],
                        pos['unrealizedPnl']
                    ))
            self.db_conn.commit()
            
            return [dict(pos) for pos in positions]
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """Close a position"""
        try:
            positions = self.get_positions()
            for pos in positions:
                contracts = pos.get('contracts', 0)
                if pos.get('symbol') == symbol and contracts and float(contracts) > 0:
                    side = 'sell' if pos.get('side') == 'long' else 'buy'
                    self.place_order(symbol, side, float(contracts))
                    
                    # Update database
                    if not self.db_conn:
                        logger.error("Database connection not available")
                        return True
                        
                    cursor = self.db_conn.cursor()
                    cursor.execute("""
                        UPDATE kucoin_positions 
                        SET status = 'CLOSED', closed_at = CURRENT_TIMESTAMP
                        WHERE symbol = %s AND status = 'OPEN'
                    """, (symbol,))
                    self.db_conn.commit()
                    
                    logger.info(f"✅ Position closed: {symbol}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

# Export service
kucoin_service = KuCoinService()
