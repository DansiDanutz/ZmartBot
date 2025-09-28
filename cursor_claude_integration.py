#!/usr/bin/env python3
"""
Cursor-Claude Integration Helper
Provides intelligent context and project understanding for Claude in Cursor
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CursorClaudeIntegration:
    """Integration helper for Claude running inside Cursor"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.context_file = os.path.join(self.project_root, '.cursor_claude_context.json')
        self.session_file = os.path.join(self.project_root, '.cursor_claude_session.json')
        
    def get_project_context(self) -> Dict[str, Any]:
        """Get comprehensive project context for Claude"""
        try:
            context = {
                'project_info': self._get_project_info(),
                'current_files': self._get_current_files(),
                'recent_changes': self._get_recent_changes(),
                'code_patterns': self._get_code_patterns(),
                'dependencies': self._get_dependencies(),
                'architecture': self._get_architecture_info(),
                'optimization_hints': self._get_optimization_hints(),
                'claude_instructions': self._get_claude_instructions()
            }
            
            # Save context for persistence
            self._save_context(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting project context: {e}")
            return {}
            
    def _get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        return {
            'name': os.path.basename(self.project_root),
            'type': self._detect_project_type(),
            'technologies': self._detect_technologies(),
            'size': self._calculate_project_size(),
            'last_modified': self._get_last_modified(),
            'git_info': self._get_git_info()
        }
        
    def _detect_project_type(self) -> str:
        """Detect project type"""
        # Check for ZmartBot specific indicators
        if 'zmart' in self.project_root.lower() or 'zmartbot' in self.project_root.lower():
            return 'zmartbot_trading_system'
            
        # Check for common project files
        if os.path.exists(os.path.join(self.project_root, 'package.json')):
            return 'nodejs_project'
        elif os.path.exists(os.path.join(self.project_root, 'requirements.txt')):
            return 'python_project'
        elif os.path.exists(os.path.join(self.project_root, 'Dockerfile')):
            return 'docker_project'
        else:
            return 'general_project'
            
    def _detect_technologies(self) -> List[str]:
        """Detect technologies used in the project"""
        technologies = []
        
        # Check package.json for Node.js technologies
        package_json = os.path.join(self.project_root, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        deps = data['dependencies']
                        if 'react' in deps:
                            technologies.append('React')
                        if 'vue' in deps:
                            technologies.append('Vue')
                        if 'angular' in deps:
                            technologies.append('Angular')
                        if 'express' in deps:
                            technologies.append('Express')
                        if 'next' in deps:
                            technologies.append('Next.js')
            except:
                pass
                
        # Check requirements.txt for Python technologies
        requirements = os.path.join(self.project_root, 'requirements.txt')
        if os.path.exists(requirements):
            try:
                with open(requirements, 'r') as f:
                    content = f.read()
                    if 'django' in content:
                        technologies.append('Django')
                    if 'flask' in content:
                        technologies.append('Flask')
                    if 'fastapi' in content:
                        technologies.append('FastAPI')
                    if 'pandas' in content:
                        technologies.append('Pandas')
                    if 'numpy' in content:
                        technologies.append('NumPy')
                    if 'requests' in content:
                        technologies.append('Requests')
            except:
                pass
                
        # Check for specific files
        if os.path.exists(os.path.join(self.project_root, 'Dockerfile')):
            technologies.append('Docker')
        if os.path.exists(os.path.join(self.project_root, 'docker-compose.yml')):
            technologies.append('Docker Compose')
        if os.path.exists(os.path.join(self.project_root, '.git')):
            technologies.append('Git')
            
        return technologies
        
    def _calculate_project_size(self) -> Dict[str, int]:
        """Calculate project size metrics"""
        file_count = 0
        total_lines = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common exclusions
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        file_count += 1
                        total_size += os.path.getsize(file_path)
                        
                        # Count lines for text files
                        if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md')):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                total_lines += len(f.readlines())
                    except:
                        pass
                        
        return {
            'files': file_count,
            'lines': total_lines,
            'size_bytes': total_size,
            'size_mb': round(total_size / (1024 * 1024), 2)
        }
        
    def _get_last_modified(self) -> str:
        """Get last modification time of the project"""
        try:
            latest_time = 0
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > latest_time:
                            latest_time = mtime
                    except:
                        pass
                        
            return datetime.fromtimestamp(latest_time).isoformat()
        except:
            return datetime.now().isoformat()
            
    def _get_git_info(self) -> Dict[str, Any]:
        """Get Git information if available"""
        try:
            import subprocess
            
            # Get current branch
            branch = subprocess.check_output(['git', 'branch', '--show-current'], 
                                           cwd=self.project_root, 
                                           stderr=subprocess.DEVNULL).decode().strip()
            
            # Get last commit
            last_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H %s'], 
                                                cwd=self.project_root, 
                                                stderr=subprocess.DEVNULL).decode().strip()
            
            return {
                'branch': branch,
                'last_commit': last_commit,
                'has_git': True
            }
        except:
            return {'has_git': False}
            
    def _get_current_files(self) -> List[Dict[str, Any]]:
        """Get information about current files in the project"""
        current_files = []
        
        # Get recently modified files
        recent_files = []
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > cutoff_time:
                            recent_files.append((file_path, mtime))
                    except:
                        pass
                        
        # Sort by modification time and take top 10
        recent_files.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, mtime in recent_files[:10]:
            try:
                size = os.path.getsize(file_path)
                ext = os.path.splitext(file_path)[1]
                
                current_files.append({
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'extension': ext,
                    'size': size,
                    'modified': datetime.fromtimestamp(mtime).isoformat(),
                    'relative_path': os.path.relpath(file_path, self.project_root)
                })
            except:
                pass
                
        return current_files
        
    def _get_recent_changes(self) -> List[Dict[str, Any]]:
        """Get recent changes in the project"""
        changes = []
        
        # This would ideally integrate with Git, but for now we'll use file modification times
        recent_files = []
        cutoff_time = time.time() - (60 * 60)  # 1 hour ago
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > cutoff_time:
                            recent_files.append((file_path, mtime))
                    except:
                        pass
                        
        # Sort by modification time
        recent_files.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, mtime in recent_files[:5]:
            changes.append({
                'file': os.path.relpath(file_path, self.project_root),
                'type': 'modified',
                'time': datetime.fromtimestamp(mtime).isoformat()
            })
            
        return changes
        
    def _get_code_patterns(self) -> Dict[str, Any]:
        """Analyze code patterns in the project"""
        patterns = {
            'languages': {},
            'imports': set(),
            'functions': [],
            'classes': [],
            'patterns': {}
        }
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                        file_path = os.path.join(root, file)
                        ext = os.path.splitext(file)[1]
                        
                        if ext not in patterns['languages']:
                            patterns['languages'][ext] = 0
                        patterns['languages'][ext] += 1
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                lines = content.split('\n')
                                
                                for line in lines:
                                    line = line.strip()
                                    
                                    # Analyze imports
                                    if line.startswith('import ') or line.startswith('from '):
                                        patterns['imports'].add(line)
                                        
                                    # Analyze functions
                                    if line.startswith('def ') or line.startswith('function '):
                                        patterns['functions'].append(line)
                                        
                                    # Analyze classes
                                    if line.startswith('class '):
                                        patterns['classes'].append(line)
                                        
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"Error analyzing code patterns: {e}")
            
        # Convert set to list for JSON serialization
        patterns['imports'] = list(patterns['imports'])
        
        return patterns
        
    def _get_dependencies(self) -> Dict[str, Any]:
        """Get project dependencies"""
        dependencies = {
            'python': [],
            'nodejs': [],
            'system': []
        }
        
        # Python dependencies
        requirements = os.path.join(self.project_root, 'requirements.txt')
        if os.path.exists(requirements):
            try:
                with open(requirements, 'r') as f:
                    dependencies['python'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except:
                pass
                
        # Node.js dependencies
        package_json = os.path.join(self.project_root, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        dependencies['nodejs'] = list(data['dependencies'].keys())
            except:
                pass
                
        return dependencies
        
    def _get_architecture_info(self) -> Dict[str, Any]:
        """Get architecture information"""
        architecture = {
            'structure': [],
            'patterns': [],
            'components': []
        }
        
        # Analyze directory structure
        dirs = [d for d in os.listdir(self.project_root) if os.path.isdir(os.path.join(self.project_root, d)) and not d.startswith('.')]
        
        architecture['structure'] = dirs
        
        # Detect common patterns
        if 'src' in dirs:
            architecture['patterns'].append('src-based')
        if 'tests' in dirs or 'test' in dirs:
            architecture['patterns'].append('test-separated')
        if 'frontend' in dirs and 'backend' in dirs:
            architecture['patterns'].append('frontend-backend-separated')
        if 'api' in dirs:
            architecture['patterns'].append('api-layer')
        if 'services' in dirs:
            architecture['patterns'].append('service-layer')
        if 'components' in dirs:
            architecture['patterns'].append('component-based')
            
        return architecture
        
    def _get_optimization_hints(self) -> List[Dict[str, Any]]:
        """Get optimization hints for the project"""
        hints = []
        
        # Check for common optimization opportunities
        if not os.path.exists(os.path.join(self.project_root, '.gitignore')):
            hints.append({
                'type': 'gitignore',
                'priority': 'high',
                'message': 'Add .gitignore file to exclude unnecessary files from version control'
            })
            
        if not os.path.exists(os.path.join(self.project_root, 'README.md')):
            hints.append({
                'type': 'documentation',
                'priority': 'medium',
                'message': 'Add README.md file for project documentation'
            })
            
        # Check for large files
        large_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > 1024 * 1024:  # 1MB
                        large_files.append(file_path)
                except:
                    pass
                    
        if large_files:
            hints.append({
                'type': 'performance',
                'priority': 'medium',
                'message': f'Found {len(large_files)} large files (>1MB) that might impact performance'
            })
            
        return hints
        
    def _get_claude_instructions(self) -> List[str]:
        """Get specific instructions for Claude based on project type"""
        instructions = []
        
        project_type = self._detect_project_type()
        
        if project_type == 'zmartbot_trading_system':
            instructions.extend([
                "This is a ZmartBot cryptocurrency trading system",
                "Focus on trading algorithms, risk management, and portfolio optimization",
                "Consider market data analysis, technical indicators, and trading strategies",
                "Pay attention to API integrations with exchanges like Binance and KuCoin",
                "Optimize for real-time data processing and low-latency trading decisions",
                "Consider security implications for trading operations",
                "Follow the existing patterns in the codebase for consistency"
            ])
        elif project_type == 'python_project':
            instructions.extend([
                "This is a Python project",
                "Follow PEP 8 style guidelines",
                "Use type hints where appropriate",
                "Consider async/await for I/O operations",
                "Implement proper error handling and logging"
            ])
        elif project_type == 'nodejs_project':
            instructions.extend([
                "This is a Node.js project",
                "Follow modern JavaScript/TypeScript best practices",
                "Use async/await instead of callbacks",
                "Implement proper error handling",
                "Consider using ESLint and Prettier for code quality"
            ])
        else:
            instructions.extend([
                "Analyze the project structure and follow existing patterns",
                "Maintain code consistency and readability",
                "Consider performance implications of changes",
                "Implement proper error handling and logging"
            ])
            
        return instructions
        
    def _save_context(self, context: Dict[str, Any]):
        """Save context to file for persistence"""
        try:
            with open(self.context_file, 'w') as f:
                json.dump(context, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving context: {e}")
            
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            'timestamp': datetime.now().isoformat(),
            'project_root': self.project_root,
            'context_file': self.context_file,
            'session_file': self.session_file
        }
        
    def update_session(self, action: str, details: Dict[str, Any] = None):
        """Update session with current action"""
        try:
            session_data = {
                'last_action': action,
                'timestamp': datetime.now().isoformat(),
                'details': details or {},
                'project_root': self.project_root
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating session: {e}")

# Convenience functions for easy integration
def get_project_context(project_root: str = None) -> Dict[str, Any]:
    """Get project context for Claude"""
    integration = CursorClaudeIntegration(project_root)
    return integration.get_project_context()

def get_claude_instructions(project_root: str = None) -> List[str]:
    """Get Claude-specific instructions for the project"""
    integration = CursorClaudeIntegration(project_root)
    context = integration.get_project_context()
    return context.get('claude_instructions', [])

def update_claude_session(action: str, details: Dict[str, Any] = None, project_root: str = None):
    """Update Claude session information"""
    integration = CursorClaudeIntegration(project_root)
    integration.update_session(action, details)

# CLI interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor-Claude Integration Helper')
    parser.add_argument('--project-root', default=os.getcwd(), help='Project root directory')
    parser.add_argument('--context', action='store_true', help='Get project context')
    parser.add_argument('--instructions', action='store_true', help='Get Claude instructions')
    parser.add_argument('--session', action='store_true', help='Get session info')
    
    args = parser.parse_args()
    
    integration = CursorClaudeIntegration(args.project_root)
    
    if args.context:
        context = integration.get_project_context()
        print(json.dumps(context, indent=2, default=str))
    elif args.instructions:
        instructions = get_claude_instructions(args.project_root)
        for instruction in instructions:
            print(f"• {instruction}")
    elif args.session:
        session = integration.get_session_info()
        print(json.dumps(session, indent=2))
    else:
        parser.print_help()
