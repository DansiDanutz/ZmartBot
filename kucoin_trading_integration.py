#!/usr/bin/env python3
"""
KuCoin Trading Integration for ZmartBot
Connects existing system with KuCoin futures trading
"""

import sys
import os
import json
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import requests

# Add backend to path
sys.path.insert(0, 'backend/zmart-api')
from src.services.kucoin_futures_service import kucoin_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class KuCoinTradingIntegration:
    """Integration layer for KuCoin with existing ZmartBot system"""
    
    def __init__(self):
        self.kucoin = kucoin_service
        self.session = requests.Session()
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'zmartbot_production',
            'user': 'zmartbot',
            'password': 'ZmartBot2025!Secure'
        }
        self.init_database()
        
    def init_database(self):
        """Initialize database connection"""
        try:
            self.db_conn = psycopg2.connect(**self.db_config)
            logger.info("✅ Database connected")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.db_conn = None
    
    def sync_with_existing_signals(self):
        """Sync KuCoin trading with existing signal system"""
        try:
            # Get signals from existing system
            resp = self.session.get(f"{BASE_URL}/api/signal-center/aggregation/BTCUSDT")
            if resp.status_code == 200:
                signal_data = resp.json()
                
                # Process signal for KuCoin
                if signal_data.get('composite_score', 50) > 65:
                    self.process_buy_signal('BTCUSDT', signal_data)
                elif signal_data.get('composite_score', 50) < 35:
                    self.process_sell_signal('BTCUSDT', signal_data)
                    
        except Exception as e:
            logger.error(f"Error syncing signals: {e}")
    
    def process_buy_signal(self, symbol: str, signal_data: Dict):
        """Process buy signal for KuCoin"""
        try:
            # Check risk management first
            if not self.check_risk_limits():
                logger.warning("Risk limits exceeded, skipping trade")
                return
            
            # Calculate position size based on existing strategy
            position_size = self.calculate_position_size(symbol)
            
            # Place order on KuCoin
            order = self.kucoin.place_order(
                symbol=symbol,
                side='buy',
                amount=position_size,
                order_type='market'
            )
            
            if order and 'id' in order:
                # Record in database
                self.record_trade_signal(symbol, 'BUY', signal_data, order['id'])
                logger.info(f"✅ Buy order placed: {order['id']}")
            
        except Exception as e:
            logger.error(f"Error processing buy signal: {e}")
    
    def process_sell_signal(self, symbol: str, signal_data: Dict):
        """Process sell signal for KuCoin"""
        try:
            # Check if we have an open position
            positions = self.kucoin.get_positions()
            for pos in positions:
                if pos.get('symbol') == symbol and pos.get('contracts', 0) > 0:
                    # Close position
                    success = self.kucoin.close_position(symbol)
                    if success:
                        self.record_trade_signal(symbol, 'SELL', signal_data, None)
                        logger.info(f"✅ Position closed: {symbol}")
                        
        except Exception as e:
            logger.error(f"Error processing sell signal: {e}")
    
    def calculate_position_size(self, symbol: str) -> float:
        """Calculate position size based on existing risk management"""
        try:
            # Get account balance
            balance = self.kucoin.get_balance()
            
            # Use 2% of available balance (conservative)
            if 'USDT' in balance:
                available = balance['USDT'].get('free', 0)
                position_value = available * 0.02
                
                # Get current price
                resp = self.session.get(f"{BASE_URL}/api/real-time/price/{symbol}")
                if resp.status_code == 200:
                    price = resp.json().get('price', 100000)
                    return position_value / price
            
            return 0.001  # Default minimum size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.001
    
    def check_risk_limits(self) -> bool:
        """Check if trading is allowed based on risk limits"""
        if not self.db_conn:
            return False
            
        try:
            cursor = self.db_conn.cursor()
            
            # Check daily loss limit
            cursor.execute("""
                SELECT SUM(realized_pnl) 
                FROM kucoin_positions 
                WHERE DATE(closed_at) = CURRENT_DATE
            """)
            daily_pnl = cursor.fetchone()[0] or 0
            
            if daily_pnl < -50:  # $50 daily loss limit
                logger.warning(f"Daily loss limit reached: ${daily_pnl}")
                return False
            
            # Check open positions count
            cursor.execute("""
                SELECT COUNT(*) 
                FROM kucoin_positions 
                WHERE status = 'OPEN'
            """)
            open_positions = cursor.fetchone()[0]
            
            if open_positions >= 3:  # Max 3 concurrent positions
                logger.warning(f"Max positions reached: {open_positions}")
                return False
            
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return False
    
    def record_trade_signal(self, symbol: str, action: str, signal_data: Dict, order_id: Optional[str]):
        """Record trade signal in database"""
        if not self.db_conn:
            return
            
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO trading_signals 
                (symbol, exchange, signal_type, action, strength, price, 
                 source, metadata, executed, executed_at, order_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                symbol,
                'kucoin',
                'composite',
                action,
                signal_data.get('composite_score', 0),
                signal_data.get('price', 0),
                'zmartbot_integration',
                json.dumps(signal_data),
                True if order_id else False,
                datetime.now() if order_id else None,
                order_id
            ))
            self.db_conn.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error recording signal: {e}")
    
    def monitor_positions(self):
        """Monitor open positions and apply stop loss/take profit"""
        try:
            positions = self.kucoin.get_positions()
            
            for pos in positions:
                if pos.get('contracts', 0) > 0:
                    symbol = pos['symbol']
                    entry_price = pos.get('entryPrice', 0)
                    current_price = pos.get('markPrice', 0)
                    unrealized_pnl = pos.get('unrealizedPnl', 0)
                    
                    # Calculate PnL percentage
                    if entry_price > 0:
                        pnl_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        # Check stop loss (1.5%)
                        if pnl_pct <= -1.5:
                            logger.warning(f"Stop loss triggered for {symbol}")
                            self.kucoin.close_position(symbol)
                            
                        # Check take profit (3%)
                        elif pnl_pct >= 3.0:
                            logger.info(f"Take profit triggered for {symbol}")
                            self.kucoin.close_position(symbol)
                    
                    # Update position metrics
                    self.update_position_metrics(pos)
                    
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    def update_position_metrics(self, position: Dict):
        """Update position metrics in database"""
        if not self.db_conn:
            return
            
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                UPDATE kucoin_positions 
                SET mark_price = %s, unrealized_pnl = %s, updated_at = CURRENT_TIMESTAMP
                WHERE symbol = %s AND status = 'OPEN'
            """, (
                position.get('markPrice', 0),
                position.get('unrealizedPnl', 0),
                position['symbol']
            ))
            self.db_conn.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def get_trading_performance(self) -> Dict:
        """Get trading performance metrics"""
        if not self.db_conn:
            return {}
            
        try:
            cursor = self.db_conn.cursor()
            
            # Get today's performance
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(realized_pnl) as total_pnl,
                    AVG(realized_pnl) as avg_pnl
                FROM kucoin_positions
                WHERE DATE(closed_at) = CURRENT_DATE
            """)
            
            result = cursor.fetchone()
            
            performance = {
                'date': datetime.now().date().isoformat(),
                'total_trades': result[0] or 0,
                'winning_trades': result[1] or 0,
                'losing_trades': result[2] or 0,
                'total_pnl': float(result[3] or 0),
                'avg_pnl': float(result[4] or 0),
                'win_rate': 0
            }
            
            if performance['total_trades'] > 0:
                performance['win_rate'] = (performance['winning_trades'] / performance['total_trades']) * 100
            
            cursor.close()
            return performance
            
        except Exception as e:
            logger.error(f"Error getting performance: {e}")
            return {}
    
    def generate_trading_report(self) -> str:
        """Generate comprehensive trading report"""
        report = []
        report.append("=" * 60)
        report.append("📊 KUCOIN TRADING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Account balance
        balance = self.kucoin.get_balance()
        if balance:
            report.append("\n💰 ACCOUNT BALANCE")
            for currency, info in balance.items():
                if isinstance(info, dict) and 'total' in info:
                    report.append(f"  • {currency}: {info['total']:.4f}")
        
        # Open positions
        positions = self.kucoin.get_positions()
        report.append(f"\n📈 OPEN POSITIONS ({len(positions)})")
        for pos in positions:
            if pos.get('contracts', 0) > 0:
                report.append(f"  • {pos['symbol']}: {pos['contracts']} contracts")
                report.append(f"    Entry: ${pos.get('entryPrice', 0):.2f}")
                report.append(f"    Current: ${pos.get('markPrice', 0):.2f}")
                report.append(f"    PnL: ${pos.get('unrealizedPnl', 0):.2f}")
        
        # Performance metrics
        performance = self.get_trading_performance()
        report.append("\n📊 TODAY'S PERFORMANCE")
        report.append(f"  • Total Trades: {performance.get('total_trades', 0)}")
        report.append(f"  • Win Rate: {performance.get('win_rate', 0):.1f}%")
        report.append(f"  • Total P&L: ${performance.get('total_pnl', 0):.2f}")
        report.append(f"  • Average P&L: ${performance.get('avg_pnl', 0):.2f}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

def main():
    """Main execution function"""
    print("\n🚀 KuCoin Trading Integration")
    print("=" * 60)
    
    # Initialize integration
    integration = KuCoinTradingIntegration()
    
    # Check account status
    print("\n📊 Checking KuCoin Account...")
    balance = integration.kucoin.get_balance()
    if balance:
        print("✅ KuCoin account connected")
        for currency, info in balance.items():
            if isinstance(info, dict) and 'total' in info:
                print(f"  • {currency}: {info['total']:.4f}")
    else:
        print("❌ Could not connect to KuCoin")
        print("   Please check API keys in .env file")
        return
    
    # Check positions
    print("\n📈 Current Positions:")
    positions = integration.kucoin.get_positions()
    if positions:
        for pos in positions:
            if pos.get('contracts', 0) > 0:
                print(f"  • {pos['symbol']}: {pos['contracts']} contracts @ ${pos.get('entryPrice', 0):.2f}")
    else:
        print("  • No open positions")
    
    # Sync with signals
    print("\n🔄 Syncing with existing signals...")
    integration.sync_with_existing_signals()
    
    # Monitor positions
    print("\n👁️ Monitoring positions...")
    integration.monitor_positions()
    
    # Generate report
    print("\n" + integration.generate_trading_report())
    
    print("\n✅ KuCoin integration active")
    print("📊 Trading with existing ZmartBot signals")

if __name__ == "__main__":
    main()