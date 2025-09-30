"""
KingFisher Image Classification Agent
Automatically classifies images and determines processing workflow
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import re

logger = logging.getLogger(__name__)

class ImageType(Enum):
    LIQUIDATION_MAP = "liquidation_map"
    LIQUIDATION_HEATMAP = "liquidation_heatmap"
    MULTI_SYMBOL = "multi_symbol"
    UNKNOWN = "unknown"

@dataclass
class ImageClassification:
    image_type: ImageType
    confidence: float
    detected_symbols: List[str]
    processing_workflow: str
    metadata: Dict[str, Any]

class ImageClassificationAgent:
    """Agent that classifies images and determines processing workflow"""
    
    def __init__(self):
        self.classification_rules = {
            'liquidation_map_keywords': [
                'liquidation map', 'liquidation clusters', 'liq map',
                'cluster map', 'liquidation levels', 'liq clusters'
            ],
            'liquidation_heatmap_keywords': [
                'liquidation heatmap', 'liq heatmap', 'heat map',
                'liquidation heat', 'thermal map', 'heatmap'
            ],
            'multi_symbol_keywords': [
                'screener', 'scanner', 'multiple symbols', 'symbol list',
                'market overview', 'crypto screener', 'ai screener'
            ]
        }
        
    async def classify_image(self, image_data: bytes, image_filename: str = "", 
                           context_text: str = "") -> ImageClassification:
        """Classify image and determine processing workflow"""
        
        try:
            # Step 1: Analyze filename and context
            filename_classification = self._analyze_filename(image_filename)
            context_classification = self._analyze_context_text(context_text)
            
            # Step 2: Perform image content analysis (simplified)
            content_classification = await self._analyze_image_content(image_data)
            
            # Step 3: Combine classifications with confidence scoring
            final_classification = self._combine_classifications(
                filename_classification, 
                context_classification, 
                content_classification
            )
            
            # Step 4: Determine processing workflow
            workflow = self._determine_workflow(final_classification)
            
            logger.info(f"🔍 Image classified as: {final_classification.image_type.value} "
                       f"(confidence: {final_classification.confidence:.2f})")
            
            return final_classification
            
        except Exception as e:
            logger.error(f"❌ Error classifying image: {e}")
            return ImageClassification(
                image_type=ImageType.UNKNOWN,
                confidence=0.0,
                detected_symbols=[],
                processing_workflow="unknown",
                metadata={"error": str(e)}
            )
    
    def _analyze_filename(self, filename: str) -> Dict[str, Any]:
        """Analyze filename for classification clues"""
        filename_lower = filename.lower()
        
        # Check for liquidation map indicators
        if any(keyword in filename_lower for keyword in self.classification_rules['liquidation_map_keywords']):
            return {
                'type': ImageType.LIQUIDATION_MAP,
                'confidence': 0.8,
                'source': 'filename'
            }
        
        # Check for liquidation heatmap indicators
        if any(keyword in filename_lower for keyword in self.classification_rules['liquidation_heatmap_keywords']):
            return {
                'type': ImageType.LIQUIDATION_HEATMAP,
                'confidence': 0.8,
                'source': 'filename'
            }
        
        # Check for multi-symbol indicators
        if any(keyword in filename_lower for keyword in self.classification_rules['multi_symbol_keywords']):
            return {
                'type': ImageType.MULTI_SYMBOL,
                'confidence': 0.7,
                'source': 'filename'
            }
        
        return {
            'type': ImageType.UNKNOWN,
            'confidence': 0.0,
            'source': 'filename'
        }
    
    def _analyze_context_text(self, context_text: str) -> Dict[str, Any]:
        """Analyze context text (Telegram message, etc.) for classification"""
        if not context_text:
            return {'type': ImageType.UNKNOWN, 'confidence': 0.0, 'source': 'context'}
        
        context_lower = context_text.lower()
        
        # Extract potential symbols from context
        symbol_pattern = r'\b([A-Z]{2,10}USDT?)\b'
        detected_symbols = re.findall(symbol_pattern, context_text.upper())
        
        # Check for liquidation map indicators
        if any(keyword in context_lower for keyword in self.classification_rules['liquidation_map_keywords']):
            return {
                'type': ImageType.LIQUIDATION_MAP,
                'confidence': 0.9,
                'symbols': detected_symbols[:1] if detected_symbols else [],  # Single symbol for liquidation maps
                'source': 'context'
            }
        
        # Check for liquidation heatmap indicators
        if any(keyword in context_lower for keyword in self.classification_rules['liquidation_heatmap_keywords']):
            return {
                'type': ImageType.LIQUIDATION_HEATMAP,
                'confidence': 0.9,
                'symbols': detected_symbols[:1] if detected_symbols else [],  # Single symbol for heatmaps
                'source': 'context'
            }
        
        # Check for multi-symbol indicators or multiple symbols detected
        if (any(keyword in context_lower for keyword in self.classification_rules['multi_symbol_keywords']) 
            or len(detected_symbols) > 1):
            return {
                'type': ImageType.MULTI_SYMBOL,
                'confidence': 0.8,
                'symbols': detected_symbols,  # Multiple symbols
                'source': 'context'
            }
        
        # Single symbol detected without specific type indicators
        if len(detected_symbols) == 1:
            return {
                'type': ImageType.LIQUIDATION_MAP,  # Default assumption for single symbol
                'confidence': 0.6,
                'symbols': detected_symbols,
                'source': 'context'
            }
        
        return {
            'type': ImageType.UNKNOWN,
            'confidence': 0.0,
            'symbols': [],
            'source': 'context'
        }
    
    async def _analyze_image_content(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image content for classification (simplified OCR/pattern recognition)"""
        
        # For now, we'll use a simplified approach
        # In a full implementation, this would use OCR, computer vision, or AI models
        
        try:
            # Simulate image analysis based on image size and characteristics
            image_size = len(image_data)
            
            # Larger images are more likely to be multi-symbol screeners
            if image_size > 500000:  # > 500KB
                return {
                    'type': ImageType.MULTI_SYMBOL,
                    'confidence': 0.6,
                    'source': 'content_analysis'
                }
            
            # Medium-sized images are likely liquidation maps/heatmaps
            elif image_size > 100000:  # > 100KB
                return {
                    'type': ImageType.LIQUIDATION_MAP,
                    'confidence': 0.5,
                    'source': 'content_analysis'
                }
            
            return {
                'type': ImageType.UNKNOWN,
                'confidence': 0.3,
                'source': 'content_analysis'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error in image content analysis: {e}")
            return {
                'type': ImageType.UNKNOWN,
                'confidence': 0.0,
                'source': 'content_analysis'
            }
    
    def _combine_classifications(self, filename_result: Dict[str, Any], 
                               context_result: Dict[str, Any], 
                               content_result: Dict[str, Any]) -> ImageClassification:
        """Combine multiple classification results with weighted scoring"""
        
        # Weight the different sources
        weights = {
            'context': 0.6,    # Context text is most reliable
            'filename': 0.3,   # Filename is moderately reliable
            'content_analysis': 0.1  # Content analysis is least reliable (simplified)
        }
        
        # Collect all results
        results = [
            (filename_result, weights['filename']),
            (context_result, weights['context']),
            (content_result, weights['content_analysis'])
        ]
        
        # Score each image type
        type_scores = {
            ImageType.LIQUIDATION_MAP: 0.0,
            ImageType.LIQUIDATION_HEATMAP: 0.0,
            ImageType.MULTI_SYMBOL: 0.0,
            ImageType.UNKNOWN: 0.0
        }
        
        detected_symbols = []
        metadata = {}
        
        for result, weight in results:
            if result['type'] != ImageType.UNKNOWN:
                type_scores[result['type']] += result['confidence'] * weight
            
            # Collect symbols
            if 'symbols' in result:
                detected_symbols.extend(result['symbols'])
            
            # Collect metadata
            metadata[f"{result['source']}_result"] = result
        
        # Remove duplicates from symbols
        detected_symbols = list(set(detected_symbols))
        
        # Find the highest scoring type
        best_type = max(type_scores.items(), key=lambda x: x[1])
        final_type = best_type[0]
        final_confidence = min(best_type[1], 1.0)  # Cap at 1.0
        
        # If confidence is too low, mark as unknown
        if final_confidence < 0.3:
            final_type = ImageType.UNKNOWN
            final_confidence = 0.0
        
        return ImageClassification(
            image_type=final_type,
            confidence=final_confidence,
            detected_symbols=detected_symbols,
            processing_workflow=self._determine_workflow_type(final_type),
            metadata=metadata
        )
    
    def _determine_workflow_type(self, image_type: ImageType) -> str:
        """Determine the processing workflow based on image type"""
        
        workflow_map = {
            ImageType.LIQUIDATION_MAP: "single_symbol_liquidation_map",
            ImageType.LIQUIDATION_HEATMAP: "single_symbol_liquidation_heatmap", 
            ImageType.MULTI_SYMBOL: "multi_symbol_analysis",
            ImageType.UNKNOWN: "manual_review"
        }
        
        return workflow_map.get(image_type, "manual_review")
    
    def _determine_workflow(self, classification: ImageClassification) -> ImageClassification:
        """Add workflow-specific metadata"""
        
        workflow_metadata = {
            "processing_steps": [],
            "expected_outputs": [],
            "airtable_strategy": ""
        }
        
        if classification.image_type == ImageType.LIQUIDATION_MAP:
            workflow_metadata.update({
                "processing_steps": [
                    "extract_single_symbol",
                    "find_or_create_airtable_record", 
                    "analyze_liquidation_clusters",
                    "update_liquidation_map_field"
                ],
                "expected_outputs": ["liquidation_analysis", "cluster_data"],
                "airtable_strategy": "single_record_update"
            })
            
        elif classification.image_type == ImageType.LIQUIDATION_HEATMAP:
            workflow_metadata.update({
                "processing_steps": [
                    "extract_single_symbol",
                    "find_or_create_airtable_record",
                    "analyze_liquidation_heatmap", 
                    "update_heatmap_field"
                ],
                "expected_outputs": ["heatmap_analysis", "thermal_data"],
                "airtable_strategy": "single_record_update"
            })
            
        elif classification.image_type == ImageType.MULTI_SYMBOL:
            workflow_metadata.update({
                "processing_steps": [
                    "extract_all_symbols",
                    "analyze_each_symbol_individually",
                    "find_or_create_multiple_airtable_records",
                    "generate_individual_reports",
                    "compose_master_summary"
                ],
                "expected_outputs": ["multiple_symbol_reports", "master_summary"],
                "airtable_strategy": "multiple_record_updates"
            })
        
        # Add workflow metadata to classification
        classification.metadata.update(workflow_metadata)
        
        return classification

# Global service instance
image_classification_agent = ImageClassificationAgent() 