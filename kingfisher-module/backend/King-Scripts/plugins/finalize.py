#!/usr/bin/env python3
"""
Finalize Plugin for STEP-5
Handles final processing, summary generation, and cleanup
"""

import os
import json
import logging
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Import the base plugin class
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from step5_runner import BasePlugin, ProcessingContext

logger = logging.getLogger(__name__)

class FinalizePlugin(BasePlugin):
    """Plugin for final processing steps, summary generation, and cleanup"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.generate_summary = config.get("generate_summary", True)
        self.cleanup_temp = config.get("cleanup_temp", True)
        self.save_results = config.get("save_results", True)
        self.results_dir = config.get("results_dir", "results")
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate context - finalize plugin is always valid"""
        return True
    
    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Execute finalization logic"""
        logger.info("🎯 Finalizing STEP-5 processing")
        
        # 1. Generate comprehensive summary
        if self.generate_summary:
            context = self._generate_processing_summary(context)
        
        # 2. Save results to disk
        if self.save_results:
            context = self._save_results(context)
        
        # 3. Validate processing completeness
        context = self._validate_processing_completeness(context)
        
        # 4. Clean up temporary files
        if self.cleanup_temp:
            context = self._cleanup_temporary_files(context)
        
        # 5. Add finalization metadata
        context.processing_metadata["finalization"] = {
            "summary_generated": self.generate_summary,
            "results_saved": self.save_results,
            "cleanup_performed": self.cleanup_temp,
            "processing_complete": len(context.errors) == 0,
            "finalization_timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ STEP-5 finalization completed")
        return context
    
    def _generate_processing_summary(self, context: ProcessingContext) -> ProcessingContext:
        """Generate comprehensive processing summary"""
        try:
            logger.info("📊 Generating processing summary")
            
            summary = {
                "symbol": context.symbol,
                "image_path": context.image_path,
                "processing_start": context.processing_metadata.get("start_time"),
                "processing_end": datetime.now().isoformat(),
                "total_duration": self._calculate_total_duration(context),
                "plugin_results": context.processing_metadata.get("plugin_results", {}),
                "analysis_data": context.analysis_data,
                "market_data": context.market_data,
                "liquidation_clusters": {
                    "total_clusters": len(context.liquidation_clusters),
                    "clusters": context.liquidation_clusters
                },
                "errors": context.errors,
                "success": len(context.errors) == 0,
                "quality_score": self._calculate_quality_score(context)
            }
            
            # Add detailed plugin performance
            summary["plugin_performance"] = self._analyze_plugin_performance(context)
            
            # Add processing insights
            summary["insights"] = self._generate_insights(context)
            
            context.analysis_data["processing_summary"] = summary
            
            logger.info(f"✅ Processing summary generated (Quality Score: {summary['quality_score']}/100)")
            
        except Exception as e:
            error_msg = f"Failed to generate processing summary: {e}"
            context.errors.append(error_msg)
            logger.error(error_msg)
        
        return context
    
    def _save_results(self, context: ProcessingContext) -> ProcessingContext:
        """Save processing results to disk"""
        try:
            logger.info("💾 Saving processing results")
            
            # Create results directory
            results_path = Path(self.results_dir)
            results_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            symbol = context.symbol or "unknown"
            filename = f"step5_results_{symbol}_{timestamp}.json"
            
            file_path = results_path / filename
            
            # Prepare results data
            results_data = {
                "metadata": {
                    "symbol": context.symbol,
                    "image_path": context.image_path,
                    "processing_timestamp": datetime.now().isoformat(),
                    "step5_version": "1.1.0"
                },
                "processing_context": {
                    "symbol": context.symbol,
                    "image_path": context.image_path,
                    "analysis_data": context.analysis_data,
                    "market_data": context.market_data,
                    "liquidation_clusters": context.liquidation_clusters,
                    "processing_metadata": context.processing_metadata,
                    "errors": context.errors
                }
            }
            
            # Save to JSON file
            with open(file_path, 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
            
            # Add file path to context
            context.processing_metadata["results_file"] = str(file_path)
            
            logger.info(f"✅ Results saved to: {file_path}")
            
        except Exception as e:
            error_msg = f"Failed to save results: {e}"
            context.errors.append(error_msg)
            logger.error(error_msg)
        
        return context
    
    def _validate_processing_completeness(self, context: ProcessingContext) -> ProcessingContext:
        """Validate that processing completed successfully"""
        logger.info("✔️ Validating processing completeness")
        
        validation_results = {
            "symbol_present": bool(context.symbol),
            "analysis_data_present": bool(context.analysis_data),
            "market_data_present": bool(context.market_data),
            "liquidation_clusters_extracted": len(context.liquidation_clusters) > 0,
            "no_critical_errors": len(context.errors) == 0,
            "all_plugins_executed": bool(context.processing_metadata.get("plugin_results"))
        }
        
        # Calculate completeness score
        total_checks = len(validation_results)
        passed_checks = sum(1 for result in validation_results.values() if result)
        completeness_score = (passed_checks / total_checks) * 100
        
        validation_summary = {
            "validation_results": validation_results,
            "completeness_score": round(completeness_score, 1),
            "validation_passed": completeness_score >= 80,  # 80% threshold
            "validation_timestamp": datetime.now().isoformat()
        }
        
        context.processing_metadata["validation"] = validation_summary
        
        if completeness_score >= 80:
            logger.info(f"✅ Processing validation passed: {completeness_score}%")
        else:
            logger.warning(f"⚠️ Processing validation failed: {completeness_score}%")
            
        return context
    
    def _cleanup_temporary_files(self, context: ProcessingContext) -> ProcessingContext:
        """Clean up temporary files and directories"""
        try:
            logger.info("🧹 Cleaning up temporary files")
            
            cleanup_stats = {
                "files_removed": 0,
                "directories_removed": 0,
                "space_freed_mb": 0,
                "errors": []
            }
            
            # Define temp directories to clean
            temp_dirs = [
                "temp",
                "tmp", 
                ".tmp",
                "cache",
                "__pycache__"
            ]
            
            base_path = Path(context.image_path).parent if context.image_path else Path.cwd()
            
            for temp_dir_name in temp_dirs:
                temp_dir = base_path / temp_dir_name
                
                if temp_dir.exists() and temp_dir.is_dir():
                    try:
                        # Calculate directory size before removal
                        dir_size = sum(f.stat().st_size for f in temp_dir.rglob('*') if f.is_file())
                        cleanup_stats["space_freed_mb"] += dir_size / (1024 * 1024)
                        
                        # Remove directory
                        shutil.rmtree(temp_dir)
                        cleanup_stats["directories_removed"] += 1
                        
                        logger.debug(f"Removed temp directory: {temp_dir}")
                        
                    except Exception as e:
                        error_msg = f"Failed to remove {temp_dir}: {e}"
                        cleanup_stats["errors"].append(error_msg)
                        logger.warning(error_msg)
            
            # Clean up specific temp file patterns
            temp_patterns = ["*.tmp", "*.temp", ".DS_Store"]
            
            for pattern in temp_patterns:
                for temp_file in base_path.rglob(pattern):
                    try:
                        file_size = temp_file.stat().st_size
                        temp_file.unlink()
                        
                        cleanup_stats["files_removed"] += 1
                        cleanup_stats["space_freed_mb"] += file_size / (1024 * 1024)
                        
                        logger.debug(f"Removed temp file: {temp_file}")
                        
                    except Exception as e:
                        error_msg = f"Failed to remove {temp_file}: {e}"
                        cleanup_stats["errors"].append(error_msg)
                        logger.warning(error_msg)
            
            # Round space freed
            cleanup_stats["space_freed_mb"] = round(cleanup_stats["space_freed_mb"], 2)
            
            context.processing_metadata["cleanup"] = cleanup_stats
            
            logger.info(f"✅ Cleanup completed: {cleanup_stats['files_removed']} files, "
                       f"{cleanup_stats['directories_removed']} directories, "
                       f"{cleanup_stats['space_freed_mb']} MB freed")
            
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            context.errors.append(error_msg)
            logger.error(error_msg)
        
        return context
    
    def _calculate_total_duration(self, context: ProcessingContext) -> float:
        """Calculate total processing duration in seconds"""
        try:
            start_time = context.processing_metadata.get("pipeline_start") or context.processing_metadata.get("start_time")
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                duration = (datetime.now() - start_dt.replace(tzinfo=None)).total_seconds()
                return round(duration, 2)
        except Exception:
            pass
        
        return 0.0
    
    def _calculate_quality_score(self, context: ProcessingContext) -> int:
        """Calculate overall processing quality score (0-100)"""
        score = 100
        
        # Deduct points for errors
        score -= len(context.errors) * 10
        
        # Deduct points for missing data
        if not context.symbol:
            score -= 15
        if not context.analysis_data:
            score -= 20
        if not context.liquidation_clusters:
            score -= 25
        if not context.market_data:
            score -= 15
        
        # Add points for successful plugin execution
        plugin_results = context.processing_metadata.get("plugin_results", {})
        successful_plugins = sum(1 for result in plugin_results.values() if result.get("success", False))
        score += successful_plugins * 5
        
        return max(0, min(100, score))
    
    def _analyze_plugin_performance(self, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze plugin performance metrics"""
        plugin_results = context.processing_metadata.get("plugin_results", {})
        
        if not plugin_results:
            return {}
        
        durations = [result.get("duration_seconds", 0) for result in plugin_results.values()]
        successful = sum(1 for result in plugin_results.values() if result.get("success", False))
        
        return {
            "total_plugins": len(plugin_results),
            "successful_plugins": successful,
            "failed_plugins": len(plugin_results) - successful,
            "success_rate": round((successful / len(plugin_results)) * 100, 1) if plugin_results else 0,
            "average_duration": round(sum(durations) / len(durations), 2) if durations else 0,
            "total_plugin_time": round(sum(durations), 2),
            "fastest_plugin": min(durations) if durations else 0,
            "slowest_plugin": max(durations) if durations else 0
        }
    
    def _generate_insights(self, context: ProcessingContext) -> List[str]:
        """Generate processing insights and recommendations"""
        insights = []
        
        # Performance insights
        total_duration = self._calculate_total_duration(context)
        if total_duration > 60:
            insights.append(f"Processing took {total_duration}s - consider optimization")
        
        # Data insights
        if context.liquidation_clusters:
            cluster_count = len(context.liquidation_clusters)
            insights.append(f"Extracted {cluster_count} liquidation clusters")
            
            if cluster_count > 8:
                insights.append("High cluster count - strong liquidation activity detected")
        
        # Error insights
        if context.errors:
            insights.append(f"{len(context.errors)} errors encountered - review for improvements")
        
        # Quality insights
        quality_score = self._calculate_quality_score(context)
        if quality_score >= 90:
            insights.append("Excellent processing quality achieved")
        elif quality_score >= 70:
            insights.append("Good processing quality with room for improvement")
        else:
            insights.append("Processing quality below expectations - review required")
        
        return insights