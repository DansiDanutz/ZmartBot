"""Basic usage example for the Symbol Alerts System."""

import asyncio
import logging
from datetime import datetime, timedelta

from src.core.engine import AlertEngine
from src.core.models import AlertConfig, AlertCondition, AlertType, TimeFrame
from src.integrations.trading_bot_connector import TradingBotConnector, ZmartTradingBot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_example():
    """Basic example of using the Symbol Alerts System."""
    
    # Initialize the alert engine
    engine = AlertEngine()
    await engine.initialize()
    await engine.start()
    
    # Initialize trading bot connector
    trading_connector = TradingBotConnector()
    
    # Add a ZmartBot (using test credentials)
    zmart_bot = ZmartTradingBot(
        api_key="your-api-key",
        api_secret="your-secret",
        passphrase="your-passphrase",
        sandbox=True,  # Use sandbox for testing
        sub_account="ZmartBot"
    )
    await trading_connector.add_bot("zmart_main", zmart_bot)
    
    try:
        # Create a simple price alert
        price_alert = AlertConfig(
            user_id="demo_user",
            symbol="BTCUSDT",
            alert_type=AlertType.PRICE_ABOVE,
            conditions=[
                AlertCondition(
                    field="price",
                    operator=">",
                    value=50000,
                    timeframe=TimeFrame.M5
                )
            ],
            message="BTC price above $50,000!",
            webhook_url="https://your-webhook-url.com/alerts",
            cooldown_minutes=30
        )
        
        alert_id = await engine.add_alert(price_alert)
        logger.info(f"Created price alert: {alert_id}")
        
        # Create a technical indicator alert
        rsi_alert = AlertConfig(
            user_id="demo_user",
            symbol="ETHUSDT",
            alert_type=AlertType.RSI_OVERSOLD,
            conditions=[
                AlertCondition(
                    field="rsi",
                    operator="<",
                    value=30,
                    timeframe=TimeFrame.H1
                )
            ],
            message="ETH RSI oversold on 1H timeframe",
            max_triggers=5,
            cooldown_minutes=60
        )
        
        alert_id2 = await engine.add_alert(rsi_alert)
        logger.info(f"Created RSI alert: {alert_id2}")
        
        # Create a multi-condition alert
        complex_alert = AlertConfig(
            user_id="demo_user",
            symbol="SOLUSDT",
            alert_type=AlertType.CUSTOM,
            conditions=[
                AlertCondition(
                    field="rsi",
                    operator=">",
                    value=45,
                    timeframe=TimeFrame.M15
                ),
                AlertCondition(
                    field="ema_12",
                    operator="cross_above",
                    value="ema_26",  # Cross above EMA26
                    timeframe=TimeFrame.M15
                ),
                AlertCondition(
                    field="volume",
                    operator=">",
                    value=1000000,  # Volume threshold
                    timeframe=TimeFrame.M15
                )
            ],
            message="SOL bullish setup: RSI > 45, EMA cross, high volume",
            expires_at=datetime.now() + timedelta(days=7),
            cooldown_minutes=120
        )
        
        alert_id3 = await engine.add_alert(complex_alert)
        logger.info(f"Created complex alert: {alert_id3}")
        
        # List all alerts
        alerts = await engine.list_alerts("demo_user")
        logger.info(f"Total alerts for user: {len(alerts)}")
        
        # Get system metrics
        metrics = await engine.get_system_metrics()
        logger.info(f"System metrics: {metrics}")
        
        # Test webhook
        webhook_result = await engine.test_webhook("https://httpbin.org/post")
        logger.info(f"Webhook test result: {webhook_result}")
        
        # Simulate running for a short time
        logger.info("System running... (press Ctrl+C to stop)")
        await asyncio.sleep(60)  # Run for 1 minute
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        # Cleanup
        await trading_connector.shutdown()
        await engine.stop()
        logger.info("System stopped")


async def advanced_example():
    """Advanced example with LLM gating and multi-timeframe analysis."""
    
    from src.alerts.advanced_triggers import AdvancedTriggerEngine
    
    # Initialize advanced trigger engine
    advanced_config = {
        "features": {
            "enable_llm_gating": True,
            "enable_orderbook": True,
            "enable_derivatives": True
        },
        "pre_signal": {
            "alignment_needed": 6,  # Require 6+ alignment points
            "fresh_events_needed": 2  # Require 2+ fresh events
        }
    }
    
    trigger_engine = AdvancedTriggerEngine(advanced_config)
    
    # This would be integrated with the main alert engine
    # for processing market data and generating advanced signals
    
    logger.info("Advanced trigger engine initialized")
    logger.info("Features enabled:")
    logger.info(f"- LLM Gating: {advanced_config['features']['enable_llm_gating']}")
    logger.info(f"- Orderbook Analysis: {advanced_config['features']['enable_orderbook']}")
    logger.info(f"- Derivatives Analysis: {advanced_config['features']['enable_derivatives']}")


async def webhook_example():
    """Example of handling webhook alerts in a trading bot."""
    
    from fastapi import FastAPI, Request
    import uvicorn
    
    app = FastAPI(title="Trading Bot Webhook Handler")
    
    @app.post("/webhook/alerts")
    async def handle_alert(request: Request):
        """Handle incoming alert webhooks."""
        try:
            alert_data = await request.json()
            
            # Extract alert information
            trigger = alert_data.get("alert_trigger", {})
            symbol = trigger.get("symbol")
            alert_type = trigger.get("alert_type")
            price = trigger.get("trigger_price")
            direction = "BUY" if "bull" in str(trigger.get("labels", [])) else "SELL"
            
            logger.info(f"Received alert: {symbol} - {alert_type} - {direction} @ {price}")
            
            # Implement your trading logic here
            if symbol and price:
                # Example: Execute trade based on alert
                trade_result = await execute_trade(symbol, direction, price)
                logger.info(f"Trade executed: {trade_result}")
            
            return {"status": "success", "message": "Alert processed"}
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            return {"status": "error", "message": str(e)}
    
    async def execute_trade(symbol: str, direction: str, price: float):
        """Execute trade based on alert."""
        # This is where you'd integrate with your trading bot
        # For example, using the ZmartTradingBot
        
        trade_size = 10  # Small test size (10 USDT)
        
        return {
            "symbol": symbol,
            "direction": direction,
            "size": trade_size,
            "price": price,
            "status": "executed"
        }
    
    # This would run as a separate service
    # uvicorn.run(app, host="0.0.0.0", port=8080)
    logger.info("Webhook handler example created")


if __name__ == "__main__":
    print("Symbol Alerts System - Usage Examples")
    print("=====================================")
    print()
    print("1. Basic Example - Simple alerts and trading bot integration")
    print("2. Advanced Example - LLM gating and multi-timeframe analysis")
    print("3. Webhook Example - Handling alerts in a trading bot")
    print()
    
    choice = input("Select example (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(basic_example())
    elif choice == "2":
        asyncio.run(advanced_example())
    elif choice == "3":
        asyncio.run(webhook_example())
    else:
        print("Invalid choice. Running basic example...")
        asyncio.run(basic_example())

