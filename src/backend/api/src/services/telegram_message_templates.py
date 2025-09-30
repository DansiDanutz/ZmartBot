#!/usr/bin/env python3
"""
📱 Telegram Message Templates
Professional, organized templates for each alert type
Ensures consistent, clear communication
"""

from typing import Dict, Any
from datetime import datetime

class MessageTemplates:
    """
    Organized templates for all Telegram message types
    Each template ensures consistent formatting and information hierarchy
    """
    
    @staticmethod
    def open_position_template(data: Dict[str, Any]) -> str:
        """
        Template for OPEN POSITION alerts
        Clear structure: Signal → Reasoning → Numbers → Strategy → Confidence
        """
        symbol = data.get('symbol', 'N/A')
        action = data.get('action', 'LONG')
        action_emoji = "🟢" if action == 'LONG' else "🔴"
        
        return f"""
{action_emoji} <b>POSITION OPENED</b> {action_emoji}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📍 ASSET:</b> {symbol}
<b>📊 ACTION:</b> {action}
<b>⏰ TIME:</b> {datetime.now().strftime('%H:%M:%S UTC')}

<b>🎯 REASONING (Why Now?):</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ <b>Technical:</b> {data.get('technical_reason', 'Breakout confirmed on multiple timeframes')}
2️⃣ <b>Momentum:</b> {data.get('momentum_reason', 'Strong volume supporting the move')}
3️⃣ <b>Risk/Reward:</b> {data.get('rr_reason', f"Favorable {data.get('risk_reward', '1:3')} ratio identified")}

<b>📈 POSITION DETAILS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>
Entry Price:    ${data.get('entry_price', 0):.4f}
Stop Loss:      ${data.get('stop_loss', 0):.4f} ({data.get('risk_percent', 2)}%)
Target 1:       ${data.get('target1', 0):.4f} (+{data.get('target1_percent', 0):.1f}%)
Target 2:       ${data.get('target2', 0):.4f} (+{data.get('target2_percent', 0):.1f}%)
Position Size:  {data.get('position_size', '2%')} of portfolio
Leverage:       {data.get('leverage', '1x')}
</code>

<b>🎲 STRATEGY:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• <b>Entry:</b> {data.get('entry_strategy', 'Market order at breakout confirmation')}
• <b>Exit Plan:</b> {data.get('exit_plan', 'Take 50% at T1, trail remainder')}
• <b>Invalidation:</b> {data.get('invalidation', 'Close below stop loss level')}

<b>📊 CONFIDENCE METRICS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Win Rate: {data.get('win_rate', 0):.1f}%
• Confidence: {data.get('confidence', 'HIGH')}
• Signal Strength: {data.get('signal_strength', '8/10')}

💭 <i>{data.get('playful_message', "The deck is stacked in our favor! Let's play this hand smart! 🃏")}</i>

<b>#Trade{data.get('trade_id', 'XXX')} #{symbol} #{'Long' if action == 'LONG' else 'Short'}</b>
"""

    @staticmethod
    def target_hit_template(data: Dict[str, Any]) -> str:
        """
        Template for TARGET HIT alerts
        Structure: Achievement → Numbers → Action Taken → Next Steps
        """
        symbol = data.get('symbol', 'N/A')
        target_num = data.get('target_number', 1)
        
        # Default values with newlines (outside f-string)
        default_action = '''• Closed 50% of position
• Moved stop to breakeven
• Trailing stop activated for remainder'''
        default_targets = '''• Target 2: $48,500 (+8.5%)
• Target 3: $52,000 (+15.2%)'''
        
        return f"""
🎯 <b>TARGET {target_num} REACHED!</b> 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📍 ASSET:</b> {symbol}
<b>✅ TARGET:</b> Level {target_num}
<b>⏰ TIME:</b> {datetime.now().strftime('%H:%M:%S UTC')}

<b>💰 PROFIT LOCKED:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>
Entry Price:     ${data.get('entry_price', 0):.4f}
Target Price:    ${data.get('target_price', 0):.4f}
Profit:          +{data.get('profit_percent', 0):.2f}%
Dollar Gain:     +${data.get('dollar_gain', 0):.2f}
Time in Trade:   {data.get('trade_duration', 'N/A')}
</code>

<b>🎯 ACTION TAKEN:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('action_taken', default_action)}

<b>📊 NEXT TARGETS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('next_targets', default_targets)}

<b>💡 WHY WE TOOK PROFITS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('profit_reasoning', 'Key resistance level reached. Smart money books profits at predetermined levels - no greed, just green!')}

💭 <i>{data.get('playful_message', "Ka-ching! 💰 The house always wins when we stick to the plan!")}</i>

<b>#Trade{data.get('trade_id', 'XXX')} #{symbol} #Profit</b>
"""

    @staticmethod
    def close_position_template(data: Dict[str, Any]) -> str:
        """
        Template for CLOSE POSITION alerts
        Structure: Result → Final Numbers → Reasoning → Lessons → Stats
        """
        symbol = data.get('symbol', 'N/A')
        pnl = data.get('pnl_percent', 0)
        is_profit = pnl > 0
        result_emoji = "✅" if is_profit else "❌"
        
        return f"""
{result_emoji} <b>POSITION CLOSED</b> {result_emoji}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📍 ASSET:</b> {symbol}
<b>📊 RESULT:</b> {"PROFIT" if is_profit else "LOSS"}
<b>⏰ TIME:</b> {datetime.now().strftime('%H:%M:%S UTC')}

<b>📈 FINAL NUMBERS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>
Entry Price:     ${data.get('entry_price', 0):.4f}
Exit Price:      ${data.get('exit_price', 0):.4f}
P&L:             {'+' if is_profit else ''}{pnl:.2f}%
Dollar Result:   {'$' if is_profit else '-$'}{abs(data.get('pnl_dollar', 0)):.2f}
Max Profit:      +{data.get('max_profit', 0):.2f}%
Max Drawdown:    -{data.get('max_drawdown', 0):.2f}%
</code>

<b>🎯 CLOSE REASONING:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('close_reason', 'Target reached' if is_profit else 'Stop loss triggered - risk management executed perfectly')}

<b>📊 TRADE STATISTICS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Duration: {data.get('duration', 'N/A')}
• Risk/Reward Achieved: {data.get('rr_achieved', 'N/A')}
• Win Rate Impact: {data.get('winrate_impact', 'N/A')}

<b>📚 LESSON:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('lesson', 'Perfect execution of the trading plan!' if is_profit else 'Losses are part of the game. Risk management kept it small.')}

💭 <i>{data.get('playful_message', "Winner winner, chicken dinner! 🍗" if is_profit else "Can't win them all, but we live to trade another day! 💪")}</i>

<b>#Trade{data.get('trade_id', 'XXX')} #{symbol} #Closed</b>
"""

    @staticmethod
    def rare_opportunity_template(data: Dict[str, Any]) -> str:
        """
        Template for RARE OPPORTUNITY alerts
        Structure: Urgency → Confluence → Setup → Historical → Action Plan
        """
        symbol = data.get('symbol', 'N/A')
        
        return f"""
🌟⚡ <b>RARE OPPORTUNITY ALERT</b> ⚡🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🚨 URGENCY: {data.get('urgency', 'HIGH')}</b>
<b>📍 ASSET:</b> {symbol}
<b>⏰ WINDOW:</b> {data.get('time_window', 'Next 2-4 hours')}

<b>🎯 WHY THIS IS SPECIAL:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('why_special', 'Perfect storm confluence - happens < 5% of the time!')}

<b>✨ CONFLUENCE FACTORS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ <b>Technical:</b> {data.get('technical', 'Major pattern completion')}
✅ <b>Volume:</b> {data.get('volume', 'Institutional accumulation detected')}
✅ <b>Sentiment:</b> {data.get('sentiment', 'Extreme bullish shift')}
✅ <b>Momentum:</b> {data.get('momentum', 'Breaking multi-month resistance')}
✅ <b>Timing:</b> {data.get('timing', 'Optimal market conditions aligned')}

<b>📊 THE SETUP:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>
Entry Zone:      ${data.get('entry_min', 0):.4f} - ${data.get('entry_max', 0):.4f}
Stop Loss:       ${data.get('stop_loss', 0):.4f} (-{data.get('risk_percent', 3)}%)
Target 1:        ${data.get('target1', 0):.4f} (+{data.get('target1_percent', 10)}%)
Target 2:        ${data.get('target2', 0):.4f} (+{data.get('target2_percent', 25)}%)
Moon Shot:       ${data.get('moon_target', 0):.4f} (+{data.get('moon_percent', 50)}%)
</code>

<b>📈 HISTORICAL CONTEXT:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('historical', 'Last 3 occurrences: +45%, +62%, +38% within 7 days')}

<b>🎲 RECOMMENDED ACTION:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Position Size: {data.get('position_size', '3-5% (larger than usual)')}
• Entry Strategy: {data.get('entry_strategy', 'Scale in aggressively on dips')}
• Risk Note: {data.get('risk_note', 'Still use stops - rare ≠ risk-free!')}

💭 <i>{data.get('playful_message', "This is it! The hand we've been waiting for! Time to press our edge! 🚀🎰")}</i>

<b>⚠️ DISCLAIMER:</b> High conviction doesn't mean guaranteed. Trade responsibly!

<b>#RareOpportunity #{symbol} #HighConviction</b>
"""

    @staticmethod
    def daily_review_template(data: Dict[str, Any]) -> str:
        """
        Template for DAILY REVIEW
        Structure: Summary → Trades → Performance → Lessons → Tomorrow
        """
        pnl = data.get('total_pnl', 0)
        pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        
        # Default values with newlines (outside f-string)
        default_best = '''1. BTC: +5.2%
2. ETH: +3.8%
3. SOL: +2.1%'''
        default_worst = '''1. XRP: -1.8%
2. ADA: -1.2%'''
        default_lessons = '''• Patience in entry paid off
• Quick stops saved capital
• Trend following worked well today'''
        default_watchlist = '''🎯 BTC - Watching $45,500 breakout
🎯 ETH - Support bounce at $2,300
🎯 SOL - Continuation above $100'''
        
        return f"""
📅 <b>DAILY TRADING REVIEW</b> 📅
{datetime.now().strftime('%B %d, %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 DAILY SUMMARY:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{pnl_emoji} <b>P&L:</b> ${pnl:.2f} ({'+' if pnl > 0 else ''}{data.get('pnl_percent', 0):.2f}%)
📈 <b>Win Rate:</b> {data.get('win_rate', 0):.1f}%
🎯 <b>Trades Taken:</b> {data.get('total_trades', 0)}
✅ <b>Winners:</b> {data.get('winning_trades', 0)}
❌ <b>Losers:</b> {data.get('losing_trades', 0)}

<b>🏆 BEST PERFORMERS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('best_trades', default_best)}

<b>📉 WORST PERFORMERS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('worst_trades', default_worst)}

<b>📈 OPEN POSITIONS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('open_positions', 'No open positions')}

<b>💡 KEY LESSONS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('lessons', default_lessons)}

<b>🔮 TOMORROW'S WATCHLIST:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('watchlist', default_watchlist)}

<b>📊 CUMULATIVE STATS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Week TD: ${data.get('week_pnl', 0):.2f}
• Month TD: ${data.get('month_pnl', 0):.2f}
• Win Streak: {data.get('win_streak', 0)} days

💭 <i>{data.get('motivational', "Another day at the office! Consistency beats luck every time! 💪" if pnl > 0 else "Rough day at the tables, but we'll bounce back tomorrow! 🎲")}</i>

<b>#DailyReview #TradingResults</b>
"""

    @staticmethod
    def high_score_symbol_template(data: Dict[str, Any]) -> str:
        """
        Template for HIGH SCORE SYMBOL
        Structure: Winner → Scores → Timeframe Analysis → Strategy → Gift Note
        """
        symbol = data.get('symbol', 'N/A')
        
        return f"""
🏆 <b>HIGH SCORE SYMBOL</b> 🏆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>👑 TODAY'S CHAMPION:</b> {symbol}
<b>🎯 OVERALL SCORE:</b> {data.get('score', 0)}/100
<b>⏰ ANALYSIS TIME:</b> {datetime.now().strftime('%H:%M UTC')}

<b>📊 SCORING BREAKDOWN:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Cryptometer: {data.get('cryptometer_score', 0)}/100
• KingFisher: {data.get('kingfisher_score', 0)}/100
• RiskMetric: {data.get('riskmetric_score', 0)}/100
• Sentiment: {data.get('sentiment_score', 0)}/100

<b>⚡ SHORT TERM (1H-4H):</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• <b>Signal:</b> {data.get('short_signal', 'LONG')}
• <b>Win Rate:</b> {data.get('short_winrate', 0)}%
• <b>Key Level:</b> ${data.get('short_level', 0):.2f}
• <b>Analysis:</b> {data.get('short_analysis', 'Bullish momentum building')}

<b>📈 MEDIUM TERM (1D-3D):</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• <b>Signal:</b> {data.get('medium_signal', 'STRONG LONG')}
• <b>Win Rate:</b> {data.get('medium_winrate', 0)}%
• <b>Key Level:</b> ${data.get('medium_level', 0):.2f}
• <b>Analysis:</b> {data.get('medium_analysis', 'Trend acceleration expected')}

<b>🎯 LONG TERM (1W-1M):</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• <b>Signal:</b> {data.get('long_signal', 'ACCUMULATE')}
• <b>Win Rate:</b> {data.get('long_winrate', 0)}%
• <b>Key Level:</b> ${data.get('long_level', 0):.2f}
• <b>Analysis:</b> {data.get('long_analysis', 'Major uptrend intact')}

<b>🎲 TRADING STRATEGY:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• <b>Best Timeframe:</b> {data.get('best_timeframe', 'Medium (1D-3D)')}
• <b>Entry:</b> {data.get('entry_strategy', 'Scale in on dips to support')}
• <b>Stop Loss:</b> {data.get('stop_strategy', 'Below key support level')}
• <b>Targets:</b> {data.get('target_strategy', 'Take profits at resistance levels')}
• <b>Position Size:</b> {data.get('position_size', '2-3% of portfolio')}

<b>💎 WHY IT'S #1:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('why_top', 'Perfect confluence across all indicators and timeframes')}

🎁 <i>This premium analysis is our gift to you! Normally $50 value - FREE for our community!</i>

⏰ <i>Next High Score Symbol in 8 hours</i>

<b>#{symbol} #HighScore #FreeAnalysis</b>
"""

    @staticmethod
    def market_update_template(data: Dict[str, Any]) -> str:
        """
        Template for 15-minute MARKET UPDATE
        Structure: Mood → Overview → Top Signals → Insight → Next Update
        """
        mood = data.get('market_mood', 'NEUTRAL')
        mood_emoji = {
            'BULLISH': '🚀',
            'BEARISH': '🐻',
            'NEUTRAL': '⚖️',
            'VOLATILE': '🎢'
        }.get(mood, '📊')
        
        return f"""
{mood_emoji} <b>MARKET UPDATE</b> {mood_emoji}
{datetime.now().strftime('%H:%M UTC')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎰 MARKET MOOD:</b> {mood}
{data.get('mood_description', 'Markets showing mixed signals')}

<b>📊 15-MIN OVERVIEW:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Signals Generated: {data.get('signals_count', 0)}
• Quality Signals: {data.get('quality_signals', 0)}
• Active Positions: {data.get('active_positions', 0)}
• Session P&L: ${data.get('session_pnl', 0):.2f}

<b>🎯 TOP OPPORTUNITIES:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('top_signals', 'No high-quality signals this period')}

<b>⚠️ RISK ALERTS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('risk_alerts', '✅ No significant risks detected')}

<b>💡 TRADING WISDOM:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('wisdom', "Patience is a trader's best friend")}

<i>Next update in 15 minutes...</i>

<b>#MarketUpdate #TradingSignals</b>
"""

    @staticmethod
    def whale_alert_template(data: Dict[str, Any]) -> str:
        """
        Template for WHALE ALERT
        Structure: Alert → Transaction → Impact → Action
        """
        return f"""
🐋 <b>WHALE ALERT</b> 🐋
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📍 ASSET:</b> {data.get('symbol', 'N/A')}
<b>🚨 TYPE:</b> {data.get('alert_type', 'Large Transfer')}
<b>⏰ TIME:</b> {datetime.now().strftime('%H:%M:%S UTC')}

<b>💰 TRANSACTION DETAILS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Amount: {data.get('amount', 'N/A')} {data.get('symbol', '')}
• USD Value: ${data.get('usd_value', 0):,.0f}
• From: {data.get('from_address', 'Unknown')[:8]}...
• To: {data.get('to_address', 'Unknown')[:8]}...
• Type: {data.get('transaction_type', 'Transfer')}

<b>📊 MARKET IMPACT:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('impact', 'Monitoring for price movement')}

<b>🎯 SUGGESTED ACTION:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('action', 'Watch for follow-through')}

<b>#WhaleAlert #{data.get('symbol', 'CRYPTO')}</b>
"""

    @staticmethod
    def stop_loss_hit_template(data: Dict[str, Any]) -> str:
        """
        Template for STOP LOSS HIT
        Structure: Alert → Loss Details → Risk Management → Next Steps
        """
        symbol = data.get('symbol', 'N/A')
        
        return f"""
🛑 <b>STOP LOSS TRIGGERED</b> 🛑
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📍 ASSET:</b> {symbol}
<b>⏰ TIME:</b> {datetime.now().strftime('%H:%M:%S UTC')}

<b>📊 LOSS DETAILS:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>
Entry Price:     ${data.get('entry_price', 0):.4f}
Stop Price:      ${data.get('stop_price', 0):.4f}
Loss:            -{data.get('loss_percent', 0):.2f}%
Dollar Loss:     -${data.get('dollar_loss', 0):.2f}
</code>

<b>✅ RISK MANAGEMENT:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Loss was within planned risk (max {data.get('max_risk', 2)}%)
• Capital preserved for next opportunity
• No revenge trading - stick to the plan

<b>📚 LESSON:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data.get('lesson', 'Stops are insurance - small loss, big protection!')}

💭 <i>Cut losses short, let winners run. This is the way! 💪</i>

<b>#StopLoss #{symbol} #RiskManagement</b>
"""

    @staticmethod
    def format_message(template_type: str, data: Dict[str, Any]) -> str:
        """
        Route to appropriate template based on message type
        """
        templates = {
            'open_position': MessageTemplates.open_position_template,
            'target_hit': MessageTemplates.target_hit_template,
            'close_position': MessageTemplates.close_position_template,
            'rare_opportunity': MessageTemplates.rare_opportunity_template,
            'daily_review': MessageTemplates.daily_review_template,
            'high_score': MessageTemplates.high_score_symbol_template,
            'market_update': MessageTemplates.market_update_template,
            'whale_alert': MessageTemplates.whale_alert_template,
            'stop_loss': MessageTemplates.stop_loss_hit_template
        }
        
        template_func = templates.get(template_type)
        if template_func:
            return template_func(data)
        else:
            return f"⚠️ Unknown template type: {template_type}"

# Example usage data structures for reference
TEMPLATE_DATA_EXAMPLES = {
    'open_position': {
        'symbol': 'BTC',
        'action': 'LONG',
        'entry_price': 45000,
        'stop_loss': 44000,
        'target1': 46500,
        'target2': 48000,
        'target1_percent': 3.3,
        'target2_percent': 6.7,
        'risk_percent': 2.2,
        'position_size': '3%',
        'leverage': '2x',
        'win_rate': 82.5,
        'confidence': 'HIGH',
        'signal_strength': '9/10',
        'technical_reason': 'Breakout above key resistance with volume',
        'momentum_reason': 'RSI divergence confirmed, MACD crossover',
        'rr_reason': 'Risk/Reward ratio of 1:3.5 identified',
        'entry_strategy': 'Market buy on confirmed breakout',
        'exit_plan': 'Take 50% at target 1, trail remainder',
        'invalidation': 'Close below $44,000 support',
        'playful_message': "We've got pocket aces! Time to play them right! 🃏",
        'trade_id': '001'
    },
    
    'target_hit': {
        'symbol': 'ETH',
        'target_number': 1,
        'entry_price': 2300,
        'target_price': 2450,
        'profit_percent': 6.5,
        'dollar_gain': 1500,
        'trade_duration': '18 hours',
        'action_taken': '• Closed 50% of position\n• Stop moved to breakeven\n• Trailing stop activated',
        'next_targets': '• Target 2: $2,550 (+10.9%)\n• Target 3: $2,700 (+17.4%)',
        'profit_reasoning': 'Major resistance at $2,450. Taking profits into strength!',
        'playful_message': "Cha-ching! 💰 First target down, more to come!",
        'trade_id': '002'
    }
}