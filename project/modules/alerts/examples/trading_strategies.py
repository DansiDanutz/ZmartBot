"""Trading strategies examples using the Symbol Alerts System."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.core.engine import AlertEngine
from src.core.models import AlertConfig, AlertCondition, AlertType, TimeFrame
from src.integrations.trading_bot_connector import TradingBotConnector, ZmartTradingBot

logger = logging.getLogger(__name__)


class TradingStrategy:
    """Base class for trading strategies."""
    
    def __init__(self, name: str, engine: AlertEngine, trading_connector: TradingBotConnector):
        self.name = name
        self.engine = engine
        self.trading_connector = trading_connector
        self.active_alerts: List[str] = []
        self.positions: Dict[str, Dict] = {}
    
    async def setup_alerts(self):
        """Setup alerts for this strategy."""
        raise NotImplementedError
    
    async def cleanup_alerts(self):
        """Remove all alerts for this strategy."""
        for alert_id in self.active_alerts:
            await self.engine.remove_alert(alert_id)
        self.active_alerts.clear()


class EMAScalpingStrategy(TradingStrategy):
    """EMA crossover scalping strategy with multi-timeframe confirmation."""
    
    def __init__(self, engine: AlertEngine, trading_connector: TradingBotConnector):
        super().__init__("EMA Scalping", engine, trading_connector)
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.trade_size = 10  # 10 USDT per trade
    
    async def setup_alerts(self):
        """Setup EMA crossover alerts with multi-timeframe confirmation."""
        
        for symbol in self.symbols:
            # 5-minute EMA crossover (entry signal)
            entry_alert = AlertConfig(
                user_id="ema_scalping",
                symbol=symbol,
                alert_type=AlertType.CUSTOM,
                conditions=[
                    AlertCondition(
                        field="ema_12",
                        operator="cross_above",
                        value="ema_26",
                        timeframe=TimeFrame.M5
                    ),
                    AlertCondition(
                        field="rsi",
                        operator=">",
                        value=40,  # Avoid oversold conditions
                        timeframe=TimeFrame.M5
                    ),
                    AlertCondition(
                        field="volume",
                        operator=">",
                        value=500000,  # Require decent volume
                        timeframe=TimeFrame.M5
                    )
                ],
                message=f"{symbol} EMA bullish crossover - LONG entry",
                webhook_url="http://localhost:8080/webhook/ema-long",
                cooldown_minutes=15
            )
            
            alert_id = await self.engine.add_alert(entry_alert)
            self.active_alerts.append(alert_id)
            
            # Bearish crossover
            exit_alert = AlertConfig(
                user_id="ema_scalping",
                symbol=symbol,
                alert_type=AlertType.CUSTOM,
                conditions=[
                    AlertCondition(
                        field="ema_12",
                        operator="cross_below",
                        value="ema_26",
                        timeframe=TimeFrame.M5
                    )
                ],
                message=f"{symbol} EMA bearish crossover - EXIT long",
                webhook_url="http://localhost:8080/webhook/ema-exit",
                cooldown_minutes=5
            )
            
            alert_id = await self.engine.add_alert(exit_alert)
            self.active_alerts.append(alert_id)
        
        logger.info(f"Setup {len(self.active_alerts)} alerts for EMA Scalping strategy")


class RSIMeanReversionStrategy(TradingStrategy):
    """RSI mean reversion strategy for oversold/overbought conditions."""
    
    def __init__(self, engine: AlertEngine, trading_connector: TradingBotConnector):
        super().__init__("RSI Mean Reversion", engine, trading_connector)
        self.symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
        self.trade_size = 15  # 15 USDT per trade
    
    async def setup_alerts(self):
        """Setup RSI mean reversion alerts."""
        
        for symbol in self.symbols:
            # Oversold entry (long)
            oversold_alert = AlertConfig(
                user_id="rsi_mean_reversion",
                symbol=symbol,
                alert_type=AlertType.RSI_OVERSOLD,
                conditions=[
                    AlertCondition(
                        field="rsi",
                        operator="<",
                        value=25,  # Deeply oversold
                        timeframe=TimeFrame.H1
                    ),
                    AlertCondition(
                        field="price",
                        operator=">",
                        value="sma_50",  # Above long-term support
                        timeframe=TimeFrame.H1
                    )
                ],
                message=f"{symbol} RSI oversold - LONG entry opportunity",
                webhook_url="http://localhost:8080/webhook/rsi-long",
                cooldown_minutes=60,
                max_triggers=3
            )
            
            alert_id = await self.engine.add_alert(oversold_alert)
            self.active_alerts.append(alert_id)
            
            # Overbought exit
            overbought_alert = AlertConfig(
                user_id="rsi_mean_reversion",
                symbol=symbol,
                alert_type=AlertType.RSI_OVERBOUGHT,
                conditions=[
                    AlertCondition(
                        field="rsi",
                        operator=">",
                        value=75,  # Overbought
                        timeframe=TimeFrame.H1
                    )
                ],
                message=f"{symbol} RSI overbought - EXIT long",
                webhook_url="http://localhost:8080/webhook/rsi-exit",
                cooldown_minutes=30
            )
            
            alert_id = await self.engine.add_alert(overbought_alert)
            self.active_alerts.append(alert_id)
        
        logger.info(f"Setup {len(self.active_alerts)} alerts for RSI Mean Reversion strategy")


class BreakoutStrategy(TradingStrategy):
    """Breakout strategy using Bollinger Bands and volume confirmation."""
    
    def __init__(self, engine: AlertEngine, trading_connector: TradingBotConnector):
        super().__init__("Breakout Strategy", engine, trading_connector)
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
        self.trade_size = 20  # 20 USDT per trade
    
    async def setup_alerts(self):
        """Setup breakout alerts with volume confirmation."""
        
        for symbol in self.symbols:
            # Bullish breakout
            bullish_breakout = AlertConfig(
                user_id="breakout_strategy",
                symbol=symbol,
                alert_type=AlertType.CUSTOM,
                conditions=[
                    AlertCondition(
                        field="price",
                        operator=">",
                        value="bb_upper",  # Price above upper Bollinger Band
                        timeframe=TimeFrame.M15
                    ),
                    AlertCondition(
                        field="volume",
                        operator=">",
                        value=1000000,  # High volume confirmation
                        timeframe=TimeFrame.M15
                    ),
                    AlertCondition(
                        field="rsi",
                        operator="<",
                        value=80,  # Not extremely overbought
                        timeframe=TimeFrame.M15
                    )
                ],
                message=f"{symbol} Bullish breakout - LONG entry",
                webhook_url="http://localhost:8080/webhook/breakout-long",
                cooldown_minutes=30
            )
            
            alert_id = await self.engine.add_alert(bullish_breakout)
            self.active_alerts.append(alert_id)
            
            # Bearish breakdown
            bearish_breakdown = AlertConfig(
                user_id="breakout_strategy",
                symbol=symbol,
                alert_type=AlertType.CUSTOM,
                conditions=[
                    AlertCondition(
                        field="price",
                        operator="<",
                        value="bb_lower",  # Price below lower Bollinger Band
                        timeframe=TimeFrame.M15
                    ),
                    AlertCondition(
                        field="volume",
                        operator=">",
                        value=1000000,  # High volume confirmation
                        timeframe=TimeFrame.M15
                    ),
                    AlertCondition(
                        field="rsi",
                        operator=">",
                        value=20,  # Not extremely oversold
                        timeframe=TimeFrame.M15
                    )
                ],
                message=f"{symbol} Bearish breakdown - SHORT entry",
                webhook_url="http://localhost:8080/webhook/breakout-short",
                cooldown_minutes=30
            )
            
            alert_id = await self.engine.add_alert(bearish_breakdown)
            self.active_alerts.append(alert_id)
        
        logger.info(f"Setup {len(self.active_alerts)} alerts for Breakout strategy")


class MultiTimeframeStrategy(TradingStrategy):
    """Advanced multi-timeframe strategy with LLM validation."""
    
    def __init__(self, engine: AlertEngine, trading_connector: TradingBotConnector):
        super().__init__("Multi-Timeframe", engine, trading_connector)
        self.symbols = ["BTCUSDT", "ETHUSDT"]
        self.trade_size = 25  # 25 USDT per trade
    
    async def setup_alerts(self):
        """Setup multi-timeframe alerts with strict conditions."""
        
        for symbol in self.symbols:
            # Strong bullish setup
            bullish_setup = AlertConfig(
                user_id="multi_timeframe",
                symbol=symbol,
                alert_type=AlertType.CUSTOM,
                conditions=[
                    # 4H trend confirmation
                    AlertCondition(
                        field="ema_12",
                        operator=">",
                        value="ema_26",
                        timeframe=TimeFrame.H4
                    ),
                    AlertCondition(
                        field="price",
                        operator=">",
                        value="sma_50",
                        timeframe=TimeFrame.H4
                    ),
                    # 1H momentum
                    AlertCondition(
                        field="macd",
                        operator="cross_above",
                        value="macd_signal",
                        timeframe=TimeFrame.H1
                    ),
                    # 15M entry
                    AlertCondition(
                        field="rsi",
                        operator=">",
                        value=45,
                        timeframe=TimeFrame.M15
                    ),
                    AlertCondition(
                        field="rsi",
                        operator="<",
                        value=65,
                        timeframe=TimeFrame.M15
                    )
                ],
                message=f"{symbol} Multi-timeframe bullish setup - HIGH CONFIDENCE LONG",
                webhook_url="http://localhost:8080/webhook/mtf-long",
                cooldown_minutes=120,
                max_triggers=2
            )
            
            alert_id = await self.engine.add_alert(bullish_setup)
            self.active_alerts.append(alert_id)
        
        logger.info(f"Setup {len(self.active_alerts)} alerts for Multi-Timeframe strategy")


class StrategyManager:
    """Manages multiple trading strategies."""
    
    def __init__(self):
        self.strategies: List[TradingStrategy] = []
        self.engine = None
        self.trading_connector = None
    
    async def initialize(self):
        """Initialize the strategy manager."""
        # Initialize alert engine
        self.engine = AlertEngine()
        await self.engine.initialize()
        await self.engine.start()
        
        # Initialize trading connector
        self.trading_connector = TradingBotConnector()
        
        # Add ZmartBot for testing
        zmart_bot = ZmartTradingBot(
            api_key="683f7d9ed0a5f40001f23621",  # Test credentials
            api_secret="30cfc70e-a027-4007-a7f9-1fa4b959094f",
            passphrase="your-passphrase",
            sandbox=True,
            sub_account="ZmartBot"
        )
        await self.trading_connector.add_bot("zmart_main", zmart_bot)
        
        logger.info("Strategy manager initialized")
    
    async def add_strategy(self, strategy_class):
        """Add a strategy to the manager."""
        strategy = strategy_class(self.engine, self.trading_connector)
        await strategy.setup_alerts()
        self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy.name}")
    
    async def remove_strategy(self, strategy_name: str):
        """Remove a strategy from the manager."""
        for i, strategy in enumerate(self.strategies):
            if strategy.name == strategy_name:
                await strategy.cleanup_alerts()
                del self.strategies[i]
                logger.info(f"Removed strategy: {strategy_name}")
                return
        logger.warning(f"Strategy not found: {strategy_name}")
    
    async def get_status(self):
        """Get status of all strategies."""
        status = {
            "total_strategies": len(self.strategies),
            "strategies": []
        }
        
        for strategy in self.strategies:
            strategy_status = {
                "name": strategy.name,
                "active_alerts": len(strategy.active_alerts),
                "positions": len(strategy.positions)
            }
            status["strategies"].append(strategy_status)
        
        # Get system metrics
        metrics = await self.engine.get_system_metrics()
        status["system_metrics"] = metrics.dict()
        
        return status
    
    async def shutdown(self):
        """Shutdown all strategies and cleanup."""
        for strategy in self.strategies:
            await strategy.cleanup_alerts()
        
        await self.trading_connector.shutdown()
        await self.engine.stop()
        
        logger.info("Strategy manager shutdown complete")


async def run_strategy_demo():
    """Run a demo of multiple trading strategies."""
    
    manager = StrategyManager()
    await manager.initialize()
    
    try:
        # Add different strategies
        await manager.add_strategy(EMAScalpingStrategy)
        await manager.add_strategy(RSIMeanReversionStrategy)
        await manager.add_strategy(BreakoutStrategy)
        await manager.add_strategy(MultiTimeframeStrategy)
        
        # Get initial status
        status = await manager.get_status()
        logger.info(f"Strategy manager status: {status}")
        
        # Run for a demo period
        logger.info("Running strategies... (press Ctrl+C to stop)")
        await asyncio.sleep(300)  # Run for 5 minutes
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Trading Strategies Demo")
    print("======================")
    print()
    print("This demo will setup multiple trading strategies:")
    print("1. EMA Scalping - Quick EMA crossover trades")
    print("2. RSI Mean Reversion - Oversold/overbought trades")
    print("3. Breakout Strategy - Bollinger Band breakouts")
    print("4. Multi-Timeframe - Advanced multi-TF analysis")
    print()
    
    input("Press Enter to start the demo...")
    
    asyncio.run(run_strategy_demo())

