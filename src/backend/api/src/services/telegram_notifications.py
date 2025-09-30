#!/usr/bin/env python3
"""
Telegram Notifications Service
Real-time trading alerts and notifications via Telegram Bot
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "ℹ️"
    SUCCESS = "✅"
    WARNING = "⚠️"
    CRITICAL = "🚨"
    TRADE = "💰"
    ANALYSIS = "📊"
    SYSTEM = "🤖"

@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str
    chat_id: str
    enable_notifications: bool = True
    silent_hours: Optional[List[int]] = None  # Hours to send silent notifications
    rate_limit: int = 30  # Max messages per minute

class TelegramNotificationService:
    """
    Telegram notification service for trading alerts
    """
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notification service
        
        Args:
            bot_token: Telegram bot token (get from @BotFather)
            chat_id: Chat ID to send messages to
        """
        # Try to get from environment variables if not provided
        import os
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not provided. Notifications disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            
        # Message queue for batching
        self.message_queue = asyncio.Queue()
        self.is_processing = False
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'last_message': None
        }
        
        logger.info(f"Telegram notification service initialized: {'Enabled' if self.enabled else 'Disabled'}")
    
    async def send_message(
        self,
        text: str,
        level: AlertLevel = AlertLevel.INFO,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """
        Send a message to Telegram
        
        Args:
            text: Message text
            level: Alert level
            parse_mode: Telegram parse mode (HTML or Markdown)
            disable_notification: Send silent notification
            
        Returns:
            True if message sent successfully
        """
        if not self.enabled:
            logger.debug(f"Telegram disabled. Message not sent: {text}")
            return False
        
        try:
            # Format message with emoji based on level
            formatted_text = f"{level.value} {text}"
            
            # Prepare request
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': formatted_text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        self.stats['messages_sent'] += 1
                        self.stats['last_message'] = datetime.now()
                        logger.debug(f"Telegram message sent: {text[:50]}...")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send Telegram message: {error_text}")
                        self.stats['messages_failed'] += 1
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            self.stats['messages_failed'] += 1
            return False
    
    async def send_trade_alert(self, trade: Dict[str, Any]) -> bool:
        """
        Send trading alert
        
        Args:
            trade: Trade information dictionary
            
        Returns:
            True if sent successfully
        """
        # Format trade alert
        action_emoji = "🟢" if trade.get('action', '').upper() in ['BUY', 'LONG'] else "🔴"
        
        message = f"""
<b>TRADE EXECUTED</b>

{action_emoji} <b>Action:</b> {trade.get('action', 'Unknown')}
💱 <b>Symbol:</b> {trade.get('symbol', 'Unknown')}
💵 <b>Size:</b> {trade.get('size', 0):.4f}
💲 <b>Price:</b> ${trade.get('price', 0):.4f}
📊 <b>Confidence:</b> {trade.get('confidence', 0):.1%}
🎯 <b>Score:</b> {trade.get('score', 0):.1f}/100

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return await self.send_message(message, AlertLevel.TRADE)
    
    async def send_analysis_report(self, analysis: Dict[str, Any]) -> bool:
        """
        Send analysis report
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            True if sent successfully
        """
        # Format analysis report
        signal_emoji = {
            'LONG': '🟢 BULLISH',
            'SHORT': '🔴 BEARISH',
            'NEUTRAL': '⚪ NEUTRAL'
        }.get(analysis.get('signal', 'NEUTRAL'), '⚪ NEUTRAL')
        
        message = f"""
<b>MARKET ANALYSIS</b>

💱 <b>Symbol:</b> {analysis.get('symbol', 'Unknown')}
{signal_emoji}
📊 <b>Score:</b> {analysis.get('score', 0):.1f}/100
🎯 <b>Confidence:</b> {analysis.get('confidence', 0):.1%}

<b>Key Indicators:</b>
• Cryptometer: {analysis.get('cryptometer_score', 0):.1f}
• KingFisher: {analysis.get('kingfisher_score', 0):.1f}
• Risk Level: {analysis.get('risk_level', 'Unknown')}

<b>Recommendation:</b>
{analysis.get('recommendation', 'No recommendation available')}

<i>Analysis Time: {datetime.now().strftime('%H:%M:%S')}</i>
"""
        
        return await self.send_message(message, AlertLevel.ANALYSIS)
    
    async def send_risk_alert(self, risk_data: Dict[str, Any]) -> bool:
        """
        Send risk management alert
        
        Args:
            risk_data: Risk information dictionary
            
        Returns:
            True if sent successfully
        """
        # Determine alert level based on risk
        risk_level = risk_data.get('risk_level', 'MEDIUM')
        if risk_level == 'CRITICAL':
            level = AlertLevel.CRITICAL
        elif risk_level == 'HIGH':
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.INFO
        
        message = f"""
<b>RISK ALERT</b>

⚠️ <b>Risk Level:</b> {risk_level}
💱 <b>Symbol:</b> {risk_data.get('symbol', 'Portfolio')}
📉 <b>Drawdown:</b> {risk_data.get('drawdown', 0):.2%}
💰 <b>Position Size:</b> {risk_data.get('position_size', 0):.4f}
🛡️ <b>Stop Loss:</b> ${risk_data.get('stop_loss', 0):.4f}

<b>Action Required:</b>
{risk_data.get('action', 'Monitor position closely')}

<i>Alert Time: {datetime.now().strftime('%H:%M:%S')}</i>
"""
        
        return await self.send_message(message, level)
    
    async def send_system_status(self, status: Dict[str, Any]) -> bool:
        """
        Send system status update
        
        Args:
            status: System status dictionary
            
        Returns:
            True if sent successfully
        """
        # Format system status
        health_emoji = "🟢" if status.get('healthy', True) else "🔴"
        
        message = f"""
<b>SYSTEM STATUS</b>

{health_emoji} <b>Health:</b> {'Healthy' if status.get('healthy', True) else 'Issues Detected'}
⚡ <b>Uptime:</b> {status.get('uptime', 'Unknown')}
📊 <b>Active Positions:</b> {status.get('active_positions', 0)}
💰 <b>Total P&L:</b> ${status.get('total_pnl', 0):.2f}

<b>Services:</b>
• Cryptometer: {status.get('cryptometer_status', '❓')}
• KuCoin: {status.get('kucoin_status', '❓')}
• Database: {status.get('database_status', '❓')}
• AI Agent: {status.get('ai_status', '❓')}

<b>Rate Limits:</b>
• API Calls: {status.get('api_calls_remaining', 0)}/{status.get('api_calls_limit', 0)}

<i>Status Update: {datetime.now().strftime('%H:%M:%S')}</i>
"""
        
        return await self.send_message(message, AlertLevel.SYSTEM)
    
    async def send_daily_summary(self, summary: Dict[str, Any]) -> bool:
        """
        Send daily trading summary
        
        Args:
            summary: Daily summary dictionary
            
        Returns:
            True if sent successfully
        """
        # Format daily summary
        profit_emoji = "🟢" if summary.get('daily_pnl', 0) > 0 else "🔴"
        
        message = f"""
<b>📅 DAILY SUMMARY</b>

{profit_emoji} <b>Daily P&L:</b> ${summary.get('daily_pnl', 0):.2f} ({summary.get('daily_pnl_pct', 0):.2%})
📈 <b>Total Trades:</b> {summary.get('total_trades', 0)}
✅ <b>Winning Trades:</b> {summary.get('winning_trades', 0)}
❌ <b>Losing Trades:</b> {summary.get('losing_trades', 0)}
🎯 <b>Win Rate:</b> {summary.get('win_rate', 0):.1%}

<b>Top Performers:</b>
{self._format_top_performers(summary.get('top_performers', []))}

<b>Worst Performers:</b>
{self._format_worst_performers(summary.get('worst_performers', []))}

<b>Portfolio Value:</b> ${summary.get('portfolio_value', 0):.2f}
<b>Available Balance:</b> ${summary.get('available_balance', 0):.2f}

<i>Summary Date: {datetime.now().strftime('%Y-%m-%d')}</i>
"""
        
        return await self.send_message(message, AlertLevel.SUCCESS)
    
    def _format_top_performers(self, performers: List[Dict]) -> str:
        """Format top performers list"""
        if not performers:
            return "• No data available"
        
        formatted = []
        for p in performers[:3]:
            emoji = "🥇" if len(formatted) == 0 else "🥈" if len(formatted) == 1 else "🥉"
            formatted.append(f"{emoji} {p.get('symbol', 'Unknown')}: +{p.get('pnl_pct', 0):.2%}")
        
        return "\n".join(formatted)
    
    def _format_worst_performers(self, performers: List[Dict]) -> str:
        """Format worst performers list"""
        if not performers:
            return "• No data available"
        
        formatted = []
        for p in performers[:3]:
            formatted.append(f"📉 {p.get('symbol', 'Unknown')}: {p.get('pnl_pct', 0):.2%}")
        
        return "\n".join(formatted)
    
    async def send_batch_messages(self, messages: List[Dict[str, Any]]) -> int:
        """
        Send multiple messages in batch
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Number of successfully sent messages
        """
        sent_count = 0
        for msg in messages:
            success = await self.send_message(
                msg.get('text', ''),
                msg.get('level', AlertLevel.INFO),
                msg.get('parse_mode', 'HTML'),
                msg.get('disable_notification', False)
            )
            if success:
                sent_count += 1
            
            # Small delay between messages to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return sent_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return {
            'enabled': self.enabled,
            'messages_sent': self.stats['messages_sent'],
            'messages_failed': self.stats['messages_failed'],
            'success_rate': (
                self.stats['messages_sent'] / 
                (self.stats['messages_sent'] + self.stats['messages_failed'])
                if (self.stats['messages_sent'] + self.stats['messages_failed']) > 0
                else 0
            ),
            'last_message': self.stats['last_message'].isoformat() if self.stats['last_message'] else None
        }

# Global Telegram service instance
telegram_service = None

def get_telegram_service() -> TelegramNotificationService:
    """Get or create Telegram service instance"""
    global telegram_service
    if telegram_service is None:
        telegram_service = TelegramNotificationService()
    return telegram_service

# Example usage functions
async def notify_trade_execution(
    symbol: str,
    action: str,
    size: float,
    price: float,
    confidence: float,
    score: float
):
    """Helper function to notify trade execution"""
    service = get_telegram_service()
    await service.send_trade_alert({
        'symbol': symbol,
        'action': action,
        'size': size,
        'price': price,
        'confidence': confidence,
        'score': score
    })

async def notify_risk_alert(
    symbol: str,
    risk_level: str,
    drawdown: float,
    action: str
):
    """Helper function to notify risk alert"""
    service = get_telegram_service()
    await service.send_risk_alert({
        'symbol': symbol,
        'risk_level': risk_level,
        'drawdown': drawdown,
        'action': action
    })

async def notify_analysis_complete(
    symbol: str,
    signal: str,
    score: float,
    confidence: float,
    recommendation: str
):
    """Helper function to notify analysis completion"""
    service = get_telegram_service()
    await service.send_analysis_report({
        'symbol': symbol,
        'signal': signal,
        'score': score,
        'confidence': confidence,
        'recommendation': recommendation
    })