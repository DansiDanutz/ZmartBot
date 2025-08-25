#!/usr/bin/env python3
"""
Automated Alert and Notification System for ZmartBot
Monitors conditions and sends alerts based on configured rules
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class AlertSystem:
    """Automated alert and notification system"""
    
    def __init__(self):
        self.session = requests.Session()
        self.alerts = []
        self.running = True
        self.init_database()
        self.load_alert_rules()
        
    def init_database(self):
        """Initialize database for alerts"""
        self.conn = sqlite3.connect('alerts.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT,
                condition TEXT,
                threshold REAL,
                symbol TEXT,
                enabled INTEGER DEFAULT 1,
                cooldown_minutes INTEGER DEFAULT 60,
                last_triggered DATETIME,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rule_id INTEGER,
                rule_name TEXT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                value REAL,
                metadata TEXT,
                FOREIGN KEY (rule_id) REFERENCES alert_rules (id)
            )
        """)
        
        self.conn.commit()
    
    def load_alert_rules(self):
        """Load or create default alert rules"""
        cursor = self.conn.cursor()
        
        default_rules = [
            # Price alerts
            {
                'name': 'btc_price_high',
                'type': 'price',
                'condition': 'above',
                'threshold': 120000,
                'symbol': 'BTCUSDT',
                'cooldown_minutes': 60
            },
            {
                'name': 'btc_price_low',
                'type': 'price',
                'condition': 'below',
                'threshold': 90000,
                'symbol': 'BTCUSDT',
                'cooldown_minutes': 60
            },
            
            # Signal alerts
            {
                'name': 'strong_buy_signal',
                'type': 'signal',
                'condition': 'above',
                'threshold': 75,
                'symbol': 'ANY',
                'cooldown_minutes': 30
            },
            {
                'name': 'strong_sell_signal',
                'type': 'signal',
                'condition': 'below',
                'threshold': 25,
                'symbol': 'ANY',
                'cooldown_minutes': 30
            },
            
            # Volatility alerts
            {
                'name': 'high_volatility',
                'type': 'volatility',
                'condition': 'above',
                'threshold': 5,  # 5% in 1 hour
                'symbol': 'ANY',
                'cooldown_minutes': 120
            },
            
            # Portfolio alerts
            {
                'name': 'portfolio_drawdown',
                'type': 'portfolio',
                'condition': 'drawdown',
                'threshold': 5,  # 5% drawdown
                'symbol': 'PORTFOLIO',
                'cooldown_minutes': 240
            },
            {
                'name': 'daily_profit_target',
                'type': 'portfolio',
                'condition': 'profit',
                'threshold': 100,  # $100 daily profit
                'symbol': 'PORTFOLIO',
                'cooldown_minutes': 1440  # Once per day
            }
        ]
        
        # Insert default rules if they don't exist
        for rule in default_rules:
            cursor.execute("""
                INSERT OR IGNORE INTO alert_rules 
                (name, type, condition, threshold, symbol, cooldown_minutes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rule['name'], rule['type'], rule['condition'],
                rule['threshold'], rule['symbol'], rule['cooldown_minutes']
            ))
        
        self.conn.commit()
        
        # Load all enabled rules
        cursor.execute("SELECT * FROM alert_rules WHERE enabled = 1")
        self.alert_rules = cursor.fetchall()
        logger.info(f"Loaded {len(self.alert_rules)} alert rules")
    
    def check_price_alert(self, rule) -> Optional[Dict]:
        """Check price-based alerts"""
        _, name, alert_type, condition, threshold, symbol, enabled, cooldown, last_triggered, metadata = rule
        
        try:
            resp = self.session.get(f"{BASE_URL}/api/real-time/price/{symbol}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                price = data.get('price', 0)
                
                triggered = False
                if condition == 'above' and price > threshold:
                    triggered = True
                    message = f"{symbol} price ${price:,.2f} is above threshold ${threshold:,.2f}"
                elif condition == 'below' and price < threshold:
                    triggered = True
                    message = f"{symbol} price ${price:,.2f} is below threshold ${threshold:,.2f}"
                
                if triggered:
                    return {
                        'rule_name': name,
                        'type': alert_type,
                        'severity': 'HIGH' if abs(price - threshold) / threshold > 0.1 else 'MEDIUM',
                        'message': message,
                        'value': price
                    }
        except Exception as e:
            logger.error(f"Error checking price alert: {e}")
        
        return None
    
    def check_signal_alert(self, rule) -> Optional[Dict]:
        """Check signal-based alerts"""
        _, name, alert_type, condition, threshold, symbol, enabled, cooldown, last_triggered, metadata = rule
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'] if symbol == 'ANY' else [symbol]
        
        for sym in symbols:
            try:
                resp = self.session.get(f"{BASE_URL}/api/signal-center/aggregation/{sym}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    score = data.get('composite_score', 50)
                    
                    triggered = False
                    if condition == 'above' and score > threshold:
                        triggered = True
                        message = f"Strong BUY signal for {sym}: Score {score}/100"
                        severity = 'HIGH'
                    elif condition == 'below' and score < threshold:
                        triggered = True
                        message = f"Strong SELL signal for {sym}: Score {score}/100"
                        severity = 'HIGH'
                    
                    if triggered:
                        return {
                            'rule_name': name,
                            'type': alert_type,
                            'severity': severity,
                            'message': message,
                            'value': score
                        }
            except Exception as e:
                logger.error(f"Error checking signal alert: {e}")
        
        return None
    
    def check_volatility_alert(self, rule) -> Optional[Dict]:
        """Check volatility-based alerts"""
        _, name, alert_type, condition, threshold, symbol, enabled, cooldown, last_triggered, metadata = rule
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'] if symbol == 'ANY' else [symbol]
        
        for sym in symbols:
            try:
                resp = self.session.get(f"{BASE_URL}/api/real-time/price/{sym}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    change_24h = abs(data.get('change_24h', 0))
                    
                    if change_24h > threshold:
                        return {
                            'rule_name': name,
                            'type': alert_type,
                            'severity': 'MEDIUM' if change_24h < threshold * 2 else 'HIGH',
                            'message': f"High volatility detected for {sym}: {change_24h:.2f}% change",
                            'value': change_24h
                        }
            except Exception as e:
                logger.error(f"Error checking volatility alert: {e}")
        
        return None
    
    def should_trigger_alert(self, rule) -> bool:
        """Check if alert should be triggered based on cooldown"""
        rule_id = rule[0]
        cooldown_minutes = rule[7]
        last_triggered = rule[8]
        
        if not last_triggered:
            return True
        
        last_time = datetime.strptime(last_triggered, '%Y-%m-%d %H:%M:%S.%f' if '.' in last_triggered else '%Y-%m-%d %H:%M:%S')
        time_diff = (datetime.now() - last_time).total_seconds() / 60
        
        return time_diff >= cooldown_minutes
    
    def trigger_alert(self, rule, alert: Dict):
        """Trigger an alert and record it"""
        rule_id = rule[0]
        
        # Record alert
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO alert_history
            (rule_id, rule_name, alert_type, severity, message, value, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rule_id, alert['rule_name'], alert['type'],
            alert['severity'], alert['message'], alert['value'],
            json.dumps(alert.get('metadata', {}))
        ))
        
        # Update last triggered time
        cursor.execute("""
            UPDATE alert_rules 
            SET last_triggered = ? 
            WHERE id = ?
        """, (datetime.now(), rule_id))
        
        self.conn.commit()
        
        # Display alert
        self.display_alert(alert)
        
        # Send notification (placeholder for email/telegram/webhook)
        self.send_notification(alert)
    
    def display_alert(self, alert: Dict):
        """Display alert in console"""
        severity_emoji = {
            'LOW': '🔵',
            'MEDIUM': '🟡',
            'HIGH': '🔴',
            'CRITICAL': '🚨'
        }
        
        emoji = severity_emoji.get(alert['severity'], '⚪')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n{emoji} ALERT [{timestamp}] {alert['severity']}")
        print(f"   {alert['message']}")
        print("-" * 60)
    
    def send_notification(self, alert: Dict):
        """Send notification via configured channels"""
        # This is a placeholder for actual notification sending
        # Could integrate with:
        # - Email (SMTP)
        # - Telegram Bot API
        # - Discord Webhook
        # - SMS (Twilio)
        # - Push notifications
        pass
    
    def monitor_alerts(self):
        """Main monitoring loop"""
        logger.info("Starting alert monitoring...")
        
        while self.running:
            try:
                for rule in self.alert_rules:
                    if not self.should_trigger_alert(rule):
                        continue
                    
                    alert_type = rule[2]
                    alert = None
                    
                    if alert_type == 'price':
                        alert = self.check_price_alert(rule)
                    elif alert_type == 'signal':
                        alert = self.check_signal_alert(rule)
                    elif alert_type == 'volatility':
                        alert = self.check_volatility_alert(rule)
                    
                    if alert:
                        self.trigger_alert(rule, alert)
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get recent alert history"""
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT timestamp, rule_name, alert_type, severity, message, value
            FROM alert_history
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        """, (since,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'timestamp': row[0],
                'rule_name': row[1],
                'type': row[2],
                'severity': row[3],
                'message': row[4],
                'value': row[5]
            })
        
        return alerts
    
    def get_alert_summary(self) -> Dict:
        """Get alert statistics summary"""
        cursor = self.conn.cursor()
        
        # Total alerts
        cursor.execute("SELECT COUNT(*) FROM alert_history")
        total_alerts = cursor.fetchone()[0]
        
        # Alerts by severity
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM alert_history 
            GROUP BY severity
        """)
        severity_counts = dict(cursor.fetchall())
        
        # Alerts in last 24h
        since_24h = datetime.now() - timedelta(hours=24)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM alert_history 
            WHERE timestamp > ?
        """, (since_24h,))
        alerts_24h = cursor.fetchone()[0]
        
        # Most frequent alerts
        cursor.execute("""
            SELECT rule_name, COUNT(*) as count
            FROM alert_history
            GROUP BY rule_name
            ORDER BY count DESC
            LIMIT 5
        """)
        top_alerts = cursor.fetchall()
        
        return {
            'total_alerts': total_alerts,
            'alerts_24h': alerts_24h,
            'severity_breakdown': severity_counts,
            'top_alerts': top_alerts
        }

def main():
    """Main function to run alert system"""
    print("\n🚨 ZmartBot Alert System")
    print("=" * 60)
    
    alert_system = AlertSystem()
    
    # Display loaded rules
    print(f"\n📋 Loaded {len(alert_system.alert_rules)} alert rules:")
    for rule in alert_system.alert_rules:
        print(f"  • {rule[1]}: {rule[2]} alert when {rule[4]} {rule[3]} {rule[5]}")
    
    # Get summary
    summary = alert_system.get_alert_summary()
    print(f"\n📊 Alert Summary:")
    print(f"  • Total Alerts: {summary['total_alerts']}")
    print(f"  • Last 24h: {summary['alerts_24h']}")
    
    if summary['severity_breakdown']:
        print(f"  • By Severity:")
        for severity, count in summary['severity_breakdown'].items():
            print(f"    - {severity}: {count}")
    
    print("\n🔄 Starting alert monitoring...")
    print("Press Ctrl+C to stop\n")
    
    try:
        alert_system.monitor_alerts()
    except KeyboardInterrupt:
        print("\n\n🛑 Alert system stopped")
        
        # Show recent alerts
        recent = alert_system.get_alert_history(1)
        if recent:
            print(f"\n📋 Recent alerts (last hour):")
            for alert in recent[:5]:
                print(f"  [{alert['timestamp']}] {alert['severity']}: {alert['message']}")
        
        print("\n✅ Alert history saved to alerts.db")

if __name__ == "__main__":
    main()