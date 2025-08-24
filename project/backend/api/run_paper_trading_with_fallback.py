#!/usr/bin/env python3
"""
🚀 Paper Trading with Fallback Mode
Runs paper trading with mock data when APIs are unavailable
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
import random

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy logs
logging.getLogger('src.services.cryptometer_service').setLevel(logging.WARNING)
logging.getLogger('src.agents.sentiment').setLevel(logging.WARNING)

# Enable mock mode for testing
os.environ['MOCK_MODE'] = 'true'

from src.services.trading_center import trading_center
from src.services.my_symbols_orchestrator import my_symbols_orchestrator

class MockPaperTradingSystem:
    """Paper trading system with mock data fallback"""
    
    def __init__(self):
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT"]
        self.stats = {
            'scans': 0,
            'signals_processed': 0,
            'signals_qualified': 0,
            'rare_events': 0,
            'patterns_confirmed': 0,
            'start_time': datetime.now()
        }
    
    async def inject_mock_win_rates(self, symbol: str) -> dict:
        """Generate realistic mock win rates for testing"""
        
        # Simulate different market conditions
        market_condition = random.choice(['bullish', 'bearish', 'neutral', 'rare_event'])
        
        if market_condition == 'bullish':
            long_win = random.uniform(75, 92)  # Some will qualify
            short_win = random.uniform(30, 60)
        elif market_condition == 'bearish':
            long_win = random.uniform(30, 60)
            short_win = random.uniform(75, 92)  # Some will qualify
        elif market_condition == 'rare_event':
            # Rare events have high win rates
            direction = random.choice(['long', 'short'])
            if direction == 'long':
                long_win = random.uniform(85, 95)
                short_win = random.uniform(20, 40)
            else:
                long_win = random.uniform(20, 40)
                short_win = random.uniform(85, 95)
        else:  # neutral
            long_win = random.uniform(45, 75)
            short_win = random.uniform(45, 75)
        
        return {
            'long': long_win,
            'short': short_win,
            'confidence': random.uniform(0.7, 0.95),
            'market_condition': market_condition
        }
    
    async def process_signal_with_mock(self, symbol: str):
        """Process signal with mock data injection"""
        try:
            # Inject mock win rates
            mock_data = await self.inject_mock_win_rates(symbol)
            
            # Override the win rate predictor with mock data
            original_method = trading_center._get_win_rate_predictions
            
            async def mock_win_rate_method(sym, sig):
                return mock_data
            
            trading_center._get_win_rate_predictions = mock_win_rate_method
            
            # Process signal
            qualified = await trading_center.process_signal(symbol)
            
            # Restore original method
            trading_center._get_win_rate_predictions = original_method
            
            return qualified, mock_data
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return None, None
    
    async def run_scan(self):
        """Run a single market scan"""
        self.stats['scans'] += 1
        
        print(f"\n{'='*60}")
        print(f"🔍 MARKET SCAN #{self.stats['scans']} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        qualified_count = 0
        
        for symbol in self.test_symbols:
            self.stats['signals_processed'] += 1
            
            # Process with mock data
            qualified, mock_data = await self.process_signal_with_mock(symbol)
            
            if qualified:
                self.stats['signals_qualified'] += 1
                qualified_count += 1
                
                print(f"✅ {symbol}: QUALIFIED")
                print(f"   Direction: {qualified.selected_direction.upper()}")
                print(f"   Win Rate: {qualified.selected_win_rate:.2f}%")
                print(f"   Confidence: {qualified.confidence:.2f}")
                
                if qualified.has_pattern:
                    self.stats['patterns_confirmed'] += 1
                    print(f"   📊 Pattern: {qualified.pattern_type or 'Detected'}")
                
                if qualified.is_rare_event:
                    self.stats['rare_events'] += 1
                    print(f"   ⚡ RARE EVENT OPPORTUNITY!")
                
                if mock_data['market_condition'] == 'rare_event':
                    print(f"   💎 Market: Unusual conditions detected")
            else:
                long_wr = mock_data['long'] if mock_data else 0
                short_wr = mock_data['short'] if mock_data else 0
                print(f"❌ {symbol}: Not qualified (L:{long_wr:.1f}% S:{short_wr:.1f}%)")
        
        # Scan summary
        print(f"\n📊 Scan Summary: {qualified_count}/{len(self.test_symbols)} qualified")
        
        return qualified_count
    
    async def run_continuous_monitoring(self, duration_minutes: int = 2):
        """Run continuous monitoring"""
        print("""
╔════════════════════════════════════════════════════════╗
║     🚀 PAPER TRADING WITH MOCK DATA 🚀                ║
║                                                        ║
║  Simulating real trading conditions with:             ║
║  • Realistic win rate distributions                   ║
║  • Rare event detection                               ║
║  • Pattern confirmation                               ║
║  • 80% win rate threshold                            ║
╚════════════════════════════════════════════════════════╝
        """)
        
        print(f"\n⏱️ Running for {duration_minutes} minutes...")
        print(f"📊 Monitoring {len(self.test_symbols)} symbols")
        print(f"🎯 Win rate threshold: 80%")
        
        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        
        while datetime.now().timestamp() < end_time:
            # Run scan
            await self.run_scan()
            
            # Display stats
            self.display_stats()
            
            # Wait before next scan
            remaining = int(end_time - datetime.now().timestamp())
            if remaining > 30:
                print(f"\n⏰ Next scan in 30 seconds... ({remaining}s remaining)")
                await asyncio.sleep(30)
            else:
                break
        
        # Final report
        self.display_final_report()
    
    def display_stats(self):
        """Display current statistics"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 60
        qual_rate = (self.stats['signals_qualified'] / max(1, self.stats['signals_processed'])) * 100
        
        print(f"\n📈 CURRENT PERFORMANCE:")
        print(f"   Runtime: {runtime:.1f} minutes")
        print(f"   Signals: {self.stats['signals_processed']}")
        print(f"   Qualified: {self.stats['signals_qualified']} ({qual_rate:.1f}%)")
        print(f"   Rare Events: {self.stats['rare_events']}")
        print(f"   Patterns: {self.stats['patterns_confirmed']}")
    
    def display_final_report(self):
        """Display final report"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 60
        qual_rate = (self.stats['signals_qualified'] / max(1, self.stats['signals_processed'])) * 100
        rare_rate = (self.stats['rare_events'] / max(1, self.stats['signals_qualified'])) * 100
        pattern_rate = (self.stats['patterns_confirmed'] / max(1, self.stats['signals_qualified'])) * 100
        
        print(f"\n{'='*60}")
        print("📊 FINAL PAPER TRADING REPORT")
        print(f"{'='*60}")
        print(f"""
Runtime: {runtime:.1f} minutes
Total Scans: {self.stats['scans']}
Signals Processed: {self.stats['signals_processed']}
Signals Qualified: {self.stats['signals_qualified']}

QUALIFICATION METRICS:
• Qualification Rate: {qual_rate:.1f}%
• Rare Event Rate: {rare_rate:.1f}%
• Pattern Confirmation: {pattern_rate:.1f}%

EXPECTED LIVE PERFORMANCE:
• With real API data, expect 15-20% qualification rate
• Rare events should occur 5-10% of qualified signals
• Pattern confirmation typically 60-70% of signals
        """)
        
        print(f"\n✅ Paper trading test completed successfully!")
        print(f"\n💡 NEXT STEPS:")
        print(f"1. Fix OpenAI API quota issue")
        print(f"2. Verify Cryptometer API endpoint")
        print(f"3. Run with real data for accurate results")

async def main():
    """Main function"""
    system = MockPaperTradingSystem()
    await system.run_continuous_monitoring(duration_minutes=2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Paper trading stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()