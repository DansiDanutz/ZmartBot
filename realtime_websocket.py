#!/usr/bin/env python3
"""
Real-time WebSocket Integration for ZmartBot
Enhances existing system with live data streaming
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
import threading
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class RealtimeDataStream:
    """WebSocket integration for existing ZmartBot system"""
    
    def __init__(self):
        self.session = requests.Session()
        self.callbacks = {}
        self.running = False
        self.price_cache = {}
        self.signal_cache = {}
        
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for specific events"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def update_price_cache(self, symbol: str, price: float, timestamp: datetime):
        """Update local price cache"""
        self.price_cache[symbol] = {
            'price': price,
            'timestamp': timestamp,
            'bid': price * 0.9995,  # Simulated bid
            'ask': price * 1.0005,  # Simulated ask
        }
        
        # Trigger price callbacks
        if 'price_update' in self.callbacks:
            for callback in self.callbacks['price_update']:
                callback(symbol, self.price_cache[symbol])
    
    def update_signal_cache(self, symbol: str, signal_data: Dict):
        """Update signal cache with new data"""
        self.signal_cache[symbol] = {
            'composite_score': signal_data.get('score', 50),
            'action': signal_data.get('action', 'HOLD'),
            'timestamp': datetime.now(),
            'confidence': signal_data.get('confidence', 0.5)
        }
        
        # Trigger signal callbacks
        if 'signal_update' in self.callbacks:
            for callback in self.callbacks['signal_update']:
                callback(symbol, self.signal_cache[symbol])
    
    async def connect_binance_stream(self, symbols: List[str]):
        """Connect to Binance WebSocket for price data"""
        # Convert symbols to lowercase for Binance WebSocket
        streams = [f"{symbol.lower()}@trade" for symbol in symbols]
        stream_url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"
        
        try:
            async with websockets.connect(stream_url) as websocket:
                logger.info(f"Connected to Binance WebSocket")
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30)
                        data = json.loads(message)
                        
                        if 'data' in data:
                            trade_data = data['data']
                            symbol = trade_data['s']  # Symbol in uppercase
                            price = float(trade_data['p'])  # Price
                            
                            self.update_price_cache(symbol, price, datetime.now())
                            
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        await websocket.ping()
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
    
    async def simulate_signal_updates(self, symbols: List[str]):
        """Simulate signal updates for existing strategy"""
        while self.running:
            for symbol in symbols:
                # Get current price
                price = self.price_cache.get(symbol, {}).get('price', 0)
                
                if price > 0:
                    # Try to get real signal from backend
                    try:
                        resp = self.session.get(
                            f"{BASE_URL}/api/signal-center/aggregation/{symbol}",
                            timeout=5
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            signal_data = {
                                'score': data.get('composite_score', 50),
                                'action': 'BUY' if data.get('composite_score', 50) > 60 else 'SELL' if data.get('composite_score', 50) < 40 else 'HOLD',
                                'confidence': data.get('composite_score', 50) / 100
                            }
                        else:
                            # Fallback to simulated signals
                            signal_data = self.generate_simulated_signal(symbol, price)
                    except:
                        # Fallback to simulated signals
                        signal_data = self.generate_simulated_signal(symbol, price)
                    
                    self.update_signal_cache(symbol, signal_data)
            
            await asyncio.sleep(10)  # Update signals every 10 seconds
    
    def generate_simulated_signal(self, symbol: str, price: float) -> Dict:
        """Generate simulated trading signal"""
        import random
        
        # Simple momentum-based signal
        if symbol not in self.price_cache or 'last_price' not in self.price_cache[symbol]:
            momentum = 0
        else:
            last_price = self.price_cache[symbol].get('last_price', price)
            momentum = (price - last_price) / last_price * 100
        
        # Calculate score based on momentum
        base_score = 50
        if momentum > 0.5:
            base_score = 60 + min(momentum * 10, 30)
        elif momentum < -0.5:
            base_score = 40 - min(abs(momentum) * 10, 30)
        
        # Add some randomness
        score = max(0, min(100, base_score + random.uniform(-5, 5)))
        
        # Store last price for next calculation
        if symbol in self.price_cache:
            self.price_cache[symbol]['last_price'] = price
        
        return {
            'score': score,
            'action': 'BUY' if score > 65 else 'SELL' if score < 35 else 'HOLD',
            'confidence': abs(score - 50) / 50
        }
    
    async def monitor_positions(self):
        """Monitor open positions and trigger alerts"""
        while self.running:
            try:
                # Load current positions from existing system
                with open('trading_strategy_state.json', 'r') as f:
                    state = json.load(f)
                    positions = state.get('positions', [])
                
                for position in positions:
                    if position.get('status') == 'OPEN':
                        symbol = position['symbol']
                        entry_price = position['entry_price']
                        
                        # Get current price
                        current_price = self.price_cache.get(symbol, {}).get('price', entry_price)
                        
                        # Calculate P&L
                        pnl_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        # Check for important events
                        if pnl_pct <= -position.get('stop_loss', 1.5):
                            self.trigger_event('stop_loss', {
                                'symbol': symbol,
                                'entry_price': entry_price,
                                'current_price': current_price,
                                'pnl_pct': pnl_pct
                            })
                        elif pnl_pct >= position.get('take_profit', 3.0):
                            self.trigger_event('take_profit', {
                                'symbol': symbol,
                                'entry_price': entry_price,
                                'current_price': current_price,
                                'pnl_pct': pnl_pct
                            })
                
            except Exception as e:
                logger.error(f"Error monitoring positions: {e}")
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    def trigger_event(self, event_type: str, data: Dict):
        """Trigger event callbacks"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
    
    async def start_streaming(self, symbols: List[str]):
        """Start all streaming tasks"""
        self.running = True
        
        # Create tasks for different data streams
        tasks = [
            self.connect_binance_stream(symbols),
            self.simulate_signal_updates(symbols),
            self.monitor_positions()
        ]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
    
    def start(self, symbols: List[str]):
        """Start WebSocket streaming in background thread"""
        def run_async():
            asyncio.run(self.start_streaming(symbols))
        
        self.thread = threading.Thread(target=run_async, daemon=True)
        self.thread.start()
        logger.info("WebSocket streaming started")
    
    def stop(self):
        """Stop WebSocket streaming"""
        self.running = False
        logger.info("WebSocket streaming stopped")
    
    def get_live_data(self, symbol: str) -> Dict:
        """Get latest live data for a symbol"""
        return {
            'price': self.price_cache.get(symbol, {}),
            'signal': self.signal_cache.get(symbol, {}),
            'timestamp': datetime.now().isoformat()
        }

class LiveTradingEnhancer:
    """Enhance existing trading strategy with live data"""
    
    def __init__(self, data_stream: RealtimeDataStream):
        self.data_stream = data_stream
        self.register_callbacks()
    
    def register_callbacks(self):
        """Register callback functions for events"""
        self.data_stream.register_callback('price_update', self.on_price_update)
        self.data_stream.register_callback('signal_update', self.on_signal_update)
        self.data_stream.register_callback('stop_loss', self.on_stop_loss)
        self.data_stream.register_callback('take_profit', self.on_take_profit)
    
    def on_price_update(self, symbol: str, price_data: Dict):
        """Handle price updates"""
        logger.info(f"Price Update - {symbol}: ${price_data['price']:.2f}")
    
    def on_signal_update(self, symbol: str, signal_data: Dict):
        """Handle signal updates"""
        action = signal_data['action']
        score = signal_data['composite_score']
        
        if action == 'BUY' and score > 75:
            logger.info(f"🚀 STRONG BUY Signal - {symbol}: Score {score}/100")
        elif action == 'SELL' and score < 25:
            logger.info(f"🔻 STRONG SELL Signal - {symbol}: Score {score}/100")
    
    def on_stop_loss(self, data: Dict):
        """Handle stop loss alerts"""
        logger.warning(f"⚠️ STOP LOSS Alert - {data['symbol']}: P&L {data['pnl_pct']:.2f}%")
    
    def on_take_profit(self, data: Dict):
        """Handle take profit alerts"""
        logger.info(f"✅ TAKE PROFIT Alert - {data['symbol']}: P&L {data['pnl_pct']:.2f}%")

def main():
    """Test WebSocket streaming"""
    print("\n🌐 ZmartBot Real-time WebSocket Integration")
    print("=" * 60)
    
    # Initialize data stream
    stream = RealtimeDataStream()
    enhancer = LiveTradingEnhancer(stream)
    
    # Symbols to monitor
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
    
    print(f"\n📡 Starting real-time data stream for:")
    for symbol in symbols:
        print(f"  • {symbol}")
    
    # Start streaming
    stream.start(symbols)
    
    print("\n🔄 Streaming live data...")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Display live data
        while True:
            import time
            time.sleep(5)
            
            print(f"\n--- Live Data Update ({datetime.now().strftime('%H:%M:%S')}) ---")
            for symbol in symbols:
                data = stream.get_live_data(symbol)
                price = data['price'].get('price', 0) if data['price'] else 0
                signal = data['signal'].get('action', 'N/A') if data['signal'] else 'N/A'
                score = data['signal'].get('composite_score', 0) if data['signal'] else 0
                
                if price > 0:
                    print(f"{symbol}: ${price:.2f} | Signal: {signal} ({score:.0f}/100)")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping data stream...")
        stream.stop()
        print("✅ WebSocket integration stopped")

if __name__ == "__main__":
    main()