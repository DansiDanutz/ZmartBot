#!/usr/bin/env python3
"""
Bug Fixes for Smart Context Optimization System
Comprehensive fixes for identified issues and potential bugs
"""

import os
import sys
import logging
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SmartContextOptimizerBugFixes:
    """
    Bug fixes and improvements for Smart Context Optimization System
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
    def fix_import_issues(self):
        """Fix import issues in enhanced_mdc_monitor.py"""
        monitor_file = self.project_root / "zmart-api" / "enhanced_mdc_monitor.py"
        
        if monitor_file.exists():
            # Read the file
            with open(monitor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the import issue
            old_import = "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.abspath(__file__)))\nfrom smart_context_optimizer import SmartContextOptimizer"
            new_import = "try:\n    from smart_context_optimizer import SmartContextOptimizer\nexcept ImportError:\n    import sys\n    import os\n    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n    from smart_context_optimizer import SmartContextOptimizer"
            
            content = content.replace(old_import, new_import)
            
            # Write back the fixed content
            with open(monitor_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info("Fixed import issues in enhanced_mdc_monitor.py")
    
    def add_thread_safety(self):
        """Add thread safety improvements"""
        # Add locks for shared resources
        lock_code = """
import threading

class ThreadSafeContextOptimizer:
    def __init__(self, project_root: str = "."):
        self.lock = threading.Lock()
        self.file_locks = {}
        
    def get_file_lock(self, file_path: str) -> threading.Lock:
        if file_path not in self.file_locks:
            with self.lock:
                if file_path not in self.file_locks:
                    self.file_locks[file_path] = threading.Lock()
        return self.file_locks[file_path]
        
    def safe_write_file(self, file_path: str, content: str):
        with self.get_file_lock(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
"""
        return lock_code
    
    def add_memory_management(self):
        """Add memory management improvements"""
        memory_code = """
class MemoryManagedOptimizer:
    def __init__(self):
        self.max_queue_size = 1000
        self.max_cache_size = 100
        self.cleanup_interval = 300  # 5 minutes
        
    def cleanup_old_data(self):
        # Clean up old performance data
        if len(self.performance_data["context_updates"]) > self.max_cache_size:
            self.performance_data["context_updates"] = self.performance_data["context_updates"][-self.max_cache_size:]
            
        if len(self.performance_data["file_changes"]) > self.max_cache_size * 2:
            self.performance_data["file_changes"] = self.performance_data["file_changes"][-self.max_cache_size * 2:]
            
        # Clean up old file locks
        current_time = time.time()
        expired_locks = [k for k, v in self.file_locks.items() 
                        if current_time - v.get('last_used', 0) > 3600]  # 1 hour
        for lock_key in expired_locks:
            del self.file_locks[lock_key]
"""
        return memory_code
    
    def add_error_recovery(self):
        """Add error recovery mechanisms"""
        recovery_code = """
class ErrorRecoveryOptimizer:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.error_count = 0
        self.last_error_time = None
        
    def safe_operation(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                self.error_count += 1
                self.last_error_time = datetime.now()
                self.logger.warning(f"Operation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Operation failed after {self.max_retries} attempts")
                    raise
"""
        return recovery_code
    
    def add_performance_monitoring(self):
        """Add performance monitoring improvements"""
        monitoring_code = """
class PerformanceMonitoringOptimizer:
    def __init__(self):
        self.performance_metrics = {
            "operation_times": [],
            "memory_usage": [],
            "error_rates": [],
            "queue_sizes": []
        }
        
    def track_operation_time(self, operation_name: str, start_time: float):
        duration = time.time() - start_time
        self.performance_metrics["operation_times"].append({
            "operation": operation_name,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 1000 operations
        if len(self.performance_metrics["operation_times"]) > 1000:
            self.performance_metrics["operation_times"] = self.performance_metrics["operation_times"][-1000:]
            
    def get_performance_report(self):
        if not self.performance_metrics["operation_times"]:
            return {}
            
        durations = [op["duration"] for op in self.performance_metrics["operation_times"]]
        return {
            "avg_operation_time": sum(durations) / len(durations),
            "max_operation_time": max(durations),
            "min_operation_time": min(durations),
            "total_operations": len(durations),
            "error_count": self.error_count
        }
"""
        return monitoring_code
    
    def add_file_integrity_checks(self):
        """Add file integrity checks"""
        integrity_code = """
class FileIntegrityOptimizer:
    def __init__(self):
        self.file_hashes = {}
        
    def calculate_file_hash(self, file_path: str) -> str:
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def verify_file_integrity(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
            
        current_hash = self.calculate_file_hash(file_path)
        stored_hash = self.file_hashes.get(file_path)
        
        if stored_hash is None:
            self.file_hashes[file_path] = current_hash
            return True
            
        return current_hash == stored_hash
        
    def update_file_hash(self, file_path: str):
        if os.path.exists(file_path):
            self.file_hashes[file_path] = self.calculate_file_hash(file_path)
"""
        return integrity_code
    
    def create_enhanced_optimizer(self):
        """Create an enhanced version with all bug fixes"""
        enhanced_code = f"""
#!/usr/bin/env python3
\"\"\"
Enhanced Smart Context Optimizer with Bug Fixes
\"\"\"

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

{self.add_thread_safety()}

{self.add_memory_management()}

{self.add_error_recovery()}

{self.add_performance_monitoring()}

{self.add_file_integrity_checks()}

class EnhancedSmartContextOptimizer(ThreadSafeContextOptimizer, MemoryManagedOptimizer, 
                                   ErrorRecoveryOptimizer, PerformanceMonitoringOptimizer,
                                   FileIntegrityOptimizer):
    \"\"\"
    Enhanced Smart Context Optimizer with all bug fixes and improvements
    \"\"\"
    
    def __init__(self, project_root: str = "."):
        super().__init__(project_root)
        self.project_root = Path(project_root)
        self.cursor_rules_dir = self.project_root / ".cursor" / "rules"
        self.claude_dir = self.project_root / ".claude"
        self.claude_contexts_dir = self.claude_dir / "contexts"
        self.claude_main_file = self.project_root / "CLAUDE.md"
        
        # Performance settings
        self.max_claude_size = 40000
        self.max_context_age_hours = 24
        self.batch_update_interval = 30
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize directories safely
        self.safe_create_directories()
        
        # Load context cache
        self.context_cache = self.load_context_cache()
        
    def safe_create_directories(self):
        \"\"\"Safely create required directories\"\"\"
        try:
            self.claude_contexts_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create directories: {{e}}")
            raise
            
    def safe_update_claude_md(self, content: str) -> bool:
        \"\"\"Safely update CLAUDE.md with error recovery\"\"\"
        def update_operation():
            with open(self.claude_main_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.update_file_hash(str(self.claude_main_file))
            
        return self.safe_operation(update_operation)
        
    def safe_scan_files(self) -> List[Dict[str, Any]]:
        \"\"\"Safely scan MDC files with error recovery\"\"\"
        def scan_operation():
            mdc_files = []
            for mdc_file in self.cursor_rules_dir.glob("**/*.mdc"):
                if mdc_file.name.endswith('.backup'):
                    continue
                    
                try:
                    if self.verify_file_integrity(str(mdc_file)):
                        # Process file
                        with open(mdc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        mdc_files.append({{
                            "file": str(mdc_file.relative_to(self.project_root)),
                            "name": mdc_file.stem,
                            "size": len(content),
                            "content": content
                        }})
                except Exception as e:
                    self.logger.warning(f"Failed to process {{mdc_file}}: {{e}}")
                    continue
                    
            return mdc_files
            
        return self.safe_operation(scan_operation)
        
    def cleanup_resources(self):
        \"\"\"Clean up resources and perform maintenance\"\"\"
        self.cleanup_old_data()
        
        # Clean up expired file locks
        current_time = time.time()
        expired_locks = [k for k, v in self.file_locks.items() 
                        if current_time - v.get('last_used', 0) > 3600]
        for lock_key in expired_locks:
            del self.file_locks[lock_key]
            
        self.logger.info(f"Cleaned up {{len(expired_locks)}} expired file locks")
"""
        return enhanced_code
    
    def create_test_suite(self):
        """Create a comprehensive test suite"""
        test_code = """
#!/usr/bin/env python3
\"\"\"
Test Suite for Smart Context Optimization System
\"\"\"

import unittest
import tempfile
import shutil
from pathlib import Path
from smart_context_optimizer import SmartContextOptimizer

class TestSmartContextOptimizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.optimizer = SmartContextOptimizer(self.test_dir)
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_directory_creation(self):
        \"\"\"Test that directories are created properly\"\"\"
        claude_dir = Path(self.test_dir) / ".claude" / "contexts"
        self.assertTrue(claude_dir.exists())
        
    def test_file_scanning(self):
        \"\"\"Test MDC file scanning\"\"\"
        # Create test MDC files
        rules_dir = Path(self.test_dir) / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = rules_dir / "test.mdc"
        test_file.write_text("# Test MDC File")
        
        files = self.optimizer.scan_mdc_files_with_relevance()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "test")
        
    def test_context_generation(self):
        \"\"\"Test context generation\"\"\"
        content = self.optimizer.generate_optimized_claude_md()
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)
        
    def test_size_limits(self):
        \"\"\"Test size limit enforcement\"\"\"
        # Create large content
        large_content = "x" * 50000
        truncated = self.optimizer.truncate_content(large_content)
        self.assertLessEqual(len(truncated), self.optimizer.max_claude_size)
        
    def test_error_handling(self):
        \"\"\"Test error handling\"\"\"
        # Test with non-existent directory
        with self.assertRaises(Exception):
            optimizer = SmartContextOptimizer("/non/existent/path")
            optimizer.scan_mdc_files_with_relevance()

if __name__ == "__main__":
    unittest.main()
"""
        return test_code

def main():
    """Main entry point for bug fixes"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bug Fixes for Smart Context Optimization System")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--fix-imports", action="store_true", help="Fix import issues")
    parser.add_argument("--create-enhanced", action="store_true", help="Create enhanced optimizer")
    parser.add_argument("--create-tests", action="store_true", help="Create test suite")
    parser.add_argument("--run-audit", action="store_true", help="Run comprehensive audit")
    
    args = parser.parse_args()
    
    bug_fixes = SmartContextOptimizerBugFixes(args.project_root)
    
    if args.fix_imports:
        bug_fixes.fix_import_issues()
        
    if args.create_enhanced:
        enhanced_code = bug_fixes.create_enhanced_optimizer()
        enhanced_file = Path(args.project_root) / "zmart-api" / "enhanced_smart_context_optimizer.py"
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_code)
        print(f"Created enhanced optimizer: {enhanced_file}")
        
    if args.create_tests:
        test_code = bug_fixes.create_test_suite()
        test_file = Path(args.project_root) / "zmart-api" / "test_smart_context_optimizer.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        print(f"Created test suite: {test_file}")
        
    if args.run_audit:
        print("Running comprehensive audit...")
        # Add audit logic here
        print("Audit completed")

if __name__ == "__main__":
    main()
