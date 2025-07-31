#!/usr/bin/env python3
"""
Test script for KingFisher Master Summary Agent
Tests the multi-agent system to control KingFisher summary results
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.master_summary_agent import MasterSummaryAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_master_summary_agent():
    """Test the Master Summary Agent functionality"""
    try:
        logger.info("🧪 Testing KingFisher Master Summary Agent...")
        
        # Initialize the Master Summary Agent
        agent = MasterSummaryAgent()
        
        # Test 1: Test the agent
        logger.info("📊 Test 1: Testing Master Summary Agent...")
        test_result = await agent.test_master_summary()
        
        print("\n" + "="*60)
        print("🎯 MASTER SUMMARY AGENT TEST RESULTS")
        print("="*60)
        print(f"Status: {test_result.get('status', 'unknown')}")
        print(f"Timestamp: {test_result.get('timestamp', 'unknown')}")
        
        if test_result.get('status') == 'success':
            summary_stats = test_result.get('summary_stats', {})
            print(f"\n📈 Summary Statistics:")
            print(f"  • Overall Sentiment: {summary_stats.get('overall_sentiment', 'N/A')}")
            print(f"  • Market Confidence: {summary_stats.get('market_confidence', 0):.1f}%")
            print(f"  • Top Performers Count: {summary_stats.get('top_performers_count', 0)}")
            print(f"  • Risk Alerts Count: {summary_stats.get('risk_alerts_count', 0)}")
            print(f"  • Trading Opportunities: {summary_stats.get('trading_opportunities_count', 0)}")
            print(f"  • Sector Analysis Count: {summary_stats.get('sector_analysis_count', 0)}")
            print(f"  • Risk Warnings Count: {summary_stats.get('risk_warnings_count', 0)}")
            print(f"  • Executive Summary: {test_result.get('executive_summary', 'N/A')}")
            print(f"  • Professional Summary Length: {summary_stats.get('professional_summary_length', 0)} characters")
        else:
            print(f"❌ Test failed: {test_result.get('error', 'Unknown error')}")
        
        # Test 2: Generate actual master summary
        logger.info("📊 Test 2: Generating Master Summary...")
        master_summary = await agent.generate_master_summary(hours_back=24)
        
        print("\n" + "="*60)
        print("🎯 MASTER SUMMARY GENERATION RESULTS")
        print("="*60)
        print(f"Overall Sentiment: {master_summary.overall_sentiment}")
        print(f"Market Confidence: {master_summary.market_confidence:.1f}%")
        print(f"Market Trend: {master_summary.market_trend}")
        print(f"Top Performers: {', '.join(master_summary.top_performers) if master_summary.top_performers else 'None'}")
        print(f"Risk Alert Symbols: {', '.join(master_summary.risk_alert_symbols) if master_summary.risk_alert_symbols else 'None'}")
        print(f"Trading Opportunities: {len(master_summary.trading_opportunities)}")
        print(f"Sector Analysis: {len(master_summary.sector_analysis)} sectors")
        print(f"Risk Warnings: {len(master_summary.risk_warnings)}")
        
        print(f"\n📝 Executive Summary:")
        print(f"  {master_summary.executive_summary}")
        
        if master_summary.professional_summary:
            print(f"\n📄 Professional Summary Preview (first 500 chars):")
            print(f"  {master_summary.professional_summary[:500]}...")
        
        # Test 3: Test with different timeframes
        logger.info("📊 Test 3: Testing different timeframes...")
        timeframes = [1, 6, 12, 24, 48]
        
        for hours in timeframes:
            try:
                summary = await agent.generate_master_summary(hours_back=hours)
                print(f"\n⏰ {hours}h Summary:")
                print(f"  • Symbols analyzed: {len(summary.trading_opportunities) + len(summary.risk_alert_symbols)}")
                print(f"  • Sentiment: {summary.overall_sentiment}")
                print(f"  • Confidence: {summary.market_confidence:.1f}%")
            except Exception as e:
                print(f"  ❌ Error with {hours}h timeframe: {str(e)}")
        
        print("\n" + "="*60)
        print("✅ MASTER SUMMARY AGENT TEST COMPLETED")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Master Summary Agent test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return False

async def test_api_endpoints():
    """Test the Master Summary API endpoints"""
    try:
        logger.info("🌐 Testing Master Summary API endpoints...")
        
        import httpx
        
        base_url = "http://localhost:8100"
        
        # Test health endpoint
        print("\n🏥 Testing health endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/master-summary/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                print(f"   Airtable connection: {health_data.get('airtable_connection', 'unknown')}")
                print(f"   Records available: {health_data.get('records_available', 0)}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        
        # Test stats endpoint
        print("\n📈 Testing stats endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/master-summary/stats")
            if response.status_code == 200:
                stats_data = response.json()
                print(f"✅ Stats retrieved:")
                print(f"   Total records: {stats_data.get('total_records', 0)}")
                print(f"   Valid summaries: {stats_data.get('valid_summaries', 0)}")
                print(f"   Symbols analyzed: {len(stats_data.get('symbols_analyzed', []))}")
            else:
                print(f"❌ Stats failed: {response.status_code}")
        
        # Test latest summary endpoint
        print("\n📊 Testing latest summary endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/master-summary/latest")
            if response.status_code == 200:
                summary_data = response.json()
                print(f"✅ Latest summary retrieved:")
                print(f"   Status: {summary_data.get('status', 'unknown')}")
                print(f"   Sentiment: {summary_data.get('overall_sentiment', 'unknown')}")
                print(f"   Confidence: {summary_data.get('market_confidence', 0):.1f}%")
                print(f"   Trading opportunities: {summary_data.get('trading_opportunities_count', 0)}")
            else:
                print(f"❌ Latest summary failed: {response.status_code}")
        
        # Test generate endpoint
        print("\n🎯 Testing generate endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/v1/master-summary/generate",
                json={"hours_back": 24, "include_sector_analysis": True, "include_risk_warnings": True}
            )
            if response.status_code == 200:
                generate_data = response.json()
                print(f"✅ Summary generated:")
                print(f"   Status: {generate_data.get('status', 'unknown')}")
                print(f"   Sentiment: {generate_data.get('overall_sentiment', 'unknown')}")
                print(f"   Confidence: {generate_data.get('market_confidence', 0):.1f}%")
                print(f"   Executive summary: {generate_data.get('executive_summary', 'N/A')[:100]}...")
            else:
                print(f"❌ Generate failed: {response.status_code}")
        
        print("\n" + "="*60)
        print("✅ API ENDPOINTS TEST COMPLETED")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API endpoints test failed: {str(e)}")
        print(f"\n❌ API test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🎯 KingFisher Master Summary Agent Test Suite")
    print("="*60)
    
    # Test the agent directly
    agent_success = await test_master_summary_agent()
    
    # Test API endpoints (if server is running)
    api_success = await test_api_endpoints()
    
    print(f"\n📊 Test Results:")
    print(f"  • Agent Test: {'✅ PASSED' if agent_success else '❌ FAILED'}")
    print(f"  • API Test: {'✅ PASSED' if api_success else '❌ FAILED'}")
    
    if agent_success and api_success:
        print("\n🎉 All tests passed! Master Summary Agent is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main()) 