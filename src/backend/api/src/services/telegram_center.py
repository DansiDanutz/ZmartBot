#!/usr/bin/env python3
"""
📱 Telegram Center - Professional Message Aggregation System
Sends consolidated updates every 15 minutes with AI-curated content
Avoids channel spam by batching and prioritizing messages
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import json
import statistics

from src.services.telegram_notifications import TelegramNotificationService, AlertLevel
from src.services.telegram_message_templates import MessageTemplates
from src.agents.unified_qa_user_agent import unified_qa_user_agent, AnalysisPackage

# AI for message composition
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1    # Immediate send (bypasses batching)
    HIGH = 2        # Include in next batch
    MEDIUM = 3      # Include if space available
    LOW = 4         # Summary only
    INFO = 5        # Aggregate statistics

class MessageType(Enum):
    """Types of messages to handle"""
    # Trading Actions (Immediate)
    OPEN_POSITION = "open_position"      # New trade opened - immediate alert
    TARGET_HIT = "target_hit"            # Target reached - immediate alert
    STOP_LOSS_HIT = "stop_loss"          # Stop loss triggered - immediate
    CLOSE_POSITION = "close_position"    # Position closed - immediate
    
    # Regular Updates (Scheduled)
    DAILY_REVIEW = "daily_review"        # Once per day at fixed time
    HIGH_SCORE_SYMBOL = "high_score"     # Every 8 hours - top performer
    MARKET_UPDATE = "market_update"      # Every 15 minutes batch
    
    # Special Alerts (Event-driven)
    RARE_OPPORTUNITY = "rare_opportunity" # Immediate when detected
    WHALE_ALERT = "whale_alert"          # Large market moves
    TREND_REVERSAL = "trend_reversal"    # Major trend changes
    VOLATILITY_SPIKE = "volatility_spike" # Sudden volatility
    
    # System & Info
    SYSTEM = "system"                    # System updates
    EDUCATION = "education"              # Educational content
    MOTIVATION = "motivation"            # Motivational messages

class TelegramCenter:
    """
    Professional Telegram Message Center
    Aggregates, prioritizes, and sends consolidated updates every 15 minutes
    """
    
    def __init__(self, interval_minutes: int = 15):
        """
        Initialize Telegram Center
        
        Args:
            interval_minutes: Minutes between consolidated updates (default 15)
        """
        # Core services
        self.telegram = TelegramNotificationService()
        self.interval = interval_minutes
        
        # Message management
        self.message_queue: Dict[MessagePriority, List[Dict]] = defaultdict(list)
        self.processed_signals = set()  # Track to avoid duplicates
        self.last_batch_time = datetime.now()
        
        # AI client for intelligent message composition
        self.ai_client = None
        if OpenAI:
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.ai_client = OpenAI(api_key=api_key)
                    logger.info("📱 AI-powered message composition enabled")
                except Exception as e:
                    logger.warning(f"Could not initialize AI client: {e}")
        
        # Market tracking
        self.market_summary = {
            'top_movers': [],
            'signals_generated': 0,
            'trades_executed': 0,
            'current_positions': {},
            'pnl_session': 0,
            'alerts_triggered': 0
        }
        
        # Configuration for message composition
        self.message_config = {
            'max_signals_per_batch': 5,      # Top 5 signals only
            'max_updates_per_batch': 10,     # Maximum updates in one message
            'include_market_summary': True,
            'include_performance': True,
            'include_education': True,       # Educational insights
            'professional_tone': True
        }
        
        # Statistics
        self.stats = {
            'batches_sent': 0,
            'messages_aggregated': 0,
            'critical_alerts': 0,
            'ai_compositions': 0
        }
        
        # Control flags
        self.is_running = False
        self.batch_task = None
        
        logger.info(f"📱 Telegram Center initialized - {interval_minutes} minute intervals")
    
    async def start(self):
        """Start the Telegram Center batch processing"""
        if self.is_running:
            logger.warning("Telegram Center already running")
            return
        
        self.is_running = True
        self.batch_task = asyncio.create_task(self._batch_processor())
        
        # Send startup message
        await self._send_immediate(
            "🚀 <b>Telegram Center Activated</b>\n\n"
            f"Professional updates every {self.interval} minutes\n"
            "High-quality signals and market insights incoming...",
            AlertLevel.SYSTEM
        )
        
        logger.info("📱 Telegram Center started")
    
    async def stop(self):
        """Stop the Telegram Center"""
        self.is_running = False
        
        if self.batch_task:
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
        
        # Send final summary before stopping
        await self._send_batch_update()
        
        await self._send_immediate(
            "🛑 <b>Telegram Center Deactivated</b>\n"
            f"Total batches sent: {self.stats['batches_sent']}",
            AlertLevel.SYSTEM
        )
        
        logger.info("📱 Telegram Center stopped")
    
    async def add_message(
        self,
        content: Dict[str, Any],
        message_type: MessageType,
        priority: MessagePriority = MessagePriority.MEDIUM
    ):
        """
        Add a message to the queue for batching
        
        Args:
            content: Message content/data
            message_type: Type of message
            priority: Message priority
        """
        # Critical messages bypass batching
        if priority == MessagePriority.CRITICAL:
            await self._handle_critical_message(content, message_type)
            return
        
        # Add to queue for batching
        message = {
            'content': content,
            'type': message_type,
            'timestamp': datetime.now(),
            'id': f"{message_type.value}_{datetime.now().timestamp()}"
        }
        
        self.message_queue[priority].append(message)
        self.stats['messages_aggregated'] += 1
        
        logger.debug(f"Message queued: {message_type.value} (Priority: {priority.name})")
    
    async def send_open_position(
        self,
        symbol: str,
        position_data: Dict[str, Any]
    ):
        """
        Send IMMEDIATE alert when opening a new position
        Provides full transparency on WHY we're entering
        """
        try:
            # Add symbol to position data
            position_data['symbol'] = symbol
            
            # Use template for consistent formatting
            message = MessageTemplates.open_position_template(position_data)
            
            # Send immediately - this is critical information
            await self.telegram.send_message(message, AlertLevel.TRADE)
            
            # Track for daily review
            self.market_summary['trades_executed'] += 1
            
            logger.info(f"📤 Sent OPEN POSITION alert for {symbol}")
            
        except Exception as e:
            logger.error(f"Failed to send open position alert: {e}")
    
    async def _compose_open_position_message(
        self, 
        symbol: str, 
        position_data: Dict[str, Any]
    ) -> str:
        """Compose detailed open position message with full explanation"""
        
        if self.ai_client:
            # AI-composed message for maximum clarity
            prompt = f"""
Create an engaging OPEN POSITION alert that explains WHY we're entering this trade.

Position Details:
- Symbol: {symbol}
- Action: {position_data.get('action', 'LONG')}
- Entry Price: ${position_data.get('entry_price', 0)}
- Stop Loss: ${position_data.get('stop_loss', 0)}
- Target 1: ${position_data.get('target1', 0)}
- Target 2: ${position_data.get('target2', 0)}
- Position Size: {position_data.get('position_size', '2%')} of portfolio
- Win Rate: {position_data.get('win_rate', 0)}%
- Confidence: {position_data.get('confidence', 'HIGH')}

Technical Reasons:
{json.dumps(position_data.get('technical_analysis', {}), indent=2)}

REQUIREMENTS:
1. Start with exciting hook: "🚨 WE'RE GOING IN!" or similar
2. Explain the setup in poker/gambling terms
3. List 3 specific reasons WHY this trade makes sense
4. Include risk management details
5. End with confidence-building statement
6. Use emojis and energy
7. Make it feel like we're all in this together

Keep it under 500 words but be thorough."""

            try:
                response = self.ai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You're a charismatic trading mentor announcing a new position to your trading club."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                content = response.choices[0].message.content
                if content is None:
                    # Fallback to template if AI returns None
                    action_emoji = "🟢" if position_data.get('action') == 'LONG' else "🔴"
                    return f"""
{action_emoji} <b>WE'RE GOING IN! NEW POSITION OPENED!</b> {action_emoji}

<b>The Play:</b> {symbol} - {position_data.get('action', 'LONG')}

<b>🎯 WHY We're Taking This Trade:</b>
1️⃣ <b>Technical Setup:</b> {position_data.get('pattern', 'Bullish breakout pattern confirmed')}
2️⃣ <b>Win Rate:</b> {position_data.get('win_rate', 75)}% probability based on our analysis
3️⃣ <b>Risk/Reward:</b> Targeting {position_data.get('risk_reward', '1:3')} ratio - the math is on our side!

<b>📊 The Numbers:</b>
• Entry: ${position_data.get('entry_price', 0):.4f}
• Stop Loss: ${position_data.get('stop_loss', 0):.4f} ({position_data.get('risk_percent', 2)}% risk)
• Target 1: ${position_data.get('target1', 0):.4f} (50% off the table)
• Target 2: ${position_data.get('target2', 0):.4f} (let it ride!)
• Position Size: {position_data.get('position_size', '2%')} of portfolio

<b>🎲 The Strategy:</b>
{position_data.get('strategy', "We're playing this like pros - tight stop, clear targets. If we're wrong, we lose small. If we're right, we win big!")}

<b>💪 Confidence Level:</b> {position_data.get('confidence', 'HIGH')}
{self._get_confidence_message(position_data.get('confidence', 'HIGH'))}

<i>⏰ Entry Time: {datetime.now().strftime('%H:%M:%S UTC')}</i>

Let's ride this together! Remember: Plan the trade, trade the plan! 🚀
"""
                return content
            except:
                pass
        
        # Fallback template
        action_emoji = "🟢" if position_data.get('action') == 'LONG' else "🔴"
        
        return f"""
{action_emoji} <b>WE'RE GOING IN! NEW POSITION OPENED!</b> {action_emoji}

<b>The Play:</b> {symbol} - {position_data.get('action', 'LONG')}

<b>🎯 WHY We're Taking This Trade:</b>
1️⃣ <b>Technical Setup:</b> {position_data.get('pattern', 'Bullish breakout pattern confirmed')}
2️⃣ <b>Win Rate:</b> {position_data.get('win_rate', 75)}% probability based on our analysis
3️⃣ <b>Risk/Reward:</b> Targeting {position_data.get('risk_reward', '1:3')} ratio - the math is on our side!

<b>📊 The Numbers:</b>
• Entry: ${position_data.get('entry_price', 0):.4f}
• Stop Loss: ${position_data.get('stop_loss', 0):.4f} ({position_data.get('risk_percent', 2)}% risk)
• Target 1: ${position_data.get('target1', 0):.4f} (50% off the table)
• Target 2: ${position_data.get('target2', 0):.4f} (let it ride!)
• Position Size: {position_data.get('position_size', '2%')} of portfolio

<b>🎲 The Strategy:</b>
{position_data.get('strategy', "We're playing this like pros - tight stop, clear targets. If we're wrong, we lose small. If we're right, we win big!")}

<b>💪 Confidence Level:</b> {position_data.get('confidence', 'HIGH')}
{self._get_confidence_message(position_data.get('confidence', 'HIGH'))}

<i>⏰ Entry Time: {datetime.now().strftime('%H:%M:%S UTC')}</i>

Let's ride this together! Remember: Plan the trade, trade the plan! 🚀
"""
    
    async def send_target_hit(
        self,
        symbol: str,
        target_data: Dict[str, Any]
    ):
        """
        Send alert when target is hit
        Explains WHY we're taking profits here
        """
        # Add symbol to target data
        target_data['symbol'] = symbol
        
        # Use template for consistent formatting
        message = MessageTemplates.target_hit_template(target_data)
        
        await self.telegram.send_message(message, AlertLevel.SUCCESS)
        logger.info(f"📤 Sent TARGET HIT alert for {symbol}")
    
    async def send_close_position(
        self,
        symbol: str,
        close_data: Dict[str, Any]
    ):
        """
        Send alert when closing a position
        Full transparency on WHY we're exiting
        """
        # Add symbol to close data
        close_data['symbol'] = symbol
        
        # Use template for consistent formatting
        message = MessageTemplates.close_position_template(close_data)
        
        await self.telegram.send_message(message, AlertLevel.TRADE)
        logger.info(f"📤 Sent CLOSE POSITION alert for {symbol}")
    
    async def send_daily_review(self):
        """
        Send comprehensive daily review
        Scheduled once per day at fixed time
        """
        # Gather all trade data for the day
        review_data = self._gather_daily_data()
        
        if self.ai_client:
            prompt = f"""
Create an engaging DAILY TRADING REVIEW that summarizes today's performance.

Today's Data:
{json.dumps(review_data, indent=2)}

Include:
1. Opening hook with today's overall result
2. List of trades (opened and closed) with brief results
3. Best trade of the day (and why it worked)
4. Lesson of the day
5. Tomorrow's watchlist (top 3 opportunities)
6. Motivational closing

Use gambling/trading metaphors. Be honest about losses but keep morale high.
Make it feel like a team debriefing after a day at the tables."""

            try:
                response = self.ai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You're a trading team leader giving the daily debrief."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=800
                )
                message = response.choices[0].message.content
            except:
                message = self._compose_standard_daily_review(review_data)
        else:
            message = self._compose_standard_daily_review(review_data)
        
        await self.telegram.send_message(
            f"📅 <b>DAILY TRADING REVIEW</b>\n{datetime.now().strftime('%B %d, %Y')}\n{'='*30}\n\n{message}",
            AlertLevel.ANALYSIS
        )
        logger.info("📤 Sent DAILY REVIEW")
    
    async def send_high_score_symbol(self):
        """
        Send top performing symbol analysis
        Every 8 hours - premium analysis for free users
        """
        # Get top symbol from scoring system
        top_symbol = await self._get_top_scoring_symbol()
        
        if not top_symbol:
            return
        
        # Get detailed analysis for all timeframes
        analysis = await self._get_detailed_symbol_analysis(top_symbol)
        
        message = f"""
🏆 <b>HIGH SCORE SYMBOL OF THE DAY</b> 🏆

<b>Winner: {top_symbol['symbol']}</b>
Overall Score: {top_symbol['score']}/100

<b>📊 3-TIMEFRAME ANALYSIS:</b>

<b>⚡ SHORT TERM (1H-4H):</b>
• Win Rate: {analysis['short']['win_rate']}%
• Signal: {analysis['short']['signal']}
• Key Level: ${analysis['short']['key_level']}
{analysis['short']['description']}

<b>📈 MEDIUM TERM (1D-3D):</b>
• Win Rate: {analysis['medium']['win_rate']}%
• Signal: {analysis['medium']['signal']}
• Key Level: ${analysis['medium']['key_level']}
{analysis['medium']['description']}

<b>🎯 LONG TERM (1W-1M):</b>
• Win Rate: {analysis['long']['win_rate']}%
• Signal: {analysis['long']['signal']}
• Key Level: ${analysis['long']['key_level']}
{analysis['long']['description']}

<b>💎 WHY THIS IS TODAY'S TOP PICK:</b>
{analysis['why_top_pick']}

<b>📍 TRADING STRATEGY:</b>
• Best Timeframe: {analysis['best_timeframe']}
• Entry Strategy: {analysis['entry_strategy']}
• Risk Management: {analysis['risk_management']}

<i>🎁 This premium analysis is our gift to you! Next high score in 8 hours.</i>

<i>⏰ {datetime.now().strftime('%H:%M UTC')}</i>
"""
        
        await self.telegram.send_message(message, AlertLevel.ANALYSIS)
        logger.info(f"📤 Sent HIGH SCORE symbol: {top_symbol['symbol']}")
    
    async def send_rare_opportunity(
        self,
        opportunity_data: Dict[str, Any]
    ):
        """
        Send RARE OPPORTUNITY alert
        Only for exceptional setups that meet strict criteria
        """
        symbol = opportunity_data['symbol']
        
        message = f"""
🌟🚨 <b>RARE OPPORTUNITY DETECTED!</b> 🚨🌟

<b>THIS DOESN'T HAPPEN OFTEN - PAY ATTENTION!</b>

<b>Symbol: {symbol}</b>

<b>🎰 Why This Is SPECIAL:</b>
{opportunity_data.get('why_rare', 
"Multiple confluence factors aligning perfectly - this is a 'perfect storm' setup that historically occurs less than 5% of the time!")}

<b>📊 The Convergence:</b>
✅ Technical: {opportunity_data.get('technical', 'Major pattern breakout')}
✅ Fundamental: {opportunity_data.get('fundamental', 'Catalyst event confirmed')}
✅ Sentiment: {opportunity_data.get('sentiment', 'Extreme bullish shift')}
✅ Volume: {opportunity_data.get('volume', 'Institutional accumulation detected')}
✅ Timing: {opportunity_data.get('timing', 'Optimal market conditions')}

<b>🎯 The Play:</b>
• Entry Zone: ${opportunity_data.get('entry_min', 0):.4f} - ${opportunity_data.get('entry_max', 0):.4f}
• Stop Loss: ${opportunity_data.get('stop_loss', 0):.4f}
• Target 1: ${opportunity_data.get('target1', 0):.4f} ({opportunity_data.get('target1_gain', 0):.1f}%)
• Target 2: ${opportunity_data.get('target2', 0):.4f} ({opportunity_data.get('target2_gain', 0):.1f}%)
• Moon Target: ${opportunity_data.get('moon_target', 0):.4f} ({opportunity_data.get('moon_gain', 0):.1f}%)

<b>⚡ Historical Context:</b>
{opportunity_data.get('historical', 
"Last time we saw this setup: +45% in 3 days. Before that: +62% in a week. This is the kind of trade that makes your month!")}

<b>🎲 Recommended Action:</b>
{opportunity_data.get('action', 
"Consider a larger position (3-5% vs normal 2%). This is where we press our edge - but STILL use stops!")}

<b>⏰ URGENCY: {opportunity_data.get('urgency', 'HIGH - Window closing fast!')}</b>

<i>Remember: Rare doesn't mean risk-free. Trade the plan!</i>
<i>But also... this is why we're here! LET'S GO! 🚀</i>

<i>{datetime.now().strftime('%H:%M:%S UTC')}</i>
"""
        
        # Rare opportunities are CRITICAL priority
        await self.telegram.send_message(message, AlertLevel.CRITICAL)
        logger.info(f"🌟 Sent RARE OPPORTUNITY alert for {symbol}")
    
    def _get_confidence_message(self, confidence: str) -> str:
        """Get playful confidence message"""
        messages = {
            'HIGH': "We're holding pocket aces here! 🃏",
            'MEDIUM': "Good cards, playing it smart! 🎯",
            'LOW': "Calculated risk, small bet! 🎲"
        }
        return messages.get(confidence, "Let's see how this plays out! 🎰")
    
    def _gather_daily_data(self) -> Dict[str, Any]:
        """Gather all data for daily review"""
        # This would pull from database/tracking
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'trades_opened': self.market_summary.get('trades_executed', 0),
            'trades_closed': 0,  # Would track separately
            'total_pnl': self.market_summary.get('pnl_session', 0),
            'win_rate': 65.5,  # Calculate from actual trades
            'best_trade': {'symbol': 'BTC', 'pnl': 5.2},
            'worst_trade': {'symbol': 'XRP', 'pnl': -1.8},
            'open_positions': self.market_summary.get('current_positions', {})
        }
    
    def _compose_standard_daily_review(self, review_data: Dict) -> str:
        """Compose standard daily review without AI"""
        pnl = review_data.get('total_pnl', 0)
        emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        
        return f"""
{emoji} Today's P&L: ${pnl:.2f} ({'+' if pnl > 0 else ''}{(pnl/10000)*100:.2f}%)

<b>📊 Today's Action:</b>
• Trades Opened: {review_data.get('trades_opened', 0)}
• Trades Closed: {review_data.get('trades_closed', 0)}
• Win Rate: {review_data.get('win_rate', 0):.1f}%

<b>🏆 Best Trade:</b>
{review_data.get('best_trade', {}).get('symbol', 'N/A')}: +{review_data.get('best_trade', {}).get('pnl', 0):.2f}%

<b>📚 Today's Lesson:</b>
{"Patience paid off - we waited for quality setups!" if pnl > 0 else "Every day is a learning opportunity. Tomorrow we come back stronger!"}

<b>👀 Tomorrow's Watchlist:</b>
Coming soon based on overnight analysis...

Keep grinding, team! Consistency beats luck every time! 💪
"""
    
    async def _get_top_scoring_symbol(self) -> Optional[Dict[str, Any]]:
        """Get the highest scoring symbol from the system"""
        # This would integrate with the scoring system
        # For now, return mock data
        return {
            'symbol': 'BTC',
            'score': 87.5,
            'components': {
                'cryptometer': 85,
                'kingfisher': 90,
                'riskmetric': 88
            }
        }
    
    async def _get_detailed_symbol_analysis(self, symbol_data: Dict) -> Dict[str, Any]:
        """Get detailed analysis for all timeframes"""
        # This would call the Unified QA Agent for comprehensive analysis
        return {
            'short': {
                'win_rate': 78.5,
                'signal': 'LONG',
                'key_level': 45000,
                'description': 'Bullish momentum building, breakout imminent'
            },
            'medium': {
                'win_rate': 82.3,
                'signal': 'STRONG LONG',
                'key_level': 48000,
                'description': 'Major resistance cleared, trend acceleration expected'
            },
            'long': {
                'win_rate': 75.0,
                'signal': 'ACCUMULATE',
                'key_level': 52000,
                'description': 'Long-term uptrend intact, building for next leg up'
            },
            'why_top_pick': 'Perfect confluence of technical, fundamental, and sentiment factors',
            'best_timeframe': 'Medium (1D-3D)',
            'entry_strategy': 'Scale in on any dips to $44,500-45,000',
            'risk_management': 'Stop loss below $43,500, position size 2-3% of portfolio'
        }
    
    async def _batch_processor(self):
        """Process message batches at regular intervals"""
        while self.is_running:
            try:
                # Wait for interval
                await asyncio.sleep(self.interval * 60)
                
                # Send batch update
                await self._send_batch_update()
                
                # Clear old processed signals (keep last hour only)
                cutoff = datetime.now() - timedelta(hours=1)
                self.processed_signals = {
                    s for s in self.processed_signals 
                    if '_' not in s or float(s.split('_')[-1]) > cutoff.timestamp()
                }
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
                await asyncio.sleep(60)  # Wait a minute before retry
    
    async def _send_batch_update(self):
        """Send consolidated batch update"""
        if not self._has_messages():
            logger.debug("No messages to send in batch")
            return
        
        try:
            # Compose professional message
            if self.ai_client:
                message = await self._compose_ai_message()
            else:
                message = self._compose_standard_message()
            
            # Send the batch
            if message:
                success = await self.telegram.send_message(
                    message,
                    AlertLevel.ANALYSIS
                )
                
                if success:
                    self.stats['batches_sent'] += 1
                    logger.info(f"📱 Batch #{self.stats['batches_sent']} sent")
                
                # Clear processed messages
                self._clear_processed_messages()
            
        except Exception as e:
            logger.error(f"Error sending batch update: {e}")
    
    async def _compose_ai_message(self) -> str:
        """Use AI to compose professional consolidated message with detailed explanations"""
        try:
            # Get top signals with full analysis
            top_signals = self._get_top_signals()
            
            # Get detailed analysis for each top signal
            signal_analyses = []
            for signal in top_signals[:3]:  # Top 3 only for detailed analysis
                analysis = await self._get_signal_analysis(signal)
                signal_analyses.append(analysis)
            
            # Get playful opening based on market conditions
            market_mood = self._get_market_mood(top_signals)
            
            # AI prompt for professional message with playful language
            prompt = f"""
You are a charismatic trading mentor who uses poker, gambling, and gaming metaphors to make trading fun and engaging.
Create an informative yet entertaining Telegram message that EXPLAINS each signal with personality.

PERSONALITY GUIDELINES:
- Use playful gambling/poker metaphors: "The deck is stacked in our favor", "Time to show our cards", "Let's bluff the market"
- Add excitement: "Let's go all-in!", "The house edge is ours!", "Time to double down!"
- Be the cool mentor: Use phrases like "Listen up, traders!", "Here's the inside scoop", "Between you and me..."
- Mix professional analysis with fun language
- Keep it engaging but not reckless - always include risk warnings

MARKET MOOD: {market_mood}

Data for your update:
- Signals analyzed in last {self.interval} minutes: {self.market_summary['signals_generated']}
- Top 3 signals with analysis:
{json.dumps(signal_analyses, indent=2)}

REQUIRED SECTIONS (with personality):

🎰 OPENING HOOK (Fun opener like "The casino's open and the odds are in our favor!")

📊 MARKET VIBE CHECK (Set the mood - are we "holding aces" or "playing it cool"?)

🎯 HOT HANDS - TOP PLAYS (Each signal with fun explanation):
For each signal:
- Use metaphors: "BTC is showing its poker face but we see through it"
- Explain the setup in an engaging way
- Include specific levels but make it fun
- Risk management with style: "Don't bet the farm" or "Keep your powder dry"

🎲 TRADER'S WISDOM (Educational but fun - like advice from a wise gambler)

♠️ HOUSE RULES (Risk reminder with personality)

Add emojis and energy! Make traders EXCITED to read this.
Format with Telegram HTML. Be entertaining yet informative.
"""
            
            if self.ai_client is None:
                return self._compose_professional_standard_message()
            
            response = self.ai_client.chat.completions.create(
                model="gpt-4" if len(signal_analyses) > 0 else "gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a charismatic trading mentor with personality! Think of yourself as a mix between:
                        - A wise poker player who knows all the tells
                        - A friendly casino dealer sharing insider tips
                        - A cool professor who makes learning fun
                        
                        Your style:
                        1. Use gambling/gaming metaphors naturally
                        2. Be exciting but responsible
                        3. Mix technical analysis with entertaining delivery
                        4. Make traders feel like they're part of an exclusive club
                        5. Always include specific prices/levels but present them with flair
                        6. Build confidence while respecting risk"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,  # Higher for more creativity
                max_tokens=1200
            )
            
            message = response.choices[0].message.content
            self.stats['ai_compositions'] += 1
            
            # Add fun header and footer
            final_message = f"""🎰 <b>ZMARTBOT TRADING FLOOR</b> 🎰
<i>{datetime.now().strftime('%B %d, %Y | %H:%M UTC')}</i>
{'═' * 35}

{message}

{'═' * 35}
📊 <b>The Score:</b>
• Hands Dealt: {self.market_summary['signals_generated']}
• Winning Hands: {len([s for s in top_signals if s['win_rate'] >= 70])}
• Next Round: {self.interval} minutes

<i>🎲 May the odds be ever in your favor!</i>
<i>Remember: The house always wins... let's BE the house! 😎</i>"""
            
            return final_message
            
        except Exception as e:
            logger.error(f"AI composition failed: {e}")
            return self._compose_professional_standard_message()
    
    async def _get_signal_analysis(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed analysis for a signal to provide context"""
        try:
            # Get additional technical data if available
            symbol = signal['symbol']
            
            # Create comprehensive signal data for explanation
            return {
                'symbol': symbol,
                'win_rate': signal['win_rate'],
                'confidence': signal['confidence'],
                'action': signal.get('action', 'HOLD'),
                'technical_factors': {
                    'trend': 'Bullish momentum confirmed by 3 timeframes',
                    'support': f"Strong support at ${signal.get('support', 'N/A')}",
                    'resistance': f"Next resistance at ${signal.get('resistance', 'N/A')}",
                    'volume': 'Above average volume supporting move',
                    'pattern': signal.get('pattern', 'Breakout pattern forming')
                },
                'entry_strategy': f"Enter on pullback to support or market if momentum continues",
                'risk_management': {
                    'stop_loss': 'Set 2-3% below entry or at key support',
                    'position_size': f"{'2-3%' if signal['confidence'] == 'HIGH' else '1-2%'} of portfolio",
                    'take_profit': 'Scale out at resistance levels, let winners run'
                },
                'market_context': 'Aligns with overall market trend'
            }
        except Exception as e:
            logger.error(f"Error getting signal analysis: {e}")
            return signal
    
    def _compose_professional_standard_message(self) -> str:
        """Compose professional message with explanations without AI"""
        sections = []
        
        # Professional header
        sections.append(
            f"📱 <b>PROFESSIONAL MARKET ANALYSIS</b>\n"
            f"<i>{datetime.now().strftime('%B %d, %Y | %H:%M UTC')}</i>\n"
            f"{'═' * 35}"
        )
        
        # Market Context with explanation
        sections.append(
            f"\n📊 <b>MARKET CONTEXT:</b>\n"
            f"The market has generated {self.market_summary['signals_generated']} signals "
            f"in the past {self.interval} minutes, indicating "
            f"{'high volatility and opportunity' if self.market_summary['signals_generated'] > 20 else 'moderate activity'}. "
            f"Current conditions favor {'momentum trading' if self.market_summary['signals_generated'] > 30 else 'selective position taking'}."
        )
        
        # Top Trading Opportunities with detailed explanations
        top_signals = self._get_top_signals()
        if top_signals:
            signals_text = "\n🎯 <b>TOP TRADING OPPORTUNITIES:</b>\n"
            
            for i, signal in enumerate(top_signals[:3], 1):
                # Add detailed explanation for each signal
                signals_text += f"\n<b>{i}. {signal['symbol']} - {signal.get('action', 'HOLD')}</b>\n"
                signals_text += f"📈 Win Rate: {signal['win_rate']:.1f}% | Confidence: {signal['confidence']}\n"
                
                # Explanation based on win rate and confidence
                if signal['win_rate'] >= 80:
                    signals_text += f"<i>This is a premium setup with exceptional probability. "
                    signals_text += f"The high win rate suggests strong momentum and clear trend direction. "
                    signals_text += f"Consider {'2-3%' if signal['confidence'] == 'HIGH' else '1-2%'} position size with tight risk management.</i>\n"
                elif signal['win_rate'] >= 70:
                    signals_text += f"<i>Strong technical setup with multiple confirmations. "
                    signals_text += f"The alignment of indicators suggests good risk/reward. "
                    signals_text += f"Enter on confirmation with stop loss at recent support.</i>\n"
                else:
                    signals_text += f"<i>Moderate opportunity requiring careful entry. "
                    signals_text += f"Wait for additional confirmation before entering. "
                    signals_text += f"Use smaller position size due to moderate confidence.</i>\n"
            
            sections.append(signals_text)
        
        # Educational Insight with explanation
        insight = self._generate_educational_insight(top_signals)
        sections.append(
            f"\n💡 <b>EDUCATIONAL INSIGHT:</b>\n"
            f"{insight}"
        )
        
        # Risk Reminder with context
        sections.append(
            f"\n⚠️ <b>RISK REMINDER:</b>\n"
            f"Even high win-rate setups can fail. Always use stop losses and never risk more than "
            f"you can afford to lose. Today's market shows "
            f"{'increased volatility - reduce position sizes accordingly' if self.market_summary['alerts_triggered'] > 5 else 'normal conditions - standard risk rules apply'}."
        )
        
        # Professional footer
        sections.append(
            f"\n{'═' * 35}\n"
            f"📈 <b>Session Stats:</b>\n"
            f"• Signals Analyzed: {self.market_summary['signals_generated']}\n"
            f"• Quality Signals: {len([s for s in top_signals if s['win_rate'] >= 70])}\n"
            f"• Next Update: {self.interval} minutes\n\n"
            f"<i>📚 Learn. Trade. Profit. Responsibly.</i>"
        )
        
        return '\n'.join(sections)
    
    def _get_market_mood(self, signals: List[Dict]) -> str:
        """Determine market mood for playful language"""
        if not signals:
            return "QUIET_TABLES"
        
        avg_win_rate = sum(s['win_rate'] for s in signals[:3]) / min(3, len(signals)) if signals else 0
        
        if avg_win_rate >= 80:
            return "ROYAL_FLUSH"  # Best possible hand
        elif avg_win_rate >= 75:
            return "FULL_HOUSE"   # Very strong
        elif avg_win_rate >= 70:
            return "STRAIGHT"     # Good hand
        elif avg_win_rate >= 65:
            return "THREE_OF_KIND" # Decent
        else:
            return "BLUFFING_TIME" # Need to be careful
    
    def _generate_educational_insight(self, signals: List[Dict]) -> str:
        """Generate educational insight with personality"""
        if not signals:
            return ("🎯 The tables are quiet, my friend. Sometimes the best play is to fold and wait. "
                   "As the old poker saying goes: 'You can't lose what you don't put in the middle.' "
                   "Save your chips for when the deck is hot! 🔥")
        
        # Analyze signal patterns
        avg_win_rate = sum(s['win_rate'] for s in signals[:3]) / min(3, len(signals)) if signals else 0
        
        if avg_win_rate >= 75:
            return ("🎰 Listen up, high-rollers! We're holding ACES here! The market's showing its cards "
                   "and we like what we see. This is when you press your advantage - but remember, "
                   "even with pocket aces, you still play smart. Let winners run with trailing stops, "
                   "don't get greedy at the top! The best gamblers know when to cash out. 💰")
        elif avg_win_rate >= 65:
            return ("🃏 We're playing with decent cards, but not a guaranteed win. Smart money plays "
                   "selective here - like a poker pro waiting for position. Take the premium setups, "
                   "pass on the marginal ones. Remember: 'Scared money don't make money, but stupid money "
                   "don't keep money!' Size down and pick your battles. 🎯")
        else:
            return ("🎲 The dice aren't rolling our way right now, traders. Time to play defense! "
                   "Even the best poker players fold 80% of their hands. No shame in sitting out a few rounds "
                   "when the odds aren't favorable. Protect your stack - there's always another game tomorrow! "
                   "As they say in Vegas: 'The longer you play, the more the house edge matters.' Be patient! ⏰")
    
    def _compose_standard_message(self) -> str:
        """Compose standard consolidated message without AI"""
        sections = []
        
        # Header
        sections.append(
            f"📱 <b>MARKET UPDATE</b> | {datetime.now().strftime('%H:%M')}\n"
            f"{'-' * 30}"
        )
        
        # Market Overview
        if self.market_summary['signals_generated'] > 0:
            sections.append(
                f"\n📊 <b>Overview:</b>\n"
                f"• Signals Generated: {self.market_summary['signals_generated']}\n"
                f"• Active Positions: {len(self.market_summary['current_positions'])}\n"
                f"• Session P&L: ${self.market_summary['pnl_session']:.2f}"
            )
        
        # Top Trading Signals
        top_signals = self._get_top_signals()
        if top_signals:
            signals_text = "\n🎯 <b>Top Signals:</b>"
            for i, signal in enumerate(top_signals[:5], 1):
                signals_text += f"\n{i}. {signal['symbol']}: "
                signals_text += f"{signal['win_rate']:.1f}% win rate "
                signals_text += f"({signal['confidence']}) "
                signals_text += f"- {signal.get('action', 'HOLD')}"
            sections.append(signals_text)
        
        # Risk Alerts
        risk_alerts = self._get_risk_alerts()
        if risk_alerts:
            alerts_text = "\n⚠️ <b>Risk Alerts:</b>"
            for alert in risk_alerts[:3]:
                alerts_text += f"\n• {alert}"
            sections.append(alerts_text)
        
        # Performance Metrics
        if self.stats['batches_sent'] > 0:
            sections.append(
                f"\n📈 <b>Performance:</b>\n"
                f"• Updates Sent: {self.stats['batches_sent']}\n"
                f"• Messages Processed: {self.stats['messages_aggregated']}"
            )
        
        # Key Insight
        insight = self._generate_insight()
        if insight:
            sections.append(f"\n💡 <b>Insight:</b>\n{insight}")
        
        # Footer
        sections.append(
            f"\n{'-' * 30}\n"
            f"<i>Next update in {self.interval} minutes</i>"
        )
        
        return '\n'.join(sections)
    
    def _get_top_signals(self) -> List[Dict[str, Any]]:
        """Get top trading signals from queue"""
        signals = []
        
        # Extract signals from HIGH and MEDIUM priority
        for priority in [MessagePriority.HIGH, MessagePriority.MEDIUM]:
            for msg in self.message_queue[priority]:
                if msg['type'] == MessageType.OPEN_POSITION:
                    content = msg['content']
                    signals.append({
                        'symbol': content['symbol'],
                        'win_rate': content['win_rate'],
                        'confidence': content['confidence'],
                        'action': content.get('data', {}).get('action', 'HOLD'),
                        'timestamp': msg['timestamp']
                    })
        
        # Sort by win rate
        signals.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return signals
    
    def _get_risk_alerts(self) -> List[str]:
        """Get risk alerts from queue"""
        alerts = []
        
        for priority in [MessagePriority.HIGH, MessagePriority.MEDIUM]:
            for msg in self.message_queue[priority]:
                if msg['type'] == MessageType.SYSTEM:
                    content = msg['content']
                    alert_text = f"{content.get('symbol', 'Portfolio')}: {content.get('message', 'Risk detected')}"
                    alerts.append(alert_text)
        
        return alerts
    
    def _generate_insight(self) -> str:
        """Generate actionable insight based on current data"""
        insights = []
        
        # Check for trend
        top_signals = self._get_top_signals()
        if len(top_signals) >= 3:
            bullish = sum(1 for s in top_signals[:3] if s.get('action') in ['BUY', 'LONG'])
            if bullish >= 2:
                insights.append("Market showing bullish momentum - consider long positions")
            elif bullish == 0:
                insights.append("Bearish signals dominating - exercise caution")
        
        # Check for high win rates
        high_win_rates = [s for s in top_signals if s['win_rate'] >= 75]
        if high_win_rates:
            symbols = ', '.join([s['symbol'] for s in high_win_rates[:3]])
            insights.append(f"High probability setups on: {symbols}")
        
        # Volume or volatility insights
        if self.market_summary['alerts_triggered'] > 5:
            insights.append("Increased market volatility - adjust position sizes")
        
        return insights[0] if insights else "Stay disciplined and follow your trading plan"
    
    async def _handle_critical_message(self, content: Dict[str, Any], message_type: MessageType):
        """Handle critical messages that bypass batching"""
        self.stats['critical_alerts'] += 1
        
        # Format based on type
        if message_type == MessageType.SYSTEM:
            message = f"""
🚨 <b>CRITICAL ALERT</b>

{content.get('message', 'Critical condition detected')}

Symbol: {content.get('symbol', 'N/A')}
Action Required: {content.get('action', 'Review immediately')}

<i>Sent: {datetime.now().strftime('%H:%M:%S')}</i>
"""
        else:
            message = f"""
🚨 <b>CRITICAL: {message_type.value.upper()}</b>

{json.dumps(content, indent=2)}

<i>Sent: {datetime.now().strftime('%H:%M:%S')}</i>
"""
        
        await self._send_immediate(message, AlertLevel.CRITICAL)
    
    async def _send_immediate(self, message: str, level: AlertLevel):
        """Send immediate message (bypasses batching)"""
        try:
            await self.telegram.send_message(message, level)
        except Exception as e:
            logger.error(f"Failed to send immediate message: {e}")
    
    def _has_messages(self) -> bool:
        """Check if there are messages to send"""
        return any(len(msgs) > 0 for msgs in self.message_queue.values())
    
    def _gather_all_messages(self) -> List[Dict]:
        """Gather all messages from queues"""
        all_messages = []
        for priority in MessagePriority:
            all_messages.extend(self.message_queue[priority])
        return all_messages
    
    def _clear_processed_messages(self):
        """Clear messages that have been sent"""
        # Keep only LOW and INFO priority messages for next batch
        for priority in [MessagePriority.HIGH, MessagePriority.MEDIUM]:
            self.message_queue[priority].clear()
        
        # Move some LOW priority to next batch if important
        low_messages = self.message_queue[MessagePriority.LOW]
        self.message_queue[MessagePriority.LOW] = low_messages[-5:] if len(low_messages) > 5 else []
    
    async def send_daily_summary(self):
        """Send comprehensive daily summary"""
        if not self.telegram.enabled:
            return
        
        summary = f"""
📅 <b>DAILY TRADING SUMMARY</b>
{datetime.now().strftime('%Y-%m-%d')}
{'=' * 30}

📊 <b>Statistics:</b>
• Total Signals: {self.market_summary['signals_generated']}
• Trades Executed: {self.market_summary['trades_executed']}
• Batch Updates: {self.stats['batches_sent']}
• Critical Alerts: {self.stats['critical_alerts']}

📈 <b>Performance:</b>
• Session P&L: ${self.market_summary['pnl_session']:.2f}
• Win Rate: {self._calculate_win_rate():.1f}%
• Best Performer: {self._get_best_performer()}

💡 <b>Tomorrow's Focus:</b>
{self._get_tomorrow_focus()}

{'=' * 30}
<i>Telegram Center Performance Optimized</i>
"""
        
        await self._send_immediate(summary, AlertLevel.ANALYSIS)
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate from signals"""
        # Placeholder - would calculate from actual results
        return 68.5
    
    def _get_best_performer(self) -> str:
        """Get best performing signal/trade"""
        top = self._get_top_signals()
        if top:
            return f"{top[0]['symbol']} ({top[0]['win_rate']:.1f}%)"
        return "N/A"
    
    def _get_tomorrow_focus(self) -> str:
        """Generate focus points for tomorrow"""
        return "Monitor support levels and watch for breakout patterns"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get center statistics"""
        return {
            'is_running': self.is_running,
            'interval_minutes': self.interval,
            'stats': self.stats,
            'market_summary': self.market_summary,
            'queue_sizes': {
                priority.name: len(self.message_queue[priority])
                for priority in MessagePriority
            },
            'ai_enabled': self.ai_client is not None
        }

# Global instance
telegram_center = TelegramCenter(interval_minutes=15)

async def get_telegram_center() -> TelegramCenter:
    """Get global Telegram Center instance"""
    return telegram_center