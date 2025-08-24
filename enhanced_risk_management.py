#!/usr/bin/env python3
"""
Enhanced Risk Management for ZmartBot
Works with existing position strategy to add safety controls
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class RiskManagement:
    """Enhanced risk management for existing trading strategy"""
    
    def __init__(self):
        self.session = requests.Session()
        self.init_database()
        self.load_risk_parameters()
    
    def init_database(self):
        """Initialize risk management database"""
        self.conn = sqlite3.connect('risk_management.db')
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_parameters (
                id INTEGER PRIMARY KEY,
                max_daily_loss REAL DEFAULT 50,
                max_position_size REAL DEFAULT 100,
                max_total_exposure REAL DEFAULT 500,
                max_consecutive_losses INTEGER DEFAULT 3,
                circuit_breaker_threshold REAL DEFAULT 100,
                correlation_limit REAL DEFAULT 0.7,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                symbol TEXT,
                description TEXT,
                action_taken TEXT,
                value REAL
            )
        """)
        
        # Insert default parameters if not exists
        cursor.execute("SELECT COUNT(*) FROM risk_parameters")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO risk_parameters 
                (max_daily_loss, max_position_size, max_total_exposure, max_consecutive_losses)
                VALUES (50, 100, 500, 3)
            """)
        
        self.conn.commit()
    
    def load_risk_parameters(self):
        """Load risk parameters from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM risk_parameters WHERE id = 1")
        params = cursor.fetchone()
        
        self.risk_params = {
            'max_daily_loss': params[1],
            'max_position_size': params[2],
            'max_total_exposure': params[3],
            'max_consecutive_losses': params[4],
            'circuit_breaker_threshold': params[5],
            'correlation_limit': params[6]
        }
        
        logger.info(f"Loaded risk parameters: {self.risk_params}")
    
    def check_position_size(self, symbol: str, proposed_size: float) -> Dict:
        """Validate position size against risk limits"""
        
        # Check single position limit
        if proposed_size > self.risk_params['max_position_size']:
            self.log_risk_event(
                'POSITION_SIZE_EXCEEDED',
                symbol,
                f"Proposed size ${proposed_size} exceeds limit ${self.risk_params['max_position_size']}",
                'REJECTED'
            )
            return {
                'approved': False,
                'reason': f"Position size exceeds limit of ${self.risk_params['max_position_size']}",
                'suggested_size': self.risk_params['max_position_size']
            }
        
        # Check total exposure
        current_exposure = self.get_current_exposure()
        if current_exposure + proposed_size > self.risk_params['max_total_exposure']:
            remaining = self.risk_params['max_total_exposure'] - current_exposure
            self.log_risk_event(
                'TOTAL_EXPOSURE_EXCEEDED',
                symbol,
                f"Would exceed total exposure limit",
                'ADJUSTED'
            )
            return {
                'approved': True,
                'adjusted': True,
                'reason': f"Adjusted to stay within exposure limit",
                'suggested_size': max(0, remaining)
            }
        
        return {
            'approved': True,
            'size': proposed_size
        }
    
    def check_daily_loss(self) -> Dict:
        """Check if daily loss limit has been reached"""
        cursor = self.conn.cursor()
        
        # Get today's P&L
        today = datetime.now().date()
        
        # This would connect to your actual trading records
        # For now, we'll check the trading_strategy_state.json
        try:
            with open('trading_strategy_state.json', 'r') as f:
                state = json.load(f)
                daily_pnl = state.get('performance', {}).get('total_pnl_usd', 0)
        except:
            daily_pnl = 0
        
        if daily_pnl < -self.risk_params['max_daily_loss']:
            self.log_risk_event(
                'DAILY_LOSS_LIMIT',
                'PORTFOLIO',
                f"Daily loss ${daily_pnl} exceeds limit ${-self.risk_params['max_daily_loss']}",
                'TRADING_HALTED'
            )
            return {
                'trading_allowed': False,
                'reason': f"Daily loss limit of ${self.risk_params['max_daily_loss']} reached",
                'current_loss': daily_pnl
            }
        
        return {
            'trading_allowed': True,
            'remaining_risk': self.risk_params['max_daily_loss'] + daily_pnl
        }
    
    def check_consecutive_losses(self) -> Dict:
        """Check for consecutive losing trades"""
        # Load recent trades from your existing system
        try:
            with open('trading_strategy_state.json', 'r') as f:
                state = json.load(f)
                positions = state.get('positions', [])
        except:
            positions = []
        
        # Count recent consecutive losses
        consecutive_losses = 0
        for pos in reversed(positions[-10:]):  # Check last 10 trades
            if pos.get('status') == 'CLOSED' and pos.get('pnl_usd', 0) < 0:
                consecutive_losses += 1
            elif pos.get('status') == 'CLOSED' and pos.get('pnl_usd', 0) > 0:
                break
        
        if consecutive_losses >= self.risk_params['max_consecutive_losses']:
            self.log_risk_event(
                'CONSECUTIVE_LOSSES',
                'SYSTEM',
                f"{consecutive_losses} consecutive losses detected",
                'COOLDOWN_PERIOD'
            )
            return {
                'trading_allowed': False,
                'reason': f"Too many consecutive losses ({consecutive_losses})",
                'cooldown_minutes': 60
            }
        
        return {
            'trading_allowed': True,
            'consecutive_losses': consecutive_losses
        }
    
    def get_current_exposure(self) -> float:
        """Calculate current total exposure"""
        try:
            with open('trading_strategy_state.json', 'r') as f:
                state = json.load(f)
                positions = state.get('positions', [])
                
            exposure = 0
            for pos in positions:
                if pos.get('status') == 'OPEN':
                    exposure += pos.get('quantity', 0) * pos.get('entry_price', 0)
            
            return exposure
        except:
            return 0
    
    def calculate_position_correlation(self, symbol1: str, symbol2: str) -> float:
        """Calculate correlation between two symbols"""
        # This would use historical price data
        # For now, return estimated correlations
        crypto_correlations = {
            ('BTCUSDT', 'ETHUSDT'): 0.8,
            ('BTCUSDT', 'SOLUSDT'): 0.7,
            ('ETHUSDT', 'SOLUSDT'): 0.75,
            ('BTCUSDT', 'BNBUSDT'): 0.65,
        }
        
        pair = tuple(sorted([symbol1, symbol2]))
        return crypto_correlations.get(pair, 0.5)
    
    def check_portfolio_correlation(self, new_symbol: str) -> Dict:
        """Check if adding position increases portfolio correlation"""
        try:
            with open('trading_strategy_state.json', 'r') as f:
                state = json.load(f)
                positions = state.get('positions', [])
        except:
            positions = []
        
        open_symbols = [p['symbol'] for p in positions if p.get('status') == 'OPEN']
        
        if not open_symbols:
            return {'approved': True}
        
        # Check correlation with existing positions
        high_correlations = []
        for symbol in open_symbols:
            correlation = self.calculate_position_correlation(new_symbol, symbol)
            if correlation > self.risk_params['correlation_limit']:
                high_correlations.append((symbol, correlation))
        
        if high_correlations:
            self.log_risk_event(
                'HIGH_CORRELATION',
                new_symbol,
                f"High correlation with existing positions: {high_correlations}",
                'WARNING'
            )
            return {
                'approved': True,
                'warning': f"High correlation with {len(high_correlations)} existing positions",
                'correlations': high_correlations
            }
        
        return {'approved': True}
    
    def apply_circuit_breaker(self) -> Dict:
        """Emergency stop if losses exceed circuit breaker threshold"""
        try:
            with open('trading_strategy_state.json', 'r') as f:
                state = json.load(f)
                performance = state.get('performance', {})
                total_pnl = performance.get('total_pnl_usd', 0)
        except:
            total_pnl = 0
        
        if total_pnl < -self.risk_params['circuit_breaker_threshold']:
            self.log_risk_event(
                'CIRCUIT_BREAKER',
                'SYSTEM',
                f"Total loss ${total_pnl} triggered circuit breaker",
                'EMERGENCY_STOP'
            )
            
            # Close all positions
            self.emergency_close_all()
            
            return {
                'triggered': True,
                'reason': f"Circuit breaker triggered at ${total_pnl} loss",
                'action': 'All positions closed, trading halted'
            }
        
        return {
            'triggered': False,
            'remaining_buffer': self.risk_params['circuit_breaker_threshold'] + total_pnl
        }
    
    def emergency_close_all(self):
        """Emergency close all open positions"""
        logger.warning("EMERGENCY: Closing all positions")
        # This would send close orders to your exchange
        # For now, we'll update the state file
        
        try:
            with open('trading_strategy_state.json', 'r') as f:
                state = json.load(f)
            
            for position in state.get('positions', []):
                if position.get('status') == 'OPEN':
                    position['status'] = 'CLOSED'
                    position['exit_reason'] = 'EMERGENCY_STOP'
                    position['exit_time'] = datetime.now().isoformat()
            
            with open('trading_strategy_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error in emergency close: {e}")
    
    def log_risk_event(self, event_type: str, symbol: str, description: str, action: str, value: float = 0):
        """Log risk management events"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO risk_events (event_type, symbol, description, action_taken, value)
            VALUES (?, ?, ?, ?, ?)
        """, (event_type, symbol, description, action, value))
        self.conn.commit()
        
        logger.warning(f"RISK EVENT: {event_type} - {symbol} - {description} - Action: {action}")
    
    def get_risk_status(self) -> Dict:
        """Get comprehensive risk status"""
        daily_loss = self.check_daily_loss()
        consecutive = self.check_consecutive_losses()
        circuit = self.apply_circuit_breaker()
        exposure = self.get_current_exposure()
        
        # Calculate risk score (0-100, lower is better)
        risk_score = 0
        
        # Daily loss component (0-30)
        if not daily_loss['trading_allowed']:
            risk_score += 30
        else:
            used_pct = (self.risk_params['max_daily_loss'] - daily_loss['remaining_risk']) / self.risk_params['max_daily_loss']
            risk_score += used_pct * 20
        
        # Consecutive losses component (0-25)
        if not consecutive['trading_allowed']:
            risk_score += 25
        else:
            risk_score += (consecutive['consecutive_losses'] / self.risk_params['max_consecutive_losses']) * 15
        
        # Exposure component (0-25)
        exposure_pct = exposure / self.risk_params['max_total_exposure']
        risk_score += exposure_pct * 25
        
        # Circuit breaker component (0-20)
        if circuit['triggered']:
            risk_score += 20
        else:
            buffer_used = 1 - (circuit['remaining_buffer'] / self.risk_params['circuit_breaker_threshold'])
            risk_score += buffer_used * 10
        
        # Determine risk level
        if risk_score < 25:
            risk_level = 'LOW'
            risk_color = '🟢'
        elif risk_score < 50:
            risk_level = 'MEDIUM'
            risk_color = '🟡'
        elif risk_score < 75:
            risk_level = 'HIGH'
            risk_color = '🟠'
        else:
            risk_level = 'CRITICAL'
            risk_color = '🔴'
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'trading_allowed': daily_loss['trading_allowed'] and consecutive['trading_allowed'] and not circuit['triggered'],
            'current_exposure': exposure,
            'max_exposure': self.risk_params['max_total_exposure'],
            'daily_loss_remaining': daily_loss.get('remaining_risk', 0),
            'consecutive_losses': consecutive.get('consecutive_losses', 0),
            'circuit_breaker_active': circuit['triggered']
        }
    
    def generate_risk_report(self) -> str:
        """Generate risk management report"""
        status = self.get_risk_status()
        
        report = []
        report.append("=" * 60)
        report.append("🛡️ RISK MANAGEMENT REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        report.append(f"\n{status['risk_color']} RISK LEVEL: {status['risk_level']}")
        report.append(f"Risk Score: {status['risk_score']}/100")
        report.append(f"Trading Status: {'✅ ALLOWED' if status['trading_allowed'] else '❌ BLOCKED'}")
        
        report.append("\n📊 EXPOSURE")
        report.append(f"  Current: ${status['current_exposure']:.2f}")
        report.append(f"  Maximum: ${status['max_exposure']:.2f}")
        report.append(f"  Utilization: {(status['current_exposure']/status['max_exposure']*100):.1f}%")
        
        report.append("\n💰 DAILY LIMITS")
        report.append(f"  Loss Remaining: ${status['daily_loss_remaining']:.2f}")
        report.append(f"  Max Daily Loss: ${self.risk_params['max_daily_loss']:.2f}")
        
        report.append("\n📈 TRADING METRICS")
        report.append(f"  Consecutive Losses: {status['consecutive_losses']}")
        report.append(f"  Max Allowed: {self.risk_params['max_consecutive_losses']}")
        report.append(f"  Circuit Breaker: {'TRIGGERED' if status['circuit_breaker_active'] else 'ACTIVE'}")
        
        # Recent risk events
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, event_type, symbol, action_taken
            FROM risk_events
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        events = cursor.fetchall()
        
        if events:
            report.append("\n⚠️ RECENT RISK EVENTS")
            for event in events:
                timestamp = datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
                report.append(f"  [{timestamp}] {event[1]}: {event[3]}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

def main():
    """Test risk management system"""
    print("\n🛡️ ZmartBot Risk Management System")
    print("=" * 60)
    
    risk_mgr = RiskManagement()
    
    # Get current risk status
    status = risk_mgr.get_risk_status()
    
    print(f"\n{status['risk_color']} Current Risk Level: {status['risk_level']}")
    print(f"Risk Score: {status['risk_score']}/100")
    print(f"Trading: {'✅ Allowed' if status['trading_allowed'] else '❌ Blocked'}")
    
    # Test position size check
    print("\n📊 Testing Position Size Validation:")
    test_positions = [
        ('BTCUSDT', 50),
        ('ETHUSDT', 150),
        ('SOLUSDT', 100)
    ]
    
    for symbol, size in test_positions:
        result = risk_mgr.check_position_size(symbol, size)
        if result['approved']:
            print(f"  ✅ {symbol}: ${size} - Approved")
        else:
            print(f"  ❌ {symbol}: ${size} - {result['reason']}")
            if 'suggested_size' in result:
                print(f"     Suggested: ${result['suggested_size']}")
    
    # Check correlations
    print("\n🔗 Testing Correlation Check:")
    correlation = risk_mgr.check_portfolio_correlation('ETHUSDT')
    if 'warning' in correlation:
        print(f"  ⚠️ {correlation['warning']}")
    else:
        print(f"  ✅ No correlation issues")
    
    # Generate full report
    print("\n" + risk_mgr.generate_risk_report())
    
    print("\n✅ Risk management system active")
    print("📊 Risk events logged to risk_management.db")

if __name__ == "__main__":
    main()