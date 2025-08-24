#!/usr/bin/env python3
"""
Backtesting Engine for ZmartBot
Validates trading strategies using historical data
"""

import pandas as pd
import numpy as np
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

@dataclass
class Trade:
    """Trade data structure"""
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    side: str  # 'LONG' or 'SHORT'
    stop_loss: float
    take_profit: float
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    exit_reason: Optional[str] = None

class BacktestingEngine:
    """Advanced backtesting system for strategy validation"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve = []
        self.session = requests.Session()
        self.init_database()
    
    def init_database(self):
        """Initialize backtesting database"""
        self.conn = sqlite3.connect('backtesting_results.db')
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                strategy_name TEXT,
                symbol TEXT,
                timeframe TEXT,
                start_date DATE,
                end_date DATE,
                initial_capital REAL,
                final_capital REAL,
                total_return REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                avg_win REAL,
                avg_loss REAL,
                profit_factor REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                recovery_factor REAL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_id INTEGER,
                symbol TEXT,
                entry_time DATETIME,
                exit_time DATETIME,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                side TEXT,
                pnl REAL,
                pnl_percent REAL,
                exit_reason TEXT,
                FOREIGN KEY (backtest_id) REFERENCES backtest_results (id)
            )
        """)
        
        self.conn.commit()
    
    def load_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Load or generate historical price data"""
        # In production, this would load from a database or API
        # For now, we'll generate synthetic data for testing
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate synthetic OHLCV data
        dates = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        # Base price (use current price if available)
        try:
            resp = self.session.get(f"{BASE_URL}/api/real-time/price/{symbol}", timeout=5)
            if resp.status_code == 200:
                base_price = resp.json().get('price', 100000 if 'BTC' in symbol else 1000)
            else:
                base_price = 100000 if 'BTC' in symbol else 1000
        except:
            base_price = 100000 if 'BTC' in symbol else 1000
        
        # Generate price movements
        returns = np.random.normal(0.001, 0.02, len(dates))  # 0.1% mean, 2% std
        prices = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices * (1 + np.random.uniform(-0.005, 0.005, len(dates))),
            'high': prices * (1 + np.random.uniform(0, 0.01, len(dates))),
            'low': prices * (1 + np.random.uniform(-0.01, 0, len(dates))),
            'close': prices,
            'volume': np.random.uniform(100, 1000, len(dates))
        })
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df
    
    def generate_signals(self, df: pd.DataFrame, strategy: str = 'momentum') -> pd.DataFrame:
        """Generate trading signals based on strategy"""
        df['signal'] = 0  # 0: no signal, 1: buy, -1: sell
        
        if strategy == 'momentum':
            # Momentum strategy: Buy when price crosses above SMA20 with high RSI
            buy_condition = (
                (df['close'] > df['sma_20']) & 
                (df['close'].shift(1) <= df['sma_20'].shift(1)) &
                (df['rsi'] > 50) &
                (df['rsi'] < 70)
            )
            
            sell_condition = (
                (df['close'] < df['sma_20']) & 
                (df['close'].shift(1) >= df['sma_20'].shift(1)) |
                (df['rsi'] > 80) |
                (df['rsi'] < 30)
            )
            
        elif strategy == 'mean_reversion':
            # Mean reversion: Buy at lower BB, sell at upper BB
            buy_condition = (
                (df['close'] < df['bb_lower']) &
                (df['rsi'] < 30)
            )
            
            sell_condition = (
                (df['close'] > df['bb_upper']) |
                (df['rsi'] > 70)
            )
            
        elif strategy == 'macd':
            # MACD crossover strategy
            buy_condition = (
                (df['macd'] > df['signal']) & 
                (df['macd'].shift(1) <= df['signal'].shift(1))
            )
            
            sell_condition = (
                (df['macd'] < df['signal']) & 
                (df['macd'].shift(1) >= df['signal'].shift(1))
            )
        
        else:  # Combined strategy
            buy_condition = (
                (df['close'] > df['sma_20']) & 
                (df['macd'] > df['signal']) &
                (df['rsi'] > 40) &
                (df['rsi'] < 60) &
                (df['volume_ratio'] > 1.2)
            )
            
            sell_condition = (
                (df['close'] < df['sma_20']) |
                (df['macd'] < df['signal']) |
                (df['rsi'] > 75) |
                (df['rsi'] < 25)
            )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        return df
    
    def backtest_strategy(
        self,
        symbol: str,
        strategy: str = 'momentum',
        days: int = 30,
        position_size: float = 0.1,  # 10% of capital per trade
        stop_loss: float = 0.02,  # 2% stop loss
        take_profit: float = 0.05,  # 5% take profit
        max_positions: int = 3
    ) -> Dict:
        """Run backtesting simulation"""
        
        # Load and prepare data
        df = self.load_historical_data(symbol, days)
        df = self.calculate_indicators(df)
        df = self.generate_signals(df, strategy)
        
        # Initialize tracking variables
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = [self.initial_capital]
        open_positions = []
        
        # Simulate trading
        for i in range(len(df)):
            current_row = df.iloc[i]
            current_price = current_row['close']
            current_time = current_row['timestamp']
            
            # Check for exit signals on open positions
            positions_to_close = []
            for position in open_positions:
                # Check stop loss
                if position.side == 'LONG':
                    if current_price <= position.stop_loss:
                        position.exit_price = position.stop_loss
                        position.exit_reason = 'STOP_LOSS'
                        positions_to_close.append(position)
                    # Check take profit
                    elif current_price >= position.take_profit:
                        position.exit_price = position.take_profit
                        position.exit_reason = 'TAKE_PROFIT'
                        positions_to_close.append(position)
                    # Check sell signal
                    elif current_row['signal'] == -1:
                        position.exit_price = current_price
                        position.exit_reason = 'SIGNAL'
                        positions_to_close.append(position)
            
            # Close positions
            for position in positions_to_close:
                position.exit_time = current_time
                
                # Calculate P&L
                if position.side == 'LONG':
                    position.pnl = (position.exit_price - position.entry_price) * position.quantity
                    position.pnl_percent = ((position.exit_price - position.entry_price) / position.entry_price) * 100
                
                self.capital += position.pnl
                self.trades.append(position)
                open_positions.remove(position)
            
            # Check for entry signals
            if current_row['signal'] == 1 and len(open_positions) < max_positions:
                # Calculate position size
                position_value = self.capital * position_size
                quantity = position_value / current_price
                
                # Create new position
                new_position = Trade(
                    symbol=symbol,
                    entry_time=current_time,
                    exit_time=None,
                    entry_price=current_price,
                    exit_price=None,
                    quantity=quantity,
                    side='LONG',
                    stop_loss=current_price * (1 - stop_loss),
                    take_profit=current_price * (1 + take_profit)
                )
                
                open_positions.append(new_position)
                self.capital -= position_value
            
            # Track equity
            total_value = self.capital
            for pos in open_positions:
                total_value += pos.quantity * current_price
            self.equity_curve.append(total_value)
        
        # Close any remaining positions at end
        for position in open_positions:
            position.exit_time = df.iloc[-1]['timestamp']
            position.exit_price = df.iloc[-1]['close']
            position.exit_reason = 'END_OF_BACKTEST'
            
            if position.side == 'LONG':
                position.pnl = (position.exit_price - position.entry_price) * position.quantity
                position.pnl_percent = ((position.exit_price - position.entry_price) / position.entry_price) * 100
            
            self.capital += position.pnl
            self.trades.append(position)
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        metrics['strategy'] = strategy
        metrics['symbol'] = symbol
        metrics['days'] = days
        
        # Save results
        self.save_results(metrics)
        
        return metrics
    
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_return': 0,
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        # Basic metrics
        winning_trades = [t for t in self.trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl and t.pnl < 0]
        
        total_trades = len(self.trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
        
        avg_win = (total_profit / len(winning_trades)) if winning_trades else 0
        avg_loss = (total_loss / len(losing_trades)) if losing_trades else 0
        
        # Return metrics
        final_capital = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Risk metrics
        equity_array = np.array(self.equity_curve)
        returns = np.diff(equity_array) / equity_array[:-1]
        
        # Sharpe Ratio (annualized, assuming hourly data)
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(24 * 365)
        else:
            sharpe_ratio = 0
        
        # Maximum Drawdown
        cumulative = equity_array / equity_array[0]
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Recovery Factor
        recovery_factor = (total_return / max_drawdown) if max_drawdown > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'recovery_factor': recovery_factor
        }
    
    def save_results(self, metrics: Dict):
        """Save backtesting results to database"""
        cursor = self.conn.cursor()
        
        # Save main results
        cursor.execute("""
            INSERT INTO backtest_results (
                strategy_name, symbol, timeframe, start_date, end_date,
                initial_capital, final_capital, total_return, total_trades,
                winning_trades, losing_trades, win_rate, avg_win, avg_loss,
                profit_factor, sharpe_ratio, max_drawdown, recovery_factor,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.get('strategy', 'unknown'),
            metrics.get('symbol', 'unknown'),
            '1H',  # timeframe
            datetime.now() - timedelta(days=metrics.get('days', 30)),
            datetime.now(),
            metrics['initial_capital'],
            metrics['final_capital'],
            metrics['total_return'],
            metrics['total_trades'],
            metrics['winning_trades'],
            metrics['losing_trades'],
            metrics['win_rate'],
            metrics['avg_win'],
            metrics['avg_loss'],
            metrics['profit_factor'],
            metrics['sharpe_ratio'],
            metrics['max_drawdown'],
            metrics['recovery_factor'],
            json.dumps(metrics)
        ))
        
        backtest_id = cursor.lastrowid
        
        # Save individual trades
        for trade in self.trades:
            if trade.exit_time and trade.pnl is not None:
                cursor.execute("""
                    INSERT INTO backtest_trades (
                        backtest_id, symbol, entry_time, exit_time,
                        entry_price, exit_price, quantity, side,
                        pnl, pnl_percent, exit_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    backtest_id,
                    trade.symbol,
                    trade.entry_time,
                    trade.exit_time,
                    trade.entry_price,
                    trade.exit_price,
                    trade.quantity,
                    trade.side,
                    trade.pnl,
                    trade.pnl_percent,
                    trade.exit_reason
                ))
        
        self.conn.commit()
    
    def generate_report(self, metrics: Dict) -> str:
        """Generate backtesting report"""
        report = []
        report.append("=" * 60)
        report.append("📊 BACKTESTING REPORT")
        report.append("=" * 60)
        report.append(f"Strategy: {metrics.get('strategy', 'N/A')}")
        report.append(f"Symbol: {metrics.get('symbol', 'N/A')}")
        report.append(f"Period: {metrics.get('days', 0)} days")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        report.append("\n💰 CAPITAL")
        report.append(f"  Initial: ${metrics['initial_capital']:,.2f}")
        report.append(f"  Final: ${metrics['final_capital']:,.2f}")
        report.append(f"  Return: {metrics['total_return']:+.2f}%")
        
        report.append("\n📈 TRADING STATISTICS")
        report.append(f"  Total Trades: {metrics['total_trades']}")
        report.append(f"  Winning Trades: {metrics['winning_trades']}")
        report.append(f"  Losing Trades: {metrics['losing_trades']}")
        report.append(f"  Win Rate: {metrics['win_rate']:.1f}%")
        
        report.append("\n💵 PROFIT/LOSS")
        report.append(f"  Average Win: ${metrics['avg_win']:+.2f}")
        report.append(f"  Average Loss: ${metrics['avg_loss']:+.2f}")
        report.append(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        
        report.append("\n📊 RISK METRICS")
        report.append(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report.append(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        report.append(f"  Recovery Factor: {metrics['recovery_factor']:.2f}")
        
        # Performance rating
        score = 0
        if metrics['win_rate'] > 50: score += 25
        if metrics['profit_factor'] > 1.5: score += 25
        if metrics['sharpe_ratio'] > 1: score += 25
        if metrics['max_drawdown'] < 20: score += 25
        
        report.append("\n⭐ PERFORMANCE RATING")
        if score >= 75:
            report.append("  Grade: A - Excellent Strategy")
        elif score >= 50:
            report.append("  Grade: B - Good Strategy")
        elif score >= 25:
            report.append("  Grade: C - Needs Improvement")
        else:
            report.append("  Grade: D - Poor Performance")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

def main():
    """Run backtesting examples"""
    print("\n🔬 ZmartBot Backtesting Engine")
    print("=" * 60)
    
    engine = BacktestingEngine(initial_capital=10000)
    
    # Test different strategies
    strategies = ['momentum', 'mean_reversion', 'macd', 'combined']
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    
    best_result = None
    best_score = -float('inf')
    
    for symbol in symbols:
        for strategy in strategies:
            print(f"\n🔄 Testing {strategy} strategy on {symbol}...")
            
            metrics = engine.backtest_strategy(
                symbol=symbol,
                strategy=strategy,
                days=30,
                position_size=0.1,
                stop_loss=0.02,
                take_profit=0.05
            )
            
            # Display results
            report = engine.generate_report(metrics)
            print(report)
            
            # Track best result
            if metrics['total_return'] > best_score:
                best_score = metrics['total_return']
                best_result = {
                    'strategy': strategy,
                    'symbol': symbol,
                    'metrics': metrics
                }
            
            # Save report
            with open(f'backtest_{symbol}_{strategy}.txt', 'w') as f:
                f.write(report)
    
    # Display best result
    if best_result:
        print("\n" + "=" * 60)
        print("🏆 BEST PERFORMING STRATEGY")
        print("=" * 60)
        print(f"Strategy: {best_result['strategy']}")
        print(f"Symbol: {best_result['symbol']}")
        print(f"Return: {best_result['metrics']['total_return']:+.2f}%")
        print(f"Win Rate: {best_result['metrics']['win_rate']:.1f}%")
        print(f"Sharpe Ratio: {best_result['metrics']['sharpe_ratio']:.2f}")
    
    print("\n✅ Backtesting complete!")
    print("📊 Results saved to backtesting_results.db")

if __name__ == "__main__":
    main()