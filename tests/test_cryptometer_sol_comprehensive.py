#!/usr/bin/env python3
"""
Comprehensive Cryptometer Test for SOL/USDT
===========================================

This test validates all our advanced Cryptometer capabilities:
1. Unified Cryptometer System
2. Multi-Model AI Analysis 
3. Historical Pattern Analysis
4. Self-Learning System
5. Calibrated Scoring
6. Professional Report Generation

Author: ZmartBot AI System
Date: January 2025
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our advanced systems
from src.services.unified_cryptometer_system import UnifiedCryptometerSystem
from src.services.multi_model_ai_agent import MultiModelAIAgent
from src.services.historical_ai_analysis_agent import HistoricalAIAnalysisAgent
from src.services.calibrated_scoring_service import CalibratedScoringService
from src.services.cryptometer_endpoint_analyzer import CryptometerEndpointAnalyzer

class CryptometerSOLTest:
    """Comprehensive test suite for SOL/USDT analysis"""
    
    def __init__(self):
        self.symbol = "SOL/USDT"
        self.test_results = {}
        self.start_time = datetime.now()
        
        # Initialize all systems
        self.unified_system = UnifiedCryptometerSystem()
        self.multi_model_ai = MultiModelAIAgent()
        self.historical_ai = HistoricalAIAnalysisAgent()
        self.calibrated_scoring = CalibratedScoringService()
        self.endpoint_analyzer = CryptometerEndpointAnalyzer()
        
        print("🚀 Cryptometer SOL/USDT Comprehensive Test Suite")
        print("=" * 60)
        print(f"Symbol: {self.symbol}")
        print(f"Test Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    async def test_1_unified_cryptometer_system(self) -> Dict[str, Any]:
        """Test 1: Unified Cryptometer System"""
        print("\n🔬 TEST 1: Unified Cryptometer System")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Test complete symbol analysis
            result = await self.unified_system.analyze_symbol_complete(self.symbol)
            
            processing_time = time.time() - start_time
            
            test_result = {
                "test_name": "Unified Cryptometer System",
                "success": True,
                "processing_time": processing_time,
                "symbol": result.get("symbol"),
                "final_score": result.get("final_score"),
                "confidence": result.get("confidence"),
                "direction": result.get("direction"),
                "patterns_detected": len(result.get("patterns_detected", [])),
                "learning_insights": len(result.get("learning_insights", [])),
                "risk_assessment": result.get("risk_assessment"),
                "details": {
                    "endpoints_analyzed": result.get("endpoints_analyzed", 0),
                    "successful_endpoints": result.get("successful_endpoints", 0),
                    "pattern_strength": result.get("pattern_strength"),
                    "market_conditions": result.get("market_conditions")
                }
            }
            
            print(f"✅ SUCCESS: {test_result['symbol']}")
            print(f"   Final Score: {test_result['final_score']:.1f}%")
            print(f"   Confidence: {test_result['confidence']:.2f}")
            print(f"   Direction: {test_result['direction']}")
            print(f"   Patterns: {test_result['patterns_detected']}")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            return test_result
            
        except Exception as e:
            error_result = {
                "test_name": "Unified Cryptometer System",
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            print(f"❌ FAILED: {str(e)}")
            return error_result
    
    async def test_2_multi_model_ai_analysis(self) -> Dict[str, Any]:
        """Test 2: Multi-Model AI Analysis"""
        print("\n🤖 TEST 2: Multi-Model AI Analysis")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Test with all available models
            result = await self.multi_model_ai.generate_comprehensive_analysis(
                self.symbol, 
                use_all_models=True
            )
            
            processing_time = time.time() - start_time
            
            multi_model_data = result.get("multi_model_analysis", {})
            system_status = result.get("system_status", {})
            
            test_result = {
                "test_name": "Multi-Model AI Analysis",
                "success": True,
                "processing_time": processing_time,
                "primary_model": multi_model_data.get("primary_model"),
                "models_used": multi_model_data.get("models_used", 0),
                "aggregate_confidence": multi_model_data.get("aggregate_confidence", 0),
                "available_models": system_status.get("available_models", 0),
                "fallback_active": system_status.get("fallback_active", False),
                "model_comparisons": len(result.get("model_comparisons", [])),
                "technical_data": result.get("technical_data", {}),
                "details": {
                    "total_processing_time": multi_model_data.get("total_processing_time", 0),
                    "model_availability": system_status.get("model_availability", {}),
                    "primary_analysis_preview": multi_model_data.get("primary_analysis", "")[:200] + "..."
                }
            }
            
            print(f"✅ SUCCESS: Multi-Model Analysis")
            print(f"   Primary Model: {test_result['primary_model']}")
            print(f"   Models Used: {test_result['models_used']}")
            print(f"   Available Models: {test_result['available_models']}")
            print(f"   Aggregate Confidence: {test_result['aggregate_confidence']:.2f}")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            return test_result
            
        except Exception as e:
            error_result = {
                "test_name": "Multi-Model AI Analysis",
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            print(f"❌ FAILED: {str(e)}")
            return error_result
    
    async def test_3_historical_pattern_analysis(self) -> Dict[str, Any]:
        """Test 3: Historical Pattern Analysis"""
        print("\n📊 TEST 3: Historical Pattern Analysis")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Test historical analysis with pattern learning
            result = await self.historical_ai.generate_historical_enhanced_report(
                self.symbol,
                store_prediction=True
            )
            
            processing_time = time.time() - start_time
            
            test_result = {
                "test_name": "Historical Pattern Analysis",
                "success": True,
                "processing_time": processing_time,
                "prediction_id": result.get("prediction_id"),
                "historical_score": result.get("historical_score"),
                "pattern_confidence": result.get("pattern_confidence"),
                "timeframe_analysis": result.get("timeframe_analysis", {}),
                "top_patterns": len(result.get("top_patterns", [])),
                "win_rate_prediction": result.get("win_rate_prediction"),
                "report_length": len(result.get("report_content", "")),
                "details": {
                    "patterns_found": result.get("patterns_found", 0),
                    "historical_matches": result.get("historical_matches", 0),
                    "confidence_factors": result.get("confidence_factors", []),
                    "risk_assessment": result.get("risk_assessment")
                }
            }
            
            print(f"✅ SUCCESS: Historical Analysis")
            print(f"   Prediction ID: {test_result['prediction_id']}")
            print(f"   Historical Score: {test_result['historical_score']:.1f}%")
            print(f"   Pattern Confidence: {test_result['pattern_confidence']:.2f}")
            print(f"   Win Rate Prediction: {test_result['win_rate_prediction']:.1f}%")
            print(f"   Report Length: {test_result['report_length']} chars")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            return test_result
            
        except Exception as e:
            error_result = {
                "test_name": "Historical Pattern Analysis",
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            print(f"❌ FAILED: {str(e)}")
            return error_result
    
    async def test_4_calibrated_scoring_system(self) -> Dict[str, Any]:
        """Test 4: Calibrated Scoring System"""
        print("\n⚖️ TEST 4: Calibrated Scoring System")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Test independent component scoring
            result = await self.calibrated_scoring.get_independent_scores(self.symbol)
            
            processing_time = time.time() - start_time
            
            test_result = {
                "test_name": "Calibrated Scoring System",
                "success": True,
                "processing_time": processing_time,
                "kingfisher_score": result.kingfisher.score if result.kingfisher else None,
                "cryptometer_score": result.cryptometer.score if result.cryptometer else None,
                "riskmetric_score": result.riskmetric.score if result.riskmetric else None,
                "components_available": sum([
                    1 for comp in [result.kingfisher, result.cryptometer, result.riskmetric] 
                    if comp is not None
                ]),
                "details": {
                    "kingfisher_confidence": result.kingfisher.confidence if result.kingfisher else None,
                    "cryptometer_confidence": result.cryptometer.confidence if result.cryptometer else None,
                    "riskmetric_confidence": result.riskmetric.confidence if result.riskmetric else None,
                    "kingfisher_direction": result.kingfisher.direction if result.kingfisher else None,
                    "cryptometer_direction": result.cryptometer.direction if result.cryptometer else None,
                    "riskmetric_direction": result.riskmetric.direction if result.riskmetric else None
                }
            }
            
            print(f"✅ SUCCESS: Calibrated Scoring")
            print(f"   KingFisher: {test_result['kingfisher_score']:.1f}%" if test_result['kingfisher_score'] else "   KingFisher: Not Available")
            print(f"   Cryptometer: {test_result['cryptometer_score']:.1f}%" if test_result['cryptometer_score'] else "   Cryptometer: Not Available")
            print(f"   RiskMetric: {test_result['riskmetric_score']:.1f}%" if test_result['riskmetric_score'] else "   RiskMetric: Not Available")
            print(f"   Components Available: {test_result['components_available']}/3")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            return test_result
            
        except Exception as e:
            error_result = {
                "test_name": "Calibrated Scoring System",
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            print(f"❌ FAILED: {str(e)}")
            return error_result
    
    async def test_5_endpoint_analysis_detailed(self) -> Dict[str, Any]:
        """Test 5: Detailed Endpoint Analysis"""
        print("\n🔍 TEST 5: Detailed Endpoint Analysis")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Test detailed endpoint analysis
            result = await self.endpoint_analyzer.analyze_symbol_complete(self.symbol)
            
            processing_time = time.time() - start_time
            
            successful_endpoints = [score for score in result.endpoint_scores if score.success]
            failed_endpoints = [score for score in result.endpoint_scores if not score.success]
            
            test_result = {
                "test_name": "Detailed Endpoint Analysis",
                "success": True,
                "processing_time": processing_time,
                "total_endpoints": len(result.endpoint_scores),
                "successful_endpoints": len(successful_endpoints),
                "failed_endpoints": len(failed_endpoints),
                "success_rate": (len(successful_endpoints) / len(result.endpoint_scores)) * 100,
                "calibrated_score": result.calibrated_score,
                "confidence": result.confidence,
                "direction": result.direction,
                "analysis_summary": result.analysis_summary,
                "details": {
                    "endpoint_breakdown": [
                        {
                            "endpoint": score.endpoint,
                            "success": score.success,
                            "score": score.score if score.success else None,
                            "confidence": score.confidence if score.success else None,
                            "patterns": len(score.patterns) if score.success else 0,
                            "error": score.error if not score.success else None
                        }
                        for score in result.endpoint_scores
                    ],
                    "top_performing_endpoints": [
                        score.endpoint for score in sorted(successful_endpoints, 
                        key=lambda x: x.score, reverse=True)[:5]
                    ]
                }
            }
            
            print(f"✅ SUCCESS: Endpoint Analysis")
            print(f"   Total Endpoints: {test_result['total_endpoints']}")
            print(f"   Successful: {test_result['successful_endpoints']}")
            print(f"   Success Rate: {test_result['success_rate']:.1f}%")
            print(f"   Calibrated Score: {test_result['calibrated_score']:.1f}%")
            print(f"   Direction: {test_result['direction']}")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            return test_result
            
        except Exception as e:
            error_result = {
                "test_name": "Detailed Endpoint Analysis",
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            print(f"❌ FAILED: {str(e)}")
            return error_result
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        print(f"\n🎯 Starting Comprehensive Cryptometer Test for {self.symbol}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_1_unified_cryptometer_system(),
            self.test_2_multi_model_ai_analysis(),
            self.test_3_historical_pattern_analysis(),
            self.test_4_calibrated_scoring_system(),
            self.test_5_endpoint_analysis_detailed()
        ]
        
        results = []
        for test in tests:
            try:
                result = await test
                results.append(result)
            except Exception as e:
                logger.error(f"Test failed with exception: {e}")
                results.append({
                    "test_name": "Unknown Test",
                    "success": False,
                    "error": str(e)
                })
        
        # Generate summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get("success", False))
        total_processing_time = sum(r.get("processing_time", 0) for r in results)
        
        summary = {
            "test_suite": "Cryptometer SOL/USDT Comprehensive Test",
            "symbol": self.symbol,
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests) * 100,
                "total_processing_time": total_processing_time
            },
            "test_results": results,
            "system_capabilities": {
                "unified_system": any(r.get("test_name") == "Unified Cryptometer System" and r.get("success") for r in results),
                "multi_model_ai": any(r.get("test_name") == "Multi-Model AI Analysis" and r.get("success") for r in results),
                "historical_analysis": any(r.get("test_name") == "Historical Pattern Analysis" and r.get("success") for r in results),
                "calibrated_scoring": any(r.get("test_name") == "Calibrated Scoring System" and r.get("success") for r in results),
                "endpoint_analysis": any(r.get("test_name") == "Detailed Endpoint Analysis" and r.get("success") for r in results)
            }
        }
        
        # Print final summary
        self.print_final_summary(summary)
        
        return summary
    
    def print_final_summary(self, summary: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"Symbol: {summary['symbol']}")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Tests: {summary['summary']['successful_tests']}/{summary['summary']['total_tests']} passed")
        print(f"Success Rate: {summary['summary']['success_rate']:.1f}%")
        print(f"Total Processing Time: {summary['summary']['total_processing_time']:.2f}s")
        
        print("\n📊 SYSTEM CAPABILITIES:")
        capabilities = summary['system_capabilities']
        for capability, status in capabilities.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {capability.replace('_', ' ').title()}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in summary['test_results']:
            status_icon = "✅" if result.get("success") else "❌"
            test_name = result.get("test_name", "Unknown")
            processing_time = result.get("processing_time", 0)
            print(f"   {status_icon} {test_name} ({processing_time:.2f}s)")
            
            if not result.get("success"):
                error = result.get("error", "Unknown error")
                print(f"      Error: {error}")
        
        if summary['summary']['success_rate'] >= 80:
            print("\n🎉 EXCELLENT: System performing above expectations!")
        elif summary['summary']['success_rate'] >= 60:
            print("\n✅ GOOD: System performing well with minor issues")
        else:
            print("\n⚠️ NEEDS ATTENTION: System has significant issues")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    test_suite = CryptometerSOLTest()
    
    try:
        results = await test_suite.run_comprehensive_test()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cryptometer_sol_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: {filename}")
        
        return results
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n❌ Test suite failed: {e}")
        return None

if __name__ == "__main__":
    # Run the comprehensive test
    results = asyncio.run(main())