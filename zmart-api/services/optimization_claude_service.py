#!/usr/bin/env python3
"""
OptimizationClaude Service - Advanced Context Optimization Engine
Intelligent CLAUDE.md optimization with adaptive scheduling and performance monitoring
"""

import os
import sys
import time
import json
import hashlib
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationResult:
    """Result of an optimization operation"""
    success: bool
    original_size: int
    optimized_size: int
    size_difference: int
    optimizations: int
    processing_time: float
    performance_level: str
    recommendations: str
    priority: str
    urgency: int
    error: Optional[str] = None

@dataclass
class OptimizationAnalysis:
    """Analysis of optimization needs"""
    priority: str
    urgency: int
    reasons: List[str]
    size: int
    lines: int
    estimated_savings: int

class OptimizationClaude:
    """
    Advanced Context Optimization Service for CLAUDE.md
    
    Features:
    - Intelligent file analysis and prioritization
    - Adaptive scheduling based on file size and growth
    - Performance monitoring and metrics
    - System protection integration
    - Advanced optimization algorithms for large files
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.claude_md_path = Path(self.config['claude_md_path'])
        self.optimization_data_path = Path(self.config['optimization_data_path'])
        self.running = False
        self.scheduler_thread = None
        self.current_interval = self.config['default_interval']
        
        # Performance metrics
        self.metrics = {
            'total_optimizations': 0,
            'total_size_saved': 0,
            'average_processing_time': 0.0,
            'large_file_optimizations': 0,
            'skipped_optimizations': 0
        }
        
        logger.info("🔧 OptimizationClaude Service initialized")
        
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'claude_md_path': '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/CLAUDE.md',
            'optimization_data_path': '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/optimization_history.json',
            'default_interval': 2 * 60 * 60,  # 2 hours in seconds
            'min_interval': 30 * 60,  # 30 minutes minimum
            'max_interval': 6 * 60 * 60,  # 6 hours maximum
            'min_mdc_files': 50,
            'size_thresholds': {
                'optimal': 25000,
                'good': 30000,
                'fair': 35000,
                'large': 40000
            },
            'enable_aggressive_optimization': True,
            'enable_adaptive_scheduling': True,
            'enable_smart_skipping': True
        }
    
    def start_service(self) -> bool:
        """Start the optimization service"""
        try:
            logger.info("🚀 Starting OptimizationClaude Service...")
            
            # Verify system integrity
            if not self._verify_system_integrity():
                logger.error("❌ System integrity check failed")
                return False
            
            # Load optimization history
            self._load_optimization_history()
            
            # Start scheduler if adaptive scheduling is enabled
            if self.config['enable_adaptive_scheduling']:
                self.running = True
                self._start_adaptive_scheduler()
            
            logger.info("✅ OptimizationClaude Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start OptimizationClaude Service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the optimization service"""
        try:
            logger.info("🛑 Stopping OptimizationClaude Service...")
            
            self.running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            # Save optimization history
            self._save_optimization_history()
            
            logger.info("✅ OptimizationClaude Service stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop OptimizationClaude Service: {e}")
            return False
    
    def _verify_system_integrity(self) -> bool:
        """Verify system integrity before optimization"""
        try:
            # Check CLAUDE.md exists
            if not self.claude_md_path.exists():
                logger.error("❌ CLAUDE.md file not found")
                return False
            
            # Check MDC files count (simplified check)
            mdc_dir = Path('.cursor/rules')
            if mdc_dir.exists():
                mdc_count = len(list(mdc_dir.glob('*.mdc')))
                if mdc_count < self.config['min_mdc_files']:
                    logger.error(f"❌ Insufficient MDC files: {mdc_count} < {self.config['min_mdc_files']}")
                    return False
                logger.info(f"✅ System integrity verified: {mdc_count} MDC files")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System integrity verification failed: {e}")
            return False
    
    def analyze_optimization_needs(self, content: str) -> OptimizationAnalysis:
        """Analyze file and determine optimization needs"""
        size = len(content)
        lines = content.count('\n')
        
        priority = 'LOW'
        urgency = 0
        reasons = []
        
        # Size-based priority
        if size > self.config['size_thresholds']['large']:
            priority = 'CRITICAL'
            urgency += 10
            reasons.append(f'File exceeds {self.config["size_thresholds"]["large"]} chars')
        elif size > self.config['size_thresholds']['fair']:
            priority = 'HIGH'
            urgency += 7
            reasons.append('File approaching size limit')
        elif size > self.config['size_thresholds']['good']:
            priority = 'MEDIUM'
            urgency += 4
            reasons.append('File size optimization beneficial')
        
        # Content-based analysis
        excessive_whitespace = len(re.findall(r'\n{4,}', content))
        if excessive_whitespace > 5:
            urgency += 3
            reasons.append('Excessive whitespace detected')
        
        redundant_patterns = len(re.findall(r'\(see [^)]+\)', content))
        if redundant_patterns > 10:
            urgency += 2
            reasons.append('Redundant pattern references')
        
        # Check for outdated timestamps
        outdated_timestamps = bool(re.search(r'2025-08-2[0-5]', content))
        if outdated_timestamps:
            urgency += 1
            reasons.append('Outdated timestamps')
        
        estimated_savings = min(size * 0.1, 2000)  # Estimate 10% savings, max 2k chars
        
        return OptimizationAnalysis(
            priority=priority,
            urgency=urgency,
            reasons=reasons,
            size=size,
            lines=lines,
            estimated_savings=int(estimated_savings)
        )
    
    def optimize_content(self, content: str) -> OptimizationResult:
        """Optimize CLAUDE.md content with advanced algorithms"""
        start_time = time.time()
        original_size = len(content)
        optimized_content = content
        optimizations = 0
        
        logger.info(f"🔧 Starting optimization - File size: {original_size} chars")
        
        # 1. Enhanced Whitespace Optimization
        before = len(optimized_content)
        optimized_content = re.sub(r'\n{4,}', '\n\n\n', optimized_content)  # Max 3 newlines
        optimized_content = re.sub(r'[ \t]+$', '', optimized_content, flags=re.MULTILINE)  # Trailing spaces
        optimized_content = re.sub(r'^[ \t]+(?=\n)', '', optimized_content, flags=re.MULTILINE)  # Leading spaces on empty lines
        optimized_content = re.sub(r'[ \t]{2,}', ' ', optimized_content)  # Multiple spaces
        if len(optimized_content) < before:
            optimizations += 1
            logger.info(f"  ✓ Whitespace optimized: {before - len(optimized_content)} chars saved")
        
        # 2. Smart Section Header Optimization
        before = len(optimized_content)
        optimized_content = re.sub(
            r'^## (🔥|📚|📊|🎯|🚨|🔄) ([^\n]+)',
            lambda m: f"## {m.group(1)} {m.group(2).strip()}",
            optimized_content,
            flags=re.MULTILINE
        )
        if len(optimized_content) < before:
            optimizations += 1
            logger.info(f"  ✓ Headers optimized: {before - len(optimized_content)} chars saved")
        
        # 3. Advanced Pattern Consolidation
        before = len(optimized_content)
        # Remove redundant context file references
        optimized_content = re.sub(r'(\*\*[^*]+\*\*:\s*\d+\s*files)\s+\(see[^)]+\)\s*\n', r'\1\n', optimized_content)
        # Consolidate repeated context references
        optimized_content = re.sub(r'(- \*\*[^*]+\*\*:)\s+([^\n]+)\s+\(see[^)]+\)', r'\1 \2', optimized_content)
        if len(optimized_content) < before:
            optimizations += 1
            logger.info(f"  ✓ Patterns consolidated: {before - len(optimized_content)} chars saved")
        
        # 4. Dynamic Size-Based Optimization
        current_size = len(optimized_content)
        if current_size > self.config['size_thresholds']['fair'] and self.config['enable_aggressive_optimization']:
            logger.info(f"⚠️  Large file detected ({current_size} chars) - Applying aggressive optimization")
            
            before = len(optimized_content)
            
            # Compress repeated sections
            optimized_content = re.sub(
                r'(\n- \*\*[^*]+\*\*: \d+ files)\n(\n- \*\*[^*]+\*\*: \d+ files)+',
                lambda m: self._compress_repeated_sections(m.group(0)),
                optimized_content
            )
            
            # Optimize context list display
            optimized_content = re.sub(
                r'## 📚 Available Contexts\n\n((?:- \*\*[^:]+\*\*:[^\n]+\n)+)',
                lambda m: self._optimize_context_list(m.group(0), m.group(1)),
                optimized_content
            )
            
            if len(optimized_content) < before:
                optimizations += 1
                logger.info(f"  ✓ Aggressive optimization: {before - len(optimized_content)} chars saved")
        
        # 5. Smart Timestamp Updates
        now = datetime.now().isoformat()
        optimized_content = re.sub(r'\*\*Generated\*\*: [^\n]+', f'**Generated**: {now}', optimized_content)
        optimized_content = re.sub(r'\*\*Last Updated\*\*: [^\n]+', f'**Last Updated**: {now}', optimized_content)
        optimizations += 2
        
        # 6. Dynamic Size and Performance Calculation
        final_size = len(optimized_content)
        optimized_content = re.sub(
            r'- \*\*CLAUDE\.md Size\*\*: \d+ characters',
            f'- **CLAUDE.md Size**: {final_size} characters',
            optimized_content
        )
        
        # 7. Intelligent Performance Status
        performance_level, recommendation = self._calculate_performance_status(final_size)
        
        optimized_content = re.sub(
            r'- \*\*Performance\*\*: [^\n]+',
            f'- **Performance**: {performance_level}{recommendation}',
            optimized_content
        )
        optimizations += 1
        
        # 8. Context Load Optimization
        if final_size > self.config['size_thresholds']['good']:
            context_note = '\n**Note**: Context auto-optimized for performance. Full details available in MDC files.\n'
            if 'Context auto-optimized' not in optimized_content:
                optimized_content = re.sub(
                    r'## 🔄 Context Management\n',
                    f'## 🔄 Context Management\n{context_note}',
                    optimized_content
                )
                optimizations += 1
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Optimization complete - Processing time: {processing_time:.2f}s")
        logger.info(f"📊 Results: {original_size} → {final_size} chars ({original_size - final_size} saved)")
        
        # Analyze optimization needs for priority
        analysis = self.analyze_optimization_needs(optimized_content)
        
        return OptimizationResult(
            success=True,
            original_size=original_size,
            optimized_size=final_size,
            size_difference=original_size - final_size,
            optimizations=optimizations,
            processing_time=processing_time,
            performance_level=performance_level,
            recommendations=recommendation.strip() or 'File size optimal',
            priority=analysis.priority,
            urgency=analysis.urgency
        )
    
    def _compress_repeated_sections(self, match_text: str) -> str:
        """Compress repeated sections in context lists"""
        lines = [line for line in match_text.split('\n') if line.strip()]
        if len(lines) > 3:
            first = lines[0]
            last = lines[-1]
            return f"\n{first}\n... ({len(lines) - 2} more contexts)\n{last}"
        return match_text
    
    def _optimize_context_list(self, full_match: str, contexts: str) -> str:
        """Optimize context list display for large files"""
        context_lines = [line for line in contexts.split('\n') if line.strip()]
        if len(context_lines) > 8:
            summary = context_lines[:5]
            summary.append(f"- ... and {len(context_lines) - 5} more contexts available")
            return f"## 📚 Available Contexts\n\n" + "\n".join(summary) + "\n"
        return full_match
    
    def _calculate_performance_status(self, file_size: int) -> Tuple[str, str]:
        """Calculate performance status and recommendations"""
        thresholds = self.config['size_thresholds']
        
        if file_size < thresholds['optimal']:
            return '✅ Optimal', ''
        elif file_size < thresholds['good']:
            return '✅ Good', ''
        elif file_size < thresholds['fair']:
            return '⚠️ Fair', ' (Consider context reduction)'
        elif file_size < thresholds['large']:
            return '⚠️ Large', ' (Context optimization needed)'
        else:
            return '❌ Critical', ' (Immediate optimization required)'
    
    def calculate_adaptive_interval(self, file_size: int, growth_rate: float = 0.0) -> int:
        """Calculate adaptive optimization interval"""
        base_interval = self.config['default_interval']
        
        # Adjust based on file size
        if file_size > self.config['size_thresholds']['fair']:
            base_interval = int(base_interval * 0.5)  # 1 hour for large files
        elif file_size > self.config['size_thresholds']['good']:
            base_interval = int(base_interval * 0.75)  # 1.5 hours for medium files
        elif file_size < self.config['size_thresholds']['optimal']:
            base_interval = int(base_interval * 2)  # 4 hours for small files
        
        # Adjust based on growth rate
        if growth_rate > 0.2:  # File growing fast (>20%)
            base_interval = int(base_interval * 0.7)  # More frequent
        elif growth_rate < 0.05:  # File stable (<5%)
            base_interval = int(base_interval * 1.3)  # Less frequent
        
        # Ensure bounds
        return max(self.config['min_interval'], min(self.config['max_interval'], base_interval))
    
    async def perform_optimization(self, is_scheduled: bool = False) -> OptimizationResult:
        """Perform context optimization"""
        try:
            # Verify system integrity
            if not self._verify_system_integrity():
                return OptimizationResult(
                    success=False,
                    original_size=0,
                    optimized_size=0,
                    size_difference=0,
                    optimizations=0,
                    processing_time=0.0,
                    performance_level='Unknown',
                    recommendations='',
                    priority='CRITICAL',
                    urgency=10,
                    error='System integrity check failed'
                )
            
            # Read CLAUDE.md file
            content = self.claude_md_path.read_text(encoding='utf-8')
            if not content:
                return OptimizationResult(
                    success=False,
                    original_size=0,
                    optimized_size=0,
                    size_difference=0,
                    optimizations=0,
                    processing_time=0.0,
                    performance_level='Unknown',
                    recommendations='',
                    priority='CRITICAL',
                    urgency=10,
                    error='CLAUDE.md file is empty or unreadable'
                )
            
            # Analyze optimization needs
            analysis = self.analyze_optimization_needs(content)
            logger.info(f"📊 Analysis: Priority={analysis.priority}, Urgency={analysis.urgency}")
            logger.info(f"📋 Reasons: {', '.join(analysis.reasons)}")
            logger.info(f"💾 Estimated savings: {analysis.estimated_savings} chars")
            
            # Skip optimization if low priority and scheduled
            if (is_scheduled and 
                self.config['enable_smart_skipping'] and 
                analysis.priority == 'LOW' and 
                analysis.urgency < 2):
                
                logger.info('⏩ Skipping optimization - Low priority, no urgent needs')
                self.metrics['skipped_optimizations'] += 1
                return OptimizationResult(
                    success=True,
                    original_size=analysis.size,
                    optimized_size=analysis.size,
                    size_difference=0,
                    optimizations=0,
                    processing_time=0.0,
                    performance_level='Skipped',
                    recommendations='Low priority optimization skipped',
                    priority=analysis.priority,
                    urgency=analysis.urgency,
                    error='Optimization skipped due to low priority'
                )
            
            # Perform optimization
            result = self.optimize_content(content)
            
            # Write optimized content back to file
            if result.success and result.size_difference > 0:
                self.claude_md_path.write_text(result.optimized_content, encoding='utf-8')
                logger.info(f"✅ Optimized content written to {self.claude_md_path}")
            
            # Update metrics
            self.metrics['total_optimizations'] += 1
            self.metrics['total_size_saved'] += result.size_difference
            self.metrics['average_processing_time'] = (
                (self.metrics['average_processing_time'] * (self.metrics['total_optimizations'] - 1) + result.processing_time) /
                self.metrics['total_optimizations']
            )
            
            if result.original_size > self.config['size_thresholds']['fair']:
                self.metrics['large_file_optimizations'] += 1
            
            # Update adaptive interval
            if self.config['enable_adaptive_scheduling']:
                history = self._load_optimization_history()
                growth_rate = self._calculate_growth_rate(history, result.original_size)
                new_interval = self.calculate_adaptive_interval(result.optimized_size, growth_rate)
                
                if new_interval != self.current_interval:
                    logger.info(f"🔄 Adaptive scheduling: Interval changed to {new_interval//60} minutes")
                    self.current_interval = new_interval
            
            # Save to history
            self._save_optimization_record(result, is_scheduled)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            return OptimizationResult(
                success=False,
                original_size=0,
                optimized_size=0,
                size_difference=0,
                optimizations=0,
                processing_time=0.0,
                performance_level='Error',
                recommendations='',
                priority='CRITICAL',
                urgency=10,
                error=str(e)
            )
    
    def _start_adaptive_scheduler(self):
        """Start the adaptive scheduler thread"""
        def scheduler_worker():
            logger.info(f"🕒 Adaptive scheduler started with {self.current_interval//60} minute intervals")
            
            while self.running:
                try:
                    time.sleep(self.current_interval)
                    
                    if not self.running:
                        break
                    
                    logger.info("🔧 Running scheduled optimization...")
                    
                    # Run optimization in async context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.perform_optimization(is_scheduled=True))
                    loop.close()
                    
                    if result.success:
                        logger.info("✅ Scheduled optimization completed successfully")
                    else:
                        logger.warning(f"⚠️ Scheduled optimization failed: {result.error}")
                        
                except Exception as e:
                    logger.error(f"❌ Scheduler error: {e}")
        
        self.scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        self.scheduler_thread.start()
    
    def _load_optimization_history(self) -> List[Dict]:
        """Load optimization history from file"""
        try:
            if self.optimization_data_path.exists():
                with open(self.optimization_data_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load optimization history: {e}")
        
        return []
    
    def _save_optimization_history(self):
        """Save optimization history to file"""
        try:
            # Create directory if it doesn't exist
            self.optimization_data_path.parent.mkdir(parents=True, exist_ok=True)
            
            history = self._load_optimization_history()
            
            # Add metrics to history
            history_data = {
                'metrics': self.metrics,
                'last_updated': datetime.now().isoformat(),
                'current_interval': self.current_interval,
                'history': history
            }
            
            with open(self.optimization_data_path, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save optimization history: {e}")
    
    def _save_optimization_record(self, result: OptimizationResult, is_scheduled: bool):
        """Save individual optimization record"""
        try:
            history = self._load_optimization_history()
            
            record = {
                'timestamp': datetime.now().isoformat(),
                'scheduled': is_scheduled,
                **asdict(result)
            }
            
            history.append(record)
            
            # Keep only last 100 records
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            self.optimization_data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.optimization_data_path, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save optimization record: {e}")
    
    def _calculate_growth_rate(self, history: List[Dict], current_size: int) -> float:
        """Calculate file growth rate from history"""
        if not history:
            return 0.0
        
        try:
            # Get last optimization size
            last_record = history[-1]
            last_size = last_record.get('optimized_size', current_size)
            
            if last_size > 0:
                growth_rate = (current_size - last_size) / last_size
                return max(0.0, growth_rate)
        except (KeyError, IndexError, ZeroDivisionError):
            pass
        
        return 0.0
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            'service_running': self.running,
            'current_interval_minutes': self.current_interval // 60,
            'metrics': self.metrics,
            'claude_md_exists': self.claude_md_path.exists(),
            'claude_md_size': self.claude_md_path.stat().st_size if self.claude_md_path.exists() else 0,
            'config': self.config,
            'last_check': datetime.now().isoformat()
        }

# Main service instance
optimization_claude_service = None

def start_optimization_claude_service(config: Optional[Dict] = None) -> bool:
    """Start the OptimizationClaude service"""
    global optimization_claude_service
    
    try:
        optimization_claude_service = OptimizationClaude(config)
        return optimization_claude_service.start_service()
    except Exception as e:
        logger.error(f"Failed to start OptimizationClaude service: {e}")
        return False

def stop_optimization_claude_service() -> bool:
    """Stop the OptimizationClaude service"""
    global optimization_claude_service
    
    try:
        if optimization_claude_service:
            return optimization_claude_service.stop_service()
        return True
    except Exception as e:
        logger.error(f"Failed to stop OptimizationClaude service: {e}")
        return False

def get_optimization_claude_status() -> Dict:
    """Get OptimizationClaude service status"""
    global optimization_claude_service
    
    if optimization_claude_service:
        return optimization_claude_service.get_status()
    
    return {
        'service_running': False,
        'error': 'Service not initialized'
    }

if __name__ == "__main__":
    # Test the service
    print("🔧 Testing OptimizationClaude Service...")
    
    if start_optimization_claude_service():
        print("✅ Service started successfully")
        
        # Run a test optimization
        import asyncio
        
        async def test_optimization():
            result = await optimization_claude_service.perform_optimization(is_scheduled=False)
            print(f"📊 Test optimization result: {result.success}")
            print(f"💾 Size: {result.original_size} → {result.optimized_size} ({result.size_difference} saved)")
            return result
        
        asyncio.run(test_optimization())
        
        # Get status
        status = get_optimization_claude_status()
        print(f"📈 Service status: {json.dumps(status, indent=2, default=str)}")
        
        # Stop service
        stop_optimization_claude_service()
        print("✅ Service stopped successfully")
    else:
        print("❌ Failed to start service")