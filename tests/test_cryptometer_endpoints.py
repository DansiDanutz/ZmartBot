#!/usr/bin/env python3
"""
Test Cryptometer Endpoint-by-Endpoint Analysis
Shows individual endpoint scores and calibrated final result
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.cryptometer_endpoint_analyzer import CryptometerEndpointAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_eth_endpoint_analysis():
    """Test ETH endpoint-by-endpoint analysis"""
    
    print("🔍 CRYPTOMETER ENDPOINT-BY-ENDPOINT ANALYSIS")
    print("=" * 80)
    print("Symbol: ETH/USDT")
    print("Strategy: Individual endpoint scoring + Agent calibration")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = CryptometerEndpointAnalyzer()
    
    symbol = "ETH"
    
    print(f"\n📊 ANALYZING ALL 17 CRYPTOMETER ENDPOINTS FOR {symbol}")
    print("⏱️  Rate Limited: 1 second delay between endpoints (17 seconds total)")
    print("-" * 80)
    
    try:
        # Get complete analysis
        analysis = await analyzer.analyze_symbol_complete(symbol)
        
        print(f"\n🎯 INDIVIDUAL ENDPOINT SCORES:")
        print("=" * 80)
        
        # Sort endpoints by score for better visualization
        sorted_endpoints = sorted(analysis.endpoint_scores, key=lambda x: x.score, reverse=True)
        
        total_weight = 0
        successful_endpoints = 0
        
        for i, endpoint_score in enumerate(sorted_endpoints, 1):
            endpoint_config = analyzer.endpoints.get(endpoint_score.endpoint, {'weight': 1, 'description': 'Unknown'})
            weight = endpoint_config['weight']
            description = endpoint_config['description']
            
            print(f"\n{i:2d}. 🔹 {endpoint_score.endpoint.upper()}")
            print(f"    📈 Score: {endpoint_score.score:.1f}%")
            print(f"    ⚖️  Weight: {weight}/100")
            print(f"    🔒 Confidence: {endpoint_score.confidence:.2f}")
            print(f"    📋 Description: {description}")
            print(f"    🔍 Analysis: {endpoint_score.analysis}")
            
            if endpoint_score.success:
                successful_endpoints += 1
                total_weight += weight
                
                if endpoint_score.patterns:
                    patterns_text = ", ".join(endpoint_score.patterns)
                    print(f"    🎯 Patterns: {patterns_text}")
                
                # Score interpretation
                if endpoint_score.score >= 80:
                    status = "🟢 STRONG SIGNAL"
                elif endpoint_score.score >= 60:
                    status = "🟡 MODERATE"
                elif endpoint_score.score >= 40:
                    status = "🟠 WEAK"
                else:
                    status = "🔴 POOR"
                
                print(f"    ⭐ Status: {status}")
            else:
                print(f"    ❌ Error: {endpoint_score.error}")
                print(f"    ⭐ Status: 🔴 FAILED")
        
        # Calibration Agent Results
        print(f"\n{'='*80}")
        print(f"🤖 CALIBRATION AGENT RESULTS")
        print(f"{'='*80}")
        
        print(f"\n📊 DATA COVERAGE:")
        print(f"   ✅ Successful Endpoints: {successful_endpoints}/{len(analysis.endpoint_scores)}")
        print(f"   📊 Coverage: {successful_endpoints/len(analysis.endpoint_scores)*100:.1f}%")
        # Calculate redistribution factor for display
        successful_weight = sum(analyzer.endpoints.get(es.endpoint, {'weight': 1})['weight'] 
                              for es in analysis.endpoint_scores if es.success)
        redistribution_factor = 100.0 / successful_weight if successful_weight > 0 else 1.0
        
        print(f"   ⚖️  Original Weight: {successful_weight}/122 → Redistributed: 100/100 (factor: {redistribution_factor:.3f})")
        
        print(f"\n🎯 CALIBRATED FINAL SCORE:")
        print(f"   📈 Final Score: {analysis.calibrated_score:.1f}%")
        print(f"   🔒 Confidence: {analysis.confidence:.2f}")
        print(f"   📍 Direction: {analysis.direction}")
        
        # Score interpretation
        if analysis.calibrated_score >= 95:
            interpretation = "🟢 EXCEPTIONAL (95%+ - Royal Flush)"
            action = "ALL-IN MAXIMUM POSITION"
        elif analysis.calibrated_score >= 90:
            interpretation = "🟢 ALL-IN (90-94% - Very Rare)"
            action = "LARGE POSITION"
        elif analysis.calibrated_score >= 80:
            interpretation = "🟢 TAKE TRADE (80-89% - Rare)"
            action = "MEDIUM POSITION"
        elif analysis.calibrated_score >= 70:
            interpretation = "🟡 MODERATE (70-79%)"
            action = "SMALL POSITION"
        elif analysis.calibrated_score >= 60:
            interpretation = "🟠 WEAK (60-69%)"
            action = "AVOID"
        else:
            interpretation = "🔴 AVOID (<60%)"
            action = "NO TRADE"
        
        print(f"   ⭐ Interpretation: {interpretation}")
        print(f"   💡 Recommended Action: {action}")
        
        print(f"\n📝 ANALYSIS SUMMARY:")
        print(f"   {analysis.analysis_summary}")
        
        # Top performing endpoints
        top_endpoints = sorted([es for es in analysis.endpoint_scores if es.success], 
                             key=lambda x: x.score, reverse=True)[:5]
        
        print(f"\n🏆 TOP 5 PERFORMING ENDPOINTS:")
        for i, endpoint in enumerate(top_endpoints, 1):
            weight = analyzer.endpoints.get(endpoint.endpoint, {'weight': 1})['weight']
            print(f"   {i}. {endpoint.endpoint}: {endpoint.score:.1f}% (weight: {weight})")
        
        # Calibration insights
        print(f"\n🔬 CALIBRATION INSIGHTS:")
        print(f"   📊 Raw weighted average would be different from calibrated score")
        print(f"   🎯 Calibration ensures 80%+ scores are truly rare opportunities")
        print(f"   ⚖️  Data coverage penalty applied for missing endpoints")
        print(f"   🤖 Agent applied realistic score distribution curve")
        
        # Trading recommendation
        print(f"\n💡 TRADING RECOMMENDATION:")
        if analysis.calibrated_score >= 80:
            print(f"   🟢 TRADE RECOMMENDED")
            print(f"   📊 High-probability setup detected")
            print(f"   🎯 Direction: {analysis.direction}")
        elif analysis.calibrated_score >= 70:
            print(f"   🟡 MODERATE OPPORTUNITY")
            print(f"   📊 Consider small position")
            print(f"   ⚠️  Monitor for improvement")
        else:
            print(f"   🔴 AVOID TRADING")
            print(f"   📊 Wait for better setup")
            print(f"   🔄 Monitor for score improvement")
        
        print(f"\n⏰ Analysis completed at: {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Error in endpoint analysis: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 STARTING CRYPTOMETER ENDPOINT ANALYSIS")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run analysis
    asyncio.run(test_eth_endpoint_analysis())
    
    print("\n✅ Cryptometer Endpoint Analysis Complete!")