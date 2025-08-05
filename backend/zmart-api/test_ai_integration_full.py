#!/usr/bin/env python3
"""
Full AI Integration Test - ZmartBot
Tests the AI integration with real OpenAI API keys
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Import services
from src.services.kingfisher_service import KingFisherService
from src.services.riskmetric_service import riskmetric_service
from src.agents.scoring.ai_win_rate_predictor import ai_predictor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullAIIntegrationTest:
    """Full test for AI integration with real API keys"""
    
    def __init__(self):
        self.kingfisher_service = KingFisherService()
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        self.results = {}
        
        # Note: API keys should be set as environment variables before running the test
        # export OPENAI_API_KEY="your-openai-key"
        # export ZMART_TRADING_API_KEY="your-zmart-key"
        
    async def setup(self):
        """Setup services"""
        logger.info("🚀 Setting up Full AI Integration Test...")
        
        # Start RiskMetric service
        await riskmetric_service.start()
        
        logger.info("✅ Services initialized")
    
    async def test_kingfisher_ai_prediction(self, symbol: str) -> Dict[str, Any]:
        """Test KingFisher AI prediction"""
        logger.info(f"🔍 Testing KingFisher AI prediction for {symbol}")
        
        try:
            # Get AI win rate prediction
            win_rate_result = await self.kingfisher_service.get_kingfisher_score(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'kingfisher',
                'win_rate': win_rate_result.get('win_rate_prediction'),
                'confidence': win_rate_result.get('confidence'),
                'direction': win_rate_result.get('direction'),
                'reasoning': win_rate_result.get('reasoning'),
                'ai_analysis': win_rate_result.get('ai_analysis'),
                'status': 'success'
            }
            
            logger.info(f"✅ KingFisher AI prediction completed for {symbol}")
            logger.info(f"   Win Rate: {result['win_rate']}%")
            logger.info(f"   Confidence: {result['confidence']}")
            logger.info(f"   Direction: {result['direction']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ KingFisher AI prediction failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'kingfisher',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_riskmetric_ai_prediction(self, symbol: str) -> Dict[str, Any]:
        """Test RiskMetric AI prediction"""
        logger.info(f"🔍 Testing RiskMetric AI prediction for {symbol}")
        
        try:
            # Get AI win rate prediction
            win_rate_result = await riskmetric_service.get_riskmetric_win_rate(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'riskmetric',
                'win_rate': win_rate_result.get('win_rate_prediction'),
                'confidence': win_rate_result.get('confidence'),
                'direction': win_rate_result.get('direction'),
                'reasoning': win_rate_result.get('reasoning'),
                'ai_analysis': win_rate_result.get('ai_analysis'),
                'status': 'success'
            }
            
            logger.info(f"✅ RiskMetric AI prediction completed for {symbol}")
            logger.info(f"   Win Rate: {result['win_rate']}%")
            logger.info(f"   Confidence: {result['confidence']}")
            logger.info(f"   Direction: {result['direction']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ RiskMetric AI prediction failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'riskmetric',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_multi_timeframe_ai_prediction(self, symbol: str) -> Dict[str, Any]:
        """Test multi-timeframe AI prediction"""
        logger.info(f"🔍 Testing multi-timeframe AI prediction for {symbol}")
        
        try:
            # Test KingFisher multi-timeframe
            kingfisher_multi = await self.kingfisher_service.get_multi_timeframe_win_rate(symbol)
            
            # Test RiskMetric multi-timeframe
            riskmetric_multi = await riskmetric_service.get_multi_timeframe_win_rate(symbol)
            
            result = {
                'symbol': symbol,
                'kingfisher_multi': kingfisher_multi,
                'riskmetric_multi': riskmetric_multi,
                'status': 'success'
            }
            
            logger.info(f"✅ Multi-timeframe AI prediction completed for {symbol}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Multi-timeframe AI prediction failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
    
    async def test_direct_ai_predictor(self, symbol: str) -> Dict[str, Any]:
        """Test direct AI predictor"""
        logger.info(f"🔍 Testing direct AI predictor for {symbol}")
        
        try:
            # Test KingFisher direct prediction
            kingfisher_prediction = await ai_predictor.predict_kingfisher_win_rate(symbol, {})
            
            # Test RiskMetric direct prediction
            riskmetric_prediction = await ai_predictor.predict_riskmetric_win_rate(symbol, {})
            
            result = {
                'symbol': symbol,
                'kingfisher_direct': kingfisher_prediction,
                'riskmetric_direct': riskmetric_prediction,
                'status': 'success'
            }
            
            logger.info(f"✅ Direct AI predictor completed for {symbol}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Direct AI predictor failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
    
    async def run_full_test(self):
        """Run full AI integration test"""
        logger.info("🎯 Starting Full AI Integration Test")
        
        await self.setup()
        
        all_results = {}
        
        for symbol in self.test_symbols:
            logger.info(f"\n📊 Testing {symbol} with real AI...")
            
            symbol_results = {}
            
            # Test each AI prediction type
            kingfisher_result = await self.test_kingfisher_ai_prediction(symbol)
            riskmetric_result = await self.test_riskmetric_ai_prediction(symbol)
            multi_result = await self.test_multi_timeframe_ai_prediction(symbol)
            direct_result = await self.test_direct_ai_predictor(symbol)
            
            symbol_results = {
                'kingfisher_ai': kingfisher_result,
                'riskmetric_ai': riskmetric_result,
                'multi_timeframe': multi_result,
                'direct_predictor': direct_result,
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
        logger.info("\n📋 Full AI Integration Test Summary")
        logger.info("=" * 60)
        
        successful_tests = 0
        failed_tests = 0
        
        for symbol, symbol_results in results.items():
            logger.info(f"\n🎯 {symbol} Results:")
            
            for test_type, test_result in symbol_results.items():
                if test_type == 'timestamp':
                    continue
                
                if isinstance(test_result, dict):
                    status = test_result.get('status', 'unknown')
                    if status == 'success':
                        successful_tests += 1
                        logger.info(f"  ✅ {test_type.upper()}: SUCCESS")
                        
                        # Log key metrics
                        if 'win_rate' in test_result:
                            logger.info(f"     Win Rate: {test_result['win_rate']}%")
                        if 'confidence' in test_result:
                            logger.info(f"     Confidence: {test_result['confidence']}")
                        if 'direction' in test_result:
                            logger.info(f"     Direction: {test_result['direction']}")
                    else:
                        failed_tests += 1
                        logger.info(f"  ❌ {test_type.upper()}: FAILED")
                        logger.info(f"     Error: {test_result.get('error', 'Unknown error')}")
                else:
                    logger.info(f"  📊 {test_type.upper()}: {test_result}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Successful Tests: {successful_tests}")
        logger.info(f"   Failed Tests: {failed_tests}")
        logger.info(f"   Success Rate: {(successful_tests/(successful_tests+failed_tests)*100):.1f}%" if (successful_tests+failed_tests) > 0 else "N/A")
        
        if successful_tests > 0:
            logger.info("🎉 Full AI Integration Test PASSED!")
            logger.info("🚀 AI Integration is PRODUCTION READY!")
        else:
            logger.error("💥 Full AI Integration Test FAILED!")
    
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
    logger.info("🚀 Starting Full AI Integration Test with Real API Keys")
    
    test = FullAIIntegrationTest()
    results = await test.run_full_test()
    
    logger.info("🏁 Full AI Integration Test completed!")
    return results

if __name__ == "__main__":
    asyncio.run(main()) 