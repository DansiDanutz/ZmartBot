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
        self.max_context_age_hours = 8  # Optimize every 8 hours to reduce compacting frequency
        self.batch_update_interval = 120  # seconds - Reduced frequency to minimize system load
        
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
        """Generate an intelligent summary of content for large files."""
        if len(content) <= max_length:
            return content
        
        # Enhanced summary extraction with priority sections
        lines = content.split('\n')
        priority_content = []
        regular_content = []
        char_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Priority content (more important for summaries)
            if any(keyword in line.lower() for keyword in 
                   ['purpose', 'overview', 'critical', 'important', 'api', 'port', 'service']):
                priority_content.append(line)
            elif line.startswith('#') or line.startswith('**'):
                priority_content.append(line)
            else:
                regular_content.append(line)
        
        # Build summary prioritizing important content
        summary_lines = []
        
        # Add priority content first
        for line in priority_content:
            if char_count + len(line) + 1 <= max_length * 0.7:  # Reserve 30% for regular content
                summary_lines.append(line)
                char_count += len(line) + 1
            else:
                break
        
        # Add regular content to fill remaining space
        for line in regular_content:
            if char_count + len(line) + 1 <= max_length:
                summary_lines.append(line)
                char_count += len(line) + 1
            else:
                break
        
        summary = ' | '.join(summary_lines)  # Use separator for clarity
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
            
            # Enhanced size-based content handling with better compression
            if file_info['size'] > 15000:  # 15KB - Very large files
                context += f"**Summary**: {file_info['summary']}\n"
                # Add key metrics for large files
                key_info = self.extract_key_information(file_info['content'])
                if key_info:
                    context += f"**Key Info**: {key_info}\n\n"
                else:
                    context += "\n"
            elif file_info['size'] > 5000:  # 5-15KB - Medium files
                context += f"**Summary**: {file_info['summary']}\n"
                # Add compressed content for medium files
                compressed_content = self.compress_content(file_info['content'], 500)
                context += f"**Compressed**: {compressed_content}\n\n"
            else:
                # Small files get smart extraction
                smart_content = self.smart_extract_content(file_info['content'], 1500)
                context += f"**Content**: {smart_content}\n\n"
            
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
            # Use smart content extraction instead of crude truncation
            smart_content = self.smart_extract_content(file_info['content'], 1000)
            claude_content += f"{smart_content}\n\n"
        
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
                    # Use smart content extraction instead of crude truncation
                    smart_content = self.smart_extract_content(file_info['content'], 800)
                    claude_content += f"{smart_content}\n\n"
        
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
            
            # Check size limit with smart truncation
            if len(claude_content) > self.max_claude_size:
                self.logger.warning(f"CLAUDE.md size ({len(claude_content)}) exceeds limit ({self.max_claude_size})")
                # Smart truncation - find safe cutoff point
                claude_content = self.smart_truncate_content(claude_content, self.max_claude_size)
            
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
