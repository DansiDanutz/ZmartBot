
#!/usr/bin/env python3
"""
Enhanced Smart Context Optimizer with Bug Fixes
Production-ready version with comprehensive error handling and performance optimizations
"""

import os
import sys
import json
import time
import hashlib
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Import the original optimizer
try:
    from smart_context_optimizer import SmartContextOptimizer
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from smart_context_optimizer import SmartContextOptimizer

class EnhancedSmartContextOptimizer(SmartContextOptimizer):
    """
    Enhanced Smart Context Optimizer with comprehensive bug fixes and improvements
    """
    
    def __init__(self, project_root: str = "."):
        # Initialize parent class
        super().__init__(project_root)
        
        # Enhanced features
        self.lock = threading.Lock()
        self.file_locks = {}
        self.max_retries = 3
        self.retry_delay = 1
        self.error_count = 0
        self.last_error_time = None
        
        # Override parent's schedule setting - Reduce frequency to minimize compacting
        self.max_context_age_hours = 8  # Reduced frequency - update every 8 hours instead of 3
        self.performance_metrics = {
            "operation_times": [],
            "error_rates": [],
            "file_hashes": {}
        }
        
        # Setup enhanced logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced directories safely
        self.safe_create_directories()
        
    def safe_create_directories(self):
        """Safely create required directories with error handling"""
        try:
            self.claude_contexts_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Directories created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create directories: {e}")
            raise
    
    def get_file_lock(self, file_path: str) -> threading.Lock:
        """Get thread-safe lock for file operations"""
        if file_path not in self.file_locks:
            with self.lock:
                if file_path not in self.file_locks:
                    self.file_locks[file_path] = threading.Lock()
        return self.file_locks[file_path]
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file for integrity verification"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def verify_file_integrity(self, file_path: str) -> bool:
        """Verify file integrity using hash comparison"""
        if not os.path.exists(file_path):
            return False
        
        current_hash = self.calculate_file_hash(file_path)
        stored_hash = self.performance_metrics["file_hashes"].get(file_path)
        
        if stored_hash is None:
            self.performance_metrics["file_hashes"][file_path] = current_hash
            return True
        
        return current_hash == stored_hash
    
    def safe_operation(self, operation, *args, **kwargs):
        """Execute operation with retry logic and error handling"""
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                result = operation(*args, **kwargs)
                
                # Track successful operation
                duration = time.time() - start_time
                self.performance_metrics["operation_times"].append({
                    "operation": operation.__name__,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                })
                
                return result
                
            except Exception as e:
                self.error_count += 1
                self.last_error_time = datetime.now()
                
                # Track failed operation
                duration = time.time() - start_time
                self.performance_metrics["operation_times"].append({
                    "operation": operation.__name__,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": str(e)
                })
                
                self.logger.warning(f"Operation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Operation failed after {self.max_retries} attempts")
                    raise
    
    def safe_write_file(self, file_path: str, content: str) -> bool:
        """Safely write file with thread safety and integrity verification"""
        def write_operation():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # Update file hash after writing
            self.performance_metrics["file_hashes"][file_path] = self.calculate_file_hash(file_path)
            # Verify write was successful
            return os.path.exists(file_path) and os.path.getsize(file_path) > 0
        
        with self.get_file_lock(file_path):
            try:
                result = self.safe_operation(write_operation)
                return result if isinstance(result, bool) else False
            except Exception:
                return False
    
    def smart_truncate_content(self, content: str, max_size: int) -> str:
        """Smart truncation that preserves content integrity - prevents mid-sentence cuts."""
        if len(content) <= max_size:
            return content
        
        # Reserve space for completion message
        safe_size = max_size - 200
        
        # Find safe truncation points (in order of preference)
        safe_points = [
            '\n## ',        # Section headers
            '\n### ',       # Subsection headers  
            '\n\n',         # Paragraph breaks
            '. ',           # Sentence endings
            '\n',           # Line endings
        ]
        
        best_cutoff = safe_size
        
        # Look for the best safe truncation point
        for point in safe_points:
            # Find all occurrences of this safe point
            positions = []
            start = 0
            while True:
                pos = content.find(point, start)
                if pos == -1:
                    break
                if pos <= safe_size:
                    positions.append(pos + len(point))
                start = pos + 1
            
            # Use the latest safe point within limits
            if positions:
                best_cutoff = max(positions)
                break
        
        # Truncate at safe point
        truncated_content = content[:best_cutoff]
        
        # Add completion message with metadata
        completion_msg = f"""

## 🔄 Content Management

**Status**: Content optimized for performance
**Full Size**: {len(content):,} characters
**Optimized Size**: {len(truncated_content):,} characters  
**Completion**: {(len(truncated_content) / len(content) * 100):.1f}%

Full context available in:
- `.claude/contexts/` - Domain-specific contexts
- `.cursor/rules/` - Complete MDC files

**Generated**: {datetime.now().isoformat()}"""
        
        return truncated_content + completion_msg
    
    def smart_extract_content(self, content: str, max_length: int) -> str:
        """Smart content extraction that preserves content integrity."""
        if len(content) <= max_length:
            return content
        
        # Find safe truncation points (in order of preference)
        safe_points = [
            '\n## ',        # Section headers
            '\n### ',       # Subsection headers  
            '\n\n',         # Paragraph breaks
            '. ',           # Sentence endings
            '\n',           # Line endings
        ]
        
        best_cutoff = max_length
        
        # Look for the best safe truncation point
        for point in safe_points:
            # Find all occurrences of this safe point
            positions = []
            start = 0
            while True:
                pos = content.find(point, start)
                if pos == -1:
                    break
                if pos <= max_length:
                    positions.append(pos + len(point))
                start = pos + 1
            
            # Use the latest safe point within limits
            if positions:
                best_cutoff = max(positions)
                break
        
        # Extract content at safe point
        extracted_content = content[:best_cutoff]
        
        # Add indication if content was truncated
        if len(content) > max_length:
            extracted_content += "..."
        
        return extracted_content
    
    def extract_key_information(self, content: str) -> str:
        """Extract key information from content for very large files."""
        key_patterns = [
            r'Port:\s*(\d+)',
            r'Type:\s*(\w+)',
            r'Purpose:\s*([^\n]+)',
            r'API.*?:\s*([^\n]+)',
            r'Status:\s*(\w+)'
        ]
        
        import re
        key_info = []
        
        for pattern in key_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                key_info.extend(matches[:2])  # Max 2 matches per pattern
        
        return ' | '.join(key_info[:5]) if key_info else ""  # Max 5 key items
    
    def compress_content(self, content: str, target_size: int) -> str:
        """Compress content by extracting most relevant sentences."""
        sentences = content.replace('\n', ' ').split('. ')
        
        # Score sentences by relevance
        scored_sentences = []
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
                
            score = 0
            # Higher score for sentences with key terms
            key_terms = ['service', 'api', 'port', 'function', 'endpoint', 'critical', 'important']
            for term in key_terms:
                if term.lower() in sentence.lower():
                    score += 1
            
            # Prefer sentences with technical details
            if any(char.isdigit() for char in sentence):  # Contains numbers
                score += 0.5
            if ':' in sentence:  # Contains definitions/explanations
                score += 0.5
                
            scored_sentences.append((score, sentence.strip()))
        
        # Sort by score and build compressed content
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        compressed = ""
        for score, sentence in scored_sentences:
            if len(compressed) + len(sentence) + 2 <= target_size:
                compressed += sentence + ". "
            else:
                break
        
        return compressed.strip()
    
    def safe_scan_files(self) -> List[Dict[str, Any]]:
        """Safely scan MDC files with error recovery and integrity checks"""
        def scan_operation():
            mdc_files = []
            for mdc_file in self.cursor_rules_dir.glob("**/*.mdc"):
                if mdc_file.name.endswith('.backup'):
                    continue
                
                try:
                    if self.verify_file_integrity(str(mdc_file)):
                        with open(mdc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Calculate relevance score - use empty string for current_task since it's not passed to this method
                        relevance = self.calculate_file_relevance(mdc_file, "")
                        domain = self.get_domain_for_file(mdc_file.stem)
                        
                        mdc_files.append({
                            "file": str(mdc_file.relative_to(self.project_root)),
                            "name": mdc_file.stem,
                            "size": len(content),
                            "content": content,
                            "domain": domain,
                            "relevance": relevance,
                            "summary": self.generate_content_summary(content)
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to process {mdc_file}: {e}")
                    continue
            
            return mdc_files
        
        try:
            result = self.safe_operation(scan_operation)
            return result if isinstance(result, list) else []
        except Exception:
            return []
    
    def enhanced_update_claude_md(self, current_task: str = "", focus_domain: str = "core") -> bool:
        """Enhanced update of CLAUDE.md with comprehensive error handling"""
        try:
            # Generate optimized content
            claude_content = self.generate_optimized_claude_md(current_task, focus_domain)
            
            # Check size limit with smart truncation
            if len(claude_content) > self.max_claude_size:
                self.logger.warning(f"CLAUDE.md size ({len(claude_content)}) exceeds limit ({self.max_claude_size})")
                claude_content = self.smart_truncate_content(claude_content, self.max_claude_size)
            
            # Safely write main CLAUDE.md
            if not self.safe_write_file(str(self.claude_main_file), claude_content):
                return False
            
            # Generate domain-specific contexts
            mdc_files = self.safe_scan_files()
            for domain in self.domains.keys():
                domain_context = self.enhanced_generate_domain_context(domain, mdc_files)
                if domain_context:
                    domain_file = self.claude_contexts_dir / f"{domain}_context.md"
                    self.safe_write_file(str(domain_file), domain_context)
            
            # Update cache
            self.context_cache['last_full_update'] = datetime.now().isoformat()
            self.save_context_cache()
            
            self.logger.info(f"CLAUDE.md updated successfully ({len(claude_content)} chars)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating CLAUDE.md: {e}")
            return False
    
    def enhanced_generate_domain_context(self, domain: str, mdc_files: List[Dict[str, Any]]) -> str:
        """Enhanced domain context generation with smart content extraction."""
        domain_files = [f for f in mdc_files if f['domain'] == domain]
        
        if not domain_files:
            return ""
        
        context = f"# {domain.title()} Domain Context\\n\\n"
        
        for file_info in domain_files:
            context += f"## {file_info['name']}\\n"
            context += f"**File**: {file_info['file']}\\n"
            context += f"**Relevance**: {file_info['relevance']}\\n"
            context += f"**Size**: {file_info['size']} bytes\\n\\n"
            
            # Enhanced size-based content handling with better compression
            if file_info['size'] > 15000:  # 15KB - Very large files
                context += f"**Summary**: {file_info['summary']}\\n"
                # Add key metrics for large files
                key_info = self.extract_key_information(file_info['content'])
                if key_info:
                    context += f"**Key Info**: {key_info}\\n\\n"
                else:
                    context += "\\n"
            elif file_info['size'] > 5000:  # 5-15KB - Medium files
                context += f"**Summary**: {file_info['summary']}\\n"
                # Add compressed content for medium files
                compressed_content = self.compress_content(file_info['content'], 500)
                context += f"**Compressed**: {compressed_content}\\n\\n"
            else:
                # Small files get smart extraction
                smart_content = self.smart_extract_content(file_info['content'], 1500)
                context += f"**Content**: {smart_content}\\n\\n"
            
            context += "---\\n\\n"
        
        return context
    
    def cleanup_resources(self):
        """Clean up resources and perform maintenance"""
        # Clean up old performance data
        if len(self.performance_metrics["operation_times"]) > 1000:
            self.performance_metrics["operation_times"] = self.performance_metrics["operation_times"][-1000:]
        
        # Clean up expired file locks (simple cleanup based on count)
        expired_locks = []
        for lock_key in list(self.file_locks.keys()):
            # Simple cleanup - in production you'd track lock usage time
            if len(self.file_locks) > 100:  # Limit total locks
                expired_locks.append(lock_key)
        
        for lock_key in expired_locks:
            del self.file_locks[lock_key]
        
        if expired_locks:
            self.logger.info(f"Cleaned up {len(expired_locks)} file locks")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        successful_ops = [op for op in self.performance_metrics["operation_times"] if op.get("success", True)]
        failed_ops = [op for op in self.performance_metrics["operation_times"] if not op.get("success", True)]
        
        if successful_ops:
            durations = [op["duration"] for op in successful_ops]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
        else:
            avg_duration = max_duration = min_duration = 0
        
        return {
            "total_operations": len(self.performance_metrics["operation_times"]),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(self.performance_metrics["operation_times"]) if self.performance_metrics["operation_times"] else 0,
            "avg_operation_time": avg_duration,
            "max_operation_time": max_duration,
            "min_operation_time": min_duration,
            "error_count": self.error_count,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "active_file_locks": len(self.file_locks),
            "tracked_files": len(self.performance_metrics["file_hashes"])
        }

def main():
    """Main entry point for Enhanced Smart Context Optimizer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Smart Context Optimizer with Bug Fixes")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--update", action="store_true", help="Update CLAUDE.md with enhanced optimization")
    parser.add_argument("--task", default="", help="Current task for relevance scoring")
    parser.add_argument("--domain", default="core", help="Focus domain for context")
    parser.add_argument("--analyze", action="store_true", help="Analyze current context performance")
    parser.add_argument("--performance", action="store_true", help="Show performance report")
    parser.add_argument("--cleanup", action="store_true", help="Clean up resources")
    
    args = parser.parse_args()
    
    optimizer = EnhancedSmartContextOptimizer(args.project_root)
    
    if args.update:
        success = optimizer.enhanced_update_claude_md(args.task, args.domain)
        exit(0 if success else 1)
    
    elif args.analyze:
        mdc_files = optimizer.safe_scan_files()
        print(f"📊 Enhanced Context Analysis:")
        print(f"Total MDC files: {len(mdc_files)}")
        print(f"High relevance files: {len([f for f in mdc_files if f.get('relevance', 0) > 50])}")
        print(f"Total content size: {sum(f['size'] for f in mdc_files)} bytes")
        
        print(f"\n🎯 Top 10 Most Relevant Files:")
        for i, file_info in enumerate(mdc_files[:10], 1):
            print(f"{i:2d}. {file_info['name']} (Size: {file_info['size']}, Domain: {file_info['domain']})")
        
        exit(0)
    
    elif args.performance:
        report = optimizer.get_performance_report()
        print("📈 Performance Report:")
        print(json.dumps(report, indent=2))
        exit(0)
    
    elif args.cleanup:
        optimizer.cleanup_resources()
        print("🧹 Resources cleaned up successfully")
        exit(0)
    
    else:
        print("No action specified. Use --help for options.")
        exit(1)

if __name__ == "__main__":
    main()
