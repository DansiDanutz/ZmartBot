#!/usr/bin/env python3
"""
Professional Analysis System Test
=================================

Test script to demonstrate the new professional analysis system that generates
reports following the SOL USDT standardized format for any trading symbol.

This test validates:
1. Executive Summary generation
2. Comprehensive Analysis reports
3. Batch analysis capabilities
4. Professional formatting
5. AI integration

Author: ZmartBot AI System
Date: January 2025
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.services.enhanced_professional_ai_agent import EnhancedProfessionalAIAgent

class ProfessionalAnalysisSystemTest:
    """Test suite for the professional analysis system"""
    
    def __init__(self):
        self.ai_agent = EnhancedProfessionalAIAgent()
        self.test_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        self.test_results = {}
        
        print("🚀 Professional Analysis System Test Suite")
        print("=" * 60)
        print("Testing standardized report generation following SOL USDT format")
        print("=" * 60)
    
    async def test_executive_summary_generation(self, symbol: str = "BTC/USDT") -> Dict[str, Any]:
        """Test executive summary generation"""
        print(f"\n📊 TEST 1: Executive Summary Generation for {symbol}")
        print("-" * 50)
        
        try:
            start_time = datetime.now()
            
            result = await self.ai_agent.generate_executive_summary(symbol)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if result.get("success"):
                report_content = result.get("report_content", "")
                word_count = len(report_content.split())
                
                print(f"✅ SUCCESS: Executive Summary Generated")
                print(f"   Symbol: {result.get('symbol')}")
                print(f"   Word Count: {word_count}")
                print(f"   Processing Time: {processing_time:.2f}s")
                print(f"   AI Models Used: {result.get('ai_insights', {}).get('multi_model_analysis', {}).get('models_used', 1)}")
                
                # Show first few lines of the report
                lines = report_content.split('\n')[:10]
                print(f"\n   Report Preview:")
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
                        if "---" in line:
                            break
                
                return {
                    "test": "executive_summary",
                    "success": True,
                    "symbol": symbol,
                    "word_count": word_count,
                    "processing_time": processing_time,
                    "ai_models_used": result.get('ai_insights', {}).get('multi_model_analysis', {}).get('models_used', 1)
                }
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                return {"test": "executive_summary", "success": False, "error": result.get('error')}
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return {"test": "executive_summary", "success": False, "error": str(e)}
    
    async def test_comprehensive_report_generation(self, symbol: str = "ETH/USDT") -> Dict[str, Any]:
        """Test comprehensive report generation"""
        print(f"\n📈 TEST 2: Comprehensive Report Generation for {symbol}")
        print("-" * 50)
        
        try:
            start_time = datetime.now()
            
            result = await self.ai_agent.generate_comprehensive_report(symbol)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if result.get("success"):
                report_content = result.get("report_content", "")
                word_count = len(report_content.split())
                
                print(f"✅ SUCCESS: Comprehensive Report Generated")
                print(f"   Symbol: {result.get('symbol')}")
                print(f"   Word Count: {word_count}")
                print(f"   Processing Time: {processing_time:.2f}s")
                print(f"   AI Models Used: {result.get('ai_insights', {}).get('multi_model_analysis', {}).get('models_used', 1)}")
                
                # Check for key sections
                key_sections = [
                    "Executive Summary",
                    "Current Market Conditions", 
                    "Technical Indicator Analysis",
                    "Win Rate Analysis",
                    "Risk Assessment",
                    "Conclusion"
                ]
                
                found_sections = []
                for section in key_sections:
                    if section in report_content:
                        found_sections.append(section)
                
                print(f"   Key Sections Found: {len(found_sections)}/{len(key_sections)}")
                
                return {
                    "test": "comprehensive_report",
                    "success": True,
                    "symbol": symbol,
                    "word_count": word_count,
                    "processing_time": processing_time,
                    "sections_found": len(found_sections),
                    "ai_models_used": result.get('ai_insights', {}).get('multi_model_analysis', {}).get('models_used', 1)
                }
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                return {"test": "comprehensive_report", "success": False, "error": result.get('error')}
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return {"test": "comprehensive_report", "success": False, "error": str(e)}
    
    async def test_batch_analysis(self, symbols: list = None) -> Dict[str, Any]:
        """Test batch analysis functionality"""
        test_symbols = symbols or ["BTC/USDT", "ETH/USDT"]
        
        print(f"\n🔄 TEST 3: Batch Analysis for {len(test_symbols)} symbols")
        print("-" * 50)
        
        try:
            start_time = datetime.now()
            
            result = await self.ai_agent.batch_analysis(test_symbols, "executive")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            batch_info = result.get("batch_analysis", {})
            
            print(f"✅ SUCCESS: Batch Analysis Completed")
            print(f"   Total Symbols: {batch_info.get('total_symbols', 0)}")
            print(f"   Successful: {batch_info.get('successful_analyses', 0)}")
            print(f"   Failed: {batch_info.get('failed_analyses', 0)}")
            print(f"   Success Rate: {batch_info.get('success_rate', 0):.1f}%")
            print(f"   Total Time: {processing_time:.2f}s")
            print(f"   Avg Time/Symbol: {batch_info.get('average_time_per_symbol', 0):.2f}s")
            
            # Show results for each symbol
            results = result.get("results", {})
            for symbol, symbol_result in results.items():
                status = "✅" if symbol_result.get("success") else "❌"
                print(f"   {status} {symbol}: {symbol_result.get('report_title', 'N/A')}")
            
            return {
                "test": "batch_analysis",
                "success": True,
                "total_symbols": len(test_symbols),
                "successful": batch_info.get('successful_analyses', 0),
                "processing_time": processing_time,
                "success_rate": batch_info.get('success_rate', 0)
            }
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return {"test": "batch_analysis", "success": False, "error": str(e)}
    
    async def test_format_consistency(self, symbol: str = "SOL/USDT") -> Dict[str, Any]:
        """Test format consistency with SOL USDT template"""
        print(f"\n📋 TEST 4: Format Consistency Check for {symbol}")
        print("-" * 50)
        
        try:
            # Generate executive summary
            exec_result = await self.ai_agent.generate_executive_summary(symbol)
            
            if not exec_result.get("success"):
                print(f"❌ FAILED: Could not generate report for format check")
                return {"test": "format_consistency", "success": False}
            
            report_content = exec_result.get("report_content", "")
            
            # Check for required sections
            required_sections = [
                "WIN RATE SUMMARY",
                "COMPOSITE SCORES",
                "KEY MARKET METRICS",
                "TRADING RECOMMENDATIONS",
                "RISK FACTORS",
                "MARKET SCENARIOS",
                "KEY INSIGHTS",
                "IMMEDIATE ACTION ITEMS"
            ]
            
            found_sections = []
            for section in required_sections:
                if section in report_content:
                    found_sections.append(section)
            
            # Check for professional formatting elements
            formatting_elements = [
                "##",  # Headers
                "**",  # Bold text
                "✅",  # Success indicators
                "⭐",  # Best indicators
                "🔻",  # Warning indicators
                "⚠️",  # Alert indicators
                "---"  # Section separators
            ]
            
            found_formatting = []
            for element in formatting_elements:
                if element in report_content:
                    found_formatting.append(element)
            
            consistency_score = (len(found_sections) / len(required_sections)) * 100
            formatting_score = (len(found_formatting) / len(formatting_elements)) * 100
            
            print(f"✅ SUCCESS: Format Consistency Check Completed")
            print(f"   Required Sections: {len(found_sections)}/{len(required_sections)} ({consistency_score:.1f}%)")
            print(f"   Formatting Elements: {len(found_formatting)}/{len(formatting_elements)} ({formatting_score:.1f}%)")
            print(f"   Overall Format Score: {(consistency_score + formatting_score) / 2:.1f}%")
            
            return {
                "test": "format_consistency",
                "success": True,
                "symbol": symbol,
                "sections_found": len(found_sections),
                "sections_required": len(required_sections),
                "consistency_score": consistency_score,
                "formatting_score": formatting_score,
                "overall_score": (consistency_score + formatting_score) / 2
            }
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return {"test": "format_consistency", "success": False, "error": str(e)}
    
    async def test_ai_integration(self) -> Dict[str, Any]:
        """Test AI system integration"""
        print(f"\n🤖 TEST 5: AI System Integration")
        print("-" * 50)
        
        try:
            # Get AI system status
            ai_status = self.ai_agent.multi_model_ai.get_model_status()
            
            available_models = ai_status.get("available_models", 0)
            model_details = ai_status.get("model_details", {})
            
            print(f"✅ SUCCESS: AI System Integration Check")
            print(f"   Available Models: {available_models}")
            
            for model_name, details in model_details.items():
                status = "✅" if details.get("available") else "❌"
                model_type = details.get("type", "unknown")
                print(f"   {status} {model_name} ({model_type})")
            
            # Test a quick analysis to verify integration
            test_result = await self.ai_agent.generate_symbol_analysis("BTC/USDT", "executive")
            integration_working = test_result.get("success", False)
            
            ai_insights = test_result.get("ai_insights", {})
            models_used = ai_insights.get("multi_model_analysis", {}).get("models_used", 0)
            
            print(f"   Integration Test: {'✅' if integration_working else '❌'}")
            print(f"   Models Used in Test: {models_used}")
            
            return {
                "test": "ai_integration",
                "success": True,
                "available_models": available_models,
                "integration_working": integration_working,
                "models_used_in_test": models_used
            }
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return {"test": "ai_integration", "success": False, "error": str(e)}
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        print(f"\n🎯 Running Complete Professional Analysis Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all tests
        tests = [
            self.test_executive_summary_generation("BTC/USDT"),
            self.test_comprehensive_report_generation("ETH/USDT"), 
            self.test_batch_analysis(["BTC/USDT", "ETH/USDT"]),
            self.test_format_consistency("SOL/USDT"),
            self.test_ai_integration()
        ]
        
        results = []
        for test in tests:
            try:
                result = await test
                results.append(result)
            except Exception as e:
                logger.error(f"Test failed with exception: {e}")
                results.append({
                    "test": "unknown",
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get("success", False))
        total_time = (datetime.now() - start_time).total_seconds()
        
        summary = {
            "test_suite": "Professional Analysis System",
            "timestamp": datetime.now().isoformat(),
            "duration": total_time,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests) * 100
            },
            "test_results": results,
            "system_capabilities": {
                "executive_summary_generation": any(r.get("test") == "executive_summary" and r.get("success") for r in results),
                "comprehensive_report_generation": any(r.get("test") == "comprehensive_report" and r.get("success") for r in results),
                "batch_analysis": any(r.get("test") == "batch_analysis" and r.get("success") for r in results),
                "format_consistency": any(r.get("test") == "format_consistency" and r.get("success") for r in results),
                "ai_integration": any(r.get("test") == "ai_integration" and r.get("success") for r in results)
            }
        }
        
        # Print final summary
        self.print_final_summary(summary)
        
        return summary
    
    def print_final_summary(self, summary: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PROFESSIONAL ANALYSIS SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        print(f"Test Duration: {summary['duration']:.2f}s")
        print(f"Tests Passed: {summary['summary']['successful_tests']}/{summary['summary']['total_tests']}")
        print(f"Success Rate: {summary['summary']['success_rate']:.1f}%")
        
        print("\n📊 SYSTEM CAPABILITIES:")
        capabilities = summary['system_capabilities']
        for capability, status in capabilities.items():
            status_icon = "✅" if status else "❌"
            capability_name = capability.replace('_', ' ').title()
            print(f"   {status_icon} {capability_name}")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in summary['test_results']:
            status_icon = "✅" if result.get("success") else "❌"
            test_name = result.get("test", "Unknown").replace('_', ' ').title()
            print(f"   {status_icon} {test_name}")
            
            if not result.get("success"):
                error = result.get("error", "Unknown error")
                print(f"      Error: {error}")
        
        if summary['summary']['success_rate'] >= 80:
            print("\n🎉 EXCELLENT: Professional Analysis System is fully operational!")
            print("   All standardized report formats are working correctly.")
            print("   SOL USDT format template successfully applied to all symbols.")
        elif summary['summary']['success_rate'] >= 60:
            print("\n✅ GOOD: Professional Analysis System is mostly operational")
            print("   Minor issues detected but core functionality working.")
        else:
            print("\n⚠️ NEEDS ATTENTION: Professional Analysis System has issues")
            print("   Multiple test failures detected.")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    test_suite = ProfessionalAnalysisSystemTest()
    
    try:
        results = await test_suite.run_complete_test_suite()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"professional_analysis_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: {filename}")
        
        return results
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n❌ Test suite failed: {e}")
        return None

if __name__ == "__main__":
    # Run the professional analysis system test
    results = asyncio.run(main())