#!/usr/bin/env python3
"""
Automated Reports API Routes
Provides endpoints for automated professional report generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime

from src.services.automated_report_system import automated_report_system

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Automated Reports"])

class ReportJobRequest(BaseModel):
    """Request model for creating a report job"""
    symbol: str
    analysis_type: str
    analysis_data: Dict[str, Any]
    priority: int = 1

class ImmediateReportRequest(BaseModel):
    """Request model for immediate report generation"""
    symbol: str
    analysis_type: str
    analysis_data: Dict[str, Any]

class ReportJobResponse(BaseModel):
    """Response model for report job"""
    job_id: str
    symbol: str
    analysis_type: str
    status: str
    created_at: str
    priority: int

class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    is_running: bool
    queue_size: int
    completed_count: int
    pending_jobs: List[Dict[str, Any]]
    recent_completed: List[Dict[str, Any]]

@router.post("/start-automation")
async def start_automation():
    """Start the automated report generation system"""
    try:
        logger.info("🚀 Starting automated report system via API...")
        
        await automated_report_system.start_automation()
        
        return {
            "status": "success",
            "message": "Automated report system started successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting automation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start automation: {str(e)}")

@router.post("/stop-automation")
async def stop_automation():
    """Stop the automated report generation system"""
    try:
        logger.info("🛑 Stopping automated report system via API...")
        
        await automated_report_system.stop_automation()
        
        return {
            "status": "success",
            "message": "Automated report system stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error stopping automation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop automation: {str(e)}")

@router.post("/add-job", response_model=ReportJobResponse)
async def add_report_job(request: ReportJobRequest):
    """Add a new report generation job to the queue"""
    try:
        logger.info(f"📝 Adding report job for {request.symbol}...")
        
        job_id = await automated_report_system.add_report_job(
            symbol=request.symbol,
            analysis_type=request.analysis_type,
            analysis_data=request.analysis_data,
            priority=request.priority
        )
        
        if not job_id:
            raise HTTPException(status_code=500, detail="Failed to create report job")
        
        return ReportJobResponse(
            job_id=job_id,
            symbol=request.symbol,
            analysis_type=request.analysis_type,
            status="pending",
            created_at=datetime.now().isoformat(),
            priority=request.priority
        )
        
    except Exception as e:
        logger.error(f"❌ Error adding report job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add report job: {str(e)}")

@router.post("/generate-immediate")
async def generate_immediate_report(request: ImmediateReportRequest):
    """Generate a report immediately (bypass queue)"""
    try:
        logger.info(f"⚡ Generating immediate report for {request.symbol}...")
        
        report = await automated_report_system.trigger_immediate_report(
            symbol=request.symbol,
            analysis_type=request.analysis_type,
            analysis_data=request.analysis_data
        )
        
        return {
            "status": "success",
            "symbol": request.symbol,
            "analysis_type": request.analysis_type,
            "report_id": report.report_id,
            "confidence_score": report.confidence_score,
            "risk_level": report.risk_level,
            "executive_summary": report.executive_summary,
            "formatted_report": report.formatted_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating immediate report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate immediate report: {str(e)}")

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a specific report job"""
    try:
        job = await automated_report_system.get_report_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        response = {
            "job_id": job.job_id,
            "symbol": job.symbol,
            "analysis_type": job.analysis_type,
            "status": job.status,
            "priority": job.priority,
            "created_at": job.created_at,
            "completed_at": job.completed_at
        }
        
        if job.report:
            response.update({
                "confidence_score": job.report.confidence_score,
                "risk_level": job.report.risk_level,
                "executive_summary": job.report.executive_summary
            })
        
        if job.error:
            response["error"] = job.error
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.get("/system-status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get the current status of the automated report system"""
    try:
        status = await automated_report_system.get_system_status()
        return SystemStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"❌ Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/statistics")
async def get_report_statistics():
    """Get statistics about report generation"""
    try:
        stats = await automated_report_system.get_report_statistics()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting report statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get report statistics: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_reports(days_to_keep: int = 7):
    """Clean up old completed reports"""
    try:
        await automated_report_system.cleanup_old_reports(days_to_keep)
        
        return {
            "status": "success",
            "message": f"Cleaned up reports older than {days_to_keep} days",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup reports: {str(e)}")

@router.get("/export")
async def export_reports(format_type: str = 'json'):
    """Export completed reports"""
    try:
        export_data = await automated_report_system.export_reports(format_type)
        
        return {
            "status": "success",
            "format": format_type,
            "data": export_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error exporting reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export reports: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for the automated report system"""
    try:
        status = await automated_report_system.get_system_status()
        
        health_status = {
            "status": "healthy" if status["is_running"] else "stopped",
            "timestamp": datetime.now().isoformat(),
            "system_running": status["is_running"],
            "queue_size": status["queue_size"],
            "completed_count": status["completed_count"],
            "service": "automated_report_system"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Automated report system health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "service": "automated_report_system"
        }

@router.get("/queue")
async def get_queue_status():
    """Get detailed queue information"""
    try:
        status = await automated_report_system.get_system_status()
        
        return {
            "status": "success",
            "queue_information": {
                "total_pending": len(status["pending_jobs"]),
                "total_completed": status["completed_count"],
                "system_running": status["is_running"],
                "pending_jobs": status["pending_jobs"],
                "recent_completed": status["recent_completed"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting queue status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")

@router.delete("/job/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a pending report job"""
    try:
        # This would require adding a cancel method to the automated report system
        # For now, we'll return a not implemented response
        
        return {
            "status": "not_implemented",
            "message": "Job cancellation not yet implemented",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error canceling job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}") 