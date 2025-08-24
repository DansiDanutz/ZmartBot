#!/usr/bin/env python3
"""
Portfolio Analytics System for ZmartBot
Provides comprehensive portfolio analysis and performance metrics
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

BASE_URL = "http://localhost:8000"

class PortfolioAnalytics:
    """Advanced portfolio analytics and tracking"""
    
    def __init__(self):
        self.session = requests.Session()
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for portfolio tracking"""
        self.conn = sqlite3.connect('portfolio_analytics.db')
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_value REAL,
                cash_balance REAL,
                positions_value REAL,
                total_pnl REAL,
                unrealized_pnl REAL,
                realized_pnl REAL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS position_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                quantity REAL,
                entry_price REAL,
                current_price REAL,
                unrealized_pnl REAL,
                unrealized_pnl_pct REAL,
                position_value REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                price REAL,
                fee REAL,
                pnl REAL,
                trade_type TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                daily_return REAL,
                cumulative_return REAL,
                sharpe_ratio REAL,
                sortino_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                profit_factor REAL,
                trades_count INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER
            )
        """)
        
        self.conn.commit()
    
    def calculate_portfolio_value(self, positions: List[Dict], cash_balance: float = 10000) -> Dict:
        """Calculate total portfolio value"""
        positions_value = 0
        unrealized_pnl = 0
        
        for position in positions:
            symbol = position['symbol']
            quantity = position['quantity']
            entry_price = position['entry_price']
            
            # Get current price
            try:
                resp = self.session.get(f"{BASE_URL}/api/real-time/price/{symbol}", timeout=5)
                if resp.status_code == 200:
                    current_price = resp.json().get('price', entry_price)
                else:
                    current_price = entry_price
            except:
                current_price = entry_price
            
            position_value = quantity * current_price
            position_pnl = (current_price - entry_price) * quantity
            
            positions_value += position_value
            unrealized_pnl += position_pnl
            
            # Store position snapshot
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO position_snapshots 
                (symbol, quantity, entry_price, current_price, unrealized_pnl, unrealized_pnl_pct, position_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol, quantity, entry_price, current_price,
                position_pnl, (position_pnl / (entry_price * quantity) * 100 if entry_price > 0 else 0),
                position_value
            ))
        
        total_value = cash_balance + positions_value
        
        # Store portfolio snapshot
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO portfolio_history 
            (total_value, cash_balance, positions_value, unrealized_pnl)
            VALUES (?, ?, ?, ?)
        """, (total_value, cash_balance, positions_value, unrealized_pnl))
        
        self.conn.commit()
        
        return {
            'total_value': total_value,
            'cash_balance': cash_balance,
            'positions_value': positions_value,
            'unrealized_pnl': unrealized_pnl,
            'positions_count': len(positions)
        }
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        cursor = self.conn.cursor()
        
        # Get portfolio history
        cursor.execute("""
            SELECT timestamp, total_value 
            FROM portfolio_history 
            ORDER BY timestamp
        """)
        history = cursor.fetchall()
        
        if len(history) < 2:
            return {'error': 'Insufficient data for metrics'}
        
        # Convert to pandas for easier calculation
        df = pd.DataFrame(history, columns=['timestamp', 'value'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Calculate returns
        df['returns'] = df['value'].pct_change()
        df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
        
        # Calculate metrics
        total_return = df['cumulative_returns'].iloc[-1]
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        if df['returns'].std() > 0:
            sharpe_ratio = (df['returns'].mean() * 252) / (df['returns'].std() * np.sqrt(252))
        else:
            sharpe_ratio = 0
        
        # Sortino Ratio
        downside_returns = df['returns'][df['returns'] < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino_ratio = (df['returns'].mean() * 252) / (downside_returns.std() * np.sqrt(252))
        else:
            sortino_ratio = 0
        
        # Maximum Drawdown
        cumulative = (1 + df['returns']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Trade statistics
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                   SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                   AVG(CASE WHEN pnl > 0 THEN pnl ELSE NULL END) as avg_win,
                   AVG(CASE WHEN pnl < 0 THEN pnl ELSE NULL END) as avg_loss
            FROM trade_history
        """)
        trade_stats = cursor.fetchone()
        
        total_trades = trade_stats[0] or 0
        winning_trades = trade_stats[1] or 0
        losing_trades = trade_stats[2] or 0
        avg_win = trade_stats[3] or 0
        avg_loss = trade_stats[4] or 0
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Profit Factor
        if avg_loss != 0 and losing_trades > 0:
            profit_factor = abs((avg_win * winning_trades) / (avg_loss * losing_trades))
        else:
            profit_factor = 0
        
        return {
            'total_return': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown * 100,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive portfolio report"""
        metrics = self.calculate_performance_metrics()
        
        # Handle error case
        if 'error' in metrics:
            metrics = {
                'total_return': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
        
        cursor = self.conn.cursor()
        
        # Get current portfolio value
        cursor.execute("""
            SELECT total_value, cash_balance, positions_value, unrealized_pnl
            FROM portfolio_history
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        current = cursor.fetchone()
        
        # Get position details
        cursor.execute("""
            SELECT symbol, quantity, entry_price, current_price, unrealized_pnl_pct
            FROM position_snapshots
            WHERE timestamp = (SELECT MAX(timestamp) FROM position_snapshots)
        """)
        positions = cursor.fetchall()
        
        report = []
        report.append("=" * 60)
        report.append("📊 ZMARTBOT PORTFOLIO ANALYTICS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if current:
            report.append("\n📈 PORTFOLIO VALUE")
            report.append(f"  Total Value: ${current[0]:,.2f}")
            report.append(f"  Cash Balance: ${current[1]:,.2f}")
            report.append(f"  Positions Value: ${current[2]:,.2f}")
            report.append(f"  Unrealized P&L: ${current[3]:+,.2f}")
        
        report.append("\n📊 PERFORMANCE METRICS")
        report.append(f"  Total Return: {metrics['total_return']:+.2f}%")
        report.append(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report.append(f"  Sortino Ratio: {metrics['sortino_ratio']:.2f}")
        report.append(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        report.append(f"  Win Rate: {metrics['win_rate']:.1f}%")
        report.append(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        
        report.append("\n📈 TRADING STATISTICS")
        report.append(f"  Total Trades: {metrics['total_trades']}")
        report.append(f"  Winning Trades: {metrics['winning_trades']}")
        report.append(f"  Losing Trades: {metrics['losing_trades']}")
        report.append(f"  Average Win: ${metrics['avg_win']:+.2f}")
        report.append(f"  Average Loss: ${metrics['avg_loss']:+.2f}")
        
        if positions:
            report.append("\n💼 CURRENT POSITIONS")
            for pos in positions:
                symbol, qty, entry, current, pnl_pct = pos
                report.append(f"  {symbol}: {qty:.4f} @ ${entry:.2f}")
                report.append(f"    Current: ${current:.2f} | P&L: {pnl_pct:+.2f}%")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def record_trade(self, trade: Dict):
        """Record a trade in the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trade_history
            (symbol, side, quantity, price, fee, pnl, trade_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade['symbol'],
            trade['side'],
            trade['quantity'],
            trade['price'],
            trade.get('fee', 0),
            trade.get('pnl', 0),
            trade.get('trade_type', 'MANUAL'),
            json.dumps(trade.get('metadata', {}))
        ))
        self.conn.commit()

def main():
    """Test portfolio analytics"""
    print("\n🔬 ZmartBot Portfolio Analytics System")
    print("=" * 60)
    
    analytics = PortfolioAnalytics()
    
    # Test with sample positions
    sample_positions = [
        {'symbol': 'BTCUSDT', 'quantity': 0.001, 'entry_price': 100000},
        {'symbol': 'ETHUSDT', 'quantity': 0.1, 'entry_price': 3500},
        {'symbol': 'SOLUSDT', 'quantity': 1.0, 'entry_price': 250}
    ]
    
    print("\n📊 Calculating portfolio value...")
    portfolio = analytics.calculate_portfolio_value(sample_positions)
    
    print(f"\n💰 Portfolio Summary:")
    print(f"  • Total Value: ${portfolio['total_value']:,.2f}")
    print(f"  • Cash Balance: ${portfolio['cash_balance']:,.2f}")
    print(f"  • Positions Value: ${portfolio['positions_value']:,.2f}")
    print(f"  • Unrealized P&L: ${portfolio['unrealized_pnl']:+,.2f}")
    print(f"  • Active Positions: {portfolio['positions_count']}")
    
    # Record some sample trades
    print("\n📝 Recording sample trades...")
    sample_trades = [
        {'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.001, 'price': 100000, 'pnl': 0},
        {'symbol': 'ETHUSDT', 'side': 'BUY', 'quantity': 0.1, 'price': 3500, 'pnl': 0},
        {'symbol': 'SOLUSDT', 'side': 'BUY', 'quantity': 1.0, 'price': 250, 'pnl': 0}
    ]
    
    for trade in sample_trades:
        analytics.record_trade(trade)
    
    # Generate report
    print("\n📋 Generating analytics report...")
    report = analytics.generate_report()
    print(report)
    
    # Save report
    with open('portfolio_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ Report saved to portfolio_report.txt")
    print("📊 Database saved to portfolio_analytics.db")

if __name__ == "__main__":
    main()