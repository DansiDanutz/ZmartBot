#!/usr/bin/env python3
"""
AI Agent Integration Test - ZmartBot
Comprehensive test for AI-powered win rate prediction across all three agents

Tests:
- KingFisher: AI analysis of liquidation clusters
- Cryptometer: AI analysis of 17 endpoints  
- RiskMetric: AI analysis of Cowen methodology
- Multi-timeframe predictions (24h, 7d, 1m)
- Win rate correlation system
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import services
from src.services.kingfisher_service import KingFisherService
from src.services.cryptometer_service import get_cryptometer_service
from src.services.riskmetric_service import riskmetric_service

# Import AI predictor
from src.agents.scoring.ai_win_rate_predictor import ai_predictor, AIModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAgentIntegrationTest:
    """Comprehensive test for AI agent integration"""
    
    def __init__(self):
        self.kingfisher_service = KingFisherService()
        self.cryptometer_service = None
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        self.results = {}
        
    async def setup(self):
        """Setup all services"""
        logger.info("🚀 Setting up AI Agent Integration Test...")
        
        # Initialize Cryptometer service
        self.cryptometer_service = await get_cryptometer_service()
        
        # Start RiskMetric service
        await riskmetric_service.start()
        
        logger.info("✅ All services initialized")
    
    async def test_kingfisher_ai_integration(self, symbol: str) -> Dict[str, Any]:
        """Test KingFisher AI win rate prediction"""
        logger.info(f"🔍 Testing KingFisher AI integration for {symbol}")
        
        try:
            # Test basic win rate prediction
            win_rate_result = await self.kingfisher_service.get_kingfisher_score(symbol)
            
            # Test multi-timeframe prediction
            multi_timeframe_result = await self.kingfisher_service.get_multi_timeframe_win_rate(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'kingfisher',
                'basic_win_rate': win_rate_result,
                'multi_timeframe': multi_timeframe_result,
                'status': 'success'
            }
            
            logger.info(f"✅ KingFisher AI test completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ KingFisher AI test failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'kingfisher',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_cryptometer_ai_integration(self, symbol: str) -> Dict[str, Any]:
        """Test Cryptometer AI win rate prediction"""
        logger.info(f"🔍 Testing Cryptometer AI integration for {symbol}")
        
        try:
            # Ensure cryptometer service is initialized
            if not self.cryptometer_service:
                self.cryptometer_service = await get_cryptometer_service()
            
            # Test basic win rate prediction
            win_rate_result = await self.cryptometer_service.get_cryptometer_win_rate(symbol)
            
            # Test multi-timeframe prediction
            multi_timeframe_result = await self.cryptometer_service.get_multi_timeframe_win_rate(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'cryptometer',
                'basic_win_rate': win_rate_result,
                'multi_timeframe': multi_timeframe_result,
                'status': 'success'
            }
            
            logger.info(f"✅ Cryptometer AI test completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Cryptometer AI test failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'cryptometer',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_riskmetric_ai_integration(self, symbol: str) -> Dict[str, Any]:
        """Test RiskMetric AI win rate prediction"""
        logger.info(f"🔍 Testing RiskMetric AI integration for {symbol}")
        
        try:
            # Test basic win rate prediction
            win_rate_result = await riskmetric_service.get_riskmetric_win_rate(symbol)
            
            # Test multi-timeframe prediction
            multi_timeframe_result = await riskmetric_service.get_multi_timeframe_win_rate(symbol)
            
            result = {
                'symbol': symbol,
                'agent': 'riskmetric',
                'basic_win_rate': win_rate_result,
                'multi_timeframe': multi_timeframe_result,
                'status': 'success'
            }
            
            logger.info(f"✅ RiskMetric AI test completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ RiskMetric AI test failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'agent': 'riskmetric',
                'status': 'error',
                'error': str(e)
            }
    
    async def test_ai_predictor_direct(self, symbol: str) -> Dict[str, Any]:
        """Test AI predictor directly"""
        logger.info(f"🔍 Testing AI predictor directly for {symbol}")
        
        try:
            # Test KingFisher prediction
            kingfisher_data = {
                'liquidation_analysis': {
                    'cluster_strength': 0.8,
                    'position': 'below',
                    'toxic_order_flow': True
                }
            }
            kingfisher_prediction = await ai_predictor.predict_kingfisher_win_rate(
                symbol, kingfisher_data, AIModel.OPENAI_GPT4
            )
            
            # Test Cryptometer prediction
            cryptometer_data = {
                'ai_screener': {'score': 75},
                'volume_spike': {'detected': True},
                'trend_analysis': {'direction': 'bullish'}
            }
            cryptometer_prediction = await ai_predictor.predict_cryptometer_win_rate(
                symbol, cryptometer_data, AIModel.OPENAI_GPT4
            )
            
            # Test RiskMetric prediction
            riskmetric_data = {
                'risk_value': 0.3,
                'time_in_risk': 0.1,
                'coefficient': 1.2
            }
            riskmetric_prediction = await ai_predictor.predict_riskmetric_win_rate(
                symbol, riskmetric_data, AIModel.ANTHROPIC_CLAUDE
            )
            
            result = {
                'symbol': symbol,
                'direct_ai_tests': {
                    'kingfisher': {
                        'win_rate': kingfisher_prediction.win_rate_prediction,
                        'confidence': kingfisher_prediction.confidence,
                        'direction': kingfisher_prediction.direction
                    },
                    'cryptometer': {
                        'win_rate': cryptometer_prediction.win_rate_prediction,
                        'confidence': cryptometer_prediction.confidence,
                        'direction': cryptometer_prediction.direction
                    },
                    'riskmetric': {
                        'win_rate': riskmetric_prediction.win_rate_prediction,
                        'confidence': riskmetric_prediction.confidence,
                        'direction': riskmetric_prediction.direction
                    }
                },
                'status': 'success'
            }
            
            logger.info(f"✅ Direct AI predictor test completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Direct AI predictor test failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
    
    async def run_comprehensive_test(self):
        """Run comprehensive AI agent integration test"""
        logger.info("🎯 Starting Comprehensive AI Agent Integration Test")
        
        await self.setup()
        
        all_results = {}
        
        for symbol in self.test_symbols:
            logger.info(f"\n📊 Testing {symbol} across all agents...")
            
            symbol_results = {}
            
            # Test each agent
            kingfisher_result = await self.test_kingfisher_ai_integration(symbol)
            cryptometer_result = await self.test_cryptometer_ai_integration(symbol)
            riskmetric_result = await self.test_riskmetric_ai_integration(symbol)
            direct_ai_result = await self.test_ai_predictor_direct(symbol)
            
            symbol_results = {
                'kingfisher': kingfisher_result,
                'cryptometer': cryptometer_result,
                'riskmetric': riskmetric_result,
                'direct_ai': direct_ai_result,
                'timestamp': datetime.now().isoformat()
            }
            
            all_results[symbol] = symbol_results
        
        # Generate summary
        await self.generate_test_summary(all_results)
        
        # Cleanup
        await self.cleanup()
        
        return all_results
    
    async def generate_test_summary(self, results: Dict[str, Any]):
        """Generate comprehensive test summary"""
        logger.info("\n📋 AI Agent Integration Test Summary")
        logger.info("=" * 60)
        
        total_symbols = len(results)
        successful_tests = 0
        failed_tests = 0
        
        for symbol, symbol_results in results.items():
            logger.info(f"\n🎯 {symbol} Results:")
            
            for agent, result in symbol_results.items():
                if agent == 'timestamp':
                    continue
                    
                status = result.get('status', 'unknown')
                if status == 'success':
                    successful_tests += 1
                    logger.info(f"  ✅ {agent.upper()}: SUCCESS")
                    
                    # Show win rate if available
                    if 'basic_win_rate' in result and 'win_rate_prediction' in result['basic_win_rate']:
                        win_rate = result['basic_win_rate']['win_rate_prediction']
                        logger.info(f"     Win Rate: {win_rate:.1f}%")
                else:
                    failed_tests += 1
                    logger.info(f"  ❌ {agent.upper()}: FAILED")
                    logger.info(f"     Error: {result.get('error', 'Unknown error')}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Total Symbols: {total_symbols}")
        logger.info(f"   Successful Tests: {successful_tests}")
        logger.info(f"   Failed Tests: {failed_tests}")
        logger.info(f"   Success Rate: {(successful_tests / (successful_tests + failed_tests) * 100):.1f}%")
        
        if successful_tests > 0:
            logger.info("🎉 AI Agent Integration Test PASSED!")
        else:
            logger.error("💥 AI Agent Integration Test FAILED!")
    
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
    logger.info("🚀 Starting AI Agent Integration Test")
    
    test = AIAgentIntegrationTest()
    results = await test.run_comprehensive_test()
    
    logger.info("🏁 AI Agent Integration Test completed!")
    return results

if __name__ == "__main__":
    asyncio.run(main()) 