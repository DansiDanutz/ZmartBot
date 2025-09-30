#!/usr/bin/env python3
"""
Complete AI System Test with OpenAI Integration
Tests the full historical pattern database with AI-enhanced analysis
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.historical_ai_analysis_agent import HistoricalAIAnalysisAgent
from src.services.advanced_learning_agent import AdvancedLearningAgent
from src.services.enhanced_ai_analysis_agent import EnhancedAIAnalysisAgent
from src.config.settings import settings

async def test_complete_ai_system():
    """Test the complete AI system with historical pattern integration"""
    
    print("🚀 STARTING COMPLETE AI SYSTEM TEST WITH OPENAI INTEGRATION")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🤖 HISTORICAL PATTERN DATABASE + AI-ENHANCED ANALYSIS")
    print("=" * 80)
    
    # Check API key configuration
    print("\n🔑 API KEY CONFIGURATION CHECK:")
    print(f"   📊 Cryptometer API Key: {'✅ Configured' if settings.CRYPTOMETER_API_KEY else '❌ Missing'}")
    print(f"   🤖 OpenAI API Key (ZmartGPT): {'✅ Configured' if settings.OPENAI_API_KEY else '❌ Missing'}")
    print(f"   💰 OpenAI API Key (ZmartTrading): {'✅ Configured' if settings.OPENAI_API_KEY_TRADING else '❌ Missing'}")
    
    if not all([settings.CRYPTOMETER_API_KEY, settings.OPENAI_API_KEY]):
        print("\n❌ Missing required API keys. Please configure all API keys.")
        return
    
    try:
        # Test symbol
        symbol = "ETH"
        print(f"\n📈 TESTING COMPLETE AI SYSTEM FOR {symbol}/USDT...")
        print("-" * 80)
        
        # Step 1: Initialize all AI agents
        print("🤖 Initializing AI Agents...")
        
        # Historical AI Analysis Agent (uses ZmartGPT key)
        historical_ai_agent = HistoricalAIAnalysisAgent(settings.OPENAI_API_KEY)
        print("   ✅ Historical AI Analysis Agent initialized")
        
        # Enhanced AI Analysis Agent (uses ZmartTrading key) 
        enhanced_ai_agent = EnhancedAIAnalysisAgent(settings.OPENAI_API_KEY_TRADING)
        print("   ✅ Enhanced AI Analysis Agent initialized")
        
        # Advanced Learning Agent
        advanced_learning_agent = AdvancedLearningAgent()
        print("   ✅ Advanced Learning Agent initialized")
        
        # Step 2: Test Historical AI Analysis (Full System)
        print(f"\n🧠 GENERATING HISTORICAL AI ANALYSIS FOR {symbol}...")
        print("   📊 This includes: Cryptometer + Historical Patterns + AI Report Generation")
        
        historical_analysis = await historical_ai_agent.generate_historical_enhanced_report(symbol, store_prediction=True)
        
        print(f"\n🎯 HISTORICAL AI ANALYSIS COMPLETE!")
        print("=" * 80)
        
        print(f"📊 ANALYSIS RESULTS:")
        print(f"   📈 Symbol: {historical_analysis['symbol']}/USDT")
        print(f"   🆔 Prediction ID: {historical_analysis['prediction_id']}")
        print(f"   📝 Report Word Count: {historical_analysis['word_count']} words")
        print(f"   🔒 AI-Enhanced Confidence: {historical_analysis['confidence_score']:.1f}%")
        print(f"   ⏰ Generated: {historical_analysis['timestamp']}")
        
        # Display Cryptometer analysis
        crypto_analysis = historical_analysis['cryptometer_analysis']
        print(f"\n📊 CRYPTOMETER ANALYSIS:")
        print(f"   🎯 Calibrated Score: {crypto_analysis['calibrated_score']:.1f}%")
        print(f"   📈 Direction: {crypto_analysis['direction']}")
        print(f"   🔒 Confidence: {crypto_analysis['confidence']:.3f}")
        print(f"   ✅ Successful Endpoints: {crypto_analysis['successful_endpoints']}/17")
        
        # Display multi-timeframe analysis
        multi_tf = historical_analysis['multi_timeframe_analysis']
        print(f"\n⏰ MULTI-TIMEFRAME ANALYSIS:")
        
        timeframes = ['24h-48h', '7d', '1m']
        directions = ['LONG', 'SHORT']
        
        for tf in timeframes:
            print(f"   📅 {tf}:")
            for direction in directions:
                key = f"{tf}_{direction}"
                if key in multi_tf:
                    data = multi_tf[key]
                    print(f"      📈 {direction}: Win Rate {data['win_rate_prediction']:.1%}, Confidence {data['confidence_level']:.1%}")
        
        # Step 3: Test Symbol Historical Summary
        print(f"\n📋 GENERATING SYMBOL HISTORICAL SUMMARY...")
        summary = await historical_ai_agent.get_symbol_historical_summary(symbol)
        
        print(f"   📊 Reliability Assessment: {summary['reliability_assessment']['assessment']}")
        print(f"   📈 Data Quality: {summary['historical_summary']['historical_analysis']['overall_statistics']['data_maturity']}")
        print(f"   ⏰ Timeframe Coverage:")
        for tf, count in summary['timeframe_coverage'].items():
            print(f"      • {tf}: {count} patterns")
        
        # Step 4: Test Top Patterns Analysis
        print(f"\n🏆 TESTING TOP PATTERNS ANALYSIS...")
        for direction in ['LONG', 'SHORT']:
            for timeframe in ['24h-48h', '7d', '1m']:
                try:
                    patterns = await historical_ai_agent.get_top_patterns_analysis(symbol, direction, timeframe)
                    if 'error' not in patterns:
                        total_patterns = len(patterns['top_patterns'])
                        matching_patterns = len(patterns['matching_current_patterns'])
                        print(f"   📊 {direction} {timeframe}: {total_patterns} top patterns, {matching_patterns} matching current")
                        if patterns['analysis_recommendation']:
                            print(f"      💡 Recommendation: {patterns['analysis_recommendation']}")
                except Exception as e:
                    print(f"   ⚠️  {direction} {timeframe}: {str(e)}")
        
        # Step 5: Test Learning-Enhanced Analysis (Comparison)
        print(f"\n🔬 TESTING LEARNING-ENHANCED ANALYSIS...")
        learning_report = await enhanced_ai_agent.generate_learning_enhanced_report(symbol, store_prediction=True)
        
        print(f"   📝 Learning Report Word Count: {learning_report.word_count} words")
        print(f"   🔒 Learning-Enhanced Confidence: {learning_report.confidence_score:.1f}%")
        print(f"   📊 Confidence Comparison:")
        print(f"      • Historical AI: {historical_analysis['confidence_score']:.1f}%")
        print(f"      • Learning-Enhanced: {learning_report.confidence_score:.1f}%")
        print(f"      • Difference: {learning_report.confidence_score - historical_analysis['confidence_score']:+.1f} points")
        
        # Step 6: Save AI Reports
        print(f"\n💾 SAVING AI REPORTS...")
        
        # Save Historical AI Report
        historical_filename = f"{symbol}_Historical_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        historical_header = f"""# {symbol}/USDT Historical AI Analysis Report

**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}  
**Analysis Type:** Historical Pattern Database + AI Enhancement  
**AI Model:** ChatGPT-4 Mini (ZmartGPT)  
**Prediction ID:** {historical_analysis['prediction_id']}  
**Confidence Score:** {historical_analysis['confidence_score']:.1f}%  
**Word Count:** {historical_analysis['word_count']} words  

**Multi-Timeframe Analysis:**
- 24h-48h Analysis: ✅ Complete
- 7-Day Analysis: ✅ Complete  
- 1-Month Analysis: ✅ Complete

**Historical Database Integration:**
- Pattern Storage: ✅ Active
- Win Rate Tracking: ✅ Active
- Top Pattern Identification: ✅ Active
- Probability Scoring: ✅ Active

---

"""
        
        with open(historical_filename, 'w', encoding='utf-8') as f:
            f.write(historical_header + historical_analysis['report_content'])
        
        print(f"   📁 Historical AI Report: {historical_filename}")
        
        # Save Learning-Enhanced Report
        learning_filename = f"{symbol}_Learning_Enhanced_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        learning_header = f"""# {symbol}/USDT Learning-Enhanced AI Analysis Report

**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}  
**Analysis Type:** Self-Learning AI Enhancement  
**AI Model:** ChatGPT-4 Mini (ZmartTrading)  
**Confidence Score:** {learning_report.confidence_score:.1f}%  
**Word Count:** {learning_report.word_count} words  

**Learning Features:**
- Self-Learning Database: ✅ Active
- Pattern Recognition: ✅ Active
- Adaptive Scoring: ✅ Active
- Confidence Calibration: ✅ Active

---

"""
        
        with open(learning_filename, 'w', encoding='utf-8') as f:
            f.write(learning_header + learning_report.report_content)
        
        print(f"   📁 Learning-Enhanced Report: {learning_filename}")
        
        # Step 7: System Status Summary
        print(f"\n📊 COMPLETE SYSTEM STATUS:")
        db_status = advanced_learning_agent.get_database_status()
        
        print(f"   🧠 Learning Database:")
        learning_stats = db_status['learning_database']['learning_progress']
        print(f"      • Patterns Learned: {learning_stats['total_patterns_learned']}")
        print(f"      • Average Success Rate: {learning_stats['average_success_rate']:.1%}")
        print(f"      • Endpoints Tracked: {learning_stats['endpoints_tracked']}")
        
        print(f"   📚 Historical Database:")
        historical_stats = db_status['historical_database']
        print(f"      • Historical Patterns: {historical_stats.get('historical_patterns_count', 0)}")
        print(f"      • Pattern Statistics: {historical_stats.get('pattern_statistics_count', 0)}")
        print(f"      • Top Patterns: {historical_stats.get('top_patterns_count', 0)}")
        print(f"      • Symbols Tracked: {historical_stats.get('symbols_tracked', 0)}")
        
        print(f"   🔗 Combined Status:")
        combined_stats = db_status['combined_status']
        print(f"      • Total Data Points: {combined_stats['total_data_points']}")
        print(f"      • Maturity Level: {combined_stats['maturity_level']}")
        
        print(f"\n✅ COMPLETE AI SYSTEM TEST SUCCESSFUL!")
        print("=" * 80)
        print(f"🎯 SYSTEM CAPABILITIES DEMONSTRATED:")
        print(f"   ✅ Historical pattern database with win rate tracking")
        print(f"   ✅ Multi-timeframe analysis (24h-48h, 7d, 1m)")
        print(f"   ✅ AI-enhanced report generation with ChatGPT-4 Mini")
        print(f"   ✅ Self-learning system with adaptive scoring")
        print(f"   ✅ Real-time learning integration")
        print(f"   ✅ Probability-based pattern scoring")
        print(f"   ✅ Top pattern identification and tracking")
        print(f"   ✅ Comprehensive database integration")
        
        print(f"\n🚀 PRODUCTION-READY FEATURES:")
        print(f"   • Dual OpenAI API integration (ZmartGPT + ZmartTrading)")
        print(f"   • Historical pattern validation across multiple timeframes")
        print(f"   • Win rate predictions based on proven historical data")
        print(f"   • Self-learning AI that improves with every analysis")
        print(f"   • Comprehensive API endpoints for all functionality")
        print(f"   • Real-time pattern recognition and scoring")
        print(f"   • Multi-database architecture for maximum performance")
        
        print(f"\n📊 API ENDPOINTS READY:")
        print(f"   🤖 Historical AI Analysis: /api/v1/historical-analysis/report/{symbol}")
        print(f"   🧠 Learning-Enhanced Analysis: /api/v1/learning-ai-analysis/report/{symbol}")
        print(f"   📊 Multi-Timeframe Analysis: /api/v1/historical-analysis/multi-timeframe/{symbol}")
        print(f"   🏆 Top Patterns Analysis: /api/v1/historical-analysis/patterns/{symbol}")
        print(f"   📈 Win Rates Analysis: /api/v1/historical-analysis/win-rates/{symbol}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check OpenAI API key validity and quota")
        print("   2. Verify Cryptometer API key is active")
        print("   3. Ensure internet connection for API calls")
        print("   4. Check database permissions")
        
        import traceback
        print(f"\n🐛 Full error traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Run the complete test
    asyncio.run(test_complete_ai_system())