#!/usr/bin/env python3
"""
ETH/USDT Focused Analysis using Calibrated Scoring System
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.calibrated_scoring_service import CalibratedScoringService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def analyze_eth_detailed():
    """Detailed analysis of ETH/USDT using our calibrated scoring strategy"""
    
    print("🔍 ETH/USDT DETAILED ANALYSIS")
    print("=" * 80)
    print("Strategy: Independent Component Scoring with Calibrated Win-Rate System")
    print("=" * 80)
    
    # Initialize the scoring service
    scoring_service = CalibratedScoringService()
    
    symbol = "ETH"
    
    print(f"\n📊 ANALYZING {symbol}/USDT")
    print("-" * 60)
    
    try:
        # Get independent scores for all components
        scores = await scoring_service.get_independent_scores(symbol)
        
        print(f"\n🎯 INDEPENDENT COMPONENT SCORES:")
        print(f"Analysis Timestamp: {scores.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        available_scores = scores.get_available_scores()
        
        total_score = 0
        component_count = 0
        recommendations = []
        
        for component, score in available_scores.items():
            print(f"\n🔹 {component.upper()} ANALYSIS:")
            print(f"   📈 Score: {score.score:.1f}/100")
            print(f"   🎯 Win Rate: {score.win_rate*100:.1f}%")
            print(f"   📍 Direction: {score.direction}")
            print(f"   🔒 Confidence: {score.confidence:.2f}")
            print(f"   🔍 Patterns Detected: {len(score.patterns)}")
            
            # Score interpretation
            if score.score >= 95:
                interpretation = "🟢 EXCEPTIONAL (95%+ - Royal Flush)"
                action = "ALL-IN MAXIMUM POSITION"
                risk_level = "VERY LOW"
            elif score.score >= 90:
                interpretation = "🟢 ALL-IN (90-94% - Very Rare)"
                action = "LARGE POSITION"
                risk_level = "LOW"
            elif score.score >= 80:
                interpretation = "🟢 TAKE TRADE (80-89% - Rare)"
                action = "MEDIUM POSITION"
                risk_level = "MODERATE"
            elif score.score >= 70:
                interpretation = "🟡 MODERATE (70-79%)"
                action = "SMALL POSITION"
                risk_level = "MODERATE-HIGH"
            elif score.score >= 60:
                interpretation = "🟠 WEAK (60-69%)"
                action = "AVOID"
                risk_level = "HIGH"
            else:
                interpretation = "🔴 AVOID (<60%)"
                action = "NO TRADE"
                risk_level = "VERY HIGH"
            
            print(f"   ⭐ Status: {interpretation}")
            print(f"   💡 Action: {action}")
            print(f"   ⚠️  Risk Level: {risk_level}")
            
            # Store for aggregation analysis
            total_score += score.score
            component_count += 1
            recommendations.append({
                'component': component,
                'score': score.score,
                'direction': score.direction,
                'action': action,
                'risk_level': risk_level
            })
            
            # Show pattern details if available
            if score.patterns and len(score.patterns) > 0:
                print(f"   📋 Pattern Details:")
                for i, pattern in enumerate(score.patterns[:3]):  # Show first 3
                    pattern_type = pattern.get('pattern_type', 'unknown')
                    signal_strength = pattern.get('signal_strength', 0)
                    print(f"      {i+1}. {pattern_type}: {signal_strength:.2f}")
            
            # Show analysis details
            if score.analysis_details:
                print(f"   🔬 Analysis Details:")
                for key, value in score.analysis_details.items():
                    if isinstance(value, dict):
                        if 'pattern_type' in value:
                            print(f"      {key}: {value['pattern_type']}")
                    elif key == 'error':
                        print(f"      ⚠️  {key}: {value}")
                    elif key == 'status':
                        print(f"      📊 {key}: {value}")
        
        # Overall Analysis
        print(f"\n{'='*60}")
        print(f"📊 OVERALL ETH/USDT ANALYSIS")
        print(f"{'='*60}")
        
        if component_count > 0:
            avg_score = total_score / component_count
            print(f"📈 Average Score: {avg_score:.1f}/100")
            
            # Determine overall recommendation
            high_confidence_components = [r for r in recommendations if r['score'] >= 80]
            moderate_components = [r for r in recommendations if 70 <= r['score'] < 80]
            weak_components = [r for r in recommendations if r['score'] < 70]
            
            print(f"\n📋 COMPONENT BREAKDOWN:")
            print(f"   🟢 High Confidence (80%+): {len(high_confidence_components)}")
            print(f"   🟡 Moderate (70-79%): {len(moderate_components)}")
            print(f"   🔴 Weak/Avoid (<70%): {len(weak_components)}")
            
            # Overall trading recommendation
            print(f"\n💡 OVERALL TRADING RECOMMENDATION:")
            
            if len(high_confidence_components) >= 2:
                overall_action = "🟢 STRONG BUY - Multiple high-confidence signals"
                position_size = "LARGE"
            elif len(high_confidence_components) >= 1:
                overall_action = "🟢 BUY - At least one high-confidence signal"
                position_size = "MEDIUM"
            elif len(moderate_components) >= 2:
                overall_action = "🟡 MODERATE BUY - Multiple moderate signals"
                position_size = "SMALL"
            elif avg_score >= 65:
                overall_action = "🟡 WEAK BUY - Average performance"
                position_size = "VERY SMALL"
            else:
                overall_action = "🔴 AVOID - Wait for better setup"
                position_size = "NONE"
            
            print(f"   🎯 Action: {overall_action}")
            print(f"   📊 Position Size: {position_size}")
            
            # Direction consensus
            directions = [r['direction'] for r in recommendations if r['direction'] != 'NEUTRAL']
            if directions:
                long_count = directions.count('LONG')
                short_count = directions.count('SHORT')
                if long_count > short_count:
                    consensus_direction = "LONG"
                elif short_count > long_count:
                    consensus_direction = "SHORT"
                else:
                    consensus_direction = "MIXED"
                print(f"   📍 Direction Consensus: {consensus_direction}")
            else:
                print(f"   📍 Direction Consensus: NEUTRAL")
            
            # Risk assessment
            risk_levels = [r['risk_level'] for r in recommendations]
            high_risk = risk_levels.count('HIGH') + risk_levels.count('VERY HIGH')
            if high_risk >= len(risk_levels) / 2:
                overall_risk = "⚠️  HIGH RISK"
            elif 'MODERATE' in risk_levels:
                overall_risk = "🟡 MODERATE RISK"
            else:
                overall_risk = "🟢 LOW RISK"
            
            print(f"   ⚠️  Overall Risk: {overall_risk}")
        
        # Strategy Notes
        print(f"\n📝 STRATEGY NOTES:")
        print(f"✅ Independent scoring prevents over-reliance on single source")
        print(f"✅ Calibrated system ensures 80%+ scores are truly rare opportunities")
        print(f"✅ Flexible aggregation allows custom weighting strategies")
        print(f"✅ Each component maintains its own methodology and confidence")
        
        print(f"\n🔄 NEXT STEPS:")
        print(f"1. Monitor for score improvements across components")
        print(f"2. Wait for 80%+ scores for high-probability trades")
        print(f"3. Implement KingFisher liquidation analysis for better signals")
        print(f"4. Add RiskMetric historical analysis for risk validation")
        
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        print(f"❌ Error analyzing {symbol}: {e}")

if __name__ == "__main__":
    print("🚀 STARTING ETH/USDT CALIBRATED ANALYSIS")
    print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run analysis
    asyncio.run(analyze_eth_detailed())
    
    print("\n✅ ETH/USDT Analysis Complete!")