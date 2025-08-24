#!/usr/bin/env python3
"""
Technical Indicators Alert Service
Monitors all 20+ technical indicators and generates alerts for significant events
"""

import asyncio
import logging
import sqlite3
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TechnicalAlert:
    alert_id: str
    symbol: str
    timeframe: str
    indicator: str
    condition: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    message: str
    timestamp: datetime
    trigger_price: float
    cross_type: Optional[str] = None
    cross_value: Optional[float] = None

class TechnicalIndicatorsAlertService:
    def __init__(self, db_path: str = "my_symbols_v2.db"):
        self.db_path = db_path
        self.alert_thresholds = {
            'rsi': {'oversold': 30, 'overbought': 70},
            'ema': {'cross_threshold': 0.1},
            'macd': {'signal_cross_threshold': 0.01, 'zero_cross_threshold': 0.01},
            'bollinger_bands': {'breakout_threshold': 1.0, 'squeeze_threshold': 0.1},
            'support_resistance': {'breakout_threshold': 0.5},
            'momentum': {'strong_threshold': 20.0, 'weak_threshold': 5.0},
            'volume': {'spike_threshold': 2.0, 'divergence_threshold': 0.5},
            'fibonacci': {'retracement_threshold': 0.1},
            'ichimoku': {'cloud_cross_threshold': 0.1},
            'stochastic': {'oversold': 20, 'overbought': 80},
            'williams_r': {'oversold': -80, 'overbought': -20},
            'cci': {'oversold': -100, 'overbought': 100},
            'adx': {'strong_trend': 25.0},
            'atr': {'high_volatility': 50.0},
            'parabolic_sar': {'trend_change_threshold': 0.1},
            'stoch_rsi': {'oversold': 20, 'overbought': 80},
            'price_patterns': {'pattern_strength_threshold': 50.0},
            'bollinger_squeeze': {'squeeze_threshold': 0.1},
            'macd_histogram': {'divergence_threshold': 0.1},
            'ma_convergence': {'convergence_threshold': 0.1},
            'price_channels': {'breakout_threshold': 0.1}
        }
        self._init_database()

    def _init_database(self):
        """Initialize database tables for alerts and cross events"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Technical alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS technical_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    indicator TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    trigger_price REAL NOT NULL,
                    cross_type TEXT,
                    cross_value REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Cross events tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cross_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    indicator TEXT NOT NULL,
                    cross_type TEXT NOT NULL,
                    cross_value REAL NOT NULL,
                    trigger_price REAL NOT NULL,
                    previous_value REAL,
                    current_value REAL,
                    cross_strength REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_technical_alerts_symbol ON technical_alerts(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_technical_alerts_timeframe ON technical_alerts(timeframe)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_technical_alerts_indicator ON technical_alerts(indicator)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_technical_alerts_timestamp ON technical_alerts(timestamp)')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cross_events_symbol ON cross_events(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cross_events_timeframe ON cross_events(timeframe)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cross_events_indicator ON cross_events(indicator)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cross_events_timestamp ON cross_events(timestamp)')
            
            conn.commit()

    def check_all_indicators(self) -> Dict[str, Any]:
        """Check all technical indicators for all symbols and generate alerts"""
        try:
            symbols = self._get_active_symbols()
            total_alerts = 0
            new_alerts = []
            
            for symbol in symbols:
                symbol_alerts = self._check_symbol_indicators(symbol)
                total_alerts += len(symbol_alerts)
                new_alerts.extend(symbol_alerts)
            
            if new_alerts:
                self._store_alerts(new_alerts)
                self._store_cross_events(new_alerts)
            
            return {
                "success": True,
                "total_alerts": total_alerts,
                "new_alerts": len(new_alerts),
                "symbols_checked": len(symbols)
            }
        except Exception as e:
            logger.error(f"Error checking all indicators: {e}")
            return {"success": False, "error": str(e)}

    def _get_active_symbols(self) -> List[str]:
        """Get list of active symbols from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol FROM symbols WHERE is_active = 1")
            return [row[0] for row in cursor.fetchall()]

    def _check_symbol_indicators(self, symbol: str) -> List[TechnicalAlert]:
        """Check all indicators for a specific symbol"""
        alerts = []
        
        # Check each indicator type
        alerts.extend(self._check_rsi_alerts(symbol))
        alerts.extend(self._check_ema_alerts(symbol))
        alerts.extend(self._check_macd_alerts(symbol))
        alerts.extend(self._check_bollinger_alerts(symbol))
        alerts.extend(self._check_support_resistance_alerts(symbol))
        alerts.extend(self._check_momentum_alerts(symbol))
        alerts.extend(self._check_volume_alerts(symbol))
        alerts.extend(self._check_other_indicators(symbol))
        
        return alerts

    def _check_rsi_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check RSI for alert conditions"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, rsi_value, signal_status, current_price, last_updated
                FROM rsi_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, rsi_value, signal_status, current_price, last_updated = row
                
                # Check oversold condition
                if rsi_value <= self.alert_thresholds['rsi']['oversold']:
                    alert = TechnicalAlert(
                        alert_id=f"rsi_oversold_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="RSI",
                        condition="oversold",
                        current_value=rsi_value,
                        threshold=self.alert_thresholds['rsi']['oversold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📉 {symbol} {timeframe} RSI OVERSOLD: {rsi_value:.2f} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="oversold",
                        cross_value=rsi_value
                    )
                    alerts.append(alert)
                
                # Check overbought condition
                elif rsi_value >= self.alert_thresholds['rsi']['overbought']:
                    alert = TechnicalAlert(
                        alert_id=f"rsi_overbought_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="RSI",
                        condition="overbought",
                        current_value=rsi_value,
                        threshold=self.alert_thresholds['rsi']['overbought'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📈 {symbol} {timeframe} RSI OVERBOUGHT: {rsi_value:.2f} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="overbought",
                        cross_value=rsi_value
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_ema_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check EMA for cross events"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, ema_9, ema_21, ema_50, ema_signal, current_price, last_updated
                FROM ema_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, ema_9, ema_21, ema_50, ema_signal, current_price, last_updated = row
                
                # Check for EMA crossovers
                if ema_signal and ema_signal != "none":
                    cross_type = "golden_cross" if "bullish" in ema_signal.lower() else "death_cross"
                    alert = TechnicalAlert(
                        alert_id=f"ema_{cross_type}_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="EMA",
                        condition=cross_type,
                        current_value=ema_9,
                        threshold=self.alert_thresholds['ema']['cross_threshold'],
                        severity=AlertSeverity.HIGH,
                        message=f"📊 {symbol} {timeframe} EMA {cross_type.upper()}: {ema_signal} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type=cross_type,
                        cross_value=current_price
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_macd_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check MACD for cross events"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, macd_line, signal_line, histogram, zero_line_cross, signal_cross, current_price, last_updated
                FROM macd_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, macd_line, signal_line, histogram, zero_line_cross, signal_cross, current_price, last_updated = row
                
                # Check signal line cross
                if signal_cross and signal_cross != "none":
                    cross_type = "signal_bullish" if "bullish" in signal_cross.lower() else "signal_bearish"
                    alert = TechnicalAlert(
                        alert_id=f"macd_signal_cross_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="MACD",
                        condition=cross_type,
                        current_value=1.0,
                        threshold=self.alert_thresholds['macd']['signal_cross_threshold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📊 {symbol} {timeframe} MACD SIGNAL CROSS: {signal_cross.upper()} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type=cross_type,
                        cross_value=current_price
                    )
                    alerts.append(alert)
                
                # Check zero line cross
                if zero_line_cross and zero_line_cross != "none":
                    cross_type = "zero_line_bullish" if "bullish" in zero_line_cross.lower() else "zero_line_bearish"
                    alert = TechnicalAlert(
                        alert_id=f"macd_zero_cross_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="MACD",
                        condition=cross_type,
                        current_value=1.0,
                        threshold=self.alert_thresholds['macd']['zero_cross_threshold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📊 {symbol} {timeframe} MACD ZERO LINE CROSS: {zero_line_cross.upper()} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type=cross_type,
                        cross_value=current_price
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_bollinger_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check Bollinger Bands for breakouts and squeezes"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, upper_band, middle_band, lower_band, bandwidth, current_price, last_updated
                FROM bollinger_bands 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, upper_band, middle_band, lower_band, bandwidth, current_price, last_updated = row
                
                # Check for breakouts
                if current_price > upper_band:
                    alert = TechnicalAlert(
                        alert_id=f"bb_breakout_bullish_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Bollinger Bands",
                        condition="breakout_bullish",
                        current_value=1.0,
                        threshold=self.alert_thresholds['bollinger_bands']['breakout_threshold'],
                        severity=AlertSeverity.HIGH,
                        message=f"💥 {symbol} {timeframe} BOLLINGER BANDS BULLISH BREAKOUT! (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="bullish_breakout",
                        cross_value=current_price
                    )
                    alerts.append(alert)
                
                elif current_price < lower_band:
                    alert = TechnicalAlert(
                        alert_id=f"bb_breakout_bearish_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Bollinger Bands",
                        condition="breakout_bearish",
                        current_value=1.0,
                        threshold=self.alert_thresholds['bollinger_bands']['breakout_threshold'],
                        severity=AlertSeverity.HIGH,
                        message=f"💥 {symbol} {timeframe} BOLLINGER BANDS BEARISH BREAKOUT! (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="bearish_breakout",
                        cross_value=current_price
                    )
                    alerts.append(alert)
                
                # Check for squeeze
                if bandwidth < self.alert_thresholds['bollinger_bands']['squeeze_threshold']:
                    alert = TechnicalAlert(
                        alert_id=f"bb_squeeze_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Bollinger Bands",
                        condition="squeeze",
                        current_value=1.0,
                        threshold=self.alert_thresholds['bollinger_bands']['squeeze_threshold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📊 {symbol} {timeframe} BOLLINGER BANDS SQUEEZE DETECTED! (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="squeeze",
                        cross_value=bandwidth
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_support_resistance_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check Support/Resistance for breakouts"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, nearest_support, nearest_resistance, price_position, breakout_potential, current_price, last_updated
                FROM support_resistance_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, nearest_support, nearest_resistance, price_position, breakout_potential, current_price, last_updated = row
                
                # Check for support/resistance breaks
                if "breakout" in breakout_potential.lower():
                    alert = TechnicalAlert(
                        alert_id=f"sr_breakout_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Support/Resistance",
                        condition=breakout_potential,
                        current_value=1.0,
                        threshold=self.alert_thresholds['support_resistance']['breakout_threshold'],
                        severity=AlertSeverity.HIGH,
                        message=f"💥 {symbol} {timeframe} SUPPORT/RESISTANCE {breakout_potential.upper()}! (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type=breakout_potential,
                        cross_value=current_price
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_momentum_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check Momentum indicators"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, momentum_status, momentum_strength, current_price, last_updated
                FROM momentum_indicators_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, momentum_status, momentum_strength, current_price, last_updated = row
                
                # Check for strong momentum
                if momentum_strength >= self.alert_thresholds['momentum']['strong_threshold']:
                    alert = TechnicalAlert(
                        alert_id=f"momentum_{momentum_status}_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Momentum",
                        condition=f"strong_{momentum_status}",
                        current_value=momentum_strength,
                        threshold=self.alert_thresholds['momentum']['strong_threshold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📉 {symbol} {timeframe} STRONG {momentum_status.upper()} MOMENTUM: {momentum_strength:.2f} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type=f"strong_{momentum_status}",
                        cross_value=momentum_strength
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_volume_alerts(self, symbol: str) -> List[TechnicalAlert]:
        """Check Volume for spikes and divergences"""
        alerts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, volume_spike_ratio, volume_divergence_type, current_price, last_updated
                FROM volume_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, volume_spike_ratio, volume_divergence_type, current_price, last_updated = row
                
                # Check for volume spikes
                if volume_spike_ratio >= self.alert_thresholds['volume']['spike_threshold']:
                    alert = TechnicalAlert(
                        alert_id=f"volume_spike_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Volume",
                        condition="volume_spike",
                        current_value=volume_spike_ratio,
                        threshold=self.alert_thresholds['volume']['spike_threshold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📊 {symbol} {timeframe} VOLUME SPIKE: {volume_spike_ratio:.2f}x (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="volume_spike",
                        cross_value=volume_spike_ratio
                    )
                    alerts.append(alert)
        
        return alerts

    def _check_other_indicators(self, symbol: str) -> List[TechnicalAlert]:
        """Check other technical indicators"""
        alerts = []
        
        # Check Williams %R
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timeframe, williams_r_value, signal_status, current_price, last_updated
                FROM williams_r_data 
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, williams_r_value, signal_status, current_price, last_updated = row
                
                if williams_r_value <= self.alert_thresholds['williams_r']['oversold']:
                    alert = TechnicalAlert(
                        alert_id=f"williams_oversold_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Williams %R",
                        condition="oversold",
                        current_value=williams_r_value,
                        threshold=self.alert_thresholds['williams_r']['oversold'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📉 {symbol} {timeframe} WILLIAMS %R OVERSOLD: {williams_r_value:.2f} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="oversold",
                        cross_value=williams_r_value
                    )
                    alerts.append(alert)
                
                elif williams_r_value >= self.alert_thresholds['williams_r']['overbought']:
                    alert = TechnicalAlert(
                        alert_id=f"williams_overbought_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator="Williams %R",
                        condition="overbought",
                        current_value=williams_r_value,
                        threshold=self.alert_thresholds['williams_r']['overbought'],
                        severity=AlertSeverity.MEDIUM,
                        message=f"📈 {symbol} {timeframe} WILLIAMS %R OVERBOUGHT: {williams_r_value:.2f} (Price: ${current_price:,.2f})",
                        timestamp=datetime.now(timezone.utc),
                        trigger_price=current_price,
                        cross_type="overbought",
                        cross_value=williams_r_value
                    )
                    alerts.append(alert)
        
        # Check CCI
        cursor.execute("""
            SELECT timeframe, cci_value, signal_status, current_price, last_updated
            FROM cci_data 
            WHERE symbol = ?
        """, (symbol,))
        
        for row in cursor.fetchall():
            timeframe, cci_value, signal_status, current_price, last_updated = row
            
            if cci_value <= self.alert_thresholds['cci']['oversold']:
                alert = TechnicalAlert(
                    alert_id=f"cci_oversold_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                    symbol=symbol,
                    timeframe=timeframe,
                    indicator="CCI",
                    condition="oversold",
                    current_value=cci_value,
                    threshold=self.alert_thresholds['cci']['oversold'],
                    severity=AlertSeverity.MEDIUM,
                    message=f"📉 {symbol} {timeframe} CCI OVERSOLD: {cci_value:.2f} (Price: ${current_price:,.2f})",
                    timestamp=datetime.now(timezone.utc),
                    trigger_price=current_price,
                    cross_type="oversold",
                    cross_value=cci_value
                )
                alerts.append(alert)
            
            elif cci_value >= self.alert_thresholds['cci']['overbought']:
                alert = TechnicalAlert(
                    alert_id=f"cci_overbought_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                    symbol=symbol,
                    timeframe=timeframe,
                    indicator="CCI",
                    condition="overbought",
                    current_value=cci_value,
                    threshold=self.alert_thresholds['cci']['overbought'],
                    severity=AlertSeverity.MEDIUM,
                    message=f"📈 {symbol} {timeframe} CCI OVERBOUGHT: {cci_value:.2f} (Price: ${current_price:,.2f})",
                    timestamp=datetime.now(timezone.utc),
                    trigger_price=current_price,
                    cross_type="overbought",
                    cross_value=cci_value
                )
                alerts.append(alert)
        
        # Check ADX
        cursor.execute("""
            SELECT timeframe, adx_value, trend_strength, current_price, last_updated
            FROM adx_data 
            WHERE symbol = ?
        """, (symbol,))
        
        for row in cursor.fetchall():
            timeframe, adx_value, trend_strength, current_price, last_updated = row
            
            if adx_value >= self.alert_thresholds['adx']['strong_trend']:
                alert = TechnicalAlert(
                    alert_id=f"adx_strong_{symbol}_{timeframe}_{datetime.now().timestamp()}",
                    symbol=symbol,
                    timeframe=timeframe,
                    indicator="ADX",
                    condition="strong_trend",
                    current_value=adx_value,
                    threshold=self.alert_thresholds['adx']['strong_trend'],
                    severity=AlertSeverity.MEDIUM,
                    message=f"📊 {symbol} {timeframe} STRONG TREND: ADX={adx_value:.2f} (Price: ${current_price:,.2f})",
                    timestamp=datetime.now(timezone.utc),
                    trigger_price=current_price,
                    cross_type="strong_trend",
                    cross_value=adx_value
                )
                alerts.append(alert)
        
        return alerts

    def _store_alerts(self, alerts: List[TechnicalAlert]):
        """Store alerts in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for alert in alerts:
                cursor.execute("""
                    INSERT OR REPLACE INTO technical_alerts 
                    (alert_id, symbol, timeframe, indicator, condition, current_value, threshold, 
                     severity, message, trigger_price, cross_type, cross_value, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id, alert.symbol, alert.timeframe, alert.indicator, alert.condition,
                    alert.current_value, alert.threshold, alert.severity.value, alert.message,
                    alert.trigger_price, alert.cross_type, alert.cross_value, alert.timestamp
                ))
            conn.commit()

    def _store_cross_events(self, alerts: List[TechnicalAlert]):
        """Store cross events in separate table for detailed tracking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for alert in alerts:
                if alert.cross_type:  # Only store if it's a cross event
                    cursor.execute("""
                        INSERT OR REPLACE INTO cross_events 
                        (event_id, symbol, timeframe, indicator, cross_type, cross_value, 
                         trigger_price, current_value, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"cross_{alert.alert_id}", alert.symbol, alert.timeframe, alert.indicator,
                        alert.cross_type, alert.cross_value, alert.trigger_price, alert.current_value,
                        alert.timestamp
                    ))
            conn.commit()

    def get_recent_alerts(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent technical alerts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT alert_id, symbol, timeframe, indicator, condition, current_value, 
                           threshold, severity, message, trigger_price, cross_type, cross_value, timestamp
                    FROM technical_alerts 
                    WHERE is_active = 1 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                alerts = []
                for row in cursor.fetchall():
                    alert_id, symbol, timeframe, indicator, condition, current_value, threshold, severity, message, trigger_price, cross_type, cross_value, timestamp = row
                    alerts.append({
                        "alert_id": alert_id,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "indicator": indicator,
                        "condition": condition,
                        "current_value": current_value,
                        "threshold": threshold,
                        "severity": severity,
                        "message": message,
                        "trigger_price": trigger_price,
                        "cross_type": cross_type,
                        "cross_value": cross_value,
                        "timestamp": timestamp
                    })
                
                return {
                    "success": True,
                    "data": alerts,
                    "count": len(alerts),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return {"success": False, "error": str(e)}

    def get_cross_events(self, symbol: Optional[str] = None, timeframe: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get cross events for specific symbol/timeframe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT event_id, symbol, timeframe, indicator, cross_type, cross_value, 
                           trigger_price, current_value, timestamp
                    FROM cross_events 
                    WHERE is_active = 1
                """
                params = []
                
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol)
                
                if timeframe:
                    query += " AND timeframe = ?"
                    params.append(timeframe)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                events = []
                for row in cursor.fetchall():
                    event_id, symbol, timeframe, indicator, cross_type, cross_value, trigger_price, current_value, timestamp = row
                    events.append({
                        "event_id": event_id,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "indicator": indicator,
                        "cross_type": cross_type,
                        "cross_value": cross_value,
                        "trigger_price": trigger_price,
                        "current_value": current_value,
                        "timestamp": timestamp
                    })
                
                return {
                    "success": True,
                    "data": events,
                    "count": len(events),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting cross events: {e}")
            return {"success": False, "error": str(e)}

# Global instance
technical_alerts_service = TechnicalIndicatorsAlertService()
