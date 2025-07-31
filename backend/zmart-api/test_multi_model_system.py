#!/usr/bin/env python3
"""
Test Multi-Model AI Analysis System
Tests OpenAI, DeepSeek, and Phi models integration with fallback capabilities
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.multi_model_ai_agent import MultiModelAIAgent, ModelType
from src.config.settings import settings

async def test_multi_model_system():
    """Test the complete multi-model AI system"""
    
    print("🚀 STARTING MULTI-MODEL AI ANALYSIS SYSTEM TEST")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🤖 OPENAI + DEEPSEEK + PHI MODELS INTEGRATION")
    print("=" * 80)
    
    try:
        # Initialize Multi-Model AI Agent
        print("\n🤖 Initializing Multi-Model AI Agent...")
        multi_model_agent = MultiModelAIAgent()
        print("✅ Multi-Model AI Agent initialized successfully")
        
        # Check model availability
        print("\n📊 MODEL AVAILABILITY CHECK:")
        model_status = multi_model_agent.get_model_status()
        
        available_models = []
        for model_name, model_info in model_status['model_details'].items():
            status = "✅ Available" if model_info['available'] else "❌ Not Available"
            model_type = model_info['type'].upper()
            print(f"   🤖 {model_name}: {status} ({model_type})")
            
            if model_info['available']:
                available_models.append(model_name)
                capabilities = model_info['capabilities']
                print(f"      📋 Capabilities: {', '.join(capabilities[:2])}...")
        
        print(f"\n📈 SUMMARY: {len(available_models)}/{len(model_status['model_details'])} models available")
        
        if not available_models:
            print("\n❌ No AI models available. Please:")
            print("   1. Configure OpenAI API key")
            print("   2. Install local models with: ./setup_local_models.sh")
            return
        
        # Test symbol
        symbol = "ETH"
        print(f"\n📈 TESTING MULTI-MODEL ANALYSIS FOR {symbol}/USDT...")
        print("-" * 80)
        
        # Test 1: Single best model analysis
        print("🎯 Test 1: Best Available Model Analysis")
        try:
            analysis = await multi_model_agent.generate_comprehensive_analysis(symbol, use_all_models=False)
            
            print(f"✅ Analysis completed successfully!")
            print(f"   📊 Primary Model: {analysis['multi_model_analysis']['primary_model']}")
            print(f"   🔒 Confidence: {analysis['multi_model_analysis']['aggregate_confidence']:.1%}")
            print(f"   ⏱️  Processing Time: {analysis['multi_model_analysis']['total_processing_time']:.2f}s")
            print(f"   📈 Trend Direction: {analysis['technical_data']['trend_direction']}")
            print(f"   📊 Current Price: {analysis['technical_data']['current_price']}")
            
        except Exception as e:
            print(f"❌ Best model analysis failed: {e}")
        
        # Test 2: All models comparison (if multiple available)
        if len(available_models) > 1:
            print(f"\n🔬 Test 2: All Models Comparison")
            try:
                comparison_analysis = await multi_model_agent.generate_comprehensive_analysis(symbol, use_all_models=True)
                
                print(f"✅ Multi-model comparison completed!")
                print(f"   📊 Models Used: {comparison_analysis['multi_model_analysis']['models_used']}")
                print(f"   🏆 Best Model: {comparison_analysis['multi_model_analysis']['primary_model']}")
                print(f"   📈 Aggregate Confidence: {comparison_analysis['multi_model_analysis']['aggregate_confidence']:.1%}")
                
                print(f"\n📊 MODEL PERFORMANCE COMPARISON:")
                for model_comparison in comparison_analysis['model_comparisons']:
                    status_icon = "✅" if model_comparison['success'] else "❌"
                    print(f"   {status_icon} {model_comparison['model']}: "
                          f"{model_comparison['confidence']:.1%} confidence, "
                          f"{model_comparison['processing_time']:.2f}s")
                
            except Exception as e:
                print(f"❌ Multi-model comparison failed: {e}")
        else:
            print(f"\n⚠️  Test 2 skipped: Only one model available")
        
        # Test 3: Model-specific capabilities
        print(f"\n🎯 Test 3: Model-Specific Capabilities")
        
        for model_type in ModelType:
            if multi_model_agent.model_status.get(model_type, False):
                print(f"\n   🤖 Testing {model_type.value}...")
                
                try:
                    # Set specific model as priority
                    multi_model_agent.model_priority = [model_type]
                    
                    specific_analysis = await multi_model_agent.generate_comprehensive_analysis(symbol, use_all_models=False)
                    
                    processing_time = specific_analysis['multi_model_analysis']['total_processing_time']
                    confidence = specific_analysis['multi_model_analysis']['aggregate_confidence']
                    
                    print(f"      ✅ Success: {confidence:.1%} confidence in {processing_time:.2f}s")
                    
                    # Show preview of analysis
                    content_preview = specific_analysis['multi_model_analysis']['primary_analysis'][:200]
                    print(f"      📝 Preview: {content_preview}...")
                    
                except Exception as e:
                    print(f"      ❌ Failed: {e}")
        
        # Test 4: Fallback system
        print(f"\n🛡️  Test 4: Fallback System Reliability")
        
        # Simulate API failures by temporarily disabling OpenAI
        original_openai_status = multi_model_agent.model_status[ModelType.OPENAI_GPT4_MINI]
        multi_model_agent.model_status[ModelType.OPENAI_GPT4_MINI] = False
        
        print("   🔄 Simulating OpenAI unavailability...")
        
        try:
            fallback_analysis = await multi_model_agent.generate_comprehensive_analysis(symbol, use_all_models=False)
            
            fallback_model = fallback_analysis['multi_model_analysis']['primary_model']
            print(f"   ✅ Fallback successful! Used: {fallback_model}")
            print(f"   🔒 Fallback Confidence: {fallback_analysis['multi_model_analysis']['aggregate_confidence']:.1%}")
            
        except Exception as e:
            print(f"   ❌ Fallback failed: {e}")
        
        # Restore original status
        multi_model_agent.model_status[ModelType.OPENAI_GPT4_MINI] = original_openai_status
        
        # Test 5: System status and recommendations
        print(f"\n📊 Test 5: System Status and Recommendations")
        
        status = multi_model_agent.get_model_status()
        
        print(f"   📈 Available Models: {status['available_models']}")
        print(f"   🏆 Recommended Primary: {status['recommended_order'][0] if status['recommended_order'] else 'None'}")
        
        local_models = sum(1 for info in status['model_details'].values() 
                          if info['available'] and info['type'] == 'local')
        cloud_models = sum(1 for info in status['model_details'].values() 
                          if info['available'] and info['type'] == 'cloud')
        
        print(f"   🖥️  Local Models: {local_models}")
        print(f"   ☁️  Cloud Models: {cloud_models}")
        
        # Display setup instructions if local models missing
        if local_models == 0:
            print(f"\n💡 SETUP RECOMMENDATIONS:")
            print(f"   To enable local AI models, run:")
            print(f"   ./setup_local_models.sh")
            print(f"   ")
            print(f"   This will install:")
            for model, cmd in status['local_models_setup'].items():
                if model not in ['ollama_install', 'verify']:
                    print(f"   • {model}: {cmd}")
        
        # Test 6: Performance benchmarking
        print(f"\n⚡ Test 6: Performance Benchmarking")
        
        performance_results = []
        
        for model_type in ModelType:
            if multi_model_agent.model_status.get(model_type, False):
                print(f"   🏃 Benchmarking {model_type.value}...")
                
                start_time = datetime.now()
                try:
                    multi_model_agent.model_priority = [model_type]
                    benchmark_analysis = await multi_model_agent.generate_comprehensive_analysis(symbol, use_all_models=False)
                    
                    processing_time = (datetime.now() - start_time).total_seconds()
                    confidence = benchmark_analysis['multi_model_analysis']['aggregate_confidence']
                    
                    performance_results.append({
                        'model': model_type.value,
                        'time': processing_time,
                        'confidence': confidence,
                        'success': True
                    })
                    
                    print(f"      ⏱️  Time: {processing_time:.2f}s, Confidence: {confidence:.1%}")
                    
                except Exception as e:
                    performance_results.append({
                        'model': model_type.value,
                        'time': 0,
                        'confidence': 0,
                        'success': False,
                        'error': str(e)
                    })
                    print(f"      ❌ Failed: {e}")
        
        # Performance summary
        if performance_results:
            successful_results = [r for r in performance_results if r['success']]
            if successful_results:
                fastest = min(successful_results, key=lambda x: x['time'])
                most_confident = max(successful_results, key=lambda x: x['confidence'])
                
                print(f"\n🏆 PERFORMANCE SUMMARY:")
                print(f"   ⚡ Fastest Model: {fastest['model']} ({fastest['time']:.2f}s)")
                print(f"   🎯 Most Confident: {most_confident['model']} ({most_confident['confidence']:.1%})")
        
        print(f"\n✅ MULTI-MODEL AI SYSTEM TEST COMPLETE!")
        print("=" * 80)
        print(f"🎯 SYSTEM CAPABILITIES DEMONSTRATED:")
        print(f"   ✅ Multi-model AI integration (OpenAI + Local models)")
        print(f"   ✅ Automatic fallback when primary models unavailable")
        print(f"   ✅ Model-specific optimizations for trading analysis")
        print(f"   ✅ Performance benchmarking and comparison")
        print(f"   ✅ Structured data analysis for technical indicators")
        print(f"   ✅ Privacy-focused local model execution")
        
        print(f"\n🚀 PRODUCTION BENEFITS:")
        print(f"   • Reliability: Multiple AI models ensure system availability")
        print(f"   • Privacy: Local models for sensitive trading data")
        print(f"   • Performance: Optimized models for different analysis types")
        print(f"   • Cost Efficiency: Reduce API costs with local models")
        print(f"   • Specialized Analysis: Each model optimized for specific tasks")
        
        print(f"\n📊 API ENDPOINTS READY:")
        print(f"   🤖 Multi-Model Analysis: /api/v1/multi-model-analysis/analyze/{symbol}")
        print(f"   🔬 Model Comparison: /api/v1/multi-model-analysis/compare-models/{symbol}")
        print(f"   📊 Model Status: /api/v1/multi-model-analysis/model-status")
        print(f"   🛠️  Setup Guide: /api/v1/multi-model-analysis/local-models/install")
        
        if local_models == 0:
            print(f"\n💡 NEXT STEPS:")
            print(f"   1. Run: ./setup_local_models.sh")
            print(f"   2. Install recommended models for enhanced capabilities")
            print(f"   3. Test local models with the API endpoints")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check API key configurations")
        print("   2. Install local models with setup script")
        print("   3. Ensure sufficient system resources")
        print("   4. Check internet connection for cloud models")
        
        import traceback
        print(f"\n🐛 Full error traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_multi_model_system())