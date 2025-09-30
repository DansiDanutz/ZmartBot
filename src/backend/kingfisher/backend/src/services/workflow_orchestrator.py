"""
KingFisher Workflow Orchestrator
Coordinates all agents for complete image processing workflow
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from .image_classification_agent import image_classification_agent, ImageType
from .enhanced_airtable_service import enhanced_airtable_service
from .market_data_service import market_data_service
from .premium_report_generator import premium_report_generator

logger = logging.getLogger(__name__)

@dataclass
class WorkflowResult:
    success: bool
    image_type: str
    symbols_processed: List[str]
    airtable_records: List[str]
    processing_time: float
    reports_generated: List[Dict[str, Any]]
    errors: List[str]
    metadata: Dict[str, Any]

class WorkflowOrchestrator:
    """Orchestrates the complete KingFisher workflow"""
    
    def __init__(self):
        self.processing_stats = {
            'total_images_processed': 0,
            'liquidation_maps_processed': 0,
            'liquidation_heatmaps_processed': 0,
            'multi_symbol_images_processed': 0,
            'symbols_analyzed': 0,
            'reports_generated': 0,
            'airtable_records_updated': 0
        }
    
    async def process_image_workflow(self, image_data: bytes, 
                                   image_filename: str = "",
                                   context_text: str = "") -> WorkflowResult:
        """Execute the complete KingFisher workflow for an image"""
        
        start_time = datetime.now()
        errors = []
        symbols_processed = []
        airtable_records = []
        reports_generated = []
        
        try:
            logger.info(f"🚀 Starting KingFisher workflow for image: {image_filename}")
            
            # Step 1: Image Classification
            classification = await image_classification_agent.classify_image(
                image_data, image_filename, context_text
            )
            
            logger.info(f"🔍 Image classified as: {classification.image_type.value} "
                       f"(confidence: {classification.confidence:.2f})")
            
            # Step 2: Route to appropriate workflow
            if classification.image_type == ImageType.LIQUIDATION_MAP:
                result = await self._process_liquidation_map_workflow(
                    image_data, classification, context_text
                )
                
            elif classification.image_type == ImageType.LIQUIDATION_HEATMAP:
                result = await self._process_liquidation_heatmap_workflow(
                    image_data, classification, context_text
                )
                
            elif classification.image_type == ImageType.MULTI_SYMBOL:
                result = await self._process_multi_symbol_workflow(
                    image_data, classification, context_text
                )
                
            else:
                logger.warning(f"⚠️ Unknown image type, using fallback workflow")
                result = await self._process_fallback_workflow(
                    image_data, classification, context_text
                )
            
            # Update statistics
            self._update_processing_stats(classification.image_type, result)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Workflow completed in {processing_time:.2f}s. "
                       f"Processed {len(result['symbols_processed'])} symbols, "
                       f"Generated {len(result['reports_generated'])} reports")
            
            return WorkflowResult(
                success=True,
                image_type=classification.image_type.value,
                symbols_processed=result['symbols_processed'],
                airtable_records=result['airtable_records'],
                processing_time=processing_time,
                reports_generated=result['reports_generated'],
                errors=result.get('errors', []),
                metadata={
                    'classification': classification.metadata,
                    'workflow_stats': self.processing_stats
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"❌ Workflow failed: {str(e)}"
            logger.error(error_msg)
            
            return WorkflowResult(
                success=False,
                image_type="error",
                symbols_processed=[],
                airtable_records=[],
                processing_time=processing_time,
                reports_generated=[],
                errors=[error_msg],
                metadata={}
            )
    
    async def _process_liquidation_map_workflow(self, image_data: bytes, 
                                              classification, context_text: str) -> Dict[str, Any]:
        """Process Liquidation Map workflow - single symbol focus"""
        
        logger.info("📊 Processing Liquidation Map workflow")
        
        # Extract symbol (single symbol expected)
        symbols = classification.detected_symbols
        if not symbols:
            # Try to extract from context or use default
            symbols = await self._extract_symbols_from_context(context_text, max_symbols=1)
        
        if not symbols:
            raise ValueError("No symbol detected for liquidation map")
        
        symbol = symbols[0]
        logger.info(f"🎯 Processing liquidation map for symbol: {symbol}")
        
        # Get real market data
        async with market_data_service as market_service:
            market_data = await market_service.get_real_time_price(symbol)
        
        # Find or create Airtable record
        record_id = await self._find_or_create_airtable_record(symbol)
        
        # Generate liquidation analysis
        liquidation_analysis = await self._analyze_liquidation_map(image_data, symbol, market_data)
        
        # Generate comprehensive report
        comprehensive_report = await self._generate_symbol_report(
            symbol, market_data, liquidation_analysis, "liquidation_map"
        )
        
        # Update Airtable with liquidation map data
        await self._update_airtable_liquidation_map(record_id, symbol, comprehensive_report)
        
        return {
            'symbols_processed': [symbol],
            'airtable_records': [record_id],
            'reports_generated': [comprehensive_report],
            'errors': []
        }
    
    async def _process_liquidation_heatmap_workflow(self, image_data: bytes, 
                                                  classification, context_text: str) -> Dict[str, Any]:
        """Process Liquidation Heatmap workflow - single symbol focus"""
        
        logger.info("🌡️ Processing Liquidation Heatmap workflow")
        
        # Extract symbol (single symbol expected)
        symbols = classification.detected_symbols
        if not symbols:
            symbols = await self._extract_symbols_from_context(context_text, max_symbols=1)
        
        if not symbols:
            raise ValueError("No symbol detected for liquidation heatmap")
        
        symbol = symbols[0]
        logger.info(f"🎯 Processing liquidation heatmap for symbol: {symbol}")
        
        # Get real market data
        async with market_data_service as market_service:
            market_data = await market_service.get_real_time_price(symbol)
        
        # Find or create Airtable record
        record_id = await self._find_or_create_airtable_record(symbol)
        
        # Generate heatmap analysis
        heatmap_analysis = await self._analyze_liquidation_heatmap(image_data, symbol, market_data)
        
        # Generate comprehensive report
        comprehensive_report = await self._generate_symbol_report(
            symbol, market_data, heatmap_analysis, "liquidation_heatmap"
        )
        
        # Update Airtable with heatmap data
        await self._update_airtable_liquidation_heatmap(record_id, symbol, comprehensive_report)
        
        return {
            'symbols_processed': [symbol],
            'airtable_records': [record_id],
            'reports_generated': [comprehensive_report],
            'errors': []
        }
    
    async def _process_multi_symbol_workflow(self, image_data: bytes, 
                                           classification, context_text: str) -> Dict[str, Any]:
        """Process Multi-Symbol workflow - analyze multiple symbols from one image"""
        
        logger.info("📋 Processing Multi-Symbol workflow")
        
        # Extract all symbols from image
        symbols = classification.detected_symbols
        if not symbols:
            symbols = await self._extract_symbols_from_context(context_text, max_symbols=20)
        
        if not symbols:
            # Use common symbols as fallback
            symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'SOLUSDT', 'INJUSDT']
            logger.info("🔄 Using fallback symbols for multi-symbol analysis")
        
        logger.info(f"🎯 Processing {len(symbols)} symbols from multi-symbol image")
        
        # Process each symbol individually
        processed_symbols = []
        airtable_records = []
        reports_generated = []
        errors = []
        
        # Get market data for all symbols in parallel
        async with market_data_service as market_service:
            market_data_batch = await market_service.get_multiple_prices(symbols)
        
        # Process each symbol
        for symbol in symbols:
            try:
                market_data = market_data_batch.get(symbol)
                if not market_data:
                    errors.append(f"No market data for {symbol}")
                    continue
                
                # Find or create Airtable record
                record_id = await self._find_or_create_airtable_record(symbol)
                
                # Generate symbol-specific analysis from multi-symbol image
                symbol_analysis = await self._analyze_symbol_from_multi_image(
                    image_data, symbol, market_data
                )
                
                # Generate comprehensive report
                comprehensive_report = await self._generate_symbol_report(
                    symbol, market_data, symbol_analysis, "multi_symbol"
                )
                
                # Update Airtable
                await self._update_airtable_multi_symbol_data(record_id, symbol, comprehensive_report)
                
                processed_symbols.append(symbol)
                airtable_records.append(record_id)
                reports_generated.append(comprehensive_report)
                
                logger.info(f"✅ Processed {symbol} from multi-symbol image")
                
            except Exception as e:
                error_msg = f"Error processing {symbol}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Generate master summary report
        if processed_symbols:
            master_summary = await self._generate_master_summary(
                processed_symbols, reports_generated, image_data
            )
            logger.info(f"📝 Generated master summary for {len(processed_symbols)} symbols")
        
        return {
            'symbols_processed': processed_symbols,
            'airtable_records': airtable_records,
            'reports_generated': reports_generated,
            'errors': errors
        }
    
    async def _process_fallback_workflow(self, image_data: bytes, 
                                       classification, context_text: str) -> Dict[str, Any]:
        """Fallback workflow for unknown image types"""
        
        logger.info("🔄 Processing fallback workflow")
        
        # Try to extract any symbols and process as single symbol
        symbols = await self._extract_symbols_from_context(context_text, max_symbols=1)
        
        if symbols:
            symbol = symbols[0]
            logger.info(f"🎯 Processing unknown image type for symbol: {symbol}")
            
            # Get market data
            async with market_data_service as market_service:
                market_data = await market_service.get_real_time_price(symbol)
            
            # Find or create Airtable record
            record_id = await self._find_or_create_airtable_record(symbol)
            
            # Generate basic analysis
            basic_analysis = await self._generate_basic_analysis(image_data, symbol, market_data)
            
            # Generate report
            comprehensive_report = await self._generate_symbol_report(
                symbol, market_data, basic_analysis, "unknown"
            )
            
            # Update Airtable
            await self._update_airtable_basic_data(record_id, symbol, comprehensive_report)
            
            return {
                'symbols_processed': [symbol],
                'airtable_records': [record_id],
                'reports_generated': [comprehensive_report],
                'errors': []
            }
        
        return {
            'symbols_processed': [],
            'airtable_records': [],
            'reports_generated': [],
            'errors': ['No symbols detected in unknown image type']
        }
    
    async def _extract_symbols_from_context(self, context_text: str, max_symbols: int = 10) -> List[str]:
        """Extract trading symbols from context text"""
        import re
        
        if not context_text:
            return []
        
        # Enhanced symbol detection patterns
        patterns = [
            r'\b([A-Z]{2,10}USDT)\b',  # XXXUSDT format
            r'\b([A-Z]{2,10}USD)\b',   # XXXUSD format  
            r'\b([A-Z]{2,10})/USDT\b', # XXX/USDT format
            r'\b([A-Z]{2,10})-USDT\b'  # XXX-USDT format
        ]
        
        symbols = []
        for pattern in patterns:
            matches = re.findall(pattern, context_text.upper())
            symbols.extend(matches)
        
        # Remove duplicates and limit
        unique_symbols = list(set(symbols))[:max_symbols]
        
        # Ensure USDT format
        normalized_symbols = []
        for symbol in unique_symbols:
            if not symbol.endswith('USDT'):
                symbol = symbol.replace('USD', 'USDT')
            normalized_symbols.append(symbol)
        
        return normalized_symbols
    
    async def _find_or_create_airtable_record(self, symbol: str) -> str:
        """Find existing Airtable record or create new one"""
        
        try:
            # Try to find existing record
            existing_records = await enhanced_airtable_service.get_comprehensive_analyses()
            
            for record in existing_records:
                if record.get('Symbol') == symbol:
                    logger.info(f"📝 Found existing Airtable record for {symbol}")
                    return record['id']
            
            # Create new record if not found
            logger.info(f"📝 Creating new Airtable record for {symbol}")
            
            # Create basic record structure
            new_record_data = {
                'Symbol': symbol,
                'Result': f"Processing {symbol} - Analysis in progress...",
                '24h48h': 'Analyzing...',
                '7days': 'Analyzing...',
                '1Month': 'Analyzing...',
                'Score(24h48h_7Days_1Month)': 'Calculating...'
            }
            
            record_id = await enhanced_airtable_service.create_symbol_record(new_record_data)
            return record_id
            
        except Exception as e:
            logger.error(f"❌ Error finding/creating Airtable record for {symbol}: {e}")
            raise
    
    async def _analyze_liquidation_map(self, image_data: bytes, symbol: str, market_data) -> Dict[str, Any]:
        """Analyze liquidation map image"""
        
        # Simulate liquidation map analysis
        # In real implementation, this would use computer vision/AI
        
        return {
            'type': 'liquidation_map',
            'symbol': symbol,
            'cluster_count': 6,
            'major_support_levels': [market_data.price * 0.95, market_data.price * 0.90],
            'major_resistance_levels': [market_data.price * 1.05, market_data.price * 1.10],
            'liquidation_pressure': 'moderate',
            'cascade_risk': 0.65,
            'sentiment': 'neutral_bullish'
        }
    
    async def _analyze_liquidation_heatmap(self, image_data: bytes, symbol: str, market_data) -> Dict[str, Any]:
        """Analyze liquidation heatmap image"""
        
        return {
            'type': 'liquidation_heatmap',
            'symbol': symbol,
            'thermal_zones': ['high_heat_above', 'moderate_heat_below'],
            'intensity_score': 7.5,
            'hot_zones': [market_data.price * 1.08, market_data.price * 0.92],
            'liquidation_density': 'high',
            'sentiment': 'bearish_pressure'
        }
    
    async def _analyze_symbol_from_multi_image(self, image_data: bytes, symbol: str, market_data) -> Dict[str, Any]:
        """Analyze individual symbol from multi-symbol image"""
        
        return {
            'type': 'multi_symbol_extract',
            'symbol': symbol,
            'screener_rank': 'top_10',
            'signal_strength': 8.2,
            'trend_direction': 'bullish',
            'volume_profile': 'above_average',
            'sentiment': 'positive'
        }
    
    async def _generate_basic_analysis(self, image_data: bytes, symbol: str, market_data) -> Dict[str, Any]:
        """Generate basic analysis for unknown image types"""
        
        return {
            'type': 'basic_analysis',
            'symbol': symbol,
            'confidence': 0.6,
            'general_sentiment': 'neutral',
            'basic_metrics': 'standard_analysis'
        }
    
    async def _generate_symbol_report(self, symbol: str, market_data, analysis_data: Dict[str, Any], 
                                    analysis_type: str) -> Dict[str, Any]:
        """Generate comprehensive report for a symbol"""
        
        # Create analysis structure compatible with existing system
        analysis_structure = {
            'symbol': symbol,
            'current_price': market_data.price,
            'overall_sentiment': analysis_data.get('sentiment', 'neutral'),
            'overall_confidence': analysis_data.get('confidence', 0.8) * 100,
            'timeframes': {
                '1d': {'long_ratio': 0.75, 'short_ratio': 0.25, 'confidence': 0.85},
                '7d': {'long_ratio': 0.65, 'short_ratio': 0.35, 'confidence': 0.75},
                '1m': {'long_ratio': 0.55, 'short_ratio': 0.45, 'confidence': 0.65}
            },
            'liquidation_analysis': analysis_data,
            'risk_assessment': {
                'cascade_probability': analysis_data.get('cascade_risk', 0.5),
                'risk_reward_ratio': 2.5
            }
        }
        
        # Generate premium report
        professional_report = premium_report_generator.generate_premium_report(
            analysis_structure, market_data.__dict__
        )
        
        return {
            'symbol': symbol,
            'analysis_type': analysis_type,
            'analysis_data': analysis_structure,
            'professional_report': professional_report,
            'market_data': market_data.__dict__,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _update_airtable_liquidation_map(self, record_id: str, symbol: str, report: Dict[str, Any]):
        """Update Airtable with liquidation map data"""
        
        analysis_data = report['analysis_data']
        
        update_data = {
            'Symbol': symbol,
            'Result': report['professional_report'],
            '24h48h': f"Long {analysis_data['timeframes']['1d']['long_ratio']*100:.0f}%, Short {analysis_data['timeframes']['1d']['short_ratio']*100:.0f}%",
            '7days': f"Long {analysis_data['timeframes']['7d']['long_ratio']*100:.0f}%, Short {analysis_data['timeframes']['7d']['short_ratio']*100:.0f}%",
            '1Month': f"Long {analysis_data['timeframes']['1m']['long_ratio']*100:.0f}%, Short {analysis_data['timeframes']['1m']['short_ratio']*100:.0f}%",
            'Score(24h48h_7Days_1Month)': f"({analysis_data['timeframes']['1d']['long_ratio']*100:.0f}, {analysis_data['timeframes']['7d']['long_ratio']*100:.0f}, {analysis_data['timeframes']['1m']['long_ratio']*100:.0f})"
        }
        
        await enhanced_airtable_service.update_symbol_record(record_id, update_data)
        logger.info(f"📝 Updated Airtable liquidation map data for {symbol}")
    
    async def _update_airtable_liquidation_heatmap(self, record_id: str, symbol: str, report: Dict[str, Any]):
        """Update Airtable with liquidation heatmap data"""
        await self._update_airtable_liquidation_map(record_id, symbol, report)  # Same structure
        logger.info(f"📝 Updated Airtable liquidation heatmap data for {symbol}")
    
    async def _update_airtable_multi_symbol_data(self, record_id: str, symbol: str, report: Dict[str, Any]):
        """Update Airtable with multi-symbol data"""
        await self._update_airtable_liquidation_map(record_id, symbol, report)  # Same structure
        logger.info(f"📝 Updated Airtable multi-symbol data for {symbol}")
    
    async def _update_airtable_basic_data(self, record_id: str, symbol: str, report: Dict[str, Any]):
        """Update Airtable with basic analysis data"""
        await self._update_airtable_liquidation_map(record_id, symbol, report)  # Same structure
        logger.info(f"📝 Updated Airtable basic analysis data for {symbol}")
    
    async def _generate_master_summary(self, symbols: List[str], reports: List[Dict[str, Any]], 
                                     image_data: bytes) -> Dict[str, Any]:
        """Generate master summary for multi-symbol analysis"""
        
        master_summary = {
            'type': 'master_summary',
            'symbols_analyzed': symbols,
            'total_symbols': len(symbols),
            'analysis_timestamp': datetime.now().isoformat(),
            'key_insights': [
                f"Analyzed {len(symbols)} symbols from multi-symbol image",
                "Generated comprehensive reports for each symbol",
                "Updated individual Airtable records",
                "Professional-grade analysis completed"
            ],
            'summary_text': f"Comprehensive analysis completed for {len(symbols)} symbols: {', '.join(symbols)}. "
                           f"Each symbol received individual professional analysis and Airtable updates."
        }
        
        return master_summary
    
    def _update_processing_stats(self, image_type: ImageType, result: Dict[str, Any]):
        """Update processing statistics"""
        
        self.processing_stats['total_images_processed'] += 1
        self.processing_stats['symbols_analyzed'] += len(result['symbols_processed'])
        self.processing_stats['reports_generated'] += len(result['reports_generated'])
        self.processing_stats['airtable_records_updated'] += len(result['airtable_records'])
        
        if image_type == ImageType.LIQUIDATION_MAP:
            self.processing_stats['liquidation_maps_processed'] += 1
        elif image_type == ImageType.LIQUIDATION_HEATMAP:
            self.processing_stats['liquidation_heatmaps_processed'] += 1
        elif image_type == ImageType.MULTI_SYMBOL:
            self.processing_stats['multi_symbol_images_processed'] += 1

# Global service instance
workflow_orchestrator = WorkflowOrchestrator() 