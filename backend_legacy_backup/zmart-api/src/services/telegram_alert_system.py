#!/usr/bin/env python3
"""
🚨 Enhanced Telegram Alert System
Sends qualified trading signals with win rate analysis
Integrates with Master Orchestration Agent for 80%+ win rate signals
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import os
from dataclasses import dataclass

from src.services.telegram_notifications import TelegramNotificationService, AlertLevel
from src.agents.unified_qa_user_agent import unified_qa_user_agent, TimeFrame, AnalysisPackage

logger = logging.getLogger(__name__)

class SignalQuality(Enum):
    """Signal quality levels"""
    PREMIUM = "🏆"     # Win rate > 80%, High confidence
    HIGH = "⭐"        # Win rate > 70%, High confidence
    MEDIUM = "✅"      # Win rate > 60%, Medium confidence
    LOW = "ℹ️"        # Win rate > 50%, Low confidence
    SKIP = "⏭️"       # Below threshold, skip

@dataclass
class AlertConfiguration:
    """Alert configuration settings"""
    min_win_rate: float = 80.0              # Minimum win rate for alerts
    min_confidence: str = "HIGH"            # Minimum confidence level
    min_score: float = 70.0                 # Minimum composite score
    alert_timeframes: Optional[List[str]] = None      # Timeframes to monitor
    max_alerts_per_hour: int = 10           # Rate limiting
    quiet_hours: Optional[List[int]] = None           # Hours to suppress non-critical alerts
    
    def __post_init__(self):
        if self.alert_timeframes is None:
            self.alert_timeframes = ["1H-4H", "1D-3D", "1W-1M"]
        if self.quiet_hours is None:
            self.quiet_hours = [23, 0, 1, 2, 3, 4, 5, 6]  # 11 PM to 6 AM

class TelegramAlertSystem:
    """
    Enhanced Telegram Alert System for qualified signals
    Only sends alerts for high-probability trading opportunities
    """
    
    def __init__(self, config: Optional[AlertConfiguration] = None):
        """
        Initialize the alert system
        
        Args:
            config: Alert configuration settings
        """
        # Initialize Telegram service
        self.telegram = TelegramNotificationService()
        
        # Configuration
        self.config = config or AlertConfiguration()
        
        # Alert tracking
        self.recent_alerts = []
        self.alert_history = {}
        
        # Statistics
        self.stats = {
            'total_signals_analyzed': 0,
            'qualified_signals': 0,
            'alerts_sent': 0,
            'premium_alerts': 0,
            'successful_trades': 0,
            'failed_trades': 0
        }
        
        # Signal queue for batch processing
        self.signal_queue = asyncio.Queue()
        self.is_monitoring = False
        
        logger.info(f"🚨 Telegram Alert System initialized with {self.config.min_win_rate}% win rate threshold")
    
    async def analyze_and_alert(
        self,
        symbol: str,
        signal_data: Dict[str, Any],
        source: str = "Master Orchestration"
    ) -> bool:
        """
        Analyze signal and send alert if it meets criteria
        
        Args:
            symbol: Trading symbol
            signal_data: Signal data from orchestration
            source: Source of the signal
        
        Returns:
            True if alert was sent
        """
        self.stats['total_signals_analyzed'] += 1
        
        try:
            # Get comprehensive analysis with win rates
            analysis = await unified_qa_user_agent.analyze_with_teaching(
                symbol=symbol,
                user_question=f"Should I trade {symbol} based on current signals?",
                package=AnalysisPackage.STANDARD
            )
            
            if not analysis['success']:
                logger.warning(f"Failed to analyze {symbol}")
                return False
            
            # Extract win rates
            win_rates = analysis['analysis']['win_rates']
            
            # Check if signal qualifies for alert
            qualification = self._qualify_signal(win_rates, signal_data)
            
            if qualification['qualified']:
                self.stats['qualified_signals'] += 1
                
                # Check rate limiting
                if not self._check_rate_limit():
                    logger.info(f"Rate limit reached, skipping alert for {symbol}")
                    return False
                
                # Check quiet hours
                if self._is_quiet_hour() and qualification['quality'] != SignalQuality.PREMIUM:
                    logger.info(f"Quiet hours, skipping non-premium alert for {symbol}")
                    return False
                
                # Format and send alert
                alert_sent = await self._send_qualified_alert(
                    symbol=symbol,
                    win_rates=win_rates,
                    signal_data=signal_data,
                    qualification=qualification,
                    source=source,
                    analysis=analysis
                )
                
                if alert_sent:
                    self.stats['alerts_sent'] += 1
                    if qualification['quality'] == SignalQuality.PREMIUM:
                        self.stats['premium_alerts'] += 1
                    
                    # Track alert
                    self._track_alert(symbol, qualification, win_rates)
                    
                    return True
            
            logger.debug(f"Signal for {symbol} did not qualify: {qualification['reason']}")
            return False
            
        except Exception as e:
            logger.error(f"Error analyzing signal for {symbol}: {e}")
            return False
    
    def _qualify_signal(
        self,
        win_rates: Dict[str, Dict[str, Any]],
        signal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine if signal qualifies for alert
        
        Returns:
            Qualification status and details
        """
        # Check each timeframe
        qualified_timeframes = []
        max_win_rate = 0
        best_confidence = "LOW"
        
        for timeframe, data in win_rates.items():
            if self.config.alert_timeframes and timeframe not in self.config.alert_timeframes:
                continue
            
            win_rate = float(data['win_rate'].rstrip('%'))
            confidence = data['confidence']
            
            # Track best values
            if win_rate > max_win_rate:
                max_win_rate = win_rate
                best_confidence = confidence
            
            # Check if this timeframe qualifies
            if win_rate >= self.config.min_win_rate and confidence == self.config.min_confidence:
                qualified_timeframes.append({
                    'timeframe': timeframe,
                    'win_rate': win_rate,
                    'confidence': confidence,
                    'recommendation': data['recommendation']
                })
        
        # Determine overall qualification
        if not qualified_timeframes:
            return {
                'qualified': False,
                'reason': f"No timeframe met criteria (min {self.config.min_win_rate}% win rate, {self.config.min_confidence} confidence)",
                'quality': SignalQuality.SKIP
            }
        
        # Determine signal quality
        if max_win_rate >= 80 and best_confidence == "HIGH":
            quality = SignalQuality.PREMIUM
        elif max_win_rate >= 70 and best_confidence == "HIGH":
            quality = SignalQuality.HIGH
        elif max_win_rate >= 60:
            quality = SignalQuality.MEDIUM
        else:
            quality = SignalQuality.LOW
        
        # Additional check from signal data
        composite_score = signal_data.get('composite_score', 0)
        if composite_score < self.config.min_score:
            return {
                'qualified': False,
                'reason': f"Composite score {composite_score:.1f} below threshold {self.config.min_score}",
                'quality': SignalQuality.SKIP
            }
        
        return {
            'qualified': True,
            'quality': quality,
            'qualified_timeframes': qualified_timeframes,
            'max_win_rate': max_win_rate,
            'best_confidence': best_confidence,
            'composite_score': composite_score
        }
    
    async def _send_qualified_alert(
        self,
        symbol: str,
        win_rates: Dict[str, Dict[str, Any]],
        signal_data: Dict[str, Any],
        qualification: Dict[str, Any],
        source: str,
        analysis: Dict[str, Any]
    ) -> bool:
        """
        Send formatted alert for qualified signal
        """
        quality_icon = qualification['quality'].value
        
        # Format timeframe details
        timeframe_details = []
        for tf in qualification['qualified_timeframes']:
            timeframe_details.append(
                f"• {tf['timeframe']}: {tf['win_rate']:.1f}% ({tf['confidence']}) - {tf['recommendation']}"
            )
        
        # Extract key recommendations
        recommendations = analysis.get('recommendations', {})
        position_size = recommendations.get('position_sizing', 'Not specified')
        primary_action = recommendations.get('primary_action', 'Not specified')
        
        # Format the alert message
        message = f"""
{quality_icon} <b>QUALIFIED TRADING SIGNAL</b> {quality_icon}

💱 <b>Symbol:</b> {symbol}
📊 <b>Signal Quality:</b> {qualification['quality'].name}
🎯 <b>Max Win Rate:</b> {qualification['max_win_rate']:.1f}%
🔥 <b>Confidence:</b> {qualification['best_confidence']}
💯 <b>Composite Score:</b> {signal_data.get('composite_score', 0):.1f}/100

<b>📈 Qualified Timeframes:</b>
{chr(10).join(timeframe_details)}

<b>🎯 Recommendation:</b>
{primary_action}

<b>💰 Position Sizing:</b>
{position_size}

<b>📊 Key Data Sources:</b>
• Cryptometer: {signal_data.get('cryptometer_score', 0):.1f}
• KingFisher: {signal_data.get('kingfisher_score', 0):.1f}
• RiskMetric: {signal_data.get('riskmetric_score', 0):.1f}

<b>⚠️ Risk Management:</b>
• Stop Loss: {recommendations.get('risk_management', {}).get('stop_loss', 'Set 2-3% below entry')}
• Take Profit: {recommendations.get('risk_management', {}).get('take_profit', 'Target 1:2 R/R minimum')}

<b>Source:</b> {source}
<i>Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>

⚡ <i>This is a high-probability signal meeting strict criteria</i>
"""
        
        # Send with appropriate alert level
        alert_level = AlertLevel.CRITICAL if qualification['quality'] == SignalQuality.PREMIUM else AlertLevel.TRADE
        
        return await self.telegram.send_message(message, alert_level)
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        # Remove old alerts (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.recent_alerts = [
            alert for alert in self.recent_alerts 
            if alert['timestamp'] > cutoff_time
        ]
        
        # Check count
        return len(self.recent_alerts) < self.config.max_alerts_per_hour
    
    def _is_quiet_hour(self) -> bool:
        """Check if current hour is in quiet hours"""
        current_hour = datetime.now().hour
        return bool(self.config.quiet_hours and current_hour in self.config.quiet_hours)
    
    def _track_alert(
        self,
        symbol: str,
        qualification: Dict[str, Any],
        win_rates: Dict[str, Dict[str, Any]]
    ):
        """Track alert for history and analysis"""
        alert_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'quality': qualification['quality'].name,
            'max_win_rate': qualification['max_win_rate'],
            'win_rates': win_rates
        }
        
        self.recent_alerts.append(alert_record)
        
        # Store in history
        if symbol not in self.alert_history:
            self.alert_history[symbol] = []
        self.alert_history[symbol].append(alert_record)
    
    async def send_performance_update(self) -> bool:
        """Send performance update of alert system"""
        if self.stats['qualified_signals'] == 0:
            success_rate = 0
        else:
            success_rate = (self.stats['successful_trades'] / self.stats['qualified_signals']) * 100
        
        message = f"""
📊 <b>ALERT SYSTEM PERFORMANCE</b>

📈 <b>Statistics:</b>
• Signals Analyzed: {self.stats['total_signals_analyzed']}
• Qualified Signals: {self.stats['qualified_signals']}
• Alerts Sent: {self.stats['alerts_sent']}
• Premium Alerts: {self.stats['premium_alerts']}

🎯 <b>Trading Results:</b>
• Successful Trades: {self.stats['successful_trades']}
• Failed Trades: {self.stats['failed_trades']}
• Success Rate: {success_rate:.1f}%

⚙️ <b>Configuration:</b>
• Min Win Rate: {self.config.min_win_rate}%
• Min Confidence: {self.config.min_confidence}
• Min Score: {self.config.min_score}

<i>Update Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return await self.telegram.send_message(message, AlertLevel.ANALYSIS)
    
    async def start_monitoring(self):
        """Start monitoring for signals"""
        if self.is_monitoring:
            logger.warning("Alert monitoring already running")
            return
        
        self.is_monitoring = True
        logger.info("🚨 Started Telegram alert monitoring")
        
        # Send startup notification
        await self.telegram.send_message(
            f"🤖 <b>Alert System Started</b>\n\n"
            f"Monitoring for signals with:\n"
            f"• Min Win Rate: {self.config.min_win_rate}%\n"
            f"• Min Confidence: {self.config.min_confidence}\n"
            f"• Active Timeframes: {', '.join(self.config.alert_timeframes or [])}",
            AlertLevel.SYSTEM
        )
        
        # Start signal processing loop
        asyncio.create_task(self._process_signal_queue())
    
    async def stop_monitoring(self):
        """Stop monitoring for signals"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        logger.info("🛑 Stopped Telegram alert monitoring")
        
        # Send shutdown notification
        await self.telegram.send_message(
            "🛑 <b>Alert System Stopped</b>",
            AlertLevel.SYSTEM
        )
    
    async def _process_signal_queue(self):
        """Process queued signals"""
        while self.is_monitoring:
            try:
                # Get signal from queue (with timeout)
                signal = await asyncio.wait_for(
                    self.signal_queue.get(),
                    timeout=60.0
                )
                
                # Process signal
                await self.analyze_and_alert(
                    symbol=signal['symbol'],
                    signal_data=signal['data'],
                    source=signal.get('source', 'Unknown')
                )
                
            except asyncio.TimeoutError:
                # No signals in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing signal queue: {e}")
                await asyncio.sleep(5)
    
    async def queue_signal(self, symbol: str, signal_data: Dict[str, Any], source: str = "API"):
        """
        Queue a signal for processing
        
        Args:
            symbol: Trading symbol
            signal_data: Signal data
            source: Source of the signal
        """
        await self.signal_queue.put({
            'symbol': symbol,
            'data': signal_data,
            'source': source
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        return {
            'stats': self.stats,
            'recent_alerts_count': len(self.recent_alerts),
            'symbols_tracked': list(self.alert_history.keys()),
            'is_monitoring': self.is_monitoring,
            'telegram_enabled': self.telegram.enabled
        }

# Global instance
alert_config = AlertConfiguration(
    min_win_rate=float(os.getenv('TELEGRAM_MIN_WIN_RATE', '80')),
    min_confidence=os.getenv('TELEGRAM_MIN_CONFIDENCE', 'HIGH'),
    min_score=float(os.getenv('TELEGRAM_MIN_SCORE', '70'))
)

telegram_alert_system = TelegramAlertSystem(alert_config)

async def get_alert_system() -> TelegramAlertSystem:
    """Get global alert system instance"""
    return telegram_alert_system