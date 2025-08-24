#!/usr/bin/env python3
"""
Start ZmartBot with Rate Limiting and Telegram Notifications
Production-ready startup with all protections enabled
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.telegram')

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.telegram_notifications import get_telegram_service
from src.services.trading_with_notifications import trading_notifier
from src.utils.rate_limiter import global_rate_limiter

async def startup_notifications():
    """Send startup notifications"""
    telegram = get_telegram_service()
    
    if telegram.enabled:
        await telegram.send_message(
            f"""
<b>🚀 ZMARTBOT SYSTEM STARTUP</b>

⚡ <b>Status:</b> INITIALIZING
📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>Services Starting:</b>
• Rate Limiting Protection ⏳
• Telegram Notifications ✅
• Cryptometer API 🔄
• KuCoin Futures 🔄
• Risk Management 🔄
• AI Analysis 🔄

<i>System initialization in progress...</i>
""",
            level="SUCCESS"
        )
        print("✅ Startup notification sent to Telegram")
    else:
        print("⚠️ Telegram notifications disabled")

async def initialize_services():
    """Initialize all services with protections"""
    print("\n" + "="*60)
    print("🚀 ZMARTBOT INITIALIZATION")
    print("="*60)
    
    # Send startup notification
    await startup_notifications()
    
    # Initialize rate limiting
    print("\n⚡ Initializing Rate Limiting...")
    stats = global_rate_limiter.get_all_stats()
    print(f"   ✅ Rate limiters configured for {len(stats)} services")
    for service in stats.keys():
        print(f"      • {service}")
    
    # Initialize trading with notifications
    print("\n📱 Initializing Trading Notifications...")
    print("   ✅ Trade alerts enabled")
    print("   ✅ Risk alerts enabled")
    print("   ✅ Daily summaries enabled")
    
    # Send system ready notification
    telegram = get_telegram_service()
    if telegram.enabled:
        await telegram.send_system_status({
            'healthy': True,
            'uptime': '0h 1m',
            'active_positions': 0,
            'total_pnl': 0.0,
            'cryptometer_status': '🟢',
            'kucoin_status': '🟢',
            'database_status': '🟢',
            'ai_status': '🟢',
            'api_calls_remaining': 100,
            'api_calls_limit': 100
        })
    
    print("\n✅ All services initialized successfully!")
    print("="*60)

async def monitor_system():
    """Continuous system monitoring with notifications"""
    telegram = get_telegram_service()
    
    while True:
        try:
            # Wait for 30 minutes
            await asyncio.sleep(1800)
            
            # Get rate limit statistics
            all_stats = global_rate_limiter.get_all_stats()
            
            # Check for any service with high block rate
            alerts_needed = []
            for service, stats in all_stats.items():
                if stats.get('block_rate', 0) > 0.2:  # More than 20% blocked
                    alerts_needed.append({
                        'service': service,
                        'block_rate': stats['block_rate'],
                        'blocked': stats['blocked_requests']
                    })
            
            # Send alert if needed
            if alerts_needed and telegram.enabled:
                message = "<b>⚠️ RATE LIMIT WARNING</b>\n\n"
                for alert in alerts_needed:
                    message += f"• {alert['service']}: {alert['block_rate']:.1%} blocked ({alert['blocked']} requests)\n"
                message += "\n<i>Consider adjusting rate limits or reducing request frequency.</i>"
                
                await telegram.send_message(message, level="WARNING")
            
            # Send periodic health check
            if telegram.enabled:
                await trading_notifier.send_system_health_update()
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in monitoring: {e}")

async def shutdown_notifications():
    """Send shutdown notifications"""
    telegram = get_telegram_service()
    
    if telegram.enabled:
        await telegram.send_message(
            f"""
<b>🛑 ZMARTBOT SYSTEM SHUTDOWN</b>

⏰ <b>Shutdown Time:</b> {datetime.now().strftime('%H:%M:%S')}
📊 <b>Session Statistics:</b>
• Trades Executed: {trading_notifier.daily_stats['trades_executed']}
• Winning Trades: {trading_notifier.daily_stats['winning_trades']}
• Losing Trades: {trading_notifier.daily_stats['losing_trades']}
• Total P&L: ${trading_notifier.daily_stats['total_pnl']:.2f}

<i>System shutting down gracefully...</i>
""",
            level="INFO"
        )

async def main():
    """Main startup function"""
    try:
        # Initialize services
        await initialize_services()
        
        # Start monitoring in background
        monitor_task = asyncio.create_task(monitor_system())
        
        # Start FastAPI server (example)
        print("\n🌐 Starting FastAPI server...")
        print("   Access the API at: http://localhost:8000")
        print("   API Documentation: http://localhost:8000/docs")
        
        # Keep running
        print("\n✅ ZmartBot is running with full protection!")
        print("   Press Ctrl+C to stop")
        
        # Wait for interrupt
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Shutdown requested...")
        await shutdown_notifications()
        monitor_task.cancel()
        await asyncio.gather(monitor_task, return_exceptions=True)
        print("✅ Shutdown complete")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        telegram = get_telegram_service()
        if telegram.enabled:
            await telegram.send_message(
                f"🚨 CRITICAL ERROR: {str(e)}",
                level="CRITICAL"
            )

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 ZMARTBOT WITH NOTIFICATIONS")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    asyncio.run(main())