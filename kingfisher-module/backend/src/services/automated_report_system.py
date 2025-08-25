#!/usr/bin/env python3
"""
Automated Report Generation System
Automatically generates professional reports after image processing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

from .enhanced_report_generator import EnhancedReportGenerator, EnhancedReport
from .master_summary_agent import MasterSummaryAgent

logger = logging.getLogger(__name__)

@dataclass
class ReportJob:
    """Data structure for report generation jobs"""
    job_id: str
    symbol: str
    analysis_type: str
    analysis_data: Dict[str, Any]
    priority: int
    status: str  # 'pending', 'processing', 'completed', 'failed'
    created_at: str
    completed_at: Optional[str] = None
    report: Optional[EnhancedReport] = None
    error: Optional[str] = None

class AutomatedReportSystem:
    """Automated system for generating professional reports"""
    
    def __init__(self):
        self.report_generator = EnhancedReportGenerator()
        self.master_summary_agent = MasterSummaryAgent()
        self.report_queue: List[ReportJob] = []
        self.completed_reports: List[ReportJob] = []
        self.is_running = False
        
    async def start_automation(self):
        """Start the automated report generation system"""
        try:
            logger.info("🚀 Starting Automated Report Generation System...")
            self.is_running = True
            
            # Start the report processing loop
            asyncio.create_task(self._process_report_queue())
            
            # Start the master summary generation loop
            asyncio.create_task(self._generate_master_summaries())
            
            logger.info("✅ Automated Report System started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error starting automated report system: {str(e)}")
            self.is_running = False
    
    async def stop_automation(self):
        """Stop the automated report generation system"""
        logger.info("🛑 Stopping Automated Report Generation System...")
        self.is_running = False
    
    async def add_report_job(self, symbol: str, analysis_type: str, analysis_data: Dict[str, Any], priority: int = 1) -> str:
        """Add a new report generation job to the queue"""
        try:
            job_id = f"RPT_{symbol}_{int(datetime.now().timestamp())}"
            
            job = ReportJob(
                job_id=job_id,
                symbol=symbol,
                analysis_type=analysis_type,
                analysis_data=analysis_data,
                priority=priority,
                status='pending',
                created_at=datetime.now().isoformat()
            )
            
            # Add to queue and sort by priority
            self.report_queue.append(job)
            self.report_queue.sort(key=lambda x: x.priority, reverse=True)
            
            logger.info(f"📝 Added report job {job_id} for {symbol} ({analysis_type})")
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Error adding report job: {str(e)}")
            return ""
    
    async def _process_report_queue(self):
        """Process the report generation queue"""
        while self.is_running:
            try:
                if self.report_queue:
                    # Get the highest priority job
                    job = self.report_queue.pop(0)
                    
                    logger.info(f"🔄 Processing report job {job.job_id} for {job.symbol}")
                    
                    # Update job status
                    job.status = 'processing'
                    
                    # Generate the report
                    report = await self.report_generator.generate_enhanced_report(
                        job.analysis_data, 
                        job.analysis_type
                    )
                    
                    # Update job with completed report
                    job.report = report
                    job.status = 'completed'
                    job.completed_at = datetime.now().isoformat()
                    
                    # Move to completed reports
                    self.completed_reports.append(job)
                    
                    logger.info(f"✅ Completed report job {job.job_id} for {job.symbol}")
                    
                    # Store report in Airtable (if configured)
                    await self._store_report_in_airtable(job)
                    
                else:
                    # No jobs in queue, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error processing report queue: {str(e)}")
                await asyncio.sleep(5)
    
    async def _generate_master_summaries(self):
        """Generate master summaries periodically"""
        while self.is_running:
            try:
                # Generate master summary every hour
                if len(self.completed_reports) > 0:
                    logger.info("🎯 Generating master summary from completed reports...")
                    
                    master_summary = await self.master_summary_agent.generate_master_summary(hours_back=24)
                    
                    # Store master summary
                    await self._store_master_summary(master_summary)
                    
                    logger.info("✅ Master summary generated and stored")
                
                # Wait for 1 hour before next generation
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"❌ Error generating master summary: {str(e)}")
                await asyncio.sleep(300)  # 5 minutes on error
    
    async def _store_report_in_airtable(self, job: ReportJob):
        """Store the completed report in Airtable"""
        try:
            if job.report:
                # This would integrate with your existing Airtable service
                # For now, we'll just log the storage
                logger.info(f"🗃️ Storing report {job.job_id} in Airtable")
                
                # Here you would call your Airtable service to store the report
                # await airtable_service.store_report(job.report)
                
        except Exception as e:
            logger.error(f"❌ Error storing report in Airtable: {str(e)}")
    
    async def _store_master_summary(self, master_summary):
        """Store the master summary"""
        try:
            logger.info(f"🗃️ Storing master summary in Airtable")
            
            # Here you would call your Airtable service to store the master summary
            # await airtable_service.store_master_summary(master_summary)
            
        except Exception as e:
            logger.error(f"❌ Error storing master summary: {str(e)}")
    
    async def get_report_status(self, job_id: str) -> Optional[ReportJob]:
        """Get the status of a specific report job"""
        # Check completed reports first
        for job in self.completed_reports:
            if job.job_id == job_id:
                return job
        
        # Check pending jobs
        for job in self.report_queue:
            if job.job_id == job_id:
                return job
        
        return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the automated report system"""
        return {
            "is_running": self.is_running,
            "queue_size": len(self.report_queue),
            "completed_count": len(self.completed_reports),
            "pending_jobs": [
                {
                    "job_id": job.job_id,
                    "symbol": job.symbol,
                    "analysis_type": job.analysis_type,
                    "priority": job.priority,
                    "created_at": job.created_at
                }
                for job in self.report_queue
            ],
            "recent_completed": [
                {
                    "job_id": job.job_id,
                    "symbol": job.symbol,
                    "analysis_type": job.analysis_type,
                    "completed_at": job.completed_at
                }
                for job in self.completed_reports[-10:]  # Last 10 completed
            ]
        }
    
    async def trigger_immediate_report(self, symbol: str, analysis_type: str, analysis_data: Dict[str, Any]) -> EnhancedReport:
        """Trigger an immediate report generation (bypass queue)"""
        try:
            logger.info(f"⚡ Generating immediate report for {symbol}")
            
            report = await self.report_generator.generate_enhanced_report(
                analysis_data, 
                analysis_type
            )
            
            logger.info(f"✅ Immediate report generated for {symbol}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating immediate report: {str(e)}")
            raise
    
    async def get_report_statistics(self) -> Dict[str, Any]:
        """Get statistics about report generation"""
        total_reports = len(self.completed_reports)
        
        if total_reports == 0:
            return {
                "total_reports": 0,
                "average_processing_time": 0,
                "success_rate": 0,
                "reports_by_type": {},
                "reports_by_symbol": {}
            }
        
        # Calculate processing times
        processing_times = []
        for job in self.completed_reports:
            if job.completed_at:
                created = datetime.fromisoformat(job.created_at)
                completed = datetime.fromisoformat(job.completed_at)
                processing_time = (completed - created).total_seconds()
                processing_times.append(processing_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Count by type
        reports_by_type = {}
        for job in self.completed_reports:
            report_type = job.analysis_type
            reports_by_type[report_type] = reports_by_type.get(report_type, 0) + 1
        
        # Count by symbol
        reports_by_symbol = {}
        for job in self.completed_reports:
            symbol = job.symbol
            reports_by_symbol[symbol] = reports_by_symbol.get(symbol, 0) + 1
        
        # Calculate success rate
        successful_reports = sum(1 for job in self.completed_reports if job.status == 'completed')
        success_rate = (successful_reports / total_reports) * 100 if total_reports > 0 else 0
        
        return {
            "total_reports": total_reports,
            "average_processing_time": avg_processing_time,
            "success_rate": success_rate,
            "reports_by_type": reports_by_type,
            "reports_by_symbol": reports_by_symbol,
            "queue_size": len(self.report_queue)
        }
    
    async def cleanup_old_reports(self, days_to_keep: int = 7):
        """Clean up old completed reports"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Filter out old reports
            self.completed_reports = [
                job for job in self.completed_reports
                if datetime.fromisoformat(job.created_at) > cutoff_date
            ]
            
            logger.info(f"🧹 Cleaned up reports older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old reports: {str(e)}")
    
    async def export_reports(self, format_type: str = 'json') -> str:
        """Export completed reports in specified format"""
        try:
            if format_type == 'json':
                export_data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "total_reports": len(self.completed_reports),
                    "reports": [
                        {
                            "job_id": job.job_id,
                            "symbol": job.symbol,
                            "analysis_type": job.analysis_type,
                            "status": job.status,
                            "created_at": job.created_at,
                            "completed_at": job.completed_at,
                            "report_summary": {
                                "confidence_score": job.report.confidence_score if job.report else 0,
                                "risk_level": job.report.risk_level if job.report else 'unknown',
                                "executive_summary": job.report.executive_summary if job.report else ''
                            } if job.report else None
                        }
                        for job in self.completed_reports
                    ]
                }
                
                return json.dumps(export_data, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"❌ Error exporting reports: {str(e)}")
            return ""

# Global instance
automated_report_system = AutomatedReportSystem() 