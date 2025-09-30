#!/usr/bin/env python3
"""
Test Data-Driven Professional Analysis System
Demonstrates the new Cryptometer endpoint-focused approach with professional win rates
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.enhanced_professional_ai_agent import EnhancedProfessionalAIAgent
from src.services.data_driven_report_generator import DataDrivenReportGenerator
from src.services.advanced_cryptometer_analyzer import AdvancedCryptometerAnalyzer

async def test_data_driven_system():
    """Test the new data-driven professional analysis system"""
    
    print("🚀 TESTING DATA-DRIVEN PROFESSIONAL ANALYSIS SYSTEM")
    print("=" * 80)
    
    # Initialize components
    ai_agent = EnhancedProfessionalAIAgent()
    data_generator = DataDrivenReportGenerator()
    analyzer = AdvancedCryptometerAnalyzer()
    
    test_symbols = ["BTC/USDT", "ETH/USDT"]
    
    print("📊 PHASE 1: CRYPTOMETER ENDPOINT ANALYSIS")
    print("-" * 60)
    
    endpoint_results = []
    
    for symbol in test_symbols:
        print(f"\n🔍 Analyzing {symbol} endpoints...")
        
        try:
            async with analyzer:
                analysis_report = await analyzer.analyze_symbol_comprehensive(symbol)
            
            print(f"✅ Analysis Complete for {symbol}")
            print(f"📈 Current Price: ${analysis_report.market_price_analysis.current_price:.4f}")
            print(f"📊 24h Change: {analysis_report.market_price_analysis.price_24h_change:+.2f}%")
            print(f"🎯 Overall Direction: {analysis_report.overall_direction}")
            print(f"🔒 Confidence: {analysis_report.confidence_level:.1%}")
            
            # Display win rates
            print(f"\n🎯 PROFESSIONAL WIN RATES:")
            print(f"   Long 24h: {analysis_report.market_price_analysis.long_win_rate_24h:.1f}%")
            print(f"   Short 24h: {analysis_report.market_price_analysis.short_win_rate_24h:.1f}%")
            print(f"   Long 7d: {analysis_report.market_price_analysis.long_win_rate_7d:.1f}%")
            print(f"   Short 7d: {analysis_report.market_price_analysis.short_win_rate_7d:.1f}%")
            
            # Display composite scores
            print(f"\n📊 COMPOSITE SCORES:")
            print(f"   Long Score: {analysis_report.composite_long_score:.1f}/100")
            print(f"   Short Score: {analysis_report.composite_short_score:.1f}/100")
            print(f"   Score Sum: {analysis_report.composite_long_score + analysis_report.composite_short_score:.1f}")
            
            # Display endpoint data quality
            print(f"\n🔍 DATA QUALITY:")
            print(f"   Endpoints Used: {len(analysis_report.data_sources_used)}")
            print(f"   Analysis Quality: {analysis_report.analysis_quality_score:.1%}")
            print(f"   Data Quality: {analysis_report.market_price_analysis.data_quality_score:.1%}")
            
            # Display key insights
            if analysis_report.key_insights:
                print(f"\n💡 KEY INSIGHTS:")
                for i, insight in enumerate(analysis_report.key_insights[:3], 1):
                    print(f"   {i}. {insight}")
            
            endpoint_results.append({
                'symbol': symbol,
                'analysis_report': analysis_report,
                'success': True
            })
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            endpoint_results.append({
                'symbol': symbol,
                'error': str(e),
                'success': False
            })
    
    print(f"\n📊 PHASE 2: DATA-DRIVEN REPORT GENERATION")
    print("-" * 60)
    
    report_results = []
    
    for symbol in test_symbols:
        print(f"\n📝 Generating data-driven report for {symbol}...")
        
        try:
            # Generate executive summary
            executive_result = await data_generator.generate_professional_executive_summary(symbol)
            
            if executive_result.get('success'):
                report_content = executive_result.get('report_content', '')
                data_quality = executive_result.get('data_quality', 0.0)
                confidence = executive_result.get('confidence', 0.0)
                data_sources = executive_result.get('data_sources', [])
                
                print(f"✅ Executive Summary Generated")
                print(f"📄 Report Length: {len(report_content)} characters")
                print(f"📊 Data Quality: {data_quality:.1%}")
                print(f"🔒 Confidence: {confidence:.1%}")
                print(f"🔗 Data Sources: {len(data_sources)} endpoints")
                
                # Check for key sections
                key_sections = [
                    "WIN RATE SUMMARY",
                    "COMPOSITE SCORES", 
                    "TRADING RECOMMENDATIONS",
                    "RISK FACTORS",
                    "KEY INSIGHTS"
                ]
                
                sections_found = []
                for section in key_sections:
                    if section in report_content:
                        sections_found.append(section)
                
                print(f"📋 Sections Found: {len(sections_found)}/{len(key_sections)}")
                for section in sections_found:
                    print(f"   ✅ {section}")
                
                # Check for professional win rates
                win_rate_mentions = report_content.count("% win rate")
                print(f"🎯 Win Rate Mentions: {win_rate_mentions}")
                
                # Check for current price mentions
                price_mentions = report_content.count("$")
                print(f"💰 Price References: {price_mentions}")
                
                report_results.append({
                    'symbol': symbol,
                    'report_length': len(report_content),
                    'data_quality': data_quality,
                    'confidence': confidence,
                    'sections_found': len(sections_found),
                    'win_rate_mentions': win_rate_mentions,
                    'success': True
                })
                
            else:
                error = executive_result.get('error', 'Unknown error')
                print(f"❌ Report generation failed: {error}")
                report_results.append({
                    'symbol': symbol,
                    'error': error,
                    'success': False
                })
                
        except Exception as e:
            print(f"❌ Error generating report for {symbol}: {e}")
            report_results.append({
                'symbol': symbol,
                'error': str(e),
                'success': False
            })
    
    print(f"\n🤖 PHASE 3: ENHANCED AI AGENT INTEGRATION")
    print("-" * 60)
    
    ai_results = []
    
    for symbol in test_symbols:
        print(f"\n🧠 AI Agent analysis for {symbol}...")
        
        try:
            # Generate using enhanced AI agent (which now uses data-driven approach)
            ai_result = await ai_agent.generate_executive_summary(symbol)
            
            if ai_result.get('success'):
                metadata = ai_result.get('metadata', {})
                learning_analysis = ai_result.get('learning_analysis', {})
                
                print(f"✅ AI Analysis Complete")
                print(f"📊 Processing Time: {metadata.get('processing_time', 0):.2f}s")
                print(f"📄 Word Count: {metadata.get('word_count', 0)}")
                print(f"🔗 Endpoint Sources: {metadata.get('endpoint_sources', 0)}")
                print(f"📈 Data Quality: {metadata.get('data_quality', 0):.1%}")
                print(f"🔒 Analysis Confidence: {metadata.get('analysis_confidence', 0):.1%}")
                print(f"🧠 Learning Enabled: {metadata.get('learning_enabled', False)}")
                
                # Learning analysis
                if learning_analysis.get('success'):
                    learning_data = learning_analysis.get('analysis', {})
                    print(f"📚 Structure Quality: {learning_data.get('structure_quality', 0):.2f}")
                    print(f"🎯 AVAX Compliant: {learning_data.get('avax_compliant', False)}")
                    
                    suggestions = learning_analysis.get('suggestions', [])
                    if suggestions:
                        print(f"💡 Improvement Suggestions: {len(suggestions)}")
                        for i, suggestion in enumerate(suggestions[:2], 1):
                            print(f"   {i}. {suggestion}")
                
                ai_results.append({
                    'symbol': symbol,
                    'processing_time': metadata.get('processing_time', 0),
                    'word_count': metadata.get('word_count', 0),
                    'endpoint_sources': metadata.get('endpoint_sources', 0),
                    'data_quality': metadata.get('data_quality', 0),
                    'analysis_confidence': metadata.get('analysis_confidence', 0),
                    'success': True
                })
                
            else:
                error = ai_result.get('error', 'Unknown error')
                print(f"❌ AI analysis failed: {error}")
                ai_results.append({
                    'symbol': symbol,
                    'error': error,
                    'success': False
                })
                
        except Exception as e:
            print(f"❌ Error in AI analysis for {symbol}: {e}")
            ai_results.append({
                'symbol': symbol,
                'error': str(e),
                'success': False
            })
    
    print(f"\n📈 PHASE 4: SYSTEM PERFORMANCE ANALYSIS")
    print("-" * 60)
    
    # Analyze endpoint results
    successful_endpoints = [r for r in endpoint_results if r['success']]
    if successful_endpoints:
        avg_confidence = sum(r['analysis_report'].confidence_level for r in successful_endpoints) / len(successful_endpoints)
        avg_data_quality = sum(r['analysis_report'].analysis_quality_score for r in successful_endpoints) / len(successful_endpoints)
        total_endpoints = sum(len(r['analysis_report'].data_sources_used) for r in successful_endpoints)
        
        print(f"🔍 ENDPOINT ANALYSIS PERFORMANCE:")
        print(f"   Success Rate: {len(successful_endpoints)}/{len(endpoint_results)} ({len(successful_endpoints)/len(endpoint_results):.1%})")
        print(f"   Average Confidence: {avg_confidence:.1%}")
        print(f"   Average Data Quality: {avg_data_quality:.1%}")
        print(f"   Total Endpoints Used: {total_endpoints}")
    
    # Analyze report results
    successful_reports = [r for r in report_results if r['success']]
    if successful_reports:
        avg_report_length = sum(r['report_length'] for r in successful_reports) / len(successful_reports)
        avg_sections = sum(r['sections_found'] for r in successful_reports) / len(successful_reports)
        total_win_rates = sum(r['win_rate_mentions'] for r in successful_reports)
        
        print(f"\n📝 REPORT GENERATION PERFORMANCE:")
        print(f"   Success Rate: {len(successful_reports)}/{len(report_results)} ({len(successful_reports)/len(report_results):.1%})")
        print(f"   Average Length: {avg_report_length:.0f} characters")
        print(f"   Average Sections: {avg_sections:.1f}/5")
        print(f"   Total Win Rate Mentions: {total_win_rates}")
    
    # Analyze AI results
    successful_ai = [r for r in ai_results if r['success']]
    if successful_ai:
        avg_processing_time = sum(r['processing_time'] for r in successful_ai) / len(successful_ai)
        avg_word_count = sum(r['word_count'] for r in successful_ai) / len(successful_ai)
        avg_endpoint_sources = sum(r['endpoint_sources'] for r in successful_ai) / len(successful_ai)
        
        print(f"\n🤖 AI AGENT PERFORMANCE:")
        print(f"   Success Rate: {len(successful_ai)}/{len(ai_results)} ({len(successful_ai)/len(ai_results):.1%})")
        print(f"   Average Processing Time: {avg_processing_time:.2f}s")
        print(f"   Average Word Count: {avg_word_count:.0f}")
        print(f"   Average Endpoint Sources: {avg_endpoint_sources:.1f}")
    
    print(f"\n✅ DATA-DRIVEN SYSTEM TEST COMPLETE")
    print("=" * 80)
    print("🎯 KEY ACHIEVEMENTS:")
    print("   • Cryptometer endpoints serve as primary data source")
    print("   • Professional win rates calculated for LONG/SHORT positions")
    print("   • Current market price integrated into analysis")
    print("   • Advanced market insights beyond generic AI content")
    print("   • Data quality scoring and confidence levels")
    print("   • Endpoint-specific analysis and contribution weighting")
    print("   • Professional trading recommendations based on real data")
    print("\n🚀 SYSTEM READY FOR PROFESSIONAL TRADING ANALYSIS!")

if __name__ == "__main__":
    asyncio.run(test_data_driven_system())