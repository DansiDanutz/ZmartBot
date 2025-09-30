#!/usr/bin/env python3
"""
Test AI Analysis Agent
Demonstrates the AI-powered technical analysis report generation
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.ai_analysis_agent import AIAnalysisAgent

async def test_ai_analysis():
    """Test the AI Analysis Agent functionality"""
    
    print("🚀 STARTING AI ANALYSIS AGENT TEST")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍 AI-POWERED TECHNICAL ANALYSIS REPORT GENERATION")
    print("=" * 80)
    
    try:
        # Initialize AI Analysis Agent
        print("\n📊 Initializing AI Analysis Agent...")
        ai_agent = AIAnalysisAgent()
        print("✅ AI Analysis Agent initialized successfully")
        
        # Test symbol
        symbol = "ETH"
        print(f"\n📈 Generating comprehensive analysis report for {symbol}/USDT...")
        print("⏱️  This may take 30-60 seconds (includes Cryptometer analysis + AI generation)")
        print("-" * 80)
        
        # Generate comprehensive report
        report = await ai_agent.generate_comprehensive_report(symbol)
        
        print(f"\n🎯 ANALYSIS REPORT GENERATED SUCCESSFULLY!")
        print("=" * 80)
        
        print(f"\n📊 REPORT METADATA:")
        print(f"   📈 Symbol: {report.symbol}/USDT")
        print(f"   📝 Word Count: {report.word_count} words")
        print(f"   🔒 Confidence Score: {report.confidence_score:.1f}%")
        print(f"   ⏰ Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"   {report.summary}")
        
        if report.recommendations:
            print(f"\n💡 KEY RECOMMENDATIONS:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        if report.risk_factors:
            print(f"\n⚠️  RISK FACTORS:")
            for i, risk in enumerate(report.risk_factors[:3], 1):
                print(f"   {i}. {risk}")
        
        print(f"\n📄 FULL REPORT CONTENT:")
        print("=" * 80)
        print(report.report_content)
        print("=" * 80)
        
        # Save report to file
        filename = f"{symbol}_AI_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Create markdown header
        markdown_header = f"""# {report.symbol}/USDT AI Technical Analysis Report

**Generated:** {report.timestamp.strftime('%B %d, %Y at %H:%M UTC')}  
**Analysis Agent:** AI-Powered Technical Analysis  
**Model:** ChatGPT-4 Mini  
**Confidence Score:** {report.confidence_score:.1f}%  
**Word Count:** {report.word_count} words  

---

"""
        
        full_content = markdown_header + report.report_content
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"\n💾 REPORT SAVED:")
        print(f"   📁 Filename: {filename}")
        print(f"   📊 Size: {len(full_content)} characters")
        
        print(f"\n✅ AI Analysis Test Complete!")
        print(f"📈 Generated professional {report.word_count}-word technical analysis report")
        print(f"🎯 Confidence Score: {report.confidence_score:.1f}%")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Ensure OpenAI API key is configured in environment variables")
        print("   2. Check internet connection for API calls")
        print("   3. Verify Cryptometer API key is working")
        print("   4. Check that all dependencies are installed")
        
        import traceback
        print(f"\n🐛 Full error traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_ai_analysis())