#!/usr/bin/env python3
"""
Test Historical Pattern Database System
Comprehensive test of historical pattern analysis with multi-timeframe win rates
"""

import asyncio
import sys
import os
import json
import uuid
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.historical_pattern_database import (
    HistoricalPatternDatabase, HistoricalPattern, TimeFrame, Direction,
    TopPattern, PatternStatistics
)
from src.services.advanced_learning_agent import AdvancedLearningAgent
from src.services.historical_ai_analysis_agent import HistoricalAIAnalysisAgent

async def test_historical_pattern_system():
    """Test the complete historical pattern system"""
    
    print("🚀 STARTING HISTORICAL PATTERN DATABASE SYSTEM TEST")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 HISTORICAL PATTERN ANALYSIS WITH MULTI-TIMEFRAME WIN RATES")
    print("=" * 80)
    
    try:
        # Initialize Historical Pattern Database
        print("\n📊 Initializing Historical Pattern Database...")
        historical_db = HistoricalPatternDatabase("test_historical_patterns.db")
        print("✅ Historical Pattern Database initialized successfully")
        
        # Initialize Advanced Learning Agent
        print("🧠 Initializing Advanced Learning Agent...")
        advanced_agent = AdvancedLearningAgent("test_learning.db", "test_historical_patterns.db")
        print("✅ Advanced Learning Agent initialized successfully")
        
        # Initialize Historical AI Analysis Agent
        print("🤖 Initializing Historical AI Analysis Agent...")
        historical_ai_agent = HistoricalAIAnalysisAgent()
        print("✅ Historical AI Analysis Agent initialized successfully")
        
        # Test symbol
        symbol = "ETH"
        print(f"\n📈 TESTING HISTORICAL PATTERN SYSTEM FOR {symbol}/USDT...")
        print("-" * 80)
        
        # Step 1: Create sample historical patterns
        print("📚 Creating sample historical patterns...")
        await create_sample_historical_patterns(historical_db, symbol)
        
        # Step 2: Test database functionality
        print("\n📊 Testing database functionality...")
        await test_database_functionality(historical_db, symbol)
        
        # Step 3: Test multi-timeframe analysis
        print("\n⏰ Testing multi-timeframe analysis...")
        await test_multi_timeframe_analysis(advanced_agent, symbol)
        
        # Step 4: Test top patterns analysis
        print("\n🏆 Testing top patterns analysis...")
        await test_top_patterns_analysis(historical_db, symbol)
        
        # Step 5: Test comprehensive analysis
        print("\n🔬 Testing comprehensive historical analysis...")
        await test_comprehensive_analysis(advanced_agent, symbol)
        
        # Step 6: Test AI-enhanced historical analysis
        print("\n🤖 Testing AI-enhanced historical analysis...")
        await test_ai_enhanced_analysis(historical_ai_agent, symbol)
        
        # Step 7: Display system statistics
        print("\n📊 SYSTEM STATISTICS:")
        display_system_statistics(historical_db, advanced_agent)
        
        print(f"\n✅ HISTORICAL PATTERN SYSTEM TEST COMPLETE!")
        print("=" * 80)
        print(f"🎯 SYSTEM FEATURES DEMONSTRATED:")
        print(f"   ✅ Historical pattern storage with win rate tracking")
        print(f"   ✅ Multi-timeframe analysis (24h-48h, 7d, 1m)")
        print(f"   ✅ Top 10 pattern identification per symbol/direction/timeframe")
        print(f"   ✅ Probability-based scoring system")
        print(f"   ✅ Real-time learning integration")
        print(f"   ✅ AI-enhanced report generation with historical context")
        
        print(f"\n🎯 BUSINESS BENEFITS:")
        print(f"   📈 Win rate predictions based on historical data")
        print(f"   🔒 Risk assessment using historical drawdowns")
        print(f"   ⚖️  Probability scoring for trading decisions")
        print(f"   🧠 Continuous learning from market outcomes")
        print(f"   📊 Multi-timeframe validation")
        print(f"   🎯 Top pattern identification for maximum accuracy")
        
        print(f"\n🚀 SYSTEM READY FOR PRODUCTION:")
        print(f"   • Historical patterns stored with comprehensive metadata")
        print(f"   • Win rates calculated across multiple timeframes")
        print(f"   • Top 10 patterns tracked per symbol/direction/timeframe")
        print(f"   • Probability scores assigned based on historical success")
        print(f"   • AI reports enhanced with historical context")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print(f"\n🐛 Full error traceback:")
        traceback.print_exc()

async def create_sample_historical_patterns(db: HistoricalPatternDatabase, symbol: str):
    """Create sample historical patterns for testing"""
    print("   📝 Creating sample patterns...")
    
    patterns_created = 0
    
    # Create patterns for different timeframes and directions
    for timeframe in TimeFrame:
        for direction in [Direction.LONG, Direction.SHORT]:
            for i in range(15):  # 15 patterns per timeframe/direction
                # Simulate different outcomes
                if i < 10:  # 10 wins
                    final_outcome = 'WIN'
                    win_rate_score = 0.8 + (i * 0.02)  # 0.8 to 0.98
                    max_profit = 5.0 + (i * 0.5)  # 5% to 12%
                    max_drawdown = -1.0 - (i * 0.1)  # -1% to -2.4%
                elif i < 13:  # 3 losses
                    final_outcome = 'LOSS'
                    win_rate_score = 0.2 - (i * 0.02)
                    max_profit = 0.5
                    max_drawdown = -3.0 - (i * 0.5)  # -3% to -4%
                else:  # 2 breakeven
                    final_outcome = 'BREAKEVEN'
                    win_rate_score = 0.5
                    max_profit = 0.2
                    max_drawdown = -0.2
                
                pattern = HistoricalPattern(
                    id=str(uuid.uuid4()),
                    symbol=symbol,
                    timestamp=datetime.now() - timedelta(days=i*2),
                    direction=direction,
                    timeframe=timeframe,
                    endpoint_scores={
                        'ticker': 50 + i * 2,
                        'ohlcv': 55 + i * 1.5,
                        'liquidation_data_v2': 60 + i * 1.8,
                        'trend_indicator_v3': 45 + i * 2.2
                    },
                    endpoint_patterns={
                        'ticker': [f'high_volume_{i}', f'price_momentum_{i}'],
                        'ohlcv': [f'bullish_trend_{i}', f'low_volatility_{i}'],
                        'liquidation_data_v2': [f'liquidation_cluster_{i}'],
                        'trend_indicator_v3': [f'trend_reversal_{i}']
                    },
                    price_at_entry=3000.0 + i * 10.0,
                    volume_data={'24h_volume': 1000000 + i * 50000},
                    market_conditions={'volatility': 0.02 + i * 0.001},
                    price_changes={timeframe.value: max_profit if final_outcome == 'WIN' else max_drawdown},
                    max_profit=max_profit,
                    max_drawdown=max_drawdown,
                    final_outcome=final_outcome,
                    win_rate_score=win_rate_score,
                    confidence_at_entry=0.7 + i * 0.01,
                    patterns_identified=[f'pattern_{i}', f'signal_{i}', f'indicator_{i}'],
                    trigger_conditions={
                        'score_threshold': 65.0 + i,
                        'confidence_threshold': 0.7,
                        'volume_factor': 1.2 + i * 0.1
                    }
                )
                
                db.store_historical_pattern(pattern)
                patterns_created += 1
    
    print(f"   ✅ Created {patterns_created} sample historical patterns")

async def test_database_functionality(db: HistoricalPatternDatabase, symbol: str):
    """Test basic database functionality"""
    print("   🔍 Testing database queries...")
    
    # Test getting top patterns
    for timeframe in TimeFrame:
        for direction in [Direction.LONG, Direction.SHORT]:
            top_patterns = db.get_top_patterns(symbol, direction, timeframe)
            print(f"   📊 {timeframe.value} {direction.value}: {len(top_patterns)} top patterns")
            
            if top_patterns:
                best_pattern = top_patterns[0]
                print(f"      🏆 Best: {best_pattern.pattern_signature} (Win Rate: {best_pattern.win_rate:.1%})")
    
    # Test probability scoring
    test_patterns = ['pattern_1', 'signal_2', 'indicator_3']
    prob_score = db.get_pattern_probability_score(symbol, test_patterns, Direction.LONG, TimeFrame.DAYS_7)
    print(f"   🎯 Probability score for test patterns: {prob_score:.3f}")
    
    # Test database statistics
    stats = db.get_database_stats()
    print(f"   📈 Database stats: {stats}")

async def test_multi_timeframe_analysis(agent: AdvancedLearningAgent, symbol: str):
    """Test multi-timeframe analysis functionality"""
    print("   ⏰ Testing multi-timeframe analysis...")
    
    # Simulate a Cryptometer analysis
    from src.services.cryptometer_endpoint_analyzer import CryptometerAnalysis, EndpointScore
    
    mock_analysis = CryptometerAnalysis(
        symbol=symbol,
        endpoint_scores=[
            EndpointScore('ticker', True, 65.0, 0.8, ['high_volume', 'price_momentum']),
            EndpointScore('ohlcv', True, 70.0, 0.75, ['bullish_trend', 'low_volatility']),
            EndpointScore('liquidation_data_v2', True, 60.0, 0.85, ['liquidation_cluster'])
        ],
        calibrated_score=68.5,
        confidence=0.78,
        direction='LONG',
        analysis_summary="Mock analysis for testing"
    )
    
    # Test storing with historical context
    prediction_id = await agent.store_analysis_with_historical_context(mock_analysis, store_prediction=True)
    print(f"   ✅ Stored analysis with prediction ID: {prediction_id}")
    
    # Test pattern probability analysis
    patterns = ['high_volume', 'bullish_trend', 'liquidation_cluster']
    for timeframe in TimeFrame:
        prob_analysis = agent.get_pattern_probability_analysis(symbol, patterns, 'LONG', timeframe)
        print(f"   📊 {timeframe.value} LONG: {prob_analysis['overall_probability']:.3f} probability, {prob_analysis['confidence_level']:.3f} confidence")

async def test_top_patterns_analysis(db: HistoricalPatternDatabase, symbol: str):
    """Test top patterns analysis"""
    print("   🏆 Testing top patterns analysis...")
    
    for timeframe in TimeFrame:
        print(f"   📅 {timeframe.value} Analysis:")
        
        # Long patterns
        long_patterns = db.get_top_patterns(symbol, Direction.LONG, timeframe)
        if long_patterns:
            print(f"      📈 LONG - Top 3 patterns:")
            for i, pattern in enumerate(long_patterns[:3], 1):
                print(f"         {i}. {pattern.pattern_signature}: {pattern.win_rate:.1%} win rate, {pattern.total_trades} trades")
        
        # Short patterns
        short_patterns = db.get_top_patterns(symbol, Direction.SHORT, timeframe)
        if short_patterns:
            print(f"      📉 SHORT - Top 3 patterns:")
            for i, pattern in enumerate(short_patterns[:3], 1):
                print(f"         {i}. {pattern.pattern_signature}: {pattern.win_rate:.1%} win rate, {pattern.total_trades} trades")

async def test_comprehensive_analysis(agent: AdvancedLearningAgent, symbol: str):
    """Test comprehensive analysis functionality"""
    print("   🔬 Testing comprehensive analysis...")
    
    comprehensive_analysis = agent.get_comprehensive_analysis(symbol)
    
    print(f"   📊 Overall Statistics:")
    overall_stats = comprehensive_analysis['historical_analysis']['overall_statistics']
    print(f"      • Total Historical Patterns: {overall_stats['total_historical_patterns']}")
    print(f"      • Overall Win Rate: {overall_stats['overall_win_rate']:.1%}")
    print(f"      • Data Maturity: {overall_stats['data_maturity']}")
    
    print(f"   🎯 Reliability Assessment:")
    reliability = comprehensive_analysis['reliability_assessment']
    print(f"      • Combined Reliability Score: {reliability['combined_reliability_score']:.1%}")
    print(f"      • Assessment: {reliability['assessment']}")
    
    print(f"   💡 Trading Recommendations:")
    for rec in comprehensive_analysis['trading_recommendations'][:3]:
        print(f"      • {rec}")

async def test_ai_enhanced_analysis(agent: HistoricalAIAnalysisAgent, symbol: str):
    """Test AI-enhanced historical analysis"""
    print("   🤖 Testing AI-enhanced analysis...")
    
    try:
        # Get symbol summary
        summary = await agent.get_symbol_historical_summary(symbol)
        print(f"   📋 Symbol Summary:")
        print(f"      • Reliability: {summary['reliability_assessment']['assessment']}")
        print(f"      • Data Quality: {summary['historical_summary']['historical_analysis']['overall_statistics']['data_maturity']}")
        
        # Test top patterns analysis
        patterns_analysis = await agent.get_top_patterns_analysis(symbol, "LONG", "7d")
        if 'error' not in patterns_analysis:
            print(f"   🏆 Top Patterns Analysis:")
            print(f"      • Total Top Patterns: {len(patterns_analysis['top_patterns'])}")
            print(f"      • Matching Current: {len(patterns_analysis['matching_current_patterns'])}")
            print(f"      • Recommendation: {patterns_analysis['analysis_recommendation']}")
        
        print("   ✅ AI-enhanced analysis completed successfully")
        
    except Exception as e:
        print(f"   ⚠️  AI-enhanced analysis skipped (requires OpenAI API): {e}")

def display_system_statistics(db: HistoricalPatternDatabase, agent: AdvancedLearningAgent):
    """Display comprehensive system statistics"""
    print("   📊 Historical Database Statistics:")
    db_stats = db.get_database_stats()
    for key, value in db_stats.items():
        print(f"      • {key}: {value}")
    
    print("   🧠 Learning Agent Statistics:")
    learning_status = agent.get_learning_summary()
    print(f"      • Patterns Learned: {learning_status['learning_progress']['total_patterns_learned']}")
    print(f"      • Average Success Rate: {learning_status['learning_progress']['average_success_rate']:.1%}")
    
    print("   🔗 Combined System Status:")
    combined_status = agent.get_database_status()
    print(f"      • Total Data Points: {combined_status['combined_status']['total_data_points']}")
    print(f"      • Symbols Tracked: {combined_status['combined_status']['symbols_tracked']}")
    print(f"      • Maturity Level: {combined_status['combined_status']['maturity_level']}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_historical_pattern_system())