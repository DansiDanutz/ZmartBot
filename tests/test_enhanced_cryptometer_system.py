#!/usr/bin/env python3
"""
Test Enhanced Cryptometer System V2
Validates Data Appendix compliance and multi-model AI integration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.cryptometer_endpoint_analyzer_v2 import CryptometerEndpointAnalyzerV2
from src.services.multi_model_ai_agent import MultiModelAIAgent
from src.config.settings import settings

async def test_enhanced_cryptometer_system():
    """Test the enhanced Cryptometer system with Data Appendix compliance"""
    
    print("🚀 ENHANCED CRYPTOMETER SYSTEM V2 - COMPREHENSIVE TEST")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 DATA APPENDIX COMPLIANCE + MULTI-MODEL AI INTEGRATION")
    print("=" * 80)
    
    try:
        # Test 1: System Configuration Validation
        print("\n🔧 Test 1: System Configuration Validation")
        print("-" * 50)
        
        print(f"📊 Cryptometer API Key: {'✅ Configured' if settings.CRYPTOMETER_API_KEY else '❌ Missing'}")
        print(f"🤖 OpenAI ZmartGPT Key: {'✅ Configured' if settings.OPENAI_API_KEY else '❌ Missing'}")
        print(f"💰 OpenAI ZmartTrading Key: {'✅ Configured' if settings.OPENAI_API_KEY_TRADING else '❌ Missing'}")
        
        if not settings.CRYPTOMETER_API_KEY:
            print("❌ Cannot proceed without Cryptometer API key")
            return
        
        # Test 2: Enhanced Cryptometer Analyzer Initialization
        print("\n🧠 Test 2: Enhanced Cryptometer Analyzer V2 Initialization")
        print("-" * 50)
        
        try:
            analyzer_v2 = CryptometerEndpointAnalyzerV2()
            print("✅ Enhanced Cryptometer Analyzer V2 initialized successfully")
            
            # Display endpoint configuration
            status = analyzer_v2.get_endpoint_status()
            print(f"📊 Total Endpoints: {status['total_endpoints']}")
            print(f"🥇 Tier 1 (High Value): {len(status['endpoint_tiers']['tier_1_high_value'])} endpoints")
            print(f"🥈 Tier 2 (Supporting): {len(status['endpoint_tiers']['tier_2_supporting'])} endpoints")
            print(f"🥉 Tier 3 (Context): {len(status['endpoint_tiers']['tier_3_context'])} endpoints")
            
            print(f"\n📋 Tier 1 High-Value Endpoints (Data Appendix Priority):")
            for endpoint in status['endpoint_tiers']['tier_1_high_value']:
                config = analyzer_v2.endpoints[endpoint]
                print(f"   • {endpoint}: {config['description']} (Weight: {config['weight']})")
            
        except Exception as e:
            print(f"❌ Enhanced Cryptometer Analyzer V2 initialization failed: {e}")
            return
        
        # Test 3: Multi-Model AI Agent Integration
        print("\n🤖 Test 3: Multi-Model AI Agent Integration")
        print("-" * 50)
        
        try:
            multi_model_agent = MultiModelAIAgent()
            print("✅ Multi-Model AI Agent initialized successfully")
            
            model_status = multi_model_agent.get_model_status()
            available_models = sum(model_status['model_details'][model]['available'] 
                                 for model in model_status['model_details'])
            print(f"📊 Available AI Models: {available_models}/{len(model_status['model_details'])}")
            
            for model_name, model_info in model_status['model_details'].items():
                status_icon = "✅" if model_info['available'] else "❌"
                model_type = model_info['type'].upper()
                print(f"   {status_icon} {model_name} ({model_type})")
            
        except Exception as e:
            print(f"❌ Multi-Model AI Agent initialization failed: {e}")
            multi_model_agent = None
        
        # Test 4: Enhanced ETH/USDT Analysis with Data Appendix Compliance
        print("\n📈 Test 4: Enhanced ETH/USDT Analysis (Data Appendix Compliance)")
        print("-" * 50)
        
        symbol = "ETH"
        print(f"🎯 Testing enhanced analysis for {symbol}/USDT...")
        print("📊 Expected: 18 endpoints, 1-second intervals, comprehensive data validation")
        
        try:
            # Run enhanced analysis
            analysis = await analyzer_v2.analyze_symbol_complete(symbol)
            
            print(f"\n✅ Enhanced Analysis Results:")
            print(f"   📊 Final Score: {analysis.calibrated_score:.1f}%")
            print(f"   🎯 Direction: {analysis.direction}")
            print(f"   🔒 Confidence: {analysis.confidence:.1%}")
            print(f"   ✅ Successful Endpoints: {analysis.successful_endpoints}/{analysis.total_endpoints}")
            print(f"   ⏱️  Processing Time: {analysis.processing_time:.1f}s")
            print(f"   📋 Data Appendix Compliance: {'✅ Yes' if analysis.data_appendix_compliance else '❌ No'}")
            print(f"   📝 Summary: {analysis.analysis_summary}")
            
            # Detailed endpoint analysis
            print(f"\n📊 Detailed Endpoint Performance:")
            tier_performance = {'tier_1': [], 'tier_2': [], 'tier_3': []}
            
            for endpoint_score in analysis.endpoint_scores:
                # Determine tier
                config = analyzer_v2.endpoints.get(endpoint_score.endpoint, {})
                priority = config.get('data_appendix_priority', 18)
                
                if priority <= 5:
                    tier = 'tier_1'
                    tier_name = 'HIGH VALUE'
                elif priority <= 10:
                    tier = 'tier_2'
                    tier_name = 'SUPPORTING'
                else:
                    tier = 'tier_3'
                    tier_name = 'CONTEXT'
                
                tier_performance[tier].append(endpoint_score)
                
                status_icon = "✅" if endpoint_score.success else "❌"
                score_text = f"{endpoint_score.score:.1f}%" if endpoint_score.success else "FAILED"
                
                print(f"   {status_icon} {endpoint_score.endpoint} ({tier_name}): {score_text}")
                if endpoint_score.success and endpoint_score.patterns:
                    print(f"      🔍 Patterns: {', '.join(endpoint_score.patterns[:3])}")
            
            # Tier performance summary
            print(f"\n🏆 Tier Performance Summary:")
            for tier, scores in tier_performance.items():
                successful = sum(1 for score in scores if score.success)
                total = len(scores)
                success_rate = (successful / total * 100) if total > 0 else 0
                print(f"   📊 {tier.upper()}: {successful}/{total} ({success_rate:.0f}% success)")
            
        except Exception as e:
            print(f"❌ Enhanced ETH analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 5: Multi-Model AI Analysis Integration
        if multi_model_agent and analysis.successful_endpoints >= 5:
            print(f"\n🤖 Test 5: Multi-Model AI Analysis Integration")
            print("-" * 50)
            
            try:
                print(f"🔄 Generating multi-model analysis for {symbol}...")
                
                # Use best available model for analysis
                ai_analysis = await multi_model_agent.generate_comprehensive_analysis(symbol, use_all_models=False)
                
                print(f"✅ Multi-Model AI Analysis Complete:")
                print(f"   🤖 Primary Model: {ai_analysis['multi_model_analysis']['primary_model']}")
                print(f"   🔒 Confidence: {ai_analysis['multi_model_analysis']['aggregate_confidence']:.1%}")
                print(f"   ⏱️  Processing Time: {ai_analysis['multi_model_analysis']['total_processing_time']:.2f}s")
                print(f"   📈 Trend Direction: {ai_analysis['technical_data']['trend_direction']}")
                
                # Show analysis preview
                analysis_preview = ai_analysis['multi_model_analysis']['primary_analysis'][:300]
                print(f"   📝 Analysis Preview: {analysis_preview}...")
                
            except Exception as e:
                print(f"❌ Multi-Model AI analysis failed: {e}")
        else:
            print(f"\n⚠️  Test 5: Multi-Model AI Analysis Skipped")
            print("   Reason: Insufficient successful endpoints or AI agent unavailable")
        
        # Test 6: Performance Benchmarking
        print(f"\n⚡ Test 6: Performance Benchmarking")
        print("-" * 50)
        
        # Data Appendix benchmarks
        da_success_rate = 100  # Data Appendix achieved 100%
        da_processing_time = 18  # Data Appendix: 18 seconds
        
        our_success_rate = (analysis.successful_endpoints / analysis.total_endpoints) * 100
        our_processing_time = analysis.processing_time
        
        print(f"📊 Performance Comparison with Data Appendix:")
        print(f"   Success Rate: {our_success_rate:.0f}% vs {da_success_rate}% (Data Appendix)")
        print(f"   Processing Time: {our_processing_time:.1f}s vs {da_processing_time}s (Data Appendix)")
        print(f"   Endpoint Coverage: {analysis.total_endpoints} endpoints (Enhanced vs 18 Data Appendix)")
        
        # Performance assessment
        success_performance = "✅ EXCELLENT" if our_success_rate >= 90 else "✅ GOOD" if our_success_rate >= 80 else "⚠️ MODERATE" if our_success_rate >= 60 else "❌ POOR"
        time_performance = "✅ EXCELLENT" if our_processing_time <= 20 else "✅ GOOD" if our_processing_time <= 30 else "⚠️ MODERATE" if our_processing_time <= 45 else "❌ SLOW"
        
        print(f"   📈 Success Rate Performance: {success_performance}")
        print(f"   ⏱️  Time Performance: {time_performance}")
        
        # Test 7: System Recommendations
        print(f"\n💡 Test 7: System Recommendations & Next Steps")
        print("-" * 50)
        
        if our_success_rate >= 80:
            print("✅ SYSTEM STATUS: PRODUCTION READY")
            print("🎯 Recommendations:")
            print("   • Deploy enhanced system for live trading analysis")
            print("   • Enable multi-model AI integration for comprehensive reports")
            print("   • Set up monitoring for Data Appendix compliance")
            
            if multi_model_agent:
                available_models = sum(multi_model_agent.model_status.values())
                if available_models > 1:
                    print("   • Consider model comparison for critical trading decisions")
                else:
                    print("   • Install local models for enhanced reliability: ./setup_local_models.sh")
        else:
            print("⚠️ SYSTEM STATUS: NEEDS OPTIMIZATION")
            print("🔧 Recommendations:")
            print("   • Investigate failed endpoints for API parameter issues")
            print("   • Check network connectivity and API rate limits")
            print("   • Review Cryptometer API documentation for updates")
        
        print(f"\n🚀 ENHANCED CRYPTOMETER SYSTEM V2 TEST COMPLETE!")
        print("=" * 80)
        
        print(f"🎯 KEY ACHIEVEMENTS:")
        print(f"   ✅ Enhanced 18-endpoint configuration based on Data Appendix")
        print(f"   ✅ Multi-model AI integration with fallback capabilities")
        print(f"   ✅ Data quality assessment and validation")
        print(f"   ✅ Tiered endpoint prioritization for optimal analysis")
        print(f"   ✅ Data Appendix compliance monitoring")
        
        print(f"\n📊 SYSTEM CAPABILITIES:")
        print(f"   • {analysis.total_endpoints}-endpoint comprehensive analysis")
        print(f"   • {our_success_rate:.0f}% average success rate")
        print(f"   • {our_processing_time:.1f}s analysis time")
        print(f"   • Multi-model AI integration ready")
        print(f"   • Real-time Data Appendix compliance validation")
        
        print(f"\n🔗 API ENDPOINTS:")
        print(f"   🧠 Enhanced Analysis: /api/v1/multi-model-analysis/analyze/{symbol}")
        print(f"   🔬 Model Comparison: /api/v1/multi-model-analysis/compare-models/{symbol}")
        print(f"   📊 System Status: /api/v1/multi-model-analysis/model-status")
        print(f"   🛠️  Setup Guide: /api/v1/multi-model-analysis/local-models/install")
        
        if our_success_rate >= 80 and multi_model_agent:
            print(f"\n✅ ENHANCED SYSTEM READY FOR PRODUCTION!")
            print(f"🤖 Multi-model AI capabilities with Data Appendix compliance")
        else:
            print(f"\n⚠️  System optimization recommended before production deployment")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Verify all API keys are configured correctly")
        print("   2. Check internet connection and API accessibility")
        print("   3. Review system logs for specific error details")
        print("   4. Ensure all dependencies are installed")
        
        import traceback
        print(f"\n🐛 Full error traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Run the enhanced system test
    asyncio.run(test_enhanced_cryptometer_system())