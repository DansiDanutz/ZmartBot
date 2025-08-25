#!/usr/bin/env python3
"""
Smart Context Optimizer for Large-Scale MDC Management
Optimizes CLAUDE.md generation for performance with large datasets
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

class SmartContextOptimizer:
    """
    Optimizes context loading and CLAUDE.md generation for large-scale systems.
    Implements relevance scoring, smart batching, and domain separation.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cursor_rules_dir = self.project_root / ".cursor" / "rules"
        self.claude_dir = self.project_root / ".claude"
        self.claude_contexts_dir = self.claude_dir / "contexts"
        self.claude_main_file = self.project_root / "CLAUDE.md"
        
        # Performance settings
        self.max_claude_size = 40000  # 40KB limit
        self.max_context_age_hours = 24
        self.batch_update_interval = 30  # seconds
        
        # Context domains
        self.domains = {
            "core": ["rule_0_mandatory", "rules", "main"],
            "trading": ["MySymbols", "WhaleAlerts", "MessiAlerts", "LiveAlerts"],
            "monitoring": ["MonitoringMDC", "diagnostics", "ProcessReaper"],
            "orchestration": ["MasterOrchestrationAgent", "OrchestrationStart", "START_zmartbot"],
            "services": ["NewService", "PortManager", "ServiceDiscovery", "ServiceRegistry"],
            "data": ["MySymbolsDatabase", "21indicatorsDatabase", "market_data"],
            "backend": ["Backend", "API-Manager", "BackendDoctorPack"],
            "frontend": ["frontend", "ControlUI"]
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize directories
        self.claude_contexts_dir.mkdir(parents=True, exist_ok=True)
        
        # Load context cache
        self.context_cache = self.load_context_cache()
        self.relevance_scores = {}
        self.session_context = {
            "current_domain": "core",
            "active_files": [],
            "last_update": None,
            "pending_updates": []
        }
    
    def load_context_cache(self) -> Dict[str, Any]:
        """Load context cache for performance optimization."""
        cache_file = self.claude_dir / "context_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading context cache: {e}")
        
        return {
            "file_hashes": {},
            "relevance_scores": {},
            "last_full_update": None,
            "domain_contexts": {}
        }
    
    def save_context_cache(self):
        """Save context cache for performance optimization."""
        cache_file = self.claude_dir / "context_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.context_cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving context cache: {e}")
    
    def calculate_file_relevance(self, mdc_file: Path, current_task: str = "") -> int:
        """Calculate relevance score for an MDC file."""
        score = 0
        file_name = mdc_file.stem.lower()
        
        # Core files always have high relevance
        if any(core in file_name for core in self.domains["core"]):
            score += 100
        
        # Recent modifications increase relevance
        if mdc_file.exists():
            mod_time = datetime.fromtimestamp(mdc_file.stat().st_mtime)
            hours_old = (datetime.now() - mod_time).total_seconds() / 3600
            if hours_old < 1:
                score += 50
            elif hours_old < 6:
                score += 30
            elif hours_old < 24:
                score += 15
        
        # Task-related keywords increase relevance
        if current_task:
            task_keywords = current_task.lower().split()
            for keyword in task_keywords:
                if keyword in file_name:
                    score += 25
        
        # File size penalty for very large files
        if mdc_file.exists():
            file_size = mdc_file.stat().st_size
            if file_size > 30000:  # 30KB
                score -= 20
            elif file_size > 50000:  # 50KB
                score -= 40
        
        return max(0, score)
    
    def get_domain_for_file(self, file_name: str) -> str:
        """Determine which domain a file belongs to."""
        file_name_lower = file_name.lower()
        
        for domain, keywords in self.domains.items():
            if any(keyword.lower() in file_name_lower for keyword in keywords):
                return domain
        
        return "misc"
    
    def scan_mdc_files_with_relevance(self, current_task: str = "") -> List[Dict[str, Any]]:
        """Scan MDC files and calculate relevance scores."""
        mdc_files = []
        
        for mdc_file in self.cursor_rules_dir.glob("**/*.mdc"):
            if mdc_file.name.endswith('.backup'):
                continue
            
            try:
                relevance = self.calculate_file_relevance(mdc_file, current_task)
                domain = self.get_domain_for_file(mdc_file.stem)
                
                with open(mdc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse metadata
                metadata = {}
                content_body = content
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        metadata_lines = parts[1].strip().split('\n')
                        for line in metadata_lines:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
                        content_body = parts[2].strip()
                
                mdc_files.append({
                    "file": str(mdc_file.relative_to(self.project_root)),
                    "name": mdc_file.stem,
                    "domain": domain,
                    "relevance": relevance,
                    "size": len(content),
                    "metadata": metadata,
                    "content": content_body,
                    "summary": self.generate_content_summary(content_body)
                })
                
            except Exception as e:
                self.logger.error(f"Error processing {mdc_file}: {e}")
        
        # Sort by relevance score
        return sorted(mdc_files, key=lambda x: x['relevance'], reverse=True)
    
    def generate_content_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of content for large files."""
        if len(content) <= max_length:
            return content
        
        # Extract first paragraph or first few sentences
        lines = content.split('\n')
        summary_lines = []
        char_count = 0
        
        for line in lines:
            if line.strip():
                if char_count + len(line) > max_length:
                    break
                summary_lines.append(line.strip())
                char_count += len(line)
        
        summary = ' '.join(summary_lines)
        return summary[:max_length] + "..." if len(summary) > max_length else summary
    
    def generate_domain_context(self, domain: str, mdc_files: List[Dict[str, Any]]) -> str:
        """Generate context for a specific domain."""
        domain_files = [f for f in mdc_files if f['domain'] == domain]
        
        if not domain_files:
            return ""
        
        context = f"# {domain.title()} Domain Context\n\n"
        
        for file_info in domain_files:
            context += f"## {file_info['name']}\n"
            context += f"**File**: {file_info['file']}\n"
            context += f"**Relevance**: {file_info['relevance']}\n"
            context += f"**Size**: {file_info['size']} bytes\n\n"
            
            # Use summary for large files, full content for small ones
            if file_info['size'] > 10000:  # 10KB
                context += f"**Summary**: {file_info['summary']}\n\n"
            else:
                context += f"**Content**:\n```\n{file_info['content'][:2000]}\n```\n\n"
            
            context += "---\n\n"
        
        return context
    
    def generate_optimized_claude_md(self, current_task: str = "", focus_domain: str = "core") -> str:
        """Generate optimized CLAUDE.md with smart context loading."""
        
        # Scan files with relevance scoring
        mdc_files = self.scan_mdc_files_with_relevance(current_task)
        
        # Start with core context
        claude_content = f"""# CLAUDE.md - Smart Context (Auto-Generated)

## 🎯 System Overview

**Last Updated**: {datetime.now().isoformat()}
**Focus Domain**: {focus_domain.title()}
**Total MDC Files**: {len(mdc_files)}
**Current Task**: {current_task or "General Development"}

## 🚨 CRITICAL RULES (Always Active)

"""
        
        # Add core domain files (always included)
        core_files = [f for f in mdc_files if f['domain'] == 'core']
        for file_info in core_files:
            claude_content += f"### {file_info['name']}\n"
            claude_content += f"{file_info['content'][:1000]}\n\n"
        
        # Add focus domain if different from core
        if focus_domain != 'core':
            claude_content += f"## 🎯 {focus_domain.title()} Domain (Current Focus)\n\n"
            focus_files = [f for f in mdc_files if f['domain'] == focus_domain]
            for file_info in focus_files[:5]:  # Limit to top 5 most relevant
                claude_content += f"### {file_info['name']}\n"
                claude_content += f"**Relevance**: {file_info['relevance']}\n"
                if file_info['size'] > 5000:
                    claude_content += f"**Summary**: {file_info['summary']}\n\n"
                else:
                    claude_content += f"{file_info['content'][:800]}\n\n"
        
        # Add high-relevance files from other domains
        claude_content += "## 🔥 High-Relevance Context\n\n"
        high_relevance = [f for f in mdc_files if f['relevance'] > 50 and f['domain'] not in ['core', focus_domain]]
        for file_info in high_relevance[:3]:  # Top 3 high-relevance files
            claude_content += f"### {file_info['name']} ({file_info['domain']})\n"
            claude_content += f"**Relevance**: {file_info['relevance']}\n"
            claude_content += f"**Summary**: {file_info['summary']}\n\n"
        
        # Add navigation to other contexts
        claude_content += "## 📚 Available Contexts\n\n"
        for domain in self.domains.keys():
            domain_files = [f for f in mdc_files if f['domain'] == domain]
            if domain_files:
                claude_content += f"- **{domain.title()}**: {len(domain_files)} files (see .claude/contexts/{domain}_context.md)\n"
        
        # Add system status
        claude_content += f"""
## 📊 System Status

- **CLAUDE.md Size**: {len(claude_content)} characters
- **Size Limit**: {self.max_claude_size} characters
- **Performance**: {'✅ Optimal' if len(claude_content) < self.max_claude_size else '⚠️ Over Limit'}

## 🔄 Context Management

This file is automatically optimized for performance. Full context available in:
- `.claude/contexts/` - Domain-specific contexts
- `.cursor/rules/` - Full MDC files
- Context updates every {self.batch_update_interval} seconds

**Generated**: {datetime.now().isoformat()}
"""
        
        return claude_content
    
    def update_claude_md_smart(self, current_task: str = "", focus_domain: str = "core") -> bool:
        """Smart update of CLAUDE.md with performance optimization."""
        
        try:
            # Generate optimized content
            claude_content = self.generate_optimized_claude_md(current_task, focus_domain)
            
            # Check size limit
            if len(claude_content) > self.max_claude_size:
                self.logger.warning(f"CLAUDE.md size ({len(claude_content)}) exceeds limit ({self.max_claude_size})")
                # Truncate if necessary
                claude_content = claude_content[:self.max_claude_size] + "\n\n[Content truncated for performance]"
            
            # Write main CLAUDE.md
            with open(self.claude_main_file, 'w', encoding='utf-8') as f:
                f.write(claude_content)
            
            # Generate domain-specific contexts
            mdc_files = self.scan_mdc_files_with_relevance(current_task)
            for domain in self.domains.keys():
                domain_context = self.generate_domain_context(domain, mdc_files)
                if domain_context:
                    domain_file = self.claude_contexts_dir / f"{domain}_context.md"
                    with open(domain_file, 'w', encoding='utf-8') as f:
                        f.write(domain_context)
            
            # Update cache
            self.context_cache['last_full_update'] = datetime.now().isoformat()
            self.save_context_cache()
            
            self.logger.info(f"CLAUDE.md updated successfully ({len(claude_content)} chars)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating CLAUDE.md: {e}")
            return False
    
    def batch_update_context(self, pending_changes: List[str]) -> bool:
        """Batch update context for performance."""
        if not pending_changes:
            return True
        
        self.logger.info(f"Batch updating context for {len(pending_changes)} changes")
        
        # Determine focus domain based on changed files
        focus_domain = "core"
        for change in pending_changes:
            domain = self.get_domain_for_file(Path(change).stem)
            if domain != "misc":
                focus_domain = domain
                break
        
        return self.update_claude_md_smart(focus_domain=focus_domain)

def main():
    """Main entry point for Smart Context Optimizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Context Optimizer for Large-Scale MDC Management")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--update", action="store_true", help="Update CLAUDE.md with smart optimization")
    parser.add_argument("--task", default="", help="Current task for relevance scoring")
    parser.add_argument("--domain", default="core", help="Focus domain for context")
    parser.add_argument("--analyze", action="store_true", help="Analyze current context performance")
    
    args = parser.parse_args()
    
    optimizer = SmartContextOptimizer(args.project_root)
    
    if args.update:
        success = optimizer.update_claude_md_smart(args.task, args.domain)
        exit(0 if success else 1)
    
    elif args.analyze:
        mdc_files = optimizer.scan_mdc_files_with_relevance(args.task)
        print(f"📊 Context Analysis:")
        print(f"Total MDC files: {len(mdc_files)}")
        print(f"High relevance files: {len([f for f in mdc_files if f['relevance'] > 50])}")
        print(f"Total content size: {sum(f['size'] for f in mdc_files)} bytes")
        
        print(f"\n🎯 Top 10 Most Relevant Files:")
        for i, file_info in enumerate(mdc_files[:10], 1):
            print(f"{i:2d}. {file_info['name']} (Score: {file_info['relevance']}, Domain: {file_info['domain']})")
        
        exit(0)
    
    else:
        print("No action specified. Use --help for options.")
        exit(1)

if __name__ == "__main__":
    main()

