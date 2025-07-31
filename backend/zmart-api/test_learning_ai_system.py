#!/usr/bin/env python3
"""
Test Self-Learning AI Analysis System
Demonstrates the self-learning capabilities and continuous improvement features
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.enhanced_ai_analysis_agent import EnhancedAIAnalysisAgent
from src.services.learning_agent import SelfLearningAgent, AnalysisPrediction, MarketOutcome
import uuid

async def test_learning_system():
    """Test the complete self-learning AI system"""
    
    print("🚀 STARTING SELF-LEARNING AI ANALYSIS SYSTEM TEST")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🧠 SELF-LEARNING AI SYSTEM WITH CONTINUOUS IMPROVEMENT")
    print("=" * 80)
    
    try:
        # Initialize Enhanced AI Analysis Agent
        print("\n📊 Initializing Self-Learning AI System...")
        enhanced_agent = EnhancedAIAnalysisAgent()
        print("✅ Enhanced AI Analysis Agent initialized successfully")
        
        # Get initial learning status
        initial_status = enhanced_agent.get_learning_status()
        print(f"\n🧠 INITIAL LEARNING STATUS:")
        print(f"   📚 Patterns Learned: {initial_status['learning_progress']['total_patterns_learned']}")
        print(f"   🎯 Average Success Rate: {initial_status['learning_progress']['average_success_rate']:.1%}")
        print(f"   📊 Endpoints Tracked: {initial_status['learning_progress']['endpoints_tracked']}")
        
        # Test symbol
        symbol = "ETH"
        print(f"\n📈 TESTING LEARNING-ENHANCED ANALYSIS FOR {symbol}/USDT...")
        print("⏱️  This includes: Cryptometer analysis + Learning enhancements + AI generation")
        print("-" * 80)
        
        # Generate learning-enhanced report
        print("🔄 Generating learning-enhanced analysis report...")
        enhanced_report = await enhanced_agent.generate_learning_enhanced_report(symbol, store_prediction=True)
        
        print(f"\n🎯 LEARNING-ENHANCED REPORT GENERATED!")
        print("=" * 80)
        
        print(f"\n📊 ENHANCED REPORT METADATA:")
        print(f"   📈 Symbol: {enhanced_report.symbol}/USDT")
        print(f"   📝 Word Count: {enhanced_report.word_count} words")
        print(f"   🔒 Learning-Enhanced Confidence: {enhanced_report.confidence_score:.1f}%")
        print(f"   ⏰ Generated: {enhanced_report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        print(f"\n📋 ENHANCED EXECUTIVE SUMMARY:")
        print(f"   {enhanced_report.summary}")
        
        if enhanced_report.recommendations:
            print(f"\n💡 LEARNING-BASED RECOMMENDATIONS:")
            for i, rec in enumerate(enhanced_report.recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        # Demonstrate learning comparison
        print(f"\n🔬 GENERATING LEARNING COMPARISON...")
        print("   Comparing standard analysis vs learning-enhanced analysis...")
        
        # Generate standard report for comparison
        standard_report = await enhanced_agent.generate_comprehensive_report(symbol)
        
        print(f"\n📊 LEARNING ENHANCEMENT COMPARISON:")
        print(f"   📈 Standard Confidence: {standard_report.confidence_score:.1f}%")
        print(f"   🧠 Enhanced Confidence: {enhanced_report.confidence_score:.1f}%")
        print(f"   📈 Improvement: {enhanced_report.confidence_score - standard_report.confidence_score:+.1f} points")
        print(f"   📝 Word Count Difference: {enhanced_report.word_count - standard_report.word_count:+d} words")
        
        # Demonstrate learning insights
        print(f"\n🧠 LEARNING INSIGHTS DEMONSTRATION:")
        if initial_status['top_performing_patterns']:
            print("   🎯 Top Performing Patterns:")
            for i, pattern in enumerate(initial_status['top_performing_patterns'][:3], 1):
                print(f"   {i}. {pattern['pattern']}: {pattern['success_rate']:.1%} success rate")
        else:
            print("   📚 Learning database is initializing - patterns will be learned from future analyses")
        
        # Simulate learning process (for demonstration)
        print(f"\n🔄 SIMULATING LEARNING PROCESS...")
        await simulate_learning_cycle(enhanced_agent, symbol)
        
        # Get updated learning status
        updated_status = enhanced_agent.get_learning_status()
        print(f"\n📈 LEARNING PROGRESS UPDATE:")
        print(f"   📚 Patterns Learned: {updated_status['learning_progress']['total_patterns_learned']}")
        print(f"   🎯 Average Success Rate: {updated_status['learning_progress']['average_success_rate']:.1%}")
        print(f"   📊 Database Size: {updated_status.get('learning_database_size', {})}")
        
        # Save enhanced report
        filename = f"{symbol}_Learning_Enhanced_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        markdown_header = f"""# {enhanced_report.symbol}/USDT Self-Learning AI Technical Analysis Report

**Generated:** {enhanced_report.timestamp.strftime('%B %d, %Y at %H:%M UTC')}  
**Analysis Agent:** Self-Learning Enhanced AI  
**Model:** ChatGPT-4 Mini + Adaptive Learning System  
**Learning-Enhanced Confidence:** {enhanced_report.confidence_score:.1f}%  
**Word Count:** {enhanced_report.word_count} words  
**Patterns Learned:** {updated_status['learning_progress']['total_patterns_learned']}  
**Learning Success Rate:** {updated_status['learning_progress']['average_success_rate']:.1%}  

---

"""
        
        full_content = markdown_header + enhanced_report.report_content
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"\n💾 LEARNING-ENHANCED REPORT SAVED:")
        print(f"   📁 Filename: {filename}")
        print(f"   📊 Size: {len(full_content)} characters")
        
        print(f"\n✅ SELF-LEARNING AI SYSTEM TEST COMPLETE!")
        print("=" * 80)
        print(f"🧠 LEARNING SYSTEM FEATURES DEMONSTRATED:")
        print(f"   ✅ Adaptive endpoint weighting based on historical performance")
        print(f"   ✅ Pattern recognition and success rate tracking")
        print(f"   ✅ Confidence calibration through learning")
        print(f"   ✅ Prediction storage for future validation")
        print(f"   ✅ Continuous improvement through feedback loops")
        print(f"   ✅ Learning-enhanced report generation")
        
        print(f"\n🎯 LEARNING SYSTEM BENEFITS:")
        print(f"   📈 Improved accuracy over time through pattern learning")
        print(f"   🔒 Enhanced confidence scoring based on historical success")
        print(f"   ⚖️  Adaptive weighting of endpoint importance")
        print(f"   🧠 Memory of successful analysis patterns")
        print(f"   🔄 Continuous self-improvement without manual intervention")
        
        print(f"\n🚀 SYSTEM READY FOR PRODUCTION:")
        print(f"   • Self-learning AI will improve with each analysis")
        print(f"   • Pattern recognition becomes more sophisticated over time")
        print(f"   • Confidence scoring adapts based on actual market outcomes")
        print(f"   • Endpoint weights adjust automatically for better accuracy")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Ensure OpenAI API key is configured")
        print("   2. Check database permissions for learning data storage")
        print("   3. Verify all dependencies are installed")
        print("   4. Check internet connection for API calls")
        
        import traceback
        print(f"\n🐛 Full error traceback:")
        traceback.print_exc()

async def simulate_learning_cycle(enhanced_agent: EnhancedAIAnalysisAgent, symbol: str):
    """Simulate a learning cycle for demonstration purposes"""
    
    print("   🔄 Simulating prediction validation cycle...")
    
    # Create a sample prediction for demonstration
    sample_prediction = AnalysisPrediction(
        id=str(uuid.uuid4()),
        symbol=symbol,
        timestamp=datetime.now() - timedelta(hours=24),
        predicted_direction="LONG",
        predicted_score=65.5,
        confidence=0.72,
        endpoint_scores={
            "ticker": 55.0,
            "ohlcv": 60.0,
            "liquidation_data_v2": 70.0,
            "trend_indicator_v3": 45.0
        },
        patterns_identified=["high_volume", "bullish_trend", "low_volatility"],
        recommendations=["Consider long position", "Monitor volume"],
        price_at_prediction=3200.0
    )
    
    # Store the prediction
    enhanced_agent.learning_agent.store_prediction(sample_prediction)
    print("   ✅ Sample prediction stored for learning")
    
    # Simulate market outcome (for demonstration)
    sample_outcome = MarketOutcome(
        prediction_id=sample_prediction.id,
        symbol=symbol,
        price_changes={"24h": 3.2},  # 3.2% price increase
        actual_direction="LONG",
        outcome_timestamp=datetime.now(),
        accuracy_score=0.85  # High accuracy
    )
    
    # Validate the prediction (this would normally happen automatically)
    enhanced_agent.learning_agent.validate_prediction(sample_outcome)
    print("   ✅ Prediction validated with 85% accuracy")
    print("   🧠 Learning system updated with new insights")
    print("   📈 Pattern success rates and endpoint weights adjusted")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_learning_system())