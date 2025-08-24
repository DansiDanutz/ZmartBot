"""
Basic Usage Example for Grok-X-Module
Demonstrates how to use the module for cryptocurrency sentiment analysis and signal generation
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add the module to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.grok_x_engine import GrokXEngine, AnalysisRequest


async def basic_sentiment_analysis():
    """Basic sentiment analysis example"""
    
    print("🚀 Starting Grok-X-Module Basic Example")
    print("=" * 50)
    
    # Define symbols to analyze
    symbols = ["BTC", "ETH", "SOL"]
    
    # Create analysis request
    request = AnalysisRequest(
        symbols=symbols,
        keywords=["bitcoin", "ethereum", "solana", "crypto"],
        time_window_hours=12,
        max_tweets=50,
        include_influencers=True,
        analysis_depth="standard"
    )
    
    try:
        # Initialize and run analysis
        async with GrokXEngine() as engine:
            print(f"📊 Analyzing sentiment for: {', '.join(symbols)}")
            print(f"⏰ Time window: {request.time_window_hours} hours")
            print(f"🐦 Max tweets: {request.max_tweets}")
            print()
            
            # Perform analysis
            result = await engine.analyze_market_sentiment(request)
            
            # Display results
            print("📈 SENTIMENT ANALYSIS RESULTS")
            print("-" * 30)
            print(f"Overall Sentiment: {result.sentiment_analysis.overall_sentiment:.3f}")
            print(f"Sentiment Label: {result.sentiment_analysis.sentiment_label}")
            print(f"Confidence: {result.sentiment_analysis.confidence:.3f}")
            print(f"Processing Time: {result.processing_time_seconds:.2f} seconds")
            print()
            
            # Display key insights
            print("🔍 KEY INSIGHTS:")
            for insight in result.sentiment_analysis.key_insights:
                print(f"  • {insight}")
            print()
            
            # Display market implications
            print("💡 MARKET IMPLICATIONS:")
            print(f"  {result.sentiment_analysis.market_implications}")
            print()
            
            # Display trading signals
            print("🎯 TRADING SIGNALS")
            print("-" * 20)
            
            if result.trading_signals:
                for signal in result.trading_signals:
                    print(f"Symbol: {signal.symbol}")
                    print(f"  Signal: {signal.signal_type.value} ({signal.strength.value})")
                    print(f"  Confidence: {signal.confidence:.3f}")
                    print(f"  Risk Level: {signal.risk_level.value}")
                    print(f"  Reasoning: {signal.reasoning}")
                    print(f"  Expires: {signal.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
            else:
                print("  No trading signals generated")
            
            # Display social metrics
            print("📱 SOCIAL MEDIA METRICS")
            print("-" * 25)
            print(f"Tweets Analyzed: {len(result.social_data.tweets)}")
            print(f"Unique Users: {len(result.social_data.users)}")
            
            if result.social_data.tweets:
                avg_engagement = sum(t.engagement_score for t in result.social_data.tweets) / len(result.social_data.tweets)
                print(f"Average Engagement: {avg_engagement:.3f}")
            
            verified_users = sum(1 for u in result.social_data.users.values() if u.verified)
            print(f"Verified Users: {verified_users}")
            print()
            
            # Save results to file
            output_file = f"analysis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            await engine.save_analysis_result(result, output_file)
            print(f"💾 Results saved to: {output_file}")
            
            # Display performance metrics
            metrics = engine.get_performance_metrics()
            print("\n⚡ ENGINE PERFORMANCE")
            print("-" * 20)
            print(f"Total Analyses: {metrics['total_analyses']}")
            print(f"Success Rate: {metrics['success_rate']:.1%}")
            print(f"Average Processing Time: {metrics['average_processing_time']:.2f}s")
            print(f"Cache Hit Rate: {metrics['cache_hit_rate']:.1%}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    
    print("\n✅ Analysis completed successfully!")
    return True


async def quick_sentiment_check():
    """Quick sentiment check example"""
    
    print("\n🔍 Quick Sentiment Check")
    print("=" * 25)
    
    symbols = ["BTC", "ETH"]
    
    try:
        async with GrokXEngine() as engine:
            sentiment_data = await engine.get_quick_sentiment(symbols)
            
            print(f"Quick sentiment for {', '.join(symbols)}:")
            print(f"  Sentiment: {sentiment_data['overall_sentiment']:.3f}")
            print(f"  Confidence: {sentiment_data['confidence']:.3f}")
            print(f"  Signals Generated: {sentiment_data['signal_count']}")
            
    except Exception as e:
        print(f"❌ Quick sentiment check failed: {e}")


async def main():
    """Main example function"""
    
    print("🤖 Grok-X-Module - Advanced Crypto Trading Signals")
    print("=" * 55)
    print("This example demonstrates basic usage of the Grok-X-Module")
    print("for cryptocurrency sentiment analysis and signal generation.")
    print()
    
    # Run basic sentiment analysis
    success = await basic_sentiment_analysis()
    
    if success:
        # Run quick sentiment check
        await quick_sentiment_check()
    
    print("\n" + "=" * 55)
    print("Example completed! Check the generated JSON file for detailed results.")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())

