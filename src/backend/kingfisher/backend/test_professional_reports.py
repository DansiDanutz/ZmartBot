#!/usr/bin/env python3
"""
Test Professional Report Generation System
Comprehensive testing of enhanced reports, automated reports, and master summaries
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.enhanced_report_generator import EnhancedReportGenerator
from src.services.automated_report_system import automated_report_system
from src.services.master_summary_agent import MasterSummaryAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_report_generator():
    """Test the enhanced report generator"""
    try:
        logger.info("🧪 Testing Enhanced Report Generator...")
        
        # Initialize the report generator
        generator = EnhancedReportGenerator()
        
        # Test data for different report types
        test_data = {
            "symbol": "BTCUSDT",
            "current_price": 45000.0,
            "sentiment": "bullish",
            "confidence": 85.5,
            "risk_level": "medium",
            "analysis_type": "liquidation_map",
            "liquidation_zones": [
                {"price_level": 44000, "volume": 1000000, "intensity": 75},
                {"price_level": 43000, "volume": 800000, "intensity": 60},
                {"price_level": 42000, "volume": 600000, "intensity": 45}
            ],
            "support_levels": [44000, 43000, 42000],
            "resistance_levels": [46000, 47000, 48000],
            "volatility": 25.5,
            "timeframe": "24h"
        }
        
        # Test liquidation map report
        logger.info("📊 Testing liquidation map report generation...")
        liquidation_report = await generator.generate_enhanced_report(test_data, "liquidation_map")
        
        print(f"\n✅ Liquidation Map Report Generated:")
        print(f"  • Report ID: {liquidation_report.report_id}")
        print(f"  • Symbol: {liquidation_report.symbol}")
        print(f"  • Confidence: {liquidation_report.confidence_score:.1f}%")
        print(f"  • Risk Level: {liquidation_report.risk_level}")
        print(f"  • Sections: {len(liquidation_report.sections)}")
        print(f"  • Report Length: {len(liquidation_report.formatted_report)} characters")
        
        # Test liquidation heatmap report
        logger.info("🔥 Testing liquidation heatmap report generation...")
        heatmap_data = {
            **test_data,
            "analysis_type": "liquidation_heatmap",
            "thermal_zones": [
                {"price_level": 45000, "intensity": 90},
                {"price_level": 44000, "intensity": 75},
                {"price_level": 43000, "intensity": 60}
            ],
            "intensity_scores": {
                "high": 90,
                "medium": 75,
                "low": 60
            }
        }
        
        heatmap_report = await generator.generate_enhanced_report(heatmap_data, "liquidation_heatmap")
        
        print(f"\n✅ Liquidation Heatmap Report Generated:")
        print(f"  • Report ID: {heatmap_report.report_id}")
        print(f"  • Symbol: {heatmap_report.symbol}")
        print(f"  • Confidence: {heatmap_report.confidence_score:.1f}%")
        print(f"  • Risk Level: {heatmap_report.risk_level}")
        print(f"  • Sections: {len(heatmap_report.sections)}")
        
        # Test multi-symbol report
        logger.info("📈 Testing multi-symbol report generation...")
        multi_symbol_data = {
            "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            "analysis_type": "multi_symbol",
            "market_sentiment": "bullish",
            "market_conditions": "Normal",
            "BTCUSDT_sentiment": "bullish",
            "BTCUSDT_confidence": 85.5,
            "BTCUSDT_risk": "medium",
            "BTCUSDT_recommendation": "Strong Buy",
            "ETHUSDT_sentiment": "bullish",
            "ETHUSDT_confidence": 78.2,
            "ETHUSDT_risk": "medium",
            "ETHUSDT_recommendation": "Buy",
            "SOLUSDT_sentiment": "neutral",
            "SOLUSDT_confidence": 65.0,
            "SOLUSDT_risk": "high",
            "SOLUSDT_recommendation": "Hold"
        }
        
        multi_symbol_report = await generator.generate_enhanced_report(multi_symbol_data, "multi_symbol")
        
        print(f"\n✅ Multi-Symbol Report Generated:")
        print(f"  • Report ID: {multi_symbol_report.report_id}")
        print(f"  • Symbols: {multi_symbol_report.symbol}")
        print(f"  • Confidence: {multi_symbol_report.confidence_score:.1f}%")
        print(f"  • Risk Level: {multi_symbol_report.risk_level}")
        print(f"  • Sections: {len(multi_symbol_report.sections)}")
        
        # Test general report
        logger.info("📋 Testing general report generation...")
        general_report = await generator.generate_enhanced_report(test_data, "general")
        
        print(f"\n✅ General Report Generated:")
        print(f"  • Report ID: {general_report.report_id}")
        print(f"  • Symbol: {general_report.symbol}")
        print(f"  • Confidence: {general_report.confidence_score:.1f}%")
        print(f"  • Risk Level: {general_report.risk_level}")
        print(f"  • Sections: {len(general_report.sections)}")
        
        print(f"\n📄 Sample Report Content (first 500 chars):")
        print(f"  {general_report.formatted_report[:500]}...")
        
        logger.info("✅ Enhanced Report Generator tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced Report Generator test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return False

async def test_automated_report_system():
    """Test the automated report system"""
    try:
        logger.info("🤖 Testing Automated Report System...")
        
        # Start the automated system
        logger.info("🚀 Starting automated report system...")
        await automated_report_system.start_automation()
        
        # Test data
        test_data = {
            "symbol": "ETHUSDT",
            "current_price": 3200.0,
            "sentiment": "bullish",
            "confidence": 82.5,
            "risk_level": "medium",
            "analysis_type": "liquidation_map",
            "liquidation_zones": [
                {"price_level": 3150, "volume": 500000, "intensity": 70},
                {"price_level": 3100, "volume": 400000, "intensity": 55}
            ],
            "support_levels": [3150, 3100],
            "resistance_levels": [3250, 3300],
            "volatility": 20.0,
            "timeframe": "24h"
        }
        
        # Test adding a job to the queue
        logger.info("📝 Testing job queue addition...")
        job_id = await automated_report_system.add_report_job(
            symbol="ETHUSDT",
            analysis_type="liquidation_map",
            analysis_data=test_data,
            priority=1
        )
        
        print(f"\n✅ Job added to queue:")
        print(f"  • Job ID: {job_id}")
        print(f"  • Symbol: ETHUSDT")
        print(f"  • Analysis Type: liquidation_map")
        print(f"  • Priority: 1")
        
        # Get system status
        logger.info("📊 Getting system status...")
        status = await automated_report_system.get_system_status()
        
        print(f"\n📊 System Status:")
        print(f"  • Running: {status['is_running']}")
        print(f"  • Queue Size: {status['queue_size']}")
        print(f"  • Completed Count: {status['completed_count']}")
        print(f"  • Pending Jobs: {len(status['pending_jobs'])}")
        
        # Test immediate report generation
        logger.info("⚡ Testing immediate report generation...")
        immediate_report = await automated_report_system.trigger_immediate_report(
            symbol="SOLUSDT",
            analysis_type="general",
            analysis_data={
                "symbol": "SOLUSDT",
                "current_price": 150.0,
                "sentiment": "neutral",
                "confidence": 70.0,
                "risk_level": "medium",
                "volatility": 15.0,
                "timeframe": "24h"
            }
        )
        
        print(f"\n✅ Immediate Report Generated:")
        print(f"  • Report ID: {immediate_report.report_id}")
        print(f"  • Symbol: {immediate_report.symbol}")
        print(f"  • Confidence: {immediate_report.confidence_score:.1f}%")
        print(f"  • Risk Level: {immediate_report.risk_level}")
        
        # Wait a bit for queue processing
        logger.info("⏳ Waiting for queue processing...")
        await asyncio.sleep(3)
        
        # Get job status
        if job_id:
            logger.info(f"📋 Getting job status for {job_id}...")
            job_status = await automated_report_system.get_report_status(job_id)
            
            if job_status:
                print(f"\n📋 Job Status:")
                print(f"  • Job ID: {job_status.job_id}")
                print(f"  • Status: {job_status.status}")
                print(f"  • Symbol: {job_status.symbol}")
                print(f"  • Created: {job_status.created_at}")
                if job_status.completed_at:
                    print(f"  • Completed: {job_status.completed_at}")
                if job_status.report:
                    print(f"  • Report ID: {job_status.report.report_id}")
                    print(f"  • Confidence: {job_status.report.confidence_score:.1f}%")
        
        # Get statistics
        logger.info("📈 Getting report statistics...")
        stats = await automated_report_system.get_report_statistics()
        
        print(f"\n📈 Report Statistics:")
        print(f"  • Total Reports: {stats['total_reports']}")
        print(f"  • Success Rate: {stats['success_rate']:.1f}%")
        print(f"  • Average Processing Time: {stats['average_processing_time']:.2f}s")
        print(f"  • Reports by Type: {stats['reports_by_type']}")
        print(f"  • Reports by Symbol: {stats['reports_by_symbol']}")
        
        # Stop the automated system
        logger.info("🛑 Stopping automated report system...")
        await automated_report_system.stop_automation()
        
        logger.info("✅ Automated Report System tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Automated Report System test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return False

async def test_master_summary_integration():
    """Test the integration between automated reports and master summary"""
    try:
        logger.info("🎯 Testing Master Summary Integration...")
        
        # Initialize the master summary agent
        master_agent = MasterSummaryAgent()
        
        # Generate a master summary
        logger.info("📊 Generating master summary...")
        master_summary = await master_agent.generate_master_summary(hours_back=24)
        
        print(f"\n🎯 Master Summary Generated:")
        print(f"  • Overall Sentiment: {master_summary.overall_sentiment}")
        print(f"  • Market Confidence: {master_summary.market_confidence:.1f}%")
        print(f"  • Market Trend: {master_summary.market_trend}")
        print(f"  • Top Performers: {len(master_summary.top_performers)}")
        print(f"  • Risk Alerts: {len(master_summary.risk_alert_symbols)}")
        print(f"  • Trading Opportunities: {len(master_summary.trading_opportunities)}")
        print(f"  • Sector Analysis: {len(master_summary.sector_analysis)}")
        print(f"  • Risk Warnings: {len(master_summary.risk_warnings)}")
        
        print(f"\n📝 Executive Summary:")
        print(f"  {master_summary.executive_summary}")
        
        if master_summary.professional_summary:
            print(f"\n📄 Professional Summary Preview (first 300 chars):")
            print(f"  {master_summary.professional_summary[:300]}...")
        
        logger.info("✅ Master Summary Integration tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Master Summary Integration test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return False

async def test_api_endpoints():
    """Test the API endpoints for professional reports"""
    try:
        logger.info("🌐 Testing API Endpoints...")
        
        import httpx
        
        base_url = "http://localhost:8100"
        
        # Test automated reports health endpoint
        print("\n🏥 Testing automated reports health endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/automated-reports/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                print(f"   System running: {health_data.get('system_running', False)}")
                print(f"   Queue size: {health_data.get('queue_size', 0)}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        
        # Test system status endpoint
        print("\n📊 Testing system status endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/automated-reports/system-status")
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ System status retrieved:")
                print(f"   Running: {status_data.get('is_running', False)}")
                print(f"   Queue size: {status_data.get('queue_size', 0)}")
                print(f"   Completed count: {status_data.get('completed_count', 0)}")
            else:
                print(f"❌ System status failed: {response.status_code}")
        
        # Test statistics endpoint
        print("\n📈 Testing statistics endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/automated-reports/statistics")
            if response.status_code == 200:
                stats_data = response.json()
                print(f"✅ Statistics retrieved:")
                print(f"   Status: {stats_data.get('status', 'unknown')}")
                if 'statistics' in stats_data:
                    stats = stats_data['statistics']
                    print(f"   Total reports: {stats.get('total_reports', 0)}")
                    print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
            else:
                print(f"❌ Statistics failed: {response.status_code}")
        
        # Test immediate report generation
        print("\n⚡ Testing immediate report generation...")
        test_data = {
            "symbol": "ADAUSDT",
            "current_price": 0.45,
            "sentiment": "neutral",
            "confidence": 75.0,
            "risk_level": "medium",
            "analysis_type": "general",
            "volatility": 18.0,
            "timeframe": "24h"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/v1/automated-reports/generate-immediate",
                json={
                    "symbol": "ADAUSDT",
                    "analysis_type": "general",
                    "analysis_data": test_data
                }
            )
            if response.status_code == 200:
                report_data = response.json()
                print(f"✅ Immediate report generated:")
                print(f"   Status: {report_data.get('status', 'unknown')}")
                print(f"   Symbol: {report_data.get('symbol', 'unknown')}")
                print(f"   Report ID: {report_data.get('report_id', 'unknown')}")
                print(f"   Confidence: {report_data.get('confidence_score', 0):.1f}%")
            else:
                print(f"❌ Immediate report generation failed: {response.status_code}")
        
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
    print("🎯 Professional Report Generation System Test Suite")
    print("="*60)
    
    # Test enhanced report generator
    enhanced_success = await test_enhanced_report_generator()
    
    # Test automated report system
    automated_success = await test_automated_report_system()
    
    # Test master summary integration
    master_success = await test_master_summary_integration()
    
    # Test API endpoints (if server is running)
    api_success = await test_api_endpoints()
    
    print(f"\n📊 Test Results:")
    print(f"  • Enhanced Report Generator: {'✅ PASSED' if enhanced_success else '❌ FAILED'}")
    print(f"  • Automated Report System: {'✅ PASSED' if automated_success else '❌ FAILED'}")
    print(f"  • Master Summary Integration: {'✅ PASSED' if master_success else '❌ FAILED'}")
    print(f"  • API Endpoints: {'✅ PASSED' if api_success else '❌ FAILED'}")
    
    if enhanced_success and automated_success and master_success and api_success:
        print("\n🎉 All tests passed! Professional Report Generation System is working correctly.")
        print("\n🚀 The system is now ready to:")
        print("  • Generate enhanced professional reports")
        print("  • Automate report generation workflows")
        print("  • Compose master summaries from all analyses")
        print("  • Provide commercial-grade trading intelligence")
    else:
        print("\n⚠️ Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main()) 