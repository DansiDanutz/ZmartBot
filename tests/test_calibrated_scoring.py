#!/usr/bin/env python3
"""
Test script for the Calibrated Scoring System
Demonstrates independent component scoring with realistic win-rate expectations
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.calibrated_scoring_service import CalibratedScoringService
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_calibrated_scoring():
    """Test the calibrated scoring system"""
    print("🧪 TESTING CALIBRATED INDEPENDENT SCORING SYSTEM")
    print("=" * 80)
    print("Expected: Mostly 40-70% scores with rare 80%+ opportunities")
    print("Methodology: Realistic win-rate scoring where 95-100 = exceptional")
    print("=" * 80)
    
    # Initialize the scoring service
    scoring_service = CalibratedScoringService()
    
    # Test symbols
    test_symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'SUI']
    
    print(f"\n🎯 Testing {len(test_symbols)} symbols: {test_symbols}")
    print("=" * 80)
    
    results = []
    
    for symbol in test_symbols:
        print(f"\n{'='*25} {symbol} ANALYSIS {'='*25}")
        
        try:
            # Get independent scores
            scores = await scoring_service.get_independent_scores(symbol)
            
            # Display scores
            scoring_service.display_scores(scores)
            
            # Store results
            available_scores = scores.get_available_scores()
            result = {
                'symbol': symbol,
                'timestamp': scores.timestamp,
                'components': {}
            }
            
            for component, score in available_scores.items():
                result['components'][component] = {
                    'score': score.score,
                    'win_rate': score.win_rate,
                    'direction': score.direction,
                    'confidence': score.confidence
                }
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error testing {symbol}: {e}")
            continue
    
    # Summary analysis
    print(f"\n{'='*80}")
    print("📊 CALIBRATED SCORING SYSTEM SUMMARY")
    print(f"{'='*80}")
    
    if results:
        # Analyze Cryptometer scores (main calibrated component)
        cryptometer_scores = []
        for result in results:
            if 'cryptometer' in result['components']:
                cryptometer_scores.append(result['components']['cryptometer']['score'])
        
        if cryptometer_scores:
            avg_score = sum(cryptometer_scores) / len(cryptometer_scores)
            high_scores = [s for s in cryptometer_scores if s >= 80]
            exceptional_scores = [s for s in cryptometer_scores if s >= 95]
            
            print(f"\n🎯 CRYPTOMETER CALIBRATED ANALYSIS:")
            print(f"   Total symbols: {len(cryptometer_scores)}")
            print(f"   Average score: {avg_score:.1f}/100")
            print(f"   High scores (80%+): {len(high_scores)}/{len(cryptometer_scores)} ({len(high_scores)/len(cryptometer_scores)*100:.1f}%)")
            print(f"   Exceptional (95%+): {len(exceptional_scores)}/{len(cryptometer_scores)} ({len(exceptional_scores)/len(cryptometer_scores)*100:.1f}%)")
            
            # Calibration assessment
            high_score_pct = len(high_scores) / len(cryptometer_scores) * 100
            if high_score_pct <= 20:
                calibration_status = "✅ PROPERLY CALIBRATED - 80%+ scores are RARE"
            elif high_score_pct <= 30:
                calibration_status = "🟡 ACCEPTABLE - Some high scores"
            else:
                calibration_status = "❌ NEEDS CALIBRATION - Too many high scores"
            
            print(f"   Calibration: {calibration_status}")
        
        # Show individual results
        print(f"\n📋 INDIVIDUAL RESULTS:")
        print("-" * 80)
        
        for result in results:
            symbol = result['symbol']
            components = result['components']
            
            print(f"\n🔹 {symbol}:")
            for component, data in components.items():
                score = data['score']
                direction = data['direction']
                
                if score >= 95:
                    status = "🟢 EXCEPTIONAL"
                elif score >= 90:
                    status = "🟢 ALL-IN"
                elif score >= 80:
                    status = "🟢 TAKE TRADE"
                elif score >= 70:
                    status = "🟡 MODERATE"
                elif score >= 60:
                    status = "🟠 WEAK"
                else:
                    status = "🔴 AVOID"
                
                print(f"   {component}: {score:.1f}/100 - {direction} - {status}")
    
    print(f"\n🚀 CALIBRATED SYSTEM FEATURES:")
    print("✅ Independent component scoring (KingFisher, Cryptometer, RiskMetric)")
    print("✅ Realistic win-rate expectations (80%+ = RARE opportunities)")
    print("✅ Flexible aggregation (ready for future implementation)")
    print("✅ No fixed 25-point system - fully modular")
    print("✅ Calibrated Cryptometer engine with confluence analysis")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Implement KingFisher liquidation analysis")
    print("2. Implement RiskMetric risk-based scoring")
    print("3. Design flexible aggregation strategy")
    print("4. Add dynamic weight adjustment")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def test_single_symbol():
    """Test detailed analysis for a single symbol"""
    symbol = "BTC"
    print(f"\n🔍 DETAILED ANALYSIS FOR {symbol}")
    print("=" * 60)
    
    scoring_service = CalibratedScoringService()
    
    # Test Cryptometer detailed analysis
    print(f"\n📊 CRYPTOMETER DETAILED ANALYSIS:")
    try:
        cryptometer_score = await scoring_service.cryptometer_engine.get_symbol_score(symbol)
        
        print(f"   Final Score: {cryptometer_score.score:.1f}/100")
        print(f"   Win Rate: {cryptometer_score.win_rate*100:.1f}%")
        print(f"   Direction: {cryptometer_score.direction}")
        print(f"   Confidence: {cryptometer_score.confidence:.2f}")
        print(f"   Patterns: {len(cryptometer_score.patterns)}")
        
        if cryptometer_score.patterns:
            print(f"\n   🔍 Pattern Details:")
            for i, pattern in enumerate(cryptometer_score.patterns[:3]):  # Show first 3
                print(f"      {i+1}. {pattern.get('pattern_type', 'unknown')}: {pattern.get('signal_strength', 0):.2f}")
        
        print(f"\n   📈 Analysis Details:")
        for key, value in cryptometer_score.analysis_details.items():
            if isinstance(value, dict) and 'pattern_type' in value:
                print(f"      {key}: {value['pattern_type']}")
        
    except Exception as e:
        logger.error(f"Error in detailed analysis: {e}")

if __name__ == "__main__":
    print("🚀 STARTING CALIBRATED SCORING SYSTEM TESTS")
    print(f"API Key configured: {'✅ YES' if settings.CRYPTOMETER_API_KEY else '❌ NO'}")
    print(f"Settings loaded: ✅ YES")
    
    # Run tests
    asyncio.run(test_calibrated_scoring())
    asyncio.run(test_single_symbol())
    
    print("\n✅ All tests completed!")