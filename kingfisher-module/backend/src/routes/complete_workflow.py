"""
KingFisher Complete Workflow API
Automatic image processing with multi-agent coordination
"""

from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from typing import Dict, Any, Optional
import logging
import json

from src.services.workflow_orchestrator import workflow_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Complete Workflow"])

@router.post("/process-complete-workflow")
async def process_complete_workflow(
    image_file: UploadFile = File(...),
    context_text: str = Form(""),
    image_filename: str = Form("")
) -> Dict[str, Any]:
    """
    Complete KingFisher workflow - automatically processes any image type:
    - Liquidation Maps: Single symbol analysis with liquidation cluster data
    - Liquidation Heatmaps: Single symbol analysis with thermal data  
    - Multi-Symbol Images: Multiple symbols analysis from one image
    - Automatic symbol detection, Airtable management, and professional reports
    """
    
    try:
        # Read image data
        image_data = await image_file.read()
        filename = image_filename or image_file.filename or "unknown_image"
        
        logger.info(f"🚀 Starting complete workflow for: {filename}")
        logger.info(f"📝 Context: {context_text[:100]}..." if len(context_text) > 100 else f"📝 Context: {context_text}")
        
        # Execute complete workflow
        result = await workflow_orchestrator.process_image_workflow(
            image_data=image_data,
            image_filename=filename,
            context_text=context_text
        )
        
        if result.success:
            logger.info(f"✅ Workflow completed successfully!")
            logger.info(f"📊 Processed {len(result.symbols_processed)} symbols")
            logger.info(f"📝 Generated {len(result.reports_generated)} reports")
            logger.info(f"🗃️ Updated {len(result.airtable_records)} Airtable records")
            
            return {
                "success": True,
                "message": f"Complete workflow executed successfully for {result.image_type}",
                "workflow_result": {
                    "image_type": result.image_type,
                    "symbols_processed": result.symbols_processed,
                    "airtable_records": result.airtable_records,
                    "processing_time": result.processing_time,
                    "reports_count": len(result.reports_generated),
                    "errors": result.errors
                },
                "processing_stats": result.metadata.get('workflow_stats', {}),
                "classification_details": result.metadata.get('classification', {})
            }
        else:
            logger.error(f"❌ Workflow failed: {result.errors}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Workflow execution failed",
                    "errors": result.errors,
                    "processing_time": result.processing_time
                }
            )
            
    except Exception as e:
        error_msg = f"❌ Complete workflow error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/workflow-stats")
async def get_workflow_stats() -> Dict[str, Any]:
    """Get KingFisher workflow processing statistics"""
    
    try:
        stats = workflow_orchestrator.processing_stats
        
        return {
            "success": True,
            "workflow_statistics": stats,
            "performance_metrics": {
                "avg_symbols_per_image": (
                    stats['symbols_analyzed'] / max(stats['total_images_processed'], 1)
                ),
                "avg_reports_per_image": (
                    stats['reports_generated'] / max(stats['total_images_processed'], 1)
                ),
                "airtable_update_rate": (
                    stats['airtable_records_updated'] / max(stats['symbols_analyzed'], 1)
                )
            }
        }
        
    except Exception as e:
        error_msg = f"❌ Error getting workflow stats: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/test-image-classification")
async def test_image_classification(
    image_file: UploadFile = File(...),
    context_text: str = Form(""),
    image_filename: str = Form("")
) -> Dict[str, Any]:
    """Test image classification without full processing"""
    
    try:
        from src.services.image_classification_agent import image_classification_agent
        
        # Read image data
        image_data = await image_file.read()
        filename = image_filename or image_file.filename or "unknown_image"
        
        # Classify image
        classification = await image_classification_agent.classify_image(
            image_data, filename, context_text
        )
        
        return {
            "success": True,
            "classification": {
                "image_type": classification.image_type.value,
                "confidence": classification.confidence,
                "detected_symbols": classification.detected_symbols,
                "processing_workflow": classification.processing_workflow,
                "metadata": classification.metadata
            }
        }
        
    except Exception as e:
        error_msg = f"❌ Image classification error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) 