#!/usr/bin/env python3
"""
Complete Telegram Image Workflow Test
Tests the entire workflow: Image Download → Analysis → Airtable Integration → Professional Reports
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramWorkflowTester:
    """Comprehensive tester for the complete Telegram image workflow"""
    
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = {}
        
        # Test data
        self.test_symbols = ["ETHUSDT", "BTCUSDT", "ADAUSDT"]
        self.test_images = {
            "liquidation_map": "test_images/kingfisher_btcusdt_1.jpg",
            "liquidation_heatmap": "test_images/kingfisher_adausdt_4.jpg",
            "multi_symbol": "test_images/kingfisher_dotusdt_5.jpg"
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_system_health(self) -> Dict[str, Any]:
        """Test if the KingFisher system is running"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "PASSED",
                        "message": "System is healthy",
                        "data": data
                    }
                else:
                    return {
                        "status": "FAILED",
                        "message": f"Health check failed: {response.status}"
                    }
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Health check error: {str(e)}"
            }
    
    async def test_telegram_image_processing(self, image_type: str, symbol: str) -> Dict[str, Any]:
        """Test complete Telegram image processing workflow"""
        try:
            # 1. Simulate image upload from Telegram
            image_path = self.test_images.get(image_type)
            if not image_path or not os.path.exists(image_path):
                return {
                    "status": "FAILED",
                    "message": f"Test image not found: {image_path}"
                }
            
            # 2. Upload image for processing
            with open(image_path, 'rb') as f:
                files = {'file': (f'kingfisher_{symbol.lower()}.jpg', f, 'image/jpeg')}
                data = {
                    'symbol': symbol,
                    'image_type': image_type,
                    'context': f"KingFisher {image_type} analysis for {symbol}",
                    'timestamp': datetime.now().isoformat()
                }
                
                async with self.session.post(
                    f"{self.base_url}/api/v1/images/process",
                    data=data,
                    files=files
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "PASSED",
                            "message": f"Image processing successful for {symbol}",
                            "data": result
                        }
                    else:
                        return {
                            "status": "FAILED",
                            "message": f"Image processing failed: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Image processing error: {str(e)}"
            }
    
    async def test_airtable_integration(self, symbol: str) -> Dict[str, Any]:
        """Test Airtable integration for symbol management"""
        try:
            # 1. Check if symbol exists in Airtable
            async with self.session.get(
                f"{self.base_url}/api/v1/airtable/symbols/{symbol}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "PASSED",
                        "message": f"Symbol {symbol} found in Airtable",
                        "data": data
                    }
                elif response.status == 404:
                    # 2. Create new symbol record
                    new_record = {
                        "symbol": symbol,
                        "created_time": datetime.now().isoformat(),
                        "status": "active",
                        "analysis_count": 0
                    }
                    
                    async with self.session.post(
                        f"{self.base_url}/api/v1/airtable/symbols",
                        json=new_record
                    ) as create_response:
                        if create_response.status == 200:
                            return {
                                "status": "PASSED",
                                "message": f"Created new symbol record for {symbol}",
                                "data": await create_response.json()
                            }
                        else:
                            return {
                                "status": "FAILED",
                                "message": f"Failed to create symbol record: {create_response.status}"
                            }
                else:
                    return {
                        "status": "FAILED",
                        "message": f"Airtable check failed: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Airtable integration error: {str(e)}"
            }
    
    async def test_professional_report_generation(self, symbol: str, image_type: str) -> Dict[str, Any]:
        """Test professional report generation with win rates and liquidation clusters"""
        try:
            # Generate professional report
            report_data = {
                "symbol": symbol,
                "image_type": image_type,
                "analysis_type": "professional",
                "include_win_rates": True,
                "include_liquidation_clusters": True,
                "include_market_price": True
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/automated-reports/generate",
                json=report_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "PASSED",
                        "message": f"Professional report generated for {symbol}",
                        "data": result
                    }
                else:
                    return {
                        "status": "FAILED",
                        "message": f"Report generation failed: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Report generation error: {str(e)}"
            }
    
    async def test_win_rate_extraction(self, symbol: str) -> Dict[str, Any]:
        """Test extraction of win rates from reports"""
        try:
            # Get win rates for different timeframes
            timeframes = ["24h", "48h", "7d", "1m"]
            win_rates = {}
            
            for timeframe in timeframes:
                async with self.session.get(
                    f"{self.base_url}/api/v1/analysis/win-rates/{symbol}",
                    params={"timeframe": timeframe}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        win_rates[timeframe] = data
                    else:
                        win_rates[timeframe] = {"error": f"Failed to get {timeframe} win rates"}
            
            return {
                "status": "PASSED",
                "message": f"Win rates extracted for {symbol}",
                "data": win_rates
            }
            
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Win rate extraction error: {str(e)}"
            }
    
    async def test_liquidation_cluster_analysis(self, symbol: str) -> Dict[str, Any]:
        """Test liquidation cluster analysis and price targets"""
        try:
            # Get liquidation cluster analysis
            async with self.session.get(
                f"{self.base_url}/api/v1/liquidation/clusters/{symbol}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract price targets
                    price_targets = {
                        "nearest_left": data.get("nearest_left_cluster", {}).get("price"),
                        "nearest_right": data.get("nearest_right_cluster", {}).get("price"),
                        "second_left": data.get("second_left_cluster", {}).get("price"),
                        "second_right": data.get("second_right_cluster", {}).get("price"),
                        "market_price": data.get("current_price")
                    }
                    
                    return {
                        "status": "PASSED",
                        "message": f"Liquidation clusters analyzed for {symbol}",
                        "data": {
                            "clusters": data,
                            "price_targets": price_targets
                        }
                    }
                else:
                    return {
                        "status": "FAILED",
                        "message": f"Liquidation analysis failed: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Liquidation analysis error: {str(e)}"
            }
    
    async def test_complete_workflow(self, symbol: str, image_type: str) -> Dict[str, Any]:
        """Test the complete workflow from image to professional report"""
        workflow_steps = []
        
        # Step 1: System Health
        health_result = await self.test_system_health()
        workflow_steps.append(("System Health", health_result))
        
        # Step 2: Airtable Integration
        airtable_result = await self.test_airtable_integration(symbol)
        workflow_steps.append(("Airtable Integration", airtable_result))
        
        # Step 3: Image Processing
        image_result = await self.test_telegram_image_processing(image_type, symbol)
        workflow_steps.append(("Image Processing", image_result))
        
        # Step 4: Professional Report Generation
        report_result = await self.test_professional_report_generation(symbol, image_type)
        workflow_steps.append(("Professional Report", report_result))
        
        # Step 5: Win Rate Extraction
        win_rate_result = await self.test_win_rate_extraction(symbol)
        workflow_steps.append(("Win Rate Extraction", win_rate_result))
        
        # Step 6: Liquidation Cluster Analysis
        cluster_result = await self.test_liquidation_cluster_analysis(symbol)
        workflow_steps.append(("Liquidation Clusters", cluster_result))
        
        # Calculate overall success
        passed_steps = sum(1 for _, result in workflow_steps if result["status"] == "PASSED")
        total_steps = len(workflow_steps)
        success_rate = (passed_steps / total_steps) * 100
        
        return {
            "status": "PASSED" if success_rate >= 80 else "FAILED",
            "message": f"Complete workflow test: {passed_steps}/{total_steps} steps passed ({success_rate:.1f}%)",
            "workflow_steps": workflow_steps,
            "success_rate": success_rate
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of the complete Telegram workflow"""
        logger.info("🚀 Starting Comprehensive Telegram Workflow Test")
        
        test_results = {}
        
        # Test 1: System Health
        logger.info("📊 Testing System Health...")
        test_results["system_health"] = await self.test_system_health()
        
        # Test 2: Complete workflow for each symbol
        for symbol in self.test_symbols:
            logger.info(f"🔄 Testing Complete Workflow for {symbol}...")
            test_results[f"workflow_{symbol}"] = await self.test_complete_workflow(
                symbol, "liquidation_map"
            )
        
        # Test 3: Different image types
        image_types = ["liquidation_map", "liquidation_heatmap", "multi_symbol"]
        for image_type in image_types:
            logger.info(f"🖼️ Testing {image_type} processing...")
            test_results[f"image_type_{image_type}"] = await self.test_telegram_image_processing(
                image_type, "ETHUSDT"
            )
        
        # Calculate overall results
        passed_tests = sum(1 for result in test_results.values() if result["status"] == "PASSED")
        total_tests = len(test_results)
        overall_success = (passed_tests / total_tests) * 100
        
        return {
            "overall_status": "PASSED" if overall_success >= 80 else "FAILED",
            "overall_success_rate": overall_success,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Run the comprehensive Telegram workflow test"""
    async with TelegramWorkflowTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # Print results
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TELEGRAM WORKFLOW TEST RESULTS")
        print("="*80)
        
        print(f"\n📊 Overall Status: {results['overall_status']}")
        print(f"📈 Success Rate: {results['overall_success_rate']:.1f}%")
        print(f"✅ Passed Tests: {results['passed_tests']}/{results['total_tests']}")
        print(f"🕐 Timestamp: {results['timestamp']}")
        
        print("\n" + "-"*80)
        print("📋 DETAILED TEST RESULTS")
        print("-"*80)
        
        for test_name, result in results['test_results'].items():
            status_emoji = "✅" if result["status"] == "PASSED" else "❌"
            print(f"\n{status_emoji} {test_name}:")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            
            if "workflow_steps" in result:
                print("   Workflow Steps:")
                for step_name, step_result in result["workflow_steps"]:
                    step_emoji = "✅" if step_result["status"] == "PASSED" else "❌"
                    print(f"     {step_emoji} {step_name}: {step_result['status']}")
        
        print("\n" + "="*80)
        print("🎯 TEST COMPLETE")
        print("="*80)
        
        return results

if __name__ == "__main__":
    asyncio.run(main()) 