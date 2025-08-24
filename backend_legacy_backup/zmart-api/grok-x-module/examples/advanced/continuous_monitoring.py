"""
Advanced Continuous Monitoring Example for Grok-X-Module
Demonstrates real-time monitoring and alert capabilities
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add the module to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.grok_x_engine import GrokXEngine, AnalysisRequest, AnalysisResult
from src.signals.signal_generator import SignalStrength, RiskLevel


class TradingAlertSystem:
    """Advanced trading alert system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_history = []
        self.signal_thresholds = {
            'min_confidence': 0.7,
            'min_strength': SignalStrength.MODERATE,
            'max_risk': RiskLevel.HIGH
        }
    
    async def process_analysis_result(self, result: AnalysisResult):
        """Process analysis result and generate alerts"""
        
        timestamp = datetime.now()
        
        print(f"\n📊 ANALYSIS UPDATE - {timestamp.strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # Display sentiment summary
        sentiment = result.sentiment_analysis
        print(f"Overall Sentiment: {sentiment.overall_sentiment:.3f} ({sentiment.sentiment_label})")
        print(f"Confidence: {sentiment.confidence:.3f}")
        print(f"Data Points: {len(result.social_data.tweets)} tweets, {len(result.social_data.users)} users")
        
        # Process trading signals
        high_priority_signals = []
        
        for signal in result.trading_signals:
            if self._is_high_priority_signal(signal):
                high_priority_signals.append(signal)
        
        if high_priority_signals:
            print(f"\n🚨 HIGH PRIORITY SIGNALS ({len(high_priority_signals)})")
            print("-" * 30)
            
            for signal in high_priority_signals:
                print(f"🎯 {signal.symbol}: {signal.signal_type.value}")
                print(f"   Strength: {signal.strength.value}")
                print(f"   Confidence: {signal.confidence:.3f}")
                print(f"   Risk: {signal.risk_level.value}")
                print(f"   Reasoning: {signal.reasoning[:100]}...")
                print()
                
                # Generate alert
                await self._generate_alert(signal, result)
        
        # Check for sentiment extremes
        if abs(sentiment.overall_sentiment) > 0.7 and sentiment.confidence > 0.8:
            sentiment_type = "EXTREMELY BULLISH" if sentiment.overall_sentiment > 0 else "EXTREMELY BEARISH"
            print(f"⚠️  {sentiment_type} SENTIMENT DETECTED!")
            print(f"   Sentiment Score: {sentiment.overall_sentiment:.3f}")
            print(f"   Confidence: {sentiment.confidence:.3f}")
            print()
        
        # Display market context
        social_metrics = result.market_context.get('social_metrics', {})
        print(f"📈 Market Activity: {social_metrics.get('total_engagement', 0):.0f} total engagement")
        print(f"👥 Verified Users: {social_metrics.get('verified_users', 0)}")
        print()
    
    def _is_high_priority_signal(self, signal) -> bool:
        """Check if signal meets high priority criteria"""
        
        strength_priority = {
            SignalStrength.VERY_STRONG: 4,
            SignalStrength.STRONG: 3,
            SignalStrength.MODERATE: 2,
            SignalStrength.WEAK: 1
        }
        
        risk_priority = {
            RiskLevel.LOW: 4,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 1
        }
        
        # Calculate priority score
        strength_score = strength_priority[signal.strength]
        risk_score = risk_priority[signal.risk_level]
        confidence_score = signal.confidence * 4
        
        priority_score = (strength_score + risk_score + confidence_score) / 3
        
        return (
            priority_score >= 3.0 and
            signal.confidence >= self.signal_thresholds['min_confidence'] and
            signal.risk_level != RiskLevel.CRITICAL
        )
    
    async def _generate_alert(self, signal, result: AnalysisResult):
        """Generate trading alert"""
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'symbol': signal.symbol,
            'signal_type': signal.signal_type.value,
            'strength': signal.strength.value,
            'confidence': signal.confidence,
            'risk_level': signal.risk_level.value,
            'reasoning': signal.reasoning,
            'sentiment_context': {
                'overall_sentiment': result.sentiment_analysis.overall_sentiment,
                'sentiment_confidence': result.sentiment_analysis.confidence
            },
            'expires_at': signal.expires_at.isoformat()
        }
        
        self.alert_history.append(alert)
        
        # In a real implementation, you would send this to:
        # - Webhook endpoints
        # - Email notifications
        # - Slack/Discord channels
        # - Trading bot APIs
        # - Database storage
        
        print(f"📢 ALERT GENERATED for {signal.symbol}")
        print(f"   Alert ID: {len(self.alert_history)}")
        print(f"   Priority: HIGH")
    
    def get_alert_summary(self) -> dict:
        """Get summary of generated alerts"""
        
        if not self.alert_history:
            return {'total_alerts': 0}
        
        # Count alerts by signal type
        signal_counts = {}
        for alert in self.alert_history:
            signal_type = alert['signal_type']
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
        
        # Count alerts by symbol
        symbol_counts = {}
        for alert in self.alert_history:
            symbol = alert['symbol']
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        return {
            'total_alerts': len(self.alert_history),
            'signal_distribution': signal_counts,
            'symbol_distribution': symbol_counts,
            'latest_alert': self.alert_history[-1]['timestamp'] if self.alert_history else None
        }


async def continuous_monitoring_example():
    """Demonstrate continuous monitoring capabilities"""
    
    print("🔄 Starting Continuous Monitoring Example")
    print("=" * 45)
    print("This will monitor cryptocurrency sentiment and generate real-time alerts.")
    print("Press Ctrl+C to stop monitoring.\n")
    
    # Symbols to monitor
    symbols = ["BTC", "ETH", "SOL", "ADA", "DOT"]
    
    # Initialize alert system
    alert_system = TradingAlertSystem()
    
    # Monitoring configuration
    monitoring_interval = 5  # minutes (reduced for demo)
    
    try:
        async with GrokXEngine() as engine:
            print(f"🎯 Monitoring symbols: {', '.join(symbols)}")
            print(f"⏱️  Update interval: {monitoring_interval} minutes")
            print(f"🚨 Alert thresholds: Confidence ≥ {alert_system.signal_thresholds['min_confidence']}")
            print()
            
            # Start continuous monitoring
            await engine.monitor_symbols_continuously(
                symbols=symbols,
                interval_minutes=monitoring_interval,
                callback=alert_system.process_analysis_result
            )
    
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")
    
    finally:
        # Display monitoring summary
        print("\n📊 MONITORING SUMMARY")
        print("=" * 25)
        
        summary = alert_system.get_alert_summary()
        print(f"Total Alerts Generated: {summary['total_alerts']}")
        
        if summary['total_alerts'] > 0:
            print("\nSignal Distribution:")
            for signal_type, count in summary['signal_distribution'].items():
                print(f"  {signal_type}: {count}")
            
            print("\nSymbol Distribution:")
            for symbol, count in summary['symbol_distribution'].items():
                print(f"  {symbol}: {count}")
            
            print(f"\nLatest Alert: {summary['latest_alert']}")


async def batch_analysis_example():
    """Demonstrate batch analysis of multiple symbols"""
    
    print("\n📦 Batch Analysis Example")
    print("=" * 30)
    
    # Multiple symbol groups
    symbol_groups = {
        'major_coins': ['BTC', 'ETH'],
        'altcoins': ['SOL', 'ADA', 'DOT'],
        'defi_tokens': ['UNI', 'AAVE', 'COMP']
    }
    
    results = {}
    
    async with GrokXEngine() as engine:
        for group_name, symbols in symbol_groups.items():
            print(f"\n🔍 Analyzing {group_name}: {', '.join(symbols)}")
            
            try:
                request = AnalysisRequest(
                    symbols=symbols,
                    time_window_hours=6,
                    max_tweets=30,
                    include_influencers=True,
                    analysis_depth="standard"
                )
                
                result = await engine.analyze_market_sentiment(request)
                results[group_name] = result
                
                # Quick summary
                sentiment = result.sentiment_analysis
                signals = result.trading_signals
                
                print(f"  Sentiment: {sentiment.overall_sentiment:.3f} ({sentiment.sentiment_label})")
                print(f"  Confidence: {sentiment.confidence:.3f}")
                print(f"  Signals: {len(signals)} generated")
                
                # Count signal types
                signal_counts = {}
                for signal in signals:
                    signal_type = signal.signal_type.value
                    signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
                
                if signal_counts:
                    signal_summary = ", ".join([f"{k}: {v}" for k, v in signal_counts.items()])
                    print(f"  Signal breakdown: {signal_summary}")
                
            except Exception as e:
                print(f"  ❌ Analysis failed: {e}")
                results[group_name] = None
    
    # Compare results across groups
    print("\n📊 CROSS-GROUP COMPARISON")
    print("-" * 30)
    
    for group_name, result in results.items():
        if result:
            sentiment = result.sentiment_analysis.overall_sentiment
            confidence = result.sentiment_analysis.confidence
            signal_count = len(result.trading_signals)
            
            print(f"{group_name:12} | Sentiment: {sentiment:6.3f} | Confidence: {confidence:.3f} | Signals: {signal_count}")


async def main():
    """Main function for advanced examples"""
    
    print("🚀 Grok-X-Module - Advanced Examples")
    print("=" * 40)
    print("Advanced usage examples including continuous monitoring and batch analysis.")
    print()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run batch analysis first
        await batch_analysis_example()
        
        print("\n" + "=" * 50)
        input("Press Enter to start continuous monitoring (or Ctrl+C to exit)...")
        
        # Run continuous monitoring
        await continuous_monitoring_example()
        
    except KeyboardInterrupt:
        print("\n👋 Examples completed!")
    
    except Exception as e:
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    # Run the advanced examples
    asyncio.run(main())

