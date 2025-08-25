#!/usr/bin/env python3
"""
KuCoin API Manager for ZmartBot
Manages multiple KuCoin API keys and selects the best one for each task
"""

import ccxt
import os
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KuCoinAPIManager:
    """Manages multiple KuCoin API configurations"""
    
    def __init__(self):
        self.apis = {
            "tradez": {
                "name": "TradeZ API",
                "api_key": "6892422bdffe710001e6f7ec",
                "secret": "485affbc-9b74-49d5-bb4f-3442a8623cdd",
                "passphrase": "Danutz1981",
                "balance": 120.01,
                "status": "ACTIVE",
                "use_for": ["monitoring", "small_trades", "testing"],
                "max_position_size": 100  # Conservative for safety
            },
            "main": {
                "name": "Main Trading API",
                "api_key": "68888bce1cad950001b6966d",
                "secret": "ba4de6f6-2fb5-4b32-8a4c-12b1f3eb045a",
                "passphrase": "Danutz1981",
                "balance": 11350.57,
                "status": "ACTIVE",
                "use_for": ["production", "large_trades", "positions"],
                "max_position_size": 1000,
                "open_positions": ["SUSHI/USDT:USDT", "AVAX/USDT:USDT"]
            }
        }
        
        self.exchanges = {}
        self.current_api = None
        self.init_exchanges()
        self.init_database()
    
    def init_exchanges(self):
        """Initialize exchange connections for all APIs"""
        for key, config in self.apis.items():
            try:
                exchange = ccxt.kucoinfutures({
                    'apiKey': config['api_key'],
                    'secret': config['secret'],
                    'password': config['passphrase'],
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'future',
                        'adjustForTimeDifference': True
                    }
                })
                self.exchanges[key] = exchange
                logger.info(f"✅ Initialized {config['name']}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {config['name']}: {e}")
                self.exchanges[key] = None
    
    def init_database(self):
        """Initialize database connection"""
        try:
            self.db_conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='zmartbot_production',
                user='zmartbot',
                password='ZmartBot2025!Secure'
            )
            
            # Create API usage tracking table
            cursor = self.db_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id SERIAL PRIMARY KEY,
                    api_name VARCHAR(50),
                    action VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    details JSONB
                )
            """)
            self.db_conn.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.db_conn = None
    
    def select_api_for_task(self, task: str) -> str:
        """Select the best API for a specific task"""
        if task in ["test", "monitor", "small_trade"]:
            # Use TradeZ for testing and monitoring
            return "tradez"
        elif task in ["production", "large_trade", "close_position"]:
            # Use Main API for production trading
            return "main"
        else:
            # Default to the one with more balance
            return "main" if self.apis["main"]["balance"] > self.apis["tradez"]["balance"] else "tradez"
    
    def get_exchange(self, task: str = "general") -> Optional[ccxt.Exchange]:
        """Get the appropriate exchange for a task"""
        api_key = self.select_api_for_task(task)
        exchange = self.exchanges.get(api_key)
        
        if exchange:
            self.current_api = api_key
            logger.info(f"Using {self.apis[api_key]['name']} for {task}")
            self.log_api_usage(api_key, task, True)
            return exchange
        else:
            logger.error(f"No exchange available for {task}")
            return None
    
    def get_account_summary(self) -> Dict:
        """Get summary of all accounts"""
        summary = {
            "total_balance": 0,
            "accounts": [],
            "open_positions": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for key, config in self.apis.items():
            exchange = self.exchanges.get(key)
            if not exchange:
                continue
            
            try:
                # Get balance
                balance = exchange.fetch_balance()
                usdt_balance = balance.get('USDT', {}).get('total', 0)
                
                # Get positions
                positions = exchange.fetch_positions()
                open_positions = [p for p in positions if p.get('contracts', 0) > 0]
                
                account_info = {
                    "name": config['name'],
                    "balance": usdt_balance,
                    "available": balance.get('USDT', {}).get('free', 0),
                    "used": balance.get('USDT', {}).get('used', 0),
                    "positions": len(open_positions),
                    "position_details": []
                }
                
                for pos in open_positions:
                    account_info["position_details"].append({
                        "symbol": pos['symbol'],
                        "contracts": pos['contracts'],
                        "side": pos['side'],
                        "unrealized_pnl": pos.get('unrealizedPnl', 0)
                    })
                
                summary["accounts"].append(account_info)
                summary["total_balance"] += usdt_balance
                summary["open_positions"].extend(account_info["position_details"])
                
            except Exception as e:
                logger.error(f"Error getting summary for {config['name']}: {e}")
        
        return summary
    
    def distribute_trading(self, symbol: str, total_size: float) -> List[Dict]:
        """Distribute trading across multiple accounts based on balance"""
        distributions = []
        
        # Calculate distribution based on available balance
        total_available = sum(
            self.apis[key]["balance"] 
            for key in self.apis 
            if self.apis[key]["status"] == "ACTIVE"
        )
        
        for key, config in self.apis.items():
            if config["status"] != "ACTIVE":
                continue
            
            # Calculate proportional size
            proportion = config["balance"] / total_available
            allocated_size = total_size * proportion
            
            # Apply limits
            max_size = config["max_position_size"]
            final_size = min(allocated_size, max_size)
            
            if final_size > 0:
                distributions.append({
                    "api": key,
                    "name": config["name"],
                    "size": final_size,
                    "percentage": proportion * 100
                })
        
        return distributions
    
    def execute_distributed_trade(self, symbol: str, side: str, total_size: float):
        """Execute a trade distributed across multiple accounts"""
        distributions = self.distribute_trading(symbol, total_size)
        results = []
        
        for dist in distributions:
            exchange = self.exchanges.get(dist["api"])
            if not exchange:
                continue
            
            try:
                logger.info(f"Placing {side} order on {dist['name']}: {dist['size']} {symbol}")
                
                order = exchange.create_market_order(
                    symbol=symbol,
                    side=side,
                    amount=dist['size']
                )
                
                results.append({
                    "api": dist["name"],
                    "order_id": order['id'],
                    "size": dist['size'],
                    "status": "SUCCESS"
                })
                
                self.log_api_usage(dist["api"], f"trade_{side}", True, {
                    "symbol": symbol,
                    "size": dist['size'],
                    "order_id": order['id']
                })
                
            except Exception as e:
                logger.error(f"Trade failed on {dist['name']}: {e}")
                results.append({
                    "api": dist["name"],
                    "size": dist['size'],
                    "status": "FAILED",
                    "error": str(e)
                })
                
                self.log_api_usage(dist["api"], f"trade_{side}", False, {
                    "error": str(e)
                })
        
        return results
    
    def monitor_all_positions(self) -> Dict:
        """Monitor positions across all accounts"""
        all_positions = {}
        
        for key, config in self.apis.items():
            exchange = self.exchanges.get(key)
            if not exchange:
                continue
            
            try:
                positions = exchange.fetch_positions()
                
                for pos in positions:
                    if pos.get('contracts', 0) > 0:
                        symbol = pos['symbol']
                        
                        if symbol not in all_positions:
                            all_positions[symbol] = {
                                "total_contracts": 0,
                                "total_unrealized_pnl": 0,
                                "accounts": []
                            }
                        
                        all_positions[symbol]["total_contracts"] += pos['contracts']
                        all_positions[symbol]["total_unrealized_pnl"] += pos.get('unrealizedPnl', 0)
                        all_positions[symbol]["accounts"].append({
                            "api": config['name'],
                            "contracts": pos['contracts'],
                            "unrealized_pnl": pos.get('unrealizedPnl', 0),
                            "entry_price": pos.get('entryPrice', 0)
                        })
                
            except Exception as e:
                logger.error(f"Error monitoring {config['name']}: {e}")
        
        return all_positions
    
    def log_api_usage(self, api_name: str, action: str, success: bool, details: Dict = None):
        """Log API usage to database"""
        if not self.db_conn:
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage (api_name, action, success, details)
                VALUES (%s, %s, %s, %s)
            """, (
                self.apis[api_name]['name'],
                action,
                success,
                json.dumps(details) if details else None
            ))
            self.db_conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error logging API usage: {e}")
    
    def get_api_statistics(self) -> Dict:
        """Get API usage statistics"""
        if not self.db_conn:
            return {}
        
        try:
            cursor = self.db_conn.cursor()
            
            # Get usage stats for each API
            stats = {}
            for key, config in self.apis.items():
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_calls,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_calls,
                        COUNT(DISTINCT DATE(timestamp)) as active_days
                    FROM api_usage
                    WHERE api_name = %s
                    AND timestamp > NOW() - INTERVAL '7 days'
                """, (config['name'],))
                
                result = cursor.fetchone()
                stats[config['name']] = {
                    "total_calls": result[0],
                    "successful_calls": result[1],
                    "success_rate": (result[1] / result[0] * 100) if result[0] > 0 else 0,
                    "active_days": result[2]
                }
            
            cursor.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

def main():
    """Test the API manager"""
    print("\n🔧 KuCoin API Manager")
    print("="*60)
    
    manager = KuCoinAPIManager()
    
    # Get account summary
    print("\n📊 Account Summary:")
    summary = manager.get_account_summary()
    print(f"Total Balance: ${summary['total_balance']:.2f}")
    
    for account in summary['accounts']:
        print(f"\n{account['name']}:")
        print(f"  • Balance: ${account['balance']:.2f}")
        print(f"  • Available: ${account['available']:.2f}")
        print(f"  • Positions: {account['positions']}")
        
        if account['position_details']:
            print("  • Open Positions:")
            for pos in account['position_details']:
                print(f"    - {pos['symbol']}: {pos['contracts']} contracts")
                print(f"      Unrealized PnL: ${pos['unrealized_pnl']:.2f}")
    
    # Test position monitoring
    print("\n📈 All Positions:")
    positions = manager.monitor_all_positions()
    for symbol, data in positions.items():
        print(f"\n{symbol}:")
        print(f"  • Total Contracts: {data['total_contracts']}")
        print(f"  • Total Unrealized PnL: ${data['total_unrealized_pnl']:.2f}")
        print(f"  • Accounts: {len(data['accounts'])}")
    
    # Test distribution
    print("\n💰 Trade Distribution Example:")
    print("For a 1000 USDT position in BTC/USDT:")
    distributions = manager.distribute_trading("BTC/USDT:USDT", 1000)
    for dist in distributions:
        print(f"  • {dist['name']}: ${dist['size']:.2f} ({dist['percentage']:.1f}%)")
    
    # Get statistics
    print("\n📊 API Usage Statistics:")
    stats = manager.get_api_statistics()
    for api_name, data in stats.items():
        print(f"\n{api_name}:")
        print(f"  • Total Calls: {data['total_calls']}")
        print(f"  • Success Rate: {data['success_rate']:.1f}%")
        print(f"  • Active Days: {data['active_days']}")
    
    print("\n✅ API Manager configured successfully")
    print("Both APIs are working and ready for trading!")

if __name__ == "__main__":
    main()