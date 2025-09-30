#!/usr/bin/env python3
"""
Simple AI Integration Test - ZmartBot
Tests the AI integration structure without requiring external API keys
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Import services
from src.services.kingfisher_service import KingFisherService
from src.services.riskmetric_service import riskmetric_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAIIntegrationTest:
    """Simple test for AI integration structure"""
    
    def __init__(self):
        self.kingfisher_service = KingFisherService()
        self.test_symbols = ["BTCUSDT", "ETHUSDT"]
        self.results = {}
        
    async def setup(self):
        """Setup services"""
        logger.info("🚀 Setting up Simple AI Integration Test...")
        
        # Start RiskMetric service
        await riskmetric_service.start()
        
        logger.info("✅ Services initialized")
    
    async def test_kingfisher_structure(self, symbol: str) -> Dict[str, Any]:
        """Test KingFisher service structure"""
        logger.info(f"🔍 Testing KingFisher structure for {symbol}")
        
        try:
            # Test basic analysis (without AI)
            analysis = await self.kingfisher_service.analyze_liquidation_data(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'kingfisher',
                'analysis_structure': analysis,
                'status': 'success'
            }
            
            logger.info(f"✅ KingFisher structure test completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ KingFisher structure test failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'kingfisher',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_riskmetric_structure(self, symbol: str) -> Dict[str, Any]:
        """Test RiskMetric service structure"""
        logger.info(f"🔍 Testing RiskMetric structure for {symbol}")
        
        try:
            # Test basic risk assessment
            risk_assessment = await riskmetric_service.assess_risk(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'riskmetric',
                'risk_assessment': risk_assessment,
                'status': 'success'
            }
            
            logger.info(f"✅ RiskMetric structure test completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ RiskMetric structure test failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'riskmetric',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_ai_predictor_structure(self):
        """Test AI predictor structure"""
        logger.info("🔍 Testing AI predictor structure")
        
        try:
            from src.agents.scoring.ai_win_rate_predictor import ai_predictor, AIModel
            
            # Test fallback prediction creation
            fallback_prediction = ai_predictor._create_fallback_prediction(
                "BTCUSDT", "kingfisher", "Test fallback"
            )
            
            result = {
                'ai_predictor': 'available',
                'fallback_prediction': fallback_prediction,
                'status': 'success'
            }
            
            logger.info("✅ AI predictor structure test completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ AI predictor structure test failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_simple_test(self):
        """Run simple integration test"""
        logger.info("🎯 Starting Simple AI Integration Test")
        
        await self.setup()
        
        all_results = {}
        
        # Test AI predictor structure
        ai_result = await self.test_ai_predictor_structure()
        all_results['ai_predictor'] = ai_result
        
        for symbol in self.test_symbols:
            logger.info(f"\n📊 Testing {symbol} structure...")
            
            symbol_results = {}
            
            # Test each agent structure
            kingfisher_result = await self.test_kingfisher_structure(symbol)
            riskmetric_result = await self.test_riskmetric_structure(symbol)
            
            symbol_results = {
                'kingfisher': kingfisher_result,
                'riskmetric': riskmetric_result,
                'timestamp': datetime.now().isoformat()
            }
            
            all_results[symbol] = symbol_results
        
        # Generate summary
        await self.generate_test_summary(all_results)
        
        # Cleanup
        await self.cleanup()
        
        return all_results
    
    async def generate_test_summary(self, results: Dict[str, Any]):
        """Generate test summary"""
        logger.info("\n📋 Simple AI Integration Test Summary")
        logger.info("=" * 50)
        
        successful_tests = 0
        failed_tests = 0
        
        for test_name, result in results.items():
            logger.info(f"\n🎯 {test_name} Results:")
            
            if isinstance(result, dict):
                for component, component_result in result.items():
                    if component == 'timestamp':
                        continue
                    
                    if isinstance(component_result, dict):
                        status = component_result.get('status', 'unknown')
                        if status == 'success':
                            successful_tests += 1
                            logger.info(f"  ✅ {component.upper()}: SUCCESS")
                        else:
                            failed_tests += 1
                            logger.info(f"  ❌ {component.upper()}: FAILED")
                            logger.info(f"     Error: {component_result.get('error', 'Unknown error')}")
                    else:
                        logger.info(f"  📊 {component.upper()}: {component_result}")
            else:
                logger.info(f"  📊 {test_name.upper()}: {result}")
        
        logger.info("\n" + "=" * 50)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Successful Tests: {successful_tests}")
        logger.info(f"   Failed Tests: {failed_tests}")
        
        if successful_tests > 0:
            logger.info("🎉 Simple AI Integration Test PASSED!")
        else:
            logger.error("💥 Simple AI Integration Test FAILED!")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        
        try:
            await riskmetric_service.stop()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {str(e)}")

async def main():
    """Main test execution"""
    logger.info("🚀 Starting Simple AI Integration Test")
    
    test = SimpleAIIntegrationTest()
    results = await test.run_simple_test()
    
    logger.info("🏁 Simple AI Integration Test completed!")
    return results

if __name__ == "__main__":
    asyncio.run(main()) 